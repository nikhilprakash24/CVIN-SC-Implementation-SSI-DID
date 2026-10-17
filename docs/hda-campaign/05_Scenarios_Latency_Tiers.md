CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Latency-Tier Scenarios: Six Cases, Three Budgets, One Rule**

**A CAV case and an AI-agent case for each of the three latency tiers, showing that the tier does not change which functions exist but dictates which read path is admissible — and therefore what must already be in the verifier's hands before the interaction begins**

Document 6 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · October 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose / Type B tables-data → Chapter 2, §2.4 (three-tier framework, contribution C6); Chapter 4, §4.4 and the latency subsection of §4.6*

> **Two notices.** (1) **Nothing in this document is a latency measurement.** Every figure below is a *budget* — an allocation of a tier's allowance across named components — or an external figure carrying its label. The suite's measured quantities are gas, and gas is not latency. *Updated 2026-10-15:* Slice 1 step 1c has since added `latencyMs` to the trace emitter and `traces/SCHEMA.md` (schema v1.1, additive), so the **instrumentation** now exists and the scripts will yield comparable numbers on Besu QBFT. The values recorded on the Hardhat in-process network are a **lower bound on any real network** and are explicitly not reported as results (10 Addendum B §1c), so this notice stands unchanged in substance: the document is still budgets, not measurements, and §7 is still the path to results. (2) **Naming.** The register in 00 §6 lists these six scenarios as "T1/T2/T3-CAV, -AGT", which collides with the typing tags T1 `declare` and T2 `verifyTyped` used throughout 04 and 10. This document therefore writes them **TS1-CAV, TS1-AGT, TS2-CAV, TS2-AGT, TS3-CAV, TS3-AGT**, and the collision is logged for S3 as correction K-HDA-9.

---

## 1. The tier contract

### 1.1 Claim

The three-tier latency framework is contribution C6 and it is usually read as a statement about *where distributed ledger technology may be used*. That reading is correct but shallow, and it has a cost: it makes the tiers sound like a feasibility filter applied from outside, when they are in fact a structural constraint that reaches all the way down into the data architecture. The deeper statement, which this document argues through six cases, is this.

**The latency tier does not change which of the twenty-three operations a scenario needs. It changes which *read path* is admissible. And because a read path is admissible only if the data it reads is already where it needs to be, the tier determines what must have been pre-positioned before the interaction starts — which is a data-placement decision, made at a different tier, possibly months earlier.**

Three consequences follow, and they are the spine of the document. First, **every tier uses the same functions**; Tier 1 does not use a smaller interface, it uses the same interface at a different time. Second, **the real design work for a fast tier happens in a slow tier**: the Tier 2 gantry decision is fast because a Tier 3 endorsement, a Tier 3 credential issuance, and a Tier 3 cache warm-up already happened. Third, **the coupling between tiers is a single parameter** — the staleness window — and the build measured its consequence rather than its size: a cached verifier accepted a revoked credential until it refreshed (finding F-VID-3, trace S7 seq 50). The tiers are not three independent regimes; they are one regime with one dial, and the dial is the security parameter nobody in the literature sets explicitly.

### 1.2 The tiers, as the programme already states them

| Tier | Budget | Thesis framing (C6) | 2020 paper's wording [5] | DLT stance |
|---|---|---|---|---|
| **Tier 1** | <100 ms | BSM and collision avoidance; SCMS (IEEE 1609.2) governs | Collision avoidance, basic safety messages, advanced navigation | **Explicitly out of scope** for any ledger |
| **Tier 2** | 100–500 ms | Cooperative operations: charging initiation, toll authorisation, parking credential exchange, V2I service registration, cooperative manoeuvre negotiation | Tolling, parking, smart EV charging, gated and restricted-area access | **The primary target**, viable if edge-deployed |
| **Tier 3** | >500 ms | Administrative: registration, type approval, operator licence, fleet management, insurance, history | Legal, finance, insurance, immutable vehicle history, driving data for neural-network and autonomous-driving training | Any DLT profile |

The two wordings differ in an instructive way. The 2020 paper's Tier 3 includes "driving data for neural-network and autonomous-driving training" — that is, the federated-learning case of 09 — which the thesis's administrative framing drops. Restoring it matters, because it is the tier's largest future workload and the one for which reputation is a precondition. This document restores it in §4.2 and 09 takes it up in full.

### 1.3 What consumes a tier's budget

A tier's allowance is spent on a sequence whose components are separable, and keeping them separate is what allows an honest design argument in the absence of measurements. For an interaction between a presenting principal and a verifier:

| Component | Symbol | What it is | Who controls it |
|---|---|---|---|
| Channel establishment | *t*<sub>ch</sub> | ECDH key agreement and AEAD session setup (08 §1); amortised if the session persists | Design: session reuse |
| Presentation construction | *t*<sub>pres</sub> | Building and signing the VP off-chain; with selective disclosure, the proof cost | Design: proof system (02) |
| Signature and disclosure verification | *t*<sub>ver</sub> | Local cryptography at the verifier | Hardware |
| Local state lookup | *t*<sub>cache</sub> | Reading F6 / F12 / G4 / T2 results from cache | Design: cache policy |
| **Chain read** | *t*<sub>read</sub> | A live view call: network round trip plus node execution | Deployment: node locality |
| **Chain write and finality** | *t*<sub>fin</sub> | Transaction submission, inclusion, and the declared finality depth | Consensus: not negotiable |
| Policy evaluation | *t*<sub>pol</sub> | The verifier's decision logic | Design |

