# Measurement Conditions — the single source of truth for reported numbers

**Rule (audit F3):** a number may appear in a thesis chapter only if it was produced by
`1_blockchain-identity$ npm run metrics` under the conditions below, and the chapter
cites the run id printed in `results/metrics/latest/meta.json`. Numbers measured under
any other conditions carry their own conditions block and never share a table with these.

## A. Fixed conditions (on-chain harness)

| Parameter | Value | Recorded in |
|---|---|---|
| Network | Hardhat Network, in-process (no HTTP), `chainId 31337`, automine on (except throughput: queue → mine) | `meta.network` |
| EVM | `cancun` | `meta.evmVersion` |
| Compiler | solc `0.8.24`, optimizer on, `runs = 200`, `viaIR = true` | `meta.solc`, `meta.optimizerRuns`, `meta.viaIR` |
| Block gas limit | 30 000 000 | `meta.network.blockGasLimit` |
| Actors | HD wallets from the Hardhat default mnemonic, roles in `benchmarks/lib/actors.js`; one fresh funded wallet per created identity | code |
| Dataset | `benchmarks/lib/dataset.js`, seed 42, 1 000 VINs, string fields padded to fixed widths | `meta.conditions.datasetSeed` |
| Repetitions | tx ops: 1 exact + 5 warm-up + **N = 30** latency samples; reads: 5 warm-up + 30; scale reads: 2 + 10; throughput: 3 bursts × 200 tx | `meta.conditions` |
| Clock | `process.hrtime.bigint()`, latency = send → last receipt, in-process | code |
| Tracing | `debug_traceTransaction` (memory/stack/storage disabled) after the receipt; does not affect measured gas or latency | `meta.conditions.trace` |

## B. What each reported quantity means

| Quantity | Definition | Deterministic? |
|---|---|---|
| `gasUsed` | Σ `receipt.gasUsed` over the transactions a semantic op needs | yes, up to calldata zero-byte pricing of generated addresses (reported as mode; range in `gasUsedRange`) |
| `gasExecution` | `gasUsed − (21 000 + calldata gas [+ 32 000 + initcode words × 2 for CREATE])` | yes (checked: run fails the determinism flag otherwise) |
| `sstoreCount`, `sloadCount` | opcode counts from the trace | yes |
| `newSlotsEstimate` | `SSTORE` steps whose `gasCost ≥ 20 000` (zero → non-zero) | yes |
| `logBytes` | Σ (32 × topics + data length) over emitted logs | yes |
| `latencyMs` (tx) | wall-clock send → receipt on the in-process node; **client + EVM execution only, no propagation or consensus** | no → median / p95 / n |
| `latencyMs` (read) | wall-clock of the adapter's resolution code incl. all JSON-RPC round-trips in-process | no → median / p95 / n |
| `readRpcCalls`, `readBytes` | JSON-RPC calls made and JSON bytes returned while resolving | yes |
| `txPerSec` | 200 queued tx ÷ (queue time + mine time) on one node | no → median of 3 |
| `costUSD` | **derived**, `gasUsed × gasPrice × ETH/USD` with the parameters printed in `meta.derivedCostParams`; illustration only | n/a |

## C. Off-chain baselines (Python, `cv2x-testbed/`)

To be recorded when `benchmark_pki_vs_erc1056.py` lands: Python version, `cryptography`
version, CPU model, N per op, and whether the Hardhat node was in-process or over HTTP
(the ERC-1056 Python provider uses HTTP JSON-RPC, which adds a localhost round-trip that
the JS harness does not have — the two latency columns are therefore **not** directly
comparable and must be labelled).

## D. Superseded numbers

| Number | Where it appeared | Status |
|---|---|---|
| "50–100 ms identity resolution" | `docs/thesis/README.md` | superseded; not trunk-generated |
| "~0.8 ms resolution" | `RESEARCH_THRUSTS_REPORT.md` | superseded; conditions unknown |
| "~45–50K gas per ERC-1056 op" | early session logs, `HANDOFF-DATA-COLLECTION-FRAMEWORK.md` v1 | superseded; see `results/metrics/latest/tables/crud_gas.md` |
| 78 068 / 68 854 / 72 219 / 51 126 gas (2026-09-24 snapshot) | `docs/figures/results_snapshot.json` | valid for its own conditions (test-suite calls on the shared `vehicleOwner` account); the harness numbers use fresh accounts and the fixed dataset, so they differ by cold/warm slot effects — cite the harness numbers |
