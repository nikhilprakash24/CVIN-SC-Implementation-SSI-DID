# TDP-007 — Test and Evaluation Master Plan

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** A.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000). **Supersedes:** nothing; it reads
beside `docs/testing/README.md` (where any test is) and `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` (the suite
plan) and does not replace either.
**Format:** the DoD test and evaluation master plan structure, reduced to what applies: test architecture,
evaluation framework (what each measure answers and how it is judged), test resources, and the exams. Counts are
those of the grand run of pass 21 as recorded in `sandbox/grand/report/GRAND_REPORT.md` and `docs/figures/dashboard_snapshot.json`;
the live counts are on DWG-001, which reads the snapshot. A later grand run moves this table's counts, not its structure.

## 1. Test architecture

| Layer | Subject | Suite | Runner | Count at the last grand run | CI job |
|---|---|---|---|---|---|
| Smoke | every adapter conforms to IF-01 | `sandbox/grand/smoke.js` | grand runner stage `smoke` | 11 adapters conforming | `metrics-harness` (adapter conformance gate) |
| L1 | identity mechanisms across options (the observed asymmetry table) | `sandbox/suites/L1-identity-mechanisms` | Hardhat | 99 passing, 0 failing | `hardhat-tests` |
| L1+L2 | per-standard contract suites, security scenarios, harness conformance, regressions | `1_blockchain-identity/test/**` | Hardhat (`CVIN_SEED=1`) | 537 passing, 0 failing | `hardhat-tests` (count gated against the grand report) |
| L3+L4 | SSI layer, infrastructure verifier v3, exemplar interactions, cv2x tests | `sandbox/py-suites/`, `2_w3c-ssi-layer/**/tests`, `cv2x-testbed/tests` | pytest (`run.sh`, no skips) | 342 passed (after WM-2 C1's eleven resolver tests) | `python-layers`, `python-full-suite`, `vc-layer-tests` |
| Demos | every implemented feature exercised once per option | `sandbox/options/*/demos` | grand runner stage `demos` | 92 demos, 1,752 steps, 594 mined transactions, 0 failures | (grand runner; demo count gate pending, plan G) |
| Mutation | the regression tests kill their mutants | `sandbox/py-suites/L3-ssi/mutation/`, `phase2/idtx/mutate_idtx.sh`, the committed 30-mutant script of WM-1 | scripts | 39 of 39 (verifier v3); 5 of 5 (IDTx gate); 30 of 30 (WM-1) | `hardhat-tests` (IDTx mutants) |
| Conformance (external) | the resolver against the W3C DID test suite | `docs/conformance/` | jest, suite at `939b31d` | 335 of 336 generated tests (#24) | not in CI (recorded reports) |
| Compliance (internal) | structural checks against DID Core v1.0 and VC DM v2.0 | `cv2x-testbed/scripts/w3c_compliance_checker.py` | python | 94.3 percent, floor 94.0 (#4) | `compliance-score` |
| Documents | every generated document rebuilt and compared; superseded figures not cited | the `--check` commands listed on DWG-005 | python | 12 checks after this pass (9 before, plus the three TDP checks) | `hardhat-tests` document step |
| Guards | every guard shown to fire | `docs/testing/probe_run_identity.sh`, `tools/run_identity/test_promote.py`, `docs/tdp/probe_tdp_checks.sh` | bash, pytest | per producer; 13 refusals; 1 tamper per TDP generator | `hardhat-tests` |

The grand runner (`python3 sandbox/grand/run.py all`) runs the first five layers in sequence, records the stage table
and the step kinds, and is run last in every pass so that the generated documents that read its report are regenerated
afterwards (handback gotcha).

## 2. Evaluation framework

Every measure is one of four kinds, judged one way.

| Kind | Judged by | Examples |
|---|---|---|
| Pre-registered verdict | the pass band, falsifier and expectation written before the first run; reported as it fell; departures are dated amendments | I1 to I5 (`INFRASTRUCTURE_PREREG.md`; #44 to #48), M4 and M5 (`PLAN_MOBI_SUMO.md`; #33, #38) |
| Determinism check | N runs of one commit byte-identical, or a declared range over declared seeds | gas benchmark 30 of 30 (#25); I4 over seeds 1 to 30 (#47); harness tables across runs (register section 5.A) |
| Descriptive measurement with confidence interval | median of 30 seeded-run medians, 95 percent bootstrap CI, p95 of run medians; compared only within a run; host and libraries recorded | #27, #44, #48 |
| Structural or count result | a count of checks, tests or cells, with the instrument named; never a percentage across instruments | #4, #24, #28, #45, #46 |

Rules applied at judgement: a number is reported as a count when it is a count (guide 1.1.9); gas is exact or a
range by rule (1.1.10); a verdict that failed is reported as failed (1.2.1); a trial run is disclosed and never
reported as a result (1.2.9).

## 3. Pre-registration protocol

1. The design note and the pre-registration are committed before any code or run (I-a; `INFRASTRUCTURE_PREREG.md`
   locked 2026-10-09).
2. Each question carries a measure, an expectation, a pass band and a falsifier.
3. The attack set is reviewed adversarially before the run, not only after (lesson of WM-1: two accepted attacks were
   found by a reviewer after seven registered ones passed).
4. A departure is a dated amendment in the pre-registration's own section, marked post hoc if made after the run it
   concerns (A1 to A3 post hoc; A4 to A6 before their runs).
5. The verdict is reported as it fell, with the history of earlier runs beside it (#44: 1.226 on v3; the v2 value
   kept as history).

## 4. Test resources

| Resource | Specification | Where recorded |
|---|---|---|
| Chain | Hardhat in-process, chain id 31337, automine, solc 0.8.24, optimizer 200 with viaIR, EVM cancun, OpenZeppelin 5.0.2 | `MEASUREMENT_CONDITIONS.md` section 1 (M1), `meta.json` |
| Runtimes | Node 22, Python 3.11; `npm ci` from the lockfile (a toolchain change is a conditions change, section 5.E) | workflows; `package-lock.json` |
| Hosts | one container per run; CPU model, count and kernel in every result header; latency compared within a run only | each result file's `environment` |
| Seeds | `CVIN_SEED=1` for the L1, Hardhat-tree and demo stages; experiment seeds 1 to 30 recorded per run | `sandbox/lib/determinism.js`; result files |
| Isolation | a fresh Hardhat node per run (started by path so the recorded process id is the node's); port checked free afterwards; nothing else on the host during a latency run, stated in the run log | run logs under `cv2x-testbed/sumo/results/run_logs/` |
| CI | 8 jobs across 3 workflows; full history checkout for the stamp check | `.github/workflows/` |

## 5. Exams

| Exam | Entry criteria | Exit criteria | Evidence |
|---|---|---|---|
| Pass gate | after-action report opened and committed first | grand run ALL OK; CI green on the closing commit; checklist of guide section 3 complete | the report's closing section |
| Work-milestone gate | every plan item has a status | the seven closing conditions of `docs/milestones/README.md` | `WM-n_REPORT.md`; audit findings register |
| Requirement verification | TDP-002 requirement with evidence rows | TDP-005 status VERIFIED (every row V, threshold met, nothing pending) | TDP-005 |
| Defence readiness | Scope v3 adopted; chapter 2 written | every crux evidenced or its gap stated as a limitation; the fifteen examiner questions each answered from a file | `CRUX_REGISTER.md`; scope reconciliation section 5 |

## 6. Limits of the test programme

- No test runs on a public or permissioned network (N-11).
- No test exercises a radio, a channel or real mobility (SC-22); the injected attacks are at the message layer.
- The external DID suite is run by hand and recorded, not in CI.
- The demo count has no CI gate yet (plan WM-2 G).
- A probe proves a guard can trip; it does not enumerate the fault classes it misses (TDP-002 EVD-05 limit).
