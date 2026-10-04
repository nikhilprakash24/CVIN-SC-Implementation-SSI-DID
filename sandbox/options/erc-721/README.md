# ERC-721 — feature demos (plan S7)

**Identity model.** A vehicle identity is one NFT: `tokenId` on a shared collection, bound both ways to a 17-char VIN (`CVINVehicleNFT`), with on-chain metadata, service-record and transfer-history storage; *ownership is control* — whoever holds the token controls the identity, and the manufacturer/admin roles (OZ AccessControl) create, annotate and deactivate it. The two "DID" variants (`CVIN_NFT_DID_ERC721`, hand-rolled `_Monolithic`) are plain Ownable ERC-721 + ERC-2981 collections with caller-chosen token ids, no VIN and no status — the first adds a toll scenario (`recordEntry`/`payToll`).

Run one demo: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/<family>.js` (one JSON line per step, summary line last, non-zero exit on failure). `demos/_lib.js` is the shared step printer, not a demo. 219 steps, 62 of them mined transactions.

| Family | Demo | Functions exercised | Measured in comparison? |
|---|---|---|---|
| Identity creation | `demos/creation.js` | `mintVehicle`, `getTotalVehicles`, `totalSupply`, `tokenByIndex`, `ownerOf`, `vehicleMetadata`, `tokenURI`, `name`, `symbol`, `supportsInterface`; DID: `mint`, `name`, `symbol`, `ownerOf`, `supportsInterface`; Mono: `mint`, `name`, `symbol`, `ownerOf`, `balanceOf`, `supportsInterface` | yes (`mintVehicle`) |
| Ownership / controller | `demos/controller.js` | `ownerOf`, `balanceOf`, `getVehiclesByOwner`, `tokenOfOwnerByIndex`, `transferFrom`, `safeTransferFrom` (3- and 4-arg, hook on contract recipient), `getOwnershipChain`; DID + Mono: `owner`, `transferOwnership`, `renounceOwnership`, `transferFrom`, both `safeTransferFrom` | no (transfer is measured under token economics / `transferFrom`) |
| Attributes / data store | `demos/attributes.js` | `grantServiceCenterRole`, `addServiceRecord`, `getServiceRecords`, `serviceRecords`, `tokenURI`, `vehicleMetadata`; DID: `mint`, `tokenURI`, `recordEntry`, `getEntryTimestamp`; Mono: `tokenURI` | no (`addServiceRecord` is the benchmark's attribute analogue) |
| Revocation / status | `demos/revocation.js` | `isVehicleActive`, `deactivateVehicle`, `ownerOf`, `transferFrom`, `addServiceRecord`, `revokeRole`, `hasRole`, `getServiceRecords` | no (`deactivateVehicle` is the benchmark's revoke) |
| Lifecycle / history | `demos/lifecycle-history.js` | `getTransferHistory`, `transferHistory`, `getOwnershipChain`, `getServiceRecords`, `serviceRecords`, log replay (`VehicleTransferred`, `ServiceRecordAdded`); DID: `recordEntry`, `getEntryTimestamp`, `EntryRecorded` replay | no |
| Authorisation / roles | `demos/authorisation-roles.js` | `DEFAULT_ADMIN_ROLE`, `MANUFACTURER_ROLE`, `INSPECTOR_ROLE`, `SERVICE_CENTER_ROLE`, `hasRole`, `getRoleAdmin`, `grantManufacturerRole`, `grantInspectorRole`, `grantServiceCenterRole`, `grantRole`, `revokeRole`, `renounceRole`, `mintVehicle`, `addServiceRecord` | no (role grants are excluded as setup) |
| Token economics | `demos/token-economics.js` | `approve`, `getApproved`, `setApprovalForAll`, `isApprovedForAll`, `transferFrom`, `safeTransferFrom`, `balanceOf`, `totalSupply`; DID: `royaltyInfo`, `approve`, `getApproved`, `setApprovalForAll`, `isApprovedForAll`, `balanceOf`, `payToll` (real ether), `renounceOwnership`; Mono: `royaltyInfo`, `approve`, `getApproved`, `setApprovalForAll`, `isApprovedForAll`, `transferFrom`, `safeTransferFrom`, `balanceOf` | yes (`approve` only) |
| VIN linkage | `demos/vin-linkage.js` | `getTokenIdFromVIN`, `getVINFromTokenId`, `vinToTokenId`, `tokenIdToVIN`, `mintVehicle` | no |
| DID / resolution | `demos/did-resolution.js` | `getVehicleDID`, `supportsInterface`, adapter `resolve` (10 views) | no (`resolve` is adapter-synthesised, gas 0) |

Not applicable (no demo): keys/delegates (`approve` delegates transfer rights, not a verification key), claims, signed execution, off-chain creation, off-chain messaging.

## Asymmetry notes

- **Creation: minted.** An identity exists only after a `MANUFACTURER_ROLE` transaction (`mintVehicle`, 542 k gas in L1); it is never implicit. The DID variants mint with a caller-chosen `tokenId`, so "VIN linkage" there is an off-chain promise.
- **Veracity and automation.** The chain enforces *who* may write (roles, `ownerOf`, approvals, 17-char VIN length and VIN uniqueness, receiver hooks on safe transfers) but never *what*: service records and token URIs are free-form strings, inspections cannot be written at all (`INSPECTOR_ROLE` gates nothing), `active=false` does not block transfers or records, and nothing is signed. A verifier must read `isVehicleActive`, parse the record strings, trust the role holders, and fetch the URIs off-chain; transfer history and ownership chain, by contrast, are first-class on-chain data (storage *and* logs).
- **Cryptography / hashing.** No application-level hashing or signature scheme: role ids are `keccak256("<NAME>_ROLE")`, token ids are counters (or caller-chosen), the VIN is stored in plain text as a `string` mapping key. Authorisation is purely `msg.sender`-based (no EIP-191, no digests). ERC-165 interface ids are the only cryptographic-looking identifiers.
- **Implemented but never compared.** Enumeration (`getVehiclesByOwner`, `tokenOfOwnerByIndex`, `tokenByIndex`), operator approvals and approved-party transfers, safe-transfer receiver hooks, the full transfer-history/ownership-chain store, service records as a lifecycle log, `renounceRole`/`getRoleAdmin`, the DID helper, and the entire `CVIN_NFT_DID_ERC721` / Monolithic surface: ERC-2981 `royaltyInfo`, the toll scenario (`recordEntry`, `getEntryTimestamp`, `payToll` with ether), Ownable admin hand-over and renounce.

## Coverage check

Union of functions exercised across the nine demos vs the public/external ABI: **CVINVehicleNFT 44/44, CVIN_NFT_DID_ERC721 20/20, CVIN_NFT_DID_ERC721_Monolithic 17/17 — no uncovered function.**

Behaviour worth flagging (all reproduced by the demos): `payToll` after `renounceOwnership` forwards ether to `address(0)` (burned); VINs are not normalised, so a lower-cased VIN mints a second identity; `deactivateVehicle` is advisory (transfers and records continue) and irreversible; `INSPECTOR_ROLE` is a dead role; `RoleAdminChanged`, listed in the manifest, is never emitted.
