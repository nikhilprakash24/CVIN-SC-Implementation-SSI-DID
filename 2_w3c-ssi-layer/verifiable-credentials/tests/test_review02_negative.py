#!/usr/bin/env python3
"""
Review 02 negative tests — SSI / VC layer (docs/REVIEW_02_CODEBASE.md §S)
=========================================================================

Every reviewer proof-of-concept for S-1, S-2, S-4, S-5, S-6, S-7, S-9 and
the canonical half of T-3 is reproduced here as a test that FAILS on the
pre-fix code (merge 434669d) and passes after the fix.

Run:  python3 -m pytest 2_w3c-ssi-layer -q
"""

import copy
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vc_issuer import (  # noqa: E402
    CredentialIssuer, RevocationRegistry, SECP256K1_N, sign_document,
)
from vc_holder import HolderWallet  # noqa: E402
from vc_verifier import (  # noqa: E402
    CredentialVerifier, NonceStore, TrustedIssuerRegistry,
)

VIN = "5YJ3E1EA0PF123456"
CHALLENGE, DOMAIN = "nonce-r02", "dmv.gov.bc.ca"


def birth_claims(issuer):
    return {"vin": VIN, "make": "Tesla", "model": "Model 3", "year": 2024,
            "manufacturingDate": "2024-01-15",
            "manufacturerDid": issuer.issuer_did}


@pytest.fixture
def issuer():
    return CredentialIssuer.with_ethr_did()


@pytest.fixture
def victim():
    return HolderWallet.with_ethr_did()


@pytest.fixture
def verifier(issuer):
    return CredentialVerifier(revocation_registry=issuer.revocation_registry)


def issue(issuer, subject_did, **kwargs):
    return issuer.issue_credential("VehicleBirthCertificate", subject_did,
                                   birth_claims(issuer), **kwargs)


def resign(issuer, doc, **proof_overrides):
    """Re-sign a modified credential with the issuer's real key."""
    doc = {k: v for k, v in doc.items() if k != "proof"}
    proof = {
        "type": "DataIntegrityProof",
        "cryptosuite": "eip191-secp256k1-recovery-2024",
        "created": "2026-01-01T00:00:00Z",
        "verificationMethod": f"{issuer.issuer_did}#controller",
        "proofPurpose": "assertionMethod",
    }
    proof.update(proof_overrides)
    proof = {k: v for k, v in proof.items() if v is not None}
    proof["proofValue"] = sign_document(doc, proof, issuer._account.key)
    doc["proof"] = proof
    return doc


# ---------------------------------------------------------------------------
# S-1 — presentation holder must be bound to the credential subject
# ---------------------------------------------------------------------------

