CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**S2 — Registry Delta**

**The merged set of new and changed content blocks produced by the HDA campaign, stated as a delta against Content Block Registry v11.3**

Document 14 of 16 · Hybrid Data Architecture (HDA) Campaign · Support document · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type B tables-data → Administrative (registry maintenance); no thesis chapter*

---

## 1. Status of this document

**This is a delta, never a replacement.** It lists only the content blocks that the HDA campaign creates or changes. It does not restate, supersede, or re-score any row of Content Block Registry v11.3. Applying this delta to v11.3 yields the next registry version; under the Deliverable Suite Architecture v1.0 (§3.2) a delta is never merged silently, so no row below is in the registry until the researcher applies it. Rows of v11.3 that the campaign corrects are handled as K-corrections (K-HDA-1 to K-HDA-7, row in §2.12), which go to the S3 K-ledger and not into this table as overwrites.

Compiled 2026-10-04 from the closing "Registry delta rows" section of each primary document (and, for Document 11, from its §5.1, which that document designates as its S2 delta). Only those sections were read; the bodies of the documents were not. Content Block Registry v11.3 itself was not opened by this pass, so no row has been checked for collision with an existing v11.3 row.

Schema (Suite Architecture §3.2): Content Block · T · Source · Ch. · Ready % · Notes and status. Type A is prose for the thesis body, Type B is tables, data and process artefacts, Type C is contribution or claim statements requiring separate audit. Ready % estimates remaining editorial work; it is not confidence in the content.

### 1.1 Coverage

| Doc | Rows | State |
|---|---|---|
| 00 | 4 | merged |
| 01 | 14 | merged |
| 02 | 16 | merged |
| 03 | 16 | merged |
| 04 | 13 | merged (file arrived during compilation) |
| 05 | 12 | merged (file arrived during compilation; 13 declared, 1 folded into 10) |
| 06 | 13 | merged |
| 07 | 14 | merged |
| 08 | 21 | merged |
| 09 | 12 | merged |
| 10 | 4 | merged (5 declared, 1 folded into the built-artefact row for the S1 rerun) |
| 11 | 13 | merged (15 declared, 2 folded into 01 and 09) |
| 99 | 4 | merged |
| Built artefacts | 7 | added on instruction to the compiling pass |
| **Total** | **163** | 160 document rows declared, 4 removed as duplicates, 7 built-artefact rows added |

Nothing is pending merge. S3 declares no content-block rows of its own and was not read.

### 1.2 Normalisations applied

Ready values are shown with a percent sign throughout (most documents gave bare numbers). Document 08 wrote mixed types as "A+B"; they are shown as "A/B" to match the other documents. No Ready value, chapter target, or note was otherwise altered; the four merged rows in §3 are the only rows whose Notes were extended.

Scenario numbers inside row text are left as each document wrote them. Several are stale against the canonical register in 00 §6; the translation is in §4 item 1.

---

## 2. Delta rows, grouped by originating document

### 2.1 Document 00 — Master Plan and Attack

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| HDA Master Plan (this document) | B | HDA 00 | Admin | n/a | Front door; scenario register governs |
| The ten-step placement argument (§3) | A | HDA 00 §3 | 4 §4.5 opening; 5 | 75% | Compressed form of 01, 03, 11 |
| Canonical scenario register S1–S19 | B | HDA 00 §6 | 4 | 85% | Supersedes per-document S-numbers |
| Staged demonstration plan | B | HDA 00 §7 | 4 (method), 5 (future work) | 80% | Depends on D7 |

### 2.2 Document 01 — On/Off-Chain Data Architecture and Anchoring

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| The six-question data-placement framing and its reduction of Set A/Set B to a placement finding | A | 01 §1 | 4 §4.4; hook 2 §2.4 | 80% | Argument complete; awaits S7/S8 numbers |
| Placement taxonomy (ten locations, eight attributes) | B | 01 Table 2.1 | 4 §4.4 | 85% | EVM constants DIGEST-LEVEL |
| Storage-vs-event finding within O1 (F3 44,760 vs F1 161,835; factor ≈3.6) | A/B | 01 §2, trace | 4 §4.2, §4.4 | 95% | Measured |
| Anchoring pattern family (seven patterns) with measured/unmeasured column | A/B | 01 §3, Table 3.1 | 4 §4.4 | 80% | Measured only for 3.1, 3.4, 3.6-as-flag |
| Read-path catalogue and tier fit | B | 01 Table 4.1 | 4 §4.5 (latency) | 80% | Propagation delay unmeasured |
| Write-path catalogue incl. delayed write with dual ordering | A/B | 01 §5, Table 5.1 | 4 §4.4; 5 §5.1 | 75% | Sponsored-write extension unbuilt |
| Two-source integrity table | B | 01 Table 6.1 | 4 §4.4 | 85% | — |
| Canonicalisation deviation and two-hash consistency assertion | A | 01 §6.3 | 4 §4.1 (compliance) | 90% | Assertion to be added to S7 |
| Parametric cost model with worked examples A–E | B | 01 §7, Tables 7.1–7.2 | 4 §4.2, §4.4 | 70% | g_a, m are estimates/hypotheses |
| "Who pays" analysis tied to controller-only authorisation | A | 01 §7.5 | 4 §4.4; 5 §5.1 | 80% | — |
| Per-function placement matrix (F1–F12, C1–C4, G1–G4) | B | 01 Table 8.1 | 4 §4.4 | 85% | Hybrid deltas to be confirmed by 03. Merged with the duplicate row in 11 §5.1: O1 only, programmatic from trace, other options pending; 11 cites this block as "01 §6" |
| Per-object placement matrix | B | 01 Table 9.1 | 4 §4.4 | 85% | — |
| Eleven placement rules | A | 01 §10 | 5 §5.1 | 85% | Instantiated by 03 |
| Open-quantity resolution table | B | 01 Table 11.1 | 4 §4.4; S3 | 90% | Feeds 00 schedule and 10 |

