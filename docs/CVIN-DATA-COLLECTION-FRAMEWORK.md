# CVIN Data-Collection & Comparative-Analysis Framework ("CRUD and Beyond")

**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Status:** v1.0 — methodology fixed; harness implemented for the three substrates on trunk (ERC-1056, ERC-721, ERC-725); remaining six substrates plug in through the adapter interface without changing the protocol.
**Companions:** `docs/MEASUREMENT_CONDITIONS.md` (the single source of truth for every reported number), `docs/AUDIT_01_ORIGINAL_GOALS.md` (findings F1–F10 this framework closes), `docs/RESEARCH_THRUSTS_REPORT.md` (H1–H5), `1_blockchain-identity/CVIN-SSI-ARCHITECTURE.md` §8.
**Harness:** `1_blockchain-identity/benchmarks/` — run with `npm run metrics` (see §10).

---

## 0. Purpose and stance

The thesis hypothesis (H1, RESEARCH_THRUSTS_REPORT §2) predicts that the minimal-state, event-log standard **ERC-1056** dominates rich-state standards on cost and is sufficient on compliance and security. The project's prior belief is that this is true. That is exactly why the measurement protocol must be fixed **before** the remaining standards are implemented, must be **identical for every substrate**, and must be **designed to be able to falsify H1**. A confirmatory study that cannot fail is not evidence; this document therefore specifies, for each hypothesis, the observation that would refute it (§8).

Three design rules follow from the audit (F1–F10):

1. **Only trunk-generated numbers are reportable.** Every figure in a chapter must be traceable to a `results/metrics/<run-id>/` directory produced by `npm run metrics` on a named commit. Session-log numbers are not evidence.
2. **One operation catalogue, one workload, all substrates.** The catalogue (§2) is defined at the level of *identity semantics* (create identity, rotate key, revoke credential …), and each standard supplies an adapter that realises each operation with that standard's primitives. Substrates never get a private workload.
3. **Exact where the EVM is exact, statistical where it is not.** Gas, calldata size, storage writes and log bytes are deterministic on a fixed compiler/EVM configuration and are reported as exact values. Latency and throughput are not deterministic and are reported with N, median, p95, min/max (§6).

---

## 1. What is compared

### 1.1 Substrates (the nine standards + two baselines)

| ID | Substrate | Identity model | State model | On trunk? | Adapter |
|---|---|---|---|---|---|
| `erc1056` | ERC-1056 EthereumDIDRegistry + CVINVehicleDIDRegistry, **pure did:ethr mode** (controller calls the registry directly) | address *is* the DID; single shared registry | **event log** (owner + delegate maps are the only storage) | ✅ | `adapters/erc1056.adapter.js` |
| `erc1056w` | same contracts, **wrapper-controlled mode** (controller hands ERC-1056 control to the wrapper at creation; all mutations via the wrapper, which tracks the vehicle owner) | as above | event log | ✅ | `adapters/erc1056w.adapter.js` |
| `erc721` | ERC-721 CVINVehicleNFT | token *is* the identity; one contract, many tokens | rich storage (metadata struct, transfer history array, service-record array) | ✅ | `adapters/erc721.adapter.js` |
| `erc725` | ERC-725 CVIN_DID_ERC725 (proxy/key-manager) | **one contract per identity** | storage (key map + key array) | ✅ | `adapters/erc725.adapter.js` |
| `erc735` | ERC-735 CVINVehicleClaimHolder (owner plays the ERC-734 MANAGEMENT key) | **one contract per identity**; claims = issuer-signed, owner-anchored | storage (claim struct incl. signature + data, topic index) | ✅ | `adapters/erc735.adapter.js` |
| `erc1155` | ERC-1155 CVINVehicleCredential1155 | the **vehicle address** is the identity; balances = credentials (soulbound) | storage (balances, VIN maps) | ✅ | `adapters/erc1155.adapter.js` |
| `erc725xy` | ERC-725 X+Y smart account `CVINVehicleERC725XY` (generic executor + key/value store, single owner) | **contract per identity** | storage (ERC-725Y key/value) | ✅ | `adapters/erc725xy.adapter.js` |
| `lsp8` | LSP8 representative `CVINVehicleLSP8` (single issuing authority; operators and LSP1 hooks omitted) | shared collection; bytes32 token = keccak(VIN) | storage (per-token key/value, generation-versioned) | ✅ | `adapters/lsp8.adapter.js` |
| `erc4337` | `CVINMinimalEntryPoint` + `CVINVehicleAccount` (research harness: no bundler/paymaster/deposits) | **account per identity**; owner key rotates, address stable | storage + EntryPoint indirection (U5) | ✅ | `adapters/erc4337.adapter.js` |
| `cvin` | CVIN-Combined `CVINCombinedIdentity` (thesis hybrid: ERC-1056 events + on-chain ERC-735 claims for the safety-critical subset) | address is the DID (shared contract) | event log + claim storage | ✅ | `adapters/cvin.adapter.js` |
| `pki` | **Baseline A:** IEEE 1609.2-style PKI (CA + enrollment/pseudonym certs + CRL) — `cv2x-testbed/identity/standard/pki_identity.py` | certificate | off-chain | ✅ (Python) | Python harness (§9) |
| `central` | **Baseline B:** centralised vehicle registry (database) — `cv2x-testbed/identity/centralized_vehicle_registry.py` | row | off-chain | ✅ (Python) | Python harness (§9) |

