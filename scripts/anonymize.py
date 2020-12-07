from pprint import pprint
from diana.dicom import DLv
from diana.dixel import Dixel, orthanc_sham_map
from diana.services import DicomDirectory, Orthanc
from dcm_registry import DicomRegistry

UPDATE_CACHE = False


def anonymize_and_upload(R: DicomRegistry, D: DicomDirectory, O: Orthanc):

    for d in R.instances.values():

        ser_mhash = Dixel.from_child(d).mhash
        # Find the real ser
        ser = R.get(ser_mhash, dlvl=DLv.SERIES)

        stu_mhash = Dixel.from_child(d, DLv.STUDY).mhash
        # Find the real stu
        stu = R.get(stu_mhash, dlvl=DLv.STUDY)

        m = orthanc_sham_map(
            stu.mhash,
            stu.dhash,
            # Try patient id first, fall back to patient name, or use "UNKNOWN"
            patient_id=stu.tags.get("PatientID", stu.tags.get("PatientName", "UNKNOWN")),
            stu_dt=stu.timestamp,

            ser_mhash = ser.mhash,
            ser_dhash = ser.dhash,
            ser_dt = ser.timestamp,

            inst_mhash = d.mhash,
            inst_dhash = d.dhash,
            inst_dt = d.timestamp
        )

        dd = D.get(d.meta["fp"], binary=True)
        r = O.put(dd)  # If no Patient ID, need to use returned value
        oid = r['ID']
        print(f"Putting {dd.main_tags()} in {oid}")
        O.anonymize(oid, replacement_map=m)  # Anon inst no longer returns image?
        O.delete(oid, dlvl=DLv.INSTANCE)


if __name__ == "__main__":

    ROOT_PATH = "~/data/incoming"
    R = DicomRegistry(shelf_reset=False)
    if UPDATE_CACHE:
        R.index_directory(rootp=ROOT_PATH)  # This gets cached

    # print("\nSERIES")
    # print("-----------------")
    # pprint(R.find({"dlvl": DLv.SERIES}))
    #
    # print("\nSTUDIES")
    # print("-----------------")
    # pprint(R.find({"dlvl": DLv.STUDY}))

    O = Orthanc(url="http://siren:8042")
    print( O.statistics() )
    O.clear()
    print( O.statistics() )

    D = DicomDirectory(root=ROOT_PATH)
    anonymize_and_upload(R, D, O)
