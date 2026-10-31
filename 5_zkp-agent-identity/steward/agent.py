"""The Steward: an agent that wraps a vehicle's identity.

    owner text --compiler--> policy --owner signs--> kernel   <--- structured request <--- interpreter <--- verifier
                                                       |                                     (may be a model)
                                     responder (learned) chooses among permitted actions
                                                       |
                       vault proves (zkid threshold proof) --> response + audit entry (hash chain, Merkle root)

What the Steward does for the owner that the owner could not do by hand: holds keys and salts without showing them,
turns intentions in English into an enforceable policy, computes zero-knowledge proofs, remembers every disclosure
to every verifier, bounds the total leakage under collusion, adapts its responses, keeps a verifiable record, and
presents its own delegated identity. Each line of that list is a test in tests/test_steward.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from zkid import sigma

from .audit import AuditLog
from .compiler import GrammarCompiler
from .kernel import REFUSE, Kernel, RequestError, default_responder, validate_request
from .policy import PolicyError, SignedPolicy, is_narrower_or_equal, policy_hash
from .vault import Vault


@dataclass
class Response:
    status: str  # "proved", "not-provable", "refused", "rejected"
    reason: str
    threshold: int | None = None
    proof: object = None
    commitment_hex: str | None = None
    agent_signature: str | None = None
    audit_hash: str | None = None


@dataclass
class Steward:
    vault: Vault
    owner_address: str
    signed_policy: SignedPolicy
    responder: object = None
    interpreter: object = None  # maps a free-text verifier message to a structured request (may be a model)
    consent: object = None
    audit: AuditLog = field(default_factory=AuditLog)

    def __post_init__(self):
        if not self.signed_policy.verify(self.owner_address):
            raise PolicyError("the policy is not signed by the owner")
        self.kernel = Kernel(self.signed_policy.doc, consent=self.consent)
        self._seen: set[str] = set()

    # ------------------------------------------------------------------ policy changes

    def propose_policy(self, text: str, compiler=None) -> tuple[bool, list[str]]:
        """Compile English into a draft. Adopt it only if it is no wider than the signed policy."""
        draft = (compiler or GrammarCompiler()).compile(text, base=self.signed_policy.doc)
        ok, why = is_narrower_or_equal(draft, self.signed_policy.doc)
        self.audit.append({"type": "policy-proposal", "adopted": ok, "draft_hash": policy_hash(draft), "why": why})
        if ok:
            self._adopt(draft, self.signed_policy)
        return ok, why

    def adopt_signed(self, signed: SignedPolicy) -> None:
        if not signed.verify(self.owner_address):
            raise PolicyError("the policy is not signed by the owner")
        self.audit.append({"type": "policy-signed", "hash": policy_hash(signed.doc)})
        self._adopt(signed.doc, signed)

    def _adopt(self, doc: dict, signed: SignedPolicy) -> None:
        monitors = self.kernel.monitors
        self.kernel = Kernel(doc, consent=self.consent)
        for a, m in monitors.items():  # memory of past disclosures survives a policy change
            if a in self.kernel.monitors:
                self.kernel.monitors[a] = m
        self.signed_policy = SignedPolicy(doc, signed.signer, signed.signature) if doc is signed.doc else self.signed_policy
        self.effective_policy = doc

    # ------------------------------------------------------------------ requests

    def handle(self, message, rng=None) -> Response:
        try:
            req = self.interpreter(message) if (self.interpreter and not isinstance(message, dict)) else message
            req = validate_request(dict(req))
        except (RequestError, TypeError, ValueError) as e:
            h = self.audit.append({"type": "rejected", "error": str(e)})
            return Response("rejected", str(e), audit_hash=h)
        first = req["verifier"] not in self._seen
        self._seen.add(req["verifier"])
        if hasattr(self.responder, "observe"):
            self.responder.observe(req, first)
        decision = self.kernel.decide(req, self.responder or default_responder)
        if decision.action == REFUSE:
            h = self.audit.append({"type": "refused", "verifier": req["verifier"], "attribute": req["attribute"],
                                   "reason": decision.reason})
            return Response("refused", decision.reason, audit_hash=h)
        context = f"{req['verifier']}|{req.get('nonce', '')}|{req['attribute']}".encode()
        outcome = self.vault.holds(req["attribute"], req["predicate"], decision.threshold)
        proof = None
        if req["predicate"] == "ge" and outcome:
            proof = self.vault.prove_ge(req["attribute"], decision.threshold, context, rng=rng)
        self.kernel.record(req, decision, outcome)
        C = self.vault.commitment(req["attribute"])
        status = "proved" if outcome else "not-provable"
        sig = self.vault.sign(f"{status}|{context.decode()}|{decision.threshold}|{C.hex()}")
        h = self.audit.append({"type": status, "verifier": req["verifier"], "attribute": req["attribute"],
                               "predicate": req["predicate"], "asked": req.get("threshold"),
                               "proved": decision.threshold, "action": decision.action})
        return Response(status, decision.reason, decision.threshold, proof, C.hex(), sig, h)


def verify_response(resp: Response, verifier: str, nonce: str, attribute: str) -> bool:
    """What a verifier runs: the proof checks against the commitment and is bound to its own identity and nonce."""
    from zkid.ec import decode
    if resp.status != "proved" or resp.proof is None:
        return False
    C = decode(bytes.fromhex(resp.commitment_hex))
    return sigma.threshold_verify(C, resp.threshold, resp.proof, 6, f"{verifier}|{nonce}|{attribute}".encode())
