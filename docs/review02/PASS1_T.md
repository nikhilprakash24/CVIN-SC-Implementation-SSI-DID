# Review 02 — Pass 1, stream P1-T (cv2x testbed)

**Date:** 2026-10-03 · **Author:** Nikhil Prakash
**Findings:** T-1, T-2, T-4, T-5, T-6, T-11 (label), plus the K-5 caveat and the parts of T-12 that sit in these files
**Inputs:** `docs/REVIEW_02_CODEBASE.md` §T and K-5, `docs/PLAN_REVIEW_02.md` (P1-T), `docs/MEASUREMENT_CONDITIONS.md` rows #21–#23, reviewer PoCs in `/tmp/review_d/`

## 1. Commits (local, not pushed)

| Commit | Scope |
|---|---|
| `473a1c5` | T-1: CA-signature check in both PKI providers + `tests/conftest.py`, `tests/test_pki_certificate_chain.py` |
| `d9fd242` | T-2, T-5, T-11 (+ T-12 ABI path): `identity/erc1056_provider.py` + `tests/test_erc1056_key_resolution.py` |
| `2a3e986` | T-4: `identity/mobi_vid_provider.py` + `tests/test_mobi_vid_verify.py` |
| `d2ad57a` | T-1 (adapter), T-6, K-5, T-12 caveats: `scripts/experiment_pki_vs_erc1056.py` + `tests/test_experiment_harness.py` |
| `2032c77` | #21 re-run: `results/pki_vs_erc1056.{csv,json,md}` (generated on clean tree `d2ad57a`, `git_dirty: false`) |
| (this file) | report |

`test_experiment_adapter_checks_ca_signature` (in the T-1 test file) needs the adapter change in `d2ad57a`; it passes from that commit on.

## 2. Per-finding changes

