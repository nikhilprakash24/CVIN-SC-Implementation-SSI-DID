# Stream H-L: three Pass 3 Low residuals

**Date:** 2026-10-15. **Base:** `ffb71b0`. **Commits:** `c5d1e8c` (fix 1), `99c796a` (fix 2),
`8c325cc` + `8f45c08` (fix 3 and the one test it changed).
**Suites after the stream:** `npx hardhat test` gives **372 passing / 23 pending** (was 369 / 23;
the +3 are the new harness self-tests). `python3 -m pytest 2_w3c-ssi-layer cv2x-testbed/tests -q`
with a node (port 8563) gives **374 passed, 0 skipped** (was 358; +8 for fix 1, +8 for fix 3).

**No number of record moved.** #21 and #27 were not re-run, and no tracked result file changed.
`attack_results.json` is byte-identical. A future regeneration of the SUMO results will differ in
three ways: it has two more injected attacks, a new `freshness` block, and a slightly higher warm
verify (fix 3, section 3).

## 1. #21 revocation sanity check asserts the reason (`c5d1e8c`)

**Problem.** `verify_after_revocation_is_false` only checked that `verify()` returned False.
ERC-1056 checks freshness *before* revocation. A gap of more than 1 s between signing and the
check would therefore have passed the check on staleness alone, without revocation ever being
enforced.

**Change.**
- Each provider's `verify_message` now records `last_reject_reason`. This covers
  `VehiclePKIIdentity`, `CentralizedIdentityProvider` and `ERC1056Provider`. The reason codes
  are `REASON_*` in `identity/freshness.py`; a freshness rejection records the string that
  `FreshnessPolicy.check()` returned.
- The attribute is written **only on rejection paths**. The accept path that every timed verify
  takes is unchanged, so the timed operation does no extra work.
- `StandardPKIAdapter` forwards the attribute to its verifier.
- The script's new `rejected_for_revocation(prov, msg)` resets the attribute, calls verify, and
  requires the reason to be `REASON_REVOKED`. The sanity key now uses it.

**Tests.** `cv2x-testbed/tests/test_revocation_sanity_reason.py` has 8 tests:
- They run `run_backend` with the "sanity" revocation replaced by a 5 s clock jump: the message
  is stale and nothing is revoked. The old check reported `True` for PKI, centralized and
  ERC-1056 (verified on `ffb71b0`: `assert True is False`); the new check reports `False`.
- A real revocation still passes all sanity keys.
- The accept path leaves the attribute untouched.
- A stale message reports `stale`, not `revoked`.

**Effect on numbers.** None. #21 was not re-run, and the timed path's code is unchanged.

## 2. Security harness checks the reverting contract (`99c796a`)

**Problem.** `matchesExpected` compared only the revert data. An identical reason that bubbled
up from another contract therefore counted as the named defense.

**Change.** `attempt()` now requires `expected.target`, a contract or an address. It works in
four steps:
1. It records the last `eth_estimateGas` / `eth_sendTransaction` / `eth_call` request that the
   thunk sent. It does this by wrapping `send` and `request` on `hre.network.provider`.
2. On a matching revert, it re-executes that request with `debug_traceCall` on the `pending`
   block, the context `eth_estimateGas` used, with memory enabled.
3. `originFromStructLogs` walks the trace:
   - Each `CALL`, `CALLCODE`, `DELEGATECALL` or `STATICCALL` that enters code opens a frame
     keyed by the callee's code address.
   - A `REVERT` is attributed to its own frame, unless that frame's most recent child call
     reverted with **byte-identical** data. In that case the frame is forwarding the revert,
     and the origin is the child's origin (recursively).
   - A child that halted exceptionally counts as reverting with empty data in the child.
4. The cell is `DEFENDED` only if the replay reproduces the observed revert data byte for byte
   **and** the origin equals the target. Any other result is `UNEXPECTED-REVERT`, and the
   origin is reported as `unverifiable (...)` where it could not be established.

**Limits** (also documented in `attackHarness.js`):
1. A frame that catches a child's revert and re-reverts with byte-identical data of its own is
   attributed to the child. This can make a check fail, but it cannot make one pass wrongly when
   the target is the outer frame.
2. Only the thunk's last request is replayed.
3. A transaction that was mined and reverted (explicit gasLimit) is replayed on the post-block
   state. That state differs only in the sender's nonce, and the byte-identical check catches
   any divergence.
4. The origin is a *code* address, so a proxied target must be named by its implementation.
   No contract in this suite uses a proxy.

**Tests.**
- All 43 attacks now name their target, which is the contract the attack calls. All are still
  `DEFENDED` under the stronger check.
- Three new self-tests fail on the old harness:
  - `LSP8: caller is not the contract owner`, bubbled through `CVINVehicleAccount.execute()`, is
    `UNEXPECTED-REVERT` with the account as target (origin = LSP8). It is `DEFENDED` with LSP8
    as target, which shows that tracing works through a forwarding frame.
  - A wrong target is `UNEXPECTED-REVERT`.
  - An attack that names no target is refused.

