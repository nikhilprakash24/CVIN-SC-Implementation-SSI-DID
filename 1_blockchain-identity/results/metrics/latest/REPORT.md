# CVIN metrics report — 2026-10-03T23-23-59Z_59405ff

_Run 2026-10-03T23-23-59Z_59405ff · commit 59405ff · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_

Cells: exact gas for tx ops; `n/a` = substrate has no primitive (reportable finding); `not impl.` = adapter not on trunk yet.

### L1 — Gas per catalogue operation (exact)

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 76,808 | 399,844 | 656,480 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 366,978 | 568,074 | 1,496,440 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 51,754 | 179,470 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 55,143 | 48,314 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 35,024 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 51,754 | 182,374 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 62,646 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 32,868 | 26,174 | 57,200 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 34,576 | n/a | 57,316 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 34,230 | 27,689 | 23,091 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 55,143 | 419,990 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 33,918 | 142,909 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 33,470 | 125,821 | 43,388 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Transactions per semantic operation

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 1 | 1 | 2 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 9 | 1 | 9 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 1 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 1 | n/a | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Storage writes per operation (SSTORE count / zero→nonzero SSTOREs)

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 2 / 2 | 24 / 15 | 6 / 6 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 10 / 3 | 27 / 23 | 41 / 34 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 2 / 1 | 13 / 6 | 1 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 2 / 1 | 1 / 1 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 1 / 0 | 4 / 4 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 2 / 1 | 13 / 6 | 1 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 2 / 1 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 2 / 0 | 1 / 0 | 6 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 1 / 0 | n/a | 6 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 1 / 0 | 1 / 0 | 1 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 2 / 1 | 24 / 16 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 1 / 0 | 5 / 5 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 1 / 0 | 5 / 4 | 6 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Event-log bytes per operation

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 224 | 416 | 224 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 2,272 | 416 | 1,120 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 128 | 288 | 96 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 192 | 128 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 288 | 224 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 128 | 288 | 96 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 288 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 192 | 128 | 64 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 288 | n/a | 64 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 256 | 96 | 96 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 192 | 416 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 256 | 256 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 256 | 256 | 64 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Calldata bytes per operation

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 516 | 420 | 2,226 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 2,244 | 612 | 2,926 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 68 | 100 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 132 | 68 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 228 | 164 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 68 | 100 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 324 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 100 | 68 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 196 | n/a | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 196 | 36 | 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 132 | 452 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 196 | 196 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 164 | 196 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Tx latency, median / p95 ms (local node, N=30)

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 9.85 / 12.045 | 11.584 / 14.063 | 18.976 / 21.548 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 70.276 / 83.47 | 12.86 / 17.727 | 68.64 / 89.115 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 6.966 / 9.552 | 9.457 / 15.102 | 6.904 / 10.103 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 7.046 / 12.168 | 7.318 / 10.059 | 7.371 / 10.912 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 7.873 / 11.363 | 7.745 / 11.024 | 7.097 / 10.064 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 6.995 / 10.472 | 10.005 / 14.052 | 6.841 / 8.699 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 12.335 / 15.56 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 8.605 / 9.842 | 7.68 / 10.252 | 9.489 / 12.495 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 8.228 / 9.683 | n/a | 9.392 / 12.125 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 7.777 / 10.774 | 7.813 / 8.685 | 6.575 / 8.98 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 7.487 / 10.268 | 11.969 / 14.243 | 7.061 / 10.502 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 7.637 / 9.415 | 8.1 / 10.95 | 7.442 / 9.237 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 7.655 / 10.984 | 7.679 / 11.094 | 8.258 / 13.301 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Read ops: RPC calls / bytes / median ms

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1_resolve_owner | 1 / 68 / 0.873 | 1 / 68 / 0.584 | 1 / 68 / 0.618 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R2_resolve_by_vin | 1 / 68 / 0.705 | 1 / 68 / 0.714 | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R3_resolve_document | 12 / 8592 / 8.156 | 7 / 2652 / 4.439 | 12 / 2800 / 8.895 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.665 | 2 / 136 / 0.998 | 1 / 196 / 0.628 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 852 / 1.367 | 1 / 708 / 1.029 | 1 / 196 / 0.596 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### Deployment (shared contracts)

| Substrate | Contract | Deploy gas | Bytecode bytes |
|---|---|---:|---:|
| ERC-1056 | EthereumDIDRegistry | 958,726 | 4,187 |
| ERC-1056 | CVINVehicleDIDRegistry | 1,750,295 | 7,528 |
| ERC-721 | CVINVehicleNFT | 2,721,476 | 11,724 |
| ERC-725 | CVIN_DID_ERC725 (issuer identity) | 519,384 | 2,043 |

**Non-deterministic execution gas detected** (distinct values across iterations):
- erc721 C1_create_identity: 373752, 376552
- erc721 U1_rotate_controller: 154730, 157530

### L2 — MOBI VID lifecycle gas per event

