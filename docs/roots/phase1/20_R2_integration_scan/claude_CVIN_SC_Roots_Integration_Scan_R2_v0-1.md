# CVIN-SC · R2 — Roots Integration Scan

**One map: every corpus artefact, every root primitive, every evaluated option, and every programme solution, placed on the eight-layer stack — so that the I2I/identity document (R3) and the proof document (R4) are written against an integrated picture rather than producing one afterwards.**

Document 2 of the Roots suite (thread G-R1, provisional) · v0.1 · 2026-09-15 · CVIN-SC Research Programme · UBC ECE MASc
Consumes: R1 v1.1 (layers L0–L7, tags T-01–T-24, T-I01–T-I22) · the corpus as sampled by project search (Terminology Freeze G-D2-D3-H2; Building Paths v1.1 preface; Family E v2.0; P1–P4 placement suite; G-B; G-C1; Pass 3-Deep; Ch. 3 sectioning; Scaffolding v0.4; the formal specification).
Assigns: `SOL-01`–`SOL-09`. Leaves `BP-` numbers as ⟦placeholders⟧ for R3 and `PF-` numbers for R4.
Governance: namespaced provisional per the P-thread rule; canonical counts and names per the Terminology Freeze (seventeen standalone options O1–O17 across five implementation families A–E, plus the Family F composite O18; six families; LFDT; QBFT; `IMinimalSSI`; Set A/B/C; Tier 1/2/3; W).

---

## 1. Reading the map

Three rules were applied to every row.

1. **Layer of residence, not layer of use.** An artefact is placed where its *mechanism* lives, even if its purpose is higher. ECDSA is L1 although it is used to prove identity (L6); AnonCreds is L6 although it depends on L1 pairings and L2 accumulators.
2. **"Enables above" is a claim; "secured by below" is a dependency.** The two columns are deliberately asymmetric: the first says what would break *above* if the item failed; the second names what the item *assumes* from beneath. R3's breaking points will be derived by walking the second column downward.
3. **One tag per mechanism.** Where the corpus names one thing under several labels (Indy-Besu = E2 = O11; ERC-8004 = O7 (v1.1) = O9 (canonical)), the canonical label is used and the alias is noted once.

Colour/ID key for layers: L0 substrate · L1 crypto · L2 authenticated structures · L3 agreement · L4 economics/governance · L5 ledger semantics · L6 identity · L7 application/I2I.

---

## 2. The programme's solutions, tagged (SOL-01 … SOL-09)

These are the things the programme has *built, specified, or derived* — as opposed to evaluated. Each gets one paragraph: what it is, which layers it lives on, and which breaking points it is expected to address (numbers left to R3).

**SOL-01 · Local native sandbox (`cvin-sandbox-v1.1`).** Hardhat + Foundry harness with a single-validator Besu QBFT node, Solidity 0.8.24, offline-pinned; `ISetA.sol` / `ISetB.sol` / `ISetC.sol` abstract interfaces; evidence as committed immutable JSONL traces (F1–F12); G-B's arms discipline (cold/first-write vs warm/rewrite, dispersion = 0 expected, exact-integer gas with N). Layers: L3–L6 (a whole stack in one process). Role: the **baseline** — it measures execution cost and interface coverage with consensus cost removed (G-B §1.4: on one validator the consensus round costs nothing). Addresses: ⟦BP-L5 execution-cost, BP-L6 coverage⟧ as *measurement*, not as *defence*; it addresses no L0/L3/L4 breaking point and R3 must say so.

**SOL-02 · Consortium Besu QBFT (HAA-1 settlement Option A).** The deployment form of the sandbox lineage: a governance-diverse validator set, deterministic finality at quorum (≈ block period), free-gas → capacity constraint (M-T2), no public mempool. Layers: L3, L4 (governance replaces cost), L5. Role: the thesis's default Plane-A substrate. Addresses: ⟦BP-L3 finality/reorg, BP-L4 fee-market failure, BP-L0 mempool metadata⟧; accepts as residual ⟦BP-L4 validator collusion⟧ (the correlated validator–issuer row in G-C1).

