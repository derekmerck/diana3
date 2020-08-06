import tempfile
from diana.endpoint import ServiceManager
from diana.services import DicomDirectory, Orthanc  # Registers classes with factory

service_text = \
"""
orthanc:
  ctype: Orthanc
  url:   http://localhost:8042

dcmdir:
  ctype: DicomDirectory
  root:  /Users/derek/data/bdr_ibis
"""


def test_mgr_from_descs():
    M = ServiceManager.from_descs(data=service_text)
    assert len( M.status() ) == 2

    print(M.status())

    with tempfile.TemporaryFile("w+") as tmp:
        tmp.write(service_text)
        tmp.seek(0)
        MM = ServiceManager.from_descs(data=tmp)
        assert( len(MM.status() ) == 2)


if __name__ == "__main__":
    test_mgr_from_descs()