### 2.3 Document 02 — ZKP and Verifiable Data

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| ZKP-as-structural-requirement argument (createPresentation gap + Allen + SCMS + GDPR) | A | 02 §1 | 5 §5.1 | 80% | Reuses thesis framing; new synthesis of four pressures |
| Five-property taxonomy (SD, unlinkability, predicate, non-revocation, PoP) + computation vs data attestation | A | 02 §1.3, §7.5 | 2 | 85% | Definitions to reuse across suite |
| Mechanism master comparison table (9 mechanisms × 11 axes) | B | 02 §2.9 | 4 Stage 19 | 70% | All cells DIGEST-LEVEL; to be partially replaced by §10 measurements |
| SD-JWT repo scheme vs RFC 9901 deviations (name-keyed digests; EIP-191 key binding) | A | 02 §2.2 | 4 | 90% | Verified against source code |
| Verification placement rule (atomic state change ⇒ on-chain) + verify-off-chain/anchor-event trust assumptions + verifier-oracle | A | 02 §3 | 4, 5 | 80% | Links to 01 taxonomy |
| F8 anchoring resolution (commitment + pairwise DID; never public DID for routine Tier 2) | A | 02 §3.7 | 5 §5.1 | 85% | Load-bearing for 03 and 08 |
| CAV ZK application matrix (9 applications) | B | 02 §4.1 | 4 | 75% | Designs; each maps to a scenario in 04–07 |
| Three-tier VIN scheme with ZK tier and Poseidon-commitment implication | A | 02 §4.2 | 4 | 70% | Raises schema question (§13) |
| Tier 1 stays with SCMS: three reasons | A | 02 §4.7 | 1, 5 | 90% | Settled position for 03 |
| Toll payment without location trail (charge-token/nullifier flow) | A | 02 §4.8 | 4 | 65% | Handed to 06 |
| Agent ZK applications incl. F12-is-public finding and zkML-as-validation-hook | A | 02 §5 | 5 | 75% | Feeds 09, 11 |
| Revocation privacy trade (status list / accumulator / ZK-over-list) with staleness window W and AccumulatorUpdated invalidation event | A/B | 02 §6 | 4 | 75% | Extension event proposed, not spec change |
| Verifiable data beyond ZK: four places for computation attestation | A | 02 §7 | 4, 5 | 80% | Pointer to 09 §6 |
| Threat analysis: ZK protects / does not protect; privacy-when-required tiering; escrow options (i)–(iii) | A | 02 §8 | 4, 5 | 80% | Escrow option (ii) recommended to 03 |
| Parametric ZK cost model per vehicle-year | B | 02 §9.1 | 4 | 70% | Formula only; variables to be bound by 10 |
| Staged ZK build plan (a)–(d) with assertions A-a1…A-d3 and metrics table | B | 02 §10 | 4, 10 | 60% | All pending |

### 2.4 Document 03 — Best-of-Both-Worlds Hybrid Design

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| HDA ranked requirement set R1–R13 with acceptance metrics | B | 03 §1 | 4, 5 | 70% | Rubric for Stage 2 scoring; parameters (τ, G_year) unmeasured |
| Seven-layer hybrid architecture L0–L6 with placement table | A/B | 03 §2 | 5 | 75% | Family F skeleton; O2–O8 evidence pending |
| Anchor · Cache · Attest · Reconcile pattern, state machine and RECONCILE rules | A | 03 §3 | 5 | 80% | Executable as unit tests after B3 |
| Staleness-window table per tier (τ1 n/a, τ2 300 s, τ2,doc 3,600 s, τ3 0, τ_gov 86,400 s) | B | 03 §3.4 | 4, 5 | 50% | Proposed defaults; measurement owed by B7 |
| Tier-to-chain-interaction matrix | B | 03 §4.1 | 4 | 80% | Extends C6 |
| IDPP as anchor migration with continuity proof | A | 03 §4.3 | 5 | 60% | Makes 2020 concept testable; S5 dependency on E1 |
| Five degraded modes with permitted/refused actions | A/B | 03 §5 | 5 | 75% | Failure branches for 04/06 scenarios |
| Threat-to-layer mapping with residual risks | B | 03 §6 | 4, 5 | 80% | Memo threat model coverage; adds cache poisoning |
| Dual-mode identity with escrowed linkage records | A | 03 §6.4 | 5 | 70% | SCMS LA precedent; closes accountability gap |
| Disclosure policy model (attributeClass × verifierClass × tier × legalBasis → mode) | B | 03 §7.1 | 5 | 65% | Feeds 02; legal rows need source-level confirmation |
| Parametric cost model with O1 anchor points and epoch-length lever | B | 03 §8 | 4, 5 | 60% | G_root, G_C1, λ hypotheses; illustrative arithmetic labelled |
| Where hybrid beats SCMS-plus-databases and where not | A | 03 §8.4 | 5 | 70% | Honest cost position incl. one-time fleet cost |
| Realisability inventory: exists / off-the-shelf / must-build | B | 03 §9 | 4, 5 | 85% | Precise repo state as of 2026-09-03 |
| Staged build plan B0–B8 with traces and gate assertions | B | 03 §9.3 | 4 | 75% | S9–S12 identifiers proposed, pending 00 |
| Three-slice demonstration plan with "cannot prove" columns | B | 03 §10 | 4, 5 | 75% | Limitations structure for Ch. 5 |
| Family F composite specification skeleton with evidence owed | B | 03 §11 | 5 | 65% | Stage 3 hypothesis; C12–C13 feed |

