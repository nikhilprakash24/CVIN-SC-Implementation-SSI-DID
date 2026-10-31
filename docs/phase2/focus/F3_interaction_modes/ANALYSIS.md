# F3 Analysis: Three Modes of Communicating with the Chain, for Reads and Writes

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F3, analysis). **Builds on:** `CAPTURE.md` (verified), `MODE_CLASSIFICATION.md`
(generated), `docs/phase2/SCOPE_RECONCILIATION.md` §3.3. **Binds:** `docs/phase2/README.md`. **Numbers:** register rows and the committed files named beside them.
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-28, AR-29, AR-30, AR-31, AR-32, AR-35, AR-36, AR-41

**The frames.** The thesis uses the six-cell frame of decision P2-D7 (§2).
A/B/C (§3) is Phase 2's analytic frame and paper P4's, and the thesis does not carry it.

**Terms used below.**

| Term | Meaning |
|---|---|
| register row (#n) | a row of the claim register, `docs/MEASUREMENT_CONDITIONS.md` |
| EOA | externally owned account: an account controlled by a private key, not by contract code |
| `eth_call` | a read-only call to a node: it runs a contract function against current state and sends no transaction |
| `eth_getLogs` | a node call that returns past event logs, the data contracts emit into transaction receipts |
| relayer | a third party that signs and submits the outer transaction of a write the owner has signed, and pays its gas |
| bundler | the party that submits an owner's signed ERC-4337 UserOperation to the EntryPoint; under ERC-4337 the account pays, and no paymaster is used here |
| P*(f) | the number of messages a verifier can check in a fraction f of a 100 ms message interval, floor(f · 100 ms / t) (`docs/LATENCY_BUDGET.md`); about 100 is needed at density |
| EntryPoint | the ERC-4337 contract that validates and executes UserOperations |
| U3, U5 | harness operations: U3 sets an attribute directly; U5 sets it through a signed, relayed operation |
| k | the re-check interval of a caching verifier: it asks the chain on every k-th message |
| M1, M1-H/HTTP, M2 | measurement conditions: Hardhat local, the harness over HTTP-RPC, public testnet |

## 1. The question, and a naming caution
F3's modes are lettered A, B and C, because in this repository **"Mode 3" and "Mode 4" already mean C-V2X sidelink
resource-allocation modes** (network-scheduled and autonomous resource selection; `cv2x-testbed/README.md`). C-V2X is cellular
vehicle-to-everything radio. The author speaks of three modes or methods by which a party communicates with the
blockchain, for reads and writes. The repository never defined them. The capture found four coherent ways to cut the
space, and that one naming clash.

## 2. The thesis frame: six cells (decision P2-D7)
The thesis classifies writes three ways and reads three ways, and every cell has a V row.
Each row is quoted with its own condition and host; no ratio is formed across rows from different runs (rule 1.1.7).

| Cell | What it is | Measured value | Row and condition |
|---|---|---|---|
| **Write, direct** | the owner's EOA signs and pays its own transaction | ERC-1056 attribute update 35,024 gas; ERC-4337 account, direct call 94,651 gas | #34 (U3), M1-H |
| **Write, relayed** | the owner signs an ERC-1056 `*Signed` operation; a relayer signs, submits and pays the outer transaction | 62,646 gas (+27,622 over direct) | #50 (U5), M1-H |
| **Write, account-abstracted** | the owner signs a UserOperation; a bundler submits it to the EntryPoint; under ERC-4337 the account pays (no paymaster here) | 141,767 gas (+47,116 over direct); EntryPoint indirection +46,830 gas per operation in the benchmark | #34, #50 (U5), M1-H; #25, M1 |
| **Read, on demand** | the verifier resolves the identity from its node at the moment of use | uncached ERC-1056 verify 9.654 ms median, 15.984 ms p95, 4 RPC calls | #21, M1, 2.10 GHz Xeon (F2 capture §2.2) |
| **Read, cached** | the verifier uses an earlier resolution and re-checks it every k messages | one probe refresh 2.76 / 2.89 ms (replicates r1 / r2); this is the cost of one refresh, not of verifying one message. Staleness at most k − 1 messages | #37, M0/M1, 2.80 GHz shared Xeon; #32 (k curve, another host); #46 |
| **Read, offline** | the verifier checks an issuer's credential in-process, with no chain contact | SSI V2V warm verify 0.142 ms [0.141, 0.143] | #27, M0, Xeon 2.10 GHz × 4 |

#21 and #37 predate the D51 fix, which adds one RPC call to a full resolution; both are due for re-run (A3b).
A within-run comparison of the three read cells is left to the A3b re-runs or to paper P4.
The data behind the withdrawn read-mode figure is the table in `../FIGURES.md`.

## 3. Phase 2's and paper P4's frame: A, B and C, repaired
This frame is not carried in the thesis. It is kept for Phase 2's analysis and for paper P4.

**The unit.** One interaction, classified at its time of use.

**Writes are classified by who signs and pays the outer transaction.**
Where the signer and the payer differ, as in ERC-4337, both are named.

| Write mode | Who signs the outer transaction | Who pays | Phase 1 instances |
|---|---|---|---|
| **A, direct** | the party itself (an EOA) | the party | every harness write except U5 (#34) |
| **B-submit, relayed** | a relayer | the relayer | ERC-1056 `*Signed` (U5, #50) |
| **B-submit, account-abstracted** | a bundler | under ERC-4337, the account, through the EntryPoint; no paymaster is used here | ERC-4337 UserOperation (U5, #34, #50) |

The harness's EntryPoint is a minimal research contract with no gas accounting: it always passes `missingAccountFunds = 0` (`1_blockchain-identity/contracts/ERC4337/CVINMinimalEntryPoint.sol:19-21`, `:79`).
So in the measured run the submitting account bears the gas, and the standard's reimbursement is not exercised.
#50 measures gas only; who pays and who is trusted are not measured.

**Reads are classified by who produced the bytes the verifier trusts.**

| Read mode | Who produced the trusted bytes | Phase 1 instances |
|---|---|---|
| **A, own node** | the verifier's own node; or any source, when the bytes carry a proof checked against a header the verifier trusts independently | every harness read (#31); the testbed's ERC-1056 resolution (#21), and the cache it fills (#32, #37) |
| **B-serve** | a third party (an RPC provider or an indexer), with no proof | none: no provider, no indexer, M2 not run |
| **C, issuer** | the issuer of a credential, checked in-process with no chain contact | V2V and V2I verification (#27, #44) |

**Attributes, recorded beside the mode and not used to classify it.**

| Attribute | Values | Example |
|---|---|---|
| Transport | in-process; local node over RPC; public provider | M1, M1-H/HTTP, M2 |
| Timing of a read | now; cached, re-checked every k messages; never re-checked (k = ∞) | #32, #37: a cache is A or B by origin, with timing "cached" |
| Timing of a write | immediate; detached (below) | Phase 1 submits every signed write at once |

**Three cases the old cut put in two cells, resolved.**
- An EOA transaction sent through a public provider is A: the party signs and pays. "Public provider" is its transport.
- A cache filled through a provider is B-serve by origin, with timing "cached". So it carries the provider's trust.
- An attribute written by an authority (ERC-1155, LSP8) is A for the authority, which signs and pays its own transaction. The vehicle is the subject of the write, not its party.

**A detached write is a timing attribute, not a mode.**
A detached write is authorised at t₀ and included at t₁ > t₀ through A or B.
Two quantities describe it: the delay t₁ − t₀, and the validity bound, the latest t₁ at which inclusion still succeeds.

| Statement | Corrected |
|---|---|
| "Phase 1 has no detached write" | **Wrong.** ERC-1056 signed operations are detached writes with no deadline. The digest binds the owner's current nonce, and the operation stays valid until that nonce is used, or until the signer stops being the owner (`1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol:165-175`). It never expires by time. The risk is that a signature held back stays valid indefinitely. Phase 1 submits each one at once, so t₁ − t₀ was never measured |
| "The F2 journal anchoring is the first prototype" of a detached write | **Wrong.** The anchoring step (F2-S3) is not built yet |
| "Someone else pays" for every B-submit write | **Wrong for ERC-4337.** Under the standard the account pays; there is no paymaster here |

**Trust, privacy and availability by mode.**

| Concern | A, direct or own node | B-submit | B-serve | C, issuer |
|---|---|---|---|---|
| Who must be trusted for correctness | the party's own node | nobody for content (the signature fixes it) | the provider, unless the read is proven against an independent header | the issuer of the credential, and the freshness rule |
| Who can censor or delay | the party's network | the relayer or bundler | the provider | nobody at use time; the issuer at renewal |
| Who learns what is being looked up | the party's node | the relayer learns the operation | the provider learns every query: a linkability channel | nobody |
| Staleness | none at the read; k − 1 messages if cached (#32, #37, #46) | none | as fresh as the provider; k − 1 messages if cached | bounded by the re-check rule: k − 1 messages (#46). D51's clock assumption is fixed in the provider, but #32 and #37 predate the fix |
| Replay across chains | none recorded | D52: the ERC-1056 signed digest lacks the chain id | none recorded | none recorded |

The capture found three other cuts (CAPTURE §7). Under the repaired frame they become attributes:

| Alternative cut | Its three values | Under the repaired frame |
|---|---|---|
| Chain contact at time of use | synchronous, periodic, none | the timing attribute of a read |
| Who acts | self, delegated, none | the signer and payer of a write |
| Transport | in-process, node over RPC, public provider | the transport attribute |

## 4. What the evidence implies
**Writes.** A relayed or account-abstracted write costs between a half and four fifths more gas than a direct one
(#50, #34; the ratios are the review's arithmetic on #50).

| Write | Direct, gas | Relayed or account-abstracted, gas | Difference | Over direct | Who pays the outer transaction |
|---|---:|---:|---:|---:|---|
| ERC-1056 attribute update | 35,024 | 62,646 | +27,622 | 0.79 | direct: the owner; relayed: the relayer |
| ERC-4337 attribute update | 94,651 | 141,767 | +47,116 | 0.50 | direct: the owner; through the EntryPoint: the account under the standard (no paymaster); the submitter in this harness |

Only two of the ten harness columns have any such path.
What it buys is that the vehicle's key need not reach the chain itself.
For ERC-1056 it also means the key need not hold funds.

**Reads.** The three read cells in §2 come from three runs on different hosts and conditions, so the thesis forms no span or ratio across them.

**The 10 Hz budget, per path and per host.** P*(0.5) is defined in the terms table.

| Path | Host | Result | Row |
|---|---|---|---|
| SSI offline verify | Xeon 2.10 GHz × 4, M0 | **fits**: warm verification is linear at 0.164 ms per neighbour, with no saturation up to 80 neighbours (13 % of the 100 ms budget); P*(0.5) ≈ 305 is a linear extrapolation beyond the tested range | #26 (Exp. C/D), #27 |
| ERC-1056 cached verifier, probe refresh | 2.80 GHz shared Xeon | **does not fit**: no finite k reaches P*(0.5) = 100; k = ∞ gives 78 and 87 (r1 / r2); zero staleness (k = 1) gives 13 and 12 | #37 |
| ERC-1056 cached verifier, full refresh | #32's host, not #37's | 110 at k = ∞, where staleness is unbounded; 4 at k = 1; the fitted crossing of 100 is at k ≈ 146 | #32 |

Zero staleness and P*(0.5) ≥ 100 were not achieved together on either host.
#32 and #37 must never be mixed (#37 note).

**Radio coupling (an argument from the standard, not evidence).**
Out of cellular coverage, only Mode C is available.
The testbed has no radio (its Mode 3 is a stub), so this rests on the standard alone (3GPP Release 14, recalled; to be cited at source).
Sidelink mode 4 is a resource-allocation mode: autonomous resource selection does not by itself remove the Uu path.
A vehicle can use mode 4 inside coverage while it holds a cellular link, which then makes A and B available (capture §5: "correlated but not equivalent").
Only operation outside coverage removes the path to the chain.
The freshness re-check (#32, #37) assumes such a path, and no Phase 1 radio code provides it.

## 5. What this means for the thesis and beyond
The placements follow the review's §4.1 and decision P2-D7.

| Item | Where |
|---|---|
| The six-cell table (§2) | thesis, chapter 4 or chapter 6 |
| The A/B/C frame (§3), the radio coupling (§4), the mode classification of demo steps | paper P4 |
| The plan (`PLAN.md`) | thesis future work, one paragraph |

- **Small addition, if the author wants it.** B-serve has no measurement. The Sepolia run (N-11) through a public provider would give it one data point.
- **Paper P4.** The A3b re-runs of #21 and #37 on one host give the within-run read comparison; a verified provider read (PLAN E-F3-2) and a timed detached write (E-F3-3) complete it.
