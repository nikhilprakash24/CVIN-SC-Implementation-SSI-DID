"""Agents need identity too (Plan 1, P6). The Steward has its own did:ethr DID and holds a delegation credential,
a W3C Verifiable Credential issued by the vehicle owner's DID with the Phase 1 VC layer
(`2_w3c-ssi-layer/verifiable-credentials`), naming the agent, the scope it may act in, the hash of the signed policy
it enforces, and an expiry; the owner can revoke it. A verifier checks the chain owner -> agent -> proof.
"""
from __future__ import annotations

import pathlib
import sys

from eth_account import Account
from eth_account.messages import encode_defunct

_VC = pathlib.Path(__file__).resolve().parents[2] / "2_w3c-ssi-layer" / "verifiable-credentials"
if str(_VC) not in sys.path:
    sys.path.insert(0, str(_VC))

from vc_issuer import CredentialIssuer  # noqa: E402
from vc_verifier import CredentialVerifier  # noqa: E402

CREDENTIAL_TYPE = "AgentDelegationCredential"


def agent_did(address: str, chain_id: str = "0x1") -> str:
    return f"did:ethr:{chain_id}:{address}"


def issue_delegation(owner: CredentialIssuer, agent_address: str, scope: list[str], policy_hash: str,
                     validity_days: int = 90) -> dict:
    issued = owner.issue_credential(
        CREDENTIAL_TYPE, agent_did(agent_address),
        {"role": "identity-steward", "scope": scope, "policyHash": policy_hash},
        validity_days=validity_days, enforce_schema=False)
    return issued["verifiableCredential"]


def verify_delegation(vc: dict, owner: CredentialIssuer, agent_address: str, presentation_text: str,
                      agent_signature: str, required_scope: str) -> tuple[bool, str]:
    """Owner signed it, it is unexpired and unrevoked, it names this agent and scope, and the agent signed now."""
    result = CredentialVerifier(revocation_registry=owner.revocation_registry, strict_schema=False).verify_credential(vc)
    if not result.valid:
        return False, "delegation credential invalid: " + "; ".join(result.errors)
    issuer = vc["issuer"] if isinstance(vc["issuer"], str) else vc["issuer"].get("id")
    if issuer != owner.issuer_did:
        return False, "issued by someone other than the owner"
    subj = vc["credentialSubject"]
    if subj.get("id") != agent_did(agent_address):
        return False, "credential names a different agent"
    if required_scope not in subj.get("scope", []):
        return False, "scope not delegated"
    signer = Account.recover_message(encode_defunct(text=presentation_text),
                                     signature=bytes.fromhex(agent_signature.removeprefix("0x")))
    if signer != agent_address:
        return False, "presentation not signed by the delegated agent"
    return True, "ok"
