# L1 identity mechanisms — cross-option asymmetry (from tests)

Generated 2026-10-04T05:40:36.116Z by `cd 1_blockchain-identity && npx hardhat test test/L1-identity-mechanisms/*.test.js` (11 options × 9 mechanisms, 99 records; each record is a fresh deploy + create).

✓ gas = the adapter ran the mechanism (exact gasUsed of the measured transaction; 0 = no transaction, e.g. implicit creation or a view) · — = NotApplicable (reason below) · ✗ = adapter error or failed assertion · · = not run

| Mechanism | cvin-combined | erc-1056-uport | erc-1056-vehicle | erc-1155 | erc-4337 | erc-721 | erc-725 | erc-725xy | erc-735 | lsp8 | mobi-vid |
|---|---|---|---|---|---|---|---|---|---|---|---|
| create | ✓ 0 | ✓ 77792 | ✓ 54639 | ✓ 103881 | ✓ 759088 | ✓ 542474 | ✓ 519384 | ✓ 1730753 | ✓ 1371394 | ✓ 149430 | ✓ 276671 |
| controller-change | ✓ 68813 | ✓ 68842 | ✓ 51669 | ✓ 83704 | ✓ 28527 | ✓ 179562 | ✓ 28378 | ✓ 28822 | ✓ 28690 | ✓ 80576 | ✓ 35456 |
| key-or-delegate | ✓ 72262 | ✓ 72219 | ✓ 35044 | — | ✓ 47569 | — | ✓ 137096 | — | — | — | ✓ 35265 |
| attribute | ✓ 51576 | ✓ 52016 | ✓ 37180 | ✓ 94150 | ✓ 94471 | ✓ 120137 | — | ✓ 95166 | — | ✓ 100282 | ✓ 37463 |
| claim | ✓ 331461 | — | — | ✓ 57115 | — | — | — | — | ✓ 314543 | ✓ 148815 | ✓ 287041 |
| revoke | ✓ 71322 | ✓ 32868 | ✓ 74823 | ✓ 37417 | — | ✓ 27677 | ✓ 41399 | ✓ 33870 | ✓ 69438 | ✓ 41838 | ✓ 74836 |
| transfer | — | — | — | ✓ 83704 | ✓ 28527 | ✓ 179562 | — | — | — | ✓ 80576 | ✓ 179826 |
| signed-op | — | ✓ 96053 | — | — | ✓ 69405 | — | ✓ 28358 | ✓ 76352 | — | — | — |
| resolve | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |

Per mechanism: create ok 11 / na 0 / fail 0 · controller-change ok 11 / na 0 / fail 0 · key-or-delegate ok 6 / na 5 / fail 0 · attribute ok 9 / na 2 / fail 0 · claim ok 5 / na 6 / fail 0 · revoke ok 10 / na 1 / fail 0 · transfer ok 5 / na 6 / fail 0 · signed-op ok 4 / na 7 / fail 0 · resolve ok 11 / na 0 / fail 0

## N/A reasons

### key-or-delegate

- **erc-1155**: no key/delegate model on ERC-1155: setApprovalForAll() is an operator approval for token moves, not a verification key (manifest: Key / delegate management not-applicable)
- **erc-721**: no key/delegate model on ERC-721: approve()/setApprovalForAll() delegate transfer rights only, not a verification key (manifest: Key / delegate management not-applicable)
- **erc-725xy**: ERC-725 X/Y has a single owner and no key/delegate model; OPERATION_DELEGATECALL is an executor opcode, not identity delegation
- **erc-735**: no key/delegate model in ERC-735 (keys are deferred to ERC-734; a single owner plays the MANAGEMENT key)
- **lsp8**: no key/delegate model: operator authorization (authorizeOperator/revokeOperator) is not implemented in this representative LSP8, and operators would delegate token moves, not verification keys (manifest: Key / delegate management not-applicable)

### attribute

