### L1 — Read ops: RPC calls / bytes / median ms

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1_resolve_owner | 1 / 68 / 0.745 | 1 / 68 / 0.618 | 1 / 68 / 0.565 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R2_resolve_by_vin | 1 / 68 / 0.835 | 1 / 68 / 0.877 | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R3_resolve_document | 12 / 8592 / 8.679 | 7 / 2652 / 4.035 | 12 / 2800 / 8.201 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 1.009 | 2 / 136 / 1.161 | 1 / 196 / 0.787 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 852 / 1.494 | 1 / 708 / 1.146 | 1 / 196 / 0.594 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-03T23-16-23Z_6620ac7 · commit 6620ac7 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
