"""
A "Dixel" is a DICOM DataItem
"""

import typing as typ
import os
import pathlib
import hashlib
import attr
import numpy as np
import pydicom
from diana.dicom import pydicom_ds_ext  # Monkey patch pydicom
from diana.dicom import DLv
from diana.endpoint import DataItem, UID, Hashable

PathLike = typ.Union[str, pathlib.Path]


@attr.s(auto_attribs=True)
class Dixel(DataItem, Hashable):
    data: np.array = None
    dlvl: DLv = None
    tags: typ.Dict = attr.ib(factory=dict)

    def oid(self, dlvl=None) -> UID:
        pass

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

    def mk_mhash(self):
        _bytes = str(self.main_tags()).encode("utf8")
        return hashlib.sha3_224(_bytes).hexdigest()

    def mk_dhash(self):
        if self.data is None:
            return None
        return hashlib.sha3_224(self.data).hexdigest()

    def mk_bhash(self):
        if self.binary is None:
            return None
        return hashlib.sha3_224(self.binary).hexdigest()

    @classmethod
    def from_file(cls,
                  fp: PathLike,
                  cache_binary: bool = False,
                  bhash_validator: typ.Callable = None) -> "Dixel":

        if not os.path.isfile(fp):
            print(fp)
            raise FileNotFoundError
        with open(fp, 'rb') as f:
            _bin = f.read()
            bhash = hashlib.sha3_224(_bin).hexdigest()
        if bhash_validator:
            if not bhash_validator(bhash):  # This may also just raise FileExists
                raise FileExistsError
        ds = pydicom.dcmread(fp)  # This should raise InvalidDicom and exit early
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
        if not fp:
            fp = self.fp()

        if self.dlvl > DLv.INSTANCE:
            raise ValueError("Can only write files")
        if not self.binary:
            raise ValueError("No file to write")
        pass

        with open(fp, "wb") as f:
            f.write(self.binary)

    @classmethod
    def from_tags(cls, tags: typ.Dict, dlvl: DLv.STUDY):
        d = cls(
            tags=tags,
            dlvl=dlvl
        )
        return d
