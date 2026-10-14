# Phase 2 Focus Figures — data tables

**Generated** by `docs/phase2/focus/make_focus_figures.py` from committed run-of-record data; do not edit. Each table is the data behind one figure in `figures/` (the table view). **Author:** Nikhil Prakash (MASc, UBC ECE).

## F1-1 State written and lifetime gas (`figures/f1_state_vs_gas.svg`)
Register #35 (lifecycle gas), #49 (zero→nonzero SSTOREs, log bytes); harness run 2026-10-09T02-09-36Z_7a9a996 (M1-H).

| Standard | new storage slots | log bytes | lifetime gas |
|---|---:|---:|---:|
| ERC-1056 (wrapper) | 9 | 6,592 | 1,025,469 |
| ERC-1056 | 8 | 6,464 | 1,050,809 |
| ERC-1155 | 21 | 6,944 | 1,261,575 (excl. 2 n/a) |
| LSP8 | 42 | 8,288 | 1,508,413 (excl. 3 n/a) |
| ERC-4337 | 37 | 3,968 | 2,221,290 |
| CVIN-Combined | 81 | 7,648 | 2,559,537 |
| ERC-721 | 92 | 4,288 | 2,706,685 |
| ERC-725xy | 38 | 3,744 | 2,956,507 (excl. 2 n/a) |
| ERC-725 | 83 | 3,072 | 3,155,103 |
| ERC-735 | 149 | 12,960 | 5,797,549 (excl. 3 n/a) |

## F1-2 Read cost against history (`figures/f1_read_cost_vs_history.svg`)
Register #31.

| Standard | h=1 RPC / bytes | h=10 RPC / bytes | h=50 RPC / bytes |
|---|---:|---:|---:|
| ERC-1056 | 14 / 10,005 | 32 / 24,153 | 112 / 87,033 |
| ERC-735 | 3 / 13,774 | 3 / 44,398 | 3 / 180,558 |
| ERC-1155 | 3 / 908 | 3 / 908 | 3 / 908 |

## F2-1 Lifecycle operations, centralized vs on chain (`figures/f2_lifecycle_parity.svg`)
Register #33 (committed second run; D60).

| Operation | centralized (ms) | MOBI-VID-V2 on chain (ms) |
|---|---:|---:|
| birth | 0.0036 | 17.689 |
| lifecycle event | 0.0089 | 14.6285 |
| ownership transfer | 0.0023 | 13.9471 |
| history query | 0.2627 | 114.222 |

## F3-1 Direct and relayed writes (`figures/f3_write_paths.svg`)
Register #50, #34.

| Standard | path | gas |
|---|---|---:|
| ERC-1056 | direct (U3) | 35,024 |
| ERC-1056 | relayed signed (U5) | 62,646 |
| ERC-4337 | direct (U3) | 94,651 |
| ERC-4337 | UserOperation via EntryPoint (U5) | 141,767 |

## F3-2 Read modes (`figures/f3_read_modes.svg`)
Register #27 (offline), #37 (probe), #21 (full resolution); #21 and #37 predate the D51 fix and its added RPC (re-run due, A3b).

| Mode | median ms |
|---|---:|
| offline: cached credential, no chain contact (V2V warm, M0) | 0.1528 |
| probe: one eth_call to check the identity is unchanged | 2.758 |
| full resolution: key replayed from event logs, uncached | 9.654 |
