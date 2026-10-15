"""Why salts and zero knowledge exist: reversing an UNSALTED SHA-256 of a VIN by enumeration (Z-E7).

Scope, written before the first run. The attacker sees the parked car (make, model, trim, model year) or a sale
listing, so it knows the world manufacturer identifier, the vehicle descriptor section, the model-year character and
the plant character; it does not know the 6-digit serial. The check digit (position 9) follows from the rest
(ISO 3779 / 49 CFR 565 weights). The space is therefore 10^6 VINs. The script enumerates it in full against the hash
of a sample VIN, on one CPU core, and records the rate. A wider space (vehicle descriptor unknown too, 33^5 x 10^6)
is extrapolated from the measured rate and, separately, from a published GPU rate; both extrapolations are status E.

    python3 bench/vin_bruteforce.py   # writes results/vin_bruteforce.json
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from bench.runid import run_identity  # noqa: E402

TRANSLIT = {**{str(d): d for d in range(10)}, "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
            "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9, "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7,
            "Y": 8, "Z": 9}
WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
TARGET = "1HGCM82633A004352"  # a widely published sample VIN
GPU_SHA256_PER_S = 22.1e9  # hashcat mode 1400 on one RTX 4090 (SOURCES_ZKP.md [Hashcat4090]); not measured here


def check_digit(vin16_with_placeholder: str) -> str:
    s = sum(TRANSLIT[c] * w for c, w in zip(vin16_with_placeholder, WEIGHTS))
    r = s % 11
    return "X" if r == 10 else str(r)


def main():
    assert check_digit(TARGET[:8] + "0" + TARGET[9:]) == TARGET[8], "check-digit algorithm"
    target_hash = hashlib.sha256(TARGET.encode()).hexdigest()
    prefix, year_plant = TARGET[:8], TARGET[9:11]
    t0 = time.perf_counter()
    found, tried = None, 0
    for serial in range(10 ** 6):
        body = f"{prefix}0{year_plant}{serial:06d}"
        vin = body[:8] + check_digit(body) + body[9:]
        tried += 1
        if hashlib.sha256(vin.encode()).hexdigest() == target_hash and found is None:
            found = vin
    elapsed = time.perf_counter() - t0
    rate = tried / elapsed
    wide = 33 ** 5 * 10 ** 6
    out = {
        "condition": "M0, one CPU core, CPython hashlib; the full 10^6 space enumerated (not stopped at the hit)",
        "run": run_identity(),
        "scope": "WMI, VDS, model-year and plant characters known; 6-digit serial unknown; check digit derived",
        "space": tried, "found": found == TARGET, "elapsed_s": elapsed, "rate_per_s": rate,
        "expectations": {"Z-E7 measured rate x space < 3600 s": "PASS" if tried / rate < 3600 else "FAIL"},
        "extrapolation_E": {
            "wide_space_vds_unknown": wide,
            "this_host_one_core_days": wide / rate / 86400,
            "one_gpu_hours_at_published_rate": wide / GPU_SHA256_PER_S / 3600,
            "note": "status E: derived from the measured rate or a published GPU rate; not run",
        },
        "salted_note": "with a 128-bit random salt the same enumeration needs 2^128 times as many guesses",
    }
    p = HERE.parent / "results" / "vin_bruteforce.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(f"found={out['found']} in {elapsed:.2f} s at {rate:,.0f} hashes/s; {out['expectations']}")
    print(out["extrapolation_E"])


if __name__ == "__main__":
    main()
