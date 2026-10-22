# Gas Charter (Class G)

**Generated** by `docs/testing/gas_charter.py`; do not edit. **Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-15 (WM-2 step B2; TSR P4-3; guide rule 1.1.10).

## 1. The rule
Every gas figure quoted in the thesis or the register is in exactly one class, and is quoted as its class says.

| Class | Meaning |
|---|---|
| G-exact | deterministic for its inputs: one value, quoted as exact |
| G-seeded | an incidental random input fixed by a recorded seed: exact for that seed |
| G-first-call | deterministic, but the first call meets different contract state: two exact values (first call, steady state) |
| G-mode | varies across the iterations of one cell with per-iteration inputs (keys, signatures, ids), each deterministic, so the cell reproduces run to run: the mode is quoted, with the range beside it |
| G-range | the varying input is the thing measured: a range over declared seeds or runs |
| G-derived | computed from other gas figures; inherits their classes |
| G-history | a record of how a past run's gas moved; not a current measurement |

## 2. The metrics harness's varying cells (run of record `7a9a996`)

Of **119** transaction cells (36 iterations each: 1 exact + 5 warm-up + 30 samples), **33** vary in total gas. The harness's own `gasDeterministic` flag tracks **execution** gas only (its comment: total gas "may differ by a few units through calldata zero-byte pricing"), so it marks 15 cells; the other 18 vary in calldata only. The harness tables quote the **mode**; `crud.json` stores each cell's `gasUsedRange`. Causes, computed from every iteration in `raw.jsonl`:

| Cause | Cells |
|---|---:|
| calldata zero bytes | 30 |
| execution path differs | 7 |
| value-dependent opcode cost | 4 |
| first-call state | 4 |

| Standard | Operation | mode | min | max | Δ execution | Δ EVM steps | cause | harness flag | class |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| cvin | `C1_create_identity` | 271,402 | 271,352 | 271,402 | 26 | 8 | calldata zero bytes; execution path differs (EVM steps vary) | execution varies | G-mode |
| cvin | `C2_create_with_attributes` | 1,015,730 | 1,015,666 | 1,015,730 | 52 | 16 | calldata zero bytes; execution path differs (EVM steps vary) | execution varies | G-mode |
| cvin | `P1_create_presentation` | 50,992 | 50,980 | 50,992 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| cvin | `V3_anchor_status` | 294,195 | 294,145 | 294,195 | 26 | 8 | calldata zero bytes; execution path differs (EVM steps vary) | execution varies | G-mode |
| cvin | `V5_revoke_credential` | 93,498 | 93,488 | 93,498 | 2 | 0 | calldata zero bytes; value-dependent opcode cost (same EVM steps) | execution varies | G-mode |
| erc1056 | `P1_create_presentation` | 34,206 | 34,194 | 34,206 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc1056 | `U5_meta_tx` | 62,646 | 62,634 | 62,646 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc1056w | `P1_create_presentation` | 45,257 | 45,245 | 45,257 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc4337 | `P1_create_presentation` | 71,764 | 71,752 | 71,764 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc4337 | `U5_meta_tx` | 141,767 | 141,731 | 141,767 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc4337 | `V1_issuer_key_anchor` | 49,151 | 49,139 | 49,151 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc721 | `C1_create_identity` | 402,567 | 399,767 | 402,567 | 2800 | 0 | first-call state (same storage writes; a slot already warm or set) | execution varies | G-first-call |
| erc721 | `D3_deactivate_identity` | 27,689 | 27,677 | 27,689 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc721 | `U1_rotate_controller` | 179,470 | 176,670 | 179,470 | 2800 | 0 | first-call state (same storage writes; a slot already warm or set) | execution varies | G-first-call |
| erc725 | `C1_create_identity` | 656,480 | 656,468 | 656,480 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc725 | `C2_create_with_attributes` | 1,496,440 | 1,496,404 | 1,496,452 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc725xy | `P1_create_presentation` | 72,369 | 72,357 | 72,369 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc725xy | `V1_issuer_key_anchor` | 49,745 | 49,721 | 49,745 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| erc735 | `C2_create_with_attributes` | 2,558,484 | 2,558,460 | 2,558,509 | 25 | 8 | calldata zero bytes; execution path differs (EVM steps vary) | execution varies | G-mode |
| erc735 | `D2_revoke_attribute` | 96,611 | 96,601 | 96,611 | 2 | 0 | calldata zero bytes; value-dependent opcode cost (same EVM steps) | execution varies | G-mode |
| erc735 | `P1_create_presentation` | 294,868 | 294,844 | 294,893 | 25 | 8 | calldata zero bytes; execution path differs (EVM steps vary) | execution varies | G-mode |
| erc735 | `U3_set_attribute` | 318,054 | 318,005 | 318,054 | 25 | 8 | calldata zero bytes; execution path differs (EVM steps vary) | execution varies | G-mode |
| erc735 | `V3_anchor_status` | 345,920 | 345,908 | 345,945 | 25 | 8 | calldata zero bytes; execution path differs (EVM steps vary) | execution varies | G-mode |
| erc735 | `V5_revoke_credential` | 92,273 | 92,264 | 92,273 | 3 | 0 | calldata zero bytes; value-dependent opcode cost (same EVM steps) | execution varies | G-mode |
| lsp8 | `C1_create_identity` | 135,544 | 135,544 | 152,644 | 17100 | 0 | first-call state (one more new storage slot) | execution varies | G-first-call |
| lsp8 | `C2_create_with_attributes` | 373,187 | 373,103 | 373,187 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| lsp8 | `D2_revoke_attribute` | 37,807 | 37,788 | 37,807 | 5 | 0 | calldata zero bytes; value-dependent opcode cost (same EVM steps) | execution varies | G-mode |
| lsp8 | `D3_deactivate_identity` | 43,044 | 43,032 | 43,044 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| lsp8 | `U1_rotate_controller` | 83,380 | 80,580 | 83,380 | 2800 | 0 | calldata zero bytes; first-call state (same storage writes; a slot already warm or set) | execution varies | G-mode |
| lsp8 | `U3_set_attribute` | 100,574 | 100,550 | 100,574 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| lsp8 | `U4_transfer_vehicle` | 83,380 | 83,368 | 83,380 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| lsp8 | `V3_anchor_status` | 54,893 | 54,881 | 54,893 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |
| lsp8 | `V5_revoke_credential` | 32,231 | 32,219 | 32,231 | 0 | 0 | calldata zero bytes | execution-deterministic | G-mode |

