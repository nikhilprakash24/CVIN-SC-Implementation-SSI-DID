CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Hybrid Data Architecture Campaign: Master Plan and Plan of Attack**

**The front door to the suite: what was asked, how it was attacked, where each demand is answered, what was built, what is measured, and what happens next**

Document 1 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · October 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type B (plan, maps, registers) → Admin; §2 and §3 are Type A candidates for Chapter 4 methodology framing*

---

## 1. The campaign in one page

**The question.** For every datum an identity system for connected and autonomous vehicles (CAVs) and AI agents handles: where does it live, who can read it, how is a write made durable, how is its integrity proven later, and what does each choice cost? The thesis has so far compared identity standards by *function coverage* (which of the twelve `IMinimalSSI` functions each provides). This campaign argues that the deeper axis is *data placement*, that the thesis's central finding (no EVM standard natively implements `createPresentation`; the LFDT/AnonCreds line does, off-chain) is an instance of that axis, and that the right synthesis is a hybrid which takes the EVM families' placement for identity anchoring and the AnonCreds placement for credentials and presentations.

**What this pass delivers.** Sixteen documents (about 150,000 words in total) and a working build:

- a core analysis trilogy — placement and anchoring (01), zero-knowledge proofs and verifiable data (02), and the hybrid design (03);
- five scenario documents, each pairing a CAV case with an AI-agent case (04–08), and an in-depth argument on reputation, identity, and federated learning (09);
- a built and measured Vehicle Identity (VID) reference layer with endorsement (10), running beside the unmodified twelve-function interface;
- the thesis-integration argument with draft prose (11), the three standing support documents (S1–S3), and paste-ready primers for running each angle pass in the chat model (99).

**The three results that are measured, not argued** (all on option O1, Hardhat local EVM; see 10):

1. The minimal VID, the vehicle registration, the driver's licence, and all eleven MOBI VID II lifecycle event types run on the twelve functions plus a governance extension with **no interface change**; the compliance suite is unchanged at 12/12 and the full suite is 19/19.
2. Credential content stays entirely off-chain (813–850 bytes per credential against a 32-byte anchor) and is verified for integrity and issuer binding with **zero chain reads**.
3. Anchoring eleven lifecycle events individually cost 1,431,745 gas; one Merkle-root anchor over the same eleven cost 130,151 — **11:1**, exactly the batch size, at the price of per-event on-chain revocation.

**The one thing to hold onto.** Everything else in the suite is a design, an argument, or a plan, and is labelled so. No latency was measured. No zero-knowledge proof was generated. Nothing ran on options other than O1, on Besu, or on hardware.

## 2. Plan of attack

The request was broad enough to be a thesis in itself, so the pass was organised to avoid the programme's known failure mode (documents that outrun their evidence).

**Step 1 — Ground in the canon.** Before writing, the pass read the programme's own record: the formal specification, the canonical sandbox v1.3 (interfaces, O1, compliance suite, S1 scenario and trace, standing rules), the thesis narrative synthesis and content registry v11.3, the three supervisor memos, the 2020 CVIN paper, the methodology and deliverable-suite convention, and the latest implementation repository. The result is `_CONTEXT_BRIEF.md`, a single verified brief that every document was written against. It fixes the vocabulary, the measured numbers, the rules (no fabricated measurements; the interface is normative; Family F is a Stage 3 design output), and the reference numbering.

**Step 2 — Build the smallest thing that makes the argument falsifiable.** The data-placement argument predicts specific things: that content can stay off-chain without losing verifiability, that batching changes cost by the batch factor, that entitlement is missing from the twelve functions. A minimal VID layer with endorsement was built to test those predictions (10). It confirmed all three and produced seven findings, two of which bear on the specification itself.

