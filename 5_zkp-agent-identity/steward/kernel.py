"""The policy kernel: deterministic, small, and the only component that can authorise a disclosure.

Input is a structured request (verifier, attribute, predicate, threshold). Output is a decision: ANSWER (prove the
predicate as asked), COARSEN (prove a stronger predicate on a public bucket boundary, so that answers carry only
bucket-level information), or REFUSE, with the reason. The kernel computes which actions the signed policy and the
leakage budget *permit*; a responder (fixed or learned) chooses among the permitted ones. The responder can only
make the kernel more conservative, never less (a shield, in the sense of safe reinforcement learning).

There is no operation that returns a raw attribute value: "reveal" is not a predicate the kernel knows.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass

from .leakage import LeakageMonitor
from .policy import ATTRIBUTES, PREDICATES, verifier_matches

ANSWER, COARSEN, REFUSE = "answer", "coarsen", "refuse"
REQUEST_FIELDS = {"verifier", "attribute", "predicate", "threshold", "nonce", "purpose", "accredited"}


@dataclass
class Decision:
    action: str
    threshold: int | None
    reason: str
    worst_case_global_bits: float = 0.0


class RequestError(ValueError):
    pass


def validate_request(req: dict) -> dict:
    extra = set(req) - REQUEST_FIELDS
    if extra:
        raise RequestError(f"unknown request field(s) {sorted(extra)}")
    for k in ("verifier", "attribute", "predicate"):
        if not isinstance(req.get(k), str):
            raise RequestError(f"{k} must be a string")
    if req["attribute"] not in ATTRIBUTES:
        raise RequestError(f"unknown attribute {req['attribute']!r}")
    if req["predicate"] not in PREDICATES:
        raise RequestError(f"unknown predicate {req['predicate']!r} (there is no 'reveal')")
    if ATTRIBUTES[req["attribute"]]["ordered"] and not isinstance(req.get("threshold"), int):
        raise RequestError("an ordered attribute needs an integer threshold")
    return req


def coarsen_threshold(t: int, predicate: str, lo: int, g: int) -> int:
    """Move t to a bucket boundary in the direction that makes the proof *stronger* than asked."""
    if g <= 1:
        return t
    off = (t - lo) % g
    if off == 0:
        return t
    return t + (g - off) if predicate == "ge" else t - off


class Kernel:
    def __init__(self, policy: dict, today: _dt.date | None = None, consent=None):
        self.policy = policy
        self.today = today or _dt.date(2026, 10, 15)
        self.consent = consent or (lambda req: False)
        self.monitors: dict[str, LeakageMonitor] = {}
        for lim in policy["limits"]:
            lo, hi = ATTRIBUTES[lim["attribute"]]["domain"]
            self.monitors[lim["attribute"]] = LeakageMonitor(tuple(range(lo, hi + 1)))

    def limit(self, attribute: str) -> dict | None:
        return next((l for l in self.policy["limits"] if l["attribute"] == attribute), None)

    def rule_for(self, req: dict) -> dict | None:
        for r in self.policy["rules"]:
            if (verifier_matches(r["verifiers"], req["verifier"]) and r["attribute"] == req["attribute"]
                    and req["predicate"] in r["predicates"]
                    and (r["expires"] is None or self.today.isoformat() <= r["expires"])):
                return r
        return None

    def permitted(self, req: dict) -> tuple[dict[str, int | None], str]:
        """Actions the policy and the budgets allow for this request, with the threshold each would prove."""
        validate_request(req)
        if req["verifier"] in self.policy["blocked_verifiers"]:
            return {}, "verifier blocked by the owner"
        if req["attribute"] in self.policy["never_reveal"]:
            return {}, "attribute is never disclosed"
        rule = self.rule_for(req)
        if rule is None:
            return {}, "no rule allows this verifier, attribute and predicate"
        if rule["consent"] and not self.consent(req):
            return {}, "the owner's consent is required and was not given"
        lim = self.limit(req["attribute"])
        if lim is None or not ATTRIBUTES[req["attribute"]]["ordered"]:
            return {ANSWER: req.get("threshold")}, "allowed by rule"
        mon = self.monitors[req["attribute"]]
        lo = ATTRIBUTES[req["attribute"]]["domain"][0]
        t = req["threshold"]
        options = {ANSWER: t, COARSEN: coarsen_threshold(t, req["predicate"], lo, lim["granularity"])}
        allowed = {}
        for act, tt in options.items():
            g, v = mon.worst_case(req["verifier"], req["predicate"], tt)
            if g > lim["global_budget_bits"] + 1e-9:
                continue
            if lim["per_verifier_budget_bits"] is not None and v > lim["per_verifier_budget_bits"] + 1e-9:
                continue
            allowed[act] = tt
        return allowed, ("allowed within budget" if allowed else "the leakage budget would be exceeded")

    def decide(self, req: dict, responder=None) -> Decision:
        allowed, reason = self.permitted(req)
        if not allowed:
            return Decision(REFUSE, None, reason)
        choice = responder(self, req, allowed) if responder else default_responder(self, req, allowed)
        if choice not in allowed:  # the shield: a responder cannot pick an action the kernel did not permit
            choice = REFUSE
        if choice == REFUSE:
            return Decision(REFUSE, None, "declined by the responder")
        tt = allowed[choice]
        wc = 0.0
        if req["attribute"] in self.monitors:
            wc = self.monitors[req["attribute"]].worst_case(req["verifier"], req["predicate"], tt)[0]
        return Decision(choice, tt, reason, wc)

    def record(self, req: dict, decision: Decision, outcome: bool) -> None:
        if decision.action != REFUSE and req["attribute"] in self.monitors:
            self.monitors[req["attribute"]].record(req["verifier"], req["predicate"], decision.threshold, outcome)


def default_responder(kernel: Kernel, req: dict, allowed: dict) -> str:
    """Fixed heuristic: answer exactly when the question is already on a bucket boundary, otherwise coarsen."""
    if COARSEN in allowed and allowed.get(ANSWER) != allowed[COARSEN]:
        return COARSEN
    return ANSWER if ANSWER in allowed else COARSEN


def answer_all_responder(kernel: Kernel, req: dict, allowed: dict) -> str:
    return ANSWER if ANSWER in allowed else (COARSEN if COARSEN in allowed else REFUSE)
