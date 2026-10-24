# 04 — Account & Claim Identity: ERC-725, ERC-725X/Y, ERC-735, ERC-4337, CVIN-Combined

This group covers the CVIN identity options where **the identity is a contract account or a claim holder** instead of a token or a pure registry entry. Five option families are involved:

- a basic ERC-725 (v1-era, key-managed) proxy account,
- a full ERC-725X + ERC-725Y smart account,
- an ERC-735 claim holder with on-chain issuer-signature verification,
- an ERC-4337 smart-contract account plus a minimal EntryPoint harness,
- the thesis's own hybrid `CVINCombinedIdentity`, which composes **ERC-1056 (event-based DID registry) + ERC-735 (on-chain claims)** in one shared registry.

All contracts live under `1_blockchain-identity/contracts/` and are self-contained, with no OpenZeppelin or vendored-package imports. Apart from the ERC-725 basic variant, each one deliberately reproduces the canonical interface and event shapes so the gas and security benchmarks compare like with like. ERC-734 has no contract of its own in the repo (there is no `contracts/ERC734`). Its MANAGEMENT-key role is played by a single `owner` address, and the basic ERC-725 contract reuses its `addKey`/`removeKey` key model.

---

## Standards & protocols

| Spec | Status | Purpose / canonical interface | Fidelity in this repo |
|---|---|---|---|
| **ERC-725 v1 (2017 "Identity")** | Draft. It was superseded by the v2 split into 725X/725Y. | Proxy identity with ERC-734-style keys: `getKey`, `addKey`, `removeKey`, `execute`, `approve`, events `KeyAdded`/`KeyRemoved`/`ExecutionRequested`/`Executed`/`Approved`. | `CVIN_DID_ERC725.sol` keeps the v1 surface but is a **skeleton**. `execute` (L80-84) only emits `Executed` and **performs no call**. `approve` (L86-88) has an empty body. Authorisation is a single `_owner` (L38, L60, L67, L81) rather than purpose-1 MANAGEMENT keys. Keys do not take part in authorisation at all. There is no `keyHasPurpose`, no `getKeysByPurpose`, and no execution IDs. |
| **ERC-725 v2: ERC-725X (executor)** | Draft/Living, maintained in the LUKSO `erc725/smart-contracts` repo. | `execute(uint256 op, address target, uint256 value, bytes data)` with ops CALL=0, CREATE=1, CREATE2=2, STATICCALL=3, DELEGATECALL=4, and `executeBatch`. Events `Executed(op, target, value, bytes4 selector)` and `ContractCreated(op, addr, value, salt)`. ERC-165 ID `0x7545acac`. | `CVINVehicleERC725XY.sol` is faithful. All 5 ops run the real opcode (L252-351). Revert data is bubbled up (L354-369). CREATE2 takes the salt from the trailing 32 bytes of `data`, following the reference convention (L330-351). The interface IDs match (L54-56). Deviations: plain `onlyOwner` instead of OZ `OwnableUnset`, `require` strings instead of custom errors, and no LSP20 reverse-verification. The header (L26-50) explains why the reference package is not inherited: it calls OZ4's 3-arg `verifyCallResult`, but the project uses OZ 5.0.2. |
| **ERC-725Y (key/value store)** | Same as ERC-725X. | `getData`, `getDataBatch`, `setData`, `setDataBatch`, event `DataChanged(bytes32 indexed, bytes)`. ERC-165 ID `0x629aa694`. | Faithful (L140-181). CVIN extension: well-known keys `keccak256("cvin:vin"/"cvin:make"/"cvin:model"/"cvin:year")` (L67-73) plus `setVehicleBirthAttributes` and `getVehicleVIN` (L190-205). These keys are **not** LSP2 JSON-schema keys. |
| **ERC-734 (Key Manager)** | Draft, never finalised. | Keys with purposes 1=MANAGEMENT, 2=ACTION, 3=CLAIM, 4=ENCRYPTION, and an execute/approve flow. | No standalone implementation. It appears in a simplified form in `CVIN_DID_ERC725.sol` (`addKey(bytes32,uint256 purpose,uint256 type)`) and as the "owner = MANAGEMENT key" substitution in `CVINVehicleClaimHolder.sol` (L8-13, L100-102). |
| **ERC-735 (Claim Holder)** | Draft issue #735, never an EIP. | `getClaim`, `getClaimIdsByTopic`, `addClaim(topic, scheme, issuer, signature, data, uri)`, `removeClaim`, `changeClaim`/`approve`, events `ClaimRequested`/`ClaimAdded`/`ClaimRemoved`/`ClaimChanged`. claimId = `keccak256(issuer, topic)`. | `CVINVehicleClaimHolder.sol` reproduces the draft interface (`IERC735`, L15-83) and claimId rule (L252). Documented deviations (L99-139): owner instead of ERC-734 keys; the request/approve flow is collapsed into a synchronous `addClaim` (`ClaimRequested` is still emitted, L268-276); **on-chain** EIP-191 ECDSA verification at add time; an (issuer, topic) whitelist (D25a); VIN binding on topic 1 (D25b); sticky issuer revocation (K-2). There is no `changeClaim`; calling `addClaim` again for the same (issuer, topic) updates the claim and emits `ClaimChanged`. |
| **ERC-4337 (Account Abstraction), v0.7 shapes** | Final ERC. The canonical EntryPoint is v0.7/v0.8. | `IAccount.validateUserOp(PackedUserOperation, bytes32 userOpHash, uint256 missingAccountFunds) returns (uint256 validationData)`. EntryPoint provides `handleOps`, `getUserOpHash`, nonces, deposits and paymasters. | `CVINVehicleAccount.sol` has a v0.7-shaped `PackedUserOperation` (L50-60), `IAccount` (L63-69) and SimpleAccount-style validation that returns 0/1 and does not revert (L136-169). `CVINMinimalEntryPoint.sol` is **explicitly NOT canonical** (L8-29): a single `handleOp`; no bundling, paymaster, aggregation, deposits, gas accounting or initCode; a plain sequential nonce; and it reverts on inner failure. `getUserOpHash` follows the v0.7 layout (L45-61). Omitted from the account: `validAfter`/`validUntil` packing and factory/CREATE2 counterfactual deployment. |
| **EIP-191 (signed data, `\x19Ethereum Signed Message:\n32`)** | Final. | Prefixing for personal_sign. | Used by the ERC-735 holder (`_recoverSigner`, L483-516) and the ERC-4337 account (`_validateSignature`, L152-169). **Not** used by `CVINCombinedIdentity`, which ecrecovers a raw digest (L420-434). As a result, issuer signatures do not carry over between the two claim contracts (noted at ERC735 L476-481). |
| **EIP-2 (low-s)** | Final. | Rules out malleable `s` values. | Enforced only in the ERC-735 holder (L508-511). The 4337 account and the Combined registry do not check `s`. Combined's revocation key is the digest, not the signature, so a malleated copy still cannot get around revocation (Combined L40-44). |
| **ERC-1271 / EIP-712** | Final. | Contract signatures and typed-data hashing. | **Not used** anywhere in this group. ERC735 L109-110 states that ERC-1271 issuers are unsupported, and 4337 L35 says "no EIP-1271". |
| **ERC-165** | Final. | `supportsInterface`. | Only `CVINVehicleERC725XY` implements it (L382-387). |
| **ERC-1056 (Lightweight Identity / did:ethr)** | Draft. | `identityOwner`, `changeOwner`, `addDelegate`, `revokeDelegate`, `validDelegate`, `setAttribute`, `revokeAttribute`, `changed`, and the `DID*Changed` events with the `previousChange` linked list. | It is the ERC-1056 half of `CVINCombinedIdentity` (L161-242), with the same event shapes and `changed` pointer. The `*Signed` meta-transaction variants and `nonce` mapping are omitted. `changeOwner` has no zero-address check, same as the reference. |
| **W3C DID Core / did:ethr** | W3C Rec / method spec. | DID document resolved from events. | Indirect only: the Combined contract's event chain is what the sandbox `did-resolution` demo walks. |

