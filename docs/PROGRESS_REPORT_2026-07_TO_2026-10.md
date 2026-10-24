# Progress Report: July to October 2026

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-20 (after-action report 24), **draft 1**.
**Reader:** *[to be set by the author: supervisor, committee, or a successor taking over the repository; the depth
of §4 and §6 changes with it]*. **AI-use statement:** *[to be inserted once decision N-23 is taken; see
`docs/DECISION_SHEET_2026-10-20.md` §A]*.
**Sources:** the after-action reports 02–24 (`docs/AFTER_ACTION_REPORT_*.md`), the claim register
(`docs/MEASUREMENT_CONDITIONS.md`; every number below with a `#` is quoted from it and only from a row of status V),
the defect log, the milestone and audit records, the handbacks, and the git history (the generated appendix
`docs/PROGRESS_APPENDIX_2026-07_TO_2026-10.md`). **Extends** `docs/DEVELOPMENT_HISTORY.md`, which ends at July 2026.

## 1. Summary
Between the July milestones (v0.7.0, v0.8.0) and today the project did three things. It turned a set of results into
a system of record: a claim register in which every quoted number carries its source, its conditions and its status,
and generated documents that CI rejects when they drift from the files they are built from. It filled the thesis's one
empty question, infrastructure messaging, with a pre-registered experiment that was designed, built, measured, reviewed
adversarially, hardened and re-run, with verdicts reported as they fell. And it found and fixed its own defects, 66
logged so far, 42 fixed, several of them in work done during these months rather than before them.

The numbers the thesis now rests on are in the register (52 rows: 34 verified, 10 superseded, 7 estimates, 1
unsupported). The test base at the last full run is 541 Hardhat tests, 342 Python tests and 92 demos over 1,758
steps, all passing (`sandbox/grand/report/GRAND_REPORT.md`). Two work milestones were defined and the first closed
under audit; the second is nine steps in. Phase 2, the research programme after the thesis, exists as documents.

## 2. Where things stood in July
v0.7.0 (2026-07-14) was the integration milestone: the changelog records that an audit of the merged parallel-session
work had found "demo theater" (mocked verification, hard-coded results, contracts that never ran) and that the release
fixed it and added the empirical layers. v0.8.0 (2026-07-15) added the ninth standard (ERC-725xy) and the statistical
treatment (N = 30, confidence intervals). `docs/DEVELOPMENT_HISTORY.md` and `CHANGELOG.md` carry that record; this
report starts where they stop.

Two things were not yet true in July. The repository had two trunks, a review lineage and a sandbox lineage, each with
its own results; and no machinery held a quoted number to its source. Both were dealt with in the autumn.

## 3. The passes, in order
Work since September is organised as passes, each with an after-action report opened before the work and closed with
CI's result. The table is the spine of this report; the sections after it draw out what matters.

