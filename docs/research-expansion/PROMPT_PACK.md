# Prompt Pack — Research Expansion, Phase by Phase

**Date:** 2026-10-15
**What this is:** The execution plan (`docs/PLAN_RESEARCH_EXPANSION.md`) rewritten as self-contained prompts. Paste one prompt into a fresh Claude Code session opened on this repository. Each prompt carries everything the session needs: context, rules, deliverables and a definition of done.

**How to use it**

1. Run the prompts **in order within a phase**. Phases 1–6 can be reordered once Phase 0 is done; check the dependency graph in the plan (§5).
2. Paste the **common preamble** (§0) first, then exactly one work-package prompt.
3. Give each session its own branch, e.g. `xp/p0-3-onchain-resolver`. Merge to the integration branch after review.
4. When a session finishes, append a row to the plan's progress log (§8). The prompts tell the session to do this.
5. If a prompt says "pre-register", do that commit *before* building anything else.

---

## §0 — Common preamble (paste before every prompt)

```text
You are working in the CVIN-SC-Implementation-SSI-DID repository (MASc thesis, UBC ECE:
comparative analysis of blockchain SSI identity standards for connected and autonomous
vehicles). Read these first, in order: README.md, docs/HANDBACK_2026-10-04.md,
docs/PLAN_RESEARCH_EXPANSION.md, docs/research-expansion/IDEAS.md (the section for your
work package), docs/research-expansion/WHY.md (the matching paragraph).

Standing rules (non-negotiable; they come from the author):
- Commits are authored "Nikhil Prakash <nikhil.prakash1995@gmail.com>" with NO AI
  co-author trailers. Commit and push at each meaningful step.
- Never skip, weaken or delete an existing test. CI fails on any Python skip.
- Do not change existing measured numbers, register rows or chapter claims. New numbers
  go into docs as "proposed register #N" until the author approves. Fetch first and
  check docs/MEASUREMENT_CONDITIONS.md for the next free row number.
- Every new feature ships with negative tests (attacks that must fail), with pass/fail
  computed, never hardcoded or printed.
- No live network calls in tests. Use recorded fixtures, clearly labelled synthetic.
- Never fabricate citations. Cite only from docs/research-expansion/SOURCES.md, or a
  source you actually opened, and add new ones there with their URL.
- Style for docs: short sentences, tables, no emojis, claim -> evidence -> interpretation,
  caveats stated in the body.
- Author decisions (framing, hypotheses, scope) are LISTED for the author, not taken.

Environment setup:
  (cd 1_blockchain-identity && npm ci && npx hardhat compile)
  pip install eth-account coincurve cryptography web3 pytest numpy
  (cd 1_blockchain-identity && npx hardhat node --port 8548 &)   # for on-chain Python tests
  mkdir -p /tmp/cv2x-art && ln -sfn "$PWD/1_blockchain-identity/artifacts/contracts/MOBI" /tmp/cv2x-art/contracts
Baseline to keep green (as of 2026-10-15): `npx hardhat test` = 389 passing / 23 pending;
`CV2X_TEST_RPC_URL=http://127.0.0.1:8548 CV2X_TEST_ARTIFACTS_DIR=/tmp/cv2x-art python -m pytest
2_w3c-ssi-layer cv2x-testbed/tests -q` = 362 passed;
`python cv2x-testbed/scripts/w3c_compliance_checker.py` = 94.3%.

Reference implementation to imitate: scenario X1 (toll corridor):
  1_blockchain-identity/contracts/Scenarios/CVINTollCorridor.sol
  1_blockchain-identity/test/Scenarios/TollCorridor.test.js
  cv2x-testbed/scenarios/toll_corridor.py, cv2x-testbed/tests/test_x1_toll_corridor.py

Finish by: re-running all three baselines and reporting the new counts; appending a row to
the progress log in docs/PLAN_RESEARCH_EXPANSION.md §8; writing a short results note
under docs/research-expansion/results/<WP>.md (what was built, numbers with their
condition, findings, caveats, author decisions needed); then commit and push.
```

