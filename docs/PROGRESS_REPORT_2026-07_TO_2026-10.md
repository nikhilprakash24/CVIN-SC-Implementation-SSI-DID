# Progress Report: July to October 2026

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-20 (after-action report 24), draft 1; **draft 2
2026-10-24** (after-action report 37, unblocked item U11), which adds reports 25 to 37 and updates every figure.
**Reader:** *[to be set by the author: supervisor, committee, or a successor taking over the repository; the depth
of §4 and §6 changes with it]*. **AI-use statement:** *[to be inserted once decision N-23 is taken; see
`docs/DECISION_SHEET_2026-10-20.md` §A]*.
**Sources:** the after-action reports 02–37 (`docs/AFTER_ACTION_REPORT_*.md`), the claim register
(`docs/MEASUREMENT_CONDITIONS.md`; every number below with a `#` is quoted from it and only from a row of status V),
the defect log, the milestone and audit records, the handbacks, and the git history (the generated appendix
`docs/PROGRESS_APPENDIX_2026-07_TO_2026-10.md`). **Extends** `docs/DEVELOPMENT_HISTORY.md`, which ends at July 2026.
The whole programme on one page, with its plan and open questions: `docs/MASTER_PLAN_2026-10-24.md`.

## 1. Summary
Between the July milestones (v0.7.0, v0.8.0) and today the project did four things. It turned a set of results into
a system of record: a claim register in which every quoted number carries its source, its conditions and its status,
and generated documents that CI rejects when they drift from the files they are built from. It filled the thesis's one
empty question, infrastructure messaging, with a pre-registered experiment that was designed, built, measured, reviewed
adversarially, hardened and re-run, with verdicts reported as they fell. It found and fixed its own defects, 66
logged so far, 42 fixed, several of them in work done during these months rather than before them. And it joined
two parallel lines of work, one of which added a fifth layer (zero-knowledge VIN proofs and the agent-wrapped
identity), into one trunk, then re-ran every result whose code had changed from clean commits.

