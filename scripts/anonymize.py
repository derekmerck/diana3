from pprint import pprint
import os
import pickle
from diana.dicom import DLv
from diana.dixel import Dixel, orthanc_sham_map
from diana.services import DicomDirectory, Orthanc
from dcm_registry import DicomRegistry


# registry with caching
def mk_registry(root_p, pkl_fn, rebuild=False):

    if not rebuild and os.path.isfile(pkl_fn):
        with open(pkl_fn, "rb") as pkl:
            return pickle.load(pkl)

    else:
        R = DicomRegistry()
        R.index_directory(rootp=root_p)

        with open(pkl_fn, "wb") as pkl:
            pickle.dump(R, pkl)

        return R


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
            patient_id=stu.tags["PatientID"],
            stu_dt=stu.timestamp,

            ser_mhash = ser.mhash,
            ser_dhash = ser.dhash,
            ser_dt = ser.timestamp,

            inst_mhash = d.mhash,
            inst_dhash = d.dhash,
            inst_dt = d.timestamp
        )

        dd = D.get(d.meta["fp"], binary=True)
        O.put(dd)
        O.anonymize(dd.oid(), replacement_map=m)  # Study level doesn't return image
        O.delete(dd.oid(), dlvl=DLv.INSTANCE)


if __name__ == "__main__":

    ROOT_PATH = "~/data/dcm"
    R = mk_registry(ROOT_PATH, "registry.pkl", rebuild=True)

    print("\nSERIES")
    print("-----------------")
    pprint(R.find({"dlvl": DLv.SERIES}))

    print("\nSTUDIES")
    print("-----------------")
    pprint(R.find({"dlvl": DLv.STUDY}))

    exit()

    O = Orthanc()
    O.clear()

    D = DicomDirectory(root=ROOT_PATH)

    anonymize_and_upload(R, D, O)
