CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Weighted Reference Index and Verification-Debt Register**

**Every source the campaign used, merged and de-duplicated across sixteen documents, weighted by how much argument rests on it, labelled with its verification state, and ordered into a prioritised reading list of what must be read at source before it is quoted in the thesis**

Document 13 of 16 · Hybrid Data Architecture (HDA) Campaign · Support document (S1) · Suite v1.0 · October 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type B (register, index) → Admin; §5 is the operative section for Chapter 4 and 5 drafting and for the limitations section*

---

## 1. What this document is, and the numbering it uses

The sixteen documents of this suite were written in parallel against a common brief, and each closes with its own sources table. That arrangement guarantees that no claim is unattributed and guarantees nothing else: the same source appears under different labels in different documents, the per-document `NEW-n` series collide outright, and the verification state of a source is recorded once per document rather than once per source — so a reader cannot tell, from any single table, whether a figure was read at source somewhere else in the suite. This document merges the tables, resolves the collisions, and states each source's verification state once.

**Numbering.** The programme's cumulative R-series lives in the Systematic Review v13.1 suite, which was not on this machine during this pass. This index therefore uses two stable series and one provisional one:

- **[1]–[28]** — the thesis reference list, carried forward verbatim from the Narrative Synthesis v11.3 (brief §10). These numbers are stable and are used unchanged throughout the suite.
- **H1–H48** — *HDA-provisional* identifiers for sources new in this campaign. They replace every per-document `NEW-n`. On merge into the Systematic Review they become R-numbers; until then, **cite H-numbers in this suite and never a bare `NEW-n`.**
- **A1–A33** — the campaign's own **primary artefacts**: code, traces, tests and programme documents read at source. These are not literature and are not weighted on the same scale; they are the suite's evidence, and §3 lists them separately because a reader checking a measured claim goes there first.

**The collision this document fixes (K-HDA-10).** The per-document `NEW-n` series were assigned independently and conflict in at least eleven places. `NEW-1` denotes the W3C Bitstring Status List in 01, 03, 06 and 08, the GDPR data-minimisation articles in 02, eIDAS 2.0 in 07, and McMahan's FedAvg paper in 09. `NEW-2` denotes EIP-2929 in 01, 03 and 06, the EVM gas schedule generally in 02, the EUDI reference framework in 07, the Noise Protocol Framework in 08, and Kairouz et al. in 09. `NEW-8` and `NEW-11` collide four ways each. No document is wrong internally; the suite is unusable as a corpus. This is logged as **K-HDA-10** and is added to the ledger in S3 §4. The crosswalk in §6 is the remedy for documents that are not rewritten.

## 2. The weighting scale

Weight answers one question: *if this source turns out to say something other than what the suite assumes, what breaks?*

| Weight | Meaning | Consequence if the source is misread |
|---|---|---|
| **W1 — load-bearing** | A specific claim in the suite depends on this source's content | The claim fails or must be restated. These are the sources to read at source first |
| **W2 — supporting** | Supplies a constant, a comparison, a cost figure, or corroboration | The claim weakens or loses a number but survives in narrowed form |
| **W3 — contextual** | Vocabulary, framing, related-work positioning, or an analogy | Nothing breaks; a sentence is reworded |

Verification state uses the brief's three labels without modification: **VERIFIED AT SOURCE** (read, in this pass or a prior one, by the author), **DIGEST-LEVEL** (taken from a summary, an abstract, a secondary citation, or the brief, and not read in full), **UNVERIFIED** (named but not read at all, including cases where only the title and claimed content are known).

The combination that matters is **W1 + not VERIFIED AT SOURCE**. Those are the suite's exposed claims, and §5.1 lists all of them in one place. There are eleven.

## 3. Primary artefacts (A-series): the campaign's own evidence

Every measured number in the suite traces to one of these. All are VERIFIED AT SOURCE by definition — they were read or generated in this pass — and all are W1, because the suite's empirical claims rest on nothing else.

| A# | Artefact | What it evidences | Cited by |
|---|---|---|---|
| A1 | `traces/i2i_O1_ERC1056_1780620182135.jsonl` (22 entries, S1, architect pass 2026-06-05) | The June gas baseline for F1–F12 | 01, 02, 03, 06, 07, 08, 09, 10 |
| A2 | `traces/i2i_O1_ERC1056_1788492893157.jsonl` (S1 rerun, operator machine) | Reproducibility: identical on 12 of 13 transactions; F8 differs by 5 gas | 10 |
| A3 | `traces/vid_minimal_O1_ERC1056_1791157391842.jsonl` (56 entries, S7) | Three minimal credentials; G0–G4, T1–T2 gas; zero-chain-read verification; stale acceptance; replay revert | 04, 05, 10 |
| A4 | `traces/vid_lifecycle_O1_ERC1056_1791157402169.jsonl` (69 entries, S8) | Eleven lifecycle types; the 11:1 Merkle-batch result; transitive endorsement; decommission | 04, 05, 10 |
| A5 | `contracts/interfaces/IMinimalSSI.sol`, `ISetA.sol`, `ISetB.sol`, `ISetC.sol` | The normative twelve functions and the Set C signatures | All |
| A6 | `contracts/implementations/O1_ERC1056.sol` | The only live option; byte-identical to canon v1.3 | 01, 02, 10 |
| A7 | `contracts/governance/EndorsementRegistry.sol`, `IControllerAdapter.sol`, `O1ControllerAdapter.sol` | G0–G4 semantics: typed, expiring, depth-bounded, transitivity-gated endorsement | 04, 07, 09, 10, 11 |
| A8 | `contracts/credentials/CredentialTypes.sol`, `TypedCredentialRegistry.sol`, `TypedHashProbe.sol` | The fourteen type identifiers; the typed-anchor rule; T1/T2 | 04, 05, 07, 10 |
| A9 | `lib/vid/credentials.js`, `lib/vid/trace.js` | Off-chain credential objects, canonicalisation, EIP-191 issuer proofs, salted-digest disclosure, verifier cache | 02, 04, 10 |
| A10 | `test/compliance.js` (12 tests), `test/vid.js` (7 tests) | 19 passing; compliance unchanged from v1.3 | 10 |
| A11 | `scenarios/run_i2i.js`, `run_vid_minimal.js`, `run_vid_lifecycle.js` | S1, S7, S8 procedures; ECDH/AEAD parameters; challenge construction | 08, 10 |
| A12 | `traces/SCHEMA.md` | The trace contract; the absence of timing fields | 05, 08, 10 |
| A13 | `docs/ARCHITECTURE.md` v1.1 | Scenario catalog S1–S6; the latency-tier organisation; family map; Family F hard rule | 03, 05, 06, 08, 09 |
| A14 | `docs/FINDINGS.md` items 4–10 | Findings F-VID-1 to F-VID-7 | 04, 05, 10, 11, S3 |
| A15 | `CLAUDE.md` (sandbox standing rules), `BUILD_PLAN.md`, `BUILD_LOG.md` WO-V entry | The method's constraints; the provenance of this build | 10, S3 |
| A16 | SSI Minimal Function Specification (Formal) §4.1, §5.3, §6 | Compliance tests; gas targets; the named governance extension | 04, 10, 11 |
| A17 | `cv2x-testbed/contracts/MOBIVIDRegistry.sol`, `MOBIVIDRegistryV2.sol` | The purpose-built baseline the VID layer re-expresses generically; role matrix; on-chain odometer | 02, 07, 10 |
| A18 | `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py`, `vc_holder.py`, `mobi-vid/README.md` | The existing VC layer: EIP-191 proofs, SD-JWT-style digests, UC1–UC10 schemas | 01, 02, 07 |
| A19 | `_CONTEXT_BRIEF.md` | The authoring contract: vocabulary, measured-number allowlist, writing rules | All |
| A20 | Supervisor memos A and B, Technical Memo 2; Thesis Narrative Synthesis v11.3 and Content Block Registry; the Deliverable Suite Architecture v1.0 convention; Building Paths preface | Architectural stance (on-chain registries, off-chain content, endorser sets, cache/revocation coupling); chapter and contribution structure; the three framework properties | All |

