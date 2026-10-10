# Brief 1 - Claims, numbers and thesis chapters versus the register and the committed data

## 1. Scope

**Question this brief answers:** is every number, verdict and wording that WM-1 put into the claim register,
the crux register, the dashboard, the README-level documents and the thesis chapters true to the committed
result files, and does any chapter claim more than a V (verified) row supports?

**Documents and data**
- `docs/MEASUREMENT_CONDITIONS.md` (the register). Primary: rows #44-#48 (infrastructure messaging, new in WM-1). Also every row WM-1 edited (`git diff db6c381 d61a284 -- docs/MEASUREMENT_CONDITIONS.md`): at least #6, #25, #26, #34-#36, #40, #41, #43. Sample at least ten further rows that cite a result file.
- Result data: `cv2x-testbed/sumo/results/infrastructure_stats.json`, `infrastructure_revocation.json`, `v2v_latency_stats.json`; `4_comparison-framework/results/infrastructure_gas.json`, `infrastructure_gas_run1.json`, `gas_benchmark.json`, `scaling_*.json`; `1_blockchain-identity/results/metrics/latest/`.
- Pre-registration and design: `docs/design/INFRASTRUCTURE_PREREG.md`, `docs/design/INFRASTRUCTURE_MESSAGING.md`.
- Generated documents: `docs/thesis/cruxes.yaml`, `docs/thesis/CRUX_REGISTER.md`, `docs/figures/dashboard_snapshot.json`, `docs/figures/results_dashboard.html`, `docs/figures/dashboard_template.html`, `docs/testing/stale_numbers.yaml`.
- Thesis chapters `docs/thesis/chapter1-introduction` ... `chapter7-conclusion` (chapter 5 §5.4.1 and §5.7 are new/edited in WM-1; chapters 1, 4, 6, 7 were NOT reviewed by anyone yet; chapters 2 and 3 only where they state what was done or measured), `docs/thesis/README.md`.
- Top-level documents that quote numbers: `README.md`, `CAPABILITIES.md`, `INVENTORY.md`, `QUICKSTART.md`, `COMPOSITION.md`, `MASTER_UPDATE.md`, `PROJECT_SUMMARY` (`docs/PROJECT_SUMMARY.md`), `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md`.
- The milestone report's own numbers: `docs/milestones/WM-1_REPORT.md` §0, §2 (size of change), §4, §5.2, §6, §10.
- Commits: `db6c381..291bbca` and `3e19e72`, `44dc926`, `d61a284`.

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
clone locally into your scratch directory: `git clone -q $SCRATCH/audit_d61a284 $SCRATCH/audit_scratch/brief-1/clone && ln -s $SCRATCH/audit_d61a284/1_blockchain-identity/node_modules $SCRATCH/audit_scratch/brief-1/clone/1_blockchain-identity/node_modules`
(the clone is yours to modify; old commits are reachable in it with `git -C $SCRATCH/audit_scratch/brief-1/clone show <rev>:<path>` or `git archive`).

**Hard rules for commands.**
- Write only to your scratch directory `$SCRATCH/audit_scratch/brief-1/` (create it).
- Long experiments (the 30-run sweeps of ~7-30 min: `run_infra_stats.py`, `run_v2v_stats.py`, `run_verify_scaling.py`, `npm run metrics`, `benchmark_scaling.js`, the I3 revocation sweep) must NOT be re-run. Recompute from the committed JSON instead.
- Allowed short runs: a single seed of the harness (seconds), the pytest suites, `npx hardhat test` (about 25-60 s) and single Hardhat scripts, the document generators in `--check` mode, `git`, `grep`, `python3 -I`, `node`. A Hardhat node, if you need one, must use a non-default port (for example 18548) and you must kill it by recorded pid.
- When running `cv2x-testbed/sumo/sumo_identity_integration.py` ALWAYS pass `--results $SCRATCH/audit_scratch/brief-1/<name>.json` (its default overwrites a committed file). Run it from a clone, not from `$SCRATCH/audit_d61a284`.
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

**C1. I1 from per-run data.** `infrastructure_stats.json` has a `per_run` block. Recompute, per run, warm SPaT verify median / warm SSI-BSM verify median, then the median of the 30 ratios and a bootstrap 95 % CI. Compare with register #44 and report §4.1 (1.096, [1.091, 1.101]) and the `I1` block. If the CI cannot be reproduced from stored data or the method is not stated, say so. State which statistic the pre-registration (§2 of the prereg) names as the verdict statistic and whether the file's `verdict` uses that one.

