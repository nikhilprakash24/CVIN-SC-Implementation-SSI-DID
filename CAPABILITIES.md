# System Capabilities Reference

**Complete guide to what this thesis implementation can do**

> Comparative Analysis of Self-Sovereign Identity Systems for Connected and
> Autonomous Vehicles — Nikhil Prakash, MASc, University of British Columbia
> (ECE, Blockchain Interdisciplinary Research Cluster).
> Version 0.9.0-dev (v0.8.0 tagged: "Rigor & Ground-Truth Hardening").

---

## 🎯 Overview

This system implements **Self-Sovereign Identity (SSI) for Connected and
Autonomous Vehicles** and compares **9 blockchain identity standards** plus the
MOBI VID application profile under one measurement harness. Every layer listed
below is **built and tested** — automated suites total ~295 passing tests
(**217 Hardhat contract tests + 28 W3C VC + 32 MOBI VID + 6 VIN-cipher +
12/12 lifecycle use cases**).

- ✅ Vehicle identity across **9 blockchain standards** (real on-chain gas)
- ✅ W3C DID resolution (4 methods)
- ✅ W3C Verifiable Credentials — issue / hold / verify, selective disclosure,
  revocation (**built**, was previously "planned")
- ✅ MOBI VID I birth certificates + VID II lifecycle events (on-chain
  attestation, AES-256-GCM VIN encryption)
- ✅ Real-time V2V safety messaging (SUMO sim, measured latency)
- ✅ Performance, security, and W3C-compliance comparison framework

**Honesty caveats (kept throughout):** gas is Hardhat-local and deterministic —
a Sepolia validation harness exists but the public-testnet run is not yet
executed; V2V latency is identity-verification CPU time only (no radio/MAC/
network stack; simulated mobility); the ERC-4337 EntryPoint and LSP8 are
minimal representative implementations; VIN-cipher key distribution / HSM
custody is out of scope for the testbed.

---

## 1️⃣ Blockchain Identity Capabilities

All 9 standards are implemented as Solidity contracts in
`1_blockchain-identity/contracts/` and benchmarked by
`scripts/benchmark_gas.js`. Gas below is the **exact `receipt.gasUsed`** of one
representative transaction per operation, measured on a fresh in-process
Hardhat network (solc 0.8.24, optimizer runs=200, viaIR, OpenZeppelin 5.0.2),
**verified byte-identical across N=30 runs (95% CI width = 0)** — EVM gas is
deterministic for fixed calldata and pre-state.

### Real measured gas (per operation)

| Standard | Create identity | Update attribute | Transfer |
|----------|----------------:|-----------------:|---------:|
| **CVIN-Combined** (ERC-1056 + ERC-735 hybrid) | 52,178 | 35,078 | 51,734 |
| **ERC-1056** (lightweight DID registry) | 52,612 | 35,512 | 51,764 |
| **ERC-1155** (multi-token, soulbound) | 103,905 | 49,156 | 83,641 |
| **LSP8** (LUKSO NFT, *minimal repr.*) | 149,352 | 55,065 | 80,526 |
| **MOBI-VID-V2** (application profile) | 298,923 | 306,980 | 200,018 |
| **ERC-725** (proxy account) | 528,647 | 137,107 | 28,397 |
| **ERC-721** (vehicle NFT) | 542,429 | 119,753 | 174,707 |
| **ERC-4337** (account abstraction, *minimal repr.*) | 768,204 | 49,366 | 28,561 |
| **ERC-735** (claim holder) | 1,404,108 | 75,188 | 28,704 |
| **ERC-725xy** (full ERC-725 X+Y smart account) | 1,704,992 | 49,950 | 28,839 |

**Key finding (H1 SUPPORTED):** ~33× spread from cheapest to most expensive
identity creation; the minimal registries (CVIN-Combined, ERC-1056) are ~10×
cheaper to create than ERC-721/ERC-725. For ERC-4337, routing the same
`setAttribute` through the EntryPoint as a UserOperation costs 96,228 gas vs
49,366 direct — a **+46,862 gas / op** indirection overhead (bundler overhead
excluded).

*Gas is dimensionless; any fiat figure depends on the live gas price and token
price and is intentionally omitted here.*

---

### ERC-1056 — Lightweight DID Registry ✅

**What it does:** every Ethereum address is implicitly its own `did:ethr` (zero
on-chain cost to exist); the registry records attributes, delegates, and owner
changes as events.