**Added by Slice 1 (2026-10-14).** All VERIFIED AT SOURCE, all W1, all documented in 10 Addenda A and B.

| A# | Artefact | What it evidences | Cited by |
|---|---|---|---|
| A21 | `contracts/credentials/BatchAnchorRegistry.sol` (B1–B3) | A dedicated batch anchor with on-chain inclusion as a gas-free view: `anchorBatch` 122,139 against 130,163 for a root via F5 (≈6% cheaper, not half); whole-batch revocation 55,267; tampered-leaf and unauthorised-issuer reverts. Settles the g_a estimate in 01 §7. **F-VID-8** | 01, 04 §2.6, 05 §5, 10 Add. A |
| A22 | `lib/vid/offline.js` and `scenarios/run_delayed_write.js` (S14) | The Anchor · Cache · Attest · Reconcile pattern of 03 §3 realised from the twelve functions plus a batch anchor: ONLINE / READ_ONLY / PARTITIONED link model, signed counter-ordered queue, dependency re-check on reconnect; stale acceptance reproduced, then "revocation wins"; zero writes during the outage, one on reconnect. **F-VID-9** | 03, 05 §3.2/§7, 06 §5, 10 Add. A |
| A23 | `contracts/harness/SetCHarness.sol` and `test/setc_harness.js` | C1–C4 executing as a **harness, not O7**: C1 83,493 (repeat attester) to 117,693 (first attestation of a subject); endorsement-gated attestation; and `resolveValidationAs`, added because `ISetC` has no validator-answer path. **F-VID-11** | 04 §2.7/§3, 06 §2, 09, 10 Add. B |
| A24 | `scenarios/run_fl_round.js` (S16), trace `fl_round_…1792035691983` (97 entries) | The GATED/UNGATED experiment: reputation-weighted error 1.87 vs 23.67 unweighted when attesters are endorsement-gated; **27.59 — worse than unweighted — when they are not.** The ordering is the result; the magnitudes are a toy model. **F-VID-10** | 09, 04 §2.8/§3.8, 10 Add. B |
| A25 | `traces/batch_anchor_O1_ERC1056_1792035482337.jsonl` (26 entries) | The three anchoring patterns side by side; inclusion proof behaviour | 01, 04, 10 Add. A |
| A26 | `traces/delayed_write_O1_ERC1056_1792035487512.jsonl` (28 entries) | The degradation and reconciliation sequence | 03, 05, 06, 10 Add. A |
| A27 | `traces/fl_round_O1_ERC1056_1792035691983.jsonl` (97 entries) | The federated round, both configurations | 09, 10 Add. B |
| A28 | `traces/vid_minimal_…1792035745190`, `vid_lifecycle_…1792035749199`; `traces/SCHEMA.md` v1.1; `lib/vid/merkle.js`; `test/batch_offline.js` | S7 and S8 re-emitted with `latencyMs`; the additive timing schema; Merkle construction and its tests. **Timing is instrumented; Hardhat values are a lower bound and not results** | 05, 10 Add. B |

| A29 | `lib/vid/bbs.js`, `scenarios/run_bbs_presentation.js` (S19), `test/bbs.js`, trace `bbs_presentation_…1792062147559` (30 entries) | **Slice 2(b), 2026-10-15.** BBS+ over BLS12-381 on the suite's own credential objects: one driver's licence presented to three verifier classes under three policies. Proof sizes 384 B (9/9 revealed), 608 B (2/9), 640 B (1/9); generate 93/107/116 ms, verify 66/59/116 ms (laptop, WASM). F8 commitment 62,470 gas in all three; BBS+ issuer key as a DID verification method via F9, 96-byte key, 60,967 gas. Unlinkability observed. **F-VID-13** (proof size rises as disclosure falls), **F-VID-14** (a proof proves issuance, not currency — after F7 it still verifies; only F6 says revoked). One new dependency, `@mattrglobal/bbs-signatures` 1.4.0 | 02, 05 §1.4/§3.2, 03 §2, 10 Add. C |

