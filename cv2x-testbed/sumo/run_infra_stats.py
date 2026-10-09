#!/usr/bin/env python3
"""
Pre-registered infrastructure-messaging experiments I1, I2, I3 and I5
(docs/design/INFRASTRUCTURE_PREREG.md; design docs/design/INFRASTRUCTURE_MESSAGING.md).

Each run is an independent subprocess of
    sumo_identity_integration.py --simulate --rsu --seed S --duration D
with seeds 1..N, exactly as run_v2v_stats.py does for V2V. Per run we take medians; across runs
we report the median, a 95 % percentile-bootstrap CI of the median (bootstrap seed 20260719, the
same as run_v2v_stats.py), and the pre-registered verdict.

    python3 run_infra_stats.py --runs 30 --duration 20                 # I1, I2, I5
    python3 run_infra_stats.py --runs 30 --duration 20 --revocation    # I3 for k in 1, 5, 25, inf

Writes results/infrastructure_stats.json and/or results/infrastructure_revocation.json.
"""
import argparse
import json
import random
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from run_v2v_stats import bootstrap_ci_of_median, environment_header

SUMO_DIR = Path(__file__).resolve().parent
SCRIPT = SUMO_DIR / "sumo_identity_integration.py"
OUT = SUMO_DIR / "results"
I1_BAND = (0.80, 1.20)
I1_FALSIFY = 2.0


