# Analysis — 2026-10-04T09-50-29Z_0eef6af

_Run 2026-10-04T09-50-29Z_0eef6af · computed from crud/lifecycle/scale/resolve.json · baseline ERC-1056_

### A1 — Cost relative to the ERC-1056 baseline (ratio; >1 = more expensive; n/a = no primitive; † = lifetime excludes n/a events)

| Quantity | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity (× baseline) | 1 | 1.90 | 5.21 | 8.55 | 20 | 1.35 | 22.53 | 1.73 | 10.53 | 3.48 |
| C2_create_with_attributes (× baseline) | 1 | 0.64 | 1.55 | 4.08 | 6.23 | 0.28 | 5.35 | 1.01 | 3.14 | 2.74 |
| U3_set_attribute (× baseline) | 1 | 1.28 | 3.43 | 3.43 | 9.07 | 1.63 | 2.72 | 2.87 | 2.70 | 1.48 |
| U4_transfer_vehicle (× baseline) | 1 | 1.10 | 3.52 | 0.55 | 0.56 | 1.62 | 0.56 | 1.61 | 0.55 | 1.33 |
| V3_anchor_status (× baseline) | 1 | 1 | 4.21 | 3.54 | 8.69 | 1.70 | 1.47 | 1.62 | 1.45 | 8.54 |
| V5_revoke_credential (× baseline) | 1 | 1 | 3.76 | 1.30 | 2.76 | 0.93 | 0.82 | 0.96 | 0.80 | 2.69 |
| Lifetime gas (× baseline) | 1 | 0.98 | 2.57 | 3 | 5.11† | 1.1† | 2.81† | 1.43† | 2.11 | 2.41 |
| Zero→nonzero SSTOREs (× baseline) | 1 | 1.13 | 11.50 | 10.38 | 18.13 | 2.25 | 4.75 | 5.25 | 4.63 | 10.13 |
| Lifetime transactions (× baseline) | 1 | 0.77 | 0.65 | 1 | 0.58 | 0.81 | 0.62 | 0.58 | 0.96 | 0.73 |

### A2 — Capability matrix: ✓ primitive present, ✗ none (reportable finding)

| Operation | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C2_create_with_attributes | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R1_resolve_owner | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R2_resolve_by_vin | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| R3_resolve_document | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R4_verify_delegate | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| U1_rotate_controller | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U2_add_delegate | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| U3_set_attribute | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U4_transfer_vehicle | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U5_meta_tx (optional) | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| D1_revoke_delegate | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| D2_revoke_attribute | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| D3_deactivate_identity | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| V1_issuer_key_anchor | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| V3_anchor_status | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| V5_revoke_credential | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| V6_status_check | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Core ops supported** | 17/17 | 16/17 | 16/17 | 16/17 | 12/17 | 14/17 | 13/17 | 13/17 | 16/17 | 16/17 |
| Missing primitives | — | U5 D2 | U5 D2 | R2 U5 | R2 R4 U2 U5 D1 V1 | R4 U2 U5 D1 | R2 R4 U2 U5 D1 | R4 U2 U5 D1 V1 | R2 | R2 U5 |

### A3 — H5 dominance analysis: a substrate is dominated if another is at least as good on every listed criterion and better on one. '—' = on the Pareto frontier for that criterion set

| Criterion | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Lifetime gas ↓ | 1,050,787 | 1,025,381 | 2,701,239 | 3,155,103 | 5,369,010 | 1,150,981 | 2,956,507 | 1,505,258 | 2,221,290 | 2,533,978 |
| Zero→nonzero SSTOREs ↓ | 8 | 9 | 92 | 83 | 145 | 18 | 38 | 42 | 37 | 81 |
| R3 RPC calls at h=50 ↓ | 112 | 55 | 7 | 61 | 3 | 3 | 2 | 3 | 61 | 107 |
| R3 median ms after lifecycle ↓ | 20.31 | 12.23 | 7.00 | 15.32 | 7.62 | 2.63 | 4.25 | 3.89 | 8.33 | 12.80 |
| Core ops supported ↑ | 17 | 16 | 16 | 16 | 12 | 14 | 13 | 13 | 16 | 16 |
| O(1) on-chain credential check (view) ↑ | no | no | yes | yes | yes | yes | yes | yes | yes | yes |
| **Dominated by** (cost axes: lifetime, SSTOREs) | — | — | ERC-1056, ERC-1056 (wrapper), ERC-1155, LSP8, ERC-4337, CVIN-Combined | ERC-1056, ERC-1056 (wrapper), ERC-1155, ERC-725xy, LSP8, ERC-4337, CVIN-Combined | ERC-1056, ERC-1056 (wrapper), ERC-721, ERC-725, ERC-1155, ERC-725xy, LSP8, ERC-4337, CVIN-Combined | ERC-1056, ERC-1056 (wrapper) | ERC-1056, ERC-1056 (wrapper), ERC-1155, ERC-4337 | ERC-1056, ERC-1056 (wrapper), ERC-1155 | ERC-1056, ERC-1056 (wrapper), ERC-1155 | ERC-1056, ERC-1056 (wrapper), ERC-1155, LSP8, ERC-4337 |
| **Dominated by** (cost + read path) | — | — | ERC-1155, LSP8 | ERC-1056 (wrapper), ERC-1155, ERC-725xy, LSP8, ERC-4337 | ERC-1155, ERC-725xy, LSP8 | — | — | ERC-1155 | ERC-1155 | ERC-1056 (wrapper), ERC-1155, LSP8, ERC-4337 |
| **Dominated by** (all six criteria) | — | — | — | ERC-4337 | ERC-1155, ERC-725xy, LSP8 | — | — | ERC-1155 | — | ERC-4337 |

### A4 — Frontier summary

- Pareto frontier on cost axes (lifetime gas, zero→nonzero SSTOREs): **ERC-1056, ERC-1056 (wrapper)**
- Pareto frontier on cost + read path: **ERC-1056, ERC-1056 (wrapper), ERC-1155, ERC-725xy**
- Pareto frontier on all six criteria: **ERC-1056, ERC-1056 (wrapper), ERC-721, ERC-1155, ERC-725xy, ERC-4337**
- Substrates whose lifetime total covers all 17 events (no n/a exclusions): ERC-1056, ERC-1056 (wrapper), ERC-721, ERC-725, ERC-4337, CVIN-Combined; the others' totals are lower bounds (†).
- Baseline ERC-1056 lifetime 1,050,787 gas; cheapest-to-dearest lifetime order: ERC-1056 (wrapper) (0.98×) < ERC-1056 (1×) < ERC-1155 (1.1×) < LSP8 (1.43×) < ERC-4337 (2.11×) < CVIN-Combined (2.41×) < ERC-721 (2.57×) < ERC-725xy (2.81×) < ERC-725 (3×) < ERC-735 (5.11×)

Criterion 'O(1) on-chain credential check' is a design property (a contract can verify a credential with one view call), not a measurement; it is the axis on which the CVIN-Combined hybrid and the storage-based substrates beat the event-log substrates. It is assigned per adapter in `analysis/analysis.js` and must be stated with the table.