class TestS1HolderBinding:

    def test_thief_with_own_did_cannot_present_victim_credential(
            self, issuer, victim, verifier):
        # PoC 1: the thief signs a VP with the thief's OWN DID and key.
        envelope = issue(issuer, victim.holder_did)
        thief = HolderWallet.with_ethr_did()
        cid = thief.store_credential(copy.deepcopy(envelope))
        vp = thief.create_presentation([cid], CHALLENGE, DOMAIN)
        ok, report = verifier.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert not ok
        # the VP signature itself is fine — the binding is what fails
        assert report["presentation"]["valid"]
        errors = report["credentials"][0]["errors"]
        assert any("holder_binding" in e for e in errors), errors

    def test_subject_presenting_own_credential_still_verifies(
            self, issuer, victim, verifier):
        cid = victim.store_credential(issue(issuer, victim.holder_did))
        vp = victim.create_presentation([cid], CHALLENGE, DOMAIN)
        ok, report = verifier.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert ok, report

    def test_subjectless_credential_rejected_unless_bearer_allowed(
            self, issuer, victim):
        doc = copy.deepcopy(issue(issuer, victim.holder_did,
                                  revocable=False)["verifiableCredential"])
        doc["credentialSubject"].pop("id")
        doc = resign(issuer, doc)
        cid = victim.store_credential(doc)
        vp = victim.create_presentation([cid], CHALLENGE, DOMAIN)

        strict = CredentialVerifier()
        ok, report = strict.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert not ok
        assert any("holder_binding" in e
                   for e in report["credentials"][0]["errors"])

        bearer = CredentialVerifier(allow_bearer_credentials=True)
        ok, report = bearer.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert ok, report

    def test_list_subject_bound_when_holder_is_one_of_them(self, issuer,
                                                          victim):
        doc = copy.deepcopy(issue(issuer, victim.holder_did,
                                  revocable=False)["verifiableCredential"])
        other = "did:ethr:0x1:0x" + "e" * 40
        doc["credentialSubject"] = [{"id": other},
                                    dict(doc["credentialSubject"])]
        doc = resign(issuer, doc)
        cid = victim.store_credential(doc)
        vp = victim.create_presentation([cid], CHALLENGE, DOMAIN)
        ok, report = CredentialVerifier().verify_presentation(
            vp, CHALLENGE, DOMAIN)
        assert ok, report

        thief = HolderWallet.with_ethr_did()
        vp = thief.create_presentation(
            [thief.store_credential(doc)], CHALLENGE, DOMAIN)
        ok, _ = CredentialVerifier().verify_presentation(
            vp, CHALLENGE, DOMAIN)
        assert not ok

    def test_configured_subject_holder_relation(self, issuer, verifier):
        # Owner presents the VEHICLE's credential: allowed only through an
        # explicit relation (in a deployment: the vehicle DID's controller).
        vehicle_did = "did:ethr:0x1:0x" + "c" * 40
        owner = HolderWallet.with_ethr_did()
        cid = owner.store_credential(issue(issuer, vehicle_did))
        vp = owner.create_presentation([cid], CHALLENGE, DOMAIN)

        ok, _ = verifier.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert not ok

        related = CredentialVerifier(
            revocation_registry=issuer.revocation_registry,
            subject_holder_binding={vehicle_did: {owner.holder_did}})
        ok, report = related.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert ok, report


# ---------------------------------------------------------------------------
# S-2 — credentialStatus fails closed; registry keyed + issuer-bound
# ---------------------------------------------------------------------------

class TestS2StatusFailClosed:

    def test_no_registry_is_invalid(self, issuer, victim):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        issuer.revoke_credential(vc["id"])
        result = CredentialVerifier().verify_credential(vc)       # PoC 2b
        assert not result.valid
        assert any("no status registry" in e for e in result.errors)

    def test_no_registry_is_invalid_even_if_not_revoked(self, issuer, victim):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        assert not CredentialVerifier().verify_credential(vc).valid

    def test_foreign_registry_is_invalid(self, issuer, victim):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        issuer.revoke_credential(vc["id"])
        other = RevocationRegistry("other")                        # PoC 2c
        result = CredentialVerifier(revocation_registry=other) \
            .verify_credential(vc)
        assert not result.valid

    def test_registry_with_same_id_bound_to_other_issuer_is_invalid(
            self, issuer, victim):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        issuer.revoke_credential(vc["id"])
        imposter = RevocationRegistry(
            registry_id=vc["credentialStatus"]["statusListCredential"],
            issuer_did="did:ethr:0x1:0x" + "f" * 40)
        result = CredentialVerifier(revocation_registry=imposter) \
            .verify_credential(vc)
        assert not result.valid
        assert any("bound to" in e for e in result.errors)

    def test_correct_registry_revoked_is_invalid(self, issuer, victim,
                                                 verifier):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        assert verifier.verify_credential(vc).valid
        issuer.revoke_credential(vc["id"], reason="stolen")
        result = verifier.verify_credential(vc)
        assert not result.valid
        assert any("revoked" in e for e in result.errors)

    def test_correct_registry_not_revoked_is_valid(self, issuer, victim,
                                                   verifier):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        result = verifier.verify_credential(vc)
        assert result.valid, result.errors
        assert result.checks["revocation"] is True

    def test_lookup_is_per_credential_across_issuers(self, victim):
        a, b = CredentialIssuer.with_ethr_did(), CredentialIssuer.with_ethr_did()
        vc_a = issue(a, victim.holder_did)["verifiableCredential"]
        vc_b = issue(b, victim.holder_did)["verifiableCredential"]
        verifier = CredentialVerifier(
            revocation_registry=[a.revocation_registry, b.revocation_registry])
        a.revoke_credential(vc_a["id"])
        assert not verifier.verify_credential(vc_a).valid
        assert verifier.verify_credential(vc_b).valid

    def test_issuers_default_registries_are_distinct_and_bound(self):
        a, b = CredentialIssuer.with_ethr_did(), CredentialIssuer.with_ethr_did()
        assert a.revocation_registry.registry_id != \
            b.revocation_registry.registry_id
        assert a.revocation_registry.issuer_did == a.issuer_did
        with pytest.raises(ValueError, match="bound to"):
            CredentialIssuer(b.issuer_did,
                             revocation_registry=a.revocation_registry)

    def test_status_entry_must_reference_this_credential(self, issuer, victim,
                                                         verifier):
        vc = copy.deepcopy(issue(issuer, victim.holder_did)
                           ["verifiableCredential"])
        vc["credentialStatus"]["id"] += "-other"
        vc = resign(issuer, vc)
        assert not verifier.verify_credential(vc).valid


