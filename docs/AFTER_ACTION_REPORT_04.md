# After-Action Report 04 — Grand Sandbox, Per-Option Sandboxes, Layered Test Suites

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-03, before any work of the pass; updated as it runs; closed when the
pass's *design step* ends (implementation steps get their own log entries)
**Trunk at start:** `394373c`, clean, CI green

## 0. The brief (author's words, condensed into checkable items)

| # | Ask | Interpretation | Deliverable |
|---|---|---|---|
| B1 | "a grand sandbox as well as sandboxes for each of the options" | One unified base ("grand sandbox", in the sense of the original sandbox guide: a versatile base to build and test anything) plus one sandbox per identity option (nine standards + MOBI VID + the PKI/centralized baselines), each with a uniform entry point | plan §2 (architecture), then implementation steps |
| B2 | "test suites for the basic identity and identity system mechanisms, then SSI, then exemplar complex interactions" | A four-layer suite: L1 identity mechanisms · L2 identity-system mechanisms · L3 SSI (DID/VC) · L4 exemplar complex interactions (use cases, V2V, lifecycle) — with the existing 279 tests re-homed, not rewritten | plan §3 |
| B3 | "each sandbox should highlight and implement every relevant feature even if not used in comparison … that asymmetry will be discussed at length" | Per-option **feature manifests** covering the standard's full relevant surface (off-chain creation and capabilities, on-chain veracity and automation, cryptography and hashing choices), and a **feature-asymmetry matrix** that becomes a thesis section | `docs/FEATURE_ASYMMETRY_MATRIX.md` (generated from the contracts, so it cannot drift) + plan §4 |
| B4 | "first the cleanest review of work and parallel work" | A clean review of what exists across all lineages (trunk, merged analysis lineage, testbed) — not the earlier audits repeated, but the state as one picture, including the duplication the merge left behind | `docs/REVIEW_02_STATE_AND_PARALLEL_WORK.md` |
| B5 | "then a clean plan to check and implement what is left" | A step-by-step plan with acceptance checks per step | `docs/PLAN_SANDBOX_AND_SUITES.md` |
| B6 | "then a clean after action report so we can do this step by step" | This file; each implementation step appends a dated entry | this file |
| B7 | "a meta commentary doc where you think out loud and even brainstorm … find an important organizing and coalescing work" | A thinking-out-loud document: what the pieces want to become, the coalescing move, open questions, risks to the thesis argument | `docs/META_COMMENTARY_2026-10.md` (linked from the existing `META_COMMENTARY.md`) |

Note on "parallel work": the author's notebooks are not in the repository; "parallel
work" here means the analysis lineage merged on 2026-09-24 and the testbed lineage —
the two parallel streams that are now one trunk. The notebook index remains requested.

## 1. Plan for the design step (before executing)

| Step | Work | Status |
|---|---|---|
| D0 | Open this report | ✅ |
| D1 | Read-only sweep: every contract's public interface, the three contract locations, suite layout, the existing meta-commentary's shape | ⏳ |
| D2 | Generate the feature-asymmetry matrix from the contracts (script → markdown) so the review and the thesis cite one source | ⏳ |
| D3 | Write the clean review (B4) | ⏳ |
| D4 | Write the clean plan (B5) with step-by-step acceptance checks | ⏳ |
| D5 | Write the meta-commentary (B7) | ⏳ |
| D6 | Commit, push, hand over; stop at the step boundary — implementation step 1 starts only after the plan has been seen | ⏳ |

## 2. Execution log
- 2026-10-03 — report opened; D1 sweep requested in the same step.
- D1 done. The regex sweep of source files under-counted (multi-line declarations),
  so the matrix was built from the compiled ABIs instead — exact function/event lists
  for all 17 contracts. Findings that shaped everything after: three generations of
  contracts coexist (research copies, the Hardhat tree, the testbed copies); **two
  different contracts are both called "ERC-1056"** and the measurements split along
  that seam; `contracts/MOBI/` duplicates the testbed's three contracts; 279 automated
  tests all sit in L1–L3 with the layers interleaved and L4 has none.
- D2 done: `4_comparison-framework/feature-matrix/make_feature_matrix.py` →
  `docs/FEATURE_ASYMMETRY_MATRIX.md` (surface sizes, 12 capability families × 10 options,
  evidence lists, auditable heuristics). One loader fix on the way (it had picked the
  `IERC735` interface artifact over `CVINVehicleClaimHolder`).
- D3 done: `docs/REVIEW_02_STATE_AND_PARALLEL_WORK.md`.
- D4 done: `docs/PLAN_SANDBOX_AND_SUITES.md` — target structure, the uniform
  `IdentityOption` adapter interface with `NotApplicable` as a first-class result,
  steps S0–S10 each with a "done when", three author decisions, risks and guards.
- D5 done: `docs/META_COMMENTARY_2026-10.md`; the bundle-era `META_COMMENTARY.md` marked
  historical with pointers.
