# Chapter 4 — Implementation (Working Draft)

**Status**: working draft. This chapter describes *what was built* — the
system architecture and its concrete realization in code — as of v0.8.0
(tagged "Rigor & Ground-Truth Hardening"; working toward 0.9.0, `VERSION`
reads `0.9.0-dev`). Every component named here maps to a committed file
under the repository; the measured *results* those components produce are
reported separately in Chapter 5. Where a component is a deliberately
minimal, representative, or simulated realization, this chapter says so
explicitly — the honesty caveats are load-bearing and are preserved
throughout.

**Scope note**: this chapter states only what exists in the repository. It
describes design and construction, not outcomes; all quantitative results
(gas, latency, compliance, security defense counts) live in Chapter 5 and
are cited here only where they characterize an implementation choice.

---

## 4.1 System Architecture

The implementation is organized as four composable layers, each a
self-contained subtree of the repository, wired so that a higher layer
consumes the artifacts of the layer beneath it without reaching into its
internals.

| Layer | Directory | Responsibility |
|---|---|---|
| 1 — Blockchain identity | `1_blockchain-identity/` | The 9 identity standards + the MOBI VID profile as Solidity contracts; gas benchmark; Sepolia harness |
| 2 — W3C SSI | `2_w3c-ssi-layer/` | DID resolution (4 methods), Verifiable Credentials (issue/hold/verify), MOBI VID I + II Python layer |
| 3 — CV2X testbed | `cv2x-testbed/` (mapped from `3_cv2x-testbed/`) | Identity providers, 12 lifecycle use cases, SUMO V2V simulation with in-path identity verification |
| 4 — Comparison & validation | `4_comparison-framework/` | Gas benchmark tables, two-lens security analysis, W3C compliance checker outputs, Sepolia validation slot |

**How the layers compose.** Layer 1 provides the on-chain root of trust:
each standard realizes a vehicle identity on the EVM and exposes the
primitives (registries, tokens, accounts, claims) that everything above
depends on. Layer 2 lifts those on-chain identities to W3C conformance —
the DID resolver turns an on-chain address or token into a DID Document,
and the Verifiable Credentials stack issues and verifies credentials whose
signing keys are the *same* keys that control the Layer-1 identities, so
that off-chain verification needs no chain round-trip. Layer 3 embeds
those credentials in a connected-vehicle setting: identity *providers*
abstract PKI, centralized, and blockchain backends behind one interface,
the use-case suite exercises full credential lifecycles end-to-end, and
the V2V simulation places real signature/credential verification directly
in the message path. Layer 4 is measurement-only: it consumes the
artifacts of Layers 1–3 (never modifying them) and turns raw
measurements into thesis tables and matrices.

**Directory-layout note (honesty).** The thesis-chapter directory
`3_cv2x-testbed/` is a mapping stub — a `README.md` that points to the
working testbed, which physically lives at repository root in
`cv2x-testbed/`. The testbed was kept at root to preserve its internal
`sys.path` wiring across the identity/scenario/sumo modules; the stub
records the chapter-to-code mapping without moving files.

**Toolchain.** Two runtimes are used, each pinned for reproducibility:

- **Solidity / Hardhat** (`1_blockchain-identity/hardhat.config.js`):
  solc **0.8.24**, optimizer at **200 runs** with **viaIR**, OpenZeppelin
  Contracts **5.0.2**, ethers v6, hardhat-toolbox; Node 18. Contract tests
  and the gas benchmark run on the in-process Hardhat network
  (`chainId 31337`).
- **Python 3.11** (`2_w3c-ssi-layer/requirements.txt`): `web3` (v7),
  `eth-account`, `cryptography`, `coincurve`-backed secp256k1, `pytest`.
  This runtime hosts the SSI layer, the testbed, and the comparison
  scripts.

The two runtimes meet at the on-chain boundary: the Python MOBI VID layer
binds to the deployed `MOBIVIDRegistryV2` contract via `web3`, and the VC
layer's `eip191-secp256k1-recovery-2024` cryptosuite uses exactly the
secp256k1 primitive the EVM's `ecrecover` uses, so a credential signed
off-chain in Python verifies on-chain in Solidity and vice-versa.

---

