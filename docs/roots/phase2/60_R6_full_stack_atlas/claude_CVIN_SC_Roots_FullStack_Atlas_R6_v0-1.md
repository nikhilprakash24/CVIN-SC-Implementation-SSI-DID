# CVIN-SC · Roots Thread G-R1 · Phase 2 — R6 The Full-Stack Atlas (forward, bottom-up)

| Field | Value |
|---|---|
| Document | **R6** — Full-Stack Atlas |
| Version | **v0-1** (first pass; v0-2 second pass to follow, both kept) |
| Date | 2026-10-23 |
| Branch / tree read | `roots/G-R1-phase2`, working tree as found on 2026-10-23 (no commit made) |
| Consumes | Phase 1: R1 v1-1 (`T-01..T-24`, `T-I01..T-I22`, L0–L7), R2 v0-1 (`SOL-01..09`, options O1–O18), R3 v0-1 (`BP-L0-01..BP-L7-07`), R4 v0-1 (`SYM-01..24`, `PF-01..31`), R5 v0-1 (`KD-R1..3`, `Q-R1..6`). Repo ground truth listed in §0.2 |
| Assigns | sub-layers LH, L0.1–L7.3 (as defined in the Phase 2 brief §3, populated here); `HW-01..HW-12`; `PRO-01..PRO-22`; `ALG-01..ALG-24` (ALG-25..26 reserved); `IMP-<sublayer>-nn` (ranges in §8); `SCF-<contract>-nn` (22 contract prefixes, 117 register rows, §2.L5.2); `BP-LH-01..06` and 33 `BP-Lx.y-nn` rows (§4); `SOL-10..SOL-17`; placeholders `PF-⟦1⟧..PF-⟦24⟧` for R7; `Q-R7..Q-R12`; `KD-R4..KD-R8` |
| Status labels | MEASURED (register row or result file) · DERIVED · DESIGN · ESTIMATED · STANDARD · not used · candidate |

`Progress ▓▓▓▓▓▓▓░░░ 70 %` — first pass complete across all sections; v0-2 to re-verify every SCF row against the test suites, resolve ⟦⟧ placeholders, and take the project's Terminology Freeze O1–O17 list from project knowledge (not reachable in this session; see §3).

**How to read.** This is the forward document: it starts at silicon and climbs to the application, one layer per section, and at every step says two things — what the level *gives* the level above, and what it *trusts* from the level below. Each section opens with a narrative paragraph for the reader who wants to move up and down abstraction without losing the thread; the register table beneath it is for the reader who wants to cite. Every row is labelled with what this programme has actually done with the component: MEASURED (with the claim-register row from `docs/MEASUREMENT_CONDITIONS.md`, written `#n`, or a result file), DESIGN (named in a design document, never executed), *not used*, or *candidate*. The single most important honesty rule, inherited from the brief, is that the executed chain in this repository is **Hardhat** — in-process (`chainId 31337`, `1_blockchain-identity/hardhat.config.js`) or a local Hardhat node (`chainId 1337` with automine plus a 1 s interval in `cv2x-testbed/hardhat.config.js`). Hyperledger Besu, QBFT, Sepolia execution and HAA-1 public anchoring are **DESIGN** throughout this document. Where the atlas cites a number, the register row is beside it; where it cannot, the cell says ESTIMATED or carries a placeholder `PF-⟦n⟧` for R7 to bound. §6 gives worked vertical traces from a concrete contract function down to the secure element; §7 is the one-table honesty summary.

---

## 0. Scope, sources and conventions

### 0.1 What "forward" means here

Phase 1 (R3 Table I.2) carried one sentence forward: *everything above the ledger borrows ordering and nothing else; everything above L1 borrows unforgeability and nothing else.* R6 tests that sentence against the components the repository actually runs. Where a component borrows something else — wall-clock time from the host (D40, D51), randomness from the operating system, a chain id from the RPC endpoint, a trusted setup from one laptop — the atlas names the hidden dependency and gives it a breaking point in §4. That is the main contribution of going deeper: the borrowed properties that the eight-layer abstraction hides.

### 0.2 Repository ground truth read for this pass

`docs/STATUS_2026-10-22.md` (incl. §5 addendum), `docs/MEASUREMENT_CONDITIONS.md` (62 rows), `docs/THREAT_MODEL.md`, `docs/LATENCY_BUDGET.md`, `docs/DEFECT_LOG.md` (D1–D66), `docs/BASIC_ID_SET_EXTENSION.md`, `docs/phase2/focus/F2_chains_and_databases/CAPTURE.md` §5, every `.sol` file under `1_blockchain-identity/contracts/**`, `phase2/idtx/contracts/`, `5_zkp-agent-identity/contracts/`, `cv2x-testbed/contracts/`; `5_zkp-agent-identity/{README.md, circuits/zkvin.circom, circuits/build_circuit.sh, zkid/, steward/vault.py}`; `cv2x-testbed/{hardhat.config.js, V2_DESIGN.md, docker/docker-compose.yml, protocols/cv2x_stack.py, identity/erc1056_provider.py, identity/freshness.py, identity/standard/pki_identity.py, sumo/}`; `2_w3c-ssi-layer/{did-resolution/did_resolver.py, verifiable-credentials/vc_issuer.py, requirements.txt}`; the three Hardhat configs; `1_blockchain-identity/SEPOLIA_VALIDATION.md`; package manifests.

