# Scope Reconciliation — The Thesis Scope Across Its Revisions, and Where Phase 2 Belongs

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2; drafted by the review team's academic adviser role, accepted by the orchestrator after verification)
**Binds:** docs/phase2/README.md; docs/STYLE_AND_RIGOUR_GUIDE.md
**Supersedes:** nothing. It is step SC of after-action report 16.
**Sources read:** `docs/ORIGINAL_PROMPT_AND_DIRECTION.md` (§A to §C), `docs/SCOPE_CHANGES.md`, `docs/thesis/README.md`,
`docs/thesis/SCAFFOLD.md`, chapters 1 and 7, `docs/thesis/CRUX_REGISTER.md`, `README.md`, `SIDE_PAPERS.md`,
`docs/AUDIT_01_ORIGINAL_GOALS.md`, `docs/milestones/WM-1_REPORT.md`, `docs/PLAN_WM-2.md`, `docs/phase2/` (charter,
evidence base, idea register, decisions, roadmap, brainstorm 1), the claim register `docs/MEASUREMENT_CONDITIONS.md`,
and the chapter 6 draft `section-feature-asymmetry.md`.
**Numbers:** every number below is quoted from a claim-register row (#n, status V unless stated) or from the file
named beside it. This memo adds no measurement. The focus folders named in report 16 (`docs/phase2/focus/`) were not
yet committed when this was written, so the placements rest on Phase 1 evidence, not on those documents.

---

## 0. Executive summary

The thesis has a defensible core, and it is narrower than its own chapters say.
A crux is a question an examiner is expected to ask, logged in `docs/thesis/CRUX_REGISTER.md`.

**The core.**

| What the core contains | Crux |
|---|---|
| A measured, same-testbed comparison of nine Ethereum identity standards on one vehicle lifecycle | C1 |
| A credential layer expressed in W3C structures, scored structurally and against the external DID suite | C5 |
| Evidence that the verification step of V2V and V2I messages fits the computational share of the safety budget when the chain is kept off the hot path | C2, C3 |
| A price for revocation freshness | C4 |

All eight cruxes are partial; none is empty; none is fully evidenced.

**How the scope got here.** It was stated twice before.
The first statement was questions and hypotheses, in June and July 2026.
The second was by subtraction, through the audit, the scope-change log and the crux register, in September and October.
The second attempt narrowed every claim but never rewrote the questions.
So chapters 1 and 7 still carry first-attempt words ("first", "throughput", "conformance", "all five supported").

**Recommendation.** I recommend a third statement, Scope v3 (§2):
- four restated questions;
- split verdicts for H1 and H5;
- a freeze at the close of work milestone WM-2 plus, at most, the Sepolia witness, a public-testnet run.

The Phase 2 focuses enter the thesis as follows, and each then gets its own paper after the defence (§4).

| Focus | Enters the thesis as |
|---|---|
| F1 | a storage-locus lens, and a definition and taxonomy of the identity-dependent transaction (IDTx), with no new number |
| F2 | only the centralised and PKI baselines already measured |
| F3 | a classification of the read and write paths already measured |

**The largest risk** to the defence is not scope at all.
It is the unwritten literature review (chapter 2), which IDTx makes more urgent, not less.

---

## 1. The scope as it evolved

### 1.1 Successive statements

| # | Statement (date, file) | What was in | Dropped or demoted, and why |
|---|---|---|---|
| S0 | Sandbox brief, 2025-11-10 (`ORIGINAL_PROMPT_AND_DIRECTION.md` §A.1) | two-stage sandbox, stages 0 to 10, an LLM interface, generic DB/cloud/API hooks, "six implementation variations of CVIN-ID"; the kernel: read a credential or identity on or off chain, then act on or off chain | the LLM interface was never built and is re-scoped as a possible defence demo (§C, review §5.8); the hooks survived as the `IdentityProvider` abstraction (§C) |
| S1 | First testbed questions, 2025-11-10 (§A.2) | DID vs PKI latency; chain query vs CRL; pseudonyms vs DIDs; network impact | questions 1 and 2 measured (#21); question 3 deferred (SC-02) then bounded (#38); question 4 out by design, no channel model (§C) |
| S2 | V2 mission, 2025-11-10 (§A.3) | a "research-grade platform", ten questions, SUMO, a channel model | three questions promoted, seven demoted as PhD-scale (SC-03; audit §1.5) |
| S3 | Roadmap mission, 2025-11-10 (§A.4) | PKI vs MOBI VID; five questions with hypotheses; success criteria | position-falsification detection deferred (SC-01: not an identity-layer question); privacy analysis deferred, later bounded (SC-02); trust user study left as future work; of the criteria, 13 met, 9 partial, 1 open, 2 dropped (§C) |
| S4 | MOBI VID design, 2025-11-10 (§A.5) | ERC-1056 base; VID I with three-tier VIN privacy; VID II as VCs; a centralised parity baseline; ten use cases | ZK VIN tier deferred (SC-12); key-management controls out (SC-15); government identity out (SC-16); "conformance" narrowed to "MOBI-VID-inspired, checked against the public texts" (SC-14, SC-14a: 2 of 8 VID I MUSTs met, per `docs/MOBI_VID_CHECKLIST.md`); SC-17, SC-18, SC-20 still pending |
| S5 | Thesis statement, 2026-06-21 (§A.6) | RQ1 to RQ4; one compound hypothesis; five contributions, two of them "first" | compound hypothesis replaced by H1 to H5 (audit F6); "first" to be reworded (SC-04, pending); "throughput" undecided (SC-05, pending); nine standards made true on the trunk by the merge (SC-07) |
| S6 | Five thrusts and H1 to H5, 2026-07-05 (§A.7) | falsifiable hypotheses per thrust | none dropped; H1 and H5 later narrowed by the evidence (#30, #36) |
| S7 | Audit and scope-change era, 2026-09-24 to 2026-10-06 (`AUDIT_01_ORIGINAL_GOALS.md`; `SCOPE_CHANGES.md` SC-01 to SC-20) | claim register; PKI baseline (#21); external W3C suite (#24); merge of the nine-standard lineage | see §1.2 for the grouped scope changes |
| S8 | WM-1 and WM-2 era, 2026-10-09 to now (`WM-1_REPORT.md`; `PLAN_WM-2.md`) | crux register C1 to C8; infrastructure messaging added and pre-registered (SC-21, #44 to #48); a results pipeline of record | SUMO deferred (SC-22); H5 claimed less strongly and W3C renamed a "structural self-score" after the audit (WM-1 report §0); WM-2 admits no new experiment (§6) |
| S9 | Phase 2 opened, 2026-10-14 (`docs/phase2/README.md`) | 23 ideas in 7 tracks; five candidate programmes; then F1, F2, F3 (report 16) | nothing chosen yet (P2-D1 open) |

### 1.2 The scope changes, grouped

| Group | Entries | Effect on the thesis |
|---|---|---|
| Deferred or out of scope | SC-01, SC-02 (partly closed by #38), SC-03, SC-12, SC-15, SC-16, SC-19, SC-22 | each is a sentence in chapter 7 §7.5 or §7.6; most are not there yet |
| Claims narrowed | SC-04 (pending), SC-06 (pending), SC-10, SC-14, SC-14a | the wording of chapters 1, 5 and 7 must follow; chapter 1 still says "first" |
| Implementation corrected | SC-08, SC-09, SC-11 | chapter 4 reports them as findings |
| Closed by measurement | SC-07, SC-13 (#33) | evidence exists. SC-13 cites "register #30"; the parity row is #33. Append a correction entry; do not edit the past one |
| Pending author decisions | SC-05, SC-06, SC-17, SC-18, SC-20 | they block the freeze of chapters 3 and 4 |
| Added | SC-21 (infrastructure, bounded) | crux C3 exists because of it |

### 1.3 Which were the first and second attempts

The statements S0 to S4 were missions: briefs for what to build, not claims to defend.
They are honest ancestors, and one of them matters more than it looks.
The S0 kernel ("read something like a credential or identity on- or off-chain and then either do something on-chain … or something off chain") already contains F1, F3 and the IDTx in seed form.
The new focuses are therefore not drift; they are the original question coming back with evidence behind it.

**The first attempt at a scope is S5 with S6.**
It was the first time the work had questions, falsifiable hypotheses and contributions.
Its weakness was ambition by assertion: "first", "throughput", "full W3C compliance", "viable alternative to PKI".

**The second attempt is S7 with S8.**
It is a scope by subtraction: recorded drops, narrowed claims, and the cruxes as the examiner's questions.
It is much the better of the two, and it is the reason the work is defensible at all.
Its weakness is that it never restated the questions positively, and it placed the cruxes beside the RQs without mapping one onto the other.

The drift that the second attempt left behind is visible in the drafts:

| Where | Says | The evidence says | Fix |
|---|---|---|---|
| Ch. 1 §1.2 and §1.4 item 1; ch. 7 §7.1 and §7.4 | "first" nine-standard comparison | SC-04 pending; audit §4 cites a 2025 SSI V2V authentication chapter | "measured, same-testbed, domain-constrained, reproducible" |
| Ch. 1 RQ1 | "storage/throughput implications" | throughput exists only in #39, status U; `README.md` RQ1 already dropped the word | cut "throughput" (SC-05) |
| Ch. 1 §1.3 preview; ch. 7 §7.3 | "all five hypotheses supported" | ch. 1's own note: the update half of H1 is not supported; lifetime margins are 2.58× and 3.00× (#30); CVIN-Combined is dominated by ERC-4337 on all six harness criteria (#36) | split verdicts (§2.3) |
| Ch. 1 RQ3 and contribution 2; thesis README "W3C Compliant System" | "conformance", "compliant" | 94.3 % is a structural self-score (#4, audit U-F4); the external DID suite gives 335/336 generated tests (#24) | "expressed in W3C structures; structural score; external suite" |
| Ch. 7 §7.5 | five limitations | missing: D51 (a revoked key verifies when the verifier's clock lags the chain by more than 900 s; register note), synthesised DID documents (C5), MOBI MUST coverage (C6), mock mobility for V2I (C3) | add them |
| Ch. 1 §1.3 | four RQs, five hypotheses | C3 and C7 have no hypothesis and no RQ | attach them to RQ4 and RQ2 as pre-registered questions; do not add post-hoc hypotheses (guide 1.2.1) |

**The third attempt, now, should be one positive and narrow statement** that maps each RQ to its hypothesis, its cruxes and its V rows, and places Phase 2 outside the thesis explicitly, with a reason for each placement.
That is §2 and §3.

---

## 2. Scope v3 (proposed)

### 2.1 The thesis statement in one paragraph

This thesis measures, on one testbed and under declared conditions, what it costs and what it buys to root a connected vehicle's identity in each of nine Ethereum identity standards.
It reports cost per operation and over a lifecycle, the security properties an executable harness can test, how far the identities can be expressed in W3C DID and VC structures and a MOBI-VID-inspired lifecycle, and whether the verification step of vehicle and roadside messages fits the computational share of the safety budget once revocation freshness is priced.
It claims nothing about radio, real mobility, public-network latency or fiat cost.

A possible title, for the author's decision (D-14): *Measured Trade-offs of Ethereum Identity Standards for Connected Vehicles: Cost, Credential Structure and Real-Time Verification*.

### 2.2 Research questions, restated to the evidence

| RQ | Restated question | V rows that answer it | Cruxes | WM-2 step that must land first |
|---|---|---|---|---|
| RQ1 Cost and storage locus | How do nine Ethereum identity standards compare in gas for an identical operation catalogue and a 17-event lifecycle, and what on-chain state does each keep for that price? | #6, #25, #26, #34, #35, #36 | C1, C8 | A6 (harness run of record re-stamped) |
| RQ2 Security and observability | Which attacks does each standard's contract surface resist under an executable harness, what does each lack (recovery, identity-level revocation), and what does a passive chain observer learn? | #28, #38 | C7, C8 | C2 (restricted attestation), A3b (#38 re-run) |
| RQ3 Standards expression | How far can chain-rooted identities be expressed in W3C DID Core and VC Data Model structures and in a MOBI-VID-inspired lifecycle, judged by an internal structural checker, the external DID test suite and a clause-level checklist? | #4, #24, #30, #33 | C5, C6 | C1 (resolver reads the chain; #24 and #4 re-run) |
| RQ4 Real-time verification | Does the verification step of V2V and V2I messages fit the computational share of the safety budget when identities are rooted on chain, and what does keeping revocation fresh cost? | #21, #27, #32, #37, #44 to #48 | C2, C3, C4 | C0 (verifier v3, D51 fix, I1 to I3 re-run), C3 (#32 and #37 back to back), A3b |

### 2.3 Hypotheses and pre-registered questions, with the verdicts the evidence allows

| Item | Restated | Verdict to report | Evidence |
|---|---|---|---|
| H1 | Minimal-state standards are at least 10× cheaper than rich-state ones to create a vehicle identity | **split.** Creation: supported under the stated definition (52,594 vs 545,101 = 10.4×; 6.9× with the VIN bound on both sides). Update and lifetime: not supported; ERC-1056 is cheapest over the lifecycle by 1.20× to 5.52×, not 10× (the 1.20× is against an ERC-1155 total that omits two events it lacks) | #6, #25, #35 |
| H2 | At least 90 % on the internal structural checker, with residual gaps confined to documented deviations | supported as a structural self-score (94.3 %; 41 PASS, 1 PARTIAL, 2 FAIL of 44); the external DID suite passes 335/336 | #4, #24 |
| H3 | Off-chain verification of pre-issued credentials fits the budget; chain reads at message time do not | supported for the verification step: SSI warm 0.153 ms [0.151, 0.154]; uncached ERC-1056 verify 9.654 ms median | #21, #27 |
| H4 | The MOBI-VID-inspired lifecycle is realisable across backends with a fidelity gradient | supported with the gradient stated | #30; `mobi_vid_backends.json` (re-executed per #43) |
| H5 | No standard dominates; the hybrid's position depends on the criteria | **split.** No dominance: supported. Hybrid: on the fidelity-per-gas plane among the MOBI backends, yet dominated by ERC-4337 on all six harness criteria | #36 |
| I1 to I5 | pre-registered infrastructure questions, no hypothesis | as registered: I1 outside band, not falsified (ratio 1.226 on verifier v3; it was 1.096, PASS, on v2; corrected 2026-10-14 after the WM-2 C0 re-run), I2 PASS (15 checks, 30/30 runs), I3 PASS (at most k − 1 messages), I4 and I5 reported | #44 to #48 |
| M4, M5 | pre-registered parity and pseudonymity questions | M4 writes PASS, "equal once cached" FAIL; M5 gas FAIL, linkability PASS (60/60 pseudonyms by one query) | #33, #38 |

Reporting the two failed halves and the two FAIL verdicts plainly is a strength at a defence.
It shows the hypotheses could fail, which is the property examiners test first.

### 2.4 Cruxes mapped to Scope v3

| Crux | RQ | What closes it before the defence | What stays a stated limitation |
|---|---|---|---|
| C1 Substrate | RQ1 | H5 wording reconciled with #36; the ERC-735 "veracity has a deployment price" sentence; A6 | local gas only (M1); the Sepolia witness if N-11 allows |
| C2 V2V | RQ4 | A3b re-runs of #21 and #27 on the trunk | mock mobility; no radio or MAC |
| C3 V2I and I2I | RQ4 | C0 verifier v3 and the I1 to I3 re-run; D2 design note decides RSU-to-RSU (recommend: scope out) | in-process back-haul and registry; a message count, not a time |
| C4 Freshness | RQ4 | the D51 fix (C0); #32 and #37 back to back (C3); the k the thesis defends (D-12) | host dependence of the knee |
| C5 W3C | RQ3 | C1 chain-reading resolver; #24 and #4 re-run; "structural" wording | one credential suite only |
| C6 MOBI VID | RQ3 | SC-17, SC-18, SC-20 recorded as deviations | MUST coverage; v1.0 text not assessable |
| C7 Privacy | RQ2 | #38 re-run (A3b) | radio, timing and position linkability |
| C8 Veracity vs automation | RQ1, RQ2 (discussion) | the chapter 6 section finished, framed by the storage locus and the IDTx definition (§3.1) | no measurement of dependent transactions |

### 2.5 What must be cut or narrowed, and why

| Item | Action | Justification |
|---|---|---|
| "First" in every contribution | narrow to "measured, same-testbed, domain-constrained, reproducible" | a priority claim falls to one counter-example; measurement breadth does not (audit §4) |
| "Throughput" in RQ1 | cut | the only figure is #39 (U), queue-and-mine on one local node; ledger throughput is a different study (BLOCKBENCH, cited in audit §4) |
| "Conformance", "compliant" | narrow | guide 1.2.2: "compliant" needs the standard's text and a clause-level check; #4 is structural |
| H1 beyond creation | report as not supported | #35 margins are 1.20× to 5.52×; reporting a failed half is required (guide 1.2.1) |
| H5 "the hybrid sits on the frontier" | narrow to the two-plane statement | #36 |
| "Viable alternative to centralized PKI" | retire | compound; replaced by H3 and the #21 and #33 baselines (audit F6) |
| MOBI VID "conformance" | narrow to "MOBI-VID-inspired, checked against the public texts", with SC-17, SC-18, SC-20 as recorded deviations | implementing them now would re-baseline birth gas and lifecycle rows during a freeze |
| CVIN-Combined as "the central design contribution" | demote to "a hybrid measured as a first-class candidate" | it is on one frontier and dominated on another (#36); designing it and finding that is still a result |
| "End to end" for any V2I figure | cut | #48 is a sum of operation costs, not a path latency |
| RSU-to-RSU messaging, SUMO, radio, Sepolia rollups, LLM interface | out, as limitations or future work | none is needed to answer RQ1 to RQ4 as restated; each is a Phase 2 idea with an owner (§3.4) |

Nothing on this list removes evidence.
Every cut removes a word that promised more than a V row holds.

### 2.6 The contributions under Scope v3

1. A same-testbed measured comparison of nine Ethereum identity standards over an identical operation catalogue and a 17-event lifecycle, with the operation definitions that make ratios meaningful (#6, #25, #34, #35, #36).
2. A credential layer and four-method resolver expressed in W3C structures, scored structurally and by the external DID suite (#4, #24).
3. Verification-step evidence for V2V and V2I messages under mock mobility, with the cost of revocation freshness measured (#21, #27, #32, #37, #44 to #48).
4. An executable security evaluation with a found-and-fixed attestation gap (#28), and a bounded on-chain observability result (#38).
5. A conceptual frame, labelled as such: where identity state lives (storage locus) and which transactions can depend on it (IDTx), mapped onto the primitives the nine standards already have (§3.1). No number is attached to it.
6. A reproducible testbed and evidence trail: claim register, run stamps, pre-registrations with dated amendments (`WM-1_REPORT.md` §3).

---

## 3. Placing F1, F2, F3 and the Phase 2 ideas

Placement key: **(a)** thesis section from existing evidence; **(b)** small new thesis experiment before the defence; **(c)** a paper after the thesis; **(d)** future work for others, with hand-off artefacts.
One constraint governs every (b): `PLAN_WM-2.md` §6 admits no new pre-registered experiment in WM-2.
A (b) therefore needs the author to open a bounded WM-3 before the defence (decision D-7).

### 3.1 F1: on-chain storage versus not, and the identity-dependent transaction

**Placement: (a) for the storage-locus lens and the IDTx definition and taxonomy; (c) for any IDTx measurement; (b) only if the author opens WM-3.**

**What Phase 1 already answers.**

| F1 question | Phase 1 evidence | Status for a chapter |
|---|---|---|
| Where each standard keeps identity state, per operation | harness tables `crud_storage.md`, `crud_logbytes.md`, `crud_calldata.md` of run `2026-10-09T02-09-36Z_7a9a996` (`1_blockchain-identity/results/metrics/latest/tables/`) | **no register row yet.** Register one V row (a derivation of the run of record) before any chapter quotes these tables |
| What the stored state costs over a lifecycle | zero-to-nonzero SSTOREs and lifecycle gas per standard (#35); 15-year lifetime, ERC-1056 cheapest at 1,450,146 gas (#26) | V |
| What it costs to read state kept in logs | ERC-1056 resolution grows with history: 112 RPC calls and 87 KB at h = 50 (#31) | V |
| What a passive observer learns from on-chain state | a delegate pool is fully linkable by one log query (#38) | V |
| On chain but unreadable | salted VIN hash plus AES-256-GCM ciphertext on the MOBI registry (`SIDE_PAPERS.md` SP-3; security matrix privacy rows) | V via #28's matrix; cite the file |
| Whether a contract can check a credential in O(1) | a declared design property per adapter in the six-criterion analysis (#36) | V as a declared criterion, not a measurement |

**An observation the chapter should make, because it is checkable in the code.**
The uPort-style ERC-1056 registry keeps `owners`, `delegates`, `changed` and `nonce` in storage, but emits attributes only as `DIDAttributeChanged` events (`1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol`, lines 71 to 80 and 314 to 322).
A contract cannot read an event log.
So the cheapest standard on every lifetime figure (#35) is cheap partly because its attributes cannot be the dependency of any on-chain transaction.
That is the veracity-versus-automation asymmetry of C8 (`section-feature-asymmetry.md` §6.x.2) stated in F1 terms, and it costs no new run to say.

**Is IDTx new?** It is both a re-framing and a contribution, and the defence will go better if the thesis says so first.
The mechanism, a guard on execution that reads some party's attributes, is old.
The contribution is the definition for vehicle identity, a taxonomy that separates cases the literature treats apart, and one evaluation dimension that Phase 1 has already measured for messages.

| Known pattern an examiner will name | What it shares with IDTx | What IDTx must add or distinguish |
|---|---|---|
| Access control in contracts (owner and role modifiers; ABAC in NIST SP 800-162) | a guard on attributes | the dependency is on an identity *named* by the transaction (a vehicle, an RSU), whose lifecycle state changes, not only on the caller |
| Permissioned tokens over an on-chain identity registry (ERC-3643 with ONCHAINID claims, built on ERC-734/735) | the closest prior art: a transfer executes only if an identity holds claims from trusted issuers | position against it explicitly; claim the taxonomy, the vehicle domain and the freshness dimension, not the mechanism |
| Oracle-conditioned execution (e.g. Town Crier; commercial oracle networks) | an off-chain fact imported to gate execution | one locus of the taxonomy, not the whole concept |
| Account-abstraction validation (ERC-4337 `validateUserOp`, paymasters) | admissibility decided by programmable validation | the "evaluated at admission" class; Phase 1 prices the indirection (+46,830 gas per operation, #25) |
| Conditional payments (escrow, hash-time-locked contracts) | execution conditional on a predicate | the predicate is an identity attribute with a revocation lifecycle |
| On-chain verification of credentials or ZK attribute proofs (e.g. Coconut; zk-creds) | the encrypted or committed case | the "committed" locus; Phase 1 has the commitment (VIN hash) but no proof |
| Confidential contracts and FHE (e.g. Hawk; FHE-enabled EVMs) | computing over encrypted state | the "encrypted" locus; out of Phase 1's reach |
| Transaction-order dependence and front-running (Luu et al., CCS 2016; front-running SoKs) | a race between a state change and a dependent transaction | the revocation race: the freshness window of a dependency |

This list names what an examiner will expect; it is not a checked bibliography.
Each entry must be read and cited from its source when chapter 2 is written (guide 1.3.8).

**A definition that should survive a defence.**
*An identity-dependent transaction (IDTx) is a transaction whose admissibility or effect is a function of the state of an identity named by the transaction, other than the validity of the transaction's own signature, evaluated from ledger storage or from an attestation that the transaction itself verifies.*
A *triggered* IDTx is one submitted by an agent because an identity's state changed; the chain does not trigger itself, so this class always has an off-chain component.

**A taxonomy with four axes.**

| Axis | Values |
|---|---|
| Dependency locus | contract storage (readable); event log (not readable by contracts); on-chain commitment or ciphertext (readable only by opening, proof or decryption); attestation carried in calldata and verified in the transaction; oracle-imported |
| Visibility | plaintext; committed (hash); encrypted |
| Initiation | holder; third party (issuer, relayer, operator); automated agent |
| Evaluation time | atomic within execution; at admission (account-abstraction validation); deferred to a verifier's cache with a re-check every k |

**One evaluation dimension, with Phase 1 evidence behind it.**
A dependency held in contract storage is evaluated in the same state transition that uses it, so there is no window between check and use.
A dependency held off chain carries a staleness window set by the verifier's re-check policy.
Phase 1 measured that window for messages: at most k − 1 stale messages (#32, #46), and a fail-open case when clocks drift (D51).
Three further dimensions complete the evaluation: dependency cost (gas to make the dependency readable, then to evaluate it), exposure (what an observer learns, #38), and failure mode under a stale dependency (fail-open or fail-closed).

**Phase 1 primitives that are IDTx in all but name**, for the chapter 4 mapping table: `payToll` in `CVIN_NFT_DID_ERC721.sol` (effect gated on `ownerOf`, storage locus); `hasValidClaim` in `CVINCombinedIdentity.sol` (a storage predicate a consumer contract could gate on); `validDelegate` in `EthereumDIDRegistry.sol` (storage); `attestEvent` in `MOBIVIDRegistryV2.sol` (role plus a signature recovered in the transaction, #28); ERC-4337 validation (admission).
No consumer contract that depends on another contract's identity state has been measured.
That is the gap the IDTx paper fills.

**Naming.** Use one name, "identity-dependent transaction (IDTx)", and retire IDDTx and IDBTx (D-6).
Three names for one concept read as an unsettled idea.

**Effort, risk, novelty, examiners.** The (a) placement costs about one chapter section and one chapter 4 table, with no new run.
Its risk is overclaiming novelty; the positioning table above is the mitigation.
A measured IDTx study (a consumer contract on three or four substrates, pre-registered) is two to four sessions and a new pre-registration; it is the strongest Phase 2 paper and the weakest candidate for a pre-defence rush.

### 3.2 F2: public and private blockchains and other databases

**Placement: (a) for the centralised and PKI baselines; (b) only the Sepolia witness, if N-11 is decided; (c) a ledger-choice paper; (d) non-EVM ledgers.**

| F2 question | Phase 1 evidence | Gap |
|---|---|---|
| Chain versus a centralised registry on the same lifecycle | M4 parity: writes at least 10× dearer on chain, PASS; "equal once cached" FAIL (#33) | in-process baseline is a lower bound (#33 caveat) |
| Chain versus an IEEE 1609.2-style PKI on identical operations | verify 0.253 ms PKI vs 9.654 ms uncached ERC-1056 (#21) | in-process PKI; one host |
| Public versus private chain | none measured | every gas figure is M1, a single local node; no M2 run (N-11) |
| What carries over between EVM chains | gas, for identical bytecode and calldata (ch. 1 §1.5) | latency, fees and finality do not carry over |

An examiner may note that the M1 condition is closer to a single-operator private chain than to a public network.
The thesis should say so in chapter 3: M1 gas transfers to any EVM network, permissioned or public, and M1 latency describes neither.
Comparing permissioned consensus (for example an EVM network under a BFT consensus) with a public testnet and a database backend is a real study: effort high, risk of comparing configurations rather than designs, novelty moderate against the benchmarking literature.
It belongs after the thesis.
The database lifecycle backend started in report 16 is useful to that paper; it should not produce a thesis number under WM-2's rule.

### 3.3 F3: three modes of communicating with the chain for reads and writes

**Placement: (a) as a classification in chapters 4 and 6; (c) a short measurement paper.**

The author has not fixed the three modes; I propose a default (D-9) that Phase 1 already measures on both axes.

| Axis | Mode | Phase 1 evidence |
|---|---|---|
| Write | direct transaction by the identity's key | #25, #34 |
| Write | relayed (an off-chain signature, submitted by another party) | only ERC-1056 (pure) and ERC-4337 have a relayed path (#34); relaying changes linkability and cost: 1,586,908 gas relayed vs 1,454,728 self-funded per epoch with one attribute each (#38) |
| Write | account-abstracted (UserOperation through an EntryPoint) | +46,830 gas per operation (#25); U5 141,767 = direct U3 + 47,116 (#34) |
| Read | on demand at message time | 9.654 ms uncached ERC-1056 verify (#21) |
| Read | cached with a re-check every k | #32; the one-call probe refresh, 2.76 / 2.89 ms per refresh (#37) |
| Read | offline credential, no chain at message time | 0.153 ms warm (#27) |

The ERC-1056 relayed-path gas sits in the harness `crud_gas` table but in no register row; register it before a chapter quotes it.
The classification that report 16 starts (every operation and demo step labelled by mode, generated from code) is a classification, not a measurement, so it fits inside WM-2's rule.
The read axis is the thesis's H3 argument restated; the write axis is SP-2 widened.

### 3.4 The Phase 2 ideas (`IDEA_REGISTER.md`)

| Idea (rank) | Placement | Reason |
|---|---|---|
| I-16 W3C on chain-backed documents (2) | (a) | it is the gate of WM-2 C1 (#24 re-run); already scheduled |
| I-05 Freshness theory (1) | (a) choose k by a stated rule; (c) the theory | the measurements have been seen, so a model fitted now is post hoc and must be labelled so (guide 1.2.1); a predictive theory tested on new hosts is a paper |
| I-14 Verifier fuzzing (8) | (a) as test infrastructure for C0 | a regression net, not a claim; no number |
| I-21 Side-paper pipeline (9) | §4 of this memo | the paper map is the pipeline's first output |
| I-19 Open release (17) | (a) as the v1.0 artefact at the defence | gated by N-12 (licence, default branch) |
| I-03 Sepolia and rollups (4) | (b) witness only, if N-11; rollups (c) | the witness is one run of an existing harness; rollup economics is a paper |
| I-08 Chain-bound signed operations (6) | (c) or (d); D52 stated as a limitation in the thesis | small, but a new contract variant during a freeze |
| I-13 Model checking caches (5) | (c) workshop paper | must rediscover D51; independent of the thesis text |
| I-12 Contract properties (13) | (d) | hand-off: D53 as the must-find target, `4_comparison-framework/security-analysis` |
| I-01 SUMO mobility (3) | (d), or (c) with I-11 | out by SC-22; needs N-4; hand-off: `cv2x-testbed/sumo/`, `docs/PLAN_SUMO_VISUALISATION.md` |
| I-04 RSU trust mesh (10) | (d) after the D2 note | C3 claims do not need it |
| I-10 Selective disclosure on the hot path (7) | (c) | a second credential suite; gives C7 a hypothesis later |
| I-18 Claims CI toolkit (11) | (c) methods paper | a contribution of its own; not a thesis claim |
| I-06, I-07, I-09, I-11, I-15, I-17, I-02, I-23 | (d) | PhD-scale, or need real mobility, radio or hardware; I-15 and I-17 are standards and desk studies others can run from `docs/MOBI_VID_CHECKLIST.md` |
| I-20 Notebook intake | the author's channel | material enters Phase 2, not the frozen thesis |
| I-22 Examiner explainer | defence preparation only | §5 of this memo is its seed question set |

---

## 4. The paper map

| # | Working title | Contribution (one sentence) | Evidence | Venue type | Depends on | Who else could write it |
|---|---|---|---|---|---|---|
| P1 | Measured Cost of Vehicle Identity on Nine Ethereum Standards | Under identical operations and a 17-event lifecycle, creation spans 33.7× across nine standards, yet lifetime margins shrink to 1.20× to 5.52×, so operation definitions decide rankings. | #6, #25, #34, #35, #36; A6 re-run | IEEE Access | WM-2 close | a co-author from the lab with the harness; condensed companion of the thesis |
| P2 | A Silent Signature, and Two Lenses for Contract Identity Security (SP-1 with SP-7) | An executable revert harness with a threat matrix found and fixed an unverified on-chain attestation, at a measured gas price. | #28; C2 of WM-2 | security-and-blockchain workshop (an IEEE S&B or ACM CCS workshop) | none | any security student with the defect log |
| P3 | Fitting Vehicle-Identity Verification into the Safety Budget, with Revocation Freshness Priced | Off-chain credential verification costs well under a millisecond, while uncached chain reads do not fit, and a re-check every k bounds staleness at k − 1 messages. | #21, #27, #32, #37, #44 to #46; C0, C3, A3b | IEEE VTC | D51 fix | a V2X student, who could add I-01 for a journal version (IEEE T-ITS) |
| P4 | Three Ways to Write, Three Ways to Read: Interaction Modes for Vehicle Identity on Ethereum | Direct, relayed and account-abstracted writes and on-demand, cached and offline reads differ in gas, latency and linkability, measured on one testbed. | #21, #25, #27, #32, #34, #37, #38; new register rows for the relayed path | IEEE ICBC (short) | P1 | the author; F3 classification as input |
| P5 | Identity-Dependent Transactions: Definition, Taxonomy and Freshness for Vehicle Identity | A definition and four-axis taxonomy of transactions that depend on identity state, with a measured comparison of dependency cost and staleness window across storage loci. | §3.1 here; a new pre-registered consumer-contract experiment | IEEE ICBC (full) or an ACM CCS workshop | P1, P3 | the author: the concept is his and should carry his name first |
| P6 | Pseudonymity on a Public Identity Registry | A delegate pool on ERC-1056 is fully linkable by one log query; per-pseudonym DIDs are unlinkable only while attribute-free or relayed. | #38; I-11 for the extended version | privacy workshop (ACM WPES) or IEEE VNC | I-01 for the extension | a privacy student with SUMO traces |
| P7 | Ledger Choice for Vehicle Identity: Public, Permissioned and Centralised | The same lifecycle on a public testnet, a permissioned EVM network and a database backend, compared by cost, latency, observability and trust assumptions. | #33, #21; Sepolia (N-11); a permissioned network; the F2 database backend | IEEE T-ITS or IEEE Access | P1, P4 | a successor MASc student; hand-off: adapters, `experiment_lifecycle_parity.py` |
| P8 | Claims That Check Themselves: CI for Research Evidence | Run stamps with per-producer scope, a promote step and a claim register, each guard shown to fire, caught faults that session logs had hidden. | `WM-1_REPORT.md`; `tools/run_identity/`; guide 1.3.11 | ACM REP or an empirical-software-engineering artefact track | none | a software-engineering collaborator |

Sequence: P1 and P2 first, since their evidence exists once WM-2 closes.
P3 follows the D51 fix and the re-runs.
P4 needs only new register rows over the existing run.
P5 and P7 each need a new pre-registered experiment and are the first Phase 2 build wave.
P6's short form could go any time; its long form waits for real mobility.
P8 is independent.
SP-4 (portability of the MOBI profile) is better taken to the MOBI working group as a standards contribution than written as a paper.
SP-3, SP-5, SP-6 and SP-8 fold into P1, P3 and P2 as condensed companions (`SIDE_PAPERS.md`, guidance).

---

## 5. What examiners will ask

| # | Question | Where the answer lives | Exists or must be created |
|---|---|---|---|
| 1 | What is new relative to the rubric-based DID-method evaluations (Fdhila et al.) and to existing SSI V2V systems? | audit §4; chapter 2 | **create**: chapter 2 is unwritten (`SCAFFOLD.md`) |
| 2 | Are your minimal ERC-4337 and LSP8 implementations representative? | ch. 1 §1.5; #34 n/a cells; C8 | exists |
| 3 | Is "ten times cheaper" robust to the operation definition and to the lifecycle? | #6, #25, #35 | exists; chapters 1 and 7 must use the split verdict |
| 4 | Is your hybrid on the frontier or not? | #36; ch. 7 §7.3 | exists |
| 5 | Which part of the 100 ms budget did you measure, on which host? | #27, `docs/LATENCY_BUDGET.md`, C2 | exists |
| 6 | Is k − 1 stale messages acceptable for a safety system, and which k do you defend? | #32, #37, #46; N-17 | **create**: the decision (D-12) |
| 7 | Can a revoked key ever verify? | D51; WM-2 C0 | **create**: the fix and the re-run |
| 8 | Does conformance of the document shape say anything about the chain state behind it? | #4, #24; WM-2 C1 | scheduled |
| 9 | Why call it MOBI if most normative requirements are unmet? | SC-14a; `docs/MOBI_VID_CHECKLIST.md` | exists; the deviations must be recorded (D-11) |
| 10 | Is a public chain compatible with V2X pseudonymity? | #38; C7 | exists |
| 11 | Why a blockchain at all, rather than a database or a PKI? | #33, #21; §3.2 | **create**: a chapter 6 section |
| 12 | How does an identity-dependent transaction differ from access control or from ERC-3643? | §3.1 here | **create**: chapter 6 section and chapter 2 positioning |
| 13 | Your title says connected vehicles; where are the infrastructure, the radio and the traffic? | C3, #44 to #48; SC-22 | exists; ch. 7 §7.5 must state it |
| 14 | Would another implementation of the same standard have different defects, and does that undermine the comparison? | C8; `docs/DEFECT_LOG.md`; ch. 6 draft | exists as a draft |
| 15 | What did you build yourself, and what did tools do? | attribution statement (`SCAFFOLD.md` front matter); N-23 | **create**: the AI-use statement the university's policy requires |

---

## 6. Decisions I need from you

Each default is mine and stands until you overturn it (guide 2.1.7).

| # | Decision | My recommended default | Why |
|---|---|---|---|
| D-1 | Adopt Scope v3 (§2) as the thesis scope | yes | it is the second attempt made positive, with nothing added that lacks a V row |
| D-2 | SC-04: reword every "first" | yes: "measured, same-testbed, domain-constrained, reproducible" | one counter-example ends a priority claim |
| D-3 | SC-05: "throughput" in RQ1 | cut | #39 is U and not a ledger throughput |
| D-4 | Report H1 and H5 as split verdicts | yes | guide 1.2.1; the register already says it (#35, #36) |
| D-5 | Treat C3 and C7 as pre-registered questions without hypotheses | yes | a hypothesis added now would be post hoc |
| D-6 | One name for the concept | "identity-dependent transaction (IDTx)"; retire IDDTx and IDBTx | one term reads as a settled idea |
| D-7 | IDTx and F1 to F3 in the thesis | (a) only: definition, taxonomy, mapping and classification from existing evidence; no WM-3 experiment | WM-2 §6; a pre-defence experiment risks the freeze for a paper's result |
| D-8 | F2 in the thesis | the centralised and PKI baselines only; private chains to P7 | nothing measured on any other ledger |
| D-9 | The three modes of F3 | write: direct, relayed, account-abstracted; read: on demand, cached, offline | Phase 1 measures all six cells |
| D-10 | Sepolia witness before the defence (N-11) | run it if you supply a funded test key and an RPC endpoint; otherwise a stated limitation | one run of an existing harness; it closes the most visible open item |
| D-11 | SC-17, SC-18, SC-20 | record as deviations; do not implement before the defence | implementation would re-baseline birth and lifecycle rows |
| D-12 | The k the thesis defends (N-9, N-17) | the one-call probe refresh at k = 1, which #37 reports as zero staleness at about 3.5× the P* of the full refresh, with the host dependence stated | the cheapest safe policy the evidence supports |
| D-13 | Phase 2's time box (P2-D2) | documents only until the defence; build waves after it | the thesis is the system of record; Phase 2 feeds papers |
| D-14 | Thesis title | the title in §2.1, or keep the current one with "measured" added | the current title promises a comparison of SSI *systems*; the work compares substrates |
| D-15 | Chapter 2 | write it next, before more Phase 2 design, with IDTx's positioning inside it | it is the largest examiner risk (question 1) |

---

A closing word, as your supervisor would say it.
You have done far more than a MASc needs, and the discipline you built around the evidence is rarer than the code.
The risk now is not that the work is thin; it is that its best results are hidden behind words they cannot carry.
Cut the words, keep the rows, write chapter 2, and let IDTx be the first paper with your name on a concept rather than a measurement.
