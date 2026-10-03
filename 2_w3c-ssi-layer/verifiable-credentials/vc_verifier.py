#!/usr/bin/env python3
"""
W3C Verifiable Credential Verifier — VC Data Model v2.0
=======================================================

Verifies credentials and presentations WITHOUT any blockchain round-trip:
the signer's Ethereum address is recovered from the secp256k1 signature and
compared against the address embedded in the issuer/holder DID (did:ethr,
did:key) or against a trusted-issuer registry (did:mobi and others).

Check pipeline for a credential:
  1. structure   — required VC DM 2.0 properties present
  2. schema      — claims validate against the registered schema
  3. temporal    — validFrom/issuanceDate reached, validUntil/expirationDate
                   not passed; all parsed as time-zone-aware instants
  4. revocation  — credentialStatus checked against the status registry it
                   names, which must be bound to the issuer (fail closed)
  5. proof       — proof type, cryptosuite, proofPurpose=assertionMethod and
                   a verificationMethod belonging to the issuer
  6. signature   — canonical (low-s, v∈{27,28}) signature; recovered signer
                   matches the issuer DID / registry; issuer allow-listed
                   when an allow-list is configured
  7. disclosure  — disclosed claim+salt pairs match signed claimDigests

Presentation verification additionally checks:
  a. VP proof metadata (type, cryptosuite, proofPurpose=authentication,
     verificationMethod belonging to the holder)
  b. VP signature recovered against the holder DID
  c. challenge matches the verifier's expected nonce (REQUIRED; replay
     protection), optionally consumed from a one-shot NonceStore
  d. domain matches the verifier's audience
  e. every embedded credential passes the credential pipeline AND is bound
     to the holder (credentialSubject.id == holder, or a configured
     subject→holder relation)

Review 02 changes (S-1, S-2, S-4, S-5, S-6, S-7, S-9, T-3) are marked
inline; docs/review02/PASS1_S.md lists the behaviour changes.

Author: Nikhil Prakash
Thesis: MASc, UBC ECE
"""

import secrets
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import (Any, Callable, Dict, Iterable, List, Optional, Tuple,
                    Union)

from vc_schemas import validate_claims, get_schema
from vc_issuer import (
    CRYPTOSUITE, PROOF_TYPE, STATUS_TYPE, RevocationRegistry, claim_digest,
    parse_datetime, recover_signer, utc_now_iso,
)


@dataclass
class VerificationResult:
    """Outcome of a verification with per-check detail."""
    valid: bool = True
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    verified_at: str = field(default_factory=utc_now_iso)
    elapsed_ms: float = 0.0

    def fail(self, check: str, message: str) -> None:
        self.valid = False
        self.checks[check] = False
        self.errors.append(f"[{check}] {message}")

    def ok(self, check: str) -> None:
        self.checks.setdefault(check, True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "checks": self.checks,
            "errors": self.errors,
            "warnings": self.warnings,
            "verifiedAt": self.verified_at,
            "elapsedMs": round(self.elapsed_ms, 3),
        }


class DIDKeyRegistry:
    """
    DID -> signing-address bindings for DIDs that do not embed an Ethereum
    address (e.g. did:mobi, or the legacy demo DIDs of the cv2x shim).

    This is KEY BINDING only (a stand-in for DID resolution); it says
    nothing about whether the DID is trusted to issue credentials. Use it
    for presentation holders. Issuer trust lives in TrustedIssuerRegistry.
    """

    def __init__(self):
        self._keys: Dict[str, str] = {}

    def register(self, did: str, address: str) -> None:
        self._keys[did] = address.lower()

    def address_for(self, did: str) -> Optional[str]:
        return self._keys.get(did)

    def __contains__(self, did: object) -> bool:
        return did in self._keys

    def __len__(self) -> int:
        return len(self._keys)


