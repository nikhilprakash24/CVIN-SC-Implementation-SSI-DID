# WP 3.2–3.4 — The Gap Matrix, Benchmark v0, and the Reproduction Kit

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Date:** 2026-10-31 · **Home:** companion SP-9 + Ch 7 future work.
**Builds on:** `p1/BENCHMARK_GAP.md` (the five axes), `p3/BENCHMARK_PROFILES.md` (WP 3.1 deep profiles),
`p2/COMPARISON.md` (the 10-system comparison), `docs/MEASUREMENT_CONDITIONS.md` (the register).
**Evidence discipline:** no new measured number here; register rows are cited by number. This document *specifies* a
benchmark; it does not claim to have *run* one as a benchmark (that is the A5 milestone, §3.4).

---

## 3.2 The contribution: a new workload class (not an empty benchmark cell)

**What this contribution is (M2, M4 reframe).** The contribution is a **new workload class** — the IDTx taxonomy
(dependency-kind × locus/encoding × evaluation-point, `ANALYSIS.md` §4.4) rendered as a measurable performance workload
— **plus** the thesis's measured substrate breadth (the same function set + IDTx tier across ten EVM substrates). It is
**NOT** the discovery of an empty benchmark cell, and it is **NOT** carried by the "Id-gate" property alone. The
"unoccupied cell / complete benchmark ∧ identity-gating" framing of earlier drafts is **demoted to motivation** below;
it is not the claim. (This directly answers the examiner's M2 — the gap must not rest on the thesis's own non-axis — and
M4 — A5 must not be a bespoke discriminator.)

A **benchmark** (as opposed to an evaluation aid, a conformance suite, or an ad-hoc measurement) is taken here to
require the five ingredients below, each justified from the benchmarking literature *independently of this thesis's
contribution*. **To avoid a bespoke rubric (M4),** these are cross-checked against the classical Gray/TPC criteria —
**relevance, portability, scalability, simplicity** (Gray, *The Benchmark Handbook*): A1 ≈ relevance, A3/A4 ≈
portability + scalability, and simplicity is a cross-cutting goal; **A5 (independent reproduction) is not a Gray/TPC
defining criterion** and is therefore **demoted here from a defining axis to a *maturity* property, applied symmetrically
— v0 lacks it too** (§3.4). A2 is retained because SPEC/TPC do define a validity/run rule, but it is a maturity gate
for performance comparability, not identity-specific.

| Axis | What it requires | Status in the benchmarking literature |
|---|---|---|
| **A1 Shared reusable workload** | a fixed, named set of operations any implementer runs | **defining** (Gray: relevance); BLOCKBENCH/DIABLO/YCSB centre on a fixed workload |
| **A2 Admission / conformance rule** | a pass/fail gate deciding what may be compared | **defining** for comparability (TPC/SPEC validity rule) |
| **A3 Metrics + measurement conditions** | defined metrics and the conditions they hold under | **defining** (Gray: portability/scalability); SPEC/TPC fix metric + reporting conditions |
| **A4 Public reusable harness** | runnable code others can execute | **defining**; Caliper/BLOCKBENCH ship a harness |
| **A5 Independent reproduction** | at least one run by someone other than the author | **maturity property, not a Gray/TPC criterion** — applied symmetrically to v0 (§3.4), not used to fail others |

**The matrix** (reconciled cell-by-cell with `p3/BENCHMARK_PROFILES.md`; ✓ / ◐ / ✗; families kept **disaggregated**
per M5). "Id-gate" = ships an in-transaction identity-dependent (IDTx-class) workload — the thesis's object property,
tracked, **not** a gap-defining axis. Note Id-gate ≡ the "IDTx" column of `BENCHMARK_PROFILES.md` (same property):

| Artefact | A1 | A2 | A3 | A4 | A5 | Id-gate |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| W3C DID Method Rubric | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| W3C DID Core test suite | ◐ | ✓ | ✗ | ✓ | ✓ | ✗ |
| W3C VC 2.0 test suite | ◐ | ✓ | ✗ | ✓ | ◐ | ✗ |
| DIF interop suites | ◐ | ✓ | ✗ | ✓ | ◐ | ✗ |
| NIST SP 800-63-4 | ✗ | ◐ | ✗ | ✗ | ✗ | ✗ |
| eIDAS/EUDI FCAF + LSPs | ◐ | ✓ | ✗ | ◐ | ✗ *(provisional, m10)* | ✗ |
| BLOCKBENCH | ✓ | ◐ | ✓ | ✓ | ✓ | ✗ (ships no identity workload) |
| DIABLO | ✓ | ◐ | ✓ | ✓ | ✓ | ✗ (ships no identity workload) |
| Caliper | ✗ | ✗ | ◐ | ✓ | ✓ | ✗ (**ships** none; **can host** one — M3) |
| Satybaldy 2026 (SSI perf.) | ◐ | ✗ | ✓ | ◐ | ✗ | ✗ |
| Frutuoso 2026 (ERC-3643) | ◐ | ✗ | ✓ | ◐ | ✗ | ◐ (off-chain accreditation; WP 3.1) |
| **ERC-3643 / T-REX** (EIP-3643) | ✗ | ✗ | ✗ | ✓ | ✓ | **✓ (on-chain, shipped)** |
| **ERC-1404 / CMTAT** (Taurus Sepolia) | ✗ | ✗ | ◐ | ✓ | ✓ | **✓ (on-chain, shipped)** |

