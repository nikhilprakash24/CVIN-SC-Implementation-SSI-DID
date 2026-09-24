# Source Register

The master provenance index for the thesis: every external standard, tool,
prior-work input, and internal measured-data artifact the work draws on, with its
role and where it is used in the repository. Each significant source also has an
individual published artifact — see `docs/ARTIFACTS_MANIFEST.md`.

**Secrets note.** The repository contains **no live credentials**. The only key
material present is the set of **canonical, publicly-documented Hardhat/Anvil test
account private keys** (e.g. account #0 `0xac0974…f2ff80`) used by tests in
`2_w3c-ssi-layer/mobi-vid/` and `cv2x-testbed/identity/`; these are not live keys.
`1_blockchain-identity/.env.example` holds placeholders only. A real `.env` must
never be committed.

---

## 1. Blockchain identity standards (the comparison substrates)

| Source | Reference | Role in thesis | Repo location |
|---|---|---|---|
| **ERC-721** | eips.ethereum.org/EIPS/eip-721 | NFT-based vehicle identity | `1_blockchain-identity/contracts/ERC721/CVINVehicleNFT.sol` |
| **ERC-725** | eips.ethereum.org/EIPS/eip-725 | Proxy-account key/data identity | `contracts/ERC725/CVIN_DID_ERC725.sol` |
| **ERC-725xy** | ERC-725 (X executor + Y data store) | Full smart-account identity (added v0.8.0) | `contracts/ERC725xy/CVINVehicleERC725XY.sol` |
| **ERC-735** | Claim Holder (ERC-735 draft) | On-chain verifiable claims | `contracts/ERC735/CVINVehicleClaimHolder.sol` |
| **ERC-1056** | eips.ethereum.org/EIPS/eip-1056 | Lightweight `did:ethr`; the H1 minimal baseline | `contracts/ERC1056/EthereumDIDRegistry.sol` |
| **ERC-1155** | eips.ethereum.org/EIPS/eip-1155 | Soulbound multi-token credentials | `contracts/ERC1155/CVINVehicleCredential1155.sol` |
| **ERC-4337** | eips.ethereum.org/EIPS/eip-4337 | Account abstraction + guardian recovery (minimal representative) | `contracts/ERC4337/CVINVehicleAccount.sol`, `CVINMinimalEntryPoint.sol` |
| **LSP8** | LUKSO LSP8 Identifiable Digital Asset | Identifiable-asset identity (minimal representative) | `contracts/LSP8/CVINVehicleLSP8.sol` |
| **CVIN-Combined** | *this thesis* (ERC-1056 + ERC-735 hybrid) | The researcher's hybrid; H5 | `contracts/CVINCombined/CVINCombinedIdentity.sol` |
| **EIP-191** | eips.ethereum.org/EIPS/eip-191 | secp256k1 message signing for VC Data Integrity proofs and `attestEvent` | VC layer + `MOBIVIDRegistryV2.sol` |
| **EIP-155** | eips.ethereum.org/EIPS/eip-155 | Chain-id in `blockchainAccountId` / replay-domain separation | DID docs, `attestEvent` digest |

> MOBI-VID-V2 (`contracts/MOBI/MOBIVIDRegistryV2.sol`) is an **application profile**
> measured alongside the nine standards, not one of them.

## 2. W3C standards

| Source | Reference | Role | Repo location |
|---|---|---|---|
| **W3C DID Core v1.0** | w3.org/TR/did-core/ | DID document model; resolver conformance (measured 93.3%) | `2_w3c-ssi-layer/did-resolution/did_resolver.py` |
| **W3C Verifiable Credentials Data Model v2.0** | w3.org/TR/vc-data-model-2.0/ | VC structure, proofs, presentations (measured 93.1%) | `2_w3c-ssi-layer/verifiable-credentials/` |

## 3. Industry & V2X standards

| Source | Reference | Role | Repo location |
|---|---|---|---|
| **MOBI VID I** (Vehicle Birth Certificate) | MOBI Vehicle Identity | Birth-certificate credential model | `2_w3c-ssi-layer/mobi-vid/birth_certificate.py` |
| **MOBI VID II** (Lifecycle Events, 11 types) | MOBI Vehicle Identity | Lifecycle-event model + attestation | `2_w3c-ssi-layer/mobi-vid/lifecycle_events.py` |
| **IEEE 1609.2** | V2X security services | PKI baseline for the V2V latency comparison | `cv2x-testbed/identity/` (PKI provider) |
| **SAE J2735** | V2X message set (BSM/DENM) | V2V message model referenced in the testbed | `cv2x-testbed/` |

## 4. Toolchain & libraries

| Tool | Version | Role |
|---|---|---|
| **Hardhat** | ^2.19 | Solidity compile/test, gas benchmark harness |
| **OpenZeppelin Contracts** | 5.0.2 | Base ERC implementations; ECDSA (EIP-2 low-s) |
| **ethers.js** | ^6.10 | JS contract interaction (v6) |
| **SUMO** | (binary; `--simulate` fallback) | V2V traffic simulation (real binary optional/future) |
| **web3.py** | 6.11 | Python chain providers |
| **eth-account / eth-keys** | 0.10 / 0.4 | Key & signature handling |
| **coincurve** | — | native secp256k1 sign/recover (V2V perf) |
| **cryptography** | 41.0.7 | AES-256-GCM VIN cipher, HKDF |
| **pytest**, **numpy/scipy/pandas/matplotlib/seaborn/plotly** | — | Python tests + data/plotting |

## 5. Prior work & external references

| Source | Role |
|---|---|
| **CVIN-ID-SCs** (researcher's earlier Truffle/Ganache repo) | Origin of the smart-contract groundwork; restructured into `1_blockchain-identity/` |
| GitHub — `nikhilprakash-cvin/2_miniature-waffle-CV2X-Testbed-MOBI-VID` | Up-to-date mirror (`github` remote) |
| GitHub — `nikhilprakash24/CVIN-SC-Implementation-SSI-DID` | Designated `origin` (currently push-blocked; stale) |
| `ubc-ece/ubc-thesis-template` | UBC LaTeX thesis template |

## 6. Internal measured-data artifacts (the "sources" for Chapter 5)

| Artifact | Produces | Chapter 5 §
|---|---|---|
| `4_comparison-framework/results/gas_benchmark.json` (+ `_stats.json`) | 9-standard gas; N=30 determinism | §5.2 |
| `4_comparison-framework/results/mobi_vid_backends.{json,csv,tex}` | H4 5-backend gas × fidelity | §5.3.1 |
| `4_comparison-framework/security-analysis/results/security_matrix.json`, `onchain_security.json`, `attack_results.{json,csv,tex}` | Two-lens security | §5.6 |
| `cv2x-testbed/sumo/results/v2v_latency_stats.json` (+ `v2v_latency.json`) | V2V latency N=30 + CIs | §5.4 |
| `4_comparison-framework/results/w3c_compliance.json` (snapshot of `w3c_compliance_checker.py`) | 93.2% W3C compliance | §5.5 |

> **Caveat:** `4_comparison-framework/results/sepolia_validation.json` is a **local
> dry-run** (chainId 31337), not a real public-testnet run. A real Sepolia witness
> is pending RPC + funded-key access.