The audit's finding F2 ("hypothesis says *alternative to PKI*, no PKI number exists") is closed only when `pki` runs the same catalogue as the chain substrates. §9 specifies how the off-chain baselines are made commensurable.

### 1.2 Levels of the comparison

| Level | Question | Instrument | Output |
|---|---|---|---|
| **L1 Operation** | What does one identity operation cost? | `MetricsCollector.measureTx` | per-op exact gas/bytes/slots + latency distribution |
| **L2 Lifecycle** | What does a vehicle cost over its life? | scenario `lifecycle` (MOBI VID I + II event sequence) | lifetime gas, per-event breakdown |
| **L3 Scale** | Does cost change as the registry fills? | scenario `scale` (op cost at N = 0 / 100 / 1 000 pre-existing identities) | marginal cost curve, slope |
| **L4 Batch** | Do batch primitives help? | scenario `batch` (1 / 10 / 100 in one tx where the standard allows) | amortised per-item gas |
| **L5 Throughput** | How many identity ops per second can one node absorb? | scenario `throughput` (automine, 200 tx burst) | tx/s, gas/s |
| **L6 Read path** | What does *resolving* a DID document cost the verifier? | scenario `resolve` (RPC calls, bytes returned, wall-clock) | calls, bytes, ms distribution |
| **L7 Qualitative** | How do substrates score on the W3C DID Method Rubric? | `benchmarks/rubric/did-method-rubric.json` | rubric table (comparable to Fdhila et al. 2021) |
| **L8 Compliance** | What fraction of DID Core / VC DM normative statements does the lifted stack satisfy? | `cv2x-testbed/scripts/w3c_compliance_checker.py` (internal) + W3C DID test suite (external, open item) | % per spec |

L1–L6 are produced by the Hardhat harness described here. L7 is author-scored with written rationale per cell. L8 exists already and is referenced, not re-specified.

---

## 2. Operation catalogue (the workload)

Operations are named at the SSI-semantic level and grouped by CRUD class. Every adapter must implement every operation marked **core**; operations marked *cond.* are executed only where the standard has a native primitive, and the report cell reads `n/a (no primitive)` otherwise — an explicit, reportable finding rather than a blank.

### 2.1 Identity (DID) operations

| Op ID | Class | Semantic | Core? | ERC-1056 realisation | ERC-721 realisation | ERC-725 realisation |
|---|---|---|---|---|---|---|
| `C1_create_identity` | CREATE | Bring a new vehicle identity into existence, bound to a VIN | core | `createVehicleDID` (wrapper: VIN↔address mapping; DID itself is implicit) | `mintVehicle` (mint + metadata struct + history entry) | `new CVIN_DID_ERC725()` **contract deployment** + `addKey(vinHash)` |
| `C2_create_with_attributes` | CREATE | Create + publish the MOBI VID-I birth-certificate attribute set (VIN, make, model, year, colour, engine, mfg date, autonomy) | core | pure: `C1` + 8 × `setAttribute` by the controller (9 tx). wrapper (`erc1056w`): `createVehicleDID` + `changeOwner(did, wrapper)` + `setVehicleAttributes` (3 tx; loses meta-tx) | `mintVehicle` already stores the struct (same tx) | `C1` + 7 × `addKey` |
| `R1_resolve_owner` | READ | Who controls this identity? | core | `identityOwner(did)` (1 SLOAD) | `ownerOf(tokenId)` | `owner()` |
| `R2_resolve_by_vin` | READ | VIN → identity | core | `getDIDFromVIN` | `getTokenIdFromVIN` | off-chain index (n/a on-chain) — *cond.* |
| `R3_resolve_document` | READ | Build the full W3C DID Document | core | event-log walk: `changed[did]` → `eth_getLogs` per `previousChange` link | view calls: `ownerOf`, `vehicleMetadata`, `tokenURI`, `getTransferHistory` | `getKeys` + `getKey` × k |
| `R4_verify_delegate` | READ | Is key K currently authorised to sign for the identity? | core | `validDelegate` | `ownerOf == K` or `getApproved == K` | `getKey(K).purpose != 0` |
| `U1_rotate_controller` | UPDATE | Change the controlling key (owner) | core | `changeOwner` | `transferFrom` (ownership *is* control) | `transferOwnership` |
| `U2_add_delegate` | UPDATE | Authorise an additional signing key with expiry | core | `addDelegate(veriKey, ttl)` | `approve` (no expiry — *documented mismatch*) | `addKey(purpose=ACTION)` (no expiry) |
| `U3_set_attribute` | UPDATE | Publish / change one attribute (e.g. service endpoint) | core | `setAttribute` (event only) | `_setTokenURI` (admin) or `addServiceRecord` | `addKey` (attribute-as-key) |
| `U4_transfer_vehicle` | UPDATE | Change of legal owner (MOBI VID-II "ownership transfer") | core | `changeOwner` + `updateOwnershipMapping` (2 tx) **or** `transferVehicleOwnership` (1 tx, wrapper-controlled) | `safeTransferFrom` (history append) | `transferOwnership` |
| `U5_meta_tx` | UPDATE | Same as U3 but signed off-chain and relayed (gasless for vehicle) | cond. | `setAttributeSigned` | n/a (no primitive) | n/a (ERC-4337 substrate provides this) |
| `D1_revoke_delegate` | DELETE | Remove a signing key before expiry | core | `revokeDelegate` | `approve(0)` | `removeKey` |
| `D2_revoke_attribute` | DELETE | Retract an attribute | core | `revokeAttribute` (event) | n/a (URI overwrite only) | `removeKey` |
| `D3_deactivate_identity` | DELETE | End-of-life: identity must resolve as deactivated | core | `changeOwner(did, 0x0)`… **note:** ERC-1056 treats owner 0x0 as "self", so deactivation = attribute `deactivated=true` (documented semantic gap) | `deactivateVehicle` (flag) or `_burn` | `renounceOwnership` |