---

## 1. `CVIN_DID_ERC725.sol` — basic ERC-725 (v1-style)

Path: `1_blockchain-identity/contracts/ERC725/CVIN_DID_ERC725.sol`. Contract `CVIN_SCBasedAccOrID_DID_ERC725Basic` (L4). It uses `pragma ^0.8.20` and has no imports and no inheritance.

**Purpose:** a per-vehicle "proxy account" whose deployment creates the identity (the deployer becomes owner). It serves as the baseline ERC-725 option in benchmarks.

**State**

| Var | Type | Line | Notes |
|---|---|---|---|
| `_owner` | `address private` | 6 | Set to `msg.sender` in the constructor. |
| `keys` | `mapping(bytes32=>Key) private` | 22 | `Key{purpose,keyType,key}` (L15-19) |
| `allKeys` | `bytes32[] private` | 24 | Enumeration list |

**Events:** `OwnershipTransferred` (L9), `KeyAdded(key,purpose,keyType)` (L10), `KeyRemoved` (L11), `Executed(operationType,to,value,data)` (L12).
**Modifiers:** none. Access is checked with inline `require(msg.sender == _owner)`.

| Function | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `constructor()` L27 | — | Sets owner = deployer | — | OwnershipTransferred | Ownable pattern |
| `owner()` L33 | public view | Returns owner | any | — | ERC-173-like |
| `transferOwnership(address)` L37 | public | Sets new owner (**no zero check**) | owner | OwnershipTransferred | ERC-173-like |
| `renounceOwnership()` L43 | public | owner = 0 | owner | OwnershipTransferred | OZ-Ownable-like |
| `getKey(bytes32)` L50 | public view | Returns (purpose,type,key) | any | — | ERC-725v1/734 |
| `getKeys()` L55 | public view | Returns all key ids | any | — | CVIN ext. |
| `addKey(bytes32,uint256,uint256)` L59 | public | Writes key, pushes to `allKeys` | owner | KeyAdded | ERC-725v1/734 (one purpose per key) |
| `removeKey(bytes32)` L66 | public | Deletes key, then swap-and-pop over `allKeys` (O(n)) | owner | KeyRemoved | ERC-725v1/734 |
| `execute(uint256,address,uint256,bytes)` L80 | public | **Only emits `Executed`; performs no call** | owner | Executed | ERC-725v1 (stub) |
| `approve(uint256,bool)` L86 | public | **Empty body, no access check** | any | — | ERC-725v1 (stub) |

