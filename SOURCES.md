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
| `4_comparison-framework/results/w3c_compliance.json` (snapshot of `w3c_compliance_checker.py`) | 94.3 % W3C compliance (register #4) | §5.5 |

> **Caveat:** `4_comparison-framework/results/sepolia_validation.json` is a **local
> dry-run** (chainId 31337), not a real public-testnet run. A real Sepolia witness
> is pending RPC + funded-key access.

## 7. Literature added for chapter 2 (verified 2026-10-22)

Each row was checked on 2026-10-22 against its DOI metadata record (Crossref), which matched the
title, authors, year and venue given here. Chapter 2 cites these as `[Key, S7]`. The researcher's
own reference set may extend or replace them.

| Key | Full reference | URL/DOI | What it supports in ch. 2 |
|---|---|---|---|
| Ahmed22 | Ahmed, M.R., Islam, A.K.M.M., Shatabda, S., Islam, S. (2022). Blockchain-Based Identity Management System and Self-Sovereign Identity Ecosystem: A Comprehensive Survey. IEEE Access 10:113436-113481. | https://doi.org/10.1109/ACCESS.2022.3216643 | §2.1.2 survey; essential components and threats of blockchain identity |
| Barreto21 | Barreto, P.S.L.M., Simplicio, M.A., Ricardini, J.E., Patil, H.K. (2021). Schnorr-Based Implicit Certification: Improving the Security and Efficiency of Vehicular Communications. IEEE Trans. Computers 70(3):393-399. | https://doi.org/10.1109/TC.2020.2988637 | §2.4.2 forgery weakness in SCMS butterfly-key provisioning and fix |
| Brousmiche18 | Brousmiche, K.L., Heno, T., Poulain, C., Dalmieres, A., Ben Hamida, E. (2018). Digitizing, Securing and Sharing Vehicles Life-cycle over a Consortium Blockchain: Lessons Learned. IFIP NTMS 2018, pp. 1-5. | https://doi.org/10.1109/NTMS.2018.8328733 | §2.3.1 early blockchain vehicle-lifecycle ledger |
| Butera23 | Butera, A., Gatteschi, V., Pratticò, F.G., Novaro, D., Vianello, D. (2023). Blockchain and NFTs-Based Trades of Second-Hand Vehicles. IEEE Access 11:57598-57615. | https://doi.org/10.1109/ACCESS.2023.3284676 | §2.3.2 NFT vehicle history and market (single substrate) |
| Butincu24 | Buțincu, C.N., Alexandrescu, A. (2024). Design Aspects of Decentralized Identifiers and Self-Sovereign Identity Systems. IEEE Access 12:60928-60942. | https://doi.org/10.1109/ACCESS.2024.3394537 | §2.1.3 DID/SSI architecture blueprints |
| Cai25 | Cai, X., Song, R., Xie, B., Xiao, Q., Xiao, B. (2025). PSP: A Privacy-Preserving Self-certify Pseudonym Protocol for V2X. ACM AsiaCCS 2025, pp. 651-664. | https://doi.org/10.1145/3708821.3736212 | §2.4.3 decentralised pseudonyms from anonymous credentials |
| ChenCompare24 | Chen, A.C.H., Liu, C.-C., Lin, C.-Y., Lin, B.-Y. (2024). V2X Credential Management System Comparison Based on IEEE 1609.2.1 and ETSI TS 102 941. IEEE NKCon 2024, pp. 1-6. | https://doi.org/10.1109/NKCon62728.2024.10774595 | §2.4.2 IEEE vs ETSI credential management, implemented |
| ChenSCMS23 | Chen, A.C.H., Lin, B.-Y., Liu, C.-C., Lin, C.-Y. (2023). Implementation and Performance Analysis of Security Credential Management System Based on IEEE 1609.2 and 1609.2.1 Standards. IEEE ICMLANT 2023, pp. 1-5. | https://doi.org/10.1109/ICMLANT59547.2023.10372990 | §2.4.2 SCMS implemented and timed |
| Cucko21 | Čučko, Š., Turkanović, M. (2021). Decentralized and Self-Sovereign Identity: Systematic Mapping Study. IEEE Access 9:139009-139027. | https://doi.org/10.1109/ACCESS.2021.3117588 | §2.1.2 field dominated by solution proposals |
| Das23 | Das, D., Dasgupta, K., Biswas, U. (2023). A secure blockchain-enabled vehicle identity management framework for intelligent transportation systems. Computers and Electrical Engineering 105:108535. | https://doi.org/10.1016/j.compeleceng.2022.108535 | §2.3.2 blockchain vehicle identity framework |
| Ferdous19 | Ferdous, M.S., Chowdhury, F., Alassafi, M.O. (2019). In Search of Self-Sovereign Identity Leveraging Blockchain Technology. IEEE Access 7:103059-103079. | https://doi.org/10.1109/ACCESS.2019.2931173 | §2.1.1 formal treatment of SSI properties |
| Gorzny25 | Gorzny, J., Soureshjani, F.H., Derka, M. (2025). Account Abstraction for Enforcing Blockchain-Based AI Agent Non-Functional Requirements. IEEE RE Workshops (REW) 2025, pp. 359-364. | https://doi.org/10.1109/REW66121.2025.00053 | §2.6.2 smart wallets for scoped delegation to agents |
| Haidar17 | Haidar, F., Kaiser, A., Lonc, B. (2017). On the Performance Evaluation of Vehicular PKI Protocol for V2X Communications Security. IEEE VTC-Fall 2017, pp. 1-5. | https://doi.org/10.1109/VTCFall.2017.8288286 | §2.4.2 measured PKI certificate-reload latency |
| Kailus24 | Kailus, A., Kern, D., Krauß, C. (2024). Self-sovereign Identity for Electric Vehicle Charging. ACNS 2024, LNCS, pp. 137-162. | https://doi.org/10.1007/978-3-031-54776-8_6 | §2.1.5 SSI replacing ISO 15118 PKI, Tamarin analysis |
| Kondova20 | Kondova, G., Erbguth, J. (2020). Self-sovereign identity on public blockchains and the GDPR. ACM SAC 2020, pp. 342-345. | https://doi.org/10.1145/3341105.3374066 | §2.1.2 qualitative comparison of Sovrin, uPort, Jolocom |
| Kosubiene25 | Košubienė, G., Masteika, S. (2025). Implementing EVM-Based Self-Sovereign Identity to Meet European Digital Identity Compliance for Decentralized Finance. Vilnius University Open Series. | https://doi.org/10.15388/LMITT.2025.13 | §2.2.3 ERC-734/735 SSI on Sepolia; single standard |
| Kuperberg20 | Kuperberg, M. (2020). Blockchain-Based Identity Management: A Survey From the Enterprise and Ecosystem Perspective. IEEE Trans. Engineering Management 67(4):1008-1027. | https://doi.org/10.1109/TEM.2019.2926471 | §2.1.2, §2.7 criteria-driven product comparison |
| Lin24 | Lin, Z.-B., Wang, T.-H., Zhao, C., Zhang, S., Yang, Q., Shi, L. (2024). A Measurement Investigation of ERC-4337 Smart Contracts on Ethereum Blockchain. IEEE ICNC 2024, pp. 1164-1170. | https://doi.org/10.1109/ICNC59896.2024.10556301 | §2.2.4, §2.2.6 measured ERC-4337 gas (one standard) |
| LopezPimentel23 | López-Pimentel, J.C., Morales-Rosales, L.A., Algredo-Badillo, I., Del-Valle-Soto, C. (2023). NFT-Vehicle: A Blockchain-Based Tokenization Architecture to Register Transactions over a Vehicle's Life Cycle. Mathematics 11(13):2801. | https://doi.org/10.3390/math11132801 | §2.3.2 ERC-721 vehicle lifecycle with cost estimate |
| NokhbehZaeem21 | Nokhbeh Zaeem, R., Chang, K.C., Huang, T.-C., et al. (2021). Blockchain-Based Self-Sovereign Identity: Survey, Requirements, Use-Cases, and Comparative Study. IEEE/WIC/ACM WI-IAT 2021, pp. 128-135. | https://doi.org/10.1145/3486622.3493917 | §2.1.2, §2.7 requirements-based comparison of SSI solutions |
| Notheisen17 | Notheisen, B., Cholewa, J.B., Shanmugam, A.P. (2017). Trading Real-World Assets on Blockchain. Business & Information Systems Engineering 59(6):425-440. | https://doi.org/10.1007/s12599-017-0499-8 | §2.3.1 vehicle trading and history prototype |
| PavaDiaz24 | Pava-Díaz, R.A., Gil-Ruiz, J., López-Sarmiento, D.A. (2024). Self-sovereign identity on the blockchain: contextual analysis and quantification of SSI principles implementation. Frontiers in Blockchain 7. | https://doi.org/10.3389/fbloc.2024.1443362 | §2.1.2, §2.7 nine-framework principle comparison |
| Satybaldy24 | Satybaldy, A., Ferdous, M.S., Nowostawski, M. (2024). A Taxonomy of Challenges for Self-Sovereign Identity Systems. IEEE Access 12:16151-16177. | https://doi.org/10.1109/ACCESS.2024.3357940 | §2.1.2 SSI challenge taxonomy |
| Simplicio21 | Simplicio, M.A., Cominetti, E.L., Patil, H.K., Ricardini, J.E., Ferraz, L.T.D., Silva, M.V.M. (2021). Privacy-Preserving Certificate Linkage/Revocation in VANETs Without Linkage Authorities. IEEE Trans. ITS 22(6):3326-3336. | https://doi.org/10.1109/TITS.2020.2981907 | §2.4.2 SCMS revocation attacks and simplification |
| Soltani21 | Soltani, R., Nguyen, U.T., An, A. (2021). A Survey of Self-Sovereign Identity Ecosystem. Security and Communication Networks 2021:1-26. | https://doi.org/10.1155/2021/8873429 | §2.1.1 identity models leading to SSI |
| Stockburger21 | Stockburger, L., Kokosioulis, G., Mukkamala, A., Mukkamala, R.R., Avital, M. (2021). Blockchain-enabled decentralized identity management: The case of self-sovereign identity in public transportation. Blockchain: Research and Applications 2(2):100014. | https://doi.org/10.1016/j.bcra.2021.100014 | §2.1.5 SSI in transport ticketing |
| Terzi21 | Terzi, S., Savvaidis, C., Sersemis, A., Votis, K., Tzovaras, D. (2021). Decentralizing Identity Management and Vehicle Rights Delegation through Self-Sovereign Identities and Blockchain. IEEE COMPSAC 2021, pp. 1217-1223. | https://doi.org/10.1109/COMPSAC51774.2021.00168 | §2.3.3 SSI for vehicles and rights delegation |
| Toth19 | Toth, K.C., Anderson-Priddy, A. (2019). Self-Sovereign Digital Identity: A Paradigm Shift for Identity. IEEE Security & Privacy 17(3):17-27. | https://doi.org/10.1109/MSEC.2018.2888782 | §2.1.1 properties of self-sovereignty |
| Wang23Hades | Wang, K., Gao, J., Wang, Q., Zhang, J., Li, Y., Guan, Z., Chen, Z. (2023). Hades: Practical Decentralized Identity with Full Accountability and Fine-grained Sybil-resistance. ACSAC 2023, pp. 216-228. | https://doi.org/10.1145/3627106.3627110 | §2.2.6 EVM identity system with its own gas evaluation |
| WangChen23 | Wang, Q., Chen, S. (2023). Account Abstraction, Analysed. IEEE Blockchain 2023, pp. 323-331. | https://doi.org/10.1109/Blockchain60715.2023.00057 | §2.2.4 ERC-4337 mechanism and security review |
| Yildiz23 | Yildiz, H., Küpper, A., Thatmann, D., Göndör, S., Herbke, P. (2023). Toward Interoperable Self-Sovereign Identities. IEEE Access 11:114080-114116. | https://doi.org/10.1109/ACCESS.2023.3313723 | §2.1.3 SSI interoperability reference model |
| Zeydan23 | Zeydan, E., Mangues, J., Arslan, S., Turk, Y. (2023). Blockchain-based Self-Sovereign Identity Solution for Vehicular Networks. DRCN 2023. | https://doi.org/10.1109/DRCN57075.2023.10108183 | §2.3.3, §2.7 SSI vs NFT for vehicles, qualitative |
