"""
Create a test redis instance:
$ docker run --rm --name my_redis -p 6379:6379 -d redis
"""
from diana.endpoint import PersistenceBackend
# This is not directly imported in the module init to
# avoid unnecessary dependency on Redis
from diana.endpoint.persistence.redis_persistence import RedisPersistenceBackend


def test_persistence(PBE: PersistenceBackend.__class__):
    # For a pickle be, these have to be synchronous b/c they only update on init
    # For a redis be, they can be arbitrary
    P = PBE()
    P["abc"] = 123

    # A new shelf will have the same values
    Q = PBE()
    assert( P["abc"] == Q["abc"] )

    # A new shelf in a different ns will have different values
    R = PBE(namespace="test")
    assert( R["abc"] is None )

    # Clearing the shelf will clear any new shelves as well
    P.clear()
    S = PBE()
    assert(S["abc"] is None)


if __name__ == "__main__":
    test_persistence(PersistenceBackend)
    test_persistence(RedisPersistenceBackend)
