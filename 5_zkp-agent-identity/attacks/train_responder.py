"""Train the Steward's responder (tabular, one-step Q-learning) on seeds 10,000-12,999 (Plan 1 amendment A1),
disjoint from the evaluation seeds 1-30. Deterministic: same seeds, same table.

    python3 attacks/train_responder.py   # writes steward/learned_q.json and results/learning_curve.json
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from simulate import run_episode  # noqa: E402
from steward.learner import QResponder  # noqa: E402

SEEDS = range(10_000, 13_000)
EVAL_EVERY = 250


def main():
    table = {}
    curve = []
    rng = random.Random(7)
    for i, seed in enumerate(SEEDS):
        variant = ("none", "single", "sybil")[seed % 3]
        eps = max(0.02, 0.3 * (1 - i / len(SEEDS)))
        r = QResponder(table, epsilon=eps, rng=rng)
        run_episode(seed, variant, "steward", responder=r, learn=True)
        table = r.q
        if (i + 1) % EVAL_EVERY == 0:
            # held-out check on 30 seeds outside both ranges, greedy policy
            stats = []
            for s in range(20_000, 20_030):
                for v in ("single", "sybil"):
                    e = run_episode(s, v, "steward", responder=QResponder(json.loads(json.dumps(table))))
                    stats.append((e.adversary_bits, e.honest_service))
            curve.append({"episodes": i + 1, "epsilon": round(eps, 4),
                          "adversary_bits_mean": sum(a for a, _ in stats) / len(stats),
                          "honest_service_mean": sum(h for _, h in stats) / len(stats)})
            print(curve[-1])
    QResponder(table).save(meta={"trained_on_seeds": [SEEDS.start, SEEDS.stop - 1], "episodes": len(SEEDS),
                                 "algorithm": "tabular one-step Q-learning (contextual bandit), alpha 0.1, "
                                              "epsilon 0.3 linearly to 0.02", "reward": "honest met +1; adversary -1 per bit"})
    out = HERE.parent / "results" / "learning_curve.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"condition": "simulation, seeded; held-out seeds 20000-20029", "curve": curve}, indent=1) + "\n")


if __name__ == "__main__":
    main()
