# CVIN-SC · Roots Thread G-R1 · Phase 2 — R6 The Full-Stack Atlas (forward, bottom-up)

| Field | Value |
|---|---|
| Document | **R6** — Full-Stack Atlas |
| Version | **v0-3** (consistency sweep per R9 v0-2 PN-35, PN-36, PN-38, PN-39; v0-1 and v0-2 kept unchanged beside it) — **re-keyed per R9 §3.1** |
| Date | 2026-10-24 |
| Branch / tree read | `roots/G-R1-phase2`, working tree as found on 2026-10-23 (no commit made) |
| Consumes | Phase 1: R1 v1-1 (`T-01..T-24`, `T-I01..T-I22`, L0–L7), R2 v0-1 (`SOL-01..09`, O1–O18), R3 v0-1 (`BP-L0-01..BP-L7-07`, requirements R1–R8 and I1–I9), R4 v0-1 (`SYM-01..24`, `PF-01..31`), R5 v0-1. Phase 2: R6 v0-1; R7 v0-1/v0-2 (`PF-32..66`, `Q-R7-01..08`); R8 v0-1 (`RV-`, `MD-`, `PAR-`); **R9 v0-1** (`PN-01..33`, `SLD-`, `NC-`, `CA-`, `PRM-`, §3 re-keying and placeholder tables, §7.1 work order). Repo ground truth in §0.2 |
| Assigns | sub-layers LH, L0.1–L7.3 (as defined in the brief §3); `HW-01..12`; `PRO-01..25` (PRO-23..25 new in v0-2); `ALG-01..24`; `IMP-<sublayer>-nn` (ranges in §9); `SCF-<prefix>-nn` (22 prefixes, 117 rows); `BP-LH-01..06` and 36 `BP-Lx.y-nn` (three new in v0-2: BP-L0.1-02, BP-L7.2-03, BP-L7.2-04); `SOL-10..17` (four of them re-labelled "mechanism", §5); `Q-R6-01..07`; `KD-R6-01, -03, -04`; cites `PF-63..66` as supplied by R7 v0-2 |
| Status scale (suite-wide, R9 PN-32) | **M** MEASURED (register row `#n` or result file) · **Dv** DERIVED · **I** IMPLEMENTED-UNMEASURED (code exists and runs; no register row) · **Ds** DESIGN (specified, not built) · **E** ESTIMATED · **S** STANDARD (cited spec or theorem) · **—** not used |
| Phase 1 erratum pointer | R9 §3.4 X-1..X-9: R4 PF-24/25/28 Δ = 2 s rows → DESIGN; R2 SOL-01 lineage note (KD-R6-01); "IEEE 1609.2 baseline" renamed (KD-R6-03) |

`Progress ▓▓▓▓▓▓▓▓▓▓ 95 %` — v0-3 consistency sweep complete: every stale cross-reference named in R9 v0-2 PN-35/36/38/39 corrected; no number changed. Remaining 5 %: the author's decisions (Q-R6-04 pseudonymity scope) and the §5 PRM tick-off in R9 v0-2.

**How to read.** The forward document: silicon to application, one layer per section. Each layer opens with an **elevator** box (what it does for the level above, what it trusts below, the one thing to remember), then a short narrative, the registers, and ↑/↓ links to adjacent layers, R7 bounds (PF-) and R8 reverse rows (RV-). §6 traces descend from a function and climb back to the R3 requirement served; §7 is the honesty summary (R9 SLD-12). The governing honesty rule: the executed chain is **Hardhat** — in-process (`chainId 31337`, `allowUnlimitedContractSize: true`, `1_blockchain-identity/hardhat.config.js`) or a Hardhat node (`chainId 1337`, automine plus a 1,000 ms interval, `cv2x-testbed/hardhat.config.js`). The run of record's `meta.json` (`1_blockchain-identity/results/metrics/latest/meta.json`, run `2026-10-23T00-49-12Z_1f4ace0`) records automine, chain 31337 and a 60,000,000 block gas limit. Besu, QBFT, Sepolia execution and HAA-1 public anchoring are **Ds** throughout.

---

## Change log v0-2 → v0-3 (consistency sweep; R9 v0-2 §2)

No number of R6's own changed. Every edit below aligns a cross-reference with R7 v0-2, R8 or the repository.

| # | Change | Where | PN |
|---|---|---|---|
| V3-01 | "PF-44c" → **PF-45** with R7 §4.4 values 0.136 / 0.449 / 0.805 (L0.4 links, BP-L0.1-02, §7 L0.1, §8 new-BP row, C-12, HANDOFF) | §2, §4, §7, §8, §9, §10 | PN-35 |
| V3-02 | "PF-46 reserved" → **PF-46** (R7 §4.5 loss bracket) | BP-L0.1-01, §8 PF-⟦5⟧ row and note | PN-35 |
| V3-03 | "PF-63/64/65/66 requested" → **PF-63/64/65/66** with the R7 §7.1 values; §8 states "resolved"; the request paragraph is re-titled "supplied" | header, §4, §8, C-05, HANDOFF | PN-35 |
| V3-04 | R7 range `PF-32..62` → `PF-32..66` | header "Consumes", §0.3 tag rule | PN-35 |
| V3-05 | PF-52 "≈ 28× like-for-like, under correction" → "18–28× by basis (RL-02)" | L2.1 links | PN-35 |
| V3-06 | "PN-11 being corrected" → closed reference (27.9 at *P* = 100, R7 §4.2) | L7 links | PN-35 |
| V3-07 | Q-R6-07 "19 of 44" → **20 of 44 (11 none + 9 state-gating only)** | key-change table | PN-36 |
| V3-08 | defect log "D1–D66" → **D1–D65** (last D-number in `docs/DEFECT_LOG.md` is D65) | §0.2 | PN-38 |
| V3-09 | §7 relation sentence to R8 §5 (77 ● of 418 per category × MD) | §7 | PN-39 |
| V3-10 | Header: version v0-3, date 2026-10-24, progress bar | header | — |

---

## Key changes v0-1 → v0-2

Every retired key and its replacement (R9 §3.1). Phase 1 keys stay frozen.

| Retired (v0-1) | → New (v0-2) | Content | Authority |
|---|---|---|---|
| ~~Q-R7~~ | → **Q-R6-01** | Terminology Freeze O1–O17 re-read | R9 §3.1 Table A |
| ~~Q-R8~~ | → **Q-R6-02** | add LSP8, CVIN-Combined, MOBI profile, ZK-VIN as options? | same |
| ~~Q-R9~~ | → **Q-R6-03** | SOL-01: this repo or sandbox lineage? | same |
| ~~Q-R10~~ | → **Q-R6-04** | is the M5 on-chain pseudonym pool meant to be unlinkable? (answer with Q-R8-04) | same |
| ~~Q-R11~~ | → **Q-R6-05** | D52 fix vs upstream fidelity | same |
| ~~Q-R12~~ | → **Q-R6-06** | reentrancy audit scope — **closed in v0-2** by the §4.2 CEI check | same; PN-05 |
| — | **Q-R6-07** (new) | negative access-control tests missing for 20 of 44 checked rows (11 none + 9 state-gating only) (§2.L5.2 cross-check) | PN-05 |
| ~~KD-R4~~ | → **KD-R6-01** | R2 SOL-01 does not describe this tree; absorbs ~~KD-R8~~ (HAA-1 Plane A has no code) | R9 X-7 |
| ~~KD-R5~~ | → merged into **KD-R7-02** (R7 owns) | Δ = 2 s has no executed source | R9 X-1 |
| ~~KD-R6~~ | → **KD-R6-03** | the repo's "1609.2" is X.509 P-256 in JSON; name it "X.509 P-256 pseudonym-certificate baseline (1609.2-style)" | R9 X-8 |
| ~~KD-R7~~ | → **KD-R6-04** | SSI BSMs are secp256k1/SHA-256, not EIP-191 | R9 X-9 |
| ~~KD-R8~~ | → merged into **KD-R6-01** | HAA-1 Plane A has no code | R9 X-7 |
| ~~PRO-13x~~ | → **PRO-23** | SAE J2735 BSM / SPaT | PN-02 |
| ~~PRO-13y~~ | → **PRO-24** | SAE J2945/1 | PN-02 |
| ~~PRO-13z~~ | → **PRO-25** | DIDComm v2 | PN-02 |
| ~~PF-⟦1⟧..PF-⟦24⟧~~ | → R7 PF tags (incl. PF-63..66) or "qualitative" | §8 resolution table | PN-03 |
| ~~"used" / "candidate" / "configured"~~ (status words) | → **I** / **Ds** (with note) / **I** | unified scale | PN-32 |
| ~~SOL-12, SOL-15, SOL-17~~ as solutions | → "mechanism (cite as IMP)", numbers reserved | §5 | PN-09 |

ALG-17 (AES-256-GCM) and ALG-21 (gas schedule) keep their numbers, because tags are frozen once issued, but carry annotations: ALG-17 "primitive (L1.1)", ALG-21 "cost model" (PN-02).

---

## 0. Scope, sources and conventions

### 0.1 What "forward" means here

Phase 1 (R3 Table I.2): *everything above the ledger borrows ordering and nothing else; everything above L1 borrows unforgeability and nothing else.* R6 tests this against the running components. Some borrow more — host wall-clock time (D40, D51), OS randomness, the endpoint's chain id, a one-laptop trusted setup — and each such hidden dependency gets a breaking point in §4. Naming them is the contribution of going deeper (R9 §2.1 iii).

### 0.2 Repository ground truth read for this pass

v0-1 read the STATUS, register (62 numbered rows), threat model, latency budget, defect log (D1–D65), basic-ID-set and F2 capture documents, every contract source, the layer-5 circuit and Steward, the testbed providers and protocol stack, `2_w3c-ssi-layer/`, the three Hardhat configs and `SEPOLIA_VALIDATION.md` (v0-1 §0.2 lists paths).

v0-2 re-read: the status column of every D-row cited here (`DEFECT_LOG.md` §B–§G); `MOBI/ERC1056Registry.sol` (`DIDRevoked` with `previousChange`, l. 18, 47, 265); `CVINVehicleDIDRegistry.sol` (`PERMANENT_ATTRIBUTE_VALIDITY = 100 * 365 days`, l. 81); `CVINCombinedIdentity.sol` (claim ops, l. 121–123); the four reentrancy surfaces (§4.2); `CVINVehicleClaimHolder.sol` l. 500–515 (low-s and zero-address guards); `CVINVehicleAccount.sol` l. 140–168; `CVINMinimalEntryPoint.sol` l. 69–92; both Hardhat configs' `chainId` lines; `docker-compose.yml` l. 74; the `L2-identity-system` per-option and security test files (for the access-control cross-check); `results/metrics/latest/{meta.json, tables/crud_gas.csv}`.