**Step 3 — Write the analysis as a dependency chain, not a pile.** 01 establishes the placement taxonomy, anchoring patterns, read and write paths, the cost model, and decision rules. 02 treats proofs. 03 composes them into the hybrid. The scenario documents (04–08) then *instantiate* the design under different pressures: full coverage, latency, reputation, payment, access, disconnection, non-vehicle registries, and the secure channel. 09 takes one consequence — collective computation needs reputation, reputation needs identity — and argues it in depth. 11 folds the whole into the thesis chapters.

**Step 4 — Carry the suite convention.** Every primary document ends with its sources and their verification state, its registry delta rows, and questions only the researcher can answer. S1–S3 merge these.

**Step 5 — Hand the angle passes to whichever tool suits them.** 99 packages the context so each angle can be deepened in the chat model; anything that produces a measurement comes back to code as a work order with trace assertions.

## 3. The argument, end to end

1. An identity system is a table: one row per datum, with placement, readership, durability, integrity proof, finality, and cost as columns (01 §1).
2. Set A (identifier, keys, delegates, lifecycle flags) is *state that must be on a shared tamper-evident substrate*; Set B (credentials, presentations) is *attestation that must not be on it in the clear*, needing only a minimal anchored residue. The EVM/LFDT divergence is two placement policies (01 §1, 11 §3).
3. Anchoring is a family of patterns — hash, Merkle root, signed-then-anchored, commitment, status list, accumulator, credential-definition — each proving something different at a different cost (01 §3). Measured here: per-event against Merkle-root anchoring (10 §5.3).
4. Read paths range from synchronous view calls to fully offline signature checks; each fits a tier and carries a staleness window that is a security parameter (01 §4; observed in 10 §5.4).
5. Write paths range from direct transactions to batched, sponsored, delayed, and sidechain writes; the hard case is the principal that must act but cannot write (01 §5, 06 §5).
6. Privacy when required comes from the proof layer — salted digests, BBS+, AnonCreds, general zero-knowledge predicates — chosen by policy, with the forensic tier deliberately *not* hidden (02).
7. The hybrid: on-chain roots of trust, identity anchors, status, and batched commitments; off-chain credentials, presentations, channels, evidence; a local signed view sufficient to act within a bounded staleness window; deterministic reconciliation (03, "Anchor · Cache · Attest · Reconcile").
8. Entitlement is not among the twelve functions; an endorsement registry beside the interface supplies it (11 §2; built and measured in 10; finding F-VID-7).
9. The same system serves licences, deeds, and repair history (07), carries the identity-to-identity secure channel (08), and is the precondition for reputation and therefore for trustworthy federated learning and similar collective computation (09).
10. The hybrid is the data architecture of Family F — a Stage 3 design hypothesis with stated evidence still owed (03 §11).

## 4. Where each thing you asked for is answered

