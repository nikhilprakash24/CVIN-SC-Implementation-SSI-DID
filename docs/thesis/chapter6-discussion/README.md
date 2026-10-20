# Chapter 6 — Discussion (Working Draft)

**Status**: working draft. This chapter *interprets* the measured results of
Chapter 5; it does not re-report them. Every interpretive claim traces back to
a specific finding in [`chapter5-results/`](../chapter5-results/), cited by
section (e.g. §5.2, §5.6). Where an argument would benefit from positioning
against earlier work, it is phrased *relative to prior work surveyed in
Chapter 2* rather than attached to a specific citation; the citation set is
assembled in the Literature Review, and no paper-specific claims are invented
here. Raw figures are quoted only where a single number carries the argument;
the full tables live in Chapter 5.

**Reading stance**: Chapter 5 answered *what was measured*. This chapter asks
*what it means* — for the choice of an identity substrate, for the viability of
blockchain identity in safety-critical V2V, for interoperability with the W3C
SSI stack, and for the industry (MOBI) context the thesis targets. The single
organizing finding is that **no standard dominates**: the nine standards, plus
the MOBI VID profile, occupy distinct, defensible points on a
security/performance/fidelity frontier, and the engineering question is not
"which is best" but "which point on the frontier a given deployment needs."

---

## 6.1 The Security/Performance Trade-off Frontier (H5)

The headline result of the thesis is a frontier, not a winner. Reading the gas
comparison (§5.2) and the threat matrix (§5.6) *together* rather than
separately is what makes the trade-off legible, and the two datasets line up in
a way that is more than coincidental: **the property that makes a standard cheap
is the same property that makes it Sybil-vulnerable.**

The two cheapest standards to instantiate an identity — CVIN-Combined and
ERC-1056, both ~52k gas — are minimal event-log designs with *no issuer
gating*: anyone can write an identity into the registry for the price of a
transaction. That is exactly why §5.6 marks them the *most* Sybil-vulnerable
(`✗`). The economic cost of forging a thousand identities is simply a thousand
cheap writes. Conversely, the issuer-gated designs (MOBI VID, ERC-1155, LSP8)
resist Sybil precisely because identity minting is a privileged operation — but
that gate is realized as heavier on-chain machinery, and they cost
correspondingly more per identity. Low Sybil cost and low gas are two views of
the same architectural decision (permissionless self-registration vs.
authority-gated issuance); one cannot be improved without surrendering the
other. This is the trade-off H5 predicted, now visible as a structural
coupling rather than a coincidence of two tables.

Three further findings show that the frontier is *multi-dimensional* — the
security axis is not a single scalar that gas can be traded against, but several
independent capabilities, each concentrated in a different standard:

- **Recovery is the sharpest single differentiator (§5.6).** Only ERC-4337
  offers genuine on-chain key recovery: a guardian can rotate the owner key and
  the identity address survives a key compromise. For every other standard, a
  compromised owner key is *permanent identity loss* (ERC-1155 and LSP8 offer a
  weaker issuer-mediated re-binding). For a vehicle expected to live 15–20 years
  across multiple owners, key loss is not an edge case — it is a certainty over
  the asset lifetime — which makes recovery a first-class requirement that only
  one standard in the set satisfies, and it satisfies it at the second-highest
  creation cost. Recovery, too, is bought with gas.

- **Identity-theft resistance tracks the transfer model (§5.6).** Whether an
  identity can be *stolen* is decided by whether the underlying token is
  transferable. ERC-721 and LSP8, being ordinary transferable tokens, let the
  whole vehicle identity move with the token (the VIN follows the token, shown
  on-chain). ERC-1155 is the unique `✓`: a soulbound `_update` override makes the
  birth credential non-transferable, so a holder-initiated transfer reverts. The
  same mechanism (non-transferability) that gives ERC-1155 its theft resistance
  is what makes it unsuitable wherever legitimate ownership *does* need to
  change hands — another facet of the same frontier.

- **On-chain PII leakage is the norm, not the exception (§5.6).** Read-back
  proved a *plaintext VIN on-chain* for ERC-721, ERC-735, ERC-1155, and LSP8.
  Only the MOBI VID family stores the VIN as a salted hash plus ciphertext and
  resolves via `did:ethr` rather than the VIN-embedding `did:mobi:<VIN>` method.
  Privacy, unlike the other axes, is *not* strictly a gas trade — it is a design
  discipline (hash-on-chain, plaintext off-chain) that most standards simply do
  not exercise by default. This is the one place the frontier can be moved
  rather than traded along, and it is a contribution the thesis makes
  concretely.

