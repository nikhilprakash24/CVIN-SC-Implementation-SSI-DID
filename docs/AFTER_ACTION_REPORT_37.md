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
