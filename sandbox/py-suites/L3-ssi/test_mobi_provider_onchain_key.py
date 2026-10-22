"""L3 — regression for defect D11b (docs/DEFECT_LOG.md).

The MOBI provider generated the vehicle's signing key after the birth transaction and
never published it, so a verifier that did not hold the provider's own registration
record had no authoritative key. Since the fix the key is anchored on-chain at
registration (MOBIVIDRegistry.anchorVehicleKey) and verify_message falls back to the
anchored attribute when it has no local record.

These tests run without a chain: the on-chain walk is stubbed at the provider's
`_resolve_key_on_chain` seam and the contract is a minimal fake exposing isRevoked.
The real walk is exercised by the L2 Hardhat regression (anchorVehicleKey) and by
cv2x-testbed/scripts/test_mobi_vid.py against a node.
"""
import copy

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from identity.base import IdentityProvider, IdentityType
from identity.mobi_vid_provider import MOBIVIDProvider

IDENTITY = "0x" + "ab" * 20
DID = f"did:ethr:0x7a69:{IDENTITY}"
BSM = {"type": "BSM", "lat": 49.26, "lon": -123.25, "speed": 13.4, "ts": 1700000000}


def _keypair():
    k = ec.generate_private_key(ec.SECP256K1())
    pub = k.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex()
    return k, pub


class _FakeFunctions:
    def __init__(self, revoked=False):
        self._revoked = revoked

    def isRevoked(self, _identity):
        revoked = self._revoked
        class _Call:
            def call(self):
                return revoked
        return _Call()


class _FakeContract:
    def __init__(self, revoked=False):
        self.functions = _FakeFunctions(revoked)


def _bare_provider(contract=None):
    p = MOBIVIDProvider.__new__(MOBIVIDProvider)
    IdentityProvider.__init__(p, IdentityType.ERC1056_DID)
    p.w3, p.contract, p.contract_address, p.vehicles, p.resolved_keys = None, contract, None, {}, {}
    return p


def _registering_provider():
    """The vehicle's own provider: holds the private key (signs) and the record."""
    p = _bare_provider()
    priv, pub = _keypair()
    p.vehicles[IDENTITY] = {"private_key": priv, "public_key": pub, "vin": "1HGBH41JXMN109186"}
    return p, priv, pub


def _verifier_with_chain_key(pub_on_chain, revoked=False):
    """A different party's provider: no local record; the chain holds the anchored key."""
    v = _bare_provider(_FakeContract(revoked))
    calls = []

    def fake_walk(identity, max_hops=64):
        calls.append(identity)
        if pub_on_chain is None:
            return None
        found = {"public_key": pub_on_chain, "valid_to": 4_000_000_000, "hops": 1, "resolved_at": 0}
        v.resolved_keys[identity] = found
        return found

    v._resolve_key_on_chain = fake_walk
    return v, calls


def test_verifier_without_local_record_uses_the_anchored_key():
    signer, _, pub = _registering_provider()
    signed = signer.sign_message(DID, BSM)
    verifier, calls = _verifier_with_chain_key(pub)
    ok, _ = verifier.verify_message(signed)
    assert ok is True
    assert calls == [IDENTITY]


def test_resolved_key_is_cached_after_the_first_walk():
    signer, _, pub = _registering_provider()
    verifier, calls = _verifier_with_chain_key(pub)
    assert verifier.verify_message(signer.sign_message(DID, BSM))[0] is True
    assert verifier.verify_message(signer.sign_message(DID, dict(BSM, ts=1700000001)))[0] is True
    assert calls == [IDENTITY]  # one walk, then the cache


def test_impostor_is_rejected_against_the_anchored_key():
    _, _, pub = _registering_provider()
    verifier, _ = _verifier_with_chain_key(pub)
    ipriv, ipub = _keypair()
    import json, hashlib
    digest = hashlib.sha256(json.dumps(BSM, sort_keys=True).encode()).digest()
    forged = {"message": BSM, "signature": ipriv.sign(digest, ec.ECDSA(hashes.SHA256())).hex(),
              "public_key": ipub, "vehicle_did": DID}
    assert verifier.verify_message(forged)[0] is False


def test_no_anchored_key_means_rejection_not_trust_in_the_message():
    signer, _, _ = _registering_provider()
    verifier, _ = _verifier_with_chain_key(None)
    assert verifier.verify_message(signer.sign_message(DID, BSM))[0] is False


def test_on_chain_revocation_wins_over_an_anchored_key():
    signer, _, pub = _registering_provider()
    verifier, _ = _verifier_with_chain_key(pub, revoked=True)
    assert verifier.verify_message(signer.sign_message(DID, BSM))[0] is False


def test_tampered_message_is_rejected_on_the_fallback_path():
    signer, _, pub = _registering_provider()
    verifier, _ = _verifier_with_chain_key(pub)
    signed = signer.sign_message(DID, BSM)
    tampered = copy.deepcopy(signed)
    tampered["message"]["speed"] = 99.0
    assert verifier.verify_message(tampered)[0] is False


def test_artifact_abi_carries_what_verification_needs():
    """The inline bootstrap ABI lacked isRevoked / lastChanged / the DID events; the
    provider now prefers the compiled artifact, which must carry them (and anchorVehicleKey)."""
    artifact = MOBIVIDProvider._load_artifact()
    assert artifact is not None, "cv2x-testbed/artifacts missing: run `cd cv2x-testbed && npx hardhat compile`"
    names = {e.get("name") for e in artifact["abi"]}
    for needed in ("isRevoked", "lastChanged", "anchorVehicleKey", "vehicleKeyAnchored",
                   "DIDAttributeChanged", "DIDOwnerChanged", "DIDDelegateChanged", "DIDRevoked"):
        assert needed in names, needed
