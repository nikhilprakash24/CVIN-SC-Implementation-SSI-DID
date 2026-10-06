### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 202.24 | 166.13 | 170.27 | 191.71 | 77.55 | 184.99 | 191.85 | 168.24 | 170.40 | 183.62 |
| tx / s (mine only) | 2723.78 | 609.26 | 834.11 | 2055.76 | 143.35 | 1224.40 | 1845.04 | 789.73 | 863.91 | 1876.42 |
| gas / s | 6,544,882 | 6,980,109 | 21,398,842 | 23,004,350 | 24,644,122 | 7,103,833 | 18,289,224 | 16,920,184 | 16,127,835 | 6,003,288 |

_Run 2026-10-04T09-50-29Z_0eef6af · commit 0eef6af · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
