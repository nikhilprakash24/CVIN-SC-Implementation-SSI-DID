# CVIN metrics report — 2026-10-04T05-41-19Z_bca0899

_Run 2026-10-04T05-41-19Z_bca0899 · commit bca0899 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_

Cells: exact gas for tx ops; `n/a` = substrate has no primitive (reportable finding); `not impl.` = adapter not on trunk yet.

### L1 — Gas per catalogue operation (exact)

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 76,808 | 145,662 | 399,844 | 656,480 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 366,978 | 234,587 | 568,074 | 1,496,440 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 51,754 | 57,188 | 179,470 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 55,143 | 64,720 | 48,314 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 35,024 | 44,677 | 120,061 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 51,754 | 57,188 | 182,374 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 62,646 | n/a | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 32,868 | 41,888 | 26,174 | 57,200 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 34,576 | n/a | n/a | 57,316 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 34,230 | 43,809 | 27,689 | 23,091 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 55,143 | 55,143 | 419,990 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 33,918 | 33,918 | 142,909 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 33,470 | 33,470 | 125,821 | 43,388 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Transactions per semantic operation

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 1 | 2 | 1 | 2 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 9 | 3 | 1 | 9 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 1 | n/a | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 1 | n/a | n/a | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 1 | 1 | 1 | 1 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Storage writes per operation (SSTORE count / zero→nonzero SSTOREs)

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 2 / 2 | 4 / 4 | 24 / 15 | 6 / 6 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 10 / 3 | 12 / 4 | 27 / 23 | 41 / 34 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 2 / 1 | 1 / 1 | 13 / 6 | 1 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 2 / 1 | 2 / 1 | 1 / 1 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 1 / 0 | 1 / 0 | 4 / 4 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 2 / 1 | 1 / 1 | 13 / 6 | 1 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 2 / 1 | n/a | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 2 / 0 | 2 / 0 | 1 / 0 | 6 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 1 / 0 | n/a | n/a | 6 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 2 / 1 | 2 / 1 | 24 / 16 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 1 / 0 | 1 / 0 | 5 / 5 | 5 / 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 1 / 0 | 1 / 0 | 5 / 4 | 6 / 0 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Event-log bytes per operation

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 224 | 352 | 416 | 224 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 2,272 | 2,400 | 416 | 1,120 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 128 | 128 | 288 | 96 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 192 | 192 | 128 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 288 | 288 | 224 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 128 | 128 | 288 | 96 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 288 | n/a | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 192 | 192 | 128 | 64 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 288 | n/a | n/a | 64 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 256 | 256 | 96 | 96 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 192 | 192 | 416 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 256 | 256 | 256 | 128 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 256 | 256 | 256 | 64 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Calldata bytes per operation

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 516 | 584 | 420 | 2,226 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 2,244 | 1,164 | 612 | 2,926 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 68 | 68 | 100 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 132 | 132 | 68 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 228 | 228 | 164 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 68 | 68 | 100 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 324 | n/a | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 100 | 100 | 68 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 196 | n/a | n/a | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 196 | 196 | 36 | 4 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 132 | 132 | 452 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 196 | 196 | 196 | 100 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 164 | 164 | 196 | 36 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Tx latency, median / p95 ms (local node, N=30)

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 9.352 / 11.288 | 17.171 / 27.382 | 13.244 / 16.714 | 20.976 / 25.773 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 76.181 / 90.41 | 35.982 / 62.088 | 13.709 / 18.501 | 79.203 / 97.753 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U1_rotate_controller | 7.637 / 12.972 | 8.193 / 12.345 | 10.961 / 12.365 | 7.213 / 11.439 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U2_add_delegate | 8.081 / 10.107 | 11.274 / 16.028 | 8.24 / 12.17 | 7.598 / 11.487 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U3_set_attribute | 8.654 / 11.424 | 11.531 / 15.185 | 8.932 / 12.362 | 7.843 / 9.068 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U4_transfer_vehicle | 7.909 / 9.545 | 8.872 / 12.403 | 11.663 / 17.938 | 7.022 / 7.849 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| U5_meta_tx | 12.466 / 16.439 | n/a | n/a | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D1_revoke_delegate | 8.436 / 12.024 | 9.451 / 12.943 | 9.551 / 13.747 | 10.667 / 22.737 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D2_revoke_attribute | 8.378 / 10.377 | n/a | n/a | 10.913 / 19.05 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| D3_deactivate_identity | 8.475 / 11.075 | 10.187 / 15.007 | 8.353 / 11.856 | 8.333 / 10.794 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V1_issuer_key_anchor | 8.293 / 11.543 | 8.158 / 10.193 | 14.337 / 22.518 | 8.303 / 11.078 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V3_anchor_status | 8.61 / 11.176 | 8.897 / 13.585 | 9.524 / 13.98 | 8.748 / 12.7 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V5_revoke_credential | 8.25 / 11.29 | 8.808 / 13.113 | 10.305 / 15.178 | 9.266 / 20.651 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L1 — Read ops: RPC calls / bytes / median ms

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1_resolve_owner | 1 / 68 / 0.66 | 1 / 68 / 0.772 | 1 / 68 / 0.718 | 1 / 68 / 0.737 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R2_resolve_by_vin | 1 / 68 / 0.661 | 1 / 68 / 0.779 | 1 / 68 / 0.729 | n/a | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R3_resolve_document | 12 / 8592 / 8.423 | 6 / 9170 / 6.075 | 7 / 2652 / 4.572 | 12 / 2800 / 9.145 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.69 | 1 / 68 / 0.968 | 2 / 136 / 1.093 | 1 / 196 / 0.745 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 852 / 1.24 | 1 / 851 / 0.954 | 1 / 708 / 1.278 | 1 / 196 / 0.687 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### Deployment (shared contracts)

