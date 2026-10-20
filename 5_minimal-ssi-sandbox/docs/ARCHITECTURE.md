# CVIN-SC Identity Sandbox — Architecture & Systems Reference

**v1.1 · June 2026 · Main Build Chat (Architect) reference document**
*Registry classification: Type B (tables) + Type A (§1, §8 prose) → Ch. 2, 3, 4*

This document is the architect-level reference for the identity sandbox: the function sets under test, the implementation options and their family structure, the sandbox design, the scenario catalog, and the LFDT ecosystem roles. It consolidates the project's prior sessions (provenance log in §9) and is the companion to `BRINGUP.md` (environment) and `BUILD_DIRECTIONS/` (CLI work orders).

---

## 1. What is being tested: the function sets

The unit of evaluation is the twelve-function minimal SSI specification (`IMinimalSSI.sol`), decomposed into three sets. The decomposition is now expressed as three Solidity interfaces in `contracts/interfaces/` so that an implementation's coverage is checkable by the compiler, not just by prose.

| Set | Interface | Functions | Evaluability |
|---|---|---|---|
| **Set A** (8) — identity baseline | `ISetA.sol` | createDID, resolveDID, updateDID, deactivateDID, addVerificationMethod, removeVerificationMethod, addDelegate, validDelegate (F1–F4, F9–F12) | Directly evaluable against ERC standards natively (Pass 1 scoring, /24) |
| **Set B** (4) — credential layer | `ISetB.sol` | issueCredential, verifyCredential, revokeCredential, createPresentation (F5–F8) | No ERC provides natively; requires pairing (JWT-VC, SD-JWT, AnonCreds, BBS+). **AnonCreds is the Set B coverage ceiling** — the 100% reference, with native ZKP `createPresentation` |
| **Set C** (ext.) — agent trust | `ISetC.sol` | attestReputation, getReputation, requestValidation, validationStatus | Derived from ERC-8004 registries (mainnet since Jan 2026); optional, exercised by agentic scenarios |

### 1.1 The twelve functions

| # | Function | Category | W3C Reference | Set |
|---|----------|----------|---------------|-----|
| F1 | createDID | DID Lifecycle | DID Core §7.1 | A |
| F2 | resolveDID | DID Lifecycle | DID Resolution | A |
| F3 | updateDID | DID Lifecycle | DID Core §7.2 | A |
| F4 | deactivateDID | DID Lifecycle | DID Core §7.3 | A |
| F5 | issueCredential | Credential Ops | VC Data Model §4.0 | B |
| F6 | verifyCredential | Credential Ops | VC Data Model §5.0 | B |
| F7 | revokeCredential | Credential Ops | BitstringStatusList | B |
| F8 | createPresentation | Credential Ops | VC Data Model §6.0 | B |
| F9 | addVerificationMethod | Key Management | DID Core §5.2 | A |
| F10 | removeVerificationMethod | Key Management | DID Core §5.2 | A |
| F11 | addDelegate | Key Management | did:ethr extension | A |
| F12 | validDelegate | Key Management | did:ethr extension | A |

## 2. What it is tested on: options and families

Two structures exist in the project corpus and both are carried here, with the v2-0 Implementation Plan + LFDT Addendum as the **governing build structure**.

### 2.1 The original eight options (Build Stages 11–17 lineage)

