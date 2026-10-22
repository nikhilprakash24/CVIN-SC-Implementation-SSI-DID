"""The predicate-narrowing ("twenty questions") attack, its Sybil-split variant, and the defences compared.

Parameters are those of Plan 1 amendment A1, fixed before the first run. Simulation, not a field result: the
verifiers, the adversary and the request stream are synthetic and seeded.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from steward.kernel import ANSWER, COARSEN, REFUSE, Kernel, answer_all_responder, default_responder
from steward.learner import LAMBDA, QResponder

LO, HI = 1995, 2026
DOMAIN = tuple(range(LO, HI + 1))
PRIOR_BITS = math.log2(len(DOMAIN))
BOUNDARIES = tuple(range(2000, 2026, 5))
N_HONEST, N_ADV, ACCREDITED = 40, 12, [f"insurer:h{i}" for i in range(6)]
BUDGET, GRANULARITY, STATIC_CAP = 3.0, 5, 2
DEFENCES = ("none", "static_cap", "budget_only", "steward_fixed", "steward", "steward_no_budget")
VARIANTS = ("single", "sybil")
# Post hoc (Plan 1 amendment A2, added after the first trial run): an adversary holding an accreditation credential.
POST_HOC_VARIANTS = ("insider",)


def policy_for(defence: str) -> dict:
    rule = {"verifiers": "insurer:*", "attribute": "model_year", "predicates": ["ge"], "consent": False, "expires": None}
    doc = {"never_reveal": ["vin", "salt", "private_key"], "blocked_verifiers": [], "rules": [rule], "limits": []}
    if defence in ("budget_only",):
        doc["limits"] = [{"attribute": "model_year", "granularity": 1, "global_budget_bits": BUDGET, "per_verifier_budget_bits": None}]
    elif defence in ("steward_fixed", "steward"):
        doc["limits"] = [{"attribute": "model_year", "granularity": GRANULARITY, "global_budget_bits": BUDGET, "per_verifier_budget_bits": None}]
    elif defence == "steward_no_budget":
        doc["limits"] = [{"attribute": "model_year", "granularity": GRANULARITY, "global_budget_bits": 64.0, "per_verifier_budget_bits": None}]
    return doc


class StaticCap:
    """At most STATIC_CAP answers per verifier identity; otherwise answer exactly."""

    def __init__(self):
        self.count = {}

    def __call__(self, kernel, req, allowed):
        n = self.count.get(req["verifier"], 0)
        if n >= STATIC_CAP:
            return REFUSE
        self.count[req["verifier"]] = n + 1
        return answer_all_responder(kernel, req, allowed)


def bits(s) -> float:
    return PRIOR_BITS - math.log2(max(len(s), 1))


@dataclass
class EpisodeResult:
    seed: int
    variant: str
    defence: str
    value: int
    adversary_bits: float
    adversary_exact: bool
    adversary_queries_to_exact: int | None
    honest_requests: int
    honest_served: int
    global_bits: float

    @property
    def honest_service(self) -> float:
        return self.honest_served / max(self.honest_requests, 1)


def run_episode(seed: int, variant: str, defence: str, responder=None, learn: bool = False) -> EpisodeResult:
    rng = random.Random(seed)
    value = rng.choice(DOMAIN)
    kernel = Kernel(policy_for(defence))
    if defence in ("steward", "steward_no_budget"):
        resp = responder if responder is not None else QResponder.load()
    elif defence == "static_cap":
        resp = StaticCap()
    elif defence == "steward_fixed":
        resp = default_responder
    else:
        resp = answer_all_responder
    # the request stream: honest requests and adversary slots, interleaved at random
    slots = ["h"] * N_HONEST + (["a"] * N_ADV if variant != "none" else [])
    rng.shuffle(slots)
    adv_set = set(DOMAIN)
    adv_q, adv_exact_at = 0, None
    honest_n = honest_ok = 0
    seen = set()
    sybil_k = 0
    collusion = set(DOMAIN)
    for slot in slots:
        if slot == "h":
            if rng.random() < 0.10:
                vid, acc = f"insurer:new-{rng.randrange(10**6)}", False
            else:
                vid, acc = rng.choice(ACCREDITED), True
            t = rng.choice(BOUNDARIES) if rng.random() < 0.7 else rng.randint(LO + 1, HI - 1)
            adversarial = False
        else:
            if variant == "single":
                vid = "insurer:adv"
            elif variant == "insider":
                vid = "insurer:adv-accredited"
            else:
                vid, sybil_k = f"insurer:s{sybil_k}", sybil_k + 1
            acc = variant == "insider"
            cand = sorted(adv_set)
            t = cand[len(cand) // 2] if len(cand) > 1 else cand[0]
            adversarial = True
            adv_q += 1
        req = {"verifier": vid, "attribute": "model_year", "predicate": "ge", "threshold": t, "accredited": acc}
        if hasattr(resp, "observe"):
            resp.observe(req, vid not in seen)
        seen.add(vid)
        d = kernel.decide(req, resp)
        outcome = d.action != REFUSE and value >= d.threshold
        kernel.record(req, d, outcome)
        reward = 0.0
        if d.action != REFUSE:
            collusion = {v for v in collusion if (v >= d.threshold) == outcome}
        if adversarial:
            before = bits(adv_set)
            if d.action != REFUSE:
                adv_set = {v for v in adv_set if (v >= d.threshold) == outcome}
            reward = -LAMBDA * (bits(adv_set) - before)
            if len(adv_set) == 1 and adv_exact_at is None:
                adv_exact_at = adv_q
        else:
            honest_n += 1
            met = d.action == ANSWER or (d.action == COARSEN and (outcome or d.threshold == t))
            honest_ok += int(met)
            reward = 1.0 if met else 0.0
        if learn and hasattr(resp, "update"):
            resp.update(reward)
    return EpisodeResult(seed, variant, defence, value, bits(adv_set), len(adv_set) == 1, adv_exact_at,
                         honest_n, honest_ok, bits(collusion))