**Notes / caveats**
- `addKey` on an id that already exists overwrites the struct and pushes a **duplicate** into `allKeys` (L61-62). `removeKey` then removes only one copy, and it emits `KeyRemoved` even for keys that do not exist.
- `execute` is not payable and does nothing. Keys never authorise anything, so this is an "interface-shape" baseline. The sandbox adapter states this explicitly.
- There is no VIN or data store.

---

## 2. `CVINVehicleERC725XY.sol` + `CVINExecuteTarget.sol` — ERC-725X/Y smart account

Path: `1_blockchain-identity/contracts/ERC725xy/CVINVehicleERC725XY.sol` (`pragma ^0.8.24`, no imports or inheritance).

**State / constants**

| Name | Type | Line |
|---|---|---|
| `_INTERFACEID_ERC165/725X/725Y` | `bytes4 internal constant` | 54-56 |
| `OPERATION_CALL..DELEGATECALL` (0-4) | `uint256 public constant` | 59-63 |
| `VIN_KEY, MAKE_KEY, MODEL_KEY, YEAR_KEY` | `bytes32 public constant` = keccak256("cvin:…") | 67-73 |
| `_owner` | `address private` | 76 |
| `_store` | `mapping(bytes32=>bytes) internal` | 79 |

**Events:** `OwnershipTransferred` (L82), `Executed(op idx, target idx, value, bytes4 selector idx)` (L84), `ContractCreated(op, addr, value, salt)` (L91), `DataChanged(bytes32 idx, bytes)` (L98).
**Modifier:** `onlyOwner` (L101).

| Function | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `constructor(address initialOwner)` L110 | payable | Sets owner (non-zero) | — | OwnershipTransferred | ERC-725 |
| `receive()` L117 | external payable | Accepts ETH | any | — | ERC-725 |
| `owner()` L120 | public view | | any | — | ERC-173 |
| `transferOwnership(address)` L128 | public | Rotates the controller (non-zero) | owner | OwnershipTransferred | ERC-173 |
| `renounceOwnership()` L134 | public | owner = 0 (single step, no 2-step confirm unlike LSP14) | owner | OwnershipTransferred | ERC-173/OZ |
| `getData(bytes32)` L140 | public view | | any | — | ERC-725Y |
| `getDataBatch(bytes32[])` L144 | public view | | any | — | ERC-725Y |
| `setData(bytes32,bytes)` L159 | public payable | Store write | owner | DataChanged | ERC-725Y |
| `setDataBatch(bytes32[],bytes[])` L163 | public payable | Equal-length, non-empty arrays | owner | DataChanged ×n | ERC-725Y |
| `_setData` L178 | internal | | — | DataChanged | ERC-725Y |
| `setVehicleBirthAttributes(string,string,string,uint256)` L190 | external | Writes 4 CVIN keys (year abi-encoded) | owner | DataChanged ×4 | CVIN extension |
| `getVehicleVIN()` L203 | external view | `string(_store[VIN_KEY])` | any | — | CVIN extension |
| `execute(uint256,address,uint256,bytes)` L216 | public payable | Dispatches to `_execute` | owner | Executed / ContractCreated | ERC-725X |
| `executeBatch(uint256[],address[],uint256[],bytes[])` L228 | public payable | Loop over `_execute` | owner | per op | ERC-725X |
| `_execute` L252 | internal | Op dispatch and parameter checks (CREATE* need target=0; STATIC/DELEGATE need value=0) | — | — | ERC-725X |
| `_executeCall` L280 / `_executeStaticCall` L291 / `_executeDelegateCall` L300 | internal | Low-level call; event emitted **before** the call | — | Executed | ERC-725X |
| `_deployCreate` L310 / `_deployCreate2` L330 | internal | Assembly create/create2 | — | ContractCreated | ERC-725X |
| `_verifyCallResult` L354 | internal pure | Bubbles up the revert | — | — | ERC-725X (ref) |
| `_selectorOf` L372 | internal pure | First 4 bytes | — | — | ERC-725X |
| `supportsInterface(bytes4)` L382 | public pure | 165/725X/725Y | any | — | ERC-165 |

