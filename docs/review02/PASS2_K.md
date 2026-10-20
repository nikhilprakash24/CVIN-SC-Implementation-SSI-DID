# Pass 2 — stream P2-K (contracts, security harness, testbed artifacts): report

**Input:** `docs/REVIEW_02_CODEBASE.md` (K-6, K-8, Q-8, Q-9, Q-14), `docs/PLAN_REVIEW_02.md`
(Pass 2), `docs/review02/PASS1_K.md`, plus two scope additions from the Pass 2
adversarial re-review: the **K-2 owner-pre-removal bypass** (High, PoC) and **Q-9
raised to High**.
**Base:** `4d3dcfa`. **Gate:** Hardhat green: **293 passing, 4 pending** (baseline
276 / 4; +17 tests, none removed, skipped or weakened).

## 1. What changed, per finding

| ID | File(s) | Change | Regression test (fails on the old code) |
|---|---|---|---|
| K-6 | `contracts/CVINCombined/CVINCombinedIdentity.sol` | `addClaim` / `removeClaim` (and the new `revokeClaimContent`) no longer write `changed[identity]`. `changed[]` is the ERC-1056 chain head and only DID events (`DIDOwnerChanged`, `DIDDelegateChanged`, `DIDAttributeChanged`) advance it; claim history lives in `ClaimAdded` / `ClaimRemoved`. | `K-6: claim add/remove does not break the changed -> previousChange chain`: setAttribute → addDelegate → addClaim → setAttribute → removeClaim; `changed` must equal the last DID block, and the resolver walk (getLogs at block *b*, topics `[DID events, identity]`, follow `previousChange`) must visit every DID block. Old code: `expected 49 to equal 48`. |
| K-8 | `contracts/LSP8/CVINVehicleLSP8.sol` | The data store is versioned: `_tokenIdData[tokenId][generation][key]`. `generation` (uint96) is packed with the owner in one `TokenRecord` slot and bumped by `revokeVehicle`. A burned token and any re-mint of the same VIN read an empty store; the re-mint writes its own VIN key. Old values stay in storage, unreachable, and in past events. Chosen over clearing because the store is open-ended (any `dataKey`), so clearing would need a key index on every write. | `K-8: re-minting a revoked VIN does not return the old token's data` (single + batch reads; new writes readable). Old code returned the old inspection bytes. |
| K-2 bypass (Pass 2, High) | `contracts/ERC735/CVINVehicleClaimHolder.sol`, `contracts/CVINCombined/CVINCombinedIdentity.sol` | New issuer-side `revokeClaimContent(topic, data)` (ERC-735) / `revokeClaimContent(identity, topic, data)` (Combined). It sets `revokedClaims[keccak256(msg.sender, digest)]` **whether or not the claim is anchored**, and removes the caller's anchored claim if it carries exactly that data (a re-issued claim with other data stays). It keys on `msg.sender`, so it can only block the caller's own signatures and needs no access control. Removal logic is shared through a private `_deleteClaim`. No new event (same deploy-cost choice as Pass 1); a revocation of non-anchored content is visible as the tx to `revokeClaimContent` and in the `revokedClaims` getter. | Both contracts: `owner pre-removes → issuer removeClaim reverts "does not exist / not found" → issuer revokeClaimContent → owner re-add reverts "claim revoked by issuer"`; anchored-claim revocation emits `ClaimRemoved`; a third party's call cannot touch the issuer's claim; revoking old content leaves re-issued data anchored. The existing "owner self-removal … may re-anchor" tests stay, renamed "(issuer has not revoked)". |
| Q-8 | `test/security/attackHarness.js`, `test/security/securityScenarios.test.js`, `scripts/security_scenarios.js` | `attempt(thunk, expected)` now **requires** the revert that proves the named defense: `{reason}` (Error(string)), `{customError, args, iface}` or `{panic}`. It decodes the raw revert data itself (`revertDataOf` / `decodeRevert`) and classifies: **DEFENDED** (exact match), **UNEXPECTED-REVERT** (other revert), **FAILED-TO-RUN** (no revert data: TypeError, ethers ABI/argument error, provider error), **VULNERABLE** (mined). All 43 executable cells carry an expected revert; custom errors are checked with exact args (attacker address and the specific role, token id, holder). Each matrix cell records `expectedRevert` next to the decoded `revertReason`. The rRecover control was added (guardian set *before* the attack; the guardian's `recoverOwner` must PASS). `security_scenarios.js` re-throws non-revert errors instead of recording them as reverted. | `Security / harness self-check` (6 tests): TypeError → FAILED-TO-RUN; ABI arg error → FAILED-TO-RUN; authority mint with empty VIN → UNEXPECTED-REVERT (`Error("LSP8: empty VIN")`); AccessControl with the wrong role → UNEXPECTED-REVERT, right role → DEFENDED; ERC-725 reason decoded; missing expectation throws. All 6 fail on the old harness. |
| Q-14 | `test/MOBIVID/MOBIVIDRegistry.test.js`, `test/ERC721/combined.js` | The garbage-attestation case (now ~line 501, was 398) asserts `ECDSAInvalidSignatureLength(len)` instead of a bare `.to.be.reverted`. `CVIN_NFT_DID_ERC721` and its monolithic variant get a non-owner mint test asserting `OwnableUnauthorizedAccount(caller)` and that no token was minted. | The contracts were already correct, so these are strengthened assertions, not bug regressions; they fail if `onlyOwner` or the ECDSA length check is removed. |
| Q-9 (raised to High) | `cv2x-testbed/artifacts/contracts/**`, `cv2x-testbed/contracts/ERC1056Registry_bytecode.txt`, root `.gitignore`, `cv2x-testbed/tests/conftest.py` (docstring), `cv2x-testbed/hardhat.config.js`, `cv2x-testbed/package.json`, `cv2x-testbed/scripts/check_artifacts_fresh.js` | **Regenerated, not untracked**, because three runtime paths load them with no compile step: `experiment_pki_vs_erc1056.py --deploy` (#21/#22), `tests/conftest.py` (`load_artifact` default) and `identity/erc1056_provider.py` (`contracts/ERC1056Registry_{abi.json,bytecode.txt}`). Rebuilt with the testbed's **own** `hardhat.config.js`: solc 0.8.20, optimizer 200 runs, no viaIR, evm paris. **Settings check:** rebuilding the pre-K-3 `ERC1056Registry.sol` (`b043238^`) with these settings reproduces the old tracked bytecode byte for byte, so the only change is the source. The ABI file is unchanged; the bytecode file and all three artifacts changed. Root `.gitignore` now ignores `cv2x-testbed/artifacts/*` except `contracts/`, plus `cv2x-testbed/cache/`. `npm run check:artifacts` (in cv2x-testbed) compiles into a scratch dir (artifacts/cache paths are now env-overridable, defaults unchanged) and exits 1 if abi/bytecode/deployedBytecode or the flat ERC1056 files differ. Verified: passes now, fails on the old V2 artifact and old `_bytecode.txt`. It is not wired into CI (cv2x-testbed has no `npm ci` step there). | Artifact commit **`1adf0ef`**; checker **`88acbdd`**. |

## 2. Q-8 findings: was anything "defended for the wrong reason"?

**No cell is defended by a different revert than the one its defense names.** All 43
executable cells match their expected revert exactly, custom-error args included.

What the stricter harness surfaced:

1. **ERC-725 "couldn't infer the reason" (4 cells).** The revert data was never missing.
   Hardhat's stack-trace engine cannot map the solc **0.8.20 + viaIR** bytecode of
   `CVIN_DID_ERC725.sol`, so its error message is generic, but `err.data` always held
   the ABI-encoded `Error("Only owner can add keys")` etc. The harness now decodes
   `err.data`, so these cells assert the real reason (`Only owner can add keys` ×2,
   `Only owner can remove keys`, `Only owner can transfer ownership`).
2. **ERC-1155 identityHijack: right outcome, wrong stated mechanism.** The cell's
   defense said "approval check + soulbound `_update` guard". The revert is OZ's
   `ERC1155MissingApprovalForAll(attacker, vehicle)`; the soulbound guard is never
   reached by this attack. The defense text now says so. The soulbound guard has no
   cell of its own (see also the Pass 1 K-13 residual: an approved operator bypasses
   the re-binding).
3. **ERC-1056 and CVIN-Combined / ERC-735 signatureReplay.** These revert with the
   generic signature check (`DIDRegistry: invalid signature`,
   `…: invalid claim/issuer signature`). That is the correct mechanism: the nonce,
   or the identity / holder address, is part of the signed digest, so the replayed
   signature recovers a different address. Comments in the test say this.
4. **Not fixed, reported (MOBI-VID-V2).** The `signatureReplay: N/A` note says
   "attestEvent stores a signature blob but never re-executes it on-chain". That is
   stale: `attestEvent` now verifies the signature with ecrecover. It also has **no
   duplicate check**, so a role-holder can resubmit the same valid attestation and
   add it to `eventAttestations[eventId]` again (inflated attestation count). A fix
   would change MOBI gas cells, so I left it for a decision. The N/A note was not
   edited either; this report records it.

`attack_results.json` was regenerated: only the per-cell `revertReason` (decoded form),
the new `expectedRevert` fields, the rRecover control string and the metadata
`outcomes`/`notes` change. The outcomes are unchanged (43/43 DEFENDED, 11 N/A).
`attack_results.{csv,tex}` (generated by `generate_attack_tables.py`) and
`onchain_security.json` (`scripts/security_scenarios.js`) changed only in their dates,
so they were **not** committed. The CSV/TeX legend still says "DEFENDED = malicious tx
reverted". It lives in Python (`generate_attack_tables.py`), which is another stream's.

## 3. Gas: before / after (`gas_benchmark.json`, `4d3dcfa` → this pass)

Conditions are unchanged from Pass 1: solc 0.8.24, optimizer 200, viaIR, evm cancun,
OZ 5.0.2, Hardhat in-process. **15 of 61 cells changed**, all in CVIN-Combined,
ERC-735 and LSP8. The other 46 are identical.

| Standard | Operation | Before | After | Δ | Δ % | Cause |
|---|---|---:|---:|---:|---:|---|
| CVIN-Combined | deployRegistry | 1,421,834 | 1,490,166 | +68,332 | +4.8 | `revokeClaimContent` + `_deleteClaim` bytecode (K-2 bypass) |
| CVIN-Combined | addDelegateOrClaim | 292,366 | 287,570 | −4,796 | −1.6 | K-6: no `changed[]` SSTORE |
| CVIN-Combined | revoke (owner removeClaim) | 73,795 | 69,721 | −4,074 | −5.5 | K-6 |
| CVIN-Combined | createIdentity | 52,192 | 52,216 | +24 | 0.0 | dispatch |
| CVIN-Combined | updateAttribute | 35,092 | 35,116 | +24 | 0.1 | dispatch |
| ERC-735 | createIdentity (per-vehicle deploy) | 1,466,088 | 1,535,776 | +69,688 | +4.8 | `revokeClaimContent` bytecode (K-2 bypass) |
| ERC-735 | revoke (owner path) | 72,142 | 72,195 | +53 | 0.1 | `_deleteClaim` refactor |
| ERC-735 | addDelegateOrClaim | 292,708 | 292,730 | +22 | 0.0 | dispatch |
| ERC-735 | updateAttribute | 77,691 | 77,713 | +22 | 0.0 | dispatch |
| ERC-735 | transferOwnership | 28,724 | 28,746 | +22 | 0.1 | dispatch |
| LSP8 | deployRegistry | 1,592,737 | 1,614,592 | +21,855 | +1.4 | K-8 generation |
| LSP8 | revoke | 41,838 | 42,141 | +303 | +0.7 | K-8 generation bump |
| LSP8 | createIdentity | 149,430 | 149,615 | +185 | +0.1 | K-8 |
| LSP8 | updateAttribute | 55,051 | 55,114 | +63 | +0.1 | K-8 |
| LSP8 | transferOwnership | 80,576 | 80,600 | +24 | 0.0 | dispatch |

Relative-cost columns in `gas_comparison.csv` that moved:
- ERC-735 create: 28.09× → 29.41×.
- CVIN-Combined deploy: 3.12× → 3.27×.
- CVIN-Combined add-claim: 8.29× → 8.15×.
- CVIN-Combined revoke: 2.90× → 2.74×.
- LSP8 deploy: 3.49× → 3.54×.
- LSP8 create: 2.86× → 2.87×.
- LSP8 revoke: 1.65× → 1.66×.

Second-digit moves in other rows come only from the +24 gas on the cheapest create and
update (CVIN-Combined):
- ERC-725 update: 3.91× → 3.90×.
- ERC-725xy create: 32.20× → 32.19×.
- MOBI update: 8.75× → 8.74×.

**Determinism.** `run_gas_stats.py --runs 30`: all 61 cells byte-identical (`all_deterministic: true`). `gas_benchmark_stats.json` is regenerated and matches `gas_benchmark.json`. The `attestEvent` figure in the MOBI notes still varies run to run (Pass 1 note); it is not gated.

**Scaling (Experiments A/B).** `benchmark_scaling.js` and `generate_scaling_tables.py` were re-run (`36cde4d`).

Experiment A (marginal cost):
- CVIN-Combined addClaim slope: −80.5 → −40.2 gas/op. The first add no longer pays
  the zero-to-nonzero `changed[]` SSTORE (first add 309,538 → 287,642), so the slope
  now matches the other standards.
- O(1) holds for all standards (R² ≈ 0.06).

Experiment B (lifetime model, 39-event profile):
- CVIN-Combined: 9,845,068 → **9,677,232** (−1.7 %).
- ERC-735: 11,202,285 → 11,272,809 (+0.6 %).
- The others are unchanged.
- The ranking is unchanged: ERC-1056 < ERC-1155 < CVIN-Combined < MOBI-VID-V2 < ERC-735.
- The CVIN-Combined / MOBI-VID-V2 gap widens from 1,579 to **169,415** gas. The
  near-tie Pass 1 reported is gone.

`scaling_verify_*` PNGs were re-rendered with unchanged data and are not recommitted
(same as Pass 1).

**cv2x-testbed #22** (Q-9; not re-run here, the Python experiment is the testbed
stream's). Measured with a Hardhat script that deploys each artifact and runs the
provider's calls (`registerVehicle` and `updateVehicleKey` with a 65-byte key,
`revokeIdentity`). The **old** tracked artifact reproduces the register row exactly
(register 54,860, issue 37,779–37,791, deploy 878,509). The regenerated artifact gives:

| #22 cell | Old tracked artifact | Regenerated (current source) | Δ |
|---|---:|---:|---:|
| deploy | 878,509 | 927,756 | +49,247 |
| register | 54,860 | 54,848–54,860 | 0 |
| issue (attribute) | 37,779–37,791 | 37,791 | 0 |
| revoke | 75,032 (75,044 in #22) | 75,245 | +213 |

The revoke difference comes from K-3: `revokeIdentity` is now one-shot. The 12-gas
difference against the register's 75,044 is the address-dependent calldata spread.
**#21/#22 must be re-run on `1adf0ef` or later.** Until then they measure bytecode
without K-3/K-4, on which `changeOwner` after a revoke still succeeds.

## 4. Proposed register text

**Row #26 (lifetime model):** CVIN-Combined 9,845,068 → 9,677,232; ERC-735 11,202,285 →
11,272,809. The other standards and the ranking are unchanged. CVIN-Combined is 169,415 gas
below MOBI-VID-V2.

**Row #25 (nine-standard gas):** append to the Pass 1 text:

> … **re-executed 2026-10-04 after the Review-02 P2-K fixes (K-6, K-8, K-2 issuer
> content revocation)**: 15 of 61 cells move, all in CVIN-Combined, ERC-735 and LSP8.
> CVIN-Combined add-claim 292,366 → 287,570 (−1.6 %) and owner claim removal 73,795 →
> 69,721 (−5.5 %), because claims no longer advance the ERC-1056 `changed` pointer. CVIN-Combined deploy
> +4.8 % and ERC-735 per-vehicle create +4.8 % (1,466,088 → 1,535,776), for
> `revokeClaimContent`. LSP8 deploy +1.4 % and ≤ +0.7 % per operation (versioned
> per-token data). ERC-1056, ERC-721, ERC-725, ERC-725xy, ERC-1155, ERC-4337 and MOBI-VID-V2
> are unchanged. The 2026-10-03 values become **S** (pre-fix: an owner could pre-empt an
> issuer revocation; CVIN-Combined claims cut the DID event chain; an LSP8 re-mint
> inherited the burned token's data).

**Row #22:** "deploy 878,509 … revoke 75,044" → **S** (pre-K-3/K-4 tracked bytecode).
Pending a re-run on `1adf0ef`, the expected values are deploy 927,756 and revoke
≈75,245; register and issue are unchanged.

**Security row (attack matrix, #5 / wherever "43/43 defended" is cited):**

> 43/43 executable attacks DEFENDED, **each with the expected revert reason or custom
> error of the named defense asserted** (custom errors with exact args), and each with a
> passing authorized-party control. A different revert counts as UNEXPECTED-REVERT and
> a non-revert error as FAILED-TO-RUN, so neither can count as defended (Review-02
> Q-8). ERC-1155 identity hijack is stopped by the OZ operator-approval check, not by
> the soulbound guard.

## 5. Not fixed, and why

- **MOBI-VID-V2 duplicate attestations** (§2 item 4). Fixing it changes MOBI gas cells.
  Author decision.
- **No `ClaimContentRevoked` event.** Revocations of non-anchored content are not
  indexable from events. The tx and the `revokedClaims` getter are the record. Adding
  the event costs deploy gas, the trade-off Pass 1 also made.
- **K-2 residual from Pass 1 still stands.** There is no nonce or expiry in the signed
  payload, but an issuer can now revoke superseded content proactively with
  `revokeClaimContent`. That turns the residual into an issuer duty, not an
  unfixable hole.
- **The metrics harness run of record** (`benchmarks/`, `results/metrics/`) includes
  CVIN-Combined / ERC-735 / LSP8 cells and needs a re-run by the harness stream.
- **`check:artifacts` is not in CI.**
- **The legend text in `generate_attack_tables.py`** (Python, other stream).

## 6. Commits

```
2755f8f CVIN-Combined: claims no longer advance the ERC-1056 changed[] chain head (K-6)
b73d426 LSP8: version the per-token data store so a re-minted VIN starts empty (K-8)
cc2ad53 Security harness: assert the expected revert per attack (Q-8)
a4c0d39 Tests: assert the specific revert for garbage attestations; onlyOwner mint negatives (Q-14)
1adf0ef cv2x-testbed: regenerate the tracked registry artifacts from current sources (Q-9)
88acbdd cv2x-testbed: add a staleness check for the tracked artifacts (Q-9)
81945b9 ERC-735: issuer revokeClaimContent closes the owner-pre-removal K-2 bypass
75d2af1 CVIN-Combined: issuer revokeClaimContent closes the owner-pre-removal K-2 bypass
fce6654 Regenerate the nine-standard gas results after the P2-K contract fixes
36cde4d Regenerate scaling experiments A/B after the P2-K contract fixes
(this report)
```
