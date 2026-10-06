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

- **S0 done**: local tags `pre-merge/sandbox` (`b70081c`) and `pre-merge/review2` (`fa6188e`).
- **S1–S3 executed** (`git merge --no-commit --no-ff` of the review-2 trunk; 64 unmerged paths):
  - *Mechanical, per the defaults:* research copies kept (M-D); their two new tests re-homed
    into the layered tree (M-E) and one relative `require` repaired; their three same-named
    after-action reports written to `docs/review02/AAR_REVIEW2_03/04/05.md`, ours kept (M-I);
    their clause-level MOBI checklist taken, ours kept as `…_2026-10-03_preview.md`; their
    experiment scripts and results of record taken, ours archived under
    `cv2x-testbed/{scripts,results}/archive-2026-10-03/` (M-G); their resolver, conformance
    generator and inputs, and ERC-1056 provider taken (M-F); the 14 benchmark result files and
    the testbed artifacts kept as placeholders for regeneration.
  - *Contracts, by hand:* `ERC1056Registry` ours (modifier form, three-arg `DIDRevoked`,
    M-B) with their `virtual`; `MOBIVIDRegistry` union (D10 ≡ K-15 comment merged; K-3
    override, K-4 guard and `anchorVehicleKey` all present); `CVINVehicleDIDRegistry` K-1 (M-C);
    ERC-1155 ours (K-13 ⊂ D7/D8); LSP8 union (`_normalizeVIN` + generation store); ERC-735
    union (K-2 revoked-content check, then D25a authorisation, then D25b VIN binding);
    CVIN-Combined per M-A (no `changed[]` advance; `DIDClaimChanged` kept). MOBI mirrors copied
    byte-identically; both Hardhat projects compile; testbed flat ABI/bytecode rewritten; their
    `check_artifacts_fresh.js` passes.
  - *Documents:* `INDEX.md` union with a dual resume pointer; `SCOPE_CHANGES.md` rebuilt from
    ours plus their SC-02/M5 note; `README.md` H-lines from theirs with 335/336, gas table
    regenerated; register: their rows kept, ours appended as #40–#43 with their status
    (M-H); conformance write-up keeps both histories (their §7–§9 → §9–§11).
  - *Provider:* `mobi_vid_provider.py` ours plus their `_registered_key_for` seam (sender by
    `vehicle_identity` or DID, case-insensitive), `vehicle_identity` on signed messages, and the
    `receipt.status` check; our on-chain key fallback sits inside the seam.
  - *Tests adjusted to the decisions:* K-1 `did` argument (3 call sites), K-3 `changeOwner`
    expectations (2), M-A `changed[]` and walk assertions (4), M3 `attestEvent` pin re-measured
    169,295 → **169,361** (+66 dispatch from `anchorVehicleKey`/K-3/K-4), ERC-1155 revert string
    (theirs → ours), the strict security harness's ERC-1155 hijack cell now expects the D7
    reason string instead of the OZ approval error; their harness adapters updated for our
    contracts (ERC-721 issuer VIN without I; ERC-735 per-topic `authorizeIssuer` as part of the
    operation; ERC-1155 credential hash → type 6..255, `issuerTransferIdentity`, revoke-then-burn
    on deactivate); the sandbox MOBI adapter's `changeController` uses
    `transferVehicleOwnership` (K-3). `package.json` globs and `security_scenarios.js` import
    repointed to the layered tree.
  - *Gate results:* Hardhat **536 passing / 23 pending / 0 failing**; review-2 Python suite
    **358 passed, 0 skipped** (fresh node on 8548; a leftover node from the analysis worktree
    had been answering on that port and failing the fixtures' probe — found and stopped by pid);
    sandbox Python **260 passed** (one L4 schema test taught the review-2 freshness record's
    `latency` row list); adapter smoke 11/11; checker on the merged resolver **94.3 %** (floor
    stays 94.0, M-L).

## 3. Decisions
- **R-A** — the merge is executed on this branch by merging the parallel trunk in, not the other
  way round: the session's push scope is this branch only, and the merged history is identical
  whichever side hosts it. Which branch becomes the default afterwards is the author's call.
- **R-B** — the Inkwell/`npat-planning` branch is not merged; it is unrelated to the thesis and
  belongs in its own repository (recorded for the author).
- **R-C** — defaults M-A…M-L in `PLAN_MERGE_LINEAGES.md` §1 are taken as written unless the author
  overturns them; each is restated in the merge commit's resolution notes.

## 4. Closing — *(written last)*
