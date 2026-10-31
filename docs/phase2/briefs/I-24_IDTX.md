# I-24 Deep-Dive Brief: Identity-Dependent Transactions (IDTx)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-20 (Phase 2 session 3, after-action report 23)
**Idea:** I-24 in `docs/phase2/ideas.yaml` (track T, author focus F1). **Builds on:**
`docs/phase2/focus/F1_onchain_storage_idtx/` (README, ANALYSIS, PLAN, EXECUTION);
`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md` §3; `docs/phase2/reviews/DISPOSITIONS_F1-F3.md`;
`phase2/idtx/`. **Sources:** `docs/phase2/briefs/I-24_sources.json` holds one entry per cited source, with the URL
fetched on 2026-10-20 and the verbatim quote. Quotes from PDFs (S01, S04, S14) undo typographic ligatures and
line-break hyphens; quotes from HTML drop the spaces left by stripped code tags. Nothing else is changed.
**Numbers:** every number below is a register row of `docs/MEASUREMENT_CONDITIONS.md` with status V, or a prediction
taken from F1 PLAN. Phase 2 has no measured result yet (Phase 2 principle 4, `docs/phase2/README.md`).

## 1. The question and the definition in force

**Question (ideas.yaml I-24).** What does conditioning a transaction on ledger-held identity state cost and risk, by
dependency kind, storage locus, encoding, evaluation and continuation?

**Definition in force.** The academic review's §3.3, adopted as the default of decision P2-D8 and restated without
change in F1 ANALYSIS §4.1:

> An **identity-dependent transaction (IDTx)** is a transaction whose admissibility or effect is a function of the
> state of an identity that the transaction names. That state is evaluated during execution, either from ledger state
> or from an attestation or proof that the transaction carries and verifies. Two cases are excluded: authentication of
> the transaction's own sender, and a check whose only subject is the identity record that the transaction itself
> modifies (identity administration). An off-chain decision that depends on identity state, such as a verifier
> accepting a message, is an **identity-dependent decision**. It shares the freshness dimension but is not a
> transaction.

This brief uses no other wording. CAPTURE.md §5's working definition is superseded (AR-2, disposed as fixed in
`DISPOSITIONS_F1-F3.md`).

## 2. Phase 1 anchor

### 2.1 What Phase 1 established (register rows with status V)

| Row | What it shows | Bearing on IDTx |
|---|---|---|
| #49 | U3 set attribute: ERC-1056 executes 1 SSTORE, 0 zero-to-nonzero, 288 log bytes; ERC-735 13 / 12, 1,024 B. Over the 17-event lifecycle, zero-to-nonzero SSTOREs range from 8 (ERC-1056) to 149 (ERC-735). The row's AR-1 correction: event-held attributes have no direct contract read, only a carried receipt proof, which Phase 1 never built | the storage locus decides whether an in-contract dependency is possible at all |
| #35 | Lifetime gas over the 17-event lifecycle: ERC-1056 1,050,809, ERC-735 5,797,561, with seven standards between | the write side of the trade-off; an association with state written, not a cause (code deposit dominates ERC-735 creation) |
| #31 | ERC-1056 resolution grows with history: 14, 32, 112 RPC calls (87 KB at h = 50); median 103.177 ms in-process at h = 50 | not writing state moves cost to every reader |
| #51 | R3 read cost at h = 1, 10, 50 for all ten columns: ERC-1056 grows in calls (14 / 32 / 112); ERC-735 stays at 3 calls while bytes grow to 180,558; ERC-725xy stays at 2 calls | state-storing standards are flat in calls, so a contract or verifier can depend on them at constant call count |
| #50 | A relayer-submitted ERC-1056 signed `setAttribute` costs 62,646 gas against the owner's direct 35,024 (+27,622); ERC-4337 through the EntryPoint costs 141,767 against 94,651 | the only Phase 1 measurement of a third party submitting on another's behalf; the prototype's keeper `fulfil` is the IDTx analogue, unmeasured |
| #32, #37 | A caching verifier accepts at most k − 1 messages after a revocation (35/35 and 280/280 trials) | the freshness dimension, measured for identity-dependent decisions only; both rows predate the D51 fix and await re-run A3b (F1 ANALYSIS §3) |

