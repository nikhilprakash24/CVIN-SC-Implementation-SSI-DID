# CVIN Research Expansion — Ideas Catalogue

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-15
**Status:** OPEN (X1 built and tested; everything else proposed)
**Companion documents:** `WHY.md` (the reasoning behind each idea), `SOURCES.md` (every external claim), `../PLAN_RESEARCH_EXPANSION.md` (the execution plan), `PROMPT_PACK.md` (phased prompts to run in fresh sessions).

---

## 0. How to read this

The thesis so far measures **primitives in isolation**: gas per standard (H1), compliance per check (H2), verify latency per message (H3), portability per backend (H4), a frontier per criterion (H5). That is the right base. What it does not yet show is what happens when the primitives meet in one realistic trip. Integration is where the hard questions are:

- Which revocation wins when the off-chain and on-chain layers disagree?
- What does the roadside learn about a car that is "self-sovereign"?
- Who pays gas for a car that holds no ETH?
- How does a road operator run old and new vehicles through the same gate?

This catalogue proposes three kinds of work:

| Series | What it is | Example |
|---|---|---|
| **X** — composed scenarios | One relatable CAV story that exercises 5–10 primitives end to end, with tests and measurements | X1 toll corridor (built) |
| **P** — primitive upgrades | A code-level improvement to one layer that several X scenarios need | P5 Semaphore-style unlinkable passage |
| **M** — moonshots | Forward-looking work that is hard and may not finish, but defines where the field is going | M1 post-quantum hybrid BSMs |

Every item carries a **tier**:

- **[G] grounded:** buildable now on the existing stack with local tools.
- **[S] stretch:** needs one new dependency or a substantial build.
- **[M] moonshot:** research-grade, partial results still count.

Every item also names the existing code it touches (`file:line` where useful), what to measure, and its sources. Source numbers like `[S12]` point to `SOURCES.md`.

**Primitive legend** used in the "touches" lines:

| Code | Primitive |
|---|---|
| DID | ERC-1056 did:ethr owner/delegate |
| VC | W3C VC issue/verify (`2_w3c-ssi-layer/verifiable-credentials`) |
| SD | Selective disclosure (salted digests) |
| REV | Revocation / status |
| 712 | EIP-712 typed signatures |
| PAY | Token / escrow / permit / channel |
| AA | ERC-4337 account, session keys, paymaster |
| MOBI | MOBI VID I/II birth + lifecycle events |
| PKI | IEEE 1609.2-style PKI baseline (`cv2x-testbed/identity/standard/pki_identity.py`) |
| V2V | SUMO/BSM message path |
| ORA | Oracle |
| ZK | Zero-knowledge proof |
| TR | Trust registry |
| LEG | Legacy-system interaction |

---

## 1. X-series: composed scenarios

### X1 — Endorsed passage, paid write (the toll corridor) [G] — **BUILT**

**Story.** A ministry of transport endorses a vehicle's DID for a tolled corridor at a vehicle class: car, EV, truck, or emergency at fee 0. The DMV, the official sponsoring party, registered the car and paid the gas to put its rotating pseudonym on-chain. At the gantry:

1. **Read.** The roadside unit challenges the car. The car presents a VP that discloses only its class and jurisdiction, not its VIN or plate. The RSU verifies the VP offline, binds the VC to the on-chain endorsement by content hash, and calls `checkTicket`.
2. **Write.** The car's pseudonym key signs an EIP-712 ticket. The gantry batches tickets into one `settleBatch` transaction against a stablecoin escrow that the car funded with an EIP-2612 permit, so the car never needs ETH.

Legacy cars without a wallet go through an ANPR plate lane in the same corridor. The operator reconciles both lanes into one revenue report.

**Touches.** DID, VC, SD, REV (off-chain and on-chain), 712, PAY, LEG, sponsorship (meta-transaction).

**Built.**
- `1_blockchain-identity/contracts/Scenarios/CVINTollCorridor.sol`, `CVINTestStable.sol`
- `test/Scenarios/TollCorridor.test.js`: 20 tests, including 14 attack cells:
  - replay, wrong gantry, self-endorsement, class downgrade
  - stolen endorsement, thief signer, revoked endorsement, rogue revoker
  - expired endorsement or ticket, price cap, empty escrow
  - expired pseudonym, old owner after `changeOwner`
  - digest swap, poisoned batch
