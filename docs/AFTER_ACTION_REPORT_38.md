# After-Action Report 38 — Integration with the Other Sessions, the NatSpec Re-run, D2 Recorded, the TDP Corrected

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-24, after report 37 closed (CI green on `165db04`). **Brief (the author, 2026-10-24):** correct the
TDP from its review; leave RSU-to-RSU messaging out of scope and say so; integrate with the other code sessions;
continue.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| I1 | Take the sync of PR #17 (the default branch's NatSpec pass, contract references and Roots documents, via the layer-5 branch) into this branch | merge clean; Hardhat suite passes; document checks pass |
| I2 | **Re-run of record after the NatSpec pass.** It changed comments in 19 contract sources; the Solidity metadata hash is part of the deployment bytecode, so deployment gas moves. Re-run every result family whose stamp then reads "code changed since", as A3b did: one clean commit, one producer at a time, compared with the committed file; a moved value restates its register row with the old value as history | stamp inventory "code changed since" reads `no` for every V row's result |
| D2 | Record the author's decision D2-a: RSU-to-RSU messaging is out of scope, stated in the decision records, the scope log, crux C3, WM-2 and chapter 6 | the statement is in each place |
| T15 | Correct TDP-001, 003, 007, 008 and 009 from `docs/tdp/REVIEW_2026-10.md`, each with a revision letter; add layer 5 | every stale and mismatch item of the review fixed or answered; TDP checks pass |
| I3 | Sync the result back toward the default branch (PR #16's route) and record the integration state | the other sessions can take it |
| R | Records, grand run, CI | CI green on the closing commit |

## 2. Execution log
- 2026-10-24 — report opened.
- **Integration state at the opening.** Since report 37 the default branch took PRs #14 and #18 (the Roots thread
  G-R1) and #15 (a NatSpec pass over the contracts with a contract reference, `docs/smart-contracts/`). Open: #13
  (IDTx phase 1, another session), #16 and #17 (the layer-5 branch syncing both ways), #19 (the TSR patch series v2).
- **I1.** The layer-5 branch at `7a59058` already holds the default branch and this branch's `1fba094`, so merging it
  is PR #17's content. Merge clean, no conflicts. Hardhat: 563 passing, 34 pending. The test register regenerated with
  two moved values.
- **Finding: a comments-only change moved results of record.** The NatSpec pass changed no code line, but no Hardhat
  configuration sets `bytecodeHash: "none"`, so each contract's metadata hash, and with it the deployment bytecode,
  changed. The gas benchmark, run on the merged tree into the result file and restored from git afterwards (not
  promoted), moved three of its cells, each by 12 gas: ERC-721 deploy 2,787,288 to 2,787,276, ERC-735 create
  1,757,881 to 1,757,893, MOBI-VID-V2 deploy 4,370,878 to 4,370,866. The L1 matrix moved two cells by 12 gas. A
  zero byte of the old hash became non-zero or the reverse, at 4 or 16 gas per calldata byte. No other cell moved; the
  33.7× creation ratio is unchanged. The default branch merged the pass without a re-run, so its register quotes the
  old values too.
- **I2, the proof that the pass changes no behaviour.** Both commits (`1fba094` and the merge) compiled in all three
  projects. Every artifact's creation and runtime bytecode was compared with the trailing metadata removed
  (`tools/run_identity/bytecode_equiv.py`, shown to fire on a one-byte change):

  | Project | Artifacts | Differ only in the metadata hash | Differ beyond it |
  |---|---|---|---|
  | `1_blockchain-identity` | 19 | 17 | 0 |
  | layer 5 (`hardhat.zkp.config.js`) | 5 | 2 | 0 |
  | `cv2x-testbed` | 3 | 3 | 0 |

  So nothing that executes the contracts can behave differently; only deployment gas sees the change.