| Event | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. VID-I birth certificate | 366,870 | 565,262 | 1,496,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 2. Issuer key anchor | 72,243 | 419,990 | 136,952 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 3. Registration credential anchored | 33,918 | 142,897 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 4. Insurance credential anchored | 33,918 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 5. Service endpoint published | 35,012 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 6. Service record 1 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 7. Service record 2 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 8. Service record 3 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 9. Service record 4 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 10. Service record 5 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 11. Delegate key added (k1) | 55,131 | 48,314 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 12. Key rotation (k1 to k2) | 87,987 | 31,214 | 192,830 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 13. Ownership transfer (resale) | 51,742 | 177,562 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 14. Re-registration credential | 33,918 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 15. Credential revocation (old insurance) | 33,470 | 125,809 | 49,218 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 16. Second ownership transfer | 34,646 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 17. End-of-life deactivation | 34,222 | 27,677 | 23,091 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| **Lifetime total** | 1,050,787 | 2,701,239 | 3,155,103 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Shared deploy gas | 2,709,021 | 2,721,476 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Per-identity deploy gas (in total) | 0 | 0 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 | 3,759,808 | 5,422,715 | 3,674,487 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 | 1,053,496 | 2,703,960 | 3,155,622 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 000 | 1,050,790 | 2,701,242 | 3,155,104 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L2 — Lifecycle totals: tx count / log bytes / zero→nonzero SSTOREs

| Metric | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Transactions | 26 | 17 | 26 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Log bytes | 6,464 | 4,288 | 3,072 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Zero→nonzero SSTOREs | 8 | 92 | 83 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L3 — Marginal cost vs population N and history h (gas; reads: RPC calls / bytes)

| Axis | op | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N=0|C2_create_with_attributes | 366,978 | 565,274 | 1,496,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|U3_set_attribute | 35,024 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|U4_transfer_vehicle | 51,754 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=0|R3_resolve_document | 12 RPC / 8434 B | 7 RPC / 2588 B | 11 RPC / 2540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|C2_create_with_attributes | 366,978 | 568,074 | 1,496,428 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|U3_set_attribute | 35,024 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|U4_transfer_vehicle | 51,754 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|R3_resolve_document | 12 RPC / 8444 B | 7 RPC / 2588 B | 11 RPC / 2540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|C2_create_with_attributes | 366,978 | 568,074 | 1,496,440 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|U3_set_attribute | 35,024 | 120,073 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|U4_transfer_vehicle | 51,754 | 179,586 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|R3_resolve_document | 12 RPC / 8454 B | 7 RPC / 2588 B | 11 RPC / 2540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|U3_set_attribute | 35,028 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|U4_transfer_vehicle | 34,658 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|R3_resolve_document | 14 RPC / 10005 B | 7 RPC / 3164 B | 12 RPC / 2800 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|U3_set_attribute | 35,028 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|U4_transfer_vehicle | 34,658 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|R3_resolve_document | 32 RPC / 24153 B | 7 RPC / 8348 B | 21 RPC / 5140 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|U3_set_attribute | 35,028 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|U4_transfer_vehicle | 34,658 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|R3_resolve_document | 112 RPC / 87033 B | 7 RPC / 31388 B | 61 RPC / 15540 B | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L3 — Read latency vs N and h: median / p95 ms (in-process, 2 warm-up + 10 samples)

| Axis | op | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N=0|R3_resolve_document | 8.472 / 9.09 | 3.925 / 5.396 | 6.82 / 7.608 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|R3_resolve_document | 8.068 / 9.171 | 3.792 / 4.967 | 8.555 / 15.267 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|R3_resolve_document | 9.012 / 11.771 | 4.093 / 5.565 | 8.852 / 10.747 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|R3_resolve_document | 8.782 / 11.576 | 4.166 / 4.854 | 8.783 / 10.321 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|R3_resolve_document | 19.718 / 25.248 | 7.769 / 13.863 | 15.719 / 18.496 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|R3_resolve_document | 68.016 / 78.582 | 29.333 / 121.629 | 52.072 / 67.677 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L4 — Create k identities: total gas (per item) [mode]

| k | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 76,808 (76,808) [sequential] | 397,044 (397,044) [sequential] | 656,480 (656,480) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 10 | 768,080 (76,808) [sequential] | 3,995,640 (399,564) [sequential] | 6,564,788 (656,479) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 100 | 7,680,800 (76,808) [sequential] | 39,981,600 (399,816) [sequential] | 65,647,832 (656,478) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 163.18 | 175.85 | 191.70 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| tx / s (mine only) | 954.69 | 1149.78 | 2225.58 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| gas / s | 5,280,982 | 22,100,260 | 23,002,620 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L6 — Verifier read path after lifecycle: RPC calls / bytes / median ms / p95 ms

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R3_resolve_document | 22 / 16936 / 14.169 / 18.659 | 7 / 5724 / 6.332 / 9.081 | 17 / 4100 / 12.655 / 15.231 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R1_resolve_owner | 1 / 68 / 0.795 / 1.318 | 1 / 68 / 0.775 / 0.903 | 1 / 68 / 0.622 / 0.886 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.891 / 1.183 | 2 / 136 / 1.093 / 1.567 | 1 / 196 / 0.776 / 1.099 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 3395 / 1.409 / 2.031 | 1 / 3268 / 2.783 / 3.046 | 1 / 196 / 0.665 / 0.866 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
