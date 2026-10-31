# WP 3.2–3.4 — The Gap Matrix, Benchmark v0, and the Reproduction Kit

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Date:** 2026-10-31 · **Home:** companion SP-9 + Ch 7 future work.
**Builds on:** `p1/BENCHMARK_GAP.md` (the five axes), `p3/BENCHMARK_PROFILES.md` (WP 3.1 deep profiles),
`p2/COMPARISON.md` (the 10-system comparison), `docs/MEASUREMENT_CONDITIONS.md` (the register).
**Evidence discipline:** no new measured number here; register rows are cited by number. This document *specifies* a
benchmark; it does not claim to have *run* one as a benchmark (that is the A5 milestone, §3.4).

---

## 3.2 The gap matrix against the five ingredients

A **benchmark** (as opposed to an evaluation aid, a conformance suite, or an ad-hoc measurement) is taken here to
require five ingredients, each justified from the benchmarking literature *independently of this thesis's contribution*
(answering the Phase-1 examiner's gerrymandering objection — the axes are not defined via "IDTx"):

| Axis | What it requires | Why it is a benchmark ingredient (independent of this work) |
|---|---|---|
| **A1 Shared reusable workload** | a fixed, named set of operations any implementer runs | BLOCKBENCH/DIABLO/YCSB all centre on a fixed workload; without it results are incomparable |
| **A2 Admission / conformance rule** | a pass/fail gate deciding what may be compared | TPC and SPEC define a validity/run rule; a performance number without a conformance gate is not comparable across systems |
| **A3 Metrics + measurement conditions** | defined metrics and the conditions they hold under | SPEC/TPC fix the metric and the reporting conditions |
| **A4 Public reusable harness** | runnable code others can execute | Caliper/BLOCKBENCH ship a harness; a described method is not one |
| **A5 Independent reproduction** | at least one run by someone other than the author | the defining property separating a benchmark from a one-off result (DIABLO has Lebedev23) |

**The matrix** (from `p3/BENCHMARK_PROFILES.md`; ✓ / ◐ / ✗). "Id-gate" = ships an in-transaction identity-dependent
(IDTx-class) workload — a *property*, not an axis, tracked because it is the thesis's object:

| Artefact | A1 | A2 | A3 | A4 | A5 | Id-gate |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| W3C DID Method Rubric | ✗ | ◐ | ✗ | ✗ | n/a | ✗ |
| W3C DID/VC + DIF test suites | ◐ | ✓ | ✗ | ✓ | ✓ | ✗ |
| NIST SP 800-63-4 | ✗ | ✓ | ✗ | ✗ | n/a | ✗ |
| eIDAS/EUDI FCAF + LSPs | ◐ | ✓ | ◐ | ◐ | ◐ | ✗ |
| BLOCKBENCH / DIABLO / Caliper | ✓ | ◐ | ✓ | ✓ | ✓ | ✗ (identity-blind) |
| Satybaldy 2026 (SSI perf.) | ◐ | ✗ | ✓ | ◐ | ✗ | ✗ |
| Frutuoso 2026 (ERC-3643) | ◐ | ✗ | ✓ | ◐ | ✗ | ◐ (off-chain accreditation; WP 3.1) |

**Reading.** Two families, two universal failures, one absolute absence:
1. **Conformance suites** (DID/VC/DIF, NIST, FCAF) have A2 but no A3 — they certify *format*, not *cost*.
2. **Performance artefacts** (BLOCKBENCH/DIABLO, Satybaldy, Frutuoso) have A3 but no A2 — a number with no admission
   gate. Among the *identity* performance studies, **A5 (independent reproduction) and A2 (admission rule) both fail
   universally**.
3. **The in-transaction identity-gating property is absent from every artefact without exception.** The general
   blockchain benchmarks are identity-blind; the SSI studies measure DID-document administration; and the closest
   candidate, Frutuoso 2026, enforces its identity check off-chain at the client (WP 3.1). **No artefact is both a
   complete benchmark and identity-gating.** That unoccupied cell — complete benchmark ∧ in-transaction identity
   workload — is the target this thesis names.

This is the narrow D-GAP claim (Phase 1) now *verified at source on the free artefacts*, not asserted from abstracts.

---

## 3.3 Benchmark v0 — a specification (not a run)

A first benchmark for identity substrates, assembled from parts this programme already has. **v0** means specified and
singly-run here; it is not a benchmark until A5 is met (§3.4).

### 3.3.1 Workload (A1)
Three tiers, each a fixed, named operation set:
- **W1 — lifecycle (the function set).** The Set A + Set B operations of `p1/FUNCTION_MAP.md`, run on each substrate as
  native-or-justified-`n-a` (the admission rule, §3.3.2). Already measured: register #35 (lifetime gas), #49 (state +
  log bytes), #51 (read cost vs history).
