# Review 02, Pass 2, stream P2-T (cv2x testbed + S-3)

**Date:** 2026-10-04 · **Author:** Nikhil Prakash
**Findings:** T-9, T-10 (documented only), T-12 (comparison framework, `ca=None`), S-3, plus three items the
session lead added during the stream: the stale tracked ERC1056Registry artifact for #21, M3
(`test_revoked_identity_rejected` did not exercise the revoked flag), and duplicate `registry_id` in
`add_status_registry`.
**Base:** `4d3dcfa`. Local commits, not pushed.

## 1. Commits

| Commit | Scope |
|---|---|
| `8518809` | T-9 (all providers, `cv2x_stack`, `basic_v2v_scenario`, SUMO layers, #21 harness config) + T-10 docstring; `tests/test_t9_freshness.py`; test configuration updates (see §3) |
| `cb07f4a` | T-12: `comparison_framework.py`, `base.py` benchmark, `run_comparison.py`; `tests/test_t12_comparison_framework.py` |
| `d333479` | S-3: `vc_verifier.py` chain id + resolver hook + documented limitation; README; duplicate `registry_id` raises; `tests/test_s3_key_binding.py` |
| `9b743f9` | M3: `test_revoked_flag_rejects_even_when_a_key_resolves` |
| `1c1b8e1` | #21 harness: `--registry-artifact` / `CV2X_REGISTRY_ARTIFACT`, bytecode provenance in the results |
| `1d0e3a2` | #21/#22/#23 results re-run on clean tree `1c1b8e1` (`git_dirty: false`) |
| (this file) | report |

## 2. Per-finding changes

### T-9: replay and freshness
- **New module `cv2x-testbed/identity/freshness.py`.** It provides three things:
  - `signed_bytes(message, timestamp)` = `json.dumps({'message', 'timestamp'}, sort_keys=True)`. The
    generation time is now inside the signature. `seq`/`msgCnt` fields are part of `message`, so they are
    signed too.
  - `generation_timestamp()`: the same naive-UTC ISO string as before, so the wire format and size do not
    change.
  - `FreshnessPolicy`: a window check, plus an optional bounded replay cache keyed on
    (signer, SHA-256 of the signed bytes).
    - Keying on the signed bytes rather than the signature makes an ECDSA (r, n−s) malleated copy count as
      a replay.
    - An entry is recorded only after the signature verifies, so a forged copy cannot poison the cache.
    - Eviction drops expired entries. When the cache is full of live entries, the oldest is evicted and
      `evicted_live` is incremented.
- **Default window (project choice).** `docs/LATENCY_BUDGET.md` documents no IEEE 1609.2 generation-time
  tolerance, and the repo has no 1609.2 profile text to cite. The default is therefore tied to the 100 ms BSM
  interval:
  - **max age 1.0 s** (10 BSM intervals);
  - **max future skew 0.1 s** (one interval);
  - **replay cache on**, 65,536 entries.

  Security is ON by default in all three providers (`self.freshness`).
- **Where the check runs:**
  - `VehiclePKIIdentity` and `CentralizedIdentityProvider` check after the certificate checks and before
    the message ECDSA verify (signer = certificate serial).
  - `ERC1056Provider` checks before any RPC (signer = DID). A stale packet costs no round trip; a test
    asserts this.
- **`protocols/cv2x_stack.py`.** `success` and `rx_info['success']` are now `signature_valid`. An invalid
  message returns `(False, rx_info)`, with `signature_valid=False` kept so callers can tell it apart from a
  radio loss.
- **`scenarios/basic_v2v_scenario.py`.** Invalid messages go to a new `rejected_messages` counter. They no
  longer count as successful receptions, and PDR still counts radio outcomes only.
- **SUMO.** Both `PKIIdentityLayer` and `SSIIdentityLayer` check the BSM's signed `timestamp` (simulation
  time) against a clock. The integration passes the simulation clock; a standalone layer uses the wall
  clock.
  - The PKI layer verifies the provider's new signed bytes.
  - The SUMO layers have **no replay cache**: the warm path is per-peer. This limitation is documented in
    `_bsm_freshness`.
  - `run_attack_tests` gained two attacks: a stale PKI BSM and a stale SSI BSM. Both are rejected.
  - `run_verify_scaling.py` now drives a simulation clock.
