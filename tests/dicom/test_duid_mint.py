from pprint import pprint
import logging
import hashlib
from diana.dicom import DcmUIDMint, DLv


def test_duid_mint():

    mhash = hashlib.sha3_224(b"0123456789abcdef").hexdigest()
    dhash = hashlib.sha3_224(b"fedcba9876543210").hexdigest()
    print(mhash)
    print(dhash)

    uid = DcmUIDMint().content_hash_uid(hex_mhash=mhash, hex_dhash=dhash)
    assert uid == "1.2.826.0.1.3680043.10.43.4.62.0.806243101896.283258269229"

    res = DcmUIDMint().hashes_from_duid(uid)
    pprint(res)

    assert res.get("duid") == uid
    assert res.get("dlvl") == DLv.INSTANCE
    assert mhash.startswith(res["mhash_s"])
    assert dhash.startswith(res["dhash_s"])
    assert "namespace" in res
    assert res.get("namespace") == DcmUIDMint.namespace

    uid2 = DcmUIDMint().content_hash_uid(namespace="testing", hex_mhash=mhash, dlvl=DLv.STUDY)
    assert uid2 == "1.2.826.0.1.3680043.10.43.4.16.2.806243101896.0"

    res2 = DcmUIDMint().hashes_from_duid(uid2)
    pprint(res2)

    assert res2["dlvl"] == DLv.STUDY
    assert res2['ns_hash'] != res["ns_hash"]
    assert res2["dhash_s"] == "0"
    assert "namespace" not in res2


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_duid_mint()
