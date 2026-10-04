# Grand sandbox report

Generated 2026-10-04T22:31:10Z at commit `7404e94` by `python3 sandbox/grand/run.py all`.

## Stages

| Stage | ok | result | s |
|---|---|---|---:|
| smoke | ✓ | {} | 4.2 |
| L1 | ✓ | {'passing': 99, 'failing': 0} | 5.3 |
| L1+L2 | ✓ | {'passing': 386, 'failing': 0} | 13.8 |
| L3+L4 | ✓ | {'passed': 94} | 7.9 |
| demos | ✓ | {'demos': 92, 'steps': 1722, 'flagged': 62, 'failures': []} |  |

## Reports produced

- `report/asymmetry.md` — union table from the manifests (declared stances)
- `report/L1-asymmetry.md` — mechanism × option table from the L1 tests (observed), with manifest agreement
- `report/demos.md` — every implemented feature exercised, with gas and flagged observations
- `docs/DEFECT_LOG.md` — what the sandbox found

## asymmetry.md

# Feature asymmetry — union table from the per-option manifests

M = measured in the comparison or an experiment · I = implemented but not used by the comparison · — = not applicable (reason in the manifest)

| Capability family | Baseline: centralized registry | Baseline: IEEE 1609.2-style PKI | CVIN-Combined | ERC-1056 / uPort-style | ERC-1056 / vehicle profile | ERC-1155 | ERC-4337 | ERC-721 | ERC-725 | ERC-725xy | ERC-735 | LSP8 | MOBI VID I + II |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Identity creation (explicit) | M | — | — | I | M | M | I | M | I | I | I | M | M |
| Ownership / controller change | M | — | M | I | I | I | M | I | I | I | I | I | M |
| Key / delegate management | — | — | M | M | I | — | M | — | M | — | — | — | M |
| Attributes / data store | — | — | I | I | I | I | I | I | — | M | — | I | I |
| Claims / credentials | I | I | M | — | — | M | — | — | — | — | M | I | M |
| Revocation / status | I | I | M | I | M | M | — | I | I | I | I | M | M |
| Delegated / signed (off-chain-authorised) execution | — | — | — | I | — | — | I | — | I | I | — | — | — |
| Lifecycle events / history | M | I | I | I | M | I | I | I | — | I | I | I | M |
| Authorisation / roles | I | — | I | I | — | I | — | I | — | — | I | — | I |
| Token economics (approvals, royalties, payments) | — | — | — | — | — | I | — | M | — | — | — | I | — |
| VIN linkage | I | — | I | I | — | I | — | I | — | I | I | I | I |
| DID / resolution helpers | — | — | I | I | M | — | — | I | — | — | — | — | M |
| Off-chain creation (identity exists before any transaction) | I | I | I | I | — | — | — | — | — | — | — | — | — |
| Message signing / verification (off-chain hot path) | — | M | — | — | I | — | — | — | — | — | — | — | I |

Options: 13 · families: 14 · cells: 182 · empty: 0 · unreviewed: 172/182

Per option — M / I / — counts:

- Baseline: centralized registry (in-process): M 3 · I 5 · — 6  (surface: {'functions': 0, 'events': 0, 'provider_methods': 15})
- Baseline: IEEE 1609.2-style PKI (in-process): M 1 · I 4 · — 9  (surface: {'functions': 0, 'events': 0, 'provider_methods': 12})
- CVIN-Combined (ERC-1056 + ERC-735 hybrid): M 4 · I 6 · — 4  (surface: {'functions': 18, 'events': 6, 'provider_methods': 0})
- ERC-1056 / uPort-style: M 1 · I 10 · — 3  (surface: {'functions': 49, 'events': 6, 'provider_methods': 0})
- ERC-1056 / vehicle profile: M 4 · I 4 · — 6  (surface: {'functions': 17, 'events': 4, 'provider_methods': 15})
- ERC-1155: M 3 · I 6 · — 5  (surface: {'functions': 34, 'events': 12, 'provider_methods': 0})
- ERC-4337: M 2 · I 4 · — 8  (surface: {'functions': 13, 'events': 7, 'provider_methods': 0})
- ERC-721: M 2 · I 7 · — 5  (surface: {'functions': 52, 'events': 15, 'provider_methods': 0})
- ERC-725: M 1 · I 4 · — 9  (surface: {'functions': 9, 'events': 4, 'provider_methods': 0})
- ERC-725xy: M 1 · I 6 · — 7  (surface: {'functions': 25, 'events': 5, 'provider_methods': 0})
- ERC-735: M 1 · I 6 · — 7  (surface: {'functions': 17, 'events': 8, 'provider_methods': 0})
- LSP8: M 2 · I 6 · — 6  (surface: {'functions': 21, 'events': 6, 'provider_methods': 0})
- MOBI VID I + II (application profile): M 7 · I 4 · — 3  (surface: {'functions': 57, 'events': 13, 'provider_methods': 11})


