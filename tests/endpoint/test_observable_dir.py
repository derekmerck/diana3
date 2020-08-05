import logging
from pathlib import Path
import os
import time
import tempfile
from diana.endpoint.daemons.observable_dir import ObservableDirectory


def test_observable_dir():

    with tempfile.TemporaryDirectory() as fp:
        logging.debug(fp)
        logging.debug(os.listdir(fp))
        assert(len(os.listdir(fp)) == 0)

        O = ObservableDirectory(root=fp)
        O.poll_events()

        time.sleep(0.2)
        Path(f"{fp}/test").touch()
        logging.debug(os.listdir(fp))
        assert(len(os.listdir(fp)) == 1)

        time.sleep(1.0)
        events = O.changes()

    assert(len(events)>0)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    test_observable_dir()
