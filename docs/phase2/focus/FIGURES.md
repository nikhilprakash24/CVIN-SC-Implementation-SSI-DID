# Phase 2 Focus Figures — data tables

**Generated** by `docs/phase2/focus/make_focus_figures.py` from committed run-of-record data; do not edit. Each table is the data behind one figure in `figures/` (the table view). **Author:** Nikhil Prakash (MASc, UBC ECE). Revised 2026-10-14 after the academic review (AR-15, AR-28, AR-37 to AR-40).

## F1-1 State written and lifetime gas (`figures/f1_state_vs_gas.svg`)
Register #35 (lifecycle gas), #49 (zero→nonzero SSTOREs, log bytes); harness run 2026-10-09T02-09-36Z_7a9a996 (M1-H). Zero→nonzero SSTOREs are opcodes, not net slots, and exclude per-identity contract code.

| Standard | zero→nonzero SSTOREs | log bytes | lifetime gas |
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
| ERC-735 | 149 | 12,960 | 5,797,561 (excl. 3 n/a) |

## F1-2 Read cost against history (`figures/f1_read_cost_vs_history.svg`)
Register #31 (ERC-1056), #51 (all columns).

| Standard | h=1 RPC / bytes | h=10 RPC / bytes | h=50 RPC / bytes |
|---|---:|---:|---:|
| ERC-1056 | 14 / 10,005 | 32 / 24,153 | 112 / 87,033 |
| ERC-735 | 3 / 13,774 | 3 / 44,398 | 3 / 180,558 |
| ERC-725xy | 2 / 2,312 | 2 / 5,192 | 2 / 17,992 |

## F2-1 Lifecycle operations, centralized vs on chain (`figures/f2_lifecycle_parity.svg`)
Register #33 (committed 2026-10-04 re-run; D60). Conditions: centralized registry: M0, in-process, a lower bound; MOBI-VID-V2: M1, local Hardhat node. history query cached vs the database's history query: 'equal once cached' band [0.5, 2] FAILED (ratio 0.041).

| Operation | centralized (ms) | MOBI-VID-V2 on chain (ms) |
|---|---:|---:|
| birth | 0.0041 | 33.0513 |
| lifecycle event | 0.0066 | 15.225 |
| ownership transfer | 0.003 | 14.0948 |
| history query | 0.1022 | 111.699 |
| history query cached | n/a | 0.0072 |
| history query cached validated | n/a | 15.4277 |

## F3-1 Direct and relayed writes (`figures/f3_write_paths.svg`)
Register #50, #34.

| Standard | path | gas |
|---|---|---:|
| ERC-1056 | direct (U3) | 35,024 |
| ERC-1056 | relayed signed (U5) | 62,646 |
| ERC-4337 | direct (U3) | 94,651 |
| ERC-4337 | UserOperation via EntryPoint (U5) | 141,767 |

## F3-2 Read costs by chain contact (table only; the figure was withdrawn)
three separately measured costs from different runs and hosts; not comparable as ratios (guide 1.1.7); the figure was withdrawn (AR-38).

| What is measured | median (ms) | unit | condition | host | register |
|---|---:|---|---|---|---|
| verify one V2V message, warm cached credential, no chain contact (SSI) | 0.1422 | per message | M0 | Xeon @ 2.10GHz, kernel fc | #27 |
| one probe refresh: an eth_call to check the identity is unchanged | 3.222 | per refresh, not per message | M1 | Xeon @ 2.10GHz, kernel fc | #37 (predates the D51 fix) |
| verify one message with an uncached ERC-1056 resolution (key replayed from event logs) | 15.513 | per message | M1 | Xeon @ 2.10GHz, kernel fc | #21 (predates the D51 fix) |