**What follows.**
- **No random input.** The harness draws every fresh key from `keccak256("cvin-bench/fresh-key/v1", 42, i)` and every credential hash from a salted keccak, both skipping values with a zero byte (register §5.A), and ethers signs deterministically (RFC 6979). A cell therefore reproduces from run to run (register §5.A, reproducibility). What varies is the input from one iteration to the next: the 36 iterations of a cell use 36 different keys, and the values derived from them (signatures, token ids, created addresses) are not filtered for zero bytes. These cells are G-mode, not G-seeded: the mode is reproducible, and a single cell is quoted with its `gasUsedRange`.
- **The fix, at A6.** Extending the zero-byte rule from keys and hashes to every derived calldata value (or quoting the range per cell) would move the calldata cells to G-exact. The harness code is frozen until its re-run of record (WM-2 A6, N-19), so the change lands there.
- **First-call state:** deterministic. The first iteration meets a contract-global slot in a different state; quote the steady state (the mode) and, where the first call matters, its value too.
- **Mechanisms not isolated:** the 8-step execution-path difference and the 2–5 gas value-dependent difference follow the per-iteration key and signature, but are not traced to an opcode. That is stated, not assumed. The plan's guess of "address-dependent storage" is not borne out: no varying cell changes its storage writes except lsp8 C1, which is first-call state.

## 3. Register rows that report gas (status V)

| Row | Class | Why |
|---|---|---|
| #1 | G-exact | Hardhat test suite, fixed signers |
| #3 | G-exact | gas-reporter average over the suite's calls; exact for the suite, not a single operation |
| #6 | G-derived | ratio of exact creation costs (#25) |
| #22 | G-range | the row reports 37,767–37,791 from calldata zero bytes |
| #25 | G-exact | benchmark_gas.js with fixed signers and its own run-to-run determinism check |
| #26 | G-derived | scaling and lifetime figures built from exact per-operation costs |
| #28 | G-exact | security scenarios with fixed accounts; the attestEvent gas is a single run |
| #29 | G-mode | metrics harness: modes of 36 iterations; varying cells in §2 |
| #30 | G-mode | metrics harness lifecycle: sums of per-operation modes |
| #31 | G-mode | metrics harness scale: modes; the row notes ≤ 12 gas from tokenId width |
| #33 | G-range | lifecycle parity: the row reports birth 398,274–398,298 |
| #34 | G-mode | metrics harness: modes of 36 iterations; varying cells in §2 |
| #35 | G-mode | metrics harness lifecycle: sums of per-operation modes |
| #36 | G-derived | dominance analysis over #34 and #35 |
| #38 | G-exact | pseudonym pool: the row states gas exact |
| #39 | G-mode | metrics harness over HTTP-RPC: gas identical to the in-process run of record (#29, #34, #35); modes as there |
| #42 | G-history | gas moved by the 2026-10-04 defect fixes |
| #43 | G-history | gas moved by the pass-06 fixes |
| #47 | G-range | I4 over declared seeds 1–30; seed 1 exact (WM-2 B1) |
| #49 | G-mode | metrics harness storage and log counts; gas column inherits §2 |
| #50 | G-mode | metrics harness: ERC-1056 U5 varies 62,634–62,646 (calldata only); U3 exact |
| #54 | G-mode | metrics harness: P1 and X1 cells are modes; re-run on the merged tree, run 2026-10-21T03-28-59Z_a9e2a28 |
| #58 | G-exact | layer 5 measure_gas.js: fixed proof and signers, receipt gas; view rows are eth_estimateGas |

23 rows classified; every V row whose claim mentions gas (21) has a class.
