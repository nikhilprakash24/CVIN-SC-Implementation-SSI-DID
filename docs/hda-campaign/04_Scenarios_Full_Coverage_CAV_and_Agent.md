CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Full-Coverage Scenarios: One Vehicle, One Agent, Every Function and Every Object**

**Two end-to-end designs that exercise the complete operational surface of the identity system — the twelve minimal functions, the governance extension, the typing layer, and the agent trust layer — with the placement, cost, and failure consequence of each step stated**

Document 5 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · October 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose / Type B tables-data → Chapter 4, §4.4 (CAV scenario analysis); Chapter 5, §5.2 (I2I generalisation to agents)*

> **Build-state note (2026-10-04).** Unlike documents 01–03 and 06–09, this document was written *after* the VID layer of document 10 was executed, and it cites that document's measured figures directly rather than deferring to them. The two scenarios specified here, S9 and S10, are **designs and are not built**; they are written to be compared against the researcher's own independently drafted full-coverage scenarios, which is the comparison the brief §8 item 2 asks for. Canonical scenario identifiers are fixed in 00 §6.
>
> **Slice-1 note (2026-10-15).** Slice 1 of 00 §7 has since been completed (10 Addenda A and B). Three things this document described as unavailable now exist and the text below has been corrected inline where it said otherwise: the **on-chain Merkle inclusion verifier** (`BatchAnchorRegistry`, §2.6), the **Set C harness** (C1–C4, §2.7 and all of §3), and **trace timing instrumentation**. One new interface finding bears directly on this document's act V and act VI: **F-VID-11 — `ISetC` provides no way for a validator to answer a validation request**, so the C3→C4 sequences written below require an extension the interface does not contain (§2.7, open question 6). The Sybil result of 10 Addendum B §1e is the empirical counterpart to §2.8 and §3.8.

---

## 1. Purpose, and what "full coverage" is being claimed

### 1.1 Claim

A function-coverage matrix proves that a standard *can* do something; it does not prove that the something is useful, that the sequence in which a real deployment would need it is coherent, or that the objects the functions manipulate add up to a system a verifier can act on. The thesis's Stage 1 and Stage 2 instruments — the twelve-test compliance suite and the coverage matrix — answer the first question very well and are silent on the other three. This document closes that silence with the smallest instrument that can: two narratives, each of which touches every operation in the system exactly where a real deployment would touch it, and each of which names, for every datum it creates, where that datum lives.

The claim is specific and falsifiable. It is that **the complete operational surface of the identity system — twenty-three distinct operations across four layers — is exercised, in a coherent order, by two ordinary stories: the first year of a vehicle's life, and the working life of a fleet-operations agent and its sub-agents.** If that is true, then the surface is neither over-specified (there is no operation the stories never need) nor under-specified (there is no point in either story where the verifier must do something the surface cannot express). Both halves of that are checkable, and §6 checks them. The result is not entirely clean: four operations are exercised only by the agent story and not the vehicle story, two are exercised by neither in a way that earns their cost, and one — the composite typed verification T2 — turns out to be needed at almost every step, which was not obvious before the sequences were written out.

### 1.2 The operational surface

The system's surface is four layers deep. Only the first is normative.

| Layer | Operations | Status | Source |
|---|---|---|---|
| Minimal interface (normative) | F1 `createDID`, F2 `resolveDID`, F3 `updateDID`, F4 `deactivateDID`, F5 `issueCredential`, F6 `verifyCredential`, F7 `revokeCredential`, F8 `createPresentation`, F9 `addVerificationMethod`, F10 `removeVerificationMethod`, F11 `addDelegate`, F12 `validDelegate` | Specified, built on O1, 12/12 | `IMinimalSSI.sol`; 10 §4 |
| Governance extension | G0 `addRoot`/`removeRoot`, G1 `registerIssuer`, G2 `endorseIssuer`, G3 `revokeEndorsement`, G4 `isEndorsed` | Built and measured in this pass | `EndorsementRegistry.sol`; 10 §3.4, §5.2 |
| Typing layer | T1 `declare`, T2 `verifyTyped` | Built and measured | `TypedCredentialRegistry.sol`; 10 §3.2 |
| Agent trust layer (optional) | C1 `attestReputation`, C2 `getReputation`, C3 `requestValidation`, C4 `validationStatus` | Interface only; **not built** | `ISetC.sol`; 10 §7 |

Twenty-three operations if `removeRoot` is counted with `addRoot`. The reason the vehicle story alone cannot exercise all of them, and why this document needs two stories rather than one, is visible already in this table: Set C exists because an agent's trustworthiness is a running estimate from its behaviour, whereas a vehicle's is mostly a set of credentials from authorities. The 2020 CVIN paper's architecture [5] had no need of a reputation primitive; an agent marketplace cannot function without one. That asymmetry is the subject of §5 and the premise of 09.

### 1.3 The object inventory

The functions are the verbs; the following are the nouns. Every scenario step below is an operation on one of these, and the placement column is the commitment this suite's design makes about it (the full justification is 01 §1–§5; the design synthesis is 03 §2).

| # | Object | Created by | Lives | Why there |
|---|---|---|---|---|
| 1 | **Decentralised identifier (DID)** and its controller | F1 | On-chain state | Must be globally agreed and permanently attributable |
| 2 | **DID document** (verification methods, service endpoints, attributes) | F3, F9, F10 | On-chain state; read via F2 | The key material history *is* the accountability record (brief §2) |
| 3 | **Delegate grant** (type, address, expiry) | F11; read F12 | On-chain state | A verifier must be able to answer "may this key act for that DID" without the DID's cooperation |
| 4 | **Lifecycle flag** (deactivated) | F4 | On-chain state | Must be unforgeable and must not delete history |
| 5 | **Credential** (W3C VC, full content) | Off-chain builder (`lib/vid/credentials.js`) | **Off-chain signed** | Volume and personal-data character; measured at 813–850 bytes against a 32-byte anchor (10 §3.3) |
| 6 | **Credential anchor** (`credentialHash`, `validUntil`, issuer, subject) | F5 | On-chain anchor | Tamper-evidence and status without disclosure |
| 7 | **Revocation state** | F7 | On-chain state | The one credential fact a verifier cannot be told by the holder |
| 8 | **Presentation commitment** (holder, credential set, challenge, domain) | F8 | On-chain anchor | Replay protection and a non-repudiable record that a disclosure occurred |
| 9 | **Root of trust** | G0 | On-chain state | The governance boundary; deliberately not derivable |
| 10 | **Issuer role declaration** | G1 | On-chain state | Permissionless, confers nothing (10 §3.4) |
| 11 | **Endorsement** (endorser, issuer, type, expiry, transitivity) | G2, G3; read G4 | On-chain state | Entitlement is the question F6 does not answer (F-VID-7) |
| 12 | **Typed declaration** (type id, typed hash) | T1; read T2 | On-chain state, *optional* | Queryability without content, at 150,463 gas — the costliest per-credential choice in the system (10 §5.3) |
| 13 | **Reputation attestation** (score, attester, evidence URI) | C1; read C2 | On-chain state (sidechain) | Inherently linkable; must accrue to a stable identifier (06 §2.1) |
| 14 | **Validation request and status** | C3; read C4 | On-chain state; payload is a root | Independent checking with the trace off-chain |
| 15 | **Secure I2I channel** (ECDH, AEAD session) | Off-chain only | **Never on-chain** | 08 is its subject; its presence in a trace as `kind=offchain` is the demonstration |
| 16 | **Verifier cache** (fetched state, fetch height, staleness window) | Local | **Local only** | The staleness window is a measured security parameter, not an optimisation (F-VID-3) |
| 17 | **Batch root** (Merkle root over an event set) | F5 with the root as `credentialHash` | On-chain anchor | 11:1 measured against per-event anchoring (10 §5.3) |
| 18 | **Oracle attestation** (external fact, signed) | Off-chain, threshold-signed | Off-chain signed; root anchored | The 2020 paper's distributed-oracle stance [5] |