*Illustrative usage (Hardhat / ethers):*
```javascript
const registry = await EthereumDIDRegistry.deploy();
// did:ethr:<chainId>:<vehicleAddress> — no creation tx required
await registry.setAttribute(vehicle, key, value, validitySeconds); // 35,512 gas
await registry.addDelegate(vehicle, "sigAuth", serviceCenter, ttl); // 54,853 gas
await registry.changeOwner(vehicle, newOwner);                      // 51,764 gas
```
**Use cases:** birth-certificate anchoring, service-center authorization, key
rotation, attribute timestamping. This is also the CVIN-Combined base.

### ERC-721 — NFT-Based Identity ✅
Each vehicle is a unique, transferable NFT (`did:nft`). Mint 542,429 gas;
`safeTransferFrom` 174,707 gas; metadata is read-only. Use cases: unique
vehicle identity, ownership-transfer tracking, marketplaces.

### ERC-725 / ERC-725xy — Proxy / Smart-Account Identity ✅
`ERC-725` separates identity from keys (key rotation, multi-key control,
generic `execute`). `ERC-725xy` is the **full ERC-725 X+Y smart account** added
in v0.8.0 — the heaviest to deploy (1,704,992 gas create) but cheap to transfer
control (28,839 gas). Use cases: multi-sig / fleet ownership, meta-transactions,
key rotation without changing the identity.

### ERC-735 — Claim Holder ✅
On-chain claim registry (addClaim / removeClaim). Expensive to deploy
(1,404,108 gas) because it carries the full claim-management state machine.
Use cases: manufacturer/regulator attestations bound to an identity.

### ERC-1155 — Multi-Token Credentials (soulbound) ✅
One contract issues many credential types; the thesis configures credentials as
**soulbound** (non-transferable). In the security analysis this is the only
standard that structurally resists identity theft. Create 103,905 gas.

### ERC-4337 — Account Abstraction (minimal representative) ✅ ⚠️
`CVINVehicleAccount` + `CVINMinimalEntryPoint` demonstrate UserOperation flow
and **guardian-based social recovery** — the only standard here with genuine
on-chain key recovery. **Deliberately minimal** (documented in the contract
headers); its gas is a lower bound. Create 768,204 gas; the EntryPoint
indirection adds +46,862 gas per routed op.

### LSP8 — LUKSO Identifiable Digital Asset (minimal representative) ✅ ⚠️
A minimal LSP8 vehicle asset for cross-ecosystem comparison. Create 149,352
gas; also a lower-bound reference implementation.

### CVIN-Combined — the thesis's own hybrid ✅
`CVINCombinedIdentity` fuses ERC-1056 lightweight DID semantics with ERC-735
claims. Cheapest identity creation measured (52,178 gas) while still supporting
claims — placing it on the security/performance frontier (H5 SUPPORTED).

---

## 2️⃣ W3C DID Resolution Capabilities ✅

`2_w3c-ssi-layer/did-resolution/did_resolver.py` resolves DIDs to W3C DID Core
v1.0 documents.

| Method | Format | Backed by |
|--------|--------|-----------|
| `did:ethr` | `did:ethr:<chainId>:<address>` | ERC-1056 |
| `did:nft`  | `did:nft:<chainId>:<contract>:<tokenId>` | ERC-721 |
| `did:key`  | `did:key:<chainId>:<address>` | ERC-725 |
| `did:mobi` | `did:mobi:<VIN>` | MOBI VID |

*Real API:*
```python
from did_resolver import DIDResolver, DIDMethod

resolver = DIDResolver()
result = resolver.resolve("did:ethr:0x1:0x123...")   # -> DIDResolutionResult
#   result.didDocument / result.didResolutionMetadata / result.didDocumentMetadata

did, doc = resolver.create_did(DIDMethod.MOBI, vin="5YJ3E1EA0PF123456")
```
Documents include `@context`, `verificationMethod`
(`EcdsaSecp256k1VerificationKey2019`, `blockchainAccountId`), and the W3C
verification relationships (`authentication`, `assertionMethod`, …). Resolution
is offline/local for the address-bearing methods; caching amortizes repeats.

---

## 3️⃣ W3C Verifiable Credentials ✅ (BUILT — 28 tests)