**Effect on numbers.** None. The matrix is still 43 DEFENDED / 11 N/A, and `attack_results.json`
was not regenerated because its content is unchanged. Origins are not written to the JSON, since
addresses depend on deployment order.

## 3. SUMO replay cache (`8c325cc`, `8f45c08`)

**Problem.** `PKIIdentityLayer` and `SSIIdentityLayer` used `FreshnessPolicy(replay_cache=False)`.
A captured BSM that was re-delivered inside the 1.1 s window was accepted again.

**Change.**
- Both layers now use the providers' `FreshnessPolicy` with the replay cache **on by default**.
  `describe()` equals `FreshnessPolicy().describe()`.
- The replay key is `"<receiver>|<sender>"` plus sha256 of the signed payload. The sender is the
  certificate fingerprint for PKI and the DID for SSI.
- Each receiver of a broadcast accepts it once. A second receiver of the same broadcast is not
  a replay. Delivering the message again to the *same* receiver is rejected.
- An entry is recorded only after the message has verified, so a forged copy cannot poison the
  cache.
- SSI now hashes the real payload into the replay key; it previously passed `b""`. The payload
  bytes are serialised once and reused for signature recovery.

**Sizing** (`replay_cache_size_for`). The cache holds one entry per accepted (receiver, message)
pair, for 1.1 s of simulation time. The live set is bounded by:

> N vehicles × 11 msg/s (10 BSM + at most 1 FCW; EEBL every 15 s fits in the margin) × 8
> receivers × 1.1 s = 96.8 entries per vehicle

With a margin of 2 the size is `max(65,536, ⌈193.6 × N⌉)`. The provider default of 65,536
therefore covers N ≤ 338; N = 1,000 gives 193,600. The results record `evicted_live`, which must
be 0. It was 0 in every scratch run.

**Results changes.**
- `run_attack_tests` gains `replay_pki_rejected` and `replay_ssi_rejected`. Each signs a fresh
  BSM, has the probe receiver accept it once, then re-delivers it, which is rejected.
- Injected-attack failures per run go from **5 to 7**. The caveat text in `run_v2v_stats.py` is
  updated to match.
- The results gain a `freshness` block (config, `rejected_replay`, `evicted_live`).
- **Benign traffic is unchanged.** At seed 42, 10 s, 50 vehicles, both old and new code sent
  5,010 messages, delivered 27,752 and verified 27,752. Over 8 seeds both sent 40,091 and
  verified 219,334. The cache rejected no genuine message.
- `test_t3_testbed_trusted_issuers.py::test_consortium_enrolled_vehicle_still_verifies` reached
  the warm path by re-delivering the same package, which is now a replay. It now signs a second
  message for the warm path and asserts that the replay is rejected (`8f45c08`).

**Tests.** `cv2x-testbed/tests/test_sumo_replay_cache.py` has 8 tests, 6 of which fail on
`ffb71b0`:
- A replay within the window is rejected in both layers.
- Another receiver accepts the same broadcast once.
- A new message from the same sender is not a replay.
- A rejected forgery does not poison the cache.
- The policy equals the provider default.
- The sizing is as stated.
- The simulation's attack results include both replay entries.

**Effect on warm verify (not #27 of record).** Measured with `run_v2v_stats.py`, 8 seeds × 10 s ×
50 vehicles, new and old code interleaved over two rounds, scratch outputs only. The host is
shared with parallel streams, and its SSI warm medians (≈0.22 ms) run above #27's 0.153 ms.
Values are across-run medians in ms.

| | old r1 | new r1 | old r2 | new r2 | Δ (new − old) |
|---|---|---|---|---|---|
| PKI warm | 0.1009 | 0.1103 | 0.1015 | 0.1130 | +0.009 to +0.012 (+9 to +11 %) |
| SSI warm | 0.2164 | 0.2290 | 0.2178 | 0.2367 | +0.013 to +0.019 (+6 to +9 %) |
| PKI sign (code unchanged) | 0.1259 | 0.1327 | 0.1282 | 0.1394 | +0.007 to +0.011 |
| SSI sign (code unchanged) | 0.3241 | 0.3280 | 0.3222 | 0.3345 | +0.004 to +0.012 |

- The sign path did not change, yet it also rose by 1 to 9 %. Part of the warm Δ is therefore
  host drift.
- In isolation, `check` + `accept` with the cache on costs **+1.8 µs** per message over the
  cache off (3.2 vs 1.45 µs, `/tmp/hl_scratch/micro.py`).
- Conclusion: the replay cache adds roughly **0.002 to 0.015 ms** to a warm verify. Against
  #27's 0.153 ms this is at most about +10 %, and it leaves every budget verdict unchanged. A
  regenerated #27 should be read as "with replay cache"; #27 of record was not re-run.

Tracked `sumo/results/v2v_latency.json` and `v2v_latency_stats.json` were rewritten by the
scripts during the scratch runs and restored afterwards. `git status` shows them clean.