The numbers the thesis now rests on are in the register (62 rows, 45 verified). The test base at the last full run
is 563 Hardhat tests, 376 Python layer tests and 92 demos over 1,758 steps, all passing
(`sandbox/grand/report/GRAND_REPORT.md`). Two work milestones were defined: the first closed under audit, the second
is 15 of 20 steps in. Phase 2, the research programme after the thesis, exists as documents.

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
| 07 | 10-06 to 10-09 | the two lineages of that time reconciled into one trunk (`bd90004`); D27; lifecycle-parity re-run | report 07 |
| 08–11 | 10-09 | the plan of 2026-10-09; infrastructure messaging (C3) designed, pre-registered, built, measured; SUMO trace; adversarial review of passes 9–10 and the run-identity fixes | reports 08–11 |
| 12 | 10-10 | work milestone WM-1 closed: plan review, backward fixes, milestone report, an audit by four briefs, presentation draft | report 12; `docs/milestones/` |
| 13–15 | 10-10 to 10-14 | WM-2 A1 (stamp inventory), A2 (one stamp helper with per-producer scope), A4 (the promote step); Phase 2 opened; hand-off to a different assistant model | reports 13–15 |
| 16 | 10-14 | WM-2 C0 (verifier v3, D51); Phase 2 focuses F1–F3 with a writing team and an academic review | report 16 |
| 17–19 | 10-14 to 10-15 | WM-2 B1 (seeded randomness, I4 over declared seeds), B2 (the gas charter), C3 (#32 and #37 on one host); result cards; contribution record | reports 17–19 |
| 20 | 10-15 | the Technical Data Package, a parallel pass in another session | report 20; `docs/tdp/` |
| 21–22 | 10-15 to 10-18 | WM-2 C1 (did:ethr resolution reads the chain), C2 (attestation restricted to owner or delegate, D54) | reports 21–22 |
| 23–24 | 10-20 | Phase 2 session 3 (two deep-dive briefs); draft 1 of this report, the decision sheet, the pre-push guard | reports 23–24 |
| 25, 27 | 10-21 to 10-22 | the TDP session again: the thesis adaptation map onto chapter 3; the requirement-to-test trace and the interface-control gate in CI | reports 25, 27 |
| 26 | 10-20 to 10-23 | chapter 2 sections and chapter 6 §6.8 drafted from the briefs' sources, later absorbed as §2.7 and §6.8 | report 26 |
| 28–31 | 10-22 (a second workstream, numbered on its own branch and renumbered at the merge) | layer 5 (zero-knowledge VIN proofs, the agent-wrapped identity, three CI jobs); the clone lineage merged (PR #3); layer 5 entered in the thesis record (#55 to #61, RQ5); chapter 2 written | reports 28–31 |
| 32 | 10-22 | **one trunk** (Plan 5): the workspace merged as the primary lineage, 43 conflicted files resolved by a written rule, register rows renumbered | report 32; `docs/LINEAGE_RELATION_2026-10-22.md` |
| 33 | 10-23 | WM-2 A3b and A6: every result family flagged "code changed since" re-run on the one trunk from clean commits; the metrics harness re-run of record | report 33 |
| 34 | 10-23 | WM-2 A5: stable claim ids, and every quoted number in a V row checked by script against its result file | report 34 |
| 35 | 10-23 | WM-2 B3 (the latency charter; four rows relabelled descriptive only) and A7 (all 376 Python tests in the test register) | report 35 |
| 36 | 10-23 | mutation probes for the C1 and C2 tests: 8 of 8 and 9 of 9 mutants killed, one test gap found and closed | report 36 |
| 37 | 10-24 | the unblocked list: CI dependencies pinned, the I-05 model as code, a read-only audit of the chapters and of the TDP, the stale-figure checker extended, the RSU-to-RSU note, this draft, the master plan | report 37 |

## 4. What was measured, re-measured and withdrawn
The register's discipline is that a number enters a chapter only with a row of status V, and that a superseded
number stays as history with an arrow to its replacement.

**Established, and re-confirmed on the one trunk.** The nine-standard gas table (#25): creating an identity spans
52,216 gas (CVIN-Combined) to 1,757,893 (ERC-735), 33.7×. V2V credential verification on the warm path at 0.142 ms,
95 % CI [0.141, 0.143] (#27), from the A3b re-run of 2026-10-22; the earlier 0.153 ms was the pre-merge run. 43 of 43
attack scenarios defended, each reverting with its documented reason (#28).

**Re-measured, and reported as it fell.** The infrastructure experiment I1 (#44): the ratio of SPaT verification to
BSM verification, against a pass band of [0.80, 1.20] pre-registered before the first run. The run of record of
2026-10-14 gave 1.226 [1.219, 1.238], outside the band and not falsified (the falsification line is 2.0). The A3b
re-run gave 1.197 [1.193, 1.201], inside it. The register reports I1 as **at the edge of the band**: the pre-registered
verdict is not re-rolled by a later run that happens to pass. The MOBI attestation cost moved twice as its security was
tightened, first when the signature check was added and again when the owner-or-delegate check of pass 22 was added;
its execution gas is now 198,694 (#28).

**Withdrawn or relabelled.** The resolver latency row of the early register was superseded because the resolver
synthesised its document rather than reading a chain (M0 row, status S; pass 21 changed the resolver). The cross-run
read-mode ratio of Phase 2's first draft was withdrawn by the academic review (report 16). "Throughput" was cut from
RQ1 by scope decision D-3 when its only row was unsupported; that row (#39) has since been re-run and is V, but the
latency charter marks its latency descriptive only, because the harness records no host (deferred item N-26). Four
latency rows in all (#26, #31, #39, #57) are now quoted as descriptive only, never compared across runs or hosts.

**Host dependence, made explicit.** Rows #32 and #37, the freshness experiments, disagreed on absolute times. Pass 19
re-ran both configurations at their own code on one host, under a decision rule committed first, and attributed the
difference to the host (#52). The lesson is now a rule, and since pass 35 a CI check: a latency row names its host,
and two rows from different hosts are never compared on absolute values.

## 5. Defects: found where, by what
The defect log holds 66 entries (D1–D66), 42 of them fixed. They were found by several instruments, and the
distribution matters more than the count.

**Every High-severity defect, with its finder.**

| Defect | What | Found by | Status |
|---|---|---|---|
| D1 | `CVINVehicleDIDRegistry` service-endpoint and delegate functions unreachable | the verification passes, 09-24 | fixed |
| D4 | the ERC-1056 provider returned a placeholder key, so chain verification could never succeed | the verification passes | fixed |
| D6 | an ERC-1155 self-transfer deleted the VIN mapping | the verification passes | fixed |
| D7 | an issuer that is also an approved operator could move the birth certificate | the sandbox demos, 10-04 | fixed |
| D10 | DIDs returned without `0x` on the address | the sandbox demos | fixed |
| D11, D11b | a MOBI message verified against the key embedded in the message; the vehicle key never anchored | the sandbox demos | fixed |
| D13 | case-sensitive VINs minted a second identity | the sandbox demos | fixed |
| D18 | an unbounded validity value | the sandbox demos | fixed |
| D21 | `DIDRevoked` severed the change chain | the sandbox demos | fixed |
| D22 | claim changes bumped `changed` without an event | the sandbox demos | fixed |
| D25 | the claim holder accepted an impostor issuer and a claim for another VIN | the sandbox demos | D25a and D25b fixed; D25c (the signature scheme) an open author decision |
| D28 | SPaT fields not bound to the RSU's credential | the adversarial review, 10-09 | fixed |
| D29 | replay inside the 1 s freshness window accepted | the adversarial review | fixed |
| D43 | register V rows kept pre-merge harness values | the WM-1 audit, 10-10 | fixed |
| D46 | H5 called "Pareto-optimal" without the scope #36 requires | the WM-1 audit | fixed in the register; chapters 1 and 6 still carry it (the chapter audit of report 37) |
| D51 | key validity decided against the verifier's wall clock instead of chain time | the WM-1 audit | fixed in pass 16 |

**The other instruments.**
- **The academic review of Phase 2** (pass 16): 41 findings, 40 fixed, which cut the IDTx count from 25 implicit
  instances to 4 under one definition, and found D64, the unsalted VIN hash in the testbed.
- **The WM-1 audit** also found D54 (medium): attestations open to any role-holder, fixed in pass 22.
- **The passes' own gates** (passes 17–22): a seeding preload that silently did nothing (pass 17), a deactivation
  rule read from a call that cannot show it (pass 21), a first design that changed a comparison column it should not
  have (pass 22).
- **Mutation probes** (pass 36): a mutant that removed the revoked-identity check survived every behaviour test and
  was killed only by a gas pin. A new test closed the gap, and probes now run behaviour tests only.
- **The checks of report 37**: A5's correction of #27 had not reached the citing documents, and the old V2V figures
  stood in 24 files, the README among them. The documents outside the thesis were corrected; the thesis chapters wait
  on WM-2 D1. The read-only chapter audit and TDP review list every other figure that has drifted.

## 6. The evidence machinery
What makes the numbers checkable, built in these months and all exercised in CI on every push:
- **the claim register** with statuses V, S, E, U and stable claim ids (`docs/testing/claims.yaml`), every quoted
  number in a V row checked by script against its result file (A5), and a crux register mapping rows to the
  thesis's eight questions;
- **run identity**: every producer of record is listed with its input scope; a run carries a stamp (commit, dirty
  flags, scope hash, toolchain); results reach the tree only through a promote step that refuses a dirty or
  mismatched run (WM-2 A1, A2, A4);
- **charters**: the gas charter (which cells vary and why) and the latency charter (which latency rows may be
  compared), both generated and checked;
- **generated documents** (dashboard, result cards, presentation, feature matrix, test register, mode
  classification, the TDP's generated documents) each with a `--check` that fails on drift, and probes that show the
  checks fire;
- **the stale-figure checker**: superseded values with their replacements, run over every tracked document, now
  with a visible "pending" class for known hits that wait on a decision;
- **mutation probes** for the IDTx, the verifier, the zero-knowledge layer, the D54 fix and the chain resolver;
- **the grand runner**, run last in every pass that changes code, and **the pre-push guard**, which runs CI's
  document checks locally;
- **CI**: 12 jobs in four workflows (11 until the blueprint data check of 2026-10-31), with the Python packages pinned to the versions the grand run passed on.

The honest measure of the guards' worth is the number of times they fired on real mistakes, which the reports
record (pass 22 alone: three; pass 37: the stale V2V figures in 24 files).

## 7. Phase 2
Phase 2 is the programme after the thesis, kept as documents until the defence (decision D-13 default). It has a
charter and protocol, an idea register of 26 anchored ideas, three author-designated focuses (on-chain storage and the
identity-dependent transaction; chains and databases; interaction modes), each with capture, analysis, plan and a
first executed step, a scope reconciliation by an academic adviser, and two deep-dive briefs with every source fetched
at origin. The briefs' main finding is that the IDTx mechanism is not new (ERC-3643 and guarded transactions precede
it), which moves the idea's value to its experiments; that is the author's decision (sheet §D). The freshness brief's
model is now code (`docs/phase2/briefs/i05_model.py`), so its out-of-sample prediction (on host 3, the probe refresh
reaches the budget at k = 12 to 14) is fixed before any measurement.

## 8. What is open
- **Decisions:** all on one page in `docs/DECISION_SHEET_2026-10-20.md`. N-23, the AI-use statement, comes first;
  D-1 (Scope v3) sits on the path to closing WM-2. New since draft 1: D2 (RSU-to-RSU messaging, recommendation scope
  out, `docs/design/RSU_TO_RSU_NOTE.md`).
- **WM-2:** 15 of 20 steps done. Left: D1 (the chapter edits, which the audit of report 37 has scoped), D2 (the
  author's decision), E1 (the independent check by a different assistant model, brief and start prompt in
  `docs/milestones/check_passes_16-22/`, not yet run), F1 (presentation draft 2), E2 (the close audit).
- **Unmerged work:** five research branches in the repository hold commits not on the trunk; none has been reviewed.
- **Deferred items:** `docs/MILESTONE_NEXT.md`, among them the Sepolia witness (N-11), SUMO (N-4), the chain-backed
  conformance run (N-24) and the harness host record (N-26).
- **Known limitations the thesis will state:** the testbed's unsalted VIN hash (D64, to be fixed after the defence
  with a uniqueness mechanism designed first), the one-chain-one-host conditions, and the self-scored internal W3C
  checker beside the external suite's result (#4, #24).

## 9. Reading this report
Every number with a `#` is a register row; the row's conditions and status apply. Counts of records (reports, defects,
tests) are from the files named in the header at the commit that wrote this draft. Where a figure has moved since July,
the register's history keeps the old value; this report quotes the current one, and names an old one only to say it
was replaced.
