CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**The VID Reference Layer: Build Documentation**

**What was built in this pass, how it sits beside the minimal interface, what was measured, and what the measurements found**

Document 11 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · October 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type B (tables, traces, code) with Type A prose in §1, §6, §7 → Chapter 4 (Stage 1 evidence; new §4.5), Appendix (traces)*

---

## 1. What this document is evidence of

This is the only document in the suite whose every number was produced by code executed in this pass. The other primary documents argue; this one reports. It records a small, deliberately minimal build: a Vehicle Identity (VID) layer placed above the twelve-function `IMinimalSSI` interface without altering it, comprising an endorsement registry, a typed-credential convention, an off-chain credential library, two trace-emitting scenarios, and a test suite. The build exists to turn three claims that the rest of the suite depends on from assertions into observations:

1. that the MOBI VID I birth certificate, a vehicle registration, a driver's licence, and all eleven MOBI VID II lifecycle event types can be realised with the twelve functions plus a governance extension, with no interface change;
2. that credential content can stay entirely off-chain while integrity, issuer binding, status, and issuer entitlement remain verifiable, and that the off-chain read path needs zero chain reads;
3. that the choice of anchoring pattern changes on-chain cost by an order of magnitude, measurably.

All three were observed. Seven findings (F-VID-1 to F-VID-7) were logged along the way, two of which are candidate errata for the formal specification.

**Scope honesty.** Everything here ran on option O1 (the ERC-1056 pattern) on a Hardhat local EVM. Nothing ran on O2–O8, on Besu, on a testnet, or on hardware. No zero-knowledge proof was generated. Set C (reputation, validation) was not implemented. Gas is a property of the contract and compiler configuration and transfers to any EVM chain; latency was not measured and nothing here supports a latency claim.

## 2. Provenance and reproducibility

| Item | Value |
|---|---|
| Repository | `github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID`, branch `vid-build` (local, unpushed at time of writing) |
| Location | `5_minimal-ssi-sandbox/` |
| Base | Canonical `cvin-sandbox` v1.3 (architect pass, 2026-06-05), vendored unmodified except one line: `solc` dependency exact-pinned to `0.8.24` (was `^0.8.24`; the caret was a flagged reproducibility risk in the July handoff) |
| Toolchain | Node 24.16.0, npm 11.13.0, Hardhat 2.x, solc-js 0.8.24 via the in-config subtask override, optimizer 200 runs, EVM target paris |
| Run dates | S1 rerun 2026-09-03 (local; 09-04 UTC); tests, S7, S8 2026-10-04 |
| Interfaces | `IMinimalSSI`, `ISetA`, `ISetB`, `ISetC` — byte-identical to v1.3 |
| O1 implementation | `O1_ERC1056.sol` — byte-identical to v1.3 |

To reproduce from a clean clone:

```bash
cd 5_minimal-ssi-sandbox && npm install
```

```bash
npx hardhat test
```

```bash
npx hardhat run scenarios/run_vid_minimal.js
```

```bash
npx hardhat run scenarios/run_vid_lifecycle.js
```

Expected: 19 passing tests; two new JSONL traces under `traces/`. Trace file names carry a wall-clock suffix, so a rerun produces new files and never overwrites the committed ones (trace immutability rule).

## 3. What was built

### 3.1 Design rule

The specification is normative and the build agent's standing rules forbid altering it. Every addition therefore lives *beside* `IMinimalSSI` and reaches it only through its public functions. The specification's own §6 names governance functions (`registerIssuer`, `endorseIssuer`) as permitted extensions; this build is the first implementation of that extension in the programme.

### 3.2 Artefacts

| Artefact | Role | On-chain state it adds |
|---|---|---|
| `contracts/governance/IControllerAdapter.sol`, `O1ControllerAdapter.sol` | Resolves "which address controls this DID" for one option by decoding that option's `resolveDID` (F2) output. One adapter per option keeps the governance layer implementation-agnostic. | None (pure view over F2) |
| `contracts/governance/EndorsementRegistry.sol` | G0 `addRoot`/`removeRoot`, G1 `registerIssuer`, G2 `endorseIssuer`, G3 `revokeEndorsement`, G4 `isEndorsed`. Endorsements are per credential type, time-bounded, optionally transitive, depth-bounded at 3. Callers act *as a DID*: controller (via adapter) or an F12-valid delegate of type `endorse`. A deactivated endorser DID (F4) voids its endorsements at read time. | Roots; issuer roles; endorsement records keyed (endorser, issuer, type) |
| `contracts/credentials/CredentialTypes.sol` | Fourteen `bytes32` type identifiers (VID_BIRTH, VEHICLE_REGISTRATION, DRIVER_LICENCE, eleven lifecycle types) and the typed-anchor rule `keccak256(abi.encode(typeId, schemaHash, contentHash))`. | None (library) |
| `contracts/credentials/TypedCredentialRegistry.sol` | T1 `declare` (optional on-chain typing) and T2 `verifyTyped`, a composite view returning F6 status ∧ G4 entitlement ∧ on-chain type binding. | One record per *declared* credential only |
| `lib/vid/credentials.js` | Off-chain layer: canonical JSON, hashing, W3C-shaped credential builders for the three minimal credentials and the lifecycle family, EIP-191 issuer signature over the typed anchor, holder wallet, verifier cache with a staleness window, fully offline verification, presentation-challenge construction, salted-digest selective disclosure. | None |
| `lib/vid/trace.js` | Shared JSONL emitter conforming to `traces/SCHEMA.md`, with extension tags G0–G4, T1–T2. | None |
| `scenarios/run_vid_minimal.js` (S7) | Minimal VID: three credentials, endorsement, off-chain and on-chain verification, presentation, three trust breaks. | — |
| `scenarios/run_vid_lifecycle.js` (S8) | All eleven lifecycle event types with role-gated endorsement, off-chain policy checks, Merkle batch, selective presentation, recall closure, decommission. | — |
| `test/vid.js` | Seven tests over the adapter, G1–G4, typing, and the off-chain library. | — |

