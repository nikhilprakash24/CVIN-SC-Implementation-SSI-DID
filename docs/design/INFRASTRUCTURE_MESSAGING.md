# Design Note — Infrastructure Messaging (V2I and Infrastructure-to-Infrastructure) on the Thesis Identity Layer

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Status:** **APPROVED by the author 2026-10-09 with defaults I-a…I-d; pre-registration locked in `docs/design/INFRASTRUCTURE_PREREG.md`.** (Was: design for audit, no code until approved (plan 2026-10-09 P4.3; scope
default Q1: V2I and infrastructure-to-infrastructure, starting with signed SPaT from a
DID-identified roadside unit).)
**Written:** 2026-10-09. **Fills:** crux C3 in `docs/thesis/CRUX_REGISTER.md`, the only crux with no
evidence. **Builds on:** `cv2x-testbed/V2_DESIGN.md` §"Infrastructure Integration" (an RSU class with
SPaT/MAP, designed 2025-11, never built).

## 1. The gap in one paragraph
Every message-path result in the thesis is vehicle-to-vehicle (register #21, #27, #32, #37, #39).
The title and chapter 1 speak of connected and autonomous vehicles, which in every deployment
standard includes infrastructure: roadside units (RSUs) broadcasting signal phase and timing
(SPaT) and intersection geometry (MAP), and back-haul links between RSUs, signal controllers and
a traffic-management centre (TMC). An examiner will ask where the infrastructure is. The identity
layer is substrate-agnostic, so the cheapest honest answer is to show that an RSU is one more DID,
issued by a road authority, and to measure what that costs and how revocation behaves.

## 2. Grounding (canonical work; identifiers to be verified against the texts before citation)

| Source | What it fixes for this design | Incorporated how |
|---|---|---|
| SAE J2735 (message set dictionary) | SPaT and MAP are the V2I messages; BSM is V2V. SPaT is broadcast about every 100 ms per intersection | the experiment signs SPaT-shaped payloads at 10 Hz, the BSM rate the V2V results use, so the two are comparable |
| IEEE 1609.2 (security services for WAVE) | infrastructure messages are signed with application certificates whose permissions (PSID/SSP) name the message type; RSUs hold longer-lived certificates than vehicles' pseudonyms | the RSU's credential carries the permitted message types as a claim; the verifier checks the claim, not just the signature |
| ETSI TS 103 097 and TS 102 941 (EU C-ITS security header and trust management) | the same split in Europe: authorisation tickets per station, a trust list, certificate revocation | the road authority is the issuer; its issuer key is the trust anchor; revocation is checked the way the V2V path checks it |
| CAMP SCMS (US security credential management system) | revocation by misbehaviour reporting and certificate revocation lists; RSUs are not pseudonymous | RSU revocation is the experiment's interesting axis (§4), measured against the PKI baseline's CRL path |
| NTCIP 1202 / 1211 (signal-controller and priority objects) | infrastructure-to-infrastructure today is SNMP-style object access between TMC and controllers, often on private networks | the I2I part is modelled as signed controller-state updates between DID-identified nodes, not as a radio broadcast; flagged as a modelling choice |

## 3. Design

### 3.1 Identities
| Entity | Identity | Issuer | Credential |
|---|---|---|---|
| Road authority | `did:ethr` controlled by the authority's key | — (trust anchor, configured) | — |
| RSU | `did:ethr` per RSU | road authority | `InfrastructureStationCredential`: location, intersection id, permitted message types (SPaT, MAP), validity |
| Signal controller | `did:ethr` per controller | road authority | `SignalControllerCredential`: intersection id, permitted updates |
| TMC | `did:ethr` | road authority | `TrafficManagementCredential` |
| Vehicle | unchanged (`did:ethr`, MOBI birth certificate, V2V credential) | unchanged | unchanged |

All credentials are issued through the canonical VC layer (`2_w3c-ssi-layer/verifiable-credentials`),
so the trusted-issuer list (review-2 T-3) and the freshness and replay policy (T-9) apply unchanged.

### 3.2 Messages and paths
| Path | Message | Signer | Verifier | New code |
|---|---|---|---|---|
| V2I broadcast | SPaT (phase, time-to-change, intersection id) and MAP (lane geometry, sent rarely) | RSU | every vehicle in range | an `RSU` station in the testbed message path, sending at 10 Hz |
| I2I back-haul | signal-state update; TMC timing plan | controller → RSU; TMC → controller | RSU; controller | a small in-process bus between infrastructure nodes |
| I2V revocation | the authority revokes an RSU's credential | authority | vehicles | reuses the revocation registry and the freshness-k policy |

The verifier on a vehicle does, in order: the freshness window and replay check (T-9); the
signature against the RSU's DID key (cold: resolve and verify the credential; warm: cached key);
the credential's permitted-message-type claim covers SPaT; the credential is not revoked.

### 3.3 What is reused, what is new
Reused: the identity providers, the VC layer, the freshness policy, the V2V harness's timing and
attack-injection code. New: an RSU station type, a SPaT/MAP payload, the permitted-type claim
check, the infrastructure bus, and a trace of each message for the visualisation
(`docs/PLAN_SUMO_VISUALISATION.md`).

## 4. Pre-registered experiment (to be fixed before the first run)

| ID | Question | Measure | Pre-registered expectation | Falsifier |
|---|---|---|---|---|
| I1 | Does SPaT verification fit the same budget as BSM? | warm and cold verify latency per SPaT, N = 30 seeded runs, M0 | warm within ±20 % of the SSI BSM warm verify of the same run | warm SPaT verify > 2× warm BSM verify |
| I2 | Is a forged or out-of-scope SPaT rejected? | injected attacks: unsigned, wrong key, valid RSU key but no SPaT permission, replayed, stale | all rejected, zero false accepts | any accept |
| I3 | How long do vehicles keep trusting a revoked RSU? | messages accepted after revocation, as a function of the freshness k | at most k − 1 (as for vehicles, #32) | more than k − 1 |
| I4 | What does an RSU identity cost on-chain? | gas to create the RSU DID and anchor its key; per-credential issuance cost | one ERC-1056 identity plus one attribute (same order as #1/#2) | — (reported) |
| I5 | Does the I2I back-haul change any of the above? | end-to-end controller-update → SPaT latency, in-process | sum of two signed hops | — (reported) |

Conditions: M0 for latency (in-process, no radio), M1 for gas. Mobility as in the V2V runs
(`--simulate` unless SUMO is approved). Results file with the environment header; one register row
per experiment; status V only from a clean tree.

## 5. Threats to validity, designed in
- No radio, no channel loss, no MAC (as for V2V): stated in every figure.
- Real deployments use IEEE 1609.2 certificates for RSUs; this models them as VCs. The comparison is
  the identity layer's cost, not a claim of interoperability with deployed RSUs.
- The I2I back-haul is in-process; real back-haul is a wired network with its own security
  (often TLS or a private network). I5 is reported, not compared.

## 6. Decisions for the author
| # | Decision | Default |
|---|---|---|
| I-a | Approve the design and the pre-registration as written | — (blocks code) |
| I-b | Include the I2I back-haul (I5), or V2I only | include, reported only |
| I-c | Add an RSU layer to the SUMO visualisation | yes, once I1–I3 run |
| I-d | Chapter treatment: a section in ch. 5 (results) and a paragraph in ch. 1 narrowing or widening the scope | section in ch. 5 if I1–I3 run; otherwise narrow ch. 1 to V2V |

## 7. As built (recorded 2026-10-10 at the close of work milestone WM-1)
| Design element | As built | Where |
|---|---|---|
| RSU, controller, TMC as `did:ethr` with road-authority credentials (§3.1) | built; the authority is the only trusted issuer | `cv2x-testbed/sumo/infrastructure_layer.py` |
| Signed SPaT, controller → RSU and TMC → controller I2I (§3.2) | built; MAP content and RSU-to-RSU messaging not built (SC-21) | same; harness `--rsu` |
| Freshness window **and replay check** (§3.2) | freshness built in the first version; **replay check missing until the review** (D29), built at `f1f9e37` as a per-receiver cache | `docs/DEFECT_LOG.md` §F |
| Binding of message fields to the credential | **not in this design**; added after the review (D28: SPaT for another intersection was accepted) | `f1f9e37` |
| Revocation re-check every k messages (§3.2) | built; registry in-process; warm-path expiry added after the review (D30) | register #46 |
| I2 attack list (§4): "unsigned, wrong key, no SPaT permission, **replayed**, stale" | the pre-registration of 2026-10-09 dropped "replayed" without an amendment; amendment A4 restored it and added further checks (7 → 13 checks: 10 attacks and 3 warm variants; amendment A5) | `INFRASTRUCTURE_PREREG.md` §4 |
| Experiments I1–I5 (§4) | run twice (`1e690c3`, `f1f9e37`); results of record at `f1f9e37` | register #44–#48, chapter 5 §5.4.1 |