## 4.2 Blockchain Identity Layer

All nine standards plus the MOBI VID application profile are implemented as
Solidity contracts under `1_blockchain-identity/contracts/`. Each is a
*vehicle identity* — a VIN-bearing, owner-controlled on-chain object — and
each was written to be benchmarked under one harness
(`scripts/benchmark_gas.js`) so that identical operations are compared
across standards.

A design convention runs through the layer: every standard is a
**clean, self-contained representative implementation** rather than an
inherited vendor package. This was a deliberate engineering decision —
several reference packages (e.g. the `erc725/smart-contracts` v7 package,
which pins OpenZeppelin ^4.9.3 and calls the 3-argument
`Address.verifyCallResult` removed in OZ 5.0) would force a mixed OZ4/OZ5
compilation graph into an otherwise OZ-5 project. Each contract instead
reproduces the standard's public interface, ERC-165 interface IDs, and
event shapes faithfully, documented in-header. Two contracts are
additionally *feature-minimal* (not merely self-contained) and say so in
their headers; these are called out explicitly below because their gas is
a lower bound, not a full-featured figure.

### The nine standards + MOBI VID profile

| Standard | Contract file | What it is, as a vehicle identity | Design trade-off |
|---|---|---|---|
| **ERC-1056** | `ERC1056/EthereumDIDRegistry.sol` (+ `CVINVehicleDIDRegistry.sol`) | Every address is implicitly its own `did:ethr` at zero on-chain cost; the registry records attributes, delegates, and owner changes as **events**, from which an off-chain resolver rebuilds the DID Document. | Cheapest lifecycle; no on-chain readability of claims by other contracts. |
| **ERC-721** | `ERC721/CVINVehicleNFT.sol` (+ `CVIN_NFT_DID_ERC721.sol`) | Each vehicle is a unique, transferable NFT (`did:nft`) carrying metadata. | Familiar ownership/transfer model; heavy to mint, and a transfer moves the whole identity (identity-theft surface). |
| **ERC-725** | `ERC725/CVIN_DID_ERC725.sol` | Proxy account separating identity from keys, with a key/data store. | Key rotation without changing the identifier; heavy deploy. |
| **ERC-725xy** | `ERC725xy/CVINVehicleERC725XY.sol` (+ `CVINExecuteTarget.sol`) | The **full ERC-725X generic executor + ERC-725Y data store** account — a self-sovereign smart account that can act on-chain and carries VIN/make/model/year as `bytes32`-keyed data. Added in v0.8.0, closing the one previously-missing standard. | Maximum on-chain capability; the **heaviest** to deploy (a complete account per identity). |
| **ERC-735** | `ERC735/CVINVehicleClaimHolder.sol` | On-chain claim holder: manufacturer/regulator attestations stored as claims with issuer signatures verified at add-time. | O(1) on-chain claim verification; carries a full claim state machine, so very heavy to deploy. |
| **ERC-1155** | `ERC1155/CVINVehicleCredential1155.sol` | One contract issues many credential types; the birth credential is configured **soulbound** via an `_update` override. | Uniquely resists identity theft (non-transferable); no key recovery. |
| **ERC-4337** | `ERC4337/CVINVehicleAccount.sol` + `ERC4337/CVINMinimalEntryPoint.sol` | Account-abstraction identity with UserOperation flow and **guardian-based social recovery** — the only standard here with genuine on-chain key recovery. | Real key recovery; account-abstraction indirection tax per operation. |
| **LSP8** | `LSP8/CVINVehicleLSP8.sol` | A LUKSO LSP8 Identifiable-Digital-Asset vehicle: each vehicle is a `bytes32` tokenId (`keccak256(VIN)`) with a per-token key/value metadata store. | Cross-ecosystem reference point; a transfer moves the identity. |
| **CVIN-Combined** | `CVINCombined/CVINCombinedIdentity.sol` | **The thesis's own hybrid**: an ERC-1056 event-based identity fused with ERC-735-style on-chain claims in a single contract, sharing one ownership model. | Cheap event-log common path *plus* O(1) on-chain claims only where safety-critical — the H5 design. |
| **MOBI VID (profile)** | `MOBI/MOBIVIDRegistryV2.sol` (extends `MOBIVIDRegistry.sol`; uses `ERC1056Registry.sol`) | The MOBI **VID II** application profile: a purpose-built registry for birth records and typed lifecycle events with role-gated, signature-verified attestations. Measured *alongside* the nine as an application profile, not one of the nine base standards. | Maximal on-chain semantic fidelity (typed events, odometer, jurisdiction, hashed VIN); pays for that structure in gas. |