## L1-asymmetry.md

# L1 identity mechanisms — cross-option asymmetry (from tests)

Generated 2026-10-04T22:27:26.307Z by `cd 1_blockchain-identity && npx hardhat test test/L1-identity-mechanisms/*.test.js` (11 options × 9 mechanisms, 99 records; each record is a fresh deploy + create).

✓ gas = the adapter ran the mechanism (exact gasUsed of the measured transaction; 0 = no transaction, e.g. implicit creation or a view) · — = NotApplicable (reason below) · ✗ = adapter error or failed assertion · · = not run

| Mechanism | cvin-combined | erc-1056-uport | erc-1056-vehicle | erc-1155 | erc-4337 | erc-721 | erc-725 | erc-725xy | erc-735 | lsp8 | mobi-vid |
|---|---|---|---|---|---|---|---|---|---|---|---|
| create | ✓ 0 | ✓ 77814 | ✓ 54655 | ✓ 107729 | ✓ 759088 | ✓ 545197 | ✓ 519384 | ✓ 1730753 | ✓ 1598928 | ✓ 152453 | ✓ 276671 |
| controller-change | ✓ 68813 | ✓ 68842 | ✓ 53882 | ✓ 89793 | ✓ 28527 | ✓ 179562 | ✓ 28378 | ✓ 28822 | ✓ 28756 | ✓ 80544 | ✓ 37735 |
| key-or-delegate | ✓ 72262 | ✓ 72219 | ✓ 35044 | — | ✓ 47569 | — | ✓ 137096 | — | — | — | ✓ 35309 |
| attribute | ✓ 51576 | ✓ 52016 | ✓ 37180 | ✓ 96478 | ✓ 94471 | ✓ 120137 | — | ✓ 95166 | — | ✓ 100283 | ✓ 37485 |
| claim | ✓ 333803 | — | — | ✓ 80131 | — | — | — | — | ✓ 320397 | ✓ 148816 | ✓ 287085 |
| revoke | ✓ 73215 | ✓ 32868 | ✓ 75370 | ✓ 72614 | — | ✓ 27677 | ✓ 41399 | ✓ 33870 | ✓ 78012 | ✓ 41812 | ✓ 75382 |
| transfer | — | — | — | ✓ 89793 | ✓ 28527 | ✓ 179562 | — | — | — | ✓ 80544 | ✓ 180105 |
| signed-op | — | ✓ 96065 | — | — | ✓ 69393 | — | ✓ 28358 | ✓ 76352 | — | — | — |
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

*(truncated; see `report/L1-asymmetry.md`)*

## demos.md

# Demos — every implemented feature exercised, per option and family

steps = contract calls demonstrated (gas is the sum of the on-chain ones) · flagged = steps whose note marks a potential defect or observation (see docs/DEFECT_LOG.md)