Eighteen object classes, of which exactly five hold on-chain state that grows with the number of *credentials* rather than the number of *principals*: anchors (6), revocation (7), presentation commitments (8), typed declarations (12), and reputation attestations (13). Those five are the scalability surface of the whole design, and every cost argument in 01 §7 and 03 §8 is ultimately about them.

### 1.4 What these scenarios are not

They are not the built scenarios. S7 and S8 were built and measured in this pass and cover the credential and endorsement machinery thoroughly (10 §3.3–§3.4); they do not cover key rotation under compromise, ownership transfer, reputation, or validation, and they have no agent half at all. S9 and S10 are the designs that would close that gap, written at the level of detail from which a build agent could produce `scenarios/run_cav_fullcoverage.js` and `scenarios/run_agent_fullcoverage.js` without further design decisions. Where a step's cost is given, it is arithmetic on a figure measured on option O1 in this pass, and is labelled as an estimate for O1 on a local Hardhat EVM — never as a measurement of S9 or S10.

---

## 2. S9 — A vehicle's first year

### 2.1 Claim

A vehicle's first year is the natural full-coverage test because it is the only period in which every category of identity event happens at least once: the vehicle is created, titled, paired with a driver, operated, serviced, damaged, assessed, re-titled, compromised, and — in the variant below — written off. A design that handles the first year handles the next fifteen, because the next fifteen are repetitions of acts III to VI. The narrative therefore doubles as the thesis's MOBI VID conformance argument (contribution C4) in operational form: MOBI VID I is act I, MOBI VID II is acts IV, V, and IX, and the registration and licence credentials that MOBI does not specify are acts II and III.

### 2.2 Dramatis personae

Fifteen DIDs, each created with F1. Costs below use the measured O1 range of 161,823–178,935 gas per `createDID` (10 §5.2); the spread is a function of storage warmth, not of the principal's kind.

| Label | Principal | Role in the governance graph |
|---|---|---|
| *M* | Transport ministry (provincial) | **Root** (G0). Endorses the registrar, inspection authority, insurer, police |
| *Ω<sub>OEM</sub>* | Manufacturer group | **Root** (G0). Endorses its own plants and, transitively, its authorised service network |
| *P* | Assembly plant | Issuer of `VID_BIRTH`; endorsed by *Ω<sub>OEM</sub>* |
| *R* | Provincial registrar (DMV) | Issuer of `VEHICLE_REGISTRATION` and `DRIVER_LICENCE`; endorsed by *M* |
| *I* | Inspection authority | Issuer of `EV_INSPECTION`; endorsed by *M* |
| *N* | Insurer | Issuer of `EV_INSURANCE_CLAIM`; endorsed by *M* |
| *L* | Police service | Issuer of `EV_THEFT_REPORT`, `EV_RECOVERY`; endorsed by *M* |
| *C* | Authorised service centre | Issuer of `EV_MAINTENANCE`, `EV_REPAIR`, `EV_MODIFICATION`; endorsed *by the OEM*, two hops from *Ω<sub>OEM</sub>* |
| *T* | Regional traffic authority | Reputation attester (C1); endorsed by *M* for `ROAD_REPORT_QUALITY` |
| *X* | Independent assessor | Validator (C3/C4); endorsed by *N* |
| *V* | **The vehicle** | Subject of the VID family; controller is initially *P*, then the owner |
| *O₁*, *O₂* | First and second owner (natural persons) | Subjects of nothing; *controllers* of *V* in turn |
| *D₁*, *D₂* | First and second driver | Subjects of `DRIVER_LICENCE` |
| — | *OBU*, *bay key*, *telematics key* | **Not DIDs.** Keys that act for *V* through F11 delegate grants and F9 verification methods |

The last row is the design decision that makes the rest work, and it is worth stating explicitly because it is the most common modelling error in vehicle-identity proposals. An on-board unit is not an identity; it is a *key that may act for* an identity, for a bounded time, in a bounded role. Modelling it as a DID would create a principal whose reputation, credentials, and history would have to be migrated every time the unit was replaced — and units are replaced. Modelling it as an F11 delegate (`sigAuth`, measured at 54,227 gas on O1) means that replacing it is one F10 and one F11, and that the vehicle's entire history survives untouched. The same argument applied to agents in §3 produces delegation *chains*, which is where the two scenarios diverge.

### 2.3 Act I — Manufacture: roots, entitlement, and a birth certificate

The chain is empty. Nothing can be verified, because there is nobody a verifier has a reason to believe.

1. The registry administrator declares the two roots: G0 `addRoot(M)`, G0 `addRoot(Ω_OEM)` — 47,604 gas each, measured. This is the only step in the entire year that is not itself authorised by something earlier in the graph, and it is therefore the step at which the system's trust is a political fact rather than a cryptographic one. Who may call `addRoot` is deployment governance and is deliberately unsolved in code (10 §3.4); the recommendation on file is a per-jurisdiction operator, which is the Local CVIN of the 2020 paper [5] (decision D6 in 00 §8).
2. F1 for *M*, *Ω<sub>OEM</sub>*, *P*, *R*, and *V*.
3. *P* declares itself: G1 `registerIssuer(P, OEM_PLANT)` — 76,800 gas, measured, and **confers nothing**. A verifier that stopped here would be trusting a self-declaration.
4. *Ω<sub>OEM</sub>* endorses it: G2 `endorseIssuer(Ω_OEM, P, VID_BIRTH, 10 years, transitive = false)` — 151,437 gas for the non-transitive form, measured. Entitlement now exists, is typed, and expires.
5. *P* builds the birth certificate off-chain: a W3C VC with `vinHash = keccak(VIN ‖ salt)`, make, model, model year, production date, plant code. The VIN itself never leaves the plant's records; the salt goes to the holder. Measured canonical size, 813 bytes (10 §3.3).
6. *P* anchors it: F5 `issueCredential(P, V, typedHash, validUntil = 0)` — 130,151 gas, measured, for the no-expiry form. The anchor is the *typed* hash `keccak(abi.encode(VID_BIRTH, schemaHash, contentHash))`, so the credential's type and schema are bound into the anchor at zero extra cost (10 §3.2).
7. *P* adds the vehicle's first verification method — the factory-installed OBU's public key: F9 `addVerificationMethod(V, keyType, pubkey)` — 59,595 gas, measured — and grants it authority to speak: F11 `addDelegate(V, sigAuth, obuAddress, validity)` — 54,227 gas, measured.

**The design point of act I.** A verifier presented with this vehicle tomorrow runs F6 (is the anchor live, unrevoked, unexpired, issuer active) and G4 (was the issuer entitled to issue *this type*). F6 alone is insufficient and the build proved it: finding F-VID-7 records that F5 is issuer-agnostic — anyone with a DID can anchor anything, and F6 will call it valid. The entire act I sequence exists to make G4 return true for a reason, and G4's cost is zero because it is a view. The endorsement that made it possible cost 151,437 gas once, for a plant that will issue hundreds of thousands of birth certificates; that is finding F-VID-4's amortisation argument in its natural setting.