**Changelog vs `BENCHMARK_PROFILES.md` (M5 — only legitimate changes, each with a reason):**
- **DID/VC/DIF disaggregated** into three rows (was one collapsed "DID/VC + DIF" row): DID Core A5 ✓ (46 impls), VC 2.0 and DIF A5 ◐ (ongoing, less consolidated) — the collapse had hidden VC/DIF ◐ behind DID Core ✓.
- **BLOCKBENCH / DIABLO / Caliper disaggregated** into three rows: Caliper A1 ✗ (bring-your-own-workload) was hidden by the ✓ of BLOCKBENCH/DIABLO; Caliper A2 ✗, A3 ◐ surfaced.
- **DID Method Rubric A5: n/a → ✗** and **NIST A5: n/a → ✗** — aligned to PROFILES (nothing is run, so reproduction is absent, not "not applicable").
- **NIST A2: ✓ → ◐** — aligned to PROFILES Artefact 3 (assurance-level *criteria* satisfied by documented assessment, not a pass/fail on a run).
- **eIDAS/EUDI A3: ◐ → ✗** and **A5 marked provisional (m10)** — aligned to PROFILES Artefact 4 (functional conformance only; A5 rests on Sokolov26 abstract-only).
- **Rubric A2: ◐ → ✗** — aligned to PROFILES Artefact 1 (it explicitly declines a verdict).
- **Two new rows (F1):** ERC-3643/T-REX and ERC-1404/CMTAT (new Artefacts 8–9 in PROFILES).

### Reading (motivation, not the claim)

Two families, two maturity failures — and the mechanism is present, not absent:
1. **Conformance suites** (DID/VC/DIF, NIST, FCAF) have A2 but no A3 — they certify *format*, not *cost*.
2. **Performance artefacts** (BLOCKBENCH/DIABLO, Satybaldy, Frutuoso) have A3 but no A2. Among the *identity*
   performance studies, A5 and A2 both fail — but A5 is a maturity property (above), so this motivates, it does not
   define, the gap.
3. **RETRACTED (F1).** An earlier reading-point 3 claimed *"the in-transaction identity-gating property is absent from
   every artefact without exception."* **That is false and is withdrawn.** ERC-3643 / T-REX runs
   `isVerified(_to)` + `canTransfer(from,to,amount)` **on-chain, in-transaction, before value moves** (EIP-3643 spec,
   read at source, WP 3.1 Artefact 8); ERC-1404 / CMTAT gates transfers on counterparty allowlist/identity state
   on-chain (measured by Taurus on Sepolia, Artefact 9); and the mechanism is deployed at scale (a16z-documented RWA
   transfer hooks). **The mechanism, the on-chain gate, and runnable harnesses already exist.**

**The narrowed, defensible gap claim (replaces the "unoccupied cell"):**

> The on-chain identity-gated-transfer mechanism **exists, is shipped (T-REX), and is deployed at scale**; what does not
> exist is a **complete A1–A5 benchmark** that packages it as a reusable, admission-gated, metric-defined performance
> workload — and no artefact packages the thesis's broader IDTx taxonomy (the full dependency-kind × locus ×
> evaluation-point space, not just receiver-allowlist transfer) as a workload.

So the contribution is a **new workload class + measured substrate breadth**, conceding that the mechanism, the on-chain
gate, and runnable harnesses (T-REX, CMTAT, Caliper) already exist. The surveyed scope is **EVM** (m9).

**Harness vs workload (M3).** "Ships an identity workload" and "can host one" are different claims and are separated
here. BLOCKBENCH, DIABLO and **especially Caliper** (which is explicitly *bring-your-own-workload*) **ship no identity
workload** but **can host one**: v0's W3 IDTx tier is implementable as a Caliper workload module against the register's
metrics. **The harness problem is largely solved; the contribution is the workload** — the IDTx taxonomy packaged as a
measurable workload class, not a new measurement tool.

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
- **W3 — the IDTx classes. [specified, not yet measured] (m8).** The four-cell taxonomy of `ANALYSIS.md` §4.4 as a
  workload: for each (dependency kind × locus × evaluation point) cell that a substrate can express, an operation whose
  admissibility depends on a *named* identity's state, evaluated in-transaction, with the `fulfil` re-check variant for
  the two-step case. The *receiver-allowlist* corner of this space is exactly what ERC-3643/T-REX and ERC-1404/CMTAT
  already ship on-chain (§3.2, F1); **what no existing artefact packages is the *full* taxonomy as a workload** (not
  just receiver-allowlist transfer) — that is the W3 contribution. **W3 is specified, not yet measured:** its prototype
  (`phase2/idtx/contracts/IdtxExecutor.sol`) is **emit-only** and its freshness numbers rest on the superseded
  register rows #32/#37 (pre-D51); it is therefore **not counted toward v0's "singly run" status** (§3.4). To anchor it
  externally rather than self-referentially (M6), W3 **adopts ERC-3643 compliance semantics (`isVerified` +
  `canTransfer`) as one concrete workload instance** (the receiver-allowlist cell), and the EUDI functional-conformance
  scenarios as a second candidate instance.

