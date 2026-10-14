# F3 Execution: Classifying Phase 1's Chain Interactions by Mode (Start of Execution)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (after-action report 16) · **Plan step:** F3-S1
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-32, AR-34, AR-35

**In the thesis, this classification is cut to paper P4** (review §4.1); D61 stays a sandbox defect.

## What was built
| File | What it is |
|---|---|
| `classify_modes.py` | classifies the harness operation catalogue (writes and reads) and every demo step of the grand runner's log by Phase 2's A/B/C frame; checked in CI with `--check` |
| `MODE_CLASSIFICATION.md` | the generated tables |

## What it establishes
- **Writes.** Every harness write is Mode A except the relayed update (`U5`), which is B-submit for ERC-1056 and
  ERC-4337, the only two standards that have it.
  Detachment is a timing attribute, not a mode (`ANALYSIS.md` §3): ERC-1056 signed operations are detached writes with no deadline, but the harness submits each one at once.
- **Reads.** Every harness read is Mode A against the harness's own node; B-serve was never exercised.
- **Demo steps.** The 1,752 steps of the grand report are classified by stated rules instead of the per-step flag
  that defect D61 showed to be inconsistent across options.
  The rule classes are mined write, view read, expected revert, local computation (no chain contact), and unclassified, which is reported rather than hidden.
  For what the grand report's 700 "off-chain" steps are, see the cross-tabulation in `MODE_CLASSIFICATION.md` §3.
  No statement about their make-up is made here without it.

## Limits
The demo classification is rule-based and approximate, by its own statement. Plan step F3-S3 (steps that carry
their kind when logged) retires it. After every grand run, `classify_modes.py` is regenerated with the other
generated documents.
