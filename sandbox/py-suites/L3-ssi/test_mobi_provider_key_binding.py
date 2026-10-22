"""L3 — regression for defect D11 (docs/DEFECT_LOG.md).

MOBIVIDProvider.verify_message used to reconstruct the public key from the signed
message itself, so an impostor signing with its own key under a vehicle's DID was
accepted. Verification is now bound to the key registered for the vehicle. Runs
without a chain: the registration record is populated directly, as
register_vehicle_birth would, and no contract is attached.
"""
import copy
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from identity.base import IdentityProvider, IdentityType
from identity.mobi_vid_provider import MOBIVIDProvider

IDENTITY = "0x" + "ab" * 20
DID = f"did:ethr:0x7a69:{IDENTITY}"


def _keypair():
    k = ec.generate_private_key(ec.SECP256K1())
    pub = k.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex()
    return k, pub


def _provider_with_vehicle():
    # MOBIVIDProvider.__init__ probes the chain and raises without one; the sign/verify
    # paths need only the base-class state, the registration record and no contract.
    p = MOBIVIDProvider.__new__(MOBIVIDProvider)
    IdentityProvider.__init__(p, IdentityType.ERC1056_DID)
    p.w3, p.contract, p.contract_address, p.vehicles = None, None, None, {}
    priv, pub = _keypair()
    p.vehicles[IDENTITY] = {"private_key": priv, "public_key": pub, "vin": "1HGBH41JXMN109186"}
    return p, priv, pub


def _sign_with(priv, pub, message, did=DID):
    import json, hashlib
    digest = hashlib.sha256(json.dumps(message, sort_keys=True).encode()).digest()
    sig = priv.sign(digest, ec.ECDSA(hashes.SHA256()))
    return {"message": message, "signature": sig.hex(), "public_key": pub, "vehicle_did": did}


BSM = {"type": "BSM", "lat": 49.26, "lon": -123.25, "speed": 13.4, "ts": 1700000000}


def test_legitimate_message_verifies():
    p, priv, pub = _provider_with_vehicle()
    signed = p.sign_message(DID, BSM)
    ok, _ = p.verify_message(signed)
    assert ok is True


def test_impostor_with_own_key_under_vehicle_did_is_rejected():
    p, _, _ = _provider_with_vehicle()
    ipriv, ipub = _keypair()
    forged = _sign_with(ipriv, ipub, BSM)             # valid signature, wrong key, right DID
    ok, _ = p.verify_message(forged)
    assert ok is False


def test_embedded_key_must_match_registered_key():
    p, priv, pub = _provider_with_vehicle()
    signed = p.sign_message(DID, BSM)
    _, ipub = _keypair()
    spoofed = dict(signed, public_key=ipub)           # right signature, lying about the key
    ok, _ = p.verify_message(spoofed)
    assert ok is False


def test_unknown_vehicle_is_rejected():
    p, priv, pub = _provider_with_vehicle()
    other = f"did:ethr:0x7a69:0x{'cd' * 20}"
    ok, _ = p.verify_message(_sign_with(priv, pub, BSM, did=other))
    assert ok is False


def test_revoked_vehicle_is_rejected():
    p, priv, pub = _provider_with_vehicle()
    signed = p.sign_message(DID, BSM)
    p.vehicles[IDENTITY]["revoked"] = True
    ok, _ = p.verify_message(signed)
    assert ok is False


def test_tampered_message_is_rejected():
    p, priv, pub = _provider_with_vehicle()
    signed = p.sign_message(DID, BSM)
    tampered = copy.deepcopy(signed); tampered["message"]["speed"] = 99.0
    ok, _ = p.verify_message(tampered)
    assert ok is False
