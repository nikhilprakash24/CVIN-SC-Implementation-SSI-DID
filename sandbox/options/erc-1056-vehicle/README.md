# erc-1056-vehicle — ERC-1056 / vehicle profile (plan S7 demos)

**Identity model.** The vehicle's own account address is its DID in the shared `ERC1056Registry` (byte-identical to the cv2x-testbed registry behind `erc1056_provider.py`); creation is an explicit, self-signed `registerVehicle` that publishes a 1-year `veriKey` attribute, and delegates/attributes exist only as events. Unlike the uPort registry it adds an identity-level kill switch (`revokeIdentity` / `isRevoked` / `revokedAt`) and drops delegate storage and all meta-transactions; credentials and V2X message signing live off-chain in the Python provider.

Run: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/<family>.js`.

| Family | Demo | Functions exercised (`ERC1056Registry.`) | Measured? (manifest) |
|---|---|---|---|
| creation | `demos/creation.js` | `registerVehicle` (self-sent; third-party, re-register, after-changeOwner, after-revoke cases), `identityOwner`, `changed`; off-chain `register_vehicle` | **yes** (#21/#29) |
| controller | `demos/controller.js` | `owners`, `identityOwner`, `changeOwner`, `changeOwner(0)` probe, `nonce` (no signed variant) | no |
| keys-delegates | `demos/keys-delegates.js` | `addDelegate` (event-only), `revokeDelegate` (validTo = now), `updateVehicleKey` (public write not in manifest), `revokeAttribute` | no |
| attributes | `demos/attributes.js` | `setAttribute`, `revokeAttribute`, gating by `revokeIdentity` | no |
| claims | `demos/claims.js` | on-chain anchor only (`registerVehicle`, `identityOwner`); off-chain `update/get/revoke_credential` steps (`onchain:false`) | n/a on-chain (off-chain VCs) |
| revocation | `demos/revocation.js` | `revokeIdentity`, `isRevoked`, `revoked`, `revokedAt`, `getIdentityInfo`, `revokeAttribute`, `revokeDelegate`; what the flag gates; off-chain `check_revocation_status(_by_address)`, `revoke_credential` | **yes** (`revokeIdentity`, `isRevoked`) |
| lifecycle-history | `demos/lifecycle-history.js` | `changed`, `lastChanged`, `nonce`, linked-list walk before/after `revokeIdentity` | **yes** (`changed`) |
| did-resolution | `demos/did-resolution.js` | `getIdentityInfo`, `identityOwner`, adapter `resolve` (+expiry); off-chain `resolve_identity(_from_address)` | **yes** (`getIdentityInfo`) |
| offchain-messaging | `demos/offchain-messaging.js` | EIP-191 sign/recover in JS mirroring `sign_message` / `verify_message`, then `identityOwner` + `isRevoked` reads | no (implemented off-chain) |

## Asymmetry notes

- **Creation: explicit, self-sovereign.** `registerVehicle` must be sent by the vehicle account itself (`actor == identityOwner`), so no registrar can onboard a vehicle; it is one event plus the `changed` pointer (≈55k). The VIN is never anchored on-chain (it lives in the off-chain `VehicleCredential`).
- **Veracity / automation.** Chain enforces: controller authorisation, the revoked flag on `addDelegate`/`setAttribute`/`updateVehicleKey`/`registerVehicle`, and a one-call status read (`getIdentityInfo`, `isRevoked`) — the V2X hot path needs exactly two reads. Verifier must: replay events for keys/delegates/attributes (no `validDelegate`, no `delegates` getter), treat `validTo <= now` as revoked, distinguish "registered vehicle" from "any address" (both resolve), and do all credential checks off-chain (`erc1056_provider.py`).
- **Cryptography / hashing.** `keccak256` attribute names (`did/pub/secp256k1/veriKey/base64`); 65-byte uncompressed secp256k1 keys as attribute values; messages signed with EIP-191 personal_sign (`sign_message` / `verify_message`); **no on-chain signature verification at all** (`nonce` is declared and never consumed); no raw-digest meta-transactions.
- **Implemented but not compared.** `changeOwner`, delegates and attributes, `updateVehicleKey`, the off-chain message path, the off-chain credential lifecycle.
- **Observed defects / surprises.** `DIDRevoked` carries no `previousChange`, so after `revokeIdentity` the `changed` linked list is severed (pointer-walk finds nothing; the adapter falls back to a range scan); `revokeIdentity` is repeatable and overwrites `revokedAt`; `changeOwner` is not gated by the revoked flag; `updateVehicleKey` adds a key without revoking the old one (two live keys); re-registration is allowed while self-owned; `changeOwner(id, 0)` restores self-control.

## Coverage check

ABI public/external functions: 17. Covered: **17 / 17**. Uncovered: none. Off-chain provider methods recorded as `onchain:false` steps: `register_vehicle`, `update_credential`, `get_credential`, `revoke_credential`, `check_revocation_status`, `check_revocation_status_by_address`, `resolve_identity`, `resolve_identity_from_address`, `sign_message`, `verify_message`.