| A30 | `circuits/AgeGate.circom`, `zk/` (2¹² ceremony + Groth16 zkey), `contracts/zk/ZKAgeGate.sol`, `scenarios/run_zk_age_gate.js` (S20), trace `zk_age_gate_…1792062543673` (17 entries) | **Slice 2(c), 2026-10-15.** A range predicate proven and verified on-chain: Poseidon(birthYear, salt) commitment ∧ birthYear ≤ maxBirthYear, 256 constraints, two public signals. Generation **3,999.9 ms**; off-chain verification **645.3 ms** (cold first call); calldata 705 B; `check` view 0 gas; **`admit` 250,283 gas**; F8 alongside 62,458. Replay and wrong-holder both revert; an under-age year produces no witness. **F-VID-16** (proving exceeds verifying by ~2 orders of magnitude, so prover placement is the design question), **F-VID-17** (predicate-capable credentials need a Poseidon commitment beside the keccak one). Pins: `circom2` 0.2.8 WASM, `snarkjs` 0.7.5, `circomlib` 2.0.5, `circomlibjs` 0.1.7. Sandbox ceremony, single contributor; no revocation input | 02, 04 §2.4, 05 §3.2.1, 10 Add. D |

| A31 | `contracts/implementations/O2_ERC721` … `O8_LFDT`, `ERC8004Registries.sol`, `SmartAccount.sol`, per-option controller adapters; S1/S7/S8 traces on all eight options | **WO-1/2/3, 2026-10-17.** Every option admits the layer **12/12 unmodified**, with the three scenarios running unchanged. This is the measured form of the "extend beside, never inside" claim, and it verified the portability doubt recorded in S3 §6.2. Includes the O8 property that no per-credential content hash is stored at all, and F-O7-1 (ERC-8004 needs `viaIR`) | 01, 04 §5, 11, 10 Add. E–I |
| A32 | `benchmarks/gas_matrix.js` → `gas_matrix.csv`, `gas_report.md`; `benchmarks/coverage.js` → `coverage_matrix.csv`, `coverage_report.md` | **WO-5, 2026-10-17.** Eight options × nineteen tags, and a native/assisted/anchor/absent declaration per function — both **generated from traces, nothing hand-entered**, which is the acceptance condition the build plan set. **F-WO5-4: the coverage ordering and the gas ordering rank the options differently**, so neither matrix alone ranks the standards and the placement axis is what reconciles them — document 01's thesis confirmed by an experiment aimed at something else | 01 §8/§10, 03, 11 §3, 10 Add. H–J |
| A33 | `scenarios/run_idpp_port.js` (S5), traces `idpp_port_O1→O8` and `idpp_port_O8→O1` | **WO-7, 2026-10-17.** The 2020 paper's ID Porting Protocol executed in both directions with nine continuity assertions, using the twelve functions and nothing else (**F-S5-1**). **F-S5-2:** the source credential stays F6-valid after the port, so supersession is verifier policy rather than a chain fact — the fifth instance of the interface-gap pattern (S3 §6.4) and a spec v1.1 candidate | 03 §4.3, 07, 11, 10 Add. J |

Suite totals after the option ports: **131 passing tests, 68 traces on file**, findings F-VID-1 to F-VID-18 plus the per-option series (F-O2-*, F-O5-1, F-O6-1, F-O7-1), F-WO5-1/2/4 and F-S5-1/2. The A-series is now the suite's single largest body of VERIFIED AT SOURCE evidence, and the asymmetry §5.1 identifies — thoroughly verified code, barely verified premises — widened rather than narrowed, because Slice 1 added eight artefacts and no readings.

**One caveat on A19 and A20.** The brief is VERIFIED AT SOURCE as a document, but the memos and the synthesis reach most documents of this suite *through* it rather than directly. Where a document attributes a framing sentence to "memo stance", the chain of custody is memo → brief → document, and the memo itself is DIGEST-LEVEL for that document. This is recorded here once rather than repeated in nine tables.

## 4. The merged literature index

### 4.1 Thesis list [1]–[28], with this campaign's use and weight

