"""secp256k1 arithmetic in readable pure Python, with operation counters.

The curve is the one Ethereum and the project's DIDs use (y^2 = x^3 + 7 over F_p). The code favours clarity over
speed: Jacobian coordinates for scalar multiplication, affine points at the interface. It is not constant time and
must not hold production keys; it exists so that every step of a proof can be read, counted and tested.

Counters (`COUNTERS`) record field multiplications, field inversions, point additions and doublings. The
manual-burden inventory (`bench/manual_burden.py`) uses them to count what a person would have to do by hand.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
B = 7

COUNTERS = {"field_mul": 0, "field_inv": 0, "point_add": 0, "point_double": 0}


def reset_counters() -> None:
    for k in COUNTERS:
        COUNTERS[k] = 0


def _fmul(a: int, b: int) -> int:
    COUNTERS["field_mul"] += 1
    return (a * b) % P


def _finv(a: int) -> int:
    COUNTERS["field_inv"] += 1
    return pow(a, P - 2, P)


@dataclass(frozen=True)
class Point:
    """An affine point; `None` coordinates denote the point at infinity."""

    x: int | None
    y: int | None

    @property
    def is_infinity(self) -> bool:
        return self.x is None

    def on_curve(self) -> bool:
        if self.is_infinity:
            return True
        return (self.y * self.y - self.x * self.x * self.x - B) % P == 0

    def __add__(self, other: "Point") -> "Point":
        return _to_affine(_jadd(_to_jac(self), _to_jac(other)))

    def __neg__(self) -> "Point":
        return self if self.is_infinity else Point(self.x, (-self.y) % P)

    def __sub__(self, other: "Point") -> "Point":
        return self + (-other)

    def __rmul__(self, k: int) -> "Point":
        return scalar_mult(k, self)

    def encode(self) -> bytes:
        """SEC 1 compressed encoding (33 bytes); infinity encodes as a single zero byte."""
        if self.is_infinity:
            return b"\x00"
        return bytes([2 + (self.y & 1)]) + self.x.to_bytes(32, "big")

    def hex(self) -> str:
        return self.encode().hex()


INFINITY = Point(None, None)
G = Point(GX, GY)


def decode(data: bytes) -> Point:
    if data == b"\x00":
        return INFINITY
    if len(data) != 33 or data[0] not in (2, 3):
        raise ValueError("not a compressed secp256k1 point")
    x = int.from_bytes(data[1:], "big")
    if x >= P:
        raise ValueError("x out of range")
    y = _sqrt((pow(x, 3, P) + B) % P)
    if y is None:
        raise ValueError("x is not on the curve")
    if (y & 1) != (data[0] & 1):
        y = P - y
    return Point(x, y)


def _sqrt(a: int) -> int | None:
    # P = 3 mod 4, so a square root is a^((P+1)/4) when one exists.
    r = pow(a, (P + 1) // 4, P)
    return r if (r * r) % P == a % P else None


# Jacobian coordinates: (X, Y, Z) represents (X/Z^2, Y/Z^3); Z = 0 is infinity.
def _to_jac(p: Point):
    return (0, 1, 0) if p.is_infinity else (p.x, p.y, 1)


def _to_affine(j) -> Point:
    X, Y, Z = j
    if Z == 0:
        return INFINITY
    zi = _finv(Z)
    zi2 = _fmul(zi, zi)
    return Point(_fmul(X, zi2), _fmul(Y, _fmul(zi2, zi)))


def _jdouble(j):
    X, Y, Z = j
    if Z == 0 or Y == 0:
        return (0, 1, 0)
    COUNTERS["point_double"] += 1
    YY = _fmul(Y, Y)
    S = (4 * _fmul(X, YY)) % P
    M = (3 * _fmul(X, X)) % P  # a = 0 for secp256k1
    X3 = (_fmul(M, M) - 2 * S) % P
    Y3 = (_fmul(M, (S - X3) % P) - 8 * _fmul(YY, YY)) % P
    Z3 = (2 * _fmul(Y, Z)) % P
    return (X3, Y3, Z3)


def _jadd(p, q):
    X1, Y1, Z1 = p
    X2, Y2, Z2 = q
    if Z1 == 0:
        return q
    if Z2 == 0:
        return p
    Z1Z1 = _fmul(Z1, Z1)
    Z2Z2 = _fmul(Z2, Z2)
    U1 = _fmul(X1, Z2Z2)
    U2 = _fmul(X2, Z1Z1)
    S1 = _fmul(Y1, _fmul(Z2, Z2Z2))
    S2 = _fmul(Y2, _fmul(Z1, Z1Z1))
    if U1 == U2:
        if S1 != S2:
            return (0, 1, 0)
        return _jdouble(p)
    COUNTERS["point_add"] += 1
    H = (U2 - U1) % P
    R = (S2 - S1) % P
    HH = _fmul(H, H)
    HHH = _fmul(H, HH)
    V = _fmul(U1, HH)
    X3 = (_fmul(R, R) - HHH - 2 * V) % P
    Y3 = (_fmul(R, (V - X3) % P) - _fmul(S1, HHH)) % P
    Z3 = _fmul(H, _fmul(Z1, Z2))
    return (X3, Y3, Z3)


def scalar_mult(k: int, p: Point) -> Point:
    """Left-to-right double-and-add. Not constant time (research code)."""
    k %= N
    if k == 0 or p.is_infinity:
        return INFINITY
    acc = (0, 1, 0)
    base = _to_jac(p)
    for bit in bin(k)[2:]:
        acc = _jdouble(acc)
        if bit == "1":
            acc = _jadd(acc, base)
    return _to_affine(acc)


def multi_mult(pairs) -> Point:
    """Sum of k_i * P_i, computed term by term (clarity over speed)."""
    acc = INFINITY
    for k, p in pairs:
        acc = acc + scalar_mult(k, p)
    return acc


def hash_to_curve(tag: bytes) -> Point:
    """Nothing-up-my-sleeve point by try-and-increment: the first x = SHA-256(tag || counter) on the curve, even y.

    Nobody knows log_G of the result, which is what a Pedersen commitment's second generator requires.
    """
    ctr = 0
    while True:
        x = int.from_bytes(hashlib.sha256(tag + ctr.to_bytes(4, "big")).digest(), "big")
        if x < P:
            y = _sqrt((pow(x, 3, P) + B) % P)
            if y is not None:
                return Point(x, y if y % 2 == 0 else P - y)
        ctr += 1


H = hash_to_curve(b"CVIN-ZKID/pedersen/H/v1")


def scalar_from_bytes(b: bytes) -> int:
    return int.from_bytes(b, "big") % N
