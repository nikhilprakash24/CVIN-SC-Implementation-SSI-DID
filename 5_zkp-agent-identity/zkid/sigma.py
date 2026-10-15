"""Sigma protocols on secp256k1, interactive and non-interactive (Fiat–Shamir).

A sigma protocol has three moves: the prover commits (a random point), the verifier challenges (a random scalar),
the prover responds (a scalar). It has three properties, each made executable in the tests:

* completeness   an honest prover with the witness always convinces the verifier;
* special soundness   two accepting transcripts with the same commitment and different challenges yield the witness
                      (`extract_*`), so a prover who can answer more than one challenge must know it;
* honest-verifier zero knowledge   accepting transcripts can be produced without the witness by choosing the
                      response first (`simulate_*`), so a transcript by itself teaches the verifier nothing.

Protocols here: Schnorr (Schnorr 1989) proof of knowledge of a discrete logarithm; Okamoto-style proof of knowledge
of a Pedersen opening; Chaum–Pedersen (1992) equality of discrete logarithms; Cramer–Damgård–Schoenmakers (1994)
OR proofs, used for bits; bit-decomposition range proofs; threshold proofs (v >= t) built on them.
Every non-interactive proof binds a `context` (verifier identity, nonce, scope) into its challenge.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field

from .ec import G, H, INFINITY, N, Point, scalar_mult
from .transcript import Transcript


def rand_scalar(rng=None) -> int:
    if rng is not None:
        return rng.randrange(1, N)
    return secrets.randbelow(N - 1) + 1


POINT_BYTES = 33
SCALAR_BYTES = 32

# --------------------------------------------------------------------------------------------- Schnorr


@dataclass
class SchnorrProof:
    R: Point
    s: int

    def size_bytes(self) -> int:
        return POINT_BYTES + SCALAR_BYTES

    def to_hex(self) -> dict:
        return {"R": self.R.hex(), "s": f"{self.s:064x}"}


class SchnorrProver:
    """The interactive prover, move by move."""

    def __init__(self, x: int):
        self.x = x % N
        self.P = scalar_mult(self.x, G)
        self._k = None

    def commit(self, rng=None) -> Point:
        self._k = rand_scalar(rng)
        return scalar_mult(self._k, G)

    def respond(self, e: int) -> int:
        if self._k is None:
            raise RuntimeError("commit first")
        s = (self._k + e * self.x) % N
        self._k = None  # a nonce is used once; reuse leaks the key (see extract_schnorr)
        return s


def schnorr_check(P: Point, R: Point, e: int, s: int) -> bool:
    return scalar_mult(s, G) == R + scalar_mult(e, P)


def _schnorr_challenge(P: Point, R: Point, context: bytes) -> int:
    return Transcript("zkid/schnorr/v1", context).point("P", P).point("R", R).challenge()


def schnorr_prove(x: int, context: bytes = b"", rng=None) -> SchnorrProof:
    prover = SchnorrProver(x)
    R = prover.commit(rng)
    e = _schnorr_challenge(prover.P, R, context)
    return SchnorrProof(R, prover.respond(e))


def schnorr_verify(P: Point, proof: SchnorrProof, context: bytes = b"") -> bool:
    if not P.on_curve() or P.is_infinity or not proof.R.on_curve() or not 0 < proof.s < N:
        return False
    e = _schnorr_challenge(P, proof.R, context)
    return schnorr_check(P, proof.R, e, proof.s)


def extract_schnorr(e1: int, s1: int, e2: int, s2: int) -> int:
    """Special soundness: from (R, e1, s1) and (R, e2, s2) with e1 != e2, x = (s1 - s2) / (e1 - e2)."""
    return ((s1 - s2) * pow((e1 - e2) % N, -1, N)) % N


def simulate_schnorr(P: Point, rng=None) -> tuple[Point, int, int]:
    """Honest-verifier zero knowledge: pick e and s, then R = sG - eP. No witness used."""
    e, s = rand_scalar(rng), rand_scalar(rng)
    return scalar_mult(s, G) - scalar_mult(e, P), e, s


# --------------------------------------------------------------------------------------------- Pedersen


def pedersen_commit(v: int, r: int) -> Point:
    """C = vG + rH: perfectly hiding (any C opens to any v under some r), computationally binding (opening to two
    values reveals log_G H, which nobody knows because H came from hash_to_curve)."""
    return scalar_mult(v % N, G) + scalar_mult(r % N, H)


@dataclass
class OpeningProof:
    A: Point
    z1: int
    z2: int

    def size_bytes(self) -> int:
        return POINT_BYTES + 2 * SCALAR_BYTES


def opening_prove(v: int, r: int, C: Point, context: bytes = b"", rng=None) -> OpeningProof:
    a, b = rand_scalar(rng), rand_scalar(rng)
    A = pedersen_commit(a, b)
    e = Transcript("zkid/pedersen-opening/v1", context).point("C", C).point("A", A).challenge()
    return OpeningProof(A, (a + e * v) % N, (b + e * r) % N)


def opening_verify(C: Point, proof: OpeningProof, context: bytes = b"") -> bool:
    e = Transcript("zkid/pedersen-opening/v1", context).point("C", C).point("A", proof.A).challenge()
    return pedersen_commit(proof.z1, proof.z2) == proof.A + scalar_mult(e, C)


# --------------------------------------------------------------------------------------------- Chaum–Pedersen


@dataclass
class DleqProof:
    A1: Point
    A2: Point
    s: int

    def size_bytes(self) -> int:
        return 2 * POINT_BYTES + SCALAR_BYTES


def dleq_prove(x: int, G1: Point, G2: Point, context: bytes = b"", rng=None) -> DleqProof:
    """Prove log_G1(P1) == log_G2(P2) == x without revealing x."""
    P1, P2 = scalar_mult(x, G1), scalar_mult(x, G2)
    k = rand_scalar(rng)
    A1, A2 = scalar_mult(k, G1), scalar_mult(k, G2)
    e = (Transcript("zkid/dleq/v1", context).point("G1", G1).point("G2", G2).point("P1", P1).point("P2", P2)
         .point("A1", A1).point("A2", A2).challenge())
    return DleqProof(A1, A2, (k + e * x) % N)


def dleq_verify(G1: Point, P1: Point, G2: Point, P2: Point, proof: DleqProof, context: bytes = b"") -> bool:
    e = (Transcript("zkid/dleq/v1", context).point("G1", G1).point("G2", G2).point("P1", P1).point("P2", P2)
         .point("A1", proof.A1).point("A2", proof.A2).challenge())
    return (scalar_mult(proof.s, G1) == proof.A1 + scalar_mult(e, P1)
            and scalar_mult(proof.s, G2) == proof.A2 + scalar_mult(e, P2))


# --------------------------------------------------------------------------------------------- CDS OR proof (bits)


@dataclass
class BitProof:
    """C commits to 0 or to 1: knowledge of r with C = rH, or with C - G = rH (Cramer–Damgård–Schoenmakers)."""

    A0: Point
    A1: Point
    e0: int
    e1: int
    z0: int
    z1: int

    def size_bytes(self) -> int:
        return 2 * POINT_BYTES + 4 * SCALAR_BYTES


def _bit_challenge(C: Point, A0: Point, A1: Point, context: bytes) -> int:
    return Transcript("zkid/bit-or/v1", context).point("C", C).point("A0", A0).point("A1", A1).challenge()


def bit_prove(b: int, r: int, C: Point, context: bytes = b"", rng=None) -> BitProof:
    if b not in (0, 1):
        raise ValueError("bit must be 0 or 1")
    Y = [C, C - G]  # the statement for branch 0 and for branch 1, each "= r * H"
    k = rand_scalar(rng)
    ef, zf = rand_scalar(rng), rand_scalar(rng)
    fake = 1 - b
    A = [None, None]
    A[b] = scalar_mult(k, H)
    A[fake] = scalar_mult(zf, H) - scalar_mult(ef, Y[fake])  # simulated branch
    e = _bit_challenge(C, A[0], A[1], context)
    eb = (e - ef) % N
    zb = (k + eb * r) % N
    es, zs = [0, 0], [0, 0]
    es[b], zs[b] = eb, zb
    es[fake], zs[fake] = ef, zf
    return BitProof(A[0], A[1], es[0], es[1], zs[0], zs[1])


def bit_verify(C: Point, p: BitProof, context: bytes = b"") -> bool:
    e = _bit_challenge(C, p.A0, p.A1, context)
    if (p.e0 + p.e1) % N != e:
        return False
    return (scalar_mult(p.z0, H) == p.A0 + scalar_mult(p.e0, C)
            and scalar_mult(p.z1, H) == p.A1 + scalar_mult(p.e1, C - G))


# --------------------------------------------------------------------------------------------- range and threshold


@dataclass
class RangeProof:
    """v in [0, 2^n): commitments to the n bits, each with a bit proof; the verifier checks sum 2^i C_i == C."""

    bit_commitments: list[Point]
    bit_proofs: list[BitProof] = field(default_factory=list)

    def size_bytes(self) -> int:
        return len(self.bit_commitments) * POINT_BYTES + sum(p.size_bytes() for p in self.bit_proofs)

    def to_hex(self) -> dict:
        return {"C_bits": [c.hex() for c in self.bit_commitments],
                "bit_proofs": [{k: (getattr(p, k).hex() if isinstance(getattr(p, k), Point) else f"{getattr(p, k):064x}")
                                for k in ("A0", "A1", "e0", "e1", "z0", "z1")} for p in self.bit_proofs]}


def range_prove(v: int, r: int, C: Point, n: int, context: bytes = b"", rng=None) -> RangeProof:
    if not 0 <= v < (1 << n):
        raise ValueError("value out of range; no honest proof exists")
    bits = [(v >> i) & 1 for i in range(n)]
    rs = [rand_scalar(rng) for _ in range(n - 1)]
    partial = sum((1 << i) * rs[i] for i in range(n - 1)) % N
    rs.append(((r - partial) * pow(1 << (n - 1), -1, N)) % N)
    Cs = [pedersen_commit(bits[i], rs[i]) for i in range(n)]
    ctx = context + C.encode()
    proofs = [bit_prove(bits[i], rs[i], Cs[i], ctx + i.to_bytes(2, "big"), rng) for i in range(n)]
    return RangeProof(Cs, proofs)


def range_verify(C: Point, proof: RangeProof, n: int, context: bytes = b"") -> bool:
    if len(proof.bit_commitments) != n or len(proof.bit_proofs) != n:
        return False
    acc = INFINITY
    for i, Ci in enumerate(proof.bit_commitments):
        acc = acc + scalar_mult(1 << i, Ci)
    if acc != C:
        return False
    ctx = context + C.encode()
    return all(bit_verify(proof.bit_commitments[i], proof.bit_proofs[i], ctx + i.to_bytes(2, "big"))
               for i in range(n))


def threshold_prove(v: int, r: int, C: Point, t: int, n: int, context: bytes = b"", rng=None) -> RangeProof:
    """Prove v >= t (and v - t < 2^n) for C = vG + rH, revealing nothing else about v: a range proof on C - tG."""
    return range_prove(v - t, r, C - scalar_mult(t, G), n, context + b"|ge|" + t.to_bytes(8, "big"), rng)


def threshold_verify(C: Point, t: int, proof: RangeProof, n: int, context: bytes = b"") -> bool:
    return range_verify(C - scalar_mult(t, G), proof, n, context + b"|ge|" + t.to_bytes(8, "big"))
