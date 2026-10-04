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

_Run 2026-10-04T09-50-29Z_0eef6af · computed from crud/lifecycle/scale/resolve.json · baseline ERC-1056_
