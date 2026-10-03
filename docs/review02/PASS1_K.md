# Pass 1 — stream P1-K (contracts): report

**Input:** `docs/REVIEW_02_CODEBASE.md` §1 K and §2; `docs/PLAN_REVIEW_02.md` (P1-K row).
**Base:** `d0fe9f0`. **Commits:** `5ec0c1c` … `faad888` (listed in §6).
**Gate:** Hardhat green: **266 passing, 4 pending** (baseline 242 / 4, +24 new tests,
none removed, skipped or weakened). The nine-standard gas JSON is regenerated and
deterministic over 30 runs. The CI determinism gate passes against the committed JSON.

## 1. What changed, per finding

| ID | File(s) | Change | Revert reason the tests assert |
|---|---|---|---|
| K-1 | `contracts/ERC1056/CVINVehicleDIDRegistry.sol` | `setVehicleAttributes(address did, …)` now takes the DID and is gated by `onlyVehicleOwner(did)`, which uses `vehicleOwnerOf`, the same rule as `setServiceEndpoint` and `addVerificationDelegate`. It requires the registry to hold ERC-1056 control of the DID and the DID to have a VIN. Validity is the finite `VEHICLE_ATTRIBUTE_VALIDITY = 100 * 365 days`, the same as MOBI's `PERMANENT_ATTRIBUTE_VALIDITY`. **This is an ABI change**: no caller in the repo used the old signature, which never succeeded. | `CVINRegistry: not vehicle owner` / `registry does not control DID` / `DID not registered` |
| K-2 | `contracts/ERC735/CVINVehicleClaimHolder.sol`, `contracts/CVINCombined/CVINCombinedIdentity.sol` | When the **issuer** calls `removeClaim`, the contract records `keccak256(issuer, signedDigest)` in the public `revokedClaims` mapping, and `addClaim` rejects that content from then on. | `ERC735: claim revoked by issuer` / `CVINCombined: claim revoked by issuer` |
| K-3 | `contracts/MOBI/ERC1056Registry.sol`, `contracts/MOBI/MOBIVIDRegistry.sol` | The internal `changeOwner`, `revokeDelegate` and `revokeAttribute` now require `!revoked`. `revokeIdentity` is one-shot, because a second call overwrote `revokedAt`. The public `changeOwner` is `virtual`. `MOBIVIDRegistry` overrides it to revert for a vehicle that has a birth certificate, which must go through `transferVehicleOwnership`. An identity with no birth certificate keeps plain ERC-1056 behaviour. V2 inherits the guard. | `MOBIVID: use transferVehicleOwnership` / `Identity is revoked` / `Vehicle identity is revoked` |
| K-4 | `contracts/MOBI/MOBIVIDRegistry.sol` | `registerVehicleBirth` requires `changed[vehicleIdentity] == 0`. Every path that writes DID state advances `changed[]`: changeOwner, setAttribute, addDelegate, revoke\*, revokeIdentity and a previous birth. One SLOAD therefore covers "already owned", "has history" and "revoked". The slot is then re-read warm, so the check costs only about +200 gas. | `MOBIVID: identity already has DID history` |
| K-11 | `CVINCombinedIdentity.sol` | `hasValidClaim` returns false when `issuer == address(0)`. | `expect(false)` |
| K-13 | `contracts/ERC1155/CVINVehicleCredential1155.sol` | `issuerTransferCredential(…, BIRTH_CERT)` rejects a recipient that already holds a BIRTH_CERT. | `CVIN1155: recipient already holds a BIRTH_CERT` |
| K-16 | `ERC721/contracts`, `ERC721/test`, `ERC725/contracts` | Deleted. They are outside the Hardhat `sources`/`tests` paths, and grep found no reference except the broken `test:erc721` script. | — |
| Q-10 | `1_blockchain-identity/package.json` | The `test:<std>` scripts now point at `test/<STD>/`, and each was run green. `test:mobivid` and `test:security` were added. `test:erc725` was removed because no ERC-725 unit suite exists. `deploy` and `deploy:all` named missing files; they are replaced by `deploy:erc1056` (`scripts/deployERC1056.js`), which was run successfully. | — |

