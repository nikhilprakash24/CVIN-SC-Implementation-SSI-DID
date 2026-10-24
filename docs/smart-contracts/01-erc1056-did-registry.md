# 01: ERC-1056 DID Registry (EthereumDIDRegistry / did:ethr) and the CVIN VIN wrapper

This group holds the repo's ERC-1056 "Lightweight Identity" option. `EthereumDIDRegistry` is a near-verbatim Solidity 0.8 port of the uPort/Veramo `ethr-did-registry`. It is one shared contract for every identity. Any Ethereum address is already a DID (`did:ethr:<address>`), and owner, delegate and attribute changes are stored as events, not as contract storage. Off-chain resolvers rebuild a W3C DID Document by walking the `changed[]` → `previousChange` event chain. `CVINVehicleDIDRegistry` is a CVIN-specific wrapper on top of it. It adds a manufacturer-gated VIN↔DID mapping, the vehicle attribute keys (VID-I), and an optional "wrapper-controlled" mode. In that mode the vehicle owner hands ERC-1056 control of the DID to the wrapper, and the wrapper then tracks the vehicle owner itself. The Python resolver `2_w3c-ssi-layer/did-resolution/did_resolver.py` implements did:ethr resolution in line with DID Core against a deployed `EthereumDIDRegistry`.

Files:
- `1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol` (408 lines)
- `1_blockchain-identity/contracts/ERC1056/CVINVehicleDIDRegistry.sol` (421 lines)
- `2_w3c-ssi-layer/did-resolution/did_resolver.py` (related, resolution side)

---

## Standards & protocols

### ERC-1056: Ethereum Lightweight Identity
- **What it is:** EIP issue #1056 (Pelle Braendgaard / uPort, 2018). It was never merged as a final EIP and lives as a GitHub issue plus the reference implementation `uport-project/ethr-did-registry` (now `decentralized-identity/ethr-did-registry`). It is a single shared registry for key management of existing accounts, so identity creation costs nothing, keys can be delegated with expiry, and attributes are published as events.
- **Canonical interface:** `identityOwner(address)`, `validDelegate(address,bytes32,address)`, `changeOwner`, `changeOwnerSigned`, `addDelegate`, `addDelegateSigned`, `revokeDelegate`, `revokeDelegateSigned`, `setAttribute`, `setAttributeSigned`, `revokeAttribute`, `revokeAttributeSigned`; public mappings `owners`, `delegates`, `changed`, `nonce`; events `DIDOwnerChanged(identity indexed, owner, previousChange)`, `DIDDelegateChanged(identity indexed, delegateType, delegate, validTo, previousChange)`, `DIDAttributeChanged(identity indexed, name, value, validTo, previousChange)`.
- **How faithful this repo is:** the full public surface, the event signatures and the signed-message digest layout match upstream.
  - Signed digest: `keccak256(0x19 ‖ 0x00 ‖ address(this) ‖ nonce[identityOwner(identity)] ‖ identity ‖ "<fnName>" ‖ args…)`, recovered with raw `ecrecover` (`EthereumDIDRegistry.sol:160-173`, `:220-235`, `:283-297`, `:337-351`, `:387-401`). This is the upstream "EIP-191 version 0x00, intended validator" form. It is **not** EIP-712 and does **not** bind `block.chainid`, so the same signature can be replayed across chains if the registry has the same address on each. `scripts/security_scenarios.js:144` records this caveat.
  - Deviations from upstream:
    1. Revert strings are `"DIDRegistry: unauthorized"` / `"DIDRegistry: invalid signature"`. Upstream uses `"bad_actor"` / `"bad_signature"`.
    2. Upstream factors the logic into internal `changeOwner(identity, actor, newOwner)` style helpers plus `checkSignature`. Here each `*Signed` function inlines the hash and the state change, which duplicates code.
    3. `setAttributeSigned` and `revokeAttributeSigned` write `changed[identity]` *before* emitting, using a cached `previousChange` (`:356-358`, `:404-406`). The unsigned versions emit first. The observable result is the same.
    4. There is no `onlyOwner` custom error and no `ecrecover` zero-address check. A zero signer can never match `identityOwner`, because that function never returns 0 except when the owner was explicitly set to 0 (see the deactivation caveat below).
  - Comment drift: the header claims "minimal gas costs (events only, no storage for attributes)". That is true for attributes, but delegates do use storage (`delegates` mapping, `:79-80`).

