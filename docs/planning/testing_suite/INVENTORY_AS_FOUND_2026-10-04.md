# Testing and Results Inventory — As Found (2026-10-04, HEAD `fa6188e`)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Purpose:** the raw, per-layer survey behind `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` §6–§7. Three read-only surveys (one per layer), consolidated and lightly edited. Nothing was executed; counts are static (`it()` / `def test_` / parametrize decorators) unless a CI total is quoted. This file is the Phase 1 starting point for the Test Case Register and is superseded by the generated registers once they exist.

Paths are relative to the repository root.

---

## Part I — `1_blockchain-identity/`

### I.1 Test files (18 files; 293 static `it()`; ≈392 at runtime because the conformance file expands ×10)

| File | `it` | `expect` | revert asserts | Categories |
|---|---|---|---|---|
| `test/CVINCombined/CVINCombinedIdentity.test.js` | 30 | 64 | 15 | functional (owner, attributes, delegates, claims); security regressions K-2, K-6, K-11, high-s malleability; 1 gas test |
| `test/ERC1056/CVINVehicleDIDRegistry.test.js` | 24 | 34 | 14 | manufacturer authorisation, create, VIN map, K-1 `setVehicleAttributes`, transfer, endpoint, delegates, queries |
| `test/ERC1056/EthereumDIDRegistry.test.js` | 19 | 26 | 3 | owner, delegates, attributes, `changed`; signed-nonce; 3 gas tests with loose `lt(100000)`/`lt(80000)` bounds |
| `test/ERC1056/PseudonymPool.test.js` | 8 | 23 | 0 | experiment check; **pins exact gas** (`71919`, `[1113456,1096368,1096368]`) and linkability; imports `scripts/experiment_pseudonym_pool.js` |
| `test/ERC1155/CVINVehicleCredential1155.test.js` | 18 | 48 | 12 | functional + negative authorisation, soulbound, K-13 |
| `test/ERC4337/CVINVehicleAccount.test.js` | 16 | 31 | 10 | UserOp, nonce replay, execute, attributes, key rotation, guardian recovery; 1 gas comparison direct vs EntryPoint |
| `test/ERC721/combined.js` | 7 | 11 | 3 | Regular vs Monolithic ERC-721; ERC-2981 |
| `test/ERC721/identityBased.js` | 1 | 2 | 0 | toll demo; no negatives |
| `test/ERC721/regularExtended.js` | 4 | 4 | 0 | `tokenURI.includes("Toyota")`; no negatives |
| `test/ERC725xy/CVINVehicleERC725XY.test.js` | 15 | 37 | 18 | 725Y data, batch, birth attrs, 725X execute (real side effect), rotation |
| `test/ERC735/CVINVehicleClaimHolder.test.js` | 23 | 58 | 15 | add/update/remove claim, tamper, unsupported scheme, K-2, ownership transfer |
| `test/LSP8/CVINVehicleLSP8.test.js` | 19 | 53 | 13 | mint, per-token data, transfer (force), burn, K-8, authority transfer |
| `test/MOBIVID/MOBIVIDRegistry.test.js` | 32 | 92 | 37 | V1 birth, VIN-hash lookup, transfer, K-3/K-4/K-15, V2 events, roles, attestation signatures, history |
| `test/MOBIVID/attestEventRegression.test.js` | 2 | 9 | 3 | M3 regression; **pins `169_295` execution gas** |
| `test/benchmarks/adapters.conformance.test.js` | 11 ×10 | 29 | 0 | harness gate; 23 `this.skip()` = declared n/a |
| `test/benchmarks/stats.test.js` | 4 | 13 | 0 | `normalCdf`, Mann–Whitney U, percentile |
| `test/security/attackHarness.js` | — | — | — | library: DEFENDED / VULNERABLE / UNEXPECTED-REVERT / FAILED-TO-RUN / N/A |
| `test/security/securityScenarios.test.js` | 60 | 119 | 55 | 6 self-checks + 9 standards × 6 attacks with differential control; 13 N/A cells without assertion; `after()` writes to `4_comparison-framework/security-analysis/results/` |

Security matrix standards: ERC-1056, ERC-721, ERC-725, ERC-735, ERC-1155, ERC-4337, LSP8, MOBI-VID-V2, CVIN-Combined. **ERC-725xy absent.**

### I.2 Adapter harness

- Base `benchmarks/adapters/IdentityAdapter.js`; `this.unsupported[opId] = reason` → `n/a`.
- Registered adapters (10): `erc1056, erc1056w, erc721, erc725, erc735, erc1155, erc725xy, lsp8, erc4337, cvin`. **MOBI-VID has no adapter.**
- Catalogue `benchmarks/lib/operations.js`: 18 ops (C1, C2, R1–R4, U1–U5, D1–D3, V1, V3, V5, V6). No V2/V4. `rotateDelegate` is a helper.
- Conformance sequence per adapter: reset → C1/C2 → R2 → U2/R4/D1 → rotateDelegate → U3/R3 → D2 → U5 → V1/V3/V6/V5 → V with separate issuer → U1/U4 → D3 + post-state check.

