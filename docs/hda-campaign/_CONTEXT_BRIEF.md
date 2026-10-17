# CONTEXT BRIEF — CVIN-SC Hybrid Data Architecture (HDA) Campaign, Suite v1.0

*Internal working brief for every author (human or agent) writing a document in this suite. Read completely before writing. Everything here was verified at source from the programme's own files on 2026-09-03 unless marked DIGEST-LEVEL or UNVERIFIED.*

---

## 0. What this campaign is

The CVIN-SC MASc thesis (Nikhil Prakash, UBC ECE; supervisors Dr. Chen Feng, Blockchain@UBC, and Dr. David G. Michelson) evaluates blockchain-based Self-Sovereign Identity (SSI) for connected and autonomous vehicles (CAVs) and, by generalisation, AI agents. This campaign produces the **general first pass** on the single largest design axis the thesis has not yet written up as a unified argument: **where identity data lives and how it is proven** — on-chain vs off-chain, anchoring, read vs write paths, zero-knowledge proofs (ZKP), verifiable data integrity, and cost — and the design of a "best of both worlds" hybrid that is scalable, realisable, cost-effective, secure, integrity-preserving, and private where required. Later passes will attack each angle separately; this pass must give depth, coverage, and cleverness across all of them, plus a way to test, build, or at minimum demonstrate every claim.

Alongside the analysis, this pass builds (in code, in the same repository) a minimal Vehicle Identity (VID) layer on the canonical sandbox: a minimal VID, a minimal driver's licence credential, a minimal vehicle registration ("car ID") credential, then the full MOBI VID II lifecycle set, all with an explicit **endorsement** pattern. Documents may reference that build by the names in §7; they must NOT invent measurements from it (see §9 rules).

## 1. Suite structure and title block (mandatory)

The programme's *Deliverable Suite Architecture v1.0* convention applies. The suite is:

| # | File | Slot | Content |
|---|---|---|---|
| 00 | `00_HDA_Master_Plan_and_Attack.md` | P | Plan of attack, suite map, thesis-integration map, build/test/demonstration plan, decisions owed |
| 01 | `01_On_Off_Chain_Data_Architecture_and_Anchoring.md` | P (core) | The data-placement analysis: on/off-chain, anchoring, read/write paths, integrity, costs, per-function and per-object |
| 02 | `02_ZKP_and_Verifiable_Data.md` | P | Zero-knowledge proofs, selective disclosure, verifiable data integrity, revocation privacy, costs, CAV + agent application |
| 03 | `03_Best_of_Both_Worlds_Hybrid_Design.md` | P | The synthesis design: tiered data placement, anchor/cache/attest pattern, degraded modes, security/privacy/integrity envelope, realisability and cost |
| 04 | `04_Scenarios_Full_Coverage_CAV_and_Agent.md` | P | Two end-to-end scenarios (one CAV, one AI agent) exercising every function (F1–F12, Set C) and every object of the identity system |
| 05 | `05_Scenarios_Latency_Tiers.md` | P | One CAV and one agent scenario per latency tier (three tiers) with data-placement consequences |
| 06 | `06_Scenarios_Reputation_Payment_GatedAccess_LowConnectivity.md` | P | CAV + agent scenario pairs for reputation, payment, gated access, and low-connectivity (read-only / delayed-write) |
| 07 | `07_Scenarios_Beyond_CAV_Backend_Systems.md` | P | Driver's licences, property deeds, repair history, other back-end registries; CAV + agent pairs; integration with legacy systems |
| 08 | `08_I2I_Secure_Communication_and_Cruxes.md` | P | Identity-to-Identity secure channel design, the cruxes (revocation propagation, key agreement, replay, offline), CAV + agent pairs |
| 09 | `09_Reputation_Identity_and_Federated_Learning.md` | P | Why federated ML (and similar collective computation) needs reputation, why reputation needs identity, why identity needs this system; road/traffic reporting, tolling, pay-per-use |
| 10 | `10_VID_Build_Documentation.md` | P | What was built in this pass, how, test results, traces (written from the real build only) |
| 11 | `11_Thesis_Integration_and_Academic_Argument.md` | P | The narrative and academic argument that folds this campaign into the thesis chapters, including the endorsement argument |
| S1 | `S1_Weighted_Reference_Index.md` | S1 | Every source, weighted, with verification state (R-series, continuing programme numbering; see §10) |
| S2 | `S2_Registry_Delta.md` | S2 | New/changed content blocks for the Content Block Registry (delta against v11.3) |
| S3 | `S3_Change_Log_and_Meta_Commentary.md` | S3 | Version log entry, methodology notes, K-ledger, unresolved items, five-part meta commentary with load-bearing questions |
| 99 | `99_Chat_Primers_for_Angle_Passes.md` | C | Paste-ready primers for the per-angle passes in the chat model |

