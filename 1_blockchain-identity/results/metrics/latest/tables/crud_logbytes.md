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

_Run 2026-10-03T23-16-23Z_6620ac7 · commit 6620ac7 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