| Substrate | Contract | Deploy gas | Bytecode bytes |
|---|---|---:|---:|
| ERC-1056 | EthereumDIDRegistry | 958,726 | 4,187 |
| ERC-1056 | CVINVehicleDIDRegistry | 1,750,295 | 7,528 |
| ERC-1056 (wrapper) | EthereumDIDRegistry | 958,726 | 4,187 |
| ERC-1056 (wrapper) | CVINVehicleDIDRegistry | 1,750,295 | 7,528 |
| ERC-721 | CVINVehicleNFT | 2,721,476 | 11,724 |
| ERC-725 | CVIN_DID_ERC725 (issuer identity) | 519,384 | 2,043 |

**Non-deterministic execution gas detected** (distinct values across iterations):
- erc721 C1_create_identity: 373752, 376552
- erc721 U1_rotate_controller: 154730, 157530

### L2 — MOBI VID lifecycle gas per event

| Event | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. VID-I birth certificate | 366,870 | 234,551 | 565,262 | 1,496,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 2. Issuer key anchor | 72,243 | 72,243 | 419,990 | 136,952 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 3. Registration credential anchored | 33,918 | 33,918 | 142,897 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 4. Insurance credential anchored | 33,918 | 33,918 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 5. Service endpoint published | 35,012 | 44,665 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 6. Service record 1 | 35,542 | 45,269 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 7. Service record 2 | 35,542 | 45,269 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 8. Service record 3 | 35,542 | 45,269 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 9. Service record 4 | 35,542 | 45,269 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 10. Service record 5 | 35,542 | 45,269 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 11. Delegate key added (k1) | 55,131 | 64,708 | 48,314 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 12. Key rotation (k1 to k2) | 87,987 | 106,584 | 31,214 | 192,830 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 13. Ownership transfer (resale) | 51,742 | 57,176 | 177,562 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 14. Re-registration credential | 33,918 | 33,918 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 15. Credential revocation (old insurance) | 33,470 | 33,470 | 125,809 | 49,218 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 16. Second ownership transfer | 34,646 | 40,084 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 17. End-of-life deactivation | 34,222 | 43,801 | 27,677 | 23,091 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| **Lifetime total** | 1,050,787 | 1,025,381 | 2,701,239 | 3,155,103 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Shared deploy gas | 2,709,021 | 2,709,021 | 2,721,476 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Per-identity deploy gas (in total) | 0 | 0 | 0 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 | 3,759,808 | 3,734,402 | 5,422,715 | 3,674,487 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 | 1,053,496 | 1,028,090 | 2,703,960 | 3,155,622 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 000 | 1,050,790 | 1,025,384 | 2,701,242 | 3,155,104 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L2 — Lifecycle totals: tx count / log bytes / zero→nonzero SSTOREs

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Transactions | 26 | 20 | 17 | 26 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Log bytes | 6,464 | 6,592 | 4,288 | 3,072 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Zero→nonzero SSTOREs | 8 | 9 | 92 | 83 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

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

