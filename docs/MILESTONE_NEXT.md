# Next Milestone — Deferred Decisions

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-09. **Why:** the author approved the infrastructure-messaging and SUMO-visualisation
designs and asked that the Infura rotation "or other decisions that can be pushed" move to the next
milestone. This file is the list. Nothing here blocks the current work; each item keeps its default.
**Milestone:** v0.9.0 (cut on the merge with a Sepolia witness, per `ORIGINAL_PROMPT_AND_DIRECTION.md` §B.2),
or the next author checkpoint, whichever comes first.

| # | Item | Default until decided | Source |
|---|---|---|---|
| N-1 | Rotate the Infura credential exposed on the onboarding lineage's branches (H1) | not rotated; not on the trunk | `docs/prior-survey/README.md` |
| N-2 | Test a clean `npm ci` without SSH (`ethereumjs-abi` via `git+ssh://`, H9) | CI installs succeed today | same |
| N-3 | Remove the unused `goerli` network entries | left in place | same |
| N-4 | Install SUMO and run S1–S3 with real mobility (S-b) | mock mobility | `docs/PLAN_SUMO_VISUALISATION.md` |
| N-5 | TSR second-pass sheet: the 20 AUTHOR decisions, incl. D-02 (test ids by record vs title) | the sheet's defaults | `docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md` |
| N-6 | Ch. 6 §6.4 wording on the 94.3 % residual (two causes plus one PARTIAL) | reword at the next chapter edit | `docs/HANDBACK_2026-10-09.md` X-2 |
| N-7 | Confirm the five sentences naming ERC-735 the heaviest create | accepted | X-1 |
| N-8 | Defect-log policy calls: D8 rest, D12 rest, D15, D16 rest, D19, D20, D23, D24, D25c (EIP-191 recommended), D26 | documented, not fixed | `docs/DEFECT_LOG.md` §C |
| N-9 | Review-2 decisions 1–6, 9–11, 13–15 (H1 wording, checker strictness, K-4/K-5/K-12, attestEvent duplicates, MOBI wording, freshness k, M4 verdict, 7.1.2 correction, privacy scope) | review-2 defaults | `docs/HANDBACK_2026-10-04.md` §4 |
| N-10 | Merge decisions M-A…M-L: re-review by a different assistant configuration | stand | `docs/PLAN_MERGE_LINEAGES.md` |
| N-11 | Push tags v0.7.0/v0.8.0; Sepolia secrets; SC-05/SC-06; notebook index; chapter 2 citations | open | `docs/HANDBACK_2026-09-30.md` |
| N-12 | Default branch of the repository | unchanged | plan 2026-10-09 Q6 |
| N-13 | `3_cv2x-testbed/README.md` July counts (outside the stale-figure checker's scope) | add to the checker at the milestone | handback X-7 |
