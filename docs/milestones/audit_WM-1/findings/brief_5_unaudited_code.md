> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`. Dispositions: after-action report 12 §4.

### Findings

**F1 | high | docs/MEASUREMENT_CONDITIONS.md:120 (copy at docs/thesis/CRUX_REGISTER.md:30) | Row #34 (status V) gives C1 create as "76,808 / 145,662 / 399,844 / 656,480 / 1,535,776 (ERC-735) / 103,913 (ERC-1155) / 1,730,753 (ERC-725xy) / 132,515 (LSP8) / 808,431 / 266,995", and its merge note says it was re-executed on 2026-10-09 | The committed run of record `1_blockchain-identity/results/metrics/latest/tables/crud_gas.md` (run 2026-10-09T02-09-36Z_7a9a996) reads 76,830 / 145,684 / 402,567 / 656,480 / 1,757,881 / 107,729 / 1,730,753 / 135,544 / 808,431 / 271,402. 8 of 10 cells differ. `sandbox/grand/report/L1-asymmetry.md` shows ERC-735 create 1,757,881, and my own `npx hardhat test` reproduced it. The row's numbers make ERC-725xy the heaviest create, while chapter 5 (README.md l.91) says ERC-735 is. Row #39 says its tables are "byte-identical to #34". | Replace the row with the 2026-10-09 table and re-run the stale-number check against crud_gas.md.**

**F2 | high | cv2x-testbed/identity/erc1056_provider.py:977 (`_ValidityClock.is_valid`; CLOCK_SKEW_S = 900 at :50) | D4/T-2 is recorded as fixed: a key revoked by its owner no longer verifies | `is_valid` returns True without reading the chain when `valid_to > wall + 900`. A revocation sets validTo to the chain's `block.timestamp`. So when chain time is more than 900 s ahead of the verifier's wall clock, a revoked key still resolves as valid. Repro on a fresh Hardhat node (port 18549): `test_erc1056_key_resolution.py` gives 8 passed. After `evm_increaseTime` (chain-wall skew 1164 s) it gives 3 failed, with "AssertionError: resolver returned a key its owner revoked". The same 3 failures appear on any reused node: the test file is not idempotent. CI passes only because its node is fresh. | Compare against the latest block time (or do a fresh read) instead of wall time, and add a skewed-clock test.**

**F3 | high | 2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py:340-349 (`signing_payload`); 2_w3c-ssi-layer/mobi-vid/lifecycle_events.py:420 and :431; 1_blockchain-identity/contracts/ERC721/CVIN_NFT_DID_ERC721_Monolithic.sol:155 | DEFECT_LOG.md:76: "Each fix lands with a regression test"; VC proof binding and MOBI lifecycle integrity are certified by passing suites | Mutation survivors, each reverted afterwards. (a) `signing_payload` made to return `canonicalize(doc)` only, so challenge, domain, proofPurpose, verificationMethod and created are no longer signed: all 358 Python tests still pass. The real code does reject edits to those fields (my PoC `vc_poc.py`), but no test pins it. (b) `detect_odometer_rollback` made to never flag: all 37 mobi-vid tests pass. The only test asserts `== []`; there is no positive case. (c) `sig_ok = True` in `_verified_attestations`: passes, and no test exercises `signatureValid` False. (d) D2: changing `_balances[to] += 1` back to `+= tokenId` leaves `npx hardhat test` at 536 passing. Only the sandbox demos (erc-721 creation.js and controller.js) fail on it. | Add tests that edit each proof option and expect rejection. Add a positive rollback test and a forged-attestation test. Add a Hardhat test for D2 with tokenId > 1.**

**F4 | high | docs/thesis/chapter7-conclusion/README.md:143 and :91; chapter5-results/README.md:428-432; chapter6-discussion/README.md:202-204; cv2x-testbed/scripts/w3c_compliance_checker.py:837-866 | "A W3C-compliant SSI layer … 94.3%"; "lifted to W3C DID/VC conformance"; "no structural incompatibility … gap is entirely in canonicalization and cryptosuite registration"; H2 "Supported" | I reproduced the score: 41 PASS + 1 PARTIAL + 2 FAIL of 44 = 94.3%, a unit-weighted mean. My classification of the 44 checks:**
- 23 are structural checks of documents the code emits itself (12 DID Core on a document synthesised from the DID string, 11 VC/VP property-presence checks).
- 14 execute a negative case.
- 5 are positive end-to-end checks.
- 2 are constant FAILs: the canonicalisation check always returns FAIL, and the cryptosuite check returns FAIL unless a constant changes.
- None asserts on source text.

Checker mutants: I ran 8 security-relevant mutants (not-yet-valid skipped, proofPurpose skipped, status-registry/issuer binding skipped, status id mismatch accepted, chain-id check removed, holder binding skipped, garbage verificationMethod type, disclosure digest skipped). Seven leave the score at 94.3% and exit 0; only the digest mutant moves it, to 92.0%.

Register #4 itself says "the score measures document structure … Label it so in chapter text", and that decision is still pending. Chapters 5.5, 6.4 and 7 do not label it.

A third deviation is undisclosed: `credentialStatus` type `CvinRevocationRegistry2024` (vc_issuer.py:119) is an in-memory, unsigned, thesis-defined list, not a registered status method. `DataIntegrityProof` with an unregistered cryptosuite cannot be verified by a standard Data Integrity library.

thesis/README.md:72 says "DID Core v1.0 93.3% (13/15)"; the checker and chapter 5 give 96.7% (14/15).

**Fix:** state "structural self-score" in chapters 5.5, 6.4 and 7, drop the "conformance/compliant" wording, list the status-method deviation, and correct thesis/README.md:72.

**F5 | medium | 2_w3c-ssi-layer/did-resolution/did_resolver.py:469 (`_resolve_ethr`); docs/thesis/chapter4-implementation/README.md:38; docs/MEASUREMENT_CONDITIONS.md:69 | Chapter 4: "the DID resolver turns an on-chain address or token into a DID Document". Row (V, chapter-grade): "0.009 ms cold / 0.002 ms warm" | `blockchain_provider` is never used; the code comment says "In production, would query ERC-1056 registry". The document is built from the DID string: `created` is the current time and `versionId` is "1", so rotation, deactivation and revocation are invisible. No chapter says this; only register #4 and the vc_verifier docstring do. The latency was measured at f602fdf, and three resolver commits since (bd18057, fa5e373, 93f4331) added deepcopy and metadata. Re-timed now (median of 30 after 3 warm-ups, with the per-call print inside `resolve()`): cold 0.068 ms, warm 0.045 ms, about 7x and 20x the recorded values. | State "synthesises the document, no chain read" in chapters 4/5. Re-measure at HEAD or mark the row S.**

**F6 | medium | README.md:36 and :183; docs/MEASUREMENT_CONDITIONS.md:96; docs/conformance/W3C_DID_TEST_SUITE.md:53-57 | "External W3C DID test suite 335/336" supports H2, "also on a registry-minted did:ethr" | Recomputed from `reports/merged-2026-10-06` jest JSON: default 336 tests / 335 passed / 1 failed; registry-minted the same; control 347/347.**
- **The failing test:** `invalidDid` on the nft vector `did:nft:0x1:0xabc`, an input the author chose.
- **Suite integrity:** the registration diff only adds `require(...)` lines, so no test is loosened; the suite commit 939b31d is pinned; regenerated implementation files equal the committed ones.
- **Limits not carried to the README/H2 rows:**
  - The suite is static-vector: it "does not call the resolver at run time", so it checks recorded output for 3 fixed DIDs.
  - The registry-minted run changes only the identifier string, because the resolver does not read the registry, so it adds no evidence about the resolver.
  - The denominator fell from 441 to 336 because tests are only instantiated for keys present in the output. Register #24 discloses this; the README and chapters do not.
  - DID-URL dereferencing (7.2), JSON production, consumers and didParameters are not run.
  - Row #24 cites §9, but the merged result is §12.
- I did not re-run Jest (network).

**Fix:** write "336 generated tests on 3 recorded documents; dereferencing not run" in the README/H2 rows, and do not present the registry-minted run as extra resolver evidence.

**F7 | medium | .github/workflows/w3c-compliance.yml:184-201; README.md:8 | README: "all run in CI with no skips"; WM-1 report: "Python layers 291" | Job `python-layers` runs `sandbox/py-suites/run.sh` with no `npm ci`, no compile and no skip gate. I simulated that environment by hiding node_modules and artifacts: "264 passed, 27 skipped", exit 0. Without a node, `pytest 2_w3c-ssi-layer cv2x-testbed/tests` gives 318 passed, 40 skipped, exit 0 (67 skipped when port 8547 is busy). Only `python-full-suite` has the skip gate: it gives 358 passed and 0 skipped with a node, which is not the 291 quoted. | Add the skip gate to python-layers and install node, or state the 27 skips.**

**F8 | medium | docs/THREAT_MODEL.md:5, :63, :76, :89; docs/MEASUREMENT_CONDITIONS.md:95; 1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol:160-172 | "54 executable attack scenarios … 43/43 applicable"; G3 replay resistance "nonce/domain/chain binding"; test cited at `test/security/securityScenarios.test.js` | `attack_results.json` has 43 DEFENDED and 11 N/A, so 43 attacks are executed, not 54. Neither `test/security/` nor `test/MOBIVID/attestEventRegression.test.js` exists; the real paths are `test/L2-identity-system/security/` and `.../per-option/MOBIVID/`. The ERC-1056 signed digest is `0x19 0x00 || this || nonce || identity || op || newOwner`, with no `block.chainid`, in all 5 `*Signed` functions. A signature is therefore replayable on another chain where the registry has the same address and the signer has the same nonce. I did not execute this (the in-process network has one chain id), so it is source-based and unconfirmed. "EIP-155 chain binding" is a mislabel. | Fix the counts and paths. Add the chain id to the digest, or narrow G3 for ERC-1056.**

**F9 | medium | docs/DEFECT_LOG.md:50 and :84-96; docs/thesis/chapter5-results/README.md:479-483; chapter6-discussion/README.md:50-56; CAPABILITIES.md:119 | Chapters 5/6 call ERC-4337 guardian recovery "genuine on-chain key recovery" (a tick in the security matrix). DEFECT_LOG §C lists the open items | PoCs in my clone (`scripts/zz_poc.js`, in-process):**
- **D15 confirmed:** after `recoverOwner` the guardian stays, and it can take ownership again without the owner.
- **D23 confirmed:** `execute(CALL setValue(777))` leaves target.value at 0.
- **D26 confirmed:** `changeOwner(id,0)` hands control back to the identity address.
- **New, not in the log:** `changeOwnerSigned(identity=0x0, v=27, r=0, s=0)` called by a stranger succeeds, because ecrecover returns 0 and `identityOwner(0)` is 0. A stranger can seize owners[address(0)]. Impact is limited to DID 0x0.
- **Caveats missing from the text:** no chapter caveats the guardian (D15). D22 is counted among the "every H item is fixed" items (DEFECT_LOG.md:24-26), yet its own text lists open parts (revokeDelegate stores a timestamp, no low-s guard, no identity-level revocation) that are missing from §C.

**Fix:** add D22's open parts and the zero-identity defect to §C, and caveat D15 wherever the recovery tick is claimed.

**F10 | medium | 1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol:335-380; docs/THREAT_MODEL.md:85-89 | The `attestEvent` gap is called closed; G4 says "a party cannot act beyond its role" | `attestEvent` checks only that the event exists, that `authorizedIssuers[msg.sender] != NONE`, and that the signature recovers to msg.sender. That signature is a self-signature and adds no authority. Any role-holder can attest any vehicle's event. The same attester can also push duplicate attestations, since there is no uniqueness check; this part is source-based, not executed. The review-2 item "restrict `attestEvent` to owner/delegates" (docs/review02/FOLLOWUP_GM.md:61) remains open and appears in neither the THREAT_MODEL nor the DEFECT_LOG. | Record it as an open defect and narrow the "closed" wording.**

**F11 | medium | docs/MEASUREMENT_CONDITIONS.md:30 vs :131 (#47) and :95 (#28) | "Gas (M1) is deterministic … a single run is exact" | The register itself records ±12 gas (#47, A4 "did not hold") and 192,659-192,683 (#28). My `npx hardhat test` against the committed `sandbox/grand/report/L1-asymmetry.json` differs in two places. CVIN-Combined claim is 316,477 committed vs 316,451 mine. The ERC-725xy execute note differs (setValue 335865 vs 662189). Random keys change the number of zero bytes in calldata. `npx hardhat test` also rewrites tracked files (L1-asymmetry.*, attack_results.json). | Say "deterministic up to calldata zero-byte count with random keys", or seed the keys.**

**F12 | medium | 1_blockchain-identity/scripts/security_scenarios.js:55-70; 4_comparison-framework/security-analysis/README.md:43-49 | The on-chain attack script that feeds `security_matrix.json` ("DEFENDED only if the malicious tx actually reverted") | `expectRevert` accepts any EVM revert and records the reason without asserting it. The strict Hardhat harness names a reason in 51 of its 52 `attempt` calls. Guard-removal flips on the script: removing the guard in EthereumDIDRegistry, ERC-725 `addKey` and the ERC-4337 account produced VULNERABLE cells. The ERC-721 mint-role mutant made the script crash (rc 1), so it fails closed. The leniency is real but could not be shown to hide a defect. | State that "43/43" refers only to the strict Hardhat test.**

**F13 | low | cv2x-testbed/identity/mobi_vid_provider.py:659 and :703 | One `_registered_key_for` | It is defined twice in the same class. The first copy (l.659, with the stale docstring "MOBIVIDRegistry anchors no signing key on-chain") is dead code overridden by the second. | Delete the first.**

**F14 | low | README.md:101; docs/MEASUREMENT_CONDITIONS.md:91 | "CI floor 93.0%" (README); row #4 says "the CI floor is 93.0 %" next to "floor 94.0" | `.github/workflows/w3c-compliance.yml` sets COMPLIANCE_FLOOR to 94.0. | Fix both.**

**F15 | low | sandbox/grand/report/demos.md (totals line); sandbox/options/*/demos/_lib.js | "92 demos / 1,752 steps / 62 flagged" | The arithmetic is correct (92 rows, 1752, 62, 0 failures). The steps break down as 1,052 mined transactions (assertion: mined), 229 reverts with a reason match, and 471 views/off-chain. At least 137 `d.offchain(...)` notes assert nothing. "Flagged" is a text note, not a failure. | Report assertions, not steps.**

**F16 | low | 1_blockchain-identity/scripts/benchmark_gas.js:213, :265, :441; docs/thesis/chapter7-conclusion/README.md:229 | "Event-log designs are an order of magnitude cheaper"; create spread 33.7x | For ERC-725, ERC-725xy and ERC-735, "create" is the full bytecode deployment of a per-vehicle contract. For the registry standards it is one entry, and `deployRegistry` (958k-4.2M) is excluded. No shared-bytecode or clone variant is measured, so the ranking and "ERC-735 heaviest" depend on that definition. The per-operation notes disclose it; chapter 7 does not. A flip under a clone-based definition is expected but not run (unconfirmed). | Add the definition caveat to chapter 7, or measure a clone variant.**

### Checked and found sound

- **C1:** Hardhat 536 passing / 23 pending, matching the claim. The 23 pending are all adapter-capability skips in `adapters.conformance.test.js` ("declared n/a"); none is the sole coverage of a registered security claim. Python with a node: 358 passed, 0 skipped. `run.sh`: 291 passed, matching the grand report.
- **C3:** 51 of 55 mutants killed. Survivors are in F3.
  - **Verifier and issuer:** signature, expiry, not-yet-valid, issuer allow-list, revocation, registry-issuer binding, proof type, cryptosuite, verificationMethod binding, proofPurpose, chain check, disclosure digest, holder binding, high-s, v in {0,1}.
  - **Freshness and providers:** window direction, future bound, replay insert and check, NaN timestamp, D11 (embedded key), embedded-key mismatch, local and on-chain revoked, ERC-1056 revoked / chain-bind / validTo / newest-key / freshness / accept.
  - **Resolver, MOBI and cipher:** D4 placeholder key, resolver omit-controller / hex chain id / wrong chain id (D27), VIN cipher (constant nonce, AAD, HKDF salt, unsalted hash), attestation digest (chain id, vehicle), odometer `<=`.
  - Two survivors are equivalent mutants and not findings: the naive-datetime regex (the tz check is redundant) and the freshness `>=` boundary. The D5 mutant was inconclusive (setup error).
- **C5 (a)-(d):** the registration diff only adds require lines; the suite commit 939b31d is pinned; the control run is 347/347 on the same harness; regenerated implementation files equal the committed ones; the resolver is unchanged since bd90004. The one failure is as documented. Scope limits are in F6.
- **C7:** 15 negative PoCs on the real VC code: tampered subject, swapped issuer, expired, not-yet-valid, revoked, wrong proof type, wrong cryptosuite, proofPurpose edit, created edit, stripped credentialStatus (also on a revoked VC), replaced @context, and VP challenge/domain edits. None was accepted. VP replay under the same challenge succeeds when no NonceStore is configured (documented as optional, S-6).
- **C8:** the PKI and centralized baselines verify a CA signature (`verify_directly_issued_by`) plus validity window and CRL. The lookups are in-memory. Row #21 labels the in-process PKI a lower bound.
- **C9:** fix mutants killed by a named regression test: D1, D6, D9, D10, D13, D18, D21 (three variants), D25a, D25b, D8 orphan guard, K-2, K-3, K-4, K-8, K-11. The fixes of both lineages are present in the code. D7, D11b and the D22/M-A semantics were not mutated. D2 is covered only by demos (F3).
- **C11/C13:**
  - All 22 guard-removal and nonce mutants were killed by the Hardhat suite: 1056 onlyOwner, 721 mint, 725 addKey, 735 onlyOwner, 4337 setAttribute, LSP8 onlyOwner, MOBI manufacturer, Combined owner, nonce increment.
  - A sweep for unguarded state-changing functions found nothing exploitable apart from F9.
  - `tx.origin` and `selfdestruct` do not appear.
  - Compiler warnings: 12, all unused parameter / shadowing / could-be-pure, none security-relevant.
  - Slither and Mythril are not installed.
- **C12:** the largest deployed bytecode is 16,878 bytes (MOBIVIDRegistryV2), so nothing exceeds EIP-170's 24,576. Optimizer 200 + viaIR + cancun is confirmed in `hardhat.config.js`. The three cv2x-testbed MOBI contracts are byte-identical to the 1_blockchain-identity copies.
- **C15:** the re-run of `benchmark_gas.js` differs from the committed `gas_benchmark.json` in metadata only, so all gas cells match. Create semantics are in F16.
- **C16:** AES-256-GCM with a random 12-byte nonce (the same VIN encrypted twice gives different ciphertext), HKDF with the VIN salt, vinHash as AAD, per-issuance salt. No misuse found.
- **C17:** the arithmetic 92 / 1,752 / 62 is correct. ABI coverage counts match the READMEs exactly (LSP8 21, NFT 44, ERC721 20, MOBI-V2 57, ERC-1155 34).
- **C18:** the testbed and MOBI contracts do not diverge (three files byte-identical, including the CI-checked ones). The testbed VC module is a shim over the canonical layer.

### Not checked (and why)

- **C2:** I did not do the twenty-test reading or the "output compared with the same function" table. I used mutation instead, because my `ast` heuristic over-counted `assert not x` as weak.
- **C6:** `did_resolver.py` read and latency re-timed; D27 fixed in code (a decimal-chain-id test kills the mutant). Not every register or chapter sentence about resolution was enumerated.
- **C10:**
  - Executed PoCs: D15, D23, D26 and the zero identity.
  - Source-confirmed only: D8-rest, D12-rest, D16-rest, D24. D24 is already shown in an existing demo.
  - Not executed: D19 and D20. My D20 PoC failed on constructor arguments.
- **C14:** the second L1 diff used the committed file as run 1. The counts of `.to.emit` without args (38 on a single line) and of gas-pin tests (1) are approximate.
- **C19, C20:** only partly checked, with no full pointer resolution for each threat or property. Threats absent from the model: front-running/squatting by an authorized manufacturer, issuer-key compromise, owner-key loss without recovery (partly in G6).
- **C5:** Jest was not re-run (network and install).
- **C8:** hidden asymmetry in rows #27, #32, #37 and #39 not analysed in depth. The C15 alternative-definition ranking flip was not run. D5, D7 and D11b mutants were not run.
- **Outside scope, noticed:**
  - Running `npx hardhat test` rewrites tracked report files (tooling brief).
  - The WM-1 report cites 291 Python layers while the CI job skips 27 (briefs 3/4).
- **Report file:** the harness refused my write to `REPORT_brief_5.md` (subagents return findings as text), so this message is the only copy.
- **Cleanup:** the Hardhat nodes I started (18548, 18549) are stopped. The frozen checkout was not modified.
