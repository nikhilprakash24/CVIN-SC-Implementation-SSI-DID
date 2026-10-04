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

_Run 2026-10-04T05-41-19Z_bca0899 · commit bca0899 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
