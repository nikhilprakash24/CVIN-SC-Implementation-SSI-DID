"""Parity and tamper-evidence tests for the database lifecycle backend (Phase 2, F2, start of execution).

Parity: the same operation sequence through the Phase 1 centralized backend and through this one gives
the same owners, counts and odometer readings. Tamper evidence: the journal refuses UPDATE and DELETE,
and an edit made by bypassing the triggers is detected by verify_journal(). No timing (principle 4).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cv2x-testbed"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from identity.lifecycle_backends import CentralizedLifecycleBackend, event_payload  # noqa: E402
from sqlite_lifecycle import SQLiteLifecycleBackend  # noqa: E402

VIN = "1HGBH41JXMN109186"


def drive(backend):
    h = backend.birth(VIN, 0)
    for i, odo in enumerate((1000, 2500, 4000, 5200)):
        backend.lifecycle_event(h, odo, event_payload(odo))
        if i % 2 == 1:
            backend.transfer(h, odo + 1)
    return h, backend.history(h)


def test_parity_with_the_phase1_centralized_backend():
    hc, central = drive(CentralizedLifecycleBackend())
    hs, sql = drive(SQLiteLifecycleBackend())
    assert sql["event_count"] == central["event_count"] == 4
    assert sql["transfer_count"] == central["transfer_count"] == 2
    assert sql["current_owner"] == central["current_owner"]
    assert [e["odometer"] for e in sql["lifecycle_events"]] == [e["odometer"] for e in central["lifecycle_events"]]


def test_the_vin_is_not_stored():
    b = SQLiteLifecycleBackend()
    drive(b)
    dump = "\n".join(b.db.iterdump())
    assert VIN not in dump


def test_odometer_rollback_refused():
    b = SQLiteLifecycleBackend()
    h = b.birth(VIN)
    b.lifecycle_event(h, 5000, {})
    with pytest.raises(ValueError):
        b.lifecycle_event(h, 4000, {})


def test_journal_is_append_only():
    b = SQLiteLifecycleBackend()
    drive(b)
    with pytest.raises(Exception, match="append-only"):
        b.db.execute("UPDATE journal SET body = '{}' WHERE seq = 2")
    with pytest.raises(Exception, match="append-only"):
        b.db.execute("DELETE FROM journal WHERE seq = 2")
    assert b.verify_journal() == []


def test_an_edit_that_bypasses_the_triggers_is_detected():
    b = SQLiteLifecycleBackend()
    drive(b)
    head = b.head()
    b.db.execute("DROP TRIGGER journal_no_update")   # what an operator with file access can do
    b.db.execute("""UPDATE journal SET body = '{"data":{},"odometer":999}' WHERE seq = 3""")
    assert b.verify_journal() == [3]
    assert b.head() == head   # the head hash alone does not reveal the edit: it must be re-derived


def test_an_operator_who_rewrites_every_hash_is_not_detected_without_an_external_anchor():
    """The limit F2 measures a chain against: re-hashing from the edit onward passes verify_journal()."""
    from sqlite_lifecycle import link
    b = SQLiteLifecycleBackend()
    drive(b)
    anchored_head = b.head()                         # what an external anchor would have recorded
    b.db.execute("DROP TRIGGER journal_no_update")
    rows = b.db.execute("SELECT seq, handle, kind, body, prev_hash FROM journal ORDER BY seq").fetchall()
    prev = rows[0][4]
    for seq, handle, kind, body, _ in rows:
        if seq == 3:
            body = '{"data":{},"odometer":999}'
        h = link(prev, handle, kind, body)
        b.db.execute("UPDATE journal SET body = ?, prev_hash = ?, entry_hash = ? WHERE seq = ?", (body, prev, h, seq))
        prev = h
    assert b.verify_journal() == []                   # internally consistent again
    assert b.head() != anchored_head                  # only an anchor kept elsewhere shows the rewrite
