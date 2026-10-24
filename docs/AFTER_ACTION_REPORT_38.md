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
