# Session Manifest — 2026-09-24 / 25

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Purpose:** every artifact produced in this work session, what it is, why it exists,
and where it lives — so the session's outputs can be audited as a set rather than
discovered one commit at a time. Ordered by the pass that produced them.

## Pass 1 — GitHub restoration and ground truth (2026-09-24)

| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT.md` | Report 01: how push was restored; the three work directions (trunk, bundle lineage, notebooks); the integration plan; §6 now carries the tag-push instructions | The pipe to GitHub had been closed for weeks; this records the fix and the merge plan |
| `docs/PROJECT_SUMMARY.md` | Commit-by-commit history, layer inventory, thrust status, and the **verification table** (every number re-run on the trunk with condition tags) | The trunk had never been verified as received — it did not compile |
| `1_blockchain-identity/hardhat.config.js` (fix) | solc 0.8.24 + `evmVersion: cancun` | OpenZeppelin ≥5.1 uses `mcopy`; without this nothing compiled |
| Contract and test fixes (`708302a`) | `CVINVehicleDIDRegistry.vehicleOwnerOf` (unreachable functions), ERC-721 `recordEntry`/`payToll`, monolithic NFT restored, ethers-v6 tests | 47/47 → later 219/219 |
| `docs/figures/results_snapshot.json`, `verification_dashboard.{png,svg,html}`, `make_verification_figure.py` | The verification figure and interactive dashboard, generated from the snapshot; published at https://claude.ai/artifact/1C5X9GpPcEwyCRDMYxYhpa | "Visualize the passed tests" |
| `docs/AUDIT_01_ORIGINAL_GOALS.md` | Audit 01: goal register (README RQs, hypothesis, contributions, roadmap criteria) vs evidence; findings F1–F10; examiner questions; positioning vs Fdhila 2021 / Schäffner; recommendations; closure notes | "What may have been missed relative to the original goals" |

## Pass 2 — Audit items 2, 3, 4, 8 (2026-09-24)

| Artifact | What it is | Why |
|---|---|---|
| `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py` → `cv2x-testbed/results/pki_vs_erc1056.{csv,json,md}` | Identical seven-operation set through PKI, centralized and ERC-1056 providers; n=50, median/p95, exact gas, RPC counts, environment header, caveats | F2: the hypothesis says "alternative to PKI"; no PKI number existed |
| Provider fixes (`1d4ad07`) | Real on-chain key resolution in `erc1056_provider.py` (placeholder `"0x04..."` removed); vehicle-signed transactions | Blockchain verification had never worked on this trunk |
| `docs/MEASUREMENT_CONDITIONS.md` | Condition tags M0/M1/M2; reporting rules; reconciliation of four resolution latencies; claim register #1–#28 | F3: the same quantity had three values across documents |
| `docs/SCOPE_CHANGES.md` | SC-01…SC-11 with reasons and thesis treatment | F10: two roadmap criteria vanished without a record |
| `.github/workflows/*.yml` (rewritten), `1_blockchain-identity/package-lock.json` (tracked) | CI matching the trunk; honest compliance floor; gas-report artifact; nine-standard benchmark with drift check | F4/C5: first green CI in the project |
| `docs/figures/resolution_latency_M0.json` | N=30 cold/warm resolution latency per method | The single-run 0.05 ms was not chapter-grade |
| `docs/LATENCY_BUDGET.md` | SAE J2945/1-derived identity budget; neighbour saturation P*(f) from measured data; freshness trade-off | Item 7 (analytic half) |
| `docs/DID_METHOD_RUBRIC.md` | W3C DID Method Rubric v2.0 mapping; ledger-envelope vs discriminating criteria | Item 9 |
| README / thesis README edits | H1–H5 everywhere; priority claims reworded; estimate banners | Items 6, 10 |
| `docs/conformance/` (31 files) | External W3C DID test-suite run: implementations generated from the resolver, raw jest reports, write-up (328/441) | Item 5 / F5 |

## Pass 3 — Bundle recovery and merge (2026-09-24)

| Artifact | What it is | Why |
|---|---|---|
| Merge commit `781dc0b` | The analysis lineage (53 commits, tip `7118b83`) merged with per-file resolution; verified 47 contracts / 219 + 60 tests / 93.2% / gas re-executed | The nine-standard work existed only in the author's bundle |
| `4_comparison-framework/results/gas_*` (re-executed) | Nine-standard gas table under evm cancun; 1–2.8% below July, ratios unchanged | Results of record must come from the trunk |
| `docs/INDEX.md` | Which document is canonical for which question | Two documentation lineages now coexist |
| `docs/thesis/chapter5-results/README.md` (note) | Re-execution note | Chapter tables quoting July values must be regenerated |
| CI fixes (`21cf8bf`, `b75c69a`) | Dependencies for the merged checker; gate accepts "EXECUTABLE COMPLIANCE SCORE" | CI green again after the merge |

## Pass 4 — Review of the CV2X testbed lineage, grounding, MOBI/SUMO plan (2026-09-25)

| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_02.md` | Report 02, written from the start of the pass and updated as it ran; includes the tag explanation | Requested: "over explain … start from the beginning" |
| `docs/REVIEW_CV2X_TESTBED_LINEAGE.md` | Review of the sandbox guide and the five design documents against the trunk: plan vs actual, drift, grounding in ≥8 canonical works, innovation opportunities | Requested review |
| `docs/figures/make_review_figures.py` → `review_roadmap_timeline.png`, `review_criteria_matrix.png`, `review_architecture.png` | The three review figures, generated from the same status data as the text | "Include figures when necessary" |
| `docs/SESSION_MANIFEST_2026-09.md` | This file | "Organize this and other relevant outputs for this work session with a description" |
| `docs/PLAN_MOBI_SUMO.md` | The MOBI VID and SUMO plans with pre-registered experiment designs and prerequisites | Requested |

## Inputs the author supplied this session

- `cvin-thesis-latest.bundle` (through `7118b83`) — recovered and merged.
- `MASTER_UPDATE.md` (bundle-era status) — identical to the merged copy; historical.
- Five design documents (CAPABILITIES, CV2X_REALISTIC_ROADMAP, MOBI_VID_RESEARCH,
  MOBI_VID1_TECHNICAL_SPEC, MOBI_VID2_SSI_DESIGN) — the subject of the Pass-4 review;
  identical to the tracked copies except CAPABILITIES (the tracked copy carries the
  results-of-record banner).

## Things produced but deliberately not committed

- `w3c_compliance_report.json`, `gas-report.txt`, `w3c_compliance_output.log` —
  generated outputs, ignored.
- The two `.dbg.json` build-path changes under `cv2x-testbed/artifacts/` — noise.
- Local tags `v0.7.0`, `v0.8.0` — present, cannot be pushed from the session.

## Pass 5 — Grand sandbox, per-option sandboxes, layered suites (2026-10-03/04)

| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_04.md` | Report 04: brief, design step, every implementation step with its gate | step-by-step execution on request |
| `docs/REVIEW_02_STATE_AND_PARALLEL_WORK.md`, `docs/PLAN_SANDBOX_AND_SUITES.md`, `docs/META_COMMENTARY_2026-10.md` | the clean review, the clean plan, the thinking-out-loud | requested in that order |
| `docs/FEATURE_ASYMMETRY_MATRIX.md` + `4_comparison-framework/feature-matrix/make_feature_matrix.py` | the on-chain surface of every option from the compiled ABIs; CI fails if stale | ground the asymmetry in code |
| `sandbox/` (grand runner, options/<slug>/{manifest.yaml, adapter.js, demos/, README.md}, lib/, py-suites/, suites→test symlink) | the grand sandbox and the per-option sandboxes | B1–B3 of the brief |
| `1_blockchain-identity/test/{L1-identity-mechanisms,L2-identity-system}` | the layered Hardhat suites (99 + 220) | the four-layer test structure |
| `sandbox/grand/report/{asymmetry,L1-asymmetry,demos,GRAND_REPORT}.md` | generated: declared union, observed mechanisms, exercised surface, the whole run | the chapter's data |
| `docs/DEFECT_LOG.md` | 26 latent defects with severity, status, treatment | what the sandbox found |
| `docs/thesis/chapter6-discussion/section-feature-asymmetry.md` | draft section: union vs intersection, three axes, asymmetry budget | S10 |
| Contract fix `CVINVehicleCredential1155` self-transfer guard + regression test; `_research-copies/` archive; CI identity/freshness checks; `js-yaml` dev dependency | hygiene the steps required | — |

## Pass 6 — Fixing the high-severity defects (2026-10-04)

| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_05.md` | Report 05: the rule every fix had to meet, the plan F1–F7, the per-fix log, decisions D-E/D-F, closing | opened before the first fix, closed after the grand run |
| `cv2x-testbed/identity/mobi_vid_provider.py` (`f87f8c4`) + `sandbox/py-suites/L3-ssi/test_mobi_provider_key_binding.py` | D11: verification bound to the registered key, not the key in the message; 6 chain-free tests | the MOBI V2V security claim depended on it |
| `ERC1056Registry.sol` (both copies, byte-identical), `CVINCombinedIdentity.sol`, `CVINVehicleDIDRegistry.sol`, `MOBIVIDRegistry.sol` (`65a143f`) + 18 regression tests | D21 (revocation terminal, `previousChange` on `DIDRevoked`), D22 (`DIDClaimChanged`), D18 (100-year validity; birth record reachable), D10 (`0x` in `did:ethr`) | resolution correctness and conformance |
| `CVINVehicleNFT.sol`, `CVINVehicleCredential1155.sol`, `CVINVehicleLSP8.sol` (`241642e`) + 15 regression tests; `_l1.js`/`smoke.js` VIN prefix; ERC-1155 adapter | D13: one `_normalizeVIN` (upper-case, ISO 3779 alphabet, no check digit) in every mint and lookup path | Sybil-adjacent duplicate identities |
| `CVINVehicleClaimHolder.sol` (`ad470b6`) + 14 regression tests; adapter, security fixture, benchmark scripts | D25a/b: issuer registry and VIN binding of topic-1 claims; D25c recorded as a design decision | claim veracity |
| `4_comparison-framework/results/gas_benchmark.json`, `gas_comparison.{csv,tex}`, `gas_moved_by_defect_fixes_2026-10-04.json` (`2b38536`) | results of record re-executed after the fixes; 22 of 55 cells moved, each listed with its delta | decision D-E: numbers must describe the code |
| `docs/MEASUREMENT_CONDITIONS.md` #25 note, #31; README gas table; `docs/thesis/README.md` figures (`3a7a4ec`) | the register and the two READMEs quote the 2026-10-04 values | no stale number left in a document that cites gas |
| 92 demos + 8 READMEs under `sandbox/options/` (`5778651`, `eed6bfc`) | steps that asserted the defective behaviour now assert the fix; READMEs split fixed from still-open | the demos are the chapter's evidence of the surface |
| `docs/DEFECT_LOG.md` §B statuses, new §C (open items with the decision each needs) | the log reflects the fix pass | the chapter cites the log |
| `sandbox/grand/report/*` (regenerated) | the grand run on the fixed trunk | the chapter's data |

## Pass 7 — The remaining high-severity defects and the conformance follow-up (2026-10-04)

| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_06.md` | Report 06: plan G1–G5, per-step log, decisions D-G/D-H/D-I, closing | opened before the first change, closed after the grand run |
| `CVINVehicleCredential1155.sol` (`d941ad5`) + `soulboundRebinding.regression.test.js` (13 tests) | D7/D8: standard transfer entry points closed; held-type bitmap (`credentialTypesOf`, types ≤ 255); `issuerTransferIdentity` atomic re-binding (`IdentityRebound`); no orphaned credentials; `URI` event | the last open **H** item on a token option |
| `CVIN_NFT_DID_ERC721.sol` (`d941ad5`) + `payTollAfterRenounce.regression.test.js` | D9: no toll to `address(0)` | one-line veracity fix |
| `MOBIVIDRegistry.sol` (both copies, `d941ad5`) + `anchorVehicleKey.regression.test.js` (4) ; `cv2x-testbed/identity/mobi_vid_provider.py` + `test_mobi_provider_onchain_key.py` (7) | D11b: `anchorVehicleKey` (manufacturer once at birth, owner thereafter); provider anchors at registration and verifies from the chain when it has no local record; artifact ABI loaded (inline ABI lacked `isRevoked`) | completes the MOBI V2V security claim |
| `sandbox/options/{erc-1155,erc-721,mobi-vid}` demos + READMEs (`7404e94`, `d941ad5`), `adapter.js` (ERC-1155), manifests, `docs/FEATURE_ASYMMETRY_MATRIX.md` | every new function exercised; adapters use the whole-identity path | 100 % surface coverage kept |
| `4_comparison-framework/results/` — `gas_benchmark.json`, `gas_comparison.{csv,tex}`, `gas_moved_by_defect_fixes_2026-10-04_pass06.json`, `mobi_vid_backends.{json,csv,tex}`, `scaling_marginal.*`, `scaling_lifetime.*`, `w3c_compliance.json`; `scripts/mobi_vid_backend_sweep.js` (fixed) | results of record re-executed on the final contracts; the sweep ran on the trunk for the first time | decision D-E |
| `docs/thesis/chapter5-results/README.md` (regenerated tables + prose), README.md, thesis README, chapters 6–7 (cells) | no document quotes a pre-fix number | register discipline |
| `docs/conformance/` — `generate_implementations.py --ethr-did`, `implementations-registry-did/`, `reports/registry-did-2026-10-04/`, write-up §8 | external DID suite on a registry-minted `did:ethr`: 335/336 | D10 follow-up |
| `docs/MEASUREMENT_CONDITIONS.md` #26 → V, #30 note, #32; `docs/DEFECT_LOG.md` (D7/D8/D9/D11b fixed, D27 added, §C refreshed) | the register and the log reflect the pass | — |

## Pass 8 — Orientation after a change of assistant; plan of 2026-10-09 (2026-10-09)
| Artifact | What it is | Why |
|---|---|---|
| `docs/PLAN_2026-10-09.md` | the plan, delivered for audit before execution | the author asked to audit first |
| `docs/STYLE_AND_RIGOUR_GUIDE.md`, `docs/TEAM_STRUCTURE.md` | the rules in one place; the agentic team and what it learned | requested |
| `docs/AFTER_ACTION_REPORT_08.md`, `docs/META_COMMENTARY_2026-10-09.md` | report and thinking-out-loud for the orientation | standing rule |

## Pass 9 — Executing the plan under its defaults (2026-10-09)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_09.md` | log, decisions E-A…E-E, closing, team-structure assessment | standing rule; requested |
| `docs/HANDBACK_2026-10-09.md` | the single entry point; supersedes both lineages' handbacks | P0.5 |
| `1_blockchain-identity/results/metrics/latest/` | metrics-harness run of record on a clean tree | P0.3 |
| `sandbox/options/{cvin-combined,erc-1056-uport,lsp8,mobi-vid}/README.md`, `sandbox/grand/report/*` | READMEs at the merged contracts; grand run ALL OK | P0.1, P0.2 |
| `docs/figures/make_dashboard_data.py`, `dashboard_snapshot.json`, `dashboard_template.html`, `make_dashboard_page.py`, `results_dashboard.html` | the generated, CI-checked results dashboard; published at https://claude.ai/artifact/1C5X9GpPcEwyCRDMYxYhpa | P1 |
| `docs/thesis/cruxes.yaml` → `docs/thesis/CRUX_REGISTER.md` | eight thesis cruxes with their evidence state | P4.1 |
| `docs/design/INFRASTRUCTURE_MESSAGING.md`, `docs/PLAN_SUMO_VISUALISATION.md` | designs awaiting audit | P4.3, P2a |
| `docs/testing/{build_register.py,test_register.yaml,coverage_matrix.md,check_stamps.py,STAMP_INVENTORY.md,stale_numbers.yaml,check_docs_numbers.py}`, `1_blockchain-identity/scripts/lib/run_stamp.js` | TSR phases 1–3 on the trunk: generated register and matrix, stamping, stale-figure check | P3.1, P3.3, P3.4 |
| `docs/prior-survey/` | the onboarding lineage, imported as provenance | P3.5 |
| `docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md` v1.1 | pre-filled from the trunk; author decisions marked | P3.6 |
| 12 citing documents (README, CAPABILITIES, COMPOSITION, SIDE_PAPERS, QUICKSTART, INVENTORY, thesis README and chapters 1, 4–7) | 82 superseded figures replaced | P3.4 |


## Pass 10 — Building the approved designs: infrastructure messaging and the SUMO trace (2026-10-09)
| Artifact | What it is | Why |
|---|---|---|
| `docs/design/INFRASTRUCTURE_PREREG.md` | I1–I5 claims, conditions and verdict rules, locked before any code (`cfbdcbc`) | I-a approved |
| `docs/MILESTONE_NEXT.md` | deferred decisions N-1…N-17 (Infura rotation first) | the author's brief |
| `cv2x-testbed/sumo/infrastructure_layer.py`, `sandbox/py-suites/L3-ssi/test_infrastructure_layer.py` | road authority, RSU, controller and TMC identities; signed SPaT and I2I; 16 L3 tests | B1 |
| `cv2x-testbed/sumo/sumo_identity_integration.py` (`--rsu`, `--refresh-k`, `--revoke-rsu-at`, `--trace`) | harness flags, off by default; counts unchanged with them off | B2, V1 |
| `cv2x-testbed/sumo/run_infra_stats.py`, `1_blockchain-identity/scripts/infrastructure_gas.js` | I1/I2/I3/I5 driver over 30 seeds; I4 gas | B3 |
| `cv2x-testbed/sumo/results/infrastructure_{stats,revocation}.json`, `4_comparison-framework/results/infrastructure_gas.json` | results of record at `1e690c3`; register #44–#48 | B3, B4 |
| `cv2x-testbed/sumo/render_trace.py`, `results/traces/*.jsonl.gz`, `results/figures/*` | two traces of record, figures, GIF, dashboard replay | B5, V2, V3, V5 |
| `docs/thesis/chapter5-results/README.md` §5.4.1 | chapter section for I1–I5 | I-d |
| `docs/AFTER_ACTION_REPORT_10.md` | log, decisions F-A/F-B, closing | standing rule |

## Pass 11 — Adversarial review of passes 9–10 and the run-identity fixes (2026-10-09)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_11.md` | plan, log, findings register (33 findings, every one with a disposition), decisions G-A…G-E, closing, team assessment | standing rule; next executable |
| `1_blockchain-identity/scripts/lib/run_stamp.js`, `cv2x-testbed/sumo/{sumo_identity_integration,run_v2v_stats}.py`, `docs/testing/probe_run_identity.sh` | producing-code clean flags that fire (`:(top)` pathspecs, results excluded), `code_clean`, CI probe | R0/R3, N-14, C1 |
| `docs/testing/check_stamps.py`, `STAMP_INVENTORY.md` | both polarities, inert and hand-check marks, classes for unstamped files | R3, R4, C2 |
| `docs/design/INFRASTRUCTURE_PREREG.md` §4 | amendments A1–A3 (post hoc) and A4 (before the re-run) | A2, B1–B5 |
| `cv2x-testbed/sumo/infrastructure_layer.py`, harness attacks, `run_infra_stats.py`, L3 tests (16 → 31) | verifier hardened: binding, replay, warm expiry, distinct reasons; 13 I2 checks | B1–B7 |
| `cv2x-testbed/sumo/results/infrastructure_{stats,revocation}.json`, traces, figures, `4_comparison-framework/results/infrastructure_gas{,_run1}.json` | results of record at `f1f9e37`; register #44–#48 rewritten with history | A4 re-run |
| `docs/testing/{check_docs_numbers.py,stale_numbers.yaml}`, `docs/figures/make_dashboard_{data,page}.py`, `dashboard_template.html`, `docs/testing/build_register.py` | hardened generated-document checks | C3–C9 |
| chapter 5 §5.4.1, `docs/thesis/cruxes.yaml` C3/C4, meta commentary §7–§8, INVENTORY, SOURCES, MASTER_UPDATE banner, `3_cv2x-testbed/README.md` | claims reworded to what was measured; stale figures fixed | A1–A7, C4, C10, C11 |

## Pass 12 — Closing work milestone WM-1: plan review, backward fixes, report, audit, presentation (2026-10-10)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_12.md` | plan W0–W7, defaults D-1…D-5, log, findings register (88), decisions H-A…H-E, closing conditions, team assessment | standing rule |
| `docs/milestones/README.md`, `WM-1_REPORT.md` | milestone scheme; the detailed WM-1 report (pre-audit at `d61a284`, revised after) | requested |
| `docs/milestones/audit_WM-1/` (briefs, findings), `docs/milestones/review_pass11/` | audit briefs by a separate brief-writer; five auditors' and three pass-11 reviewers' reports, verbatim | requested; P-F10 |
| `docs/PLAN_WM-2.md`; `docs/PLAN_2026-10-09.md` §5 | the reformulated plan; status of every item of the executed plan | requested |
| `docs/HANDBACK_2026-10-10.md` | consolidated handback, supersedes 2026-10-09 | closing condition 7 |
| `docs/presentation/` (`make_presentation.py`, `REPORT_DRAFT_1.md`, `report_page.html`, figures, `EXPANSION_PLAN_DRAFT2.md`) | presentation report draft 1, generated from committed data, and what draft 2 expands | requested |
| backward fixes: `DEFECT_LOG.md` §F–§G (D28–D57), style guide, team structure, SC-21/22, CHANGELOG, chapters 1/4/5/6/7, README, register rows #4, #27, #29–#36, #39, #44–#48 | the review findings and the audit's | requested |
| tests and tooling: `mutation/mutate_infrastructure_layer.py`, `test_proof_options_signed.py`, `test_aggregator_checks.py`, `balanceCountsTokens.regression.test.js`, `check_test_counts.py`, CI skip gate and PR triggers, stamp inventory column | guards the audit showed missing | audit |
| `4_comparison-framework/results/infrastructure_gas_runs/` | I4 over 30 runs | A-F3, B-F9 |

## Pass 13 — Work milestone WM-2, step A1 (2026-10-10)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_13.md` | plan, log, closing | standing rule |
| `docs/testing/check_stamps.py` (`--check-coverage`), `STAMP_INVENTORY.md`, CI step | every tracked result file accounted for; CI fails on an unaccounted one | WM-2 A1, N-21 |

## Pass 14 — Work milestone WM-2, step A2 (2026-10-12)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_14.md` | plan, log, closing | standing rule |
| `tools/run_identity/producers.json`, `scopes.json`, `stamp.py` | 20 producers of record, each with its resolved import closure and declared inputs; the Python stamp helper; `--check` in CI | WM-2 A2, D49 |
| `1_blockchain-identity/scripts/lib/run_stamp.js` | the JS helper, reading the same scopes | same |
| 14 producers (6 JS scripts, 4 SUMO drivers, 3 testbed experiments, the richness driver) | call the helper with their own file; stamp field names kept | same |
| `tools/run_identity/probe.py`, `docs/testing/probe_run_identity.sh`, CI step | both helpers, every producer: edit to imported code, new input file, new results file; shown to fail on four broken helpers | same |
| `docs/testing/check_stamps.py`, `STAMP_INVENTORY.md` | "code changed since" from the scopes; stamp-only commits verified line by line | same |

## Pass 15 — WM-2 step A4; Phase 2 opened; handback for the next session (2026-10-14)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_15.md` | plan, log, closing | standing rule |
| `tools/run_identity/promote.py`, `test_promote.py` | runs and the promote step; 13 refusal tests (in CI) | WM-2 A4 |
| `1_blockchain-identity/scripts/lib/run_stamp.js` (`newRun`, `writeManifest`, `commitFull`), `attackHarness.js`, `securityScenarios.test.js`, `package.json` (`security:promote`), `.gitignore` (`/runs/`) | the security matrix written to `runs/` and promoted explicitly | WM-2 A4, D56 in part |
| `tools/run_identity/producers.json`, `scopes.json` | the security-matrix producer corrected to `securityScenarios.test.js` | A2 gap found in A4 |
| `docs/phase2/` (README, EVIDENCE_BASE, ideas.yaml, IDEA_REGISTER, build_phase2.py, ARCHITECTURE, ROADMAP, BRAINSTORM_01, DECISIONS, sessions/SESSION_LOG) | Phase 2 charter and P2.0 ideation; register checked in CI | the author's request of 2026-10-14 |
| `docs/HANDBACK_2026-10-14.md` | consolidated handback, including what a new assistant model must know | standing rule; change of assistant |

## Pass 16 — WM-2 C0; Phase 2 focuses F1–F3; scope reconciliation; academic review (2026-10-14)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_16.md` | plan, log, closing | standing rule |
| `docs/design/INFRASTRUCTURE_PREREG.md` amendment A6 | verifier v3 and the extended I2, before any change | WM-2 C0 |
| `cv2x-testbed/sumo/infrastructure_layer.py`, `run_infra_stats.py`, `sumo_identity_integration.py`; `cv2x-testbed/identity/erc1056_provider.py` | verifier v3 (D37–D42); the D51 fix | WM-2 C0 |
| `sandbox/py-suites/L3-ssi/test_infrastructure_v3.py`, mutation script; `cv2x-testbed/tests/test_d51_chain_time.py` | regression tests failing on the old code; 39/39 mutants | WM-2 C0 |
| `cv2x-testbed/sumo/results/infrastructure_{stats,revocation}.json`, `run_logs/2026-10-14_7d08dce/` | I1–I3, I5 runs of record at `7d08dce` | WM-2 C0 |
| `docs/MEASUREMENT_CONDITIONS.md` | #44–#46, #48 re-stated; #49–#51 added; dated corrections (#49, M2 tag); D51 update | C0; F1–F3; review |
| `docs/phase2/focus/F1_onchain_storage_idtx/`, `F2_chains_and_databases/`, `F3_interaction_modes/` | the three author-designated focuses | the author's request |
| `phase2/idtx/` (contracts, tests, `mutate_idtx.sh`), `1_blockchain-identity/hardhat.phase2.config.js` | the IDTx prototype | F1 execution start |
| `phase2/backends/` | the database lifecycle backend with a hash-chained journal | F2 execution start |
| `docs/phase2/focus/F3_interaction_modes/classify_modes.py`, `MODE_CLASSIFICATION.md` | the generated mode classification | F3 execution start |
| `docs/phase2/focus/make_focus_figures.py`, `FIGURES.md`, `figures/` | four generated figures and their tables | figures |
| `docs/phase2/SCOPE_RECONCILIATION.md`, `reviews/` | the scope across its revisions; the academic review and its dispositions | writing team |
| `docs/phase2/PHASE2_PROGRAMME.md`, `CHAT_WORKSPACE_BRIEF.md`, `inbox/` | the consolidated document; the hand-off to a chat workspace | the author's request |

## Pass 17 — WM-2 B1: deterministic gas, or ranges by rule (2026-10-14)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_17.md` | plan, log, closing | standing rule |
| `sandbox/lib/determinism.js`; `sandbox/grand/run.py` (seeded stages); `sandbox/options/erc-725xy/adapter.js`, `erc-735/adapter.js` (counters) | incidental randomness seeded | B1, N-18 |
| `1_blockchain-identity/scripts/infrastructure_gas.js`; `4_comparison-framework/results/infrastructure_gas.json`, `infrastructure_gas_runs/` | I4 over declared seeds, inputs recorded; runs of record at `a950cdf` | B1 |
| `docs/STYLE_AND_RIGOUR_GUIDE.md` 1.1.10; `docs/MEASUREMENT_CONDITIONS.md` §1, #47 | the rule; the re-stated row | B1 |


## Pass 18 — WM-2 B2 gas charter; result cards (2026-10-15)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_18.md` | plan, log, closing | standing rule |
| `docs/testing/gas_charter.py`, `GAS_CHARTER.md`; `docs/MEASUREMENT_CONDITIONS.md` §5.A (gas class row) | class-G charter; varying harness cells root-caused; V gas rows classified | B2 |
| `docs/figures/make_result_cards.py`, `result_cards.html` | every V register row as a card, checked against the register | the author's request |
| `.github/workflows/test-contracts.yml` | both checks in the document step | CI |
| `docs/PLAN_WM-2.md`, `docs/HANDBACK_2026-10-14.md` §10 | B2 done; next C3 | records |

## Pass 19 — WM-2 C3; contribution record (2026-10-15)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_19.md` | plan (C3 decision rule first), log, closing | standing rule |
| `cv2x-testbed/results/freshness_k_c3/` | six C3 runs at `8216507` and `f660402`, with a manifest | C3 |
| `docs/MEASUREMENT_CONDITIONS.md` #52; notes on #32 and #37; `docs/testing/check_stamps.py` aggregate | the host comparison | C3 |
| `docs/figures/make_contribution_record.py`, `contribution_template.html`, `contribution_record.html` | the contribution calendar with sourced evidence | the author's request |
| `docs/figures/make_result_cards.py` (card #52), `docs/PLAN_WM-2.md`, `docs/HANDBACK_2026-10-14.md` §11 | records | records |

## Pass 20 — Technical Data Package (parallel pass, 2026-10-15)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_20.md` | plan T0-T7, log, closing | standing rule |
| `docs/tdp/README.md` (TDP-000) | index, conventions, sources for the formats | the author's request: a parallel document set in the engineering register |
| `docs/tdp/requirements.yaml`, `make_vcrm.py` → `TDP-002_SYSTEM_SPECIFICATION.md`, `TDP-005_VERIFICATION_CROSS_REFERENCE_MATRIX.md` | 36 shall-statements; statuses computed from the register, snapshot, tree and CI | T3 |
| `docs/tdp/make_blueprints.py` → `drawings/DWG-001..006.svg`; `TDP-004_DESIGN_DESCRIPTION_AND_BLUEPRINTS.md` | six blueprint sheets with title blocks, notes and bills of materials, every number read from a file | T4 |
| `docs/tdp/make_fmeca.py` → `TDP-006_FMECA.md` | failure-mode worksheet over every logged defect, counts cross-checked with the snapshot | T5 |
| `docs/tdp/TDP-001_PROGRAM_SUMMARY.md`, `TDP-003_INTERFACE_CONTROL_DOCUMENT.md`, `TDP-007_TEST_AND_EVALUATION_MASTER_PLAN.md`, `TDP-008_CONFIGURATION_BASELINE.md`, `TDP-009_RISK_REGISTER.md` | hand-written documents, every number a V row | T6 |
| `docs/tdp/TDP-PLAN.md`, `TDP-RUNBOOK.md` | the plan with status and findings; the plan as phases with prompts | T1, T2 |
| `docs/tdp/probe_tdp_checks.sh`; `.github/workflows/test-contracts.yml`; `docs/testing/stale_numbers.yaml` | the three checks and their probe in CI; the worksheet exempted as a record | T7 |
| `docs/INDEX.md`, `docs/HANDBACK_2026-10-14.md` section 12 | records | records |
## Pass 21 — WM-2 C1: did:ethr resolution reads the chain (2026-10-15)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_21.md` | plan, defaults, log, closing | standing rule |
| `2_w3c-ssi-layer/did-resolution/did_resolver.py`; `tests/test_did_resolver_chain.py`; two tests in `mobi-vid/tests/test_mobi_vid_layer.py` | the chain path and its tests (9 of 11 fail on the old code) | C1 |
| `docs/MEASUREMENT_CONDITIONS.md` (#4, #24 notes), `docs/MOBI_VID_CHECKLIST.md` (VID-R1), `docs/MILESTONE_NEXT.md` (N-24), `docs/PLAN_WM-2.md` | records | C1 |
| `docs/tdp/requirements.yaml` STD-01, TDP-002, TDP-005 | the one change report 20's guard asked for | coordination |

## Pass 22 — WM-2 C2: attestation restricted (D54); hand-off and check brief (2026-10-17)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_22.md` | plan, defaults, log, closing | standing rule |
| `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol`, `MOBIVIDRegistryV2.sol`; tests; scripts; Python MOBI client; MOBI demos | the fix and its callers | C2 |
| `4_comparison-framework/results/gas_benchmark.json`, `gas_comparison.*`, `mobi_vid_backends.json`, `scaling_*.json`, `security-analysis/results/onchain_security.json` | re-runs of record at `92cc4d5` | C2 |
| register #25, #26, #28; `docs/testing/stale_numbers.yaml`; chapters 5 and 6; README, CAPABILITIES, QUICKSTART; DEFECT_LOG D54; THREAT_MODEL G4; N-25 | records | C2 |
| `docs/HANDOFF_2026-10-17.md`, `docs/milestones/check_passes_16-22/CHECK_BRIEF.md` | hand-off and the check brief for the other model | the author's request |

## Pass 23 — Phase 2 session 3: deep-dive briefs (2026-10-20)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_23.md` | plan, log, closing | standing rule |
| `docs/phase2/briefs/I-24_IDTX.md`, `I-24_sources.json`, `I-05_FRESHNESS.md`, `I-05_sources.json` | the two briefs with every cited source's URL and quote | session 3 |
| `docs/phase2/sessions/SESSION_LOG.md` entry 3; `ideas.yaml` (I-24 test count) | records | session 3 |
| `docs/milestones/check_passes_16-22/START_PROMPT.md`; `docs/planning/PROGRESS_REPORT_PLAN_2026-10-20.md` | the fresh-session prompt; the plan for the hand-over write-up | the author's requests |

## Pass 24 — Lead's pass: decision sheet, pre-push guard, progress report (2026-10-20)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_24.md` | plan, log, closing | standing rule |
| `tools/prepush_check.sh` | CI's document and copy guards, run locally before a push; probe included | pass 22's three red runs |
| `docs/DECISION_SHEET_2026-10-20.md` | every open author decision on one page | the backlog was scattered over five files |
| `docs/PROGRESS_REPORT_2026-07_TO_2026-10.md`, `docs/make_progress_appendix.py`, `PROGRESS_APPENDIX_2026-07_TO_2026-10.md` | the hand-over write-up, draft 1, with its generated commit appendix | the author's request |

## Pass 25 — TDP runbook phase 10: thesis adaptation map (2026-10-21)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_25.md` | plan, log, closing | standing rule |
| `docs/tdp/TDP-010_THESIS_ADAPTATION_MAP.md` | requirements onto chapter 3; drift table; outline v2 | the author's request |
| `docs/tdp/README.md`, `TDP-RUNBOOK.md`, `TDP-PLAN.md`; handback section 16 | records | records |

## Pass 27 — TDP runbook phases 8 and 9 (2026-10-22)
| Artifact | What it is | Why |
|---|---|---|
| `docs/AFTER_ACTION_REPORT_27.md` | plan, log, closing | standing rule |
| `docs/tdp/requirements.yaml` (`tests`), `make_vcrm.py`, TDP-005 section 3 | requirement-to-test trace with its guard | phase 8 |
| `docs/tdp/check_icd.py`; `probe_tdp_checks.sh`; `.github/workflows/test-contracts.yml` | the ICD gate, its probe, its CI line | phase 9 |
| `docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md` | IF-04 as built after C1; two shorthand tokens reworded | held by the gate |
| `docs/tdp/make_blueprints.py`, `drawings/` | corrected test path; document-check list regenerated | records |
## Pass 28 — Plan 1: ZKP and the agent-wrapped identity (2026-10-15)
Outputs: `docs/zkp/` (plans 1 and 2 with phased prompts; reports A, B, C; sources; integration map; citation checker);
`5_zkp-agent-identity/` (zkid, ZK-VIN circuit and artefacts, ZkVinGate, Schnorr verifier, the Steward, attacks, bench,
figures, demo, tests, mutation probe); `1_blockchain-identity/hardhat.zkp.config.js`; `.github/workflows/zkp-layer5.yml`;
README section. Report: `docs/AFTER_ACTION_REPORT_28.md`.