### 2.2 Credential (VC) operations

Credentials are W3C VCs issued **off-chain** by `2_w3c-ssi-layer/verifiable-credentials/` for every substrate; what differs per substrate is the **on-chain anchor** (issuer key resolution) and the **revocation mechanism**. These are the operations that make the "VC layer" comparable across chains.

| Op ID | Class | Semantic | Core? | ERC-1056 | ERC-721 | ERC-725 |
|---|---|---|---|---|---|---|
| `V1_issuer_key_anchor` | CREATE | Issuer publishes the verification key a verifier will resolve | core | `addDelegate(veriKey)` on issuer DID | issuer holds an NFT; key = `ownerOf` | `addKey(purpose=CLAIM)` |
| `V2_issue_credential` | CREATE | Sign VC off-chain (no chain tx) | core | Python VC layer (latency only) | same | same |
| `V3_anchor_status` | CREATE | Put credential status on-chain so it can be revoked | core | `setAttribute(statusListHash)` event | `addServiceRecord(uri)` | `addKey(credentialHash)` |
| `V4_verify_credential` | READ | Verifier: resolve issuer key (R3/R4) + check status + verify signature | core | `validDelegate` + status read + off-chain ECDSA | `ownerOf` + status read + ECDSA | `getKey` + status read + ECDSA |
| `V5_revoke_credential` | DELETE | Issuer revokes | core | `revokeAttribute` (event) or Status-List bit flip | `deactivate` / URI overwrite | `removeKey` |
| `V6_status_check` | READ | Is credential C revoked? | core | event walk or status-list read | view | view |

### 2.2a Realisations on the substrates added 2026-10-04

