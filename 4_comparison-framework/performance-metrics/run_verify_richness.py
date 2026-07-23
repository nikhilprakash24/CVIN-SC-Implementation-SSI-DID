#!/usr/bin/env python3
"""
Experiment C — Verification latency vs credential richness (RQ-S3a)
===================================================================

Measures REAL W3C Verifiable Credential verification latency as a function of
credential richness, using the canonical VC layer in
``2_w3c-ssi-layer/verifiable-credentials/`` (vc_issuer / vc_holder /
vc_verifier — real secp256k1 EIP-191 sign + public-key recovery, VC DM 2.0).

Two sweeps (design fixed in docs/SCALING_EXPERIMENTS.md §Experiment C):

  1. credential_richness — issue a VC carrying N in {1,2,4,8,16,32} claims and
     measure full verify_credential() latency (structure, schema, temporal,
     revocation, secp256k1 issuer-signature recovery, disclosure). The median
     over >=200 warm runs is the reported statistic; p95 is the warm tail.

  2. selective_disclosure — issue ONE selective-disclosure VC with N=16 salted
     claim digests, then disclose k in {1,2,4,8,16} claim+salt pairs and measure
     verify_credential() (signature recovery over the 16-digest signed document
     is constant in k; the k salted-digest recomputations are the marginal cost).

Analysis: least-squares fit of latency(N) and latency(k); report the scaling
order and whether latency stays well under the 10 ms signature-check target
across the whole range.

Honesty (docs/RESEARCH_AUDIT.md §4.5 / thesis §5.4): this is a *repeatability*
measurement on a single host, crypto-only. Absolute latencies are
hardware-dependent; the median-of-warm-runs and the scaling ORDER are the
transferable results, not a population confidence interval.

Writes 4_comparison-framework/results/scaling_verify.json (Experiment D's
driver appends v2v_density to the same file).

Usage:
    python3 run_verify_richness.py [--runs 300] [--warmup 50]
"""

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
VC_DIR = REPO_ROOT / "2_w3c-ssi-layer" / "verifiable-credentials"
RESULTS_DIR = HERE.parent / "results"
OUT_JSON = RESULTS_DIR / "scaling_verify.json"

# Import the REAL canonical VC layer.
sys.path.insert(0, str(VC_DIR))
from vc_issuer import CredentialIssuer          # noqa: E402
from vc_verifier import CredentialVerifier      # noqa: E402

# Fixed experimental design (do not fit to the data).
N_VALUES = [1, 2, 4, 8, 16, 32]
SD_N = 16
K_VALUES = [1, 2, 4, 8, 16]
SIG_CHECK_TARGET_MS = 10.0

# A subject DID that carries a syntactically valid Ethereum address so the
# verifier's DID<->address binding check exercises the real recovery path.
SUBJECT_DID = "did:ethr:0x1:0x1111111111111111111111111111111111111111"


def make_claims(n):
    """n comparably sized string claims (richer credential => larger payload)."""
    return {
        f"claim_{i:03d}": f"val_{i:03d}_" + ("a1b2c3d4" * 3)  # 24-char tail
        for i in range(n)
    }


def median_ms(fn, runs, warmup):
    """Warm up, then time `fn` `runs` times; return (median_ms, p95_ms, mean_ms)."""
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000.0)
    samples.sort()
    n = len(samples)
    p95 = samples[min(n - 1, int(np.ceil(0.95 * n)) - 1)]
    return (round(statistics.median(samples), 5),
            round(p95, 5),
            round(statistics.fmean(samples), 5))


