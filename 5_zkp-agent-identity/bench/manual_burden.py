"""P2: what one zero-knowledge presentation would cost a person working by hand.

Two kinds of numbers, kept apart in the output:
* MEASURED (exact, from committed runs): operation counts from the zkid counters (results/sigma_bench.json), the
  ZK-VIN constraint and wire counts and the size of a real proof (results/zkvin_bench.json), character counts of the
  values a person would have to read and copy.
* ESTIMATED (status E): times and error probabilities obtained by pricing the measured counts at published human
  rates. Each rate is cited in docs/zkp/SOURCES_ZKP.md and chosen to be generous to the human.

Rates.
* SHA-256 by hand: one round in 16 min 45 s (Shirriff 2014, [SHIRRIFF-2014]). The FIPS 180-4 round function is about
  26 operations on 32-bit words (Sigma1 5, Ch 4, four additions for T1; Sigma0 5, Maj 5, one addition for T2; two
  final additions), so one 32-bit word operation takes about 38.7 s.
* A 256-bit modular multiplication priced at 200 word operations: 64 word products (each 32x32 product counted as ONE
  operation, which is very generous), about 100 additions with carries, and a reduction; about 2.1 hours.
* Transcription: 0.6 % residual error per character typed (Panko's compilation, [PANKO-ERR]); the chance of copying
  n characters with no error is (1 - 0.006)^n.
* Groth16 prover (no Pippenger, the textbook algorithm a person would follow): multi-scalar multiplications over the
  wires and the evaluation domain, about 384 point operations per 254-bit scalar, 12 field multiplications per G1 point
  operation and 36 per G2 point operation, plus seven FFTs of the domain size. Verifier: four pairings at about 15,000
  field multiplications each (order of magnitude for an optimal ate pairing on BN254). These are order-of-magnitude
  figures (E), stated as such.

    python3 bench/manual_burden.py   # needs results/sigma_bench.json and results/zkvin_bench.json
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from bench.runid import run_identity  # noqa: E402

RES = HERE.parent / "results"
SHA_ROUND_S = 16 * 60 + 45
WORD_OPS_PER_ROUND = 26
WORD_OP_S = SHA_ROUND_S / WORD_OPS_PER_ROUND
WORD_OPS_PER_FIELD_MUL = 200
FIELD_MUL_S = WORD_OPS_PER_FIELD_MUL * WORD_OP_S
CHAR_ERROR = 0.006
WORK_HOURS_PER_YEAR = 2000


def human(seconds: float) -> dict:
    h = seconds / 3600
    return {"hours": h, "working_days_8h": h / 8, "working_years_2000h": h / WORK_HOURS_PER_YEAR}


def main():
    sb = json.loads((RES / "sigma_bench.json").read_text())
    zb = json.loads((RES / "zkvin_bench.json").read_text())
    oc = sb["operation_counts"]
    wires = int(zb["circuit"]["wires"])
    constraints = int(zb["circuit"]["non-linear constraints"]) + int(zb["circuit"]["linear constraints"])
    domain = 1 << math.ceil(math.log2(constraints))
    g1_scalars = 3 * wires + domain
    g2_scalars = wires
    groth_prove_fmul = g1_scalars * 384 * 12 + g2_scalars * 384 * 36 + 7 * domain * int(math.log2(domain)) // 2
    groth_verify_fmul = 4 * 15000
    proof_chars = len(json.dumps(zb["sample_proof"]))
    signal_chars = len(json.dumps(zb["sample_public_signals"]))
    copy = {
        "owner private key (hex)": 64, "agent private key (hex)": 64, "commitment salt (field element, decimal)": 77,
        "Ethereum address (hex)": 40, "ZK-VIN Groth16 proof (JSON as produced)": proof_chars,
        "ZK-VIN public signals (decimal)": signal_chars,
        "6-bit threshold proof (sigma protocol, hex)": sb["hex_chars"]["threshold_proof_6bit"],
    }
    tasks = {
        "Schnorr verification (one signature-sized proof)": oc["schnorr_verify"]["field_mul"],
        "6-bit threshold proof, prove (model year >= t)": oc["threshold_prove_6bit"]["field_mul"],
        "6-bit threshold proof, verify": oc["threshold_verify_6bit"]["field_mul"],
        "ZK-VIN Groth16 proof, prove (E: textbook algorithm)": groth_prove_fmul,
        "ZK-VIN Groth16 proof, verify (E: four pairings)": groth_verify_fmul,
    }
    out = {
        "condition": "MEASURED counts (exact) priced at cited human rates (status E)",
        "run": run_identity(),
        "rates_E": {"sha256_round_s": SHA_ROUND_S, "word_op_s": WORD_OP_S, "field_mul_s": FIELD_MUL_S,
                    "char_error": CHAR_ERROR, "sources": ["SHIRRIFF-2014", "PANKO-ERR", "FIPS-180-4"]},
        "measured": {"zkvin_wires": wires, "zkvin_constraints": constraints, "groth16_domain": domain,
                     "field_mul_counts": {k: v for k, v in tasks.items() if "(E" not in k},
                     "characters_to_copy": copy},
        "estimated_E": {
            "field_mul_counts_E": {k: v for k, v in tasks.items() if "(E" in k},
            "time_by_hand": {k: human(v * FIELD_MUL_S) for k, v in tasks.items()},
            "sha256_one_compression_by_hand": human(64 * SHA_ROUND_S),
            "p_copy_without_error": {k: (1 - CHAR_ERROR) ** n for k, n in copy.items()},
            "p_one_presentation_copied_without_error": (1 - CHAR_ERROR) ** (proof_chars + signal_chars + 77 + 64),
        },
        "agent_measured_M0": {"threshold_prove_ms": sb["timing"]["threshold_prove_6bit"]["median_ms"],
                              "threshold_verify_ms": sb["timing"]["threshold_verify_6bit"]["median_ms"],
                              "groth16_prove_ms": zb["prove_ms"]["median"], "groth16_verify_ms": zb["verify_ms"]["median"]},
    }
    (RES / "manual_burden.json").write_text(json.dumps(out, indent=1) + "\n")
    for k, v in out["estimated_E"]["time_by_hand"].items():
        print(f"{k:55s} {v['hours']:>14,.1f} h  = {v['working_years_2000h']:>12,.2f} working years")
    for k, v in out["estimated_E"]["p_copy_without_error"].items():
        print(f"P(copy {k} without error) = {v:.3f}")
    print("P(one presentation copied without error) =", out["estimated_E"]["p_one_presentation_copied_without_error"])


if __name__ == "__main__":
    main()