### did:ethr DID method (DIF `ethr-did-resolver` spec)
- DID syntax: `did:ethr:[<network|chainId>:]<0x address | compressed pubkey>`. The DID Document is derived from registry events:
  - the owner becomes `#controller` (`EcdsaSecp256k1RecoveryMethod2020`, `blockchainAccountId eip155:<chain>:<owner>`);
  - `veriKey` / `sigAuth` delegates become `#delegate-N`;
  - attributes named `did/pub/<alg>/<purpose>/<encoding>` become verification methods, and `did/svc/<type>` become services;
  - setting the owner to `0x0` deactivates the DID.
- **Spec requires attribute names / delegate types to be bytes32 *right-padded ASCII strings*** (e.g. `stringToBytes32("did/svc/MessagingService")`). **Deviation:** `CVINVehicleDIDRegistry` defines every key as `keccak256("did/...")` (`CVINVehicleDIDRegistry.sol:44-70`), and the sandbox adapter also hashes names (`addDelegate(identity, keccak256(purpose), …)`, `setAttribute(identity, keccak256(name), …)`). A spec-conformant did:ethr resolver cannot decode hashed names back into `did/svc/...` / `did/pub/...`, and cannot recognise `keccak256("veriKey")` as `veriKey`. These attributes and delegates therefore do **not** show up in a standard did:ethr DID Document; only the raw events record them. The repo's Python resolver decodes names with `_bytes32_to_str` (`did_resolver.py:401`), so it only maps names that were written as padded ASCII.

### W3C DID Core v1.0 and DID Resolution
- DID Core (W3C Recommendation, July 2022) defines the DID Document data model (`id`, `verificationMethod`, `authentication`, `assertionMethod`, `service`, …) and the `resolve()` / `resolveRepresentation()` contract, which returns `didResolutionMetadata`, `didDocument` and `didDocumentMetadata`, with error codes `invalidDid`, `notFound` and `representationNotSupported`. The DID Resolution spec is still a W3C CCG/WG draft.
- `did_resolver.py` implements both functions: `DIDResolver.resolve` (`:783`) and `resolve_representation` (`:869`). The result classes are at `:171-257`.
  - **On-chain mode:** you pass `rpc_url` plus `ethr_registry`. `ERC1056Reader` (`:421`) then:
    - reads the head `changed[identity]`;
    - walks backwards through `previousChange` values that point strictly to earlier blocks (`:484-489`);
    - replays the events forward, keyed like ethr-did-resolver's `eventIndex` (`:497`), and treats an owner of `0x0` as deactivated (`:510-513`).

    `erc1056_document` (`:567`) builds `#controller`, `#controllerKey` (when a key is supplied), `#delegate-N` and `#service-N`. `versionId` is the last change block, and `deactivated` is set in metadata (`:578-584`). On-chain mode fails closed: an RPC or consistency failure returns `internalError`, and a DID for another chain returns `notFound`. Results carry the non-standard metadata `cvinResolutionMode: "erc1056-registry"`.
  - **Offline mode (default):** the document is synthesised from the DID string alone, with `cvinResolutionMode: "offline-synthesized"`. It is not a registry read.
  - `parse_chain_id` (`:283`) accepts ethr-did-resolver network names and maps them to EIP-155 chain ids.
  - `_resolve_mobi_onchain` (`:1198`) reuses the same ERC-1056 reader for `did:mobi`, putting the did:ethr into `alsoKnownAs`.

### ERC-191 / meta-transactions
The `*Signed` entry points let a relayer submit operations for the identity owner. `nonce` is per **signer** (`nonce[signer]++`), and the digest reads it as `nonce[identityOwner(identity)]`. That means one owner who controls several identities shares one nonce across all of them, the same as upstream.

---

## Contract: `EthereumDIDRegistry` (`1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol`)

**Purpose:** a shared ERC-1056 registry for did:ethr. **Inheritance/imports:** none. Pragma `^0.8.20`.

