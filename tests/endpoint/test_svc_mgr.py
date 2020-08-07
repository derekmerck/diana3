import tempfile
import yaml
from diana.endpoint import ServiceManager
import diana.services  # Registers classes with factory
import pytest

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

    MMM = ServiceManager.from_descs(data="{orthanc:{ctype: Orthanc}}")
    assert len( MMM.status() ) == 1

    with pytest.raises(yaml.parser.ParserError):
        ServiceManager.from_descs(data="{orthanc:{ctype: Orthanc}")

    with pytest.raises(KeyError):
        ServiceManager.from_descs(data="{orthanc:{ctype: Orthanc111}}")


if __name__ == "__main__":
    test_mgr_from_descs()