The security analysis also produced a *method* finding worth carrying into the
discussion: the `attestEvent` signature-verification gap that the threat-matrix
lens surfaced and the thesis then fixed (attestations now `ecrecover` against a
domain-separated digest; forged and replayed signatures revert; §5.6). The cost
of the fix — attestEvent rising from 121,110 to 192,718 gas — is the
security/performance trade-off made concrete *within a single operation*: the
extra ~72k gas buys on-chain signature verification that the original code
omitted. That a source-reading lens caught what a passing revert-suite could
not is itself an argument for the two-lens security methodology of Chapter 3.

**Interpretation.** The frontier is real and it is multi-dimensional. No
standard is simultaneously cheapest, Sybil-resistant, recoverable,
theft-proof, and privacy-preserving; each strong property is concentrated in a
different standard and paid for in gas or in a lost capability elsewhere.
Relative to prior work surveyed in Chapter 2 — which tends to evaluate identity
standards one axis at a time (cost *or* security *or* compliance) — the
contribution here is the *joint* frontier: the same nine standards measured on
every axis under one operation set and one threat model, so the trade-offs
between axes are visible rather than assumed.

---

## 6.2 Which Standard When — A Data-Grounded Decision Guide

Because no standard dominates, the practical output of the comparison is a
*selection guide*: given a deployment's dominant requirement, the data points
to a specific standard (or small set). The guide below is grounded entirely in
Chapter 5 findings — the gas comparison (§5.2), the security matrix (§5.6), and
the H4 backend-sweep fidelity gradient (§5.3.1).

| If the dominant requirement is… | Choose | Because (Chapter 5 evidence) |
|---|---|---|
| **Cost-sensitive, high-volume identity** (fleets, mass registration) | ERC-1056 or CVIN-Combined | Cheapest creation (~52k gas), ~10× under NFT/proxy designs (§5.2). Accept the Sybil exposure or gate issuance off-chain. |
| **Verifiable on-chain claims / attestation** (inspections, recalls, warranty) | ERC-735 or CVIN-Combined | The claim-capable backends; the only ones reaching 5/5 fidelity with native multi-party attestation (§5.3.1, §5.6). |
| **Key recovery is paramount** (long-lived assets, owner-key loss expected) | ERC-4337 | The only standard with genuine on-chain guardian recovery (§5.6). |
| **Identity-theft resistance** (birth credential must not be transferable) | ERC-1155 | Uniquely soulbound; transfer of the birth credential reverts (§5.6). |
| **On-chain VIN privacy** | MOBI VID family | The only family that hashes + encrypts the VIN rather than storing plaintext (§5.6). |
| **Maximal-fidelity, purpose-built reference** (regulatory/industry pilot) | MOBI VID V2 | Richest structured on-chain data; the semantic-fidelity reference the others are measured against (§5.3.1). |

Two points make this guide more than a lookup table.

**First, the fidelity gradient (H4) explains the "claims" row.** The
backend sweep (§5.3.1) established that MOBI VID's three canonical operations
port across backends but *fidelity is not uniform*: birth and lifecycle
attestation are native on all five backends, but genuine multi-party
attestation is native only on the three claim-capable/purpose-built backends
(ERC-735, CVIN-Combined, MOBI-VID-V2, each 5/5) and degrades to off-chain VCs
or an unlinked approximation on the pure event-log/token backends (ERC-1056,
ERC-1155, each 3/5). So the choice between "cost-sensitive" and "attestation"
rows is not a free knob — it is the *same* event-log-vs-claim architectural
split that drives the gas frontier in §6.1. A deployment that needs on-chain,
independently-signed third-party attestations cannot have the ~52k identity
price; it must move up to a claim-capable design.

**Second, the guide composes.** Because the requirements are largely
independent axes (§6.1), most real deployments will name a *primary* axis and
tolerate the rest. The value of CVIN-Combined (§6.5) is that it collapses two of
the most common rows — cheap high-volume identity *and* verifiable on-chain
claims — into one standard, which is why it appears in two rows above. A
deployment whose primary axis is *recovery* or *theft resistance*, however,
cannot be served by the hybrid and must select ERC-4337 or ERC-1155
respectively; those capabilities are not in the hybrid's composition.

Relative to prior work surveyed in Chapter 2, the contribution of this section
is a decision procedure keyed to *measured* properties of a common
implementation, rather than to specification-reading or vendor claims.

