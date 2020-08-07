""""
Create a test orthanc instance:
$ docker run --rm -d -p 8042:8042 derekmerck/orthanc-wbvc
"""
import logging
from diana.services import Orthanc

# TODO: Orthanc test for get/put/find etc.


def test_orthanc():
    O = Orthanc()
    assert( O.status( ) )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_orthanc()