- `cv2x-testbed/scenarios/toll_corridor.py`, plus `cv2x-testbed/tests/test_x1_toll_corridor.py` (4 tests)
- Results in `cv2x-testbed/results/x1_toll_corridor.json`

**Measured** (M1 Hardhat; recorded, not yet a register row):

| Quantity | Value |
|---|---|
| `payToll` gas | 110.6k |
| `settleBatch` gas per ticket, batch of 10 | 58.5k |
| `settleBatch` gas per ticket, batch of 25 | 56.2k |
| Gate read, median (VP verify + `eth_call`, over HTTP) | ≈21–23 ms |
| Sponsored `addDelegateSigned` | ≈99k gas per vehicle |

**Findings that matter for the thesis:**

1. **Split-brain revocation is real and must be checked twice.** `suspended-5` (DMV registration revoked off-chain) is stopped at the VP stage. `revoked-6` (corridor endorsement revoked on-chain) passes the VP stage and is stopped only by `checkTicket` code 7. Either layer alone admits one of the two.
2. **Pseudonym rotation does not buy unlinkability here.** The DID address is in every ticket and every `TollPaid` event. This is the motivating gap for P5.
3. **Batching halves the write cost.** 110.6k drops to 56.2k gas per ticket. This feeds the fiat cost model in P14.

### X2 — The rental handoff: driving licence meets the car [G→S]

**Story.**
1. A renter walks up to a car-share vehicle. The car itself is the verifier.
2. The renter presents a **mobile driving licence**. The car checks three predicates: age ≥ 25, licence class ≥ B, and the licence is not suspended. It learns nothing else: no name, no address, no licence number.
3. The car's ERC-4337 account installs a **session key** for the renter. The key is scoped to "unlock, drive, pay corridor tolls ≤ $20/day" and expires at return time.
4. Mid-rental, the licence is suspended: the DMV flips a bit in a **Bitstring Status List**. The car checks status at the next ignition, refuses to start, and logs a MOBI lifecycle event.
5. At return, a damage inspection is recorded as a MOBI VID II event with a multi-party attestation (inspector + renter co-sign). The deposit escrow releases to the renter, or to the owner on damage, under a 2-of-3 rule (owner, renter, insurer).

**Touches.** VC (licence issuance by DMV), SD or ZK (age predicate), REV (status list), AA (session keys), MOBI (`attestEvent`), PAY (escrow), 712.

**Code delta.**
- `DriverLicenceCredential` schema, scenario-local. ISO 18013-5 data elements are mirrored as claims.
- `CVINVehicleAccount.sol` gains `addSessionKey(key, policyHash, validUntil)` and a policy check in `validateUserOp`.
- `RentalEscrow.sol`.
- A scenario script and tests.
- A grounded version first: SD reveals a derived `ageOver25: true` claim the DMV signs (the mDL `age_over_NN` pattern). P11 replaces it with a real mdoc, and P5 or P4 with a ZK predicate.

**Measure.** Time from presentation to unlock; session-key gas against owner-key gas; time from status-list flip to refusal; bytes disclosed against a full-licence disclosure.

**Sources.** S10–S15 (ISO 18013-5/-7, AAMVA, the EUDI ARF, the EU driving-licence directive); S16 (Bitstring Status List); S28 (ERC-4337).

### X3 — The honest used-car sale: oracle-attested VIN, legacy title, atomic swap [G→S]

**Story.**
1. A seller lists a 2019 car. The buyer's app pulls the MOBI birth certificate and lifecycle history from chain (H4 machinery).
2. A **VIN oracle** fetches two things and signs an EIP-712 report: the NHTSA vPIC decode (make/model/year from the VIN) and an NMVTIS title-brand plus last-odometer record. The oracle is m-of-n signers, mocked locally from recorded JSON fixtures.
3. A **consistency engine** compares three sources: the vPIC decode against the birth certificate, NMVTIS odometer against the MOBI odometer history (`detect_odometer_rollback` already exists), and the title brand against the on-chain theft/total-loss events. Mismatches surface as typed warnings, never silent passes.
4. Settlement is **atomic** in one ERC-4337 batched UserOp. The stablecoin moves to the seller, ERC-1056 `changeOwner` moves the DID, and the DMV contract emits a new `RegistrationCredential` hash. Either all happen or none.
5. **Legacy bridge.** The car predates MOBI and has only a paper title. The DMV issues a **bridge credential**: a VC whose issuer DID is `did:web:dmv.example` and whose proof chains to the DMV's existing X.509 certificate (did:x509-shaped). The VC attests "title #T maps to vehicle DID D". The old world vouches the car into the new one.

