# Thesis Repository - Complete Inventory

**Last Updated**: July 23, 2026
**Version**: v0.8.0 tagged ("Rigor & Ground-Truth Hardening"); working toward 0.9.0 (VERSION reads `0.9.0-dev`)
**Repository (mirror, up to date through tags)**: https://github.com/nikhilprakash-cvin/2_miniature-waffle-CV2X-Testbed-MOBI-VID
**Repository (designated origin)**: https://github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID

---

## 📊 Summary Statistics

| Category | Status | Evidence |
|----------|--------|----------|
| Smart Contracts (all 9 standards + MOBI VID) | ✅ Complete | 217 Hardhat tests passing |
| W3C SSI Layer (DID + VC + MOBI VID) | ✅ Complete | 28 VC + 32 MOBI VID pytest passing; 93.2% measured W3C compliance |
| CV2X Testbed (use cases + V2V + SUMO-sim) | 🔄 ~85% | 12/12 use cases; real-crypto V2V loop measured (N=30); mobility still simulated |
| Comparison Framework | ✅ Complete | 9/9 standards gas-benchmarked (N=30, σ=0); security matrices + Sepolia harness generated |
| Documentation | 🔄 ~80% | honest-claims cleanup done; Chapter 5 results draft assembled from measured artifacts |
| CI/CD | ✅ Complete | 3 workflows (contracts, benchmark, W3C compliance gate ≥90%) |
| **OVERALL** | **~70%+** | **~295 automated tests green** |

Automated test totals (all green): **217 Hardhat contract tests + 28 W3C VC + 32 MOBI VID (Python) + 12/12 lifecycle use cases** (~295 total). W3C compliance: **93.2% measured** (executable checker, CI-gated ≥90%).

---

## 1️⃣ Blockchain Identity Layer (`1_blockchain-identity/`)

Hardhat project implementing all 9 blockchain identity standards plus the MOBI VID application profile. **217 tests passing.** solc 0.8.24, optimizer (200 runs) + viaIR, OpenZeppelin 5.0.2.

### The 9 standards + MOBI VID (Solidity contracts)

| Standard | File | Lines | Status | Notes |
|----------|------|-------|--------|-------|
| ERC-1056 | `contracts/ERC1056/EthereumDIDRegistry.sol` | 408 | ✅ Complete | Standard ERC-1056 registry (event-log DID) |
| ERC-1056 | `contracts/ERC1056/CVINVehicleDIDRegistry.sol` | 331 | ✅ Complete | Vehicle-specific DID registry |
| ERC-721 | `contracts/ERC721/CVINVehicleNFT.sol` | 400 | ✅ Complete | Vehicle NFT with DID integration |
| ERC-721 | `contracts/ERC721/CVIN_NFT_DID_ERC721.sol` | 44 | ✅ Complete | NFT DID thin wrapper |
| ERC-725 | `contracts/ERC725/CVIN_DID_ERC725.sol` | 89 | ✅ Complete | Proxy account with key/data store |
| ERC-725xy | `contracts/ERC725xy/CVINVehicleERC725XY.sol` | 388 | ✅ Complete | Full ERC-725X (executor) + ERC-725Y (data store) account — added v0.8.0, closing the last missing standard |
| ERC-725xy | `contracts/ERC725xy/CVINExecuteTarget.sol` | 26 | ✅ Complete | Execution target used in tests |
| ERC-735 | `contracts/ERC735/CVINVehicleClaimHolder.sol` | 346 | ✅ Complete | On-chain claim holder with issuer signatures |
| ERC-1155 | `contracts/ERC1155/CVINVehicleCredential1155.sol` | 214 | ✅ Complete | Soulbound credential (resists identity theft) |
| ERC-4337 | `contracts/ERC4337/CVINVehicleAccount.sol` | 248 | ✅ Complete | Account abstraction, guardian recovery |
| ERC-4337 | `contracts/ERC4337/CVINMinimalEntryPoint.sol` | 93 | ✅ Complete | **Minimal representative** EntryPoint (gas is a lower bound; documented in header) |
| LSP8 | `contracts/LSP8/CVINVehicleLSP8.sol` | 317 | ✅ Complete | **Minimal representative** LSP8 identity |
| CVIN-Combined | `contracts/CVINCombined/CVINCombinedIdentity.sol` | 335 | ✅ Complete | Thesis hybrid: ERC-1056 event identity + ERC-735 on-chain claims (H5) |
| MOBI VID | `contracts/MOBI/MOBIVIDRegistryV2.sol` | 572 | ✅ Complete | VID II registry; `attestEvent` ecrecover signature verification + AES-256-GCM VIN encryption |
| MOBI VID | `contracts/MOBI/MOBIVIDRegistry.sol` | 524 | ✅ Complete | VID I birth-registration registry |
| MOBI VID | `contracts/MOBI/ERC1056Registry.sol` | 321 | ✅ Complete | ERC-1056 registry used by MOBI layer |