| # | Asked for | Where | Status |
|---|---|---|---|
| 1 | Fork the latest CVIN repository | Local clone of `nikhilprakash24/CVIN-SC-Implementation-SSI-DID` on new branch `vid-build`; canonical sandbox v1.3 vendored as `5_minimal-ssi-sandbox/` | Done locally; **not pushed** (decision D1) |
| 2 | Basic minimal VID | `lib/vid` + S7; 10 §3.3 | Built, measured |
| 3 | Minimal driver's licence | same | Built, measured |
| 4 | Minimal car ID (vehicle registration) | same | Built, measured |
| 5 | All the VIDs (MOBI VID II lifecycle, eleven types) | S8; 10 §3.4, §5 | Built, measured |
| 6 | Use endorsement | `EndorsementRegistry.sol` (G0–G4); 10 §3.4; argument in 11 §2 | Built, measured, argued |
| 7 | Documentation and what is needed for the thesis, with narrative and academic argument | 10 (build), 11 (integration and draft prose) | Written |
| 8 | CAV scenario and agent scenario using all functions and objects (create, do not build) | 04 | Written as designs (S9, S10) |
| 9 | Example scenario per latency tier | 05 | Written |
| 10 | Reputation, payment, gated access, low connectivity (read-only or delayed write) | 06 | Written |
| 11 | Back-end systems beyond CAVs: licences, deeds, repair history | 07 | Written |
| 12 | ZKP (huge) | 02 | Written; no proof generated |
| 13 | I2I secure communication and the other cruxes | 08 | Written |
| 14 | Off-chain and on-chain | 01 (core), 03 (design) | Written; partly measured |
| 15 | Two per topic (CAV and agent), then connection to problems solved and further functionality (tolling, pay-as-you-use roads, road and traffic reporting, federated ML) | Every scenario section in 04–08 carries a "problems solved / further functionality" tail | Written |
| 16 | A whole in-depth treatment: federated ML needs reputation, reputation needs identity, identity needs this system; and the same for similar cases | 09 (§3–§5 the chain; §7 other cases) | Written |
| 17 | **The redirected priority:** a whole body of work on on/off-chain data and anchoring, read and write, ZKP, verifiable data integrity, and cost, through to the best-of-both-worlds design | 01, 02, 03 (≈42,000 words), measured anchor points in 10 | Written; core claims measured on O1 |
| 18 | Minimum three documents including a meta commentary, deeply integrated with the rest of the work | Sixteen; S3 is the meta commentary; 11 and S2 are the integration | Written |
| 19 | If the chat is the better tool, documents to feed it | 99 | Written |
| 20 | A proper way to test, build, or at least demonstrate | Every primary document has a demonstration plan; §7 below consolidates | Planned; first slice built |

## 5. Reading order

For a supervisor with thirty minutes: this document §1 and §3, then 10 §5–§6, then 11 §2–§3.
For the argument: 01 → 02 → 03.
For breadth: 04, then whichever of 05–09 matches the question at hand.
For writing the thesis: 11, then S2, then S1's verification-debt list.
For the next pass: S3 §5, then 99.

## 6. Canonical scenario register

The primary documents were written in parallel and several independently proposed the identifier "S9" for different scripts. This register governs; S3 records the correction (K-HDA-8).

