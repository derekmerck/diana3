import typing as typ
import pathlib
import attr
import numpy as np
from diana.dicom import DLv
from diana.endpoint import Data, UID

PathLike = typ.Union[str, pathlib.Path]


@attr.s(auto_attribs=True)
class Dixel(Data):
    data: np.array = None
    dlvl: DLv = None
    tags: typ.Dict = attr.ib(factory=dict)
    file: typ.ByteString = None

    def oid(self, dlvl=None) -> UID:
        pass

    def fp(self) -> pathlib.Path:
        pass

    @classmethod
    def from_file(cls, fp: PathLike):
        pass

    def write_file(self, fp: PathLike):
        pass

    @classmethod
    def from_tags(cls, tags):
        pass