### State variables
| Name | Type | Line | Meaning |
|---|---|---|---|
| `owners` | `mapping(address=>address)` public | 71 | Explicit owner; `0` means "self" (see `identityOwner`) |
| `changed` | `mapping(address=>uint)` public | 74 | Block number of the identity's last change (head of the event chain) |
| `nonce` | `mapping(address=>uint)` public | 77 | Meta-tx nonce per signer/owner |
| `delegates` | `mapping(address=>mapping(bytes32=>mapping(address=>uint)))` public | 80-81 | `validTo` timestamp per (identity, type, delegate) |

### Events
`DIDOwnerChanged(address indexed identity, address owner, uint previousChange)` (`:30`); `DIDDelegateChanged(address indexed identity, bytes32 delegateType, address delegate, uint validTo, uint previousChange)` (`:44`); `DIDAttributeChanged(address indexed identity, bytes32 name, bytes value, uint validTo, uint previousChange)` (`:60`). A `validTo` of 0 means revoked.

### Modifiers
`onlyOwner(address identity, address actor)` (`:90`) requires `actor == identityOwner(identity)`.

### Functions
| Signature | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `identityOwner(address identity) returns (address)` (`:105`) | public view | Returns `owners[identity]`, or `identity` if unset | anyone | none | ERC-1056 |
| `validDelegate(address,bytes32,address) returns (bool)` (`:120`) | public view | `delegates[..] > block.timestamp` | anyone | none | ERC-1056 |
| `changeOwner(address identity, address newOwner)` (`:136`) | public | Sets `owners[identity]`, then updates `changed` | `onlyOwner` | `DIDOwnerChanged` | ERC-1056 |
| `changeOwnerSigned(identity, v, r, s, newOwner)` (`:153`) | public | Same as above, authorised by the owner's signature; `nonce[signer]++` | signature from current owner (any relayer) | `DIDOwnerChanged` | ERC-1056 |
| `addDelegate(identity, delegateType, delegate, validity)` (`:190`) | public | `delegates[...] = block.timestamp + validity` | `onlyOwner` | `DIDDelegateChanged` | ERC-1056 |
| `addDelegateSigned(identity, v, r, s, delegateType, delegate, validity)` (`:211`) | public | Signed version | owner signature | `DIDDelegateChanged` | ERC-1056 |
| `revokeDelegate(identity, delegateType, delegate)` (`:256`) | public | Sets validity to 0 | `onlyOwner` | `DIDDelegateChanged` (validTo 0) | ERC-1056 |
| `revokeDelegateSigned(identity, v, r, s, delegateType, delegate)` (`:275`) | public | Signed version | owner signature | `DIDDelegateChanged` | ERC-1056 |
| `setAttribute(identity, bytes32 name, bytes value, uint validity)` (`:314`) | public | Emits only; no storage except `changed` | `onlyOwner` | `DIDAttributeChanged` | ERC-1056 |
| `setAttributeSigned(identity, v, r, s, name, value, validity)` (`:328`) | public | Signed version | owner signature | `DIDAttributeChanged` | ERC-1056 |
| `revokeAttribute(identity, name, value)` (`:367`) | public | Emits with `validTo = 0` | `onlyOwner` | `DIDAttributeChanged` | ERC-1056 |
| `revokeAttributeSigned(identity, v, r, s, name, value)` (`:379`) | public | Signed version | owner signature | `DIDAttributeChanged` | ERC-1056 |
| auto getters `owners`, `changed`, `nonce`, `delegates` | public view | mapping reads | anyone | none | ERC-1056 |

### Design notes / security caveats
- **Overflow:** `block.timestamp + validity` uses checked arithmetic, so passing `type(uint256).max` reverts with panic 0x11. This was defect D18 in the wrapper, which is why the wrapper uses a 100-year validity.
- **Cross-chain replay:** the signed digest has no `chainid`, and the nonce is shared per owner across identities.
- **Contracts cannot read attributes:** attributes exist only as events, so no contract can read an attribute value. `phase2/idtx` works around this with a commitment store (`phase2/idtx/contracts/IdtxExecutor.sol:20-21`; test `phase2/idtx/test/idtx.test.js:138`).
- **Irreversible deactivation:** `changeOwner(identity, address(0))` permanently "deactivates" the DID per did:ethr. After that, `identityOwner` returns `identity` again, because the `owners` value is 0. In practice the original key regains control on-chain while resolvers treat the DID as deactivated. The behaviour is inherited from upstream.
- **No identity-level revocation and no guardians/recovery.** Revocation is per delegate and per attribute.
- **Unchecked delegates:** delegates are not checked for authority on-chain except by `validDelegate`; anything that relies on them must call it.

