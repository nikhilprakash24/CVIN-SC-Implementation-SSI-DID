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