**SOL-03 · Public anchoring in commitment form with checkpointing.** Plane A writes its own state root to a public chain per interval ("anchoring the anchor", P3 §2.3); per-credential anchors are Pedersen or salted-hash commitments (T-I15), never content hashes — the EDPB v2.0 ¶52–54 posture (P4 KD-P1). Layers: L2 (commitment, Merkle root), L5 (the public chain as ordering oracle). Role: converts consortium finality into publicly auditable non-equivocation at negligible cost (one A2-rung tx per interval, WO-P4). Addresses: ⟦BP-L4 validator collusion — detectability, not prevention; BP-L6 issuer equivocation; BP-L2 private-chain history rewrite⟧.

**SOL-04 · Public L2 / L1 settlement (HAA-1 Options B and C).** Same semantics as SOL-02 with different constants: L2 rollup (soft-second inclusion, L1-hard at batch finality, sub-cent cost, public mempool → relay path) or L1 direct (probabilistic → economic finality, the C16 variance finding). Layers: L3–L5. Role: the **upper bound** on trust base and the reference against which SOL-02's residuals are priced. Sidetree/ION (T-I19) is the deployed precedent. Addresses: ⟦BP-L4 collusion⟧ maximally; introduces ⟦BP-L0 mempool metadata, BP-L4 fee variance, BP-L3 sequencer admissibility (SR-16)⟧.

**SOL-05 · HAA-1, the hybrid anchored architecture.** Four planes — A (anchor/settlement), V (verification/status service), D (data-availability/archive), and the wallet/holder plane — with the three motions (write, read, revoke) and the checkpoint arrow; realises the Family E "four-way separation" (public anchoring · public status · private content · provable claims) with the corrections the Session A canon applied. Layers: spans L2–L7. Role: the programme's *design contribution at the architecture level*; it composes SOL-02 (or -04) + SOL-03 + SOL-06 + SOL-09 + Paladin-style private groups. Addresses: the union of the above plus ⟦BP-L6 revocation-latency window W, BP-L7 Tier-2 latency⟧ via the read-path completeness rule (real-time checks against σ-bounded cached state; on-chain presentation anchor is a Tier-3 audit artefact).

**SOL-06 · `IMinimalSSI` — the twelve-function interface.** Set A (eight DID/key functions), Set B (all twelve, adding `issueCredential`, `verifyCredential`, `revokeCredential`, `createPresentation`), Set C (agent extension, `ISetC.sol`, scope pending). Derived from the W3C data model (T-I17) by the operation-universe / M-1 elimination trace (Pass 3-Deep). Layers: L6 (its registry face is Plane A's interface). Role: the *specification contribution*; the comparison ruler for O1–O17. Addresses: no breaking point directly — it is the thing breaking points are measured against; but its minimality argument (G-A1) is itself a ⟦BP-L6 coverage-completeness⟧ claim R4 should bound.

**SOL-07 · The LFDT stack as adopted (Family E composition).** Indy (O10) or Indy-Besu (O11) as registry; AnonCreds (O12) for credentials; DIDComm v2 (O16) for the channel; ACA-Py / Credo-TS (O17) as agents; Paladin (O15) as the EVM privacy overlay. Layers: L3–L7. Role: the *convergence evidence* (C11) — that LFDT and the ERC ecosystem independently arrived at the same registry/credential separation — and the only source of a native `createPresentation`. Addresses: ⟦BP-L6 selective-disclosure, BP-L6 unlinkability, BP-L7 channel⟧; accepts ⟦BP-L1 pairing-assumption strength, BP-L2 accumulator witness distribution⟧.

**SOL-08 · Family F composite (O18).** The Stage 3 synthesis: minimum-cost composite achieving full `IMinimalSSI` compliance from the best-validated components of A–E. Derived, not measured; never counted among the seventeen evaluated options. Layers: L5–L7. Role: the *design contribution at the option level*. Addresses: ⟦BP-L6 createPresentation gap X2⟧ by composition (E2 + E6 + O12 pattern).

**SOL-09 · Revocation profiles SL and AC.** Profile SL: bitstring status list served from Plane V, root anchored on Plane A each epoch, herd privacy from list size ≥ 131,072, `ttl` set from the W budget. Profile AC: accumulator value on Plane A, witnesses on Plane D/V, holder carries a non-revocation proof (offline-friendly). Layers: L2 (list/accumulator), L6 (`revokeCredential`). Role: the two engineerable forms of the revocation-latency window; the interface is agnostic between them. Addresses: ⟦BP-L6 revocation latency, BP-L6 revocation-check linkability⟧; the choice is priced by WO-P3.

*Not tagged as SOL-:* the security campaign's adversary set A1–A6 and the SR- register (they are *threat* artefacts, consumed by R3's BP- derivation); the Stage 16 CAV scenario and Pass 4 grounding (they are *context*); the empirical protocol G-B (it is *method*).