**Touches.** ORA, MOBI, LEG (NMVTIS, vPIC, paper title), DID transfer, PAY, AA batching, TR, ZK (odometer range proof in the stretch version).

**Code delta.**
- `VINOracle.sol`: quorum EIP-712 reports, report-hash replay set, staleness bound.
- `cv2x-testbed/oracle/` with recorded fixtures, so there is no network in CI, plus an optional live-fetch script for vPIC.
- `SaleSettlement.sol` or a 4337 batch.
- A did:web / did:x509 resolver branch in `did_resolver.py`. The `DIDMethod.WEB` enum value already exists and returns `methodNotSupported`.

**Measure.**
- Fraud-detection matrix: rollback, washed title, cloned VIN, oracle collusion below and at quorum.
- Gas of an atomic sale against the sum of its separate steps.
- Oracle trust surface: how many parties must collude to pass a washed title.

**Sources.** S45–S50 (DECO, Town Crier, TLSNotary, Chainlink, vPIC, NMVTIS); S66–S69 (did:x509, did:web, X.509–DID inheritance).

### X4 — The dual-stack intersection: PKI and SSI in the same radio range [G]

**Story.** A signalised intersection during a ten-year migration. Some cars carry IEEE 1609.2/SCMS-style pseudonym certificates (the existing `pki_identity.py`); others carry DIDs and V2V safety VCs. The RSU runs three policies:

- **Accept-either.** The trust registry lists both the SCMS root and the DID issuers.
- **Shadow mode** (the canary migration). Every PKI-signed BSM is also verified on the SSI path when the car is dual-stack. Disagreements are logged, so the operator gains evidence before switching.
- **Cut-over on date D.** After D, PKI-only BSMs are advisory: displayed, but they cannot trigger emergency braking.

Dual-stack cars sign each BSM twice: an ECDSA certificate signature and an SSI signature. That costs bytes and CPU.

**Touches.** PKI, DID, VC, V2V, TR, LEG.

**Code delta.**
- `DualStackIdentityLayer` in `cv2x-testbed/sumo/sumo_identity_integration.py`, beside `PKIIdentityLayer` (:148) and `SSIIdentityLayer` (:225).
- A sweep over the adoption fraction 0 → 100%. This reuses the PLAN_MOBI_SUMO experiment S5 "mixed fleet".
- A policy enum.
- Trust anchors in a registry, so the PKI root is listed as a did:x509-shaped entry.

**Measure.**
- The **migration curve**: verify ms per BSM, bytes per BSM, and the fraction of safety-relevant messages actionable, each against the adoption fraction.
- Disagreement rate in shadow mode, with injected faults: a revoked PKI certificate whose SSI key is not revoked, and the reverse.

**Why it matters.** Nobody migrates a safety-critical network by flag day. This quantifies the transition the thesis's conclusion implies.

**Sources.** S20–S27 (1609.2, 1609.2.1, ETSI TS 102 941, CCMS, pseudonym surveys, misbehaviour detection); S66–S71 (did:x509, inheritance of trust, ToIP TRQP, the EBSI TIR).

### X5 — Green wave for the ambulance, with accountable anonymity [G→S]

**Story.**
1. A legacy computer-aided dispatch (CAD) system dispatches an ambulance to incident #4471.
2. Dispatch issues a **delegated, 20-minute VC**, "may request signal pre-emption on route R for incident I", to the ambulance's DID. The CAD is legacy; a thin adapter signs on its behalf with an HSM key that is listed in the trust registry.
3. RSUs along the route grant pre-emption. Each grant consumes a **nullifier** derived from (incident, intersection), so a stolen credential cannot buy a city-wide green wave.
4. The vehicle stays pseudonymous to the RSUs. However, the dispatch VC carries an **escrowed identity**: the ambulance ID is encrypted to a 2-of-3 committee (police, health authority, ombudsperson) and opened only on audit.

**Touches.** VC delegation chains (dispatch → vehicle), short-lived credentials, nullifiers, threshold-escrowed identity, LEG (CAD), V2V priority, misbehaviour (SC-01).

