# Phase 2 Idea Register

**Generated** by `docs/phase2/build_phase2.py` from `docs/phase2/ideas.yaml`; do not edit by hand. **Author:** Nikhil Prakash (MASc, UBC ECE). **Part of:** Phase 2, sub-phase P2.0 (`docs/phase2/README.md`).

**Scores:** orchestrator estimate, Phase 2 session 1 (2026-10-14); not yet reviewed by the author. Each idea is scored 1-5 on value, novelty, feasibility, reuse of Phase 1 assets and risk; the total is 0.30×value + 0.20×novelty + 0.20×feasibility + 0.15×reuse + 0.15×safety (safety = 6 − risk). The ranking orders the conversation; it does not choose. The author chooses (P2-D1).

26 ideas in 7 tracks; 6 candidate programmes. Every anchor below was checked to exist in the Phase 1 artefact it names.

## Ranking

| Rank | Idea | Track | Total | value | novelty | feas. | reuse | risk | Phase 1 anchors | Needs |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | **I-05** A theory of revocation freshness (k, time bounds and their optimum) | T | 4.45 | 5 | 4 | 4 | 5 | 2 | C4, N-17, D51, #32, #37, #46 | — |
| 2 | **I-24** Identity-dependent transactions (IDTx): definition, taxonomy, measured cost and staleness (author focus F1) | T | 4.45 | 5 | 4 | 4 | 5 | 2 | C1, C8, D51, D54, D64, #49, #31 | — |
| 3 | **I-16** W3C external validity on chain-backed documents | S | 4.10 | 4 | 2 | 5 | 5 | 1 | C5, #4, #24 | — |
| 4 | **I-01** Real mobility drives the existing V2V/V2I layer (SUMO + TraCI) | R | 4.05 | 5 | 2 | 4 | 5 | 2 | C2, C3, N-4, SC-22, #27, #44 | — |
| 5 | **I-03** Public-chain witness and rollup economics | R | 3.95 | 4 | 3 | 4 | 5 | 2 | N-11, #25, #26, C1 | — |
| 6 | **I-26** Modes of chain interaction (direct, mediated, detached) and mode selection per message class (author focus F3) | R | 3.95 | 4 | 3 | 4 | 5 | 2 | C2, C3, C4, #50, #27, #37, D52, D61 | I-25 |
| 7 | **I-13** Model checking the revocation and cache protocol | A | 3.85 | 4 | 4 | 4 | 3 | 2 | D51, C4, C3, N-17 | — |
| 8 | **I-08** Chain-bound signed operations (the cross-chain replay and owner-0 cases) | T | 3.80 | 3 | 2 | 5 | 5 | 1 | D52, D53, N-9 | — |
| 9 | **I-10** Selective-disclosure vehicle credentials (SD-JWT VC, BBS signatures) on the hot path | P | 3.80 | 4 | 3 | 4 | 4 | 2 | C5, C7, #26, #27 | — |
| 10 | **I-14** Property-based fuzzing of the message verifier | A | 3.80 | 3 | 2 | 5 | 5 | 1 | D37, D38, D39, D40, D41, D42 | — |
| 11 | **I-21** Side-paper pipeline | W | 3.80 | 3 | 2 | 5 | 5 | 1 | SP-1, SP-2, SP-7, SP-8 | — |
| 12 | **I-25** Substrate study: database, anchored journal, permissioned chain and rollup for vehicle identity (author focus F2) | R | 3.80 | 4 | 3 | 4 | 4 | 2 | C1, N-11, #33, #21, D62 | — |
| 13 | **I-04** Infrastructure trust mesh (RSU-to-RSU revocation propagation and handover) | T | 3.65 | 4 | 4 | 3 | 4 | 3 | C3, N-16, N-17, #46 | I-05 |
| 14 | **I-18** Research-claims CI as a reusable toolkit | E | 3.65 | 3 | 3 | 4 | 5 | 2 | D49, D33, D50 | — |
| 15 | **I-11** Linkability beyond the ledger (timing, position and pseudonym-change attacks) | P | 3.50 | 4 | 4 | 3 | 3 | 3 | C7, #38, SC-12 | I-01 |
| 16 | **I-12** Formal properties of the identity contracts | A | 3.50 | 3 | 3 | 4 | 4 | 2 | D53, D54, #28, C1 | — |
| 17 | **I-07** Misbehaviour detection to revocation, end to end | T | 3.45 | 4 | 3 | 3 | 4 | 3 | C4, C3, SC-03, #46 | I-05, I-01 |
| 18 | **I-20** Notebook intake into labelled extension slots | E | 3.45 | 4 | 3 | 3 | 3 | 2 | N-11 | — |
| 19 | **I-17** Vehicle credentials in the EU digital identity wallet framework | S | 3.40 | 3 | 4 | 4 | 2 | 2 | C5, C6 | — |
| 20 | **I-19** Open testbed release | E | 3.40 | 3 | 1 | 4 | 5 | 1 | N-2, N-11 | — |
| 21 | **I-06** Hybrid PKI and DID (IEEE 1609.2 certificates anchored to decentralized identifiers) | T | 3.30 | 4 | 4 | 2 | 4 | 4 | SC-03, C1, C2, #27 | — |
| 22 | **I-15** MOBI VID conformance completion and standards engagement | S | 3.30 | 3 | 2 | 4 | 4 | 2 | C6, SC-17, SC-18, SP-4, SP-1 | — |
| 23 | **I-22** An evidence-grounded explainer over the claim register | W | 3.05 | 2 | 3 | 4 | 4 | 3 | C1, C8 | I-18 |
| 24 | **I-02** Channel access in the latency budget (C-V2X mode 4 or 802.11p via ns-3 / OMNeT++ Veins) | R | 2.95 | 4 | 3 | 2 | 3 | 4 | C2, #27, SC-03 | I-01 |
| 25 | **I-09** Zero-knowledge VIN tier | P | 2.90 | 3 | 5 | 2 | 2 | 4 | SC-12, C7, SP-3 | — |
| 26 | **I-23** Hardware path (OBD-II/CAN data and a real RSU or V2X radio) | R | 2.15 | 3 | 3 | 1 | 2 | 5 | C2, C3 | I-01, I-02 |

