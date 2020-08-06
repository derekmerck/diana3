
import logging
import numpy as np
from diana.endpoint import DataItem, ComparatorType


def test_cmp():

    a1 = DataItem(meta={"id": "a"}, data=np.array([1]))
    A1 = DataItem(meta={"id": "a"}, data=np.array([1]))
    a2 = DataItem(meta={"id": "a"}, data=np.array([2]))
    b1 = DataItem(meta={"id": "b"}, data=np.array([1]))
    b2 = DataItem(meta={"id": "b"}, data=np.array([2]))

    assert ( a1 == a1 )
    assert not ( a1 == A1 )

    DataItem.comparator = ComparatorType.DATA
    assert ( a1 == A1 )
    assert ( a1 == b1 )
    assert ( a2 == b2 )
    assert not ( a1 == a2 )
    assert not ( a1 == b2 )
    assert not ( a1 == b2 )

    DataItem.comparator = ComparatorType.METADATA
    assert ( a1 == A1 )
    assert ( a1 == a2 )
    assert not ( a1 == b1 )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_cmp()