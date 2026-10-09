# Testing Suite & Results Plan — Second-Pass Sheet

**Companion to:** `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` (TSR Plan v1.0)
**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-04 · **Sheet version:** 1.1 (pre-filled 2026-10-09 from the merged trunk; author decisions marked AUTHOR)
**Purpose:** the author's second pass over the plan, done from chat. Every item has an ID; answer by ID in any order ("D-03: option b", "P-07: see photo 12", "C-erc735-U2: N, no key management"). Items left blank take the stated default. The filled sheet is the input to Phase 2 and is kept under version control, so the paper notes end up redundant with the repository (S13).

### Pre-fill of 2026-10-09 (plan `docs/PLAN_2026-10-09.md` step P3.6)

**What was pre-filled.** Each D-decision now records either the decision already taken on the
trunk, with the file and section that took it, or **AUTHOR**, meaning nothing on the trunk decided
it and the sheet's default stands unless the author overturns it. Each V-verification says whether
it can be checked by reading the repository and, if so, what the files show. Each O-finding says
whether it still holds on the trunk. Sections C, Q and S carry short trunk notes where a file
settles a fact. Sections P and R are the author's and are left blank. No pre-filled line is the
author's answer.

**Where from.** The merged trunk `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy`, read at
`5a83bc2` (2026-10-09). The sources are `docs/testing/README.md` §2 (how TSR maps onto the
sandbox, decisions taken at the merge); `docs/reconciliation/RECON_TSR.md` §4 (13 naming
conflicts); `docs/PLAN_MERGE_LINEAGES.md` §1 (M-A…M-L, standing by default per
`docs/AFTER_ACTION_REPORT_09.md` §0, Q5); `docs/PLAN_2026-10-09.md`; `docs/AFTER_ACTION_REPORT_07.md`
to `_09.md`; `docs/HANDBACK_2026-10-04.md` §4; `docs/MEASUREMENT_CONDITIONS.md`;
`docs/SCOPE_CHANGES.md`; `docs/STYLE_AND_RIGOUR_GUIDE.md`; and the code and result files named
in each row. Commands run were read-only (`git rev-parse`, `git diff --stat`, `grep`, JSON reads,
and `docs/testing/check_docs_numbers.py`, which only reads).

**Caveats.**
1. The TSR inventory was taken on the review-2 tree `fa6188e`, before the merge. Paths moved:
   `test/<Std>/` is now `1_blockchain-identity/test/L2-identity-system/per-option/<Std>/`, and
   `test/security/` is now `test/L2-identity-system/security/`. `test/benchmarks/` and
   `benchmarks/` kept their paths. Every row below cites the current path.
2. The trunk moved during this pre-fill: P0.3 (`f976e57`), P3.3 and P3.4 (`230ac1a`, `5a83bc2`)
   landed while it was written, and the rows were re-checked against `5a83bc2`. Uncommitted edits
   in the working tree at that time (one CI line, two sandbox reports) are not relied on.
3. The merged handback `docs/HANDBACK_2026-10-06.md` (plan P0.5) does not exist yet. The AUTHOR
   rows below are the list it should carry.

**Counts.** D: 6 decided on the trunk, 4 partly decided, 20 AUTHOR. V: 9 checked against files
(V-02 only in part), 6 not checkable by reading files. O: 15 hold, 4 partly resolved, 1 resolved.

How to use in chat, in one message or several:

```
D-01 b
V-04 confirmed
P-01 kind=function sut=erc1056,cvin op=U6 cls=F,A note="recovery via delegate quorum — notebook 2 p.14"
C-erc1155-U2 N "soulbound: operators have no power"
Q-3.2 "keep E-levels but merge E6/E7"
```

Legend for cells: **T** tested · **N** n/a, no primitive (give the reason) · **G** gap, add it · **P** on paper, intake · **X** out of scope (SC entry will be drafted).

---

## Section D — Decisions the plan needs (defaults in bold)

