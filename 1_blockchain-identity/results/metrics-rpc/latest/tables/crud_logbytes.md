### L1 — Event-log bytes per operation

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | 224 | 352 | 416 | 224 | 288 | 544 | 256 | 800 | 288 | 512 |
| C2_create_with_attributes | 2,272 | 2,400 | 416 | 1,120 | 2,464 | 544 | 1,376 | 3,264 | 1,408 | 1,632 |
| U1_rotate_controller | 128 | 128 | 288 | 96 | 96 | 192 | 96 | 256 | 96 | 128 |
| U2_add_delegate | 192 | 192 | 128 | 128 | n/a | n/a | n/a | n/a | 96 | 192 |
| U3_set_attribute | 288 | 288 | 224 | 128 | 1,024 | 352 | 192 | 416 | 192 | 288 |
| U4_transfer_vehicle | 128 | 128 | 288 | 96 | 96 | 192 | 96 | 256 | 96 | 128 |
| U5_meta_tx | 288 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 704 | n/a |
| D1_revoke_delegate | 192 | 192 | 128 | 64 | n/a | n/a | n/a | n/a | 96 | 192 |
| D2_revoke_attribute | 288 | n/a | n/a | 64 | 512 | 352 | 128 | 288 | 128 | 288 |
| D3_deactivate_identity | 256 | 256 | 96 | 96 | 96 | 352 | 96 | 352 | 96 | 256 |
| V1_issuer_key_anchor | 192 | 192 | 416 | 128 | n/a | 128 | 160 | n/a | 160 | 192 |
| V3_anchor_status | 256 | 256 | 256 | 128 | 960 | 352 | 160 | 352 | 160 | 512 |
| V5_revoke_credential | 256 | 256 | 256 | 64 | 480 | 352 | 128 | 288 | 128 | 160 |

_Run 2026-10-04T22-09-23Z_c3b7cb1 · commit c3b7cb1 · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine · N=30_
