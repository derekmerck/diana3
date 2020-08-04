import logging
from pathlib import Path
import os
import time
import tempfile
from diana.endpoint.daemons.observable_dir import ObservableDirectory

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    with tempfile.TemporaryDirectory() as fp:
        logging.debug(fp)
        logging.debug(os.listdir(fp))

        O = ObservableDirectory(root=fp)
        O.poll_events()

        time.sleep(0.5)
        Path(f"{fp}/test").touch()
        logging.debug(os.listdir(fp))

        time.sleep(3.0)
