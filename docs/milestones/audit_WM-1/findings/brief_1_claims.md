> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`. Dispositions: after-action report 12 §4.

### Findings

Line numbers refer to the frozen checkout at d61a284. Scratch files are under audit_scratch/brief-1/. The report file `REPORT_brief_1.md` could not be written, because the tool refused to write report files. This message is the full report.

F1 | high | docs/MEASUREMENT_CONDITIONS.md:121 (also :120, :116, :115, :125; docs/thesis/CRUX_REGISTER.md:30,31,148; docs/milestones/WM-1_REPORT.md:163) | Rows #34 and #35 are status V. Their "Merge note (2026-10-09)" says the rows were re-executed as run 2026-10-09T02-09-36Z_7a9a996 and that the earlier run is S. Report §4.2 is titled "Other results re-executed in WM-1 (no number moved)". | The V rows still quote the superseded run 2026-10-04T09-50-29Z_0eef6af. I diffed `1_blockchain-identity/results/metrics/latest/*.json` between db6c381 and 291bbca.
- **Lifetime gas (lifecycle.json):** ERC-1056 1,050,787 -> 1,050,809. ERC-1155 1,150,981 -> 1,261,575 (+9.6 %). ERC-735 5,369,010 -> 5,797,549 (+8.0 %). CVIN-Combined 2,533,978 -> 2,559,537. ERC-721 2,701,239 -> 2,706,685. LSP8 1,505,258 -> 1,508,413. Wrapper 1,025,381 -> 1,025,469.
- **Zero->nonzero SSTOREs:** ERC-735 145 -> 149. ERC-1155 18 -> 21.
- **#34 C1 create:** ERC-735 1,535,776 -> 1,757,881 (+14 %). CVIN 266,995 -> 271,402. ERC-1155 103,913 -> 107,729. ERC-721 399,844 -> 402,567. LSP8 132,515 -> 135,544. ERC-1056 76,808 -> 76,830. ERC-1155 U3 57,147 -> 80,131.
- **Integer cells moved:** crud.json 306, lifecycle.json 132, scale.json 264, batch.json 96, throughput.json 9, analysis.json 9.
- **#35 margins no longer match the current run:** over ERC-1155, 1.10x is now 1.201x. Over ERC-735, 5.1x is now 5.52x.
- **#30 and #29:** both also quote the old run (1,050,787 / 2,701,239 and 76,808 / 399,844).
- **#39:** it says "every gas table byte-identical to #34/#35" and "same meta.measured hashes as #34". `metrics-rpc/latest/tables/lifecycle_gas.md` still shows 1,050,787 / 5,369,010 / 1,150,981, so the claim is false against the current #34/#35 data.
- **Report §4.2:** "no number moved" holds only for the five JS producers. For those I checked 0 numeric cells moved in gas_benchmark, mobi_vid_backends, scaling_lifetime, scaling_marginal and onchain_security. It does not hold for the metrics harness.
- **Rule broken:** guide rule 1.1.4 ("values are never frozen against the code they no longer describe"). | Rewrite the numbers in #29, #30, #34, #35 and #39 and the margin sentences from `latest/`. Correct the §4.2 heading and the "frontier and dominance unchanged" row so they list the moved cells.

F2 | high | docs/testing/stale_numbers.yaml:90 (also docs/testing/check_docs_numbers.py:34, docs/MEASUREMENT_CONDITIONS.md:92 and :120) | Commit 36e0309 removed 1,535,776 from the stale list because "it is the current harness C1 create for ERC-735 (#34)". | This is false. The current harness C1 for ERC-735 is 1,757,881 (`metrics/latest/tables/crud_gas.md`, row C1_create_identity), the same as gas_benchmark.json. The exemption rests on #34, which is itself stale (F1). The checker also skips MEASUREMENT_CONDITIONS.md and CRUX_REGISTER.md as "history" globs (stale_numbers.yaml:11-40). That is why F1 passed the checker ("0 stale figure(s); 89 files scanned").
- **Live uses of the old ERC-735 create figure** (1,535,776 / "1.54 M") outside history: HANDOFF-DATA-COLLECTION-FRAMEWORK.md:130,148,161, docs/DID_METHOD_RUBRIC.md:81, 4_comparison-framework/security-analysis/README.md:125. | Restore 1,535,776 to the list, fix the three live citations, and add a register-vs-result-file number check so the register is not exempt.

F3 | high | docs/MEASUREMENT_CONDITIONS.md:30-31 (rule; also :23 and #47 at :133), README.md:258, CAPABILITIES.md:32,48, docs/thesis/chapter5-results/README.md:58 and :544, docs/thesis/chapter7-conclusion/README.md:76,141,163, docs/thesis/README.md:51, docs/figures/dashboard_template.html:103, QUICKSTART.md:189 | The register rule says gas is "deterministic ... report a single exact value". Other documents say "gas is deterministic and identical on any EVM chain", "Gas is Hardhat-local and deterministic" and "byte-identical, sigma = 0". | WM-1's own I4 result (#47: all five operations differ by exactly 12 between two runs) contradicts these unqualified statements, and the rule was not amended. I ran the I4 operations 12 times in my clone.
- **Spread is wider than ±12:**
  - op1: 52,570 / 52,594 / 52,606.
  - op4: 35,486 / 35,498 / 35,510.
  - op5: 35,026 / 35,050 / 35,062.
- **Ops 2 and 3 never moved in my 12 runs:** 34,050 and 51,754. Their calldata holds no key, only the random RSU address.
- **What the committed pair implies:** the committed pair shifted by 12 on all five operations, including 2 and 3. So the cause there cannot be a key zero byte. The only calldata common to all five is the RSU address.
- **What the repository records:** #47 and chapter 5 §5.4.1 say "a fresh random key" and "mechanism not isolated". The committed JSON records neither address nor key, so the cause cannot be checked from the repository.
- **"52,594 equals the bare ERC-1056 create of #6":** this compares one random draw with a fixed-key benchmark value. I4's own maximum is 52,606. | Amend the rule and the sentences to "deterministic for fixed calldata". Report I4 ranges with the number of runs and the zero-byte counts. Drop "equals" in #47.

F4 | high | docs/thesis/chapter7-conclusion/README.md:122 and :154-155 (also chapter1 :207-210) | H5 is "Supported ... Pareto-optimal among 5/5 backends". The hybrid is "shown to be Pareto-optimal". | Register #36 (V) says "the hybrid is not on the frontier under these criteria". The dashboard snapshot (harness block) has `"cvin": ["erc4337"]` in `dominated_by_all`, meaning ERC-4337 dominates the hybrid on all six criteria. cruxes.yaml C1 gap: "H5's wording must reconcile with it". Chapters 5 (:659-662) and 6 (:270-274) scope the claim to cost x fidelity. Chapter 7 has no qualifier. | Add the scope (fidelity-per-gas plane only; dominated by ERC-4337 on the six harness criteria) to ch7 §7.3 and §7.4.

F5 | medium | docs/MEASUREMENT_CONDITIONS.md:130-134 (#44-#48; #44 and #48 are the latency rows) | Latency rows give median of run medians plus CI only. | The register's own rule (:33-36) and chapter 3 §3.4.3 (:269-272) require median and p95 after 3 discarded warm-ups. `run_infra_stats.py:agg()` computes median, mean and CI only. No p95 and no warm-up discard exist in the driver or the JSON. #27 does report p95. | Add p95 of run medians, or state the deviation in the rows.

F6 | medium | docs/milestones/WM-1_REPORT.md:21 (also README.md:161, docs/figures/dashboard_template.html:356, docs/thesis/cruxes.yaml:38) | "Every pre-registered verdict passes". I3 is "PASS (<= k - 1)". The crux claim is that a cached verifier honours a revoked RSU for at most k-1 messages. | The bound is structural. `infrastructure_layer.py` re-checks when `entry["seen"] % refresh_every == 0`, so at most k-1 messages can pass whatever the data, and the check cannot fail unless the code is edited.
- **Recomputed from per_run, all matching the register:** max accepted after revocation 0 / 4 / 24 / 100; runs at the bound 30 / 16 / 6; mean totals 0 / 6.73 / 40.97 / 496.23; 3-14 vehicles cached.
- **The k=∞ value 100:** it is a duration artefact. rsu_1 sends 10 Hz for the 10 s after revocation.
- **Disclosure gap:** register #46 and chapter 5 disclose that the bound follows from the cadence. The report §0, the README table, the dashboard and the crux claim show PASS without that caveat. | State that I3 is an implementation conformance check, not evidence about revocation latency, and explain the 100.

F7 | medium | docs/PROJECT_SUMMARY.md:39-40; INVENTORY.md:28,53,233; README.md:93; QUICKSTART.md:78; COMPOSITION.md:127; docs/thesis/chapter7-conclusion/README.md:157 | Live status documents cite "219 passing" and "60 passed" (PROJECT_SUMMARY, which docs/INDEX.md:21 names as the status authority). They also cite "217 tests passing" (INVENTORY), a "369-test Hardhat suite" (README), "217-test suite" (QUICKSTART) and "~295 tests" (COMPOSITION, ch7). Report §5.3 says the live stale test-count lines were fixed. | Current counts are 536 Hardhat and 291 Python. The checker misses these lines for two reasons.
- **Patterns do not match:** `\b217 Hardhat` and `\b(217|219|369|386) passing` do not match "217 tests passing" or "369-test".
- **Markers excuse the line:** PROJECT_SUMMARY:39 is excused by the history marker "before" ("47/47 before the merge"). The marker list includes ordinary words (was, before, old, earlier, previous), and each excuses a whole line. | Fix the lines. Require an explicit history tag instead of free words. Add "N tests passing" and "N-test" patterns.

F8 | medium | docs/milestones/WM-1_REPORT.md:31 (also docs/figures/dashboard_template.html:333) | "Python layers L3 + L4 (sandbox) 260 -> 291". | `sandbox/py-suites/run.sh` also runs `2_w3c-ssi-layer`. Collected in my clone: L3-ssi 46, L4 19, 2_w3c-ssi-layer 226, total 291. L3 + L4 is 65. The +31 is correct (31 infrastructure tests). | Relabel the stage in the report and the dashboard.

F9 | medium | docs/design/INFRASTRUCTURE_PREREG.md amendment A4 (also docs/MEASUREMENT_CONDITIONS.md:130-131, docs/thesis/README.md:55, docs/thesis/cruxes.yaml:38, docs/design/INFRASTRUCTURE_MESSAGING.md:98) | I2 is "13 registered checks", described elsewhere as "13 registered attacks". The design §7 says A4 "restored it with 12 further checks". | Original check (d) at cfbdcbc was a SPaT from a vehicle whose credential permits BSM/DENM, which tests the permitted-type check.
- **What (d) tests now:** A4 and the harness (`sumo_identity_integration.py` ~849-855) sign with a vehicle credential from the V2V issuer. It is rejected as `credential_invalid` (untrusted issuer), the same verifier branch as (e). The permitted-type check for a trusted-issuer vehicle credential is no longer tested, and A4 does not say (d) changed.
- **Counts:** there are 10 distinct attacks plus 3 warm variants, not 13 attacks. Going from 7 to 13 checks adds 6, not 12. | State in A4 that (d) changed meaning. Say "13 checks (10 attacks, 3 warm variants)". Fix "12".

F10 | medium | docs/thesis/chapter4-implementation/README.md:64, :193, :470; docs/thesis/chapter5-results/README.md:705 | Chapter 4: Python runtime "`web3` (v7)"; the VC verifier is a "6-stage offline verification pipeline". Chapter 5: ERC-725xy is "by far the most expensive to instantiate". | `2_w3c-ssi-layer/requirements.txt:4` pins `web3==6.11.0`. The `vc_verifier.py` docstring lists 7 stages (it adds "proof"). Chapter 5 :90-91 and register #25 say ERC-735 is the heaviest create (1,757,881 vs 1,680,816, a 4.6 % gap). The other chapter 4 statements I checked match the code (see C15). | Correct the three statements.

F11 | medium | docs/thesis/chapter1-introduction/README.md:195-196 (vs chapter7:118, chapter5:523) | Chapter 1 H1 says "at least 10x cheaper ... for identity creation and update". | Chapter 5, chapter 7 and register #30 restrict H1 to creation ("holds for the create-identity operation only"). On update, ERC-1056 is 35,494 gas vs ERC-721 119,737 (3.4x) and ERC-725 137,096 (3.9x). The hypothesis as stated in chapter 1 is not supported, yet chapters 5 and 7 call H1 "Supported". | Align the chapter 1 wording with the statement that was tested.

F12 | medium | docs/thesis/chapter6-discussion/README.md:204-205,219 | "The residual gap is confined to two specific, documented places"; "the gap is entirely in canonicalization and cryptosuite registration". | 94.3 % is (41 + 0.5)/44. The shortfall includes one PARTIAL DID Core check (w3c_compliance.json: DID Core 14 PASS + 1 PARTIAL; VC 27 PASS + 2 FAIL). The text itself says "apart from that one PARTIAL" two lines earlier. This is open item N-6, still unreworded at d61a284. | Reword as N-6 says.

F13 | medium | docs/figures/dashboard_template.html:353 and dashboard_snapshot.json (v2v block) | The infrastructure panel shows "warm SPaT 0.182 ms vs BSM 0.166 ms". The V2V panel of the same page shows SSI warm 0.153 ms [0.151, 0.154] for the same BSM path. | One quantity has two values with disjoint CIs (0.1648-0.1689 vs 0.1513-0.1538) on one page, with no note in the infrastructure panel. Only register #44 gives the host explanation. I tested the explanation. I ran 6 seeds each of the 58a6513 harness and the d61a284 harness (no --rsu, 20 s, this host). SSI warm median was 0.166 (old) vs 0.168 (new), so the +8 % is host/library, not WM-1 code. That supports the register. The I1 row is also labelled "SPaT fits the BSM budget" with no mention of k=∞ (A1) or the extra-work bias. | Put the host note and the A1 note in the infrastructure panel.

F14 | medium | docs/design/INFRASTRUCTURE_MESSAGING.md:69 and §7 (:98-100) | Design I5 is "end-to-end controller-update -> SPaT latency". The as-built table has a row "Experiments I1-I5 run twice ... results of record at f1f9e37". | I5 as measured is a sum of four operation costs, explicitly not a path latency (A3). I4 as designed ("per-credential issuance cost") is not measured. Section 7 records neither change, only the I2 list. | Add I4 and I5 rows to the as-built table.

F15 | low | docs/milestones/WM-1_REPORT.md:97 | "50 files are documents". | `git diff --name-only db6c381 291bbca` gives 75 .md files (55 outside the harness run), plus 2 html and 4 yaml. No grouping gives 50. | Recount.

F16 | low | docs/thesis/chapter7-conclusion/README.md:148 | "attacks caught at zero false-negative/positive over 1.65 M verifications". | The attack evidence is 5 deterministic injected attacks x 30 runs = 150 rejections. The 1.65 M verifications are benign messages. | Reword to "5 injected attack types, 150/150 rejected; no benign message rejected".

F17 | low | chapters 1, 3, 4, 6 and 7 (no mention of infrastructure results) | Design §6 (I-d) default: a chapter 1 paragraph on scope. Crux C3 examiner question: "Your title says connected vehicles; where is the infrastructure?" | Only chapter 5 (§5.4.1, §5.7) and the READMEs mention the infrastructure results. Chapter 1 scope, chapter 4 (no description of `infrastructure_layer.py`) and chapter 7 (hypotheses, contributions, limitations) are silent. The report lists this as deferred (WM-2 D1), so it is a disclosed gap, not a hidden one. | None beyond the WM-2 item.

### Checked and found sound

- **C1:** sound.
  - Per-run ratios recomputed: median 1.096422, mean 1.096683, CI [1.091188, 1.100856].
  - I reproduced the CI by calling `bootstrap_ci_of_median` with Random(20260719).
  - Prereg §2 names the median of per-run ratios as the verdict statistic, and the file's verdict uses it.
- **C2:** sound.
  - Medians of run medians: SPaT warm 0.18225, BSM warm 0.166, SPaT cold 0.4772, SPaT sign 0.25525.
  - Ratio of medians is 1.0979 against median of ratios 1.0964.
  - The register's 0.182/0.166 = 1.096 holds to rounding.
- **C3:** sound for the original text.
  - The only change to the cfbdcbc text is "*(none)*" replaced by the amendments.
  - A1-A3 are labelled post hoc in the prereg, and A1 is disclosed in #44.
  - No amendment loosens an original band. A1 favours PASS but is disclosed.
  - A3 concerns a row with no verdict. A4 adds checks. The change to (d) is F9.
- **C4:** sound apart from F9.
  - The 13 ids in the JSON match #45's (a)-(j) plus three warm variants.
  - All 30 runs rejected for the expected reason.
  - Totals are 24,000 sent, 138,895 verified, 0 rejected. That counts SPaT only; I2I rejections are not counted.
- **C5:** counts sound (meaning is F6).
- **C6:** cells sound.
  - Run of record: 52,594 / 34,038 / 51,742 / 35,486 / 35,050. run1 is +12 on each.
  - Commit f1f9e37, dirty false and dirtyAnyFile true, as #47 says.
  - The mechanism is F3.
- **C7:** sound.
  - I5 0.88555 [0.8785, 0.9125] and TMC hop 0.4637 [0.45575, 0.48375] recomputed.
  - The definition matches `run_infra_stats.py`.
  - The asymmetric CI comes from a percentile bootstrap on right-skewed run values (max 0.9703).
- **C8:** sound.
  - Stats file: tree_clean and code_clean true.
  - Revocation file: tree_clean false, code_clean true.
  - Gas file: dirty false.
  - No producer code changed between f1f9e37 and d61a284; `git diff --stat` over the producer paths shows only result and figure files.
- **C9:** the register explanation is sound (kernel v80 vs v64, cryptography 41.0.7 vs 49.0.0, A/B above). The presentation issue is F13.
- **C10:** sound.
  - Parsed status column: db6c381 has 43 rows (V27/S8/E7/B1). Both 291bbca and d61a284 have 48 rows (V31/S10/E7).
  - Changes: #26 B->V, #40 V->S, #41 V->S, and #44-#48 new as V.
  - Arithmetic: 27 + 5 + 1 - 2 = 31.
- **C11:** sound.
  - V counts follow the register. C4 uses #32, #37 and #40, and #40 is S, so C4 has 2 V rows.
  - C3 has 5. "0 of 8 without V" follows.
  - C4's claim is covered by #32 and #37 (staleness <= k-1 in 35/35 and 280/280 trials), so excluding #46 is consistent.
  - All of H1-H5 map to a crux. C3 and C7 have no hypothesis by design.
- **C12:** partly sound.
  - `make_dashboard_data.py --check` in my clone printed "snapshot, crux register and page are current".
  - Snapshot values matched their sources: register 48 rows V31/S10/E7, tests 536/291/92/1,752, compliance 94.3 (41/1/2 of 44), conformance 335/336, security 43 DEFENDED / 11 N/A, v2v 0.1528/0.3991, and the I1-I5 block.
  - The template has no typed result numbers beyond the constants block. Line 103's "byte-identical" sentence is typed text (F3).
  - The infrastructure panel's definitions (13 checks, sum of four operation costs) match #45 and #48.
- **C13:** sound for the new text.
  - Every number in §5.4.1 and §5.7 maps to rows #44-#48 and JSON fields.
  - Survivors of "secures", "costs exactly", "2.4 s", "clean tree" in WM-1 documents: none.
  - `experiment_freshness_k.py:518` and its generated .md still say "0.4 s at k = 5, 2.4 s at k = 25" for V2V. That predates WM-1.
- **C15:** partly sound. Ten or more statements checked.
  - Matching the code: 10 schemas, 11 event types, NONE+8 roles, 4 DID methods, 28 VC tests, 9 cipher tests.
  - Matching the code: freshness 1.0 s / 0.1 s, the verifier's order and reasons, RSU positions, 1 s and 5 s periods, contract file names.
  - Mismatches are F10.
- **C16:** the environment header is captured before the runs and N = 30 holds. The p95 and warm-up gap is F5.
- **C18:** sound apart from F15.
  - 175 files, +38,505 / -23,197.
  - 66 harness files, +22,153 / -22,154.
  - 28 code files, +2,446 / -98.
  - Contracts, `1_blockchain-identity/test/`, `hardhat.config.js` and `cv2x-testbed/contracts/`: empty diff.
  - Defect log D1-D36 (37 entries with D11b; 28 at db6c381). Stamp inventory "20 of 29".
  - "87 files scanned" reproduced by running the checker at 291bbca in my clone (89 at d61a284).
- **C19:** sound in substance.
  - GRAND_REPORT.md says "Generated ... at commit 601e1de". It was committed in 291bbca.
  - The diff 601e1de..291bbca touches only report and docs files, so the code and tests are identical.
  - "At 291bbca" means the file's commit; the run was at 601e1de. The dashboard cites 601e1de.
  - The "L3 + L4" label is F8.
- **C21:** partly sound.
  - "No gas or sweep cell moved" holds for the five JS producers (0 numeric leaves moved).
  - It does not hold for the metrics harness (F1).
  - For #27, the sumo, identity and resolver code changed after commit 58a6513, but my same-host A/B shows no effect on BSM warm (0.166 vs 0.168).
- **C22:** sound. PASS and FAIL are attached to WM-1 experiments only for I1-I3, and only as the prereg and A4 allow. No H1-H5 verdict changed in WM-1 without a rule.

### Not checked (and why)

- **C14 (chapters 1, 4, 6, 7):** done by sampling, not exhaustively.
  - Read: chapter 7 in full, the chapter 1 hypotheses and contributions, chapter 4 component statements, and chapter 6 §6.4 and §6.5.
  - Not read line by line: chapter 6 §6.1-6.3 and §6.6 onward, chapter 1 §1.1-1.3, chapter 4 §4.5.
  - The 94.3 % score (41/1/2 of 44; DID Core 14/15; VC 27/29) matches w3c_compliance.json.
  - 335/336 matches the conformance block in the dashboard snapshot, and 43/43 matches attack_results.json. I did not open the external suite reports (Brief 5).
  - N-7: one residual contradiction found (F10).
- **C17:** the stale-figure scan ran the yaml patterns over all tracked non-binary files, plus test counts in top-level documents.
  - Superseded figures remain in docs/artifacts/*.html (52,178; 542,429; 1,704,992; ~33x; 93.2 %; "3 injected attacks").
  - They also remain in docs/figures/verification_dashboard.html, results_snapshot.json and make_review_figures.py (328/441, 93.2 %).
  - These look like dated snapshots, and ARTIFACTS_MANIFEST.md calls the dossiers local files. Nothing in the files marks them historical, and I did not find them cited as current.
  - Count phrasings outside my patterns may remain.
- **C20:**
  - Applying the V definition literally: #44 and #45 meet it.
  - #46 meets it under guide rule 1.1.6 (code_clean true, whole-tree flag false).
  - #47 and #48 meet it as measurements.
  - #34-#36 as V is not justified by their own text (F1). I did not re-derive N-19.
- **Register row sampling:** I read #4, #24, #25, #27, #28, #29-#32, #34-#39. #21, #23 and #33 only partly; I did not re-derive their numbers from their JSON.
- **Not pursued (outside this brief, for routing):**
  - `_binding_ok` skips the station check when a message has no `rsu` key (a `SignalStateUpdate` has none).
  - Warm-path expiry uses `time.time()`, not the injected clock.
  - `cached_at_revocation` reads the layer's private `_cache`.
  - Register #28's text mixes pre-merge attestEvent gas (169,295; 192,659-192,683) with post-merge (169,361; 192,749).
  - CAPABILITIES.md:373, CHANGELOG.md:71 and SIDE_PAPERS.md:27 still say 192,718; chapter 5 says 192,749 (Brief 5).
  - w3c_compliance.json and attack_results.json (dated 2026-07-19) carry no commit stamp, although #4 and #28 are V.
  - The consolidated handback and presentation report do not exist at d61a284 and were not judged.
