# Research Audit — Interim Internal Report

*Status: **interim internal report**, not a finished assessment — a research-grade
self-critique captured at v0.9.0-dev to inform decisions, revised as the work matures.
It is written to be interrogated, not admired.*

**Scope of what this gates.** This report gates **new research, experiments, and
outward claims** (the §6 program) — those wait on the researcher's §7 framing
decisions. It does **not** gate **consolidation**: capturing the existing knowledge
base into stable, complete artifacts is proceeding now, because the goal is to have
ALL current information stabilized and full *before* deciding what to add.*

**Subject:** MASc thesis (UBC ECE) — comparative analysis of blockchain identity
standards as SSI substrates for connected/autonomous vehicles.
**State:** v0.9.0-dev; implementation over-complete; 6/7 chapters drafted; all five
hypotheses measured-supported *subject to the validity caveats in §4*.

---

## 1. What this project is (the research, not the repo)

A single-testbed empirical comparison of nine blockchain identity substrates
(ERC-721/725/725xy/735/1056/1155/4337, LSP8, and a hybrid) evaluated as vehicle
identities against four automotive constraints — cost, real-time verifiability,
security, and W3C interoperability — with the MOBI VID profile as the industry target.
The intended **contribution is knowledge, not an artifact**: a measured account of how
the substrate choice trades cost against capability and security, and where a hybrid
sits on that trade-off.

## 2. What we have produced (honest inventory)

| Category | State | Note |
|---|---|---|
| Implementation (9 standards + W3C VC/DID + MOBI VID + CV2X testbed) | **Over-complete** | ~295 automated tests; more than a thesis strictly needs |
| Measured results (gas, V2V latency, security, compliance, MOBI backends) | **Complete, committed** | `SOURCES.md §6` |
| Provenance spine (attribution, sources, genealogy, composition) | **Complete** | corrected the record; researcher owns the ideas |
| Thesis chapters | **6/7 drafted, grounded** | Ch.2 lit-review pending citations; drafts are *not yet examiner-grade prose* |
| Public-testnet validation | **Harness only** | Sepolia run not executed (dry-run on local chain only) |

**Blunt read:** the *building* is done and then some. The unfinished work is almost
entirely **research writing and research-grade validation** — which is exactly the
discipline an ECE MASc is examined on, and the thing least addressed so far.

## 3. The knowledge claims (what an examiner should take away)

Stated as claims about the world, each with its evidence and — critically — the
boundary beyond which it does not hold:

- **K1 — Substrate cost spans ~33× and is dominated by on-chain state footprint.**
  Identity creation: 52,178 gas (event-log hybrid) → 1,704,992 (full ERC-725 account).
  *Knowledge:* the cost driver is how much state the design writes, not the standard's
  "features" per se.
- **K2 — Cost and Sybil-resistance are the same architectural decision.** The cheapest
  substrates are permissionless self-registration (Sybil-exposed); Sybil-resistant ones
  are issuer-gated (costlier). This coupling — not any single "winner" — is the central
  systems result.
- **K3 — Verification cost is not the V2V bottleneck.** Cryptographic verification of a
  pre-issued credential is sub-millisecond; therefore the blockchain-identity question
  for V2V is an *issuance/architecture* question, not a *verification-latency* one.
- **K4 — Open-standard conformance is reachable to a bounded last mile** (measured
  93.2%, residual = two deliberate deviations).
- **K5 — A cost/capability hybrid exists** (CVIN-Combined) that takes the cheap path for
  the common case and pays for verifiable claims only on demand.

## 4. Critical research self-assessment (the part that matters)

*These are the threats an ECE examiner will raise. Stating them first is the discipline;
several genuinely narrow our headline claims.*

### 4.1 Construct validity — is gas the right cost metric?
Gas measures *computational work on the EVM*, not deployment cost. Gas→fiat spans
orders of magnitude across L1/L2 and fee-market conditions. Our comparison is a valid
measure of **relative on-chain work**, but the thesis currently implies economic cost
without a fee-market model. **Fix:** either (a) reframe explicitly as relative
computational cost, or (b) add a fee-scenario cost model (L1 vs an L2 vs a consortium
chain) turning gas into a defensible cost range. Recommend (a) as the core claim, (b)
as a scenario appendix.

