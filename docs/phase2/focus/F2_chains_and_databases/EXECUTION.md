# F2 Execution — A Database Lifecycle Backend with a Hash-Chained Journal (Start of Execution)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (after-action report 16) · **Plan step:** F2-S1

## What was built
| File | What it is |
|---|---|
| `phase2/backends/sqlite_lifecycle.py` | `SQLiteLifecycleBackend`: persistent, transactional storage (SQLite, Python standard library), behind the same interface as Phase 1's two lifecycle backends (birth, lifecycle event, transfer, history, current owner). Every write is one row of an append-only journal: triggers refuse UPDATE and DELETE, and each row carries sha256(previous hash, entry), so `verify_journal()` detects an edit made by someone who bypassed the triggers. The VIN is stored only as a salted hash; odometer rollback is refused |
| `phase2/backends/test_sqlite_lifecycle.py` | 6 tests |

## What the tests establish
| # | Test | What it shows for F2 |
|---|---|---|
| 1 | Parity with Phase 1's centralized backend | the same operation sequence gives the same owners, counts and odometer readings |
| 2 | The VIN is not stored | a full dump of the database contains no VIN |
| 3 | Odometer rollback refused | the database enforces the lifecycle rule Phase 1's aggregator checks off chain |
| 4 | The journal is append-only | UPDATE and DELETE are refused; the journal verifies |
| 5 | An edit that bypasses the triggers is detected | the hash chain localises the edited row |
| 6 | **An operator who re-derives every later hash is not detected** | the journal is internally consistent again. Only a head hash kept elsewhere (an anchor) reveals the rewrite. This is the precise point where a database stops and a ledger, or an anchor on one, begins (`PLAN.md` E-F2-2) |

All 6 pass. No timing was taken (Phase 2 principle 4).

## Run it
```bash
python3 -m pytest -q phase2/backends/test_sqlite_lifecycle.py
```