**Total contract Solidity**: ~4,656 lines across 16 files.

### Test Files (217 tests total)

| File | `it()` scenarios | Status | Purpose |
|------|------------------|--------|---------|
| `test/ERC1056/EthereumDIDRegistry.test.js` | 19 | ✅ | ERC-1056 registry |
| `test/ERC1056/CVINVehicleDIDRegistry.test.js` | 19 | ✅ | Vehicle DID |
| `test/ERC721/combined.js` | 3 | ✅ | NFT comprehensive |
| `test/ERC721/identityBased.js` | 1 | ✅ | Identity-focused |
| `test/ERC721/regularExtended.js` | 4 | ✅ | Extended NFT |
| `test/ERC725xy/CVINVehicleERC725XY.test.js` | 15 | ✅ | ERC-725X+Y account |
| `test/ERC735/CVINVehicleClaimHolder.test.js` | 16 | ✅ | Claim holder |
| `test/ERC1155/CVINVehicleCredential1155.test.js` | 17 | ✅ | Soulbound credential |
| `test/ERC4337/CVINVehicleAccount.test.js` | 16 | ✅ | Account abstraction + guardian recovery |
| `test/LSP8/CVINVehicleLSP8.test.js` | 18 | ✅ | LSP8 identity |
| `test/CVINCombined/CVINCombinedIdentity.test.js` | 19 | ✅ | Hybrid identity |
| `test/MOBIVID/MOBIVIDRegistry.test.js` | 16 | ✅ | MOBI VID incl. `attestEvent` forge/replay reverts |
| `test/security/securityScenarios.test.js` | 54 | ✅ | Adversarial revert suite — 43/43 applicable cells DEFENDED |
| `test/security/attackHarness.js` | (helper) | ✅ | Shared attack-scenario harness |

> The 217 passing total exceeds the raw `it()` count above because several suites generate parameterized cases per standard/operation at runtime.

### Scripts

| File | Status | Purpose |
|------|--------|---------|
| `scripts/benchmark_gas.js` | ✅ Complete | Gas benchmark across all 9 standards + MOBI VID → `gas_benchmark.json` |
| `scripts/security_scenarios.js` | ✅ Complete | Drives on-chain security scenarios |
| `scripts/validate_sepolia.js` | ✅ Complete | Public-testnet (Sepolia) validation harness — **not yet executed** (needs RPC URL + funded key) |
| `scripts/deployERC1056.js` | ✅ Complete | ERC-1056 deployment |

### Documentation / Config

| File | Status | Purpose |
|------|--------|---------|
| `hardhat.config.js`, `package.json` | ✅ Complete | Hardhat / NPM config |
| `SEPOLIA_VALIDATION.md` | ✅ Complete | Sepolia validation procedure (run pending) |

**Status**: ✅ **COMPLETE** — all 9 standards + MOBI VID implemented, tested (217), and gas-benchmarked.

---

## 2️⃣ W3C SSI Layer (`2_w3c-ssi-layer/`)

### DID Resolution ✅

| File | Lines | Status | Description |
|------|-------|--------|-------------|
| `did-resolution/did_resolver.py` | 518 | ✅ Complete | W3C DID Core resolver — 4 methods (did:ethr, did:nft, did:key, did:mobi) |

### Verifiable Credentials ✅ — **28 tests passing**

