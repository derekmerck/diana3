import os
import logging
from diana.dixel.dixel import Dixel


fp = "~/data/dcm"
# Dixel doesn't auto-majickally expand paths
fp = os.path.expanduser(fp)


def test_from_file():
    fn = "ibis2/IM100"
    d = Dixel.from_file(os.path.join(fp, fn))
    assert d.tags["PatientID"] == "15.03.26-07:44:14-STD-1.3.12.2.1107.5.1.4.66502"

    print(d)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_from_file()