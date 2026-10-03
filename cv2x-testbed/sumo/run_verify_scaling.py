#!/usr/bin/env python3
"""
Experiment D — V2V verification saturation point vs neighbor density (RQ-S3b)
=============================================================================

Dedicated measurement driver for the dense-intersection scaling study
(docs/SCALING_EXPERIMENTS.md §Experiment D). It reuses the REAL SSI identity
layer from ``sumo_identity_integration.py`` (secp256k1 EIP-191 sign at the
sender, signature recovery + cached-peer address comparison at the receiver —
the WARM V2V verification path) WITHOUT touching that file, so the main
simulation's MAX_NEIGHBORS=8 runtime cap is left intact.

Question: at a 10 Hz BSM rate every vehicle has a 100 ms budget to verify all
messages received in that interval. As neighbor density P grows, how much of
that budget does per-vehicle verification consume, and at what P* does it blow
the 100 ms budget?

Design:
  - One receiver vehicle; P sender neighbors, P in {5,10,20,40,80}.
  - All peers pre-cached (warm): the receiver has already done first-contact
    VC verification for every neighbor, so each per-message cost is the warm
    path (recover secp256k1 signer + compare to cached address).
  - Per interval, every neighbor signs a fresh BSM (position/seq change each
    100 ms tick). Signing is done OUTSIDE the timed region; we time only the
    receiver verifying all P messages -> per-vehicle per-interval verification
    time. Reported statistic is the MEDIAN over >=200 warm intervals.

Saturation point P*: smallest P whose median per-interval verification time
exceeds the 100 ms budget. If none within P<=80, we report "beyond tested
range" and extrapolate P* from a least-squares linear fit of per-interval time
vs P (verification is per-message-independent, so the total is ~linear in P).

Honesty (docs/RESEARCH_AUDIT.md §4.4): crypto verification LOAD ONLY. Excludes
radio propagation, MAC-layer contention, channel loss and queueing — messages
are delivered in-process. This is a CPU-time saturation bound, not an
end-to-end V2V latency.

Appends a ``v2v_density`` block to
4_comparison-framework/results/scaling_verify.json (created by the Experiment C
driver run_verify_richness.py; this driver creates the file if run first).

Usage:
    python3 run_verify_scaling.py [--intervals 300] [--warmup 50]
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

SUMO_DIR = Path(__file__).resolve().parent
CV2X_ROOT = SUMO_DIR.parent
REPO_ROOT = CV2X_ROOT.parent
OUT_JSON = (REPO_ROOT / "4_comparison-framework" / "results"
            / "scaling_verify.json")

# Import the REAL SSI identity layer without running the main simulation.
sys.path.insert(0, str(CV2X_ROOT))
from sumo.sumo_identity_integration import SSIIdentityLayer  # noqa: E402

P_VALUES = [5, 10, 20, 40, 80]
P_MAX = max(P_VALUES)
BUDGET_MS = 100.0          # 10 Hz BSM interval = 100 ms
RECEIVER = "rx_focus"


def build_bsm(sender_id, seq, sim_time):
    """A BSM payload comparable to sumo_identity_integration._build_bsm."""
    return {
        "msg_type": "BSM",
        "seq": seq,
        "sender": sender_id,
        "timestamp": round(sim_time, 3),
        "position": [round(10.0 + seq * 0.7, 2), 500.0],
        "speed": round(25.0 + (seq % 7) * 0.3, 2),
        "heading": 90.0,
        "emergency": False,
    }


def linear_fit(xs, ys):
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    b, a = np.polyfit(x, y, 1)          # slope, intercept
    yhat = a + b * x
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(b), float(a), r2


def p95(sorted_vals):
    n = len(sorted_vals)
    return sorted_vals[min(n - 1, int(np.ceil(0.95 * n)) - 1)]


def main():
    ap = argparse.ArgumentParser(description="Experiment D: V2V verification "
                                             "saturation vs neighbor density")
    ap.add_argument("--intervals", type=int, default=300,
                    help="timed warm 100 ms intervals per P (>=200; default 300)")
    ap.add_argument("--warmup", type=int, default=50,
                    help="untimed warmup intervals per P (default 50)")
    args = ap.parse_args()

    print("Experiment D — V2V verification saturation vs neighbor density")
    print(f"  SSI layer: {CV2X_ROOT}/sumo/sumo_identity_integration.py")
    print(f"  {args.intervals} timed intervals/P, {args.warmup} warmup/P\n")

    layer = SSIIdentityLayer()
    senders = [f"veh_{i:03d}" for i in range(P_MAX)]
    for s in senders:
        layer.enroll(s, "5YJ3E1EA0PF12345" + s[-1], "Tesla", "Model 3", 2024)

    # Warm the receiver's peer cache: first-contact VC verification for every
    # neighbor, so every subsequent verify is the warm signature-recovery path.
    for s in senders:
        pkg, _ = layer.sign(s, build_bsm(s, 0, 0.0))
        ok, _, cold = layer.verify(RECEIVER, pkg)
        assert ok and cold, f"cold warm-up failed for {s}"
    for s in senders:  # confirm warm path is now active
        pkg, _ = layer.sign(s, build_bsm(s, 1, 0.1))
        ok, _, cold = layer.verify(RECEIVER, pkg)
        assert ok and not cold, f"peer {s} not cached after first contact"

    ps, per_interval_median, per_interval_p95, per_interval_mean = [], [], [], []
    per_message_median = []
    for P in P_VALUES:
        subset = senders[:P]

        # Warmup intervals (untimed).
        for w in range(args.warmup):
            pkgs = [layer.sign(s, build_bsm(s, 100 + w, 0.1))[0] for s in subset]
            for pkg in pkgs:
                layer.verify(RECEIVER, pkg)

        totals = []
        per_msg = []
        for it in range(args.intervals):
            # Sign P fresh BSMs OUTSIDE the timed region.
            pkgs = [layer.sign(s, build_bsm(s, 1000 + it, it * 0.1))[0]
                    for s in subset]
            t0 = time.perf_counter()
            for pkg in pkgs:
                ok, ms, cold = layer.verify(RECEIVER, pkg)
                per_msg.append(ms)
                if not ok or cold:
                    raise RuntimeError("expected warm successful verification")
            totals.append((time.perf_counter() - t0) * 1000.0)

        totals.sort()
        med = statistics.median(totals)
        ps.append(P)
        per_interval_median.append(round(med, 5))
        per_interval_p95.append(round(p95(totals), 5))
        per_interval_mean.append(round(statistics.fmean(totals), 5))
        per_message_median.append(round(statistics.median(per_msg), 6))
        util = 100.0 * med / BUDGET_MS
        print(f"  P={P:3d}  per-interval median={med:8.4f} ms  "
              f"p95={p95(totals):8.4f} ms  ({util:5.2f}% of {BUDGET_MS:.0f} ms budget)")

    # Saturation point within the tested range.
    saturation_P = next((P for P, m in zip(ps, per_interval_median)
                         if m > BUDGET_MS), None)

    # Linear extrapolation P* = (budget - intercept) / slope.
    slope, intercept, r2 = linear_fit(ps, per_interval_median)
    extrapolated_P = ((BUDGET_MS - intercept) / slope) if slope > 0 else None

    if saturation_P is not None:
        note = (f"per-interval verification exceeds the {BUDGET_MS:.0f} ms budget "
                f"at P*={saturation_P} neighbors")
    else:
        note = (f"per-interval verification stays within the {BUDGET_MS:.0f} ms "
                f"budget across the whole tested range (P<=80); saturation is "
                f"beyond the tested range, extrapolated P*~="
                f"{extrapolated_P:.0f} neighbors")

    print(f"\n  fit: per_interval_ms ~= {intercept:.4f} + {slope:.5f}*P  "
          f"(R^2={r2:.4f})")
    print(f"  {note}")

    block = {
        "P": ps,
        "per_interval_ms": per_interval_median,
        "per_interval_p95_ms": per_interval_p95,
        "per_interval_mean_ms": per_interval_mean,
        "per_message_median_ms": per_message_median,
        "budget_ms": BUDGET_MS,
        "saturation_P": saturation_P,
        "extrapolated_saturation_P": (round(extrapolated_P, 1)
                                      if extrapolated_P else None),
        "fit": {
            "slope_ms_per_neighbor": round(slope, 6),
            "intercept_ms": round(intercept, 6),
            "r2": round(r2, 4),
        },
        "intervals_per_point": args.intervals,
        "warmup_per_point": args.warmup,
        "saturation_note": note,
        "method": (
            "Reuses SSIIdentityLayer from sumo_identity_integration.py (real "
            "secp256k1 EIP-191 sign at sender, signature recovery + cached-peer "
            "address comparison at receiver = warm V2V verify path). One receiver "
            "verifies P pre-cached neighbors per 100 ms interval; P neighbors are "
            "signed fresh each interval OUTSIDE the timed region, and only the "
            "receiver's P verifications are timed (time.perf_counter). Reported "
            "per_interval_ms is the MEDIAN over the timed intervals. P* is the "
            "smallest P whose median exceeds 100 ms; if none within P<=80 it is "
            "extrapolated from a least-squares linear fit."
        ),
        "honesty": (
            "Crypto verification LOAD ONLY (RESEARCH_AUDIT §4.4). Excludes radio "
            "propagation, MAC-layer contention, channel loss and queueing; BSMs "
            "are delivered in-process. This is a CPU-time saturation bound, not "
            "end-to-end V2V latency. Warm path (cached peers) only — first-contact "
            "VC verification is amortised and not included per interval."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if OUT_JSON.exists():
        try:
            existing = json.loads(OUT_JSON.read_text())
        except Exception:
            existing = {}
    existing["v2v_density"] = block
    OUT_JSON.write_text(json.dumps(existing, indent=2))
    print(f"\nAppended v2v_density to {OUT_JSON}")


if __name__ == "__main__":
    main()
