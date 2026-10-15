# After-Action Report 18 — WM-2 B2 (Gas Charter) and Result Cards

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-15, after report 17 closed at `04dcdcc` (CI 8/8 green on `8855a4d`); closed at the end of this pass
**Brief (the author, 2026-10-15):** accept defaults and continue to the next executable; add another form of
results in which the results become content blocks or cards, in the style of the results dashboard.

## 1. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| B2 | WM-2 step B2: a class-G gas charter, generated. Every gas figure in one class (exact, seeded, first-call, mode, range, derived, history); the metrics harness's varying cells root-caused from the raw rows of run of record `7a9a996`; every V register row that reports gas classified | orchestrator; measurement methodologist | `gas_charter.py --check` in CI; it fails when a V gas row has no class (shown to fire) |
| RC | Result cards: one card per V register row (headline value, claim, conditions, status, source), generated from the register and the dashboard snapshot, with a `--check` in CI; published as a private page beside the dashboard | orchestrator; visualisation engineer | the generator reads only committed files; `--check` fails on a stale page; every card's value appears in its register row |
| R | Records (register note, plan, handback addendum, session manifest), grand run last, CI | orchestrator | CI green on the closing commit |

The harness code stays frozen until A6 (N-19). No new measurement is made in this pass.

## 2. Execution log
- 2026-10-15 — report opened.
- **B2, gas charter.** `docs/testing/gas_charter.py` writes `docs/testing/GAS_CHARTER.md` from the raw rows of run of
  record `7a9a996` and from the register. Findings:
  - **27 of 110** crud tx cells vary in total gas across their 36 iterations, not 14. The harness's `gasDeterministic`
    flag covers execution gas only and marks 14; the other 13 vary in calldata only.
  - Causes: calldata zero bytes 24 cells; execution path (8 or 16 EVM steps) 6; value-dependent cost (2–5 gas) 4;
    first-call state 4 (erc721 C1 and U1 and lsp8 U1 at 2,800 gas; lsp8 C1 at 17,100 gas, one more new slot).
  - **A correction to my own first draft.** It called the inputs random and the fix seeding. The harness has no random
    input: keys and credential hashes are keccak-derived with zero bytes skipped, and signing is deterministic. Cells
    reproduce run to run; they vary from iteration to iteration because each iteration uses a new key, and the values
    derived from it are not filtered for zero bytes. The class is G-mode (reproducible mode, range beside it), and the
    fix at A6 is to extend the zero-byte rule, not to seed.
  - The plan's guess "address-dependent storage" is not borne out: only lsp8 C1 changes its storage writes, and that
    is first-call state (checked over `sstoreCount` and `zeroToNonzeroSstores` of every varying cell).
  - The two execution mechanisms are not traced to an opcode; the charter says so.
  - 20 V register rows that report gas are classified. The check fails when a V gas row has no class, or a class
    names a missing row; both shown to fire by deleting #29 and adding #999 in a test import.
  - Register §5.A gained a "Gas class" row; the CI document step runs `gas_charter.py --check`; plan B2 marked done.