---

## Phase 0 — Foundation

### P0.2 — X1 register rows

```text
Work package 0.2: register rows for scenario X1.
1. Re-run X1 on a clean tree: `npx hardhat test test/Scenarios/TollCorridor.test.js` (capture
   the settleBatch gas line) and `python cv2x-testbed/scenarios/toll_corridor.py --rpc ...`.
   Run the Python scenario 30 times and report the median and 95% CI of read_ms_median,
   using the bootstrap the repo already uses in 4_comparison-framework (find it).
2. Draft rows #40 (X1 gas: payToll; settleBatch at 1, 10, 25 per ticket; tag M1) and #41
   (X1 gate read: VP verify + eth_call over HTTP; tag M1-H/HTTP; single host). Explain the
   ~12-gas run-to-run variance: fresh keys change calldata zero bytes. Show it by running
   with fixed keys, where gas becomes deterministic.
3. Do NOT add the rows yourself. Write them in docs/research-expansion/results/P0.2.md as
   "proposed", in the exact register column format, for the author to paste.
```

### P0.3 — On-chain DID resolution (P6)

```text
Work package 0.3 (P6): make DIDResolver._resolve_ethr (2_w3c-ssi-layer/did-resolution/
did_resolver.py ~line 438) read the chain when a blockchain_provider is given. Today it
synthesises a document. Implement ERC-1056 log walking (DIDOwnerChanged,
DIDDelegateChanged, DIDAttributeChanged via the `changed[]` linked list), following the
DIF ethr-did-resolver method spec. The logic in cv2x-testbed/identity/erc1056_provider.py
resolve_identity_from_address can guide you, but the resolver must stay self-contained.
Keep offline behaviour byte-identical when no provider is passed: existing tests and the
W3C DID test-suite run must not change.
Tests:
- owner change reflected;
- delegate add/expiry reflected (veriKey -> verificationMethod; sigAuth -> authentication);
- attribute-published service endpoint;
- deactivated identity (owner = 0x0) yields deactivated metadata;
- resolution time against history length h, compared with register #39 (report as proposed).
Re-run the compliance checker and the DID suite (docs/conformance) and record any delta.
```

### P0.4 — EIP-712 everywhere (P1)

```text
Work package 0.4 (P1): add EIP-712 typed-data variants, keeping the old functions for
parity rows:
  - CVINCombinedIdentity.addClaim (raw digest today, CVINCombinedIdentity.sol:390-412)
  - CVINVehicleClaimHolder.addClaim (EIP-191 personal-sign today)
  - MOBIVIDRegistryV2.attestEvent (EIP-191 today)
Use OpenZeppelin 5.0.2 EIP712 + ECDSA, as in contracts/Scenarios/CVINTollCorridor.sol.
Add a security-harness attack "crossContractReplay": a signature produced for contract A
replayed at contract B (same ABI, different address) and, separately, on another chainId.
The harness ATTACKS list is fixed (test/security/attackHarness.js:43-50); extend it
deliberately and update the matrix writer and its consumers in
4_comparison-framework/security-analysis. Expected: the new paths are DEFENDED; any old
path that is VULNERABLE is reported as such, never hidden.
Deliver a gas delta table (old vs typed) as a proposed register row.
```

### P0.5 — Bitstring Status List (P2)

```text
Work package 0.5 (P2): implement W3C Bitstring Status List v1.0
(https://www.w3.org/TR/vc-bitstring-status-list/) beside the existing
CvinRevocationRegistry2024 (2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py:105-174).
- Issuer: allocate indices, publish a BitstringStatusListCredential (gzip + multibase
  base64url), support statusPurpose revocation and suspension.
- Verifier: fetch from an in-memory resolver map (no network), decompress, check the bit,
  and fail closed exactly as the current registry does.
- Optional: anchor the status-list credential hash in a tiny contract and verify it.
Measure: verify ms and list size at 16,384 / 131,072 / 1,048,576 entries; herd size.
Keep all existing tests green; add structure and negative tests. Re-run the compliance
checker and report any delta. Do not edit the checker to raise the score.
```