| Ref | Source | State | W | Used in this campaign for |
|---|---|---|---|---|
| [1] | Allen, The Path to Self-Sovereign Identity, 2016 | VERIFIED AT SOURCE | W3 | Consent, minimisation, persistence, control principles (02 §1.2, 07 §1.2, 09 §4.1) |
| [2] | Mühle et al., Computer Science Review 2018 | DIGEST-LEVEL | W3 | SSI component taxonomy (background only) |
| [3] | Ferdous et al., IEEE Access 2019 | DIGEST-LEVEL | W3 | SSI definitional framing |
| [4] | Mazzocca et al., IEEE COMST 2025 | DIGEST-LEVEL | W3 | Survey positioning |
| **[5]** | **Prakash, Michelson, Feng, CVIN, IEEE VTC2020-Spring** | **VERIFIED AT SOURCE** | **W1** | **Latency tiers (both wordings); dual identity modes; Local CVINs and IDPPs; distributed oracles; RSUs as edge servers; sidechain/backbone anchoring; wireless constraints; the Tier 3 training-data item.** The most load-bearing single source in the suite and the only W1 that is also fully verified — it is the author's own |
| [6] | Brecht et al., SCMS, IEEE T-ITS 2018 | DIGEST-LEVEL | **W1** | The accountability gap; pseudonym pools and linkage authorities; misbehaviour authority; centralised-PKI archetype. **Exposed:** the whole "extension, not replacement" argument rests on what SCMS does and does not do |
| [7] | Agudo, Montenegro-Gómez, Lopez, D-V2X, IEEE TVT 2021 | DIGEST-LEVEL | W3 | Related work in decentralised V2X |
| [8] | W3C DID Core 1.0, 2022 | DIGEST-LEVEL (VERIFIED AT SOURCE via brief §3 in 02, 06, 07) | **W1** | Set A semantics; verification methods; resolution and deactivation behaviour that F2/F4/F9/F10 implement |
| [9] | W3C VC Data Model 1.1, 2022 | DIGEST-LEVEL / VERIFIED via brief | **W1** | Credential and presentation objects; `credentialStatus`; challenge and domain |
| [10] | W3C VC Data Model 2.0, 2025 | DIGEST-LEVEL | W2 | Credential shape used by the build's objects; privacy considerations on status and hashes |
| [11] | Rodriguez Garzon et al., AI agents with DIDs and VCs, ICAART 2026 | DIGEST-LEVEL | **W1** | Agents hold keys, present VCs, sign actions. **Exposed:** the agent half of the suite (04 §3, 06, 08, 09 §7) leans on this and on [19] |
| [12] | Camenisch & Lysyanskaya, CRYPTO 2004 | DIGEST-LEVEL | W2 | CL signatures and the accumulator lineage; basis for ZK link and predicate proofs |
| [13] | Flamini et al., selective disclosure mechanisms, JISA 2024 | DIGEST-LEVEL | W2 | Comparative framing and constrained-device cost ranges (02 §2) |
| [14] | Fett, Yasuda, Campbell, SD-JWT, RFC 9901, Nov 2025 | DIGEST-LEVEL | **W1** | Salted claim digests as per-claim commitments — the construction the build actually implements in A9 |
| [15] | Weyl, Ohlhaver, Buterin, Decentralized Society, 2022 | DIGEST-LEVEL | W3 | Non-transferable reputation; whitewashing discussion |
| [16] | Li et al., BDRA, IEEE IoT J. 2023 | DIGEST-LEVEL | W3 | Related work |
| [17] | Kortesniemi et al., DID methods evaluation | DIGEST-LEVEL | W3 | Method-comparison precedent |
| [18] | Schardong & Custódio, SSI systematic review, Sensors 2022 | DIGEST-LEVEL | W3 | Review positioning |
| **[19]** | De Rossi et al., ERC-8004 Trustless Agents, 2025 | DIGEST-LEVEL | **W1** | The three-registry pattern; 0–100 scores with evidence URIs; validation hooks. **Exposed:** ISetC is derived from this and Set C was never built, so nothing in the suite checks the derivation |
| [20] | Fedrecheski et al., SSI for IoT, GIoTS 2020 | DIGEST-LEVEL | W3 | Constrained-device framing |
| [21] | Chen, SCMS performance comparison, arXiv:2501.03237 | DIGEST-LEVEL | W2 | SCMS performance baseline |
| [22] | Dunphy, blockchain trilemma / Indy, arXiv:2204.05784 | DIGEST-LEVEL | W2 | Definition-anchor and accumulator placement in Indy; AnonCreds proof-size context; shard-vs-backbone trade-off framing |
| [23] | ERC-1056 | VERIFIED AT SOURCE via A6; standard text DIGEST-LEVEL | **W1** | Event-sourced design; `changed` pointer; `sigAuth`/`veriKey` delegate types underlying F11/F12 |
| [24] | ERC-4337 | DIGEST-LEVEL | W2 | Agent as account-abstraction principal (C14); paymaster-sponsored writes |
| [25] | LFDT, Indy on Besu joins did:indy | DIGEST-LEVEL | W2 | E1 substrate; QBFT finality; AnonCreds anchoring model |
| [26] | W3C DID Spec Registries | DIGEST-LEVEL | W3 | Method enumeration |
| [27] | MOBI VID I–II | DIGEST-LEVEL (via A17, A18) | **W1** | The credential families and issuer roles the build implements. **Exposed:** contribution C4 is a conformance mapping to a specification known only through the repository's own summary of it |
| [28] | IEEE 1609.2-2022 | **UNVERIFIED** | **W1** | The Tier 1 boundary. **Most exposed source in the suite:** see §5.2 |

### 4.2 New sources H1–H48

Grouped by kind. The "replaces" column is the crosswalk; §6 inverts it.

**Standards and specifications**

| H# | Source | State | W | Used for | Replaces |
|---|---|---|---|---|---|
| H1 | W3C Bitstring Status List v1.0 | DIGEST-LEVEL | W2 | Status-list revocation; epoch digests; gate-side snapshots | 01/03/06/08 NEW-1, 07 NEW-5 |
| H2 | W3C Data Integrity BBS Cryptosuites v1.0 (`bbs-2023`) | DIGEST-LEVEL | W2 | Unlinkable presentations; signed-then-anchored | 01 NEW-6, 02 NEW-7, 03 NEW-2 |
| H3 | EIP-2929 (state-access gas costs) | DIGEST-LEVEL | **W1** | SSTORE 20,000 / SLOAD 2,100 cold, 100 warm — the constants under every cost model in 01 §7 and 03 §8 | 01/03/06 NEW-2, part of 02 NEW-2 |
| H4 | EIP-4844 (blob transactions) | DIGEST-LEVEL | W3 | Cheap ephemeral data; noted, not relied on | 01 NEW-3, 03 NEW-4 |
| H5 | EIP-2028 calldata pricing; EIP-1559 lineage; Yellow Paper LOG gas | DIGEST-LEVEL | W2 | 16 gas/non-zero byte; 8 gas/byte event data | 06 NEW-3, 08 NEW-12 |
| H6 | EIP-2537 (BLS12-381 precompiles) | DIGEST-LEVEL | W2 | Whether BBS+ verification is on-chain-feasible (02 §2.3) | 02 NEW-9 |
| H7 | ERC-2771 (native meta-transactions) | **UNVERIFIED** | W2 | The sponsored-write path (01 §5.3) | 01 NEW-11 |
| H8 | ERC-7579 (modular smart accounts) | DIGEST-LEVEL | W2 | Agent policy modules at L1 (C14) | 03 NEW-10 |
| H9 | RFC 3161 (time-stamp protocol) | **UNVERIFIED** | W3 | Two-source timestamping (01 §6.4) | 01 NEW-12 |
| H10 | RFC 8785 (JSON Canonicalization Scheme) | **UNVERIFIED** | W2 | Canonicalisation migration path; the build's own canonicalisation deviates | 01 NEW-13 |
| H11 | RFC 8446 TLS 1.3; RFC 9266 channel bindings | DIGEST-LEVEL | W2 | Channel-binding analogy (08 §2.5, §6) | 08 NEW-3 |
| H12 | RFC 9420 Messaging Layer Security | DIGEST-LEVEL | W2 | Tree-based group keys for swarms (08 §3(f)) | 08 NEW-5 |
| H13 | RFC 9180 HPKE | DIGEST-LEVEL | W2 | Escrow-token encryption; DIDComm ECDH-ES basis | 08 NEW-9 |
| H14 | IETF CFRG, The BBS Signature Scheme (draft) | DIGEST-LEVEL | W2 | Proof and signature sizes (02 §2.3) | 02 NEW-6 |
| H15 | IETF OAuth WG, SD-JWT VC profile | DIGEST-LEVEL | W3 | Maturity of the SD-JWT line | 02 NEW-3 |
| H16 | DIF DIDComm Messaging v2 | DIGEST-LEVEL | W2 | Envelopes and key-agreement types (08 §6) | 08 NEW-6 |
| H17 | Noise Protocol Framework (Perrin) | DIGEST-LEVEL | **W1** | The XX pattern and key schedule the I2I channel design adopts (08 §2.4) | 08 NEW-2 |
| H18 | Signal Double Ratchet specification | DIGEST-LEVEL | W2 | Symmetric and DH ratchet for forward secrecy (08 §2.6) | 08 NEW-4 |
| H19 | ISO/IEC 18013-5 (mobile driving licence) | DIGEST-LEVEL | **W1** | Data-element compatibility of the licence credential. **Exposed:** 07's claim that the design is compatible with the mDL standard is untested | 07 NEW-3 |
| H20 | ETSI TR 103 460 / TS 103 759 (C-ITS misbehaviour reporting) | **UNVERIFIED** | W2 | The misbehaviour-reporting path (09 §2.5) | 09 NEW-11 |
| H21 | 3GPP TS 23.287 / PC5 latency studies | **UNVERIFIED** | W2 | Transport budgets, stated as targets only (08 §3(e)) | 08 NEW-11 |