### 3.3 The three minimal credentials

Each is a JSON object with W3C VC Data Model 2.0 shape (`@context`, `type`, `issuer`, `credentialSubject`, `validUntil`, `credentialSchema` with digest). None of it is written to the chain.

| Credential | Issuer → subject | Claims (all off-chain) | Privacy device |
|---|---|---|---|
| **VID birth certificate** (MOBI VID I) | OEM plant → vehicle DID | vinHash, make, model, modelYear, productionDate, manufacturerDid, plantCode | VIN never stored; `vinHash = keccak(VIN ‖ salt)` with the salt held by the holder |
| **Vehicle registration** ("car ID") | DMV → vehicle DID | plate, jurisdiction, ownerDid, validFrom, validUntil, registrarDid | Content off-chain; anchor reveals nothing |
| **Driver's licence** | DMV → driver DID | licenceClass, restrictions, jurisdiction, validity, `birthYearCommitment` | Birth year is a salted commitment, the hook for the age-predicate proofs of 02 §4 |

Measured canonical sizes (trace S7 seq 21): 813, 825, and 850 bytes respectively; the chain receives a 32-byte anchor for each.

### 3.4 Endorsement, concretely

The registry separates three things that are easy to conflate. *Registration* (G1) is a permissionless self-declaration of role and confers nothing. *Endorsement* (G2) is a typed, expiring statement by one DID that another may issue a credential type; it confers entitlement only if a chain of unexpired endorsements, each by an active DID, reaches a root within three hops, and every intermediate endorsement is marked transitive. *Roots* (G0) are declared by the registry administrator and are the governance boundary: who administers the registry is a deployment decision (a ministry, a consortium multisig, a Local CVIN operator) and is deliberately not solved in code.

In S7 the Ministry root endorses the DMV for VEHICLE_REGISTRATION and DRIVER_LICENCE, and the OEM root endorses its plant for VID_BIRTH. In S8 the Ministry endorses the OEM *transitively* for MAINTENANCE, REPAIR, and MODIFICATION, and the OEM in turn endorses its service centre — a two-hop chain that mirrors how an authorised service network is actually constituted.

## 4. Test results

`npx hardhat test`, 2026-10-04: **19 passing**, 0 failing.

| Suite | Tests | Result |
|---|---|---|
| O1_ERC1056 — IMinimalSSI compliance (unchanged from v1.3; spec §4.1 verbatim) | 12 | 12 pass |
| VID layer | 7 | 7 pass |

The seven VID tests assert: adapter controller/activity resolution through F2 only; G1 authorisation by controller or `endorse` delegate, and rejection of others; G2/G4 type-specificity and expiry; the transitive-endorser rule, unknown-issuer and self-endorsement rejection; G3 revocation and voiding by endorser deactivation; the typed anchor end to end including tamper rejection, non-reverting unknown-credential reads, and endorsement revocation leaving status valid but entitlement false; and the off-chain library's canonicalisation key-order independence, issuer recovery, tamper detection, and equality of the JavaScript and Solidity typed-hash encodings.

## 5. Measurements

All figures are `gasUsed` read from the committed traces. View calls cost no gas and are recorded as `kind: view`.

### 5.1 Traces on file

| Trace | Scenario | Entries | tx / view / off-chain | Total gas | Tags covered |
|---|---|---|---|---|---|
| `i2i_O1_ERC1056_1780620182135.jsonl` | S1 (architect pass, 2026-06-05) | 22 | 13 / 6 / 1 | 1,168,146 | F1–F12 |
| `i2i_O1_ERC1056_1788492893157.jsonl` | S1 rerun, this machine (2026-09-03) | 22 | 13 / 6 / 1 | 1,168,151 | F1–F12 |
| `vid_minimal_O1_ERC1056_1791157391842.jsonl` | S7 | 56 | 27 / 18 / 9 | 2,898,052 | F1–F12, G0–G4, T1–T2 |
| `vid_lifecycle_O1_ERC1056_1791157402169.jsonl` | S8 | 69 | 47 / 6 / 14 | 6,182,978 | F1, F2, F4–F8, G0–G2, G4 |