### P0.6 — Trust-registry contract (P7)

```text
Work package 0.6 (P7): build TrustRegistry.sol, shaped after the ToIP Trust Registry
Query Protocol v2.0 (SOURCES S70) and the EBSI TIR (S71):
isAuthorized(entity, action bytes32, resource bytes32, framework bytes32) -> bool, plus
scoped recognition of another registry ("recognise registry R for action A only").
Wire CVINTollCorridor to read issuer trust from it, via a new CVINTollCorridorTR or an
optional constructor argument, without changing X1 behaviour or its tests.
Tests: grant, revoke, expiry, scoped federation (recognised for title history, NOT for
registration), and a non-governor cannot write. Report gas per query.
```

---

## Phase 1 — Transition and legacy

### P1.1 — X4 dual-stack intersection

```text
Work package 1.1 (X4). PRE-REGISTER FIRST: commit H7 to docs/research-expansion/results/P1.1.md
before building: "shadow-mode dual stack detects 100% of injected revocation
disagreements at < 2x the per-message verification cost of the single SSI path". Use the
author-approved wording if one exists in docs/PLAN_RESEARCH_EXPANSION.md §6 AD-2.
Build DualStackIdentityLayer in cv2x-testbed/sumo/sumo_identity_integration.py, beside
PKIIdentityLayer (:148) and SSIIdentityLayer (:225). A dual-stack vehicle signs each BSM
twice. Receiver policies: ACCEPT_EITHER, SHADOW (verify both, log disagreements, act on
PKI), CUTOVER (after date D, PKI-only BSMs are advisory and cannot trigger EEBL/FCW).
Sweep the adoption fraction 0..100% in steps of 10, N=30 seeds each, in --simulate mode.
Inject faults: PKI certificate revoked but SSI key live, and the reverse. Report verify
ms per BSM, bytes per BSM, % safety messages actionable, and the disagreement detection
rate. Produce a migration-curve figure (matplotlib, PNG + CSV + JSON). Report the H7
verdict as observed.
```

### P1.2 — Legacy bridge: did:web / did:x509 (P13)

```text
Work package 1.2 (P13): add did:web resolution (DIDMethod.WEB exists but returns
methodNotSupported) using an in-memory "web" map, so there is no network. Add a
did:x509-shaped method following draft-birkholz-did-x509-03 (S66), bound to the CA
fingerprint of the existing VehiclePKI_CA (cv2x-testbed/identity/standard/pki_identity.py:284).
Build a bridge-credential issuer: the legacy CA (X.509) vouches "certificate serial S <->
vehicle DID D" as a VC verifiable through the did:x509 chain. State in the docs that
IEEE 1609.2 certificates are not X.509, so a production version needs an adaptation.
Tests: valid bridge; revoked certificate (CRL) invalidates the bridge; wrong CA
fingerprint; leaf predicate mismatch.
```

### P1.3 — VIN oracle (P9)

```text
Work package 1.3 (P9): build VINOracle.sol: m-of-n EIP-712 signed reports
{vinHash, decodedMakeModelYearHash, titleBrand, lastOdometer, observedAt, sourceId},
with a replay set on report hashes and a staleness bound. Off-chain: cv2x-testbed/oracle/
with SYNTHETIC recorded fixtures shaped like the NHTSA vPIC DecodeVinValues response
(S49) and NMVTIS fields (S50), labelled synthetic in the file headers. Add an optional
script live_vpic_fetch.py that is never imported by tests. Tests: quorum met; quorum-1;
a duplicate signer counted once; stale report; replayed report; non-oracle signer.
Produce a collusion matrix.
```

### P1.4 — X3 honest used-car sale

