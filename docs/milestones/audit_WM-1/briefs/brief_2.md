# Brief 2 - Code and security of what WM-1 built (infrastructure layer, harness, drivers, tests, trace tooling)

## 1. Scope

**Question this brief answers:** does the infrastructure-messaging verifier really reject what the register says
it rejects, can it be defeated by something the 13-check set does not contain, are its tests able to fail, and
do the harness changes leave the earlier V2V results of record untouched?

**Code (frozen checkout paths)**
- `cv2x-testbed/sumo/infrastructure_layer.py` (218 lines; the verifier; read all of it).
- `cv2x-testbed/sumo/sumo_identity_integration.py` (diff `db6c381..d61a284`: +307 lines; flags `--rsu`, `--refresh-k`, `--revoke-rsu-at`, `--trace`; the I2 attack constructions; the timed regions of the V2V path).
- `cv2x-testbed/sumo/run_infra_stats.py`, `run_v2v_stats.py` (diff), `render_trace.py`.
- `cv2x-testbed/identity/freshness.py`, `cv2x-testbed/identity/w3c_verifiable_credentials.py` and the VC layer they use (`2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py`, `vc_verifier.py`): the infrastructure verifier delegates credential checks to them, but they were not changed or reviewed by WM-1.
- `1_blockchain-identity/scripts/infrastructure_gas.js`, `scripts/lib/run_stamp.js` (the run-stamp helper added to four other producers).
- `sandbox/py-suites/L3-ssi/test_infrastructure_layer.py` (31 tests) and its `conftest.py`.
- Design/pre-registration/threat model: `docs/design/INFRASTRUCTURE_MESSAGING.md`, `docs/design/INFRASTRUCTURE_PREREG.md`, `docs/PLAN_SUMO_VISUALISATION.md` (trace schema `cvin-v2v-trace/1`), `docs/THREAT_MODEL.md`.
- Committed traces and figures: `cv2x-testbed/sumo/results/traces/`, `cv2x-testbed/sumo/results/figures/`, `cv2x-testbed/sumo/results/infrastructure_*.json`.
- Commits `47c3314`, `1e690c3`, `f1f9e37`, `b1d3f72`, `601e1de`, `36e0309` (code parts only).

## Common context (read first; identical in all five briefs)