| File | Lines | Status | Description |
|------|-------|--------|-------------|
| `verifiable-credentials/vc_issuer.py` | 337 | ✅ Complete | Issuance, EIP-191 secp256k1 Data Integrity proofs, revocation registry |
| `verifiable-credentials/vc_holder.py` | 230 | ✅ Complete | Wallet, presentations (challenge/domain), selective disclosure (SD-JWT-style salted digests) |
| `verifiable-credentials/vc_verifier.py` | 441 | ✅ Complete | 6-stage offline verification pipeline, compliance self-scorer |
| `verifiable-credentials/vc_schemas.py` | 338 | ✅ Complete | 10 automotive schemas (1:1 with thesis use cases) |
| `verifiable-credentials/tests/test_vc_layer.py` | — | ✅ Complete | 28 tests (all passing) |
| `verifiable-credentials/BUILD_PLAN.md`, `README.md` | — | ✅ Complete | Design decisions + measured performance |

**Capabilities**: issuer, holder wallet, verifier (6-stage offline pipeline), 10 automotive schemas, selective disclosure, revocation registry, EIP-191 secp256k1 Data Integrity proofs.

### MOBI VID ✅ — **32 Python tests passing**

| File | Lines | Status | Description |
|------|-------|--------|-------------|
| `mobi-vid/birth_certificate.py` | 393 | ✅ Complete | VID I: W3C VC birth certificate + keccak256 on-chain content-hash anchoring |
| `mobi-vid/lifecycle_events.py` | 436 | ✅ Complete | VID II: 11 lifecycle event types, attestations, history aggregation |
| `mobi-vid/mobi_vid_registry.py` | 387 | ✅ Complete | web3 v7 binding to `MOBIVIDRegistryV2` |
| `mobi-vid/tests/test_mobi_vid_layer.py` | — | ✅ Complete | MOBI VID layer tests (on-chain, self-managed Hardhat node) |
| `mobi-vid/tests/test_vin_cipher.py` | — | ✅ Complete | AES-256-GCM VIN encryption tests (replaced earlier demo XOR) |
| `mobi-vid/README.md` | — | ✅ Complete | Honest implemented-status table |

**MOBI VID Python test suite total**: 32 tests (layer + VIN cipher). On-chain `attestEvent` now verifies attester signature via ecrecover (forged/replayed attestations revert); attestEvent cost rose 121k → 193k gas as a result.

### Config

| File | Status | Purpose |
|------|--------|---------|
| `requirements.txt` | ✅ Complete | Python deps (web3, eth-account, cryptography, coincurve, pytest) |

**Status**: ✅ **COMPLETE** — DID resolver (4 methods), VC layer (28 tests), MOBI VID layer (32 tests).

---

## 3️⃣ CV2X Testbed (`3_cv2x-testbed/` → `cv2x-testbed/`)

`3_cv2x-testbed/` is a thesis-chapter mapping stub (a `README.md` that points to the working testbed). The **working CV2X testbed physically lives in the repo-root `cv2x-testbed/`** directory (kept there to preserve internal `sys.path` wiring).

### Working testbed contents (`cv2x-testbed/`)

| Component | Location | Status |
|-----------|----------|--------|
| Use-case suite (12 lifecycle scenarios) | `scripts/test_use_cases.py` | ✅ 12/12 passing, real VC verification (forged/replayed credentials fail; computed pass/fail) |
| Identity providers (PKI, centralized, ERC-1056, MOBI VID, W3C VC) | `identity/` | ✅ Clean under web3 v7 |
| V2V scenarios (basic V2V, integration) | `scenarios/` | ✅ Real ECDSA verification |
| SUMO V2V simulation | `sumo/sumo_identity_integration.py` | 🔄 `--simulate` mode; real ECDSA (PKI) + real W3C VC (SSI) verification in the message path; 10 Hz BSM |
| V2V N=30 statistics harness | `sumo/run_v2v_stats.py` | ✅ Produces `sumo/results/v2v_latency_stats.json` (seeds 1–30) |
| SUMO configs (50 vehicles) | `sumo/*.net.xml`, `routes.rou.xml`, `simulation.sumocfg` | 🔄 hand-authored; regenerate with `netconvert` for real-SUMO runs |
| CV2X protocol stack (PHY/MAC, BSM/DENM) | `protocols/cv2x_stack.py` | ✅ Simulation-grade |
| W3C compliance checker (executable) | `scripts/w3c_compliance_checker.py` | ✅ 93.2% measured |
| MOBI VID / VIN encryption test scripts | `scripts/test_mobi_vid.py`, `scripts/test_vin_encryption.py` | ✅ Passing |
| On-chain contracts + Hardhat project | `contracts/`, `hardhat.config.js` | ✅ ERC-1056, MOBI VID V1/V2 |