```text
Work package 1.4 (X3), depends on 1.3: compose the MOBI history (2_w3c-ssi-layer/mobi-vid),
the VIN oracle, and an atomic settlement: stablecoin -> seller; ERC-1056 changeOwner;
DMV RegistrationCredential hash emitted. Use either a SaleSettlement contract the parties
pre-authorise with EIP-712, or one ERC-4337 batched UserOp. Explain the choice.
Consistency engine: vPIC decode vs birth certificate; NMVTIS odometer vs MOBI odometer
history (reuse detect_odometer_rollback); title brand vs on-chain THEFT_REPORT /
DECOMMISSION. Legacy path: a pre-MOBI car with a paper title gets a DMV bridge credential
(from P1.2) and enters the same flow. Fraud matrix: rollback, washed title, cloned VIN,
oracle quorum-1, buyer underpays, partial-failure atomicity. Report gas of the atomic
sale vs the sum of its separate steps.
```

---

## Phase 2 — Privacy

### P2.0 + P2.1 — Unlinkable passage (P5)

```text
Work package 2.1 (P5): close the X1 linkability finding (every TollPaid event names the DID).
PRE-REGISTER FIRST (commit before code): H8 "an unlinkable toll settles at <= 10x X1
payToll gas (<= 1,106,000) and proves in <= 2 s on a laptop", unless the author set
other thresholds in the plan's AD-2.
Design: the ministry inserts each endorsed vehicle's identity commitment into a per-class
Merkle group (Semaphore v4 [S4] or a minimal circom circuit + snarkjs Groth16 [S5]). At
the gantry the vehicle proves membership in class C's group, plus a nullifier =
H(secret, corridorId, epoch), with the ticket hash as the external signal. Escrow cannot
be per-DID without linking trips, so use per-epoch prepaid anonymous credit: a deposit
buys k toll units bound to commitments. Analyse the anonymity set honestly: per class,
per epoch, deposit timing.
Toolchain: keep circom/snarkjs out of the default CI path. Commit the verifier contract,
the zkey hash and test proofs, so CI verifies committed proofs without proving.
Tests: valid proof settles; nullifier reuse blocked; proof for class EV used to pay as
class CAR fails; a stale Merkle root fails; and no on-chain field equal across two trips
of the same vehicle (an assert over the events).
Report verifier gas, proof size, proving time (laptop; and ARM if available), and the
H8 verdict as observed.
```

### P2.2 — SD-JWT VC (P3)

```text
Work package 2.2 (P3): implement RFC 9901 SD-JWT (S3) with key binding (SD-JWT+KB), ES256K
over the existing secp256k1 keys, in 2_w3c-ssi-layer/verifiable-credentials/sd_jwt.py.
Issue the X1 corridor endorsement as an SD-JWT VC as well, and verify it at the gate.
Compare against the Data Integrity SD path: bytes on the wire, issue/verify ms, number
of disclosures. Negative tests: tampered disclosure, missing KB, wrong audience or nonce,
expired token, disclosure for an undeclared claim.
```

### P2.3 — BBS feasibility (P4)

```text
Work package 2.3 (P4): timeboxed (one session). Survey maintained BBS implementations that
are usable from Python, natively or via WASM/Node, against draft-irtf-cfrg-bbs-signatures
(S2) and W3C vc-di-bbs (S1). If one is usable, issue a VehicleBirthCertificate with
bbs-2023, derive two unlinkable proofs disclosing {make, year}, and show the proofs share
no common bytes. Measure proof size against hidden-message count and verify time. If
none is usable, write the negative result with evidence (versions, errors, spec gaps).
That is a valid outcome.
```

### P2.4 — X11 parking-enforcement inversion

```text
Work package 2.4 (X11): the city signs a CurbPolicy VC ("2h, EV-only, residents exempt,
zone Z"). The vehicle produces EIP-712 receipts (policyHash, arrive, leave, residentProof)
where residentProof is a selective disclosure of the RegistrationCredential's zone, never
the address. An officer verifies a receipt from a phone script. Compare the "exposure"
(identifiers collected per check) against a plate-photo lane, using the same exposure
format as X1. Negative tests: an expired policy, a receipt for another car, an
overstayed window, a forged zone.
```