---

## 3. The integration table

Columns: **Item** · **Layer(s)** · **Enables above** (what breaks upward if it fails) · **Secured by below** (what it assumes) · **Corpus source** · **Tags**.

### 3.1 Root primitives — cash lineage (T-01 … T-24)

| Item | Layer | Enables above | Secured by below | Corpus source | Tags |
|---|---|---|---|---|---|
| TCP/IP, best-effort transport | L0 | every message and block reaches peers | physical network; nothing cryptographic | R1 §1 | T-01 |
| P2P overlays: gossip, DHT, tit-for-tat | L0 | open membership, propagation, bootstrap | none — must be assumed hostile | R1 §1 | T-02 |
| Sybil attack result | L0/L3 | (negative) forbids identity-count voting → forces L4 | — | R1 §1; G-C1 adversary model | T-03 |
| Public-key crypto, DH, RSA | L1 | ownership, key agreement, signatures | integer factoring / DLP hardness | R1 §2 | T-04 |
| GMR signature security definition | L1 | "only the holder can spend/sign" is a theorem | EUF-CMA assumption | R1 §2 | T-05 |
| ECC, ECDSA, secp256k1 | L1 | compact ownership proofs for every EVM option | ECDLP hardness; nonce entropy | R1 §2; every sandbox trace | T-06 |
| SHA-256, RIPEMD-160 | L1 | PoW, Merkle, tx IDs, addresses, commitments | pre/second-pre/collision resistance | R1 §2 | T-07 |
| Merkle trees | L2 | block commitment, SPV, status-list roots, state tries | T-07 collision resistance | R1 §3; Building Paths preface | T-08 |
| Haber–Stornetta linked timestamping | L2 | the chain's tamper-evidence; CT logs; anchoring | T-07 | R1 §3 | T-09 |
| Chain of blocks | L2 | ordered history | T-08 + T-09 + T-15 | R1 §3 | T-10 |
| Byzantine agreement, FLP | L3 | one history among faulty nodes | timing assumption (partial synchrony) | R1 §4; G-B §1.4 | T-11 |
| PBFT → QBFT / RBFT | L3 | deterministic finality in a known set | n ≥ 3f+1; identities known (rejects T-03) | R1 §4; Family E v2.0 E1/E2 finality comparison | T-12 |
| Nakamoto consensus | L3 | open-membership agreement | T-15 + honest majority of work | R1 §4 | T-13 |
| PoW as pricing; Hashcash | L4 | Sybil cost; leader lottery | T-07 preimage resistance | R1 §5 | T-14, T-15 |
| RPOW | L4/L5 | PoW as bearer token (concept) | one trusted server (its failure) | R1 §5 | T-16 |
| Incentive-compatible design | L4 | honest behaviour as best response | game-theoretic assumptions | R1 §5 | T-17 |
| Difficulty adjustment | L4 | stable cost function under varying participation | feedback control | R1 §5 | T-18 |
| eCash / blind signatures | L5 | payer anonymity (concept later reused by T-I13) | trusted bank (its failure) | R1 §6 | T-19 |
| Cypherpunk agenda | — (social) | the requirement set: privacy through crypto, not law | — | R1 §6 | T-20 |
| b-money, bit gold | L5 | shared ledger, PoW chain (concepts) | unresolved: conflict resolution / trusted registry | R1 §6 | T-21, T-22 |
| Centralised e-currencies (cautionary) | L5 | (negative) demand exists; central issuer is a legal SPOF | — | R1 §6 | T-23 |
| Double-spend problem | L5 | the requirement Bitcoin closes; generalises to *equivocation* at L6 | — | R1 §6 | T-24 |

