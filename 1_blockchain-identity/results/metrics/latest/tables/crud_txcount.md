### L1 — Transactions per semantic operation

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 2 | 1 |
| C2_create_with_attributes | 9 | 3 | 1 | 9 | 3 | 1 | 2 | 2 | 9 | 2 |
| U1_rotate_controller | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| U2_add_delegate | 1 | 1 | 1 | 1 | n/a | n/a | n/a | n/a | 1 | 1 |
| U3_set_attribute | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| U4_transfer_vehicle | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| U5_meta_tx | 1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 1 | n/a |
| D1_revoke_delegate | 1 | 1 | 1 | 1 | n/a | n/a | n/a | n/a | 1 | 1 |
| D2_revoke_attribute | 1 | n/a | n/a | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| D3_deactivate_identity | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| V1_issuer_key_anchor | 1 | 1 | 1 | 1 | n/a | 1 | 1 | n/a | 1 | 1 |
| V3_anchor_status | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 |
| V5_revoke_credential | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

_Run 2026-10-09T02-09-36Z_7a9a996 · commit 7a9a996 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
