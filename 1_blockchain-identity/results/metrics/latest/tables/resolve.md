### L6 — Verifier read path after lifecycle: RPC calls / bytes / median ms / p95 ms

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R3_resolve_document | 22 / 16936 / 15.948 / 23.707 | 7 / 5724 / 7.586 / 22.515 | 17 / 4100 / 13.5 / 15.936 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R1_resolve_owner | 1 / 68 / 0.924 / 1.086 | 1 / 68 / 0.776 / 1.134 | 1 / 68 / 0.719 / 1.793 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 1.169 / 2.306 | 2 / 136 / 1.14 / 1.909 | 1 / 196 / 0.986 / 1.207 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 3395 / 1.443 / 2.318 | 1 / 3268 / 2.867 / 14.342 | 1 / 196 / 0.721 / 0.913 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-03T23-16-23Z_6620ac7 · commit 6620ac7 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
