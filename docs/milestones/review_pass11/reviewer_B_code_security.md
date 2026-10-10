> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`. Dispositions: after-action report 11 §4.

## Findings

**F1 | high | `cv2x-testbed/sumo/infrastructure_layer.py:121-164` (verify), `sumo_identity_integration.py` SPaT build | Signed message fields are never bound to the credential.** The credential carries `intersectionId` and `location`, and the SPaT carries `rsu` and `intersection`. The verifier ignores all four, on both cold and warm paths. A valid, non-revoked RSU can sign SPaT for another intersection, and a controller can sign updates for another intersection. A single compromised RSU can therefore issue spoofed signal phases for any intersection. The design lists "subject binding" and the credential's location and intersection claims as part of the model. I2 has no attack for this, so a 30/30 pass says nothing about it.
Evidence: `review_poc/p2.py` enrols `rsu_2` (int_2) and `rsu_3`, then has `rsu_2` sign `{"msg_type":"SPaT","rsu":"rsu_3","intersection":"int_3",...}`. Result: `verify("v1", p)` returns `(True, ..., None)`. The ctrl_1 update for int_1 is likewise accepted by any receiver, because the update has no addressee and no binding.
Fix: on both paths, require `message["intersection"] == subject["intersectionId"]` (and `message["rsu"] == subject["stationId"]` when present). Add an I2 attack (h), a cross-intersection SPaT.

**F2 | high | `infrastructure_layer.py:65` (`replay_cache=False`) and `sumo_identity_integration.py:run_infrastructure_attacks` | Replay is accepted and never tested, though the design promises it.** Both design documents say the verifier does "freshness window and replay check (T-9)". The design's I2 list names "replayed" as an attack. The pre-registration's list of (a)-(g) silently drops it. A captured package is accepted again within the 1.0 s window, by the same receiver and by a different receiver, warm or cold.
Evidence: `p2.py` shows a first accept `True`, a replay at +0.9 s to the same receiver `True`, and the same package to a fresh receiver B `True`. It is rejected only after the window, as `stale`.
Fix: either enable the replay cache (as the cv2x providers do) and add a replay attack to I2, or state in the pre-registration and chapter 5 that replay inside the window is an accepted limitation. The V2V layer documents the same limitation (`_bsm_freshness`), but the infrastructure design text claims the opposite.

**F3 | medium | `run_infrastructure_attacks`, `sumo_identity_integration.py` | All 7 attacks hit fresh cold receivers, and the rejection reason is never recorded.**
Reasons from `review_poc/p1.py` (monkeypatched `verify`):

| Attack | Receiver state | Reason |
|---|---|---|
| i2a | cold | unsigned |
| i2b | cold | wrong_key |
| i2c | cold | not_permitted |
| i2d | cold | credential_invalid |
| i2e | cold | credential_invalid |
| i2f | cold | stale |
| i2g | cold | wrong_key |

- Not every rejection is for an unrelated reason: each attack is rejected by the intended check, so no stale-masks-everything problem. i2f is rejected as stale only because it is the only stale-timestamped one, and the others carry a fresh timestamp.
- i2d and i2e are the same defence (untrusted issuer). i2d never tests "vehicle credential from the trusted authority". The unit test is the same.
- No attack runs against a warm receiver. The warm wrong-key, warm not-permitted and warm stale paths are untested in the harness. The reasons are not written to the results JSON or the trace, which only record `rejected: true`. The 30/30 is only a boolean.
- A future-dated message (timestamp ahead of `now` by more than 0.1 s) is never attacked.
Fix: log `reason` into `attack_tests` and the trace, run each attack against a pre-warmed receiver as well, and add the replay, cross-intersection and future-dated attacks.

**F4 | medium | `infrastructure_layer.py:130-143` | Warm path never re-checks credential expiry.** Only revocation is re-checked, and only every k messages. With the default `refresh_every=None`, an expired credential (365-day validity) stays trusted for the life of the cache. With a finite k, expiry is still not re-checked, only revocation. This is likely acceptable for the thesis, but the module docstring and prereg do not say so.
Fix: store `expirationDate` in the cache entry and check it on every message (cheap), or disclose it.

**F5 | medium | `sandbox/py-suites/L3-ssi/test_infrastructure_layer.py` | Four mutants survive; the tests cannot fail on them.** Method: copy the layer, disable one check, rerun the file. `review_poc/mut.py`, 17 mutants run. The 18th (exception-accepts) failed to apply, so no result for it.
- Survived: `warm_permitted_removed`. The warm `msg_type not in permitted` check can be deleted and all 16 tests pass.
- Survived: `future_unbounded` (`max_future_s=1e9`). There is no future-timestamp test.
- Survived: `subject_mismatch_removed`.
- Survived: `no_credential_accept`. The cold path accepts a package with no credential.
- Equivalent for the I3 bound, but the test cannot see the cadence: `refresh_off_by_one` and `seen_not_counted` also survive, because the test only asserts `accepted <= k-1`. Checking on every message passes it. Add a lower bound (the check happens by the k-th message), and a test that a revoked sender is not dropped before the k-th message.
- Killed: cold permitted, freshness removed, stale window huge, unsigned, warm key, cold key, credential invalid, revocation refresh, cache not deleted, trusts any issuer, cache poisoning.
Fix: add tests for warm not_permitted, future timestamp (+0.2 s), subject mismatch (a valid credential for DID A presented with sender_did B), and a missing credential.

**F6 | low | `infrastructure_layer.py:116-117` | A non-hashable `sender_did` raises `TypeError` outside the `try`.** The "never a crash" claim fails for `{"sender_did": ["a"], ...}`; `p2.py` shows the traceback at `cold = sender_did not in cache`. It is in-process only, so there is no network exposure. Fix: move the `sender_did`, `cache` and `cold` computation inside the `try`, or type-check them.

**F7 | low | `sumo_identity_integration.py` `main()`, `refresh_k = None if ... in ("inf","none","0")` | `--refresh-k 0` silently becomes infinity.** The layer itself rejects 0 with `ValueError`. A user reading 0 as "check every message" would silently get the least safe setting. Fix: reject 0 in the CLI.

**F8 | low | `render_trace.py:94` | The RSU label x-position in the spacetime figure uses the loop variable `ts` left over from the last vehicle track.** It is the end time of whichever vehicle came last, not the trace end. It is harmless with the mock mobility, where all vehicles run to the end.

**F9 | low | `render_trace.py:207` (animation) | Rejected BSM links are drawn grey, the same as accepted ones.** Only SPaT links are coloured green or red. Rejected V2V traffic is not distinguishable, though the title says so.

**F10 | low | `infrastructure_layer.py:131-133` | The revocation counter `seen` increments on any signature-valid-length message claiming a cached `sender_did`, including forged or replayed ones, before the key check.** This is not exploitable: it only makes re-checks more frequent. It does mean "every k-th message" is not "every k-th valid message", so the I3 bound is on messages presented, not accepted. `p2.py` shows `seen` = 2 after 2 forged messages.

**F11 | low | I4 gas script, `infrastructure_gas.js:34-44` and row #47 | Ordering effect not disclosed.** The "RSU anchors its key 52,594" figure includes the first write to `changed[rsu]` (and later `owners[]`, a 0 to nonzero SSTORE), which the later operations avoid. Calling it the cost of "an RSU anchoring its key" is fine, but it is not marginal to the later rows. The metadata also has `dirtyAnyFile: true`; row #47 says "dirty false", which is true only for the tracked-code flag. I could not run Hardhat (no `node_modules`), so the JSON values were only compared with the register text.

## Checked and found sound
- **Cold path.** It verifies the credential through the canonical verifier (trusted issuer = authority only, validity and revocation), requires `subject.id == sender_did`, requires the recovered address to equal the DID address, and requires the type to be permitted. A mismatch cannot poison the cache. The cache is written only after all of these pass. `cache_poison` mutants are killed.
- **Warm path.** It recovers the signature against the cached address, checks the permitted type and checks freshness on every message. Wrong-key and stale messages are rejected (`p2.py`).
- **Freshness.** It is applied before the signature check; the signed timestamp is inside the signed message. Future timestamps beyond 0.1 s, non-finite values, bools, strings and missing timestamps are rejected. The 0.1 s tolerance is accepted by design.
- **`revoke()`.** Cold verification fails afterwards: `credential_invalid` for a fresh receiver, and after a drop. With k=5 the cached receiver accepted 4 messages, then `revoked`, then `credential_invalid`.
- **Revocation counting.** The counter is per (receiver, sender), because the cache is per receiver and keyed by DID. This matches the I3 per-(vehicle, RSU 1) claim. The result files show max accepted 0, 4, 24 and 100 for k = 1, 5, 25 and inf, as claimed. `refresh_every` of 0 or negative raises `ValueError` and None means infinity. No exception becomes an accept.
- **Canonical JSON.** `sort_keys`, compact separators, sha256 and EIP-191. There is no field-ambiguity found: a changed type or timestamp changes the signed bytes.
- **Harness with flags off.** Seed 7, 10 s gives sent 5,011, delivered 26,877, verified 26,877, failures 5, safety events 11, and the same with `--trace`. `--rsu` leaves the V2V counts unchanged too.
- **Timing and trace.** The SPaT and BSM verify timers are both internal `perf_counter` pairs. Trace writes sit outside the timed regions. The SPaT warm path does slightly more work than the BSM one (counter, refresh check, type check, two `.lower()`), so the ratio is biased against SPaT if at all. Result file: ratio median 0.996, CI [0.9946, 1.0009], per-run 0.986-1.014, 0 legitimate rejections, 30/30 all attacks rejected.
- **`run_infra_stats.py`.** Key names are consistent with `_infra_results`; the I1 verdict logic matches the pre-registration (m < 0.8 gives "outside band, not falsified"; `m > 2.0` gives FAIL); the I3 bound is `k-1` and `inf` is reported; the I2 verdict requires 7 attack names in every run; the environment header is captured before the runs.
- **`render_trace.py` figures.** The latency figure shows only `ok` rx (accepted); the revocation figure marks rejected as `x` in red and accepted as `|` in green, and the axes are correct.
- **Gas JSON.** It matches the register text; the 52,594 equality with row #6 is consistent with the same `setAttribute` form in `benchmark_gas.js`.

## Not checked (and why)
- **Hardhat run of `infrastructure_gas.js`.** No `node_modules` in the worktree. Only the JSON and the register text were compared.
- **Figure rendering.** I read `render_trace.py` and the trace contents (reasons, y-range 500-507 within the animation's ylim 495-520) but did not open the PNG or GIF files, nor run `render_trace.py`.
- **TraCI/SUMO path.** The mock mobility only; the `--rsu` flag was not run with real SUMO.
- **Cross-run timing.** No statistical re-run of the 30 runs; I took the committed JSON at face value.

PoC and mutation scripts are in `$SCRATCH/review_poc/`: `p1.py`, `p2.py` and `mut.py`.
