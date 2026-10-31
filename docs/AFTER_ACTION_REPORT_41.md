# After-Action Report 41 — The Stale-Figure Checker Reads HTML and TeX

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-31, after report 40 closed (CI green on `f98cf45`). **Brief (the author):** "go ahead with the HTML
and TeX checker too" (the rest of T-19). **Claim, pushed before the work:** this pass changes the checker and the
documents it flags; it re-runs no producer.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| S1 | `check_docs_numbers.py` scans tracked `.html` and `.tex` files outside the result folders: HTML as its visible text and its inline script data (a page's numbers often live in an embedded JSON snapshot), TeX with its thousands groups (`1{,}757{,}881`, `\,`) and math markers normalised | shown to fire on a superseded value in each format; every real hit fixed at its source (the generator, not the output) or classed as history with a reason |
| S2 | Records; CI | CI green on the closing commit |

## 2. Execution log
- 2026-10-31 — report opened.
- **S1, HTML and TeX.** `check_docs_numbers.py` now reads tracked `.html` (visible text and inline script data; style
  blocks, comments and tags removed with their newlines kept, so a hit names the page's own line; entities and no-break
  spaces decoded) and `.tex` (thousands groups `1{,}757{,}881` and `1\,757\,881` joined, `\%`, `\times`, `$` and
  `\text{}` normalised). Scope 206 → 215 files.
  - **Shown to fire in each format:** `warm verify&nbsp;0.153&#160;ms` in the results dashboard's text and
    `"warm":"0.153 ms"` in its script data are both caught; `$1{,}757{,}881$` in a TeX table is caught; restored, clean.
  - **What the first run found:** 21 superseded figures in 10 files, 19 of them in the provenance dossiers of
    `docs/artifacts/`, which their manifest already declares dated July snapshots, and 2 in
    `docs/figures/verification_dashboard.html`, the verification snapshot of 2026-10-03 at `cac1729` (it quotes 369
    Hardhat tests). Both are classed as history with those reasons rather than rewritten, since each is a dated record and
    the dashboard would need a new suite snapshot to regenerate. `docs/ARTIFACTS_MANIFEST.md` no longer says the checker
    reads Markdown only.
  - In scope and clean: the results dashboard, result cards, contribution record, master atlas, presentation page and
    the two security TeX tables. The thesis has no TeX yet; when chapters are typeset, the checker reads them unchanged.
- **Finding, not fixed here:** `docs/PROJECT_SUMMARY.md` (September) presents the verification snapshot's gas as "the
  first gas numbers traceable to this trunk"; it passes the checker only because its old values have no entries. It is a
  dated document still listed as canonical in `docs/INDEX.md` for "what exists". New task T-20: mark it dated or
  refresh it.

## 3. Closing
T-19 is complete: the stale-figure checker reads Markdown, SVG, HTML and TeX, each shown to fire, with no new CI step
(CI and the pre-push guard already run it). Every real hit was a dated record and is classed as history with its reason.
