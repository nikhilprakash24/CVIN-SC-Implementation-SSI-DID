CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Best of Both Worlds: The Hybrid Identity Data Architecture for Connected Vehicles and AI Agents**

**A Stage 3 design synthesis: tiered data placement, the Anchor · Cache · Attest · Reconcile pattern, degraded modes, the security/privacy/integrity envelope, cost, realisability, and how to demonstrate it**

Document 4 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose → Chapter 5, §5.x "The hybrid data architecture" (feeds Family F, C12–C13); methodology hooks → Chapter 4, §4.x*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 0. Status of this document: a design contribution, not a build

This document designs a composite identity data architecture. It is the Stage 3 output of the programme's three-stage inductive method (Stage 1 Native Sandbox → Stage 2 SSI Overlay → Stage 3 Gap Analysis and Benchmark). Under the programme's hard rule, Family F ("CVIN Combined") is synthesised from gap analysis and is never scaffolded as a Stage 1 sandbox option; the rule is restated verbatim in the sandbox's `CLAUDE.md` and `docs/ARCHITECTURE.md` and it binds this document. Nothing below has been built as a composite. What has been built is narrower and is named exactly in §10: one Stage 1 option (O1, ERC-1056 pattern) passing 12/12 compliance tests, one executed scenario (S1) with a 22-entry execution trace, a Python VC layer in the wider repository, and the MOBI VID contracts in the CV2X testbed. Every number in this document that is presented as measured comes from that S1 trace and is labelled with its function tag; every other quantity is a target, a budget, or a formula with named variables.

The claim of the document is this: an identity data architecture that is simultaneously safe for vehicles, scalable to national fleets, cheap enough to run, tamper-evident, and private where the law or the use case demands it is not obtained by choosing between on-chain and off-chain placement, nor by choosing between a lightweight EVM anchor and a purpose-built SSI stack. It is obtained by fixing a small number of invariants about *what may be trusted from a local cache, for how long, and what happens when the cache and the chain disagree*, and then letting each layer be supplied by whichever existing standard already satisfies those invariants most cheaply. The rest of the document makes that claim testable.

## 1. Design goals as a ranked, testable requirement set

The requirements are derived from four sources that the thesis already holds fixed: the three-tier latency framework of the 2020 CVIN paper [5] and its wireless constraints (scarce on-board compute, variable traffic load, unreliable links, intermittent coverage); the supervisor memos' threat model (impersonation, replay/equivocation, key compromise, Sybil/collusion, credential theft and mis-issuance, supply-chain compromise, plus chain faults: reorgs, rollbacks, partitions, delayed finality); the legal constraints of the GDPR and of eIDAS 2.0 as they bear on immutable ledgers and on unlinkable presentation (NEW-8, NEW-9, both DIGEST-LEVEL); and the accountability gap that motivates the thesis in the first place, namely that SCMS pseudonymity [6], [28] precludes answering "what is the history of actions taken by vehicle V?".

The requirements are ranked. Ranking matters because the requirements conflict at the margins (unlinkability against accountability, availability against revocation freshness, cost against integrity), and a design that cannot say which one yields is not a design. The rule adopted is that a lower-ranked requirement may be relaxed to satisfy a higher-ranked one, but never silently: the relaxation must be a declared parameter with a declared default and a named degraded mode (§5).

| Rank | ID | Requirement | Acceptance metric (how it would be shown) |
|---|---|---|---|
| 1 | R1 | **Safety independence.** No Tier 1 (<100 ms) path ever depends on ledger availability, ledger reads, or ledger writes. SCMS/IEEE 1609.2 governs Tier 1; this architecture only supplies keys and pseudonym linkage material to it out of band. | A Tier 1 scenario trace contains zero entries of kind `tx` or `view` inside the safety-message loop; formally, the Tier 1 verifier's code path has no dependency on the resolver. Demonstrated by static inspection plus a trace assertion. |
| 2 | R2 | **Integrity of acceptance.** A verifier accepts a credential or presentation only if (a) the signature verifies against a DID document it holds, and (b) the credential's anchor is either confirmed on chain or present in a signed local cache whose age is within the tier's staleness window τ. | 100% of `accept` decisions in a trace carry a provenance record `(anchorRef, cacheAge, τ)`; any accept with `cacheAge > τ` is a test failure. |
| 3 | R3 | **Bounded revocation staleness.** The interval between chain inclusion of a revocation (F7, G3) and the moment every conforming verifier rejects the revoked object is at most τ_tier. | Measured as `t_reject − t_include` in an S1-style teardown scenario; target τ2 and τ3 are parameters (§3.4), not results. |
| 4 | R4 | **Accountability.** Every Tier 3 action, and every Tier 2 action that has commercial or legal effect, is attributable after the fact to a DID with a tamper-evident key-material history, without weakening R7. | For any logged action, a reconstruction procedure returns the chain of anchors (DID creation, key at time of signing, credential anchor, endorsement at issuance time) that authorised it. |
| 5 | R5 | **Availability under disconnection.** A principal within its staleness window can complete Tier 2 interactions with no chain access, and can queue writes for later inclusion without loss or reordering ambiguity. | A scenario with the chain unreachable completes its Tier 2 interactions; on reconnect, queued writes are included and the reconciliation log shows zero unresolved conflicts. |
| 6 | R6 | **Privacy by policy.** Routine disclosures use the least-revealing mode the disclosure policy permits (§7); presentations of the same credential to different verifiers are unlinkable when the policy so requires; linkage for audit exists only under escrow. | Two presentations of the same credential to two verifier classes marked `unlinkable` share no common identifier, hash, or signature value; escrow decryption reproduces the linkage. |
| 7 | R7 | **Cost bound.** On-chain cost per principal-year is bounded by a declared budget G_year, and per-event anchor cost is amortised as G_root/b for batch size b (§8). | Parameters measured by Caliper on Besu QBFT; the S1 gas values are the anchor points. |
| 8 | R8 | **Scalability.** Write load on the anchor chain grows as O(E/b) for E events; read latency for a principal is O(1) in fleet size N because reads are served from a local, signed cache. | Read latency in a benchmark is independent of N; write throughput is a function of b only. |
| 9 | R9 | **Interface conformance.** IMinimalSSI (F1–F12), its errors and events, are not altered; every extension lives beside it. | The 12-test compliance suite passes unmodified on the anchor implementation. |
| 10 | R10 | **Portability.** A principal's identity and credentials can be migrated between shards or chains (the 2020 paper's ID Porting Protocol) with a continuity proof a verifier can check. | An S5-style port trace ends with a verifier on the destination chain accepting a presentation whose credential was issued on the source chain. |
| 11 | R11 | **Explicit governance.** Issuer and endorser roots of trust are on-chain, rotatable, and revocable; revocation of an endorsement invalidates issuances after its effective time only. | Endorsement-revocation scenario: credentials issued before the revocation remain valid; those after are rejected; the boundary is the chain-inclusion time. |
| 12 | R12 | **Legal compatibility.** Nothing on chain is personal data recoverable after the off-chain content and its salt are deleted; presentation formats are among those the EUDI ARF admits. | Argued (§7.4), not measured: an erasure procedure leaves only salted commitments and credential-definition hashes on chain. |
| 13 | R13 | **Realisability.** Every layer names either an existing tool or a build item with a gate and a trace. | The build plan (§9.3) has no layer without a named artifact and an acceptance assertion. |

Two remarks on the ranking. First, R1 is placed above R2 deliberately: an integrity check that could stall a collision-avoidance message is a safety defect, not a security feature. This is exactly why the 2020 paper put distributed-ledger technology out of scope for the low-latency tier [5] and why the thesis frames SSI as extending, not replacing, SCMS. Second, R6 (privacy) is ranked below R4 (accountability) and above R7 (cost): the architecture will pay for privacy, but it will not buy privacy that destroys attributability. That ordering is what makes the dual-mode identity of the 2020 paper (pseudonymous stream versus verinym) an escrow design rather than an either/or (§6.4, §7.3).

## 2. The architecture in layers

The architecture is seven layers, L0 to L6. For each layer the questions answered are the same four: what is on chain, what is off chain, what is cached at the principal or at the edge, and which invariants the layer maintains. The table at the end of the section summarises placement; the prose argues it. Document 01 gives the per-object and per-function placement analysis that these choices rest on; this section does not repeat it, it composes it.

### 2.1 L0: roots of trust and governance

*Claim.* The roots of trust are endorser DIDs, and the chain's job at L0 is to make the set of endorsers, the issuers they endorse, the credential types each endorsement covers, and the key-rotation history of all of them, publicly discoverable and tamper-evident.

*Reasoning.* The supervisor memos require explicit governance: issuer roles, endorser sets, key rotation. The spec's §6 governance extension names the functions (registerIssuer, endorseIssuer, proposeChange) and the campaign build gives them a home, `EndorsementRegistry.sol`, with G1 registerIssuer, G2 endorseIssuer, G3 revokeEndorsement, G4 isEndorsed. The verification policy the whole architecture relies on is then a conjunction: F6 valid *and* G4 endorsed for that credential type *at the time of issuance*. The temporal qualifier is the entire point of putting endorsements on chain: an endorsement that is later revoked must not retroactively invalidate credentials issued while it stood, and only a chain (or an equivalently ordered log) can fix "while it stood" beyond dispute.

*Placement.* On chain: endorser DIDs (Set A, F1), the endorsement edges with validity windows (G2), their revocations (G3), and the key-rotation history of endorsers and issuers (F3, F9, F10). Off chain: the governance documents that justify an endorsement (a ministry's delegation instrument, an OEM's plant accreditation), referenced by hash. Cached: the endorsement graph is small (thousands of edges for a national jurisdiction, not millions) and changes rarely, so every verifier holds a full signed copy with a staleness window τ_gov that is the longest in the system. Invariant L0-I1: no credential is accepted whose issuer was not endorsed for its type at the credential's anchor time. Invariant L0-I2: an endorser or issuer key rotation is effective from its chain-inclusion time; signatures under the old key are valid before that time and invalid after it.

*Chain choice.* L0 tolerates either a permissioned chain (Besu QBFT with a validator set drawn from the endorsers themselves) or a public L1. The argument for permissioned at L0 is that the parties who must agree on the endorsement graph are a small, legally identifiable set (ministries, OEMs, insurers), which is exactly the case in which deterministic finality and a closed validator set cost nothing in decentralisation the design actually needs. The argument for public is that a Local CVIN [5] wanting to prove its governance state to a foreign jurisdiction benefits from an anchor neither side controls. The design resolves this by not choosing: L0 state is *anchored* (Merkle root of the endorsement graph per epoch) to whatever backbone chain the deployment selects, and the backbone can be public while the operational chain is permissioned. This is the 2020 paper's sidechain-to-backbone pattern applied to governance.

### 2.2 L1: identity anchor layer (Set A)

*Claim.* Vehicles and other physical principals should be anchored with an ERC-1056-style, event-sourced identity pattern; AI agents that require programmable authorisation should be anchored with a contract-account pattern; and both should sit behind the same IMinimalSSI Set A interface so that the choice is invisible above L1.

