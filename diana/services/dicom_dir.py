import typing as typ
import os
import attr
from libsvc.endpoint import Endpoint, Serializable
from libsvc.utils import PathLike, mk_path
from diana.dixel.dixel import Dixel


@attr.s(auto_attribs=True, hash=False)
class DicomDirectory(Endpoint, Serializable):

    root: PathLike = attr.ib(default=None, converter=mk_path)

    def status(self):
        return os.path.isdir(self.root)

    def get(self, fp: PathLike, binary: bool = False, ignore_errors=False, bhash_validator: typ.Callable=None) -> Dixel:
        _fp = self.root / fp
        d = Dixel.from_file(_fp, cache_binary=binary, ignore_errors=ignore_errors, bhash_validator=bhash_validator)
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
