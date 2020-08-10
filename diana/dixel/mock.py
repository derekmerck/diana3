"""
Create a minimal study/series/instance dixel-hierarchy
"""

from datetime import datetime
import numpy as np
from .dixel import Dixel
from ..dicom import DLv

PIXEL_DIMS = DIM = (10, 10)
SLICES = 5


def gen_study(pid: str, stid: str, num_series=2, data_start=0) -> Dixel:
    d = Dixel(tags={"PatientID": f"pat-{pid}",
                    "StudyInstanceUID":  f"stu-{stid}"},
              timestamp=datetime.now(),
              dlvl=DLv.STUDY)
    for i in range(num_series):
        c = gen_series(pid, stid, i, SLICES, data_start=data_start+i*(10*10*5))
        for m in c.children:
            d.add_child(m)
    return d


def gen_series(pid: str, stid: str, serid=0, num_slices=SLICES, data_start=0) -> Dixel:
    d = Dixel(tags={"PatientID": f"pat-{pid}",
                    "StudyInstanceUID":  f"stu-{stid}",
                    "SeriesInstanceUID": f"ser-{serid}"},
              meta={"source": "mock"},
              timestamp = datetime.now(),
              dlvl=DLv.SERIES)
    for i in range(num_slices):
        c = gen_instance(pid, stid, serid, inid=i, data_start=data_start+i*(10*10))
        d.add_child(c)
    return d


def gen_instance(pid, stid, serid=0, inid=0, data_start=0):
    data: np.ndarray = np.arange(data_start, data_start+np.prod(DIM)).reshape(DIM)
    d = Dixel(tags={"PatientID": f"pat-{pid}",
                    "StudyInstanceUID":  f"stu-{stid}",
                    "SeriesInstanceUID": f"ser-{serid}",
                    "SOPInstanceUID":    f"inst-{inid}",
                    "ImagePositionPatient": [0, 0, 0],
                    "Rows": DIM[0],
                    "Columns": DIM[1]},
              meta={"source": "mock"},
              timestamp=datetime.now(),
              data=data)
    return d
