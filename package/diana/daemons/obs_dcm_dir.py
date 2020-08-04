from diana.endpoint import ObservableDirectory, FileEventType
from diana.services import DicomDirectory


class ObservableDicomDir(DicomDirectory, ObservableDirectory):
    pass

