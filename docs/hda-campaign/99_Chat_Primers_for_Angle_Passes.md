CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Chat Primers for the Angle Passes**

**Paste-ready, self-contained prompts that let each per-angle deep pass be run in the chat model and still return a suite-compliant document**

Document 16 of 16 · Hybrid Data Architecture (HDA) Campaign · Companion · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type B tables-data (process artefact) → Chapter 2, §2.4 (methodology appendix); no thesis-body prose*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 1. How to use this document

The general pass (documents 00–11) was written in the code environment, where the author can read trace files, run the compliance suite, and verify numbers at source. The angle passes that follow are deeper and narrower, and the researcher may prefer to run several of them in the chat model, where long argued prose and iterative critique are cheaper. A fresh chat carries none of the programme's memory, so each primer below must carry it: the specification, the families, the tiers, the only measured numbers that exist, the suite convention, and the hard rules. A primer that omits any of these produces a document that reads well and fails the suite.

The mechanics are simple. For every angle pass, paste §2 (the Programme Context Block) first, then the primer for that angle (§3), then attach the input files the primer names. The chat model's output must be a single Markdown document with the suite title block and the three closing sections; the acceptance checklist in each primer is what the researcher applies before the document is committed under `docs/`. §4 gives the primer for maintaining the three support documents, and §5 says which angles cannot be completed in chat at all because they produce measurements, and how a chat pass hands measurement work back to the command-line agent as a work order.

Nothing in this document is new analysis; it is compression. Where a primer states a fact, the fact was taken from the Context Brief of this suite, which was itself verified at source on 2026-09-03; where a primer names a planned artifact, the name is the one fixed in 00 and 10, and the artifact's status is "under construction" until 10 says otherwise.

---

## 2. Programme Context Block (prepend verbatim to every primer)

