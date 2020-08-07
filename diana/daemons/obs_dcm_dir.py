import attr
from libsvc.endpoint import Serializable
from libsvc.daemon import ObservableDirectory
from diana.services import DicomDirectory


@attr.s(hash=False)
class ObservableDicomDir(DicomDirectory, ObservableDirectory):
    pass


Serializable.Factory.register(ObservableDicomDir)