---

## 6.3 Real-Time V2V Viability (H3)

The V2V latency result (§5.4) answers the question that most directly gates
deployment: *can a blockchain-rooted identity be verified fast enough for
safety-critical V2V messaging?* The measured warm-verify median of 0.165 ms and
cold (full-credential) median of 0.400 ms, against the ~100 ms end-to-end V2V
safety budget, give a margin of roughly two-and-a-half to three orders of
magnitude. The interpretation matters more than the numbers.

**What the result means.** The viable architecture is *pre-issued credential +
off-chain verification*: the vehicle carries a credential minted at
registration time, and peers verify it at message time with a local signature
check against a cached peer key — no chain round-trip in the hot path. Under
that architecture, the cryptographic cost of blockchain identity is negligible
at the V2V timescale. This reframes where the cost of blockchain identity
actually lives: **it is at issuance/registration (the RQ1 gas of §5.2), not at
verification.** The expensive, once-per-lifetime act is writing the identity
on-chain; the frequent, safety-critical act is verifying it, and that is cheap.
A design that instead required an on-chain *read* at message time — as some
naive "check the registry" schemes would — would not clear the budget, which is
precisely the boundary H3 was stated to test (§3.1.2). The result therefore
does more than pass a threshold; it discriminates between a viable and a
non-viable integration pattern.

**The SSI-vs-PKI comparison, correctly sized.** SSI warm verification costs
about 1.6× the IEEE 1609.2 PKI baseline per message (0.165 ms vs 0.102 ms), and
the N=30 confidence intervals are non-overlapping, so the difference is real
rather than noise (§5.4). But at the safety timescale both are immaterial: a
1.6× multiplier on a sub-millisecond operation is not a barrier when the budget
is 100 ms. The honest reading is that blockchain-rooted identity introduces *no
latency obstacle* to V2V safety messaging, while offering the richer trust and
revocation semantics of the SSI stack that the PKI baseline lacks. The integrity
result reinforces this: across 1.65M verifications the only failures were
exactly the 90 injected attacks (3 per run × 30 runs), caught with zero false
positives and zero false negatives — the verification path is both fast and
correct.

**The honest boundary.** The measured quantity is *cryptographic verification
cost*, not full end-to-end latency. The numbers deliberately exclude the
radio/MAC/congestion/network-stack contribution, and mobility is simulated
(no SUMO binary in the measurement environment; §5.4, §5.8). This boundary is
stated plainly because it is where the remaining risk lives: in a real
deployment the network stack, not the cryptography, is the dominant latency
term. What the thesis establishes is the *previously open* question — that the
identity-verification component is not the bottleneck and has ample headroom —
not the end-to-end budget, which is out of scope and would require radio-layer
measurement. Framed this way, H3 is *supported for the component it measures*,
and the caveat is a scoping statement, not a weakness concealed.

---

## 6.4 W3C Compliance and Interoperability (H2)

The 93.2% aggregate compliance figure (§5.5) is best read not as a grade but as
a *structural* claim about interoperability: blockchain-rooted identities can be
lifted into W3C DID Core v1.0 and VC Data Model v2.0 conformance through a
resolution/issuance layer, and the residual gap is confined to two specific,
documented places rather than diffused across the model.

**What 93.2% means.** The score decomposes into DID Core 93.3% (13/15 checks)
and VC Data Model 93.1% (27/29 checks). Critically, the ~7% shortfall is *not*
a scatter of partial failures across the data model — it is exactly **two
deviations**, both deliberate and both documented as failures rather than
hidden: (1) proof canonicalization uses deterministic sorted-key JSON rather
than URDNA2015 RDF canonicalization, and (2) the cryptosuite
(`eip191-secp256k1-recovery-2024`) is thesis-defined — Ethereum-native and
offline-verifiable — rather than a W3C-registered suite. Everything else in the
executable checklist passes. The interpretation is that there is **no structural
incompatibility** between blockchain identity and the W3C SSI data model; the
gap is entirely in *canonicalization and cryptosuite registration*, both of
which are additive, non-breaking changes.