### 2.5 Document 04 — Full-Coverage Scenarios, CAV and Agent

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| Scenario design method (actors as DIDs, object classes, eight-field step table, two-way coverage obligation) | A | 04 §1 | 4.3 | 80% | Reusable by 05–08 |
| Three interface boundaries exposed by full-life scenarios (no delegate revocation; no controller transfer; undefined validation response) | A | 04 §1.5 | 5.2 / limitations | 70% | Candidate spec v1.1 notes; needs researcher decision (§9) |
| S9 "A vehicle's first year" step table (37 steps) | B | 04 §2.2 | 4.3 | 75% | Design only; no trace |
| S9 design rationale (dual mode, write-free tolling, predicate gate, forensic read, selective-omission attack) | A | 04 §2.3 | 4.3 | 70% | Cross-refs 01, 02, 03, 06, 08 |
| S10 "Fleet-operations agent and sub-agents" step table (30 steps) | B | 04 §3.2 | 5.2 | 75% | Design only; no trace |
| Delegation-is-not-capability argument with negative test | A | 04 §3.3 | 5.2 | 80% | Supports C14 |
| Archival-issuer rule for trace anchors (Org anchors, agent is subject) | A | 04 §3.3; S7 trace seq 54–55 | 5.2 | 75% | Rests on a measured S7 behaviour |
| Budget-predicate authorisation and its concurrency weakness | A | 04 §3.3 | 5.2 | 60% | ZK detail deferred to 02 |
| Function × scenario and object × scenario coverage matrices | B | 04 §5.1–5.2 | 4.3 | 85% | Step ids, not ticks |
| Tier and placement summary; "F8 is the single T2 write" observation | A/B | 04 §5.3 | 4.3 / 4.5 | 75% | Links to createPresentation finding |
| Built-evidence map (S9/S10 steps ↔ S1/S7/S8 trace seq) | B | 04 §6.1; three traces | 4.3 | 90% | Verified at source |
| Gas read from S1/S7/S8 traces (governance and typing tags included) | B | 04 Table 8 | 4.2 | 90% | O1 only; not S9/S10 predictions |
| S9/S10 trace assertions and laptop-limits list | B | 04 §6.3–6.4 | 4.3 / limitations | 70% | Becomes test spec when scripts are approved |

### 2.6 Document 05 — Latency-Tier Scenarios

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| Tier framework restated as a placement rule; symbolic budget `L_radio + L_crypto + L_lookup + L_decision` and the `L_write` exclusion | A | 05 §1.1–§1.2 | 2 §2.4 | 80% | Consistent with 03 §4.1; no numeric budget split asserted |
| Per-tier operating envelope (allowed F-tags, read/write model, staleness, evidence) | B | 05 §1.3 | 2 §2.4; 4 Stage 18 | 85% | Self-contained table |
| T1-CAV: SSI credential licences the pseudonym pool; checked only at enrolment and epoch renewal; two-direction revocation | A | 05 §2.1 | 1 (extension-not-replacement); 4 Stage 18 | 75% | `SCMS_ENROLMENT_ELIGIBILITY` type is a proposal |
| T1-AGT: session key as pseudonym-certificate analogue, with four stated limits; checkpoint interval as accountability parameter | A | 05 §2.2 | 5 (I2I generalisation) | 75% | Ties to C14 |
| T2-CAV: charging step table with budget terms; F8 split into signed presentation and deferred commitment; replay defence moves to verifier nonce | A/B | 05 §3.1 | 4 Stage 18 | 80% | S7 entries 32–34 and 49–51 are the evidence |
| Stale-cache acceptance after revocation as built evidence that τ2 is a security parameter | A | 05 §1.4, §3.1 | 4 Stage 18; 5 (limitations) | 85% | From S7 trace |
| T2-AGT: A2A phases on cached views; hard versus soft signal staleness rule | A | 05 §3.2 | 5 (I2I generalisation) | 70% | Needs Set C host for demonstration |
| T3-CAV: transfer as ordered synchronous writes; no atomic transfer and no early delegate withdrawal among the twelve functions | A | 05 §4.1 | 4 (CAV scenario analysis); 5 (limitations) | 75% | Depends on open question 3 |
| T3-AGT: onboarding and issuer cost by addition from S7 gas; dispute as redemption of deferred anchors | A | 05 §4.2 | 5 (I2I generalisation) | 70% | Set C cost unmeasured |
| Escalation ladder: provisioning down, disputes up; end-to-end revocation latency as sum of windows | A/B | 05 §5 | 2 §2.4; 5 | 80% | Candidate figure for C6 |
| Trace schema 1.1 timing fields (`t0`, `t1`, `lat`, `chainReads`, `cacheAgeMs`, `viewBlock`, `tier`, `net`) | B | 05 §6.2 | 4 Stage 18 (method) | 60% | Proposal; must go through PROPOSALS.md |
| Three evidence levels and what each can and cannot show; acceptance criteria per tier | B | 05 §6.3–§6.6 | 4 Stage 18 | 80% | Ready % rises with WO-8 |

