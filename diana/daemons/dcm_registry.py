from enum import Enum, auto
import typing as typ
import os
from pprint import pprint
import pickle
from datetime import datetime, timedelta
import attr
from libsvc.endpoint import Endpoint, UID
from libsvc.daemon import ObservableMixin, Event
from libsvc.utils import PathLike
from diana.dicom import DLv
from diana.dixel import Dixel, InvalidDicomException
from diana.services import DicomDirectory
from .obs_orthanc import OrthancEventType as DicomEventType

TEST_SHELF_FILE = os.path.expanduser("/tmp/dcm_registry.pkl")
NUM_KEY_CHARS = 10
STABLE_TIMEOUT = timedelta(seconds=10)

class KeyType(Enum):
    UUID  = auto()
    MHASH = auto()
    DHASH = auto()
    BHASH = auto()
    IHUID = auto()

KTy = KeyType


@attr.s(auto_attribs=True)
class DicomRegistry(Endpoint):

    shelf: bool = True
    shelf_reset: bool = False
    shelf_file: str = TEST_SHELF_FILE
    # freeze_req: bool = attr.ib(init=False, default=False)

    instances: dict = attr.ib(factory=dict, init=False)
    dhashes:   dict = attr.ib(factory=dict, init=False)
    bhashes:   dict = attr.ib(factory=dict, init=False)
    studies:   dict = attr.ib(factory=dict, init=False)
    series:    dict = attr.ib(factory=dict, init=False)

    def __attrs_post_init__(self):
        if self.shelf and os.path.isfile(self.shelf_file) and not self.shelf_reset:
            with open(self.shelf_file, "rb") as f:
                print("Using shelved data")
                self.instances, self.dhashes, self.bhashes, self.studies, self.series = pickle.load(f)

    def t(self, dixel: Dixel, kt: KeyType = KTy.MHASH) -> UID:
        if kt == KTy.MHASH:
            return dixel.mhash[:NUM_KEY_CHARS]
        elif kt == KTy.DHASH:
            return dixel.dhash[:NUM_KEY_CHARS]
        elif kt == KTy.BHASH:
            return dixel.bhash[:NUM_KEY_CHARS]
        else:
            raise ValueError

    def index_instance(self, D: DicomDirectory, fn: str):

        def check_bhashes(value):
            _value = value[:NUM_KEY_CHARS]
            return not (_value in self.bhashes)  # True if its needed

        try:
            # May raise "InvalidDicomException" if not dicom
            # (or return None if ignore_errors flag is set)
            inst = D.get(fn, bhash_validator=check_bhashes)
            # Some instances are un-indexable
            if inst.dhash == None:
                print(f"No pixels found in {fn}")
                self.bhashes[self.t(inst, KTy.BHASH)] = inst.mhash
                return
            self.put(inst)
        except FileExistsError:
            # print(f"Already indexed {fn}")
            pass
        except InvalidDicomException:
            print(f"Not a DICOM file {fn}")
        return

    def index_directory(self, rootp: PathLike):
        D = DicomDirectory(root=rootp)
        file_names = D.inventory()

        # def check_bhashes(value):
        #     _value = value[:NUM_KEY_CHARS]
        #     return not (_value in self.bhashes)  # True if its needed

        for fn in file_names:

            self.index_instance(D, fn)

            #
            # try:
            #     # May raise "InvalidDicomException" if not dicom
            #     # (or return None if ignore_errors flag is set)
            #     inst = D.get(fn, bhash_validator=check_bhashes)
            #     # Some instances are un-indexable
            #     if inst.dhash == None:
            #         print(f"No pixels found in {fn}")
            #         self.bhashes[self.t(inst, KTy.BHASH)] = inst.mhash
            #         continue
            #     self.put(inst)
            # except FileExistsError:
            #     # print(f"Already indexed {fn}")
            #     continue
            # except InvalidDicomException:
            #     print(f"Not a DICOM file {fn}")
            #     continue

        # Safe to freeze after reading an entire dir
        self.freeze()

    def get(self, uid: UID, dlvl: DLv = DLv.STUDY, **kwargs) -> Dixel:
        if dlvl == DLv.STUDY:
            return self.studies[uid[:NUM_KEY_CHARS]]
        elif dlvl == DLv.SERIES:
            return self.series[uid[:NUM_KEY_CHARS]]
        return self.instances[uid[:NUM_KEY_CHARS]]

    def put(self, inst: Dixel, **kwargs):

        self.dhashes[self.t(inst, KTy.DHASH)] = inst
        self.bhashes[self.t(inst, KTy.BHASH)] = inst
        self.instances[self.t(inst)] = inst

        ser = Dixel.from_child(inst, dlvl=DLv.SERIES)
        if not self.series.get(self.t(ser)):
            self.series[self.t(ser)] = ser
        else:
            self.series[self.t(ser)].add_child( inst )

        stu = Dixel.from_child(inst, dlvl=DLv.STUDY)
        if not self.studies.get(self.t(stu)):
            self.studies[self.t(stu)] = stu
        else:
            self.studies[self.t(stu)].add_child(stu)

    def freeze(self):
        collections = [*self.series.values(), *self.studies.values()]
        rehash_items = [x for x in collections if x.stale_dhash or x.stale_bhash]

        if len(rehash_items) == 0:
            print("No registry updates, so no freeze required")
            return

        pprint([x.summary() for x in rehash_items])
        print(self.dhashes.keys())

        for item in rehash_items:
            try:
                del( self.dhashes[item.dhash[:NUM_KEY_CHARS]] )
            except KeyError:
                print(f"No precedent dhash: {item.dhash[:NUM_KEY_CHARS]}")
                pass
            try:
                del( self.bhashes[item.bhash[:NUM_KEY_CHARS]] )
            except KeyError:
                print(f"No precedent bhash: {item.bhash[:NUM_KEY_CHARS]}")
                pass
            self.dhashes[self.t(item, KTy.DHASH)] = item.dhash
            self.bhashes[self.t(item, KTy.BHASH)] = item.bhash
            item.stale_bhash = None
            item.stale_dhash = None

        if self.shelf_file:
            with open(self.shelf_file, "wb") as f:
                pickle.dump((self.instances, self.dhashes, self.bhashes, self.studies, self.series), f)
            print("Updated shelf cache")

    def find(self, q: typ.Mapping, **kwargs) -> typ.Dict:
        dlvl = q.get("dlvl")
        if dlvl == DLv.STUDY:
            collection = self.studies
        elif dlvl == DLv.SERIES:
            collection = self.series
        elif dlvl == DLv.INSTANCE:
            collection = self.instances
        else:
            raise ValueError(f"No find available for q={q}")

        res = { k: v.summary() for k, v in collection.items() }

        return res


@attr.s(auto_attribs=True)
class ObservableDicomRegistry(DicomRegistry, ObservableMixin):
    events: typ.List = attr.Factory(list)

    def changes(self) -> typ.List:
        these = self.events[:]
        self.events = []
        return these

    def freeze(self):
        # freeze the registry
        DicomRegistry.freeze(self)

        now = datetime.now()
        collections = [*self.series.values(), *self.studies.values()]

        stable_items = [x for x in collections if x.update_ts and now - x.update_ts >= STABLE_TIMEOUT ]

        # Process changes
        for item in stable_items:
            if item.dlvl == DLv.STUDY:
                e = Event(event_type=DicomEventType.STUDY_STABLE, data=item)
            else:
                e = Event(event_type=DicomEventType.SERIES_STABLE, data=item)
            self.events.append(e)
            item.update_ts = None
