"""Evaluate every defence against both attack variants on seeds 1-30 and compute Z-E5 and Z-E6 by rule
(Plan 1 §1.1 and amendment A1). Writes results/attacks.json.

    python3 attacks/run_attacks.py
"""
from __future__ import annotations

import json
import math
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from bench.runid import run_identity  # noqa: E402
from simulate import BUDGET, DEFENCES, DOMAIN, POST_HOC_VARIANTS, PRIOR_BITS, VARIANTS, run_episode  # noqa: E402

SEEDS = range(1, 31)


def summarise(eps):
    ab = [e.adversary_bits for e in eps]
    hs = [e.honest_service for e in eps]
    return {"adversary_bits": {"mean": statistics.mean(ab), "max": max(ab), "min": min(ab)},
            "adversary_exact_recoveries": sum(e.adversary_exact for e in eps),
            "honest_service": {"mean": statistics.mean(hs), "min": min(hs)},
            "per_seed": [{"seed": e.seed, "value": e.value, "adversary_bits": round(e.adversary_bits, 4),
                          "exact": e.adversary_exact, "queries_to_exact": e.adversary_queries_to_exact,
                          "honest_service": round(e.honest_service, 4), "collusion_bits": round(e.global_bits, 4)}
                         for e in eps]}


def main():
    table = {}
    for d in DEFENCES:
        for v in VARIANTS + ("none",) + POST_HOC_VARIANTS:
            table[f"{d}|{v}"] = [run_episode(s, v, d) for s in SEEDS]
    bound = math.ceil(math.log2(len(DOMAIN)))
    ze5 = all(e.adversary_exact and e.adversary_queries_to_exact <= bound for e in table["none|single"])
    ze6 = all(e.adversary_bits <= BUDGET + 1e-9 and e.honest_service >= 0.90
              for v in VARIANTS for e in table[f"steward|{v}"])
    ze6_leak = all(e.adversary_bits <= BUDGET + 1e-9 for v in VARIANTS for e in table[f"steward|{v}"])
    ze6_serv = [round(e.honest_service, 4) for v in VARIANTS for e in table[f"steward|{v}"]]
    out = {
        "condition": "simulation (synthetic verifiers and adversary), seeds 1-30, parameters of Plan 1 amendment A1",
        "run": run_identity(),
        "prior_bits": PRIOR_BITS,
        "budget_bits": BUDGET,
        "expectations": {
            f"Z-E5 undefended single-verifier attack recovers the exact value in <= {bound} queries on every seed":
                "PASS" if ze5 else "FAIL",
            "Z-E6 Steward keeps adversary leakage <= 3.0 bits AND serves >= 90% of honest requests, on every seed of both variants":
                "PASS" if ze6 else "FAIL",
        },
        "z_e6_parts": {"leakage_bound_held_on_all_60": ze6_leak,
                       "seeds_below_90pct_service": sum(1 for x in ze6_serv if x < 0.90),
                       "min_service": min(ze6_serv)},
        "results": {k: summarise(v) for k, v in table.items() if k.split("|")[1] not in POST_HOC_VARIANTS},
        "post_hoc_A2_insider": {k: summarise(v) for k, v in table.items() if k.split("|")[1] in POST_HOC_VARIANTS},
    }
    p = HERE.parent / "results" / "attacks.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["expectations"], indent=1), out["z_e6_parts"])
    for k, v in {**out["results"], **out["post_hoc_A2_insider"]}.items():
        print(f"{k:28s} adv bits mean {v['adversary_bits']['mean']:.2f} max {v['adversary_bits']['max']:.2f} "
              f"exact {v['adversary_exact_recoveries']:2d}/30  honest {v['honest_service']['mean']:.3f} (min {v['honest_service']['min']:.3f})")


if __name__ == "__main__":
    main()