**The repository.** A master's-thesis research repository (author: Nikhil Prakash, UBC ECE) on blockchain /
self-sovereign identity (SSI) for connected vehicles. It holds: Solidity contracts for nine identity
standards (Hardhat, `1_blockchain-identity/`), a Python W3C DID / Verifiable-Credential layer
(`2_w3c-ssi-layer/`), a V2V / V2I message-path testbed with a mock-mobility simulation harness
(`cv2x-testbed/`), a comparison framework and committed result files (`4_comparison-framework/`), a
"sandbox" with per-option demos and test layers (`sandbox/`), a claim register
(`docs/MEASUREMENT_CONDITIONS.md`, rows #1-#48; status V = verified, S, E, B, ...), generated dashboards and
registers (`docs/figures/`, `docs/testing/`, `docs/thesis/`), and thesis chapters (`docs/thesis/chapter1..7`).

**The work under audit.** Work milestone WM-1 = passes 8-11, commit range `db6c381..291bbca` (27 commits),
plus the closing pass 12 (commits `3e19e72`, `44dc926`, `d61a284`) which made "backward fixes" and wrote the
milestone report. WM-1's headline content: merge closure; generated, CI-checked documents (dashboard,
crux register, test register, stale-figure checker, run-stamp / "dirty flag" tooling); and a new
infrastructure-messaging layer (roadside units, signal controllers, a traffic-management centre as
credentialed DIDs; signed SPaT messages) with five pre-registered experiments I1-I5 (register rows #44-#48),
an adversarial review in pass 11, hardening, and a re-run. The milestone report
(`docs/milestones/WM-1_REPORT.md`) was written BEFORE this audit, so the report is itself under audit.
The orchestrating assistant did the work and wrote the report; you are independent of it. Nothing it wrote
is evidence of its own correctness: re-derive.

**Frozen checkout (read only).** `$SCRATCH/audit_d61a284` (commit `d61a284`). Do not edit, commit, push, stash, `git worktree add`,
`git checkout`, or run anything that writes inside it. Do NOT touch `/home/user/CVIN-SC-Implementation-SSI-DID`.
`node_modules` is available through a symlink in `$SCRATCH/audit_d61a284/1_blockchain-identity`. When you need a writable copy,
clone locally into your scratch directory: `git clone -q $SCRATCH/audit_d61a284 $SCRATCH/audit_scratch/brief-2/clone && ln -s $SCRATCH/audit_d61a284/1_blockchain-identity/node_modules $SCRATCH/audit_scratch/brief-2/clone/1_blockchain-identity/node_modules`
(the clone is yours to modify; old commits are reachable in it with `git -C $SCRATCH/audit_scratch/brief-2/clone show <rev>:<path>` or `git archive`).

**Hard rules for commands.**
- Write only to your scratch directory `$SCRATCH/audit_scratch/brief-2/` (create it).
- Long experiments (the 30-run sweeps of ~7-30 min: `run_infra_stats.py`, `run_v2v_stats.py`, `run_verify_scaling.py`, `npm run metrics`, `benchmark_scaling.js`, the I3 revocation sweep) must NOT be re-run. Recompute from the committed JSON instead.
- Allowed short runs: a single seed of the harness (seconds), the pytest suites, `npx hardhat test` (about 25-60 s) and single Hardhat scripts, the document generators in `--check` mode, `git`, `grep`, `python3 -I`, `node`. A Hardhat node, if you need one, must use a non-default port (for example 18548) and you must kill it by recorded pid.
- When running `cv2x-testbed/sumo/sumo_identity_integration.py` ALWAYS pass `--results $SCRATCH/audit_scratch/brief-2/<name>.json` (its default overwrites a committed file). Run it from a clone, not from `$SCRATCH/audit_d61a284`.
- Network is available only through a proxy; do not rely on it except for `gh api repos/nikhilprakash24/CVIN-SC-Implementation-SSI-DID/...` read calls (CI check runs) where a check says so. If the network call fails, say so under "Not checked".
- Installed toolchain at audit time: Python 3.11.15, Node 22, pytest 9.1.1, eth-account 0.14.0, cryptography 41.0.7, coincurve 21.0.0, web3 8.0.0, matplotlib 3.11.2, numpy 2.4.6, PyYAML 6.0.1. Differences from CI (unpinned installs) are themselves worth noting but are not findings unless they change an outcome.

**Mindset.** Be adversarial. The audit exists because the people who did the work chose the earlier review's
scope. Prefer checks that could FAIL. For every "passes / is verified / is covered / is CI-checked / byte-identical /
N of N" statement you meet, ask: what would the check look like if the claim were false, and does the
existing check actually distinguish the two? Look especially in places the milestone report does not mention.
If you find a claim you cannot verify because the evidence is not in the repository (for example a script
or data set that is described but not committed), that IS a finding (irreproducibility), with severity medium
or higher if a register number depends on it.


## 2. Numbered checks

Work in a clone (`$S/clone`). Put every proof of concept in `$S/poc_*.py` and quote its output in the finding.
The verifier is in-process Python; you can import it directly (`sys.path.insert(0, "<clone>/cv2x-testbed"); from sumo.infrastructure_layer import InfrastructureLayer` or run from `cv2x-testbed/sumo`).

**C1. Field binding is conditional.** `_binding_ok` skips the station check when the message has no `rsu` key (`"rsu" in message`) and tests `intersection` only if the credential names an `intersectionId`. Construct: (a) an RSU credential with `stationId` but a SPaT that omits `rsu`; (b) a credential with no `intersectionId` (what do `enroll()` callers in the harness and in `run_infra_stats.py` pass for controllers and the TMC?) signing a SPaT for any intersection; (c) a SPaT with `intersection` absent. Determine which are accepted, whether they are within the register's claim "a valid RSU signs SPaT for another RSU's intersection -> binding" (#45 (h)) and whether the design says binding is mandatory. Report accepted forgeries as a security finding with the exact message.

**C2. Credential issuer trust.** Read `CredentialVerifier.verify_credential`. Attack: a credential whose `issuer` field names the road authority's DID but whose proof is made with the attacker's key; a credential reusing a revoked credential `id`; a credential with the right issuer and a tampered `credentialSubject` (e.g. add `permittedMessages`); a credential from the rogue authority carrying the authority's DID string. Does the verifier bind the issuer DID to the key that made the proof (by recovery against the DID's address, or against the key held in `trusted_issuers`) or only compare DID strings? #45 (e) only covers "untrusted authority" under its own DID.

