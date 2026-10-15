# Baseline — TSR Plan Phase 0 (2026-10-15)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Tree:** `ef2c851` (plan commit on top of trunk `fa6188e`), clean before the runs
**Purpose:** the frozen reference every later phase is diffed against (plan §8, Phase 0). Everything here was executed in this pass; nothing is copied from a session log.

## 1. Environment

| Item | Value |
|---|---|
| Host | Linux 6.18 x86_64, 4 vCPU, 15 GB (cloud container; **a different host from the 2026-10-04 runs**, so latency figures are not comparable, gas is) |
| Node / npm | v22.22.0 / 10.9.4 |
| Hardhat / ethers / solc | 2.28.6 / 6.17.0 / 0.8.24 (47 Solidity files compile, evm target cancun) |
| Python | 3.11.15 |
| web3 / eth_account / coincurve / cryptography / numpy | 8.0.0 / 0.14.0 / 21.0.0 / 49.0.0 / 2.4.6 (installed unpinned, as CI does; pinning is Phase 3) |
| Install | `npm ci` (lockfile), `pip install eth-account coincurve cryptography web3 pytest numpy` |

## 2. Suites (tier `full`)

| Suite | Command | Result | Wall time | Matches handback 2026-10-04? |
|---|---|---|---|---|
| Hardhat | `npx hardhat test` | **369 passing, 23 pending** (23 = declared n/a adapter ops) | 13.7 s | yes |
| Python, all suites, node on 8548, MOBI artifacts | `pytest 2_w3c-ssi-layer cv2x-testbed/tests -q -rs` | **358 passed, 0 skipped**, 54 warnings (cryptography naïve-datetime deprecation in `centralized_provider.py:344`) | 11.4 s | yes |
| Use cases | `python3 cv2x-testbed/scripts/test_use_cases.py` | **12/12** | — | yes |
| W3C checker | `python3 cv2x-testbed/scripts/w3c_compliance_checker.py` | **94.3 %** (41 PASS, 1 PARTIAL, 2 FAIL of 44) | — | yes |

Side effects observed: `npx hardhat test` rewrote `4_comparison-framework/security-analysis/results/attack_results.*` with **identical content** (git clean afterwards). `benchmark_gas.js` changed only the `date` field (restored with `git checkout`). The checker wrote `w3c_compliance_report.json` into the working directory it was run from.

## 3. Producers (tier `measure`)

| Producer | Result | Gate |
|---|---|---|
| `scripts/benchmark_gas.js` → `gas_benchmark.json` | **0 of 55 cells changed** against the committed results of record | cell-by-cell diff (same check as CI) |
| `npm run metrics` (harness, all six scenarios, ten adapters, N = 30) | see §4 | compared cell by cell against the previous `latest` (`2026-10-04T09-50-29Z_0eef6af`) |
| `npm run metrics:analyze` | see §4 | — |

Not re-run in Phase 0 (no code change touches them; they stay at their 2026-10-04 state): V2V N = 30 seeds (`run_v2v_stats.py`, ≈ 30 × 20 s), scaling A–D, MOBI backend sweep, freshness-k, lifecycle parity, pseudonym pool, security lens 2, external W3C suite. Each is listed in `results_register.csv` with its stamp status; Phase 5 brings them under `run_all.sh --tier measure`.

## 4. Harness run of record on HEAD

Run **`2026-10-15T05-03-01Z_ef2c851`**, promoted to `results/metrics/latest` (previous: `2026-10-04T09-50-29Z_0eef6af`).

| Check | Result |
|---|---|
| `meta.measured.contractsTree` vs `HEAD:1_blockchain-identity/contracts` | `04c33c2` = `04c33c2` ✓ (closes plan §6.4 item 1) |
| `dirty` / `dirtyMeasured` | `true` / **`false`** — the working tree held this pass's uncommitted docs and tools; none of the four measured paths differed, which is the §5.F condition |
| Hardfork executed / block gas | osaka / 60 M (as §5.A) |
| crud: 192 (adapter, op) cells × 11 exact fields (gasUsed, intrinsic, execution, calldata, logs, SSTORE/SLOAD, zero→nonzero, txCount, supported) vs previous run | **0 differences** — run-to-run byte-identity of exact metrics confirmed on a different host |
| lifecycle: lifetime totals per adapter | unchanged |
| exact tables (`crud_gas`, `crud_storage`, `crud_calldata`, `crud_txcount`, `lifecycle_*`, `scale`, `batch`) | content identical; only the run-id footer changed; the `.csv` versions are byte-identical |
| `gasDeterministic:false` cells | still 14, same cells (iteration-to-iteration ranges; plan §6.4 item 2, Phase 4 packet P4-3) |
| latency tables (`*_latency*`, `resolve`, `throughput`) | moved, as expected on a different host; e.g. R3 median ms after lifecycle: ERC-1056 20.31 → 16.71, ERC-1155 2.63 → 2.57 |
| `npm run metrics:analyze` | A1 ratios, A2 capabilities, A5 rubric exact inputs unchanged; A3/A4 **frontier (all six criteria) unchanged**: erc1056, erc1056w, erc721, erc1155, erc725xy, erc4337 — CVIN-Combined still dominated (register #36 holds on this host) |

Register consequence: rows #29–#31, #34–#36 keep status **V** with the run id updated to `2026-10-15T05-03-01Z_ef2c851`; the latency figures in #31 (ms) are host-specific and now have a second-host observation (E7 candidate once the plan's replication protocol exists). #39 (HTTP condition) was **not** re-run.

## 5. Quarantine (W0-B)

Moved to `4_comparison-framework/results/superseded/2026-10-15/` with a README naming the superseding file and every document that still cites them: `sensitivity.{json,csv,tex}` (July, `paris`, no generator) and `w3c_compliance.json` (July, 93.18 %). The checker output of this pass replaces the latter at the same path (94.3 %; no stamp yet). `docs/figures/results_snapshot.json` stays (figure input; register §1 wording listed for Phase 7).

## 6. Output hashes (sha256, first 16 hex)

| File | Hash |
|---|---|
| `4_comparison-framework/results/gas_benchmark.json` (restored, committed) | `4ec80356cf86d829` |
| checker report (this run) | `3e1a3669ca31506e` |
| `results/metrics/latest/crud.json` before re-run (0eef6af run) | `bcd6e33326748f95` |
| `results/metrics/latest/crud.json` after re-run | `fb9e48e8bdd85b06` |

## 7. Exit criteria (plan §8 Phase 0)

- [x] all suites green, no skips
- [x] `meta.measured.contractsTree == HEAD:1_blockchain-identity/contracts` — `04c33c2` = `04c33c2`
- [x] baseline hashes recorded
- [x] register rows whose numbers moved: none; #29–#31, #34–#36 re-stamped on the new run id (same values); latency-only rows get a second-host observation