**The archival problem, surfaced here and not solved.** F6 reports a credential invalid once its issuer DID is deactivated (finding F-VID-2). Plants close. A birth certificate must outlive its plant, so either *P* is a long-lived archival DID that is never deactivated, or verifier policy distinguishes "valid now" from "validly issued" by reading the `CredentialIssued` event and the endorsement record as of the issuance block. The second is correct and costs nothing extra, because events are permanent and the endorsement record carries `issuedAt`; it is recorded as decision D5 in 00 §8 because it is a policy the thesis must name, not a mechanism it must build.

### 2.4 Act II — Titling: the car ID, and the one credential worth typing on-chain

1. *M* endorses the registrar: G1 `registerIssuer(R, DMV)`, then G2 `endorseIssuer(M, R, VEHICLE_REGISTRATION, 5 years, false)` and again for `DRIVER_LICENCE`.
2. F1 for *O₁*. The owner's DID is created now and not earlier, and it is a *person's* DID with the same shape as everything else — which is the point of 07's argument that the system is not a vehicle system.
3. Control of the vehicle passes from plant to owner. The vehicle's controller is changed through the implementation's controller mechanism and the new controller is recorded in the DID document; the OBU delegate survives, because it was granted by *V*, not by *P*.
4. *R* issues the registration: 825 bytes off-chain (plate, jurisdiction, owner DID, validity, registrar DID), anchored with F5 `validUntil = expiry` — 150,087 gas, measured, for the with-expiry form. Finding F-VID-6 records the 19.9K-gas difference: an on-chain expiry costs a storage slot. It is worth paying here and almost nowhere else, because a registration must expire *against a non-cooperating holder*; a holder presenting a stale registration should fail even if the holder would rather not.
5. **T1 `declare`** — 150,463 gas, measured, the single most expensive per-credential operation in the system. This is the only credential in the entire year for which the on-chain typing path is recommended, and the reason is a specific third party: a police officer at the roadside who has the plate but not the credential. On-chain typing lets that officer discover *that a registration of this type exists and is current for this vehicle* without holding its content; off-chain typing cannot, because off-chain typing requires the content to recompute the hash. Every other credential in the year is consumed by a party that already holds it, so every other credential takes the free path. Stating the rule generally: **pay for on-chain typing exactly when the credential's consumer is someone who cannot have been given the credential in advance.**
6. *R* issues *D₁*'s licence: 850 bytes, with `birthYearCommitment` as a salted commitment — the hook for the age predicate of 02 §4 — anchored with F5 and expiry.

### 2.5 Act III — Operation: the Tier 2 loop, and the only functions that run at road speed

This act is where the identity system must not be in the way. Its latency budget is 100–500 ms (the C6 framework; see 05 §3), and its defining property is that **no on-chain write occurs inside it.**

1. The OBU opens an I2I channel to an RSU (08 §1: ECDH P-256, AES-256-GCM, `kind=offchain` in the trace, deliberately never on-chain).
2. The OBU presents. Off-chain: a verifiable presentation over the registration and, where the service requires a licensed driver, the licence, with selective disclosure (02) revealing vehicle class and validity and not plate or identity. On-chain, *optionally*: F8 `createPresentation` — 62,441 gas for one credential, 69,786 for two, measured. The optionality is the design decision. F8 buys a non-repudiable, replay-protected record that a disclosure occurred; it costs a transaction inside a window that cannot afford one. The resolution is in 03 §4.1 and is used throughout 05: **F8 is committed at Tier 3, after the fact, either per event on a Local CVIN sidechain or as one batched commitment per epoch on the backbone.** The Tier 2 decision is made from the off-chain presentation and the cache.
3. The verifier checks: F12 `validDelegate(V, sigAuth, obuAddress)` — is this key entitled to speak for this vehicle; F6 on the registration anchor; G4 on the registrar's entitlement; T2 `verifyTyped` as the composite that returns all of status, entitlement, and type binding in one view call. All four are views. All four cost nothing. All four can be served from cache.
4. And here is where the build's most uncomfortable measurement applies. Finding F-VID-3: a cached verifier **accepted a revoked registration** until it refreshed (trace S7 seq 50, `ok=true`; corrected at seq 51). The staleness window is not an engineering convenience; it is the security parameter of the entire Tier 2 read path, and every tier scenario in 05, every gated-access design in 06 §4, and the revocation-propagation crux in 08 are arguing about its size.

**Coverage note.** Act III exercises F2, F6, F8, F12, G4, T2 and nothing else. Six of the twenty-three operations carry the entire operational load of a vehicle's ordinary day, and five of the six are free. That ratio is the strongest single argument in the suite for the hybrid placement, and it is why 01 §4 treats read paths rather than write paths as the design's centre of gravity.

### 2.6 Act IV — Service history: transitive endorsement and the batching trade-off

1. *Ω<sub>OEM</sub>* endorses *C*, the service centre, for `EV_MAINTENANCE`, `EV_REPAIR`, and `EV_MODIFICATION`. To do so legitimately *Ω<sub>OEM</sub>* must itself hold a transitive endorsement for those types, so the chain is *M* → *Ω<sub>OEM</sub>* (transitive, 171,373 gas measured — the extra 20K over the non-transitive form is the one storage slot for the flag) → *C* (non-transitive, 182,800 gas measured for the non-root endorser form). Two hops, depth-bounded at three by the registry. This mirrors how an authorised service network is actually constituted, which is the point: the governance graph is not an abstraction over the industry, it is a transcription of it.
2. A service visit grants the bay a temporary key: F11 `addDelegate(V, sigAuth, bayKey, 4 hours)`. It expires by itself. No revocation transaction is needed, and this is the cheapest safe pattern in the whole system — a grant whose expiry does the work that a revocation would otherwise have to do.
3. Each service event is a credential: odometer, work performed, parts, technician. Odometer monotonicity is checked *off-chain* against the previous event, because the chain holds no odometer and should not.
4. Anchoring: the choice the build measured. Eleven lifecycle events anchored individually cost 1,431,745 gas; the same eleven under one Merkle root cost 130,151 — a ratio of 11:1, exactly the batch size, because the anchor write is constant in the number of leaves (10 §5.3, finding F-VID-5). What is lost is per-event on-chain status and revocation. The rule that follows, and which this act applies, is that **append-only history batches and revocable entitlement does not.** Maintenance and inspection records batch. Registration and licence do not.
5. One consequence worth naming: a batched event's per-event verifiability is recovered off-chain by a four-hash inclusion proof against the anchored root, and *on*-chain by a Merkle verifier. **Slice 1 built it** (`BatchAnchorRegistry`, scenario S17, 10 Addendum A §1): a purpose-built `anchorBatch` costs 122,139 gas against 130,163 for the same root pushed through F5, and it recovers on-chain inclusion as a **gas-free view** with a 128-byte proof, with whole-batch revocation at 55,267. So the act IV choice is now three-way rather than two-way, and the third option dominates: 11.72:1 against per-event anchoring, with on-chain inclusion retained. The measured surprise is that the purpose-built anchor is only about **6% cheaper** than reusing F5, not half the price, because new storage slots dominate either way — which settles an open estimate in 01 §7 that had guessed 60,000 (finding F-VID-8).