`2_w3c-ssi-layer/verifiable-credentials/` implements the **VC Data Model 2.0**
end-to-end with an Ethereum-native securing mechanism. Signatures verify
**offline via secp256k1 public-key recovery** — no blockchain round-trip at
verification time (the V2V latency requirement).

- **Proof:** `DataIntegrityProof`, cryptosuite `eip191-secp256k1-recovery-2024`
  (EIP-191 personal-sign over deterministic canonical JSON). The signing key is
  the same key that controls the issuer's on-chain identity.
- **10 automotive schemas** (`vc_schemas.py`): VehicleBirthCertificate,
  OwnershipTransfer, InsuranceClaim, MaintenanceRecord, SafetyRecall,
  TheftReport, RegistrationCredential, DecommissionCertificate,
  V2VSafetyCredential, EmissionsCompliance.
- **Selective disclosure:** SD-JWT-style salted claim digests — the signed VC
  carries only `claimDigests`; the holder discloses chosen claim+salt pairs at
  presentation time and the verifier recomputes each digest.
- **Revocation:** `credentialStatus` checked against a `RevocationRegistry`
  (in-memory or JSON-file backed; MOBI VID adds the on-chain anchor).
- **6-stage verify pipeline:** structure → schema → temporal → revocation →
  signature → disclosure. Presentations additionally bind challenge (replay
  protection) and domain (audience), with `proofPurpose: authentication`.

*Real API (matches the modules):*
```python
from vc_issuer import CredentialIssuer
from vc_holder import HolderWallet
from vc_verifier import CredentialVerifier

issuer = CredentialIssuer.with_ethr_did(chain_id="0x1")   # DID derived from key
envelope = issuer.issue_credential(
    credential_type="VehicleBirthCertificate",
    subject_did="did:mobi:5YJ3E1EA0PF123456",
    claims={"vin": "5YJ3E1EA0PF123456", "make": "Tesla", "model": "Model 3",
            "year": 2024, "manufacturingDate": "2024-01-15",
            "manufacturerDid": issuer.issuer_did},
    validity_days=None,          # birth certificates do not expire
)                                # -> {"verifiableCredential": ..., "disclosures": ...}

wallet = HolderWallet.with_ethr_did()
cid = wallet.store_credential(envelope)
vp = wallet.create_presentation([cid], challenge="nonce-42",
                                domain="dmv.gov.bc.ca")

verifier = CredentialVerifier(revocation_registry=issuer.revocation_registry)
ok, report = verifier.verify_presentation(vp, "nonce-42", "dmv.gov.bc.ca")
# report["credentials"][0]["checks"] -> {structure, schema, temporal,
#   revocation, signature, disclosure}
```
Forged proofs, tampered disclosures, wrong-challenge replays, expired and
revoked credentials all fail these checks — exercised by the 28-test suite
(`tests/test_vc_layer.py`).

---

## 4️⃣ MOBI VID Capabilities ✅ (BUILT — 32 tests + 6 VIN-cipher)

`2_w3c-ssi-layer/mobi-vid/` layers MOBI VID on top of the canonical VC layer and
anchors each credential on-chain via **content-hash anchoring**
(keccak256 of the canonicalized signed VC → contract field). **No IPFS is
involved anywhere.** The registry contract is `MOBIVIDRegistryV2.sol`.

### MOBI VID I — Birth Certificate
`BirthCertificateIssuer.issue_birth_certificate(...)` (1) issues a
schema-enforced `VehicleBirthCertificate` VC, (2) computes its keccak256
content hash, and (3) registers the birth on-chain.

- **VIN privacy — salted hash:** only `sha256(vin || ":" || salt)` (32-byte
  random salt) reaches the chain; the salt is disclosed off-chain to parties
  that must link VIN → vehicle. The vehicle DID is `did:ethr:<chainId>:<addr>`,
  **not** `did:mobi:<VIN>`, so the identifier itself never leaks the VIN.
- **VIN encryption — AES-256-GCM** (replaced an earlier demo XOR): the 32-byte
  key is HKDF-SHA256-derived from a per-vehicle owner secret (salted by the VIN
  salt); the ciphertext is AEAD-bound to the on-chain `vinHash` via GCM
  associated data, so it cannot be transplanted onto another record. Neither VIN
  nor key ever reaches the chain. (6 dedicated cipher tests;
  `tests/test_vin_cipher.py`.)