# ---------------------------------------------------------------------------
# S-4 — date-times parsed as time-zone-aware instants
# ---------------------------------------------------------------------------

class TestS4Temporal:

    def _signed(self, issuer, victim, **props):
        doc = copy.deepcopy(issue(issuer, victim.holder_did, revocable=False,
                                  validity_days=None)["verifiableCredential"])
        doc.update(props)
        return resign(issuer, doc)

    def _temporal_only_failure(self, result):
        assert not result.valid
        assert set(k for k, v in result.checks.items() if not v) == \
            {"temporal"}, result.errors

    def test_offset_valid_until_already_past(self, issuer, victim):
        # PoC 3: 2 h ago in UTC, written with +12:00 → lexically "future"
        past = (datetime.now(timezone.utc) - timedelta(hours=2)) \
            .astimezone(timezone(timedelta(hours=12)))
        doc = self._signed(issuer, victim,
                           validUntil=past.strftime("%Y-%m-%dT%H:%M:%S+12:00"))
        self._temporal_only_failure(CredentialVerifier().verify_credential(doc))

    def test_offset_valid_until_in_future_accepted(self, issuer, victim):
        future = (datetime.now(timezone.utc) + timedelta(hours=2)) \
            .astimezone(timezone(timedelta(hours=-8)))
        doc = self._signed(issuer, victim,
                           validUntil=future.strftime("%Y-%m-%dT%H:%M:%S-08:00"))
        result = CredentialVerifier().verify_credential(doc)
        assert result.valid, result.errors

    def test_offset_valid_from_not_yet_reached(self, issuer, victim):
        # 2 h in the future in UTC, written with -12:00 (lexically "past")
        future = (datetime.now(timezone.utc) + timedelta(hours=2)) \
            .astimezone(timezone(timedelta(hours=-12)))
        doc = self._signed(issuer, victim,
                           validFrom=future.strftime("%Y-%m-%dT%H:%M:%S-12:00"))
        self._temporal_only_failure(CredentialVerifier().verify_credential(doc))

    @pytest.mark.parametrize("bad", ["never", "2026-01-01T00:00:00",
                                     "2026-01-01", 20991231, None])
    def test_unparseable_naive_or_non_string_rejected(self, issuer, victim,
                                                      bad):
        doc = self._signed(issuer, victim, validUntil=bad)        # PoC 3c
        result = CredentialVerifier().verify_credential(doc)
        self._temporal_only_failure(result)
        assert any("invalid 'validUntil'" in e for e in result.errors)

    def test_vc11_expiration_date_honoured(self, issuer, victim):
        doc = self._signed(issuer, victim,
                           expirationDate="2001-01-01T00:00:00Z")  # PoC 3b
        self._temporal_only_failure(CredentialVerifier().verify_credential(doc))

    def test_vc11_issuance_date_in_future_rejected(self, issuer, victim):
        doc = self._signed(issuer, victim,
                           issuanceDate="2999-01-01T00:00:00Z")
        self._temporal_only_failure(CredentialVerifier().verify_credential(doc))


