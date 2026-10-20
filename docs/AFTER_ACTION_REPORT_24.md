# After-Action Report 24 — Lead's Pass: Decision Sheet, Pre-push Guard, Progress Report

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-20, after report 23 closed at `de27b7c` (CI 8/8 green on `024274d`); closed at the end of this pass
**Brief (the author, 2026-10-20):** continue; as the lead now, add what the project needs, and integrate with the
rest of the work. The cross-model check of passes 16–22 runs in a separate session; this pass holds its pushes until
that session has closed, so one session writes to the branch at a time.

## 1. What a fresh look at the project shows
- **The author's decisions are scattered.** Open decisions live in five files (`docs/phase2/DECISIONS.md`,
  `SCOPE_RECONCILIATION.md` §6, `MILESTONE_NEXT.md`, reports 21 and 22, and now the I-24 brief). None of them is on
  one page with a recommendation, so they stay open. Several block chapter work (D-1, D-15, N-23).
- **CI went red three times in pass 22** on guards that run in seconds and could have run locally before each push
  (the byte-identical MOBI copies, the stale-figure checker, the testbed artifact freshness).
- **The hand-over write-up the author asked for** has a plan (`docs/planning/PROGRESS_REPORT_PLAN_2026-10-20.md`)
  and no draft. `docs/DEVELOPMENT_HISTORY.md` stops at July 2026.

## 2. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| L1 | `docs/DECISION_SHEET_2026-10-20.md`: every open author decision on one page, each with the files it lives in, what it blocks, the orchestrator's default and a recommendation; ordered by what it unblocks | orchestrator | every decision id in the five sources appears; nothing is decided by the sheet |
| L2 | `tools/prepush_check.sh`: runs, locally and unpiped, every guard of CI's document step plus the MOBI-copies check and the feature-matrix check; exits non-zero on the first failure; documented in the handback as the step before every push | CI engineer | the script fails when one guard is broken (shown by a probe), and passes on the clean tree |
| L3 | `docs/PROGRESS_REPORT_2026-07_TO_2026-10.md`, draft 1 per the plan, with a generated appendix of commits per pass; the stale-figure checker and `check_docs_numbers.py` run on it | orchestrator; technical writer | every number quoted carries its register row; the checker is clean; the reader and the AI-use statement are left as marked gaps for the author |
| R | Records; push after the check session has closed; CI | orchestrator | CI green on the closing commit |

No code, test, result file or register row changes in this pass; no grand run (as reports 20 and 23).

## 3. Execution log
- 2026-10-20 — report opened (committed locally; the push waits for the check session).
- **L2, pre-push guard.** `tools/prepush_check.sh` runs the MOBI-copies check, the feature-matrix check and the
  thirteen document checks of CI's document step; `--probe` breaks a MOBI copy, expects the failure, and restores it.
  Shown to fire; passes on the clean tree. The testbed artifact check runs when `cv2x-testbed/node_modules` is CI's
  link, or with `PREPUSH_TESTBED=1`.
- **L1, decision sheet.** `docs/DECISION_SHEET_2026-10-20.md`: 26 decision ids from five files, in four groups by
  what they unblock, each with the file it lives in, the default in force and a recommendation. Every id in the five
  sources is on the sheet (checked by grep). The sheet decides nothing.
- **L3, progress report, draft 1.** `docs/PROGRESS_REPORT_2026-07_TO_2026-10.md` (nine sections) with the generated
  appendix `docs/PROGRESS_APPENDIX_2026-07_TO_2026-10.md` from `docs/make_progress_appendix.py` (175 commits in 21
  groups since July; passes whose opening commit lacks the "report N opened" subject merge into their neighbour, as
  the generator's docstring says). The stale-figure checker is clean on both. Every register number carries its row;
  the defect counts (42 fixed, 6 partly, 18 open of 66) and test counts are from the dashboard snapshot at this
  commit. The reader and the AI-use statement are marked gaps for the author (decision sheet §A). The appendix is
  regenerated at each pass's close rather than CI-checked, like the contribution record, because it reads git.