**Regulation**

| H# | Source | State | W | Used for | Replaces |
|---|---|---|---|---|---|
| H22 | GDPR, Regulation (EU) 2016/679 (Art. 5(1)(c), 17, 25; Recital 26) | DIGEST-LEVEL | **W1** | Whether a per-credential content hash is personal data; erasure by revoke-and-delete; data minimisation. **Exposed:** a substantive legal claim in 01 §6, 02 §1.2, 03 §7.4 and 07 §1.4, made without reading the articles | 02 NEW-1, 03 NEW-9, 07 NEW-4 |
| H23 | Regulation (EU) 2024/1183 (eIDAS 2.0) | DIGEST-LEVEL | W2 | Direction of travel: holder-held attestations, registries authoritative | 03 NEW-8, 07 NEW-1 |
| H24 | EUDI Wallet Architecture and Reference Framework | DIGEST-LEVEL | W2 | Trust lists; admitted formats; unlinkability requirement; no PII on ledger | 02 NEW-4, 07 NEW-2 |

**Cryptography and distributed systems**

| H# | Source | State | W | Used for | Replaces |
|---|---|---|---|---|---|
| H25 | Merkle, A digital signature based on a conventional encryption function, CRYPTO 1987 | DIGEST-LEVEL | **W1** | Batch roots and inclusion proofs — the construction behind the measured 11:1 result and every bundle anchor in the suite | 01 NEW-4, 03 NEW-6, 06 NEW-10, 07 NEW-9 |
| H26 | Au, Susilo, Mu (2006); Camenisch, Drijvers, Lehmann (2016) — BBS+ | DIGEST-LEVEL | W2 | The BBS+ scheme itself (02 §2.3) | 02 NEW-5 |
| H27 | Douceur, The Sybil Attack, IPTPS 2002 | DIGEST-LEVEL | **W1** | Sybil resistance is impossible without a certifying authority or a participation cost — the hinge of the endorsement-and-reputation argument in 06 §2.2 and 09 §3.2, §4.3 | 06 NEW-6, 09 NEW-5 |
| H28 | Kamvar, Schlosser, Garcia-Molina, EigenTrust, WWW 2003 | DIGEST-LEVEL | W2 | Transitive attester weighting with pre-trusted roots; the analogue of endorsed scorers | 06 NEW-7, 09 NEW-6 |
| H29 | Hardy, The Confused Deputy, ACM SIGOPS OSR 1988 | DIGEST-LEVEL | W2 | The delegation-chain crux and the guard in 04 §3.3, 07 §2.7, 08 §3(h) | 07 NEW-7, 08 NEW-10 |
| H30 | Semaphore (ZK group membership and signalling) | DIGEST-LEVEL | W2 | Anonymity-set bound for the pseudonym-to-verinym link proof (06 §2.2) | 06 NEW-13 |
| H31 | Poon & Dryja, Lightning Network, 2016 | **UNVERIFIED** | W3 | The state-channel payment rail option (06 §3) | 06 NEW-11 |

**Federated learning and robust aggregation**

| H# | Source | State | W | Used for | Replaces |
|---|---|---|---|---|---|
| H32 | McMahan et al., Communication-efficient learning of deep networks from decentralized data, AISTATS 2017 (FedAvg) | DIGEST-LEVEL | **W1** | The definition of federated learning and sample-count weighting on which all of 09 §2–§3 is built | 06 NEW-5, 09 NEW-1 |
| H33 | Kairouz et al., Advances and Open Problems in Federated Learning, FnT ML 2021 | DIGEST-LEVEL | **W1** | The open-problems framing (robustness, non-IID data, update privacy, intermittent participation) that 09 claims reputation addresses | 06 NEW-8, 09 NEW-2 |
| H34 | Blanchard et al., Krum, NeurIPS 2017 | DIGEST-LEVEL | **W1** | The Byzantine-tolerance bound and selection rule; 09 §3.1's claim that robust aggregation gets cheaper when low-reputation contributors can be excluded first | 06 NEW-9, 09 NEW-3 |
| H35 | Yin et al., Byzantine-robust distributed learning (trimmed mean, median), ICML 2018 | DIGEST-LEVEL | W2 | Coordinate-wise robust estimators (09 §3.1, §6.5) | 09 NEW-4 |
| H36 | Bagdasaryan et al., How to backdoor federated learning, AISTATS 2020 | **UNVERIFIED** | W2 | Model-replacement and sleeper attacks (09 §3.1, §8) | 09 NEW-8 |
| H37 | Fung, Yoon, Beschastnikh, FoolsGold, RAID 2020 | **UNVERIFIED** | W2 | Sybil-update similarity as a screen (09 §3.2, §8) | 09 NEW-9 |
| H38 | Bonawitz et al., Practical secure aggregation, CCS 2017 | **UNVERIFIED** | W2 | Secure-aggregation shares as the contribution object when update privacy is required (09 §6.2) | 09 NEW-10 |