- 2026-10-04 — resumed after a date roll; tree intact; D6: design step committed (`852a508`).
- **Implementation step S0** (author said "continue"; plan §3 decisions taken at their recommended defaults, recorded as D-B/D-C/D-D below): the two ERC-1056 variants named as sub-options in `MEASUREMENT_CONDITIONS.md` §1.1 with their measurement provenance; research copies archived under `1_blockchain-identity/_research-copies/` with a README (references were descriptive only; Hardhat sources unaffected); two CI checks added to the contract workflow — MOBI copies byte-identical (verified identical today), feature matrix not stale (regenerated in CI and diffed). Both checks validated locally before push; CI for the S0 commit recorded below.
- **Implementation step S1**: `sandbox/grand/make_manifests.py` generates 13 per-option manifests (`sandbox/options/<slug>/manifest.yaml`) from the ABIs, the benchmark notes (which name the functions actually measured), the providers' method lists and two declared off-chain families, plus the grand union (`sandbox/grand/manifest.yaml`); `sandbox/grand/run.py matrix|check` renders `sandbox/grand/report/asymmetry.md` and fails on empty cells. Acceptance: 13 options × 14 families = 182 cells, 0 empty. Every cell is `reviewed: false` — the manifests are skeletons until reviewed; `run.py` reports the unreviewed count. Known limitation recorded in `sandbox/README.md`: regeneration overwrites reviewed edits (merge support is an S1 follow-up).
- **Implementation step S2 scaffolding** committed (`b610364`): `sandbox/lib/identity_option.js` (interface, `NotApplicable`), `sandbox/grand/smoke.js` (acceptance runner), adapter conventions; the ten adapters delegated in two groups split by option directory.
- **Implementation step S4**, first attempt reverted by its own gate: moving the test files to `sandbox/suites/` made `npx hardhat test` collect nothing — Node resolves `chai`/Hardhat relative to each file and nothing above `1_blockchain-identity` has a `node_modules`. Second attempt: the layering lives in `1_blockchain-identity/test/{L1-identity-mechanisms,L2-identity-system/{per-option,security}}` (files moved unchanged with `git mv`) and `sandbox/suites` is a symlink to it. Gate: **219 passing** after the move → committed. Lesson recorded: a gate that reverts is worth more than a gate that warns.
- **Implementation step S5** (and the schema half of S6): `sandbox/py-suites/` — L3 gains the external DID-suite *record* regression (335/336 floor) and the internal checker as a test (94.3 floor); L4 gains record-of-record checks for the three experiments (presence, environment header, row structure — numbers never asserted across hosts). Two failed gates on the way: relying on `testpaths` with `-c` collected the whole repository including the chain-dependent `cv2x-testbed/scripts/test_*.py` (5 errors, 1 failure); fixed by naming the paths explicitly in `sandbox/py-suites/run.sh`. Green before commit: 68 tests (60 existing + 8 new).
- **Implementation step S2 done**: eleven adapters (the ERC-1056 split makes eleven on-chain options) written in two parallel groups, each with its method→function mapping in the header; `smoke.js` reports `all 11 adapter(s) conform`. Findings the adapters produced, acted on: (a) a **sixth latent contract defect** — `CVINVehicleCredential1155.issuerTransferCredential` with `from == to` deleted the VIN mapping; guarded with a revert and covered by `selfTransfer.regression.test.js` (Hardhat suite 219 → 220); (b) two runner bugs of mine (a `capabilities` key demanded inside `capabilities()`; a 14-character VIN where contracts require 17) fixed; (c) manifest stances corrected in the generator: CVIN-Combined creates implicitly at 0 gas; ERC-4337 off-chain creation is not applicable in this harness (no factory, EntryPoint rejects initCode); `OPERATION_DELEGATECALL` no longer counts as key delegation; `nonce` no longer counts as signed execution (ERC-1056 vehicle profile has no `*Signed` entry points). Interface gaps reported by the adapters and left for S3 to resolve: `signedOp` has no target parameter and no op vocabulary; `revoke(id|claimId)` is underspecified for per-item revocation; Hardhat signers cannot sign raw digests (adapters derive keys from the test mnemonic). Gas per method per option is now printed by the smoke run — the first cross-option table produced by the sandbox.
- **Implementation step S6 done** (remaining half): the twelve lifecycle use cases run as pytest cases by invoking the script's own functions in-process (the script's `use_cases` list was hoisted to a module-level `USE_CASES`, CLI unchanged: still 12/12); a V2V harness smoke runs `--simulate` with 10 vehicles for 2 s against a temp results path (a `--results` flag was added to the harness because its default path is `__file__`-relative, so a temp cwd alone would not have protected the committed JSON) in 0.8 s and asserts structure, not numbers. Python side: **81 passed** (68 + 12 + 1), re-run here; the committed `v2v_latency.json` is byte-identical. L4 now has automated tests for the first time.
- **S9 (part)**: a `python-layers` CI job runs `sandbox/py-suites/run.sh` in the compliance workflow; green on GitHub for `97ecbd3` (W3C SSI Compliance run 37180347706). The L1 job follows S3.

- **D-B** keep both ERC-1056 variants as named sub-options (default). **D-C** archive the research copies (default). **D-D** asymmetry discussion as a chapter-6 section (default). All reversible on the author's word.

## 4. Closing of the design step

**Done.** The four documents the author asked for, in the order asked: the clean review,
the clean plan, this report (opened first, closed now), and the meta-commentary — plus
the generated feature-asymmetry matrix that grounds all of them in code.

**Not done, by design.** No sandbox code was written. The author asked for step-by-step
execution after the plan; implementation starts with S0 (name the ERC-1056 fork, pin
the MOBI copies in CI) and S1 (twelve manifests) on the author's word, and each step
will append an entry here with its acceptance check.

**Needed from the author (plan §3).** (1) keep both ERC-1056 variants as named
sub-options — recommended — or unify; (2) archive the research copies under
`_research-copies/` — recommended — or leave; (3) where the asymmetry discussion lives.
Everything else in S0–S9 is executable without input.

## 3. Decisions
- **D-A** — the matrix is *generated* from the contracts' interfaces, then annotated by
  hand only in a separate "interpretation" column, so "every relevant feature" is
  grounded in code rather than in memory of the standards.

## 4. Closing (written at the end of the design step)
