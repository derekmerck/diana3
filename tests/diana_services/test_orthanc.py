""""
Create a test orthanc instance:
$ docker run --rm -d -p 8042:8042 derekmerck/orthanc-wbvc
"""
import logging
from pprint import pprint
from libsvc.endpoint import ComparatorType as CTy
from diana.dicom import DLv
from diana.dixel import Dixel
from diana.exceptions import InvalidDicomException
from diana.services import Orthanc, DicomDirectory

# TODO: Orthanc test for find etc.


def test_orthanc_status():
    O = Orthanc()
    assert( O.status( ) )


def test_orthanc_upload():

    O = Orthanc()
    O.clear()

    ROOTP = "~/data/dcm/ibis2"
    D = DicomDirectory(ROOTP)

    d = D.get("IM1", binary=True)
    print(d.summary())
    O.put(d)
    g = O.get(d.oid(), dlvl=DLv.INSTANCE)
    Dixel.comparator = CTy.METADATA
    assert d == g

    e = Dixel.from_child(d)
    h = O.get(e.oid(), dlvl=DLv.SERIES)
    assert e == h

    f = Dixel.from_child(e)
    i = O.get(f.oid(), dlvl=DLv.STUDY)
    assert f == i


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    orthanc_upload_test()
