# Review 02 — Codebase Review (2026-10-03)

**Tree reviewed:** merge commit `434669d` (trunk `3203ee8` + data-collection lineage `441791b`)
**Baseline on that tree:** 242 Hardhat passing / 4 pending · 60 Python passed · checker 93.2 %
**Method:** five independent read-only lenses run in parallel:
contracts · measurement harness · SSI/VC layer · cv2x testbed · CI, tests and claims.
Each finding was checked against the code. Findings marked **[PoC]** were reproduced:
on-chain through the Hardhat console, or with a throwaway script that shows the wrong
outcome. A full metrics re-run on the merged tree (`2026-10-03T22-36-47Z_434669d`) was
compared cell-by-cell with the committed run of record.

**Severity scale.**
- **Critical:** a security check that passes when it must fail, *and* the thesis relies on it.
- **High:** a confirmed bypass or broken function, or a bug that changes a cited number
  or ranking.
- **Medium:** a measurement or definition error that does not change a ranking; a
  doc–code contradiction an examiner would find.
- **Low:** hygiene.

**Prior review.** The requested branch `review-codebase-011CUp…` is not recoverable
(`HANDOFF_2026-10-03_REVIEW2.md` §1). This review supersedes nothing in `AUDIT_01`,
`RESEARCH_AUDIT` or `REVIEW_CV2X_TESTBED_LINEAGE`; it is a code-level review, and those are
claims- and methodology-level reviews.

---

## 0. Executive summary