The S1 rerun reproduces the June trace exactly on twelve of thirteen transactions; `createPresentation` differs by five gas (62,446 against 62,441) because the challenge is derived from a random nonce and calldata zero-byte counts vary. This is the first operator-machine rerun of S1 on record and is offered as the G1 gate evidence the July handoff asked for; whether it is credited as G1 is the architect's call.

### 5.2 Gas by function (O1, all four traces)

| Tag | Function | Measured gas (min–max) | n | Spec §5.3 target (ERC-1056) | Within target |
|---|---|---|---|---|---|
| F1 | createDID | 161,823–178,935 | 22 | <100K | No (known deviation, FINDINGS 1) |
| F3 | updateDID | 44,760–45,036 | 3 | <80K | Yes |
| F4 | deactivateDID | 55,127 | 4 | <50K | No (10% over) |
| F5 | issueCredential, no expiry | 130,151–130,163 | 18 | <120K | No (8% over) |
| F5 | issueCredential, with expiry | 150,087–150,099 | 2 | <120K | No |
| F7 | revokeCredential | 32,968–32,980 | 4 | <50K | Yes |
| F8 | createPresentation, 1 credential | 62,441–62,574 | 4 | <150K | Yes |
| F8 | createPresentation, 2 credentials | 69,786 | 1 | <150K | Yes |
| F9 | addVerificationMethod | 59,595–59,607 | 5 | <100K | Yes |
| F10 | removeVerificationMethod | 36,454–36,478 | 3 | <50K | Yes |
| F11 | addDelegate | 54,227 | 3 | <60K | Yes |
| G0 | addRoot | 47,604 | 3 | — | — |
| G1 | registerIssuer | 76,800–76,812 | 9 | — | — |
| G2 | endorseIssuer, root endorser | 151,437–171,373 | 14 | — | — |
| G2 | endorseIssuer, non-root endorser | 182,800 | 3 | — | — |
| G3 | revokeEndorsement | 55,597 | 1 | — | — |
| T1 | declare (on-chain typing) | 150,463 | 1 | — | — |

Two observations the earlier documents in this suite could not make because the numbers did not yet exist. First, `deactivateDID` and `issueCredential` miss their targets by small margins on O1, in addition to the known `createDID` miss; three of the eleven state-changing functions are therefore over target on the lightest standard, all for the same structural reason (explicit storage for interface uniformity). Second, within G2 the root-endorser range splits cleanly: 151,437–151,461 for non-transitive endorsements and 171,373 for transitive ones, a difference of one storage slot for the flag.

### 5.3 The anchoring-pattern result

| Pattern | Writes | Gas | What is kept | What is lost |
|---|---|---|---|---|
| Per-event anchor (S8 seq 34–54) | 11 × F5 | 1,431,745 | Per-event F6 status and F7 revocation | — |
| Merkle-root anchor (S8 seq 62) | 1 × F5 | 130,151 | Integrity and existence of all eleven; 4-hash inclusion proofs off-chain | Per-event on-chain status and revocation |
| Off-chain typing (default) | 0 extra | 0 | Type bound into the anchor; verifier recomputes | Type not discoverable without the content |
| On-chain typing (T1) | 1 per credential | 150,463 | Type queryable without content | More than doubles the per-credential write cost |

The batching ratio is exactly the batch size, as the cost model in 01 §7 predicts: the anchor write is constant in the number of leaves. The lesson for the hybrid design in 03 is that batching is free in gas and expensive in revocation granularity, so it suits append-only history (maintenance, inspection) and does not suit revocable entitlements (registration, licence). The on-chain typing result is the other half of the same lesson: queryability is the costly property, and it was bought here for more than the price of the credential anchor itself.

### 5.4 Read-path observations

| Observation | Trace evidence |
|---|---|
| Three credentials verified for integrity and issuer binding with zero chain reads, from a warmed cache | S7 seq 32–34 |
| Eleven lifecycle credentials verified the same way | S8 seq 60 |
| After on-chain revocation, an unrefreshed cache still accepts | S7 seq 50 (ok=true), corrected at seq 51 after an F6 read |
| After endorsement revocation, F6 status remains valid while entitlement is false | S7 seq 53 |
| An unendorsed self-report is F6-valid and distinguishable only by G4 | S8 seq 55–56 |
| Replay of a used presentation challenge reverts | S7 seq 45 |
| A decommissioned vehicle DID remains resolvable with the deactivated flag | S8 seq 68 |

## 6. Findings

Recorded in `5_minimal-ssi-sandbox/docs/FINDINGS.md` items 4–10. Stated here with their consequence for the thesis.

**F-VID-1 — the minimal interface proves status, not content binding.** `verifyCredential` returns validity, issuer, revocation, and expiry, but not the anchored hash, and O1 has no getter. Through the twelve functions alone a verifier cannot confirm that the credential in its hand is the one anchored under a given identifier. The build closes the gap off-chain (issuer signature over the typed anchor, zero gas) or on-chain (T1, 150,463 gas). This is a specification-level observation and a candidate for spec v1.1: either F6 returns the hash, or the specification states that content binding is an off-chain obligation. It also sharpens the data-placement argument of 01: the interface as written already assumes the off-chain proof exists.

