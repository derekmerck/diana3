"""
Provides persistent inventory and reverse lookups for
available Dixel items

Dixels are represented by headers and hashes, and have sets of
references to children
"""

import logging
import typing as typ
from enum import Enum
import attr
from libsvc.endpoint import UID
from libsvc.persistence import RedisPersistenceBackend
from libsvc.utils import hex_xor as xor
from diana.dixel.dixel import Dixel, DLv

from dcm_registry import NUM_KEY_CHARS, DicomRegistry

KEY_SEP = "/"
ROOTP = "~/data/dcm/ibis1"

class RegistryNamespace(Enum):
    MHASHES   = "mh"
    BHASHES   = "bh"
    DHASHES   = "dh"
    INSTANCES = "inst"
    SERIES    = "ser"
    STUDIES   = "stu"
    MEMBERS   = "mem"

RNs = RegistryNamespace


@attr.s(auto_attribs=True)
class RedisDicomRegistry(DicomRegistry, RedisPersistenceBackend):

    namespace: str = "dcm_reg"

    def t(self, dixel: Dixel, rns: RNs = None) -> UID:

        if not rns:
            if dixel.dlvl == DLv.INSTANCE:
                rns = RNs.INSTANCES
            elif dixel.dlvl == DLv.SERIES:
                rns = RNs.SERIES
            elif dixel.dlvl == DLv.STUDY:
                rns = RNs.STUDIES
            else:
                raise ValueError("Missing registry ns")

        if rns == RNs.BHASHES:
            h = dixel.bhash
        elif rns == RNs.DHASHES:
            h = dixel.dhash
        else:
            h = dixel.mhash

        s = KEY_SEP.join([self.namespace,
                          rns.value,
                          h[:NUM_KEY_CHARS]])

        return s

    # def status(self) -> bool:
    #     pass

    def get(self, mhash: UID, **kwargs) -> Dixel:
        s = KEY_SEP.join([self.namespace,
                          RNs.MHASHES.value,
                          mhash[:NUM_KEY_CHARS]])
        summary = self.gateway.hgetall(s)
        d = Dixel.from_summary(summary)
        return d

    # def exists(self, key: UID, kty: KeyType = KTy.MHASH, **kwargs) -> bool:
    #     if kty == KTy.BHASH:
    #         return self.gateway.exists(self.t(key, kty.BHASH) + "/m")
    #     elif kty == KTy.DHASH:
    #         return self.gateway.get(self.t(key, kty.DHASH) + "/m")
    #     elif kty == KTy.MHASH:
    #         return self.gateway.get(self.t(key, KTy.MHASH) + "/t")
    #     else:
    #         raise RuntimeError

    def find(self, query: typ.Dict, *args, **kwargs) -> typ.List[UID]:
        dlvl = query.get("dlvl")
        if not dlvl:
            raise ValueError

        if dlvl == DLv.SERIES:
            s = KEY_SEP.join([self.namespace,
                              RNs.SERIES.value,
                              "*"])
            return self.gateway.keys(s)
        elif dlvl == DLv.SERIES:
            s = KEY_SEP.join([self.namespace,
                              RNs.SERIES.value,
                              "*"])
            return self.gateway.keys(s)
        elif dlvl == DLv.STUDY:
            s = KEY_SEP.join([self.namespace,
                              RNs.STUDIES.value,
                              "*"])
            return self.gateway.keys(s)

        raise RuntimeError

    def put(self, dixel: Dixel, **kwargs) -> UID:

        """
        /{ns}/idx/bh/{bhash}    -> mhash     # file exists?
        /{ns}/idx/dh/{dhash}    -> mhash

        /{ns}/idx/inst/{mhash}  -> summary
        /{ns}/idx/ser/{mhash}   -> summary
        /{ns}/idx/stu/{mhash}   -> summary
        /{ns}/idx/mem/{mhash}   -> set( children mhashes )
        """

        logging.debug(f"Putting {dixel.mhash} from {dixel.fp()}")

        if dixel.dlvl != DLv.INSTANCE:
            raise TypeError("Can only put instances in index")

        bhash_key = self.t(dixel, RNs.BHASHES)
        self.gateway.set(bhash_key, dixel.mhash)

        # print(self.gateway.get(bhash_key))
        # exit()

        dhash_key = self.t(dixel, RNs.DHASHES)
        self.gateway.set(dhash_key, dixel.mhash)

        mhash_key = self.t(dixel)
        self.gateway.hmset(mhash_key, dixel.summary())

        # Add the series and the study if not already present
        ser = Dixel.from_child(dixel, dlvl=DLv.SERIES)
        ser_mhash_key = self.t(ser)
        if not self.gateway.exists(ser_mhash_key):
            self.gateway.hmset(ser_mhash_key, ser.summary())
        else:
            n = self.gateway.hget(ser_mhash_key, "n_children").decode("utf8")
            nn = int(n) + 1
            self.gateway.hset(ser_mhash_key, "n_children", nn)
            b = self.gateway.hget(ser_mhash_key, "bhash").decode("utf8")
            bb = xor(b, dixel.bhash)
            self.gateway.hset(ser_mhash_key, "dhash", bb)
            d = self.gateway.hget(ser_mhash_key, "dhash").decode("utf8") # Redundant str/unstr
            dd = xor(d, dixel.dhash)
            self.gateway.hset(ser_mhash_key, "dhash", dd)

        ser_children_key = self.t(ser, RNs.MEMBERS)
        self.gateway.sadd(ser_children_key, dixel.mhash)

        # TODO: Oops, now do the study!

        return dixel.mhash

    def freeze(self):
        return
        # TODO: fix freeze
        for ser_mhash in self.find({"dlvl": DLv.SERIES}):
            ser: Dixel = self.get(ser_mhash)
            self.gateway.set(self.t(ser, RNs.DHASHES), ser.dhash)
            self.gateway.set(self.t(ser, RNs.BHASHES), ser.bhash)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    R = RedisDicomRegistry()
    R.index_directory(rootp=ROOTP)

    print( R.find({"dlvl": DLv.SERIES}) )