| Pass | Dates | Work | Record |
|---|---|---|---|
| 02–04 | 09-24 to 09-30 | review of the testbed lineage; the handback's list executed; the grand sandbox and per-option sandboxes with layered test suites | reports 02–04 |
| 05–06 | 10-04 | the high-severity defects the sandbox found, fixed with regression tests; conformance follow-up; results of record re-executed on the final contracts | reports 05–06 |
| 07 | 10-06 to 10-09 | the two lineages reconciled into one trunk (`bd90004`); D27; lifecycle-parity re-run | report 07 |
| 08–11 | 10-09 | the plan of 2026-10-09; infrastructure messaging (C3) designed, pre-registered, built, measured; SUMO trace; adversarial review of passes 9–10 and the run-identity fixes | reports 08–11 |
| 12 | 10-10 | work milestone WM-1 closed: plan review, backward fixes, milestone report, an audit by four briefs, presentation draft | report 12; `docs/milestones/` |
| 13–15 | 10-10 to 10-14 | WM-2 A1 (stamp inventory), A2 (one stamp helper with per-producer scope), A4 (the promote step); Phase 2 opened; hand-off to a different assistant model | reports 13–15 |
| 16 | 10-14 | WM-2 C0 (verifier v3, D51); Phase 2 focuses F1–F3 with a writing team and an academic review | report 16 |
| 17–19 | 10-14 to 10-15 | WM-2 B1 (seeded randomness, I4 over declared seeds), B2 (the gas charter), C3 (#32 and #37 on one host); result cards; contribution record | reports 17–19 |
| 20 | 10-15 | the Technical Data Package, a parallel pass in another session | report 20; `docs/tdp/` |
| 21–22 | 10-15 to 10-18 | WM-2 C1 (did:ethr resolution reads the chain), C2 (attestation restricted to owner or delegate, D54) | reports 21–22 |
| 23–24 | 10-20 | Phase 2 session 3 (two deep-dive briefs); this report, the decision sheet, the pre-push guard | reports 23–24 |

## 4. What was measured, re-measured and withdrawn
The register's discipline is that a number enters a chapter only with a row of status V, and that a superseded
number stays as history with an arrow to its replacement. Three examples of each kind, with their rows.

**Established and unchanged since July.** The nine-standard gas table (#25): creating an identity spans 52,216 gas
(CVIN-Combined) to 1,757,881 (ERC-735), 33.7×. V2V credential verification on the warm path at 0.142 ms, 95 % CI
[0.141, 0.143] (#27). 43 of 43 attack scenarios defended, each reverting with its documented reason (#28).

**Re-measured, and reported as it fell.** The infrastructure experiment I1 (#44): the ratio of SPaT verification to
BSM verification is 1.226 [1.219, 1.238] on verifier v3, against a pass band of [0.80, 1.20] pre-registered before
the first run. It is outside the band and not falsified (the falsification line is 2.0), and the register says so
rather than re-running until it passed. The MOBI attestation cost moved twice as its security was tightened: to
192,749 gas when the signature check was added, and to 222,082 when the owner-or-delegate check of pass 22 was added
(#28; the execution-gas pin is 198,694).

**Withdrawn.** The resolver latency row of the early register was superseded because the resolver synthesised its
document rather than reading a chain (M0 row, status S; pass 21 changed the resolver). The cross-run read-mode ratio
of Phase 2's first draft was withdrawn by the academic review (report 16). "Throughput" was cut from RQ1 because the
only throughput row is unsupported (#39, status U; scope decision D-3).

**Host dependence, made explicit.** Rows #32 and #37, the freshness experiments, disagreed on absolute times. Pass 19
re-ran both configurations at their own code on one host, under a decision rule committed first, and attributed the
difference to the host (#52). The lesson is now a rule: a latency row names its host, and two rows from different hosts
are never compared on absolute values.

## 5. Defects: found where, by what
The defect log holds 66 entries (D1–D66): 42 fixed, 6 partly fixed, 18 open. They were found by five instruments, and
the distribution matters more than the count:
- **the sandbox and its demos** (passes 04–06): the high-severity contract defects, among them an ERC-1155 transfer that
  bypassed the identity model (D7/D8) and a MOBI provider that did not bind verification to the registered key (D11);
- **the adversarial review of passes 9–10** (pass 11): the run-identity guards that certified runs of record had never
  worked (D49 and its neighbours); no result moved, but the evidence had been mis-stated for two passes;
- **the WM-1 audit** (pass 12): 72 findings from four briefs, each dispositioned; among them D51, the verifier that
  trusted its own clock over the chain's, and D54, attestations open to any role-holder;
- **the academic review of Phase 2** (pass 16): 41 findings, 40 fixed, which cut the IDTx count from 25 implicit
  instances to 4 under one definition, and found D64, the unsalted VIN hash in the testbed;
- **the passes' own gates** (passes 17–22): a seeding preload that silently did nothing (pass 17), a deactivation rule
  read from a call that cannot show it (pass 21), a first design that changed a comparison column it should not have
  (pass 22). Each is in its report, with what caught it.

## 6. The evidence machinery
What makes the numbers checkable, built in these months and all exercised in CI on every push:
- **the claim register** with statuses V, S, E, U and a crux register mapping rows to the thesis's eight questions;
- **run identity**: every producer of record is listed with its input scope; a run carries a stamp (commit, dirty
  flags, scope hash, toolchain); results reach the tree only through a promote step that refuses a dirty or mismatched
  run (WM-2 A1, A2, A4);
- **generated documents** (dashboard, result cards, presentation, gas charter, feature matrix, test register, mode
  classification, the TDP's three generated documents) each with a `--check` that fails on drift, and probes in CI that
  show the checks fire;
- **the stale-figure checker**: a list of superseded values with their replacements, run over every tracked document;
- **the grand runner**, run last in every pass that changes code: smoke, L1, the Hardhat tree, the Python layers, the
  demos, with a report that the dashboard reads.

The guard count grew from passes 12 to 24; the honest measure of their worth is the number of times they fired on real
mistakes, which the reports record (pass 22 alone: three).

## 7. Phase 2
Phase 2 is the programme after the thesis, kept as documents until the defence (decision D-13 default). It has a
charter and protocol, an idea register of 26 anchored ideas, three author-designated focuses (on-chain storage and the
identity-dependent transaction; chains and databases; interaction modes), each with capture, analysis, plan and a
first executed step, a scope reconciliation by an academic adviser, and two deep-dive briefs with every source fetched
at origin. The briefs' main finding is that the IDTx mechanism is not new (ERC-3643 and guarded transactions precede
it), which moves the idea's value to its experiments; that is the author's decision (sheet §D).

## 8. What is open
- **Decisions:** all on one page in `docs/DECISION_SHEET_2026-10-20.md`. N-23, the AI-use statement, comes first.
- **WM-2:** nine of twenty steps done. Next: an independent check of passes 16–22 by a different assistant model
  (brief and start prompt in `docs/milestones/check_passes_16-22/`), then A3 and A3b (the re-runs that become the
  thesis's numbers), A6 (the harness re-run), B3 (the latency charter), D1 (the chapters).
- **Deferred items:** `docs/MILESTONE_NEXT.md`, 19 open, among them the Sepolia witness (N-11), SUMO (N-4) and the
  chain-backed conformance run (N-24).
- **Known limitations the thesis will state:** the testbed's unsalted VIN hash (D64, to be fixed after the defence
  with a uniqueness mechanism designed first), the one-chain-one-host conditions, and the self-scored internal W3C
  checker beside the external suite's result (#4, #24).

## 9. Reading this report
Every number with a `#` is a register row; the row's conditions and status apply. Counts of records (reports, defects,
tests) are from the files named in the header at the commit that wrote this draft. Where a figure has moved since July,
the register's history keeps the old value; this report quotes only the current one.
