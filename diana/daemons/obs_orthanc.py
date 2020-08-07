
import typing as typ
from enum import Enum
from service.daemon import ObservableMixin, Event, Serializable
from diana.services import Orthanc


class OrthancEventType(Enum):
    INSTANCE_ADDED = "instance_added"
    STUDY_STABLE = "study_stable"


class ObservableOrthanc(Orthanc, ObservableMixin):

    def changes(self) -> typ.List[Event]:
        events = []
        resource = "changes"
        r: typ.List[typ.Dict] = self.request(resource)
        for change in r:
            # TODO: Lookup orthanc events format
            event_type = None
            if change["type"] == "new_instance":
                event_type = OrthancEventType.INSTANCE_ADDED
            elif change["type"] == "study_stable":
                event_type = OrthancEventType.STUDY_STABLE

            if event_type:
                event = Event(
                    event_type = event_type,
                    data = change["oid"]
                )
                events.append(event)
            return events


Serializable.Factory.register(ObservableOrthanc)