**C2. I1 component medians.** Recompute "SPaT warm 0.182 / BSM warm 0.166 / SPaT cold 0.477 / SPaT sign 0.255 ms (medians of run medians)" from `per_run`. Check that 0.182/0.166 = 1.096 is consistent with the stated ratio-of-medians vs median-of-ratios distinction.

**C3. Pre-registered bands unchanged.** `git log -p --follow docs/design/INFRASTRUCTURE_PREREG.md`: confirm that the original §1-§3 text (pass/fail bands I1 [0.80, 1.20] / > 2.0, I2 definition, I3 bound, I4/I5 "reported") was not edited after the lock commit `cfbdcbc`, only appended to. List every textual change to the original sections. Then judge amendments A1-A4: does any amendment make a PASS easier (A1 sets I1 at k = infinity; A3 redefines I5; A4 extends I2)? Quote the amendment text and say whether the register's "pre-registered ... verdict PASS" wording discloses that.

**C4. I2.** In the JSON, list the 13 registered checks and their expected reasons, the per-run outcomes and `totals`. Confirm 13/13 rejected for the expected reason in 30/30 runs, and recompute "0 legitimate SPaT rejected of 138,895". Define from the harness code what "legitimate SPaT" counts (which runs, receivers, incl. or excl. post-revocation messages). Check register #45's lettering (a)-(j) + three warm variants = 13 against the JSON ids.

**C5. I3.** `infrastructure_revocation.json`: recompute max accepted after revocation per k (0 / 4 / 24 / 100), runs reaching the bound (30 / 16 / 6), mean totals (0 / 6.73 / 40.97 / 496.23) and "3-14 vehicles held rsu_1 in cache". Then argue whether "PASS (<= k-1)" can fail at all: the counter in `cv2x-testbed/sumo/infrastructure_layer.py` re-checks every k-th presented message, so the bound is structural. If the bound is a tautology of the implementation, the register wording "pre-registered ... verdict PASS" and the report's "Every pre-registered verdict passes" overstate evidential content; say so with the argument. Also check the k = infinity value 100 (what limits it to 100?).

**C6. I4 gas.** Compare register #47 and report §4.1 against `infrastructure_gas.json` and `infrastructure_gas_run1.json` cell by cell (five operations, two runs, ranges). Check "identity creation 0", "52,594 equals the bare ERC-1056 create of #6" (find #6's value and its source file) and the "+-12 gas = one calldata zero byte" explanation (EIP-2028 4 vs 16 gas: is a 12 difference consistent with exactly one byte? Does a fresh random key change the zero-byte count by exactly one in both runs for all five operations, or could the difference be something else, such as cold/warm storage? The register admits the mechanism is not isolated; check that no other document states it as established). Check the `commit` and `dirty` fields in the JSON against "commit `f1f9e37`, run-stamp dirty false".

**C7. I5.** Recompute 0.886 [0.879, 0.913] and TMC hop 0.464 [0.456, 0.484] from `per_run`. Comment on the asymmetric CI. Check the definition ("sum of four per-run medians") against `run_infra_stats.py`.

**C8. Run identity of the rows.** For #44-#48 the register states `tree_clean` / `code_clean` / `dirty` values (#44 both true, #46 `tree_clean` false, #47 dirty false). Read the `environment` block of each cited JSON and compare. For each of the five result files, run `git log --oneline -- <file>` and `git diff <commit-in-file> HEAD --stat -- cv2x-testbed/sumo cv2x-testbed/identity 2_w3c-ssi-layer 1_blockchain-identity/scripts 1_blockchain-identity/contracts 1_blockchain-identity/hardhat.config.js`: has any producing code changed since the commit the file claims to come from? (Pass 11 re-ran at `f1f9e37` but committed at `601e1de`.)

**C9. Host / comparability claim.** #44 says absolute values are not comparable with #27 (kernel `fc-v80` vs `fc-v64`, library set). Compare the `environment` blocks of `infrastructure_stats.json` and `v2v_latency_stats.json`. Does any chapter or the dashboard nevertheless put SPaT (#44) and BSM (#27) absolute values side by side, or compare #44's warm BSM 0.166 ms with #27's warm BSM value? Find #27's value; if they differ by more than the CI, the "same code path" in two result files gives different numbers and the text must say why.

**C10. Register status counts.** Report §0 says rows 43 -> 48 and V/S/E/B 27/8/7/1 -> 31/10/7/0. Parse the status column of the register at `db6c381`, at `291bbca` and at `d61a284` (`git show rev:docs/MEASUREMENT_CONDITIONS.md`). Recompute the counts; list every row whose status changed during WM-1 and check each change is justified in the row text and in an after-action report. 43 + 5 new V rows cannot give V = 31 from 27 without status changes in old rows: identify them.

