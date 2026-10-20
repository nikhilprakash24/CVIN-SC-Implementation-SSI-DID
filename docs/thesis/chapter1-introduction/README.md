# Chapter 1 — Introduction (Working Draft)

**Status**: working draft. This chapter motivates the study, states the
research problem and the gap it addresses, sets out the research questions and
falsifiable hypotheses that organize the work, and previews the contributions
and the structure of the thesis. It is deliberately forward-looking: the
literature that positions this work is surveyed in Chapter 2, the methods that
produce every quantitative claim are specified in Chapter 3, the system that
was built is described in Chapter 4, and the measured results — to which the
headline numbers quoted here are forward-references — are reported in
Chapter 5. Where a result is previewed here it is stated as a pointer to its
Chapter 5 provenance, not re-derived.

---

## 1.1 Motivation and Context

### 1.1.1 Vehicles are becoming networked identities

Connected and Autonomous Vehicles (CAVs) no longer act as isolated machines.
Through Vehicle-to-Everything (V2X) communication — vehicle-to-vehicle (V2V),
vehicle-to-infrastructure (V2I), and vehicle-to-network exchanges — a modern
vehicle continuously broadcasts and consumes safety-critical messages: its
position, heading, and speed in Basic Safety Messages (BSMs) at roughly 10 Hz,
and event notifications that drive applications such as Forward Collision
Warning (FCW), Emergency Electronic Brake Light (EEBL), and Intersection
Movement Assist (IMA). Because a receiving vehicle may act autonomously on a
message it did not originate — braking, steering, or re-routing — the value of
V2X is bounded by a single prerequisite: the receiver must be able to *trust
that the sender is who it claims to be*, and to make that trust decision inside
a hard real-time envelope of roughly 100 ms end-to-end.

Trust in this setting is not a one-time event. A vehicle has a **lifelong
digital identity** that must persist and evolve across a chain of custody
spanning manufacture, sale, registration, ownership transfer, maintenance,
inspection, recall, and eventual decommissioning — often over one to two
decades and across multiple owners, jurisdictions, and service providers. The
identity substrate must therefore support not only fast authentication at
message time but also a durable, auditable lifecycle record, all while
respecting the privacy of the vehicle and its operators.

### 1.1.2 Centralized PKI versus Self-Sovereign Identity

The prevailing approach to V2X trust is a **centralized Public Key
Infrastructure (PKI)**. In the IEEE 1609.2 / SAE model, a Security Credential
Management System issues short-lived pseudonym certificates that vehicles use
to sign safety messages, with certificate authorities and revocation lists
anchoring the chain of trust. This model is mature and delivers fast
signature verification, but it concentrates trust in a set of central
authorities: it presumes always-available certificate and revocation
infrastructure, ties a vehicle's credentials to issuer availability and
policy, and offers the vehicle owner little sovereignty over the identity data
that describes their asset.

**Self-Sovereign Identity (SSI)** proposes a different arrangement in which the
subject — here, the vehicle and, by extension, its owner — holds and controls
its own identifiers and credentials, presents them directly to verifiers, and
depends on no single issuer being online at verification time. The World Wide
Web Consortium (W3C) has standardized the core building blocks: **Decentralized
Identifiers (DIDs)**, which are self-controlled, cryptographically verifiable
identifiers that resolve to a DID Document describing the subject's keys and
services (DID Core v1.0), and **Verifiable Credentials (VCs)**, a data model
for tamper-evident, cryptographically signed claims that a holder can present
and a verifier can check offline (VC Data Model v2.0). The broader positioning
of SSI relative to PKI, and the prior work applying each to vehicular settings,
is surveyed in Chapter 2.

### 1.1.3 Why blockchain, W3C DID/VC, and MOBI VID

SSI needs a **root of trust** for its identifiers and for the anchoring and
revocation of credentials that does not itself reintroduce a single central
authority. A blockchain — an append-only, publicly verifiable, tamper-evident
ledger — is a natural candidate: it can host self-controlled identifiers,
anchor credential commitments and lifecycle events, and expose a revocation
surface, all without a privileged operator. The Ethereum ecosystem in
particular has produced a family of token and identity standards (the ERC and
LSP series, and account-abstraction designs) that can each serve as an
on-chain identity substrate, and the W3C DID method registry already includes
Ethereum-native methods such as `did:ethr`. This makes **blockchain + W3C
DID/VC** a concrete, standards-aligned way to realize vehicular SSI: the chain
roots the identity, the DID layer makes it W3C-resolvable, and the VC layer
makes credentials verifiable offline — the last property being exactly what a
100 ms V2V budget demands.