**What it means for real-world interoperability.** The two deviations are of a
specific, benign kind. Adopting URDNA2015 and registering (or swapping to) a
standard cryptosuite are *implementation* changes that do not touch the identity
architecture, the credential schemas, or the resolution logic — they are the
last-mile of conformance, not a redesign. This matters for a CAV deployment
because it means an SSI vehicle credential produced by this stack is already
shaped for interoperation with the broader W3C ecosystem, and the path to full
conformance is a bounded, well-understood engineering task rather than an open
research problem. The honest counterpoint, which the thesis states, is that
until those two changes are made the credentials are *not* byte-for-byte
interoperable with verifiers that demand URDNA2015 or a registered suite; 93.2%
is a real, measured 93.2%, not a rounded-up 100%. Relative to prior work
surveyed in Chapter 2, the contribution is that compliance here is *executable
and measured* (a checker that runs against the real VC layer and DID resolver),
not asserted from a specification-conformance narrative.

---

## 6.5 The CVIN-Combined Contribution — Pareto-Optimality on Fidelity-per-Gas

The thesis's own design, CVIN-Combined (an ERC-1056-style event identity fused
with ERC-735-style on-chain claims), is the synthesis that the frontier
argument points toward, and both gas datasets (§5.2, §5.3, §5.3.1) show *why*
it is Pareto-optimal rather than merely cheap.