```python
result = issuer.issue_birth_certificate(
    vehicle_identity=vehicle.address, vin="5YJ3E1EA0PF123456",
    make="Tesla", model="Model 3", year=2024,
    manufacturing_date="2024-01-15", first_owner=owner.address)
# -> verifiableCredential, vinSalt, vinHash, vinSecret, contentHash, gasUsed
```
`BirthCertificateVerifier.verify(...)` checks the VC pipeline **and** that
keccak256(VC) equals the on-chain `birthCertHash`, the (vin, salt) recomputes
the on-chain `vinHash`, and the VC issuer equals the on-chain manufacturer.

### MOBI VID II — Lifecycle Events
`LifecycleEventRecorder.record_event(...)` issues an event VC and anchors it
on-chain in one call. The enums mirror `MOBIVIDRegistryV2.sol` exactly:

**11 event types:** MAINTENANCE, REPAIR, ACCIDENT, RECALL, INSPECTION,
MODIFICATION, THEFT_REPORT, RECOVERY, INSURANCE_CLAIM, REGISTRATION,
DECOMMISSION. Types with a registered schema are issued strict; the rest are
still cryptographically signed and verifiable.

**Issuer roles (NONE + 8):** MANUFACTURER, DEALER, SERVICE_CENTER,
INSPECTION_STATION, GOVERNMENT_DMV, INSURANCE_COMPANY, POLICE, OWNER — the
contract gates which role may issue which event.

**On-chain multi-party attestation:** `attest_event(...)` produces an EIP-191
signature over a domain-separated digest
`keccak256(contract, chainId, vehicle, eventId)`; the contract recovers the
signer on-chain (**ecrecover**) and requires it to equal the attester, so
forged/replayed attestations revert. `VehicleHistoryAggregator` rebuilds a
fully verified history (anchor integrity + signature recovery + issuer
consistency) and includes an odometer-rollback fraud heuristic.

---

## 5️⃣ Lifecycle Use Cases ✅ (12/12 passing)

`cv2x-testbed/scripts/test_use_cases.py` runs 12 end-to-end scenarios with
**real cryptographic verification** and **computed** (not hardcoded) pass/fail;
the suite exits nonzero if any use case fails.

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

Forged and replayed credentials are demonstrated to **fail** within these flows,
not merely asserted.

---

## 6️⃣ CV2X / V2V Safety Messaging ✅

`cv2x-testbed/sumo/sumo_identity_integration.py --simulate` runs a 3-lane
highway V2V simulation broadcasting 10 Hz Basic Safety Messages, with **real
ECDSA (PKI baseline)** and **real W3C VC (SSI)** verification in the message
path. `run_v2v_stats.py` aggregates **N=30 seeded runs**.

**Measured verification latency — median [95% CI], ms:**

| Path | Warm verify | Cold verify |
|------|------------:|------------:|
| SSI (blockchain credential) | **0.165 [0.162, 0.168]** | 0.400 [0.392, 0.405] |
| PKI baseline | 0.102 [0.101, 0.104] | — |

Across the campaign: **1,650,318 verifications, 90 failures** — exactly the 3
injected attacks × 30 runs (all caught). **H3 SUPPORTED:** the warm SSI verify
sits ~600× under the 100 ms V2V budget.

**Caveats (stated in the results):** figures are pure identity-verification CPU
time — no radio/MAC/propagation/queueing; mobility is a mock kinematic model
(no SUMO binary required; real SUMO is optional/future); single warm,
uncontended core, so absolute latencies are hardware-dependent.

---

## 7️⃣ Comparison Framework ✅

`4_comparison-framework/` turns the raw measurements into thesis artifacts.

### Gas benchmark
`1_blockchain-identity/scripts/benchmark_gas.js` benchmarks all 9 standards +
MOBI-VID-V2 across 7 operations; `performance-metrics/run_gas_stats.py` reruns
N=30 and records determinism (`gas_benchmark_stats.json`).
`performance-metrics/generate_tables.py` emits the thesis **LaTeX** table
(`results/gas_comparison.tex`) and **CSV** (`gas_comparison.csv`).

### W3C compliance checker
`cv2x-testbed/scripts/w3c_compliance_checker.py` is an **executable** checker
(negative checks are first-class: forged/tampered/expired/unsupported inputs
must be rejected). Measured score **93.2%** (44 executed checks), CI-gated at
≥90% — **H2 SUPPORTED**. The 2 documented deviations are canonical JSON vs
URDNA2015 and the thesis-defined cryptosuite.

