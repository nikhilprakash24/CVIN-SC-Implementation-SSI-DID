CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Reputation, Identity, and Federated Learning**

**Why collective computation among connected vehicles and agents needs reputation, why reputation needs persistent accountable identity, and why that identity needs the IMinimalSSI + endorsement + Set C system — argued as a chain of necessity and generalised to every analogous case**

Document 10 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose → Chapter 5, new §5.x "Reputation, identity, and collective computation"; motivation hooks → Chapter 1, §1.2; Set C evaluation hooks → Chapter 4, §4.x*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 1. Purpose, thesis, and where this lands

This document makes one argument and then shows that it is not one argument but a pattern. The argument is a chain of four necessities:

1. Collective computation across connected and autonomous vehicles (CAVs) and artificial-intelligence agents — federated machine learning (FL) for driving and traffic models, cooperative perception, crowd-sourced high-definition (HD) maps, road-condition and traffic reporting, collaborative misbehaviour detection, and pay-per-use road pricing — produces an output that is only as good as the contributions it aggregates.
2. Aggregating contributions robustly means weighting, admitting, and excluding participants, and doing that well over time requires **reputation**: a summary of each participant's history that can be turned into a weight.
3. Reputation is meaningless unless it attaches to something that persists, cannot be freely duplicated, cannot be sold, and can be held to account — that is, **identity** with specific properties.
4. Identity with those properties, *plus* selective disclosure so that reputation does not collapse into surveillance, is precisely what the thesis's twelve-function interface (IMinimalSSI, F1–F12), the endorsement extension (G1–G4), and the optional Set C trust layer (C1–C4) provide — and, more sharply, several of the properties are *not* provided by the alternatives the thesis compares against (SCMS pseudonym certificates alone; a bare federated identity provider; a token-only registry).

The pattern is that the same four links hold, with the nouns substituted, for every case the researcher grouped under "and the like": cooperative perception, HD-map crowdsourcing, road-condition reporting, pay-per-use roads, agent task marketplaces, and collaborative anomaly detection. Section 7 states the pattern and tabulates the substitutions.

This document is deliberately the *why* document of the suite. The data-placement mechanics it relies on are in 01 (what goes on-chain, what is anchored, what is cached); the zero-knowledge machinery is in 02; the tiered hybrid that hosts the design is in 03; the scenario grammar (actors, objects, F-tags, tiers, placement, failures, tail) is exercised in 04, 05, 06 and 08; and this document points to them rather than repeating them. It contributes three things the thesis does not yet contain: a Chapter 5 section that turns the Memo A/B stance on "optional reputation" into a necessity argument; two motivation paragraphs for Chapter 1 that tie the accountability gap to the collective-computation use cases the 2020 CVIN paper [5] already placed in its high-latency tier; and, for Chapter 4, a concrete statement of what a Set C benchmark must measure (convergence, stability, Sybil and collusion resistance, and the effect of reputation on partner selection) and a demonstration plan that can produce those measurements from the sandbox.

A word on register. Every section opens with its claim, then the reasoning, then either the evidence or the test that would produce evidence. Where a quantity is measured it comes from the O1 ERC-1056 trace in the sandbox (`5_minimal-ssi-sandbox/traces/i2i_O1_ERC1056_1780620182135.jsonl`) and is labelled as such; every other number is a target, a budget, a formula, or an external figure carrying a DIGEST-LEVEL or UNVERIFIED label. Nothing in this document is a result of running an FL system; the FL demonstration in Section 9 is a plan.

## 2. The collective-computation problem in CAVs

**Claim.** Each of the collective-computation workloads that the CAV and agent ecosystem already anticipates — FL, cooperative perception, HD-map crowdsourcing, road-condition reporting, misbehaviour detection — is an *aggregation over untrusted contributors*, and each fails in a characteristic way when a contributor is wrong, malicious, or duplicated.

### 2.1 Federated learning for driving and traffic models

Federated learning, in the form introduced as FedAvg by McMahan et al. [NEW-1, DIGEST-LEVEL], trains a shared model by having each client compute an update on its local data and having a server average those updates, weighted by local dataset size, without the raw data leaving the client. The survey by Kairouz et al. [NEW-2, DIGEST-LEVEL] catalogues the open problems: heterogeneity of data and devices, communication cost, privacy of the updates themselves, and — the problem that this document turns on — robustness to clients that send poisoned or fabricated updates. In the CAV setting the clients are vehicles (or their fleet back-ends) and the models are perception networks, driver-behaviour predictors, traffic-flow forecasters, energy-consumption estimators, and the like. The 2020 CVIN paper [5] placed "driving data for neural network and autonomous driving training" in its high-latency tier, which is the correct placement: the training round is administrative (Tier 3, >500 ms) even though the model it produces will eventually run inside Tier 1 (<100 ms) on the vehicle. That asymmetry — computed slowly, consumed fast — recurs throughout this document and is the single most important placement fact for reputation.

What FL needs from each participant is (a) an update computed from genuine local data by the agreed procedure, (b) a truthful statement of the weight that update deserves (in FedAvg, the number of local samples), (c) availability across enough rounds for the model to converge, and (d) a way to find out afterwards which update came from whom if the model degrades. FedAvg as published assumes (a) and (b) by construction and provides nothing for (d).

### 2.2 Cooperative perception

Cooperative perception has vehicles and roadside units (RSUs) share detected objects (or intermediate features) so that a receiver "sees" around occlusions and beyond sensor range. It runs in Tier 1 or the low end of Tier 2, and its failure is immediate: a fabricated ghost vehicle causes a needless emergency brake; a suppressed real pedestrian causes a collision. What it needs from participants is correct detection, honest confidence, accurate localisation, and timeliness. Crucially, it cannot afford a chain read in the loop; whatever trust it applies must already be resident on the receiver before the message arrives. The Security Credential Management System (SCMS) [6], [28] authenticates that a message came from *an* enrolled device; it does not say whether that device's detections have historically been good.

### 2.3 Crowd-sourced HD maps

HD-map crowdsourcing aggregates lane geometry, signage, and change detection from many vehicles' passes. It is an averaging problem over noisy observations with a heavy-tailed error distribution (mis-calibrated sensors, wrong lane assignments) and an adversarial one (an actor who wants a map to show a lane where there is none). It needs from participants sensor calibration quality, honest change reports, and geographic coverage; its aggregation is spatial (per map tile) rather than per model, but it is still a weighted combination in which a bad contributor's weight is the whole question.

### 2.4 Road-condition and traffic reporting

Road-condition reporting (potholes, ice, debris, construction) and traffic-state reporting (speed, density, incidents) are already the follow-on "further functionality" tail of the CAV scenarios in 04–06, and the 2020 paper listed advanced navigation among its low-latency services and immutable history among its high-latency ones [5]. These are the simplest aggregations — counts and averages per road segment — and therefore the cheapest to attack: a handful of fabricated reports closes a road on every navigation system in the region. They need from participants truthful observation, plausible location (a report should come from a vehicle that was there), and non-duplication.

### 2.5 Collaborative misbehaviour detection

Misbehaviour detection in vehicle-to-everything (V2X) systems — the local plausibility checks on basic safety messages (BSMs) and the reporting of implausible senders to a misbehaviour authority so that their certificates can be revoked — is itself a collective computation: individual detectors produce reports, and an authority aggregates reports across many detectors before acting. ETSI's work on misbehaviour reporting and the SCMS misbehaviour authority define the reporting path [NEW-11, UNVERIFIED; 6]. Its adversarial structure is the sharpest of the five: the attacker's goal may be to get an honest vehicle revoked (slander), and the system's aggregation must therefore weight reports by the reporter's own standing.

### 2.6 What each workload needs from participants

The five workloads differ in tier, in aggregation function, and in failure mode, but their participant requirements are the same four, in different proportions. Table 2.1 states them; the rest of the document shows that each requirement traces to reputation and from there to identity.

**Table 2.1 — Participant requirements per collective-computation workload**

