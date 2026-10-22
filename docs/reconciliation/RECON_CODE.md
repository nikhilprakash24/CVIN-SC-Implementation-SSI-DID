<!-- Read-only analysis produced 2026-10-06 for docs/REVIEW_03_PARALLEL_LINEAGES.md; branches compared: claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy @ b70081c (ours) vs origin/claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt @ fa6188e (theirs); merge base 3203ee8. Every number carries its source path. -->

# RECON_CODE — code-level overlap and conflict analysis

Base: `3203ee8` (2026-09-30).
OURS: `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` @ `b70081c` (35 commits, 355 files changed vs base).
THEIRS: `origin/claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` @ `fa6188e` (155 commits, 404 files changed vs base; repo default).
Merge base confirmed: `git merge-base b70081c fa6188e` = `3203ee8`.
Method: `git diff --name-only 3203ee8 <ref>` on both sides, `comm -12`; `git merge-tree --write-tree b70081c fa6188e` (git 2.43.0) for textual conflicts (result tree `27a0db5c…`, conflict-hunk counts read from that tree); their suites run in a detached worktree of `fa6188e` (removed afterwards; main working tree untouched).

Defect-ID vocabularies: ours = `docs/DEFECT_LOG.md` (D7, D8, D9, D10, D11, D11b, D13, D16, D18, D21, D22, D25a/b/c, D27); theirs = `docs/review02/PASS1_K.md` / `PASS2_K.md` (K-1 … K-16), `PASS1_T.md` (T-2 … T-12), `PASS1_S.md` (S-10), `FOLLOWUP_GR.md` (R1–R4), `PASS1_H.md` (H-12), Q-8/Q-9/Q-12 (CI/harness).

---

## 1. Files changed on BOTH sides (61) and the 3-way merge result

`merge-tree` reports **64 conflicted paths**: 54 content/add-add conflicts among the 61 both-changed files, plus 8 rename/delete conflicts and 2 file-location conflicts outside the both-changed set. 7 of the 61 auto-merge cleanly.

### 1.1 Contracts (9 both-changed + 1 derived text) — all 10 CONFLICT

| path | ours (vs base) | theirs (vs base) | merge-tree | hunks / lines |
|---|---|---|---|---|
| `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol` | +82: D10 `":0x"` prefix in `getVehicleDID`; D11b `anchorVehicleKey` (+`VEHICLE_KEY_ATTRIBUTE`, `vehicleKeyAnchored`, `VehicleKeyAnchored`) | +34: K-15 `":0x"` prefix (identical code line, different comment); K-4 `require(changed[id]==0)` in `registerVehicleBirth`; K-3 `changeOwner` public override reverting for born vehicles | CONFLICT (content) | 2 / 18 |
| `cv2x-testbed/contracts/MOBIVIDRegistry.sol` | byte-identical copy of the above | byte-identical copy of the above | CONFLICT (content) | 2 / 18 |
| `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol` | +50/−32: `notRevoked` modifier on changeOwner/addDelegate/revokeDelegate/setAttribute/revokeAttribute/updateVehicleKey; `revokeIdentity` single-shot; **`DIDRevoked` gains `previousChange` (ABI change, D21)**; D16 | +18/−4: inline `require(!revoked)` in changeOwner/revokeDelegate/revokeAttribute/revokeIdentity (K-3); `changeOwner(address,address)` made `virtual` (needed by their MOBIVIDRegistry override); DIDRevoked ABI deliberately unchanged (K-5) | CONFLICT (content) | 4 / 32 |
| `cv2x-testbed/contracts/ERC1056Registry.sol` | identical copy | identical copy | CONFLICT (content) | 4 / 32 |
| `cv2x-testbed/contracts/ERC1056Registry_bytecode.txt` | regenerated from our source | regenerated from their source | CONFLICT (content) | — (1-line file) |
| `1_blockchain-identity/contracts/ERC1056/CVINVehicleDIDRegistry.sol` | +13: D18 constant `PERMANENT_ATTRIBUTE_VALIDITY = 100*365 days` replaces `type(uint256).max`; signature unchanged (`did = msg.sender`) | +61/−17: K-1 constant `VEHICLE_ATTRIBUTE_VALIDITY`; **`setVehicleAttributes(address did, …)` — new first parameter**, `onlyVehicleOwner(did)`, requires `didRegistry.identityOwner(did)==address(this)` | CONFLICT (content) | 1 / 8 |
| `1_blockchain-identity/contracts/ERC1155/CVINVehicleCredential1155.sol` | +223: D7 `safeTransferFrom`/`safeBatchTransferFrom` revert for everyone; D8 `_heldTypes` bitmap, `MAX_CREDENTIAL_TYPE=255`, `credentialTypesOf`, BIRTH_CERT burn guard, `issuerTransferIdentity`, `IdentityRebound`, `URI` event; D13 `_normalizeVIN`/`vinHashOf`/`vehicleForVIN`; self-transfer guard | +9: K-13 `require(balanceOf(to,BIRTH_CERT)==0, "CVIN1155: recipient already holds a BIRTH_CERT")` in `issuerTransferCredential` | CONFLICT (content) | 1 / 13 |
| `1_blockchain-identity/contracts/ERC735/CVINVehicleClaimHolder.sol` | +109: D25a issuer registry (`authorizeIssuer`/`revokeIssuer`/`isAuthorizedIssuer`, `addClaim` requires `issuer==owner || authorized`); D25b `_encodesHolderVin` for topic 1; D25c scheme note | +79: K-2 sticky issuer revocation (`revokedClaims`, `revokeClaimContent`, `_deleteClaim`, `digest` local in `addClaim`) | CONFLICT (content) | 3 / 56 |
| `1_blockchain-identity/contracts/LSP8/CVINVehicleLSP8.sol` | +59: D13 `_normalizeVIN` in `mintVehicle` and `tokenIdForVIN` | +53/−19: K-8 `TokenRecord{owner,generation}` replaces `_tokenOwners`; data store keyed `tokenId=>generation=>key`; `revokeVehicle` bumps generation | CONFLICT (content) | 2 / 20 |
| `1_blockchain-identity/contracts/CVINCombined/CVINCombinedIdentity.sol` | +19: D22 new event `DIDClaimChanged(identity,claimId,topic,removed,previousChange)` emitted by add/removeClaim; `changed[]` still advanced | +103/−17: **K-6 add/removeClaim no longer advance `changed[]`**; K-2 sticky revocation (`revokedClaims`, `revokeClaimContent`, `_deleteClaim`); K-11 `hasValidClaim(issuer==0)` → false; `_claimDigest` refactor | CONFLICT (content) | 2 / 16 |