### 4.2 Internal validity — are we comparing standards or our implementations?
Gas depends on *how we wrote each contract*, and two standards (ERC-4337 EntryPoint,
LSP8) are explicitly **minimal/representative**. Implementation quality is a confound:
a hand-optimized ERC-721 could move materially. **Fix:** (a) state the confound plainly
(done in-header, must be elevated to a named threat in Ch.3/§5.8); (b) where feasible,
benchmark against a canonical reference implementation (e.g. the official
ERC-4337 EntryPoint) and report the delta; (c) add per-operation *opcode/SSTORE
accounting* so the gas is explained by structure, not just reported — this converts a
"my number" into a mechanistic result.

### 4.3 The gas "N=30, σ=0" framing is not statistical rigor. — ✓ ADDRESSED
*(§5.2/§5.9 now present gas determinism as reproducibility verification, not CIs; slopes reported as exact.)*
EVM gas is deterministic for fixed calldata + pre-state; running it 30× confirms the
EVM is deterministic, nothing more. Presenting it as "confidence intervals" is a
category error. **Fix:** relabel as **reproducibility/determinism verification** (which
is genuinely valuable), and reserve statistical language for the latency study.

### 4.4 The V2V "~600× margin" is a scope mismatch. — ✓ PARTLY ADDRESSED
*(§5.4/§5.7 claim narrowed to "verification is not the bottleneck" with explicit scope; the analytic end-to-end budget figure — §15 — still pending a citation set.)*
We compare a *sub-component* (crypto verification, 0.165 ms) against the *whole-system*
100 ms V2V budget. The dominant budget terms — radio access/MAC contention, propagation,
queuing, application processing — are **excluded** (no network stack; mock mobility;
single host). The defensible claim is narrow: *credential verification is not the
bottleneck*. **Fix:** (a) restate the claim at that scope; (b) add an **analytic budget
decomposition** placing verification within a literature-sourced end-to-end V2V budget
(IEEE 1609.2 / SAE J2735 timing) — this is a paper-worthy figure and needs no new code;
(c) optionally a real-SUMO/ns-3 run, but (b) already discharges the examiner's objection.

### 4.5 The latency CI is repeatability, not population inference.
Thirty same-host seeded runs estimate *measurement-noise* dispersion (scheduler, GC),
not a sampling distribution over a population. The bootstrap CI is legitimate **as a
repeatability interval** and must be labeled so. **Fix:** relabel; report host/OS; if a
population claim is wanted, vary the platform (different CPUs) — otherwise keep the
narrower, correct interpretation.

### 4.6 The W3C compliance checker grades our own homework.
93.2% is measured against *our reading of the spec* in a *self-authored* checker.
**Fix:** run against the **official W3C VC/DID test vectors / conformance suite** where
they exist, and report our checker's agreement with them; without that, present 93.2%
as a self-assessment, explicitly.

### 4.7 The threat model is informal. — ✓ ADDRESSED
*(`docs/THREAT_MODEL.md`: formal adversary model A1–A4, trust assumptions T1–T4, goals G1–G8, mapped to the 54 scenarios + matrix dimensions.)*
The security work is strong operationally (54 executable attacks, found-and-fixed
attestation gap) but there is no *formalized* adversary model (capabilities, trust
assumptions, what is out of scope). **Fix:** a half-page formal threat model in Ch.3;
map each of the 54 scenarios and the six matrix dimensions to it.

### 4.8 Missing experimental design elements an ECE thesis expects. — ✓ ADDRESSED
*(§5.9 adds marginal-cost stationarity, a lifetime-cost model, verification-richness and traffic-density scaling with a saturation point; §5.9.4 adds optimizer + calldata sensitivity (SN-1/2 — ranking robust across optimizer settings; 12 gas/byte calldata rule); PKI baseline foregrounded.)*
- **No scaling studies.** Gas vs #delegates/#claims; verify-latency vs credential size
  and vs #peers. Scaling curves are standard ECE evidence and are cheap to produce here.
