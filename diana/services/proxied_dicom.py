import typing as typ
import attr
from diana.libsvc import UID, Serializable
from diana.dicom import DLv
from .orthanc import Orthanc

@attr.s(auto_attribs=True)
class ProxiedDicomNode(Orthanc):

    remote_node: str = None  # Orthanc remote modality name

    # Actually returns a list of dicts the with the requested fields
    # could just return the stuid/serid/inst id by default and use that
    # as a unique key for a single-object get?
    # Or call it "find_many" and "get_many"?
    def find(self, query: typ.Dict, dlvl=DLv.STUDY, retrieve=False) -> typ.List[UID]:
        r = self.rfind(query, remote_node=self.remote_node, retrieve=retrieve)
        return r

    # May get multiple, should either catch that or return an iterator?
    def get(self, query: typ.Dict, dlvl=DLv.STUDY):
        r = self.rfind(query, dlvl=dlvl, remote_node=self.remote_node, retrieve=True)
        res = []
        for r in r:
            rr = self.get(r, dlvl=dlvl)
            res.append(rr)
        return res


Serializable.Factory.register(ProxiedDicomNode)
