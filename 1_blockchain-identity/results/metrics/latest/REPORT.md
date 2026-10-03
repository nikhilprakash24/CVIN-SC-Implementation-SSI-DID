# CVIN metrics report — 2026-09-30T23-34-57Z_3b786c2

_Run 2026-09-30T23-34-57Z_3b786c2 · commit 3b786c2 · solc 0.8.24 cancun runs=200 viaIR=true · Hardhat in-process automine · N=30_

Cells: exact gas for tx ops; `n/a` = substrate has no primitive (reportable finding); `not impl.` = adapter not on trunk yet.

### L1 — Gas per catalogue operation (exact)

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 76,786 | 399,844 | 656,480 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 366,956 | 568,074 | 1,496,440 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 51,754 | 179,482 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 55,143 | 48,314 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 35,024 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 51,754 | 182,399 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 62,646 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 32,868 | 26,174 | 57,200 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 34,576 | n/a | 57,316 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 34,230 | 27,689 | 23,091 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 55,143 | 419,990 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 33,918 | 142,909 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 33,470 | 125,821 | 214,099 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

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

### L1 — Storage writes per operation (SSTORE count / new slots)

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
| C1_create_identity | 11.644 / 23.617 | 14.434 / 19.007 | 23.741 / 32.455 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 86.135 / 113.235 | 15.046 / 22.422 | 82.659 / 103.03 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 8.354 / 12.412 | 10.252 / 15.283 | 7.494 / 12.651 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 8.553 / 13.09 | 8.655 / 11.968 | 8.636 / 12.618 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 8.81 / 12.993 | 8.538 / 11.825 | 8.551 / 12.823 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 8.545 / 10.49 | 11.691 / 15.087 | 8.407 / 11.945 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 13.154 / 17.096 | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 9.107 / 13.836 | 9.493 / 13.276 | 11.041 / 14.296 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 9.069 / 12.251 | n/a | 10.479 / 14.86 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 8.715 / 13.041 | 10.205 / 12.397 | 7.938 / 10.779 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 8.466 / 13.608 | 15.236 / 20.983 | 9.353 / 14.868 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 9.038 / 13.956 | 10.255 / 13.567 | 8.174 / 11.757 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 8.391 / 12.279 | 9.689 / 13.629 | 26.711 / 68.47 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Read ops: RPC calls / bytes / median ms

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1_resolve_owner | 1 / 68 / 0.641 | 1 / 68 / 0.95 | 1 / 68 / 0.557 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R2_resolve_by_vin | 1 / 68 / 0.68 | 1 / 68 / 0.993 | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R3_resolve_document | 12 / 8592 / 8.589 | 7 / 2652 / 4.554 | 12 / 2800 / 8.174 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.763 | 2 / 136 / 1.229 | 1 / 196 / 0.708 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 92656 / 23.925 | 1 / 708 / 1.322 | 1 / 196 / 0.62 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### Deployment (shared contracts)

| Substrate | Contract | Deploy gas | Bytecode bytes |
|---|---|---:|---:|
| ERC-1056 | EthereumDIDRegistry | 958,726 | 4,187 |
| ERC-1056 | CVINVehicleDIDRegistry | 1,715,174 | 7,365 |
| ERC-721 | CVINVehicleNFT | 2,751,406 | 11,863 |
| ERC-725 | CVIN_DID_ERC725 (issuer identity) | 519,384 | 2,043 |

**Non-deterministic execution gas detected** (distinct values across iterations):
- erc721 U1_rotate_controller: 154742, 157542
- erc725 D1_revoke_delegate: 35768, 35771

### L2 — MOBI VID lifecycle gas per event

| Event | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. VID-I birth certificate | 366,848 | 565,262 | 1,496,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 2. Issuer key anchor | 72,243 | 419,990 | 136,952 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 3. Registration credential anchored | 33,906 | 142,897 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 4. Insurance credential anchored | 33,906 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 5. Service endpoint published | 35,012 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 6. Service record 1 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 7. Service record 2 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 8. Service record 3 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 9. Service record 4 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 10. Service record 5 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 11. Key rotation (add new, revoke old) | 87,975 | 57,376 | 192,830 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 12. Ownership transfer (resale) | 51,742 | 179,587 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 13. Re-registration credential | 33,918 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 14. Credential revocation (old insurance) | 33,458 | 125,809 | 49,218 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 15. Second ownership transfer | 34,646 | 179,599 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 16. End-of-life deactivation | 34,222 | 27,677 | 23,091 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| **Lifetime total** | 995,586 | 2,681,137 | 3,035,251 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Shared deploy gas | 2,673,900 | 2,751,406 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Per-identity deploy gas (in total) | 0 | 0 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 | 3,669,486 | 5,432,543 | 3,554,635 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 | 998,260 | 2,683,888 | 3,035,770 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 000 | 995,589 | 2,681,140 | 3,035,252 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L2 — Lifecycle totals: tx count / log bytes / new slots

| Metric | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Transactions | 25 | 17 | 25 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Log bytes | 6,272 | 4,288 | 2,944 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| New storage slots | 7 | 91 | 79 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

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

### L4 — Create k identities: total gas (per item) [mode]

| k | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 76,786 (76,786) [sequential] | 397,044 (397,044) [sequential] | 656,480 (656,480) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 10 | 767,860 (76,786) [sequential] | 3,995,628 (399,563) [sequential] | 6,564,788 (656,479) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 100 | 7,678,480 (76,785) [sequential] | 39,981,504 (399,815) [sequential] | 65,647,832 (656,478) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 131.33 | 139.89 | 151.14 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| tx / s (mine only) | 1779.72 | 1248.75 | 2110.42 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| gas / s | 4,250,130 | 17,581,224 | 18,136,045 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L6 — Verifier read path after lifecycle: RPC calls / bytes / median ms / p95 ms

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R3_resolve_document | 22 / 16936 / 18.435 / 22.966 | 7 / 5724 / 6.355 / 14.277 | 17 / 4100 / 12.805 / 15.291 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R1_resolve_owner | 1 / 68 / 0.81 / 1.618 | 1 / 68 / 0.704 / 0.906 | 1 / 68 / 0.562 / 0.7 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.858 / 1.732 | 2 / 136 / 1.103 / 1.709 | 2 / 264 / 1.428 / 1.884 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 3395 / 1.403 / 2.008 | 1 / 3268 / 2.671 / 10.575 | 1 / 196 / 0.91 / 1.06 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
