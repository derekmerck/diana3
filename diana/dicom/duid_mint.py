"""
DICOM Hash UID Mint

Derek Merck, Spring 2020

Minting reproducible UIDs is important for anticipating the OIDs of anonymized
studies and for ensuring that studies are linked by SeriesUI and StudyUID, even
when individual image instances are anonymized statelessly.

Conversely, tying the InstanceUID to pixel-data or other data features can help
ensure that multiple copies of identical image data collide at the same DICOM UID
space.
"""

import typing as typ
import attr
import hashlib
from .utils import DLv


def hash2int(h, digits):
    return int(h.hexdigest(), 16) % (10 ** digits)


def hash_str(s, digits=2):
    return str(hash2int(hashlib.sha1(str(s).encode("UTF8")), digits))


@attr.s
class DcmUIDMint(object):

    prefix: str = "1.2.826.0.1.3680043.10.43"
    """
    Prefix parts:
      - 1 - iso
      - 2 - ansi
      - 840 - us
      - 0.1.3680043.10.43 - sub-organization within medicalconnections.co.uk

    A 25 character prefix leaves 39 digits and stops available (64 chars max)
    """

    # This is the namespace of the mint, it is encoded into each UID
    namespace: str = "dicom"

    @classmethod
    def hashes_from_uid(cls, instance_uid: str) -> typ.Dict[str, str]:
        # Convenience function to extract the hex ihash suffix from an inst ihash uid
        # B/c the hashed uid is lossy, only the first 10-hex values of the meta and
        # data hash can be recovered.
        if not instance_uid.startswith(DcmUIDMint.prefix):
            raise ValueError(f"Bad prefix")
        working_str = instance_uid[len(DcmUIDMint.prefix)+1:]

        try:
            schema, namespace, *suffix = working_str.split('.')
        except:
            raise ValueError("Not in duid mint schema")

        if schema == hash_str("hash_uid", 2):

            res = {
                "schema": "hash_uid",
                "ns_hash": str(hex(int(namespace)))[2:],
                "dlvl": DLv( int(suffix[0]) ),
                "mhash_s": str(hex(int(suffix[1])))[2:],
                "dhash_s": str(hex(int(suffix[2])))[2:]
            }
            return res

        raise ValueError(f"Schema {schema} is not 'hash_uid'")

    def content_hash_uid(self,
                 hex_mhash: str,
                 hex_dhash: str,
                 dlvl: DLv = DLv.INSTANCE,
                 namespace: str = None):
        """
        UID format suitable for validating header and pixel content independently.

        An hash uid has the form:

          `prefix.schema.namespace.lvl.mhash.dhash`
           {25+1}  {2+1}  {2+1}   {3+1}{10+1}{10+1}

        Where
          - prefix = 25 digits + stop                       26
          - schema = stop + 2 digits                   +3 = 29
          - namespace = 2 digits + stop                +3 = 32
          - level = 1 digit + stop                     +2 = 34
          - 12-bit mhash = 12 digits + stop           +13 = 47
          - 12-bit dhash = 12 digits                  +12 = 59

        Total length is 59 chars

        A single instance study will result in the same content hash for
        study, series, and instance.  A single series study will share the
        content hash for both the study and series, so we have to use a
        DICOM-level field (inst=0,ser=1,stu=2) to guarantee uniqueness.

        Similarly, users can force a totally clean UID while maintaining the
        reference content hash suffix for a freshly copied/anonymized image by
        manually setting the app_id to something unique like "anon".

        Annotations are intended to include validation data, like an abbreviated
        series and study content hash for reference, hence they are also passed using
        hexidecimal representation.
        """

        _namespace = hash_str( namespace or self.namespace )
        schema = hash_str("hash_uid", 2)
        level = dlvl.value
        dec_mhash = int(hex_mhash, 16) / 2**(4*12)
        dec_dhash = int(hex_dhash, 16) / 2**(4*12)

        bitlen = len(hex_mhash) * 4
        # 42-bits available for 12 decimal digits (4*12)
        shift = bitlen - 40

        dec_mhash = int(hex_mhash, 16) >> shift
        dec_dhash = int(hex_dhash, 16) >> shift

        uid = f"{DcmUIDMint.prefix}.{schema}.{_namespace}.{level}.{dec_mhash}.{dec_dhash}"
        return uid
