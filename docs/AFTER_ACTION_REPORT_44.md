# After-Action Report 44 — Branch Decisions B-2 to B-4 Recorded and Applied

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-11-22, after report 43 (another session: the default branch merged into the trunk, PR #25 open).
**Brief (the author, 2026-11-22):** "B-2 to B-4: go with your recommendations". Documents only; no producer re-run.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| B-2 | Simulation visuals kept apart until WM-2 D1 | recorded |
| B-3 | TSR series: review after WM-2 closes | recorded, with what of it has reached the trunk since |
| B-4 | X1 documents only: take the research-expansion documents onto the trunk, not the build | the documents pass the checks; the build stays on its branch, and the documents say so |
| R | Decision sheet, branch review, master plan, index; CI | CI green on the closing commit |

## 2. Execution log
- **B-2.** No action: `claude/simulation-visual-plan-gp4exp` stays unmerged; it changes #27's producers, so it waits for
  WM-2 D1's choice of chapter 5 figures.
- **B-3.** Most of the TSR series reached the trunk after the review of 2026-10-24: the author merged PR #19 into the
  default branch, and report 43 merged the default branch here. Two commits remain on the branch, both wiring:
  `f570d10` (CI and the pre-push guard run the test-register completeness guard and the charter citation guard, each
  with a probe) and `badbe52` (DWG-005 regenerated for those CI steps). Until they are reviewed, the two guards exist on
  the trunk but are not run by CI. Kept for the review after WM-2 closes, as decided.
- **B-4.** `docs/PLAN_RESEARCH_EXPANSION.md` and `docs/research-expansion/` (seven documents) were taken from
  `claude/cvin-research-improvements-559o01` with `git checkout <branch> -- <paths>`, not a merge, so the branch's code
  stays on it: `CVINTollCorridor.sol`, `CVINTestStable.sol`, `TollCorridor.test.js`, `toll_corridor.py`,
  `test_x1_toll_corridor.py` and `x1_toll_corridor.json`. The stale-figure checker caught one superseded value on
  arrival (WHY.md quoted the V2V verify as 0.153 ms; now 0.142 ms, #27). `results/X1.md` and the folder's README open
  with a note that the X1 build is not on the trunk, so its figures are not results of record and carry no register row.
  `docs/INDEX.md` gains a row.
- **Records.** The decision sheet's §F gives B-1 to B-4 a row each; the branch review marks each decision; the master
  plan's T-16 reads answered.

## 3. Closing
All four branch decisions are answered and applied. No branch is waiting on the author: the simulation visuals wait
for WM-2 D1, the TSR remainder and the X1 build wait for WM-2's close and D-13.
- **CI at `6e480ed`: the contracts job red, for a cause outside this pass.** The GitHub runner image's system Python is
  now 3.14; the contracts job was the only one with no `setup-python` step, so `pip install -r ci/requirements-ci.txt`
  ran there, found no 3.14 wheel for the pinned `coincurve==21.0.0`, and failed building it from source
  ("Expected exactly one LICENSE file in cffi distribution"). The job now pins Python 3.11, as every other job does (a
  scan of all 12 jobs found no other Python use without a pinned interpreter). DWG-005, which draws the CI steps, is
  regenerated.
