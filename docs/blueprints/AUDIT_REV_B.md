# Blueprint Set — P1 Number Audit (Rev A → Rev B)

**Date:** 2026-10-22 · **Scope:** every measured value drawn by `sheets_*.py`, checked against its result-of-record file and its row in `docs/MEASUREMENT_CONDITIONS.md`. **Result:** 17 corrections on 10 sheets, all applied in Rev B. Every sheet now carries revision row B.

## Method

Each number on a sheet was traced to the register row it cites and the file that row names. Values copied from descriptive documents were replaced with result-file values: `CAPABILITIES.md`, `README.md` and the analytic tables in `LATENCY_BUDGET.md` §3. Wrong row numbers were corrected. Values the register marks superseded (S) were replaced or qualified.

## Corrections

| # | Sheet | Rev A | Rev B | Source |
|---|---|---|---|---|
| 1 | BP-103 | setAttribute 35,512 · addDelegate 54,853 · changeOwner 51,764 (CAPABILITIES, July) | 35,494 · 54,831 · 51,754 | `gas_benchmark.json`, #25 |
| 2 | BP-102 | tx anatomy total 35,512 | 35,494; the segment split is now marked estimate E | #25 |
| 3 | BP-102 | attestEvent 121,110 → 192,718 | adds the current build value, 192,671 receipt gas | #28 (192,718 is not reachable on this build) |
| 4 | BP-205 | 192,718 as the fixed cost | 192,718 July, 192,671 now, 169,295 execution gas | #28 |
| 5 | BP-403 | 121,110 → 192,718 | same qualification as #4 | #28 |
| 6 | BP-103, BP-201 | HTTP read path cited as #38 | #39; adds the value, 203 ms median at h = 50 | #38 is the pseudonym pool |
| 7 | BP-201 | external W3C suite 336/441 | 335/336 generated tests | #24 (the denominator changed; 336/441 is S) |
| 8 | BP-201, BP-202 | internal checker 94.3% cited as #23 | #4 | #23 is message size |
| 9 | BP-201 | M0 resolve 0.009 ms "descriptive" | 0.0089 ms median, cold | `docs/figures/resolution_latency_M0.json` (no register row) |
| 10 | BP-301 | 12/12 use cases cited as #22 | no register row; source is `test_use_cases.py` | #22 is cv2x registry gas |
| 11 | BP-301 | birth 16.9 ms (an old #21 register latency, S) | 14.13 ms median, MOBI-VID-V2 birth | #33 (definition differs from #25 gas; flagged) |
| 12 | BP-301 | forged certificate fails at message 11 | message 12, where verification runs | sheet logic |
| 13 | BP-302 | 1.65 M verifications, 90 failures = 3 attacks × 30 | 1,650,318 verifications, 150 failures = 5 attacks × 30 | #27 |
| 14 | BP-302 | one-call refresh "≈95" | the knee is not confirmed: no finite k reaches P* = 100 on the #37 host | #37 |
| 15 | BP-302, BP-502 | P*(0.5) at k = ∞ ≈ 116 (median) | 110, using the mean, as the register does | #32 |
| 16 | BP-502 | PKI 0.321 / 0.366 ms (LATENCY_BUDGET §3, older #21) | 0.253 / 0.329 ms; P* recomputed to 98 / 197 / 395 | #21 |
| 17 | BP-501 | 4337 dial 96,228 vs 49,366 · lifetime 2.6× / 3.0× | 96,173 vs 49,343 · 2.57× / 3.00× | #25, #30 |

## Checked and unchanged

All ten create-gas cells (#25). The spread is 32.2×. The EntryPoint delta is +46,830 (96,173 − 49,343). The 43/43 and 54-cell attack totals match `attack_results.csv`. Every Lens 2 cell matches `security_matrix.csv`. The basic-set coverage matches A6. The freshness fit 0.428 + 10.52/k, k ≈ 146, and the staleness bound of k − 1 all match #32. The V2V figures 0.153 [0.151, 0.154], 0.399 and 0.094 match #27. MOBI birth gas 299,143 matches #25.

## Found outside the sheets (not changed here)

These are pre-existing drift points in other documents. They are reported, not fixed, because they are outside this change.

- **`README.md` line 151 and `CAPABILITIES.md` line 314:** both say "90 failures = 3 injected attacks". Register #27 says 150 failures = 5 attacks × 30.
- **`4_comparison-framework/results/w3c_compliance.json`:** the file is dated 2026-07-23 and scores 93.18% (40 PASS, 2 PARTIAL). Register #4 says 94.3%. The committed snapshot predates review 02 and should be regenerated.
- **Register #26:** the header still reads "P*≈772 at 0.130 ms/neighbour". Its own body records the re-execution at 0.164 ms/neighbour.
