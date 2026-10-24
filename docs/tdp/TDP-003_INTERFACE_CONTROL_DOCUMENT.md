# TDP-003 — Interface Control Document

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** B; IF-04 and section 7 wording revised 2026-10-22 (report 27, held by `check_icd.py`).
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000). **Supersedes:** nothing.
**Format:** MIL-STD-498 interface design description, reduced to what a software testbed has: for each interface,
the two sides, the direction, the data carried with its fields, the implementation that defines it, and the test or
check that holds it. Every field name is copied from the source file named in the row. No interface is described
that the tree does not contain; the Phase 2 interfaces are a sketch (`docs/phase2/ARCHITECTURE.md` section 2) and
are listed in section 8 as planned, not built.

## 1. Interface register

| ID | Interface | From → To (planes) | Defined in | Held by |
|---|---|---|---|---|
| IF-01 | Identity adapter (benchmarks) | harness → substrate (P5 → P2) | `1_blockchain-identity/benchmarks/adapters/IdentityAdapter.js` | adapter conformance gate (`npm run test:conformance`, CI job `metrics-harness`); smoke stage of the grand runner (11 adapters) |
| IF-02 | Identity provider (testbed) | scenario or experiment → provider (P1/P3 → P2/P3) | `cv2x-testbed/identity/base.py` (`IdentityProvider`) | L3/L4 Python suites; `test_t12_comparison_framework.py` |
| IF-03 | Verifiable credential | issuer → holder → verifier (P3) | `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py`, `vc_holder.py`, `vc_verifier.py` | VC layer suite (CI job `vc-layer-tests`); the internal checker (#4) |
| IF-04 | DID resolution | any verifier → resolver (P3) | `2_w3c-ssi-layer/did-resolution/did_resolver.py` (`DIDResolver.resolve`, `resolve_representation`) | external W3C DID test suite (#24); internal checker (#4) |
| IF-05 | Signed message package (V2V) | vehicle → vehicle (P1) | `cv2x-testbed/sumo/sumo_identity_integration.py` (`SSIIdentityLayer.sign`, `PKIIdentityLayer`) | `run_v2v_stats.py` (#27); 7 injected attacks per run |
| IF-06 | Signed message package (V2I, I2I) | RSU → vehicle; controller → RSU; TMC → controller (P1) | `cv2x-testbed/sumo/infrastructure_layer.py` (`sign`, `verify`) | pre-registered I2 (#45); `test_infrastructure_v3.py`; mutation script 39 of 39 |
| IF-07 | Freshness and replay policy | every verifier (P4) | `cv2x-testbed/identity/freshness.py` (`signed_bytes`, `FreshnessPolicy`) | `cv2x-testbed/tests/test_t9_freshness.py` |
| IF-08 | Revocation re-check (k) | verifier cache → chain or registry (P4 → P2) | `cv2x-testbed/identity/erc1056_provider.py`; `infrastructure_layer.py` (`refresh_every`) | #32, #37, #46; `test_freshness_k.py`, `test_freshness_k_probe.py`; `test_d51_chain_time.py` |
| IF-09 | Run stamp | producer → result file (P5) | `tools/run_identity/stamp.py` (`stamp()`); `1_blockchain-identity/scripts/lib/run_stamp.js` | `stamp.py --check`; `docs/testing/probe_run_identity.sh` (CI) |
| IF-10 | Producer manifest and promote | producer → `runs/` → tracked result (P5) | `tools/run_identity/producers.json`, `scopes.json`, `promote.py` | `test_promote.py` (13 refusal tests, CI) |
| IF-11 | Claim register row | result file → chapter, generator (P5 → P6) | `docs/MEASUREMENT_CONDITIONS.md` section 3 (the table) | `make_dashboard_data.py` parser (status marker anchored at the cell start); `build_register.py --check`; `check_docs_numbers.py` |
| IF-12 | Option manifest (sandbox) | option → grand runner (P2 → P5) | `sandbox/options/<slug>/manifest.yaml`; `sandbox/grand/manifest.yaml` | `sandbox/grand/run.py check` (fails on any empty cell); feature matrix check in CI |
| IF-13 | Result file header | experiment → file (P5) | each experiment script's `environment` dict | `check_stamps.py --check-coverage` (every tracked result file classified) |
| IF-14 | ZK-VIN gate and verifiers (layer 5) | vehicle prover → chain (P3 → P2) | `5_zkp-agent-identity/contracts/ZkVinGate.sol` (`anchorCommitment`, `admit`), `Groth16Verifier.sol` (`verifyProof`), `SchnorrEcrecoverVerifier.sol` (`verify`, `prove`) | `5_zkp-agent-identity/test-contracts/zkvin_gate.test.js`; `scripts/prove_and_verify.js`; CI jobs `zkvin` and `contracts` in `zkp-layer5.yml`; #56, #58 |
| IF-15 | Steward policy (layer 5) | owner and verifiers → Steward agent (P3/P4) | `5_zkp-agent-identity/steward/` (`policy.py`, `compiler.py`, `kernel.py`, `leakage.py`, `delegation.py`, `agent.py`) | `5_zkp-agent-identity/tests/test_steward.py`, `test_attacks.py`; CI job `python` in `zkp-layer5.yml`; #61 |

## 2. IF-01 Identity adapter (JS)

Contract: mutating methods return `{ txs: TransactionResponse[], result? }`; read methods return plain values;
`handle` is opaque. A substrate that lacks a primitive throws `NotSupported(adapter, op, reason)`; the harness
records the cell as n/a. Operations, in the catalogue's order, as declared by the abstract class:

| Group | Operations |
|---|---|
| Deploy and create | `deploy`, `createIdentity` (C1), `createIdentityWithAttributes` (C2) |
| Read | `resolveOwner` (R1), `resolveByVin` (R2), `resolveDocument` (R3), `verifyDelegate` (R4) |
| Update | `rotateController` (U1), `addDelegate` (U2), `setAttribute` (U3), `transferVehicle` (U4), `metaTxSetAttribute` (U5, relayed) |
| Delete | `revokeDelegate` (D1), `rotateDelegate`, `revokeAttribute` (D2), `deactivate` (D3) |
| Credential | `prepareIssuer`, `anchorIssuerKey` (V1), `anchorStatus` (V3), `revokeCredential` (V5), `statusCheck` (V6) |
| Presentation and execute | `createPresentation` (P1), `executeCall` (X1) |
| Throughput | `prepareThroughputSenders`, `throughputOp` |

Measured through this interface: #29, #34, #35, #36, #49, #50, #51 (run of record `2026-10-23T00-49-12Z_1f4ace0`, the A3b/A6 re-run of 2026-10-23; every gas cell identical to the runs at 7a9a996 and a9e2a28; #49, #50 and #51 still cite 7a9a996 as their source) and #54 (P1, X1).
The catalogue's definitions per standard are in `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md`.

## 3. IF-02 Identity provider (Python)

Abstract methods of `IdentityProvider`, each returning the metrics record the comparison framework aggregates:

| Method | Returns | Role in the experiments |
|---|---|---|
| `register_vehicle(vehicle_id, metadata)` | `VehicleCredential` | register (#21) |
| `sign_message(vehicle_id, message)` | signed message dict | sign (#21, #33) |
| `verify_message(signed_message)` | `(bool, IdentityMetrics)` | the hot path; uncached ERC-1056 verify 15.513 ms median, 5 RPCs, host-dependent (#21, A3b) |
| `revoke_credential(vehicle_id, reason)` | bool | revoke (#21) |
| `check_revocation_status(vehicle_id)` | `(bool, latency)` | check-revocation (#21) |
| `update_credential(vehicle_id, updates)` | bool | lifecycle writes (#33) |
| `get_credential(vehicle_id)` | `VehicleCredential` or None | — |
| `resolve_identity(vehicle_id)` | `(dict or None, latency)` | resolve (#21) |

Providers: `centralized_provider.py`, `erc1056_provider.py`, `mobi_vid_provider.py`, `standard/pki_identity.py`.
The ERC-1056 provider talks to the cv2x `ERC1056Registry` (K-5), not to `EthereumDIDRegistry`; the two are not
comparable and the register says so on every row that uses them.

## 4. IF-03 Verifiable credential, IF-04 DID resolution

Credential document produced by `CredentialIssuer.issue_credential`:

| Field | Content |
|---|---|
| `@context` | the VC Data Model v2.0 context, the CVIN context, any extra contexts |
| `id`, `type` | credential id; `["VerifiableCredential", <credential_type>]` |
| `issuer`, `validFrom`, `validUntil` | issuer DID; UTC timestamps |
| `credentialSubject` | `{id: <subject DID>, ...claims}` |
| `credentialStatus` | present when a revocation registry is attached |
| `proof` | `type`, `cryptosuite` (EIP-191 secp256k1 recovery), `proofPurpose`, created, verification method, proof value |

Verifier checks, each reported by name in `VerificationResult` (`vc_verifier.py`): `structure`, `schema`,
`signature`, `temporal`, `revocation`, `disclosure`, `holder_binding`; for presentations `vp_signature`,
`vp_challenge`, `vp_domain`, `vp_freshness`, `vp_purpose`. Trusted issuers are an explicit allow-list
(`TrustedIssuerRegistry`); before review 02 (T-3) every issuer self-registered.

Resolver: `DIDResolver.resolve(did) -> DIDResolutionResult` with `didDocument`, `didResolutionMetadata`
(`contentType` absent on `resolve()`, present on `resolveRepresentation()` per DID Core 7.1.2) and
`didDocumentMetadata`; methods `did:ethr`, `did:nft`, `did:key`, `did:mobi`. Since WM-2 C1 (report 21, commit 7ae268a) the
`did:ethr` document is read from the ERC-1056 registry when the resolver is given a provider and the registry address
(owner, delegates, attributes, chain-time validity, deactivation including `DIDRevoked`); without a provider it returns
the default document, stated as not read from a chain (C1-d1). The external suite and the internal checker resolve
without a provider, so #4 and #24 did not move; a chain-backed suite run on C1's provider path is deferred (N-24). The merged clone
lineage's separate on-chain set (Hardhat ERC-1056 and MOBIVIDRegistryV2) scores 311 of 311 (#24); it is a different
inventory and is never summed with 335 of 336.

## 5. IF-05, IF-06 Signed message packages

| Field | V2V (`SSIIdentityLayer`) | V2I / I2I (`InfrastructureLayer`) |
|---|---|---|
| `message` | the BSM payload with `msg_type`, generation `timestamp`, sequence | SPaT, MAP, `SignalStateUpdate` or `TimingPlan` with `msg_type`, `timestamp`; SPaT and MAP must carry `rsu` and `intersection`, `SignalStateUpdate` must carry `intersection` (`REQUIRED_FIELDS`) |
| `sender_did` | `did:ethr:0x1:<address>` | same |
| `signature` | EIP-191 secp256k1 over `signed_bytes(message, timestamp)` | same |
| `credential` | the subject's `V2VSafetyCredential`, attached for first contact | `InfrastructureStationCredential`, `SignalControllerCredential` or `TrafficManagementCredential` with claims `stationId`, `stationKind`, `permittedMessages`, `location` |
| `identity_type` | `ssi_vc` | `infra_vc` |

Verification order and rejection reasons: DWG-003. The PKI layer carries a PEM certificate instead of a credential;
message sizes are register #23.

## 6. IF-07, IF-08 Freshness, replay and re-check

`signed_bytes(message, timestamp)` is `json.dumps({"message": ..., "timestamp": ...}, sort_keys=True)`; the
generation time is inside the signature. Policy defaults: `DEFAULT_MAX_AGE_S` 1.0 s, `DEFAULT_MAX_FUTURE_S` 0.1 s,
`DEFAULT_REPLAY_CACHE_SIZE` 65,536 entries, keyed by `(signer, sha256(signed bytes))` so signature malleability does
not make a new message. Both bounds are constructor arguments; the defaults are a project choice tied to the 100 ms
interval and are documented in the module. The re-check cadence is `refresh_every` (an integer at least 1, or
None for never; D39 made the parser reject anything else). A re-check consults the authority's registry (in-process,
I3) or the chain (`--refresh-mode full|probe`, #32, #37).

## 7. IF-09 to IF-13 Evidence formats

**Run stamp (`stamp()`), fields:** `commit`, `code_dirty` (uncommitted change inside the producer's resolved scope),
`tree_dirty` (anywhere in the tree), `scope` (the producer key), `scope_files` (count), `scope_sha` (sha256 of the
sorted scope paths, 12 hex). The JS helper writes the same fields from the same `scopes.json`. Rule 1.1.6: a run with
`code_dirty` true is discarded and the discard written down.

**Producer entry (`producers.json`):** `inputs` (files or directories whose change changes the result, or a reference to an
entry of `input_sets`, written `@hardhat`), `results` (the tracked destinations), with the shared `search` paths and `exclude` globs. Resolved
by `stamp.py --write` into `scopes.json`.

**Result file header (`environment`), as written by the freshness experiment:** `date_utc`, `git_commit`,
`git_dirty`, `python_version`, `node_version`, `hardhat_version`, `ethers_version`, `cryptography_version`, `os`,
`cpu_model`, `cpu_count`, `timer`, `repetitions_per_op`, `discarded_warmup_runs`, `p95_method`, `web3_version`,
`rpc_url`, `chain_id`, `block_gas_limit`, `automine`, `contract_address`, `contract_deploy_gas`, `client_version`.
Other experiments write the same family of keys; the Python header also carries `code_clean` beside `tree_clean`
since N-14.

**Register row (`MEASUREMENT_CONDITIONS.md`):** columns `#`, `Claim`, `Location`, `Tag`, `Source on trunk`,
`Status`; the status letter is the bold marker at the start of the status cell and nothing else is parsed as it.

**Option manifest:** `option`, `slug`, `kind`, `contracts`, `provider`, `benchmark_key`, `experiments`,
`benchmark_ops`, `families` (a list) each with `name`, `stance` (`measured-in-comparison`, `implemented`,
`not-applicable`), `functions`, `measured`, `reason`, `reviewed`.

## 8. Planned interfaces (sketch, not built)

`MobilitySource` (P0), `Channel` (P1), `LedgerTarget` (P2), `CredentialSuite` (P3), `RevocationPolicy` and
`Detector` (P4), from `docs/phase2/ARCHITECTURE.md` section 2. Each would keep the Phase 1 implementation as its
reference implementation and record the implementation in use in the run stamp. None exists in code; TDP-002
carries no requirement on them.

## 9. Layer 5 interfaces (IF-14, IF-15)

IF-14: the vehicle anchors a commitment with `anchorCommitment` and is admitted by `admit`, which verifies a Groth16
proof on chain (301,163 gas, #58) against the 3,498-constraint ZK-VIN circuit (#56). The Groth16 keys come from a
single-party setup that is insecure for deployment (#57). IF-15: the Steward turns the owner's rules into a signed
policy, computes the proofs and bounds what verifiers learn; in simulation it holds leakage to 3.0 bits or less but
serves fewer than 90 percent of honest requests on 25 of 60 runs, so Z-E6 FAILed (#61). Both are held by the CI
workflow `.github/workflows/zkp-layer5.yml` (jobs `python`, `zkvin`, `contracts`); the grand runner does not run them.

## Revision history

| Rev | Date | Change |
|---|---|---|
| B | 2026-10-24 | corrected from docs/tdp/REVIEW_2026-10.md (after-action report 38): P1 and X1 adapter group, harness run history, #21 at 15.513 ms, 311/311 on-chain set, 7 injected attacks, IF-14 and IF-15 for layer 5 |