**F-VID-2 — credential validity is tied to issuer liveness.** F6 reports a credential invalid once its issuer DID is deactivated. That is right for a licence and wrong for a birth certificate, whose issuing plant may close while the vehicle lives on. The design consequence is an archival-issuer policy: immutable credentials are issued from a long-lived DID, or verifier policy distinguishes "valid now" from "validly issued".

**F-VID-3 — stale acceptance is real.** A cached verifier accepted a revoked registration until it refreshed. The staleness window is therefore not a theoretical parameter; it is the measured security parameter of every cached read path, and 03, 05, 06, and 08 treat it as such.

**F-VID-4 — endorsement is the most expensive governance write, and it amortises.** At 151K–183K gas an endorsement costs more than a credential anchor, but it is paid per issuer per type, not per credential.

**F-VID-5 — batching measured at 11:1**, with the revocation-granularity trade-off of §5.3.

**F-VID-6 — expiry costs a storage slot** (about 19.9K gas), which argues for putting expiry in the signed off-chain credential and reserving on-chain expiry for credentials whose expiry must be enforced against a non-cooperating holder.

**F-VID-7 — F5 is issuer-agnostic.** Anyone with a DID can anchor anything; F6 will call it valid. Entitlement is not among the twelve functions. This is the empirical case for the endorsement extension and the strongest single piece of evidence for the argument in 11 §2.

## 7. What was not built, and what it would take

| Not built | Why it matters | Smallest next step |
|---|---|---|
| The VID layer on O2–O8 | The layer is implementation-agnostic by construction, but that is untested; each option needs its own controller adapter | Blocked on WO-1 (ports); then one adapter and one environment variable per option |
| Set C (reputation, validation) | Scenarios in 04, 06, 09 depend on C1–C4 | A minimal `ISetC` harness beside O1, labelled as a harness, pending O7 |
| Merkle inclusion verification on-chain | S8 computes the root and anchors it; inclusion is verified off-chain only | A 20-line verifier library and a test |
| Any zero-knowledge proof | 02's staged plan (BBS+, then a circom range proof with an on-chain verifier) | Stage (b) of 02 §10 |
| Delayed-write reconciliation | 03 and 06 specify it; S14 is a design | A mock provider that rejects writes for N steps, then a batch anchor |
| Latency of anything | All tier claims remain design claims | Timing fields in the trace (schema v2), then Besu QBFT |
| Administrator governance for roots | A single admin key is a placeholder | A multisig or an on-chain vote; a design decision first |
| Explorer rendering of G/T tags | Layer 2 does not yet know the extension tags | Add the tags to the explorer's legend when WO-6 runs |

One process note. The canonical sandbox's standing rules send unplanned scope to a proposals file rather than to code. This build was directed by the operator and is logged in `BUILD_LOG.md` as work order WO-V with that provenance; it should be ratified or re-scoped by the architect, and `BUILD_PLAN.md` was left untouched for that reason.

---

## Sources used in this document

