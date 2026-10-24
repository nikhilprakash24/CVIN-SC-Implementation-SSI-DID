# CVIN-SC · Roots Phase 2 · R8 — Reverse Anchor Register

| Field | Value |
|---|---|
| Document | **R8** Reverse Anchor Register |
| Version | **v0-2** (second pass: panel corrections applied, placeholders resolved, PAR registry merged; v0-1 kept unchanged) |
| Date | 2026-10-23 |
| Thread | G-R1 Roots, Phase 2 (branch `roots/G-R1-phase2`) |
| Re-keyed | per R9 §3.1 (Q-R8-nn, KD-R8-nn; retirement lines in §10) · Phase 1 erratum pointer: R9 §3.4 X-1..X-9 |
| Consumes | Phase 1 R1–R4 (L-, T-, T-I-, SOL-01..09, BP-, PF-01..31, SYM-01..24); Phase 2 shared brief v1.0; **R6 v0-1** (HW-, PRO-, ALG-, IMP-, SCF-, BP-LH/Lx.y, SOL-10..17); **R7 v0-1** (PF-32..62, PAR-01..26 → re-mapped here); **R9 v0-1** (PN-22..30, §3.1 Tables A/B, §3.3 Tables C′/D′, §6 PRM/B-nn); repo at 2026-10-22: `docs/MEASUREMENT_CONDITIONS.md` (62 numbered rows), `docs/STATUS_2026-10-22.md` l. 112 (562 Hardhat / 376 Python), contracts cited in-row |
| Owns | **RV-<CAT>-nn** (19 categories, 311 rows) · **MD-01..MD-22** · **PAR-01..PAR-43** (sole PAR- owner; R7 cites these numbers) · Q-R8-01..05 · KD-R8-01..06 |
| Companion | `docs/roots/phase2/80_R8_reverse_register/r8_coverage.py` (recomputes §5 from this file) |

`Progress ▓▓▓▓▓▓▓▓░░ 80 %`. All panel findings against R8 are applied, there are no bracketed placeholders left, and the coverage matrix is recomputed by script. Still to do: replace the open-PF rows (§9) when R7 v0-2 supplies PF-63..66, regenerate FIG-R11, and run the author's PRM tick-off (§7).

---

## 0. How to use this register

