"""
Recursively read in a directory and register the instances with
their series and study parents.
"""

from pprint import pprint
import logging
import os
from diana.dicom import DLv
from diana.dixel import Dixel
from diana.services import DicomDirectory

# Suppress warnings about ugly data
logger = logging.getLogger("ExceptionHandlingIterator")
logger.setLevel(logging.ERROR)

D = DicomDirectory("/Users/derek/data/bdr_ibis")
# D = DicomDirectory("/data/incoming")
file_names = D.inventory()

studies   = dict()
series    = dict()
instances = dict()

for fn in file_names:
    try:
        # May raise "InvalidDicomError" (or return None if ignore_errors flag is set)
        inst = D.get(fn)
    except:
        continue
    # print(inst.main_tags())
    instances[inst.mhash[0:6]] = inst

    ser = Dixel.from_child(inst, dlvl=DLv.SERIES)
    if not series.get(ser.mhash[0:6]):
        series[ser.mhash[0:6]] = ser
        ser.meta["fp"] = os.path.dirname(fn)
    else:
        series[ser.mhash[0:6]].add_child( inst )

    stu = Dixel.from_child(inst, dlvl=DLv.STUDY)
    if not studies.get(stu.mhash[0:6]):
        studies[stu.mhash[0:6]] = stu
        stu.meta["fp"] = os.path.dirname(fn)
    else:
        studies[stu.mhash[0:6]].add_child(stu)

ser_out = { k: {**v.main_tags(),
                "time": v.timestamp,
                "dhash": v.dhash[0:6]}
            for k, v in series.items() }

stu_out = { k: {**v.main_tags(),
                "time": v.timestamp,
                "dhash": v.dhash[0:6]}
            for k, v in studies.items() }

print("\nSERIES")
print("-----------------")
pprint(ser_out)

print("\nSTUDIES")
print("-----------------")
pprint(stu_out)
