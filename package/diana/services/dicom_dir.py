import typing as typ
import os
import pathlib
import attr
from diana.endpoint import Endpoint, Serializable
from diana.dicom import DLv
from diana.dixel import Dixel

PathLike = typ.Union[str, pathlib.Path]


@attr.s(auto_attribs=True, hash=False)
class DicomDirectory(Endpoint, Serializable):

    root: PathLike = attr.ib(default=None, converter=pathlib.Path)

    def get(self, fp: PathLike, binary: bool = False, **kwargs) -> Dixel:
        _fp = self.root / fp
        d = Dixel.from_file(_fp, cache_binary=binary)
        return d

    def put(self, dixel: Dixel, fp: PathLike = None, **kwargs):
        _fp = self.root / fp
        dixel.write_file(_fp)

    # TODO: test with nested dirs
    def inventory(self):
        res = []
        for root, dirs, files in os.walk(self.root):
            res = [f for f in files]
        return res