### Honesty caveats specific to this layer

- **ERC-4337 EntryPoint is a minimal representative harness.**
  `CVINMinimalEntryPoint.sol` states in its header that it is
  "SIMPLIFIED RESEARCH HARNESS — NOT the canonical ERC-4337 EntryPoint."
  It handles a single UserOperation (no bundler mempool / `handleOps`
  batching), no paymaster, no signature aggregation, no gas
  accounting/deposits/stakes/refunds, and no `initCode` deployment. It
  exists to *isolate and measure* the EntryPoint indirection overhead
  against a direct EOA call; the `userOpHash` computation mirrors the v0.7
  scheme for hash-compatibility. Its gas is therefore a **lower bound** on
  a fully-featured EntryPoint.
- **LSP8 is a minimal representative implementation.**
  `CVINVehicleLSP8.sol` is a self-contained LSP8-flavored asset that does
  not import the LUKSO `lsp-smart-contracts` package; it implements the
  conformant tokenId format, ownership, transfer, and per-token data-store
  signatures/events, with omissions documented in-header. Its gas is
  likewise a lower bound.
- **CVIN-Combined is the thesis's own contribution**, not a pre-existing
  standard. Its header records the design rationale: events are cheap for
  the common identity path, but a vehicle interacting with infrastructure
  "cannot walk an event log inside the EVM," so the safety-critical subset
  (VIN, manufacturer/type-approval, periodic-inspection) is stored as
  ERC-735-style claims whose issuer signature is verified with `ecrecover`
  at add-time, enabling O(1) `getClaim` later. Both sides share the
  ERC-1056 `identityOwner` gate.
- **MOBI VID V2 is the application profile**, measured next to the nine
  base standards rather than counted among them.

---

## 4.3 W3C SSI Layer

`2_w3c-ssi-layer/` lifts the on-chain identities of Layer 1 to W3C
conformance and adds the credential machinery the testbed consumes. It has
three parts: DID resolution, the Verifiable Credentials stack, and the
MOBI VID Python layer.

### 4.3.1 DID Resolver — four methods

`did-resolution/did_resolver.py` implements a W3C **DID Core v1.0**
resolver over four methods, each backed by a Layer-1 standard:

| Method | Format | Backed by |
|---|---|---|
| `did:ethr` | `did:ethr:<chainId>:<address>` | ERC-1056 |
| `did:nft` | `did:nft:<chainId>:<contract>:<tokenId>` | ERC-721 |
| `did:key` | `did:key:<chainId>:<address>` | ERC-725 |
| `did:mobi` | `did:mobi:<VIN>` | MOBI VID |

Resolution returns a `DIDResolutionResult` (`didDocument`,
`didResolutionMetadata`, `didDocumentMetadata`); documents carry
`@context`, `verificationMethod`
(`EcdsaSecp256k1VerificationKey2019`, `blockchainAccountId`), and the W3C
verification relationships (`authentication`, `assertionMethod`, …).
Resolution is offline/local for the address-bearing methods, with caching
to amortize repeats. The resolver *defines* `did:mobi:<VIN>` but the MOBI
on-chain layer deliberately resolves vehicles via `did:ethr` instead, so
the VIN is never embedded in the public identifier (§4.3.3) — the
VIN-embedding method is retained in the resolver but flagged as a privacy
footgun the on-chain layer avoids.

### 4.3.2 Verifiable Credentials stack

`verifiable-credentials/` implements the **VC Data Model 2.0** end-to-end
with an Ethereum-native securing mechanism, split across issuer, holder,
and verifier:

- **Issuer** (`vc_issuer.py`) — issues credentials, produces
  `DataIntegrityProof`s under the cryptosuite
  **`eip191-secp256k1-recovery-2024`** (EIP-191 personal-sign over
  deterministic canonical JSON, signed by the key that controls the
  issuer's on-chain identity), and manages a revocation registry.
- **Holder** (`vc_holder.py`) — a wallet that stores credentials, builds
  presentations bound to a `challenge` (replay protection) and `domain`
  (audience) with `proofPurpose: authentication`, and performs
  **selective disclosure** (SD-JWT-style salted claim digests: the signed
  VC carries only `claimDigests`, and the holder discloses chosen
  claim+salt pairs at presentation time).
- **Verifier** (`vc_verifier.py`) — a **6-stage offline verification
  pipeline**: structure → schema → temporal → revocation → signature →
  disclosure. Signature verification is secp256k1 public-key recovery, so
  **no blockchain round-trip is needed at verification time** — the
  property the V2V latency budget requires.

The stack ships **10 automotive schemas** (`vc_schemas.py`), 1:1 with the
thesis use cases: VehicleBirthCertificate, OwnershipTransfer,
InsuranceClaim, MaintenanceRecord, SafetyRecall, TheftReport,
RegistrationCredential, DecommissionCertificate, V2VSafetyCredential,
EmissionsCompliance. Forged proofs, tampered disclosures, wrong-challenge
replays, and expired/revoked credentials all fail the pipeline — exercised
by the 28-test suite (`tests/test_vc_layer.py`).

### 4.3.3 MOBI VID — VID I and VID II

`mobi-vid/` layers MOBI VID on top of the canonical VC stack and anchors
each credential on-chain by **content-hash anchoring** (keccak256 of the
canonicalized signed VC written to a contract field — no IPFS anywhere).
The registry contract is `MOBIVIDRegistryV2.sol`.

**VID I — Birth Certificate** (`birth_certificate.py`).
`BirthCertificateIssuer.issue_birth_certificate(...)` (1) issues a
schema-enforced `VehicleBirthCertificate` VC, (2) computes its keccak256
content hash, and (3) registers the birth on-chain. Two privacy mechanisms
protect the VIN:

- **Salted hash on-chain**: only `sha256(vin || ":" || salt)` (32-byte
  random salt) reaches the chain; the salt is disclosed off-chain only to
  parties that must link VIN → vehicle. The vehicle DID is
  `did:ethr:<chainId>:<addr>`, so the identifier itself never leaks the
  VIN.
- **AES-256-GCM VIN encryption** (this replaced an earlier demo XOR): the
  32-byte key is **HKDF-SHA256**-derived from a per-vehicle owner secret
  (salted by the VIN salt); the ciphertext is AEAD-bound to the on-chain
  `vinHash` via GCM associated data, so it cannot be transplanted onto
  another record. Neither the VIN nor the key ever reaches the chain.
  Covered by 9 cipher tests in `tests/test_vin_cipher.py` (part of the 32
  MOBI VID Python tests) plus 6 in
  `cv2x-testbed/scripts/test_vin_encryption.py`.
  **Caveat**: VIN-cipher key distribution / HSM custody is out of scope
  for the testbed; the thesis claim is the privacy *architecture*
  (hash-on-chain, encrypt off-chain), not a production key-management
  system.

`BirthCertificateVerifier.verify(...)` checks the full VC pipeline *and*
that keccak256(VC) equals the on-chain `birthCertHash`, that (vin, salt)
recomputes the on-chain `vinHash`, and that the VC issuer equals the
on-chain manufacturer.

**VID II — Lifecycle Events** (`lifecycle_events.py`).
`LifecycleEventRecorder.record_event(...)` issues an event VC and anchors
it on-chain in one call. The Python enums mirror `MOBIVIDRegistryV2.sol`
exactly:

- **11 event types**: MAINTENANCE, REPAIR, ACCIDENT, RECALL, INSPECTION,
  MODIFICATION, THEFT_REPORT, RECOVERY, INSURANCE_CLAIM, REGISTRATION,
  DECOMMISSION.
- **Issuer roles (NONE + 8)**: MANUFACTURER, DEALER, SERVICE_CENTER,
  INSPECTION_STATION, GOVERNMENT_DMV, INSURANCE_COMPANY, POLICE, OWNER —
  the contract gates which role may issue which event.
- **On-chain multi-party attestation**: `attest_event(...)` produces an
  EIP-191 signature over a domain-separated digest
  `keccak256(contract, chainId, vehicle, eventId)`; the contract's
  `attestEvent` recovers the signer on-chain via **`ecrecover`** (OZ
  ECDSA, low-s) and requires it to equal the attester, so forged and
  replayed attestations revert. `VehicleHistoryAggregator` rebuilds a
  fully verified history (anchor integrity + signature recovery + issuer
  consistency) with an odometer-rollback fraud heuristic.

The `attestEvent` signature verification is itself a
found-and-fixed result: the original `attestEvent` *stored* an attestation
signature but never verified it on-chain (role-gated only) — a
replay/forgery gap surfaced by the security analysis and then closed
(cost rose 121k → 193k gas). Chapter 5 §5.6 reports the before/after tests
and the gas delta; the point here is that the shipped contract verifies.
The MOBI VID Python suite totals **32 tests** (layer + VIN cipher).

---

## 4.4 CV2X Testbed

`cv2x-testbed/` embeds the identity machinery in a connected/autonomous
vehicle setting. It has three pieces relevant to this chapter: pluggable
identity providers, the lifecycle use-case suite, and the V2V simulation.

### 4.4.1 Identity providers

`identity/base.py` defines an abstract, backend-agnostic identity
interface (`IdentityType`, unified metric collection, hot-swappable at
runtime) so that applications "don't know or care" which identity system
is underneath. Concrete providers implement it for each backend family:

- **PKI / centralized** — `identity/standard/pki_identity.py` (IEEE
  1609.2-style pseudonym certificates, real ECDSA P-256),
  `identity/centralized_provider.py`,
  `identity/centralized_vehicle_registry.py`.
- **Blockchain / SSI** — `identity/erc1056_provider.py`,
  `identity/mobi_vid_provider.py`, and
  `identity/w3c_verifiable_credentials.py` (a shim onto the canonical
  Layer-2 VC stack).
- `identity/comparison_framework.py` unifies metrics across all backends
  so PKI and SSI are measured on equal footing.

### 4.4.2 Twelve lifecycle use cases

`scripts/test_use_cases.py` runs 12 end-to-end scenarios with **real
cryptographic verification** and **computed** (not hardcoded) pass/fail —
the suite exits nonzero if any scenario fails:

1. Vehicle Manufacturing & Birth Registration
2. Regular Maintenance Service
3. Ownership Transfer (Used-Car Sale)
4. Insurance Claim (Accident)
5. Manufacturer Recall
6. Cross-Border Vehicle Import
7. Fleet Management
8. Emissions Testing & Compliance
9. Vehicle Theft & Recovery
10. Autonomous Vehicle Data Sharing (selective disclosure)
11. Dealership-Mediated Sale (Trade-In + Certified Resale)
12. End-of-Life Decommission

Within these flows, **forged and replayed credentials are demonstrated to
fail** — verification is exercised adversarially, not merely asserted.
Result: **12/12 passing**.

### 4.4.3 SUMO V2V simulation with in-path identity verification

`sumo/sumo_identity_integration.py --simulate` runs a highway V2V
simulation broadcasting **10 Hz** Basic Safety Messages, with **identity
verification placed directly in the message path** for two populations:

- **PKI population** — every BSM is signed with real ECDSA P-256 at send
  and verified at receive; the cold path additionally validates the
  pseudonym-certificate chain against the CA, then caches the cert public
  key (warm path = signature check only).
- **SSI population** — each vehicle holds an Ethereum secp256k1 key, a
  `did:ethr` DID, and a W3C `V2VSafetyCredential` issued through the Layer-2
  VC stack; BSMs are signed per-message with EIP-191 personal-sign. The
  cold path performs full VC verification (structure, validity window,
  revocation, issuer signature recovery, subject/DID binding), then caches
  the peer address (warm path = signature recovery + address comparison).

Cold (first-contact) and warm (per-message) latencies are recorded
separately per population. `sumo/run_v2v_stats.py` drives the simulation as
independent seeded subprocesses to aggregate an **N=30** campaign into
`sumo/results/v2v_latency_stats.json`. The CV2X protocol stack
(`protocols/cv2x_stack.py`, PHY/MAC + BSM/DENM) is simulation-grade, and
V2V scenarios live in `scenarios/` (`basic_v2v_scenario.py`,
`cv2x_identity_integration.py`).

**Honesty caveats (per the module header).** What is *real*: all signing,
signature verification, certificate-chain validation, and VC verification
(timed with `time.perf_counter`). What is *mock*: vehicle mobility in
`--simulate` mode (no SUMO binary required; the SUMO/TraCI code path and
hand-authored configs exist but were not exercised against the binary in
the measurement environment), and the radio channel (messages delivered
in-process; no radio/MAC/network stack). The measurement bounds the
*cryptographic* cost of identity verification, which was the open question;
the network-stack contribution is out of scope. Chapter 5 §5.4 reports the
resulting latencies.

---

## 4.5 Comparison & Validation Framework

`4_comparison-framework/` is measurement-only: it consumes the artifacts of
Layers 1–3 and never modifies them. Five instruments make up the framework.

1. **Gas benchmark + table generation.**
   `1_blockchain-identity/scripts/benchmark_gas.js` runs an identical
   operation set across all nine standards + MOBI-VID-V2 on a fresh
   in-process network and records exact `receipt.gasUsed` into
   `results/gas_benchmark.json`.
   `performance-metrics/run_gas_stats.py` re-runs the benchmark N=30 to
   record determinism (`gas_benchmark_stats.json`), and
   `performance-metrics/generate_tables.py` emits the camera-ready LaTeX
   (`results/gas_comparison.tex`) and CSV (`gas_comparison.csv`).

2. **Two-lens security analysis** (`security-analysis/`).
   *Lens 1 — executable attack suite*: the Mocha scenarios in
   `1_blockchain-identity/test/security/securityScenarios.test.js` (with
   the `attackHarness.js` helper) fire adversarial transactions against the
   deployed contracts and assert reverts, with a differential control that
   the authorized operation succeeds; results are tabulated to
   `security-analysis/results/attack_results.{json,csv,tex}`.
   *Lens 2 — threat-matrix analysis*
   (`attack_scenarios.py`, `generate_attack_tables.py` →
   `security_matrix.{json,csv}`, `onchain_security.json`,
   `security_comparison.tex`) extends beyond pass/fail defense to
   properties a revert test cannot express: Sybil economics, recovery
   availability, and on-chain PII leakage. The two lenses' relationship is
   documented in `security-analysis/README.md`.

3. **W3C compliance checker.**
   `cv2x-testbed/scripts/w3c_compliance_checker.py` is an *executable*
   checker (negative checks are first-class: forged/tampered/expired/
   unsupported inputs must be rejected) that scores the Layer-2 VC stack and
   DID resolver against DID Core v1.0 and VC Data Model 2.0. It is CI-gated
   at ≥90%; the two documented deviations (canonical JSON vs URDNA2015; the
   thesis-defined cryptosuite) are counted as failures rather than hidden.
   Chapter 5 §5.5 reports the measured score.

4. **Sepolia validation harness.**
   `1_blockchain-identity/scripts/validate_sepolia.js` +
   `SEPOLIA_VALIDATION.md` re-run the gas benchmark against public Sepolia
   to confirm the local numbers, writing to
   `results/sepolia_validation.json`. **This harness is built but not yet
   executed** — it needs an RPC URL and a funded test key; the results slot
   is a placeholder until the run. The gas *comparison* remains valid
   locally because EVM gas is a deterministic function of opcodes executed;
   what Sepolia would add is absolute confirmation on a public chain.

5. **MOBI VID backend sweep.**
   `1_blockchain-identity/scripts/mobi_vid_backend_sweep.js` maps MOBI VID's
   three canonical operations (birth, lifecycle, third-party attestation)
   onto every backend's *native* primitives — reusing the existing,
   unmodified contracts, no new Solidity — and records real `gasUsed` plus
   an honest fidelity rating (native vs forced/approximate). Tables are
   generated by `performance-metrics/generate_mobi_backend_table.py`
   (`mobi_vid_backends.{csv,tex}`). This is the H4 evidence in Chapter 5
   §5.3.1.

---

## 4.6 Testing & Reproducibility

The implementation is backed by roughly **295 automated tests, all green**,
across both runtimes:

| Suite | Count | Location |
|---|--:|---|
| Hardhat contract tests | 217 | `1_blockchain-identity/test/**` |
| W3C Verifiable Credentials | 28 | `2_w3c-ssi-layer/verifiable-credentials/tests/test_vc_layer.py` |
| MOBI VID layer | 32 | `2_w3c-ssi-layer/mobi-vid/tests/` (incl. VIN cipher) |
| VIN cipher (subset of MOBI VID) | 6 | `2_w3c-ssi-layer/mobi-vid/tests/test_vin_cipher.py` |
| Lifecycle use cases | 12/12 | `cv2x-testbed/scripts/test_use_cases.py` |

The 217 Hardhat total exceeds the raw `it()` count because several suites
generate parameterized cases per standard/operation at runtime. The
security suite (`test/security/securityScenarios.test.js`, 54 scenarios,
43/43 applicable cells defended) stays green *because* the contracts
defend, so a regression would surface as a real CI failure.

**Reproducibility properties.**

- **Committed lockfile** — `1_blockchain-identity` ships an npm lockfile so
  `npm ci` installs a byte-identical dependency tree; the getting-started
  path is `npm ci && npx hardhat test` → 217 passing.
- **Deterministic outputs** — gas is exact `receipt.gasUsed` and was
  verified byte-identical across N=30 runs (σ=0, 95% CI width 0); the
  benchmark, compliance, and V2V commands regenerate every number reported
  in Chapter 5.
- **CI workflows** (`.github/workflows/`) — three gates:
  `test-contracts.yml` (the 217 Hardhat tests), `benchmark.yml` (gas
  benchmark), and `w3c-compliance.yml` (the ≥90% compliance gate).
- **Verified commands** (from `INVENTORY.md` / `CAPABILITIES.md`):
  - Contracts: `cd 1_blockchain-identity && npm ci && npx hardhat test`
  - VC: `python3 -m pytest 2_w3c-ssi-layer/verifiable-credentials/tests/`
  - MOBI VID: `cd 2_w3c-ssi-layer/mobi-vid && python3 -m pytest tests/`
  - Use cases: `python3 cv2x-testbed/scripts/test_use_cases.py`
  - Compliance: `python3 cv2x-testbed/scripts/w3c_compliance_checker.py`
  - Gas: `cd 1_blockchain-identity && npx hardhat run scripts/benchmark_gas.js`
  - V2V: `python3 cv2x-testbed/sumo/sumo_identity_integration.py --simulate`
    (N=30 via `cv2x-testbed/sumo/run_v2v_stats.py`)

---

## 4.7 Summary

This chapter described a four-layer implementation: (1) nine blockchain
identity standards plus the MOBI VID profile, each a self-contained
representative Solidity contract benchmarked under one harness — with the
ERC-4337 EntryPoint and LSP8 flagged as deliberately minimal (lower-bound
gas) and CVIN-Combined identified as the thesis's own ERC-1056+ERC-735
hybrid; (2) a W3C SSI layer that resolves four DID methods and issues,
holds, and verifies Verifiable Credentials offline (6-stage pipeline, 10
schemas, selective disclosure, revocation, EIP-191 Data Integrity proofs),
including MOBI VID I birth certificates (content-hash anchoring,
AES-256-GCM VIN encryption) and VID II lifecycle events (on-chain
`ecrecover` attestation verification); (3) a CV2X testbed with pluggable
identity providers, 12 real-crypto lifecycle use cases, and a SUMO V2V
simulation that runs real signature/credential verification in the message
path; and (4) a measurement-only comparison framework producing the gas,
security, compliance, and validation artifacts Chapter 5 reports. The
build is reproducible — a committed lockfile, deterministic outputs, three
CI gates, and ~295 green tests — and its honesty caveats (minimal ERC-4337/
LSP8, unexecuted Sepolia run, simulated mobility and radio, out-of-scope
VIN key custody) are stated where they arise rather than deferred.

---

*Working draft. Component references are to committed files in the
repository as of v0.8.0 / 0.9.0-dev; measured results are reported in
Chapter 5.*
