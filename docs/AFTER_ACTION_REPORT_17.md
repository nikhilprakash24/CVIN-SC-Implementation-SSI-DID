# After-Action Report 17 — WM-2 Step B1 (Deterministic Gas, or Ranges by Rule)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-14, after report 16 closed at `1e96842` (CI 8/8 green on `6cb502f`); closed at the end of this pass
**Brief:** the author's "accept defaults and continue to the next executable". All open decisions keep their
defaults (P2-D7 to P2-D10, the scope reconciliation's D-1 to D-15 with D-12 withdrawn, N-23 open). The next
executable is `docs/PLAN_WM-2.md` **B1** (N-18; default W2-c: seed where the input is incidental, range where it is
the thing measured).

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| B1.1 | Find every random input behind the gas that varies between runs: three L1 cells across the last ten committed reports (CVIN-Combined claim and revoke, ERC-725xy signed-op), the demos' 45 drifting steps (audit T-F13), and I4 (#47) | each source named with its file and line |
| B1.2 | Incidental inputs (fixture keys, nonces, placeholder VINs) are seeded: a preload, `sandbox/lib/determinism.js`, seeds `ethers.Wallet.createRandom` and `ethers.randomBytes` when `CVIN_SEED` is set; `Date.now()` used as a gas-bearing value is replaced by a counter. The grand runner sets `CVIN_SEED=1` for the L1 and demo stages. No Phase 1 producer of record and nothing in `1_blockchain-identity/benchmarks/` changes | two consecutive L1 runs and two consecutive demo runs give identical gas in every cell and step |
| B1.3 | I4 (`infrastructure_gas.js`): the RSU keys come from a declared seed and are recorded in the result; the run of record is seed 1 (exact), and the range is reported over seeds 1–30 (the key-dependent cost is the thing measured, so a range, now reproducible) | two runs at seed 1 byte-identical in `operations`; the 30-seed range reproduced by a second run; #47 re-stated with history |
| B1.4 | The rule written into the register's conditions and the guide | rule text in `docs/MEASUREMENT_CONDITIONS.md` §1 and guide 1.1.10 |
| R | Records; grand run last; CI | CI green on the closing commit |

## 2. Execution log
- 2026-10-14 — report opened.