At the industry level, the **Mobility Open Blockchain Initiative (MOBI)** has
defined the **Vehicle Identity (VID)** standard as a blockchain-anchored
"digital birth certificate" (VID I) and lifecycle record (VID II) for
vehicles. MOBI VID gives this thesis an authoritative, domain-specific target
for *what* a vehicle identity should contain and how its lifecycle should be
structured, complementing the W3C's cross-domain identity primitives.

### 1.1.4 The automotive constraints

What makes vehicular identity a distinct research problem — rather than a
direct application of general-purpose SSI — is the set of constraints the
automotive setting imposes simultaneously:

- **Cost.** On-chain operations cost gas. A design that anchors identity or
  lifecycle events on-chain is only viable at fleet scale if its per-operation
  cost is modest, and different standards differ by more than an order of
  magnitude on exactly this axis (RQ1).
- **Latency.** Safety-critical V2V applications operate within a ~100 ms
  end-to-end budget. Any identity verification performed at message time must
  fit inside that envelope, which effectively rules out on-chain reads on the
  hot path and puts a premium on offline-verifiable credentials (RQ4).
- **Privacy.** A vehicle identity is bound to sensitive data — most obviously
  the Vehicle Identification Number (VIN) — and to the location traces implied
  by continuous BSM broadcast. An identity substrate that leaks a plaintext VIN
  on-chain, or that ties a persistent identifier to every broadcast, creates a
  surveillance surface (RQ2).
- **Security.** The V2X threat model includes Sybil attacks, impersonation,
  message replay, credential forgery, and privacy leakage, all against an
  adversary that can inject traffic. The identity architecture must resist this
  model, and must offer a credible answer to key compromise and recovery over a
  vehicle's long life (RQ2).

No single existing standard was designed against all four constraints at once,
and — as the next section argues — no one has systematically measured how the
available standards actually trade off against one another in this setting.

---

## 1.2 Problem Statement and Gap

The building blocks for vehicular SSI exist, but they are fragmented, and the
guidance for choosing among them is missing.

**The standards were proposed in isolation.** There are many candidate
blockchain identity standards — event-log registries, non-fungible and
multi-token designs, smart-account and claim-holder contracts, and vendor
extensions — each introduced to solve its own problem, each with its own cost
and capability profile, and each typically evaluated (if at all) on its own
terms rather than against the others on a common task. A practitioner asking
"which of these should root a vehicle's identity?" finds specifications and
isolated demonstrations, not a controlled comparison.

**Industry standards say WHAT, not HOW.** MOBI VID specifies the *content* and
*lifecycle* of a vehicle identity — the birth certificate, the eleven lifecycle
event types, the attestation model — but it is deliberately implementation-
agnostic about the *substrate*. It does not prescribe which blockchain identity
standard should carry that model, nor does it quantify what each candidate
substrate would cost, expose, or resist. The gap between the industry
specification and a deployable implementation is precisely the
substrate-selection question this thesis addresses.

**No systematic, empirical comparison exists.** As surveyed in Chapter 2, prior
work tends to advocate a single standard, evaluate it in isolation, or reason
about trade-offs analytically rather than measuring them. What is missing is a
**systematic, empirical, comparative evaluation** that (i) applies the *same*
vehicle-identity operations, the *same* threat model, and the *same* W3C
compliance checklist to *every* candidate standard; (ii) reports *measured*
outcomes — real gas, real verification latency, real attack results — rather
than specification-level assertions; and (iii) does so specifically under the
automotive constraints of cost, latency, privacy, and security. Without such an
evaluation, standard selection for vehicular SSI rests on intuition and
vendor framing rather than evidence.

**This thesis addresses that gap.** It is, to the author's knowledge and as
positioned in Chapter 2, the first study to place nine blockchain identity
standards on one comparative footing for the CAV setting and to measure, rather
than assert, how they perform.

---

## 1.3 Research Questions and Hypotheses

The work is organized around four principal research questions and five
falsifiable hypotheses. Each hypothesis is stated so that the collected data
can contradict it; the methods that test each one are specified in Chapter 3,
and the outcomes are reported in Chapter 5. The nine standards under comparison
are **ERC-1056, ERC-721, ERC-725, ERC-725xy, ERC-735, ERC-1155, ERC-4337,
LSP8, and the thesis's own CVIN-Combined hybrid** (an ERC-1056 event identity
fused with ERC-735 on-chain claims); the **MOBI VID V2** application profile is
measured alongside them as a purpose-built reference rather than as one of the
nine base standards.

### Research questions

- **RQ1 — Performance.** How do the nine standards compare on gas cost (and
  the associated storage/throughput implications) when executing an identical
  set of vehicle-identity operations?