- **Benchmark (#21).** `experiment_pki_vs_erc1056.py` installs `BENCHMARK_FRESHNESS` explicitly and
  identically on every backend's verifier: the secure default, with the cache on. It records the policy in
  the environment block and the `.md`, and adds two sanity checks: a replayed packet is rejected, and an
  altered timestamp is rejected.

### T-10 (not implemented, documented)
The `ERC1056Provider.verify_message` docstring now says the following:
- Only the custom `did/pub/secp256k1/veriKey/base64` attribute (the newest valid one) is accepted as a
  signing key.
- The identity owner's key (an `identityOwner` ecrecover) and `sigAuth`/`veriKey` delegates are **not**
  accepted, so verify fails closed. This is narrower than ERC-1056's "owner or valid delegate".
- Resolution uses the registry's **latest** state at verification time, not the state at signing. With the
  1 s window, the gap is bounded by the window plus the block time.

### T-12
- `benchmark_verification` returns `(elapsed_ms, verified)` per iteration and signs a fresh message per
  iteration (untimed).
- `run_full_benchmark` times only successful verifies into the mean and records
  `verification_success_count` and `verification_failure_count`.
- `IdentitySystemBenchmark(name, ca=…)` is used by enrollment and pseudonym requests. Before the fix they
  called `…(None)`, which always raised (swallowed) and reported 0 ms. `run_comparison.py` passes the CA.
- `IdentityManager.benchmark_verification` (`base.py`) signs a fresh message per iteration. Re-verifying
  one packet is a replay since T-9.

### S-3
- `CredentialVerifier(chain_id=<int>)` rejects did:ethr and did:key issuers (VC) and holders (VP) whose DID
  names another chain.
  - A bare `did:ethr:<addr>` counts as chain 1, matching `DIDResolver._resolve_ethr`.
  - The chain may be written in hex, decimal or as a network name. A test asserts that the parsing agrees
    with `did_resolver.parse_chain_id`.
  - With no `chain_id`, behaviour is unchanged.
- `CredentialVerifier(did_resolver=…)` adds the resolver hook. The recovered signer must be an address
  (`blockchainAccountId`/`ethereumAddress`) of a method listed under `assertionMethod` (VC) or
  `authentication` (VP). The proof's `verificationMethod` must be listed there too. Resolution errors,
  exceptions and deactivated documents fail closed.
- The limitation is stated in the module docstring and `verifiable-credentials/README.md`: the default key
  binding is **offline and non-rotating**, so a rotated-out key stays valid. The repo's `DIDResolver`
  synthesises documents and does not read the chain, so with it the hook adds structure checks, not
  rotation.
- `add_status_registry` raises `ValueError` when a *different* registry with the same `registry_id` is
  added. Adding the same object again is idempotent.

### Added by the session lead
- **Stale artifact (#21/#22).** The run deployed a fresh compile of the current
  `cv2x-testbed/contracts/ERC1056Registry.sol` (identical to `1_blockchain-identity/contracts/MOBI/`).
  - It was compiled with the **testbed's settings**: solc 0.8.20, optimizer 200, evm paris, no viaIR. The
    `1_blockchain-identity` artifact uses 0.8.24 with viaIR, so it was not used.
  - The scratch compile is not committed. The ABI is identical to `contracts/ERC1056Registry_abi.json`.
  - The results record `registry_artifact`, `registry_bytecode_sha256` (`8ca9cfe5…5812`) and
    `registry_compiler`.
  - The tracked artifact is unchanged; another stream owns it.
- **M3.** The new test mines `updateVehicleKey` and `revokeIdentity` in **one block** (automine off,
  `evm_mine`). The event chain is therefore not cut and the new key resolves (asserted), so only the
  `is_revoked` flag can reject. With that check removed (`if False and …`, temporary), the test **fails**:
  1 failed, 7 passed. The original test is kept.

## 3. Tests

| Suite | Before | After |
|---|---|---|
| `pytest cv2x-testbed/tests 2_w3c-ssi-layer` (node on :8550, artifacts linked) | 195 passed, 0 skipped | **248 passed, 0 skipped** |
| `scripts/test_use_cases.py` | 12/12 | **12/12** |
| `sumo_identity_integration.py --simulate --duration 5 --vehicles 10` | sent 500, verified 400, failures 3 | sent 500, verified 400, **failures 5**. The two extra failures are the new stale-BSM attacks, both rejected |
| `run_v2v_stats.py --runs 3 --duration 5 --vehicles 10` (output to scratch) | — | 3/3 ok; the tracked `sumo/results/v2v_latency.json` it overwrote was restored |
| `basic_v2v_scenario.py --time 2` | — | 38/38 receptions, 0 rejected |

New tests: `test_t9_freshness.py` (29), `test_t12_comparison_framework.py` (3), `test_s3_key_binding.py`
(17), `test_revoked_flag_rejects_even_when_a_key_resolves` (1) and `test_registry_artifact_provenance_recorded`
(1). The two PKI positive controls added to `test_pki_certificate_chain.py` make the count 53.

**Checked against the old code.** The new test files were copied into a `git archive` of `4d3dcfa`; only
`freshness.py` was added so that the imports resolve.

| File | Fail on old code | Pass on old code |
|---|---|---|
| `test_t9_freshness.py` | 22 | 7: unit tests of the new module, plus positive controls |
| `test_t12_comparison_framework.py` | 3 | 0 |
| `test_s3_key_binding.py` | 15 | 2: the unchanged-default control, and the `chain_id` type check, which old code ignores |
| M3 test | — | fails with the check mutated out, as above |

**Configuration-only edits to existing tests** (no assertion weakened):
- `test_pki_certificate_chain._package` signs the new bytes. Two positive controls were added, so the
  forged-certificate cases still fail on the certificate, not on the format.
- `test_erc1056_key_resolution`:
  - the provider fixture uses a 60 s window, so a rejection can only come from key state;
  - the T-2 PoC verifies a second message signed before the revocation instead of re-verifying the
    accepted one, which would otherwise be a replay;
  - it asserts `rejected_replay == 0`.
- `test_t3_testbed_trusted_issuers`: the SUMO messages carry `timestamp: time.time()`, so they fail for the
  trust reason, not for a missing timestamp.

## 4. #21 / #22 / #23: old → new

Three runs are compared:
- **Old**: the Pass 1 run of record, `2032c77` (`d2ad57a`, chain 1337, interval and automine mining,
  tracked artifact).
- **Pre-T-9, same host**: the code at `4d3dcfa`, run against the same fresh registry and node immediately
  after the new run. Output was written to a scratch directory, not committed.
- **New**: `1d0e3a2`, generated from clean tree `1c1b8e1` with `git_dirty: false`. Hardhat 2.28.6 on :8550,
  chain 31337, automine only, cryptography 49.0.0, n = 50, warm-up 3.

| Backend / op (median / p95 ms) | Old | Pre-T-9, same host | New |
|---|---:|---:|---:|
| pki_standard verify | 0.276 / 0.372 | 0.232 / 0.289 | **0.253 / 0.329** |
| pki_centralized verify | 0.252 / 0.298 | 0.247 / 0.289 | **0.254 / 0.325** |
| erc1056 verify (4 RPCs throughout) | 11.163 / 13.524 | 8.981 / 11.606 | **9.654 / 15.984** |
| erc1056 resolve | 10.885 / 12.785 | 8.987 / 12.054 | 8.336 / 9.850 |
| erc1056 check_revocation | 7.207 / 7.993 | 5.642 / 7.662 | 5.810 / 9.516 |
| erc1056 register / issue / revoke | 15.35 / 13.11 / 12.25 | 13.10 / 11.48 / 10.28 | 12.94 / 12.02 / 10.80 |
| pki_standard sign / erc1056 sign | 0.049 / 0.388 | 0.047 / 0.386 | 0.050 / 0.375 |

Verify ratio, ERC-1056 ÷ PKI: old ≈40× (vs `pki_standard`) and ≈44× (vs `pki_centralized`); new ≈**38×** in
both cases.

**The T-9 effect, same host.**
- PKI verify rises by about 0.01–0.02 ms (+3 % to +9 %): timestamp parse, SHA-256 and the cache insert.
- The ERC-1056 change (+0.7 ms median) is within the run-to-run RPC noise. The p95 of 15.98 ms is a tail
  outlier, not a code effect.
- The drop of all ERC-1056 cells versus "old" comes from the node configuration: chain 31337 with automine
  only (no 1 s interval mining), and a different node process. T-9 is not the cause.
- The ordering and the conclusions of #21 are unchanged.

**Sizes (#23, JSON bytes, median).** Old 1,078 / 1,110 / 595; new **1,078 / 1,110 / 596**. The +1 B on
ERC-1056 is the chain id inside the DID (`0x7a69` for 31337 against `0x539` for 1337). It is not T-9, and
the pre-T-9 same-host run also gives 596. T-9 leaves the wire format unchanged.

**Gas (#22, `cv2x` ERC1056Registry, receipt values).**

| Operation | Old (tracked artifact) | New (fresh compile of current source, 0.8.20/opt 200) |
|---|---:|---:|
| register | 54,860 (54,836..54,860) | 54,860 (54,824..54,860) |
| issue | 37,791 (37,767..37,791) | 37,791 (37,767..37,791) |
| revoke | 75,044 (75,032..75,044) | **75,257** (75,245..75,257) |
| deploy | 878,509 | **927,756** |

Revoke (+213) and deploy (+49,247) move because of the K-3 contract fix (`revoked[]` checks added). They
are not a T-9 effect. Both match the session lead's figures.

## 5. Proposed register text (session to apply; shared docs not edited)

**Row #21 (new):**

> verify **0.253 / 0.329** ms PKI (pki_standard; pki_centralized 0.254 / 0.325) vs **9.654 / 15.984** ms
> ERC-1056 uncached (4 RPCs) → ≈38×; resolve 0.001 vs 8.336; check-revocation 0.001 vs 5.810; register
> 4.1 vs 12.9; issue 0.19 vs 12.0; revoke 0.015 vs 10.8. All verifiers enforce T-9 freshness (signed
> generation time, 1.0 s / 0.1 s window, replay cache), configured identically. Hardhat 2.28.6, chain
> 31337, automine, registry compiled fresh from current source (solc 0.8.20/opt 200). Commit `1c1b8e1`,
> results `1d0e3a2`. **V**. Caveats as before (K-5; in-process PKI is a lower bound; uncached ERC-1056).

**Old #21 (`2032c77`) → S.** Reason: T-9 changes the signed bytes and adds a freshness/replay check to every
verify, and the registry bytecode was stale (pre-K-3). Same-host A/B: PKI verify +0.01–0.02 ms; ERC-1056
within noise. The absolute ERC-1056 drop (11.2 → 9.7 ms) is a node-configuration effect (automine only,
chain 31337), not a code effect.

**Row #22 (new):** register 54,860 · issue 37,791 · **revoke 75,257** · **deploy 927,756** (current
source, post-K-3; old 75,044 / 878,509 came from the stale tracked artifact). The K-5 qualifier is
unchanged.

**Row #23:** unchanged in substance. Now 1,078 / 1,110 / 596 B; the +1 B comes from the chain id in the DID.

**Row #12 / #27:** the citations of #21 should read 0.25 ms and 9.7 ms.

**Other figures possibly affected (not re-run):**
- `run_verify_scaling.py` (Exp. D) and the SUMO warm figures now include the timestamp check (a few
  hundred ns per message).
- In the 3-run check, SSI warm is 0.165 ms, the same as the cited 0.165 ms.

## 6. Notes and limitations
- The SUMO layers do freshness only. There is no replay cache there, so a duplicate inside the window is
  accepted.
- An evicted live replay-cache entry re-opens replay inside the window. `evicted_live` counts these
  evictions; size the cache to the message rate × window.
- `json` remains imported in `test_pki_certificate_chain.py`, unused after `_package` changed. Harmless.
- The deprecation warnings for `not_valid_before`/`not_valid_after` in both PKI providers predate this
  stream and were not touched.