`cv2x-testbed/contracts/{ERC1056Registry,MOBIVIDRegistry,MOBIVIDRegistryV2}.sol` are
still byte-identical to `contracts/MOBI/` (checked with `cmp`). `EthereumDIDRegistry.sol`
is untouched (K-12).

**K-2 design choices.**
- **Revocation key: the issuer plus the signed digest.** I did not key on the claimId,
  because that would stop an issuer from ever re-issuing a topic, such as next year's
  inspection. I did not key on the signature bytes either, because they can be
  re-encoded: CVIN-Combined has no low-s check, and ERC-735 accepts both v = 0/1 and
  v = 27/28. A test confirms that a malleated high-s copy of a revoked signature is
  rejected.
- **Re-issuing.** The issuer re-issues by signing new data. Byte-identical data stays
  revoked.
- **Owner self-removal is not a revocation.** It records nothing, and the owner may
  re-anchor the claim later. The owner is only choosing which claims to present; the
  issuer's attestation is still valid.
- **No new event or view.** The first version added a `ClaimRevokedByIssuer` event and
  an `isClaimRevoked` view. Together they cost about 57k extra deployment gas in each
  contract. They were dropped in `3ac47d1`. An issuer removal is the `ClaimRemoved`
  whose sender is the issuer, and verifiers can read `revokedClaims(key)` directly.

## 2. Tests added (24)

Each new test was run against the unfixed contracts first. They all failed, the PoC tests
with "didn't revert" or "expected true to be false". They pass now.

- `test/ERC1056/CVINVehicleDIDRegistry.test.js` (5):
  - all eight attributes are set with validTo = now + 100y;
  - authorisation follows `transferVehicleOwnership`;
  - stranger, no-control and no-VIN callers revert.
- `test/ERC735/CVINVehicleClaimHolder.test.js` (4):
  - **issuer removes, then the owner re-adds with the old signature: reverts;**
  - the key is recorded;
  - the issuer can re-issue with new data;
  - the owner can re-add after its own removal.
- `test/CVINCombined/CVINCombinedIdentity.test.js` (6):
  - the same four K-2 cases;
  - a malleated high-s signature is rejected;
  - K-11: an empty slot is not a valid claim.
- `test/MOBIVID/MOBIVIDRegistry.test.js` (8):
  - K-3: `changeOwner` on a born vehicle reverts (V1 and V2);
  - an unborn identity can still `changeOwner` (positive control);
  - a revoked vehicle blocks transfer, `revokeDelegate`, `revokeAttribute` and a second revoke;
  - a revoked plain identity blocks `changeOwner`;
  - K-4: birth is rejected after `changeOwner`, after `revokeIdentity` (with empty
    attributes too, which was the old bypass) and after `setAttribute`.
- `test/ERC1155/CVINVehicleCredential1155.test.js` (1):
  - K-13: moving a BIRTH_CERT onto a holder that has one reverts, and both VIN bindings
    stay intact.

## 3. Gas: before / after (`gas_benchmark.json`, HEAD `d0fe9f0` → `ffedb4e`)

Conditions: solc 0.8.24, optimizer 200, viaIR, evm cancun, OZ 5.0.2, Hardhat in-process.
19 of 61 cells changed. The other 42 are identical, including every ERC-1056, ERC-721,
ERC-725, ERC-725xy, ERC-4337 and LSP8 cell.