- **RQ2 — Security.** Which architecture best resists the V2X threat model
  (Sybil, impersonation, replay, credential forgery, privacy leakage), and how
  do the standards differ on key compromise and recovery?
- **RQ3 — W3C compliance.** Can blockchain-rooted identities be lifted to W3C
  DID Core v1.0 and VC Data Model v2.0 conformance through a resolution and
  issuance layer, and where do structural mismatches remain?
- **RQ4 — Real-time feasibility.** Can identity establishment plus credential
  verification fit inside the latency envelope of safety-critical V2V
  applications (~100 ms end-to-end)?

### Hypotheses

- **H1 (Performance).** Minimal-state standards (e.g. ERC-1056) are at least
  **10× cheaper** than rich-state standards (e.g. ERC-725/735) on gas for
  identity creation and update, trading away on-chain expressiveness.
- **H2 (Compliance).** At least **90%** aggregate W3C compliance is achievable
  through a resolution/translation layer, with residual gaps confined to
  specific properties requiring off-chain augmentation.
- **H3 (Real-time).** Off-chain verification of pre-issued credentials (a
  signature check with no chain round-trip at message time) **meets the V2V
  budget**, whereas any design requiring on-chain reads at message time does
  not.
- **H4 (Industry alignment).** MOBI VID's identity and lifecycle model is
  **realizable across multiple blockchain backends**, mapping most economically
  onto event-log standards and most faithfully onto claim-based standards, with
  the hybrid dominating the fidelity-per-gas frontier.
- **H5 (Security frontier).** **No single standard dominates**; the standards
  occupy a security/performance Pareto frontier, and a hybrid (ERC-1056
  identity + ERC-735 claims) sits on that frontier.