---

## Phase 3 — Human credentials and accounts

### P3.1 — ERC-4337 hardening (P8)

```text
Work package 3.1 (P8): in 1_blockchain-identity/contracts/ERC4337/CVINVehicleAccount.sol:
replace instant single-guardian recovery (recoverOwner :228; caveat noted at
scripts/security_scenarios.js:619) with an m-of-n guardian proposal + timelock + owner
veto. Add session keys (addSessionKey(key, policy{targets, selectors, spendCap,
validUntil})) checked in validateUserOp. Add a minimal sponsoring paymaster to
CVINMinimalEntryPoint, labelled a representative implementation like the existing one.
Keep the existing benchmark contract and its numbers untouched: build the hardened
version as a new contract and compare gas. Attack cells: guardian-minority takeover,
recovery during timelock vetoed, session key outside policy, expired session key,
paymaster drain attempt.
```

### P3.2 — X2 rental handoff

```text
Work package 3.2 (X2), depends on 0.5 and 3.1: the DMV issues a DriverLicenceCredential
(claims mirroring ISO 18013-5 data elements, S10, including age_over_25 and driving
privileges by category). The car acts as verifier: it requires age_over_25 and category
B, and learns nothing else (selective disclosure). On success the car's 4337 account
installs a renter session key (unlock, drive, tolls <= $20/day, until return time). Mid-
rental the DMV suspends the licence via the Bitstring Status List (statusPurpose
suspension). At the next ignition check the car refuses and records a MOBI lifecycle
event. At return: an inspector + renter co-attest a damage event (attestEvent), and a 2-of-3
escrow (owner, renter, insurer) releases the deposit. Reuse X1 to pay a toll with the
session key. Measure: presentation -> unlock ms; flip -> refusal (as a function of check
cadence); disclosed bytes vs the full licence.
```

### P3.3 — ISO 18013-5 mdoc (P11)

```text
Work package 3.3 (P11): issue and verify an ISO 18013-5-shaped mdoc: CBOR IssuerSigned
items, a COSE_Sign1 Mobile Security Object with digests, and device authentication over
a simulated session transcript. Use the cbor2 + pycose (or equivalent) libraries, pinned.
Simulate a roadside licence check: the officer's reader requests {portrait omitted,
age_over_18, driving_privileges}. Compare against the VC path from X2: bytes, verify ms,
number of round trips. State clearly what is simulated (no BLE/NFC engagement) and cite
S10/S11 for structure.
```

### P3.4 — OpenID4VC (P10)

```text
Work package 3.4 (P10): wrap the existing issuer and verifier in minimal OpenID4VCI
(pre-authorized code flow) and OpenID4VP (presentation_definition / DCQL, direct_post)
endpoints, using Python's stdlib http.server on localhost, with no external services.
Run the X1 endorsement issuance and the X2 licence presentation through them. Report
round trips and latency, and list which HAIP 1.0 requirements (S18) are met or unmet.
Never claim conformance; claim "exercised".
```

---

## Phase 4 — Economics

### P4.1 — Fiat cost model (P14)

```text
Work package 4.1 (P14): build 4_comparison-framework/cost-model/: convert every V-status
gas row (H1 create, the lifecycle rows #30/#35, X1 rows once approved) to USD on Ethereum
L1 and three L2s. Use dated fee snapshots that you record into a JSON file with source
URLs and retrieval timestamps. If the network is unavailable, use explicitly labelled
historical values and say so. Compute per-vehicle-per-year cost for: one lifecycle, 2
ownership transfers, 4 services, and 500 toll passages (single vs batch 25). Sensitivity
over gas price (p10/p50/p90) and ETH price. Output CSV/JSON/LaTeX like the other
generators. This closes chapter 6 §6.6.3 future work.
```

### P4.2 — Merkle anchoring (P15)