Adapter × op realisation (N native primitive · E emulated/mapped · – declared n/a):

| Op | erc1056 | erc1056w | erc721 | erc725 | erc735 | erc1155 | erc725xy | lsp8 | erc4337 | cvin |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | E wrapper `createVehicleDID` | E (+`changeOwner`→wrapper) | N `mintVehicle` | E deploy+`addKey` | N deploy | N `registerVehicle` | E deploy+`setData` | N `mintVehicle` | E deploy+`setAttribute` | E manufacturer VIN claim |
| C2 | E 9 tx | N `setVehicleAttributes` 3 tx | N (subset of attrs) | E 9 × `addKey` | E +claim | E = C1 (attrs off-chain) | N `setDataBatch` | N `setDataBatchForTokenIds` | E 9 tx | E +claim |
| R1 | N | N | N | N | N | E `isRegistered` | N | N | N | N |
| R2 | E wrapper | E | N | – (off-chain map) | – | N | – | E keccak+`exists` | – | – |
| R3 | E event replay | E | E | E | E log enumeration | E | E | E | E | E `changed` chain + claim logs |
| R4 | N `validDelegate` | N | E owner/`getApproved` | E `getKey` | – | – | – | – | E guardian==key | N |
| U1 | N | N | N `transferFrom` | N | N | E re-bind × (1+types) | N | N `transfer(force)` | N | N |
| U2 | N | N | E `approve` (no TTL) | E `addKey` (no TTL) | – | – | – | – | E `setGuardian` | N |
| U3 | N | E `setServiceEndpoint` | E `addServiceRecord` | E `addKey(hash)` | E self-signed claim | E badge (payload not stored) | N `setData` | E authority writes | N | N |
| U4 | = U1 | = U1 | N `safeTransferFrom` | = U1 | = U1 | = U1 | = U1 | = U1 | = U1 | = U1 |
| U5 | N `setAttributeSigned` | – | – | – | – | – | – | – | N `handleOp` | – |
| D1 | N | N | E `approve(0)` | N `removeKey` | – | – | – | – | E `setGuardian(0)` | N |
| D2 | N | – | – (append-only) | E `removeKey` | N `removeClaim` | E burn badge | E `setData(0x)` | E | E | N |
| D3 | E `did/deactivated` attr | E | N `deactivateVehicle` | E `renounceOwnership` | E owner→`0xdEaD` | E burn BIRTH_CERT | E `renounceOwnership` | N `revokeVehicle` | E owner→`0xdEaD` | E attr |
| V1 | E delegate on issuer DID | E | E issuer NFT | E `addKey` CLAIM | – | E `grantRole` | E issuer account | – | E | E |
| V3/V5/V6 | E attr/`revokeAttribute`/log scan | E | E strings + scan | E key STATUS | N claim ops | N `issueCredential`/burn/`hasCredential` | E issuer account | E authority data | E | N claim ops |

Not covered by the harness: recovery (4337 `recover`), a generic add-claim op, ERC-725X `execute`, MOBI-VID.

### I.3 Harness mechanics and outputs

- `run.js` (`npm run metrics`): env `METRICS_N` (30), `METRICS_WARMUP` (5), `METRICS_SCALE_N` (0,100,1000), `METRICS_SCALE_H` (1,10,50); bursts 10 senders × 20 tx × 3.
- Run id = ISO timestamp + short SHA → `results/metrics/runs/<id>/`, copied to `latest/`. `meta.measured` = git object hashes of `benchmarks/`, `contracts/`, `hardhat.config.js`, lockfile; `dirty`, `dirtyMeasured`.
- `repeatTx`: 1 exact + 5 warm-up + 30 samples, fresh precondition each; `gasUsed` reported as the **mode**, with `gasUsedRange` and `gasDeterministic`.
- Per-tx metrics via `debug_traceTransaction`: gas (used/intrinsic/execution), calldata bytes, logs, SSTORE/SLOAD, zero→nonzero SSTOREs, EVM steps, calls, depth; reads: RPC count, bytes, method mix.
- Scenarios: `crud` (L1), `lifecycle` (L2, 17 events, fleet apportionment 1/1k/1M), `scale` (L3), `batch` (L4, all sequential), `throughput` (L5), `resolve` (L6).
- `lib/dataset.js` mulberry32 seed 42, 1100 vehicles; `scenarios/common.js` deterministic fresh keys.
- `rubric/did-method-rubric.json`: scores for 3 of 10 substrates; all `reviewed:false`.
- Run of record `results/metrics/latest` = `2026-10-04T09-50-29Z_0eef6af` (clean; in-process). `results/metrics-rpc/latest` = `2026-10-04T22-09-23Z_c3b7cb1` (HTTP; `scaleN 0,100`; `dirty:true`, `dirtyMeasured:false`).
- **Verified 2026-10-04:** `HEAD:1_blockchain-identity/contracts` = `04c33c2…` ≠ `meta.measured.contractsTree` `6c58b31…` (commits `27a2184`, `d5320b2`, MOBI-only). **14 crud cells `gasDeterministic:false`**: cvin C1 [266945,266995], C2 [1006855,1006919], V3 [289738,289788], V5 [89962,89972]; erc721 C1 [397044,399844], U1 [176670,179470]; erc735 C2, U3, D2, V3, V5; lsp8 C1 [132515,149615], U1 [80612,83412], D2.