**Code delta.**
- Delegated-credential verify: the VC's issuer must itself hold a `DispatchAuthority` VC from the health authority. This is a chain of two.
- A nullifier set in the corridor-style contract, or kept off-chain at the RSU with periodic anchoring (P15).
- Threshold decryption via Shamir secret sharing of an AES key. Python `cryptography` plus a small Shamir implementation is enough for a demo.

**Measure.** Pre-emption decision latency against the J2945/1-style budget the repo already uses (`docs/LATENCY_BUDGET.md`); abuse resistance; audit-open cost.

**Sources.** S27 (misbehaviour detection); S1–S5 (ZK, nullifiers); S70 (trust registries).

### X6 — Sovereign Plug & Charge with a battery passport and a payment channel [S]

**Story.**
1. An EV pulls into a charger. Mutual authentication: the car proves its DID and its **battery passport VC** (chemistry, state of health, carbon footprint, as the EU Battery Regulation requires for EV batteries from 2027). The charger proves its own DID, listed by its charge-point operator in a trust registry.
2. Charging is paid over a **unidirectional payment channel**. The car signs cumulative EIP-712 vouchers every 0.1 kWh, and the charger redeems only the last voucher on-chain.
3. In vehicle-to-grid (V2G) mode the car sells energy back and *issues* a receipt VC. The car becomes an issuer, not only a holder.

Compare against X1: per-event on-chain settlement (gantry) against channel settlement (charger). That gives one curve for "how many events before a channel pays off".

**Touches.** DID, VC (battery passport, with MOBI Battery Birth Certificate alignment), mutual authentication, PAY (channel), 712, TR, car-as-issuer.

**Code delta.** `PaymentChannel.sol` (open / redeem / timeout); a `BatteryPassport` schema; a mutual-auth handshake script; a voucher-rate experiment.

**Measure.** Gas per kWh against the session length; voucher sign/verify ms; and the trust-anchor count, compared with ISO 15118-20 Plug & Charge PKI (multiple roots, cross-certification).

**Sources.** S37–S41 (state channels, MOTIVE, Unterweger EV payments, the IOTA M2M case, ISO 15118-20 PKI); S52–S53 (battery passport, MOBI BBC); S93 (Kailus et al., SSI for EV charging, already cited in repo docs).

### X7 — Recall to over-the-air update, with a chain of custody [S]

**Story.**
1. A regulator issues a `SafetyRecall` VC (the schema exists).
2. The OEM publishes Uptane-style signed update metadata: targets, snapshot and timestamp roles, with the firmware hash anchored on-chain.
3. The vehicle verifies the role signatures and the anchor before installing, then records a MOBI `MODIFICATION` event with the new firmware hash.
4. A type-approval authority asks for UN R156 evidence. The OEM answers with a VP that aggregates the recall VC, the anchored metadata hash, and the vehicle-signed installation events for the affected fleet.

**Touches.** VC, MOBI events, anchoring (Merkle), multi-role signing (TUF/Uptane), compliance evidence as VPs.

**Code delta.** `FirmwareAnchor.sol` (per release: Merkle root of targets + role-key set); a minimal Uptane-shaped metadata verifier in Python; a fleet Merkle proof of installation.

**Measure.** Anchoring gas per release (constant); per-vehicle verify ms; evidence-pack size against fleet size.

**Sources.** S55–S58 (UN R155/R156, ISO/SAE 21434, Uptane).

### X8 — Consent-scoped crash black box [G→S]

**Story.**
1. The event data recorder hashes 1 Hz telemetry into a Merkle tree. The root is anchored once per minute through P15 batch anchoring at the RSU, so it is nearly free.
2. After a crash, the owner consents with a VP to reveal exactly t−30 s to t+5 s to the insurer and the police, with Merkle inclusion proofs per sample.
3. Both vehicles' anchored roots are cross-checked.
4. A **staged crash**, where one party fabricates telemetry after the fact, fails, because its roots were anchored before the incident.
5. An `InsuranceClaim` VC is issued (the schema exists) and recorded as a MOBI event attested by both insurers through `attestEvent`.

**Touches.** Merkle commitments, SD over time ranges, consent VPs, MOBI multi-party attestation, fraud detection.

**Measure.** Anchoring gas per vehicle-hour; proof size per revealed second; fraud-detection matrix.

