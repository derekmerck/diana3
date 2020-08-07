from enum import IntEnum
from pathlib import Path
import binascii
import logging
from datetime import datetime
from dateutil.parser import parse as dt_parse
import typing


class DicomLevel(IntEnum):
    INSTANCE = 0
    SERIES = 1
    STUDY = 2
    PATIENT = 3
    COLLECTION = 4

    def __str__(self):
        return str(self.name).lower()

    def parent(self):
        if self.value < 4:
            return DicomLevel(self.value + 1)
        else:
            return -1


DLv = DicomLevel

# Requires a simplified tag dictionary, not a pydicom Dataset
# TODO: May need to reverse s (date T time) and put in special parses
# Here is a strange time format:
# 142854 20200229  h:m:s y:m:d  ??
def dicom_best_dt(tags: typing.Dict, level=DLv.INSTANCE,
            strict=False,     # Raise if unable to parse dt for requested level
            allow_no_dt=False # Raise if also unable to parse dt at _any_ level
            ):
    logger = logging.getLogger("dcm_best_dt")

    if level == DLv.INSTANCE:
        if tags.get('InstanceCreationTime') and tags.get("InstanceCreationDate"):
            s = f"{tags.get('InstanceCreationTime')} {tags.get('InstanceCreationDate')}"
            return dt_parse( s )
        elif strict:
            raise ValueError
        else:
            return dicom_best_dt(tags, level=DLv.SERIES)
    elif level == DLv.SERIES:
        if tags.get('SeriesTime') and tags.get("SeriesDate"):
            s = f"{tags.get('SeriesTime')} {tags.get('SeriesDate')}"
            return dt_parse( s )
        elif strict:
            raise ValueError
        else:
            return dicom_best_dt(tags, level=DLv.STUDY)
    elif level == DLv.STUDY:
        if tags.get('StudyTime') and tags.get("StudyDate"):
            s = f"{tags.get('StudyTime')} {tags.get('StudyDate')}"
            return dt_parse( s )
        elif strict:
            raise ValueError
        elif allow_no_dt:
            logger.warning("Using dt can create unstable meta hashes")
            return datetime.now()
    else:
        raise ValueError(f"Bad dt level request ({level})")


def is_dicom(item) -> bool:
    logger = logging.getLogger("is_dcm")

    def check(data):
        data.seek(0x80)
        header = data.read(4)
        magic = binascii.hexlify(header)
        if magic == b"4449434d":
            # logging.debug("Passed")
            return True
        logger.warning("{} is NOT dcm format".format(data))
        return False

    if isinstance(item, Path) or isinstance(item, str):
        # logger.debug("Checking file is dicom")
        with open(item, 'rb') as f:
            return check(f)
    else:
        # logger.debug("Checking data is dicom")
        return check(item)