Two repository facts shape everything below:
- **Byte-identical copies.** `cv2x-testbed/contracts/{ERC1056Registry, MOBIVIDRegistry, MOBIVIDRegistryV2}.sol` are byte-identical to `1_blockchain-identity/contracts/MOBI/` (v0-1 `cmp`; D21's fix text says the identity is CI-checked). One SCF register covers both. The builds differ (solc 0.8.20 default EVM in the testbed; 0.8.24 / `cancun` / viaIR in the main tree), so gas differs by build (#22 vs #29), not by source. The testbed does **not** compile `EthereumDIDRegistry`.
- **Two "ERC-1056" contracts** (register §1.1, K-5): `EthereumDIDRegistry` (uPort/DIF lineage, implicit identities, `*Signed` meta-transactions; prefix **EDR**) and `ERC1056Registry` (vehicle profile, explicit `registerVehicle`, terminal `revokeIdentity`, no `*Signed`; prefix **VPR**). They are never pooled.

### 0.3 Tag conventions

`HW-nn` hardware class · `PRO-nn` protocol · `ALG-nn` algorithm · `IMP-<sublayer>-nn` implementation · `SCF-<prefix>-nn` contract function · `BP-LH-nn`, `BP-Lx.y-nn` breaking points · `SOL-10+` repository solutions. Cited, never redefined: Phase 1 tags; R7's `PF-32..66`, `SYM-25..58`; R8's `RV-`, `MD-`, `PAR-` (R8 owns PAR-, R9 §3.1); R9's `PN-`, `SLD-`, `NC-`, `CA-`, `PRM-`, `B-`. Register rows are `#n`; defects `Dn`; threat-model goals `G1–G8` and trust assumptions `TM-T1..T4` (the prefix avoids a collision with `T-0x`). R3 requirements are written **R1–R8** (channel) and **I1–I9** (identity) as in R3 §1; where "R1" could be read as the Roots document, it is written "req. R1".

**Defect status column.** Every register table in §2 now ends with **Dn @ 2026-10-22**: *fixed* (with commit), *part* (fixed with an open residue named in the log), *open*, *doc* (documented, no code change), or "—". It is read from `DEFECT_LOG.md`, which wins over this document (R9 §3.4 rule).

---

## 1. The extended stack

The table refines Phase 1's eight layers into the brief's sub-layers and adds LH beneath L0. Read top to bottom, it is the dependency direction ("secured by"). Read bottom to top, it is the enabling direction.

| Sub-layer | One-line role | Trusts from below | Gives above | Phase 1 tags |
|---|---|---|---|---|
| **LH.1** CPU / silicon / RNG | executes faithfully; supplies entropy | physics; foundry; microcode | correct arithmetic; unpredictable bits | below L0; `BP-L1-01/02`, `PF-06` |
| **LH.2** secure elements | isolate keys; sign without export | LH.1; vendor certification | non-exportable keys; attestation | T-I05; `BP-L1-07`, `BP-L7-01` |
| **LH.3** vehicle E/E | ECUs, gateway, OBU; bus | LH.1, LH.2 | host for agent and V2X stack; vehicle data | L7 endpoint; `BP-L7-01` |
| **LH.4** radio and positioning | V2X modems; GNSS | LH.1; RF; constellation | bearer; **time and position** | L0; hidden dependency of req. R8 |
| **LH.5** server / cloud hosts | run clients, RPC, resolvers | LH.1; hypervisor; operator | a place for L3 and Plane V | SOL-02 substrate |
| **L0.1** PHY / MAC | 802.11p/bd, PC5 mode 4, NR-V2X, Uu | LH.4 | best-effort frames | T-01 analogue |
| **L0.2** IP / transport | IP, UDP, TCP, QUIC; WSMP | L0.1 | datagrams / streams | T-01 |
| **L0.3** P2P overlay | RLPx, discv4/v5, libp2p | L0.2; node keys | discovery, propagation | T-02, T-03; `BP-L0-01..03` |
| **L0.4** RPC transport | JSON-RPC, Engine API, TLS | L0.2; LH.5 | a client's window into state | HAA-1 Plane V read path |
| **L1.1** primitives | secp256k1, P-256, Ed25519, keccak, SHA-256, Poseidon, BN254, BLS12-381 | LH.1 entropy; hardness | unforgeability, binding | T-04..07, T-I10/11/14/15 |
| **L1.2** crypto libraries | libsecp256k1, noble, `cryptography`, snarkjs/circom … | L1.1; LH.1; runtime | callable implementations | `BP-L1-07` locus |
| **L2.1** state structures | MPT, receipts, blooms, mappings | L1.1 keccak | authenticated state and history | T-08, T-09; `BP-L2-01` |
| **L2.2** storage engines | LevelDB, RocksDB, in-memory | LH.5; OS | persistence | — |
| **L2.3** off-chain structures | status lists, accumulators, CAS | L1.1; Plane D | revocation, availability | T-I12, SOL-09 |
| **L3.1** consensus protocol | QBFT, IBFT 2.0, Clique, Gasper, automine | L0.3; validator keys | one ordered history; finality | T-11..13; `BP-L3-01..06` |
| **L3.2** client implementation | Besu, Geth, Hardhat, Anvil, Ganache | L3.1; L2.2; L1.2 | a running node | monoculture |
| **L4.1** fee model | gas, EIP-1559, free-gas | L3 | price, back-pressure | T-14, T-17 |
| **L4.2** permissioning / governance | allowlists, validator admission, contract roles | L3; L5 | who may write / validate | `BP-L4-04/06` |
| **L4.3** capacity | block gas limit, interval | L3.1 | ops/s ceiling | `PF-24` |
| **L5.1** EVM and precompiles | opcodes, 0x01, 0x02, 0x05–0x08 | L1.2 in client; L2.1 | deterministic execution | T-10 |
| **L5.2** contract code | this repo's 24 contract files | L5.1; L4.2 roles | registries, claims, gates | O1–O9, SOL-06 |
| **L5.3** transaction formats | legacy/155, 2930, 1559, 4844, 7702; UserOps | L1.1; L3 | replay-scoped transitions | `BP-L5-02/03` |
| **L6.1** DID methods | did:ethr, did:mobi, did:nft, did:key, did:web | L5.2; L0.4 | identifier → key (I1, I3) | T-I17; O1, O10–11 |
| **L6.2** credential formats | Data Integrity (thesis cryptosuite), SD-JWT-style digests | L1.1; L6.1 | attribute binding, disclosure (I5–I7) | T-I11/13/17/20 |
| **L6.3** IDTX functions | IMinimalSSI F1–F12; IdtxExecutor; ZkVinGate | L5.2; L6.1/6.2 | identity-dependent actions | SOL-06; I-24 |
| **L7.1** wallet / agent | ethers, web3.py, resolvers, Steward | L1.2; L0.4; LH.2 | custody, resolution, policy | O17, T-I22 |
| **L7.2** messaging | freshness module, JSON-signed BSM/SPaT, 1609.2 (Ds) | L6; L1; LH.4 time | authenticated fresh messages (req. R1, R8) | T-I05/09/18; `BP-L7-04/05` |
| **L7.3** scenarios | SUMO V2V, RSU/TMC, tolls, lifecycle, ZK admission | everything below | the application claims | `BP-L7-07` |

---

## 2. Layer by layer

### LH — Hardware and physical trust anchors

> **Does for above:** supplies unpredictable bits and an isolated place to use a private key (to L1), a vehicle, a radio, a clock and a position (to L7). **Trusts below:** physics, a foundry and vendor firmware, none of which the programme can inspect. **Remember:** nothing at LH is measured. Every "unforgeable" above is conditional on rows here.

Keys are generated in software on a cloud Xeon (#27, #57 headers); the threat model puts HSM and side-channel compromise out of scope (`docs/THREAT_MODEL.md` §2, §6). The sharpest repository fact is a code path, not a device: the testbed derives vehicle controller keys as SHA-256(vehicle_id) (`erc1056_provider.py` l. 370–388, marked INSECURE in source).

#### LH.1 CPU, silicon and RNG

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn @ 10-22 |
|---|---|---|---|---|---|---|---|
| HW-01 | General-purpose CPU (x86-64 Xeon of record) | executes node, prover, verifier | microcode; isolation | all M0/M1 results | M as environment only (#27 "Xeon 2.10 GHz × 4"; #57 "2.80 GHz Xeon") | result headers | — |
| HW-02 | Hardware RNG (RDRAND/RDSEED, ARM TRNG) | entropy into the OS pool | silicon; SP 800-90B health tests (S) | IMP-LH.1-01 | — (never observed) | — | — |
| IMP-LH.1-01 | OS CSPRNG via `secrets`, `cryptography`, `Account.create()` | key and nonce generation | HW-02; kernel | ALG-01, ALG-02 | I | `steward/vault.py`; `erc1056_provider.py` (`ec.generate_private_key(SECP256K1)`) | — |
| IMP-LH.1-02 | **Test-only deterministic keys**: controller = SHA-256(vehicle_id) | re-derive accounts without storage | nothing (public) | testbed only | I (labelled INSECURE) | `erc1056_provider.py` `vehicle_account()` l. 370–388 | — (R9 CA-18 proposes a guard) |
| IMP-LH.1-03 | Seeded PRNG (`CVIN_SEED`, seeds 1–30) | reproducible incidental randomness | none by design | reproducible gas (#47) | I | register §1 (WM-2 B1) | — |

#### LH.2 Secure elements

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| HW-03 | HSM (OBU/RSU, CA) | holds signing keys; signs on request | FIPS 140-3 / CC (S) | ALG-05 for PRO-12 | Ds (THREAT_MODEL §2 assumes it away) | — | — |
| HW-04 | TPM 2.0 | measured boot; sealed keys | TCG (S) | node-key protection | — | — | — |
| HW-05 | TEE (SGX/TDX, TrustZone, SEV) | memory-isolated execution | vendor attestation | possible home for the Steward vault (SOL-14) | Ds (v0-1 "candidate"; no design document names it) | — | — |
| HW-06 | Secure element / eSIM / wallet SE | non-exportable secp256k1 owner key | CC EAL5+ (S) | every SCF write's owner key | Ds (`erc1056_provider.py` docstring) | — | — |

#### LH.3 Vehicle E/E architecture

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| HW-07 | ECUs and central gateway | host functions; domain firewall | ISO/SAE 21434; UN R155 (S) | host for L7.1 | — | — | — |
| HW-08 | OBU | V2X processor + HSM + modem | HW-03, HW-09 | PRO-12, PRO-23 | I (simulated as a Python object) | `protocols/cv2x_stack.py` `CV2XStack` | — |
| PRO-01 | CAN / CAN-FD | in-vehicle bus, no native authentication | AUTOSAR SecOC (S, optional) | odometer and sensor data behind lifecycle events | — | — | — |
| PRO-02 | Automotive Ethernet + MACsec | in-vehicle backbone | IEEE 802.1AE (S) | as PRO-01 | — | — | — |

#### LH.4 Radio and positioning hardware

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| HW-09 | V2X modem (802.11p; PC5) | 5.9 GHz bearer | regulatory certification | L0.1 | I (FSPL + Gaussian shadowing model, `PHYLayer`) | `cv2x_stack.py` l. 256–360 | — |
| HW-10 | GNSS receiver | **time** (PPS, UTC) and **position** | signal integrity (civil authentication only via Galileo OSNMA, S) | the freshness rule (IMP-L7.2-01); BSM position; PC5 sync | Ds (`freshness.py` assumes "GNSS-disciplined OBU clocks") | — | — |

#### LH.5 Server and cloud hosts

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| HW-11 | Cloud VM / container host (CI, measurement host) | runs Hardhat, Python, snarkjs | hypervisor; operator | every M row | M as environment (#52, #55 same-host replicates) | `.github/workflows/` | — |
| HW-12 | Validator / RPC node host | runs IMP-L3.2-01 | HW-04; governance | SOL-02 Plane A | Ds | — | — |
| IMP-LH.5-01 | Docker compose (SUMO, ns-3, PKI-CA, identity manager, Ganache) | testbed orchestration; maps `8545:8545` | container isolation | L7.3 | Ds-level file; no M row uses it | `cv2x-testbed/docker/docker-compose.yml` l. 74 | — |

↑ see L0 (the radio and the hosts carry L0's frames and RPC) and L1 (entropy → ALG-01). ↓ nothing below. R7: PF-41/42 (RNG; demoted to one ch6 sentence by R9 DRP-07), PF-43 (hardware *t_ver*, E), PF-47 (GNSS holdover). R8: RV-HW-01..11 (R8 v0-2 splits RV-HW-10 into CPU M-as-environment and RNG —, per PN-23d), RV-THR-10, RV-THR-15 (deterministic test key, to be added by R8 v0-2 per PN-28).

---

### L0 — Network

> **Does for above:** moves bytes between parties who are not co-located. **Trusts below:** LH.4 for a bearer, LH.5 for hosts, LH.1 for node keys. **Remember:** L0 promises nothing about sender, delivery or exclusivity, so every property above it is cryptographic. In this programme the radio is a simulation and the chain network is a loopback.

Radio: `cv2x_stack.py`. Chain side: in-process EVM (M1) or `127.0.0.1:8545` (M1-H/HTTP, "≈1–2 ms" per round trip). No P2P overlay ever carried a block. L0 supplies *conditions* for R7 to bound; v0-2 adds one R7 found: the radio itself can link pseudonyms (BP-L0.1-02).

#### L0.1 PHY / MAC

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| PRO-03 | IEEE 802.11p / bd (DSRC, ITS-G5) | OFDM PHY + EDCA, outside-BSS broadcast | none (open medium) | PRO-08; BSM at 10 Hz | — (named only as a frequency default in `PHYLayer`) | `cv2x_stack.py` | — |
| PRO-04 | LTE-V2X PC5 **mode 4** (Rel-14) | sidelink with sensing-based SPS | GNSS sync (HW-10) | V2V broadcast without a base station | I (`ResourcePool` 50 PRB × 4 sub-channels, −90 dBm sensing; `MODE_4`); no reselection counter (Q-R7-04) | `cv2x_stack.py` l. 27–31, 125–200 | — |
| PRO-05 | PC5 mode 3 | network-assisted allocation | eNB scheduling | as PRO-04 | I (enum only) | same | — |
| PRO-06 | NR-V2X sidelink (Rel-16/17) | 5G unicast/groupcast | as PRO-04 | manoeuvre coordination (`MCM` enum) | — | — | — |
| PRO-07 | Cellular Uu | vehicle ↔ backend | 3GPP AKA, SIM | RPC reads, CRL download, revocation backhaul | — (hidden precondition of any M2 read) | — | — |

#### L0.2 IP and transport

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| PRO-08 | WSMP (IEEE 1609.3) | non-IP single-hop datagrams with PSID | none (1609.2 above) | PRO-12 | — | — | — |
| PRO-09 | UDP / TCP over IPv4/6 | datagrams, streams | none | L0.3, L0.4 | M as condition (TCP loopback, M1-H/HTTP, #39) | — | — |
| PRO-10 | QUIC | encrypted multiplexed transport | TLS 1.3 (T-I04) | libp2p; DIDComm | — | — | — |

#### L0.3 P2P overlay

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| PRO-11 | devp2p **RLPx** | ECIES handshake, AES-CTR framing with MAC | node key (ALG-01) | eth/68 gossip; QBFT messages | — (Hardhat has no peers) | — | — |
| PRO-11a | discv4 | Kademlia over UDP, signed packets | node keys; no admission cost (T-02, T-03) | PRO-11 | — | — | — |
| PRO-11b | discv5 | ENR, encrypted handshake, topic ads | as 11a plus session keys | consensus-layer clients | — | — | — |
| PRO-11c | libp2p (gossipsub, Noise, yamux) | consensus-layer P2P | Noise (T-I08) | Gasper | — | — | — |
| IMP-L0.3-01 | Besu static-nodes / bootnodes + node permissioning | closed consortium peer set | IMP-L4.2-01 | SOL-02 | Ds | — | — |

#### L0.4 RPC transport

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| PRO-13 | Ethereum JSON-RPC over HTTP | `eth_call`, `eth_getLogs`, `eth_sendRawTransaction`, `eth_getBlockByNumber`, `debug_traceTransaction` | **nothing by default** (no auth, no TLS on loopback, responses not proven) | every resolver and provider read | M: #21 (5 RPCs per uncached verify), #31/#51 (calls and bytes vs history), #37 (one-call probe) | `erc1056_provider.py`; `did_resolver.py`; `1_blockchain-identity/benchmarks/` | D51 fixed (`7d08dce`, adds one `eth_getBlockByNumber`) |
| PRO-13a | JSON-RPC over WebSocket (`eth_subscribe`) | push of logs/heads | as PRO-13 | a revocation push channel | — | — | — |
| PRO-13b | Hardhat RPC (`hardhat_getAutomine`, `evm_mine`) | node control | none | reproducible M1 runs | I | `experiment_pki_vs_erc1056.py` ≈ l. 901 | — |
| PRO-14 | Engine API (JWT) | EL ↔ CL | HS256 shared secret | Gasper-backed Option C | — | — | — |
| PRO-15 | TLS to a remote provider | server authentication | X.509 (T-I02) | M2 Sepolia | Ds (procedure only; `sepolia_validation.json` never committed, F2 CAPTURE §5; R9 NC-07) | `scripts/validate_sepolia.js` | — |
| IMP-L0.4-01 | web3.py `HTTPProvider` + `ExtraDataToPOAMiddleware` | Python RPC client | PRO-13 | providers, MOBI client | I; the PoA middleware is the **only** code hook toward a PoA chain | `erc1056_provider.py` l. 25–27; `mobi_vid_provider.py` l. 30, 69 | — |
| IMP-L0.4-02 | ethers v6 `JsonRpcProvider` / in-process provider | JS RPC client | PRO-13 | harness, Sepolia and ZK scripts | I (M as condition of every M1 row) | `package.json` (`ethers ^6.10.0`) | — |

↑ see L1 (what the bytes carry is signed there) and L6.1 (resolution is the main L0.4 consumer). ↓ see LH.4 (bearer, time), LH.5 (RPC host). R7: PF-44 and PF-45 (airtime; reselection linkability 0.136 / 0.449 / 0.805 by *P_keep*, R7 §4.4), PF-48 (backhaul renewal), PF-54 (read path vs staleness). R8: RV-NET-01..14, RV-PROT-05..09/14, RV-READ-07/11/12, RV-THR-07, RV-THR-13 (lying RPC endpoint, R8 v0-2 per PN-28).

---
### L1 — Cryptographic primitives and their libraries

> **Does for above:** unforgeability and binding. L5 borrows `ecrecover` to decide who may write, L6 borrows signatures to bind a key to an identifier, L7 borrows them to decide whom to trust on the road. **Trusts below:** LH.1 entropy and hardness assumptions (ECDLP; collision resistance of keccak-256 and SHA-256; q-type pairing assumptions for Groth16). **Remember:** the repository runs at least six independent secp256k1 implementations and three on-chain signature schemes. Each is a separate place a bug or an inconsistency can live.

The six: `cryptography`/OpenSSL, `coincurve`/libsecp256k1, `eth-keys`/`eth_account`, ethers/noble, Hardhat's EthereumJS `ecrecover`, and pure-Python `zkid/ec.py`.

#### L1.1 Primitives and algorithms

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| ALG-01 | secp256k1 key generation | d ∈ [1, n−1]; Q = dG | IMP-LH.1-01; ECDLP (T-06) | every account and did:ethr | I | `zkid/ec.py`, `vault.py`, `erc1056_provider.py` | — |
| ALG-02 | ECDSA secp256k1, RFC 6979 nonces | sign a 32-byte digest | ALG-01; RFC 6979 (S) removes `BP-L1-02`'s RNG dependence | L5.3 tx signatures; EIP-191 | I (via eth_account / ethers; RFC 6979 is S library behaviour, not verified here) | — | — |
| ALG-03 | ECDSA public-key recovery (`ecrecover`) | (digest, v, r, s) → address | ALG-02; EIP-2 low-s (S) applies to tx signatures only | contract authorisation; offline VC verification | I (in 9 contracts; costs inside M gas rows) | `EthereumDIDRegistry.sol` l. 172, 234, 296, 351, 400 | D53 open |
| ALG-04 | ECDSA secp256k1 over **SHA-256** | testbed BSM signatures under did:ethr | ALG-01; SHA-256 | IMP-L7.2-02 | M inside #21, #27 (KD-R6-04: not EIP-191) | `erc1056_provider.py` `sign_message` (`ec.ECDSA(hashes.SHA256())`) | — |
| ALG-05 | ECDSA **P-256** / SHA-256 | X.509 P-256 baseline signatures | ECDLP on P-256 | PKI baseline (#21, #27) | M | `pki_identity.py` l. 52–53, 182 | — |
| ALG-06 | Ed25519 | EdDSA | ECDLP on Curve25519 | did:key, DIDComm, Indy | — (attribute name in a comment only) | `EthereumDIDRegistry.sol` l. 310 | — |
| ALG-07 | keccak-256 | addresses, selectors, slots, signed digests | sponge security (T-07) | L2.1; L5.3; every SCF digest | I (pure-Python reference with 24 rounds) | `zkid/hashing.py` | — |
| ALG-08 | SHA-256 | message digests; replay-cache keys; VIN hashes | T-07 | IMP-L2.3-06; D64; #60 | M (#60 enumeration rate) | `freshness.py`; `mobi_vid_provider.py` | D64 open |
| ALG-09 | Poseidon (circomlib) | SNARK-friendly hash over BN254 Fr | algebraic-hash assumptions | ZK-VIN commitment, tree, nullifier | M inside #56–#58 | `circuits/zkvin.circom` | — |
| ALG-10 | BN254 pairing | e: G1 × G2 → GT | ≈ 100-bit after kTNFS (R4 `PF-10`; R9 PN-18 asks R7 to log the source) | Groth16 on chain | M inside #58 | `Groth16Verifier.sol` l. 94, 104, 178 | — |
| ALG-11 | BLS12-381 pairing | ≈ 120-bit curve | as ALG-10 | BBS+, Gasper, EIP-2537 | — | — | — |
| ALG-12 | Groth16 (T-I14) | constant-size zk-SNARK | ALG-10; per-circuit **trusted setup** (`BP-L1-06`) | SOL-11 | M: #56 (3,498 constraints), #57 (prove 398.6 ms / verify 18.42 ms medians, M0), #58 (`admit` 301,163 gas) | `5_zkp-agent-identity/` | — (R9 CA-06 proposes a defect) |
| ALG-13 | PLONK / Halo2 / Bulletproofs | universal or transparent proofs | as above, no per-circuit setup | alternative to ALG-12 | — | — | — |
| ALG-14 | Sigma protocols (Schnorr PoK, Pedersen, Chaum–Pedersen, CDS OR, Fiat–Shamir) | interactive → NIZK over secp256k1 | ECDLP; ROM (T-I10, T-I15) | Steward proofs; on-chain Schnorr | M: #59 (timings, group-op counts), #58 (Schnorr PoK 28,775 gas) | `zkid/sigma.py`, `transcript.py` | — |
| ALG-15 | "ecrecover hack" Schnorr verification | R' = s·G − e·P via `ecrecover`, compare addresses | ALG-03; keccak in the ROM | SCF-SCH-01/02 | M (#58) | `SchnorrEcrecoverVerifier.sol` l. 5–25 | — |
| ALG-16 | CL signatures / BBS+ | multi-show anonymous credentials | q-SDH, LRSW, strong RSA | O12; BBS cryptosuite | — | — | — |
| ALG-17 | AES-256-GCM — *primitive (L1.1), not an algorithm in the brief's sense* | authenticated encryption of the VIN beside its salted hash | AES; nonce uniqueness | MOBI `encryptedVIN` | I | `mobi_vid_provider.py` l. 34, 105–110 | D64 open (the ciphertext does not hide the VIN in this realisation) |

#### L1.2 Cryptographic libraries

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L1.2-01 | Python `cryptography` (OpenSSL) | P-256 and secp256k1 ECDSA, X.509, AES-GCM | OpenSSL constant-time code | PKI baseline, testbed signing | M as environment (#21 cryptography 50.0.1 at A3b; #27 49.0.0) | `requirements.txt` | — |
| IMP-L1.2-02 | `coincurve` (libsecp256k1) | fast secp256k1 | libsecp256k1's reviewed constant-time code | V2V warm verify | M as environment (#27 coincurve 21.0.0) | `5_zkp-agent-identity/README.md` | — |
| IMP-L1.2-03 | `eth-account` / `eth-keys` / `ecdsa` / `pycryptodome` | Ethereum signing, EIP-191, keccak | IMP-L1.2-02 or pure Python | VC issuer, providers, Steward | I | `vc_issuer.py` l. 36–37, 44 | — |
| IMP-L1.2-04 | ethers v6 (noble-curves) | JS signing, ABI | noble's audited code | harness, Sepolia script | I | `package.json` | — |
| IMP-L1.2-05 | EthereumJS EVM in Hardhat (precompiles) | `ecrecover`, `sha256`, bn256 | its own crypto deps | every M1 number | M as condition (Hardhat 2.28.6, #21, #58) | — | — |
| IMP-L1.2-06 | BouncyCastle / gnark-crypto in Besu | Besu precompiles and signing | JVM; vendor review | SOL-02 | Ds | — | — |
| IMP-L1.2-07 | circom 2.2.2 + circomlib 2.0.5 | R1CS and witness generator | compiler and template correctness | ALG-12 | M as tool (#56) | `circuits/build_circuit.sh` | — |
| IMP-L1.2-08 | snarkjs 0.7.6 | powers of tau, setup, prove, verify, verifier export | ffjavascript arithmetic | ALG-12; `Groth16Verifier.sol` | M as tool (#57) | same | — |
| IMP-L1.2-09 | `zkid` (pure-Python secp256k1, keccak, sigma) | counted proof arithmetic | nothing: **"not constant time and must not hold production keys"** | #59, #62 | M (research only) | `zkid/ec.py` l. 1–8 | — |
| IMP-L1.2-10 | anoncreds-rs | CL credentials, accumulators | ALG-16 | O12 | — | — | — |
| IMP-L1.2-11 | OpenZeppelin 5.0.2 `ECDSA`, `MessageHashUtils` | recovery with low-s and zero-address rejection | ALG-03, EIP-2 | SCF-MOBI2-04 | I (cost inside #28) | `MOBIVIDRegistryV2.sol` l. 5–6, 369–377 | D54 fixed (2026-10-17) |

↑ see L5.1 (the EVM's `ecrecover` is IMP-L1.2-05), L6.2 (VC proofs), L7.2 (BSM signing). ↓ see LH.1 (entropy for ALG-01/02). R7: PF-32 (ECDSA), PF-33 (keccak; 19.93-bit VIN preimage, #60), PF-34 (commitments: hiding iff salted), PF-35 (Groth16 with single-party setup), PF-51 (on-chain Groth16 cost). R8: RV-PRIM-01..15, RV-SIG-01..04/09, RV-ALG-05/06, RV-THR-01. R9: PRM-L1.1-01..04 lock the digest, hash, salt and setup choices; B-03 (one scheme) and B-05 (salted VIN) block them.

---

### L2 — Authenticated data structures and storage

> **Does for above:** turns L1's hashes into structures whose contents can be proved — a state root over every slot, a receipts root over every event. **Trusts below:** L1.1 keccak for binding, L2.2 for not losing data. **Remember:** in this programme that proof is never exercised. Hardhat state is read through JSON-RPC, which returns values, not proofs.

A did:ethr resolver replaying events trusts that its logs are those under the receipts root. ERC-1056 attributes live *only* in logs (#49), so receipts and the `changed`/`previousChange` list are the whole DID document. v0-1 reported that list as cut by two contracts; it is not (D21, D22 fixed; IMP-L2.1-04).

#### L2.1 State structures

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| ALG-18 | Merkle-Patricia Trie (state, storage, tx, receipts) | authenticated map; root in header | ALG-07 (T-08) | `eth_getProof` light verification | I implicitly in Hardhat; **never proved against** | — | — |
| IMP-L2.1-01 | Besu Bonsai tries | MPT with diff-based storage | ALG-18 | SOL-02 | Ds | — | — |
| IMP-L2.1-02 | Receipts and log blooms | events per tx; 2,048-bit bloom per block | receipts root | **the ERC-1056 document** (U3 is "1 SSTORE / 0 zero→nonzero, 288 B" of log, #49) | M (#49 log bytes; #31/#51 `eth_getLogs` walk: 112 RPC calls / 87 KB at h = 50) | `EthereumDIDRegistry.sol` events | — |
| IMP-L2.1-03 | Solidity mapping storage | `owners`, `delegates`, `changed`, `nonce`, `revoked`, `vehicleBirths`, `nullifierUsed` … | ALG-07; trie | every view SCF; IdtxExecutor reads | M as SSTORE counts (#30: zero→nonzero 8 / 92 / 83 for ERC-1056 / 721 / 725 lifecycles) | all contracts | — |
| IMP-L2.1-04 | ERC-1056 `changed[identity]` list (`previousChange` pointers) | lets a resolver walk events backwards | IMP-L2.1-02; contract discipline | did:ethr resolution (**ALG-23**; v0-1 wrongly wrote ALG-21) | I; **not cut** on this tree: VPR's `DIDRevoked` carries `previousChange` (D21 fixed `65a143f`; `ERC1056Registry.sol` l. 18, 47); CMB claim ops no longer advance `changed` and emit `DIDClaimChanged(…, previousChange)` (D22 fixed `65a143f`, merged semantics `bd90004`) | `EthereumDIDRegistry.sol`; `MOBI/ERC1056Registry.sol`; `CVINCombinedIdentity.sol` l. 121–123 | D21 part; D22 part |

#### L2.2 Storage engines

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L2.2-01 | Hardhat in-memory state | ephemeral M1 state | process memory | all M1 gas | M as condition | — | — |
| IMP-L2.2-02 | RocksDB (Besu) / Pebble, LevelDB (Geth) | persistent KV under the trie | disk; fsync | SOL-02 durability | Ds | — | — |
| IMP-L2.2-03 | Python dict "centralized registry" | mutable, unauthenticated baseline | nothing (F2 CAPTURE §5) | PKI/centralised rows (#33) | M as baseline | `centralized_vehicle_registry.py` | — |
| IMP-L2.2-04 | PKI provider's `ct_log` | "a plain list", not a CT log | nothing | — | I | `centralized_provider.py` l. 62 | — |

#### L2.3 Off-chain structures

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L2.3-01 | VC `credentialStatus` + `RevocationRegistry` (memory or JSON file) | off-chain VC revocation | the file's host; no anchoring | F7 revokeCredential | I | `vc_issuer.py` l. 110–175 | — (R9 B-14) |
| IMP-L2.3-02 | Bitstring status list (SOL-09 profile SL) | herd-private revocation | list size (R4 `PF-29`) | SOL-09 | Ds | — | — |
| IMP-L2.3-03 | CL / bilinear accumulator | non-revocation witness | T-I12 | SOL-09 AC | — | — | — |
| IMP-L2.3-04 | Poseidon Merkle tree of WMIs (depth 4) | manufacturer allowlist in the ZK statement | ALG-09 | SOL-11 | M inside #56–#58 | `zkvin.circom` `MerkleInclusion(4)` | — |
| IMP-L2.3-05 | IPFS / CAS | content-addressed bodies | CID; pinning owner | `tokenURI`, `recordURI`, `dataHash` | — ("no IPFS anywhere", F2 CAPTURE §5); lifecycle backend discards the body | `lifecycle_backends.py` l. 191–195 | — |
| IMP-L2.3-06 | Replay cache (bounded `OrderedDict`, key = (signer, SHA-256(signed bytes))) | reject duplicates in the window | ALG-08; size bound | IMP-L7.2-01 | M (#45 I2 replay checks 30/30); default 65,536 entries holds 5,958 senders at 10 Hz × 1.1 s (R7 PF-53; the docstring's "650" is wrong, R9 CA-08) | `freshness.py` | D29 fixed |

↑ see L6.1 (resolution walks IMP-L2.1-04), L6.3 (IdtxExecutor reads IMP-L2.1-03). ↓ see L1.1 (keccak), LH.5 (disks). R7: PF-52 (storage vs log; 18–28× by basis (RL-02)), PF-53 (cache sizing). R8: RV-DLT-03, RV-READ-05/06/08/09/13, RV-SVC-04/05.

---

### L3 — Agreement

> **Does for above:** makes a registry *one* registry — a single ordered sequence, so "the owner of this DID" has one answer. **Trusts below:** L0.3 to deliver within a bound; L1 for validator signatures. **Remember:** the executed mechanism is Hardhat automine: *N_v* = 1, no block interval, finality trivially immediate (R7 PF-39). Gas transfers to other EVM networks; latency and finality do not (R9 SLD-01, NC-01).

Phase 1 assumed QBFT with Δ = 2 s (R4 `PF-25`, `PF-28`); R9 X-1 and KD-R7-02 re-label those rows DESIGN. Automine gives ordering trivially and safety and liveness not at all — fine for gas, wrong for finality. It is the deepest gap between Phase 1's assumptions and the code.

#### L3.1 Consensus protocol

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| ALG-19 | Hardhat automine | one block per transaction, immediately | single process | M1 ordering | M as condition (`meta.json` `automine: true`, chain 31337) | `1_blockchain-identity/hardhat.config.js` | — |
| ALG-19a | Hardhat interval mining (`auto: true, interval: 1000`) | also mine every 1,000 ms | single process | testbed node (chain 1337) | I; mode recorded per run (`hardhat_getAutomine`) | `cv2x-testbed/hardhat.config.js` l. 15–21 | — |
| ALG-20 | QBFT (T-12) | finality at 2f_B+1 commit seals; round change on timeout | N_v ≥ 3f_B+1; partial synchrony (R4 `PF-16`, `PF-17`; R7 PF-37) | SOL-02 Plane A | Ds | — | — |
| ALG-20a | IBFT 2.0 | QBFT's predecessor | as ALG-20 | — | — | — | — |
| ALG-20b | Clique (EIP-225) | round-robin PoA | honest signer majority | dev/test nets; `extraData` the PoA middleware tolerates | — | — | — |
| ALG-20c | Gasper | PoS finality per epoch pair | ⅔ stake honest; BLS | Sepolia, mainnet (Option C) | Ds (M2 never run) | — | — |

#### L3.2 Client implementation

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L3.2-01 | Hyperledger Besu | EL client with QBFT, permissioning, privacy (O15) | IMP-L1.2-06; IMP-L2.2-02 | SOL-01 (as R2 describes it), SOL-02 | **Ds** — named only in `V2_DESIGN.md` l. 391 and F2 CAPTURE; no config, genesis or trace | — | — |
| IMP-L3.2-02 | Hardhat Network 2.28.6 | in-process / localhost dev chain | IMP-L1.2-05 | all M1, M1-H, M1-H/HTTP rows | M (#21, #39, #58) | both trees | — |
| IMP-L3.2-03 | Geth | reference Go client | — | Sepolia nodes behind PRO-15 | — | — | — |
| IMP-L3.2-04 | Anvil (Foundry) | Rust dev chain | — | R2's SOL-01 "Foundry" | — (absent from this tree; KD-R6-01) | — | — |
| IMP-L3.2-05 | Ganache | JS dev chain in the compose file; `ganache` network on 7545 | — | IMP-LH.5-01 | Ds (configured; no M row uses it) | `docker-compose.yml`; `cv2x-testbed/hardhat.config.js` l. 26–29 | — |
| IMP-L3.2-06 | GoQuorum | permissioned EL | — | — | Ds (name only) | `V2_DESIGN.md` l. 392 | — |

↑ see L4 (capacity and permissioning are rules L3 enforces), L5.3 (EIP-155 chain id is an L3 identity), L6.3 (IDTX intent/fulfil races need real block time). ↓ see L0.3 (no overlay ever ran), L1.1 (validator keys). R7: PF-37 (quorums), PF-38 (messages), PF-39 (automine is *N_v* = 1), PF-40 (t_conf with round changes) — all appendix-only per R9 SLD-13 except PF-39. R8: RV-ALG-01..03, RV-DLT-01/02/07, RV-IMPL-01..05, RV-THR-06; MD-01/02/10 stay empty (R8 Q-R8-02).

---

### L4 — Economics, governance and capacity

> **Does for above:** decides who may write and how much writing the chain accepts — a price signal and an admission rule. **Trusts below:** L3 to enforce the rule. **Remember:** in this repository permissioning lives entirely in contract roles, and every role is a single EOA key. A validator set is a quorum; a contract role is not.

Gas is measured exhaustively, as a resource count, not a price: USD is ESTIMATED (#20) and the L2 fee parameter "not a defensible figure" (F2 CAPTURE §5). The instrument's block gas limit, 60,000,000, is a Hardhat default, not a design input. R4's 30 M and 100 M rows are design scenarios, not errors (R9 PN-14, X-2; R8 PAR-06 carries *G*).

#### L4.1 Fee model

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| ALG-21 | EVM gas schedule (cancun / paris) — *cost model, not an algorithm in the brief's sense* | per-opcode cost incl. EIP-2929 cold/warm, EIP-2028 calldata 4/16 gas per byte | client conformance | every gas figure | M (all gas rows; zero-byte spread #22, #47) | register §1 rules | — |
| ALG-22 | EIP-1559 base fee + tip | congestion pricing | L3 | Option B/C cost (R4 `PF-23`) | — (local `gasPrice`) | `erc1056_provider.py` `_send_tx` | — |
| IMP-L4.1-01 | Free-gas consortium (`min-gas-price=0`) | capacity by governance | IMP-L4.2-01 | SOL-02 | Ds (`BP-L4-05`) | — | — |

#### L4.2 Permissioning and governance

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L4.2-01 | Besu node/account permissioning | who may peer, who may send | admin keys of the permissioning contract | SOL-02 admission | Ds | — | — |
| IMP-L4.2-02 | QBFT validator-set votes | validator admission | ⅔ of validators | `BP-L4-04/06` | Ds | — | — |
| IMP-L4.2-03 | Contract roles: `registryAuthority` (MOBI), `ISSUER_ROLE` (1155), `MANUFACTURER_ROLE`/`SERVICE_CENTER_ROLE` (721), `governor` (ZkVinGate), `contractOwner` (CVDR), `owner` (LSP8, 735, 725xy) | issuer and manufacturer admission | **one EOA key each** | SCF-MOBI1-01..03, SCF-E1155-*, SCF-ZKG-02 | M as attack cells (#28: 43/43 defended; #45: 30/30) | §2.L5.2 | D16 part (silent `transferRegistryAuthority` open) |

#### L4.3 Capacity

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L4.3-01 | Block gas limit (instrument) | per-block budget *G* | client config | ops/s (R7 PF-49 at *G* ∈ {30 M, 60 M, 100 M}) | M as config: 60,000,000 (`meta.json` `network.blockGasLimit`) — an instrument value, not a design parameter (PAR-06) | `meta.json`; testbed results record `block_gas_limit` | — |
| IMP-L4.3-02 | `allowUnlimitedContractSize: true` | disables the EIP-170 24,576-byte limit | — | deploys of 725xy/735-class contracts | M as condition (register §1) — a **deployability caveat** | `1_blockchain-identity/hardhat.config.js` l. 63 | — |

↑ see L5.2 (the roles are SCF access checks). ↓ see L3 (enforcement), L3.1 Δ (capacity needs a block interval the executed chain does not have). R7: PF-49 (capacity, *G* and Δ both PAR), PF-50 (fleet ratio; an upper bound on a design excluded on privacy grounds, R9 PN-15), PF-60 (governance concentration). R8: RV-ALG-08, RV-DLT-04/05/10/11, RV-GOV-01/02/07.

---

### L5 — Ledger semantics: the EVM, this repository's contracts, and transaction formats

> **Does for above:** functions that read and mutate identity state under rules (owner-only, role-only, signature-gated). **Trusts below:** L5.1 `ecrecover` for who signed, L2.1 to keep the result, L3 to order it, L4.2 for who holds the admin keys. **Remember:** L5.2 is the thesis's artefact. Its signature discipline is uneven — three schemes, chain-id binding in two places only — and that is where the defect log concentrates.

The register lists every state-changing function and groups getters. v0-2 adds defect status and a negative-test cross-check for the 44 state-changing rows on EDR, VPR, MOBI1, MOBI2, CMB and E4337A (R9 §7.1 item 6).

#### L5.1 EVM and precompiles

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L5.1-01 | EVM (`cancun` target in main tree; solc default in testbed) | deterministic execution | client conformance | every SCF | M as condition | configs | — |
| PRO-16 | Precompile **0x01 `ecrecover`** | public-key recovery; returns address or zero | IMP-L1.2-05; **no low-s rule** (EIP-2 governs tx signatures, not the precompile — S) | SCF-EDR-04/06/08/10/12, SCF-CMB-06, SCF-E735-01, SCF-E4337A-01, SCF-SCH-01/02 | I (costs inside M rows) | §2.L5.2 | D53 open |
| PRO-17 | 0x02 `sha256` | SHA-256 in the EVM | IMP-L1.2-05 | not called | — | — | — |
| PRO-18 | **0x06 `ecAdd`, 0x07 `ecMul`, 0x08 `ecPairing`** (EIP-196/197, EIP-1108 prices) | BN254 arithmetic and pairing | ALG-10 | SCF-G16-01 | M in aggregate (#58: `verifyProof` estimate 256,038 incl. 21,000 base; R7 PF-51 model within 1.3 %) | `Groth16Verifier.sol` l. 94, 104, 178 | — |
| PRO-19 | 0x05 `modexp` | big-integer modexp | — | RSA/CL verifiers | — | — | — |
| PRO-20 | EIP-2537 BLS12-381 precompiles | BLS12-381 ops | ALG-11 | BBS+/BLS | — | — | — |
| IMP-L5.1-02 | `staticcall` / `delegatecall` / `call` | external calls | EVM | 725X and 4337 `execute`; IDTX reads | I | `CVINVehicleERC725XY.sol` l. 287–306 | D24 open |
| IMP-L5.1-03 | `block.timestamp`, `block.number`, `block.chainid` | chain time, height, chain id | proposer honesty within client rules | `validDelegate` expiry; `changed`; MOBI2 attestation domain; IDTX deadlines | I — **chain time** is what D51's fix adopted | `EthereumDIDRegistry.sol` l. 127; `IdtxExecutor.sol` | D51 fixed |

#### L5.2 Smart-contract function register (this repository)

Conventions. **SC** state-changing; **V** view/pure. "Root primitives" names the lower-layer tags a function rests on: `ecrecover → PRO-16/ALG-03/T-06`, `keccak → ALG-07/T-07`, `mapping → IMP-L2.1-03`, `events → IMP-L2.1-02`, `chain time → IMP-L5.1-03`. The IMinimalSSI role names the function rather than an F-number, because the F-number order inside Set A is **[B1]** in `docs/BASIC_ID_SET_EXTENSION.md` (R9 B-01; prose prefix "IMS-F*n*" once fixed). **Neg.** (in the six cross-checked prefixes only): **Y** a test calls the function as a non-authorised party and expects a revert; **st** only state-gating negatives exist (revoked, already registered); **N** no negative test found. Source of the check: `1_blockchain-identity/test/L2-identity-system/{per-option, security}/**` and `test/L1-identity-mechanisms/08-signed-op.test.js`, read for this pass, not executed.

**SCF-EDR — `ERC1056/EthereumDIDRegistry.sol` (uPort/DIF lineage; O1)**

| Tag | Function | SC/V | Access control | Events | IMinimalSSI / IDTX role | Root primitives | Neg. | Dn |
|---|---|---|---|---|---|---|---|---|
| SCF-EDR-01 | `identityOwner(identity)` | V | — | — | resolve; IDTX Owner predicate | mapping; default-to-self | — | — |
| SCF-EDR-02 | `validDelegate(identity, type, delegate)` | V | — | — | verify delegate; IDTX Delegate predicate | mapping; chain time | — | — |
| SCF-EDR-03 | `changeOwner` | SC | `onlyOwner` | `DIDOwnerChanged(…, previousChange)` | key/controller rotation (U1) | tx signature; mapping; events | Y | D26 open |
| SCF-EDR-04 | `changeOwnerSigned(identity, v, r, s, newOwner)` | SC | signature by current owner over `0x19 0x00 ‖ this ‖ nonce ‖ identity ‖ "changeOwner" ‖ newOwner` (l. 160–172) | as 03 | relayed rotation (U5 class) | ecrecover, keccak, `nonce`; **no chain id**; zero signer accepted for identity 0x0 | N (positive only, l. 53–68) | D52 doc; D53 open |
| SCF-EDR-05 | `addDelegate` | SC | `onlyOwner` | `DIDDelegateChanged` | delegates (U2) | mapping; chain time | Y | — |
| SCF-EDR-06 | `addDelegateSigned` | SC | owner signature | as 05 | relayed U2 | as 04 | N | D52, D53 |
| SCF-EDR-07 | `revokeDelegate` | SC | `onlyOwner` | `DIDDelegateChanged` (validTo = now) | revoke delegate (D1-op) | mapping; chain time | N | — |
| SCF-EDR-08 | `revokeDelegateSigned` | SC | owner signature | as 07 | relayed | as 04 | N | D52, D53 |
| SCF-EDR-09 | `setAttribute` | SC | `onlyOwner` | `DIDAttributeChanged` (value **only in the log**) | attributes (U3); issuer-key anchor | events; chain time | Y | — |
| SCF-EDR-10 | `setAttributeSigned` | SC | owner signature | as 09 | U5 meta-tx — M #50 (62,646 vs direct 35,024) | as 04 | Y (replay of a consumed meta-tx) | D52, D53 |
| SCF-EDR-11 | `revokeAttribute` | SC | `onlyOwner` | `DIDAttributeChanged` (validTo 0) | revoke attribute (D2-op) | events | Y | — |
| SCF-EDR-12 | `revokeAttributeSigned` | SC | owner signature | as 11 | relayed | as 04 | N | D52, D53 |
| — | public mappings `owners`, `delegates`, `changed`, `nonce` | V | — | — | resolver walk start | mapping | — | — |

**SCF-CVDR — `ERC1056/CVINVehicleDIDRegistry.sol` (wrapper over EDR; O1 "wrapper mode")**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-CVDR-01 | `setAuthorizedManufacturer` | SC | `onlyContractOwner` | `ManufacturerAuthorized` | issuer admission | single admin key | — |
| SCF-CVDR-02 | `createVehicleDID(vin, owner, …)` | SC | `onlyAuthorizedManufacturer` | `VehicleDIDCreated` | createDID + VIN binding — M #1 | keccak(VIN) map; reverse map not one-to-one | D20 open |
| SCF-CVDR-03 | `setVehicleAttributes(did, …)` | SC | `onlyVehicleOwner(did)` | via EDR `DIDAttributeChanged` | attributes (eight-attribute birth record) | validity `PERMANENT_ATTRIBUTE_VALIDITY = 100 * 365 days` (l. 81); the birth record **is reachable** ("permanent" = 100-year) | D18 fixed `65a143f` |
| SCF-CVDR-04 | `transferVehicleOwnership` | SC | `onlyVehicleOwner` | `VehicleOwnershipTransferred` | U4 | wrapper keeps ERC-1056 custody | D19 open |
| SCF-CVDR-05 | `updateOwnershipMapping(old, new)` | SC | requires `identityOwner(old) == new` | — | VIN-map bookkeeping after U1 | keccak(VIN); reads SCF-EDR-01 | — |
| SCF-CVDR-06 | `setServiceEndpoint` | SC | `onlyVehicleOwner` | via EDR | service endpoints | — | D1 fixed `708302a` |
| SCF-CVDR-07 | `addVerificationDelegate` | SC | `onlyVehicleOwner` | via EDR | U2 | — | D1 fixed |
| SCF-CVDR-08 | `revokeVerificationDelegate` | SC | `onlyVehicleOwner` | via EDR | revoke delegate | — | D1 fixed |
| SCF-CVDR-09 | getters `getDIDFromVIN`, `getVINFromDID`, `vehicleOwnerOf`, `getVehicleOwner`, `isValidDelegate` | V | — | — | resolve | **`getVINFromDID` returns the VIN in plaintext** (G7; R9 CA-10) | — |

**SCF-VPR — `MOBI/ERC1056Registry.sol` ≡ `cv2x-testbed/contracts/ERC1056Registry.sol` (vehicle profile; #21–#22)**

| Tag | Function | SC/V | Access control | Events | Role | Root primitives / notes | Neg. | Dn |
|---|---|---|---|---|---|---|---|---|
| SCF-VPR-01 | `identityOwner`, `isRevoked`, `lastChanged`, `getIdentityInfo` | V | — | — | resolve; the **one-call probe** (#37) | mapping | — | — |
| SCF-VPR-02 | `changeOwner` | SC | `onlyOwner` + `notRevoked` | `DIDOwnerChanged` | U1 | `changeOwner(0)` restores self-control | st | D21 fixed (gating); D26 open |
| SCF-VPR-03 | `addDelegate` | SC | `onlyOwner` + `notRevoked` | `DIDDelegateChanged` | U2 | chain time | st | — |
| SCF-VPR-04 | `revokeDelegate` | SC | as 03 | as 03 | revoke delegate | — | st | D21 fixed (gating) |
| SCF-VPR-05 | `setAttribute` | SC | as 03 | `DIDAttributeChanged` | U3 / issuer anchor — M #22 "issue" 37,807 | events | st | — |
| SCF-VPR-06 | `revokeAttribute` | SC | as 03 | as 05 | revoke attribute | mismatched value accepted | st | D16 part (this residue open) |
| SCF-VPR-07 | `revokeIdentity` | SC | `onlyOwner`; single-shot ("Identity already revoked", l. 265) | `DIDRevoked(identity, revokedAt, previousChange)` — **walk not severed** | deactivation (terminal) — M #22 revoke 75,609 (pre-fix build; D21 fix adds 547 gas per the log, re-stated in #31) | mapping; events | Y (stranger) | D21 fixed `65a143f` |
| SCF-VPR-08 | `registerVehicle(identity, publicKey)` | SC | caller is the identity (via `onlyOwner` inside `setAttribute`); not revoked; not yet transferred | `DIDAttributeChanged` (key, 1-year validity) | createDID (explicit) — M #22 register 54,868 | testbed key = SHA-256(vehicle_id) (IMP-LH.1-02) | st | — |
| SCF-VPR-09 | `updateVehicleKey` | SC | `onlyOwner` + `notRevoked` | `DIDAttributeChanged` | key rotation | **adds a key without revoking the old one** | st | D21 part (this residue open) |

**SCF-MOBI1 — `MOBI/MOBIVIDRegistry.sol` (extends VPR; MOBI VID I)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Neg. | Dn |
|---|---|---|---|---|---|---|---|---|
| SCF-MOBI1-01 | `authorizeManufacturer` | SC | `onlyRegistryAuthority` | `ManufacturerAuthorized` | issuer admission | single authority key | N | — |
| SCF-MOBI1-02 | `revokeManufacturerAuthorization` | SC | `onlyRegistryAuthority` | `ManufacturerAuthorizationRevoked` | issuer revocation | — | N | — |
| SCF-MOBI1-03 | `transferRegistryAuthority` | SC | `onlyRegistryAuthority` | **none** | governance handover | governance key = root of the registry | N | D16 part (silent; open) |
| SCF-MOBI1-04 | `registerVehicleBirth(identity, vinHash, encryptedVIN, birthCertHash, firstOwner, attrs)` | SC | `onlyAuthorizedManufacturer`, `vehicleNotRegistered` | `VehicleBirthRegistered` | createDID + birth credential | salted `vinHash` + AES-GCM (ALG-17); testbed address derivation undermines both | Y | D64 open (testbed only) |
| SCF-MOBI1-05 | `addDelegate` / `revokeDelegate` (overrides) | SC | VPR rules + registered | as VPR | U2 / revoke | — | st | — |
| SCF-MOBI1-06 | `anchorVehicleKey` | SC | owner, or registering manufacturer once before any transfer; 33/65-byte key | `VehicleKeyAnchored` | anchors the message key | permanent (100-year) attribute | Y (stranger) | D11b fixed `d941ad5` |
| SCF-MOBI1-07 | `changeOwner` (override) | SC | VPR rules; **reverts for a born vehicle** ("use transferVehicleOwnership") | `DIDOwnerChanged` | U1 | ownership history can no longer be bypassed | st | D16 fixed for this part (`bd90004`) |
| SCF-MOBI1-08 | `transferVehicleOwnership(identity, newOwner, odometer, authority)` | SC | `vehicleRegistered`, `onlyOwner` | `VehicleOwnershipTransferred` | U4 | odometer is caller-asserted (LH.3 unbound) | Y | — |
| SCF-MOBI1-09 | getters `getVehicleBirth`, `lookupByVINHash`, `getOwnershipHistory(+Count)`, `vehicleExists`, `getVehicleInfo`, `getVehicleDID`, `validDelegate` | V | — | — | resolve; did:mobi | `0x` in the did:ethr string | — | D10 fixed `65a143f` |

**SCF-MOBI2 — `MOBI/MOBIVIDRegistryV2.sol` (extends MOBI1; MOBI VID II)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Neg. | Dn |
|---|---|---|---|---|---|---|---|---|
| SCF-MOBI2-01 | `authorizeIssuer(issuer, role)` | SC | `onlyRegistryAuthority` | `IssuerAuthorized` | issuer admission | organisational roles registry-wide | Y (outsider, impostor) | D16 part |
| SCF-MOBI2-02 | `revokeIssuerAuthorization` | SC | `onlyRegistryAuthority` | `IssuerAuthorizationRevoked` | issuer revocation | — | N | — |
| SCF-MOBI2-03 | `recordLifecycleEvent(…)` | SC | `vehicleRegistered`, `onlyAuthorizedIssuer(type)`, not revoked; OWNER role must be current owner (K-15) | `LifecycleEventRecorded` | lifecycle credential — M #33 (255,267 gas) | keccak eventId; body off chain, discarded | Y | D16 fixed for OWNER scoping |
| SCF-MOBI2-04 | `attestEvent(eventId, identity, signature)` | SC | role-holder **and** owner or stored `veriKey` delegate; once per attester | `EventAttested` | endorsement — M #28 (198,694 execution gas) | **OZ `ECDSA.recover` (low-s, non-zero)** over EIP-191(keccak(this ‖ chainid ‖ identity ‖ eventId)); chain-bound | Y | D54 fixed (2026-10-17) |
| SCF-MOBI2-05 | getters `isAuthorizedIssuer`, `getVehicleEvents`, `getEvent`, `getEventAttestations`, `getCompleteHistory`, … | V | — | — | status read | — | — | — |

**SCF-CMB — `CVINCombined/CVINCombinedIdentity.sol` (ERC-1056 + ERC-735 hybrid)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Neg. | Dn |
|---|---|---|---|---|---|---|---|---|
| SCF-CMB-01 | `changeOwner` | SC | `onlyIdentityOwner` | `DIDOwnerChanged` | U1 | zero-address semantics | Y | D26 open |
| SCF-CMB-02 | `addDelegate` | SC | `onlyIdentityOwner` | `DIDDelegateChanged` | U2 | — | Y | — |
| SCF-CMB-03 | `revokeDelegate` | SC | `onlyIdentityOwner` | as 02 | revoke delegate | stores a timestamp | N | D22 part (this residue open) |
| SCF-CMB-04 | `setAttribute` | SC | `onlyIdentityOwner` | `DIDAttributeChanged` | U3 — M #34 (51,742) | events | Y | — |
| SCF-CMB-05 | `revokeAttribute` | SC | `onlyIdentityOwner` | as 04 | revoke attribute | — | N | — |
| SCF-CMB-06 | `addClaim(identity, topic, scheme, issuer, sig, data, uri)` | SC | `onlyIdentityOwner`; issuer signature checked at add time | `ClaimAdded`, `DIDClaimChanged(…, previousChange)` | on-chain claim issuance | **raw `ecrecover`** over keccak(this ‖ identity ‖ topic ‖ data); **no low-s guard**; revocation keyed on the content digest, so a high-s copy of a revoked signature is still rejected (test l. 407) | Y | D22 part (low-s open); D25c (scheme) open |
| SCF-CMB-07 | `removeClaim` | SC | identity owner or claim issuer | `ClaimRemoved`, `DIDClaimChanged` | holder-side revoke | does **not** advance `changed`; walk intact | Y | D22 fixed (`65a143f`, `bd90004`) |
| SCF-CMB-08 | `revokeClaimContent(identity, topic, data)` | SC | any caller; records keccak(msg.sender ‖ digest), so only its own issuance | `ClaimRemoved` if present | issuer-side revoke | keccak | Y | — |
| SCF-CMB-09 | getters `identityOwner`, `validDelegate`, `getClaim`, `getClaimIdsByTopic`, `hasValidClaim` | V | — | — | O(1) on-chain claim check (#36) | mapping | — | — |

**SCF-E735 — `ERC735/CVINVehicleClaimHolder.sol` (O6)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-E735-01 | `addClaim(…)` | SC | `onlyOwner`; issuer authorised for topic; VIN attestation encodes the holder's VIN | `ClaimAdded`/`ClaimChanged` | issuance — M #34 create 1,757,881 (incl. deploy) | **EIP-191-prefixed** ecrecover **with** EIP-2 low-s and zero-address guards (l. 500–515) | D25a/b fixed `ad470b6`; D25c open |
| SCF-E735-02 | `removeClaim` | SC | owner or issuer | `ClaimRemoved` | holder revoke | — | — |
| SCF-E735-03 | `revokeClaimContent` | SC | any caller, own issuance only | — | issuer revoke | keccak | — |
| SCF-E735-04 | `authorizeIssuer` / `revokeIssuer` | SC | `onlyOwner` | `IssuerAuthorized` / `IssuerRevoked` | trust list | single owner key | D25a fixed |
| SCF-E735-05 | `transferOwnership` | SC | `onlyOwner` | `OwnershipTransferred` | U4 | — | — |
| SCF-E735-06 | getters `getClaim`, `getClaimIdsByTopic`, `claimExists`, `isAuthorizedIssuer` | V | — | — | verify | — | — |

**SCF-E725B — `ERC725/CVIN_DID_ERC725.sol` (O5)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-E725B-01 | `transferOwnership`, `renounceOwnership` | SC | `msg.sender == _owner` | `OwnershipTransferred` | U4 / lock | `transferOwnership(0)` unguarded | D23 open |
| SCF-E725B-02 | `addKey`, `removeKey` | SC | owner | `KeyAdded`/`KeyRemoved` | key management | dangling `getKeys` entry | D23 open |
| SCF-E725B-03 | `execute(op, to, value, data)` | SC | owner | `Executed` | agent proxy | **stub: performs no call** — not an X1 realisation (use SCF-E725XY-04, R9 PN-23) | D23 open |
| SCF-E725B-04 | `approve(id, bool)` | SC | public no-op | — | — | — | D23 open |
| SCF-E725B-05 | getters `owner`, `getKey`, `getKeys` | V | — | — | resolve | — | — |

**SCF-E725XY — `ERC725xy/CVINVehicleERC725XY.sol` (O6 base); SCF-EXT — `CVINExecuteTarget.sol`**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-E725XY-01 | `transferOwnership`, `renounceOwnership` | SC | `onlyOwner` | `OwnershipTransferred` | U4 | — | — |
| SCF-E725XY-02 | `setData`, `setDataBatch` (payable) | SC | `onlyOwner` | `DataChanged` | U3 (stored) | payable; VIN rewritable | D24 open |
| SCF-E725XY-03 | `setVehicleBirthAttributes` | SC | `onlyOwner` | `DataChanged` | createDID attributes | VIN in storage | D24 open |
| SCF-E725XY-04 | `execute`, `executeBatch` | SC | `onlyOwner` | `Executed`, `ContractCreated` | agent proxy **X1** — M #54 | CALL / STATICCALL / **DELEGATECALL** / CREATE / CREATE2 (l. 216–306); event before call, no state written after (§4.2) | D24 open |
| SCF-E725XY-05 | getters incl. `getVehicleVIN` | V | — | — | resolve | plaintext VIN getter (CA-10) | — |
| SCF-EXT-01 | `setValue`, `willRevert` | SC / pure | none | `ValueSet` | X1 test target | — | — |

**SCF-E1155 — `ERC1155/CVINVehicleCredential1155.sol` (O2)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-E1155-01 | `registerVehicle(vehicle, vin)` | SC | `ISSUER_ROLE` | `VehicleRegistered` | createDID | `_normalizeVIN`; keccak(VIN) | D13 fixed `241642e` |
| SCF-E1155-02 | `issueCredential` | SC | `ISSUER_ROLE` | `CredentialIssued` | issuance | flat issuer role | D8 part |
| SCF-E1155-03 | `revokeCredential` | SC | `ISSUER_ROLE` | `CredentialRevoked` | revocation | any issuer may revoke another's | D8 part (this residue open) |
| SCF-E1155-04 | `issuerTransferCredential` / `issuerTransferIdentity` | SC | `ISSUER_ROLE` | `IdentityRebound` | issuer-mediated U4 | — | D6 fixed `a798370`; D7 fixed `d941ad5` |
| SCF-E1155-05 | `setTokenURI` | SC | `ISSUER_ROLE` | `URI` | metadata | — | D8 fixed (URI event) |
| SCF-E1155-06 | `safeTransferFrom`, `safeBatchTransferFrom` (revert) | pure | — | — | soulbound (G8) | — | D7 fixed |
| SCF-E1155-07 | getters incl. `vinHashOf`, `vehicleForVIN` | V | — | — | verify | **unsalted keccak(VIN)** — enumerable (cf. #60; CA-10) | — |

**SCF-E721N (`ERC721/CVINVehicleNFT.sol`, O3); SCF-E721T (`CVIN_NFT_DID_ERC721.sol`, toll demo); SCF-E721M (`…_Monolithic.sol`)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-E721N-01 | `mintVehicle(…)` | SC | `MANUFACTURER_ROLE` | `VehicleMinted` | createDID — M #3, #29 | VIN normalised | D13 fixed |
| SCF-E721N-02 | `addServiceRecord` | SC | `SERVICE_CENTER_ROLE` | `ServiceRecordAdded` | lifecycle credential | body off chain | — |
| SCF-E721N-03 | `deactivateVehicle` | SC | `DEFAULT_ADMIN_ROLE` | `VehicleDeactivated` | deactivation | advisory, irreversible | D14 open |
| SCF-E721N-04 | `grant…Role` ×3 | SC | `DEFAULT_ADMIN_ROLE` | `RoleGranted` | governance | inspector role gates nothing | D14 open |
| SCF-E721N-05 | `_update` hook and standard transfers | SC | owner / approved | `Transfer`, `VehicleTransferred` | U4 | history kept | — |
| SCF-E721N-06 | getters incl. `getVINFromTokenId` | V | — | — | resolve | plaintext VIN getters (CA-10) | — |
| SCF-E721T-01 | `mint(to, id, uri)` | SC | `onlyOwner` | `Transfer` | createDID (demo) | — | — |
| SCF-E721T-02 | `recordEntry(id, ts)` | SC | `onlyOwner` | `EntryRecorded` | toll scenario | operator-asserted timestamp | — |
| SCF-E721T-03 | `payToll(id)` (payable) | SC | token owner (`ownerOf(id) == msg.sender`, l. 72) | `TollPaid` | payment IDTx-like | value `call` to the contract owner; no state after the call (§4.2) | D9 fixed `d941ad5` |
| SCF-E721M-01 | `mint`, `approve`, `setApprovalForAll`, `transferFrom`, `safeTransferFrom` ×2 | SC | ERC-721 rules; `onlyOwner` for mint | `Transfer`, `Approval`, `ApprovalForAll` | hand-written baseline | `_checkOnERC721Received` after the state update (§4.2) | D2 fixed `708302a` |
| SCF-E721M-02 | getters | V | — | — | — | — | — |

**SCF-LSP8 — `LSP8/CVINVehicleLSP8.sol`**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-LSP8-01 | `mintVehicle(owner, vin)` | SC | `onlyOwner` | `Transfer`, `VehicleMinted` | createDID; tokenId = keccak(normalised VIN) | **unsalted, enumerable** (CA-10) | D13 fixed |
| SCF-LSP8-02 | `transfer(…)` | SC | owner / operator | `Transfer` | U4 | no LSP1 probing | D12 part (open) |
| SCF-LSP8-03 | `revokeVehicle` | SC | collection owner or token owner | `Transfer` to 0, `VehicleRevoked` | deactivation | generation counter | D12 fixed for re-mint (`bd90004`) |
| SCF-LSP8-04 | `setDataForTokenId`, `setDataBatchForTokenIds` | SC | `onlyOwner` | `TokenIdDataChanged` | attributes | VIN key overwritable | D12 part (open) |
| SCF-LSP8-05 | `transferOwnership` | SC | `onlyOwner` | `OwnershipTransferred` | governance | — | — |
| SCF-LSP8-06 | getters incl. `tokenIdForVIN` | V | — | — | resolve | — | — |

**SCF-E4337A — `ERC4337/CVINVehicleAccount.sol`; SCF-E4337EP — `CVINMinimalEntryPoint.sol` (O7, minimal)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Neg. | Dn |
|---|---|---|---|---|---|---|---|---|
| SCF-E4337A-01 | `validateUserOp` | SC | `msg.sender == entryPoint` | — | UserOp authentication | **raw ecrecover over EIP-191(userOpHash)**; rejects zero address; no low-s guard (l. 152–168); prefund `call` only if `missingAccountFunds > 0` (always 0 here) | Y | — |
| SCF-E4337A-02 | `execute(target, value, data)` | SC | `onlyOwnerOrEntryPoint` | `Executed` | agent proxy X1 | single `call`, no state after (§4.2) | Y | — |
| SCF-E4337A-03 | `transferOwnership` | SC | `onlyOwnerOrEntryPoint`; zero owner rejected | `OwnershipTransferred` | U1/U4 | — | Y | — |
| SCF-E4337A-04 | `setGuardian` | SC | `onlyOwnerOrEntryPoint` | `GuardianChanged` | recovery setup (I9) | — | Y | — |
| SCF-E4337A-05 | `recoverOwner` | SC | guardian only; **no time-lock, no threshold** | `OwnerRecovered` | social recovery | guardian persists as super-owner; R4 `PF-30` | Y | D15 open |
| SCF-E4337A-06 | `setAttribute` / `getAttribute` | SC / V | `onlyOwnerOrEntryPoint` | `AttributeChanged` | U3 — M #34 (94,651) | storage | Y | — |
| SCF-E4337EP-01 | `handleOp(userOp)` | SC | anyone; nonce must match | `UserOperationHandled` | UserOp execution — M #25 (+46,830/op), #50 (+47,116) | userOpHash = keccak(packed ‖ entryPoint ‖ **chainid**); nonce written before validation and call (l. 71–72); an inner revert reverts the whole op, nonce included | — | D15 open (documented harness property) |
| SCF-E4337EP-02 | `getUserOpHash`, `nonces` | V | — | — | — | keccak | — | — |

**SCF-IDC / SCF-IDTX — `phase2/idtx/contracts/IdtxExecutor.sol` (SOL-10)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-IDC-01 | `setCommitment(identity, key, commitment, until)` | SC | `registry.identityOwner(identity) == msg.sender` | `CommitmentSet` | Commitment dependency source | reads SCF-EDR-01; chain time | — |
| SCF-IDC-02 | `revokeCommitment` | SC | identity owner | `CommitmentRevoked` | revocation | — | — |
| SCF-IDC-03 | `valueOf(identity, key)` | V | — | — | zero if expired or setter no longer owner (AR-6) | chain time; SCF-EDR-01 | — |
| SCF-IDTX-01 | `holds(dep)` | V | — | — | identity predicate (Owner / Delegate / Commitment); **independent of msg.sender** (AR-4) | SCF-EDR-01/02, SCF-IDC-03 | — |
| SCF-IDTX-02 | `execute(dep, action)` | SC | anyone; requires `holds` | `Executed` | same-transaction IDTx | atomicity | — |
| SCF-IDTX-03 | `createIntent(dep, action, deadline)` | SC | anyone | `IntentCreated` | next-transaction IDTx, step 1 | chain time | — |
| SCF-IDTX-04 | `fulfil(id)` | SC | anyone (keeper); re-evaluates `holds` | `IntentFulfilled`, `Executed` | step 2 | no TOCTOU on chain; keeper liveness off chain | — |
| SCF-IDTX-05 | `intentCount()` | V | — | — | — | — | — |

**SCF-G16, SCF-ZKG, SCF-SCH — `5_zkp-agent-identity/contracts/` (SOL-11)**

| Tag | Function | SC/V | Access control | Events | Role | Notes | Dn |
|---|---|---|---|---|---|---|---|
| SCF-G16-01 | `verifyProof(pA, pB, pC, pubSignals[7])` | V | — | — | Groth16 verification (snarkjs-generated) | PRO-18; `checkField`; verification key from an **insecure single-party setup** | — (CA-06) |
| SCF-ZKG-01 | `anchorCommitment(identity, commitment)` | SC | identity's ERC-1056 owner | `CommitmentAnchored` | issuer-free anchor — M #58 (51,558) | Poseidon value | — |
| SCF-ZKG-02 | `setService(serviceId, scope, minYear, region, challenge)` | SC | `governor` | `ServiceSet` | verifier policy | single governor key; static challenge | — (CA-12) |
| SCF-ZKG-03 | `admit(identity, serviceId, a, b, c, pub, action)` | SC | anyone with a valid proof; signals match anchor, `mfrRoot`, service; nullifier unused | `Admitted` | IDTx with knowledge-of-opening dependency — M #58 (301,163) | SCF-G16-01; nullifier map | — |
| SCF-ZKG-04 | getters | V | — | — | — | — | — |
| SCF-SCH-01 | `verify(parity, px, message, e, s)` | pure | — | — | Schnorr PoK check | ALG-15 via PRO-16 | — |
| SCF-SCH-02 | `prove(…)` | SC | anyone | `Proved` | on-chain PoK record — M #58 (28,775) | no replay guard | — (CA-13) |

**Register summary.** 22 prefixes, 117 rows (each grouped getter row counted once; R9 verified the count). Signature schemes across the nine signature-verifying contracts are **three**: raw-digest `ecrecover` (EDR, CMB), EIP-191-prefixed `ecrecover` (E735, E4337A), and OpenZeppelin ECDSA with chain id (MOBI2). Only MOBI2's `attestEvent` and the 4337 EntryPoint bind `block.chainid`. Low-s is enforced by E735 (explicit guard) and MOBI2 (OZ) only; zero-address recovery is rejected by E735, E4337A and MOBI2, not by EDR or CMB (D53; R9 CA-03). R9 SLD-06 locks this inventory.

**Access-control cross-check (44 rows).** Negative tests exist for **24** of the 44 state-changing rows on EDR, VPR, MOBI1, MOBI2, CMB and E4337A; **9** have only state-gating negatives (the revoked/registered gates added by the D21 fix, `ERC1056Registry.regression.test.js` l. 142–167, and the born-vehicle `changeOwner` revert); **11** have none: SCF-EDR-04, -06, -07, -08, -12; SCF-MOBI1-01, -02, -03; SCF-MOBI2-02; SCF-CMB-03, -05. In every one of the 20 the access check is present in source; the gap is test evidence, not code. Logged as **Q-R6-07** and offered to R7 PF-61(a) and the security campaign (R9 SLD-16). Status of this check: source-read, I (not executed in this pass).

#### L5.3 Transaction formats

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| PRO-21 | Legacy tx with **EIP-155** chain id | outer-tx replay protection | ALG-02 | every SC call | M as condition (`build_transaction` with `gasPrice`; eth_account adds chain id) | `erc1056_provider.py` `_send_tx` | — |
| PRO-21a | EIP-2930 (type 1) | access lists | as above | gas optimisation | — | — | — |
| PRO-21b | EIP-1559 (type 2) | base fee / tip | as above | Option B/C | I (ethers v6 default where supported; not recorded separately) | — | — |
| PRO-21c | EIP-4844 (type 3) | blobs | KZG | Option B anchoring | — | — | — |
| PRO-21d | EIP-7702 (type 4) | EOA delegates to code (O8) | ALG-02 | O8 | — | — | — |
| PRO-22 | ERC-4337 UserOperation | account-abstraction intent | SCF-E4337A-01 | O7 relayed path | M (#25, #34, #50) with a **minimal** EntryPoint (no bundler, paymaster or prefund) | `ERC4337/` | D15 open |
| PRO-22a | ERC-1056 signed meta-transaction (`*Signed`) | in-contract relayed write | SCF-EDR-04 digest | U5 | M (#50) | `EthereumDIDRegistry.sol` | D52 doc |
| PRO-22b | EIP-191 personal-sign / EIP-712 typed data | off-chain message signing | ALG-02 | VC proofs, attestations | EIP-191: I; EIP-712: — | `vc_issuer.py`; `MOBIVIDRegistryV2.sol` | — |

↑ see L6 (every DID method and IDTX function is an L5.2 call or read). ↓ see L5.1 (`ecrecover`, precompiles), L4.2 (who holds the role keys), L3 (ordering; EIP-155 chain id), L2.1 (where state and logs live). R7: PF-49 (per-function capacity), PF-51 (Groth16), PF-52 (storage vs log), PF-61 (contract security vector; the cross-check above feeds (a)). R8: RV-SC-01..20, RV-SCF-01..42, RV-TX-01..15, RV-THR-08, RV-THR-11/12 (D52/D53, R8 v0-2). R9: PRM-L5.2-01..06; B-02, B-04, B-07, B-10.

---
### L6 — Identity

> **Does for above:** answers the thesis's questions — *which key speaks for this vehicle now* (I1, I3), *what has an issuer said* (I5), *can it be shown without showing everything* (I6) — through a resolver, an offline-checkable credential, and functions whose effect depends on identity state (IDTX). **Trusts below:** L5.2 registries for authoritative state, L0.4 for reading it, L1 for every signature. **Remember:** did:ethr resolution fails closed on *errors*, not on *lies*: it trusts the RPC endpoint (R9 NC-06).

did:ethr resolution reads the registry when given a provider (WM-2 C1), fails closed on RPC error and passes 335/336 of the W3C DID suite (#24). The VC layer declares its deviation (thesis cryptosuite, deterministic JSON, `vc_issuer.py` l. 12–14). No AnonCreds, BBS+, mDL or did:indy code exists.

#### L6.1 DID methods

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| ALG-23 | **did:ethr** resolution (ERC-1056 event replay) | start at `changed[identity]`, walk `previousChange` via `eth_getLogs`, replay forward; fail closed | SCF-EDR-01/02, IMP-L2.1-02/04; PRO-13; chain time for `validTo` | L7 verifiers; issuer-key lookup | M: #24 (335/336), #31/#51 (14 → 32 → 112 RPC calls at h = 1/10/50; median 91.113 ms at h = 50 in-process), #21 (15.513 ms uncached verify, testbed variant on VPR) | `did_resolver.py`; `erc1056_provider.py`; JS `ethr-did-resolver ^10.1.0` | D51 fixed; D63 doc |
| ALG-23a | did:ethr **offline synthesis** | document from the DID string alone; marked `cvinResolutionMode: "offline-synthesized"` | nothing on chain (key = address) | M0 hot path | I (default mode) | `did_resolver.py` header | — |
| ALG-24 | **did:mobi** resolution | `did:mobi:<salted VIN hash>` → `lookupByVINHash` → `getVehicleDID` → ERC-1056 state | SCF-MOBI1-09; VPR state | MOBI scenarios | I (`cvinResolutionMode: "mobi-vid-registry"`) | same | D10 fixed |
| ALG-24a | did:nft, did:key, did:web | resolver branches | contract reads or synthesis | comparison breadth | I | `did_resolver.py` l. 12–15, 59 | — |
| IMP-L6.1-01 | did:indy / Indy-Besu (O10/O11) | purpose-built registry | RBFT / QBFT | SOL-07 | — | — | — |
| IMP-L6.1-02 | CAIP-10 `blockchainAccountId` | chain-qualified account | spec | interop | I; decimal chain reference since the merge | `did_resolver.py` | D27 fixed (`bd90004`) |

#### L6.2 Credential formats

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L6.2-01 | W3C VC Data Model **v2.0** with `DataIntegrityProof`, cryptosuite `eip191-secp256k1-recovery-2024` (thesis-defined) | issuer signs deterministic JSON with EIP-191; verifier recovers the address offline | ALG-03, PRO-22b; ALG-23 for the issuer key | issuance/verification; V2V warm verify | M: #4 (internal checker 94.3 %), #27 (warm 0.142 ms [0.141, 0.143]), #55 | `vc_issuer.py`, `vc_verifier.py`, `vc_holder.py` | D30 fixed |
| IMP-L6.2-02 | SD-JWT-style salted claim digests | holder discloses subsets | ALG-08 salts | createPresentation (off-chain) | I | `vc_issuer.py` header | — |
| IMP-L6.2-03 | VC-JWT / JOSE (`did-jwt` 0.1.0) | JWT envelope | T-I09 | interop | — (dependency listed only) | `requirements.txt` | — |
| IMP-L6.2-04 | JSON-LD URDNA2015 (`pyld==2.0.3`) | RDF canonicalisation | spec | full conformance | — (**documented deviation**) | `vc_issuer.py` l. 12–14 | — |
| IMP-L6.2-05 | MOBI VID birth and lifecycle payloads | VID I/II; hash on chain, body off | SCF-MOBI1-04, SCF-MOBI2-03 | MOBI scenarios | I | `2_w3c-ssi-layer/mobi-vid/` | — |
| IMP-L6.2-06 | ZK-VIN commitment credential (Poseidon(VIN, year, region, salt)) | presentation = Groth16 proof | ALG-09, ALG-12 | SOL-11 | M (#56–#58) | `5_zkp-agent-identity/` | — |
| IMP-L6.2-07 | AnonCreds, BBS+ Data Integrity, ISO mDL | anonymous or device-bound credentials | ALG-16; COSE | I6/I7 at native strength | — | — | — |

#### L6.3 IDTX functions

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L6.3-01 | IMinimalSSI F1–F12 (Set A / Set B) across the ten harness adapters | the basic digital-ID set | the adapters' contracts | admission and comparison | M: #53 (Set A 11/11 or 10/11 by substrate), #54 (P1 createPresentation and X1 execute gas; X1 only on 725xy and 4337) | `BASIC_ID_SET_EXTENSION.md`; `adapters.conformance.test.js` | D23 open (725 basic X1 stub) |
| IMP-L6.3-02 | **IdtxExecutor** + IdentityCommitments (SOL-10) | Owner / Delegate / Commitment dependency; same-tx `execute`; next-tx `createIntent`/`fulfil` | SCF-EDR-01/02; SCF-IDC-03; chain time | tolls, insurance, keeper actions | **I** (compiled under `hardhat.phase2.config.js`; "No number from this prototype is a result", source header; R9 DRP-05) | `phase2/idtx/contracts/IdtxExecutor.sol` | — |
| IMP-L6.3-03 | **ZkVinGate.admit** (SOL-11) | IDTx whose dependency is knowledge of a commitment opening; per-scope nullifier | SCF-G16-01; SCF-ZKG-01 | privacy-preserving admission | M (#58) | `ZkVinGate.sol` | — |
| IMP-L6.3-04 | MOBI V2 `attestEvent` as co-signed endorsement | owner-consented, chain-bound attestation | SCF-MOBI2-04 | lifecycle trust | M (#28) | `MOBIVIDRegistryV2.sol` | D54 fixed |

↑ see L7 (verifiers and agents consume resolution and credentials). ↓ see L5.2 (EDR/VPR/MOBI state), L0.4 (unproven reads), L1 (signatures, hashes, Groth16). R7: PF-34 (hiding iff salted), PF-36 (composition lemma; gated on a blind re-derivation, R9 SLD-10), PF-54/55 (state freshness, *k_f*\*), PF-62 (privacy *k_A*, ℓ). R8: RV-IDTX-01..28, RV-VC-01..19, RV-READ-01..04, RV-ALG-04. R9: PRM-L6.1-01..03, PRM-L6.2-01..03, PRM-L6.3-01..03; B-01, B-11..15.

---

### L7 — Application and identity-to-identity communication

> **Does for above:** the safety and service applications get one decision — *accept this message from this sender now, or not* — within a budget (50 ms of the 100 ms BSM interval, `docs/LATENCY_BUDGET.md` §1, a project choice from SAE J2945/1 cadence, PRO-24). **Trusts below:** L6 for keys and status, L1 for signatures and, hidden, LH.4 for the clock its freshness rule compares against. **Remember:** the repository signs JSON, not ASN.1. Its messages cost 2.9× to 5.0× the airtime of a compact 1609.2 digest-signed BSM (R7 PF-44 from measured sizes #23; R9 SLD-04, NC-10). On the cached path, the bottleneck is OBU verification and airtime, not the ledger (R9 SLD-03).

L7 is a set of Python providers and simulators carrying a DID or a PEM certificate, not a 1609.2 `SignedData`. Within that frame it is rigorous (signed generation time, bounded replay cache, verifier v3, pre-registered gates I1–I5, #44–#48). Two things must be kept apart (R7 §6; R9 PN-24): *message freshness* (age window and replay cache, `freshness.py`) and *state freshness* (how stale the cached identity state may be, `ERC1056Provider.set_refresh_every` and `_probe_identity_info`, `erc1056_provider.py` l. 146, 257). The first is bounded in seconds; the second in messages (≤ *k_f* − 1, #46), and not in time at all, because the state cache has no TTL (BP-L7.2-03).

#### L7.1 Wallet and agent software

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L7.1-01 | ethers v6 / Hardhat ethers | JS wallet and contract client | IMP-L1.2-04 | harness and tests (562 Hardhat tests per `STATUS_2026-10-22.md` §5 addendum; the §1.1 table's 541 is the earlier full run) | M as condition | `1_blockchain-identity/` | — |
| IMP-L7.1-02 | web3.py 6.x + eth-account | Python client | IMP-L1.2-03 | providers; MOBI client (376 Python tests, same §5 addendum) | M as condition | `requirements.txt` (`web3==6.11.0`) | — |
| IMP-L7.1-03 | ethr-did + ethr-did-resolver (JS) | DID tooling | ALG-23 | conformance | I (dependency) | `package.json` | — |
| IMP-L7.1-04 | Identity providers: `erc1056_provider`, `mobi_vid_provider`, `centralized_provider`, `pki_identity`, `lifecycle_backends`, `comparison_framework` | sign/verify/register/revoke per substrate | the L6/L5 layers per provider | every testbed row (#21, #32, #33, #37) | M | `cv2x-testbed/identity/` | D4, D5 fixed `1d4ad07`; D11 fixed; D51 fixed; D63 doc; D64 open |
| IMP-L7.1-05 | **Steward** agent (vault, policy, compiler, kernel, leakage audit, learner, delegation, audit log) | wraps the identity; signed policy; proofs; leakage bound | IMP-L1.2-09; ALG-14; vault without value getter | SOL-14 | M in Sim (#61; README "≤ 3.0 bits on 90/90 runs", Sim) | `steward/` | — |
| IMP-L7.1-06 | Veramo, ACA-Py, Credo-TS (O17) | full SSI agents | DIDComm, AnonCreds | SOL-07 | — | — | — |

#### L7.2 Messaging protocols

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L7.2-01 | **Freshness module** (`signed_bytes`, `max_age_s` 1.0 s / `max_future_s` 0.1 s, bounded replay cache) | *message* freshness: generation time inside the signature; age window; duplicate rejection | ALG-08; **the receiver's clock** (HW-10 by assumption); IMP-L2.3-06 | req. R8 for every provider | M (#21 same policy for all verifiers; #45 I2 replay 30/30) | `freshness.py` l. 30–63 | D29 fixed |
| IMP-L7.2-02 | JSON-signed BSM / SPaT (SSI: DID + secp256k1/SHA-256; PKI: PEM cert + P-256) | the testbed's secured message | ALG-04 / ALG-05; IMP-L7.2-01 | V2V and RSU scenarios | M: #23 (596 B DID-carrying vs 1,078–1,110 B PEM-carrying), #27, #44–#48 | `cv2x_stack.py`; `sumo/infrastructure_layer.py` | — |
| IMP-L7.2-03 | **Verifier v3** (infrastructure layer) | field binding, per-receiver replay, warm-path expiry, size/depth limits, DID method/chain check | IMP-L7.2-01 | infrastructure trust | M (#44–#48) | `infrastructure_layer.py` | D28–D31 fixed `f1f9e37`; D37–D39, D41, D42 fixed (2026-10-14); D40 doc |
| IMP-L7.2-04 | **State refresh every *k_f*** with one-call probe (`set_refresh_every`, `_probe_identity_info`) — *state* freshness | re-check identity every *k*-th message via `getIdentityInfo`; full resolution only on change; **no TTL** | SCF-VPR-01; PRO-13 | bounded staleness in messages | M (#32 knee *k* ≈ 90 for *P*\*(0.5) = 100; #37 probe 3.222 ms; #46 "at most k − 1 further SPaT") | `erc1056_provider.py` l. 123, 146, 257 | D39 fixed; D63 doc |
| PRO-12 | IEEE 1609.2 secured messages (`SignedData`, implicit/explicit certificates, SCMS butterfly keys) | deployed V2X security envelope | ALG-05; HW-03; SCMS (T-I05) | the incumbent L6/L7 | Ds: the repo's pseudonym certificates are X.509 P-256 in JSON (KD-R6-03); "this repository has no IEEE 1609.2 security-profile text to quote" (`freshness.py`) | `pki_identity.py`; `sumo_identity_integration.py` l. 8, 209 | — |
| PRO-12a | ETSI TS 103 097 / TS 102 941 | European V2X security | as PRO-12 | — | — (named only) | `pki_identity.py` docstring | — |
| **PRO-23** (~~PRO-13x~~) | SAE J2735 BSM, SPaT (UPER ASN.1) | message set | none intrinsic | safety apps | I: **J2735-like** dataclasses serialised as JSON; `MessageType` also lists CAM, DENM, CPM, MCM | `cv2x_stack.py` l. 18–100 | — |
| **PRO-24** (~~PRO-13y~~) | SAE J2945/1 (10 Hz, congestion control) | on-board requirements | — | the 100 ms interval of the budget | S (source of the budget) | `LATENCY_BUDGET.md` §1 | — |
| **PRO-25** (~~PRO-13z~~) | DIDComm v2 (O16) | DID-authenticated encrypted messaging | JOSE, X25519/Ed25519 | I2I channel | — (no code) | — | — |

IMP-L7.2-04 (new) tags the code behind SOL-16 so R8 can anchor state freshness to the right module (PN-24).

#### L7.3 Application scenarios

| Tag | Component | What it does | Secured by | Enables above | St | Repo | Dn |
|---|---|---|---|---|---|---|---|
| IMP-L7.3-01 | SUMO highway-intersection scenario; TraCI; `--simulate` mobility | V2V identity under mobility | IMP-L7.2-02 | V2V latency, saturation | M: #27 (in `--simulate`: "simulated mobility, real identity crypto"); SUMO-binary runs not run (#15 E; "50 vehicles" dropped, R9 DRP-06) | `cv2x-testbed/sumo/` | — |
| IMP-L7.3-02 | RSU / TMC infrastructure (SPaT from credentialed RSUs) | infrastructure trust | IMP-L7.2-03 | I1–I5 gates | M (#44–#48) | `infrastructure_layer.py`, `run_infra_stats.py` | — |
| IMP-L7.3-03 | MOBI VID lifecycle (17 events), M4 parity | vehicle life on chain | SCF-MOBI1/2 | lifecycle cost | M (#30, #33, #35) | harness L2; `lifecycle_parity.*` | D60 open (#33 re-statement) |
| IMP-L7.3-04 | M5 pseudonym pool (20 `addDelegate` per 5-min epoch) | rotating pseudonyms as ERC-1056 delegates | SCF-EDR-05 | intended req. R5 unlinkability | M (#38: 1,113,456 gas first epoch; **60 of 60 pseudonyms linked by one `eth_getLogs`** — a negative result) | `PseudonymPool.test.js`; register #38 | — (R9 CA-11 proposes a design defect) |
| IMP-L7.3-05 | Toll entry and payment | NFT entry record + payable toll | SCF-E721T-02/03 | tolling | I (tests only) | `CVIN_NFT_DID_ERC721.sol` | D9 fixed |
| IMP-L7.3-06 | ZK admission (full-circle demo) | prove year / region / manufacturer without the VIN | SOL-11, SOL-14 | privacy-preserving services | M (#56–#62) | `demos/full_circle_demo.py` | — |
| IMP-L7.3-07 | ns-3 C-V2X simulation | packet-level radio | — | L0 realism | Ds (compose service only) | `docker-compose.yml` | — |

↑ nothing above: L7 is where the thesis's claims are made. ↓ see L6 (resolution, credentials), L1 (ALG-04/05), L0.1 (airtime), LH.4 (clock). R7: PF-43 (verify load ρ_v = *P*·*r_BSM*·*t_ver*; the "ledger is not the bottleneck" condition is *k_f* ≥ *r_BSM*·*P*·*t_chain*/*f_id*, 27.9 at *P* = 100, R7 §4.2; R9 PN-11 closed), PF-44 (airtime), PF-47 (clock), PF-53 (cache), PF-54..56 (state freshness). R8: RV-PROT-08..13, RV-SIG-10..14, RV-ALG-09..12, RV-SCN-01..13, RV-THR-03/04/14, RV-PROT-16 (encoding size, R8 v0-2). R9: PRM-L7.2-01/02; B-08, B-16.

---

## 3. Mapping: the repository's "nine standards" vs O1–O17 and Families A–F

The repository compares **nine standards** in ten harness columns (README l. 225; #34): ERC-1056 (pure and wrapper), ERC-721, ERC-725, ERC-725xy, ERC-735, ERC-1155, ERC-4337, LSP8 and CVIN-Combined, with MOBI VID V2 as an application profile. The option list O1–O18 and Families A–F come from Phase 1 R2 §3.3, which quotes the Terminology Freeze. R9 PN-22 confirms it against R2 l. 115–119 as the reference for R8 v0-2. The Freeze itself was not re-read (Q-R6-01 open).

| Repo column (harness / SCF prefix) | Project option | Family | Match quality | Note |
|---|---|---|---|---|
| ERC-1056 pure (SCF-EDR) | **O1** ERC-1056 | A | exact | the canon's only 12/12 baseline (BASIC_ID_SET §1) |
| ERC-1056 wrapper (SCF-CVDR) | O1 (application profile) | A | sub-option | K-5 |
| ERC-1056 vehicle profile (SCF-VPR) | O1 variant | A | sub-option, **not** byte-faithful | explicit creation, terminal revocation, no `*Signed` |
| ERC-1155 (SCF-E1155) | **O2** | A | exact | — |
| ERC-721 (SCF-E721N; E721T, E721M auxiliary) | **O3** ERC-721 soulbound | B | close (E721N allows transfers; only 1155 is soulbound) | — |
| — | O4 ERC-6551 | B | **absent** | — |
| ERC-725 basic (SCF-E725B) | **O5** | C | exact, with the D23 stub | — |
| ERC-725xy (SCF-E725XY) + ERC-735 (SCF-E735) | **O6** ERC-725xy + unmerged ERC-735 | C | split into two columns | — |
| ERC-4337 (SCF-E4337A/EP) | **O7** | C | minimal (no bundler/paymaster) | — |
| — | O8 EIP-7702 | C | **absent** | — |
| — (Steward is nearest) | O9 ERC-8004 | D | absent as a contract | — |
| LSP8 (SCF-LSP8) | **none** | — | repo-only | possible addition (Q-R6-02) |
| CVIN-Combined (SCF-CMB) | O6 + O1 composite; a precursor of **O18** | F (precursor) | repo-only | the thesis's own hybrid |
| MOBI VID I/II (SCF-MOBI1/2) | application profile over O1 | A + application | repo-only | MOBI standard, not an ERC |
| ZK-VIN (SCF-G16/ZKG/SCH) | adjacent to **O15** Paladin's on-chain Groth16 idea | E (adjacent) | repo-only | plain EVM |
| IdtxExecutor (SCF-IDTX) | none | — | repo-only | I-24; prior art ERC-3643 (STATUS §3 item 6) |
| — | O10 Indy, O11 Indy-Besu, O12 AnonCreds, O13 Identus, O14 CREDEBL, O16 DIDComm v2, O17 ACA-Py/Credo | E | **absent from code** | Family E exists only in documents |

The repository *measures* Families A–C and a Family-F precursor, *adds* four artefacts the option list lacks (LSP8, CVIN-Combined, MOBI profile, ZK-VIN/IDTX) and *executes nothing* from Families D or E. A sentence that ranks Family E against A–C on measured data has no row to cite.

---

## 4. New breaking points at the deeper levels

Columns follow R3 Part II. **Bound** carries an R7 tag (PF-63..66 included) or "qualitative" (§8; PN-03).

### 4.1 Register

| Tag | Attack / failure | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-LH-01 | **Weak or predictable RNG on an ECU/OBU** (boot-time starvation, RDRAND-only trust, DRBG flaw) | key or nonce drawn before the pool is seeded; no RFC 6979 | `BP-L1-01/02` on the vehicle: key recoverable, every write and BSM forgeable | RFC 6979 (ALG-02); SE-internal keygen (HW-06); health tests — all Ds | PF-41, PF-42 |
| BP-LH-02 | **Test-key derivation leaks into a deployment**: controller key = SHA-256(vehicle_id) | IMP-LH.1-02 reused outside the testbed | anyone who knows a vehicle id rotates or revokes its identity (G1, G8 fail) | INSECURE label in source; deployment guard open (CA-18) | **PF-63** (κ = H(vehicle_id | adversary's knowledge): 0 bits if the id is public, 19.93 bits for a VIN with unknown serial; R7 §7.1) |
| BP-LH-03 | **TEE/SE side channel or fault** | co-located or physical attacker | `BP-L1-07` against the Steward vault or wallet SE; `zkid` not constant time | constant-time libs (IMP-L1.2-02); keep `zkid` out of production — open | R4 `PF-12` (reuse) |
| BP-LH-04 | **GNSS spoofing / meaconing → time** | civil GNSS unauthenticated; clock GNSS-disciplined | the freshness window accepts replays shifted by the spoofed offset; `max_future_s` = 0.1 s is the only guard; PC5 sync degraded | holdover oscillator, multi-source time, OSNMA — Ds | PF-47 (items 1, 4) |
| BP-LH-05 | **GNSS spoofing → position** | as above | an authentic vehicle broadcasts a false position (misbehaviour, not forgery) | misbehaviour detection — out of scope | qualitative |
| BP-LH-06 | **Host compromise of the RPC/resolver node** | Plane V or the testbed RPC host owned | every read is a lie the verifier cannot detect | `eth_getProof` against a trusted header — not used | **PF-64** (P(accept false read) 1.0×10⁻³ with one endpoint at *p_lie* = 10⁻³, 3.00×10⁻⁶ for 2-of-3 independent endpoints; R7 §7.1) |
| BP-L0.1-01 | **Sidelink congestion / jamming** | high CBR; SPS collisions | BSMs lost; Tier-1 deadline missed (`BP-L7-07`) | J2945/1 congestion control — modelled only (`ResourcePool.update_cbr`) | PF-44 (capacity); PF-46 (P_loss bracket vs load, e.g. [0.034, 0.190] for digest BSMs at *n* = 100, CBR 0.20; R7 §4.5) |
| **BP-L0.1-02** (new) | **RF-layer pseudonym linkability through SPS resource persistence** | a vehicle changes pseudonym but keeps its semi-persistent resource (counter *C* not expired, or kept with *P_keep*) | an observer of the sidelink links old and new pseudonyms by the resource they occupy: req. R5 fails at L0.1 even if L6 is unlinkable | force resource reselection at every pseudonym change — open; `cv2x_stack.py` has no reselection counter (Q-R7-04) | **PF-45** (0.136 / 0.449 / 0.805 by *P_keep*; R7 §4.4) |
| BP-L0.2-01 | **Revocation over intermittent backhaul** | verifier offline for *T_off* | W grows by *T_off*; status cannot refresh; the probe cannot run | bounded-staleness cache and fail-closed policy per tier — Ds | PF-48 |
| BP-L0.3-01 | **Eclipse via discv4** | public discovery on a consortium node | stale state fed to the node | static nodes + permissioning (IMP-L0.3-01) — Ds | qualitative (no P2P in repo) |
| BP-L0.4-01 | **JSON-RPC exposure** (`eth_sendRawTransaction`, `debug_*`, `admin_*` on 0.0.0.0) | RPC bound publicly (compose maps `8545:8545`, l. 74) | DoS, inspection, unlocked-account abuse | loopback binding, auth proxy, method allowlist — open (CA-18) | qualitative |
| BP-L0.4-02 | **Unproven RPC responses** | a verifier uses PRO-13 for did:ethr | a lying or stale endpoint returns a rotated-out key or hides `DIDRevoked`; resolution fails closed on errors only | proof-carrying reads or independent endpoints — open (R9 B-12, NC-06) | **PF-64** (1.0×10⁻³ single endpoint; R7 §7.1) |
| BP-L0.4-03 | **Chain-id confusion at the client** | verifier trusts `eth_chainId` | a DID resolved against another chain's same-address registry (compounds D52) | verifier v3 checks method and chain (D41 fixed) — closed for the infrastructure path | qualitative |
| BP-L1.1-01 | **Signature-scheme inconsistency** (raw / EIP-191 / OZ) | one issuer, two contracts | a signature valid or invalid depending on target; raw-digest schemes accept a signature over any 32-byte value the signer ever signed raw | one scheme (EIP-191/EIP-712) — author decision (D25c; R9 B-03, CA-04) | qualitative |
| BP-L1.1-02 | **Missing low-s check on raw `ecrecover`** (EDR, CMB, E4337A) | caller supplies (r, n − s) | a second valid signature; replay keyed on signature bytes would miss it | EDR uses a nonce (safe); CMB keys revocation on the content digest (safe, test l. 407); E4337EP nonce (safe); open as hygiene (D22 rest) | qualitative |
| BP-L1.2-01 | **secp256k1 library divergence** (six implementations) | a bug in one | verifier and contract disagree | differential tests — partial (security suite runs EVM vs ethers) | qualitative |
| BP-L1.2-02 | **Precompile / curve bug in a client** (bn256; `ecrecover` r = 0) | client defect (L3.2) | false Groth16 acceptance or D53-class zero-address recovery | client diversity; `recovered != 0` guards — partial (OZ path, E735, E4337A only) | PF-60 (HHI; partial) |
| BP-L1.2-03 | **Circom under-constraint** | circuit author error | a false statement satisfies the R1CS; `admit` accepts | range checks and booleanity read in source; five false statements rejected (`prove_and_verify.js`, #57) — **no formal under-constraint audit** | qualitative; audit status in PF-61(e) |
| BP-L1.2-04 | **Insecure Groth16 setup in use** (single-party, fixed entropy) | the committed zkey reused beyond research | whoever holds the toxic waste forges any ZK-VIN proof | multi-party ceremony — open (CA-06; R9 NC-04) | PF-35; R4 `PF-11` with *t_s* = 1 |
| BP-L1.2-05 | **Challenge bound only by `challengeSquared`**; static per-service challenge | `setService` stores one challenge per service | proofs replayable within a service until the nullifier is spent; nullifier makes admission one-shot per scope | nullifier (SCF-ZKG-03) — partial (CA-12) | qualitative |
| BP-L2.1-01 | **Event-only state cannot be read on chain** | a contract needs an ERC-1056 attribute value | IDTX needs a commitment store (#49) | IdentityCommitments (SCF-IDC) — closed by design | qualitative |
| BP-L2.1-02 | **Linked-list severance** (historical) | was: `revokeIdentity` without `previousChange` (D21) and claim ops advancing `changed` (D22) | resolver missed history | **historical; closed** by D21 (`65a143f`) and D22 (`65a143f`, `bd90004`). Open residue on this list: none. Adjacent open residues: `updateVehicleKey` adds without revoking (D21 rest); CMB `revokeDelegate` timestamp, no low-s, no identity-level revocation (D22 rest) | qualitative |
| BP-L2.2-01 | **Log pruning / storage corruption** | pruned receipts; snap sync without receipts | did:ethr resolution impossible from that node | archive or receipt-retaining nodes for Plane V — Ds | qualitative |
| BP-L2.3-01 | **Off-chain body loss** | no Plane-D owner | anchor verifies, nothing to verify against (`lifecycle_backends.py` l. 191–195) | Plane D — Ds | R4 `PF-05` |
| BP-L2.3-02 | **Replay-cache eviction** | > 65,536 live entries in 1.1 s | an evicted message replays inside the window | sizing rule — partial | PF-53 |
| BP-L3.2-01 | **Client monoculture** (Besu-only consortium; Hardhat-only evidence) | one client version everywhere | one bug halts or forks Plane A; BFT's independence assumption void | ≥ 2 clients — Ds; M2 on a second client — open (D-10) | PF-60 (partial); **PF-65** (common-mode term, extends R4 `PF-16`: at *N_v* = 4, *p_c* = 0.05, 1.40·10⁻² rising to 2.39·10⁻² at *p_cm* = 0.01; R7 §7.1) |
| BP-L3.2-02 | **Dev-chain semantics differ from production** (automine, unlimited code size, zero base fee, single-process time) | results taken from IMP-L3.2-02 | latency and finality not transferable; oversized bytecode may not deploy; time-dependent logic never sees block-time jitter | M2 witness and Besu deployment — open | PF-39 (gas factor = 1; latency not transferable) |
| BP-L4.2-01 | **Permissioning-contract compromise** (Besu) | admin key stolen | attacker admits nodes/accounts or ejects validators | multisig / timelock — Ds | **PF-66** (governance key vs m-of-n: 1.00×10⁻² for 1-of-1, 2.98×10⁻⁴ for 2-of-3 at *p_key* = 0.01; analogue R4 `PF-30`; R7 §7.1) |
| BP-L4.2-02 | **Single-key contract governance** (`registryAuthority`, `governor`, `contractOwner`, `DEFAULT_ADMIN_ROLE`) | that key lost or stolen | issuer, service and manufacturer lists rewritten; `transferRegistryAuthority` silent | multisig / timelock — open (CA-16) | **PF-66** (R7 §7.1) |
| BP-L5.2-01 | **Cross-chain replay of ERC-1056 `*Signed` ops** (D52) | **met by default in this repository**: the harness (chain 31337) and the testbed node (chain 1337) both deploy from Hardhat's default accounts, so the same deployer key and nonce give the same registry address on both; equally for any same-key or CREATE2 deployment. The signer's `nonce[owner]` must also match, which holds for a fresh identity (nonce 0) on both chains | an owner change signed for one chain replays on the other (`BP-L5-02` realised) | documented, G3 narrowed (D52 "documented"); a fix leaves upstream bytecode (Q-R6-05; R9 B-02, CA-01). Executed two-chain test proposed (**CA-02**) to move this from source-read to M | **precondition, not a probability** (R9 PN-03): same deployer key + same deployment nonce + same signer nonce. Caveat: today the testbed compiles VPR and MOBI only, not EDR, so CA-02 must deploy EDR on the 1337 node itself |
| BP-L5.2-02 | **Zero-identity seizure** (D53) | identity `0x0`; v = 27, r = s = 0 | `owners[0x0]` seized; impact limited to DID 0x0 | open (L); WM-2 C2; CA-03 | qualitative |
| BP-L5.2-03 | **Replay inside the window (D29) and binding fail-open (D28, D38)** at L7 | same message to other receivers; credential without `intersectionId` | forged-context SPaT accepted | verifier v3 (D28, D29 fixed `f1f9e37`; D38 fixed 2026-10-14) — closed; residual by design: a fresh relay to a receiver that never heard it | PF-47; PF-53 |
| BP-L5.2-04 | **Guardian super-owner** (D15) | guardian key compromised at any time | instant takeover via `recoverOwner` | time-lock and threshold — open (CA-05) | R4 `PF-30` |
| BP-L5.2-05 | **Unrestricted DELEGATECALL** in ERC-725X (D24) | owner delegatecalls a malicious target | slot 0 `_owner` overwritten | documented spec hazard — open | qualitative |
| BP-L5.2-06 | **Reentrancy surfaces** (`payToll`, `_checkOnERC721Received`, 725X `execute`, 4337 `execute`/`handleOp`) | malicious receiver or target | — | **audited in v0-2 (§4.2): no state written after the external call in any of the four; low exposure.** Kept as a BP so the audit is citable; R9 CA-17 can close on that basis | qualitative (CEI check, I) |
| BP-L6.1-01 | **Unsalted VIN-derived identity (D64) and unsalted `keccak(VIN)` token ids (1155, LSP8)** | VIN enumerable per make/plant/year | G7 fails: salted `vinHash` and AES-GCM beside it do not hide the VIN in the testbed realisation; #60 reverses a serial-unknown VIN hash in 3.58 s | ZK-VIN with salt (SOL-11) — closed for the ZK path only (R9 SLD-08, NC-08) | PF-33, PF-34 |
| BP-L6.2-01 | **Non-standard cryptosuite and canonicalisation** | a verifier expects URDNA2015 / a registered suite | interop failure; parties may sign/verify different bytes | documented deviation — open (R9 B-13) | qualitative |
| BP-L7.2-01 | **Pseudonym linkability through the registry** (M5 pool: pseudonyms are delegates of one DID) | an observer reads `DIDDelegateChanged` | every pseudonym is linked to the vehicle DID: req. R5 fails *by construction* — M #38 (60/60 via one `eth_getLogs`) | off-chain pseudonym certificates (1609.2 butterfly keys) or ZK membership — open (Q-R6-04; CA-11; R9 NC-03) | PF-62 (*k_A* = 1) |
| BP-L7.2-02 | **Wall-clock dependence in validity checks** (D40, D51, D63) | verifier clock ≠ chain time | revoked key accepted (D51 pre-fix) or valid key rejected; probe path judges expiry by last-learned chain time + 900 s (D63) | D51 fixed (`7d08dce`); D40 and D63 documented (CA-14) | PF-47 (partial: no CLOCK_SKEW_S term) |
| **BP-L7.2-03** (new) | **Quiet-sender hole: cached state has no TTL** | a sender stops transmitting (or transmits rarely) after its identity is revoked or rotated; the verifier keeps its cached state | staleness is bounded in *messages* (≤ *k_f* − 1, #46) but **unbounded in time**: a sender that resumes after a long silence is accepted on cached state until its *k*-th message | add `min(k, T_ttl)` — open (CA-07; Q-R7-07; R9 B-16) | **PF-54** (and PF-55 for *k_f*\*) |
| **BP-L7.2-04** (new) | **Message encoding size vs channel capacity** | the repository's JSON encoding (596 B DID, 1,110 B PEM, #23) deployed on a 10 MHz channel | at CBR 0.6, an 802.11p channel holds 63 (DID) or 37 (PEM) vehicles against ≈ 182 for a digest-signed 1609.2 BSM: Tier-1 deadline missed at modest density (`BP-L7-07`) | compact UPER/1609.2 encoding — open; "research JSON, not deployable" (R9 SLD-04, NC-10) | **PF-44** (DERIVED from M sizes, E PHY overheads) |
| BP-L7.3-01 | **Steward / oracle trust** | the agent's host or an issuer lies | proofs about false attributes; odometer rollback recorded as authentic | issuer-signed commitments; Steward audit log — partial | qualitative |

### 4.2 Checks-effects-interactions audit of the four reentrancy surfaces (PN-05)

Source-read, status **I**. Question: is state written, or a security check made, after the external call?

| Surface | External call | State written before the call | After the call | Verdict |
|---|---|---|---|---|
| `CVIN_NFT_DID_ERC721.payToll` (l. 71–83) | `payable(operator).call{value: msg.value}("")`, operator = contract owner | none (checks only: token owner, value > 0, operator ≠ 0) | `require(sent)`; `emit TollPaid` | CEI holds; no state to corrupt. Re-entry would only pay another toll with the re-entrant's own value |
| `CVIN_NFT_DID_ERC721_Monolithic._safeTransfer` → `_checkOnERC721Received` (l. 134–137, 190–205) | `IERC721Receiver(to).onERC721Received(…)` | `_transfer` completes (approval cleared, balances and owner updated) | return-value check only | CEI holds. A re-entrant receiver sees post-transfer state; the classic ERC-721 receiver pattern |
| `CVINVehicleERC725XY.execute` / `_executeCall`, `_executeDelegateCall` (l. 216–306) | `call` / `delegatecall` / `staticcall` / CREATE / CREATE2 | event emitted | `_verifyCallResult` only | CEI holds; `onlyOwner` on entry. Re-entry requires the owner as caller. The real hazard is DELEGATECALL itself (BP-L5.2-05, D24), not reentrancy |
| `CVINVehicleAccount.execute` (l. 186–196); `CVINMinimalEntryPoint.handleOp` (l. 69–92) | `target.call{value}(data)`; `userOp.sender.call(callData)` | EntryPoint: nonce incremented **before** validation and call (l. 71–72) | revert bubbling; event | CEI holds. A re-entrant `handleOp` meets the incremented nonce. The account's prefund `call` (l. 147) never executes here (`missingAccountFunds` is always 0) |

Result: no reentrancy finding; Q-R6-06 closed. BP-L5.2-06 stays as a *checked* surface, citable as "no CEI violation (source-read)" — not a substitute for an external audit (R9 SLD-16).

---

## 5. New solutions found in the repository (SOL-10 onward)

Test (R9 PN-09): an item is a SOL if it moves an identity design on R3's trust–finality–cost surface or removes a Phase 1 breaking point; if it only hardens one component, it is a mechanism cited by IMP/ALG tag. **The author decides (Q-R9-01); this is the v0-2 proposal.**

| Tag | Item | Layers | Addresses (BP) | St | v0-2 disposition | Repo |
|---|---|---|---|---|---|---|
| **SOL-10** | **IdtxExecutor + IdentityCommitments** — identity-dependent transactions with Owner/Delegate/Commitment predicates, caller-independent; same-tx and intent/fulfil; commitment voids when its setter stops owning the identity | L5.2, L6.3 | BP-L2.1-01; `BP-L6-06` (confused deputy); intent-to-action TOCTOU | **I** (compiled prototype; no result by its own rule; mechanism is prior art, I-24 brief) | **SOL** — adds a new operation class to the identity surface (R9 keeps it) | `phase2/idtx/contracts/IdtxExecutor.sol` |
| **SOL-11** | **ZK-VIN** — Poseidon commitment to (VIN, year, region, salt), WMI membership, year threshold, per-scope nullifier, Groth16 on BN254, `ZkVinGate.admit` | L1.1–L6.3 | BP-L6.1-01; `BP-L6-05`; `BP-L6-08` for the predicates it covers | M (#56–#58); setup insecure (BP-L1.2-04) | **SOL** — the only VIN-hiding path (R9 keeps it) | `5_zkp-agent-identity/circuits`, `contracts` |
| SOL-12 | Schnorr-via-ecrecover verifier and the `zkid` sigma library | L1.1, L5.1 | cost alternative to SOL-11 for simple statements | M (#58 28,775 gas; #59) | **mechanism** — cite as ALG-15, IMP-L1.2-09; it is a cheaper primitive for a statement SOL-11 already covers, and does not move the design | `SchnorrEcrecoverVerifier.sol`; `zkid/` |
| **SOL-13** | **MOBI VID registries (I, II)** — manufacturer-gated birth, anchored key, ownership history, role-gated lifecycle events, owner-consented chain-bound attestations | L5.2, L6.1, L6.2 | `BP-L6-03/07` partly; D11/D11b; D54 | M (#28, #30, #33, #35) | **SOL** — an application profile with its own trust model (R9 keeps it) | `contracts/MOBI/` |
| **SOL-14** | **Steward agent** — vault without value getters, signed owner policy, leakage audit, learned responder, delegated identity | L7.1 (with L1.1 sigma) | twenty-questions narrowing (#61); `BP-L7-01` partly | M in Sim (#61, #62) | **SOL** — moves the disclosure boundary into the agent (R9 keeps it) | `steward/` |
| SOL-15 | Freshness module + verifier v3 | L7.2 (with L2.3) | `BP-L7-04`; BP-L5.2-03; D28–D31, D37–D42 | M (#21, #44–#48) | **mechanism** — cite as IMP-L7.2-01, IMP-L7.2-03; defect-driven hardening of the message path every design needs | `freshness.py`; `infrastructure_layer.py` |
| SOL-16 | Freshness-*k* cached verification with one-call probe | L6.1, L7.2, L0.4 | `BP-L7-03` vs `BP-L7-07`; turns W into a *k*-parameter (R4 `PF-15`) | M (#32, #37, #52, #55; #46) | **Disposition: keep as SOL, contrary to the panel.** It is the repository's realisation of HAA-1's read rule (*k_f* → ∞ takes the ledger off the Tier-1 path, R9 §1 point 2). It moves the design along the finality–latency axis of R3's surface: it trades bounded staleness for latency. That is a trilemma move, not a hardening. Cite the code as IMP-L7.2-04; cite the trade-off as SOL-16. If the author disagrees, re-label it "mechanism" and nothing else changes | `erc1056_provider.py` |
| SOL-17 | On-chain did:ethr resolution, fail-closed | L6.1, L0.4 | `BP-L2-05` partly; not BP-L0.4-02 | M (#24, #31, #51) | **mechanism** — cite as ALG-23; a correct resolver is a precondition of every design | `did_resolver.py` |

Proposed contribution list: **SOL-10, SOL-11, SOL-13, SOL-14, SOL-16**. The numbers SOL-12, SOL-15 and SOL-17 stay reserved, because tags are frozen once issued, and are annotated "mechanism (cite as IMP/ALG)" (R9 DRP-09).

**SOL-01 lineage (KD-R6-01).** R2's SOL-01 ("Hardhat + Foundry harness with a single-validator Besu QBFT node") does not describe this branch: no Foundry, no Besu config, genesis or trace (v0-1 search; R9 §1); the only Besu text is `V2_DESIGN.md` l. 391. It refers to the `cvin-sandbox-v1.x` lineage. KD-R6-01 absorbs ~~KD-R8~~: HAA-1 Plane A has no code here.

---
## 6. Secured-by chains: worked vertical traces

Each trace descends from a function ("⇐" = "is secured by") and ends with its weakest link, what is measured, and — new in v0-2 — **↑ Serves**, the R3 requirement it exists for (R9 §2.1).

**Trace 1 — key rotation on ERC-1056 (`SCF-EDR-03 changeOwner`).**
`changeOwner(identity, newOwner)` writes `owners[identity]` ⇐ `onlyOwner`: `msg.sender == identityOwner(identity)` (SCF-EDR-01, IMP-L2.1-03) ⇐ `msg.sender` is the address recovered from the outer transaction signature (PRO-21, EIP-155 chain id) ⇐ client-side ECDSA secp256k1 over keccak(RLP(tx)) (ALG-02, ALG-07) with an RFC 6979 nonce ⇐ the private key in the wallet (IMP-L7.1-02 in the testbed; HW-06 in deployment) ⇐ OS CSPRNG (IMP-LH.1-01) ⇐ hardware RNG (HW-02). Ordering: the rotation is final when its block is — under ALG-19 automine, instantly and trivially; under ALG-20 QBFT in SOL-02, after R4 `PF-25` (Ds).
*Weakest link:* the testbed's vehicle key is SHA-256(vehicle_id) (BP-LH-02). *Measured:* two gas figures, different contexts (PN-06): **68,854** (register #2, M1, per-option test context, status V) and **51,754** (harness U1 `rotate_controller`, ERC-1056 pure column, `results/metrics/latest/tables/crud_gas.csv`, run `2026-10-23T00-49-12Z_1f4ace0`). Prose quotes the register row; harness tables quote the run id (R9 PN-21). *Design:* everything below the CSPRNG.
**↑ Serves:** I3 key lifecycle (rotation with a history no one can rewrite); req. R7 ordering.

**Trace 2 — the relayed variant (`SCF-EDR-04 changeOwnerSigned`).**
As Trace 1, but authority comes from the inner signature: `ecrecover(keccak(0x19 0x00 ‖ registry ‖ nonce[owner] ‖ identity ‖ "changeOwner" ‖ newOwner), v, r, s)` (PRO-16, ALG-03; `EthereumDIDRegistry.sol` l. 160–172) ⇐ the EVM's `ecrecover` (IMP-L1.2-05; IMP-L1.2-06 in Besu) ⇐ ECDLP (T-06). The relayer's outer transaction authenticates only the relayer.
*Weakest link:* the digest binds registry address and nonce, **not chain id** (D52 → BP-L5.2-01, whose precondition is met by default here); r = s = 0 seizes DID 0x0 (D53). No negative test exists for this function (Q-R6-07). *Measured:* #50 (U5 `setAttributeSigned` 62,646 gas; the `changeOwnerSigned` cell is in the L1 signed-op suite, `08-signed-op.test.js`).
**↑ Serves:** I3 under relayed submission (U5); req. R8 replay resistance — narrowed to one chain (R9 NC-09).

**Trace 3 — a V2V SSI BSM (`IMP-L7.2-02` via `sign_message` / `verify_message`).**
Receiver accepts ⇐ message freshness: window and replay cache (IMP-L7.2-01, IMP-L2.3-06) ⇐ the receiver's clock (HW-10 by assumption; host clock in the testbed) ⇐ signature over `signed_bytes(message, generation_time)` verifies under the sender's key (ALG-04, ECDSA secp256k1 with SHA-256, IMP-L1.2-01) ⇐ that key is the sender's current `did/pub/secp256k1/veriKey` attribute (SCF-VPR-05/08), resolved by `eth_getLogs` replay (ALG-23, PRO-13), or held in the state cache for *k* messages (IMP-L7.2-04, SOL-16) ⇐ the attribute's `validTo` judged in chain time (IMP-L5.1-03; D51 fixed) ⇐ the registration transaction was signed by the controller key (Trace 1).
*Weakest links:* GNSS time (BP-LH-04); unproven RPC (BP-L0.4-02); the TTL-less state cache (BP-L7.2-03); message size on air (BP-L7.2-04). *Measured:* #21 (15.513 ms uncached verify), #37 (3.222 ms probe), #27 (0.142 ms warm, on a Xeon, not an OBU — R9 SLD-03, NC-05). This path is **not** EIP-191/keccak and is not checked on chain; it shares only the curve with Trace 1 (KD-R6-04).
**↑ Serves:** req. R1 authenticity, req. R8 freshness, req. R6 availability within Tier 1; I1 binding, I8 revocation with a bound (in messages, not seconds).

**Trace 4 — the PKI baseline BSM ("X.509 P-256 pseudonym-certificate baseline, 1609.2-style", KD-R6-03).**
Receiver accepts ⇐ freshness (as Trace 3) ⇐ ECDSA P-256 / SHA-256 signature (ALG-05, IMP-L1.2-01) ⇐ the certificate chains to the CA (X.509, T-I02) and is not on the CRL set ⇐ the CA's P-256 key (software here; HW-03 in deployment) ⇐ CSPRNG. Deployed: 1609.2 `SignedData`, SCMS butterfly keys, OBU HSM (PRO-12, HW-03, HW-08) — **Ds**.
*Weakest link:* the CA key's custody. *Measured:* #21 (0.226 ms verify), #23 (1,078–1,110 B).
**↑ Serves:** req. R1, req. R8 for the incumbent comparator; req. R5 only in its deployed (Ds) form.

**Trace 5 — ZK-VIN admission (`SCF-ZKG-03 admit`).**
`Admitted` ⇐ `nullifierUsed[scope][nf]` false and public signals equal the anchored commitment, `mfrRoot` and service fields (SCF-ZKG-01/02) ⇐ `verifyProof` true (SCF-G16-01) ⇐ `ecMul`/`ecAdd` for the input combination and one `ecPairing` (PRO-18) ⇐ BN254 ≈ 100-bit security (ALG-10) **and** a verification key from a setup whose toxic waste was destroyed — here single-party, fixed entropy (BP-L1.2-04; R7 PF-35) ⇐ a sound R1CS (IMP-L1.2-07; BP-L1.2-03) ⇐ Poseidon collision resistance (ALG-09) ⇐ the commitment anchored by the identity's ERC-1056 owner (Trace 1).
*Weakest link:* the setup. *Measured:* #56–#58; on-chain cost model within 1.3 % of measured (R7 PF-51).
**↑ Serves:** I6 selective disclosure (predicates over the VIN); req. R5 unlinkability across scopes (nullifier per scope); G7 VIN privacy.

**Trace 6 — owner-consented lifecycle attestation (`SCF-MOBI2-04 attestEvent`).**
Attestation stored ⇐ `ECDSA.recover(toEthSignedMessageHash(keccak(this ‖ chainid ‖ vehicle ‖ eventId)), sig) == msg.sender` (IMP-L1.2-11: low-s, non-zero, chain-bound — the most hardened recovery in the repository) ⇐ `msg.sender` holds an issuer role (SCF-MOBI2-01; one `registryAuthority` key, BP-L4.2-02) **and** is the vehicle's owner or stored `veriKey` delegate (D54 fix) ⇐ the outer transaction signature (Trace 1).
*Weakest link:* the single registry-authority key. *Measured:* #28 (198,694 execution gas).
**↑ Serves:** I5 attribute issuance with holder consent; req. R4 non-repudiation of the endorsement.

**Trace 7 — a next-transaction IDTx (`SCF-IDTX-03/04 createIntent → fulfil`).**
`Executed` at fulfilment ⇐ `holds(dep)` re-evaluated now — e.g. Commitment kind ⇐ `IdentityCommitments.valueOf` non-zero (chain time vs `validUntil`; `setBy == identityOwner`) ⇐ SCF-EDR-01 ⇐ the owner's rotation history (Trace 1) ⇐ intent, any intervening rotation and fulfilment ordered in one history (L3.1).
*Weakest link:* keeper liveness and chain time are external; with automine every transaction is its own block, so the race the design defends against is never exercised (BP-L3.2-02). *Status:* **I** (no result by its own rule).
**↑ Serves:** I4 delegation and I3 lifecycle as *preconditions of an action* (I-24's IDTx definition P2-D8); req. R7 ordering.

**Trace 8 — an on-chain Schnorr PoK (`SCF-SCH-02 prove`).**
`Proved` ⇐ `e == keccak(ecrecover(h, parity+27, px, σ) ‖ parity ‖ px ‖ message)` (ALG-15) ⇐ `ecrecover` computing r⁻¹(σ·P − h·G) (PRO-16) ⇐ ECDLP and keccak as a random oracle (T-06, T-07, T-I10).
*Weakest link:* no replay guard — the same proof can be resubmitted (CA-13). *Measured:* #58 (28,775 gas).
**↑ Serves:** I2 control proof (knowledge, not freshness).

**Trace 9 — a VC presentation verified offline (`IMP-L6.2-01/02`).**
Verifier accepts ⇐ EIP-191 recovery over deterministic JSON (ALG-03, PRO-22b; not URDNA2015, BP-L6.2-01) yields the issuer's address ⇐ that address is, or is a delegate of, the issuer DID (ALG-23 on chain, or ALG-23a synthesised, which binds nothing beyond key = address) ⇐ disclosed claims hash to the signed salted digests (ALG-08) ⇐ `credentialStatus` not revoked in the `RevocationRegistry` (IMP-L2.3-01: memory or JSON file, **no anchoring**) ⇐ issuer key from a CSPRNG.
*Weakest link:* the status registry's host. *Measured:* #4, #27.
**↑ Serves:** I7 verification, I6 selective disclosure, I8 revocation (bound only by the status file's host).

---

## 7. What is measured vs designed (one row per sub-layer)

Locked by R9 SLD-12 (ch1 §1.5, ch5 §5.8, Appendix E). §7 lists *what* was measured per sub-layer; the per-dimension evidence count is R8 §5 (77 ● of 418 category × MD cells). The two are complementary, not the same count: this table's "M" column is per sub-layer and pools every MD (RL-04 (ii); PN-39).

| Sub-layer | M in this programme (rows / files) | Ds only | Not used | Honest one-line summary |
|---|---|---|---|---|
| LH.1 | environment headers (#27, #57) | entropy quality | — | keys come from a cloud host's OS CSPRNG, or from SHA-256(vehicle_id) in the testbed |
| LH.2 | — | HSM, SE, TEE | TPM | no key in this programme has lived in hardware |
| LH.3 | — | — (OBU is I, a Python object) | CAN, Ethernet, gateway | the vehicle is simulated |
| LH.4 | — | GNSS time assumption | real modems | radio is a free-space model; time is the host clock |
| LH.5 | same-host replicates (#52, #55) | validator hosts | — | one host per run |
| L0.1 | — (PC5 mode-4 `ResourcePool` is I; no row) | reselection on pseudonym change | 802.11p, NR-V2X | no PHY/MAC result; RF linkability is Dv only (PF-45) |
| L0.2 | loopback HTTP cost (#39) | Uu backhaul | WSMP, QUIC | localhost only |
| L0.3 | — | static nodes, permissioning | devp2p, discv4/5, libp2p | no P2P network ever ran |
| L0.4 | RPC counts and bytes (#21, #31, #37, #51) | TLS to providers | WS, Engine API | reads are unproven |
| L1.1 | ECDSA/P-256 verify (#21, #27); Groth16 (#56–#58); sigma (#59); hash enumeration (#60) | — | Ed25519, BLS12-381, CL/BBS+ | the best-measured layer after gas |
| L1.2 | library versions per result | BouncyCastle (Besu) | anoncreds-rs | six secp256k1 implementations in use |
| L2.1 | SSTORE and log-byte counts (#30, #49) | Bonsai | proofs (`eth_getProof`) | state is counted, never proved; the `changed` walk is intact (D21, D22 fixed) |
| L2.2 | — (in-memory) | RocksDB | — | nothing persists beyond a run |
| L2.3 | replay-cache behaviour (#45) | status list, CAS | accumulators | revocation lists are a Python dict or file |
| L3.1 | automine as the condition of every M1 row (`meta.json`) | QBFT, Gasper | IBFT 2.0, Clique | no consensus protocol has been measured; *N_v* = 1 |
| L3.2 | Hardhat 2.28.6 | Besu, Quorum, Ganache (configured) | Geth, Anvil | single-client evidence |
| L4.1 | gas, exhaustively (#1–#3, #22, #25, #29–#35, #47–#50, #54, #58) | free gas, EIP-1559 pricing | blobs | gas is exact; price is E (#20) |
| L4.2 | role-gated attack cells (#28, #45) | node/account permissioning, validator governance | — | governance is single EOA keys |
| L4.3 | instrument *G* = 60 M (`meta.json`) | capacity at design *G* and Δ (PF-49) | — | capacity is Dv, not measured |
| L5.1 | precompile gas in aggregate (#58) | — | sha256, modexp, BLS | `ecrecover` and bn256 carry the load |
| L5.2 | per-function gas and attack cells for ten columns (#25, #28, #29–#36, #49–#54) | — (IdtxExecutor is I) | — | 117 SCF rows; negative tests for 24 of 44 checked rows (Q-R6-07); CEI clean on four surfaces (I) |
| L5.3 | legacy/EIP-155; UserOps (#25, #50); `*Signed` meta-tx (#50) | — | 2930, 4844, 7702 | chain id binds the outer tx only |
| L6.1 | did:ethr on chain (#24, #31, #51) | — | did:indy | did:ethr and did:mobi are real; the rest are synthesised |
| L6.2 | VC v2.0 Data Integrity, thesis cryptosuite (#4, #27) | — | AnonCreds, BBS+, mDL | selective disclosure is SD-JWT-style digests |
| L6.3 | Set A/B coverage (#53, #54); ZK admission (#58); attestations (#28) | — | — | IDTX exists as code without a result (I) |
| L7.1 | provider timings (#21, #32, #33, #37); Steward Sim (#61) | — | ACA-Py, Veramo | Python providers, not agents |
| L7.2 | message freshness and verifier v3 (#44–#48); state refresh *k* (#32, #37, #46); message size (#23) | 1609.2 encodings; TTL | DIDComm | JSON-signed messages; staleness bounded in messages, not time |
| L7.3 | V2V in `--simulate` (#27); RSU/TMC (#44–#48); lifecycle (#30, #33); pseudonym pool (#38, negative) | SUMO-binary runs (#15 E), ns-3 | — | mobility is mocked in the runs of record |

---

## 8. Placeholder resolution (v0-1 PF-⟦n⟧ → v0-2)

From R9 §3.3 Table A′. Every former request is now supplied by R7 v0-2 (PF-46, PF-63..66).

| v0-1 | Meaning | v0-2 | State |
|---|---|---|---|
| ~~PF-⟦1⟧~~ | κ_eff vs boot entropy | **PF-41, PF-42** | resolved |
| ~~PF-⟦2⟧~~ | κ of the vehicle-id space | **PF-63** (κ = H(vehicle_id); R7 §7.1) | resolved |
| ~~PF-⟦3⟧~~ | accepted replay age = max_age + δ_clock | **PF-47** items 1, 4 | resolved |
| ~~PF-⟦4⟧~~ | P(false read) vs independent endpoints | **PF-64** (R7 §7.1) | resolved |
| ~~PF-⟦5⟧~~ | P_loss(CBR) | **PF-44** (capacity); **PF-46** (P_loss bracket; R7 §4.5) | resolved (first-order bracket) |
| ~~PF-⟦6⟧~~ | W ≥ σ + T_off | **PF-48** | resolved |
| ~~PF-⟦7⟧~~ | eclipse cost vs table size | — | qualitative (no P2P in repo) |
| ~~PF-⟦8⟧~~ | p_bug × client share | **PF-60** (HHI) | partial |
| ~~PF-⟦9⟧~~ | circuit soundness / audit coverage | — (PF-35 assumes a sound R1CS) | qualitative; audit status → PF-61(e) |
| ~~PF-⟦10⟧~~ | log availability vs pruning | — | qualitative |
| ~~PF-⟦11⟧~~ | P(evict live) | **PF-53** | resolved |
| ~~PF-⟦12⟧~~ | *p_c* with correlation ρ_c | PF-60 (partial) + **PF-65** (R7 §7.1) | resolved |
| ~~PF-⟦13⟧~~ | dev-to-prod transfer factor | **PF-39** (gas factor 1; latency not transferable) | resolved as a negative statement |
| ~~PF-⟦14⟧~~ | governance key vs m-of-n | **PF-66** (analogue R4 `PF-30`; R7 §7.1) | resolved |
| ~~PF-⟦15⟧~~ | cross-chain address + nonce match | — | **re-posed as a precondition** in BP-L5.2-01 |
| ~~PF-⟦16⟧~~ | VIN entropy vs hash rate | **PF-33, PF-34** (19.93 bits; #60) | resolved |
| ~~PF-⟦17⟧~~ | on-chain anonymity set of a pseudonym pool | **PF-62** (*k_A* = 1; #38) | resolved |
| ~~PF-⟦18⟧~~ | skew vs CLOCK_SKEW_S | **PF-47** (no CLOCK_SKEW_S term) | partial |
| ~~PF-⟦19⟧~~ | oracle / issuer misreport detection | — | qualitative |
| ~~PF-⟦20⟧..⟦24⟧~~ | reserved | — | released (unused) |
| (new) | BP-L0.1-02, BP-L7.2-03, BP-L7.2-04 | **PF-45, PF-54, PF-44** | resolved at creation |

**Live ⟦⟧ placeholders remaining: none** (⟦⟧ appears only in struck-through retirement entries). Former requests are supplied (PF-63..66: four; PF-46); the remaining open bounds carry the word "qualitative" (seven BPs from v0-1 placeholders, plus those that never had one). The two v0-2 partial bindings are closed: PF-45 (reselection linkability, R7 §4.4) and PF-46 (loss bracket, R7 §4.5).

**Supplied by R7 v0-2 (PF-63..66; formerly requested here).** PF-63 deterministic-key entropy: κ = min-entropy of the vehicle-id space (likely a sentence, not a bound). PF-64 false-read probability with *r_e* independent RPC endpoints and a collusion prior. PF-65 correlated client failure: R4 `PF-16` with correlation ρ_c across validators sharing a client. PF-66 governance-key compromise vs m-of-n multisig with time-lock.

---

## 9. Change log v0-1 → v0-2

| # | Change | Where | Answers |
|---|---|---|---|
| C-01 | Defect statuses re-verified against `DEFECT_LOG.md`; D18, D21, D22 rewritten as fixed with commits, open residues named; "Dn @ 2026-10-22" column added to every §2 table | SCF-CVDR-03, SCF-VPR-07/09, SCF-CMB-03/06/07, IMP-L2.1-04, BP-L2.1-02 | PN-01 |
| C-03 | ALG-21 → ALG-23 cross-reference fixed in IMP-L2.1-04; ALG-17 annotated "primitive (L1.1)", ALG-21 "cost model" | L1.1, L2.1, L4.1 | PN-02 |
| C-04 | PRO-13x/y/z re-tagged PRO-23/24/25, with strike-through retirement | L7.2; key-change table | PN-02 |
| C-05 | Every PF-⟦n⟧ resolved to R7 tags, re-posed, marked qualitative, or bound to PF-63..66 (supplied by R7 v0-2) | §4, §8 | PN-03 |
| C-07 | BP-L5.2-01 precondition stated concretely (default Hardhat accounts on 31337 and 1337; same deployer, deployment nonce and signer nonce); CA-02 cited, with the caveat that the testbed does not compile EDR | BP-L5.2-01, Trace 2 | PN-04 |
| C-08 | CEI audit of the four reentrancy surfaces done from source; Q-R6-06 closed; BP-L5.2-06 kept as an audited surface | §4.2 | PN-05 |
| C-09 | Negative-test cross-check of 44 state-changing rows on EDR, VPR, MOBI1, MOBI2, CMB, E4337A ("Neg." column); 20 gaps logged as Q-R6-07 | §2.L5.2 | PN-05 |
| C-10 | Trace 1 quotes both gas figures with context and provenance (68,854 #2; 51,754 harness run `1f4ace0`) | §6 | PN-06 |
| C-11 | Test counts 562 Hardhat / 376 Python, with the STATUS section named | IMP-L7.1-01/02 | PN-07 |
| C-12 | Three BPs added: BP-L0.1-02 (SPS resource persistence), BP-L7.2-03 (no TTL on cached state), BP-L7.2-04 (encoding size vs capacity), bound by PF-45, PF-54, PF-44 | §4 | PN-08 |
| C-13 | SOL test stated; SOL-12, SOL-15, SOL-17 re-labelled "mechanism"; SOL-16 kept as SOL with a disposition note | §5 | PN-09 (partly disputed) |
| C-14 | "↑ Serves" line added to every trace | §6 | R9 §2.1 clarity; §7.1 item 10 |
| C-15 | Unified status scale (M/Dv/I/Ds/E/S/—); "candidate" → Ds with note; "used" → I; IdtxExecutor → I | all tables; header | PN-32 |
| C-16 | Re-keying Q-R7..12 → Q-R6-01..06, KD-R4..8 → KD-R6-01/03/04 (02 → KD-R7-02, 05 → KD-R6-01) with strike-through table | header; §5; HANDOFF | PN-31; R9 §3.1 |
| C-17 | Elevator box and ↑/↓ cross-links (to adjacent layers, R7 PF, R8 RV, R9 PRM) at every layer; last column of §1 links PF and RV | §1, §2 | brief §5; v0-2 instruction 4 |
| C-18 | Message vs state freshness separated; IMP-L7.2-04 added for the state-refresh code so R8 can re-anchor RV-READ-03 / RV-ALG-09 | L7, L7.2 | PN-24 (supports R8) |
| C-19 | O-mapping re-confirmed as the reference for R8's fix; Freeze re-read still open | §3 | PN-22 (supports R8) |
| C-20 | Capacity and *G* re-labelled: 60 M is the instrument's limit, *G* and Δ are PAR; PF-50 marked privacy-excluded | L4, L4.3 | PN-14, PN-15 (alignment) |
| C-21 | Status corrections at row level: E735 has low-s and zero-address guards (v0-1 implied none); VPR `revokeIdentity` single-shot; MOBI1 `changeOwner` reverts for born vehicles (D16 part); D27 fixed; D54 fixed | §2.L5.2, L6.1 | repo re-read (PN-01 discipline) |
| C-22 | Padding cut (status prose, §0.2 listing) | throughout | v0-2 instruction 6 |

**Disposition notes (where v0-2 keeps v0-1's position, or departs from R9).**
- *PN-09, SOL-16.* Kept as SOL against the panel's proposal. Reason in §5: it is the repository's realisation of HAA-1's read rule and trades staleness for latency, which is a move on R3's surface. The panel's own §1 point 2 relies on exactly this move. The code is re-tagged IMP-L7.2-04, so a demotion later costs one line.
- *PN-05, BP-L5.2-06.* R9 offered "audit or remove". Audited, and **kept** as an audited surface rather than removed, so the negative result is citable.
- *R9 §7.1 item 6 count.* R9 says "the 40 state-changing rows"; this register gives 44 for the named prefixes (EDR 10, VPR 8, MOBI1 8, MOBI2 4, CMB 8, E4337A 6; E4337EP-01 excluded as an entry point). The difference is counting, not scope.

---

## 10. HANDOFF (R6 v0-2 → R7 v0-2, R8 v0-2, R9 v0-2)

**Files.** `docs/roots/phase2/60_R6_full_stack_atlas/claude_CVIN_SC_Roots_FullStack_Atlas_R6_v0-2.md` (this). v0-1 untouched. Nothing else written; no commit.

**Tags.** Unchanged ranges: HW-01..12, PRO-01..22 (with suffixes; ~~13x–z~~ retired), ALG-01..24, IMP- as v0-1, 22 SCF prefixes / 117 rows, BP-LH-01..06, SOL-10..17. **New:** PRO-23..25; IMP-L7.2-04; BP-L0.1-02, BP-L7.2-03, BP-L7.2-04; Q-R6-01..07; KD-R6-01, -03, -04. **Retired:** ~~Q-R7..Q-R12~~ → Q-R6-01..06; ~~KD-R4~~ → KD-R6-01; ~~KD-R5~~ → KD-R7-02; ~~KD-R6~~ → KD-R6-03; ~~KD-R7~~ → KD-R6-04; ~~KD-R8~~ → KD-R6-01; ~~PRO-13x/y/z~~ → PRO-23/24/25; ~~PF-⟦1..24⟧~~ → §8. **Consumed:** R7 PF-33..66 (requested 63..66); R8 RV-, PAR-06; R9 PN-, SLD-, NC-, CA-, PRM-, B-.

**Five load-bearing decisions.** (1) Executed chain = Hardhat automine, *N_v* = 1; every Besu/QBFT/Sepolia row is Ds (SLD-01). (2) The defect log wins over this atlas on status: D18, D21 and D22 are fixed, and BP-L2.1-02 is historical. (3) D52's precondition is met by default in this repository, so cross-chain replay is a configuration fact, not a coincidence. (4) Message freshness (seconds) and state freshness (messages, no TTL) are different properties with different code. (5) Contribution list proposed as SOL-10, -11, -13, -14, -16; SOL-12, -15, -17 are mechanisms.

**Open questions.** Q-R6-01 Freeze re-read. Q-R6-02 add LSP8 etc. as options. Q-R6-03 SOL-01 lineage (answered by KD-R6-01 unless the author objects). Q-R6-04 M5 pool unlinkability scope (with Q-R8-04, Q-R9-02). Q-R6-05 D52 fix vs fidelity. Q-R6-07 the 20 negative-test gaps. Q-R9-01 accept SOL-16 as SOL?

**Corrections issued.** KD-R6-01 SOL-01 does not describe this tree. KD-R6-03 the "1609.2" baseline is X.509 P-256 in JSON. KD-R6-04 SSI BSMs are secp256k1/SHA-256. To R8: anchor state freshness to IMP-L7.2-04; take O-mapping from §3. To R7: none outstanding (PF-45, PF-46 and PF-63..66 supplied in R7 v0-2).
