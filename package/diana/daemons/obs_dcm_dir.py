import attr
from diana.endpoint import ObservableDirectory, FileEventType
from diana.services import DicomDirectory


@attr.s(hash=False)
class ObservableDicomDir(DicomDirectory, ObservableDirectory):
    pass

