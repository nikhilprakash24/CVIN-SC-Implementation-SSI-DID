# After-Action Report 34 — WM-2 A5: Every Quoted Number Checked Against Its Result File

**Author:** Nikhil Prakash (MASc, UBC ECE). **Opened and closed:** 2026-10-23. **Plan:** `docs/PLAN_WM-2_A5.md`,
written and pushed (`9e6f843`) before the data file. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`.

## 1. What was built
- `docs/testing/claims.yaml`: a stable id for each of the 62 register rows and, for each of the 45 V rows, the
  tracked result files that carry its numbers; `derived:` entries for bold values no file holds, each with its
  arithmetic (5: #24 335/336 as sums over five suite reports; #31 87 KB = 87,033 B; #50 27,622 = 62,646 − 35,024;
  #56 3,498 = 1,667 + 1,831).
- `docs/testing/check_claims.py --check`, in CI (`test-contracts.yml`) and `tools/prepush_check.sh`: fails on a row
  without an entry, an entry without a row, a V row without a tracked source, a bold claim number in none of its
  sources (normalised: separators removed, file values rounded to the shown decimals), or a `derived:` value that
  is in fact in a source.
- `docs/testing/probe_check_claims.sh` (in CI): the check passes on the tree and fails on an edited bold number, a
  V row without sources and an unknown row.

## 2. What it found (the audit T-F3 failure, nine times)
Nine claim cells still quoted values their result files no longer held, after the A3b re-runs (pass 33) had
restated them only in the status cell: **#21, #22, #26, #27, #31, #32, #37, #44, #48.** Each claim cell now states the
current value read from its result file; the old values are history in the status cell, with the date and reason.
#31's 103.177 ms had left every file when the A3b harness run replaced `results/metrics/latest`; #26's stale 0.164
was not bold, so the checker could not see it, and was fixed by hand.

## 3. Limits
- Only **bold** numbers in the claim cell are checked; non-bold numbers and status-cell history are not.
- The CSV tokenizer reads `83,149` (two fields) as one number; markdown tables are listed beside such CSVs.
- #1–#3 rest on `docs/review02/FOLLOWUP_FC.md` and the hand-assembled `docs/figures/results_snapshot.json`; #3's
  `gas-report.txt` is not tracked.

## 4. Next
WM-2 A7 (the Python suites in the test register), B3 (latency charter), D1 (chapters against the register).