# ---------------------------------------------------------------------------
# S-5 — proof metadata whitelist
# ---------------------------------------------------------------------------

class TestS5ProofMetadata:

    def _vc(self, issuer, victim):
        return issue(issuer, victim.holder_did,
                     revocable=False)["verifiableCredential"]

    @pytest.mark.parametrize("override", [
        {"type": "Bogus"},
        {"cryptosuite": "none"},
        {"cryptosuite": None},
        {"proofPurpose": "authentication"},
        {"verificationMethod": "did:example:evil#k"},
        {"verificationMethod": None},
        {"created": "yesterday"},
    ])
    def test_bad_proof_metadata_rejected(self, issuer, victim, override):
        doc = resign(issuer, self._vc(issuer, victim), **override)
        result = CredentialVerifier().verify_credential(doc)
        assert not result.valid
        assert result.checks.get("proof") is False, result.errors

    def test_poc5_combined(self, issuer, victim):
        d = {k: v for k, v in self._vc(issuer, victim).items() if k != "proof"}
        p = {"type": "Bogus", "cryptosuite": "none",
             "proofPurpose": "authentication",
             "verificationMethod": "did:example:evil#k"}
        p["proofValue"] = sign_document(d, p, issuer._account.key)
        d["proof"] = p
        assert not CredentialVerifier().verify_credential(d).valid

    def test_genuine_proof_passes_metadata_check(self, issuer, victim):
        result = CredentialVerifier().verify_credential(self._vc(issuer, victim))
        assert result.valid and result.checks["proof"], result.errors

    def _vp_with_proof(self, wallet, **override):
        vp = {"@context": ["https://www.w3.org/ns/credentials/v2"],
              "type": ["VerifiablePresentation"],
              "holder": wallet.holder_did, "verifiableCredential": []}
        proof = {"type": "DataIntegrityProof",
                 "cryptosuite": "eip191-secp256k1-recovery-2024",
                 "created": "2026-01-01T00:00:00Z",
                 "verificationMethod": f"{wallet.holder_did}#controller",
                 "proofPurpose": "authentication",
                 "challenge": CHALLENGE, "domain": DOMAIN}
        proof.update(override)
        proof["proofValue"] = sign_document(vp, proof, wallet._account.key)
        vp["proof"] = proof
        return vp

    def test_vp_genuine_metadata_passes(self, victim):
        ok, report = CredentialVerifier().verify_presentation(
            self._vp_with_proof(victim), CHALLENGE, DOMAIN)
        assert ok, report

    @pytest.mark.parametrize("override", [
        {"type": "Bogus"},
        {"cryptosuite": "none"},
        {"verificationMethod": "did:ethr:0x1:0x" + "a" * 40 + "#controller"},
    ])
    def test_vp_bad_metadata_rejected(self, victim, override):
        ok, report = CredentialVerifier().verify_presentation(
            self._vp_with_proof(victim, **override), CHALLENGE, DOMAIN)
        assert not ok
        assert report["presentation"]["checks"].get("vp_proof") is False


# ---------------------------------------------------------------------------
# S-6 — challenge required; optional one-shot nonce store
# ---------------------------------------------------------------------------

