<!-- Renamed at the merge of 2026-10-06 from docs/AFTER_ACTION_REPORT_05.md (review-2 lineage); the sandbox lineage's report with that number keeps the original path. See docs/PLAN_MERGE_LINEAGES.md M-I. -->
# After-Action Report 05 — Next-session list after the follow-up (2026-10-04)

**Opened:** before the pass ran. **Status:** CLOSED 2026-10-04; results are in `docs/HANDBACK_2026-10-04.md` §4.
**Input:** `docs/HANDBACK_2026-10-04.md` §4, the second "Next session (executable now)" list.
Author decisions (handback items 1–12) are **not** taken here.
**Base:** `a204451`. A parallel harness session also pushes to this branch (register #34–#35 are
its rows). This pass numbers new register rows from **#36**, fetches before every push, and stays
off `1_blockchain-identity/benchmarks/**`, `results/metrics/**`, `HANDOFF-DATA-COLLECTION-FRAMEWORK.md`
and register §5.

## Plan

| Stream | Item | Output | Gate |
|---|---|---|---|
| **G-R** resolver | Fix R1–R4 (104 of the 105 external-suite failures) in `did_resolver.py`'s metadata classes; re-run w3c/did-test-suite @ `939b31d` with the unchanged method | `docs/conformance/` §9, register #24 | ≈440/441 expected; no regression; internal checker reported before and after |
| **G-M** MOBI quick fixes | `getVehicleDID` emits `did:ethr:0x7a69:0x…` (K-15/checklist); OWNER-role event types restricted to that vehicle's current owner (K-15: the global OWNER role can file theft reports against any vehicle). The `did:mobi` placeholder resolver is left (design) | contracts + tests; regenerated gas with before/after | Hardhat green; determinism gate 55/55 |
| **G-K** experiments | One-call refresh for freshness-k (a `changed()` probe, full resolution only when it moved), re-run #32; M5 pseudonym pool, as pre-registered in `PLAN_MOBI_SUMO.md` A.2 | `cv2x-testbed/results/freshness_k*`, M5 results, register #36+ | pre-registered verdicts reported as-is |

## Phase log

| Phase | Commit | Result |
|---|---|---|
| Open | `f73e81e` | Plan; new rows were to start at #36 |
| G-R | merge + #24/#4 commit | Resolver R1–R4 fixed; suite **335/336** (denominator 441 → 336); generator and checker instrument corrections disclosed |
| G-M | merge + `6e098fd` | `getVehicleDID` well-formed; OWNER-role events per vehicle; 2/55 gas cells; checklist updated |
| M4 re-run | (session) | #33 re-measured on the post-G-M bytecode; verdicts unchanged; event gas +223 |
| G-K | merge | Probe refresh (#37) and M5 (#38) |
| Close | this commit | Register, handback, README |

## Notes in flight
- **My plan's "≈440/441" was wrong.** The suite generates tests only for keys that are present, so
  removing null keys shrank the denominator to 336. #24 states this so the two totals are never
  compared as a percentage.
- **Two instrument changes were accepted, with disclosure.** (1) The suite input generator crashed on
  the fixed resolver (`assert error is None` on an absent key) and passed `resolve()` output off as
  `resolveRepresentation()`; it now calls the real function, with DIDs and vectors unchanged. (2) The
  checker's 7.1.2 check enforced a spec violation (`contentType` on `resolve()`). It was corrected to
  DID Core §7.1.2 and is now stricter (the stream must parse to the DID). The score is unchanged at
  94.3 %, which is why it is disclosed in #4 rather than buried: the old check would read 92.0 %,
  below the CI floor. This is author decision 13.
- **Stale-bytecode trap avoided.** G-M rebuilt the testbed MOBI bytecode that #33 had measured, so the
  session re-ran M4 rather than leave #33 describing code no longer in the tree (the R2-H2 lesson).
- **Register-number collision.** The parallel session took #36 while G-K was running, so G-K's
  proposed #36/#37 were entered as #37/#38 and every reference was updated.

## Closing summary
- All four items on the list are done. New rows #37 and #38; #4, #24, #25 and #33 updated.
- Two pre-registered predictions failed and are reported as failures: the M5 gas, and the one-call
  knee (not reached on this host).
- Three new author decisions (handback items 13–15).
