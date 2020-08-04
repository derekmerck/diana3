from enum import Enum
import logging
from multiprocessing import Process
from functools import partial
from diana.endpoint.daemons.watcher import *


class EventType(Enum):
    CHANGED = "changed"


class MockObservable(ObservableMixin):

    # Whenever "changes" is invoked, return single "CHANGED" event
    # with the data "hello"
    def changes(self):
        return [Event(event_type=EventType.CHANGED, data="hello")]

    # Print the passed data, along with a kwarg provided by partial
    def changed_handler(self, data, var=None):
        s = f"{self._uuid.hex[0:8]} says var={var} and data={data}"
        print(s)

def test_watcher():
    mock = MockObservable()

    # When "mock" generates a "CHANGED" event, print the data
    t0 = Trigger(
        source=mock,
        event_type=EventType.CHANGED,
        handler=print
    )

    # When "mock" generates a "CHANGED" event, call a handler on
    # the source with additoinal kwargs
    t1 = Trigger(
        source=mock,
        event_type=EventType.CHANGED,
        handler=partial(mock.changed_handler, var="GOODBYE")
    )

    D = Watcher(triggers=[t0, t1])
    D.handle_all()

    process = Process(target=D.run, args=())
    process.start()

    time.sleep(5.0)  # Should print hello a few times, once a second

    process.terminate()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_watcher()
