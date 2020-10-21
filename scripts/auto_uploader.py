from libsvc.daemon import Watcher, Trigger, Event, FileEventType
from diana.daemons import ObservableDicomDir, DicomEventType, DicomRegistry
from diana.services import Orthanc
from diana.dicom import DcmUIDMint

# CONFIG

dcm_dir_kwargs = {
    "root": "/data/incomming"
}
registry_kwargs = {
    "url": "redis:6379"
}
orthanc_kwargs = {
    "url": "http://orthanc-queue:8042",
    "user": "orthanc",
    "password": "passw0rd"
}
orthanc_archive_peer = "orthanc-hobit"


if __name__ == "__main__":

    D = ObservableDicomDir(**dcm_dir_kwargs)
    R = DicomRegistry(**registry_kwargs)
    Q = Orthanc(**orthanc_kwargs)
    # M = DcmUIDMint()
    # N = NotificationDispatcher()

    def handle_file(event: Event):
        fp = event.data
        dcm = D.get(fp, bhash_validator=R.bhashes, binary=True)
        if dcm:
            R.register(dcm)   # Sets mhash, dhash, info
            Q.put(dcm)

    t_file = Trigger(
        source=D,
        event_type=FileEventType.INSTANCE_ADDED,
        handler=print
        # handle=handle_file
    )

    W = Watcher(triggers=[t_file])

    W.run()

    # def handle_study(event: Event):
    #     oid = event.data
    #     dx = Q.get(oid, view="meta")
    #     dhash = R.dhash(mhash=dx.mhash)
    #     new_duids = M.content_hash_uid(hex_mhash=dx.mhash, hex_dhash=dhash)
    #     repl_map = Orthanc.anonymization_map(new_duids)
    #     new_oid = Q.anonymize(oid, replacement_map=repl_map)
    #     new_dx = Q.get(new_oid, view="meta")
    #     Q.send(new_oid, "orthanc-hobit")
    #
    #     audit_trail = R.info(mhash=dx.mhash)
    #     channels = func(audit_trail)
    #     N.send("study_available", new_dx, channels)
    #

    # # Study becomes stable in the queue
    # t_study = Trigger(
    #     source=Q,
    #     event_type=DicomEventType.STUDY_STABLE,
    #     handler=print
    #     # handle=handle_study
    # )

    # W = Watcher(triggers=[t_file, t_study])
    #
    # W.run()
