# Unblocked Work, 2026-10-23: What Can Be Done Without an Answer From the Author

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-23 (after-action report 26, open).
**Purpose:** everything the orchestrator can do next with no decision from the author and no answer from the check
session, so the author can approve or strike items. Each item says what it produces, why it needs no one, its size in
passes, the risk, and the orchestrator's recommendation. **Nothing on this list starts until the author says which
items to take**, except that the order proposed in §3 is what would run if the answer is "all of it".

Two rules hold throughout: no result of record is re-run before the check session has reported (that is the point of
the check), and one session pushes to the branch at a time (the TDP session is active; the check session has not run).

## 1. Items that need nothing from anyone

| # | Item | Produces | Why it needs no one | Size | Risk | Recommendation |
|---|---|---|---|---|---|---|
| U1 | **WM-2 B3, the latency charter** (class L): every latency row conforms (within-run comparison, host and library record, N ≥ 30) or is relabelled "descriptive only"; generated and CI-checked, as the gas charter is | `docs/testing/LATENCY_CHARTER.md` + generator + CI line; register notes on relabelled rows | reads the register and the result files; changes no measurement | 1 pass | a row may have to be relabelled, which the thesis then must respect; that is the charter's purpose | **take** |
| U2 | **WM-2 A5, `claims.yaml`**: stable ids for every register row; every V row's quoted numbers checked against its result file by script (the WM-1 audit showed an edited row passed every guard) | `docs/testing/claims.yaml` + checker in CI | mechanical; strengthens the guard that A3b and A6 will rely on | 1 to 2 passes | the checker will find rows whose quoted numbers it cannot locate in a file; each is a finding, not a fix | **take, before A3** |
| U3 | **WM-2 A7**: the Python suites (L3, L4, SSI layer, 342 tests) entered in the test register with TC ids | `docs/testing/test_register.yaml` extended; coverage matrix regenerated | generated from the test files | 1 pass | none to results | take |
| U4 | **Mutation scripts for the C1 and C2 tests**, as `mutate_idtx.sh` and the verifier mutation script exist: show that the resolver chain tests and the D54 tests kill mutants of the code they guard | `2_w3c-ssi-layer/did-resolution/mutation/`, `1_blockchain-identity/test/.../mutate_d54.sh`; CI lines | rule 1.3.11, every guard shown to fire; C1 and C2 have regression proofs but no mutant counts | 1 pass | none to results; a surviving mutant is a finding about test strength | **take** |
| U5 | **WM-2 D2**: RSU-to-RSU messaging design note (what it would add to crux C3; whether the thesis needs it) | `docs/design/RSU_TO_RSU_NOTE.md` | a note for the author to decide on; no build | half a pass | none | take |
| U6 | **A read-only audit of chapters 1, 4, 6, 7 against the register**: a findings list of every number, claim and sentence that lacks a V row or contradicts one (the reading half of WM-2 D1, without the editing half, which waits on D-1) | `docs/thesis/CHAPTER_AUDIT_2026-10.md` | reads only; the chapter edits wait for D-1 | 1 pass | none; the list is what D1 then works from | **take** |
| U7 | **A read-only audit of the TDP documents against the register**: TDP-001, 003, 007, 008, 009 are hand-written by the parallel session and only the stale-figure checker has read them; list any claim beyond the evidence | `docs/tdp/REVIEW_2026-10.md`, findings only, for the TDP session to dispose | reads only; no TDP file edited | half a pass | none | take |
| U8 | **I-05's model as code**: a script that computes k_min, the sensitivity and the two predictions from V-row inputs, so the prediction is reproducible before any measurement; no measurement | `docs/phase2/briefs/i05_model.py` with a `--check` that the brief's P1 and P2 reproduce | arithmetic over V rows; Phase 2 principle 4 (no Phase 2 number is a result) kept by labelling | half a pass | none | take |
| U9 | **Pin the CI Python dependencies** (`pip install` lines are unpinned, by the workflows' own header note) to the versions the runs of record used, read from their stamps | workflow files; a note in the handback | reproducibility; no result changes | half a pass | a pinned version may no longer install on the runner; CI tells us | take, low priority |
| U10 | **`check_docs_numbers.py` for small integers**: the result-cards check is weak on small integers (report 18); add exact-phrase patterns for the counts most often quoted (test counts, defect counts, "4 of 26") | checker entries; shown to fire | tooling only | half a pass | none | take, low priority |
| U11 | **Progress report, deeper draft**: per-pass narrative paragraphs under §3, and §5's defect section expanded to every High defect with its finder; the reader and the AI-use statement stay as marked gaps | draft 2 of `docs/PROGRESS_REPORT_2026-07_TO_2026-10.md` | the records exist; only the two gaps need the author | 1 pass | none | take after the check, so the findings go in once |
| U12 | **Session hygiene**: `docs/DEVELOPMENT_HISTORY.md` pointer to the progress report; INDEX rows for the new documents; handback §7's reading order updated to include the decision sheet and the start prompt | small edits | housekeeping | quarter of a pass | none | take with U11 |

## 2. Items that look unblocked but are not, and why
| Item | Why it waits |
|---|---|
| WM-2 A3, A3b, A6 (stamp calls and the re-runs of record) | they turn results into records; the check of passes 16–22 is meant to precede that. A3's stamp-call part alone is code, but its gate is a clean re-run, which is the thing being held |
| WM-2 D1 (editing the chapters) | D-1 (adopt Scope v3) decides what the chapters say; U6 does the reading half now |
| Chapter 2 sections 2.1 to 2.5 | the author's reference set; nothing is cited unread |
| The progress report's final form; sharing any page | N-23 and the reader |
| Phase 2 build steps (E-F1-1, E-F3-3, F2-S3) | P2-D1 and P2-D7; and D-13's default keeps Phase 2 to documents until the defence |
| N-24 (chain-backed W3C suite run) | a new measurement; after the check, with A3b |
| D-10 Sepolia | two secrets from the author |
| Running the check brief's K1–K13 here | it would not be independent; that is the whole reason for the other session |
| A scholarly-database search for "identity-dependent transaction" (the brief's open item) | the research connectors are not reachable from this session today; web search only, which the brief already did |

## 3. Proposed order if the answer is "all of it"
U2 (claims.yaml) → U1 (latency charter) → U4 (mutation scripts) → U3 (A7) → U6 (chapter audit) → U7 (TDP review)
→ U5 (D2 note) → U8 (I-05 model) → U9, U10 → U11, U12 after the check has reported.
Each is its own after-action report, opened and committed first, pushed when the branch is quiet, closed with CI.
U2, U1 and U4 come first because A3b and A6, which follow the check, will lean on them.

## 4. What the author does with this document
Reply with the item ids to take, or "all", or strike-throughs. Anything not named stays untouched.
