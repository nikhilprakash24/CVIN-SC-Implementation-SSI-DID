# CVIN-SC · Roots Phase 2 · R8 — Reverse Anchor Register

| Field | Value |
|---|---|
| Document | **R8** Reverse Anchor Register |
| Version | **v0-1** (first pass: broad, dense, short cells; built to be deepened) |
| Date | 2026-10-23 |
| Thread | G-R1 Roots, Phase 2 (branch `roots/G-R1-phase2`) |
| Consumes | Phase 1 R1 (L0–L7, T-01..24, T-I01..22), R2 (SOL-01..09, O1–O18), R3 (R1–R8, I1–I9, BP-L0-01..BP-L7-07, flows), R4 (PF-01..31, PF-01′..04′, SYM-01..24); Phase 2 shared brief (LH, L0.1–L7.3); repo ground truth at 2026-10-22 (`docs/STATUS_2026-10-22.md`, `docs/MEASUREMENT_CONDITIONS.md` rows #1–#63, `docs/BASIC_ID_SET_EXTENSION.md`, `docs/phase2/briefs/I-24_IDTX.md`, `docs/LATENCY_BUDGET.md`, `docs/thesis/CRUX_REGISTER.md`, contracts and code paths cited in-row) |
| Cites as placeholders | R6 (IMP-, PRO-, ALG-, HW-, SCF-, SOL-10+, BP-LH/Lx.y) and R7 (PF-32+, SYM-25+) — written ⟦…-??⟧, resolved in v0-2 |
| Assigns | **RV-<CAT>-nn** (19 categories, 301 rows) · **MD-01..MD-22** · **PAR-01..PAR-30** |

`Progress ▓▓▓▓▓▓░░░░ 60 %` — breadth complete for v0-1; every row has an anchor and a status; R6/R7 placeholders and per-row PF formulas remain for v0-2.

---

## 0. How to use this register

**What it is.** Phase 1 and R6 run *upwards*: a primitive enables a layer, which enables a function. R8 runs *downwards*: it starts from something the programme *does* — a transaction, a credential endorsement, a read, a signature, an IDTX call — and names, for each, the roots it stands on (L-, T-, T-I-, SOL- tags; R6's SCF-/IMP-/PRO-/ALG-/HW- tags), the breaking points that can take it down (BP-), the dimensions on which it can be judged (MD-), the bound that supplies the number (PF-), the knobs that move the number (PAR-), and how much of that is already evidenced (status). Its purpose is that *every single thing can eventually be anchored to its roots and proved or measured*.

**Column key (all register tables).**
| Column | Meaning |
|---|---|
| RV | this register's tag, `RV-<CAT>-nn`, frozen once issued |
| Item · Meaning | the upper-level functionality, in a few words |
| Sub-layer | LH, L0.1 … L7.3 from the shared brief |
| Anchors down to | tags it stands on, nearest first (SCF/IMP/PRO/ALG placeholders, SOL, T-, T-I-, L) |
| BP | breaking points that defeat it |
| MD | dimensions it can be measured on |
| PF | bound/derivation that supplies the metric (⟦PF-??⟧ = R7 to supply) |
| PAR | parameters that move the metric |
| St | evidence status: **M** MEASURED (register row #n) · **Dv** DERIVED · **Ds** DESIGN · **E** ESTIMATED · **S** STANDARD · **I** IMPLEMENTED-UNMEASURED (code and tests exist, no register row) · **—** absent |
| Deepen in | best chat: Roots · IDTX · Cost · Scale · Lat · SecC (security campaign G-C1) · MV1 (G-MV1 MOBI VID) · WHY (G-WHY) · RIM (G-RIM) · New |

**Rules.**
1. **Anchored** = every cell of the row cites a tag (or an explicit `—` with reason). A row with a ⟦placeholder⟧ is *provisionally anchored*. A row whose PF is ⟦PF-??⟧ is *unbounded*. A row whose St is Ds/E is *unevidenced*. These three states are what later chats remove.
2. **Status never upgrades by assertion.** M requires a `MEASUREMENT_CONDITIONS.md` row with status V; numbers appear only with that row. Besu, QBFT, public anchoring, HAA-1 Planes V/D are **Ds** (shared brief §2). Sepolia (M2) is a gas *witness* only (`1_blockchain-identity/SEPOLIA_VALIDATION.md`); M2 latency is "not yet measured" (`MEASUREMENT_CONDITIONS.md`, M2 rule).
3. **To add a row:** take the next free number in the category; fill Item and Sub-layer first; then Anchors (at least one Phase-1 tag); then BP from R3 Part II; then MD from §1; PF from R4 or ⟦PF-??⟧; PAR from §2; St with its evidence path. Never renumber; retire with `~~RV-…~~ → RV-…`.
4. **To deepen a category (another chat picks it up):** open the routing row in §6; copy the category table into that chat's working file; for each row (a) resolve placeholders against R6/R7, (b) replace ⟦PF-??⟧ with a stated formula and inputs, (c) bind PAR values for the configuration under study, (d) run or cite the measurement, (e) return the row with a version note (`RV-VC-03 v0-2: St Ds→M #nn`). The Roots thread merges returns; no other chat edits R8 in place.
5. **Parameters are declared, not set** ("parameter after please"): §2 lists them; no row fixes a PAR value.

**Repo-vocabulary mapping (no silent choice).**
| Repo term | Phase-1 / R8 term |
|---|---|
| "nine standards" / ten harness columns (ERC-1056 pure + wrapper, 721, 725, 725xy, 735, 1155, 4337, LSP8, CVIN-Combined) | options O1–O9 (R2 §3); substrates for RV-SC |
| catalogue ops C1, C2, R1–R4, U1–U5, D1–D3, V1, V3, V5, V6, X1, P1 (`docs/BASIC_ID_SET_EXTENSION.md` §2.1) | IMinimalSSI functions in RV-IDTX (F-numbering inside the sets is **[B1]**, pending canon archive — row #53) |
| condition classes M0, M1, M1-H, M1-H/HTTP, M2, Sim | MD-17 evidence qualifier |
| IDTx (I-24 definition, P2-D8) | RV-IDTX-2x; "identity-dependent decision" = RV-READ/RV-VC verify rows |
| cruxes C1–C8 (`CRUX_REGISTER.md`) | coverage routes in §5–§6 |

---

## 1. Measurement dimensions MD-01..MD-22

Each dimension is a ruler. The unit is what a row's metric is reported in; the source names the bound that turns parameters into a number.

| MD | Dimension | Definition (1–2 lines) | Unit | Formula source |
|---|---|---|---|---|
| MD-01 | Time to confirm / finality | time from submission to inclusion, and to irreversible acceptance | s; blocks; depth z | PF-17 (round timeout), PF-19 (PoW depth), PF-20 (forced inclusion); ⟦PF-?? QBFT finality time⟧ |
| MD-02 | Decentralisation confidence | probability no colluding quorum can rewrite or censor, given validator count and independence | P(collusion); N_v, f_B | PF-16, PF-21, PF-22; ⟦PF-?? Nakamoto coefficient⟧ |
| MD-03 | Trilemma position | point on R3 Part III cost surface (trust base × finality/cost variance, security fixed) | ordinal + coordinates | R3 Part III; R4 §3; ⟦PF-?? surface map⟧ |
| MD-04 | Smart-contract security | absence of exploitable defect; attack-matrix outcome; mutation score | attacks defended / total; mutants killed | register #28, #45; ⟦PF-?? SC defect model⟧ |
| MD-05 | Protocol security | channel/message properties R1–R8 hold under the threat model | properties held; attacks rejected | R3 Table I.2; PF-01′, PF-25; ⟦PF-?? protocol proof⟧ |
| MD-06 | Cryptographic security level | best known generic attack cost, classical and quantum | bits | PF-06, PF-08, PF-09, PF-10, PF-11 |
| MD-07 | Cost | on-chain execution cost; converted to currency only in one dated appendix (register #20 rule) | gas; $ at stated date | register #1–#3, #22, #25, #29, #34, #35; PF-24 |
| MD-08 | Storage footprint | state and log growth per operation | SSTORE (zero→nonzero), log bytes | register #49 |
| MD-09 | Privacy / linkability | correlation across uses; anonymity set; leakage | bits leaked; set size | PF-04′, PF-29; register #38, #61; ⟦PF-?? linkability metric⟧ |
| MD-10 | Availability / liveness | probability the function can complete when needed | P; downtime | PF-02′, PF-05; ⟦PF-?? BFT liveness⟧ |
| MD-11 | Capacity / scale | sustainable rate and its ceiling | ops/s; ops/block; neighbours | PF-24; register #26, #31; `LATENCY_BUDGET.md` §2 |
| MD-12 | Latency (per-op) | wall time of the operation itself | ms (median, p95) | register #21, #27, #31, #32, #37, #44, #52, #57 |
| MD-13 | Latency-tier fit | whether the operation fits Tier 1 (< 100 ms), Tier 2, Tier 3 | tier; slack | PF-31; `LATENCY_BUDGET.md` §1 |
| MD-14 | Revocation latency W | time from revocation decision to every verifier refusing | s; messages (k − 1) | PF-28, PF-27; register #32, #37, #46 |
| MD-15 | Freshness / staleness σ | age of cached state at decision time | s; refresh interval k | PF-15; register #32, #37, #52, #55 |
| MD-16 | Auditability / non-repudiation | an after-the-fact party can prove what happened and who did it | provable (y/n); detection latency | PF-13; R3 R4/R4′ |
| MD-17 | Evidence status | M/Dv/Ds/E/S/I + condition class M0–M2/Sim | label | `MEASUREMENT_CONDITIONS.md` tags; shared brief §2 |
| MD-18 | Regulatory posture | GDPR/EDPB fit (erasure, commitment form, minimisation) | posture class | R2 §4 (EDPB commitment form); ⟦PF-?? not quantitative⟧ |
| MD-19 | Interoperability / conformance | conformance to W3C DID/VC, MOBI, IEEE, SAE specs | tests passed / total | register #4, #24, #53 |
| MD-20 | Recoverability | probability control survives key loss without enabling theft | P; threshold (t, m_r) | PF-30, PF-06 |
| MD-21 | Ordering-race window | interval in which a dependent action can see stale or reordered identity state | s; blocks | PF-25, PF-26; I-24 §2.2 (unmeasured) |
| MD-22 | Operational burden | human/agent steps and error probability to operate | steps; P(error) | register #62 |

---

## 2. Parameter registry PAR-01..PAR-30 (declared only — set later)

These are the knobs that change the numbers; no value is fixed here. "Candidates" lists the values a study may choose; R7 owns any bound that depends on them.

| PAR | Name | What it is | Moves MD | Candidate values | Set |
|---|---|---|---|---|---|
| PAR-01 | DLT family | ledger type | 01,02,03,07,10,11 | EVM consortium; public L2; public L1; Indy (O10) | later |
| PAR-02 | Client implementation | node software | 01,04,10,12 | Hardhat Network; Besu; Geth; Anvil; Indy-node | later |
| PAR-03 | Consensus protocol | agreement rule | 01,02,10 | automine; QBFT; IBFT2; Clique; Gasper; RBFT; PoW | later |
| PAR-04 | Validator count N_v and f_B | committee size, fault budget | 02,10 | 4, 7, 10, 16 … | later |
| PAR-05 | Block time | slot / round target | 01,11,14 | automine; 1–15 s | later |
| PAR-06 | Block gas limit G | per-block capacity | 11 | network default; consortium choice | later |
| PAR-07 | Gas pricing model | fee rule | 07,14 | free-gas; EIP-1559; fixed | later |
| PAR-08 | DID method | identifier scheme | 06,09,19 | did:ethr; did:mobi; did:indy; did:web; did:key | later |
| PAR-09 | Credential format | VC encoding | 09,19,07 | VC-JWT; JSON-LD DI; AnonCreds; SD-JWT; mDL | later |
| PAR-10 | Signature scheme / curve | signing algorithm | 06,12 | ECDSA secp256k1; ECDSA P-256; Ed25519; BBS+ BLS12-381; CL | later |
| PAR-11 | Proof system | ZK scheme | 06,07,12 | Groth16 BN254; PLONK; sigma protocols; Bulletproofs | later |
| PAR-12 | Revocation profile | status mechanism | 09,14 | SL bitstring status list; AC accumulator (SOL-09) | later |
| PAR-13 | Anchoring interval τ_a | checkpoint cadence | 16,07 | per block; minutes; hours | later |
| PAR-14 | Public anchor target | where checkpoints land | 02,07,16 | Sepolia; L2; L1 | later |
| PAR-15 | Hardware key class | key storage | 06,20 | software; SE; TPM; TEE; HSM | later |
| PAR-16 | Radio technology | V2X air interface | 12,13,10 | 802.11p; LTE-V2X PC5; NR-V2X; Uu | later |
| PAR-17 | Deployment placement | locus of state | 07,08,09,18 | on-chain; off-chain; anchored; hybrid (placement suite P1–P4) | later |
| PAR-18 | Network scope | where the ledger runs | 01,02,10 | local; consortium; public L2; L1 | later |
| PAR-19 | Verifier refresh interval k / t_poll | cache policy | 14,15,12 | k ∈ {1,5,25,∞} as in #32; time-based | later |
| PAR-20 | Cache TTL | max cached age | 15,14 | s–h | later |
| PAR-21 | Delegate validity (TTL) | delegate expiry | 14,09 | per epoch (cf. #38) | later |
| PAR-22 | Pseudonym epoch / pool size | rotation cadence | 09,07 | e.g. 20 per 5 min as in #38 | later |
| PAR-23 | Recovery threshold (t, m_r) | social/guardian recovery | 20 | 1-of-1 guardian; t-of-m | later |
| PAR-24 | Identity budget fraction f | share of 100 ms BSM interval | 13 | 0.25; 0.5; 1.0 (`LATENCY_BUDGET.md` §1) | later |
| PAR-25 | Neighbour density | vehicles in range | 11,12 | SUMO scenario values | later |
| PAR-26 | RPC transport | client link | 12 | in-process; HTTP; WS | later |
| PAR-27 | Replica count r | off-chain copies | 10 | 1–5 | later |
| PAR-28 | Permissioning mode | admission rule | 02,18 | open; node-permissioned; account-permissioned | later |
| PAR-29 | Hash function | commitment/hash choice | 06,07 | keccak-256; SHA-256; Poseidon | later |
| PAR-30 | Salt / commitment form | hiding of anchored values | 09,18 | unsalted; salted hash; Pedersen | later |

---

## 3. The register

Reading direction: categories run roughly top-down — what the user does (TX, IDTX, VC, SIG, READ) → what makes it work (PRIM, ALG, PROT, SC, SCF) → where it runs (NET, DLT, IMPL, HW, SVC) → why it exists and who governs it (SCN, GOV) → how we know (MET). Each section opens with where the category sits.

### 3.1 RV-TX — Transactions

A transaction is the unit by which anything above L5 changes ledger state. It sits at **L5.3** (format) and descends through L5.1 (EVM execution), L4.1 (fee), L3 (ordering), L0.3/L0.4 (propagation). Abstraction runs from "the wallet sent it" down to "a signed RLP blob ordered by consensus". What every row borrows from below is *ordering* (R3 carry-forward sentence).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-TX-01 | Write tx (EOA, EIP-1559) | signed state change | L5.3 | ⟦ALG-?? ECDSA⟧; T-05, T-06, T-10 | BP-L5-02, L5-03, L4-03 | 01,07,12 | PF-23, PF-24 | 01,05,07 | M (#22, #29) | Cost |
| RV-TX-02 | Legacy / EIP-155 tx | chain-id domain-separated | L5.3 | T-05; R3 R8 | BP-L5-02 | 05 | — (STANDARD) | 01 | S | Roots |
| RV-TX-03 | EIP-2930 access-list tx | pre-declared storage | L5.3 | L5.1 gas | BP-L4-03 | 07 | ⟦PF-?? warm/cold⟧ | 07 | — | Cost |
| RV-TX-04 | Read call (`eth_call`) | non-state-changing execution | L5.1, L0.4 | ⟦PRO-?? JSON-RPC⟧ | BP-L2-05, L7-03 | 12,15 | PF-15 | 26 | M (#21, #37) | Lat |
| RV-TX-05 | Batch tx | many ops in one tx | L5.3 | L4.3 | BP-L4-05 | 07,11 | PF-24 | 06 | M (catalogue L4 batch, #34) | Scale |
| RV-TX-06 | Meta-tx (signed, relayed) | third party pays/submits | L5.3, L5.2 | ⟦SCF-ERC1056-?? setAttributeSigned⟧; T-05 | BP-L5-02, L5-05 | 07,21 | ⟦PF-?? relay overhead⟧ | 07 | M (#50) | Cost |
| RV-TX-07 | ERC-4337 UserOp | account-abstraction op via EntryPoint | L5.3 | ⟦SCF-4337-?? handleOp⟧; SOL-06 | BP-L5-04 | 07,20 | — | 07 | M (#25, #50) | Cost |
| RV-TX-08 | EIP-7702 delegation tx | EOA sets code delegation | L5.3 | T-05 | BP-L5-04, L6-06 | 04,20 | ⟦PF-??⟧ | 02 | — (not in repo) | New |
| RV-TX-09 | Anchor / checkpoint tx | commitment of private state to public chain | L5.3, L2.1 | SOL-03; T-09; T-I15 | BP-L4-03, L0-04 | 16,07,09 | PF-13, PF-04′ | 13,14 | Ds | Roots |
| RV-TX-10 | Contract deploy tx | code deposit | L5.3 | L5.1 | BP-L5-04 | 07 | — | 06 | M (#22, #58) | Cost |
| RV-TX-11 | Forced-inclusion tx | L1 bypass of censoring sequencer | L5.3 | SOL-04 | BP-L3-06 | 01 | PF-20 | 18 | Ds | Scale |
| RV-TX-12 | Replacement / cancel tx | same nonce, higher fee | L4.1 | EIP-1559 | BP-L5-05 | 01,21 | PF-23 | 07 | — | Lat |
| RV-TX-13 | Private (Paladin-style) tx | content restricted to group | L5.3 | O15; SOL-05 | BP-L0-04 | 09,18 | ⟦PF-??⟧ | 17,28 | Ds | Roots |
| RV-TX-14 | Receipt / event emission | log as evidence | L5.1, L2.1 | T-08 | BP-L2-01 | 08,16 | — | 17 | M (#49) | Cost |
| RV-TX-15 | Mempool propagation | gossip to proposers | L0.3 | T-02; ⟦PRO-?? devp2p⟧ | BP-L0-01, L0-04 | 09,01 | PF-01′ | 18 | — | Scale |

### 3.2 RV-IDTX — Identity transactions and IDTX functions

These are the programme's identity operations: the IMinimalSSI twelve (SOL-06, Set A/B; Set C pending) and the I-24 identity-dependent transactions. They sit at **L6.3** and are realised in L5.2 contracts; downward they cash out as RV-TX rows; upward they are what RV-VC and RV-SCN call. Catalogue ops are from `docs/BASIC_ID_SET_EXTENSION.md` §2.1; F-numbering inside sets is [B1] except F8 = `createPresentation` (row #54).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-IDTX-01 | createDID | identifier + controller binding (C1/C2) | L6.3 | ⟦SCF-CVINVehicleDIDRegistry-?? createVehicleDID⟧; T-I17; I1 | BP-L1-01, L6-01 | 07,06,19 | PF-02, PF-03, PF-04, PF-24 | 08,17 | M (#1, #29, #34) | Cost |
| RV-IDTX-02 | resolveDID | build DID document (R1–R3) | L6.1 | RV-READ-01; T-I17 | BP-L2-05, L7-03 | 12,13,15 | PF-15, PF-31 | 08,26 | M (#31, #51) | Lat |
| RV-IDTX-03 | updateDID / rotate controller | changeOwner (U1/U4) | L6.3 | ⟦SCF-ERC1056-?? changeOwner⟧; I3; T-09 | BP-L6-02, L5-01 | 07,21 | PF-25, PF-26 | 05,18 | M (#2, #29) | IDTX |
| RV-IDTX-04 | deactivateDID | identity terminated (D3) | L6.3 | ⟦SCF-MOBI-ERC1056Registry-?? revokeIdentity⟧ | BP-L6-10 | 07,16,18 | — | 17 | M (#35 lifecycle event 17) | MV1 |
| RV-IDTX-05 | addVerificationMethod | attribute/key added (U3) | L6.3 | ⟦SCF-ERC1056-?? setAttribute⟧ | BP-L6-09 | 07,08 | — | 17 | M (#2, #49) | Cost |
| RV-IDTX-06 | removeVerificationMethod | attribute revoked (D2) | L6.3 | ⟦SCF-ERC1056-?? revokeAttribute⟧ | BP-L6-04 | 07,14 | PF-28 | 17 | M (#29) | Cost |
| RV-IDTX-07 | addDelegate | scoped delegate with TTL (U2) | L6.3 | ⟦SCF-ERC1056-?? addDelegate⟧; I4 | BP-L6-06 | 07,09 | — | 21,22 | M (#2, #38) | IDTX |
| RV-IDTX-08 | validDelegate | delegate check (R4) | L6.3 | ⟦SCF-ERC1056-?? validDelegate⟧; I2 | BP-L6-06, L7-03 | 12,15 | PF-15 | 19 | M (#51 R4 cells) | Lat |
| RV-IDTX-09 | revokeDelegate | delegate retired (D1) | L6.3 | ⟦SCF-ERC1056-?? revokeDelegate⟧ | BP-L6-04 | 07,14 | PF-28 | 21 | M (#29) | IDTX |
| RV-IDTX-10 | issueCredential | issuer key + status anchor (V1, V3) | L6.3 | RV-VC-01; I5; T-I17 | BP-L6-03 | 07,06 | PF-06 | 09,12 | M (#29, #34) | Cost |
| RV-IDTX-11 | verifyCredential | status check (V6) + off-chain proof | L6.3 | RV-VC-08; I7 | BP-L6-04, L7-03 | 12,13,14 | PF-15, PF-28, PF-31 | 12,19 | M (#21, #27) | Lat |
| RV-IDTX-12 | revokeCredential | status flip (V5) | L6.3 | RV-VC-10; I8; SOL-09 | BP-L6-04 | 07,14 | PF-28 | 12,13 | M (#22, #29) | Lat |
| RV-IDTX-13 | createPresentation (F8) | holder-built presentation (P1) | L6.3 | I6; T-I11, T-I13 | BP-L6-08, L6-05 | 07,09 | ⟦PF-?? disclosure leakage⟧ | 09 | M (#54) | IDTX |
| RV-IDTX-14 | execute (X1) | identity acts as account | L6.3, L5.2 | ⟦SCF-4337-?? handleOp⟧; ⟦SCF-ERC725-?? execute⟧ | BP-L5-04, L6-06 | 07,04 | — | 07 | M (#54) | IDTX |
| RV-IDTX-15 | Relayed op (U5) | signed op submitted by relayer | L6.3 | RV-TX-06 | BP-L5-02 | 07 | — | 07 | M (#50) | Cost |
| RV-IDTX-16 | Set C agent extension | delegated agent authority | L6.3 | SOL-06 Set C; T-I22 | BP-L6-06 | 04,09 | ⟦PF-??⟧ | 21 | Ds (scope pending, Q-R2) | New |
| RV-IDTX-20 | IDTx (definition P2-D8) | tx conditioned on named identity's state | L6.3, L5.2 | I-24 §1; SOL-06 | BP-L5-05, L6-02 | 21,07,15 | PF-25 | 05,17 | Ds (no IDTx measured, I-24 §2.2) | IDTX |
| RV-IDTX-21 | `IdtxExecutor.execute` | act if dependency holds now | L5.2 | ⟦SCF-IdtxExecutor-?? execute⟧; ⟦SOL-1? IdtxExecutor⟧ | BP-L5-05, L6-02 | 07,21 | ⟦PF-?? dependency gas⟧ | 05 | I (12 tests, 5 mutants; no gas result — I-24 §2.2) | IDTX |
| RV-IDTX-22 | `createIntent` → `fulfil` | deferred action, keeper fulfils by deadline | L5.2 | ⟦SCF-IdtxExecutor-?? createIntent/fulfil⟧ | BP-L5-05, L3-06 | 21,01 | PF-25 | 05 | I | IDTX |
| RV-IDTX-23 | `holds(Dependency)` kinds Owner/Delegate/Commitment | dependency evaluation | L5.2 | `phase2/idtx/contracts/IdtxExecutor.sol` enum `Kind` | BP-L7-03 | 15,21 | PF-15 | 17 | I | IDTX |
| RV-IDTX-24 | `setCommitment` / `revokeCommitment` | registered commitment with expiry | L5.2 | T-I15; SOL-03 | BP-L6-04 | 14,18 | PF-28 | 30 | I | IDTX |
| RV-IDTX-25 | `payToll` (IDTx instance) | toll gated on identity | L5.2 | ⟦SCF-CVIN_NFT_DID_ERC721-?? payToll⟧ | BP-L5-05 | 07 | — | 07 | I (classified IDTx, F1 ANALYSIS §4.2) | IDTX |
| RV-IDTX-26 | MOBI birth (T5) as IDTx | birth gated on manufacturer authority | L5.2 | ⟦SCF-MOBIVIDRegistry-?? registerVehicleBirth⟧ | BP-L6-03 | 07 | — | 17 | M (#33 birth) | MV1 |
| RV-IDTX-27 | `addClaim` (T10/T11) as IDTx | claim gated on issuer authorisation | L5.2 | ⟦SCF-ERC735-?? addClaim⟧ | BP-L6-03, L6-09 | 07,08 | — | 17 | M (#34, #49) | IDTX |
| RV-IDTX-28 | ZK admission (`ZkVinGate.admit`) | access gated on proof of VIN predicate | L5.2 | ⟦SCF-ZkVinGate-?? admit⟧; T-I14 | BP-L1-06 | 07,09,06 | PF-10, PF-11 | 11 | M (#58) | SecC |

### 3.3 RV-VC — Credentials

Credentials are the attribute layer: issuer-signed statements about a subject, held and presented by a wallet. They sit at **L6.2** (format) over L1.1 (signatures, pairings) with status anchored in L2.3/L5.2. Abstraction runs from "a licence class endorsement" to "a signature plus a bit in a status list".

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-VC-01 | Issue | issuer signs claim set | L6.2 | `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py`; T-I17; T-05 | BP-L6-03 | 06,12,19 | PF-06 | 09,10 | M (#21 issue) | RIM |
| RV-VC-02 | Endorsement / attestation | additional authority countersigns event | L6.2, L5.2 | ⟦SCF-MOBIVIDRegistryV2-?? attestEvent⟧ | BP-L6-03, L6-07 | 07,16 | — | 17 | M (#28 attestEvent gas) | MV1 |
| RV-VC-03 | Licence class endorsement (e.g. class 7 → 5) | DMV-style upgrade: new VC, old suspended | L6.2, L7.3 | RV-VC-01 + RV-VC-11; I5, I8 | BP-L6-03, L6-04 | 14,16,18 | PF-28 | 09,12 | Ds | New |
| RV-VC-04 | Present | holder discloses to verifier | L6.2 | `vc_holder.py`; RV-IDTX-13 | BP-L7-04 | 09,12 | — | 09 | M (#54 on-chain P1) | RIM |
| RV-VC-05 | Selective disclosure | reveal subset of claims | L6.2 | T-I11, T-I13; O12 | BP-L6-05, L6-08 | 09,06 | PF-10 | 09,10 | Ds (native only in O12, X2) | Roots |
| RV-VC-06 | Predicate proof | prove "age ≥ x" without value | L6.2 | T-I14; `zkvin.circom` | BP-L1-06, L6-05 | 09,12,07 | PF-11 | 11 | M (#56, #57) | SecC |
| RV-VC-07 | Predicate narrowing defence | bound adversary leakage across queries | L6.2, L7.1 | `5_zkp-agent-identity/steward/` | BP-L6-05 | 09,22 | ⟦PF-?? leakage bits⟧ | 22 | M (#61, Sim) | SecC |
| RV-VC-08 | Verify | signature + issuer key + status | L6.2 | `vc_verifier.py`; I7 | BP-L6-04, L7-03 | 12,13 | PF-31 | 10,19 | M (#21, #27) | Lat |
| RV-VC-09 | Status check | list/registry lookup | L6.2, L2.3 | RV-READ-05; SOL-09 | BP-L7-03, L6-05 | 14,15,09 | PF-15, PF-29 | 12,19 | M (#32, #37) | Lat |
| RV-VC-10 | Revoke | permanent invalidation | L6.2 | RV-IDTX-12; SOL-09 | BP-L6-04 | 14 | PF-28 | 12,13 | M (#46 RSU) | Lat |
| RV-VC-11 | Suspend | reversible invalidation | L6.2 | status purpose "suspension" (T-I17) | BP-L6-04 | 14 | PF-28 | 12 | — | New |
| RV-VC-12 | Expire | validity-period lapse | L6.2 | R8 freshness; clock | BP-L7-04 | 15 | — | 20 | — | Lat |
| RV-VC-13 | Re-issue | replacement after rotation/upgrade | L6.2 | RV-VC-01; PF-27 | BP-L6-03 | 14,07 | PF-27 | 09 | — | New |
| RV-VC-14 | Schema / cred-def publication | shared claim shape | L6.2 | O10/O12; T-I20 | BP-L6-09 | 19,04 | — | 09 | Ds | Roots |
| RV-VC-15 | Birth certificate (MOBI VID I) | first vehicle credential | L6.2 | `2_w3c-ssi-layer/mobi-vid/birth_certificate.py` | BP-L6-03 | 19,07 | — | 08 | M (#33) | MV1 |
| RV-VC-16 | Lifecycle event credential (VID II) | maintenance/odometer/crash record | L6.2 | `lifecycle_events.py`; ⟦SCF-MOBIVIDRegistryV2-?? recordLifecycleEvent⟧ | BP-L6-07 | 07,16 | — | 17 | M (#30, #35) | MV1 |
| RV-VC-17 | ERC-735 claim | on-chain signed claim | L6.2, L5.2 | ⟦SCF-ERC735-?? addClaim⟧ | BP-L6-09 | 07,08 | — | 17 | M (#34, #49) | Cost |
| RV-VC-18 | ERC-1155 soulbound credential | token-as-credential | L6.2, L5.2 | ⟦SCF-ERC1155-?? issueCredential⟧ | BP-L6-08 | 07 | — | 17 | M (#34) | Cost |
| RV-VC-19 | RSU credential | infrastructure authority VC | L6.2 | C3 crux; `INFRASTRUCTURE_PREREG.md` | BP-L6-03 | 12,14 | PF-28 | 19 | M (#44, #46, #47) | Lat |

### 3.4 RV-SIG — Signatures and key operations

Every authority in the stack is, at the bottom, a signature. These rows sit at **L1.1/L1.2** with key custody in **LH.2**; upward they underwrite R1 authenticity, R4 non-repudiation, I2 control.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-SIG-01 | Sign (ECDSA secp256k1) | produce σ over digest | L1.1 | ⟦ALG-?? ECDSA⟧; T-05, T-06 | BP-L1-02, L1-07 | 06,12 | PF-06, PF-07 | 10,15 | M (#48 sign, M0) | SecC |
| RV-SIG-02 | Verify | check σ against key | L1.1 | T-05 | BP-L1-04 | 12,13 | PF-06 | 10 | M (#27) | Lat |
| RV-SIG-03 | ecrecover | address from σ (precompile 0x01) | L5.1 | ⟦ALG-?? ecrecover⟧ | BP-L5-03 | 07 | — | 10 | I (used in `_recoverSigner`, ERC-735) | Cost |
| RV-SIG-04 | Key generation | sample secret scalar | L1.1, LH.1 | RNG; T-06 | BP-L1-01 | 06 | PF-06 | 15 | — | SecC |
| RV-SIG-05 | Key rotation | replace controller key | L6.3 | RV-IDTX-03 | BP-L6-02 | 21,14 | PF-25 | 05 | M (#2) | IDTX |
| RV-SIG-06 | Delegation signature | owner-signed delegate/attribute | L5.2 | ⟦SCF-ERC1056-?? addDelegateSigned⟧ | BP-L5-02 | 07,05 | — | 10 | M (#50) | Cost |
| RV-SIG-07 | Threshold / guardian recovery | regain control via guardian | L6.3 | ⟦SCF-4337Account-?? recoverOwner⟧; I9 | BP-L6-10 | 20 | PF-30 | 23 | I | SecC |
| RV-SIG-08 | BBS+ / CL proof | multi-message sig with ZK disclosure | L1.1 | T-I11, T-I13 | BP-L1-05 | 06,09 | PF-10 | 10 | Ds | Roots |
| RV-SIG-09 | Schnorr proof of knowledge | prove key possession | L1.1 | T-I10; `SchnorrEcrecoverVerifier.sol` | BP-L1-02 | 07,06 | — | 10 | M (#58, #59) | SecC |
| RV-SIG-10 | IEEE 1609.2 signed message | V2X SPDU signature | L7.2 | T-I05; ⟦PRO-?? 1609.2⟧ | BP-L7-05 | 05,13 | PF-31 | 10,16 | Ds (repo uses SSI/PKI providers, not 1609.2 encoding) | Lat |
| RV-SIG-11 | Certificate (X.509 / 1609.2) | CA binding of key | L6 | T-I02, T-I05; `identity/standard/pki_identity.py` | BP-L6-03 | 12,06 | — | 10 | M (#21 PKI) | Lat |
| RV-SIG-12 | Butterfly / pseudonym keys | unlinkable short-term keys | L6.1 | T-I05; SCMS | BP-L6-05 | 09,07 | PF-04′ | 22 | M (#38 pool on ERC-1056) | SecC |
| RV-SIG-13 | Post-quantum signature | migration target | L1.1 | BP-L1-04 | BP-L1-04 | 06 | PF-09 | 10 | — | New |
| RV-SIG-14 | Message-level signature on SPaT | RSU signs signal phase | L7.2 | C3 | BP-L7-05 | 12 | — | 10 | M (#44 sign) | Lat |

### 3.5 RV-READ — Reads and resolution

Reads are where the programme's latency budget is spent. They sit at **L6.1 / L0.4 / L2.1–L2.3**; the HAA-1 read-path rule (SOL-05) says Tier 1/2 reads never touch the ledger directly.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-READ-01 | DID resolution (event replay) | rebuild doc from ERC-1056 logs | L6.1 | `cv2x-testbed/identity/erc1056_provider.py` `_resolve_key_from_events`; T-I17 | BP-L7-03, L2-05 | 12,11 | PF-31 | 26,08 | M (#31: calls grow with h) | Lat |
| RV-READ-02 | Off-chain DID resolve (no chain) | construct doc from identifier | L6.1 | `2_w3c-ssi-layer/did-resolution/did_resolver.py` | BP-L6-01 | 12,19 | — | 08 | M (M0 rows, `MEASUREMENT_CONDITIONS.md` header) | Lat |
| RV-READ-03 | Cached read | local cache hit | L7.1 | `cv2x-testbed/identity/freshness.py` | BP-L7-03 | 12,15 | PF-15 | 19,20 | M (#32 k=∞) | Lat |
| RV-READ-04 | Probe refresh | one `getIdentityInfo` call, resolve if changed | L6.1 | `erc1056_provider.py` `_probe_identity_info` | BP-L7-03 | 12,15 | PF-15 | 19 | M (#37, #52, #55) | Lat |
| RV-READ-05 | Status-list fetch | whole-list download | L2.3 | SOL-09 SL | BP-L0-05, L6-05 | 09,12 | PF-29 | 12 | Ds | Lat |
| RV-READ-06 | Accumulator witness | non-membership proof update | L2.3 | SOL-09 AC; T-I12 | BP-L2-03 | 07,12 | PF-14 | 12 | Ds | Scale |
| RV-READ-07 | RPC read (`eth_call`) | contract view | L0.4 | RV-TX-04 | BP-L0-01 | 12 | — | 26 | M (#21 RPC list) | Lat |
| RV-READ-08 | Event/log query (`eth_getLogs`) | filter logs | L0.4, L2.2 | ⟦PRO-?? JSON-RPC⟧ | BP-L2-05 | 12,11 | ⟦PF-?? log-scan cost⟧ | 02,26 | M (#31, #51) | Scale |
| RV-READ-09 | Archive / history query | ownership, events history | L2.2 | ⟦SCF-MOBIVIDRegistryV2-?? getCompleteHistory⟧ | BP-L0-05 | 10,16 | PF-05 | 27 | I | MV1 |
| RV-READ-10 | VIN lookup | VIN → DID | L6.1 | ⟦SCF-MOBIVIDRegistry-?? lookupByVINHash⟧ | BP-L6-05 | 09,12 | — | 30 | M (catalogue R2, #29) | MV1 |
| RV-READ-11 | Read over HTTP JSON-RPC | transport-bound condition | L0.4 | M1-H/HTTP | BP-L0-02 | 12 | — | 26 | M (#39) | Lat |
| RV-READ-12 | Read against public RPC (M2) | provider-mediated read | L0.4 | M2 | BP-L0-01, L0-04 | 12,09 | — | 18 | — (not yet measured) | Lat |
| RV-READ-13 | Light-client / proof-backed read | Merkle proof of state | L2.1 | T-08; ⟦ALG-?? MPT proof⟧ | BP-L2-01 | 05,12 | ⟦PF-??⟧ | 02 | — | New |

### 3.6 RV-PRIM — Cryptographic primitives

The floor of L1. Each primitive is a *T-* or *T-I-* root; upward it is borrowed as "unforgeability" or "hiding". These rows are mostly STANDARD; measurement is per implementation.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-PRIM-01 | keccak-256 | EVM hash | L1.1 | T-07 | BP-L1-03 | 06 | PF-08 | 29 | S | Roots |
| RV-PRIM-02 | SHA-256 | VIN/commitment hash | L1.1 | T-07 | BP-L1-03 | 06,09 | PF-08 | 29 | M (#60 brute-force of unsalted VIN) | SecC |
| RV-PRIM-03 | Poseidon | circuit hash | L1.1 | T-I14 | BP-L1-03 | 06 | ⟦PF-??⟧ | 29 | I (`zkvin.circom`) | SecC |
| RV-PRIM-04 | Hash commitment | salted binding | L1.1 | T-I15 | BP-L6-05 | 09,18 | PF-08 | 30 | I | SecC |
| RV-PRIM-05 | Pedersen commitment | perfectly hiding | L1.1 | T-I15 | BP-L1-04 | 09,06 | — | 30 | M (#59) | SecC |
| RV-PRIM-06 | ECDSA secp256k1 | signature scheme | L1.1 | T-06 | BP-L1-02 | 06 | PF-06, PF-07 | 10 | S | Roots |
| RV-PRIM-07 | Ed25519 / EdDSA | did:key / DIDComm | L1.1 | T-06 | BP-L1-07 | 06 | PF-06 | 10 | S | Roots |
| RV-PRIM-08 | BN254 pairing | Groth16 verifier precompile | L1.1 | T-I11 | BP-L1-05 | 06 | PF-10 | 11 | S | Roots |
| RV-PRIM-09 | BLS12-381 pairing | BBS+ | L1.1 | T-I11 | BP-L1-05 | 06 | PF-10 | 10 | S | Roots |
| RV-PRIM-10 | Groth16 | SNARK | L1.1 | T-I14 | BP-L1-06 | 06,07,12 | PF-11 | 11 | M (#56–#58) | SecC |
| RV-PRIM-11 | Sigma protocols (Schnorr, Chaum–Pedersen, CDS OR) | interactive ZK | L1.1 | T-I10 | BP-L1-02 | 12,06 | — | 11 | M (#59) | SecC |
| RV-PRIM-12 | Accumulator | set membership | L1.1 | T-I12 | BP-L2-03 | 07,12 | PF-14 | 12 | Ds | Scale |
| RV-PRIM-13 | Merkle tree | membership/inclusion | L1.1 | T-08 | BP-L2-01 | 06 | — | 29 | M (#59 Merkle membership) | Roots |
| RV-PRIM-14 | RNG / entropy | key and nonce source | LH.1 | T-06 | BP-L1-01, L1-02 | 06 | PF-06, PF-07 | 15 | — | SecC |
| RV-PRIM-15 | AEAD / ECDH | channel confidentiality | L1.1 | T-04; T-I09 | BP-L7-05 | 05,06 | — | 10 | Ds | Roots |

### 3.7 RV-ALG — Algorithms

Algorithms compose primitives into procedures (R6 defines ALG-, R7 bounds them). They span **L1.2–L6.1**.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-ALG-01 | Consensus round (QBFT) | propose/prepare/commit | L3.1 | T-11, T-12; SOL-02 | BP-L3-01, L3-02, L3-03 | 01,02,10 | PF-16, PF-17 | 03,04,05 | Ds | Scale |
| RV-ALG-02 | Automine (Hardhat) | one tx → one block | L3.1 | SOL-01 | — (no adversary) | 01 | — | 03 | M (M1 class) | Roots |
| RV-ALG-03 | Fork choice (LMD-GHOST/Casper FFG) | public L1 head selection | L3.1 | T-13 | BP-L3-04, L3-05 | 01,02 | PF-18, PF-19 | 03 | S | Roots |
| RV-ALG-04 | DID resolution algorithm | DID Core resolve | L6.1 | T-I17 | BP-L2-05 | 12,19 | PF-31 | 08 | M (#24) | Lat |
| RV-ALG-05 | Proof generation | witness → proof | L1.2 | T-I14 | BP-L1-06 | 12 | ⟦PF-?? prover time⟧ | 11,15 | M (#57) | SecC |
| RV-ALG-06 | Proof verification | on/off-chain verify | L1.2, L5.1 | T-I14 | BP-L1-06 | 12,07 | ⟦PF-??⟧ | 11 | M (#57, #58) | SecC |
| RV-ALG-07 | Merkle proof check | inclusion verify | L2.1 | T-08 | BP-L2-01 | 06 | — | 29 | M (#59) | Roots |
| RV-ALG-08 | Gas metering | cost accounting per opcode | L5.1 | L4.1 | BP-L4-05 | 07 | PF-24 | 06,07 | M (#25) | Cost |
| RV-ALG-09 | Freshness check (k-refresh) | accept from cache ≤ k − 1 | L7.1 | `freshness.py` | BP-L7-03 | 14,15 | PF-15, PF-28 | 19 | M (#32, #46) | Lat |
| RV-ALG-10 | Replay check (timestamp/nonce) | reject stale/duplicate | L7.1 | `freshness.py` `check`; R8 | BP-L7-04 | 05 | — | 20 | M (#45 attack set) | SecC |
| RV-ALG-11 | Steward policy / learner | disclosure budget control | L7.1 | `steward/policy.py`, `learner.py` | BP-L6-05 | 09,22 | ⟦PF-??⟧ | 22 | M (#61, Sim) | SecC |
| RV-ALG-12 | Sidelink resource selection (SB-SPS) | radio resource allocation | L0.1 | `protocols/cv2x_stack.py` `allocate_resource`, CBR | BP-L0-02 | 10,11 | ⟦PF-?? CBR bound⟧ | 16,25 | I (model only) | Scale |
| RV-ALG-13 | Status-list encode/decode | bitstring compression | L2.3 | SOL-09 | BP-L6-05 | 09 | PF-29 | 12 | Ds | Lat |
| RV-ALG-14 | Peer discovery | discv4/discv5 Kademlia | L0.3 | T-02 | BP-L0-01, L0-03 | 10 | PF-01′, PF-03′ | 02 | — | Scale |

### 3.8 RV-PROT — Protocols

Protocols fix the interaction between parties (R6 PRO-). They sit at **L0.2–L0.4** (transport, P2P, RPC) and **L7.2** (messaging, credential exchange).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-PROT-01 | DIDComm v2 | authenticated encrypted messaging | L7.2 | T-I18; O16 | BP-L7-02, L7-05 | 05,09 | — | 10 | Ds | Roots |
| RV-PROT-02 | Issue Credential / Present Proof | Aries credential exchange | L7.2 | T-I21 | BP-L7-04 | 05,19 | — | 09 | Ds | Roots |
| RV-PROT-03 | OID4VCI / OID4VP | OpenID credential exchange | L7.2 | T-I17 | BP-L7-05 | 19 | — | 09 | — | New |
| RV-PROT-04 | TLS 1.3 | RPC/agent channel | L0.4 | T-I04 | BP-L7-05 | 05 | — | 26 | — | SecC |
| RV-PROT-05 | devp2p / RLPx | node transport | L0.3 | T-02 | BP-L0-01 | 10,09 | PF-01′ | 02 | — | Scale |
| RV-PROT-06 | discv5 | node discovery | L0.3 | T-02 | BP-L0-03 | 10 | PF-03′ | 02 | — | Scale |
| RV-PROT-07 | JSON-RPC | client ↔ node | L0.4 | ⟦PRO-?? JSON-RPC⟧ | BP-L0-01 | 12 | — | 26 | M (#21, #39) | Lat |
| RV-PROT-08 | IEEE 1609.2 | V2X security services | L7.2 | T-I05 | BP-L7-05, L6-05 | 05,13 | PF-31 | 16 | Ds | Lat |
| RV-PROT-09 | IEEE 1609.3 WSMP | non-IP V2X transport | L0.2 | T-01 | BP-L0-02 | 13 | — | 16 | — | Lat |
| RV-PROT-10 | SAE J2735 BSM | 10 Hz safety message | L7.2 | `protocols/cv2x_stack.py` class `BSM` | BP-L7-07 | 13,11 | PF-31 | 24,25 | M (#27 verify per BSM) | Lat |
| RV-PROT-11 | SAE J2735 SPaT | signal phase and timing | L7.2 | C3; `INFRASTRUCTURE_PREREG.md` | BP-L7-07 | 13 | PF-31 | 24 | M (#44) | Lat |
| RV-PROT-12 | DENM / CAM | ETSI messages | L7.2 | `cv2x_stack.py` `send_denm` | BP-L7-07 | 13 | — | 16 | I | Lat |
| RV-PROT-13 | MOBI VID I/II flows | birth, lifecycle, transfer | L7.2, L6.3 | `2_w3c-ssi-layer/mobi-vid/`; C6 | BP-L6-07 | 19,07 | — | 08 | M (#30, #33) | MV1 |
| RV-PROT-14 | Engine API | consensus ↔ execution client | L0.4 | ⟦PRO-??⟧ | BP-L3-03 | 10 | — | 02 | — | New |
| RV-PROT-15 | Checkpoint protocol | private → public commit | L3, L5.3 | SOL-03 | BP-L4-04 | 16 | PF-13 | 13,14 | Ds | Roots |

### 3.9 RV-SC — Smart contracts (families in the repo)

Contracts are **L5.2**: code that turns a transaction (L5.3) into identity semantics (L6.3). Each family is an option O1–O9 or a programme solution. Paths under `1_blockchain-identity/contracts/` unless stated.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-SC-01 | `ERC1056/EthereumDIDRegistry.sol` | bare ERC-1056 (did:ethr) | L5.2 | O1; T-I17 | BP-L5-04 | 07,08,04 | PF-24 | 06 | M (#2, #34, #35) | Cost |
| RV-SC-02 | `ERC1056/CVINVehicleDIDRegistry.sol` | vehicle wrapper (VIN binding) | L5.2 | O1 wrapper | BP-L5-04 | 07 | — | 17 | M (#1, #34) | Cost |
| RV-SC-03 | `MOBI/ERC1056Registry.sol` | testbed registry with `revokeIdentity` | L5.2 | O1 variant | BP-L5-04 | 07,12 | — | 17 | M (#22) | Lat |
| RV-SC-04 | `ERC721/CVINVehicleNFT.sol` | vehicle NFT, roles, service records | L5.2 | O2 | BP-L5-04 | 07 | — | 17 | M (#3, #34) | Cost |
| RV-SC-05 | `ERC721/CVIN_NFT_DID_ERC721*.sol` | NFT-DID incl. `payToll` | L5.2 | O2 | BP-L5-04 | 07 | — | 17 | I | IDTX |
| RV-SC-06 | `ERC725/CVIN_DID_ERC725.sol` | key-manager identity | L5.2 | O3 | BP-L5-04 | 07 | — | 17 | M (#29, #34) | Cost |
| RV-SC-07 | `ERC725xy/CVINVehicleERC725XY.sol` | ERC-725X/Y data + execute | L5.2 | O3 variant | BP-L5-04 | 07 | — | 17 | M (#34) | Cost |
| RV-SC-08 | `ERC735/CVINVehicleClaimHolder.sol` | on-chain claims | L5.2 | O4 | BP-L6-09 | 07,08 | — | 17 | M (#34, #49) | Cost |
| RV-SC-09 | `ERC1155/CVINVehicleCredential1155.sol` | soulbound credentials | L5.2 | O5 | BP-L6-08 | 07 | — | 17 | M (#34) | Cost |
| RV-SC-10 | `ERC4337/CVINVehicleAccount.sol` + `CVINMinimalEntryPoint.sol` | smart account, guardian | L5.2 | O7 | BP-L5-04, L6-10 | 07,20 | PF-30 | 23 | M (#25, #50) | Cost |
| RV-SC-11 | `LSP8/CVINVehicleLSP8.sol` | LUKSO identifiable token | L5.2 | O-family per R2 | BP-L5-04 | 07 | — | 17 | M (#34) | Cost |
| RV-SC-12 | `MOBI/MOBIVIDRegistry.sol` | VID I birth, ownership | L5.2 | MOBI VID; C6 | BP-L6-03 | 07,19 | — | 17 | M (#30, #33) | MV1 |
| RV-SC-13 | `MOBI/MOBIVIDRegistryV2.sol` | VID II lifecycle, attestations | L5.2 | MOBI VID; C6 | BP-L6-07 | 07,16 | — | 17 | M (#28, #35) | MV1 |
| RV-SC-14 | `CVINCombined/CVINCombinedIdentity.sol` | ERC-1056 + ERC-735 merge | L5.2 | programme composite | BP-L5-04 | 07 | — | 17 | M (#34, #54) | Cost |
| RV-SC-15 | `phase2/idtx/contracts/IdtxExecutor.sol` | IDTx executor + commitments | L5.2 | ⟦SOL-1? IdtxExecutor⟧ | BP-L5-05 | 07,21 | ⟦PF-??⟧ | 05 | I | IDTX |
| RV-SC-16 | `5_zkp-agent-identity/contracts/Groth16Verifier.sol` | zk verifier | L5.2, L5.1 | T-I14; bn256 precompiles | BP-L1-06 | 07 | PF-11 | 11 | M (#58) | SecC |
| RV-SC-17 | `ZkVinGate.sol` | proof-gated admission | L5.2 | ⟦SOL-1? zk VIN⟧ | BP-L1-06 | 07,09 | — | 11 | M (#58) | SecC |
| RV-SC-18 | `SchnorrEcrecoverVerifier.sol` | Schnorr PoK via ecrecover | L5.2 | T-I10 | BP-L1-02 | 07 | — | 10 | M (#58) | SecC |
| RV-SC-19 | `ERC725xy/CVINExecuteTarget.sol` | test target for execute | L5.2 | — (fixture) | — | 07 | — | — | I | Cost |
| RV-SC-20 | cv2x-testbed `contracts/` | registry deployed by testbed | L5.2 | RV-SC-03 | BP-L5-04 | 07,12 | — | 17 | M (#22, #47) | Lat |

### 3.10 RV-SCF — Smart-contract functions (state-changing, most important)

The verbs of L5.2. SCF tags are R6's; here each is a placeholder with contract and function name verified by `grep` of the source.

| RV | Contract.function | Meaning | Anchors | BP | MD | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|
| RV-SCF-01 | EthereumDIDRegistry.changeOwner | rotate controller | ⟦SCF-ERC1056-??⟧; RV-IDTX-03 | BP-L6-02 | 07,21 | 05 | M (#2) | IDTX |
| RV-SCF-02 | EthereumDIDRegistry.changeOwnerSigned | relayed rotation | ⟦SCF-ERC1056-??⟧ | BP-L5-02 | 07 | 07 | I | Cost |
| RV-SCF-03 | EthereumDIDRegistry.addDelegate | delegate with validity | ⟦SCF-ERC1056-??⟧ | BP-L6-06 | 07 | 21 | M (#2, #38) | IDTX |
| RV-SCF-04 | EthereumDIDRegistry.addDelegateSigned | relayed delegate | ⟦SCF-ERC1056-??⟧ | BP-L5-02 | 07 | 07 | I | Cost |
| RV-SCF-05 | EthereumDIDRegistry.revokeDelegate | delegate retired | ⟦SCF-ERC1056-??⟧ | BP-L6-04 | 07,14 | 21 | M (#29) | IDTX |
| RV-SCF-06 | EthereumDIDRegistry.setAttribute | add DID-doc attribute | ⟦SCF-ERC1056-??⟧ | BP-L6-09 | 07,08 | 17 | M (#2, #49) | Cost |
| RV-SCF-07 | EthereumDIDRegistry.setAttributeSigned | relayed attribute | ⟦SCF-ERC1056-??⟧ | BP-L5-02 | 07 | 07 | M (#50) | Cost |
| RV-SCF-08 | EthereumDIDRegistry.revokeAttribute | remove attribute | ⟦SCF-ERC1056-??⟧ | BP-L6-04 | 07 | 17 | M (#29) | Cost |
| RV-SCF-09 | CVINVehicleDIDRegistry.createVehicleDID | VIN-bound DID | ⟦SCF-CVINVDR-??⟧ | BP-L6-05 | 07,09 | 30 | M (#1) | Cost |
| RV-SCF-10 | CVINVehicleDIDRegistry.transferVehicleOwnership | owner change | ⟦SCF-CVINVDR-??⟧ | BP-L6-02 | 07 | 17 | I | MV1 |
| RV-SCF-11 | CVINVehicleDIDRegistry.addVerificationDelegate | delegate (wrapper) | ⟦SCF-CVINVDR-??⟧ | BP-L6-06 | 07 | 21 | M (#34 wrapper) | Cost |
| RV-SCF-12 | MOBI ERC1056Registry.registerVehicle | testbed register | ⟦SCF-MOBI1056-??⟧ | BP-L6-01 | 07 | 17 | M (#22) | Lat |
| RV-SCF-13 | MOBI ERC1056Registry.revokeIdentity | identity revoke | ⟦SCF-MOBI1056-??⟧ | BP-L6-04 | 07,14 | 12 | M (#22 revoke) | Lat |
| RV-SCF-14 | MOBI ERC1056Registry.updateVehicleKey | key update | ⟦SCF-MOBI1056-??⟧ | BP-L6-02 | 07 | 05 | I | Lat |
| RV-SCF-15 | MOBIVIDRegistry.registerVehicleBirth | VID I birth | ⟦SCF-MOBIV1-??⟧ | BP-L6-03 | 07 | 17 | M (#33) | MV1 |
| RV-SCF-16 | MOBIVIDRegistry.anchorVehicleKey | anchor key to DID | ⟦SCF-MOBIV1-??⟧ | BP-L6-02 | 07 | 17 | I (#43 history) | MV1 |
| RV-SCF-17 | MOBIVIDRegistry.transferVehicleOwnership | ownership transfer | ⟦SCF-MOBIV1-??⟧ | BP-L5-05 | 07,16 | 17 | M (#35 event 16) | MV1 |
| RV-SCF-18 | MOBIVIDRegistry.authorizeManufacturer | issuer admission | ⟦SCF-MOBIV1-??⟧ | BP-L4-06 | 04,02 | 28 | I | MV1 |
| RV-SCF-19 | MOBIVIDRegistryV2.recordLifecycleEvent | VID II event | ⟦SCF-MOBIV2-??⟧ | BP-L6-07 | 07,08 | 17 | M (#35) | MV1 |
| RV-SCF-20 | MOBIVIDRegistryV2.attestEvent | third-party attestation | ⟦SCF-MOBIV2-??⟧ | BP-L6-03 | 07 | 17 | M (#28) | MV1 |
| RV-SCF-21 | MOBIVIDRegistryV2.authorizeIssuer / revokeIssuerAuthorization | trust-list edit | ⟦SCF-MOBIV2-??⟧ | BP-L4-06 | 04,14 | 28 | I | MV1 |
| RV-SCF-22 | CVINVehicleClaimHolder.addClaim | ERC-735 claim | ⟦SCF-ERC735-??⟧ | BP-L6-09 | 07,08 | 17 | M (#34, #49) | Cost |
| RV-SCF-23 | CVINVehicleClaimHolder.revokeClaimContent / removeClaim | claim revoke | ⟦SCF-ERC735-??⟧ | BP-L6-04 | 07 | 12 | M (#34) | Cost |
| RV-SCF-24 | CVINVehicleCredential1155.issueCredential | mint credential | ⟦SCF-ERC1155-??⟧ | BP-L6-03 | 07 | 17 | M (#34) | Cost |
| RV-SCF-25 | CVINVehicleCredential1155.revokeCredential | burn credential | ⟦SCF-ERC1155-??⟧ | BP-L6-04 | 07 | 12 | M (#34) | Cost |
| RV-SCF-26 | CVINVehicleCredential1155.issuerTransferIdentity | issuer-mediated transfer | ⟦SCF-ERC1155-??⟧ | BP-L6-06 | 07 | 17 | I (#43 history) | Cost |
| RV-SCF-27 | CVINVehicleNFT.mintVehicle | NFT mint | ⟦SCF-ERC721-??⟧ | BP-L5-04 | 07 | 17 | M (#3) | Cost |
| RV-SCF-28 | CVINVehicleNFT.addServiceRecord | maintenance record | ⟦SCF-ERC721-??⟧ | BP-L6-07 | 07,08 | 17 | I | MV1 |
| RV-SCF-29 | CVINVehicleNFT.deactivateVehicle | retire vehicle | ⟦SCF-ERC721-??⟧ | BP-L6-10 | 07 | 17 | I | MV1 |
| RV-SCF-30 | CVIN_NFT_DID_ERC721.payToll | toll payment | ⟦SCF-ERC721DID-??⟧ | BP-L5-05 | 07 | 07 | I | IDTX |
| RV-SCF-31 | CVIN_DID_ERC725.addKey / removeKey | key management | ⟦SCF-ERC725-??⟧ | BP-L6-02 | 07 | 15 | M (#34) | Cost |
| RV-SCF-32 | CVIN_DID_ERC725.execute | identity acts | ⟦SCF-ERC725-??⟧ | BP-L5-04 | 07,04 | 07 | M (#54 X1) | IDTX |
| RV-SCF-33 | CVINVehicleERC725XY.setData | key-value data | ⟦SCF-ERC725XY-??⟧ | BP-L6-09 | 07,08 | 17 | M (#34) | Cost |
| RV-SCF-34 | CVINMinimalEntryPoint.handleOp | UserOp dispatch | ⟦SCF-4337EP-??⟧ | BP-L5-04 | 07 | 07 | M (#25 +EntryPoint indirection) | Cost |
| RV-SCF-35 | CVINVehicleAccount.setGuardian / recoverOwner | recovery path | ⟦SCF-4337Acct-??⟧ | BP-L6-10 | 20 | 23 | I | SecC |
| RV-SCF-36 | CVINVehicleLSP8.mintVehicle / revokeVehicle | LSP8 lifecycle | ⟦SCF-LSP8-??⟧ | BP-L5-04 | 07 | 17 | M (#34) | Cost |
| RV-SCF-37 | CVINCombinedIdentity.addClaim / changeOwner | combined ops | ⟦SCF-Combined-??⟧ | BP-L5-04 | 07 | 17 | M (#34) | Cost |
| RV-SCF-38 | IdtxExecutor.execute | gated action | ⟦SCF-IDTX-??⟧ | BP-L5-05 | 07,21 | 05 | I | IDTX |
| RV-SCF-39 | IdtxExecutor.createIntent / fulfil | deferred action | ⟦SCF-IDTX-??⟧ | BP-L3-06 | 21 | 05 | I | IDTX |
| RV-SCF-40 | IdentityCommitments.setCommitment / revokeCommitment | commitment with expiry | ⟦SCF-IDTX-??⟧ | BP-L6-04 | 14,18 | 30 | I | IDTX |
| RV-SCF-41 | ZkVinGate.admit | proof-gated admission | ⟦SCF-ZKVIN-??⟧ | BP-L1-06 | 07 | 11 | M (#58) | SecC |
| RV-SCF-42 | ZkVinGate.anchorCommitment | VIN commitment anchor | ⟦SCF-ZKVIN-??⟧ | BP-L6-05 | 07,18 | 30 | M (#58) | SecC |

### 3.11 RV-NET — Network and nodes

Where the stack physically lives: **L0.1–L0.4** links and **LH.5** hosts, with node roles defined by L3.2 clients. Abstraction runs from "a vehicle talks to an RSU" to "a UDP datagram over PC5".

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-NET-01 | Validator node | proposes/votes | L3.2, LH.5 | ⟦IMP-L3.2-?? Besu⟧; T-12 | BP-L3-01, L4-04 | 02,10 | PF-16 | 04,02 | Ds | Scale |
| RV-NET-02 | RPC node | serves reads/writes | L0.4, LH.5 | ⟦IMP-L3.2-??⟧ | BP-L0-01, L2-05 | 12,10 | — | 26 | M (#39, local) | Lat |
| RV-NET-03 | Archive node | full history | L2.2 | T-10 | BP-L0-05 | 10,16 | PF-05 | 27 | — | Scale |
| RV-NET-04 | Bootnode | discovery entry | L0.3 | T-02 | BP-L0-01 | 10 | PF-01′ | 02 | — | Scale |
| RV-NET-05 | RSU | roadside unit, credentialed | LH.3, L7.3 | C3 | BP-L7-01 | 12,14 | PF-28 | 16 | M (#44–#47, Sim) | Lat |
| RV-NET-06 | OBU | on-board unit | LH.3 | ⟦HW-?? OBU⟧ | BP-L7-01 | 12,13 | PF-31 | 15,16 | — (Sim only) | Lat |
| RV-NET-07 | TMC / controller | traffic management centre | L7.3 | C3; #48 path | BP-L6-03 | 12 | — | 10 | M (#48) | Lat |
| RV-NET-08 | DIDComm mediator | message relay | L7.2 | T-I18 | BP-L7-02 | 09,10 | — | — | Ds | Roots |
| RV-NET-09 | Tx relayer / bundler | submits on behalf | L5.3 | RV-TX-06/07 | BP-L5-05 | 07,21 | — | 07 | M (#50) | Cost |
| RV-NET-10 | P2P link (node–node) | devp2p link | L0.3 | RV-PROT-05 | BP-L0-01, L0-02 | 10 | PF-02′ | 18 | — | Scale |
| RV-NET-11 | V2X sidelink (PC5) | direct vehicle link | L0.1 | `cv2x_stack.py` path loss, CBR | BP-L0-02 | 11,13 | ⟦PF-?? PDR⟧ | 16,25 | I (model) | Lat |
| RV-NET-12 | Backhaul (Uu / fibre) | RSU ↔ cloud | L0.1, L0.2 | T-01 | BP-L0-02 | 10,12 | — | 16 | — | Lat |
| RV-NET-13 | Local Hardhat node | in-process or HTTP | L3.2 | SOL-01 | — | 12 | — | 26 | M (M1, M1-H/HTTP) | Roots |
| RV-NET-14 | Docker testbed network | multi-container | LH.5 | `cv2x-testbed/docker/` | BP-L0-02 | 10 | — | 18 | I | Scale |

### 3.12 RV-DLT — The DLT as a system

The ledger viewed whole: **L2–L4** properties a reader trusts without seeing. This is where the programme's settlement choice (SOL-01..05) lives.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-DLT-01 | Ledger (append-only order) | one history | L2.1, L3 | T-09, T-10 | BP-L2-02 | 16,02 | PF-13 | 01,03 | S | Roots |
| RV-DLT-02 | Finality | irreversible acceptance | L3.1 | T-12/T-13 | BP-L3-01, L3-05 | 01 | PF-17, PF-19 | 03,05 | Ds (automine trivial) | Scale |
| RV-DLT-03 | State (world state trie) | account/storage map | L2.1 | T-08; MPT | BP-L2-01 | 08 | — | 02 | M (#49 SSTORE counts) | Cost |
| RV-DLT-04 | Permissioning | who may run/send | L4.2 | SOL-02 | BP-L4-06 | 02,18 | — | 28 | Ds | Roots |
| RV-DLT-05 | Governance | validator/issuer admission | L4.2 | SOL-02, SOL-05 | BP-L4-06, L4-04 | 02 | PF-16 | 04,28 | Ds | WHY |
| RV-DLT-06 | Upgrade | client/contract change | L4.2, L5.2 | BP-L5-04 | BP-L5-04 | 04 | — | 02 | — (no proxies in repo, cf. RV-SC rows) | SecC |
| RV-DLT-07 | Fork / reorg | competing history | L3.1 | T-13 | BP-L2-02, L3-05 | 01,02 | PF-19, PF-21 | 03 | S | Roots |
| RV-DLT-08 | Checkpoint | commitment to public chain | L2, L3 | SOL-03 | BP-L4-04 | 16 | PF-13 | 13,14 | Ds | Roots |
| RV-DLT-09 | Anchoring (commitment form) | EDPB-compatible anchor | L2.3 | SOL-03; T-I15 | BP-L6-05 | 18,09 | PF-04′ | 30 | Ds | Roots |
| RV-DLT-10 | Capacity ceiling | ops/s per configuration | L4.3 | PF-24 | BP-L4-05 | 11 | PF-24 | 05,06 | Dv (PF-24) | Scale |
| RV-DLT-11 | Fee market | price of inclusion | L4.1 | EIP-1559 | BP-L4-03 | 07,14 | PF-23 | 07 | Ds | Cost |
| RV-DLT-12 | Settlement option A/B/C | HAA-1 Plane A choice | L3–L5 | SOL-02, SOL-04, SOL-05 | BP-L3-06, L4-04 | 03 | R4 §4 | 18 | Ds | Roots |

### 3.13 RV-IMPL — Implementations, clients, tooling

Concrete software at **L3.2, L1.2, L7.1** and the evaluation tools that host it (R6 IMP-).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-IMPL-01 | Hardhat Network | in-process EVM, chain 31337 | L3.2 | ⟦IMP-L3.2-??⟧; `1_blockchain-identity/hardhat.config.js` | — | 07,12 | — | 02 | M (M1 class) | Roots |
| RV-IMPL-02 | Hyperledger Besu | consortium client | L3.2 | ⟦IMP-L3.2-??⟧; `cv2x-testbed/V2_DESIGN.md` | BP-L3-03 | 01,10 | ⟦PF-??⟧ | 02,03 | Ds | Scale |
| RV-IMPL-03 | Geth | public client | L3.2 | ⟦IMP-L3.2-??⟧ | — | 10 | — | 02 | — | New |
| RV-IMPL-04 | Anvil | Foundry node | L3.2 | ⟦IMP-L3.2-??⟧ | — | 12 | — | 02 | — | New |
| RV-IMPL-05 | Sepolia | public testnet, chain 11155111 | L3.2 | `SEPOLIA_VALIDATION.md` | BP-L4-03 | 07 | — | 18 | M2 witness of gas only | Cost |
| RV-IMPL-06 | Docker testbed | containerised stack | LH.5 | `cv2x-testbed/docker/` | — | 10 | — | 18 | I | Scale |
| RV-IMPL-07 | SUMO | traffic simulation | L7.3 | `cv2x-testbed/sumo/` | — | 11 | — | 25 | E (#15: configured, not run) | Scale |
| RV-IMPL-08 | ethers.js | JS client | L7.1 | ⟦IMP-L7.1-??⟧ | BP-L7-01 | 12 | — | 26 | M (harness) | Cost |
| RV-IMPL-09 | web3.py | Python client | L7.1 | ⟦IMP-L7.1-??⟧ | — | 12 | — | 26 | M (#21 overhead noted) | Lat |
| RV-IMPL-10 | snarkjs | prover/verifier | L1.2 | ⟦IMP-L1.2-??⟧ | BP-L1-06 | 12 | — | 11 | M (#57) | SecC |
| RV-IMPL-11 | circom | circuit compiler | L1.2 | ⟦IMP-L1.2-??⟧ | BP-L1-06 | 04 | — | 11 | M (#56) | SecC |
| RV-IMPL-12 | solc 0.8.24 / viaIR / cancun | compiler config | L5.1 | M1 tag | BP-L5-04 | 07 | — | 02 | M (M1 class) | Cost |
| RV-IMPL-13 | Python VC/DID layer | `2_w3c-ssi-layer/` | L6.2 | — | BP-L6-09 | 19 | — | 09 | M (#4) | RIM |
| RV-IMPL-14 | W3C DID test suite | external conformance | L6.1 | T-I17 | — | 19 | — | 08 | M (#24) | RIM |
| RV-IMPL-15 | did-resolver / Veramo / ACA-Py | agent frameworks | L7.1 | T-I21 | — | 19 | — | 09 | — | New |
| RV-IMPL-16 | Indy-node / anoncreds-rs | O10/O12 implementations | L3.2, L1.2 | T-I20, T-I21 | BP-L1-05 | 06,19 | PF-10 | 09 | Ds | Roots |

### 3.14 RV-HW — Hardware

**LH**, the new bottom layer: the physical trust anchors keys and clocks rest on (R6 HW-).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-HW-01 | Secure element (SE / eSIM) | in-vehicle key store | LH.2 | ⟦HW-??⟧ | BP-L1-07, ⟦BP-LH-??⟧ | 06,20 | PF-12 | 15 | — | SecC |
| RV-HW-02 | HSM | issuer/CA key store | LH.2 | ⟦HW-??⟧ | BP-L6-03 | 06,12 | ⟦PF-?? HSM sign latency⟧ | 15 | — | SecC |
| RV-HW-03 | TEE | isolated execution | LH.2 | ⟦HW-??⟧ | BP-L1-07 | 06 | PF-12 | 15 | — | SecC |
| RV-HW-04 | TPM | host attestation | LH.2 | ⟦HW-??⟧ | ⟦BP-LH-??⟧ | 06 | — | 15 | — | SecC |
| RV-HW-05 | ECU / gateway | vehicle compute, CAN/Ethernet | LH.3 | ⟦HW-??⟧ | BP-L7-01 | 12,05 | — | — | — | New |
| RV-HW-06 | OBU hardware | V2X host | LH.3 | ⟦HW-??⟧ | BP-L7-01 | 12,13 | PF-31 | 16 | — | Lat |
| RV-HW-07 | V2X modem | PC5/802.11p radio | LH.4 | ⟦HW-??⟧ | BP-L0-02 | 13,11 | ⟦PF-??⟧ | 16 | — | Lat |
| RV-HW-08 | GNSS receiver | time + position | LH.4 | ⟦HW-??⟧ | ⟦BP-LH-?? spoofing⟧ | 15,05 | ⟦PF-??⟧ | — | — | SecC |
| RV-HW-09 | Node server | validator/RPC host | LH.5 | ⟦HW-??⟧ | BP-L0-02 | 10,12 | — | 02 | — | Scale |
| RV-HW-10 | CPU / RNG | primitives' silicon | LH.1 | ⟦HW-??⟧ | BP-L1-01 | 12,06 | PF-06 | 15 | M (host-dependent timings, #27 M0) | Lat |
| RV-HW-11 | GPU (attacker) | brute-force capacity | LH.1 | — | BP-L6-05 | 06,09 | — | 30 | E (#60 extrapolation) | SecC |

### 3.15 RV-SVC — Off-chain services

HAA-1 Planes V and D and their helpers, at **L2.3 / L7.1**. They carry what the ledger should not: content, status distribution, caches.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-SVC-01 | Resolver service | DID → document | L6.1, L7.1 | RV-READ-01; SOL-05 | BP-L2-05 | 12,10 | PF-31 | 26 | M (#31, local) | Lat |
| RV-SVC-02 | Verifier service (cached) | σ-bounded decisions | L7.1 | `freshness.py`; SOL-05 Plane V | BP-L7-03 | 14,15 | PF-15 | 19 | M (#32, #37) | Lat |
| RV-SVC-03 | Status service | publishes list/root | L2.3 | SOL-09 | BP-L6-07, L0-05 | 10,14 | PF-29 | 12 | Ds | Lat |
| RV-SVC-04 | Archive (Plane D) | content availability | L2.3 | SOL-05 | BP-L0-05, L2-04 | 10,18 | PF-05 | 27 | Ds | Scale |
| RV-SVC-05 | IPFS / CAS | content addressing | L2.3 | T-02, T-07 | BP-L2-04 | 10 | PF-05 | 27 | — | Scale |
| RV-SVC-06 | Steward agent | disclosure control | L7.1 | `5_zkp-agent-identity/steward/` | BP-L6-05 | 09,22 | ⟦PF-??⟧ | 22 | M (#61) | SecC |
| RV-SVC-07 | Oracle | off-chain fact on-chain | L5.2 | — | BP-L6-07 | 04,16 | — | — | — | New |
| RV-SVC-08 | Keeper (intent fulfiller) | executes `fulfil` | L7.1 | RV-IDTX-22 | BP-L3-06 | 21,10 | — | 05 | I | IDTX |
| RV-SVC-09 | Issuer service | signs VCs | L7.1 | `vc_issuer.py` | BP-L6-03 | 12 | — | 15 | M (#21 issue) | RIM |
| RV-SVC-10 | Trust registry service | accredited issuers | L4.2, L6 | RV-GOV-02 | BP-L4-06 | 02 | — | 28 | I (on-chain lists) | WHY |

### 3.16 RV-SCN — Application scenarios

**L7.3**: the reasons the stack exists. Each scenario composes rows above; measuring it means measuring its chain.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-SCN-01 | Tolls | identity-gated payment | L7.3 | RV-IDTX-25; RV-SCF-30 | BP-L5-05 | 07,13,09 | PF-31 | 07,18 | I | IDTX |
| RV-SCN-02 | Gated access (zk) | admit on predicate | L7.3 | RV-IDTX-28 | BP-L1-06 | 09,07 | PF-11 | 11 | M (#58) | SecC |
| RV-SCN-03 | Licence class endorsement 7 → 5 | upgrade a driver credential | L7.3 | RV-VC-03; §4(a) | BP-L6-03, L6-04 | 14,16,18 | PF-28 | 09,12 | Ds | New |
| RV-SCN-04 | Maintenance record | service history | L7.3 | RV-SCF-19, RV-SCF-28 | BP-L6-07 | 07,16 | — | 17 | M (#35) | MV1 |
| RV-SCN-05 | Crash record | forensic event | L7.3 | RV-VC-16; R2 gap (availability owner) | BP-L0-05, L6-07 | 16,10 | PF-05 | 27 | Ds | MV1 |
| RV-SCN-06 | Ownership transfer | sale | L7.3 | RV-SCF-17 | BP-L5-05 | 07,16 | — | 17 | M (#35) | MV1 |
| RV-SCN-07 | Pay-per-use | metered service | L7.3 | RV-IDTX-22 | BP-L4-03 | 07 | PF-23 | 07 | — | New |
| RV-SCN-08 | RSU SPaT | signed signal timing | L7.3 | RV-PROT-11 | BP-L7-07 | 12,13,14 | PF-31 | 19,24 | M (#44, #46) | Lat |
| RV-SCN-09 | I2I message | infrastructure-to-infrastructure | L7.3 | C3; #48 TMC path | BP-L7-05 | 12,05 | — | 10 | M (#48 crypto cost only) | Lat |
| RV-SCN-10 | V2V BSM authentication | per-message trust | L7.3 | §4(c) | BP-L7-07 | 13,11 | PF-31 | 24,25 | M (#27) | Lat |
| RV-SCN-11 | Agent identity | AI/agent acting for vehicle | L7.3 | T-I22; Set C | BP-L6-06 | 04,09 | — | 21 | Ds | New |
| RV-SCN-12 | Pseudonymous V2X | rotating identities | L7.3 | RV-SIG-12 | BP-L6-05 | 09,07 | PF-04′ | 22 | M (#38) | SecC |
| RV-SCN-13 | Vehicle birth | manufacturer creates identity | L7.3 | RV-VC-15 | BP-L6-03 | 07 | — | 17 | M (#33) | MV1 |

### 3.17 RV-GOV — Governance and regulatory

Mostly **L4.2** plus the legal envelope above L7. Few of these are measurable in units; their MD is usually MD-18 or MD-02.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-GOV-01 | Validator admission | who joins consensus | L4.2 | SOL-02; T-03 | BP-L4-06, L4-04 | 02 | PF-16 | 04,28 | Ds | WHY |
| RV-GOV-02 | Issuer accreditation / trust registry | who may issue | L4.2, L6 | ⟦SCF-MOBIV2-?? authorizeIssuer⟧ | BP-L6-03, L4-06 | 02,04 | — | 28 | I | WHY |
| RV-GOV-03 | GDPR erasure | right to be forgotten | — (legal) | R2 §4 | BP-L6-05 | 18 | — | 17,30 | Ds | WHY |
| RV-GOV-04 | EDPB commitment-form posture | no personal data on chain | — | SOL-03; T-I15 | BP-L6-05 | 18,09 | PF-08 | 30 | Ds (#60 shows unsalted VIN hash reversible) | SecC |
| RV-GOV-05 | Audit | after-the-fact proof | L4.2, L5 | PF-13; R3 R4 | BP-L4-04 | 16 | PF-13 | 13 | Ds | SecC |
| RV-GOV-06 | Key-ceremony governance | trusted setup | L1 | T-I14 | BP-L1-06 | 06 | PF-11 | 11 | — | SecC |
| RV-GOV-07 | Registry authority transfer | admin handover | L5.2 | ⟦SCF-MOBIV1-?? transferRegistryAuthority⟧ | BP-L4-06, L5-04 | 04 | — | 28 | I | MV1 |
| RV-GOV-08 | Standards conformance claim | W3C / MOBI | — | RV-MET-05 | — | 19 | — | 08 | M (#4, #24) | RIM |

### 3.18 RV-MET — Evaluation artefacts

How evidence anchors *upwards*: each artefact turns a Ds row into M. These sit outside the stack; their anchor is the row they evidence.

| RV | Item | Meaning | Evidences | Anchors | MD | St | Deepen in |
|---|---|---|---|---|---|---|---|
| RV-MET-01 | Claim register (`MEASUREMENT_CONDITIONS.md`) | every number with status | all M rows | 63 rows (count of numbered lines, 2026-10-23) | 17 | M | Roots |
| RV-MET-02 | Hardhat test suites | contract behaviour | RV-SC, RV-SCF | 541 Hardhat (STATUS §1.1) | 04 | M | RIM |
| RV-MET-03 | Python tests | VC/DID/testbed | RV-VC, RV-READ | 342 Python (STATUS §1.1) | 04,19 | M | RIM |
| RV-MET-04 | Metrics harness (L1–L6, ten columns) | gas, footprint, reads | RV-IDTX, RV-SCF | #29–#36, #49–#51 | 07,08,12 | M | Cost |
| RV-MET-05 | W3C checker + external DID suite | conformance | RV-IDTX-02 | #4, #24 | 19 | M | RIM |
| RV-MET-06 | Security matrix (43 attacks) | SC security | RV-SC | #28 | 04 | M | SecC |
| RV-MET-07 | Pre-registered I1–I5 | infrastructure messaging | RV-SCN-08/09 | #44–#48 | 12,14 | M | Lat |
| RV-MET-08 | Freshness experiments | W, σ | RV-ALG-09 | #32, #37, #52, #55 | 14,15 | M | Lat |
| RV-MET-09 | IDTx tests + mutants | executor behaviour | RV-IDTX-21..24 | `phase2/idtx/test/idtx.test.js`; `mutate_idtx.sh` | 04 | I | IDTX |
| RV-MET-10 | ZK bench + attacks | ZK costs, leakage | RV-PRIM-10, RV-VC-07 | #56–#62 | 07,09,12 | M | SecC |
| RV-MET-11 | CI (8 jobs, document checks) | regression | all | `.github/workflows/` | 17 | M | RIM |
| RV-MET-12 | Sepolia witness | gas external validity | RV-IMPL-05 | `SEPOLIA_VALIDATION.md` | 07 | M2 gas only | Cost |
| RV-MET-13 | Defect log | known faults | RV-SC | `docs/DEFECT_LOG.md` (66 logged, 18 open, STATUS §1.1) | 04 | M | SecC |
| RV-MET-14 | Crux register | thesis claims ↔ rows | RV-SCN | `docs/thesis/CRUX_REGISTER.md` C1–C8 | 17 | M | G-RIM |
| RV-MET-15 | Consensus/finality testbed | MD-01/02 measurement | RV-DLT-02, RV-ALG-01 | — (needs multi-node Besu) | 01,02,10 | — | Scale |

### 3.19 RV-THR — Threat and adversary operations (added category)

The attacks the BP- rows abstract, phrased as *operations* so they can be measured like any other function. Mostly SecC.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St | Deepen in |
|---|---|---|---|---|---|---|---|---|---|---|
| RV-THR-01 | VIN-hash enumeration | reverse unsalted commitment | L1.1 | RV-PRIM-02 | BP-L6-05 | 09,06 | PF-08 | 30 | M (#60) | SecC |
| RV-THR-02 | Predicate narrowing | twenty-questions | L6.2 | RV-VC-07 | BP-L6-05 | 09 | ⟦PF-??⟧ | 22 | M (#61) | SecC |
| RV-THR-03 | Stale-cache acceptance | use revoked identity | L7.1 | RV-ALG-09 | BP-L7-03 | 14 | PF-28 | 19 | M (#46) | Lat |
| RV-THR-04 | Replay / forgery of SPaT | message attacks | L7.2 | RV-ALG-10 | BP-L7-04 | 05 | — | 20 | M (#45) | SecC |
| RV-THR-05 | Rotation race | attacker vs owner rotation | L6.3 | RV-IDTX-03 | BP-L6-02 | 21 | PF-25 | 05 | — (single node, I-24 §2.2) | IDTX |
| RV-THR-06 | Validator collusion | rewrite private history | L4.2 | RV-GOV-01 | BP-L4-04 | 02,16 | PF-13, PF-16 | 04 | Dv | Scale |
| RV-THR-07 | Eclipse of RPC client | false view | L0.3 | RV-NET-02 | BP-L0-01 | 05 | PF-01′ | 18 | — | SecC |
| RV-THR-08 | Contract attack matrix | 43 attacks | L5.2 | RV-MET-06 | BP-L5-04 | 04 | — | — | M (#28) | SecC |
| RV-THR-09 | Sybil split vs per-verifier cap | defeat static cap | L7.1 | RV-SVC-06 | BP-L6-05 | 09 | — | 22 | M (#61) | SecC |
| RV-THR-10 | GNSS spoofing | false time/position | LH.4 | RV-HW-08 | ⟦BP-LH-??⟧ | 15,05 | ⟦PF-??⟧ | — | — | SecC |

---

## 4. Five worked anchor chains

Each chain starts at the top and descends one step per line, naming the layer and the tag that carries the step; MDs on which the whole chain can be judged follow.

### 4(a) A VC endorsement — licence class upgrade (class 7 → class 5)

1. **L7.3** RV-SCN-03 — licensing authority decides to upgrade the holder.
2. **L7.1** RV-SVC-09 issuer service builds a new class-5 credential.
3. **L6.2** RV-VC-03 = RV-VC-01 (issue, I5) + RV-VC-11 (suspend/revoke class-7, I8).
4. **L6.1** issuer DID resolved by verifiers later (RV-READ-01; T-I17).
5. **L1.1** RV-SIG-01 issuer signs (T-05/T-06); in an O12 profile RV-SIG-08 CL/BBS+ instead (T-I11).
6. **LH.2** RV-HW-02 issuer key in HSM (⟦HW-??⟧; BP-L6-03).
7. **L6.3** RV-IDTX-12 revokeCredential on the old class (SOL-09 profile, PAR-12).
8. **L5.2** status anchor: e.g. RV-SCF-25 / RV-SCF-23 or a status-list root (⟦SCF-??⟧).
9. **L5.3 → L3** RV-TX-01 write ordered (RV-ALG-02 on Hardhat today; RV-ALG-01 QBFT in design).
10. **L2.3** RV-SVC-03 status service republishes list; verifiers' caches converge (PF-15).
11. **L7.2** holder presents class 5 (RV-VC-04, RV-PROT-02); verifier checks (RV-VC-08/09).
**MDs:** 14 (W between upgrade and old-class refusal), 16 (audit of who endorsed), 18 (no licence data on chain), 06, 07. **Status:** Ds end to end; the parts (issue, revoke, verify) are M in other contexts (#21, #46). **Gap:** no repo representation of endorsement-as-supersession.

### 4(b) A DID resolution read at Tier 2

1. **L7.3** a verifier at an intersection needs the sender's key (Tier 2, PF-31).
2. **L7.1** RV-SVC-02 cached verifier: hit → RV-READ-03 (`freshness.py`); miss or k-th → refresh.
3. **L6.1** RV-READ-04 probe: one `getIdentityInfo` call; if changed, RV-READ-01 full event replay.
4. **L0.4** RV-PROT-07 JSON-RPC (`eth_call`, `eth_getLogs`) over PAR-26 transport.
5. **L3.2** RV-NET-02 RPC node (Hardhat today, RV-IMPL-01).
6. **L2.2/L2.1** logs and state read (RV-DLT-03); history length h drives call count.
7. **LH.5** RV-HW-09 host.
**MDs:** 12 (#31: grows with h; #37 probe), 13 (fit vs PF-31 Tier 2), 15 (σ, #52), 10, 09 (RPC provider sees who is resolved — BP-L0-04). **Status:** M at M1/M1-H/HTTP; M2 not measured. **Gap:** remote-RPC latency (RV-READ-12).

### 4(c) A signature on a V2X BSM

1. **L7.3** RV-SCN-10 vehicle broadcasts at 10 Hz (`LATENCY_BUDGET.md` §1).
2. **L7.2** RV-PROT-10 J2735 BSM built (`cv2x_stack.py` `BSM.from_vehicle_state`); in production a 1609.2 SPDU (RV-PROT-08, Ds).
3. **L6.1** sender key = DID verification method or pseudonym certificate (RV-SIG-11/12).
4. **L1.1** RV-SIG-01 ECDSA sign (PAR-10); **LH.2** key in SE (RV-HW-01).
5. **L0.1** RV-NET-11 PC5 sidelink (PAR-16), resource selection RV-ALG-12.
6. Receiver **L1.1** RV-SIG-02 verify; **L7.1** RV-ALG-09 freshness and RV-ALG-10 replay check.
7. **L7.3** decision within identity budget f (PAR-24).
**MDs:** 12 (#27 warm/cold), 13 (Tier 1), 11 (neighbour saturation, `LATENCY_BUDGET.md` §2), 06, 09 (linkability via stable key), 14. **Status:** verify M (#27, M0); radio I (model); 1609.2 encoding Ds. **Gap:** end-to-end with radio.

### 4(d) revokeCredential and the window W

1. **L7.3** authority revokes RSU or vehicle credential (RV-SCN-08).
2. **L6.3** RV-IDTX-12 revokeCredential; **L6.2** RV-VC-10.
3. **L5.2** RV-SCF-13 `revokeIdentity` (testbed) or status-list update.
4. **L5.3 → L3.1** RV-TX-01, ordered; ledger share of W per option (PF-28: Option A ledger share small, Option C hours via PF-19).
5. **L2.3** RV-SVC-03 status published.
6. **L7.1** verifier caches refresh every k (PAR-19) — RV-ALG-09; acceptances after revocation ≤ k − 1.
7. Checkpoint (RV-DLT-08) makes the timing forensic, does not shorten W (R3 Part IV).
**MDs:** 14 (#32, #37, #46), 15, 16, 07 (#22 revoke gas), 09 (PF-29 if whole-list fetch). **Status:** M for k-bound (#46 PASS) on in-process registry; Ds for public settlement share.

### 4(e) A write transaction to finality and checkpoint

1. **L6.3** an identity op (e.g. RV-IDTX-03 changeOwner) is requested.
2. **L7.1** ethers/web3.py (RV-IMPL-08/09) builds and signs (RV-SIG-01; RNG RV-PRIM-14, LH.1).
3. **L5.3** RV-TX-01 EIP-1559 (or RV-TX-06 relayed, RV-TX-07 UserOp).
4. **L0.4 → L0.3** submitted via JSON-RPC; gossiped (RV-TX-15, RV-PROT-05).
5. **L4.1** fee rule (PAR-07); **L4.3** capacity (PF-24).
6. **L3.1** ordering: automine (RV-ALG-02, M) / QBFT (RV-ALG-01, Ds) — finality MD-01 via PF-17.
7. **L5.1** EVM executes; gas metered (RV-ALG-08); state and logs written (RV-DLT-03, RV-TX-14).
8. **L2.2** persisted (⟦IMP-L2.2-?? RocksDB/LevelDB⟧).
9. **L5.3** RV-TX-09 checkpoint to public chain every τ_a (PAR-13; SOL-03).
10. Detection of rewrite ≤ τ_a + t_pub (PF-13).
**MDs:** 01, 02, 07 (#2), 08 (#49), 11, 16, 21. **Status:** steps 1–7 M on Hardhat; 6 (BFT), 9–10 Ds.

---

## 5. Coverage matrix — categories × MD dimensions

Cell code: **●** measurable now (≥ 1 row M or Dv on that MD) · **○** design only (rows exist, Ds/I/E/S) · **·** empty (no row targets this MD). Columns are MD numbers.

| Cat | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TX | ○ | · | · | ○ | ○ | · | ● | ● | ○ | · | ● | ● | · | · | ● | ○ | ● | ○ | · | ○ | ● | · |
| IDTX | ○ | · | · | ● | · | ● | ● | ● | ● | · | · | ● | ● | ● | ● | ● | ● | ○ | ● | · | ○ | · |
| VC | · | · | · | · | · | ● | ● | ● | ● | · | · | ● | ● | ● | ● | ● | ● | ○ | ● | · | · | ● |
| SIG | · | · | · | · | ○ | ● | ● | · | ● | · | · | ● | ○ | ○ | · | · | ● | · | · | ○ | ○ | · |
| READ | · | · | · | · | ○ | · | ○ | · | ● | ○ | ● | ● | ● | · | ● | ○ | ● | · | ● | · | · | · |
| PRIM | · | · | · | · | ○ | ● | ● | · | ● | · | · | ● | · | · | · | · | ● | ○ | · | · | · | · |
| ALG | ○ | ○ | · | · | ● | ○ | ● | · | ● | ○ | ○ | ● | · | ● | ● | · | ● | · | ● | · | · | ● |
| PROT | · | · | · | · | ○ | · | ● | · | ○ | ○ | ● | ● | ● | · | · | ○ | ● | · | ● | · | · | · |
| SC | · | · | · | ● | · | · | ● | ● | ● | · | · | ● | · | ● | · | ● | ● | · | ● | ○ | ○ | · |
| SCF | · | ○ | · | ○ | · | · | ● | ● | ● | · | · | · | · | ● | · | ● | ● | ○ | · | ○ | ○ | · |
| NET | · | ○ | · | · | · | · | ● | · | ○ | ○ | ○ | ● | ○ | ● | · | · | ● | · | · | · | ● | · |
| DLT | ○ | ○ | ○ | ○ | · | · | ○ | ● | ○ | · | ● | · | · | ○ | · | ○ | ● | ○ | · | · | · | · |
| IMPL | ○ | · | · | ● | · | ○ | ● | · | · | ○ | ○ | ● | · | · | · | · | ● | · | ● | · | · | · |
| HW | · | · | · | · | ○ | ○ | · | · | ○ | ○ | ○ | ● | ○ | · | ○ | · | ● | · | · | ○ | · | · |
| SVC | · | ○ | · | ○ | · | · | · | · | ● | ○ | · | ● | · | ● | ● | ○ | ● | ○ | ● | · | ○ | ● |
| SCN | · | · | · | · | ○ | · | ● | · | ● | ○ | ● | ● | ● | ● | · | ● | ● | ○ | · | · | · | · |
| GOV | · | ○ | · | ○ | · | ○ | · | · | ● | · | · | · | · | · | · | ○ | ● | ○ | ● | · | · | · |
| MET | ○ | ○ | · | ● | · | · | ● | ● | ● | ○ | · | ● | · | ● | ● | · | ● | · | ● | · | · | · |
| THR | · | ● | · | ● | ● | ● | · | · | ● | · | · | · | · | ● | ○ | ● | ● | · | · | · | ○ | · |

**Headline (19 × 22 = 418 cells):** **● 128 measurable now** (≈ 31 %), **○ 83 design-only** (≈ 20 %), **· 207 empty** (≈ 50 %). Column view: MD-07 cost, MD-12 latency and MD-17 evidence status are dense; **MD-01 finality, MD-02 decentralisation confidence, MD-03 trilemma position and MD-10 availability have no ● cell except one Dv** (RV-THR-06 on MD-02) — the consequence of a single automining node; MD-20 recoverability and MD-18 regulatory posture are design-only everywhere.

---

## 6. Where to deepen — routing table

| Category | Best chat | Why | Second |
|---|---|---|---|
| RV-TX | Cost thread | gas per tx type is its native unit (#25, #50) | Scale (capacity) |
| RV-IDTX | IDTX work chats | I-24 brief, executor, P2-D8 definition live there | Cost |
| RV-VC | G-RIM | VC layer code and function cards (F5–F8) are RIM material | new chat for licence endorsement (RV-VC-03) |
| RV-SIG | Security campaign G-C1 | key custody, nonce, recovery are threat-model items | Latency (verify cost) |
| RV-READ | Latency thread | Tier 2 and σ are its questions (#31, #37, #52) | Scale (history growth) |
| RV-PRIM | this Roots thread (R7) | bounds are PF material; ZK costs to SecC | Security campaign |
| RV-ALG | this Roots thread (R6/R7) | ALG- defined in R6, bounded in R7 | Scale (consensus) |
| RV-PROT | Latency thread | J2735/1609.2 budget; DIDComm to Roots | Security campaign |
| RV-SC | Cost thread | nine-standard tables | Security campaign (attack matrix) |
| RV-SCF | IDTX work chats + Cost | function-level dependency and gas | G-MV1 for MOBI functions |
| RV-NET | Scale thread | multi-node, density, backhaul | Latency |
| RV-DLT | Scale thread | finality/decentralisation need a multi-node testbed | this Roots thread (settlement option theory) |
| RV-IMPL | Scale thread | Besu bring-up is the missing implementation | G-RIM (inventory) |
| RV-HW | Security campaign | LH trust anchors | new chat (vehicle E/E) |
| RV-SVC | Latency thread | Plane V caches dominate W | Scale (Plane D) |
| RV-SCN | G-MV1 MOBI VID (vehicle lifecycle); Latency (SPaT/BSM) | scenario owners | new chat (tolls, licence, pay-per-use) |
| RV-GOV | G-WHY | posture and admission are argument, not measurement | Security campaign (audit) |
| RV-MET | G-RIM | Appendix B test/trace index is the home | this Roots thread (register discipline) |
| RV-THR | Security campaign G-C1 | adversary operations | Latency (stale-cache) |

---

## 7. HANDOFF (v0-1 → v0-2)

**Files.** `docs/roots/phase2/80_R8_reverse_register/claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-1.md` (this). Nothing else written.

**Tags assigned.** RV- 301 rows in 19 categories: TX 15 · IDTX 25 (01–16, 20–28) · VC 19 · SIG 14 · READ 13 · PRIM 15 · ALG 14 · PROT 15 · SC 20 · SCF 42 · NET 14 · DLT 12 · IMPL 16 · HW 11 · SVC 10 · SCN 13 · GOV 8 · MET 15 · THR 10 (added category). MD-01..MD-22. PAR-01..PAR-30. **Consumed:** L0–L7, LH/L0.1–L7.3, T-, T-I-, SOL-01..09, BP- (R3), PF-01..31 and PF-01′..04′, register rows #1–#63.

**Five decisions.**
1. Status scale adds **I** (implemented, unmeasured) between Ds and M, so IdtxExecutor and similar code are not mislabelled as either design or result.
2. IMinimalSSI functions are keyed by name and catalogue op, not F-number (F-numbering is [B1], row #53), except F8.
3. MD-08 storage footprint, MD-21 ordering-race window and MD-22 operational burden added beyond the brief's list.
4. RV-THR added: attacks as measurable operations.
5. Coverage cell ● requires an M or Dv row in that category on that MD; I does not count.

**Placeholders to resolve against R6/R7.** All ⟦SCF-…-??⟧ (≈ 60, one per RV-SCF row and IDTX/SC cross-references); ⟦IMP-L3.2/L1.2/L7.1/L2.2-??⟧; ⟦PRO-??⟧ for JSON-RPC, devp2p, 1609.2, Engine API; ⟦ALG-??⟧ ECDSA, ecrecover, MPT proof; ⟦HW-??⟧ all of RV-HW; ⟦BP-LH-??⟧ (GNSS spoofing, SE extraction); ⟦SOL-1?⟧ IdtxExecutor, zk VIN, steward; ⟦PF-??⟧ QBFT finality, Nakamoto coefficient, relay overhead, SC defect model, linkability metric, prover time, HSM latency, PDR/CBR.

**Corrections.** None to Phase 1. Note: IDTX numbering gap 17–19 is deliberate, reserved for Set C functions; row count (301) verified by script against the tables.

**Open questions.** **Q-R7** Is licence endorsement a supersession (new VC + revoke) or an attestation on the existing VC (RV-VC-02 pattern)? **Q-R8** Which chat owns MD-01/02/10 — Scale needs a multi-node Besu run that no thread has scheduled. **Q-R9** Should M2 (Sepolia) latency be measured at all, given `SEPOLIA_VALIDATION.md` disclaims it? **Q-R10** Is 1609.2 encoding in scope, or does the thesis stay at SSI/PKI provider abstraction (RV-PROT-08)?
