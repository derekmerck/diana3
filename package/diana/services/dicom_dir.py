import typing as typ
import pathlib
from diana.endpoint import Endpoint, Serializable
from diana.dicom import DLv
from diana.dixel import Dixel

PathLike = typ.Union[str, pathlib.Path]


class DicomDirectory(Endpoint, Serializable):

    root: pathlib.Path

    def get(self, fp: PathLike, **kwargs) -> Dixel:
        _fp = self.root / fp
        d = Dixel.from_file(_fp)
        return d

    def put(self, dixel: Dixel, fp: PathLike = None, **kwargs):
        if dixel.dlvl > DLv.INSTANCE:
            raise TypeError("Can only write files for instance objects")
        if not dixel.file:
            raise ValueError("No file data found")

        if not fp:
            fp = dixel.meta.get("fp")
            if not fp:
                raise ValueError("No file path found")

        _fp = self.root / fp
        dixel.write_file(fp)
