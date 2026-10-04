# erc-725 — ERC-725 basic proxy account (plan S7 demos)

**Identity model.** Each vehicle identity is its own `CVIN_SCBasedAccOrID_DID_ERC725Basic` contract: deployment is creation, the contract address is the identifier, and `owner()` (the deployer) plays the ERC-734 MANAGEMENT key. It carries an ERC-734-style key store (`addKey`/`getKey`/`getKeys`/`removeKey`) but no data store, no claims and an `execute` that only emits an event.

Run: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725/demos/<family>.js`.

| Family | Demo | Functions exercised | Measured? (manifest) |
|---|---|---|---|
| creation | `demos/creation.js` | constructor (deploy = create), `owner`, `getKeys` (empty), `transferOwnership` (foreign-owner path) | implemented (creation = deployment, counted as createIdentity) |
| controller | `demos/controller.js` | `owner`, `transferOwnership` (incl. to zero — no guard), `renounceOwnership`, `addKey`/`getKey` (stale MANAGEMENT key after rotation) | no (benchmark transferOwnership uses it) |
| keys-delegates | `demos/keys-delegates.js` | `addKey` ×4 purposes (MANAGEMENT/ACTION/CLAIM/ENCRYPTION) and types (ECDSA/RSA), `getKey`, `getKeys`, `removeKey` (compaction, duplicate, non-existent) | **yes** (`addKey`) |
| revocation | `demos/revocation.js` | `removeKey` with 7 keys, `getKey` after, `renounceOwnership` as the only identity-level exit, `getKeys` survive renounce | implemented (sub-identity only) |
| signed-execution | `demos/signed-execution.js` | `execute` (CALL to a real target: no side effect), `execute` self-`transferOwnership` (not applied), `approve` (no-op stub), `owner` | implemented (not measured) |

## Asymmetry notes

- **Creation: deployed.** One contract per vehicle (≈519k gas, ≈7× the ERC-1056 "create"); no shared registry, so nothing indexes vehicles and the VIN is not stored anywhere (VIN linkage n/a).
- **Veracity / automation.** The chain enforces only `msg.sender == owner` on every mutation. It does **not** enforce ERC-734 semantics: keys are descriptive records, not authorisation (a listed MANAGEMENT key cannot act; the stale key of a previous owner stays listed). `execute` performs no call and verifies no signature, so the `Executed` log is an intent record a verifier cannot trust. Keys carry no expiry; key revocation is an O(1) `getKey` read; identity-level revocation does not exist (owner()==0 after `renounceOwnership` is a convention).
- **Cryptography / hashing.** No signature verification on-chain. Key ids are opaque `bytes32` (the adapter uses `keccak256(abi.encode(address))`, the ERC-734 convention); `keyType` 1 = ECDSA, 2 = RSA is informational only.
- **Implemented but not compared.** `renounceOwnership`, `execute`, `approve`, key purposes other than 1 and 3, `getKeys` enumeration.
- **Observed defects / surprises.** `execute` is a stub (emits only; L1 "signed-op 28,358" is the price of an event); `approve` is callable by anyone and does nothing; duplicate `addKey` pushes the id twice and a later `removeKey` leaves a dangling index entry whose `getKey` is zeros; `removeKey` of a non-existent key succeeds and emits `KeyRemoved`; `transferOwnership(0)` has no zero guard; `getKeys` order changes on removal.

## Coverage check

ABI public/external functions: 9. Covered: **9 / 9**. Uncovered: none. (`CVINExecuteTarget` from the ERC-725xy helpers is used only as an observable call target.)
