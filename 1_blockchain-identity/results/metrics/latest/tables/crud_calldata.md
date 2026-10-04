### L1 — Calldata bytes per operation

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 516 | 584 | 420 | 2,226 | 7,375 | 132 | 7,817 | 132 | 3,749 | 452 |
| C2_create_with_attributes | 2,244 | 1,164 | 612 | 2,926 | 8,403 | 132 | 8,841 | 1,448 | 4,673 | 1,512 |
| U1_rotate_controller | 68 | 68 | 100 | 36 | 36 | 100 | 36 | 196 | 36 | 68 |
| U2_add_delegate | 132 | 132 | 68 | 100 | n/a | n/a | n/a | n/a | 36 | 132 |
| U3_set_attribute | 228 | 228 | 164 | 100 | 452 | 100 | 164 | 196 | 164 | 228 |
| U4_transfer_vehicle | 68 | 68 | 100 | 36 | 36 | 100 | 36 | 196 | 36 | 68 |
| U5_meta_tx | 324 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 900 | n/a |
| D1_revoke_delegate | 100 | 100 | 68 | 36 | n/a | n/a | n/a | n/a | 36 | 100 |
| D2_revoke_attribute | 196 | n/a | n/a | 36 | 36 | 100 | 100 | 132 | 100 | 196 |
| D3_deactivate_identity | 196 | 196 | 36 | 4 | 36 | 100 | 4 | 100 | 36 | 196 |
| V1_issuer_key_anchor | 132 | 132 | 452 | 100 | n/a | 68 | 132 | n/a | 132 | 132 |
| V3_anchor_status | 196 | 196 | 196 | 100 | 420 | 100 | 132 | 164 | 132 | 452 |
| V5_revoke_credential | 164 | 164 | 196 | 36 | 36 | 100 | 100 | 132 | 100 | 68 |

_Run 2026-10-04T09-50-29Z_0eef6af · commit 0eef6af · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
