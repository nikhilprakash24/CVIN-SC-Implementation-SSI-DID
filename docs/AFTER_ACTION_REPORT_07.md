# After-Action Report 07 — Reconciling the Parallel Work of 2026-10-04/06, then D27 and the Lifecycle-Parity Re-run

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-06, before any change; updated per step; closed at the end
**Trunk at start:** `b70081c` on `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy`, clean, CI green
**Brief:** "continue — reference other work done as well in recent days." The author has been
working in other sessions in parallel; this pass must first find that work, say what it is,
reconcile it with this branch (what agrees, what overlaps, what conflicts), and only then
continue the executable list from the handback addendum 0d (D27, lifecycle-parity re-run).

## 0. Rule for this pass
Nothing from another branch is merged or copied until it has been read and its relation to
this branch is written down here. Reconciliation is by document first (what each branch
claims, which numbers, which instruments), by code second. A conflict between two
measurements of the same quantity is resolved by re-execution on one tree, never by
choosing a number.

## 1. What the fetch found (2026-10-06)

| Branch / tag | Last commit | Subject | First reading |
|---|---|---|---|
| `claude/testing-suite-organization-z5j7dc` | 2026-10-06 | Plan: organised testing suite and results (TSR Plan v1.0), second-pass sheet, as-found inventory | a parallel session organising the test suite and results — overlaps directly with the sandbox/layered-suite work of passes 04–06 |
| `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` | 2026-10-04 | Handback §7: log the analysis layer, rubric inputs, HTTP condition and the measured … | a parallel session with its own handback; **now the repository's default branch** |
| `claude/npat-game-planning-011CV17TmUnDjXXG8chDTXd6` | 2026-10-04 | Inkwell: Phase 0 kickoff package … | apparently unrelated to the thesis (to be confirmed) |
| `sandbox-onboarding`, `wo-s0/*`, `docs/root-readme` | 2026-07 / 09-24 | onboarding plans, understanding report, evidence and findings | the earlier "WO-S0" onboarding lineage, previously known |
| tag `asfound/pre-onboarding` | — | — | an as-found marker set by another session |

### 1.1 First reading of the parallel trunk's handback (`docs/HANDBACK_2026-10-04.md` on `clone-cvin-id-scs`)

