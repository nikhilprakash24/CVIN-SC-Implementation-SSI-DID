# erc-735 — ERC-735 claim holder (plan S7 demos)

**Identity model.** One `CVINVehicleClaimHolder` contract per vehicle: deployment with the VIN is creation, the contract address is the identifier, `vin`/`vinHash` are immutable, and a single `owner` plays the ERC-734 MANAGEMENT key. Trusted issuers sign attestations off-chain; the owner anchors them as claims whose issuer signature is verified **on-chain at add time** (EIP-191 ECDSA), so later verifiers read `getClaim`/`claimExists` in O(1).

Run: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/<family>.js`.

| Family | Demo | Functions exercised | Measured? (manifest) |
|---|---|---|---|
| creation | `demos/creation.js` | constructor(vin) (empty-VIN revert), `vin`, `vinHash`, `owner`, `getClaimIdsByTopic` (empty), `transferOwnership` (foreign-owner path) | implemented (deployment counted as createIdentity) |
| controller | `demos/controller.js` | `owner`, `transferOwnership` (zero guard; no renounce), `claimExists` after sale, `addClaim`/`removeClaim` access after rotation | no (benchmark transferOwnership) |
| claims | `demos/claims.js` | `VIN_ATTESTATION/MANUFACTURER_CERT/INSPECTION/INSURANCE`, `ECDSA_SCHEME`, `addClaim` (3 issuers, in-place update → `ClaimChanged`), `getClaim`, `getClaimIdsByTopic`, `claimExists`, `removeClaim` (owner- and issuer-side); negatives: wrong signer, tampered data, raw-digest signature, high-s malleability, short sig, scheme ≠ 1, zero issuer, non-owner | **yes** (`addClaim`, `removeClaim`) |
| revocation | `demos/revocation.js` | `removeClaim` owner-side / issuer-side, index compaction, zero tombstone, no expiry, no identity-level revocation | implemented (sub-identity only) |
| lifecycle-history | `demos/lifecycle-history.js` | `ClaimRequested`+`ClaimAdded` → `ClaimChanged` ×2 → `ClaimRemoved` (full claim), `OwnershipTransferred`; log-scan timeline vs current state | implemented (not measured) |
| authorisation-roles | `demos/authorisation-roles.js` | `MANUFACTURER_CERT` as a role topic, owner-only anchoring, per-claim issuer rights, impostor manufacturer accepted | implemented (not measured) |
| vin-linkage | `demos/vin-linkage.js` | `vin`, `vinHash`, `VIN_ATTESTATION` claim, attested-vs-asserted check, mismatching attestation accepted, duplicate-VIN identity | implemented (not measured) |

## Asymmetry notes

- **Creation: deployed**, VIN fixed in the constructor (≈1.37M). No registry: VIN uniqueness across identities is unenforceable; `vinHash` is the indexed key for an off-chain VIN→contract index.
- **Veracity / automation.** Chain enforces: owner-only anchoring (holder consent — even the issuer cannot push a claim), **issuer signature validity** (ecrecover, EIP-2 low-s, 65 bytes, scheme 1), claim binding to (this contract, topic, data), per-claim removal rights (owner or that issuer). It does **not** enforce: that an issuer is an accredited authority (any key can sign a `MANUFACTURER_CERT`), currency (no expiry), consistency between a `VIN_ATTESTATION` payload and `vin()`, identity-level status (no revoke, no renounce, no freeze).
- **Cryptography / hashing.** `claimId = keccak256(issuer ‖ topic)` (one claim per issuer per topic); digest `keccak256(abi.encodePacked(identity, topic, data))` signed **with the EIP-191 `"\x19Ethereum Signed Message:\n32"` prefix** (personal_sign-compatible) — incompatible with CVIN-Combined's raw-digest convention (shown: a raw signature is rejected here); `vinHash = keccak256(bytes(vin))`; ERC-1271 contract issuers unsupported.
- **Implemented but not compared.** `ClaimChanged` in-place updates, issuer-side revocation, `claimExists`, `getClaimIdsByTopic`, the INSPECTION/INSURANCE topics, the malleability guard, `ClaimRequested` compatibility events.
- **Observed surprises.** No issuer whitelist (two competing manufacturer certificates coexist; a verifier must pick by address); a topic-1 attestation for a different VIN is accepted; removed claims leave no tombstone (zeros = never issued); `getClaimIdsByTopic` order changes on removal; the identity can never be made ownerless or revoked.

## Coverage check

ABI public/external functions: 14. Covered: **14 / 14**. Uncovered: none.
