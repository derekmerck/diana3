"""
A "Dixel" is a DICOM DataItem
"""

import typing as typ
import os
from datetime import datetime
import pathlib
import hashlib
import attr
import numpy as np
import pydicom
from diana.dicom import pydicom_ds_ext  # Monkey patch pydicom
from diana.dicom import DLv, dicom_best_dt
from diana.endpoint import DataItem, UID, Hashable, hex_xor as xor
from diana.endpoint import EndpointTypeException

PathLike = typ.Union[str, pathlib.Path]
UID_JOIN_CHAR = "|"


@attr.s(auto_attribs=True)
class InvalidDicomException(pydicom.errors.InvalidDicomError, EndpointTypeException):
    fp: PathLike = None


@attr.s(auto_attribs=True, hash=False)
class Dixel(DataItem, Hashable):
    data: np.array = None
    dlvl: DLv = None
    tags: typ.Dict = attr.ib(factory=dict)

    def fp(self) -> pathlib.Path:
        return self.meta.get("fp") or pathlib.Path(f"{self._uuid.hex}.dcm")

    main_tag_keys_ = {
        DLv.STUDY: ["PatientID",       # Not guaranteed exists/unique
                    "StudyInstanceUID",
                    "AccessionNumber", # Not guaranteed exists/unique
                    "StudyDate",
                    "StudyTime"
                    # Should include protocol/StudyDesc/RPC
                    ],
        DLv.SERIES: ["SeriesInstanceUID",
                    # "SeriesNumber",
                    # "SeriesDescription",
                    "SeriesDate",
                    "SeriesTime",
                    "BodyPartExamined"],
        DLv.INSTANCE: ["SOPInstanceUID",
                    # "InstanceNumber",
                    "InstanceCreationDate",
                    "InstanceCreationTime"]
    }

    @classmethod
    def main_tag_keys(cls, dlvl):
        res = []
        for i in range(dlvl, DLv.STUDY+1):
            res += cls.main_tag_keys_[i]
        return res

    def main_tags(self, dlvl: DLv = None):
        _dlvl = dlvl or self.dlvl
        main_tag_keys = self.__class__.main_tag_keys(_dlvl)
        res = {k: self.tags.get(k) for k in main_tag_keys if self.tags.get(k)}  # Skip None
        return res

    @property
    def inuid(self) -> str:
        if self.dlvl == DLv.INSTANCE:
            return self.tags.get("SOPInstanceUID")
        else:
            raise ValueError

    @property
    def sruid(self) -> str:
        if self.dlvl <= DLv.SERIES:
            return self.tags.get("SeriesInstanceUID")
        else:
            raise ValueError

    @property
    def stuid(self) -> str:
        if self.dlvl <= DLv.STUDY:
            return self.tags.get("StudyInstanceUID")
        else:
            raise ValueError

    # Can get series or study uid str
    def get_uid_str(self, dlvl: DLv = None):
        _dlvl = dlvl or self.dlvl
        uid_parts = [self.stuid]
        if _dlvl <= DLv.SERIES:
            uid_parts.append(self.sruid)
        if _dlvl == DLv.INSTANCE:
            uid_parts.append(self.inuid)
        return UID_JOIN_CHAR.join(uid_parts)

    def mk_mhash(self, dlvl: DLv = None):
        _dlvl = dlvl or self.dlvl
        _bytes = self.get_uid_str(_dlvl).encode("utf8")
        return hashlib.sha224( _bytes ).hexdigest()

    def mk_dhash(self):
        if self.data is None:
            return None
        return hashlib.sha3_224(self.data).hexdigest()

    def mk_bhash(self):
        if self.binary is None:
            return None
        return hashlib.sha3_224(self.binary).hexdigest()

    def mk_timestamp(self) -> datetime:
        try:
            return dicom_best_dt(self.tags, level=self.dlvl)
        except:
            return datetime.now()

    @classmethod
    def from_file(cls,
                  fp: PathLike,
                  cache_binary: bool = False,
                  bhash_validator: typ.Callable = None,
                  ignore_errors: bool = False) -> typ.Union["Dixel", None]:
        if not os.path.isfile(fp):
            if not ignore_errors:
                print(fp)
                raise FileNotFoundError
            else:
                return
        with open(fp, 'rb') as f:
            _bin = f.read()
            bhash = hashlib.sha3_224(_bin).hexdigest()
        if bhash_validator:
            if not bhash_validator(bhash):  # This may also just raise FileExists
                if not ignore_errors:
                    raise FileExistsError
                else:
                    return
        try:
            ds = pydicom.dcmread(fp)  # This should raise InvalidDicom and exit early
        except pydicom.errors.InvalidDicomError:
            if not ignore_errors:
                # print(f"Failed to parse dicom from {fp}")
                raise InvalidDicomException(fp)
            else:
                return
        tags = ds.get_dict()
        d = cls(dlvl=DLv.INSTANCE,
                tags=tags,
                bhash=bhash,
                data=ds.get_pixels(),
                binary=_bin if cache_binary else None,
                # sources=[f"file:{fp}"]
            )
        return d

    def write_file(self, fp: PathLike = None):
        if self.dlvl > DLv.INSTANCE:
            raise ValueError("Can only write files")
        if not self.binary:
            raise ValueError("No file to write")
        pass
        _fp = fp or self.fp()
        with open(_fp, "wb") as f:
            f.write(self.binary)

    @classmethod
    def from_tags(cls, tags: typ.Dict, dlvl: DLv.STUDY):
        d = cls(
            tags=tags,
            dlvl=dlvl
        )
        return d

    children: typ.Set = attr.ib(factory=set)

    def add_child(self, child: "Dixel"):
        self.children.add(child)
        if self.dhash is None:
            self.dhash = child.dhash
        else:
            self.dhash = xor(self.dhash, child.dhash)
        if self.bhash is None:
            self.bhash = child.bhash
        else:
            self.bhash = xor(self.bhash, child.bhash)

    @classmethod
    def from_child(cls, child: "Dixel", dlvl: DLv = None) -> "Dixel":
        _dlvl = dlvl or child.dlvl + 1
        parent_tags = child.main_tags(_dlvl)
        parent = Dixel.from_tags(parent_tags, _dlvl)
        parent.add_child(child)
        return parent
