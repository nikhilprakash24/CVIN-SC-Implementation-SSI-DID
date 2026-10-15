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
- **C1-a, code.** `did_resolver.py`:
  - **Chain path.** `_resolve_ethr` calls a new `_resolve_ethr_chain` when the resolver has a provider. That method
    checks the provider's chain against the DID's, reads `identityOwner` and `changed`, and walks the identity's
    events block by block through `previousChange`. For each delegate and each attribute, the latest event decides
    its state. An entry counts only while `validTo` is later than the latest block's timestamp (chain time).
  - **Document.** Delegates become `veriKey` / `sigAuth` methods. `did/pub/<alg>/<purpose>/<hex|base58>` attributes
    become keys, and `did/svc/<type>` attributes become services. `versionId` and `updated` come from the last
    change.
  - **Constructor.** It takes `registries` (chain id to address). With a provider and no explicit TTL, the resolver
    does not cache, so it cannot serve a document from before an owner change or a revocation.
- **Two errors of mine, caught by the tests.**
  - The first draft read deactivation from `identityOwner`. That call returns the identity itself when the stored
    owner is 0x0, so deactivation never showed. Deactivation is now read from the latest `DIDOwnerChanged` event, as
    the reference resolver does.
  - The MOBI registry adds a `DIDRevoked` event. An undecoded event would have stopped the `previousChange` walk
    early, silently dropping older events. It is now decoded and read as deactivation, since revocation is terminal
    in that contract.
- **C1-a, tests.**
  - `test_did_resolver_chain.py` has 9 tests on a real node. It uses `CV2X_TEST_RPC_URL` when set, or else starts
    its own node on 8563, because the L3 + L4 job fails on any skip.
  - Against the old resolver on a fresh node, 7 fail (owner change, delegates, attributes, expiry, deactivation,
    unconfigured chain, cache) and 2 pass. Those two pin behaviour that must not change: an identity without events,
    and the no-provider document.
  - Two MOBI tests were added. One checks that a born vehicle resolves from the chain to its first owner (VID-R1 (b),
    review-02 FOLLOWUP_FE finding 2). The other checks that a revoked identity resolves as deactivated; it fails with
    the `DIDRevoked` rule removed (shown). Both fail on the old code only because it has no `registries` parameter, so
    of the 11 new tests, 9 fail on the old code and 7 of those on behaviour.
- **A slip in the regression proof, caught.** My first old-versus-new run reported the old resolver passing all 9.
  An earlier attempt had been aborted, and its shell was killed by `pkill -f`, which matched its own command line.
  It had already copied the new file in, so the "old" run tested new code. I re-ran with the old file written from
  git, checked by a grep, and caches removed: 7 failed. Processes are now stopped by checking their own argv.
- **C1-b.**
  - Checker (#4): 41 PASS, 1 PARTIAL, 2 FAIL of 44, so 94.3%, unchanged.
  - Suite (#24): the regenerated inputs equal the committed ones up to timestamps, in 6 of 6 files. The suite reads
    only these files, so its result cannot move, and I did not re-run it on identical inputs. A suite run on
    chain-backed DIDs, and the chain-path resolution latency, are deferred as **N-24**.
  - #4 and #24 have a dated note. The MOBI checklist's VID-R1 now reads "met with a provider; partial without".
  - Python layers: 342 passed (331 + 9 + 2), no skips. A first count of 340 was taken before the two MOBI tests.
- **Coordination with report 20 (parallel pass).** After rebasing onto its TDP generators (`4699f21`), its
  `make_vcrm.py --check` failed with "pending step C1 is marked done in PLAN_WM-2; remove it". That is its guard
  working. I made the one change it asked for in `docs/tdp/requirements.yaml` STD-01: `pending: []`, with its limit
  sentence updated to say the checker still resolves without a provider. I regenerated TDP-002 and TDP-005 with its
  own generator; its three checks pass. No other report-20 file was touched.