**Title block (copy verbatim, fill the brackets):**

```
CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**[Document title]**

**[Subtitle stating this document's specific function]**

Document [N] of 16 · Hybrid Data Architecture (HDA) Campaign · [Primary deliverable | Support document | Companion] · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: [Type A prose / Type B tables-data / Type C framing] → Chapter [n], §[n.n]*
```

Every primary document ends with three mandatory closing sections: **"Sources used in this document"** (a table: R# or NEW-n, source, verification state VERIFIED AT SOURCE / DIGEST-LEVEL / UNVERIFIED, how used), **"Registry delta rows"** (the content blocks this document creates, in the S2 row schema: Content Block · T · Source · Ch. · Ready % · Notes), and **"Open questions for the researcher"** (each one load-bearing: something only the researcher can decide).

## 2. The thesis, in the words it already uses

**Title:** *Towards a Minimal Function Specification for Blockchain-Based Self-Sovereign Identity in Connected and Autonomous Systems.* Five chapters: 1 Introduction (SCMS accountability gap; CVIN lineage; extension-not-replacement) · 2 Background and Methodology (Allen's ten SSI principles; W3C DID Core 1.0 and VC Data Model; the twelve-function IMinimalSSI derivation by necessity/sufficiency/orthogonality; Set A/B decomposition; three-tier latency framework) · 3 Standards Inventory (six families, fourteen to nineteen options; the createPresentation gap) · 4 Evaluation and Results (compliance, gas, CAV scenario analysis, real-world concerns, latency, ZKP) · 5 Discussion (createPresentation as structural insight; I2I generalisation to agents; LFDT convergence; Family F composite; limitations).

**Contributions C1–C15** (use these numbers when saying where a claim lands): C1 derivation methodology · C2 IMinimalSSI interface · C3 Set A/Set B decomposition · C4 MOBI VID conformance mapping · C5 abstract compliance suite · C6 three-tier CAV latency framework · C7 identity standard inventory · C8–C9 compliance results and gas benchmarks · C10 ZKP and selective-disclosure analysis · C11 LFDT convergence validation (Indy-on-Besu) · C12–C13 intersectional benchmark and minimum-cost composite (Family F) · C14 I2I agent identity wrapper (ERC-4337 + ERC-7579, A2A/MCP) · C15 I2I bridging paper.

**Foundational framing sentences already in the draft (reuse, do not contradict):**
- SCMS (IEEE 1609.2) governs Tier 1 BSM authentication; SSI *extends* it for Tier 2/3. "Extension, not replacement" of both SCMS and of the 2020 CVIN architecture.
- The accountability gap: SCMS pseudonymity precludes answering "what is the history of actions taken by vehicle V?"; a blockchain-anchored DID gives a permanent, tamper-evident key-material history while ZKP presentations keep routine disclosure minimal.
- The three-tier latency framework: **Tier 1 <100 ms** (BSM/collision avoidance — DLT explicitly out of scope), **Tier 2 100–500 ms** (cooperative operations: charging session initiation, toll authorisation, parking credential exchange, V2I service registration, cooperative manoeuvre negotiation — the primary DLT target, viable if edge-deployed), **Tier 3 >500 ms** (administrative: registration, type approval, operator licence, fleet management, insurance, history — any DLT profile). The 2020 paper's original wording of the tiers: low latency = collision avoidance, basic safety messages, advanced navigation; medium = tolling, parking, smart EV charging, gated/restricted area access; high = legal, finance, insurance, immutable vehicle history, driving data for neural-network and autonomous-driving training.
- The central empirical finding: **no EVM standard natively implements createPresentation (F8)**; EVM optimises identity anchoring (Set A) and defers selective disclosure to off-chain middleware; LFDT/AnonCreds implements native ZKP presentations off-chain and anchors only credential definitions and revocation accumulators. AnonCreds is the Set B coverage ceiling (12/12). In the sandbox, F8 is *declared and anchor-implemented* (challenge-bound, replay-protected); the finding is about *native* support.
- The 2020 CVIN paper's other signature concepts that must stay testable: **dual identity modes** (public/pairwise DIDs; pseudonymous stream vs verinym for commercial transactions), **Local CVINs derived from a Global CVIN via ID Porting Protocols (IDPPs)** for jurisdiction-specific policy and smaller shards to reduce lookup latency, **distributed oracles** (Chainlink-style) to link off-chain real-world data to a CVIN ID / digital twin without a central authority, **RSUs as edge servers**, **MEC/5G-aware consensus** and **sidechains anchored to a backbone chain** (most transactions in the sidechain, few on-chain), and the wireless constraints: scarce compute, variable traffic load, unreliable links, intermittent coverage.
- Supervisor memos (Memo A/B, Technical Memo 2) fix the architectural stance: DIDs as cryptographic roots; VCs as portable attestations; **on-chain registries for discovery and revocation; content and logs off-chain with on-chain integrity anchors where appropriate**; explicit governance (issuer roles, **endorser sets**, key rotation); ZKP for selective disclosure and unlinkability, verification on-chain when needed or off-chain with auditable anchoring; agents hold keys, present VCs, produce ZK proofs, sign actions, leave signed execution traces; optional reputation (issuer quality, third-party endorsements, observed behaviour; Sybil/collusion handled by issuer weighting, participation costs, anomaly screens); AEAD channels with forward secrecy; **off-chain verification avoids block-time delays; only lifecycle events and anchors on-chain; cache invalidation synchronised with revocation state**; revocation models = status lists (simpler proofs) vs accumulators (holder privacy) with measured revocation latency, staleness windows, verification cost; threat model = impersonation, replay/equivocation, key compromise, Sybil/collusion, credential theft/mis-issuance, supply-chain compromise, plus chain faults (reorgs, rollbacks, partitions, delayed finality); A2A phases = discovery → handshake → session policy → interaction logging → revocation/dispute signalling; EVM-first, ERC-725/735/740-inspired, L2/zkEVM-extensible, adapters for non-EVM; storage IPFS/Arweave or enterprise depending on regulation; benchmark axes = security/privacy, performance, reputation dynamics, robustness, auditability.
- The Building Paths preface establishes three framework properties every option instantiates differently: **block finality as (probabilistic or deterministic) immutability**, **hash-on-chain as integrity without disclosure** (with the GDPR nuance that per-credential content hashes may themselves be personal data, whereas credential-definition hashes and accumulators are safely public), and **the forensic audit trail as an accountability primitive** ("not that blockchain prevents attacks, but that it makes attacks permanently visible and attributable"; for agents, operational transparency rather than algorithmic transparency).

## 3. The specification (normative; never alter)

Twelve functions, three sets. Interface `IMinimalSSI.sol` (Solidity ^0.8.20; sandbox compiles at 0.8.24, optimizer 200 runs, evm paris).

| F | Function | Set | Signature (abridged) | W3C basis |
|---|---|---|---|---|
| F1 | createDID | A | `createDID(address controller) → bytes32 did` | DID Core §7.1 |
| F2 | resolveDID | A | `resolveDID(bytes32) view → (bytes document, bytes metadata)`; empty bytes for unknown, never reverts | DID Resolution |
| F3 | updateDID | A | `updateDID(bytes32 did, bytes32 key, bytes value, uint256 validity)` | DID Core §7.2 |
| F4 | deactivateDID | A | irreversible; DID stays resolvable with flag | DID Core §7.3 |
| F5 | issueCredential | B | `issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil) → bytes32 credentialId` — **content off-chain, only the hash on-chain** | VC DM §4 |
| F6 | verifyCredential | B | `view → (bool valid, bytes32 issuer, bool revoked, bool expired)`; checks existence, revocation, expiry, issuer deactivation; never reverts | VC DM §5 |
| F7 | revokeCredential | B | issuer-only, idempotent, irreversible | BitstringStatusList |
| F8 | createPresentation | B | `createPresentation(bytes32 holder, bytes32[] credentialIds, bytes32 challenge, string domain) → bytes32 presentationId`; verifies holder ownership; challenge replay prevention | VC DM §6 |
| F9 | addVerificationMethod | A | `(bytes32 did, bytes32 keyType, bytes publicKey) → bytes32 keyId` | DID Core §5.2 |
| F10 | removeVerificationMethod | A | must never remove the last key | DID Core §5.2 |
| F11 | addDelegate | A | `(bytes32 did, bytes32 delegateType, address delegate, uint256 validity)`; types sigAuth, veriKey | did:ethr |
| F12 | validDelegate | A | `view → bool`; false on expiry/absence, never reverts | did:ethr |

Errors: NotAuthorized, DIDNotFound, DIDAlreadyDeactivated, CredentialNotFound, CredentialRevoked, CredentialExpired, InvalidCredential. Events on every state change (DIDCreated, DIDUpdated, DIDDeactivated, CredentialIssued, CredentialRevokedEvent [renamed from the spec's colliding `CredentialRevoked`; spec erratum for v1.1], PresentationCreated, VerificationMethodAdded/Removed, DelegateAdded).

**Set C (ISetC, optional, ERC-8004-derived agent trust):** `attestReputation(did, uint8 score, string evidenceURI)`, `getReputation(did) → (meanScore, attestationCount)`, `requestValidation(did, validationType, payload) → requestId`, `validationStatus(requestId) → status`.

**Extended functions named by the spec §6 (not required for compliance; this campaign uses the Governance ones):** batch ops; recovery (recoverDID, addRecoveryKey); privacy (createSelectivePresentation, verifyZKProof); **governance (registerIssuer, endorseIssuer, proposeChange)**; discovery (searchByAttribute, getServiceEndpoints). Extended functions must not violate the minimal interface's constraints.

**Spec gas targets (hypotheses, not results):** ERC-1056 / ERC-725: createDID <100K / <600K; resolveDID <10K / <20K; updateDID <80K / <100K; deactivateDID <50K / <60K; issueCredential <120K / <150K; verifyCredential <10K / <15K; revokeCredential <50K / <60K; createPresentation <150K / <200K; addVerificationMethod <100K / <120K; removeVerificationMethod <50K / <60K; addDelegate <60K / <70K; validDelegate <5K / <10K.

## 4. Families, options, and evidence state

Six families, governing structure from the v2-0 Implementation Plan: A Lightweight (ERC-1056, ERC-1155) · B Token-as-identity (ERC-721 lineage, ERC-6551) · C Contract account/claims (ERC-725, ERC-725xy/ERC-735, ERC-4337, EIP-7702) · D Agent/registry (ERC-8004; mainnet 29 Jan 2026) · E Purpose-built SSI (E1 Indy-on-Besu, E2 Identus, E3 AnonCreds, plus CREDEBL, Paladin, DIDComm v2, ACA-Py/Credo-TS in the expanded set) · **F CVIN Combined = Stage 3 synthesis output only; never built as a Stage 1 sandbox — hard rule.** Sandbox option numbering: O1 ERC-1056 · O2 ERC-721 · O3 ERC-725 · O4 ERC-725xy · O5 ERC-1155 · O6 ERC-4337 · O7 ERC-8004 · O8 LFDT/Indy-on-Besu. (The thesis draft uses a different O-numbering in places; when in doubt name the standard, not the O-number.)

Set A scoring anchors (Pass 1, /24, viability ≥16): ERC-1056 23 · LFDT 22 · ERC-725 20 · ERC-725xy 20 · ERC-4337 18 · ERC-721 15 · ERC-8004 15. Only O1 is confirmed live in the sandbox; the others are *prior evaluation pending confirmation*.

Three-stage inductive methodology: Stage 1 Native Sandbox → Stage 2 SSI Overlay (coverage F/P/X) → Stage 3 Gap Analysis and Benchmark (Family F). Gate-based, trace-driven method: gates G0–G6; traces (JSONL per `traces/SCHEMA.md`: seq, impl, ts, kind tx/view/offchain/deploy/summary, fn, fnId, identity, txHash, gasUsed, events, note) are the evidentiary artifacts; documentary evidence never resolves empirical tokens; unresolved knowledge is carried as placeholder tokens with declared resolution authorities.

## 5. Real measurements available today (the ONLY numbers you may cite as measured)

Sandbox v1.3, O1_ERC1056, scenario S1 (E2E secure I2I channel), trace `traces/i2i_O1_ERC1056_1780620182135.jsonl`, 22 entries, 12/12 functions, Hardhat local EVM, solc 0.8.24:

| Step | Function | Gas |
|---|---|---|
| createDID (Registry) | F1 | 178,935 |
| createDID (IdentityA) | F1 | 161,835 |
| createDID (IdentityB) | F1 | 161,823 |
| issueCredential | F5 | 130,163 |
| addDelegate (OBU, sigAuth, 3600 s) | F11 | 54,227 |
| createPresentation | F8 | 62,441 |
| revokeCredential | F7 | 32,980 |
| deactivateDID | F4 | 55,127 |

Recorded deviation: createDID ≈162–179K vs the <100K target, caused by explicit-DID storage (interface uniformity costs gas on the lightest standard). View functions (F2, F6, F12) are gas-free reads. The off-chain steps in S1 are ECDH P-256 + AES-256-GCM, deliberately never on-chain. Gas for other functions in S1 (addVerificationMethod, removeVerificationMethod, updateDID) exists in the trace file; cite it only by reading the file (`5_minimal-ssi-sandbox/traces/`). Anything not in a trace is a **hypothesis or a target**, and must be labelled so.

Widely cited external figures you may use only with the label **DIGEST-LEVEL** and a source: Groth16 on-chain verification ≈200–350K gas (the thesis draft says ~350K); Ethereum calldata 16 gas/non-zero byte, 4 gas/zero byte; SSTORE new slot 20,000 gas, SLOAD ≈2,100 cold / 100 warm (EIP-2929); event LOG data 8 gas/byte + topic costs; EIP-4844 blobs as cheap ephemeral data (~18 days retention); VehiclePassport (arXiv:2509.06133) 22 ms proof generation / sub-5 ms verification for vehicular attribute proofs; Canada ≈33 M registered vehicles; ERC-1056 setAttribute ≈75K, changeOwner ≈50K, addDelegate ≈55K in the reference registry; ERC-725 deployment ≈450–550K. Everything else external: **UNVERIFIED** unless you name the source and state you did not read it at source.

## 6. What exists in the repository being extended

Repository: `github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID`, branch `vid-build` (this campaign's branch), local clone `C:\Users\nikhilp\Desktop\CVIN-2026-VID-Build`. It contains: `1_blockchain-identity/` (ERC-1056 registry + CVINVehicleDIDRegistry, ERC-721 CVINVehicleNFT, ERC-725; Hardhat tests) · `2_w3c-ssi-layer/` (Python DID resolver for did:ethr/did:nft/did:key/did:mobi; **VC layer**: EIP-191 secp256k1 Data Integrity proofs over canonical JSON, SD-JWT-style salted claim digests for selective disclosure, registry-based `credentialStatus` revocation; ten automotive credential schemas UC1–UC10 + EmissionsCompliance) · `cv2x-testbed/` (MOBIVIDRegistry v1/v2 Solidity: birth certificate with vinHash + encrypted VIN + birthCertHash; lifecycle events with 11 event types MAINTENANCE, REPAIR, ACCIDENT, RECALL, INSPECTION, MODIFICATION, THEFT_REPORT, RECOVERY, INSURANCE_CLAIM, REGISTRATION, DECOMMISSION and 8 issuer roles MANUFACTURER, SERVICE_CENTER, GOVERNMENT_DMV, GOVERNMENT_INSPECTION, INSURANCE_COMPANY, POLICE, OWNER, FLEET_MANAGER; multi-party attestations; SUMO harness; centralized-PKI comparison provider) · thesis docs. MOBI VID I = immutable birth certificate (manufacturer-issued: VIN, make, model, year, production, first owner); MOBI VID II = mutable lifecycle events, multi-issuer.

New in this campaign: `5_minimal-ssi-sandbox/` = the canonical cvin-sandbox v1.3 (IMinimalSSI + ISetA/B/C, O1_ERC1056 12/12, parameterised compliance suite, S1 scenario, trace schema, CLAUDE.md hard rules) vendored in, plus the VID build of §7.

## 7. The build in this pass (reference by these names; numbers only from its traces once they exist)

Design principle: **the VID layer sits above IMinimalSSI and never alters it.** Credentials are W3C-shaped JSON objects off-chain; the chain holds only the anchor (F5 hash + validity), revocation state (F7), presentation commitments (F8), and governance (endorsement).

Planned artifacts (names are final; status is "under construction" until 10_VID_Build_Documentation says otherwise):
- `contracts/governance/EndorsementRegistry.sol` — implements the spec §6 governance extension: `registerIssuer(bytes32 issuerDid, bytes32 role)`, `endorseIssuer(bytes32 endorserDid, bytes32 issuerDid, bytes32 credentialType, uint256 validity)`, `isEndorsed(issuerDid, credentialType) view`, revocation of endorsements; roots of trust are endorser DIDs (e.g., a transport ministry endorses a DMV for DriverLicence; an OEM endorses its plants for VehicleBirthCertificate). Verification policy = F6 valid AND issuer endorsed for that type at issuance time.
- `contracts/credentials/CredentialTypeRegistry.sol` (or folded into the above) — typed credential families as bytes32 type ids with schema hashes: `VID_BIRTH` (MOBI VID I), `VEHICLE_REGISTRATION` (the "car ID": plate, jurisdiction, owner DID, validity), `DRIVER_LICENCE` (holder DID, class, restrictions, expiry — content off-chain; on-chain only the anchor), and the VID II lifecycle family (the 11 event types above).
- `lib/vid/` (JS) — credential object builders + canonical JSON + keccak hashing that produce the `credentialHash` passed to F5; presentation builders that compute the F8 `challenge`; a local "holder wallet" and "verifier" that verify off-chain (signature + hash match) and consult the chain only for F6/F12/endorsement state.
- `scenarios/run_vid_minimal.js` — S7 "minimal VID": OEM DID, DMV DID, ministry endorser DID, vehicle DID, driver DID; endorse; issue VID_BIRTH, VEHICLE_REGISTRATION, DRIVER_LICENCE; verify off-chain and on-chain; present (challenge-bound); revoke one; re-verify; emits a JSONL trace with fnId tags including the extension functions (tagged `G1`… for governance).
- `scenarios/run_vid_lifecycle.js` — S8 "all the VIDs": the 11 lifecycle event credentials issued by the role-appropriate issuers, with endorsement gating, odometer monotonicity checked off-chain, a theft→recovery chain, decommission; trace emitted.
- `test/vid.js` — tests for the endorsement and credential-type layer, running alongside the untouched 12-test compliance suite.

Everything above is on O1 (ERC-1056 pattern) first; the layer is implementation-agnostic by construction (it only calls IMinimalSSI + the governance registry), so running it on O2–O8 is a later work order.

## 8. The user's demanded coverage (checklist — every item must be substantively covered somewhere in the suite, and 00 must map where)

1. On-chain vs off-chain data; anchoring; read paths vs write paths; ZKP; verifiable data (integrity); costs — as the major decision axis between candidate systems, all the way to designing the best-of-both-worlds hybrid (scalable, realisable, cost-effective, secure, integrity, safety, privacy when required). **Primary.**
2. A CAV scenario and an AI-agent scenario that use *all* functions and objects of the identity system (created as designs, not built; to be compared with the user's own later).
3. One example scenario per latency tier (CAV and agent each).
4. Reputation; payment; gated access; low-connectivity (read-only or delayed write) scenarios (CAV and agent each).
5. Back-end systems beyond CAVs: driver's licences, deeds, repair history (CAV and agent each).
6. ZKP (huge; its own document).
7. I2I secure communication (its own document) plus the other cruxes it exposes.
8. Off-chain and on-chain (integrated into 1).
9. For every scenario: follow-on explanation connecting to problems solved or additional functionality — toll payment, pay-as-you-use roads, reporting of road and traffic conditions, federated machine learning.
10. A whole in-depth treatment of why reputation is needed for federated ML and the like, why reputation needs identity, and why identity needs the system being built; and the same chain for any other analogous collective-computation case (e.g., cooperative perception / crowd-sourced HD maps / collaborative anomaly detection).
11. A proper way to test/build, or at least demonstrate, each thing.
12. Minimum three documents including a meta commentary, deeply integrated with the rest of the work; if a piece is better done in the chat model, produce a primer document to feed it (99).
13. Endorsement as a first-class pattern in the identity design and the academic argument.

## 9. Writing rules (non-negotiable)

1. **No fabricated measurements.** Real numbers come only from §5 or from trace files you have read. External numbers carry DIGEST-LEVEL or UNVERIFIED labels and a source. Design-stage quantities are stated as targets, budgets, or formulas with variables, never as results.
2. **Interface is normative.** Never propose changing IMinimalSSI signatures, errors, or events. Extensions live beside it.
3. **Family F is design only.** Document 03 designs the hybrid; it may propose a build plan, but must state that the composite is a Stage 3 output and not a Stage 1 sandbox.
4. **Register:** academic, narrative, argued. Each section opens with the claim, then the reasoning, then the evidence or the test that would produce evidence. Use IEEE numbered citations; carry forward the thesis reference list [1]–[28] in §10 verbatim numbering, and add NEW-n for new sources (S1 will renumber into the R-series later). Prefer prose over bullets for argument; use tables for comparisons, matrices, and budgets. Headings numbered. No emoji.
5. **Cleverness with honesty.** Where a design is clever (e.g., a read path that needs no chain access, a write path that survives offline), say precisely what assumption makes it work and what breaks it.
6. **CAV and agent in every scenario document:** each scenario states actors (DIDs), objects (credentials, endorsements, presentations, channels, reputation attestations, oracles), the function sequence with F-tags (F1–F12, Set C: C1 attestReputation, C2 getReputation, C3 requestValidation, C4 validationStatus; governance: G1 registerIssuer, G2 endorseIssuer, G3 revokeEndorsement, G4 isEndorsed), the tier, the on-chain/off-chain placement of every datum, the failure modes, and the "problems solved / further functionality" tail. Then the demonstration or test that would validate it (which scenario script, which trace assertions, which metric).
7. **Cross-reference** sibling documents by number (e.g., "see 02 §4"). Do not duplicate more than a paragraph of another document's content; point to it.
8. **Length targets:** 01 and 02 and 03 and 09: 6,000–10,000 words each. 04–08: 4,000–7,000 words each. 11: 4,000–6,000. Support documents as needed. Depth over padding; every paragraph must do work.
9. Dates: today is 2026-09-03. Sandbox v1.3 date 2026-06-05. ERC-8004 mainnet 2026-01-29. SD-JWT RFC 9901 Nov 2025. Aries archived Apr 2025.
10. Terminology: "connected and autonomous vehicle (CAV)", "on-board unit (OBU)", "roadside unit (RSU)", "verifiable credential (VC)", "verifiable presentation (VP)", "decentralised identifier (DID)", "identity-to-identity (I2I)", "Security Credential Management System (SCMS)", "Vehicle Identity (VID)" per MOBI. Spell out on first use.

## 10. Reference list to carry forward (verbatim numbering from Thesis Narrative Synthesis v11.3)

[1] C. Allen, 'The Path to Self-Sovereign Identity,' 2016. · [2] Mühle et al., Computer Science Review 2018. · [3] Ferdous et al., IEEE Access 2019. · [4] Mazzocca et al., IEEE COMST 2025 (early access). · [5] Prakash, Michelson, Feng, 'CVIN: Connected vehicle information network,' IEEE VTC2020-Spring. · [6] Brecht et al., 'A security credential management system for V2X communications,' IEEE T-ITS 2018. · [7] Agudo, Montenegro-Gómez, Lopez, D-V2X, IEEE TVT 2021. · [8] W3C DID Core 1.0, 2022. · [9] W3C VC Data Model 1.1, 2022. · [10] W3C VC Data Model 2.0, 2025. · [11] Rodriguez Garzon et al., 'AI agents with decentralized identifiers and verifiable credentials,' ICAART 2026 / arXiv:2511.02841. · [12] Camenisch & Lysyanskaya, CRYPTO 2004. · [13] Flamini et al., selective disclosure mechanisms, J. Inf. Security Appl. 2024. · [14] Fett, Yasuda, Campbell, SD-JWT, RFC 9901, Nov 2025. · [15] Weyl, Ohlhaver, Buterin, Decentralized Society, 2022. · [16] Li et al., BDRA, IEEE IoT J. 2023. · [17] Kortesniemi et al., DID methods evaluation, 2019/2021. · [18] Schardong & Custódio, SSI systematic review, Sensors 2022. · [19] De Rossi et al., ERC-8004 Trustless Agents, 2025. · [20] Fedrecheski et al., SSI for IoT, GIoTS 2020. · [21] Chen, SCMS performance comparison, arXiv:2501.03237. · [22] Dunphy, blockchain trilemma for decentralized identity / Indy, arXiv:2204.05784. · [23] ERC-1056. · [24] ERC-4337. · [25] LFDT, Indy on Besu joins did:indy. · [26] W3C DID Spec Registries. · [27] MOBI VID I–II. · [28] IEEE 1609.2-2022.

Suggested NEW sources (add with your own verification label; most will be DIGEST-LEVEL): W3C Bitstring Status List v1.0; W3C Data Integrity / BBS Cryptosuite; EIP-2929 / EIP-4844 / EIP-1559; ERC-725/735/6551/7579/7702; Chainlink oracle whitepaper; McMahan et al. federated learning (2017); Kairouz et al. 'Advances and Open Problems in Federated Learning' (2021); Blanchard et al. Krum (2017) and Byzantine-robust aggregation literature; Sybil attack (Douceur 2002); EigenTrust (Kamvar 2003); Merkle proofs / light clients; IPFS/Arweave; Trust over IP governance stack; eIDAS 2.0 / EUDI ARF; ISO/SAE 21434; ETSI TS 102 941; C-ITS / SAE J2735 BSM; DIDComm v2; Google A2A; Anthropic MCP; ERC-8004 registries; zk-SNARK verification cost references (Groth16, PLONK), Semaphore; CL/AnonCreds v1 and AnonCreds v2 (BBS+); Indy-on-Besu.
