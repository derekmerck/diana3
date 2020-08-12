from pprint import pprint
from diana.services import DicomDirectory, Orthanc
from diana.dicom import DLv
from diana.dixel import Dixel, orthanc_sham_map


def test_file_anon():
    TEST_ROOTP = "~/data/dcm/ibis2"
    D = DicomDirectory(TEST_ROOTP)
    FN = "IM1"
    d = D.get(FN, binary=True)

    O = Orthanc()
    O.clear()
    O.put(d)

    assert O.exists(d.oid(), dlvl=DLv.INSTANCE)
    assert not O.exists("abcd", dlvl=DLv.INSTANCE)

    ser = Dixel.from_child(d, DLv.SERIES)
    stu = Dixel.from_child(d, DLv.STUDY)

    m = orthanc_sham_map(
        stu.mhash,
        stu.dhash,
        patient_id=stu.tags["PatientID"],
        stu_dt=stu.timestamp,

        ser_mhash=ser.mhash,
        ser_dhash=ser.dhash,
        ser_dt=ser.timestamp,

        inst_mhash=d.mhash,
        inst_dhash=d.dhash,
        inst_dt=d.timestamp
    )

    pprint(m)

    # Don't have to get it back -- pass an instance id with
    r = O.anonymize(d.oid(), dlvl=DLv.STUDY, replacement_map=m)
    print(r)

