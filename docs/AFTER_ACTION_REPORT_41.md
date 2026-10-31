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
