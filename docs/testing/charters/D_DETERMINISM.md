# Charter D — Determinism and run identity

**Status:** draft, 2026-10-22. **Binds:** guide 1.1.6, 1.1.10, 1.3.10, 1.3.11; `tools/run_identity/`.

## 1. What a passing check establishes
That a result was produced by the code it names, from a clean tree, and that re-running that code reproduces it:
byte-identical for exact metrics, within the stated distribution for statistical ones.

## 2. Oracle
- Gas determinism gate: every cell of the nine-standard table identical over 30 runs and against the committed file (#25).
- Seeded randomness: two runs with the same `CVIN_SEED` byte-identical (WM-2 B1).
- Run identity: the producer's stamp names its commit and per-producer scope; `dirty: false` on the producing code;
  the promote step refuses dirty runs, other commits, changed scopes and edited outputs (13 refusal tests).
- Stamp inventory: every tracked result file is covered (`check_stamps.py --check-coverage`).

## 3. Design
Producers write to `runs/` and reach a tracked path only through `promote.py`. Every guard has a probe that fails
on the broken version (`probe_run_identity.sh`, the builder's `--check-complete` probes).

## 4. Falsifiers it carries
| Claim | Refuting observation |
|---|---|
| "gas is exact" for a row | any cell differing between two runs at the same code, without a declared class (`GAS_CHARTER.md`) |
| "the run of record describes this code" | stamp scope hash differs from the current tree for a V row, without a "code changed since" note |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Internal | iteration-varying inputs (keys, signatures) mistaken for nondeterminism | gas classes G-mode, G-first-call |
| Internal | a guard that never trips | probes in CI (guide 1.3.11) |
| External | toolchain drift (Hardhat minor versions moved cells) | lockfile in the run identity |

## 6. Reporting
`STAMP_INVENTORY.md`; the "code changed since" column; delta files when results move.

## 7. Replication
Every CI run.

## 8. Limits
Latency is not byte-reproducible by nature; its reproducibility is the latency charter's replication rule (`../LATENCY_CHARTER.md`).
