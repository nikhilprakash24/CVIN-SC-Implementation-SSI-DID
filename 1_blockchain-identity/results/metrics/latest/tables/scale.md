### L3 — Marginal cost vs population N and history h (gas; reads: RPC calls / bytes)

| Axis | op | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N=0|C2_create_with_attributes | 366,978 | 234,587 | 565,274 | 1,496,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|U3_set_attribute | 35,024 | 44,677 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|U4_transfer_vehicle | 51,754 | 57,188 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|R3_resolve_document | 12 RPC / 8434 B | 5 RPC / 8427 B | 7 RPC / 2588 B | 11 RPC / 2540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|C2_create_with_attributes | 366,978 | 234,587 | 568,074 | 1,496,428 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|U3_set_attribute | 35,024 | 44,677 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|U4_transfer_vehicle | 51,754 | 57,188 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|R3_resolve_document | 12 RPC / 8444 B | 5 RPC / 8437 B | 7 RPC / 2588 B | 11 RPC / 2540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|C2_create_with_attributes | 366,978 | 234,587 | 568,074 | 1,496,440 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|U3_set_attribute | 35,024 | 44,677 | 120,073 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|U4_transfer_vehicle | 51,754 | 57,188 | 179,586 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|R3_resolve_document | 12 RPC / 8454 B | 5 RPC / 8447 B | 7 RPC / 2588 B | 11 RPC / 2540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|U3_set_attribute | 35,028 | 44,681 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|U4_transfer_vehicle | 34,658 | 40,096 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|R3_resolve_document | 14 RPC / 10005 B | 6 RPC / 9404 B | 7 RPC / 3164 B | 12 RPC / 2800 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|U3_set_attribute | 35,028 | 44,681 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|U4_transfer_vehicle | 34,658 | 40,096 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|R3_resolve_document | 32 RPC / 24153 B | 15 RPC / 18203 B | 7 RPC / 8348 B | 21 RPC / 5140 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|U3_set_attribute | 35,028 | 44,681 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|U4_transfer_vehicle | 34,658 | 40,096 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|R3_resolve_document | 112 RPC / 87033 B | 55 RPC / 57323 B | 7 RPC / 31388 B | 61 RPC / 15540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-04T05-41-19Z_bca0899 · commit bca0899 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