### 1.2 Hardhat tests — 0 both-changed paths textually (ours moved the tree), 4 files merged through rename detection, 2 file-location conflicts

- Ours renamed `test/<Std>/…` → `test/L2-identity-system/per-option/<Std>/…` (R100 for 10 files, R090 ERC1155 test, R096 ERC735 test, R095 attackHarness) and added `test/L1-identity-mechanisms/` (11 files) plus 11 `*.regression.test.js`.
- Theirs modified in place: `CVINCombined/CVINCombinedIdentity.test.js` (+171), `ERC1056/CVINVehicleDIDRegistry.test.js` (+90), `ERC1155/CVINVehicleCredential1155.test.js` (+18), `ERC721/combined.js` (+16), `ERC735/CVINVehicleClaimHolder.test.js` (+98), `LSP8/CVINVehicleLSP8.test.js` (+30), `MOBIVID/MOBIVIDRegistry.test.js` (+207), `security/attackHarness.js` (+168), `security/securityScenarios.test.js` (+290); added `ERC1056/PseudonymPool.test.js` (95), `MOBIVID/attestEventRegression.test.js` (156), `benchmarks/adapters.conformance.test.js` (155), `benchmarks/stats.test.js` (36).
- merge-tree: "Auto-merging" (rename-followed, clean) for `…/per-option/ERC1155/CVINVehicleCredential1155.test.js`, `…/per-option/ERC735/CVINVehicleClaimHolder.test.js`, `…/security/attackHarness.js`, `…/security/securityScenarios.test.js`.
- CONFLICT (file location) ×2: their new `test/ERC1056/PseudonymPool.test.js` and `test/MOBIVID/attestEventRegression.test.js` land in a directory we renamed; merge-tree suggests `test/L2-identity-system/per-option/ERC1056/PseudonymPool.test.js` and `…/per-option/MOBIVID/attestEventRegression.test.js`. Their `test/benchmarks/*` has no counterpart on ours (new dir, clean).

### 1.3 Scripts (5 both-changed)

| path | ours | theirs | merge-tree |
|---|---|---|---|
| `1_blockchain-identity/scripts/security_scenarios.js` | +16/−?: ERC-735 scenario calls `holder.authorizeIssuer(issuer, TOPIC)` (D25a setup); ERC-1155 identity_theft mechanism text (D7); recovery via `issuerTransferIdentity` and checks `INSPECTION` moved too | +22: `expectRevert` re-throws non-revert errors ("attack FAILED-TO-RUN", Q-8) using `revertDataOf` imported from **`../test/security/attackHarness`**; hard-coded gas figures in mechanism strings replaced by "matrix cost_proxy_gas" | Auto-merged (0 hunks) — **but the new `require("../test/security/attackHarness")` resolves to a path we moved to `test/L2-identity-system/security/attackHarness.js`; broken after merge** |
| `cv2x-testbed/scripts/experiment_freshness_k.py` | NEW, 419 lines; drives `ERC1056Provider(freshness_k=k)`; rows pki_standard / erc1056 off / k=1,5,25,100,inf; n=200 | NEW, 705 lines; imports the `experiment_pki_vs_erc1056.py` harness; drives `ERC1056Provider(refresh_every=k, refresh_mode=…)`; n=250; T-9 freshness installed for every k | CONFLICT (add/add), 5 hunks / 1077 lines — not mergeable, choose one |
| `cv2x-testbed/scripts/experiment_lifecycle_parity.py` | NEW, 802 lines | NEW, 411 lines | CONFLICT (add/add), 4 hunks / 1173 lines — choose one |
| `cv2x-testbed/scripts/test_use_cases.py` | +19/−17: `USE_CASES` list hoisted to module level for `sandbox/py-suites/L4` parametrisation | +20/−4: `CredentialVerifier(trusted_issuers=[…], subject_holder_binding={…})` in use cases 3, 6, 10, 11 (T-3/S-1/S-2; depends on their `vc_verifier.py` API, which we did not touch) | Auto-merged, 0 hunks |
| `cv2x-testbed/sumo/sumo_identity_integration.py` | +5: `--results PATH` CLI option | +70/−10: T-9 `FreshnessPolicy` on both layers (sim-clock), stale-BSM attack test, `CredentialVerifier(trusted_issuers=[self.issuer])`, `_pki_payload_bytes(signed)` signs message+timestamp | Auto-merged, 0 hunks |

Also both-changed: `1_blockchain-identity/package.json` (ours: `js-yaml` devDependency; theirs: all `test:*` script paths rewritten to `test/<Std>/*.js`, `test:mobivid`, `test:security`, `metrics*`, `test:conformance`, `deploy:erc1056`) — auto-merged, 0 hunks; **but their `test:*` globs point at `test/ERC721/*.js` etc., which on ours are `test/L2-identity-system/per-option/…` → every `npm run test:<std>` is empty after merge.** `package-lock.json`: ours +4/−3 (js-yaml), theirs unchanged → clean.

### 1.4 Python testbed (2) — both CONFLICT

`cv2x-testbed/identity/erc1056_provider.py` (6 hunks / 114 lines) and `cv2x-testbed/identity/mobi_vid_provider.py` (1 hunk / 45 lines). Detail in §5. Theirs additionally changed 7 other files in `cv2x-testbed/identity/` that we did not touch (`base.py`, `centralized_provider.py`, `comparison_framework.py`, `freshness.py` [new], `lifecycle_backends.py`, `standard/pki_identity.py`, `w3c_verifiable_credentials.py`) — clean.

### 1.5 Resolver (1) — CONFLICT

