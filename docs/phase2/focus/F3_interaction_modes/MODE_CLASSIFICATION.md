# F3 Mode Classification of Phase 1's Chain Interactions

**Generated** by `docs/phase2/focus/F3_interaction_modes/classify_modes.py`; do not edit. **Author:** Nikhil Prakash (MASc, UBC ECE). **Taxonomy:** the orchestrator's default (A direct, B mediated (B-submit, B-serve), C detached), pending the author's decision P2-D7 (`docs/phase2/DECISIONS.md`).

## 1. Writes in the harness operation catalogue (run of record, M1-H)

| Operation | Mode | standards with this operation |
|---|---|---:|
| `C1_create_identity` | A | 10 of 10 |
| `C2_create_with_attributes` | A | 10 of 10 |
| `U1_rotate_controller` | A | 10 of 10 |
| `U2_add_delegate` | A | 6 of 10 |
| `U3_set_attribute` | A | 10 of 10 |
| `U4_transfer_vehicle` | A | 10 of 10 |
| `U5_meta_tx` | B-submit | 2 of 10 |
| `D1_revoke_delegate` | A | 6 of 10 |
| `D2_revoke_attribute` | A | 8 of 10 |
| `D3_deactivate_identity` | A | 10 of 10 |
| `V1_issuer_key_anchor` | A | 8 of 10 |
| `V3_anchor_status` | A | 10 of 10 |
| `V5_revoke_credential` | A | 10 of 10 |

Every harness write is Mode A except `U5_meta_tx`: ERC-1056 signed operations sent by a relayer and ERC-4337 UserOperations sent by a bundler (B-submit; gas in register #50). No write in Phase 1 is Mode C.

## 2. Reads in the harness (all Mode A: the harness's own node; RPC calls per read)

| Operation | fewest RPC calls | most RPC calls | standards |
|---|---:|---:|---:|
| `R1_resolve_owner` | 1 | 2 | 10 |
| `R2_resolve_by_vin` | 1 | 1 | 5 |
| `R3_resolve_document` | 2 | 12 | 10 |
| `R4_verify_delegate` | 1 | 2 | 6 |
| `V6_status_check` | 1 | 1 | 10 |

B-serve (a provider or indexer answers) was never measured: every read went to a local node (F3 capture §2). Mode C reads are the testbed's cached verification (register #27, #32, #37, #46), not harness operations.

## 3. Demo steps, classified by rule (grand runner log)

Source: `sandbox/grand/report/demos.json` (1752 steps). Rules: a step with gas is a mined write; a note or step naming a revert is an expected revert; a view-style function name is a read; a signing, credential, hashing or proof function is local computation (no chain contact). Rule-based and approximate: `unclassified` is reported, not hidden.

| Option | write (A, mined) | read (A, view call) | expected revert (A) | local computation (no chain contact) | unclassified | flag-based off-chain (D61) |
|---|---:|---:|---:|---:|---:|---:|
| cvin-combined | 63 | 54 | 18 | 7 | 10 | 3 |
| erc-1056-uport | 89 | 49 | 24 | 17 | 25 | 5 |
| erc-1056-vehicle | 44 | 28 | 22 | 14 | 7 | 13 |
| erc-1155 | 57 | 0 | 53 | 75 | 0 | 128 |
| erc-4337 | 28 | 23 | 27 | 11 | 20 | 81 |
| erc-721 | 60 | 68 | 46 | 2 | 46 | 162 |
| erc-725 | 38 | 19 | 9 | 1 | 7 | 0 |
| erc-725xy | 48 | 29 | 24 | 0 | 24 | 0 |
| erc-735 | 54 | 38 | 35 | 5 | 15 | 2 |
| lsp8 | 35 | 31 | 33 | 8 | 36 | 108 |
| mobi-vid | 77 | 54 | 79 | 20 | 46 | 199 |
| **all** | **593** | **393** | **370** | **160** | **236** | **701** |

### Cross-tabulation: the grand report's flag against the rule class (academic review AR-34)

| Flag in the grand report | write (A, mined) | read (A, view call) | expected revert (A) | local computation (no chain contact) | unclassified | total |
|---|---:|---:|---:|---:|---:|---:|
| mined | 593 | 0 | 0 | 0 | 0 | 593 |
| on-chain, no gas | 0 | 215 | 131 | 28 | 84 | 458 |
| flag: off-chain | 0 | 178 | 239 | 132 | 152 | 701 |

A signing step that serves a relayed write is classed here as local computation; it belongs to the write it serves, which the rules cannot see (a limit of rule-based classification; F3 plan step F3-S3 retires it).
