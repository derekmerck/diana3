"""
Provides persistent inventory and reverse lookups for
available Dixel items

Dixels are represented by headers and hashes, and have sets of
references to children

"""

import typing as typ
from enum import Enum, auto
import attr
from libsvc.endpoint import Endpoint, Serializable, UID, DataItem
from libsvc.persistence import RedisPersistenceBackend
from diana.dixel import Dixel

class KeyType(Enum):
    UUID = auto()
    MHASH = auto()
    DHASH = auto()
    BHASH = auto()
    DHUID = auto()


@attr.s(auto_attribs=True)
class RedisIndex(Endpoint, Serializable, RedisPersistenceBackend):

    def status(self) -> bool:
        pass

    def get(self, uid: UID, *args, **kwargs) -> Dixel:
        pass

    def find(self, query: typ.Dict, *args, **kwargs) -> typ.List[UID]:
        pass

    def put(self, data: Dixel, *args, **kwargs) -> UID:
        pass

    def delete(self, uid: UID, *args, **kwargs) -> bool:
        pass

    def inventory(self, *args, **kwargs) -> typ.Union[UID, DataItem]:
        pass