> **CVIN-SC HDA CAMPAIGN — CONTEXT BLOCK v1.0 (2026-09-03).** You are an author in the CVIN-SC Research Programme (Nikhil Prakash, MASc, UBC ECE; supervisors Dr. Chen Feng and Dr. David G. Michelson). The thesis, *Towards a Minimal Function Specification for Blockchain-Based Self-Sovereign Identity in Connected and Autonomous Systems*, evaluates blockchain-based self-sovereign identity (SSI) for connected and autonomous vehicles (CAVs) and, by generalisation, AI agents. Five chapters: 1 Introduction (the SCMS accountability gap; CVIN 2020 lineage; extension-not-replacement) · 2 Background and Methodology (Allen's ten principles; W3C DID Core 1.0 and VC Data Model; the twelve-function derivation; Set A/B; the three-tier latency framework) · 3 Standards Inventory · 4 Evaluation and Results · 5 Discussion. Contributions are numbered C1–C15; the ones you will most often cite are C2 (IMinimalSSI interface), C3 (Set A/B decomposition), C6 (three-tier latency framework), C10 (ZKP and selective disclosure), C11 (LFDT convergence), C12–C13 (intersectional benchmark and minimum-cost composite, Family F), C14 (I2I agent identity wrapper), C15 (I2I bridging paper).
>
> **Framing you must reuse and never contradict.** SCMS (IEEE 1609.2) governs Tier 1 basic safety message authentication; SSI *extends* it for Tiers 2 and 3. The accountability gap: SCMS pseudonymity cannot answer "what is the history of actions taken by vehicle V?"; a blockchain-anchored decentralised identifier (DID) gives a tamper-evident key-material history while zero-knowledge proof (ZKP) presentations keep routine disclosure minimal. Tiers: **Tier 1 <100 ms** (collision avoidance, BSM — DLT out of scope) · **Tier 2 100–500 ms** (charging session initiation, toll authorisation, parking, V2I service registration, cooperative manoeuvres — the primary DLT target, viable if edge-deployed) · **Tier 3 >500 ms** (registration, type approval, licensing, fleet, insurance, history). The central empirical finding: **no EVM standard natively implements createPresentation (F8)**; EVM optimises anchoring (Set A) and defers selective disclosure off-chain; LFDT/AnonCreds implements native ZKP presentations off-chain and anchors only credential definitions and revocation accumulators (AnonCreds is the Set B ceiling, 12/12). Supervisor memos fix the stance: on-chain registries for discovery and revocation; content and logs off-chain with on-chain integrity anchors; explicit governance (issuer roles, endorser sets, key rotation); off-chain verification avoids block-time delays; only lifecycle events and anchors on-chain; cache invalidation synchronised with revocation state. CVIN 2020 concepts that must stay testable: dual identity modes (public/pairwise DIDs), Local CVINs derived from a Global CVIN via ID Porting Protocols, distributed oracles, RSUs as edge servers, sidechains anchored to a backbone. Three framework properties: finality as immutability; hash-on-chain as integrity without disclosure (with the GDPR nuance that per-credential content hashes may be personal data while credential-definition hashes and accumulators are safely public); the forensic audit trail as accountability primitive.
>
> **The specification (normative; never alter).** Interface `IMinimalSSI.sol`, twelve functions: **Set A** F1 createDID · F2 resolveDID (view, never reverts) · F3 updateDID · F4 deactivateDID (irreversible, still resolvable) · F9 addVerificationMethod · F10 removeVerificationMethod (never the last key) · F11 addDelegate (sigAuth, veriKey) · F12 validDelegate (view). **Set B** F5 issueCredential (**content off-chain, only the hash on-chain**) · F6 verifyCredential (view: valid, issuer, revoked, expired) · F7 revokeCredential (issuer-only, idempotent, irreversible) · F8 createPresentation (holder, credentialIds, challenge, domain; challenge replay prevention). **Set C** (optional, ERC-8004-derived): C1 attestReputation · C2 getReputation · C3 requestValidation · C4 validationStatus. **Governance extension** (spec §6, used by this campaign): G1 registerIssuer · G2 endorseIssuer · G3 revokeEndorsement · G4 isEndorsed. Extensions live beside the interface and never change its signatures, errors, or events.
>
> **Families and options.** A Lightweight (ERC-1056, ERC-1155) · B Token-as-identity (ERC-721, ERC-6551) · C Contract account/claims (ERC-725, ERC-725xy/735, ERC-4337, EIP-7702) · D Agent registry (ERC-8004, mainnet 2026-01-29) · E Purpose-built SSI (Indy-on-Besu, Identus, AnonCreds, plus CREDEBL, Paladin, DIDComm v2, ACA-Py/Credo-TS) · **F CVIN Combined = Stage 3 synthesis output only, never a Stage 1 sandbox.** Sandbox options O1 ERC-1056 · O2 ERC-721 · O3 ERC-725 · O4 ERC-725xy · O5 ERC-1155 · O6 ERC-4337 · O7 ERC-8004 · O8 LFDT/Indy-on-Besu. Set A scoring anchors (/24): ERC-1056 23 · LFDT 22 · ERC-725 20 · ERC-725xy 20 · ERC-4337 18 · ERC-721 15 · ERC-8004 15. **Only O1 is confirmed live**; all others are prior evaluation pending confirmation.
>
> **The only measured numbers you may cite as measured** (sandbox v1.3, O1_ERC1056, scenario S1, Hardhat local EVM, solc 0.8.24, trace `traces/i2i_O1_ERC1056_1780620182135.jsonl`):
>
> | Function | F | Gas (measured) |
> |---|---|---|
> | createDID (Registry / IdentityA / IdentityB) | F1 | 178,935 / 161,835 / 161,823 |
> | issueCredential | F5 | 130,163 |
> | addVerificationMethod | F9 | 59,607 |
> | addDelegate (OBU, sigAuth, 3600 s) | F11 | 54,227 |
> | createPresentation | F8 | 62,441 |
> | revokeCredential | F7 | 32,980 |
> | removeVerificationMethod | F10 | 36,478 |
> | updateDID | F3 | 44,760 |
> | deactivateDID | F4 | 55,127 |
> | resolveDID, verifyCredential, validDelegate | F2, F6, F12 | view; gas-free reads |
>
> Recorded deviation: createDID ≈162–179K against a <100K target, caused by explicit-DID storage. Spec gas targets (ERC-1056 / ERC-725, e.g. createDID <100K / <600K, createPresentation <150K / <200K) are **hypotheses, not results**. External figures usable only with the label **DIGEST-LEVEL** and a source: Groth16 on-chain verification ≈200–350K gas; calldata 16/4 gas per byte; SSTORE new slot 20,000; SLOAD ≈2,100 cold / 100 warm; LOG data 8 gas/byte; EIP-4844 blobs ≈18-day retention; VehiclePassport (arXiv:2509.06133) 22 ms proof / sub-5 ms verification; Canada ≈33 M vehicles. Everything else external is **UNVERIFIED** until named with its source. **Any quantity you have not been given is a target, a budget, or a formula with variables — never a result.**
>
> **The build this campaign references (names final; status "under construction" until 10 says otherwise):** `contracts/governance/EndorsementRegistry.sol` (G1–G4; verification policy = F6 valid AND issuer endorsed for the type at issuance time) · `contracts/credentials/CredentialTypeRegistry.sol` (types VID_BIRTH, VEHICLE_REGISTRATION, DRIVER_LICENCE, and the eleven MOBI VID II lifecycle event types) · `lib/vid/` (credential builders, canonical JSON, keccak hashing, presentation builders, local holder wallet and verifier) · `scenarios/run_vid_minimal.js` (S7) · `scenarios/run_vid_lifecycle.js` (S8) · `test/vid.js`. The VID layer sits above IMinimalSSI and never alters it. Traces are JSONL per `traces/SCHEMA.md` (seq, impl, ts, kind, fn, fnId, identity, txHash, gasUsed, events, note) and are the only admissible source of new measurements.
>
> **Suite convention (Deliverable Suite Architecture v1.0).** Every document carries the programme title block (title; subtitle; "Document N of M"; suite and class; version; the full companion line; registry classification Type A prose / B tables-data / C framing with chapter target). Every primary document ends with three sections: **Sources used in this document** (R# or NEW-n · source · VERIFIED AT SOURCE / DIGEST-LEVEL / UNVERIFIED · how used), **Registry delta rows** (Content Block · T · Source · Ch. · Ready % · Notes), and **Open questions for the researcher** (each load-bearing: only the researcher can decide it). Citations are IEEE-numbered; thesis references [1]–[28] keep their numbering; new sources are NEW-n. Register: academic, argued; each section opens with the claim, then reasoning, then evidence or the test that would produce it; prose for argument, tables for comparisons; numbered headings; no emoji. Cross-reference sibling documents by number ("see 02 §4") rather than duplicating them. Every scenario names actors (DIDs), objects, the F/C/G-tagged function sequence, the tier, on-chain/off-chain placement of every datum, failure modes, the "problems solved / further functionality" tail, and the test that would validate it. Today is 2026-09-03.

*(≈760 words. Keep the block intact; do not summarise it further when pasting.)*

---

## 3. The ten angle primers

Each primer assumes the Context Block has been pasted immediately above it. The deliverable file names below follow a proposed follow-on series, **HDA Angle Passes, Suite v1.1**, in which each angle document is a primary deliverable `A<n>_<name>.md` under `docs/hda-angle-passes/`, deepening the general-pass document it names. The series name and numbering are a decision the researcher must fix before the first angle document is produced (Suite Architecture, Part III step 1); see the open questions in §7.

The "standing rules" paragraph is deliberately repeated in every primer rather than referenced, because a chat that is asked to produce 8,000 words will lose a rule it was only pointed at.

### 3.1 Primer A1 — On/off-chain placement deep pass with a per-standard scoring rubric

**Objective.** Deepen 01 into a decision instrument: for every function F1–F12, every Set C and governance function, and every identity object (DID document, key material, delegation, credential content, credential anchor, revocation state, presentation commitment, endorsement, reputation attestation, oracle report, channel state), produce a placement verdict (on-chain state, on-chain event only, anchor-only, off-chain signed, off-chain unsigned) per standard family, and score each family on a rubric whose weights are explicit.

**Inputs to attach.** `01_On_Off_Chain_Data_Architecture_and_Anchoring.md`; `03_Best_of_Both_Worlds_Hybrid_Design.md` (§ on tiered placement only); `SSI-Minimal-Function-Specification-Formal.md`; `CVIN_Building_Paths_v1-1_SixLevel.docx` (plain text) for the family profiles; `traces/i2i_O1_ERC1056_1780620182135.jsonl`; `traces/SCHEMA.md`; Memo A and Technical Memo 2 (PDF).

**Deliverable.** `A1_Placement_Deep_Pass_and_Scoring_Rubric.md` · primary deliverable of the angle series, deepening 01 · 7,000–10,000 words · Type B with Type A argument sections · required sections: 1 Claim and scope; 2 The placement vocabulary (five placement classes, defined operationally by what a verifier must read and what a writer must pay); 3 Read paths and write paths per function, with a cost formula in variables (bytes, SSTORE count, LOG bytes, calldata) and the O1 measured values substituted only where they exist; 4 Per-object placement matrix; 5 The scoring rubric (criteria, weights, scoring rule, tie-break) and its application to the six families; 6 Sensitivity analysis (which weight flips the ranking); 7 What the rubric cannot see (GDPR erasure, finality, chain faults); 8 Demonstration plan (which trace assertions on S7/S8 would confirm each placement); closing sections.

**Standing rules.** Real numbers only from the Context Block table or from a trace file you have been given; every other quantity is a target, budget, or formula. IMinimalSSI is normative; propose no signature, error, or event changes. Family F is a Stage 3 synthesis, never a sandbox. Label external figures DIGEST-LEVEL or UNVERIFIED with a source. IEEE numbering [1]–[28] carried forward; NEW-n for additions. Cross-reference 01, 02, 03 by number; do not restate them. Title block and the three closing sections are mandatory.

**Load-bearing questions the pass must return.** (a) Which rubric weight vector does the researcher endorse as the thesis's, given that it determines the Family F composite of C13? (b) Is a per-credential content hash on a public chain acceptable under the researcher's GDPR reading, or must the anchor be a salted commitment? (c) Does the researcher want the rubric scored against the eight sandbox options or the six families?

**Acceptance checklist.** Title block verbatim with "Document N of M" for the angle series · every table cell in the matrix carries a placement class, not prose · no gas number appears that is not in the Context Block table or a named trace line · rubric weights sum to a stated total and the sensitivity section flips at least one · closing three sections present · each open question fails the "could the author answer it alone" test · word count within range.

### 3.2 Primer A2 — ZKP deep pass with a benchmark protocol

**Objective.** Deepen 02 into (i) a comparative treatment of the proof systems that matter to the thesis (CL/AnonCreds v1, BBS+/AnonCreds v2, SD-JWT salted-digest disclosure, Groth16/PLONK circuits, Semaphore-style membership) along the axes of proof size, prover time, verifier cost on-chain and off-chain, unlinkability, revocation privacy (status list versus accumulator), and setup trust, and (ii) a benchmark protocol precise enough that the command-line agent can execute it without design decisions.

**Inputs to attach.** `02_ZKP_and_Verifiable_Data.md`; `01` §§ on anchoring and integrity; the VC layer description from `2_w3c-ssi-layer/` (SD-JWT-style salted claim digests, EIP-191 Data Integrity proofs); `CVIN_Family_E_Expansion_v2-0_Full.docx` (plain text; AnonCreds sections); the thesis reference entries [12], [13], [14].

**Deliverable.** `A2_ZKP_Deep_Pass_and_Benchmark_Protocol.md` · primary, deepening 02 · 7,000–10,000 words · Type A/B · required sections: 1 Claim; 2 What must be proven in each tier (predicate catalogue: age/class of licence, registration validity, non-revocation, endorsement chain, reputation threshold, set membership); 3 Proof-system comparison matrix with every cell labelled by verification state; 4 Revocation privacy: status list versus accumulator, staleness window, verifier cost, holder cost; 5 On-chain versus off-chain verification with auditable anchoring, including the GDPR nuance; 6 CAV and agent application (one worked predicate each, F8 challenge binding stated); 7 **Benchmark protocol**: hypotheses in falsifiable form; independent variables; fixed environment (Hardhat local, solc 0.8.24, optimizer 200); metrics and units; trace fields to add without breaking SCHEMA.md (a versioned extension); number of runs; acceptance thresholds stated as targets; exact assertions the trace must satisfy; 8 Demonstration plan; closing sections.

**Standing rules.** As in A1. In addition: proof-generation and verification timings from the literature are DIGEST-LEVEL at best; the sandbox has produced **no** ZKP measurement, and the document must say so in its first section.

**Load-bearing questions.** (a) Which proof system does the thesis commit to for Tier 2, given that only one can be benchmarked before submission? (b) Does the researcher accept a Hardhat-local Groth16 verifier gas measurement as evidence for C10, or require an L2/zkEVM run? (c) Is revocation privacy (accumulators) a thesis claim or future work?

**Acceptance checklist.** Every comparison cell labelled · benchmark protocol has hypotheses, variables, environment, metrics, run count, thresholds, and trace assertions, in that order · no timing or gas number presented as measured · SCHEMA.md extension is versioned, not silent · closing sections · questions load-bearing.

### 3.3 Primer A3 — Hybrid design deep pass toward the Family F specification

**Objective.** Take 03 from an argued design to a specification-grade description of Family F (CVIN Combined) as a Stage 3 output: the tiered placement policy, the anchor/cache/attest pattern, the degraded modes, the security/privacy/integrity envelope, the governance (endorser sets), and a realisability plan that says which existing option contributes which mechanism — without building anything.

**Inputs to attach.** `03_Best_of_Both_Worlds_Hybrid_Design.md`; `01` and `02` closing sections; `A1` and `A2` outputs if they exist; `CVIN_Native_Sandbox_Build_and_Verification_Methodology_v1-0.docx` (plain text; the three-stage method); `METHODOLOGY.md`; Memo B.

**Deliverable.** `A3_Family_F_Specification_Draft.md` · primary, deepening 03 · 7,000–10,000 words · Type A/B/C · required sections: 1 Claim (Family F is the minimum-cost composite that satisfies the placement rubric under the tier constraints); 2 Normative language (MUST/SHOULD, defined) and the statement that this is a Stage 3 synthesis; 3 Placement policy by tier and object; 4 Anchor/cache/attest pattern with cache-invalidation synchronised to revocation state; 5 Degraded modes (offline read, delayed write, partition, reorg) with the assumption each relies on and what breaks it; 6 Security, privacy, integrity envelope against the memo threat model; 7 Governance: endorser sets, issuer roles, key rotation; 8 Composition map (which mechanism from which family/option) and why the composite is not a wrapped registry; 9 Realisability and cost as budgets in variables; 10 Build plan as a work order for a later stage; closing sections.

**Standing rules.** As in A1, with emphasis: **Family F is design only**; the document may propose a build plan but must state, in its first section and its title block subtitle, that the composite is a Stage 3 output and not a Stage 1 sandbox. Cleverness with honesty: every clever path names its enabling assumption and its failure condition.

**Load-bearing questions.** (a) Does the researcher want Family F specified as an interface profile (a constrained use of IMinimalSSI plus extensions) or as an architecture (nodes, RSUs, sidechains)? (b) Which degraded mode is in-thesis and which is future work? (c) Is the composite's cost claim (C13) to be stated as a formula or as an O1-substituted estimate with bounds?

**Acceptance checklist.** "Stage 3 output, not a sandbox" appears in §2 and the subtitle · no new interface signatures · every degraded mode has an assumption and a break condition · budgets in variables · composition map names a source option for every mechanism · closing sections · questions load-bearing.

### 3.4 Primer A4 — Scenario comparison pass (the researcher's scenarios versus 04)

**Objective.** Compare the researcher's own CAV and AI-agent scenarios (written independently) with the two designed in 04, function by function and object by object, to find coverage gaps, placement disagreements, and differences in failure-mode treatment, and to produce a merged scenario pair for the thesis.

**Inputs to attach.** `04_Scenarios_Full_Coverage_CAV_and_Agent.md`; the researcher's own scenario documents (any format); `SSI-Minimal-Function-Specification-Formal.md` (function list); `06`, `07` for the scenario template.

**Deliverable.** `A4_Scenario_Comparison_and_Merge.md` · primary, deepening 04 · 4,000–6,000 words · Type B · required sections: 1 Claim; 2 Coverage matrix (rows F1–F12, C1–C4, G1–G4, and every object; columns 04-CAV, 04-agent, researcher-CAV, researcher-agent); 3 Placement disagreements with the argument for each resolution; 4 Failure-mode disagreements; 5 Merged scenario pair in the standard template (actors, objects, tagged sequence, tier, placement, failure modes, tail, test); 6 What the merge would demonstrate and which scenario script (S7/S8 or a proposed S9) would carry it; closing sections.

**Standing rules.** As in A1. The researcher's scenarios are inputs, not authorities: where they disagree with the specification (for example, a Tier 1 chain read), say so rather than accommodate it.

**Load-bearing questions.** (a) Which of the two CAV scenarios becomes the thesis's Chapter 4 scenario? (b) Does the researcher accept a scenario that reads the chain in Tier 2 only via an edge cache, or insist on no chain read at all below 500 ms? (c) Which uncovered function, if any, is acceptable to leave uncovered in the thesis scenario?

**Acceptance checklist.** Matrix covers every function and object · every disagreement has a resolution argued from the specification or the tiers · merged pair complete in the template · test named for the merged pair · closing sections.

### 3.5 Primer A5 — Latency-tier measurement design (Caliper / Besu / AURORA)

**Objective.** Design, without executing, the measurement campaign that would convert the three-tier framework (C6) from design into evidence: what is measured, on what stack (Hyperledger Caliper against Besu QBFT; the Hardhat-local proxy; the AURORA testbed named in the programme's P0 sign-off, with the substitution it implies openly stated), and with what claim boundaries.

**Inputs to attach.** `05_Scenarios_Latency_Tiers.md`; `03` degraded-modes section; `CVIN_SC_Manual_Audit_Playbook_v1-0.md` §4 (the cut-line and the Stage 18 entry); `METHODOLOGY.md`; `traces/SCHEMA.md`; the CVIN 2020 paper [5].

**Deliverable.** `A5_Latency_Tier_Measurement_Design.md` · primary, deepening 05 · 4,000–6,000 words · Type B · required sections: 1 Claim (which latency claims the thesis can make at each evidence level: Hardhat-local, Besu-local, edge-deployed); 2 Measurands (end-to-end verify latency by path: cached off-chain, RSU edge read, remote chain read, write-and-finalise), units, and where in the trace each is recorded; 3 Stack options with what each can and cannot show; 4 Experimental design (factors, levels, runs, warm/cold cache, block time, finality); 5 Threats to validity; 6 Claim-boundary sentences for Chapter 4 at each evidence level; 7 Work order for the CLI agent; closing sections.

**Standing rules.** As in A1. **No latency number may appear as measured**: the sandbox has none; the S1 trace records gas and ordering, not wall-clock latency of verification paths. Any figure from Caliper or Besu literature is DIGEST-LEVEL with a source.

**Load-bearing questions.** (a) Which evidence level is the thesis's cut-line for C6 — Hardhat-local proxy, Besu-local, or none (design-only)? (b) Is the AURORA-to-sandbox substitution to be stated in Limitations, as the P0 sign-off proposed? (c) Which single Tier 2 operation (charging, toll, parking) is the one to measure if only one can be?

**Acceptance checklist.** No measured latency · every measurand has a unit and a trace field · claim-boundary sentences present for each evidence level · work order has acceptance criteria and trace assertions · closing sections.

### 3.6 Primer A6 — Reputation, payment, gated access, and low-connectivity deep pass with state machines

**Objective.** Deepen 06 by giving each of the four scenario families an explicit state machine for both the CAV and the agent case: states, transitions, which function (F/C/G) fires each transition, what is read and written where, and how the machine behaves under read-only and delayed-write connectivity.

**Inputs to attach.** `06_Scenarios_Reputation_Payment_GatedAccess_LowConnectivity.md`; `03` degraded modes; `08` for channel state; `09` §§ on reputation semantics; the ISetC description; Memo B (reputation and Sybil handling).

**Deliverable.** `A6_State_Machines_Reputation_Payment_Gated_Offline.md` · primary, deepening 06 · 5,000–7,000 words · Type B · required sections: 1 Claim; 2 Notation (states, guards, actions; placement annotation per transition); 3–6 One section per family, each with a CAV machine and an agent machine, transition table, placement table, failure transitions, and the offline variant (which transitions are permitted with a stale cache, for how long, and what reconciles on reconnection); 7 Sybil and collusion handling in the reputation machine (issuer weighting, participation cost, anomaly screen) with what each defends against and what it does not; 8 Demonstration plan mapping every transition to a scenario step and a trace assertion; closing sections.

**Standing rules.** As in A1. Payment is modelled as an authorisation and settlement pattern, not as a token design; do not invent a token. Reputation numbers (scores, thresholds) are parameters, not results.

**Load-bearing questions.** (a) Does the researcher want reputation attestations (C1) anchored on-chain per attestation or aggregated off-chain with a periodic anchor? (b) What staleness window is acceptable for gated access under read-only connectivity? (c) Is payment in-thesis scope or a "further functionality" tail only?

**Acceptance checklist.** Eight machines (four families × CAV/agent) each with transition and placement tables · every transition tagged with a function · offline variant for each · Sybil section names defence and residual · demonstration plan complete · closing sections.

### 3.7 Primer A7 — Beyond-CAV registries and legacy integration

**Objective.** Deepen 07: driver's licences, property deeds and vehicle title, repair and maintenance history, inspection and emissions registries, and their integration with legacy back ends (DMV databases, OEM systems, insurer systems) through the endorsement pattern and oracles, with the CAV and agent pairs preserved.

**Inputs to attach.** `07_Scenarios_Beyond_CAV_Backend_Systems.md`; the credential-type list (VID_BIRTH, VEHICLE_REGISTRATION, DRIVER_LICENCE, eleven lifecycle types) and the eight issuer roles from the Context Block; the ten automotive schemas UC1–UC10 from `2_w3c-ssi-layer/` (attach the schema files); MOBI VID I–II [27]; Memo A on oracles.

**Deliverable.** `A7_Beyond_CAV_Registries_and_Legacy_Integration.md` · primary, deepening 07 · 5,000–7,000 words · Type A/B · required sections: 1 Claim (the same twelve functions plus endorsement suffice for back-end registries; what changes is the issuer graph and the placement of content); 2 Registry catalogue with issuer role, endorser, credential type, content placement, anchor, revocation model; 3 Legacy integration patterns (mirror-and-anchor, oracle-attested read, issuer-side signing gateway) with trust assumptions; 4 Data-protection consequences per registry; 5 CAV and agent scenario pairs per registry in the standard template; 6 Demonstration plan (which types S8 covers; which need a new scenario); closing sections.

**Standing rules.** As in A1. Do not claim any legacy system's interface; describe integration patterns generically and mark jurisdiction-specific facts UNVERIFIED.

**Load-bearing questions.** (a) Which registry beyond the vehicle ones is in-thesis (licence is likely; deeds may be illustration only)? (b) Does the researcher accept an oracle-attested read as sufficient integrity for repair history, or require issuer signing? (c) Which jurisdiction's licence classes are the worked example?

**Acceptance checklist.** Catalogue complete for every named registry · each integration pattern has a trust assumption · CAV and agent pairs present for each registry · closing sections.

### 3.8 Primer A8 — I2I protocol specification pass toward a DIDComm/A2A-compatible spec

**Objective.** Take 08 from a channel design and crux list to a protocol specification: message types, the handshake bound to F8 challenge and F12 delegation, key agreement and forward secrecy, session policy, interaction logging (signed execution traces), revocation propagation and cache invalidation, replay protection, offline operation, and explicit compatibility mappings to DIDComm v2 and to Google A2A / Anthropic MCP phases (discovery → handshake → session policy → interaction logging → revocation/dispute signalling).

**Inputs to attach.** `08_I2I_Secure_Communication_and_Cruxes.md`; `scenarios/run_i2i.js` (the S1 script; the off-chain ECDH P-256 + AES-256-GCM steps are its `kind=offchain` entries); `traces/i2i_O1_ERC1056_1780620182135.jsonl`; Memo A §4 (A2A phases); [11], [19]; DIDComm v2 and A2A specification references as NEW-n.

**Deliverable.** `A8_I2I_Protocol_Specification_Draft.md` · primary, deepening 08 · 6,000–8,000 words · Type B/C · required sections: 1 Claim and scope (what the protocol is not: it does not replace SCMS at Tier 1); 2 Terminology and normative language; 3 Roles and identifiers (DIDs, delegates, endorsed issuers); 4 Message catalogue with field tables; 5 Handshake sequence with F-tags at every chain touch and a statement of what is read off-chain from cache; 6 Key agreement, AEAD, forward secrecy; 7 Session policy and interaction logging; 8 Revocation propagation and staleness; 9 Replay and equivocation; 10 Offline and delayed-write behaviour; 11 Compatibility mapping tables (DIDComm v2; A2A/MCP phases); 12 Security considerations against the memo threat model and chain faults; 13 Conformance: the trace assertions an implementation must satisfy; closing sections.

**Standing rules.** As in A1. The S1 trace is the only executed I2I evidence and it records one channel, one option; the specification must not imply interoperability has been tested. Cryptographic parameters are stated as choices with rationale, not as measured security levels.

**Load-bearing questions.** (a) Is the specification to target DIDComm v2 compatibility strictly, or only a documented mapping? (b) Are agent sessions (A2A) and vehicle sessions one protocol with profiles, or two? (c) Does the researcher want interaction logs anchored per session or per epoch?

**Acceptance checklist.** Every message has a field table · every chain touch in the handshake is F-tagged · offline section names the assumption and the break · both compatibility tables present · conformance assertions map to SCHEMA.md fields · closing sections.

### 3.9 Primer A9 — Reputation-for-federated-ML benchmark design

**Objective.** Deepen 09 into a benchmark design that would test the chain "federated ML needs reputation; reputation needs identity; identity needs this system" — and the analogous chains for cooperative perception, crowd-sourced HD maps, and collaborative anomaly detection — by specifying an experiment in which identity-bound reputation (Set C attestations weighted by endorsed issuers) is compared with identity-free robust aggregation under Sybil and poisoning attacks.

**Inputs to attach.** `09_Reputation_Identity_and_Federated_Learning.md`; `06` reputation section or `A6` if it exists; the ISetC description; Memo B (Sybil/collusion); NEW-n references for McMahan et al. 2017, Kairouz et al. 2021, Blanchard et al. 2017 (Krum), Douceur 2002, Kamvar et al. 2003 (EigenTrust), each labelled DIGEST-LEVEL unless read.

**Deliverable.** `A9_Reputation_for_Federated_ML_Benchmark_Design.md` · primary, deepening 09 · 5,000–7,000 words · Type B/C · required sections: 1 Claim in falsifiable form; 2 The three-link argument restated with what each link would look like if false; 3 Threat model (Sybil, collusion, data poisoning, model poisoning, free-riding) mapped to identity, reputation, and aggregation defences; 4 Experimental design: task, data partition, client population, attacker fraction, aggregation rules compared (mean, Krum-style, reputation-weighted), reputation update rule tied to C1/C2 semantics, identity cost as participation cost, metrics (accuracy under attack, attacker influence, convergence rounds, cost per client in on-chain operations as counts not gas); 5 Analogous cases (perception, maps, anomaly detection) with the parameter that changes; 6 What the benchmark cannot show; 7 Work order for the CLI agent, including whether it runs in the sandbox repository or a separate one; closing sections.

**Standing rules.** As in A1. No ML result may be reported; the section is a design. Federated-learning figures from the literature are DIGEST-LEVEL with a source.

**Load-bearing questions.** (a) Is this benchmark in-thesis or Paper 3 material? (b) Which collective-computation case is the thesis's primary example — federated learning or cooperative perception? (c) Is the reputation update rule a thesis contribution or borrowed?

**Acceptance checklist.** Falsifiable claim · threat-to-defence table · full experimental design with metrics and units · "cannot show" section · work order with acceptance criteria · closing sections.

### 3.10 Primer A10 — Thesis prose conversion pass (Type B/C to Type A) with the style gate

**Objective.** Convert designated Type B (tables, data) and Type C (framing, claims) blocks from the general pass into Type A thesis prose for the chapter and section named in each block's registry row, applying the programme's **Writing Style Directions v1.0** (25 directives and the 7-step gate) as the acceptance gate. The pass must refer to the gate by name and apply it as supplied; it must not invent or paraphrase its content.

**Inputs to attach.** `Writing Style Directions v1.0` (mandatory; the pass cannot run without it); `11_Thesis_Integration_and_Academic_Argument.md`; `S2_Registry_Delta.md` (the rows marked for promotion); the specific source documents for the blocks being converted; `CVIN_SC_Thesis_Narrative_Synthesis_v11-3.docx` (plain text) for the target chapter's existing prose and numbering; the reference list [1]–[28].

**Deliverable.** `A10_Thesis_Prose_Conversion_<chapter>.md` (one file per target chapter) · primary, feeding 11 · length as the target sections require, typically 2,000–5,000 words per chapter file · Type A · required sections: 1 Conversion register (block name, source document and section, target chapter §, word count, gate result step-by-step); 2 The prose, under the thesis's own section numbering, with IEEE citations resolved to [n] or NEW-n; 3 Terminology check against the programme list (CAV, OBU, RSU, VC, VP, DID, I2I, SCMS, VID; spelled out on first use); 4 Claims narrowed (any Type C claim whose evidence is DIGEST-LEVEL or pending is rewritten to what is verified, in the K14 manner: narrow rather than defend); closing sections.

**Standing rules.** As in A1, with two emphases. First, converting a table to prose must not upgrade its verification state: a DIGEST-LEVEL figure remains hedged in prose. Second, the gate is applied literally from the attached Style Directions; if the file is not attached, stop and ask for it rather than approximating the gate.

**Load-bearing questions.** (a) Which chapter is converted first — Chapter 4 (results, pending empirical) or Chapter 5 (discussion, scaffolding)? (b) Does the researcher want the createPresentation finding stated as a specification-level finding (as the audit playbook §4 proposes) or held until cross-option runs exist? (c) Which registry rows are frozen for conversion and which remain open?

**Acceptance checklist.** Style Directions attached and named in the conversion register · every converted block shows its 7-step gate result · no verification state upgraded · thesis numbering matches the Synthesis v11.3 target · terminology check passed · closing sections.

---

## 4. Primer S — Support-document maintenance (S1, S2, S3)

**Objective.** After any angle pass, append to the three standing support documents of this suite without regenerating them. This primer is pasted after the Context Block whenever an angle document is accepted.

**Inputs to attach.** `S1_Weighted_Reference_Index.md`, `S2_Registry_Delta.md`, `S3_Change_Log_and_Meta_Commentary.md` (current versions); the accepted angle document; the programme's cumulative R-series index from the Systematic Review v13.1 suite if the researcher wants R-numbers assigned rather than NEW-n placeholders.

**Rules the pass must follow.** S1 is cumulative programme memory: **never restart the R-numbering**; carry every existing row forward unchanged, append new sources after the last R-number in use, and convert the angle document's NEW-n entries to R-numbers only if the researcher has supplied the live index (otherwise they remain NEW-n with a note "awaiting R-assignment"). Every new row states class, weight on the ten-point scale with a one-line rationale, and exactly one of VERIFIED AT SOURCE / DIGEST-LEVEL / UNVERIFIED; no empirical claim graduates from a secondary or promotional source. S2 is a delta, never a replacement: one row per new or changed block in the schema Content Block · T · Source · Ch. · Ready % · Notes, with Ready % as an estimate of remaining editorial work. S3 gains, for each pass, a version-log entry (suite name, session scope, request fulfilled, documents issued, what is superseded, registry effect, numbering note), methodology notes, **K-ledger** additions (K-numbers continue the programme series; each item states the error, the correction, and every document that must carry the propagation, including the four corrections already owed propagation, K29, K30, K32, K45, if the pass touched their subject), an unresolved-items register, and the five-part meta commentary.

**The load-bearing question test.** Each meta-commentary part closes with one question. Before writing it, the pass must apply the test from the Suite Architecture: if the author could answer the question alone, the part has not done its work; the question must require the researcher's judgement, access, or decision. A question that asks "should this be verified?" fails; a question that asks "given that the only verified option is O1, do you accept the coverage matrix as a design contribution or delay Chapter 4 for WO-1?" passes.

**Acceptance checklist.** S1 row count increased, never decreased; no R-number reused or renumbered · S2 contains only delta rows · S3 has all five sections for this pass and the K-ledger continues the series · every commentary question passes the test · the angle document's "Sources used" table reconciles one-to-one with the S1 additions.

---

## 5. When to use chat and when to use code

**The rule.** Any pass whose deliverable contains a measurement — a gas figure, a latency, a proof time, a model accuracy, a test count — must be executed in the code environment, because the only admissible source of a new number is a trace file produced by a scenario script under the sandbox's hard rules (real gas only; committed traces immutable; new runs are new files). Any pass whose deliverable is argument, design, comparison, specification, or prose can be done in chat, provided the Context Block is present and the acceptance checklist is applied.

| Angle | Chat-suitable | Requires code | Notes |
|---|---|---|---|
| A1 Placement rubric | Yes | Only if the demonstration section is to be executed | The rubric is design; S7/S8 assertions confirm placement later |
| A2 ZKP deep pass | Design and comparison: yes | The benchmark protocol's execution: code | Chat writes the protocol; CLI runs it |
| A3 Family F specification | Yes | No (design only, by rule) | A build plan is a work order, not a build |
| A4 Scenario comparison | Yes | No | Merged pair's test is a later work order |
| A5 Latency design | Yes | Any latency figure: code, on a named stack | Chat must not report latency |
| A6 State machines | Yes | Demonstration mapping executed later | — |
| A7 Beyond-CAV registries | Yes | New credential types in S8: code | Schemas attached, not run |
| A8 I2I protocol | Yes | Conformance assertions: code | S1 trace is the only evidence; do not extend it in chat |
| A9 FL benchmark design | Yes | Any result: code, possibly separate repository | — |
| A10 Prose conversion | Yes | No | Requires the Style Directions file |

**Hand-back format.** When a chat pass produces something the CLI agent must build or measure, the chat closes with a work order in the following form, which the researcher pastes to the CLI agent unchanged:

> **WORK ORDER WO-A<n>-<k>** · Source: A<n> §<s> · Repository path: `5_minimal-ssi-sandbox/` · Branch: `vid-build`.
> **Scope.** One paragraph stating what is built or measured and what is explicitly out of scope.
> **Files touched.** Exact paths; new scenario scripts named `run_<id>.js` matching the catalogue; no interface changes.
> **Acceptance criteria.** Numbered, each testable: the compliance suite stays 12/12 unmodified; `npx hardhat compile` green; the new test file passes; the scenario emits a JSONL trace per `traces/SCHEMA.md` (or a versioned extension named here).
> **Trace assertions.** A list of the form: "entry with fnId=F8 and identity=Vehicle has gasUsed present and events ≥ 1"; "no entry with kind=tx occurs between the offline read at seq=a and the reconnection at seq=b"; "entry with fnId=G4 returns false after the G3 entry". Each assertion names the field it inspects.
> **Deviations.** Instruction that any miss against spec targets or scoring anchors is recorded in `docs/FINDINGS.md` with its cause, not optimised away.
> **Return.** The trace file name, the FINDINGS entry if any, and the numbers, which the angle document then cites by file name and seq.

A work order without trace assertions is not acceptable, because the assertions are what make the chat's design claim falsifiable by the build; a chat that cannot write them has not finished its design.

---

## 6. Sources used in this document

| R# / NEW | Source | Verification state | How used |
|---|---|---|---|
| — | `_CONTEXT_BRIEF.md` (this suite, 2026-09-03) | VERIFIED AT SOURCE | All facts in the Context Block; specification; families; measured numbers; rules |
| — | `traces/i2i_O1_ERC1056_1780620182135.jsonl` and `traces/SCHEMA.md` | VERIFIED AT SOURCE | Gas values for F3, F9, F10 added to the measured table; trace field names |
| — | Deliverable Suite Architecture v1.0 | VERIFIED AT SOURCE | Suite slots, title block, S1/S2/S3 schemas, load-bearing question test, reuse checklist |
| — | Manual Audit Playbook v1.0 | VERIFIED AT SOURCE | K29/K30/K32/K45, Style Directions name (25 directives, 7-step gate), Stage 18 Caliper/Besu, AURORA sign-off, §4 cut-line |
| — | `5_minimal-ssi-sandbox/CLAUDE.md` | VERIFIED AT SOURCE | Hard rules quoted in §5; project commands |
| [5], [11], [12], [13], [14], [19], [27] | Thesis reference list | carried forward; not re-read for this document | Named as attachments in primers |
| NEW-n (McMahan 2017; Kairouz 2021; Blanchard 2017; Douceur 2002; Kamvar 2003; DIDComm v2; A2A; MCP) | Suggested sources in the Context Brief | UNVERIFIED (named, not read here) | Named as attachments in A8 and A9 with the label the pass must carry |

A second trace file, `traces/i2i_O1_ERC1056_1788492893157.jsonl`, exists in the repository with identical values except createPresentation at 62,446 gas; the Context Block cites the first file, as the brief does, and an angle pass that needs run-to-run variation should cite both by name.

## 7. Registry delta rows

| Content Block | T | Source | Ch. | Ready | Notes and status |
|---|---|---|---|---|---|
| HDA Programme Context Block v1.0 | B | HDA general pass, 99 §2 | 2 (methodology appendix) | 90% | Reusable across angle passes; re-issue when 10 publishes VID traces |
| HDA angle-pass primer set A1–A10 | B | HDA general pass, 99 §3 | Admin | 85% | Deliverable naming awaits the series decision (§8 Q1) |
| Chat-to-CLI work-order format with trace assertions | B | HDA general pass, 99 §5 | 2 (methodology) | 85% | Candidate for METHODOLOGY.md twin; check against Suite Architecture on next revision |
| Support-document maintenance primer | B | HDA general pass, 99 §4 | Admin | 90% | Depends on live R-series index availability |

## 8. Open questions for the researcher

1. **Series and numbering.** The primers propose "HDA Angle Passes, Suite v1.1" with files `A1`–`A10` under `docs/hda-angle-passes/`. The Suite Architecture requires the series to be fixed before the first document is produced, and the same document's open decision C2 (campaign-local versus programme-wide numbering) is still unresolved. Which numbering does the researcher adopt, and does it settle C2 for all campaigns?
2. **R-assignment authority.** Angle passes run in chat will emit NEW-n sources. Only the researcher holds the live cumulative R-series index from the Systematic Review v13.1 suite (which the audit playbook records as living in chat downloads). Will the researcher supply it to each maintenance pass, or accept NEW-n placeholders until a single consolidation pass?
3. **Order of angles.** The primers are independent, but A3 is stronger after A1 and A2, and A10 is only worth running on frozen registry rows. Given the audit playbook's cut-line logic, which angles are in-thesis and which are Paper 2/3 material, so that chat effort is not spent on passes whose output will be deferred?
4. **Measurement authority for angle passes.** The primers forbid chat from reporting any measurement. If a chat pass proposes a measurement the sandbox cannot yet make (Besu latency, Groth16 verifier gas, FL accuracy), does the researcher want the work order queued behind the WO-1 cut-line decision, or run opportunistically as design-only demonstrations?
