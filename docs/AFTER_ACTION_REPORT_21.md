# After-Action Report 21 — WM-2 C1: did:ethr Resolution Reads the Chain

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-15, after report 19 closed at `e18b06a` (CI 8/8 green on `9975a2e`). Report 20 is a parallel pass
on this branch (the Technical Data Package, `docs/tdp/`); this pass does not touch its files. Closed at the end of this
pass.
**Brief (the author, 2026-10-15):** continue; say when to switch the assistant model again and what the process would
be; perhaps later a handoff document and a summary of work for a check by the other model.

## 1. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| C1-a | `2_w3c-ssi-layer/did-resolution/did_resolver.py`: with a Web3 provider and a registry address for the DID's chain, `_resolve_ethr` reads the ERC-1056 `EthereumDIDRegistry` (owner, the `changed` linked list of `DIDOwnerChanged`, `DIDDelegateChanged`, `DIDAttributeChanged` events) and builds the document by the reference did:ethr rules. Validity is decided in chain time (the latest block's timestamp), as for D51. Without a provider it returns the default document of an identity with no registry events, as now, and says so in its docstring | SSI/W3C specialist | new tests on a real Hardhat node: owner change, delegate added and revoked, attribute (key, service) set and revoked, deactivation, an unconfigured chain. Each test must fail on the old code (shown) |
| C1-b | Re-run the internal checker (#4) and the external W3C DID test suite (#24) after the change; re-register what moves, keeping old values as history | measurement methodologist | the numbers in #4 and #24 are either unchanged (stated) or re-stated with their run |
| R | Records, grand run last, CI; the answer on switching models and the hand-off process | orchestrator | CI green on the closing commit |

**Defaults (the author may overturn).**
| # | Decision | Default |
|---|---|---|
| C1-d1 | Behaviour without a provider | keep the default document. It is the correct resolution of an identity with no registry events, and every current caller relies on it. The docstring states that it is not read from a chain |
| C1-d2 | Error for a chain with no configured registry | `notFound` with a message naming the chain. DID Core defines no network error, and the reference resolver's `unknownNetwork` is not a DID Core code |
| C1-d3 | Verification method type for owner and delegates | keep `EcdsaSecp256k1VerificationKey2019` with `blockchainAccountId`, the type the current documents and the suite run use |
| C1-d4 | Scope of #24's re-run | the suite's inputs are unchanged (they resolve without a provider), so the re-run checks for regressions. A chain-backed suite run is a separate, larger step, logged as a deferred item if it does not fit this pass |

## 2. Execution log
- 2026-10-15 — report opened.