**Infrastructure, platforms, and protocols**

| H# | Source | State | W | Used for | Replaces |
|---|---|---|---|---|---|
| H39 | IPFS (Benet 2014) / Arweave whitepaper | **UNVERIFIED** | W2 | Content-addressed storage for credential bodies and evidence bundles | 01 NEW-5, 03 NEW-7 |
| H40 | Chainlink decentralised oracle whitepaper | DIGEST-LEVEL | W2 | The oracle-set pattern behind the 2020 paper's distributed oracles; fiat settlement attestation; ground truth for scoring | 03 NEW-5, 06 NEW-4, 09 NEW-7 |
| H41 | Trust over IP governance stack | DIGEST-LEVEL | W2 | Vocabulary for the endorsement/trust-registry layer and escrow governance | 03 NEW-11, 07 NEW-6 |
| H42 | LFDT AnonCreds v1.0 spec; AnonCreds v2 (BBS+) working documents | DIGEST-LEVEL | **W1** | AnonCreds as the Set B coverage ceiling — the comparator for the thesis's central finding about `createPresentation` | 02 NEW-8 |
| H43 | mattrglobal/bbs-signatures; pairing_crypto | DIGEST-LEVEL | W3 | Implementation availability for stage (b) of 02 §10 | 02 NEW-10 |
| H44 | BC Verifiable Organizations Network | DIGEST-LEVEL | W3 | A deployed AnonCreds-lineage registry; jurisdictional relevance | 02 NEW-11 |
| H45 | Google A2A protocol | DIGEST-LEVEL | W2 | Agent discovery cards and task lifecycle; the A2A phases in the memo stance | 08 NEW-7 |
| H46 | Anthropic Model Context Protocol specification | DIGEST-LEVEL | W2 | Capability-gated tool access; tool schemas as channel payload | 06 NEW-12, 08 NEW-8 |
| H47 | VehiclePassport, arXiv:2509.06133 | DIGEST-LEVEL | **W1** | 22 ms proof generation, sub-5 ms verification — **the only timing figure anywhere in the suite**, and therefore the sole external basis for every claim that Tier 2 ZK verification is feasible (05 §3.2, 06 §4.2, 01 §4.5) | 01 NEW-8, 06 NEW-14 |
| H48 | Torrens title system (general legal reference) | DIGEST-LEVEL | W3 | Register-conclusive title as the model for revoke-and-reissue (07 §3.2) | 07 NEW-8 |

## 5. The verification-debt register

This is the section document 00 §5 directs a reader to, and the list S3 §5.1 stood in for until now.

### 5.1 The eleven exposed claims (W1 and not verified at source)

Ordered by how much of the suite fails if the source does not say what the suite assumes.