*Reasoning, with the Set A evidence.* The Set A scoring anchors from Pass 1 (out of 24, viability ≥16) are ERC-1056 23, LFDT 22, ERC-725 20, ERC-725xy 20, ERC-4337 18, ERC-721 15, ERC-8004 15. Only ERC-1056 (O1) is confirmed live in the sandbox with 12/12 compliance; the others are prior evaluations pending confirmation. On the measured evidence, O1's lifecycle costs in the S1 trace are: createDID 161,823–178,935 gas (F1), addVerificationMethod 59,607 (F9), addDelegate 54,227 (F11), removeVerificationMethod 36,478 (F10), updateDID 44,760 (F3), deactivateDID 55,127 (F4); resolveDID and validDelegate are gas-free views. The recorded deviation, createDID at roughly 1.6–1.8 times the spec's <100K target, is an interface-uniformity cost (explicit DID storage rather than pure event-sourcing) and is a finding, not a defect to be hidden.

Why event-sourced for vehicles: a vehicle's identity is long-lived (a decade or more), has a low but non-zero rate of key events (annual rotation, occasional delegate changes, one ownership transfer every few years), and its verifiers overwhelmingly need to answer "which key was authoritative at time t?" That is precisely the question an event log answers cheaply: the DID document is reconstructed by replaying events, and the replay can be done once at the edge and cached. A contract-per-vehicle pattern (ERC-725 lineage) buys direct on-chain queryability that vehicles do not need at Tier 2, at a deployment cost of roughly 450–550K gas (DIGEST-LEVEL, reference registry figures) that, multiplied by a Canadian fleet of about 33 million vehicles (DIGEST-LEVEL), dominates every other cost in the system.

Why contract-account for agents needing programmable authorisation: an AI agent acting for a principal must be able to express *policy* about which actions it may sign, with which spending limit, for how long, and with which co-signer. The event-sourced pattern can express delegation (F11 addDelegate with a type and validity) but not conditional authorisation. ERC-4337 account abstraction [24], with ERC-7579 modules (NEW-10, DIGEST-LEVEL) supplying validation logic, expresses the policy as code the chain enforces, and the thesis's C14 wrapper already places agent identity there. The cost is higher deployment gas and a richer attack surface, which is acceptable because the population of agents is smaller than the fleet and each agent's economic exposure is larger. Agents that do not need programmable authorisation (a data-collection agent that only signs telemetry) should use the event-sourced pattern like a vehicle.