| Workload | Aggregation | Tier of aggregation | Tier of consumption | Needs from participants | Characteristic failure |
|---|---|---|---|---|---|
| Federated learning | Weighted average of model updates (FedAvg) or robust variant | 3 | 1 (model runs on vehicle) | Genuine local data; correct procedure; truthful weight; availability; attributability | Poisoned model, backdoor, slow convergence |
| Cooperative perception | Fusion of detections | 1–2 | 1 | Correct detection; honest confidence; timeliness | Ghost objects, suppressed objects |
| HD-map crowdsourcing | Spatial averaging per tile; change voting | 3 | 1–2 | Calibration quality; honest change reports; coverage | Corrupted tiles, false lanes |
| Road/traffic reporting | Counts and averages per segment | 2–3 | 2 | Truthful observation; plausible location; non-duplication | Fabricated closures, traffic manipulation |
| Misbehaviour detection | Report aggregation before revocation | 3 | 1 (revocation reaches BSM path) | Honest reports; reporter standing | Slander-driven revocation of honest vehicles |
| Pay-per-use roads | Sum of usage attestations | 2 (attestation), 3 (settlement) | 3 | Truthful attestation by RSU; correct vehicle binding | Over- or under-billing; ghost usage |

The last row is added because the researcher's checklist groups pay-per-use roads with this family, and it fits: usage is attested by RSUs and summed by a billing back-end, and the weight the billing system should give an RSU's attestations is, once again, a matter of that RSU's history.

## 3. Why aggregation needs reputation

**Claim.** Robust aggregation rules bound the damage a *fraction* of bad contributors can do; they say nothing about who counts as a contributor. Without identity the fraction is chosen by the attacker (Sybil). With identity but without reputation, admission is a one-bit decision that is cheap to pass and expensive to revoke. Reputation is the mechanism that converts history into a continuous weight, and it is also the mechanism that makes incentives — payment for contributions and penalties for bad ones — enforceable.

### 3.1 What Byzantine-robust aggregation actually guarantees

The Byzantine-robust aggregation literature replaces the plain mean with an estimator that tolerates a bounded number of arbitrary inputs. Krum [NEW-3, DIGEST-LEVEL] selects the single update whose summed squared distance to its nearest n − f − 2 neighbours is smallest and tolerates f Byzantine clients when 2f + 2 < n. Coordinate-wise trimmed mean and median [NEW-4, DIGEST-LEVEL] discard the extreme β fraction on each coordinate, or take the median, and tolerate up to a constant fraction below one half. Kairouz et al. [NEW-2] review these and their failure modes: all of them assume that the *number* of malicious clients is bounded relative to the total, that honest clients' updates are roughly similar (which fails under non-independent, non-identically distributed data, exactly the CAV situation where a vehicle in Whistler and one in downtown Vancouver see different worlds), and that an attacker cannot make its update look like the honest majority (which the later "model replacement" and backdoor literature [NEW-8, UNVERIFIED] shows to be a weak assumption).

The point for this document is not to select among these estimators. It is to observe what they take as given. Every one of them is parameterised by n, the number of participants, and by f or β, the number or fraction that may be bad. They protect against a bounded minority. They do not tell you how to make sure the minority is bounded.

### 3.2 Without identity the attacker chooses the fraction

Douceur's Sybil-attack result [NEW-5, DIGEST-LEVEL] is the reason: in a system without a logically centralised authority that certifies identities, an entity can present as many identities as it likes, and every scheme that assumes a bounded fraction of faulty identities is defeated by an attacker that manufactures identities until it holds the fraction. Applied to FL, an attacker with one vehicle and the ability to enrol arbitrarily many "vehicles" becomes f = n/2 at will; Krum's condition 2f + 2 < n fails; trimmed mean discards honest updates as outliers. The same is true of a road-closure vote, a map-tile change vote, or a misbehaviour-report threshold. Later work on FL specifically treats Sybil defence as a distinct problem from Byzantine robustness — for example by exploiting the similarity of Sybil updates to each other [NEW-9, UNVERIFIED] — precisely because the robust estimators do not solve it.

Douceur's own conclusion is that the only reliable defence is a certifying authority, and the SCMS [6] is exactly that authority for the BSM layer: enrolment certificates are issued by an enrolment CA after device attestation, and pseudonym certificates are derived under the authority's linkage scheme. So a naive reading would say the CAV problem is solved. It is not, for two reasons the thesis has already established. First, SCMS pseudonym certificates are deliberately *unlinkable across time* by outside observers, which is the right property for BSMs and the wrong property for a reputation system: reputation requires exactly the linkage that pseudonyms destroy. Second, the accountability gap the thesis names in Chapter 1 — that SCMS pseudonymity precludes answering "what is the history of actions taken by vehicle V?" — is, restated, "SCMS provides Sybil resistance without a reputation substrate". Section 4 returns to how the verinym/pseudonym split resolves this without giving up unlinkability where it matters.

### 3.3 With identity but without reputation, admission is binary and gaming is cheap

Suppose identities are certified (each participant holds a credential from an admitted issuer) but nothing else is recorded. Admission is then a one-bit decision: hold the credential, contribute; do not, do not. Three problems follow. The bit is expensive to flip off: revoking a participant's credential requires evidence, an issuer willing to act, and, in a CAV context, a legal process, so in practice a bad participant remains admitted for a long time. The bit carries no gradation: a vehicle whose sensor is drifting is not malicious and should not be revoked, but its map contributions should count less, and a binary system has no way to say so. And the bit is transferable in practice even when it is not in principle: a fleet operator's credential admits every one of its vehicles, and one bad vehicle in a good fleet has the same weight as the fleet's best. Reputation is the thing that makes admission continuous and the weight per-participant rather than per-issuer.

### 3.4 Reputation converts history into weight

Define reputation for this document as *a summary statistic of a participant's contribution history, computed by parties entitled to score it, that an aggregator may consult to set the participant's weight, admission, or exclusion in the next round*. Three features of that definition matter. It is a summary — a mean, a count, a recency-weighted average — so that the aggregator does not need the full history at decision time (the placement consequence is that the summary is cacheable and the history is anchored; 01 §5). It is computed by *entitled* parties, which means the scoring function has its own trust structure: who may score whom is a governance question and, in the thesis's vocabulary, an endorsement question (G1–G4). And it is consumed *before* the next contribution, which means the read path is on the critical path of every round and the write path is not.

The weight rule is the point where reputation enters the aggregation algebra. In the reference design of Section 6 the rule is stated explicitly: a weight that is zero below a threshold (exclusion), capped for new participants (cold-start suppression, which is the Sybil defence), and otherwise increasing in the mean score and saturating in the attestation count. Nothing in the Byzantine-robust literature is displaced by this; the reputation weight is applied *before* Krum or trimmed mean, so the estimator's bounded-fraction assumption holds over reputation-weighted mass rather than over raw head-count. That is the sentence that resolves the tension between 3.1 and 3.2: robust aggregation bounds the damage of a minority, and reputation-weighting is what keeps the adversary a minority.

### 3.5 The signals that feed reputation

Reputation for collective computation is fed by at least three kinds of signal, and a design that conflates them mis-scores. *Data-quality* signals measure how useful a contribution was: in FL, the change in validation loss attributable to including the update (or a cheaper proxy such as agreement with the robust aggregate); in maps, agreement with the consensus tile after settlement; in perception, agreement with later ground truth. *Availability* signals measure participation itself: rounds joined, reports delivered, uptime — these are what make a model converge and are gamed by exactly the low-effort strategies that Sybils use. *Honesty* signals measure whether the participant's claims about itself were true: its stated sample count, its stated location, the validity of its proof of correct computation. Each maps to a different evidence object and, in the reference design, to a different `evidenceURI` schema in the C1 attestation; Section 6.4 gives the mapping.

### 3.6 Incentives need accountable identity twice

If contributions are paid for — and in a market of independent vehicle owners and independent agents they will be — then the payment system needs to know whom to pay, which is an identity question, and the penalty system needs to be able to withhold, claw back, or slash, which is an identity *and* reputation question. Payment without reputation pays Sybils; reputation without payment has no stick beyond exclusion, which for a Sybil is free. The two systems therefore share an identity substrate and a ledger of contribution events; 06 designs the payment scenarios and this document only requires that the same DID that accrues reputation is the one that is paid and, if a stake is posted, the one that is slashed. The audit trail — "not that blockchain prevents attacks, but that it makes attacks permanently visible and attributable", in the framing the thesis already uses — is what makes slashing defensible after the fact.

## 4. Why reputation needs identity

**Claim.** A reputation score is a function of a history; a history is a sequence of events attributed to a subject; and for that attribution to mean anything the subject must persist across events, must not be duplicable at will, must not be transferable to another party, must be accountable for the events, and must be able to control *who* learns the linkage between events. Each of these is a property of identity, and not every identity system has all five.

### 4.1 Persistence

