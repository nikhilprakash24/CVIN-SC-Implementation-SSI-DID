# After-Action Report 03 — Review 2 (2026-10-03)

**Opened:** at Phase 1, before the review ran. **Status:** OPEN, updated as each phase lands.
**Plan of record:** `docs/HANDOFF_2026-10-03_REVIEW2.md` §4.

## Phase log

| Phase | Commit | Result |
|---|---|---|
| 0 Save point | `cced8ac` | Handoff and plan pushed. The requested resume branch `review-codebase-011CUp…` is not on any reachable remote (3 repos checked), so review 2 starts from the trunk's review documents |
| 1 Integrate | `434669d` | Trunk `3203ee8` merged into the data-collection lineage. 3 conflicts resolved (register unified as tags M1/M1-H, rows #29–#31). **242 Hardhat passing / 4 pending, 60 Python, checker 93.2 %**: identical to both handbacks |
| 2 Review | `d0fe9f0` | `REVIEW_02_CODEBASE.md`: 64 findings across five lenses (contracts, harness, SSI/VC, testbed, CI/claims); **3 Critical, 13 High**. The commit message says "62 / 4 Critical / 16 High", a miscount corrected here. A metrics re-run on the merged tree found 12–25-gas drift between runs (H-3) |
| 3 Plan | `d0fe9f0` | `PLAN_REVIEW_02.md`: four parallel Pass 1 streams on disjoint files, Pass 2 re-review and Medium items, 4 author decisions held back |
| 4 Pass 1 | `282d63e` … `8409814` | CI Q-1/Q-12 (`282d63e`), Q-2 (`d1735f5`); streams merged: P1-T `93580a7`, P1-K `0f45348`, P1-S `8d31f43`, P1-H `59405ff`; run of record `8409814`; register and HANDOFF updated (this commit). **Hardhat 276 passing / 4 pending · Python 161 + 34 (0 skipped with a node) · checker 94.3 % · 12/12 use cases · nine-standard determinism 55/55 · metrics gas tables byte-identical between runs.** Every Critical and High in the review that the session owns is fixed, each with a regression test that fails on the old code |
| 5 Pass 2+ | — | |
| 6 Handback | — | |

## Decisions taken in-session (and why)
- **Merge, not rebase.** Both lineages are pushed and cited by commit id in documents; a
  merge keeps every cited id valid.
- **`sandbox-onboarding` not merged.** Its history is unrelated (TEST repo's stream);
  `TEST_ONBOARDING.md` already cross-references it.
- **Register unification.** The data-collection file claimed that harness output was the
  *only* source of chapter numbers. That contradicted the trunk register, which admits
  M0/M1/M2 sources. Resolved by scoping the harness rule to tag M1-H. No number changed.
- **CI.** The harness's CI job moved to `actions/*@v4`; the v3 artifact actions are
  retired on GitHub and would fail the job.

## Notes in flight
- **Pass 1 ran as four isolated worktrees** (contracts, harness, SSI, testbed), each restricted to disjoint
  files and forbidden to edit shared docs. Each stream wrote a report (`docs/review02/PASS1_{K,H,S,T}.md`)
  with proposed register text, and the session applied all register edits in one place. All four merged
  with **zero conflicts**.
- **#21 moved, and in the direction the review predicted.** PKI verify now does its CA check
  (×1.6–2.0 slower, same host); ERC-1056 verify lost a redundant RPC (×0.64). The gap goes from ≈57× to ≈40×;
  the ordering is unchanged. A library upgrade on this host (`cryptography` 41 → 49) made every PKI cell
  2–4× faster on its own, so the stream ran a same-host A/B to separate the two effects.
- **Harness: K-1 moved an ERC-1056 cell by +22 gas** through selector dispatch (`setVehicleAttributes`
  signature changed). It is deterministic, explained, and recorded in #1 and #29.
- **The checker score went up, not down** (93.2 → 94.3 %): the resolver fix (S-10) made one PARTIAL a PASS.
  The scoring was not touched; T-7 stays with the author, and the CI floor stays at 93.0.
- **Port gotcha:** the MOBI pytest fixture starts its own node on 8547; testbed tests need a different
  port (CI uses 8548). Recorded in the CI job comment.