### T-1 — certificate signature never verified (Critical)
- `identity/standard/pki_identity.py`: `VehiclePKIIdentity.verify_message(signed, crl, ca_certificate=None)` now runs `cert.verify_directly_issued_by(anchor)` (issuer name == CA subject **and** the CA's ECDSA P-256 signature over the TBS certificate), then the CRL, the validity window, and the message signature. The trust anchor is the CA the vehicle enrolled with (set in `request_enrollment_certificate`), or one set with the new `trust_ca()`, or the explicit argument. With no anchor the message is rejected. The existing two-argument callers (`protocols/cv2x_stack.py`, `scenarios/basic_v2v_scenario.py`, `comparison_framework.py`) keep working because their identities enroll with the CA.
- `identity/centralized_provider.py`: the issuer-*name* comparison is replaced by the same `verify_directly_issued_by(self.ca_certificate)`.
- `scripts/experiment_pki_vs_erc1056.py`: the adapter's verifier gets `trust_ca(self.ca.ca_certificate)`.

### T-2 — revoked key returned by the backward walk (Critical)
`ERC1056Provider._resolve_key_from_events` now (1) collects every event along the `previousChange` chain (one `eth_getLogs` per hop, as before), (2) sorts them by `(blockNumber, logIndex)` and replays them oldest-first, where the newest event per `(name, value)` wins and a `validTo` that is not in the future removes the pair, and (3) returns the most recently set surviving `veriKey`. `max_hops` goes from 64 to 256. A history truncated at the oldest end can only lose old keys, so it fails closed.

**Surprise found while testing: chain time differs from wall time.** `validTo` is chain time. The cv2x Hardhat config uses automine plus 1 s interval mining, and its block timestamps ran about 3 s ahead of the wall clock. A `revokeAttribute` sets `validTo = block.timestamp`. Judged against `time.time()`, that revocation looks still valid for a few seconds, which is why the reviewer PoC had to `sleep(1.1)`.

The fix adds a small `_ValidityClock`:
- if `validTo` is more than 900 s from the wall clock, the wall clock decides, with no RPC;
- otherwise one `eth_getBlockByNumber('latest')` fetches the chain time, and `max(wall, chain)` decides.

The verify hot path therefore pays no extra RPC. A recent revocation costs one. The tests have no sleeps.

### T-4 — MOBI VID verify trusts the message's key; revoke ignores status (High)
- `verify_message` resolves the sender (`vehicle_identity`, else `vehicle_did`; only `did:` or `0x` forms) to the key stored in the provider's registration record. It then:
  - rejects unknown or locally revoked identities;
  - checks the on-chain revoked flag with `getVehicleInfo` when a contract is loaded (an unregistered vehicle makes the call revert, so it is rejected);
  - rejects a message-supplied `public_key` that differs from the registered key.

  The message's key is never used. `sign_message` now also emits `vehicle_identity`.
- `revoke_credential` returns `True` and sets the local flag only when `receipt['status'] == 1`.
- **Limitation (unchanged):** `MOBIVIDRegistry` stores no signing key on-chain, so the key comes from the registering provider's local record. A verifier on a separate instance cannot resolve it. This is a design gap and is out of scope here.

### T-5 — redundant `isRevoked` eth_call (High)
`verify_message` uses `identity_data['is_revoked']` from `getIdentityInfo` (fails closed if absent). Verify RPCs go from 7 to 4 (`eth_chainId, eth_call, eth_chainId, eth_getLogs`). The generated `.md` previously said the minimum was "3 registry round trips (2 eth_call + 1 eth_getLogs)". It now computes the list from the measured methods and states the general minimum: 1 `eth_call` + 1 `eth_getLogs` per change-history block, + 1 `eth_getBlockByNumber` only when a `validTo` is within 900 s of the clock.

### T-6 — RPC count snapshotted after the untimed check (Med)
`measure()` snapshots `rpc.count`/`rpc.methods` immediately after `t1`, before `check()`. ERC-1056 `revoke_credential` goes from 8 to 5 RPCs (the post-check's `eth_chainId, eth_call, eth_chainId` are no longer counted).

### T-11 — controller key = sha256(vehicle_id) (Med, label only)
`ERC1056Provider.vehicle_account` docstring now says **TEST-ONLY / INSECURE BY CONSTRUCTION** and explains why. A two-line `!!!` comment sits on the derivation line. No behaviour change.

### T-12 (parts in these files) and K-5
- The ERC-1056 ABI is loaded relative to the module, not the CWD. The inline fallback ABI has no events, so running from another directory used to break key resolution. A test covers this.
- `--deploy` makes the experiment deploy its own registry and record the deploy `gasUsed` from this run's receipt.
- `CV2X_NODE_MODULES` lets the environment header read the Hardhat and ethers versions from a `node_modules` outside the tree. The run of record is `git_dirty: false`.
- The generated `.md` now has:
  - the truthful PKI verify description;
  - the curve-implementation caveat for the sign cost;
  - the list of review-02 fixes that move numbers;
  - a new caveat 7 (K-5): the ERC-1056 column is the cv2x `ERC1056Registry`, not `EthereumDIDRegistry`.

## 3. Tests

New pytest suite `cv2x-testbed/tests/` (34 tests):

| File | Tests | Chain? |
|---|---|---|
| `test_pki_certificate_chain.py` | 15: PoC forged self-signed cert, both with the CA subject copied and with an arbitrary issuer; a same-name rogue CA; an expired CA-signed cert; a revoked cert; a tampered message; no trust anchor; an enrolled peer; the experiment adapter; the centralized equivalents. Legitimate messages are accepted | no |
| `test_erc1056_key_resolution.py` | 7: the PoC (set key, `revokeAttribute` → resolve returns no key, verify fails), rotation (newest wins; old-key message rejected), revoking an older key leaves the newer one, set → revoke → set restores, a revoked identity is rejected, verify RPCs are exactly `eth_call + eth_getLogs` (+ `eth_chainId`), ABI independent of CWD | **yes** |
| `test_mobi_vid_verify.py` | 11: the PoC `poc_mobi_selfkey.py` verbatim (including on a bare `object.__new__` instance), impersonation with the attacker's own key with and without a `public_key` field, registered key accepted via identity and DID, local revocation, `receipt.status` 0/1 (mocked), on-chain register → verify → revoke, a stale local flag overridden by the chain, an unauthorised revoke reporting `False` | 3 on-chain |
| `test_experiment_harness.py` | 1: RPC snapshot excludes the untimed check | no |

**Skip policy.** On-chain tests use `$CV2X_TEST_RPC_URL` (default `http://127.0.0.1:8545`) and are skipped **only** when no node answers there. They were **actually run** against a Hardhat 2.28.6 node on port 8546:

```
CV2X_TEST_RPC_URL=http://127.0.0.1:8546 CV2X_TEST_ARTIFACTS_DIR=<fresh compile> python3 -m pytest cv2x-testbed/tests  →  34 passed
python3 -m pytest cv2x-testbed/tests   (no node on 8545)                                                                 →  24 passed, 10 skipped
```

**Before-fix check.** The same tests were run against the pre-fix tree (`git archive d0fe9f0`):
- 18 failed and 9 errored;
- the 9 errors are the standard-PKI fixture calling the new `trust_ca`;
- every PoC-derived test failed, as it should.

**Stale artifact (Q-9, not fixed here).** The tracked `cv2x-testbed/artifacts/contracts/MOBIVIDRegistry.sol/MOBIVIDRegistry.json` predates the source fix in `bddbc42`: `registerVehicleBirth` panics with 0x11 (overflow). The three on-chain MOBI tests therefore need a fresh `npx hardhat compile` output, passed via `CV2X_TEST_ARTIFACTS_DIR`. With the tracked artifact they **fail**; they do not skip. The ERC1056Registry artifact matches its source byte for byte.

## 4. #21 / #22 / #23 — before and after

Three columns:
- **Old**: the run of record (2026-09-24, `ed85dfd`, `git_dirty: true`, cryptography 41.0.7, Hardhat 2.27.0, kernel fc-v37).
- **Pre-fix (same host)**: the pre-fix code (`d0fe9f0`) run on this session's host, against a fresh node, immediately before the new run. Only this column isolates the fix effect.
- **New**: the run of record committed in `2032c77` (2026-10-03T22:59Z, `d2ad57a`, `git_dirty: false`, cryptography 49.0.0, Hardhat 2.28.6/EDR 0.3.8, chain 1337, automine, n = 50, warm-up 3, same Xeon 2.10 GHz × 4).

### Latency (median / p95, ms) and RPC calls per op

| Backend | Operation | Old | Pre-fix (same host) | New | RPC old → pre-fix → new |
|---|---|---:|---:|---:|---:|
| pki_standard | register_identity | 15.167 / 19.528 | 4.064 / 4.460 | 4.307 / 5.011 | – |
| pki_standard | issue_credential | 0.721 / 0.878 | 0.196 / 0.243 | 0.209 / 0.283 | – |
| pki_standard | sign_message | 0.054 / 0.089 | 0.048 / 0.075 | 0.049 / 0.074 | – |
| pki_standard | **verify_message** | **0.321 / 0.366** | 0.135 / 0.161 | **0.276 / 0.372** | – |
| pki_standard | resolve_identity | 0.171 / 0.196 | 0.001 / 0.001 | 0.001 / 0.001 | – |
| pki_standard | check_revocation | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 | – |
| pki_standard | revoke_credential | 0.020 / 0.044 | 0.014 / 0.024 | 0.016 / 0.032 | – |
| pki_centralized | register_identity | 5.023 / 5.600 | 2.202 / 2.769 | 2.282 / 2.848 | – |
| pki_centralized | issue_credential | 0.227 / 0.289 | 0.111 / 0.169 | 0.104 / 0.148 | – |
| pki_centralized | sign_message | 0.058 / 0.082 | 0.050 / 0.082 | 0.048 / 0.068 | – |
| pki_centralized | **verify_message** | **0.369 / 0.418** | 0.155 / 0.190 | **0.252 / 0.298** | – |
| pki_centralized | resolve_identity | 0.018 / 0.029 | 0.007 / 0.008 | 0.007 / 0.007 | – |
| pki_centralized | check_revocation | 0.000 / 0.001 | 0.000 / 0.001 | 0.000 / 0.001 | – |
| pki_centralized | revoke_credential | 0.018 / 0.036 | 0.014 / 0.034 | 0.012 / 0.015 | – |
| erc1056_did | register_identity | 16.912 / 22.034 | 15.320 / 18.988 | 15.352 / 17.763 | 6 → 6 → 6 |
| erc1056_did | issue_credential | 13.517 / 15.697 | 13.022 / 15.421 | 13.106 / 15.438 | 5 → 5 → 5 |
| erc1056_did | sign_message | 0.401 / 0.456 | 0.650 / 0.718 | 0.388 / 0.512 | – |
| erc1056_did | **verify_message** | **18.158 / 23.741** | 17.337 / 20.307 | **11.163 / 13.524** | **7 → 7 → 4** |
| erc1056_did | (verify: resolution share, median) | 10.553 | 9.831 | 10.536 | |
| erc1056_did | resolve_identity | 10.058 / 12.753 | 10.337 / 14.806 | 10.885 / 12.785 | 4 → 4 → 4 |
| erc1056_did | check_revocation | 7.712 / 9.365 | 6.877 / 9.656 | 7.207 / 7.993 | 3 → 3 → 3 |
| erc1056_did | revoke_credential | 12.568 / 15.534 | 12.006 / 15.133 | 12.249 / 15.487 | **8 → 8 → 5** |

Verify ratio, ERC-1056 ÷ PKI (medians):

| | vs pki_standard | vs pki_centralized |
|---|---:|---:|
| Old | 56.6× | 49.2× |
| Pre-fix, same host | 128.3× | 112.0× |
| **New** | **40.5×** | **44.4×** |

Fix effect, same host (pre-fix → new):
- PKI verify: ×2.04 (standard) and ×1.63 (centralized). This is the added CA-signature ECDSA verify.
- ERC-1056 verify: ×0.64, from 3 RPCs fewer.

**The ordering does not flip; the gap narrows**, as the review predicted.

### Gas (#22; exact receipt values, min..max from calldata zero-bytes)

| Operation | Old | New |
|---|---:|---:|
| register (`registerVehicle`) | 54,860 (54,836..54,860) | 54,860 (54,836..54,860) |
| issue (`updateVehicleKey`) | 37,779 (37,755..37,779) | 37,791 (37,767..37,791) |
| revoke (`revokeIdentity`) | 75,044 (75,032..75,044) | 75,044 (75,032..75,044) |
| deploy | 878,509 (from `deployments/localhost.json`) | 878,509 (this run's receipt, `--deploy`) |

The +12 on issue is not a code effect. Issue always runs on one vehicle (`v_issue`), whose address is derived from the per-run tag. This run's address has one fewer zero byte in calldata (16 − 4 = 12 gas, EIP-2028, cf. H-3). No contract changed.

### Message size (#23; JSON bytes, median)

| Backend | Old | New |
|---|---:|---:|
| pki_standard | 1,078 | 1,078 |
| pki_centralized | 1,106 | 1,110 |
| erc1056_did | 595 | 595 |

The centralized +4 B comes from the random content of the PEM certificate (serial number and DER signature length), not from a code change. The #23 statement "≈1.08–1.11 kB vs 595 B" still holds.

### Conditions that changed between the old and new runs (not fixes)
- cryptography 41.0.7 → 49.0.0. This is the main reason all PKI figures fell 2–4× regardless of the fixes. The largest effect is on X.509 object access: standard `resolve_identity`, which is a dict lookup plus `cert.public_key()`, went from 0.171 to 0.001 ms.
- Hardhat 2.27.0 → 2.28.6 (EDR 0.3.8 in both), ethers 6.15.0 → 6.17.0.
- Kernel build fc-v37 → fc-v64.
- RPC port 8546 instead of 8545.
- Registry deployed by the script (`--deploy`) at the same address, `0x5FbDB…0aa3`.
- `git_dirty` true → false.

## 5. Proposed replacement register text (for the session to apply; shared doc not edited)

**Row #21 (new):**

> | 21 | PKI vs ERC-1056 identical operations, n=50 (median / p95 ms; PKI = pki_standard, pki_centralized in the .md): verify **0.276 / 0.372** PKI (CA signature + issuer + validity + CRL + message signature, 2 ECDSA verifies) vs **11.163 / 13.524** ERC-1056 uncached (4 RPC calls: 1 `eth_call` + 1 `eth_getLogs` + 2 web3 `eth_chainId`) → ≈40× (≈44× vs pki_centralized 0.252); resolve 0.001 vs 10.885; check-revocation 0.001 vs 7.207; register 4.3 vs 15.4; issue 0.21 vs 13.1; revoke 0.016 vs 12.2 (5 RPCs) | `cv2x-testbed/results/pki_vs_erc1056.{csv,json,md}` | M0 (PKI, in-process) / M1 (ERC-1056 via local RPC, Hardhat 2.28.6, chain 1337, automine) | `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py --deploy`, commit `d2ad57a` (git_dirty false), results `2032c77` | **V** — with the caveats in the .md: in-process PKI is a lower bound on real PKI; local RPC floor ≈2.4 ms per round trip; ERC-1056 verify measured uncached (worst case); **the ERC-1056 column is the cv2x `ERC1056Registry`, not `EthereumDIDRegistry` (K-5), so it is not comparable with #25/#29**; PKI timings depend strongly on the `cryptography` version (49.0.0 here; on 41.0.7 the PKI operations were 2–4× slower). Supersedes the 2026-09-24 row (see 5.D) |

**Row #21 (old), to move to §5.D as S:**

> | verify 0.321/0.366 PKI vs 18.158/23.741 ERC-1056 (7 RPC); revoke 8 RPC; resolve 0.171 vs 10.058; register 15.2 vs 16.9; issue 0.72 vs 13.5 (2026-09-24, `ed85dfd`, git_dirty) | register #21, chapters citing "18.2 ms" / "0.32 ms" | **S** — review 02: PKI verify skipped the CA signature check (T-1, forged certificates accepted); ERC-1056 verify made a redundant `isRevoked` call (T-5); RPC counts included the untimed post-check (T-6); ERC-1056 key resolution returned revoked keys (T-2). Re-run 2026-10-03 (`2032c77`); same-host A/B shows PKI verify ×1.6–2.0 and ERC-1056 verify ×0.64 from the fixes |

**Row #22 (new):**

> | 22 | `cv2x-testbed` ERC1056Registry gas: register 54,860 · issue (attribute) 37,791 (37,767..37,791; calldata zero-byte spread, ±12/byte) · revoke 75,044 · deploy 878,509 | same | M1 (solc 0.8.20, optimizer 200, chain 1337) | same, `--deploy` receipt, results `2032c77` | **V** — a *different contract* from the `1_blockchain-identity` registries in #1–2 and from `EthereumDIDRegistry` in #25/#29 (**K-5**: the cv2x `ERC1056Registry` is not `EthereumDIDRegistry`: no `*Signed` functions, owner-only `registerVehicle`/`updateVehicleKey`/`revokeIdentity` wrappers, a whole-identity revoked flag, and a `DIDRevoked` event with no `previousChange` that cuts the event chain). Do not merge the columns or quote these as "ERC-1056 gas" without that qualifier |

**Row #23:** unchanged ("PKI ≈1.08–1.11 kB vs ERC-1056 595 B"). Re-confirmed in the new run: 1,078 / 1,110 / 595 B.

**Rows that cite #21 values and will need a follow-up edit (not done here):** #12 ("measured values are #21 (PKI 0.32 ms …; ERC-1056 uncached 18.2 ms)") and #27 ("compare #21's uncached 18.2 ms") should read 0.28 ms and 11.2 ms.

## 6. Notes

- **ERC-1056 rotation semantics (T-10 stays open).** Under forward replay a key that was rotated out but never revoked is still a valid attribute, because `updateVehicleKey` does not revoke the old key. The provider returns only the newest key, so a message signed with the old key is rejected, and a test asserts this. If the newest key is later revoked, the older un-revoked key becomes the resolved key again. That is correct ERC-1056 attribute semantics, but it may not match "rotation" as the testbed intends. Owner/delegate semantics remain unimplemented (T-10).
- **PKI register cost** dropped from 15.2 to 4.3 ms between runs, almost entirely because of the cryptography upgrade (the same-host pre-fix run gives 4.06 ms). The fixes do not touch registration.
- The ERC-1056 `sign_message` median of 0.650 ms in the same-host pre-fix run is a transient outlier (sign code is unchanged; the new run gives 0.388 ms). It shows that latency cells within about ±0.3 ms should not be over-read.
- The reviewer PoC scripts are hard-wired to port 8545 and the main checkout. Their logic is reproduced in the tests above (`/tmp/review_d/poc_pki_forged_cert.py` → T-1 tests; `poc_erc1056_revoke_attr.py` → `test_revoked_key_no_longer_verifies`; `poc_mobi_selfkey.py` → `test_poc_*`; `poc_erc_redundant_rpc.py` → `test_verify_uses_no_isRevoked_call`).