## Tracks

| Track | Theme | Ideas |
|---|---|---|
| R | Realism of the evaluation (mobility, radio, public chains) | I-01, I-02, I-03, I-23, I-25, I-26 |
| T | Trust and revocation architecture | I-04, I-05, I-06, I-07, I-08, I-24 |
| P | Privacy of vehicle identity | I-09, I-10, I-11 |
| A | Assurance (formal methods, model checking, fuzzing) | I-12, I-13, I-14 |
| S | Standards and industry alignment | I-15, I-16, I-17 |
| E | Evidence platform and open release | I-18, I-19, I-20 |
| W | Writing, dissemination and interfaces | I-21, I-22 |

## Candidate programmes (decision P2-D1)

| Programme | Ideas | Mean total | Effect on the thesis cruxes |
|---|---|---:|---|
| **PG-focus** The author's three focuses (designated 2026-10-14, not chosen by score) | I-24, I-25, I-26 | 4.07 | F1 concept and F3 taxonomy enter chapter 6 with existing rows; measured studies follow the thesis (scope reconciliation) |
| **PG-alpha** Realistic deployment evidence | I-01, I-02, I-03, I-11 | 3.61 | moves C2, C3 and C7 off mock mobility and local chains |
| **PG-beta** Trust and revocation science | I-05, I-04, I-07, I-13 | 3.85 | gives C3 and C4 a model, a design and a proof obligation instead of only measurements |
| **PG-gamma** Privacy-preserving vehicle credentials | I-10, I-09, I-11, I-17 | 3.40 | gives C7 a hypothesis and C5 a second credential suite |
| **PG-delta** Assured identity contracts and verifiers | I-12, I-13, I-14, I-08 | 3.74 | turns the security results (#28) from tested to partly proved |
| **PG-strand** Continuous strands (run beside any programme) | I-16, I-18, I-21, I-20, I-19 | 3.68 | external validity, method contribution, dissemination, author intake |

## Idea cards

### I-01 — Real mobility drives the existing V2V/V2I layer (SUMO + TraCI)
*Track R · rank 4 · total 4.05*

- **Question.** Do verification load, freshness behaviour and the infrastructure results (#44-#46) change when vehicle positions, densities and contact times come from a traffic simulation instead of mock mobility?
- **Why (Phase 1).** Every latency and freshness result of Phase 1 is under mock mobility; the crux register names this the main gap of C2 and C3.
- **Anchors.** C2, C3, N-4, SC-22, #27, #44
- **Builds on.** `cv2x-testbed/sumo/sumo_identity_integration.py`, `cv2x-testbed/sumo/infrastructure_layer.py`, `docs/PLAN_SUMO_VISUALISATION.md`
- **First step.** A TraCI mobility adapter behind the mock-mobility interface the drivers already use; one scenario (S1) replayed under both; compare the per-vehicle neighbour-count distribution.
- **Kill criterion.** If the neighbour-count and contact-time distributions match the mock within a band set before the run, keep mock mobility and record the comparison as the result.
- **Needs:** nothing · **needed by:** I-02, I-07, I-11, I-23

### I-02 — Channel access in the latency budget (C-V2X mode 4 or 802.11p via ns-3 / OMNeT++ Veins)
*Track R · rank 24 · total 2.95*

- **Question.** How much of the 100 ms safety budget is left for identity verification once channel access, packet loss and retransmission are simulated?
- **Why (Phase 1).** Phase 1 verifies within the budget computationally (#27) but has no radio or MAC; chapter 5 names the end-to-end budget as future work.
- **Anchors.** C2, #27, SC-03
- **Builds on.** `docs/thesis/chapter5-results/README.md`, `cv2x-testbed/sumo/run_v2v_stats.py`
- **First step.** A spike that couples one simulator to the existing message path for a two-vehicle exchange and measures integration effort, before any experiment is designed.
- **Kill criterion.** If the spike needs more than two sessions to exchange one signed message, move to a literature-calibrated channel model instead.
- **Needs:** I-01 · **needed by:** I-23

### I-03 — Public-chain witness and rollup economics
*Track R · rank 5 · total 3.95*

- **Question.** Do the nine-standard gas rankings hold on a public testnet and on an L2 rollup, and what does a vehicle identity cost in fees over its life once calldata pricing and blob fees apply?
- **Why (Phase 1).** All gas is local (M1); chapter 6 leaves the dollar calibration of the cost frontier to future work; v0.9.0 is defined by a Sepolia witness.
- **Anchors.** N-11, #25, #26, C1
- **Builds on.** `1_blockchain-identity/scripts/validate_sepolia.js`, `1_blockchain-identity/SEPOLIA_VALIDATION.md`, `1_blockchain-identity/scripts/benchmark_gas.js`, `docs/thesis/chapter6-discussion/README.md`
- **First step.** Run the existing Sepolia validation (author decision N-11: secrets), then the benchmark on one rollup testnet with the same contracts; compare rankings, not absolute numbers.
- **Kill criterion.** None needed for the witness; the rollup arm stops if the ranking is unchanged and fee data cannot be stated under a dated condition.
- **Needs:** nothing · **needed by:** nothing

### I-04 — Infrastructure trust mesh (RSU-to-RSU revocation propagation and handover)
*Track T · rank 13 · total 3.65*

- **Question.** How quickly does a revocation reach every RSU on a corridor, and what does a vehicle crossing RSU boundaries experience, when RSUs exchange revocation state peer to peer instead of each reading the chain?
- **Why (Phase 1).** C3 lists "no RSU-to-RSU" among its five gaps; N-16 asks for a design note first.
- **Anchors.** C3, N-16, N-17, #46
- **Builds on.** `cv2x-testbed/sumo/infrastructure_layer.py`, `docs/design`
- **First step.** The N-16 design note (WM-2 D2) extended into a protocol sketch with two candidate propagation rules and the metric each would be judged by.
- **Kill criterion.** If the design note shows the thesis claims for C3 do not need it, it stays a Phase 2 study, not a thesis chapter.
- **Needs:** I-05 · **needed by:** nothing

### I-05 — A theory of revocation freshness (k, time bounds and their optimum)
*Track T · rank 1 · total 4.45*

- **Question.** Given a revocation rate, a verification cost and a chain-read cost, which re-check policy minimises cost subject to a bound on accepting a revoked credential, and does the measured knee (#32, #37) match it?
- **Why (Phase 1).** Phase 1 measures k empirically and states that a message bound is not a time bound (guide 1.1.9); the thesis must still choose k (C4, N-17), and D51 shows the clock matters.
- **Anchors.** C4, N-17, D51, #32, #37, #46
- **Builds on.** `cv2x-testbed/identity/freshness.py`, `cv2x-testbed/scripts/experiment_freshness_k.py`, `docs/STYLE_AND_RIGOUR_GUIDE.md`
- **First step.** Write the cost model on paper with its assumptions, derive the optimal policy for message-bounded and time-bounded caches, and predict the knee for the Phase 1 conditions before re-reading the measurements.
- **Kill criterion.** If the model cannot predict the measured knee within its own stated error, report the mismatch and use it to choose k by rule, not to claim a theory.
- **Needs:** nothing · **needed by:** I-04, I-07

### I-06 — Hybrid PKI and DID (IEEE 1609.2 certificates anchored to decentralized identifiers)
*Track T · rank 21 · total 3.30*

- **Question.** Can a vehicle keep 1609.2-style pseudonym certificates on the hot path while the issuing authority's keys and revocation live in a DID registry, and what does it cost against each pure design?
- **Why (Phase 1).** Phase 1 measures PKI and SSI side by side (#27); V2 question 8 (hybrid) was demoted to future work as PhD-scale (SC-03).
- **Anchors.** SC-03, C1, C2, #27
- **Builds on.** `cv2x-testbed/identity/standard/pki_identity.py`, `cv2x-testbed/identity/erc1056_provider.py`, `cv2x-testbed/V2_DESIGN.md`
- **First step.** A scoped design (one authority, one revocation path) with its threat model, to size whether it is MASc-sized or must stay future work.
- **Kill criterion.** If the scoped design needs a new SCMS baseline to be meaningful, keep it as a written proposal.
- **Needs:** nothing · **needed by:** nothing

### I-07 — Misbehaviour detection to revocation, end to end
*Track T · rank 17 · total 3.45*

- **Question.** How long from a detectable misbehaviour to a revoked identity being refused by every verifier, and which link dominates (detection, governance, chain inclusion, freshness)?
- **Why (Phase 1).** Phase 1 measures the freshness end of this chain only; V2 question 9 (ML misbehaviour detection) was demoted (SC-03).
- **Anchors.** C4, C3, SC-03, #46
- **Builds on.** `cv2x-testbed/identity/freshness.py`, `cv2x-testbed/sumo/infrastructure_layer.py`, `cv2x-testbed/V2_COMPLETE_ROADMAP.md`
- **First step.** A time-to-exclusion decomposition with a rule-based detector (no ML) and the existing freshness policy, as a design and measurement plan.
- **Kill criterion.** If detection quality dominates and cannot be measured without real data, narrow to "time from decision to exclusion".
- **Needs:** I-05, I-01 · **needed by:** nothing

### I-08 — Chain-bound signed operations (the cross-chain replay and owner-0 cases)
*Track T · rank 8 · total 3.80*

- **Question.** What does binding the chain id into ERC-1056 signed operations cost, and is a byte-faithful upstream registry defensible for vehicles given D52?
- **Why (Phase 1).** D52 (no chain id in the signed digest) and D53 (owner 0) are open design questions tied to the upstream-fidelity decision (N-9, review-2 K-12).
- **Anchors.** D52, D53, N-9
- **Builds on.** `1_blockchain-identity/contracts`, `docs/DEFECT_LOG.md`
- **First step.** A variant contract beside the upstream one, its regression tests (each failing on the upstream), and the gas delta per signed operation.
- **Kill criterion.** None; small and bounded. It feeds N-9.
- **Needs:** nothing · **needed by:** nothing

### I-09 — Zero-knowledge VIN tier
*Track P · rank 25 · total 2.90*

- **Question.** Can a vehicle prove VIN-bound properties (manufacturer, model year, registration region) without revealing the VIN or a linkable hash, at a verify cost inside the V2V budget?
- **Why (Phase 1).** The three-tier VIN privacy design left the ZK tier as future work (SC-12); SP-3 covers the hash-and-encrypt tiers only.
- **Anchors.** SC-12, C7, SP-3
- **Builds on.** `MOBI_VID_RESEARCH.md`, `cv2x-testbed/scripts/test_vin_encryption.py`
- **First step.** A literature and tooling survey (circuit size, proving and verifying time for the three properties) before any circuit is written.
- **Kill criterion.** If verification cannot fit the budget on vehicle-class hardware per the literature, keep it as an off-hot-path (registration-time) proof only.
- **Needs:** nothing · **needed by:** nothing

### I-10 — Selective-disclosure vehicle credentials (SD-JWT VC, BBS signatures) on the hot path
*Track P · rank 9 · total 3.80*

- **Question.** What do selective-disclosure credential formats cost to verify against the current VC suite, and which disclosures does a V2V or V2I verifier actually need?
- **Why (Phase 1).** C5 is structural and C7 has no hypothesis; Phase 1 measured credential richness against verify time (#26, #27) for one suite only.
- **Anchors.** C5, C7, #26, #27
- **Builds on.** `2_w3c-ssi-layer/verifiable-credentials`, `4_comparison-framework/performance-metrics/run_verify_richness.py`
- **First step.** A disclosure-needs table per message type (BSM, SPaT, MAP) written from the existing message schemas, then one SD-JWT VC prototype measured with the richness driver.
- **Kill criterion.** If no message type needs selective disclosure on the hot path, the idea moves to registration and service-access flows.
- **Needs:** nothing · **needed by:** nothing

### I-11 — Linkability beyond the ledger (timing, position and pseudonym-change attacks)
*Track P · rank 15 · total 3.50*

- **Question.** With real mobility, how linkable are a vehicle's pseudonyms through timing and position alone, and how much does each Phase 1 identity design add or remove?
- **Why (Phase 1).** C7 records radio, timing and position linkability as future work; the pseudonym-pool experiment found the delegate pool fully linkable on-chain.
- **Anchors.** C7, #38, SC-12
- **Builds on.** `1_blockchain-identity/scripts/experiment_pseudonym_pool.js`, `docs/thesis/CRUX_REGISTER.md`
- **First step.** Choose one published linkability metric and one tracker, applied to SUMO traces with identity overlays; pre-register the comparison.
- **Kill criterion.** If real mobility (I-01) is not available, stop: mock positions would measure the mock.
- **Needs:** I-01 · **needed by:** nothing

### I-12 — Formal properties of the identity contracts
*Track A · rank 16 · total 3.50*

- **Question.** Which security properties (owner-only mutation, revocation monotonicity, no identity seizure) can be proved for the nine contracts with off-the-shelf tools, and do the proofs find what the attack harness missed?
- **Why (Phase 1).** Chapter 7 lists formal verification as future work; D53 (owner 0) and D54 (attestation authority) were found by reading, not by the 43-cell attack harness (#28).
- **Anchors.** D53, D54, #28, C1
- **Builds on.** `1_blockchain-identity/contracts`, `4_comparison-framework/security-analysis`, `docs/thesis/chapter7-conclusion/README.md`
- **First step.** Three properties stated in prose for two contracts, then checked with the Solidity compiler's model checker and one symbolic tool; D53 used as the must-find target.
- **Kill criterion.** If neither tool finds D53 on the unfixed contract, report the tool limitation and stop.
- **Needs:** nothing · **needed by:** nothing

### I-13 — Model checking the revocation and cache protocol
*Track A · rank 7 · total 3.85*

- **Question.** Does a formal model of verifier caches, RSU caches and chain time admit a run in which a revoked key is accepted, and under which clock assumptions?
- **Why (Phase 1).** D51 (clock skew accepts a revoked key) is exactly the kind of interleaving a model checker finds; C3 and C4 rest on cache rules nobody has modelled.
- **Anchors.** D51, C4, C3, N-17
- **Builds on.** `cv2x-testbed/identity/erc1056_provider.py`, `cv2x-testbed/identity/freshness.py`
- **First step.** A small TLA+ or PlusCal model of one verifier, one chain and one revocation, required to rediscover D51 before it is extended to RSUs.
- **Kill criterion.** If the model cannot rediscover D51, it is not modelling the system; stop.
- **Needs:** nothing · **needed by:** nothing

### I-14 — Property-based fuzzing of the message verifier
*Track A · rank 10 · total 3.80*

- **Question.** What does property-based fuzzing of the infrastructure verifier find beyond the six robustness defects the audit found by hand?
- **Why (Phase 1).** D37-D42 were found by auditors reading code; the verifier v3 (WM-2 C0) will fix them, and a fuzzer is the regression net.
- **Anchors.** D37, D38, D39, D40, D41, D42
- **Builds on.** `cv2x-testbed/sumo/infrastructure_layer.py`, `sandbox/py-suites/L3-ssi/mutation/mutate_infrastructure_layer.py`
- **First step.** Hypothesis strategies for SPaT/MAP/BSM messages and credentials; required to rediscover D37 and D39 on the pre-v3 code.
- **Kill criterion.** None; it becomes part of the test suite.
- **Needs:** nothing · **needed by:** nothing

### I-15 — MOBI VID conformance completion and standards engagement
*Track S · rank 22 · total 3.30*

- **Question.** What would full VID I MUST coverage take, and which Phase 1 findings (fidelity per backend, the attestation fix) are contributions MOBI could adopt?
- **Why (Phase 1).** C6 records few VID I MUSTs met and missing birth-certificate fields; SC-17 and SC-18 are pending; chapter 7 lists standardization engagement.
- **Anchors.** C6, SC-17, SC-18, SP-4, SP-1
- **Builds on.** `MOBI_VID1_TECHNICAL_SPEC.md`, `2_w3c-ssi-layer/mobi-vid`
- **First step.** A MUST-by-MUST gap table from the v2.0 text with effort per row.
- **Kill criterion.** If the remaining MUSTs are organisational, not technical, report coverage and stop.
- **Needs:** nothing · **needed by:** nothing

### I-16 — W3C external validity on chain-backed documents
*Track S · rank 3 · total 4.10*

- **Question.** Do the official DID and VC test suites still pass when the resolver reads chain state instead of synthesising the document from the identifier?
- **Why (Phase 1).** C5 rests on a synthesised document; the 94.3 % figure is a structural self-score (#4); WM-2 C1 makes the resolver read the chain.
- **Anchors.** C5, #4, #24
- **Builds on.** `2_w3c-ssi-layer/did-resolution`, `docs/conformance`, `cv2x-testbed/scripts/w3c_compliance_checker.py`
- **First step.** After WM-2 C1, re-run the external suite (#24) against the chain-reading resolver and add the VC data-model suite.
- **Kill criterion.** None; it is the natural follow-up of C1.
- **Needs:** nothing · **needed by:** nothing

### I-17 — Vehicle credentials in the EU digital identity wallet framework
*Track S · rank 19 · total 3.40*

- **Question.** How do Phase 1's vehicle credentials map onto the EU digital identity wallet architecture (issuers, relying parties, trust lists), and what is missing for a vehicle as a credential holder?
- **Why (Phase 1).** Phase 1 is grounded in W3C and MOBI only; a regulatory mapping widens the thesis's external relevance (C5, C6).
- **Anchors.** C5, C6
- **Builds on.** `MOBI_VID2_SSI_DESIGN.md`, `2_w3c-ssi-layer/verifiable-credentials`
- **First step.** A mapping table from canonical sources (the architecture reference framework), written as a desk study.
- **Kill criterion.** If the framework has no notion of a non-person holder that fits, record that as the finding.
- **Needs:** nothing · **needed by:** nothing

### I-18 — Research-claims CI as a reusable toolkit
*Track E · rank 14 · total 3.65*

- **Question.** Can the Phase 1 evidence machinery (run stamps with per-producer scope, promote, claim register, stale-figure check) be packaged so another research codebase can adopt it, and does it catch real faults there?
- **Why (Phase 1).** Phase 1 built it to make its own claims checkable (tools/run_identity, docs/testing); its guards were each shown to fire; that is a methods contribution in its own right.
- **Anchors.** D49, D33, D50
- **Builds on.** `tools/run_identity/stamp.py`, `tools/run_identity/promote.py`, `docs/testing/check_stamps.py`, `docs/testing/check_docs_numbers.py`, `docs/MEASUREMENT_CONDITIONS.md`
- **First step.** An interface sketch (producer manifest, scope resolver, register schema) and one external codebase chosen as a pilot.
- **Kill criterion.** If the toolkit cannot be separated from this repository's layout without rewriting it, keep it internal.
- **Needs:** nothing · **needed by:** I-22

### I-19 — Open testbed release
*Track E · rank 20 · total 3.40*

- **Question.** What must a third party install and run to reproduce the headline results, and how long does it take a newcomer?
- **Why (Phase 1).** The original direction asks for an open-source testbed for a university connected-vehicles lab; the dashboard and grand runner exist.
- **Anchors.** N-2, N-11
- **Builds on.** `docs/ORIGINAL_PROMPT_AND_DIRECTION.md`, `sandbox/grand/run.py`, `docs/figures/results_dashboard.html`, `cv2x-testbed/V2_COMPLETE_ROADMAP.md`
- **First step.** A clean-machine reproduction script and a timed newcomer walkthrough; every failure becomes an issue.
- **Kill criterion.** None; it is a deliverable, gated by author decisions on licence and default branch (N-12).
- **Needs:** nothing · **needed by:** nothing

### I-20 — Notebook intake into labelled extension slots
*Track E · rank 18 · total 3.45*

- **Question.** Which of the author's notebook research threads attach to which Phase 1 artefact, and which need a new one?
- **Why (Phase 1).** The original direction reserves "extension slots" for the author's notebooks; the master update plans labelled slots in the thesis.
- **Anchors.** N-11
- **Builds on.** `docs/ORIGINAL_PROMPT_AND_DIRECTION.md`, `MASTER_UPDATE.md`
- **First step.** An intake template (thread, claim, evidence needed, Phase 1 anchor, Phase 2 idea it joins) for the author to fill; the register then grows from it.
- **Kill criterion.** None; it is the author's input channel into this register.
- **Needs:** nothing · **needed by:** nothing

### I-21 — Side-paper pipeline
*Track W · rank 11 · total 3.80*

- **Question.** Which side papers can be written from Phase 1 evidence alone, in which order, and to which venues?
- **Why (Phase 1).** SIDE_PAPERS.md lists eight; SP-1, SP-2, SP-3, SP-7 and SP-8 separate cleanly from the thesis.
- **Anchors.** SP-1, SP-2, SP-7, SP-8
- **Builds on.** `SIDE_PAPERS.md`, `docs/presentation/REPORT_DRAFT_1.md`
- **First step.** One-page outlines for SP-1 and SP-2 that cite only V rows, with the missing evidence named.
- **Kill criterion.** None; each paper is gated by its rows being V.
- **Needs:** nothing · **needed by:** nothing

### I-22 — An evidence-grounded explainer over the claim register
*Track W · rank 23 · total 3.05*

- **Question.** Can a question-answering interface answer an examiner's questions about the work using only register rows, cruxes and their sources, and refuse when no V row supports an answer?
- **Why (Phase 1).** The original sandbox brief included an LLM interface, later re-scoped as a possible defence demo; the register now gives it a ground truth to be held to.
- **Anchors.** C1, C8
- **Builds on.** `docs/ORIGINAL_PROMPT_AND_DIRECTION.md`, `docs/MEASUREMENT_CONDITIONS.md`, `docs/thesis/CRUX_REGISTER.md`
- **First step.** Twenty examiner-style questions with the rows that answer each, written by hand, as the evaluation set before any interface is built.
- **Kill criterion.** If the evaluation set shows answers need prose judgement the register does not hold, keep it as the question bank for defence preparation.
- **Needs:** I-18 · **needed by:** nothing

### I-23 — Hardware path (OBD-II/CAN data and a real RSU or V2X radio)
*Track R · rank 26 · total 2.15*

- **Question.** What is the smallest hardware-in-the-loop setup that tests one Phase 1 identity flow on a real radio or real vehicle data?
- **Why (Phase 1).** The realistic roadmap ends in real-world integration; it is the long-horizon form of I-01 and I-02.
- **Anchors.** C2, C3
- **Builds on.** `CV2X_REALISTIC_ROADMAP.md`
- **First step.** An equipment and access survey (lab radios, RSU loan, vehicle data) with costs; no build.
- **Kill criterion.** If no hardware is available within the degree's timeline, record as post-degree.
- **Needs:** I-01, I-02 · **needed by:** nothing

### I-24 — Identity-dependent transactions (IDTx): definition, taxonomy, measured cost and staleness (author focus F1)
*Track T · rank 2 · total 4.45*

- **Question.** What does conditioning a transaction on ledger-held identity state cost and risk, by dependency kind, storage locus, encoding, evaluation and continuation?
- **Why (Phase 1).** The author's coined concept; Phase 1 holds 25 implicit instances and measures the storage trade-off (#49, #35, #31) but never what a storage choice forbids.
- **Anchors.** C1, C8, D51, D54, D64, #49, #31
- **Builds on.** `docs/phase2/focus/F1_onchain_storage_idtx/ANALYSIS.md`, `phase2/idtx/contracts/IdtxExecutor.sol`
- **First step.** Done: the prototype with 12 behaviour tests (count corrected in session 3). Next: lock the F1 plan as a pre-registration and run E-F1-1 and E-F1-2.
- **Kill criterion.** If the measured overhead and the TOCTOU result add nothing beyond access control, keep IDTx as a taxonomy in chapter 6 and drop the paper.
- **Needs:** nothing · **needed by:** nothing

### I-25 — Substrate study: database, anchored journal, permissioned chain and rollup for vehicle identity (author focus F2)
*Track R · rank 12 · total 3.80*

- **Question.** The same lifecycle on four substrates: what does each cost, and what verification does each give a party who does not trust the operator?
- **Why (Phase 1).** Phase 1 ran one local chain and an in-memory registry (#33); gas transfers across EVM chains but latency and trust do not.
- **Anchors.** C1, N-11, #33, #21, D62
- **Builds on.** `docs/phase2/focus/F2_chains_and_databases/ANALYSIS.md`, `phase2/backends/sqlite_lifecycle.py`, `cv2x-testbed/identity/lifecycle_backends.py`
- **First step.** Done: the database backend with a hash-chained journal and 6 tests. Next: anchoring the journal head on chain (F2-S3).
- **Kill criterion.** If the author declines installing a permissioned client (P2-D9), run the three local substrates and state the gap.
- **Needs:** nothing · **needed by:** I-26

### I-26 — Modes of chain interaction (direct, mediated, detached) and mode selection per message class (author focus F3)
*Track R · rank 6 · total 3.95*

- **Question.** Which mode should each vehicle message class use, given latency, trust, privacy and staleness, and what does a verified mediated read cost?
- **Why (Phase 1).** Phase 1 measured direct and relayed writes (#50) and three read modes (#21, #37, #27) but never a provider-served read or a detached write.
- **Anchors.** C2, C3, C4, #50, #27, #37, D52, D61
- **Builds on.** `docs/phase2/focus/F3_interaction_modes/ANALYSIS.md`, `docs/phase2/focus/F3_interaction_modes/classify_modes.py`
- **First step.** Done: the generated classification. Next: the author's choice of taxonomy (P2-D7), then the detached-write prototype (E-F3-3).
- **Kill criterion.** None for the taxonomy; the provider arm waits for N-11.
- **Needs:** I-25 · **needed by:** nothing
