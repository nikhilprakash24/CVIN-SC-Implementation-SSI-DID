# TDP-002 — System Specification: Vehicle Identity Testbed (CVIN-SC)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Generated** by `docs/tdp/make_vcrm.py` from `docs/tdp/requirements.yaml`, the claim register (`docs/MEASUREMENT_CONDITIONS.md`), `docs/figures/dashboard_snapshot.json`, the tracked tree and `.github/workflows`. Do not edit by hand; edit the YAML and regenerate. Checked in CI.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000) for conventions.
**Format:** MIL-STD-961E section order (1 scope, 2 applicable documents, 3 requirements, 4 verification, 5 packaging, 6 notes). Format only; no certification is claimed.

## 1. Scope

1.1 **Identification.** This specification covers the research testbed in this repository: nine Ethereum identity substrates and one application profile (layer 1), a W3C credential and resolution layer (layer 2), a connected-vehicle message testbed with mock mobility (layer 3) and the comparison and evidence machinery (layer 4 and `tools/run_identity`).

1.2 **Purpose.** It states, as shall-statements, what the testbed was built to show, each traced to a research question, hypothesis, pre-registration, threat goal or rigour rule already on the trunk, so that verification can be read off the claim register mechanically (TDP-005).

1.3 **Limits.** The testbed measures on an in-process EVM (M1), in-process cryptography (M0) and mock mobility. It has no radio, no channel, no real traffic and no public-network run. Every requirement carries its limit verbatim from the register's caveats.

## 2. Applicable documents