### I.4 Scripts (older nine-standard pipeline → `4_comparison-framework/results/`)

`benchmark_gas.js` (one exact sample per lifecycle op, nine standards + MOBI-VID-V2; CI diff gate) · `benchmark_scaling.js` (Exp. A/B) · `experiment_pseudonym_pool.js` (M5) · `mobi_vid_backend_sweep.js` (H4) · `security_scenarios.js` (lens 2 on-chain) · `validate_sepolia.js` (witness, 3 standards; never run) · `deployERC1056.js`.

### I.5 Contracts (solc 0.8.24)

ERC1056 `EthereumDIDRegistry`, `CVINVehicleDIDRegistry` · ERC721 `CVINVehicleNFT`, `CVIN_NFT_DID_ERC721`, `…_Monolithic` · ERC725 `CVIN_DID_ERC725` · ERC725xy `CVINVehicleERC725XY`, `CVINExecuteTarget` · ERC735 `CVINVehicleClaimHolder` · ERC1155 `CVINVehicleCredential1155` · ERC4337 `CVINVehicleAccount`, `CVINMinimalEntryPoint` (simplified) · LSP8 `CVINVehicleLSP8` (self-contained stand-in) · MOBI `ERC1056Registry` (second ERC-1056), `MOBIVIDRegistry`, `MOBIVIDRegistryV2` · CVINCombined `CVINCombinedIdentity`.

Config: compilers 0.8.24 (viaIR, cancun, runs 200), 0.8.20, 0.8.19, 0.8.0, 0.7.6; `chainId 31337`; `allowUnlimitedContractSize: true`; no hardfork pinned (executes osaka); mocha timeout 200 s. Unused deps: `@lukso/lsp-smart-contracts`, `ethr-did-resolver`.

### I.6 Reviewer-flag list (layer 1)

1. Deterministic-gas claim is run-to-run only; 14 cells vary iteration-to-iteration and the mode hides it.
2. `bootstrapMedianCI` and `mannWhitneyU` implemented, never called; throughput 3 bursts; scale reads 10 samples; lifecycle latency 1 sample.
3. Conformance is not an equivalence test (U1≡U4 in 9/10; ERC-1155 attribute probe; ERC-725 stores hash only; LSP8 authority-written; ERC-721 C2 fewer attributes; no `NotSupported` assertion; C1 never checks R1; "pure" ERC-1056 C1/R2 via wrapper).
4. ERC-4337 adapter uses the recovery guardian as the delegate.
5. No dedicated unit tests: `CVINVehicleNFT`, `CVIN_DID_ERC725`, `MOBI/ERC1056Registry`; ERC-725xy missing from security; MOBI-VID missing from harness.
6. Hardcoded: pinned gas (defensible oracles, undocumented); loose `lt()` gas tests that only log; `derivedCostParams`; `ctx.dataset[900+i]`.
7. Weak ERC-721 legacy tests; 13 N/A security cells with no assertion; `recordEntry` uses `Date.now()`.
8. Validity: unlimited contract size; cancun/osaka; minimal EntryPoint; LSP8 stand-in; two ERC-1056 implementations.
9. Two parallel gas pipelines with no reconciliation; `scripts/` outputs carry no measured hash; CI harness job never diffs against `latest`.
10. Tests with side effects (security `after()`).
11. Stale docs: README placeholders ("six implementations"), CI "47 tests", rubric 7/10 empty.

---

## Part II — `2_w3c-ssi-layer/`, `3_cv2x-testbed/`, `cv2x-testbed/`

### II.1 pytest suites (CI `python-full-suite`: `pytest 2_w3c-ssi-layer cv2x-testbed/tests`; a skip fails the job)