| # | Source | W1 claim that depends on it | If it is wrong |
|---|---|---|---|
| 1 | **[28] IEEE 1609.2-2022** (UNVERIFIED) | The Tier 1 boundary: that SCMS authenticates basic safety messages and that SSI extends rather than replaces it | The thesis's framing sentence and all of 05 §2 are restated. Chapter 1's motivation is affected |
| 2 | **[6] Brecht et al., SCMS** (DIGEST-LEVEL) | The accountability gap — that SCMS pseudonymity precludes answering "what is the history of actions of vehicle V?" | The problem the thesis exists to solve is mis-stated. **This is the single most consequential item in the register** |
| 3 | **H47 VehiclePassport** (DIGEST-LEVEL) | That Tier 2 ZK verification is feasible, via 22 ms / sub-5 ms | **Superseded by internal measurement, 2026-10-15 — and contradicted.** The suite's own BBS+ figures (A29) are 93–116 ms to generate and 59–116 ms to verify, 4–5× slower than H47, which is enough to put the most selective policy at 232 ms of a 500 ms Tier 2 allowance. H47 should no longer be cited as a bound: different implementation, different hardware, different proof. The exposure has **inverted** — the risk is no longer that an unread source might not support the claim, but that the suite's own measurement does not support the claim the unread source was carrying. 05 §3.2 withdraws the affected sentence |
| 4 | **H22 GDPR** (DIGEST-LEVEL) | That per-credential content hashes may be personal data while definition hashes and accumulators are safely public | The privacy argument of 01 §6, 03 §7.4 and 07 §1.4 changes shape. A legal claim should not be DIGEST-LEVEL in a submitted thesis |
| 5 | **H3 EIP-2929** (DIGEST-LEVEL) | The SSTORE/SLOAD constants under every cost model | Cost models are recomputed. Low risk (the constants are widely replicated) but high reach |
| 6 | **H32/H33/H34 McMahan, Kairouz, Krum** (DIGEST-LEVEL) | That reputation addresses the **named open problems** of FL and that robust aggregation benefits from pre-filtering | *Reworded after Slice 1 (§5.4).* The **mechanism** is now internally evidenced (A24: gated 1.87 against 23.67 unweighted; ungated 27.59 against 24.35 unweighted), so 09's chain no longer rests on literature alone. What remains exposed is the **positioning**: that this mechanism answers problems the FL field has named, and that Krum's tolerance bound behaves as 09 §3.1 claims. If the literature says otherwise, 09 keeps its result and loses its place in the field |
| 7 | **H27 Douceur** (DIGEST-LEVEL) | That Sybil resistance requires a certifying authority or participation cost | The endorsement-as-Sybil-cost argument in 06 §2.2 and 09 §4.3 loses its foundation |
| 8 | **[27] MOBI VID I–II** (DIGEST-LEVEL, via the repository's own summary) | Contribution C4, the conformance mapping | A named contribution rests on a specification read only in paraphrase |
| 9 | **[11] + [19] agent sources** (DIGEST-LEVEL) | The agent generalisation and the Set C derivation | The agent half of the suite — the part S3 §6.2 already flags as least evidenced — also has unverified foundations |
| 10 | **H42 AnonCreds** (DIGEST-LEVEL) | That AnonCreds is the Set B coverage ceiling with native `createPresentation` | The thesis's central comparative finding needs restating |
| 11 | **H19 ISO/IEC 18013-5** (DIGEST-LEVEL) | That the licence credential is data-element compatible with the mDL standard | A compatibility claim in 07 is withdrawn |

**The pattern worth naming.** Items 1, 2, 8 and 10 are all sources that define *what the thesis is about* — the SCMS boundary, the accountability gap, the MOBI mapping, the AnonCreds ceiling. None has been read at source in this campaign. The suite has verified its own code thoroughly and its own premises hardly at all. That is the inverse of the usual failure and is arguably worse, because code can be re-run and a misread premise propagates silently into every document.

### 5.2 Prioritised reading list

Four sessions, in this order. Each discharges a block of the register.

1. **[28] IEEE 1609.2-2022 and [6] Brecht et al.** Settles items 1 and 2, i.e. the thesis's problem statement and its Tier 1 boundary. Nothing else in this list comes close in consequence. Output: a corrected framing paragraph for Chapter 1 and a verified §2 for document 05.
2. **H22 GDPR (Art. 5(1)(c), 17, 25; Recital 26) and H24 EUDI ARF.** Settles item 4 and firms up the regulatory sections of 03 and 07. A legal claim in a submitted thesis should be read at source as a matter of course.
3. **H32, H33, H34 (FedAvg, Kairouz, Krum) and H27 (Douceur).** Settles items 6 and 7 and converts document 09 — the suite's widest-reaching argument — from a chain of plausible links into a cited one.
4. **[27] MOBI VID I–II and H42 AnonCreds.** Settles items 8 and 10, the two named contributions (C4 and the `createPresentation` finding) that rest on paraphrase.

H47 (item 3) is deliberately not on this list: reading it would confirm a figure, but the figure is a substitute for a measurement the programme should take itself. It is discharged by Slice 1c and Slice 4 of 00 §7, not by reading.

### 5.3 Sources named but not read at all (UNVERIFIED)

Eleven: [28], H7, H9, H10, H20, H21, H31, H36, H37, H38, H39. Of these only [28] is W1. The remaining ten are W2 or W3 and support sentences that can be deleted without structural damage — which is the correct disposition if they are not read before submission. **The rule this register proposes: no UNVERIFIED source survives into the thesis. Either it is read, or the sentence it supports is cut.**

### 5.4 Measurement debt, restated by source

Distinct from source debt, and not dischargeable by reading. The full register is S3 §5.1. As first written, this section recorded three absences: no internal source for any latency figure, none for Set C costs, and none for any generated proof. **Slice 1 (2026-10-14) changed two of the three** (A21–A33 below):

| Absence | State after Slice 1 |
|---|---|
| Latency | **Chain latency instrumented, not measured** (A12 carries `latencyMs` at schema v1.1; A25–A28 record it, but in-process values are a lower bound). **Cryptographic latency is now genuinely measured** (A29, Slice 2b): 93–116 ms to generate a BBS+ proof and 59–116 ms to verify, laptop WASM. This is the suite's first internal timing result of any kind, and it **contradicts H47** by 4–5× — see §5.1 item 3, now rewritten |
| Set C costs | **Harness figures exist** (A23: C1 83,493–117,693 gas). They are explicitly not ERC-8004 costs, so §5.1 item 9's exposure on [19] is unchanged for *cost comparison* but discharged for *mechanism* — C1–C4 now execute |
| Generated proof | **Discharged for stages (b) and (c).** (A29) BBS+ proofs generated, sized (384–640 B), verified against the issuer's public key alone, unlinkability observed. (A30) A Groth16 range predicate proven *and verified on-chain*: 250,283 gas for `admit`, 0 as a view. **This retires the suite's longest-standing digest-level quantity** — the "≈200–350K gas Groth16 verification" of K-HDA-6 now has a measured point at the low end of its own range, for a two-signal circuit inclusive of a storage write. **Open:** stage (d), AnonCreds comparison and accumulator revocation privacy; and the *warm* verification figure — 645.3 ms is a cold first call, and whether the warm figure is tens of milliseconds decides whether predicate proofs are usable at Tier 2 at all (05 §3.2.1 and its open question 5; measurement debt, so it is registered in S3 §5.1 rather than here) |

The one item that improved materially is §5.1 item 6. Document 09's chain — collective computation needs reputation, reputation needs Sybil-resistant identity — now has **internal evidence** (A24, A28): with an entitlement gate on attesters the reputation-weighted error was 1.87 against 23.67 unweighted; without the gate it was 27.59 against that configuration's own 24.35 unweighted, i.e. *worse than not weighting at all*. The mechanism is observed on a toy model. What is still unread is the FL literature itself (H32–H34), so the narrower claim that reputation addresses the **named open problems** of federated learning — Kairouz et al.'s framing, and Krum's tolerance bound — is still carried on digest-level sources. §5.1 item 6 is therefore reworded rather than discharged: the *mechanism* is evidenced, the *literature positioning* is not.

## 6. Crosswalk: per-document `NEW-n` to H-numbers

For reading the nine documents that were not rewritten. Left column is what the document says; right is what it means.

| Doc | NEW-1 | NEW-2 | NEW-3 | NEW-4 | NEW-5 | NEW-6 | NEW-7 | NEW-8 | NEW-9 | NEW-10 | NEW-11 | NEW-12 | NEW-13 | NEW-14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | H1 | H3 | H4 | H25 | H39 | H2 | — | H47 | — | — | H7 | H9 | H10 | — |
| 02 | H22 | H3+H5 | H15 | H24 | H26 | H14 | H2 | H42 | H6 | H43 | H44 | — | — | — |
| 03 | H1 | H2 | H3 | H4 | H40 | H25 | H39 | H23 | H22 | H8 | H41 | — | — | — |
| 06 | H1 | H3 | H5 | H40 | H32 | H27 | H28 | H33 | H34 | H25 | H31 | H46 | H30 | H47 |
| 07 | H23 | H24 | H19 | H22 | H1 | H41 | H29 | H48 | H25 | — | — | — | — | — |
| 08 | H1 | H17 | H11 | H18 | H12 | H16 | H45 | H46 | H13 | H29 | H21 | H5 | — | — |
| 09 | H32 | H33 | H34 | H35 | H27 | H28 | H40 | H36 | H37 | H38 | H20 | — | — | — |

Documents 04, 05, 10, 11, S2 and S3 cite H-numbers or bracketed thesis numbers directly and need no crosswalk. Document 02's `NEW-2` conflates the EVM gas schedule generally and maps to both H3 and H5.

## 7. How to cite from this suite

Three rules, to keep the next pass from re-creating K-HDA-10.

1. **Cite [n] for thesis-list sources and Hn for everything else.** A bare `NEW-n` is not a citation; it is a per-document note that means nothing outside its document.
2. **Carry the verification label with the number on first use in any new document**, and take it from this index rather than re-deciding it. A source that is DIGEST-LEVEL here is DIGEST-LEVEL everywhere until someone reads it and updates §4.
3. **Cite A-numbers for measured claims**, never a prose restatement of a figure from a sibling document. Every gas number in the suite is in A1–A4 and A21–A33; a figure without an A-number behind it is a hypothesis.

---

## Sources used in this document

| Id | Source | Verification state | How used |
|---|---|---|---|
| — | The "Sources used in this document" tables of 01, 02, 03, 06, 07, 08, 09, 10, 04, 05, S3 | VERIFIED AT SOURCE (read in full for this document) | The entire merged index; the collision analysis of §1 and §6 |
| A19 | `_CONTEXT_BRIEF.md` §5, §9, §10 | VERIFIED AT SOURCE | The thesis list [1]–[28] verbatim; the measured-number allowlist; the suggested-new-sources list; the three verification labels |
| A14, A15 | `docs/FINDINGS.md`, `BUILD_LOG.md` | VERIFIED AT SOURCE | A-series artefact descriptions |
| — | HDA 00 §5, §9; S3 §4, §5 | VERIFIED AT SOURCE | What this register was asked to contain; the K-ledger it extends |
| — | The individual literature items indexed in §4 | **As labelled per row** | This document does not itself read any source; it records and weights the state in which the suite left each one |

**A note on this document's own verification state.** S1 is an index, and its claims are of two kinds. Claims about *what the suite says* are VERIFIED AT SOURCE: every row was built by reading the sibling documents' tables. Claims about *what a source says* are inherited, not checked — this document read no literature. The weights in §2 and §4 are the author's judgement about which claims depend on which sources, and they are the most contestable content here; a reader who disagrees with a W-assignment is disagreeing about what the suite's arguments rest on, which is a useful disagreement to have early.

## Registry delta rows

| Content Block | T | Source | Ch. | Ready | Notes and status |
|---|---|---|---|---|---|
| Weighted reference index, merged across the suite ([1]–[28], H1–H48, A1–A20) | B | S1 §3–§4 | Admin; all | 85% | Provisional H-numbers; merges into the R-series with the Systematic Review v13.1 |
| Three-level weighting scale (W1/W2/W3 by consequence of misreading) | C | S1 §2 | Admin; 5 (limitations) | 80% | Method is reusable for the whole programme's bibliography |
| **The eleven exposed claims (W1 and unverified)** | B | S1 §5.1 | 5 §5.6 | 90% | The operative output of this document; directly usable as limitations prose |
| Prioritised four-session reading list | B | S1 §5.2 | Admin | 90% | Settles items 1–2, 4, 6–7, 8 and 10 in that order |
| Finding: the suite verified its code and not its premises | A/C | S1 §5.1 closing | 5 §5.6 | 75% | Pairs with S3 §6.5; a diagnosis of the programme's verification habits |
| `NEW-n` → H-number crosswalk for the nine un-rewritten documents | B | S1 §6 | Admin | 95% | Remedy for K-HDA-10 |
| Citation rules for subsequent passes | C | S1 §7 | Admin | n/a | Process proposal |
| **K-HDA-10** (per-document `NEW-n` series collide across the suite) | B | S1 §1 | Admin | n/a | New correction; added to the S3 §4 ledger |

## Open questions for the researcher

1. **Will the four reading sessions of §5.2 happen before the thesis prose is frozen?** Items 1 and 2 define the thesis's problem statement. If they are not read, Chapter 1 is written on a paraphrase of SCMS, and that is the kind of thing an examiner in this field will notice immediately.
2. **Does the no-UNVERIFIED-source rule of §5.3 stand?** Accepting it means either reading ten more sources or cutting the sentences they support. The second is cheap and is probably correct for all ten.
3. **Are the W1 assignments right?** Eleven sources are claimed to be load-bearing. If any of 04's or 09's arguments actually rest on something marked W2, this register is understating the exposure — and the author of both the arguments and the register is poorly placed to tell.
4. **When does the H-series merge into the R-series?** Until it does, this suite and the Systematic Review v13.1 suite have disjoint numbering, and any document that cites across the two will be ambiguous. The merge is bookkeeping, it is not hard, and it is exactly the kind of work S3 §6.5 observes gets dropped.
5. **Should contribution C4 be restated?** §5.1 item 8 notes that the MOBI conformance mapping rests on the repository's own summary of MOBI VID I–II rather than on the specification. Either the specification is obtained, or C4 is phrased as conformance to the programme's reconstruction of it.
