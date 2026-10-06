# Plan — Merging the Sandbox and Review-2 Lineages into One Trunk

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Input:** `docs/REVIEW_03_PARALLEL_LINEAGES.md` and `docs/reconciliation/RECON_{DOCS,CODE,TSR}.md`
**Where the merge happens:** on this branch (`claude/cv2x-testbed-setup-…`), merging
`origin/claude/clone-cvin-id-scs-…` @ `fa6188e`; the TSR commit `ef2c851` is brought in the same
way afterwards. The other branch is never pushed to. The author decides later which branch is
the default; the merged history is the same either way.

## 0. Rules
- Nothing is resolved by choosing a number: every result of record is re-executed once on the
  merged contracts, on one host, and the register says so.
- Every conflict resolution that is a design choice is recorded as a decision (M-A…) with the
  default taken and the author's right to overturn it; the two reconciliation reports already
  recommend a default for each.
- The merge commit compiles and passes both test bodies before it is pushed; re-executions and
  text follow in separate commits so that each is reviewable.
- Nothing from either lineage is deleted except by an explicit decision (research copies).

## 1. Decisions needed (defaults in bold; the author may overturn any)

| ID | Question | Default |
|---|---|---|
| M-A | CVIN-Combined claim ops: K-6 (no `changed` advance) vs D22 (`DIDClaimChanged` + advance) | **K-6 semantics; keep emitting `DIDClaimChanged` without advancing `changed`** |
| M-B | `DIDRevoked` two-arg (theirs, K-5 caveat) vs three-arg with `previousChange` (ours, D21) | **three-arg** |
| M-C | `setVehicleAttributes(address did, …)` (K-1) vs unchanged signature (D18) | **K-1**, our constant kept as an alias |
| M-D | Research copies deleted (K-16) vs archived (`_research-copies/`) | **archived** |
| M-E | Test layout flat vs layered L1/L2 | **layered**; their new tests re-homed; their npm globs fixed |
| M-F | Resolver + checker pair | **theirs** (decimal CAIP-10 closes D27; corrected 7.1.2 check); one floor set from the measured score |
| M-G | Experiment scripts of record for freshness-k and lifecycle parity | **theirs** (clean tree, T-9, pre-registered); our `attest_event` row ported; our 2026-10-03 results archived |
| M-H | Register numbering | **theirs #1–#39 kept; ours appended #40–#43**; SC-14 kept, their proposals SC-15…SC-21 |
| M-I | Same-named after-action reports | **suffix by lineage**: `_03_review2.md` etc. under `docs/review02/`; ours keep their names |
| M-J | Which handback is the entry point after the merge | **a new `HANDBACK_2026-10-06.md`** superseding both |
| M-K | The Inkwell / `npat-planning` branch | **not merged**; recommend its own repository; recorded |
| M-L | Compliance floor | **set to the merged measured score's floor (94.0 if 94.3 is measured)** |

## 2. Steps and gates

| # | Step | Gate (must pass before the next step) |
|---|---|---|
| S0 | Freeze: local tags `pre-merge/sandbox` = `b70081c`, `pre-merge/review2` = `fa6188e`; record the 61 both-changed paths in the report | tags exist; report §2 lists the paths |
| S1 | `git merge --no-commit origin/clone-cvin-id-scs`; resolve the 18 document conflicts: rename their AAR 03/04/05 (M-I), keep our `MOBI_VID_CHECKLIST.md` as `…_2026-10-03_preview.md` and take theirs, union `INDEX.md`, rebuild `SCOPE_CHANGES.md`, merge `LATENCY_BUDGET.md` paragraphs, keep both conformance histories as dated sections, register per M-H | every document opens; no `<<<<<<<` markers; `INDEX.md` lists every file |
| S2 | Resolve the 10 contract conflicts per §1 (M-A…M-D) and mirror the three MOBI copies byte-identically; compile both Hardhat projects; rebuild `cv2x-testbed/artifacts` and `ERC1056Registry_{abi,bytecode}` | `npx hardhat compile` in both; `cmp` of the three MOBI copies; their `check_artifacts_fresh.js` |
| S3 | Tests: re-home their new test files (M-E); fix their `package.json` globs and `security_scenarios.js` require path; update our six K-1 call sites and the two K-3 expectations; add `authorizeIssuer` setup to their ERC-735 tests; delete our five D22 assertions per M-A; align the one ERC-1155 revert string | `npx hardhat test` all passing, 0 failing (target ≥ 386 + their new files); L1 99/99; smoke; grand runner stages smoke/L1/L1+L2 |
| S4 | Python/SSI layer: take theirs as base; port D11b (`anchorVehicleKey`, artifact ABI, on-chain fallback) and the three-arg walk; checker per M-F | their full Python suite (no skips) + `sandbox/py-suites/run.sh`; checker score read; floor set (M-L) |
| S5 | Experiments and results of record, one host, back to back: nine-standard gas (+30-run determinism), scaling A/B, MOBI sweep, security scenarios (`attack_results.json`, matrix), #1/#2, M3 pin, #21/#22/#23, #32 full + #37 probe, #33 (two-tx birth), metrics harness run and analysis, HTTP condition | every producer re-run on the merged head; each register row that describes code re-stamped V with date and commit; delta files for the cells moved |
| S6 | Sandbox regeneration: manifests, feature matrix, demos (their K-1/K-3/K-6 change steps in `erc-1056-uport`, `mobi-vid`, `cvin-combined`), grand runner `all` | ALL OK; coverage 100 % per option kept |
| S7 | External DID suite on the merged resolver, fixtures and registry-minted DID; regenerate `docs/conformance/implementations*` | ≥ 335/336 both; write-up section added |
| S8 | CI union (`benchmark.yml` theirs, `test-contracts.yml` ours, `w3c-compliance.yml` both jobs; one floor); push | all workflows green on the merged head |
| S9 | Text once from the merged state: `README.md`, chapter 5 regenerated by the generators, chapters 1/6/7 and `CAPABILITIES.md`/`SIDE_PAPERS.md`/`COMPOSITION.md`/`INVENTORY.md`/`QUICKSTART.md` stale-figure lists, defect log (D12 half-closed by K-8, D16-rest by K-3, D27 by S-10; new findings from their review mapped), `HANDBACK_2026-10-06.md` with the union of author decisions (their 15 + our open items + M-A…M-L) | no document quotes a pre-merge number without its register row; handback lists every pending decision |
| S10 | Bring in `ef2c851` (TSR plan) and adopt its documentation half per `RECON_TSR.md` §5: `docs/testing/` registers fed from the sandbox manifests and L1/demo JSON, TC tags on the L1 files, stamping of producers, `check_docs_numbers.py` | TSR mapping table in `docs/testing/README.md`; register builder runs in CI |

## 3. What is re-executed, and why (decision D-E restated)
Every numeric claim that describes code is re-measured on the merged contracts because both
lineages changed the same contracts in different ways; neither lineage's numbers describe the
merged code. The old values are kept as superseded rows, never overwritten in place.

## 4. Order of work and checkpoints
S0–S3 form one merge commit (the tree must compile and pass before it is pushed). S4 is a second
commit. S5 is one commit per producer (gas, scaling, sweep, security, experiments, harness). S6–S8
one commit each. S9 and S10 one commit each. After-action report 07 is updated at every step and
closed after S10; a handback is written even if the pass stops early.
