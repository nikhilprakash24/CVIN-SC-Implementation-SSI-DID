# After-Action Report 06 — The Remaining High-Severity Defects and the Conformance Follow-up

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-04, after Report 05 closed; updated per step; closed at the end
**Trunk at start:** `a764387`, clean, CI green
**Input:** `docs/DEFECT_LOG.md` §C and the "next executable" list in the handback addendum 0c.
The author said "continue".

## 0. Rule for every step
Unchanged from Report 05 §0: a fix lands only with a regression test in the layer that
owns the path, the affected demos green, the grand runner green, and every result of
record the fix moves regenerated or annotated (register row, delta file).

## 1. Plan

| # | Item | What is done | Regression test owner | Results moved |
|---|---|---|---|---|
| G1 | D7 / D8 — ERC-1155 BIRTH_CERT moved by a standard transfer does not re-bind the VIN; standard transfers reach unregistered addresses; burning the BIRTH_CERT orphans the other credentials; any issuer revokes any issuer's credential | override `_update` so the BIRTH_CERT is soulbound to the standard path (only `issuerTransferCredential` moves it and re-binds); block standard transfers to unregistered addresses; block burning a BIRTH_CERT while other credentials exist; revocation restricted to the issuing issuer or the admin | L2 ERC1155 suite + one security-harness scenario | ERC-1155 gas cells (transfer/revoke; register #31 extended) |
| G2 | D11b — the vehicle key is never anchored on-chain | at registration the provider publishes `did/pub/Secp256k1/veriKey/hex` as an ERC-1056 attribute from the identity's controller; `verify_message` falls back to the on-chain attribute when no local record exists | L3 pytest (chain-free for the fallback logic) + an L4 Hardhat-backed test if the harness is cheap | none in the nine-standard table (MOBI column is an application profile; the registration gas is recorded as a note) |
| G3 | D9 — `payToll` after `renounceOwnership` burns the toll | guard `owner() != address(0)` | L2 ERC721 suite | none |
| G4 | D10 follow-up — the external W3C DID test suite has only run on the resolver's own fixtures | mint a `did:ethr` from `MOBIVIDRegistry` on a Hardhat node, resolve it through the resolver, feed the result to the suite's implementation files, re-run | `docs/conformance/` write-up and raw report | conformance row (register #4 note) |
| G5 | Chapter-5 tables quote July gas values | regenerate from the 2026-10-04 `gas_benchmark.json`; mark the re-execution note resolved | — | the chapter tables (register #25/#31 are the sources) |

Order: G1 and G3 together (contracts; one compile); G2 after (Python; the ERC-1056
attribute path exists since D18/D21); G4 and G5 after the chain is settled.

## 2. Execution log
- 2026-10-04 — report opened; state check (tree clean at `a764387`); code read for G1/G3 requested.
- **G1 (D7/D8) designed and landed.** Reading the callers showed the real problem was structural, not a missing `require`: the adapter, the benchmark, the security script and six demos all moved the BIRTH_CERT *alone*, and nothing on-chain knew which other credentials a vehicle held. Fix in `CVINVehicleCredential1155`: (i) the standard `safeTransferFrom` / `safeBatchTransferFrom` entry points are overridden to revert for everyone — no transient flag, no sender check; the issuer paths call the internal transfers directly (D7); (ii) a per-vehicle **bitmap of held credential types** maintained in `_update`, which requires credential types ≤ 255 (`MAX_CREDENTIAL_TYPE`) — the price of making the held set enumerable on-chain (decision D-G); (iii) `issuerTransferCredential`: non-BIRTH types only to a registered vehicle, the BIRTH_CERT alone only when nothing else is held; (iv) new `issuerTransferIdentity(from, to)` moves the BIRTH_CERT and every held type in one `TransferBatch` and re-binds the VIN (`IdentityRebound` event); (v) `revokeCredential(BIRTH_CERT)` refuses while other credentials are held (no orphans); (vi) `setTokenURI` emits the standard `URI` event. The flat issuer role (any issuer may revoke another's credential) is documented, not fixed, because a fungible balance carries no issuer. 13 regression tests; two older L2 tests that asserted the old behaviour updated; L1 99/99 and the smoke still pass with the adapter now using `issuerTransferIdentity` and revoking held credentials before the BIRTH_CERT. Gas: `issuerTransferCredential(BIRTH_CERT)` 86,298 on a clean vehicle; `issuerTransferIdentity` with two held types 164,830 (register #31 to be extended after the benchmark re-execution).
- **G3 (D9) landed**: `payToll` reverts "no toll operator (ownership renounced)"; 2 regression tests (toll reaches the operator; after renounce the revert returns the ether).
- **G2 (D11b) landed.** `MOBIVIDRegistry.anchorVehicleKey(identity, publicKey)` publishes the key as the ERC-1056 attribute `did/pub/secp256k1/veriKey/base64` (decision D-H: the name `registerVehicle`, `updateVehicleKey` and both resolvers already use, so one walk finds the key whichever path wrote it) with the 100-year validity; the registering manufacturer may anchor once and only before the first sale, the owner at any time. Both contract copies byte-identical; 4 L2 regression tests including a JS re-implementation of the resolver walk (2 hops through an unrelated later attribute). Provider: the key pair is generated *before* the birth and anchored right after it (second transaction, 69.7–69.9 k gas); `verify_message` falls back to the on-chain attribute (walk from `lastChanged`, cached) when it holds no local record. **Found on the way:** the provider's inline bootstrap ABI lacked `isRevoked`, so the D11 fix's on-chain revocation check could never have run through it — the provider now loads the compiled Hardhat artifact (cv2x-testbed/artifacts) first, and `deploy_contract` takes its bytecode from the same artifact (the `_bytecode.txt` it expected does not exist in the tree). 7 chain-free L3 tests (94 Python total); `scripts/test_mobi_vid.py` passes end to end against a Hardhat node; a separate acceptance script verified that a *second* provider with empty local state verifies a message through the real walk, rejects an impostor, and sees the on-chain revocation. `keys-delegates.js` exercises the new surface (MOBIVIDRegistryV2 57/57); manifests and matrix regenerated.
- **Demos for the ERC-1155 / ERC-721 fixes** (delegated; accepted by my own run, 18/18): the standard-path steps now assert the closed entry points, `issuerTransferIdentity` is exercised end to end (event, batch, held types, VIN indexes, no `keccak("")` alias), the no-orphan and type-range reverts and the `URI` event are asserted, and the toll demo asserts the D9 revert. READMEs split fixed from open; ERC-1155 coverage 34/34. Commit `7404e94`.
- **Results of record re-executed** on the final contracts: nine-standard table — 10 of 61 cells moved, all ERC-1155 (D7/D8) and MOBI (D11b, dispatch offsets), listed with causes in `gas_moved_by_defect_fixes_2026-10-04_pass06.json`; scaling experiments A and B re-executed (marginal O(1) holds; ERC-1155's first-op step is now ×2 cold slots because of the bitmap; lifetime ranking unchanged, CVIN-Combined 9,839,660 still below MOBI-VID-V2 9,848,183); the MOBI backend sweep (H4) re-executed **for the first time on the trunk** — and could not run at first: `mobi_vid_backend_sweep.js` had been broken since the D25 issuer registry (unauthorised issuers), a caller the pass-05 sweep of callers missed; fixed (per-topic `authorizeIssuer` as setup), 15/15 cells moved (ERC-735 +2.5 k from the issuer check, ERC-1155 lifecycle 57,126 → 80,131 from the bitmap), fidelity scores unchanged. Register #26 → V, #32 added. The `scaling_verify_*` figures were restored after an incidental re-render (their data did not change).
- **G4 done** (delegated): the external W3C DID test suite re-run on `did:ethr:0x7a69:0x2244c598f83916430028a1b3c438c640ca0e0375`, minted by `MOBIVIDRegistry.getVehicleDID` on Hardhat at `d941ad5` — **335/336**, identical to the fixture run on the same day and commit, same single `did:nft` failure (§7.4). `generate_implementations.py` takes `--ethr-did`; the registry-DID inputs and raw reports are under `docs/conformance/`; write-up §8. One observation logged as **D27**: the resolver writes `blockchainAccountId` with a hex chain id where CAIP-10 uses decimal (not scored by the suite). §8.5 states the limit honestly: the suite certifies the identifier and the document shape, not on-chain state (the resolver builds the document from the identifier alone).
- **G5 done**: chapter 5 regenerated — the four result tables (§5.2 gas, §5.3.1 MOBI sweep, §5.9.1 marginal, §5.9.2 lifetime) rebuilt by script from the JSON files of record, every quoted figure in the prose updated (ratios recomputed: ~32× spread, ~10.4× ERC-721/ERC-1056, 46,830-gas 4337 indirection), the cold-slot sentence corrected for ERC-1155, §5.5 updated to the current checker (94.3 %, 14/15 + 27/29, 41 PASS + 1 PARTIAL + 2 FAIL / 44; results of record refreshed from the checker run), the H2 row and the chapter's top note replaced by a regeneration note. The same cells fixed in README.md, thesis README, chapters 6 and 7.

## 3. Decisions
- **D-G** — ERC-1155 credential types are bounded to 1..255 so that the set a vehicle holds is a per-vehicle bitmap the contract can enumerate (`credentialTypesOf`) and move atomically (`issuerTransferIdentity`). The alternative (an array of distinct types per vehicle) costs ~60 k gas on first issuance of a type versus ~22 k for the bitmap, and an open type space is not a property any demo or experiment relied on (the widest type used anywhere is 7). This is a model constraint and is stated in the contract NatSpec.
- **D-H** — the anchored MOBI vehicle key uses the attribute name `did/pub/secp256k1/veriKey/base64` already used by `registerVehicle`, `updateVehicleKey`, the ERC-1056 provider and the DID resolver, rather than a new `…/hex` name, so that every existing walk finds it; the value is the raw 65-byte point (as it already was for `registerVehicle`), the "base64" in the name being historical. The manufacturer's power to anchor is one-shot and ends at the first sale.
- **D-I** — the standard ERC-1155 transfer entry points are closed outright rather than gated: a gate that admits "issuer who is also an approved operator" is exactly what D7 exploited, and no caller in the tree used the standard path legitimately.

- **Grand run on the final tree**: ALL OK — smoke 11/11, L1 99, L1+L2 **386**, L3+L4 **94**, demos 92/92 with **1,722** steps and 62 flagged observations (pass 05 closed at 366 / 87 / 1,688 / 66: +19 Hardhat and +7 Python regression tests, +34 demo steps, four fewer flags because D7/D8/D9/D11b are now asserted reverts or anchored state).

## 4. Closing

**What was done.** The last two high-severity defects (D7, D11b) and two medium ones (D8's
first three parts, D9) are fixed under the same rule as pass 05; every result of record was
re-executed on the final contracts; the conformance claim was re-run on an identifier the
registry itself produced; and chapter 5 no longer quotes a single pre-fix number. The defect
log's open list now contains only items that need an author decision, plus two mechanical
ones (D27, the `credentialTypesOf`-style documentation of the flat issuer role).

**What this pass found that nobody was looking for.** Three things, all of the kind the
sandbox was built to surface. (1) The MOBI backend sweep — the H4 table's source — had been
silently broken since the D25 issuer registry: a caller the pass-05 sweep of callers missed.
It had never been re-executed on the trunk, so the chapter's §5.3.1 numbers were still the
bundle lineage's. It now runs, and the table is from the trunk. (2) The MOBI provider's
inline bootstrap ABI lacked `isRevoked`, so the D11 on-chain revocation check added in pass 05
could never have executed through it; the artifact ABI is now authoritative, and the
two-provider acceptance proves the whole chain-side path. (3) The resolver's
`blockchainAccountId` uses a hex chain id where CAIP-10 uses decimal (D27, low, mechanical).
Each is a sentence for the implementation chapter's veracity discussion: "implemented"
surface that no test reached was wrong in ways that did not show until the surface was
exercised end to end.

**What I changed my mind about.** I first designed D7 as a gate ("issuer *and* internal
re-binding path"); reading the callers showed that no legitimate caller used the standard
path at all, and that the gate's admitted case was exactly the exploit. Closing the entry
points outright (D-I) is simpler and strictly safer. I also first planned to enumerate held
credentials with a per-vehicle array; the bitmap (D-G) is three times cheaper and the type
bound it imposes is a constraint nothing relied on.

**What the fixes cost.** ERC-1155's first issuance of a credential type now pays one extra
cold SSTORE (+22,994) so the identity can move atomically; its deployment grew by 491 k; the
MOBI registry's by 204 k. Register #32 lists every cell. The lifetime ranking in §5.9.2 did
not change, but ERC-1155's lifetime estimate rose ~6 %: the price of knowing, on-chain, what
a vehicle holds.

**What I did not do.** No open **M** item needing an author decision was touched (D12,
D15, D16-rest, D19, D20, D23, D24, D25c, D26). D27 is mechanical and short but touches the
resolver, whose conformance inputs would then be regenerated; it is left for the next pass
so that this pass's conformance run stays attributable to one resolver version. The
lifecycle-parity experiment (#30) was not re-run after D11b made MOBI registration a
two-transaction operation; the row is annotated. The SUMO half of the plan still waits on
the author's install go-ahead.

**Trunk at close:** `7404e94` + this closing commit; tree clean after push; CI read on the
closing commit and recorded in the handback.
