### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 152.66 | 156.73 | 131.85 | 175.26 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| tx / s (mine only) | 2452.81 | 1177.11 | 408.93 | 1291.41 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| gas / s | 4,940,436 | 6,585,171 | 16,571,016 | 21,030,595 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-04T05-41-19Z_bca0899 · commit bca0899 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