def linear_fit(xs, ys):
    """Least-squares slope/intercept + R^2 of ys ~ a + b*x."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    b, a = np.polyfit(x, y, 1)          # slope, intercept
    yhat = a + b * x
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return round(float(b), 6), round(float(a), 6), round(r2, 4)


def scaling_verdict(xs, ys):
    """Characterise the scaling order from the fit and the spread."""
    slope, intercept, r2 = linear_fit(xs, ys)
    lo, hi = min(ys), max(ys)
    spread_ratio = hi / lo if lo > 0 else float("inf")
    # Marginal cost per unit relative to the baseline (intercept-dominated).
    rel_slope = slope / intercept if intercept else float("inf")
    if spread_ratio < 1.25 and abs(rel_slope) < 0.02:
        order = "O(1) — effectively constant (ECDSA recovery dominates)"
    elif r2 >= 0.9 and slope > 0:
        order = "O(N) — linear marginal growth"
    else:
        order = "sub-linear / weakly N-dependent"
    return {
        "slope_ms_per_unit": slope,
        "intercept_ms": intercept,
        "r2": r2,
        "spread_ratio_max_over_min": round(spread_ratio, 3),
        "relative_slope_per_unit": round(rel_slope, 5),
        "order": order,
    }


def run_credential_richness(runs, warmup):
    issuer = CredentialIssuer.with_ethr_did(chain_id="0x1")
    verifier = CredentialVerifier(revocation_registry=issuer.revocation_registry)

    ns, medians, p95s, means = [], [], [], []
    for n in N_VALUES:
        env = issuer.issue_credential(
            credential_type="ScalingTestCredential",
            subject_did=SUBJECT_DID,
            claims=make_claims(n),
            validity_days=365,
            enforce_schema=False,          # unregistered test type: sign is real
        )
        vc = env["verifiableCredential"]
        # Sanity: the credential must actually verify (real crypto path).
        assert verifier.verify_credential(vc).valid, f"N={n} did not verify"
        med, p95, mean = median_ms(lambda: verifier.verify_credential(vc),
                                   runs, warmup)
        ns.append(n)
        medians.append(med)
        p95s.append(p95)
        means.append(mean)
        print(f"  N={n:2d}  median={med:.4f} ms  p95={p95:.4f} ms")

    verdict = scaling_verdict(ns, medians)
    under_target = all(m < SIG_CHECK_TARGET_MS for m in p95s)
    return {
        "N": ns,
        "median_ms": medians,
        "p95_ms": p95s,
        "mean_ms": means,
        "runs_per_point": runs,
        "warmup_per_point": warmup,
        "sig_check_target_ms": SIG_CHECK_TARGET_MS,
        "stays_under_target_across_range": under_target,
        "scaling": verdict,
    }


def run_selective_disclosure(runs, warmup):
    issuer = CredentialIssuer.with_ethr_did(chain_id="0x1")
    verifier = CredentialVerifier(revocation_registry=issuer.revocation_registry)

    env = issuer.issue_credential(
        credential_type="ScalingTestCredential",
        subject_did=SUBJECT_DID,
        claims=make_claims(SD_N),
        validity_days=365,
        selective_disclosure=True,
        enforce_schema=False,
    )
    vc = env["verifiableCredential"]
    disclosures = env["disclosures"]
    names = list(disclosures.keys())

    ks, medians, p95s, means = [], [], [], []
    for k in K_VALUES:
        vc_k = dict(vc)
        vc_k["disclosedClaims"] = {nm: disclosures[nm] for nm in names[:k]}
        assert verifier.verify_credential(vc_k).valid, f"k={k} did not verify"
        med, p95, mean = median_ms(lambda: verifier.verify_credential(vc_k),
                                   runs, warmup)
        ks.append(k)
        medians.append(med)
        p95s.append(p95)
        means.append(mean)
        print(f"  k={k:2d}/{SD_N}  median={med:.4f} ms  p95={p95:.4f} ms")

    verdict = scaling_verdict(ks, medians)
    return {
        "N": SD_N,
        "k": ks,
        "median_ms": medians,
        "p95_ms": p95s,
        "mean_ms": means,
        "runs_per_point": runs,
        "warmup_per_point": warmup,
        "scaling": verdict,
    }


def host_note():
    return (
        f"{platform.system()} {platform.release()} | "
        f"{platform.machine()} | "
        f"python {platform.python_version()} | "
        f"processor={platform.processor() or 'n/a'}"
    )


def main():
    ap = argparse.ArgumentParser(description="Experiment C: verification "
                                             "latency vs credential richness")
    ap.add_argument("--runs", type=int, default=300,
                    help="timed warm runs per point (>=200; default 300)")
    ap.add_argument("--warmup", type=int, default=50,
                    help="untimed warmup runs per point (default 50)")
    args = ap.parse_args()

    print("Experiment C — verification latency vs credential richness")
    print(f"  VC layer: {VC_DIR}")
    print(f"  {args.runs} timed runs/point, {args.warmup} warmup/point\n")

    print("[1/2] credential richness sweep (N claims):")
    richness = run_credential_richness(args.runs, args.warmup)
    print(f"  -> scaling order: {richness['scaling']['order']}")
    print(f"  -> p95 stays < {SIG_CHECK_TARGET_MS} ms across range: "
          f"{richness['stays_under_target_across_range']}\n")

    print(f"[2/2] selective disclosure sweep (N={SD_N}, disclose k):")
    sd = run_selective_disclosure(args.runs, args.warmup)
    print(f"  -> scaling order: {sd['scaling']['order']}\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    # Preserve any v2v_density block already appended by the Experiment D driver.
    existing = {}
    if OUT_JSON.exists():
        try:
            existing = json.loads(OUT_JSON.read_text())
        except Exception:
            existing = {}

    out = dict(existing)
    out["credential_richness"] = richness
    out["selective_disclosure"] = sd
    out["method"] = (
        "Real W3C VC DM 2.0 verification via the canonical VC layer "
        "(2_w3c-ssi-layer/verifiable-credentials: secp256k1 EIP-191 sign + "
        "public-key recovery, verify_credential runs structure/schema/temporal/"
        "revocation/signature/disclosure checks). For each point we warm up "
        f"{args.warmup} runs then take the MEDIAN over {args.runs} warm runs "
        "(p95 is the warm tail), timed with time.perf_counter. Credential "
        "richness varies N claims in {1,2,4,8,16,32}; selective disclosure fixes "
        "N=16 salted claim digests and discloses k in {1,2,4,8,16}. Scaling "
        "order is a least-squares fit of median latency vs N (and vs k)."
    )
    out["host_note"] = host_note()
    out["repeatability_caveat"] = (
        "Single host, crypto-only, warm uncontended core (thesis §5.4 / "
        "RESEARCH_AUDIT §4.5 repeatability framing). Absolute latencies are "
        "hardware-dependent; the transferable results are the median and the "
        "scaling ORDER, not a population confidence interval."
    )

    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
