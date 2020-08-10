import typing as typ
import requests
import attr
from hashlib import sha1
from libsvc.endpoint import Endpoint, RestAgent, RTy, Serializable, UID
from diana.dicom import DLv
from diana.dixel.dixel import Dixel


def dlvl_to_orthanc_resource(dlvl: DLv) -> str:
    if dlvl == DLv.STUDY:
        return "studies"
    elif dlvl == DLv.SERIES:
        return "series"
    elif dlvl == DLv.INSTANCE:
        return "instances"
    raise ValueError


DLv.opath = dlvl_to_orthanc_resource


@attr.s(auto_attribs=True, hash=False)
class Orthanc(Endpoint, RestAgent, Serializable):
    """DIANA API and helpers for Orthanc"""

    url: str = "http://localhost:8042"
    username: str = "orthanc"
    password: str = "passw0rd"
    aet: str = "ORTHANC"

    metadata_keys: typ.ClassVar = [
        "LastUpdate",
        "AnonymizedFrom",
        "ReceptionDate",
        "RemoteAet",
        "ModifiedFrom"
        "Origin",
        "TransferSyntax",
        "SopClassUid",
        "IndexInSeries",             # instance level only
        "ExpectedNumberOfInstances"  # series level only
    ]

    def setup_new_session(self) -> requests.Session:
        session = requests.Session()
        session.auth = (self.username, self.password)
        return session
        # TODO: Check and see if the "diana" metadata key is available and append it to the list

    def status(self, **kwargs) -> bool:
        resource = "system"
        r = self.request(resource, **kwargs)
        return r is not None

    def get(self, oid: UID, dlvl: DLv = DLv.STUDY, binary: bool = False, **kwargs) -> Dixel:
        resource = f"{dlvl.opath()}/{oid}"
        tags = self.request(resource, **kwargs)
        d = Dixel.from_tags(tags)
        if binary:
            if dlvl > DLv.INSTANCE:
                route = "archive"
            else:
                route = "file"
            resource = f"{dlvl.opath()}/{oid}/{route}"
            _file = self.request(resource, **kwargs)
            if _file:
                d.file = _file
        return d

    def find(self, query: typ.Dict, *args, **kwargs) -> typ.List[UID]:
        resource = "tools/find"
        return self.request(resource, RTy.POST, json=query)

    def rfind(self, query: typ.Dict, remote_node: str, retrieve=False) -> typ.List[typ.Dict]:
        raise NotImplementedError

    def put(self, dixel: Dixel, *args, **kwargs):
        if dixel.dlvl > DLv.INSTANCE:
            raise TypeError("Can only send instance objects")
        if not dixel.binary:
            raise ValueError("No file data found")
        resource = "instances"
        # headers = {'content-type': 'application/dicom'}
        r = self.request(resource, RTy.POST, data=dixel.binary)
        return r

    def delete(self, oid: UID, dlvl: DLv = DLv.STUDY, **kwargs) -> bool:
        resource = f"{dlvl.opath()}/{oid}"
        r = self.request(resource, RTy.DELETE)
        return r

    def inventory(self, dlvl: DLv = DLv.STUDY, **kwargs) -> typ.List[UID]:
        resource = f"{dlvl.to_orthanc_resource()}"
        r = self.request(resource)
        return r

    def clear(self, *args, **kwargs):
        studies = self.inventory()
        for oid in studies:
            self.delete(oid)

    # Other useful API calls

    def anonymize(self, oid: UID, dlvl: DLv = DLv.STUDY,
                  replacement_map: typ.Dict = None) -> typ.Union[bytes, str]:
        resource = f"{dlvl.opath()}/{oid}/anonymize"
        r = self.request(resource, RTy.POST, json=replacement_map)
        if dlvl >= DLv.SERIES:
            # Anonymizing a collection returns the oid of the new object
            return r.get("ID")
        else:
            # Anonymizing an instance returns entire new file as bytes
            # It must be resubmitted as a new image to access it from
            # the Orthanc instance
            return r

    def modify(self, oid: UID, dlvl: DLv = DLv.STUDY,
               replacement_map: typ.Dict = None) -> typ.Union[bytes, str]:
        resource = f"{dlvl.opath()}/{oid}/modify"
        r = self.request(resource, RTy.POST, json=replacement_map)
        if dlvl >= DLv.SERIES:
            return r.get("ID")
        else:
            return r

    def send(self, oid: UID, dest: str, dest_type: str):
        if dest_type not in ["peers", "modalities"]:
            raise ValueError("dest_type should be either 'peers' or 'modalities'")
        resource = f"{dest_type}/{dest}/store"
        data = oid
        headers = {'content-type': 'application/text'}
        self.request(resource, RTy.POST, data=data, headers=headers)

    def statistics(self, **kwargs):
        return self.request("statistics", **kwargs)

    def system(self, **kwargs):
        return self.request("system", **kwargs)

    def reset(self):
        return self.request("tools/reset")

    def changes(self, current=0, limit=10):
        params = { 'since': current, 'limit': limit }
        return self.request("changes", params=params)

    def recho(self, domain: str):
        resource = f"modalities/{domain}/echo"
        headers = {'content-type': 'application/text'}
        response = self.request(resource, RTy.POST, data=self.aet, headers=headers)
        return response

    def get_metadata(self, oid: UID, dlvl: DLv, key: str ):
        if key not in Orthanc.metadata_keys:
            raise ValueError("No such metadata key")
        resource = "{dlvl.opath()}/{oid}/metadata/{key}"
        return self.request(resource)

    def put_metadata(self, oid: str, dlvl: DLv, key: str, value: str):
        if key not in Orthanc.metadata_keys:
            raise ValueError("No such metadata key")
        resource = f"{dlvl.opath()}/{oid}/metadata/{key}"
        data = value
        return self.request(resource, RTy.PUT, data=data)


Serializable.Factory.register(Orthanc)


def get_dixel_oid(dixel: Dixel, dlvl: DLv = None) -> UID:
    _dlvl = dlvl or dixel.dlvl
    if not dixel.tags.get("PatientID"):
        raise KeyError("No patient ID, cannot predict the oid")
    if dlvl == DLv.INSTANCE:
        s = "|".join([dixel.tags["PatientID"], dixel.stuid, dixel.sruid, dixel.inuid])
    elif dlvl == DLv.SERIES:
        s = "|".join([dixel.tags["PatientID"], dixel.stuid, dixel.sruid])
    elif dlvl == DLv.STUDY:
        s = "|".join([dixel.tags["PatientID"], dixel.stuid])
    elif dlvl == DLv.PATIENT:
        s = dixel.tags["PatientID"]
    else:
        raise TypeError("Unknown dicom level for oid")
    h = sha1(s.encode("UTF8"))
    d = h.hexdigest()
    s = '-'.join(d[i:i + 8] for i in range(0, len(d), 8))
    return s


Dixel.oid = get_dixel_oid
