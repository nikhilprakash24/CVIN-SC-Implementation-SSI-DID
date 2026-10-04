# cvin-combined — ERC-1056 + ERC-735 hybrid (plan S7 demos)

**Identity model.** One shared `CVINCombinedIdentity` registry in which every address is an identity (ERC-1056 side: `identityOwner` defaults to self, event-only attributes, stored time-bound delegates, a `changed` pointer) and the same `identityOwner` gates an ERC-735-style on-chain claim store for the safety-critical subset (VIN, manufacturer/type approval, inspection) whose issuer signature is verified at `addClaim` time so contracts can later check `hasValidClaim`/`getClaim` in O(1). Creation is implicit (0 gas); no meta-transactions and no identity-level revocation.

Run: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/<family>.js`.

| Family | Demo | Functions exercised | Measured? (manifest) |
|---|---|---|---|
| controller | `demos/controller.js` | `identityOwner`, `changeOwner` (gates attributes AND claims), `changeOwner(0)` probe, no `owners`/`changeOwnerSigned` | **yes** (`changeOwner`) |
| keys-delegates | `demos/keys-delegates.js` | `addDelegate`, `delegates`, `validDelegate`, on-chain expiry, `revokeDelegate` (validity = now) | **yes** (`revokeDelegate`) |
| attributes | `demos/attributes.js` | `setAttribute` (rotation, firmware hash), `revokeAttribute` (validTo = 0), `changed`; VIN as attribute vs as claim | implemented (benchmark createIdentity/updateAttribute use `setAttribute`) |
| claims | `demos/claims.js` | `CLAIM_TOPIC_VIN/MANUFACTURER/INSPECTION`, `SCHEME_ECDSA`, `addClaim` (raw-digest sig; in-place re-add), `getClaim`, `getClaimIdsByTopic`, `hasValidClaim`, `removeClaim`; negatives: EIP-191 sig, wrong identity binding, tampered data, 64-byte sig, scheme ≠ 1, zero issuer, non-owner | **yes** (`addClaim`, `removeClaim`) |
| revocation | `demos/revocation.js` | `revokeAttribute`, `revokeDelegate`, `removeClaim` owner-side and issuer-side (funded issuer), `hasValidClaim` after; gas ladder | **yes** (`revokeDelegate`) |
| lifecycle-history | `demos/lifecycle-history.js` | `changed` walk; cut by `addClaim`/`removeClaim`; `ClaimAdded`/`ClaimRemoved` indexed by identity | implemented (not measured) |
| authorisation-roles | `demos/authorisation-roles.js` | `CLAIM_TOPIC_MANUFACTURER` as role, `hasValidClaim(id, topic, trustedIssuer)`, impostor accepted, per-claim issuer rights | implemented (not measured) |
| vin-linkage | `demos/vin-linkage.js` | `CLAIM_TOPIC_VIN` via adapter `create({anchorVin})`, `getClaim`, `hasValidClaim`, `setAttribute` alternative, duplicate VIN | implemented (not measured) |
| did-resolution | `demos/did-resolution.js` | `identityOwner`, `getClaimIdsByTopic`, adapter `resolve` (event walk + claims) before/after delegate expiry | implemented (not measured) |
| offchain-creation | `demos/offchain-creation.js` | fresh address: `identityOwner`, `changed`, `hasValidClaim`, `getClaimIdsByTopic`; OEM pre-signs the VIN claim; first tx is `addClaim` | implemented (L1 create = 0; manifest auto-stance said n/a) |

## Asymmetry notes

- **Creation: implicit** (0 gas) — a factory can generate the key and the OEM can sign the VIN claim before the vehicle ever touches the chain; the first transaction may already be a trusted-claim anchoring. The comparison labels the first `setAttribute` as createIdentity.
- **Veracity / automation.** Chain enforces: one controller for both halves, delegate validity (`validDelegate`), **issuer signature validity and binding to (registry, identity, topic, data)** at `addClaim`, holder consent, per-claim removal rights. On-chain verifiers get O(1) answers (`hasValidClaim`, `validDelegate`, `getClaim`) for the safety-critical subset; everything else (keys, services, attributes) needs an off-chain event replay. Not enforced: issuer accreditation (any key can issue a manufacturer claim), claim expiry (`hasValidClaim` = "present"), VIN uniqueness, identity-level revocation, signature malleability.
- **Cryptography / hashing.** `claimId = keccak256(issuer ‖ topic)`; claim digest `keccak256(abi.encodePacked(registry, identity, topic, data))` signed as a **raw secp256k1 digest, no EIP-191 prefix** (mirrors ERC-1056 meta-tx signing; HSM/signingKey, not personal_sign) — the opposite convention of the ERC-735 claim holder, so the two are signature-incompatible (demonstrated both ways). Attribute names/delegate types are `keccak256` strings. No nonce, no meta-transactions.
- **Implemented but not compared.** Delegate expiry, attribute revocation, issuer-side claim withdrawal, in-place claim re-add, `hasValidClaim` as an on-chain gate, VIN anchoring as a claim, the two verification paths in one identity.
- **Observed defects / surprises.** `addClaim`/`removeClaim` bump `changed` without an ERC-1056 event, so the `previousChange` linked list is **cut at every claim operation** (a did:ethr resolver finds nothing; the adapter range-scans); `revokeDelegate` leaves the timestamp in storage (no refund, resolver must test `<= now`); re-adding a claim emits `ClaimAdded` (no `ClaimChanged`); no EIP-2 low-s guard; `changeOwner(id, 0)` restores self-control; no identity-level revocation at all (the vehicle-profile registry has one).

## Coverage check

ABI public/external functions: 18. Covered: **18 / 18**. Uncovered: none.
