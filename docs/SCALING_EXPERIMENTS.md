# Scaling & Sensitivity Experiments — Design

*Research design for the scaling study (addresses `RESEARCH_AUDIT.md` §4.8: "no
scaling studies"). Written before implementation so the hypotheses, variables, and
controls are fixed in advance — not fitted to whatever the data happens to show.*

## Motivation — reframing the cost question

The gas benchmark (§5.2) measures the **first** operation on a fresh identity. But a
vehicle identity is not a point event: it is a **decades-long accumulating record** —
one birth certificate, then a lifetime of maintenance events, ownership transfers,
recalls, and inspections. Over a 15–20 year service life a vehicle may accrue dozens
of lifecycle events. The deployment-relevant question is therefore not *"what does one
operation cost?"* but:

> **RQ-S1.** As a vehicle accumulates history, does per-operation cost stay constant
> (O(1)) or degrade (O(n))? A standard whose marginal cost grows with history is
> disqualifying at automotive lifetimes.
>
> **RQ-S2.** What is the *integrated* cost of a realistic vehicle lifetime per standard?
>
> **RQ-S3.** Does credential **verification** stay within the V2V budget as credentials
> grow richer and as neighbor density rises (the dense-intersection case)?

This turns a point comparison into a lifecycle comparison — a novel and, we argue,
more decision-relevant framing.

## Experiment A — Marginal-cost stationarity (RQ-S1)

**Design.** On a fresh deployment of each standard, perform K = 50 sequential
same-type "append to history" operations; record `gasUsed[i]` for each i ∈ [1, 50].

**Per-standard operation (grounded in the real contracts):**
| Standard | Append operation | A priori expectation |
|---|---|---|
| ERC-1056 | `setAttribute` (event-log; no array growth) | flat, O(1) |
| ERC-735 | `addClaim` (mapping + topic-id array push) | test for growth |
| ERC-1155 | issue/mint a credential token | ~flat |
| CVIN-Combined | `addClaim` | test for growth |
| MOBI-VID-V2 | `recordLifecycleEvent` (events array append) | append O(1); test |

**Variables.** IV: operation index i (with fixed-size payload, same actor).
DV: `gasUsed[i]`. **Control:** identical payload each op; fresh chain per standard;
optimizer fixed at 200 runs.
**Analysis.** Least-squares slope of gas vs i; report slope (gas/op) and R². Slope ≈ 0
⇒ O(1) marginal cost; slope > 0 ⇒ history-dependent degradation. Report the first-op
vs 50th-op delta explicitly.

## Experiment B — Lifetime cost model (RQ-S2)

**Design.** Define a canonical, defensible 15-year event profile and integrate the
measured per-op costs (from A + the benchmark) into a total lifetime gas figure per
standard.

**Canonical lifecycle profile (stated as an assumption, varied in sensitivity):**
1 birth certificate · 30 maintenance events (2/yr × 15) · 3 ownership transfers ·
4 periodic inspections · 1 recall  → ≈ 39 recorded events.

**Output.** A lifetime-gas table + bar chart per standard, decomposed by event class.
This is the deployment headline: *cost of a vehicle's whole identity, not one write.*
**Honesty:** the profile is an assumption; report the model and let it be varied
(±50% event frequency) as a one-line sensitivity band. Gas is relative on-chain work,
not fiat (per `RESEARCH_AUDIT.md` §4.1).

## Experiment C — Verification latency vs credential richness (RQ-S3a)

**Design.** Issue VCs carrying N ∈ {1,2,4,8,16,32} claims; measure verification latency
(median over ≥200 warm runs, real secp256k1). Repeat for selective disclosure (disclose
k of N). **DV:** verify latency; **IV:** claim count N (and disclosed k).
**Analysis.** Fit latency(N); report the scaling order and whether it stays ≪ the 10 ms
signature-check target across the range. Same repeatability caveat as §5.4 (single host,
crypto-only).

## Experiment D — V2V verification load vs neighbor density (RQ-S3b) — the saturation point

**Design.** In the SUMO harness, vary neighbor count P ∈ {5,10,20,40,80} that each
vehicle must verify per 10 Hz BSM interval; measure per-vehicle per-interval verification
time (warm, cached peers). **The engineering deliverable:** the **verification saturation
point** — the density P\* at which per-interval verification exceeds the 100 ms budget
(if within range). This is the dense-intersection scenario and a genuinely useful result.
**Honesty:** crypto verification load only; excludes radio/MAC (per §4.4).

## Sensitivity analyses

- **SN-1 — optimizer runs.** Re-measure representative operations at solc optimizer
  runs ∈ {1, 200, 10000}; report gas deltas so the headline numbers aren't an artifact of
  one setting.
- **SN-2 — calldata composition.** Quantify the zero-byte vs non-zero-byte calldata gas
  effect (the source of the +12-gas artifact seen in the Sepolia dry-run), so signature/
  address byte patterns are accounted for, not mysterious.

## Deliverables
- `4_comparison-framework/results/scaling_marginal.json` (Exp A), `scaling_lifetime.json`
  (Exp B), `scaling_verify.json` (C/D), `sensitivity.json` (SN).
- Table/figure generators → CSV + LaTeX in `4_comparison-framework/results/`.
- A Chapter 5 sub-section (§5.9 Scaling & Lifetime Cost) reporting A–D with the RQ-S
  verdicts, held to the `COMPOSITION.md` Part II discipline.

## Validity notes (carried from the audit)
Marginal-cost slopes are exact/deterministic (report as such, not as CIs). Latency uses
the §5.4 repeatability framing. Lifetime cost is a **model** over an assumed profile,
labeled as such. All gas is relative on-chain work.