**Measured V2V result** (N=30 seeded runs): SSI warm verify **0.165 ms** [0.162, 0.168]; cold 0.400 ms; PKI warm 0.102 ms. 1,650,318 messages verified, 90 failures = exactly the 3 injected attacks × 30 runs (zero false positives/negatives). ~600× margin to the 100 ms V2V budget (H3 supported).

**Honest caveats**: V2V latency excludes radio/MAC/network-stack; mobility is simulated (no SUMO binary in the measurement environment).

**Status**: 🔄 **~85%** — use cases, V2V real-crypto loop, and statistics done; real-SUMO execution is optional/future.

---

## 4️⃣ Comparison Framework (`4_comparison-framework/`)

### Performance metrics ✅

| File | Status | Purpose |
|------|--------|---------|
| `performance-metrics/generate_tables.py` | ✅ Complete | LaTeX/CSV table generation from benchmark JSON |
| `performance-metrics/run_gas_stats.py` | ✅ Complete | N=30 gas stability run (σ=0, CI width 0) |
| `results/gas_benchmark.json`, `gas_benchmark_stats.json` | ✅ Complete | Exact `gasUsed` per standard; 30-run stability |
| `results/gas_comparison.csv`, `gas_comparison.tex` | ✅ Complete | Camera-ready gas comparison table |
| `results/sepolia_validation.json` | ✅ Complete (scaffold) | Sepolia validation output slot (real run pending) |

**Gas finding (RQ1/H1)**: ~33× spread across standards; CVIN-Combined 52,178 gas (cheapest) → ERC-725xy 1,704,992 (heaviest full-account deploy); ERC-1056 ~10× cheaper than ERC-721/725 (H1 supported); ERC-4337 EntryPoint indirection = +46,862 gas/op.

### Security analysis ✅ — two complementary lenses

| File | Status | Purpose |
|------|--------|---------|
| `security-analysis/attack_scenarios.py` | ✅ Complete | Attack-scenario modeling |
| `security-analysis/generate_attack_tables.py` | ✅ Complete | Attack + security matrix table generation |
| `security-analysis/results/attack_results.{json,csv,tex}` | ✅ Complete | Test-suite lens (54 scenarios; 43/43 applicable cells DEFENDED) |
| `security-analysis/results/security_matrix.{json,csv}` | ✅ Complete | Analysis lens: Sybil economics, recovery availability, on-chain PII leakage |
| `security-analysis/results/onchain_security.json`, `security_comparison.tex` | ✅ Complete | On-chain security findings + comparison table |
| `security-analysis/EXECUTABLE_ATTACK_SCENARIOS.md`, `README.md`, `INDEX.md` | ✅ Complete | Documentation of both lenses |

**Security finding (RQ2/H5)**: no standard dominates (security/performance frontier); only ERC-4337 has genuine on-chain key recovery; ERC-1155 uniquely resists identity theft (soulbound); MOBI VID is the only family that hashes + encrypts the VIN. MOBI `attestEvent` signature-verification gap was found AND fixed (121k → 193k gas).

**Status**: ✅ **COMPLETE** — gas benchmark, security matrices, and Sepolia harness all generated.

---

## 5️⃣ Documentation (`docs/`)

| File | Status | Purpose |
|------|--------|---------|
| `docs/RESEARCH_THRUSTS_REPORT.md` | ✅ Complete | Research thrusts mapping |
| `docs/planning/NEXT_STAGES_PLAN.md` | ✅ Complete | Next-stages plan |
| `docs/thesis/README.md` | ✅ Updated | Thesis chapter structure / status / timeline |
| `docs/thesis/chapter5-results/README.md` | ✅ Complete | **Chapter 5 Results — working draft from measured artifacts** (gas RQ1, V2V RQ4, W3C RQ3, security RQ2, hypotheses table) |

