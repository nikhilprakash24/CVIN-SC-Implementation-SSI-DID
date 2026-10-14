# F2 Analysis — Public and Private Blockchains, and Other Databases, for Vehicle Identity

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F2, analysis). **Builds on:** `CAPTURE.md` (verified),
`docs/phase2/SCOPE_RECONCILIATION.md` §4. **Binds:** `docs/phase2/README.md`. **Numbers:** register rows only.

## 1. The question
Phase 1 compared nine identity *standards* on one ledger: a single local Hardhat node (condition M1). Its other
substrates are an in-memory registry and a PKI baseline. F2 asks the question Phase 1 held fixed: **on which kind of
ledger or database should vehicle identity live**, and which Phase 1 results survive a change of substrate?

The capture shows a naming trap to avoid from the start. In Phase 1, "backend" means a contract standard on the same
local chain (H4's five MOBI backends), "substrate" in crux C1 means a standard, and "permissioned" in the DID rubric
means role-gated contracts. None of them means a permissioned ledger. In F2, **substrate means the ledger or
database itself.**

## 2. What transfers from Phase 1, and what does not
| Phase 1 result | Transfers to another EVM ledger? | Why |
|---|---|---|
| Gas per operation (#25, #34, #35, #49, #50) | **yes, to the unit**, on any EVM chain with the same fork rules and compiler settings | gas is a property of the bytecode and the EVM rules, not of the network |
| Fees (gas × price) | **no** | price is set by each network's fee market, or by its operator on a private chain |
| Latency of chain operations (#21, #31, #33, #39) | **no** | Phase 1 has automine on one local node: no consensus, no block interval, no network |
| V2V and V2I verification latency (#27, #44) | **yes** | it is in-process (M0) and never touches a chain |
| Security results under the attack harness (#28) | **yes** for contract logic; **no** for ordering attacks | a single automine node has no mempool, so front-running and reordering were not testable |
| The k − 1 staleness bound (#46) | **yes** | it is a property of the verifier's re-check rule |

## 3. A substrate taxonomy
| Substrate | Who writes | Who reads | Who can verify history | Finality | Cost model | Trust | Privacy |
|---|---|---|---|---|---|---|---|
| Public L1 (Ethereum mainnet; Sepolia as its test stand-in) | anyone who pays | anyone | anyone | probabilistic, then economic finality (minutes) | fee market | the protocol and its validators | none by default: everything is public |
| Public L2 rollup | anyone, through a sequencer | anyone | anyone, with the L1's data | soft confirmation in seconds; L1 finality later | L2 fee plus L1 data cost | sequencer for ordering and liveness; L1 for safety | public |
| Permissioned EVM (a consortium chain with a BFT consensus) | members | members, or the public if published | members | immediate, under BFT | operator-set; can be zero | the consortium's honest majority | members only, unless data is published |
| Permissioned non-EVM ledger | members, through endorsement policies | channel members | channel members | immediate | operator infrastructure | the endorsers | channel-scoped |
| Conventional database | the operator | whom the operator serves | **only the operator** | immediate | infrastructure | the operator, fully | operator-controlled; erasure possible |
| Append-only, hash-chained database | the operator | whom the operator serves | the operator, or anyone given the journal | immediate | infrastructure | the operator, but rewrites need every later hash re-derived | operator-controlled |
| The same, with its head hash anchored on a public chain | the operator | as above | **anyone holding an anchored head** can detect a rewrite before it | anchor finality | one anchor write per batch | the operator for content; the chain for history integrity | content private; the head public |
| PKI directory (certificate authority) | the CA | relying parties | the CA; certificate transparency logs where used | immediate | infrastructure | the CA | certificate fields public |

## 4. The two Phase 1 comparisons that already speak to F2
**Database against chain, the same lifecycle (#33).** The on-chain backend's writes are about 1,600 to 6,000 times
slower than the in-process registry, and its uncached history query is slower still. A cached copy of the chain's
history matches the database's speed, and failed the pre-registered "equal once cached" band only because the
database's own serialisation dominated (figure F2-1). Read as F2 evidence, the result says: **a chain costs latency
on every write, and nothing on reads that can be served from a cache**. It also says what the chain buys is not
speed. It buys verification by parties who do not trust the operator. The database baseline offers no such
verification: it is in-memory, with no persistence, no caller authentication and no audit log (capture §1).

**PKI against a chain-backed identity, the same messages (#21, #27).** On the V2V hot path both are in-process, and
SSI's warm verify is 0.153 ms against PKI's 0.094 (#27). An uncached ERC-1056 verification, which reads the chain, is
9.654 ms against PKI's 0.253 (#21). So the chain belongs off the hot path, as Phase 1's cached design already
places it.

## 5. The design space the evidence points to: a hybrid by data class
| Data class | Needs | Substrate it points to | Phase 1 evidence |
|---|---|---|---|
| Vehicle root identity, owner, key delegates | public verifiability; any party may depend on it (F1 IDTx) | a public chain (L1 or a rollup) | #25, #26: lifetime cost of the cheapest standard |
| Lifecycle events by authorised parties (maintenance, inspection) | verifiable by buyers and insurers; written by many parties | a permissioned or public chain; or a database whose journal head is anchored publicly | #33 (chain cost); the F2 prototype (anchored journal) |
| Per-message credentials (V2V, V2I) | sub-millisecond verification, no chain on the hot path | off chain, anchored (F1 L4), with a bounded re-check | #27, #44, #46 |
| Personal or regulated data (owner identity, history detail) | erasure, access control | a database or encrypted off-chain store; commitments on chain only (F1 L3) | D64 shows a derived identifier defeats the commitment |
| Revocation status | fast reads by many verifiers; integrity | a chain or an anchored list, cached by verifiers | #32, #37, #46 |

## 6. Where Phase 1 is silent, stated precisely
- **No permissioned or private ledger was built or run.** The PoA client middleware exists, but no committed result
  uses a PoA chain (capture §3).
- **No public network was run.** The Sepolia validation is scripted and has never run on this trunk (N-11), so no
  result file exists.
- **No rollup, no content-addressed store, no conventional persistent database** (the baseline is in memory).
- **No ordering or mempool effects**, because the local node mines each transaction alone.

## 7. What this means for the thesis and beyond
- **Thesis.** Section 2's transfer table and section 4's two comparisons fit chapter 6 with existing rows. Chapter 5
  should cite #33 as SC-13 promised (D62).
- **Small additions before the defence, if the author wants them.** The Sepolia witness (N-11) is the one public-chain
  data point the thesis has always planned. It turns "gas transfers to the unit" from an argument into a measurement.
- **Paper after the thesis.** A substrate study: the same lifecycle on a database, an anchored journal, a
  permissioned EVM chain and a rollup, with the trust each buys and the latency each costs.
