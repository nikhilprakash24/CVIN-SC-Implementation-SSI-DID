# Testing Suite & Results Plan — Second-Pass Sheet

**Companion to:** `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` (TSR Plan v1.0)
**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-04 · **Sheet version:** 1.0 (blank)
**Purpose:** the author's second pass over the plan, done from chat. Every item has an ID; answer by ID in any order ("D-03: option b", "P-07: see photo 12", "C-erc735-U2: N, no key management"). Items left blank take the stated default. The filled sheet is the input to Phase 2 and is kept under version control, so the paper notes end up redundant with the repository (S13).

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
| D-01 | Where the organised suite lives | a) `docs/testing/` + `tools/testing/` (additive; nothing moves) · b) new top-level `5_testing-suite/` to match `1_…4_` · c) inside `4_comparison-framework/` | **a** | |
| D-02 | Tagging mechanism | a) tag in test titles/markers, registers generated · b) hand-maintained register only · c) both, with CI cross-check | **a** | |
| D-03 | Matrix cell vocabulary | a) `T/N/G/P/X` as proposed · b) add `W` (weak: test exists but assertion is loose) as a sixth value · c) other | **b** is recommended if ERC-721 legacy tests stay | |
| D-04 | Tiers | a) smoke / full / measure · b) full / measure only · c) add `external` for Sepolia/SUMO/W3C suite | **c** | |
| D-05 | Recovery as a catalogue op (`U6_recover_controller`) and re-mapping ERC-4337 R4/U2/D1 to n/a | a) yes, accept the 4337 core-ops count change · b) keep the guardian-as-delegate mapping with a note · c) defer | **a** | |
| D-06 | MOBI VID adapter in the harness | a) add `mobi.adapter.js` (declared n/a where VID II lacks a primitive) · b) keep MOBI as application profile only (sweep + benchmark_gas) | **a** | |
| D-07 | Non-deterministic gas cells (14) | a) fix fixtures so every cell is exact · b) report `mode [min,max]` with cause · c) both: fix where the cause is the fixture, report where it is the standard | **c** | |
| D-08 | Use-case suite backend | a) keep `central` + add MOBI V2 backend · b) replace with MOBI V2 only · c) run on all five sweep backends | **a** | |
| D-09 | Statistics in latency tables | a) add bootstrap CI + Mann–Whitney/Cliff's δ columns, Holm-corrected · b) CI only · c) leave descriptive with footer | **a** | |
| D-10 | Results producers write to `runs/` and promote explicitly (no script overwrites tracked results) | a) yes, all producers · b) only the ones listed in HANDBACK §6 | **a** | |
| D-11 | Machine-readable claim register (`claims.yaml`) | a) mirror, prose stays canonical · b) make YAML canonical and generate the prose table · c) none | **a** | |
| D-12 | Work-item names M1–M7 (PLAN_MOBI_SUMO) that collide with condition tags | a) rename work items W1–W7 in a note; never touch tags · b) leave; add a glossary line | **a** | |
| D-13 | Reporting standards to cite in charters | a) ACM SIGSOFT Empirical Standards (Benchmarking, Engineering Research) + ACM badging · b) add ISO/IEC/IEEE 29119 test documentation · c) a) only | **a** | |
| D-14 | Replication protocol target | a) second host for every L/S result of record · b) second replicate same host, second host for headline rows only (#27, #32/#37, #21) · c) none beyond today | **b** | |
| D-15 | Phase 8 (Sepolia, real SUMO) | a) schedule after Phase 7 · b) interleave with Phase 5 · c) out of this plan | **a** | |
| D-16 | Commit attribution for this stream | a) author-attributed, no AI trailers (repo standing rule B.1) · b) default tool attribution | **a** (applied to this pass) | |
| D-17 | Version bump on completion | a) 0.9.0 at Phase 7 · b) 0.9.0 only with a Sepolia witness (per handback) · c) 0.8.x | **b** | |