**C11. Crux register.** Recompute, from the register status column and `cruxes.yaml` `evidence_rows`, the number of V rows per crux and compare with report §10 (7, 5, 5, 2, 2, 2, 1, 3) and `CRUX_REGISTER.md`. Check the report's "0 of 8 cruxes with no V evidence" and each crux's "state" (partial) against whatever definition `make_dashboard_data.py` uses. Read the C3 claim sentence in `cruxes.yaml` ("about 10 % more", "13 registered attacks ...") against the data. C4: the report says #46 was "considered and excluded (count, not latency)" but C3 and the register cite #46 for revocation: is it consistent that revocation freshness (C4) has 2 V rows while its direct experiment is excluded? Does any crux claim a hypothesis (H1-H5) mapping that is missing (C3 has `hypotheses: []`; plan P4.2 promised a thrust/hypothesis map)?

**C12. Dashboard.** Run `python3 docs/figures/make_dashboard_data.py --check` in a clone. Independently verify at least eight numbers in `dashboard_snapshot.json` (choose from different panels, including the I1-I5 panel and the test-counts panel) against their `source` and `register` fields. Open `dashboard_template.html` and `results_dashboard.html`: find any number literal typed into the template or page that is not generated (the claim is "no number of its own"). Check that the infrastructure panel shows the same definitions as #44-#48 (I2 = 13 checks; I5 = sum of operation costs, not a latency).

