# Base-Completion Plan — a thesis-complete base before the notebooks

**Goal (researcher's).** Reach a **self-contained base that would pass as a thesis on
its own**, then layer in the researcher's additional material ("a couple notebooks
full"). Base first; expand second. This plan is the path to that base and is tracked
in `META_COMMENTARY.md`; the argument it serves lives in `COMPOSITION.md`.

## What "thesis-complete base" means (the examiner's checklist)
1. A coherent argument end-to-end — **have it** (`COMPOSITION.md`).
2. Claims that survive scrutiny — **needs** the `RESEARCH_AUDIT.md` reframes applied.
3. A literature review — **needs** the researcher's citation set (Ch. 2).
4. Examiner-grade prose — **needs** a writing-discipline pass, chapter by chapter.
5. An assembled thesis document — **needs** LaTeX assembly (UBC template).

## Gap to close (priority order)
| # | Item | Owner | Blocking? |
|---|---|---|---|
| 1 | Ch. 2 literature review | researcher (citations) → me (draft) | **yes — #1** |
| 2 | Apply audit reframes (defensible claims) | me | no (ungated) |
| 3 | Scaling experiments → §5.9 | me (in flight) | no |
| 4 | Chapters → examiner-grade prose | me | no (Ch.5 first) |
| 5 | LaTeX assembly + slots for notebooks | me | no |

## Blocking from the researcher (minimal, precise)
1. **Ch. 2 citation set** (BibTeX or rough list) — unblocks the whole "make it a real
   thesis" phase. #1.
2. **A one-page index of the notebooks** — *what's in them*, not the content — so the
   base's extension slots are shaped correctly and nothing is duplicated.
3. **GitHub access** → push ~45 commits + version tags.
4. **Sepolia creds** (RPC + funded test key) → real testnet witness → RQ1 external
   validity → cut `v0.9.0`.
5. **Which hypotheses are load-bearing** for the defense → concentrate polish there.

## Sequence
- **Me now (ungated):** scaling → §5.9; apply audit reframes; Ch. 5 to examiner-grade
  (writing exemplar) → re-thread `COMPOSITION.md`; assemble LaTeX skeleton with
  labeled slots for the notebook material.
- **Researcher (when convenient):** citations + notebook index + access + Sepolia.
- **Then:** Ch. 2 written; remaining chapters to examiner-grade → **base is
  thesis-complete.**
- **Then:** integrate the notebooks against the slotted base.

## Design principle for the base
Build the base to **receive** the notebooks: leave labeled extension points (new
experiments slot into §5.x; new related work into Ch. 2; new discussion threads into
Ch. 6) so the additional material strengthens a solid base rather than reshaping an
unfinished one.
