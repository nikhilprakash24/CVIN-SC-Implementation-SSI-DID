# Testing Suite Replan — Phases 3 and 6 against the trunk as it stands (2026-10-22)

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-22 on `claude/testing-suite-organization-z5j7dc`.
**Supersedes:** the phase order of `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` §8 for Phases 3 and 6 only; the
taxonomy (§3), identifiers (§4) and rigour protocol (§9) stand. **Binds:** the trunk's `docs/STYLE_AND_RIGOUR_GUIDE.md`,
`docs/PLAN_WM-2.md` and `docs/STATUS_2026-10-22.md` (trunk = `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` at
`87334d6`, named the trunk by the latest handback and status note).

## 0. The answer first

Most of what this branch planned on 2026-10-04 and executed on 2026-10-15 has since been done on the trunk, in the
trunk's own names. This branch's Phase 0/1 outputs (`a01b5de`, `6548a88`) are **superseded** and are not to be merged
as they are. What remains for Phases 3 and 6 is narrower than the plan said:

1. **Phase 3, tagging:** put the four test bodies that the trunk's register does not yet cover into it, with the
   trunk's derived-identifier method (no test title edited). This is WM-2 step **A7** (Python suites) plus the
   per-option contract tests and the harness/stats tests, which no WM-2 step names.