### 2.7 Document 06 — Reputation, Payment, Gated Access, Low Connectivity

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| Common frame: placement columns (state / anchor / off-chain signed / cached) and failure taxonomy for scenario families | A | 06 §1 | 4 §4.3 | 80% | Depends on 01's matrix column names being finalised |
| Reputation on the verinym, evidence under pseudonyms, link proof at scoring time (CAV road reports) | A | 06 §2.2 | 4 §4.3; 5 §5.2 | 75% | Link-proof form (co-signature vs ZK) to be fixed by 02 |
| Reputation attack surface and on-chain/off-chain evidence split for agents; decay as verifier-side policy | A | 06 §2.3 | 5 §5.2 | 75% | Ties to C14 wrapper |
| "The identity system authorises and receipts; the rail executes" — payment split with receipt anchoring and no location trail | A | 06 §3 | 4 §4.3 | 80% | Charging vs tolling anchoring granularity rule |
| Delegate scope as confused-deputy prevention (typed F11 delegations beside the interface) | A | 06 §3.3 | 5 §5.2 | 70% | Extension type vocabulary needs a name in S2 |
| Offline-capable gate: snapshot height as security parameter; endorsement check from cache | A | 06 §4 | 4 §4.3 | 80% | Reuses `EmissionsCompliance` schema |
| Revocation propagation latency Δ + L as the agent access-control exposure window | A | 06 §4.3 | 5 §5.2 | 75% | Cross-checked against 08's channel crux |
| Read-only stale-action table with the negative-state asymmetry | B | 06 §5.2 | 4 §4.4 | 85% | Table is self-contained |
| Delayed-write queue (counter, local time, h₀), ordering and conflict rules, reconciliation rule for meanwhile-revocation | A | 06 §5.2 | 4 §4.4 | 80% | Clock-trust assumption declared |
| Connectivity state machine ONLINE / STALE-OK / STALE-EXPIRED / RECONCILING | B | 06 §5.2 | 4 §4.4 | 80% | Prefix-of-queue batch rule is the novel row |
| Lease credential as the bound on autonomous agent action; intersection of lease, mandate, capability windows | A | 06 §5.3 | 5 §5.2 | 75% | — |
| Consolidated placement and cost table for the four pairs; "cost drivers are epoch/session counts, never event counts" | B | 06 §6 | 4 §4.3 | 85% | Empirical form of the minimality claim |
| Demonstration plan S11–S14 with trace assertions and mock-provider design | B | 06 §7 | 4 §4.4 | 60% | Ready % rises when scripts exist and 10 reports traces |

### 2.8 Document 07 — Beyond-CAV Back-End Systems

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| Register-of-record principle: chain as anchor and verification substrate, never the authoritative register; correctability, privacy, institutional arguments | A | 07 §1.3 | 5 §5.2; 4 §4.4 | 85% | Needs supervisor view on how strongly to state the legal argument |
| GDPR hash nuance applied to registries: salted content hashes, erasure by revoke-and-delete, batch roots as set commitments | A | 07 §1.4; 01; 02 | 4 §4.4 | 75% | eIDAS 2.0 / EUDI ARF citations DIGEST-LEVEL; verify at source before submission |
| Minimal `DRIVER_LICENCE` credential object (mDL-compatible field naming) | B | 07 §2.3; brief §7 | 4 §4.3; 5 §5.2 | 80% | Field names to be confirmed against `lib/vid` builders when built |
| Three-verifier disclosure profiles for one anchored licence (police / car-share / insurer) with F8, SD digests, pairwise delegation | A/B | 07 §2.4 | 5 §5.2 | 80% | ZK linkage path unmeasured; stated as two-level design |
| Cross-jurisdiction recognition by endorsement walk; Local CVIN / IDPP mapping; signed endorsement-extract fallback | A | 07 §2.6; [5] | 5 §5.2 | 70% | Endorsement-extract object schema not yet specified |
| Licensed-operator delegation pattern with transitive revocation and confused-deputy guard (verifier-enforced scope) | A | 07 §2.7, §4.5 | 5 §5.2 (I2I) | 85% | Feeds 11 endorsement argument and 04 agent scenario |
| Deed transfer as revoke-and-reissue with event-log ordering proof; lien as referencing credential; atomicity gap and batch extension | A | 07 §3.3–3.5 | 5 §5.2 | 80% | Torrens mapping DIGEST-LEVEL |
| Conveyancing-agent chain-of-title walk using only F2/F6/G4 plus off-chain objects; declared degradation when historical content unavailable | A | 07 §3.6 | 5 §5.2 | 80% | Demonstrable by proposed S9 |
| Completeness mechanisms for lifecycle history: public anchor count vs `HISTORY_SNAPSHOT` Merkle root; privacy trade-off with pairwise DIDs | A | 07 §4.3 | 4 §4.4; 5 §5.2 | 75% | Policy choice left to researcher (§11 Q3) |
| Relocation of `MOBIVIDRegistryV2` on-chain fields (odometer, jurisdiction) to off-chain credential content with verifier-side monotonicity | A/B | 07 §4.1, §4.3; V2 contract | 4 §4.4 | 85% | Directly contrasts pre-campaign contract with HDA placement |
| Legacy adapter pattern: signer/anchor, issuance queue with G4 pre-check, read API, reconciliation job; invariant "no PII on-chain" | A | 07 §5.1–5.5 | 4 §4.4 | 85% | Throughput stated as formula only |
| Bulk Merkle migration: one root per batch, status-list revocation for migrated records, no per-record chain cost | A/B | 07 §5.4 | 4 §4.4; 5 §5.2 | 80% | Staleness-window policy for migrated credentials to be set in 03 |
| Registry comparison table (8 rows × 8 axes); type-invariant on-chain footprint; cost driver as event rate | B | 07 §6 | 5 §5.2 | 90% | No numbers; ready for direct inclusion |
| Demonstration plan and trace assertions for S7/S8/proposed S9 | B | 07 §8 | 4 §4.3 | 70% | Contingent on build; 10 reports |

