#!/usr/bin/env python3
"""
VIN encryption tests for MOBIVIDProvider (AES-256-GCM)
======================================================

Exercises the provider's real VIN cipher WITHOUT a blockchain node: the
provider is built with ``__new__`` and only the VIN-key state is populated,
so no web3 connection is required.

Proves:
    * _encrypt_vin -> _decrypt_vin round-trips the exact VIN,
    * the key is derived from the provider master key and NOT discarded
      (the old code generated a key and threw it away),
    * _decrypt_vin returns the VIN, not the old "[ENCRYPTED_VIN]" placeholder,
    * a tampered ciphertext fails the GCM auth tag,
    * a wrong (different-master) key fails,
    * the plaintext VIN never appears in the stored ciphertext.

Run: python3 -m pytest scripts/test_vin_encryption.py -v   (from cv2x-testbed/)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from identity.mobi_vid_provider import MOBIVIDProvider  # noqa: E402
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: E402
from cryptography.exceptions import InvalidTag  # noqa: E402

VIN = "1HGBH41JXMN109186"
VEHICLE = "0x0123456789abcdef0123456789abcdef01234567"


def _provider(master_key=None):
    """Build a provider exercising only the VIN cipher (no web3 connection)."""
    p = MOBIVIDProvider.__new__(MOBIVIDProvider)
    p.vin_master_key = master_key or AESGCM.generate_key(bit_length=256)
    p.vin_encryption_keys = {}
    return p


def test_encrypt_decrypt_round_trip():
    p = _provider()
    ct = p._encrypt_vin(VIN, VEHICLE)
    assert p._decrypt_vin(ct, VEHICLE) == VIN
    # No more "[ENCRYPTED_VIN]" placeholder.
    assert p._decrypt_vin(ct, VEHICLE) != "[ENCRYPTED_VIN]"


def test_key_is_retained_not_discarded():
    p = _provider()
    ct = p._encrypt_vin(VIN, VEHICLE)
    # The per-vehicle key is cached (kept), and re-derivable from the master.
    assert VEHICLE in p.vin_encryption_keys
    assert p.export_vin_key(VEHICLE) == p.vin_encryption_keys[VEHICLE]
    assert len(p.export_vin_key(VEHICLE)) == 32
    # A fresh provider with the SAME master key decrypts the same ciphertext.
    p2 = _provider(master_key=p.vin_master_key)
    assert p2._decrypt_vin(ct, VEHICLE) == VIN


def test_plaintext_never_in_ciphertext():
    p = _provider()
    ct = p._encrypt_vin(VIN, VEHICLE)
    assert VIN not in ct
    assert VIN.encode("utf-8").hex() not in ct


def test_tampered_ciphertext_fails():
    p = _provider()
    ct = p._encrypt_vin(VIN, VEHICLE)
    blob = bytearray.fromhex(ct)
    blob[-1] ^= 0x01
    with pytest.raises(InvalidTag):
        p._decrypt_vin(blob.hex(), VEHICLE)


def test_wrong_master_key_fails():
    p = _provider()
    ct = p._encrypt_vin(VIN, VEHICLE)
    other = _provider()  # different random master key
    with pytest.raises(InvalidTag):
        other._decrypt_vin(ct, VEHICLE)


def test_wrong_vehicle_identity_fails_aad():
    p = _provider()
    ct = p._encrypt_vin(VIN, VEHICLE)
    # Same master key, but decrypting under a different vehicle identity
    # (fresh key from the derivation salt AND mismatched AAD) must fail.
    p.vin_encryption_keys.clear()
    with pytest.raises(InvalidTag):
        p._decrypt_vin(ct, "0x0000000000000000000000000000000000000000")
