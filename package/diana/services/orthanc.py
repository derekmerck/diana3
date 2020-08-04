import typing as typ
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


class Orthanc(Endpoint, RestAgent, Serializable):

    def get(self, oid: UID, dlvl: DLv = DLv.STUDY, **kwargs) -> Dixel:
        resource = f"{dlvl.to_orthanc_resource()}/{oid}"
        tags = self.request(resource, "get")
        d = Dixel.from_tags(tags)
        return d

    def get_binary(self, oid: UID, dlvl: DLv = DLv.STUDY, **kwargs) -> Dixel:
        resource = f"{dlvl.to_orthanc_resource()}/{oid}/file"
        file = self.request(resource, "get")
        d = Dixel.from_file(file)
        return d

    def put(self, dixel: Dixel, *args, **kwargs):
        if dixel.dlvl > DLv.INSTANCE:
            raise TypeError("Can only write files for instance objects")
        if not dixel.file:
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

    def status(self) -> bool:
        resource = "system"
        r = self.request(resource)
        return r is not None

