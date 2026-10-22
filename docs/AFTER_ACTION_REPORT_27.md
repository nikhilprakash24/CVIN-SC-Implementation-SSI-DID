# After-Action Report 27 — TDP Runbook Phases 8 and 9: Requirement-to-Test Trace and the ICD Gate

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-22, after report 25 closed at `ed42ba2` (CI 8/8 green on `7bb683e`); report 26 is the check
session's. Closed at the end of this pass.
**Brief (the author, 2026-10-22):** run runbook phases 8 and 9; continue.

## 1. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| P8 | A `tests` list per requirement in `docs/tdp/requirements.yaml`, naming entries of `docs/testing/test_register.yaml` (TC ids) or, for a measurement, the producing script by path; `make_vcrm.py` prints the trace in TDP-005 and fails `--check` on an id or path that does not exist | orchestrator; CI engineer | the new check shown to fire on a fake id; every T-method requirement names at least one test or script |
| P9 | `docs/tdp/check_icd.py --check`: every backticked identifier in TDP-003 sections 2 to 7 exists in the source file its section names; added to the CI document step and to `probe_tdp_checks.sh` with a tamper probe | orchestrator; CI engineer | shown to fire on a fake identifier |
| R | Runbook phases 8 and 9 marked executed; handback addendum; manifest; `tools/prepush_check.sh`; CI read and recorded | orchestrator | CI green on the closing commit |

**Defaults.** P8-a: a `tests` entry is a TC id or a repository path; a path counts as the test of record for a
measurement, since the register has no TC entries for experiments (N-15, A7 pending). P9-a: a token is checked as a
literal substring of the section's source files, after stripping call parentheses; tokens with spaces, angle brackets
or a leading `--` are skipped and listed as unchecked.

## 2. Execution log
- 2026-10-22 — report opened.
- **P8, requirement-to-test trace.** Every requirement in `requirements.yaml` has a `tests` list: 20 test-register
  ids (the 11 L1 `C1-F` cells for SYS-01, the 9 `identityHijack-A` cells for SEC-01) and 38 paths to producing scripts,
  regression tests or records. `make_vcrm.py` fails on an unknown id, a missing path, or a test-method requirement
  with no entry; TDP-005 gained section 3, the trace. Shown to fire three ways before it passed: a fake id
  (`TC-fake-id-A`) and, unplanned, two paths I had written from the register's own text that no longer exist
  (`test/MOBIVID/attestEventRegression.test.js`, `test/ERC1056/PseudonymPool.test.js`; both moved under
  `test/L2-identity-system/per-option/`). The register row #28 and DWG-006's bill of materials carried the old paths;
  the drawing is corrected here, the register row is the other session's to correct (noted for its next pass).
- **P9, the ICD gate.** `docs/tdp/check_icd.py` reads TDP-003 sections 2 to 7, takes every backticked token, strips
  call parentheses, and requires it as a literal substring of the section's named sources; a file name must exist in
  the tree; a dotted name is checked part by part. First run: 10 of 179 tokens not found. Each was a document fault,
  not a source fault: three bare file names and a run id needed their files among the sources; `@input_set` and
  `families[]` were my shorthand, not the schema's text (reworded to `@hardhat` and `families`); one commit hash was
  backticked as if it were code. The IF-04 paragraph was also rewritten to the C1 as-built state (report 21), since
  it still said "in progress". Final: 183 checked, 0 not found, 15 skipped as non-identifiers. The gate is in the CI
  document step and in `probe_tdp_checks.sh`, which appends a fake identifier and expects failure.
- **Side effect caught by its own check.** Adding the CI line made DWG-005 stale, because the sheet lists the
  document checks parsed from the workflow (now 13); regenerated.
- **Records.** Runbook phases 8 and 9 marked executed; TDP-000 names the gate; `tools/prepush_check.sh` run (its
  feature-matrix step cannot run in this container, as in report 25; everything else passes).

## 3. Closing
The pass delivered P8, P9 and R. CI result on the closing commit: recorded in the "Report 27 closed" commit.

**Four TDP guards now stand in CI** (matrix, worksheet, drawings, interface document), each with a probe that
shows it fires. The package's remaining runbook phases are 11 (external review) and 12 (Rev B issue).

**Next:** phase 11 needs a session that did not write the package; phase 12 waits on the WM-2 steps that move the
rows the hand-written documents quote (A3b, A6). The decision sheet's section A is still the author's.