**Sources.** S60 (EDPB 02/2025: why the raw data stays off-chain).

### X9 — Crossing the border: BC → Washington import [S]

**Story.**
1. The car is registered in British Columbia (did:ethr on chain A).
2. It is imported into Washington State. The CBP import declaration and the WA Department of Licensing registration are issued by issuers from a *different* trust registry.
3. The two registries federate: WA's registry lists BC's DMV as "recognised for title history, not for registration".
4. The car's DID and history move with it. If the jurisdictions run different ledgers, an L1 anchor and an L2 operation are joined by a cross-chain message, mocked as CCIP-shaped.

**Touches.** TR federation, VC from three issuers, MOBI history portability, chain-id-aware DIDs (the resolver already parses chain IDs), cross-chain (moonshot part).

**Code delta.** A federated `TrustRegistry` with scoped recognition; a scenario script. The existing UC "cross-border import" in `test_use_cases.py` is upgraded from a printout to verified credentials.

**Sources.** S70–S71 (TRQP, EBSI TIR); S84–S85 (cross-chain SSI isolation, DID benchmarks).

### X10 — The robotaxi is an economic agent [M-flavoured S]

**Story.** A Level-4 robotaxi has:

1. An **agent identity**: an ERC-8004-shaped registry entry pointing to its DID.
2. A **model-provenance VC**: hash of the driving-policy model, safety-case reference, and AI Act conformity statement, issued by the type-approval authority.
3. An **operator delegation**: the fleet operator's DID delegates "carry passengers in zone Z" with a daily spending cap enforced by its ERC-4337 account policy.

A passenger hails with a VP: payment ability, plus age if alcohol delivery is involved. The robotaxi pays X1 tolls and X6 charging by itself. Every ride produces a reputation entry signed by the passenger, and an AV-only lane admits only vehicles whose model hash is on the authority's current list.

**Touches.** Everything: AA policy, X1, X6, VC, TR, reputation, ORA (model list), LEG (taxi licensing).

**Sources.** S83 (ERC-8004 and its empirical liveness study); S82 (AI agents with DIDs/VCs); S59 (EU AI Act and vehicles); S78–S79 (C2PA, DICE).

### X11 — The parking-enforcement inversion [G]

**Story.** Parking enforcement today photographs plates. Instead:

1. The curb's smart sign broadcasts its policy: "2 h, EV-only, residents exempt", signed by the city's DID.
2. The car proves compliance *to itself*. On request it emits a receipt: a signed `(policyHash, arrive, leave, residentProof?)` tuple. The resident proof is SD of the `RegistrationCredential` address zone, never the address itself.
3. An enforcement officer checks the receipt with a phone.

No plate database is ever built, because the car carries its own evidence.

**Touches.** VC (city policy as a credential), SD, 712 receipts, LEG (citation back office).

**Measure.** Identifiers collected per enforcement check: plate-photo lane against the receipt lane. This is the X1 exposure metric applied to a second domain.

### X12 — "Proof of not-stolen" at the parts yard [G]

**Story.** A parts yard buys a catalytic converter. The part carries a MOBI-anchored part DID. The seller proves three things:

- the donor vehicle had a `DECOMMISSION` event from a licensed facility;
- the part's serial is in the donor's birth attributes;
- the donor has no open `THEFT_REPORT`.

Each is a query against existing MOBI V2 events (`get_events_by_type`).

**Touches.** MOBI events, per-part DIDs (the identity hierarchy from SC-18), VC.

**Why.** It is cheap to build on what exists and speaks directly to a real crime trend. A good demo chapter vignette.

---

## 2. P-series: primitive upgrades (what the X scenarios need)

