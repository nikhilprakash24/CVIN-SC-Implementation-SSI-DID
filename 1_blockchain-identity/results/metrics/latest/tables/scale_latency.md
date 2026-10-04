### L3 — Read latency vs N and h: median / p95 ms (in-process, 2 warm-up + 10 samples)

| Axis | op | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N=0|R3_resolve_document | 7.488 / 8.037 | 5.72 / 7.991 | 4.576 / 5.453 | 7.473 / 8.289 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|R3_resolve_document | 7.296 / 8.922 | 4.927 / 5.717 | 3.683 / 7.628 | 6.32 / 7.894 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|R3_resolve_document | 7.429 / 7.76 | 4.988 / 9.199 | 4.679 / 7.591 | 7.667 / 8.5 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|R3_resolve_document | 11.591 / 16.477 | 5.724 / 6.272 | 4.092 / 5.608 | 7.641 / 8.672 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|R3_resolve_document | 22.432 / 26.479 | 12.532 / 14.205 | 6.076 / 7.321 | 12.075 / 15.867 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|R3_resolve_document | 74.889 / 87.744 | 39.394 / 55.041 | 16.225 / 24.504 | 43.686 / 54.095 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-04T05-31-55Z_3ea92f7 · commit 3ea92f7 (dirty) · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