1. **The headline PKI-vs-ERC-1056 experiment (register #21) is biased, in both directions
   at once, in favour of PKI.**
   - The PKI verifier never checks the CA signature on the certificate (T-1, **[PoC]**:
     a forged certificate is accepted). That leaves out the second ECDSA verify, about
     1.7× its cost.
   - The ERC-1056 verifier makes a redundant `isRevoked` RPC, about 38 % of the cited
     18.2 ms (T-5).
   - The ordering will not flip, but the ratio will shrink and #21 must be re-run before a
     chapter cites it.
2. **Revocation does not reliably revoke.**
   - Two independent ERC-1056 resolvers bring back revoked keys or delegates (T-2 **[PoC]**,
     H-4).
   - The VC verifier passes revoked credentials whenever no registry, or the wrong one,
     is configured, and every MOBI and SUMO call site is in that state (S-2 **[PoC]**).
   - An ERC-735 claim the issuer revoked can be re-added by the holder (K-2 **[PoC]**).
3. **Presentations are not bound to the credential subject** (S-1, **[PoC]**). A stolen
   credential can be presented under the thief's own DID. The test meant to cover this
   tests a weaker attack.
4. **MOBI VID registry access-control holes** (K-3, K-4, **[PoC]**):
   - the public `changeOwner` bypasses the ownership-history record and the revocation
     state;
   - an authorised manufacturer can take over an existing DID through
     `registerVehicleBirth`.
5. **Harness numbers are mostly right, with one artifact and several mis-transcriptions.**
   - **Artifact:** ERC-725 V5 = 214,099 depends on N (71,243 at N = 5; H-1). It comes from
     the issuer's key array growing as N rises.
   - **Lifecycle ratio:** 2.7× becomes about 2.6× once the omitted delegate-add is
     counted (H-2).
   - **HANDOFF figures that don't match the run:** five figures in the HANDOFF don't
     match the run it cites (H-6).
   - **Determinism:** gas is not byte-for-byte deterministic. Random wallets change
     calldata zero-bytes by 12–25 gas per cell (H-3).
   - **What doesn't move:** no ranking changes.
6. **CI does not test what the handback says it tests.**
   - The benchmark workflow only triggers on `main`, which does not exist (Q-1).
   - The 32 MOBI-VID Python tests never run in CI (Q-2).
7. **The claims surface has drifted.**
   - The README marks H1 "Supported (~10×)". The newest data in the repo say ≈2.6–3.0×
     on lifetime cost.
   - Test counts disagree in five places.
   - Register rows #5, #9 and #16–#19 were overtaken by the merge (Q-3–Q-5).

The signature mathematics, the VIN cipher (AES-256-GCM, HKDF, AD-bound), the harness's
statistics core (percentiles, bootstrap, rank/tie maths), calldata and CREATE gas
accounting, the nine-standard gas determinism (55/55 cells reproduce) and the 93.2 %
formula itself all hold up.

---

## 1. Findings

### K — Contracts (`1_blockchain-identity/contracts/**`)

| ID | Sev | Where | Defect | Failure scenario |
|---|---|---|---|---|
| K-1 | High **[PoC]** | `ERC1056/CVINVehicleDIDRegistry.sol:197-207` | `setVehicleAttributes` passes `validity = type(uint256).max`, so `block.timestamp + validity` overflows; it also requires `msg.sender == did` before that | Always reverts (`unauthorized`, or panic 0x11 once the wrapper owns the DID). Untested; the harness works around it with 8 single calls |
| K-2 | High **[PoC]** | `ERC735/CVINVehicleClaimHolder.sol:129-137`; `CVINCombined/CVINCombinedIdentity.sol:153-158,245` | Issuer signature covers `(holder, topic, data)` only; no revocation record, nonce or expiry | Issuer removes a "failed inspection" claim; the owner calls `addClaim` with the old signature and the claim is back |
| K-3 | High **[PoC]** | `MOBI/ERC1056Registry.sol:90-102,147-170,243-249`; `MOBIVIDRegistry.sol:198-231` | Public `changeOwner` / `revokeDelegate` / `revokeAttribute` ignore `revoked[]`; `changeOwner` skips `ownershipHistory` | An owner transfers without an odometer or authority record; a revoked VID is re-assigned |
| K-4 | High **[PoC]** | `MOBI/MOBIVIDRegistry.sol:141-171` | `registerVehicleBirth` overwrites `owners[vehicleIdentity]` with no check | An authorised manufacturer takes over any existing `did:ethr`, or re-births a revoked VID |
| K-5 | Med | `MOBI/ERC1056Registry.sol` (also `cv2x-testbed/contracts/`) | Not ERC-1056: no delegates or `*Signed` functions; revocation sets `validTo = now`; `DIDRevoked` advances `changed[]` with no `previousChange`, cutting the event chain | The cv2x "ERC-1056" columns (#21, #22) measure a different registry from `EthereumDIDRegistry`. **Must be stated wherever #21/#22 are cited** |
| K-6 | Med | `CVINCombined/CVINCombinedIdentity.sol:49-64,174,196` | Claim events advance `changed[]` with no `previousChange` | A resolver walking `changed` stops at a claim block and loses earlier history |
| K-7 | Med **[PoC]** | `ERC1056/CVINVehicleDIDRegistry.sol:157-161,244-266` | `updateOwnershipMapping` is permissionless; the DID is the owner's EOA, so a second vehicle overwrites `didToVIN` | Anyone re-points a VIN at the wrapper contract; the DID document is orphaned |
| K-8 | Med **[PoC]** | `LSP8/CVINVehicleLSP8.sol:135-147,161-167` | `revokeVehicle` leaves `_tokenIdData`; tokenId = keccak(VIN) | Re-minting the same VIN returns the old inspection data |
| K-9 | Med | `ERC725/CVIN_DID_ERC725.sol:59-88` | `execute`/`approve` are no-ops; `addKey` pushes duplicates; `removeKey` is O(n). It is really an ERC-734 key manager | The "ERC-725" baseline is weaker and cheaper on some operations, dearer on others (see H-1) |
| K-10 | Med | ERC-721 / 735 / LSP8 / 4337 / MOBI | Gas bias unrelated to the standard: VIN stored 3× and a history push on every transfer (ERC-721); duplicate events (ERC-735, LSP8); minimal EntryPoint without prefund accounting (understates 4337) | Cross-standard ratios carry implementation choices. Document them in the chapter's threats to validity |
| K-11 | Low **[PoC]** | `CVINCombined/CVINCombinedIdentity.sol:225-233` | `hasValidClaim` is true for an empty slot | `hasValidClaim(id, 0, 0x0) == true` |
| K-12 | Low | `ERC1056/EthereumDIDRegistry.sol` | Upstream behaviour: no chainId in the signed digest; `ecrecover → 0` accepted for a zero-owner identity | Faithful to ethr-did-registry; the chapter should say so. **Not changed** (fidelity to the standard is the point) |
| K-13 | Low | `ERC1155/CVINVehicleCredential1155.sol:82-97` | BIRTH_CERT transfer to a holder that already has one overwrites `vehicleVIN[to]` | The other vehicle's VIN is orphaned |
| K-14 | Low | `ERC4337/CVINMinimalEntryPoint.sol`, `CVINVehicleAccount.sol:139-145` | Nonce rolled back when execution reverts; guardian recovery doesn't emit `OwnershipTransferred` | A failed op can be replayed; indexers miss recovery |
| K-15 | Low | `MOBIVIDRegistry.getVehicleDID`; V2 `OWNER` role | Malformed `did:ethr:0x7a69:<no 0x>`; the global OWNER role can file theft or accident reports against any vehicle | |
| K-16 | Low | `ERC721/contracts/*`, `ERC721/test/*`, `ERC725/contracts/*` | Dead, drifted copies (one still has the `_balances[to] += tokenId` bug); not compiled | Someone cites the wrong copy |

### H — Measurement harness (`1_blockchain-identity/benchmarks/**`, gas scripts)

| ID | Sev | Where | Defect | Effect on reported numbers |
|---|---|---|---|---|
| H-1 | High | `scenarios/crud.js:54-60`, `adapters/erc725.adapter.js:108-121` | V1/V3/V5 share one issuer contract across iterations; ERC-725 `removeKey` is O(keys) | ERC-725 V5 214,099 at N=30 vs 71,243 at N=5 vs 49,218 in lifecycle; the "6.4×" gap is really ≈1.5–2.1×. ERC-1056 V6 read bytes also depend on N |
| H-2 | Med | `scenarios/lifecycle.js:22-24,41-43`; `adapters/erc721.adapter.js:103-106` | The `addDelegate(k1)` that event 11 revokes is an unmeasured precondition; ERC-721 "rotate" = approve(k2) then approve(0) | Lifetime ratio 2.7× → ≈2.6× (ERC-725 3.0× unchanged); ranking unchanged |
| H-3 | Med | `scenarios/common.js:27,32` | `Wallet.createRandom()`: addresses differ per run, so calldata zero-byte counts differ | Re-run moved ERC-721 U1 179,482→179,470, U4 182,399→182,374 and batch cells ±12–36. "Reproduce byte-for-byte" is not true |
| H-4 | Med **[PoC]** | `adapters/erc1056.adapter.js:109-116` | Resolver keeps revoked delegates (`validTo=0` events skipped, not applied); reverse order within a block; expired attributes kept | R3 "full DID document" is wrong after a revocation. RPC counts and bytes are unaffected |
| H-5 | Med | `lib/stats.js:87-92` | `normalCdf` mixes two erf approximations: Φ(1.96)=0.981 | Mann–Whitney p too small. **Latent**: no scenario calls it yet |
| H-6 | Med | `HANDOFF-DATA-COLLECTION-FRAMEWORK.md` §3 | Throughput (152–164 tx/s; JSON 131–151), R3 medians (15.3/6.9/14.1; JSON 18.4/6.4/12.8), "13/16 events" (JSON 12/16), D3 minimum mis-attributed | Text ≠ run of record |
| H-7 | Med | `scenarios/resolve.js` | `R4_verify_delegate` queries a key that was never delegated | Row measures the negative path; mislabelled |
| H-8 | Med | `lifecycle.js:60`, `report.js:104` | "New storage slots left behind" is the sum of zero→nonzero writes, not net state | ERC-725 79 → ≈74–75 net; label wrong, ranking unchanged |
| H-9 | Low | `MetricsCollector.js:184,305-326` | `gasExecution` is net of refunds; reported gas = mode over iterations, but slot and log counts come from iteration 0 | Definitions in `MEASUREMENT_CONDITIONS.md` §5.B incomplete |
| H-10 | Low | `meta.json`, §5.A | Hardhat 2.29 executes **Osaka** (compile target cancun); docs say block gas 30M (meta 60M), 1,000 VINs (dataset 1,100), warm-ups 3 vs 5 | Conditions block inaccurate |
| H-11 | Low | adapters | Some timed `fn`s include extra reads or deployment polling | Small latency inflation (ERC-1056 U5, ERC-721 C1, ERC-725 C1) |
| H-12 | Low | `run_gas_stats.py:99`; `benchmark_scaling.js:~380` | [min,max] labelled `ci95`; lifetime model uses option (a) and the stale 52,612 | Labels; ranking unaffected |

### S — SSI / VC layer (`2_w3c-ssi-layer/**`)

| ID | Sev | Where | Defect | Failure scenario |
|---|---|---|---|---|
| S-1 | **Critical** **[PoC]** | `vc_verifier.py:297-363` | No check that `vp.holder == credentialSubject.id` | A thief presents the victim's credential under the thief's own DID → `valid=True` |
| S-2 | High **[PoC]** | `vc_verifier.py:218-236` | Status declared but no registry, so it passes with a warning; the lookup ignores `credentialStatus.statusListCredential` | Revoked credential: correct registry → False; no registry → **True**; unrelated registry → **True**. Every MOBI and SUMO verifier is built without a registry |
| S-3 | Med | `vc_verifier.py:86-107,238-268` | Key binding = "address in the DID"; DID never resolved; chain id ignored; `verificationMethod` unchecked | Rotated or compromised keys stay valid; `did:ethr:0x1:A` ≡ `did:ethr:0x7a69:A` |
| S-4 | Med **[PoC]** | `vc_verifier.py:206-216` | `validFrom`/`validUntil` compared as strings; `expirationDate` (VC 1.1) ignored | `validUntil` "+12:00" already in the past, "never", and a 2001 `expirationDate` are all accepted |
| S-5 | Med **[PoC]** | `vc_verifier.py:238-268` | `proof.type`, `cryptosuite`, `proofPurpose` not validated | `type:"Bogus"`, `cryptosuite:"none"`, `proofPurpose:"authentication"` verify |
| S-6 | Med **[PoC]** | `vc_verifier.py:318-322` | Challenge and domain optional; no nonce store; `created` not bounded | A presentation with no challenge verifies when the caller passes `None` |
| S-7 | Low **[PoC]** | `vc_issuer.py:297-305` | High-s and v∈{0,1} accepted (malleable) | Two valid encodings per proof |
| S-8 | Low | `vc_issuer.py:47-54` | `json.dumps` canonicalisation, not JCS/RDFC | Proofs are not interoperable; qualify the "VC DM 2.0 conformant" claim |
| S-9 | Low | `vc_verifier.py:182,286` | Malformed `disclosedClaims` raise `KeyError` | A holder can crash the verifier (fails closed) |
| S-10 | Med **[PoC]** | `did_resolver.py:202-207,233-234,265,218` | Cache never expires and returns the mutable cached object; unknown methods → `internalError` (the `methodNotSupported` branch is dead); no identifier validation; CAIP-10 chain id in hex | Mutating one result poisons later resolutions; `did:ethr:not-an-address` resolves |

### T — cv2x testbed (`cv2x-testbed/**`)

| ID | Sev | Where | Defect | Failure scenario / effect |
|---|---|---|---|---|
| T-1 | **Critical** **[PoC]** | `identity/standard/pki_identity.py:177-228`; `identity/centralized_provider.py:304-359` | Certificate signature never verified against the CA (centralized checks the issuer *name* only) | A self-signed certificate signs a forged hard-brake message → accepted. #21 PKI verify omits about 1.7× its cost; the `.md` says "issuer name check" |
| T-2 | **Critical** **[PoC]** | `identity/erc1056_provider.py:656-677` | Backward walk skips a revocation event (`validTo = now`) and returns the older, still-"valid" key | A key revoked by its owner still verifies messages |
| T-3 | High **[PoC]** | `identity/w3c_verifiable_credentials.py:132,155`; `vc_verifier.py:255-258` | Every issuer *and wallet* self-registers in `SHARED_TRUSTED_ISSUERS`; `did:ethr` issuers are not allow-listed | A vehicle issues itself a `V2VSafetyCredential`; SUMO's SSI layer accepts it, contradicting its "trusted-issuer check" docstring |
| T-4 | High **[PoC]** | `identity/mobi_vid_provider.py:540-608` | Verify trusts `signed_message['public_key']`; `revoke_credential` ignores `receipt.status` | Any unregistered key verifies; a failed revocation reports success |
| T-5 | High | `identity/erc1056_provider.py:426-436` | Redundant `isRevoked` eth_call (`getIdentityInfo` already returns it) | #21 ERC-1056 verify 16.6 ms / 7 RPCs → 10.3 ms / 4 RPCs (measured) |
| T-6 | Med | `scripts/experiment_pki_vs_erc1056.py:207-216` | RPC count snapshotted after the untimed post-check | Revoke reported as 8 RPCs; really 5–6 |
| T-7 | Med | `w3c_compliance_checker.py:207-240` | Malformed-DID checks PASS on any error; the unsupported-method check is PARTIAL for the same wrong code | Applied consistently: 93.2 % → **90.9 %**. CI gate floor is 93.0 %, so this is an **author decision** |
| T-8 | Med | `did_resolver.py:270-310` | DID Core checks test a synthesised template (`created = now()`; nothing queried) | "DID Core 13/15" measures document shape only; label accordingly |
| T-9 | Med **[PoC]** | PKI, ERC-1056, centralized and SUMO providers; `protocols/cv2x_stack.py:513-532` | Timestamp unsigned or unchecked; no de-duplication; `success=True` on invalid messages | Replay of any packet verifies; the scenario counts failures as successes |
| T-10 | Med | `identity/erc1056_provider.py:626-679` | Only the custom `veriKey` attribute is accepted; owner and delegate semantics are not implemented; latest state used, not state at signing | Fails closed. "ERC-1056 verify" ≠ "owner or valid delegate" |
| T-11 | Med | `identity/erc1056_provider.py:181-189` | Controller key = sha256(vehicle_id) | Anyone can derive any vehicle's key. Test-only; must be labelled |
| T-12 | Low | various | CWD-relative ABI path with an eventless fallback; run of record `git_dirty: True`; secp256k1-vs-P-256 sign cost caveat incomplete; `comparison_framework.py` ignores verify results; `ca=None` | |

### Q — CI, tests, claims (`.github/`, tests, top-level docs)

| ID | Sev | Where | Defect | Consequence |
|---|---|---|---|---|
| Q-1 | High | `.github/workflows/benchmark.yml:15-21` | Push trigger is `main` only (no `main` exists) | The harness, nine-standard gate and gas report never run on push |
| Q-2 | High | `.github/workflows/w3c-compliance.yml:45` | Only `test_vc_layer.py` runs; MOBI-VID tests skip when artifacts are missing | 32 of 60 Python tests are local-only; a skip would read as green |
| Q-3 | High | `README.md:35,141,168` vs HANDOFF §0 | H1 "Supported ~10×" vs "refuted as stated, 2.7×/3.0× lifetime"; harness lineage absent from README/INDEX/HANDBACK | An examiner sees a verdict the repo's own data contradict. Restatement is an **author decision** (framing) |
| Q-4 | High | README:130 vs `crud_gas.md` | ERC-1056 create 52,594 (`benchmark_gas.js`) vs 76,786 (harness C1) without definitions side by side | Two figures for "the same thing" |
| Q-5 | Med | HANDBACK, README, register #5, workflow headers | Test counts 47 / 217 / 219 / 242; "68 security scenarios" (54 exist: 43 executable + 11 N/A); register "#1–#28" (now #31) | Inconsistent claims |
| Q-6 | Med | `MEASUREMENT_CONDITIONS.md` | #16–#19 B vs #25–#28 V for the same claims; #9 "ERC-725 untested" (it is tested); #25 quotes July values; #26 vs #30 lifetime definitions | Register contradicts itself |
| Q-7 | Med | `README.md:123` | "All numbers measured", but V2V 0.165 ms and scaling are register status B | |
| Q-8 | Med | `test/security/attackHarness.js:83-93` | Any thrown error = DEFENDED; no revert reason asserted; ERC-725 cells "couldn't infer reason" | "43/43 defended" would survive a regression that fails for another reason |
| Q-9 | Med | `cv2x-testbed/artifacts/**` tracked | Pre-fix vulnerable `MOBIVIDRegistryV2` bytecode committed; root `.gitignore` lacks `artifacts/` | A deploy from the testbed uses the bytecode without the fix |
| Q-10 | Med | `1_blockchain-identity/package.json:8-21` | 8 of 9 `test:<std>` scripts and `deploy`/`deploy:all` point at missing paths | Documented commands fail |
| Q-11 | Low | README:141, CAPABILITIES | ERC-4337 overhead +46,862 (cancun run: 46,830) | Stale |
| Q-12 | Low | `benchmark.yml:119` | Determinism gate ignores a cell that disappears | A dropped measurement passes |
| Q-13 | Low | `adapters.conformance.test.js:33,55,60,81` | D2, U5, D3 execute without checking post-state; R2 only checks non-zero | Gate weaker than claimed. The 4 pending are legitimate |
| Q-14 | Low | `MOBIVIDRegistry.test.js:398`; `test/ERC721/*` | Bare `.to.be.reverted`; no `onlyOwner mint` negative | |

---

## 2. Effect on the claim register

| Row | Effect | Action |
|---|---|---|
| #4 (93.2 %) | T-7: consistent scoring gives 90.9 %; T-8: DID Core checks are structural | Author decides: tighten the checker and re-baseline the CI gate, or footnote. Session will not move the gate unilaterally |
| #21 (PKI vs ERC-1056) | T-1, T-5, T-6, K-5 | **Re-run** after the fixes; keep the old row as S with the reason |
| #22 | K-5 (not `EthereumDIDRegistry`) | Add the caveat |
| #24 (external 328/441) | S-10: a further cause beyond R1–R5 (unknown method → `internalError`) | Add to the conformance doc |
| #29 | H-1, H-3 | Re-run with a fresh issuer per op and deterministic wallets |
| #30 | H-2, H-8 | Re-run; restate 2.7× → measured value; rename the slot metric |
| #31 | H-4, H-7 | Re-run with the corrected resolver |
| #5, #9, #16–#19 | Q-6 | Mark S (superseded by #25–#28 on the merged trunk) |

## 3. Decisions this review surfaces for the author
1. **T-7 / #4.** Tighten the checker, so the score reads ≈90.9 % and the gate floor
   moves, or keep 93.2 % with a footnote.
2. **Q-3 / H1.** Restate H1 as "≥10× on create-identity (definition b: 6.9×); ≈2.6×–3.0×
   on lifetime cost". The handback recommends this; it is a framing change.
3. **K-12.** Keep `EthereumDIDRegistry` byte-faithful to upstream (recommended) and document
   its weaknesses, or harden it, which would change the "ERC-1056" being measured.
4. **K-5.** Rebuild the cv2x registry on `EthereumDIDRegistry` so #21/#22 measure the same
   ERC-1056 as #25/#29, or keep it and caveat. This changes a results-of-record experiment.
