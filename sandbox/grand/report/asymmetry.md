# Feature asymmetry — union table from the per-option manifests

M = measured in the comparison or an experiment · I = implemented but not used by the comparison · — = not applicable (reason in the manifest)

| Capability family | Baseline: centralized registry | Baseline: IEEE 1609.2-style PKI | CVIN-Combined | ERC-1056 / uPort-style | ERC-1056 / vehicle profile | ERC-1155 | ERC-4337 | ERC-721 | ERC-725 | ERC-725xy | ERC-735 | LSP8 | MOBI VID I + II |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Identity creation (explicit) | M | — | — | I | M | M | I | M | I | I | I | M | M |
| Ownership / controller change | M | — | M | I | I | I | M | I | I | I | I | I | M |
| Key / delegate management | — | — | M | M | I | — | M | — | M | — | — | — | M |
| Attributes / data store | — | — | I | I | I | I | I | I | — | M | — | I | I |
| Claims / credentials | I | I | M | — | — | M | — | — | — | — | M | I | M |
| Revocation / status | I | I | M | I | M | M | — | I | I | I | I | M | M |
| Delegated / signed (off-chain-authorised) execution | — | — | — | I | — | — | I | — | I | I | — | — | — |
| Lifecycle events / history | M | I | I | I | M | I | I | I | — | I | I | I | M |
| Authorisation / roles | I | — | I | I | — | I | — | I | — | — | I | — | I |
| Token economics (approvals, royalties, payments) | — | — | — | — | — | I | — | M | — | — | — | I | — |
| VIN linkage | I | — | I | I | — | I | — | I | — | I | I | I | I |
| DID / resolution helpers | — | — | I | I | M | — | — | I | — | — | — | — | M |
| Off-chain creation (identity exists before any transaction) | I | I | I | I | — | — | — | — | — | — | — | — | — |
| Message signing / verification (off-chain hot path) | — | M | — | — | I | — | — | — | — | — | — | — | I |

Options: 13 · families: 14 · cells: 182 · empty: 0 · unreviewed: 172/182

Per option — M / I / — counts:

- Baseline: centralized registry (in-process): M 3 · I 5 · — 6  (surface: {'functions': 0, 'events': 0, 'provider_methods': 15})
- Baseline: IEEE 1609.2-style PKI (in-process): M 1 · I 4 · — 9  (surface: {'functions': 0, 'events': 0, 'provider_methods': 12})
- CVIN-Combined (ERC-1056 + ERC-735 hybrid): M 4 · I 6 · — 4  (surface: {'functions': 18, 'events': 6, 'provider_methods': 0})
- ERC-1056 / uPort-style: M 1 · I 10 · — 3  (surface: {'functions': 49, 'events': 6, 'provider_methods': 0})
- ERC-1056 / vehicle profile: M 4 · I 4 · — 6  (surface: {'functions': 17, 'events': 4, 'provider_methods': 15})
- ERC-1155: M 3 · I 6 · — 5  (surface: {'functions': 34, 'events': 12, 'provider_methods': 0})
- ERC-4337: M 2 · I 4 · — 8  (surface: {'functions': 13, 'events': 7, 'provider_methods': 0})
- ERC-721: M 2 · I 7 · — 5  (surface: {'functions': 52, 'events': 15, 'provider_methods': 0})
- ERC-725: M 1 · I 4 · — 9  (surface: {'functions': 9, 'events': 4, 'provider_methods': 0})
- ERC-725xy: M 1 · I 6 · — 7  (surface: {'functions': 25, 'events': 5, 'provider_methods': 0})
- ERC-735: M 1 · I 6 · — 7  (surface: {'functions': 17, 'events': 8, 'provider_methods': 0})
- LSP8: M 2 · I 6 · — 6  (surface: {'functions': 21, 'events': 6, 'provider_methods': 0})
- MOBI VID I + II (application profile): M 7 · I 4 · — 3  (surface: {'functions': 57, 'events': 13, 'provider_methods': 11})
