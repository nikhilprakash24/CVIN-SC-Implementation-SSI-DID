> **Superseded history (2026-10-24).** Written on this branch on 2026-10-15 against the pre-merge tree; its harness run (`2026-10-15T05-03-01Z_ef2c851`) and `docs/testing/` v0 files were reverted from this branch because the trunk produced its own run of record and register afterwards (WM-2 A6, A7; branch review T-12). Kept as the record of what was run. Not a result of record; cite nothing from it.

# After-Action Report 06 — Testing suite & results organisation, Phases 0–1 (2026-10-15)

**Opened:** at the start of the pass. **Status:** CLOSED 2026-10-15; Phases 0 and 1 done under defaults; Phase 2 waits on the filled sheet.
**Input:** `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` (TSR Plan v1.0) and its second-pass sheet. The author has not yet filled the sheet; this pass runs **under the sheet's stated defaults** (D-01 a, D-02 a, D-03 a, D-04 c, D-07 c, D-10 a, D-11 a, D-16 a) and takes no author decision (D-20 … D-32 untouched).
**Base:** `ef2c851` on `claude/testing-suite-organization-z5j7dc`. Standing rules S1–S13 apply; no test skipped or weakened; author-attributed commits.

## Plan

| Phase | Item | Output | Gate |
|---|---|---|---|
| **0** W0-A baseline | run every suite and the two deterministic producers on HEAD; record environment, counts, durations, hashes; re-run the metrics harness so `latest` is stamped on HEAD's contracts tree | `docs/testing/BASELINE_2026-10.md`; `results/metrics/latest` on HEAD | all green, no skips; `meta.measured.contractsTree == HEAD`; harness cells diffed against the previous `latest` |
| **0** W0-B quarantine | move result files with no producer or superseded content to `results/superseded/<date>/` with a README | `4_comparison-framework/results/superseded/2026-10-15/` | every moved file names its superseder and its citing documents |
| **1** registers v0 | parse every Mocha/pytest/script test and the checker into a Test Case Register; hand-write the results register and the claims mirror; generate the coverage matrix | `docs/testing/*`, `tools/testing/build_register.py`, `mapping_rules.json` | every test has ≥ 1 row; `UNMAPPED.md` empty; every V claim has an RR |

## Phase log

| Phase | Commit | Result |
|---|---|---|
| Open | — | fresh container: `npm ci`, `hardhat compile` (47 files), Python deps installed unpinned (as CI) |
| 0 suites | `a01b5de` | Hardhat **369 / 23 pending** (13.7 s); Python **358 passed, 0 skipped** (11.4 s, node 8548 + MOBI artifacts, as CI); use cases **12/12**; checker **94.3 %**. All four match `HANDBACK_2026-10-04.md` §2 |
| 0 producers | `a01b5de` | `benchmark_gas.js`: **0/55 cells changed** (date field only; restored). Harness re-run: `2026-10-15T05-03-01Z_ef2c851` promoted to `latest`; contracts tree = HEAD; **0/192 crud cells × 11 exact fields changed**, lifecycle totals unchanged, frontier unchanged; latency moved (different host). ≈ 55 min on this 4-vCPU host (the handback's ≈ 4 min was on a faster host) |
| 0 quarantine | `a01b5de` | `sensitivity.*` and the July `w3c_compliance.json` moved; checker output of this pass placed at `4_comparison-framework/results/w3c_compliance.json` (94.3 %, unstamped) |
| 1 registers | `a01b5de` | `build_register.py` v0: **1,504 rows** (mocha 679, pytest 378, script 87, harness 360); 0 unmapped after four rule iterations; 603 untagged (expected: tags are Phase 3). `results_register.csv` 19 rows; `claims.csv` 39 rows mirroring register #1–#39 |

## Decisions taken in this pass (reversible; recorded for the sheet)

1. Register files are **CSV + JSON**, not YAML (no new dependency; Q-1.1 default).
2. Contract-level functions outside the catalogue (interfaces, name/symbol, ERC-725X `execute`, the toll demo, `changed` block tracking) are mapped to a visible op **`misc`** rather than forced into C1…V6; Phase 2 decides whether `execute` becomes a catalogue op.
3. ERC-4337 guardian tests map to the proposed **U6** (recover) when the title says recover/guardian, per plan §7.1, so the matrix already shows where U6 would sit.
4. The use-case suite's rows carry the note "pass = no exception; explicit oracle only in UC 3, 6, 10, 11, 12" so the I-class cells are not read as strong evidence.
5. The harness G/L rows take their `T`/`N` from `crud.json` `supported` and carry `gasDeterministic:false` in `notes` for the 14 affected cells.

## Known limits of v0 (for Phase 2 review)

- Title heuristics over-assign in places (e.g. any title containing "delegate" maps to U2 even when the test is about R4); the rules file is the fix point.
- `erc725` has no dedicated unit tests, so its F/N cells are empty by fact, not by mapping error.
- Evidence level is E3 for anything under a CI-collected path and E1 otherwise; E2 (assertion audit) is not computed yet.
- The hypothesis column is rule-based (`hyp_by_class_sut`), not per-test.

## Hand-off

Next: Phase 2 needs the filled second-pass sheet. Phase 3 (tagging) and Phase 6 charter drafts can proceed without it.
