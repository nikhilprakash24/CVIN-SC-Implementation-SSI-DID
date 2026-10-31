"""The adaptive responder: tabular Q-learning over request features, shielded by the kernel.

The kernel bounds what can leak; the responder decides how to spend the bound. A global budget alone is a shared
resource an adversary can drain, refusing honest verifiers later (a denial of service against the owner). The
responder learns, from reward in simulation, when to answer exactly, when to coarsen and when to decline, from
features a deployed agent can observe: whether the verifier holds an accreditation credential, whether the
question sits on a bucket boundary, how often this verifier has asked, how many first-time verifiers have
appeared recently, and how much of the budget is spent. It never sees whether a requester is an adversary.

Reward (simulation only): +1 when an honest requester's need is met, 0 when not; minus LAMBDA per bit an
adversary gains. Training uses seeds disjoint from evaluation (attacks/train_responder.py).
"""
from __future__ import annotations

import json
import pathlib
import random

from .kernel import ANSWER, COARSEN, REFUSE, Kernel

ACTIONS = (ANSWER, COARSEN, REFUSE)
LAMBDA = 1.0
Q_FILE = pathlib.Path(__file__).with_name("learned_q.json")


def features(kernel: Kernel, req: dict, history) -> tuple:
    lim = kernel.limit(req["attribute"])
    mon = kernel.monitors.get(req["attribute"])
    lo = 1995
    on_boundary = int(lim is None or (req["threshold"] - lo) % lim["granularity"] == 0)
    asked = sum(1 for h in history if h["verifier"] == req["verifier"])
    recent = history[-10:]
    first_seen = {h["verifier"] for h in recent if h.get("first_time")}
    used = 0 if mon is None or lim is None else mon.global_bits() / max(lim["global_budget_bits"], 1e-9)
    return (int(bool(req.get("accredited"))), on_boundary, min(asked, 2),
            0 if len(first_seen) <= 1 else (1 if len(first_seen) <= 3 else 2), 0 if used < 1 / 3 else (1 if used < 2 / 3 else 2))


class QResponder:
    def __init__(self, table: dict | None = None, epsilon: float = 0.0, rng: random.Random | None = None):
        self.q = table or {}
        self.epsilon = epsilon
        self.rng = rng or random.Random(0)
        self.history: list[dict] = []
        self.last = None

    def values(self, state) -> list[float]:
        return self.q.setdefault(repr(state), [0.0, 0.0, 0.0])

    def __call__(self, kernel: Kernel, req: dict, allowed: dict) -> str:
        state = features(kernel, req, self.history)
        legal = [a for a in ACTIONS if a in allowed or a == REFUSE]
        if self.rng.random() < self.epsilon:
            act = self.rng.choice(legal)
        else:
            vals = self.values(state)
            act = max(legal, key=lambda a: (vals[ACTIONS.index(a)], -ACTIONS.index(a)))
        self.last = (state, act)
        return act

    def observe(self, req: dict, first_time: bool) -> None:
        self.history.append({"verifier": req["verifier"], "first_time": first_time})

    def update(self, reward: float, alpha: float = 0.1) -> None:
        # contextual-bandit update (one-step return): requests are treated as independent decisions
        if self.last is None:
            return
        state, act = self.last
        vals = self.values(state)
        i = ACTIONS.index(act)
        vals[i] += alpha * (reward - vals[i])
        self.last = None

    def save(self, path=Q_FILE, meta: dict | None = None) -> None:
        path.write_text(json.dumps({"meta": meta or {}, "q": dict(sorted(self.q.items()))}, indent=1) + "\n")

    @classmethod
    def load(cls, path=Q_FILE) -> "QResponder":
        return cls(json.loads(pathlib.Path(path).read_text())["q"])