class TestS6Challenge:

    def _vp_without_challenge(self, issuer, wallet):
        # PoC 6: a VP whose proof carries no challenge/domain at all
        vp = wallet.create_presentation(
            [wallet.store_credential(issue(issuer, wallet.holder_did))],
            challenge="x", domain="y")
        vp.pop("proof")
        p = {"type": "DataIntegrityProof",
             "cryptosuite": "eip191-secp256k1-recovery-2024",
             "proofPurpose": "authentication",
             "verificationMethod": wallet.holder_did + "#controller"}
        p["proofValue"] = sign_document(vp, p, wallet._account.key)
        vp["proof"] = p
        return vp

    @pytest.mark.parametrize("expected", [None, ""])
    def test_missing_expected_challenge_refused(self, issuer, victim,
                                                verifier, expected):
        vp = self._vp_without_challenge(issuer, victim)
        with pytest.raises(ValueError, match="challenge"):
            verifier.verify_presentation(vp, expected, None)

    def test_challengeless_vp_fails_against_real_challenge(self, issuer,
                                                           victim, verifier):
        vp = self._vp_without_challenge(issuer, victim)
        ok, _ = verifier.verify_presentation(vp, "fresh-nonce", None)
        assert not ok

    def test_nonce_store_is_one_shot(self, issuer, victim):
        nonces = NonceStore()
        verifier = CredentialVerifier(
            revocation_registry=issuer.revocation_registry,
            nonce_store=nonces)
        cid = victim.store_credential(issue(issuer, victim.holder_did))
        nonce = nonces.issue()
        vp = victim.create_presentation([cid], nonce, DOMAIN)
        ok, report = verifier.verify_presentation(vp, nonce, DOMAIN)
        assert ok, report
        ok, report = verifier.verify_presentation(vp, nonce, DOMAIN)
        assert not ok                                   # replay
        assert any("already used" in e
                   for e in report["presentation"]["errors"])

    def test_nonce_store_rejects_unissued_nonce(self, issuer, victim):
        verifier = CredentialVerifier(
            revocation_registry=issuer.revocation_registry,
            nonce_store=NonceStore())
        cid = victim.store_credential(issue(issuer, victim.holder_did))
        vp = victim.create_presentation([cid], "self-chosen", DOMAIN)
        ok, _ = verifier.verify_presentation(vp, "self-chosen", DOMAIN)
        assert not ok

    def test_max_proof_age(self, issuer, victim):
        cid = victim.store_credential(issue(issuer, victim.holder_did))
        vp = victim.create_presentation([cid], CHALLENGE, DOMAIN)
        fresh = CredentialVerifier(
            revocation_registry=issuer.revocation_registry,
            max_proof_age_s=60)
        assert fresh.verify_presentation(vp, CHALLENGE, DOMAIN)[0]
        stale = copy.deepcopy(vp)
        stale["proof"]["created"] = "2020-01-01T00:00:00Z"
        stale["proof"]["proofValue"] = sign_document(
            stale, stale["proof"], victim._account.key)
        ok, report = fresh.verify_presentation(stale, CHALLENGE, DOMAIN)
        assert not ok
        assert report["presentation"]["checks"]["vp_freshness"] is False


# ---------------------------------------------------------------------------
# S-7 — one canonical signature encoding
# ---------------------------------------------------------------------------

def _malleate(proof_value, flip_s=True, v_override=None):
    sig = bytes.fromhex(proof_value.removeprefix("0x"))
    r, s, v = sig[:32], int.from_bytes(sig[32:64], "big"), sig[64]
    if flip_s:
        s = SECP256K1_N - s
        v = 27 if v == 28 else 28
    if v_override is not None:
        v = v_override
    return (r + s.to_bytes(32, "big") + bytes([v])).hex()