`2_w3c-ssi-layer/did-resolution/did_resolver.py`: 19 hunks / 257 conflict lines (the largest code conflict). Detail in §6. Their other 14 files under `2_w3c-ssi-layer/` (tests, mobi-vid, verifiable-credentials) are theirs-only → clean.

### 1.6 CI (1)

`.github/workflows/w3c-compliance.yml`: ours +25/−3, theirs +65/−1 → **auto-merged, 0 hunks**. `benchmark.yml` theirs-only (+44), `test-contracts.yml` ours-only (+19). Detail in §7.

### 1.7 Results / artifacts (23) — all CONFLICT

`4_comparison-framework/results/`: `gas_benchmark.json`, `gas_comparison.{csv,tex}`, `mobi_vid_backends.{csv,json,tex}`, `scaling_lifetime.{csv,json,png,tex}`, `scaling_marginal.{csv,json,png,tex}` (14; the 2 PNGs are binary conflicts). `4_comparison-framework/security-analysis/results/attack_results.json` (ours 2 lines, theirs 150 lines). `cv2x-testbed/results/{freshness_k,lifecycle_parity}.{csv,json,md}` (6, add/add). `cv2x-testbed/artifacts/contracts/MOBIVIDRegistry.sol/MOBIVIDRegistry.json`, `…/MOBIVIDRegistryV2.sol/MOBIVIDRegistryV2.json` (2). Dates in §4.

### 1.8 Docs (18)

Conflicted: `README.md` (4 hunks / 38), `docs/INDEX.md` (1 / 11), `docs/MEASUREMENT_CONDITIONS.md`, `docs/SCOPE_CHANGES.md`, `docs/MOBI_VID_CHECKLIST.md` (add/add), `docs/AFTER_ACTION_REPORT_0{3,4,5}.md` (add/add — both lineages wrote reports 03–05 with the same filenames and different content), `docs/conformance/W3C_DID_TEST_SUITE.md`, `docs/conformance/generate_implementations.py`, `docs/conformance/implementations/cvin-{did,resolver}-{ethr,mobi,nft}.json` (6). Auto-merged: `docs/LATENCY_BUDGET.md`, `docs/PROJECT_SUMMARY.md`.

### 1.9 Outside the both-changed set: 8 rename/delete conflicts

Ours moved `1_blockchain-identity/ERC721/{README.md,contracts/*,scripts/*,test/*}` and `ERC725/{README.md,contracts/CVIN_DID_ERC725.sol}` to `1_blockchain-identity/_research-copies/…` (R100) and added `_research-copies/README.md`; theirs deleted (K-16) `ERC721/contracts/CVIN_NFT_DID_ERC721{,_monolithic,_monolithic_alt}.sol`, `ERC721/contracts/README.md`, `ERC721/test/{combined,identityBased,regularExtended}.js`, `ERC725/contracts/CVIN_DID_ERC725.sol` → 8 `CONFLICT (rename/delete)`. Neither path set is in Hardhat `sources`/`tests`.

---

## 2. Contract-by-contract table (every .sol changed on either side)

