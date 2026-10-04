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

| # | Where | Defect | Sev | Treatment |
|---|---|---|---|---|
| D7 | `CVINVehicleCredential1155` | an issuer that is also an approved operator can move the BIRTH_CERT with standard `safeTransferFrom`, which does **not** re-bind `vehicleVIN`/`vinHashToVehicle`; a later `issuerTransferCredential` propagates an empty VIN (`keccak256("")`) | **H** | fix: route all BIRTH_CERT moves through the re-binding path or block standard transfers of it (it is meant to be soulbound); add to the security scenarios |
| D8 | `CVINVehicleCredential1155` | standard transfers reach unregistered addresses; burning the BIRTH_CERT orphans other credentials; any issuer can revoke any issuer's credentials; `URI` event never emitted | M | fix the first three with the D7 change; document the issuer model |
| D9 | `CVIN_NFT_DID_ERC721.payToll` | after `renounceOwnership`, tolls are sent to `address(0)` (burned) | M | guard `owner() != address(0)`; one-line fix + test |
| D10 | `MOBIVIDRegistry.getVehicleDID` | returns `did:ethr:0x7a69:<40 hex>` **without `0x`** on the address — non-conformant `did:ethr`; the adapter's `resolve()` copies it | **H** (conformance claim) | fix the string builder; re-run the external DID suite with a `did:ethr` from this registry |
| D11 | `mobi_vid_provider.verify_message` | verified against the public key **embedded in the message**, so an impostor signing with its own key under the vehicle's DID passed | **H** (security claim) | **fixed 2026-10-04 (registration-record binding)**: the key is resolved from the vehicle's registration record by `vehicle_did`; an embedded key must match it; unknown and revoked vehicles rejected (on-chain `isRevoked` consulted when a contract is attached); 6 regression tests in `sandbox/py-suites/L3-ssi/test_mobi_provider_key_binding.py`. Note: the SUMO harness verifies through the VC layer, not this provider, so the V2V results were never on this path |
| D11b | `mobi_vid_provider` registration | the vehicle's key is generated *after* the on-chain birth and never anchored on-chain, so a verifier without the registration record has no authoritative key to bind to | **H** (completes D11) | open: at registration, publish the key as an ERC-1056 attribute on the identity (`did/pub/Secp256k1/veriKey/hex`) sent by the identity's controller, and have `verify_message` fall back to the on-chain attribute when the local record is absent; needs the D21 registry changes to land first |
| D12 | `CVINVehicleLSP8` | `DATA_KEY_VIN` overwritable by the authority (VIN no longer hashes to the tokenId); a revoked VIN can be re-minted and inherits stale data keys; `force=false` to the collection itself succeeds (no LSP1 probing) | M | make the VIN key immutable after mint; clear data keys on revoke; document the LSP1 gap |
| D13 | ERC-721, ERC-1155, LSP8 | VINs are case-sensitive: the lower-cased VIN mints a second identity (no normalisation; ISO 3779 checks only on length, ERC-721 only) | **H** (Sybil-adjacent) | normalise and validate VINs (ISO 3779: 17 chars, no I/O/Q, check digit) in every mint path; add a scenario |
| D14 | ERC-721 | `INSPECTOR_ROLE` gates nothing; `deactivateVehicle` is advisory and irreversible | L | document or remove |
| D15 | ERC-4337 | `recoverOwner` leaves the guardian in place (a permanent super-owner); the minimal EntryPoint rolls back the nonce on inner revert | M | document as a property of the minimal harness; consider clearing the guardian on recovery |
| D16 | MOBI VID registries | `revokeIdentity` repeatable (moves `revokedAt`); `changeOwner` ignores the revoked flag and bypasses ownership history; `revokeAttribute` accepts a mismatched value; the OWNER issuer role is registry-wide; `transferRegistryAuthority` emits no event; `nonce` is dead state | M | fix the first two (they affect lifecycle-history veracity); document the rest |
| D17 | OpenZeppelin 5.x ERC-1155 | self-`setApprovalForAll` accepted | L | upstream behaviour; note only |
| D18 | `CVINVehicleDIDRegistry.setVehicleAttributes` | passes `type(uint256).max` as validity; `EthereumDIDRegistry.setAttribute` computes `block.timestamp + validity` → arithmetic panic; the eight-attribute birth record is **unreachable** through the wrapper | **H** | fix: a bounded validity (or `type(uint256).max - block.timestamp`); regression test |
| D19 | `CVINVehicleDIDRegistry` | after `transferVehicleOwnership` the wrapper stays ERC-1056 `identityOwner` with no release function; the new owner cannot act on the registry directly | M | add a release/hand-back function; document the custody model |
| D20 | `CVINVehicleDIDRegistry.createVehicleDID` | an owner that already has a VIN silently overwrites `didToVIN` (reverse map not one-to-one) | M | require no existing mapping or support many VINs explicitly |
| D21 | `ERC1056Registry` (vehicle profile) | `DIDRevoked` carries no `previousChange`, so `revokeIdentity` **severs the `changed()` linked list** that `did:ethr` resolution walks; `revokeIdentity` repeatable; `changeOwner` not gated by the revoked flag; `updateVehicleKey` adds a key without revoking the old one | **H** (resolution correctness) | emit `previousChange`; gate on revoked; regression test through the provider's event walk |
| D22 | `CVINCombinedIdentity` | `addClaim`/`removeClaim` bump `changed` without an ERC-1056 event — the linked list is cut at every claim operation (the adapter range-scans to compensate); `revokeDelegate` stores a timestamp; no EIP-2 low-s guard; no identity-level revocation | **H** (resolution correctness) | emit a change event with `previousChange` on claim ops; low-s check |
| D23 | `CVIN_SCBasedAccOrID_DID_ERC725Basic` | `execute` is a stub (emits `Executed`, performs no call) — the L1 signed-op figure (28,358 gas) is the cost of an event; `approve` is a public no-op; duplicate `addKey` leaves a dangling `getKeys` entry after `removeKey`; `transferOwnership(0)` unguarded | M | manifest reason corrected (stub); implement or remove `execute`; fix key bookkeeping |
| D24 | `CVINVehicleERC725XY` | unrestricted DELEGATECALL can overwrite slot 0 (`_owner`) — spec-conformant but bricks the identity; `setData` payable; VIN freely rewritable and duplicable across accounts | M | document the executor hazard; VIN immutability after creation |
| D25 | `CVINVehicleClaimHolder` | no issuer whitelist (an impostor `MANUFACTURER_CERT` is accepted); a `VIN_ATTESTATION` for a different VIN accepted on topic 1; raw-digest signatures rejected while CVIN-Combined rejects EIP-191 — the two claim contracts are signature-incompatible | **H** (veracity) | issuer registry; bind VIN attestations to the holder's VIN; one signature scheme across claim contracts |
| D26 | both ERC-1056 registries and the hybrid | `changeOwner(id, address(0))` restores self-control instead of locking the identity | M | treat zero as "lock" or reject |

## C. How the log is used

- A defect with severity **H** blocks any chapter claim that depends on the affected
  path until it is fixed or the claim is narrowed (D10 → conformance; D11 → MOBI V2V
  security; D13 → Sybil resistance of token-shaped options).
- Each fix lands with a regression test in the relevant L2 per-option suite or the
  security harness, and this table is updated with the commit.
- The chapter on the feature asymmetry cites this log as evidence that "implemented"
  surface carries risk the comparison never priced — the asymmetry budget's security
  column.
