"""Session leakage of predicate proofs, and the audit rule that bounds it.

Every predicate proof ("model year >= t") is zero-knowledge on its own and still reveals one bit: whether the
predicate holds. A verifier that chooses t adaptively recovers the value by bisection, and a verifier with many
identities (a Sybil set) can spread the questions so that no single identity asks much. Per-proof zero knowledge
is not session privacy (Plan 1, P5). The lineage is the statistical-database literature: Denning's tracker (1979),
Dinur and Nissim's reconstruction (2003), simulatable auditing (Kenthapadi, Mishra and Nissim 2005).

The monitor keeps, for one ordered attribute, the set of values consistent with every answer given to anyone
(the collusion view) and with every answer given to each verifier. Leakage is the drop in Shannon entropy under a
uniform prior: bits = log2(|domain|) - log2(|candidates|).

The audit rule is *simulatable*: whether a question may be answered is decided from the worst case over both
possible answers, never from the true answer. A refusal therefore carries no information about the value; an
auditor that refused only when the true answer leaked too much would leak through its refusals.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


def outcome_set(candidates: frozenset, predicate: str, t: int, outcome: bool) -> frozenset:
    if predicate == "ge":
        return frozenset(v for v in candidates if (v >= t) == outcome)
    if predicate == "le":
        return frozenset(v for v in candidates if (v <= t) == outcome)
    if predicate == "eq":
        return frozenset(v for v in candidates if (v == t) == outcome)
    raise ValueError(predicate)


@dataclass
class LeakageMonitor:
    domain: tuple[int, ...]
    global_set: frozenset = None
    per_verifier: dict = field(default_factory=dict)

    def __post_init__(self):
        self.global_set = frozenset(self.domain)

    @property
    def prior_bits(self) -> float:
        return math.log2(len(self.domain))

    def bits(self, s: frozenset) -> float:
        return self.prior_bits - math.log2(max(len(s), 1))

    def global_bits(self) -> float:
        return self.bits(self.global_set)

    def verifier_bits(self, verifier: str) -> float:
        return self.bits(self.per_verifier.get(verifier, frozenset(self.domain)))

    def worst_case_bits(self, s: frozenset, predicate: str, t: int) -> float:
        """Leakage after answering, maximised over the two answers that could be given (simulatable)."""
        outs = [outcome_set(s, predicate, t, o) for o in (True, False)]
        outs = [o for o in outs if o]  # an impossible answer is never given
        return max(self.bits(o) for o in outs)

    def worst_case(self, verifier: str, predicate: str, t: int) -> tuple[float, float]:
        vs = self.per_verifier.get(verifier, frozenset(self.domain))
        return self.worst_case_bits(self.global_set, predicate, t), self.worst_case_bits(vs, predicate, t)

    def record(self, verifier: str, predicate: str, t: int, outcome: bool) -> None:
        self.global_set = outcome_set(self.global_set, predicate, t, outcome)
        vs = self.per_verifier.get(verifier, frozenset(self.domain))
        self.per_verifier[verifier] = outcome_set(vs, predicate, t, outcome)