| Option | Family | ok | steps | gas (sum) | flagged | s |
|---|---|---|---:|---:|---:|---:|
| cvin-combined | attributes | ✓ | 13 | 1,898,506 | 1 | 3.0 |
| cvin-combined | authorisation-roles | ✓ | 13 | 2,110,592 | 2 | 2.0 |
| cvin-combined | claims | ✓ | 29 | 2,717,215 | 1 | 2.2 |
| cvin-combined | controller | ✓ | 14 | 1,867,447 | 0 | 2.1 |
| cvin-combined | did-resolution | ✓ | 12 | 2,142,645 | 0 | 2.2 |
| cvin-combined | keys-delegates | ✓ | 13 | 1,630,869 | 1 | 2.0 |
| cvin-combined | lifecycle-history | ✓ | 14 | 1,875,531 | 0 | 3.0 |
| cvin-combined | offchain-creation | ✓ | 11 | 1,695,486 | 0 | 2.1 |
| cvin-combined | revocation | ✓ | 15 | 2,313,378 | 0 | 2.1 |
| cvin-combined | vin-linkage | ✓ | 10 | 2,024,473 | 0 | 2.1 |
| erc-1056-uport | attributes | ✓ | 31 | 3,207,931 | 0 | 2.8 |
| erc-1056-uport | authorisation-roles | ✓ | 13 | 2,839,940 | 1 | 2.2 |
| erc-1056-uport | controller | ✓ | 30 | 3,197,110 | 1 | 2.4 |
| erc-1056-uport | creation | ✓ | 15 | 2,895,902 | 0 | 2.0 |
| erc-1056-uport | did-resolution | ✓ | 14 | 2,907,751 | 0 | 2.2 |
| erc-1056-uport | keys-delegates | ✓ | 22 | 3,155,682 | 0 | 2.3 |
| erc-1056-uport | lifecycle-history | ✓ | 13 | 2,992,681 | 0 | 2.5 |
| erc-1056-uport | offchain-creation | ✓ | 13 | 2,873,063 | 0 | 2.7 |
| erc-1056-uport | revocation | ✓ | 21 | 3,394,035 | 2 | 2.4 |
| erc-1056-uport | signed-execution | ✓ | 13 | 1,253,961 | 0 | 2.2 |
| erc-1056-uport | vin-linkage | ✓ | 15 | 2,878,296 | 2 | 2.6 |
| erc-1056-vehicle | attributes | ✓ | 10 | 949,706 | 0 | 2.0 |
| erc-1056-vehicle | claims | ✓ | 10 | 764,425 | 0 | 3.0 |
| erc-1056-vehicle | controller | ✓ | 13 | 850,065 | 1 | 2.4 |
| erc-1056-vehicle | creation | ✓ | 13 | 985,891 | 1 | 2.5 |
| erc-1056-vehicle | did-resolution | ✓ | 11 | 836,433 | 0 | 2.5 |
| erc-1056-vehicle | keys-delegates | ✓ | 11 | 909,286 | 1 | 2.0 |
| erc-1056-vehicle | lifecycle-history | ✓ | 13 | 965,015 | 0 | 3.2 |
| erc-1056-vehicle | offchain-messaging | ✓ | 10 | 839,795 | 1 | 2.3 |
| erc-1056-vehicle | revocation | ✓ | 24 | 981,757 | 0 | 2.3 |
| erc-1155 | attributes | ✓ | 13 | 221,810 | 1 | 2.5 |
| erc-1155 | authorisation-roles | ✓ | 19 | 637,364 | 2 | 2.4 |
| erc-1155 | claims | ✓ | 28 | 627,064 | 3 | 2.1 |
| erc-1155 | controller | ✓ | 46 | 819,716 | 1 | 2.3 |
| erc-1155 | creation | ✓ | 20 | 215,458 | 0 | 2.1 |
| erc-1155 | lifecycle-history | ✓ | 14 | 596,226 | 0 | 2.2 |
| erc-1155 | revocation | ✓ | 18 | 378,104 | 2 | 2.2 |
| erc-1155 | token-economics | ✓ | 13 | 117,555 | 2 | 2.3 |
| erc-1155 | vin-linkage | ✓ | 14 | 233,583 | 0 | 2.1 |
| erc-4337 | attributes | ✓ | 15 | 302,272 | 0 | 2.0 |
| erc-4337 | controller | ✓ | 21 | 257,662 | 0 | 2.9 |
| erc-4337 | creation | ✓ | 14 | 21,062 | 0 | 2.1 |
| erc-4337 | keys-delegates | ✓ | 19 | 205,742 | 1 | 2.5 |
| erc-4337 | lifecycle-history | ✓ | 15 | 295,592 | 0 | 2.1 |
| erc-4337 | signed-execution | ✓ | 25 | 258,512 | 0 | 2.2 |
| erc-721 | attributes | ✓ | 24 | 451,966 | 0 | 2.1 |
| erc-721 | authorisation-roles | ✓ | 22 | 859,358 | 2 | 1.9 |
| erc-721 | controller | ✓ | 37 | 1,103,280 | 0 | 2.9 |
| erc-721 | creation | ✓ | 38 | 1,284,083 | 0 | 2.5 |
| erc-721 | did-resolution | ✓ | 8 | 0 | 0 | 2.1 |
| erc-721 | lifecycle-history | ✓ | 18 | 568,094 | 0 | 1.9 |
| erc-721 | revocation | ✓ | 16 | 338,694 | 2 | 2.9 |
| erc-721 | token-economics | ✓ | 44 | 943,147 | 0 | 2.0 |
| erc-721 | vin-linkage | ✓ | 15 | 500,311 | 0 | 3.0 |

*(truncated; see `report/demos.md`)*