### 3.2 Root primitives — identity lineage (T-I01 … T-I22)

| Item | Layer | Enables above | Secured by below | Corpus source | Tags |
|---|---|---|---|---|---|
| Needham–Schroeder / Kerberos | L6/L7 | the TTP ticket pattern SSI removes | symmetric keys; server secrecy | R1 §10.1 | T-I01 |
| X.509 PKI, CRL/OCSP, Certificate Transparency | L6 | key↔name binding; expiry; revocation; public issuance logs | T-04/T-05; CA honesty (its failure → CT via T-08/T-09) | R1 §10.1; Pass 4 (1609.2 lineage) | T-I02 |
| PGP web of trust | L6 | decentralised key binding (concept) | peer signatures; graph trust | R1 §10.1 | T-I03 |
| SSL/TLS → 1.3 | L7 | the reference I2I channel | T-I02 for identity; T-04 DH; AEAD | R1 §10.2 | T-I04 |
| IEEE 1609.2 / ETSI TS 102 941; ECQV implicit certs; butterfly keys / SCMS | L6 | Tier-1 authentication with rotating unlinkable pseudonyms, no ledger | T-06; PKI hierarchy (SCMS) | Pass 4 CAV grounding; Security campaign Pass 1 anchor material | T-I05 |
| OTR | L7 | deniability + forward secrecy (concept) | per-message DH | R1 §10.2 | T-I06 |
| Signal X3DH / Double Ratchet; MLS | L7 | asynchronous authenticated confidentiality; PCS | T-04 DH on curves; prekey authenticity (L6) | R1 §10.2 | T-I07 |
| Noise framework | L7 | analysable handshake between two static keys | T-04; pattern proofs | R1 §10.2 | T-I08 |
| JOSE / COSE | L7 | transport-independent signed/encrypted objects (VC-JWT, DIDComm envelope) | L1 only; adds no crypto | R1 §10.2 | T-I09 |
| ZKP: GMR, Fiat–Shamir, Schnorr ID | L1 | prove control/attributes without disclosure | random-oracle model (F-S); DLP | R1 §10.3; Stage 19 | T-I10 |
| Pairings: BLS, CL, BBS+ | L1 | signatures on committed attributes; unlinkable multi-show | q-SDH / LRSW (stronger than ECDLP) | R1 §10.3; Stage 19 (BBS+) | T-I11 |
| Accumulators | L2 | constant-size non-revocation proofs | strong-RSA / q-SDH; witness distribution | R1 §10.3; P3 Profile AC; G-C1 W decomposition | T-I12 |
| Anonymous credentials: Chaum, U-Prove, Idemix | L6 | unlinkable credential shows (concept + code, no registry) | T-I10/T-I11 | R1 §10.3; Family E O12 lineage | T-I13 |
| zk-SNARK Groth16; Bulletproofs | L1 | predicate proofs; on-chain verification | trusted setup (Groth16); pairing assumptions | U-17 re-argument; Paladin O15 | T-I14 |
| Pedersen / hash commitments | L1 | hiding anchors that satisfy EDPB ¶52–54 | DLP (Pedersen); T-07 (hash) | P2/P3; P4 KD-P1 | T-I15 |
| Namecoin; Zooko's triangle | L5/L6 | ledger-as-registry (concept); the trilemma's naming form | Bitcoin L0–L5 | R1 §10.4 | T-I16 |
| W3C DID Core, VC-DM | L6 | the data model `IMinimalSSI` is derived from; hybrid by construction | L1 signatures; a verifiable data registry (L5) | formal spec; Pass 3-Deep operation universe | T-I17 |
| DIDComm v2 | L7 | mutually authenticated encrypted messaging between DIDs; Set B protocols | T-I09 JWE; ECDH-1PU; DID resolution (L6) | Family E O16 | T-I18 |
| Sidetree / ION | L2/L6 | batched DID ops anchored by one hash on a public chain | T-08; public-chain ordering (L5) | P2 placement ladder; R1 §10.4 | T-I19 |
| AnonCreds | L6 | native `createPresentation`; predicate proofs; accumulator revocation | T-I11 CL; T-I12; registry (L5) | Family E O12; X2 crux | T-I20 |
| LFDT stack: Indy, Aries, Besu, AnonCreds, Paladin | L3–L7 | the deployed permissioned identity stack | RBFT/QBFT (T-12); T-I11/T-I12/T-I14 | Family E v2.0 | T-I21 |
| ERC-8004; A2A; MCP | L6/L7 | agent identity, reputation, validation; capability advertisement | ERC-721 (O3) base; L1 signatures | Family D O9; Stage 31 | T-I22 |

