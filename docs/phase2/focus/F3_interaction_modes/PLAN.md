# F3 Plan: Interaction-Mode Experiments (Pre-Registration Draft)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F3, plan). **State:** a draft, not locked, nothing run (principle 4).
**Builds on:** `ANALYSIS.md`; `classify_modes.py` and `MODE_CLASSIFICATION.md` (EXECUTION.md).
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-25, AR-29, AR-32, AR-33, AR-35, AR-41

**In the thesis, this plan is one future-work paragraph** (review §4.1). It serves paper P4 and Phase 2's A/B/C frame (`ANALYSIS.md` §3).
Every prediction below is fixed before any run; a cell marked "at lock" is fixed when the plan is locked (F3-S4), before any run.

## 1. Experiments and one design step
| ID | Kind | Question | Design | Measure | Needs |
|---|---|---|---|---|---|
| **E-F3-1** | descriptive, done | How does each Phase 1 interaction classify, by rule? | **done as a generated table:** harness operations and demo steps classified (`MODE_CLASSIFICATION.md`), with the cross-tabulation of the grand report's flag against rule class in §3 | counts per class; unclassified reported | none |
| **E-F3-2** | experiment | What does a verified provider read cost, against an unverified one? | for one ERC-1056 identity on Sepolia, read three storage values (the owner, `changed`, one delegate's expiry) with `eth_getProof` (EIP-1186), and verify the account and storage proofs against a block header taken from an **independent light client**, not from the provider. In the same run, read the same values unverified by `eth_call` at the same block. Attributes held only in logs need a receipt proof and are **out of scope** | provider RPC calls and light-client calls, counted separately; response bytes; latency median and p95, n = 50 per arm, one host, one dated run; the verification outcome per value | a public provider and a funded key (N-11); a light client for Sepolia |
| **E-F3-3** | experiment | What delay and what validity bound does a detached write carry, and can it avoid the nonce problem? | lifecycle events signed at t₀ over a per-vehicle sequence number and an expiry, generated at a fixed interval Δ, included at t₁ through A or B in batches of B ∈ {1, 10, 100} anchored as a Merkle root; **interval mining** at a stated block interval T_b, not automine | t₁ − t₀ per event, in blocks and seconds; the validity bound (the expiry) and whether late inclusion is refused; the count of signed but unanchored events at the worst instant; rejection of reordered and replayed events | the F2 anchor contract (F2-S3) |
| **D-F3-1** (was E-F3-4) | **design step, not a test** | Which mode should each message class use? | a decision table over message classes (BSM, SPaT, MAP, lifecycle event, ownership transfer, revocation) against the latency budget, trust and staleness, filled from the measured costs per path and host (`ANALYSIS.md` §4) | a selection rule, stated with its inputs | E-F3-2, E-F3-3 |

## 2. Predictions, verdict rules and kill criteria
| ID | Point prediction and band | Verdict rule | Kill criterion |
|---|---|---|---|
| **E-F3-1** | none (descriptive) | no verdict; the unclassified count is reported | retired by F3-S3, once steps carry their kind when logged |
| **E-F3-2** | (a) Provider calls: 1 `eth_getProof` carrying the three storage keys (EIP-1186 takes a list of keys for one account; recalled, check at source) against 3 `eth_call` for the unverified arm, plus the light client's header. (b) Every proven value equals the `eth_call` value at the same block. (c) A proof with one altered byte, or checked against another block's header, is rejected. The delegate's expiry is compared with the header's timestamp, not the verifier's clock (D51). (d) Bytes and latency: point and band at lock (the repository holds no basis) | PASS if (a), (b) and (c) all hold; (d) is reported with its band verdict | stop if no independent light client is available for the target network: a header from the same provider adds no trust, so the experiment would measure nothing |
| **E-F3-3** | (a) At most B − 1 events signed and not yet anchored at the worst instant (the same window as F2's N − 1 entries, and the write-side twin of k − 1). (b) Maximum t₁ − t₀ = (B − 1) · Δ + T_b, band [(B − 1) · Δ, (B − 1) · Δ + 2 · T_b]. (c) Every event presented after its expiry, and every reordered or replayed event, is rejected. Anchor gas ÷ B is arithmetic: reported, no verdict | PASS if (a), (b) and (c) all hold for every B | not run until F2-S3 exists; stop if a replay cannot be rejected without the registry nonce, since the design then has the nonce problem it was meant to remove |
| **D-F3-1** | none: a design step has no prediction | none; it is reviewed, not tested | none |

## 3. Steps
| Step | Work | Gate |
|---|---|---|
| F3-S1 | **done:** the generated classification (E-F3-1), in CI | `--check` |
| F3-S2 | the author decides the frame (P2-D7): six cells for the thesis, A/B/C for Phase 2 and P4 | decision recorded |
| F3-S3 | fix the demo logging so steps carry their kind (D61), then retire the rule-based demo table | grand report split comparable across options |
| F3-S4 | fix the "at lock" cells, lock this plan; run E-F3-3 locally; run E-F3-2 when N-11 and a light client allow | pre-registration committed first |
| F3-S5 | D-F3-1 from the measured costs | academic review |

## 4. Risks
| Risk | Mitigation |
|---|---|
| The author's three modes differ from the default | the alternative cuts become attributes in `ANALYSIS.md` §3; the classification script takes the taxonomy as data |
| Provider latency varies with time and place | within-run comparison only; dated; never compared across days |
| Automine lets the experimenter create the detached-write window | E-F3-3 runs under interval mining with a stated block interval |
| The rule-based demo classification misleads | it is labelled approximate, reports its unclassified count, and is retired by F3-S3 |
