# WM-2 A5 — Claims Checked Against Their Result Files (plan, written before building)

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-23. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`;
`docs/PLAN_WM-2.md` A5 (audit T-F3: an edited #44 passed every guard).

**Gate:** CI fails on (a) a V row without a source file, (b) a declared source that is not a tracked file or names
no row, (c) a number quoted in a V row's claim that its result files do not contain.

## Design
1. **`docs/testing/claims.yaml`** — one entry per register row: a stable string id (`c25-nine-standard-gas`), the row
   number, and for every V row the result files that carry its numbers. Hand-maintained; the register stays the
   source of the claims' text.
2. **`docs/testing/check_claims.py --check`** (in CI and the pre-push check):
   - every register row has exactly one entry and every entry a row (ids unique);
   - every V row lists ≥ 1 source, every source is a tracked file;
   - **number check:** each **bold** number in a V row's claim cell (the headline values) must occur in at least one
     of its sources, compared after normalising (thousands separators removed; a file value rounded to the number
     of decimals the row shows). A bold number that is legitimately not in any file — a ratio, a difference, a count
     derived by hand — is listed under the entry's `derived:` with its formula in words; the checker refuses a
     `derived:` value that *is* found in a source (so the list cannot hide drift).
3. **Probe** (`docs/testing/probe_check_claims.sh`): the check must fail on (i) a bold number edited in a V row,
   (ii) a source removed from claims.yaml, (iii) an entry for a row that does not exist; and pass on the tree.

## Not in scope
Checking non-bold numbers (history notes keep old values on purpose); E/S/U rows' numbers.
