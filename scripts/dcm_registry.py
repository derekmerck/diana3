"""
Recursively read in a directory and register the instances with
their series and study parents.
"""

# import os
# from enum import Enum, auto
# import typing as typ
from pprint import pprint
# import pickle
import logging
# import attr
# from libsvc.endpoint import Endpoint, UID
# from libsvc.utils import PathLike
# from diana.dixel.dixel import Dixel
# from diana.services import DicomDirectory
# from diana.exceptions import InvalidDicomException
from diana.dicom import DLv
from diana.daemons import DicomRegistry, ObservableDicomRegistry

RESET_INDEX = True
# TEST_ROOTP = "~/data/incoming"
TEST_ROOTP1 = "~/data/dcm/ibis1"
TEST_ROOTP2 = "~/data/dcm/ibis2"

#
# TEST_SHELF_FILE = os.path.expanduser("~/data/dcm_registry.pkl")
# NUM_KEY_CHARS = 10
#
#
# class KeyType(Enum):
#     UUID  = auto()
#     MHASH = auto()
#     DHASH = auto()
#     BHASH = auto()
#     IHUID = auto()
#
# KTy = KeyType
#
#
# @attr.s(auto_attribs=True)
# class DicomRegistry(Endpoint):
#
#     shelf: bool = True
#     shelf_reset: bool = False
#     shelf_file: str = TEST_SHELF_FILE
#     freeze_req: bool = attr.ib(init=False, default=False)
#
#     instances: dict = attr.ib(factory=dict, init=False)
#     dhashes:   dict = attr.ib(factory=dict, init=False)
#     bhashes:   dict = attr.ib(factory=dict, init=False)
#     studies:   dict = attr.ib(factory=dict, init=False)
#     series:    dict = attr.ib(factory=dict, init=False)
#
#     def __attrs_post_init__(self):
#         if self.shelf and os.path.isfile(self.shelf_file) and not self.shelf_reset:
#             with open(self.shelf_file, "rb") as f:
#                 print("Using shelved data")
#                 self.instances, self.dhashes, self.bhashes, self.studies, self.series = pickle.load(f)
#
#     def t(self, dixel: Dixel, kt: KeyType = KTy.MHASH) -> UID:
#         if kt == KTy.MHASH:
#             return dixel.mhash[:NUM_KEY_CHARS]
#         elif kt == KTy.DHASH:
#             return dixel.dhash[:NUM_KEY_CHARS]
#         elif kt == KTy.BHASH:
#             return dixel.bhash[:NUM_KEY_CHARS]
#         else:
#             raise ValueError
#
#     def index_directory(self, rootp: PathLike):
#         D = DicomDirectory(root=rootp)
#         file_names = D.inventory()
#
#         def check_bhashes(value):
#             _value = value[:NUM_KEY_CHARS]
#             return not (_value in self.bhashes)  # True if its needed
#
#         for fn in file_names:
#             try:
#                 # May raise "InvalidDicomException" if not dicom
#                 # (or return None if ignore_errors flag is set)
#                 inst = D.get(fn, bhash_validator=check_bhashes)
#                 # Some instances are un-indexable
#                 if inst.dhash == None:
#                     print(f"No pixels found in {fn}")
#                     self.bhashes[self.t(inst, KTy.BHASH)] = inst.mhash
#                     continue
#                 self.put(inst)
#             except FileExistsError:
#                 # print(f"Already indexed {fn}")
#                 continue
#             except InvalidDicomException:
#                 print(f"Not a DICOM file {fn}")
#                 continue
#         self.freeze()
#
#     def get(self, uid: UID, dlvl: DLv = DLv.STUDY, **kwargs) -> Dixel:
#         if dlvl == DLv.STUDY:
#             return self.studies[uid[:NUM_KEY_CHARS]]
#         elif dlvl == DLv.SERIES:
#             return self.series[uid[:NUM_KEY_CHARS]]
#         return self.instances[uid[:NUM_KEY_CHARS]]
#
#     def put(self, inst: Dixel, **kwargs):
#
#         # put should trigger a freeze request
#         self.freeze_req = True
#
#         self.dhashes[self.t(inst, KTy.DHASH)] = inst.mhash
#         self.bhashes[self.t(inst, KTy.BHASH)] = inst.mhash
#         self.instances[self.t(inst)] = inst
#
#         ser = Dixel.from_child(inst, dlvl=DLv.SERIES)
#         if not self.series.get(self.t(ser)):
#             self.series[self.t(ser)] = ser
#         else:
#             self.series[self.t(ser)].add_child( inst )
#
#         stu = Dixel.from_child(inst, dlvl=DLv.STUDY)
#         if not self.studies.get(self.t(stu)):
#             self.studies[self.t(stu)] = stu
#         else:
#             self.studies[self.t(stu)].add_child(stu)
#
#     def freeze(self):
#         if not self.freeze_req:
#             print("No registry updates, so no freeze required")
#             return
#
#         for collection in [self.series.values(), self.studies.values()]:
#             for item in collection:
#                 self.dhashes[self.t(item, KTy.DHASH)] = item.dhash
#                 self.bhashes[self.t(item, KTy.BHASH)] = item.bhash
#
#         if self.shelf_file:
#             with open(self.shelf_file, "wb") as f:
#                 pickle.dump((self.instances, self.dhashes, self.bhashes, self.studies, self.series), f)
#             print("Updated shelf cache")
#
#     def find(self, q: typ.Mapping, **kwargs) -> typ.Dict:
#         dlvl = q.get("dlvl")
#         if dlvl == DLv.STUDY:
#             collection = self.studies
#         elif dlvl == DLv.SERIES:
#             collection = self.series
#         elif dlvl == DLv.INSTANCE:
#             collection = self.instances
#         else:
#             raise ValueError(f"No find available for q={q}")
#
#         res = { k: v.summary() for k, v in collection.items() }
#
#         return res


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    R = ObservableDicomRegistry(shelf_reset=RESET_INDEX)
    if RESET_INDEX:
        R.index_directory(rootp=TEST_ROOTP1)
        print([(x.data.mhash[:10], x.event_type) for x in R.changes()])

        R.freeze()
        R.index_directory(rootp=TEST_ROOTP2)
        R.freeze()
        print([(x.data.mhash[:10], x.event_type) for x in R.changes()])
        print([(x.data.mhash[:10], x.event_type) for x in R.changes()])

    #
    # print("\nSERIES")
    # print("-----------------")
    # pprint(R.find({"dlvl": DLv.SERIES}))

    print("\nSTUDIES")
    print("-----------------")
    studies = R.find({"dlvl": DLv.STUDY})
    # useful_keys = ['AccessionNumber', 'PatientID', 'fp', 'n_children', 'timestamp']
    #
    # result = {}
    # for stuid, summary in studies.items():
    #     summary = {k: v for k, v in summary.items() if k in useful_keys}
    #     result[stuid] = summary
    # pprint(result)

    pprint(studies)
