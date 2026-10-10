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

**Fix passes of 2026-10-04 (After-Action Reports 05 and 06):** every **H** item is fixed —
D10, D11, D11b, D13, D18, D21, D22, D25a/b in pass 05/06 and D7 in pass 06 — plus D8 (first
three parts) and D9, with 66 Hardhat + 13 Python regression tests, the results of record
re-executed after each pass (register #31 and #32 list every cell that moved and why) and
every demo updated to assert the fixed behaviour. D16 is partly fixed through D21. The
remaining open items are listed in §C with the author decisions they need.

| # | Where | Defect | Sev | Treatment |
|---|---|---|---|---|
| D7 | `CVINVehicleCredential1155` | an issuer that is also an approved operator can move the BIRTH_CERT with standard `safeTransferFrom`, which does **not** re-bind `vehicleVIN`/`vinHashToVehicle`; a later `issuerTransferCredential` propagates an empty VIN (`keccak256("")`) | **H** | **fixed `d941ad5`** (decision D-I): the standard `safeTransferFrom` / `safeBatchTransferFrom` entry points revert for everyone; the only inter-address moves are the issuer paths, and `issuerTransferIdentity(from, to)` moves the BIRTH_CERT with every held credential in one `TransferBatch`, re-binding the VIN (`IdentityRebound`). 13 regression tests (`soulboundRebinding.regression.test.js`); security harness `identityHijack` and the recovery scenario now go through the whole-identity path; ERC-1155 demos assert the closed path and the atomic move. Gas: register #32 |
| D8 | `CVINVehicleCredential1155` | standard transfers reach unregistered addresses; burning the BIRTH_CERT orphans other credentials; any issuer can revoke any issuer's credentials; `URI` event never emitted | M | **first three fixed `d941ad5`** (decision D-G): a per-vehicle bitmap of held credential types (types bounded to 1..255, `credentialTypesOf`) lets the contract refuse a BIRTH_CERT burn or lone move while other credentials are held, refuse non-BIRTH credentials to unregistered addresses, and move the identity atomically; `setTokenURI` now emits the standard `URI` event. **Documented, not fixed:** the flat ISSUER_ROLE — any issuer may revoke another issuer's credential, because a fungible balance carries no issuer |
| D9 | `CVIN_NFT_DID_ERC721.payToll` | after `renounceOwnership`, tolls are sent to `address(0)` (burned) | M | **fixed `d941ad5`**: `payToll` reverts "no toll operator (ownership renounced)"; 2 regression tests (`payTollAfterRenounce.regression.test.js`); `erc-721/demos/token-economics.js` asserts the revert |
| D10 | `MOBIVIDRegistry.getVehicleDID` | returns `did:ethr:0x7a69:<40 hex>` **without `0x`** on the address — non-conformant `did:ethr`; the adapter's `resolve()` copies it | **H** (conformance claim) | **fixed `65a143f`**: string builder emits `0x`; L2 MOBIVID regression test checks the did:ethr ABNF; `mobi-vid/demos/did-resolution.js` asserts the full shape. Follow-up done 2026-10-04: external DID suite re-run on `did:ethr:0x7a69:0x2244c598f83916430028a1b3c438c640ca0e0375` minted by `getVehicleDID` on Hardhat — 335/336, same result and same single (did:nft) failure as the fixture run (`docs/conformance/W3C_DID_TEST_SUITE.md` §8) |
| D11 | `mobi_vid_provider.verify_message` | verified against the public key **embedded in the message**, so an impostor signing with its own key under the vehicle's DID passed | **H** (security claim) | **fixed 2026-10-04 (registration-record binding)**: the key is resolved from the vehicle's registration record by `vehicle_did`; an embedded key must match it; unknown and revoked vehicles rejected (on-chain `isRevoked` consulted when a contract is attached); 6 regression tests in `sandbox/py-suites/L3-ssi/test_mobi_provider_key_binding.py`. Note: the SUMO harness verifies through the VC layer, not this provider, so the V2V results were never on this path |
| D11b | `mobi_vid_provider` registration | the vehicle's key is generated *after* the on-chain birth and never anchored on-chain, so a verifier without the registration record has no authoritative key to bind to | **H** (completes D11) | **fixed `d941ad5`** (decision D-H): `MOBIVIDRegistry.anchorVehicleKey` publishes the key as the ERC-1056 attribute `did/pub/secp256k1/veriKey/base64` (100-year validity) — the registering manufacturer once and only before the first sale, the owner at any time; the provider generates the key before the birth and anchors it right after (second transaction, ≈69.8 k gas), and `verify_message` falls back to the anchored attribute (walk from `lastChanged`, cached) when it has no local record. 4 L2 + 7 L3 regression tests; `scripts/test_mobi_vid.py` and a two-provider acceptance (no local record → verified through a 2-hop walk; impostor rejected; on-chain revocation seen) pass against a Hardhat node. Found on the way: the provider's inline ABI lacked `isRevoked`, so the D11 on-chain check could never run through it — the compiled artifact ABI is now loaded first |
| D12 | `CVINVehicleLSP8` | `DATA_KEY_VIN` overwritable by the authority (VIN no longer hashes to the tokenId); a revoked VIN can be re-minted and inherits stale data keys; `force=false` to the collection itself succeeds (no LSP1 probing) | M | **second half fixed by the merge (`bd90004`, review-2 K-8)**: token records carry a generation and the data store is keyed `tokenId => generation => key`, so a revoked and re-minted VIN no longer inherits stale data keys (`lsp8/demos/revocation.js` asserts it). **Open**: `DATA_KEY_VIN` overwritable by the authority; `force=false` to the collection itself (no LSP1 probing) |
| D13 | ERC-721, ERC-1155, LSP8 | VINs are case-sensitive: the lower-cased VIN mints a second identity (no normalisation; ISO 3779 checks only on length, ERC-721 only) | **H** (Sybil-adjacent) | **fixed `241642e`**: identical `_normalizeVIN` helpers in `CVINVehicleNFT`, `CVINVehicleCredential1155` (+ `vinHashOf`/`vehicleForVIN` views) and `CVINVehicleLSP8` — 17 bytes, a–z upper-cased, bitmap check against 0–9/A–Z minus I/O/Q; the ISO 3779 check digit is deliberately **not** enforced (manufacturer-specific weighting outside North America; recorded in the contract NatSpec); lookups normalise too. 15 regression tests; mint gas +2.7k/+3.4k/+3.0k (register #31). Fallout: test VINs beginning with "VIN" were invalid (the I) — L1 helper and smoke runner now use "CVN" |
| D14 | ERC-721 | `INSPECTOR_ROLE` gates nothing; `deactivateVehicle` is advisory and irreversible | L | document or remove |
| D15 | ERC-4337 | `recoverOwner` leaves the guardian in place (a permanent super-owner); the minimal EntryPoint rolls back the nonce on inner revert | M | document as a property of the minimal harness; consider clearing the guardian on recovery |
| D16 | MOBI VID registries | `revokeIdentity` repeatable (moves `revokedAt`); `changeOwner` ignores the revoked flag and bypasses ownership history; `revokeAttribute` accepts a mismatched value; the OWNER issuer role is registry-wide; `transferRegistryAuthority` emits no event; `nonce` is dead state | M | **fixed `65a143f` (via D21) and the merge `bd90004` (review-2 K-3, K-15)**: `revokeIdentity` single-shot; `changeOwner` reverts for a revoked identity and, for a born vehicle, reverts outright ("MOBIVID: use transferVehicleOwnership") so the ownership history can no longer be bypassed; OWNER-role lifecycle events are restricted to the vehicle's current owner. **Open**: mismatched `revokeAttribute` value; silent `transferRegistryAuthority`; dead `nonce` |
| D17 | OpenZeppelin 5.x ERC-1155 | self-`setApprovalForAll` accepted | L | upstream behaviour; note only |
| D18 | `CVINVehicleDIDRegistry.setVehicleAttributes` | passes `type(uint256).max` as validity; `EthereumDIDRegistry.setAttribute` computes `block.timestamp + validity` → arithmetic panic; the eight-attribute birth record is **unreachable** through the wrapper | **H** | **fixed `65a143f`**: `PERMANENT_ATTRIBUTE_VALIDITY = 100 * 365 days`; the eight-attribute birth record is reachable through the wrapper (83,290 gas in the L2 test; `erc-1056-uport/demos/attributes.js` asserts all eight `DIDAttributeChanged` with `validTo = now + validity`). Consequence for the chapter: "permanent" attributes are 100-year attributes — the resolver treats them as valid, and the expiry date is on-chain rather than implicit |
| D19 | `CVINVehicleDIDRegistry` | after `transferVehicleOwnership` the wrapper stays ERC-1056 `identityOwner` with no release function; the new owner cannot act on the registry directly | M | add a release/hand-back function; document the custody model |
| D20 | `CVINVehicleDIDRegistry.createVehicleDID` | an owner that already has a VIN silently overwrites `didToVIN` (reverse map not one-to-one) | M | require no existing mapping or support many VINs explicitly |
| D21 | `ERC1056Registry` (vehicle profile) | `DIDRevoked` carries no `previousChange`, so `revokeIdentity` **severs the `changed()` linked list** that `did:ethr` resolution walks; `revokeIdentity` repeatable; `changeOwner` not gated by the revoked flag; `updateVehicleKey` adds a key without revoking the old one | **H** (resolution correctness) | **fixed `65a143f`** (decision D-F, revocation terminal): `DIDRevoked(identity, revokedAt, previousChange)`; a second `revokeIdentity` reverts "Identity already revoked"; every mutator including `revokeDelegate`/`revokeAttribute` carries `notRevoked`; the MOBI copy is byte-identical (CI-checked). L2 regression tests walk the `changed()` list through the revocation; `erc-1056-vehicle/demos/lifecycle-history.js` walks 5 events to genesis with no cut. Gas: `revokeIdentity` +547, `changeOwner` +2,213 (register #31). **Open**: `updateVehicleKey` still adds a key without revoking the old one (a rotation would need an explicit revoke of the prior `veriKey` attribute) |
| D22 | `CVINCombinedIdentity` | `addClaim`/`removeClaim` bump `changed` without an ERC-1056 event — the linked list is cut at every claim operation (the adapter range-scans to compensate); `revokeDelegate` stores a timestamp; no EIP-2 low-s guard; no identity-level revocation | **H** (resolution correctness) | **fixed `65a143f`, revised by the merge (`bd90004`, decision M-A)**: the review-2 lineage fixed the same cut the other way (K-6: claim ops no longer advance `changed[]`). Merged semantics: claim ops do **not** advance the chain head and still emit `DIDClaimChanged(…, previousChange)` — the walk is never cut and the claim history stays indexable; regression tests and `cvin-combined` demos assert the merged behaviour. **Open**: `revokeDelegate` timestamp semantics, no EIP-2 low-s guard (review-2 K-2 keys revocation on the signed digest for that reason), no identity-level revocation |
| D23 | `CVIN_SCBasedAccOrID_DID_ERC725Basic` | `execute` is a stub (emits `Executed`, performs no call) — the L1 signed-op figure (28,358 gas) is the cost of an event; `approve` is a public no-op; duplicate `addKey` leaves a dangling `getKeys` entry after `removeKey`; `transferOwnership(0)` unguarded | M | manifest reason corrected to "stub" (`2b38536`, reviewed flag kept). **Open**: implement or remove `execute`; fix key bookkeeping; guard `transferOwnership(0)` |
| D24 | `CVINVehicleERC725XY` | unrestricted DELEGATECALL can overwrite slot 0 (`_owner`) — spec-conformant but bricks the identity; `setData` payable; VIN freely rewritable and duplicable across accounts | M | document the executor hazard; VIN immutability after creation |
| D25 | `CVINVehicleClaimHolder` | no issuer whitelist (an impostor `MANUFACTURER_CERT` is accepted); a `VIN_ATTESTATION` for a different VIN accepted on topic 1; raw-digest signatures rejected while CVIN-Combined rejects EIP-191 — the two claim contracts are signature-incompatible | **H** (veracity) | **D25a/D25b fixed `ad470b6`**: `authorizeIssuer`/`revokeIssuer`/`isAuthorizedIssuer` (owner-only; the owner is exempt as self-issuer); `addClaim` checks signature → issuer authorised → topic-1 VIN binding (`_encodesHolderVin`: the trailing `bytes(vin).length` bytes of the claim data must hash to `vinHash`). 14 regression tests; callers updated (adapter, security fixture, gas and scaling benchmarks); deploy +227,534 gas, claim ops moved (register #31); `erc-735` demos assert the reverts (`5778651`). **D25c open — author decision**: the signature scheme (ERC-735 raw digest vs CVIN-Combined EIP-191) is recorded in the contract NatSpec; recommendation EIP-191 across both, matching the VC layer and ERC-4337 |
| D26 | both ERC-1056 registries and the hybrid | `changeOwner(id, address(0))` restores self-control instead of locking the identity | M | treat zero as "lock" or reject |
| D27 | `did_resolver.py` (`did:ethr`) | `verificationMethod[].blockchainAccountId` is emitted as `eip155:0x7a69:<address>` — a hex chain id — whereas CAIP-10 / the did:ethr method specification use the decimal chain reference (`eip155:31337:<address>`). Found by the conformance re-run on a registry-minted DID (`docs/conformance/W3C_DID_TEST_SUITE.md` §8.5); the W3C suite does not check the value, so the 335/336 score is unaffected | L (interop) | **fixed by the merge (`bd90004`, review-2 S-10)**: the merged resolver writes the decimal CAIP-10 chain reference (`eip155:31337:…`); conformance inputs regenerated; external suite 335/336 on the merged resolver (`W3C_DID_TEST_SUITE.md` §12) |

## C. What is still open after the fix pass, and what each needs

| Item | Sev | Blocked on | Suggested treatment |
|---|---|---|---|
| D15 (ERC-4337 guardian persists) | M | author: is "guardian as permanent super-owner" the intended recovery model? | document, or clear the guardian on recovery |
| D19 (wrapper custody after transfer) | M | author: custody model | release function |
| D20 (one owner, many VINs) | M | author: policy | require no existing mapping, or support many |
| D23 (`execute` stub) | M | author: implement or drop the L1 signed-op cell for ERC-725 basic | — |
| D24 (unrestricted DELEGATECALL) | M | author: document as the spec's executor hazard | VIN immutability after creation |
| D25c (signature scheme) | design | author decision — recommendation EIP-191 | one scheme across claim contracts |
| D26 (`changeOwner(0)`) | M | author: lock or reject | — |
| D33 rest (`benchmarks/run.js` `dirtyMeasured` inert) | M | the next metrics-harness run of record (the fix changes the harness's measured-code hash) | root-anchored pathspecs, as in `run_stamp.js`; N-19 |
| D8 rest (flat issuer role: any issuer may revoke another's credential) | M | author: per-issuance issuer records would change the credential model | documented in the contract and the ERC-1155 README |
| D12 rest (`DATA_KEY_VIN` overwritable; no LSP1 probing) | M | author: should the VIN data key be immutable after mint? | immutable VIN key; document the LSP1 gap |
| D16 rest (`revokeAttribute` value, silent `transferRegistryAuthority`, dead `nonce`) | L | — | document |
| D14, D17 | L | — | document |
| D10 follow-up | — | done 2026-10-04 | external DID suite run on a registry-minted `did:ethr`: 335/336, identical to the fixture run (`docs/conformance/W3C_DID_TEST_SUITE.md` §8) |

## D. How the log is used

- A defect with severity **H** blocks any chapter claim that depends on the affected
  path until it is fixed or the claim is narrowed (D10 → conformance; D11 → MOBI V2V
  security; D13 → Sybil resistance of token-shaped options).
- Each fix lands with a regression test in the relevant L2 per-option suite or the
  security harness, and this table is updated with the commit.
- The chapter on the feature asymmetry cites this log as evidence that "implemented"
  surface carries risk the comparison never priced — the asymmetry budget's security
  column.

## E. Cross-reference with the review-2 findings merged on 2026-10-06

The parallel review-2 lineage (`docs/REVIEW_02_CODEBASE.md`, 64 findings K/H/S/T/Q; fixes in
`docs/review02/`) reached several of the same defects by code review. Mapping, after the merge:

| Review-2 finding | This log | Relation |
|---|---|---|
| K-15 `getVehicleDID` 0x prefix | D10 | identical code change, made independently |
| K-1 `setVehicleAttributes` overflow (+ `did` parameter) | D18 | same root cause; K-1 also changed the ABI — merged (M-C) |
| K-3 revocation terminal, `changeOwner` closed for born vehicles | D21, D16 | same semantics; K-3's `changeOwner` closure completes D16 |
| K-13 BIRTH_CERT onto a registered holder | D7 / D8 | strict subset of D7/D8 (K-13 rated the operator bypass Low; D7 closed it as High) |
| K-6 claim ops and `changed[]` | D22 | same defect, mutually exclusive fixes; merged per M-A |
| K-8 generation-keyed LSP8 data store | D12 | fixes D12's second half |
| K-15 OWNER-role scoping (V2) | D16 | closes the "registry-wide OWNER role" part |
| T-4 MOBI verify key from the record | D11 | same defect; D11b (on-chain anchoring) goes further and is kept |
| S-10 decimal CAIP-10 chain id | D27 | fixes D27 |
| K-2 sticky issuer revocation, K-11, K-4, T-1, T-2, T-9, S-1…S-9, Pass-3 replay cache | — | no counterpart here; merged as-is |
| D13 VIN normalisation, D25a/b issuer registry + VIN binding, D9, D11b | — | no counterpart there; kept |

## F. Found by the adversarial review of 2026-10-09 (after-action report 11) — work milestone WM-1

Logged at the close of WM-1 (after-action report 12): report 11's plan said review findings that are
defects of the system under test go here, and they had been recorded only in report 11 §4. Review
finding ids in brackets.

| # | Where | Defect | Sev | Status |
|---|---|---|---|---|
| D28 | `cv2x-testbed/sumo/infrastructure_layer.py` | message fields not bound to the credential: a valid RSU could sign SPaT naming another intersection (and a controller an update for another intersection), accepted on cold and warm paths [B1] | H | fixed `f1f9e37` (binding to `intersectionId`/`stationId`; I2 check (h); register #45) |
| D29 | same | replay inside the 1 s freshness window accepted, to the same and to other receivers, though the design promised a replay check [B2] | H | fixed `f1f9e37` (per-receiver replay cache; I2 check (i)). Residual, by design: a fresh message relayed to a receiver that never heard it is not detectable by a replay cache |
| D30 | same | warm path never re-checked credential expiry; the first fix read `expirationDate` while the VC layer writes `validUntil` and was inert until its test failed [B4] | M | fixed `f1f9e37` |
| D31 | same | an unhashable `sender_did` raised outside the guarded block (crash instead of rejection) [B6] | L | fixed `f1f9e37` |
| D32 | `sumo_identity_integration.py` CLI | `--refresh-k 0` silently meant "never re-check" (k = ∞) [B7] | L | fixed `f1f9e37` (rejected) |
| D33 | `1_blockchain-identity/scripts/lib/run_stamp.js`, `sumo_identity_integration.py` `_environment()`, `1_blockchain-identity/benchmarks/run.js` | producing-code "dirty" flags used repository-relative pathspecs from a subdirectory and could never be true [C1; found by the orchestrator in report 11 R0] | M (rigour: runs of record were vouched for by an inert flag) | partly fixed: `b1d3f72` for the run stamp and the harness header, with a CI probe; **open** for `benchmarks/run.js` (N-19, with the next harness run of record). Every affected run was shown clean on other evidence |
| D34 | `docs/testing/check_stamps.py` | `tree_clean` shown under "dirty" without negation: the inventory read inverted for every Python header [C2] | L | fixed `b1d3f72` |
| D35 | `docs/testing/check_docs_numbers.py`, `stale_numbers.yaml` | scanned 7 files; substring history markers ("old " in "cold ") and number formatting let live superseded figures pass; one listed "stale" value was current (#34) [C3, C4] | M | fixed `36e0309` (87 files, normalisation, whole-word markers) |
| D36 | `docs/figures/make_dashboard_data.py` | `--check` did not cover the published page; status parser not anchored; crux evidence counted non-V and missing rows [C5, C7, C8] | M | fixed `36e0309` |
