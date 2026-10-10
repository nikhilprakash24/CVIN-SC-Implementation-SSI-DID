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

### Amendments A1–A3 — 2026-10-09, **post hoc** (recorded after the first runs at `1e690c3`)
Raised by the adversarial review of after-action report 11 (finding A-F2): three departures had been
recorded only in after-action report 10 and the register. They are recorded here, marked post hoc.
- **A1 (I1).** I1 runs with k = ∞ (no revocation re-check on the warm SPaT path), because the warm
  BSM path it is compared with has none (decision F-A). I1 therefore compares warm paths without
  revocation checking; the cost of a re-check is **not** measured by I3 either (I3 counts messages).
  In this harness the re-check is an in-process lookup; a chain read costs milliseconds (#37, #40).
- **A2 (I4).** ERC-1056 has no identity-level revocation. The nearest operation, revocation of the
  RSU's key attribute (`revokeAttribute`), is measured; message-level RSU revocation is the
  credential registry (I3).
- **A3 (I5).** The measure as specified (median of the per-message sum along controller → RSU →
  vehicle) is not computable: in the harness the RSU's SPaT does not consume the controller's update,
  so there is no per-message chain. What is computed is the median across runs of the **sum of four
  per-run median operation costs**. It is a cost of the cryptographic operations on that path, not a
  path latency (no update period, queuing, network or tail).

### Amendment A4 — 2026-10-09, **before any code change or run of pass 11**
The adversarial review (after-action report 11, findings B-F1…B-F5) showed that the verifier did not
bind message fields to the credential (a valid RSU could sign SPaT for another intersection), did not
reject replays inside the freshness window (the design promised a replay check), did not re-check
credential expiry on the warm path, and reported every timestamp failure as "stale"; and that I2
recorded only whether an attack was rejected, not why, and only against first-contact receivers.
The verifier is hardened (field binding to `intersectionId` and `stationId`; a per-receiver replay
cache inside the window; warm-path expiry; reasons stale, future, replay, binding kept distinct),
and the experiments are re-run at the new commit as the runs of record. The first runs (#44–#48 at
`1e690c3`) stay in the register as history.
- **I2 (extended).** Thirteen checks per run, each with an expected rejection reason. Against a
  receiver with no cached state: (a) unsigned → `unsigned`; (b) wrong key → `wrong_key`; (c) MAP-only
  RSU signs SPaT → `not_permitted`; (d) vehicle credential (issuer outside the infrastructure trust
  list) → `credential_invalid`; (e) untrusted authority → `credential_invalid`; (f) stale (5 s) →
  `stale`; (g) forged controller update → `wrong_key`; **(h)** a valid RSU signs SPaT naming another
  RSU's intersection → `binding`; **(i)** a captured legitimate SPaT replayed to the same receiver
  inside the window → `replay`; **(j)** SPaT timestamped 0.5 s in the future → `future`. Against a
  receiver that has already cached the signer (warm): **(b-w)** → `wrong_key`; **(c-w)** → `not_permitted`;
  **(f-w)** → `stale`. **PASS** iff all 13 are rejected with their expected reason in every run;
  **FAIL** if any is accepted, or rejected for a different reason, in any run.
- **I1** rule unchanged (A1 applies). The hardened SPaT warm path does work the BSM warm path does not
  (binding compare, replay lookup; the BSM replay cache is off in the harness), so any bias is against
  SPaT. I1 is run with no other job on the host.
- **I3** rule unchanged.
- **I4** is run twice; the two gas tables are expected to be byte-identical (reported).
- **I5** is reported under the A3 definition.
- **Bootstrap.** Each reported quantity gets its own `random.Random(20260719)` (finding A-F9), so a
  quantity's CI no longer depends on how many quantities were computed before it. The I1 ratio CI was
  the first computed and is unaffected by this change.


### Amendment A5 — 2026-10-10, **post hoc** (recorded at the close of WM-1, from the milestone audit)
- **(d) changed meaning in A4 without saying so** (audit finding A-9). As registered on 2026-10-09, (d) was
  "SPaT from a vehicle (its credential permits BSM/DENM)", a test of the permitted-type check. In A4 and
  in the harness, (d) signs with a vehicle credential from the V2V issuer, which the infrastructure
  verifier does not trust, so it is rejected as `credential_invalid` — the same branch as (e). The
  permitted-type check for a credential from the trusted authority is exercised by (c) and (c-w). I2's
  13 checks are therefore **10 distinct attacks plus 3 warm variants**, and they exercise 9 distinct
  rejection branches; A4 added 6 checks to the original 7, not 12 (the design's §7 said 12).
- **A4's heading said "before any code change or run of pass 11"** (audit finding P-9). Commit
  `b1d3f72` changed the harness header two minutes before A4 (`98e64e4`); it touched only the run-identity
  metadata (`PRODUCING_PATHSPECS`, `code_clean`), no measured path. Read A4's heading as "before any
  change to the verifier and before any registered re-run".
- **Latency reporting** (audit finding A-5). The register's latency rule asks for median and p95 after
  three discarded warm-ups; the I1 and I5 driver discards no warm-up and reports no p95. The p95 of the
  run medians is computed from the committed per-run data and stated in rows #44 and #48 with this deviation.
