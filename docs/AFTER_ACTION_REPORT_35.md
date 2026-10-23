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
- **B3, latency charter.** `docs/testing/latency_charter.py` writes `docs/testing/LATENCY_CHARTER.md`: 14 rows
  classed, 9 L-within, 1 L-absolute, 4 L-descriptive (#26, #31, #39, #57), 1 L-derived (#36). Both guards shown to fire
  (a missing class for #27; #31 claimed as L-within against a file with no CPU).
  - **Finding: the metrics harness records no host.** Its `meta.json` names Node and the compiler but not the CPU, so
    #31 and #39 are descriptive only for latency (gas unaffected). Logged as **N-26**: record the CPU at the next
    harness run of record.
  - **Finding: #55's summary file records no CPU**; each of its 12 replicate files does, so the check reads one.
  - The four relabelled rows carry a dated register note. The first wording of #57's note said "gas", which made the
    gas charter treat #57 as a gas row; reworded, since #57 reports no gas.
  - CI's document step and `tools/prepush_check.sh` run `latency_charter.py --check`. Regenerated: the test register,
    dashboard, result cards, presentation page, and the TDP's DWG-005 (with its own generator; it reads the register).
- **A7, Python suites in the test register.** The grand runner's Python stage now passes `--junitxml` (classic
  format, which records each test's file) to `sandbox/py-suites/run.sh` and reduces the output to
  `sandbox/grand/report/py_layers.json`: file, name and outcome per test, sorted, paths made repository-relative
  (pytest's root is `sandbox/py-suites`; the first record had `../../` paths, corrected before commit).
  `build_register.py` gives each test a TC id `TC-py-<module>-<test>`, disambiguated by a short hash where two names
  collide. Result: 376 entries (L3 78, L4 19, SSI layer 279), equal to the record's 376 tests, all pass. The register's
  `--check` passes; the pre-push guard passes, including the TDP's trace check that reads the register.
- **Grand run (last), at `b49c9a1`.** ALL OK: smoke 11, L1 99, Hardhat 562, Python layers 376, 92 demos / 1,758 steps.
  Generated documents regenerated; the pre-push guard passes.

## 3. Closing
The pass delivered both steps. **CI 11 of 11 green on `09c5363`.** WM-2 stands at 15 of 20 steps.

**B3** classes every verified latency figure. Four rows are now descriptive only. The most useful finding is that the
metrics harness never recorded the machine it ran on, so its latency rows cannot be compared across runs until N-26
is done; its gas rows are unaffected. **A7** puts all 376 Python tests in the test register from a per-test record the
grand runner now keeps, so the register covers every suite.

**Next:** the remaining unblocked items (mutation scripts for the C1 and C2 tests, the read-only chapter and TDP
audits, D2, the I-05 model, CI hygiene, progress report draft 2). D1 waits on the author's D-1.
