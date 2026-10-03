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

_Run 2026-09-30T23-34-57Z_3b786c2 · commit 3b786c2 · solc 0.8.24 cancun runs=200 viaIR=true · Hardhat in-process automine · N=30_
