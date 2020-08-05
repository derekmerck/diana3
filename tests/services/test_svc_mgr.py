from pprint import pprint
from diana.endpoint import ServiceManager
from diana.services import DicomDirectory, Orthanc  # Registers classes with factory
# from diana.endpoint.persistence.redis_persistence import RedisPersistenceBackend

service_text = \
"""
orthanc:
  ctype: Orthanc
  url:   http://localhost:8042

dcmdir:
  ctype: DicomDirectory
  root:  /Users/derek/data/bdr_ibis1
"""


def test_mgr_from_descs():
    M = ServiceManager.from_descs(data=service_text)
    assert len( M.status() ) == 2


if __name__ == "__main__":
    test_mgr_from_descs()