| # | Standard | Identity model | Key characteristics | Build status |
|---|----------|---------------|---------------------|--------------|
| O1 | ERC-1056 | Address = DID, event-sourced (did:ethr) | Veramo ecosystem anchor; lowest gas | **In sandbox, 12/12 passing** |
| O2 | ERC-721 | Soulbound NFT = identity | Simple ownership; limited key mgmt | **In sandbox, 12/12 passing** (fresh native implementation 2026-10-17, WO-1 fallback clause) |
| O3 | ERC-725 | Proxy contract = DID | Key-value store (725Y); direct queryability | **In sandbox, 12/12 passing** (fresh native implementation 2026-10-17; createDID ≈747–764K) |
| O4 | ERC-725xy | Contract + ERC-735 claims | LUKSO-inspired; key purposes; highest native coverage (~79%) | **In sandbox, 12/12 passing** (fresh native implementation 2026-10-17; createDID ≈1.62M; issueCredential = ERC-735 claim, 308K) |
| O5 | ERC-1155 | Multi-token soulbound bundle | Batch capable; weak DID lifecycle | **In sandbox, 12/12 passing** (fresh native implementation 2026-10-17; credentials are tokens, revoke = burn) |
| O6 | ERC-4337 | Smart account = DID | validateUserOp validation keys; social recovery; 1M+ deployments | **In sandbox, 12/12 passing** (fresh native implementation 2026-10-17; delegates = session keys; createDID ≈1.08M) |
| O7 | ERC-8004 | Agent identity + registries | Identity (ERC-721/CAIP-10) + Reputation (0–100, evidence URIs) + Validation (zkML/TEE hooks); **mainnet Jan 29 2026** | **In sandbox, 12/12 passing** (three registries per the Draft EIP + IMinimalSSI/ISetC layer, 2026-10-17; viaIR per-file) |
| O8 | LFDT | Indy-on-Besu adapter | nymTx pattern on EVM; AnonCreds-native Set B | **In sandbox, 12/12 passing** (indy-besu record shapes; schema/cred-def/revocation registries; 2026-10-17) |

**Set A scoring baselines (Pass 1, /24)** — recovered from the three-pass evaluation; the CLI uses these as sanity anchors (large deviations in a fresh implementation indicate a porting error, not a new finding):

| ERC-1056 | LFDT | ERC-725* | ERC-725xy | ERC-4337 | ERC-721 | ERC-8004 |
|---|---|---|---|---|---|---|
| 23 | 22 | 20 | 20 | 18 | 15 | 15 |

*Viability threshold ≥16. ERC-1155 was architecturally subsumed by ERC-721 in scoring but remains a build option.*

### 2.2 The governing structure: 6 families, 14 options (v2-0 + LFDT Addendum)

The v2-0 Implementation Plan organizes evaluation into six architectural families totaling 14 options, evaluated through a **three-stage methodology: Stage 1 Native Sandbox → Stage 2 SSI Overlay → Stage 3 Gap Analysis.**

| Family | Name | Confirmed members | Notes |
|---|---|---|---|
| A | Lightweight | ERC-1056, ERC-1155 | "How far can existing EVM infrastructure stretch?" |
| B | Token-as-identity | ERC-721 lineage (+ ERC-6551 token-bound accounts ⊕) | ⊕ membership to verify in WO-0 |
| C | Contract account / claims | ERC-725, ERC-725xy (+ ERC-4337, EIP-7702 ⊕) | ⊕ membership to verify in WO-0 |
| D | Agent / registry | ERC-8004 (⊕ placement to verify) | ERC-8004 + ERC-6551 noted complementary (agent NFT + own wallet) |
| **E** | Purpose-built SSI (expanded) | **E1 Indy-Besu · E2 Identus · E3 AnonCreds** | Expansion replaces single Indy-on-Besu entry; repo dirs `LFDT/E1-indy-besu/`, `E2-identus/`, `E3-anoncreds/` |
| F | **CVIN Combined** | Hybrid synthesis | **Stage 3 output only — never built as a Stage 1 sandbox.** Hard rule for the CLI. |

⊕ = exact family membership not fully recoverable from session snippets; **WO-0 in BUILD_PLAN.md ingests the v2-0 plan DOCX as the authoritative source before any family-dependent work runs.**

**Family E member contrast (from the LFDT Addendum):**

| Attribute | E1 — Indy-Besu | E2 — Identus | E3 — AnonCreds |
|---|---|---|---|
| Ledger | Besu (EVM, QBFT) — same substrate as ERC options | Cardano (eUTxO) — contrasting account model | Ledger-agnostic (VDR adapter) |
| DID method | did:indy:besu | did:prism | Any VDR; method-agnostic |
| VC format | AnonCreds (CL) + SD-JWT + W3C VC-JWT | JWT-VC + AnonCreds | CL (v1) + BBS+ (v2), pluggable |
| DID lifecycle (F1–F4) | Full, via Solidity | Full, via REST API | VDR adapter only (0 native) |
| Credential ops (F5–F8) | Full; ALLOSAUR revocation | Full; JWT revocation registry | Deepest — core purpose |

**Known label collision (flagged, not silently fixed):** "Family E" = E1/E2/E3 purpose-built SSI in the v2-0 addendum, but = the agentic protocol layer (A2A, MCP, Auto ID) in the April-5 building-paths document. The build repo uses the v2-0 meaning; the agentic protocol layer is referred to here as the **Agentic Frontier** (not a family). Thesis-consistency item logged for the registry.