| path | changed by | ours | theirs | same defect twice? | recommended resolution |
|---|---|---|---|---|---|
| `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol` (+ `cv2x-testbed/contracts/MOBIVIDRegistry.sol`, identical on both heads) | both | D10 `did:ethr:0x<chain>:0x<addr>`; D11b `anchorVehicleKey` (owner any time; registering manufacturer once, only while `ownershipHistory.length==0`), writes attribute `did/pub/secp256k1/veriKey/base64` with `PERMANENT_ATTRIBUTE_VALIDITY` | K-15 same `":0x"` line; K-4 pristine-identity guard on birth; K-3 `changeOwner` override `require(!vehicleBirths[identity].exists, "MOBIVID: use transferVehicleOwnership")` | **YES: D10 ≡ K-15** (identical code change `":"`→`":0x"`; conflict is comment-only). K-3 implements what our DEFECT_LOG lists as deferred "D16 rest (route changeOwner through transferOwnership or forbid it)". | Union: keep D11b block + K-3 override + K-4 require; keep one `getVehicleDID` comment citing both IDs. Requires theirs' `virtual` in `ERC1056Registry.changeOwner`. Then fix our `test/L2-identity-system/per-option/MOBIVID/MOBIVIDRegistry.regression.test.js` lines 81 (expects revert "Identity is revoked"; K-3 reverts first with "MOBIVID: use transferVehicleOwnership") and 93 (expects `changeOwner` on a born vehicle to emit `DIDOwnerChanged`; K-3 reverts). Re-copy to `cv2x-testbed/contracts/` (our CI `cmp` gate). |
| `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol` (+ `cv2x-testbed/contracts/ERC1056Registry.sol`) | both | `notRevoked` modifier (6 mutators); one-shot `revokeIdentity` ("Identity already revoked"); `DIDRevoked(identity, revokedAt, previousChange)` — ABI change | inline `require(!revoked)` in 3 mutators + revokeIdentity ("Identity is revoked"); `changeOwner` public `virtual`; DIDRevoked unchanged (K-5 kept) | **YES: D16/D21 freeze-on-revoke and single-shot revoke ≡ K-3** (same semantics; ours modifier form covers 6 functions vs their 4). Divergent: D21 `previousChange` on `DIDRevoked` — theirs decided not to (their `erc1056_provider._resolve_key_from_events` and `cv2x-testbed/tests/test_erc1056_key_resolution.py` lines 128–130 assume DIDRevoked cuts the chain). | Take ours (superset) + add `virtual` from theirs; unify the revert string (ours "Identity already revoked" vs theirs "Identity is revoked" for a second revoke — their K-3 tests assert theirs). Regenerate `cv2x-testbed/contracts/ERC1056Registry_{abi.json,bytecode.txt}` and `cv2x-testbed/artifacts/**` (their `scripts/check_artifacts_fresh.js` gates this in CI). Update their resolver comment/test wording; the walk code on theirs already tolerates a `previousChange`-bearing DIDRevoked. |
| `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol` (+ `cv2x-testbed/contracts/MOBIVIDRegistryV2.sol`) | theirs | — | K-15: `recordLifecycleEvent` requires an OWNER-role issuer to be `identityOwner(vehicleIdentity)`; doc on `isAuthorizedIssuer` | no (our D16 entry mentions "the OWNER issuer role" as open; theirs fixed it) | Take theirs; clean merge. Our `cv2x-testbed/scripts/deploy_mobi_vid.js` can deploy it (`MOBI_VID_CONTRACT=MOBIVIDRegistryV2`). |
| `1_blockchain-identity/contracts/ERC1056/CVINVehicleDIDRegistry.sol` | both | D18: finite validity constant, nothing else | K-1: finite validity constant **and** `setVehicleAttributes(address did, …)` with `onlyVehicleOwner(did)` + registry-controls-DID check | **YES: D18 ≡ K-1** (same panic 0x11 root cause). Theirs is strictly deeper (ABI change). | Take theirs. Update our 3 call sites in `test/L2-identity-system/per-option/ERC1056/CVINVehicleDIDRegistry.regression.test.js` (lines 56, 90, 98) and 3 in `sandbox/options/erc-1056-uport/demos/attributes.js` (lines 92, 93, 102) to pass `did`. Drop our `PERMANENT_ATTRIBUTE_VALIDITY` or alias it to `VEHICLE_ATTRIBUTE_VALIDITY`. |
| `1_blockchain-identity/contracts/ERC1155/CVINVehicleCredential1155.sol` | both | D7, D8, D13 (+223 lines; see §1.1) | K-13 recipient-already-registered check only | **YES: K-13 ⊂ our D7/D8** (`require(balanceOf(to,BIRTH_CERT)==0, "CVIN1155: recipient already registered")` already present in our `issuerTransferCredential`). | Take ours. Pick one revert string: their `test/ERC1155/CVINVehicleCredential1155.test.js:235` asserts `"CVIN1155: recipient already holds a BIRTH_CERT"`. Their test at :210–222 moves BIRTH_CERT of a vehicle registered in `beforeEach` with no other credentials → passes under our "holds other credentials" rule. Their `"OTHERVIN000000001"` (contains I and O) at :74 is reached only after our "vehicle already registered" require, which precedes `_normalizeVIN` → still passes. |
| `1_blockchain-identity/contracts/ERC735/CVINVehicleClaimHolder.sol` | both | D25a issuer whitelist, D25b VIN binding, D25c doc | K-2 sticky issuer revocation + `revokeClaimContent` | **NO — complementary** (authorisation vs. revocation-persistence). Both edit the `addClaim` body and the header comment → 3 hunks. | Union. Order in `addClaim`: signature → `!revokedClaims` (K-2) → authorised-or-self (D25a) → VIN binding (D25b). Then their ERC-735 tests need `authorizeIssuer` setup: their `test/ERC735/CVINVehicleClaimHolder.test.js` has 18 `addClaim(` calls and 0 `authorizeIssuer(`; their `test/security/securityScenarios.test.js` has 12 `addClaim(` (the 2 `authorizeIssuer` hits there are MOBI-V2's `authorizeIssuer(address,IssuerRole)`, not ERC-735). Gas rows ERC-735 createIdentity/addDelegateOrClaim change again (theirs already +94,694 / +2,531 from K-2). |
| `1_blockchain-identity/contracts/LSP8/CVINVehicleLSP8.sol` | both | D13 VIN normalisation | K-8 generation-keyed data store | NO — complementary | Union by hand in `mintVehicle`: `normalizedVIN = _normalizeVIN(vin); tokenId = keccak256(bytes(normalizedVIN)); TokenRecord storage record = _tokens[tokenId]; … _tokenIdData[tokenId][record.generation][DATA_KEY_VIN] = bytes(normalizedVIN)`. Their K-8 test re-mints `"1HGBH41JXMN109186"` (valid under D13). |
| `1_blockchain-identity/contracts/CVINCombined/CVINCombinedIdentity.sol` | both | D22: emit `DIDClaimChanged(…, previousChange)` and keep advancing `changed[]` | K-6: stop advancing `changed[]` on claim ops (no new event); K-2; K-11 | **YES, INCOMPATIBLE: D22 vs K-6 fix the same defect (claim ops cut the did:ethr pointer walk) in mutually exclusive ways.** Our `…/per-option/CVINCombined/CVINCombinedIdentity.regression.test.js` lines 94–97 and 106–109 assert `DIDClaimChanged` AND `changed(id) == receipt.blockNumber` after a claim op; their test "K-6: claim add/remove does not break the changed -> previousChange chain" asserts the opposite. | Author decision. Recommendation: K-6 (claims are not DID-document state; no new event; matches ethr-did-resolver), plus K-2 and K-11. Then delete our `DIDClaimChanged` event, our 5 D22 regression `it()`s, and update the other `DIDClaimChanged` consumers on ours: `sandbox/options/cvin-combined/demos/lifecycle-history.js`, `sandbox/options/cvin-combined/manifest.yaml`, `sandbox/options/cvin-combined/README.md`, `sandbox/grand/report/demos.json`, `docs/FEATURE_ASYMMETRY_MATRIX.md` (CI-gated generator), `docs/MEASUREMENT_CONDITIONS.md`, `docs/DEFECT_LOG.md`. |
| `1_blockchain-identity/contracts/ERC721/CVINVehicleNFT.sol` | ours | D13 `_normalizeVIN` in `mintVehicle` and `getTokenIdFromVIN` (+46) | — | no | Keep; clean. |
| `1_blockchain-identity/contracts/ERC721/CVIN_NFT_DID_ERC721.sol` | ours | D9 `payToll` reverts "no toll operator (ownership renounced)" (+6/−2) | — | no | Keep; clean. |
| `1_blockchain-identity/_research-copies/ERC721/contracts/CVIN_NFT_DID_ERC721{,_monolithic,_monolithic_alt}.sol`, `_research-copies/ERC725/contracts/CVIN_DID_ERC725.sol` | ours (rename) / theirs (delete) | moved from `ERC721/`, `ERC725/` + new `_research-copies/README.md` | K-16 deleted (outside Hardhat paths; only reference was the broken `test:erc721` script) | n/a | Accept deletion unless the thesis cites them; if kept, keep under `_research-copies/` (merge-tree leaves them as rename/delete conflicts either way). |

---

## 3. Tests

### 3.1 Ours (caller-supplied, corroborated by `docs/AFTER_ACTION_REPORT_06.md` line 42)
- Hardhat: `1_blockchain-identity/test/L1-identity-mechanisms` (9 test files + `_l1.js`) + `test/L2-identity-system/{per-option/*,security/*}` (26 files): **386 passing** ("L1 99, L1+L2 386").
- Python: `sandbox/py-suites/run.sh` → `pytest -c sandbox/py-suites/pytest.ini sandbox/py-suites/L3-ssi sandbox/py-suites/L4-exemplar-interactions 2_w3c-ssi-layer`: **94** ("L3+L4 94"). Not re-run here.

### 3.2 Theirs (measured in the worktree at `fa6188e`)
- Layout: 18 files — `test/{CVINCombined,ERC1056,ERC1155,ERC4337,ERC721,ERC725xy,ERC735,LSP8,MOBIVID,security,benchmarks}/…` (flat, pre-rename layout; see §1.2 list).
- Install: `npm ci` in `1_blockchain-identity/` (lockfile `package-lock.json` present, no `yarn.lock`; `node_modules` absent in a fresh checkout) — exit 0.
- `npx hardhat compile`: **47 Solidity files compiled** (evm target cancun), exit 0. (Their `test-contracts.yml` header comment still says "32 contracts compile, 47 tests pass" — stale on both sides.)
- `npx hardhat test`: **369 passing, 23 pending, 0 failing** (15 s), exit 0. All 23 pending are in `test/benchmarks/adapters.conformance.test.js` ("Benchmark adapter conformance"), titles of the form "D2 revoke attribute (or declared n/a)", "U5 meta-tx (or declared n/a)", "R2 resolve by VIN (or declared n/a)", "U2/R4/D1 delegate lifecycle", "rotateDelegate: new key valid, old key invalid (H-2)" — adapter-declared n/a, skipped by design.
- Python, exactly as `.github/workflows/w3c-compliance.yml` job `python-full-suite`: Hardhat node started from `1_blockchain-identity` on port 8548 (pid recorded and killed afterwards), `CV2X_TEST_RPC_URL=http://127.0.0.1:8548`, `CV2X_TEST_ARTIFACTS_DIR=<dir with contracts -> 1_blockchain-identity/artifacts/contracts/MOBI>`, `python -m pytest 2_w3c-ssi-layer cv2x-testbed/tests -q -rs`: **358 passed, 0 skipped, 0 failed** (12.70 s), exit 0. Collected per directory: `2_w3c-ssi-layer/did-resolution` 75, `2_w3c-ssi-layer/mobi-vid` 37 (starts its own Hardhat node on 8547), `2_w3c-ssi-layer/verifiable-credentials` 114, `cv2x-testbed/tests` 132.
- `cv2x-testbed/scripts/check_artifacts_fresh.js` (CI step "Testbed artifacts match a fresh compile"): exit 0, "cv2x-testbed artifacts are fresh (ERC1056Registry, MOBIVIDRegistry, MOBIVIDRegistryV2 + ERC1056Registry_{abi,bytecode})".
- Python 3.11.15, web3 8.0.0, pytest 9.1.1, numpy 2.4.6 (deps already present in this container).

### 3.3 Post-merge test breakage to expect (from the API deltas above)
- Ours → fail against theirs: `MOBIVIDRegistry.regression.test.js` :81, :93 (K-3); `CVINVehicleDIDRegistry.regression.test.js` :56, :90, :98 (K-1 signature); `CVINCombinedIdentity.regression.test.js` 5 `it()`s (K-6); `sandbox/options/erc-1056-uport/demos/attributes.js` :92, :93, :102.
- Theirs → fail against ours: `test/ERC735/CVINVehicleClaimHolder.test.js` (18 `addClaim` without `authorizeIssuer`), ERC-735 scenarios in `test/security/securityScenarios.test.js`; `test/ERC1155/…:235` revert string; `test/CVINCombined` "K-6" test (if D22 kept); `cv2x-testbed/tests/test_erc1056_key_resolution.py` docstring/assumption at :128 (DIDRevoked no `previousChange`) — behaviour still rejects, wording stale; their `scripts/security_scenarios.js` import path (§1.3); their `package.json` `test:*` globs (§1.3).

---

## 4. Scripts and results

### 4.1 Scripts
| script | ours | theirs |
|---|---|---|
| `1_blockchain-identity/scripts/benchmark_gas.js` | +6/−1: `authorizeIssuer(manufacturer, VIN_ATTESTATION)` and `(inspector, INSPECTION)` setup (D25a, not measured); ERC-1155 transferOwnership note | unchanged |
| `1_blockchain-identity/scripts/benchmark_scaling.js` | +1: `authorizeIssuer` before each ERC-735 `addClaim` | unchanged |
| `1_blockchain-identity/scripts/mobi_vid_backend_sweep.js` | +6: `authorizeIssuer` ×3 (MANUFACTURER_CERT, INSPECTION, INSURANCE) | unchanged |
| `1_blockchain-identity/scripts/security_scenarios.js` | see §1.3 | see §1.3 (broken require path after merge) |
| `1_blockchain-identity/scripts/experiment_pseudonym_pool.js` | — | NEW 521 lines (M5 pseudonym pool on `EthereumDIDRegistry`, schemes A/B0/B1/B2) |
| `4_comparison-framework/performance-metrics/run_gas_stats.py` | unchanged | +11/−5: `ci95` key renamed `range_min_max` (H-12: "not a CI"); description text |
| `4_comparison-framework/performance-metrics/{generate_scaling_tables.py,run_verify_richness.py}` | unchanged | +23/−?, +46 new |
| `4_comparison-framework/feature-matrix/make_feature_matrix.py` | NEW 111 lines (generates `docs/FEATURE_ASYMMETRY_MATRIX.md`; CI-gated) | — |
| `4_comparison-framework/security-analysis/{attack_scenarios.py,generate_attack_tables.py,README.md}` | unchanged | +87, +24, +10 |
| `cv2x-testbed/scripts/deploy_mobi_vid.js` | +21/−?: `MOBI_VID_CONTRACT` env selects V1/V2; writes `<Name>_abi.json` / `<Name>_bytecode.txt` | unchanged |
| `cv2x-testbed/scripts/check_artifacts_fresh.js` | — | NEW 77 lines (Q-9) |
| `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py` | unchanged | +206 (harness exported for the freshness script; T-9) |
| `cv2x-testbed/scripts/w3c_compliance_checker.py` | unchanged | +15 |
| `cv2x-testbed/scripts/run_comparison.py` | unchanged | 2 lines |
| `cv2x-testbed/scripts/experiment_{freshness_k,lifecycle_parity}.py`, `test_use_cases.py` | see §1.3 | see §1.3 |
| `1_blockchain-identity/benchmarks/**` (30 files), `analysis/analysis.js` | — | NEW metrics harness (`npm run metrics`, `test:conformance`) |

### 4.2 Results files regenerated — dates from the JSON `metadata.date` / `environment.date_utc` fields

| file | ours (`b70081c`) | theirs (`fa6188e`) |
|---|---|---|
| `4_comparison-framework/results/gas_benchmark.json` | `2026-10-04T22:20:14.461Z` (commit `d06d004`) | `2026-10-04T22:12:48.074Z` (commit `4573ee3`) |
| `4_comparison-framework/results/mobi_vid_backends.json` | `2026-10-04T22:23:25.375Z` (`d06d004`) | `2026-10-04T22:13:17.721Z` (`191b920`) |
| `4_comparison-framework/results/scaling_lifetime.json` | `2026-10-04T22:20:58.308Z` (`d06d004`) | `2026-10-04T05:27:35.783Z` (`36cde4d`) |
| `4_comparison-framework/results/scaling_marginal.json` | `2026-10-04T22:20:58.305Z` (`d06d004`) | `2026-10-04T05:27:35.782Z` (`36cde4d`) |
| `4_comparison-framework/security-analysis/results/attack_results.json` | `metadata.date` = `2026-07-19T21:10:16.411Z` (unchanged field; file touched in `d06d004`, 2 lines) | `metadata.date` = `2026-07-19T21:10:16.411Z` (unchanged field; file touched in `cc2ad53`, 150 lines) |
| `cv2x-testbed/results/freshness_k.json` | `2026-10-03T22:36:00+00:00`, git `1194565` dirty, n=200, chain 1337, rpc :8545, hardhat 2.27.0, deploy gas 878,509 | `2026-10-04T09:24:10+00:00`, git `8216507` clean, n=250, chain 31337, rpc :8554, hardhat 2.28.6, deploy gas 927,756, registry bytecode sha256 `8ca9cfe5…` |
| `cv2x-testbed/results/lifecycle_parity.json` | `2026-10-03T22:49:58+00:00`, git `e7a2541` dirty, `MOBIVIDRegistryV2` deploy gas 4,919,599, rpc :8547 | `2026-10-04T22:17:02+00:00`, git `4f09875` clean, deploy gas 5,059,513, rpc :8558, bytecode sha256 `94fcfeac…` |
| theirs-only: `cv2x-testbed/results/freshness_k.png`, `freshness_k_probe*` (16 files), `pki_vs_erc1056.{csv,json,md}` modified; `4_comparison-framework/security-analysis/results/{attack_results.csv,attack_results.tex,onchain_security.json,security_matrix.csv,security_matrix.json}` | — | present |

All four `4_comparison-framework/results/*.json` were regenerated on both sides on 2026-10-04 against different contract sets (ours: D7/D8/D13/D22/D25 bytecode; theirs: K-1/K-2/K-3/K-4/K-11/K-13), so every numeric cell can differ. Their `benchmark.yml` job `nine-standard-gas` fails on any `gasUsed` drift or added/missing cell vs the committed JSON (Q-12) → after a merge, `benchmark_gas.js` must be re-run and the JSON/CSV/TeX recommitted in the same change. Same for `cv2x-testbed/artifacts/**` (their `check_artifacts_fresh.js` gate) and for `cv2x-testbed/contracts/ERC1056Registry_bytecode.txt`.

---

## 5. Python testbed (`cv2x-testbed/identity/*.py`)

### `mobi_vid_provider.py` (both; 1 hunk / 45 lines in `verify_message`)
- Ours (+170): D11 verify against the **registered** key (`vehicle_did` → identity → local record; `isRevoked()` on-chain; embedded key must equal); D11b: generate key pair before birth, `_anchor_vehicle_key` tx after `registerVehicleBirth`, `_resolve_key_on_chain` (walk `lastChanged` → `previousChange` over `DIDOwnerChanged/DIDDelegateChanged/DIDAttributeChanged/DIDRevoked`, newest valid `did/pub/secp256k1/veriKey/base64`), `resolved_keys` cache; ABI from `artifacts/contracts/MOBIVIDRegistry.sol/MOBIVIDRegistry.json` (`_ARTIFACT_PATH`, `_contract_abi`), deploy bytecode fallback to artifact.
- Theirs (+78/−8): T-4 `_registered_key_for` (accepts `vehicle_identity` or `vehicle_did`; local record; `getVehicleInfo()` for on-chain revocation; "MOBIVIDRegistry anchors no signing key on-chain" — no longer true after D11b); `sign_message` adds `vehicle_identity`; `revoke_credential` returns False on `receipt.status != 1`.
- **Same defect twice: D11 ≡ T-4** (impostor key embedded in message). Ours is a superset (chain fallback). Resolution: our `verify_message` + their `vehicle_identity` field + their `receipt.status` check; choose one on-chain revocation call (`isRevoked` vs `getVehicleInfo`). Their `cv2x-testbed/tests/test_mobi_vid_verify.py` and our `sandbox/py-suites/L3-ssi/test_mobi_provider_{key_binding,onchain_key}.py` both must pass.

### `erc1056_provider.py` (both; 6 hunks / 114 lines: ctor, `_load_contract`, `verify_message`, `_resolve_key_from_events` tail)
- Ours (+150): verifier cache with `freshness_k` ctor arg (None=off, int≥1, 0/'inf'), `_cached_identity`, `_changed_block` (single raw `eth_call` of `changed()`), `verifier_cache_stats`, `clear_verifier_cache`; inline ABI gains `changed`; ABI path candidates (cwd, then module-relative); D21 comment (DIDRevoked now carries `previousChange`).
- Theirs (+250/−40): `refresh_every` (int≥1 or None) + `refresh_mode` ('full'|'probe'), `set_refresh_every`, `_probe_identity_info` (raw `eth_call` of `getIdentityInfo`), counters; **T-9 `FreshnessPolicy` (timestamp window + replay cache) — `sign_message`/`verify_message` now sign `signed_bytes(message, timestamp)` (wire-format change)**; DID bound to local chain id; **T-2 `_resolve_key_from_events` rewritten as collect→replay→select with `_ValidityClock`/`CLOCK_SKEW_S`, max_hops 256**; T-5 drop redundant `isRevoked` call; T-11 doc on `vehicle_account`; module-relative `_ABI_PATH`; keeps "DIDRevoked carries no previousChange" (K-5).
- **Same feature twice (freshness-k cache), incompatible APIs** (`freshness_k=` vs `refresh_every=`/`refresh_mode=`); each side's `experiment_freshness_k.py` and `results/freshness_k.*` depend on its own API. Only consumer of ours in `sandbox/`: `sandbox/py-suites/L4-exemplar-interactions/test_experiment_records_are_well_formed.py:13` reads `cv2x-testbed/results/freshness_k.json` (schema check). Resolution: take theirs as base (T-2/T-9 are correctness fixes with 132 testbed tests), port our `changed()`-only probe as a third `refresh_mode` if wanted, take their `experiment_freshness_k.py` + results, and re-check our L4 schema test against their JSON.

---

## 6. Resolver (`2_w3c-ssi-layer/did-resolution/did_resolver.py`, 19 hunks / 257 lines)

| concern | ours (2026-10-03 fixes) | theirs (G-R R1–R4, S-10) | same? |
|---|---|---|---|
| DID syntax | `DID_SYNTAX` regex (DID Core 3.1 ABNF) → `invalidDid`; unknown method → `methodNotSupported`; `DIDResolutionError(Exception)` | `_DID_RE.fullmatch` (same ABNF) → `invalidDid` / `methodNotSupported`; `DIDResolutionError(ValueError)` | same fix, different class base |
| metadata shape | `DIDResolutionMetadata.to_dict` / `DIDDocumentMetadata.to_dict` omit None/[]/False; `contentType` popped for `resolve()` | R1 error only on failure, R2 contentType only on representation, R3 no nulls; same two `to_dict`s (default `contentType=None`) | same fix |
| timestamps | `xml_datetime_now()` → `%Y-%m-%dT%H:%M:%SZ` | R4 `xml_datetime(dt=None)` same format | same fix |
| resolveRepresentation | `resolve_representation(did, accept)` + alias `resolveRepresentation`; returns `DIDResolutionResult` with new field `didDocumentStream`; `DIDDocument.to_representation()`; `representationNotSupported` | `resolve_representation(did, accept)` returns **new dataclass `DIDRepresentationResult`**; `representationNotSupported` | same feature, different return type |
| per-method id checks | part-count checks for ethr/key/nft/mobi → `invalidDid` | part-count checks + `_ETH_ADDRESS_RE`/`_ETH_PUBKEY_RE` (compressed secp256k1 identifiers via `eth_keys`), did:ethr network names | theirs stricter |
| **`blockchainAccountId` chain id (our D27)** | **still hex**: `blockchainAccountId=f"eip155:{chain_id}:{address}"` with `chain_id` the raw DID segment (e.g. `eip155:0x7a69:0x…`) at lines 462/503/551 — D27 is listed OPEN in our `docs/DEFECT_LOG.md` (line 71: "nothing — mechanical") | **fixed (S-10)**: `parse_chain_id()` → decimal (`eip155:31337:0x…`), hex/decimal/network-name accepted; asserted by their `tests/test_did_resolver_review02.py` (:105, :114) and `verifiable-credentials/tests/test_s3_key_binding.py:94` (`startswith("eip155:1:")`) | **theirs fixes D27; ours does not** |
| cache | unchanged dict; caches every result reached (errors raise earlier) | `cache_ttl_s`, monotonic stamps, `copy.deepcopy` on store and on hit (S-10 poisoning fix) | theirs only |
| error path | `_error_result()` helper (empty stream on representation) | inline error results | equivalent |

Resolution: take theirs as base (75 pytest cases in `2_w3c-ssi-layer/did-resolution/tests/`), port our `DIDDocument.to_representation()` and the `resolveRepresentation` alias, then re-run the external W3C DID test suite (`docs/conformance/W3C_DID_TEST_SUITE.md`, ours 335/336) and regenerate `docs/conformance/implementations/*.json` via `generate_implementations.py` (both conflicted). Our compliance floor 94.0 was measured on our resolver; their checker (`w3c_compliance_checker.py` +15) and their resolver give an unknown post-merge score → re-measure before choosing the floor.

---

## 7. CI (`.github/workflows/`)

| file | ours vs base | theirs vs base | merge |
|---|---|---|---|
| `benchmark.yml` | unchanged | +44: new job `metrics-harness` (`npm run test:conformance`, `npm run metrics` → `benchmarks/run.js`, uploads `results/metrics/latest`); Q-12 drift check also fails on missing/new cells | clean (theirs) |
| `test-contracts.yml` | +19: step "MOBI contract copies byte-identical" (`cmp` for ERC1056Registry, MOBIVIDRegistry, MOBIVIDRegistryV2 between `1_blockchain-identity/contracts/MOBI` and `cv2x-testbed/contracts`); step "feature-asymmetry matrix up to date" (`python3 4_comparison-framework/feature-matrix/make_feature_matrix.py` + `git diff --exit-code docs/FEATURE_ASYMMETRY_MATRIX.md`) | unchanged | clean (ours) |
| `w3c-compliance.yml` | `COMPLIANCE_FLOOR` 93.0 → 94.0 (+comment); new job `python-layers` (pip only; runs `sandbox/py-suites/run.sh`) | new job `python-full-suite` (npm ci + compile; `check_artifacts_fresh.js`; Hardhat node :8548; `pytest 2_w3c-ssi-layer cv2x-testbed/tests`; fails if any test is skipped) | auto-merged, 0 hunks |

Coexistence: yes — job ids are disjoint (`vc-layer-tests`, `python-full-suite`, `compliance-score`, `python-layers`, `hardhat-tests`, `gas-benchmarks`, `nine-standard-gas`, `metrics-harness`). Overlaps/caveats: (a) both `python-layers` and `python-full-suite` run `2_w3c-ssi-layer`; our job installs no Node, so their `mobi-vid/tests/test_mobi_vid_layer.py` would `pytest.skip` ("1_blockchain-identity/node_modules missing") there — tolerated by our job, fatal only in theirs (which has the deps); (b) the floor must be re-measured post-merge (§6); (c) our `cmp` gate forces every MOBI `.sol` edit to be mirrored to `cv2x-testbed/contracts/` (both sides kept their copies identical in their own trees — verified); (d) their `nine-standard-gas` and `check_artifacts_fresh` gates force regeneration of `gas_benchmark.json` and `cv2x-testbed/artifacts/**` in the merge commit; (e) their `metrics-harness` job runs their new `benchmarks/` adapters against the merged contracts — ERC-735 adapter will hit D25a (`addClaim` needs `authorizeIssuer`) and ERC-1056 adapter hits K-1 only if it calls `setVehicleAttributes` (their PASS1_K notes it uses eight single `setAttribute`s).

---

## 8. Merge-risk ranking — 10 files most likely to need a hand merge

1. `2_w3c-ssi-layer/did-resolution/did_resolver.py` — 19 hunks / 257 lines; two independent re-implementations of DID Core 7.1 with different types (`DIDRepresentationResult` vs `didDocumentStream` field); D27 fixed only on theirs; 75 of their tests + our 6 conformance JSONs + the 335/336 external-suite claim depend on exact output shape.
2. `cv2x-testbed/identity/erc1056_provider.py` — 6 hunks / 114 lines; two incompatible cache APIs (`freshness_k` vs `refresh_every`/`refresh_mode`); theirs also changes the signed wire format (T-9) and the key-resolution algorithm (T-2); each side's `experiment_freshness_k.py` + `results/freshness_k.*` (add/add, 1077 conflict lines) only works with its own provider.
3. `1_blockchain-identity/contracts/CVINCombined/CVINCombinedIdentity.sol` — only 2 hunks, but D22 and K-6 are mutually exclusive designs; 5 of our regression `it()`s and 1 of theirs assert opposite `changed()` behaviour; `DIDClaimChanged` has 10 further consumers on ours (sandbox demo, manifest, feature matrix, docs).
4. `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol` + byte-identical `cv2x-testbed/contracts/ERC1056Registry.sol` — 4 hunks each; modifier vs inline require; `DIDRevoked` ABI change (ours) vs their explicit K-5 decision and test wording; needs `virtual` from theirs; forces regeneration of `ERC1056Registry_{abi.json,bytecode.txt}` and 2 artifacts JSON (both conflicted) and must satisfy our `cmp` gate and their freshness gate.
5. `1_blockchain-identity/contracts/ERC735/CVINVehicleClaimHolder.sol` — 3 hunks / 56 lines in header, `addClaim`, `removeClaim`; complementary but every one of their 18 ERC-735 `addClaim` test calls and the 12 in their security test need `authorizeIssuer` setup; gas tables move again.
6. `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol` + `cv2x-testbed/contracts/MOBIVIDRegistry.sol` — 2 hunks each; D10 ≡ K-15 identical code (comment conflict); adjacent insertions (`anchorVehicleKey` vs `changeOwner` override); our regression test :81/:93 contradict K-3; `MOBIVIDRegistry.json` artifact conflict.
7. `cv2x-testbed/identity/mobi_vid_provider.py` — 1 hunk / 45 lines but `verify_message` rewritten twice (D11 ≡ T-4) with different helper shapes; their comment "anchors no signing key on-chain" is false after D11b; both test suites (`cv2x-testbed/tests/test_mobi_vid_verify.py` vs `sandbox/py-suites/L3-ssi/test_mobi_provider_*`) must pass.
8. `cv2x-testbed/scripts/experiment_lifecycle_parity.py` (add/add, 802 vs 411 lines, 1173 conflict lines) with `cv2x-testbed/results/lifecycle_parity.{csv,json,md}` (add/add) — pick one lineage and re-run against the merged `MOBIVIDRegistryV2` (deploy gas differs: 4,919,599 ours vs 5,059,513 theirs, and will differ again).
9. `1_blockchain-identity/contracts/ERC1056/CVINVehicleDIDRegistry.sol` — 1 hunk only, but K-1 changes the `setVehicleAttributes` ABI; 6 call sites on ours (3 regression-test, 3 sandbox demo) to update; D18 ≡ K-1 so our constant is redundant.
10. `1_blockchain-identity/scripts/security_scenarios.js` + `4_comparison-framework/security-analysis/results/attack_results.json` — the script auto-merges textually, yet their new `require("../test/security/attackHarness")` points at a path we moved (`test/L2-identity-system/security/attackHarness.js`), and both sides edited `attack_results.json` cells (2 vs 150 lines) → fix the path, re-run, recommit. Same class of silent breakage: their rewritten `package.json` `test:*` globs target the pre-rename `test/<Std>/` directories.

Also notable but mechanical: `1_blockchain-identity/contracts/ERC1155/CVINVehicleCredential1155.sol` (ours is a superset of K-13; align one revert string with their test :235); `LSP8/CVINVehicleLSP8.sol` (2 hunks, union in `mintVehicle`); the 14 `4_comparison-framework/results/*` files (regenerate, do not merge); 18 doc conflicts incl. three same-named `AFTER_ACTION_REPORT_0{3,4,5}.md` written independently on each side (renumber one set); 8 rename/delete conflicts under `_research-copies/` (choose delete or keep).