**What it is.** Phase 1 and R6 run *upwards*: a primitive enables a layer, and the layer enables a function. R8 runs *downwards*. It starts from something the programme *does*, such as a transaction, a credential endorsement, a read, a signature or an IDTX call. For each one it names: the tags it stands on (L-, T-, T-I-, SOL-, and R6's SCF-/IMP-/PRO-/ALG-/HW-); the breaking points that can defeat it (BP-); the dimensions it can be judged on (MD-); the bound that supplies the number (PF-); the parameters that move the number (PAR-); and how much of this is already evidenced (St).

**Column key.**
| Column | Meaning |
|---|---|
| RV | the register tag, `RV-<CAT>-nn`; frozen once issued, never renumbered |
| Anchors down to | tags the item stands on, nearest first |
| BP | breaking points (R3 Part II; R6 §4 for BP-LH / BP-Lx.y) |
| MD | dimensions. **`aa,bb / cc`**: the MDs before the slash are the ones the St evidence actually covers. The MDs after the slash apply to the item but are not evidenced by that row. With no slash, St covers every listed MD. |
| PF | the bound. R4 PF-01..31 and R7 PF-32..62. "qual." means a qualitative treatment by decision. "req PF-6x" means requested from R7 v0-2. |
| PAR | parameters (§2) |
| St | unified status scale (R9 PN-32): **M** MEASURED (register row #n, status V) · **Dv** DERIVED (PF + inputs) · **I** IMPLEMENTED-UNMEASURED (code/tests, or a source-read fact about code, with no register row) · **Ds** DESIGN · **E** ESTIMATED · **S** STANDARD · **—** absent |

**Rules.**
1. **Anchored** means every cell cites a tag, or carries `—` with a reason. A row whose PF reads "req PF-6x" is *unbounded*. A row with St Ds/E/I/— is *unevidenced*.
2. **Status never upgrades by assertion.** M needs a `MEASURED_CONDITIONS` row with status V, and a number appears only together with its row. Besu, QBFT, public anchoring and HAA-1 Planes V/D are Ds. **The executed chain is one automining Hardhat process (N_v = 1, chain 31337, G = 60 M; R7 PF-39).** A Hardhat latency never goes in an MD-01 cell (R9 SLD-01, NC-01). Sepolia (M2) is a gas witness whose JSON is not committed, so it is I, not M (R9 NC-07).
3. **Adding a row:** take the next free number in its category, and fill Item, then Sub-layer, Anchors, BP, MD, PF, PAR and St. Retire a row with `~~RV-…~~ → RV-…`.
4. **Deepening a category:** follow the "Deepen next" line under each category. The receiving chat returns rows with a version note (`RV-VC-03 v0-3: St Ds→M #nn`). Only the Roots thread merges returns into R8.
5. **Parameters are declared, not set.** No row fixes a PAR value.

**Repo-vocabulary mapping (no silent choice; corrected per PN-22).**
| Repo term | Phase 1 / R8 term |
|---|---|
| "nine standards" in ten harness columns | options per R2 §3.3 via R6 §3: ERC-1056 → **O1** · ERC-1155 → **O2** · ERC-721 → **O3** · (ERC-6551 **O4**, absent) · ERC-725 → **O5** · ERC-725xy + ERC-735 → **O6** · ERC-4337 → **O7** · LSP8 → none (repo-only, Q-R6-02) · CVIN-Combined → O18 precursor (Family F) |
| catalogue ops C1, C2, R1–R4, U1–U5, D1–D3, V1, V3, V5, V6, X1, P1 | IMinimalSSI functions in RV-IDTX. F-numbering inside the sets is **[B1]** (R9 B-01). In prose use "IMS-F*n*" once fixed. |
| condition classes M0, M1, M1-H, M1-H/HTTP, M2, Sim | MD-17 qualifier |
| IDTx (I-24, P2-D8) | RV-IDTX-20..28 |

---

## 1. Measurement dimensions MD-01..MD-22 (now bound to R7 PFs)

Each dimension is a ruler. The formula column cites the PF that turns parameters into a number (R9 Table C′, PN-25). R7 §7's rule holds: cite the PF, not the number.

| MD | Dimension | Definition | Unit | Formula (PF) | Executed-system note |
|---|---|---|---|---|---|
| MD-01 | Time to confirm / finality | submission → inclusion → irreversible acceptance | s; blocks; depth z | **PF-57** E[t_conf] = E[t_incl] + E[t_fin] + E[round-change]; tail **PF-40** (BFT); R4 PF-17/19/20 | PF-39: t_fin ≡ 0 on automine, so no executed value exists |
| MD-02 | Decentralisation confidence | how unlikely a colluding quorum or a monoculture can rewrite or censor | NC; P(collusion); HHI; H | **PF-60** (NC = f_B+1; HHI = Σ s_c²; Shannon H; governance score); R4 PF-16/21/22; correlated failure req **PF-65** | NC = 1, HHI = 1.0 |
| MD-03 | Trilemma position | point (T, L, C) on R3's cost surface | coordinates | **PF-58** T = −log₁₀ PF-16, L = log₁₀ E[t_conf], C = log₁₀ ops/s (PF-49) | L undefined without Δ |
| MD-04 | Smart-contract security | vector over the SCF register | fractions; pass rate; audit class | **PF-61** (a) access-check coverage, (b) replay-protection coverage, (c) mutation kill rate, (d) attack-matrix pass, (e) audit status | (c), (d) M; (a), (b), (e) open (Q-R7-08) |
| MD-05 | Protocol security | properties R1–R8 under the threat model, as a reduction | (class, loss, bits) | **PF-59** bits = minᵢ(−log₂ εᵢ) − log₂(terms) − log₂ n_D; composition **PF-36** (labelled union bound, PN-19); R4 PF-01′, PF-25 | ledger term ε_L = p_c of one operator |
| MD-06 | Cryptographic security level | best generic attack, classical / quantum | bits | **PF-32** ECDSA, **PF-33** keccak/ROM, **PF-34** commitments, **PF-35** Groth16 (setup); R4 PF-06, 08–11 | — |
| MD-07 | Cost | on-chain execution cost; currency only in one dated appendix (#20) | gas (GAS_CHARTER class) | **PF-52** g_F and storage/log (corrected basis, PN-13), **PF-51** Groth16, **PF-49** capacity cost; R4 PF-24 | gas is portable (PF-39) |
| MD-08 | Storage footprint | state and log growth per op | SSTORE z→nz; log bytes | **PF-52** | #49 |
| MD-09 | Privacy / linkability | correlation across uses; anonymity set; hiding | k_A; ℓ; bits | **PF-62** (k_A, ℓ_RF from **PF-44c** corrected ≈ 0.14–0.80, chain-layer ℓ = 60/60 #38, hiding bits PF-33/#60); R4 PF-04′, PF-29 | — |
| MD-10 | Availability / liveness | P(function completes when needed) | P; downtime | **PF-57a** (write = P(≥⌈2N_v/3⌉ up); read; revocation tail PF-48); **PF-37** liveness after GST; R4 PF-02′, PF-05 | one process, so not meaningful |
| MD-11 | Capacity / scale | sustainable rate and ceiling | ops/s; ops/block; neighbours; vehicles per channel | **PF-49** ops/s = G/(g_F·Δ) (G, Δ as PAR, PN-14); **PF-43** P\*(f_id); **PF-44** N_fit; PF-50 bounds a privacy-excluded design only (PN-15) | — |
| MD-12 | Latency (per op) | wall time of the operation itself | ms (median, p95) | register rows; **PF-39** says what an M1 latency is (client + RPC + execution) | — |
| MD-13 | Latency-tier fit | fit to Tier 1 (< 100 ms) / 2 / 3 | tier; slack; ρ_v | **PF-43** ρ_v = P·r_BSM·t_ver ≤ f_id (corrected condition k_f ≥ r_BSM·P·t_chain/f_id, PN-11); R4 PF-31 | — |
| MD-14 | Revocation latency W | revocation decision → every verifier refusing | s; messages (k_f − 1) | **PF-48** (renewal, tail quantiles), **PF-54**, **PF-55**; R4 PF-27/28 | in messages only, because no TTL exists (CA-07) |
| MD-15 | Freshness / staleness | message freshness (window) **and** state staleness (cache), kept separate | s; messages | message: **PF-47**, **PF-53**; state: **PF-54** ≤ k_f − 1 msgs, **PF-55** k_f\* = ⌊r_s σ_max⌋ + 1; **PF-56** term table | — |
| MD-16 | Auditability | an after-the-fact party can prove what happened and who did it | y/n; detection latency | R4 PF-13 | — |
| MD-17 | Evidence status | St + condition class | label | shared brief §2; register tags | — |
| MD-18 | Regulatory posture | GDPR/EDPB fit | posture class | qual. (by decision; KD-R8-05) | — |
| MD-19 | Interoperability | conformance to W3C, MOBI, IEEE, SAE | passed / total | register #4, #24, #53 | — |
| MD-20 | Recoverability | control survives key loss without enabling theft | P; (t, m_r) | R4 PF-30; governance req **PF-66** | — |
| MD-21 | Ordering-race window | interval in which a dependent action sees stale or reordered state | s; blocks | R4 PF-25/26; **PF-40** | single node: no race observable |
| MD-22 | Operational burden | steps and P(error) | steps | register #62 | — |

---

## 2. Parameter registry PAR-01..PAR-43 (R8 is sole owner; declared only)

R8 owns PAR- (R9 §3.1). R7's 26 parameters are absorbed by the mapping table, and the 13 that R8 lacked are appended as PAR-31..43. **No value is chosen here.** "Candidates" lists options only. R7 states the repository's current condition with its status.

**2.1 Mapping table R7 PAR → R8 PAR** (R9 Table B; R7 v0-2 must cite the right-hand numbers).
| R7 | → R8 | R7 | → R8 | R7 | → R8 | R7 | → R8 |
|---|---|---|---|---|---|---|---|
| 01 N_v | 04 | 08 RNG | **34** | 15 gossip | **37** | 22 K | 22 |
| 02 Δ | 05 | 09 V2X curve | 10 | 16 freshness window | **38** | 23 fleet V | **42** |
| 03 G | 06 | 10 radio | 16 | 17 backhaul | **39** | 24 settlement | 18 |
| 04 t_rc | **31** | 11 MCS | **35** | 18 k_f, TTL | 19 + 20 | 25 W budgets | **43** |
| 05 proposer | **32** | 12 encoding L_sec | **36** | 19 replay cache | **40** | 26 density P | 25 |
| 06 client shares | 02 | 13 f_id | 24 | 20 revocation | 12 | | |
| 07 t_sig, t_ver | **33** | 14 RTT class | 26 | 21 proof system | 11 + **41** | | |

**2.2 Registry.**
| PAR | Name (symbol) | Moves MD | Feeds PF | Candidates (not chosen) | Origin |
|---|---|---|---|---|---|
| PAR-01 | DLT family | 01,02,03,07,10,11 | 57, 58 | EVM consortium; public L2; public L1; Indy | R8 |
| PAR-02 | Client implementation(s) and shares (s_c) | 01,02,04,10,12 | 60 | Hardhat; Besu; Geth; Anvil; Indy-node; shares | R8 + R7-06 |
| PAR-03 | Consensus protocol | 01,02,10 | 37, 39, 57 | automine; QBFT; IBFT2; Clique; Gasper | R8 |
| PAR-04 | Validator count N_v and f_B | 02,10,05 | 16, 36, 37, 38, 40, 57, 60 | 4, 7, 10, 16 | R8 = R7-01 |
| PAR-05 | Block interval Δ | 01,11,14 | 24, 25, 28, 40, 49, 57 | none (automine); 1–15 s | R8 = R7-02 |
| PAR-06 | Block gas limit G | 11 | 24, 49, 50 | 30 M; 60 M (instrument); 100 M | R8 = R7-03 |
| PAR-07 | Gas pricing model | 07,14 | 23 | free-gas; EIP-1559; fixed | R8 |
| PAR-08 | DID method | 06,09,19 | 62 | did:ethr; did:mobi; did:indy; did:web; did:key | R8 |
| PAR-09 | Credential format | 09,19,07 | 62 | VC-JWT; JSON-LD DI; AnonCreds; SD-JWT; mDL | R8 |
| PAR-10 | Signature scheme / curve (incl. V2X) | 06,12 | 32, 43 | secp256k1; P-256; Ed25519; BBS+; CL | R8 = R7-09 |
| PAR-11 | Proof system | 06,07,12 | 35, 51 | Groth16 BN254; PLONK; sigma; Bulletproofs | R8 + R7-21 |
| PAR-12 | Revocation profile | 09,14 | 29, 62 | SL status list; AC accumulator | R8 = R7-20 |
| PAR-13 | Anchoring interval τ_a | 16,07 | 13 | per block; minutes; hours | R8 |
| PAR-14 | Public anchor target | 02,07,16 | 13, 19 | Sepolia; L2; L1 | R8 |
| PAR-15 | Key-storage class | 06,20 | 12, 41 | software; SE; TPM; TEE; HSM | R8 |
| PAR-16 | Radio technology | 12,13,10,11 | 44 | 802.11p; LTE-V2X PC5; NR-V2X; Uu | R8 = R7-10 |
| PAR-17 | Deployment placement | 07,08,09,18 | 52, 62 | on-chain; off-chain; anchored; hybrid (P1–P4) | R8 |
| PAR-18 | Network scope / settlement option | 01,02,10 | 26, 28, 57 | local; consortium; L2; L1 / A, B, C | R8 + R7-24 |
| PAR-19 | Re-check period k_f | 14,15,12 | 54, 55 | {1, 5, 25, ∞}; time-based | R8 + R7-18 |
| PAR-20 | State-cache TTL T_ttl | 15,14 | 54, 55 | s – h; none | R8 + R7-18 |
| PAR-21 | Delegate validity | 14,09 | 28 | per epoch | R8 |
| PAR-22 | Pseudonym budget K / pool | 09,07 | R4 04, 50, 62 | per epoch; per year | R8 = R7-22 |
| PAR-23 | Recovery threshold (t, m_r) | 20 | R4 30 | 1-of-1; t-of-m; time-lock | R8 |
| PAR-24 | Identity budget fraction f_id | 13 | 43, 54, 55 | 0.25; 0.5; 1.0 | R8 = R7-13 |
| PAR-25 | Neighbour density P | 11,12,13 | 43, 44, 53 | scenario values | R8 = R7-26 |
| PAR-26 | RPC transport and RTT class | 12 | R4 31, 43, 57 | in-process; HTTP; WS; WAN | R8 + R7-14 |
| PAR-27 | Replica count r | 10 | R4 05 | 1–5 | R8 |
| PAR-28 | Permissioning mode | 02,18 | 60 | open; node-; account-permissioned | R8 |
| PAR-29 | Hash function | 06,07 | 33 | keccak-256; SHA-256; Poseidon | R8 |
| PAR-30 | Salt / commitment form | 09,18 | 34, 62 | unsalted; salted hash; Pedersen | R8 |
| PAR-31 | QBFT round-change timeout t_rc | 01,10 | R4 17, 40, 57 | vendor default; tuned | R7-04 |
| PAR-32 | Proposer selection policy | 01,21 | 40 | round-robin; weighted | R7-05 |
| PAR-33 | Sign/verify hardware class (t_sig, t_ver) | 12,13,11 | 43, 57 | server sw; A53-class; MCU HSM; ASIC | R7-07 |
| PAR-34 | RNG min-entropy and seeding policy (H_∞, κ) | 06 | 41, 42 | OS CSPRNG; SE TRNG; health-tested | R7-08 |
| PAR-35 | MCS / data rate | 11,13 | 44 | 6 / 12 Mb/s; PC5 MCS | R7-11 |
| PAR-36 | Message encoding and 1609.2 profile (L_sec) | 11,13 | 44 | JSON; UPER + digest; UPER + cert | R7-12 |
| PAR-37 | Gossip fan-out / topology (F_g, D_g) | 01,10 | R4 17, 28; gossip PF to be assigned (R9 PN-10) | — | R7-15 |
| PAR-38 | Freshness window (T_max,age, T_max,fut) | 15,05 | 47, 53 | 1.0/0.1 s; tighter | R7-16 |
| PAR-39 | RSU backhaul availability (A_L, μ_off, CV) | 10,14 | 48, 57a | scenario | R7-17 |
| PAR-40 | Replay-cache size C_rc | 05,15 | 53 | sized to P | R7-19 |
| PAR-41 | ZK setup ceremony (t_s parties) | 06 | 35, R4 11 | single-party (prototype); MPC | R7-21 |
| PAR-42 | Fleet size V | 11,07 | R4 04, 50 | scenario | R7-23 |
| PAR-43 | Manoeuvre-class W budgets W_B | 14,13 | R4 02′, 15; 48, 54 | per manoeuvre class (Q-R5) | R7-25 |

---

## 3. The register

Categories run top-down. First comes what the user does (TX, IDTX, VC, SIG, READ). Then what makes it work (PRIM, ALG, PROT, SC, SCF). Then where it runs (NET, DLT, IMPL, HW, SVC). Then why it exists and who governs it (SCN, GOV). Then how we know (MET, THR). Each section opens with where the category sits, and each ends with a **Deepen next** line naming the best chat and the first question to take there.

### 3.1 RV-TX — Transactions

A transaction is the unit by which anything above L5 changes ledger state. It sits at **L5.3** and descends through L5.1 (execution), L4.1 (fee), L3 (ordering) and L0.3/L0.4 (propagation). What every row borrows from below is *ordering*. On this tree ordering is trivial: one automining process (PF-39).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-TX-01 | Write tx (EOA) | signed state change | L5.3 | PRO-21; ALG-02, ALG-07; T-05, T-06 | BP-L5-02, L5-03, L4-03 | 07,12 / 01 | PF-52, PF-57, PF-39 | 05,07 | M (#22, #29) |
| RV-TX-02 | Legacy / EIP-155 tx | chain-id domain separation of the outer tx | L5.3 | PRO-21; T-05 | BP-L5-02 | 05 | — (standard) | 01 | S |
| RV-TX-03 | EIP-2930 access-list tx | pre-declared storage | L5.3 | PRO-21a; ALG-21 | BP-L4-03 | 07 | PF-52 (partial, EIP-2929) | 07 | — |
| RV-TX-04 | Read call (`eth_call`) | non-state-changing execution | L5.1, L0.4 | PRO-13 | BP-L2-05, L7-03, BP-L0.4-02 | 12,15 | PF-54 | 26 | M (#21, #37) |
| RV-TX-05 | Batch tx | many ops in one tx | L5.3 | IMP-L4.3-01 | BP-L4-05 | 07 / 11 | PF-49 | 06 | M (#34) |
| RV-TX-06 | Meta-tx (in-contract signed, relayed) | third party submits | L5.3, L5.2 | PRO-22a; SCF-EDR-10 | BP-L5-02, BP-L5.2-01 | 07 / 21 | open (#50 measures; qual.) | 07 | M (#50) |
| RV-TX-07 | ERC-4337 UserOp | account-abstraction op | L5.3 | PRO-22; SCF-E4337EP-01 | BP-L5-04 | 07 / 20 | — | 07 | M (#25, #50) |
| RV-TX-08 | EIP-7702 set-code tx | EOA delegates to code (O8) | L5.3 | PRO-21d | BP-L5-04, L6-06 | 04,20 | qual. (absent) | 02 | — |
| RV-TX-09 | Anchor / checkpoint tx | private-state commitment to a public chain | L5.3, L2.1 | SOL-03; T-09; T-I15 | BP-L4-03, L0-04 | 16,07,09 | R4 PF-13, PF-04′ | 13,14 | Ds |
| RV-TX-10 | Contract deploy | code deposit | L5.3 | IMP-L5.1-01; IMP-L4.3-02 | BP-L5-04 | 07 | — | 06 | M (#22, #58) |
| RV-TX-11 | Forced inclusion | L1 bypass of a censoring sequencer | L5.3 | SOL-04 | BP-L3-06 | 01 | R4 PF-20 | 18 | Ds |
| RV-TX-12 | Replacement / cancel | same nonce, higher fee | L4.1 | ALG-22 | BP-L5-05 | 01,21 | R4 PF-23 | 07 | — |
| RV-TX-13 | Private (Paladin-style) tx | group-restricted content | L5.3 | O15; SOL-05 | BP-L0-04 | 09,18 | qual. | 17,28 | Ds |
| RV-TX-14 | Receipt / event emission | log as evidence | L5.1, L2.1 | IMP-L2.1-02; T-08 | BP-L2-01 | 08 / 16 | PF-52 | 17 | M (#49) |
| RV-TX-15 | Mempool propagation | gossip to proposers | L0.3 | PRO-11; T-02 | BP-L0-01, L0-04 | 09,01 | R4 PF-01′ | 37 | — |

**Deepen next.** Cost thread. *First question:* "Which GAS_CHARTER class and which single run of record does each RV-TX gas cell cite (PN-21)?"

### 3.2 RV-IDTX — Identity transactions and IDTX functions

These are the programme's identity operations: the IMinimalSSI functions (Set A/B, Set C pending) and the I-24 identity-dependent transactions. They sit at **L6.3**, are realised in L5.2 contracts, cash out as RV-TX rows, and are what RV-VC and RV-SCN call. Function names follow the catalogue; F-numbers stay [B1] (R9 B-01), except F8 = createPresentation.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-IDTX-01 | createDID | identifier + controller (C1/C2) | L6.3 | SCF-CVDR-02; SCF-EDR-01 (implicit, 0 gas); SCF-VPR-08 (explicit); T-I17 | BP-L1-01, L6-01, BP-L6.1-01 | 07 / 06,19 | PF-52; R4 PF-02..04 | 08,17 | M (#1, #29, #34) |
| RV-IDTX-02 | resolveDID | build the DID document | L6.1 | RV-READ-01; ALG-23; T-I17 | BP-L2-05, L7-03, BP-L0.4-02 | 12,15 / 13 | PF-54; R4 PF-31 | 08,26 | M (#31, #51) |
| RV-IDTX-03 | updateDID / rotate controller (U1/U4) | changeOwner | L6.3 | SCF-EDR-03; I3; T-09 | BP-L6-02, L5-01 | 07 / 21 | R4 PF-25/26; PF-40 | 05,18 | M (#2, #29) |
| RV-IDTX-04 | deactivateDID (D3) | identity terminated | L6.3 | SCF-VPR-07 (now emits `previousChange`, D21 fixed) | BP-L6-10 | 07 / 16,18 | — | 17 | M (#35 event 17) |
| RV-IDTX-05 | addVerificationMethod (U3) | attribute/key added | L6.3 | SCF-EDR-09 | BP-L6-09, BP-L2.1-01 | 07,08 | PF-52 | 17 | M (#2, #49) |
| RV-IDTX-06 | removeVerificationMethod (D2) | attribute revoked | L6.3 | SCF-EDR-11 | BP-L6-04 | 07 / 14 | PF-54 | 17 | M (#29) |
| RV-IDTX-07 | addDelegate (U2) | scoped delegate with validity | L6.3 | SCF-EDR-05; I4 | BP-L6-06, BP-L7.2-01 | 07 / 09 | PF-62 | 21,22 | M (#2) |
| RV-IDTX-08 | validDelegate (R4) | delegate check in chain time | L6.3 | SCF-EDR-02; IMP-L5.1-03; I2 | BP-L6-06, L7-03, BP-L7.2-02 | 12 / 15 | PF-54 | 19 | M (#51) |
| RV-IDTX-09 | revokeDelegate (D1) | delegate retired | L6.3 | SCF-EDR-07 | BP-L6-04 | 07 / 14 | PF-54 | 21 | M (#29) |
| RV-IDTX-10 | issueCredential (V1, V3) | issuer key + status anchor | L6.3 | RV-VC-01; I5 | BP-L6-03 | 07 / 06 | PF-32 | 09,12 | M (#29, #34) |
| RV-IDTX-11 | verifyCredential (V6) | status + off-chain proof | L6.3 | RV-VC-08; I7 | BP-L6-04, L7-03 | 12 / 13,14 | PF-43, PF-54 | 12,19 | M (#21, #27) |
| RV-IDTX-12 | revokeCredential (V5) | status flip | L6.3 | RV-VC-10; I8; SOL-09 | BP-L6-04 | 07 / 14 | PF-48, PF-54 | 12,13 | M (#22, #29) |
| RV-IDTX-13 | createPresentation (F8, P1) | holder-built presentation | L6.3 | IMP-L6.2-02; I6; T-I11, T-I13 | BP-L6-08, L6-05 | 07 / 09 | PF-62 (partial) | 09 | M (#54) |
| RV-IDTX-14 | execute (X1) | identity acts as account | L6.3, L5.2 | **SCF-E725XY-04, SCF-E4337A-02** (not SCF-E725B-03, a stub; PN-23b) | BP-L5-04, L6-06, BP-L5.2-05 | 07 / 04 | — | 07 | M (#54; 725xy and 4337 only) |
| RV-IDTX-15 | Relayed op (U5) | signed op via relayer | L6.3 | RV-TX-06; SCF-EDR-10 | BP-L5-02, BP-L5.2-01 | 07 | — | 07 | M (#50) |
| RV-IDTX-16 | Set C agent extension | delegated agent authority | L6.3 | SOL-06 Set C; T-I22 | BP-L6-06 | 04,09 | qual. | 21 | Ds (scope pending) |
| RV-IDTX-20 | IDTx (P2-D8) | tx conditioned on a named identity's state | L6.3, L5.2 | I-24 §1; SOL-10 | BP-L5-05, L6-02 | 21,07,15 | R4 PF-25 | 05,17 | Ds (I-24 §2.2) |
| RV-IDTX-21 | `IdtxExecutor.execute` | act if dependency holds now | L5.2 | SCF-IDTX-02; SCF-IDTX-01; SOL-10 | BP-L5-05, L6-02 | 07,21 | open (Q-R7-03; E-F1-1) | 05 | I (12 tests, 5 mutants) |
| RV-IDTX-22 | `createIntent` → `fulfil` | deferred action, keeper fulfils by deadline | L5.2 | SCF-IDTX-03, -04 | BP-L5-05, L3-06 | 21,01 | R4 PF-25 | 05 | I |
| RV-IDTX-23 | `holds(Dependency)` Owner/Delegate/Commitment | caller-independent predicate | L5.2 | SCF-IDTX-01; SCF-EDR-01/02; SCF-IDC-03 | BP-L7-03 | 15,21 | PF-54 | 17 | I |
| RV-IDTX-24 | `setCommitment` / `revokeCommitment` | commitment with expiry | L5.2 | SCF-IDC-01, -02; T-I15 | BP-L6-04, BP-L2.1-01 | 14,18 | PF-34 | 30 | I |
| RV-IDTX-25 | `payToll` as IDTx | toll gated on identity | L5.2 | SCF-E721T-03 | BP-L5-05, BP-L5.2-06 | 07 | — | 07 | I |
| RV-IDTX-26 | MOBI birth (T5) as IDTx | birth gated on manufacturer authority | L5.2 | SCF-MOBI1-04; SOL-13 | BP-L6-03 | 07 | — | 17 | M (#33) |
| RV-IDTX-27 | `addClaim` (T10/T11) as IDTx | claim gated on issuer authorisation | L5.2 | SCF-E735-01 | BP-L6-03, L6-09, BP-L1.1-01 | 07,08 | — | 17 | M (#34, #49) |
| RV-IDTX-28 | ZK admission `ZkVinGate.admit` | access gated on VIN predicate proof | L5.2 | SCF-ZKG-03; SCF-G16-01; SOL-11; T-I14 | BP-L1-06, BP-L1.2-04 | 07 / 09,06 | PF-35, PF-51 | 11,41 | M (#58) |

**Deepen next.** IDTX work chats. *First question:* "Run E-F1-1 so that RV-IDTX-21..24 move from I to M with gas, and decide B-04 and B-15 for Set A admission."

### 3.3 RV-VC — Credentials

Credentials are the attribute layer: issuer-signed statements, held and presented by a wallet. They sit at **L6.2** over L1.1 signatures, with status in L2.3/L5.2.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-VC-01 | Issue | issuer signs claim set | L6.2 | IMP-L6.2-01; PRO-22b; T-I17 | BP-L6-03, BP-L6.2-01 | 12 / 06,19 | PF-32 | 09,10 | M (#21) |
| RV-VC-02 | Endorsement / attestation | co-signed event | L6.2, L5.2 | SCF-MOBI2-04; IMP-L6.3-04 | BP-L6-03, L6-07 | 07 / 16 | — | 17 | M (#28) |
| RV-VC-03 | Licence class endorsement 7 → 5 | new VC, old suspended | L6.2, L7.3 | RV-VC-01 + RV-VC-11; I5, I8 | BP-L6-03, L6-04 | 14,16,18 | PF-48 | 09,12 | Ds (Q-R8-01) |
| RV-VC-04 | Present | holder discloses | L6.2 | IMP-L6.2-02; RV-IDTX-13 | BP-L7-04 | 07 / 09,12 | — | 09 | M (#54 P1) |
| RV-VC-05 | Selective disclosure | reveal subset | L6.2 | IMP-L6.2-02; ALG-16; T-I11, T-I13 | BP-L6-05, L6-08 | 09,06 | R4 PF-10 | 09,10 | Ds (native only in O12) |
| RV-VC-06 | Predicate proof | "year ≥ x" without the value | L6.2 | ALG-12; IMP-L6.2-06 | BP-L1-06, L6-05, BP-L1.2-03 | 12,07 / 09 | PF-35 | 11 | M (#56, #57) |
| RV-VC-07 | Predicate-narrowing defence | bound leakage across queries | L6.2, L7.1 | IMP-L7.1-05; SOL-14 | BP-L6-05 | 09,22 | PF-62 (hiding bits, partial) | 22 | M (#61, Sim) |
| RV-VC-08 | Verify | signature + issuer key + status | L6.2 | IMP-L6.2-01; ALG-03; I7 | BP-L6-04, L7-03 | 12 / 13 | PF-43 | 10,19 | M (#21, #27) |
| RV-VC-09 | Status check | list / registry lookup | L6.2, L2.3 | IMP-L2.3-01; RV-READ-05 | BP-L7-03, L6-05 | 14,15 / 09 | PF-54; R4 PF-29 | 12,19 | M (#32, #37) |
| RV-VC-10 | Revoke | permanent invalidation | L6.2 | RV-IDTX-12; SOL-09 | BP-L6-04 | 14 | PF-48, PF-54 | 12,13 | M (#46) |
| RV-VC-11 | Suspend | reversible invalidation | L6.2 | IMP-L2.3-02 (status purpose) | BP-L6-04 | 14 | PF-54 | 12 | — |
| RV-VC-12 | Expire | validity lapse | L6.2 | IMP-L5.1-03 / receiver clock (HW-10) | BP-L7-04, BP-LH-04 | 15 | PF-47 | 38 | — |
| RV-VC-13 | Re-issue | replacement after rotation | L6.2 | RV-VC-01 | BP-L6-03 | 14,07 | R4 PF-27 | 09 | — |
| RV-VC-14 | Schema / cred-def publication | shared claim shape | L6.2 | IMP-L6.2-07; T-I20 | BP-L6-09 | 19,04 | — | 09 | Ds |
| RV-VC-15 | Birth certificate (MOBI VID I) | first vehicle credential | L6.2 | IMP-L6.2-05; SCF-MOBI1-04 | BP-L6-03 | 07 / 19 | — | 08 | M (#33) |
| RV-VC-16 | Lifecycle event credential (VID II) | maintenance / odometer / crash | L6.2 | IMP-L6.2-05; SCF-MOBI2-03 | BP-L6-07, BP-L2.3-01 | 07 / 16 | — | 17 | M (#30, #35) |
| RV-VC-17 | ERC-735 claim | on-chain signed claim | L6.2, L5.2 | SCF-E735-01 | BP-L6-09, BP-L1.1-01 | 07,08 | PF-52 | 17 | M (#34, #49) |
| RV-VC-18 | ERC-1155 soulbound credential | token as credential | L6.2, L5.2 | SCF-E1155-02 | BP-L6-08 | 07 | — | 17 | M (#34) |
| RV-VC-19 | RSU credential | infrastructure authority VC | L6.2 | IMP-L7.2-03; C3 | BP-L6-03 | 12,14 | PF-48 | 19 | M (#44, #46, #47) |

**Deepen next.** G-RIM, plus a new chat for RV-VC-03. *First question (G-RIM):* "Is the thesis-defined cryptosuite kept, or is a registered one adopted (B-13)?" *New chat:* "Is endorsement a supersession or an attestation (Q-R8-01)?"

### 3.4 RV-SIG — Signatures and key operations

Every authority in the stack is, at the bottom, a signature. These rows sit at **L1.1/L1.2**, with custody in **LH.2**. Upward they underwrite R1 authenticity, R4 non-repudiation and I2 control. The repository uses three signature schemes across nine contracts (R9 SLD-06).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-SIG-01 | Sign (ECDSA secp256k1) | σ over digest | L1.1 | ALG-02; IMP-L1.2-01..04; T-05, T-06 | BP-L1-02, L1-07, BP-LH-01 | 12 / 06 | PF-32 | 10,15,33 | M (#48 sign, M0) |
| RV-SIG-02 | Verify | σ against key | L1.1 | ALG-02/04/05; IMP-L1.2-02 | BP-L1-04, BP-L1.2-01 | 12 / 13 | PF-32, PF-43 | 10,33 | M (#27) |
| RV-SIG-03 | ecrecover | address from σ (0x01) | L5.1 | ALG-03; PRO-16 | BP-L5-03, BP-L1.1-02, BP-L5.2-02 | 07 | PF-32 | 10 | I |
| RV-SIG-04 | Key generation | sample secret scalar | L1.1, LH.1 | ALG-01; IMP-LH.1-01; HW-02 | BP-L1-01, BP-LH-01 | 06 | PF-41, PF-42 | 15,34 | — |
| RV-SIG-05 | Key rotation | replace controller | L6.3 | RV-IDTX-03 | BP-L6-02 | 07 / 21,14 | R4 PF-25 | 05 | M (#2) |
| RV-SIG-06 | Delegation signature | owner-signed delegate/attribute | L5.2 | SCF-EDR-06; PRO-22a | BP-L5-02, BP-L5.2-01 | 07 / 05 | — | 10 | M (#50) |
| RV-SIG-07 | Guardian recovery | regain control via guardian | L6.3 | SCF-E4337A-04, -05; I9 | BP-L6-10, BP-L5.2-04 | 20 | R4 PF-30 | 23 | I |
| RV-SIG-08 | BBS+ / CL proof | multi-message ZK disclosure | L1.1 | ALG-16; T-I11, T-I13 | BP-L1-05 | 06,09 | R4 PF-10 | 10 | Ds |
| RV-SIG-09 | Schnorr PoK | prove key possession | L1.1 | ALG-14, ALG-15; SCF-SCH-01/02 | BP-L1-02 | 07 / 06 | PF-32 | 10 | M (#58, #59) |
| RV-SIG-10 | IEEE 1609.2 signed message | V2X SPDU | L7.2 | PRO-12; ALG-05; T-I05 | BP-L7-05 | 05,13 | PF-43, PF-44 | 10,16,36 | Ds (repo uses JSON; KD-R6-03) |
| RV-SIG-11 | Certificate (X.509 P-256, 1609.2-style) | CA binding of key | L6 | ALG-05; T-I02; `pki_identity.py` | BP-L6-03 | 12 / 06 | PF-32 | 10 | M (#21 PKI) |
| RV-SIG-12 | Butterfly / pseudonym keys (1609.2 SCMS) | unlinkable short-term keys | L6.1 | PRO-12; T-I05 | BP-L6-05 | 09,07 | PF-62; R4 PF-04′ | 22 | Ds (not in repo; PN-23c) |
| RV-SIG-13 | Post-quantum signature | migration target | L1.1 | — | BP-L1-04 | 06 | R4 PF-09 | 10 | — |
| RV-SIG-14 | SPaT message signature | RSU signs signal phase | L7.2 | IMP-L7.2-02; C3 | BP-L7-05 | 12 | — | 10 | M (#44) |

**Deepen next.** Security campaign G-C1. *First question:* "Which single signature scheme (EIP-191 or EIP-712, with chain id) replaces the three in use, and is D52 fixed or documented (B-02, B-03)?"

### 3.5 RV-READ — Reads and resolution

Reads are where the latency budget is spent. They sit at **L6.1 / L0.4 / L2.1–L2.3**. The HAA-1 read rule (SOL-05) keeps Tier 1/2 reads off the ledger. **Message freshness (`freshness.py`) and state staleness (the provider's k-refresh cache) are kept apart** (PN-24).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-READ-01 | DID resolution (event replay) | rebuild doc from ERC-1056 logs | L6.1 | ALG-23; PRO-13; IMP-L2.1-02/04; `erc1056_provider.py` | BP-L7-03, L2-05, BP-L0.4-02 | 12,11 | PF-52 (read side) | 26,08 | M (#31) |
| RV-READ-02 | Offline DID synthesis | doc from identifier only | L6.1 | ALG-23a | BP-L6-01 | 12 / 19 | — | 08 | M (M0 rows) |
| RV-READ-03 | Cached state read | state-cache hit, ≤ k_f − 1 messages stale | L7.1 | **`erc1056_provider.py` `set_refresh_every`** (state cache); SOL-16 (mechanism, PN-09) | BP-L7-03, BP-L7.2-03 | 12,15 / 14 | PF-54, PF-55 | 19,20 | M (#32 k=∞) |
| RV-READ-04 | Probe refresh | one `getIdentityInfo`, resolve if changed | L6.1 | `_probe_identity_info`; SCF-VPR-01 | BP-L7-03, BP-L7.2-02 | 12,15 | PF-54 | 19 | M (#37, #52, #55) |
| RV-READ-05 | Status-list fetch | whole-list download | L2.3 | IMP-L2.3-02; SOL-09 | BP-L0-05, L6-05 | 09,12 | R4 PF-29; PF-62 | 12 | Ds |
| RV-READ-06 | Accumulator witness | non-membership update | L2.3 | IMP-L2.3-03; T-I12 | BP-L2-03 | 07,12 | R4 PF-14 | 12 | Ds |
| RV-READ-07 | RPC read (`eth_call`) | contract view | L0.4 | PRO-13; IMP-L0.4-01/02 | BP-L0-01, BP-L0.4-02 | 12 | PF-39 | 26 | M (#21) |
| RV-READ-08 | Log query (`eth_getLogs`) | filter logs | L0.4, L2.2 | PRO-13; IMP-L2.1-02 | BP-L2-05, BP-L2.2-01 | 12,11 | PF-52 (read side, partial) | 02,26 | M (#31, #51) |
| RV-READ-09 | History query | events history | L2.2 | SCF-MOBI2-05 | BP-L0-05 | 10,16 | R4 PF-05 | 27 | I |
| RV-READ-10 | VIN lookup | VIN hash → DID | L6.1 | SCF-MOBI1-09; ALG-24 | BP-L6-05, BP-L6.1-01 | 12 / 09 | PF-33, PF-62 | 30 | M (#29) |
| RV-READ-11 | Read over HTTP JSON-RPC | transport condition | L0.4 | PRO-13; PRO-09 | BP-L0-02 | 12 | PF-39 | 26 | M (#39) |
| RV-READ-12 | Read against public RPC (M2) | provider-mediated read | L0.4 | PRO-15 | BP-L0-01, L0-04, BP-L0.4-02 | 12,09 | — | 18,26 | — (not measured; NC-07) |
| RV-READ-13 | Proof-backed read | Merkle proof of state | L2.1 | ALG-18; T-08 | BP-L2-01, BP-L0.4-02 | 05,12 | req PF-64 | 02 | — |
| RV-READ-14 | State-cache TTL | max cached age in time | L7.1 | `erc1056_provider.py` (absent); CA-07 | BP-L7.2-03 | 14,15 | PF-54, PF-55 | 20 | — (no TTL; CA-07) |

**Deepen next.** Latency thread. *First question:* "Add T_ttl (CA-07) and report W in seconds as well as messages: what is the measured staleness at k_f\* = ⌊r_s σ_max⌋ + 1?"

### 3.6 RV-PRIM — Cryptographic primitives

These rows are the floor of L1. Each is a T- or T-I- root, and upward it is borrowed as "unforgeability" or "hiding". The rows are mostly STANDARD, and measurement happens per implementation.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-PRIM-01 | keccak-256 | EVM hash | L1.1 | ALG-07; T-07 | BP-L1-03 | 06 | PF-33 | 29 | S |
| RV-PRIM-02 | SHA-256 | BSM digest, replay key, VIN hash | L1.1 | ALG-08; T-07 | BP-L1-03, BP-L6.1-01 | 09 / 06 | PF-33 | 29 | M (#60 unsalted VIN reversed) |
| RV-PRIM-03 | Poseidon | circuit hash | L1.1 | ALG-09; T-I14 | BP-L1-03 | 06 | S (ROM-class; no PF by decision) | 29 | I |
| RV-PRIM-04 | Hash commitment | salted binding | L1.1 | IMP-L6.2-06; SCF-IDC-01; T-I15 | BP-L6-05 | 09,18 | PF-34 | 30 | I |
| RV-PRIM-05 | Pedersen commitment | perfectly hiding | L1.1 | ALG-14; T-I15 | BP-L1-04 | 09,06 | PF-34 | 30 | M (#59) |
| RV-PRIM-06 | ECDSA secp256k1 | signature scheme | L1.1 | ALG-02; T-06 | BP-L1-02 | 06 | PF-32 | 10 | S |
| RV-PRIM-07 | Ed25519 | did:key, DIDComm | L1.1 | ALG-06; T-06 | BP-L1-07 | 06 | PF-32 (analogue) | 10 | S |
| RV-PRIM-08 | BN254 pairing | Groth16 precompiles | L1.1 | ALG-10; PRO-18 | BP-L1-05, BP-L1.2-02 | 06 | R4 PF-10 | 11 | S |
| RV-PRIM-09 | BLS12-381 pairing | BBS+ | L1.1 | ALG-11 | BP-L1-05 | 06 | R4 PF-10 | 10 | S |
| RV-PRIM-10 | Groth16 | SNARK | L1.1 | ALG-12; IMP-L1.2-07/08 | BP-L1-06, BP-L1.2-04 | 07,12 / 06 | PF-35, PF-51 | 11,41 | M (#56–#58) |
| RV-PRIM-11 | Sigma protocols | interactive ZK | L1.1 | ALG-14; IMP-L1.2-09 | BP-L1-02 | 12 / 06 | — | 11 | M (#59) |
| RV-PRIM-12 | Accumulator | set membership | L1.1 | IMP-L2.3-03; T-I12 | BP-L2-03 | 07,12 | R4 PF-14 | 12 | Ds |
| RV-PRIM-13 | Merkle tree | inclusion | L1.1 | IMP-L2.3-04; T-08 | BP-L2-01 | 06 | — | 29 | M (#59) |
| RV-PRIM-14 | RNG / entropy | key and nonce source | LH.1 | HW-02; IMP-LH.1-01 | BP-L1-01, L1-02, BP-LH-01 | 06 | PF-41, PF-42 | 34 | — |
| RV-PRIM-15 | AEAD / ECDH | channel confidentiality; VIN ciphertext | L1.1 | ALG-17; T-04; T-I09 | BP-L7-05 | 05,06 | — | 10 | Ds |

**Deepen next.** This Roots thread (R7 v0-2). *First question:* "Fix the salted-commitment rule for every low-entropy attribute (B-05): salt length, custody, and whether the did:mobi identifier is salted."

### 3.7 RV-ALG — Algorithms

Algorithms compose primitives into procedures (R6 defines ALG-, R7 bounds them). They span **L1.2–L6.1** and L0.1.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-ALG-01 | QBFT round | propose / prepare / commit | L3.1 | ALG-20; IMP-L3.2-01; SOL-02 | BP-L3-01..03 | 01,02,10 | PF-37, PF-38, PF-40 | 03,04,05,31,32 | Ds |
| RV-ALG-02 | Hardhat automine | one tx → one block, N_v = 1 | L3.1 | ALG-19; IMP-L3.2-02 | — (no adversary) | 17 | PF-39 | 03 | M (config, `meta.json`) |
| RV-ALG-03 | Fork choice (Gasper) | public L1 head | L3.1 | ALG-20c; T-13 | BP-L3-04, L3-05 | 01,02 | R4 PF-18/19 | 03 | S |
| RV-ALG-04 | DID resolution algorithm | DID Core resolve | L6.1 | ALG-23, ALG-24 | BP-L2-05 | 12,19 | PF-52 (read side) | 08 | M (#24) |
| RV-ALG-05 | Proof generation | witness → proof | L1.2 | ALG-12; IMP-L1.2-08 | BP-L1-06 | 12 | none needed (#57) | 11,15 | M (#57) |
| RV-ALG-06 | Proof verification | on/off-chain verify | L1.2, L5.1 | SCF-G16-01; PRO-18 | BP-L1-06, BP-L1.2-02 | 12,07 | PF-51 | 11 | M (#57, #58) |
| RV-ALG-07 | Merkle proof check | inclusion verify | L2.1 | ALG-18 | BP-L2-01 | 06 | — | 29 | M (#59) |
| RV-ALG-08 | Gas metering | per-opcode accounting | L5.1 | ALG-21 (cost model) | BP-L4-05 | 07 | PF-52, PF-49 | 06,07 | M (#25) |
| RV-ALG-09 | State refresh (k-refresh) | accept from state cache ≤ k_f − 1 | L7.1 | **`erc1056_provider.py`** (PN-24); SOL-16 | BP-L7-03, BP-L7.2-03 | 14,15 | PF-54, PF-55 | 19,20 | M (#32, #46) |
| RV-ALG-10 | Message freshness + replay check | reject stale/duplicate | L7.1 | IMP-L7.2-01; IMP-L2.3-06 (`freshness.py`) | BP-L7-04, BP-L2.3-02, BP-LH-04 | 05 | PF-47, PF-53 | 38,40 | M (#45) |
| RV-ALG-11 | Steward policy / learner | disclosure budget control | L7.1 | IMP-L7.1-05 | BP-L6-05 | 09,22 | PF-62 (partial) | 22 | M (#61, Sim) |
| RV-ALG-12 | Sidelink resource selection (SB-SPS) | radio resource allocation | L0.1 | PRO-04; `cv2x_stack.py` | BP-L0-02, BP-L0.1-01 | 10,11 / 09 | PF-44, PF-44c; PF-46 reserved | 16,25 | I (model only) |
| RV-ALG-13 | Status-list encode/decode | bitstring | L2.3 | IMP-L2.3-02 | BP-L6-05 | 09 | R4 PF-29 | 12 | Ds |
| RV-ALG-14 | Peer discovery | discv4/v5 | L0.3 | PRO-11a/b | BP-L0-01, BP-L0.3-01 | 10 | R4 PF-01′, PF-03′ | 02 | — |

**Deepen next.** This Roots thread (with Scale). *First question:* "Add an SPS reselection counter to `cv2x_stack.py` so that PF-44c (≈ 0.14–0.80) can be measured rather than simulated (Q-R7-04)."

### 3.8 RV-PROT — Protocols

Protocols fix the interaction between parties (R6 PRO-). They sit at **L0.2–L0.4** and **L7.2**.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-PROT-01 | DIDComm v2 | authenticated encrypted messaging | L7.2 | PRO-25 (was PRO-13z); T-I18; O16 | BP-L7-02, L7-05 | 05,09 | PF-59 | 10 | Ds |
| RV-PROT-02 | Issue Credential / Present Proof | Aries exchange | L7.2 | IMP-L7.1-06; T-I21 | BP-L7-04 | 05,19 | — | 09 | Ds |
| RV-PROT-03 | OID4VCI / OID4VP | OpenID exchange | L7.2 | T-I17 | BP-L7-05 | 19 | — | 09 | — |
| RV-PROT-04 | TLS 1.3 on RPC | endpoint authentication | L0.4 | PRO-15; T-I04 | BP-L7-05, BP-L0.4-01 | 05 | — | 26 | — |
| RV-PROT-05 | devp2p / RLPx | node transport | L0.3 | PRO-11 | BP-L0-01 | 10,09 | R4 PF-01′ | 02,37 | — |
| RV-PROT-06 | discv5 | node discovery | L0.3 | PRO-11b | BP-L0-03, BP-L0.3-01 | 10 | R4 PF-03′ | 02 | — |
| RV-PROT-07 | JSON-RPC | client ↔ node | L0.4 | PRO-13 | BP-L0-01, BP-L0.4-01/02/03 | 12 | PF-39 | 26 | M (#21, #39) |
| RV-PROT-08 | IEEE 1609.2 | V2X security services | L7.2 | PRO-12 | BP-L7-05, L6-05 | 05,13 | PF-43, PF-44 | 16,36 | Ds |
| RV-PROT-09 | IEEE 1609.3 WSMP | non-IP V2X transport | L0.2 | PRO-08 | BP-L0-02 | 13 | PF-44 | 16 | — |
| RV-PROT-10 | SAE J2735 BSM (JSON-like) | 10 Hz safety message | L7.2 | PRO-23 (was PRO-13x); PRO-24 (J2945/1); IMP-L7.2-02 | BP-L7-07, BP-L7.2-04 | 13 / 11 | PF-43, PF-44 | 24,25,36 | M (#27) |
| RV-PROT-11 | SAE J2735 SPaT | signal phase and timing | L7.2 | PRO-23; IMP-L7.2-03 | BP-L7-07 | 13 | PF-43 | 24 | M (#44) |
| RV-PROT-12 | DENM / CAM | ETSI messages | L7.2 | PRO-12a; `cv2x_stack.py` | BP-L7-07 | 13 | — | 16 | I |
| RV-PROT-13 | MOBI VID I/II flows | birth, lifecycle, transfer | L7.2, L6.3 | SOL-13; IMP-L6.2-05 | BP-L6-07 | 07 / 19 | — | 08 | M (#30, #33) |
| RV-PROT-14 | Engine API | CL ↔ EL | L0.4 | PRO-14 | BP-L3-03 | 10 | — | 02 | — |
| RV-PROT-15 | Checkpoint protocol | private → public commit | L3, L5.3 | SOL-03 | BP-L4-04 | 16 | R4 PF-13 | 13,14 | Ds |
| RV-PROT-16 | Message encoding size vs airtime | bytes per signed BSM → channel time | L7.2, L0.1 | IMP-L7.2-02; PRO-03, PRO-04 | BP-L7.2-04, BP-L7-07 | 11,13 | PF-44 (from #23 sizes) | 35,36,16,25 | Dv (PF-44 on #23) |

**Deepen next.** Latency thread. *First question:* "Is 1609.2 encoding in scope (Q-R8-04 with Q-R6-04)? If it is, source the BSM part I and MAC overhead sizes so that SLD-04 can be cited."

### 3.9 RV-SC — Smart contracts (families in the repo)

Contracts are **L5.2**: code that turns a transaction into identity semantics. The option column follows R2 §3.3 / R6 §3 (**PN-22 corrected**). Paths are under `1_blockchain-identity/contracts/` unless stated.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-SC-01 | `ERC1056/EthereumDIDRegistry.sol` | bare ERC-1056 | L5.2 | **O1**; SCF-EDR | BP-L5-04, BP-L5.2-01/02 | 07,08 / 04 | PF-52, PF-61 | 06 | M (#2, #34, #35) |
| RV-SC-02 | `ERC1056/CVINVehicleDIDRegistry.sol` | vehicle wrapper | L5.2 | **O1** wrapper; SCF-CVDR | BP-L5-04, BP-L6.1-01 | 07 | — | 17 | M (#1, #34) |
| RV-SC-03 | `MOBI/ERC1056Registry.sol` | vehicle profile with `revokeIdentity` | L5.2 | **O1** variant; SCF-VPR | BP-L5-04 | 07,12 | — | 17 | M (#22) |
| RV-SC-04 | `ERC721/CVINVehicleNFT.sol` | vehicle NFT, roles, service records | L5.2 | **O3**; SCF-E721N | BP-L5-04 | 07 | — | 17 | M (#3, #34) |
| RV-SC-05 | `ERC721/CVIN_NFT_DID_ERC721*.sol` | NFT-DID incl. `payToll` | L5.2 | **O3** (auxiliary); SCF-E721T/M | BP-L5-04, BP-L5.2-06 | 07 | — | 17 | I |
| RV-SC-06 | `ERC725/CVIN_DID_ERC725.sol` | key-manager identity (`execute` is a stub) | L5.2 | **O5**; SCF-E725B | BP-L5-04 | 07 | — | 17 | M (#29, #34) |
| RV-SC-07 | `ERC725xy/CVINVehicleERC725XY.sol` | ERC-725X/Y data + execute | L5.2 | **O6**; SCF-E725XY | BP-L5-04, BP-L5.2-05 | 07 | — | 17 | M (#34, #54) |
| RV-SC-08 | `ERC735/CVINVehicleClaimHolder.sol` | on-chain claims | L5.2 | **O6**; SCF-E735 | BP-L6-09, BP-L1.1-01 | 07,08 | PF-52 | 17 | M (#34, #49) |
| RV-SC-09 | `ERC1155/CVINVehicleCredential1155.sol` | soulbound credentials | L5.2 | **O2**; SCF-E1155 | BP-L6-08, BP-L6.1-01 | 07 | — | 17 | M (#34) |
| RV-SC-10 | `ERC4337/CVINVehicleAccount.sol` + `CVINMinimalEntryPoint.sol` | smart account, guardian | L5.2 | **O7**; SCF-E4337A/EP | BP-L5-04, L6-10, BP-L5.2-04 | 07 / 20 | R4 PF-30 | 23 | M (#25, #50) |
| RV-SC-11 | `LSP8/CVINVehicleLSP8.sol` | LUKSO identifiable token | L5.2 | none (repo-only; Q-R6-02); SCF-LSP8 | BP-L5-04, BP-L6.1-01 | 07 | — | 17 | M (#34) |
| RV-SC-12 | `MOBI/MOBIVIDRegistry.sol` | VID I birth, ownership | L5.2 | O1 application profile; SOL-13; SCF-MOBI1 | BP-L6-03, BP-L4.2-02 | 07 / 19 | — | 17 | M (#30, #33) |
| RV-SC-13 | `MOBI/MOBIVIDRegistryV2.sol` | VID II lifecycle, attestations | L5.2 | SOL-13; SCF-MOBI2 | BP-L6-07 | 07 / 16 | — | 17 | M (#28, #35) |
| RV-SC-14 | `CVINCombined/CVINCombinedIdentity.sol` | ERC-1056 + ERC-735 | L5.2 | O18 precursor (Family F); SCF-CMB | BP-L5-04, BP-L1.1-01 | 07 | — | 17 | M (#34, #54) |
| RV-SC-15 | `phase2/idtx/contracts/IdtxExecutor.sol` | IDTx executor + commitments | L5.2 | **SOL-10**; SCF-IDTX, SCF-IDC | BP-L5-05, BP-L2.1-01 | 07,21 | open (Q-R7-03) | 05 | I |
| RV-SC-16 | `5_zkp-agent-identity/contracts/Groth16Verifier.sol` | zk verifier | L5.2, L5.1 | SCF-G16-01; PRO-18 | BP-L1-06, BP-L1.2-02/04 | 07 | PF-51 | 11,41 | M (#58) |
| RV-SC-17 | `ZkVinGate.sol` | proof-gated admission | L5.2 | **SOL-11**; SCF-ZKG | BP-L1-06, BP-L1.2-05 | 07 / 09 | PF-35 | 11 | M (#58) |
| RV-SC-18 | `SchnorrEcrecoverVerifier.sol` | Schnorr PoK via ecrecover | L5.2 | SOL-12 (mechanism, PN-09); SCF-SCH | BP-L1-02 | 07 | — | 10 | M (#58) |
| RV-SC-19 | `ERC725xy/CVINExecuteTarget.sol` | test target for execute | L5.2 | SCF-EXT-01 (fixture) | — | 07 | — | — | I |
| RV-SC-20 | cv2x-testbed `contracts/` | registry deployed by testbed | L5.2 | RV-SC-03 | BP-L5-04, BP-LH-02 | 07,12 | — | 17 | M (#22, #47) |

**Deepen next.** Cost thread (with G-C1 for PF-61). *First question:* "Tabulate PF-61(a) access-check coverage and PF-61(b) replay-protection coverage over R6's SCF register (Q-R7-08)."

### 3.10 RV-SCF — Smart-contract functions (state-changing, most important)

These are the verbs of L5.2. Every row now carries R6's SCF tag (R9 Table D′).

| RV | Contract.function | Meaning | SCF tag | BP | MD | PAR | St |
|---|---|---|---|---|---|---|---|
| RV-SCF-01 | EthereumDIDRegistry.changeOwner | rotate controller | SCF-EDR-03 | BP-L6-02 | 07 / 21 | 05 | M (#2) |
| RV-SCF-02 | EthereumDIDRegistry.changeOwnerSigned | relayed rotation | SCF-EDR-04 | BP-L5-02, BP-L5.2-01, BP-L5.2-02 | 07 | 07 | I |
| RV-SCF-03 | EthereumDIDRegistry.addDelegate | delegate with validity | SCF-EDR-05 | BP-L6-06 | 07 | 21 | M (#2, #38) |
| RV-SCF-04 | EthereumDIDRegistry.addDelegateSigned | relayed delegate | SCF-EDR-06 | BP-L5-02, BP-L5.2-01 | 07 | 07 | I |
| RV-SCF-05 | EthereumDIDRegistry.revokeDelegate | delegate retired | SCF-EDR-07 | BP-L6-04 | 07 / 14 | 21 | M (#29) |
| RV-SCF-06 | EthereumDIDRegistry.setAttribute | add attribute (log only) | SCF-EDR-09 | BP-L6-09, BP-L2.1-01 | 07,08 | 17 | M (#2, #49) |
| RV-SCF-07 | EthereumDIDRegistry.setAttributeSigned | relayed attribute | SCF-EDR-10 | BP-L5-02, BP-L5.2-01 | 07 | 07 | M (#50) |
| RV-SCF-08 | EthereumDIDRegistry.revokeAttribute | remove attribute | SCF-EDR-11 | BP-L6-04 | 07 | 17 | M (#29) |
| RV-SCF-09 | CVINVehicleDIDRegistry.createVehicleDID | VIN-bound DID | SCF-CVDR-02 | BP-L6-05, BP-L6.1-01 | 07 / 09 | 30 | M (#1) |
| RV-SCF-10 | CVINVehicleDIDRegistry.transferVehicleOwnership | owner change | SCF-CVDR-04 | BP-L6-02 | 07 | 17 | I |
| RV-SCF-11 | CVINVehicleDIDRegistry.addVerificationDelegate | delegate (wrapper) | SCF-CVDR-07 | BP-L6-06 | 07 | 21 | M (#34) |
| RV-SCF-12 | ERC1056Registry.registerVehicle | explicit create (testbed) | SCF-VPR-08 | BP-L6-01, BP-LH-02 | 07 | 17 | M (#22) |
| RV-SCF-13 | ERC1056Registry.revokeIdentity | identity revoke (`previousChange` emitted; D21 fixed) | SCF-VPR-07 | BP-L6-04 | 07 / 14 | 12 | M (#22) |
| RV-SCF-14 | ERC1056Registry.updateVehicleKey | key update | SCF-VPR-09 | BP-L6-02 | 07 | 05 | I |
| RV-SCF-15 | MOBIVIDRegistry.registerVehicleBirth | VID I birth | SCF-MOBI1-04 | BP-L6-03, BP-L6.1-01 | 07 | 17 | M (#33) |
| RV-SCF-16 | MOBIVIDRegistry.anchorVehicleKey | anchor key to DID | SCF-MOBI1-06 | BP-L6-02 | 07 | 17 | I |
| RV-SCF-17 | MOBIVIDRegistry.transferVehicleOwnership | ownership transfer | SCF-MOBI1-08 | BP-L5-05 | 07 / 16 | 17 | M (#35) |
| RV-SCF-18 | MOBIVIDRegistry.authorizeManufacturer | issuer admission | SCF-MOBI1-01 | BP-L4-06, BP-L4.2-02 | 04,02 | 28 | I |
| RV-SCF-19 | MOBIVIDRegistryV2.recordLifecycleEvent | VID II event | SCF-MOBI2-03 | BP-L6-07 | 07,08 | 17 | M (#35) |
| RV-SCF-20 | MOBIVIDRegistryV2.attestEvent | chain-bound attestation | SCF-MOBI2-04 | BP-L6-03 | 07 | 17 | M (#28) |
| RV-SCF-21 | MOBIVIDRegistryV2.authorizeIssuer / revokeIssuerAuthorization | trust-list edit | SCF-MOBI2-01, -02 | BP-L4-06, BP-L4.2-02 | 04,14 | 28 | I |
| RV-SCF-22 | CVINVehicleClaimHolder.addClaim | ERC-735 claim | SCF-E735-01 | BP-L6-09, BP-L1.1-01 | 07,08 | 17 | M (#34, #49) |
| RV-SCF-23 | CVINVehicleClaimHolder.revokeClaimContent / removeClaim | claim revoke | SCF-E735-03, -02 | BP-L6-04 | 07 | 12 | M (#34) |
| RV-SCF-24 | CVINVehicleCredential1155.issueCredential | mint credential | SCF-E1155-02 | BP-L6-03 | 07 | 17 | M (#34) |
| RV-SCF-25 | CVINVehicleCredential1155.revokeCredential | burn credential | SCF-E1155-03 | BP-L6-04 | 07 | 12 | M (#34) |
| RV-SCF-26 | CVINVehicleCredential1155.issuerTransferIdentity | issuer-mediated transfer | SCF-E1155-04 | BP-L6-06 | 07 | 17 | I |
| RV-SCF-27 | CVINVehicleNFT.mintVehicle | NFT mint | SCF-E721N-01 | BP-L5-04 | 07 | 17 | M (#3) |
| RV-SCF-28 | CVINVehicleNFT.addServiceRecord | maintenance record | SCF-E721N-02 | BP-L6-07 | 07,08 | 17 | I |
| RV-SCF-29 | CVINVehicleNFT.deactivateVehicle | retire vehicle | SCF-E721N-03 | BP-L6-10 | 07 | 17 | I |
| RV-SCF-30 | CVIN_NFT_DID_ERC721.payToll | toll payment | SCF-E721T-03 | BP-L5-05, BP-L5.2-06 | 07 | 07 | I |
| RV-SCF-31 | CVIN_DID_ERC725.addKey / removeKey | key management | SCF-E725B-02 | BP-L6-02 | 07 | 15 | M (#34) |
| RV-SCF-32 | CVIN_DID_ERC725.execute | identity acts (**stub: emits, performs no call**) | SCF-E725B-03 | BP-L5-04 | 07,04 | 07 | — (stub; D23; PN-23a) |
| RV-SCF-33 | CVINVehicleERC725XY.setData | key-value data | SCF-E725XY-02 | BP-L6-09 | 07,08 | 17 | M (#34) |
| RV-SCF-34 | CVINMinimalEntryPoint.handleOp | UserOp dispatch (chain-bound hash) | SCF-E4337EP-01 | BP-L5-04 | 07 | 07 | M (#25) |
| RV-SCF-35 | CVINVehicleAccount.setGuardian / recoverOwner | recovery path | SCF-E4337A-04, -05 | BP-L6-10, BP-L5.2-04 | 20 | 23 | I |
| RV-SCF-36 | CVINVehicleLSP8.mintVehicle / revokeVehicle | LSP8 lifecycle | SCF-LSP8-01, -03 | BP-L5-04, BP-L6.1-01 | 07 | 17 | M (#34) |
| RV-SCF-37 | CVINCombinedIdentity.addClaim / changeOwner | combined ops | SCF-CMB-06, -01 | BP-L5-04, BP-L1.1-02 | 07 | 17 | M (#34) |
| RV-SCF-38 | IdtxExecutor.execute | gated action | SCF-IDTX-02 | BP-L5-05 | 07,21 | 05 | I |
| RV-SCF-39 | IdtxExecutor.createIntent / fulfil | deferred action | SCF-IDTX-03, -04 | BP-L3-06 | 21 | 05 | I |
| RV-SCF-40 | IdentityCommitments.setCommitment / revokeCommitment | commitment with expiry | SCF-IDC-01, -02 | BP-L6-04 | 14,18 | 30 | I |
| RV-SCF-41 | ZkVinGate.admit | proof-gated admission | SCF-ZKG-03 | BP-L1-06, BP-L1.2-05 | 07 | 11 | M (#58) |
| RV-SCF-42 | ZkVinGate.anchorCommitment | VIN commitment anchor | SCF-ZKG-01 | BP-L6-05 | 07 / 18 | 30 | M (#58) |
| RV-SCF-43 | CVINVehicleERC725XY.execute / executeBatch | real X1 executor | SCF-E725XY-04 | BP-L5-04, BP-L5.2-05 | 07 | 07 | M (#54) |
| RV-SCF-44 | CVINVehicleAccount.execute | X1 via smart account | SCF-E4337A-02 | BP-L5-04, BP-L5.2-06 | 07 | 07 | M (#54) |

**Deepen next.** IDTX work chats, plus Cost. G-MV1 handles the MOBI rows. *First question:* "Do the CEI / reentrancy check on SCF-E721T-03, SCF-E721M-01, SCF-E725XY-04 and SCF-E4337A-02 (CA-17), so that BP-L5.2-06 is either analysed or withdrawn."

### 3.11 RV-NET — Network and nodes

This is where the stack physically lives: **L0.1–L0.4** links and **LH.5** hosts. The chain side is loopback. The vehicle side is a model.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-NET-01 | Validator node | proposes / votes | L3.2, LH.5 | IMP-L3.2-01; HW-12; T-12 | BP-L3-01, L4-04, BP-L3.2-01 | 02,10 | PF-37, PF-60 | 04,02 | Ds |
| RV-NET-02 | RPC node | serves reads/writes | L0.4, LH.5 | IMP-L3.2-02 (today); HW-11 | BP-L0-01, L2-05, BP-LH-06, BP-L0.4-01 | 12 / 10 | PF-39 | 26 | M (#39, local) |
| RV-NET-03 | Archive node | full history | L2.2 | IMP-L2.2-02; T-10 | BP-L0-05, BP-L2.2-01 | 10,16 | R4 PF-05 | 27 | — |
| RV-NET-04 | Bootnode | discovery entry | L0.3 | IMP-L0.3-01; PRO-11a | BP-L0-01, BP-L0.3-01 | 10 | R4 PF-01′ | 02 | — |
| RV-NET-05 | RSU | credentialed roadside unit | LH.3, L7.3 | IMP-L7.3-02; C3 | BP-L7-01, BP-L0.2-01 | 12,14 | PF-48 | 16,39 | M (#44–#47, Sim) |
| RV-NET-06 | OBU | on-board unit | LH.3 | HW-08 | BP-L7-01 | 12,13 | PF-43 | 15,16,33 | — (Sim object only) |
| RV-NET-07 | TMC / controller | traffic management centre | L7.3 | IMP-L7.3-02; C3 | BP-L6-03 | 12 | — | 10 | M (#48) |
| RV-NET-08 | DIDComm mediator | message relay | L7.2 | PRO-25; T-I18 | BP-L7-02 | 09,10 | — | — | Ds |
| RV-NET-09 | Relayer / bundler | submits on behalf | L5.3 | PRO-22, PRO-22a | BP-L5-05 | 07 / 21 | — | 07 | M (#50) |
| RV-NET-10 | P2P link | devp2p link | L0.3 | PRO-11 | BP-L0-01, L0-02 | 10 | R4 PF-02′ | 18,37 | — |
| RV-NET-11 | V2X sidelink (PC5) | direct vehicle link | L0.1 | PRO-04; HW-09 | BP-L0-02, BP-L0.1-01 | 11,13 | PF-44; PF-46 reserved | 16,25,35 | I (model) |
| RV-NET-12 | Backhaul (Uu / fibre) | RSU ↔ cloud | L0.1, L0.2 | PRO-07; T-01 | BP-L0-02, BP-L0.2-01 | 10,12,14 | PF-48 | 16,39 | — |
| RV-NET-13 | Local Hardhat node | in-process or HTTP | L3.2 | IMP-L3.2-02; ALG-19 | — | 12 | PF-39 | 26 | M (M1, M1-H/HTTP) |
| RV-NET-14 | Docker testbed network | multi-container | LH.5 | IMP-LH.5-01 | BP-L0-02, BP-L0.4-01 | 10 | — | 18 | I |

**Deepen next.** Scale thread. *First question:* "Who brings up a ≥ 4-node network (Besu or otherwise) with a committed genesis (Q-R7-01, Q-R8-02)? Until then every RV-NET-01/03/04/10 cell stays Ds or —."

### 3.12 RV-DLT — The DLT as a system

This is the ledger seen whole: the L2–L4 properties a reader trusts without seeing. The settlement choice (SOL-01..05) lives here.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-DLT-01 | Ledger (append-only order) | one history | L2.1, L3 | T-09, T-10 | BP-L2-02 | 16,02 | R4 PF-13 | 01,03 | S |
| RV-DLT-02 | Finality | irreversible acceptance | L3.1 | ALG-20 / ALG-19 | BP-L3-01, L3-05 | 01 | PF-57, PF-40; PF-39 (≡ 0 on automine) | 03,05,31 | Ds |
| RV-DLT-03 | World-state trie | account/storage map | L2.1 | ALG-18; IMP-L2.1-03 | BP-L2-01 | 08 | PF-52 | 02 | M (#49) |
| RV-DLT-04 | Permissioning | who may run / send | L4.2 | IMP-L4.2-01; SOL-02 | BP-L4-06, BP-L4.2-01 | 02,18 | PF-60 | 28 | Ds |
| RV-DLT-05 | Governance | validator / issuer admission | L4.2 | IMP-L4.2-02/03 | BP-L4-06, L4-04, BP-L4.2-02 | 02 | PF-60; req PF-66 | 04,28 | Ds |
| RV-DLT-06 | Upgrade | client / contract change | L4.2, L5.2 | — (no proxies in repo) | BP-L5-04 | 04 | PF-61(e) | 02 | — |
| RV-DLT-07 | Fork / reorg | competing history | L3.1 | ALG-20c; T-13 | BP-L2-02, L3-05 | 01,02 | R4 PF-19, PF-21 | 03 | S |
| RV-DLT-08 | Checkpoint | commitment to a public chain | L2, L3 | SOL-03 | BP-L4-04 | 16 | R4 PF-13 | 13,14 | Ds |
| RV-DLT-09 | Anchoring (commitment form) | EDPB-compatible anchor | L2.3 | SOL-03; T-I15 | BP-L6-05 | 18,09 | PF-34; R4 PF-04′ | 30 | Ds |
| RV-DLT-10 | Capacity ceiling | ops/s per configuration | L4.3 | IMP-L4.3-01 | BP-L4-05 | 11 | PF-49 (G, Δ PAR; KD-R7-01 qualified) | 05,06 | Dv (PF-49) |
| RV-DLT-11 | Fee market | price of inclusion | L4.1 | ALG-22 | BP-L4-03 | 07,14 | R4 PF-23 | 07 | Ds |
| RV-DLT-12 | Settlement option A/B/C | HAA-1 Plane A choice | L3–L5 | SOL-02, SOL-04, SOL-05 | BP-L3-06, L4-04 | 03 | PF-58; R4 §4 | 18 | Ds |

**Deepen next.** Scale thread, and this Roots thread for theory. *First question:* "Should appendix H (design-only consensus bounds, SLD-13) exist, and which PF-58 (T, L, C) points does it plot (Q-R9-03)?"

### 3.13 RV-IMPL — Implementations, clients, tooling

Concrete software at **L3.2, L1.2 and L7.1**, and the evaluation tools that host it.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-IMPL-01 | Hardhat Network 2.28.6 | in-process EVM, chain 31337 | L3.2 | IMP-L3.2-02; `hardhat.config.js` | BP-L3.2-02 | 07,12 | PF-39 | 02 | M (M1 class) |
| RV-IMPL-02 | Hyperledger Besu | consortium client | L3.2 | IMP-L3.2-01; `V2_DESIGN.md` | BP-L3-03, BP-L3.2-01 | 01,10 | PF-37, PF-38, PF-40 | 02,03,31 | Ds |
| RV-IMPL-03 | Geth | public client | L3.2 | IMP-L3.2-03 | — | 10 | — | 02 | — |
| RV-IMPL-04 | Anvil | Foundry node | L3.2 | IMP-L3.2-04 | — | 12 | — | 02 | — |
| RV-IMPL-05 | Sepolia | public testnet | L3.2 | PRO-15; `SEPOLIA_VALIDATION.md` | BP-L4-03 | 07 | — | 18 | I (gas witness; JSON not committed; NC-07) |
| RV-IMPL-06 | Docker testbed | containerised stack | LH.5 | IMP-LH.5-01; IMP-L3.2-05 | BP-L0.4-01 | 10 | — | 18 | I |
| RV-IMPL-07 | SUMO | traffic simulation | L7.3 | IMP-L7.3-01 | — | 11 | — | 25 | E (#15; DRP-06) |
| RV-IMPL-08 | ethers v6 | JS client | L7.1 | IMP-L7.1-01; IMP-L1.2-04 | BP-L7-01 | 12 | — | 26 | M (harness) |
| RV-IMPL-09 | web3.py | Python client | L7.1 | IMP-L7.1-02; IMP-L0.4-01 | — | 12 | — | 26 | M (#21) |
| RV-IMPL-10 | snarkjs 0.7.6 | prover / verifier | L1.2 | IMP-L1.2-08 | BP-L1-06, BP-L1.2-04 | 12 | PF-35 | 11,41 | M (#57) |
| RV-IMPL-11 | circom 2.2.2 | circuit compiler | L1.2 | IMP-L1.2-07 | BP-L1-06, BP-L1.2-03 | 04 | PF-61 (audit) | 11 | M (#56) |
| RV-IMPL-12 | solc 0.8.24 / viaIR / cancun | compiler config | L5.1 | IMP-L5.1-01; IMP-L4.3-02 | BP-L5-04 | 07 | — | 02 | M (M1 class) |
| RV-IMPL-13 | Python VC/DID layer | `2_w3c-ssi-layer/` | L6.2 | IMP-L6.2-01..05 | BP-L6-09, BP-L6.2-01 | 19 | — | 09 | M (#4) |
| RV-IMPL-14 | W3C DID test suite | external conformance | L6.1 | ALG-23; T-I17 | — | 19 | — | 08 | M (#24) |
| RV-IMPL-15 | Veramo / ACA-Py / Credo | agent frameworks | L7.1 | IMP-L7.1-06 | — | 19 | — | 09 | — |
| RV-IMPL-16 | Indy-node / anoncreds-rs | O10/O12 implementations | L3.2, L1.2 | IMP-L6.1-01; IMP-L1.2-10 | BP-L1-05 | 06,19 | R4 PF-10 | 09 | Ds |

**Deepen next.** Scale thread, with G-RIM for the inventory. *First question:* "Commit the Sepolia witness JSON (or drop RV-IMPL-05), and decide whether a second client is ever run for MD-02 (D-10)."

### 3.14 RV-HW — Hardware

**LH**, the new bottom layer: the physical trust anchors that keys and clocks rest on (R6 HW-). Nothing at LH is measured except the measurement host itself.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-HW-01 | Secure element / eSIM | in-vehicle key store | LH.2 | HW-06 | BP-L1-07, BP-LH-03 | 06,20 | R4 PF-12 | 15 | — |
| RV-HW-02 | HSM | issuer / OBU key store | LH.2 | HW-03 | BP-L6-03 | 06,12 | PF-43 (E classes) | 15,33 | — |
| RV-HW-03 | TEE | isolated execution (Steward vault candidate) | LH.2 | HW-05 | BP-L1-07, BP-LH-03 | 06 | R4 PF-12 | 15 | — |
| RV-HW-04 | TPM | host attestation | LH.2 | HW-04 | BP-LH-06 | 06 | — | 15 | — |
| RV-HW-05 | ECU / gateway | vehicle compute | LH.3 | HW-07; PRO-01, PRO-02 | BP-L7-01, BP-LH-05 | 12,05 | — | — | — |
| RV-HW-06 | OBU hardware | V2X host | LH.3 | HW-08 | BP-L7-01 | 12,13 | PF-43 | 16,33 | — |
| RV-HW-07 | V2X modem | PC5 / 802.11p radio | LH.4 | HW-09 | BP-L0-02, BP-L0.1-01 | 13,11 | PF-44 | 16,35 | — |
| RV-HW-08 | GNSS receiver | time + position | LH.4 | HW-10 | BP-LH-04, BP-LH-05 | 15,05 | PF-47 | 38 | — |
| RV-HW-09 | Node server | validator / RPC host | LH.5 | HW-12 (validator), HW-11 (measurement host) | BP-L0-02, BP-LH-06 | 10,12 | — | 02 | — |
| RV-HW-10 | CPU (measurement host) | executes every M0/M1 result | LH.1 | HW-01 | — | 12 | — | 33 | M (environment only, #27, #57; PN-23d) |
| RV-HW-11 | GPU (attacker) | brute-force capacity | LH.1 | — | BP-L6-05, BP-L6.1-01 | 06,09 | PF-33 | 30 | E (#60 extrapolation) |
| RV-HW-12 | Hardware RNG | entropy source | LH.1 | HW-02; IMP-LH.1-01 | BP-L1-01, BP-LH-01 | 06 | PF-41, PF-42 | 34 | — (never measured; split from v0-1 RV-HW-10) |

**Deepen next.** Security campaign G-C1, with a new chat for vehicle E/E. *First question:* "Source primary HSM/ECU t_ver classes (Q-R7-02) so that PAR-33 has cited candidates and NC-05 can stay as worded."

### 3.15 RV-SVC — Off-chain services

HAA-1 Planes V and D and their helpers, at **L2.3 / L7.1**. They carry what the ledger should not: content, status distribution, caches.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-SVC-01 | Resolver service | DID → document, fail-closed | L6.1, L7.1 | SOL-17 (mechanism, PN-09); ALG-23 | BP-L2-05, BP-L0.4-02 | 12 / 10 | PF-52 (read), PF-57a | 26 | M (#31, local) |
| RV-SVC-02 | Verifier service (cached) | message-fresh, state-bounded decisions | L7.1 | `erc1056_provider.py` (state); IMP-L7.2-01, -03 (message) | BP-L7-03, BP-L7.2-03 | 14,15 | PF-54, PF-47 | 19,20,38 | M (#32, #37) |
| RV-SVC-03 | Status service | publishes list / root | L2.3 | IMP-L2.3-02; SOL-09 | BP-L6-07, L0-05 | 10,14 | R4 PF-29; PF-48 | 12 | Ds |
| RV-SVC-04 | Archive (Plane D) | content availability | L2.3 | SOL-05 | BP-L0-05, L2-04, BP-L2.3-01 | 10,18 | R4 PF-05 | 27 | Ds |
| RV-SVC-05 | IPFS / CAS | content addressing | L2.3 | IMP-L2.3-05 | BP-L2-04 | 10 | R4 PF-05 | 27 | — |
| RV-SVC-06 | Steward agent | disclosure control | L7.1 | SOL-14; IMP-L7.1-05 | BP-L6-05, BP-L7.3-01 | 09,22 | PF-62 (partial) | 22 | M (#61) |
| RV-SVC-07 | Oracle | off-chain fact on chain | L5.2 | — | BP-L6-07, BP-L7.3-01 | 04,16 | qual. | — | — |
| RV-SVC-08 | Keeper (intent fulfiller) | executes `fulfil` | L7.1 | SCF-IDTX-04 | BP-L3-06 | 21,10 | — | 05 | I |
| RV-SVC-09 | Issuer service | signs VCs | L7.1 | IMP-L6.2-01 | BP-L6-03 | 12 | — | 15 | M (#21) |
| RV-SVC-10 | Trust-registry service | accredited issuers | L4.2, L6 | IMP-L4.2-03; SCF-MOBI2-01 | BP-L4-06, BP-L4.2-02 | 02 | PF-60 | 28 | I (on-chain lists) |

**Deepen next.** Latency thread (Plane V), with Scale for Plane D. *First question:* "Under PAR-39 backhaul models, which W quantile (PF-48) does each RSU class need, and does the verifier fail closed when the backhaul is down?"

### 3.16 RV-SCN — Application scenarios

**L7.3** holds the reasons the stack exists. Each scenario composes the rows above, so measuring a scenario means measuring its chain.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-SCN-01 | Tolls | identity-gated payment | L7.3 | IMP-L7.3-05; RV-IDTX-25 | BP-L5-05 | 07,13,09 | R4 PF-31 | 07,18 | I |
| RV-SCN-02 | Gated access (zk) | admit on predicate | L7.3 | IMP-L7.3-06; RV-IDTX-28 | BP-L1-06 | 07 / 09 | PF-35 | 11 | M (#58) |
| RV-SCN-03 | Licence endorsement 7 → 5 | upgrade a driver credential | L7.3 | RV-VC-03; §4.5 | BP-L6-03, L6-04 | 14,16,18 | PF-48 | 09,12 | Ds |
| RV-SCN-04 | Maintenance record | service history | L7.3 | IMP-L7.3-03; RV-SCF-19, -28 | BP-L6-07 | 07 / 16 | — | 17 | M (#35) |
| RV-SCN-05 | Crash record | forensic event | L7.3 | RV-VC-16 | BP-L0-05, L6-07, BP-L2.3-01 | 16,10 | R4 PF-05 | 27 | Ds |
| RV-SCN-06 | Ownership transfer | sale | L7.3 | RV-SCF-17 | BP-L5-05 | 07 / 16 | — | 17 | M (#35) |
| RV-SCN-07 | Pay-per-use | metered service | L7.3 | RV-IDTX-22 | BP-L4-03 | 07 | R4 PF-23 | 07 | — |
| RV-SCN-08 | RSU SPaT | signed signal timing | L7.3 | IMP-L7.3-02; RV-PROT-11 | BP-L7-07 | 12,14 / 13 | PF-43, PF-54 | 19,24 | M (#44, #46) |
| RV-SCN-09 | I2I message | infrastructure-to-infrastructure | L7.3 | IMP-L7.3-02 | BP-L7-05 | 12 / 05 | — | 10 | M (#48, crypto cost only) |
| RV-SCN-10 | V2V BSM authentication | per-message trust | L7.3 | §4.3; IMP-L7.3-01 | BP-L7-07, BP-L7.2-04 | 13 / 11 | PF-43, PF-44 | 24,25,33,36 | M (#27; server-class host, not vehicle) |
| RV-SCN-11 | Agent identity | agent acting for the vehicle | L7.3 | T-I22; Set C | BP-L6-06 | 04,09 | qual. | 21 | Ds |
| RV-SCN-12 | Pseudonymous V2X (M5 on-chain pool) | rotating identities as ERC-1056 delegates | L7.3 | IMP-L7.3-04; SCF-EDR-05 | BP-L6-05, BP-L7.2-01, BP-L0.1-02 | 09 / 07 | PF-62, PF-44c | 22 | M (#38): **negative result, linkable** (PN-23c) |
| RV-SCN-13 | Vehicle birth | manufacturer creates identity | L7.3 | RV-VC-15; SOL-13 | BP-L6-03 | 07 | — | 17 | M (#33) |

**Deepen next.** G-MV1 for lifecycle, Latency for SPaT/BSM, and a new chat for tolls, licences and pay-per-use. *First question (G-MV1):* "Is the M5 pool retired as a design (CA-11), and what replaces it for R5 unlinkability?"

### 3.17 RV-GOV — Governance and regulatory

These are mostly **L4.2**, plus the legal envelope above L7. MD-02 and MD-18 dominate.

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-GOV-01 | Validator admission | who joins consensus | L4.2 | IMP-L4.2-02; SOL-02; T-03 | BP-L4-06, L4-04 | 02 | PF-60; R4 PF-16 | 04,28 | Ds |
| RV-GOV-02 | Issuer accreditation | who may issue | L4.2, L6 | SCF-MOBI2-01; IMP-L4.2-03 | BP-L6-03, L4-06, BP-L4.2-02 | 02,04 | PF-60 | 28 | I |
| RV-GOV-03 | GDPR erasure | right to be forgotten | — (legal) | R2 §4 | BP-L6-05 | 18 | qual. | 17,30 | Ds |
| RV-GOV-04 | EDPB commitment-form posture | no personal data on chain | — | SOL-03; T-I15; PRM-L1.1-03 | BP-L6-05, BP-L6.1-01 | 18,09 | PF-34 | 30 | Ds (#60 shows unsalted VIN reversible) |
| RV-GOV-05 | Audit | after-the-fact proof | L4.2, L5 | R3 R4 | BP-L4-04 | 16 | R4 PF-13 | 13 | Ds |
| RV-GOV-06 | Key-ceremony governance | ZK trusted setup | L1 | ALG-12; IMP-L1.2-08 | BP-L1-06, BP-L1.2-04 | 06 | PF-35; R4 PF-11 | 41 | M (#57: setup single-party, insecure; PN-28) |
| RV-GOV-07 | Registry authority transfer | admin handover (silent) | L5.2 | SCF-MOBI1-03 | BP-L4-06, L5-04, BP-L4.2-02 | 04 | req PF-66 | 28 | I |
| RV-GOV-08 | Standards conformance claim | W3C / MOBI | — | RV-MET-05 | BP-L6.2-01 | 19 | — | 08 | M (#4, #24) |

**Deepen next.** G-WHY, with G-C1 for audit. *First question:* "State the governance posture of every single-key role (registryAuthority, governor, ISSUER_ROLE) and say whether m-of-n is in scope (CA-16, PF-66)."

### 3.18 RV-MET — Evaluation artefacts

These rows show how evidence anchors *upwards*: each artefact turns a Ds row into an M row.

| RV | Item | Meaning | Evidences | Anchors | MD | St |
|---|---|---|---|---|---|---|
| RV-MET-01 | Claim register (`MEASUREMENT_CONDITIONS.md`) | every number with status | all M rows | **62 numbered rows** (2026-10-23; PN-29) | 17 | M |
| RV-MET-02 | Hardhat test suites | contract behaviour | RV-SC, RV-SCF | **562** Hardhat (STATUS l. 112) | 04 | M |
| RV-MET-03 | Python tests | VC/DID/testbed | RV-VC, RV-READ | **376** Python (STATUS l. 112) | 04,19 | M |
| RV-MET-04 | Metrics harness (ten columns) | gas, footprint, reads | RV-IDTX, RV-SCF | #29–#36, #49–#51 | 07,08,12 | M |
| RV-MET-05 | W3C checker + external DID suite | conformance | RV-IDTX-02 | #4, #24 | 19 | M |
| RV-MET-06 | Security matrix (43 attacks) | SC security, PF-61(d) | RV-SC | #28 | 04 | M |
| RV-MET-07 | Pre-registered I1–I5 | infrastructure messaging | RV-SCN-08/09 | #44–#48 | 12,14 | M |
| RV-MET-08 | Freshness experiments | W, staleness | RV-ALG-09 | #32, #37, #52, #55 | 14,15 | M |
| RV-MET-09 | IDTx tests + mutants | PF-61(c) for SOL-10 | RV-IDTX-21..24 | `phase2/idtx/test/idtx.test.js`; `mutate_idtx.sh` | 04 | I |
| RV-MET-10 | ZK bench + attacks | ZK costs, leakage | RV-PRIM-10, RV-VC-07 | #56–#62 | 07,09,12 | M |
| RV-MET-11 | CI (8 jobs) | regression | all | `.github/workflows/` | 17 | M |
| RV-MET-12 | Sepolia witness | gas external validity | RV-IMPL-05 | `SEPOLIA_VALIDATION.md` (JSON not committed) | 07 | I (NC-07) |
| RV-MET-13 | Defect log | known faults | RV-SC | `docs/DEFECT_LOG.md` (STATUS §1.1 counts; re-read statuses per PN-01) | 04 | M |
| RV-MET-14 | Crux register | thesis claims ↔ rows | RV-SCN | `docs/thesis/CRUX_REGISTER.md` C1–C8 | 17 | M |
| RV-MET-15 | Consensus / finality testbed | MD-01/02/10 measurement | RV-DLT-02, RV-ALG-01 | — (needs a multi-node network) | 01,02,10 | — |

**Deepen next.** G-RIM, with this Roots thread for register discipline. *First question:* "Fix register row #26's internal inconsistency (CA-09: 0.156 vs 0.164 ms/neighbour) before SLD-03 cites it."

### 3.19 RV-THR — Threat and adversary operations

These are the attacks that the BP- rows abstract, phrased as *operations* so that they can be measured like any other function. Rows 11–15 are new (PN-28).

| RV | Item | Meaning | Sub-layer | Anchors down to | BP | MD | PF | PAR | St |
|---|---|---|---|---|---|---|---|---|---|
| RV-THR-01 | VIN-hash enumeration | reverse unsalted commitment | L1.1 | RV-PRIM-02; ALG-08 | BP-L6-05, BP-L6.1-01 | 09,06 | PF-33, PF-62 | 30 | M (#60) |
| RV-THR-02 | Predicate narrowing | twenty questions | L6.2 | RV-VC-07 | BP-L6-05 | 09 | PF-62 (partial) | 22 | M (#61) |
| RV-THR-03 | Stale-cache acceptance | use revoked identity | L7.1 | RV-ALG-09 | BP-L7-03, BP-L7.2-03 | 14 | PF-54 | 19,20 | M (#46) |
| RV-THR-04 | SPaT replay / forgery | message attacks | L7.2 | RV-ALG-10 | BP-L7-04, BP-L5.2-03 | 05 | PF-47, PF-53 | 38,40 | M (#45) |
| RV-THR-05 | Rotation race | attacker vs owner rotation | L6.3 | RV-IDTX-03 | BP-L6-02 | 21 | R4 PF-25; PF-40 | 05,32 | — (single node) |
| RV-THR-06 | Validator collusion | rewrite private history | L4.2 | RV-GOV-01 | BP-L4-04 | 02 / 16 | PF-60; R4 PF-13, PF-16 | 04 | Dv (from E p_c) |
| RV-THR-07 | Eclipse of a node | false view | L0.3 | RV-NET-04; PRO-11a | BP-L0-01, BP-L0.3-01 | 05 | qual. (no P2P in repo) | 18 | — |
| RV-THR-08 | Contract attack matrix | 43 attacks | L5.2 | RV-MET-06 | BP-L5-04 | 04 | PF-61(d) | — | M (#28) |
| RV-THR-09 | Sybil split vs per-verifier cap | defeat static cap | L7.1 | RV-SVC-06 | BP-L6-05 | 09 | PF-62 | 22 | M (#61) |
| RV-THR-10 | GNSS spoofing | false time / position | LH.4 | RV-HW-08; HW-10 | BP-LH-04, BP-LH-05 | 15,05 | PF-47 | 38 | — |
| RV-THR-11 | Cross-chain replay of `*Signed` ops (D52) | owner change replayed on another chain | L5.2 | SCF-EDR-04/06/08/10/12; precondition met by default (31337/1337, same deployer) | BP-L5.2-01 | 05,04 | precondition, not probability (PN-03) | 18 | I (source-read; CA-02 pending) |
| RV-THR-12 | Zero-signer seizure (D53) | r = s = 0 seizes DID 0x0 | L5.2 | SCF-EDR-04; PRO-16 | BP-L5.2-02 | 04 | — | — | I (source-read; CA-03) |
| RV-THR-13 | Lying RPC endpoint | stale / false state returned | L0.4 | PRO-13; ALG-23 | BP-L0.4-02, BP-LH-06 | 05,15 | req PF-64 | 26 | — (no test; NC-06) |
| RV-THR-14 | Pseudonym-pool linkage | one `eth_getLogs` links all pseudonyms | L6.1, L0.4 | IMP-L7.3-04; SCF-EDR-05 | BP-L7.2-01 | 09 | PF-62 (k_A = 1) | 22 | M (#38: 60/60) |
| RV-THR-15 | Deterministic test-key derivation | key = SHA-256(vehicle_id) | LH.1 | IMP-LH.1-02 | BP-LH-02 | 06 | req PF-63 | 34 | I (source-read; CA-18) |

**Deepen next.** Security campaign G-C1. *First question:* "Execute the two-chain replay test (CA-02) so that RV-THR-11 moves from I to M, and decide fix vs fidelity (B-02)."

---

## 4. Worked anchor chains (lead chain now the measured one; PN-30, DRP-10)

Each chain starts at the top and descends one step per line, naming the layer and the tag that carries each step.

### 4.1 Lead chain — revokeCredential and the window W (was v0-1 §4(d))

1. **L7.3** an authority revokes an RSU or vehicle credential (RV-SCN-08).
2. **L6.3** RV-IDTX-12; **L6.2** RV-VC-10.
3. **L5.2** RV-SCF-13 `revokeIdentity` (SCF-VPR-07, emits `previousChange`), or a status update (SCF-E1155-03 / SCF-E735-03 / IMP-L2.3-02).
4. **L5.3 → L3.1** RV-TX-01 ordered by ALG-19 (automine; PF-39). The settlement share of W under QBFT is DESIGN (PF-40, PF-57).
5. **L2.3** RV-SVC-03 status published (Ds).
6. **L7.1** the verifier's *state* cache refreshes every k_f (PAR-19), RV-ALG-09 in `erc1056_provider.py`. Accepts after revocation are ≤ k_f − 1 messages (PF-54). With no TTL (RV-READ-14) the bound is in messages, not seconds.
7. **L7.1** message freshness (RV-ALG-10, `freshness.py`) is a separate guard and does not bound W.
8. A checkpoint (RV-DLT-08) makes the timing forensic. It does not shorten W.
**MDs:** 14 (#32, #37, #46), 15, 07 (#22), 16. **Status:** the k-bound is M (#46 PASS, verifier v3, in-process registry). The time bound needs a TTL (SLD-05). The public settlement share is Ds.

### 4.2 A DID resolution read at Tier 2

1. **L7.3** a verifier at an intersection needs the sender's key (Tier 2; PF-43, R4 PF-31).
2. **L7.1** RV-SVC-02: state-cache hit → RV-READ-03 (`erc1056_provider.py`); every k_f-th message → refresh.
3. **L6.1** RV-READ-04 probe (`getIdentityInfo`, SCF-VPR-01); if changed, RV-READ-01 full replay (ALG-23).
4. **L0.4** RV-PROT-07 JSON-RPC (PRO-13) over PAR-26; responses are unproven (BP-L0.4-02, RV-THR-13).
5. **L3.2** RV-NET-02 (IMP-L3.2-02 today) → **L2.1/L2.2** IMP-L2.1-02 logs, history h → **LH.5** HW-11.
**MDs:** 12 (#31, #37), 13, 15 (#52). **Status:** M at M1 / M1-H/HTTP. M2 not measured.

### 4.3 A signature on a V2X BSM

1. **L7.3** RV-SCN-10 at 10 Hz (PRO-24).
2. **L7.2** RV-PROT-10 JSON-like BSM (PRO-23; IMP-L7.2-02). The 1609.2 SPDU (RV-PROT-08) is Ds.
3. **L6.1** sender key = DID verification method (SCF-VPR-05/08) or an X.509 P-256 certificate (RV-SIG-11).
4. **L1.1** ALG-04 ECDSA secp256k1 over SHA-256 (not EIP-191; KD-R6-04). **LH.2** key in SE (RV-HW-01, Ds). The testbed key is SHA-256(vehicle_id) (RV-THR-15).
5. **L0.1** RV-NET-11 PC5 (model); airtime RV-PROT-16 (PF-44); resource persistence links pseudonyms (PF-44c).
6. The receiver verifies (RV-SIG-02, PF-43), then applies message freshness (RV-ALG-10) and the state cache (RV-ALG-09).
**MDs:** 12 (#27), 13 and 11 (PF-43, PF-44), 09 (PF-62). **Status:** verify M (#27, server-class host). Airtime Dv. Radio I. Vehicle hardware —.

### 4.4 A write transaction (to finality in design only)

1. **L6.3** RV-IDTX-03 changeOwner (SCF-EDR-03) → **L7.1** RV-IMPL-08/09 build and sign (ALG-02; RV-PRIM-14 RNG, —).
2. **L5.3** RV-TX-01 (PRO-21) → **L0.4** PRO-13 → **L3.1** ALG-19 (M, N_v = 1) or ALG-20 (Ds, PF-40/57).
3. **L5.1** execution and gas (RV-ALG-08) → **L2.1** state and logs (RV-DLT-03, RV-TX-14) → **L2.2** IMP-L2.2-01 (today) or IMP-L2.2-02 (Ds).
4. **L5.3** RV-TX-09 checkpoint every τ_a (PAR-13); detection ≤ τ_a + t_pub (R4 PF-13), Ds.
**MDs:** 07 (#2), 08 (#49), 12; 01, 02 and 21 are design only. **Status:** steps 1–3 are M on Hardhat. Finality and checkpoint are Ds.

### 4.5 A VC endorsement: licence class upgrade (retained as Ds; not the illustrative chain)

RV-SCN-03 → RV-SVC-09 → RV-VC-03 = RV-VC-01 + RV-VC-11 → RV-READ-01 → RV-SIG-01 (ALG-02; or ALG-16 in O12) → RV-HW-02 (HW-03) → RV-IDTX-12 → status anchor SCF-E1155-03 / SCF-E735-03 / IMP-L2.3-02 → RV-TX-01 → RV-SVC-03 → RV-VC-04, RV-VC-08/09. **Status:** Ds end to end (Q-R8-01). The parts are M elsewhere (#21, #46).

---

## 5. Coverage matrix — categories × MD (recomputed by `r8_coverage.py`)

Cell code (PN-27): **●** measured (at least one row with St M that covers that MD, i.e. the MD sits before the slash) · **◐** derived only (at least one Dv row covers it and no M row does) · **○** design (rows target that MD but none evidences it: Ds, I, E, S, —, or listed after the slash) · **·** empty. The script parses §3 of this file. Re-run it after any edit.

<!-- COVERAGE-BEGIN -->
| Cat | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TX | ○ | · | · | ○ | ○ | · | ● | ● | ○ | · | ○ | ● | · | · | ● | ○ | · | ○ | · | ○ | ○ | · |
| IDTX | ○ | · | · | ○ | · | ○ | ● | ● | ○ | · | · | ● | ○ | ○ | ● | ○ | · | ○ | ○ | · | ○ | · |
| VC | · | · | · | ○ | · | ○ | ● | ● | ● | · | · | ● | ○ | ● | ● | ○ | · | ○ | ○ | · | · | ● |
| SIG | · | · | · | · | ○ | ○ | ● | · | ○ | · | · | ● | ○ | ○ | · | · | · | · | · | ○ | ○ | · |
| READ | · | · | · | · | ○ | · | ○ | · | ○ | ○ | ● | ● | · | ○ | ● | ○ | · | · | ○ | · | · | · |
| PRIM | · | · | · | · | ○ | ● | ● | · | ● | · | · | ● | · | · | · | · | · | ○ | · | · | · | · |
| ALG | ○ | ○ | · | · | ● | ● | ● | · | ● | ○ | ○ | ● | · | ● | ● | · | ● | · | ● | · | · | ● |
| PROT | · | · | · | · | ○ | · | ● | · | ○ | ○ | ◐ | ● | ● | · | · | ○ | · | · | ○ | · | · | · |
| SC | · | · | · | ○ | · | · | ● | ● | ○ | · | · | ● | · | · | · | ○ | · | · | ○ | ○ | ○ | · |
| SCF | · | ○ | · | ○ | · | · | ● | ● | ○ | · | · | · | · | ○ | · | ○ | · | ○ | · | ○ | ○ | · |
| NET | · | ○ | · | · | · | · | ● | · | ○ | ○ | ○ | ● | ○ | ● | · | ○ | · | · | · | · | ○ | · |
| DLT | ○ | ○ | ○ | ○ | · | · | ○ | ● | ○ | · | ◐ | · | · | ○ | · | ○ | · | ○ | · | · | · | · |
| IMPL | ○ | · | · | ● | · | ○ | ● | · | · | ○ | ○ | ● | · | · | · | · | · | · | ● | · | · | · |
| HW | · | · | · | · | ○ | ○ | · | · | ○ | ○ | ○ | ● | ○ | · | ○ | · | · | · | · | ○ | · | · |
| SVC | · | ○ | · | ○ | · | · | · | · | ● | ○ | · | ● | · | ● | ● | ○ | · | ○ | · | · | ○ | ● |
| SCN | · | · | · | ○ | ○ | · | ● | · | ● | ○ | ○ | ● | ● | ● | · | ○ | · | ○ | · | · | · | · |
| GOV | · | ○ | · | ○ | · | ● | · | · | ○ | · | · | · | · | · | · | ○ | · | ○ | ● | · | · | · |
| MET | ○ | ○ | · | ● | · | · | ● | ● | ● | ○ | · | ● | · | ● | ● | · | ● | · | ● | · | · | · |
| THR | · | ◐ | · | ● | ● | ● | · | · | ● | · | · | · | · | ● | ○ | ○ | · | · | · | · | ○ | · |

The fall from v0-1's 128 ● reflects the PN-27 split, the slash rule (an M row counts only for the MDs it evidences) and the PN-23 downgrades. No measurement was lost.

**Headline (19 × 22 = 418 cells; 311 rows):** **● 77 measured** (18.4 %) · **◐ 3 derived only** (0.7 %) · **○ 115 design** (27.5 %) · **· 223 empty** (53.3 %).

MD columns with no ● cell: MD-01, MD-02, MD-03, MD-10, MD-16, MD-18, MD-20, MD-21. These are the consequence of one automining node (PF-39) and of absent hardware, and are not a gap in the bookkeeping.
<!-- COVERAGE-END -->

---

## 6. Routing summary

The "Deepen next" lines in §3 replace v0-1's routing table. In short: TX, SC → Cost · IDTX, SCF → IDTX work chats · VC → G-RIM (+ new chat for RV-VC-03) · SIG, THR, HW → Security campaign G-C1 · READ, PROT, SVC → Latency · PRIM, ALG → this Roots thread · NET, DLT, IMPL → Scale · SCN → G-MV1 / Latency / new chat · GOV → G-WHY · MET → G-RIM.

---

## 7. Locking the DID / DID-system primitives (from R9 §6)

*What this section does for the level above:* chapters 3–5 compare "an identical operation set" across substrates, and that comparison is only as firm as the names and semantics of the operations. *What it trusts from below:* L1 primitives and L5.2 registry state. The table lists the minimal RV rows that each R9 primitive (PRM-) locks. All of them are flagged **LOCK-candidate**. A row becomes LOCKED when the author ticks every blocking question in the parallel primitives review and `PRIMITIVES_LOCK v1.0` is frozen (R9 §6.3 item 12).

| ☐ | RV row(s) | PRM | Primitive / semantics to lock | Evidence today | Blocking B-nn | Flag |
|---|---|---|---|---|---|---|
| ☐ | RV-PRIM-06, RV-SIG-01, RV-SIG-02 | PRM-L1.1-01 | ECDSA secp256k1, RFC 6979, low-s; **one digest per use** | S / M (#27, #48) | B-03 | LOCK-candidate |
| ☐ | RV-PRIM-01, RV-PRIM-02 | PRM-L1.1-02 | keccak for on-chain digests; SHA-256 for BSM (or switch) | S / M (#60) | B-08 | LOCK-candidate |
| ☐ | RV-PRIM-04, RV-IDTX-24 | PRM-L1.1-03 | salted commitment C = H(x ‖ s), \|s\| ≥ 128 bits, mandatory for VIN | I | **B-05** | LOCK-candidate |
| ☐ | RV-PRIM-10, RV-GOV-06 | PRM-L1.1-04 | Groth16 / Poseidon with the setup trust stated | M (#56–#58) | B-09 | LOCK-candidate |
| ☐ | RV-SIG-03 | PRM-L5.2-03 (part) | ecrecover guard `signer ≠ 0` | I | B-07 | LOCK-candidate |
| ☐ | RV-IDTX-01 | PRM-L5.2-02 | createDID = implicit (0 gas) or explicit `registerVehicle` | M (#22, #47) | B-06 | LOCK-candidate |
| ☐ | RV-IDTX-03, RV-SCF-01/02 | PRM-L5.2-03 | changeOwner (+Signed): chain-id scope, zero-address semantics | M (#2) / I (D52) | **B-02**, B-07 | LOCK-candidate |
| ☐ | RV-IDTX-07, -08, -09 | PRM-L5.2-04 | add/revoke delegate; validDelegate in chain time; revoke = validTo := now | M (#2, #29, #51) | **B-04** | LOCK-candidate |
| ☐ | RV-IDTX-05, -06 | PRM-L5.2-05 | set/revoke attribute; "permanent" = 100-year validity | M (#2, #29, #49) | B-04 | LOCK-candidate |
| ☐ | RV-IDTX-04 | PRM-L5.2-06 | deactivation with `previousChange` (in VPR, absent in EDR) | M (#35) | B-10 | LOCK-candidate |
| ☐ | RV-IDTX-13 | PRM-L6.2-03 | createPresentation (F8): salted digests, nonce anchor | M (#54) | — | LOCK-candidate (no blocker) |
| ☐ | RV-IDTX-14 | PRM-L6.3-02 | X1 execute requires a real executor (725xy, 4337) | M (#54) | B-15 | LOCK-candidate |
| ☐ | RV-IDTX-01..14 (names) | PRM-L6.3-01 | IMinimalSSI F1–F12 numbering inside Sets A/B ("IMS-F*n*") | — [B1] | **B-01** | LOCK-candidate |
| ☐ | RV-IDTX-23 | PRM-L6.3-03 | IDTX dependency kinds; caller-independent predicate (P2-D8) | I | — | LOCK-candidate (no blocker) |
| ☐ | RV-READ-01, RV-ALG-04 | PRM-L6.1-02 | did:ethr resolution: replay from `changed`, fail-closed, chain-time validity, modes labelled | M (#24, #31) | B-12 | LOCK-candidate |
| ☐ | RV-READ-02 | PRM-L6.1-01 | did:ethr syntax with chain qualifier; CAIP-10 decimal reference | M (M0) | B-11 | LOCK-candidate |
| ☐ | RV-READ-10 | PRM-L6.1-03 | did:mobi identifier from a salted VIN hash; salt custody | M (#29) | B-05 | LOCK-candidate |
| ☐ | RV-ALG-10 | PRM-L7.2-01 | signed message = payload ‖ generation time; window; content-keyed replay cache | M (#45) | B-08 | LOCK-candidate |
| ☐ | RV-READ-03, RV-READ-14, RV-ALG-09 | PRM-L7.2-02 | state refresh every k_f **and** TTL | M (#32) / — (TTL) | B-16 | LOCK-candidate |
| ☐ | RV-VC-01, RV-VC-08 | PRM-L6.2-01 | VC 2.0 DI, `eip191-secp256k1-recovery-2024`, deterministic JSON (declared deviation) | M (#4, #27) | B-13 | LOCK-candidate |
| ☐ | RV-VC-09 | PRM-L6.2-02 | credential status anchored or not | M (#32) | B-14 | LOCK-candidate |

Two rows have no blocker (PRM-L6.2-03, PRM-L6.3-03) and can be locked at once. The bold blockers (B-01, B-02, B-04, B-05) gate the most rows.

---

## 8. Key changes v0-1 → v0-2

| # | Change | Where | PN / source |
|---|---|---|---|
| 1 | Option mapping corrected: 721 → O3, 725 → O5, 725xy/735 → O6, 1155 → O2, LSP8 → none, Combined → O18 precursor | §0, §3.9 | PN-22, X-11 |
| 2 | Status downgrades: RV-SCF-32 → — (stub); RV-IDTX-14 re-anchored to SCF-E725XY-04/E4337A-02; RV-SIG-12 → Ds; RV-SCN-12 → M negative result; RV-HW-10 → CPU only, RNG split to RV-HW-12 (—); Sepolia rows M → I | §3.2, 3.4, 3.10, 3.13, 3.14, 3.16, 3.18 | PN-23, NC-07 |
| 3 | State staleness separated from message freshness; RV-READ-03, RV-ALG-09, RV-SVC-02 re-anchored to `erc1056_provider.py` | §3.5, 3.7, 3.15, §4.1 | PN-24 |
| 4 | Every MD bound to an R7 PF | §1 | PN-25, Table C′ |
| 5 | PAR registry: sole owner; R7 mapping table; PAR-31..43 appended; each PAR lists the MDs and PFs it feeds | §2 | PN-26, PN-31, Table B |
| 6 | Coverage cell split ● / ◐ / ○ / ·; MD "evidenced / not evidenced" slash notation; matrix computed by script | §0, §5, `r8_coverage.py` | PN-27 |
| 7 | New rows RV-THR-11..15, RV-PROT-16, RV-READ-14, RV-SCF-43/44, RV-HW-12; RV-GOV-06 cites #57 | §3 | PN-28, PN-23 |
| 8 | Counts: 62 register rows; 562 / 376 tests | §3.18 | PN-29, PN-07 |
| 9 | Measured revocation chain leads; licence chain demoted to §4.5 | §4 | PN-30, DRP-10 |
| 10 | All bracketed placeholders resolved (R9 Tables D′, A′, B′); open PFs declared as "req PF-63..66", "open" or "qual." | throughout, §9 | PN-03, §3.3 |
| 11 | Unified status scale incl. I | §0 | PN-32 |
| 12 | Re-keying Q-R8-nn, KD-R8-nn; "Deepen next" per category; §7 primitives lock | §3, §7, §10 | §3.1, §6 |
| 13 | RV-ALG-02 no longer offers an MD-01 cell (Hardhat is not time-to-confirm) | §3.7 | SLD-01, NC-01 |

---

## 9. Open bound rows (declared, not placeholders)

| Row(s) | Needed | Disposition |
|---|---|---|
| RV-THR-15 | κ of deterministic test keys | req **PF-63** |
| RV-READ-13, RV-THR-13 | false-read probability vs independent endpoints | req **PF-64** |
| MD-02 (correlated failure) | p_c with correlation ρ_c | req **PF-65** |
| RV-DLT-05, RV-GOV-07, MD-20 | governance key vs m-of-n | req **PF-66** |
| RV-IDTX-21, RV-SC-15 | IDTX dependency gas | open (Q-R7-03, E-F1-1) |
| RV-TX-06 | relay overhead formula | open (#50 measures; qual.) |
| RV-TX-08, RV-TX-13, RV-IDTX-16, RV-SVC-07, RV-SCN-11, RV-THR-07, MD-18 | — | qual. by decision |
| PAR-37 | gossip PF | R7 to assign or drop (PN-10) |

---

## 10. Change log

| Ver | Date | Change |
|---|---|---|
| v0-1 | 2026-10-23 | First pass: 301 rows (headline 128 ● / 83 ○ / 207 ·), MD-01..22, PAR-01..30, 155 placeholders. |
| v0-2 | 2026-10-23 | Second pass applying R9 PN-22..30 (+ PN-03, 07, 26, 31, 32 cross-document). 311 rows (+10). PAR-01..43. Zero bracketed placeholders. Coverage recomputed by script. Primitives lock section added. |

**Retirement lines (R9 §3.1).** ~~Q-R7 (R8)~~ → Q-R8-01 · ~~Q-R8 (R8)~~ → Q-R8-02 · ~~Q-R9 (R8)~~ → Q-R8-03 · ~~Q-R10 (R8)~~ → Q-R8-04 · ~~R7 PAR-01..26~~ → R8 PAR per §2.1 · ~~PRO-13x/y/z~~ → PRO-23/24/25 (cited) · ~~RV-HW-10 "CPU / RNG"~~ → RV-HW-10 CPU + RV-HW-12 RNG · v0-1 "Five decisions" → KD-R8-01..05.

---

## 11. HANDOFF (R8 v0-2)

**Files.** `docs/roots/phase2/80_R8_reverse_register/claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-2.md` (this file) and `r8_coverage.py` (same folder). v0-1 is untouched. Nothing outside `docs/roots/phase2/` was modified.

**Tags.** RV-: 311 rows in 19 categories (TX 15 · IDTX 25 · VC 19 · SIG 14 · READ 14 · PRIM 15 · ALG 14 · PROT 16 · SC 20 · SCF 44 · NET 14 · DLT 12 · IMPL 16 · HW 12 · SVC 10 · SCN 13 · GOV 8 · MET 15 · THR 15). MD-01..22. **PAR-01..43 (sole owner).** Q-R8-01..05. KD-R8-01..06. **Consumed:** R6 HW-/PRO-/ALG-/IMP-/SCF-/BP-LH/Lx.y/SOL-10..17; R7 PF-32..62; R9 PN-, SLD-, NC-, CA-, PRM-, B-.

**Load-bearing decisions.** **KD-R8-01** Status I is suite-wide. M needs a V row; source-read code facts are I. **KD-R8-02** The MD slash notation: an M row evidences only the MDs before the slash. **KD-R8-03** Coverage uses ● / ◐ / ○ / ·, computed by script from this file only. **KD-R8-04** R8 owns PAR-; the numbers are frozen and R7 v0-2 must cite them. **KD-R8-05** MD-18 is qualitative by decision. **KD-R8-06** Message freshness and state staleness are separate rows and separate PFs.

**Open questions.** Q-R8-01 licence endorsement: supersession or attestation? Q-R8-02 owner of MD-01/02/10 (multi-node run). Q-R8-03 measure M2 latency at all? Q-R8-04 is 1609.2 encoding in scope (answer with Q-R6-04)? **Q-R8-05** (new) Is the slash notation adopted by R6 §7 for its measured-vs-designed table, so that SLD-12's two figures agree?

**Corrections issued.** PN-22 mapping, PN-23 downgrades (five rows plus the Sepolia rows), PN-24 re-anchoring, PN-29 counts. No status was upgraded.

**For the figures agent.** Regenerate FIG-R11 from the `r8_coverage.py` output (four cell codes).