```text
Work package 4.2 (P15): AnchorLog.sol stores one Merkle root per (anchorer, minute).
A Python helper builds trees (keccak, sorted pairs, OZ MerkleProof-compatible) and
proofs. The RSU anchors N verification records per minute. Measure gas per anchored item
for N = 1, 10, 100, 1000, and proof size. Tests: a valid inclusion; a wrong leaf; a root
from another minute; a non-authorised anchorer.
```

### P4.3 — X6 sovereign Plug & Charge

```text
Work package 4.3 (X6): mutual authentication. The EV presents its DID + a BatteryPassport
VC (fields inspired by EU 2023/1542 [S52] and the MOBI Battery Birth Certificate [S53];
scenario-local schema). The charger presents its DID, listed by its charge-point
operator in the TrustRegistry (P7). Payment: a unidirectional PaymentChannel.sol (open
with a permit, EIP-712 cumulative vouchers every 0.1 kWh, close with the last voucher,
timeout refund). V2G mode: the car issues a receipt VC. Break-even analysis: on-chain gas
per kWh vs session length, against X1-style per-event settlement. Negative tests: an
old voucher, a voucher over the deposit, a charger closing with a non-latest voucher,
timeout griefing.
```

### P4.4 — X8 consent-scoped black box

```text
Work package 4.4 (X8), depends on 4.2: simulate 1 Hz EDR telemetry for two vehicles;
anchor a per-minute root via AnchorLog. After a synthetic crash, the owner issues a
consent VP revealing samples t-30..t+5 with inclusion proofs to an insurer verifier.
Staged-crash test: a party fabricates post-hoc telemetry; detection must come from the
anchored roots. Issue an InsuranceClaim VC (existing schema) and record it as a MOBI event
attested by both insurers. Report proof bytes per revealed second and anchoring gas per
vehicle-hour.
```

---

## Phase 5 — Safety and regulation

### P5.1 — X7 recall → OTA chain of custody

```text
Work package 5.1 (X7): a regulator issues a SafetyRecall VC (existing schema). The OEM
publishes Uptane-shaped metadata (S58), with root/targets/snapshot/timestamp roles in
Python, and anchors the targets hash on-chain (FirmwareAnchor.sol). The vehicle verifies
the role signatures and the anchor before "installing", then records a MOBI
MODIFICATION event with the firmware hash. Build an R156 evidence VP for a 1,000-vehicle
fleet using a Merkle root of installation events (reuse P15). Report evidence-pack size
against fleet size. Negative tests: a rollback attack, a mix-and-match of metadata,
a key compromised below threshold, an unanchored image.
```

### P5.2 — X5 ambulance green wave

```text
Work package 5.2 (X5): a delegation chain. The health authority issues a DispatchAuthority
VC to the dispatch centre (a legacy CAD adapter with an HSM-like key); dispatch issues a
20-minute PreemptionGrant VC for (incident, route) to the ambulance DID. The RSU verifies
the chain, consumes a nullifier H(incident, intersection), and grants pre-emption. The
grant carries the ambulance ID encrypted to a 2-of-3 committee (Shamir-shared AES key).
Tests: an expired grant; an off-route intersection; nullifier reuse; dispatch without
authority; a single committee member cannot open; two can. Report the decision latency
against the docs/LATENCY_BUDGET.md budget.
```

### P5.3 — Formal and fuzz assurance (P12)

```text
Work package 5.3 (P12): for CVINTollCorridor and the hardened 4337 account (P3.1): state
invariants (escrow conservation: sum(escrowOf) + treasury == token.balanceOf(corridor)
under deposit/withdraw/settle; nonce single-use; recovery cannot complete before the
timelock). Check them with Echidna or Foundry invariant fuzzing (add Foundry in a
separate folder; do not disturb Hardhat), and optionally Halmos or SMTChecker. Report
the invariants proven or fuzzed, the run counts, and any counterexample, with a fix plus
a regression test. Closes chapter 7 future-work item 4 for these contracts.
```

---

## Phase 6 — Moonshots (timeboxed: one session each)

