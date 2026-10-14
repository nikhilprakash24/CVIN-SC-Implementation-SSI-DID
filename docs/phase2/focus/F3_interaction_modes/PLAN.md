# F3 Plan — Interaction-Mode Experiments (Pre-Registration Draft)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F3, plan). **State:** a draft, not locked, nothing run (principle 4).
**Builds on:** `ANALYSIS.md`; `classify_modes.py` and `MODE_CLASSIFICATION.md` (EXECUTION.md).

## 1. Experiments
| ID | Question | Design | Measure | Prediction | Needs |
|---|---|---|---|---|---|
| **E-F3-1** | How does each Phase 1 interaction classify, by rule? | **done as a generated table:** harness operations and demo steps classified (`MODE_CLASSIFICATION.md`) | counts per class; unclassified reported | — (descriptive) | — |
| **E-F3-2** | What does a verified B-serve read cost against an unverified one? | resolve the same identity through a provider, with and without a state proof (`eth_getProof`) checked against a trusted block header | RPC calls, bytes, latency (N ≥ 30, one host, within-run comparison) | a proven read costs one extra call and a few kilobytes; latency dominated by the network | a public provider (N-11) |
| **E-F3-3** | Can a write be detached (signed now, anchored later) without the nonce problem? | lifecycle events signed offline over a per-vehicle sequence number instead of the registry nonce, batched and anchored as a Merkle root | anchor gas per event against direct writes; rejection of a reordered or replayed event (test) | per-event gas falls with batch size; every reordered or replayed event rejected | the F2 anchor contract (F2-S3) |
| **E-F3-4** | Which mode should each message class use? | a decision table over message classes (BSM, SPaT, MAP, lifecycle event, ownership transfer, revocation) against the latency budget, trust and staleness | a selection rule, checked against the measured costs | Mode C for all 10 Hz classes; A or B-submit for lifecycle writes; A with a probe for revocation re-checks | E-F3-2 |

## 2. Steps
| Step | Work | Gate |
|---|---|---|
| F3-S1 | **done:** the generated classification (E-F3-1), in CI | `--check` |
| F3-S2 | the author decides the taxonomy (P2-D7) | decision recorded |
| F3-S3 | fix the demo logging so steps carry their kind (D61), then retire the rule-based demo table | grand report split comparable across options |
| F3-S4 | lock this plan; run E-F3-3 locally; run E-F3-2 when N-11 allows | pre-registration committed first |
| F3-S5 | E-F3-4 from the measured costs | academic review |

## 3. Risks
| Risk | Mitigation |
|---|---|
| The author's three modes differ from the default | three alternative cuts are mapped in `ANALYSIS.md` §2; the classification script takes the taxonomy as data |
| Provider latency varies with time and place | within-run comparison only; dated; never compared across days |
| The rule-based demo classification misleads | it is labelled approximate, reports its unclassified count, and is retired by F3-S3 |