*Placement.* On chain: DID creation, key additions and removals, delegate grants, deactivation flags, all as events (and, in O1's implementation, in explicit storage). Off chain: nothing at L1 is inherently off chain, but the *resolved* DID document is a derived artifact and should be treated as cache, never as source. Cached: resolved DID documents with the block number at which they were resolved (the cache key is `(did, blockNumber)`), held at the principal for its counterparties and at RSUs for the vehicles in their coverage. Invariant L1-I1: a DID document cached at block n is a correct view of the DID at block n; correctness at any later block is only asserted within the staleness window. Invariant L1-I2 (from the spec): the last verification method is never removed; a deactivated DID remains resolvable with its flag.

### 2.3 L2: credential layer (Set B)

*Claim.* Credentials are W3C VCs [9], [10] held off chain by the holder; the chain holds only the anchor (the F5 credential hash and validity), the revocation state (F7), and, for status-list revocation, the list's current root; the architecture runs status-list and accumulator revocation *in parallel* and lets the presentation layer choose which to prove against.

*Reasoning.* The measured F5 issueCredential cost on O1 is 130,163 gas for a 32-byte hash and a validity; the content never touches the chain, exactly as the spec requires. The central empirical finding of the thesis, that no EVM standard natively implements createPresentation, is what forces the credential *content* off chain: the chain cannot verify a W3C VC's proof economically, so it should not hold what it cannot verify. What it holds is the smallest object that lets an off-chain verifier check that a credential it has been shown is the one the issuer anchored.

Dual revocation is the one place this document departs from picking a single mechanism, and the departure is deliberate. Status lists (W3C Bitstring Status List, NEW-1) are cheap to maintain and cheap to prove against, but a status-list index is a persistent identifier that links every presentation of the credential; that is acceptable for Tier 3 (an insurer checking a registration) and unacceptable for unlinkable Tier 2 presentations. Accumulators (CL/ALLOSAUR in the AnonCreds lineage, NEW-15, DIGEST-LEVEL) give the holder a non-revocation proof that reveals nothing about which credential it is, at the cost of witness updates on every revocation. Document 02 analyses the two in depth; the design decision here is that *both* revocation states are derived from the same F7 event, so there is one truth (the F7 log) and two proof formats. The invariant that makes this safe is L2-I3 below.

*Placement.* On chain: F5 anchor (hash, issuer DID, subject DID, validUntil), F7 revocation flag, the epoch root of the status list, and the accumulator value per epoch; also the credential-type registry (`CredentialTypeRegistry`: type id, schema hash), which is safely public because credential-definition hashes are not personal data (the GDPR nuance from the Building Paths preface). Off chain: the credential document, its Data Integrity proof, the status list bitstring itself (content-addressed, see L6), the accumulator witnesses. Cached: at the holder, its own credentials and current witnesses; at the verifier, the status lists it checks most often, tagged by epoch; at the RSU edge, the status lists for credential types that Tier 2 services in its area accept. Invariant L2-I1: `hash(canonical(credential)) == anchor.credentialHash` for every accepted credential. Invariant L2-I2: the salt that makes the credential hash unlinkable to any predictable content lives in the credential, so deleting the credential deletes the ability to reproduce the hash. Invariant L2-I3: status-list bit i and accumulator membership of credential i are both derived from the F7 log by a deterministic function, and a verifier that observes them disagree treats the credential as revoked (revocation-wins).

### 2.4 L3: presentation and privacy layer

*Claim.* SD-JWT [14] is the baseline presentation format because it is the cheapest that satisfies selective disclosure and is what the EUDI ARF admits; BBS+ (W3C Data Integrity BBS cryptosuite, NEW-2; AnonCreds v2) is used where the disclosure policy requires unlinkability; ZK predicates (range and set-membership proofs) are used only where the policy requires that an attribute *not* be disclosed but a fact about it must be proven.

*Reasoning.* This is the layer where the thesis's structural insight lives: EVM standards optimise identity anchoring and defer selective disclosure to off-chain middleware, while the AnonCreds lineage implements native ZK presentations off chain and anchors only credential definitions and revocation accumulators. The hybrid takes exactly the union of what each is good at. The F8 createPresentation function on chain, measured at 62,441 gas in S1, is *not* a presentation in the W3C sense; it is a commitment that binds a challenge and a domain to a holder and a set of credential ids, giving replay protection and an on-chain record that a presentation was made. The presentation proper is off chain in one of three formats, chosen by policy (§7). Document 02 gives the cost and privacy analysis of the three formats; the design statement here is only that the choice is a per-disclosure policy output, not a system-wide setting, and that the F8 commitment is the same regardless of format.

*Placement.* On chain: the F8 commitment (holder, credential ids, challenge, domain) *when the policy requires a chain-visible record*; nothing otherwise. Off chain: the presentation, its proof, the verifier's verification record. Cached: verifier-side, the issuer public keys and credential-definition hashes needed to verify each format; holder-side, precomputed BBS+ blinding material and accumulator witnesses so that Tier 2 presentation latency is dominated by the proof, not by fetches. Invariant L3-I1: every presentation carries a challenge that the verifier generated or that binds to a chain-visible F8 commitment; a presentation without a fresh challenge is rejected. Invariant L3-I2: an unlinkable presentation contains no value that appears in any other presentation of the same credential (the BBS+ proof, the accumulator witness randomisation, and the pairwise DID together give this).

### 2.5 L4: transport and I2I layer

*Claim.* All identity-to-identity traffic runs over an off-chain authenticated-encryption channel with forward secrecy, whose session key is bound to on-chain identity state through a challenge-bound presentation; the chain is consulted only at channel setup and on a revocation signal, never per message.

*Reasoning.* S1 demonstrates the pattern end to end on O1: mutual authentication by F2/F6/F12 views, an F8 commitment to a challenge derived from the channel hello, then ECDH P-256 and AES-256-GCM off chain, then a mid-session revocation (F7) that the verifier detects on its next F6 check and tears the channel down. The trace records the off-chain step explicitly (`kind: offchain`, 42-byte ciphertext, 16-byte tag) precisely so that the hybrid boundary is evidenced, not asserted. Document 08 designs the channel in full, including the cruxes: revocation propagation into a live session, key agreement across key rotation, replay, and offline operation. The design statement here is placement: what L4 needs from the chain is *state*, not *service*; it reads the state through the L1–L2 caches, so a channel can be established with zero chain round trips when the caches are fresh.

*Placement.* On chain: nothing per message; the F8 commitment at setup if the policy requires it. Off chain: the channel, the session transcript (retained per the interaction-logging phase of the A2A model in the memos), the signed session-close record. Cached: per-peer session state including the block number at which the peer's DID document and credential status were last confirmed. Invariant L4-I1: the session key is derived from material that includes the challenge of the setup presentation, so a channel cannot be established by replaying a captured presentation. Invariant L4-I2: a channel whose peer credential or DID is observed revoked or deactivated is closed within τ_tier of the observation, and all messages after the revocation's chain-inclusion time are marked "received under stale state" in the transcript.

### 2.6 L5: trust signals (Set C)

*Claim.* Reputation and validation attestations are on chain as small scored records with evidence URIs pointing off chain, following the ERC-8004 pattern [19]; they are trust *inputs* to policy, never authorisation by themselves.

*Reasoning.* The memos admit reputation as optional and warn about Sybil and collusion; document 09 makes the case that federated learning and other collective computation cannot function without a reputation that is bound to an identity that cannot be cheaply re-created. The ISetC interface (attestReputation, getReputation, requestValidation, validationStatus) is what the architecture exposes. The design decision at L5 is that an attestation is only *counted* if the attester is itself an endorsed issuer for the `ReputationAttestation` type (an L0 dependency), which is the "issuer weighting" Sybil defence from the memos made concrete; unendorsed attestations are stored but weighted zero by default policy.

*Placement.* On chain: C1 attestReputation records (subject DID, score, evidence URI hash, attester DID), C3 validation requests and C4 status. Off chain: evidence (execution traces, sensor logs, model-contribution records), content-addressed. Cached: aggregate scores at verifiers, with epoch tags. Invariant L5-I1: a reputation score is never used as a sole authorisation input; it is combined with a valid credential under policy. Invariant L5-I2: evidence URIs resolve to content whose hash matches the on-chain record, or the attestation is treated as absent.

### 2.7 L6: data and oracle layer

*Claim.* All bulky data (credential documents, status lists, evidence, execution traces, governance documents) lives in content-addressed off-chain stores; real-world facts enter the system through distributed oracles that sign what they observe under their own DIDs; the chain holds content hashes and oracle attestation anchors, nothing more.

*Reasoning.* This is the 2020 paper's distributed-oracle concept [5] made concrete: an oracle (an inspection station's sensor, a toll gantry, a charging station's meter) is a DID with an endorsed issuer role, and its observations are credentials like any other, anchored by F5 and subject to F7. That unifies "oracle data" with "credential data" and removes any need for a separate trust mechanism: the oracle's trustworthiness is its endorsement (L0) plus its reputation (L5). Content-addressing (IPFS-style CIDs, NEW-7, DIGEST-LEVEL) is chosen because it makes the off-chain store's integrity a property of the address, so the chain's hash *is* the address, and a cache can serve content that any party can verify without contacting the origin. Enterprise or regulated storage can substitute for public IPFS where the regulation requires; the invariant is on the addressing, not the host.

*Placement.* On chain: content hashes (as F5 anchors, as evidence URI hashes, as governance-document hashes), oracle DIDs, oracle attestation anchors. Off chain: everything else. Cached: content by CID at RSU edges and at principals, with no staleness concept because content-addressed data does not go stale (its *status* does, and that is L2's concern). Invariant L6-I1: no on-chain reference to off-chain content is accepted unless the content's hash equals the reference. Invariant L6-I2: an oracle observation is a credential; it has an issuer, an anchor, and a revocation path.

### 2.8 Placement summary

| Layer | On chain | Off chain | Cached (where, keyed by) | Governing invariants |
|---|---|---|---|---|
| L0 Governance | Endorser DIDs; endorsement edges and revocations; key-rotation history; epoch Merkle root of the graph (anchored to backbone) | Delegation instruments, accreditation documents | Full endorsement graph at every verifier, keyed by epoch | L0-I1 endorsed-at-issuance; L0-I2 rotation effective at inclusion |
| L1 Identity (Set A) | Events for F1, F3, F4, F9, F10, F11 (explicit storage in O1) | Nothing intrinsic | Resolved DID documents at principals and RSUs, keyed by (did, blockNumber) | L1-I1 cache correct at its block; L1-I2 last key never removed |
| L2 Credentials (Set B) | F5 anchor; F7 flag; status-list epoch root; accumulator value; credential-type registry | Credential documents and proofs; status-list bitstrings; witnesses | Own credentials and witnesses at holder; status lists at verifiers and RSUs, keyed by epoch | L2-I1 hash match; L2-I2 salt-in-content; L2-I3 revocation-wins on disagreement |
| L3 Presentation | F8 commitment when policy requires | Presentations, proofs, verification records | Issuer keys and definitions at verifiers; blinding material at holders | L3-I1 fresh challenge; L3-I2 no shared value in unlinkable mode |
| L4 Transport | Nothing per message | Channels, transcripts, close records | Peer state with last-confirmed block | L4-I1 challenge in key derivation; L4-I2 close within τ |
| L5 Trust signals (Set C) | C1 records; C3/C4 requests and status | Evidence | Aggregates at verifiers, keyed by epoch | L5-I1 never sole authorisation; L5-I2 evidence hash match |
| L6 Data/oracle | Content hashes; oracle DIDs and attestation anchors | All content | Content by CID at edges and principals (no staleness) | L6-I1 hash equals reference; L6-I2 oracle observation is a credential |

## 3. The core pattern: Anchor · Cache · Attest · Reconcile

*Claim.* One pattern, applied uniformly across L0–L6, is what lets the architecture be safe at Tier 1, available at Tier 2 without connectivity, and accountable at Tier 3: every principal keeps a *signed local view* (the cache) sufficient to act for a bounded staleness window; anchors are written to the chain *asynchronously and in batches*; every action a principal takes is an *attestation* (a signed event or presentation) logged off chain and Merkle-anchored; and *reconciliation* on reconnect resolves disagreements between cache, log, and chain by deterministic rules that never require a human and never require agreement between the parties.

### 3.1 The four verbs

**Anchor.** An anchor is the minimum on-chain object that makes an off-chain object verifiable: for an identity, the Set A events; for a credential, the F5 hash; for a batch of off-chain attestations, a Merkle root. Anchors are written by the party that owns the object (the issuer for credentials, the controller for DID events, the logging principal for attestation batches). The design rule is that anchors are *asynchronous with respect to the action they anchor*. A credential can be issued, delivered, and used before its F5 anchor is included, provided the verifier's policy for that tier accepts "anchor pending" (it never does at Tier 3 for legal effect, and it may at Tier 2 within τ2 for an endorsed issuer whose signature verifies). The batch rule is that anchors are aggregated per epoch into a Merkle root where the object type admits it (attestation logs, status lists) and written individually where the interface requires it (F5 is per-credential by specification; batching F5 is a spec §6 extension, "batch ops", and is discussed in §8 as a cost lever, not assumed).

**Cache.** A cache is a *signed* local view. The signature matters: an RSU that serves a resolved DID document to a vehicle signs the document together with the block number at which it resolved it, so the vehicle holds a statement "at block n, DID d resolved to document D, says RSU r" that is itself an attestation with a DID behind it. This turns cache-poisoning from an undetectable attack into an attributable one (§6). The cache carries, for every entry, the block number and the wall-clock time of its last confirmation, and the tier-dependent staleness window τ. The principal is permitted to act on an entry if and only if `now − t_confirmed ≤ τ_tier`; otherwise the entry is *stale* and the principal is in a degraded mode (§5).

**Attest.** Every action with identity significance is a signed event: a presentation made, a presentation accepted, a channel opened or closed, a credential issued or received, a reputation attestation given, an oracle observation. Attestations are appended to the principal's off-chain log in the order taken, each carrying the principal's view of the chain (the block number of its freshest cache entry) at the moment of the action. The log is Merkle-anchored per epoch (an epoch is a configurable interval; the default proposal is per day for vehicles and per hour for agents, both parameters). This is the forensic audit trail of the Building Paths preface: the chain does not prevent a bad action, it makes the action permanently visible and attributable, including the fact that it was taken under a stale view.

**Reconcile.** On reconnect, or on each epoch boundary while connected, the principal compares its log and cache against the chain and applies the rules of §3.3. Reconciliation produces three outputs: an updated cache, a set of queued writes now submitted (or abandoned as superseded), and a list of *retrospective invalidations*: actions in the log that were valid under the view at the time but are invalid under the chain's view (for example, a presentation accepted from a credential revoked minutes earlier). Retrospective invalidations are not undone by the identity system (it cannot undo a toll gate opening); they are surfaced to the application layer with the evidence, which is exactly what R4 requires.

### 3.2 The principal state machine

Each principal (vehicle OBU, RSU, agent, verifier service) runs the following state machine over its cache freshness and chain reachability.

```
states:
  SYNCED        -- chain reachable, cache confirmed within tau_tier
  LAGGING       -- chain reachable, but confirmation older than tau_tier/2 (refresh in progress)
  OFFLINE_FRESH -- chain unreachable, cache age <= tau_tier
  OFFLINE_STALE -- chain unreachable, cache age  > tau_tier
  PARTITIONED   -- chain reachable, but observed chain view conflicts with a
                   previously confirmed view (fork, rollback, or shard divergence)
  RECOVERING    -- reconciliation in progress after OFFLINE_* or PARTITIONED

transitions:
  SYNCED        --(age > tau/2)--------------------> LAGGING
  LAGGING       --(refresh ok)---------------------> SYNCED
  LAGGING       --(chain unreachable)--------------> OFFLINE_FRESH
  SYNCED        --(chain unreachable)--------------> OFFLINE_FRESH
  OFFLINE_FRESH --(age > tau)----------------------> OFFLINE_STALE
  OFFLINE_*     --(chain reachable)----------------> RECOVERING
  SYNCED|LAGGING--(view conflict detected)---------> PARTITIONED
  PARTITIONED   --(canonical view chosen)----------> RECOVERING
  RECOVERING    --(reconcile complete, no conflict)-> SYNCED
  RECOVERING    --(reconcile complete, conflicts)--> SYNCED  (conflicts emitted as
                                                     retrospective invalidations)

permitted actions by state (Tier 2 unless noted):
  SYNCED        : read, present, accept, write (writes submitted immediately)
  LAGGING       : read, present, accept, write (writes submitted immediately)
  OFFLINE_FRESH : read, present, accept (accept only if peer's status also fresh),
                  queue writes
  OFFLINE_STALE : read (marked stale), present (marked stale), REFUSE accept
                  for any object whose status could have changed (credentials,
                  delegates); queue writes; Tier 1 unaffected (R1)
  PARTITIONED   : read-only; refuse accept; refuse write until canonical view chosen
  RECOVERING    : read-only; refuse accept; drain queue under reconcile rules
```

The asymmetry between `present` and `accept` in `OFFLINE_STALE` is the design's central safety valve. A holder may always show what it has (its credential is its own; it may be revoked, but presenting a revoked credential is not the holder's risk to bear beyond the flag in its log); a verifier may not *accept* against a stale view, because acceptance is where the verifier takes on risk. Whether a stale verifier refuses or accepts-with-flag is a policy parameter per verifier class (§7.2): a parking gate may accept-with-flag and reconcile later, a border crossing may not.

### 3.3 The reconciliation rules, formally

Let the principal's off-chain log be a sequence of attestations `a_1 … a_k`, each with `(actor, kind, object, t_sig, view_block, sig)`. Let the chain's canonical event log for the objects referenced be `E`, each event with `(kind, object, t_incl, block, index)`. Let the queue of pending writes be `Q`. Reconciliation is the following deterministic procedure.

```
procedure RECONCILE(log, cache, Q, chain):
  -- Rule R-ORDER: canonical order is chain inclusion order for anchored events;
  --   for events not yet anchored, issuer-signed time; ties broken by hash.
  E := chain.events(objects referenced by log ∪ Q ∪ cache)
  order(e) := (e.block, e.index)            if e anchored
            := (∞, e.t_sig, hash(e))         otherwise

  -- Rule R-REV (revocation wins): for any object with a revocation or
  --   deactivation event in E, the object is invalid from t_incl of that
  --   event, regardless of any later-signed issuance, presentation, or
  --   acceptance, and regardless of arrival order.
  for each object o with rev(o) ∈ E:
     cache[o].status := REVOKED at rev(o).t_incl
     for each a ∈ log with a.object = o and a.kind ∈ {accept, open_channel}
         and a.t_sig ≥ rev(o).t_incl:
        emit RETROSPECTIVE_INVALIDATION(a, rev(o))

  -- Rule R-KEY (rotation boundary): a signature under key k on object o is
  --   valid iff k was a verification method (or valid delegate) of the signer's
  --   DID at the block whose timestamp is the greatest ≤ a.t_sig. Signatures
  --   made in a staleness window under a since-removed key are quarantined,
  --   not rejected: the application decides.
  for each a ∈ log:
     if not valid_key_at(a.actor, a.key, block_at(a.t_sig)):
        if a.view_block < removal_block(a.key): emit QUARANTINE(a)   -- acted under stale view
        else:                                    emit REJECT(a)       -- acted after knowing

  -- Rule R-ENDORSE (endorsed-at-issuance): a credential anchored at block n
  --   is acceptable only if its issuer was endorsed for its type at block n.
  for each credential c ∈ cache:
     if not endorsed_at(c.issuer, c.type, c.anchor_block):
        cache[c].status := UNENDORSED; emit INVALIDATION(c)

  -- Rule R-QUEUE (superseded writes drop, others submit in signed order):
  for each w ∈ Q in t_sig order:
     if superseded(w, E):      drop(w)        -- e.g. a queued update to a now-deactivated DID
     else if conflicts(w, E):  emit CONFLICT(w); drop(w)   -- e.g. removing a key already removed
     else:                     submit(w)

  -- Rule R-ANCHOR: the log epoch is closed and its Merkle root queued as a write.
  Q.append(anchor(merkle_root(log[epoch])))
  cache.confirmed_block := chain.head; cache.t_confirmed := now
```

Three properties follow, and each is a test. Determinism: two honest principals reconciling the same log against the same chain produce identical outputs (test: run RECONCILE twice on a recorded trace; diff is empty). Revocation monotonicity: once an object is REVOKED in a cache it never returns to VALID (test: search the trace for any VALID after REVOKED on the same object; must be empty). Attributability: every RETROSPECTIVE_INVALIDATION names the acceptance attestation and the revocation event, both signed, both anchored (test: for every emitted invalidation, both referenced records resolve).

What breaks it, stated honestly: R-ORDER depends on chain finality. On a chain with probabilistic finality a reorg can change `(block, index)` for recent events; the design therefore defines "anchored" as *included beyond the finality depth* the deployment declares (deterministic under QBFT, a depth parameter under a public L1), and events shallower than that are ordered as if unanchored. R-KEY depends on block timestamps being monotone and close to wall-clock, which is true within seconds on a healthy chain and is a declared assumption. R-REV assumes that the revocation event is *visible*; a principal that has been partitioned from every honest RSU cannot learn it, which is why OFFLINE_STALE forbids acceptance and why τ is short at Tier 2.

### 3.4 Staleness windows per tier

The staleness window is the single most important parameter in the design, and it is a parameter, not a result. The proposed defaults are stated as design targets to be tuned by measurement in the demonstration plan (§10), and the reasoning for each is given.

| Tier | τ_tier (proposed default, parameter) | What the window bounds | Reasoning |
|---|---|---|---|
| Tier 1 (<100 ms) | Not applicable to ledger state. SCMS pseudonym certificate lifetime governs (IEEE 1609.2 [28]). | Nothing; there is no ledger read in the loop (R1). | The only SSI-side object at Tier 1 is the pairwise/pseudonymous DID material provisioned to the OBU out of band; its validity is that of the SCMS certificate it accompanies. |
| Tier 2 (100–500 ms) | τ2 = 300 s for credential and delegate status; τ2,doc = 3,600 s for DID documents | The maximum interval a Tier 2 verifier may act on a revoked credential without knowing. | Bounded by the RSU refresh cycle: an RSU in coverage can refresh its status lists every few blocks; 300 s is an order of magnitude above QBFT block time and below the duration of a typical charging or parking session, so a revocation lands within the session (the S1 teardown, generalised). DID documents change far less often; an hour is proposed. |
| Tier 3 (>500 ms) | τ3 = 0 (read-through to chain at finality) for legal-effect writes; τ3,read = one epoch for history queries | Legal effect requires the chain's current view. | Registration, ownership transfer, and insurance issuance are not time-critical; there is no reason to accept staleness. |
| Governance (L0) | τ_gov = 86,400 s | Endorsement graph freshness. | The graph changes rarely; revocation of an endorsement is a Tier 3 event whose consequences are handled by R-ENDORSE, which is time-bounded by the anchor block, not by the verifier's cache age. |

The relationship among the windows is the design's claim to safety under disconnection: a vehicle that leaves coverage with a cache confirmed at time t may act as a Tier 2 verifier until t + τ2 and as a Tier 2 holder indefinitely (with its presentations marked stale beyond t + τ2), and must refuse Tier 3 acceptance immediately. Document 05 instantiates this per tier with one CAV and one agent scenario each; document 06 works the read-only and delayed-write cases in detail.

## 4. Tier-to-placement mapping, shards, and the ID Porting Protocol

*Claim.* The tiers map to chain interaction as follows: nothing touches the chain synchronously at Tier 1; Tier 2 performs reads only, served through the cache, and queues writes; Tier 3 performs reads and writes synchronously against chain finality. Local CVIN shards, L2 rollups, and sidechains with backbone anchoring all fit this mapping as different *placements of the same anchor*, and the ID Porting Protocol is the migration of an anchor between placements with a continuity proof.

### 4.1 What may touch the chain, by tier

| Tier | Synchronous chain reads | Synchronous chain writes | Cache role | Queued writes |
|---|---|---|---|---|
| 1 | None (R1) | None | Not consulted | None; Tier 1 generates no identity events |
| 2 | None on the critical path; background refresh of status lists and DID documents at the RSU edge | None | Sole source for F2, F6, F12, G4 decisions | F8 commitments (if policy requires), C1 attestations, log-epoch anchors |
| 3 | F2, F6, F12, G4 read-through at finality | F1, F3, F4, F5, F7, F9, F10, F11, G1–G3 | Advisory only | None (writes are synchronous) |

The Tier 2 row is the "clever" part and its assumption should be stated. A Tier 2 verifier (a charging station, a toll gantry, an RSU acting for a parking operator) makes *no* chain call during the interaction. That works because (a) all the state it needs is in Set A views and Set B/status views that change slowly relative to τ2, (b) those views are prefetched for the population of credentials the verifier's service class accepts, and (c) the F8 commitment, if required, can be written after the interaction because its purpose is replay protection and audit, not admission. The assumption that makes it work is that the RSU edge is *reachable* by the verifier and is itself refreshing within τ2; the thing that breaks it is an RSU whose backhaul has failed silently while it continues to serve cached views, which is why cache entries are signed with block numbers and the verifier checks `age`, not merely `presence`.

### 4.2 Shards, L2, and sidechains as anchor placements

The 2020 paper proposed Local CVINs derived from a Global CVIN, sidechains carrying most transactions with few on the backbone, and MEC/5G-aware consensus at the edge [5]. In the vocabulary of this document these are three placements of the L1–L2 anchors:

A *Local CVIN shard* is a permissioned chain (Besu QBFT is the reference substrate, shared with E1 Indy-on-Besu [25]) whose validators are the jurisdiction's endorsers, holding the Set A and Set B state of the principals registered there, and anchoring its epoch state root to a backbone. Its benefits are those the paper claimed: smaller state, lower lookup latency, jurisdiction-specific policy. Its cost is that a verifier in another shard must trust the backbone anchor plus a Merkle proof rather than reading the state directly.

An *L2 rollup* over a public L1 is the same idea with the backbone's security inherited more tightly: the rollup's state root is posted to L1 and, for a zk-rollup, proven. For this architecture the relevant property is only that the per-event cost on the rollup is a fraction λ (λ < 1, a parameter measured per rollup) of the L1 cost, and that finality to L1 is delayed by the rollup's posting interval, which lengthens τ3 for cross-domain acceptance.

A *sidechain with backbone anchoring* is the general case: any chain whose epoch root is written to a backbone chain. In the architecture this is how L0 is treated regardless of where L1–L2 sit (§2.1).

The unifying rule: an anchor is *valid for a verifier* if the verifier can check it against a chain it trusts *or* against a Merkle proof rooted in such a chain. That rule is what makes the placement invisible above L2: the credential layer, presentation layer, and transport layer never know whether an anchor lives on a shard, a rollup, or the backbone. The invariant is L2-I1 with the anchor's location abstracted behind an `anchorRef` that names `(chainId, contract, blockNumber, proof?)`.

### 4.3 The ID Porting Protocol as anchor migration with continuity proofs

*Claim.* An IDPP port of a principal from source placement S to destination placement D is a three-step transaction whose correctness can be checked by any verifier: (1) on S, the controller writes a *port-out* event naming D and a commitment to the principal's current state root (DID document, credential anchor set, endorsement dependencies); (2) on D, the controller creates the DID (F1) and writes a *port-in* event containing the S anchor reference, the state root, and a Merkle proof of the S port-out event's inclusion beyond finality; (3) on S, the DID is deactivated (F4) with the standard flag plus a reference to the D anchor, so that a resolver on S returns "moved to D" rather than "gone".

The continuity proof a verifier on D checks is: the D port-in references an S port-out; the S port-out is included beyond finality (proof against the backbone anchor if the verifier does not read S directly); the two state roots match; and the S DID is now deactivated with a forward reference. Credentials issued on S remain verifiable on D because their F5 anchors are in the S state root that the port-in committed to; their revocation, however, continues to happen on S (the issuer did not move), so a D verifier checking a ported credential must read S's status for it, which is the one place the port is not free. The design accepts this rather than re-issuing every credential: re-issuance is the issuer's choice, triggered by the port-in event as a notification.

What this does that the 2020 paper could not: it makes the IDPP *testable*, which the sandbox catalog already anticipated as scenario S5 (O1 → O8/E1). The demonstration plan (§10) places the IDPP slice after the reconciliation slice because the port is, in the vocabulary of §3, a reconciliation between two chains with a declared canonical order (source before destination).

## 5. Degraded modes

*Claim.* Every failure the threat model and the wireless constraints name maps to one of five degraded modes, and in each mode the state machine of §3.2 tells every principal what it may still do safely and what it must refuse. Recovery is always RECONCILE.

**Read-only mode.** Trigger: chain reads succeed (directly or via a fresh RSU cache) but writes are not accepted (L1 congestion, sequencer outage on a rollup, a validator-set quorum loss that leaves the chain readable but not progressing). Principals stay SYNCED or LAGGING for reads, so Tier 2 continues unaffected; Tier 3 writes queue. What must be refused: Tier 3 legal-effect operations that require a synchronous write (ownership transfer, registration issuance) are not *pretended*; the application receives "queued, not effective". What is still safe: issuing a credential off chain with anchor-pending status for Tier 2 use, because the issuer's signature and endorsement can be verified without the anchor. Recovery: writes drain in signed order under R-QUEUE when writes resume.

**Delayed-write mode.** Trigger: the principal itself is intermittently connected (the vehicle case) while the chain is healthy. This is OFFLINE_FRESH then OFFLINE_STALE. The holder presents as usual; the verifier role on the same principal (a vehicle verifying another vehicle's credential for a cooperative manoeuvre) accepts only while fresh. Queued writes accumulate: F8 commitments, C1 attestations, log-epoch anchors. What must be refused: acceptance under OFFLINE_STALE (§3.2). Recovery: RECONCILE on reconnect; retrospective invalidations are the expected output and are not errors. Document 06 works this mode as a scenario pair.

**Partition mode.** Trigger: two shards, or two segments of one chain, progress independently (a network partition among validators; an RSU cluster cut from the backbone that continues to serve). Principals detect it when a newly observed chain view conflicts with a previously confirmed view (a block at height h with a different hash than the cached one). State: PARTITIONED, read-only, no acceptance. What must be refused: everything that depends on ordering, because R-ORDER is undefined until the canonical branch is chosen. What is still safe: Tier 1 (unaffected by construction), and presenting (the holder's log records which view it acted under). Recovery: the deployment's finality rule chooses the canonical branch (deterministic under QBFT: the partition with quorum; under probabilistic finality: the heavier chain beyond the finality depth); every principal then RECONCILEs, and actions accepted on the abandoned branch become retrospective invalidations.

**Revocation-storm mode.** Trigger: an issuer key compromise or a recall that revokes a large fraction of a credential population at once (the SCMS analogue is a misbehaviour-authority mass revocation). Two effects: the status list changes wholesale (cheap, one epoch root) and the accumulator must be updated for every revoked element with every remaining holder's witness needing refresh (expensive, and the holders are the vehicles). Safe behaviour: verifiers shorten τ2 to the minimum the deployment allows (a parameter, τ2,storm) for the affected credential type, and prefer status-list proofs over accumulator proofs until witnesses have been refreshed; holders whose witnesses are stale present with the status-list index instead, trading unlinkability for availability *for the duration of the storm and with the trade logged*. What must be refused: acceptance of accumulator proofs against a pre-storm accumulator value. Recovery: witness refresh completes; the epoch closes; τ2 returns to default. Document 02 quantifies the witness-update cost; the design statement here is that dual revocation (L2) is precisely what makes a storm survivable.

**Key-compromise mode.** Three sub-cases. *Holder key* (a vehicle's OBU key extracted): the controller rotates (F9 then F10) and, under R-KEY, signatures under the old key after the removal block are rejected while those in the staleness window are quarantined; the holder's credentials are unaffected because they bind to the DID, not the key, unless the issuer's policy binds them to a key, in which case re-issuance is triggered. *Issuer key*: the issuer rotates; credentials signed by the old key remain valid if issued before the rotation block (R-KEY applied to issuer signatures); a compromise detected late becomes a revocation storm for the credentials issued in the exposure window. *Endorser key* (the root-of-trust case): the endorser rotates and re-endorses; under R-ENDORSE the endorsements made under the compromised key in the exposure window are revoked with G3 and every credential issued under those endorsements in that window is invalid, which is a revocation storm one level up. What is still safe in every sub-case: Tier 1, and the audit trail, which is the point: the compromise window is bounded by block numbers and the affected set is computable. Recovery: RECONCILE plus re-issuance where the policy demands.

The five modes and their permitted-action tables are what document 04's full-coverage scenarios and document 06's low-connectivity scenarios exercise as failure branches; the test for each mode is an assertion on the trace that no `accept` occurred in a state that forbids it.

## 6. Security and integrity argument

*Claim.* Each threat in the memos' threat model is addressed by a named layer and pattern, and each has a residual risk that is stated rather than hidden.

| Threat | Layer / pattern that addresses it | Mechanism | Residual risk |
|---|---|---|---|
| Impersonation | L1 + L3 + L4 | A presentation is signed under a key that resolves (F2) to the claimed DID at the current block; the channel key derives from the challenge (L4-I1). | A compromised key impersonates until rotation; bounded by detection time and τ (key-compromise mode). |
| Replay | L3 + L4 + F8 | Fresh verifier challenge; F8 commitment binds challenge and domain on chain; channel nonces. | A verifier that reuses challenges defeats itself; the design cannot prevent verifier misconfiguration, only make it detectable in the F8 log. |
| Equivocation (presenting inconsistent state to different parties) | L2 anchors + attestation log + R-ORDER | The anchor is one object on one chain; a holder cannot present credential state that differs from the anchor without failing L2-I1; its own log, once anchored, fixes what it said. | Before the epoch anchor lands, a holder can equivocate off chain; the residual is the epoch length, a parameter. |
| Key compromise | L1 rotation + R-KEY | Rotation events are ordered; validity of signatures is a function of block time. | Signatures in the staleness window are quarantined, not resolved; the application must decide. |
| Sybil | L0 + L5 | Identity creation is cheap by design (F1 is roughly 162–179K gas on O1), so Sybil resistance comes not from creation cost but from *endorsement*: an unendorsed DID has no credentials that any policy accepts, and no reputation that any policy counts (L5-I1). | A compromised or negligent issuer can mint endorsed Sybils; bounded by the issuer's own endorsement and reputation; detected by anomaly screens the memos name, which are outside this architecture. |
| Collusion (attesters colluding on reputation) | L5 + L0 | Attester weighting by endorsement; evidence hashes on chain (L5-I2) so that colluding attesters must also fabricate evidence that any auditor can inspect. | Colluding endorsed attesters with fabricated evidence are not prevented; they are permanently attributable, which is the forensic-audit-trail primitive doing its work. Document 09 treats the reputation dynamics. |
| Credential theft | L3 holder binding + L4 | A stolen credential document is useless without the holder's key, because presentations are signed by the holder and, in BBS+/AnonCreds, the credential's link secret never leaves the holder. | Theft of credential *and* key is key compromise. |
| Mis-issuance | L0 R-ENDORSE + L2 F7 | An issuer not endorsed for the type cannot produce an acceptable credential; a mis-issued credential by an endorsed issuer is revoked (F7) and the revocation propagates within τ. | The window between mis-issuance and revocation is the issuer's detection time plus τ. |
| Supply-chain compromise (OBU firmware, RSU software) | L1 delegation + signed caches | An OBU acts as a delegate (F11, sigAuth, with validity) of the vehicle DID, not as the vehicle itself; RSU caches are signed under the RSU's DID, so a compromised RSU serving false views is attributable and its DID deactivatable (F4). | A compromised OBU acts within its delegation until the delegation expires or is removed; the validity parameter (3,600 s in S1) is the bound. |
| Reorg | R-ORDER finality depth | Events shallower than the finality depth are treated as unanchored. | Under probabilistic finality a deep reorg beyond the declared depth is a chain failure the design does not survive without manual intervention; deterministic finality (QBFT) removes the case. |
| Rollback (validator-set decision to revert) | PARTITIONED → RECONCILE | Treated as a partition whose canonical branch is chosen by governance. | Actions accepted on the rolled-back branch are retrospective invalidations; their real-world effects are not undone. |
| Partition | Partition mode | Read-only, no acceptance, until canonical branch chosen. | Availability loss for the partition's duration; Tier 1 unaffected. |
| Delayed finality | τ and anchor-pending policy | Tier 2 accepts anchor-pending objects from endorsed issuers within τ2; Tier 3 waits. | A Tier 2 acceptance of an anchor-pending credential that never lands is a retrospective invalidation. |
| Cache poisoning (not in the memos, but induced by this design) | Signed caches with block numbers | An RSU cannot serve a false view without signing it; a verifier checks age and signature. | An RSU serving a *true but stale* view is not poisoning; it is the staleness window, which is the accepted risk. |

### 6.4 The forensic audit trail against unlinkable presentations: dual-mode identity

The tension between R4 (accountability) and R6 (privacy) is resolved by the 2020 paper's dual-mode identity, made concrete. Every physical principal has a *verinym* DID (its public identity, anchored at L1 on the jurisdiction's shard, carrying its MOBI VID birth certificate [27] and registration) and any number of *pairwise or pseudonymous* DIDs used for Tier 1 streams and for unlinkable Tier 2 presentations. The verinym is the object that answers "what is the history of actions taken by vehicle V?" and closes the SCMS accountability gap. The pseudonyms are what keep routine disclosure minimal.

The link between them is the *escrowed linkage record*: for each pseudonym, a record `(pseudonymDID, verinymDID, creationBlock)` encrypted to a threshold key held by an escrow set (the design proposes the regulator, a court-appointed custodian, and the operator, t-of-n, as parameters), with the *hash* of the record anchored on chain at pseudonym creation. This mirrors the SCMS's split of linkage authority into two parties that must both cooperate to de-pseudonymise [6], and improves on it in one respect: the existence of the linkage record is itself on chain, so a pseudonym without an anchored linkage hash is by construction *not* a pseudonym of any verinym and is treated as unendorsed. Audit therefore proceeds: an authorised party obtains a threshold decryption of the linkage record, verifies its hash against the anchor, and then reads the verinym's tamper-evident history. Routine verifiers never see the linkage. Document 08 handles the channel-level consequences (a channel opened under a pseudonym is closed when the *verinym's* credential is revoked, which requires the holder's own cache, not the verifier's, to make the connection, and that is safe because the holder is the party being revoked).

## 7. Privacy when required

*Claim.* Privacy is a policy output, not a system-wide setting. The disclosure policy model determines, for every (attribute class, verifier class, tier, legal basis) tuple, the least-revealing disclosure mode that satisfies the verifier's need, and zero-knowledge proof is invoked only when that mode is `zk-predicate` or `unlinkable`.

### 7.1 The disclosure policy model

A policy is a table of rows `(attributeClass, verifierClass, tier, legalBasis) → mode`, where:

- *attributeClass* partitions credential attributes by sensitivity: `identifier` (VIN, plate, licence number), `entitlement` (licence class, registration validity, insurance in force), `measurement` (odometer, emissions reading), `biographic` (name, address, date of birth), `relational` (owner DID, fleet membership).
- *verifierClass* partitions verifiers by role and endorsement: `safety-peer` (another vehicle, Tier 1), `service-operator` (charging, tolling, parking: Tier 2), `access-controller` (gated area, Tier 2), `regulator` (DMV, inspection, police: Tier 3), `commercial-counterparty` (insurer, buyer, lessor: Tier 3), `collective-computation` (a federated-learning aggregator or map server: Tier 2/3, document 09).
- *legalBasis* is the GDPR-style ground: `contract`, `legal-obligation`, `consent`, `legitimate-interest`, `vital-interest`.
- *mode* is one of: `none` (attribute not disclosed, no proof), `plaintext-anchored` (attribute disclosed with hash-anchored integrity), `selective` (SD-JWT: only the named attributes disclosed, the rest hashed), `zk-predicate` (a predicate over the attribute is proven, the attribute is not disclosed: age ≥ 18, registration valid on date d, odometer within a class), `unlinkable` (BBS+/AnonCreds presentation with no correlating value, optionally with predicates).

A representative policy fragment, as a design proposal:

| attributeClass | verifierClass | tier | legalBasis | mode |
|---|---|---|---|---|
| entitlement (licence class) | access-controller | 2 | contract | zk-predicate (class ∈ permitted set) |
| entitlement (registration valid) | service-operator | 2 | contract | unlinkable + predicate (valid on today) |
| identifier (plate) | regulator | 3 | legal-obligation | plaintext-anchored |
| measurement (odometer) | commercial-counterparty | 3 | contract | selective (odometer disclosed; owner not) |
| measurement (sensor quality score) | collective-computation | 2 | legitimate-interest | unlinkable + predicate (score ≥ threshold) |
| biographic (any) | service-operator | 2 | any | none |
| relational (fleet membership) | access-controller | 2 | contract | zk-predicate (member of fleet set) |

The rule of composition is that the holder's wallet evaluates the policy at presentation time, given the verifier's presented class (which is itself a credential the verifier presents, under an endorsement, so verifier class is not self-asserted), and chooses the mode; the verifier's policy states the *maximum* it will accept in the other direction (a regulator will not accept `unlinkable` for a plate check). If the two are incompatible the presentation fails closed and the failure is attested. Document 02 gives the cryptographic cost of each mode and the revocation-privacy interaction; the design statement here is that the mode is chosen per row, which is what lets the architecture pay for zero-knowledge only where a row demands it.

### 7.2 When ZKP is invoked

A ZK proof is generated only for rows with mode `zk-predicate` or `unlinkable`. On the measured and digest-level evidence, this is the right economy: the on-chain F8 commitment costs 62,441 gas regardless of mode, an off-chain SD-JWT presentation costs a signature verification, an off-chain BBS+ presentation costs a pairing-based verification in the millisecond range (VehiclePassport reports 22 ms proof generation and sub-5 ms verification for vehicular attribute proofs, arXiv:2509.06133, DIGEST-LEVEL), while on-chain Groth16 verification costs roughly 200–350K gas (DIGEST-LEVEL) and is therefore reserved for the rare case in which the *chain itself* must be convinced (an agent's contract account gating an action on a ZK-verified credential, the ERC-4337 case at L1). The design rule: verification is off chain unless the party that must be convinced is a contract, and then the contract verifies a proof whose statement is small (a predicate) rather than a full credential.

### 7.3 How audit access is escrowed

§6.4 gives the linkage escrow. Two further escrow rules complete the model. First, *policy escrow*: the disclosure policy in force at the time of a presentation is itself content-addressed and its hash is included in the presentation's attestation, so an auditor can later establish what the holder was entitled to withhold. Second, *evidence escrow*: for `unlinkable` presentations that had commercial effect (a toll paid, a charge delivered), the verifier retains the presentation and its own acceptance attestation, and the holder retains the pseudonym-to-verinym linkage under the threshold escrow, so that a dispute can be resolved by combining the two under authorisation without the verifier ever having held the linkage. The Trust over IP governance stack (NEW-11, DIGEST-LEVEL) supplies the vocabulary in which the escrow set and its authorisation rules would be published as a governance framework; the EndorsementRegistry is where their DIDs are anchored.

### 7.4 GDPR and eIDAS compatibility, argued

The GDPR argument (R12) is that nothing on chain is personal data after erasure. On chain are: DID identifiers (pseudonymous key hashes; the verinym DID is linkable to a person only through the off-chain registration credential, which is erasable); F5 credential hashes, which the Building Paths preface rightly warns may themselves be personal data if the content is predictable; status-list bits and accumulator values; endorsement edges among institutional DIDs. The design's answer to the credential-hash concern is L2-I2: the canonical credential document includes a per-credential random salt, so the F5 hash is a commitment that cannot be reproduced or tested against guessed content once the document (with its salt) is deleted. That is not a novel technique, it is the SD-JWT salted-digest construction [14] applied to the whole credential; the point is that the campaign's VC layer already uses salted claim digests, so the mechanism is in the repository. The eIDAS 2.0 argument is that the presentation formats admitted (SD-JWT VC as baseline, with BBS+ where unlinkability is required) are among those the EUDI Architecture Reference Framework admits (NEW-8, DIGEST-LEVEL; not read at source), and that the unlinkability requirement the ARF places on person-identification presentations is satisfied by the `unlinkable` mode. Both arguments are legal, not empirical; they are carried as open questions (§14) for the researcher to confirm with a source read at source.

## 8. Cost and scalability

*Claim.* The whole architecture's on-chain cost is a linear function of the number of anchored events divided by the batch size, plus the per-principal lifecycle cost; reads cost nothing on chain; and the architecture is cheaper than SCMS-plus-databases wherever the *audit* property is required and more expensive wherever it is not.

### 8.1 The parametric model

Variables: N vehicles; M agents; per vehicle per year, k_key key events (F9/F10/F3), k_del delegate events (F11), k_cred credentials received (F5 by the issuer), k_rev revocations affecting it (F7), k_pres chain-committed presentations (F8, only where policy requires), k_att reputation attestations (C1); per agent per year the same with primes; b the batch size for Merkle-anchored logs; G_root the gas of one root write (a hypothesis: one SSTORE new slot at 20,000 gas plus call overhead, DIGEST-LEVEL for the SSTORE figure; target <60K until measured); λ the L2 cost factor (λ = 1 on L1; λ < 1 measured per rollup); p the gas price in the deployment's unit of account.

Anchor points, all real O1 measurements from the S1 trace and labelled by function:

| Symbol | Function | Measured gas (O1, S1 trace) |
|---|---|---|
| G_F1 | createDID | 161,823–178,935 |
| G_F3 | updateDID | 44,760 |
| G_F4 | deactivateDID | 55,127 |
| G_F5 | issueCredential | 130,163 |
| G_F7 | revokeCredential | 32,980 |
| G_F8 | createPresentation | 62,441 |
| G_F9 | addVerificationMethod | 59,607 |
| G_F10 | removeVerificationMethod | 36,478 |
| G_F11 | addDelegate | 54,227 |

Per-vehicle one-time cost: `G_once = G_F1 + (initial keys) · G_F9 + (initial delegates) · G_F11`. Per-vehicle annual cost:

`G_year(v) = k_key · G̅_key + k_del · G_F11 + k_cred · G_F5 + k_rev · G_F7 + k_pres · G_F8 + k_att · G_C1 + (E_v / b) · G_root`

where G̅_key is the mean of the key-event gas values and E_v is the number of off-chain attestations the vehicle logs per year (every presentation made or accepted, every channel), which are *never* individually on chain. G_C1 is unmeasured (O7 is not confirmed live) and is carried as a hypothesis. Fleet cost per year: `G_fleet = N · G_year(v) + M · G_year(a)`, and the money cost is `λ · p · G_fleet`.

An illustrative evaluation of the formula, stated as arithmetic on measured gas and not as a measurement: a vehicle with k_key = 2 (one rotation: F9 then F10, 59,607 + 36,478), k_del = 2 (two OBU delegate renewals at 54,227), k_cred = 4 (registration, insurance, inspection, one lifecycle event, at 130,163 each), k_rev = 1 (32,980), k_pres = 0 (Tier 2 policy does not require chain commitment), E_v = 2,000 attestations at b = 2,000 (one daily epoch root, so E_v/b ≈ 365 roots... which shows the batch parameter must be stated as roots per year, r = 365) gives `G_year ≈ 96,085 + 108,454 + 520,652 + 32,980 + 365 · G_root`. With G_root at its <60K target the last term is ≈ 21.9 M gas, dominating everything else, which is the point of stating the formula: the *epoch length* is the cost lever, not the credential count. At one root per week (r = 52) the term is ≈ 3.1 M gas; at one root per month, ≈ 0.7 M gas. The trade is against equivocation exposure (§6): a longer epoch is cheaper and lets a holder equivocate off chain for longer before its log is fixed. The parameter belongs to the deployment, and the demonstration plan measures G_root rather than assuming it.

### 8.2 The effect of batching, L2, and read-caching

*Batching.* The root term is `r · G_root` regardless of E_v, so per-attestation on-chain cost is `G_root / (E_v / r)`, which goes to zero as the epoch lengthens. Batching F5 (spec §6 batch ops) would similarly amortise the 130,163-gas issuance across a Merkle root of credential hashes, at the cost of per-credential inclusion proofs the verifier must check; the design leaves per-credential F5 in place for Tier 3 credentials (legal effect wants an individual anchor) and proposes batched anchoring for high-volume Tier 2 credentials such as oracle observations. Not assumed; a build item (§9.3).

*L2.* Every term scales by λ. Because the design's reads are all local, moving the anchors to an L2 costs nothing in read latency; it costs τ3 (finality to L1 is delayed by the rollup's posting interval) and it costs the cross-domain verifier a Merkle proof. For Local CVIN shards under QBFT, λ is not a cost factor but a *pricing decision* of the consortium, and the relevant scarce resource is validator throughput, which is what Caliper measures (§10.2).

*Read-caching.* On-chain read cost is zero (F2, F6, F12, G4 are views) and the design keeps it zero at every tier. What the cache buys is *latency*: a Tier 2 verification that requires no network round trip is bounded by local signature and proof verification, which is the only way the 100–500 ms tier is met on a variable-load, intermittent link. The cost moved off chain is edge storage and refresh bandwidth: an RSU holds, per credential type it serves, one status list (a bitstring of L bits for L credentials of that type in the jurisdiction) refreshed once per epoch, plus DID documents for the vehicles in its coverage; both are O(population served), not O(N).

### 8.3 Scaling argument

Writes: the chain sees `N · (lifecycle events) + (N + M) · r` transactions per year, that is, O(events / b) where b is the effective batch (the attestation volume per root). This is independent of interaction volume, which is the property SCMS-plus-databases lacks: in a database design every interaction the operator wants auditable is a write to a database the operator controls, so audit volume and write volume are the same number. Reads: O(1) in N for every principal, because the cache holds only what the principal's counterparties and services need, and content-addressed data is served from any cache without trust. The one term that grows with N on the read side is the RSU's status-list footprint, and it grows with the *jurisdiction's* population, not the national fleet, which is exactly what the Local CVIN shard bounds.

### 8.4 Where it is cheaper than SCMS-plus-databases, and where it is not

Cheaper: wherever the property required is *cross-organisational, tamper-evident audit*. In SCMS the misbehaviour authority, the linkage authorities, and the operators each keep databases whose consistency with one another is a matter of procedure; reconciling them after a dispute is an organisational cost that scales with the number of parties. In this architecture the anchor is one object, reconciliation is R-ORDER, and the audit trail is the chain plus Merkle proofs. Also cheaper: wherever the property required is *portability* (the IDPP), because a database identity does not port; it is re-created.

Not cheaper: for the raw provisioning of pseudonym certificates at Tier 1, which SCMS does in bulk with a butterfly-key expansion and no per-certificate ledger write, and which this architecture does not attempt to do (R1). Not cheaper: for high-frequency Tier 2 events in a single operator's domain where no cross-party audit is ever needed (a private parking operator with its own customers); there a database wins on every axis, and the architecture's honest position is that such an operator should use the architecture only for the *credentials* it accepts, not for its own logs. Not cheaper: for the first year, because the one-time G_once per vehicle across a national fleet is a capital cost with no database analogue; at the O1 measured F1 cost and 33 million vehicles (DIGEST-LEVEL) it is on the order of 5–6 × 10^12 gas, which is a figure to be confronted, not hidden, and which is the strongest argument for a permissioned shard where gas is not priced against a public market.

## 9. Realisability

### 9.1 What exists today, precisely

In the sandbox `5_minimal-ssi-sandbox/` (v1.3, 2026-06-05): the interfaces `IMinimalSSI.sol`, `ISetA.sol`, `ISetB.sol`, `ISetC.sol` compile clean at solc 0.8.24; `O1_ERC1056.sol` passes the 12-test parameterised compliance suite; scenario `scenarios/run_i2i.js` (S1) has been executed against O1 producing `traces/i2i_O1_ERC1056_1780620182135.jsonl` with 22 entries covering 12/12 functions and the gas values of §8.1, plus the off-chain ECDH P-256 and AES-256-GCM step and the mid-session revocation teardown. Files `O2_ERC721.sol` through `O8_LFDT.sol` are present in `contracts/implementations/` as ports whose compliance is prior evaluation pending confirmation; they are not cited here as evidence. The directory `contracts/credentials/` exists and is empty; there is no `lib/` directory; `scenarios/` contains only `run_i2i.js`. The planned VID layer (EndorsementRegistry, CredentialTypeRegistry, `lib/vid/`, S7 `run_vid_minimal.js`, S8 `run_vid_lifecycle.js`, `test/vid.js`) is therefore under construction and no number from it exists; document 10 will report it when it does.

In the wider repository (branch `vid-build`): `2_w3c-ssi-layer/` holds a Python DID resolver for did:ethr, did:nft, did:key, and did:mobi, and a VC layer with EIP-191 secp256k1 Data Integrity proofs over canonical JSON, SD-JWT-style salted claim digests for selective disclosure, registry-based `credentialStatus` revocation, and ten automotive credential schemas plus EmissionsCompliance. This is the L2 and baseline-L3 implementation the design assumes, in Python. `cv2x-testbed/` holds MOBIVIDRegistry v1/v2 in Solidity: the VID I birth certificate (VIN hash, encrypted VIN, birth-certificate hash), the VID II lifecycle with 11 event types and 8 issuer roles, multi-party attestations, a SUMO harness, and a centralised-PKI comparison provider. This is the domain content of L2 for vehicles and the comparison baseline for §8.4.

### 9.2 What is off the shelf

| Layer | Off-the-shelf candidate | What it supplies | Label |
|---|---|---|---|
| L1 (vehicles) | Veramo (did:ethr, ERC-1056 registry) | Resolver, key management, JWT/LD credential plugins | DIGEST-LEVEL (tool not exercised in this pass) |
| L1 (agents) | ERC-4337 bundler/entry-point reference; ERC-7579 module reference | Contract-account validation with pluggable policy | DIGEST-LEVEL |
| L2/L3 (AnonCreds) | anoncreds-rs (OWF), ACA-Py or Credo-TS | CL credentials, accumulator revocation, ZK presentations; agent framework | DIGEST-LEVEL; Aries archived Apr 2025, successors under OWF |
| L2/L3 (BBS+) | W3C Data Integrity BBS cryptosuite implementations; AnonCreds v2 | Unlinkable presentations | DIGEST-LEVEL |
| L3 (ZK predicates on chain) | snarkjs + circom; Semaphore for set membership | Groth16/PLONK proof generation and Solidity verifiers | DIGEST-LEVEL |
| L0/L1 substrate | Hyperledger Besu, QBFT consensus | Permissioned EVM with deterministic finality; same substrate as E1 | DIGEST-LEVEL |
| L6 (oracles) | Chainlink (whitepaper) | Decentralised oracle networks; the 2020 paper's reference | DIGEST-LEVEL |
| L6 (storage) | IPFS/Arweave or enterprise object store with CID addressing | Content-addressed off-chain storage | DIGEST-LEVEL |
| Benchmark | Hyperledger Caliper | Workload modules per function; TPS, p50/p95 latency vs Besu SUTs | DIGEST-LEVEL; named in ARCHITECTURE.md §2.3 as the Stage 3 instrument |

### 9.3 What must be built, and the staged plan with gates

The programme's gate/trace method requires each stage to name its trace and its acceptance assertion. Scenario identifiers S9–S12 below are proposals for the catalog and are subject to the master plan's (00) decision; S7 and S8 are the campaign's already-named build.

| Stage | Build item | Trace it produces | Acceptance assertion (gate) |
|---|---|---|---|
| B0 (done) | O1 + S1 | `traces/i2i_O1_ERC1056_*.jsonl` | 12/12 fnIds present; `revokeCredential` followed by `verifyCredential` with `valid=false`. Met. |
| B1 | EndorsementRegistry (G1–G4), CredentialTypeRegistry, `lib/vid/` builders, S7 `run_vid_minimal.js`, `test/vid.js` | `traces/vid_minimal_O1_*.jsonl` | Compliance suite still 12/12 unmodified (R9); every `issueCredential` entry is preceded by an `isEndorsed=true` view for its type; one revoked credential re-verifies `valid=false`; presentation challenge-bound. |
| B2 | S8 `run_vid_lifecycle.js`: 11 lifecycle types, 8 roles, odometer monotonicity off chain, theft → recovery, decommission | `traces/vid_lifecycle_O1_*.jsonl` | Every lifecycle credential's issuer role matches its type's permitted roles; an issuance by a non-endorsed role reverts with NotAuthorized (or is refused off chain and logged); odometer regression is refused off chain. |
| B3 | Signed local cache + attestation log + RECONCILE (JS, in `lib/cache/`); S9 "delayed-write reconciliation": vehicle goes offline, presents and accepts within τ2, a revocation lands while offline, vehicle reconnects | `traces/reconcile_O1_*.jsonl` with `kind: offchain` entries for cache decisions and a `reconcile` summary | Exactly one RETROSPECTIVE_INVALIDATION, naming the offline acceptance and the F7 event; zero acceptances after cache age exceeded τ2; RECONCILE run twice yields identical output. |
| B4 | Dual revocation: status-list epoch root contract beside IMinimalSSI; accumulator via anoncreds-rs off chain; both derived from the F7 log; S10 "revocation storm" | `traces/revstorm_O1_*.jsonl` | After k revocations in one epoch, status-list and accumulator disagree for zero credentials (L2-I3); a verifier presented with an accumulator proof against the pre-storm value refuses. |
| B5 | BBS+ presentation path (off chain) with policy table of §7.1; S11 "policy-selected disclosure": same credential presented to `access-controller` (zk-predicate) and `regulator` (plaintext-anchored) | `traces/disclosure_O1_*.jsonl` | Two `unlinkable` presentations of one credential to two verifiers share no byte string longer than the format's fixed headers; the regulator presentation reveals the plate; the F8 commitment gas is recorded for each. |
| B6 | IDPP port with continuity proof (S5 as catalogued, O1 → O8/E1 once E1 is confirmed compliant), plus shard anchoring (epoch root of a Local CVIN to a backbone contract) | `traces/idpp_O1_O8_*.jsonl` | Destination verifier accepts a presentation of a source-issued credential; source DID resolves with the "moved" flag; the port-out inclusion proof verifies against the backbone root. |
| B7 | Besu QBFT network (4 validators) + Caliper workloads for F1–F12 and G1–G4; measure G_root and the τ2 propagation time | Caliper reports + `traces/*_besu_*.jsonl` | TPS and p95 latency reported per function; G_root measured (replaces the <60K hypothesis); `t_reject − t_include` measured for a revocation (replaces the τ2 default with an observed lower bound). |
| B8 | Hardware slice: AURORA/OBU/RSU with RSU acting as cache server | Field traces | The Tier 2 interaction completes with zero chain calls on the OBU (R1/R5 in the field); RSU-signed cache entries verify on the OBU. |

Gates are sequential for B1–B3 (each depends on the previous), B4 and B5 are parallel after B3, B6 depends on E1 confirmation (outside this campaign's scope), B7 depends on B1–B5, and B8 on B7. The rule the build inherits from `CLAUDE.md` is that a scenario that cannot meet its assertion natively is not stubbed to green; the coverage consequence is recorded in `docs/FINDINGS.md`.

## 10. The demonstration plan

*Claim.* The architecture can be demonstrated in three slices of increasing cost, and each slice proves something specific and cannot prove something specific.

### 10.1 The minimum demonstrable slice: twenty minutes on a laptop

Requires B1–B5 complete on Hardhat's local EVM. The demonstration replays traces in the Identity Sandbox Explorer (Layer 2 of the sandbox design) and, where live execution is cheap, runs it.

| Minute | What is shown | Which trace | What the audience sees proven |
|---|---|---|---|
| 0–3 | S1 replayed: three DIDs, two credentials, key and delegate setup, mutual authentication by views, the F8 challenge-bound commitment, the off-chain AEAD step, the mid-session revocation and teardown | `i2i_O1_ERC1056_1780620182135.jsonl` (exists) | The hybrid boundary is real: identity state on chain, the channel off chain, revocation propagating across the boundary. Real gas on every tx. |
| 3–7 | S7 replayed: endorsement graph built (ministry → DMV for DRIVER_LICENCE; OEM → plant for VID_BIRTH), three typed credentials issued with endorsement gating, one revoked | `vid_minimal_O1_*.jsonl` (B1) | L0 governance is explicit and enforced; the endorsed-at-issuance rule is visible as the view preceding each issuance. |
| 7–10 | S8 replayed at speed: the eleven lifecycle events, a theft report and recovery, decommission; one refused issuance by a wrong role | `vid_lifecycle_O1_*.jsonl` (B2) | The MOBI VID II lifecycle sits above IMinimalSSI unaltered; multi-issuer, role-gated. |
| 10–14 | S9 run live: the vehicle's cache is snapshotted, the chain is "disconnected" (the script stops reading), a Tier 2 presentation and acceptance happen from cache, a revocation is written by the issuer, the vehicle "reconnects" and RECONCILE emits one retrospective invalidation | `reconcile_O1_*.jsonl` (B3) | Delayed-write and bounded-staleness are real and deterministic; the invalidation is attributable to two signed, anchored records. |
| 14–17 | S10 excerpt: a batch of revocations; the status list and accumulator both update; a stale accumulator proof is refused | `revstorm_O1_*.jsonl` (B4) | Dual revocation from one truth; the storm is survivable. |
| 17–20 | S11 run live: one credential, two verifiers, two modes; the two unlinkable presentations shown side by side with no common value; the regulator presentation shown with the plate; F8 gas identical for both | `disclosure_O1_*.jsonl` (B5) | Privacy is a policy output; ZK is invoked only where the row demands it; accountability survives. |

What the laptop slice cannot prove: any latency claim (Hardhat's local EVM has no network, no consensus, no gossip), any throughput claim, any τ2 propagation time, and any claim about the wireless constraints. It proves *structure* and *ordering* and *gas*, which is what the sandbox was designed to make citable.

### 10.2 The testnet slice

Requires B7. A four-validator Besu QBFT network, the O1 registry and the governance and status-list contracts deployed, Caliper workloads for every function, and the S9–S11 scripts pointed at the network instead of Hardhat. What it adds: measured block time and finality, measured G_root, measured `t_reject − t_include` for a revocation across the network (the first real τ2 lower bound), TPS and p50/p95 per function, and the cross-option table that feeds C12–C13 when O2–O8 are confirmed. What it cannot prove: anything about the radio link, the OBU's compute budget, or intermittent coverage, because the testnet's principals are processes on a LAN.

### 10.3 The hardware slice

Requires B8. The programme's AURORA/OBU/RSU hardware with the RSU running a cache server (an L1–L2 view signed under the RSU's DID and refreshed from the testnet) and the OBU running the holder wallet and the verifier role of §3.2. What it adds: the Tier 2 interaction measured end to end on a real link, the RSU-signed cache verified on the OBU, a coverage gap induced by moving the vehicle (or attenuating the link) and the resulting OFFLINE_FRESH → OFFLINE_STALE transition observed on the OBU, and the reconnection reconcile. What it cannot prove: fleet-scale behaviour (N is a handful), revocation-storm dynamics at population scale, or anything about a public L1. Those remain modelled (§8) until a larger deployment exists, and the document is explicit that they are modelled.

## 11. How this becomes Family F

*Claim.* Family F is a composite specification in which each layer of §2 is supplied by a named standard, stated as a Stage 3 hypothesis with the evidence still owed to confirm it; it is not a new implementation and it must never become one in the Stage 1 sandbox.

| Layer | Supplied by | Family / option of origin | Evidence in hand | Evidence owed |
|---|---|---|---|---|
| L0 Governance | EndorsementRegistry beside IMinimalSSI; anchored epoch roots | Campaign build (spec §6 governance extension) | None yet (B1) | S7 trace; G1–G4 gas |
| L1 Vehicles | ERC-1056 event-sourced pattern [23] | Family A, O1 | 12/12 compliance; S1 gas | Confirmation on Besu; createDID deviation analysis (Stage 15 item) |
| L1 Agents | ERC-4337 account [24] + ERC-7579 modules | Family C, O6 | Prior Set A score 18/24, pending confirmation | O6 compliance run; policy-module gas |
| L2 Anchors and revocation | F5/F7 on O1; status-list root contract; accumulator via AnonCreds lineage | Family A + Family E (E3) | F5 130,163 and F7 32,980 measured | B4 trace; witness-update cost (02) |
| L3 Presentation | SD-JWT baseline [14]; BBS+ (Data Integrity BBS / AnonCreds v2) for unlinkability; Groth16/PLONK verifiers only for contract-side predicates | Family E (E3) + tooling | F8 commitment 62,441 measured; Python VC layer with salted digests | B5 trace; proof-time measurements (02) |
| L4 Transport | Challenge-bound AEAD channel (S1 pattern); DIDComm v2 as the message envelope where interoperability with OWF agents is required | Campaign (S1) + DIF DIDComm | S1 off-chain step | 08's crux scenarios |
| L5 Trust signals | ISetC per ERC-8004 registries [19] | Family D, O7 | Prior Set A score 15/24 (below viability as an *anchor*; adequate as a *registry*) | O7 compliance run; C1 gas |
| L6 Data/oracle | CID-addressed storage; oracles as endorsed issuers | 2020 paper concept [5] + tooling | None | B2 (inspection oracle as SERVICE_CENTER/GOVERNMENT_INSPECTION issuer) |
| Substrate | Besu QBFT shard with backbone anchoring; L2 optional | Family E (E1) substrate | None | B7 Caliper |

The composite is a hypothesis in the precise sense the method demands: it predicts that a system assembled from these parts satisfies R1–R13 with the placements of §2.8 and the parameters of §3.4, and each row names the trace that would confirm or refute its part. The intersectional benchmark (C12) is what produces the cross-option evidence for the "supplied by" column, and the minimum-cost composite (C13) is what §8 becomes once G_root, G_C1, and λ are measured rather than hypothesised.

## 12. Methodology hooks for Chapter 4

Three hooks are offered for the evaluation chapter. First, the requirement set of §1 is an *acceptance-metric table* and can be adopted as the rubric against which every option's Stage 2 overlay is scored, replacing the informal "coverage F/P/X" with "which R-rows does this option satisfy natively, which with an adapter, and which not at all". Second, the reconciliation rules of §3.3 are *executable*: the RECONCILE procedure over a recorded trace is a deterministic function, and its determinism, revocation-monotonicity, and attributability properties are unit tests, which places a design claim under the same evidentiary regime as a gas claim. Third, the demonstration slices of §10 are ordered by what they cannot prove, which gives the limitations section of Chapter 5 its structure for free: each slice's "cannot prove" column is a limitation with a named remedy.

## 13. Sources used in this document

| R# / NEW-n | Source | Verification state | How used |
|---|---|---|---|
| [5] | Prakash, Michelson, Feng, CVIN, IEEE VTC2020-Spring | VERIFIED AT SOURCE (via the brief's extraction) | Tiers, wireless constraints, Local CVINs/IDPP, sidechains, distributed oracles, dual-mode identity |
| [6] | Brecht et al., SCMS, IEEE T-ITS 2018 | DIGEST-LEVEL | Linkage-authority split as escrow precedent; misbehaviour-authority mass revocation |
| [8] | W3C DID Core 1.0 | DIGEST-LEVEL | Set A semantics |
| [9], [10] | W3C VC Data Model 1.1 / 2.0 | DIGEST-LEVEL | Credential and presentation objects at L2/L3 |
| [11] | Rodriguez Garzon et al., AI agents with DIDs and VCs | DIGEST-LEVEL | Agent principals hold keys, present VCs, sign actions |
| [12] | Camenisch and Lysyanskaya, CRYPTO 2004 | DIGEST-LEVEL | Accumulator and CL lineage at L2/L3 |
| [14] | Fett, Yasuda, Campbell, SD-JWT, RFC 9901 | DIGEST-LEVEL | Baseline presentation format; salted-digest construction reused for L2-I2 |
| [19] | De Rossi et al., ERC-8004 | DIGEST-LEVEL | L5 registries and evidence-URI pattern |
| [22] | Dunphy, blockchain trilemma for decentralised identity | DIGEST-LEVEL | Trade-off framing for shards vs backbone |
| [23] | ERC-1056 | DIGEST-LEVEL | L1 vehicle anchor pattern |
| [24] | ERC-4337 | DIGEST-LEVEL | L1 agent anchor pattern |
| [25] | LFDT, Indy on Besu | DIGEST-LEVEL | Besu QBFT as shared substrate; E1 |
| [27] | MOBI VID I–II | DIGEST-LEVEL | Verinym content; lifecycle families at L2 |
| [28] | IEEE 1609.2-2022 | DIGEST-LEVEL | Tier 1 governance; pseudonym certificate lifetime |
| Sandbox trace | `5_minimal-ssi-sandbox/traces/i2i_O1_ERC1056_1780620182135.jsonl` | VERIFIED AT SOURCE (read in full) | All measured gas values in §2, §6, §8, §11 |
| Sandbox docs | `docs/ARCHITECTURE.md` v1.1, `CLAUDE.md`, `scenarios/run_i2i.js`, `traces/SCHEMA.md` | VERIFIED AT SOURCE (read in full) | Family F hard rule; scenario catalog; S1 mechanics; trace contract |
| NEW-1 | W3C Bitstring Status List v1.0 | DIGEST-LEVEL | Status-list revocation at L2 |
| NEW-2 | W3C Data Integrity BBS Cryptosuite | DIGEST-LEVEL | Unlinkable presentations at L3 |
| NEW-3 | EIP-2929 (SLOAD/SSTORE costs) | DIGEST-LEVEL | SSTORE 20,000 in the G_root hypothesis |
| NEW-4 | EIP-4844 | DIGEST-LEVEL | Noted as a cheap ephemeral-data option; not relied upon |
| NEW-5 | Chainlink whitepaper | DIGEST-LEVEL | L6 oracle networks |
| NEW-6 | Merkle proofs / light clients (general) | DIGEST-LEVEL | Anchor validity via inclusion proofs; IDPP continuity proof |
| NEW-7 | IPFS / Arweave | DIGEST-LEVEL | Content addressing at L6 |
| NEW-8 | eIDAS 2.0 / EUDI ARF | DIGEST-LEVEL; not read at source | Admitted formats; unlinkability requirement (§7.4) |
| NEW-9 | GDPR (Art. 17 erasure; personal-data definition) | DIGEST-LEVEL; not read at source | R12 argument (§7.4) |
| NEW-10 | ERC-7579 | DIGEST-LEVEL | Agent policy modules at L1 |
| NEW-11 | Trust over IP governance stack | DIGEST-LEVEL | Vocabulary for escrow governance (§7.3) |
| NEW-13 | Hyperledger Caliper | DIGEST-LEVEL | Testnet slice instrument |
| NEW-14 | Hyperledger Besu QBFT | DIGEST-LEVEL | Substrate with deterministic finality |
| NEW-15 | ALLOSAUR / AnonCreds revocation accumulators | DIGEST-LEVEL | Accumulator revocation at L2; storm mode |
| NEW-16 | Veramo; ACA-Py / Credo-TS; anoncreds-rs; snarkjs / circom; Semaphore | DIGEST-LEVEL; tools not exercised in this pass | Off-the-shelf table (§9.2) |
| NEW-17 | VehiclePassport, arXiv:2509.06133 | DIGEST-LEVEL | Proof-time figures cited with label (§7.2) |
| NEW-18 | Canada registered-vehicle count (≈33 M) | DIGEST-LEVEL | Fleet-scale arithmetic (§8.4) |

## 14. Registry delta rows

| Content Block | T | Source | Ch. | Ready % | Notes |
|---|---|---|---|---|---|
| HDA ranked requirement set R1–R13 with acceptance metrics | B | 03 §1 | 4, 5 | 70 | Rubric for Stage 2 scoring; parameters (τ, G_year) unmeasured |
| Seven-layer hybrid architecture L0–L6 with placement table | A/B | 03 §2 | 5 | 75 | Family F skeleton; O2–O8 evidence pending |
| Anchor · Cache · Attest · Reconcile pattern, state machine and RECONCILE rules | A | 03 §3 | 5 | 80 | Executable as unit tests after B3 |
| Staleness-window table per tier (τ1 n/a, τ2 300 s, τ2,doc 3,600 s, τ3 0, τ_gov 86,400 s) | B | 03 §3.4 | 4, 5 | 50 | Proposed defaults; measurement owed by B7 |
| Tier-to-chain-interaction matrix | B | 03 §4.1 | 4 | 80 | Extends C6 |
| IDPP as anchor migration with continuity proof | A | 03 §4.3 | 5 | 60 | Makes 2020 concept testable; S5 dependency on E1 |
| Five degraded modes with permitted/refused actions | A/B | 03 §5 | 5 | 75 | Failure branches for 04/06 scenarios |
| Threat-to-layer mapping with residual risks | B | 03 §6 | 4, 5 | 80 | Memo threat model coverage; adds cache poisoning |
| Dual-mode identity with escrowed linkage records | A | 03 §6.4 | 5 | 70 | SCMS LA precedent; closes accountability gap |
| Disclosure policy model (attributeClass × verifierClass × tier × legalBasis → mode) | B | 03 §7.1 | 5 | 65 | Feeds 02; legal rows need source-level confirmation |
| Parametric cost model with O1 anchor points and epoch-length lever | B | 03 §8 | 4, 5 | 60 | G_root, G_C1, λ hypotheses; illustrative arithmetic labelled |
| Where hybrid beats SCMS-plus-databases and where not | A | 03 §8.4 | 5 | 70 | Honest cost position incl. one-time fleet cost |
| Realisability inventory: exists / off-the-shelf / must-build | B | 03 §9 | 4, 5 | 85 | Precise repo state as of 2026-09-03 |
| Staged build plan B0–B8 with traces and gate assertions | B | 03 §9.3 | 4 | 75 | S9–S12 identifiers proposed, pending 00 |
| Three-slice demonstration plan with "cannot prove" columns | B | 03 §10 | 4, 5 | 75 | Limitations structure for Ch. 5 |
| Family F composite specification skeleton with evidence owed | B | 03 §11 | 5 | 65 | Stage 3 hypothesis; C12–C13 feed |

## 15. Open questions for the researcher

1. **Epoch length and equivocation exposure.** The cost model shows the log-anchoring epoch, not credential volume, dominates on-chain cost, and the epoch is also the window in which a holder can equivocate off chain. Only the researcher can decide the deployment's acceptable exposure (daily, weekly, monthly) and whether it differs for vehicles and agents; the choice fixes r in §8.1.

2. **Escrow set composition and threshold.** §6.4 proposes regulator, court custodian, and operator with t-of-n. Whether the thesis wants to commit to a specific set (and whether ICBC-style provincial insurers belong in it, following the 2020 paper's example) is a governance stance the researcher must take before 11 folds the dual-mode argument into Chapter 5.

3. **Stale-verifier policy default.** §3.2 leaves "accept-with-flag" versus "refuse" under OFFLINE_STALE as a per-verifier-class parameter. The researcher should decide the default for the CAV scenarios in 04–06 (the document leans to refuse for access-controllers and accept-with-flag for service-operators) because it changes what those scenarios demonstrate.

4. **Permissioned shard versus public backbone for the reference deployment.** §8.4 argues the one-time fleet cost is the strongest case for a permissioned shard; §2.1 argues cross-jurisdiction proof is the strongest case for a public backbone anchor. The demonstration plan can only build one first; the researcher must choose which the testnet slice targets (the document assumes Besu QBFT).

5. **Batched F5 as a spec §6 extension.** Batching credential anchors for high-volume Tier 2 credentials would change the per-credential evidence a verifier needs (an inclusion proof). Whether the thesis wants to admit a batched-anchor variant into the Family F composite, or keep per-credential F5 as the only anchor form for conformance reasons, is a specification decision.

6. **Legal sources at source.** The GDPR and eIDAS/EUDI ARF arguments in §7.4 are DIGEST-LEVEL. The researcher should decide whether Chapter 5 makes the legal-compatibility claim at all, and if so, which two sources will be read at source to support it.

7. **Whether O7's registry role is admissible below the viability threshold.** ERC-8004 scored 15/24 as a Set A *anchor* (below viability) but is proposed here as the L5 *registry* only. The researcher must decide whether the thesis's viability rule applies per role or per standard, since Family F depends on the former reading.