`cv2x-testbed/tests/conftest.py`: `rpc_url` from `$CV2X_TEST_RPC_URL` (skips if no node), `load_artifact()` from `$CV2X_TEST_ARTIFACTS_DIR`, `deploy()`.

| File | tests (parametrize) | node? | Covers |
|---|---|---|---|
| `2_w3c-ssi-layer/did-resolution/tests/test_did_resolver_metadata_shape.py` | 11 (2) | no | R1–R4 metadata shape |
| `…/did-resolution/tests/test_did_resolver_review02.py` | 7 (3) | no | S-10: cache isolation, `invalidDid`, ABNF, CAIP-10 |
| `2_w3c-ssi-layer/mobi-vid/tests/test_mobi_vid_layer.py` | 28 | **own node 8547** | deploy → issuers → birth VC + anchor → 3 events → attestation → history; negatives (role, tamper, fail-closed revocation S-2) |
| `…/mobi-vid/tests/test_vin_cipher.py` | 9 | no | AES-256-GCM/HKDF round trip, tamper, wrong secret/salt/AAD |
| `…/verifiable-credentials/tests/test_vc_layer.py` | 25 (1) | no | gates G2–G9 of `BUILD_PLAN.md` |
| `…/verifiable-credentials/tests/test_review02_negative.py` | 37 (7) | no | PoCs S-1, S-2, S-4–S-7, S-9, T-3 |
| `…/verifiable-credentials/tests/test_s3_key_binding.py` | 17 | no | chain-id binding; key binding via resolver |
| `…/verifiable-credentials/tests/test_t3_testbed_trusted_issuers.py` | 9 | no | trusted-issuer allow-list (T-3) |
| `cv2x-testbed/tests/test_attack_scenarios_identity_theft.py` | 4 | no | S-1 holder binding |
| `…/test_erc1056_key_resolution.py` | 8 | yes | T-2 forward replay; T-5 no extra RPC |
| `…/test_experiment_harness.py` | 2 | no | T-6 RPC counter; artifact provenance |
| `…/test_freshness_k.py` | 11 (4) | 3 | refresh schedule, staleness k−1, k=∞, 0 RPC cached |
| `…/test_freshness_k_probe.py` | 12 (5) | 6 | probe = 1 `eth_call`; detects revocation/rotation |
| `…/test_lifecycle_parity.py` | 6 | 3 | M4 adapters, verdict rule, unauthorised issuer |
| `…/test_mobi_vid_verify.py` | 10 (1) | 3 | T-4 self-supplied key rejected; `receipt.status` |
| `…/test_pki_certificate_chain.py` | 17 | no | T-1 forged certs, same-name CA, expiry, CRL, fail-closed |
| `…/test_t12_comparison_framework.py` | 3 | no | T-12 failed verify not a timing; PKI uses CA |
| `…/test_t9_freshness.py` | 32 (2) | 8 | T-9 replay/stale/future/altered timestamp, bounded cache, stack semantics, SUMO layers |

All report via pytest only; none writes JSON.

### II.2 Script-style tests (`cv2x-testbed/scripts/`, none in CI)

- `test_use_cases.py` (1663 lines): 12 use cases on `CentralizedVehicleRegistry` (in-memory) + VC shim; "pass" = no exception; 8 `raise RuntimeError` checks, all in use cases 3, 6, 10, 11, 12; use cases 1, 2, 4, 5, 7, 8, 9 have no explicit check; UC12 passes even when post-decommission events are not blocked. Use cases: 1 Manufacturing & Birth · 2 Maintenance · 3 Ownership Transfer · 4 Insurance Claim · 5 Recall · 6 Cross-Border Import · 7 Fleet · 8 Emissions · 9 Theft & Recovery · 10 AV Data Sharing · 11 Dealership Sale · 12 End-of-Life.
- `test_mobi_vid.py`: needs node 8545 + deployment; `test_vin_privacy` prints only; `test_mobi_vid_compliance` is a **hardcoded dict printing "100%"**; positional args (not pytest-collectable).
- `test_vin_encryption.py`: 6 real pytest tests, **outside CI**.
- `test_comparison.py`: blockchain numbers "ASSUMED public-mainnet estimates — NOT measured"; writes `comparison_results.json` to CWD.
- `test_identity_comparison.py`: needs 8545 + `deployments/localhost.json`; writes `results/comparison_<ts>.json`.
- `run_all_demos.py` ("all 10 scenarios"), `run_comparison.py`, `scenarios/cv2x_identity_integration.py` (3 scenarios; stdout + exit code).

### II.3 W3C compliance checker and external suite

