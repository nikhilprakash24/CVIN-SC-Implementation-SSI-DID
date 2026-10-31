# F2 Analysis: Public and Private Blockchains, and Other Databases, for Vehicle Identity

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F2, analysis). **Builds on:** `CAPTURE.md` (verified),
`docs/phase2/SCOPE_RECONCILIATION.md` §3.2. **Binds:** `docs/phase2/README.md`. **Numbers:** register rows and the committed files named beside them.
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-18, AR-19, AR-20, AR-21, AR-26, AR-27, AR-41

**Terms used below.** A register row (#n) is a row of the claim register, `docs/MEASUREMENT_CONDITIONS.md`. Condition
M1 is a single local Hardhat node. Automine means that node mines each transaction into its own block at once.

## 1. The question
F2 asks the question Phase 1 held fixed: **on which kind of ledger or database should vehicle identity live**, and
which Phase 1 results survive a change of substrate? Phase 1 compared nine identity *standards* on one ledger: a
single local Hardhat node (condition M1). Its other substrates are an in-memory registry and a PKI baseline.

In F2, **substrate means the ledger or database itself.** The capture shows a naming trap to avoid from the start.
Three Phase 1 words sound like a permissioned ledger, and none of them means one:

| Word | What it means in Phase 1 |
|---|---|
| "backend" | a contract standard on the same local chain (H4's five MOBI backends) |
| "substrate", in crux C1 | a standard |
| "permissioned", in the DID rubric | role-gated contracts |

## 2. What transfers from Phase 1, and under which conditions
Execution gas is identical only under four conditions, and cross-network gas is reported within a tolerance.
Fees, chain latency, finality and ordering results do not transfer.
Here k is a verifier's re-check interval: it asks the chain on every k-th message.
This section belongs in chapter 3, threats to validity.

**The gas statement.** Execution gas is identical for identical bytecode, calldata, pre-state and execution fork.
Intrinsic gas moves with calldata bytes, so cross-network gas is reported within a stated tolerance.

| Condition | Why it can fail on another network | Repository evidence |
|---|---|---|
| Identical calldata | intrinsic gas charges zero and non-zero calldata bytes differently (EIP-2028); a new network gives new addresses, and addresses sit in calldata | #47: gas varies by multiples of 12 when the RSU address is random; `1_blockchain-identity/scripts/validate_sepolia.js:59` tolerates 100 gas for this reason |
| Identical pre-state | a new deployment starts from different storage: slots cold or warm, zero or non-zero | #47 (its key-anchor cell includes first writes to the identity's storage) |
| Identical execution fork | the harness is compiled for `cancun` and executed under `osaka`; the target network's fork must be named | `docs/MEASUREMENT_CONDITIONS.md` §5.A |
| Identical gas schedule | an L2 can add a data fee or change the schedule; a permissioned EVM on an older fork may reject `cancun` bytecode (recalled: PUSH0, MCOPY; check at source) | none; no L2 or permissioned chain was run |

For the orchestrator: the register's §1 M2 line says M1 gas "must match to the unit".
That wording conflicts with this section and with the 100-gas tolerance of the Sepolia script.

| Phase 1 result | Holds on another EVM ledger? | Condition |
|---|---|---|
| Execution gas per operation (#25, #34, #35, #49, #50) | **identical** under the four conditions above; **within 100 gas** across networks | the conditions table above |
| Fees (gas × price) | **no** | price is set by each network's fee market, or by its operator on a private chain |
| Latency and finality of chain operations (#21, #31, #33, #39) | **no** | Phase 1 has automine on one local node: no consensus, no block interval, no network |
| V2V and V2I verification latency (#27, #44) | **does not depend on the ledger** | it is in-process (M0) and never touches a chain; its absolute value still depends on the host |
| Security results under the attack harness (#28) | **yes** for contract logic, where bytecode and fork are identical; **no** for ordering attacks; **new risk:** D52 | a single automine node has no mempool, so front-running and reordering were not testable. D52 (the ERC-1056 signed digest lacks the chain id) exists only once a deployment spans several chains |
| The k − 1 staleness bound (#46) | **yes, as a message count of the verifier's rule**, under three conditions | (1) #46 is M0, with no propagation delay. (2) On a chain with finality, the revocation instant is ambiguous: inclusion or finality must be named. (3) A reorg can undo an included revocation, so the bound holds from finality only |

## 3. A substrate taxonomy (drawn from literature, to be cited in chapter 2)
This table restates literature and holds no repository evidence.
Chapter 2 cites it at source (candidates in the review's §3.1: Xu et al.; Wüst and Gervais; Dinh et al.; Antonopoulos et al.).
In this table, L1 and L2 mean layer 1 and layer 2 of a public blockchain, not F1's storage loci.
BFT is Byzantine-fault-tolerant consensus.

| Substrate | Who writes | Who reads | Who can verify history | Finality | Cost model | Trust | Privacy |
|---|---|---|---|---|---|---|---|
| Public L1 (Ethereum mainnet; Sepolia as its test stand-in) | anyone who pays | anyone | anyone | inclusion first; economic finality after a protocol-defined number of epochs (value to cite at source) | fee market | the protocol and its validators | none by default: everything is public |
| Optimistic rollup | anyone, through a sequencer | anyone | anyone with the L1's data, once the challenge period has passed | soft confirmation from the sequencer; L1 finality after the challenge period | L2 fee plus L1 data cost | sequencer for ordering and liveness; the L1 and one honest challenger for safety | public |
| Validity-proof rollup | anyone, through a sequencer | anyone | anyone with the L1's data and the validity proof | soft confirmation; L1 finality once the proof is verified | L2 fee plus L1 data and proof cost | sequencer for ordering and liveness; the L1 and the proof system for safety | public |
| Validium | anyone, through a sequencer | holders of the off-chain data | only holders of the data, which the L1 does not receive | as the proof system | L2 fee plus proof cost | as a validity-proof rollup, plus whoever holds the data | the data is off the L1 |
| Permissioned EVM (a consortium chain with a BFT consensus) | members | members, or the public if published | members | immediate, under BFT | operator-set; can be zero | the consortium's honest majority | members only, unless data is published |
| Permissioned non-EVM ledger | members, through endorsement policies | channel members | channel members | immediate | operator infrastructure | the endorsers | channel-scoped |
| Conventional database | the operator | whom the operator serves | **only the operator** | immediate | infrastructure | the operator, fully | operator-controlled; erasure possible |
| Append-only, hash-chained database | the operator | whom the operator serves | the operator, or anyone given the journal, except for deletion at the tail | immediate | infrastructure | the operator, but rewrites need every later hash re-derived | operator-controlled |
| The same, with its head hash anchored on a public chain | the operator | as above | **anyone holding an anchored head** can detect a rewrite or a truncation before it; the N − 1 entries after the last anchor stay open | anchor finality | one anchor write per batch | the operator for content; the chain for history integrity | content private; the head public |
| PKI directory (certificate authority) | the CA | relying parties | the CA; certificate transparency logs where used | immediate | infrastructure | the CA | certificate fields public |

## 4. The two Phase 1 comparisons that already speak to F2
Two existing comparisons answer part of F2.
Database against chain (#33) shows what the chain costs on writes, and that a cache did not reach the database's band.
PKI against a chain-backed identity (#21, #27) shows where the chain belongs.

**Database against chain, the same lifecycle (#33).** #33 has two runs, and each number below names its run (D60).
The committed result file holds the disclosed 2026-10-04 re-run on the post-G-M bytecode (`cv2x-testbed/results/lifecycle_parity.md`).

| Operation | Centralized, median ms (re-run) | MOBI-VID-V2, median ms (re-run) | RPC calls | Pre-registered verdict |
|---|---:|---:|---:|---|
| birth, lifecycle event, ownership transfer | 0.0036, 0.0089, 0.0023 | 17.689, 14.629, 13.947 | 6, 5, 5 | ≥ 10× for writes: **PASS** ×3 (re-run 4.9e3×, 1.6e3×, 6.0e3×; first run ≈1,850 to 5,930×) |
| history query, uncached | 0.2627 | 114.222 | 39 | none |
| history query, cached copy | 0.2627 | 0.011 | 0 | "equal once cached", band [0.5, 2]: **FAIL** (re-run ratio 0.041; first run ratio 0.072) |
| history query, cached copy plus freshness probe | 0.2627 | 15.403 | 6 | none (`lifecycle_parity.md:60`) |

- **The writes.** On the re-run, the on-chain writes are 1.6e3 to 6.0e3 times slower than the in-process registry (first run: ≈1,850 to 5,930 times).
  The registry is in-process dictionaries, so these ratios are upper bounds (#33 caveat).
- **The cache.** The pre-registered "equal once cached" result FAILED.
  The cached read fell outside the band: 0.011 ms against 0.2627 ms, ratio 0.041 on the re-run.
- **Post hoc, not pre-registered:** the database's own serialisation sets its 0.2627 ms; without it the history query is 0.0007 ms (diagnostic row, `lifecycle_parity.md:54`; F2 capture §2.1(b)).
  This explains the FAIL after the fact and does not change it.
- **The cache's freshness cost.** A cache hit costs 0.011 ms and no RPC call, but it is fresh only as of its last fill.
  Checking it for freshness costs 15.403 ms and 6 RPC calls (`lifecycle_parity.md:60`).
- **What the chain buys (design argument, not a measurement).** A chain offers verification by parties who do not trust the operator.
  M1 has a single operator, so Phase 1 never measured this (F2 capture §4).
  Chapter 6 cites the argument from its literature (review §3.1, for example Wüst and Gervais).
- **What the baseline lacks.** It is in-memory, with no persistence, no caller authentication and no audit log (capture §1).

**PKI against a chain-backed identity, the same messages (#21, #27).** The chain belongs off the hot path, as Phase
1's cached design already places it. SSI here is self-sovereign identity, the chain-backed design.
The two rows come from different runs and conditions, so each is read within its own row only.

| Verification | SSI (chain-backed) | PKI | Row and condition |
|---|---|---|---|
| V2V hot path, warm, both in-process | 0.142 ms | 0.090 ms | #27, M0 |
| uncached ERC-1056, which reads the chain | 9.654 ms | 0.253 ms | #21, M0 (PKI) and M1 (ERC-1056) |

## 5. The design space the evidence points to: a hybrid by data class (design, cut to future work)
This section is a design proposal, not a finding; the thesis carries it only as future work (review §4.1).
Each class of data points to the substrate that meets its needs. "F1 L3"
and "F1 L4" are F1's storage loci: a commitment in state, and data off chain with an anchor on chain.

| Data class | Needs | Substrate it points to | Phase 1 evidence |
|---|---|---|---|
| Vehicle root identity, owner, key delegates | public verifiability; any party may depend on it (F1 IDTx) | a public chain (L1 or a rollup) | #25, #26: lifetime cost of the cheapest standard |
| Lifecycle events by authorised parties (maintenance, inspection) | verifiable by buyers and insurers; written by many parties | a permissioned or public chain; or a database whose journal head is anchored publicly | #33 (chain cost); the F2 journal (anchoring not built, F2-S3) |
| Per-message credentials (V2V, V2I) | sub-millisecond verification, no chain on the hot path | off chain, anchored (F1 L4), with a bounded re-check | #27, #44, #46 |
| Personal or regulated data (owner identity, history detail) | erasure, access control | a database or encrypted off-chain store; commitments on chain only (F1 L3) | D64 shows a derived identifier defeats the commitment |
| Revocation status | fast reads by many verifiers; integrity | a chain or an anchored list, cached by verifiers | #32, #37, #46 |

## 6. Where Phase 1 is silent, stated precisely
Phase 1's substrates are one local chain, an in-memory registry and a PKI baseline (§1). It is silent on the rest:
- **No permissioned or private ledger was built or run.** The PoA client middleware exists, but no committed result
  uses a PoA chain (capture §3).
- **No public network was run.** The Sepolia validation is scripted and has never run on this trunk (N-11), so no
  result file exists.
- **No rollup, no content-addressed store, no conventional persistent database** (the baseline is in memory).
- **No ordering or mempool effects**, because the local node mines each transaction alone.
- **No decentralisation.** M1 has one operator, so no result speaks to verification by parties who distrust it.

## 7. What this means for the thesis and beyond
The placements follow the review's §4.1.

| Item | Where |
|---|---|
| The transfer table (§2), with its conditions | chapter 3, threats to validity |
| The #33 comparison with its FAIL, the post hoc label and the freshness cost; the #21 and #27 rows (§4) | chapter 5 (as SC-13 promised, D62) and chapter 6, "why a blockchain" |
| The substrate taxonomy (§3) | chapter 2, cited at source |
| The hybrid placement (§5), the SQLite backend, the plan | future work, one paragraph each |
| The Sepolia witness (N-11), if the author wants it before the defence | chapter 3: cross-network gas against the 100-gas tolerance, on one network |

- **Paper after the thesis (P7).** A substrate study: the same lifecycle on a database, an anchored journal, a
  permissioned EVM chain and a public testnet, with the trust each buys and the windows each leaves open (k − 1 messages, N − 1 entries).
