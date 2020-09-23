
"""
There are two "watching" routes

DcmDir -- add to registry
Registry -- stable study

Watch new file arrive
Once study is stable, compute study anonymization hash
collect all instances
  - upload each
  - anonymize each
Send study available email

"""

from libsvc.daemon import ObservableDirectory
from diana.services import

dcm_dir = "/data/incomming"

D = ObservableDirectory(root=dcm_dir)


def watcher():
    mock = MockObservable()

    # When "mock" generates a "CHANGED" event, print the data
    t0 = Trigger(
        source=mock,
        event_type=EventType.CHANGED,
        handler=print
    )

    # When "mock" generates a "CHANGED" event, call a handler on
    # the source with additional kwargs
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

    captured = capsys.readouterr()
    assert "var=GOODBYE and data=hello" in captured.out
