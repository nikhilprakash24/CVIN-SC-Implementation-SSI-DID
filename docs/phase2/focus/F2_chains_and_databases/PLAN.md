# F2 Plan: Substrate Experiments (Pre-Registration Draft)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F2, plan). **State:** a draft, not locked, nothing run (principle 4).
**Builds on:** `ANALYSIS.md`; the database backend `phase2/backends/` (EXECUTION.md).
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-18, AR-23, AR-24, AR-25, AR-35, AR-41

**In the thesis, this plan is one future-work paragraph** (review §4.1). Build waves come after the defence (D-13).
Every prediction below is fixed before any run; a cell marked "at lock" is fixed when the plan is locked (F2-S4), before any run.

## 1. Measures
| Measure | Definition |
|---|---|
| Write latency | wall-clock median and p95 per operation, from the call to a durable commit: the receipt on a chain, the commit's return on the journal. n = 50 per operation after 3 discarded warm-ups, as #33. One host, one run, all substrates in the same run |
| Journal configuration | file-backed, not `:memory:` (the backend's default). SQLite's `synchronous` and `journal_mode` are read by PRAGMA at run time and recorded |
| Permissioned-chain configuration | consensus, validator count and block interval T_b, recorded. Latency includes inclusion; the finality rule is named |
| Execution gas | the receipt's `gasUsed`, with the compile target and the execution fork of each network recorded (`docs/MEASUREMENT_CONDITIONS.md` §5.A) |
| Undetected window | the number of most recent journal entries whose rewrite or truncation an auditor holding the last anchored head cannot detect |
| Fee components on a rollup | L2 execution fee (execution gas × L2 gas price) and L1 data fee (as the rollup's receipt reports it), each dated |

## 2. Experiments
| ID | Question | Design | Needs |
|---|---|---|---|
| **E-F2-1** | The same lifecycle, four substrates: what does each cost and buy? | the M4 operation sequence (#33) through the in-memory registry, the file-backed SQLite journal, the local chain, and a permissioned EVM chain; plus a third-party verification test per substrate: rewrite one entry, truncate the tail, and ask who detects it | a permissioned EVM client installed (author decision P2-D9) |
| **E-F2-2** | What window does anchoring a journal leave open, and what does one anchor cost? | journal head anchored every N entries, N ∈ {1, 10, 100}, on the local chain; rewrites and truncations at every position relative to the last anchor | the backend's anchoring step (F2-S3) |
| **E-F2-3** | Does execution gas hold on a public network within the stated tolerance? | the Phase 1 validation script (`validate_sepolia.js`) on Sepolia | secrets for N-11 |
| **E-F2-4** | What does a rollup change, per cost component? | the nine-standard benchmark on one EVM-equivalent rollup testnet, at a named fork | access to a rollup testnet |

## 3. Predictions, verdict rules and kill criteria
| ID | Point prediction and band | Verdict rule | Kill criterion |
|---|---|---|---|
| **E-F2-1** | (a) Journal write median: above the in-memory registry and below the local chain, and nearer the registry on a log scale, in the same run. (b) Permissioned-chain write median: the local chain's write median plus T_b / 2 (mean wait for the next block), band [local median, local median + T_b]. (c) Detection: the in-memory registry detects nothing; the journal alone detects a trigger-bypassing edit, but neither a full re-derivation nor a tail truncation; the anchored journal (once F2-S3 exists), the local chain and the permissioned chain detect both, for entries before the last anchor | (a) PASS if log(journal ÷ registry) < log(chain ÷ journal). (b) PASS if the median falls in the band. (c) PASS if every detection cell matches. Each part is reported separately, FAIL as FAIL | the fourth substrate is dropped, and reported as not run, if P2-D9 is still "no" at lock; the experiment stops if the journal fails parity with #33's sequence |
| **E-F2-2** | (a) Undetected window: exactly N − 1 entries at the worst instant (just before the next anchor), the write-side twin of the verifier's k − 1. (b) Every rewrite or truncation of an entry at or before the last anchor is detected. (c) Anchor gas: point computed by hand from the anchor contract's source at lock; band ±100 gas (the head hash is random calldata, AR-18) | PASS if (a), (b) and (c) all hold for every N. Amortised gas per entry (anchor gas ÷ N) is arithmetic: reported, no verdict | stop if the post-anchor detection test passes without the anchor (the F2-S3 gate), since the experiment would then measure nothing |
| **E-F2-3** | Every operation's Sepolia `gasUsed` within ±100 gas of its M1 value (`validate_sepolia.js:59`); every non-zero difference a multiple of 12 gas (calldata bytes, #47). Fees reported in the network's units at the dated price, never compared | PASS if every difference is within 100 gas. A difference that is not a multiple of 12 is reported as a pre-state or fork effect and named | the experiment is future work if no funded key and endpoint (N-11) exist before the defence; the §2 gas wording in `ANALYSIS.md` holds either way |
| **E-F2-4** | (a) Execution gas: each cell within ±100 gas of #34, so the ranking of standards by execution gas is unchanged. (b) L2 execution fee: the same ranking as (a), since one gas price applies within a run. (c) L1 data fee: ranks with calldata bytes (`1_blockchain-identity/results/metrics/latest/tables/crud_calldata.csv`). For identity creation (C1), ERC-735 (8,402 bytes) and ERC-725xy (7,817 bytes) carry the two largest L1 data fees, then ERC-4337 (3,749) and ERC-725 (2,226). (d) Total fee: reported and dated, with no prediction, since it depends on both prices on the day | (a) PASS if every cell is within 100 gas. (b) PASS if the rankings match. (c) PASS if the C1 ranking by L1 data fee equals the ranking by C1 calldata bytes, except between equal byte counts (ERC-1155 and LSP8, 132 bytes each). A reordering by the rollup's compression is a FAIL, reported | stop if the rollup is not EVM-equivalent at a named fork: (a) and (b) then do not apply, and the run is reported as a different VM |

## 4. Steps
| Step | Work | Gate |
|---|---|---|
| F2-S1 | **done:** the SQLite journal backend (EXECUTION.md). Tests: see `phase2/backends/test_sqlite_lifecycle.py` (updated for AR-22) | tests pass |
| F2-S2 | register the backend in the parity experiment as a third backend, behind the same interface; stamp and promote | producer registered before any run |
| F2-S3 | anchoring: write the journal head to a small anchor contract every N entries; a test that a rewrite or truncation before the anchor is detected | test fails without the anchor |
| F2-S4 | fix the "at lock" cells, lock this plan; then run E-F2-1 (three local substrates first) and E-F2-2 | pre-registration committed first |
| F2-S5 | E-F2-3 and E-F2-4 when the author's decisions allow | N-11, P2-D9 |

## 5. Risks
| Risk | Mitigation |
|---|---|
| Comparing an in-process database with a networked chain flatters the database | report both, and add the file-backed journal as a persistent, transactional middle point; state that the in-memory registry is a lower bound (#33 caveat) |
| A permissioned chain's latency depends on its consensus settings | fix and record block interval, validator count and consensus; report as one configuration, not "private chains" in general |
| Cross-network gas differs by calldata, pre-state or fork | report within the 100-gas tolerance, with both forks named (`ANALYSIS.md` §2) |
| Public-network fees change daily | fees are reported dated and never compared across dates |