- **I2, what re-runs and what does not (the orchestrator's default, stated as such).** The merge flipped 23 result
  families to "code changed since". Re-running the testbed's latency families for a comments-only change would replace
  each run of record with a new run that differs only by host noise, so they are not re-run: their claims contain no
  deployment gas (the files record a deploy figure only in their environment header). `check_stamps.py` gains
  `COMMENT_ONLY_COMMITS`, a sibling of the existing stamp-only list: a listed commit is verified line by line (in
  `.sol` files every changed line is a comment or blank; compiled artifacts and bytecode files differ only in the
  metadata; debug files only in their build-info pointer), and it exempts only the result prefixes named
  (`cv2x-testbed/`), which then read "no (comment-only)". Shown to fire: listing the C2 commit `92cc4d5` fails the
  check on its first code line. The gas families and the harness re-run.
- **I2, the re-run (one clean commit, `963439a`, one producer at a time, 13:00 to 13:25 UTC).** Gas benchmark and
  its 30-run statistics, the MOBI backend sweep, scaling, I4 (one run and seeds 1 to 30), the pseudonym pool, the
  security scenarios and matrix (attack results through the promote step), and the metrics harness in-process and over
  HTTP-RPC with its analysis. Every step exited 0. What moved, all by the metadata hash in deployment code:

  | Cell | Before | After | Register |
  |---|---|---|---|
  | ERC-735 create (benchmark, harness C1, security Sybil proxy) | 1,757,881 | 1,757,893 | #25, #34 |
  | MOBI-VID-V2 deploy | 4,370,878 | 4,370,866 | #25 |
  | ERC-721 deploy (benchmark, harness shared deploy) | 2,787,288 | 2,787,276 | #34 |
  | ERC-735 lifetime, scaling Exp. B (band 6,724,999 to 16,659,210) | 11,692,092 | 11,692,104 | #26 |
  | ERC-735 lifetime, harness 17-event lifecycle | 5,797,549 | 5,797,561 | #35 |

  Batch cells scale with the batch (+120 for 10, +1,200 for 100). No other gas cell moved in any family; the 33.7×
  spread, the rankings and #36's dominance sets and frontier are identical. One cell outside the change also differed:
  the MOBI third-party attestation receipt in the backend sweep, 222,058 to 222,070, inside the range #28 already
  records (its signed message includes the block time, so its calldata varies run to run).
- **The harness's latency moved by host noise, so rows #31 and #39 are restated** from the new run, with the old values
  as history (h = 50 ERC-1056 median 91.113 to 85.585 ms in-process). Both rows are descriptive only. Finding: #39's
  latency sentence was older than the run it cited (the file read 169.079 ms where the row said 162.5); A5's check had
  missed it because it reads only bold figures. Result cards #31 and #39 updated by their generator's own check.
- **Old values in citing documents.** Five new stale-figure entries; 12 files outside the thesis corrected; the
  thesis hits join the pending list for WM-2 D1 (33 pending in all); `docs/phase2/reviews/` joins the history globs
  (a dated review keeps its day's figures). The RPC run's analysis step wrote 16 files that the run of record never had;
  they were removed, so the run's file set is unchanged.
- **A new CI gate, so this cannot recur silently.** The NatSpec pass reached the default branch with CI green while it
  had moved three register values, because "code changed since" was reported, never enforced. `check_stamps.py
  --check-coverage` (run by CI) now fails when any stamped result of record, or run directory, reads "yes", unless its
  commits are listed as stamp-only or comment-only, or it is in `KNOWN_STALE` with a reason. Five entries are listed;
  one, #26's density sweep of 2026-10-04, carries "reason to be confirmed" (task T-17). Shown to fire: before the
  promote it flagged the attack results, the RPC run and the scaling repeats.
- **D2.** Recorded as SC-24; chapter 6 §6.6.3 gains a threats-to-validity bullet stating that RSU-to-RSU messaging is
  out of scope and why (the one chapter edit made before D-1, at the author's explicit request); crux C3's gap, WM-2
  D2 (done), N-16 (closed), the note's status and the decision sheet's new §F record it.
- **T15, the TDP corrected.** A subagent applied the review's rows to TDP-001, 003, 007, 008 and 009 (11 of 13, 6 of
  6, 12 of 12, 16 of 17, 8 of 8; the skipped ones were already fixed or waited for this re-run and are now done here),
  each at revision B with a revision-history row; R-04 to R-07 retired, R-14 to R-18 and I-05, I-06 added; layer 5
  added throughout. Spot-checked here (#21 at 15.513 ms, the retirements). `check_icd.py`: 185 identifiers, 0 missing.
- **Integration: two sessions re-ran the same families.** When this pass came to push, the branch had moved: the
  session that relays syncs through the layer-5 branch had found the same NatSpec effect, re-run the gas families and
  the in-process harness first (`2c6799a`, harness `2026-10-24T12-29-26Z_7a59058`, 12:29 UTC on its own host), merged
  this pass's checker commit, and the author merged PR #17 into this branch. **Resolution, under report 33's rule of
  one run per producer and no re-roll:** the first run is the run of record. Wherever both sessions ran a producer,
  its results are taken; this pass's duplicate runs of those families are discarded (their gas agreed cell for cell,
  so nothing is lost). This pass's runs stay where it was the only one: the security scenarios and matrix (promoted,
  content unchanged), the I4 seeds study and the HTTP-RPC harness (`2026-10-24T13-13-44Z_963439a`).
  - The register takes the other session's rows #25 and #31 to #35; this pass adds what they had not: #26 and #35
    restated (their files read 11,692,104 and 5,797,561 but the rows still quoted the old values; A5's check missed
    it because the figures are not bold), #34's ERC-735 create, and #39.
  - **#39 can no longer compare the two runs' latency:** the in-process run of record and the RPC run come from
    different hosts (their in-process U3 median 14.4 ms is above this RPC run's 13.8 ms). The row keeps the RPC run's
    absolute values, descriptive only, and the gas identity, re-checked against their run: crud, lifecycle and batch
    tables identical, 18 of 18 common scale rows identical.
  - Their stale-figure additions are kept (the Roots G-R1 snapshots join the history globs); their chapter 5 and 7
    corrections of 1,757,881 clear that pending entry. Result card #31 follows #31 (153.786 ms on their host).
  - **Process finding:** two sessions repeated a re-run because neither could see the other's work in progress. The
    master plan's §3.4 now asks a session to push an opened report before a re-run, so the other sees it on fetch.
- **CI at `243c2bb`: the contracts job red** on the interface-control check: TDP-003 had gained a backticked commit
  id, which the check reads as an identifier. Written as plain text.
- **Grand run (last), at `243c2bb` plus that fix.** The first attempt failed in its Python stage: this container's
  system cryptography could not load (`cffi` missing), not a test failure; with `cffi` installed, **ALL OK**: smoke 11,
  L1 99, Hardhat 563, Python layers 376, 92 demos / 1,758 steps. Generated documents regenerated.
- **CI green on `6a574a2`** (all four workflows).
- **I3, B-1 (the author's "integrate", read as the recommended integration steps).** `claude/exploration-plan` merged
  (docs only; its baseline line marked as the 2026-10-15 history). `claude/system-blueprint-diagrams-fd8apg` is **not**
  merged: a trial merge in a worktree showed its 23 generated sheets carry superseded values in their SVG text (0.153 ms
  in five places, #21's old PKI 0.253 ms, #32-derived P* rows), which the stale-figure checker cannot see because it
  reads Markdown only (WM-2 G item T-F16). Its X-series tables regenerated cleanly from current data and both of their
  README observations still hold, so the work is sound; it needs a refresh of the sheet sources against the register
  before merging (new task T-18). B-2 to B-4 stay as recommended: simulation visuals and the TSR series kept apart
  (the TSR session has PR #19 open to the default branch), X1 documents only when wanted.

## 3. Closing
The pass did what the author asked and one thing the integration forced.

- **Integration.** This branch now holds the default branch's NatSpec pass, contract reference and Roots thread, the
  other session's re-run, and the exploration workspace. The first re-run of each producer is the run of record; this
  pass kept its own runs only where it was alone (security, I4 seeds, HTTP-RPC). The way back to the default branch is
  PR #16's route, which the relaying session maintains.
- **The finding.** A comments-only change to the contracts moved five register gas figures by 12 gas through the
  metadata hash, and reached the default branch with CI green. The bytecode is proved identical apart from the hash, the
  gas families are re-run and the rows restated, and **CI now fails when a result of record describes code the trunk no
  longer has**, unless the commit is proved stamp-only or comment-only or the result is listed with a reason.
- **D2** is recorded as SC-24 and stated in chapter 6 and crux C3. **The TDP** is at revision B with layer 5 in it.

**Grand run** ALL OK (Hardhat 563, Python 376, 92 demos / 1,758 steps). **New tasks:** T-17 (confirm #26's density
sweep), T-18 (refresh the blueprint sheets, then merge), T-19 (stale-figure checker on SVG). **Still waiting on the
author:** N-23, the report's reader, D-1, the check session, B-2 to B-4.

**CI green on `18fb9f8`** (all four workflows). Report 38 is closed.