### L3 — Read latency vs N and h: median / p95 ms (in-process, 2 warm-up + 10 samples)

| Axis | op | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N=0|R3_resolve_document | 9.377 / 12.628 | 5.693 / 8.546 | 3.949 / 5.164 | 9.354 / 11.323 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=100|R3_resolve_document | 8.66 / 12.292 | 5.308 / 6.155 | 4.372 / 5.437 | 9.442 / 14.432 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| N=1000|R3_resolve_document | 11.645 / 14.593 | 7.04 / 9.245 | 3.868 / 5.077 | 7.193 / 10.999 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=1|R3_resolve_document | 10.037 / 14.587 | 6.59 / 7.543 | 3.613 / 5.438 | 10.203 / 16.268 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=10|R3_resolve_document | 21.047 / 25.573 | 12.003 / 13.702 | 8.033 / 12.499 | 14.445 / 16.467 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| h=50|R3_resolve_document | 77.301 / 117.713 | 43.763 / 51.596 | 28.149 / 65.459 | 40.956 / 51.772 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L4 — Create k identities: total gas (per item) [mode]

| k | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 76,808 (76,808) [sequential] | 145,662 (145,662) [sequential] | 397,044 (397,044) [sequential] | 656,480 (656,480) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 10 | 768,080 (76,808) [sequential] | 1,456,620 (145,662) [sequential] | 3,995,640 (399,564) [sequential] | 6,564,788 (656,479) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 100 | 7,680,800 (76,808) [sequential] | 14,566,200 (145,662) [sequential] | 39,981,600 (399,816) [sequential] | 65,647,832 (656,478) [sequential] | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)

| Metric | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tx / s (queue + mine) | 152.66 | 156.73 | 131.85 | 175.26 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| tx / s (mine only) | 2452.81 | 1177.11 | 408.93 | 1291.41 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| gas / s | 4,940,436 | 6,585,171 | 16,571,016 | 21,030,595 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

### L6 — Verifier read path after lifecycle: RPC calls / bytes / median ms / p95 ms

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R3_resolve_document | 22 / 16936 / 16.48 / 21.082 | 14 / 16328 / 11.816 / 15.563 | 7 / 5724 / 6.017 / 8.483 | 17 / 4100 / 11.977 / 15.49 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R1_resolve_owner | 1 / 68 / 0.797 / 1.806 | 1 / 68 / 1.156 / 1.926 | 1 / 68 / 0.739 / 0.952 | 1 / 68 / 0.737 / 0.879 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| R4_verify_delegate | 1 / 68 / 0.869 / 1.249 | 1 / 68 / 1.655 / 3.008 | 2 / 136 / 1.158 / 1.969 | 1 / 196 / 1.075 / 1.317 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| V6_status_check | 1 / 3395 / 1.42 / 2.497 | 1 / 3395 / 1.312 / 1.71 | 1 / 3268 / 2.636 / 3.544 | 1 / 196 / 0.867 / 1.088 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
