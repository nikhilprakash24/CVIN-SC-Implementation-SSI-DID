# ERC-1155 — feature demos (plan S7)

**Identity model.** Each ERC-1155 token id is a *credential type* (1 BIRTH_CERT, 2 REGISTRATION, 3 INSPECTION_CERT, 4 INSURANCE_CERT, 5 MAINTENANCE_BADGE — any other uint is accepted too); a vehicle is the *address* that holds one soulbound BIRTH_CERT, indexed by `vehicleVIN` (address → VIN) and `vinHashToVehicle` (keccak256(VIN) → address). All writes and every transfer between two addresses require `ISSUER_ROLE`; holders can only receive, so a controller change is an issuer re-binding the BIRTH_CERT to a new address (the identity address itself changes, which is why the adapter uses the VIN hash as the id).

Run one demo: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/<family>.js`. `demos/_lib.js` is the shared step printer. 155 steps, 59 mined transactions.

| Family | Demo | Functions exercised | Measured in comparison? |
|---|---|---|---|
| Identity creation | `demos/creation.js` | `registerVehicle`, `BIRTH_CERT`…`MAINTENANCE_BADGE`, `isRegistered`, `balanceOf`, `balanceOfBatch`, `vehicleVIN`, `vinHashToVehicle`, `supportsInterface` | yes (`registerVehicle`) |
| Ownership / controller | `demos/controller.js` | `safeTransferFrom`, `safeBatchTransferFrom` (soulbound reverts; issuer-as-operator path; receiver hook), `setApprovalForAll`, `issuerTransferCredential` (incl. the 2026-10-04 self-transfer guard), `balanceOfBatch`, `isRegistered`, `vehicleVIN`, `vinHashToVehicle`, `registerVehicle` | yes (`issuerTransferCredential` of BIRTH_CERT = transfer / controller-change) |
| Attributes / data store | `demos/attributes.js` | `uri`, `setTokenURI` | no (`setTokenURI` is the benchmark's attribute analogue) |
| Claims / credentials | `demos/claims.js` | `ISSUER_ROLE`, `INSPECTION_CERT`, `hasCredential`, `issueCredential` (all types, multi-unit, custom type), `balanceOfBatch`, `grantRole`, `issuerTransferCredential`, `revokeCredential` | yes (`issueCredential`, `revokeCredential`) |
| Revocation / status | `demos/revocation.js` | `revokeCredential` (unit and BIRTH_CERT = deregistration), `hasCredential`, `isRegistered`, `vehicleVIN`, `vinHashToVehicle`, `issueCredential`, `registerVehicle`, `ISSUER_ROLE`, `grantRole`, `revokeRole` | yes (`revokeCredential`) |
| Lifecycle / history | `demos/lifecycle-history.js` | all writes above plus log replay of `VehicleRegistered`, `CredentialIssued`, `CredentialRevoked`, `TransferSingle`, `TransferBatch`, `RoleGranted`, `RoleRevoked`, `RoleAdminChanged` (never emitted) | no |
| Authorisation / roles | `demos/authorisation-roles.js` | `DEFAULT_ADMIN_ROLE`, `ISSUER_ROLE`, `hasRole`, `getRoleAdmin`, `grantRole`, `revokeRole`, `renounceRole`, and every ISSUER-gated write | no |
| Token economics | `demos/token-economics.js` | `balanceOf`, `balanceOfBatch`, `setApprovalForAll`, `isApprovedForAll`, `safeTransferFrom` (operator rejected), `supportsInterface` | no |
| VIN linkage | `demos/vin-linkage.js` | `vehicleVIN`, `vinHashToVehicle`, `registerVehicle`, `issuerTransferCredential`, `revokeCredential` | no |

Not applicable (no demo): keys/delegates, signed execution, DID helpers (the adapter forms `did:cvin:erc1155:…` itself), off-chain creation, off-chain messaging.

## Asymmetry notes

- **Creation: minted.** `registerVehicle` by an issuer mints the BIRTH_CERT (104 k gas in L1). Only emptiness of the VIN is checked — a 5-character VIN is accepted. Deregistration is reversible: the same VIN can be registered again later.
- **Veracity and automation.** The chain enforces the issuer role on every write and transfer, BIRTH_CERT uniqueness per address, VIN-hash uniqueness, and the receiver hook; it enforces nothing about *content*: a credential is `(address, type, amount)` with no issuer, date, expiry or subject stored, so "revoked" and "never issued" read identically and a credential from a since-revoked issuer stays valid. A verifier must replay `CredentialIssued`/`CredentialRevoked` logs to learn who issued what and when, and read the (collection-wide) `uri` documents off-chain. The standard ERC-1155 `URI` event is never emitted, so generic indexers miss metadata changes.
- **Cryptography / hashing.** `keccak256(bytes(vin))` is the only hash (the uniqueness index; plain VIN is also stored and logged); role ids are `keccak256("ISSUER_ROLE")`. No signatures anywhere — authorisation is `msg.sender` + role.
- **Implemented but never compared.** Batch reads/transfers (`balanceOfBatch`, `safeBatchTransferFrom`), the standard transfer path for issuers who are also approved operators, receiver hooks on contract recipients, operator approvals (inert under the soulbound override), credential types 2/4/5 and multi-unit (fungible) issuance, `hasCredential`, `renounceRole`/`getRoleAdmin`, and the self-transfer guard.

## Coverage check

Union of functions exercised across the nine demos vs the public/external ABI: **CVINVehicleCredential1155 29/29 — no uncovered function.**

Behaviour worth flagging (reproduced by `controller.js` and `revocation.js`): an issuer that is also an approved operator can move the BIRTH_CERT through the *standard* `safeTransferFrom`, which does **not** re-bind `vehicleVIN`/`vinHashToVehicle` — the new holder is "registered" with an empty VIN, the index still points to the old address, and a subsequent `issuerTransferCredential` propagates the empty VIN (and maps `keccak256("")`) rather than repairing it; standard transfers also deliver credentials to unregistered addresses; burning the BIRTH_CERT orphans the other credentials on the address; any issuer may revoke another issuer's credentials.