**Preview of findings (see Chapter 5).** The thesis finds **all five
hypotheses supported**. H1, H2, H3, and H5 are supported outright; H4 is
supported with a documented *fidelity gradient* — the identity and lifecycle
operations port natively to every backend measured, while native on-chain
multi-party attestation is available only on the claim-capable and
purpose-built backends. The exact measured evidence for each verdict (gas
spreads, the measured compliance percentage, the V2V verification latencies,
the security matrix, and the hybrid's frontier position) is reported in
Chapter 5 and must be read there; this chapter states only the direction of the
result.

---

## 1.4 Contributions

This thesis makes the following contributions, each grounded in a built and
tested artifact and quantified in Chapter 5:

1. **The first nine-standard empirical comparison for vehicular SSI.** All nine
   blockchain identity standards (plus the MOBI VID V2 profile) are implemented
   as smart contracts and exercised over one canonical vehicle-identity
   operation set, yielding the first controlled, apples-to-apples comparison of
   these standards as CAV identity substrates. The gas comparison is measured
   as exact `receipt.gasUsed` and reproduced across N=30 runs (Chapter 5, RQ1).

2. **A W3C-compliant SSI layer over blockchain identity.** A DID resolver (four
   methods: `did:ethr`, `did:nft`, `did:key`, `did:mobi`) and a full Verifiable
   Credentials stack (issuer, holder wallet, and a multi-stage offline
   verifier, with selective disclosure and revocation) lift on-chain identities
   to W3C conformance. An executable, CI-gated compliance checker measures
   **93.2%** aggregate compliance against DID Core v1.0 and VC Data Model v2.0
   (Chapter 5, RQ3).

3. **Evidence that blockchain identity is viable for real-time V2V.** Real
   cryptographic identity verification is placed directly in a simulated V2V
   message path and timed. The warm (per-message) SSI verification is on the
   order of a fraction of a millisecond against a ~100 ms budget — a margin of
   roughly two to three orders of magnitude — over more than a million
   verifications with every injected attack caught (Chapter 5, RQ4). The exact
   latencies and confidence intervals are reported there.

4. **A found-and-fixed security result.** The security analysis surfaced a
   concrete vulnerability — MOBI VID's `attestEvent` stored an attestation
   signature that was never verified on-chain, a replay/forgery gap gated only
   by role — and then fixed it: attestations are now recovered from a
   domain-separated signature and forged, wrong-key, and replayed attestations
   revert. The fix carries a measured gas cost, making the
   security/performance trade-off concrete (Chapter 5, RQ2).

5. **The CVIN-Combined hybrid.** The thesis proposes and implements a hybrid
   standard that fuses an ERC-1056-style event identity with ERC-735-style
   on-chain claims, and shows empirically that it pays the cheap event-log price
   for the common identity path while offering verifiable on-chain claims when
   needed — landing on the fidelity-per-gas and security/performance frontiers
   (Chapter 5, RQ1 and RQ2).

6. **A reproducible, open testbed.** The comparison rests on an open,
   re-runnable testbed: nine standards plus the MOBI VID profile, a four-method
   DID resolver, the VC stack, twelve end-to-end lifecycle use cases with real
   cryptographic verification, and a simulated V2V harness — backed by roughly
   **295 automated tests** (217 Hardhat contract tests, 28 VC, 32 MOBI VID, 6
   VIN-cipher, and 12/12 lifecycle use cases) with every reported number
   traceable to a committed artifact and a documented command (Chapters 3–5).

---

## 1.5 Scope and Honesty

The credibility of a comparative, empirical study rests on being explicit about
what was measured under real conditions versus what is representative or
simulated. This thesis treats that honesty as a first-class asset and preserves
the following caveats throughout (they are stated in full in Chapters 3 and 5):

- **Gas: local, deterministic, with a testnet validation harness.** All gas
  figures are produced on the Hardhat in-process EVM (`chainId 31337`, solc
  0.8.24, OpenZeppelin 5.0.2) and are deterministic — verified byte-identical
  across N=30 runs. Because gas is a function of the opcodes executed and is
  identical across EVM chains for identical bytecode and calldata, the
  *comparison* between standards is valid on any chain; absolute fiat cost,
  which depends on live gas price, is not claimed. A public-testnet (Sepolia)
  validation harness exists to witness the local numbers on a real network, but
  the real run requires a funded test key and an RPC endpoint and had **not yet
  been executed** at the time of writing.

- **V2V latency: real crypto, simulated mobility and network.** All signing,
  signature verification, certificate-chain validation, and credential
  verification in the V2V study are real and are timed around the actual
  cryptographic calls. However, vehicle mobility is simulated (a kinematic
  highway model; the SUMO/TraCI code path exists but was not exercised against
  the SUMO binary in the measurement environment), and the **radio, MAC, and
  network stack are excluded** — messages are delivered in-process. The V2V
  figures therefore bound the *cryptographic* verification cost, which is the
  open question this thrust addresses; they are not an end-to-end network
  latency, in which the network stack would be the dominant term.

- **Representative implementations.** The ERC-4337 EntryPoint and the LSP8
  contract are deliberately minimal, representative research implementations
  (their omissions are documented in the contract headers); their gas figures
  are a lower bound on a fully featured implementation, and the ERC-4337
  indirection overhead excludes real-world bundler/mempool cost.

- **Demo-scope items.** MOBI VID's on-chain privacy *architecture* — hash and
  encrypt the VIN on-chain, keep the plaintext off-chain — is the thesis claim;
  the specific cipher and, in particular, VIN-cipher key distribution and HSM
  custody are out of scope for the testbed. The two W3C compliance deviations
  (canonical JSON in place of URDNA2015 canonicalization, and a thesis-defined
  rather than W3C-registered cryptosuite) are executed, counted as failures,
  and thus already charged against the reported compliance percentage rather
  than argued away.

Stating these boundaries up front is what allows the measured claims in
Chapter 5 to be read as strong evidence within a scope that is honestly drawn.

---

## 1.6 Thesis Roadmap

- **Chapter 1 — Introduction (this chapter).** Motivates vehicular SSI, states
  the problem and gap, and sets out the research questions, hypotheses,
  contributions, and scope.
- **Chapter 2 — Literature Review.** Surveys V2X trust, centralized PKI versus
  SSI, W3C DID/VC and blockchain identity standards, and MOBI VID, positioning
  this comparative study within the prior work.
- **Chapter 3 — Methodology.** Specifies the comparative research design: the
  canonical operation set, and the exact, reproducible measurement procedures
  for gas, V2V latency, security, W3C compliance, and MOBI VID portability,
  each tied to its committed script.
- **Chapter 4 — Implementation.** Describes what was built — the four-layer
  architecture, the nine standards plus the MOBI VID profile, the DID resolver
  and VC stack, and the CV2X testbed — and the deliberately representative or
  simulated components.
- **Chapter 5 — Results.** Reports the measured outcomes for RQ1–RQ4 and the
  verdicts on H1–H5, with every number traceable to a committed artifact.
- **Chapter 6 — Discussion.** Interprets the results, draws out the
  substrate-selection guidance, and revisits the trade-offs and threats to
  validity.
- **Chapter 7 — Conclusion.** Summarizes the contributions and outlines future
  work, including the public-testnet validation run and real-SUMO execution.

---

*Working draft. Headline quantities referenced in this chapter are
forward-references to Chapter 5, where each is reported with its provenance and
reproduction command; nothing quantitative is derived here.*
