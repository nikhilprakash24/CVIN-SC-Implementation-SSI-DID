"""
A database lifecycle backend (Phase 2, focus F2, start of execution; docs/phase2/focus/F2_chains_and_databases/).

The third point between the two Phase 1 lifecycle backends (cv2x-testbed/identity/lifecycle_backends.py):
the in-memory centralized registry (no persistence, no audit) and MOBI-VID-V2 on chain (persistence,
public verifiability, consensus). This one is a conventional database with one ledger-like property
added, so that F2 can separate what a chain contributes from what a careful database already gives:

  * persistent, transactional storage (SQLite, stdlib; a file or :memory:);
  * an **append-only journal**: every write is one row; UPDATE and DELETE on the journal are refused by
    triggers;
  * **hash chaining**: each journal row stores sha256(previous hash || canonical JSON of the entry), so
    `verify_journal()` detects any edit, deletion or reordering made by someone who bypassed the
    triggers (for example the database's own administrator editing the file);
  * the same interface as the Phase 1 backends: birth, lifecycle_event, transfer, history,
    current_owner, with `name` and `is_chain`.

What it does NOT give, by construction, and what F2 measures against the chain: no third party can
verify the journal without the operator's cooperation (the head hash is not published anywhere); the
operator can rewrite the whole chain of hashes; there is no consensus and no availability beyond the
operator. Anchoring the journal head on a chain (a hybrid) is the planned next step (F2 plan, step 3).

Not a result producer yet: nothing here is timed. The parity tests are in
phase2/backends/test_sqlite_lifecycle.py.
"""
import hashlib
import json
import sqlite3
from typing import Any, Dict, List, Optional

GENESIS = "0" * 64

SCHEMA = """
CREATE TABLE vehicles (handle TEXT PRIMARY KEY, vin_hash TEXT NOT NULL, birth TEXT NOT NULL, owner TEXT NOT NULL);
CREATE TABLE journal (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    handle TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL,
    prev_hash TEXT NOT NULL, entry_hash TEXT NOT NULL UNIQUE);
CREATE TRIGGER journal_no_update BEFORE UPDATE ON journal BEGIN SELECT RAISE(ABORT, 'journal is append-only'); END;
CREATE TRIGGER journal_no_delete BEFORE DELETE ON journal BEGIN SELECT RAISE(ABORT, 'journal is append-only'); END;
"""


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def link(prev_hash: str, handle: str, kind: str, body: str) -> str:
    return hashlib.sha256((prev_hash + "|" + handle + "|" + kind + "|" + body).encode()).hexdigest()


class SQLiteLifecycleBackend:
    name = "sqlite_journal"
    is_chain = False

    def __init__(self, path: str = ":memory:", salt: bytes = b"phase2-f2"):
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)
        self.salt = salt
        self.owners = ["OWNER-A", "OWNER-B"]
        self.last_receipt = None
        self._n = 0

    # ------------------------------------------------------------------ writes
    def _append(self, handle: str, kind: str, body: Dict[str, Any]) -> str:
        row = self.db.execute("SELECT entry_hash FROM journal ORDER BY seq DESC LIMIT 1").fetchone()
        prev = row[0] if row else GENESIS
        text = canonical(body)
        h = link(prev, handle, kind, text)
        self.db.execute("INSERT INTO journal (handle, kind, body, prev_hash, entry_hash) VALUES (?, ?, ?, ?, ?)",
                        (handle, kind, text, prev, h))
        return h

    def birth(self, vin: str, first_owner_index: int = 0) -> str:
        self._n += 1
        handle = f"vehicle_sql_{self._n}"
        vin_hash = hashlib.sha256(self.salt + vin.encode()).hexdigest()   # the VIN itself is not stored
        owner = self.owners[first_owner_index]
        birth = {"vin_hash": vin_hash, "first_owner": owner}
        with self.db:
            self.db.execute("INSERT INTO vehicles VALUES (?, ?, ?, ?)", (handle, vin_hash, canonical(birth), owner))
            self._append(handle, "birth", birth)
        return handle

    def lifecycle_event(self, handle: str, odometer: int, data: Dict[str, Any]):
        last = self._last_odometer(handle)
        if last is not None and odometer < last:
            raise ValueError(f"odometer rollback: {odometer} < {last}")
        with self.db:
            return self._append(handle, "event", {"odometer": odometer, "data": data})

    def transfer(self, handle: str, odometer: int):
        current = self.current_owner(handle)
        new = self.owners[1] if current == self.owners[0] else self.owners[0]
        with self.db:
            self.db.execute("UPDATE vehicles SET owner = ? WHERE handle = ?", (new, handle))
            return self._append(handle, "transfer", {"from": current, "to": new, "odometer": odometer})

    # ------------------------------------------------------------------ reads
    def _last_odometer(self, handle: str) -> Optional[int]:
        rows = self.db.execute("SELECT body FROM journal WHERE handle = ? AND kind IN ('event', 'transfer') "
                               "ORDER BY seq DESC LIMIT 1", (handle,)).fetchall()
        return json.loads(rows[0][0])["odometer"] if rows else None

    def current_owner(self, handle: str) -> str:
        row = self.db.execute("SELECT owner FROM vehicles WHERE handle = ?", (handle,)).fetchone()
        if row is None:
            raise KeyError(handle)
        return row[0]

    def history(self, handle: str) -> Dict[str, Any]:
        rows = self.db.execute("SELECT kind, body FROM journal WHERE handle = ? ORDER BY seq", (handle,)).fetchall()
        if not rows:
            return {}
        events = [json.loads(b) for k, b in rows if k == "event"]
        transfers = [json.loads(b) for k, b in rows if k == "transfer"]
        birth = next(json.loads(b) for k, b in rows if k == "birth")
        return {"birth_certificate": birth, "current_owner": self.current_owner(handle),
                "lifecycle_events": events, "ownership_history": transfers,
                "event_count": len(events), "transfer_count": len(transfers)}

    # ------------------------------------------------------------------ audit
    def head(self) -> str:
        row = self.db.execute("SELECT entry_hash FROM journal ORDER BY seq DESC LIMIT 1").fetchone()
        return row[0] if row else GENESIS

    def verify_journal(self) -> List[int]:
        """Sequence numbers whose link is broken (empty = the journal is intact from genesis to head)."""
        bad, prev = [], GENESIS
        for seq, handle, kind, body, prev_hash, entry_hash in self.db.execute(
                "SELECT seq, handle, kind, body, prev_hash, entry_hash FROM journal ORDER BY seq"):
            if prev_hash != prev or entry_hash != link(prev_hash, handle, kind, body):
                bad.append(seq)
            prev = entry_hash
        return bad