Two repository facts shape everything below and are stated once here:
- **Byte-identical copies.** `cv2x-testbed/contracts/{ERC1056Registry, MOBIVIDRegistry, MOBIVIDRegistryV2}.sol` are byte-identical to `1_blockchain-identity/contracts/MOBI/` (checked with `cmp` for this pass). One SCF register covers both; the testbed compiles them with solc 0.8.20 / evm default (`cv2x-testbed/hardhat.config.js`), the main tree with 0.8.24 / `cancun` / viaIR — so gas differs by build (#22 vs #29), not by source.
- **Two "ERC-1056" contracts** (register §1.1, K-5): `EthereumDIDRegistry` (the uPort/DIF lineage, implicit identities, `*Signed` meta-transactions) and `ERC1056Registry` (the vehicle profile, explicit `registerVehicle`, `revokeIdentity`, no `*Signed`). The atlas gives them different SCF prefixes (`EDR`, `VPR`) and never mixes them.

### 0.3 Tag conventions used in this document

`HW-nn` hardware class · `PRO-nn` wire or interaction protocol · `ALG-nn` algorithm · `IMP-<sublayer>-nn` concrete implementation · `SCF-<prefix>-nn` contract function · `BP-LH-nn`, `BP-Lx.y-nn` new breaking points · `SOL-10+` repo solutions · `PF-⟦n⟧` bound placeholder owned by R7 · `⟦…⟧` cross-document tag not yet assigned. Phase 1 tags (`T-`, `T-I`, `SOL-01..09`, `BP-Lx-nn`, `PF-01..31`, `SYM-`) are cited, never redefined. Register rows are `#n`; defects `Dn`; threat-model goals `G1–G8`, adversaries `A1–A4`, trust assumptions `T1–T4` (prefixed `TM-` where a collision with root tags `T-0x` could confuse: `TM-T1` is "chain integrity").

---

## 1. The extended stack

The table refines Phase 1's eight layers into the brief's sub-layers and adds LH beneath L0. Read top to bottom it is the dependency direction ("secured by"); read bottom to top it is the enabling direction.

| Sub-layer | One-line role | Trusts from below | Gives above | Refines Phase-1 layer / tags |
|---|---|---|---|---|
| **LH.1** CPU / silicon / RNG | executes instructions faithfully; supplies entropy | physics; foundry; microcode vendor | correct arithmetic; unpredictable bits for key and nonce generation | below L0; precondition of `BP-L1-01`, `BP-L1-02`, `PF-06` (κ) |
| **LH.2** secure elements | isolate keys; sign without exporting | LH.1; the vendor's certification | non-exportable private keys; attestation of the signer | T-I05 HSM domain; `BP-L1-07`, `BP-L7-01` |
| **LH.3** vehicle E/E | ECUs, gateway, OBU; in-vehicle bus | LH.1, LH.2 | a host for the wallet/agent and the V2X stack; vehicle data (odometer, position) | L7 endpoint; `BP-L7-01` |
| **LH.4** radio and positioning | DSRC / C-V2X modems; GNSS receiver | LH.1; RF environment; satellite constellation | a radio bearer; **time and position** | L0 physical; hidden dependency of R8 freshness |
| **LH.5** server / cloud hosts | run node clients, RPC endpoints, resolvers | LH.1; the hypervisor and cloud operator | a place for L3 clients and Plane V services | L3 / SOL-02 deployment substrate |
| **L0.1** PHY / MAC | 802.11p/bd, LTE-V2X PC5 mode 4, NR-V2X, Uu | LH.4 | best-effort broadcast/unicast frames | T-01 analogue for V2X |
| **L0.2** IP / transport | IPv4/6, UDP, TCP, QUIC; WSMP | L0.1 | addressed datagrams / streams | T-01 |
| **L0.3** P2P overlay | devp2p RLPx, discv4/v5, libp2p, gossip | L0.2; L1 (node keys) | peer discovery, block and tx propagation | T-02, T-03; `BP-L0-01..03` |
| **L0.4** RPC transport | JSON-RPC over HTTP/WS, Engine API, TLS | L0.2; LH.5 | a client's window into chain state | new; the "read path" of HAA-1 Plane V |
| **L1.1** primitives | secp256k1/ECDSA, P-256, Ed25519, keccak-256, SHA-256, Poseidon, BN254, BLS12-381 | LH.1 entropy; hardness assumptions | unforgeability, binding, collision resistance | T-04..T-07, T-I10, T-I11, T-I14, T-I15 |
| **L1.2** crypto libraries | libsecp256k1/coincurve, noble, ethers, BouncyCastle, Python `cryptography`, snarkjs/circom, anoncreds-rs | L1.1; LH.1; the language runtime | callable, (hopefully) constant-time implementations | new; `BP-L1-07` locus |
| **L2.1** state structures | MPT, Bonsai, receipts trie, log blooms, contract mappings | L1.1 keccak | authenticated state and event history | T-08, T-09; `BP-L2-01` |
| **L2.2** storage engines | LevelDB, RocksDB, Hardhat in-memory state | LH.5 disk; OS | persistence of L2.1 | new; storage corruption |
| **L2.3** off-chain structures | status lists, accumulators, Merkle trees, CAS/IPFS | L1.1; Plane D owner | revocation and data availability | T-I12, SOL-09; `BP-L0-05`, `BP-L2-03/04` |
| **L3.1** consensus protocol | QBFT, IBFT 2.0, Clique, Gasper, automine | L0.3; L1.1 validator keys | a single ordered history; finality | T-11..T-13; `BP-L3-01..06` |
| **L3.2** client implementation | Besu, Geth, Hardhat Network, Anvil, Ganache | L3.1 spec; L2.2; L1.2 | a running node | new; monoculture |
| **L4.1** fee model | gas schedule, EIP-1559, free-gas | L3 | pricing and back-pressure | T-14, T-17; `BP-L4-03/05` |
| **L4.2** permissioning / governance | node/account allowlists, validator admission, contract admin roles | L3; L5 (on-chain allowlists) | who may write, who may validate | `BP-L4-04/06` |
| **L4.3** capacity | block gas limit, block interval | L3.1 Δ | ops/s ceiling | `PF-24` |
| **L5.1** EVM and precompiles | opcodes, `ecrecover` 0x01, `sha256` 0x02, bn256 0x06–0x08, modexp 0x05 | L1.2 inside the client; L2.1 | deterministic execution; cheap crypto | T-10 semantics; `BP-L5-*` |
| **L5.2** smart-contract code | **this repo's 24 contract files** | L5.1; L4.2 roles | identity registries, claims, gates | O1–O9, SOL-06; `BP-L5-04` |
| **L5.3** transaction formats | legacy, EIP-155, 2930, 1559, 4844, 7702; ERC-4337 UserOps | L1.1; L3 ordering | authenticated, replay-scoped state transitions | `BP-L5-02/03` |
| **L6.1** DID methods | did:ethr, did:mobi, did:nft, did:key, did:web (repo); did:indy (not used) | L5.2 registries; L0.4 reads | identifier → key binding (I1, I3) | T-I17; O1, O10–O11 |
| **L6.2** credential formats | Data Integrity (eip191-secp256k1 cryptosuite), SD-JWT-style digests; AnonCreds/BBS+/mDL not used | L1.1; L6.1 issuer keys | attribute binding, selective disclosure (I4–I8) | T-I11, T-I13, T-I17, T-I20 |
| **L6.3** IDTX functions | IMinimalSSI F1–F12; IdtxExecutor; ZkVinGate | L5.2; L6.1/6.2 | identity-dependent actions | SOL-06; I-24 |
| **L7.1** wallet / agent | ethers, web3.py, eth-account, ethr-did-resolver, Steward | L1.2; L0.4; LH.2 | key custody, resolution, policy | O17, T-I22 |
| **L7.2** messaging | freshness module, JSON-signed BSM/SPaT, 1609.2 (DESIGN), DIDComm (not used) | L6; L1; LH.4 time | authenticated fresh messages (R1, R8) | T-I05, T-I09, T-I18; `BP-L7-04/05` |
| **L7.3** scenarios | SUMO V2V and RSU/TMC, tolls, lifecycle, ZK admission | everything below | the thesis's application claims | `BP-L7-07` |

---

## 2. Layer by layer

### LH — Hardware and physical trust anchors

Everything the stack calls "unforgeable" is unforgeable only if a key was drawn from enough entropy and never left a place an adversary can read. LH is where both of those are decided. It gives L1 two things — unpredictable bits and an isolated place to use a private key — and it gives L7 a vehicle that can host a wallet, a radio that can carry a message, and a clock and position that the freshness rule silently depends on. It trusts only physics, a foundry, and vendor firmware, none of which this programme can inspect. **Nothing at LH is measured in this programme**: the repository's keys are generated in software on a cloud Xeon (#27, #57 environment headers), and its threat model puts HSM and side-channel compromise explicitly out of scope (`docs/THREAT_MODEL.md` §2, §6). LH is therefore a DESIGN layer whose rows are here so that §4 can name what the thesis's security claims are conditional on.

#### LH.1 CPU, silicon and RNG

| Tag | Component | What it does | Secured by | Enables above | Status in this programme | Repo location |
|---|---|---|---|---|---|---|
| HW-01 | General-purpose CPU (x86-64 Xeon of record) | executes node, prover, verifier | vendor microcode; physical isolation | all M0/M1 results | MEASURED as environment only (#27: "Xeon 2.10 GHz × 4"; #57: "2.80 GHz Xeon") | result headers |
| HW-02 | Hardware RNG (Intel RDRAND/RDSEED, ARM TRNG) | entropy source feeding the OS pool | silicon design; health tests (NIST SP 800-90B, STANDARD) | IMP-LH.1-01 | not observed directly | — |
| IMP-LH.1-01 | OS CSPRNG (`/dev/urandom`, `getrandom`) via Python `secrets`, `cryptography`, `eth_account.Account.create()` | key and nonce generation | HW-02; kernel | ALG-01 keygen, ALG-02 nonces | used, not measured | `5_zkp-agent-identity/steward/vault.py` (`secrets.randbelow`, `Account.create()`); `erc1056_provider.py` (`ec.generate_private_key(SECP256K1)`) |
| IMP-LH.1-02 | **Test-only deterministic keys**: controller key = SHA-256(vehicle_id) | re-derive vehicle accounts without storage | nothing (publicly derivable) | testbed experiments only | used, labelled INSECURE in source | `cv2x-testbed/identity/erc1056_provider.py` `vehicle_account()` (review 02 T-11) |
| IMP-LH.1-03 | Seeded PRNG (`CVIN_SEED`, seeds 1–30) | reproducible incidental randomness | none (by design) | reproducible gas (#47) | used | register §1 (WM-2 B1) |

#### LH.2 Secure elements

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| HW-03 | HSM (V2X OBU/RSU HSM, CA HSM) | holds 1609.2 signing keys; signs on request | FIPS 140-3 / CC certification (STANDARD); tamper response | ALG-05 P-256 signing for PRO-12 | DESIGN (THREAT_MODEL §2: "physical/side-channel attacks on the vehicle HSM" assumed away) | — |
| HW-04 | TPM 2.0 | measured boot; sealed keys on hosts and ECUs | TCG spec (STANDARD) | node-key protection (LH.5); attested boot of the agent | not used | — |
| HW-05 | TEE (Intel SGX/TDX, Arm TrustZone, AMD SEV) | run code with memory isolation | vendor attestation | candidate home for the Steward vault (SOL-14) | candidate | — |
| HW-06 | Secure element / eSIM / wallet SE | non-exportable secp256k1 key for the owner wallet | CC EAL5+ (STANDARD) | the owner key behind every SCF write | DESIGN (`erc1056_provider.py` docstring: "keep it in the vehicle's secure element / HSM") | — |

#### LH.3 Vehicle E/E architecture

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| HW-07 | ECUs and the central gateway | host vehicle functions; firewall between domains | ISO/SAE 21434 process; UN R155 CSMS (STANDARD) | host for L7.1 agent | not used | — |
| HW-08 | OBU (on-board unit) | V2X application processor + HSM + modem | HW-03, HW-09 | PRO-12, PRO-13 | simulated as a Python object | `cv2x-testbed/protocols/cv2x_stack.py` `CV2XStack` |
| PRO-01 | CAN / CAN-FD | in-vehicle bus, no native authentication | AUTOSAR SecOC (STANDARD, optional MAC) | odometer and sensor data that lifecycle events attest | not used | — |
| PRO-02 | Automotive Ethernet (100/1000BASE-T1) with MACsec | high-rate in-vehicle backbone | IEEE 802.1AE (STANDARD) | as PRO-01 | not used | — |

#### LH.4 Radio and positioning hardware

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| HW-09 | V2X modem (DSRC 802.11p chipset; C-V2X PC5 chipset) | radio bearer at 5.9 GHz | regulatory certification | L0.1 | simulated (FSPL + Gaussian shadowing, `PHYLayer`) | `protocols/cv2x_stack.py` lines 256–360 |
| HW-10 | GNSS receiver | **time** (PPS, UTC) and **position** | satellite signal integrity (no civil authentication except Galileo OSNMA, STANDARD) | the generation-time freshness rule (IMP-L7.2-01); the position fields of every BSM; the PC5 mode-4 sync | DESIGN — the freshness module's comment assumes "GNSS-disciplined OBU clocks are far tighter" (`identity/freshness.py`) | — |

#### LH.5 Server and cloud hosts

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| HW-11 | Cloud VM / container host (the CI runners and the measurement host) | runs Hardhat, Python, snarkjs | hypervisor isolation; operator | every MEASURED row | MEASURED as environment (#52, #55: same-host replicates; "foreign-CPU load") | `.github/workflows/` |
| HW-12 | Validator / RPC node host (consortium) | runs IMP-L3.2-01 Besu | HW-04 TPM; operator governance | SOL-02 Plane A | DESIGN | — |
| IMP-LH.5-01 | Docker compose (SUMO, ns-3, PKI-CA, identity manager, **Ganache**) | testbed orchestration | container isolation | L7.3 scenarios | DESIGN-level file; not referenced by any MEASURED row read for this pass | `cv2x-testbed/docker/docker-compose.yml` |

---

### L0 — Network

L0 gives L1–L7 the ability to move bytes between parties who are not co-located, and it promises nothing about who sent them, whether they arrived, or whether the peer you hear from is the only one there is. That is why every property above L0 is built on cryptography, not on the network. It trusts LH.4 for a bearer and LH.1 for node keys. In this programme the vehicle-side radio is a **simulation** (`cv2x_stack.py`), and the chain-side network is a **loopback**: in-process EVM (M1) or `http://127.0.0.1:8545` (M1-H/HTTP, register §1, "≈1–2 ms" per round trip). No P2P overlay has ever carried a block in this programme. L0's role in the thesis is therefore to supply the *conditions* (latency, loss, eclipse, partition) that R7 must bound, not results.

#### L0.1 PHY / MAC

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| PRO-03 | IEEE 802.11p / 802.11bd (DSRC, ITS-G5) | OFDM PHY + EDCA MAC, outside-BSS broadcast | none (open medium) | PRO-08 WSMP; BSM at 10 Hz | not used (named only as "ITS-G5" frequency default in `PHYLayer`) | `cv2x_stack.py` |
| PRO-04 | LTE-V2X PC5 **mode 4** (3GPP Rel-14) | sidelink with sensing-based semi-persistent scheduling (SB-SPS) | GNSS sync (HW-10) | V2V broadcast without a base station | simulated: `ResourcePool` (50 PRB × 4 sub-channels, RSSI < −90 dBm sensing threshold), `CommunicationMode.MODE_4` | `cv2x_stack.py` lines 27–31, 125–200 |
| PRO-05 | LTE-V2X PC5 mode 3 | network-assisted sidelink allocation | eNB scheduling | as PRO-04 | enum only | same |
| PRO-06 | NR-V2X sidelink (Rel-16/17) | 5G sidelink, unicast/groupcast | as PRO-04 | advanced manoeuvre coordination (`MCM` enum) | not used | — |
| PRO-07 | Cellular Uu (LTE/5G to network) | vehicle ↔ backend | 3GPP AKA, SIM | RPC reads (L0.4), certificate and CRL download, backhaul for revocation | not used; a hidden precondition of every M2 read | — |

#### L0.2 IP and transport

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| PRO-08 | WSMP (IEEE 1609.3) | non-IP single-hop V2X datagrams with PSID | none (1609.2 sits above) | PRO-12 secured messages | not used | — |
| PRO-09 | UDP / TCP over IPv4/IPv6 | datagrams and streams | none | L0.3, L0.4 | used (TCP loopback for HTTP RPC) | M1-H/HTTP condition |
| PRO-10 | QUIC (RFC 9000) | encrypted multiplexed transport | TLS 1.3 (T-I04) | libp2p transport; DIDComm candidates | not used | — |

#### L0.3 P2P overlay

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| PRO-11 | devp2p **RLPx** | ECIES (secp256k1) handshake, AES-CTR framing with MAC between Ethereum nodes | node key (ALG-01); L1.1 | block and tx gossip (eth/68), QBFT messages in Besu | not used (Hardhat has no peers) | — |
| PRO-11a | **discv4** (Kademlia over UDP, signed packets) | peer discovery | node-key signatures; no admission cost (T-02, T-03) | PRO-11 | not used | — |
| PRO-11b | **discv5** (ENR, encrypted handshake, topic ads) | improved discovery | as PRO-11a, plus session keys | consensus-layer clients | not used | — |
| PRO-11c | libp2p (gossipsub, Noise, yamux) | consensus-layer P2P | Noise (T-I08) | Gasper attestations | not used | — |
| IMP-L0.3-01 | Besu static-nodes / bootnodes + node permissioning | closed peer set for a consortium | IMP-L4.2-01 | SOL-02 | DESIGN | — |

#### L0.4 RPC transport

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| PRO-13 | Ethereum JSON-RPC over HTTP | `eth_call`, `eth_getLogs`, `eth_sendRawTransaction`, `eth_getBlockByNumber`, `debug_traceTransaction` | **nothing by default** (no auth, no TLS on loopback; responses not proven) | every resolver and provider read; the harness's storage counts | MEASURED: #21 (5 RPCs per uncached verify: `eth_chainId, eth_call, eth_chainId, eth_getLogs, eth_getBlockByNumber`), #31/#51 (RPC calls and bytes vs history), #37 (one-call probe) | `cv2x-testbed/identity/erc1056_provider.py`; `2_w3c-ssi-layer/did-resolution/did_resolver.py`; `1_blockchain-identity/benchmarks/` |
| PRO-13a | JSON-RPC over WebSocket (`eth_subscribe`) | push of logs/heads | as PRO-13 | a revocation push channel (would shorten σ, `PF-15`) | not used | — |
| PRO-13b | Hardhat-specific RPC (`hardhat_getAutomine`, `evm_mine`) | node control | none | reproducible M1 runs | used | `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py` line ~901 |
| PRO-14 | Engine API (EL ↔ CL, JWT-authenticated) | post-Merge block building | HS256 JWT shared secret | Gasper-backed L1 (Option C) | not used | — |
| PRO-15 | TLS on RPC (provider HTTPS: Alchemy/Infura) | server authentication of a remote endpoint | X.509 PKI (T-I02) | M2 Sepolia | DESIGN — documented procedure only (`SEPOLIA_VALIDATION.md`); `sepolia_validation.json` never committed (F2 CAPTURE §5) | `1_blockchain-identity/scripts/validate_sepolia.js` |
| IMP-L0.4-01 | web3.py `HTTPProvider` (+ `ExtraDataToPOAMiddleware`) | Python RPC client; PoA `extraData` tolerance | PRO-13 | providers, MOBI registry client | used; the PoA middleware is the **only** code hook toward a PoA/consortium chain (F2 CAPTURE §5) | `erc1056_provider.py` l. 25–27; `mobi_vid_provider.py` l. 30, 69; `2_w3c-ssi-layer/mobi-vid/mobi_vid_registry.py` l. 31, 103 |
| IMP-L0.4-02 | ethers v6 `JsonRpcProvider` / Hardhat in-process provider | JS RPC client | PRO-13 | harness, Sepolia script, ZK gas script | used | `1_blockchain-identity/package.json` (`ethers ^6.10.0`) |

---

### L1 — Cryptographic primitives and their libraries

L1 is the one layer whose promise every other layer cashes: L5 borrows `ecrecover` to decide who may write, L6 borrows signatures to bind a key to an identifier, L7 borrows them to decide whom to trust on the road. It gives unforgeability and binding; it trusts LH.1 for entropy and a set of hardness assumptions (ECDLP, collision resistance of keccak-256 and SHA-256, q-type pairing assumptions for Groth16 knowledge soundness). L1.2 matters as much as L1.1 here, because the repository runs at least **six** independent implementations of secp256k1 (Python `cryptography`/OpenSSL, `coincurve`/libsecp256k1, `eth-keys`, `eth_account`, ethers/noble, the EVM's own `ecrecover` in Hardhat's EthereumJS, and the readable pure-Python `zkid/ec.py`) and three of SHA-256 / keccak. Each is a separate place a bug can live.

#### L1.1 Primitives and algorithms

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| ALG-01 | secp256k1 key generation | sample d ∈ [1, n−1]; Q = dG | IMP-LH.1-01 entropy; ECDLP (T-06) | every Ethereum account and every did:ethr | used | `zkid/ec.py` (curve constants), `vault.py`, `erc1056_provider.py` |
| ALG-02 | ECDSA secp256k1 with RFC 6979 deterministic nonces | sign a 32-byte digest | ALG-01; RFC 6979 (STANDARD) removes `BP-L1-02` dependence on the RNG | L5.3 tx signatures; EIP-191 personal-sign | used via eth_account / ethers (both implement RFC 6979 — STANDARD library behaviour, not verified in this pass) | — |
| ALG-03 | ECDSA public-key recovery (`ecrecover`) | (digest, v, r, s) → address | ALG-02; EIP-2 low-s rule (STANDARD) for malleability | contract authorisation (SCF-EDR-*, SCF-CMB-*, SCF-E735-*, SCF-E4337A-01), offline VC verification | used in 9 contracts (§2.L5.2) | `EthereumDIDRegistry.sol` l. 172, 234, 296, 351, 400 |
| ALG-04 | ECDSA secp256k1 over **SHA-256** (non-Ethereum message signing) | testbed BSM signatures under did:ethr | ALG-01; SHA-256 | IMP-L7.2-02 | used — the ERC-1056 provider signs BSMs with `ec.ECDSA(hashes.SHA256())` on a SECP256K1 key, not keccak/EIP-191 | `erc1056_provider.py` `sign_message` |
| ALG-05 | ECDSA **P-256** (secp256r1) with SHA-256 | IEEE 1609.2 / X.509 baseline signatures | ECDLP on P-256 | PKI baseline (#21, #27) | used | `identity/standard/pki_identity.py` l. 52–53, 182; `sumo_identity_integration.py` l. 209 |
| ALG-06 | Ed25519 (RFC 8032) | EdDSA signatures | ECDLP on Curve25519 | did:key, DIDComm, Indy | not used (attribute name `did/pub/Ed25519/veriKey` appears only as a comment) | `EthereumDIDRegistry.sol` l. 310 |
| ALG-07 | keccak-256 (original Keccak padding 0x01) | hashing for addresses, selectors, storage slots, signed digests | sponge security (T-07) | L2.1 slots; L5.3 tx hash; every SCF digest | used; pure-Python reference with all 24 rounds | `zkid/hashing.py` |
| ALG-08 | SHA-256 (FIPS 180-4) | message digests; replay-cache keys; VIN hashes | T-07 | IMP-L7.2-01 replay cache; D64 address derivation; #60 brute force | used | `identity/freshness.py`; `mobi_vid_provider.py` |
| ALG-09 | Poseidon (circomlib) | SNARK-friendly hash over BN254 Fr | algebraic-hash assumptions (younger than T-07) | ZK-VIN commitment, Merkle tree, nullifier | used | `circuits/zkvin.circom` |
| ALG-10 | BN254 (alt_bn128) pairing | e: G1 × G2 → GT | ~100-bit security after kTNFS (`PF-10`, STANDARD) | Groth16 verification on chain | used via precompiles 0x06–0x08 | `Groth16Verifier.sol` l. 94, 104, 178 |
| ALG-11 | BLS12-381 pairing | ~120-bit pairing curve (`PF-10`) | as ALG-10 | BBS+, Gasper BLS signatures, EIP-2537 precompiles | not used | — |
| ALG-12 | Groth16 (T-I14) | constant-size zk-SNARK, 3 pairings-equation check | ALG-10; circuit-specific **trusted setup** (`BP-L1-06`); knowledge-of-exponent assumptions | SOL-11 ZK-VIN | MEASURED: #56 (3,498 constraints), #57 (prove 398.6 ms / verify 18.42 ms medians, M0), #58 (301,163 gas `admit`) | `5_zkp-agent-identity/` |
| ALG-13 | PLONK / Halo2 / Bulletproofs | universal-setup or transparent proofs | as above minus per-circuit setup | alternative to ALG-12 | not used | — |
| ALG-14 | Sigma protocols: Schnorr PoK, Pedersen commitments, Chaum–Pedersen, CDS OR, range/threshold proofs, Fiat–Shamir transcripts | interactive-to-NIZK proofs over secp256k1 | ECDLP; random-oracle model (T-I10, T-I15) | Steward threshold proofs (SOL-14); on-chain Schnorr | MEASURED: #59 (timings and exact group-op counts), #58 (Schnorr PoK tx 28,775 gas) | `5_zkp-agent-identity/zkid/sigma.py`, `transcript.py`; `SchnorrEcrecoverVerifier.sol` |
| ALG-15 | "ecrecover hack" Schnorr verification | compute R' = s·G − e·P through ecrecover and compare its address | ALG-03; keccak-in-ROM | SCF-SCH-01/02 | MEASURED (#58) | `SchnorrEcrecoverVerifier.sol` l. 5–25 |
| ALG-16 | CL signatures / BBS+ | multi-show anonymous credentials (T-I11, T-I13) | q-SDH, LRSW, strong RSA | O12 AnonCreds; W3C BBS cryptosuite | not used | — |
| ALG-17 | AES-256-GCM | authenticated encryption of the VIN beside its salted hash | AES; nonce uniqueness | MOBI `encryptedVIN` field | used | `mobi_vid_provider.py` l. 34, 105–110 |

#### L1.2 Cryptographic libraries

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L1.2-01 | Python `cryptography` (OpenSSL backend) | P-256 and secp256k1 ECDSA, X.509, AES-GCM | OpenSSL constant-time code | PKI baseline, testbed signing | used; version in results (#21 cryptography 50.0.1 at A3b; #27 49.0.0) | `requirements.txt` (`cryptography>=41.0.0`, `==41.0.7`) |
| IMP-L1.2-02 | `coincurve` (libsecp256k1 binding) | fast secp256k1 | libsecp256k1's constant-time, formally reviewed code | V2V warm verify path | used (#27 environment: coincurve 21.0.0) | `5_zkp-agent-identity/README.md` install line |
| IMP-L1.2-03 | `eth-account` / `eth-keys` / `ecdsa` / `pycryptodome` | Ethereum signing, EIP-191, keccak | IMP-L1.2-02 or pure Python | VC issuer (cryptosuite `eip191-secp256k1-recovery-2024`), providers, Steward | used | `vc_issuer.py` l. 36–37, 44 |
| IMP-L1.2-04 | ethers v6 (noble-curves inside) | JS signing and ABI | noble's audited curve code | harness, Sepolia script | used | `1_blockchain-identity/package.json` |
| IMP-L1.2-05 | EthereumJS EVM inside Hardhat (precompile implementations) | `ecrecover`, `sha256`, bn256 add/mul/pairing | its own crypto deps | every M1 number | used (Hardhat 2.28.6 per #21, #58) | — |
| IMP-L1.2-06 | BouncyCastle / gnark-crypto inside Besu | Besu's precompiles and signing | JVM; vendor review | SOL-02 | DESIGN | — |
| IMP-L1.2-07 | circom 2.2.2 compiler + circomlib 2.0.5 | R1CS and witness generator from the circuit | compiler correctness; template correctness | ALG-12 | used (#56) | `circuits/build_circuit.sh`; `5_zkp-agent-identity/package.json` |
| IMP-L1.2-08 | snarkjs 0.7.6 | powers-of-tau, Groth16 setup, prove, verify, Solidity verifier export | ffjavascript field arithmetic | ALG-12; generated `Groth16Verifier.sol` | used (#57) | same |
| IMP-L1.2-09 | `zkid` (readable pure-Python secp256k1, keccak, sigma) | proof arithmetic with operation counters | nothing — **"not constant time and must not hold production keys"** (module docstring) | #59, #62 manual-burden counts | used (research) | `5_zkp-agent-identity/zkid/ec.py` l. 1–8 |
| IMP-L1.2-10 | anoncreds-rs | CL credentials, revocation accumulators | ALG-16 | O12 | not used | — |
| IMP-L1.2-11 | OpenZeppelin 5.0.2 `ECDSA`, `MessageHashUtils` | Solidity signature recovery with low-s and zero-address rejection | ALG-03, EIP-2 | SCF-MOBI2-04 `attestEvent` | used | `MOBIVIDRegistryV2.sol` l. 5–6, 369–377 |

---

### L2 — Authenticated data structures and storage

L2 turns L1's hashes into structures whose contents can be proved: a state root that commits to every account and every contract slot, a receipts root that commits to every event a registry emitted. L5 contracts and L6 resolvers rely on it without saying so — a `did:ethr` resolver that replays `DIDOwnerChanged` events is trusting that the logs it was given are the logs under the block's receipts root. In this programme that trust is *never exercised*: Hardhat's in-memory state is read through JSON-RPC, which returns values, not proofs (PRO-13). L2 gives L5/L6 persistence and, in principle, proof; it trusts L1.1 keccak for binding and L2.2 for not losing the data.

#### L2.1 State structures

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| ALG-18 | Merkle-Patricia Trie (state, storage, tx, receipts tries) | authenticated key-value map; state root in block header | ALG-07 (T-08) | `eth_getProof` light verification of registry state | used implicitly by Hardhat; **never proved against** | — |
| IMP-L2.1-01 | Besu Bonsai tries (flat DB + trie logs) | MPT with diff-based storage | ALG-18 | SOL-02 storage efficiency | DESIGN | — |
| IMP-L2.1-02 | Receipts and log blooms | event logs per tx; 2048-bit bloom per block for filter queries | receipts root (ALG-18) | **the whole ERC-1056 document**: attributes live only in `DIDAttributeChanged` events (register #49: U3 is "1 SSTORE / 0 zero→nonzero, 288 B" of log) | MEASURED (#49 log bytes; #31/#51 `eth_getLogs` walk cost: 112 RPC calls / 87 KB at h = 50) | `EthereumDIDRegistry.sol` events |
| IMP-L2.1-03 | Solidity mapping storage (keccak(key ‖ slot)) | contract state: `owners`, `delegates`, `changed`, `nonce`, `revoked`, `vehicleBirths`, `nullifierUsed` … | ALG-07; L2.1 trie | every `view` SCF and every on-chain read by IdtxExecutor | MEASURED as SSTORE counts (#30: zero→nonzero SSTOREs 8 / 92 / 83 for ERC-1056 / 721 / 725 lifecycles) | all contracts |
| IMP-L2.1-04 | ERC-1056 `changed[identity]` linked list (`previousChange` block pointers) | lets a resolver walk an identity's events backwards | IMP-L2.1-02; contract discipline | did:ethr resolution (ALG-21) | used; **cut** by D21 (vehicle profile `DIDRevoked` has no `previousChange`) and D22 (Combined claim ops) | `EthereumDIDRegistry.sol`; `ERC1056Registry.sol` |

#### L2.2 Storage engines

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L2.2-01 | Hardhat in-memory state (EthereumJS `StateManager`) | ephemeral state for M1 | process memory | all M1 gas | used | — |
| IMP-L2.2-02 | RocksDB (Besu) / Pebble/LevelDB (Geth) | persistent KV under the trie | disk integrity; fsync | SOL-02 durability | DESIGN | — |
| IMP-L2.2-03 | Python dict "centralized registry" | baseline registry: mutable, unauthenticated, not persisted | nothing (F2 CAPTURE §5) | PKI/centralised comparison rows (#33) | used | `cv2x-testbed/identity/centralized_vehicle_registry.py` |
| IMP-L2.2-04 | PKI provider's `ct_log` | a "certificate transparency" list | nothing — "a plain list" (F2 CAPTURE §5) | — | used, not a CT log | `centralized_provider.py` l. 62 |

#### L2.3 Off-chain structures

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L2.3-01 | VC `credentialStatus` + `RevocationRegistry` (in-memory or JSON file) | revocation of off-chain VCs | the file's host; no anchoring | F7 `revokeCredential` for the VC layer | used | `vc_issuer.py` l. 110–175 |
| IMP-L2.3-02 | Bitstring status list (W3C, SOL-09 profile SL) | herd-private revocation | list size (`PF-29`) | SOL-09 | DESIGN | — |
| IMP-L2.3-03 | CL / bilinear accumulator (SOL-09 profile AC) | non-revocation witness | T-I12 | SOL-09 | not used | — |
| IMP-L2.3-04 | Poseidon Merkle tree of authorised WMIs (depth 4) | manufacturer allowlist inside the ZK statement | ALG-09 | SOL-11 | used | `zkvin.circom` `MerkleInclusion(4)`; `zkid/merkle.py` |
| IMP-L2.3-05 | IPFS / CAS for credential bodies and service records | content-addressed availability | CID = hash; pinning owner | `tokenURI`, `recordURI`, `dataHash` fields | not used ("no IPFS anywhere", F2 CAPTURE §5); lifecycle backend stores the hash and discards the body | `lifecycle_backends.py` l. 191–195 |
| IMP-L2.3-06 | Replay cache (bounded `OrderedDict`, key = (signer, SHA-256(signed bytes))) | reject duplicates inside the freshness window | ALG-08; size bound | IMP-L7.2-01 | used; default 65,536 entries (module docstring) | `identity/freshness.py` |

---

### L3 — Agreement

L3 is what makes a registry *one* registry: it gives L5 a single ordered sequence of transactions so that "the owner of this DID" has one answer. It trusts L0.3 to deliver messages within some bound and L1 for validator signatures. In Phase 1 every finality number assumed QBFT with Δ = 2 s (`PF-25`, `PF-28`). The repository's executed agreement mechanism is **Hardhat automine**: one process, one "validator", a block the instant a transaction arrives (register M1; #21 "automine"). That mechanism provides ordering trivially and safety and liveness not at all, which is acceptable for gas (deterministic per bytecode) and wrong for anything the thesis says about finality. This is the deepest single gap between Phase 1's assumptions and the code.

#### L3.1 Consensus protocol

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| ALG-19 | Hardhat automine | mine one block per transaction, immediately | single process | M1 ordering | MEASURED as the condition of every M1 row | `1_blockchain-identity/hardhat.config.js` (default) |
| ALG-19a | Hardhat interval mining (`mining: { auto: true, interval: 1000 }`) | additionally mine every 1,000 ms | single process | testbed node | configured; which mode a given run used is recorded per run (`hardhat_getAutomine`) | `cv2x-testbed/hardhat.config.js` |
| ALG-20 | QBFT (Istanbul-family BFT, T-12) | deterministic finality at 2f_B+1 commit seals; round change on timeout | N_v ≥ 3f_B+1; partial synchrony (`PF-16`, `PF-17`) | SOL-02 Plane A | DESIGN | — |
| ALG-20a | IBFT 2.0 | QBFT's predecessor in Besu | as ALG-20 | — | not used | — |
| ALG-20b | Clique (EIP-225 PoA) | round-robin signer PoA, probabilistic-ish finality | honest majority of signers | dev and test networks; the `extraData` the PoA middleware tolerates | not used | — |
| ALG-20c | Gasper (Casper FFG + LMD-GHOST) | PoS finality per epoch pair | ⅔ stake honest; BLS (ALG-11) | Sepolia, mainnet (Option C) | DESIGN (M2 never run, #-none) | — |

#### L3.2 Client implementation

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L3.2-01 | Hyperledger Besu (Java) | EL client with QBFT, permissioning, privacy (Paladin O15) | IMP-L1.2-06; IMP-L2.2-02 | SOL-01 (as described in R2), SOL-02 | **DESIGN** — named only in `cv2x-testbed/V2_DESIGN.md` l. 391 ("Private Chains: Hyperledger Besu, Quorum") and F2 CAPTURE; no config, genesis or trace in this repo | — |
| IMP-L3.2-02 | Hardhat Network 2.28.6 (EthereumJS VM) | in-process / localhost dev chain | IMP-L1.2-05 | all M1, M1-H, M1-H/HTTP rows | MEASURED (#21, #39, #58) | `1_blockchain-identity/`, `cv2x-testbed/` |
| IMP-L3.2-03 | Geth | reference Go EL client | — | Sepolia nodes behind PRO-15 | not used directly | — |
| IMP-L3.2-04 | Anvil (Foundry) | Rust dev chain | — | R2's SOL-01 "Hardhat + Foundry harness" | not used in this repo | — |
| IMP-L3.2-05 | Ganache (`trufflesuite/ganache:latest`) | JS dev chain in the compose file; `ganache` network (port 7545) in the testbed config | — | IMP-LH.5-01 | configured, unused by MEASURED rows read | `docker-compose.yml`; `cv2x-testbed/hardhat.config.js` |
| IMP-L3.2-06 | Quorum (GoQuorum) | permissioned EL with Raft/IBFT/QBFT | — | — | DESIGN name only | `V2_DESIGN.md` l. 392 |

---

### L4 — Economics, governance and capacity

L4 decides who may write and how much writing the chain will accept. It gives L5 a price signal (or its absence) and an admission rule; it trusts L3 to enforce whatever the rule is. The repository measures gas exhaustively — gas is its main quantitative output (#1–#3, #22, #25, #29–#35, #47–#50, #54, #58) — but it measures gas as a *resource count*, not as a price: USD figures are ESTIMATED (#20) and the L2 fee parameter is "not a defensible figure" (F2 CAPTURE §5). Permissioning in the repository lives entirely in **contract roles** (L5.2 `onlyRegistryAuthority`, `ISSUER_ROLE`, `governor`), not in node or account permissioning; that is a substantive design fact for HAA-1, because a contract role is a single key while a validator set is a quorum.

#### L4.1 Fee model

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| ALG-21 | EVM gas schedule (cancun / paris) | per-opcode cost incl. EIP-2929 cold/warm access, EIP-2028 calldata 4/16 gas per byte | client conformance | every gas figure | MEASURED (all gas rows; zero-byte spread #22, #47) | register §1 rules |
| ALG-22 | EIP-1559 base fee + tip | congestion pricing | L3 block production | Option B/C cost (`PF-23`) | not exercised (local `gasPrice` from node) | `erc1056_provider.py` `_send_tx` uses legacy `gasPrice` |
| IMP-L4.1-01 | Free-gas consortium (`min-gas-price=0`) | no fee; capacity by governance | IMP-L4.2-01 | SOL-02 | DESIGN (`BP-L4-05`) | — |

#### L4.2 Permissioning and governance

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L4.2-01 | Besu node/account permissioning (local allowlist files or on-chain permissioning contracts) | who may peer, who may send tx | the permissioning contract's admin keys | SOL-02 write admission | DESIGN | — |
| IMP-L4.2-02 | QBFT validator-set governance (vote add/remove) | validator admission | ⅔ of validators | `BP-L4-04/06` | DESIGN | — |
| IMP-L4.2-03 | Contract-level roles: `registryAuthority` (MOBI), `ISSUER_ROLE` (1155), `MANUFACTURER_ROLE`/`SERVICE_CENTER_ROLE` (721), `governor` (ZkVinGate), `contractOwner` (CVDR), `owner` (LSP8, 735, 725xy) | issuer and manufacturer admission | **a single EOA key each** | SCF-MOBI1-01..03, SCF-E1155-*, SCF-ZKG-02 | MEASURED as attack cells (#28: 43/43 defended; #45: 15 checks 30/30) | §2.L5.2 |

#### L4.3 Capacity

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L4.3-01 | Block gas limit (Hardhat default; recorded per run) | per-block budget G (`SYM`, `PF-24`) | client config | ops/s | recorded as a field (`block_gas_limit`) in testbed results; value not quoted here | `experiment_pki_vs_erc1056.py` l. 548, 595 |
| IMP-L4.3-02 | `allowUnlimitedContractSize: true` | disables EIP-170 24,576-byte code limit | — | deploys of ERC-725xy/ERC-735 class contracts | used in M1 (register §1) — a **deployability caveat**: bytecode that relies on it would not deploy on a conformant chain | `1_blockchain-identity/hardhat.config.js` |

---

### L5 — Ledger semantics: the EVM, this repository's contracts, and transaction formats

L5 is where identity becomes code. It gives L6 functions that read and mutate identity state under rules (owner-only, role-only, signature-gated); it trusts L5.1's `ecrecover` to say who signed, L2.1 to keep the result, L3 to order it, and L4.2 for who holds the admin keys. The sub-layer that matters most to the thesis is L5.2: the 24 contract files are the thesis's artefact, and their access-control and signature discipline is where the repository's own defect log (D1–D66) concentrates. The register in §2.L5.2 lists every state-changing function and groups trivial getters.

#### L5.1 EVM and precompiles

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L5.1-01 | EVM (Shanghai/Cancun opcode set; `cancun` target in main tree, solc-default in testbed) | deterministic execution | client conformance to the Yellow Paper / EELS | every SCF | used | configs |
| PRO-16 | Precompile **0x01 `ecrecover`** | secp256k1 public-key recovery, returns address or empty | IMP-L1.2-05; **does not enforce low-s** (EIP-2 applies to tx signatures, not to the precompile — STANDARD) | SCF-EDR-04/06/08/10/12, SCF-CMB-07, SCF-E735-01, SCF-E4337A-01, SCF-SCH-01/02 | used | §2.L5.2 |
| PRO-17 | Precompile 0x02 `sha256` | SHA-256 in the EVM | IMP-L1.2-05 | not called by repo contracts | not used | — |
| PRO-18 | Precompiles **0x06 `ecAdd`, 0x07 `ecMul`, 0x08 `ecPairing`** (BN254, EIP-196/197, repriced EIP-1108) | G1 arithmetic and the pairing check | ALG-10 | SCF-G16-01 Groth16 verification | used (`staticcall(…, 6|7|8, …)`) — MEASURED in aggregate (#58: `verifyProof` view estimate 256,038 incl. 21,000 base) | `Groth16Verifier.sol` l. 94, 104, 178 |
| PRO-19 | Precompile 0x05 `modexp` | big-integer modexp | — | RSA/CL verifiers | not used | — |
| PRO-20 | EIP-2537 BLS12-381 precompiles (Pectra) | BLS12-381 ops | ALG-11 | BBS+/BLS verifiers | not used | — |
| IMP-L5.1-02 | `staticcall` / `delegatecall` / `call` semantics | external calls; context-preserving delegatecall | EVM | ERC-725X execute, 4337 execute, IDTX reads | used; `delegatecall` hazard D24 | `CVINVehicleERC725XY.sol` l. 287–306 |
| IMP-L5.1-03 | `block.timestamp`, `block.number`, `block.chainid` | chain time, height, chain id | proposer honesty (timestamp is proposer-set within client rules) | `validDelegate` expiry; `changed`; MOBI V2 attestation domain; IDTX deadlines | used — **chain time** is what D51 had to adopt for key validity | `EthereumDIDRegistry.sol` l. 127; `IdtxExecutor.sol` |

#### L5.2 Smart-contract function register (this repository)

Conventions. **SC** = state-changing; **V** = view/pure. "Root primitives" names the lower-layer tags each function's security rests on: `ecrecover → PRO-16/ALG-03/T-06`, `keccak → ALG-07/T-07`, `mapping → IMP-L2.1-03`, `events → IMP-L2.1-02`, `chain time → IMP-L5.1-03`. "F#" maps to IMinimalSSI per `docs/BASIC_ID_SET_EXTENSION.md` §1–2.1 (F1–F4, F9–F12 Set A; F5–F8 Set B; the exact F-number order inside Set A is marked **[B1]** in that file, so this register names the function rather than guessing a number where the source does not fix one). Access control is read from the source, not the tests; v0-2 will cross-check each against the security suite.

**SCF-EDR — `1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol` (uPort/DIF lineage; O1)**

| Tag | Function | SC/V | Access control | Events | IMinimalSSI / IDTX role | Root primitives |
|---|---|---|---|---|---|---|
| SCF-EDR-01 | `identityOwner(identity)` | V | — | — | resolve (Set A); IDTX Owner predicate | mapping; default-to-self |
| SCF-EDR-02 | `validDelegate(identity, type, delegate)` | V | — | — | R4 verify delegate; IDTX Delegate predicate | mapping; **chain time** |
| SCF-EDR-03 | `changeOwner(identity, newOwner)` | SC | `onlyOwner(identity, msg.sender)` | `DIDOwnerChanged(…, previousChange)` | key/controller rotation (U1) | tx signature (L5.3); mapping; events |
| SCF-EDR-04 | `changeOwnerSigned(identity, v, r, s, newOwner)` | SC | signature by current owner over `0x19 0x00 ‖ this ‖ nonce ‖ identity ‖ "changeOwner" ‖ newOwner` | as 03 | relayed rotation (U5 class) | **ecrecover**, keccak, `nonce` mapping; **no chain id (D52)**; zero-identity seizure (D53) |
| SCF-EDR-05 | `addDelegate(identity, type, delegate, validity)` | SC | `onlyOwner` | `DIDDelegateChanged` | delegates (U2) | mapping; chain time |
| SCF-EDR-06 | `addDelegateSigned(…)` | SC | owner signature | as 05 | relayed U2 | as 04 |
| SCF-EDR-07 | `revokeDelegate(identity, type, delegate)` | SC | `onlyOwner` | `DIDDelegateChanged` (validTo = now) | D1 revoke delegate | mapping; chain time |
| SCF-EDR-08 | `revokeDelegateSigned(…)` | SC | owner signature | as 07 | relayed D1 | as 04 |
| SCF-EDR-09 | `setAttribute(identity, name, value, validity)` | SC | `onlyOwner` | `DIDAttributeChanged` (value **only in the log**) | attributes (U3); issuer-key anchor (V1) | events; chain time |
| SCF-EDR-10 | `setAttributeSigned(…)` | SC | owner signature | as 09 | U5 meta-tx — MEASURED #50 (62,646 vs 35,024) | as 04 |
| SCF-EDR-11 | `revokeAttribute(identity, name, value)` | SC | `onlyOwner` | `DIDAttributeChanged` (validTo 0) | D2 revoke attribute; V5 | events |
| SCF-EDR-12 | `revokeAttributeSigned(…)` | SC | owner signature | as 11 | relayed D2 | as 04 |
| — | public mappings `owners`, `delegates`, `changed`, `nonce` | V | — | — | resolver walk start (`changed`) | mapping |

**SCF-CVDR — `ERC1056/CVINVehicleDIDRegistry.sol` (vehicle wrapper over SCF-EDR; O1 "wrapper mode")**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-CVDR-01 | `setAuthorizedManufacturer(m, bool)` | SC | `onlyContractOwner` | `ManufacturerAuthorized` | issuer admission (L4.2) | single admin key |
| SCF-CVDR-02 | `createVehicleDID(vin, owner, make, model, year, …)` | SC | `onlyAuthorizedManufacturer` | `VehicleDIDCreated` | createDID (+VIN binding, C2) — MEASURED #1 | keccak(VIN) map; D20 reverse-map overwrite |
| SCF-CVDR-03 | `setVehicleAttributes(did, …)` | SC | `onlyVehicleOwner(did)` | via EDR `DIDAttributeChanged` | attributes | D18: passes `uint256.max` validity → arithmetic panic in EDR (birth record unreachable) |
| SCF-CVDR-04 | `transferVehicleOwnership(did, newOwner)` | SC | `onlyVehicleOwner` | `VehicleOwnershipTransferred` | U4 ownership transfer | D19 wrapper custody |
| SCF-CVDR-05 | `updateOwnershipMapping(old, new)` | SC | requires `didRegistry.identityOwner(old) == new` (the ERC-1056 rotation must already have happened) | — | bookkeeping of the VIN map after U1 | keccak(VIN); reads SCF-EDR-01 |
| SCF-CVDR-06 | `setServiceEndpoint(did, type, url, validity)` | SC | `onlyVehicleOwner` | via EDR | service endpoints | D1 fixed |
| SCF-CVDR-07 | `addVerificationDelegate(…)` | SC | `onlyVehicleOwner` | via EDR | U2 | — |
| SCF-CVDR-08 | `revokeVerificationDelegate(…)` | SC | `onlyVehicleOwner` | via EDR | D1 | — |
| SCF-CVDR-09 | getters `getDIDFromVIN`, `getVINFromDID`, `vehicleOwnerOf`, `getVehicleOwner`, `isValidDelegate` | V | — | — | R1/R2 | **`getVINFromDID` returns the VIN in plaintext from storage** (G7 relevant) |

**SCF-VPR — `MOBI/ERC1056Registry.sol` ≡ `cv2x-testbed/contracts/ERC1056Registry.sol` (vehicle profile; #21–#22)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-VPR-01 | `identityOwner`, `isRevoked`, `lastChanged`, `getIdentityInfo` | V | — | — | resolve; the **one-call probe** (#37) | mapping |
| SCF-VPR-02 | `changeOwner(identity, newOwner)` | SC | `onlyOwner` + `notRevoked` (internal) | `DIDOwnerChanged` | U1 | D26 `changeOwner(0)` restores self-control |
| SCF-VPR-03 | `addDelegate(…)` | SC | `onlyOwner` + `notRevoked` | `DIDDelegateChanged` | U2 | chain time |
| SCF-VPR-04 | `revokeDelegate(…)` | SC | as 03 | as 03 | D1 | — |
| SCF-VPR-05 | `setAttribute(…)` | SC | as 03 | `DIDAttributeChanged` | U3 / V1 — MEASURED #22 "issue" 37,807 | events |
| SCF-VPR-06 | `revokeAttribute(…)` | SC | as 03 | as 05 | D2 | D16 rest: mismatched value accepted |
| SCF-VPR-07 | `revokeIdentity(identity)` | SC | `onlyOwner` | `DIDRevoked` (**no `previousChange`**, D21) | F-deactivation (D3) — MEASURED #22 revoke 75,609 | severs resolver walk |
| SCF-VPR-08 | `registerVehicle(identity, publicKey)` | SC | caller must be the identity itself (via `onlyOwner(identity, msg.sender)` inside `setAttribute`); not revoked; not yet transferred | `DIDAttributeChanged` (key attribute, 1-year validity) | createDID (explicit) — MEASURED #22 register 54,868 | the testbed's key for this call is SHA-256(vehicle_id) (IMP-LH.1-02) |
| SCF-VPR-09 | `updateVehicleKey(identity, newKey)` | SC | `onlyOwner` + `notRevoked` | `DIDAttributeChanged` | key rotation | — |

**SCF-MOBI1 — `MOBI/MOBIVIDRegistry.sol` (extends VPR; MOBI VID I)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-MOBI1-01 | `authorizeManufacturer(m)` | SC | `onlyRegistryAuthority` | `ManufacturerAuthorized` | issuer admission | single authority key |
| SCF-MOBI1-02 | `revokeManufacturerAuthorization(m)` | SC | `onlyRegistryAuthority` | `ManufacturerAuthorizationRevoked` | issuer revocation | — |
| SCF-MOBI1-03 | `transferRegistryAuthority(new)` | SC | `onlyRegistryAuthority` | (silent — D16 rest) | governance handover | **governance key = root of the whole registry** |
| SCF-MOBI1-04 | `registerVehicleBirth(identity, vinHash, encryptedVIN, birthCertHash, firstOwner, attrs)` | SC | `onlyAuthorizedManufacturer`, `vehicleNotRegistered` | `VehicleBirthRegistered` | createDID + issueCredential (birth) | salted `vinHash` + AES-GCM ciphertext (ALG-17); undermined by D64 address derivation |
| SCF-MOBI1-05 | `addDelegate` / `revokeDelegate` (overrides) | SC | VPR rules + registered | as VPR | U2 / D1 | — |
| SCF-MOBI1-06 | `anchorVehicleKey(identity, publicKey)` | SC | owner, or registering manufacturer once before any transfer; 33/65-byte key | `VehicleKeyAnchored(keccak(pk))` | issuer-key anchor for the vehicle's message key (D11b fix) | keccak; permanent attribute validity |
| SCF-MOBI1-07 | `changeOwner` (override) | SC | VPR + MOBI rules | `DIDOwnerChanged` | U1 | D16: earlier bypass of revoked flag / history |
| SCF-MOBI1-08 | `transferVehicleOwnership(identity, newOwner, odometer, authority)` | SC | `vehicleRegistered`, `onlyOwner` | `VehicleOwnershipTransferred` | U4 | odometer is caller-asserted (LH.3 unbound) |
| SCF-MOBI1-09 | getters `getVehicleBirth`, `lookupByVINHash`, `getOwnershipHistory(+Count)`, `vehicleExists`, `getVehicleInfo`, `getVehicleDID`, `validDelegate` | V | — | — | R1/R2/R3; did:mobi resolution | D10 fixed (`0x` in did:ethr string) |

**SCF-MOBI2 — `MOBI/MOBIVIDRegistryV2.sol` (extends MOBI1; MOBI VID II lifecycle)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-MOBI2-01 | `authorizeIssuer(issuer, role)` | SC | `onlyRegistryAuthority` | `IssuerAuthorized` | issuer admission (roles OWNER, DEALER, …) | registry-wide roles (D16) |
| SCF-MOBI2-02 | `revokeIssuerAuthorization(issuer)` | SC | `onlyRegistryAuthority` | `IssuerAuthorizationRevoked` | issuer revocation | — |
| SCF-MOBI2-03 | `recordLifecycleEvent(identity, type, odometer, dataHash, credentialHash, jurisdiction)` | SC | `vehicleRegistered`, `onlyAuthorizedIssuer(type)`, not revoked; OWNER-role must also be current owner (K-15) | `LifecycleEventRecorded` | issueCredential (lifecycle) — MEASURED #33 lifecycle event 255,267 gas | keccak eventId; `dataHash` body off-chain, discarded (IMP-L2.3-05) |
| SCF-MOBI2-04 | `attestEvent(eventId, identity, signature)` | SC | role-holder **and** owner or valid `veriKey` delegate (D54, C2); once per attester | `EventAttested` | endorsement / co-signature — MEASURED #28 (198,694 execution gas) | **OZ ECDSA.recover (low-s, non-zero)** over EIP-191(keccak(this ‖ chainid ‖ identity ‖ eventId)); chain-bound |
| SCF-MOBI2-05 | getters `isAuthorizedIssuer`, `getVehicleEvents`, `getEvent`, `getEventAttestations`, `getEventTypeCount`, `getCompleteHistory`, `getEventsByType`, `getOdometerHistory` | V | — | — | verifyCredential (status read, V6) | — |

**SCF-CMB — `CVINCombined/CVINCombinedIdentity.sol` (ERC-1056 + ERC-735 hybrid; thesis's own)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-CMB-01 | `changeOwner` | SC | `onlyIdentityOwner` | `DIDOwnerChanged` | U1 | D26 |
| SCF-CMB-02 | `addDelegate` | SC | `onlyIdentityOwner` | `DIDDelegateChanged` | U2 | — |
| SCF-CMB-03 | `revokeDelegate` | SC | `onlyIdentityOwner` | as 02 | D1 | D22 rest: stores a timestamp |
| SCF-CMB-04 | `setAttribute` | SC | `onlyIdentityOwner` | `DIDAttributeChanged` | U3 — MEASURED #34 (51,742) | events |
| SCF-CMB-05 | `revokeAttribute` | SC | `onlyIdentityOwner` | as 04 | D2 | — |
| SCF-CMB-06 | `addClaim(identity, topic, scheme, issuer, sig, data, uri)` | SC | `onlyIdentityOwner`; issuer signature verified at add time | `ClaimAdded`, `DIDClaimChanged` | issueCredential (on-chain claim) | **raw ecrecover over keccak(this ‖ identity ‖ topic ‖ data); no low-s guard (D22)**; revoked-content check |
| SCF-CMB-07 | `removeClaim(identity, claimId)` | SC | the identity's owner or the claim's issuer | `ClaimRemoved` | revokeCredential (holder side) | D22: bumps `changed` without ERC-1056 event |
| SCF-CMB-08 | `revokeClaimContent(identity, topic, data)` | SC | any caller, records keccak(msg.sender ‖ digest) — can only revoke its own issuance | `ClaimRemoved` if present | revokeCredential (issuer side) | keccak |
| SCF-CMB-09 | getters `identityOwner`, `validDelegate`, `getClaim`, `getClaimIdsByTopic`, `hasValidClaim` | V | — | — | verifyCredential (O(1) on-chain claim check, #36) | mapping |

**SCF-E735 — `ERC735/CVINVehicleClaimHolder.sol` (per-vehicle claim holder; O6)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-E735-01 | `addClaim(topic, scheme, issuer, sig, data, uri)` | SC | `onlyOwner`; issuer must be authorised for topic (D25a); VIN attestation must encode the holder's VIN (D25b) | `ClaimAdded`/`ClaimChanged` | issueCredential — MEASURED #34 create 1,757,881 (incl. deploy) | **EIP-191-prefixed** ecrecover (D25c: inconsistent with SCF-CMB-06 raw digest) |
| SCF-E735-02 | `removeClaim(claimId)` | SC | owner or issuer | `ClaimRemoved` | revoke (holder) | — |
| SCF-E735-03 | `revokeClaimContent(topic, data)` | SC | any caller, own issuance only | — | revoke (issuer) | keccak |
| SCF-E735-04 | `authorizeIssuer(issuer, topic)` / `revokeIssuer(issuer, topic)` | SC | `onlyOwner` | `IssuerAuthorized` / `IssuerRevoked` | trust-list management | single owner key |
| SCF-E735-05 | `transferOwnership(new)` | SC | `onlyOwner` | `OwnershipTransferred` | U4 | — |
| SCF-E735-06 | getters `getClaim`, `getClaimIdsByTopic`, `claimExists`, `isAuthorizedIssuer` | V | — | — | verify | — |

**SCF-E725B — `ERC725/CVIN_DID_ERC725.sol` (`CVIN_SCBasedAccOrID_DID_ERC725Basic`; O5)**

| Tag | Function | SC/V | Access control | Events | Role | Notes |
|---|---|---|---|---|---|---|
| SCF-E725B-01 | `transferOwnership`, `renounceOwnership` | SC | `msg.sender == _owner` | `OwnershipTransferred` | U4 / lock | — |
| SCF-E725B-02 | `addKey(key, purpose, type)`, `removeKey(key)` | SC | owner | `KeyAdded`/`KeyRemoved` | key management | D23 dangling `getKeys` entry |
| SCF-E725B-03 | `execute(op, to, value, data)` | SC | owner | `Executed` | agent proxy (F-execute) | **stub: performs no call (D23)** |
| SCF-E725B-04 | `approve(id, bool)` | SC | public no-op (D23) | — | — | — |
| SCF-E725B-05 | getters `owner`, `getKey`, `getKeys` | V | — | — | resolve | — |

**SCF-E725XY — `ERC725xy/CVINVehicleERC725XY.sol` (full ERC-725 X+Y; O6 base) and SCF-EXT — `CVINExecuteTarget.sol` (test target)**

| Tag | Function | SC/V | Access control | Events | Role | Notes |
|---|---|---|---|---|---|---|
| SCF-E725XY-01 | `transferOwnership`, `renounceOwnership` | SC | `onlyOwner` | `OwnershipTransferred` | U4 | — |
| SCF-E725XY-02 | `setData`, `setDataBatch` (payable) | SC | `onlyOwner` | `DataChanged` | U3 attributes (stored, not logged-only) | D24: payable; VIN rewritable |
| SCF-E725XY-03 | `setVehicleBirthAttributes(vin, make, model, year)` | SC | `onlyOwner` | `DataChanged` | createDID attributes | VIN in storage |
| SCF-E725XY-04 | `execute(opType, target, value, data)`, `executeBatch` | SC | `onlyOwner` | `Executed`, `ContractCreated` | agent proxy X1 — MEASURED #54 | CALL / STATICCALL / **DELEGATECALL (D24 slot-0 overwrite)** / CREATE / CREATE2 |
| SCF-E725XY-05 | getters `owner`, `getData`, `getDataBatch`, `getVehicleVIN`, `supportsInterface` | V | — | — | resolve | — |
| SCF-EXT-01 | `setValue(v)`, `willRevert()` | SC / pure | none | `ValueSet` | test target for X1 | — |

**SCF-E1155 — `ERC1155/CVINVehicleCredential1155.sol` (O2)**

| Tag | Function | SC/V | Access control | Events | Role | Notes |
|---|---|---|---|---|---|---|
| SCF-E1155-01 | `registerVehicle(vehicle, vin)` | SC | `onlyRole(ISSUER_ROLE)` | `VehicleRegistered` | createDID | `_normalizeVIN` (D13); keccak(VIN) |
| SCF-E1155-02 | `issueCredential(vehicle, type, amount)` | SC | `ISSUER_ROLE` | `CredentialIssued` | issueCredential | flat issuer role (D8 rest) |
| SCF-E1155-03 | `revokeCredential(vehicle, type, amount)` | SC | `ISSUER_ROLE` | `CredentialRevoked` | revokeCredential | any issuer may revoke another's (D8 rest) |
| SCF-E1155-04 | `issuerTransferCredential(from, to, type, amount)` / `issuerTransferIdentity(from, to)` | SC | `ISSUER_ROLE` | `IdentityRebound` | U4 (issuer-mediated) | D6, D7 fixed |
| SCF-E1155-05 | `setTokenURI(type, uri)` | SC | `onlyRole(ISSUER_ROLE)` | `CredentialURIUpdated` / `URI` | metadata | — |
| SCF-E1155-06 | `safeTransferFrom`, `safeBatchTransferFrom` (overridden, revert) | pure | — | — | soulbound property (G8) | — |
| SCF-E1155-07 | getters `uri`, `isRegistered`, `hasCredential`, `credentialTypesOf`, `vinHashOf`, `vehicleForVIN`, `supportsInterface` | V | — | — | verify | `vinHashOf` is unsalted keccak(VIN) — enumerable (cf. #60) |

**SCF-E721N — `ERC721/CVINVehicleNFT.sol` (O3); SCF-E721T — `CVIN_NFT_DID_ERC721.sol` (toll demo); SCF-E721M — `CVIN_NFT_DID_ERC721_Monolithic.sol`**

| Tag | Function | SC/V | Access control | Events | Role | Notes |
|---|---|---|---|---|---|---|
| SCF-E721N-01 | `mintVehicle(to, vin, make, model, year, color, uri)` | SC | `MANUFACTURER_ROLE` | `VehicleMinted` | createDID — MEASURED #3, #29 | D13 normalisation |
| SCF-E721N-02 | `addServiceRecord(tokenId, uri)` | SC | `SERVICE_CENTER_ROLE` | `ServiceRecordAdded` | lifecycle credential | body off-chain (URI) |
| SCF-E721N-03 | `deactivateVehicle(tokenId)` | SC | `DEFAULT_ADMIN_ROLE` | `VehicleDeactivated` | deactivation | D14: advisory, irreversible |
| SCF-E721N-04 | `grantManufacturerRole`, `grantInspectorRole`, `grantServiceCenterRole` | SC | `DEFAULT_ADMIN_ROLE` | OZ `RoleGranted` | governance | D14: inspector role gates nothing |
| SCF-E721N-05 | `_update` override (transfer hook) and standard ERC-721 transfers | SC | token owner / approved | `Transfer`, `VehicleTransferred` | U4 | transfer history kept |
| SCF-E721N-06 | getters `getServiceRecords`, `getTransferHistory`, `getOwnershipChain`, `isVehicleActive`, `getVehicleDID`, `getTokenIdFromVIN`, `getVINFromTokenId`, `getVehiclesByOwner`, `getTotalVehicles`, `tokenURI` | V | — | — | resolve | plaintext VIN getters |
| SCF-E721T-01 | `mint(to, id, uri)` | SC | `onlyOwner` | `Transfer` | createDID (toll demo) | — |
| SCF-E721T-02 | `recordEntry(id, ts)` | SC | `onlyOwner` | `EntryRecorded` | toll scenario (L7.3) | operator-asserted timestamp |
| SCF-E721T-03 | `payToll(id)` (payable) | SC | any payer | `TollPaid` | payment IDTx-like | value `call` to operator; D9 fixed (reverts after renounce) |
| SCF-E721M-01 | `mint`, `approve`, `setApprovalForAll`, `transferFrom`, `safeTransferFrom`×2 | SC | ERC-721 rules / `onlyOwner` for mint | `Transfer`, `Approval`, `ApprovalForAll` | hand-written ERC-721 baseline | D2 fixed (`_balances += 1`); `_checkOnERC721Received` external call |
| SCF-E721M-02 | getters `name`, `symbol`, `balanceOf`, `ownerOf`, `tokenURI`, `getApproved`, `isApprovedForAll`, `royaltyInfo`, `supportsInterface` | V | — | — | — | — |

**SCF-LSP8 — `LSP8/CVINVehicleLSP8.sol` (minimal LSP8 representative)**

| Tag | Function | SC/V | Access control | Events | Role | Notes |
|---|---|---|---|---|---|---|
| SCF-LSP8-01 | `mintVehicle(owner, vin)` | SC | `onlyOwner` | `Transfer`, `VehicleMinted` | createDID; tokenId = keccak(normalised VIN) | enumerable tokenId (unsalted) |
| SCF-LSP8-02 | `transfer(from, to, tokenId, force, data)` | SC | token owner / operator (source) | `Transfer` | U4 | D12: no LSP1 probing |
| SCF-LSP8-03 | `revokeVehicle(tokenId, data)` | SC | collection owner or token owner | `Transfer` to 0, `VehicleRevoked` | deactivation | generation counter |
| SCF-LSP8-04 | `setDataForTokenId`, `setDataBatchForTokenIds` | SC | `onlyOwner` (authority) | `TokenIdDataChanged` | attributes | D12: VIN key overwritable |
| SCF-LSP8-05 | `transferOwnership` | SC | `onlyOwner` | `OwnershipTransferred` | governance | — |
| SCF-LSP8-06 | getters `totalSupply`, `balanceOf`, `tokenOwnerOf`, `tokenIdsOf`, `tokenIdForVIN`, `exists`, `getDataForTokenId`, `getDataBatchForTokenIds` | V | — | — | resolve | — |

**SCF-E4337A — `ERC4337/CVINVehicleAccount.sol`; SCF-E4337EP — `CVINMinimalEntryPoint.sol` (O7, minimal representative)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-E4337A-01 | `validateUserOp(userOp, hash, missingFunds)` | SC | called by EntryPoint | — | authentication of a UserOp | **raw ecrecover over EIP-191(userOpHash)**, rejects zero address; no low-s guard; prefund `call` |
| SCF-E4337A-02 | `execute(target, value, data)` | SC | `onlyOwnerOrEntryPoint` | `Executed` | agent proxy X1 | arbitrary `call` |
| SCF-E4337A-03 | `transferOwnership(new)` | SC | `onlyOwnerOrEntryPoint` | `OwnershipTransferred` | U1/U4 | — |
| SCF-E4337A-04 | `setGuardian(g)` | SC | `onlyOwnerOrEntryPoint` | `GuardianChanged` | recovery setup (I9) | — |
| SCF-E4337A-05 | `recoverOwner(new)` | SC | `msg.sender == guardian` only; **no time-lock, no threshold** | `OwnerRecovered` | social recovery (G6) | D15: guardian persists as super-owner; `PF-30` |
| SCF-E4337A-06 | `setAttribute(key, value)` / `getAttribute(key)` | SC / V | `onlyOwnerOrEntryPoint` | `AttributeChanged` | U3 — MEASURED #34 (94,651) | storage |
| SCF-E4337EP-01 | `handleOp(userOp)` | SC | anyone; nonce must match | `UserOperationHandled` | UserOp execution — MEASURED #25 (+46,830/op), #50 (+47,116) | userOpHash = keccak(packed ‖ entryPoint ‖ **chainid**); D15: nonce rolls back on inner revert |
| SCF-E4337EP-02 | `getUserOpHash`, `nonces` | V | — | — | — | keccak |

**SCF-IDC / SCF-IDTX — `phase2/idtx/contracts/IdtxExecutor.sol` (SOL-10)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-IDC-01 | `setCommitment(identity, key, commitment, until)` | SC | `registry.identityOwner(identity) == msg.sender` | `CommitmentSet` | IDTX Commitment dependency source | external `staticcall`-like read of SCF-EDR-01; chain time |
| SCF-IDC-02 | `revokeCommitment(identity, key)` | SC | identity owner | `CommitmentRevoked` | revocation of the dependency | — |
| SCF-IDC-03 | `valueOf(identity, key)` | V | — | — | returns zero if expired or setter no longer owner (AR-6) | chain time; SCF-EDR-01 |
| SCF-IDTX-01 | `holds(dep)` | V | — | — | the identity predicate (Owner / Delegate / Commitment); **independent of msg.sender** (AR-4) | SCF-EDR-01/02, SCF-IDC-03 |
| SCF-IDTX-02 | `execute(dep, action)` | SC | anyone; requires `holds` | `Executed` | same-transaction IDTx | atomicity (L5.1) |
| SCF-IDTX-03 | `createIntent(dep, action, deadline)` | SC | anyone | `IntentCreated` | next-transaction IDTx step 1 | chain time |
| SCF-IDTX-04 | `fulfil(id)` | SC | anyone (keeper); re-evaluates `holds` | `IntentFulfilled`, `Executed` | next-transaction IDTx step 2 | no TOCTOU on chain; keeper liveness off chain |
| SCF-IDTX-05 | `intentCount()` | V | — | — | — | — |

**SCF-G16, SCF-ZKG, SCF-SCH — `5_zkp-agent-identity/contracts/` (SOL-11)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes |
|---|---|---|---|---|---|---|
| SCF-G16-01 | `verifyProof(pA, pB, pC, pubSignals[7])` | V | — | — | Groth16 verification (snarkjs-generated) | **PRO-18 0x06/0x07/0x08**; `checkField` on public signals; verification key constants from an **insecure single-party setup** |
| SCF-ZKG-01 | `anchorCommitment(identity, commitment)` | SC | `registry.identityOwner(identity) == msg.sender` | `CommitmentAnchored` | issuer-free credential anchor — MEASURED #58 (51,558) | Poseidon commitment value; ERC-1056 read |
| SCF-ZKG-02 | `setService(serviceId, scope, minYear, region, challenge)` | SC | `governor` only | `ServiceSet` | verifier policy registration | single governor key; static challenge per service |
| SCF-ZKG-03 | `admit(identity, serviceId, a, b, c, pub, action)` | SC | anyone with a valid proof; signals must equal anchored commitment, `mfrRoot`, service fields; nullifier unused in scope | `Admitted` | **IDTx with knowledge-of-opening dependency**; createPresentation-like (F8) — MEASURED #58 (301,163) | SCF-G16-01; nullifier map; Poseidon (in circuit) |
| SCF-ZKG-04 | public getters `commitmentOf`, `services`, `nullifierUsed`, `mfrRoot`, `governor` | V | — | — | — | — |
| SCF-SCH-01 | `verify(parity, px, message, e, s)` | pure | — | — | Schnorr PoK check | ALG-15 via PRO-16 |
| SCF-SCH-02 | `prove(…)` | SC | anyone | `Proved` | on-chain PoK record — MEASURED #58 (28,775) | as 01; no replay guard (a proof can be re-submitted) |

Register summary: **22 prefixes**, **117 SCF rows** counting each grouped getter row once (v0-2 will produce the exact per-function count from the ABIs). Signature schemes in use across the 9 signature-verifying contracts are **three**: raw-digest `ecrecover` (EDR, CMB), EIP-191-prefixed `ecrecover` (E735, E4337A), and OpenZeppelin ECDSA with low-s and chain id (MOBI2). Only MOBI2 and the 4337 EntryPoint bind `block.chainid`; EDR binds neither chain id nor low-s.

#### L5.3 Transaction formats

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| PRO-21 | Legacy tx with **EIP-155** chain id in v | replay protection across chains for the *outer* tx | ALG-02 | every SC call | used (`build_transaction` with `gasPrice`; eth_account adds chain id) | `erc1056_provider.py` `_send_tx` |
| PRO-21a | EIP-2930 access-list tx (type 1) | pre-declared storage access | as above | gas optimisation | not used | — |
| PRO-21b | EIP-1559 tx (type 2) | base-fee/tip pricing | as above | Option B/C | default in ethers v6 on chains that support it; not separately recorded | — |
| PRO-21c | EIP-4844 blob tx (type 3) | data blobs for rollups | KZG (BLS12-381) | Option B anchoring cost | not used | — |
| PRO-21d | EIP-7702 set-code tx (type 4) | EOA delegates to code (O8) | ALG-02 | O8 | not used | — |
| PRO-22 | ERC-4337 UserOperation (PackedUserOperation) | account-abstraction intent via EntryPoint | SCF-E4337A-01 | O7 relayed path | MEASURED (#25, #34, #50) with a **minimal** EntryPoint (no bundler, no paymaster, no prefund) | `ERC4337/` |
| PRO-22a | ERC-1056 signed meta-transaction (`*Signed`) | in-contract relayed write | SCF-EDR-04 digest | U5 | MEASURED (#50) | `EthereumDIDRegistry.sol` |
| PRO-22b | EIP-191 personal-sign / EIP-712 typed data | off-chain message signing | ALG-02 | VC proofs (`eip191-secp256k1-recovery-2024`), attestations | EIP-191 used; EIP-712 not used | `vc_issuer.py`; `MOBIVIDRegistryV2.sol` |

---

### L6 — Identity

L6 is where the stack starts answering the questions the thesis is about: *which key speaks for this vehicle now* (I1, I3), *what has an issuer said about it* (I4–I5), and *can that be shown without showing everything* (I6). It gives L7 a resolver that turns a DID string into a document, a credential that a verifier can check offline, and — new in this repository — functions whose effect depends on an identity's state (IDTX). It trusts L5.2's registries for the authoritative state, L0.4 for reading it, and L1 for every signature. The repository is unusually concrete here: did:ethr resolution reads the registry when given a provider (WM-2 C1, report 21), fails closed on RPC error, and passes 335/336 of the external W3C DID test suite (#24). It is also explicit about its deviations: the VC layer uses a thesis-defined cryptosuite and deterministic JSON instead of URDNA2015 (`vc_issuer.py` header). No AnonCreds, BBS+, mDL or did:indy code exists in the tree.

#### L6.1 DID methods

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| ALG-23 | **did:ethr** resolution (ERC-1056 event replay) | start at `changed[identity]`, walk `previousChange` backwards via `eth_getLogs`, replay owner/delegate/attribute events forward (ethr-did-resolver mapping); fail closed | SCF-EDR-01/02, IMP-L2.1-02/04; PRO-13; chain time for `validTo` (D51 fix) | L7 verifiers; VC issuer-key lookup | MEASURED: #24 (335/336 external suite), #31/#51 (14 → 32 → 112 RPC calls at h = 1/10/50; median 91.113 ms at h = 50 in-process), #21 (15.513 ms uncached verify, testbed variant) | `2_w3c-ssi-layer/did-resolution/did_resolver.py`; `cv2x-testbed/identity/erc1056_provider.py`; JS `ethr-did-resolver ^10.1.0` |
| ALG-23a | did:ethr **offline synthesis** | build a document from the DID string alone; marked `cvinResolutionMode: "offline-synthesized"` | nothing on chain (key = address) | M0 hot path | used (default mode) | `did_resolver.py` header |
| ALG-24 | **did:mobi** resolution | `did:mobi:<salted VIN hash>` → `MOBIVIDRegistry.lookupByVINHash` → `getVehicleDID` → ERC-1056 state in the MOBI registry | SCF-MOBI1-09; VPR state | MOBI VID scenarios | used; `cvinResolutionMode: "mobi-vid-registry"` | same |
| ALG-24a | did:nft, did:key (as used here for ERC-725 proxies), did:web | resolver branches | contract reads or synthesis | comparison breadth | used (resolver supports ethr, nft, key, mobi, web — F2 CAPTURE §5) | `did_resolver.py` l. 12–15, 59 |
| IMP-L6.1-01 | did:indy / Indy-Besu (O10/O11) | purpose-built registry | RBFT / QBFT | SOL-07 | not used | — |
| IMP-L6.1-02 | CAIP-10 `blockchainAccountId` | chain-qualified account in the document | spec | interop | used; D27 (hex vs decimal chain reference) | `did_resolver.py` |

#### L6.2 Credential formats

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L6.2-01 | W3C VC Data Model **v2.0** with `DataIntegrityProof`, cryptosuite `eip191-secp256k1-recovery-2024` (thesis-defined) | issuer signs deterministic JSON with EIP-191; verifier recovers the address offline | ALG-03, PRO-22b; ALG-23 for issuer key | F5/F6; V2V warm verify | MEASURED: #4 (internal checker 94.3 %), #27 (warm 0.142 ms median), #55 | `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py`, `vc_verifier.py`, `vc_holder.py` |
| IMP-L6.2-02 | SD-JWT-style salted claim digests | holder discloses subsets; credential signs only digests | ALG-08 salts | F8 createPresentation (off-chain) | used | `vc_issuer.py` header |
| IMP-L6.2-03 | VC-JWT / JOSE (`did-jwt` Python 0.1.0 dependency) | JWT envelope | T-I09 | interop | dependency listed; not shown in MEASURED rows | `requirements.txt` |
| IMP-L6.2-04 | JSON-LD URDNA2015 canonicalisation (`pyld==2.0.3` listed) | RDF dataset canonicalisation | spec | full Data Integrity conformance | **documented deviation** (not used for proofs) | `vc_issuer.py` l. 12–14 |
| IMP-L6.2-05 | MOBI VID birth certificate and lifecycle events (Python) | VID I/II payloads; hash on chain, body off chain | SCF-MOBI1-04, SCF-MOBI2-03 | MOBI scenarios | used | `2_w3c-ssi-layer/mobi-vid/` |
| IMP-L6.2-06 | ZK-VIN commitment credential (Poseidon(VIN, year, region, salt)) | a credential whose presentation is a Groth16 proof | ALG-09, ALG-12 | SOL-11 | MEASURED (#56–#58) | `5_zkp-agent-identity/` |
| IMP-L6.2-07 | AnonCreds (O12), BBS+ Data Integrity, ISO mDL / mdoc (COSE) | anonymous or device-bound credentials | ALG-16; COSE | I6/I7 at native strength | not used | — |

#### L6.3 IDTX functions

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L6.3-01 | IMinimalSSI F1–F12 (Set A / Set B) as realised by the ten harness adapters | the basic digital-ID set | the adapters' contracts (§2.L5.2) | admission and comparison | MEASURED: #53 (Set A 11/11 or 10/11 per substrate), #54 (P1 createPresentation and X1 execute gas) | `docs/BASIC_ID_SET_EXTENSION.md`; `test/benchmarks/adapters.conformance.test.js` |
| IMP-L6.3-02 | **IdtxExecutor** + IdentityCommitments (SOL-10) | Owner / Delegate / Commitment dependency; same-tx `execute`; next-tx `createIntent`/`fulfil` with re-evaluation | SCF-EDR-01/02; SCF-IDC-03; chain time | tolls, insurance, keeper actions | DESIGN-with-code: prototype compiled under `hardhat.phase2.config.js`; "No number from this prototype is a result" (source header) | `phase2/idtx/contracts/IdtxExecutor.sol` |
| IMP-L6.3-03 | **ZkVinGate.admit** (SOL-11) | IDTx whose dependency is knowledge of a commitment opening, with a per-scope nullifier | SCF-G16-01; SCF-ZKG-01 | privacy-preserving admission | MEASURED (#58) | `5_zkp-agent-identity/contracts/ZkVinGate.sol` |
| IMP-L6.3-04 | MOBI V2 `attestEvent` as co-signed endorsement | owner-consented attestation, chain-bound signature | SCF-MOBI2-04 | lifecycle trust | MEASURED (#28) | `MOBIVIDRegistryV2.sol` |

---

### L7 — Application and identity-to-identity communication

L7 is where the vehicle meets another vehicle, an RSU, a toll operator or an insurer, and every lower layer is cashed in a single decision: *accept this message from this sender now, or not*. It gives the safety and service applications that decision within a budget (the identity budget is 50 ms of the 100 ms BSM interval — `docs/LATENCY_BUDGET.md` §1, a project choice from SAE J2945/1 cadence); it trusts L6 for keys and status, L1 for signatures, and — the hidden one — LH.4 for the clock its freshness rule compares against. The repository's L7 is a set of Python providers and simulators: it signs JSON, not ASN.1; it carries a DID or a PEM certificate, not a 1609.2 `SignedData` structure; and its radio is a model. Within that frame it is rigorous: the freshness module binds generation time inside the signature and runs a bounded replay cache; verifier v3 fixed six defects (D37–D42); the infrastructure gates I1–I5 are pre-registered (#44–#48).

#### L7.1 Wallet and agent software

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L7.1-01 | ethers v6 / Hardhat ethers | JS wallet and contract client | IMP-L1.2-04 | harness, tests (562 Hardhat per STATUS §5) | used | `1_blockchain-identity/` |
| IMP-L7.1-02 | web3.py 6.x + eth-account | Python wallet and contract client | IMP-L1.2-03 | testbed providers, MOBI registry client | used | `requirements.txt` (`web3==6.11.0`, `>=6.0.0`) |
| IMP-L7.1-03 | ethr-did (JS) + ethr-did-resolver | JS DID tooling | ALG-23 | conformance | dependency (`ethr-did ^2.3.0`, `ethr-did-resolver ^10.1.0`) | `1_blockchain-identity/package.json` |
| IMP-L7.1-04 | Identity providers: `erc1056_provider`, `mobi_vid_provider`, `centralized_provider`, `pki_identity`, `lifecycle_backends`, `comparison_framework` | sign/verify/register/revoke per substrate under one interface (`base.py`) | the L6/L5 layers per provider | every testbed row (#21, #32, #33, #37) | used | `cv2x-testbed/identity/` |
| IMP-L7.1-05 | **Steward** agent (vault, policy, compiler, kernel, leakage audit, learner, delegation, audit log) | wraps the vehicle identity; turns owner rules into a signed policy; computes proofs; bounds leakage | IMP-L1.2-09; ALG-14; vault discipline (no value getter) | SOL-14 | MEASURED in Sim: #61 (twenty-questions attack and defences), README headline "≤ 3.0 bits on 90/90 runs" (Sim) | `5_zkp-agent-identity/steward/` |
| IMP-L7.1-06 | Veramo, ACA-Py, Credo-TS (O17) | full SSI agents | DIDComm, AnonCreds | SOL-07 | not used | — |

#### L7.2 Messaging protocols

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L7.2-01 | **Freshness module** (`signed_bytes`, window `max_age_s` 1.0 s / `max_future_s` 0.1 s, bounded replay cache) | generation time inside the signature; age window; duplicate rejection | ALG-08; **the receiver's clock** (HW-10 by assumption); IMP-L2.3-06 | R8 freshness for every provider (review 02 T-9) | MEASURED as part of #21 (same T-9 policy for all verifiers) and #45 (I2 replay checks 30/30) | `cv2x-testbed/identity/freshness.py` |
| IMP-L7.2-02 | JSON-signed BSM / SPaT (SSI: DID + secp256k1-SHA-256 signature; PKI: PEM cert + P-256) | the testbed's secured message | ALG-04 / ALG-05; IMP-L7.2-01 | V2V and RSU scenarios | MEASURED: #23 (596 B DID-carrying vs 1,078–1,110 B PEM-carrying), #27, #44–#48 | `protocols/cv2x_stack.py`; `sumo/infrastructure_layer.py` |
| IMP-L7.2-03 | **Verifier v3** (infrastructure layer) | field binding (intersection/station), per-receiver replay, expiry on warm path, size/depth limits, DID method/chain check | IMP-L7.2-01; D28–D31, D37–D42 fixes | SOL-15 | MEASURED (#44–#48) | `cv2x-testbed/sumo/infrastructure_layer.py` |
| PRO-12 | IEEE 1609.2 secured messages (`Ieee1609Dot2Data`, `SignedData`, implicit/explicit certificates, SCMS butterfly keys) | the deployed V2X security envelope | ALG-05; HW-03; SCMS PKI (T-I05) | the incumbent L6/L7 | DESIGN / referenced: "IEEE 1609.2-style" pseudonym certificates are X.509 P-256 in this repo, **not** 1609.2 encodings; "this repository has no IEEE 1609.2 security-profile text to quote" (`freshness.py`) | `pki_identity.py`; `sumo_identity_integration.py` l. 8, 209 |
| PRO-12a | ETSI TS 103 097 / TS 102 941 | European V2X security and trust | as PRO-12 | — | named only | `pki_identity.py` docstring |
| PRO-13x | SAE J2735 BSM, SPaT (UPER-encoded ASN.1) | message set | none intrinsic | safety apps | **J2735-like** dataclasses serialised as JSON; `MessageType` also lists CAM, DENM, CPM, MCM | `cv2x_stack.py` l. 18–100; `experiment_pki_vs_erc1056.py` l. 204 |
| PRO-13y | SAE J2945/1 (BSM rate 10 Hz, congestion control) | on-board requirements | — | the 100 ms interval of the identity budget | STANDARD source of the budget | `docs/LATENCY_BUDGET.md` §1 |
| PRO-13z | DIDComm v2 (O16) | DID-authenticated encrypted messaging, mediators | JOSE (T-I09), X25519/Ed25519 | I2I channel (R1–R8) | not used (no DIDComm code in the tree) | — |

#### L7.3 Application scenarios

| Tag | Component | What it does | Secured by | Enables above | Status | Repo |
|---|---|---|---|---|---|---|
| IMP-L7.3-01 | SUMO highway-intersection scenario (`highway_intersection.net.xml`, `routes.rou.xml`), TraCI coupling; `--simulate` mock mobility | V2V identity under mobility | IMP-L7.2-02 | V2V latency and saturation | MEASURED: #27 (in `--simulate` mode — "simulated mobility, real identity crypto"); SUMO-binary runs: #15 says configured, not run ("50 vehicles" is E) | `cv2x-testbed/sumo/` |
| IMP-L7.3-02 | RSU / TMC infrastructure scenario (SPaT from credentialed RSUs, controller → RSU → vehicle) | infrastructure trust | IMP-L7.2-03 | I1–I5 | MEASURED (#44–#48) | `sumo/infrastructure_layer.py`, `run_infra_stats.py` |
| IMP-L7.3-03 | MOBI VID lifecycle (17 events) and M4 parity | vehicle life on chain | SCF-MOBI1/2 | lifecycle cost | MEASURED (#30, #33, #35) | harness L2; `cv2x-testbed/results/lifecycle_parity.*` |
| IMP-L7.3-04 | M5 pseudonym pool (20 `addDelegate` per 5-min epoch) | rotating V2X pseudonyms as ERC-1056 delegates | SCF-EDR-05 | unlinkability (R5) | MEASURED (#38: 1,113,456 gas first epoch) | register #38 |
| IMP-L7.3-05 | Toll entry and payment | NFT entry record + payable toll | SCF-E721T-02/03 | tolling | used in tests | `CVIN_NFT_DID_ERC721.sol` |
| IMP-L7.3-06 | ZK admission to a service (full-circle demo) | prove model year / region / manufacturer without the VIN | SOL-11, SOL-14 | privacy-preserving services | MEASURED (#56–#62) | `5_zkp-agent-identity/demos/full_circle_demo.py` |
| IMP-L7.3-07 | ns-3 C-V2X network simulation | packet-level radio | — | L0 realism | DESIGN (compose service only) | `docker-compose.yml` |

---

## 3. Mapping: the repository's "nine standards" vs O1–O17 and Families A–F

The repository compares **nine standards** in ten harness columns (README l. 225; register #34): ERC-1056 (pure and wrapper), ERC-721, ERC-725, ERC-725xy, ERC-735, ERC-1155, ERC-4337, LSP8 and CVIN-Combined, with MOBI VID V2 as an application profile. The project's option list O1–O18 with Families A–F is taken here from Phase 1 R2 §3.3, which quotes the Terminology Freeze. **The Projects tool was not available in this session, so the Terminology Freeze itself was not re-read; the mapping is provisional to the extent R2 §3.3 is** (logged as Q-R7).

| Repo column (harness / SCF prefix) | Project option | Family | Match quality | Note |
|---|---|---|---|---|
| ERC-1056 pure (`EthereumDIDRegistry`, SCF-EDR) | **O1** ERC-1056 | A | exact | the canon's only 12/12 baseline (BASIC_ID_SET §1) |
| ERC-1056 wrapper (`CVINVehicleDIDRegistry`, SCF-CVDR) | O1 (application profile) | A | sub-option | K-5 / register §1.1 |
| ERC-1056 vehicle profile (`ERC1056Registry`, SCF-VPR) | O1 variant | A | sub-option, **not** byte-faithful | explicit creation and revocation; no `*Signed` |
| ERC-1155 (SCF-E1155) | **O2** | A | exact | — |
| ERC-721 (SCF-E721N; E721T, E721M auxiliary) | **O3** ERC-721 soulbound | B | close (transfers allowed in E721N; soulbound only in 1155) | — |
| — | O4 ERC-6551 TBA | B | **absent from repo** | — |
| ERC-725 basic (SCF-E725B) | **O5** | C | exact (with D23 stub) | — |
| ERC-725xy (SCF-E725XY) + ERC-735 (SCF-E735) | **O6** ERC-725xy + unmerged ERC-735 | C | split into two columns in the repo | — |
| ERC-4337 (SCF-E4337A/EP) | **O7** | C | minimal representative (no bundler/paymaster) | — |
| — | O8 EIP-7702 | C | **absent** | — |
| — (Steward delegated identity is the nearest) | O9 ERC-8004 | D | **absent as a contract**; conceptually adjacent to SOL-14 | — |
| LSP8 (SCF-LSP8) | **none** | — | repo-only | LUKSO standard; not in O1–O17 → candidate addition (Q-R8) |
| CVIN-Combined (SCF-CMB) | nearest O6 + O1 composite; a precursor of **O18** (Family F) | F (precursor) | repo-only | the thesis's own hybrid |
| MOBI VID I/II (SCF-MOBI1/2) | application profile over O1 | A + application | repo-only | MOBI standard, not an ERC |
| ZK-VIN (SCF-G16/ZKG/SCH) | touches **O15** Paladin's on-chain Groth16 verifier idea | E (adjacent) | repo-only | not Paladin; plain EVM |
| IdtxExecutor (SCF-IDTX) | none | — | repo-only | I-24; prior art ERC-3643 (STATUS §3 item 6) |
| — | O10 Indy, O11 Indy-Besu, O12 AnonCreds, O13 Identus, O14 CREDEBL, O16 DIDComm v2, O17 ACA-Py/Credo | E | **all absent from code** | Family E exists in the repo only as documents |

Reading: the repository *measures* Families A–C (and a Family-F precursor), *adds* four artefacts the option list does not contain (LSP8, CVIN-Combined, MOBI profile, ZK-VIN/IDTX), and *executes nothing* from Family D or E. Any thesis sentence that ranks Family E against A–C on measured data has no repository row to cite.

---

## 4. New breaking points at the deeper levels

Columns follow R3 Part II. "Closed by" cites a SOL, an IMP, a defect fix, or "open". Bounds are `PF-⟦n⟧` placeholders for R7 (variables listed in §8).

| Tag | Attack / failure | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-LH-01 | **Weak or predictable RNG on an embedded ECU/OBU** (boot-time entropy starvation, RDRAND-only trust, vendor DRBG flaw) | key or nonce generated before the pool is seeded; no RFC 6979 | `BP-L1-01`/`BP-L1-02` realised on the vehicle: private key recoverable → every SCF write and every BSM forgeable for that vehicle | RFC 6979 (ALG-02) for nonces; SE-internal keygen (HW-06); entropy health tests — all DESIGN | `PF-⟦1⟧` (effective κ vs boot entropy) |
| BP-LH-02 | **Test-key derivation leaks into a deployment**: controller key = SHA-256(vehicle_id) | IMP-LH.1-02 code path reused outside the testbed | anyone who knows a vehicle id rotates or revokes its identity (G1, G8 fail) | labelled INSECURE in source; open as deployment guard | `PF-⟦2⟧` (κ = entropy of vehicle-id space) |
| BP-LH-03 | **TEE/SE side channel or fault** (cache timing, Plundervolt-class, EM) | co-located or physical attacker | `BP-L1-07` against the Steward vault or wallet SE; `zkid` explicitly not constant time | constant-time libs (IMP-L1.2-02); keep `zkid` out of production — open | `PF-12` reuse (side-channel ≤ T_rot + PF-26) |
| BP-LH-04 | **GNSS spoofing / meaconing → time** | civil GNSS unauthenticated; receiver clock disciplined by GNSS | freshness window (IMP-L7.2-01) accepts replays shifted by the spoofed offset; `max_future_s` = 0.1 s is the only guard; PC5 mode-4 sync degraded | holdover oscillator + multi-source time; OSNMA — DESIGN | `PF-⟦3⟧` (accepted replay age = max_age + clock offset) |
| BP-LH-05 | **GNSS spoofing → position** | as above | BSM position fields are signed but *asserted*; an authentic vehicle broadcasts false position (misbehaviour, not forgery) | misbehaviour detection — out of scope | — (qualitative) |
| BP-LH-06 | **Host compromise of the RPC/resolver node** | Plane V or the testbed's RPC host owned | every read (PRO-13) is a lie the verifier cannot detect (no proofs) → `BP-L2-05` equivocation | light-client proofs (`eth_getProof` against a trusted header) — not used | `PF-⟦4⟧` |
| BP-L0.1-01 | **Sidelink congestion / jamming** | channel busy ratio high; SB-SPS collisions | BSMs lost → freshness rejects or staleness; Tier-1 deadline missed (`BP-L7-07`) | congestion control (J2945/1) — simulated only (`ResourcePool.update_cbr`) | `PF-⟦5⟧` (P_loss vs CBR) |
| BP-L0.2-01 | **Revocation over intermittent backhaul** (Uu outage, rural coverage) | verifier offline from Plane V for duration T_off | W grows by T_off; CRL/status cannot refresh; k-refresh probe (#37) cannot run | cache-with-bounded-staleness and fail-closed policy per tier — DESIGN | `PF-⟦6⟧` (W ≥ σ + T_off) |
| BP-L0.3-01 | **Eclipse via discv4** (table poisoning with Sybil node IDs; no admission cost) | public discovery enabled on a consortium node | node sees an attacker chain view; on a BFT chain it cannot finalise but can be fed stale state → `BP-L0-01` at implementation level | static-nodes + node permissioning (IMP-L0.3-01) — DESIGN | `PF-⟦7⟧` (eclipse cost vs table size) |
| BP-L0.4-01 | **JSON-RPC exposure** (unauthenticated `eth_sendRawTransaction`, `debug_*`, `admin_*`, personal namespaces on 0.0.0.0) | RPC bound publicly (the compose file maps `8545:8545`) | DoS, state inspection, on misconfigured nodes unlocked-account abuse | bind to loopback, auth proxy, method allowlist — open (testbed) | — |
| BP-L0.4-02 | **Unproven RPC responses** (resolver trusts the endpoint) | any verifier using PRO-13 for did:ethr | a malicious or stale endpoint returns a rotated-out key or hides `DIDRevoked`; did:ethr resolution "fails closed" only on *errors*, not on *lies* | proof-carrying reads or multiple independent endpoints — open | `PF-⟦4⟧` |
| BP-L0.4-03 | **Chain-id confusion at the client** | verifier trusts the endpoint's `eth_chainId` (called twice per verify, #21) | a DID for chain A resolved against chain B's identical-address registry (compounds D52) | verifier v3 checks DID method and chain against the authority network (D41 fix) — closed for the infra path | — |
| BP-L1.1-01 | **Signature-scheme inconsistency across contracts** (raw digest vs EIP-191 vs OZ ECDSA) | an issuer signs once for two contracts | the same signature valid or invalid depending on target (D25c); raw-digest schemes accept a signature over any 32-byte value the signer ever signed raw | one scheme (recommendation EIP-191/EIP-712) — author decision | — |
| BP-L1.1-02 | **Missing low-s check on raw `ecrecover`** (SCF-EDR, SCF-CMB, SCF-E4337A) | caller supplies (r, n−s) | second valid signature for the same message; replay keyed on signature bytes would miss it (the freshness module keys on content for exactly this reason) | content-keyed replay / nonces — EDR uses a nonce (safe); CMB keys revocations by content digest (safe); open as hygiene (D22 rest) | — |
| BP-L1.2-01 | **Library monoculture or divergence in secp256k1** (six implementations) | a bug in one implementation (historic: OpenSSL DER parsing, malleability) | verifier and contract disagree on validity → consensus or acceptance split | cross-implementation differential tests — partly (the security suite runs EVM vs ethers) | — |
| BP-L1.2-02 | **Precompile / curve bug in a client** (bn256 pairing, `ecrecover` edge cases such as r = 0) | client implementation defect (L3.2) | false Groth16 acceptance (SOL-11) or D53-class zero-address recovery | client diversity; contract guards (`recovered != 0`) — partial (only OZ path and 4337 account reject zero) | `PF-⟦8⟧` (P(precompile defect) × monoculture) |
| BP-L1.2-03 | **Circom under-constraint** (a signal assigned with `<--` and not constrained; a comparator without range checks) | circuit author error | prover satisfies the R1CS with a false statement → `ZkVinGate.admit` accepts | the circuit range-checks year inputs to 12 bits before `GreaterEqThan`, booleanity of path indices, 6-bit VIN characters (read in source); five false statements rejected (`prove_and_verify.js`, Z-E1..E4 PASS, #57) — **no formal under-constraint audit** | `PF-⟦9⟧` |
| BP-L1.2-04 | **Insecure Groth16 setup in use** (single-party, fixed entropy "INSECURE") | the committed zkey reused beyond research | whoever holds the toxic waste forges any ZK-VIN proof (`BP-L1-06` realised) | multi-party ceremony (Plan 1 to-do 11) — open | `PF-11` (p_s^t_s with t_s = 1 today) |
| BP-L1.2-05 | **Challenge bound by a trivial constraint** (`challengeSquared <== challenge*challenge`) and static per-service challenge | ZkVinGate `setService` stores one challenge per service | proofs are replayable across sessions *within* a service until the nullifier is spent; nullifier makes admission one-shot per scope, so the effect is bounded to first use | nullifier per scope (SCF-ZKG-03) — partially closed | — |
| BP-L2.1-01 | **Event-only state cannot be read on chain** (ERC-1056 attributes) | a contract needs an attribute's value | IDTX must add a commitment store (SOL-10 rationale, register #49); any on-chain check of an ERC-1056 attribute is impossible | IdentityCommitments (SCF-IDC) — closed by design | — |
| BP-L2.1-02 | **Linked-list severance** (`changed`/`previousChange` broken) | `revokeIdentity` (D21) or claim ops (D22) | resolver misses history → stale or wrong document (I3) | D21/D22 documented; adapter range-scans — partial | — |
| BP-L2.2-01 | **Storage corruption / pruning** of logs on a node | disk fault, pruned receipts, snap-sync without receipts | did:ethr resolution (log replay) impossible from that node even though state is intact | archive or receipt-retaining nodes for Plane V — DESIGN | `PF-⟦10⟧` |
| BP-L2.3-01 | **Off-chain body loss** (lifecycle `dataHash` with body discarded; URIs without pinning) | no Plane-D owner | anchor verifies, nothing to verify against (`BP-L0-05` realised in code: `lifecycle_backends.py` l. 191–195) | Plane D — DESIGN | `PF-05` |
| BP-L2.3-02 | **Replay-cache eviction** | cache full of live entries (> 65,536 in 1.1 s) | an evicted message replays inside the window (`evicted_live` counter) | sizing rule in module docstring — partial | `PF-⟦11⟧` (rate × window vs cache size) |
| BP-L3.2-01 | **Client monoculture** (one EL client, e.g. Besu-only consortium; or Hardhat-only evidence) | every validator runs the same client version | a single client bug halts or forks the whole Plane A (correlated failure; BFT's independence assumption in `PF-16` void) | ≥ 2 clients — DESIGN; for the *evidence*, M2 on a second client (Sepolia) — open (D-10) | `PF-⟦12⟧` (p_c with correlation ρ_c) |
| BP-L3.2-02 | **Dev-chain semantics differ from production** (automine, `allowUnlimitedContractSize`, zero base fee, single-process time) | results taken from IMP-L3.2-02 | latencies and finality are not transferable (register M1 rule); oversized bytecode may not deploy; time-dependent logic (validTo, deadlines) never sees real block-time jitter | M2 witness (D-10) and Besu deployment — open | `PF-⟦13⟧` |
| BP-L4.2-01 | **Besu permissioning-contract compromise** | admin key of the on-chain node/account allowlist stolen | attacker admits its own nodes and accounts, or ejects honest validators → `BP-L4-06` in one key | multi-sig/timelocked admin — DESIGN | `PF-⟦14⟧` |
| BP-L4.2-02 | **Single-key contract governance** (`registryAuthority`, `governor`, `contractOwner`, `DEFAULT_ADMIN_ROLE`) | that key lost or stolen | issuer list rewritten (MOBI), service policy rewritten (ZkVinGate), manufacturer list rewritten (CVDR); `transferRegistryAuthority` silent (D16) | multi-sig / timelock — open | `PF-⟦14⟧` |
| BP-L5.2-01 | **Cross-chain signature replay** of ERC-1056 `*Signed` ops (D52) | same registry address and signer nonce on two chains (deterministic deployment) | an owner change signed for the sandbox replays elsewhere (`BP-L5-02` realised) | documented (G3 narrowed); fix departs from upstream bytecode — author decision | `PF-⟦15⟧` (P(address and nonce collide across deployments)) |
| BP-L5.2-02 | **Zero-identity seizure** via `ecrecover` returning 0 (D53) | identity `0x0`; v = 27, r = s = 0 | `owners[0x0]` seized; impact limited to DID 0x0 | open (L) | — |
| BP-L5.2-03 | **Replay inside freshness window** (D29) and **field-binding fail-open** (D28, D38) at L7 | same message to same/other receivers; credential lacking `intersectionId` | forged-context SPaT accepted | verifier v3 per-receiver replay cache and binding (SOL-15) — closed; residual: fresh relay by design | `PF-⟦3⟧` |
| BP-L5.2-04 | **Guardian super-owner** (D15) | guardian key compromised at any time | instant, unconditional takeover via `recoverOwner` (no delay, no threshold) → `BP-L6-10` | time-lock and threshold — open (`PF-30` says any threshold is weaker than the key) | `PF-30` |
| BP-L5.2-05 | **Unrestricted DELEGATECALL** in ERC-725X (D24) | owner (or a compromised owner key) delegatecalls a malicious target | slot 0 `_owner` overwritten → identity bricked or hijacked | documented spec hazard | — |
| BP-L5.2-06 | **Reentrancy surfaces**: value `call` in `payToll`, `_checkOnERC721Received` in the monolithic 721, arbitrary `execute` in 725X/4337 | malicious receiver/target | state updated after external call could be re-entered; v0-2 to audit ordering per function | Checks-effects-interactions — **not audited in this pass** | — |
| BP-L6.1-01 | **Unsalted VIN-derived identity address** (D64) and unsalted `keccak(VIN)` token ids (1155, LSP8) | VIN enumerable per make/plant/year | G7 fails: the salted `vinHash` and AES-GCM ciphertext beside it do not hide the VIN; #60 shows a serial-unknown VIN hash reversed in 3.58 s | ZK-VIN commitments with salt (SOL-11) — closed for the ZK path only | `PF-⟦16⟧` (VIN entropy vs hash rate; input #60) |
| BP-L6.2-01 | **Non-standard cryptosuite and canonicalisation** | third-party verifier expects URDNA2015 / a registered cryptosuite | interop failure; a canonicalisation mismatch can make two parties sign/verify different bytes | documented deviation — open | — |
| BP-L7.2-01 | **V2X pseudonym linkability through the registry** (M5 pool: pseudonyms are delegates of one DID) | an observer reads `DIDDelegateChanged` events | every pseudonym is publicly linked to the vehicle DID on chain (R5 fails *by construction*) unless the delegate set itself is unlinkable | pseudonym certificates off chain (1609.2 butterfly keys) or ZK membership — open | `PF-⟦17⟧` (anonymity set = 1 on chain) |
| BP-L7.2-02 | **Wall-clock dependence in validity checks** (D40, D51, D63) | verifier clock differs from chain time | revoked delegate key accepted (D51 pre-fix), or valid key rejected; probe path still judges expiry by last-learned chain time (D63) | chain-time decision on full resolution (D51 fixed); D63 open | `PF-⟦18⟧` (skew bound vs `CLOCK_SKEW_S` = 900 s) |
| BP-L7.3-01 | **Steward / oracle trust** (the agent computes proofs and holds the vault; lifecycle issuers assert odometer) | the agent's host or the issuer lies | proofs about false attributes (the commitment binds what the issuer committed, not the truth); odometer rollback recorded as authentic | issuer-signed commitments; misbehaviour audit — partial (Steward audit log) | `PF-⟦19⟧` |

---

## 5. New solutions found in the repository (SOL-10 onward)

| Tag | Solution | Layers | Addresses (BP) | Status | Repo |
|---|---|---|---|---|---|
| **SOL-10** | **IdtxExecutor + IdentityCommitments** — identity-dependent transactions with Owner/Delegate/Commitment predicates; same-tx and intent/fulfil continuations; predicate independent of caller; commitment voids when its setter stops owning the identity | L5.2, L6.3 | BP-L2.1-01; `BP-L6-06` (confused deputy: predicate names the identity, not the caller); TOCTOU between intent and action | DESIGN-with-code (compiled prototype; no result by its own rule); mechanism found to be prior art (I-24 brief) | `phase2/idtx/contracts/IdtxExecutor.sol` |
| **SOL-11** | **ZK-VIN** — Poseidon commitment to (VIN, year, region, salt), WMI Merkle membership, year threshold, per-scope nullifier; Groth16 on BN254; `ZkVinGate.admit` | L1.1, L1.2, L5.1, L5.2, L6.2, L6.3 | BP-L6.1-01; `BP-L6-05` (linkability across scopes); `BP-L6-08` (createPresentation gap X2) for the predicates it covers | MEASURED (#56–#58); setup INSECURE (BP-L1.2-04) | `5_zkp-agent-identity/circuits`, `contracts` |
| **SOL-12** | **Schnorr-via-ecrecover verifier and the `zkid` sigma library** — cheaper proofs of knowledge on chain; readable counted arithmetic | L1.1, L5.1 | cost alternative to SOL-11 for simple statements | MEASURED (#58 28,775 gas; #59) | `SchnorrEcrecoverVerifier.sol`; `zkid/` |
| **SOL-13** | **MOBI VID registries (I and II)** — manufacturer-gated birth, anchored vehicle key, ownership history with odometer, role-gated lifecycle events, owner-consented chain-bound attestations | L5.2, L6.1, L6.2 | `BP-L6-03`/`BP-L6-07` partially (anchored keys, single registry); D11/D11b (key binding); D54 (attestation consent) | MEASURED (#28, #30, #33, #35) | `1_blockchain-identity/contracts/MOBI/` (≡ `cv2x-testbed/contracts/`) |
| **SOL-14** | **Steward agent** — vault without value getters, signed owner policy, leakage audit against a bit budget, learned responder, delegated identity | L7.1 (with L1.1 sigma) | twenty-questions predicate narrowing (#61); `BP-L7-01` partially (secrets never leave the vault object) | MEASURED in Sim (#61, #62) | `5_zkp-agent-identity/steward/` |
| **SOL-15** | **Freshness module + verifier v3** — signed generation time, bounded replay cache keyed on content, field binding, warm-path expiry, size/depth limits, DID chain check | L7.2 (with L2.3 cache) | `BP-L7-04`; BP-L5.2-03; D28–D31, D37–D42 | MEASURED (#21, #44–#48) | `cv2x-testbed/identity/freshness.py`; `sumo/infrastructure_layer.py` |
| **SOL-16** | **Freshness-k cached verification with one-call probe** — re-check identity every k-th message via one `getIdentityInfo` call, full resolution only on change | L6.1, L7.2, L0.4 | `BP-L7-03` (stale cache) traded against `BP-L7-07` (tier budget); turns W into a k-parameter (`PF-15`) | MEASURED (#32, #37, #52, #55; #46 I3 "at most k − 1 further SPaT") | `cv2x-testbed/identity/erc1056_provider.py` |
| **SOL-17** | **On-chain did:ethr resolution, fail-closed** — log-replay resolver with explicit resolution-mode metadata | L6.1, L0.4 | `BP-L2-05` partially (never synthesises a document when on-chain mode fails); not BP-L0.4-02 (cannot detect a lying endpoint) | MEASURED (#24, #31, #51) | `2_w3c-ssi-layer/did-resolution/did_resolver.py` |

SOL-01 (R2) is described in Phase 1 as "Hardhat + Foundry harness with a single-validator Besu QBFT node". **The repository on this branch contains neither Foundry nor any Besu node configuration** (searched: no Besu/QBFT string in any `.py`, `.js`, `.yml` or `.json` outside `node_modules`; the only Besu text is `V2_DESIGN.md` l. 391). That description refers to the separate `cvin-sandbox-v1.x` lineage, not to this tree (KD-R4).

---

## 6. Secured-by chains: worked vertical traces

Each trace starts at a concrete function and descends. "⇐" reads "is secured by". The status of the weakest link is given at the end of each trace.

**Trace 1 — key rotation on ERC-1056 (`SCF-EDR-03 changeOwner`).**
`changeOwner(identity, newOwner)` writes `owners[identity]` ⇐ `onlyOwner`: `msg.sender == identityOwner(identity)` (SCF-EDR-01, mapping IMP-L2.1-03) ⇐ `msg.sender` is the address recovered from the outer transaction signature (PRO-21, EIP-155 chain id in v) ⇐ client-side ECDSA secp256k1 over keccak(RLP(tx)) (ALG-02, ALG-07) with RFC 6979 nonce ⇐ private key held by the wallet (IMP-L7.1-02 eth-account in the testbed; HW-06 SE in deployment) ⇐ generated from the OS CSPRNG (IMP-LH.1-01) ⇐ RDRAND/TRNG (HW-02). Ordering: the rotation is final when the block is (ALG-19 automine in M1: instantly, trivially; ALG-20 QBFT in SOL-02: `PF-25`). *Weakest link in this programme:* the testbed's vehicle key is SHA-256(vehicle_id) (BP-LH-02). *Measured:* gas #2 (68,854 wrapper context). *Design:* everything below the CSPRNG.

**Trace 2 — the relayed variant (`SCF-EDR-04 changeOwnerSigned`).**
As Trace 1, but the authority is the inner signature: `ecrecover(keccak(0x19 0x00 ‖ registry ‖ nonce[owner] ‖ identity ‖ "changeOwner" ‖ newOwner), v, r, s)` (PRO-16, ALG-03) ⇐ the EVM's `ecrecover` implementation (IMP-L1.2-05 EthereumJS; IMP-L1.2-06 BouncyCastle in Besu) ⇐ secp256k1 ECDLP (T-06). The relayer's outer tx authenticates only the relayer. *Gap:* the digest binds the registry address and nonce, **not the chain id** (D52 → BP-L5.2-01), and `identityOwner(0) = 0` lets r = s = 0 seize DID 0x0 (D53). *Measured:* #50 (U5 62,646 gas).

**Trace 3 — a V2V SSI BSM (`IMP-L7.2-02` via `erc1056_provider.sign_message` and `verify_message`).**
Receiver accepts ⇐ freshness window and replay cache (IMP-L7.2-01, IMP-L2.3-06) ⇐ receiver's clock (HW-10 GNSS by assumption; host clock in the testbed) ⇐ signature over `signed_bytes(message, generation_time)` verifies under the sender's key (ALG-04: ECDSA secp256k1 with SHA-256 via IMP-L1.2-01) ⇐ the key is the sender's current `did/pub/secp256k1/veriKey` attribute (SCF-VPR-05/08), resolved by `eth_getLogs` replay (ALG-23, PRO-13) or held in cache for k messages (SOL-16) ⇐ the attribute's `validTo` judged in chain time (IMP-L5.1-03, D51 fix) ⇐ the registration tx was signed by the vehicle's controller key (Trace 1). *Weakest links:* GNSS time (BP-LH-04), unproven RPC (BP-L0.4-02). *Measured:* #21 (15.513 ms uncached verify), #37 (3.222 ms probe), #27 (0.142 ms warm). Note that this path is **not** an EIP-191/keccak signature and is not checked on chain; it shares only the curve with Trace 1.

**Trace 4 — a PKI baseline BSM ("IEEE 1609.2-style").**
Receiver accepts ⇐ freshness (as Trace 3) ⇐ ECDSA P-256 / SHA-256 signature (ALG-05, IMP-L1.2-01) ⇐ the pseudonym certificate chains to the CA (X.509, T-I02) and is not on the CRL set ⇐ the CA's P-256 key (generated in software here; HW-03 HSM in deployment) ⇐ CSPRNG. In a deployed system the envelope would be 1609.2 `SignedData` with SCMS butterfly-key certificates and the HSM in the OBU (PRO-12, HW-03, HW-08) — **DESIGN** in this repo, where the certificate is PEM X.509 carried in JSON. *Measured:* #21 (0.226 ms verify), #23 (1,078–1,110 B).

**Trace 5 — ZK-VIN admission (`SCF-ZKG-03 admit`).**
`Admitted` emitted ⇐ `nullifierUsed[scope][nf]` was false (mapping) and public signals equal the anchored commitment, `mfrRoot` and service fields (SCF-ZKG-01/02) ⇐ `Groth16Verifier.verifyProof` returned true (SCF-G16-01) ⇐ `ecMul`/`ecAdd` for the public-input linear combination and one `ecPairing` (PRO-18, 0x06–0x08) ⇐ BN254 pairing security ≈ 100 bits (ALG-10, `PF-10`) **and** the verification key came from a setup whose toxic waste was destroyed — here a single-party, fixed-entropy ceremony (BP-L1.2-04, `PF-11` with t_s = 1) ⇐ the R1CS encodes the statement soundly (IMP-L1.2-07 circom 2.2.2 + circomlib; BP-L1.2-03) ⇐ Poseidon collision resistance (ALG-09) ⇐ the commitment was anchored by the identity's ERC-1056 owner (Trace 1). *Measured:* #56–#58. *Weakest link:* the setup.

**Trace 6 — owner-consented lifecycle attestation (`SCF-MOBI2-04 attestEvent`).**
Attestation stored ⇐ `ECDSA.recover(toEthSignedMessageHash(keccak(this ‖ chainid ‖ vehicle ‖ eventId)), sig) == msg.sender` (IMP-L1.2-11: low-s, non-zero, chain-bound — the only fully hardened recovery in the repo) ⇐ `msg.sender` holds an issuer role (SCF-MOBI2-01, single `registryAuthority` key: BP-L4.2-02) **and** is the vehicle's owner or valid `veriKey` delegate (SCF-VPR-01, `validDelegate` in chain time) ⇐ outer tx signature (Trace 1). *Measured:* #28 (198,694 execution gas).

**Trace 7 — a next-transaction IDTx (`SCF-IDTX-03/04 createIntent → fulfil`).**
`Executed` at fulfilment ⇐ `holds(dep)` re-evaluated now: e.g. Commitment kind ⇐ `IdentityCommitments.valueOf` non-zero (chain time vs `validUntil`; `setBy == identityOwner`) ⇐ SCF-EDR-01 ⇐ the owner's rotation history (Trace 1) ⇐ ordering of the intent, any intervening rotation, and the fulfilment in one history (L3.1). *Gap:* keeper liveness and chain time are external; with automine every tx is its own block, so the intent-to-fulfil race the design defends against is never exercised (BP-L3.2-02). *Status:* DESIGN-with-code.

**Trace 8 — an on-chain Schnorr PoK (`SCF-SCH-02 prove`).**
`Proved` ⇐ `e == keccak(ecrecover(h, parity+27, px, σ) ‖ parity ‖ px ‖ message)` (ALG-15) ⇐ `ecrecover` computing r⁻¹(σ·P − h·G) (PRO-16) ⇐ ECDLP and keccak as a random oracle (T-06, T-07, T-I10). *Gap:* no replay guard — anyone can resubmit the same proof (it proves knowledge once, not freshness). *Measured:* #58.

**Trace 9 — a VC presentation verified offline (`IMP-L6.2-01/02`).**
Verifier accepts ⇐ EIP-191 recovery over deterministic JSON (ALG-03, PRO-22b; not URDNA2015 — BP-L6.2-01) yields the issuer's address ⇐ that address is (or is a delegate of) the issuer DID (ALG-23 on-chain or ALG-23a synthesised — the latter binds nothing beyond "key = address") ⇐ disclosed claims hash to the signed salted digests (ALG-08) ⇐ `credentialStatus` not revoked in the `RevocationRegistry` (IMP-L2.3-01: in-memory or JSON file, **no anchoring**) ⇐ issuer key from CSPRNG. *Weakest link:* the status registry's host. *Measured:* #4, #27.

---

## 7. What is measured vs designed (one row per sub-layer)

| Sub-layer | MEASURED in this programme (rows / files) | DESIGN only | Not used | Honest one-line summary |
|---|---|---|---|---|
| LH.1 | environment headers (#27, #57) | entropy quality | — | keys come from a cloud host's OS CSPRNG, or from SHA-256(vehicle_id) in the testbed |
| LH.2 | — | HSM, SE (docstrings, threat model) | TPM, TEE | no key in this programme has lived in hardware |
| LH.3 | — | OBU as Python object | CAN, Ethernet, gateway | the vehicle is simulated |
| LH.4 | — | GNSS time assumption (freshness docstring) | real modems | radio is a free-space model; time is the host clock |
| LH.5 | same-host replicates (#52, #55) | validator hosts | — | one host per run |
| L0.1 | — (simulated `ResourcePool`, not a register row) | PC5 mode 4 model | 802.11p, NR-V2X | no PHY/MAC result |
| L0.2 | loopback HTTP cost (M1-H/HTTP, #39) | Uu backhaul | WSMP, QUIC | localhost only |
| L0.3 | — | static nodes, permissioning | devp2p, discv4/5, libp2p | no P2P network ever ran |
| L0.4 | RPC counts and bytes (#21, #31, #37, #51) | TLS to providers (Sepolia procedure) | WS, Engine API | reads are unproven |
| L1.1 | ECDSA/P-256 verify (#21, #27); Groth16 (#56–#58); sigma (#59); hash brute force (#60) | — | Ed25519, BLS12-381, CL/BBS+ | the best-measured layer after gas |
| L1.2 | library versions recorded per result | BouncyCastle (Besu) | anoncreds-rs | six secp256k1 implementations in use |
| L2.1 | SSTORE and log-byte counts (#30, #49) | Bonsai | proofs (`eth_getProof`) | state is counted, never proved |
| L2.2 | — (in-memory) | RocksDB | — | nothing persists beyond a run |
| L2.3 | replay cache behaviour (#45) | status list, CAS | accumulators | revocation lists are a Python dict or file |
| L3.1 | automine as the condition of every M1 row | QBFT, Gasper | IBFT 2.0, Clique | no consensus protocol has been measured |
| L3.2 | Hardhat 2.28.6 | Besu, Quorum | Geth, Anvil (Ganache configured only) | single-client evidence |
| L4.1 | gas, exhaustively (#1–#3, #22, #25, #29–#35, #47–#50, #54, #58) | free-gas, EIP-1559 pricing | blobs | gas is exact; price is ESTIMATED (#20) |
| L4.2 | role-gated attack cells (#28, #45) | node/account permissioning, validator governance | — | governance is single EOA keys |
| L4.3 | ops-per-block not measured; `block_gas_limit` recorded | `PF-24` capacity | — | capacity is derived, not measured |
| L5.1 | precompile gas in aggregate (#58) | — | sha256, modexp, BLS precompiles | ecrecover and bn256 are the load-bearing precompiles |
| L5.2 | per-function gas and attack cells for 10 columns (#25, #28, #29–#36, #49–#54) | IdtxExecutor numbers (by its own rule) | — | the thesis's core artefact; 117 SCF rows |
| L5.3 | legacy/EIP-155 tx; 4337 UserOps (#25, #50); `*Signed` meta-tx (#50) | — | 2930, 4844, 7702 | — |
| L6.1 | did:ethr on-chain resolution (#24, #31, #51) | — | did:indy | did:ethr is real; did:mobi is real; the rest are synthesised |
| L6.2 | VC v2.0 Data Integrity (thesis cryptosuite) (#4, #27) | — | AnonCreds, BBS+, mDL | selective disclosure is SD-JWT-style digests |
| L6.3 | Set A/B coverage (#53, #54); ZK admission (#58); attestations (#28) | IdtxExecutor | — | IDTX exists as code without a result |
| L7.1 | providers' timings (#21, #32, #33, #37); Steward Sim (#61) | — | ACA-Py, Veramo | Python providers, not agents |
| L7.2 | freshness and verifier v3 (#44–#48); message size (#23) | 1609.2 encodings | DIDComm | JSON-signed messages |
| L7.3 | V2V in `--simulate` (#27); RSU/TMC (#44–#48); lifecycle (#30, #33); pseudonym pool (#38) | SUMO-binary runs (#15 E), ns-3 | — | mobility is mocked in the runs of record |

---

## 8. HANDOFF (R6 v0-1 → R7, R8, R9 and R6 v0-2)

**Files.** `docs/roots/phase2/60_R6_full_stack_atlas/claude_CVIN_SC_Roots_FullStack_Atlas_R6_v0-1.md` (this file). Nothing else written.

**Tag ranges assigned (exact).** `HW-01..HW-12` · `PRO-01..PRO-22` (with letter suffixes 11a–c, 13a–b, 13x–z, 21a–d, 22a–b) · `ALG-01..ALG-24` (with 19a, 20a–c, 23a, 24a) · `IMP-LH.1-01..03`, `IMP-LH.5-01`, `IMP-L0.3-01`, `IMP-L0.4-01..02`, `IMP-L1.2-01..11`, `IMP-L2.1-01..04`, `IMP-L2.2-01..04`, `IMP-L2.3-01..06`, `IMP-L3.2-01..06`, `IMP-L4.1-01`, `IMP-L4.2-01..03`, `IMP-L4.3-01..02`, `IMP-L5.1-01..03`, `IMP-L6.1-01..02`, `IMP-L6.2-01..07`, `IMP-L6.3-01..04`, `IMP-L7.1-01..06`, `IMP-L7.2-01..03`, `IMP-L7.3-01..07` · SCF prefixes `EDR, CVDR, VPR, MOBI1, MOBI2, CMB, E735, E725B, E725XY, EXT, E1155, E721N, E721T, E721M, LSP8, E4337A, E4337EP, IDC, IDTX, G16, ZKG, SCH` · `BP-LH-01..06`; `BP-L0.1-01`, `BP-L0.2-01`, `BP-L0.3-01`, `BP-L0.4-01..03`, `BP-L1.1-01..02`, `BP-L1.2-01..05`, `BP-L2.1-01..02`, `BP-L2.2-01`, `BP-L2.3-01..02`, `BP-L3.2-01..02`, `BP-L4.2-01..02`, `BP-L5.2-01..06`, `BP-L6.1-01`, `BP-L6.2-01`, `BP-L7.2-01..02`, `BP-L7.3-01` · `SOL-10..SOL-17`. (ALG-17 = AES-GCM is listed under L1.1; ALG-25/26 reserved, unused.)

**Five load-bearing decisions.** (1) Executed chain = Hardhat; every Besu/QBFT/Sepolia row is DESIGN. (2) The two ERC-1056 contracts get separate prefixes (EDR, VPR) and are never pooled. (3) Testbed contract copies are treated as one source (byte-identical), two builds. (4) The O-mapping (§3) is provisional on R2 §3.3, not the Freeze itself. (5) LH and L0.1 are DESIGN layers kept in the atlas only to make conditional security claims explicit.

**PF placeholders for R7.** ⟦1⟧ κ_eff vs boot entropy · ⟦2⟧ κ = log₂|vehicle-id space| · ⟦3⟧ accepted replay age = max_age_s + δ_clock · ⟦4⟧ P(undetected false read) vs number of independent endpoints r_e · ⟦5⟧ P_loss(CBR) · ⟦6⟧ W ≥ σ + T_off · ⟦7⟧ eclipse cost vs table size, Sybil IDs · ⟦8⟧ p_bug × client share · ⟦9⟧ soundness error of circuit (audit coverage) · ⟦10⟧ log availability vs pruning policy · ⟦11⟧ P(evict live) = f(rate, window, cache size) · ⟦12⟧ p_c with correlation ρ_c · ⟦13⟧ dev-to-prod latency transfer factor · ⟦14⟧ governance-key compromise vs m-of-n · ⟦15⟧ P(cross-chain address+nonce match) · ⟦16⟧ VIN entropy vs hash rate (#60) · ⟦17⟧ on-chain anonymity set of a pseudonym pool · ⟦18⟧ skew bound vs CLOCK_SKEW_S · ⟦19⟧ oracle/issuer misreport detection · ⟦20⟧–⟦24⟧ reserved.

**Open questions.** Q-R7 Terminology Freeze O1–O17 re-read (Projects tool unavailable). Q-R8 add LSP8, CVIN-Combined, MOBI profile, ZK-VIN as options? Q-R9 is SOL-01 this repo or the sandbox lineage? Q-R10 is the M5 on-chain pseudonym pool meant to be unlinkable? Q-R11 D52 fix vs upstream fidelity. Q-R12 reentrancy audit scope for v0-2.

**Corrections.** KD-R4 R2's SOL-01 ("single-validator Besu QBFT, Foundry") does not describe this tree. KD-R5 Phase 1 `PF-25/PF-28`'s Δ = 2 s has no executed source here. KD-R6 the repo's "1609.2" is X.509 P-256 in JSON. KD-R7 SSI BSMs are secp256k1-SHA-256, not EIP-191. KD-R8 HAA-1 Plane A has no code.
