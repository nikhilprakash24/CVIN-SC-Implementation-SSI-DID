# Pre-registration — Infrastructure Messaging Experiments I1–I5

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Locked:** 2026-10-09, in the commit that adds this file, **before the first run**. Any later change
is appended as a dated amendment below; the original text is never edited.
**Design:** `docs/design/INFRASTRUCTURE_MESSAGING.md` (approved by the author 2026-10-09 with defaults
I-a…I-d: back-haul included and reported only; RSU layer in the visualisation; chapter-5 section if run).
**Crux:** C3 (`docs/thesis/CRUX_REGISTER.md`).

## 1. Common conditions
| Item | Value |
|---|---|
| Harness | `cv2x-testbed/sumo/sumo_identity_integration.py --simulate --rsu` (mock mobility; SUMO not installed, decision S-b) |
| Statistics driver | `cv2x-testbed/sumo/run_infra_stats.py`, same method as `run_v2v_stats.py`: independent subprocesses, seeds 1…30 |
| Duration / vehicles | 20 s simulated per run, 50 vehicles, 10 Hz BSM (unchanged V2V population: 70 % SSI, 30 % PKI) |
| Infrastructure | 4 RSUs along the 5 km highway at x = 625, 1875, 3125, 4375 m, each with its signal controller; 1 traffic-management centre (TMC) |
| Identities | road authority = issuer DID (trusted anchor); RSU, controller and TMC each a `did:ethr` with a credential from the authority listing permitted message types |
| V2I | each RSU signs a SPaT at 10 Hz (EIP-191 over canonical JSON with a signed timestamp); delivered to the ≤ 8 nearest vehicles within 300 m (the BSM radio model) |
| I2I | each controller signs a signal-state update every 1 s → its RSU verifies; the TMC signs a timing plan every 5 s → each controller verifies |
| Verification | freshness window (T-9 policy); signature recovery; cold path = credential verification (trusted issuer, validity, revocation, subject binding) + permitted-type check; warm path = cached signer address + permitted type |
| Condition tags | latency M0 (in-process, no radio); gas M1 (Hardhat local) |

## 2. Hypotheses, measures and verdict rules
| ID | Question | Measure | PASS if | FAIL (falsified) if | Otherwise |
|---|---|---|---|---|---|
| **I1** | Does SPaT verification fit the same budget as BSM? | per run: median warm SPaT verify ÷ median warm SSI BSM verify (same run); across 30 runs: median ratio with 95 % bootstrap CI | median ratio in [0.80, 1.20] | median ratio > 2.0 | "outside band, not falsified" |
| **I2** | Are forged or out-of-scope infrastructure messages rejected? | injected per run: (a) unsigned SPaT; (b) SPaT signed with a key that is not the claimed RSU's; (c) SPaT from an RSU whose credential permits MAP only; (d) SPaT from a vehicle (its credential permits BSM/DENM); (e) SPaT from an RSU credentialed by an untrusted authority; (f) stale SPaT (5 s old); (g) forged I2I controller update | every attack rejected in every run | any attack accepted in any run | — |
| **I3** | How long do vehicles keep trusting a revoked RSU? | the authority revokes RSU 1's credential at t = 10 s; verifiers re-check revocation every k-th message from a cached signer, k ∈ {1, 5, 25, ∞}; count SPaT accepted per (vehicle, RSU 1) after revocation | for every finite k, max accepted after revocation ≤ k − 1 | any finite k exceeds k − 1 | k = ∞ is reported (expected: never stops) |
| **I4** | What does an RSU identity cost on chain? | gas: anchor the RSU's verification key as an ERC-1056 attribute; change of controller; revocation of the RSU identity — on `EthereumDIDRegistry` | reported (no verdict) | — | — |
| **I5** | What does the I2I back-haul add? | per run: median (controller sign + RSU verify + RSU SPaT sign + vehicle warm SPaT verify), and the TMC → controller hop | reported (no verdict) | — | — |

## 3. What will be reported regardless of outcome
All five rows enter the claim register (#44–#48) with their verdicts as they fall; a FAIL is reported
as a FAIL. The `--rsu` flag is off by default, so the V2V results of record (#27) are unaffected;
a run without `--rsu` must reproduce the same message, verification and attack counts.

## 4. Amendments
*(none)*
