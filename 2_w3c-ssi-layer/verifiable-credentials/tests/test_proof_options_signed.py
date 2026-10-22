"""Every proof option is covered by the signature (WM-1 audit, finding U-F3a).

A mutant that signs only the document body (dropping `created`, `challenge`, `domain` and the other proof
options from the signed payload) passed all 358 Python tests: the code was right but nothing pinned it.
Each test edits one proof option that no other check inspects and expects the verification to fail.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vc_holder import HolderWallet  # noqa: E402
from vc_issuer import CredentialIssuer  # noqa: E402
from vc_verifier import CredentialVerifier  # noqa: E402

CLAIMS = {"vin": "5YJ3E1EA0PF123456", "make": "Tesla", "model": "Model 3", "year": 2024,
          "manufacturingDate": "2024-01-15"}


def _setup():
    issuer = CredentialIssuer.with_ethr_did()
    wallet = HolderWallet.with_ethr_did()
    verifier = CredentialVerifier(revocation_registry=issuer.revocation_registry)
    claims = dict(CLAIMS, manufacturerDid=issuer.issuer_did)
    vc = issuer.issue_credential("VehicleBirthCertificate", wallet.holder_did, claims=claims,
                                 validity_days=365)["verifiableCredential"]
    return issuer, wallet, verifier, vc


def test_baseline_credential_verifies():
    _, _, verifier, vc = _setup()
    assert verifier.verify_credential(vc).valid


def test_edited_proof_created_is_rejected():
    _, _, verifier, vc = _setup()
    t = copy.deepcopy(vc)
    t["proof"]["created"] = "2000-01-01T00:00:00Z"
    assert not verifier.verify_credential(t).valid


def test_presentation_challenge_rewritten_to_a_new_nonce_is_rejected():
    _, wallet, verifier, vc = _setup()
    cid = wallet.store_credential({"verifiableCredential": vc})
    vp = wallet.create_presentation([cid], challenge="nonce-1", domain="verifier.example")
    assert verifier.verify_presentation(vp, "nonce-1", "verifier.example")[0]
    replayed = copy.deepcopy(vp)
    replayed["proof"]["challenge"] = "nonce-2"            # an attacker re-labels a captured VP
    assert not verifier.verify_presentation(replayed, "nonce-2", "verifier.example")[0]


def test_presentation_domain_rewritten_is_rejected():
    _, wallet, verifier, vc = _setup()
    cid = wallet.store_credential({"verifiableCredential": vc})
    vp = wallet.create_presentation([cid], challenge="nonce-1", domain="verifier.example")
    moved = copy.deepcopy(vp)
    moved["proof"]["domain"] = "other-verifier.example"
    assert not verifier.verify_presentation(moved, "nonce-1", "other-verifier.example")[0]