**The mechanism: pay the cheap price on the common path, the claim price only
on demand.** The hybrid's identity-lifecycle operations are statistically
indistinguishable from the cheapest standard in the study — create 52,178
(vs ERC-1056's 52,612), update and transfer likewise at ERC-1056 cost (§5.3) —
because for those operations it *is* an event-log identity. It only pays the
expensive on-chain-claim price (~290k gas for `addClaim`) when a verifiable
on-chain claim is actually required. The common path (which dominates the
operation mix over a vehicle's life) runs at the floor cost, and the expensive
path is invoked only for the safety-critical subset of claims that genuinely
need on-chain verifiability. This is not an averaging trick — it is a design
that lets the *caller* choose which price to pay per operation.

**The Pareto argument, from the backend sweep.** §5.3.1 makes the optimality
precise rather than rhetorical. Among the backends that reach full 5/5 fidelity
(native birth, lifecycle, multi-party attestation, verifiable claims,
revocation), CVIN-Combined achieves that fidelity at the **lowest total cost of
any 5/5 backend**: its three canonical operations sum to 421,263 gas, against
798,621 for MOBI-VID-V2 and 870,577 for ERC-735. No backend offers *both* higher
fidelity *and* lower gas — which is the definition of Pareto-optimality on the
fidelity-per-gas plane. The hybrid dominates ERC-735 outright (equal fidelity,
roughly half the gas) and dominates the purpose-built registry on cost while
matching its fidelity score.

**The honest qualifier.** Pareto-optimality on the *fidelity-per-gas* plane is
not global superiority. The hybrid is `✗` on Sybil cost (it inherits the
permissionless self-registration that makes it cheap, §6.1) and has no recovery
and no soulbound theft resistance — so on the *security* axes it does not
dominate ERC-4337 or ERC-1155. Its optimality is scoped to the two axes it was
designed to reconcile — capability fidelity and gas — and on those it is the
best point measured. That scoping is exactly consistent with H5: the hybrid does
not break the frontier, it *sits on it* at a uniquely favourable point for the
cost-plus-claims requirement class identified in §6.2.

MOBI-VID-V2 remains the *reference*, and this is not a contradiction: its equal
5/5 score understates its semantic richness (11 typed event types, per-event
odometer/jurisdiction/VC-hash/verified-flag, salted-hash VIN privacy). The extra
birth/lifecycle gas is precisely what buys that on-chain structure; the hybrid
achieves the same *concept-level* fidelity by pushing the richest structure to
where it is cheaper. The two are complementary: the registry is the
maximal-fidelity purpose-built target, the hybrid is the most economical general
substrate that still reaches full concept fidelity.

---

## 6.6 Practical and Industry Implications, and Threats to Validity

### 6.6.1 Industry alignment (MOBI)

The MOBI VID backend sweep (§5.3.1) is the thesis's bridge to industry practice,
and its practical message is portability with a documented fidelity gradient.
MOBI VID's application semantics — birth certificate (VID I) and lifecycle
events (VID II) — are **not locked to a single purpose-built contract**; they
are realizable across the standard identity substrates, natively on the three
claim-capable/purpose-built backends and partially (attestation off-chain) on
the two event-log/token backends. For the MOBI ecosystem this means the VID data
model can be deployed on whichever substrate a given OEM or jurisdiction has
already standardized on, with the fidelity/cost consequence known in advance
from §5.3.1 rather than discovered in production. The purpose-built MOBI-VID-V2
registry remains the maximal-fidelity target, and the hybrid the most economical
full-fidelity general substrate — giving an integrator a measured spectrum
rather than a single mandated implementation. A concrete industry-relevant
by-product is the `attestEvent` hardening (§5.6): a real signature-verification
gap in an attestation primitive, found by source review and fixed, is exactly
the class of issue an industry pilot needs surfaced before deployment.

### 6.6.2 Practical implications

- **Issuance is the cost center, verification is nearly free (§6.3).** Budget
  the on-chain gas of §5.2 as a one-time registration cost; the recurring
  safety-path verification is sub-millisecond. Deployment economics should be
  reasoned about at issuance, not per message.
- **Choose the substrate from the requirement, not the hype (§6.2).** The
  decision guide keys the choice to a measured dominant requirement; there is no
  universally correct standard.
- **Privacy is a discipline, not a default (§6.1).** Plaintext-VIN leakage is the
  norm across standards; a hash-on-chain/plaintext-off-chain architecture (the
  MOBI VID pattern) must be adopted deliberately.
- **Conformance is a bounded last-mile (§6.4).** Full W3C interoperability is two
  documented, non-structural changes away (canonicalization + cryptosuite
  registration).

### 6.6.3 Threats to validity (recap)

The interpretations above inherit the threats to validity stated in §5.8 and
§3.8; they are recapped here because they bound the reach of the discussion, not
merely the results.

- **Local vs. public chain.** Gas is deterministic across EVM chains, so the
  *comparison* (the frontier of §6.1, the Pareto claim of §6.5) is valid; the
  absolute fiat cost is not claimed, and a Sepolia validation run is planned but
  not yet executed. The frontier's *shape* is robust; its dollar calibration is
  future work.
- **Network stack excluded from V2V latency (§6.3).** The V2V viability claim is
  scoped to cryptographic verification cost. The end-to-end budget, dominated by
  the radio/MAC/network stack, is out of scope and is the dominant remaining
  term in a real deployment.
- **Simulated mobility.** The SUMO/TraCI path exists but was exercised in
  `--simulate` mode, not against the SUMO binary; the mobility model is a
  simplification of real traffic dynamics.
- **Representative contracts.** LSP8 and the ERC-4337 EntryPoint are deliberately
  minimal research implementations; their gas is a *lower bound*, so their
  position on the frontier (§6.1) could only move upward (costlier) with a
  fully-featured implementation — which does not weaken, and slightly
  strengthens, the "cheap standards are Sybil-vulnerable" reading.
- **Demo-grade VIN encryption.** The privacy *architecture* (hash-on-chain,
  plaintext off-chain) is the thesis claim; the specific cipher and key
  custody/HSM story are out of scope for the testbed.

None of these threats undercut the central interpretive claim — that the
standards occupy a real, multi-dimensional frontier and that selection is a
requirement-driven choice along it. They bound the *quantitative reach* (absolute
cost, end-to-end latency), not the *comparative structure*, which is what the
discussion rests on.

---

## 6.7 Summary

The discussion converts Chapter 5's measurements into a single defensible
thesis: **there is no dominant blockchain identity standard for CAV SSI; there
is a frontier, and engineering is the act of choosing a point on it.** The
frontier is multi-dimensional (§6.1) — cheap standards are Sybil-vulnerable,
recovery is isolated to ERC-4337, soulbound theft resistance to ERC-1155,
on-chain VIN privacy to the MOBI VID family — so selection must be
requirement-driven (§6.2). Blockchain identity is viable for real-time V2V under
a pre-issue/off-chain-verify architecture, with the cost living at issuance and
not verification (§6.3); it interoperates with the W3C stack up to two
documented, non-structural deviations (§6.4). The thesis's CVIN-Combined hybrid
is Pareto-optimal on the fidelity-per-gas plane — full concept fidelity at the
lowest gas of any full-fidelity backend — without claiming to dominate the
security axes it was not designed for (§6.5). For industry (MOBI), the VID data
model is portable across substrates along a measured fidelity gradient, with the
purpose-built registry as the maximal-fidelity reference (§6.6). All five
hypotheses (H1–H5) are supported by these interpretations, subject to the
scoping threats to validity recapped above.

---

*Working draft. Every interpretive claim is traceable to a numbered finding in
[`chapter5-results/`](../chapter5-results/); positioning against earlier
literature is deferred to Chapter 2 and phrased "relative to prior work
surveyed in Chapter 2" rather than attached to fabricated citations. Numbers are
quoted only where load-bearing; regenerate them via the Chapter 5 commands.*
