"""Merkle trees (Merkle 1979/1987) with domain-separated leaves and nodes.

Leaves are hashed as H(0x00 || data) and inner nodes as H(0x01 || left || right) so that an inner node can never be
passed off as a leaf (the second-preimage trick against naive trees). An odd node is promoted unchanged. An inclusion
proof is the list of sibling hashes from leaf to root with their side; it has ceil(log2 n) entries.
"""
from __future__ import annotations

from .hashing import sha256


def leaf_hash(data: bytes, fn=sha256) -> bytes:
    return fn(b"\x00" + data)


def node_hash(left: bytes, right: bytes, fn=sha256) -> bytes:
    return fn(b"\x01" + left + right)


class MerkleTree:
    def __init__(self, leaves: list[bytes], fn=sha256):
        if not leaves:
            raise ValueError("a Merkle tree needs at least one leaf")
        self.fn = fn
        self.levels = [[leaf_hash(x, fn) for x in leaves]]
        while len(self.levels[-1]) > 1:
            cur = self.levels[-1]
            nxt = []
            for i in range(0, len(cur), 2):
                nxt.append(node_hash(cur[i], cur[i + 1], fn) if i + 1 < len(cur) else cur[i])
            self.levels.append(nxt)

    @property
    def root(self) -> bytes:
        return self.levels[-1][0]

    def prove(self, index: int) -> list[tuple[str, bytes]]:
        path = []
        for level in self.levels[:-1]:
            sib = index ^ 1
            if sib < len(level):
                path.append(("L" if sib < index else "R", level[sib]))
            index //= 2
        return path


def verify_inclusion(data: bytes, path: list[tuple[str, bytes]], root: bytes, fn=sha256) -> bool:
    h = leaf_hash(data, fn)
    for side, sib in path:
        h = node_hash(sib, h, fn) if side == "L" else node_hash(h, sib, fn)
    return h == root