---

## Contract: `CVINVehicleDIDRegistry` (`1_blockchain-identity/contracts/ERC1056/CVINVehicleDIDRegistry.sol`)

**Purpose:** a vehicle-identity wrapper (CVIN extension). **Imports:** `./EthereumDIDRegistry.sol`. It holds a reference to the registry and does not inherit from it.

### State variables / constants
| Name | Type | Line | Meaning |
|---|---|---|---|
| `didRegistry` | `EthereumDIDRegistry` public | 22 | Underlying registry (set in constructor) |
| `vinToDID` | `mapping(bytes32=>address)` public | 25 | `keccak256(vin)` → DID |
| `didToVIN` | `mapping(address=>string)` public | 28 | Reverse lookup (plaintext VIN on-chain) |
| `authorizedManufacturers` | `mapping(address=>bool)` public | 31 | Who may create vehicle DIDs |
| `owner` | `address` public | 34 | Admin (deployer) |
| `vehicleOwners` | `mapping(address=>address)` public | 40 | Vehicle owner while the wrapper controls the DID (`0` means the DID itself) |
| `DID_VIN`, `DID_MAKE`, `DID_MODEL`, `DID_YEAR`, `DID_COLOR`, `DID_ENGINE`, `DID_MANUFACTURING_DATE`, `DID_AUTONOMY_LEVEL` | `bytes32` constant | 44-53 | `keccak256("did/vehicle/…")` attribute keys |
| `SVC_CREDENTIAL_SERVICE`, `SVC_MESSAGING`, `SVC_TELEMETRY` | `bytes32` constant | 56-59 | `keccak256("did/svc/…")` |
| `VEHICLE_ATTRIBUTE_VALIDITY` | `uint256` constant = 100·365 days | 66 | Used by `setVehicleAttributes` |
| `DELEGATE_VERIKEY`, `DELEGATE_SIGAUTH` | `bytes32` constant | 69-70 | `keccak256("veriKey")`, `keccak256("sigAuth")` |
| `PERMANENT_ATTRIBUTE_VALIDITY` | `uint256` constant = 100·365 days | 81 | **Duplicate** of `VEHICLE_ATTRIBUTE_VALIDITY` and unused internally; the D18 regression test reads it |

### Events
`VehicleDIDCreated(address indexed did, string vin, address indexed owner, address indexed manufacturer)` (`:85`); `VehicleOwnershipTransferred(address indexed did, address indexed previousOwner, address indexed newOwner)` (`:92`); `ManufacturerAuthorized(address indexed manufacturer, bool authorized)` (`:98`).

### Modifiers
`onlyContractOwner` (`:102`); `onlyAuthorizedManufacturer` (`:107`); `onlyVehicleOwner(did)` (`:115`), which requires `msg.sender == vehicleOwnerOf(did)`.

