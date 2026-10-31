"""A tamper-evident audit log: every request and decision, hash-chained, with a Merkle root that can be anchored on
chain (one 32-byte value per period), so the owner can later prove what the agent did and did not disclose.
"""
from __future__ import annotations

import hashlib
import json

from zkid.merkle import MerkleTree


class AuditLog:
    GENESIS = "0" * 64

    def __init__(self):
        self.entries: list[dict] = []

    def append(self, event: dict) -> str:
        prev = self.entries[-1]["hash"] if self.entries else self.GENESIS
        body = json.dumps(event, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256((prev + body).encode()).hexdigest()
        self.entries.append({"prev": prev, "event": event, "hash": h})
        return h

    def verify(self) -> bool:
        prev = self.GENESIS
        for e in self.entries:
            body = json.dumps(e["event"], sort_keys=True, separators=(",", ":"))
            if e["prev"] != prev or hashlib.sha256((prev + body).encode()).hexdigest() != e["hash"]:
                return False
            prev = e["hash"]
        return True

    def root(self) -> str:
        if not self.entries:
            return self.GENESIS
        return MerkleTree([bytes.fromhex(e["hash"]) for e in self.entries]).root.hex()
