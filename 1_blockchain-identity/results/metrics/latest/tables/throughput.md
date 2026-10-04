### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 147.89 | 159.05 | 125.14 | 183.75 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| tx / s (mine only) | 1652.08 | 1198.60 | 344.75 | 2394.57 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| gas / s | 4,786,272 | 6,682,651 | 15,833,689 | 22,049,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-04T05-31-55Z_3ea92f7 · commit 3ea92f7 (dirty) · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
