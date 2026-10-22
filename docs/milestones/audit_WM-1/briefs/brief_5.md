# Brief 5 - The code nobody has audited: Python suites outside L3, the contracts, and the test suites that certify them

## 1. Scope

**Why this brief exists.** The pass-11 review covered only passes 9-10. It did not look at the Python suites
outside `sandbox/py-suites/L3-ssi`, at the Solidity contracts, or at the tests and security harness that back
the register's security and conformance rows. WM-1's headline status ("ALL OK", 536 Hardhat tests, 291 Python
tests, W3C score 94.3 %, 43/43 attack scenarios, 335/336 external DID suite) rests on exactly that code. WM-1
did not change the contracts (`git diff db6c381 291bbca -- 1_blockchain-identity/contracts` is empty) but its
results of record, the infrastructure verifier's trust root, and thesis crux C1/C5/C6/C8 all depend on them.

**Question this brief answers:** do the tests and checkers that certify the unaudited code have the power to
fail, and does the code have the security and conformance properties the register and thesis claim?

**Code and data**
- Python: `2_w3c-ssi-layer/` (all: `did-resolution/did_resolver.py` + tests, `verifiable-credentials/*.py` + tests, `mobi-vid/*.py` + tests), `cv2x-testbed/identity/` (providers: `erc1056_provider.py`, `mobi_vid_provider.py`, `centralized_*`, `freshness.py`, `lifecycle_backends.py`, `comparison_framework.py`, `w3c_verifiable_credentials.py`, `standard/`), `cv2x-testbed/tests/`, `cv2x-testbed/scripts/w3c_compliance_checker.py` (the 94.3 % score), `sandbox/py-suites/L3-ssi` (other than `test_infrastructure_layer.py`) and `L4-exemplar-interactions`.
- Solidity: `1_blockchain-identity/contracts/**` (nine standards; `ERC1056/EthereumDIDRegistry.sol` is the I4 target; `MOBI/`; `ERC1155/`; `CVINCombined/`; `ERC4337/`; `ERC721/`; `ERC725*`; `ERC735`; `LSP8`), their copies `cv2x-testbed/contracts/`.
- Tests and harnesses: `1_blockchain-identity/test/**` (L1 mechanisms, L2 per-option, security), `1_blockchain-identity/scripts/security_scenarios.js` and `benchmark_gas.js`, `1_blockchain-identity/benchmarks/`, `sandbox/options/*/demos`, `sandbox/grand/`.
- Conformance evidence: `docs/conformance/` (external W3C DID test-suite runs: `suite-run/`, `reports/**`, `implementations*/`), `docs/conformance/W3C_DID_TEST_SUITE.md`.
- Claims about them: register rows #4, #21-#28, #32, #33, #37-#43; `docs/DEFECT_LOG.md` D1-D27 and §C (open items); `docs/THREAT_MODEL.md`; `docs/FEATURE_ASYMMETRY_MATRIX.md`; thesis chapters 5-6 sections on security, conformance, privacy (C7), MOBI (C6).

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
clone locally into your scratch directory: `git clone -q $SCRATCH/audit_d61a284 $SCRATCH/audit_scratch/brief-5/clone && ln -s $SCRATCH/audit_d61a284/1_blockchain-identity/node_modules $SCRATCH/audit_scratch/brief-5/clone/1_blockchain-identity/node_modules`
(the clone is yours to modify; old commits are reachable in it with `git -C $SCRATCH/audit_scratch/brief-5/clone show <rev>:<path>` or `git archive`).

**Hard rules for commands.**
- Write only to your scratch directory `$SCRATCH/audit_scratch/brief-5/` (create it).
- Long experiments (the 30-run sweeps of ~7-30 min: `run_infra_stats.py`, `run_v2v_stats.py`, `run_verify_scaling.py`, `npm run metrics`, `benchmark_scaling.js`, the I3 revocation sweep) must NOT be re-run. Recompute from the committed JSON instead.
- Allowed short runs: a single seed of the harness (seconds), the pytest suites, `npx hardhat test` (about 25-60 s) and single Hardhat scripts, the document generators in `--check` mode, `git`, `grep`, `python3 -I`, `node`. A Hardhat node, if you need one, must use a non-default port (for example 18548) and you must kill it by recorded pid.
- When running `cv2x-testbed/sumo/sumo_identity_integration.py` ALWAYS pass `--results $SCRATCH/audit_scratch/brief-5/<name>.json` (its default overwrites a committed file). Run it from a clone, not from `$SCRATCH/audit_d61a284`.
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