### 2.9 Document 08 — I2I Secure Communication and Cruxes

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| S1 trace reading: proves/does-not-prove table | A | 08 §1 | 4 | 90% | Direct from trace; carries the seven declared gaps |
| I2I protocol specification: four-message handshake with signed/encrypted/anchored matrix | A/B | 08 §2.3 | 5 §5.2 | 75% | Design; validated by §7 steps 1–3 |
| Key agreement from F9 verification methods with F11 delegate pattern (option (i)) | A | 08 §2.4 | 5 §5.2 | 70% | Interface-preserving; needs §7 step 2 |
| Challenge-bound presentation as channel binding to on-chain state | A | 08 §2.5, §6 | 5 §5.1–5.2 | 80% | The thesis contribution; S1 partially demonstrates |
| Session policy as credential-derived object; scope intersection rule | A | 08 §2.7, §3(h) | 5 §5.2 | 65% | Needs policy table in `lib/vid/` (10) |
| Revocation-synchronised cache rule: one clock, `W_max` per type | A | 08 §3(a) | 4, 5 | 80% | Memo A rule made operational; test defined |
| Versioned-document downgrade defence | A | 08 §3(b) | 4 | 70% | Uses ERC-1056 `changed` semantics |
| Offline policy class with pre-fetched state and leases; irreducible issuer-compromise exposure | A | 08 §3(c) | 4, 5 | 65% | Pairs with 03 degraded modes and 06 low-connectivity |
| Dual-mode channel with escrowed linkability and C3-audited unlock | A | 08 §3(d) | 5 | 60% | Depends on 02 cryptosuite choice |
| Transport assumptions list (must/must-not) | B | 08 §3(e) | 4 | 75% | Hardware-dependent budgets flagged |
| Group channel stances: leader-keyed vs MLS-style | A | 08 §3(f) | 5 | 55% | Sandbox test defined; no build yet |
| Chain-fault behaviour: observed vs final, provisional policy | A | 08 §3(g) | 4 | 65% | Hardhat snapshot test defined |
| Agent cruxes: confused deputy, injection-resistant policy, tool authorisation, anchored execution log | A | 08 §3(h) | 5 §5.2 | 70% | Core of C14 argument |
| Channel data-placement table | B | 08 §4.1 | 4 | 85% | Consistent with 01/03 |
| Per-session cost formula with measured `G_F8`, `G_F3` | B | 08 §4.2 | 4 | 80% | Only measured terms from trace; fleet arithmetic labelled |
| Scenario: V2I charging handshake | A/B | 08 §5.1 | 4 | 70% | Step table; test named |
| Scenario: RSU report channel with epoch batching and escrow | A/B | 08 §5.2 | 4, 5 | 65% | Feeds 09 |
| Scenario: agent-to-agent negotiation (S6 made concrete) | A/B | 08 §5.3 | 5 | 65% | Set C gas unmeasured |
| Scenario: agent-to-tool session | A/B | 08 §5.4 | 5 | 65% | Bridge to 07 legacy adapters |
| Protocol relation matrix: DIDComm/TLS/Noise/1609.2/A2A-MCP reuse vs contribution | A/B | 08 §6 | 5 §5.2, 3 | 75% | Two contributions isolated |
| S1 extension plan (11 steps) with trace assertions and metrics | B | 08 §7 | 4 | 80% | Executable work order for 10 |