The design rule that all six scenarios obey falls straight out of the table: *t*<sub>fin</sub> is the only component measured in seconds on a public chain and is therefore excluded from Tiers 1 and 2 absolutely; *t*<sub>read</sub> is the only component whose magnitude depends on where a node is, and is therefore the component that edge deployment (the 2020 paper's RSU-as-edge-server, MEC/5G-aware consensus, and Local CVIN sharding [5]) exists to shrink; and *t*<sub>cache</sub> is the component that replaces *t*<sub>read</sub> when even an edge read is too slow. **Tier 1 admits only *t*<sub>ver</sub> and *t*<sub>pol</sub>. Tier 2 admits those plus *t*<sub>cache</sub>, and *t*<sub>read</sub> only against an edge node. Tier 3 admits everything.**

### 1.4 The read-path ladder

01 §4 sets out the read paths; here they are ranked by the tier each can serve. This ladder is the operational content of the whole document.

| Rung | Read path | What it proves | Admissible at |
|---|---|---|---|
| 0 | **Fully offline**: verify the issuer's signature over the typed anchor using a DID document the verifier already holds | Integrity, issuer binding, type, claims | Tier 1, 2, 3 |
| 1 | **Cached state**: rung 0 plus F6 / F12 / G4 / T2 results from a local copy with a recorded fetch height | The above plus status and entitlement *as of the fetch* | Tier 1 (pre-positioned), 2, 3 |
| 2 | **Edge read**: a live view call to a co-located or regional node | The above, current to the node's head | Tier 2, 3 |
| 3 | **Remote read**: a live view call to a distant node | Same, slower | Tier 3 |
| 4 | **Write-then-read**: submit a transaction and wait for the declared finality depth | A state change has durably occurred | Tier 3 only |

The build demonstrated rung 0 twice: three credentials verified for integrity and issuer binding with **zero chain reads** from a warmed cache (trace S7 seq 32–34), and eleven lifecycle credentials verified the same way (S8 seq 60). That is the single most important observation in this document, because it establishes that the bottom rung of the ladder — the only rung Tier 1 can use — is not hypothetical. It also establishes the rung's exact weakness in the same breath: at S7 seq 50 the same cached verifier accepted a credential that had been revoked on-chain, and needed an F6 read at seq 51 to correct itself. Rung 0 proves everything except the one thing only the chain knows.

Slice 2(b) confirmed that from a second, independent direction. A BBS+ proof **proves issuance, not currency**: after the credential is revoked with F7 the proof still verifies correctly, and only an F6 read reveals the revocation (finding F-VID-14). So the limitation is not an artefact of caching — it is a property of offline verification as such, and no improvement in the proof system removes it. Every rung-0 design in this document therefore carries the same irreducible exposure, and the staleness window is the only thing bounding it.

---

## 2. Tier 1 (<100 ms): identity is pre-positioned, or it is absent

### 2.1 The tier's rule

Below 100 ms there is no chain, no cache refresh, and no negotiation. There is a message, a signature, and a decision. The identity system's role is therefore not to participate but to have *already* participated: everything the Tier 1 verifier will need must be in its memory before the safety-critical moment, and the system's actual contribution to Tier 1 is made at Tier 3, in the form of the material that was distributed, and after the fact, in the form of the accountability record.

This is not a concession. It is the thesis's "extension, not replacement" stance made precise: SCMS (IEEE 1609.2) authenticates the basic safety message in the Tier 1 window and SSI does not try to; SSI supplies what SCMS structurally cannot, which is the ability to answer later what the history of actions taken by a particular vehicle was. Saying that the ledger is out of scope for Tier 1 and then describing what the identity layer nonetheless does for Tier 1 is more useful than either claiming the tier or abandoning it.

### 2.2 TS1-CAV — Cooperative emergency braking in a platoon

**Setting.** Four vehicles in a cooperative platoon on a highway. The lead vehicle detects an obstruction and broadcasts a cooperative braking intent. Each follower must act within the Tier 1 budget. A wrongly accepted message causes a phantom brake and a collision; a wrongly rejected message causes a collision.

**Actors.** Vehicles *V₁…V₄*, each with an OBU holding (a) an SCMS pseudonym certificate for BSM authentication and (b) a `sigAuth` delegate grant from its vehicle DID (F11, 54,227 gas measured, granted at Tier 3). A platoon-coordination RSU, delegate of the road operator. A `PLATOON_ELIGIBILITY` credential issued at Tier 3 by the operator to each vehicle, attesting that its automated driving system is of a class certified for cooperative braking.

**Objects and where they are at the moment of braking.** In each follower's memory, placed there during platoon formation: the lead's DID document (verification methods), the lead's `PLATOON_ELIGIBILITY` credential *body* and the issuer's signature over its typed anchor, the F6 / G4 / T2 results for that credential with their fetch height, and the session keys of the pairwise I2I channel. On-chain, untouched during the event: the DIDs, the grant, the anchor, the endorsement. **The chain is not read and not written inside the window.**

**Function sequence, split by tier.** This split is the point of the scenario.

- *Tier 3, at platoon formation (seconds to minutes, and off the critical path):* each vehicle presents over the channel — off-chain VP over `PLATOON_ELIGIBILITY` with selective disclosure of the certification class only; each verifies with rung 2 or 3, F6 and F12 and G4 and T2 live; F8 is committed in batch afterwards, not inside formation; each vehicle **caches** the others' DID documents and verification results, recording the fetch height and the staleness window it has agreed to.
- *Tier 1, per safety message (the window):* the message carries the SCMS pseudonym signature for authentication and a second signature under the lead's `sigAuth` delegate key binding the message to the vehicle DID whose eligibility was verified at formation. The follower checks both signatures against material it already holds — rung 0 — evaluates policy, and brakes. Components spent: *t*<sub>ver</sub> and *t*<sub>pol</sub>. Components not spent: everything else.
- *Tier 3, after the event:* the braking event, the messages, and the decisions are bundled, rooted, and anchored with a single F5 (130,151 gas measured for the no-expiry form — one write for the whole event, by the batching result of 10 §5.3). This is the accountability record, and it is the only on-chain trace the event leaves.

**Why the double signature, and the honest cost.** The SCMS signature says "a certified, unrevoked C-ITS station sent this"; it deliberately does not say which vehicle, because pseudonymity is the point. The delegate signature says "the vehicle whose eligibility you verified at formation sent this". Both are needed, and carrying both costs calldata, airtime, and a second verification in the tightest budget in the system. Whether that cost is affordable is an **open empirical question this document cannot answer**: it needs the signature-verification cost of the target OBU hardware and the available airtime, which is Slice 4 of 00 §7 on the AURORA testbed. If it is not affordable, the fallback is that the eligibility binding is checked only at formation and the Tier 1 messages carry SCMS alone — which weakens the accountability claim from per-message to per-session, and that weakening should be stated in the thesis rather than discovered by a reviewer.

**Failure modes.** *Replay of a braking message* is defended by the message's own sequence number and timestamp, not by F8 — F8 cannot be in this window. *Revocation during the platoon*: the lead's credential is revoked on-chain mid-journey, and every follower's cache is stale. This is finding F-VID-3 in the worst place it can occur, and it is the subject of 08's revocation-propagation crux; the mitigation is an out-of-band revocation push over the established channels, which converts a cache-staleness problem into a message-delivery problem and does not eliminate it. *Key compromise of the lead's delegate key* within the session is bounded by the grant's validity, which is why formation grants should be short. *Partition* has no effect, because nothing in the window needs the network beyond the direct link — the one respect in which Tier 1 is the most robust tier rather than the most fragile.

**Problems solved, and further functionality.** The accountability gap is closed for the event: a post-incident investigator can establish which vehicle sent which message, under which key, with which certified capability, from an anchored bundle — while no roadside observer learned the vehicle's identity at the time. Extensions: the same pre-positioning pattern serves cooperative manoeuvre negotiation and intersection crossing; the anchored event bundles are training data for cooperative-perception models, which is the federated-learning connection (09 §7) and the 2020 paper's own Tier 3 "driving data for neural-network training".

**Demonstration hook.** Proposed script `scenarios/run_tier1_platoon.js` (TS1-CAV). The honest assertion is structural, not temporal: assert that between the formation `summary` entry and the post-event F5 there is **no** `kind=tx` and **no** `kind=view` entry — that is, that the Tier 1 window touches neither chain state nor chain reads — and that the post-event anchor's `credentialHash` equals the keccak of the event bundle logged off-chain. Timing instrumentation now exists (schema v1.1, Slice 1c), but a Tier 1 latency claim requires OBU hardware over a real radio and nothing short of it; the structural assertion is what can be evidenced now, and it is worth having, because "no chain access in the window" is the architecturally load-bearing claim and it is checkable today.

### 2.3 TS1-AGT — The in-loop safety veto

**Setting.** A control agent issues actuation commands to industrial or vehicular equipment at a fixed cycle; a separate, smaller **guardian** agent holds a veto and must exercise it within the cycle. The budget is the control cycle, which may be well under 100 ms.

**Actors.** Control agent *A*<sub>c</sub> and guardian *A*<sub>g</sub>, both delegates of operator *O* (F11), each holding an `AGENT_CAPABILITY` credential from an endorsed certifier (04 §3.4) and, for the guardian, a `SAFETY_AUTHORITY` credential naming the equipment classes over which its veto is valid.

**Sequence.** At startup, Tier 3: mutual verification at rung 2, caching of DID documents, credentials, and F12 / F6 / G4 / T2 results; a long-lived authenticated channel. In the loop, Tier 1: the actuator accepts a command only if it carries *A*<sub>c</sub>'s signature and no veto token from *A*<sub>g</sub> for that cycle; the guardian's veto is a signed token verified at rung 0. After the fact, Tier 3: the cycle log is rooted and anchored periodically.

**The one structural difference from the vehicle case, and it matters.** A vehicle's Tier 1 counterparties are *strangers encountered at speed*; an agent's are usually *processes started by the same operator*. The agent case can therefore pre-position its trust material with certainty, because the operator controls both ends, and the hard problem — establishing trust with an unknown counterparty inside a 100 ms window — does not arise. The honest conclusion is that **Tier 1 for agents is mostly easy for a reason that does not generalise**: it is easy when the principal is shared, and when it is not (an agent accepting a real-time veto from another organisation's guardian), it is exactly as hard as the vehicle case and has the same answer, pre-positioning at Tier 3.

**Failure modes.** A *stale guardian capability* has the same shape as the stale platoon credential, with the same push mitigation. *A withheld veto* — the guardian is silenced by a network fault — must fail safe, which is a control-system property and not an identity property; the identity layer's contribution is that the silence is attributable, because the anchored cycle log shows the gap. *Prompt injection* of the control agent is outside the identity layer's reach (04 §3.11), and the layer's contribution is again containment and attribution rather than prevention.

**Problems solved, and further functionality.** The veto becomes auditable without becoming slow, which is the general form of what the identity layer offers any real-time system. Extensions: the same pattern is the enforcement point for agent-mediated tolling and pay-as-you-use road charging at Tier 2 (§3), and the anchored cycle logs are the per-agent evidence base from which reputation is computed at Tier 3 (04 §3.8, 09).

### 2.4 What Tier 1 establishes

That the identity system's contribution to the fastest tier is entirely a matter of *when* its work is done, not *whether*. Both cases spend their budget on two components only, both rely on rung 0, both pre-position at Tier 3, and both leave a single batched anchor behind. Neither reads nor writes the chain inside the window, and both would be broken by a revocation that arrives during the window — which is why the revocation-propagation crux of 08 is the correct place for the programme's attention, and why the staleness window is the parameter this document keeps returning to.

---

## 3. Tier 2 (100–500 ms): decide from signatures and cache; write afterwards

### 3.1 The tier's rule

Tier 2 is the tier the thesis is *for*. It is wide enough to admit a verification but not a consensus, and the operations in it — toll authorisation, charging initiation, parking and gated-area credential exchange, V2I service registration — are exactly the operations for which a pseudonymous SCMS certificate is insufficient (they involve money, entitlement, or access) and a chain write is impossible.

The rule has two halves, and the second is more often forgotten. **No Tier 2 decision waits for a chain write.** And: **a Tier 2 decision may read the chain only against an edge node, and must degrade to cache when it cannot.** A design that is correct only when the regional node answers in 40 ms is a design that fails in a tunnel, and the low-connectivity scenarios of 06 §5 are the same design under the degradation this rule requires.

### 3.2 TS2-CAV — Entry to a restricted zone at speed

**Setting.** A low-emission zone with free-flow enforcement: no barrier, cameras and an RSU, vehicles entering at 50 km/h. The verifier must decide, within the budget, whether a vehicle is entitled to enter and whether a charge applies. At 50 km/h a 500 ms budget is about 7 m of road, which is the physical reason the budget is what it is.

**Actors and objects.** Vehicle *V* with OBU delegate; zone authority *Z*<sub>LEZ</sub> and its RSUs (F11 delegates); ministry *M* endorsing *Z*<sub>LEZ</sub>; an `EMISSIONS_COMPLIANCE` credential (the schema already exists in `2_w3c-ssi-layer`'s UC set) and the `VEHICLE_REGISTRATION` of 04 §2.4; a receipt, if a charge applies; the settlement root.

**Sequence within the budget.** Channel (reused if the vehicle has been here before, so *t*<sub>ch</sub> is often zero); off-chain VP over the emissions credential with selective disclosure of the emissions class and validity only — not the plate, not the owner, not the registration body; verification at rung 0 for integrity, issuer binding, and claims; rung 1 for status and entitlement from the cache, with an opportunistic rung 2 refresh *in parallel with* the decision rather than before it; policy; open. Outside the budget, at Tier 3: the receipt is appended to the epoch bundle and the root is anchored once with a single F5 — the batching pattern, with the per-passage on-chain cost being the measured 130,151 gas divided by the number of passages in the epoch, which is arithmetic on a measured value and not a measurement of the scenario.

**The budget, as an allocation rather than a measurement.**

| Component | Allocation | Basis |
|---|---|---|
| *t*<sub>ch</sub> | 0 for a reused session; otherwise the dominant cost | 08 §2 |
| *t*<sub>pres</sub> + *t*<sub>ver</sub> | The scenario's irreducible cryptographic core | **Measured 2026-10-15** on BBS+ (10 Addendum C): 93/66 ms for full disclosure, 107/59 ms for class-plus-validity, **116/116 ms for the most selective policy** — laptop, WASM, not an OBU. Compare VehiclePassport's 22 ms generation and sub-5 ms verification (**DIGEST-LEVEL**, arXiv:2509.06133), which is 4–5× faster. A plain signature plus salted-digest disclosure remains cheaper than either |
| *t*<sub>cache</sub> | Local memory | Design |
| *t*<sub>read</sub> | **Must fit, or be moved off the critical path** | Deployment; the RSU-as-edge-server stance [5] |
| *t*<sub>fin</sub> | **Excluded** | Consensus |
| *t*<sub>pol</sub> | Verifier logic | Design |

The allocation shows where the engineering risk actually is, and it is not where a reader might expect. The problem is *t*<sub>ch</sub> on a first encounter and *t*<sub>read</sub> when the node is not local. Both are deployment and session-management problems, and that is a useful finding for a thesis whose instinct is to treat the proof system as the bottleneck.

**Correction to the above, 2026-10-15 — the first time this suite's own measurement contradicted its own argument.** When this section was written, the only figure available was VehiclePassport's 22 ms generation and sub-5 ms verification, and the conclusion drawn was that "the cryptography is not the problem… comfortably inside the budget." Slice 2(b) then measured BBS+ on the suite's own credential objects and got **93–116 ms to generate and 59–116 ms to verify** (10 Addendum C) — on a laptop, in WASM, with no radio and no OBU. For the most selective policy that is **232 ms of a 500 ms Tier 2 allowance, before the channel, the cache read, or the policy evaluation**, and the ceiling of the tier is no longer comfortable; at the 100 ms end of the tier it does not fit at all.

Three things follow, and the first is the honest one. (i) **The sentence "the cryptography is not the problem" is withdrawn for the ZK path.** It stands for the signature-plus-salted-digest path, which is what the build's default actually uses and which is cheaper than both figures; the correction is specifically about BBS+ and any proof system of that weight. (ii) The gap between 22 ms and 116 ms is a 4–5× discrepancy between an external figure and an internal one for nominally the same kind of operation, which means **H47 should not be used as a bound at all** — it is a different implementation, on different hardware, for a different proof, and S1 §5.1 item 3 already flagged it as the suite's single most load-bearing unverified figure. (iii) There is a perverse relationship in the measurements: **proof size and proof time both rise as disclosure falls** (findings F-VID-13 and the timings above), so the most privacy-preserving policy is also the slowest and the largest. Privacy is not free at Tier 2, and the tier's budget is where the bill arrives. That is a sharper and more defensible claim than the one it replaces, and it is a thesis-grade result rather than a caveat.

What this does not license is the opposite overstatement. WASM on a laptop is not an OBU, and a native implementation on purpose-built hardware could plausibly move either way. The disciplined conclusion is that **the cryptographic core can no longer be assumed negligible in the Tier 2 budget, and the policy-to-latency relationship must be measured on target hardware before any tier claim is made for a ZK path** (Slice 4; §7 step 5).

### 3.2.1 The disclosure ladder, priced (2026-10-15, Slice 2 complete)

Stage (c) then measured the third path, and the three now sit side by side on the same driver's licence credential. This table is the single most consequential thing in this document, because it converts the choice of disclosure mechanism from a privacy preference into a **tier eligibility constraint**.

| Path | What the verifier learns | Generate | Verify | On-chain | Tier 2 eligible? |
|---|---|---|---|---|---|
| Hash + signature (build default) | The whole credential | negligible | negligible | F8 62,441–62,574 | **Yes** |
| BBS+ selective disclosure (S19) | Chosen claims only | 93–116 ms | 59–116 ms | F8 62,470 | **Marginal** — 232 ms of 500 ms at the most selective policy; fails at the 100 ms end |
| Groth16 predicate (S20) | Only the predicate's result | **3,999.9 ms** | **645.3 ms** off-chain (cold); 0 gas as a view; **250,283 gas** as `admit` | F8 62,458 alongside | **No, not generated in-band.** Proving alone is 8× the whole tier |

Three readings, in order of how much they change the thesis.

**(i) Proving, not verifying, is the Tier 2 problem — and that inverts the usual framing.** The literature's attention, and this suite's own earlier attention, went to on-chain verification cost; the measured answer is that verification is affordable (250,283 gas as a transaction, which is about twice a credential anchor, or **nothing at all as a view**) while *generation* is 4 seconds. Proving is more expensive than verifying by roughly two orders of magnitude (finding F-VID-16). A design that worried about verifier gas was worrying about the cheap end.

**(ii) The consequence is a placement decision, which is this suite's native idiom.** If a predicate proof cannot be generated inside the tier that needs it, then it must not be generated there. Three placements follow, and they are design options rather than measurements:

- **Pre-computation at a Tier 3 epoch.** The holder generates the proof when it has time and power — at issuance, overnight, on a charger — and presents it later. This works precisely when the predicate and its public signals are known in advance and stable: "holder is over 18" is stable for life; "holder is over 18 *and this nonce*" is not, so the freshness binding has to come from somewhere cheaper, which is the channel (08) rather than the circuit.
- **A delegated prover.** The OBU hands the witness to a trusted edge prover. This defeats the point unless the prover is the holder's own equipment, because the witness contains the secret; it is viable for a fleet with a depot server and not for a private vehicle at a gantry.
- **Don't use a predicate proof at Tier 2.** Use BBS+ or the hash path, and reserve predicates for Tier 3 admission decisions that are made once and cached — which is exactly what the measured `admit` transaction models.

**(iii) It sharpens the privacy-latency claim rather than reversing it.** §3.2's correction said proof size and time both rise as disclosure falls. Stage (c) extends that to the strongest privacy mechanism and the relationship holds at a far steeper slope: revealing *only a predicate's result* costs four seconds of proving. **Privacy is purchasable at every tier, but the currency changes** — at Tier 3 it is gas and proving time, at Tier 2 it is pre-computation and the staleness that pre-computation implies, and at Tier 1 it is unavailable at any price, which is why TS1 pre-positions everything (§2.1).

Two cautions, both load-bearing. The 645.3 ms off-chain verification is a **cold first call** in snarkjs; a warm verifier is ordinarily far faster, and **the warm figure was not measured** — which matters, because if warm verification is tens of milliseconds then the pre-computation placement above is viable at Tier 2 and the whole predicate path is rescued for gated access. That single unmeasured number is now the most decision-relevant quantity in this document. And the circuit has no revocation input, so a predicate proof shows the holder satisfied the predicate at proving time and says nothing about currency — F-VID-14's limitation (§1.4), now compounded by the pre-computation placement, since a proof computed last night is a night stale by construction.

**The parallel-refresh pattern, and what makes it sound.** Issuing the rung-2 read *concurrently with* the decision rather than before it removes *t*<sub>read</sub> from the critical path entirely, at the price of a decision made on state that may be one refresh out of date. It is sound only because the consequence is bounded and reversible: a vehicle wrongly admitted to a zone is billed at Tier 3 when the refresh lands, or is flagged for enforcement. The pattern would be unsound for an irreversible action, and the general rule — **a Tier 2 decision may be made on stale state exactly when the action it authorises can be unwound or priced at Tier 3** — is the cleanest statement this document has of why Tier 2 works at all. Gated access with a physical, irreversible consequence (a secure depot gate) does not qualify, and 06 §4 treats it accordingly.

**Failure modes.** *Stale acceptance* is the designed-for case, priced as above; the window's size is the policy decision, and F-VID-3 is the evidence that it is real. *Revoked entitlement inside the window*: the zone authority's push channel narrows it; nothing closes it. *Replay at a second gantry* is defended by binding the challenge to the zone identifier and a time bucket. *Operator equivocation* on receipts is caught at Tier 3 by the anchored root. *Partition*: the RSU falls to cache-only and continues, which is the degraded mode of 03 §5 and the whole point of designing the read path as a ladder.

**Problems solved, and further functionality.** This is pay-as-you-use road pricing in its cleanest form: the vehicle proves class and compliance, the charge is computed off-chain, the receipt is anchored in a batch, and the jurisdiction never receives a trip record — the privacy argument of 06 §3.2, which is what makes distance-based charging politically tractable. Extensions: the same exchange carries road-condition reports in the opposite direction at no additional protocol cost, since the channel is already open and authenticated, and those reports are the reputation evidence of 04 §2.8 and the training input of 09.

**Demonstration hook.** `scenarios/run_tier2_zone.js` (TS2-CAV). Assertions: no `kind=tx` between channel open and the entry decision; the decision entry records which rung it used and the cache's fetch height, so that a stale decision is *visible in the trace* rather than inferred; N passages produce exactly one F5; an injected revocation between fetch and decision produces an admitted-then-billed outcome and a trace entry marking it — which makes the parallel-refresh pattern's failure mode an observation rather than a caveat. Metric: rung distribution across decisions, and the count of decisions made at each staleness age.

### 3.3 TS2-AGT — Tool-call authorisation inside an agent's action loop

**Setting.** An agent calls an external tool. The budget is set not by physics but by the agent's own loop: a 400 ms authorisation inside a reasoning step that takes seconds is invisible, and the same 400 ms inside a loop making thousands of calls a minute is the system's throughput limit. **Tier 2 for agents is a throughput budget, not a safety budget**, and that single difference reshapes the design.

**Actors and objects.** Agent *A* and sub-agent *A₂* (04 §3); tool provider *S*; `AGENT_CAPABILITY`, `DELEGATION_SCOPE`, `SPENDING_MANDATE` credentials; the chained delegate grants *O*→*A* and *A*→*A₂*.

**Sequence.** Session established once and reused for thousands of calls, so *t*<sub>ch</sub> amortises to nothing — the single largest structural advantage the agent case has over the vehicle case, whose counterparties change every few hundred metres. Per call: the scope and budget predicates are evaluated against credentials and the agent's own signed spend ledger, at rung 0; status and entitlement come from cache at rung 1, refreshed on a schedule rather than per call; the chained F12 checks are cached; F8 is batched to Tier 3; policy decides.

**The throughput consequence.** Because the budget is throughput rather than safety, the correct optimisation is the opposite of the vehicle case's. A vehicle minimises latency per interaction and accepts per-interaction cost; an agent minimises *per-call work* and will accept higher latency on the first call of a session to do so. Concretely: verify the chain once per session rather than once per call, cache aggressively, batch every commitment, and make the per-call path a pure signature-and-predicate evaluation with no lookups at all. The staleness window is correspondingly *longer* for agents and the exposure *larger*, because a session may make a hundred thousand calls under a credential state checked once — which is why the mandate's ceiling matters so much: it bounds the damage of a stale authorisation in a way the vehicle case's zone entry does not need.

**Failure modes.** *Stale scope* across a long session, bounded by the mandate ceiling and by a maximum session age that the provider, not the agent, sets. *Runaway loop*: an agent in a defective cycle exhausts its mandate; the ceiling is the control, and the provider's rate limit is the backstop — neither is an identity mechanism, and claiming otherwise would overstate the layer. *Confused deputy* across the chained delegation is the attenuation gap of 04 §3.5 and is the one failure here that the identity layer should close and currently cannot. *Replay* is defended by per-call nonces in the channel, not by F8.

**Problems solved, and further functionality.** An unknown agent gains metered access to a paid API on evidence rather than on a shared secret, with spending bounded by a credential its principal can revoke with one F7. Extensions: the same per-call path is the admission control for a federated-learning round — a participant presents capability and scope, the coordinator admits at rung 1, and the round proceeds — which is 09's mechanism, and the per-call economy described here is why an FL round with thousands of participants is feasible at all.

### 3.4 What Tier 2 establishes

Both cases make the decision without touching the chain, both defer every write, and both are correct only because the staleness window is bounded and the authorised action is reversible or priced. The two differ in what the budget is for — safety against throughput — and that difference inverts the optimisation: per-interaction minimisation for vehicles, per-call minimisation for agents. The shared conclusion is the suite's design slogan in its most defensible form: **the chain is consulted on a schedule, not on demand, and never on the critical path.**

---

## 4. Tier 3 (>500 ms): the chain is in the loop, and everything expensive happens here

### 4.1 The tier's rule

Tier 3 has no latency constraint worth designing around, so its rule is about something else: **Tier 3 is where every cost the faster tiers refused to pay is paid.** Every endorsement, every credential issuance, every batched anchor, every presentation commitment, every reputation attestation, every cache warm-up, and every revocation lands here. The tier is not the least interesting; it is where the architecture's entire write load lives, and therefore where its scalability is decided.

This re-framing has a consequence for the thesis's evaluation chapter. The measured gas figures of 10 §5 are **all** Tier 3 figures. There is not a single Tier 1 or Tier 2 gas number in the suite and there cannot be, because those tiers do not write. So the cost evaluation and the latency evaluation are measuring different tiers, and any sentence that puts them side by side must say so.

### 4.2 TS3-CAV — Ownership transfer, underwriting, and the training corpus

**Setting.** Three administrative operations that the vehicle's owner experiences as taking minutes to days: transferring title, renewing insurance, and contributing driving data to a model-training programme.

**Sequence (the first two are 04 §2.9 and §2.8 and are not repeated; what is added here is the tier analysis).** Transfer is a sequence of writes — F7 at 32,968 gas, F1 for the new owner at 161,823–178,935, F5 with expiry at 150,087, T1 at 150,463, F10 at 36,454, F9 at 59,595, all measured on O1 — whose *total* is the number the thesis should quote for the operation, and whose *latency* is dominated not by consensus but by the administrative process around it. The honest observation is that for Tier 3 the ledger is almost never the slow part: a registrar's business process takes a day and a block takes seconds. That is worth stating because it reverses the intuition that blockchain is slow; it is slow relative to a 100 ms safety window and fast relative to every Tier 3 process the thesis actually examines.

Underwriting adds the C2 read of reputation (04 §2.8) and is interesting at this tier for a different reason: it is the first operation whose *input* is an aggregate over the whole history, so it is the first operation whose cost depends on the history's volume. Because the history is off-chain and batched, that cost is borne by the insurer's indexer and not by the chain — which is the placement argument paying off in the one place a sceptic would expect it to fail.

The training corpus restores the 2020 paper's own Tier 3 item. A vehicle contributes driving data for neural-network and autonomous-driving training; the contribution is an off-chain bundle, the bundle is rooted, the root is anchored, and the contributor's reputation weights its contribution in whatever aggregation consumes it. This is federated learning with the words changed, it belongs at Tier 3 by the paper's own classification, and 09 is its full treatment. Naming it here matters because the thesis's administrative framing of Tier 3 currently omits the tier's largest future workload.

**Failure modes.** *Non-atomicity* of transfer (04 §2.9) is a Tier 3 phenomenon and is managed by making the interval visible rather than by removing it. *Reorganisation* before the declared finality depth is the only tier where this is a live concern, because it is the only tier that writes; 03 §6 sets the depth. *Revocation storms* — a batch of credentials revoked at once, scenario S18 — are a Tier 3 write-load problem and the reason the tier's throughput matters.

**Problems solved, and further functionality.** Immutable vehicle history, title, and insurance are the 2020 paper's Tier 3 list, and the measured build already covers the credential machinery for all of them (10 §3). Extensions: toll and road-use *settlement* (as distinct from authorisation) is a Tier 3 batch; road-condition reporting *scoring* is a Tier 3 epoch close; federated learning is a Tier 3 round. Every "further functionality" item in the brief's checklist resolves to a Tier 3 write and a Tier 2 read, which is a tidy and slightly surprising summary of the whole scenario programme.

### 4.3 TS3-AGT — Onboarding and capability certification

**Setting.** A new agent is brought into service: the operator is verified as a legal entity, the agent is created, certified, endorsed, registered in a marketplace, and given a mandate. This is 04 §3.3–§3.5 and the tier analysis is what is added.

Every operation is a write, and the sequence is the most write-heavy in either story: F1, F9, F11, F5 ×3, T1, G1, G2, F3. On the measured O1 figures that is on the order of a million gas for one agent, which is the figure that makes the §2.4 conclusion of 04 — ephemeral agents must not have DIDs — quantitative rather than aesthetic. Onboarding is slow and expensive and happens once; the agent then operates for its whole life at Tier 2 for free. **The agent architecture is economically viable precisely because its cost is front-loaded into a tier with no latency constraint**, and the design failure to avoid is any pattern that moves onboarding-class work into the operating loop.

**Failure modes.** *Certifier compromise* is the G3 case and its consequence is measured (F6 valid, G4 false — trace S7 seq 53). *Onboarding as a denial-of-service vector*: an attacker drives up the registry's state by onboarding agents. The participation cost *is* the defence, and the figure above is that cost; this is the Sybil argument of 06 §2.2 arriving from the agent side.

---

## 5. The parameters that couple the tiers

| Parameter | What it couples | Set by | Evidence state |
|---|---|---|---|
| **Staleness window** | Tier 2 and Tier 1 decisions to Tier 3 revocation | Verifier policy | Consequence measured (F-VID-3); size unmeasured |
| **Revocation propagation delay** | Tier 3 writes to Tier 1/2 caches | Push infrastructure | Unmeasured; 08's crux |
| **Finality depth** | Tier 3 writes to anything that relies on them | Consensus choice | Design parameter; 03 §6 |
| **Cache warm-up scope** | What Tier 1 can do at all | Tier 3 pre-positioning | Demonstrated at rung 0 (S7 seq 32–34, S8 seq 60) |
| **Batch epoch length** | Tier 2 event volume to Tier 3 write cost | Operator policy | Ratio measured at 11:1 via F5, and **11.72:1 via the dedicated `anchorBatch`** which also keeps on-chain inclusion (10 §5.3; Addendum A §1) |
| **Session lifetime** | Per-call cost at Tier 2 to staleness exposure | Provider policy | Unmeasured |

Three of six are measured, in the sense that their *consequence* or *ratio* has been observed; **none has a measured magnitude in time.** That remains true after Slice 1: timing is now instrumented, but only on an in-process network whose values are a lower bound (notice 1). The staleness window's consequence has since been observed a second time and in a more operationally pointed form — S14 reproduced stale acceptance under a simulated partition and then showed the reconciliation outcome, "revocation wins", with the admitted toll pass denied at settlement (finding F-VID-9). Setting these parameters is the deployment design task; measuring their magnitudes is Slices 3 and 4. The table is offered as the agenda rather than as a result.

## 6. What breaks each tier

**Tier 1** breaks when the trust material was not pre-positioned — a stranger encountered at speed with no prior session — and when a revocation lands inside the window. Neither has a cryptographic remedy; the first is answered by formation protocols, the second by push and by accepting a bounded exposure.

**Tier 2** breaks when the authorised action is irreversible and the state is stale, and when *t*<sub>ch</sub> cannot be amortised because counterparties never repeat. The first is a policy error and is avoidable by the rule in §3.2; the second is a deployment property and is what RSU edge caching exists to fix.

**Tier 3** breaks on write throughput, not on latency: revocation storms, fleet-scale onboarding, and per-event anchoring that should have been batched. All three are cost problems with known mitigations, and all three are why the sharding and sidechain stance of the 2020 paper [5] is in the design (03 §4.2).

## 7. Turning these six designs into results

The six scenarios are designs and the suite should not pretend otherwise. The path to evidence is short and ordered.

1. ~~**Trace schema v2** — timing fields, versioned (00 §7 step 1c).~~ **Done, 2026-10-14**, as schema v1.1 rather than v2 because the field is purely additive (10 Addendum B §1c). `latencyMs` is recorded on every transaction and optionally on views. The canonical S1 script keeps its own emitter and was deliberately left untouched, so S1 is not yet timed.
2. **Re-emit the scenarios under schema v1.1.** Partly done: S7 and S8 were re-emitted (`vid_minimal_…1792035745190`, `vid_lifecycle_…1792035749199`), and S14, S16 and S17 are timed from birth. **S1 remains untimed** by the decision in step 1. The resulting Hardhat-local timings are a **lower bound and nothing more** — no network, no consensus, no radio. Their only legitimate use is to establish that the non-network components (*t*<sub>pres</sub>, *t*<sub>ver</sub>, *t*<sub>pol</sub>) are small, which is a real and useful negative result and which nobody has yet extracted from the re-emitted traces. **That extraction is now the cheapest open step in this document's path.**
3. **Build TS2-CAV and TS2-AGT** against the existing sandbox; both are buildable today, and their structural assertions (no `tx` in the window; rung and fetch-height recorded per decision) are evidence even without timing. Slice 1's S14 already demonstrates the TS2-CAV shape under degradation: a toll pass admitted on cached status during a READ_ONLY period, with zero writes during the outage and one batched write on reconnect (10 Addendum A §2) — which is §3.2's parallel-refresh pattern and its failure mode, observed.
4. **Besu QBFT and Caliper** (WO-8) for *t*<sub>read</sub>, *t*<sub>fin</sub>, and throughput against a real consensus, mapped to the three-tier analysis the Stage 18 plan already anticipates.
5. **Hardware** on the AURORA testbed for *t*<sub>ch</sub> and *t*<sub>ver</sub> on real OBUs over a real radio. **Only this step can support a Tier 2 latency claim, and only it can settle the double-signature question of §2.2.**

Until step 5, every sentence in the thesis about tier feasibility must be phrased as a budget and an argument, not as a result. Document 11 §5.3 holds the narrowed-claim sentences for exactly this purpose, and the six scenarios here are written so that each one's claim can be narrowed without being withdrawn.

---

## Sources used in this document

| Id | Source | Verification state | How used |
|---|---|---|---|
| — | `_CONTEXT_BRIEF.md` §2 (tier framework, both wordings), §5, §9 | VERIFIED AT SOURCE | Tier definitions, measurement rules |
| — | HDA 10 §5.2–§5.4 and the four committed traces | VERIFIED AT SOURCE | Every gas figure; rung-0 demonstration; F-VID-3 |
| — | HDA 01 §4 (read paths), 03 §4–§6, 04 §2–§3, 06 §3–§5, 08 §1–§2 | VERIFIED AT SOURCE for the claims cross-referenced | Read-path ladder, degraded modes, scenario bodies — pointed to, not duplicated |
| [5] | Prakash, Michelson, Feng, CVIN, IEEE VTC2020-Spring | VERIFIED AT SOURCE | Original tier wording; RSU-as-edge-server; MEC/5G consensus; sidechains; the Tier 3 training-data item |
| [28] | IEEE 1609.2-2022 | **UNVERIFIED** (not read at source; taken from the thesis draft and [5]) | SCMS role in Tier 1 — flagged in 00 §9 as a known limit of this pass |
| NEW | VehiclePassport, arXiv:2509.06133 | DIGEST-LEVEL | The one external timing figure: 22 ms generation, sub-5 ms verification for vehicular attribute proofs |
| [19] | ERC-8004 Trustless Agents | DIGEST-LEVEL | Agent registry and capability patterns |

## Registry delta rows

| Content Block | T | Source | Ch. | Ready | Notes and status |
|---|---|---|---|---|---|
| **The tier contract: tier determines read path, not function set** | A | HDA 05 §1.1 | 2 §2.4; 4 | 85% | Sharpens C6 from a feasibility filter to a data-placement constraint |
| Latency budget decomposition (seven components) | B | HDA 05 §1.3 | 2 §2.4; 4 | 80% | Gives every tier claim a shape that can be narrowed, not withdrawn |
| **The read-path ladder (rungs 0–4) mapped to tiers** | B | HDA 05 §1.4 | 4 §4.5 | 85% | Rung 0 demonstrated by S7/S8; the operational core of the document |
| TS1-CAV platoon braking; TS1-AGT safety veto | A | HDA 05 §2.2–§2.3 | 4 §4.4 | 70% | Designs. Double-signature cost is an open empirical question (hardware) |
| TS2-CAV zone entry; TS2-AGT tool-call authorisation | A | HDA 05 §3.2–§3.3 | 4 §4.4 | 75% | Buildable today; structural assertions available without timing |
| TS3-CAV transfer/underwriting/training corpus; TS3-AGT onboarding | A | HDA 05 §4.2–§4.3 | 4, 5 | 75% | Restores the 2020 paper's Tier 3 training-data item |
| **Reversibility rule for Tier 2 stale decisions** | A | HDA 05 §3.2 | 4 §4.5 | 80% | Why Tier 2 works at all; excludes irreversible gated access |
| Safety-budget versus throughput-budget inversion (CAV vs agent at Tier 2) | A | HDA 05 §3.3, §3.4 | 5 §5.2 | 75% | The clearest CAV/agent divergence in the tier analysis |
| All measured gas is Tier 3 gas | A | HDA 05 §4.1 | 4 | 90% | Constrains how cost and latency results may be presented together |
| Tier-coupling parameter table | B | HDA 05 §5 | 4, 5 | 70% | Three of six have measured consequences; none has a measured magnitude |
| Measurement path to tier results (five ordered steps) | B | HDA 05 §7 | 4 (method), 5 (future work) | 85% | Depends on decision D7 |

## Open questions for the researcher

1. **Does the Tier 1 accountability binding survive its own cost?** §2.2 carries both an SCMS pseudonym signature and a vehicle-DID delegate signature per safety message, and only OBU hardware over a real radio can say whether that is affordable. If it is not, the accountability claim narrows from per-message to per-session. Which claim does Chapter 1's accountability-gap argument actually need?
2. **Is the parallel-refresh pattern acceptable?** §3.2 removes the chain read from the critical path by deciding before the refresh lands, and is sound only because a zone entry can be priced after the fact. Does the thesis endorse this as a design rule, with the irreversibility exclusion, or treat it as an implementation trick?
3. **How long may an agent session run on state checked once?** §3.3 notes that an agent may make a hundred thousand calls under one verification, so the agent staleness exposure is orders of magnitude larger than the vehicle's. Is there a principled bound, or is the mandate ceiling the only real control?
4. **Does Tier 3 reclaim the training-data workload?** The 2020 paper put driving data for model training in Tier 3; the thesis's administrative framing dropped it. Restoring it makes 09 part of the tier framework rather than an appendix to it, and changes what Chapter 2 §2.4 says the tiers are for.
5. **What is the *warm* Groth16 verification time?** §3.2.1 measured 645.3 ms on a cold first call, and that single number decides whether the pre-computation placement rescues predicate proofs for Tier 2 gated access or whether predicates are a Tier 3 mechanism only. It is one line of benchmarking against artefacts already on disk, and it is now the highest-leverage unmeasured quantity in the suite.
6. **Where does the prover live?** Finding F-VID-16 makes this the design question, and §3.2.1 gives three options (pre-computation at a Tier 3 epoch, a delegated prover, or no predicates at Tier 2). The choice is a deployment-architecture commitment the thesis must name, and it interacts with freshness: a pre-computed proof is stale by construction, so the challenge binding has to move into the channel.
7. ~~**Is schema v2 authorised now?**~~ **Answered by execution, 2026-10-14**: timing landed as additive schema v1.1. The question that replaces it is narrower and still open — **will anyone extract the non-network component bound from the re-emitted traces?** The timings exist, nobody has read them, and the one legitimate claim they support (that *t*<sub>pres</sub>, *t*<sub>ver</sub> and *t*<sub>pol</sub> are small enough to be irrelevant to the Tier 2 budget) is the negative result that would let §3.2's budget table stop hedging about the cryptographic core. It is an afternoon's work on data already on disk, which makes it the single highest-yield item left in this document.