class TrustedIssuerRegistry(DIDKeyRegistry):
    """
    Trusted-issuer allow-list: issuer DID -> authorised signing address.

    In production this is populated from the on-chain issuer registry; for
    experiments it is seeded directly by the VERIFIER's configuration (never
    by issuers or wallets themselves — review 02, T-3).

    When a CredentialVerifier is constructed WITH a TrustedIssuerRegistry,
    the registry is an allow-list: every issuer, including address-bearing
    did:ethr / did:key issuers, must be registered. For an address-bearing
    DID the registered address must equal the embedded one.
    """

    def is_trusted(self, did: str) -> bool:
        return did in self


class NonceStore:
    """
    One-shot challenge store (review 02, S-6). The verifier ``issue()``s a
    nonce, sends it to the holder, and ``verify_presentation`` ``consume()``s
    it: a nonce verifies at most once and only within ``ttl_s``.
    """

    def __init__(self, ttl_s: float = 300.0):
        self.ttl_s = ttl_s
        self._issued: Dict[str, float] = {}

    def issue(self) -> str:
        nonce = secrets.token_urlsafe(16)
        self._issued[nonce] = time.monotonic() + self.ttl_s
        return nonce

    def consume(self, nonce: str) -> bool:
        expiry = self._issued.pop(nonce, None)
        return expiry is not None and time.monotonic() <= expiry


def address_from_did(did: str) -> Optional[str]:
    """
    Extract the Ethereum address from DID methods that embed one.

    Supported (this repository's conventions):
      did:ethr:<chainId>:<address>   (ERC-1056)
      did:ethr:<address>
      did:key:<chainId>:<address>    (ERC-725, repo convention)
      did:nft:<chainId>:<contract>:<tokenId> → controller = contract? No —
          NFT identity is token-controlled; signature checks require the
          current token owner, resolved on-chain. Returns None here (the
          trusted registry or a chain lookup must supply the owner).
    """
    if not isinstance(did, str):
        return None
    parts = did.split(":")
    if len(parts) < 3:
        return None
    method = parts[1]
    candidate = parts[-1]
    if method in ("ethr", "key") and candidate.startswith("0x") \
            and len(candidate) == 42:
        try:
            int(candidate[2:], 16)
        except ValueError:
            return None
        return candidate.lower()
    return None


def did_of(verification_method: Any) -> Optional[str]:
    """The DID part of a verificationMethod DID URL (strip #fragment)."""
    if not isinstance(verification_method, str) or \
            not verification_method.startswith("did:"):
        return None
    return verification_method.split("#", 1)[0]


SubjectHolderBinding = Union[
    Callable[[str, str], bool], Mapping]


