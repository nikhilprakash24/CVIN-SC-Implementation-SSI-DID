# Coverage Matrix — option × capability family

**Generated** by `docs/testing/build_register.py` from `sandbox/options/*/manifest.yaml` and `sandbox/grand/report/demos.json`. Do not edit; regenerate.

T = exercised by a passing demo · T* = passing demo that flags steps (DEFECT or OBSERVATION; see `sandbox/grand/report/demos.md`) · F = demo failing · G = implemented, no demo · N = not applicable (reason in the manifest) · +M = measured in the comparison.

| Option | creation | controller | keys-delegates | attributes | claims | revocation | signed-execution | lifecycle-history | authorisation-roles | token-economics | vin-linkage | did-resolution | offchain-creation | offchain-messaging |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline-centralized | G+M | G+M | N | N | G | G | N | G+M | G | N | G | N | G | N |
| baseline-pki | N | N | N | N | G | G | N | G | N | N | N | N | G | G+M |
| cvin-combined | N | T+M | T*+M | T* | T*+M | T+M | N | T | T* | N | T | T | T | N |
| erc-1056-uport | T | T* | T+M | T | N | T* | T | T | T* | N | T* | T | T | N |
| erc-1056-vehicle | T*+M | T* | T* | T | N | T+M | N | T+M | N | N | N | T+M | N | T* |
| erc-1155 | T+M | T* | N | T* | T*+M | T*+M | N | T | T*+M | T* | T | N | N | N |
| erc-4337 | T | T+M | T*+M | T | N | N | T | T | N | N | N | N | N | N |
| erc-721 | T+M | T | N | T | N | T* | N | T | T* | T+M | T | T | N | N |
| erc-725 | T | T* | T*+M | N | N | T* | T* | N | N | N | N | N | N | N |
| erc-725xy | T | T | N | T+M | N | T | T* | T | N | N | T* | N | N | N |
| erc-735 | T | T | N | N | T+M | T | N | T | T | N | T | N | N | N |
| lsp8 | T+M | T* | N | T | T* | T*+M | N | T | N | T | T* | N | N | N |
| mobi-vid | T*+M | T*+M | T*+M | T* | T*+M | T*+M | N | T+M | T* | N | T* | T*+M | N | T |

Totals: G 13, N 78, T 51, T* 40.
The two baselines (centralized registry, IEEE 1609.2-style PKI) are Python providers with no feature demos by design; their G cells are exercised by the Python suites and the experiments, not by demos.

Test register: 1212 TC entries in `docs/testing/test_register.yaml`.

**Manifest / demo mismatches** (shown as N above):
- erc-1056-vehicle / Claims / credentials: manifest says not applicable, but a passing demo exists

## Unit and Python test bodies — subject × property class

Count of registered tests (per-option contract tests, harness and stats tests, testbed Python tests, Phase 2 prototypes, promote-step tests), mapped by `docs/testing/unit_rules.yaml`; each register entry records the rule that mapped it. F functional · N negative · A adversarial · W conformance · G gas · L latency · S scale · D determinism · I integration. A test counted under two functions is counted once here.

| Subject | F | N | A | W | G | L | S | D | I | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline-centralized | · | · | · | · | · | · | · | · | 6 | 6 |
| baseline-pki | 5 | 7 | 5 | · | · | · | · | · | · | 17 |
| cv2x-erc1056 | 39 | 7 | 2 | · | · | · | · | · | · | 48 |
| cvin-combined | 18 | 13 | 2 | · | 1 | · | · | · | · | 34 |
| erc-1056-uport | 12 | 4 | · | · | 11 | · | · | · | · | 27 |
| erc-1056-vehicle | 15 | 12 | · | · | · | · | · | · | · | 27 |
| erc-1155 | 4 | 27 | · | · | 7 | · | · | · | · | 38 |
| erc-4337 | 9 | 6 | 1 | · | · | · | · | · | · | 16 |
| erc-721 | 10 | 11 | · | · | · | · | · | · | · | 21 |
| erc-725xy | 5 | 9 | · | · | 1 | · | · | · | · | 15 |
| erc-735 | 8 | 20 | 2 | · | 7 | · | · | · | · | 37 |
| harness-adapters | · | · | · | 13 | · | · | · | · | · | 13 |
| lsp8 | 4 | 14 | · | · | 6 | · | · | · | · | 24 |
| mobi-vid | 23 | 32 | 15 | 2 | 1 | · | · | · | · | 73 |
| phase2-backends | 6 | 2 | 1 | · | · | · | · | · | · | 9 |
| phase2-idtx | 8 | 4 | · | · | · | · | · | · | · | 12 |
| pipeline | 2 | · | · | · | · | 2 | · | 20 | · | 24 |
| v2v-path | 8 | 14 | 15 | · | · | · | · | · | · | 37 |
| vc-layer | · | · | 4 | · | · | · | · | · | · | 4 |
| zkp-agent | 8 | 5 | 2 | · | · | · | · | · | · | 15 |
| zkp-vin | 16 | 6 | 10 | · | · | · | · | · | · | 32 |
| **all** | 200 | 193 | 59 | 15 | 34 | 2 | 0 | 20 | 6 | 529 |
