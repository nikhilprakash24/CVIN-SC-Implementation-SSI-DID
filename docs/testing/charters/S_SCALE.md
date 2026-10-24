# Charter S — Scale

**Status:** draft, 2026-10-22. **Binds:** `docs/SCALING_EXPERIMENTS.md` (pre-registration); guide 1.2.7.

## 1. What a scale result establishes
How a cost or a latency changes with registry population N, per-identity history h, claim count, or neighbour density,
over the tested range. It does not establish behaviour beyond the tested range; an extrapolated point (a saturation P*)
is labelled as an extrapolation.

## 2. Oracle
A pre-declared shape: flat (O(1)), linear with a slope, or a named class, judged by a fitted slope with its R² or by a
pre-declared tolerance, over pre-declared points.

## 3. Design
Points declared before the run (N ∈ {0, 100, 1 000}; h ∈ {1, 10, 50}; P ≤ 80); repeats declared before the run
(Exp. C's five-repeat confirmation block, #26). Gas axes are exact; latency axes follow the latency charter (`../LATENCY_CHARTER.md`).

## 4. Falsifiers it carries
| Hypothesis | Refuting observation | Rows |
|---|---|---|
| H1′ (marginal cost flat in N) | a positive slope in N beyond the declared tolerance | #31 |
| "resolution cost grows with history for event-log options" | flat R3 cost in h for ERC-1056 | #31, #51 |
| verify O(1) in claim count | slope in claims beyond tolerance | #26 (C) |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Construct | population built by the harness, not by real usage | stated |
| Internal | tokenId width and calldata zero bytes move gas by a few units | gas classes (`GAS_CHARTER.md`) |
| External | extrapolation beyond tested points | labelled |

## 6. Reporting
Slope, R², tested range and the extrapolation flag in every table.

## 7. Replication
Exp. A/B status B (bundle lineage) until re-executed on this trunk's definitions (#26).

## 8. Limits
No unit tests carry class S; scale evidence is experiments only (`coverage_matrix.md`).
