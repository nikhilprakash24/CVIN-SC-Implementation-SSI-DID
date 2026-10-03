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
