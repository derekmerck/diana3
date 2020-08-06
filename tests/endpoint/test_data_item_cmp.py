import logging
import itertools
import numpy as np
from diana.endpoint import DataItem, ComparatorType


def test_dynamic_cmp():

    _meta_a = {"id": "a"}
    _meta_b = {"id": "b"}

    _data_1 = np.array([1])
    _data_2 = np.array([2])

    _file_1 = b"12345678"
    _file_2 = b"abcdefgh"

    cross = itertools.product( [_meta_a, _meta_b],
                               [_data_1, _data_2],
                               [_file_1, _file_2] )
    perms = itertools.permutations(cross, 2)

    def comparisons( args1, args2 ):
        a = DataItem(meta=args1[0], data=args1[1], binary=args1[2])
        b = DataItem(meta=args2[0], data=args2[1], binary=args2[2])

        DataItem.comparator = ComparatorType.STRICT
        assert(a == a)
        assert(b == b)
        assert(a != b)

        DataItem.comparator = ComparatorType.METADATA
        assert(a == a)
        assert(b == b)
        assert(a != b if a.meta != b.meta else a == b)

        DataItem.comparator = ComparatorType.DATA
        assert(a == a)
        assert(b == b)
        assert(a != b if a.data != b.data else a == b)

        DataItem.comparator = ComparatorType.BINARY
        assert(a == a)
        assert(b == b)
        assert(a != b if a.binary != b.binary else a == b)

    for p in perms:
        comparisons(*p)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_cmp()