**Caveats:** DELEGATECALL lets the owner overwrite `_owner` or the store, as the spec permits. `msg.value` sent with `executeBatch` is not reconciled against `sum(values)`; the reference contract checks this and this one does not. There is no reentrancy guard; access control is owner-only. `setData` is payable but the ETH has no use.

**`CVINExecuteTarget.sol`** (L11-26) is a test/demo helper and is not a standard. It has `value` and `lastCaller` (`uint256`/`address public`, L12-13) and event `ValueSet(caller idx, value)` (L15).

| Function | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `setValue(uint256)` L17 | external | Stores value and `msg.sender` | any | ValueSet | test helper |
| `willRevert()` L23 | external pure | Always reverts | any | — | test helper |

---

## 3. `CVINVehicleClaimHolder.sol` — ERC-735 claim holder

Path: `1_blockchain-identity/contracts/ERC735/CVINVehicleClaimHolder.sol`. It declares `interface IERC735` (L15-83) and `contract CVINVehicleClaimHolder is IERC735` (L141). One instance is one vehicle.

**State**

| Name | Type | Line | Notes |
|---|---|---|---|
| `VIN_ATTESTATION=1, MANUFACTURER_CERT=2, INSPECTION=3, INSURANCE=4` | public constant | 143-146 | CVIN topics |
| `ECDSA_SCHEME=1` | public constant | 149 | |
| `vin` | `string public` | 154 | |
| `vinHash` | `bytes32 public` | 157 | keccak(vin) |
| `owner` | `address public` | 160 | ERC-734 MANAGEMENT-key role |
| `claims` | `mapping(bytes32=>Claim) private` | 172 | claimId = keccak(issuer,topic) |
| `claimIdsByTopic` | `mapping(uint256=>bytes32[]) private` | 175 | |
| `authorizedIssuers` | `mapping(address=>mapping(uint256=>bool)) private` | 178 | D25a |
| `revokedClaims` | `mapping(bytes32=>bool) public` | 185 | K-2: key = keccak(issuer, digest) |

**Events:** the ERC-735 events `ClaimRequested`/`ClaimAdded`/`ClaimRemoved`/`ClaimChanged` (L16-54), and the CVIN events `OwnershipTransferred`, `VehicleIdentityCreated(vinHash idx, vin, owner idx)`, `IssuerAuthorized`, `IssuerRevoked` (L188-191).
**Modifier:** `onlyOwner` (L194).