### 2.10 Document 09 — Reputation, Identity and Federated Learning

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| The four-link necessity chain (collective computation → reputation → identity → this system) | A | 09 §1, §3–§5 | 5, new §5.x (11 targets §5.6) | 80% | Argument complete; needs the S9 demonstration to cite. Merged with the duplicate row in 11 §5.1 ("Reputation-identity-endorsement chain"), which was marked pending 09 |
| Collective-computation workloads and participant requirements (Table 2.1) | B | 09 §2 | 1 §1.2 hook; 5 | 85% | Ties 2020 paper's high-latency tier to FL |
| Robust aggregation assumes a bounded fraction; reputation keeps the adversary a minority | A | 09 §3.1–§3.4 | 5 | 80% | Krum / trimmed mean DIGEST-LEVEL |
| Verinym/pseudonym resolution of the FL-privacy vs reputation-linkability tension (Layer one / Layer two) | A | 09 §4.5 | 5; 2 (cross-ref 02) | 70% | Layer two costs owed to the ZKP angle pass |
| Requirement → function/object mapping for reputation (Table 5.1) | B | 09 §5.1 | 4 (Set C evaluation), 5 | 85% | On-chain reputation is a cache; history is the event log |
| Reputation-weighted FL round protocol with F-tags and placement (Table 6.1) | B | 09 §6.2 | 4, 5 | 75% | Design; unmeasured except F5/F8/F11 |
| Contribution proof, scoring, weighting and exclusion rules (formulae) | A | 09 §6.3–§6.5 | 5 | 75% | Parametric; c₀, θ, α are programme parameters |
| Parametric per-round gas model (Table 6.2) | B | 09 §6.9 | 4 | 60% | Only F5/F8/F11 measured; g_C1, g_C3, g_G variables |
| The chain instantiated per case (Table 7.1) | B | 09 §7 | 5 | 80% | Covers researcher checklist item 10 |
| Reputation-layer attack analysis with measurability (Table 8.1) | B | 09 §8 | 4, 5 (limitations) | 75% | Feeds Memo A "reputation dynamics" axis |
| S9 demonstration plan and ISetC harness caveat | A | 09 §9 | 4; sandbox PROPOSALS | 70% | Harness gas is not O7 gas — rule 5 |
| Set C benchmark metrics (convergence, stability, Sybil/collusion, partner selection) | B | 09 §8.1, §9.3 | 4 | 70% | Metric definitions final; values owed |

### 2.11 Document 10 — VID Build Documentation

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| VID reference layer build record (this document) | B | HDA 10 | 4 §4.5, App. | 85% | Convert §5–§6 to prose for the thesis |
| Gas-by-function table, O1, four traces | B | HDA 10 §5.2 | 4 | 90% | First table with G and T tags; three target misses now recorded. Merged with the row in 05 §1.4 ("Measured O1 gas, S1 and S7 side by side", 90%, target Ch. 4 gas benchmarks), which 05 itself marked as a duplicate of this table |
| Anchoring-pattern measurement (11:1; on-chain typing cost) | B | HDA 10 §5.3 | 4, 5 | 90% | Feeds 01 §7 and 03 §8 |
| Findings F-VID-1 to F-VID-7 | A/B | HDA 10 §6; FINDINGS.md 4–10 | 4, 5 | 80% | F-VID-1 and F-VID-2 are spec v1.1 candidates |

### 2.12 Document 11 — Thesis Integration and Academic Argument

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| Placement axis argument (four classes, read/write, Set A/B reframing) | A | HDA 11 §3; 01 §2–§5 | 2 (§2.5), 5 (§5.1) | 80% | Thesis prose; cites only S1 trace numbers |
| Endorsement argument (minimal trust-framework primitive, lineage, beside-not-inside) | A | HDA 11 §2 | 2 (§2.5), 3 (§3.1) | 80% | NEW-1..NEW-4 need S1 verification labels |
| Ch.4 §4.5 opening prose | A | HDA 11 §4.1 | 4 | 75% | O2–O8 columns pending WO-1–3; σ pending Stage 18 |
| Ch.5 §5.5 opening prose | A | HDA 11 §4.2 | 5 | 75% | Realisability claim gated on 10 |
| Read-path cost model (formulas with σ, k, s) | B | 01 §7; 03 §4 | 4, 5 | 70% | No measurement; model only |
| Family F data-architecture specification (tiered mapping) | A | 03 | 5 (§5.5) | 70% | Stage 3 design; never a sandbox |
| Endorsement test series specification (G1–G4 assertions) | B | HDA 11 §2.4; 10 | 4 | 60% | Ready % rises when test/vid.js is green |
| MOBI VID conformance mapping with roles and endorsement column | B | HDA 11 §2.5; 10 | 3 (§3.3) | 65% | Re-expression of cv2x-testbed roles |
| Ch.1 motivation additions (placement gap; who-may-issue) | A | HDA 11 §1.1 | 1 | 85% | <200 words |
| C16 proposal text | C | HDA 11 §1.6 | 1 (§1.3) | n/a | Decision owed |
| K-corrections K-HDA-1..K-HDA-7 | B | HDA 11 §5.2 | 2, 3, 4 | n/a | To S3 K-ledger |
| HDA 11 Thesis Integration (the document itself) | A | HDA campaign | 1–5 | 80% | Primary integration map; administrative row declared in the closing section of 11 |
| C16 decision record | C | researcher | 1 | n/a | Pending decision; administrative row declared in the closing section of 11 |

### 2.13 Document 99 — Chat Primers for Angle Passes

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| HDA Programme Context Block v1.0 | B | HDA general pass, 99 §2 | 2 (methodology appendix) | 90% | Reusable across angle passes; re-issue when 10 publishes VID traces |
| HDA angle-pass primer set A1–A10 | B | HDA general pass, 99 §3 | Admin | 85% | Deliverable naming awaits the series decision (§8 Q1) |
| Chat-to-CLI work-order format with trace assertions | B | HDA general pass, 99 §5 | 2 (methodology) | 85% | Candidate for METHODOLOGY.md twin; check against Suite Architecture on next revision |
| Support-document maintenance primer | B | HDA general pass, 99 §4 | Admin | 90% | Depends on live R-series index availability |

### 2.14 Built artefacts (VID build, this pass)