Allen's principles of self-sovereign identity [1] begin with existence and persistence: identities must live independently of any single provider and must be long-lived. For reputation this is not a nicety but the precondition: a score attached to an identifier that expires with a session or a pseudonym certificate batch is a score over a window too short to be informative and too easy to reset. The thesis's central "accountability gap" argument is a persistence argument: SCMS pseudonyms are engineered for non-persistence; the blockchain-anchored DID (F1 createDID; F2 resolveDID returning a document for any DID that ever existed, including deactivated ones under F4) is engineered for persistence with a tamper-evident key-material history. Reputation lives on the persistent object.

### 4.2 Non-transferability

If reputation can be sold, it becomes a commodity and the market price of a good reputation is the price of the attack. Weyl, Ohlhaver and Buterin's argument for non-transferable "soulbound" tokens [15] is exactly this: attestations about a subject are meaningful only if they cannot be moved to another subject. In the thesis's design non-transferability is not enforced by token semantics (although O2 and O5 in the sandbox do mint soulbound tokens as their native pattern); it is enforced by the fact that reputation attestations (C1) are keyed by DID, that DID control is a matter of key material (F9–F12), and that transferring control of a DID is a visible on-chain event (F3 updateDID, DIDUpdated) that a scoring policy can treat as a reputation reset. The audit trail makes the transfer detectable; the policy makes it costly.

### 4.3 Sybil cost

Douceur's result says Sybil resistance needs an authority; the thesis's design says the authority is a *set* of endorsed issuers rather than a single one, and that admission to a collective computation requires a participation credential (F5) from an issuer endorsed for that credential type (G2, checked by G4). The cost of a Sybil identity is then the cost of obtaining one more such credential — a vehicle registration, a fleet-membership credential, an agent-operator credential — and that cost is set by the issuer's process, not by the ledger. Two further costs stack on top. The reputation cold-start cap (Section 6.5) means a fresh identity has near-zero weight until it has contributed honestly for some rounds, so the Sybil must *do the work* before it can *do the damage*. And a participation stake (06) makes the identity's misbehaviour financially costly. Memo A's stance — "Sybil/collusion handled by issuer weighting, participation costs, anomaly screens" — is precisely this triple.

### 4.4 Accountability

