# Handoff — Second Codebase Review (save point), 2026-10-03

**For:** the planning chat (and any later session)
**Working branch:** `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt`
**Save-point base:** `441791b` (data-collection lineage tip) — before any review-2 change
**Authoring rule in force:** commits authored by Nikhil Prakash, no AI co-author trailers
(`docs/ORIGINAL_PROMPT_AND_DIRECTION.md` §B.1 on the trunk).

This document is the save point. It records what was found when review 2 started, the
plan the review follows, and how to resume if the session ends. The review report,
remediation plan and pass reports come after it and are listed in §6.

---

## 1. The branch the request referred to

The request was to resume from **`claude/review-codebase-011CUpSkztZkbHszuvbpahcj`**.

**That branch does not exist on any remote the session can reach.** I checked:
- `nikhilprakash24/CVIN-SC-Implementation-SSI-DID`: 7 heads, none named `review-codebase*`
- `nikhilprakash24/TEST` (the sandbox-onboarding fork): 6 heads, none
- `nikhilprakash24/CVIN_2024`: `main` only
- full history of every fetched ref: no commit message or file mentions the branch or its session id

Session id `011CUp…` is older than both surviving Claude lineages (`011CUy…`, `011CUz…`,
both from 2025-11-10), so it was most likely an early session that was never pushed.
Its substance appears to have been taken over by the later review artifacts on the
trunk: `docs/AUDIT_01_ORIGINAL_GOALS.md`, `docs/RESEARCH_AUDIT.md`,
`docs/REVIEW_CV2X_TESTBED_LINEAGE.md` (Pass 4) and the two after-action reports.
**Review 2 therefore starts from those documents and the code as it now stands.**
If the planning chat holds that session's notes, attach them and I'll reconcile
them against `docs/REVIEW_02_CODEBASE.md`.

## 2. Lineage map at the save point

| Ref | Relation to working branch | Last activity | What it holds |
|---|---|---|---|
| `claude/cv2x-testbed-setup-011CUz5…` (**trunk**) | 71 ahead / 6 behind; forked at `084edfd` | 2026-09-30, `3203ee8` | Thesis chapters 1–7, nine standards, 219 Hardhat / 60 Python tests, W3C external conformance 328/441, claim register #1–#28, audits, Pass 4 review, `HANDBACK_2026-09-30.md` |
| **working branch** (this) | — | 2026-10-03, `441791b` | Data-collection framework ("CRUD and Beyond"): 18-op catalogue, adapter harness for ERC-1056/721/725, first trunk-traceable metrics run, `HANDOFF-DATA-COLLECTION-FRAMEWORK.md` |
| `sandbox-onboarding` + `wo-s0/*` + `docs/root-readme` | **unrelated history** (TEST repo's stream) | 2026-09-24 | WO-S0 onboarding of the sandbox; cross-referenced from `TEST_ONBOARDING.md`. **Not merged**, by design |

Dry-run merge of trunk → working branch: **3 conflicts**.
- `.github/workflows/benchmark.yml`: both edited
- `.gitignore`: both edited
- `docs/MEASUREMENT_CONDITIONS.md`: **add/add**. Each lineage created its own file under the
  same name: the trunk's claim register #1–#28 and this branch's conditions of record.
  This is the only substantive conflict, and resolving it means merging two registers
  into one.

## 3. State as reported by each lineage (to be re-verified after the merge)

| Check | Trunk handback (2026-09-30) | Working branch handback (2026-10-03) |
|---|---|---|
| Hardhat | 219 passing | 47 + 23 conformance (4 declared n/a) |
| Python | 60 passed | 28 passed (verified today; VC layer only exists here) |
| Compliance checker | 93.2 % (merged instrument) | — |
| `package-lock.json` | tracked (`ed85dfd`) | **absent**, so `npm ci` fails on this branch (verified today) |
| Headline results | 9-standard gas, PKI-vs-ERC-1056, external conformance | L1–L6 metrics for 3 substrates; H1 "≥10×" **not supported** (2.7× / 3.0× lifetime) |

## 4. The plan (clean)

| Phase | Output | Exit criterion |
|---|---|---|
| **0 Save point** | this file, committed and pushed | on origin |
| **1 Integrate** | merge the trunk into the working branch; one unified `MEASUREMENT_CONDITIONS.md` (trunk register #1–#28 plus the data-collection conditions as new sections/rows); CI workflow union | Hardhat, Python and checker all green on the merged tree; numbers match §3 or the difference is explained |
| **2 Review 2** | `docs/REVIEW_02_CODEBASE.md`: severity-ranked findings across contracts, benchmark harness, SSI/VC Python layer, testbed scripts, CI, and claims-vs-code | every finding has file:line, failure scenario, severity |
| **3 Remediation plan** | `docs/PLAN_REVIEW_02.md`: findings grouped into passes; each item is fix / test / or document-as-limitation | each item has an owner (session or author) |
| **4 Pass 1** | fixes for every session-owned item rated High or Critical, with tests | suites green; each fix has a regression test where testable |
| **5 Pass 2+** | re-review the Pass 1 diff adversarially, then take Medium items; a third pass if Pass 2 finds new issues | no open session-owned High or Critical; diff re-reviewed |
| **6 Handback** | `docs/HANDBACK_2026-10-03.md` + after-action report | pushed; resume-in-five-commands verified |

**Out of scope for review 2** (author-gated, unchanged from the trunk handback §4):
pushing tags v0.7.0/v0.8.0, SUMO install go-ahead, framing approval for
`REVIEW_CV2X_TESTBED_LINEAGE.md` §6, decisions SC-05/SC-06, Sepolia secrets, notebook
index and Chapter 2 citations. Review 2 lists any new author decisions it surfaces and
does not make them.

## 5. Standing rules carried forward
- Author-attributed commits, no AI trailers; commit and push at every phase boundary.
- A number enters a chapter only with a register row of status V (`MEASUREMENT_CONDITIONS.md`).
- No test is skipped or weakened to get green. A failing claim is restated, never hidden.
- Never end abruptly; every pass closes with its report.

## 6. Documents this review will produce
1. `docs/HANDOFF_2026-10-03_REVIEW2.md` (this file)
2. `docs/REVIEW_02_CODEBASE.md`
3. `docs/PLAN_REVIEW_02.md`
4. `docs/AFTER_ACTION_REPORT_03.md` (opened at Phase 1, closed at Phase 6)
5. `docs/HANDBACK_2026-10-03.md`

## 7. Resume from this save point
```bash
git clone https://github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID && cd CVIN-SC-Implementation-SSI-DID
git checkout claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt
git log --oneline -1 -- docs/HANDOFF_2026-10-03_REVIEW2.md   # this save point
# then follow §4 from the first phase whose output is not yet on the branch
```
