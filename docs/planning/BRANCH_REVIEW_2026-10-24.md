# Branch Review, 2026-10-24: the Five Research Branches Not on the Trunk

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-24 (after-action report 37; master plan task T-12,
question Q-B7). **Read-only:** nothing was merged. Each branch was compared with this branch at `28dd0b9`, and the
two docs-only branches were trial-merged in a throwaway branch, with the pre-push guard run on the result.

## 1. Summary
| Branch | Unmerged commits | What it adds | Touches results of record? | Recommendation |
|---|---|---|---|---|
| `claude/exploration-plan` | 2 (10-15) | related-work workspace scaffold, 8 files | no | **merge after one fix**: its README quotes "369 passing" as the baseline of its day; mark that line as dated |
| `claude/system-blueprint-diagrams-fd8apg` | 2 (10-22) | 23 generated blueprint sheets, their generator, a Rev B number audit, X-series figures | no, docs only | **merge after regeneration**: 19 superseded figures, in its audit and X-series tables; regenerate them from the current register, then merge |
| `claude/simulation-visual-plan-gp4exp` | 3 (10-21 to 10-22) | V2V event traces, chapter figures, offline replays, a real SUMO network | **yes**: changes `run_v2v_stats.py`, `sumo_identity_integration.py` and the SUMO network, the producers of #27 | **author decision**: merging marks #27 "code changed since", so it needs a re-run of #27 at the merged commit; worth it only if the figures go in the thesis |
| `claude/testing-suite-organization-z5j7dc` | 4 (10-15 to 10-22) | TSR phases 0, 1, 3 and 6, staged as a patch series under `docs/planning/testing_suite/staged/` | **yes**: replaces `1_blockchain-identity/results/metrics/latest/` (about 20,000 lines removed) | **do not merge the branch.** Its harness results predate A6's run of record (2026-10-23). Review the staged patch series and take its parts that A5 and A7 did not already cover |
| `claude/cvin-research-improvements-559o01` | 4 (10-15 to 10-22) | research expansion documents, and scenario X1 (two new contracts, a Hardhat test, a Python scenario and a result) | adds a new result, `x1_toll_corridor.json` | **author decision**: X1 is new building, which decision D-13 defers until after the defence. Its documents could merge alone, as Phase 2 material |

## 2. Findings
- **No branch conflicts with the trunk** in the two trial merges. The risk is drift, not conflict: all five branches
  were built before the A3b re-runs and the A5 correction of 2026-10-22 and 10-23.
- **The trial merge of the two docs-only branches fails the stale-figure check.** 21 hits in 5 files:

| File | Hits |
|---|---|
| `docs/blueprints/AUDIT_REV_B.md` | 10 |
| `docs/figures/x_series/XT-02_lifetime_footprint.md` | 6 |
| `docs/figures/x_series/README.md` | 2 |
| `docs/figures/x_series/XT-03_requirement_decision_table.md` | 1 |
| `docs/related-work/README.md` | 2 |

  The XT-02 values are #35's pre-A6 lifetime gas (for example ERC-735 5,369,010, now 5,797,549), and XT-03 quotes the
  old 0.153 ms. So the checker does what it was built to do: it stops a merge from bringing superseded figures back.
- **Two branches change result producers.** The simulation-visual branch edits the V2V driver and the SUMO network.
  The TSR branch rewrites the harness's results. Neither can merge without a decision about the results of record.

## 3. What the author decides
| Id | Decision | Options | Recommendation |
|---|---|---|---|
| B-1 | Merge `exploration-plan` and `system-blueprint-diagrams` after the fixes in §1 (**done**: exploration 2026-10-24, report 38; blueprints 2026-10-31 at Rev C, report 40) | yes / no | **yes**: one pass, no result changes |
| B-2 | The simulation visuals: thesis figures or not | merge and re-run #27 / keep apart | **keep apart until WM-2 D1** decides which figures chapter 5 uses |
| B-3 | The TSR patch series | review and take parts / close | **review**, after WM-2 closes |
| B-4 | Scenario X1 | merge its documents only / all / keep apart | **documents only**; the build waits for D-13 |