### 2.7 Act V — Damage, assessment, and the validation primitive

1. A collision produces an `EV_ACCIDENT` credential issued by *L* and an insurance claim. The claim needs several credentials at once, so the owner's wallet builds a multi-credential presentation: F8 over the registration, the accident record, and the relevant service history — 69,786 gas measured for two credentials, so three is an extrapolation and is labelled as one.
2. *N* wants the damage assessed by someone who is not the claimant and not itself: C3 `requestValidation(V, DAMAGE_ASSESSMENT, root)`, where `root` is the Merkle root of the evidence bundle (photographs, sensor logs, the repair estimate) and **not the bundle**. The payload is `bytes calldata` and its size is under the caller's control; the design rule from 06 §2.3 applies unchanged — the payload is a root and a URI, never the content.
3. *X* assesses off-chain and the result is read with C4 `validationStatus(requestId)`.
4. *N* issues `EV_INSURANCE_CLAIM` with F5.

**The gap, now partly closed — and one new hole.** When this document was drafted, C1–C4 were interface only. Slice 1 step 1d built a **harness** (`contracts/harness/SetCHarness.sol`, 10 Addendum B), so C1–C4 now execute: `attestReputation` measures 83,493 gas for a repeat attester and 117,693 for the first attestation of a subject. Those are **harness figures and must not be cited as ERC-8004 costs** — there is no agent NFT and no ERC-8004 fidelity — so the agent half of §3 is unblocked for demonstration but not for cost comparison against O7.

The harness also found something this act had assumed away. **Finding F-VID-11: `ISetC` provides no way for a validator to answer a validation request.** C3 `requestValidation` raises one and C4 `validationStatus` reads a status, but no function lets *X* write the assessment that C4 would report; the harness had to add `resolveValidationAs` to make the sequence run at all. Step 3 of this act as written — "*X* assesses off-chain and the result is read with C4" — therefore describes something the twelve functions plus `ISetC` cannot express. This is the third interface-level finding of the same kind as F-VID-1 and F-VID-7, and it is a candidate for `ISetC` v1.1 (open question 6). The harness's gating choice is the other half of the story: an attester must hold a `REPUTATION_ATTESTER` endorsement before it may score, which is the mechanism act VI's Sybil resistance depends on and which 10 Addendum B §1e measures.

### 2.8 Act VI — Reputation: the vehicle earns something no authority gave it

Through the year the vehicle has been reporting road conditions — ice, potholes, obstructions — under rotating pseudonyms. At each epoch close the traffic authority scores the contributions and C1 `attestReputation(V, score, evidenceURI)` accrues the score to the vehicle's verinym, with the evidence URI pointing at the Merkle root of that epoch's report bundle. The mechanism, the dual-mode pseudonym/verinym split that keeps the reports unlinkable while the score is linkable, the ZK link proof that binds them at scoring time, and the honest statement of what breaks it (small anonymity sets at rural RSUs) are all set out in 06 §2.2 and are not repeated here.

What act VI adds is the *consumption* side, which 06 does not cover: the insurer *N*, at renewal, reads C2 `getReputation(V)` and prices accordingly. This is the first point in the vehicle's year at which a commercial decision is made from evidence that no authority issued — not a credential from a ministry but an aggregate of observed behaviour. It is also the first point at which the vehicle has an incentive to lie that no credential check can detect, because the lie is not in a claim, it is in the behaviour. That is precisely the problem reputation exists to price, and the full argument — that collective computation needs reputation, that reputation needs identity, and that identity needs this system — is 09.

### 2.9 Act VII — Ownership transfer: the hardest ordinary operation

Transfer is where identity systems quietly fail, because four things must change atomically in a system that has no atomicity across layers.

1. *R* revokes the old registration: F7 `revokeCredential` — 32,968 gas, measured, idempotent and irreversible.
2. F1 for *O₂*. Control of *V* passes to *O₂*.
3. *R* issues a new registration to the new owner, with T1 `declare` again for roadside discoverability.
4. Keys: the previous owner's personal key is removed with F10 `removeVerificationMethod` — 36,454 gas, measured — and the new owner's added with F9. The interface guarantees that F10 can never remove the last key, which is what prevents a transfer from bricking the vehicle's identity.
5. `EV_REGISTRATION` lifecycle event anchored; the service history is *not* reissued, and this is the point of the act. The history belongs to the vehicle, is anchored under the vehicle's DID, and transfers with it without a single additional write. A used-car buyer verifies eleven years of maintenance with eleven inclusion proofs against anchors the seller never controlled.

**The non-atomicity, stated plainly.** Between step 1 and step 3 the vehicle is unregistered. A verifier that reads the chain in that interval correctly refuses it. Whether that interval is a block or a week is an administrative fact, not a cryptographic one, and no amount of design removes it; what the design can do is make the interval visible — both the revocation and the new anchor are timestamped events — so that a dispute about "was it registered on the 14th" is answerable. 03 §3.3's reconciliation rules give the holder's wallet the corresponding duty: a wallet that has seen the F7 must stop presenting the credential even if the Tier 2 verifier's cache has not yet caught up.

### 2.10 Act VIII — Compromise: what rotation does and does not save

The OBU is extracted and its key cloned. Three operations in sequence: F10 removes the compromised verification method; F11's grant is allowed to expire or, if it must end now, the delegate grant is overwritten by a zero-validity re-grant (the registry pattern on O1); F9 adds the replacement unit's key and F11 re-grants.

What survives: the vehicle's DID, every credential anchored to it, every service record, and the reputation on its verinym. None of those were bound to the compromised key. What does not survive: anything the attacker signed before removal, which remains validly signed and permanently attributable to a key that was authorised at the time. The chain's record makes the compromise *visible and bounded* — the window is exactly from the last pre-compromise event to the F10 block — and this is the forensic-audit primitive of the Building Paths preface in its sharpest form: the design does not prevent the attack, it makes the attack's extent provable. The accountability-gap argument of Chapter 1 is this paragraph.

Where the service centre, not the vehicle, is at fault — a bay that issued false maintenance records — the remedy is G3 `revokeEndorsement` — 55,597 gas, measured. The build measured the consequence precisely (trace S7 seq 53): after endorsement revocation, **F6 status remains valid while entitlement is false.** The credentials the bay issued are not retroactively invalid; they are retroactively *unentitled*, and a verifier that checks only F6 will accept them. Any verifier that cares must check G4. This is the single most important operational consequence of the endorsement design and the reason 11 §2 argues the pattern belongs in the thesis rather than in an appendix.

### 2.11 Act IX — Recall, theft, recovery

A manufacturer recall is an `EV_RECALL` credential issued by *Ω<sub>OEM</sub>* to the affected vehicles and closed by a service event that references it; the closure is checkable because both are anchored and the service credential cites the recall's credential ID. Theft is `EV_THEFT_REPORT` by *L*, which a verifier treats as a policy flag rather than a revocation — the vehicle's registration is still valid, which is exactly what makes the theft report necessary as a separate typed credential. Recovery is `EV_RECOVERY`, and the pair forms a chain that the build exercised in S8.

### 2.12 Act X — End of life