| Id | Source | Verification state | How used |
|---|---|---|---|
| — | Traces `i2i_O1_ERC1056_1780620182135`, `…1788492893157`, `vid_minimal_O1_ERC1056_1791157391842`, `vid_lifecycle_O1_ERC1056_1791157402169` | VERIFIED AT SOURCE (generated or read in this pass) | Every gas figure |
| — | `IMinimalSSI.sol`, `O1_ERC1056.sol`, sandbox `CLAUDE.md`, `ARCHITECTURE.md` v1.1 | VERIFIED AT SOURCE | Interface constraints, standing rules |
| — | SSI Minimal Function Specification (Formal) §5.3, §6 | VERIFIED AT SOURCE | Gas targets; governance extension |
| [27] | MOBI VID I–II | DIGEST-LEVEL (via the repository's own summary of event types and roles) | Credential and role vocabulary |
| [10] | W3C VC Data Model 2.0 | DIGEST-LEVEL | Credential object shape |

## Registry delta rows

| Content Block | T | Source | Ch. | Ready | Notes and status |
|---|---|---|---|---|---|
| VID reference layer build record (this document) | B | HDA 10 | 4 §4.5, App. | 85% | Convert §5–§6 to prose for the thesis |
| Gas-by-function table, O1, four traces | B | HDA 10 §5.2 | 4 | 90% | First table with G and T tags; three target misses now recorded |
| Anchoring-pattern measurement (11:1; on-chain typing cost) | B | HDA 10 §5.3 | 4, 5 | 90% | Feeds 01 §7 and 03 §8 |
| Findings F-VID-1 to F-VID-7 | A/B | HDA 10 §6; FINDINGS.md 4–10 | 4, 5 | 80% | F-VID-1 and F-VID-2 are spec v1.1 candidates |
| First operator-machine S1 rerun | B | HDA 10 §5.1 | 4 | 85% | G1 credit owed by architect |

## Open questions for the researcher

1. **Is WO-V ratified?** The build sits outside WO-0–WO-9. Should it be adopted into the canonical plan as a work order, or kept as a sidecar in this repository only?
2. **F-VID-1: change the specification or state the obligation?** Returning the anchored hash from F6 would alter the normative interface; stating that content binding is off-chain would not. Which goes into spec v1.1?
3. **Who administers roots?** The endorsement argument in the thesis needs a named governance model for the registry administrator. Is that a ministry, a consortium, or a per-Local-CVIN operator?
4. **Does the S1 rerun count as gate G1?** It was run by the build agent on the operator's machine, not by the operator by hand.
5. **Push and merge.** The branch `vid-build` is local. Should it be pushed to the fork and opened as a pull request, and against which repository — this one or `CVIN-ID/CVIN-ID-SCs`?

---

## Addendum A — Slice 1, steps 1a and 1b (2026-10-14)

Two of the five laptop-only steps planned in 00 §7 were executed after the suite was issued. Both run on O1 on the Hardhat network; the full test suite is now **23 passing**.

### A.1 S17 — dedicated batch anchor with on-chain inclusion (`scenarios/run_batch_anchor.js`, trace `batch_anchor_O1_ERC1056_1792035482337.jsonl`, 26 entries)

`BatchAnchorRegistry.sol` stores a Merkle root under a batch id for an issuer DID (authorised through the controller adapter), verifies leaf inclusion as a view, and revokes a whole batch. The three patterns on the same eleven credentials:

| Pattern | Writes | Gas | On-chain inclusion | Revocation granularity |
|---|---|---|---|---|
| A — eleven F5 anchors | 11 | 1,431,769 | per leaf (F6) | per leaf (F7) |
| B — root through F5 (S8's method) | 1 | 130,163 | none | whole root |
| C — `anchorBatch` | 1 | 122,139 | yes, gas-free view; 4-hash (128-byte) proof | whole batch (`revokeBatch`, 55,267) |

Ratios A/B = 11.00 and A/C = 11.72. This settles the open estimate in 01 §7 (g_a was guessed at 60,000): a purpose-built anchor is about 6% cheaper than reusing F5, not half the price, because the dominant cost is the new storage slots either way. The trace also shows a tampered leaf failing inclusion and the unauthorised-issuer revert. **Finding F-VID-8.**

### A.2 S14 — delayed write and reconciliation (`scenarios/run_delayed_write.js`, trace `delayed_write_O1_ERC1056_1792035487512.jsonl`, 28 entries)

`lib/vid/offline.js` models the OBU's link (ONLINE, READ_ONLY, PARTITIONED), a signed, counter-ordered write queue, and a reconciliation step that re-checks each queued event's dependencies against current chain state. The run: registration issued online → READ_ONLY (a toll pass is admitted on cached status and a signed event queued; the chain is still readable) → PARTITIONED (two telemetry events queued; the DMV revokes the registration meanwhile; the cached view still says valid — F-VID-3 reproduced at seq 19) → ONLINE (reconcile: toll pass rejected because its dependency is revoked, "revocation wins"; the two telemetry events anchored with one `anchorBatch`, 122,127 gas; inclusion proven on-chain). Writes during the outage: zero. Writes on reconnect: one. **Finding F-VID-9.**

What this does and does not show. It shows that the Anchor · Cache · Attest · Reconcile pattern of 03 §3 is implementable from the twelve functions plus a batch anchor, and that the staleness window is where the risk sits: the gate admitted a vehicle whose settlement was later denied, so the design must carry a dispute path (06 §3). It does not show timing (no latency fields yet; step 1c), and the link model is a flag in a script, not a network.

### A.3 Still open from Slice 1

1c trace timing fields (schema v2) · 1d minimal `ISetC` harness · 1e S16 federated round with Sybil injection. Decisions D1–D8 in 00 §8 are unchanged; D1 (push) is now more urgent, since six traces exist on one disk.

## Addendum B — Slice 1, steps 1c–1e (2026-10-14)

**1c Timing.** `lib/vid/trace.js` now records `latencyMs` on every transaction and (optionally) view entry; `traces/SCHEMA.md` carries it as schema v1.1, additive. On the Hardhat in-process network these values are a lower bound on any real network and are not reported here as results; the instrumentation exists so the same scripts yield comparable numbers on Besu QBFT (05 §7). The canonical S1 script keeps its own emitter and is untouched.

**1d Set C harness.** `contracts/harness/SetCHarness.sol` implements `ISetC` (C1–C4) as a *harness*, not as option O7: there is no agent NFT and no ERC-8004 fidelity. Its one deliberate design choice is that an attester must hold an endorsement for `REPUTATION_ATTESTER` in the `EndorsementRegistry` before it may score (gated mode); an ungated mode exists as the experimental control. Because `ISetC` defines no way for a validator to answer a validation request, the harness adds `resolveValidationAs` — **finding F-VID-11**, a candidate for `ISetC` v1.1. Gas on the harness: C1 `attestReputationAs` 83,493 (repeat attester) to 117,693 (first attestation of a subject); these are harness figures and must not be cited as ERC-8004 costs.

**1e S16 federated round with Sybil injection** (`scenarios/run_fl_round.js`, trace `fl_round_O1_ERC1056_1792035691983.jsonl`, 97 entries). A toy scalar model (six honest clients reporting ≈80, four Sybils reporting 20); contributions are signed off-chain objects whose digests are Merkle-anchored once per round (`anchorBatch`); the aggregator reads reputation (C2) and weights by it; a model-provenance validation request (C3) is raised and resolved by the endorsed aggregator (C4).

| Configuration | Sybil mutual scoring | Sybil weight | Unweighted error | Reputation-weighted error |
|---|---|---|---|---|
| GATED (endorsed attesters only) | 4 attempts, all revert `NotEntitled` | 0.05 (floor) | 23.67 | **1.87** |
| UNGATED (anyone scores anyone) | 12 accepted | 1.00 (reputation 100/3) | 24.35 | **27.59** |

The ordering is the result, not the magnitudes (the model is a toy and the Sybil fraction is chosen): with an entitlement gate on attesters, reputation suppresses the Sybils; without it, reputation is *worse than no weighting* because the Sybils manufacture their own standing. That is the chain 09 argues — collective computation needs reputation, reputation needs Sybil-resistant identity, and the Sybil resistance here is exactly the endorsement registry. **Finding F-VID-10.**

**Slice 1 status: complete** (1a–1e). Test suite: 26 passing. Traces on file: eight. Next slices (00 §7): proofs (Slice 2), other options and Besu (Slice 3), hardware (Slice 4). Decisions D1–D8 unchanged.

## Addendum C — Slice 2, stage (b): BBS+ selective disclosure (2026-10-15)

One new dependency (`@mattrglobal/bbs-signatures` 1.4.0, WASM in Node). `lib/vid/bbs.js` signs the credential's claim vector with a BLS12-381 BBS+ key, derives nonce-bound proofs revealing a chosen subset, and verifies them with the issuer's public key alone. Scenario S19 (`run_bbs_presentation.js`, trace `bbs_presentation_O1_ERC1056_1792062147559.jsonl`, 30 entries) presents the same driver's licence to three verifier classes under three policies. Suite: **29 passing**.

| Verifier | Policy | Revealed | Proof size | Prove / verify (laptop, WASM) | On-chain |
|---|---|---|---|---|---|
| Police (forensic tier) | full disclosure | 9/9 | 384 B | 93 / 66 ms | F8 commitment 62,470 gas |
| Car-share kiosk | class + validity | 2/9 | 608 B | 107 / 59 ms | F8 commitment 62,470 gas |
| Age-gated venue | jurisdiction only | 1/9 | 640 B | 116 / 116 ms | F8 commitment 62,470 gas |

What this settles. (i) The proof layer is orthogonal to the anchor: the typed hash passed to F5 is unchanged, the F8 commitment costs the same, and the verifier's only chain reads are F6 and G4 (02 §3, 03 §2 layer L3). (ii) Unlinkability is observed: two proofs for the same policy differ byte-for-byte, whereas the hash path re-sends the same credential bytes every time. (iii) The issuer key is a DID verification method (F9, 96-byte key, 60,967 gas), so key discovery is the ordinary resolve-and-cache path. (iv) A BBS+ proof proves issuance, not currency: after F7 it still verifies and only F6 says revoked (**F-VID-14**), which is the stage (d) accumulator question. (v) Proof size rises as disclosure falls (**F-VID-13**).

What it does not settle. Timings are a laptop with WASM, not an OBU; no range predicate was proven (the age gate reveals only the jurisdiction — stage (c), which needs the circom compiler binary, a non-npm install); no on-chain proof verification was measured; revocation privacy (accumulator witnesses) is untouched.

## Addendum D — Slice 2, stage (c): Groth16 range predicate with on-chain verification (2026-10-15)

Dependencies (exact pins): `circom2` 0.2.8 (the WASM build of circom 2.0.8 — no native compiler install), `snarkjs` 0.7.5, `circomlib` 2.0.5, `circomlibjs` 0.1.7. Circuit `circuits/AgeGate.circom`: Poseidon(birthYear, salt) = commitment ∧ birthYear ≤ maxBirthYear; 256 constraints, two public signals. A 2¹² powers-of-tau ceremony and the Groth16 zkey live in `zk/` (final artefacts committed; intermediates ignored). The verifier is the snarkjs Solidity export; `ZKAgeGate.sol` wraps it with a replay-protected `admit` transaction (so the cost is measurable) and a free `check` view. Scenario S20 (`run_zk_age_gate.js`, trace `zk_age_gate_O1_ERC1056_1792062543673.jsonl`, 17 entries).

| Step | Measured |
|---|---|
| Proof generation (laptop, WASM witness, first call incl. initialisation) | 3,999.9 ms |
| Off-chain verification (snarkjs, first call) | 645.3 ms |
| Proof calldata | 705 B |
| On-chain `check` (view) | 0 gas, returns true |
| **On-chain `admit` (Groth16 pairing check + replay flag + event)** | **250,283 gas** |
| F8 presentation commitment alongside | 62,458 gas |
| Replay of the same admission | reverts `Replay` |
| Same proof against another holder's commitment | reverts `InvalidProof` |
| Under-age year (2012 > 2008) | no witness, hence no proof — the constraint fails at proving time |

What this settles. The thesis's standing "≈200–350K gas" for Groth16 verification (K-HDA-6) now has a measured point at the low end, for a two-signal circuit on bn128, inclusive of a storage write. The three disclosure paths are now side by side on the same credential: the hash path reveals the credential; BBS+ (Addendum C) reveals chosen claims; the predicate proof reveals only the result — and the on-chain cost of the first two is F8 alone, while the third adds either a free view or a ≈250K transaction (02 §3's "verify off-chain, anchor the verification" rule applies at Tier 2). Proving is the expensive side by two orders of magnitude (**F-VID-16**), which makes prover placement — OBU, pre-computation at issuance epochs, or a delegated prover — the design question for 05's Tier 2 budgets, not verifier gas. A predicate-capable credential needs a Poseidon commitment beside (or instead of) the keccak one (**F-VID-17**).

What it does not settle. All timings are a laptop with a WASM witness generator on a cold start; nothing here is an OBU figure. The ceremony is a sandbox ceremony (single contributor) and the circuit has no revocation input; a non-revocation predicate (accumulator witness) is stage (d) territory.

**Slice 2 status:** (a) salted digests — in repo; (b) BBS+ — done; (c) Groth16 predicate — done; (d) anoncreds-rs comparison — not started (Rust/Python FFI; needs a decision on whether it lives in this repository).

## Addendum E — WO-1 begins: O2 (ERC-721) ported; the VID layer runs on a second option (2026-10-17)

`O2_ERC721.sol` is a fresh native implementation (the Stage 12 source was not available; WO-1's fallback clause applies): `createDID` mints a soulbound token (OpenZeppelin 5.0.2 base, `_update` reverts every transfer and burn), `ownerOf` is the controller, deactivation sets a flag and keeps the token so the DID stays resolvable (DID Core §7.3 — the burn-versus-deactivate gap recorded in Building Paths is closed by *not* using burn), keys and delegates are per-token state, and Set B is the shared anchor pattern. It is admitted to the compliance suite at **12/12 unmodified**; four native-semantics tests were added (mint, soulbound, deactivate-without-burn, adapter reuse). Suite: **48 passing** (12 compliance tests × 2 options + 24 layer tests).

S1, S7 and S8 were then run with `IMPL=O2_ERC721` and **no script changes** — the implementation-agnostic claim of §7 is now observed, because O2 returns the same `resolveDID` document layout as O1, so the controller adapter and every governance and credential contract work unchanged (a convention now recorded for O3–O8).

| Function | O1 (S1) | O2 (S1) | Δ |
|---|---|---|---|
| createDID (first / subsequent) | 178,935 / 161,835 | 185,326 / 168,226 | +6,391 |
| issueCredential | 130,163 | 128,393 | −1,770 |
| addVerificationMethod | 59,607 | 57,767 | −1,840 |
| addDelegate | 54,227 | 52,495 | −1,732 |
| createPresentation (1 credential) | 62,441 | 60,729 | −1,712 |
| revokeCredential | 32,980 | 33,087 | +107 |
| removeVerificationMethod | 36,478 | 34,743 | −1,735 |
| updateDID | 44,760 | 42,935 | −1,825 |
| deactivateDID | 55,127 | 53,280 | −1,847 |

The mint costs about 6.4K more than O1's explicit-DID write; everything else is marginally cheaper on O2. The thesis's Pass-1 Set A anchor placed ERC-721 at 15/24 against ERC-1056's 23/24; these traces show that gap is one of *semantics* (what the standard offers natively), not of *gas* once the missing semantics are added as per-token state — a point the comparative evaluation should make explicitly (**F-O2-2**). Governance writes on O2 are within ~1.5K of O1 (registry storage dominates).

Remaining in WO-1: O3 ERC-725, O4 ERC-725xy, O5 ERC-1155, O6 ERC-4337 — each needs its native pattern and, where its document layout differs, its own controller adapter.

## Addendum F — O3 (ERC-725) ported: the contract-per-identity profile measured (2026-10-17)

`ERC725Account.sol` is a minimal ERC-725X/Y account (key-value `getData`/`setData`, `execute`, owner plus a manager role) written fresh because the ERC725Alliance package pins OpenZeppelin 4.x against the 5.x pin O2 uses. `O3_ERC725.sol` deploys one account per `createDID`; the DID is the account address and every identity datum — metadata, verification keys (the key bytes themselves), delegates, the deactivation flag, and the credential anchors (in the issuer's own store) — is ERC-725Y data readable with `getData` and no indexer. Admitted **12/12 unmodified**; S1, S7, S8 run unchanged; suite **60 passing** (12 × 3 options + 24 layer tests).

| Function | O1 ERC-1056 | O2 ERC-721 | O3 ERC-725 | Spec target (725) |
|---|---|---|---|---|
| createDID (first / next) | 178,935 / 161,835 | 185,326 / 168,226 | **764,090 / 746,978** | <600K — missed |
| updateDID | 44,760 | 42,935 | 178,398 | <100K — missed |
| deactivateDID | 55,127 | 53,280 | 92,675 | <60K — missed |
| issueCredential | 130,163 | 128,393 | 142,377 | <150K |
| revokeCredential | 32,980 | 33,087 | 74,587 | <60K — missed |
| createPresentation (1 cred.) | 62,441 | 60,729 | 79,084 | <200K |
| addVerificationMethod | 59,607 | 57,767 | 169,101 | <120K — missed |
| removeVerificationMethod | 36,478 | 34,743 | 66,974 | <60K — missed |
| addDelegate | 54,227 | 52,495 | 85,306 | <70K — missed |
| registerIssuer (G1) | 76,800 | 75,326 | 111,002 | — |
| endorseIssuer (G2, root) | 151,449 | 149,975 | 185,519 | — |
| revokeEndorsement (G3) | 55,597 | 54,123 | 89,667 | — |
| declare (T1) | 150,463 | 148,740 | 183,850 | — |

Two results. First, the Family C placement is quantified: O3 stores what O1 only logs (key bytes, attribute values), so the functions that write identity content cost three to four times more, and identity creation costs a deployment — about 4.3× O1. The spec's ERC-725 targets are missed on seven functions; the cause is architectural (external writes into a per-identity contract), so per FINDINGS rule 6 it is recorded, not optimised away. Second, and new: the governance layer's cost rose ~34K per write on O3 although its code is identical, because authorising *by DID* means resolving the controller through the option's read path, which on O3 is four cold external calls. Data placement in the identity layer is inherited by every layer that reads it (**F-O3-2**) — the per-function placement matrix in 01 §8 should carry an "authorisation read cost" column.

Remaining in WO-1: O4 ERC-725xy (adds ERC-735 claims and key purposes — the option expected to carry the highest native Set B coverage), O5 ERC-1155, O6 ERC-4337.

## Addendum G — O4 (ERC-725xy) ported: the native-claim path priced (2026-10-17)

`ClaimHolderAccount.sol` combines an ERC-725Y store, ERC-734 purpose keys (MANAGEMENT, ACTION, CLAIM, ENCRYPTION) and ERC-735 claims, written fresh from the drafts. `O4_ERC725xy.sol` deploys one per `createDID`; the controller is the MANAGEMENT key; verification methods are ERC-734 keys; delegates are ACTION keys with a 725Y expiry beside them (ERC-734 has none); and — the point of this option — **credentials are ERC-735 claims written on the subject's account**, read back with `getClaim` and revoked with `removeClaim`, with a registry index supplying the `validUntil` that ERC-735 lacks. Admitted **12/12 unmodified**; S1, S7, S8 run unchanged; suite **72 passing**.

| Function | O1 ERC-1056 | O2 ERC-721 | O3 ERC-725 | O4 ERC-725xy |
|---|---|---|---|---|
| createDID (first / next) | 178,935 / 161,835 | 185,326 / 168,226 | 764,090 / 746,978 | **1,633,094 / 1,615,982** |
| updateDID | 44,760 | 42,935 | 178,398 | 180,877 |
| deactivateDID | 55,127 | 53,280 | 92,675 | 95,120 |
| issueCredential | 130,163 | 128,393 | 142,377 | **308,310** |
| revokeCredential | 32,980 | 33,087 | 74,587 | 75,518 |
| createPresentation (1 cred.) | 62,441 | 60,729 | 79,084 | 72,625 |
| addVerificationMethod | 59,607 | 57,767 | 169,101 | 180,375 / 163,275 |
| removeVerificationMethod | 36,478 | 34,743 | 66,974 | 69,177 |
| addDelegate | 54,227 | 52,495 | 85,306 | 214,107 |
| registerIssuer (G1) | 76,800 | 75,326 | 111,002 | 111,474 |
| endorseIssuer (G2, root) | 151,449 | 149,975 | 185,519 | 185,991 |

The result the thesis needs from this option is now a number: the only EVM pattern with a *native* credential object costs 2.4× the anchor pattern per issuance and 2.3× per revocation, and buys a credential record that is queryable from the subject's own account without an indexer. Whether that is worth it is a placement decision, not a coverage one (01 §10): the claim is on-chain state, the anchor is an off-chain attestation with an on-chain residue. ERC-735's missing expiry and revocation state (**F-O4-3**) keep F5–F7 "assisted" rather than native, confirming the Set B coverage table in `ARCHITECTURE.md` §5 from measurement rather than inspection.

With four options the cross-option gas matrix (WO-5) can be generated from traces; O5 ERC-1155 and O6 ERC-4337 remain in WO-1.