### 3.3 Evaluated options O1 – O17 and the composite O18

Statuses per the Accuracy Ledger (K-22): ERC-1056 Stagnant · ERC-725 Draft · ERC-735 never merged · ERC-6551 Review · ERC-4337 Final · EIP-7702 Final · ERC-8004 Draft. Aliases: O9 = O7 in Building Paths v1.1 (the only mapping the corpus states); O11 = E2; O12 = E3; O13 = E4; O10 = E1; O14 = E5; O15 = E6; O16 = E7; O17 = E8.

| Option | Family | Layer | Enables above | Secured by below | Corpus source | Tags |
|---|---|---|---|---|---|---|
| O1 ERC-1056 | A | L6 (registry face) | DID = account, zero-gas creation; attributes, delegates, owner change | T-06 ECDSA; EVM ordering (L5); SP-1 control | Narrative Synthesis §3.1; K-19 | T-I17 pattern; SOL-01 baseline |
| O2 ERC-1155 | A | L5/L6 | batch credential lower bound | token semantics; not SSI-structured | Family E v2.0 T3.2 | — |
| O3 ERC-721 soulbound | B | L5/L6 | identity-as-non-transferable-asset | token ownership (L5) | Narrative Synthesis | T-I22 base |
| O4 ERC-6551 TBA | B | L6 | asset-with-wallet; deterministic counterfactual account | O3; CREATE2 determinism (L5) | Accuracy Ledger | — |
| O5 ERC-725 | C | L6 | key-value identity store + execute | ownership; EVM storage | Pass 3-Deep §4 | — |
| O6 ERC-725xy + unmerged ERC-735 | C | L6 | claims layer (store-only); SP-2 composite | O5; ERC-735 status caveat (K-20) | Sandbox methodology T-735 series | SOL-08 input |
| O7 ERC-4337 | C | L5/L6 | programmable validation; social recovery; 63.25 M accounts (K-21) | EntryPoint contract; bundler liveness (L0/L3) | Accuracy Ledger; Stage 31 | — |
| O8 EIP-7702 | C | L5 | EOA → smart-account bridge (Pectra, 7 May 2025) | protocol upgrade | Accuracy Ledger | — |
| O9 ERC-8004 | D | L6/L7 | Identity, Reputation, Validation registries for agents (names per ledger correction) | O3; L1 signatures | Accuracy Ledger; Stage 31 | T-I22; Set C target |
| O10 Indy (E1) | E | L3–L6 | purpose-built identity ledger; NYM/ATTRIB/SCHEMA/CRED_DEF/REVOC_REG | RBFT (T-12); steward governance (L4) | Family E v2.0 | T-I21; SOL-07 |
| O11 Indy-Besu (E2) | E | L3–L6 | the same registry as Solidity on Besu QBFT; on-chain validator signing history | QBFT (T-12) | Family E v2.0 | T-I21; SOL-02/07 |
| O12 AnonCreds (E3) | E | L6 | 12/12 Set B; native `createPresentation` (X2) | T-I11 CL; T-I12 accumulator; anoncreds-rs via FFI | Family E v2.0; Pass 3-Deep | T-I20; SOL-07/08 |
| O13 Identus (E4) | E | L6/L7 | national-deployment platform (API coverage mode) | Cardano / Prism anchoring | Family E v2.0 | — |
| O14 CREDEBL (E5) | E | L6/L7 | platform (API coverage mode) | — | Family E v2.0 | — |
| O15 Paladin (E6) | E | L1/L5 overlay | private tx groups (privacy marker hash on-chain); on-chain Groth16 verifier; Pedersen confidential ERC-20 | Besu; T-I14; T-I15 | Family E v2.0 | SOL-05 privacy plane |
| O16 DIDComm v2 (E7) | E | L7 | the channel and the Set B protocols | T-I09; T-I18 | Family E v2.0 | T-I18; SOL-07 |
| O17 ACA-Py / Credo-TS (E8) | E | L6/L7 (agent) | full-stack reachability of all twelve functions | O16; O12; a registry | Family E v2.0 | SOL-07 |
| O18 Family F composite | F | L5–L7 | full `IMinimalSSI` at minimum cost (derived) | its components | Terminology Freeze §8.3 | SOL-08 |

