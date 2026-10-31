# F2 Execution: A Database Lifecycle Backend with a Hash-Chained Journal (Start of Execution)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (after-action report 16) · **Plan step:** F2-S1
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-22, AR-35

**In the thesis, this backend is future work** (review §4.1). It is an instrument for the F2 plan, not a result.

## What was built
| File | What it is |
|---|---|
| `phase2/backends/sqlite_lifecycle.py` | `SQLiteLifecycleBackend`: transactional storage (SQLite, Python standard library), persistent when given a file path, behind the same interface as Phase 1's two lifecycle backends (birth, lifecycle event, transfer, history, current owner). Every write is one row of an append-only journal: triggers refuse UPDATE and DELETE, and each row carries sha256(previous hash, entry). Odometer rollback is refused. The current owner is derived from the journal, and the VIN is stored only as a keyed hash under a per-instance secret (both changed for AR-22) |
| `phase2/backends/test_sqlite_lifecycle.py` | the tests |

Tests: see `phase2/backends/test_sqlite_lifecycle.py` (updated for AR-22).

## What the journal detects, and what it does not
| Change by someone who bypasses the triggers | Detected by `verify_journal()` alone? | What would detect it |
|---|---|---|
| An edit of one row, later hashes left as they were | **yes**: the hash chain localises the edited row | the journal itself |
| An edit of one row, every later hash re-derived | **no**: the journal is internally consistent again | a head hash kept outside the database (an anchor) |
| Deletion of rows at the tail | **no**: the shorter journal is internally consistent | a head hash kept outside the database, or an entry count held by someone else |
| Any change to the N − 1 entries written after the last anchor | **no**, even with an anchor | the next anchor (`PLAN.md` E-F2-2) |

So the journal alone is tamper-evident only against an edit that leaves later hashes untouched.
An external head is where a database stops and a ledger, or an anchor on one, begins.
The anchor is not built yet (plan step F2-S3).

No timing was taken (Phase 2 principle 4).

## Run it
```bash
python3 -m pytest -q phase2/backends/test_sqlite_lifecycle.py
```
