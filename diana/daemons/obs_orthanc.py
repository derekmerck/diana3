
import typing as typ
from enum import Enum
import requests
import attr
from libsvc.endpoint import Serializable
from libsvc.daemon import ObservableMixin, Event
from diana.services import Orthanc

# orthanc:8042/changes looks like this:
"""
{
   "Changes" : [
      {
         "ChangeType" : "NewInstance",
         "Date" : "20200908T170549",
         "ID" : "ac9b9cb1-7929a293-e3508457-683f7a7d-10bc31b2",
         "Path" : "/instances/ac9b9cb1-7929a293-e3508457-683f7a7d-10bc31b2",
         "ResourceType" : "Instance",
         "Seq" : 1
      }
   ],
   "Done" : true,
   "Last" : 4
}
Change types:  NewInstance, NewSeries, NewStudy, NewPatient, 
               StableSeries, StableStudy, StablePatient
"""


class OrthancEventType(Enum):
    INSTANCE_ADDED = "instance_added"
    SERIES_ADDED   = "series_added"
    STUDY_ADDED    = "study_added"
    PATIENT_ADDED  = "patient_added"
    SERIES_STABLE  = "series_stable"
    STUDY_STABLE   = "study_stable"
    PATIENT_STABLE = "patient_stable"


@attr.s(auto_attribs=True, hash=False)
class ObservableOrthanc(ObservableMixin, Orthanc):
    current_change: int = 0

    # Override default changes method to return a list of actionable events
    def changes(self, **kwargs) -> typ.List[Event]:
        params = { 'since': self.current_change, 'limit': 0 }

        try:
            r: typ.Dict = self.request("changes", params=params)
        except requests.exceptions.ConnectionError:
            return []

        events = []
        for change in r["Changes"]:
            # TODO: Lookup orthanc events format
            event_type = None
            if change["type"] == "NewInstance":
                event_type = OrthancEventType.INSTANCE_ADDED
            elif change["type"] == "StableStudy":
                event_type = OrthancEventType.STUDY_STABLE

            if event_type:
                event = Event(
                    event_type = event_type,
                    data = {"oid": change["ID"]}
                )
                events.append(event)

        self.current_change = r["Last"]
        return events


Serializable.Factory.register(ObservableOrthanc)