| ID | Decision | Options | Default | Answer |
|---|---|---|---|---|
| D-01 | Where the organised suite lives | a) `docs/testing/` + `tools/testing/` (additive; nothing moves) · b) new top-level `5_testing-suite/` to match `1_…4_` · c) inside `4_comparison-framework/` | **a** | **Decided on the trunk: a, adapted.** Generated documents go under `docs/testing/`; `tools/testing/` ≡ `sandbox/grand/` (`docs/testing/README.md` §2 row 2; `RECON_TSR.md` §4 #2). Note: the builders landed as `docs/testing/build_register.py`, `check_docs_numbers.py` and `check_stamps.py` (`aef16af`, `230ac1a`), not under `sandbox/grand/`. There is no `tools/` directory. |
| D-02 | Tagging mechanism | a) tag in test titles/markers, registers generated · b) hand-maintained register only · c) both, with CI cross-check | **a** | **Decided on the trunk: a** (`docs/testing/README.md` §2 row 1: "TSR tags go into test titles on either layout"; `PLAN_2026-10-09.md` P3.1). The first implementation differs. `build_register.py` (`aef16af`) derives TC ids from `L1-asymmetry.json`, `attack_results.json` and `demos.json`, and "no test title is changed". No pytest marker exists, and the Python suites are not in `test_register.yaml`, whose counts block lists only L1, the security harness and the demos. |
| D-03 | Matrix cell vocabulary | a) `T/N/G/P/X` as proposed · b) add `W` (weak: test exists but assertion is loose) as a sixth value · c) other | **b** is recommended if ERC-721 legacy tests stay | **AUTHOR. Default b stands unless overturned.** The trunk decided only the derivation rule: manifest `not-applicable` ⇒ N, L1 ✓ ⇒ T, `implemented` with no test ⇒ G (`docs/testing/README.md` §2 row 4). `RECON_TSR.md` §4 #4 recommends W. The ERC-721 legacy files are still present with 0 revert assertions (`per-option/ERC721/regularExtended.js`, `identityBased.js`). Conflict to settle: `docs/testing/coverage_matrix.md` uses X = "demo failing" plus a `+M` suffix, while S12 reserves X for out of scope. |
| D-04 | Tiers | a) smoke / full / measure · b) full / measure only · c) add `external` for Sepolia/SUMO/W3C suite | **c** | **AUTHOR. Default c stands.** `RECON_TSR.md` §4 #11 concurs: tiers are tags, and `external` is the manual external-suite run that `sandbox/py-suites/L3-ssi/test_external_did_conformance_regression.py` guards. No tier tag exists on the trunk. |
| D-05 | Recovery as a catalogue op (`U6_recover_controller`) and re-mapping ERC-4337 R4/U2/D1 to n/a | a) yes, accept the 4337 core-ops count change · b) keep the guardian-as-delegate mapping with a note · c) defer | **a** | **AUTHOR. Default a stands.** Nothing decided. The 4337 adapter still maps the guardian to R4/U2/D1 (`1_blockchain-identity/benchmarks/adapters/erc4337.adapter.js:79,104`). `DEFECT_LOG.md` D15 (the guardian persists after recovery) is an open author question. `build_register.py` maps the L1 `claim` mechanism to a proposed op **V7** add-claim, alongside U6 (`RECON_TSR.md` §4 #6). |
| D-06 | MOBI VID adapter in the harness | a) add `mobi.adapter.js` (declared n/a where VID II lacks a primitive) · b) keep MOBI as application profile only (sweep + benchmark_gas) | **a** | **AUTHOR. Default a stands.** The harness still has no MOBI adapter: `1_blockchain-identity/benchmarks/adapters/` holds ten. The sandbox L1 has `sandbox/options/mobi-vid/adapter.js`, which serves a different harness (`RECON_TSR.md` §3). |
| D-07 | Non-deterministic gas cells (14) | a) fix fixtures so every cell is exact · b) report `mode [min,max]` with cause · c) both: fix where the cause is the fixture, report where it is the standard | **c** | **AUTHOR. Default c stands.** The same 14 cells are non-deterministic in the new run of record (see V-06). `MEASUREMENT_CONDITIONS.md` §5.B (revised `gasUsed` row) names the causes. No fixture was changed. |
| D-08 | Use-case suite backend | a) keep `central` + add MOBI V2 backend · b) replace with MOBI V2 only · c) run on all five sweep backends | **a** | **AUTHOR. Default a stands.** The use cases now run in CI as 12 pytest cases (`sandbox/py-suites/L4-exemplar-interactions/test_lifecycle_use_cases.py`). They still run on `CentralizedVehicleRegistry` only, and there is no MOBI V2 backend. |
| D-09 | Statistics in latency tables | a) add bootstrap CI + Mann–Whitney/Cliff's δ columns, Holm-corrected · b) CI only · c) leave descriptive with footer | **a** | **AUTHOR. Default a stands.** `bootstrapMedianCI` and `mannWhitneyU` are referenced only in `benchmarks/lib/stats.js` and `test/benchmarks/stats.test.js`. |
| D-10 | Results producers write to `runs/` and promote explicitly (no script overwrites tracked results) | a) yes, all producers · b) only the ones listed in HANDBACK §6 | **a** | **Decided on the trunk: a, for results of record.** `docs/testing/README.md` §2 row 7 says "adopt promote/superseded for the results of record; keep the delta files". `RECON_TSR.md` §4 #7 exempts the derived `sandbox/grand/report/*`. The step is scheduled as `PLAN_2026-10-09.md` P3.3. State at `5a83bc2`: a run-stamp helper is in four JS producers (`1_blockchain-identity/scripts/lib/run_stamp.js`, `230ac1a`), and `docs/testing/STAMP_INVENTORY.md` reports 11 of 25 results fully stamped. There is no `runs/`→promote for `4_comparison-framework/results/` and no `superseded/` directory. |
| D-11 | Machine-readable claim register (`claims.yaml`) | a) mirror, prose stays canonical · b) make YAML canonical and generate the prose table · c) none | **a** | **AUTHOR on a vs b. Default a stands.** The trunk ruled out c: `claims.yaml` with stable string ids is adopted (`docs/testing/README.md` §2 row 8; `PLAN_2026-10-09.md` P3.2). P3.2 says the register is "generated from or checked against it", which leaves a and b open. Not built yet: there is no `docs/testing/claims.yaml`. |
| D-12 | Work-item names M1–M7 (PLAN_MOBI_SUMO) that collide with condition tags | a) rename work items W1–W7 in a note; never touch tags · b) leave; add a glossary line | **a** | **AUTHOR. Default a stands.** Not done: `docs/PLAN_MOBI_SUMO.md` lines 32–36 still name work items M1–M5. The sister collision (harness L1–L8 against suite layers L1–L4) was decided: the harness levels are renamed in prose (`docs/testing/README.md` §2 row 3; `RECON_TSR.md` §4 #3). The merge added a third M-series, the decisions M-A…M-L (`PLAN_MERGE_LINEAGES.md` §1). |
| D-13 | Reporting standards to cite in charters | a) ACM SIGSOFT Empirical Standards (Benchmarking, Engineering Research) + ACM badging · b) add ISO/IEC/IEEE 29119 test documentation · c) a) only | **a** | **AUTHOR. Default a stands.** Nothing on the trunk decides this. No charter exists yet. |
| D-14 | Replication protocol target | a) second host for every L/S result of record · b) second replicate same host, second host for headline rows only (#27, #32/#37, #21) · c) none beyond today | **b** | **AUTHOR. Default b stands.** No replication protocol is on the trunk. Register #37 was measured on a second host and is marked "host-dependent: never mix with #32". |
| D-15 | Phase 8 (Sepolia, real SUMO) | a) schedule after Phase 7 · b) interleave with Phase 5 · c) out of this plan | **a** | **AUTHOR. Default a stands.** The SUMO half is gated by `PLAN_2026-10-09.md` Q2, taken as "no install" (`AFTER_ACTION_REPORT_09.md` §0). Sepolia is not scheduled anywhere: M2 is "not yet run on this trunk" (`MEASUREMENT_CONDITIONS.md` §1). |
| D-16 | Commit attribution for this stream | a) author-attributed, no AI trailers (repo standing rule B.1) · b) default tool attribution | **a** (applied to this pass) | **Decided on the trunk: a.** Sources: `STYLE_AND_RIGOUR_GUIDE.md` §1.3 item 1; `HANDBACK_2026-10-04.md` §7; `AFTER_ACTION_REPORT_08.md` decision O-C, where the author's rule takes precedence over the attribution the session environment supplies; `RECON_TSR.md` §4 #13. Observation: the root `TEST_ONBOARDING.md` ends with a tool-attribution line, contrary to §1.3 item 1. |
| D-17 | Version bump on completion | a) 0.9.0 at Phase 7 · b) 0.9.0 only with a Sepolia witness (per handback) · c) 0.8.x | **b** | **AUTHOR. Default b stands.** The last release in `CHANGELOG.md` is 0.8.0 (2026-07-15). Tags v0.7.0 and v0.8.0 exist in the local clone but not on `origin`, where `git ls-remote --tags` lists only `asfound/pre-onboarding`. |

