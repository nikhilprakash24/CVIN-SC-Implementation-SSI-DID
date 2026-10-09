# Analysis — 2026-10-09T02-09-36Z_7a9a996

_Run 2026-10-09T02-09-36Z_7a9a996 · computed from crud/lifecycle/scale/resolve.json · baseline ERC-1056_

### A1 — Cost relative to the ERC-1056 baseline (ratio; >1 = more expensive; n/a = no primitive; † = lifetime excludes n/a events)

| Quantity | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1_create_identity (× baseline) | 1 | 1.90 | 5.24 | 8.54 | 22.88 | 1.40 | 22.53 | 1.76 | 10.52 | 3.53 |
| C2_create_with_attributes (× baseline) | 1 | 0.64 | 1.56 | 4.08 | 6.97 | 0.29 | 5.35 | 1.02 | 3.14 | 2.77 |
| U3_set_attribute (× baseline) | 1 | 1.28 | 3.43 | 3.43 | 9.08 | 2.29 | 2.72 | 2.87 | 2.70 | 1.48 |
| U4_transfer_vehicle (× baseline) | 1 | 1.10 | 3.52 | 0.55 | 0.56 | 1.74 | 0.56 | 1.61 | 0.55 | 1.33 |
| V3_anchor_status (× baseline) | 1 | 1 | 4.21 | 3.54 | 10.20 | 2.36 | 1.47 | 1.62 | 1.45 | 8.67 |
| V5_revoke_credential (× baseline) | 1 | 1 | 3.76 | 1.30 | 2.76 | 0.99 | 0.82 | 0.96 | 0.80 | 2.79 |
| Lifetime gas (× baseline) | 1 | 0.98 | 2.58 | 3 | 5.52† | 1.2† | 2.81† | 1.44† | 2.11 | 2.44 |
| Zero→nonzero SSTOREs (× baseline) | 1 | 1.13 | 11.50 | 10.38 | 18.63 | 2.63 | 4.75 | 5.25 | 4.63 | 10.13 |
| Lifetime transactions (× baseline) | 1 | 0.77 | 0.65 | 1 | 0.73 | 0.69 | 0.62 | 0.58 | 0.96 | 0.73 |

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
| Lifetime gas ↓ | 1,050,809 | 1,025,469 | 2,706,685 | 3,155,103 | 5,797,549 | 1,261,575 | 2,956,507 | 1,508,413 | 2,221,290 | 2,559,537 |
| Zero→nonzero SSTOREs ↓ | 8 | 9 | 92 | 83 | 149 | 21 | 38 | 42 | 37 | 81 |
| R3 RPC calls at h=50 ↓ | 112 | 55 | 7 | 61 | 3 | 3 | 2 | 3 | 61 | 107 |
| R3 median ms after lifecycle ↓ | 16.70 | 13.45 | 6.65 | 15.96 | 10.42 | 3.57 | 4.33 | 4.70 | 9.75 | 13.30 |
| Core ops supported ↑ | 17 | 16 | 16 | 16 | 12 | 14 | 13 | 13 | 16 | 16 |
| O(1) on-chain credential check (view) ↑ | no | no | yes | yes | yes | yes | yes | yes | yes | yes |
| **Dominated by** (cost axes: lifetime, SSTOREs) | — | — | ERC-1056, ERC-1056 (wrapper), ERC-1155, LSP8, ERC-4337, CVIN-Combined | ERC-1056, ERC-1056 (wrapper), ERC-1155, ERC-725xy, LSP8, ERC-4337, CVIN-Combined | ERC-1056, ERC-1056 (wrapper), ERC-721, ERC-725, ERC-1155, ERC-725xy, LSP8, ERC-4337, CVIN-Combined | ERC-1056, ERC-1056 (wrapper) | ERC-1056, ERC-1056 (wrapper), ERC-1155, ERC-4337 | ERC-1056, ERC-1056 (wrapper), ERC-1155 | ERC-1056, ERC-1056 (wrapper), ERC-1155 | ERC-1056, ERC-1056 (wrapper), ERC-1155, LSP8, ERC-4337 |
| **Dominated by** (cost + read path) | — | — | ERC-1155, LSP8 | ERC-1056 (wrapper), ERC-1155, ERC-725xy, LSP8, ERC-4337 | ERC-1155, ERC-725xy, LSP8 | — | — | ERC-1155 | ERC-1155 | ERC-1155, LSP8, ERC-4337 |
| **Dominated by** (all six criteria) | — | — | — | ERC-4337 | ERC-1155, ERC-725xy, LSP8 | — | — | ERC-1155 | — | ERC-4337 |

### A4 — Frontier summary

