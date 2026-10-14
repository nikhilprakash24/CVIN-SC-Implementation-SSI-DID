# F2 Capture — Public and Private Blockchains and Other Databases in Phase 1

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F2, capture; research agent draft, verified by the orchestrator)
**Binds:** docs/phase2/README.md

Scope: what Phase 1 uses, prepares, measures and says about the substrate that holds a vehicle's identity
and lifecycle data: an EVM chain (local, HTTP-served, public testnet), a centralized registry, a PKI, and
the off-chain credential layer. Citation forms: `path:line`, or `#n` for a row of the claim register in
`docs/MEASUREMENT_CONDITIONS.md` (the register table is at lines 105-154). Numbers are copied from the
named committed file; none is new. "Unverified" marks what this capture could not confirm from the tree.

## 0. What Phase 1 already shows

1. Every on-chain number comes from a single local Hardhat EVM (chain id 31337, automine): gas is exact,
   latency excludes consensus and propagation (`docs/MEASUREMENT_CONDITIONS.md:23`, `:211`).
2. The public-testnet condition M2 exists only as a prepared harness; no Sepolia result is committed
   (`docs/MEASUREMENT_CONDITIONS.md:26`; `4_comparison-framework/results/sepolia_validation.json` absent).
3. The only transport condition beyond in-process is localhost HTTP (#39), and its row is status **U**.
4. Two non-chain substrates are measured against chains: the centralized lifecycle registry (#33) and an
   in-process X.509 PKI (#21, #27). Both are in-process Python dictionaries, so they are lower bounds.
5. The V2V hot path does not touch any ledger: SSI warm verify is an M0 figure (#27); uncached chain
   resolution is 9.654 ms median on localhost (#21) and 203 ms at history 50 over HTTP (#39, U).
6. "Permissioned" appears in Phase 1 only at the contract level (role-gated ERC-1155, LSP8), never as a
   permissioned ledger (`docs/DID_METHOD_RUBRIC.md:84`). Besu, Quorum, consortium chains, rollups and IPFS
   appear only in 2025 design documents and in future-work or audit text; nothing was built on them.
7. The thesis threats sections reduce the substrate question to "gas is deterministic across EVM chains"
   plus a pending Sepolia run; mempool, fee market, consensus latency and operator trust are not analysed.

## 1. Substrates Phase 1 uses or prepares

### 1.1 Inventory

| Substrate | Condition tag | Code / config | Status in Phase 1 |
|---|---|---|---|
| Hardhat in-process EVM | M1, M1-H | `1_blockchain-identity/hardhat.config.js:61-64` (chain 31337, `allowUnlimitedContractSize`); harness network `docs/MEASUREMENT_CONDITIONS.md:190` | used for all JS gas results |
| Hardhat node over HTTP JSON-RPC | M1-H/HTTP; also the Python M1 experiments | `hardhat.config.js:65-67` (`localhost` 127.0.0.1:8545); Python RPC URLs `cv2x-testbed/results/pki_vs_erc1056.json` (`rpc_url` 127.0.0.1:8550), `lifecycle_parity.json` (127.0.0.1:8558) | used; harness run U (#39) |
| Sepolia public testnet | M2 | `hardhat.config.js:68-72` (chain 11155111); `1_blockchain-identity/scripts/validate_sepolia.js`; `1_blockchain-identity/SEPOLIA_VALIDATION.md` | prepared, never run (N-11) |
| Goerli | none | `hardhat.config.js:73` (`goerli` entry) | dead config; removal is N-3 (`docs/MILESTONE_NEXT.md:19`) |
| Centralized vehicle registry | M0 | `cv2x-testbed/identity/centralized_vehicle_registry.py`; `sandbox/options/baseline-centralized/manifest.yaml` | used (#33; #41 S) |
| Centralized PKI provider (CA, CRL, CT log) | M0 | `cv2x-testbed/identity/centralized_provider.py` | used as `pki_centralized` in #21 |
| IEEE 1609.2-style PKI | M0 | `cv2x-testbed/identity/standard/pki_identity.py`; `sandbox/options/baseline-pki/manifest.yaml` | used (#21, #23, #27) |
| Lifecycle backends | M0 vs M1 over HTTP | `cv2x-testbed/identity/lifecycle_backends.py:58-104` (centralized), `:109-255` (MOBI VID V2 on chain) | used (#33) |
| Off-chain VC layer (status registry, issuer allow-list, resolver) | M0 | `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py:108-160`, `vc_verifier.py:111-153`, `2_w3c-ssi-layer/did-resolution/did_resolver.py` | used (#4, #24, #26 C/D, #27) |
| PoA client middleware | none | `cv2x-testbed/identity/erc1056_provider.py:74-76`, `mobi_vid_provider.py:68-69`, `2_w3c-ssi-layer/mobi-vid/mobi_vid_registry.py:99-103` | code path only; no committed result on a PoA chain (unverified beyond a grep of the results directories) |

### 1.2 Properties per substrate

| Substrate | Trust model | Who can write | Who can read | Finality | Cost model |
|---|---|---|---|---|---|
| Hardhat in-process (M1) | the experimenter's process is the whole network; integrity assumed (`docs/THREAT_MODEL.md:46`) | the Hardhat default-mnemonic role wallets and seeded fresh keys (`docs/MEASUREMENT_CONDITIONS.md:194`); contract rules decide the rest | the same process | immediate: automine, one tx per block except the throughput bursts (`:190`) | exact `gasUsed`; no fee market; USD only as a derived illustration with fixed parameters (`:215`) |
| Hardhat node over HTTP | same single operator; adds a localhost transport | same | any client on localhost | immediate (automine; `pki_vs_erc1056.json` `automine: true`) | same gas, byte-identical tables (#39); latency adds one HTTP round trip per call, ≈1-2 ms (`:25`), ≈2.5 ms floor in the Python stack (`:232`) |
| Sepolia (M2) | third-party public network; its consensus is not described anywhere in the repository | any funded key; the harness needs at least 0.05 test ETH (`validate_sepolia.js:49`) | anyone, via a block explorer (`SEPOLIA_VALIDATION.md:10-15`) | not recorded (no run) | gas claimed identical to M1 within a 100-gas calldata tolerance (`validate_sepolia.js:59`); fee in test ETH, not recorded |
| Centralized vehicle registry | one authority; the docstring lists "single point of failure", "trust required in central authority", "can be censored/manipulated" (`centralized_vehicle_registry.py:160-162`) | issuers by role table (`:646-662`); the caller is not authenticated (`cv2x-testbed/results/lifecycle_parity.md:75`; SC-13 "centralized transfer is unauthenticated", `docs/SCOPE_CHANGES.md:24`) | the process only; stores the plain VIN (`:72`) | immediate and mutable: Python dicts "simulating PostgreSQL" (`:16`, `:170`), no hash chain or signed log (no such code in the file) | none modelled; storage size estimated as JSON bytes (`:630-643`) |
| Centralized PKI provider | one CA; `single_point_of_failure = True`, `availability_percentage = 99.9` "Assumed CA uptime" (`centralized_provider.py:76-77`, an assumption, not a measurement) | the CA | the process; CRL and a simplified certificate-transparency list (`:59-62`, `:504-510`) | immediate | none |
| 1609.2-style PKI | CA hierarchy flattened to one level; X.509 certificates, not 1609.2 encodings (`pki_identity.py:313-382`; `pki_vs_erc1056.md:105`) | the CA issues; vehicles sign | anyone holding the CA certificate and the CRL set (`pki_identity.py:39`, `:199`) | CRL is a Python set, no distribution delay (`pki_vs_erc1056.md:105`) | none; message carries the certificate: 1,078 / 1,110 B vs 596 B for ERC-1056 (#23) |
| Off-chain VC layer | issuer keys are the Layer-1 identity keys, so verification needs no chain round trip (`docs/thesis/chapter4-implementation/README.md:40-41`); trusted issuers seeded by the verifier's configuration (`vc_verifier.py:137-145`) | issuers (VCs); the status registry's bound issuer (`vc_issuer.py:116-123`) | any verifier holding the VC | status registry is in-memory or a JSON file (`vc_issuer.py:112-114`); MOBI VCs are anchored by keccak256 of the canonical VC in a contract field, "no IPFS anywhere" (`chapter4-implementation/README.md:209-211`) | none off-chain; the anchoring transaction is on M1 |

### 1.3 What Phase 1 measured on each, and what it did not

| Substrate | Measured (rows) | Not measured |
|---|---|---|
| Hardhat in-process | nine-standard gas, spread 52,216 → 1,757,881 = 33.7×, ERC-4337 indirection +46,830 gas/op (#25); 15-year lifetimes (#26 A/B); harness per-op, lifecycle and read-path counts (#29-#31, #34-#36), e.g. ERC-1056 lifetime 1,050,809 (#35) and 112 RPC calls / 87 KB / ≈65-71 ms at h = 50 (#31); security 43/43 (#28); pseudonym pool (#38); RSU gas (#47) | any latency that includes block production; fees; reorgs; concurrency beyond one node |
| Hardhat over HTTP | M1-H/HTTP: gas byte-identical, latency ≈2-2.5× in-process, R3 at h = 50 ERC-1056 203 / 238 ms, ERC-1155 5.3 / 6.4 ms (#39, **U**); Python experiments over localhost RPC: #21, #22, #32, #33, #37 | WAN or provider latency (stated as still open, `HANDOFF-DATA-COLLECTION-FRAMEWORK.md:231`) |
| Sepolia | nothing; "Not yet run on this trunk" (`docs/MEASUREMENT_CONDITIONS.md:26`); the 50-100 ms "with blockchain lookup" figure is an estimate (#10, status E; `:77`) | gas witness, inclusion latency, confirmation depth, fees |
| Centralized registry | #33 (and #41, S, which keeps the only `attest_event` row: 13.137 / 16.837 ms on chain, "no centralized equivalent") | a real database, network, authentication, durability, audit log, concurrency |
| Centralized PKI / 1609.2 PKI | #21 (verify 0.253 / 0.329 ms pki_standard, 0.254 / 0.325 pki_centralized); #23; #27 (PKI warm 0.094 ms) | CA network round trips, OCSP, CRL download, pseudonym provisioning at scale (`pki_vs_erc1056.md:105`) |
| Off-chain VC layer | #4 (94.3 % structural self-score), #24 (335/336), #26 C/D (verify O(1) in claim count), #27 | resolution that reads chain state: the resolver synthesises the document from the identifier (`docs/MEASUREMENT_CONDITIONS.md:73`; `docs/thesis/CRUX_REGISTER.md:133`) |

**Throughput.** The run of record's `throughput.json` reports medians of 79.2 to 170.0 tx/s, and each
200-transaction burst is mined in 1 block (2 for ERC-735)
(`1_blockchain-identity/results/metrics/latest/throughput.json`, field `blocks`). No register row carries
these cells. #39's "78-202 in-process" comes from the pre-merge run. The rate is set by the client
queueing transactions into one node with a 60,000,000 block gas limit (`docs/MEASUREMENT_CONDITIONS.md:193`),
so it is not a ledger throughput. SC-05 ("throughput" in RQ1) is still pending (`docs/SCOPE_CHANGES.md:16`).

## 2. Measured comparisons between substrates

### 2.1 Centralized registry vs MOBI VID V2 on chain (#33, M0 vs M1 over localhost HTTP)

Pre-registered in `docs/PLAN_MOBI_SUMO.md` §A.2; n = 50 after 3 warm-ups. The committed result file is the
disclosed second run on the post-G-M bytecode (2026-10-04T22:17:02Z, commit `4f09875`, 2.80 GHz Xeon,
Hardhat 2.28.6, automine; `cv2x-testbed/results/lifecycle_parity.md:9-28`). The row's headline values
(birth 0.0028 / 0.0076 vs 14.13 / 20.77 ms) are from the first run, whose bytecode is no longer in the tree (#33).

| Operation | Centralized median / p95 (ms) | MOBI VID V2 median / p95 (ms) | Gas | RPC/op | Ratio (median) | Verdict |
|---|---|---|---|---|---|---|
| birth | 0.0036 / 0.0058 | 17.689 / 31.403 | 398,274-398,298 | 6 | 4.86e3× | PASS |
| lifecycle event | 0.0089 / 0.0158 | 14.629 / 27.072 | 255,466-255,490 | 5 | 1.64e3× | PASS |
| ownership transfer | 0.0023 / 0.0047 | 13.947 / 17.921 | 182,144 | 5 | 6.04e3× | PASS |
| history (10 events, 2 transfers), uncached | 0.2627 / 0.3039 | 114.222 / 142.183 | - | 39 | 435× | no verdict |
| history, cached copy | 0.2627 / 0.3039 | 0.011 / 0.022 | - | 0 | 0.0414× | **FAIL** (band [0.5, 2]) |
| history, cached + 2-call staleness probe | 0.2627 / 0.3039 | 15.403 / 23.530 | - | 6 | 58.6× | no verdict |

Source: `cv2x-testbed/results/lifecycle_parity.md:38-60`; MOBIVIDRegistryV2 deploy 5,059,513 gas (`:62`).
Reading for F2: (a) the write gap is three orders of magnitude, but the centralized side is in-process
dictionaries, so the ratios are upper bounds (`lifecycle_parity.md:75`); on a public chain the gap would grow
by the block interval (`:76`). (b) The "equal once cached" FAIL is set by the baseline's serialisation:
without `dataclasses.asdict` the centralized history is 0.0007 ms (post-hoc diagnostic, `:44`, `:54`).
(c) The work differs: MOBI encrypts and hashes the VIN and stores event hashes, the centralized registry
stores plain VIN and full bodies (`:77`). (d) Neither chapter 5 nor chapter 6 cites #33 (a grep of
`docs/thesis/chapter5-results/` and `chapter6-discussion/` for "parity", "M4", "centraliz" finds nothing),
although SC-13 says "Ch. 5 reports the parity table" (`docs/SCOPE_CHANGES.md:24`, which also still names it
"register #30").

### 2.2 PKI vs ERC-1056 (#21, M0 vs M1 over localhost HTTP)

| Operation | PKI median (ms) | ERC-1056 median (ms) | ERC-1056 RPC calls | Ratio |
|---|---|---|---|---|
| verify | 0.253 (p95 0.329) | 9.654 (p95 15.984), uncached | 4 (2 are web3 `eth_chainId` overhead) | ≈38× |
| resolve | 0.001 | 8.336 | 4 | - |
| check revocation | 0.001 | 5.810 | 3 | - |
| register / issue / revoke | 4.1 / 0.19 / 0.015 | 12.9 / 12.0 / 10.8 | 5-6 | - |

Source: #21; `cv2x-testbed/results/pki_vs_erc1056.json` (environment: 2.10 GHz Xeon, Hardhat 2.28.6,
automine, registry solc 0.8.20 / evm paris, deploy 927,756 gas, #22). The ERC-1056 column is the cv2x
`ERC1056Registry`, not `EthereumDIDRegistry` (K-5, #21). The `.md` states that only the shape transfers:
"On a public or consortium network, write operations ... take one block interval or more ... plus
confirmation depth" (`cv2x-testbed/results/pki_vs_erc1056.md:106`). Caching changes the picture: a
one-call probe refresh costs 2.76 / 2.89 ms (#37), and the cached path ≈0.43 ms median (#32).

### 2.3 SSI vs PKI V2V verification (#27, M0 only)

SSI warm 0.153 ms [0.151, 0.154], PKI warm 0.094 [0.093, 0.095]; cold 0.399 vs 0.220; 1,650,318 verifies,
150 failures = 5 injected attacks × 30 runs (#27; `cv2x-testbed/sumo/results/v2v_latency_stats.json`,
`per_population`, `totals`). No ledger is contacted in either population, so this compares credential
formats, not substrates. Chapter 6 still says "90 injected attacks (3 per run × 30 runs)"
(`docs/thesis/chapter6-discussion/README.md:182`), which disagrees with #27 and the result file.

### 2.4 MOBI VID across "backends" (H4; `4_comparison-framework/results/mobi_vid_backends.json`)

| Backend | Birth gas | Lifecycle event gas | Third-party attestation gas | Fidelity |
|---|---|---|---|---|
| ERC-1056 | 51,944 | 34,928 | 61,501 (approximate) | 3/5 |
| ERC-735 | 295,242 | 295,277 | 295,289 (native) | 5/5 |
| ERC-1155 | 107,729 | 80,131 | 63,031 (approximate) | 3/5 |
| CVIN-Combined | 51,766 | 34,690 | 336,896 (native) | 5/5 |
| MOBI-VID-V2 | 299,143 | 307,210 | 192,749 (native) | 5/5 |

Same values in `docs/presentation/REPORT_DRAFT_1.md:81-88`. Metadata: `network: hardhat-local`, chain
31337, commit `d0cc19c`, `dirty: false` but `dirtyAnyFile: true`, dated 2026-10-09. No register row carries
these cells; #43 records the sweep's first trunk re-execution on 2026-10-04 with "fidelity scores unchanged".
For F2 the point is that all five "backends" are contracts on **one** local EVM. H4 ("realisable across
blockchain backends", `REPORT_DRAFT_1.md:26`) is a claim across contract standards, not across ledgers.

### 2.5 In-process vs HTTP RPC (#39, M1-H vs M1-H/HTTP, status U)

| Quantity | In-process | HTTP | Source |
|---|---|---|---|
| gas tables | reference | byte-identical | #39 |
| ERC-1056 U3 tx median | 8.0 ms | 18.1 ms | #39 |
| R1 read | 0.9 ms | 2.0 ms | #39 |
| R3 at h = 50, ERC-1056 | 112 RPC, ≈65-71 ms (#31, merged run) | 203 / 238 ms (pre-merge run) | #31, #39 |
| R3 at h = 50, ERC-1155 | 3 RPC | 5.3 / 6.4 ms | #39; `HANDOFF-DATA-COLLECTION-FRAMEWORK.md:200-201` |
| throughput | 78-202 tx/s | 43-98 tx/s | #39 |

#39 is **U** because it measured the pre-merge contracts (run `2026-10-04T22-09-23Z_c3b7cb1`); re-run is
WM-2 step A6. Its structural result (event-log substrates need O(h) RPC calls) is restated by #36. The
handoff's conclusion that resolution at message time is excluded "by their own read-path structure, not
by the network" (`HANDOFF-DATA-COLLECTION-FRAMEWORK.md:205`) is the one Phase 1 statement that bears on
substrate choice for reads. Do not combine #31 and #39 in one table without the run ids (§5.F rules).

## 3. What the repository says about private chains and other databases

| # | Where | What it says | Kind |
|---|---|---|---|
| 1 | `docs/DID_METHOD_RUBRIC.md:19-33` | all nine standards are contracts on one ledger; ledger-level criteria are "answered once for Ethereum L1 / a chosen L2" and do not discriminate | design observation, a stated finding |
| 2 | `docs/DID_METHOD_RUBRIC.md:42`, `:72`, `:82-85` | ERC-1155 and LSP8 are "permissioned" (one writing authority), "a different trust model from the open substrates" to weigh in chapter 6 | contract-level permissioning, not a permissioned ledger |
| 3 | `docs/DID_METHOD_RUBRIC.md:88-95` | ledger-level envelope "to be written once for the deployment target (Ethereum L1 vs an L2)"; "Status: to assess" | open item, never done |
| 4 | `docs/DID_METHOD_RUBRIC.md:45`, `:47` | 3.2.4 "ETH for gas on every write"; 3.2.6 "bounded by ledger throughput" tied to SC-05 | public-chain assumption, unmeasured |
| 5 | `cv2x-testbed/V2_DESIGN.md:382-392` | backend list: Sepolia, Mumbai, BSC testnet, Polygon, Optimism and Arbitrum (rollups), "Private Chains: Hyperledger Besu, Quorum" | 2025 design aspiration; only Hardhat and the Sepolia harness exist |
| 6 | `cv2x-testbed/V2_DESIGN.md:413`, `:427-428` | "Off-chain storage (IPFS) integration"; "Mode 4: Federated DID (consortium blockchain)", "Mode 5: Layer 2 DID (rollup-based)" | design aspiration, not built; SC-03 demoted the V2 hybrid questions to future work (`docs/SCOPE_CHANGES.md:14`) |
| 7 | `MOBI_VID1_TECHNICAL_SPEC.md:63` | blockchain layer "Ethereum / Polygon / BSC / Private Chain" (spec dated 2025-11-10, "DESIGN PHASE", `:4-6`) | design aspiration |
| 8 | `MOBI_VID1_TECHNICAL_SPEC.md:108`, `:512-513` | certificate of origin as `ipfs://` URI; `_store_on_ipfs` | design pseudocode; `_store_on_ipfs` exists in no Python file (grep) |
| 9 | `MOBI_VID_RESEARCH.md:333-335`, `:345-347` | "Store hashes/merkle roots on-chain, full data on IPFS/Arweave"; multi-chain via chain id in the DID and a cross-chain resolver | research note (2025), not implemented |
| 10 | `MOBI_VID_RESEARCH.md:59` | Hyperledger and IOTA listed among MOBI members | context only |
| 11 | contracts: `CVINVehicleNFT.sol:19`, `:109`, `:195`; `CVINVehicleCredential1155.sol:83`; `MOBIVIDRegistryV2.sol:76` (both copies) | IPFS URIs as metadata strings; `dataHash` commented "IPFS hash of detailed event data" | field naming only; the testbed writes SHA-256 of the JSON body (`lifecycle_backends.py:191-195`) |
| 12 | `docs/thesis/chapter4-implementation/README.md:209-211` | content-hash anchoring of the VC, "no IPFS anywhere" | design choice (rejects content-addressed storage implicitly; no reason recorded) |
| 13 | `cv2x-testbed/identity/centralized_vehicle_registry.py:1-21`, `:151-165` | the baseline is an in-memory database "simulating PostgreSQL/MySQL" with a "RESTful API (simulated)" and a list of advantages and disadvantages | design choice: control/baseline; the database is not real |
| 14 | `cv2x-testbed/results/pki_vs_erc1056.md:106`; `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py:674` | "public or consortium network": writes take a block interval or more plus confirmation depth | caveat on M1 latency |
| 15 | `docs/THREAT_MODEL.md:40-41`, `:46-47` | chain integrity trusted, "standard L1/consortium assumption"; consensus attacks out of scope | trust assumption |
| 16 | `docs/RESEARCH_AUDIT.md:71-77` | gas is relative on-chain work; option (b) a fee-scenario model "L1 vs an L2 vs a consortium chain" as an appendix | audit recommendation, not done |
| 17 | `docs/AUDIT_01_ORIGINAL_GOALS.md:272-276`, `:353` | BLOCKBENCH ("Analyzing Private Blockchains") cited for throughput/latency/fault-tolerance as distinct dimensions; measure TPS or drop it from RQ1 | audit input to SC-05 (pending) |
| 18 | `docs/thesis/chapter2-literature-review/README.md:1-16` | stub; planned sections cover the nine ERC standards and the PKI baseline only | no ledger-type or database literature planned |
| 19 | `COMPOSITION.md:45-47` | the cheapest identities are "the most Sybil-exposed (permissionless self-registration)" | links openness of write access to Sybil cost (contract level) |
| 20 | `1_blockchain-identity/results/metrics/latest/meta.json` `derivedCostParams` | `gasPriceGweiL1` 20, `gasPriceGweiL2` 0.05, `ethUSD` 3000 | illustration only (`docs/MEASUREMENT_CONDITIONS.md:215`); undated, not a measurement |
| 21 | `docs/phase2/IDEA_REGISTER.md:83-91`; `docs/phase2/ARCHITECTURE.md:26`, `:57`; `docs/phase2/EVIDENCE_BASE.md:30` | I-03 "public-chain witness and rollup economics"; `LedgerTarget` with tags M1, HTTP, testnet, rollup; seed S-03 | Phase 2 future work; no permissioned or database arm |

The SQL and database search over the named documents found no other use: Phase 1 has no SQL engine, no
persistent store beyond the VC status registry's optional JSON file (`vc_issuer.py:112-114`) and committed
result files. Grep over `docs/thesis` for Hyperledger, Fabric, Besu, Quorum, permissioned and consortium
found nothing outside the threat-model and caveat text listed above.

## 4. Threats to validity the substrate choice creates

| Threat | What Phase 1 records | Where | Gap in the record |
|---|---|---|---|
| Local gas vs public fees | gas deterministic across EVM chains, so comparisons hold; fiat cost not claimed; Sepolia witness pending | ch. 3 §3.8 T1 `docs/thesis/chapter3-methodology/README.md:495-501`; ch. 5 `chapter5-results/README.md:550-553`; ch. 6 `chapter6-discussion/README.md:335-339`; ch. 7 `chapter7-conclusion/README.md:168-173`; #20 (E) | "identical on any EVM chain" is untested here; the harness compiles for `cancun` but executes under `osaka` (`docs/MEASUREMENT_CONDITIONS.md:191`), and the target network's hardfork is not recorded (unverified whether Sepolia would match) |
| No consensus or inclusion latency | tx latency is "client + EVM execution only, no propagation or consensus" | `docs/MEASUREMENT_CONDITIONS.md:23`, `:211`; `lifecycle_parity.md:76`; `pki_vs_erc1056.md:106` | no block-interval model; no confirmation-depth policy for revocation |
| No mempool, front-running or ordering | only that the ERC-4337 delta "excludes real-world bundler/mempool overhead" | ch. 3 `:517-523`; ch. 1 `chapter1-introduction/README.md:314` | not analysed for revocation races, ownership transfer or `*Signed` relays; the threat model excludes consensus attacks (`docs/THREAT_MODEL.md:40-41`) |
| Single-operator trust | chain integrity trusted (T1); the centralized baseline flags its own single point of failure | `docs/THREAT_MODEL.md:46-47`; `centralized_vehicle_registry.py:160-162`; `centralized_provider.py:76-77` | the M1 chain has the same single operator as the centralized registry, so Phase 1 never measures decentralisation itself |
| Public readability | one `eth_getLogs` links 60/60 pseudonyms of a delegate pool | #38; crux C7 "Is a public chain compatible with V2X pseudonymity at all?" (`docs/thesis/CRUX_REGISTER.md:175`) | no measurement of a read-restricted ledger |
| Clock vs chain time | ERC-1056 key validity uses the verifier's wall clock beyond 900 s from `validTo` | D51 (`docs/DEFECT_LOG.md:153`); register banner `docs/MEASUREMENT_CONDITIONS.md:99-103` | block-time behaviour of a public chain not modelled |
| Cross-chain replay | signed ERC-1056 digests bind registry address and nonce, not chain id | D52 (`docs/DEFECT_LOG.md:154`); seed S-07 (`docs/phase2/EVIDENCE_BASE.md:34`) | becomes live as soon as the same registry is deployed on two chains (testnet, private chain, L2) |
| Baselines are in-process | centralized and PKI figures are lower bounds; write ratios upper bounds | `lifecycle_parity.md:75`; `pki_vs_erc1056.md:105` | no networked database or CA measured |
| RPC provider dependence | Infura credential exposed on another lineage; rotation deferred | N-1 (`docs/MILESTONE_NEXT.md:17`) | M2 would add a third-party provider to the trust base; not discussed in the chapters |

**Cruxes.** C1 asks which *standard* should anchor the DID (`docs/thesis/CRUX_REGISTER.md:20`); its gaps
are the ERC-735 sentence and the H5 reconciliation (`:37-38`), and none concerns the ledger. C2 lists #39
as U evidence and its gaps are mobility and host dependence (`:58-62`). C3's gap list records that "the
I2I back-haul and the revocation registry are in-process (no propagation delay, no lookup cost)" (`:85`):
the RSU revocation result (#46) uses an in-process registry, not a chain. So no crux poses the substrate
question (chain type, operator set, fee model) as such; C1's word "substrate" means contract standard.

## 5. Gaps for F2

| Gap | Precise statement | Nearest Phase 1 artefact |
|---|---|---|
| Public chain | No M2 result exists; `sepolia_validation.json` was never committed (absent; no git history for the path). Every chapter states the run is pending. v0.9.0 is defined by a Sepolia witness (`docs/MILESTONE_NEXT.md:7`; `docs/ORIGINAL_PROMPT_AND_DIRECTION.md:134`). The harness covers 3 standards by default (`validate_sepolia.js:46`), gas only, "not a performance / latency / throughput sample" (`SEPOLIA_VALIDATION.md:16-18`). The handoff's lifecycle-per-substrate Sepolia run (`HANDOFF-DATA-COLLECTION-FRAMEWORK.md:232`) is also open | `validate_sepolia.js`; N-11 |
| Permissioned EVM chains (Besu, Quorum, a PoA consortium) | Not deployed, configured or measured. The only hooks are the PoA `extraData` middleware in three Python clients and the "consortium" caveats. Validator-set governance, permissioning of write and read access, and private transactions are not discussed in any chapter | `V2_DESIGN.md:390-392`; `mobi_vid_registry.py:99-103` |
| Non-EVM ledgers (Fabric, Indy-style ledgers, IOTA) | Absent from code, configs and chapters; Hyperledger and IOTA appear only as MOBI members (`MOBI_VID_RESEARCH.md:59`). The DID resolver supports ethr, nft, key, mobi and web only (`did_resolver.py:31-37`) | none |
| Rollups and L2 | Named in `V2_DESIGN.md:386-388`, `:428`, in the rubric's "a chosen L2" (`DID_METHOD_RUBRIC.md:25`), and as a fixed `gasPriceGweiL2` of 0.05 in `derivedCostParams`. A single L2 gas price omits the L1 data component of rollup fees (analyst note), so the derived L2 cost is not a defensible figure. Phase 2 I-03 is the only plan | `meta.json`; I-03 |
| Conventional database with an audit log | The centralized registry is mutable Python dicts with no persistence, no authentication of the caller, no append-only or hash-chained log, and no signed export. A tamper-evident database (signed append-only log, transparency log, ledger table) was neither built nor compared; the PKI provider's `ct_log` is a plain list (`centralized_provider.py:62`) | `centralized_vehicle_registry.py`; #33 |
| Content-addressed storage (IPFS, Arweave) | Only URI strings and comments; chapter 4 states "no IPFS anywhere". Off-chain payload availability, pinning, and the hash-on-chain / body-off-chain split proposed in `MOBI_VID_RESEARCH.md:335` are untested; the lifecycle backend stores the hash and discards the body (`lifecycle_backends.py:191-195`) | `MOBIVIDRegistryV2.sol:76` |
| Chain-backed resolution | The resolver synthesises `did:ethr` documents without reading the chain (#4 note; C5 gap `CRUX_REGISTER.md:133`); WM-2 C1 is to change this (`docs/MEASUREMENT_CONDITIONS.md:73`) | `did_resolver.py` |
| Ledger-level rubric envelope | "Status: to assess" (`DID_METHOD_RUBRIC.md:93`), so no criterion compares ledgers | `DID_METHOD_RUBRIC.md` §2 |
| Throughput and concurrency | No ledger throughput; only client-bound burst rates on one node (§1.3); SC-05 pending | `throughput.json`; #39 |
| Chapter coverage of #33 | the only measured database-vs-chain comparison is not cited by chapters 5 or 6 | §2.1 (d) |
| Register housekeeping | sandbox manifests cite sandbox-lineage numbers: `baseline-centralized` lists `#21`, `#30` (`sandbox/options/baseline-centralized/manifest.yaml:7-9`), where the parity row is now #33 and #21 measures `centralized_provider.py`, not the vehicle registry; `baseline-pki` lists `#29` (`baseline-pki/manifest.yaml:7-9`, register #40 "was #29"). SC-13 still says "register #30" | `docs/SCOPE_CHANGES.md:24` |

**Bottom line for F2.** Phase 1 measured one point on the substrate axis (one local EVM, one operator) and two
in-process non-chain baselines. Its cross-substrate claims are about cost *shape* (gas, RPC-call counts)
on that chain. Public-chain behaviour, permissioned ledgers, rollups, auditable databases and
content-addressed storage are unmeasured, and the thesis says so only for the public chain.
