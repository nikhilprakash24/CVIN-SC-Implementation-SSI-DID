# Coverage Matrix — option × capability family

**Generated** by `docs/testing/build_register.py` from `sandbox/options/*/manifest.yaml` and `sandbox/grand/report/demos.json`. Do not edit; regenerate.

T = exercised by a passing demo · F = demo failing · G = implemented, no demo · N = not applicable (reason in the manifest) · +M = measured in the comparison.

| Option | creation | controller | keys-delegates | attributes | claims | revocation | signed-execution | lifecycle-history | authorisation-roles | token-economics | vin-linkage | did-resolution | offchain-creation | offchain-messaging |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline-centralized | G+M | G+M | N | N | G | G | N | G+M | G | N | G | N | G | N |
| baseline-pki | N | N | N | N | G | G | N | G | N | N | N | N | G | G+M |
| cvin-combined | N | T+M | T+M | T | T+M | T+M | N | T | T | N | T | T | T | N |
| erc-1056-uport | T | T | T+M | T | N | T | T | T | T | N | T | T | T | N |
| erc-1056-vehicle | T+M | T | T | T | N | T+M | N | T+M | N | N | N | T+M | N | T |
| erc-1155 | T+M | T | N | T | T+M | T+M | N | T | T+M | T | T | N | N | N |
| erc-4337 | T | T+M | T+M | T | N | N | T | T | N | N | N | N | N | N |
| erc-721 | T+M | T | N | T | N | T | N | T | T | T+M | T | T | N | N |
| erc-725 | T | T | T+M | N | N | T | T | N | N | N | N | N | N | N |
| erc-725xy | T | T | N | T+M | N | T | T | T | N | N | T | N | N | N |
| erc-735 | T | T | N | N | T+M | T | N | T | T | N | T | N | N | N |
| lsp8 | T+M | T | N | T | T | T+M | N | T | N | T | T | N | N | N |
| mobi-vid | T+M | T+M | T+M | T | T+M | T+M | N | T+M | T | N | T | T+M | N | T |

Totals: G 13, N 78, T 91.
The two baselines (centralized registry, IEEE 1609.2-style PKI) are Python providers with no feature demos by design; their G cells are exercised by the Python suites and the experiments, not by demos.

Test register: 305 TC entries in `docs/testing/test_register.yaml`.