- Pareto frontier on cost axes (lifetime gas, zero→nonzero SSTOREs): **ERC-1056, ERC-1056 (wrapper)**
- Pareto frontier on cost + read path: **ERC-1056, ERC-1056 (wrapper), ERC-1155, ERC-725xy**
- Pareto frontier on all six criteria: **ERC-1056, ERC-1056 (wrapper), ERC-721, ERC-1155, ERC-725xy, ERC-4337**
- Substrates whose lifetime total covers all 17 events (no n/a exclusions): ERC-1056, ERC-1056 (wrapper), ERC-721, ERC-725, ERC-4337, CVIN-Combined; the others' totals are lower bounds (†).
- Baseline ERC-1056 lifetime 1,050,809 gas; cheapest-to-dearest lifetime order: ERC-1056 (wrapper) (0.98×) < ERC-1056 (1×) < ERC-1155 (1.2×) < LSP8 (1.44×) < ERC-4337 (2.11×) < CVIN-Combined (2.44×) < ERC-721 (2.58×) < ERC-725xy (2.81×) < ERC-725 (3×) < ERC-735 (5.52×)

Criterion 'O(1) on-chain credential check' is a design property (a contract can verify a credential with one view call), not a measurement; it is the axis on which the CVIN-Combined hybrid and the storage-based substrates beat the event-log substrates. It is assigned per adapter in `analysis/analysis.js` and must be stated with the table.

### A5 — W3C DID Method Rubric: measured inputs per criterion (▲ = quantitative cell fed by this run)

| Rubric criterion | ERC-1056 | ERC-1056 (wrapper) | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.2.5 Offline creation (identity exists before any tx?) | yes (implicit identity; C1 only binds the VIN) | yes (implicit identity; C1 only binds the VIN) | no (mint / deploy / register tx) | no (mint / deploy / register tx) | no (mint / deploy / register tx) | no (mint / deploy / register tx) | no (mint / deploy / register tx) | no (mint / deploy / register tx) | no (mint / deploy / register tx) | yes (implicit identity; C1 only binds the VIN) |
| 3.2.7 ▲ Creation cost: C1 bind VIN (gas) | 76,830 | 145,684 (2 tx) | 402,567 | 656,480 (2 tx) | 1,757,881 | 107,729 | 1,730,753 (2 tx) | 135,544 | 808,431 (2 tx) | 271,402 |
| 3.2.7 ▲ Creation incl. VID-I attributes: C2 (gas) | 367,000 (9 tx) | 234,631 (3 tx) | 570,797 | 1,496,440 (9 tx) | 2,558,484 (3 tx) | 107,729 | 1,963,543 (2 tx) | 373,187 (2 tx) | 1,153,124 (9 tx) | 1,015,730 (2 tx) |
| 3.2.8 ▲ Update cost: U3 attribute (gas) | 35,024 | 44,677 | 120,061 | 119,996 | 318,054 | 80,131 | 95,334 | 100,574 | 94,651 | 51,742 |
| 3.2.8 ▲ Controller rotation: U1 (gas) | 51,754 | 57,188 | 179,470 | 28,390 | 28,812 | 89,805 | 28,834 | 83,380 | 28,539 | 68,847 |
| 3.2.8 ▲ Deletion: D3 deactivate (gas) | 34,230 | 43,809 | 27,689 | 23,091 | 28,596 | 39,565 | 23,182 | 43,044 | 28,323 | 51,016 |
| 3.3.2 ▲ Limited-resource resolution: R3 RPC calls at h=50 | 112 | 55 | 7 | 61 | 3 | 3 | 2 | 3 | 61 | 107 |
| 3.3.2 ▲ Resolution median ms after lifecycle | 16.70 | 13.45 | 6.65 | 15.96 | 10.42 | 3.57 | 4.33 | 4.70 | 9.75 | 13.30 |
| 3.4.1 Auditability: linked event chain vs state snapshot | full linked history (previousChange chain) | full linked history (previousChange chain) | events + current state (no chain pointer) | current state (events unlinked) | events + current state (no chain pointer) | current state (events unlinked) | current state (events unlinked) | current state (events unlinked) | current state (events unlinked) | full linked history (previousChange chain) |
| 3.4.7 Verification relationships: delegate keys | delegates with TTL | delegates with TTL | approval (no expiry) | delegates with TTL | none | none | none | none | recovery guardian only | delegates with TTL |
| 3.4.8 Relayed / signed operations (meta-tx) | yes | no | no | no | no | no | no | no | yes | no |
| 3.7.2 ▲ Incentive for many DIDs: lifetime gas × baseline | 1 | 0.98 | 2.58 | 3 | 5.52† | 1.2† | 2.81† | 1.44† | 2.11 | 2.44 |
