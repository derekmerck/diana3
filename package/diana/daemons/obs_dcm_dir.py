import attr
from diana.endpoint import ObservableDirectory, Serializable
from diana.services import DicomDirectory


@attr.s(hash=False)
class ObservableDicomDir(DicomDirectory, ObservableDirectory):
    pass


Serializable.Factory.register(ObservableDicomDir)
