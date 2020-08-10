"""
Recursively read in a directory and register the instances with
their series and study parents.
"""

from enum import Enum, auto
import typing as typ
from pprint import pprint
import logging
import attr
from libsvc.endpoint import Endpoint, UID
from libsvc.utils import PathLike
from diana.dicom import DLv
from diana.dixel.dixel import Dixel
from diana.services import DicomDirectory
from diana.exceptions import InvalidDicomException

TEST_ROOTP = "~/data/dcm"
NUM_KEY_CHARS = 10


class KeyType(Enum):
    UUID  = auto()
    MHASH = auto()
    DHASH = auto()
    BHASH = auto()
    IHUID = auto()

KTy = KeyType


@attr.s(auto_attribs=True)
class DicomRegistry(Endpoint):

    instances: dict = attr.ib(factory=dict, init=False)
    dhashes:   dict = attr.ib(factory=dict, init=False)
    bhashes:   dict = attr.ib(factory=dict, init=False)
    studies:   dict = attr.ib(factory=dict, init=False)
    series:    dict = attr.ib(factory=dict, init=False)

    def t(self, dixel: Dixel, kt: KeyType = KTy.MHASH) -> UID:
        if kt == KTy.MHASH:
            return dixel.mhash[:NUM_KEY_CHARS]
        elif kt == KTy.DHASH:
            return dixel.dhash[:NUM_KEY_CHARS]
        elif kt == KTy.BHASH:
            return dixel.bhash[:NUM_KEY_CHARS]
        else:
            raise ValueError

    def index_directory(self, rootp: PathLike):
        D = DicomDirectory(root=rootp)
        file_names = D.inventory()

        for fn in file_names:
            try:
                # May raise "InvalidDicomError" (or return None if ignore_errors flag is set)
                inst = D.get(fn)
                self.put(inst)
            except InvalidDicomException:
                continue
        self.freeze()

    def put(self, inst: Dixel, **kwargs):

        self.dhashes[self.t(inst, KTy.DHASH)] = inst.mhash
        self.bhashes[self.t(inst, KTy.BHASH)] = inst.mhash
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
        for collection in [self.series, self.studies]:
            for item in collection:
                self.dhashes[self.t(item, KTy.DHASH)] = item.dhash
                self.bhashes[self.t(item, KTy.BHASH)] = item.bhash


    def find(self, q: typ.Mapping, **kwargs):
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    R = DicomRegistry()
    R.index_directory(rootp=TEST_ROOTP)

    print("\nSERIES")
    print("-----------------")
    pprint(R.find({"dlvl": DLv.SERIES}))

    print("\nSTUDIES")
    print("-----------------")
    pprint(R.find({"dlvl": DLv.STUDY}))
