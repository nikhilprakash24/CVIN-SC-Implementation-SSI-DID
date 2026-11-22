# Appendix: Commits per Pass, July 2026 Onwards

**Generated** by `docs/make_progress_appendix.py` from the branch's first-parent history since 2026-07-01; do not edit. A pass runs from the commit that opens its after-action report to the commit before the next opening. Author identities are as git records them.

## before the reports (2026-07-23 to 2026-09-30, 26 commits)

| Commit | Date | Subject |
|---|---|---|
| `dfac1e9` | 2026-07-23 | update with mobi vid w3c did ssi compliance and more |
| `a91e76c` | 2026-09-24 | Add after-action report: GitHub push restored, integration plan for both work directions |
| `b0934a8` | 2026-09-24 | Fix Hardhat build (solc 0.8.24 + cancun) and ethers v6 test harness |
| `7229db3` | 2026-09-24 | Add detailed project summary report with verified ground-truth results |
| `c4d4e3d` | 2026-09-24 | Ignore generated analysis artifacts (w3c_compliance_report.json, gas-report.txt) |
| `14f10da` | 2026-09-24 | Add internal audit 01 (drift from original goals) and verification figure tooling |
| `708302a` | 2026-09-24 | Reconcile contract test suite: 47/47 passing (was 30/14) |
| `652486e` | 2026-09-24 | Verification snapshot, figure and dashboard; summary and audit updated to 47/47 |
| `f602fdf` | 2026-09-24 | Measurement conditions, claim register and scope-change log (audit items 3 and 8) |
| `a12129e` | 2026-09-24 | Chapter-grade M0 DID-resolution latency (N=30, cold and warm) replaces single-run figure |
| `5ab8d4d` | 2026-09-24 | Rewrite CI workflows to match the trunk; every step verified locally (audit item 4) |
| `ed85dfd` | 2026-09-24 | Track 1_blockchain-identity/package-lock.json so npm ci is reproducible in CI |
| `1d4ad07` | 2026-09-24 | PKI vs ERC-1056 identical-operations experiment (audit item 2, closes F2) |
| `a61d05d` | 2026-09-24 | Fold PKI-vs-ERC-1056 results and green CI into the register, summary, audit and scope log |
| `b482b12` | 2026-09-24 | Unify hypotheses (H1-H5), reword priority claims, derive the V2V latency budget, adopt the DID Method Rubric |
| `bffbad5` | 2026-09-24 | Audit 01: record end-of-second-pass status of the recommendations |
| `ed62314` | 2026-09-24 | External W3C DID test-suite run against the resolver (audit item 5, F5) |
| `f3c2940` | 2026-09-24 | Record external W3C conformance (328/441) in the claim register, audit F5 and summary |
| `781dc0b` | 2026-09-24 | Merge analysis lineage (bundle tip 7118b83, 53 commits) onto the trunk |
| `d157169` | 2026-09-24 | After-action report: merge commit recorded; tags v0.7.0/v0.8.0 need a push from the author's machine (session push policy is branch-only) |
| `21cf8bf` | 2026-09-24 | CI: install Python deps in the compliance-score job (merged checker imports the VC layer) |
| `b75c69a` | 2026-09-24 | CI: compliance gate accepts the merged checker's 'EXECUTABLE COMPLIANCE SCORE' label |
| `5a62137` | 2026-09-24 | Register #4: merged checker methodology (executable score, VC DM 2.0); SC-06: instrument already on 2.0 |
| `c663247` | 2026-09-30 | Pass 4: review of the CV2X testbed lineage, grounding in 13 canonical works, session manifest, MOBI/SUMO plan, after-action report 02 |
| `9350d64` | 2026-09-30 | Pass 4 closed: figure layout fixes, criteria totals reconciled (13/9/1/2), SC-12/SC-13, after-action report 02 completed |
| `3203ee8` | 2026-09-30 | Verification pass clean; add the original prompt-and-direction record and the 2026-09-30 handback |

## report 3 (2026-10-03 to 2026-10-04, 22 commits)

