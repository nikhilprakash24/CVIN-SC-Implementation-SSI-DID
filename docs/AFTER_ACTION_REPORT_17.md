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
- **B1.1, the sources.** Across the last ten committed L1 reports, exactly three cells drifted: CVIN-Combined
  claim (316,439 / 316,451 / 316,477) and revoke (70,864 / 70,873 / 70,883), and ERC-725xy signed-op (76,340 / 76,352).
  - The causes are a random claim issuer wallet (`sandbox/options/cvin-combined/adapter.js:65`) and `Date.now()`
    used as a value in calldata (`sandbox/options/erc-725xy/adapter.js:184`).
  - The demos draw 54 `Wallet.createRandom` and 23 `randomBytes` calls, and `erc-735/adapter.js:98` makes a
    placeholder VIN from the clock.
  - I4 drew a random RSU key per run and never recorded it.
- **B1.2, seeding.** `sandbox/lib/determinism.js` is preloaded through `NODE_OPTIONS=--require` and active only
  when `CVIN_SEED` is set. It seeds `ethers.Wallet.createRandom` and `ethers.randomBytes`. The grand runner sets
  `CVIN_SEED=1` for its L1, Hardhat-tree and demo stages and records the seed in the report.
  - **First gate run.** All three seeded L1 runs failed in 0.0 s, and their "identical" comparison was therefore
    vacuous. The preload could not resolve `ethers` from `sandbox/lib`. It now resolves from the working directory.
  - **Second fault.** ethers v6 exposes `randomBytes` on two objects, and Hardhat copies from the second; both are
    patched now. Each fault was found by checking the gate's output, not just its exit code.
  - **Gate, L1.** Three seeded runs are identical in all 99 cells.
  - **Gate, demos.** Two seeded runs are identical in **1,749 of 1,752 steps**; 44 steps differ from the committed
    unseeded run. The 3 that still vary are MOBI `attestEvent` steps (36-gas spread). Their event id hashes
    `block.timestamp` inside `MOBIVIDRegistryV2.sol:271–277`, and block time comes from the node's clock, which no
    input seed controls.
  - **Departure from §1's gate**, which asked for every step: these 3 are **declared** time-dependent and reported
    as a range. Fixing them would mean controlling the node's clock or changing a Phase 1 contract, and neither
    belongs in B1.
  - No producer of record and nothing in `1_blockchain-identity/benchmarks/` changed. The metrics harness keeps its
    own dataset seed.
- **B1.3, I4.** `infrastructure_gas.js` derives the RSU keys from declared seeds (`I4_SEEDS`, default 1) and records
  each run's seed, address and public keys.
  - **Runs of record:** in a clean worktree at `a950cdf`, seed 1 twice and seeds 1–30 twice. Both repeats are
    byte-identical (`dirty` false).
  - **Seed 1:** 0 / 52,606 / 34,050 / 51,754 / 35,510 / 35,062, each equal to the old 30-run mode.
  - **Range over seeds 1–30:** key anchor 52,582–52,606; revoke 35,038–35,062. The other cells are as before. The
    old unseeded range (52,558–52,606; 35,014–35,062) came from a different, unrecorded key sample.
  - **Re-stated:** #47 (with history), the README, chapter 5 and the presentation, plus stale entries for the old
    ranges. The dashboard reader was fixed for the seeded summary format, in which a seed list replaces the run count.
- **B1.4, the rule.** Guide rule 1.1.10 and register §1 were amended. Random inputs are declared. Incidental inputs
  are seeded, with the seed recorded. Inputs that are the thing measured are reported as a range over declared seeds,
  with the inputs recorded. Time derived inside a contract cannot be seeded by input; such steps are declared.
- **Grand run (last), the first with seeded stages.** ALL OK: smoke 11 adapters, L1 99, Hardhat 537, Python layers 331,
  92 demos / 1,752 steps (594 mined transactions). The report records `CVIN_SEED=1`. The documents generated from the
  run were regenerated, including the F3 mode classification.

## 3. Closing
**B1 is done; N-18 is closed.** CI 8 of 8 green on `8855a4d`.
- **Seeded:** incidental randomness in the L1 suite and the demos. The L1 suite is now identical in 99 of 99 cells
  across seeded runs, and the demos in 1,749 of 1,752 steps.
- **Declared:** the three remaining steps, which depend on block time inside a Phase 1 contract.
- **I4:** a range over declared seeds that a second run reproduces exactly, with every run's keys recorded. The
  pre-registered expectation of byte-identical runs (A4) now holds per seed.
- **The rule:** written into guide 1.1.10.

**Two faults of this pass,** both caught by inspecting the gate's output:
- a preload that silently failed to load;
- a generator patched on only one of the two objects ethers exposes.

**Next:** WM-2 B2, the gas charter. It sets exact or range for every gas row, and root-causes the 14
non-deterministic harness cells.

