# Defect Log — latent defects found in the research code, and their status

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Started:** 2026-10-04 (gathers findings from 2026-09-24 onward)
**Why this file exists:** the sandbox and the verification passes keep finding defects that
no earlier test reached. Each is a *result* for the implementation chapter — the
veracity/automation asymmetry made concrete — and several bear on security claims.
Status: **fixed** (with the commit) · **open** (with severity and the planned treatment).
Severity: **H** affects a thesis claim or a security property · **M** wrong behaviour,
bounded impact · **L** cosmetic or advisory.

## A. Found by the verification passes (2026-09-24), all fixed

| # | Where | Defect | Sev | Status |
|---|---|---|---|---|
| D1 | `CVINVehicleDIDRegistry` | service-endpoint and delegate functions unreachable (owner check vs wrapper as sender) | H | fixed `708302a` (`vehicleOwnerOf`) |
| D2 | `CVIN_NFT_DID_ERC721_Monolithic` | `_balances += tokenId` instead of `+= 1` | M | fixed `708302a` |
| D3 | ERC-1056 test | EIP-191 signing against a raw-`ecrecover` contract | L (test) | fixed `708302a` |
| D4 | `erc1056_provider.py` | key resolution returned the placeholder `"0x04..."`; blockchain verification could never succeed | H | fixed `1d4ad07` |
| D5 | `erc1056_provider.py` | vehicle transactions deployer-signed, rejected by `onlyOwner` | M | fixed `1d4ad07` |
| D6 | `CVINVehicleCredential1155` | `issuerTransferCredential(from == to)` deleted the VIN mapping | H | fixed `a798370` (+ regression test) |

## B. Found by the S7 feature demos (2026-10-04) — open unless marked

**Fix pass of 2026-10-04 (After-Action Report 05):** every **H** item except D7 and D11b
is fixed — D10, D11, D13, D18, D21, D22, D25a/b — with 47 Hardhat + 6 Python regression
tests, the results of record re-executed (register #31 lists the 22 gas cells that
moved) and 92 demos updated to assert the fixed behaviour. D16 is partly fixed through
D21. The remaining open items are listed in §C with the author decisions they need.

