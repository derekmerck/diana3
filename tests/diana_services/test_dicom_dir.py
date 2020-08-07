import logging
import os
import tempfile
import pathlib
from diana.services import DicomDirectory
from diana.exceptions import InvalidDicomException
import pytest

rootp = "~/data/dcm"


def test_get():
    D = DicomDirectory(root=rootp)
    fn = "ibis1/01001_2.16.840.1.113669.632.21.1139687029.3025563835.31534914061935431.dcm"
    d = D.get(fn)
    assert d.tags["PatientID"] == "123456789"

    fn = "ibis2/IM100"
    d = D.get(fn)
    assert d.tags["PatientID"] == "15.03.26-07:44:14-STD-1.3.12.2.1107.5.1.4.66502"



# Has to recurse for this to work at all
def test_inventory():
    D = DicomDirectory(root=rootp)
    inv = D.inventory()
    # Each has about 350+ studies
    assert len(inv) > 700


def test_status_and_exceptions():
    with tempfile.TemporaryDirectory() as tmp:
        D = DicomDirectory(root=tmp)
        assert( D.status() )
        (pathlib.Path(tmp) / "test").touch()
        with pytest.raises(InvalidDicomException):
            D.get("test")
        with pytest.raises(FileNotFoundError):
            D.get("testtesttest")

    assert D.get("test", ignore_errors=True) is None
    assert D.get("testtesttest", ignore_errors=True) is None
    assert not D.status()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_status_and_exceptions()
