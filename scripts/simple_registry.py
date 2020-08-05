from pprint import pprint
import logging
import os
import pathlib
from diana.dicom import DLv, dicom_best_dt
from diana.dixel import Dixel
from diana.services import DicomDirectory

logger = logging.getLogger("ExceptionHandlingIterator")
logger.setLevel(logging.ERROR)

D = DicomDirectory("/Users/derek/data/bdr_ibis")
file_names = D.inventory()

studies   = dict()
series    = dict()
instances = dict()

for fn in file_names:
    inst = D.get(fn)
    # print(inst.main_tags())
    instances[inst.mhash[0:6]] = inst.main_tags()

    ser = Dixel.from_tags(inst.main_tags(dlvl=DLv.SERIES), dlvl=DLv.SERIES)
    if not series.get(ser.mhash[0:6]):
        best_dt = dicom_best_dt(ser.main_tags(dlvl=DLv.STUDY))
        series[ser.mhash[0:6]] = {
            **ser.main_tags(),
            "n_insts": 1,
            "SeriesDateTime": best_dt.strftime("%d/%m/%y %H:%M:%S"),
            "path": str(pathlib.Path(fn).parent)
        }
    else:
        series[ser.mhash[0:6]]["n_insts"] += 1

    stu = Dixel.from_tags(inst.main_tags(dlvl=DLv.STUDY), dlvl=DLv.STUDY)
    if not studies.get(stu.mhash[0:6]):
        best_dt = dicom_best_dt(stu.main_tags(dlvl=DLv.STUDY))
        studies[stu.mhash[0:6]] = {
            **stu.main_tags(),
            "n_insts": 1,
            "StudyDateTime": best_dt.strftime("%B %d %Y, %H:%M"),
            "path": str(pathlib.Path(fn).parent)
        }
    else:
        studies[stu.mhash[0:6]]["n_insts"] += 1

print()
print("SERIES")
print("-----------------")
pprint(series)

print("STUDIES")
print("-----------------")
pprint(studies)