### 2.3 LFDT ecosystem: cross-cutting roles, not options

| Component | Stage 1 (Native Sandbox) | Stage 2 (SSI Overlay) | Stage 3 (Gap Analysis) |
|---|---|---|---|
| Aries / ACA-Py | Protocol gap **marker** (annotation only; RFC 0454 reference path) | Set B reference implementation; "Aries-assisted" vs "native" in coverage matrices | Bridge-cost quantification (gas + DIDComm overhead) → Family F gas budget |
| AnonCreds | E3 native sandbox (proof-generation ms = primary metric) | **Set B coverage ceiling (100% reference)** | ZKP cost baseline: CL vs BBS+ vs SD-JWT vs none → feeds Stage 19 |
| Caliper | Workload modules for all 12 functions; TPS, p50/p95 latency, gas/op vs Besu SUTs | n/a (structural mapping) | Cross-option performance table → contributions C12/C13 |
| CREDEBL | Not evaluated (deployment platform) | n/a | Production evidence (Bhutan NDI, PNG SevisPass) for real-world section |

Ecosystem corrections carried into Inventory v3: Aries **archived April 2025** (success migration: ACA-Py/Credo-TS/Bifold → OpenWallet Foundation; DIDComm → DIF); Indy SDK deprecated in favor of Askar + Indy VDR + AnonCreds; new agentic-identity efforts (Hiero Heka, First Person Project) sharpen the Stage 31 novelty claim — this thesis contributes the minimal-function compliance/benchmark layer *beneath* such platforms.

## 3. Sandbox design (two-layer, trace-driven)

**Layer 1 — Execution sandbox (ground truth).** One Hardhat project (`cvin-sandbox/`), all EVM options deployed against the shared interfaces, scenario scripts emitting JSONL execution traces (txHash, F1–F12 tag, acting identity, gas, events, reverts). Traces are the evidentiary artifacts: every Ch. 4 claim is reproducible by re-running a scenario. The previously separate `cvin-benchmark/` project (Stage 15) is **unified into this repo** — benchmarking is a script, not a second environment.

**Layer 2 — Identity Sandbox Explorer (visualization).** React artifact replaying traces: identity cards (DID, keys, delegates, VCs + revocation state), transaction timeline with F-tags and gas, I2I channel pane (handshake → AEAD exchange → teardown on revocation), 12-function coverage tracker. The trace schema (`traces/SCHEMA.md`) is the contract between layers.

Rationale: visualization alone cannot defend gas/ordering claims; execution alone produces nothing demonstrable. Decoupling via traces makes Layer 1 citable and Layer 2 presentable.

## 4. Scenario catalog (organized by the 2020 paper's latency tiers)

The three latency tiers originate in the published CVIN paper (IEEE VTC2020-Spring) — low (<100 ms: BSM/collision avoidance), medium (100–500 ms: tolling, EV charging, parking), high (>500 ms: finance, insurance, vehicle history). The catalog exercises every tier plus the paper's two signature concepts (dual identity modes; IDPPs):

