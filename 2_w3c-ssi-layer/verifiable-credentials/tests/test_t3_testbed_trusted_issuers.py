#!/usr/bin/env python3
"""
Review 02, T-3 — the cv2x testbed's VC shim and SUMO SSI layer use an
explicit trusted-issuer allow-list.

Before the fix every CredentialIssuer AND every HolderWallet in
`cv2x-testbed/identity/w3c_verifiable_credentials.py` registered itself in a
shared TrustedIssuerRegistry, so a vehicle could issue itself a
V2VSafetyCredential and SUMO's SSIIdentityLayer accepted its messages
(/tmp/review_d/poc_ssi_selfissued.py). These tests fail on 434669d.

Lives here (not under cv2x-testbed/) so the `pytest 2_w3c-ssi-layer` gate
runs it.
"""

import sys
import uuid
import warnings
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
TESTBED = REPO / "cv2x-testbed"
for p in (TESTBED, TESTBED / "sumo"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from eth_account import Account  # noqa: E402

from identity.w3c_verifiable_credentials import (  # noqa: E402
    CredentialIssuer, CredentialVerifier, HolderWallet, SHARED_HOLDER_KEYS,
)

VIN = "5YJ3E1EA0PF123456"


def demo_did(tag):
    return f"did:ethr:0x1:0x{tag}{uuid.uuid4().hex[:8].upper()}"


def ethr_issuer(name):
    acct = Account.create()
    return CredentialIssuer(f"did:ethr:0x1:{acct.address}", acct.key.hex(),
                            name)


@pytest.fixture(scope="module")
def sumo():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import sumo_identity_integration as module
    return module


class TestSumoSelfIssuedCredential:

    def test_self_issued_v2v_credential_rejected(self, sumo):
        # PoC: attacker key + rogue did:ethr issuer the consortium never
        # trusted, issuing a V2VSafetyCredential to the attacker's DID.
        layer = sumo.SSIIdentityLayer()
        layer.enroll("legit", VIN, "Tesla", "M3", 2024)
        attacker = Account.create()
        did = f"did:ethr:0x1:{attacker.address}"
        rogue = ethr_issuer("Rogue")
        cred = rogue.issue_credential(
            "V2VSafetyCredential", did,
            {"vin": "FAKE", "authorizedMessages": ["BSM", "DENM"]},
            validity_days=365)
        layer.wallets["attacker"] = {"account": attacker, "did": did,
                                     "credential": cred}
        pkg, _ = layer.sign("attacker", {"msgID": "DENM",
                                         "event": "hard-brake", "speed": 0})
        ok, _, cold = layer.verify("victim", pkg)
        assert cold
        assert ok is False

    def test_vehicle_cannot_self_issue_with_own_key(self, sumo):
        layer = sumo.SSIIdentityLayer()
        attacker = Account.create()
        did = f"did:ethr:0x1:{attacker.address}"
        self_issuer = CredentialIssuer(did, attacker.key.hex(), "Me")
        cred = self_issuer.issue_credential(
            "V2VSafetyCredential", did, {"vin": "FAKE"}, validity_days=365)
        layer.wallets["self"] = {"account": attacker, "did": did,
                                 "credential": cred}
        pkg, _ = layer.sign("self", {"msgID": "BSM", "speed": 10})
        assert layer.verify("victim", pkg)[0] is False

    def test_consortium_enrolled_vehicle_still_verifies(self, sumo):
        layer = sumo.SSIIdentityLayer()
        layer.enroll("legit", VIN, "Tesla", "M3", 2024)
        pkg, _ = layer.sign("legit", {"msgID": "BSM", "speed": 10})
        ok, _, cold = layer.verify("rx", pkg)
        assert ok and cold
        ok, _, cold = layer.verify("rx", pkg)
        assert ok and not cold

    def test_revoked_consortium_credential_rejected(self, sumo):
        layer = sumo.SSIIdentityLayer()
        wallet = layer.enroll("legit", VIN, "Tesla", "M3", 2024)
        layer.issuer.revoke_credential(wallet["credential"].id, "decommissioned")
        pkg, _ = layer.sign("legit", {"msgID": "BSM", "speed": 10})
        assert layer.verify("rx", pkg)[0] is False


class TestShimTrust:

    def _vc(self, issuer, subject):
        return issuer.issue_credential("VehicleBirthCertificate", subject,
                                       {"vin": VIN, "make": "Tesla"})

    def test_constructing_an_issuer_does_not_make_it_trusted(self):
        issuer = CredentialIssuer(demo_did("ISS"), "0x" + "3" * 64, "X")
        vc = self._vc(issuer, demo_did("VEH"))
        ok, report = CredentialVerifier().verify_credential(vc)
        assert not ok
        ok, report = CredentialVerifier(trusted_issuers=[issuer]) \
            .verify_credential(vc)
        assert ok, report

    def test_wallet_is_not_a_trusted_issuer(self):
        consortium = ethr_issuer("Consortium")
        holder_did = demo_did("WAL")
        wallet = HolderWallet(holder_did, "0x" + "4" * 64)
        # the wallet's own key "issues" a credential under its own DID
        forged = CredentialIssuer(holder_did, "0x" + "4" * 64)
        vc = self._vc(forged, holder_did)
        wallet.store_credential(vc)
        ok, _ = CredentialVerifier(trusted_issuers=[consortium]) \
            .verify_credential(vc)
        assert not ok

    def test_ethr_issuer_must_be_on_allow_list(self):
        consortium, rogue = ethr_issuer("C"), ethr_issuer("R")
        vc = self._vc(rogue, demo_did("VEH"))
        ok, report = CredentialVerifier(trusted_issuers=[consortium]) \
            .verify_credential(vc)
        assert not ok
        assert any("allow-list" in e for e in report["errors"])

    def test_demo_did_key_binding_cannot_be_hijacked(self):
        did = demo_did("OWN")
        HolderWallet(did, "0x" + "5" * 64)
        HolderWallet(did, "0x" + "5" * 64)          # same key: fine
        with pytest.raises(ValueError, match="already bound"):
            HolderWallet(did, "0x" + "6" * 64)
        assert SHARED_HOLDER_KEYS.address_for(did) == \
            Account.from_key("0x" + "5" * 64).address.lower()

    def test_owner_presents_vehicle_credential_only_with_relation(self):
        issuer = CredentialIssuer(demo_did("ISS"), "0x" + "7" * 64, "X")
        vehicle, owner = demo_did("VEH"), HolderWallet(demo_did("OWN"),
                                                       "0x" + "8" * 64)
        vc = self._vc(issuer, vehicle)
        owner.store_credential(vc)
        vp = owner.create_presentation([vc.id], challenge="c", domain="d")
        ok, _ = CredentialVerifier(trusted_issuers=[issuer]) \
            .verify_presentation(vp, "c", "d")
        assert not ok
        ok, report = CredentialVerifier(
            trusted_issuers=[issuer],
            subject_holder_binding={vehicle: {owner.holder_did}},
        ).verify_presentation(vp, "c", "d")
        assert ok, report
