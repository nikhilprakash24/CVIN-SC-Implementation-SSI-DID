"""Scoped nullifiers: a value that is the same every time one secret is used in one scope, and unlinkable across
scopes.

A verifier (an RSU, a toll operator, an insurer) gets one nullifier per vehicle per scope. It can refuse a second use
in its scope (no double claim, no replay) but cannot match the vehicle with another scope's nullifier. Two forms:

* hash form   nf = SHA-256(domain || secret || scope), used by the Groth16 ZK-VIN circuit (with Poseidon there);
* key form    nf = x * H_scope with H_scope = hash_to_curve(scope), and a Chaum–Pedersen proof that nf uses the same
              x as a public key; a verifiable, deterministic pseudonym for holders who already show a key.
"""
from __future__ import annotations

from .ec import G, Point, hash_to_curve, scalar_mult
from .hashing import sha256
from .sigma import DleqProof, dleq_prove, dleq_verify


def hash_nullifier(secret: bytes, scope: bytes) -> bytes:
    return sha256(b"zkid/nullifier/v1|" + len(secret).to_bytes(2, "big") + secret + scope)


def scope_point(scope: bytes) -> Point:
    return hash_to_curve(b"zkid/scope/v1|" + scope)


def key_nullifier(x: int, scope: bytes, context: bytes = b"", rng=None) -> tuple[Point, DleqProof]:
    Hs = scope_point(scope)
    return scalar_mult(x, Hs), dleq_prove(x, G, Hs, context, rng)


def key_nullifier_verify(P: Point, scope: bytes, nf: Point, proof: DleqProof, context: bytes = b"") -> bool:
    return dleq_verify(G, P, scope_point(scope), nf, proof, context)