| Function | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `constructor(string _vin)` L200 | — | Non-empty VIN; stores vin and vinHash; owner = deployer | — | OwnershipTransferred, VehicleIdentityCreated | CVIN ext. |
| `addClaim(topic,scheme,issuer,sig,data,uri)` L225 | external | Checks issuer≠0 and scheme==1; checks the EIP-191 sig over `keccak(this,topic,data)` recovers to issuer; checks the content is not revoked; checks issuer==owner OR the issuer is whitelisted for the topic; topic 1 requires a VIN suffix match; then upserts | owner | new: ClaimRequested + ClaimAdded. Existing: ClaimChanged | ERC-735 (+CVIN checks) |
| `removeClaim(bytes32)` L290 | external | Deletes. If the caller is the issuer, also marks the content revoked | owner or issuer | ClaimRemoved | ERC-735 (+K-2) |
| `revokeClaimContent(uint256,bytes)` L325 | external | Marks keccak(msg.sender, digest) revoked; removes the matching anchored claim | any (it can only affect the caller's own content) | ClaimRemoved (if anchored) | CVIN ext. (K-2 pass 2) |
| `_deleteClaim` L337 | private | Swap-and-pop unindex, then delete | — | ClaimRemoved | — |
| `getClaim(bytes32)` L360 | external view | | any | — | ERC-735 |
| `getClaimIdsByTopic(uint256)` L383 | external view | | any | — | ERC-735 |
| `claimExists(address,uint256)` L392 | external view | | any | — | CVIN ext. |
| `authorizeIssuer(address,uint256)` L405 | external | Whitelists; reverts if already set | owner | IssuerAuthorized | CVIN ext. (D25a) |
| `revokeIssuer(address,uint256)` L417 | external | Forward-looking only | owner | IssuerRevoked | CVIN ext. |
| `isAuthorizedIssuer(address,uint256)` L425 | external view | Excludes the self-issue exemption | any | — | CVIN ext. |
| `transferOwnership(address)` L434 | external | Non-zero; issuer authorisations persist | owner | OwnershipTransferred | ERC-173 / 734 role |
| `_encodesHolderVin(bytes)` L455 | internal view | The trailing `len(vin)` bytes must equal the VIN | — | — | CVIN ext. (D25b) |
| `_recoverSigner(bytes32,bytes)` L483 | internal pure | 65-byte sig, v normalisation, EIP-2 low-s, EIP-191 prefix, ecrecover | — | — | EIP-191/EIP-2 |

**Caveats (documented in source):** there is no nonce or expiry in the signed payload, so an older claim for the same (issuer, topic) that was never revoked can be re-anchored (L136-139). ERC-1271 issuers are unsupported. There is no `renounceOwnership`. The signature scheme differs from the Combined contract (L469-481).

---

## 4. ERC-4337: `CVINVehicleAccount.sol` + `CVINMinimalEntryPoint.sol`

### 4a. `CVINVehicleAccount.sol`
Path: `1_blockchain-identity/contracts/ERC4337/CVINVehicleAccount.sol`. It defines the file-level `struct PackedUserOperation` (L50-60), `interface IAccount` (L63-69) and `contract CVINVehicleAccount is IAccount` (L71).

| State | Type | Line |
|---|---|---|
| `SIG_VALIDATION_FAILED=1 / SUCCESS=0` | internal constant | 75-76 |
| `owner` | `address public` | 81 |
| `entryPoint` | `address public immutable` | 84 |
| `guardian` | `address public` | 87 |
| `_attributes` | `mapping(bytes32=>bytes) private` | 90 |

**Events (L94-99):** `VehicleAccountCreated`, `OwnershipTransferred`, `GuardianChanged`, `OwnerRecovered`, `AttributeChanged(key idx, value)`, `Executed(target idx, value, data)`.
**Modifier:** `onlyOwnerOrEntryPoint` (L109): allows owner, entryPoint, or `address(this)`.

| Function | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `constructor(address _entryPoint, address _owner)` L119 | — | Both must be non-zero | — | VehicleAccountCreated | ERC-4337 (no factory) |
| `receive()` L127 | external payable | | any | — | ERC-4337 |
| `validateUserOp(PackedUserOperation,bytes32,uint256)` L136 | external | EIP-191 ecrecover of userOpHash; returns 0/1; pays the prefund when >0 | entryPoint only | — | ERC-4337 IAccount |
| `_validateSignature` L152 / `_splitSignature` L171 | internal | No low-s check, no v normalisation | — | — | SimpleAccount v0.7 pattern |
| `execute(address,uint256,bytes)` L186 | external | Low-level call; bubbles up revert | owner / EP / self | Executed | SimpleAccount |
| `transferOwnership(address)` L208 | external | Key rotation (non-zero) | owner / EP / self | OwnershipTransferred | CVIN ext. |
| `setGuardian(address)` L218 | external | Sets or clears the guardian | owner / EP / self | GuardianChanged | CVIN ext. (social recovery) |
| `recoverOwner(address)` L228 | external | Guardian installs a new owner | guardian | OwnerRecovered | CVIN ext. |
| `setAttribute(bytes32,bytes)` L239 | external | ERC-725Y-flavoured store | owner / EP / self | AttributeChanged | CVIN ext. |
| `getAttribute(bytes32)` L245 | external view | | any | — | CVIN ext. |

**Caveats:** a single guardian can take over the account immediately; there is no timelock, threshold or owner veto. `validateUserOp` has `override` but `IAccount` is an interface, which compiles fine on 0.8.24. Signature malleability is not checked, but this is harmless here because the nonce lives in the EntryPoint.

### 4b. `CVINMinimalEntryPoint.sol`
It imports `{PackedUserOperation, IAccount}` from `./CVINVehicleAccount.sol` (L4). It has state `nonces` (`mapping(address=>uint256) public`, L33) and event `UserOperationHandled(userOpHash idx, sender idx, nonce, success)` (L35).

| Function | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `getUserOpHash(PackedUserOperation)` L45 | public view | v0.7 layout: keccak(abi.encode(packedHash, this, chainid)) | any | — | ERC-4337 v0.7 |
| `handleOp(PackedUserOperation)` L69 | external | Rejects initCode; checks and bumps the nonce; validateUserOp must return 0; calls `sender` with callData; bubbles up revert | any (bundler) | UserOperationHandled (success is always true) | Simplified ERC-4337 (canonical is `handleOps`) |

**Caveat:** the nonce is bumped before validation, but the whole transaction reverts on failure, so nothing is consumed.

---

## 5. `CVINCombinedIdentity.sol` — ERC-1056 + ERC-735 hybrid

Path: `1_blockchain-identity/contracts/CVINCombined/CVINCombinedIdentity.sol`. It is a single **shared registry** with no imports or inheritance. **It combines ERC-1056** (ownership, delegates, event-only attributes, the `changed` linked list) **with ERC-735** (on-chain, signature-verified claims, keyed per identity). The rationale is in L10-32: events are cheap, while safety-critical claims need O(1) on-chain checks.

| State | Type | Line | Notes |
|---|---|---|---|
| `CLAIM_TOPIC_VIN=1, _MANUFACTURER=2, _INSPECTION=3` | public constant | 54-56 | No insurance topic |
| `SCHEME_ECDSA=1` | public constant | 59 | |
| `_owners` | `mapping(address=>address) private` | 64 | 0 means self-owned |
| `delegates` | `mapping(address=>mapping(bytes32=>mapping(address=>uint256))) public` | 67 | expiry |
| `changed` | `mapping(address=>uint256) public` | 74 | DID-event chain head (claims do not advance it, K-6) |
| `_claims` | `mapping(address=>mapping(bytes32=>Claim)) private` | 88 | |
| `_claimIdsByTopic` | `mapping(address=>mapping(uint256=>bytes32[])) private` | 91 | |
| `revokedClaims` | `mapping(bytes32=>bool) public` | 98 | keccak(issuer, raw digest) |

**Events:** `DIDOwnerChanged`, `DIDDelegateChanged`, `DIDAttributeChanged` (ERC-1056 shapes, L103-117); `DIDClaimChanged(identity idx, claimId, topic, removed, previousChange)` (CVIN, L128); `ClaimAdded(claimId idx, identity idx, topic idx, scheme, issuer, sig, data, uri)` (L137); `ClaimRemoved(claimId idx, identity idx, topic idx, issuer)` (L147). The last two are ERC-735-*style* but have different signatures from the draft, because they add `identity`, move the indexing, and drop fields from `ClaimRemoved`.
**Modifier:** `onlyIdentityOwner(identity)` (L156).

| Function | Vis/Mut | What it does | Access | Events | Origin |
|---|---|---|---|---|---|
| `identityOwner(address)` L164 | public view | Override or self | any | — | ERC-1056 |
| `changeOwner(address,address)` L173 | external | Sets owner; bumps `changed` | identity owner | DIDOwnerChanged | ERC-1056 |
| `addDelegate(address,bytes32,address,uint256)` L185 | external | validTo = now + validity | identity owner | DIDDelegateChanged | ERC-1056 |
| `revokeDelegate(address,bytes32,address)` L198 | external | validTo = now | identity owner | DIDDelegateChanged | ERC-1056 |
| `validDelegate(address,bytes32,address)` L209 | external view | expiry > now | any | — | ERC-1056 |
| `setAttribute(address,bytes32,bytes,uint256)` L224 | external | Event only, plus `changed` | identity owner | DIDAttributeChanged | ERC-1056 |
| `revokeAttribute(address,bytes32,bytes)` L235 | external | validTo = 0 | identity owner | DIDAttributeChanged | ERC-1056 |
| `addClaim(identity,topic,scheme,issuer,sig,data,uri)` L254 | external | Raw-digest ecrecover over `keccak(this,identity,topic,data)`; revocation check; upsert. **No issuer whitelist, no VIN binding** | identity owner | ClaimAdded, DIDClaimChanged(removed=false) | ERC-735 style |
| `removeClaim(address,bytes32)` L303 | external | Issuer removal is recorded as revoked | identity owner or issuer | ClaimRemoved, DIDClaimChanged(true) | ERC-735 style (+K-2) |
| `revokeClaimContent(address,uint256,bytes)` L336 | external | Same as in the ERC-735 holder | any (own content only) | ClaimRemoved/DIDClaimChanged if anchored | CVIN ext. |
| `_deleteClaim` L348 | private | Swap-and-pop | — | ClaimRemoved, DIDClaimChanged | — |
| `getClaim(address,bytes32)` L365 | external view | | any | — | ERC-735 style |
| `getClaimIdsByTopic(address,uint256)` L385 | external view | | any | — | ERC-735 style |
| `hasValidClaim(address,uint256,address)` L395 | external view | False when issuer==0 (K-11) | any | — | CVIN ext. |
| `_claimDigest` L411 / `_recoverRawDigest` L420 | internal | Raw ecrecover; returns 0 on a bad length or v | — | — | ERC-1056-ref style |

**Caveats**
- **Stale comment:** the `DIDClaimChanged` NatSpec (L119-127) says addClaim and removeClaim "advance `changed[identity]`". The code deliberately does **not** do this (L292-297, L346-347, K-6), and `previousChange` there is only a correlation value.
- Any address can anchor claims about itself from any signer, because no issuer registry exists here, unlike the ERC-735 holder. A verifier must therefore filter by `issuer`, which is why `hasValidClaim` takes an issuer.
- There is no zero-address check on `changeOwner`, and no `*Signed` meta-transaction functions.
- `revokeDelegate` sets validTo = `block.timestamp`, so `validDelegate` (strict `>`) is false in that same block.

---

## Where / when / how it's used

No references were found in `cv2x-testbed/`, `phase2` code, `5_zkp-agent-identity/`, or deploy scripts. The only `scripts/deploy*` file is `deployERC1056.js`. All of these contracts are deployed inline by the scripts, tests and adapters listed below.

**Hardhat tests** (`1_blockchain-identity/test/`)
- `L2-identity-system/per-option/ERC725xy/CVINVehicleERC725XY.test.js`: all 5 operations, batch, Y store, ownership. It uses `CVINExecuteTarget`.
- `L2-identity-system/per-option/ERC735/CVINVehicleClaimHolder.test.js` and `.regression.test.js`: EIP-191 claims, issuer registry, VIN binding, K-2 revocation.
- `L2-identity-system/per-option/ERC4337/CVINVehicleAccount.test.js`: handleOp, nonce, key rotation, guardian recovery.
- `L2-identity-system/per-option/CVINCombined/CVINCombinedIdentity.test.js` and `.regression.test.js`: raw-digest claims, the `changed` chain, K-6 and K-11.
- `L2-identity-system/security/securityScenarios.test.js`: attack scenarios for ERC-725 basic, 735, 4337 and Combined.
- `L1-identity-mechanisms/*.test.js` (for example `08-signed-op.test.js`): run each sandbox adapter through generic mechanisms.
- `benchmarks/adapters.conformance.test.js`: checks the benchmark adapters; references `CVINExecuteTarget`.

**Scripts / benchmarks** (`1_blockchain-identity/scripts/`, `benchmarks/`)
- `scripts/benchmark_gas.js`: deploys every contract in this group (ERC-725 L197, 725xy L249, 735 L409, 4337 L557, Combined L715) and measures deploy/create/update/claim/revoke/transfer. Output goes to `4_comparison-framework/results/gas_benchmark*.json`.
- `scripts/security_scenarios.js`: ERC-725 (L284), 735 (L353), 4337 (L528), Combined (L807). Output goes to `4_comparison-framework/security-analysis/results/attack_results.json`.
- `scripts/benchmark_scaling.js` (735, Combined) writes `results/scaling_marginal.json`. `scripts/mobi_vid_backend_sweep.js` (735, Combined) writes `results/mobi_vid_backends.json`.
- `scripts/validate_sepolia.js`: Sepolia validation for 725xy (L253) and Combined; see `1_blockchain-identity/SEPOLIA_VALIDATION.md`.
- `benchmarks/adapters/{erc725,erc725xy,erc735,erc4337,cvin}.adapter.js` with `benchmarks/run.js` and `scenarios/crud.js` (which uses `CVINExecuteTarget`). Results go to `1_blockchain-identity/results/metrics{,-rpc}/latest/`.
- `4_comparison-framework/feature-matrix/make_feature_matrix.py`: the Python layer. It statically scans these .sol files (L22-26) to build the feature matrix.

**Sandbox** (`sandbox/options/<slug>/`, with `adapter.js`, `manifest.yaml`, `demos/*.js`, `README.md`). Each adapter header maps the uniform IdentityOption methods to contract functions:
- `erc-725`: create = deploy; changeController = `transferOwnership`; addKeyOrDelegate = `addKey(keccak(abi.encode(addr)), purpose, 1)`; revoke = `removeKey`; signedOp = `execute(0,…)`, noted as having no effect; setAttribute and addClaim are NotApplicable. Demos: creation, controller, keys-delegates, revocation, signed-execution.
- `erc-725xy`: create = deploy + `setData(VIN_KEY, vin)`; setAttribute = `setData`; revoke = `setData(key, 0x)`; signedOp = `execute(CALL, CVINExecuteTarget, setValue)` followed by a `lastCaller` check. Demos: attributes, controller, creation, lifecycle-history, revocation, signed-execution, vin-linkage.
- `erc-735`: create = `new CVINVehicleClaimHolder(vin)`; addClaim = EIP-191 `signMessage`, then `addClaim`; revoke = `removeClaim`. Demos: authorisation-roles, claims, controller, creation, lifecycle-history, revocation, vin-linkage.
- `erc-4337`: deploy = EntryPoint; create = `new CVINVehicleAccount(ep, owner)`; addKeyOrDelegate = `setGuardian`; setAttribute = `setAttribute(keccak(key), value)`; signedOp = `handleOp`. Demos: attributes, controller, creation, keys-delegates, lifecycle-history, signed-execution.
- `cvin-combined`: deploy = registry; create is implicit with 0 gas; addKeyOrDelegate = `addDelegate`; setAttribute is event-only; addClaim uses a raw-digest `signingKey.sign`; resolve walks `changed`→`previousChange`. Demos: attributes, authorisation-roles, claims, controller, did-resolution, keys-delegates, lifecycle-history, offchain-creation, revocation, vin-linkage.
- `sandbox/grand/make_manifests.py` generates the manifests. `sandbox/grand/report/{demos.json,L1-asymmetry.*,GRAND_REPORT.md}` aggregate the results.

**Docs referencing them:** `docs/DEFECT_LOG.md` (D22, D25a-c), `docs/REVIEW_02_CODEBASE.md`, `docs/review02/PASS1_K.md`/`PASS2_K.md` (K-2, K-6, K-11), `docs/AFTER_ACTION_REPORT_05.md` (F7 signature unification), `docs/FEATURE_ASYMMETRY_MATRIX.md`, `docs/tdp/TDP-006_FMECA.md`, `docs/thesis/chapter4-implementation/README.md`, `docs/thesis/chapter5-results/README.md`, `docs/phase2/focus/F1_onchain_storage_idtx/CAPTURE.md`, `docs/phase2/focus/F3_interaction_modes/*` (4337), `INVENTORY.md`, `SOURCES.md`, `CAPABILITIES.md`.

**Typical call sequences**
- *ERC-735:* the owner deploys `CVINVehicleClaimHolder(vin)`, then calls `authorizeIssuer(oem, 2)`. The issuer signs `signMessage(keccak(holder, topic, data))`. The owner calls `addClaim(...)`; a verifier reads `getClaimIdsByTopic` and `getClaim`. The issuer can later call `removeClaim` or `revokeClaimContent`. On a sale, the owner calls `transferOwnership`.
- *ERC-4337:* deploy `CVINMinimalEntryPoint`, then `CVINVehicleAccount(ep, owner)`. Build a `PackedUserOperation` whose callData is `transferOwnership`, `setAttribute` or `execute`. Get `getUserOpHash`, have the owner sign it with `signMessage`, and the bundler sends `handleOp`. For recovery, the guardian calls `recoverOwner(newKey)`.
- *Combined:* deploy the registry once; the identity is the vehicle address. Call `setAttribute`/`addDelegate` (cheap events), then `addClaim(identity, 1..3, …)` with a raw-signed digest. On-chain verifiers call `hasValidClaim(identity, topic, issuer)`, and off-chain resolvers walk the `DID*Changed` events.
- *ERC-725X/Y:* deploy `CVINVehicleERC725XY(owner)`, call `setVehicleBirthAttributes` or `setData`, then `execute(op, …)` to act on-chain.

---

## Duplicates / copies

- `1_blockchain-identity/_research-copies/ERC725/contracts/CVIN_DID_ERC725.sol` is **byte-identical** (`cmp`) to `contracts/ERC725/CVIN_DID_ERC725.sol`. Its `README.md` is a stale description: it presents `execute` and `approve` as functional and contains a placeholder `git clone https://github.com/your-repo/...` setup.
- `1_blockchain-identity/_research-copies/ERC725xy/` contains only `README.md` files (including `contracts_all/README.md`) and **no .sol copy** of the X/Y contract.
- No other copies of `CVINVehicleERC725XY`, `CVINExecuteTarget`, `CVINVehicleClaimHolder`, `CVINVehicleAccount`, `CVINMinimalEntryPoint` or `CVINCombinedIdentity` exist outside `1_blockchain-identity/contracts/` (searched by filename, excluding node_modules).