These rows were supplied to the compiling pass as the record of what was built. Document 10 is the document of record for them. Entry counts, test counts and tag coverage are carried as given; this pass read only 10's closing sections and did not open the traces or run the tests. The four trace files named by 10 do exist under `5_minimal-ssi-sandbox/traces/`.

| Content Block | T | Source | Ch. | Ready % | Notes and status |
|---|---|---|---|---|---|
| EndorsementRegistry.sol + O1ControllerAdapter (G0–G4) | B | HDA general pass, VID build; 10 | 4 | 85% | Built. Governance extension beside IMinimalSSI, never inside it. Evidence for 11's endorsement argument and for the "Endorsement test series specification" row in §2.12 (still 60% there) |
| TypedCredentialRegistry + CredentialTypes (T1–T2) | B | HDA general pass, VID build; 10 | 4 | 85% | Built. 02 open question 5 (schema quantisation as a registry rule) and 06's unnamed delegation-type vocabulary both bear on this block; 10 records an on-chain typing cost in its anchoring-pattern row |
| lib/vid credential library (off-chain objects, offline verification) | B | HDA general pass, VID build; 10 | 4 | 80% | Built. Dependencies still open in other rows: 07 `DRIVER_LICENCE` field names, 08 session-policy table, 02 open question 1 (Poseidon or dual commitment) |
| S7 vid_minimal trace (56 entries, 12/12 F + G0–G4 + T1–T2, real gas) | B | HDA general pass, VID build; 10 | 4 App. | 85% | Built. File `vid_minimal_O1_ERC1056_1791157391842.jsonl`. Cited at source by 04, 05 and 10. 01's two-hash consistency assertion was marked "to be added to S7"; none of the closing sections read says whether it was |
| S8 vid_lifecycle trace (69 entries, 11 MOBI VID II event types, Merkle batch) | B | HDA general pass, VID build; 10 | 4 App. | 85% | Built. File `vid_lifecycle_O1_ERC1056_1791157402169.jsonl`. Cited at source by 04 and 10; 05 states it did not read it. What S8 should anchor depends on 07 open question 1 |
| VID layer test suite (7 tests; 19 passing with compliance) | B | HDA general pass, VID build; 10 | 4 | 85% | Built. Should raise the Ready % of 11's "Endorsement test series specification" row |
| Fresh S1 rerun on operator machine 2026-09-03 | B | HDA general pass, VID build; 10 §5.1 | 4 | 85% | Built. Merged with 10's row "First operator-machine S1 rerun" (85%; "G1 credit owed by architect"). **Date conflict, see §4 item 2**: the only S1 rerun trace on disk, `i2i_O1_ERC1056_1788492893157.jsonl`, is dated 2026-09-04 03:34 UTC by both its file name and its modification time |

---

## 3. Deduplication record

Four declared rows duplicate a row owned by another document. Each was folded into the owning row, whose Notes were extended; nothing was dropped.

| Removed row | Folded into | What was carried over |
|---|---|---|
| 11 §5.1 "Per-function placement matrix, O1" · B · 01 §6 · Ch. 4 · 85 | 01, "Per-function placement matrix (F1–F12, C1–C4, G1–G4)" | 11's scope note (O1 only, programmatic from trace, other options pending). The section pointer differs, see §4 item 4 |
| 11 §5.1 "Reputation-identity-endorsement chain (FL, cooperative perception)" · A · 09 · Ch. 5 (§5.6) · "pending 09" | 09, "The four-link necessity chain" | 11's chapter target §5.6; 11's "pending 09" is resolved by 09's own 80 |
| 05 "Measured O1 gas, S1 and S7 side by side, read from traces" · B · 05 §1.4 · Ch. 4 · 90 | 10, "Gas-by-function table, O1, four traces" | 05 marked its own row "Duplicates 10 if 10 tabulates S7; keep one". 10 is the document of record |
| 10 "First operator-machine S1 rerun" · B · HDA 10 §5.1 · Ch. 4 · 85% | Built artefacts, "Fresh S1 rerun on operator machine 2026-09-03" | 10's note on the G1 gate credit |

Pairs that overlap but were kept as separate rows, because type or scope differs. The registry maintainer should decide whether each is one block or two.

- 04 "Gas read from S1/S7/S8 traces" (Table 8, 90%) and 10 "Gas-by-function table, O1, four traces" (90%). Two tabulations of the same traces; Chapter 4 should carry one.
- 11 "Family F data-architecture specification" (A, 70%) and 03 "Family F composite specification skeleton" (B, 65%).
- 11 "Read-path cost model" and 01 "Read-path catalogue and tier fit".
- 11 "Endorsement test series specification" (60%) and the built "VID layer test suite" (85%).
- 00 "The ten-step placement argument" (75%), described by 00 as a compressed form of 01, 03 and 11, and 11 "Placement axis argument" (80%).
- 00 "Staged demonstration plan" and the build or demonstration plans in 02 §10, 03 §9.3, 03 §10, 06 §7, 07 §8, 08 §7 and 09 §9. 00's row should be treated as the governing one.
- 03 "Tier-to-chain-interaction matrix" and 05 "Per-tier operating envelope"; 05 says its framework is consistent with 03 §4.1.

Five documents each carry a parametric cost model (01 §7, 02 §9.1, 03 §8, 08 §4.2, 09 §6.9). They model different quantities and are kept as five rows. 10's "Anchoring-pattern measurement" row says it feeds 01 §7 and 03 §8, so those two models now have measured inputs that their own rows (70% and 60%) do not yet reflect.

