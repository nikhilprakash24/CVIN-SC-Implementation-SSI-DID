### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 171.79 | 103.72 | 134.04 | 210.69 | 86.01 | 183.35 | 153.58 | 161.16 | 180.92 | 162.58 |
| tx / s (mine only) | 2555.54 | 201.08 | 339.72 | 2369.77 | 181.23 | 792.41 | 565.88 | 940.76 | 1018.55 | 1214.80 |
| gas / s | 5,706,628 | 4,357,774 | 16,845,415 | 25,281,108 | 27,352,986 | 7,733,774 | 14,640,838 | 16,208,409 | 17,124,438 | 5,243,316 |

_Run 2026-10-23T00-49-12Z_1f4ace0 · commit 1f4ace0 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