| Op | ERC-735 (`erc735`) | ERC-1155 (`erc1155`) |
|---|---|---|
| C1 | deploy `CVINVehicleClaimHolder(vin)` by the owner (1 tx, CREATE) | `registerVehicle(vehicle, vin)` by an ISSUER (mints BIRTH_CERT) |
| C2 | C1 + one manufacturer-signed `MANUFACTURER_CERT` claim carrying the ABI-encoded VID-I fields (2 tx) | **= C1**: no per-vehicle attribute store (`uri` is per credential *type*); VID-I attributes stay off-chain — a reportable gap |
| R1 | `owner()` | vehicle address if `isRegistered`, else 0x0 |
| R2 | n/a (no on-chain VIN index) | `vinHashToVehicle` |
| R3 | `owner`, `vin`, then **event-log replay** of `ClaimAdded/Changed/Removed` (claims are not enumerable on-chain) | `vehicleVIN` + `balanceOfBatch` over the 5 types + `uri` |
| R4 / U2 / D1 | n/a — no key management (the draft's ERC-734 is absent; owner is the only key) | n/a — no key management; soulbound tokens give operators no power |
| U1 / U4 | `transferOwnership` | issuer re-binds BIRTH_CERT **and every credential type held** to the new address (`issuerTransferCredential` is one type per tx → 1 + #types tx) |
| U3 | owner **self-signed** claim, topic = keccak(name), data = value (signature verified on-chain) | `issueCredential(vehicle, MAINTENANCE_BADGE, 1)` by the service centre — payload not storable |
| U5 | n/a | n/a |
| D2 | owner `removeClaim` | burn one MAINTENANCE_BADGE |
| D3 | `transferOwnership(0xdEaD)` (no deactivate primitive; claims stay readable) | burn BIRTH_CERT (deregisters, clears VIN maps) |
| V1 | n/a — the issuer key is the issuer EOA | `grantRole(ISSUER_ROLE, key)` by the admin |
| V3 | issuer signs (identity, topic = uint(credHash), data = credHash); **owner** anchors with `addClaim` | `issueCredential(vehicle, uint(credHash), 1)` by the issuer — each credential is its own token type |
| V5 | issuer `removeClaim` (sticky revocation) | issuer `revokeCredential` (burn) |
| V6 | `claimExists(issuer, topic)` | `hasCredential(vehicle, type)` |
| batch | none (sequential) | none exposed (`mintBatch` exists in ERC-1155 but the contract has no batch registration) — sequential |

Lifecycle events whose primitive a substrate lacks (2, 11, 12 for both) are recorded as `n/a` and excluded from that substrate's lifetime total, which then says "excl. k n/a".

### 2.2b Realisations on the last four substrates (2026-10-04)

| Op | ERC-725xy (`erc725xy`) | LSP8 (`lsp8`) | ERC-4337 (`erc4337`) | CVIN-Combined (`cvin`) |
|---|---|---|---|---|
| C1 | deploy account(owner) + `setData(VIN)` (2 tx) | `mintVehicle` by the authority (token = keccak(VIN)) | deploy account(entryPoint, owner) + `setAttribute(VIN)` (2 tx) | manufacturer-signed **VIN attestation claim** (topic 1) anchored by the owner (1 tx; the address is already an identity) |
| C2 | deploy + `setDataBatch` of the 8 VID-I keys (2 tx) | C1 + `setDataBatchForTokenIds` (7 keys, 1 tx) | deploy + 8 × `setAttribute` (9 tx; no batch) | C1 + manufacturer claim (topic 2) with the ABI-encoded VID-I fields (2 tx) |
| R1 | `owner()` | `tokenOwnerOf` (0x0 if burned) | `owner()` | `identityOwner` |
| R2 | n/a | `exists(keccak(vin))` → tokenId | n/a | n/a (VIN is claim data) |
| R3 | `owner` + `getDataBatch` (2 RPC) | `exists` + `getDataBatchForTokenIds` + `tokenOwnerOf` | `owner`, `guardian`, `getAttribute` × keys | `changed`-chain walk (DID events; claims do not advance it) + one `ClaimAdded` and one `ClaimRemoved` log query; validity judged against the **latest block timestamp** |
| R4 / U2 / D1 | n/a (single owner; no LSP6 key manager) | n/a (operators not implemented) | **guardian** = single recovery slot: `setGuardian(key)` / `setGuardian(0)` / `guardian()==key` — a recovery key that can install a new owner, not a signing delegate (documented stretch); rotation = one `setGuardian` | `addDelegate` / `revokeDelegate` / `validDelegate` (ERC-1056 semantics) |
| U1 / U4 | `transferOwnership` | token owner `transfer(from,to,id,force=true,"")` | `transferOwnership` | `changeOwner` |
| U3 / D2 | `setData(key, value)` / `setData(key, 0x)` | authority `setDataForTokenId` / clear | `setAttribute` / `setAttribute(key, 0x)` | event attribute / `revokeAttribute` (validTo = 0) |
| U5 | n/a | n/a | **headline path**: owner signs a `PackedUserOperation` (EIP-191 over `userOpHash`) with `callData = execute(self, 0, setAttribute(..))`; relayer calls `EntryPoint.handleOp` | n/a |
| D3 | `renounceOwnership` | authority `revokeVehicle` (burn, data generation bumped) | `transferOwnership(0xdEaD)` (no primitive) | permanent `did/deactivated` attribute (no primitive) |
| V1 | issuer's own account `setData(issuerKey)` | n/a (single authority) | issuer's own account `setAttribute(issuerKey)` | issuer `addDelegate` on its own identity |
| V3 / V5 / V6 | issuer account `setData(credHash, "active")` / `setData(credHash, 0x)` / `getData` | authority `setDataForTokenId(token, credHash, "active")` / clear / read | issuer account `setAttribute(credHash, ..)` / clear / `getAttribute` | issuer-signed claim (topic = uint(credHash), **raw-digest** signature) anchored by the owner / issuer `removeClaim` (sticky) / `hasValidClaim` (O(1)) |
| batch | `setDataBatch` (data), none for creation | `setDataBatchForTokenIds` (data), none for mint | none | none |

For `erc725xy`, `erc4337` (and `erc725` before them) the issuer's credential status lives in the issuer's own per-identity contract, deployed once as a shared cost (`prepareIssuer` deploys one per fresh issuer, unmeasured).

### 2.3 "Beyond CRUD" — per-operation dimensions recorded for every op

For each executed op, `MetricsCollector` records (exact unless marked ~):

| Field | Meaning | Source |
|---|---|---|
| `gasUsed` | execution gas of the tx | receipt |
| `gasIntrinsic` | 21 000 + calldata gas (4/16 per byte) | computed from calldata |
| `gasExecution` | `gasUsed − gasIntrinsic` | derived |
| `calldataBytes` | bytes of tx input | tx |
| `logBytes` | Σ over logs (32 × topics + data length) | receipt |
| `logCount` | number of events | receipt |
| `sstoreCount` / `sloadCount` | storage writes / reads executed | `debug_traceTransaction` opcode count |
| `newSlotsEstimate` | writes that turned a zero slot non-zero (20 000-gas class) | trace: `SSTORE` with prior value 0 (when storage tracing enabled) |
| `txCount` | number of transactions the semantic op needed (e.g. U4 on ERC-1056 = 2) | adapter |
| `latencyMs` ~ | wall-clock from `send` to receipt on local node | harness clock; N repetitions |
| `bytecodeBytes` / `deployGas` | size and deployment cost of the contract(s) the substrate needs (charged once for shared registries, **per identity** for contract-per-identity standards) | deploy receipt |
| `stateFootprintBytes` | persistent storage the identity leaves behind: `newSlots × 32` | derived |
| `readRpcCalls` / `readBytes` | for READ ops: JSON-RPC calls made and bytes returned to build the answer | provider wrapper |

Derived, parameterised (not measured — parameters are printed in the report header):

- `costUSD = gasUsed × gasPriceGwei × 1e-9 × ethUSD` for a stated `(gasPriceGwei, ethUSD)` pair, and for an L2 pair (`gasPriceGwei_L2`). Defaults: 20 gwei / 0.05 gwei, ETH = 3 000 USD. These are illustration, not results.
- `lifetimeGas = C2 + k·U3 + m·U4 + n·V3 + n·V5 + D3` under the MOBI VID-II event mix (§4.4).

---

## 3. Measurement conditions (normative; mirrored in `docs/MEASUREMENT_CONDITIONS.md`)

| Parameter | Value | Why it matters |
|---|---|---|
| Node | Hardhat Network in-process, `chainId 31337`, automine | deterministic gas; zero network latency ⇒ latency figures measure *client + EVM execution*, not propagation |
| Compiler | solc **0.8.24**, optimizer on, `runs = 200`, `viaIR = true`, `evmVersion = cancun` | gas is a function of these; changing any invalidates comparison |
| Block gas limit | 30 000 000 | bounds batch scenario |
| Base fee / gas price | Hardhat default (irrelevant to `gasUsed`; relevant only to derived USD) | |
| Accounts | Hardhat default 20 accounts; roles fixed: `[deployer, manufacturer, vehicleOwner, newOwner, issuer, verifier, serviceCenter, attacker]` | identical actors for every substrate |
| Dataset | `benchmarks/lib/dataset.js`: 1 000 syntactically valid 17-char VINs (deterministic PRNG seed 42), fixed make/model/colour tables, fixed attribute payload sizes (endpoint URL 64 B, credential hash 32 B) | payload size drives calldata & log gas; must be equal across substrates |
| Repetitions | exact metrics: 1 (deterministic; harness asserts run-to-run equality); latency: **N = 30** per op; throughput: 3 bursts × 200 tx | F8 |
| Warm-up | 5 discarded executions before latency sampling | JIT / provider warm-up |
| Clock | `process.hrtime.bigint()` | ns resolution |
| Trace | `debug_traceTransaction` with `disableMemory, disableStack` = true; `disableStorage` = false only for `newSlotsEstimate` | cost of tracing does not affect measured gas |
| Run identity | `results/metrics/<UTC-timestamp>_<short-sha>/` containing `meta.json` (commit, dirty flag, node/solc versions, this table) | traceability (F3) |

Anything measured under different conditions must be labelled with its own conditions block and **must not** be placed in the same table as trunk results.

---

## 4. Scenarios

### 4.1 `crud` — L1 baseline (fresh state)
For each substrate, for each core op: deploy fresh, execute the op once for exact metrics, then N = 30 more times (fresh identity each time where the op is not idempotent) for latency. Output: one row per (substrate, op).

### 4.2 `batch` — L4
Where the standard has a batch primitive (ERC-1155 `mintBatch`, ERC-725xy `setDataBatch`, LSP8 `transferBatch`, multicall on CVIN-Combined), execute the op for batch sizes {1, 10, 100} in one tx and report amortised gas per item. Substrates without a primitive are run as 1/10/100 *sequential* txs so the table still has a comparable "cost of 100" column, flagged `sequential`.

### 4.3 `scale` — L3
Pre-populate the registry with N ∈ {0, 100, 1 000} identities (dataset VINs 0..N-1), then measure the *marginal* cost of `C2`, `U3`, `U4`, `R3`. Hypothesis-relevant: mapping-based storage is O(1); array-scanning code (e.g. `removeKey`'s linear scan in ERC-725, `getOwnershipChain` in ERC-721) is O(k) in *per-identity* history, so the scale axis also varies per-identity history length h ∈ {1, 10, 50} for `U4` and `R3`.

### 4.4 `lifecycle` — L2 (MOBI VID I + II)
One vehicle, the canonical event sequence, on every substrate:

| # | MOBI VID event | Catalogue op | Actor |
|---|---|---|---|
| 1 | VID-I birth certificate | `C2` | manufacturer |
| 2 | Issuer key anchor (registration authority) | `V1` | issuer |
| 3 | Registration credential issued + anchored | `V2` + `V3` | issuer |
| 4 | Insurance credential anchored | `V3` | issuer |
| 5 | Service endpoint published (telematics) | `U3` | owner |
| 6–10 | 5 × service/maintenance record | `U3` / `addServiceRecord` | service centre |
| 11 | Key rotation (device replacement) | `U2` + `D1` | owner |
| 12 | Ownership transfer (resale) | `U4` | owner → newOwner |
| 13 | Re-registration credential | `V3` | issuer |
| 14 | Credential revocation (old insurance) | `V5` | issuer |
| 15 | Second ownership transfer | `U4` | newOwner → third |
| 16 | End-of-life | `D3` | admin/owner |

Output: per-event gas and the **lifetime total**, plus the substrate's fixed cost (deploy) apportioned as `deployGas / assumedFleet` for fleet ∈ {1, 1 000, 1 000 000} — the number that decides whether contract-per-identity standards can ever be competitive.

### 4.5 `throughput` — L5
Automine on; fire 200 `U3` txs from 10 distinct senders (20 each, sequential nonces) as fast as the provider accepts; measure wall-clock for the burst → tx/s and gas/s. Report 3 bursts, median. This is a **node-bound** upper bound on a single local node and is labelled as such; it is *not* a public-chain throughput claim.

### 4.6 `resolve` — L6 (read path, verifier-side)
For each substrate, after the `lifecycle` sequence (so history is realistic), build the DID Document via the adapter's `resolveDocument()` and record `readRpcCalls`, `readBytes`, `latencyMs` (N = 30). For ERC-1056 this is the `changed`/`previousChange` linked-list walk over `eth_getLogs`; the number of hops equals the number of on-chain changes — the honest cost of the event-log model.

---

## 5. Adapter interface (`benchmarks/adapters/IdentityAdapter.js`)

Each substrate implements:

```js
class IdentityAdapter {
  static id;                    // 'erc1056'
  static label;                 // 'ERC-1056 (EthereumDIDRegistry)'
  async deploy(actors)          // deploy shared contracts; returns {contracts, deployReceipts}
  async createIdentity(vin, owner)                 // C1  → {txs:[tx...], handle}
  async createIdentityWithAttributes(vin, owner, a) // C2
  async resolveOwner(handle)                        // R1  → value (view)
  async resolveByVin(vin)                           // R2
  async resolveDocument(handle)                     // R3  → {document, rpcCalls, bytes}
  async verifyDelegate(handle, key)                 // R4
  async rotateController(handle, newOwner)          // U1
  async addDelegate(handle, key, ttl)               // U2
  async setAttribute(handle, name, value)           // U3
  async transferVehicle(handle, from, to)           // U4
  async metaTxSetAttribute(handle, signer, relayer) // U5 | throws NotSupported
  async revokeDelegate(handle, key)                 // D1
  async revokeAttribute(handle, name)               // D2
  async deactivate(handle)                          // D3
  async anchorIssuerKey(issuer, key)                // V1
  async anchorStatus(handle, credHash)              // V3
  async revokeCredential(handle, credHash)          // V5
  async statusCheck(handle, credHash)               // V6
  supports(opId)                                    // boolean → n/a cells
}
```

Mutating methods return `{ txs: [TransactionResponse...] }`; the collector measures every tx and sums, recording `txCount`. View methods are wrapped by a counting provider so `readRpcCalls`/`readBytes` are captured without adapter code knowing.

A substrate is "in the study" when its adapter passes `benchmarks/adapters/conformance.test.js` — a test that every core op executes and leaves the identity in the expected state. This is the gate the audit's F4 asks for, expressed as code.

---

## 6. Statistics and reporting rules

- **Exact metrics** (gas, bytes, slots, counts): report the single value; the harness re-executes the op on a fresh chain and asserts equality — a mismatch fails the run (guards against hidden nondeterminism such as timestamp-dependent branches).
- **Latency / throughput**: report `n, median, p95, min, max, mean, sd`. Use median for headline, p95 for the V2V budget argument (T3). No confidence-interval claims on N = 30 without stating the distribution; if a CI is wanted, bootstrap (10 000 resamples) — implemented in `lib/stats.js`.
- **Comparisons between substrates** on exact metrics need no test: a difference in gas is a fact of the code. Comparisons on latency use the Mann–Whitney U (non-parametric; latencies are skewed) — `lib/stats.js#mannWhitneyU`.
- **Ratios** ("ERC-1056 is k× cheaper") are computed from the exact values and quoted with the op ID, e.g. `C2: 78 068 vs 102 804 → 1.32×`. Never quote a ratio without the op.
- Each table carries a footer: run-id, commit, conditions hash.

---

## 6a. Analysis layer (`npm run metrics:analyze`)

`1_blockchain-identity/analysis/analysis.js` (outside `benchmarks/`, so it is not part of the measured code whose hashes identify a run, §5.F of the conditions) is a pure function of a run directory and writes `ANALYSIS.md`, `analysis.json` and `tables/analysis_*.{md,csv,tex}`:

- **A1 ratios** — each substrate's C1/C2/U3/U4/V3/V5 gas, lifetime gas, zero→nonzero SSTOREs and transaction count as a multiple of the ERC-1056 baseline; `†` marks lifetime totals that exclude `n/a` events (lower bounds, not like-for-like).
- **A2 capability matrix** — ✓/✗ per catalogue op per substrate from the `supported` flags, with the count of core ops supported. A ✗ is a property of the standard's primitives (or of the representative implementation, stated in §2.2a/b), and a finding in its own right.
- **A3 dominance (H5)** — six criteria: lifetime gas ↓, zero→nonzero SSTOREs ↓, R3 RPC calls at the largest measured history ↓, R3 median ms after the lifecycle ↓, core ops supported ↑, O(1) on-chain credential check ↑. The last is a design property assigned per adapter (storage-based substrates and the hybrid: yes; event-log substrates: no) and is declared with the table. A substrate is *dominated* on a criterion set if another is at least as good on every criterion in the set and strictly better on one; the table lists who dominates whom for three sets (cost only; cost + read path; all six) and A4 names the Pareto frontier for each.

Rules: the analysis never re-measures; it reads the run of record. Because dominance on "cost only" with ERC-1155's lower-bound lifetime (†) would overstate ERC-1155, A4 lists which substrates have full-coverage totals; the thesis compares frontier membership on the full-coverage subset first.

## 7. Qualitative axis — W3C DID Method Rubric

To be comparable with Fdhila et al. (2021) and Schäffner, each substrate is scored on the W3C DID Method Rubric criteria used by those works. `benchmarks/rubric/did-method-rubric.json` holds, per criterion, per substrate: `score`, `evidence` (a file/line or a measured value), `assessor`, `date`. Criteria (rubric §§ as named in the W3C document): rulemaking, enforcement, open contribution, open participation, security (key rotation, deactivation, DID-doc integrity), privacy (correlation, DID-doc PII, herd privacy), interoperability (DID Core conformance, resolver availability), scalability (throughput, storage), cost (transaction cost per op — **this is where L1 numbers enter**), decentralisation of operation, sustainability.

Rule: a rubric cell may cite a measured number (L1–L6) or a file line; it may not cite a session summary.

---

## 8. Hypotheses → measurements → falsifiers

| Hyp. | Claim (from thrusts report) | Measurement that tests it | **Observation that refutes it** |
|---|---|---|---|
| H1 | ERC-1056 ≥ 10× cheaper than rich-state standards for create/update | `crud` C2, U3, U4 exact gas; `lifecycle` total | Any rich-state substrate within 10× on the *lifetime* total, or ERC-1056 not the minimum on C2 **and** U3 |
| H1' (scale) | ERC-1056 marginal cost is flat in N and h | `scale` slopes | Positive slope for ERC-1056 in N or h |
| H3 | Off-chain VC verification with pre-resolved keys fits the 100 ms J2945/1 budget; on-chain read at message time does not | `resolve` p95 + Python `V4` p95 | p95(resolve) < 100 ms on a *remote* RPC would weaken the second half; p95(V4 off-chain) ≥ 100 ms refutes the first |
| H4 | Event-log standards are cheapest for VID-II events; claim-based most faithful | `lifecycle` per-event gas; rubric "fidelity" column | Claim-based substrate cheaper on ≥ 8/16 events |
| H5 | No single standard dominates; the hybrid is Pareto-optimal | Pareto set over (lifetime gas, rubric security, rubric privacy, resolve p95) | A single non-hybrid substrate dominating on all four |
| PKI | ERC-1056 stack is a viable alternative to PKI | Python harness: identical catalogue on `pki` vs `erc1056` (§9) | ERC-1056 worse on *every* dimension (cost, verify latency, revocation propagation) |

---

## 9. Off-chain baselines (PKI, centralised) — commensurability

The Python providers already implement `register_vehicle / sign / verify / revoke / check_revocation / resolve` (`cv2x-testbed/identity/base.py`). They are mapped onto the catalogue as: `C2→register_vehicle`, `V2→sign_message`, `V4→verify_message`, `V5→revoke_credential`, `V6→check_revocation_status`, `R3→resolve_identity`. Gas is undefined off-chain; the commensurable dimensions are **latency (ms, N = 30)**, **bytes on the wire** (certificate/VC + signature size — `comparison_framework.measure_sizes`), **revocation propagation** (time from revoke to first negative status answer) and **infrastructure assumption** (CA online? database online?), the last recorded as a categorical column. Script to produce the single CSV the audit asks for: `cv2x-testbed/scripts/benchmark_pki_vs_erc1056.py` (next step; it needs a running Hardhat node — `npm run node` — because `erc1056_provider.py` speaks JSON-RPC).

---

## 10. Running the harness and reading the output

```bash
cd 1_blockchain-identity
npm install
npm run metrics                 # all scenarios, all adapters → results/metrics/<run-id>/
npm run metrics -- --scenarios crud,lifecycle --adapters erc1056,erc721
npm run metrics:report          # regenerate comparison tables from the latest run
```

Output tree per run:

```
results/metrics/<run-id>/
  meta.json            # commit, dirty flag, versions, conditions (§3)
  raw.jsonl            # one line per measured tx / view, all fields of §2.3
  crud.json            # per (substrate, op) aggregated rows
  lifecycle.json
  scale.json
  batch.json
  throughput.json
  resolve.json
  tables/
    crud.md            # 9-column comparison matrix (n/a cells explicit)
    crud.csv
    crud.tex           # booktabs table for the thesis
    lifecycle.md/.csv/.tex
    ...
results/metrics/latest -> <run-id>   (symlink; the only run chapters may cite)
```

`results/metrics/latest/**` is committed so the numbers the thesis cites are in git; older runs are kept locally and are not committed.

---

## 11. Threats to validity (pre-registered, per §5 of the audit)

| Type | Threat | Control in the design |
|---|---|---|
| Construct | "Cost" measured as gas only, ignoring L2 vs L1 price | gas is the invariant; USD is a labelled derived column with explicit parameters |
| Construct | Latency on an in-process node is not V2X latency | reported as *client+EVM* latency; the V2V budget argument uses the off-chain V4 path. A second labelled condition (`M1-H/HTTP`: same harness over `npx hardhat node` on localhost, `METRICS_OUT=results/metrics-rpc --network localhost`) gives the lower bound of RPC-mediated latency; gas must be identical between the two, which is checked. Neither is a WAN figure |
| Internal | Adapters could favour one standard by choosing cheap paths | catalogue fixed first; each adapter's realisation is listed in §2 and reviewable; conformance test enforces semantics |
| Internal | Compiler settings differ by contract | one config for all; `meta.json` records it; run fails if a contract compiled with a different setting is loaded |
| Internal | Warm cache / JIT | warm-up discarded; latencies are within-run only |
| External | Only 3 of 9 substrates on trunk today | tables print `not implemented` cells; no nine-standard claim is made until all adapters pass conformance |
| External | Hardhat ≠ mainnet EVM | Cancun EVM parity; gas is EVM-defined; a Sepolia confirmation run is a stated future item |
| Conclusion | Small N for latency | N = 30 with median/p95, non-parametric test, bootstrap CI available |

---

## 12. Scope-change log (audit F10)

| Date | Change | Reason |
|---|---|---|
| 2026-09-30 | Privacy analysis re-scoped from quantitative (k-anonymity, ε) to rubric-scored + measured `logBytes`/PII-on-chain inventory | no ground-truth population to compute k-anonymity against; PII-on-chain inventory (which attributes each substrate emits in clear) is measurable and directly decision-relevant |
| 2026-09-30 | Position-falsification detection remains out of scope | misbehaviour detection is a separate research area (SCMS MA); identity substrate does not affect it |
| 2026-09-30 | Throughput defined as single-node automine tx/s | public-chain throughput is a property of the chain, not the standard; the single-node figure isolates the standard's execution cost |

---

## 13. Deliverables checklist

- [x] Methodology fixed (this document)
- [x] `MEASUREMENT_CONDITIONS.md`
- [x] Harness: collector, stats, exporters, dataset, adapter interface
- [x] Adapters: ERC-1056 (pure), ERC-1056 (wrapper), ERC-721, ERC-725 (+ conformance test)
- [x] Scenarios: crud, lifecycle, scale, batch, throughput, resolve
- [x] First trunk-traceable run committed under `results/metrics/latest`
- [x] Adapters: ERC-735, ERC-1155 (contracts from the review-02 trunk; conformance green; §2.2a)
- [x] Adapters: ERC-725xy, LSP8, ERC-4337, CVIN-Combined (§2.2b) — all nine standards (ten columns with the ERC-1056 wrapper variant) now run the same catalogue
- [ ] Python: `benchmark_pki_vs_erc1056.py` (closes F2)
- [ ] Rubric scored for all substrates with evidence cells
- [ ] External W3C DID test-suite run (closes F5)
- [ ] Sepolia confirmation run (one lifecycle per substrate)