**C3. Replay cache side effects.** Read `FreshnessPolicy.check` and `.accept` (`cv2x-testbed/identity/freshness.py`). Does `check()` insert into the replay cache or is insertion deferred to `accept()` after a successful verify (the verifier calls `accept` only when `ok`)? Test: an attacker sends a forged (invalid-signature) packet carrying the same payload bytes as an imminent genuine one: is the genuine one then rejected as `replay`? Test cache growth under a flood of unique valid-looking packets (memory / eviction; time complexity of each `check`), and replay keys that collide across message types (`replay_key = receiver|sender`, payload hashed?). Test the two documented residuals: relay to a receiver that never saw the message (register says not covered) and replay AFTER the window but with a forged timestamp (signed timestamp, so should fail).

**C4. Clocks.** The verifier takes `now` for freshness, but the warm-path expiry uses `time.time()` and the cold path's credential validity uses whatever `CredentialVerifier` uses (check). In the harness, simulated time is used for messages. Construct a case with a simulated clock past the credential's `validUntil` (and one before `validFrom`) and show which path catches it and which does not. Is `validFrom` / `issuanceDate` in the future checked at all?

**C5. Revocation path.** Trace the k-th-message re-check: counter `seen` increments before the wrong-key / expiry / permitted / binding branches, and counts forged messages (documented as "only makes the re-check come sooner"). Verify with a PoC that (a) after revocation at most k-1 further messages pass for k = 1, 5, 25 for ANY phase of the counter, including a counter that starts at 0 on first warm use; (b) the message that triggers the re-check is rejected and the cache entry deleted; (c) the next message from the same DID takes the cold path and is rejected by `verify_credential` (revocation) rather than re-accepted; (d) a revoked RSU whose credential is re-presented in a new package with a different credential id is handled; (e) `refresh_every` of bool/float/str/negative is rejected; the CLI `--refresh-k` parser (`inf`, `0`, `-1`, `abc`, `1.5`) behaves as documented. Compare to the I3 claim "<= k-1".

**C6. DID/address binding.** Cold path compares the recovered address with `sender_did.rsplit(":", 1)[-1]`. Test DIDs with a different chain segment (`did:ethr:0x5:...`, `did:ethr:mainnet:...`, `did:web:...`), upper/lower/checksum case, trailing text, a DID with extra colons, and a credential subject id that differs only in case. Is the chain segment part of the trust decision? Does it matter for the claims?