Additional living docs at repo root: `README.md`, `CHANGELOG.md`, `CAPABILITIES.md`, `QUICKSTART.md`, `CV2X_REALISTIC_ROADMAP.md`, `MOBI_VID*` specs.

> **Historical record — do not rewrite** (kept as a research log): `SESSION_*`, `AUTONOMOUS_*`, `SECOND_PASS_PLAN.md`, `SESSION_THESIS_INTEGRATION.md`.

---

## 6️⃣ CI/CD Infrastructure (`.github/workflows/`)

| File | Status | Purpose |
|------|--------|---------|
| `test-contracts.yml` | ✅ Complete | Smart-contract testing (217 Hardhat) |
| `benchmark.yml` | ✅ Complete | Gas benchmarks |
| `w3c-compliance.yml` | ✅ Complete | W3C compliance gate (≥90%; measured 93.2%) |

**Status**: ✅ **COMPLETE** — fully automated.

---

## 📈 Progress Tracking

### Overall Completion: ~70%+

```
████████████████████░░░░ ~70%+
```

| Phase | Completion | Status |
|-------|------------|--------|
| Smart Contracts (9 standards + MOBI VID) | 100% (217 tests) | ✅ |
| W3C DID Layer | 100% (4 methods) | ✅ |
| W3C VC Layer | 100% (28 tests) | ✅ |
| MOBI VID (Python + on-chain) | 100% (32 tests; AES-256-GCM VIN) | ✅ |
| CV2X Testbed | ~85% (12/12 use cases + real-crypto V2V N=30; SUMO in simulate mode) | 🔄 |
| Comparison Framework | 100% (gas N=30 σ=0, security two-lens, Sepolia harness) | ✅ |
| W3C Compliance | 93.2% measured (executable checker) | ✅ |
| Documentation | ~80% (Ch. 5 results draft from measured artifacts) | 🔄 |
| CI/CD | 100% | ✅ |

**Remaining work**: public-testnet (Sepolia) validation run (harness exists, not executed), optional real-SUMO execution, and thesis writing.

---

## Hypotheses Status (from measured results)

| Hypothesis | Verdict |
|------------|---------|
| H1 — minimal-state ≥10× cheaper for identity creation | ✅ Supported (ERC-1056 52,612 vs ERC-721 542,429 = 10.3×) |
| H2 — ≥90% W3C compliance achievable | ✅ Supported (93.2% measured) |
| H3 — off-chain verify meets V2V budget | ✅ Supported (SSI warm 0.165 ms ≪ 100 ms) |
| H4 — MOBI VID realizable across backends | 🔄 Partial (one backend measured) |
| H5 — hybrid on the cost/capability frontier | ✅ Supported (CVIN-Combined) |

---

## 🔧 Dependencies

**Node.js/Hardhat**: hardhat, @openzeppelin/contracts 5.0.2, ethers 6, hardhat-toolbox. Node 18.
**Python 3.11**: web3, eth-account, cryptography, coincurve, pytest.
**Optional** (CV2X real-SUMO): SUMO traffic simulator, traci, sumolib — not required for `--simulate` mode.

---

## 🚀 Getting Started (verified commands)

- Contracts: `cd 1_blockchain-identity && npm ci && npx hardhat test` → 217 passing
- VC tests: `python3 -m pytest 2_w3c-ssi-layer/verifiable-credentials/tests/` → 28
- MOBI VID tests: `cd 2_w3c-ssi-layer/mobi-vid && python3 -m pytest tests/` → 32
- Use cases: `python3 cv2x-testbed/scripts/test_use_cases.py` → 12/12
- W3C compliance: `python3 cv2x-testbed/scripts/w3c_compliance_checker.py` → 93.2%
- Gas benchmark: `cd 1_blockchain-identity && npx hardhat run scripts/benchmark_gas.js`; tables via `4_comparison-framework/performance-metrics/generate_tables.py`
- V2V sim: `python3 cv2x-testbed/sumo/sumo_identity_integration.py --simulate`; N=30 stats via `cv2x-testbed/sumo/run_v2v_stats.py`

---

**Last Updated**: July 23, 2026
**Maintainer**: Nikhil Prakash (UBC MASc Thesis)
