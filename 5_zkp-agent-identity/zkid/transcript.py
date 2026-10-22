"""Fiat–Shamir transcripts.

An interactive sigma protocol becomes non-interactive when the verifier's random challenge is replaced by a hash of
everything the verifier would have seen. The hash must cover the statement, every commitment, the protocol name and
the context (who is asking, a fresh nonce); leaving any of them out is the classic "weak Fiat–Shamir" mistake, which
lets a proof be replayed or re-targeted. Every proof in `zkid` takes its challenge from a `Transcript`.
"""
from __future__ import annotations

import hashlib

from .ec import N, Point


class Transcript:
    def __init__(self, protocol: str, context: bytes = b""):
        self._h = hashlib.sha256()
        self._absorb(b"proto", protocol.encode())
        self._absorb(b"ctx", context)

    def _absorb(self, label: bytes, data: bytes) -> None:
        self._h.update(len(label).to_bytes(2, "big") + label + len(data).to_bytes(4, "big") + data)

    def point(self, label: str, p: Point) -> "Transcript":
        self._absorb(label.encode(), p.encode())
        return self

    def scalar(self, label: str, k: int) -> "Transcript":
        self._absorb(label.encode(), (k % N).to_bytes(32, "big"))
        return self

    def bytes(self, label: str, b: bytes) -> "Transcript":
        self._absorb(label.encode(), b)
        return self

    def challenge(self, label: str = "challenge") -> int:
        h = self._h.copy()
        h.update(b"\xff" + label.encode())
        e = int.from_bytes(h.digest(), "big") % N
        # Bind the challenge into the running state so a second challenge differs.
        self._absorb(b"chal", e.to_bytes(32, "big"))
        return e
