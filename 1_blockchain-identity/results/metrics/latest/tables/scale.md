### L3 — Marginal cost vs population N and history h (gas; reads: median ms / RPC calls)

| Axis | op | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N=0|C2_create_with_attributes | 366,956 | 565,274 | 1,496,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|U3_set_attribute | 35,024 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|U4_transfer_vehicle | 51,754 | 179,599 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|R3_resolve_document | 9.238 ms / 12 | 4.345 ms / 7 | 7.867 ms / 11 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|C2_create_with_attributes | 366,956 | 568,074 | 1,496,428 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|U3_set_attribute | 35,024 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|U4_transfer_vehicle | 51,754 | 179,599 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|R3_resolve_document | 9.242 ms / 12 | 5.635 ms / 7 | 10.202 ms / 11 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|C2_create_with_attributes | 366,956 | 568,074 | 1,496,440 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|U3_set_attribute | 35,024 | 120,073 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|U4_transfer_vehicle | 51,754 | 179,611 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|R3_resolve_document | 8.411 ms / 12 | 5.082 ms / 7 | 9.116 ms / 11 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|U3_set_attribute | 35,016 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|U4_transfer_vehicle | 34,646 | 179,599 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|R3_resolve_document | 11.487 ms / 14 | 3.81 ms / 7 | 8.348 ms / 12 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|U3_set_attribute | 35,028 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|U4_transfer_vehicle | 34,658 | 179,599 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|R3_resolve_document | 27.729 ms / 32 | 9.015 ms / 7 | 15.2 ms / 21 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|U3_set_attribute | 35,028 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|U4_transfer_vehicle | 34,658 | 179,599 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|R3_resolve_document | 79.929 ms / 112 | 23.172 ms / 7 | 51.709 ms / 61 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-09-30T23-34-57Z_3b786c2 · commit 3b786c2 · solc 0.8.24 cancun runs=200 viaIR=true · Hardhat in-process automine · N=30_