| ID | Scenario | Tier | Functions | Status |
|---|---|---|---|---|
| **S1** | E2E secure I2I channel: mutual auth → VP challenge-binding → off-chain ECDH/AES-256-GCM → **mid-session revocation teardown** | Low (anchors off-chain) | **12/12** | **Verified, trace on file** |
| S2 | Dual-mode identity: pseudonymous DID for BSM stream + verinym DID with MOBI VID for commercial tx — one system, both modes (the SCMS differentiator) | Low + Medium | F1, F2, F4–F8, F11, F12 | **Verified on O1–O8 (2026-10-19)**; escrowed linkage shown |
| S3 | Medium-tier commercial: EV-charging session — verinym handshake, tariff credential, payment-anchored receipt | Medium | F1, F2, F5, F6, F8 + G | **Verified on O1–O8 (2026-10-19)**; Tier 2 path has zero chain entries |
| S4 | High-tier lifecycle: insurance credential (ICBC example from the 2020 paper), vehicle history attestation, ownership transfer with key rotation | High | F1–F3, F5–F7, F9–F12 + G | **Verified on O1–O8 (2026-10-19)**; transfer = rotation + expiry + re-issuance |
| S5 | **IDPP port**: identity + credentials ported O1 → O8 (E1) — makes the 2020 ID Porting Protocol concept testable for the first time | Cross | F1, F3, F4, F5, F6, F11, F12 ×2 impls | **Verified both directions (O1→O8, O8→O1), traces on file (2026-10-17)**; finding: no 'superseded' status in the interface |
| S6 | Agentic wrapper: agent principal with ERC-8004 reputation + validation, credential-gated action (Stage 31 feed) | Cross | Set C + F8 | Deferred to Stage 31 |
| S7 | Minimal VID with endorsement (birth certificate, registration, driver licence; G0–G4, T1–T2) | High | 12/12 + G/T | **Verified on O1–O8** |
| S8 | All eleven MOBI VID II lifecycle event types, role-gated endorsement, Merkle batch | High | F1,F2,F4–F8 + G | **Verified on O1–O8** |
| S14 | Delayed write: READ_ONLY/PARTITIONED modes, signed queue, reconcile (revocation wins), one batch anchor | Medium (offline) | F5–F7 + B1–B2 | **Verified on O1** |
| S16 | Reputation-weighted federated round, GATED vs UNGATED Sybil experiment (Set C harness) | High | C1–C4 + B1 | **Verified on O1 (harness)** |
| S17 | Batch anchor with on-chain inclusion proofs; A/B/C anchoring comparison | High | F5 + B1–B3 | **Verified on O1** |
| S19 | BBS+ policy-selected disclosure to three verifier classes | Medium | F5,F8,F9 | **Verified on O1** |
| S20 | Groth16 age-gate predicate, on-chain verification (250,283 gas) | Medium | F5,F8 + Z1–Z2 | **Verified on O1** |

Detail for S7–S20: `../docs/hda-campaign/10_VID_Build_Documentation.md`; canonical register: `../docs/hda-campaign/00_HDA_Master_Plan_and_Attack.md` §6.

## 5. Verified state (as of this version)

| Item | State |
|---|---|
| Interfaces | `IMinimalSSI.sol`, `ISetA.sol`, `ISetB.sol`, `ISetC.sol` — compile clean (solc 0.8.24) |
| O1_ERC1056 | Complete reference implementation, **12/12 compliance tests passing** |
| O2_ERC721 | Native soulbound port, **12/12 passing**; S1/S7/S8 traces on file (2026-10-17) |
| O3_ERC725 | Contract-per-identity port (ERC725Account + registry), **12/12 passing**; S1/S7/S8 traces on file (2026-10-17) |
| O4_ERC725xy | ClaimHolderAccount (725Y + 734 keys + 735 claims) port, **12/12 passing**; S1/S7/S8 traces on file (2026-10-17) |
| O5_ERC1155 | Soulbound multi-token port (credentials are tokens), **12/12 passing**; S1/S7/S8 traces on file (2026-10-17) |
| O6_ERC4337 | SmartAccount (validateUserOp, session keys) port, **12/12 passing**; S1/S7/S8 traces on file (2026-10-17) |
| O7_ERC8004 | Three ERC-8004 registries + compliance layer (reference ISetC), **12/12 passing**; S1/S7/S8 traces on file (2026-10-17) |
| O8_LFDT | Indy-on-Besu adapter, **12/12 passing**; S1/S7/S8 traces on file (2026-10-17) |
| Gas matrix | `benchmarks/gas_matrix.js` → `gas_matrix.csv`, `gas_report.md` generated from traces, eight options |
| Tier coverage | `benchmarks/tier_coverage.js` → `tier_coverage.md` (per-scenario, per-tier function coverage from traces; WO-4 AC) |
| Coverage matrix | `benchmarks/coverage.js` → `coverage_matrix.csv`, `coverage_report.md` (native/assisted/anchor/absent per option × F1–F12, trace-checked) — WO-5 complete |
| Compliance suite | `test/compliance.js`, parameterized; spec §4.1 implemented verbatim; **O1–O8 enabled, 96/96** |
| Scenario S1 | Executed; 22-entry JSONL trace, 12/12 functions, real gas |
| Offline toolchain | Hardhat compiles via npm solc-js (no binary downloads) — CI/air-gap reproducible |