### Functions
| Signature | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `constructor(address _didRegistry)` (`:125`) | — | Binds the registry; deployer becomes `owner` and an authorised manufacturer | — | none | CVIN extension |
| `setAuthorizedManufacturer(address, bool)` (`:133`) | external | Grants or revokes the manufacturer role | `onlyContractOwner` | `ManufacturerAuthorized` | CVIN extension |
| `createVehicleDID(vin, vehicleOwner, make, model, uint16 year, color, engineNumber, uint256 manufacturingDate, autonomyLevel) returns (address did)` (`:156`) | external | Requires a 17-char VIN that is not yet registered; `did = vehicleOwner`; stores both mappings. **make…autonomyLevel are accepted but ignored** (no attributes are written) | `onlyAuthorizedManufacturer` | `VehicleDIDCreated` | CVIN extension |
| `setVehicleAttributes(address did, make, model, year, color, engineNumber, manufacturingDate, autonomyLevel)` (`:218`) | external | Requires the wrapper to be the ERC-1056 owner and the DID to be registered; calls `didRegistry.setAttribute` 8 times (VIN, make, …; `year`/date `abi.encodePacked`) with 100-year validity | `onlyVehicleOwner(did)` | 8× `DIDAttributeChanged` (from the registry) | CVIN extension over ERC-1056 `setAttribute` |
| `transferVehicleOwnership(address did, address newOwner)` (`:259`) | external | Wrapper-controlled mode only: updates `vehicleOwners[did]`; the ERC-1056 owner stays the wrapper | `onlyVehicleOwner(did)` | `VehicleOwnershipTransferred` | CVIN extension |
| `updateOwnershipMapping(address oldOwnerDID, address newOwnerDID)` (`:282`) | external | Direct-flow follow-up after `changeOwner(old, new)`: requires `identityOwner(old) == new`, then moves the VIN mappings to `newOwnerDID` | **anyone** (check is state-based) | `VehicleOwnershipTransferred(old, old, new)` | CVIN extension |
| `setServiceEndpoint(address did, bytes32 endpointType, string url, uint validity)` (`:315`) | external | Forwards to `didRegistry.setAttribute`; reverts in the registry unless the wrapper controls the DID | `onlyVehicleOwner(did)` | `DIDAttributeChanged` | ERC-1056 passthrough |
| `addVerificationDelegate(did, delegateAddress, delegateType, validity)` (`:333`) | external | Forwards to `didRegistry.addDelegate` | `onlyVehicleOwner(did)` | `DIDDelegateChanged` | ERC-1056 passthrough |
| `revokeVerificationDelegate(did, delegateAddress, delegateType)` (`:348`) | external | Forwards to `didRegistry.revokeDelegate` | `onlyVehicleOwner(did)` | `DIDDelegateChanged` | ERC-1056 passthrough |
| `getDIDFromVIN(string vin) returns (address)` (`:363`) | external view | `vinToDID[keccak256(vin)]` | anyone | none | CVIN extension |
| `getVINFromDID(address) returns (string)` (`:373`) | external view | `didToVIN` | anyone | none | CVIN extension |
| `vehicleOwnerOf(address did) returns (address)` (`:389`) | public view | Returns the ERC-1056 controller unless that is the wrapper itself; otherwise `vehicleOwners[did]`, or `did` if unset | anyone | none | CVIN extension |
| `getVehicleOwner(address)` (`:403`) | external view | Alias for `vehicleOwnerOf` | anyone | none | CVIN extension |
| `isValidDelegate(did, delegateType, delegateAddress) returns (bool)` (`:414`) | external view | Forwards to `didRegistry.validDelegate` | anyone | none | ERC-1056 passthrough |
| auto getters for every public mapping and constant | public view | — | anyone | none | — |

### Design notes / security caveats
- **Two modes.**
  - *Direct mode:* the owner calls the registry directly. The wrapper only holds the VIN mapping.
  - *Wrapper-controlled mode:* the owner calls `didRegistry.changeOwner(did, wrapper)`. After that, `setVehicleAttributes`, `setServiceEndpoint`, the delegate functions and `transferVehicleOwnership` work.
- **No way back:** the wrapper has no function that calls `didRegistry.changeOwner` to return control, so once a DID is handed over, ERC-1056 control is locked in the wrapper for good (including key rotation and signed operations). `benchmarks/adapters/erc1056w.adapter.js:26` notes "no signed entry point".
- **No owner consent at creation:** `createVehicleDID` lets any authorised manufacturer bind an arbitrary address as a vehicle DID, without the owner's consent and without checking whether that address already holds a VIN. A second VIN for the same address overwrites `didToVIN` but leaves the old `vinToDID` entry in place.
- **DID conflated with owner:** "DID = owner address" means an ownership transfer in direct mode moves the VIN to a *different* DID (`updateOwnershipMapping` re-keys to `newOwnerDID`). The vehicle's identifier is not stable, which contradicts the ERC-1056 idea of a stable identity with a rotating controller.
- **Plaintext VIN on-chain:** `didToVIN` stores the VIN in clear, and the `VehicleDIDCreated` event carries it too.
- **Ignored parameters:** `createVehicleDID`'s attribute parameters are dead inputs (gas cost, misleading API).
- **Hashed keys (non-conformant):** the `keccak256` attribute and delegate keys do not follow did:ethr naming (see Standards).
- **History of fixes:** `setVehicleAttributes` was previously unreachable (REVIEW_02 K-1 / defect D18: no `did` parameter, plus a `uint256.max` validity). It was fixed as documented in the comments at `:204-208` and `:72-80`. The duplicate constant is left over from that fix.
- **Missing revocation passthrough:** the wrapper exposes no `revokeAttribute`, so a service endpoint set in wrapper mode cannot be revoked.