Pending author decisions already on file (answer here or in `HANDBACK_2026-10-04.md` §4; the plan does not depend on them but Phase 7's docs reconciliation does). The sheet gives no default for D-20…D-32, so an AUTHOR row names the handback's recommendation where it gives one.

| ID | Decision (handback ref) | Answer |
|---|---|---|
| D-20 | H1 wording (Q-3): "~10× create (bare 10.3×, VIN-bound 6.9×); lifetime 2.6×/3.0×" vs restated hypothesis | **AUTHOR.** Nothing decided (`HANDBACK_2026-10-04.md` §4 item 1). On the merged contracts the bare ratio reads 10.4× (register #6 merge note, 52,594 vs 545,101). The VIN-bound 6.9× is not restated there. The lifetime figures are 2.57× / 3.00× (#30). |
| D-21 | Checker strictness T-7/T-8 and the 7.1.2 correction (#4; 94.3 % vs 92.0 %, CI floor) | **Partly decided at the merge, by default.** The corrected 7.1.2 check is kept: M-F takes "theirs … corrected 7.1.2 check" (`PLAN_MERGE_LINEAGES.md` §1). The floor is 94.0 (M-L; `.github/workflows/w3c-compliance.yml:124`), against a measured 94.3 % (`AFTER_ACTION_REPORT_07.md` §2). Both defaults stand until overturned (`AFTER_ACTION_REPORT_09.md` §0, Q5). **AUTHOR:** the T-7/T-8 strictness and the "structural" label, which register #4 marks "Author decision pending". |
| D-22 | K-4 residual (manufacturer can birth an unused did:ethr) | **AUTHOR.** The K-4 guard is in the merged `MOBIVIDRegistry` (`AFTER_ACTION_REPORT_07.md` §2). The residual named in `HANDBACK_2026-10-04.md` §4 item 3 is not addressed. |
| D-23 | attestEvent duplicates / restrict to current owner and delegates (moves #28) | **AUTHOR.** The code is unchanged. `MOBIVIDRegistryV2.attestEvent` admits any authorised issuer role and appends with no duplicate check (`1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol` lines 335–373). The M3 pin is now 169,361 (register #28 merge note). |
| D-24 | K-5 (cv2x `ERC1056Registry` vs `EthereumDIDRegistry`): rebuild or keep caveat | **Decided by default on the sandbox lineage: keep the caveat and name the variant.** Both contracts are kept, as "ERC-1056 / uPort-style" and "ERC-1056 / vehicle profile" (`MEASUREMENT_CONDITIONS.md` §1.1, "decision of 2026-10-04, plan S0"). Rows #21, #22, #32 and #37 carry the K-5 caveat. The author may still order the rebuild. |
| D-25 | K-12 keep `EthereumDIDRegistry` byte-faithful | **AUTHOR.** `HANDBACK_2026-10-04.md` §4 item 6 recommends keeping it byte-faithful. The trunk has no upstream-faithfulness check. The CI byte-identity gate covers only the three MOBI copies (`.github/workflows/test-contracts.yml`, step at line 38). |
| D-26 | MOBI claim wording ("MOBI-VID-inspired profile") and SC-14–SC-20 | **Partly decided by default at the merge.** The wording is "a MOBI-VID-inspired profile, checked against the public texts" (`SCOPE_CHANGES.md` SC-14a). SC-15 and SC-16 are out of scope, and SC-19 is deferred. **AUTHOR:** SC-17, SC-18 and SC-20, each marked "Decision pending". Inconsistency to fix: `SCOPE_CHANGES.md` line 49 lists SC-15…SC-20, but line 52 says the checklist's proposals became SC-15…SC-21 (M-H). |
| D-27 | H3 design point: k, host, f to defend (#32/#37/#39) | **AUTHOR.** Nothing decided (`HANDBACK_2026-10-04.md` §4 items 10 and 14). #32 puts the knee at k ≈ 146. On the second host, #37 finds that no finite k reaches P*(0.5) = 100. `docs/thesis/CRUX_REGISTER.md` C4 names the host dependence as the gap. |
| D-28 | M4 verdict wording (#33) | **Decided by standing rule:** the result is reported as FAIL, as pre-registered (`STYLE_AND_RIGOUR_GUIDE.md` §1.2 item 1; register #33 reads "FAIL", with the post-hoc explanation labelled). The chapter sentence still needs the author's framing approval (`HANDBACK_2026-10-04.md` §4 item 7). |
| D-29 | Privacy framing (#38): per-pseudonym identities + relayer? | **AUTHOR.** Nothing decided (`HANDBACK_2026-10-04.md` §4 item 15). SC-02 is partly closed and SC-19 is deferred (`SCOPE_CHANGES.md`). |
| D-30 | H5 wording given #36 (hybrid dominated by ERC-4337 on all six criteria) and the criteria change from pre-registration | **AUTHOR.** Nothing decided. The criteria drift still holds (see O-16). The P0.3 re-run left the frontier and dominance unchanged (`f976e57`). |
| D-31 | Chapter stale-figure list (handback §4.7/§4.12): approve the replacement values | **Done on the trunk; approval still the author's.** `5a83bc2` replaced 82 superseded figures in 12 citing documents with the current register values. `docs/testing/check_docs_numbers.py` now reports "0 stale figure(s) in 0 file(s)", and the remaining 93.2 % mentions are marked as history (e.g. `docs/thesis/README.md` lines 45, 70, 120). **AUTHOR:** approve the edited chapter text, as `HANDBACK_2026-10-04.md` §4 item 7 requires for chapter text. |
| D-32 | Push tags v0.7.0/v0.8.0; SUMO go-ahead; Sepolia secrets; SC-05/SC-06; notebook index | **Partly decided.** The SUMO go-ahead was taken as "no install" (`PLAN_2026-10-09.md` Q2; `AFTER_ACTION_REPORT_09.md` §0). **AUTHOR:** pushing the tags (local only, see D-17), Sepolia secrets, SC-05 and SC-06 (both "Decision pending" in `SCOPE_CHANGES.md`), and the notebook index. |

---

## Section V — Verify the plan's reading of the repository

Mark each **confirmed**, **wrong** (say what), or **unsure**.

| ID | Statement in the plan | Answer |
|---|---|---|
| V-01 | The 18-op catalogue (C1…V6) is the right level for "basic identity functions" of the chain options, and B3 (K1–K12) / B4 (M1–M8) are the right extensions for the credential layer and the V2V path | **Not checkable from files (author judgment).** Trunk context: `docs/testing/README.md` §2 row 6 keeps C1…V6 for the harness and TC tags and the 14 families for the manifests. `build_register.py` adds V7 add-claim for the L1 `claim` mechanism. |
| V-02 | The subject list in plan §3.1 (23 SUTs incl. sub-IDs) is complete; nothing on paper names another implementation option | **Checked in part; the notebooks are not checkable.** The repository names one option the list lacks: the onboarding lineage's track III, LSP0, which the trunk replaced with LSP8 and calls a "loose mapping" (`docs/prior-survey/README.md` lines 69 and 86). The TSR ids map onto the 13 sandbox slugs (`RECON_TSR.md` §4 #5), and `erc-1056-vehicle` corresponds to TSR's `cv2x-erc1056`. |
| V-03 | The property classes F/N/A/W/G/L/S/D/I/Q cover every kind of test you intend; nothing is missing (e.g. usability, energy, privacy metrics) | **Not checkable from files (author intent).** Trunk note: `docs/testing/test_register.yaml` tags the security-harness cells with class **S** (`TC-<slug>-<attack>-S`, 54 rows). TSR §3.3 uses S for Scale and A for Adversarial. |
| V-04 | The evidence ladder E0–E7 matches how you want to grade cells for the thesis (chapter cites at E5+) | **Not checkable from files (author preference).** Trunk note: the generated register assigns E3 to every L1 row (`test_register.yaml`). |
| V-05 | Run of record ≠ HEAD (contracts tree `6c58b31` vs `04c33c2`) should be fixed by re-running on HEAD in Phase 0, not by declaring the MOBI-only commits irrelevant | **Confirmed, and done.** The re-run approach is the trunk's rule (`PLAN_MERGE_LINEAGES.md` §0; `STYLE_AND_RIGOUR_GUIDE.md` §1.1 items 4–6). P0.3 (`f976e57`) produced run `2026-10-09T02-09-36Z_7a9a996` with `dirty: false` and `dirtyMeasured: false`. All four `meta.measured` hashes equal `git rev-parse HEAD:1_blockchain-identity/{benchmarks,contracts,hardhat.config.js,package-lock.json}` at `5a83bc2`, with contracts tree `2e70d1f`. The dirty post-merge run of 2026-10-06 was discarded (`AFTER_ACTION_REPORT_07.md` §2). |
| V-06 | The 14 non-deterministic gas cells are a real reporting issue (tables show the mode), not a known-and-accepted property | **Fact checked; the framing is the author's.** The new run of record still has exactly 14 cells with `gasDeterministic: false`: cvin C1/C2/V3/V5; erc721 C1/U1; erc735 C2/U3/D2/V3/V5; lsp8 C1/U1/D2 (`1_blockchain-identity/results/metrics/latest/crud.json`). `MEASUREMENT_CONDITIONS.md` §5.B (revised row) discloses that the mode is reported, with causes and ranges. So the property is documented, but the tables still show only the mode. |
| V-07 | `test_use_cases.py` running on the centralised backend and passing on "no exception" is a gap, not the intended baseline role | **Fact confirmed; whether it is a gap is the author's call.** Every use case builds a `CentralizedVehicleRegistry` (`cv2x-testbed/scripts/test_use_cases.py`). The pytest wrapper says "Success == returns normally" (`sandbox/py-suites/L4-exemplar-interactions/test_lifecycle_use_cases.py`). The file has 9 `raise RuntimeError` checks, all in use cases 3, 6, 10, 11 and 12 (the inventory said 8), so use cases 1, 2, 4, 5, 7, 8 and 9 have none. New since `fa6188e`: the 12 cases run in CI through `sandbox/py-suites/run.sh`. |
| V-08 | `test_mobi_vid.py`'s hardcoded "100 % compliance" and `vc_verifier.COMPLIANCE_CHECKLIST` (85.7 %) should be removed or replaced, never cited | **Fact confirmed; the remedy is the author's.** Both are still present and unchanged since `fa6188e`: `cv2x-testbed/scripts/test_mobi_vid.py:379` prints "Overall Compliance: 100%", and `2_w3c-ssi-layer/verifiable-credentials/vc_verifier.py:947–968` computes the checklist score. The 85.7 % is cited once, labelled "Self-scored", in `2_w3c-ssi-layer/verifiable-credentials/README.md:16`. |
| V-09 | Stale artefacts (`w3c_compliance.json` July, `sensitivity.*` July/paris, `results_snapshot.json` 708302a) should be quarantined to `results/superseded/`, not deleted | **Checked; the plan's reading is partly out of date.** `4_comparison-framework/results/w3c_compliance.json` was regenerated on 2026-10-04 (`d06d004`: 44 checks, 41/1/2, 94.3 %), so it is no longer July, though it carries no commit or dirty stamp (`docs/testing/STAMP_INVENTORY.md`). `sensitivity.{json,csv,tex}` are still from July (`1a902da`, `evmTarget: paris`), and no generator for them was found. `docs/figures/results_snapshot.json` is now commit `cac1729` (2026-10-03), not `708302a`, and still pre-merge. The generated `docs/figures/dashboard_snapshot.json` (P1.1) now exists alongside it. No `superseded/` directory exists anywhere. |
| V-10 | The security `after()` hook writing into `4_comparison-framework/` is a side effect to remove, not a feature | **Fact confirmed; the framing is the author's.** `1_blockchain-identity/test/L2-identity-system/security/securityScenarios.test.js:1445` calls `writeMatrix`, which writes `4_comparison-framework/security-analysis/results/attack_results.json` (`attackHarness.js:272–293`). That file is now also an input of record: register #28's merge note cites it, and `docs/testing/build_register.py` reads it. |
| V-11 | Both external-suite denominators (336/441 and 335/336) must be reported with the matched-pair table | **Confirmed, and already done.** `docs/conformance/W3C_DID_TEST_SUITE.md` reports 336/441 (lines 39, 731), 335/336 (lines 508, 989) and the test-by-test matched comparison (line 818). Register #24 says "never quote 335/336 against 336/441 as a percentage gain". |
| V-12 | `sumo/README.md`, `mobi-vid/README.md`, `3_cv2x-testbed/README.md`, `security-analysis/README.md`, `INDEX.md` stale counts are to be regenerated, not hand-edited | **Checked; the rule was adopted, and these files are outside the checker.** The trunk rule is that READMEs cite `GRAND_REPORT.md` and do not type totals (`docs/testing/README.md` §2 last row). `5a83bc2` applied it in 12 documents. `docs/testing/stale_numbers.yaml` does not scope any file V-12 names. Still stale at `5a83bc2`: `3_cv2x-testbed/README.md` (July: "12/12 passing", "28 tests", "21 tests") and `docs/INDEX.md:18` ("#1–#31"). `.github/workflows/test-contracts.yml:5` still says "47 tests pass". |
| V-13 | Phase ordering (0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8) and the 10–14 agent-session estimate are acceptable | **Not checkable from files (author acceptance).** Trunk context: `PLAN_2026-10-09.md` §3 runs TSR phases 1–3 as P3.1 after P0–P1. Phase 0's re-run was done by the merge (`PLAN_MERGE_LINEAGES.md` S5) and P0.3. |
| V-14 | The "three-click rule" for an examiner (README → matrix → test/result/register) is the right usability target | **Not checkable from files (author preference); adopted on the trunk** (`docs/testing/README.md` §1, "Three clicks to any test"). |
| V-15 | The TEST-repo onboarding stream (`TEST_ONBOARDING.md`: IMinimalSSI F1–F12, gates G0–G6, 12-test regime) should be mapped into the same matrix as a 24th SUT / extra function group in Phase 2, or stays a separate stream | **Not checkable from files (author or architect ruling).** Trunk state: the lineage was imported as documents only, as provenance (`PLAN_2026-10-09.md` Q4, taken in `AFTER_ACTION_REPORT_09.md` §0). `docs/prior-survey/README.md` line 107 says "Nothing in this directory is maintained". `TEST_ONBOARDING.md` line 9 records the mapping as "architect ruling pending". |

---

## Section P — Paper-notes intake (one row per item; add rows freely)

*Not pre-filled: the paper material is the author's (S13), and no notebook content is in the repository (TSR §1.1).*

Fill what you can; a photo/page reference is enough for the worker to follow up. Kinds: `function` · `test-idea` · `result-table` · `figure` · `hypothesis` · `threat` · `scope-note` · `definition` · `other`.

| ID | Kind | SUT(s) | Function(s) | Class | One-line content / page ref | Already in repo? (leave blank if unsure) |
|---|---|---|---|---|---|---|
| P-01 | | | | | | |
| P-02 | | | | | | |
| P-03 | | | | | | |
| P-04 | | | | | | |
| P-05 | | | | | | |
| P-06 | | | | | | |
| P-07 | | | | | | |
| P-08 | | | | | | |
| P-09 | | | | | | |
| P-10 | | | | | | |
| P-11 | | | | | | |
| P-12 | | | | | | |
| P-13 | | | | | | |
| P-14 | | | | | | |
| P-15 | | | | | | |
| P-16 | | | | | | |
| P-17 | | | | | | |
| P-18 | | | | | | |
| P-19 | | | | | | |
| P-20 | | | | | | |

Prompts to jog the notebooks (tick if there is material; the worker will ask for it):
- [ ] a per-standard function list that differs from C1…V6 (e.g. "add claim", "recover", "batch create", "pseudonym rotation")
- [ ] the "basic identity functions" list from the sandbox guide / IMinimalSSI F1–F12
- [ ] hand-drawn comparison tables (gas, latency, security, compliance) with columns the repo does not produce
- [ ] figures sketched for chapter 5/6 (Pareto plot axes, CDFs, timelines)
- [ ] attack ideas not in the six-attack grid (e.g. front-running, griefing, DoS on event walk, time-of-check/time-of-use on freshness)
- [ ] threats to validity you have written down
- [ ] scope decisions made on paper but not in `SCOPE_CHANGES.md`
- [ ] budgets/targets (ms, gas, bytes) you want asserted as executable falsifiers
- [ ] examiner questions you anticipate (each becomes a row the matrix must answer)

---

## Section C — Cell triage (Function × SUT, classes F/N/A; the G/L cells are complete per plan App. C)

Mark only cells you want changed from the plan's proposal. Row = op, column = SUT. The plan proposes **G** for every cell listed in §7.1 and **T** where the inventory shows an asserting test. Write `C-<sut>-<op> <T|N|G|P|X> "<reason>"`.

Proposed `G` cells to confirm or override. The "Trunk state" column is the pre-fill. "Your answer" is the author's.

| Cell | Plan proposal | Trunk state at `5a83bc2` (pre-fill) | Your answer |
|---|---|---|---|
| C-erc725xy-{all 6 attacks} (class A) | G | Still absent: 0 matches for `725xy` in `test/L2-identity-system/security/securityScenarios.test.js`, and its `after()` contract list has nine standards | |
| C-mobi-v2-{C1…V6} (harness) | G | No harness adapter (D-06). The sandbox L1 covers `mobi-vid` through its own adapter, so `TC-mobi-vid-*` rows appear in `test_register.yaml` | |
| C-{all}-U6 recover (new op) | G, cond. | No U6 op. ERC-4337 recovery is exercised by `sandbox/options/erc-4337/demos/keys-delegates.js` (`RECON_TSR.md` §3). D15 is open | |
| C-erc4337-{R4,U2,D1} | re-map to N (guardian ≠ delegate) | Not re-mapped (`erc4337.adapter.js:79,104`) | |
| C-{all}-{declared n/a} `NotSupported` assertion | G | Built in the sandbox L1 as a manifest-checked `NotApplicable` (27 `L1:F:n/a` rows in `test_register.yaml`). The harness conformance test still uses `this.skip()` at 5 call sites (`test/benchmarks/adapters.conformance.test.js`) | |
| C-erc721-{N class, legacy files} | G | Unchanged: 0 revert assertions in `regularExtended.js` and `identityBased.js` | |
| C-CVINVehicleNFT / CVIN_DID_ERC725 / MOBI-ERC1056Registry unit files | G | Partly closed: `per-option/ERC1056/ERC1056Registry.regression.test.js` exists. `CVINVehicleNFT` appears only in `per-option/ERC721/vinNormalisation.regression.test.js`. No L2 file for `CVIN_DID_ERC725`. Demos exercise both (`RECON_TSR.md` §3) | |
| C-use-cases-{1,2,4,5,7,8,9} oracles | G | Unchanged (V-07) | |
| C-vc-layer-K4 on chain-resolved keys per substrate (M1-H/HTTP) | G | Not checked in this pre-fill | |
| C-did-resolver/ethr-K8 chain read; did:mobi | G (or X with SC) | did:ethr chain read not built: `did_resolver.py:278–287` stores `blockchain_provider` and nothing else uses it. did:mobi not checked | |
| C-{all}-Q rubric scoring | G | 3 of 9 substrates scored (erc1056, erc721, erc725), 0 `reviewed: true` (`1_blockchain-identity/benchmarks/rubric/did-method-rubric.json`) | |
| C-{all}-{G,L} at M2 (Sepolia) | X pending go-ahead | No Sepolia run; `sepolia_validation.json` is absent (O-20) | |
| C-v2v-path with real SUMO mobility | X pending go-ahead | Gated by Q2 "no install" (`AFTER_ACTION_REPORT_09.md` §0); P2a design only (`docs/PLAN_SUMO_VISUALISATION.md`) | |

Free cells (add any): 

| Cell | Value | Reason |
|---|---|---|
| | | |
| | | |

---

## Section Q — Per-phase review questions

Answer briefly or leave for the default. *Pre-fill notes (trunk facts, not answers) are in italics.*

**Phase 0**
- Q-0.1 Is a full re-run of every producer acceptable in Phase 0 (≈ 1 h compute), or only the harness and the suites?
  *Pre-fill: the merge already re-ran every result of record on the merged contracts (`PLAN_MERGE_LINEAGES.md` S5; `PLAN_2026-10-09.md` §0). The harness run of record followed in P0.3 (`f976e57`). AUTHOR.*
- Q-0.2 Any artefact that must **not** be quarantined even if stale?
  *Pre-fill: AUTHOR.*

**Phase 1**
- Q-1.1 Should the register be YAML (human-diffable) with CSV export, or CSV-first?
  *Pre-fill: the trunk register is YAML (`docs/testing/test_register.yaml`, `aef16af`), with no CSV export. AUTHOR on the export.*
- Q-1.2 Should one test be allowed several rows (covers several functions) or must tests be split?
  *Pre-fill: the builder gives an L1 cell separate F and G rows (`TC-…-F`, `TC-…-G`). AUTHOR.*

**Phase 2**
- Q-2.1 How do you want to hand over paper material: photos in `docs/planning/testing_suite/paper/` (committed), a private folder, or transcribed in this sheet only?
  *Pre-fill: AUTHOR.*
- Q-2.2 Who signs off the matrix v1: you alone, or with a committee member?
  *Pre-fill: AUTHOR.*

**Phase 3**
- Q-3.1 Any test file that must not be touched even for a title tag (e.g. byte-faithful upstream tests)?
  *Pre-fill: so far no test title has been touched (`aef16af`). The K-12 byte-faithfulness question is D-25. AUTHOR.*
- Q-3.2 Keep the three CI workflows and add a fourth, or consolidate into one with jobs?
  *Pre-fill: there are still three workflows. The register, dashboard and crux checks were added as steps in `test-contracts.yml` (lines 57–65), not as a fourth workflow. AUTHOR.*
- Q-3.3 Pin Python deps with hashes (strict) or versions only?
  *Pre-fill: AUTHOR. The deps are still unpinned (O-12).*

**Phase 4**
- Q-4.1 Priority order among the six packets P4-1…P4-6 (default: 2, 3, 1, 4, 6, 5)?
  *Pre-fill: AUTHOR.*
- Q-4.2 For the non-deterministic cells, is changing fixtures (fixed-length signatures) acceptable, given it changes the measured gas of record for those cells?
  *Pre-fill: AUTHOR. A changed result must be re-executed and its old value kept as S or in a delta file (`STYLE_AND_RIGOUR_GUIDE.md` §1.1 item 4).*

**Phase 5**
- Q-5.1 `make` or a shell/Python entry point (`tools/testing/run_all.sh`)? Windows is not a target?
  *Pre-fill: decided at the merge: `tools/testing/` ≡ `sandbox/grand/`, so the entry point is `python3 sandbox/grand/run.py` (`docs/testing/README.md` §1 and §2 row 2). It has no tiers yet. Windows: nothing on file. AUTHOR.*
- Q-5.2 Keep both gas pipelines (`benchmark_gas.js` and the harness) with a reconciliation test, or retire `benchmark_gas.js` after the harness covers MOBI?
  *Pre-fill: AUTHOR. Both are still producers of record (#25 and #34).*

**Phase 6**
- Q-6.1 Which hypotheses need numeric thresholds pre-registered v2 before any new measurement (default: all of H1, H1′, H3, H4, H5, PKI)?
  *Pre-fill: AUTHOR. `docs/design/INFRASTRUCTURE_MESSAGING.md` is the P4.3 note with pre-registered I1–I5 for infrastructure messaging (`3a2a806`), which is outside H1–H5.*
- Q-6.2 Rubric scoring: self-scored with evidence cells, or do you want a second scorer (committee member / collaborator) for `reviewed:true`?
  *Pre-fill: AUTHOR. The three scored substrates carry `"assessor": "NP"` and `reviewed: false`.*

**Phase 7**
- Q-7.1 Should chapter text be edited by the session (with your framing approval per item) or only diffed and left to you?
  *Pre-fill: `5a83bc2` edited chapter figures to register values (D-31). The approval of that text is open. AUTHOR.*
- Q-7.2 Keep `docs/review03/` naming to match review 02?
  *Pre-fill: review-2 documents live under `docs/review02/` (M-I). `PLAN_2026-10-09.md` Q7 reserves the adversarial review for a later session under a different assistant configuration. AUTHOR.*

---

## Section R — Priorities (rank 1 = first)

*Not pre-filled: the ranks are the author's. For reference, `PLAN_2026-10-09.md` §3 already fixes the order of this pass: P0 → P1.1–P1.2 → P4.1 → P1.3–P1.4 → P3.1–P3.6 → P2a → P4.3.*

| Item | Rank |
|---|---|
| Coverage matrix exists and is generated (Phases 1, 3) | |
| Gap cells filled for the nine chain standards (Phase 4: P4-1, P4-2, P4-3) | |
| Results pipeline with one entry point and stamping (Phase 5) | |
| Statistics and charters (Phase 6) | |
| Docs reconciliation and stale numbers (Phase 7) | |
| Use cases on a chain backend with oracles (P4-4) | |
| Resolver chain read (P4-5) | |
| External validation (Phase 8) | |
| Paper intake (Phase 2) | |

---

## Section O — Open questions from the three surveys to triage (Accept = do it in the plan's phase · Defer = note, later · Reject = not a problem, say why)

*Pre-fill: each row says whether the finding still holds on the trunk at `5a83bc2`, with evidence. The Accept / Defer / Reject triage is the author's in every row (AUTHOR).*

| ID | Finding (source) | Accept / Defer / Reject |
|---|---|---|
| O-01 | ERC-4337 adapter maps guardian to delegate (I.6 #4) | **Holds.** `benchmarks/adapters/erc4337.adapter.js:79` (`verifyDelegate` compares with `guardian()`) and `:104` (`addDelegate`, "guardian has no expiry"). The file is unchanged since `fa6188e`. Triage: AUTHOR. |
| O-02 | Conformance test not an equivalence test (I.6 #3) | **Holds.** `1_blockchain-identity/test/benchmarks/adapters.conformance.test.js` is unchanged since `fa6188e`. It still `this.skip()`s declared n/a ops (5 call sites) and tests U1/U4 in one case (line 130). Triage: AUTHOR. |
| O-03 | 14 non-deterministic cells hidden by mode (I.6 #1) | **Holds** in the new run of record `2026-10-09T02-09-36Z_7a9a996`: the same 14 cells (V-06). Triage: AUTHOR. |
| O-04 | Stats implemented, not used (I.6 #2) | **Holds.** `bootstrapMedianCI` and `mannWhitneyU` are referenced only in `benchmarks/lib/stats.js` and `test/benchmarks/stats.test.js`, with no caller in `benchmarks/scenarios/` or `analysis/`. Triage: AUTHOR. |
| O-05 | Security `after()` side effect (I.6 #10) | **Holds** (V-10). Triage: AUTHOR. |
| O-06 | ERC-725xy absent from security matrix (I.6 #5) | **Holds.** 0 matches for `725xy` in the security harness. Register #28 still reads 43/43 defended, 11 N/A, over nine standards. Triage: AUTHOR. |
| O-07 | Use-case suite oracles and backend (II.8 #1) | **Holds** for oracles and backend (V-07). One part has improved since `fa6188e`: the suite now runs in CI. Triage: AUTHOR. |
| O-08 | Hardcoded compliance prints (II.8 #2) | **Holds** (V-08). Triage: AUTHOR. |
| O-09 | Unseeded randomness in stack/scenarios/use cases (II.8 #6) | **Holds for the stack.** `cv2x-testbed/protocols/cv2x_stack.py` imports `random` (line 10) and calls `random.choice` and `random.randint` (lines 183, 238–239) with no seed. The file is unchanged since `fa6188e`. `test_use_cases.py` contains no `random`, so that part was not confirmed. The scenarios were not checked. Triage: AUTHOR. |
| O-10 | Checker writes to CWD; committed copy stale (II.8 #4/#5) | **Partly resolved.** The CWD write holds: `cv2x-testbed/scripts/w3c_compliance_checker.py:992,1020` defaults to a relative `w3c_compliance_report.json`, and `.gitignore:6` ignores that name. The committed copy is no longer stale: `4_comparison-framework/results/w3c_compliance.json` was regenerated on 2026-10-04 and reads 94.3 % over 44 checks. It still has no commit stamp (`STAMP_INVENTORY.md`). Triage: AUTHOR. |
| O-11 | External-suite offline synthesis caveat (II.8 #9) | **Holds.** The resolver does not read the chain: `blockchain_provider` is stored (`2_w3c-ssi-layer/did-resolution/did_resolver.py:278–287`) and used nowhere else. The 335/336 results measure synthesised documents. Triage: AUTHOR. |
| O-12 | `requirements.txt` broken; deps unpinned (II.8 #8) | **Holds.** `2_w3c-ssi-layer/requirements.txt` is unchanged since `fa6188e` (`web3==6.11.0` line 4, `did-jwt==0.1.0` line 13). The CI `python-layers` job installs unpinned packages (`RECON_TSR.md` §5.1 item 12). Triage: AUTHOR. |
| O-13 | Run of record ≠ HEAD (III.8 #1) | **Resolved** by P0.3 (`f976e57`); see V-05. Triage: AUTHOR (Reject as resolved, or close). |
| O-14 | No regeneration path; stale snapshots (III.8 #2) | **Partly resolved.** Tests have one entry point (`sandbox/grand/run.py all`). The dashboard snapshot is generated and CI-checked (`docs/figures/make_dashboard_data.py --check`, `test-contracts.yml` lines 57–65). There is still no single command that regenerates the results of record. `results_snapshot.json` (`cac1729`) and `sensitivity.*` (July) are still in place (V-09). Triage: AUTHOR. |
| O-15 | Three gas instruments, no mixing check (III.8 #4) | **Holds.** The rule exists only in prose: M1-H numbers "never share a table with M1 numbers from other scripts" (`MEASUREMENT_CONDITIONS.md` §5). No file found enforces it. Triage: AUTHOR. |
| O-16 | H5 criteria drift from pre-registration (III.8 #6) | **Holds.** `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` line 298 pre-registers four criteria for H5. The A3 analysis (line 278) and register #36 use six. `SCOPE_CHANGES.md` has no entry for the change. Triage: AUTHOR. |
| O-17 | Claims surface drift across ~10 docs (III.8 #8) | **Partly resolved.** `5a83bc2` fixed 82 figures in 12 documents, and `docs/testing/check_docs_numbers.py` exits clean over its scope (`stale_numbers.yaml`: README, CAPABILITIES, COMPOSITION, SIDE_PAPERS, QUICKSTART, INVENTORY, `docs/thesis/**`). Outside that scope the drift remains (V-12). Triage: AUTHOR. |
| O-18 | Rubric unscored; CI target < floor; harness job no gate (III.8 #9) | **Holds** in all three parts. The rubric has 3 of 9 substrates scored and 0 reviewed (C-{all}-Q). `w3c-compliance.yml` has `COMPLIANCE_FLOOR: '94.0'` and `COMPLIANCE_TARGET: '90.0'` (lines 124–125), so the target is below the floor. The `benchmark.yml` harness job runs `npm run metrics` and uploads the result with no diff gate, and the file is unchanged since `fa6188e`. Triage: AUTHOR. |
| O-19 | M-number collision; register numbering (III.8 #9) | **Holds.** The M-work items are not renamed (D-12). The register's ordinal collision was settled by M-H (#40–#43 appended), but the table order is still non-monotonic (#1–#4, #25–#28, #24, #5–#22, #29–#43, #23 in `MEASUREMENT_CONDITIONS.md` §3). `claims.yaml` is not built (D-11). Triage: AUTHOR. |
| O-20 | Dangling references (`sepolia_validation.json`, `docs/conformance/internal/…`) (III.8 #9) | **Partly resolved.** `sepolia_validation.json` is still referenced (`SOURCES.md:85`, `CAPABILITIES.md:347`, `docs/thesis/chapter3-methodology/README.md:217`) and exists nowhere in the tree. `docs/conformance/internal/…` is no longer referenced outside the TSR planning documents. A local copy of it exists but is git-ignored. Triage: AUTHOR. |

---

## Section S — Standing rules to confirm (plan §0.1)

*Pre-fill: the rows note the trunk state; keeping or changing each rule is the author's (AUTHOR).*

| Rule | Keep / change |
|---|---|
| S10 untagged test fails the register build | AUTHOR. No untagged gate exists: the builder derives ids from records and no title is tagged (D-02). `build_register.py --check` fails only on a stale register. |
| S11 result without stamp is not of record | AUTHOR. Partly applied: `STAMP_INVENTORY.md` reports 11 of 25 results fully stamped, and P3.3 is in progress (`230ac1a`). |
| S12 five-value cells (or six with `W`, D-03) | AUTHOR. Conflict on the trunk: `coverage_matrix.md` uses T/X/G/N(+M) with X = "demo failing" (D-03). The register's class S for security clashes with TSR's S = Scale (V-03). |
| S13 paper copy never the only copy | AUTHOR. Nothing on file. |

---

## Section L — Sheet change log

| Version | Date | By | Change |
|---|---|---|---|
| 1.0 | 2026-10-04 | session | blank sheet issued with TSR Plan v1.0 |
| 1.1 | 2026-10-09 | session (plan P3.6) | pre-filled from the merged trunk at `5a83bc2`: D-rows record the decision taken on the trunk with its source, or AUTHOR with the sheet's default; V-rows say checked/not checkable with evidence; O-rows say holds/partly resolved/resolved; trunk notes added to C, Q, S; P and R left to the author |
