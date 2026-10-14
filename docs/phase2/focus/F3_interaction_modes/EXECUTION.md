# F3 Execution — Classifying Phase 1's Chain Interactions by Mode (Start of Execution)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (after-action report 16) · **Plan step:** F3-S1

## What was built
| File | What it is |
|---|---|
| `classify_modes.py` | classifies the harness operation catalogue (writes and reads) and every demo step of the grand runner's log by the default taxonomy (A direct, B-submit, B-serve, C detached); checked in CI with `--check` |
| `MODE_CLASSIFICATION.md` | the generated tables |

## What it establishes
- **Writes.** Every harness write is Mode A except the relayed update (`U5`), which is B-submit for ERC-1056 and
  ERC-4337, the only two standards that have it. No Phase 1 write is Mode C.
- **Reads.** Every harness read is Mode A against the harness's own node; B-serve was never exercised.
- **Demo steps.** The 1,752 steps are classified by stated rules instead of the per-step flag that defect D61 showed
  to be inconsistent across options:

  | Class | Steps |
  |---|---:|
  | mined writes (A) | 594 |
  | view reads (A) | 393 |
  | expected reverts (A) | 369 |
  | off-chain work (C) | 160 |
  | unclassified, reported rather than hidden | 236 |

  The grand report's "off-chain" count of 700 is therefore mostly reads and expected reverts logged under one flag.

## Limits
The demo classification is rule-based and approximate, by its own statement. Plan step F3-S3 (steps that carry
their kind when logged) retires it. After every grand run, `classify_modes.py` is regenerated with the other
generated documents.