- `w3c_compliance_checker.py`: `_run_check(spec, section, requirement, fn)`; string → PASS; `("PARTIAL"|"FAIL", note)`; exception → FAIL. 44 executed checks (DID Core 15, VC DM 17, presentations 7, selective disclosure 3, securing-mechanism deviations 2 forced FAIL) + 10 qualitative SSI principles excluded. Score = (PASS + 0.5·PARTIAL)/44: 94.3 % = 41/1/2. Writes `w3c_compliance_report.json` to **CWD**, no commit/env. Committed `4_comparison-framework/results/w3c_compliance.json` is July, 93.18 %. `docs/conformance/internal/w3c_compliance_report.json` is referenced but absent. `vc_verifier.py:947 COMPLIANCE_CHECKLIST` is a second hardcoded self-score (85.7 %).
- External suite (`docs/conformance/W3C_DID_TEST_SUITE.md`): `w3c/did-test-suite` @ `939b31d`, jest 26.6.3; inputs from `generate_implementations.py` (3 DID + 3 resolver entries); control 347/347. History: 328/441 (09-24) → 336/441 (10-04, R5 cleared; R5′ bad vector `did:nft:0x1:0xabc`) → **335/336** (10-04b after R1–R4). Denominator fell because the suite generates `it` blocks conditionally on key presence; matched pairs: 157 P→P, 36 F→P, 1 F→F, 0 P→F; 68 F and 37 vacuous P no longer generated. Caveat: `_resolve_ethr` synthesises offline; `blockchain_provider` unused.

### II.4 `cv2x-testbed/sumo/`

- `sumo_identity_integration.py --simulate`: `MockMobility` 50 vehicles, 5 km, 3 lanes, 10 Hz, ≤ 8 receivers in 300 m, in-process delivery. `--seed` seeds mobility only; keys fresh per run. PKI layer: P-256 pseudonym certs; cold = chain/CA/validity/CRL; warm = cached key. SSI layer: did:ethr + `V2VSafetyCredential` (EIP-191); cold = full VC verify; warm = recover + compare. No chain involved. Five injected attacks per run (tampered PKI/SSI, stale PKI/SSI −5 s, uncredentialed SSI). Budgets 100 ms and 10 ms vs p95.
- `run_v2v_stats.py`: seeds 1..30, subprocess per seed; per-run medians; across runs median/mean/`ci95` (percentile bootstrap, 10 000, seed 20260719)/p95; `environment_header()`. Output `results/v2v_latency_stats.json`. Committed run: 30/30 seeds, 20 s each, commit `58a6513`, clean; 300,591 sent, 1,650,318 verified, 150 failures = 5 × 30. Medians ms: warm PKI 0.0939 / SSI 0.1528; cold 0.220 / 0.399.
- `results/v2v_latency.json`: last seed only; no seed or environment block. `sumo/README.md` table (60 s) does not match.
- `run_verify_scaling.py` (Exp. D) writes into `4_comparison-framework/results/scaling_verify.json`.

### II.5 Identity providers and protocols

`identity/base.py IdentityProvider`: `register_vehicle, sign_message, verify_message, revoke_credential, check_revocation_status, update_credential, get_credential, resolve_identity`; `IdentityManager.compare_all_providers`, `IdentityBenchmark`.

| Provider | File | Notes |
|---|---|---|
| `CentralizedIdentityProvider` | `centralized_provider.py` | 20 pseudonym certs, `get_crl`, CT log |
| `ERC1056Provider` | `erc1056_provider.py` | deploy, fund, resolve by address, `set_refresh_every(k, mode)` |
| `MOBIVIDProvider` | `mobi_vid_provider.py` | birth, `export_vin_key`, AES-GCM; `update_credential` always False |
| `VehiclePKIIdentity`/`VehiclePKI_CA` | `standard/pki_identity.py` | not an `IdentityProvider`; enrolment/pseudonym CSR, `trust_ca`, revoke, CRL |
| `CentralizedVehicleRegistry` | `centralized_vehicle_registry.py` | birth, event, transfer, issuer auth, history, odometer fraud |
| `CentralizedLifecycleBackend`/`MOBIVIDV2LifecycleBackend` | `lifecycle_backends.py` | M4 |
| VC shim | `w3c_verifiable_credentials.py` | delegates to `2_w3c-ssi-layer` |
| `FreshnessPolicy` | `freshness.py` | T-9 |

`protocols/cv2x_stack.py`: simulation-grade PHY/MAC, BSM/DENM; **unseeded `random`**.

MOBI backend sweep: `1_blockchain-identity/scripts/mobi_vid_backend_sweep.js` → `generate_mobi_backend_table.py` → `mobi_vid_backends.{json,csv,tex}`; backends ERC-1056, ERC-735, ERC-1155, CVIN-Combined, MOBI-VID-V2; ops birthAttestation, lifecycleEvent, thirdPartyAttestation; fidelity = native concepts / 5; one tx per cell.