### 3.4 Corpus artefacts (every project file), placed

| Corpus artefact | Layer(s) it speaks to | What it contributes to the map | Tags it defines or consumes |
|---|---|---|---|
| SSI-Minimal-Function-Specification-Formal.md | L6 | the twelve functions; on-chain hash / off-chain content stipulation | SOL-06 |
| METHODOLOGY.md; CVIN Native Sandbox Build & Verification Methodology v1.0 | L3–L6 | the sandbox, gates G0–G6, SP-1/SP-2, T-725/735/740 series | SOL-01 |
| CVIN_Building_Paths_v1-1_SixLevel | L2–L6 | the preface on finality, hash-on-chain, audit trail; the superseded 8-option numbering | consumes T-08, T-12, T-13; alias note O7→O9 |
| CVIN_Family_E_Expansion v1.0 / v2.0 | L3–L7 | Family E sub-layers; E1/E2 finality comparison; archival differential; Paladin four-way separation | T-I20/T-I21; SOL-07 |
| CVIN_SC_Thesis_Narrative_Synthesis v11.3; Content Registry v11.3 / v12.0 | all | the thesis's own ordering of these ideas; the option count drift (frozen since) | — |
| CVIN_Content_Block_Registry_v1 | admin | superseded block registry (K-11 error origin) | — |
| CVIN_SC_Deliverable_Suite_Architecture v1.0 | admin | S1/S2/S3 support-document forms; the security campaign's four passes | the S3 five-part form R5 will use |
| RelatedWork Audit v2; RelatedWork Audit Execution G-D1 | — (literature) | positioning; the "only option that…" scoping rule | — |
| Consolidation Audit Manual v1.0; Consolidation Audit & Production Manual v2.0 | admin | K-corrections; production process | — |
| Minimality Argument Hardening G-A1; Coverage Argument Checkability G-A2 | L6 | minimality and coverage arguments for SOL-06 | SOL-06 |
| Gap Taxonomy; Academic Rigour Dossier; Crux Defence Compendium X1–X6 | L6 (mainly) | the six cruxes; X2 = createPresentation gap; X4 = tier budgets; X5 = accuracy | consumed by R3 Part I |
| Empirical Rigour Protocol G-B | L3–L5 | measurands, arms, clock boundaries M-L1…; determinism rule | R4 §3 inputs |
| Security & Privacy Campaign G-C1 | L0–L7 | adversaries A1–A6; W decomposition; SR- register; mempool metadata; read-path completeness | R3 Part II threat source |
| Agentic I2I Validation G-E1 | L6/L7 | the agent extension (Set C) and the I2I framing | T-I22 |
| Accuracy Ledger & Terminology Freeze G-D2-D3-H2; S1 Reference Index & Accuracy Ledger | admin | EA-/K- corrections; frozen names and counts | governs every row above |
| Thesis Production & Institutional Process G-F-G | admin | UBC process | — |
| Chapter 1–5 Sectioning; Security Thread & Front/Back Matter Sectioning | all | where each layer lands in the thesis; the notation list (W, adversaries, risk IDs) | R4 must not collide with §10.2 notation |
| Suite Guide & Reading Map; Master Writing Plan; Master Execution Plan; Scaffolding v0.1–v0.4; Status Board 2026-08-18; Version Control Log; Harvest Kit; 14-Day Sprint Plan | admin | governance and sequencing | — |
| Pass 2 Verification Dossier; Pass 3 Deep Verification & CEV Ledger; Pass 3-Deep Operation Universe & M-1 Trace; Pass 1–4 Meta-Commentary Log; Manual v2.0 Pass 1 Meta-Log; Session A Reconciliation Record | L6 + admin | the CEV format; the operation universe; the X2 grounding at source | R4 CEV-R rows follow this format |
| Pass 4 CAV / IoV Vehicular Domain Grounding | L0, L6, L7 | 1609.2 / SCMS incumbent; tiers; radio substrate | T-I05 |
| On/Off-Chain Placement suite P1–P4 (G-P1) | L2–L7 | placement morphology; cost ladder; HAA-1; settlement spectrum; EDPB posture; MC-P lessons | SOL-02/03/04/05/09 |
| Thesis Ch. 2 §2.3 Derivation DRAFT | L6 | prose derivation of the interface | SOL-06 |
| Technical Memo 2; Memo A; Memo B (PDFs) | context | Type C sources for codebase facts and timeline only (framing superseded, F-3) | — |