| Standard | Operation | Before | After | Δ | Δ % | Cause |
|---|---|---:|---:|---:|---:|---|
| ERC-735 | createIdentity (per-vehicle deploy) | 1,371,394 | 1,466,088 | +94,694 | +6.9 | K-2 bytecode |
| ERC-735 | addDelegateOrClaim | 290,177 | 292,708 | +2,531 | +0.9 | K-2 cold read of `revokedClaims` |
| ERC-735 | updateAttribute (re-add claim) | 75,160 | 77,691 | +2,531 | +3.4 | K-2 |
| ERC-735 | revoke (owner path) | 72,064 | 72,142 | +78 | +0.1 | K-2 branch |
| ERC-735 | transferOwnership | 28,702 | 28,724 | +22 | 0.1 | dispatch |
| CVIN-Combined | deployRegistry | 1,325,604 | 1,421,834 | +96,230 | +7.3 | K-2, K-11 bytecode |
| CVIN-Combined | addDelegateOrClaim | 289,886 | 292,366 | +2,480 | +0.9 | K-2 |
| CVIN-Combined | revoke (owner path) | 73,688 | 73,795 | +107 | +0.1 | K-2 branch |
| CVIN-Combined | createIdentity | 52,170 | 52,192 | +22 | 0.0 | dispatch |
| CVIN-Combined | updateAttribute | 35,070 | 35,092 | +22 | 0.1 | dispatch |
| CVIN-Combined | transferOwnership | 51,725 | 51,747 | +22 | 0.0 | dispatch |
| ERC-1155 | deployRegistry | 2,277,168 | 2,304,865 | +27,697 | +1.2 | K-13 |
| ERC-1155 | transferOwnership | 83,608 | 83,947 | +339 | +0.4 | K-13 balance check |
| ERC-1155 | createIdentity | 103,881 | 103,913 | +32 | 0.0 | dispatch |
| ERC-1155 | addDelegateOrClaim | 57,115 | 57,147 | +32 | 0.1 | dispatch |
| MOBI-VID-V2 | deployRegistry | 3,952,603 | 4,025,159 | +72,556 | +1.8 | K-3, K-4 |
| MOBI-VID-V2 | revoke | 74,836 | 75,052 | +216 | +0.3 | K-3 one-shot revoke |
| MOBI-VID-V2 | transferOwnership | 199,810 | 200,023 | +213 | +0.1 | K-3 revoked check |
| MOBI-VID-V2 | createIdentity | 298,941 | 299,143 | +202 | +0.1 | K-4 |

Not in the table: an **issuer-path** ERC-735 `removeClaim` now costs 90,623 against
72,142 on the owner path. The difference is the revocation SSTORE. The benchmark
measures the owner path.

Relative-cost columns in `gas_comparison.csv` that moved:
- ERC-735 create: 26.29× → 28.09×.
- ERC-735 add-claim: 8.23× → 8.30×.
- ERC-721 create: 10.40× → 10.39×.
- ERC-725xy create: 32.22× → 32.20×.

The ERC-721 and ERC-725xy ratios moved only because the cheapest create (CVIN-Combined)
rose by 22 gas.

**Determinism.** `run_gas_stats.py --runs 30` gives all 61 cells byte-identical
(`all_deterministic: true`). The committed `gas_benchmark_stats.json` was still the July
2026 pre-cancun run, so it did not match `gas_benchmark.json` before this pass; it does
now. The CI gate (`benchmark.yml`, nine-standard-gas) compares `gasUsed` only and passes.

**Other regenerated results** (separate commits, each with its own caveat):
- `mobi_vid_backends.{json,csv,tex}` (`54b79c9`) and `scaling_{marginal,lifetime}.*`
  (`faad888`). Both committed versions were July 2026 runs under the default EVM target,
  so their diffs also carry the evm-cancun drift the gas table already took on
  2026-09-24. Effects:
  - The scaling slopes and R² are unchanged.
  - The lifetime ranking is unchanged.
  - ERC-735 lifetime: 11,052,885 → 11,202,285.
  - CVIN-Combined lifetime: 9,759,510 → 9,845,068. This is now only 1,579 gas below
    MOBI-VID-V2.
  - The ERC-1056 lifetime figure in register row #26 moves 1,450,824 → 1,450,146. That
    is drift only; no ERC-1056 contract changed.
- `onchain_security.json` was re-run. Only its date changed, so it was not committed.

## 4. Proposed register text, row #25

