"""
Review 02, R2-L5: the identity-theft cell of the security matrix
(4_comparison-framework/security-analysis/attack_scenarios.py) must exercise
the S-1 holder binding, not only the weaker same-DID/wrong-key thief.

The realistic thief presents the victim's credential under the thief's OWN
did:ethr, with a VP the thief signs correctly. Only the S-1 check (the VP
holder must be the credential subject) stops it. Removing that check makes
test_own_did_thief_is_rejected_by_holder_binding fail.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))
_SEC = os.path.join(_REPO, "4_comparison-framework", "security-analysis")
_VC = os.path.join(_REPO, "2_w3c-ssi-layer", "verifiable-credentials")
for _p in (_SEC, _VC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import attack_scenarios  # noqa: E402
from vc_holder import HolderWallet  # noqa: E402
from vc_issuer import CredentialIssuer  # noqa: E402
from vc_verifier import CredentialVerifier  # noqa: E402


def _setup():
    issuer = CredentialIssuer.with_ethr_did()
    victim = HolderWallet.with_ethr_did()
    verifier = CredentialVerifier(revocation_registry=issuer.revocation_registry)
    vc = issuer.issue_credential(
        "VehicleBirthCertificate", victim.holder_did,
        claims={"vin": "5YJ3E1EA0PF123456", "make": "Tesla", "model": "3",
                "year": 2024, "manufacturingDate": "2024-01-15",
                "manufacturerDid": issuer.issuer_did},
        validity_days=None,
    )["verifiableCredential"]
    return victim, vc, verifier


def test_genuine_holder_control_passes():
    victim, vc, verifier = _setup()
    cid = victim.store_credential({"verifiableCredential": vc, "disclosures": None})
    vp = victim.create_presentation([cid], challenge="c-ok", domain="dmv.gov.bc.ca")
    ok, report = verifier.verify_presentation(vp, "c-ok", "dmv.gov.bc.ca")
    assert ok, report


def test_own_did_thief_is_rejected_by_holder_binding():
    victim, vc, verifier = _setup()
    res = attack_scenarios.identity_theft_attacks(victim, vc, verifier)["own_did"]
    assert res["thief_did"].startswith("did:ethr:")
    assert res["thief_did"] != victim.holder_did
    # The thief's VP proof itself is valid: the rejection is the S-1 binding.
    assert res["vp_proof_valid"] is True
    assert res["rejected"] is True
    assert res["errors"], "expected a holder_binding error"
    assert all("is not the credential subject" in e for e in res["errors"])


def test_same_did_wrong_key_thief_is_rejected_by_vp_proof():
    victim, vc, verifier = _setup()
    res = attack_scenarios.identity_theft_attacks(victim, vc, verifier)["same_did_wrong_key"]
    assert res["rejected"] is True
    assert any("not holder" in e for e in res["errors"])


def test_matrix_identity_theft_cell_is_defended_with_both_variants():
    cell = attack_scenarios.run_offchain_vc_attacks()["identity_theft"]
    assert cell["outcome"] == "DEFENDED"
    assert set(cell["variants"]) == {"same_did_wrong_key", "own_did"}
    assert all(v["rejected"] for v in cell["variants"].values())