F7 sweeps the revocable credentials (registration; the licence is the driver's and is untouched). The decommission event is anchored. F4 `deactivateDID(V)` — 55,127 gas, measured — is irreversible, and the vehicle's DID **remains resolvable with the deactivated flag set** (trace S8 seq 68). That property is not a nicety: a salvage dispute, a parts-provenance query, or a liability claim three years later all require the history to resolve. A design that deleted the DID would destroy the evidence that justified building the system.

### 2.13 Coverage ledger for S9

| Op | Where exercised | Op | Where exercised |
|---|---|---|---|
| F1 | Acts I, II, VII | G0 | Act I |
| F2 | Act III (and every verification) | G1 | Acts I, II, IV |
| F3 | Act II (service endpoint), VII | G2 | Acts I, II, IV (transitive chain) |
| F4 | Act X | G3 | Act VIII |
| F5 | Acts I, II, IV, V, IX | G4 | Act III (and every verification) |
| F6 | Act III (and every verification) | T1 | Acts II, VII (registration only) |
| F7 | Acts VII, X | T2 | Act III (and every verification) |
| F8 | Acts III, V, VI | C1 | Act VI |
| F9 | Acts I, VII, VIII | C2 | Act VI |
| F10 | Acts VII, VIII | C3 | Act V |
| F11 | Acts I, IV, VIII | C4 | Act V |
| F12 | Act III | `removeRoot` | **Not exercised** |

Twenty-two of twenty-three. `removeRoot` is not exercised because a root's removal is a governance event on the scale of a jurisdiction, not of a vehicle; it belongs in the governance scenario that 07 §8 sketches, and its absence here is a finding about the scenario, not about the system.

### 2.14 Placement ledger

| Datum | Placement | Volume driver |
|---|---|---|
| 15 DIDs, their keys, delegates, flags | On-chain state | Principals (bounded) |
| 2 roots, 6 issuer roles, 8 endorsements | On-chain state | Institutions (bounded, amortised) |
| ~20 credential anchors (3 minimal + lifecycle + batch roots) | On-chain anchor | Credentials (the growth surface) |
| 2 typed declarations | On-chain state | **Chosen**, not forced |
| 1 revocation + end-of-life sweep | On-chain state | Revocable credentials only |
| ~4 presentation commitments | On-chain anchor | Batched at Tier 3 |
| 1 reputation attestation per epoch | On-chain state, sidechain | Epochs, not reports |
| Every credential body, report, receipt, photograph, sensor log, assessment, channel | **Off-chain signed** | Unbounded, and therefore necessarily off-chain |
| Every verifier's view of the above | **Cached**, with a declared window | — |

### 2.15 Failure modes

*Impersonation* fails at F12: an unauthorised key cannot act for *V*. *Mis-issuance* is caught by G4, not F6 — the central operational lesson of act VIII. *Replay* of a presentation reverts on the challenge check (trace S7 seq 45). *Stale acceptance* is real and bounded only by the cache window (F-VID-3). *Key compromise* is bounded and visible but not retroactively undone (act VIII). *Chain reorganisation* after an anchor leaves the credential still validly signed off-chain; the anchor is resubmitted, and the wallet treats an anchor as final only after the finality depth 03 declares. *Supply-chain compromise* at the plant is the one failure the design does not bound: a compromised plant key issues birth certificates that are valid and entitled, and the only remedies are G3 and the forensic trail — which is an honest limit and is stated as one in 03 §6.

### 2.16 Problems solved, and further functionality

The year as written already solves the thesis's motivating problem: "what is the history of actions taken by vehicle V?" is answerable, because every act left an attributable anchor, while routine roadside disclosure revealed only vehicle class. SCMS cannot answer it, and that is the accountability gap of Chapter 1.

Four extensions attach without new primitives. **Toll payment and pay-as-you-use roads**: act III's presentation becomes a payment authorisation and act IV's batching becomes the settlement root; 06 §3 has the design, and the only new object is the receipt. **Road and traffic condition reporting**: act VI is already the pipeline, and its reports are the input. **Federated learning**: a model update is a report of a different type, the reputation of act VI weights it, and the endorsement of act I is what makes a Sybil expensive; 09 is the argument. **Used-vehicle market efficiency**: act IV's batched history plus act VII's costless transfer of that history is, economically, the largest single consequence of the design and the one a non-technical committee member will find most immediately persuasive.

### 2.17 Demonstration hook

Proposed script `scenarios/run_cav_fullcoverage.js` (S9). Assertions: (a) the trace contains at least one entry for each of the twenty-two tags of §2.13, verified by a tag-set assertion rather than by eye; (b) between the act III channel-open `offchain` entry and the authorisation decision there is **no** `kind=tx` entry; (c) the act VII sequence contains F7 before the replacement F5, and an F2 read between them returns a resolvable DID with no current registration; (d) after the act VIII F10, a signature from the removed key fails F12; (e) after the act VIII G3, F6 on a credential issued by *C* returns valid while G4 returns false — the S7 seq 53 property, reasserted in the ownership context; (f) total gas is reported split three ways, into principal setup, governance, and per-credential cost, because the thesis's cost claim is about the third only. Metrics: on-chain gas per act; the ratio of `offchain` to `tx` entries over the whole year; the number of chain reads required for the act III decision, which should be zero from a warm cache.

---

## 3. S10 — A fleet-operations agent and its sub-agents

### 3.1 Claim

The agent story is not the vehicle story with the nouns changed, and the interesting part of this document is exactly where it stops being so. Three differences are structural rather than cosmetic. First, agents *spawn*: a principal delegates to an agent, which delegates to sub-agents, and the authority must *attenuate* down the chain — which turns F11's flat delegate grant into a chain whose composition is a security property nobody has specified. Second, an agent's trustworthiness is a running estimate from behaviour rather than a set of credentials from authorities, which is why Set C exists at all. Third, an agent's lifecycle is measured in hours where a vehicle's is measured in years, so operations the vehicle performs once — creation, key rotation, retirement — the agent performs continuously, and their cost moves from negligible to dominant.

The claim is that **the same twenty-three operations cover the agent case, that the three differences are accommodated by composition rather than by new primitives, and that one of them — attenuation — is accommodated only by a convention the interface does not enforce.** The last clause is a finding, and it is this document's contribution to the C14 agent-wrapper line of work.

### 3.2 Dramatis personae

| Label | Principal | Role |
|---|---|---|
| *Γ* | Industry consortium | **Root** (G0) for agent-capability credential types |
| *Z* | Capability certifier | Issuer of `AGENT_CAPABILITY`; endorsed by *Γ* |
| *O* | Fleet operator (legal entity) | The **principal**; holder of a `LEGAL_ENTITY` credential (07 §4); controller of the agent |
| *A* | Fleet-operations agent | An account-abstraction principal (ERC-4337 pattern, contribution C14) with its own DID |
| *A₁* | Maintenance-scheduling sub-agent | Delegate of *A*, narrower scope, shorter life |
| *A₂* | Route-optimisation sub-agent | Delegate of *A* |
| *K* | Agent marketplace / registry | ERC-8004-derived (O7 pattern) [19]; endorses validators |
| *S* | Telematics data service (tool provider) | Counterparty; gates access on presentation |
| *X<sub>A</sub>* | Validator agent | C3/C4 validation; endorsed by *K* |
| *V₁…Vₙ* | The fleet's vehicles | The S9 principals — this is where the two stories join |

Six credential types are needed that `CredentialTypes.sol` does not define: `LEGAL_ENTITY`, `AGENT_CAPABILITY`, `DELEGATION_SCOPE`, `SPENDING_MANDATE`, `TASK_ASSIGNMENT`, `TASK_OUTCOME`. They are **proposed, not built**; adding them is a one-line-per-type change to the library and costs nothing, because the typed-anchor rule is generic over the type identifier. That the vehicle vocabulary extends to agents by adding constants to a library — and not by touching the interface — is itself the C14 argument in miniature.

### 3.3 Act I — The principal, and why the agent is never the root of its own authority

1. G0 `addRoot(Γ)`. F1 for *Γ*, *Z*, *O*, *K*.
2. *O* obtains a `LEGAL_ENTITY` credential from a corporate registry — the same structure as a vehicle registration, a different registry, and the subject of 07 §4.
3. F1 for *A*. The agent exists.
4. **The binding step.** *O* grants F11 `addDelegate(O, sigAuth, A_account, validity)`. The agent acts *as a delegate of its principal*, not as a free-floating identity. Every counterparty check in the rest of the story begins with F12 `validDelegate(O, sigAuth, A_account)`, and this is the confused-deputy guard: an agent that has been tricked into acting outside its mandate is still an agent whose every action is attributable to a principal with legal personality, assets, and a reputation to lose. A design in which the agent is its own root has no such anchor, and the whitewashing attack of 06 §2.3 becomes free.
5. Grant validity is the control. A delegation with a 30-day validity is a 30-day liability; the operator renews deliberately. Expiry doing the work of revocation is the same cheap-safe pattern as the service bay in S9 act IV, and for agents it is not a nicety but the primary control, because agents are numerous and revocation transactions are not free.

### 3.4 Act II — Capability certification, and the second credential worth typing on-chain

1. G1 `registerIssuer(Z, CERTIFIER)`; G2 `endorseIssuer(Γ, Z, AGENT_CAPABILITY, 2 years, false)`.
2. *Z* evaluates *A* — against what, and how, is an open research question this document does not pretend to answer; the design assumption is an off-chain conformance process whose report is the credential's evidence — and issues `AGENT_CAPABILITY` to *A*: capability classes, evaluation date, evaluation report digest, validity. F5 with expiry.
3. **T1 `declare`.** This is the second and last credential in either story for which on-chain typing earns its 150,463 gas, and for the same reason as the vehicle registration: the consumer is a party who cannot have been given the credential in advance. A marketplace or a counterparty discovering *A* for the first time needs to learn that a current capability credential of this type exists before any channel is opened. The rule of §2.4 holds in both stories, which is weak evidence that it is the right rule.
4. *A* publishes a service endpoint with F3 `updateDID` — 44,760 gas, measured — pointing at its capability manifest, following the ERC-8004 `tokenURI`-to-capability-JSON pattern [19].

### 3.5 Act III — Sub-agents, and the attenuation finding

The operator's agent spawns two sub-agents. *A₁* may read maintenance schedules and book service slots; *A₂* may read telemetry and compute routes. Neither may spend money. Neither may act for the fleet's vehicles.

1. F1 for *A₁*, *A₂*. F9 adds each one's key.
2. F11 `addDelegate(A, sigAuth, A₁_account, 7 days)` and likewise for *A₂*.
3. A `DELEGATION_SCOPE` credential is issued by *A* to each sub-agent, off-chain, stating the permitted operations, counterparties, and limits, anchored with F5.

**The finding.** F11's delegate grant is a *type and an expiry*, and nothing else. The interface has no notion of a scope, no notion of attenuation, and no notion of depth: *A₁* holding a `sigAuth` grant from *A* can, as far as the interface is concerned, grant `sigAuth` to *A₃*, and a verifier walking the chain cannot tell from on-chain state alone that *A₃*'s authority ought to be narrower than *A*'s. The scope lives in an off-chain credential that a verifier must know to ask for.

Three responses, and the design chooses the third.

- *Change the interface* to carry a scope and a depth bound. Forbidden: the interface is normative (brief §9 rule 2), and rightly so — a scope language is a policy question that would be frozen into a specification whose whole value is minimality.
- *Rely on the off-chain scope credential alone.* Insufficient: a verifier that forgets to ask for it sees a valid delegate chain and accepts.
- **Compose, by analogy with endorsement.** The `EndorsementRegistry` already solved this exact problem for issuers: it is typed, time-bounded, depth-bounded at three, and it requires every intermediate link to be explicitly marked transitive before a chain is honoured. A `DelegationRegistry` beside the interface, with the same shape — typed scopes, expiry, explicit transitivity, `MAX_DEPTH` — gives a verifier one view call that answers "may this key perform this operation for that principal, through a chain no deeper than three, every link of which was marked as permitting further delegation". It needs no interface change, it reuses a pattern that has been built and measured, and its cost profile would be the measured G-series profile: expensive per grant, amortised per use, free to read.

This is the strongest argument in this document and it is an argument the vehicle story could not have produced, because vehicles do not spawn. It is offered as a thesis contribution candidate in §5 and as an open question in the closing section.

### 3.6 Act IV — Engagement: the Tier 2 loop for agents

*A₂* needs telemetry from *S*. The budget is the agent's action loop, which is 05 §3.2's subject.

1. Channel to *S* (08).
2. *S* verifies, all from cache, all free: F12 on the *O*→*A* grant; F12 on the *A*→*A₂* grant; F6 on the `AGENT_CAPABILITY` anchor; G4 on *Z*'s entitlement; T2 as the composite; C2 `getReputation(A)` against the service's threshold.
3. *A₂* presents: off-chain VP over the capability and scope credentials with selective disclosure; F8 committed later, at Tier 3, batched.
4. *S* serves the data.

The shape is identical to S9 act III, with one addition and one subtraction. The addition is C2: a vehicle is admitted on its credentials, an agent on its credentials *and its history*. The subtraction is that nothing here is physically urgent — a 400 ms delay inconveniences an agent and endangers nobody — which is why 05 argues that the agent tiers are shaped by throughput and cost rather than by safety.

### 3.7 Act V — Spending: the mandate and the predicate

*A* must pay *S* for metered access. `SPENDING_MANDATE` is issued by *O* to *A*: ceiling, permitted counterparties, validity, off-chain, anchored. At each request *A* proves a predicate — requested amount plus spent-to-date does not exceed the ceiling — against the mandate and its own signed spend ledger. The identity system authorises and receipts; it does not move value; the rail is independent. 06 §3.3 has the design and the three rails; the point here is only that the mandate is a credential like any other, that its ceiling is enforced by a proof rather than by a contract, and that *O* can revoke it with one F7 at 32,968 gas.

### 3.8 Act VI — Outcome, validation, reputation

*A₁* books a service slot for *V₇* — and here the two stories join, because *A₁* must present a credential proving it may act for the fleet operator who owns *V₇*, and the service centre *C* of S9 act IV is the counterparty. The booking produces a `TASK_OUTCOME` credential whose evidence is the root of *A₁*'s signed execution trace (the memo stance: agents "leave signed execution traces"). *A* raises C3 `requestValidation(A₁, TASK_OUTCOME, traceRoot)`; *X<sub>A</sub>* evaluates; C4 reads the status; *K* or the counterparty calls C1 `attestReputation(A₁, score, evidenceURI → traceRoot)`; future counterparties read C2.

The agent's actions are themselves the evidence, which is the deepest difference from the vehicle case. A vehicle's reputation is built from reports *about the world*; an agent's is built from records *of itself*. That makes agent reputation cheaper to produce and easier to fake, and it is why the validation primitive C3/C4 — an independent check before scoring — is load-bearing for agents and optional for vehicles.

### 3.9 Act VII — Compromise and retirement

*A₂* is compromised through a prompt-injection path (the failure mode has no analogue in the vehicle story and no cryptographic remedy). Containment is the delegation structure: F10 removes *A₂*'s key; the *A*→*A₂* grant is expired or overwritten; F7 revokes its scope credential; the damage is bounded by the scope that *A₂* held, which is the whole reason for attenuation. If *Z* certified a capability class that was systematically unsafe, G3 revokes *Z*'s endorsement and every capability credential it issued becomes F6-valid and G4-unentitled — the S7 seq 53 property again, now at consortium scale.

Retirement is routine: F4 `deactivateDID(A₂)`, irreversible, still resolvable. Agents are retired constantly, and at 55,127 gas measured per deactivation a fleet that spawns a thousand short-lived sub-agents a day cannot afford to deactivate them on a backbone chain. The design consequence is sharp and is the agent case's distinctive cost finding: **ephemeral agents must not get DIDs.** They get delegate grants with short validity under a persistent agent's DID, and they expire. A DID is for a principal whose history must outlive it. This is the same lesson as the OBU in §2.2, discovered independently from the opposite direction, and it generalises: *create an identity only for something that accrues history; use a delegate for everything that merely acts.*

### 3.10 Coverage ledger for S10

| Op | Where | Op | Where |
|---|---|---|---|
| F1 | Acts I, II, III | G0 | Act I |
| F2 | Act IV | G1 | Act II |
| F3 | Act II (service endpoint) | G2 | Act II |
| F4 | Act VII | G3 | Act VII |
| F5 | Acts I, II, III, V, VI | G4 | Act IV |
| F6 | Act IV | T1 | Act II |
| F7 | Acts V, VII | T2 | Act IV |
| F8 | Act IV | C1 | Act VI |
| F9 | Acts I, III, VII | C2 | Acts IV, VI |
| F10 | Act VII | C3 | Act VI |
| F11 | Acts I, III | C4 | Act VI |
| F12 | Act IV (twice, chained) | `removeRoot` | **Not exercised** |

Twenty-two of twenty-three again, and the same one missing. Taken together the two stories leave `removeRoot` as the only operation in the system that no ordinary operational narrative needs — which is the correct result for a governance primitive, and a useful one: it tells the thesis that the governance layer has exactly one operation whose justification must be institutional rather than operational.

### 3.11 Failure modes specific to agents

*Whitewashing*: discard *A*, create *A′*. Defended by the *O*-rooted delegation — *O*'s delegations are on-chain and dated, so a verifier policy can require a minimum delegation age or read the principal's aggregate across delegates. *Collusion rings*: agents attest each other. Defended off-chain by weighting attestations by the attester's own endorsement and reputation (EigenTrust-style transitive weighting), computed from on-chain events, which keeps C1 cheap and the weighting revisable without a contract upgrade. *Confused deputy*: handled by scope, and only properly by the registry of §3.5. *Prompt injection and goal corruption*: **not an identity problem and not solved here.** The identity system's contribution is that the corrupted agent's every action is signed, scoped, bounded, and attributable to a principal — operational transparency rather than algorithmic transparency, exactly as the Building Paths preface frames it for agents. Saying so plainly is better than implying that a credential system defends against a model-level attack.

### 3.12 Problems solved, and further functionality

The agent story's immediate yield is that a counterparty can admit an unknown agent on evidence rather than on an API key: capability certified by an endorsed certifier, scope bounded by an attenuated delegation chain, spending bounded by a mandate, history visible as reputation, every action attributable to a legal person. That is the C14 wrapper's purpose stated operationally, and it is the same machinery the vehicle uses.

Extensions: **tolling and pay-as-you-use roads** become agent-mediated, with *A* holding the mandate and the vehicles presenting under it; **road and traffic reporting** becomes an agent market in which *A₂*'s route optimisation both consumes reports and produces them, with reputation on both sides; **federated learning** is the same loop with the task being a training round and the outcome a model update — the marketplace *is* the coordinator, the validator *is* the robust aggregator, and the reputation *is* the aggregation weight. 09 makes that identification its spine, and this act is the evidence that it is an identification and not an analogy.

### 3.13 Demonstration hook

Proposed script `scenarios/run_agent_fullcoverage.js` (S10). **No longer blocked**: the `ISetC` harness of Slice 1 step 1d supplies C1–C4 (and `resolveValidationAs` for the C3→C4 answer path of F-VID-11), and `run_fl_round.js` already demonstrates the C1/C2/C3/C4 sequence end to end, so S10 is buildable today against the existing sandbox. Assertions: (a) the tag set of §3.10; (b) the chained F12 in act IV — two `view` entries, *O*→*A* and *A*→*A₂*, both true, with a third assertion that removing the *O*→*A* grant makes the *A*→*A₂* check insufficient, which is the attenuation finding made executable; (c) a sub-agent acting outside its `DELEGATION_SCOPE` is rejected by the verifier's policy check while F12 still returns true — the gap of §3.5, demonstrated rather than argued; (d) C3 precedes C1 for every outcome; (e) after act VII's G3, F6 valid and G4 false on a capability credential. Metrics: gas per sub-agent lifecycle (the figure that decides whether ephemeral agents may have DIDs — on the measured F1 and F4 costs it is already decisive, and the assertion is there to make it undeniable); number of chain reads for the act IV decision from a warm cache, which should be zero.

---

## 4. What the two scenarios together establish

| Property | Vehicle (S9) | Agent (S10) | Consequence |
|---|---|---|---|
| Principal lifetime | 15 years | hours to months | Deactivation cost is negligible for vehicles, dominant for agents |
| Delegation shape | Flat: one OBU, one bay key | **Chained and attenuating** | F11 is sufficient for S9 and insufficient for S10 (§3.5) |
| Trust basis | Credentials from authorities | Credentials *and* behavioural history | Set C is optional for S9, load-bearing for S10 |
| Evidence origin | Reports about the world | Records of itself | Agent reputation is cheaper to produce, easier to fake, needs C3 |
| Urgency of the Tier 2 loop | Physical safety | Throughput and cost | 05 treats the two tier families differently for this reason |
| Who bears liability | Owner, by registration | Principal, by delegation | Both are credentials; the agent's is the newer idea |
| The costly choice | T1 on the registration | T1 on the capability credential | Same rule, independently derived (§2.4, §3.4) |

Three results follow that neither story would have produced alone.

**The identity-versus-delegate rule.** Create a DID for what accrues history; use a delegate for what merely acts. Derived in §2.2 from the OBU's replaceability and in §3.9 from the ephemeral agent's cost, and decisive in both.

**Attenuation is missing and composable.** The interface's delegate grant carries a type and an expiry, not a scope or a depth. The gap is real, it bites only when principals spawn, and it is closable by a registry beside the interface with the shape the endorsement registry already has and the cost profile the build already measured. This is this document's candidate contribution, and it is a contribution of the *same kind* as the endorsement argument of 11 §2 — which strengthens both, because it means the "extend beside, never inside" method has now produced two results rather than one.

**T2 is needed almost everywhere.** The composite typed verification appears in every verification step of both stories, because every verification needs status *and* entitlement *and* type binding, and F6 gives only the first. This was not obvious before the sequences were written out: T2 was built as a convenience for the VID layer, and it turns out to be the system's actual verification primitive. Whether the specification should say so — whether the twelve functions' verification story is incomplete without a composite — is a question for spec v1.1 and is related to, but distinct from, finding F-VID-1.

## 5. Consolidated coverage and what cannot be exercised today

| Layer | Exercised by S9 | Exercised by S10 | Buildable today |
|---|---|---|---|
| F1–F12 | All twelve | All twelve | Yes — built and measured on O1 |
| G0–G4 | All five (`removeRoot` excepted) | All five (`removeRoot` excepted) | Yes — built and measured |
| T1, T2 | Both | Both | Yes — built and measured |
| C1–C4 | All four | All four | **Yes, on a harness** (Slice 1 step 1d) — exercises the sequence; **not** a source of ERC-8004 costs, and C3→C4 needs the F-VID-11 extension |
| Attenuated delegation | n/a | Needed; not available | **No** — needs the registry of §3.5. The one remaining blocker |
| Merkle inclusion on-chain | Act IV batching | — | **Yes** (`BatchAnchorRegistry`, S17, Slice 1 step 1b) |
| Any latency figure | — | — | Instrumented (`latencyMs`, schema v1.1) but **Hardhat values are a lower bound, not results**; needs Besu, then hardware |

When this document was drafted it said that roughly four-fifths of the two scenarios could be built against the existing sandbox, with the remaining fifth blocked on three small pieces of work — a Set C harness, a Merkle verifier, and a delegation registry. **Slice 1 built the first two.** Both scenarios are now buildable end to end with one exception: the attenuated-delegation registry of §3.5, which is the only structural gap left in either story and which is not in any slice plan because this document is where it was first identified. That it is the sole survivor of the three is mild corroboration that it is a real finding rather than an artefact of how S10 was written.

---

## Sources used in this document

| Id | Source | Verification state | How used |
|---|---|---|---|
| — | `_CONTEXT_BRIEF.md` §3, §7, §8, §9 | VERIFIED AT SOURCE | Operation inventory, writing rules, coverage checklist |
| — | HDA 10 §3–§6 and the four committed traces | VERIFIED AT SOURCE | Every gas figure and every finding cited |
| — | `IMinimalSSI.sol`, `ISetC.sol`, `EndorsementRegistry.sol`, `TypedCredentialRegistry.sol`, `CredentialTypes.sol` | VERIFIED AT SOURCE (read in this pass) | Operation semantics, delegate-grant shape, depth bound |
| — | HDA 01 §4–§5, 03 §2–§4, 06 §2–§4, 08 §1, 09 | VERIFIED AT SOURCE for the claims cross-referenced | Placement, tiers, reputation mechanics, channel — pointed to, not duplicated |
| [5] | Prakash, Michelson, Feng, CVIN, IEEE VTC2020-Spring | VERIFIED AT SOURCE | Local CVIN governance, distributed oracles, dual-mode identity |
| [19] | De Rossi et al., ERC-8004 Trustless Agents | DIGEST-LEVEL | Set C derivation; capability-manifest endpoint pattern |
| [24] | ERC-4337 | DIGEST-LEVEL | Agent as account-abstraction principal (C14) |
| [27] | MOBI VID I–II | DIGEST-LEVEL (via the repository's own event-type and role summary) | Credential family and issuer roles |
| [11] | Rodriguez Garzon et al., AI agents with DIDs and VCs | DIGEST-LEVEL | Agent-identity framing |

## Registry delta rows

| Content Block | T | Source | Ch. | Ready | Notes and status |
|---|---|---|---|---|---|
| Full-coverage CAV scenario S9 (ten acts, coverage and placement ledgers) | A/B | HDA 04 §2 | 4 §4.4 | 80% | Design; buildable except Set C. Doubles as the C4 MOBI conformance argument in operational form |
| Full-coverage agent scenario S10 (seven acts) | A/B | HDA 04 §3 | 5 §5.2 | 75% | Design; **unblocked 2026-10-14** by the Set C harness (Slice 1d). Buildable except the attenuated delegation of §3.5 |
| Operation inventory: 23 operations across four layers | B | HDA 04 §1.2 | 2 §2.5, 4 | 90% | The surface the compliance suite does not cover |
| Object inventory: 18 classes with placement | B | HDA 04 §1.3 | 4 §4.5 | 85% | Identifies the five objects that scale with credentials |
| **The identity-versus-delegate rule** | A | HDA 04 §2.2, §3.9, §4 | 4, 5 | 85% | Derived twice independently; immediately usable prose |
| **The attenuation finding and the composed DelegationRegistry** | A | HDA 04 §3.5, §4 | 5 §5.2 | 70% | Contribution candidate; second instance of the extend-beside method after endorsement |
| T2 as the system's actual verification primitive | A | HDA 04 §2.5, §4 | 2 §2.5, 5 | 65% | Spec v1.1 question, adjacent to F-VID-1 |
| On-chain typing rule: pay when the consumer cannot hold the credential in advance | A | HDA 04 §2.4, §3.4 | 4 §4.5 | 80% | Derived independently in both scenarios |
| Coverage result: 22 of 23 operations per scenario; `removeRoot` institutional only | B | HDA 04 §2.13, §3.10, §5 | 4 | 90% | — |

## Open questions for the researcher

1. **Is attenuated delegation a contribution, a finding, or a work order?** §3.5 argues that F11 is insufficient once principals spawn and that a `DelegationRegistry` beside the interface closes the gap by the same method as endorsement. If this is a contribution it affects the C14 framing and Chapter 5 §5.2; if it is a finding it belongs with F-VID-7; if it is a work order it belongs in the build plan. It cannot be all three, and the choice shapes how §3 is written up.
2. **Should the specification name a composite verification?** §4 finds that T2 — status and entitlement and type binding together — is the primitive every verifier actually uses, and that F6 alone is never sufficient in either scenario. Does spec v1.1 say so, and if so as a normative function or as a stated verifier obligation? This interacts with decision D4 on F-VID-1.
3. **Which of S9 and S10 is built first, and is either built before the researcher's own full-coverage scenarios are compared against them?** The brief's purpose for this document is comparison. Building first risks anchoring the comparison on this document's choices.
4. **Does the vehicle scenario carry the MOBI conformance argument (C4) in the thesis, or does the existing mapping table?** S9 §2 is the mapping in operational form and is more persuasive, but it is a design, and the mapping table is evidence.
5. **May ephemeral sub-agents ever have DIDs?** §3.9 concludes no, on measured deactivation cost. If a deployment on a Local CVIN sidechain makes the cost negligible, the conclusion weakens — and the thesis would then be making a claim about a chain's economics rather than about identity design. Which claim is intended?
6. **Does `ISetC` v1.1 gain a validator-answer function (F-VID-11)?** Act V and act VI both run C3 → assessment → C4, and §2.7 now records that the interface has no function for the middle step; the harness added `resolveValidationAs` to make it work. `ISetC` is optional and non-normative, so extending it does not touch `IMinimalSSI` — which makes this the cheapest of the three interface findings to act on, and the one most likely to be waved through without the thesis noticing it is the third instance of the same pattern (F-VID-1 content binding, F-VID-7 entitlement, F-VID-11 validation answer: in each case the interface describes a check but omits the write that would make the check meaningful). Is that pattern itself worth naming in Chapter 5?