| # | Where | Defect | Sev | Treatment |
|---|---|---|---|---|
| D7 | `CVINVehicleCredential1155` | an issuer that is also an approved operator can move the BIRTH_CERT with standard `safeTransferFrom`, which does **not** re-bind `vehicleVIN`/`vinHashToVehicle`; a later `issuerTransferCredential` propagates an empty VIN (`keccak256("")`) | **H** | fix: route all BIRTH_CERT moves through the re-binding path or block standard transfers of it (it is meant to be soulbound); add to the security scenarios |
| D8 | `CVINVehicleCredential1155` | standard transfers reach unregistered addresses; burning the BIRTH_CERT orphans other credentials; any issuer can revoke any issuer's credentials; `URI` event never emitted | M | fix the first three with the D7 change; document the issuer model |
| D9 | `CVIN_NFT_DID_ERC721.payToll` | after `renounceOwnership`, tolls are sent to `address(0)` (burned) | M | guard `owner() != address(0)`; one-line fix + test |
| D10 | `MOBIVIDRegistry.getVehicleDID` | returns `did:ethr:0x7a69:<40 hex>` **without `0x`** on the address — non-conformant `did:ethr`; the adapter's `resolve()` copies it | **H** (conformance claim) | **fixed `65a143f`**: string builder emits `0x`; L2 MOBIVID regression test checks the did:ethr ABNF; `mobi-vid/demos/did-resolution.js` asserts the full shape. Still to do: re-run the external DID suite with a `did:ethr` minted by this registry (the suite currently runs on the resolver's own fixtures) |
| D11 | `mobi_vid_provider.verify_message` | verified against the public key **embedded in the message**, so an impostor signing with its own key under the vehicle's DID passed | **H** (security claim) | **fixed 2026-10-04 (registration-record binding)**: the key is resolved from the vehicle's registration record by `vehicle_did`; an embedded key must match it; unknown and revoked vehicles rejected (on-chain `isRevoked` consulted when a contract is attached); 6 regression tests in `sandbox/py-suites/L3-ssi/test_mobi_provider_key_binding.py`. Note: the SUMO harness verifies through the VC layer, not this provider, so the V2V results were never on this path |
| D11b | `mobi_vid_provider` registration | the vehicle's key is generated *after* the on-chain birth and never anchored on-chain, so a verifier without the registration record has no authoritative key to bind to | **H** (completes D11) | open: at registration, publish the key as an ERC-1056 attribute on the identity (`did/pub/Secp256k1/veriKey/hex`) sent by the identity's controller, and have `verify_message` fall back to the on-chain attribute when the local record is absent; needs the D21 registry changes to land first |
| D12 | `CVINVehicleLSP8` | `DATA_KEY_VIN` overwritable by the authority (VIN no longer hashes to the tokenId); a revoked VIN can be re-minted and inherits stale data keys; `force=false` to the collection itself succeeds (no LSP1 probing) | M | make the VIN key immutable after mint; clear data keys on revoke; document the LSP1 gap |
| D13 | ERC-721, ERC-1155, LSP8 | VINs are case-sensitive: the lower-cased VIN mints a second identity (no normalisation; ISO 3779 checks only on length, ERC-721 only) | **H** (Sybil-adjacent) | **fixed `241642e`**: identical `_normalizeVIN` helpers in `CVINVehicleNFT`, `CVINVehicleCredential1155` (+ `vinHashOf`/`vehicleForVIN` views) and `CVINVehicleLSP8` — 17 bytes, a–z upper-cased, bitmap check against 0–9/A–Z minus I/O/Q; the ISO 3779 check digit is deliberately **not** enforced (manufacturer-specific weighting outside North America; recorded in the contract NatSpec); lookups normalise too. 15 regression tests; mint gas +2.7k/+3.4k/+3.0k (register #31). Fallout: test VINs beginning with "VIN" were invalid (the I) — L1 helper and smoke runner now use "CVN" |
| D14 | ERC-721 | `INSPECTOR_ROLE` gates nothing; `deactivateVehicle` is advisory and irreversible | L | document or remove |
| D15 | ERC-4337 | `recoverOwner` leaves the guardian in place (a permanent super-owner); the minimal EntryPoint rolls back the nonce on inner revert | M | document as a property of the minimal harness; consider clearing the guardian on recovery |
| D16 | MOBI VID registries | `revokeIdentity` repeatable (moves `revokedAt`); `changeOwner` ignores the revoked flag and bypasses ownership history; `revokeAttribute` accepts a mismatched value; the OWNER issuer role is registry-wide; `transferRegistryAuthority` emits no event; `nonce` is dead state | M | **partly fixed `65a143f`** (via D21, the registries share `ERC1056Registry`): `revokeIdentity` now reverts on a second call and `changeOwner` reverts for a revoked identity. **Open**: `changeOwner` still bypasses MOBI's ownership history (needs odometer/authority inputs — author decision), mismatched `revokeAttribute` value, registry-wide OWNER role, silent `transferRegistryAuthority`, dead `nonce` |
| D17 | OpenZeppelin 5.x ERC-1155 | self-`setApprovalForAll` accepted | L | upstream behaviour; note only |
| D18 | `CVINVehicleDIDRegistry.setVehicleAttributes` | passes `type(uint256).max` as validity; `EthereumDIDRegistry.setAttribute` computes `block.timestamp + validity` → arithmetic panic; the eight-attribute birth record is **unreachable** through the wrapper | **H** | **fixed `65a143f`**: `PERMANENT_ATTRIBUTE_VALIDITY = 100 * 365 days`; the eight-attribute birth record is reachable through the wrapper (83,290 gas in the L2 test; `erc-1056-uport/demos/attributes.js` asserts all eight `DIDAttributeChanged` with `validTo = now + validity`). Consequence for the chapter: "permanent" attributes are 100-year attributes — the resolver treats them as valid, and the expiry date is on-chain rather than implicit |
| D19 | `CVINVehicleDIDRegistry` | after `transferVehicleOwnership` the wrapper stays ERC-1056 `identityOwner` with no release function; the new owner cannot act on the registry directly | M | add a release/hand-back function; document the custody model |
| D20 | `CVINVehicleDIDRegistry.createVehicleDID` | an owner that already has a VIN silently overwrites `didToVIN` (reverse map not one-to-one) | M | require no existing mapping or support many VINs explicitly |
| D21 | `ERC1056Registry` (vehicle profile) | `DIDRevoked` carries no `previousChange`, so `revokeIdentity` **severs the `changed()` linked list** that `did:ethr` resolution walks; `revokeIdentity` repeatable; `changeOwner` not gated by the revoked flag; `updateVehicleKey` adds a key without revoking the old one | **H** (resolution correctness) | **fixed `65a143f`** (decision D-F, revocation terminal): `DIDRevoked(identity, revokedAt, previousChange)`; a second `revokeIdentity` reverts "Identity already revoked"; every mutator including `revokeDelegate`/`revokeAttribute` carries `notRevoked`; the MOBI copy is byte-identical (CI-checked). L2 regression tests walk the `changed()` list through the revocation; `erc-1056-vehicle/demos/lifecycle-history.js` walks 5 events to genesis with no cut. Gas: `revokeIdentity` +547, `changeOwner` +2,213 (register #31). **Open**: `updateVehicleKey` still adds a key without revoking the old one (a rotation would need an explicit revoke of the prior `veriKey` attribute) |
| D22 | `CVINCombinedIdentity` | `addClaim`/`removeClaim` bump `changed` without an ERC-1056 event — the linked list is cut at every claim operation (the adapter range-scans to compensate); `revokeDelegate` stores a timestamp; no EIP-2 low-s guard; no identity-level revocation | **H** (resolution correctness) | **fixed `65a143f`** for the list cut: `DIDClaimChanged(identity, claimId, topic, removed, previousChange)` on `addClaim`/`removeClaim`; the resolver walk completes (L2 CVINCombined test; `cvin-combined/demos/lifecycle-history.js` walks the full 5-event history). `addClaim` +2,328 gas (register #31). **Open**: `revokeDelegate` timestamp semantics, no EIP-2 low-s guard, no identity-level revocation |
| D23 | `CVIN_SCBasedAccOrID_DID_ERC725Basic` | `execute` is a stub (emits `Executed`, performs no call) — the L1 signed-op figure (28,358 gas) is the cost of an event; `approve` is a public no-op; duplicate `addKey` leaves a dangling `getKeys` entry after `removeKey`; `transferOwnership(0)` unguarded | M | manifest reason corrected to "stub" (`2b38536`, reviewed flag kept). **Open**: implement or remove `execute`; fix key bookkeeping; guard `transferOwnership(0)` |
| D24 | `CVINVehicleERC725XY` | unrestricted DELEGATECALL can overwrite slot 0 (`_owner`) — spec-conformant but bricks the identity; `setData` payable; VIN freely rewritable and duplicable across accounts | M | document the executor hazard; VIN immutability after creation |
| D25 | `CVINVehicleClaimHolder` | no issuer whitelist (an impostor `MANUFACTURER_CERT` is accepted); a `VIN_ATTESTATION` for a different VIN accepted on topic 1; raw-digest signatures rejected while CVIN-Combined rejects EIP-191 — the two claim contracts are signature-incompatible | **H** (veracity) | **D25a/D25b fixed `ad470b6`**: `authorizeIssuer`/`revokeIssuer`/`isAuthorizedIssuer` (owner-only; the owner is exempt as self-issuer); `addClaim` checks signature → issuer authorised → topic-1 VIN binding (`_encodesHolderVin`: the trailing `bytes(vin).length` bytes of the claim data must hash to `vinHash`). 14 regression tests; callers updated (adapter, security fixture, gas and scaling benchmarks); deploy +227,534 gas, claim ops moved (register #31); `erc-735` demos assert the reverts (`5778651`). **D25c open — author decision**: the signature scheme (ERC-735 raw digest vs CVIN-Combined EIP-191) is recorded in the contract NatSpec; recommendation EIP-191 across both, matching the VC layer and ERC-4337 |
| D26 | both ERC-1056 registries and the hybrid | `changeOwner(id, address(0))` restores self-control instead of locking the identity | M | treat zero as "lock" or reject |

## C. What is still open after the fix pass, and what each needs

| Item | Sev | Blocked on | Suggested treatment |
|---|---|---|---|
| D7 / D8 (ERC-1155 BIRTH_CERT transfers) | **H** / M | nothing — mechanical | override `_update` to block standard transfers of `BIRTH_CERT` (soulbound) and route every move through the re-binding path; one scenario in the security harness |
| D11b (vehicle key never anchored on-chain) | **H** | D21 landed — now unblocked | publish `did/pub/Secp256k1/veriKey/hex` at registration from the controller; `verify_message` falls back to the on-chain attribute |
| D9 (`payToll` after renounce) | M | nothing | one-line guard + test |
| D12 (LSP8 VIN key overwritable) | M | author: should the VIN data key be immutable after mint? | immutable VIN key; clear data keys on revoke |
| D15 (ERC-4337 guardian persists) | M | author: is "guardian as permanent super-owner" the intended recovery model? | document, or clear the guardian on recovery |
| D16 rest (ownership history on `changeOwner`) | M | author: odometer/authority inputs for the history entry | route `changeOwner` through `transferOwnership` or forbid it on MOBI identities |
| D19 (wrapper custody after transfer) | M | author: custody model | release function |
| D20 (one owner, many VINs) | M | author: policy | require no existing mapping, or support many |
| D23 (`execute` stub) | M | author: implement or drop the L1 signed-op cell for ERC-725 basic | — |
| D24 (unrestricted DELEGATECALL) | M | author: document as the spec's executor hazard | VIN immutability after creation |
| D25c (signature scheme) | design | author decision — recommendation EIP-191 | one scheme across claim contracts |
| D26 (`changeOwner(0)`) | M | author: lock or reject | — |
| D14, D17 | L | — | document |
| D10 follow-up | — | nothing | external DID suite run on a registry-minted `did:ethr` |

## D. How the log is used

- A defect with severity **H** blocks any chapter claim that depends on the affected
  path until it is fixed or the claim is narrowed (D10 → conformance; D11 → MOBI V2V
  security; D13 → Sybil resistance of token-shaped options).
- Each fix lands with a regression test in the relevant L2 per-option suite or the
  security harness, and this table is updated with the commit.
- The chapter on the feature asymmetry cites this log as evidence that "implemented"
  surface carries risk the comparison never priced — the asymmetry budget's security
  column.