Work in a clone. For anything needing a chain use Hardhat in-process or a node on a port you start (kill it by pid).

**C1. Run everything, count skips.** In a clone: `npx hardhat test` (record passing / pending / failing and the list of pending tests with titles - the claim is 536 / 23), `python3 -m pytest 2_w3c-ssi-layer cv2x-testbed/tests -q -rs` with a Hardhat node on your own port and the environment variables of `.github/workflows/w3c-compliance.yml` (job `python-full-suite`), then `sandbox/py-suites/run.sh -rs`. Compare totals with 291 and the CI "no skips" rule. List every skipped / xfailed / deselected test and the reason. Run the Python suites once WITHOUT a node: how many tests skip silently and what does the exit code say?

**C2. Test power audit of Python suites.** For every test file outside `L3-ssi/test_infrastructure_layer.py`, build a table: file | tests | tests with at least one assertion on a computed value | tests whose only assertion is truthiness / key presence / `is not None` / `len(x) > 0` | tests that catch a broad exception and pass | tests that mock or stub the unit they claim to test | tests that compare a function's output to the same function. Use a script (`ast`) to find the first four, then read a sample of at least twenty tests. Report suites whose passing does not constrain behaviour, naming the claim each is cited for (register row, DEFECT_LOG regression, grand report).

**C3. Mutation spot checks on security-critical Python.** Mutate in the clone and re-run the relevant suite; every mutant should fail some test. At least 15 mutants: `vc_verifier.py` (skip signature verification; skip expiry; skip issuer trust; skip revocation; accept `issuer` mismatch; accept any proof type); `vc_issuer.py` (sign over a different digest; omit the subject id); `freshness.py` (window comparison direction; skip replay insert; off-by-one in k); `mobi_vid_provider.py` `verify_message` (use the key embedded in the message instead of the registration record: this is defect D11, a fixed High; does a test fail when the fix is reverted?); `erc1056_provider.py` key resolution (return the placeholder key: D4); `did_resolver.py` (omit controller, wrong chain id, hex chain id: D27); `birth_certificate.py`, `lifecycle_events.py`, `vin_cipher`. Report survivors with the diff.