| Commit | Date | Subject |
|---|---|---|
| `1194565` | 2026-10-03 | M1: MOBI VID I section-level reconciliation; conformance claim narrowed (SC-14); after-action report 03 opened |
| `c464468` | 2026-10-03 | N2: DID resolver conformance fixes — official W3C DID test suite 328/441 -> 335/336; internal checker 94.3% |
| `e7a2541` | 2026-10-03 | N4: freshness-k cached verifier measured; latency-budget estimate rows become measured rows (register #29) |
| `cac1729` | 2026-10-03 | N3 / M4: lifecycle-parity comparison measured — centralized registry vs MOBI VID V2 (register #30; SC-13 closed) |
| `394373c` | 2026-10-03 | Pass 03 closed: verification snapshot/dashboard refreshed to 2026-10-03 numbers; after-action report 03 completed; handback addendum |
| `852a508` | 2026-10-04 | Design step for the grand sandbox, per-option sandboxes and layered suites: review 02, plan, meta-commentary, feature-asymmetry matrix, afte… |
| `2475899` | 2026-10-04 | S0: name the two ERC-1056 variants; archive the research copies; CI checks for MOBI copy identity and feature-matrix freshness |
| `c83b799` | 2026-10-04 | S1: per-option feature manifests (13), grand union manifest, matrix renderer and check, sandbox README |
| `b610364` | 2026-10-04 | S2 scaffolding: IdentityOption interface with NotApplicable as a first-class result, smoke runner (S2 acceptance), adapter conventions |
| `aa55a3c` | 2026-10-04 | S4: layer the Hardhat tests in place (test/L1-identity-mechanisms, test/L2-identity-system/{per-option,security}); sandbox/suites symlinks t… |
| `7245ffb` | 2026-10-04 | S5 (+S6 schema half): Python layers L3/L4 under sandbox/py-suites — conformance record regression, internal checker as a test, experiment-re… |
| `e36a0dd` | 2026-10-04 | S4 follow-up: security harness writes attack_results.json to the canonical 4_comparison-framework path after the test-tree layering (one mor… |
| `a798370` | 2026-10-04 | S2: eleven IdentityOption adapters (all conform on the smoke runner); ERC-1155 self-transfer defect guarded + regression test; runner and ma… |
| `c087d90` | 2026-10-04 | S6: the twelve lifecycle use cases as pytest cases and a V2V harness smoke (L4 now has automated tests); Python side 81 passed |
| `97ecbd3` | 2026-10-04 | S9 (part): CI job for the Python layers — sandbox/py-suites/run.sh (L3 + L4 + SSI-layer suites, 81 tests) |
| `c112f22` | 2026-10-04 | Report 04 / plan: python-layers CI job verified green on GitHub (S9 part) |
| `ab984c3` | 2026-10-04 | S3: uniform L1 identity-mechanism suite over all eleven adapters (99 tests; whole tree 319); test-produced asymmetry table with manifest dis… |
| `08b81de` | 2026-10-04 | Manifest review as generator rules (seven L1 disagreements resolved with evidence); reviewed stances preserved across regeneration; L1 repor… |
| `99284ec` | 2026-10-04 | S7 (group B): feature demos for ERC-721, ERC-1155, ERC-4337, LSP8 and MOBI VID — every public function exercised, including features the com… |
| `fdb05a7` | 2026-10-04 | S7 (group A) + defect log: feature demos for the two ERC-1056 variants, ERC-725, ERC-725xy, ERC-735, CVIN-Combined; docs/DEFECT_LOG.md D1-D2… |
| `2afa35c` | 2026-10-04 | S8: the grand runner — run.py all orchestrates smoke, L1, the Hardhat tree, the Python layers and all 92 demos into report/GRAND_REPORT.md (… |
| `b6b887f` | 2026-10-04 | S10 draft section on the feature asymmetry; report 04 implementation stretch closed; handback addendum; session manifest pass 5 |

## report 5 (2026-10-04 to 2026-10-04, 9 commits)

| Commit | Date | Subject |
|---|---|---|
| `f87f8c4` | 2026-10-04 | F1 / D11: MOBI provider verification bound to the registered key (impostors under a vehicle's DID rejected); six regression tests; D11b reco… |
| `65a143f` | 2026-10-04 | F2-F4, F6: fix D21 (revocation severs the did:ethr change list; mutators after revoke), D22 (claim ops cut the list), D18 (birth record unre… |
| `241642e` | 2026-10-04 | F5 / D13: VIN normalisation and ISO 3779 validation on ERC-721, ERC-1155 and LSP8 mint and lookup paths; 15 regression tests |
| `ad470b6` | 2026-10-04 | F7 / D25: ERC-735 claim holder gains a per-topic issuer registry and binds VIN attestations to the holder's VIN; 14 regression tests; caller… |
| `2b38536` | 2026-10-04 | Results of record re-executed after the defect fixes: nine-standard gas table (cells moved listed), feature matrix and manifests regenerated… |
| `3a7a4ec` | 2026-10-04 | Register #25 note and #31 (gas moved by the defect fixes); README gas table and thesis-README figures refreshed from the 2026-10-04 results … |
| `5778651` | 2026-10-04 | ERC-735 demos and README updated to the D25 fix: issuer registry exercised (17/17 functions), impostor and wrong-VIN steps now assert the re… |
| `eed6bfc` | 2026-10-04 | Demos and READMEs of seven options updated to the defect fixes: steps that asserted D10/D11/D13/D18/D21/D22 now assert the fixed behaviour (… |
| `a764387` | 2026-10-04 | Fix pass closed: grand run ALL OK on the fixed trunk (366 Hardhat, 87 Python, 92 demos / 1,688 steps); defect log statuses with commits and … |

## report 6 (2026-10-04 to 2026-10-04, 4 commits)

| Commit | Date | Subject |
|---|---|---|
| `d941ad5` | 2026-10-04 | D7/D8, D9, D11b fixed with regression tests: ERC-1155 standard transfers closed, held-credential bitmap, issuerTransferIdentity atomic re-bi… |
| `7404e94` | 2026-10-04 | ERC-1155 and ERC-721 demos and READMEs updated to the D7/D8/D9 fixes: standard transfers assert the closed entry points, issuerTransferIdent… |
| `d06d004` | 2026-10-04 | Pass 06 closed: results of record re-executed on the final contracts (nine-standard table, scaling A/B, MOBI backend sweep — script fixed, i… |
| `b70081c` | 2026-10-04 | Handback 0d: CI result recorded for the pass-06 commits |

## report 7 (2026-10-06 to 2026-10-09, 12 commits)

| Commit | Date | Subject |
|---|---|---|
| `2b7836d` | 2026-10-06 | Review 03 and merge plan: the repository has two trunks since 2026-09-30 (this sandbox lineage and the review-2 lineage, now the default bra… |
| `bd90004` | 2026-10-06 | Merge the review-2 lineage (clone-cvin-id-scs @ fa6188e) into the sandbox lineage: one trunk |
| `19aed0a` | 2026-10-06 | Merge S5 (part 1): manifests and feature-asymmetry matrix regenerated from the merged ABIs (CI freshness gate); scaling A/B, MOBI backend sw… |
| `d517c56` | 2026-10-06 | Merge S7: external W3C DID test suite re-run on the merged resolver — 335/336 on the fixtures and 335/336 on a registry-minted did:ethr (con… |
| `80e8f03` | 2026-10-06 | Testbed artifacts compiled the way CI compiles them (root node_modules, OpenZeppelin 5.0.2): MOBIVIDRegistryV2 artifact regenerated; the loc… |
| `8658a0f` | 2026-10-06 | Merge S9 (part 1): defect log closes D27 (S-10), half of D12 (K-8) and the rest of D16 (K-3/K-15), revises D22 (M-A) and cross-references th… |
| `2c03a3d` | 2026-10-06 | Merge the TSR plan commit (testing-suite-organization @ ef2c851): TESTING_SUITE_RESULTS_PLAN v1.0, second-pass sheet, as-found inventory; in… |
| `0444ae8` | 2026-10-06 | docs/testing/README.md: entry point for the organised suite after the merge (three clicks to any test; TSR plan mapped onto the grand sandbo… |
| `52903c4` | 2026-10-06 | Review-2 documents point at the renamed after-action reports (docs/review02/AAR_REVIEW2_03/04/05.md); header notes on the renamed files; aft… |
| `db6c381` | 2026-10-06 | Merge S5: nine-standard gas determinism re-checked on the merged contracts — N=30 runs, every cell byte-identical (gas_benchmark_stats.json) |
| `dc8348c` | 2026-10-09 | Merge S6 (part 1): nine demos updated to the merged contracts (K-1 setVehicleAttributes did argument, K-3 changeOwner closed for born vehicl… |
| `0f1dbc5` | 2026-10-09 | Plan of 2026-10-09 for audit (close the merge pass; generated results dashboard; SUMO visualisation; structured tests and the unreconciled o… |

## report 9 (2026-10-09 to 2026-10-09, 12 commits)

| Commit | Date | Subject |
|---|---|---|
| `7a9a996` | 2026-10-09 | After-action report 09 opened: executing the plan of 2026-10-09 under its defaults |
| `ca3a44d` | 2026-10-09 | P1.1, P1.2, P4.1: generated dashboard snapshot and crux register (docs/thesis/cruxes.yaml -> CRUX_REGISTER.md) built only from committed res… |
| `3a2a806` | 2026-10-09 | P3.5: onboarding lineage imported as provenance (documents only, verbatim below a source header; reconciliation note maps its tracks and haz… |
| `aef16af` | 2026-10-09 | P0.1: four option READMEs brought to the merged contracts (K-1/K-2/K-3/K-4/K-6/K-8/K-15; coverage 20/20, 50/50, 21/21, 57/57; step counts fr… |
| `230ac1a` | 2026-10-09 | P3.3, P3.4: run-stamp helper (commit, dirty, node, hardhat) spread into the four JS producers' metadata; stamp inventory of the 25 results o… |
| `f976e57` | 2026-10-09 | P0.3: metrics-harness run of record on a clean tree (2026-10-09T02-09-36Z_7a9a996, dirty false; frontier and dominance unchanged), register … |
| `5a83bc2` | 2026-10-09 | P3.4: 82 superseded figures in 12 citing documents brought to the current register values (test totals now cite the grand report; ERC-735 na… |
| `8885a7f` | 2026-10-09 | P0.2: grand run on the merged trunk ALL OK (Hardhat 536, Python 260, 92 demos / 1,752 steps); grand report, test register, coverage matrix, … |
| `d0cc19c` | 2026-10-09 | Run stamp: dirty is measured over the producing code paths (contracts, scripts, configuration, lockfile), as the metrics harness does; a pro… |
| `d54178e` | 2026-10-09 | P3.3: four JS producers re-run from a clean tree with run stamps (commit d0cc19c, dirty false); no gas or sweep cell moved; stamp inventory,… |
| `577a5ab` | 2026-10-09 | Pass 9 closed: handback 2026-10-09 supersedes both lineages' handbacks; report 07 (merge pass) closed; report 09 closed with the team-struct… |
| `0874b99` | 2026-10-09 | Handback 2026-10-09: CI result recorded (8/8 green on 577a5ab) |

## report 10 (2026-10-09 to 2026-10-09, 6 commits)

| Commit | Date | Subject |
|---|---|---|
| `cfbdcbc` | 2026-10-09 | Designs approved with defaults (infrastructure messaging I-a..I-d; SUMO visualisation S-a..S-c); pre-registration of I1-I5 locked before any… |
| `47c3314` | 2026-10-09 | Infrastructure messaging built per the approved design: identity layer (road authority, RSU, controller, TMC as credentialed DIDs; permitted… |
| `1e690c3` | 2026-10-09 | run_infra_stats: environment header captured before the runs |
| `9006d4c` | 2026-10-09 | Infrastructure messaging results of record (pre-registered I1-I5): I1 PASS (SPaT/BSM warm verify ratio 0.996, 95% CI [0.995, 1.001], N=30), … |
| `94c2b7c` | 2026-10-09 | Pass 10 grand run ALL OK (Hardhat 536, Python layers 276, 92 demos / 1,752 steps); after-action report 10 log through B6; deferred items N-1… |
| `0ba7c6c` | 2026-10-09 | After-action report 10 closed (decisions F-C, F-D; team-structure assessment); handback addendum for pass 10; index and handback point to re… |

## report 11 (2026-10-09 to 2026-10-09, 7 commits)

| Commit | Date | Subject |
|---|---|---|
| `5cc39c2` | 2026-10-09 | After-action report 11 opened (adversarial review of passes 9-10, run-identity fixes); F-C accepted by the author |
| `b1d3f72` | 2026-10-09 | Run-identity flags fixed: the producing-code dirty flags of the JS run stamp and the harness header could never fire (relative pathspecs fro… |
| `98e64e4` | 2026-10-09 | Pre-registration amendments: A1-A3 post hoc (I1 at k=inf; I4 key revocation; I5 as a sum of operation costs), A4 before any pass-11 code or … |
| `f1f9e37` | 2026-10-09 | Infrastructure verifier hardened after the adversarial review (amendment A4): message fields bound to the credential (intersectionId, statio… |
| `36e0309` | 2026-10-09 | Generated-document checks hardened after the adversarial review: stale-figure checker scans every tracked Markdown file except named history… |
| `601e1de` | 2026-10-09 | Infrastructure results of record re-run on the hardened verifier (f1f9e37, amendment A4): I1 PASS (ratio 1.096, 95% CI [1.091, 1.101]; was 0… |
| `291bbca` | 2026-10-09 | Pass 11 closed: grand run ALL OK (Hardhat 536, Python layers 291, 92 demos / 1,752 steps); after-action report 11 log, decisions G-A..G-E, c… |

## report 12 (2026-10-10 to 2026-10-10, 13 commits)

| Commit | Date | Subject |
|---|---|---|
| `3e19e72` | 2026-10-10 | After-action report 12 opened: close work milestone WM-1 (passes 8-11) with plan review, backward fixes, milestone report, audit and present… |
| `44dc926` | 2026-10-10 | WM-1 close, step W2: plan review and backward fixes. Milestone scheme (docs/milestones); plan of 2026-10-09 status table (P3.2 claims.yaml f… |
| `d61a284` | 2026-10-10 | WM-1 close, step W3: work milestone report drafted before the audit (scope, timeline, deliverables, results of record with both runs, defect… |
| `c363358` | 2026-10-10 | WM-1 close, step W5: presentation report draft 1 generated from committed data (10 sections, results with register rows, 8 generated figures… |
| `d877a4f` | 2026-10-10 | WM-1 close: audit briefs archived (written by a separate brief-writer agent; scratch paths normalised); consolidated handback 2026-10-10 dra… |
| `8d5d25c` | 2026-10-10 | WM-1 audit, fixes (part 1): register #29/#30/#34-#36 re-stated from the 2026-10-09 harness run of record (they kept pre-merge values; D43), … |
| `a1c9cb8` | 2026-10-10 | WM-1 audit, fixes (part 2): WM-1 report revised against the audit (plan status recount 15/3/4/1/2 with P0.4 not recorded; harness numbers mo… |
| `0fe7d29` | 2026-10-10 | Stale-figure checker: the verbatim reviewer and auditor reports are records and keep the values they quote (history list); the previous comm… |
| `9a04eb7` | 2026-10-10 | WM-1 audit: findings register for briefs 1-4 (72 findings with dispositions and commits); recorded checks and the piped-check slip in report… |
| `885f642` | 2026-10-10 | WM-1 audit, fixes (part 3, brief 5 and close-out of the register): tests that could not fail now can (VC proof options signed, odometer roll… |
| `017acfc` | 2026-10-10 | Test register regenerated: a separate npx hardhat test run (for the new count gate) rewrote the tracked L1 report with input-dependent gas a… |
| `8c9fe6b` | 2026-10-10 | Work milestone WM-1 closed (pass 12): final grand run ALL OK (Hardhat 537, Python layers 305, 92 demos / 1,752 steps); handback 2026-10-10 v… |
| `9d0625e` | 2026-10-10 | WM-1 close recorded: CI 8/8 green on 8c9fe6b; dashboard v6 and presentation page v2 published from it |

## report 13 (2026-10-10 to 2026-10-10, 2 commits)

| Commit | Date | Subject |
|---|---|---|
| `a209710` | 2026-10-10 | After-action report 13 opened: WM-2 step A1 (stamp inventory over every result directory) |
| `e639dad` | 2026-10-10 | WM-2 A1 (N-21): stamp inventory accounts for every tracked result file (161, 0 uncovered); --check-coverage in CI, shown to fail; report 13 … |

## report 14 (2026-10-12 to 2026-10-12, 5 commits)

| Commit | Date | Subject |
|---|---|---|
| `2ef1133` | 2026-10-12 | After-action report 14 opened: WM-2 step A2 (one stamp helper with per-producer scope, D49) |
| `188efec` | 2026-10-12 | WM-2 A2 (D49): one run stamp with per-producer scope for JS and Python |
| `4e99cf1` | 2026-10-12 | WM-2 A2: harness run.js restored (benchmarksTree equals the run of record's again; switch at A6 per N-19); stamp-only commits verified; D49 … |
| `1f3cd8f` | 2026-10-12 | WM-2 A2: CI checks out full history (stamp-only verification needs it; shallow clone now fails with a message); grand run ALL OK (Hardhat 53… |
| `2756c2c` | 2026-10-12 | Report 14 closed: CI 8/8 green on 1f3cd8f |

## report 15 (2026-10-14 to 2026-10-14, 5 commits)

| Commit | Date | Subject |
|---|---|---|
| `91d61c2` | 2026-10-14 | After-action report 15 opened: WM-2 A4 (promote step), Phase 2 opened, handoff |
| `1012ebd` | 2026-10-14 | WM-2 A4: promote step, piloted on the security matrix (D56) |
| `b02ea17` | 2026-10-14 | Phase 2 opened (P2.0, session 1): charter and session protocol, evidence base (18 seeds), idea register as data (23 ideas, 7 tracks, 5 candi… |
| `4b2b30c` | 2026-10-14 | Pass 15 closed: WM-2 A4 recorded (plan, defect log D56 in part, N-20); handback 2026-10-14 (supersedes 2026-10-10; section for a session on … |
| `5509b6a` | 2026-10-14 | Report 15 closed: CI 8/8 green on 4b2b30c |

## report 16 (2026-10-14 to 2026-10-14, 8 commits)

| Commit | Date | Subject |
|---|---|---|
| `dc1ef41` | 2026-10-14 | After-action report 16 opened: Phase 2 focus areas F1-F3, scope reconciliation, writing team, WM-2 C0 |
| `c7e333f` | 2026-10-14 | Pre-registration amendment A6 (before any verifier change): verifier v3 for D37-D42; I2 extended to 15 checks; I1-I3, I5 re-run as runs of r… |
| `7d08dce` | 2026-10-14 | WM-2 C0: verifier v3 (D37-D42) and the D51 fix |
| `bda4940` | 2026-10-14 | Phase 2 focus areas F1-F3 (capture, analysis, plan, execution start), scope reconciliation, register rows #49-#50, defects D58-D64 |
| `d881f02` | 2026-10-14 | WM-2 C0 runs of record and the academic review of F1-F3 (fixes, part 1) |
| `e3087de` | 2026-10-14 | Academic review of F1-F3 (fixes, part 2) and pass 16 records |
| `6cb502f` | 2026-10-14 | Pass 16 grand run ALL OK (Hardhat 537, Python layers 331, 92 demos / 1,752 steps); v3 test count corrected to 26; generated documents regene… |
| `1e96842` | 2026-10-14 | Report 16 closed: CI 8/8 green on 6cb502f |

## report 17 (2026-10-14 to 2026-10-14, 4 commits)

| Commit | Date | Subject |
|---|---|---|
| `9be4dfb` | 2026-10-14 | After-action report 17 opened: WM-2 B1 (deterministic gas, or ranges by rule) |
| `a950cdf` | 2026-10-14 | WM-2 B1: seeded randomness for incidental inputs; I4 over declared seeds; the rule written |
| `8855a4d` | 2026-10-14 | WM-2 B1 closed: I4 runs of record over declared seeds 1-30 at a950cdf (seed 1 exact, range reproduced by a second run); #47, README, chapter… |
| `04dcdcc` | 2026-10-14 | Report 17 closed: CI 8/8 green on 8855a4d |

## report 18 (2026-10-15 to 2026-10-15, 6 commits)

| Commit | Date | Subject |
|---|---|---|
| `902cebd` | 2026-10-15 | Report 18 opened: WM-2 B2 gas charter and result cards |
| `001941a` | 2026-10-15 | WM-2 B2: gas charter generated from the run of record; 27 varying harness cells root-caused (flag marks 14, execution only); 20 V gas rows c… |
| `4b3697a` | 2026-10-15 | Result cards: every V register row as a card, generated and CI-checked against the register; published beside the results board |
| `af8a006` | 2026-10-15 | Pass 18 records: handback addendum, session manifest |
| `aba1d7c` | 2026-10-15 | Pass 18 grand run ALL OK at af8a006 (Hardhat 537, 92 demos / 1,752 steps); generated documents regenerated |
| `b7997f8` | 2026-10-15 | Report 18 closed: CI 8/8 green on aba1d7c |

## report 19 (2026-10-15 to 2026-10-15, 5 commits)

| Commit | Date | Subject |
|---|---|---|
| `ff2bfba` | 2026-10-15 | Report 19 opened: contribution record; WM-2 C3 design and decision rule written before any run |
| `3c9fd89` | 2026-10-15 | WM-2 C3: #32 and #37 at their own code on one host, two replicates; the host explains their difference (#52); notes on #32 and #37; card for… |
| `c89baea` | 2026-10-15 | Contribution record: the history as a contribution calendar with sourced evidence tiles and stated scope; generator and page |
| `c4b35ce` | 2026-10-15 | Pass 19 records: handback addendum, session manifest |
| `9975a2e` | 2026-10-15 | Pass 19 grand run ALL OK at c4b35ce (Hardhat 537, Python layers 331, 92 demos / 1,752 steps); generated documents regenerated |

## report 20 (2026-10-15 to 2026-10-15, 2 commits)

| Commit | Date | Subject |
|---|---|---|
| `ac0dbb9` | 2026-10-15 | After-action report 20 opened: Technical Data Package (parallel document set in the engineering register), plan T0-T7 and defaults |
| `e18b06a` | 2026-10-15 | Report 19 closed: CI 8/8 green on 9975a2e |

## report 21 (2026-10-15 to 2026-10-15, 8 commits)

| Commit | Date | Subject |
|---|---|---|
| `c24572f` | 2026-10-15 | Report 21 opened: WM-2 C1, did:ethr resolution reads the ERC-1056 registry; defaults stated |
| `4699f21` | 2026-10-15 | TDP generators: requirements source and VCRM (TDP-002, TDP-005), FMECA worksheet from the defect log (TDP-006), six blueprint drawings from … |
| `7ae268a` | 2026-10-15 | WM-2 C1: did:ethr resolution reads the ERC-1056 registry when given a provider (owner, delegates, attributes, chain-time validity, deactivat… |
| `7e43ea0` | 2026-10-15 | TDP STD-01: C1 no longer pending (its VCRM guard asked for it after WM-2 C1); TDP-002 and TDP-005 regenerated with their own generator |
| `5cc751b` | 2026-10-15 | Pass 21 records: handback addendum, session manifest |
| `f61ed34` | 2026-10-15 | Pass 21 grand run ALL OK at 5cc751b (Python layers 342); generated documents regenerated; CI red since 4699f21 fixed: TDP-006 (generated fro… |
| `914dcb2` | 2026-10-15 | Technical Data Package (pass 20): index, programme summary, interface control, design description, test plan, configuration baseline, risk r… |
| `916f349` | 2026-10-15 | Report 21 closed: CI 8/8 green on f61ed34 |

## report 22 (2026-10-17 to 2026-10-18, 12 commits)

| Commit | Date | Subject |
|---|---|---|
| `7b65d80` | 2026-10-17 | Report 22 opened: WM-2 C2 (D54); the MOBI registry stores no delegations, so the fix stores them as the canonical registry does; defaults st… |
| `92cc4d5` | 2026-10-17 | WM-2 C2 (D54): MOBI registry stores delegations (validDelegate); attestEvent requires the vehicle's owner or a veriKey delegate, once per ev… |
| `dd3755b` | 2026-10-17 | WM-2 C2 re-runs of record at 92cc4d5: only MOBI-VID-V2 cells move (addDelegate +22,328, attestation +29,333, deploy +141,098, dispatch offse… |
| `7fe8c37` | 2026-10-17 | Hand-off 2026-10-17 and check brief for passes 16-22 (13 claims with commands, expected results and falsifiers; findings format) |
| `16099ed` | 2026-10-17 | Pass 22 records: handback addendum, session manifest |
| `a45be79` | 2026-10-17 | WM-2 C2 redesign: delegation storage moves from the shared ERC1056Registry base into MOBIVIDRegistry (override of the base's internal delega… |
| `7e00cf1` | 2026-10-17 | WM-2 C2 re-runs of record for the final design at a45be79: only MOBI-VID-V2 moves (addDelegate 57,667, deploy 4,370,878; others as before); … |
| `f65b5cf` | 2026-10-17 | Pass 22 grand run ALL OK at 7e00cf1 on the final C2 design (Hardhat 541, Python layers 342, 92 demos / 1,758 steps); the first run, on the f… |
| `e40c50a` | 2026-10-18 | WM-2 C2: testbed copies of the MOBI contracts synced and its artifacts recompiled (CI requires them byte-identical; failed since 92cc4d5); t… |
| `72a29de` | 2026-10-18 | Testbed artifacts rebuilt with CI's node_modules (the local testbed node_modules has other Hardhat and OpenZeppelin versions; MOBIVIDRegistr… |
| `160b425` | 2026-10-18 | Pass 22 grand run (last) ALL OK at 72a29de after the testbed sync; generated documents regenerated |
| `bf4ca58` | 2026-10-18 | Report 22 closed: CI 8/8 green on 160b425 |

## report 23 (2026-10-20 to 2026-10-20, 5 commits)

| Commit | Date | Subject |
|---|---|---|
| `b6f40c8` | 2026-10-20 | Report 23 opened: Phase 2 session 3 (deep-dive briefs I-24, I-05), taken before A3 so the cross-model check can precede new runs of record; … |
| `4e47c5a` | 2026-10-20 | Check of passes 16-22: opening message for a fresh session |
| `651eaa5` | 2026-10-20 | Phase 2 session 3: deep-dive brief I-24 (IDTx), 18 sources fetched at origin, 10 re-checked; ideas.yaml test count corrected to 12; plan for… |
| `024274d` | 2026-10-20 | Phase 2 session 3: deep-dive brief I-05 (freshness theory), 15 entries fetched at origin, 8 re-checked (Springer not re-verifiable here, sta… |
| `de27b7c` | 2026-10-20 | Report 23 closed: CI 8/8 green on 024274d |

## report 24 (2026-10-20 to 2026-10-20, 6 commits)

| Commit | Date | Subject |
|---|---|---|
| `c6dc3af` | 2026-10-20 | Report 24 opened (lead's pass); tools/prepush_check.sh mirrors CI's document and copy guards locally, with a probe that shows it fires |
| `e3944ec` | 2026-10-20 | Decision sheet: every open author decision on one page, with what it blocks, the default in force and a recommendation |
| `41c0535` | 2026-10-20 | Progress report July to October 2026, draft 1, with a generated commit appendix; handback addendum; manifest; report 24 log |
| `46f8d1f` | 2026-10-20 | Fix the red document step: the generated progress appendix is a history document for the stale-figure checker; one sentence reworded; prepus… |
| `b7ea6f4` | 2026-10-20 | Report 24 closed: CI 8/8 green on 46f8d1f |
| `a9b03c2` | 2026-10-20 | Report 20 closed: CI 8/8 green on 914dcb2 |

## report 26 (2026-10-20 to 2026-10-20, 2 commits)

| Commit | Date | Subject |
|---|---|---|
| `972f7ae` | 2026-10-20 | Chapter 2 draft sections 2.4a (revocation freshness) and 2.6 (the IDTx positioned), from the two Phase 2 briefs' fetched sources; report 26 … |
| `73cba2d` | 2026-10-20 | Chapter 6 draft section 6.8: the identity-dependent transaction, what it is and what it is not (examiner question 12); report 26 log |

## report 25 (2026-10-21 to 2026-10-22, 6 commits)

| Commit | Date | Subject |
|---|---|---|
| `af774c2` | 2026-10-21 | After-action report 25 opened: TDP runbook phase 10, thesis adaptation map onto chapter 3 |
| `7bb683e` | 2026-10-21 | TDP runbook phase 10: thesis adaptation map onto chapter 3 (TDP-010), state per requirement, drift table, outline v2; records; progress appe… |
| `ed42ba2` | 2026-10-21 | Report 25 closed: CI 8/8 green on 7bb683e |
| `36b0605` | 2026-10-22 | Status for the author, 2026-10-22: done, next in order, what needs the author, the check session |
| `df64ce9` | 2026-10-22 | Status and report 26: report 25 was taken by the TDP session; the check takes the next free number |
| `87334d6` | 2026-10-22 | Status: two remaining references to report 25 corrected |

## report 27 (2026-10-22 to 2026-10-23, 9 commits)

| Commit | Date | Subject |
|---|---|---|
| `fa275da` | 2026-10-22 | After-action report 27 opened: TDP runbook phases 8 and 9 |
| `ad6d6c5` | 2026-10-22 | TDP runbook phases 8 and 9: requirement-to-test trace with its guard (TDP-005 section 3); ICD gate check_icd.py in CI with a probe; TDP-003 … |
| `ec7e19b` | 2026-10-22 | Report 27 closed: CI 8/8 green on ad6d6c5 |
| `81dc3ac` | 2026-10-22 | Merge PR #7: the integrated trunk into the cv2x-testbed workspace (Plan 5) |
| `9990db7` | 2026-10-22 | Merge PR #9: keep the workspace in sync (WM-2 A3b and A6) |
| `40cdbcd` | 2026-10-23 | Unblocked work list, 2026-10-23: twelve items that need no decision, nine that wait and why, a proposed order |
| `62a41c6` | 2026-10-23 | After the merge of PRs 3-9: status addendum (A3, A3b, A6 done elsewhere; 62 rows; next A5), unblocked list revised, the two report-26 drafts… |
| `35eead9` | 2026-10-22 | Merge PR #11: keep the workspace in sync (WM-2 A5) |
| `f67efb6` | 2026-10-23 | Unblocked list: A5 done by another session (50888c7) |

## report 35 (2026-10-23 to 2026-10-23, 6 commits)

| Commit | Date | Subject |
|---|---|---|
| `cf60516` | 2026-10-23 | Report 35 opened: WM-2 B3 (latency charter) and A7 (Python suites in the test register) |
| `0236430` | 2026-10-23 | WM-2 B3: latency charter (14 rows classed; #26, #31, #39, #57 descriptive only, noted in the register); the harness records no CPU (N-26); c… |
| `9383158` | 2026-10-23 | WM-2 A7: the grand runner keeps a per-test record of the Python layers; the test register gives each of the 376 Python tests a TC id (L3 78,… |
| `b49c9a1` | 2026-10-23 | Plan WM-2: B3 and A7 done (report 35) |
| `09c5363` | 2026-10-23 | Pass 35 grand run ALL OK at b49c9a1 (Hardhat 562, Python 376); generated documents regenerated |
| `55bf410` | 2026-10-23 | Reports 35 and 26 closed: CI 11/11 green on 09c5363 |

## report 36 (2026-10-23 to 2026-10-24, 16 commits)

| Commit | Date | Subject |
|---|---|---|
| `2dbfc30` | 2026-10-23 | Report 36 opened: mutation probes for the C1 and C2 tests |
| `cea9cf0` | 2026-10-23 | Mutation probes for the C1 and C2 tests: resolver 0/9 survive; D54 probe on behaviour tests found one survivor (revoked identity), closed by… |
| `cb5ed18` | 2026-10-23 | Pass 36 grand run ALL OK at cea9cf0 (Hardhat 563); generated documents regenerated |
| `558fc9d` | 2026-10-23 | CI: run the chain-resolver mutants in the Python job, which has the node (report 36) |
| `6a7fe6c` | 2026-10-24 | Close report 36 (CI green); report 37: pinned CI Python packages (U9), I-05 model as code (U8) |
| `3406bca` | 2026-10-24 | Master plan and atlas: phases, integration, plan forward, Phase B open questions, blockers, reading list, catalogue (report 37) |
| `99e30e4` | 2026-10-24 | Chapter audit (U6, read-only) and the visual master atlas (report 37) |
| `8984cad` | 2026-10-24 | Atlas: U6 shown done (report 37) |
| `e481889` | 2026-10-24 | CI: read the pins file from the workspace root, for jobs that run in a subdirectory (report 37) |
| `56448d1` | 2026-10-24 | Report 37: CI green with the pins |
| `5f09e93` | 2026-10-24 | Stale-figure checker: superseded #27/#28/#22/#25 values and small counts; 24 files corrected outside the thesis; thesis hits pending on D1 (… |
| `8b35320` | 2026-10-24 | RSU-to-RSU design note (U5 = WM-2 D2) and the read-only TDP review (U7) (report 37) |
| `28dd0b9` | 2026-10-24 | Progress report draft 2 (U11); index, history and handback hygiene (U12); unblocked list marked done (report 37) |
| `165db04` | 2026-10-24 | Branch review (T-12); master plan and atlas updated; report 37 closing |
| `1fba094` | 2026-10-24 | Report 37 closed: CI green on 165db04 |
| `7b53fb5` | 2026-10-24 | Merge PR #17's sync: the default branch's NatSpec, contract-reference and Roots documents into the workspace |

## report 38 (2026-10-24 to 2026-10-24, 8 commits)

| Commit | Date | Subject |
|---|---|---|
| `7c8a78a` | 2026-10-24 | Merge PR #17's sync (NatSpec pass, contract reference, Roots documents); test register regenerated; report 38 opened |
| `963439a` | 2026-10-24 | Stamp checker: comment-only commits, verified, exempt only results without deployment gas; bytecode equivalence tool (report 38) |
| `57dfab4` | 2026-10-24 | Re-run of record after the NatSpec pass: five deployment-gas cells moved by 12, rows 25, 26, 31, 34, 35, 39 restated; CI gate on code change… |
| `243c2bb` | 2026-10-24 | Merge the integration branch (the other session's NatSpec re-run, PR #17, Roots); one run of record per producer; rows 26, 34, 35, 39 comple… |
| `6a574a2` | 2026-10-24 | TDP-003: commit id as plain text (ICD check); grand run ALL OK; generated documents regenerated (report 38) |
| `c9dc64b` | 2026-10-24 | Merge claude/exploration-plan (B-1, docs only): related-work workspace scaffold |
| `18fb9f8` | 2026-10-24 | Merge the exploration workspace (B-1); master plan tasks; report 38 closing |
| `b50864c` | 2026-10-24 | Report 38 closed: CI green on 18fb9f8 |

## report 39 (2026-10-31 to 2026-10-31, 3 commits)

| Commit | Date | Subject |
|---|---|---|
| `e02e603` | 2026-10-31 | After-action report 39 opened: TDP revision B completed (records, Layer 5 requirements, TDP-004 and TDP-010) |
| `219a844` | 2026-10-31 | TDP revision B completed (report 39): SYS-04 and the L5 group in the specification, file-backed verdicts, DWG-007 for layer 5, revision bloc… |
| `8cf93fe` | 2026-10-31 | Drawings: space runs as no-break spaces so column alignment survives rendering; DWG-004 staleness note updated to A3b and #55 (report 39 add… |

## report 40 (2026-10-31 to 2026-10-31, 6 commits)

| Commit | Date | Subject |
|---|---|---|
| `7144544` | 2026-10-31 | After-action report 40 opened: SVG stale-figure checker, blueprint refresh and merge (claim pushed before the work) |
| `c38f6a9` | 2026-10-31 | Stale-figure checker reads the text of tracked SVG drawings (T-19, report 40) |
| `f98cf45` | 2026-10-31 | Merge the blueprint set at Rev C, refreshed on the trunk's results (lock: 96 values traced); blueprint check in the pre-push guard; CI is 12… |
| `dc1a78a` | 2026-10-31 | Report 39 closed: CI green on 8cf93fe |
| `3b9a5ba` | 2026-10-31 | Report 40 closed: CI green on f98cf45 |
| `f3c150e` | 2026-10-31 | Atlas: blueprint merge shown done (report 40) |

## report 41 (2026-10-31 to 2026-10-31, 4 commits)

| Commit | Date | Subject |
|---|---|---|
| `a29e02f` | 2026-10-31 | After-action report 41 opened: the stale-figure checker reads HTML and TeX (claim pushed before the work) |
| `dc79377` | 2026-10-31 | Stale-figure checker reads HTML (text and script data) and TeX; dated dossiers and the 10-03 verification snapshot classed as history (T-19 … |
| `c048b9f` | 2026-10-31 | Report 41 closed: CI green on dc79377 |
| `2e09060` | 2026-10-31 | Row #26 density sweep confirmed current, its stamp exception explained (T-17); the September project summary dated, index updated (T-20); re… |

## report 43 (2026-10-31 to 2026-10-31, 4 commits)

| Commit | Date | Subject |
|---|---|---|
| `0d21926` | 2026-10-31 | After-action report 43 opened: merge the default branch into the trunk and open the pull request back |
| `261aa12` | 2026-10-31 | Merge the default branch (PR #19 test register and charters, PR #21 Roots receipts, PR #16, investor room) into the trunk (report 43) |
| `9058159` | 2026-10-31 | Report 43: merge logged, pull request #25 opened; handback addendum; manifest |
| `4f81159` | 2026-10-31 | Report 42 closed: CI green on 2e09060 |

243 commits in 31 groups.