---

## Where / when / how it's used

**Typical lifecycle**
1. Deploy `EthereumDIDRegistry`, then `CVINVehicleDIDRegistry(registry)`.
2. *(Optional)* the admin calls `setAuthorizedManufacturer`.
3. Create the vehicle DID:
   - implicitly, at 0 gas (every address is a DID), or
   - explicitly, by the manufacturer calling `createVehicleDID(vin, owner, …)`.
4. Update:
   - in direct mode, the owner calls `setAttribute` / `addDelegate`, or the signed variants through a relayer;
   - in wrapper mode, the owner calls `changeOwner(did, wrapper)` and then `setVehicleAttributes` / `setServiceEndpoint` / `addVerificationDelegate`.
5. Resolve off-chain: `identityOwner` / `changed`, then the event walk (`did_resolver.py`, sandbox `resolve`), plus `getVINFromDID` / `getDIDFromVIN`.
6. Revoke with `revokeDelegate` / `revokeAttribute`, or deactivate with `changeOwner(…, 0x0)`.
7. Transfer:
   - direct mode: `changeOwner` followed by `updateOwnershipMapping`;
   - wrapper mode: `transferVehicleOwnership`.

**Deploy scripts**
- `1_blockchain-identity/scripts/deployERC1056.js` deploys both contracts and writes `deployments/erc1056-deployment.json`.

**Hardhat tests** (`1_blockchain-identity/test/L2-identity-system/per-option/ERC1056/`)
- `EthereumDIDRegistry.test.js` (29 `it`): owner, delegate, attribute, changed-tracking and gas; also signed ops with the raw digest.
- `CVINVehicleDIDRegistry.test.js` (28 `it`): manufacturer auth, creation, `setVehicleAttributes` (K-1), ownership transfer, service endpoints, delegates, queries.
- `CVINVehicleDIDRegistry.regression.test.js` (3 `it`): D18 regression (`PERMANENT_ATTRIBUTE_VALIDITY`, eight attributes resolve from events).
- `PseudonymPool.test.js` (M5 pseudonym pool on `EthereumDIDRegistry`).
- `ERC1056Registry.regression.test.js` in the same folder tests the *different* `contracts/MOBI/ERC1056Registry.sol`.
- `1_blockchain-identity/test/L2-identity-system/security/securityScenarios.test.js:185` covers "Security / ERC-1056 (EthereumDIDRegistry)" attacks such as an unauthorised `addDelegate`.
- `5_zkp-agent-identity/test-contracts/zkvin_gate.test.js` deploys the Phase 1 `EthereumDIDRegistry` artifact unmodified as the anchor for the zkVIN gate.
- `phase2/idtx/test/idtx.test.js` and `phase2/idtx/contracts/IdtxExecutor.sol` call the registry through an `IERC1056` interface (`:38`).

**Sandbox** (`sandbox/options/erc-1056-uport/`)
- `adapter.js`: its header maps each method to a contract function:
  - `deploy`: both constructors;
  - `create`: `createVehicleDID`, or `{implicit:true}` at 0 gas;
  - `changeController`: `changeOwner`;
  - `addKeyOrDelegate`: `addDelegate(keccak256(purpose))`;
  - `setAttribute`: `setAttribute(keccak256(name))`;
  - `revoke`: `revokeDelegate` / `revokeAttribute`;
  - `signedOp`: `changeOwnerSigned`;
  - `resolve`: on-chain reads plus the event walk plus `getVINFromDID` / `vehicleOwnerOf`;
  - `addClaim` and `transfer` are NotApplicable.

  The wrapper-only functions are listed as not used.