### 3.3.2 Admission rule (A2) — honest status: OPEN (M7)
A substrate is reported, for every W1 operation, as **native / composed / justified-`n-a`** (the Phase-2
n-a-vs-Absent rule). **This is a reporting/classification rule, not yet a genuine admit/reject gate:** as the examiner
(M7) notes, a scheme that admits everyone who either implements *or* justifies `n-a` has **no reject condition**, so it
is not an A2 pass/fail gate. Two honest options, and v0 takes the second:

1. *A genuine reject condition* would be, e.g., "a substrate is **rejected** if any **Set A core** operation is neither
   native nor composable (only a true `Absent`, not a justified `n-a`)" — a non-trivial gate that some substrates fail.
   This is a candidate for v0.1, **not yet adopted**.
2. **Concede A2 is OPEN for v0.** v0 ships the per-operation *classification* (the `IMinimalSSI` twelve-test suite is
   its executable form) but **not** a result-admission gate, so **A2 is not satisfied** (see §3.4).

**External anchor (M6).** To stop the rule being wholly in-house, v0 **adopts ERC-3643 compliance semantics**
(`isVerified(_to)` + `canTransfer(from,to,amount)`, EIP-3643, read at source) as one external referent for the W3
admission predicate — a substrate's receiver-allowlist IDTx instance is admissible exactly when it reproduces those
on-chain checks — **and/or** the EUDI functional-conformance scenarios for the credential-presentation instances. The
workload (W3) and the admission predicate are thereby tied to an external standard, not only to this repository.

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

**v0 axis status, restated honestly (M6, M7).** v0 is **A1 ✓** (the W1/W2 operation sets; W3 specified-not-measured,
m8), **A3 ✓** (register metrics with conditions), **A4 partial** (public runnable harness for W1/W2; the W3 tier is an
emit-only prototype, so A4 is not yet complete for the IDTx tier), with **A2 OPEN** (a classification rule, not a reject
gate — §3.3.2) and **A5 OPEN** (no independent reproduction). **v0 does NOT "satisfy A1–A4"** — that earlier claim is
withdrawn; the correct statement is **A1 / A3 / A4(partial), with A2 and A5 open.** Because W3 is specified-not-measured,
even the "singly run" status covers W1/W2, not the IDTx tier.

**A5 is a maturity property applied symmetrically (M4):** the examiner's even-handed point (Phase-1 obj. 4) holds —
*this thesis's own proposed benchmark also lacks an independent reproduction at publication; A5 is a maturity milestone
for any candidate, this one included,* and (new) A5 is not a Gray/TPC defining criterion, so it is not used to fail
prior art. The kit that would let an external party close A5 (and A2):

1. **A pinned environment** — the run-of-record's node, compiler, and transport (M1-H), as a container or lockfile.
2. **One command** — `npm run metrics:analyze` (or equivalent) emitting the register tables from a clean checkout.
3. **The admission gate as a test** — the conformance suite returning per-substrate native/composed/n-a.
4. **The W3 IDTx tier as a runnable workload** — the prototype generalized from `emit` to a measured effect (the
   current prototype demonstrates the admissibility predicate only; Phase-1 obj. 15), with the ordering-race condition
   reported.
5. **A results schema + a call for external runs** — a fixed table format so a second party's numbers are directly
   comparable, and an explicit invitation (Ch 7) for one.

**Milestone ladder:** v0 (A1 / A3 / A4-partial; A2 and A5 open; W1/W2 singly run, W3 specified-not-measured) → v0.1
(external environment pin + one-command run + a genuine A2 reject condition, §3.3.2) → **v1 (A5 met: one independent
reproduction; W3 measured)** → v1.x (cross-paradigm W1, the non-ledger systems). The thesis claims v0 at this status;
v1 is future work, and the measured IDTx study (paper P5) is where the W3 tier is run in earnest.

---

## Open items into the examiner pass (WP 3.6)
- A3's W3 metrics lean on #32/#37, flagged pre-D51 provisional (carried from Phase 1 obj. 7); the re-run is P5.
- The prototype demonstrates the predicate, not a measured effect (obj. 15) — §3.4 item 4 states this.
- v0 is EVM-scoped (§3.3.5); the cross-paradigm claim is explicitly deferred, not assumed.