**C7. Malformed input fuzz.** The layer says "malformed input is a rejection, never a crash". Fuzz `verify()` with: non-dict package, missing keys, `message` a list/str/None, `timestamp` NaN / inf / bool / str / negative / 1e308, `msg_type` unhashable (list/dict), `signature` of wrong length / non-hex / bytes, `credential` as str / list / huge nested dict (recursion), very large payloads (CPU time of canonicalisation, 10 MB), `sender_did` bytes. Record any exception that escapes, any `ok=True`, any case where the cache is mutated by a rejected message, and any reason string that does not match the documented set (`stale future replay binding expired wrong_key not_permitted credential_invalid subject_mismatch unsigned no_credential revoked bad_timestamp error:*`). Note whether the exception handler hides a bug in a legitimate path (reasons of the form `error:...` in the committed result JSON's legitimate traffic: expected 0).

**C8. Attack set versus the 13 checks.** List the attacks in `sumo_identity_integration.py` (`attack_tests`, keys starting `i2`) and map each to its register letter. For each: is there a paired positive control (the same message unmodified is accepted by the same receiver), so that the rejection reason is not an artefact of a broken fixture? Is the comparison `reason == expected` strict? For (f) stale and (j) future, are the offsets just beyond the window or far beyond it (boundary behaviour untested)? Name any attack from the design's threat list (`INFRASTRUCTURE_MESSAGING.md`, section on threats) that has no check (e.g. rogue RSU with valid credential but compromised key, expired credential on first contact, credential presented for a different DID, downgrade to unsigned, message-type confusion between MAP and SPaT, controller impersonation, TMC plan replay, flooding) and report whether it is stated as out of scope.

**C9. Tests and mutants.** Run `python3 -m pytest sandbox/py-suites/L3-ssi/test_infrastructure_layer.py -q` (clone). Then create your own mutation set of at least 12 mutants of `infrastructure_layer.py` NOT taken from the orchestrator's list (report 11 says "26 of 26 mutants killed", but the mutant set is not committed: confirm with `git grep -il mutant` that no script or list exists; if so, the claim is unreproducible, say so). Suggested mutants: freshness window constants; `%` -> `>=` in the cadence; drop `del cache[...]` on revoke or expiry; drop the `accept()` call; swap `lower()` comparisons; drop the `subject.get("id")` check; `permitted` check on cold path only; binding check only on cold path; invert the expiry comparison; make `_expiry` return None; drop `entry["seen"] += 1`; make `verify_credential` result ignored; change `trusted_issuers` to include the rogue. Report each surviving mutant with the diff. Also read the tests for assertions that cannot fail (asserting only `ok is False` without the reason; fixtures that share state; tests that call the private helper they are meant to check).

**C10. Does the V2V result of record survive the harness change?** The report says: with all new flags off, and with `--trace` only, seed 7 / 10 s gives 19 of 19 identical integer counts to the pre-change baseline. Reproduce: export `db6c381` and `d61a284` versions of the harness into two scratch directories (`git archive`), run both with identical arguments (`--simulate --seed 7 --duration 10 --results $S/a.json`, ditto b.json; read the script's `--help` for the exact baseline invocation used in `docs/AFTER_ACTION_REPORT_10.md`), compare every non-timing field, and list which fields the "19 counts" are. Also run with `--rsu`, with `--trace`, and with `--rsu --trace` twice each to test determinism of counts. Check whether the new code consumes the seeded RNG when flags are off (an extra `random.*` call shifts all later draws).

**C11. Timed regions.** `v2v_latency_stats.json` (register #27) was produced before the harness changed by 307 lines. Diff the timed code regions (`perf_counter` start/stop) of the BSM sign / verify paths between `db6c381` and `d61a284`. If anything inside a timed region changed (extra checks, logging, trace hooks, freshness changes), the committed #27 numbers no longer describe the current code, and WM-1 did not re-run them: report. Check also that `--trace` recording is outside the timed regions.

**C12. "Like for like".** I1 compares warm SPaT verify with warm SSI-BSM verify and the design says signing is "exactly as for SSI BSMs". Compare, line by line, what is inside the timed region for each: canonicalisation, hashing, freshness check, replay check, signature recovery, address compare, permitted-type, binding, expiry. List what the SPaT path does that the BSM path does not and vice versa, and say which direction the bias goes and whether the register's note ("biased against SPaT") is right. Check that the BSM path being compared is the same function used for #27.

**C13. `infrastructure_gas.js`.** Read it. Check: network config (optimizer, viaIR, cancun) is the one defined as tag M1 (`hardhat.config.js`); each of the five operations is what the register says (`setAttribute` for the key anchor, `changeOwner` to hand to the authority, `revokeAttribute`); who signs (the RSU or the authority); whether any operation is measured after prior writes that make it cheaper or dearer than the first-ever call; whether the "two runs" are really two invocations or one invocation twice; where run1 and run2 are written; whether the script can overwrite committed results by default. Run it once in the clone (`npx hardhat run scripts/infrastructure_gas.js`, writes into the clone) and compare with both committed files.

**C14. Run-stamp scope.** `scripts/lib/run_stamp.js` and the Python `_environment()` / `environment_header()` compute `dirty` / `code_clean` from pathspecs. List the pathspecs. Then test in the clone: (1) edit a tracked file in each producing path (contracts, scripts, config, lockfile, `cv2x-testbed/sumo`, `cv2x-testbed/identity`, `2_w3c-ssi-layer/verifiable-credentials`, `2_w3c-ssi-layer/did-resolution`): does the flag flip? (2) a staged-only change; (3) an untracked file; (4) a `.gitignore`d file in a producing path; (5) a change to a dependency outside the pathspec (for the Python header: `cv2x-testbed/identity/freshness.py` and the VC layer, which the infrastructure verifier imports). If a file the measured code imports is outside the pathspec, `code_clean: true` can be reported for code that is not the committed code: that falsifies the "code_clean" evidence used in register rows #44, #45, #46. Also run `docs/testing/probe_run_identity.sh` from the clone and say what it does NOT test.

**C15. Trace and renderer.** Read the trace schema in `docs/PLAN_SUMO_VISUALISATION.md` and a committed trace (`cv2x-testbed/sumo/results/traces/`). Check: header fields; whether private keys, full signatures or credentials are written into the committed JSONL (secrets, size); whether events in the trace sum to the aggregates in the same run's JSON; whether `render_trace.py` colours and labels match the legend (the report mentions a fixed "renderer label and BSM rejection colour"); figure captions in `cv2x-testbed/sumo/results/figures` and the dashboard replay versus the data (a figure that says "rejected" where the trace says "accepted"). Do not re-run the renderer for byte-identity (Brief 3 does).

**C16. Secrets in the tree and history.** The onboarding lineage import (`docs/prior-survey/`) is reported to concern an exposed Infura credential (open item N-1). Run `git grep -n -E "infura\.io/v3/[0-9a-f]{20,}|[0-9a-f]{64}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY|mnemonic|sk-[A-Za-z0-9]{20,}"` over the frozen checkout, and `git log -S"infura.io/v3/" --oneline` over its history. Report any live-looking credential or private key on the trunk (hardhat default test keys are not findings; say so if you meet them). Check `.env.example`, `.gitignore` and `hardhat.config.js` for any committed `.env` or key.

**C17. Threat model completeness.** Compare `docs/THREAT_MODEL.md` and the design's threat section with what the verifier implements. Pick every mitigation claimed for infrastructure messages (about eight) and locate the code line and the test that proves it. Report claimed mitigations with no code or no test, and claimed standards grounding (SAE J2735 SPaT/MAP, IEEE 1609.2, ETSI TS 103 097 / 102 941, CAMP SCMS, NTCIP) whose description is wrong (for instance, a mechanism attributed to a standard that the standard does not specify, or a 1 s freshness figure presented as a standard value when it is a project policy "review-2 T-9").

**C18. Experiment drivers.** `run_infra_stats.py`: seeds 1..30 independent subprocesses; where the verdict strings are computed; whether verdict thresholds in code equal the pre-registered bands (grep `0.80`, `1.20`, `2.0`); whether the I2 totals are recomputed from per-run data or copied; whether a failed child run is silently dropped (N stays 30 or shrinks); whether warm-up samples are discarded before medians; whether the environment header is captured before the runs (commit `1e690c3` says so) and `commit` / `tree_clean` are measured once at start or at the end (a run can change the tree).

**C19. `--revoke-rsu-at` and RSU placement logic.** Check the revocation schedule: is the revocation applied by simulated time at the same step for all receivers; what happens when the vehicle first meets `rsu_1` AFTER revocation (cold path rejects) and is that counted in "accepted after revocation"? Does a vehicle that leaves range and re-enters keep its cache? Is "3-14 vehicles held rsu_1 in cache" measured at the instant of revocation? An error here changes I3's counts without breaking its bound.

**C20. Pass-12 code changes.** `git diff 291bbca d61a284 --stat -- '*.py' '*.js' '*.sh' '*.yaml'` and read every code/tool change in the closing pass (`check_docs_numbers.py`, `stale_numbers.yaml`, and anything else): do they have tests; do the "8 live stale lines" and the arrow-rule change do what the commit message says; is there any code change in pass 12 that moved a number without a register note?


## 3. Commands you may run

### Commands you may use (read-only on the frozen checkout; writes only under `$SCRATCH/audit_scratch/brief-2/`)
```
FC=$SCRATCH/audit_d61a284
S=$SCRATCH/audit_scratch/brief-2
mkdir -p $S
cd $FC && git log --oneline db6c381..d61a284          # the commit range
git -C $FC show <rev>:<path>                            # old versions
git -C $FC diff db6c381 291bbca -- <path>               # WM-1 diff; also 291bbca..d61a284 for pass 12
git -C $FC grep -n "<pattern>" -- <paths>               # search tracked files (does not write)
python3 -I -c '...'                                     # recompute from committed JSON
```

### Brief-specific commands
```
git clone -q $FC $S/clone && ln -s $FC/1_blockchain-identity/node_modules $S/clone/1_blockchain-identity/node_modules
cd $S/clone/cv2x-testbed/sumo && python3 sumo_identity_integration.py --help
python3 sumo_identity_integration.py --simulate --seed 7 --duration 10 --results $S/seed7_flags_off.json
python3 sumo_identity_integration.py --simulate --seed 7 --duration 10 --rsu --results $S/seed7_rsu.json --trace $S/seed7.trace.jsonl
cd $S/clone && python3 -m pytest sandbox/py-suites/L3-ssi/test_infrastructure_layer.py -q
cd $S/clone/1_blockchain-identity && npx hardhat run scripts/infrastructure_gas.js   # writes into the clone only
mkdir -p $S/old && git -C $FC archive db6c381 cv2x-testbed 2_w3c-ssi-layer | tar -x -C $S/old
```

## Output format (mandatory)

Write your report to `$SCRATCH/audit_scratch/brief-2/REPORT_brief_2.md` and also return it as your final message. Report ONLY what is
wrong, with evidence. No praise, no style or taste preferences, no restating what the repository says.

Severity:
- **high**: a wrong number, verdict or security property in the register, thesis, dashboard or milestone report;
  a check or test that can pass while the thing it certifies is wrong; a false statement about what was verified.
- **medium**: an overclaim, misleading wording, irreproducibility (cannot be regenerated or re-derived from the
  repository), a documented-as-complete item that is incomplete, an inconsistency between two documents.
- **low**: cosmetic or trivially fixable with no effect on a claim.

Sections, in this order:

### Findings
One item per finding, exactly in this shape:

`F<n> | <high|medium|low> | <file>:<line> | <claim in the repo, quoted or tightly paraphrased> | <what is actually true, with evidence: the command you ran and its output, or a quoted line> | <suggested fix>`

Number findings F1, F2, ... in the order you want them read (high first). Give a file:line for every finding
(use the frozen checkout's line numbers; for a document claim give the line of the claim). If a finding
spans several places, list the primary one and name the others in the evidence column.

### Checked and found sound
One line per numbered check of this brief (use the brief's own numbering, e.g. "C7: sound, because ...") that you
executed and that did not produce a finding, with the one-line evidence (the value you recomputed and the value
in the repository). Checks that produced findings are not repeated here.

### Not checked (and why)
Every numbered check you did not complete or could only partly complete, and why (tool missing, would require
a long run, ambiguity, out of time). Also list anything you noticed outside this brief's scope that you did not
pursue; the coordinator will route it.

Do not pad. A short report with five well-evidenced findings is better than a long one with speculation. Mark
anything you could not confirm as "unconfirmed" and say what would confirm it.