> Nine-standard gas table (deploy / create / update / delegate-or-claim / revoke /
> transfer per standard; MOBI-VID-V2 as application profile; ERC-4337 EntryPoint
> indirection +46,830 gas/op; create-identity spread 52,192 (CVIN-Combined) →
> 1,680,816 (ERC-725xy) = 32.2×) · M1 (solc 0.8.24, optimizer 200 + viaIR, evm cancun,
> OZ 5.0.2, Hardhat local) · `benchmark_gas.js` → `gas_benchmark.json`,
> `gas_comparison.{csv,tex}` · **V — re-executed 2026-10-03 after the Review-02 P1-K
> contract fixes (K-2, K-3, K-4, K-11, K-13)**: 19 of 61 cells move, all in ERC-735,
> CVIN-Combined, ERC-1155 and MOBI-VID-V2. ERC-735 per-vehicle create +6.9 %
> (1,371,394 → 1,466,088; sticky issuer revocation); CVIN-Combined deploy +7.3 %; claim
> adds +2.5k; ERC-1155 and MOBI ≤ +1.8 % on deploy and ≤ +0.4 % per operation.
> ERC-1056, ERC-721, ERC-725, ERC-725xy, ERC-4337 and LSP8 are unchanged. 30/30 runs are
> byte-identical. The 2026-09-24 values become **S** (pre-fix contracts: an issuer
> revocation could be undone by the holder, and MOBI ownership history could be
> bypassed).

Check before adopting: the old row's "52,178 → 1,704,992" and "+46,862" match neither
the HEAD JSON nor this one. HEAD already had 52,170 → 1,680,816 and an EntryPoint
indirection of 96,173 − 49,343 = 46,830. Those figures appear to predate the cancun
re-run.

## 5. Not fixed, and why

- **K-2 residual: no nonce or expiry in the claim signature.** If an issuer replaces
  claim A with claim B and never removes A, the owner can re-anchor A. Closing this
  changes the signed payload, which means changes to the off-chain signer and the
  benchmark calldata. Pass 2 or an author decision. Documented in both contracts.
- **K-13 residual.** An issuer the vehicle has approved (`setApprovalForAll`) can still
  move a BIRTH_CERT with plain `safeTransferFrom`. This bypasses the VIN re-binding, and
  the new check, which sits in `issuerTransferCredential`. It needs the holder to have
  granted approval, so it is Low. The fix would be a guard in `_update`.
- **K-1 and the harness.** The metrics adapter still uses eight single `setAttribute`
  calls. The comment in `benchmarks/adapters/erc1056.adapter.js` stays accurate.
  Switching the adapter is a harness change, which belongs to P1-H.
- **Stale note in `scripts/benchmark_gas.js` (MOBI-V2).** It says birth attributes must
  be empty because of the V1 overflow, which was fixed earlier. It is left because P1-H
  edits the harness; it affects notes only, not gas. Also in the notes: the `attestEvent`
  figure (192,671 to 192,718) varies between runs because the eventId depends on
  `block.timestamp`. That one is not gated.
- **Testbed artifacts.** `cv2x-testbed/artifacts` were not recompiled (Pass 2 / Q-9). The
  Python providers still run the pre-fix bytecode until then.
- **Out of scope by instruction.** K-5, K-6, K-7, K-8, K-9, K-10, K-12, K-14, K-15.
- **Leftovers from K-16.** `ERC721/scripts` (ethers-v5 deploy scripts) and the
  `ERC721/`, `ERC725/` READMEs are not referenced by the build and were left in place.
  `docs/PROJECT_SUMMARY.md` §3.1 still names `..._monolithic_alt.sol`. That is a shared
  doc, so it is not edited here.

## 6. Commits

```
5ec0c1c Fix CVINVehicleDIDRegistry.setVehicleAttributes so it can succeed (K-1)
a64d31b ERC-735 holder: make issuer revocation stick (K-2)
6c47ac9 CVIN-Combined: sticky issuer revocation (K-2) and empty-slot hasValidClaim (K-11)
b043238 MOBI VID: close the ownership bypass and freeze revoked identities (K-3, K-4)
ee3a574 ERC-1155: reject moving a BIRTH_CERT onto a registered vehicle (K-13)
63d4d3a Remove dead drifted contract/test copies (K-16); fix npm test scripts (Q-10)
3ac47d1 K-2: drop the extra revocation event and view to cut deployment cost
ffedb4e Regenerate the nine-standard gas results after the P1-K contract fixes
54b79c9 Regenerate the MOBI VID backend sweep after the P1-K contract fixes
faad888 Regenerate scaling experiments A/B after the P1-K contract fixes
```