| ID | Scenario | Specified in | State |
|---|---|---|---|
| S1 | End-to-end secure I2I channel, 12/12 functions, mid-session revocation | sandbox; 08 §1 | **Built**; two traces (June architect pass; September rerun on this machine) |
| S2–S4 | Dual-mode identity; EV charging; insurance lifecycle | sandbox `ARCHITECTURE.md` §4; 10 Addendum K | **Built**; 24 traces (all eight options) |
| S6 | Agentic wrapper (Stage 31) | sandbox `ARCHITECTURE.md` §4 | Specified in canon; unbuilt (O7 + 04's S10 design are its inputs) |
| S5 | IDPP port O1 ↔ O8 | sandbox `ARCHITECTURE.md` §4; 10 Addendum J | **Built** both directions; traces on file |
| S7 | Minimal VID with endorsement | 10 | **Built**; trace on file |
| S8 | All eleven lifecycle VIDs, Merkle batch | 10 | **Built**; trace on file |
| S9 | CAV full coverage: "a vehicle's first year" | 04 | Design |
| S10 | Agent full coverage: fleet-operations agent and sub-agents | 04 | Design |
| S11 | Reputation (CAV road reports; agent marketplace) | 06 §2 | Design |
| S12 | Payment authorisation and receipt anchoring | 06 §3 | Design |
| S13 | Gated access, offline-capable verifier | 06 §4 | Design |
| S14 | Delayed-write reconciliation | 06 §5; 03 §3 (there called S9); 10 Addendum A | **Built**; trace on file |
| S15 | Deed/title credential | 07 §3, §8 (there called S9) | Design |
| S16 | Reputation-weighted federated-learning round | 09 §9 (there called S9); 10 Addendum B | **Built** on the Set C harness; trace on file |
| S17 | Batch-anchor contract with on-chain inclusion verification | 01 §11 (there called S9); 10 Addendum A | **Built**; trace on file |
| S18 | Revocation storm | 03 §10 (there called S10) | Design |
| S19 | Policy-selected disclosure across verifier classes (BBS+) | 03 §10 (there called S11); 10 Addendum C | **Built**; trace on file |
| S20 | Age-gate range predicate, Groth16, on-chain verification | 02 §4 C-2, §10 stage (c); 10 Addendum D | **Built**; trace on file; 250,283 gas measured |
| TS1/TS2/TS3-CAV, -AGT | Six tier scenarios, one CAV and one agent per latency tier | 05 | Design. Renamed from "T1/T2/T3" to avoid collision with the typing tags T1 `declare` and T2 `verifyTyped` (correction K-HDA-9, S3 §4) |

Extension tags used in traces: G0 addRoot · G1 registerIssuer · G2 endorseIssuer · G3 revokeEndorsement · G4 isEndorsed · T1 declare · T2 verifyTyped · C1–C4 the four Set C functions (unbuilt).

## 7. Build, test, and demonstration plan

The programme's method is that a claim graduates only through a gate with a named trace. The plan below keeps that discipline.

**Slice 0 — exists today (laptop, about two minutes to run).**
Compliance suite and VID tests (19 passing); S1, S7, S8 with traces. Demonstrates: all twelve functions; endorsement gating; off-chain verification with zero chain reads; stale-cache acceptance and its correction; replay prevention; revocation of a credential, of an endorsement, and of an issuer; the 11:1 batching result; a decommissioned DID that stays resolvable.

**Slice 1 — DONE 2026-10-14 (see 10 Addenda A and B).** Ordered by evidence gained per unit of effort.

| Step | Adds | Settles | Acceptance (trace assertion) |
|---|---|---|---|
| 1a | S14 delayed-write: a mock provider rejects writes for N steps; the OBU queues signed events; one batch anchor on reconnect | Whether reconciliation rules in 03 §3 are implementable and what they cost | Queued `offchain` entries followed by one `tx`; a revocation issued during the outage wins on reconcile |
| 1b | S17 on-chain Merkle inclusion verifier | Whether batched events can regain per-event verifiability on-chain, and at what read cost | Inclusion true for a leaf, false for a tampered leaf |
| 1c | Timing fields in the trace schema (versioned) | Gives every later scenario a latency column; Hardhat-local is a lower bound only | Schema v2 documented; S1/S7/S8 re-emitted |
| 1d | Minimal `ISetC` harness beside O1 | Unblocks S11 and S16 | C1–C4 exercised; labelled harness, not O7 |
| 1e | S16 toy federated round with a Sybil injection | The reputation-needs-identity claim of 09, as an observation | Sybil weight suppressed when endorsement is required; not suppressed without it |

**Slice 2 — proofs (02 §10).** (a) salted-digest disclosure exists; (b) BBS+ over the same credential objects; (c) a circom range proof with an on-chain verifier, gas in a trace; (d) anoncreds-rs as the Set B ceiling comparison. Each is a new dependency and a separate work order.

**Slice 3 — other options and a real chain.** One controller adapter per ported option (after WO-1), then the same scenarios unchanged; Besu QBFT and Caliper for throughput and latency (WO-8).

**Slice 4 — hardware.** OBU/RSU on the AURORA testbed. Only this slice can support a Tier 2 latency claim.

**What a twenty-minute demonstration shows today.** Run the suite; replay S7 while narrating the three trust breaks; show the 813-byte credential beside its 32-byte anchor; replay S8 and put the two anchoring costs side by side; open FINDINGS items 4–10.

## 8. Decisions owed

| # | Decision | Why it blocks | Recommendation |
|---|---|---|---|
| D1 | Push `vid-build` and open a pull request; against which repository | Nothing is backed up off this machine | Push to the fork now; choose the PR target after D2 |
| D2 | Ratify the build as a work order (WO-V) in the canonical plan, or keep it as a sidecar | The canonical rules send unplanned scope to proposals; the build was operator-directed | Ratify; it is the first implementation of the specification's own §6 governance extension |
| D3 | Contribution C16 (endorsement-gated credential architecture and VID reference layer): separate, or folded into C4 and C12 | Fixes Chapter 1 §1.3 and the framing of 11 | Fold, unless the committee wants the build named (11 §1.6 gives both cases) |
| D4 | Specification v1.1: does F6 return the anchored hash, or does the specification state that content binding is an off-chain obligation (F-VID-1) | Touches the normative interface | State the obligation; do not change the signature |
| D5 | Archival-issuer policy for immutable credentials (F-VID-2) | Affects the birth-certificate design and 07 | Issue from a long-lived root DID; verifier policy distinguishes "valid now" from "validly issued" |
| D6 | Who administers endorsement roots | The governance model the thesis must name | Per-jurisdiction operator (the Local CVIN of the 2020 paper), stated as a design parameter |
| D7 | The empirical cut-line: how much of Slice 1–3 is in the thesis | Sets how Chapters 4 and 5 phrase every tier and proof claim | Slice 1 in; Slice 2(b) or (c) as one demonstration; Slices 3–4 as named future work |
| D8 | Which angle pass first, and in which tool | Sequencing of the next month | On/off-chain per-standard scoring rubric (primer 1) in chat, in parallel with Slice 1a–1b in code |

## 9. Known limits of this pass

- The nine documents drafted before the build treat S7/S8 as pending; each now carries a post-build note pointing to 10 and to the reconciliation table in S3 §3. They were not rewritten.
- External quantities (proof sizes, verifier gas, rollup multipliers, fleet sizes) are labelled DIGEST-LEVEL or UNVERIFIED throughout; S1 lists the verification debt. None should be quoted in the thesis before it is read at source.
- Currency figures in 01 §7 and 03 §8 use illustrative gas and token prices chosen for arithmetic; only the ratios are claims.
- The programme's cumulative reference numbering (R-series) lives in the Systematic Review v13.1 suite, which was not on this machine; S1 uses provisional identifiers pending merge.
- The Tier-1 and SCMS material was written from the thesis draft and the 2020 paper, not from IEEE 1609.2 read at source.

---

## Sources used in this document

| Id | Source | Verification state | How used |
|---|---|---|---|
| — | `_CONTEXT_BRIEF.md` and the files it was compiled from (specification, sandbox v1.3, synthesis and registry v11.3, memos, 2020 paper, suite architecture, audit playbook) | VERIFIED AT SOURCE | Plan, vocabulary, rules |
| — | Traces and test output of this pass (10 §4–§5) | VERIFIED AT SOURCE | §1 results |
| — | Documents 01–11, 99 of this suite | VERIFIED AT SOURCE for structure (headings read); content sampled, not fully re-read | §3–§6 maps |

## Registry delta rows

| Content Block | T | Source | Ch. | Ready | Notes and status |
|---|---|---|---|---|---|
| HDA Master Plan (this document) | B | HDA 00 | Admin | n/a | Front door; scenario register governs |
| The ten-step placement argument (§3) | A | HDA 00 §3 | 4 §4.5 opening; 5 | 75% | Compressed form of 01, 03, 11 |
| Canonical scenario register S1–S19 | B | HDA 00 §6 | 4 | 85% | Supersedes per-document S-numbers |
| Staged demonstration plan | B | HDA 00 §7 | 4 (method), 5 (future work) | 80% | Depends on D7 |

## Open questions for the researcher

The eight decisions of §8 are the open questions. The two that cannot wait are D1 (the work is on one disk) and D7 (every sentence about tiers and proofs in Chapters 4 and 5 depends on where the empirical line is drawn).
