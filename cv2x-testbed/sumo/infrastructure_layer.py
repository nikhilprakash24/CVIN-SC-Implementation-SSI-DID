"""
Infrastructure identity layer: roadside units, signal controllers and a traffic-management centre
as credentialed DIDs (design: docs/design/INFRASTRUCTURE_MESSAGING.md; pre-registration:
docs/design/INFRASTRUCTURE_PREREG.md, experiments I1-I5).

An RSU is one more DID. A road authority (the trust anchor) issues it an
InfrastructureStationCredential that lists the message types it may sign (SPaT, MAP); controllers
and the TMC get credentials the same way. Messages are signed exactly like the SSI BSMs in
sumo_identity_integration.py (EIP-191 over sha256 of canonical JSON, with a signed timestamp), so
the comparison with V2V is like for like.

Verification at a receiver:
  every message : freshness window on the signed timestamp (review-2 T-9 policy: `stale` if older
                  than 1 s, `future` if more than 0.1 s ahead), a per-receiver replay check inside
                  the window (`replay`; a broadcast reaching many receivers is not a replay), and
                  signature recovery;
  cold (first contact with a signer DID): the credential is verified by the canonical VC layer
                  (trusted issuer = the road authority only, validity window, revocation), the
                  credential subject must be the sender DID, the recovered address must be the DID's
                  address, the message type must be in the credential's permittedMessages, and the
                  message's `intersection` / `rsu` fields, when the credential names an
                  intersectionId / stationId, must equal them (`binding`);
  warm          : recovered address equals the cached one, the message type is permitted, the field
                  binding holds and the credential has not expired;
                  every k-th message from a cached signer re-checks the authority's revocation
                  registry (k = refresh_every; None = never, i.e. k = infinity). A revoked signer is
                  dropped from the cache and the message rejected. The counter counts messages
                  presented under the cached DID (forged ones included), so a forgery can only make
                  the re-check come sooner.

Hardened after the adversarial review of after-action report 11 (binding, replay, warm expiry,
distinct reasons); pre-registration amendment A4.

What is real: all key generation, signing, signature recovery and credential verification
(time.perf_counter). What is not: the radio (in-process delivery, as for V2V) and the back-haul
network (in-process; real back-haul is wired, often TLS or a private network).
"""
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from eth_account import Account
from eth_account.messages import encode_defunct

from identity.freshness import FreshnessPolicy
from identity.w3c_verifiable_credentials import CredentialIssuer, CredentialVerifier

STATION_CREDENTIAL = {
    "rsu": "InfrastructureStationCredential",
    "controller": "SignalControllerCredential",
    "tmc": "TrafficManagementCredential",
}


def canonical(message: Dict[str, Any]) -> bytes:
    return json.dumps(message, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def signable(message: Dict[str, Any]):
    return encode_defunct(hashlib.sha256(canonical(message)).digest())


def _doc(credential: Any) -> Dict[str, Any]:
    return credential.to_dict() if hasattr(credential, "to_dict") else credential


def _expiry(doc: Dict[str, Any]) -> Optional[float]:
    exp = doc.get("validUntil") or doc.get("expirationDate")   # VC 2.0, then VC 1.1
    if not exp:
        return None
    dt = datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
    return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).timestamp()


def _binding_ok(message: Dict[str, Any], binding: Dict[str, Any]) -> bool:
    """Message fields that name an intersection or station must match the credential."""
    if binding.get("intersectionId") is not None and message.get("intersection") != binding["intersectionId"]:
        return False
    if binding.get("stationId") is not None and "rsu" in message and message["rsu"] != binding["stationId"]:
        return False
    return True


_FRESHNESS_REASON = {"stale": "stale", "timestamp in the future": "future", "replay": "replay"}


