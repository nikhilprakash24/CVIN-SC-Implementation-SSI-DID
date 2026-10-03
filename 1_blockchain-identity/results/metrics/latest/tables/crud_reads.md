### L1 — Read ops: RPC calls / bytes / median ms

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1_resolve_owner | 1 / 68 / 0.641 | 1 / 68 / 0.95 | 1 / 68 / 0.557 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R2_resolve_by_vin | 1 / 68 / 0.68 | 1 / 68 / 0.993 | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R3_resolve_document | 12 / 8592 / 8.589 | 7 / 2652 / 4.554 | 12 / 2800 / 8.174 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.763 | 2 / 136 / 1.229 | 1 / 196 / 0.708 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 92656 / 23.925 | 1 / 708 / 1.322 | 1 / 196 / 0.62 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-09-30T23-34-57Z_3b786c2 · commit 3b786c2 · solc 0.8.24 cancun runs=200 viaIR=true · Hardhat in-process automine · N=30_