- `manifest.yaml`: lists both contracts, the `benchmark_ops` descriptions and function families (explicit creation and ownership marked "implemented, not used by the comparison"; key/delegate marked "measured").
- `demos/`: `creation`, `offchain-creation`, `controller`, `keys-delegates`, `attributes`, `revocation`, `signed-execution`, `authorisation-roles`, `lifecycle-history`, `did-resolution`, `vin-linkage` (`.js`).
- `README.md`.
- `sandbox/grand/make_manifests.py:23` generates the manifest entry, and `sandbox/grand/report/demos.json` holds the demo results.
- `sandbox/options/cvin-combined/demos/vin-linkage.js:48` contrasts that option with `CVINVehicleDIDRegistry`'s VIN index.

**Benchmarks / gas** (`1_blockchain-identity/`)
- `scripts/benchmark_gas.js` (`benchmarkERC1056`, `:65`).
- `scripts/benchmark_scaling.js` (`scaleERC1056`, `setAttribute` growth).
- `scripts/infrastructure_gas.js` (RSU identity cost).
- `scripts/mobi_vid_backend_sweep.js` (`sweepERC1056`; birth record as `setAttribute`, attestation approximated by `setAttributeSigned`).
- `scripts/security_scenarios.js` (`scenarioERC1056`, cross-chain replay caveat).
- `scripts/experiment_pseudonym_pool.js` (M5).
- `scripts/validate_sepolia.js` (`validateERC1056`, Sepolia validation).
- `benchmarks/adapters/erc1056.adapter.js` (direct mode) and `erc1056w.adapter.js` (wrapper-controlled mode).
- `benchmarks/rubric/did-method-rubric.json`.
- `5_zkp-agent-identity/scripts/measure_gas.js` uses the artifact for reference gas (createIdentity 52,594).
- Results go to `4_comparison-framework/results/` (`gas_benchmark*.json`, `infrastructure_gas*.json`, `scaling_marginal.json`, `mobi_vid_backends.json`, `pseudonym_pool.*`), and `4_comparison-framework/feature-matrix/make_feature_matrix.py` and `security-analysis/` read them.

**Python layers**
- `2_w3c-ssi-layer/did-resolution/did_resolver.py`: on-chain did:ethr resolution, described above.
- Its tests: `tests/test_did_resolver_onchain_ethr.py` deploys the `EthereumDIDRegistry` artifact on a Hardhat node and resolves; `tests/test_did_resolver_chain.py` and `tests/resolver_chain_helpers.py` hold the shared deploy helpers.
- `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py` and `experiment_freshness_k.py` use `cv2x-testbed/identity/erc1056_provider.py` against the **separate** `cv2x-testbed/contracts/ERC1056Registry.sol`, not this contract. They mention ERC-1056 but are a different implementation.

**Docs** (non-exhaustive): `1_blockchain-identity/CVIN-SSI-ARCHITECTURE.md`, `docs/DEFECT_LOG.md` (D18), `docs/review02/PASS1_K.md` (K-1), `docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md`, `docs/FEATURE_ASYMMETRY_MATRIX.md`, `docs/conformance/W3C_DID_TEST_SUITE.md` plus `generate_implementations_onchain.py`, `docs/thesis/chapter4-implementation/README.md`, `CAPABILITIES.md`, `INVENTORY.md`, `SOURCES.md`.

---

## Duplicates / copies
- No other copy of `EthereumDIDRegistry.sol` or `CVINVehicleDIDRegistry.sol` exists outside `node_modules`/`artifacts` (checked with `find`). Phase 2 and `5_zkp-agent-identity` reuse the **compiled artifact** (`1_blockchain-identity/artifacts/contracts/ERC1056/EthereumDIDRegistry.sol/EthereumDIDRegistry.json`), not a source copy. That means they depend on the Phase 1 build having been run.
- **Related but different contracts** (not duplicates):
  - `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol`: the "ERC-1056 / vehicle profile" sandbox option.
  - `cv2x-testbed/contracts/ERC1056Registry.sol`: the cv2x testbed registry, which `scripts/experiment_pseudonym_pool.js:6-7` explicitly says is "NOT" this one (K-5).
- `1_blockchain-identity/_research-copies/ERC1056/` holds research notes only (Markdown summaries of upstream EthereumDIDRegistry / EthrDID / EthrDIDResolver, plus comparisons), no `.sol`.
