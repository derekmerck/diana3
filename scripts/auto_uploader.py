from libsvc.daemon import Watcher, Trigger, Event, FileEventType
from diana.daemons import ObservableDicomDir
from diana.services import Orthanc, HashRegistry

# CONFIG

CLEAR_HASHES = False  # Reset hash registry
CLEAR_DICOM  = False  # Reset orthanc data
UPLOAD_DICOM = True  # Upload Dicom files
ROOT_PATH    = "/data/incoming"
ORTHANC_URL  = "http://orthanc-queue:8042"
CACHE_FILE   = "/data/tmp/hashes.pkl"
ANNOUNCMENT_INTERVAL = 50

if __name__ == "__main__":

    D = ObservableDicomDir(root=ROOT_PATH)
    H = HashRegistry(cache_file=CACHE_FILE)
    Q = Orthanc(url=ORTHANC_URL)

    def handle_file(event: Event):
        fp = event.data
        dx = D.get(fp, bhash_validator=lambda x: not H.exists, binary=True)
        if dx is not None:
            H.put(dx)
            if UPLOAD_DICOM and Q is not None:
                Q.put(dx)

    t_file = Trigger(
        source=D,
        event_type=FileEventType.INSTANCE_ADDED,
        handler=print
        # handle=handle_file
    )

    W = Watcher(triggers=[t_file])

    W.run()