| ID | Upgrade | Tier | Needed by | Touches existing code | Measure |
|---|---|---|---|---|---|
| P1 | **EIP-712 everywhere.** Move CVIN-Combined's raw digest (`CVINCombinedIdentity.sol:390-412`), ERC-735 claims and MOBI `attestEvent` to domain-separated typed data. Keep the old functions for parity rows. | G | X1–X10 | 3 contracts, tests, security harness | Gas delta; a new attack cell "cross-contract signature replay" |
| P2 | **Bitstring Status List** in place of `CvinRevocationRegistry2024`: a gzip+base64 bitstring credential, with its hash optionally anchored on-chain | G | X1, X2, X5 | `vc_issuer.py:105-174`, `vc_verifier.py` revocation stage | Verify ms and bytes at 131,072 entries; herd-privacy set size; compliance-checker delta |
| P3 | **SD-JWT VC (RFC 9901)** issuer/verifier with key binding, beside Data Integrity | G | X2, X11 | new `sd_jwt.py` | Size and latency against DI-SD; interop note |
| P4 | **BBS (`bbs-2023`)** unlinkable selective disclosure | S | X1, X2, X11 | new cryptosuite module (evaluate libraries first) | Proof size against hidden-message count; verify ms on the BSM path |
| P5 | **Unlinkable passage.** Semaphore-style group membership + nullifier per (corridor, epoch), Groth16 verifier on-chain. This closes the X1 linkability gap. | S | X1, X5, X11 | `CVINTollCorridor` v2; circom/snarkjs toolchain | Verifier gas; proof gen ms on a laptop and on a Raspberry-Pi-class ECU; anonymity-set size |
| P6 | **On-chain DID resolution** in `DIDResolver._resolve_ethr`. It currently synthesises documents (`did_resolver.py:438`). Already on the HANDBACK next-session list. | G | all | `did_resolver.py`, `erc1056_provider.py` | Resolution ms against history h (cf. #39) |
| P7 | **Trust-registry contract** (TRQP-shaped `isAuthorized(entity, action, resource, framework)`), replacing ad-hoc `trustedIssuer` maps | G | X1, X3, X4, X5, X9 | Corridor, MOBI V2 `authorizeIssuer` | Gas per query; federation semantics |
| P8 | **ERC-4337 hardening.** Guardian threshold + timelock recovery (closes the instant single-guardian caveat at `scripts/security_scenarios.js:619`), session keys, a sponsoring paymaster, an EIP-7702 variant | G→S | X2, X3, X10 | `CVINVehicleAccount.sol`, `CVINMinimalEntryPoint.sol` | Recovery attack cells; paymaster overhead in gas |
| P9 | **VIN oracle**: quorum EIP-712 reports, recorded fixtures, optional live vPIC | G | X3 | new | Fraud matrix; collusion threshold |
| P10 | **OpenID4VCI / OpenID4VP** endpoints (stdlib HTTP) around the existing issuer and verifier | S | X2, X3 | new `oid4vc/` | Protocol round trips; HAIP profile gaps |
| P11 | **ISO 18013-5 mdoc** (CBOR/COSE MSO) issuance and verification | S | X2 | new `mdoc/` | mdoc against VC verify ms at a roadside licence check |
| P12 | **Formal and fuzz assurance** (chapter 7 future-work item 4): SMTChecker or Halmos invariants plus Echidna/Foundry fuzzing for the corridor escrow and 4337 recovery | S | all | contracts | Invariants proven; fuzz counterexamples |
| P13 | **Legacy bridge**: `did:web` + `did:x509` resolution, an X.509 → VC bridge-credential issuer, dual-proof BSMs | G→S | X3, X4, X5 | `did_resolver.py` (WEB enum exists), `pki_identity.py` | Bridge trust-path length; bytes per BSM |
| P14 | **Fiat cost model**: gas → USD on L1 and on three L2s from recorded fee snapshots (chapter 6 §6.6.3 future work). Turns H1 and X1 gas into dollars per vehicle per year. | G | all | `4_comparison-framework/` | USD per lifecycle and per toll; sensitivity to gas price |
| P15 | **Merkle batch anchoring at the RSU**: aggregate N verifications or attestations into one root per minute | G | X5, X7, X8 | new `AnchorLog.sol` | Gas per anchored item against N; proof size |

---

## 3. M-series: moonshots

**M1 — Post-quantum hybrid BSMs. [M]**
- Sign each BSM with ECDSA plus ML-DSA-44, using a PQ library such as `liboqs-python`.
- Measure bytes against the ~1,400-byte V2V payload budget, and verify ms against the 100 ms budget, on the existing SUMO path.
- Store the PQ key as an ERC-1056 attribute, so crypto-agility is a DID-document change, not a fleet recall.
- Sources: S74–S77.

**M2 — Verifiable autonomy. [M]**
- An AV may enter an AV-only lane only if it can prove two things: its ECU booted a measured image (DICE/TPM attestation chain), and the loaded driving-policy model hash is on the authority's certified list (C2PA-style manifest as a VC).
- Stretch goal: a zkML proof that a tiny perception model produced a given output.
- Sources: S78–S81.

**M3 — Intersection as a market. [M]**
- Auction-based autonomous intersection management with commit-reveal sealed bids, settled through X1 escrow.
- Emergency vehicles bid via endorsement (X5) rather than money.
- Study fairness: do poor commuters always wait? Test a "Vickrey with a per-day credit" design.
- Sources: S86–S88.

**M4 — Privacy-preserving usage-based insurance. [M]**
- The car proves "I drove < 8,000 km and never exceeded the limit by > 20 km/h" from signed telemetry (X8 anchors) in ZK. The insurer prices on the proof, not on the data.
- The literature sweep found no peer-reviewed ZK-telematics UBI paper. This is a genuine gap: SIDE_PAPERS candidate SP-9.
- Source: S89 (SOA ZKP report), which documents the gap.

**M5 — Threshold platoons. [M]**
- A truck platoon is itself a DID controlled by a FROST threshold key. Members join and leave by resharing.
- The platoon pays one toll for the convoy (X1 with a group signer) and signs platoon-control messages as a group.

**M6 — Privacy-preserving enforcement: "prove you obeyed". [M]**
- Road rules (speed zones, school zones, low-emission zones) are published as signed policy credentials.
- The car proves compliance in ZK over its own anchored telemetry, instead of being surveilled by cameras.
- This inverts the enforcement model; X11 is the grounded first step.

**M7 — Self-paying car. [M]**
- The car's ERC-4337 account runs a budget policy: tolls, parking, charging, per-km insurance, and micro-earnings from data sales and V2G.
- It negotiates with service agents (ERC-8004-style) under owner-set constraints.
- X10 is the integration test.

**M8 — DePIN telemetry with compute-to-data. [M]**
- Owners sell aggregate traffic data. Raw data never leaves the car, or leaves only FHE-encrypted, and buyers pay per query.
- Comparator: the DIMO vehicle-ID NFT model against this repo's ERC-721.
- Sources: S90–S92.

**M9 — Fifteen-year identity. [M]**
- Vehicles outlive cryptosystems.
- Design and test a key-rotation ceremony that moves a vehicle DID from secp256k1 to a hybrid PQ key without losing MOBI history or ownership chain.
- Measure what breaks.

**M10 — Revocation at radio speed. [S→M]**
- RSUs broadcast a compressed revocation cascade (a CRLite-style Bloom-filter cascade) every second.
- Compare against freshness-k (#32, #37), and against the gate's double check in X1.

---

## 4. Cross-cutting research instruments (methodology contributions)

1. **The scenario triple.** Every X scenario reports *(gas, latency, exposure)*, where exposure is the list of identifiers the counterparty learned, plus whether they are linkable across sites. X1 already emits it. This becomes a reusable metric next to the DID rubric.
2. **The migration curve.** For X1 (legacy lane), X4 (dual-stack) and X3 (bridge credential): cost, privacy and safety as functions of the adoption fraction. This quantifies transition, not just endpoints.
3. **Split-brain revocation analysis.** For each composition, enumerate where revocation state lives (off-chain registry, on-chain bit, status list, freshness cache) and test every disagreement combination. X1 found that the double check is necessary. Generalise it into a table.
4. **Composite attack cells.** Extend `test/security/attackHarness.js` beyond its fixed six attack keys with cross-layer attacks:
   - VC valid but on-chain revoked;
   - endorsement for DID A presented by DID B;
   - sponsor front-running a permit;
   - oracle quorum minus one.
5. **Fiat-denominated results (P14)** so that a policymaker can read the thesis.

---

## 5. Priority shortlist (what would most strengthen the thesis per hour)

1. X1 polish and register rows. Done in code; needs author sign-off on register #40/#41.
2. P6 on-chain resolution, P1 EIP-712 and P2 status list. Small, and they raise rigor across the board.
3. X4 dual-stack migration curve. Reuses SUMO; the highest-impact transition evidence.
4. X3 oracle + legacy bridge. The "old system meets new" story the conclusion needs.
5. P5 unlinkable passage. Closes the X1 finding with a ZK result; a strong side paper.
6. X2 rental handoff (licence + session keys). The most relatable demo.
7. P14 fiat cost model.

Everything else is ordered in `../PLAN_RESEARCH_EXPANSION.md`.
