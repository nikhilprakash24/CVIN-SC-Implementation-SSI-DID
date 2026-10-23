# After-Action Report 35 — WM-2 B3 (Latency Charter) and A7 (Python Suites in the Test Register)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-23, after report 34 (WM-2 A5, another session) and this session's report 26. **Brief (the author,
2026-10-23):** take every item of `docs/planning/UNBLOCKED_WORK_2026-10-23.md`; the other session is done.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| B3 | `docs/testing/latency_charter.py` writes `docs/testing/LATENCY_CHARTER.md`. Every V register row that reports a latency is classed: **L-within** (its comparisons are within one run or one host; N ≥ 30 per reported statistic; host and libraries recorded), **L-absolute** (no comparison; same N and record rules), **L-descriptive** (fails one rule; the reason stated), **L-derived** (computed from other rows; inherits). For L-within and L-absolute the script checks that the cited result file records the CPU. Rows that fail are relabelled in the register with a dated note | `--check` in CI and in the pre-push guard; it fails when a V latency row has no class or a conforming row's file records no CPU (shown to fire) |
| A7 | The grand runner keeps a per-test outcome record of the Python layers (`sandbox/grand/report/py_layers.json`, from pytest's JUnit output, names and outcomes only); `build_register.py` reads it and gives each Python test a deterministic TC id | register and coverage matrix regenerate; every Python test in the record has one TC entry; `--check` passes |
| R | Records, grand run last, CI | CI green on the closing commit |

## 2. Execution log
- 2026-10-23 — report opened.