### 2.2 What Phase 1 left open

- **No IDTx was measured.** F1 ANALYSIS §4.2 re-classifies the 25 captured instances plus `payToll` and finds 4 of
  26 are IDTx (T5 MOBI birth, T10 and T11 `addClaim`, `payToll`). None has a measured dependency cost separate from
  its action.
- **No proof-carrying locus exists.** The L1 (event log) locus can condition an on-chain action only through a
  receipt proof; Phase 1 built none (#49 correction, AR-1).
- **No ordering window was measured.** Phase 1 ran a single automining node, so the race between a dependency's
  change and a dependent transaction never arose (F1 ANALYSIS §4.5).
- **The prototype exists but is not a measurement.** `phase2/idtx/contracts/IdtxExecutor.sol` implements three
  dependency kinds (Owner, Delegate, registered-commitment validity) and two continuations (`execute`;
  `createIntent` then `fulfil`) against the unmodified Phase 1 `EthereumDIDRegistry`.
  `phase2/idtx/test/idtx.test.js` holds 12 behaviour tests and `phase2/idtx/mutate_idtx.sh` 5 gate mutants. No gas
  from them is a result (F1 EXECUTION).

## 3. Literature

All sources below were fetched at their origin on 2026-10-20. Quotes are in `I-24_sources.json`. "Venue" states only
what the fetched page states.

### 3.1 Ordering dependence, front-running and TOCTOU

| ID | Source | What it establishes | Consequence for IDTx |
|---|---|---|---|
| S01 | Luu, Chu, Olickel, Saxena, Hobor, "Making Smart Contracts Smarter", ACM CCS 2016 | Defines transaction-ordering-dependent (TOD) contracts: the final state depends on how the miner orders the transactions that invoke the contract. Proposes **guarded transactions**: a transaction carries a guard condition g on the current state and is dropped if g does not hold | The prototype's `fulfil`, which re-evaluates the identity predicate at execution, is an application-level guarded transaction whose guard is identity state. The mechanism is prior art; the IDTx claim must not be the re-check itself |
| S02 | Daian, Goldfeder, Kell, Li, Zhao, Bentov, Breidenbach, Juels, "Flash Boys 2.0", arXiv:1904.05234, 2019 | Measures front-running bots and priority gas auctions; names transaction-ordering dependencies as a large, complex risk | The ordering race in F1 ANALYSIS §4.5 is an instance of this class. An identity change (owner transfer, revocation) and a dependent transaction can be reordered by whoever builds the block |
| S03 | Eskandari, Moosavi, Clark, "SoK: Transparent Dishonesty: front-running attacks on Blockchain", FC 2019 (journal reference on the arXiv page) | Defines front-running as benefit from prior access to upcoming transactions; maps proposed mitigations into categories | Supplies the mitigation vocabulary for the IDTx ordering row (deadlines, commit-reveal) instead of inventing one |
| S04 | Bishop, Dilger, "Checking for Race Conditions in File Accesses", Computing Systems 9(2), 1996 | Defines a TOCTTOU flaw: a program checks a characteristic, then acts assuming it still holds when it does not | The origin of the term the F1 packages use. Their spelling is "TOCTTOU"; the F1 documents write "TOCTOU" |

### 3.2 Access control and identity checks in contracts

| ID | Source | What it establishes | Consequence for IDTx |
|---|---|---|---|
| S05 | Hu, Ferraiolo, Kuhn, Schnitzer, Sandlin, Miller, Scarfone, NIST SP 800-162, January 2014 (updates to 08-02-2019) | ABAC evaluates attributes of the **subject, object**, requested operations and environment against policy | ABAC already admits object attributes. "The predicate is about the named identity, not the caller" (F1 EXECUTION, AR-4) is therefore ABAC with the named identity as object. The IDTx distinction from ABAC must rest on the ledger-specific axes (locus, encoding, evaluation point, freshness), not on subject versus object |
| S06 | Braendgaard, Torstensson, ERC-1056 "Ethereum Lightweight Identity" (status Stagnant), created 2018-05-03 | Specifies `validDelegate` as a view and keeps attributes in `DIDAttributeChanged` events; states that contract events store data "exclusively for off-chain use" | The standard itself confirms the L1 constraint: an attribute is not a contract-readable dependency. `identityOwner` and `validDelegate` are the L0 dependencies the prototype uses |
| S07 | Buterin, Weiss, Tirosh, Nacson, Forshtat, Gazso, Hess, ERC-4337 "Account Abstraction Using Alt Mempool" (status Final), created 2021-09-29 | UserOperation validation depends on EVM state that other UserOperations or transactions can change, so the standard introduces simulation | The admission-time evaluation point has a stated staleness problem at origin. F1 ANALYSIS §4.2 excludes `validateUserOp` as sender authentication; an admission-time check on a *named* identity is still an IDTx and inherits this problem |
| S08 | Weiss, Tirosh, Forshtat, Nacson, ERC-7562 "Account Abstraction Validation Scope Rules" (status Review), created 2023-09-01 | A UserOperation's validity may depend on mutable state, so a second validation runs before inclusion. Storage access during validation is limited to the account's associated storage; a staked paymaster or factory gets read-only access to any non-entity storage (STO-033) | On this reading of STO-010 to STO-033, an account's validation cannot read a registry slot keyed by *another* identity; only a staked entity can. So the "at admission" cell of the evaluation-point axis is constrained by a standard, not only by cost |
| S09 | Lebrun, Malghem, Thizy, Falempin, Boudjemaa, ERC-3643 "T-REX" (status Final), created 2021-07-09 | `isVerified` runs inside `transfer`, `transferFrom`, `mint` and `forcedTransfer` and checks that the **receiver** is in the Identity Registry with the required claims signed by a trusted issuer | By §3.3 a T-REX transfer is an IDTx: its admissibility depends on the state of an identity the transaction names (the receiver), not on the sender. This is the closest prior art, as the review says, and it is a standard at Final status |

### 3.3 Off-chain data, proofs and credential status

| ID | Source | What it establishes | Consequence for IDTx |
|---|---|---|---|
| S10 | Jentzsch, Jentzsch, EIP-1186 `eth_getProof` (status Stagnant), created 2018-06-24 | An RPC method returns Merkle proofs for accounts and storage values; with a trusted state root they verify offline | Gives L0 dependencies a proof form for off-chain verifiers. It covers storage, not logs, so it does not build the L1 receipt proof (as AR-33 already notes) |
| S11 | Buterin, Stanczak, Ballet, Singh, Jasoria, Hagopian, Brouwer, Mahmoodi, EIP-2935 "Serve historical block hashes from state" (status Final), created 2020-09-03 | Stores the last HISTORY_SERVE_WINDOW (8191) block hashes in a system contract; BLOCKHASH_SERVE_WINDOW stays 256 | Sets how old a block can be for a contract to check a carried receipt or storage proof against its hash. An L1 dependency on an event older than the window needs another anchor. Which fork activated it is not stated on the fetched page |
| S12 | Eskandari, Salehi, Gu, Clark, "SoK: Oracles from the Ground Truth to Market Manipulation", ACM AFT 2021 | Contracts see only data already on chain or fed into it; an oracle mediates everything else | The L4 locus (carried attestation) is the oracle problem with the issuer as oracle. The IDTx taxonomy should cite this SoK for the L4 trust model instead of re-deriving it |
| S13 | Heiss, Muth, Pallas, Tai, "Non-Disclosing Credential On-chaining for Blockchain-based Decentralized Applications", arXiv:2209.09584, 2022 | A W3C-VC-compliant model for verifying identity-related attributes on chain with zkSNARKs, compared against CL-signature verification | The closest prior work for a knowledge dependency (F1 ANALYSIS §4.4, "a commitment is equality-only"). An IDTx on a hidden attribute already has a published design; F1 cites it rather than building one |
| S14 | Naghmouchi, Kaffel, Laurent, "An automatized Identity and Access Management system for IoT combining Self-Sovereign Identity and smart contracts", arXiv:2201.00231, 2022 (extended version of FPS 2021) | An Ethereum contract acts as the verifier for smart-vehicle access; it reads Hyperledger Indy to verify issuer and holder signatures | The closest vehicle-domain prior work. Its access decision is an IDTx with a cross-ledger dependency; the paper does not frame it by locus or freshness |
| S15 | Longley, Sporny, Steele (authors); Sporny, Longley, Prorock, Alkhraishi (editors), "Bitstring Status List v1.0", W3C Recommendation 15 May 2025 | Publishes revocation and suspension status as bitstrings; an optional `ttl` gives the time to live before a refresh SHOULD be attempted | The credential layer already carries a freshness parameter in time. F1's freshness dimension (k − 1 messages, #32, #37) should be stated against `ttl`, which bounds staleness in time, as F1 ANALYSIS §4.5 asks |

### 3.4 Does anything already name the concept?

Two web searches for the exact phrases "identity-dependent transaction", "identity-conditioned", "identity-gated" and
"identity-aware" with smart contracts found no paper that defines any of them. Patent hits used the words
descriptively. This is a negative search result, not proof of absence; a scholarly-database search (ACM DL, IEEE
Xplore, DBLP) has not been run. The mechanism, however, is named and standardised under other names: guarded
transactions (S01), compliance checks on eligibility (S09), validation rules (S07, S08) and contract-as-verifier
(S13, S14).

### 3.5 What the literature does to the claim

| Claimed in F1 ANALYSIS §4.3 | Status after reading |
|---|---|
| The guard-on-execution mechanism is not new | confirmed and sharpened: S01 proposes it in general, S09 standardises it for identity claims |
| The definition separates dependence on another identity from authentication and administration | holds against S07 and OpenZeppelin `onlyRole` (T01), which gate on the caller. Does not separate it from ABAC (S05), where object attributes are standard |
| A taxonomy keyed to storage locus | no fetched source does this. S06, S10, S11 and S08 each constrain one cell, which is evidence the axis matters |
| The freshness dimension is absent from access-control and token-compliance work | partly: S07 and S08 state the staleness problem for admission; S15 carries a `ttl`. None measures a staleness window for an identity dependency |

## 4. Tooling for the first experiment

| Tool | Version | Source of the version | Use |
|---|---|---|---|
| Hardhat (Hardhat Network) | 2.28.6 installed; `^2.19.4` declared | `1_blockchain-identity/node_modules/hardhat/package.json`; `package.json` | the M1 node. Automine for E-F1-1 and E-F1-2; interval mining (`evm_setIntervalMining`) and FIFO mempool order for E-F1-3 (T02) |
| solc | 0.8.24, optimizer 200, viaIR, `cancun` | `1_blockchain-identity/hardhat.phase2.config.js` | as F1 PLAN conditions |
| ethers | 6.17.0 installed; `^6.10.0` declared | `node_modules/ethers/package.json` | receipts (`gasUsed`) and `debug_traceTransaction` for the opcode explanation of a miss |
| OpenZeppelin Contracts | 5.0.2 | `node_modules/@openzeppelin/contracts/package.json`; register #25 | `AccessControl` (T01) for an optional caller-role control arm (§7.3) |
| Phase 1 `EthereumDIDRegistry` | unmodified Phase 1 artifact | `phase2/idtx/test/idtx.test.js` | the L0 dependency target |
| IDTx prototype | at trunk | `phase2/idtx/` | the instrument; needs `executePlain` (F1-S4) |
| Phase 1 `MetricsCollector` | at trunk | `benchmarks/lib/MetricsCollector.js` (#49 note) | SSTORE and zero-to-nonzero counts from traces |
| Slither | 0.11.6 (PyPI, uploaded 2026-07-28) | `pypi.org/pypi/slither-analyzer/json` (T03) | static check of the locus contracts. Its published detector table lists no transaction-ordering detector, so it does not serve E-F1-3 |
| `mutate_idtx.sh` | at trunk | `phase2/idtx/` | shows each gate fires; the `no_recheck_at_fulfil` mutant is E-F1-3's no-re-check arm |

Not available and not needed for the first experiment: a receipt-proof verifier for L1 (S10 covers storage only), a
staked ERC-4337 bundler for the admission cell (S08), and a zero-knowledge verifier (S13).

## 5. Size

| Session | Work | Output |
|---|---|---|
| 1 | Add `executePlain`; write the seeded harness; lock F1 PLAN as `docs/phase2/prereg/` (F1-S4) | a committed pre-registration before any run |
| 2 | Run E-F1-1 (three kinds, two continuations, N = 30 seeded); trace any miss | a cost table and verdicts |
| 3 | Build the four locus contracts for E-F1-2 (L0, L1, L3, L4) holding one VIN-bound datum; run writes and reads at h = 1, 10, 50 | the locus table; the in-transaction feasibility tests |
| 4 | Promote clean runs to register rows; write the chapter 6 paragraph and the P5 table | rows with status V |

**Four sessions** for E-F1-1 and E-F1-2, if L4 reuses the Phase 1 issuer path (`attestEvent`, `addClaim`). If L4
needs new issuer infrastructure, F1 PLAN reports it as not run, and the count stays four.

**MASc-sized or not.** The thesis already holds the definition, taxonomy and re-classified inventory as conceptual
(review §4.1). E-F1-1 and E-F1-2 are MASc-sized as one measured table that backs the taxonomy. They are not a paper on
their own: §3.5 shows the cost of an L0 check is what S09 already pays. What turns it into P5 is the review's list
(§4.2): one proof-carrying locus (a receipt proof against an EIP-2935 hash, two to four more sessions) and the
ordering window under interval mining (E-F1-3, one to two sessions). Both are beyond the thesis by the scope
reconciliation's placement.

## 6. Risk

| Risk | Evidence | Effect |
|---|---|---|
| The mechanism is already done | S01 (guarded transactions); S09 (identity-gated transfers, Final) | the contribution cannot be "contracts that check identity". It has to be the locus-keyed taxonomy and a measured window |
| The definition collapses into ABAC | S05 includes object attributes | AR-4's "named identity, not caller" is not a distinction from ABAC. The definition still separates IDTx from *caller* access control (T01, S07) and from administration, which is what the inventory count (4 of 26) rests on |
| E-F1-1 measures only the gas schedule | F1 PLAN derives every band from cold account and slot access | a PASS confirms arithmetic. It cannot show anything beyond access control, because a caller-role check reading one cold slot costs the same opcodes |
| A scholarly search finds the term | §3.4 searched the open web only | the positioning paragraph changes; the taxonomy and measurements stand |
| L4 or L1 cannot be built in budget | §4 | E-F1-2 reports them as not run (F1 PLAN), and the locus axis keeps unmeasured cells |

**The kill criterion in light of the literature.** ideas.yaml says: "If the measured overhead and the TOCTOU result add
nothing beyond access control, keep IDTx as a taxonomy in chapter 6 and drop the paper." Read against §3:

- **Measured overhead** at L0 will add nothing beyond access control by construction. An L0 IDTx and a role check
  both read registry storage; S09 already pays this cost in every compliant transfer. E-F1-1 alone therefore cannot
  satisfy the criterion, and the brief recommends saying so in the pre-registration.
- **The TOCTOU result** as built (tests 9 and 10) adds nothing beyond S01: re-evaluation at execution is a guarded
  transaction. What S01 to S03 leave unmeasured is the *window*: how many blocks or seconds a dependent transaction
  stays exposed to an identity change it cannot see. That is E-F1-3, not E-F1-1.
- **The locus result** is where IDTx differs from access control. Access control assumes the attribute is readable.
  S06 says L1 data is for off-chain use only, S11 bounds how far back a proof can reach, and S08 forbids an account
  reading another identity's storage at admission. None of the fetched work tabulates these constraints by locus.

So the criterion should be operationalised before the lock as: **keep the paper if E-F1-2 shows at least one locus
whose dependency is infeasible or differently priced than an L0 read, or E-F1-3 reports a non-zero exposure window
for the no-re-check arm. Otherwise apply the kill.** This is a proposal for the author's decision, not a change to
ideas.yaml.

## 7. First experiment (pre-registrable design)

The design is F1 PLAN's E-F1-1 and E-F1-2 unchanged in measure and bands, with the verdict rules and one optional
control arm made explicit. Nothing has been run.

### 7.1 E-F1-1: the cost of each dependency kind

- **Hypothesis H1.** The gas an IDTx adds over its action is the cost of the reads its dependency kind performs, and
  nothing else.
- **Predictions** (F1 PLAN §1, written before any run): Owner adds 5,700 to 6,500 gas; Delegate 6,000 to 7,000;
  Commitment 14,000 to 17,000; `createIntent` costs 150,000 to 200,000; `fulfil` 35,000 to 50,000. The intent's
  storage is more than 60 % of `createIntent` plus `fulfil` ("dominated").
- **Measure.** Receipt `gasUsed` of the IDTx call minus that of `executePlain(action)` with calldata of equal length.
- **Conditions.** M1; Hardhat 2.28.6 automine; solc 0.8.24, optimizer 200, viaIR, compile target `cancun`; the node's
  execution hardfork recorded in the stamp; N = 30 seeded calls per kind; each call starts from cold access (a fresh
  transaction per call).
- **Falsified if** any kind's mean falls outside its band, or two seeded runs of the same input differ in gas (gas
  must be exact for seeded inputs, rule 1.1.10). A miss is reported with the opcode trace that explains it.

### 7.2 E-F1-2: what the storage locus changes, datum held fixed

- **Hypothesis H2.** For one VIN-bound attribute, the locus decides both who pays to read it and whether a contract can
  depend on it in the same transaction.
- **Predictions** (F1 PLAN §1): L1 is the cheapest to write and the only locus whose read grows in RPC calls with h;
  L0 and L3 stay flat in calls; L4 adds one signature check per dependency. In-transaction dependency is possible at
  L0, L3 and L4 and impossible at L1 without a carried proof.
- **Measure.** Write gas; read RPC calls and bytes at h in {1, 10, 50}; a pass or fail test for in-transaction
  dependency per locus.
- **Conditions.** As 7.1; the same datum and history at every locus.
- **Falsified if** a state-held locus (L0, L3) grows in calls with h, L1 does not, or a contract reads an L1 value
  without a carried proof.

### 7.3 Optional control arm (a proposal, not in F1 PLAN)

Add `executeRole(action)`, gated by OpenZeppelin `onlyRole` on the caller, reading one cold slot. **Prediction:** its
added gas falls inside the Owner band of 7.1. A PASS states, with a number, that an L0 IDTx costs what caller access
control costs, which is the honest baseline the kill criterion (§6) needs. A FAIL would mean the IDTx gate has a cost
the gas schedule does not explain, and the trace would say why.

### 7.4 Consistency with F1 PLAN

The measure, the control `executePlain`, the bands, N, the conditions and the L4 not-run rule are F1 PLAN's. This
brief adds the falsification wording, the cold-access condition, and the optional arm of 7.3. E-F1-3 (ordering window
under interval mining) and E-F1-4 (VIN enumeration, D64) stay in F1-S6.

## 8. Sources not read

| Wanted | Why | Status |
|---|---|---|
| Luu et al. at the eprint PDF (`eprint.iacr.org/2016/633.pdf`) | the server returned a challenge page | read instead at the authors' copy (S01); the eprint abstract page was also read |
| Daian et al., IEEE S&P 2020 proceedings page | the computer.org page returned no content | cited as the arXiv version (S02); the venue is not stated in this brief |
| Slither's GitHub README | GitHub access is not enabled in this session | the PyPI metadata was read instead (T03) |
| Xu et al., ICSA 2017; Eberhardt and Tai, ESOCC 2017 (review §3.1) | not fetched in this session | for the locus table in chapter 2, not this brief |
| EIP-2929 (cold access gas costs) | not fetched | F1 PLAN's bands rest on it; to be read before the lock |
| EIP-155, EIP-712, EIP-2771; OASIS XACML 3.0 | not fetched | review §3.1 items outside this brief's question |
| Coconut (NDSS 2019); Hawk (IEEE S&P 2016) | not fetched | review §3.1; the committed and encrypted loci |
| A scholarly-database search for the term (§3.4) | open-web search only | to run before P5 |

Fetched on 2026-10-20 and not cited: Town Crier (eprint 2016/168), zk-creds (eprint 2022/878), Muth et al. (eprint
2022/492), Torres et al. "Frontrunner Jones" (arXiv:2102.03347), W3C VC Data Model v2.0. Each is relevant to P5 but
adds nothing to this brief beyond S12, S13 and S02.