class TestS7Malleability:

    def test_high_s_twin_rejected(self, issuer, victim, verifier):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        assert verifier.verify_credential(vc).valid
        twin = copy.deepcopy(vc)                                  # PoC 4
        twin["proof"]["proofValue"] = _malleate(vc["proof"]["proofValue"])
        assert twin["proof"]["proofValue"] != vc["proof"]["proofValue"]
        result = verifier.verify_credential(twin)
        assert not result.valid
        assert result.checks["signature"] is False
        assert any("high-s" in e for e in result.errors)

    @pytest.mark.parametrize("v", [0, 1, 29])
    def test_non_canonical_v_rejected(self, issuer, victim, verifier, v):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        sig = vc["proof"]["proofValue"]
        orig_v = bytes.fromhex(sig.removeprefix("0x"))[64]
        alt = copy.deepcopy(vc)
        alt["proof"]["proofValue"] = _malleate(
            sig, flip_s=False, v_override=(orig_v - 27 if v in (0, 1) else v))
        result = verifier.verify_credential(alt)
        assert not result.valid
        assert result.checks["signature"] is False

    def test_high_s_vp_rejected(self, issuer, victim, verifier):
        cid = victim.store_credential(issue(issuer, victim.holder_did))
        vp = victim.create_presentation([cid], CHALLENGE, DOMAIN)
        vp["proof"]["proofValue"] = _malleate(vp["proof"]["proofValue"])
        ok, report = verifier.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert not ok
        assert report["presentation"]["checks"]["vp_signature"] is False


# ---------------------------------------------------------------------------
# S-9 — malformed disclosedClaims give an invalid result, not an exception
# ---------------------------------------------------------------------------

class TestS9MalformedDisclosures:

    def _sd(self, issuer, wallet):
        env = issuer.issue_credential(
            "MaintenanceRecord", wallet.holder_did,
            claims={"vin": VIN, "serviceCenterDid": issuer.issuer_did,
                    "serviceDate": "2026-06-01", "serviceType": "brakes",
                    "odometerKm": 42150},
            selective_disclosure=True)
        return wallet.store_credential(env)

    @pytest.mark.parametrize("malformed", [
        {"odometerKm": {"value": 1}},                 # salt missing
        {"odometerKm": {"salt": "00"}},               # value missing
        {"odometerKm": "42150"},                      # entry not an object
        {"odometerKm": {"value": 1, "salt": 7}},      # salt not a string
        ["odometerKm"],                               # not an object at all
        "everything",
    ])
    def test_malformed_disclosure_is_invalid_not_crash(
            self, issuer, victim, verifier, malformed):
        cid = self._sd(issuer, victim)
        vc = copy.deepcopy(victim.get_credential(cid))
        vc["disclosedClaims"] = malformed
        result = verifier.verify_credential(vc)          # must not raise
        assert not result.valid
        assert result.checks.get("disclosure") is False

        victim.store_credential(vc)
        vp = victim.create_presentation([cid], CHALLENGE, DOMAIN)
        ok, report = verifier.verify_presentation(vp, CHALLENGE, DOMAIN)
        assert not ok

    @pytest.mark.parametrize("garbage", [None, "vc", 42, ["x"]])
    def test_non_object_inputs_are_invalid(self, verifier, garbage):
        assert not verifier.verify_credential(garbage).valid
        ok, _ = verifier.verify_presentation(garbage, CHALLENGE, DOMAIN)
        assert not ok


# ---------------------------------------------------------------------------
# T-3 (canonical half) — explicit trusted-issuer allow-list
# ---------------------------------------------------------------------------

class TestT3AllowList:

    def test_ethr_issuer_must_be_on_configured_allow_list(self, issuer,
                                                          victim):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        consortium = CredentialIssuer.with_ethr_did()
        allow = TrustedIssuerRegistry()
        allow.register(consortium.issuer_did, consortium.address)
        verifier = CredentialVerifier(
            revocation_registry=issuer.revocation_registry,
            trusted_issuers=allow)
        result = verifier.verify_credential(vc)
        assert not result.valid
        assert any("allow-list" in e for e in result.errors)

        allow.register(issuer.issuer_did, issuer.address)
        assert verifier.verify_credential(vc).valid

    def test_allow_list_address_must_match_did(self, issuer, victim):
        vc = issue(issuer, victim.holder_did)["verifiableCredential"]
        allow = TrustedIssuerRegistry()
        allow.register(issuer.issuer_did, "0x" + "1" * 40)
        verifier = CredentialVerifier(
            revocation_registry=issuer.revocation_registry,
            trusted_issuers=allow)
        assert not verifier.verify_credential(vc).valid
