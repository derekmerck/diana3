"""
Registry for hash values and summary metadata for DICOM items.

This data structure is important for computing collection content-hashes
("dhashes"), which are dependent on children content-hashes.

dhashes, in turn, are used to generate consistent, content-based DICOM UIDs
for deidentification.

This implementation uses a pickle file for persistence.

TODO: This single-key implementation has a collision problem with
      content-hashes for single-series studies and single-instance series.
      However, is currently irrelevant b/c there are no collection-level
      lookups by content-hash.
"""

import typing as typ
from collections import defaultdict
import os
import uuid
import pickle
from libsvc.endpoint import Endpoint, UID
from libsvc.utils import hex_xor
from diana.dixel import Dixel
from diana.dicom import DLv
import attr


@attr.s(auto_attribs=True)
class HashRegistry(Endpoint):
    """
    Content-hash registry with a dict backend and pickle-file persistence

    _Any_ known hash (content, binary, meta) can be used to lookup a
    registry-specific uid pointer in "hashes" that points to summary data in "meta".

    "exists" also provides a way to early-exit unnecessary file reads for DICOM
    objects that have already been registered.
    """

    meta:  typ.Dict[UID, typ.Dict] = attr.Factory(dict)
    hashes:  typ.Dict[UID, UID] = attr.Factory(dict)
    links:  typ.Dict[UID, typ.Set[UID]] = attr.ib(init=False)
    @links.default
    def mk_links(self):
        return defaultdict(set)

    def get(self, hash: UID, **kwargs) -> typ.Dict:
        _uid = self.hashes.get(hash)
        if _uid is None:
            raise KeyError(f"Nothing registered to hash {hash}")
        return self.meta.get(_uid)

    def put(self, dx: Dixel, link_duplicates=False, ignore_errors=True, **kwargs):
        if dx.dlvl > DLv.INSTANCE:
            if ignore_errors:
                print("Can only register instances")
                return
            raise ValueError("Can only register instances")
        if dx.dhash is None:
            if ignore_errors:
                print("Can only register hashed dixels")
                return
            raise AttributeError("Can only register hashed dixels")
        _uid = self.hashes.get(dx.mhash)
        if _uid is None:
            _uid = uuid.uuid4().hex
            self.meta[_uid] = dx.summary()
            self.hashes[dx.mhash] = _uid
            self.needs_cached = True  # Flag a cache update
        if self.hashes.get(dx.dhash) is None:
            self.hashes[dx.dhash] = _uid
        elif self.hashes.get(dx.dhash) != _uid:
            if link_duplicates:
                _uid1 = self.hashes.get(dx.dhash)
                self.links[_uid1].add(_uid)
                self.links[_uid].add(_uid1)
            if ignore_errors:
                print("Already seen this dhash under a different UID")
                return
            else:
                raise ValueError("Already seen this dhash under a different UID")
        if dx.bhash is not None:
            if self.hashes.get(dx.bhash) is None:
                self.hashes[dx.bhash] = _uid
            elif self.hashes.get(dx.bhash) != _uid:
                # This is always very bad!
                raise ValueError("Already seen this bhash under a different UID")

        def register_parent(par):
            _uid = self.hashes.get(par.mhash)
            if _uid is None:
                _uid = uuid.uuid4().hex
                self.meta[_uid] = par.summary()
                self.hashes[par.mhash] = _uid
                # self.hashes[par.uhash] = _uid
            cur_dhash = self.meta[_uid]["dhash"] or ""
            if cur_dhash in self.hashes:
                del(self.hashes[cur_dhash])
            new_dhash = hex_xor(dx.dhash, cur_dhash)
            self.meta[_uid]["dhash"] = new_dhash
            self.hashes[new_dhash] = _uid
            if dx.bhash is not None:
                cur_bhash = self.meta[_uid]["bhash"] or ""
                if cur_bhash in self.hashes:
                    del(self.hashes[cur_bhash])
                new_bhash = hex_xor(dx.bhash, cur_bhash)
                self.meta[_uid]["bhash"] = new_bhash
                self.hashes[new_bhash] = _uid


        ser = Dixel.from_child(dx, dlvl=DLv.SERIES)
        register_parent(ser)

        stu = Dixel.from_child(dx, dlvl=DLv.STUDY)
        register_parent(stu)

    def exists(self, hash: UID, **kwargs) -> bool:
        """Fast forward to skip registering existing objects"""
        return hash in self.hashes

    def studies(self):
        return {k: v for k,v in self.meta.items() if DLv.of(v["dlvl"])==DLv.STUDY}

    def series(self):
        return {k: v for k,v in self.meta.items() if DLv.of(v["dlvl"])==DLv.SERIES}

    def instances(self):
        return {k: v for k,v in self.meta.items() if DLv.of(v["dlvl"])==DLv.INSTANCE}

    def find(self, q: typ.Mapping, **kwargs) -> typ.Dict:
        dlvl = q.get("dlvl")
        if dlvl == DLv.STUDY:
            collection = self.studies()
        elif dlvl == DLv.SERIES:
            collection = self.series()
        elif dlvl == DLv.INSTANCE:
            collection = self.instances()
        else:
            raise ValueError(f"No find available for q={q}")
        return collection

    def set(self, key, mhash):
        _uid = self.hashes.get(mhash)
        if _uid is None:
            raise KeyError(f"No referent for mhash {mhash}")
        self.hashes[key] = _uid

    def link(self, mhash0, mhash1):
        _uid0 = self.hashes.get(mhash0)
        if _uid0 is None:
            raise KeyError(f"No referent for mhash {mhash0}")
        _uid1 = self.hashes.get(mhash1)
        if _uid0 is None:
            raise KeyError(f"No referent for mhash {mhash1}")
        self.links[_uid0].add(_uid1)
        self.links[_uid1].add(_uid0)

    def aliases(self, mhash):
        _uid = self.hashes.get(mhash)
        if _uid is None:
            return None
        results = []
        for alias in self.links.get(_uid):
            results.append( self.meta.get(alias) )
        return results

    # PERSISTENCE

    clear_cache: bool = False
    cache_file: str = "/tmp/hashes.pik"
    needs_cached: bool = attr.ib(init=False, default=False)

    # TODO: Should inherit from libsvc.persistence
    def shelve(self):
        if not self.needs_cached:
            return
        with open(self.cache_file, "wb") as f:
            pickle.dump((self.meta, self.hashes), f)
        self.needs_cached = False

    def unshelve(self):
        with open(self.cache_file, "rb") as f:
            self.meta, self.hashes = pickle.load(f)

    def __attrs_post_init__(self):
        if not self.clear_cache and os.path.isfile(self.cache_file):
            self.unshelve()