- **W2 — composition (the 17-event vehicle life).** The MOBI VID I+II lifecycle (L2), a fixed event sequence from birth
  to deactivation, so substrates are compared over a *realistic trajectory*, not single calls.
- **W3 — the IDTx classes.** The four-cell taxonomy of `ANALYSIS.md` §4.4 as a workload: for each (dependency kind ×
  locus × evaluation point) cell that a substrate can express, an operation whose admissibility depends on a *named*
  identity's state, evaluated in-transaction, with the `fulfil` re-check variant for the two-step case. **This is the
  tier no existing artefact has** (§3.2). Prototype: `phase2/idtx/contracts/IdtxExecutor.sol`.

### 3.3.2 Admission rule (A2)
A substrate is admitted iff, for every W1 operation, it either implements the operation or carries a **justified
`n-a`** (the standard has no counterpart — the Phase-2 n-a-vs-Absent rule). Admission is reported *per operation*
(native / composed / n-a), not as a single pass/fail, so the comparison ranks the admitted rather than hiding
composition. The twelve-test compliance suite (`IMinimalSSI`) is the executable form of this gate.

### 3.3.3 Metrics + conditions (A3)
The register's existing metrics and their stated measurement conditions (`docs/MEASUREMENT_CONDITIONS.md`): lifetime
and per-op gas (#35), zero→nonzero SSTORE + log bytes (#49), read RPC-calls/bytes vs history h (#31, #51), all under
the declared condition (M1-H, the stated node/transport/run-of-record). For W3 additionally: the staleness bound for
off-chain decisions (k−1 messages, register #32/#37 — flagged pre-D51, to be re-run under chain-time) and a stated
accounting of the mempool ordering-race exposure (AR-10) as a reported condition, not a measured number.

### 3.3.4 Harness (A4)
This repository: the 10-adapter conformance harness (`adapters.conformance.test.js`), the metrics collector
(`benchmarks/lib/MetricsCollector.js`), and the IDTx prototype + its mutation tests (`phase2/idtx/`). The harness is
public and runnable; the run-of-record procedure is already documented.

### 3.3.5 Scope line (what v0 is NOT)
v0 is EVM-substrate-scoped. It does **not** yet cover the non-ledger systems of `p2/COMPARISON.md` (OIDC/SAML/X.509/
mDL/V2X/FIDO2/ledgerless SSI); those enter as a cross-paradigm extension once W1 is expressed in paradigm-neutral terms
(a known limitation — the function set is an EVM-derived capability surface, Phase 2 M2).

---

## 3.4 What would make it a benchmark (the reproduction kit + A5)

v0 satisfies A1–A4 and is run once (here). **It is not a benchmark until A5** — an independent party runs it and
reports. The honest statement (Phase-1 examiner obj. 4, applied evenhandedly): *this thesis's own proposed benchmark
also lacks an independent reproduction at publication; A5 is a maturity milestone for any candidate, this one
included.* The kit that would let an external party close A5:

1. **A pinned environment** — the run-of-record's node, compiler, and transport (M1-H), as a container or lockfile.
2. **One command** — `npm run metrics:analyze` (or equivalent) emitting the register tables from a clean checkout.
3. **The admission gate as a test** — the conformance suite returning per-substrate native/composed/n-a.
4. **The W3 IDTx tier as a runnable workload** — the prototype generalized from `emit` to a measured effect (the
   current prototype demonstrates the admissibility predicate only; Phase-1 obj. 15), with the ordering-race condition
   reported.
5. **A results schema + a call for external runs** — a fixed table format so a second party's numbers are directly
   comparable, and an explicit invitation (Ch 7) for one.

**Milestone ladder:** v0 (specified + singly run, A1–A4) → v0.1 (external environment pin + one-command run) →
**v1 (A5 met: one independent reproduction)** → v1.x (cross-paradigm W1, the non-ledger systems). The thesis claims
v0; v1 is future work, and the measured IDTx study (paper P5) is where the W3 tier is run in earnest.

---

## Open items into the examiner pass (WP 3.6)
- A3's W3 metrics lean on #32/#37, flagged pre-D51 provisional (carried from Phase 1 obj. 7); the re-run is P5.
- The prototype demonstrates the predicate, not a measured effect (obj. 15) — §3.4 item 4 states this.
- v0 is EVM-scoped (§3.3.5); the cross-paradigm claim is explicitly deferred, not assumed.
