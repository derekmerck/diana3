"""
Orthanc Replacement Map
---------------------------

This is a _dependent_ mapping, it assumes that the complete validation study
  and series level hashes are available.

New UIDs encodes study, series, and instance validation for unique data
  and metadata (like a credit card num)

If a patient_id is provided, it is hashed and used to generate a
  consistent +/-5 day time offset for all study, series, and instance timestamps

Otherwise a random patient id and time offset is assigned based on system time

All other common PHI field are stripped per usual (patient dob, sex, etc.)
"""

import hashlib
import time
from datetime import datetime
from libsvc.utils import small_rand_td
from diana.dicom import DLv, dicom_date, dicom_time
from diana.dicom import DcmUIDMint


def orthanc_sham_map(stu_mhash: str,
                     stu_dhash: str,
                     patient_id=None,
                     stu_dt: datetime = None,

                     ser_mhash: str = None,
                     ser_dhash: str = None,
                     ser_dt: datetime = None,

                     inst_mhash: str = None,
                     inst_dhash: str = None,
                     inst_dt: datetime = None,

                     uid_ns: str = None):

    D = DcmUIDMint()

    # Replacement maps at any level must include study info
    sham_study_uid = D.content_hash_uid(stu_mhash, stu_dhash, DLv.STUDY, uid_ns)
    sham_accession_number = hashlib.sha3_224(sham_study_uid.encode("utf8")).hexdigest()
    _patient_id = patient_id or str(time.time())
    sham_patient_id = hashlib.sha3_224(_patient_id.encode("utf8")).hexdigest()

    _stu_dt = stu_dt or datetime.now()
    study_time_offset = small_rand_td(_seed=_patient_id)
    sham_stu_dt = _stu_dt + study_time_offset

    replace = {
        "PatientID": sham_patient_id,
        "PatientName": sham_patient_id,    # Convenience
        "StudyInstanceUID": sham_study_uid,
        "AccessionNumber": sham_accession_number,
        "StudyID": sham_accession_number,  # Convenience
        "StudyDate": dicom_date(sham_stu_dt),
        "StudyTime": dicom_time(sham_stu_dt),
    }

    # Requested at least a series-level replacement map
    if ser_mhash and ser_dhash:

        sham_series_uid = D.content_hash_uid(ser_mhash, ser_dhash, DLv.SERIES, uid_ns)
        _ser_dt = ser_dt or _stu_dt
        sham_ser_dt = _ser_dt + study_time_offset

        replace = { **replace,
            "SeriesInstanceUID": sham_series_uid,
            "SeriesDate": dicom_date(sham_ser_dt),
            "SeriesTime": dicom_time(sham_ser_dt)
        }

    # Requested an instance-level replacement map
    if inst_mhash and inst_dhash:

        sham_inst_uid = D.content_hash_uid(inst_mhash, inst_dhash, DLv.INSTANCE, uid_ns)
        _inst_dt = inst_dt or _ser_dt
        sham_inst_dt = _inst_dt + study_time_offset

        replace = { **replace,
            'SOPInstanceUID': sham_inst_uid,
            'InstanceCreationTime': dicom_date(sham_inst_dt),
            'InstanceCreationDate': dicom_time(sham_inst_dt)
        }

    return {
        "Replace": replace,
        "Force": True
    }