### II.6 `2_w3c-ssi-layer/` modules

`mobi-vid/`: `mobi_vid_registry.py`, `birth_certificate.py`, `lifecycle_events.py` (11 types, 8 roles, aggregator, odometer rollback); README gas 306,923 is stale (307,166 after G-M). `verifiable-credentials/`: `vc_issuer.py` (canonicalize, `RevocationRegistry`, EIP-191), `vc_holder.py`, `vc_schemas.py`, `vc_verifier.py` (`DIDKeyRegistry`, `TrustedIssuerRegistry`, `NonceStore`, verify VC/VP, hardcoded checklist). `did-resolution/did_resolver.py`: `resolve`, `resolve_representation`, `create_did`, `xml_datetime`; ethr/nft/key/mobi all offline. `requirements.txt` not installable (`did-jwt==0.1.0`; web3 6.11 vs v7 code).

Freshness-k lives in `cv2x-testbed` (`ERC1056Provider(refresh_every=k, refresh_mode='full'|'probe')`; driver `scripts/experiment_freshness_k.py`). M5 pool: `experiment_pseudonym_pool.js` → `pseudonym_pool.*`, pre-registered in `PLAN_MOBI_SUMO.md` §A.2. HTTP condition: `results/metrics-rpc/latest`, register #39.

### II.7 `cv2x-testbed/results/` (28 files, all from experiment scripts; each JSON has `environment` and `config`)

