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
