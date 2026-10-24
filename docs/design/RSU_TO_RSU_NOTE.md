# Design Note: RSU-to-RSU Messaging (WM-2 D2, Deferred Item N-16)

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-24 (after-action report 37, unblocked item U5).
**Status:** **decided 2026-10-24: D2-a, out of scope** (the author; SC-24). Nothing is built, and nothing here is a result.
**Reads:** crux C3 in `docs/thesis/CRUX_REGISTER.md`; `docs/design/INFRASTRUCTURE_MESSAGING.md` §3 and §7;
`cv2x-testbed/sumo/infrastructure_layer.py`; register rows #44 to #48.

## 1. The question
Crux C3 asks whether the identity layer secures infrastructure messages: SPaT and MAP, RSU-to-RSU, and
RSU-to-traffic-management. Five verified rows answer it for two of the three link types:

| Link | Built | Evidence |
|---|---|---|
| RSU to vehicle (signed SPaT) | yes | #44 warm cost, #45 15 checks rejected for their reasons in 30/30 runs, #46 revocation bound k − 1 |
| Controller to RSU, TMC to controller (back-haul) | yes, in-process | #45, #48 (sum of four operation costs on that path) |
| RSU to RSU | **no** | stated as a gap in C3 and in `INFRASTRUCTURE_MESSAGING.md` §7 |

## 2. What RSU-to-RSU messaging would be
In deployed corridors, roadside units exchange messages with each other mainly for three jobs. These are named
here from the design note's grounding and need checking against the standards before any citation:

1. **Relaying a warning along a corridor.** RSU A hears a hazard and RSU B rebroadcasts it to vehicles that never
   heard A.
2. **Handing over state.** One RSU passes a revocation update or a misbehaviour report to the next.
3. **Coordination between neighbouring intersections.** For example, signal-phase plans for green waves. Today this
   usually goes through controllers and the TMC, which the current build already covers.

## 3. What it would add to C3, and what it would not
**Already covered by the existing mechanism.** One RSU-to-RSU hop is a signed message from one credentialed
infrastructure node to another. `InfrastructureLayer` already checks the sender's DID, its road-authority credential,
expiry, replay, and that the message type is in the credential's permitted list. So a single hop adds no new identity
mechanism. It is a new entry in the permitted-type table and a new path in the harness.

**New, and the reason it matters.** Job 1 is a relay. When B rebroadcasts A's warning, a vehicle has to check two
different things:

- **Origin.** A really signed the warning.
- **Authority to relay.** B is allowed to forward it, inside its region, within a time window.

The current message format has one signer. A relay needs either a nested signature (B signs over A's signed
message) or a credential that names B's relay scope. This is the same gap C3 already states for V2V: a fresh message
relayed within the 1 s window to a receiver that never heard it is not detected. RSU-to-RSU relay would make that
gap a designed feature, so it would need its own replay rule (an origin time plus a hop limit).

**Not answered even if built.** The back-haul is in-process, so there would still be no propagation delay, no
lookup cost and no network security on the wired link. Those are C3's main validity limits, and building
RSU-to-RSU messaging in the same harness would not lift them.

## 4. Options
| Option | Work | Adds to the thesis | Cost |
|---|---|---|---|
| **D2-a. Scope out (recommended)** | one paragraph in chapter 6's C3 discussion and in the limitations: RSU-to-RSU is an infrastructure-to-infrastructure hop the layer already authenticates; relay semantics are future work shared with the V2V relay gap | an honest boundary for the examiner's question "where is the infrastructure?" | none |
| D2-b. Minimal build | one message type `hazard_relay` with a nested signature; two RSUs; three registered checks (valid relay accepted, relay outside B's region rejected, forged origin rejected); reported only, no verdict | a fourth link type exercised; the relay rule designed rather than assumed | about one pass, plus a pre-registration amendment, a register row and a chapter paragraph |
| D2-c. Full design | D2-b plus a hop limit, an origin-time replay rule and a corridor of several RSUs in SUMO | a relay study | several passes; needs SUMO (N-4), which decision P2-D4 defers |

## 5. Recommendation
**D2-a, scope out**, stated in chapter 6 and the limitations. Three reasons:

1. A single RSU-to-RSU hop uses a mechanism #45 already verifies, so building it would add a demonstration but no
   new claim.
2. The new part, relay authority, is a protocol design question. It belongs with the V2V relay gap, not with the
   identity layer this thesis measures.
3. Decision D-13 keeps new building to a minimum before the defence, and D2-b would also need a pre-registration
   amendment.

If the examiner's question is expected to press hard, D2-b is the smallest build that answers it with evidence. It
fits in one pass after WM-2 D1.

## 6. What the author decides
Reply "D2-a" or "D2-b". With D2-a, WM-2 D1 adds the paragraph and step D2 closes. With D2-b, a pre-registration
amendment is written and committed before any code.
