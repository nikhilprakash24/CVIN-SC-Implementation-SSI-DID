#!/usr/bin/env python3
"""
VIN cipher unit tests (AES-256-GCM)
===================================

Pure-crypto tests for the VID I VIN cipher in ``birth_certificate.py``. These
do NOT need a Hardhat node (unlike ``test_mobi_vid_layer.py``) and therefore
always run, proving the confidentiality/authenticity properties directly:

    * encrypt -> decrypt round-trips the exact VIN,
    * a tampered ciphertext fails the GCM auth tag (raises),
    * the wrong secret / wrong salt / wrong AAD all fail,
    * the plaintext VIN never appears in the stored/anchored ciphertext,
    * the key is derived (HKDF), never emitted in the artifact.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from birth_certificate import (  # noqa: E402
    decrypt_vin, derive_vin_key, encrypt_vin, new_vin_salt, salted_vin_hash,
)
from cryptography.exceptions import InvalidTag  # noqa: E402

VIN = "5YJ3E1EA0PF123456"
SECRET = "owner-only-secret"


def _fixture():
    salt = new_vin_salt()
    aad = salted_vin_hash(VIN, salt)
    ct = encrypt_vin(VIN, SECRET, salt=salt, aad=aad)
    return salt, aad, ct


def test_round_trip_recovers_exact_vin():
    salt, aad, ct = _fixture()
    assert decrypt_vin(ct, SECRET, salt=salt, aad=aad) == VIN


def test_ciphertext_never_leaks_plaintext_or_key():
    salt, aad, ct = _fixture()
    # No plaintext VIN in the artifact...
    assert VIN not in ct
    assert VIN.encode("utf-8").hex() not in ct
    # ...and no derived key material either.
    assert derive_vin_key(SECRET, salt).hex() not in ct
    assert ct.startswith("gcm1:")


def test_fresh_nonce_makes_ciphertext_nondeterministic():
    salt, aad, ct1 = _fixture()
    ct2 = encrypt_vin(VIN, SECRET, salt=salt, aad=aad)
    assert ct1 != ct2  # fresh 12-byte nonce per call
    assert decrypt_vin(ct2, SECRET, salt=salt, aad=aad) == VIN


def test_tampered_ciphertext_fails_auth_tag():
    salt, aad, ct = _fixture()
    blob = bytearray.fromhex(ct[len("gcm1:"):])
    blob[-1] ^= 0x01  # flip a tag byte
    with pytest.raises(InvalidTag):
        decrypt_vin("gcm1:" + blob.hex(), SECRET, salt=salt, aad=aad)


def test_wrong_secret_fails():
    salt, aad, ct = _fixture()
    with pytest.raises(InvalidTag):
        decrypt_vin(ct, "wrong-secret", salt=salt, aad=aad)


def test_wrong_salt_fails():
    salt, aad, ct = _fixture()
    with pytest.raises(InvalidTag):
        decrypt_vin(ct, SECRET, salt=new_vin_salt(), aad=aad)


def test_wrong_aad_fails():
    salt, _, ct = _fixture()
    with pytest.raises(InvalidTag):
        decrypt_vin(ct, SECRET, salt=salt, aad=b"\x00" * 32)


def test_bad_format_rejected():
    salt, aad, _ = _fixture()
    with pytest.raises(ValueError):
        decrypt_vin("xor1:deadbeef", SECRET, salt=salt, aad=aad)


def test_derived_key_is_256_bit_and_deterministic():
    salt = new_vin_salt()
    k1 = derive_vin_key(SECRET, salt)
    k2 = derive_vin_key(SECRET, salt)
    assert len(k1) == 32 and k1 == k2
    # Different salt -> different key (per-vehicle domain separation)
    assert derive_vin_key(SECRET, new_vin_salt()) != k1