**Recorded deviations:** O1 `createDID` ≈162–179K gas vs spec's <100K target (explicit-DID storage vs pure event-sourcing — interface uniformity has measurable cost; Stage 15 optimization item). Spec erratum: `CredentialRevoked` declared as both error and event (name collision; event renamed `CredentialRevokedEvent`; log for spec v1.1).

## 6. Gas targets (spec §5.3, retained as benchmark hypotheses)

| Function | ERC-1056 target | ERC-725 target | | Function | ERC-1056 | ERC-725 |
|---|---|---|---|---|---|---|
| createDID | <100K | <600K | | revokeCredential | <50K | <60K |
| resolveDID | <10K | <20K | | createPresentation | <150K | <200K |
| updateDID | <80K | <100K | | addVerificationMethod | <100K | <120K |
| deactivateDID | <50K | <60K | | removeVerificationMethod | <50K | <60K |
| issueCredential | <120K | <150K | | addDelegate | <60K | <70K |
| verifyCredential | <10K | <15K | | validDelegate | <5K | <10K |

## 7. Document map

| Doc | Role |
|---|---|
| `docs/ARCHITECTURE.md` (this) | Architect reference: what is tested, on what, how |
| `docs/BRINGUP.md` | Environment: prerequisites, layout, bring-up sequence, expected outputs |
| `BUILD_DIRECTIONS/CLAUDE.md` | Standing instructions for the Claude Code CLI agent |
| `BUILD_DIRECTIONS/BUILD_PLAN.md` | Ordered work orders (WO-0…WO-9) with acceptance criteria |
| `traces/SCHEMA.md` | Layer 1 → Layer 2 trace contract |

## 8. Why this architecture (thesis framing)

The sandbox operationalizes the extension-not-replacement argument: the 2020 paper posed multi-option questions (which platforms for which latency tiers; how to port identity across chains; how to decouple identity from any single ledger) and explicitly treated Indy/Aries as "a starting point." The 14-option, family-structured sandbox is the systematic answer to those questions — including making IDPPs (S5) and dual-mode identity (S2) empirically testable for the first time. Within-family comparisons isolate architectural costs; cross-family comparisons reveal fundamental trade-offs; the LFDT layer supplies the measurement instruments and the Set B ceiling. None of the LFDT incubation projects competes as a Set A identity anchor — they are credential/privacy/platform layers above it, which itself evidences the extension thesis.

## 9. Integration provenance log (this pass)

| Source | Integrated | Change/insight |
|---|---|---|
| CVIN paper (IEEE VTC2020-Spring) | Latency tiers, dual identity modes, IDPPs, ICBC example, Local CVINs | Scenario catalog reorganized by tier; S2 (dual-mode) and S5 (IDPP) added; 2020 concepts become testable |
| Stage 11/12 sessions | 8-option list, native-pattern principle, O6 validateUserOp pattern, O7/O8 specs | "Native patterns, never wrapped registries" codified as CLI build rule; O7 three-registry spec recovered |
| Stage 14 session | 9-step BSM/I2I pipeline, 8/12 coverage, 4 negative-lifecycle gap | S1 extends to 12/12 via mid-session revocation; explorer panel design inherits Stage 14 layout |
| Stage 15 session | Separate cvin-benchmark project; ISetA/B/C decomposition; Pass 1 scores (/24) | Projects unified; three interfaces added to repo (compile-verified); scores kept as sanity anchors |
| Main Chat 4 / three-pass eval | Set A/B/C definitions, viability threshold, "no ERC natively supports createPresentation" | Set B ceiling framing; ISetB NatSpec records the finding |
| v2-0 Plan + LFDT Addendum (Apr 2026) | 6 families / 14 options; three-stage methodology; LFDT cross-cutting roles; Family F = Stage 3 output | Governing structure adopted; WO-0 created to ingest authoritative plan; Family-F hard rule for CLI |
| Building-paths doc (Apr 2026) | 5-family narrative taxonomy; six-level profiles | "Family E" label collision flagged; agentic layer renamed "Agentic Frontier" in build repo only |
| LFDT web verification (Jun 2026) | Incubation set (AnonCreds, Identus, CREDEBL, Paladin, Caliper, Minokawa); Aries archived; ACA-Py → OWF; Hiero Heka; First Person Project | Inventory v3 corrections; Stage 31 positioning sharpened |
