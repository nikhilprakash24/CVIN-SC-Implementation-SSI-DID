# Self-Sovereign Identity for Connected and Autonomous Vehicles
## A Comparative Analysis of Blockchain-Based Identity Standards

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![UBC](https://img.shields.io/badge/Institution-UBC-blue.svg)](https://www.ubc.ca/)
[![Thesis](https://img.shields.io/badge/Type-MASc%20Thesis-green.svg)](https://www.ubc.ca/)

> **Status:** v0.8.0 ("Rigor & Ground-Truth Hardening"), working toward 0.9.0. ~295 automated tests green (217 Hardhat + 28 W3C VC + 32 MOBI VID + 6 VIN-cipher + 12/12 lifecycle use cases). **W3C compliance 93.2%** (executable checker, CI-gated at ≥90%). All implementation phases built and tested; remaining work is public-testnet (Sepolia) validation, optional real-SUMO, and thesis writing.

---

## 📚 Thesis Overview

**Title**: Comparative Analysis of Self-Sovereign Identity Systems for Connected and Autonomous Vehicles

**Author**: Nikhil Prakash  
**Institution**: University of British Columbia (UBC)  
**Department**: Electrical and Computer Engineering  
**Research Cluster**: Blockchain Interdisciplinary Research Cluster  
**Degree**: Master of Applied Science (MASc)  
**Year**: 2025-2026

### Research Questions

1. **Performance (RQ1)**: How do different blockchain identity standards compare in terms of transaction (gas) cost for vehicle identity management?

2. **Security (RQ2)**: Which identity architecture provides the strongest security guarantees for V2X (Vehicle-to-Everything) communication?

3. **Compliance (RQ3)**: Can blockchain-based identity systems achieve W3C Self-Sovereign Identity compliance while meeting automotive industry requirements (MOBI VID)?

4. **Practical Feasibility (RQ4)**: Are blockchain identity systems viable for real-time safety-critical V2V (Vehicle-to-Vehicle) communication?

### Hypotheses

- **H1** — Minimal identity standards (e.g. ERC-1056) are at least ~10× cheaper to create than heavyweight account standards. **SUPPORTED.**
- **H2** — A blockchain identity layer can reach ≥90% W3C compliance. **SUPPORTED (93.2% measured).**
- **H3** — Off-chain credential verification meets the real-time V2V latency budget (100 ms). **SUPPORTED (0.165 ms warm).**
- **H4** — MOBI VID generalizes across identity backends. **SUPPORTED** (5-backend realization sweep; birth + lifecycle native on all, multi-party attestation native on claim-capable backends — a documented fidelity gradient).
- **H5** — A hybrid design can sit on the security/performance frontier. **SUPPORTED (CVIN-Combined).**

Overarching hypothesis: lightweight blockchain identity standards can provide sufficient security and W3C compliance for vehicle identity management while maintaining performance suitable for real-time V2V safety applications, offering a viable alternative to centralized PKI systems.

---

## 🏗️ Repository Structure

```
CVIN-SC-Implementation-SSI-DID/
│
├── 1_blockchain-identity/              # Hardhat project — 9 standards + MOBI VID
│   ├── contracts/                      # CVINCombined, ERC1056, ERC1155, ERC4337,
│   │                                   #   ERC721, ERC725, ERC725xy, ERC735, LSP8, MOBI
│   ├── test/                           # 217 contract tests (per-standard + security/)
│   ├── scripts/                        # benchmark_gas.js, validate_sepolia.js, deploy, security
│   └── SEPOLIA_VALIDATION.md           # public-testnet validation harness (not yet run)
│
├── 2_w3c-ssi-layer/                    # W3C SSI layer
│   ├── did-resolution/                 # W3C DID resolver (did:ethr, did:nft, did:key, did:mobi)
│   ├── verifiable-credentials/         # VC issuer / holder / verifier (28 tests)
│   └── mobi-vid/                       # MOBI VID I + VID II Python layer (32 tests)
│
├── 3_cv2x-testbed/                     # Thesis-chapter scaffolding
│   └── README.md                       #   maps to the working testbed in cv2x-testbed/
│
├── cv2x-testbed/                       # Working CV2X testbed
│   ├── identity/                       # identity providers
│   ├── scripts/                        # 12 lifecycle use cases, W3C compliance checker
│   ├── sumo/                           # V2V simulation (real ECDSA + real VC verify)
│   ├── protocols/                      # protocol stack
│   └── contracts/                      # testbed contracts
│
├── 4_comparison-framework/             # Comparative analysis (real data)
│   ├── performance-metrics/            # gas/latency table + stats generators
│   ├── security-analysis/             # attack scenarios (two lenses), threat matrix
│   └── results/                        # gas_benchmark.json/.csv/.tex, stats, sepolia stub
│
├── docs/                               # Documentation
│   ├── RESEARCH_THRUSTS_REPORT.md
│   ├── planning/NEXT_STAGES_PLAN.md
│   └── thesis/                         # chapter5-results (measured), thesis README
│
└── README.md                           # This file
```

---

## 🔬 Research Methodology

### Phase 1 — Blockchain Identity Implementation (✅ Complete)
All 9 standards implemented as Hardhat contracts and benchmarked on-chain (hardhat-local).

- ✅ Smart contracts for all 9 standards + MOBI VID
- ✅ 217-test Hardhat suite (per-standard + `test/security/`)
- ✅ Gas benchmark (`scripts/benchmark_gas.js`), N=30 deterministic runs
- ✅ Sepolia validation harness authored (`scripts/validate_sepolia.js`) — run pending

### Phase 2 — W3C SSI Compliance (✅ Complete)
- ✅ W3C DID resolver — 4 methods (`did:ethr`, `did:nft`, `did:key`, `did:mobi`)
- ✅ Verifiable Credentials — issuer, holder wallet, verifier (6-stage offline pipeline), 10 automotive schemas, selective disclosure (SD-JWT-style salted digests), revocation registry, EIP-191 secp256k1 Data Integrity proofs (28 tests)
- ✅ MOBI VID I (birth certificate: W3C VC + on-chain content-hash anchoring) and VID II (11 lifecycle event types with on-chain `attestEvent` ecrecover verification and AES-256-GCM VIN encryption) — 32 tests
- ✅ Compliance checker (executable) — **93.2% measured**, CI-gated ≥90%

### Phase 3 — CV2X Testbed Integration (✅ Complete)
- ✅ 12 end-to-end lifecycle use cases with REAL cryptographic verification (forged/replayed credentials fail; pass/fail is computed, not hardcoded) — 12/12
- ✅ CV2X V2V: SUMO simulation with real ECDSA (PKI baseline) and real W3C VC (SSI) verification in the message path; 10 Hz BSM; injected attacks caught
- ✅ Security suites (Mocha attack scenarios + analysis)

### Phase 4 — Comparative Analysis (✅ Complete)
- ✅ Gas benchmark across all 9 standards + MOBI VID V2 (real measured data)
- ✅ V2V latency study, N=30 seeded runs with confidence intervals
- ✅ Security analysis — two complementary lenses (test suite + threat matrix)
- ✅ Table/figure generators (JSON/CSV/LaTeX) feeding the results chapter

### Phase 5 — Thesis Writing (🔄 In Progress)
- 🔄 Chapter 5 (Results) measured-data draft in `docs/thesis/chapter5-results/`
- 🔄 Remaining: full write-up, discussion, conclusions
- ⏳ Optional/future: public-testnet (Sepolia) validation run; real-SUMO binary run

---

## 📊 Key Results (Measured)

All numbers below are measured from the repository. Gas is **Hardhat-local**, solc 0.8.24, OpenZeppelin 5.0.2 — deterministic and verified byte-identical across N=30 runs (CI width 0).

### Gas — create identity (RQ1 / H1)

| Standard | Create-identity gas |
|---|---:|
| CVIN-Combined | 52,178 |
| ERC-1056 | 52,612 |
| ERC-1155 | 103,905 |
| LSP8 *(representative)* | 149,352 |
| MOBI-VID-V2 *(application profile)* | 298,923 |
| ERC-725 | 528,647 |
| ERC-721 | 542,429 |
| ERC-4337 *(representative EntryPoint)* | 768,204 |
| ERC-735 | 1,404,108 |
| ERC-725xy | 1,704,992 |

**Key finding:** ~33× spread across standards; ERC-1056 is ~10× cheaper than ERC-721/ERC-725 (**H1 supported**). The ERC-4337 EntryPoint indirection adds +46,862 gas/op. MOBI VID V2 is measured alongside as an application profile, not as one of the 9 base standards.

### V2V latency (RQ4 / H3) — N=30 seeded runs, median [95% CI], ms

| Path | Median latency (ms) |
|---|---|
| SSI (blockchain credential), warm verify | **0.165** [0.162, 0.168] |
| SSI, cold (full VC verify) | 0.400 [0.392, 0.405] |
| PKI baseline, warm | 0.102 [0.101, 0.104] |

1.65M verifications; 90 failures = exactly the 3 injected attacks × 30 runs. **H3 supported** — roughly a 600× margin to the 100 ms V2V budget. *Caveat: excludes radio/MAC/network-stack latency; mobility is simulated (no SUMO binary required).*

### Security (RQ2 / H5) — two complementary lenses

- **Lens 1 (test suite, `1_blockchain-identity/test/security/`)**: 54 Mocha attack scenarios; **43/43 applicable cells DEFENDED**; CI-gated.
- **Lens 2 (analysis)**: threat matrix adding Sybil economics, recovery availability, and on-chain PII leakage.

Findings: no standard dominates (a security/performance frontier — **H5**); only ERC-4337 offers genuine on-chain key recovery; ERC-1155 uniquely resists identity theft (soulbound); MOBI VID is the only family that both hashes and encrypts the VIN. A MOBI `attestEvent` signature-verification gap was found **and fixed** (121k → 193k gas; forged/replayed attestations now revert).

### W3C compliance (RQ3 / H2)

**93.2% measured** across 44 executed checks, with 2 documented deviations (canonical JSON vs URDNA2015; a thesis-defined cryptosuite). **H2 supported.**

### Hypotheses status

| Hypothesis | Status |
|---|---|
| H1 — minimal ≥10× cheaper | ✅ Supported |
| H2 — ≥90% W3C compliance | ✅ Supported (93.2%) |
| H3 — off-chain verify meets V2V budget | ✅ Supported (0.165 ms warm) |
| H4 — MOBI VID across backends | ✅ Supported (5-backend sweep; fidelity gradient) |
| H5 — hybrid on the frontier | ✅ Supported (CVIN-Combined) |

---

## 🧩 The 9 Standards Benchmarked

ERC-1056, ERC-721, ERC-725, **ERC-725xy** (full ERC-725X+Y account; added in v0.8.0), ERC-735, ERC-1155, ERC-4337 (minimal representative EntryPoint + account, guardian recovery), LSP8 (minimal representative), and **CVIN-Combined** (the thesis's own ERC-1056 + ERC-735 hybrid). MOBI VID V2 is measured alongside as an application profile.

**Honesty note:** the ERC-4337 EntryPoint and LSP8 are deliberately minimal research implementations (documented in their contract headers); their gas figures are lower bounds, not production-representative.

---

## 🚀 Getting Started

### Prerequisites

- **Node.js 18** and npm
- **Python 3.11**
- Python packages: `web3`, `eth-account`, `cryptography`, `pytest`, `coincurve`
- SUMO binary is **not** required — the V2V study runs in `--simulate` mode (real SUMO is optional/future)

### Smart-contract tests (217 passing)

```bash
cd 1_blockchain-identity
npm ci
npx hardhat test
```

### W3C SSI layer tests

```bash
# Verifiable Credentials (28 tests)
python3 -m pytest 2_w3c-ssi-layer/verifiable-credentials/tests/

# MOBI VID I + II (32 tests)
cd 2_w3c-ssi-layer/mobi-vid && python3 -m pytest tests/
```

### Lifecycle use cases & W3C compliance

```bash
# 12 end-to-end lifecycle use cases (12/12)
python3 cv2x-testbed/scripts/test_use_cases.py

# Executable W3C compliance checker (reports 93.2%)
python3 cv2x-testbed/scripts/w3c_compliance_checker.py
```

### Gas benchmark & result tables

```bash
cd 1_blockchain-identity
npx hardhat run scripts/benchmark_gas.js
# Regenerate comparison tables (JSON/CSV/LaTeX):
python3 4_comparison-framework/performance-metrics/generate_tables.py
```

### V2V simulation & latency stats

```bash
# V2V simulation (real ECDSA + real VC verification)
python3 cv2x-testbed/sumo/sumo_identity_integration.py --simulate

# N=30 latency statistics with confidence intervals
python3 cv2x-testbed/sumo/run_v2v_stats.py
```

---

## ⚠️ Scope & Honesty Caveats

- **Gas is Hardhat-local and deterministic.** A public-testnet (Sepolia) validation harness exists (`1_blockchain-identity/scripts/validate_sepolia.js`, `1_blockchain-identity/SEPOLIA_VALIDATION.md`) but the real run requires an RPC URL and a funded test key and has **not yet been executed**.
- **V2V latency excludes the network stack** (radio/MAC/PHY); mobility is **simulated** — no SUMO binary is invoked.
- **ERC-4337 EntryPoint and LSP8 are minimal representative implementations**; their gas figures are lower bounds.
- **VIN-cipher key distribution / HSM custody** is out of scope for the testbed.

---

## 📖 Documentation

### Standards & specifications referenced

1. **W3C DID Core v1.0**: https://www.w3.org/TR/did-core/
2. **W3C Verifiable Credentials Data Model**: https://www.w3.org/TR/vc-data-model-2.0/
3. **MOBI VID Specification**: https://dlt.mobi/vid/
4. **ERC-1056**: Lightweight (ethr) DID standard
5. **IEEE 1609.2**: V2X Security Services

### Key in-repo documents

- `docs/RESEARCH_THRUSTS_REPORT.md` — research thrusts overview
- `docs/planning/NEXT_STAGES_PLAN.md` — remaining-work plan
- `docs/thesis/chapter5-results/` — measured-results draft (Chapter 5)
- `1_blockchain-identity/CVIN-SSI-ARCHITECTURE.md` — system architecture
- `1_blockchain-identity/SEPOLIA_VALIDATION.md` — public-testnet validation harness
- `4_comparison-framework/security-analysis/` — executable attack scenarios & threat matrix
- `CHANGELOG.md` — version history (current: v0.8.0, working toward 0.9.0)

---

## 🎯 Lifecycle Use Cases Implemented

12 end-to-end lifecycle use cases run with **real** cryptographic verification (forged and replayed credentials fail; pass/fail is computed). They cover vehicle birth registration, maintenance, ownership transfer, insurance, recall, cross-border import, fleet management, emissions/compliance, theft & recovery, and autonomous-vehicle data sharing. Each exercises multi-party interactions, VC issuance/verification, selective disclosure, and an auditable trail.

```bash
python3 cv2x-testbed/scripts/test_use_cases.py   # 12/12
```

---

## 📈 Research Contributions

1. **Comprehensive on-chain comparison** of 9 blockchain identity standards for automotive identity, with measured gas, latency, and security data.
2. **Real-time V2V integration** with blockchain identity verification in the message path (real ECDSA and real W3C VC).
3. **MOBI VID + W3C bridge** — automotive lifecycle identity expressed as W3C Verifiable Credentials.
4. **Hybrid architecture (CVIN-Combined)** combining ERC-1056 + ERC-735 on the security/performance frontier.
5. **Open, reproducible testbed** with CI-gated tests and an executable compliance checker.

---

## 🤝 Contributing

This is active thesis research. For questions or collaboration:
- 📧 Email: nikhil.prakash1995@gmail.com

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

**Academic Use**: Please cite this work if used in academic publications:

```bibtex
@mastersthesis{prakash2026ssi,
  author = {Prakash, Nikhil},
  title = {Comparative Analysis of Self-Sovereign Identity Systems for Connected and Autonomous Vehicles},
  school = {University of British Columbia},
  year = {2026},
  type = {Master's Thesis},
  department = {Electrical and Computer Engineering}
}
```

---

## 🙏 Acknowledgments

- UBC Blockchain Interdisciplinary Research Cluster
- MOBI (Mobility Open Blockchain Initiative)
- W3C DID & VC Working Groups

---

<div align="center">

**🎓 UBC ECE Department | 🔗 Blockchain Research Cluster | 🚗 MOBI VID**

*Building the future of vehicular identity*

</div>