**C13. Chapter 5 §5.4.1 and §5.7.** Extract every number in the new text and map it to a register row and a JSON field. Flag any number without a V row, any rounding that changes meaning, and any verb stronger than the evidence ("secures", "end to end", "costs exactly", "2.4 s of trust", "clean tree"): the report says these were rewritten in pass 11; search `docs/` (all of it, including thesis chapters, README, CAPABILITIES, INVENTORY, QUICKSTART, PROJECT_SUMMARY, the dashboard template, design docs and the figures' captions in `cv2x-testbed/sumo/results/figures`) for survivors with `git grep -n -i -E "secur(e|es|ed)|end[- ]to[- ]end|exactly|guarantee|prove[sd]?|clean tree"` and judge each hit that concerns WM-1 results.

**C14. Chapters 1, 4, 6, 7 (never reviewed).** For each chapter, extract every quantitative or verification statement (numbers with units, percentages, "N of M", "tested", "validated", "verified", "conformant", "secure", "complies"). Build a table: statement | chapter:line | register row | row status | source file value. Report every statement with no register row, with a non-V row presented as established, or whose value differs from the source. Pay special attention to: the W3C compliance score (94.3 %) and the external DID-suite result (335/336), the "94.3 % residual" wording (open item N-6), the sentences naming ERC-735 the heaviest create (open item N-7), "43/43" security scenarios, hypothesis verdicts H1-H5 and the thesis title's scope against what was measured (mock mobility, no radio, no Sepolia, no real SUMO).

**C15. Chapter 4 versus code.** Chapter 4 (implementation) and `docs/design/INFRASTRUCTURE_MESSAGING.md` §7 ("as built") describe the system. Check at least ten concrete statements (function names, contract names, flags, message fields, freshness window 1 s / 0.1 s, the checks the verifier performs and their order, number of standards and contracts, line or file counts) against the code. Report descriptions that do not match.

**C16. Chapters 2 and 3 where they state what was done.** Chapter 3 (methodology) states the measurement rules (N >= 30, 3 discarded warm-ups, median and p95, environment header, M-tags). Check whether the I1-I5 experiments follow them (look in `run_infra_stats.py` for warm-ups discarded, p95 reported, header captured; the register says "median of run medians" only) and whether chapter 3 / the style guide demand p95 for latency rows #44/#48. Report any WM-1 latency row that does not satisfy the rules it cites.

**C17. Stale figures outside the checker's reach.** `docs/testing/stale_numbers.yaml` lists superseded figures; the checker scans tracked Markdown files minus named history files. Grep ALL tracked files (any extension: `.html`, `.json`, `.tex`, `.csv`, `.py` comments, `.yaml`, notebooks, `docs/thesis/appendices`, `docs/figures/*.html|svg`) for each superseded figure and for the counts the report calls current (536, 23, 291, 92, 1,752, 99, 260, 276, 217, 369, 52,170, ~33x). Report any live stale citation. Also list which Markdown files are excluded as "history" and whether any excluded file is cited as current elsewhere.

**C18. Report §0, §2, §6 arithmetic.** Recompute: files changed 175, +38,505 / -23,197 (`git diff --shortstat db6c381 291bbca`); "66 files and +-22,150 lines are the regenerated metrics-harness run"; "50 files are documents"; "28 code files carry +2,446 / -98" (`git diff --numstat`). Recompute "Contracts changed: none" with the exact command in the report, and also for `cv2x-testbed/contracts/`, `1_blockchain-identity/test/` and `hardhat.config.js`. Check "Defect log entries D1-D27 -> D1-D36", "Documents scanned 87", "Result files with a complete stamp 11 of 25 -> 20 of 29" against `docs/testing/STAMP_INVENTORY.md` and by counting the result files yourself.

**C19. Test and demo counts and their commit.** Report §0/§6 and several documents say "536 / 23, 291, 92 demos / 1,752 steps" come from the grand report at `291bbca`. `sandbox/grand/report/GRAND_REPORT.md` says "Generated ... at commit `601e1de`". Check `git log` for that file and what changed in tests between `601e1de` and `291bbca`; confirm or refute "at `291bbca`" and "ALL OK on the closing commit". Cross-check against Brief 3's re-run if available; here only the documents' consistency matters. Also check "Python layers L3 + L4: 260 -> 291" arithmetic against the 31 added infrastructure tests and the count of tests collected by `sandbox/py-suites/run.sh` (which includes `2_w3c-ssi-layer`, so the label "L3 + L4" may be wrong).

**C20. Status V justified?** For #44-#48 the register status is V. The style guide (`docs/STYLE_AND_RIGOUR_GUIDE.md`) and the register legend define what V requires (clean tree, condition tag, source, commit, N, ...). Apply the definition literally to each of the five rows and to the other rows WM-1 touched. Candidates: #46 (whole-tree flag false, F-C accepted by the author), #47 (mechanism not isolated, expectation failed), #48 ("not a path latency"), #34-#36 (harness run whose `dirtyMeasured` flag the report itself says is inert; open item N-19: is a V justified when the clean-tree evidence is the "tree was clean seconds before"?).

**C21. Stamped-evidence chain for older V rows.** For every register row with status V that cites a result JSON with a `commit` field, test whether the producing code (contracts, scripts, harness) changed after that commit (`git diff <commit> HEAD -- <producers>`). WM-1 claims "no gas or sweep cell moved" after re-running four JS producers and that the metrics-harness run of record is unchanged: verify at least three of these by comparing the committed JSON before (`db6c381`) and after (`291bbca`) with a script (diff all numeric leaves; list the cells that moved and by how much, and compare with the "no number moved" statements in report §4.2 and register #25/#26/#34-#36).

**C22. "Verdict" words.** Search the register, chapters and dashboard for "PASS", "FAIL", "falsified", "confirmed", "supports H" attached to WM-1 experiments; check each is a statement the pre-registration allows (verdict rules in prereg §2). Report any hypothesis verdict (H1-H5) that changed or was asserted in WM-1 without a pre-registered rule.


## 3. Commands you may run

### Commands you may use (read-only on the frozen checkout; writes only under `$SCRATCH/audit_scratch/brief-1/`)
```
FC=$SCRATCH/audit_d61a284
S=$SCRATCH/audit_scratch/brief-1
mkdir -p $S
cd $FC && git log --oneline db6c381..d61a284          # the commit range
git -C $FC show <rev>:<path>                            # old versions
git -C $FC diff db6c381 291bbca -- <path>               # WM-1 diff; also 291bbca..d61a284 for pass 12
git -C $FC grep -n "<pattern>" -- <paths>               # search tracked files (does not write)
python3 -I -c '...'                                     # recompute from committed JSON
```

### Brief-specific commands
```
# per-run recomputation skeleton
python3 -I - <<'PY'
import json, statistics as st
d = json.load(open("$SCRATCH/audit_d61a284/cv2x-testbed/sumo/results/infrastructure_stats.json"))
print(d.keys(), d["per_run"][0].keys() if isinstance(d["per_run"], list) else list(d["per_run"])[:3])
PY
git -C $FC diff --numstat db6c381 291bbca | awk '{a+=$1; d+=$2} END {print NR, a, d}'
git -C $FC show db6c381:docs/MEASUREMENT_CONDITIONS.md > $S/register_db6c381.md
python3 $FC/docs/figures/make_dashboard_data.py --check          # may only be run from a clone if it writes
python3 $FC/cv2x-testbed/scripts/w3c_compliance_checker.py       # stdlib-only; run from a clone (writes a report file)
```

## Output format (mandatory)

Write your report to `$SCRATCH/audit_scratch/brief-1/REPORT_brief_1.md` and also return it as your final message. Report ONLY what is
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