### P6.1 — M1 post-quantum hybrid BSMs

```text
Work package 6.1 (M1): add ML-DSA-44 (FIPS 204, S74) signing to the SSI BSM path in
cv2x-testbed/sumo/sumo_identity_integration.py via liboqs-python or another maintained
binding (pinned). Mode HYBRID: ECDSA + ML-DSA over the same payload. Measure bytes per
BSM, sign/verify ms (N=30 seeds, the repo's CI method), and whether a BSM fits the
payload budget used in the literature (S75/S76; cite the primary number you verify).
Publish the PQ public key as an ERC-1056 attribute and resolve it (P6). If no binding
installs, report the negative result with evidence.
```

### P6.2 — M4 zero-knowledge usage-based insurance

```text
Work package 6.2 (M4), depends on 4.4 and 2.1's toolchain: prove "total distance this
month < D and no 1 Hz sample exceeded the speed limit by > 20 km/h" over telemetry
committed in X8 anchors, without revealing samples. Start tiny (e.g. 600 samples) and
report how proving time scales. Write a side-paper outline (proposed SP-9) noting the
literature gap recorded in SOURCES S89. Be explicit about the trust in the telemetry
source (signed by an ECU key; M2 would attest it).
```

### P6.3 — M9 fifteen-year identity

```text
Work package 6.3 (M9): script a key-rotation ceremony for a vehicle DID: secp256k1 owner ->
new secp256k1 owner + a published ML-DSA key (attribute), then simulate "ECDSA
deprecated" and verify the history using only the post-rotation keys. Check that the MOBI
birth certificate, lifecycle events and ownership chain remain verifiable. List exactly
what breaks (e.g. EIP-191 proofs on old VCs) and propose mitigations (re-anchoring,
countersigning). Output: a results note plus tests for what works.
```

### P6.4 — X10 robotaxi as an economic agent

```text
Work package 6.4 (X10): an ERC-8004-shaped agent registry entry (S83) pointing to the
robotaxi DID; a ModelProvenance VC (model hash, safety-case URI, AI Act conformity
statement placeholder) from the type-approval authority; the operator's delegation with
a daily spending policy (P3.1 session keys). Compose: hail (passenger VP) -> ride -> X1
toll -> X6 charge -> passenger-signed reputation entry. An AV-only lane admits only
vehicles whose model hash is on the authority's current list (TrustRegistry P7). Tests:
a revoked model hash, a spend over the cap, a reputation entry from a non-passenger.
```

### P6.5 — Remaining moonshot notes

```text
Work package 6.5: write one-page future-work notes for M2 (verifiable autonomy: DICE/TPM
+ C2PA-style model manifest), M3 (intersection auctions), M5 (FROST threshold platoons),
M6 (prove-you-obeyed enforcement), M7 (self-paying car), M8 (DePIN compute-to-data) and
M10 (revocation cascades vs freshness-k). Each note: problem, sketch on this repo's
primitives, the first experiment, the main obstacle with a source from SOURCES.md, and
what result would justify continuing. Put them in docs/research-expansion/moonshots/.
```

---

## Phase 7 — Thesis integration

### P7.1 — Chapters and side papers

```text
Work package 7.1: integrate the completed work packages into docs/thesis/:
- chapter 4: a section on the composed-scenario architecture, with X1 as the worked example;
- chapter 5: composed-scenario results as (gas, latency, exposure) triples, citing only
  V-status register rows;
- chapter 6: discussion of split-brain revocation, rotation != unlinkability, and the
  migration curve;
- chapter 7: moonshot future work with the prototype evidence gathered.
Propose (do not adopt) SIDE_PAPERS.md entries SP-9 (ZK UBI), SP-10 (split-brain
revocation in composed SSI services) and SP-11 (the cost of unlinkable tolling). Add
docs/INDEX.md rows for every new document and a CHANGELOG entry. List all open author
decisions in a new handback file docs/HANDBACK_<date>.md.
```
