# Phase 2 Evidence Base — What Phase 1 Gives and What It Leaves Open

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, P2.0, session 1), against trunk `1012ebd`. **Binds:** `docs/phase2/README.md`.
**Sources:** the claim register (`docs/MEASUREMENT_CONDITIONS.md`), the crux register (`docs/thesis/CRUX_REGISTER.md`),
the defect log, the deferred list (`docs/MILESTONE_NEXT.md`), scope changes, chapter 7 §7.5–§7.6, `SIDE_PAPERS.md`,
the original direction (`docs/ORIGINAL_PROMPT_AND_DIRECTION.md`). Numbers below are quoted with their register row.
Phase 2 adds no number here.

## 1. What Phase 1 established (the assets Phase 2 reuses)
| Asset | What it is | Register / source | Phase 2 use |
|---|---|---|---|
| Nine-standard identity substrate | the same vehicle lifecycle on nine Ethereum identity standards plus two baselines, behind one adapter interface (`IdentityAdapter.js`, 11 adapters) | #25, #34; `1_blockchain-identity/benchmarks/adapters/` | ledger plane for every idea that needs a chain (I-03, I-08, I-12) |
| Gas results, exact and lifetime | per-operation gas; lifetime ranking reversal over 15 years | #25, #26 | baseline to compare public-chain and rollup costs against (I-03) |
| V2V verification within the budget | SSI warm verify 0.153 ms [0.151, 0.154], cold 0.399, against PKI | #27 | the hot-path cost every new credential format is measured against (I-06, I-10) |
| Freshness measured | re-check every k messages: the knee between k = 1 and k = 5 | #32, #37 | the data a freshness theory must predict (I-05) |
| Infrastructure messaging | signed SPaT/MAP from credentialed RSUs; I1–I3 pre-registered and passed; a revoked RSU honoured for at most k − 1 messages | #44–#46 | the base of the RSU trust mesh (I-04) and of time-to-exclusion (I-07) |
| Security, tested | 43 of 43 applicable attack cells defended under a strict harness | #28 | the tested baseline that formal methods would partly prove (I-12) |
| W3C conformance, structural and external | internal checker 94.3 % (structural self-score); external DID suite 335 of 336 | #4, #24 | the base of external validity on chain-backed documents (I-16) |
| Evidence machinery | claim register; stamps with per-producer scope (`tools/run_identity/`); promote step; stale-figure checker; generated dashboard and presentation; audits | WM-1 report; reports 13–15 | Phase 2 inherits it; I-18 asks whether it generalises |
| Lifecycle profile | MOBI VID I + II realised on several backends with a fidelity score | `2_w3c-ssi-layer/mobi-vid`; `cv2x-testbed/identity/lifecycle_backends.py` | standards track (I-15, I-17) |

## 2. What Phase 1 leaves open, as seeds
A seed is an open item Phase 2 can start from. Each names its Phase 1 source and the ideas that grow from it.

| Seed | Open item | Phase 1 source | Ideas |
|---|---|---|---|
| S-01 | All V2V and V2I results are under mock mobility; no traffic simulation run | C2, C3, N-4, SC-22 | I-01, I-11, I-07 |
| S-02 | No radio or MAC: the safety budget is checked computationally only | C2, chapter 5; SC-03 (5G NR-V2X demoted) | I-02, I-23 |
| S-03 | All gas is local; the Sepolia witness is undone; no fee calibration | N-11, #25, #26, chapter 6 | I-03 |
| S-04 | No RSU-to-RSU messaging; the C3 cache never expires | C3, N-16 | I-04 |
| S-05 | The thesis must choose k; a message bound is not a time bound; clock skew accepts a revoked key | C4, N-17, D51, guide 1.1.9 | I-05, I-13 |
| S-06 | Hybrid PKI–DID and ML misbehaviour detection were demoted as PhD-scale | SC-03 | I-06, I-07 |
| S-07 | Signed operations omit the chain id; owner-0 seizure; attestation authority | D52, D53, D54, N-9 | I-08, I-12 |
| S-08 | The ZK VIN tier was deferred; privacy beyond the ledger is future work | SC-12, C7 | I-09, I-11 |
| S-09 | One credential suite only; C7 has no hypothesis | C5, C7, #26 | I-10 |
| S-10 | Verifier robustness defects found by reading, not by tools | D37–D42 | I-14 |
| S-11 | Few MOBI VID I MUSTs met; scope changes pending | C6, SC-17, SC-18 | I-15 |
| S-12 | W3C checks run on a synthesised document | C5, #4 | I-16 |
| S-13 | Only W3C and MOBI frames; no regulatory frame | C5, C6 | I-17 |
| S-14 | The evidence machinery is bespoke to this repository | D33, D49, D50 | I-18, I-22 |
| S-15 | Open release and newcomer reproduction untested | N-2, N-12, original direction B.9 | I-19 |
| S-16 | The author's notebook research has no intake channel yet | original direction B.3; `MASTER_UPDATE.md` §7 | I-20 |
| S-17 | Eight side papers listed, none written | `SIDE_PAPERS.md` | I-21 |
| S-18 | The re-scoped LLM interface of the original brief | original direction §C | I-22 |

## 3. Chapter 7 §7.6 future work, mapped
| §7.6 item (smallest to largest lift) | Ideas |
|---|---|
| Sepolia validation run | I-03 (witness arm) |
| Real SUMO plus ns-3 radio and MAC | I-01, I-02 |
| Denser and adversarial-density scale | I-01 with I-07 |
| Formal verification and model checking of the contracts | I-12, I-13 |
| Cross-jurisdiction identity and ZK selective disclosure | I-09, I-10, I-17 |
| Standardization engagement with MOBI | I-15 |

## 4. The cruxes, and which ideas move them
All eight cruxes are partial (none a gap, none fully evidenced). An idea "moves" a crux if its result would
change the crux's status line.

| Crux | Ideas that move it |
|---|---|
| C1 Substrate | I-03, I-06, I-08, I-12 |
| C2 V2V messaging | I-01, I-02, I-06, I-23 |
| C3 V2I / I2I | I-01, I-04, I-07, I-13 |
| C4 Revocation freshness | I-05, I-07, I-13 |
| C5 W3C | I-10, I-16, I-17 |
| C6 MOBI VID | I-15, I-17 |
| C7 Privacy | I-09, I-10, I-11 |
| C8 Veracity vs automation | I-22 (indirectly); no idea moves it directly: **a gap in this register** (B1-12) |

## 5. Constraints Phase 2 inherits
- WM-2 is not closed. Its open steps (C0 verifier v3 with the D51 fix, C1 chain-reading resolver, C2 restricted
  attestation, the re-runs) change code that several ideas build on. Ideas that depend on those paths start
  their build only after the Phase 1 step (`ROADMAP.md` §3).
- Author decisions pending in Phase 1 bear on Phase 2: N-4 (SUMO install) gates I-01; N-11 (Sepolia secrets,
  tags) gates I-03; N-9 (upstream fidelity) frames I-08; N-23 (AI-use disclosure) applies to every Phase 2
  document as much as to Phase 1.
- The degree's timeline. Phase 2's first build wave must fit whatever the author decides remains before the
  defence (P2-D2).