The parallel branch is not a side stream; it calls itself **"now the single trunk"**: it merged
this branch's state as of `3203ee8` (the 2026-09-30 handback) together with a *second* parallel
lineage, the "data-collection framework" (a metrics harness with adapters for all nine standards,
`HANDOFF-DATA-COLLECTION-FRAMEWORK.md`), then ran a "Review 2" of the codebase — 64 findings from
five lenses, 3 Critical and 13 High — and fixed them in three passes with regression tests, plus
two follow-up passes. It re-executed many results of record (#21, #25, #29–#33, #37, #38), reports
369 Hardhat + 358 Python tests with CI green, and leaves 15 author decisions and a next-session list
(resolver chain read, `attestEvent` restriction, re-run #32/#37 on one host).

Both lineages therefore did overlapping work on the same files from the same base, in the same
48 hours, with different findings, different fixes and different numbers:

| Quantity | This branch (passes 03–06) | Parallel trunk (review 2) |
|---|---|---|
| Base | `3203ee8` | `3203ee8` + the data-collection lineage |
| Commits since base | 35 | 155 |
| Defect/finding register | `DEFECT_LOG.md` D1–D27 (sandbox-found) | `REVIEW_02_CODEBASE.md` 64 findings (K-, S-, H-, T-, Q- series) |
| Contract fixes | D10, D11/D11b, D13, D18, D21, D22, D25, D7/D8, D9 | review-2 K- series (e.g. K-15 = our D10; K-1 selector shift; K-2 bypass; K-3; attestEvent) |
| Nine-standard create spread | 52,170 → 1,680,816 | 52,216 → 1,680,816 (ERC-735 1,535,776 vs ours 1,598,928) |
| External DID suite | 335/336 (fixture and registry-minted DID) | 335/336 (R1–R4 fixed; same denominator change) |
| Checker | 94.3 % | 94.3 % (with a 7.1.2 check correction, disclosed) |
| Tests | 386 Hardhat + 94 Python (layered L1–L4, 92 demos) | 369 Hardhat / 23 pending + 358 Python (metrics harness, MOBI pytest, resolver, testbed) |
| Register rows added | #29–#32 | #29–#38 (collision) |
| Same-named files | `AFTER_ACTION_REPORT_03/04/05.md` | `AFTER_ACTION_REPORT_03/04/05.md` with different content |
| Chapter 5 | regenerated from the re-executed results | not updated (awaiting framing approval) |

A third branch (`npat-game-planning`) carries the review-2 lineage up to `f646e88` plus an
unrelated planning project (`npat-planning/`, "Inkwell"); a fourth (`testing-suite-organization`,
2026-10-06) adds a testing-suite/results plan (TSR v1.0) on top of the parallel trunk.

## 2. Execution log
- 2026-10-06 — report opened; fetch done; per-branch analysis requested (merge bases, commits ahead/behind, files touched, their handback/plan documents). Three read-only analyses delegated: documents (claims, registers, collisions), code (contracts, tests, scripts, results, merge-tree conflicts), and the TSR plan branch against the sandbox already built here.

- **Analyses received and distilled.** The three read-only reports are kept verbatim under
  `docs/reconciliation/` (RECON_DOCS: 21 contradictions and a renumbering; RECON_CODE: 64
  conflicted paths from `git merge-tree`, contract-by-contract table, their suites run in a
  worktree — 369/23 Hardhat, 358 Python, 0 skipped, exact as their handback says; RECON_TSR: 40-row
  mapping of the TSR plan onto the sandbox, 13 naming conflicts). Distilled into
  `docs/REVIEW_03_PARALLEL_LINEAGES.md` (the clean review) and `docs/PLAN_MERGE_LINEAGES.md`
  (the clean plan: decisions M-A…M-L with defaults, steps S0–S10 with gates).
- **Findings that change what I believed.** (1) Their K-15 and our D10 produced byte-identical
  code — the two sessions fixed the same bug the same way without knowing of each other. (2) Their
  review found three things ours did not: forged PKI certificates were accepted (T-1), the ERC-1056
  replay cache could be evaded by re-spelling a DID (Pass 3), and the resolver cache could be
  poisoned (S-10); ours found what theirs did not: the ERC-1155 operator bypass they rated Low is
  the D7 High, the MOBI key was never anchored (D11b), VINs were case-sensitive (D13), and the
  claim-holder accepted impostor issuers (D25). (3) Their `SCOPE_CHANGES.md` was truncated by a
  commit; ours is the rebuild source. (4) Their MOBI checklist found the VID I v2.0 text public —
  our SC-14 rationale is wrong on that point. (5) The D27 I logged two days ago is already fixed on
  their side (S-10, decimal CAIP-10).
- **Scope decision for this pass.** The merge is the next pass, not a side task: ten conflicts are
  design decisions and every result of record must be re-executed on the merged contracts. This
  pass delivers the review and the plan, then starts S0–S3 (one merge commit that compiles and
  passes both test bodies) under the plan's defaults, each default recorded as a decision the
  author may overturn.

## 3. Decisions
- **R-A** — the merge is executed on this branch by merging the parallel trunk in, not the other
  way round: the session's push scope is this branch only, and the merged history is identical
  whichever side hosts it. Which branch becomes the default afterwards is the author's call.
- **R-B** — the Inkwell/`npat-planning` branch is not merged; it is unrelated to the thesis and
  belongs in its own repository (recorded for the author).
- **R-C** — defaults M-A…M-L in `PLAN_MERGE_LINEAGES.md` §1 are taken as written unless the author
  overturns them; each is restated in the merge commit's resolution notes.

## 4. Closing — *(written last)*