Accountability is the property that a history can be *shown* to belong to a subject in a way a third party can check. In the thesis's design every event that feeds reputation leaves an anchor: a credential hash (F5), a presentation commitment (F8), a delegate authorisation (F11), a reputation attestation event (C1's `ReputationAttested`), a validation request (C3's `ValidationRequested`). The content behind the anchor is off-chain, but the anchor is enough for a dispute: a participant who claims to have been scored unfairly can present the contribution whose hash was anchored in the round's commitment; an aggregator who claims a participant poisoned the model can point to the anchored update hash and the off-chain update that matches it. This is the "forensic audit trail as an accountability primitive" from the Building Paths preface, applied to reputation.

### 4.5 Privacy, and the apparent contradiction

Here is the tension this section must resolve. Federated learning is *motivated* by privacy: the whole reason to send updates instead of data is that the data is sensitive. Reputation is *inherently* linkable: it requires that many contributions be attributed to one subject. If reputation requires that every update be publicly attributed to a vehicle's persistent identity, then FL over a reputation system leaks a per-vehicle participation history that is itself sensitive (which roads, which hours, which fleet). The 2020 paper's dual identity modes [5] — a pseudonymous stream for routine interaction and a verinym for commercial transactions — are the shape of the resolution, and 02 supplies the cryptography.

The resolution has two layers. *Layer one*: contributions are made under **pairwise or per-round pseudonymous DIDs**, and reputation is attested to the **verinym**. The aggregator, which is an endorsed party operating under a data-handling policy credential, is the only party that learns the pseudonym-to-verinym link, and it learns it because the participant chooses to present it (F8, challenge-bound, to the aggregator only). The public chain then shows that aggregator A attested score s to verinym V at time t, with an `evidenceURI` that is a commitment, not a plaintext pointer — and nothing about *which* contribution or *which* round. This is the design recommended for the general pass because it uses only functions that exist today. What it leaks is the fact of participation in A's programme, and Section 8.6 treats that leak honestly.

*Layer two*, for the ZKP angle pass (02 §6): the participant presents, under the pseudonym, a zero-knowledge proof that "the holder of this pseudonym controls a verinym whose reputation from endorsed scorers is at least θ and which holds a participation credential from an endorsed issuer", without revealing the verinym; the aggregator admits and weights the pseudonym on the strength of the proof; and reputation is later folded back onto the verinym by a second proof of pseudonym control. The aggregator then never learns the link. The cost is the proof (02 gives the DIGEST-LEVEL figures: Groth16 on-chain verification ≈200–350K gas if verified on-chain; verification off-chain with an anchored result is the cheaper hybrid), and the complication is that the on-chain `getReputation` view (C2) cannot itself be queried privately — the proof must be over an off-chain copy of the attestation history that is anchored on-chain (01 §5, "anchor/cache/attest"). Layer two is what turns "reputation on the verinym; contributions under pseudonyms" from a policy promise into a cryptographic one.

## 5. Why identity needs this system

**Claim.** Each of the five properties in Section 4, and each of the four participant requirements in Section 2, maps onto a specific function or object of the thesis's system, and the mapping is tight enough that removing any component removes a property. This section is the bridge between the necessity argument and the reference design.

### 5.1 The mapping

**Table 5.1 — Requirement → function/object mapping**

| Requirement (from §2–§4) | Function / object | What it provides | Placement (01) | Tier |
|---|---|---|---|---|
| Persistence of the subject | F1 createDID, F2 resolveDID, F3 updateDID, F4 deactivateDID | A DID that exists from creation, resolves forever (deactivated DIDs remain resolvable with a flag), and whose control changes are events | DID document anchor on-chain; document body off-chain in O1's event-sourced pattern | 3 |
| Device or training node acting for the subject | F11 addDelegate (sigAuth), F12 validDelegate, F9/F10 verification methods | The OBU, edge trainer, or fleet server signs contributions with a delegate key bounded by validity; verifiers check with a free view | Delegate mapping on-chain; delegate key held on device | 3 (grant), 1–2 (check, cached) |
| Admission proof | F5 issueCredential (participation credential, content off-chain), F6 verifyCredential | Proof that an endorsed issuer admitted this subject to this programme; revocable (F7) | Hash + validity on-chain; W3C-shaped credential off-chain | 3 (issue), 2 (verify, cached) |
| Selective proof of standing | F8 createPresentation (+ 02's ZK extensions) | Challenge-bound, replay-protected presentation of credentials to an aggregator or scorer | Presentation commitment on-chain; presentation body off-chain | 2–3 |
| Who may vouch for a participant | G1 registerIssuer, G2 endorseIssuer, G4 isEndorsed | Roots of trust for participation credentials (a transport ministry endorses a fleet regulator; an OEM endorses its fleet back-end) | Endorsement registry on-chain | 3 |
| Who may score | G2 endorseIssuer with credentialType = SCORER (or AGGREGATOR), G3 revokeEndorsement | Only endorsed aggregators' C1 attestations count in a policy; slander from unendorsed parties has zero weight | Endorsement registry on-chain | 3 |
| Reputation summary | C1 attestReputation(did, score, evidenceURI), C2 getReputation → (meanScore, attestationCount) | Score on 0–100 (uint8), attester recorded in the event, evidence pointer; free read of mean and count | Mean and count on-chain (the cache); full attestation history in the event log; evidence off-chain | 3 (write), 1–3 (read, cached) |
| Proof of correct local computation | C3 requestValidation(did, validationType, payload) → requestId, C4 validationStatus | zkML or TEE-attested proof that the update was computed by the agreed procedure on data of the claimed size; validators are endorsed | Request and status on-chain; proof off-chain, payload = proof hash | 3 |
| Round anchoring | F5 issued by the aggregator DID with credentialHash = keccak(roundRecord) | Round id, global model hash, contributor-set commitment (Merkle root of contribution hashes), aggregation rule id | Hash on-chain; roundRecord and model weights off-chain (IPFS/enterprise store per 01 §7) | 3 |
| Payment and slashing | Same DID; 06's payment objects | Accountable payee; slashable stake | See 06 | 2–3 |

### 5.2 Three observations the mapping forces

First, **the on-chain reputation object is a cache, not the history.** ISetC's `getReputation` returns only a mean and a count; it cannot express recency, per-attester weighting, or per-programme scoping. Those live in the `ReputationAttested` event log (indexed by DID and by attester), which is the true history, and in the off-chain evidence the URIs point to. A policy that wants a recency-weighted score computes it off-chain from the event log and treats the on-chain scalar as the fast-path approximation — which is exactly the anchor/cache/attest pattern 03 §4 uses for everything else. This is not a weakness to hide; it is the design.

Second, **the aggregator is an identity too.** It has a DID, it is endorsed for the SCORER role by a root the participants recognise, its C1 attestations are events with its DID as `attester`, and it is itself scorable. A participant-side policy can therefore weight aggregators, and an aggregator that mis-scores accumulates a history. Section 8.7 uses this against the "malicious aggregator" attack.

Third, **the check is free and the write is rare.** F6, F12, G4 and C2 are views; on a cached node they cost nothing and complete in the sub-100 ms budget of Tier 1 if the node is local (RSU as edge server, in the 2020 paper's language [5]). C1, C3, F5 and F11 are writes, but per round there is one F5 (the round anchor) and k C1 calls (one per scored participant), and per participant there is one F11 per delegate validity window. The measured O1 costs of the writes that exist — F5 130,163 gas, F11 54,227 gas, F8 62,441 gas, F7 32,980 gas (all from the S1 trace) — are the only measured inputs to the cost model in Section 6.9; C1 and C3 are unmeasured and are carried as variables.

## 6. Reference design: reputation-weighted federated learning over CVIN identities

**Claim.** A complete FL round can be specified over the thesis's objects such that every trust decision is traceable to an on-chain anchor, every participant is a DID acting through a delegate, every score is an attestation by an endorsed scorer, and the per-round on-chain cost is one anchor transaction plus one attestation per scored participant. This section is the design; Section 9 is how to demonstrate it.

### 6.1 Actors and objects

*Actors (DIDs).* A **programme authority** P (a transport ministry, a consortium, or a fleet regulator) that acts as the endorsement root for the programme. An **aggregator** A, endorsed by P for the roles AGGREGATOR and SCORER for credential type `FL_PARTICIPATION`. A set of **participants** V₁…Vₙ (vehicle verinyms, or fleet back-end DIDs acting for many vehicles, or agent DIDs), each with one or more **delegates** D_i (the OBU or the training node; F11, sigAuth). An optional set of **validators** X_j endorsed by P for VALIDATOR, operating zkML or TEE validation. Optional **pseudonymous DIDs** V_i^(r) per round under the dual-mode pattern.

*Objects.* A `FL_PARTICIPATION` credential per participant (F5, issued by an endorsed issuer, content off-chain: programme id, allowed model families, data-class declaration, validity). A `roundRecord` per round (off-chain JSON; hash anchored by F5). A `contributionProof` per participant per round (off-chain; hash committed in the round's Merkle root). A `ReputationAttested` event per scored participant per round (C1). A `ValidationRequested` event per validated contribution (C3). A payment object per round (06).

### 6.2 The round protocol

**Table 6.1 — One FL round, with F-tags, placement, and tier**

| Step | Actor → action | Function tags | On-chain datum | Off-chain datum | Tier |
|---|---|---|---|---|---|
| 0 (once) | P registers and endorses A for AGGREGATOR/SCORER; endorses issuers for FL_PARTICIPATION; endorses X_j for VALIDATOR | G1, G2 | Endorsement entries | Governance policy document | 3 |
| 0 (once per participant) | Issuer issues FL_PARTICIPATION to V_i; V_i adds D_i as sigAuth delegate with validity T_d | F5, F11 | credentialHash, validUntil; delegate mapping | Credential JSON in holder wallet | 3 |
| 1 | A publishes round r: global model M_r (weights off-chain), roundRecord_r draft (round id, model hash, aggregation rule id, weight rule parameters, deadline) | — (F5 anchor at step 7) | — | M_r, roundRecord_r | 3 |
| 2 | V_i (via D_i) decides to join; fetches reputation-gated eligibility from cache: A checks F6(cred_i), G4(issuer_i, FL_PARTICIPATION), F12(V_i, sigAuth, D_i), C2(V_i) | F6, G4, F12, C2 (views) | reads only | cached snapshot of chain state on A's edge node | 3 (read from cache) |
| 3 | D_i trains locally on V_i's data; produces update Δ_i; computes contributionProof_i (§6.3); optionally requests validation of Δ_i | (C3 optional) | ValidationRequested(V_i, type, requestId) if used | Δ_i, contributionProof_i, zkML/TEE proof | 3 |
| 4 | D_i sends (Δ_i or its secure-aggregation share, contributionProof_i) to A over an I2I channel (08) authenticated by D_i's delegate key; if pseudonymous, presents link proof (F8 or 02's ZK presentation) | F8 (if presenting), F12 (A verifies D_i) | PresentationCreated if F8 used | Channel transcript, update | 3 |
| 5 | A verifies each contributionProof_i; drops invalid; computes weights w_i from C2 snapshot and validation status C4 (§6.5); applies robust aggregation over weighted updates; produces M_{r+1} | C4 (view) | — | M_{r+1}, per-participant score inputs | 3 |
| 6 | A scores each participant s_i ∈ [0,100] (§6.4); writes evidence object E_i (contribution hash, score components, round id) to off-chain store; attests | C1 ×k | ReputationAttested(V_i, A, s_i, evidenceURI_i) | E_i | 3 |
| 7 | A finalises roundRecord_r with Merkle root of all contributionProof hashes and hash(M_{r+1}); anchors it as a credential issued by A to the programme DID | F5 | credentialHash = keccak(roundRecord_r), validUntil | roundRecord_r, M_{r+1}, Merkle tree | 3 |
| 8 | Payment for round r released against roundRecord_r and the C1 events (06) | 06's tags | per 06 | per 06 | 3 |
| 9 (exceptional) | V_i disputes s_i: presents contributionProof_i and Merkle path against roundRecord_r's root to P or an arbiter; if upheld, P or A issues a corrective C1 attestation and, if A is at fault, P scores A | F8, C1, (G3 if A is de-endorsed) | PresentationCreated; ReputationAttested (corrective) ; endorsement revocation | Dispute bundle | 3 |

Every step's placement follows 01's rule: content off-chain, hash on-chain, reads from a cache synchronised with revocation state. The round is entirely Tier 3, which is why it can afford chain writes at all; the Tier 1 consumer of M_{r+1} — the vehicle running it — never touches the chain.

### 6.3 The contribution proof

A `contributionProof_i` for round r is the tuple

```
contributionProof_i = ( r, V_i (or V_i^(r)), h(Δ_i), n_i, t_i,
                        [π_norm_i], sig_{D_i}( r ‖ V_i ‖ h(Δ_i) ‖ n_i ‖ t_i ‖ [h(π_norm_i)] ) )
```

where h(Δ_i) is the keccak hash of the serialised update (or of the participant's secure-aggregation share), n_i is the claimed local sample count, t_i is a timestamp, π_norm_i is an optional zero-knowledge proof that ‖Δ_i‖ is within the round's bound B (a norm-bounding proof is the cheapest useful honesty proof: it prevents the "scale the update by 10⁶" model-replacement attack without revealing the update), and the signature is by the delegate key D_i, whose authority over V_i is checkable with F12 at any time (including retroactively at a dispute, because the delegate grant and its validity are on-chain events). The proof is what makes the contribution *accountable*: it binds a specific update to a specific identity through a key whose authorisation is anchored. It costs nothing on-chain; it is included in the round's Merkle tree.

### 6.4 Scoring by the aggregator

The aggregator is endorsed for SCORER, so its C1 attestations are the ones a participant-side or programme-side policy counts. The score s_i for round r is a policy-defined function of three components, each with an evidence field in E_i:

- **Quality q_i**: a measure of the update's usefulness. Cheap proxy: cosine similarity of Δ_i to the robust aggregate (a participant whose update points the way the trimmed majority points is scored higher); costlier proxy: leave-one-out validation-loss delta on A's held-out set. Both are stated in E_i with the aggregate hash, so a disputant can recompute.
- **Availability a_i**: 1 if the contribution arrived by the deadline with a valid proof, 0 otherwise.
- **Honesty h_i**: 1 if all claims checked (norm bound proof valid; n_i consistent with the participation credential's declared data class; validation status via C4 = accepted if validation was requested), 0 if any failed.

A representative rule is s_i = 100 · a_i · h_i · clip(q_i, 0, 1), but the rule is a programme parameter, not a system constant, and it must be published in `roundRecord_r` (aggregation rule id and weight rule parameters) so that scores are reproducible. The `evidenceURI_i` points to E_i; per 01's GDPR nuance, E_i itself must not be personal data in the clear, so it carries hashes and score components, not the update.

### 6.5 Reputation update, weighting rule, and exclusion

*On-chain update.* C1 appends an attestation; C2 returns the running mean over all attestations and the count. Because ISetC exposes only (meanScore, attestationCount), recency is not on-chain. A policy that wants an exponentially weighted score r_i,t = (1 − α) r_i,t−1 + α s_i,t computes it off-chain from the `ReputationAttested` event stream and anchors nothing extra; the chain's mean is the coarse cache.

*Weighting rule.* Let m_i be the reputation used by the policy (on-chain mean, or off-chain recency-weighted score), c_i the attestation count, θ the exclusion threshold, c₀ the cold-start count, and v_i ∈ {1, β} a validation multiplier (β < 1 for unvalidated contributions when validation is available). Then

```
w_i = 0                                            if m_i < θ and c_i ≥ c_min      (excluded)
w_i = v_i · (m_i / 100) · min(1, c_i / c₀) · n_i   otherwise
```

and the weighted updates are passed to the robust aggregator (trimmed mean over weighted mass, or Krum over the top-weighted set). The `min(1, c_i/c₀)` factor is the Sybil defence: a fresh identity contributes at most 1/c₀ of a seasoned identity's weight per unit of claimed data, so an attacker with m fresh identities has weight at most m · n_max / c₀ against an honest population of N seasoned identities with weight ≈ N · n̄. The condition for the attacker to remain below the robust estimator's tolerated fraction β_tol is m · n_max / c₀ < β_tol · N · n̄ — a formula the demonstration in Section 9 will test, not a result.

*Exclusion.* Exclusion is a policy over (m_i, c_i), never an on-chain flag: the chain records attestations, the policy decides. This is deliberate — an on-chain "banned" bit would be a governance decision disguised as a data field. If a programme wants an enforceable exclusion it revokes the participation credential (F7) and the F6 check at step 2 fails.

### 6.6 Appeal

A participant who believes s_i was wrong holds contributionProof_i and can obtain the Merkle path from A (or reconstruct it from the round's published tree). It presents (F8, challenge-bound to the arbiter's domain) the participation credential and, off-chain, the proof and path against the anchored roundRecord_r hash. The arbiter — P or a P-endorsed dispute role — recomputes q_i from E_i's published inputs. If the score is overturned the arbiter issues a corrective C1 attestation; because C2 is a mean, a corrective attestation only partially cancels the bad one, which is a known limitation of ISetC's scalar design and one of the open questions in Section 12. If A is found to have mis-scored systematically, P scores A (C1 on A's DID) and may revoke A's SCORER endorsement (G3), after which A's attestations stop counting in policies that check G4 at attestation time.

### 6.7 Payment

Payment is out of scope here and designed in 06 (payment scenarios for CAV and agent). The interface this document requires of it is minimal: the payee is the DID that received the C1 attestation; the payment for round r is conditioned on the existence of roundRecord_r's anchor and of V_i's contribution hash in its Merkle root; and any stake posted for participation is slashable against a corrective attestation or an upheld dispute.

### 6.8 The audit trail

At the end of round r the chain holds: the endorsement entries that authorised A and the issuers; each participant's participation credential hash and delegate grant; one round anchor whose hash commits to every contribution hash and to the new model; k `ReputationAttested` events naming A as attester; any `ValidationRequested` events; any `PresentationCreated` events from disputes. Off-chain, under the anchors, sit the round record, the model, the contribution proofs, the evidence objects, and the validation proofs. This is enough to answer, after the fact and by anyone with read access, *which identities contributed to model M_{r+1}, with what weight, scored by whom, on what evidence* — which is the collective-computation form of the accountability question the thesis opened with.

### 6.9 Parametric cost per round

The only measured anchor available is the O1 ERC-1056 trace from S1. The round cost model uses those numbers where a function has been measured and variables elsewhere.

**Table 6.2 — On-chain gas per round (parametric)**

| Item | Count per round | Gas each | Source of gas figure |
|---|---|---|---|
| Round anchor (F5 issueCredential) | 1 | 130,163 | Measured, O1, S1 trace |
| Reputation attestation (C1 attestReputation) | k (scored participants) | g_C1 | Unmeasured; hypothesis: one SSTORE-class update to mean/count plus a LOG with an indexed DID, indexed attester, and a string; a target of ≤ 80K is plausible on ERC-8004-shaped storage but is **not a result** |
| Validation request (C3) | n_val ≤ k | g_C3 | Unmeasured |
| Dispute presentation (F8) | n_disp (exceptional) | 62,441 | Measured, O1, S1 trace |
| Delegate grant (F11) | amortised: 1 per participant per T_d | 54,227 | Measured, O1, S1 trace |
| Participation credential (F5) | amortised: 1 per participant per validity | 130,163 | Measured, O1, S1 trace |
| Endorsements (G1/G2) | amortised: once per programme | g_G | Unmeasured (EndorsementRegistry under construction; 10 will report) |
| All reads (F6, F12, G4, C2, C4) | many | 0 | View functions; gas-free reads |

So G_round = 130,163 + k · g_C1 + n_val · g_C3 + n_disp · 62,441, plus amortised per-participant costs of (130,163 + 54,227)/T. The design's leverage is in the first term: without the Merkle batch, anchoring every contribution individually would cost k · 130,163 rather than 130,163 — for k = 1,000 that is the difference between one F5 and a thousand — and the batch loses nothing that a dispute needs, because each participant holds its own leaf and path. Whether k · g_C1 is acceptable depends on g_C1 and on the chosen chain (an L2 or the 2020 paper's sidechain-anchored-to-backbone pattern [5] changes the fiat cost by orders of magnitude without changing the gas). The alternative of batching C1 — one attestation per round carrying a Merkle root of scores — is *not* available without extending ISetC, which the interface rules forbid for the minimal set but which the spec's §6 batch-operations extension explicitly contemplates; Section 12 puts it to the researcher.

## 7. The same chain for other cases

**Claim.** Substitute the contribution object and the aggregation, and the four links hold unchanged. The pattern, stated once: *any collective computation that aggregates contributions from many parties must weight those contributions; weighting over time is reputation; reputation requires persistent, Sybil-resistant, non-transferable, accountable, selectively-disclosable identity; and those five properties map to F1–F4 (persistence), F5–F7 with G1–G4 (Sybil cost via endorsed admission), key-material events F3/F9–F12 (non-transferability and delegation), the anchor set F5/F8/C1/C3 (accountability), and F8 with 02's ZK extensions (selective disclosure).*

**Table 7.1 — The chain instantiated per case**

| Case | Contribution object | Aggregation need | Reputation signal | Identity requirement | Function / object mapping |
|---|---|---|---|---|---|
| Federated learning (§6) | Model update Δ_i + contributionProof | Weighted robust average per round | Quality (agreement with aggregate, validation delta), availability, honesty (norm/validation proofs) | Persistent verinym; delegate = training node; pseudonym per round optional | F1–F4; F11/F12; F5/F6 participation; G2/G4 for AGGREGATOR/SCORER; C1/C2; C3/C4 zkML/TEE; F5 round anchor |
| Cooperative perception | Detected-object list with confidence, signed by OBU | Fusion with per-source trust; Tier 1, no chain in loop | Agreement of past detections with later ground truth (scored by RSU or fleet back-end in Tier 3) | Persistent identity behind SCMS pseudonym, disclosed only to scorer; delegate = OBU | F11/F12 (OBU delegate); C1 by endorsed RSU operator; C2 snapshot pre-fetched to receiver's cache; SCMS remains the Tier 1 signer (extension, not replacement) |
| Crowd-sourced HD maps | Tile observation / change report with sensor metadata | Spatial consensus per tile; change acceptance vote | Post-settlement agreement with consensus; calibration honesty | Persistent identity for calibration track record; pseudonymous location trail | F5 map-contributor credential (issued by map operator, endorsed by ministry); C1 per settlement epoch; F5 epoch anchor with Merkle root of observations |
| Road-condition and traffic reporting | Report (segment, condition, time) signed by OBU | Count/average per segment with de-duplication and reporter weighting | Confirmation rate of past reports; location plausibility | Persistent identity; proof-of-presence without revealing route (02) | F11/F12; C1 by endorsed road authority; F8/ZK presence proof; read path from RSU cache (Tier 2) |
| Pay-per-use roads | Usage attestation (vehicle, gantry, time) signed by RSU | Sum of attestations per vehicle per period | Reputation of the *attesting RSU* (consistency with neighbouring gantries, dispute rate); vehicle-side dispute history | Both RSU and vehicle are DIDs; RSU is a delegate of the road operator | F11 (RSU as operator delegate); C1 on RSU DID by operator's auditor; F5 period anchor; F8 for vehicle dispute; payment per 06 |
| Agent task marketplace | Task outcome (deliverable hash, acceptance) | Partner selection: choose agents by expected outcome | Task success rate, timeliness, dispute rate (ERC-8004's native use) | Persistent agent DID; operator as endorser; delegate = runtime instance | F1–F4; F11/F12 (runtime as delegate); F5 capability credential; C1/C2 (ERC-8004 reputation registry pattern); C3/C4 validation of outputs; A2A phases per Memo B |
| Collaborative anomaly / misbehaviour detection | Misbehaviour report (suspect, evidence hash) signed by detector | Threshold over weighted reports before revocation | Precision of past reports (reports later upheld); false-report rate | Persistent detector identity; slander accountability | C1 on detector DID by misbehaviour authority; F5 report anchor batch; F7 on the suspect's credential only after weighted threshold; audit trail for slander disputes |

Two rows deserve a sentence. Cooperative perception shows the "computed slowly, consumed fast" asymmetry in its purest form: the reputation is *written* by an RSU operator in Tier 3 after comparing a vehicle's past detections against later ground truth, and *read* by a receiving vehicle from a cache it pre-fetched when it entered the RSU's coverage, so that the Tier 1 fusion loop applies a per-source weight without any network round trip. 05 places this in its Tier 1 CAV scenario; the design principle is that the chain never appears in the loop, and the pre-fetched snapshot's staleness window is the parameter that must be measured (Memo B's "cache invalidation synchronised with revocation state"). Pay-per-use roads invert the usual direction: the reputation that matters most is that of the *infrastructure* (the attesting RSU), because a mis-calibrated or compromised gantry over-bills thousands of vehicles; the vehicle's identity is needed for dispute, the RSU's for weighting. The identity system does not care which party is infrastructure — an RSU is a DID with a delegate key like any OBU — and that symmetry is an argument for the thesis's I2I generalisation.

## 8. Attack analysis on the reputation layer

**Claim.** The reputation layer introduces its own attack surface, distinct from the aggregation's. Each attack has a mitigation in the design and a residual risk that must be stated; several are measurable in the sandbox and therefore belong in the Chapter 4 benchmark.

**Table 8.1 — Attacks, mitigations, residual risk, measurability**

| Attack | Mechanism | Mitigation in the design | Residual risk | Measurable in the benchmark? |
|---|---|---|---|---|
| Sybil | Attacker enrols many identities to exceed the robust estimator's tolerated fraction | Endorsed admission (F5 from G4-endorsed issuer) sets the per-identity cost; cold-start cap min(1, c/c₀) bounds fresh-identity weight; participation stake (06) | Issuer compromise or a lax issuer mints cheap identities; c₀ trades Sybil resistance against onboarding speed | Yes: inject m Sybils, measure their total weight fraction and the aggregate's error vs. rounds (§9) |
| Whitewashing | A low-reputation identity abandons its DID and re-enrols fresh | Persistence (F4 is irreversible and the DID stays resolvable); a fresh DID starts at the cold-start cap; re-enrolment requires a new participation credential whose issuer can check the *subject's* real-world binding (VIN, operator) | Where the real-world binding is weak (agents with no operator credential) whitewashing is cheap; the defence is then purely economic (stake) | Yes: model an identity that resets at reputation < θ; measure rounds-to-recover-weight vs. c₀ |
| Collusion / ballot-stuffing | A set of participants coordinate to look mutually consistent so that a similarity-based quality score rewards them, or coordinate to score one another if peers may score | Only G4-endorsed scorers' C1 attestations count; participants do not score participants in the reference design; anomaly screen on update similarity (the FoolsGold-style observation that colluders' updates are more similar to each other than honest updates are [NEW-9, UNVERIFIED]) | Endorsed scorer colludes with participants (see aggregator row); similarity screens misfire under non-IID data | Yes: inject a colluding block with correlated updates; measure the quality score they obtain and their weight |
| Slander | An attester writes low scores against an honest identity | Attestations are events with the attester's DID; policies count only endorsed attesters; corrective attestations; the slanderer's own reputation is scorable by P; G3 de-endorsement | ISetC's mean is scalar, so a burst of low scores from a briefly-endorsed attester depresses the on-chain mean until diluted; the off-chain policy can filter by attester but the cached scalar cannot | Yes: inject slander attestations; measure on-chain mean vs. off-chain attester-filtered score, and the effect on the victim's weight |
| Poisoning behind good reputation ("sleeper") | An identity contributes honestly for many rounds, then submits a backdoored update while carrying high weight | Norm-bound proof in contributionProof limits single-round leverage; robust estimator still applied over weighted mass; recency-weighted off-chain score reacts faster than the on-chain mean; validation (C3/C4) where available | A well-crafted, norm-bounded backdoor that survives trimmed mean is a known open problem in the FL literature [NEW-2, NEW-8]; reputation reduces but does not remove it | Partly: the sandbox can measure the weight a sleeper holds and how fast it falls after detection; it cannot certify robustness to unknown backdoors |
| Reputation as a linkability leak | The public C1 event reveals that verinym V participates in A's programme at time t; across programmes and time this is a behavioural profile | Layer-one pseudonymous contributions with reputation on the verinym reveal only participation, not content; Layer-two ZK standing proofs (02 §6) hide the verinym from A; `evidenceURI` is a commitment; Local CVIN shards [5] confine the audience; attestation batching and timing jitter | Under Layer one the participation fact itself is public; under Layer two the reputation snapshot must be re-anchored off-chain for the proof, adding a staleness window | Partly: linkability can be reasoned about, not measured in the sandbox; the ZK angle pass should cost the Layer-two proof |
| Malicious or negligent aggregator | A mis-scores, drops honest contributions, or publishes a model that does not match its anchored contributor set | A is a DID; its attestations are attributable; P scores A; participants hold contribution proofs and Merkle paths for dispute (§6.6); the round anchor commits A to a specific contributor set and model hash, so substitution is detectable | Detection is after the fact; a round already released may have been consumed; multiple aggregators with cross-checked anchors are the structural fix (an open question) | Yes: have the demonstration aggregator drop a valid contribution; assert that the participant's dispute succeeds against the anchored root |
| Evidence rot | `evidenceURI` targets disappear, so a dispute cannot recompute a score | Evidence stored content-addressed (IPFS/Arweave per 01 §7) so the URI is a hash; the score components are also in the participant's own copy of E_i delivered at step 6 | Content-addressed storage without pinning still rots; enterprise stores depend on the operator | Yes: assert in the trace that every `evidenceURI` is content-addressed and resolvable at round end |
| Delegate key compromise | An attacker steals D_i and contributes as V_i | F11 validity bounds the window; F10/F11 rotation; the compromise leaves the honest V_i's reputation damaged — which is the correct outcome for accountability but unjust for the victim | Reputation repair after a key compromise is a governance process, not a function | Partly: measure the number of rounds a compromised delegate can act before validity expiry under different T_d |

### 8.1 What the benchmark should measure

Memo A's benchmark axes include *reputation dynamics*: convergence, stability, Sybil and collusion resistance, and the effect on partner selection. Section 9 turns each into a metric the sandbox can produce. Convergence: rounds to reach a target error with and without reputation weighting, honest population only, and under attack. Stability: variance of the reputation score of an honest participant across rounds, and the score's sensitivity to a single bad round (the α of the off-chain rule and the dilution rate of the on-chain mean). Sybil resistance: the total weight fraction obtained by m fresh identities as a function of c₀ and of the number of rounds they contribute honestly first. Collusion resistance: the quality score a correlated block obtains relative to independent honest participants. Partner selection: in the agent-marketplace instantiation (Table 7.1), the fraction of tasks routed to high-reputation agents, and the loss when reputation is unavailable (the low-connectivity case of 06).

## 9. Demonstration plan

**Claim.** Every step of Section 6 can be exercised in the existing sandbox with one new scenario script, one small extension contract beside O1, and no change to IMinimalSSI, and the attack rows marked "Yes" in Table 8.1 can be measured from the resulting trace. The plan is stated as a work order in the sandbox's own conventions (`scenarios/run_<id>.js`, JSONL trace per `traces/SCHEMA.md`, no scope invention).

### 9.1 What exists and what does not

The sandbox (v1.3) has `ISetC.sol` compiled and clean, O1_ERC1056 live with 12/12 compliance, and the S1 I2I scenario producing the measured trace. `O7_ERC8004.sol` is present as an eleven-line placeholder (a commented-out abstract contract); it does not implement ISetC, and the scenario catalogue defers the agentic wrapper S6 to Stage 31. The `EndorsementRegistry` of §7 in the context brief is under construction. So there is today no Set C implementation to call.

### 9.2 The minimal ISetC stub (with caveat)

Proposal: `contracts/extensions/SetC_Minimal.sol`, a standalone contract implementing ISetC exactly as declared — `attestReputation` stores a running sum and count per DID and emits `ReputationAttested`; `getReputation` returns (sum/count as uint8, count); `requestValidation` stores the payload hash under a fresh requestId and emits `ValidationRequested`; `validationStatus` returns a status settable by an address the deployer designates as validator. It is deployed beside O1 and consults O1 only through IMinimalSSI views (F2 to check the DID exists; F12 to check that `msg.sender` is a valid delegate of the attester DID when attestations are made through a delegate). It lives in `extensions/`, not `implementations/`, because it is not an option and must not be confused with O7.

The caveat must be carried into every trace and into 10: **this stub is not ERC-8004 and its gas is not O7's gas.** ERC-8004's native pattern is three registries (Identity as ERC-721 with CAIP-10 addressing; Reputation with 0–100 scores and evidence URIs; Validation with zkML/TEE hooks) [19], and the sandbox's hard rule "native patterns, never wrapped registries" means O7's measurements must come from that pattern when O7 is built. The stub is a *harness* for the reputation-weighting logic, and its C1/C3 gas may be reported only as "SetC_Minimal on O1, harness figure, not an option benchmark". This respects rule 5 (traces are evidence; never copy gas between options) and rule 7 (scope goes to PROPOSALS.md first). The stub should also be listed in `BUILD_DIRECTIONS/PROPOSALS.md` before it is coded.

### 9.3 Scenario S9: `scenarios/run_fl_reputation.js`

*Setup.* Deploy O1 and SetC_Minimal (and, once built, EndorsementRegistry; until then, the script models endorsement by a local table and tags the steps G1/G2/G4 with `kind: "offchain"` and a note stating the substitution). Create DIDs (F1) for P, A, X, and N honest participants; add a sigAuth delegate (F11, validity T_d) for each participant; issue FL_PARTICIPATION (F5) to each from an issuer DID. Simulated learning: a linear model on synthetic non-IID data (each participant holds a shard with a different mean), local step = one gradient step, so that "convergence" is the error of the global parameter against the known generating parameter — a toy that makes the aggregation behaviour observable without a machine-learning stack, runnable in Node with no dependencies beyond Hardhat.

*Round loop (R rounds).* For each round: A reads C2 for all participants (view; logged as `kind: "view"`); each delegate produces Δ_i and a contributionProof signed with the delegate key; A verifies signatures and F12 (view); A computes w_i by §6.5, applies coordinate-wise trimmed mean over weighted updates, updates the global parameter; A scores s_i = 100 · a_i · h_i · clip(cos(Δ_i, aggregate), 0, 1); A calls C1 for each participant (tx; gasUsed recorded); A builds a Merkle tree of contribution hashes and anchors keccak(roundRecord) via F5 (tx). Model, round record, evidence objects, and tree are written to `traces/fl_artifacts/<run>/` as the off-chain store.

*Experiments (each a flag on the script, each producing its own trace file).*

- **E0 baseline**: N honest, no attack, reputation weighting on. Metric: error vs. round; gas per round.
- **E1 no-reputation control**: same, with w_i = n_i (plain FedAvg with trimmed mean). Metric: error vs. round; used as the comparison for every attack case.
- **E2 Sybil injection**: at round r_s, add m fresh DIDs (F1, F11, F5 — all real transactions, so the Sybil's enrolment cost is itself measured in gas) that submit updates pulling the parameter toward a target. Metric: Sybil total weight fraction per round; error vs. round with and without the cold-start cap; the smallest m at which the trimmed mean breaks in E1 vs. in E0. The trace assertion is that Σ_{Sybil} w_i / Σ_all w_i ≤ m · n_max / (c₀ · Σ_honest w_i) for every round before the Sybils have accumulated c₀ attestations.
- **E3 whitewashing**: one participant with s < θ deactivates (F4) and re-enrols. Metric: rounds until its weight recovers to the seasoned level; assertion that the deactivated DID still resolves (F2) with the deactivated flag.
- **E4 slander**: an unendorsed DID calls C1 with score 0 against an honest participant. Metric: on-chain mean (C2) vs. off-chain endorsed-attester-filtered score; assertion that the weight rule, when configured to filter by G4, is unaffected, and that the unfiltered on-chain mean is depressed (recording the scalar-cache limitation as a finding).
- **E5 aggregator drop**: A omits one valid contribution from the aggregate but (bug) includes its hash in the tree, or excludes it from the tree. Metric/assertion: the participant's dispute (F8 presentation + Merkle path check off-chain) succeeds in the first case and the exclusion is detectable in the second because the participant's signed contributionProof carries the round id and the anchored root does not contain it.
- **E6 sleeper**: one participant contributes honestly for r_h rounds then submits a norm-bounded adversarial update. Metric: its weight at the attack round, the aggregate's displacement, and the number of rounds until its off-chain recency-weighted score drops below θ versus the on-chain mean.

*Trace assertions common to all experiments.* Every tx entry has a real `gasUsed`; every C1 entry's `identity` is the attester DID and its note records the target DID and score; every round's F5 entry's note records the Merkle root; a post-run checker recomputes every root from the artifacts and every contributionProof signature against the delegate key valid (F12) at that round's block; the summary entry reports per-experiment metrics. The trace schema needs no change: C1–C4 use the existing `fnId` field (as the brief's tagging already assumes), and off-chain steps use `kind: "offchain"`.

### 9.4 What the demonstration will and will not show

It will show, with real gas, the per-round cost structure of Table 6.2 on O1 plus the harness stub; the weight-suppression effect of the cold-start cap against injected Sybils on a toy model; the audit-trail property (disputes resolvable against anchors); and the scalar-cache limitation of ISetC under slander. It will not show robustness of any real driving model to any real poisoning attack, nor the Tier 1 consumption path (that needs the cv2x-testbed's SUMO harness and an OBU), nor Layer-two ZK standing proofs (02's angle pass), nor O7-native gas.

### 9.5 The testnet and hardware path

Stage two is the same script against a public testnet or an L2 (the sidechain-anchored-to-backbone pattern of [5] maps naturally onto an L2 with periodic settlement), which replaces Hardhat's instant mining with real block times and lets the round protocol's deadline logic and the cache-staleness window be measured rather than assumed. Stage three moves the participants onto the CV2X testbed already in the repository (`cv2x-testbed/`, SUMO harness, MOBIVIDRegistry), with OBU development boards holding delegate keys, an RSU acting as A's edge cache serving F6/F12/G4/C2 snapshots, and the cooperative-perception row of Table 7.1 exercised in Tier 1 against the pre-fetched reputation snapshot — which is where the "computed slowly, consumed fast" claim gets its only real test. Stage four, after O7 is built natively, reruns S9 against O7's three registries and reports the C1/C3 gas as an option benchmark, retiring the harness figures.

## 10. Sources used in this document

| Ref | Source | Verification state | How used |
|---|---|---|---|
| [1] | C. Allen, "The Path to Self-Sovereign Identity," 2016 | VERIFIED AT SOURCE (thesis list) | Persistence and control principles (§4.1) |
| [5] | Prakash, Michelson, Feng, "CVIN: Connected vehicle information network," IEEE VTC2020-Spring | VERIFIED AT SOURCE | Latency tiers incl. "driving data for neural network training" in the high-latency tier; dual identity modes; Local CVINs; RSUs as edge servers; sidechain anchoring (§2, §4.5, §7, §8, §9.5) |
| [6] | Brecht et al., "A security credential management system for V2X communications," IEEE T-ITS 2018 | VERIFIED AT SOURCE (thesis list) | SCMS as certifying authority; pseudonym unlinkability vs reputation; misbehaviour authority (§2.5, §3.2) |
| [8] | W3C DID Core 1.0, 2022 | VERIFIED AT SOURCE (thesis list) | DID persistence and deactivation semantics (§4.1) |
| [9] | W3C VC Data Model 1.1, 2022 | VERIFIED AT SOURCE (thesis list) | Participation credential and presentation objects (§5, §6) |
| [11] | Rodriguez Garzon et al., "AI agents with decentralized identifiers and verifiable credentials," ICAART 2026 | DIGEST-LEVEL | Agent DID/VC pattern for the marketplace row (§7) |
| [15] | Weyl, Ohlhaver, Buterin, "Decentralized Society," 2022 | DIGEST-LEVEL | Non-transferability argument (§4.2) |
| [19] | De Rossi et al., ERC-8004 Trustless Agents, 2025 | DIGEST-LEVEL | Three-registry pattern; 0–100 reputation with evidence URIs; validation hooks (§5, §9.2) |
| [28] | IEEE 1609.2-2022 | DIGEST-LEVEL | Tier 1 message authentication remains SCMS (§2.2, §7) |
| NEW-1 | McMahan et al., "Communication-efficient learning of deep networks from decentralized data," AISTATS 2017 (FedAvg) | DIGEST-LEVEL | Definition of FL and sample-count weighting (§2.1, §3) |
| NEW-2 | Kairouz et al., "Advances and open problems in federated learning," Foundations and Trends in ML 2021 | DIGEST-LEVEL | Open problems: robustness, non-IID, privacy of updates (§2.1, §3.1, §8) |
| NEW-3 | Blanchard et al., "Machine learning with adversaries: Byzantine tolerant gradient descent" (Krum), NeurIPS 2017 | DIGEST-LEVEL | Krum selection rule and tolerance bound (§3.1) |
| NEW-4 | Yin et al., "Byzantine-robust distributed learning: towards optimal statistical rates" (trimmed mean, median), ICML 2018 | DIGEST-LEVEL | Coordinate-wise trimmed mean and median (§3.1, §6.5) |
| NEW-5 | Douceur, "The Sybil attack," IPTPS 2002 | DIGEST-LEVEL | Sybil impossibility without a certifying authority (§3.2, §4.3) |
| NEW-6 | Kamvar, Schlosser, Garcia-Molina, "The EigenTrust algorithm for reputation management in P2P networks," WWW 2003 | DIGEST-LEVEL | Reputation as transitive trust with pre-trusted roots; analogue of endorsed scorers (§3.4, §5) |
| NEW-7 | Chainlink decentralised oracle whitepaper | DIGEST-LEVEL | Oracle pattern for off-chain ground truth feeding scores (§7, cooperative perception and maps) |
| NEW-8 | Bagdasaryan et al., "How to backdoor federated learning," AISTATS 2020 | UNVERIFIED (not read at source) | Model-replacement / sleeper attack (§3.1, §8) |
| NEW-9 | Fung, Yoon, Beschastnikh, "The limitations of federated learning in Sybil settings" (FoolsGold), RAID 2020 | UNVERIFIED (not read at source) | Sybil updates' mutual similarity as a screen (§3.2, §8) |
| NEW-10 | Bonawitz et al., "Practical secure aggregation for privacy-preserving machine learning," CCS 2017 | UNVERIFIED (not read at source) | Secure-aggregation shares as the contribution object when update privacy is required (§6.2 step 4) |
| NEW-11 | ETSI TR 103 460 / TS 103 759 misbehaviour reporting for C-ITS | UNVERIFIED (not read at source) | Misbehaviour reporting path (§2.5) |
| Sandbox trace | `5_minimal-ssi-sandbox/traces/i2i_O1_ERC1056_1780620182135.jsonl` | VERIFIED AT SOURCE (read in full) | All measured gas figures: F5 130,163; F11 54,227; F8 62,441; F7 32,980; F1 161,823–178,935; F3 44,760; F4 55,127; F9 59,607; F10 36,478 (§5.2, §6.9) |
| Sandbox source | `contracts/interfaces/ISetC.sol`; `contracts/implementations/O7_ERC8004.sol`; `docs/ARCHITECTURE.md`; `test/compliance.js` | VERIFIED AT SOURCE | ISetC signatures and events; O7 placeholder status; S6 deferral; O1-only admission (§5, §9.1) |

## 11. Registry delta rows

| Content Block | T | Source | Ch. | Ready % | Notes |
|---|---|---|---|---|---|
| The four-link necessity chain (collective computation → reputation → identity → this system) | A | 09 §1, §3–§5 | 5, new §5.x | 80 | Argument complete; needs the S9 demonstration to cite |
| Collective-computation workloads and participant requirements (Table 2.1) | B | 09 §2 | 1 §1.2 hook; 5 | 85 | Ties 2020 paper's high-latency tier to FL |
| Robust aggregation assumes a bounded fraction; reputation keeps the adversary a minority | A | 09 §3.1–§3.4 | 5 | 80 | Krum / trimmed mean DIGEST-LEVEL |
| Verinym/pseudonym resolution of the FL-privacy vs reputation-linkability tension (Layer one / Layer two) | A | 09 §4.5 | 5; 2 (cross-ref 02) | 70 | Layer two costs owed to the ZKP angle pass |
| Requirement → function/object mapping for reputation (Table 5.1) | B | 09 §5.1 | 4 (Set C evaluation), 5 | 85 | On-chain reputation is a cache; history is the event log |
| Reputation-weighted FL round protocol with F-tags and placement (Table 6.1) | B | 09 §6.2 | 4, 5 | 75 | Design; unmeasured except F5/F8/F11 |
| Contribution proof, scoring, weighting and exclusion rules (formulae) | A | 09 §6.3–§6.5 | 5 | 75 | Parametric; c₀, θ, α are programme parameters |
| Parametric per-round gas model (Table 6.2) | B | 09 §6.9 | 4 | 60 | Only F5/F8/F11 measured; g_C1, g_C3, g_G variables |
| The chain instantiated per case (Table 7.1) | B | 09 §7 | 5 | 80 | Covers researcher checklist item 10 |
| Reputation-layer attack analysis with measurability (Table 8.1) | B | 09 §8 | 4, 5 (limitations) | 75 | Feeds Memo A "reputation dynamics" axis |
| S9 demonstration plan and ISetC harness caveat | A | 09 §9 | 4; sandbox PROPOSALS | 70 | Harness gas is not O7 gas — rule 5 |
| Set C benchmark metrics (convergence, stability, Sybil/collusion, partner selection) | B | 09 §8.1, §9.3 | 4 | 70 | Metric definitions final; values owed |

## 12. Open questions for the researcher

1. **Scalar reputation on-chain.** ISetC's `getReputation` returns only a mean and a count, which cannot express recency or attester filtering and is depressed by slander until diluted. The design treats it as a cache and computes the real score off-chain from events. Do you want to keep ISetC exactly as declared (and accept that Chapter 4's Set C benchmark measures a cache), or propose an ISetC v1.1 with a batched or attester-scoped read as a spec §6 extension? This decides whether S9's E4 result is reported as a limitation or as a resolved design point.
2. **Batching C1.** The per-round cost is dominated by k · g_C1. A single per-round attestation carrying a Merkle root of scores would collapse it, but that is an extension beyond ISetC. Is the spec §6 batch-operations extension the right home, and does the thesis want to argue that reputation writes should be batched by construction?
3. **Layer one or Layer two for the general pass.** Layer one (aggregator learns the pseudonym-to-verinym link; public sees participation fact) is buildable today; Layer two (ZK standing proof; aggregator never learns the verinym) is the privacy-correct design but depends on 02's cost figures. Which should the thesis present as the CVIN-SC position, with the other as future work?
4. **Who endorses aggregators.** The design assumes a programme authority P that endorses aggregators and validators. For a public road-authority programme P is obvious; for a fleet's private FL programme, or an open agent marketplace, P may be the fleet operator or may not exist. Should the thesis's endorsement argument (11) claim that every collective computation needs an endorsement root, or admit a root-less mode with purely economic Sybil defence?
5. **Reputation repair after key compromise.** A stolen delegate key damages an honest verinym's reputation, which is correct for accountability and unjust for the victim. Is repair a governance process outside the specification (the current position), or should the thesis propose a corrective-attestation convention?
6. **Whether to build the SetC_Minimal harness now.** It gives S9 something to call and produces real (harness) gas, at the cost of a contract that is deliberately not an option and must be labelled as such in every trace. Alternatively S9 waits for O7. Which ordering do you want in the build plan, given that O7's native three-registry build is a larger work order?
7. **The toy model.** S9 uses a linear model on synthetic non-IID shards so that convergence is observable without an ML stack. Is that acceptable for the thesis's Chapter 4 demonstration, or must the FL demonstration use a real (small) perception or traffic model to be credible to the examining committee?
