"""Prover for SchnorrEcrecoverVerifier.sol: a Schnorr proof of key knowledge in the form the ecrecover trick checks.

    python3 -m zkid.schnorr_evm   # writes fixtures/schnorr_evm.json (seeded, CVIN_SEED)
"""
from __future__ import annotations

import json
import os
import pathlib
import random

from .ec import G, N, Point, scalar_mult
from .hashing import keccak256


def eth_address(p: Point) -> bytes:
    return keccak256(p.x.to_bytes(32, "big") + p.y.to_bytes(32, "big"))[12:]


def prove(x: int, message: bytes, rng=None) -> dict:
    rng = rng or random.SystemRandom()
    P = scalar_mult(x, G)
    while True:
        k = rng.randrange(1, N)
        R = scalar_mult(k, G)
        parity = P.y & 1
        e = int.from_bytes(keccak256(eth_address(R) + bytes([parity]) + P.x.to_bytes(32, "big") + message), "big")
        if e < N:
            break
    s = (k + e * x) % N
    return {"parity": parity, "px": "0x" + P.x.to_bytes(32, "big").hex(), "message": "0x" + message.hex(),
            "e": "0x" + e.to_bytes(32, "big").hex(), "s": "0x" + s.to_bytes(32, "big").hex()}


if __name__ == "__main__":
    rng = random.Random(int(os.environ.get("CVIN_SEED", "1")))
    x = rng.randrange(1, N)
    msg = keccak256(b"did:ethr:vehicle|rsu:42|nonce-0001")
    out = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "schnorr_evm.json"
    out.write_text(json.dumps({"note": "seeded fixture; regenerate with python3 -m zkid.schnorr_evm",
                               "proof": prove(x, msg, rng)}, indent=2) + "\n")
    print("wrote", out)
