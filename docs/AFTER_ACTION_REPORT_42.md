# After-Action Report 42 — T-17 (Row #26's Density Sweep Confirmed) and T-20 (the September Project Summary Dated)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-31, after report 41 closed (CI green on `dc79377`). **Brief (the author):** "continue"; the two
tasks of the master plan that need no answer. Documents and checker reasons only; no producer re-run.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| T-17 | Find why `scaling_verify.json` (#26) reads "code changed since: yes", replace its "to be confirmed" reason | the reason traced to commits and files |
| T-20 | `docs/PROJECT_SUMMARY.md` is a September snapshot still listed as canonical | dated, and the index points elsewhere |
| R | Records; CI | CI green on the closing commit |

## 2. Execution log
- **T-17, confirmed, and the content is current.** The file has two sections. Exp. C (credential richness) carries the
  file's only stamp (2026-10-04, `d78e344`); its producer's scope differs from that stamp only by the stamp-only commit
  `188efec` (WM-2 A2). Exp. D's section (`v2v_density`) was rewritten by the A3b re-run at `0b39570`: P = 80 at 12.45 ms
  and P* 641.2 match #26 and `scaling_verify_density.csv`. The "yes" comes from Exp. D's scope (its driver fix and the
  SUMO layer changed), because `run_verify_scaling.py` writes no stamp of its own into the shared file. The
  `KNOWN_STALE` reason now says exactly this; new task T-21 has the driver write its own stamp block at its next run,
  after which the exception goes. The five `scaling_verify_repeats/` files are Exp. D repeats of 2026-10-04 on the
  pre-fix driver; #26's current claim does not use them (the latency charter already calls the row descriptive for
  lack of replicates), so their reason now calls them history.
- **T-20.** `docs/PROJECT_SUMMARY.md` gains a dated banner (the restoration day, 2026-09-24: 29 commits, 47 tests), as
  `MASTER_UPDATE.md` has. `docs/INDEX.md` answers "what exists and does it run?" with the master plan §1 and §4 and the
  grand report, and lists the summary under Historical.

## 3. Closing
Both tasks done; one follow-up (T-21) waits on the next #26 run. The master plan's task table records all three.