class CredentialVerifier:
    """
    Verifier for W3C VCs and VPs issued by this thesis stack.

    Args:
        revocation_registry: one RevocationRegistry or an iterable of them.
            Credentials carrying ``credentialStatus`` are checked against
            the registry whose ``registry_id`` equals the credential's
            ``statusListCredential``, and that registry must be bound to
            the credential's issuer. If no such registry is configured the
            credential is INVALID (fail closed — review 02, S-2).
        trusted_issuers: when given, an issuer ALLOW-LIST (T-3): issuers
            not in it are rejected, including did:ethr issuers. When
            omitted, address-bearing issuer DIDs are accepted on signature
            alone (open world) and other DIDs are rejected.
        holder_keys: DID -> address bindings for presentation holders whose
            DIDs do not embed an address (key binding, not trust).
        subject_holder_binding: optional relation allowing a holder to
            present a credential whose subject is another DID it controls
            (e.g. an owner presenting the vehicle's credential): either a
            mapping ``{subject_did: iterable of holder DIDs}`` or a callable
            ``(subject_did, holder_did) -> bool``. Without it the holder
            must BE the subject (S-1).
        allow_bearer_credentials: accept embedded credentials whose
            subject has no ``id`` (bearer credentials). Off by default:
            such credentials are rejected inside presentations (S-1).
        nonce_store: optional NonceStore; when set, the expected challenge
            must be consumable from it (single use).
        max_proof_age_s: optional bound on the age of a VP proof's
            ``created`` (and on its being in the future).
        strict_schema: False downgrades schema violations to warnings.
    """

    REQUIRED_VC_PROPERTIES = ("@context", "type", "issuer",
                              "credentialSubject", "proof")
    CLOCK_SKEW = timedelta(minutes=5)

    def __init__(self,
                 revocation_registry: Union[
                     RevocationRegistry, Iterable[RevocationRegistry],
                     None] = None,
                 trusted_issuers: Optional[TrustedIssuerRegistry] = None,
                 strict_schema: bool = True,
                 holder_keys: Optional[DIDKeyRegistry] = None,
                 subject_holder_binding: Optional[SubjectHolderBinding]
                 = None,
                 allow_bearer_credentials: bool = False,
                 nonce_store: Optional[NonceStore] = None,
                 max_proof_age_s: Optional[float] = None):
        self._status_registries: Dict[str, RevocationRegistry] = {}
        if isinstance(revocation_registry, RevocationRegistry):
            revocation_registry = [revocation_registry]
        for registry in revocation_registry or []:
            self.add_status_registry(registry)
        # T-3: an explicitly configured registry is an allow-list.
        self.enforce_issuer_allow_list = trusted_issuers is not None
        self.trusted_issuers = trusted_issuers if trusted_issuers is not None \
            else TrustedIssuerRegistry()
        self.holder_keys = holder_keys or DIDKeyRegistry()
        if isinstance(subject_holder_binding, Mapping):
            relation = {k: set(v) for k, v in subject_holder_binding.items()}
            self._subject_holder_binding: Optional[Callable[[str, str], bool]] \
                = lambda subject, holder: holder in relation.get(subject, ())
        else:
            self._subject_holder_binding = subject_holder_binding
        self.allow_bearer_credentials = allow_bearer_credentials
        self.nonce_store = nonce_store
        self.max_proof_age_s = max_proof_age_s
        # strict_schema=False downgrades schema violations to warnings —
        # used by legacy demo callers whose claims predate the registered
        # schemas. Signature/temporal/revocation checks are never relaxed.
        self.strict_schema = strict_schema

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def add_status_registry(self, registry: RevocationRegistry) -> None:
        """Make a status registry available, keyed by its registry_id."""
        if not isinstance(registry, RevocationRegistry):
            raise TypeError(f"not a RevocationRegistry: {registry!r}")
        self._status_registries[registry.registry_id] = registry

    @property
    def revocation_registry(self) -> Optional[RevocationRegistry]:
        """Backward-compatible accessor: the single configured registry."""
        if len(self._status_registries) == 1:
            return next(iter(self._status_registries.values()))
        return None

    # ------------------------------------------------------------------
    # Credential verification
    # ------------------------------------------------------------------

    def verify_credential(self, vc: Dict[str, Any]) -> VerificationResult:
        t0 = time.perf_counter()
        result = VerificationResult()

        try:
            self._check_structure(vc, result)
            if result.valid:
                self._check_schema(vc, result)
                self._check_temporal(vc, result)
                self._check_revocation(vc, result)
                self._check_signature(vc, result)
                self._check_disclosures(vc, result)
        except Exception as exc:  # S-9: malformed input → invalid, not crash
            result.fail("internal",
                        f"verification aborted on malformed input: "
                        f"{type(exc).__name__}: {exc}")

        result.elapsed_ms = (time.perf_counter() - t0) * 1000
        return result

    @staticmethod
    def _issuer_did(vc: Dict[str, Any]) -> Optional[str]:
        issuer = vc.get("issuer")
        did = issuer.get("id") if isinstance(issuer, dict) else issuer
        return did if isinstance(did, str) else None

    @staticmethod
    def _subjects(vc: Dict[str, Any]) -> List[Any]:
        subject = vc.get("credentialSubject")
        return subject if isinstance(subject, list) else [subject]

    def _check_structure(self, vc: Dict[str, Any],
                         result: VerificationResult) -> None:
        if not isinstance(vc, dict):
            result.fail("structure", "credential is not a JSON object")
            return
        for prop in self.REQUIRED_VC_PROPERTIES:
            if prop not in vc:
                result.fail("structure", f"missing required property '{prop}'")
        if "structure" not in result.checks:
            types = vc.get("type", [])
            if not isinstance(types, list) or \
                    "VerifiableCredential" not in types:
                result.fail("structure",
                            "'type' must include 'VerifiableCredential'")
            issuer_did = self._issuer_did(vc)
            if issuer_did is None or not issuer_did.startswith("did:"):
                result.fail("structure", "'issuer' must be a DID (string or "
                                         "object with string 'id')")
            subjects = self._subjects(vc)
            if not subjects or not all(isinstance(s, dict) for s in subjects):
                result.fail("structure", "'credentialSubject' must be an "
                                         "object or a non-empty list of "
                                         "objects")
            elif not any(isinstance(s.get("id"), str) for s in subjects):
                result.warnings.append("credentialSubject has no 'id'")
        result.ok("structure")

    def _check_schema(self, vc: Dict[str, Any],
                      result: VerificationResult) -> None:
        specific_types = [t for t in vc.get("type", [])
                          if t != "VerifiableCredential"]
        if not specific_types:
            result.warnings.append("no specific credential type to validate")
            result.ok("schema")
            return
        cred_type = specific_types[0]
        if get_schema(cred_type) is None:
            result.warnings.append(f"no registered schema for '{cred_type}'")
            result.ok("schema")
            return

        subjects = self._subjects(vc)
        for raw_subject in subjects:
            if len(subjects) > 1 and set(raw_subject) <= {"id"}:
                continue  # bare subject reference in a multi-subject VC
            self._check_subject_schema(vc, cred_type, raw_subject, result)
        result.ok("schema")

    def _check_subject_schema(self, vc: Dict[str, Any], cred_type: str,
                              raw_subject: Dict[str, Any],
                              result: VerificationResult) -> None:
        subject = dict(raw_subject)
        subject.pop("id", None)
        if "claimDigests" in subject:
            # Selective-disclosure credential: raw claims are not present in
            # the signed document; schema validation applies to disclosed
            # claims only (partial, by design). Malformed disclosure entries
            # are rejected by _check_disclosures (S-9); skip them here.
            disclosed = vc.get("disclosedClaims", {})
            if not isinstance(disclosed, dict):
                return
            partial = {k: v["value"] for k, v in disclosed.items()
                       if isinstance(v, dict) and "value" in v}
            schema = get_schema(cred_type)
            specs = {p.name: p for p in schema.properties}
            for name, value in partial.items():
                spec = specs.get(name)
                if spec and not isinstance(value, spec.types):
                    result.fail("schema",
                                f"disclosed claim '{name}' has wrong type")
                elif spec and spec.validator and not spec.validator(value):
                    result.fail("schema",
                                f"disclosed claim '{name}' failed validation")
            return

        ok, errors = validate_claims(cred_type, subject)
        if not ok:
            if self.strict_schema:
                for e in errors:
                    result.fail("schema", e)
            else:
                for e in errors:
                    result.warnings.append(f"[schema] {e}")

    # S-4: (property, bound) — "from" bounds must be reached, "until"
    # bounds must not be passed. VC 1.1 names are honoured too.
    TEMPORAL_PROPERTIES = (
        ("validFrom", "from"),
        ("issuanceDate", "from"),
        ("validUntil", "until"),
        ("expirationDate", "until"),
    )

    def _check_temporal(self, vc: Dict[str, Any],
                        result: VerificationResult) -> None:
        now = datetime.now(timezone.utc)
        for prop, bound in self.TEMPORAL_PROPERTIES:
            if prop not in vc:
                continue
            raw = vc[prop]
            try:
                instant = parse_datetime(raw)
            except ValueError as exc:
                result.fail("temporal", f"invalid '{prop}': {exc}")
                continue
            if bound == "from" and now < instant:
                result.fail("temporal", f"not yet valid ({prop}={raw})")
            elif bound == "until" and now > instant:
                result.fail("temporal", f"expired ({prop}={raw})")
        result.ok("temporal")

    def _check_revocation(self, vc: Dict[str, Any],
                          result: VerificationResult) -> None:
        if "credentialStatus" not in vc:
            result.ok("revocation")
            return
        statuses = vc["credentialStatus"]
        statuses = statuses if isinstance(statuses, list) else [statuses]
        if not statuses:
            result.fail("revocation", "empty credentialStatus")
            return
        issuer_did = self._issuer_did(vc)
        credential_id = vc.get("id")
        for status in statuses:
            self._check_one_status(status, issuer_did, credential_id, result)
        result.ok("revocation")

    def _check_one_status(self, status: Any, issuer_did: Optional[str],
                          credential_id: Any,
                          result: VerificationResult) -> None:
        # S-2: a declared status that cannot be checked is a failure, not a
        # warning. The registry is found BY the credential's own
        # statusListCredential and must be bound to the credential's issuer.
        if not isinstance(status, dict):
            result.fail("revocation", "credentialStatus entry is not an "
                                      "object")
            return
        if status.get("type") != STATUS_TYPE:
            result.fail("revocation",
                        f"unsupported credentialStatus type "
                        f"{status.get('type')!r} (status cannot be checked)")
            return
        list_ref = status.get("statusListCredential")
        registry = self._status_registries.get(list_ref) \
            if isinstance(list_ref, str) else None
        if registry is None:
            result.fail("revocation",
                        f"no status registry configured for "
                        f"statusListCredential {list_ref!r} — revocation "
                        f"status cannot be checked (fail closed)")
            return
        if registry.issuer_did is None or registry.issuer_did != issuer_did:
            result.fail("revocation",
                        f"status registry {list_ref} is bound to "
                        f"{registry.issuer_did!r}, not to the credential "
                        f"issuer {issuer_did!r}")
            return
        if not isinstance(credential_id, str) or \
                status.get("id") != f"{list_ref}#{credential_id}":
            result.fail("revocation",
                        "credentialStatus.id does not reference this "
                        "credential in its status list")
            return
        if registry.is_revoked(credential_id):
            info = registry.revocation_info(credential_id) or {}
            result.fail("revocation",
                        f"credential revoked at {info.get('revokedAt')} "
                        f"(reason: {info.get('reason')})")

    def _check_proof_metadata(self, proof: Dict[str, Any],
                              expected_purpose: str,
                              controller_did: Optional[str],
                              check: str,
                              result: VerificationResult) -> None:
        """S-5: proof type, cryptosuite, purpose and verification method."""
        if proof.get("type") != PROOF_TYPE:
            result.fail(check, f"proof type {proof.get('type')!r} is not "
                               f"{PROOF_TYPE!r}")
        if proof.get("cryptosuite") != CRYPTOSUITE:
            result.fail(check, f"cryptosuite {proof.get('cryptosuite')!r} "
                               f"is not {CRYPTOSUITE!r}")
        if proof.get("proofPurpose") != expected_purpose:
            result.fail(check, f"proofPurpose {proof.get('proofPurpose')!r} "
                               f"must be {expected_purpose!r}")
        vm_did = did_of(proof.get("verificationMethod"))
        if vm_did is None or vm_did != controller_did:
            result.fail(check,
                        f"verificationMethod "
                        f"{proof.get('verificationMethod')!r} does not "
                        f"belong to {controller_did!r}")
        if "created" in proof:
            try:
                parse_datetime(proof["created"])
            except ValueError as exc:
                result.fail(check, f"invalid proof 'created': {exc}")

    def _check_signature(self, vc: Dict[str, Any],
                         result: VerificationResult) -> None:
        proof = vc.get("proof")
        if not isinstance(proof, dict) or "proofValue" not in proof:
            result.fail("signature", "missing or malformed proof")
            return
        issuer_did = self._issuer_did(vc)
        self._check_proof_metadata(proof, "assertionMethod", issuer_did,
                                   "proof", result)
        result.ok("proof")
        try:
            # disclosedClaims is holder-attached, never part of the
            # issuer-signed document — strip before recovery.
            signed_doc = {k: v for k, v in vc.items()
                          if k != "disclosedClaims"}
            recovered = recover_signer(signed_doc, proof).lower()
        except Exception as exc:
            result.fail("signature", f"signature recovery failed: {exc}")
            return

        embedded = address_from_did(issuer_did)
        registered = self.trusted_issuers.address_for(issuer_did)
        if self.enforce_issuer_allow_list:
            # T-3: with an allow-list configured, every issuer must be on it
            # — address-bearing did:ethr issuers included.
            if not self.trusted_issuers.is_trusted(issuer_did):
                result.fail("signature",
                            f"issuer '{issuer_did}' is not in the "
                            f"trusted-issuer allow-list")
                return
            if embedded is not None and registered is not None \
                    and registered != embedded:
                result.fail("signature",
                            f"allow-list address {registered} for "
                            f"'{issuer_did}' contradicts the address in "
                            f"the DID")
                return
        expected = embedded or registered
        if expected is None:
            result.fail("signature",
                        f"cannot determine signing address for issuer "
                        f"'{issuer_did}' (not address-bearing, not in "
                        f"trusted registry)")
            return
        if recovered != expected:
            result.fail("signature",
                        f"recovered signer {recovered} does not match "
                        f"issuer {issuer_did}")
        result.ok("signature")

    def _check_disclosures(self, vc: Dict[str, Any],
                           result: VerificationResult) -> None:
        if "disclosedClaims" not in vc:
            result.ok("disclosure")
            return
        disclosed = vc["disclosedClaims"]
        # S-9: holder-supplied structure is validated, never indexed blindly.
        if not isinstance(disclosed, dict):
            result.fail("disclosure", "disclosedClaims must be an object")
            return
        subject = vc.get("credentialSubject")
        digests = subject.get("claimDigests") \
            if isinstance(subject, dict) else None
        if not digests or not isinstance(digests, dict):
            result.fail("disclosure",
                        "disclosedClaims present but credential carries no "
                        "claimDigests")
            return
        for name, entry in disclosed.items():
            if not isinstance(entry, dict) or "value" not in entry \
                    or not isinstance(entry.get("salt"), str):
                result.fail("disclosure",
                            f"malformed disclosure for claim '{name}' "
                            f"(need {{'value', 'salt': str}})")
                continue
            if name not in digests:
                result.fail("disclosure", f"no signed digest for claim '{name}'")
                continue
            recomputed = claim_digest(name, entry["value"], entry["salt"])
            if recomputed != digests[name]:
                result.fail("disclosure",
                            f"digest mismatch for claim '{name}' — value or "
                            f"salt was tampered with")
        result.ok("disclosure")

    # ------------------------------------------------------------------
    # Presentation verification
    # ------------------------------------------------------------------

    def _holder_address(self, holder_did: Any) -> Optional[str]:
        if not isinstance(holder_did, str):
            return None
        return address_from_did(holder_did) \
            or self.holder_keys.address_for(holder_did) \
            or self.trusted_issuers.address_for(holder_did)

    def _check_holder_binding(self, vc: Any, holder_did: Any,
                              result: VerificationResult) -> None:
        """
        S-1: the presenter must be the credential's subject (or hold a
        configured relation to it). Without this a thief could present a
        stolen credential under the thief's own DID and key.
        """
        if not isinstance(vc, dict):
            return  # already rejected by the structure check
        subject_ids = [s.get("id") for s in self._subjects(vc)
                       if isinstance(s, dict) and isinstance(s.get("id"), str)]
        if not subject_ids:
            if self.allow_bearer_credentials:
                result.warnings.append(
                    "bearer credential (no credentialSubject.id) accepted "
                    "because allow_bearer_credentials=True")
                result.ok("holder_binding")
            else:
                result.fail("holder_binding",
                            "credentialSubject has no 'id', so the "
                            "credential cannot be bound to the presenter "
                            "(bearer credentials are disabled)")
            return
        if holder_did in subject_ids:
            result.ok("holder_binding")
            return
        relation = self._subject_holder_binding
        if relation is not None and isinstance(holder_did, str) and \
                any(relation(sid, holder_did) for sid in subject_ids):
            result.warnings.append(
                f"holder {holder_did} presents a credential about "
                f"{subject_ids} under a configured subject→holder relation")
            result.ok("holder_binding")
            return
        result.fail("holder_binding",
                    f"presentation holder {holder_did} is not the credential "
                    f"subject {subject_ids}")

    def verify_presentation(self, vp: Dict[str, Any],
                            expected_challenge: str,
                            expected_domain: Optional[str]
                            ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify a Verifiable Presentation and every credential inside it.

        ``expected_challenge`` is REQUIRED (non-empty string): a verifier
        that does not issue a challenge has no replay protection, so calling
        without one is a programming error and raises ``ValueError``
        (review 02, S-6). ``expected_domain`` may be None only for a VP
        that carries no domain.

        Returns (is_valid, report) where report contains the VP-level
        result plus one entry per embedded credential.
        """
        if not isinstance(expected_challenge, str) or not expected_challenge:
            raise ValueError("verify_presentation requires a non-empty "
                             "expected_challenge (replay protection)")
        t0 = time.perf_counter()
        vp_result = VerificationResult()
        credential_reports: List[Dict[str, Any]] = []
        all_creds_valid = True

        try:
            if not isinstance(vp, dict):
                raise TypeError("presentation is not a JSON object")
            holder_did = vp.get("holder")
            proof = vp.get("proof")
            if not isinstance(proof, dict) or "proofValue" not in proof:
                vp_result.fail("vp_signature", "missing or malformed proof")
            else:
                self._check_vp_proof(vp, proof, holder_did,
                                     expected_challenge, expected_domain,
                                     vp_result)

            vp_result.ok("vp_challenge")
            vp_result.ok("vp_domain")
            vp_result.ok("vp_purpose")

            creds = vp.get("verifiableCredential", [])
            if isinstance(creds, dict):
                creds = [creds]
            if not isinstance(creds, list):
                vp_result.fail("structure",
                               "verifiableCredential must be a list")
                creds = []
            for vc in creds:
                cred_result = self.verify_credential(vc)
                self._check_holder_binding(vc, holder_did, cred_result)
                credential_reports.append({
                    "credentialId": vc.get("id")
                    if isinstance(vc, dict) else None,
                    **cred_result.to_dict(),
                })
                all_creds_valid = all_creds_valid and cred_result.valid
        except Exception as exc:  # S-9: malformed input → invalid, not crash
            vp_result.fail("internal",
                           f"verification aborted on malformed input: "
                           f"{type(exc).__name__}: {exc}")

        vp_result.elapsed_ms = (time.perf_counter() - t0) * 1000
        is_valid = vp_result.valid and all_creds_valid
        report = {
            "valid": is_valid,
            "presentation": vp_result.to_dict(),
            "credentials": credential_reports,
        }
        return is_valid, report

    def _check_vp_proof(self, vp: Dict[str, Any], proof: Dict[str, Any],
                        holder_did: Any, expected_challenge: str,
                        expected_domain: Optional[str],
                        vp_result: VerificationResult) -> None:
        if proof.get("proofPurpose") != "authentication":
            vp_result.fail("vp_purpose",
                           "presentation proofPurpose must be "
                           "'authentication'")
        self._check_proof_metadata(
            proof, "authentication",
            holder_did if isinstance(holder_did, str) else None,
            "vp_proof", vp_result)
        vp_result.ok("vp_proof")
        challenge_ok = proof.get("challenge") == expected_challenge
        if not challenge_ok:
            vp_result.fail("vp_challenge",
                           "challenge mismatch (possible replay)")
        if proof.get("domain") != expected_domain:
            vp_result.fail("vp_domain", "domain mismatch (wrong audience)")
        if self.max_proof_age_s is not None:
            self._check_proof_age(proof, vp_result)

        expected_addr = self._holder_address(holder_did)
        try:
            recovered = recover_signer(vp, proof).lower()
            if expected_addr is None:
                vp_result.fail("vp_signature",
                               f"cannot determine holder address for "
                               f"'{holder_did}'")
            elif recovered != expected_addr:
                vp_result.fail("vp_signature",
                               f"presentation signed by {recovered}, "
                               f"not holder {holder_did}")
            else:
                vp_result.ok("vp_signature")
        except Exception as exc:
            vp_result.fail("vp_signature", f"recovery failed: {exc}")

        # One-shot nonce: consumed once the challenge matched, whatever
        # the rest of the outcome, so a nonce can never be retried.
        if self.nonce_store is not None and challenge_ok and \
                not self.nonce_store.consume(expected_challenge):
            vp_result.fail("vp_challenge",
                           "challenge was not issued by this verifier, "
                           "has expired, or was already used (replay)")

    def _check_proof_age(self, proof: Dict[str, Any],
                         vp_result: VerificationResult) -> None:
        try:
            created = parse_datetime(proof.get("created"))
        except ValueError as exc:
            vp_result.fail("vp_freshness", f"proof 'created' required: {exc}")
            return
        now = datetime.now(timezone.utc)
        if created > now + self.CLOCK_SKEW:
            vp_result.fail("vp_freshness", "proof 'created' is in the future")
        elif now - created > timedelta(seconds=self.max_proof_age_s):
            vp_result.fail("vp_freshness",
                           f"proof older than {self.max_proof_age_s} s")
        vp_result.ok("vp_freshness")


# ---------------------------------------------------------------------------
# W3C VC DM 2.0 compliance self-check (feeds w3c-compliance.yml)
# ---------------------------------------------------------------------------

COMPLIANCE_CHECKLIST = [
    ("@context with base v2 context", True),
    ("credential 'id' (URI)", True),
    ("'type' incl. VerifiableCredential", True),
    ("'issuer' identified by DID", True),
    ("'validFrom' / 'validUntil' (v2 vocabulary)", True),
    ("'credentialSubject' with subject id", True),
    ("'credentialSchema' declared", True),
    ("'credentialStatus' (revocation)", True),
    ("Securing mechanism: embedded DataIntegrityProof", True),
    ("Proof purposes: assertionMethod / authentication", True),
    ("VP with 'holder' + challenge/domain binding", True),
    ("Selective disclosure mechanism", True),
    ("JSON-LD canonicalization (URDNA2015)", False),  # deviation: canonical JSON
    ("Registered cryptosuite (ecdsa-rdfc-2019 etc.)", False),  # thesis-defined suite
]


def compliance_score() -> Tuple[float, List[Tuple[str, bool]]]:
    """Return (percentage, checklist) for the thesis compliance matrix."""
    passed = sum(1 for _, ok in COMPLIANCE_CHECKLIST if ok)
    return 100.0 * passed / len(COMPLIANCE_CHECKLIST), COMPLIANCE_CHECKLIST


if __name__ == "__main__":
    import json as _json
    from vc_issuer import CredentialIssuer
    from vc_holder import HolderWallet

    print("=== Verifier Demo: full issue → present → verify pipeline ===\n")

    issuer = CredentialIssuer.with_ethr_did()
    wallet = HolderWallet.with_ethr_did()
    verifier = CredentialVerifier(
        revocation_registry=issuer.revocation_registry
    )

    envelope = issuer.issue_credential(
        credential_type="VehicleBirthCertificate",
        subject_did=wallet.holder_did,
        claims={
            "vin": "5YJ3E1EA0PF123456",
            "make": "Tesla", "model": "Model 3", "year": 2024,
            "manufacturingDate": "2024-01-15",
            "manufacturerDid": issuer.issuer_did,
        },
        validity_days=None,
    )
    cid = wallet.store_credential(envelope)
    vp = wallet.create_presentation([cid], challenge="nonce-42",
                                    domain="dmv.gov.bc.ca")

    ok, report = verifier.verify_presentation(vp, "nonce-42", "dmv.gov.bc.ca")
    print(f"Presentation valid: {ok}")
    print(_json.dumps(report, indent=2))

    print("\n--- Replay attempt with wrong challenge ---")
    ok2, _ = verifier.verify_presentation(vp, "different-nonce",
                                          "dmv.gov.bc.ca")
    print(f"Replay accepted: {ok2} (must be False)")

    print("\n--- Revocation ---")
    issuer.revoke_credential(cid, reason="test revocation")
    result = verifier.verify_credential(
        wallet.get_credential(cid)
    )
    print(f"After revoke, credential valid: {result.valid} (must be False)")

    score, checklist = compliance_score()
    print(f"\nW3C VC DM 2.0 compliance self-score: {score:.1f}%")
    for item, passed in checklist:
        print(f"  {'✅' if passed else '❌'} {item}")
