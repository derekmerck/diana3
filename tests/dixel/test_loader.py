import os
import logging
from diana.dixel import Dixel

# TODO: Set this to something for a test-time dl
fp = "/Users/derek/data/bdr_ibis/bdr_ibis1"


def test_from_file():
    fn = "01001_2.16.840.1.113669.632.21.1139687029.3025563835.31534914061935431.dcm"
    d = Dixel.from_file(os.path.join(fp, fn))
    assert d.tags["PatientID"] == "123456789"

    print(d)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_from_file()