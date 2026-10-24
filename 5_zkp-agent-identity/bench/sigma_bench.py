"""Timings and sizes of the zkid primitives, condition M0 (in-process Python, no chain), N=30 per operation after one
discarded warm-up. Also records operation counts (field multiplications, inversions, point additions and doublings)
per operation from the zkid counters; those counts are exact and feed bench/manual_burden.py.

    python3 bench/sigma_bench.py   # writes results/sigma_bench.json
"""
from __future__ import annotations

import json
import pathlib
import random
import statistics
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from bench.runid import run_identity  # noqa: E402
from zkid import ec, hashing, merkle, sigma  # noqa: E402
from zkid.ec import G, N, scalar_mult  # noqa: E402

N_RUNS = 30


def timed(fn, n=N_RUNS):
    fn()  # warm-up, discarded
    xs = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        fn()
        xs.append((time.perf_counter_ns() - t0) / 1e6)
    return {"n": n, "median_ms": statistics.median(xs), "min_ms": min(xs), "max_ms": max(xs)}


def counted(fn):
    ec.reset_counters()
    fn()
    return dict(ec.COUNTERS)


def main():
    rng = random.Random(1)
    x = rng.randrange(1, N)
    P = scalar_mult(x, G)
    v, r = 2022, rng.randrange(1, N)
    C = sigma.pedersen_commit(v, r)
    sp = sigma.schnorr_prove(x, b"ctx", rng)
    tp = sigma.threshold_prove(v, r, C, 2020, 6, b"ctx", rng)
    leaves = [f"WMI-{i}".encode() for i in range(16)]
    tree = merkle.MerkleTree(leaves)
    path = tree.prove(5)
    ops = {
        "schnorr_prove": lambda: sigma.schnorr_prove(x, b"ctx", rng),
        "schnorr_verify": lambda: sigma.schnorr_verify(P, sp, b"ctx"),
        "pedersen_commit": lambda: sigma.pedersen_commit(v, r),
        "threshold_prove_6bit": lambda: sigma.threshold_prove(v, r, C, 2020, 6, b"ctx", rng),
        "threshold_verify_6bit": lambda: sigma.threshold_verify(C, 2020, tp, 6, b"ctx"),
        "merkle_verify_16_leaves": lambda: merkle.verify_inclusion(leaves[5], path, tree.root),
        "keccak256_64B": lambda: hashing.keccak256(bytes(64)),
    }
    out = {
        "condition": "M0 (in-process CPython, pure-Python secp256k1; not constant time; one warm-up discarded)",
        "run": run_identity(),
        "timing": {k: timed(f) for k, f in ops.items()},
        "operation_counts": {k: counted(f) for k, f in ops.items() if not k.startswith(("merkle", "keccak"))},
        "sizes_bytes": {"schnorr_proof": sp.size_bytes(), "threshold_proof_6bit": tp.size_bytes(),
                        "pedersen_commitment": 33, "merkle_path_16_leaves": sum(len(h) for _, h in path)},
        "hex_chars": {"schnorr_proof": len(json.dumps(sp.to_hex())), "threshold_proof_6bit": len(json.dumps(tp.to_hex()))},
    }
    p = HERE.parent / "results" / "sigma_bench.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    for k, t in out["timing"].items():
        print(f"{k:26s} {t['median_ms']:9.3f} ms")
    print(out["sizes_bytes"], out["operation_counts"]["threshold_prove_6bit"])


if __name__ == "__main__":
    main()
