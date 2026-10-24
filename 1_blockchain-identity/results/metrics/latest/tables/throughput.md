### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 153.26 | 102.13 | 125.98 | 162.95 | 77.66 | 142.81 | 147.47 | 150.53 | 143.97 | 157.11 |
| tx / s (mine only) | 1215.12 | 315.12 | 406.34 | 1570.25 | 184.99 | 920.79 | 1502.85 | 1620.81 | 1599.80 | 1676.13 |
| gas / s | 4,959,922 | 4,290,844 | 15,940,214 | 19,552,985 | 24,698,410 | 6,023,847 | 14,058,518 | 15,139,320 | 13,626,423 | 5,158,710 |

_Run 2026-10-24T13-01-37Z_963439a · commit 963439a · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