Pending author decisions already on file (answer here or in `HANDBACK_2026-10-04.md` §4; the plan does not depend on them but Phase 7's docs reconciliation does):

| ID | Decision (handback ref) | Answer |
|---|---|---|
| D-20 | H1 wording (Q-3): "~10× create (bare 10.3×, VIN-bound 6.9×); lifetime 2.6×/3.0×" vs restated hypothesis | |
| D-21 | Checker strictness T-7/T-8 and the 7.1.2 correction (#4; 94.3 % vs 92.0 %, CI floor) | |
| D-22 | K-4 residual (manufacturer can birth an unused did:ethr) | |
| D-23 | attestEvent duplicates / restrict to current owner and delegates (moves #28) | |
| D-24 | K-5 (cv2x `ERC1056Registry` vs `EthereumDIDRegistry`): rebuild or keep caveat | |
| D-25 | K-12 keep `EthereumDIDRegistry` byte-faithful | |
| D-26 | MOBI claim wording ("MOBI-VID-inspired profile") and SC-14–SC-20 | |
| D-27 | H3 design point: k, host, f to defend (#32/#37/#39) | |
| D-28 | M4 verdict wording (#33) | |
| D-29 | Privacy framing (#38): per-pseudonym identities + relayer? | |
| D-30 | H5 wording given #36 (hybrid dominated by ERC-4337 on all six criteria) and the criteria change from pre-registration | |
| D-31 | Chapter stale-figure list (handback §4.7/§4.12): approve the replacement values | |
| D-32 | Push tags v0.7.0/v0.8.0; SUMO go-ahead; Sepolia secrets; SC-05/SC-06; notebook index | |

---

## Section V — Verify the plan's reading of the repository

Mark each **confirmed**, **wrong** (say what), or **unsure**.

| ID | Statement in the plan | Answer |
|---|---|---|
| V-01 | The 18-op catalogue (C1…V6) is the right level for "basic identity functions" of the chain options, and B3 (K1–K12) / B4 (M1–M8) are the right extensions for the credential layer and the V2V path | |
| V-02 | The subject list in plan §3.1 (23 SUTs incl. sub-IDs) is complete; nothing on paper names another implementation option | |
| V-03 | The property classes F/N/A/W/G/L/S/D/I/Q cover every kind of test you intend; nothing is missing (e.g. usability, energy, privacy metrics) | |
| V-04 | The evidence ladder E0–E7 matches how you want to grade cells for the thesis (chapter cites at E5+) | |
| V-05 | Run of record ≠ HEAD (contracts tree `6c58b31` vs `04c33c2`) should be fixed by re-running on HEAD in Phase 0, not by declaring the MOBI-only commits irrelevant | |
| V-06 | The 14 non-deterministic gas cells are a real reporting issue (tables show the mode), not a known-and-accepted property | |
| V-07 | `test_use_cases.py` running on the centralised backend and passing on "no exception" is a gap, not the intended baseline role | |
| V-08 | `test_mobi_vid.py`'s hardcoded "100 % compliance" and `vc_verifier.COMPLIANCE_CHECKLIST` (85.7 %) should be removed or replaced, never cited | |
| V-09 | Stale artefacts (`w3c_compliance.json` July, `sensitivity.*` July/paris, `results_snapshot.json` 708302a) should be quarantined to `results/superseded/`, not deleted | |
| V-10 | The security `after()` hook writing into `4_comparison-framework/` is a side effect to remove, not a feature | |
| V-11 | Both external-suite denominators (336/441 and 335/336) must be reported with the matched-pair table | |
| V-12 | `sumo/README.md`, `mobi-vid/README.md`, `3_cv2x-testbed/README.md`, `security-analysis/README.md`, `INDEX.md` stale counts are to be regenerated, not hand-edited | |
| V-13 | Phase ordering (0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8) and the 10–14 agent-session estimate are acceptable | |
| V-14 | The "three-click rule" for an examiner (README → matrix → test/result/register) is the right usability target | |
| V-15 | The TEST-repo onboarding stream (`TEST_ONBOARDING.md`: IMinimalSSI F1–F12, gates G0–G6, 12-test regime) should be mapped into the same matrix as a 24th SUT / extra function group in Phase 2, or stays a separate stream | |

---

## Section P — Paper-notes intake (one row per item; add rows freely)

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

Proposed `G` cells to confirm or override:

| Cell | Plan proposal | Your answer |
|---|---|---|
| C-erc725xy-{all 6 attacks} (class A) | G | |
| C-mobi-v2-{C1…V6} (harness) | G | |
| C-{all}-U6 recover (new op) | G, cond. | |
| C-erc4337-{R4,U2,D1} | re-map to N (guardian ≠ delegate) | |
| C-{all}-{declared n/a} `NotSupported` assertion | G | |
| C-erc721-{N class, legacy files} | G | |
| C-CVINVehicleNFT / CVIN_DID_ERC725 / MOBI-ERC1056Registry unit files | G | |
| C-use-cases-{1,2,4,5,7,8,9} oracles | G | |
| C-vc-layer-K4 on chain-resolved keys per substrate (M1-H/HTTP) | G | |
| C-did-resolver/ethr-K8 chain read; did:mobi | G (or X with SC) | |
| C-{all}-Q rubric scoring | G | |
| C-{all}-{G,L} at M2 (Sepolia) | X pending go-ahead | |
| C-v2v-path with real SUMO mobility | X pending go-ahead | |

Free cells (add any): 

| Cell | Value | Reason |
|---|---|---|
| | | |
| | | |

---

## Section Q — Per-phase review questions

Answer briefly or leave for the default.

**Phase 0**
- Q-0.1 Is a full re-run of every producer acceptable in Phase 0 (≈ 1 h compute), or only the harness and the suites?
- Q-0.2 Any artefact that must **not** be quarantined even if stale?

**Phase 1**
- Q-1.1 Should the register be YAML (human-diffable) with CSV export, or CSV-first?
- Q-1.2 Should one test be allowed several rows (covers several functions) or must tests be split?

**Phase 2**
- Q-2.1 How do you want to hand over paper material: photos in `docs/planning/testing_suite/paper/` (committed), a private folder, or transcribed in this sheet only?
- Q-2.2 Who signs off the matrix v1: you alone, or with a committee member?

**Phase 3**
- Q-3.1 Any test file that must not be touched even for a title tag (e.g. byte-faithful upstream tests)?
- Q-3.2 Keep the three CI workflows and add a fourth, or consolidate into one with jobs?
- Q-3.3 Pin Python deps with hashes (strict) or versions only?

**Phase 4**
- Q-4.1 Priority order among the six packets P4-1…P4-6 (default: 2, 3, 1, 4, 6, 5)?
- Q-4.2 For the non-deterministic cells, is changing fixtures (fixed-length signatures) acceptable, given it changes the measured gas of record for those cells?

**Phase 5**
- Q-5.1 `make` or a shell/Python entry point (`tools/testing/run_all.sh`)? Windows is not a target?
- Q-5.2 Keep both gas pipelines (`benchmark_gas.js` and the harness) with a reconciliation test, or retire `benchmark_gas.js` after the harness covers MOBI?

**Phase 6**
- Q-6.1 Which hypotheses need numeric thresholds pre-registered v2 before any new measurement (default: all of H1, H1′, H3, H4, H5, PKI)?
- Q-6.2 Rubric scoring: self-scored with evidence cells, or do you want a second scorer (committee member / collaborator) for `reviewed:true`?

**Phase 7**
- Q-7.1 Should chapter text be edited by the session (with your framing approval per item) or only diffed and left to you?
- Q-7.2 Keep `docs/review03/` naming to match review 02?

---

## Section R — Priorities (rank 1 = first)

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

| ID | Finding (source) | Accept / Defer / Reject |
|---|---|---|
| O-01 | ERC-4337 adapter maps guardian to delegate (I.6 #4) | |
| O-02 | Conformance test not an equivalence test (I.6 #3) | |
| O-03 | 14 non-deterministic cells hidden by mode (I.6 #1) | |
| O-04 | Stats implemented, not used (I.6 #2) | |
| O-05 | Security `after()` side effect (I.6 #10) | |
| O-06 | ERC-725xy absent from security matrix (I.6 #5) | |
| O-07 | Use-case suite oracles and backend (II.8 #1) | |
| O-08 | Hardcoded compliance prints (II.8 #2) | |
| O-09 | Unseeded randomness in stack/scenarios/use cases (II.8 #6) | |
| O-10 | Checker writes to CWD; committed copy stale (II.8 #4/#5) | |
| O-11 | External-suite offline synthesis caveat (II.8 #9) | |
| O-12 | `requirements.txt` broken; deps unpinned (II.8 #8) | |
| O-13 | Run of record ≠ HEAD (III.8 #1) | |
| O-14 | No regeneration path; stale snapshots (III.8 #2) | |
| O-15 | Three gas instruments, no mixing check (III.8 #4) | |
| O-16 | H5 criteria drift from pre-registration (III.8 #6) | |
| O-17 | Claims surface drift across ~10 docs (III.8 #8) | |
| O-18 | Rubric unscored; CI target < floor; harness job no gate (III.8 #9) | |
| O-19 | M-number collision; register numbering (III.8 #9) | |
| O-20 | Dangling references (`sepolia_validation.json`, `docs/conformance/internal/…`) (III.8 #9) | |

---

## Section S — Standing rules to confirm (plan §0.1)

| Rule | Keep / change |
|---|---|
| S10 untagged test fails the register build | |
| S11 result without stamp is not of record | |
| S12 five-value cells (or six with `W`, D-03) | |
| S13 paper copy never the only copy | |

---

## Section L — Sheet change log

| Version | Date | By | Change |
|---|---|---|---|
| 1.0 | 2026-10-04 | session | blank sheet issued with TSR Plan v1.0 |
| | | | |
