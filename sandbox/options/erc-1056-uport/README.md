# erc-1056-uport — ERC-1056 / uPort-style (plan S7 demos)

**Identity model.** Every Ethereum address already is a DID (`did:ethr`) in the single shared `EthereumDIDRegistry`: `identityOwner(x)` defaults to `x`, and the DID document is rebuilt off-chain from `DIDOwnerChanged` / `DIDDelegateChanged` / `DIDAttributeChanged` events linked through the `changed` pointer. The `CVINVehicleDIDRegistry` wrapper adds VIN↔DID mappings, a manufacturer role and vehicle helpers, but its mutating helpers only work after the vehicle owner has made the wrapper the ERC-1056 owner of the DID.

Run: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/<family>.js` (one JSON line per step, `summary` line last, non-zero exit on failure).

| Family | Demo | Functions exercised (`EthereumDIDRegistry` unless `W.` = wrapper) | Measured in comparison? (manifest) |
|---|---|---|---|
| creation | `demos/creation.js` | `W.createVehicleDID`, `W.getDIDFromVIN`, `W.didToVIN`, `identityOwner`, `changed`, `setAttribute` (first key) | no — comparison counts the first `setAttribute` as createIdentity |
| controller | `demos/controller.js` | `changeOwner`, `changeOwnerSigned`, `identityOwner`, `owners`, `W.owner`, `W.vehicleOwners`, `W.vehicleOwnerOf`, `W.getVehicleOwner`, `W.transferVehicleOwnership`, `W.updateOwnershipMapping` | no (benchmark transferOwnership uses `changeOwner`) |
| keys-delegates | `demos/keys-delegates.js` | `addDelegate`, `addDelegateSigned`, `delegates`, `validDelegate`, `revokeDelegate`, `revokeDelegateSigned`, `W.DELEGATE_VERIKEY/SIGAUTH`, `W.isValidDelegate`, `W.addVerificationDelegate`, `W.revokeVerificationDelegate`, expiry via `evm_increaseTime` | **yes** (`addDelegate`) |
| attributes | `demos/attributes.js` | `setAttribute`, `setAttributeSigned`, `revokeAttribute`, `revokeAttributeSigned`, `W.setVehicleAttributes` (8-event birth record, resolved back through the adapter), `W.PERMANENT_ATTRIBUTE_VALIDITY`, `W.setServiceEndpoint`, all 11 `W.DID_*` / `W.SVC_*` constants | no (benchmark createIdentity/updateAttribute use `setAttribute`) |
| revocation | `demos/revocation.js` | `revokeAttribute(+Signed)`, `revokeDelegate(+Signed)`, `W.revokeVerificationDelegate`, `changeOwner(0)` probe | no (benchmark revoke uses `revokeAttribute`) |
| signed-execution | `demos/signed-execution.js` | `setAttributeSigned`, `addDelegateSigned`, `revokeDelegateSigned`, `revokeAttributeSigned`, `changeOwnerSigned`, `nonce`; replay + forgery rejected | no (L1 signed-op only) |
| lifecycle-history | `demos/lifecycle-history.js` | `changed` linked-list walk over 5 events, adapter `resolve` | no |
| authorisation-roles | `demos/authorisation-roles.js` | `W.owner`, `W.authorizedManufacturers`, `W.setAuthorizedManufacturer` (grant/revoke), gated `createVehicleDID` | no |
| vin-linkage | `demos/vin-linkage.js` | `W.DID_VIN`, `W.vinToDID`, `W.didToVIN`, `W.getDIDFromVIN`, `W.getVINFromDID` | no |
| did-resolution | `demos/did-resolution.js` | `W.didRegistry`, `identityOwner`, `validDelegate`, `W.vehicleOwnerOf`, `W.getVINFromDID`, adapter `resolve` before/after expiry | no |
| offchain-creation | `demos/offchain-creation.js` | `identityOwner`/`changed`/`owners`/`nonce`/`validDelegate` on a never-funded address; first tx is `addDelegate` | no (L1 create = 0) |

## Asymmetry notes

- **Creation: implicit.** 0 gas; the address is the DID. Two explicit alternatives exist and are not compared: the first key publication (what the benchmark calls createIdentity, ≈78k) and `createVehicleDID` (VIN-bound, 2 SSTOREs, manufacturer-gated).
- **Veracity / automation.** The chain enforces: controller authorisation (`identityOwner`), delegate validity windows (`validDelegate` is an on-chain view), meta-tx replay protection (`nonce`), VIN length (17) and uniqueness, the manufacturer role. A verifier must: replay the event log (`changed` → `previousChange`), apply `validTo` to attributes itself (no on-chain check), query the wrapper separately for the VIN (not in the event history), and verify every credential off-chain (`2_w3c-ssi-layer/verifiable-credentials`) — the chain holds only the `SVC_CREDENTIAL_SERVICE` endpoint.
- **Cryptography / hashing.** `keccak256` for attribute names, delegate types and `vinToDID` keys. Signed operations: raw secp256k1 over `keccak256(0x19 ‖ 0x00 ‖ registry ‖ nonce[owner] ‖ identity ‖ "op" ‖ args)` — **no EIP-191 prefix** (personal_sign wallets cannot produce it; the nonce is keyed by the owner, not the identity). Off-chain VCs use EIP-191 / JSON-LD in the SSI layer.
- **Implemented but not compared.** All five `*Signed` meta-transactions, delegate expiry without a transaction, the `changed` linked list, the whole wrapper (VIN mappings, roles, `transferVehicleOwnership`, `updateOwnershipMapping`, `setServiceEndpoint`, `add/revokeVerificationDelegate`), the second ownership model (VIN re-pointed to a new DID).
- **Observed defects / surprises** (steps marked OBSERVATION / FIXED (Dnn)). *Fixed 2026-10-04 — D18 (`docs/DEFECT_LOG.md`):* `setVehicleAttributes` now succeeds — its validity is the bounded `PERMANENT_ATTRIBUTE_VALIDITY` (100 y) instead of `type(uint256).max`, so the eight-attribute birth record is reachable through the wrapper (83 k gas; `attributes.js` asserts the 8 events and resolves them through the adapter). *Still open:* after `transferVehicleOwnership` the wrapper keeps ERC-1056 control and has no release function (D19); a second `createVehicleDID` for the same owner silently overwrites `didToVIN` (D20); `changeOwner(did, 0)` restores self-control instead of locking (D26); revoking a never-set attribute succeeds; the wrapper owner is immutable.

## Coverage check

ABI public/external functions: 49 (16 registry + 33 wrapper, `PERMANENT_ATTRIBUTE_VALIDITY` added by the D18 fix). Covered by the demos: **49 / 49**. Uncovered: none. (Non-ABI labels used for constructors, `adapter.*` and `offchain:*` steps.)