**C4. The 94.3 % W3C compliance score.** Read `cv2x-testbed/scripts/w3c_compliance_checker.py` fully. Run it in a clone and reproduce the score; the CI floor is 94.0. For the weights and the check list: how many checks are (a) assertions on source text (string/regex presence in files), (b) self-referential (the checker generates the object and validates it with rules it also wrote), (c) executing the real code path with a negative case, (d) always PASS or a constant? Sample 20 PASS checks and decide whether each could fail if the property were absent. Check the "two documented deviations counted FAIL by design" claim, and whether the percentage is a unit-weighted or category-weighted mean (change one weight and see). Compare the chapter/register wording ("conformance", "compliant", "lifts to DID/VC conformance - H2") with what the score measures (register row #4 and review-2's decision that the checker is "structural"). Report any wording that presents the structural score as conformance.

**C5. External W3C DID test suite (335/336).** Read `docs/conformance/W3C_DID_TEST_SUITE.md`, `suite-run/` (`run-cvin.js`, `run-cvin-cli.js`, `cli-to-report.js`, `default.js-registration.diff`), the `reports/**` directories and their `jest-control` vs `jest-cvin` outputs. Recompute 335/336 from the committed Jest JSON/logs for the registry-minted `did:ethr` run and the fixture run; identify the one failure and its stated cause. Determine: (a) what the registration diff changes in the suite (does it disable or loosen any test? a suite run with edited assertions is not the W3C suite); (b) what the "control" run is and whether it fails when it should (a control that cannot fail proves nothing); (c) whether the DIDs under test are produced by the system's resolver or by a fixture written to pass; (d) whether the version/commit of the upstream suite is pinned and recorded; (e) whether `reports/` timestamps/commits are consistent with the claimed re-runs after the 2026-10-04 contract fixes. Report anything that makes "335/336" a statement about less than the whole suite or about a different object than the thesis implies.

**C6. DID resolver.** `did_resolver.py`: does `did:ethr` resolution read the chain (register/thesis wording says resolution "with blockchain lookup" is only legitimate for M2) or build the document from the address and static data (WM-2 C1 says `_resolve_ethr` "reads the chain instead of the static document" is still to do)? List every chapter/register/README sentence about resolution and check each against the code. Verify defect D27 (hex chain id in `blockchainAccountId`) status and where the thesis cites the resolver output. Check `docs/figures/resolution_latency_M0.json` and the register row that cites it: what is timed (document construction from an address) and is it presented as "resolution latency" without that qualification anywhere?

**C7. Verifiable Credentials layer.** Read `vc_issuer.py`, `vc_verifier.py`, `vc_holder.py`, `vc_schemas.py`. Check: what is signed (canonicalisation: JCS / URDNA2015 / ad-hoc JSON dump?), proof `type` strings (are they registered W3C/DIF suite names, or invented?), `@context` handling, `validFrom`/`validUntil` vs `issuanceDate`/`expirationDate` semantics and timezone handling (naive datetimes), revocation list integrity (can the holder or an attacker alter the list; is the status list signed), replay of presentations (challenge/domain), whether `verify_credential` checks that the proof was made by the issuer's key resolved from the issuer DID or only by a key supplied with the credential. Write at least six negative PoCs in `$S` (tampered subject, swapped issuer, expired, not-yet-valid, revoked, wrong-type proof) and report any accepted.

**C8. Providers and the baselines (fairness of the comparison).** The headline comparison pits blockchain-rooted identity against a centralized registry and an "IEEE 1609.2-style PKI". Read `centralized_provider.py`, `centralized_vehicle_registry.py`, and the PKI baseline in `comparison_framework.py` / `cv2x-testbed/tests/test_pki_certificate_chain.py`. Check: does the PKI baseline really verify a certificate chain with signatures (and revocation / CRL handling) or compare strings; does the centralized baseline's lookup include any I/O or network; does each baseline implement the same operations the blockchain options are charged for (creation, rotation, revocation, resolution); is any asymmetry hidden in the register's comparison rows (#21, #27, #32, #37, #39)? Report asymmetries that favour the thesis hypotheses and are not stated as limitations.

**C9. Verification of fixed defects: do the regression tests fail on the old code?** `docs/DEFECT_LOG.md` §A/§B lists High defects "fixed `<commit>` (+ regression test)": D1, D4, D6, D7, D10, D11, D11b, D13, D18, D21, D22, D25a/b (and D2, D9, D8-first-three). For each, (1) locate the fix commit and the fixing lines, (2) find the regression test, (3) in the clone, revert the fix (checkout the parent version of the contract / provider file only) and run just that test: it must fail. Report fixes without a test, tests that still pass on the old code (a check that can pass while wrong), and fixes that are not in the code at `d61a284` (reverted by the merge of the lineages?). Because the two lineages were merged in WM-1's lead-up, also check that the fixes of BOTH lineages survive (K-1, K-3, K-4, K-6, K-8, K-15 per the option READMEs).

**C10. Open defects and exploitability.** For the open items in DEFECT_LOG §C (D8 rest, D12 rest, D15, D16 rest, D19, D20, D23, D24, D25c, D26) and the carried review-2 item `attestEvent` (WM-2 C2: "restrict `attestEvent` to the vehicle's owner and delegates"), write a minimal Hardhat script or test in the clone that demonstrates each is exploitable as described (or is not). Then search the thesis chapters, README, CAPABILITIES, the dashboard and the feature-asymmetry matrix for statements that contradict an open defect (for example "only the owner can ..." or "revocation is final" where D16/D26 say otherwise). Report contradictions as high if they concern a security property.

**C11. Static review of the nine standards' access control.** For each contract in `contracts/**` list every external/public state-changing function with its modifier / `require` guard in a table (script: parse the ABI from `artifacts` after `npx hardhat compile`, and read the source). Flag: functions with no guard that modify identity state; `tx.origin`; `ecrecover` without a zero-address check or low-s check (D22) in meta-transaction functions (`setAttributeSigned`, `changeOwnerSigned`, ... in `EthereumDIDRegistry.sol` and the vehicle variants); nonce handling and replay across chains (chain id in the signed digest?); `delegatecall`/`call` with user-supplied targets (ERC-725 family; D24); reentrancy in token transfers (ERC-721/1155 `_checkOnERC*Received`) with state written after the external call; unchecked arithmetic in `unchecked` blocks; `block.timestamp` use for validity; `selfdestruct`; initialisation functions callable by anyone; upgradeability. Run `npx hardhat compile` and report every compiler warning. If Slither or Mythril is not installed say so (do not install from the network if blocked).

**C12. Contract size and deployability.** `hardhat.config.js` sets `allowUnlimitedContractSize` (condition tag M1). From the compiled artifacts compute deployed bytecode size of every contract; any above 24,576 bytes (EIP-170) cannot be deployed on a real network, so its M1 deployment gas and any Sepolia plan are not transferable. Report such contracts and every register/thesis sentence that compares deployment costs across standards without that caveat. Also check the optimizer settings used for the gas results (optimizer 200 + viaIR + cancun) against the CI job and the register's M1 definition, and that `cv2x-testbed` compiles the MOBI copies with solc 0.8.20 (CI header) while the main project uses 0.8.24: are the byte-identical Solidity files compiled differently, and which build do the testbed experiments (#21, #22) use?

**C13. Security harness: strict or lenient reverts?** Read `scripts/security_scenarios.js` (43 scenarios claimed passing, register #28 / "strict harness 0 unexpected reverts") and `test/L2-identity-system/security/*.test.js`. For every scenario that expects a revert: does it assert the specific revert reason / custom error, or any revert (a revert from a wrong-nonce, insufficient-funds or ABI mistake would also "pass")? Count scenarios with a specific reason vs generic `.to.be.reverted`. For ten attack scenarios, modify the target contract guard in the clone (remove the `require`) and check the scenario flips to FAIL. Also check that the scenarios cover the attacks the threat model lists for the contracts and name the ones that are not covered.

**C14. Hardhat test quality.** `git grep -n -E "\.only\(|\.skip\(|xit\(|xdescribe\(|it\.skip|describe\.skip|this\.skip|pending" -- 1_blockchain-identity/test sandbox` and the 23 pending tests: are any pending tests the only coverage for a registered security claim? Count tests with no assertion, tests asserting only `.to.emit(contract, "Event")` without args, tests inside `try/catch` that swallow assertion errors, and tests that assert a gas number (these make results of record fragile - open item N-18). Run the test suite twice and diff the L1 gas output; report cells that differ (the register says gas is deterministic).

**C15. Nine-standard gas benchmark (rows #25, #26, #43).** Recompute three register cells from `4_comparison-framework/results/gas_benchmark.json`; re-run `npx hardhat run scripts/benchmark_gas.js` in the clone (short) and diff against the committed file (cell by cell). Review the benchmark's operation definitions: for each of the nine standards what call counts as "create", "update", "add claim", "revoke", "transfer"; is the same semantic operation measured (e.g. ERC-1056 "create" = 0 / first attribute set vs ERC-721 mint with metadata); are first-write (cold SSTORE) costs included for some and not others; are gas figures including the 21,000 intrinsic cost; is a deployment amortised. The thesis claim "ERC-735 now heaviest create" (N-7) and "minimal-state standards an order of magnitude cheaper" (crux C1) must follow from the definitions: test the claim under a different but defensible operation definition and report if the ranking flips.

**C16. Privacy and cryptography in the MOBI/VIN layer.** `2_w3c-ssi-layer/mobi-vid/` (`vin_cipher`, `birth_certificate.py`): cipher and mode, key derivation, nonce/IV generation and reuse, deterministic encryption linking the same VIN across messages, authentication (AEAD or not), key storage, timing; the pseudonym experiments (`scripts/experiment_pseudonym_pool.js`, register #38 "M5") versus the claims in crux C7 and chapters 5-6 on linkability. Write a PoC for any cryptographic misuse (for example the same ciphertext for the same VIN twice, ECB-like patterns, nonce reuse).

**C17. Demos (92, 1,752 steps).** Choose ten demos from different options in `sandbox/options/*/demos`. For each: do the steps assert (throw on mismatch) or only log; is "flagged" a failure or an observation; change a contract guard or an expected value in the clone and check the demo fails. Check the arithmetic of "1,752 steps" and "62 flagged" from `sandbox/grand/report/demos.json`, and that coverage tables in the option READMEs ("20/20, 50/50, 21/21, 57/57") equal the demo manifests (recount public functions from ABIs vs functions named in demo steps).

**C18. Duplicate and divergent code.** `cv2x-testbed/contracts/*.sol` vs `1_blockchain-identity/contracts/MOBI/*.sol` (CI checks byte identity for three files only) and `1_blockchain-identity/_research-copies/**` (copies of ERC contracts: are any imported or tested, or can a reader mistake them for the code under test?); `sandbox/lib`, `sandbox/options/*` adapters vs `1_blockchain-identity/benchmarks/adapters`; two `w3c_verifiable_credentials` implementations (testbed `identity/` vs `2_w3c-ssi-layer/verifiable-credentials`): which does each experiment import; if they diverge, a result may certify one while the thesis describes the other. Report divergences relevant to a claim.

**C19. Threat model versus code.** `docs/THREAT_MODEL.md`: list each stated threat and its mitigation/"covered by" pointer; for at least ten, find the code and the test; report pointers that do not resolve or do not demonstrate the mitigation, and threats applicable to the code but absent from the model (contract-level: front-running of `createVehicleDID`, griefing, owner key loss with no recovery, issuer key compromise, oracle/VIN-registry trust).

**C20. The previous review's blind spots, by chapter.** Chapters 1-4 and 6-7 are covered for numbers by Brief 1. Here, for chapters 5-6 sections about security properties of contracts and VC layer, list each property claimed (for example "only the owner can transfer", "revoked credentials cannot be re-activated", "key rotation invalidates old signatures", "replay is rejected") and find the test or scenario that exercises it and the contract line that enforces it; report properties with no executable evidence.


## 3. Commands you may run

### Commands you may use (read-only on the frozen checkout; writes only under `$SCRATCH/audit_scratch/brief-5/`)
```
FC=$SCRATCH/audit_d61a284
S=$SCRATCH/audit_scratch/brief-5
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
cd $S/clone/1_blockchain-identity && npx hardhat compile 2>&1 | tail -40 && npx hardhat test 2>&1 | tail -60
cd $S/clone/1_blockchain-identity && npx hardhat node --port 18548 > $S/node.log 2>&1 & echo $! > $S/node.pid   # kill $(cat $S/node.pid) afterwards
cd $S/clone && CV2X_TEST_RPC_URL=http://127.0.0.1:18548 python3 -m pytest 2_w3c-ssi-layer cv2x-testbed/tests -q -rs
cd $S/clone && sandbox/py-suites/run.sh -rs
cd $S/clone && python3 cv2x-testbed/scripts/w3c_compliance_checker.py
cd $S/clone/1_blockchain-identity && npx hardhat run scripts/security_scenarios.js   # writes into the clone only
cd $S/clone/1_blockchain-identity && npx hardhat run scripts/benchmark_gas.js        # ditto
git -C $FC log --oneline -S"<snippet>" -- <file>    # find a fix commit; revert in the clone with: git -C $S/clone show <parent>:<path> > <path>
```
Note: some pytest suites in `cv2x-testbed/tests` need compiled contracts from `1_blockchain-identity/artifacts/contracts/MOBI` (see the `python-full-suite` job in the workflow for the exact symlink and environment variables).

## Output format (mandatory)

Write your report to `$SCRATCH/audit_scratch/brief-5/REPORT_brief_5.md` and also return it as your final message. Report ONLY what is
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
