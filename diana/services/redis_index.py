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

KEY_SEP = "/"
HASH_KEY_LEN = 10

class KeyType(Enum):
    UUID  = auto()
    MHASH = auto()
    DHASH = auto()
    BHASH = auto()
    DHUID = auto()

KTy = KeyType

class SlotType(Enum):
    VALUE = "value"
    DICT  = "dict"
    SET   = "set"

STy = SlotType


def to_redis(dixel: Dixel, pbe: RedisPersistenceBackend):

    N = 10
    key_bhash    = f"index/b:{dixel.bhash[:N]}/v"     # -> m:dixel.mhash[:N]
    key_children = f"index/m:{dixel.mhash[:N]}/s"     # -> set([mhashes])
    key_data     = f"index/m:{dixel.mhash[:N]}/d"     # -> dict(main_keys, hashes)
    key_serial   = f"index/m:{dixel.mhash[:N]}/v"     # -> pickle(object w/o data/binary)




@attr.s(auto_attribs=True)
class RedisIndex(Endpoint, Serializable, RedisPersistenceBackend):

    namespace: str = "index"

    def t(self, dixel: Dixel,
          kty: KTy = KTy.MHASH,
          sty: STy = STy.VALUE) -> str:

        if KeyType == KeyType.MHASH:
            h = dixel.mhash
        elif KeyType == KeyType.DHASH:
            h = dixel.dhash
        elif KeyType == KeyType.BHASH:
            h = dixel.dhash
        else:
            raise TypeError("Unknown key type")

        s = KEY_SEP.join([self.namespace,
                          h[:HASH_KEY_LEN],
                          sty.value])
        return s

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
