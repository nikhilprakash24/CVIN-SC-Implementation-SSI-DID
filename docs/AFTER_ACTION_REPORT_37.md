# After-Action Report 37 — Unblocked Items U9 (CI Python Pins), U8 (I-05 Model) and U6 (Chapter Audit)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-23, after report 36 closed (CI green on `558fc9d`). **Brief:** the author's "all" for
`docs/planning/UNBLOCKED_WORK_2026-10-23.md`.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| U9 | CI installs Python packages from one pinned file, `ci/requirements-ci.txt`, instead of unpinned names in seven steps | CI green with the pins |
| U8 | `docs/phase2/briefs/i05_model.py` computes the I-05 brief's predictions from its V-row inputs, labelled as a prediction | `--check` reproduces the brief's table, shown to fire |
| U6 | Read-only audit of chapters 1, 2, 4, 6 and 7 against the claim register, to `docs/thesis/CHAPTER_AUDIT_2026-10.md`. No chapter text changes | every quantitative claim classed |
| R | Records, CI | CI green on the closing commit |

## 2. Execution log
- 2026-10-23 — report opened.
- **Lost work, redone.** The first U9 and U8 commits were made locally and not pushed; the container was reclaimed
  and they were lost. Both were rebuilt from the session record on 2026-10-24. Rule carried forward: push each
  finished step at once.
- **U9.** Seven `pip install` steps in three workflows now read `ci/requirements-ci.txt`. The pins are the versions
  the grand run of 2026-10-23 passed on; CI's install logs do not print versions, so these are the only known-good set.
- **U8, I-05's model as code.** The script computes P0 to P3 from the brief's V-row inputs (#32, #37, #52) in exact
  decimals and prints them labelled as a Phase 2 prediction. Its `--check` reproduces the brief's table (P0 k = 40 to
  51, P1 12 to 14, P2 52 to 65, P3 ≈ 1.9 to 2.1, 5.9 and 49) and was shown to fire on an edited P1 row. It runs in
  CI's document step and the pre-push guard.
- **Master plan (the author's request of 2026-10-24).** `docs/MASTER_PLAN_2026-10-24.md`: all phases, milestones
  and passes; the lineages, pull requests and the other branches of this repository (five research branches hold
  unmerged work, none reviewed: new task T-12); the plan forward; a Phase B section of twelve open questions in the
  form the sister session's master plan uses; the to-dos and blockers with what each unblocks; a reading order; and
  the artifact catalogue by importance and by date, with the published pages. The sister session's master plan could
  not be read here (the documents connector did not connect), so §6 follows its described form, not its text.
- **Visual atlas.** `docs/figures/master_atlas.html`, published as the private page *CVIN-SC Master Atlas*
  (https://claude.ai/artifact/99tvf1uGNF8r8ekpWXJffM); its content is the master plan's.
- **U6, chapter audit (read-only).** `docs/thesis/CHAPTER_AUDIT_2026-10.md`, written by a subagent from the register
  and the latency charter; no chapter changed. Over chapters 1, 2, 4, 6 and 7: 39 OK, 22 mismatch, 2 overstated,
  16 unsourced, 13 stale. Two findings re-checked here against the register and confirmed: chapter 1 calls H5
  "supported outright" while #36 has CVIN-Combined dominated by ERC-4337 on all six criteria; chapters 6 and 7 quote
  the V2V warm verify as 0.153 ms where #27 reads 0.142 ms [0.141, 0.143]. **Finding about the tooling:** the
  stale-figure checker did not catch 0.153 in the chapters, so its entries miss superseded #27 values; this goes to
  U10. The fixes are WM-2 D1's editing half, which waits on D-1.
- **CI after U9 (`6a7fe6c` onward): 2 workflows red.** Two jobs set a subdirectory as their working directory, so the relative path to the pins file failed. Every install now reads `$GITHUB_WORKSPACE/ci/requirements-ci.txt`.
- **CI green on `e481889`** (all four workflows), with the pinned packages. Report stays open for U7, U5, U10, U11 and U12.
- **U10, the stale-figure checker.** Eight entries added for superseded #27, #28, #22 and #25 values, with exact
  phrases for the small counts (150 of 150, 5 per run × 30). **Finding: A5's correction of #27 (2026-10-23) never
  reached the citing documents.** The new entries found the old V2V figures (0.153 ms, cold 0.399, PKI 0.094, 150
  failures, ~650×) in 24 files, including the README and chapter 5, which the chapter audit had not covered. Outside
  the thesis, all were corrected to #27's values (0.142 ms [0.141, 0.143], cold 0.363, PKI 0.090, 210 = 7 × 30,
  ~700× against the 100 ms budget), and the July attestEvent pair now names itself as history. The 28 hits in
  `docs/thesis/` are left for WM-2 D1: the checker gained a **pending** class that prints them, does not fail on
  them, fails on any new hit elsewhere (shown to fire), and reports a pending glob as CLEARED once its hits are gone.
- **U5 = WM-2 D2, the RSU-to-RSU note.** `docs/design/RSU_TO_RSU_NOTE.md`. A single RSU-to-RSU hop uses the
  mechanism #45 already verifies (credentialed sender, permitted message type, expiry, replay; checked in
  `infrastructure_layer.py`); the new part is relay authority (origin versus the right to forward), which is the V2V
  relay gap C3 already states. Recommendation **D2-a, scope out** with a chapter 6 paragraph; D2-b (one relay type,
  three checks, about one pass) if the author wants evidence. New author decision D2.
- **U7, TDP review (read-only).** `docs/tdp/REVIEW_2026-10.md`, written by a subagent; no TDP document changed by
  it. 101 claims in TDP-001, 003, 007, 008 and 009: 45 OK, 6 mismatch, 2 overstated, 37 stale, 11 missing. Most
  stale items come from the A3b re-runs of 10-22 and 10-23; layer 5 is absent from all five documents. Two findings
  re-checked here and confirmed: TDP-001 calls #39 "status U" (it is V); #21's uncached verify is now 15.513 ms, not
  9.654. TDP-001's 0.153 ms had already been corrected under U10. The corrections are a follow-up (new task T-15),
  since the TDP has its own revision rule (a revision letter per document).
