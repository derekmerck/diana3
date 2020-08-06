import typing as typ
import requests
import attr
from hashlib import sha1
from diana.endpoint import Endpoint, RestAgent, Serializable, UID
from diana.dicom import DLv
from diana.dixel import Dixel

oid = UID


def dlvl_to_orthanc_resource(dlvl: DLv) -> str:
    if dlvl == DLv.STUDY:
        return "studies"
    elif dlvl == DLv.SERIES:
        return "series"
    elif dlvl == DLv.INSTANCE:
        return "instances"


DLv.to_orthanc_resource = dlvl_to_orthanc_resource


@attr.s(auto_attribs=True, hash=False)
class Orthanc(Endpoint, RestAgent, Serializable):

    def setup_new_session(self) -> requests.Session:
        pass

    def status(self) -> bool:
        resource = "system"
        r = self.request(resource)
        return r is not None

    def get(self, oid: UID, dlvl: DLv = DLv.STUDY, binary: bool = False) -> Dixel:
        resource = f"{dlvl.to_orthanc_resource()}/{oid}"
        tags = self.request(resource, "get")
        d = Dixel.from_tags(tags)
        if binary:
            if dlvl > DLv.INSTANCE:
                route = "archive"
            else:
                route = "image"
            resource = f"{dlvl.to_orthanc_resource()}/{oid}/{route}"
            _file = self.request(resource, "get")
            if _file:
                d.file = _file
        return d

    def find(self, query: typ.Dict, *args, **kwargs) -> typ.List[UID]:
        raise NotImplementedError

    def rfind(self, query: typ.Dict, remote_node: str, retrieve=False) -> typ.List[typ.Dict]:
        raise NotImplementedError

    def put(self, dixel: Dixel, *args, **kwargs):
        if dixel.dlvl > DLv.INSTANCE:
            raise TypeError("Can only send instance objects")
        if not dixel.binary:
            raise ValueError("No file data found")
        resource = "instances"
        r = self.request(resource, "post", data=dixel.file)
        return r

    def delete(self, oid: UID, dlvl: DLv = DLv.STUDY, **kwargs) -> bool:
        resource = f"{dlvl.to_orthanc_resource()}/{oid}"
        r = self.request(resource, "delete")
        return r

    def inventory(self, dlvl: DLv = DLv.STUDY, **kwargs) -> typ.List[oid]:
        resource = f"{dlvl.to_orthanc_resource()}"
        r = self.request(resource)
        return r

    def clear(self, *args, **kwargs):
        studies = self.inventory()
        for oid in studies:
            self.delete(oid)


def orthanc_hash(PatientID: str,
                 StudyInstanceUID: str,
                 SeriesInstanceUID=None,
                 SOPInstanceUID=None) -> sha1:
    if not SeriesInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID])
    elif not SOPInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID])
    else:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID])


def dixel_oid(dixel, dlvl: DLv = None):
    _dlvl = dlvl or dixel.dlvl
    if not dixel.tags.get("PatientID"):
        raise KeyError("No patient ID, cannot predict the oid")
    if dlvl == DLv.INSTANCE:
        s = "|".join([dixel.tags["PatientID"], dixel.stuid, dixel.serid, dixel.inuid])
    elif dlvl == DLv.SERIES:
        s = "|".join([dixel.tags["PatientID"], dixel.stuid, dixel.serid])
    elif dlvl == DLv.STUDY:
        s = "|".join([dixel.tags["PatientID"], dixel.stuid])
    elif dlvl == DLv.PATIENT:
        s = dixel.tags["PatientID"]
    else:
        raise TypeError("Unknown dixel level for oid")
    return sha1(s.encode("UTF8"))


Dixel.oid = dixel_oid

Serializable.Factory.register(Orthanc)
