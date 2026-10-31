# Roots Thread G-R1 · Phase 2 — Shared Brief for Every Agent

v1.0 · 2026-10-23 · read this whole file before writing anything.

## 1. What Phase 2 is

Phase 1 (`docs/roots/phase1/`, read its `README.md` first) built an eight-layer stack L0–L7 from the
Bitcoin roots and the identity lineage, placed the programme's solutions (SOL-01..09) on it, derived
51 breaking points (BP-), and bounded them numerically (PF-01..31, SYM-01..24). It stayed at the level
of *primitives and architectures*.

Phase 2 goes **deeper and more complete**: everything from hardware to the application — silicon and
secure elements, vehicle E/E and radios, operating systems and runtimes, node clients, P2P and RPC
networking, storage engines and tries, consensus implementations, the EVM and precompiles, transaction
formats, the actual smart-contract code in this repository, credential formats, DID methods, wallets
and agents, V2X message standards, the testbed — each tied back down to the Phase 1 roots (T-, T-I-,
L-, SOL-, BP-, PF- tags) in the same "enabled by / secured by" discipline. Then a **reverse-direction**
register that starts from the programme's high-level functionality (a transaction, a VC endorsement,
a read, a signature, the IDTX functions…) and anchors each one down to the roots, with the
measurable dimensions it can be judged on.

## 2. Be contemporary — the repo as of 2026-10-22 is the ground truth for "what exists"

Read before writing (skim, don't read every line):
- `docs/STATUS_2026-10-22.md` — current state, claim register summary, what's next.
- `docs/DECISION_SHEET_2026-10-20.md` — open decisions.
- `docs/MEASUREMENT_CONDITIONS.md` — the claim register: every number with its status (V verified,
  superseded, estimate, unsupported) and condition class (M0, M2…). **Quote numbers only from here,
  with the row**, or mark them ESTIMATED.
- `docs/THREAT_MODEL.md`, `docs/LATENCY_BUDGET.md`, `docs/SCALING_EXPERIMENTS.md`.
- `docs/tdp/` (Technical Data Package), `docs/phase2/` (the *repo's* Phase 2 — a different thing
  from this Roots Phase 2; don't confuse them), `docs/phase2/briefs/I-24_IDTX.md`.
- Code: `1_blockchain-identity/contracts/**` (ERC-1056, ERC-721, ERC-725, ERC-725xy, ERC-735,
  ERC-1155, ERC-4337, LSP8, MOBI VID registries, CVINCombined), `phase2/idtx/contracts/IdtxExecutor.sol`,
  `5_zkp-agent-identity/` (circom circuit `zkvin.circom`, steward, attacks), `2_w3c-ssi-layer/`
  (did-resolution, verifiable-credentials, mobi-vid), `cv2x-testbed/` (identity providers incl.
  `erc1056_provider.py`, `freshness.py`; `protocols/cv2x_stack.py`; SUMO; docker),
  `1_blockchain-identity/hardhat.config.js`.
- Project knowledge (via the Projects tool, `project_search`, if your tools include it): the
  Terminology Freeze, Family E, the placement suite P1–P4, G-C1 security campaign.

**Honesty rule that matters most:** the repository's executed chain is **Hardhat** (and Sepolia per
`1_blockchain-identity/SEPOLIA_VALIDATION.md`). **Hyperledger Besu / QBFT appears only in design
documents** (`cv2x-testbed/V2_DESIGN.md`, `docs/phase2/focus/F2_chains_and_databases/CAPTURE.md`) and in
the Phase-1 SOL-01/02 descriptions. Every statement about Besu, QBFT, public anchoring or HAA-1 is
**DESIGN** unless you find an executed trace. Label each claim: MEASURED (cite register row or result
file) · DERIVED (equation + inputs) · DESIGN (specified, not built) · ESTIMATED · STANDARD (cited
spec/theorem). Never upgrade a status.

Where the repo's vocabulary differs from Phase 1 (e.g. the repo's "nine standards" vs the project's
O1–O17 option list), give a mapping table rather than picking one silently.

## 3. Tags — extend, never redefine

Phase 1 tags are frozen: L0–L7, T-01..T-24, T-I01..T-I22, SOL-01..09, BP-L0-01..BP-L7-07, SYM-01..24,
PF-01..31, FIG-R1..R6. Phase 2 adds:

