from pprint import pprint
from datetime import datetime
import time
from dateutil.parser import parse as dt_parse
from diana.dixel import orthanc_sham_map
from diana.dicom import DcmUIDMint


def test_sham_map():
    stu_mhash = "abcdef123457890"
    stu_dhash = "123457890abcdef"

    m = orthanc_sham_map(stu_mhash, stu_dhash)
    pprint(m)

    stu_duid = m["Replace"]["StudyInstanceUID"]
    h = DcmUIDMint.hashes_from_duid(stu_duid)
    pprint(h)

    assert stu_mhash.startswith(h["mhash_s"])
    assert stu_dhash.startswith(h["dhash_s"])

    stu_dt = datetime(year=2000, month=1, day=1, hour=0)

    m = orthanc_sham_map(stu_mhash, stu_dhash, stu_dt=stu_dt)
    pprint(m)

    sham_st_dt_str = m["Replace"]["StudyDate"]
    sham_st_dt = dt_parse(sham_st_dt_str)

    stu_time_diff = sham_st_dt - stu_dt
    assert abs(stu_time_diff.days) <= 5  # Default is +/-5 days


    # Assume study has only one series, so dhash is the same (mhash wouldn't be tho)
    m = orthanc_sham_map(stu_mhash, stu_dhash, stu_dt=stu_dt, ser_mhash=stu_mhash, ser_dhash=stu_dhash)
    pprint(m)

    assert m["Replace"]["SeriesInstanceUID"]

    # Assume study has only one series, so dhash is the same (mhash wouldn't be tho)
    m = orthanc_sham_map(stu_mhash, stu_dhash, stu_dt=stu_dt,
                         ser_mhash=stu_mhash, ser_dhash=stu_dhash,
                         inst_mhash=stu_mhash, inst_dhash=stu_dhash, inst_dt=datetime.now())
    pprint(m)

    assert m["Replace"]["SOPInstanceUID"]

    # Assume study has only one series, so dhash is the same (mhash wouldn't be tho)
    m = orthanc_sham_map(stu_mhash, stu_dhash, patient_id="ABCD")
    pid0 = m["Replace"]["PatientID"]
    stm0 = m["Replace"]["StudyTime"]
    time.sleep(1)
    m = orthanc_sham_map(stu_mhash + "123", stu_dhash + "abc", patient_id="ABCD")
    pid1 = m["Replace"]["PatientID"]
    stm1 = m["Replace"]["StudyTime"]

    assert pid0 == pid1
    print(stm0)
    print(stm1)
    assert int(stm1) > int(stm0)       # Should be offset by about 1 sec
    assert int(stm1) <= int(stm0) + 2  # and at most 2 secs


if __name__ == "__main__":

    test_sham_map()