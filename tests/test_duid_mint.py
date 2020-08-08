from pprint import pprint
import logging
import hashlib
from diana.dicom import DcmUIDMint


def test_duid_mint():

    mhash = hashlib.sha3_224(b"0123456789abcdef").hexdigest()
    dhash = hashlib.sha3_224(b"fedcba9876543210").hexdigest()
    uid = DcmUIDMint().content_hash_uid(hex_mhash=mhash, hex_dhash=dhash)

    assert uid == "1.2.826.0.1.3680043.10.43.4.62.0.806243101896.283258269229"
    res = DcmUIDMint().hashes_from_uid(uid)

    assert mhash.startswith(res["mhash_s"])
    assert dhash.startswith(res["dhash_s"])

    # pprint(res)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_duid_mint()