### Sepolia validation harness
`1_blockchain-identity/scripts/validate_sepolia.js` + `SEPOLIA_VALIDATION.md`
re-run the gas benchmark against public Sepolia to confirm the local numbers.
**Not yet executed** — it needs an RPC URL and a funded test key
(`results/sepolia_validation.json` is a placeholder until then).

---

## 8️⃣ Security Capabilities ✅ (two complementary lenses)

### Lens 1 — executable attack suite
`1_blockchain-identity/test/security/securityScenarios.test.js` runs Mocha
attack scenarios against the deployed contracts. The security matrix has **54
cells; 43/43 applicable cells DEFENDED** (11 are structurally N/A per standard),
CI-gated. Forged issuance, unauthorized state writes, unauthorized
delegate/claim installs, and unauthorized revocations all revert with the
expected reasons (`4_comparison-framework/security-analysis/`).

### Lens 2 — threat-matrix analysis
Adds properties the test suite cannot execute: Sybil economics, recovery
availability, and on-chain PII leakage. **Findings (H5):** no standard dominates
— security and performance trade off along a frontier; only **ERC-4337** has
genuine on-chain key recovery; **ERC-1155** (soulbound) uniquely resists
identity theft; the **MOBI VID** family is the only one that both hashes and
encrypts the VIN.

### Found-and-fixed result (honesty asset)
The audit found MOBI `attestEvent` was **storing** an attestation signature but
never verifying it (a forgery/replay gap). It now recovers the signer on-chain
(ecrecover) and reverts forged/replayed attestations. Cost moved
**121,110 → 192,718 gas**; the MOBI `Replay` security test now passes.

---

## 📊 Capability Matrix

| Capability | ERC-1056 | ERC-721 | ERC-725(xy) | ERC-735 | ERC-1155 | ERC-4337 | LSP8 | CVIN-Comb. | W3C VC | MOBI VID |
|------------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Identity creation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ✅ |
| Ownership transfer | ✅ | ✅ | ✅ | ✅ | soulbound | ✅ | ✅ | ✅ | N/A | ✅ |
| Key rotation / recovery | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ recovery | ✅ | ✅ | N/A | ✅ |
| On-chain claims | via hybrid | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ (VC) | ✅ |
| VIN privacy (hash+encrypt) | — | — | — | — | — | — | — | — | — | ✅ |
| W3C DID resolvable | ✅ | ✅ | ✅ | — | — | — | — | ✅ | — | ✅ |

---

## 🎯 What This System Can Do (Summary)

### ✅ Built and tested
1. Create & compare vehicle identities across **9 blockchain standards** with
   real, deterministic on-chain gas (N=30).
2. Resolve DIDs to W3C DID Core documents (**4 methods**).
3. **Issue / hold / verify W3C Verifiable Credentials** with selective
   disclosure and revocation (28 tests).
4. **MOBI VID I + II** with on-chain content-hash anchoring, on-chain
   attestation (ecrecover), and AES-256-GCM VIN encryption (32 + 6 tests).
5. Run **12 lifecycle use cases** end-to-end with real crypto (12/12).
6. Simulate **V2V** with real signature verification and measured latency.
7. Generate the comparison artifacts: gas benchmark (LaTeX/CSV), security
   matrix, and the executable **93.2%** W3C-compliance report.

### 🔜 Remaining
1. Public-testnet (**Sepolia**) validation run (harness ready; needs RPC + key).
2. Optional real-SUMO mobility (mock kinematics used today).
3. Thesis writing.

---

## 📈 Hypotheses Status

| # | Hypothesis | Status | Evidence |
|---|------------|--------|----------|
| H1 | Minimal standards ≥10× cheaper to create | **Supported** | ERC-1056/CVIN-Combined ~10× under ERC-721/725; ~33× total spread |
| H2 | ≥90% W3C compliance | **Supported** | 93.2% executable checker |
| H3 | Off-chain verify meets V2V budget | **Supported** | 0.165 ms warm SSI verify, ~600× margin |
| H4 | MOBI VID across backends | **Partial** | one backend measured |
| H5 | Hybrid on the security/perf frontier | **Supported** | CVIN-Combined |

---

**Status:** Living document — reflects the built system as of v0.9.0-dev.
**Maintainer:** Nikhil Prakash (UBC MASc thesis).
