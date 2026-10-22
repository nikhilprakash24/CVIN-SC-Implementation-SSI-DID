> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`. Dispositions: after-action report 12 §4.

### Findings

(`$S` = `$SCRATCH/audit_scratch/brief-2`. The same report is saved at `$S/REPORT_brief_2.md`.)

F1 | high | sandbox/py-suites/L3-ssi/test_infrastructure_layer.py:1 (claim: docs/MEASUREMENT_CONDITIONS.md:131 row #45 "31 tests; 26/26 mutants of the layer killed"; also docs/milestones/WM-1_REPORT.md:33,121; AAR 11 line 95) | Replay protection can be removed for every message except a signer's first contact, and the 31 tests and the 13-check I2 battery still pass. "26/26 mutants killed" cannot be reproduced.
- **Mutant M31:** at infrastructure_layer.py:213, `if ok:` becomes `if ok and cold:`, so only cold-path messages enter the replay cache.
- **Evidence:** run in the copy `$S/mut31/root`.
  - `pytest test_infrastructure_layer.py` gives `31 passed`.
  - The harness (`sumo_identity_integration.py --simulate --seed 3 --duration 3 --rsu`) shows all 13 `i2*` lines as "rejected (...; expected ...) -> True", including `i2i_replayed_spat: rejected (replay; expected replay)`.
  - PoC `$S/poc_m31.py` prints `cold first: (True, None)`, `warm genuine: (True, None)`, `warm replay (must be 'replay'): (True, None)`.
- **Why it passes:** test_i2i and harness check (i) replay only a signer's first (cold) message. The SPaT stream is almost entirely warm. So #45(i) "replay -> replay" is verified for one message per receiver and signer.
- **Mutant list is not committed:** `git grep -il mutant` lists only docs/MEASUREMENT_CONDITIONS.md, docs/AFTER_ACTION_REPORT_11.md and docs/milestones/WM-1_REPORT.md. No script or list exists.
- **My own set of 42 mutants** (`$S/mutate.py`, `$S/mutants2.py`, run with `PYTHONDONTWRITEBYTECODE` and `__pycache__` removed) left these genuine survivors:
  - M31, above.
  - M05: dropping `del cache[sender_did]` on expiry at line 179.
  - M22 and M23: freshness boundary `>` to `>=` at identity/freshness.py:167 and :170. Tests use 5 s and 0.5 s offsets, never the boundary.
  - M07 and M30 survive but are equivalent mutants. M01 and M02 (window constants) and the other 36 were killed.
| Add a warm-path replay test (accept a warm message, resend the identical packet, expect `replay`) and a boundary test at exactly `max_age` and `max_future`. Commit the mutant set as a script. Correct the #45 and report wording to what the committed tests kill.

F2 | medium | cv2x-testbed/sumo/infrastructure_layer.py:57-58,160,215 (claim: line 215 "malformed input is a rejection, never a crash") | One unauthenticated package with a deeply nested `message` kills the whole Python process with a segfault instead of being rejected.
- **Reproduction:** `python3 -I -X faulthandler $S/poc_c7b.py 100000` prints `Fatal Python error: Segmentation fault ... json/encoder.py line 258 in iterencode / canonical (infrastructure_layer.py line 58) / verify (line 160)`.
- **Threshold:** depth 80000 gives `False wrong_key` (fine).
- **Cause (inferred, not isolated):** standalone `json.dumps(d, sort_keys=True, ...)` at depth 100000 raises RecursionError. The crash appears only inside `verify`, probably because the imported crypto libraries raise the recursion limit.
- **Test gap:** the L3 malformed-input test only tries `{"sender_did": "x"}` and `["a"]`.
- **Rest of the fuzz** (`$S/poc_c7.py`):
  - Inputs: non-dict package, missing keys, message as list/str/None, timestamp NaN/inf/bool/str/negative/1e308/10**400, unhashable `msg_type`, bad signatures, bad credentials, bytes/None `sender_did`, 10 MB payload (0.38 s).
  - Result: 0 escaped exceptions, 0 `ok=True`, 0 replay-cache mutations, only documented reasons or `error:*`. It prints `PROBLEMS: []`.
| Bound message size and nesting before `canonical()`, or canonicalise iteratively. Add a depth test.

F3 | medium | cv2x-testbed/sumo/infrastructure_layer.py:77-83 (claim: docs/MEASUREMENT_CONDITIONS.md:131 (h) "a valid RSU signs SPaT for another RSU's intersection -> binding"; design 3.1 "RSU credential carries ... intersection id") | Field binding is fail-open. It applies only if the credential carries `intersectionId` or `stationId`, and the station check applies only if the message has an `rsu` key. `enroll()` makes `intersectionId` optional (lines 112-117).
- **Accepted, from PoC `$S/poc_c1.py`** (RSU enrolled with `intersectionId=int_1`):
  - `a) rsu_1 omits rsu, int_1 -> True None`, message `{'msg_type':'SPaT','phase':'GREEN','timestamp':0.0,'intersection':'int_1'}`.
  - `b2) TMC (no intersectionId) signs SPaT, any intersection -> True None`, with `intersection: int_9`, when the TMC credential lists SPaT.
  - An RSU enrolled without `extra={"intersectionId":...}` signs SPaT for any intersection. The unit-test fixture `layer`, `rsu_maponly` and `rsu_rogue` are enrolled this way (test_infrastructure_layer.py:35-38).
- **Rejected correctly:** wrong `rsu` value, and SPaT without `intersection` from a bound RSU (`binding`). The warm path behaves the same.
- **What stands:** harness RSUs and controllers are enrolled with `intersectionId` (sumo_identity_integration.py:558-561), so the committed I2(h) result is genuine. The claim holds only for credentials that carry the claim, and the register does not say so.
- **TMC relay:** the TMC credential has no binding. `$S/poc_c8_tmc.py` shows a TimingPlan relayed from ctrl_1 to ctrl_2 inside the window is accepted: `relayed to ctrl_2 inside window: (True, None)`.
| Make the station and intersection claims mandatory for rsu/controller kinds and require the `rsu` field in SPaT. State the TMC and relay limit under #45 "Not covered".

F4 | medium | cv2x-testbed/sumo/infrastructure_layer.py:93,171 and sumo_identity_integration.py:1316-1321 (claim: `--refresh-k` "must be >= 1, or inf (0 used to mean inf silently; review finding B-F7)"; I3 "<= k-1") | The same silent-disable class remains in the library: some `refresh_every` values never trigger a re-check.
- **From `$S/poc_c5.py`:** `nan`, `inf`, `1.5` and `True` are all accepted. With `nan`, "accepted after revoke 7 of 7" (bound void, no error). `'5'` raises TypeError, not the documented ValueError.
- **CLI:** `--refresh-k abc` and `--refresh-k 1.5` end in an uncaught `ValueError: invalid literal for int()` traceback instead of `parser.error` (line 1319). Only `0` and `-1` are handled.
- **The k-1 bound itself holds.** For k = 1, 5, 25 and every counter phase from 0 to 2k, the worst case after revocation is 0/4/24, equal to k-1. The trigger message is rejected as `revoked` and the cache entry is deleted. The next message is cold and `credential_invalid`. A re-presented revoked credential is `credential_invalid`.
| Require `type(refresh_every) is int`. Wrap `int()` in the CLI parser.

F5 | medium | cv2x-testbed/sumo/infrastructure_layer.py:178 (claim: module docstring lines 12-29, "the credential has not expired"; freshness uses the injected clock) | Credential validity ignores the injected clock and `now` on both paths. The cold path uses wall-clock `datetime.now` inside vc_verifier.py:532 (`_check_temporal`). The warm path uses `time.time()`.
- **Evidence** (`$S/poc_c3c4.py`): with receiver `now` = wall clock + 400 days and a 365-day credential, the cold path gives `(True, None)` and the warm path gives `(True, None)`. A simulated time of 0, before `validFrom`, is accepted for the same reason.
- **What is checked:** a future `validFrom` or `issuanceDate` is checked, but against the wall clock.
- **Effect on results:** none in the harness (simulated 0-20 s, 365-day credentials). It is a design and documentation gap.
| Pass `now` into the credential check, or document that credential validity is wall-clock only. Test a clock past `validUntil`.

F6 | low | cv2x-testbed/sumo/sumo_identity_integration.py:842-870,873-878 (claim: register #45 "Cached signer: (b-w) (c-w) (f-w)") | The gate does not verify that the warm variants are warm.
- **Gate:** the genuine warm-up verifications at lines 869-870 have their results discarded. The pass criterion `(not ok) and reason == expected` ignores `cold`. run_infra_stats.py:91-92 also ignores it.
- **Cold gives the same result:** (b-w) and (c-w) would produce the same reasons on a cold receiver. (f-w) is decided before the cache is read. A broken warm-up would still give 13/13.
- **The number stands:** infrastructure_stats.json `per_run.attack_reasons` shows `cold: False` for all three in 30/30 runs.
- **Positive controls and offsets:** no cold attack has a paired positive control (the same unmodified message accepted by the same probe) except (i). Offsets are (f) 5 s against a 1 s window and (j) 0.5 s against 0.1 s, so the boundaries are untested.
| Assert `cold is False` for the `*_w` checks. Add a positive control per attack.

F7 | low | docs/testing/check_docs_numbers.py:57-62 (commit 44dc926 "stale-figure checker no longer excuses range arrows") | The new arrow rule excuses a stale value whenever the entry's current number is a substring of anything after the arrow.
- **PoC** (in the clone, tracked via `git add`): the line `The run showed 90 failures out of 5 attacks -> 1500 runs.` is not reported, because "150" is a substring of "1500". The control line `... 90 failures in the sweep.` is reported (`1 stale figure(s) in 1 file(s)`, rc=1).
- **Digit-free entries:** entries whose `current` has no digit (the new `\b(217|219|369|386) passing` entry) set `cur=None` and never excuse an arrow, which is safe.
- **No test** accompanies the change.
| Match the current value with word boundaries. Add a self-test.

F8 | low | cv2x-testbed/sumo/infrastructure_layer.py:202 (claim: cold path "the recovered address must be the DID's address") | The DID's chain and method segment are not part of the trust decision. Only the last colon-separated token is compared.
- **Evidence** (`$S/poc_c2.py`): when the authority issues a credential to a re-spelled subject DID, all of these are accepted: `did:ethr:0x5:<addr>`, `did:ethr:mainnet:<addr>`, `did:web:evil.example:<addr>`, `did:ethr:<addr>`, `did:key:<addr>`, `did:ethr:0x1:a:b:<addr>`, and lower- or upper-case addresses. The cache is keyed by the raw DID string.
- **Not an outside attack:** it needs an authority-issued credential. The C2 attacks (tampered `permittedMessages`, authority DID string with attacker key, expired credential) are all `credential_invalid`.
| Validate the DID (method, chain, 42-character address) before use.

F9 | low | docs/MEASUREMENT_CONDITIONS.md:133 (row #47, "35,486–35,498") | The I4 gas ranges are two-sample.
- **Evidence:** a third invocation of `npx hardhat run scripts/infrastructure_gas.js` in the clone gave `rotate_key_by_authority 35510`, outside the register range. The other four values (52606, 34050, 51754, 35062) fall inside their ranges. Committed values are 35,486 (infrastructure_gas.json) and 35,498 (infrastructure_gas_run1.json).
- **Explanation too narrow:** the row attributes the spread to random-key calldata zero bytes at ±12 gas each, which predicts more spread than two samples show.
- **Script:** it overwrites the committed infrastructure_gas.json by default (no output argument, line 55). It hard-codes `solcVersion: "0.8.24"` (line 51) instead of reading the compiler. The config (0.8.24, optimizer 200, viaIR, cancun) does match M1.
| Describe the values as "observed in N runs, ±12 per zero byte", or use a fixed key. Write to a run-specific path.

F10 | low | docs/PLAN_SUMO_VISUALISATION.md:34-38 vs cv2x-testbed/sumo/results/traces/*.jsonl.gz | The documented trace schema `cvin-v2v-trace/1` differs from what is written.
- **Documented but not written:** the header fields `commit`, `dirty` and `host`, and `net: highway_intersection.net.xml`.
- **Written instead:** `environment.git_commit`, `environment.code_dirty`, `net: "mock 5 km 3-lane highway"`, plus `rsu`, `rsus`, `refresh_k`, `revoke_rsu_at` and `caveat`.
- **Events:** rx `reason` is `"rejected"` for BSM rejects, where the plan lists `tampered|unknown_sender|stale|replay`. The event types `attack` and `revoke`, and `sign_ms` on tx, are undocumented.
- **Trace content is sound:** no 64-hex strings, no DIDs or 0x addresses, no key material. SPaT counts (800 sent, 4544 verified) equal infrastructure_stats.json `per_run[0]`. The k=5 trace gives max 4 accepted and total 9, equal to infrastructure_revocation.json seed 1.
| Update the schema section to as-built.

### Checked and found sound

- **C2:** sound. `CredentialVerifier.verify_credential` recovers the proof signer and compares it with the allow-list or embedded address (vc_verifier.py `_check_signature`). The PoC attacks (tampered `permittedMessages`, authority DID string with attacker key, expired credential) all give `credential_invalid`.
- **C3:** sound.
  - A forged same-payload packet is rejected `wrong_key` with replay-cache length 0, and the genuine one then verifies.
  - A genuine replay gives `replay`.
  - A relay to another receiver is accepted (documented residual).
  - A rewritten timestamp after the window gives `wrong_key`.
  - 3000 unique valid messages grow the cache to 3000 at 0.22 ms each.
  - The replay key is receiver|sender plus sha256 of the canonical message including `msg_type`.
- **C5 (a)-(d):** sound. Worst accepted after revocation is 0/4/24 for k = 1/5/25 over all phases. See F4 for (e).
- **C6:** no outside exploit, since it needs an authority-issued credential. See F8 for the residue.
- **C8:**
  - The attack list is `I2_EXPECTED`: 13 entries (a-j plus b-w, c-w, f-w), and the `reason == expected` comparison is strict.
  - Threats with no check and not stated out of scope: flooding/DoS, a rogue RSU with a compromised but valid key (only revocation helps), and TimingPlan recipient binding (F3).
  - Message-type confusion is covered by the signed `msg_type` plus the permitted check.
- **C10:** sound.
  - With seed 7 and 10 s, all 25 integer fields (including the baseline counts: 5011 sent, 26877 delivered and verified, 5 failures, 11 safety events) are identical between db6c381 and d61a284 with flags off, with `--trace`, and run twice.
  - `--rsu` and `--rsu --trace`, each run twice, are also identical (44 integer fields; the 25 baseline fields unchanged).
  - So the new code does not consume the seeded RNG.
- **C11:** sound.
  - A diff of the sign/verify bodies (PKI and SSI) between db6c381 and d61a284 shows only a docstring and added `Metrics` fields.
  - Trace writes (sumo_identity_integration.py:725,741) are after the timed return.
  - The identity/ and 2_w3c-ssi-layer/ sources are byte-identical to db6c381, so #27 still describes the BSM code.
- **C12:** the direction of the register note is right.
  - SPaT warm does canonicalisation twice, hashes the payload, inserts into the replay cache, and runs the binding, `time.time()` expiry and permitted checks.
  - BSM warm canonicalises once, has no replay cache, and has no permitted, binding or expiry check.
  - The canonical JSON function is the same (`_ssi_payload_bytes` equals `canonical`).
  - The I1 ratio recomputes to 1.0964, equal to the committed value.
- **C13:** config matches M1. The RSU signs create, anchor and handover; the authority signs rotate and revoke. First-ever writes are included and stated. Two separate invocations are committed as run1 and final. See F9 for the residue.
- **C14:** sound for the claimed scope.
  - **Python:** the pathspecs (`:(top)cv2x-testbed/sumo`, `:(top)cv2x-testbed/identity`, `:(top)2_w3c-ssi-layer`, results excluded) cover everything the harness imports. Per `$S/poc_c14.py`:
    - Editing freshness.py, vc_verifier.py, did_resolver.py or render_trace.py gives `code_clean` False.
    - A staged-only change and an untracked file in identity/ also give False.
    - A gitignored `.pyc` and files under results/ stay True, as intended.
    - An edit under cv2x-testbed/scenarios (not imported) stays True.
  - **JS stamp:** edits to contracts, scripts, config, lockfile and cv2x-testbed/contracts flip `dirty`. test/ and benchmarks/ do not, and infrastructure_gas.js does not import them.
  - **Probe:** `probe_run_identity.sh` prints OK. It tests only untracked probe files in three paths. It does not test tracked edits, staged changes, the identity and VC paths, or the JS scripts and config paths.
- **C15 (partly):** the trace has no keys, signatures or credentials; counts match the JSON; renderer colours and labels match the legend. See F10 for schema drift.
- **C16:** sound for the trunk.
  - **Tree:** the regex set over the frozen tree finds only placeholders (`YOUR_INFURA_KEY`, `YOUR_ALCHEMY_KEY`), the Hardhat default key `0x59c699...` (test, not a finding), and dummy `0x1111...` keys. No `.env` is tracked, only `.env.example`.
  - **History:** `git log --all -S"infura.io/v3/"` shows a live-looking 32-hex Infura key in commits 0ab45bb and 2ed9bcf. Neither is an ancestor of HEAD; they are reachable only from remotes/origin/sandbox-onboarding, wo-s0/* and docs/root-readme. This is the known open item N-1.
  - **Docs:** docs/prior-survey does not contain the value.
- **C18 (partly):**
  - The thresholds in code (0.80, 1.20, 2.0) equal the pre-registration.
  - I2 pass is computed from per-run booleans.
  - Totals are recomputed from `per_run` (24000, 138895, 0).
  - A failed child run aborts with RuntimeError, so N cannot shrink silently.
  - The environment header is captured before the runs.
  - The I3 JSON header has `tree_clean: false` (the I1 results file was uncommitted) with `code_clean: true`.
- **C19 (partly):**
  - Revocation is applied at the first step with `sim_time >= revoke_at`, before any send, for all receivers.
  - A cold first meeting after revocation is rejected `credential_invalid` and not counted as accepted.
  - The cache persists when a vehicle leaves and re-enters.
  - `cached_at_revocation` is counted at that instant, excluding probes.
  - Recomputed from the k=5 seed-1 trace: 8 receivers, max accepted 4, total 9, equal to the JSON.
- **C20:** the only code changes in pass 12 are `check_docs_numbers.py` and `stale_numbers.yaml` (see F7). No number-producing code moved.

### Not checked (and why)

- **C9:** the assertion-strength reading is partial. I read all 31 tests and the weak ones are noted in F1 and F6. No test calls a private helper to check itself.
- **C10:** I could not reproduce the exact "19 counts" list, because the repository gives no list. There are 25 integer fields and all are identical.
- **C12:** no timing microbenchmark of the extra SPaT work. The direction is derived from the code only.
- **C15:** the dashboard replay JSON and figure captions were not compared to the data. The renderer was not re-run (Brief 3).
- **C17:**
  - **Traceability:** mitigation to code line to test is done for freshness, replay (see F1), permitted, binding, revocation cadence, warm expiry and trust anchor.
  - **Threat model:** THREAT_MODEL.md has no infrastructure-message threat (no hit for rsu, infra or spat). Those threats live only in INFRASTRUCTURE_PREREG.md amendment A4.
  - **Standards:** the standards statements in the design (PSID/SSP, authorisation tickets, CRL) were not checked against the standards texts. The 1 s / 0.1 s window is labelled a project policy in freshness.py, not presented as a standard.
- **C18:** warm-up samples are not discarded (medians of all warm samples); not quantified. The pre-registered I5 definition was not re-derived.
- **C20:** the "8 live stale lines fixed" statement was not recomputed.
- **Outside scope, not pursued:**
  - GitHub Actions CI history (no network use).
  - The real SUMO/TraCI path (untested, no SUMO installed).
  - The orchestrator's 26 mutants (not committed).