- **No sensitivity analysis** (e.g. optimizer runs, calldata size effects).
- **Baseline under-used:** the centralized/PKI baseline exists but isn't foregrounded as
  the control condition it is.

### 4.9 "Pareto-optimal" is used loosely. — ✓ ADDRESSED
*(§5.9.2 now gives the formal dominance relation and proves CVIN-Combined non-dominated on (cost, fidelity) at creation and lifetime scope, spanning the frontier as claim fraction f varies; security axis reported separately as no-total-order.)*
Claiming CVIN-Combined is Pareto-optimal requires the axes, the dominance relation, and
a demonstration that no compared point dominates it. **Fix:** define the objective space
(gas × fidelity, and separately gas × security-score), plot the frontier, and show the
hybrid is non-dominated — or soften to "on the favourable region of the trade-off."

## 5. What we can defensibly claim *today* vs. after §4 fixes

| Hypothesis | Claim today (honest) | What §4 fix upgrades it to |
|---|---|---|
| H1 | ERC-1056-class is ~10× cheaper in on-chain work (internally valid) | + mechanistic (opcode accounting) + reference-impl delta |
| H2 | 93.2% self-assessed compliance | + external conformance-vector agreement |
| H3 | Credential *verification* is not the V2V bottleneck (sub-ms) | + analytic end-to-end budget placement |
| H4 | MOBI VID ports across 5 backends with a fidelity gradient | solid; add opcode/structure explanation |
| H5 | A hybrid occupies the favourable trade-off region | + formal frontier/dominance proof |

**The honest headline:** the *comparative* results are internally strong; the
*generalization* claims (economic cost, whole-system V2V latency, external compliance)
are where an examiner pushes, and §4 says exactly how to close each — mostly with
analysis and reframing, not new building.

## 6. Next steps — as a research program (not a task list)

Sequenced by defense-readiness per unit effort; most are analysis/writing, not code:

1. **Reframe & relabel (writing, high leverage):** determinism vs CIs (§4.3), latency
   scope (§4.4/4.5), gas as relative computational cost (§4.1). Touches Ch.3/§5 prose.
2. **Analytic V2V budget decomposition (§4.4):** one figure + text situating 0.165 ms in
   a literature-sourced end-to-end budget. No new code.
3. **Formal threat model (§4.7):** half-page in Ch.3; wire to the 54 scenarios.
4. **Scaling & sensitivity experiments (§4.8):** gas vs #claims/#delegates; verify vs
   credential size / #peers. New code + new figures — the strongest *new* evidence.
5. **Mechanistic gas explanation (§4.2):** opcode/SSTORE accounting per operation;
   reference-impl deltas for the representative contracts.
6. **External W3C conformance (§4.6):** run official vectors; report agreement.
7. **Formal frontier/dominance for H5 (§4.9).**
8. **Real Sepolia witness** (needs RPC + funded key) → cut v0.9.0.
9. **Chapter 2 literature review** (needs the researcher's citation set) + take one
   chapter to examiner-grade prose as the writing exemplar.

## 7. What needs the researcher (audit decisions)
- **Framing calls:** accept the narrower, defensible claims in §5 (recommended), or
  invest in the experiments that broaden them (§6.4–4.6)? This is a scope decision only
  you can make.
- **Citation set** for Ch.2 and for the §4.4 V2V budget / §4.6 conformance references.
- **Sepolia creds** and **GitHub access** (push pending; everything committed + bundled).
- **Which hypotheses are load-bearing for the defense** — so we spend effort where the
  committee will actually probe.

---

*Prepared for researcher audit. Nothing here is added to the thesis until you've
reviewed the framing decisions in §7. The point of this document is to make the
research risks explicit before we expand — consistent with "have ALL possible
information before we add more."*