def run_once(seed, duration, extra):
    with tempfile.TemporaryDirectory() as td:
        res = Path(td) / "r.json"
        cmd = [sys.executable, str(SCRIPT), "--simulate", "--rsu", "--seed", str(seed),
               "--duration", str(duration), "--results", str(res)] + extra
        p = subprocess.run(cmd, cwd=str(SUMO_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if p.returncode != 0 or not res.exists():
            raise RuntimeError(f"seed {seed} failed:\n{p.stdout[-2000:]}")
        return json.loads(res.read_text())


def agg(values, rng):
    v = [x for x in values if x is not None]
    return {"run_medians": v, "median": round(statistics.median(v), 6), "mean": round(statistics.fmean(v), 6),
            "ci95": bootstrap_ci_of_median(v, rng=rng)}


def main_i1(args):
    rows = []
    t0 = time.time()
    for seed in range(1, args.runs + 1):
        d = run_once(seed, args.duration, [])
        inf = d["infrastructure"]
        med = lambda b, k: (b.get(k) or {}).get("median_ms")
        row = {"seed": seed,
               "spat_warm": med(inf["spat"], "warm_ms"), "spat_cold": med(inf["spat"], "cold_ms"),
               "spat_sign": med(inf["spat"], "sign_ms"), "bsm_ssi_warm": med(d["ssi"], "warm_ms"),
               "bsm_ssi_cold": med(d["ssi"], "cold_ms"),
               "ctrl_sign": med(inf["i2i_controller_to_rsu"], "sign_ms"),
               "ctrl_verify_warm": med(inf["i2i_controller_to_rsu"], "warm_ms"),
               "tmc_sign": med(inf["i2i_tmc_to_controller"], "sign_ms"),
               "tmc_verify_warm": med(inf["i2i_tmc_to_controller"], "warm_ms"),
               "spat_sent": inf["spat"]["sent"], "spat_verified": inf["spat"]["verified"],
               "spat_rejected": inf["spat"]["rejected"],
               "attacks": {k: v for k, v in d["attack_tests"].items() if k.startswith("i2")}}
        row["ratio_spat_to_bsm_warm"] = row["spat_warm"] / row["bsm_ssi_warm"]
        row["i5_backhaul_ms"] = row["ctrl_sign"] + row["ctrl_verify_warm"] + row["spat_sign"] + row["spat_warm"]
        row["i5_tmc_hop_ms"] = row["tmc_sign"] + row["tmc_verify_warm"]
        rows.append(row)
        print(f"seed {seed:2d}: SPaT warm {row['spat_warm']:.4f} ms, BSM warm {row['bsm_ssi_warm']:.4f} ms, "
              f"ratio {row['ratio_spat_to_bsm_warm']:.3f}, attacks rejected {all(row['attacks'].values())}", flush=True)
    rng = random.Random(20260719)
    ratio = agg([r["ratio_spat_to_bsm_warm"] for r in rows], rng)
    m = ratio["median"]
    i1 = "PASS" if I1_BAND[0] <= m <= I1_BAND[1] else ("FAIL" if m > I1_FALSIFY else "outside band, not falsified")
    attacks = sorted({k for r in rows for k in r["attacks"]})
    i2_ok = all(r["attacks"].get(k) is True for r in rows for k in attacks) and len(attacks) == 7
    out = {
        "environment": environment_header(), "prereg": "docs/design/INFRASTRUCTURE_PREREG.md",
        "config": {"runs": args.runs, "duration_s": args.duration, "vehicles": 50, "rsus": 4,
                   "refresh_k": "inf (I1 compares warm paths without a revocation re-check, as the BSM warm path has none)",
                   "condition": "M0, mock mobility, real cryptography, no radio channel"},
        "I1": {"claim": f"median warm SPaT verify / median warm SSI BSM verify in [{I1_BAND[0]}, {I1_BAND[1]}]; falsified if > {I1_FALSIFY}",
               "ratio": ratio, "verdict": i1,
               "spat_warm_ms": agg([r["spat_warm"] for r in rows], rng), "bsm_ssi_warm_ms": agg([r["bsm_ssi_warm"] for r in rows], rng),
               "spat_cold_ms": agg([r["spat_cold"] for r in rows], rng), "spat_sign_ms": agg([r["spat_sign"] for r in rows], rng)},
        "I2": {"claim": "every injected infrastructure attack rejected in every run", "attacks": attacks,
               "runs_all_rejected": sum(1 for r in rows if all(r["attacks"].values())), "runs": len(rows),
               "verdict": "PASS" if i2_ok else "FAIL"},
        "I5": {"claim": "reported, no verdict",
               "controller_to_vehicle_ms": agg([r["i5_backhaul_ms"] for r in rows], rng),
               "tmc_to_controller_ms": agg([r["i5_tmc_hop_ms"] for r in rows], rng),
               "definition": "controller sign + RSU warm verify + RSU SPaT sign + vehicle warm SPaT verify (per-run medians, summed); TMC hop = TMC sign + controller warm verify"},
        "totals": {"spat_sent": sum(r["spat_sent"] for r in rows), "spat_verified": sum(r["spat_verified"] for r in rows),
                   "spat_rejected_legitimate": sum(r["spat_rejected"] for r in rows)},
        "per_run": rows, "wall_clock_s": round(time.time() - t0, 1),
    }
    (OUT / "infrastructure_stats.json").write_text(json.dumps(out, indent=2))
    print(f"\nI1 ratio median {m:.3f} {ratio['ci95']} -> {i1}; I2 {out['I2']['verdict']}; "
          f"I5 back-haul {out['I5']['controller_to_vehicle_ms']['median']:.3f} ms")


def main_i3(args):
    t0 = time.time()
    per_k = {}
    for k in ("1", "5", "25", "inf"):
        rows = []
        for seed in range(1, args.runs + 1):
            d = run_once(seed, args.duration, ["--refresh-k", k, "--revoke-rsu-at", str(args.revoke_at)])
            rev = d["infrastructure"]["revocation"]
            rows.append({"seed": seed, **{x: rev[x] for x in ("receivers_after_revocation", "max_accepted_after_revocation",
                                                             "total_accepted_after_revocation")}})
        mx = max(r["max_accepted_after_revocation"] for r in rows)
        bound = None if k == "inf" else int(k) - 1
        verdict = ("reported (expected never to stop)" if bound is None else ("PASS" if mx <= bound else "FAIL"))
        per_k[k] = {"bound_k_minus_1": bound, "max_accepted_after_revocation": mx,
                    "mean_total_accepted_after_revocation": round(statistics.fmean(r["total_accepted_after_revocation"] for r in rows), 2),
                    "verdict": verdict, "per_run": rows}
        print(f"k={k}: max accepted after revocation {mx} (bound {bound}) -> {verdict}", flush=True)
    finite = [v["verdict"] for k, v in per_k.items() if k != "inf"]
    out = {"environment": environment_header(), "prereg": "docs/design/INFRASTRUCTURE_PREREG.md",
           "config": {"runs": args.runs, "duration_s": args.duration, "revoke_rsu_1_at_s": args.revoke_at,
                      "condition": "M0, mock mobility, real cryptography"},
           "I3": {"claim": "for every finite k, max SPaT accepted from the revoked RSU per receiver <= k - 1",
                  "per_k": per_k, "verdict": "PASS" if all(v == "PASS" for v in finite) else "FAIL"},
           "wall_clock_s": round(time.time() - t0, 1)}
    (OUT / "infrastructure_revocation.json").write_text(json.dumps(out, indent=2))
    print(f"I3 -> {out['I3']['verdict']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--duration", type=int, default=20)
    ap.add_argument("--revocation", action="store_true")
    ap.add_argument("--revoke-at", type=float, default=10.0)
    a = ap.parse_args()
    (main_i3 if a.revocation else main_i1)(a)
