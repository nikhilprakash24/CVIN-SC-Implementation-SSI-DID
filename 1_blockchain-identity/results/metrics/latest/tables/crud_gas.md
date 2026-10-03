### L1 — Gas per catalogue operation (exact)

| Operation | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 76,786 | 399,844 | 656,480 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| C2_create_with_attributes | 366,956 | 568,074 | 1,496,440 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
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

_Run 2026-10-03T23-16-23Z_6620ac7 · commit 6620ac7 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