## 4. Conflicts and inconsistencies found while merging

1. **Stale scenario numbers in row text.** 00's "Canonical scenario register S1–S19" supersedes per-document S-numbers. S7 and S8 are the built traces; S9 and S10 are 04's two full-coverage scenarios; S11–S14 are 06's four. Rows written before the register still use local numbers, and each must be re-read as follows before it enters the registry:

   | Row (document) | Says | Canonical (00 §6) |
   |---|---|---|
   | 07 "Conveyancing-agent chain-of-title walk … Demonstrable by proposed S9"; 07 "Demonstration plan … for S7/S8/proposed S9" | S9 | S15 |
   | 09 "The four-link necessity chain … needs the S9 demonstration"; 09 "S9 demonstration plan and ISetC harness caveat" | S9 | S16 |
   | 03 "Staged build plan B0–B8 … S9–S12 identifiers proposed, pending 00" | S9, S10, S11 | S14 (delayed write), S18 (revocation storm), S19 (policy-selected disclosure); 00 gives no mapping for 03's S12 |
   | 01 "Open-quantity resolution table" (01 §11 proposes a batch-anchor scenario) | S9 | S17 |
   | 04 rows naming S9 and S10; 06 "Demonstration plan S11–S14" | as written | unchanged |

2. **Date of the S1 rerun.** The built-artefact row supplied to this pass reads "Fresh S1 rerun on operator machine 2026-09-03", and 00's register calls it the "October rerun". 10 identifies the rerun as `i2i_O1_ERC1056_1788492893157.jsonl`. That file's name suffix and its modification time both give 2026-09-04 03:34 UTC (the evening of 2026-09-03 Pacific), and Document 99, written against a brief dated 2026-09-03, already cites it. Only the S7 and S8 traces are dated 2026-10-04. Either the rerun happened in September and the row's date is wrong, or there was an October rerun whose trace is not on disk. The row is carried as supplied and must not be cited with a date until the researcher confirms which.
3. **Which S1 trace is "the" S1 trace.** 01, 02, 03, 06, 08, 09 and 11 cite the June file (createPresentation 62,441); 04 takes its S1 evidence and gas from the September rerun (62,446). Both are valid runs. Any registry row quoting F8 gas should name the file.
4. **Section pointer for the per-function placement matrix.** 01 locates it at Table 8.1; 11 cites "01 §6". The 01 pointer is retained.
5. **Section pointer for the read-path cost model.** 11 cites "01 §7; 03 §4". 01's rows place the read-path catalogue at Table 4.1 and the cost model at §7; 03's rows place the tier matrix at §4.1 and the cost model at §8. 11's row is carried as written and flagged.
6. **Three names for the staleness window.** 02 uses `W` and asks whether it stays a variable; 03 publishes proposed defaults as τ (τ2 = 300 s and others, 50% ready); 08 uses `W_max` per credential type; 05 uses τ2 and reports from the S7 trace that a stale cache accepts after revocation, calling τ2 a security parameter; 07 defers the value for migrated credentials to 03. These appear to be one parameter. 03's defaults remain proposals; 05's row is evidence that the window matters, not a measurement of its right value.
7. **Two trace-schema extensions.** 08 "S1 extension plan" carries schema additions (08 §7) and 05 proposes "Trace schema 1.1 timing fields" (60%, "must go through PROPOSALS.md"). They should be one proposal.
8. **Specification v1.1 candidates are scattered.** The interface is normative and no document alters it, but four documents queue changes beside it: 04 (three interface boundaries: no delegate revocation, no controller transfer, undefined validation response), 05 (no atomic transfer, no early delegate withdrawal), 09 (ISetC batched or attester-scoped read), 10 (F-VID-1 and F-VID-2). 04 and 05 appear to describe the same delegate gap in different words. One consolidated candidate list is needed before any of these rows is cited.
9. **Link-proof form is circular between 02 and 06.** 06 says the form (co-signature or ZK) is "to be fixed by 02"; 02's toll-payment row is "handed to 06". It is 06's open question 1.
10. **Set C gas has no real-option source.** Rows in 05, 06, 08 and 09 carry cost terms that depend on C1–C4 gas; 09 states that harness gas is not O7 gas and 00's register says S16 "needs a Set C harness". These rows stay at design status regardless of Ready %.
11. **Rows overtaken by the build.** 03's "Realisability inventory" states the repository "as of 2026-09-03"; 01's "awaits S7/S8 numbers" and "Assertion to be added to S7", 02's "variables to be bound by 10", 07's "Contingent on build; 10 reports" and 11's "Ready % rises when test/vid.js is green" were all written before 10 existed. Their Ready % and Notes are carried unchanged and now understate the evidence.
12. **Ready % is not confidence.** 01's placement taxonomy (85%) rests on EVM constants taken from the brief; 02's master comparison table (70%) has every cell DIGEST-LEVEL. See S1 "Verification debt" for the sources these rows stand on.

## 5. How to apply

Append the rows of §2 to Content Block Registry v11.3 as new rows to produce the next registry version, and record the application in S3. Before applying: resolve the rerun date (§4 item 2); rewrite stale S-numbers per §4 item 1; check the new rows against v11.3 for collisions, which this pass could not do. K-HDA-1 to K-HDA-7 change existing v11.3 text and are applied only through the S3 K-ledger.