---

## 4. Gaps in the map

### 4.1 Primitives with no corpus artefact (R3/R4 will have to source them fresh)

| Primitive | Why it matters to the thesis | Suggested landing |
|---|---|---|
| T-I07 Signal / MLS; T-I08 Noise | the I2I channel is asserted (DIDComm) but its cryptographic pedigree is never stated; needed for the L7 breaking points | R3 Part II L7; one paragraph in Ch. 2 background |
| T-I06 OTR deniability vs non-repudiation | the audit argument (Building Paths preface) silently assumes non-repudiation; V2X privacy sometimes wants the opposite | R3 Part I requirement table |
| T-03 Sybil as applied to the *validator set* | G-C1 has validator collusion but not the Sybil framing that explains why permissioned = identity-based | R3 Part II L3/L4 |
| T-18 difficulty adjustment ↔ M-T2 capacity constraint | free-gas QBFT has no L4 cost function; the analogue is capacity governance and it is unnamed | R3 Part III; R4 §3 |
| T-I02 Certificate Transparency | the closest deployed precedent for public anchoring of identity state; not cited anywhere | R3 Part III SOL-03; Related Work |
| T-I16 Zooko's triangle | the naming-system form of the trilemma; useful framing for the DID-method choice | R3 Part III |
| Key-generation entropy and address-space bounds | no document states the collision probabilities for n vehicles × keys × rotations | R4 §1 (PF-01…04) — the reason R4 exists |
| Post-quantum status of every L1 primitive in use | the ledger has EA-05 "not post-quantum" for one item; no layer-wide statement | R3 Part II L1; R4 §2 |

### 4.2 Corpus artefacts with no root primitive named

| Artefact / claim | The unstated dependency | Fix |
|---|---|---|
| "Hash-on-chain as an integrity mechanism" (Building Paths preface) | rests on T-07 second-preimage + T-09; and, post-EDPB, must be commitment-form (T-I15) | cite T-07/T-09/T-I15 in Ch. 2 |
| "QBFT immediate finality" (G-B §1.4; Family E) | rests on T-12 with n ≥ 3f+1 and partial synchrony (T-11 FLP escape) | state the assumption once; R4 PF- for f-of-N |
| "Forensic reconstruction possible" (R-R3 archival guarantee) | rests on L2 append-only + an availability owner (Plane D) — availability is not a cryptographic property | R3 BP-L2/L0 availability row |
| The W decomposition (`t_include, t_finalise, t_propagate, t_cache, t_poll`) | `t_propagate` is an L0 gossip property; never tied to T-02 | R4 §2 revocation bound |
| Herd privacy from list size ≥ 131,072 | rests on an anonymity-set argument (k-anonymity); primitive unnamed | R4 SYM-/PF- for anonymity set |
| "Only AnonCreds achieves 12/12" | rests on T-I11 pairing assumptions — a *stronger* assumption than the EVM options' ECDLP; the ranking should carry the assumption class | R3 Part II L1; R4 §4 sensitivity |