class InfrastructureLayer:
    """Road authority + infrastructure stations + verifier caches."""

    def __init__(self, clock=None, refresh_every: Optional[int] = None):
        if refresh_every is not None and refresh_every < 1:
            raise ValueError("refresh_every must be >= 1 or None (infinity)")
        self.refresh_every = refresh_every
        # Replay keys are (receiver, sender): one SPaT broadcast to eight vehicles is eight first
        # receptions, not seven replays.
        self.freshness = FreshnessPolicy(replay_cache=True, clock=clock)
        authority = Account.create()
        self.authority_did = f"did:ethr:0x1:{authority.address}"
        self.authority = CredentialIssuer(self.authority_did, authority.key.hex(), "CVIN Road Authority")
        # Only the road authority is trusted for infrastructure messages.
        self.verifier = CredentialVerifier(trusted_issuers=[self.authority])
        # An authority nobody trusts, for attack I2(e).
        rogue = Account.create()
        self.rogue_authority = CredentialIssuer(f"did:ethr:0x1:{rogue.address}", rogue.key.hex(), "Rogue Authority")
        self.stations: Dict[str, Dict[str, Any]] = {}
        # receiver_id -> {sender_did: {"address", "permitted", "credential_id", "seen"}}
        self._cache: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # ---------------------------------------------------------------- enrolment
    def enroll(self, station_id: str, kind: str, permitted: List[str],
               position: Optional[Tuple[float, float]] = None,
               issuer: Optional[CredentialIssuer] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        account = Account.create()
        did = f"did:ethr:0x1:{account.address}"
        claims = {"stationId": station_id, "stationKind": kind, "permittedMessages": list(permitted)}
        if position is not None:
            claims["location"] = {"x": round(position[0], 1), "y": round(position[1], 1)}
        if extra:
            claims.update(extra)
        credential = (issuer or self.authority).issue_credential(
            credential_type=STATION_CREDENTIAL.get(kind, "InfrastructureStationCredential"),
            subject_did=did, claims=claims, validity_days=365)
        station = {"id": station_id, "kind": kind, "account": account, "did": did,
                   "credential": credential, "credential_id": _doc(credential)["id"],
                   "permitted": list(permitted), "position": position}
        self.stations[station_id] = station
        return station

    def revoke(self, station_id: str, reason: str = "compromised") -> None:
        self.authority.revoke_credential(self.stations[station_id]["credential_id"], reason=reason)

    # ---------------------------------------------------------------- signing
    def sign(self, station_id: str, message: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        station = self.stations[station_id]
        t0 = time.perf_counter()
        sig = Account.sign_message(signable(message), station["account"].key)
        package = {"message": message, "sender_did": station["did"], "signature": sig.signature.hex(),
                   "credential": station["credential"], "identity_type": "infra_vc"}
        return package, (time.perf_counter() - t0) * 1000.0

    # ---------------------------------------------------------------- verification
    def verify(self, receiver_id: str, package: Dict[str, Any],
               now: Optional[float] = None) -> Tuple[bool, float, bool, Optional[str]]:
        """Returns (ok, latency_ms, cold, reason). `reason` names why a message was rejected."""
        t0 = time.perf_counter()
        reason = None
        ok = False
        cold = True
        try:
            cache = self._cache.setdefault(receiver_id, {})
            sender_did = package["sender_did"]
            if not isinstance(sender_did, str):
                raise TypeError("sender_did must be a string")
            cold = sender_did not in cache
            message = package["message"]
            msg_type = message.get("msg_type")
            replay_key = f"{receiver_id}|{sender_did}"
            payload = canonical(message)
            fresh = self.freshness.check(message.get("timestamp"), replay_key, payload, now=now)
            if fresh is not None:
                reason = next((v for k, v in _FRESHNESS_REASON.items() if fresh.startswith(k)), "bad_timestamp")
            elif not package.get("signature"):
                reason = "unsigned"
            else:
                recovered = Account.recover_message(signable(message), signature=package["signature"])
                if not cold:
                    entry = cache[sender_did]
                    entry["seen"] += 1
                    if self.refresh_every is not None and entry["seen"] % self.refresh_every == 0:
                        if self.authority.revocation_registry.is_revoked(entry["credential_id"]):
                            del cache[sender_did]
                            reason = "revoked"
                    if reason is None:
                        if recovered.lower() != entry["address"].lower():
                            reason = "wrong_key"
                        elif entry["expires"] is not None and time.time() > entry["expires"]:
                            del cache[sender_did]
                            reason = "expired"
                        elif msg_type not in entry["permitted"]:
                            reason = "not_permitted"
                        elif not _binding_ok(message, entry["binding"]):
                            reason = "binding"
                        else:
                            ok = True
                else:
                    credential = package.get("credential")
                    if credential is None:
                        reason = "no_credential"
                    else:
                        valid, _report = self.verifier.verify_credential(credential)
                        doc = _doc(credential)
                        subject = doc.get("credentialSubject", {})
                        permitted = subject.get("permittedMessages", [])
                        binding = {"intersectionId": subject.get("intersectionId"),
                                   "stationId": subject.get("stationId")}
                        if not valid:
                            reason = "credential_invalid"   # untrusted issuer, expired or revoked
                        elif subject.get("id") != sender_did:
                            reason = "subject_mismatch"
                        elif recovered.lower() != sender_did.rsplit(":", 1)[-1].lower():
                            reason = "wrong_key"
                        elif msg_type not in permitted:
                            reason = "not_permitted"
                        elif not _binding_ok(message, binding):
                            reason = "binding"
                        else:
                            cache[sender_did] = {"address": recovered, "permitted": list(permitted),
                                                 "credential_id": doc["id"], "seen": 0,
                                                 "binding": binding, "expires": _expiry(doc)}
                            ok = True
            if ok:
                self.freshness.accept(replay_key, payload, message.get("timestamp"), now=now)
        except Exception as e:  # malformed input is a rejection, never a crash
            reason = reason or f"error:{type(e).__name__}"
            ok = False
        return ok, (time.perf_counter() - t0) * 1000.0, cold, reason