| Document | Role here |
|---|---|
| `docs/MEASUREMENT_CONDITIONS.md` | condition tags M0-M2; the claim register (#1-#52) |
| `docs/STYLE_AND_RIGOUR_GUIDE.md` | rules on numbers, claims and process |
| `docs/THREAT_MODEL.md` | adversaries A1-A4, goals G1-G8 |
| `docs/LATENCY_BUDGET.md` | the 100 ms interval, the identity share f and P*(f) |
| `docs/design/INFRASTRUCTURE_PREREG.md` | pre-registered I1-I5 with amendments |
| `docs/PLAN_MOBI_SUMO.md` | pre-registered M4, M5 |
| `docs/phase2/SCOPE_RECONCILIATION.md` | RQ1-RQ4 as restated to the evidence (Scope v3) |
| SAE J2945/1 | the 10 Hz BSM cadence the budget derives from |
| IEEE 1609.2; ETSI TS 103 097 | the certificate-based baselines the PKI design models |
| W3C DID Core v1.0; W3C VC Data Model v2.0 | the structures the credential layer is checked against |
| MOBI VID I v2.0 TS/2024; VID II UC texts | the lifecycle profile is checked against the public texts only |
| MIL-STD-961E | the section order of this document |

## 3. Requirements

Convention. "Shall" marks a requirement. The threshold values are the ones the trunk declared before the measurement (a pre-registration, the latency budget, the CI gate); none is chosen here. Each requirement ends with its declared limit.

### 3.1 System and scope (SYS)

**SYS-01 Identical operation set across substrates.** The comparison framework shall drive each of the nine identity substrates and the MOBI VID profile through one declared operation catalogue, and shall record an operation a substrate cannot perform as not applicable rather than emulating it.

- Derived from: RQ1; chapter 3 section 3.2 (identical operation set; "not supported" is null, never faked)
- Verification: Inspection; register #25, #34
- Limit: Minimal representative implementations of ERC-4337 and LSP8 (chapter 4 caveats); "excl. n/a" totals are not comparable with full totals (#35).

**SYS-02 One evidence register for every number.** Every quantitative claim in a thesis chapter shall carry a condition tag, a source path and a commit, and shall be cited only from a claim-register row of status V.

- Derived from: guide rules 1.1.2, 1.1.3; docs/MEASUREMENT_CONDITIONS.md section 2
- Verification: Inspection
- Limit: The checker scans tracked Markdown only; HTML and SVG outputs are held by their generators' --check instead.

**SYS-03 Declared conditions per measurement.** Every measurement shall be produced under one of the declared condition tags (M0 in-process, M1 Hardhat local, M1-H harness, M1-H/HTTP, M2 public testnet) and the tag shall travel with the number.

- Derived from: docs/MEASUREMENT_CONDITIONS.md section 1
- Verification: Inspection; register #25, #27, #34
- Limit: No M2 (public testnet) measurement exists on the trunk (N-11).

### 3.2 Cost and storage (RQ1) (PRF)

**PRF-01 Nine-standard gas table, deterministic.** The gas benchmark shall report exact receipt gas for deploy, create, update, delegate-or-claim, revoke and transfer on every substrate, and thirty consecutive runs of one commit shall be byte-identical.

- Derived from: RQ1; H1; guide rule 1.1.8
- Verification: Test; register #25; threshold: 30/30 runs byte-identical
- Limit: M1 only (local Hardhat, cancun); operation definitions differ per standard and are declared per row.

**PRF-02 Create-identity ratio stated under its definition.** The create-identity cost ratio between ERC-1056 and ERC-721 shall be reported under each operation definition in use (bare creation; VIN bound on both sides), never as a single figure.

- Derived from: H1 (creation half); register
- Verification: Analysis; register #6, #25
- Limit: H1's update and lifetime halves are not supported (#35); the split verdict is the one to report.

**PRF-03 Lifecycle gas over seventeen events.** The metrics harness shall report lifecycle gas over the declared seventeen MOBI VID events for every substrate, with events a substrate lacks listed as excluded.

- Derived from: RQ1; H1 (lifetime half); H4
- Verification: Test; register #30, #35
- Limit: Run of record 2026-10-23T00-49-12Z_1f4ace0 (A3b re-run on the one trunk); the harness flag that marks measured-code dirtiness is live since WM-2 A6 (2026-10-23; D33, N-19).

**PRF-04 Lifetime cost model with sensitivity band.** A fifteen-year lifetime cost model shall rank substrates with a declared sensitivity band on recurring event frequency.

- Derived from: RQ1; docs/SCALING_EXPERIMENTS.md
- Verification: Analysis; register #26
- Limit: A model over an assumed profile, not a measurement of a fleet.

**PRF-05 On-chain footprint and read cost against history.** The harness shall report, per substrate, the storage writes and log bytes of the lifecycle and the RPC calls and bytes needed to resolve a document at history depths 1, 10 and 50.

- Derived from: RQ1 (storage locus); Phase 2 focus F1
- Verification: Test; register #31, #49, #51
- Limit: SSTORE opcodes counted, not net slots; per-identity contract code not counted (#49).

**PRF-07 Relayed and account-abstracted write cost.** The gas of a write submitted by a relayer on a signed message, and of a write through an account-abstraction entry point, shall be reported against the owner's direct write on the same substrate.

- Derived from: Phase 2 focus F3 (interaction modes); register
- Verification: Test; register #34, #50
- Limit: Gas only; who pays and who is trusted are not measured; the ERC-1056 signed digest omits the chain id (D52).

**PRF-06 Dominance analysis on declared criteria.** The frontier analysis shall evaluate every substrate on six declared criteria and shall report dominance as computed, including the hybrid's position.

- Derived from: H5; register
- Verification: Analysis; register #36
- Limit: The O(1) on-chain credential check is a design property assigned per adapter, not a measurement; CVIN-Combined is dominated by ERC-4337 on all six criteria (#36).

### 3.3 Security and observability (RQ2) (SEC)

**SEC-01 Executable revert harness, strict reasons.** Every applicable attack cell of the security harness shall revert with its documented expected reason, with a differential control showing the authorised action succeeds.

- Derived from: RQ2; H5; goals G1-G4; chapter 3 section 3.5.1
- Verification: Test; register #28; threshold: 43 applicable cells DEFENDED
- Limit: 11 cells are declared not applicable; the on-chain script accepts any revert, so "43/43" refers to the strict harness only (#28).

**SEC-02 Signed generation time, freshness window and replay cache.** Every message verifier shall sign the generation time with the payload, reject messages outside a declared freshness window, and reject a repeated signed digest within that window.

- Derived from: goal G3; review-02 T-9; docs/THREAT_MODEL.md section 4
- Verification: Test; register #21, #45
- Limit: A fresh message relayed inside the window to a receiver that never heard it is not detected (#45); ERC-1056 signed operations do not bind the chain id (D52, G3 narrowed).

**SEC-03 Revocation staleness bounded by the re-check cadence.** A verifier that re-checks revocation every k messages shall accept at most k minus 1 messages from a revoked sender, for vehicles and for roadside units.

- Derived from: H3; I3; goal G4
- Verification: Test; register #32, #37, #46; threshold: I3 at k=25 PASS (bound 24)
- Limit: A message count, not a time; the verifier cache does not expire; the registry is in-process for I3 (#46).

**SEC-04 Revoked key under clock skew.** The ERC-1056 provider shall reject a revoked key regardless of the verifier's clock offset from the chain.

- Derived from: defect D51 (open high at WM-1 close; fixed in code at WM-2 C0)
- Verification: Test; register #32, #37
- Limit: Rows

**SEC-05 Attestation authority.** An on-chain lifecycle attestation shall be accepted only when signed by a party authorised for that vehicle.

- Derived from: goal G2, G4; register
- Verification: Test; register #28
- Limit: The signature check is in place; since WM-2 C2 (report 22) the attester must also be the vehicle's owner or its veriKey delegate, once per event (D54 fixed); the role list is still granted registry-wide.

**SEC-06 VIN confidentiality on chain.** The vehicle identification number shall not appear in plaintext in any on-chain state or event of the MOBI VID registries.

- Derived from: goal G7; A4 observer
- Verification: Inspection; register #28
- Limit: The cv2x testbed derives a vehicle identity from an unsalted VIN hash (D64, open); the matrix row is structural, not a measurement of linkability.

**SEC-07 Pseudonym pool observability.** The linkability of a delegate-based pseudonym pool on a public registry shall be measured by the number of pseudonyms one log query returns, with its gas cost.

- Derived from: RQ2 (observability); M5 pre-registration; SC-02
- Verification: Test; register #38
- Limit: Chain-layer linkability only; radio, timing and position linkability are out of scope (SC-02).

### 3.4 Standards expression (RQ3) (STD)

**STD-01 Internal structural checker at or above ninety percent.** The executable W3C checker shall score at least 90 percent on DID Core v1.0 and VC Data Model v2.0 structural checks, with every failing check named.

- Derived from: H2; RQ3
- Verification: Test; register #4; threshold: score >= 90
- Limit: Self-scored and structural; the DID Core checks test a synthesised document (C5 gap). WM-2 C1 (report 21) made did:ethr resolution read the chain when given a provider, but the checker resolves without one, so its documents are still synthesised.

**STD-02 External DID test suite.** The resolver shall be run against the external W3C DID test suite and every generated test shall be reported with its outcome.

- Derived from: H2; RQ3
- Verification: Test; register #24; threshold: 335 of 336 generated tests
- Limit: The denominator is 336 generated tests, not 441; DID-URL dereferencing is not run.

**STD-03 MOBI-VID-inspired lifecycle on several backends.** The birth and lifecycle operations shall be realised on the ERC-1056, ERC-721, ERC-725, ERC-735, ERC-1155 and MOBI V2 backends with a declared fidelity score per backend.

- Derived from: H4; RQ3
- Verification: Demonstration; register #30, #33
- Limit: 2 of 8 VID I MUSTs met; the profile is "MOBI-VID-inspired, checked against the public texts" (SC-14a).

**STD-04 Database parity for lifecycle writes.** The lifecycle writes of the MOBI V2 registry shall be compared with an in-process registry under a pre-registered band, and the verdict reported as it fell.

- Derived from: M4 pre-registration (PLAN_MOBI_SUMO.md A.2); SC-13
- Verification: Test; register #33
- Limit: Writes PASS (at least 10x); "equal once cached" FAIL (ratio set by the baseline's serialisation); the baseline is a lower bound.

### 3.5 Real-time verification (RQ4) (RTV)

**RTV-01 Warm credential verification inside the identity budget share.** Warm verification of a signed basic safety message with a pre-issued credential shall take no more than 0.5 ms per message, so that at least 100 neighbours can be serviced inside half of the 100 ms interval.

- Derived from: H3; RQ4; docs/LATENCY_BUDGET.md section 2 (P*(0.5) >= 100)
- Verification: Test; register #27; threshold: SSI warm verify median <= 0.5 ms
- Limit: M0, mock mobility, one host; re-run on the one trunk at A3b (2026-10-23,

**RTV-02 Uncached chain read at message time reported.** The cost of resolving a sender's key and revocation status from the chain at message time shall be measured on the same operations as the PKI baseline and reported beside it.

- Derived from: H3 (second half); RQ4; A.2 questions 1 and 2
- Verification: Test; register #21
- Limit: The ERC-1056 column is the cv2x registry, not EthereumDIDRegistry (K-5); the PKI baseline is in-process, a lower bound on deployed PKI.

**RTV-03 Freshness-k curve with both refresh modes.** The amortised verification cost shall be measured as a function of the re-check cadence k for a full-resolution refresh and a one-call probe refresh, and the host of each run shall be stated with its local cost.

- Derived from: H3; crux C4; docs/LATENCY_BUDGET.md section 4
- Verification: Test; register #32, #37, #52
- Limit: The knee is the most host-sensitive figure; no finite k reached P*(0.5)=100 on

**RTV-04 Signed message size.** The size of a signed safety message shall be reported for the certificate-carrying PKI design and the credential-referencing SSI design.

- Derived from: A.2 question 4 (bounded to message size); RQ4
- Verification: Test; register #23
- Limit: Bytes only; no channel model, so no airtime or loss figure follows from it.

### 3.6 Infrastructure messaging (pre-registered I1-I5) (INF)

**INF-01 SPaT verification cost against BSM (I1).** Warm verification of a signed SPaT from a credentialed roadside unit shall be measured against a warm BSM in the same run, with the pre-registered pass band reported as it fell.

- Derived from: pre-registered I1 (docs/design/INFRASTRUCTURE_PREREG.md; amendments A1, A4, A6)
- Verification: Test; register #44
- Limit: The ratio moved outside its band on verifier v3 and the cause is not isolated (different host builds); not falsified.

**INF-02 Registered attacks rejected for their reasons (I2).** Each registered attack on the infrastructure verifier shall be rejected with its expected reason in every run, and the warm variants shall verify warm.

- Derived from: pre-registered I2 (amendments A4, A5, A6)
- Verification: Test; register #45; threshold: 30/30 runs, all 15 checks as expected
- Limit: Not covered - a fresh message relayed to a receiver that never saw it within the 1 s window.

**INF-03 Revoked roadside unit trusted for at most k minus 1 messages (I3).** A vehicle that cached a roadside unit's key shall accept at most k minus 1 further SPaT after the unit's credential is revoked.

- Derived from: pre-registered I3
- Verification: Test; register #46
- Limit: In-process registry; message count, not time; no cache expiry.

**INF-04 Roadside unit identity cost on chain (I4).** The gas of creating a roadside unit identity, anchoring its key and endpoint, handing control to the authority, rotating and revoking the key shall be reported as a range over declared seeds.

- Derived from: pre-registered I4 (amendments A2, A4); guide rule 1.1.10
- Verification: Test; register #47
- Limit: Per-credential issuance costs no gas in this design and is not measured.

**INF-05 Back-haul operation cost (I5).** The cryptographic cost of the controller-to-roadside-unit-to-vehicle path shall be reported as a sum of per-operation medians, labelled as not a path latency.

- Derived from: pre-registered I5 (amendment A3)
- Verification: Test; register #48
- Limit: The harness does not chain the SPaT to the controller update; queuing, network and tail are excluded.

### 3.7 Evidence and reproducibility (process) (EVD)

**EVD-01 Run stamp with per-producer scope.** Every producer of a result of record shall stamp its output with the commit, a producing-code dirty flag computed over its resolved import closure and declared inputs, and the whole-tree flag beside it.

- Derived from: guide rule 1.1.6; WM-2 A2 (D49)
- Verification: Inspection
- Limit: The metrics harness takes its measured-code flag from the shared helper since A6 (2026-10-23, D33 closed by it).

**EVD-02 Promotion only from a clean run.** A result file shall reach its tracked path only through a promote step that refuses dirty runs, other commits, changed scopes, edited outputs and undeclared destinations.

- Derived from: WM-2 A4 (D56)
- Verification: Test
- Limit: A run at an earlier commit cannot pass the promote step and is copied with a manifest as a declared deviation (report 19).

**EVD-03 Pre-registration before any run, amendments dated.** Every pre-registered experiment shall have its questions, measures, expectations and falsifiers committed before the first run, and every departure shall be a dated amendment marked post hoc where applicable.

- Derived from: guide rules 1.2.7, 1.2.9
- Verification: Inspection; register #44, #45, #46, #47, #48, #33, #38
- Limit: Amendments A1-A3 were post hoc and are marked so.

**EVD-04 Generated documents regenerated and checked.** Every generated document (snapshot, registers, charter, cards, presentation, Phase 2 figures) shall be rebuilt from committed sources and compared in CI, and shall never be edited by hand.

- Derived from: guide rule 1.3.10; handback gotchas
- Verification: Inspection
- Limit: The contribution record depends on git history and is regenerated at each pass's close, not checked in CI.

**EVD-05 Every guard shown to fire.** Every clean-tree flag, stale-figure checker and document check shall have a probe in CI that fails on the broken version.

- Derived from: guide rule 1.3.11
- Verification: Demonstration
- Limit: A probe proves the guard can trip, not that it trips on every fault class.

**EVD-06 Full suite with no skips.** The Hardhat suite, both Python bodies and the demo runner shall run in CI with a skip counted as a failure, and the test count shall be gated against the grand report.

- Derived from: guide rule 1.2.6; audit U-F7, T-2
- Verification: Test
- Limit: Three MOBI demo steps hash block.timestamp and are declared timestamp-dependent (B1).

## 4. Verification

4.1 **Methods.** T test (the measurement runs and its output is compared with a declared threshold or recorded as a verdict); A analysis (a derivation from measured data, with its inputs named); I inspection (the artefact exists in the tracked tree and, where stated, a CI step exercises it); D demonstration (a run shows the behaviour; counts, not thresholds).

4.2 **Cross-reference.** The status of every requirement is computed in TDP-005 from the register, the snapshot, the tree and the workflows. This document carries no status.

4.3 **Rule.** A requirement is verified only by register rows of status V. An E, S, U or B row is listed and does not count (the rule of `docs/thesis/CRUX_REGISTER.md`).

## 5. Packaging and delivery

The deliverable is the repository at a named commit: contracts, scripts, tests, results of record with run stamps, the register, the generated documents and this package. A release is a version tag cut by the author (N-11). Reproduction commands are in `docs/HANDBACK_2026-10-14.md` section 5 and TDP-008.

## 6. Notes

6.1 **Definitions.** Substrate: one identity standard realised as a contract set. Warm/cold: with/without the sender's key in the verifier cache. k: the re-check cadence in messages. P*(f): the number of neighbours serviceable inside the fraction f of the 100 ms interval. V/E/S/U/B: register statuses (verified, estimate, superseded, unverified, bundle lineage).

6.2 **Acronyms.** BSM basic safety message; SPaT signal phase and timing; RSU roadside unit; TMC traffic management centre; DID decentralised identifier; VC verifiable credential; VIN vehicle identification number; PKI public-key infrastructure; EVM Ethereum virtual machine; RPC remote procedure call; CI continuous integration.

6.3 **Count.** 36 requirements in 7 groups.
