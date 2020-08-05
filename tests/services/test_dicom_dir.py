import logging
import tempfile
from diana.dixel import Dixel
from diana.services import DicomDirectory

# TODO: Set this to something for a test-time dl
fp = "/Users/derek/data/bdr_ibis1"


def test_get():
    D = DicomDirectory(root=fp)
    fn = "01001_2.16.840.1.113669.632.21.1139687029.3025563835.31534914061935431.dcm"
    d = D.get(fn)
    assert d.tags["PatientID"] == "123456789"


def test_inventory():
    D = DicomDirectory(root=fp)
    inv = D.inventory()
    assert len(inv) > 100


def test_status():
    with tempfile.TemporaryDirectory() as tmp:
        D = DicomDirectory(root=tmp)
        assert( D.status() )

    assert not D.status()




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_status()