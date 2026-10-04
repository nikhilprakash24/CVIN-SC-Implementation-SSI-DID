# LSP8 — feature demos (plan S7)

**Identity model.** A vehicle identity is one bytes32 token `tokenId = keccak256(bytes(VIN))` on a representative LSP8 collection whose contract `owner` is the issuing authority (mints, burns, writes data) while the token owner is the vehicle owner (transfers with the LSP8 5-arg `transfer(from,to,tokenId,force,data)`). Every fact about the vehicle lives in an ERC-725Y/LSP2-style per-token key/value store (`setDataForTokenId` / `getDataForTokenId`, with batch variants and well-known `DATA_KEY_*` constants); LSP1 universal-receiver hooks, operators and the collection-level ERC-725Y store are intentionally omitted.

Run one demo: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/<family>.js`. `demos/_lib.js` is the shared step printer. 137 steps, 34 mined transactions.

| Family | Demo | Functions exercised | Measured in comparison? |
|---|---|---|---|
| Identity creation | `demos/creation.js` | `mintVehicle` (+ guards), `tokenIdForVIN`, `exists`, `tokenOwnerOf`, `getDataForTokenId`, `DATA_KEY_VIN`, `totalSupply`, `balanceOf`, `tokenIdsOf`, `name`, `symbol`, `owner` | yes (`mintVehicle`) |
| Ownership / controller | `demos/controller.js` | `tokenOwnerOf`, `owner`, `transfer` (force true/false, EOA vs contract recipients, every guard), `tokenIdsOf`, `transferOwnership` (authority hand-over), `mintVehicle` | no (the 5-arg `transfer` is measured as transfer / controller-change) |
| Attributes / data store | `demos/attributes.js` | `DATA_KEY_VIN`, `DATA_KEY_REGISTRATION`, `DATA_KEY_INSPECTION`, `DATA_KEY_INSURANCE`, `setDataForTokenId`, `getDataForTokenId`, `setDataBatchForTokenIds`, `getDataBatchForTokenIds` | no (`setDataForTokenId` is the benchmark's updateAttribute) |
| Claims / credentials | `demos/claims.js` | `DATA_KEY_INSPECTION`, `setDataForTokenId` (signed attestation stored, forged one stored too), `getDataForTokenId`, adapter `addClaim` / `revoke(claimId)`, off-chain `verifyMessage` | yes (adapter `addClaim` = `setDataForTokenId(DATA_KEY_INSPECTION)`) |
| Revocation / status | `demos/revocation.js` | `revokeVehicle` (authority and token owner), `exists`, `tokenOwnerOf`, `totalSupply`, `balanceOf`, `tokenIdsOf`, `getDataForTokenId` (stale data), `setDataForTokenId`, `mintVehicle` (re-mint) | yes (`revokeVehicle`) |
| Lifecycle / history | `demos/lifecycle-history.js` | all writes plus log replay of `TokenIdDataChanged`, `DataChanged`, `Transfer`, `VehicleMinted`, `VehicleRevoked`, `OwnershipTransferred`, adapter `resolve` | no |
| Token economics | `demos/token-economics.js` | `totalSupply`, `balanceOf` across mint/transfer/burn, `transfer`, `revokeVehicle`; ABI proof that `authorizeOperator`/`revokeOperator`/`isOperatorFor`/`getOperatorsOf`/`royaltyInfo` do not exist | no |
| VIN linkage | `demos/vin-linkage.js` | `DATA_KEY_VIN`, `tokenIdForVIN`, `mintVehicle`, `getDataForTokenId`, `exists`, `setDataForTokenId` (VIN key overwritten) | no |

Not applicable (no demo): keys/delegates (operators not implemented), signed execution, authorisation roles (single `owner`), DID helpers (adapter forms `did:cvin:lsp8:…`), off-chain creation, off-chain messaging.

## Asymmetry notes

- **Creation: minted.** `mintVehicle` by the authority (149 k gas in L1). The identifier is *derivable before the mint* (`tokenIdForVIN` is pure), which is the closest any token option gets to a counterfactual id — but nothing exists until the transaction. The VIN is upper-cased and ISO 3779-checked (17 chars, no I/O/Q; check digit not enforced) in both `mintVehicle` and `tokenIdForVIN` since the D13 fix.
- **Veracity and automation.** The chain enforces authority-only writes, token-owner-only transfers, the `force` flag against code-less recipients, and existence checks. It does not probe recipients (no LSP1), so `force=false` to a contract that can never move the token succeeds; it never verifies the signatures stored in attestation slots; it keeps only the latest value per key (odometer rollbacks are accepted; history is in `TokenIdDataChanged` logs); and it leaves a burned token's data in place, so a re-minted VIN inherits stale attestations. A verifier must re-hash the stored VIN against the tokenId, replay logs for key enumeration and history, and decide off-chain which attestation signers to trust.
- **Cryptography / hashing.** `keccak256` for the token id (`bytes(normalised VIN)` — an off-chain verifier must upper-case before hashing, exactly as the contract does) and the data keys (`keccak256("CVIN_<NAME>")`); any signature inside a data value is an application convention (the demo uses EIP-191 personal-sign over `keccak256(payload)`, verified off-chain with `ethers.verifyMessage`). Authorisation itself is `msg.sender`-based.
- **Implemented but never compared.** Batch data read/write, the `force=false` path and contract recipients, `tokenIdsOf` enumeration, token-owner self-revocation, the `data` payload on transfers/burns, authority hand-over (`transferOwnership`), `exists`, and the three well-known keys other than the VIN.

## Coverage check

Union of functions exercised across the eight demos vs the public/external ABI: **CVINVehicleLSP8 21/21 — no uncovered function.**

Behaviour worth flagging (reproduced). *Fixed 2026-10-04 — D13 (`docs/DEFECT_LOG.md`), `creation.js` and `vin-linkage.js` assert it and mark the steps `FIXED (D13)`:* the lower-cased VIN derives the same tokenId and can no longer mint a second identity; short VINs and I/O/Q are rejected. *Still open (D12):* `DATA_KEY_VIN` is an ordinary key the authority can overwrite, after which the stored VIN no longer hashes to the tokenId; a revoked VIN can be re-minted with its old data keys intact (inherited inspection); `force=false` does not protect against the collection contract itself as recipient (token stuck).