2. **Phase 6, charters:** the gas charter exists (WM-2 B2) and the latency charter is WM-2 **B3**. The other eight
   charters (F, N, A, W, S, D, I, Q) are scheduled nowhere. This pass drafts all nine missing ones as documents; it
   relabels no register row (that is B3's gate and waits on A6).

Neither item changes a result of record, a contract, a test body or a register row, so neither collides with the
pending cross-model check (status note §4) or with WM-2 A3–A7's order.

## 1. What changed since this branch's plan (read, not assumed)

| Plan item (TSR v1.0) | State on the trunk today | Source |
|---|---|---|
| Test locations "tag, do not relocate" | tests re-homed into `test/L1-identity-mechanisms`, `test/L2-identity-system/{per-option,security}` before the plan reached the trunk | `docs/reconciliation/RECON_TSR.md` §0 |
| Phase 1 registers and matrix | `docs/testing/build_register.py`: **305** TC entries derived from result JSON (L1 mechanisms 99 + 60 gas, strict security 54, demos 92); coverage matrix by capability family; `--check` in CI | `docs/testing/test_register.yaml` |
| Phase 0 baseline / run of record | harness re-run on the merged tree; run identity, per-producer stamps, promote step | WM-2 A1, A2, A4, A6 (clone line); `tools/run_identity/` |
| Phase 5 stamps, promote, inventory | 161→209 tracked result files, 0 uncovered | `docs/testing/STAMP_INVENTORY.md` |
| P4-3 / class-G charter | done, generated, CI-checked: seven gas classes, varying cells root-caused | `docs/testing/GAS_CHARTER.md` (WM-2 B2) |
| `check_docs_numbers.py` | exists, in CI | `docs/testing/` |
| Class-L charter | scheduled | WM-2 B3, after A6 |
| `claims.yaml` | scheduled | WM-2 A5 |
| Python suites in the register | scheduled | WM-2 A7 (N-15, audit P-F8) |
| Per-option contract tests, harness/stats tests in the register | **not scheduled** | gap |
| Charters F, N, A, W, S, D, I, Q | **not scheduled** | gap |
| Paper intake, second-pass sheet | still open; the sheet is the author's | this branch |

Counts on the trunk (last grand run, `sandbox/grand/report/GRAND_REPORT.md`, commit `72a29de`): Hardhat 541, Python
layers 342, 99 mechanism cells, 92 demos. The clone line, after PR #3, reports Hardhat 559; the two trunks have
diverged (cv2x 46 commits not on the clone line, clone line 70 not on cv2x) and reconciling them is the trunk
sessions' work, not this pass's.

## 2. Decisions taken here (defaults; the author may overturn each)

| ID | Decision | Default taken | Alternative |
|---|---|---|---|
| R-1 | Base for this work | the cv2x trunk at `87334d6` | the clone line at `bc4618f` |
| R-2 | Tags in titles or derived | **derived** identifiers, no title edited (the trunk builder's stated principle) | title tags (`[TC-…]`), which the trunk README §2 also mentions; touches ≈ 600 test files |
| R-3 | Identifier for an untagged test | `TC-<slug>-<op>-<cls>-<hash8>`, hash of `path::describe::title`; stable while the title is | sequence numbers (unstable under insertion) |
| R-4 | Op and class for a test without a structured record | rule file, reviewed; the rule that fired is recorded per entry | hand mapping |
| R-5 | This branch's Phase 0/1 files | kept as history only (§5); not merged over the trunk's | merge and reconcile line by line |
| R-6 | Charter scope this pass | drafts for all nine classes not yet chartered; L drafted for B3 to adopt | wait for B3 |

## 3. Phase 3 (tagging), replanned

**Goal.** Every test the trunk runs has exactly one register entry or more, so the coverage question can be asked
of the whole suite and not only of the mechanism layer.

| Step | Body | Method | Gate |
|---|---|---|---|
| T1 | `test/L2-identity-system/per-option/**` (291 `it`) | parse `describe`/`it` titles; slug from the folder via the builder's `STD_TO_SLUG`; op and class by rule | every `it` has an entry; 0 unmapped slug |
| T2 | `test/benchmarks/**` (15 `it`) | same; subject `pipeline` or the adapter | as T1 |
| T3 | Python: `2_w3c-ssi-layer`, `cv2x-testbed/tests`, `sandbox/py-suites` (333 `def test_`) | `pytest --collect-only -q` node ids when collectable, else static parse; subject from path | entries = collected items; parametrised items counted |
| T4 | the builder | one new source block in `docs/testing/build_register.py`, layer `L2u` (unit) and `py`; existing 305 entries untouched; `--check` still exits 0 | regenerated register differs only by added entries |
| T5 | guard (rule 1.3.11) | `--check-complete`: fails if a test exists with no entry; shown to fire by adding a dummy test in a scratch copy | probe fails on the broken copy |

Not in this pass: title tags (R-2), the harness `crud.json` cells as TCs (they are results, already counted as +M in
the matrix), and any CI wiring change while the check runs.

## 4. Phase 6 (charters), replanned

One page each, in `docs/testing/charters/`, using the template of TSR §9.2 (what it establishes, oracle, design,
falsifiers, threats, reporting, replication, limits). Every number quoted carries its register row; where no row
exists, the charter says "no row" and quotes no number.

| Charter | Class | Draws on | Status after this pass |
|---|---|---|---|
| F | functional | per-option tests, L1 mechanisms, demos | draft |
| N | negative / revert | exact-revert rule (review 02), per-option negatives | draft |
| A | adversarial | strict security harness, `THREAT_MODEL.md`, defect log | draft |
| W | conformance | W3C checker, external DID suite (both denominators), adapter conformance, MOBI checklist | draft |
| G | gas | — | **exists** (`GAS_CHARTER.md`); linked, not rewritten |
| L | latency | guide 1.1.7, register conditions, freshness and V2V rows | draft, offered to WM-2 B3 |
| S | scale | scaling experiments, harness scale scenario | draft |
| D | determinism | B1 seeding, stamps, promote, determinism gates | draft |
| I | integration | use cases, lifecycle parity, demos | draft |
| Q | analysis | analysis layer, rubric, dominance (and the H5 criteria change) | draft |

Gate: every charter names its oracle and at least one falsifier with the test or result that would show it; a
reviewer script checks that every `#nn` cited exists in the register.

## 5. This branch's earlier outputs

`a01b5de` and `6548a88` (2026-10-15) ran Phase 0/1 on the pre-merge layout. Their findings were real on that tree
(run of record re-stamped on HEAD; 0 of 192 × 11 exact cells moved; 14 iteration-varying cells) and the trunk reached
the same results independently (WM-2 A6, B2: 27 varying cells once calldata variation is counted). The files collide
with the trunk's (`docs/testing/README.md`, an after-action report 06, the metrics `latest/`). Default R-5: when this
branch is next brought up to the trunk, the trunk's versions win and these move to
`docs/testing/history/TSR_BRANCH_2026-10-15/`.

## 6. How the work lands

A merge of the trunk into this branch was refused by the session's permission policy (shared-resource change), and
WM-2's order holds results-of-record work until the check reports. So this pass:

1. commits this replan to this branch;
2. builds T1–T5 and the charters in a local, detached checkout of the trunk, and runs their gates there;
3. commits them on this branch as a reviewable patch series under `docs/planning/testing_suite/staged/`, with the
   gate output, so nothing is lost if the container is reclaimed.

Applying the series to the trunk, or merging the trunk into this branch first, is the author's call (§7).

## 7. What needs the author

| Item | Form of the answer |
|---|---|
| Allow this branch to take the trunk (merge), or land the staged series on the trunk in a trunk session | "merge here" or "apply on trunk after the check" |
| R-1 to R-6 | ids and a word each, or silence (defaults stand) |
| The second-pass sheet | unchanged; still the input to paper intake |