**Sub-layers** (refine, don't replace, L0–L7) and one new layer below L0:
| Sub-layer | Contents |
|---|---|
| **LH** Hardware & physical trust anchors (new, below L0) | LH.1 CPU/silicon and RNG · LH.2 secure elements (HSM, TPM, TEE, SE, eSIM) · LH.3 vehicle E/E (ECU, OBU, gateway, CAN/Ethernet) · LH.4 radio and positioning hardware (DSRC/C-V2X modems, GNSS as time and position source) · LH.5 server/cloud hosts for nodes |
| L0.1 PHY/MAC | IEEE 802.11p/bd, LTE-V2X PC5 mode 4, NR-V2X, cellular Uu |
| L0.2 IP/transport | IPv4/6, UDP, TCP, QUIC; WSMP (IEEE 1609.3) for non-IP V2X |
| L0.3 P2P overlay | devp2p RLPx, discv4/discv5, libp2p, gossip |
| L0.4 RPC transport | JSON-RPC over HTTP/WS, Engine API, TLS on RPC |
| L1.1 primitives / L1.2 crypto libraries | secp256k1, keccak, BN254/BLS12-381 · libsecp256k1, noble, BouncyCastle, snarkjs/circom, anoncreds-rs |
| L2.1 state structures / L2.2 storage engines / L2.3 off-chain structures | MPT, Bonsai tries · RocksDB, LevelDB · status lists, accumulators, IPFS |
| L3.1 consensus protocol / L3.2 client implementation | QBFT, Clique, Gasper, Hardhat automine · Besu, Geth, Hardhat Network |
| L4.1 fee model / L4.2 permissioning and governance / L4.3 capacity | gas, EIP-1559, free-gas · node/account permissioning · block gas limit |
| L5.1 EVM and precompiles / L5.2 smart-contract code / L5.3 transaction formats | opcodes, ecrecover (0x01), bn256 add/mul/pairing (0x06–0x08) · this repo's contracts · legacy/EIP-155/1559/2930/7702 txs, ERC-4337 UserOps |
| L6.1 DID methods / L6.2 credential formats / L6.3 IDTX functions | did:ethr, did:mobi, did:indy, did:web, did:key · VC-JWT, JSON-LD, AnonCreds, SD-JWT, mDL · IMinimalSSI F1–F12, IdtxExecutor |
| L7.1 wallet/agent software / L7.2 messaging protocols / L7.3 application scenarios | ethers, web3.py, did-resolver, Veramo, ACA-Py · DIDComm v2, IEEE 1609.2 secured messages, SAE J2735 BSM/SPaT · tolls, licence endorsement, RSU/TMC |

**New tag namespaces (Phase 2):**
| Tag | Meaning | Owner |
|---|---|---|
| `IMP-<sublayer>-nn` | a concrete implementation/product/library (e.g. `IMP-L3.2-01` Hyperledger Besu) | R6 |
| `PRO-nn` | a protocol (wire or interaction) | R6 |
| `ALG-nn` | an algorithm (signing, hashing, consensus round, proof system, resolution) | R6 defines, R7 bounds |
| `HW-nn` | a hardware component class | R6 |
| `SCF-<contract>-nn` | a smart-contract function in this repo (e.g. `SCF-ERC1056-03 changeOwner`) | R6 |
| `BP-LH-nn`, `BP-Lx.y-nn` | breaking points added below/inside existing layers | R6 |
| `SOL-10`+ | further programme solutions found in the repo (e.g. IdtxExecutor, zk VIN circuit, steward) | R6 |
| `PF-32`+, `SYM-25`+ | further bounds and symbols | R7 |
| `RV-<CAT>-nn` | an upper-level functionality item in the reverse register | R8 |
| `MD-01..` | measurement dimension (time to confirm, decentralisation confidence, trilemma position, SC security, protocol security, cost, privacy, availability, capacity, tier fit…) | R8 defines |
| `PAR-nn` | a parameter to be set later when an implementation choice matters (declare, don't fill) | R8/R7 |
| `FIG-R7`+ | Phase 2 figures | visual agent |
| `KD-R4+`, `Q-R7+`, `F-R5+`, `LIM-R5+`, `MC-R6+` | record keys continue from Phase 1 | all |

Rules: a tag is defined once, in its owner document; others cite. If you need a tag owned by another
document that does not exist yet, write it as `⟦IMP-L3.2-?? Besu⟧` and the v0-2 pass will resolve it.

## 4. File names and versions

All under `docs/roots/phase2/`. Every document is issued as **v0-1 (first pass)** and later **v0-2
(second pass)**; both are kept. Pattern: `claude_CVIN_SC_Roots_<Name>_R<n>_v0-<k>.md`.
| Doc | Folder | Name |
|---|---|---|
| R6 Full-Stack Atlas (forward, deep) | `60_R6_full_stack_atlas/` | `claude_CVIN_SC_Roots_FullStack_Atlas_R6_v0-1.md` |
| R7 Theory and ECE Bounds | `70_R7_theory_ece_bounds/` | `claude_CVIN_SC_Roots_Theory_ECE_Bounds_R7_v0-1.md` |
| R8 Reverse Anchor Register | `80_R8_reverse_register/` | `claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-1.md` |
| R9 Professors' Panel Review | `90_R9_panel_review/` | `claude_CVIN_SC_Roots_Panel_Review_R9_v0-1.md` |
| Figures | `figures/` | `FIG-R7_<slug>.svg` … |

## 5. House style

British spelling (Terminology Freeze). Follow `docs/STYLE_AND_RIGOUR_GUIDE.md`. Each document opens with
a header block (document number, version, date 2026-10-23, consumes, assigns), an approximate progress
bar line (e.g. `Progress ▓▓▓▓▓▓░░░░ 60 %`), and ends with a HANDOFF block (≤ 400 words: files, tag ranges
consumed, five load-bearing decisions, open questions, corrections). Narrative matters: each major
section opens with a paragraph that says what this level does for the level above and what it trusts
from the level below — the reader must be able to move up and down levels of abstraction without
losing the thread. Tables for registers; prose for argument. No bare numbers. Do not write thesis
chapter prose. Do not modify anything outside `docs/roots/phase2/`.