`pki_vs_erc1056.*` (n=50, warm-up 3; `--render-only`) · `freshness_k.*` (n=250, full) · `freshness_k_probe[_r2]`, `freshness_k_probe_fullref[_r2]` (#37) · `lifecycle_parity.*` (M4, n=50). `hardhat_version` null in 5/7 JSONs; commits short.

### II.8 Reviewer-flag list (layer 2)

1. Use-case suite: no-exception pass; 7/12 unchecked; central backend; stdout only.
2. Hardcoded passes: `test_mobi_vid_compliance` 100 %; `test_vin_privacy`; `COMPLIANCE_CHECKLIST` 85.7 %.
3. Assumed data as results: `test_comparison.py`; SUMO excludes network.
4. Stale/contradictory: `w3c_compliance.json` 93.2 %; `3_cv2x-testbed/README.md` (93.2 %, 28 VC, 21 MOBI); `sumo/README.md` table; `mobi-vid/README.md` gas; `run_all_demos.py` "10 scenarios".
5. Not regenerated by a committed script: checker JSON (CWD, artifact only); comparison JSONs; `demo_results.json`.
6. Seeds: `cv2x_stack.py`, scenarios, use cases unseeded; SUMO seeds mobility only; per-seed `v2v_latency.json` overwritten; freshness/parity/pki runs lack a seed field.
7. Environment stamping missing in checker, use cases, `test_mobi_vid`, comparisons, `v2v_latency.json`; `hardhat_version` null; short commits.
8. CI holes: `test_vin_encryption.py` and all script tests outside CI; VC job runs one file; `requirements.txt` broken; deps unpinned.
9. External-suite validity: offline-synthesised documents; denominator shrank by 105; report both.
10. N=1 figures (sweep, M5 gas) deterministic but single; M4 "single full run, no stopping rule".
11. SUMO net hand-authored; real SUMO never run.

---

## Part III — `4_comparison-framework/`, `docs/`, CI, root docs

### III.1 Claim register (`docs/MEASUREMENT_CONDITIONS.md`)

Rule of record: condition tag + source path + commit, or the number is a target/estimate. Tags M0, M1, M1-H, M1-H/HTTP, M2 (never run). Status V/E/S/U/B (no U rows). §5 sets M1-H conditions: compiled cancun, **executed osaka**; block gas 60 M; 1,100 VINs; 1 exact + 5 warm-up + N = 30; toolchain pinning (Hardhat 2.29.1 moved ERC-721 U1/U4 by +12/+25); run identity = four measured hashes. **Rows run #1–#39**, non-monotonic order.

| # | Summary | Tag | Status |
|---|---|---|---|
| 1 | createVehicleDID 78,090 | M1 | V |
| 2 | changeOwner 68,854 / addDelegate 72,219 / setAttribute 51,126 | M1 | V |
| 3 | ERC-721 bare mint 102,804 | M1 | V |
| 4 | internal checker 94.3 % (41/1/2 of 44); structural caveat; 92.0 % under old check | M0 | V (decision pending) |
| 5 | VC 28/28, contracts 47/47 | — | S |
| 6 | ERC-1056 vs ERC-721: 10.3× bare, 6.9× VIN-bound, 1.32× withdrawn | M1 | V |
| 7–9 | early gas estimates | M1 | E/E/S |
| 10 | resolution 50–100 ms with chain lookup | M2 | E |
| 11 | resolution ~0.8 ms | M0 | S |
| 12–14 | VC verify estimates | M0/M2 | E/S/E |
| 15 | SUMO 50 vehicles | — | E |
| 16–19 | bundle-lineage claims | — | S |
| 20 | USD costs | — | E |
| 21 | PKI vs ERC-1056 verify 0.253 vs 9.654 ms (≈38×), n=50; K-5 caveat | M0/M1 | V |
| 22 | cv2x ERC1056Registry gas (0.8.20, paris) | M1 | V |
| 23 | signed BSM size PKI 1,078/1,110 B vs ERC-1056 596 B | — | V |
| 24 | external DID suite 335/336 (was 441) | M0 | V |
| 25 | nine-standard gas; spread 52,216 → 1,680,816 (32.2×); 4337 +46,830 | M1 | V (re-run 3×) |
| 26 | scaling: A/B **B**; C/D **V** (0.164 ms/neighbour, P*≈609 extrapolated) | M1/M0 | B/V |
| 27 | V2V SSI warm 0.153 [0.151, 0.154]; 150 failures = 5 × 30 | M0 | V |
| 28 | security 43/43 exact; attestEvent 169,295 | M1 | V |
| 29 | harness L1 three substrates | M1-H | V |
| 30 | harness L2 lifecycle 1,050,787 / 2,701,239 / 3,155,103 (2.57× / 3.00×) | M1-H | V |
| 31 | L3/L6 flat in N; ERC-1056 resolve 112 RPC at h=50 | M1-H | V |
| 32 | freshness-k knee k≈146 | M0/M1 | V |
| 33 | M4 parity: writes PASS; cached-equal FAIL (pre-registered) | M0/M1 | V |
| 34 | harness L1 ten columns | M1-H | V |
| 35 | harness L2 ten columns; ERC-1056 only 1.10× over ERC-1155 | M1-H | V |
| 36 | H5 dominance: CVIN-Combined dominated by ERC-4337 | M1-H derived | V |
| 37 | probe refresh; no k reaches P*(0.5)=100 on host 2 | M0/M1 | V |
| 38 | M5 pool: gas FAIL (0.76×), linkability PASS | M1 | V |
| 39 | HTTP: ERC-1056 R3 at h=50 203 ms median | M1-H/HTTP | V |

Naming collision: `PLAN_MOBI_SUMO.md` §A.1 M1–M7 are work items (M1 checklist, M2 fidelity table, M3 attestEvent regression, M4 parity, M5 pool, M6 ZK-VIN, M7 Sepolia), S0–S8 SUMO experiments.

### III.2 Review process

Review 02: five lenses; families K/H/S/T/Q; severity Critical/High/Medium/Low; 64 findings + 2 (Pass 2) + 1 (Pass 3) → 3 Critical, 16 High; all Critical and 15/16 High fixed; Q-3 (restate H1) open, author decision. Passes: PASS1_{K,H,S,T}, PASS2_REREVIEW, PASS2_{K,T}; follow-ups FA (#26 C/D, #27), FB (external suite), FC (security matrix, M3), FD (freshness-k, M4), FE (MOBI checklist), GK (probe, M5), GM (MOBI K-15), GR (resolver R1–R4). After-action reports 01–05. Author decisions pending: HANDBACK §4 items 1–15. Never run: Sepolia, real SUMO.

### III.3 `docs/` subfolders and the analysis layer

- `conformance/`: generator, runner shims, three dated report sets, write-up §1–9.
- `artifacts/`: 29 HTML provenance dossiers (`ARTIFACTS_MANIFEST.md`: Wave A done; B/C partial).
- `figures/`: `make_verification_figure.py` ← `results_snapshot.json` (**708302a: 89.6 %, 47 tests**); `make_review_figures.py` hard-codes plan-vs-actual; `resolution_latency_M0.json`.
- `thesis/`: README, SCAFFOLD, seven chapter READMEs; ch. 5 §5.1–5.9.4; §5.7 verdict table.
- `planning/NEXT_STAGES_PLAN.md`: stages 0.8/0.9/1.0-rc (1.0rc.3 `make reproduce` not done).
- Rubric: `DID_METHOD_RUBRIC.md` §1 three columns (stale), §1a six added; ▲ cells from `analysis_rubric_inputs.*`; JSON unscored for 7/10; ledger envelope "to assess".
- Analysis: `analysis/analysis.js` → `ANALYSIS.md`, `analysis.json`, `analysis_{ratios,capabilities,pareto,rubric_inputs}`; A1 ratios (`†`), A2 capabilities, A3/A4 dominance/Pareto (six criteria, three sets), A5 rubric inputs.

### III.4 `4_comparison-framework/`

Scripts: `generate_tables.py` (gas csv/tex) · `run_gas_stats.py --runs 30` (`all_deterministic`; H-12 ci95 mislabel fixed) · `generate_mobi_backend_table.py` · `generate_scaling_tables.py` (A–D) · `run_verify_richness.py` (overwrites tracked `scaling_verify.json`). Other results: `scaling_verify_repeats/` (C/D run1–5, C_R6–R10, confirmation summary) · `sensitivity.*` (**no generator; July; paris**) · `pseudonym_pool.*` · `w3c_compliance.json` (**July, 93.18**).

Security lens 1: `securityScenarios.test.js` → `attack_results.*` (54 = 6 × 9; 43 applicable; exact revert; **metadata "measured 2026-07-19"**). Lens 2: `attack_scenarios.py` + `security_scenarios.js` → `onchain_security.json`, `security_matrix.*`, `security_comparison.tex`; 6 categories × 10 rows; `*` reasoned; last 2026-10-04T09:16; **not in CI**. Stale counts in `security-analysis/README.md` (MOBI replay Partial* vs DEFENDED*), `INDEX.md` ("201-test"), framework README ("147-test", nine vs ten).

### III.5 CI

`benchmark.yml` (push, nightly, dispatch): gas-report job; nine-standard job with cell diff gate; metrics-harness job (`test:conformance` + `npm run metrics`, **upload only**). `test-contracts.yml`: compile + test; header "47 tests". `w3c-compliance.yml`: VC job (one file); `python-full-suite` (artifact freshness, node 8548, no-skip gate); `compliance-score` (FLOOR 93.0 enforced; TARGET 90.0 printed, below floor; comment says 93.2 %). Not in CI: lens 2, scaling, sweep, external suite, cv2x experiments. Python deps unpinned.

### III.6 Root docs

`HANDOFF-DATA-COLLECTION-FRAMEWORK.md` §3.4/3.7 verdicts: H1 refuted as stated at lifetime level (1.1–5.1×); H1′ supported; H3 second half measured; H4 12/17; H5 frontier exists, hybrid not on it. `COMPOSITION.md` badly stale (52,178 → 1,704,992, ~33×, ~10×, 0.165 ms, 93.2 %, P*≈772, "hybrid on the favourable corner", "all five supported", "~295 tests"). `PROVENANCE.md` attribution. `META_COMMENTARY.md` D7/D9 pending, stale counts.

### III.7 Hypotheses: drift and contradictions

- H1 wording: "≥10× create" (ch. 5) · "≥10× create/update, falsified at lifetime" (framework §8) · "substantially cheaper" (README). Ratios 10.3× / ~10× / 6.9× / 2.57× / 2.63× / 3.00× / 1.10×; spread ~33× / 32× / 32.2×; minimum 52,170 / 52,178 / 52,192 / 52,216 / 52,594.
- H2: 93.2 % (ch. 1/5/6/7, COMPOSITION, INVENTORY, JSON, CI comment) vs 94.3 % vs 92.0 % vs 90.9 % vs 89.6 %; external 328/441 (README) vs 335/336.
- H3: "10 ms auth budget" (COMPOSITION, ch. 5) vs "100 ms J2945/1"; 0.165 vs 0.153; P* 772 vs 609; "90 failures = 3 × 30" vs "150 = 5 × 30"; #32/#37 k≈146 or never; #39 over budget on localhost.
- H4: sweep vs harness 12/17.
- H5: "hybrid Pareto-optimal" (README, ch. 5, COMPOSITION, SP-6) vs #36 dominated by ERC-4337; criteria changed from 4 (framework §8) to 6 (A3).
- Test counts: 47 / 147 / 201 / 217 / ~295 / 302 / 351 / 353 / 369 Hardhat; 286 / 358 Python; 739 README.

### III.8 Reviewer-flag list (layer 3)

1. Run of record ≠ HEAD (verified; see I.3).
2. No single regeneration path; stale snapshots (`w3c_compliance.json`, `sensitivity.*`, `results_snapshot.json`, attack date stamp, lifetime model B).
3. Scripts overwrite tracked results.
4. Three gas instruments plus the cv2x registry, no machine check against mixing.
5. Thin statistics: single host; host-dependent knees; no inferential test between substrates; self-scored W3C; simulated mobility; no M2.
6. Pre-registration drift (H5 criteria); most hypotheses lack thresholds/stopping rules.
7. Representative implementations bias ratios (K-9/K-10); `†` lower bounds.
8. Claims surface hand-typed and drifted across ~10 documents.
9. Rubric unscored; CI target < floor; harness job no gate; deps unpinned; register numbering non-monotonic; M-number collision; dangling references (`sepolia_validation.json`, `docs/conformance/internal/…`).
