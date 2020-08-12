from datetime import datetime


def dicom_date(dt: datetime) -> str:
    s = dt.strftime("%Y%m%d")
    return s


def dicom_time(dt: datetime) -> str:
    s = dt.strftime("%H%M%S")
    return s
