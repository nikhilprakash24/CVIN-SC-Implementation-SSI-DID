### L1 — Read ops: RPC calls / bytes / median ms

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1_resolve_owner | 1 / 68 / 0.594 | 1 / 68 / 0.798 | 1 / 68 / 0.847 | 1 / 68 / 0.667 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R2_resolve_by_vin | 1 / 68 / 0.598 | 1 / 68 / 0.714 | 1 / 68 / 0.931 | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R3_resolve_document | 12 / 8592 / 7.224 | 6 / 9170 / 5.774 | 7 / 2652 / 4.215 | 12 / 2800 / 9.01 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.709 | 1 / 68 / 0.782 | 2 / 136 / 1.089 | 1 / 196 / 1.069 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 852 / 1.133 | 1 / 851 / 1.006 | 1 / 708 / 1.398 | 1 / 196 / 0.856 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-04T05-31-55Z_3ea92f7 · commit 3ea92f7 (dirty) · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
