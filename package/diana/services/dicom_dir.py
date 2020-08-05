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

    def status(self):
        return os.path.isdir(self.root)

    def get(self, fp: PathLike, binary: bool = False, **kwargs) -> Dixel:
        _fp = self.root / fp
        d = Dixel.from_file(_fp, cache_binary=binary)
        return d

    def put(self, dixel: Dixel, fp: PathLike = None, **kwargs):
        _fp = self.root / fp
        dixel.write_file(_fp)

    def inventory(self, relative=True):
        """If loading with a DicomDir rooted here, return relative paths"""
        res = []
        for root, dirs, files in os.walk(self.root):
            for f in files:
                fp = os.path.join(root, f)  # abs
                if relative:
                    fp = os.path.relpath(fp, self.root)  # rel
                res.append(fp)
        return res


Serializable.Factory.register(DicomDirectory)
