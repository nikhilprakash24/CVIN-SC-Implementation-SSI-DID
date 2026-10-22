# XT-01 — Gas per operation as a multiple of ERC-1056

*X-SERIES · EXPLORATORY · CLAUDE-INITIATED, NOT AUTHOR-DIRECTED · not cited until promoted.* Source `4_comparison-framework/results/gas_benchmark.json` (#25). A multiple above 1 means dearer than ERC-1056. Operation definitions differ per standard (see #6), so a ratio describes the realisation, not the abstract operation.

| Standard | createIdentity | updateAttribute | addDelegateOrClaim | revoke | transferOwnership |
|---|---:|---:|---:|---:|---:|
| CVIN-Combined | 0.99× | 0.99× | 5.24× | 1.99× | 1.00× |
| ERC-1056 | 1.00× | 1.00× | 1.00× | 1.00× | 1.00× |
| ERC-1155 | 1.98× | 1.38× | 1.04× | 0.87× | 1.62× |
| LSP8 | 2.84× | 1.55× | n/a | 1.20× | 1.56× |
| MOBI-VID-V2 | 5.69× | 8.65× | 0.64× | 2.14× | 3.86× |
| ERC-725 | 9.88× | 3.86× | 2.19× | 1.24× | 0.55× |
| ERC-721 | 10.31× | 3.37× | 0.88× | 0.79× | 3.38× |
| ERC-4337 | 14.43× | 1.39× | 0.87× | 0.73× | 0.55× |
| ERC-735 | 29.20× | 2.19× | 5.34× | 2.06× | 0.56× |
| ERC-725xy | 31.96× | 1.41× | n/a | n/a | 0.56× |