- **erc-725**: no attribute/data store in the ERC-725 basic proxy (ERC-725Y setData is the erc-725xy option)
- **erc-735**: no attribute store in ERC-735; the closest analogue is a claim (addClaim)

### claim

- **erc-1056-uport**: ERC-1056 stores no claims on-chain; the Claims family is only the SVC_CREDENTIAL_SERVICE endpoint attribute (use setAttribute); credentials live off-chain
- **erc-1056-vehicle**: no on-chain claim function; credentials are off-chain W3C VCs handled by erc1056_provider.py (update/get/revoke_credential)
- **erc-4337**: no on-chain claim/credential model in ERC-4337: the account validates UserOperations and stores attributes, it does not hold claims (manifest: Claims / credentials not-applicable)
- **erc-721**: no claim/credential model on ERC-721: inspector/service-center roles write unsigned records, there is no signed claim (manifest: Claims / credentials not-applicable)
- **erc-725**: no claim storage; claims live in the companion ERC-735 claim holder (erc-735 option)
- **erc-725xy**: no claim model in ERC-725 X/Y; claims live in the ERC-735 claim holder

### revoke

- **erc-4337**: no identity-level revocation in ERC-4337: the account contract persists; only the recovery guardian can be cleared via setGuardian(0) (manifest: Revocation / status not-applicable) _(prep: addKeyOrDelegate; sub-identity revoke(addKeyOrDelegate handle) ok gas=25429 setGuardian(0): guardian (recovery delegate) revoked)_

### transfer

- **cvin-combined**: no token in the hybrid; control moves with changeOwner (changeController)
- **erc-1056-uport**: ERC-1056 has no token to transfer; the DID is the address and control moves with changeOwner (changeController)
- **erc-1056-vehicle**: ERC-1056 has no token to transfer; control moves with changeOwner (changeController)
- **erc-725**: identity is a contract account, not a token; ownership moves with transferOwnership (changeController); approve() is an unimplemented stub
- **erc-725xy**: identity is a contract account, not a token; ownership moves with transferOwnership (changeController)
- **erc-735**: identity is a contract, not a token; ownership moves with transferOwnership (changeController)

### signed-op

- **cvin-combined**: no *Signed meta-transaction entry points in CVINCombinedIdentity; issuer signatures are verified in addClaim (authorisation of a claim, not delegated execution)
- **erc-1056-vehicle**: ERC1056Registry declares a nonce mapping but exposes no *Signed meta-transaction entry point (no changeOwnerSigned / addDelegateSigned / setAttributeSigned)
- **erc-1155**: no off-chain-authorised execution on ERC-1155: no permit, meta-transaction or signed entry point (manifest: Delegated / signed execution not-applicable)
- **erc-721**: no off-chain-authorised execution on ERC-721: no permit, meta-transaction or signed entry point (manifest: Delegated / signed execution not-applicable)
- **erc-735**: no meta-transaction or execute surface in ERC-735; all mutations are owner msg.sender-gated
- **lsp8**: no off-chain-authorised execution on LSP8: no permit, meta-transaction or signed entry point (manifest: Delegated / signed execution not-applicable)
- **mobi-vid**: no signed (meta-transaction) execution: the ERC1056Registry base declares nonce but implements no changeOwnerSigned/addDelegateSigned/setAttributeSigned; attestEvent verifies an EIP-191 signature but is a role-gated direct call by the attester (manifest lists this family as implemented via `nonce` only)

## Manifest stance vs observed outcome

Family per mechanism: create → "Identity creation (explicit)" / "Off-chain creation (identity exists before any transaction)"; controller-change → "Ownership / controller change"; key-or-delegate → "Key / delegate management"; attribute → "Attributes / data store"; claim → "Claims / credentials"; revoke → "Revocation / status"; transfer → "Token economics (approvals, royalties, payments)" / "Ownership / controller change"; signed-op → "Delegated / signed (off-chain-authorised) execution". `resolve` is adapter-synthesised for every option and is not compared.

Agreements: 88 of 88. Disagreements (0; manifests were not edited):

- none
