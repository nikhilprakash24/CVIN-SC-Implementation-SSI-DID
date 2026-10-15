"""Hash functions used by the project: SHA-256 (FIPS 180-4) and Keccak-256 (the Ethereum variant of FIPS 202).

Python's hashlib has SHA-256 and SHA3-256, but Ethereum's Keccak-256 uses the original Keccak padding (0x01), not
SHA-3's (0x06), so the two differ. Keccak-f[1600] is written out here in full so a reader can see every round; the
round count (24) and the per-round steps (theta, rho, pi, chi, iota) are what the manual-burden inventory counts.
"""
from __future__ import annotations

import hashlib

_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]
_ROT = [
    [0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14],
]
_MASK = (1 << 64) - 1
KECCAK_ROUNDS = 24


def _rol(v: int, n: int) -> int:
    return ((v << n) | (v >> (64 - n))) & _MASK if n else v


def _keccak_f(a):
    for rnd in range(KECCAK_ROUNDS):
        c = [a[x][0] ^ a[x][1] ^ a[x][2] ^ a[x][3] ^ a[x][4] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rol(c[(x + 1) % 5], 1) for x in range(5)]
        a = [[a[x][y] ^ d[x] for y in range(5)] for x in range(5)]
        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = _rol(a[x][y], _ROT[x][y])
        a = [[b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
        a[0][0] ^= _RC[rnd]
    return a


def keccak256(data: bytes) -> bytes:
    rate = 136
    msg = bytearray(data)
    msg.append(0x01)
    while len(msg) % rate:
        msg.append(0)
    msg[-1] |= 0x80
    state = [[0] * 5 for _ in range(5)]
    for off in range(0, len(msg), rate):
        block = msg[off:off + rate]
        for i in range(rate // 8):
            x, y = i % 5, i // 5
            state[x][y] ^= int.from_bytes(block[8 * i:8 * i + 8], "little")
        state = _keccak_f(state)
    out = b"".join(state[i % 5][i // 5].to_bytes(8, "little") for i in range(4))
    return out


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hash_commit(value: bytes, salt: bytes, fn=sha256) -> bytes:
    """A hash commitment: binding under collision resistance, hiding only if `salt` has enough entropy.

    Without a salt a low-entropy value (a VIN, a birth date) is recovered by enumeration; `bench/vin_bruteforce.py`
    measures how fast.
    """
    return fn(salt + value)