### 4.3 Terminology to watch (potential collisions for R4's SYM- table)

`W` is thesis notation (revocation-latency window; G-C1 §2.7) — R4 must reuse it, not redefine. `A1–A6` are adversary identifiers in G-C1 and *also* the settlement-option letters A/B/C in P3 and the plane letters A/V/D — R4 should avoid bare single capitals for its own symbols. `f` is the BFT faulty-node count in T-12 and also the F/P/✕ verdict letter; use `f_B` for the former. `N` is sample size in G-B and validator count in QBFT; use `N_v` for validators. `σ` is the cache-staleness bound in HAA-1; keep it.

---

## 5. What R3 should take from this document, in one paragraph

Write Part I against §3.2's "enables above" column and R1 §10.5's requirement table; derive Part II's breaking points by walking each item's "secured by below" entry to its failure; place SOL-01…SOL-09 on the trilemma in Part III using §2's "addresses / accepts" lists; and make the three Part IV flows trace through O11/O12/O16 (the HAA-1 default) with O1 as the EVM-baseline counter-trace. Every "X is secured by Y" sentence already has its tag pair in the tables above.

---

## HANDOFF (paste at the top of Prompt 2)

**Thread:** G-R1 (provisional), Prompt 1 complete, 2026-09-15.
**Files issued:** `claude_CVIN_SC_Roots_Lineage_R1_v1-1.md` (supersedes `Bitcoin_Technology_Lineage_Report_v1-0.md`; L0–L5 unchanged, §§10–12 new); `claude_CVIN_SC_Roots_Lineage_R1_v1-1.svg` (eight layers, two timelines, convergence panel, SOL strip); `claude_CVIN_SC_Roots_Integration_Scan_R2_v0-1.md` (this document).
**Tag ranges consumed:** `T-01`–`T-24` (frozen from v1.0); `T-I01`–`T-I22`; `SOL-01`–`SOL-09`. `BP-` and `PF-` untouched. Layers `L0`–`L7` fixed.
**SOL- list:** 01 local sandbox (baseline, consensus cost removed) · 02 consortium Besu QBFT (Option A) · 03 public anchoring in commitment form + checkpoint · 04 public L2/L1 (Options B/C, upper bound) · 05 HAA-1 hybrid (four planes; composes 02+03+06+09+Paladin) · 06 `IMinimalSSI` Set A/B/C · 07 LFDT stack as adopted (O10/11, O12, O16, O17, O15) · 08 Family F composite O18 · 09 revocation profiles SL / AC.
**Five load-bearing decisions:** (1) layer of *residence* not *use* — ECDSA is L1, AnonCreds is L6; (2) L5 renamed "ledger semantics" so it generalises from cash to state; (3) T-I05 (1609.2/SCMS) is placed as the L6 *incumbent* the ledger must not degrade, not as an option; (4) SOL-01 is a measurement instrument, not a defence — R3 must not credit it with closing any L0/L3/L4 breaking point; (5) the AnonCreds 12/12 ranking carries a stronger assumption class (q-SDH/LRSW) than the EVM options (ECDLP) — R3 states it, R4 bounds it.
**Symbol collisions to avoid in R4:** reuse thesis `W`, `σ`; avoid bare `A`, `f`, `N`; use `f_B`, `N_v`.
**Open Q-R#:** Q-R1 — should T-I05's SCMS butterfly-key unlinkability be treated as a *requirement* the ledger design must match at Tier 1, or as out of scope (ledger out of scope at Tier 1 per X4)? Q-R2 — does Set C's scope (`ISetC.sol`) exist in the codebase yet, so R3 can name its functions, or must R3 leave Set C as a placeholder? Q-R3 — is Certificate Transparency to be added to the Related Work as the anchoring precedent (it is absent from the audit)?
**Corrections:** none logged this pass (KD-R none). One observation for the Accuracy Ledger: R1 v1.0 §7 states ERC-8004 "mainnet January 29 2026" per Family E v2.0; the S1 ledger phrases this as "reference contracts deployed" and warns against "standard finalised" — R3 should use the ledger's wording.
