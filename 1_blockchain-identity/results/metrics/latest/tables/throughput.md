### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 98.15 | 86.85 | 80.52 | 119.90 | 44.30 | 110.83 | 105.48 | 99.15 | 112.08 | 107.57 |
| tx / s (mine only) | 1545.85 | 339.82 | 217.54 | 1656.59 | 82.44 | 865.88 | 611.05 | 722.38 | 915.43 | 1610.31 |
| gas / s | 3,186,289 | 3,649,056 | 10,118,888 | 14,387,246 | 14,088,768 | 4,675,101 | 10,055,793 | 9,971,616 | 10,608,280 | 3,440,051 |

_Run 2026-10-31T03-29-43Z_291a801 · commit 291a801 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
