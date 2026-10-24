# Stream H-R: on-chain DID resolution (did:ethr, did:mobi)

> *Lineage merge note (2026-10-21, PR #3): register rows from the clone lineage were renumbered on the merged trunk (the optional on-chain resolve-latency row proposed here as #40 was never entered; the clone lineage's #40 is #53).*


**Date:** 2026-10-15. **Base:** `ffb71b0`.
**Full suite write-up:** `docs/conformance/W3C_DID_TEST_SUITE.md` section 10.
**Scope:** AAR-06 row H-R. Make `_resolve_ethr` read the ERC-1056 registry
and fail closed; replace the did:mobi placeholder or declare it out of scope;
re-measure register rows #24 and #4.

## Design (`2_w3c-ssi-layer/did-resolution/did_resolver.py`)

**Modes.**

* **Offline** (the default, `DIDResolver()`): unchanged documents. Every
  success now carries `didResolutionMetadata.cvinResolutionMode:
  "offline-synthesized"`.
* **On-chain**: `DIDResolver(rpc_url=…, ethr_registry=…, mobi_registry=…,
  chain_id=None)`. Successes are labelled `erc1056-registry` or
  `mobi-vid-registry`.
* Passing an RPC without a registry, or a registry without an RPC, raises
  `ValueError`.

**Why a non-standard property.** DID Core 7.1.2 allows resolution-metadata
properties beyond the common ones. A clearly prefixed name cannot be
mistaken for a registered term; a reused `method`-style property could be.
The external suite generated an identical inventory with identical results
with the property present (W3C §10.2), so it is not penalised.

**did:ethr (ERC-1056).**

* All reads are pinned to one head block. `changed(identity)` gives the last
  change block. The resolver then walks back one `eth_getLogs` per block,
  following the smallest `previousChange` that is strictly older than the
  block. That rule handles two transactions in one block and MOBI's
  self-referencing birth event. The walk is capped at 10 000 blocks.
* Events are replayed forward with ethr-did-resolver semantics:
  - the entry for each (type, delegate) or (name, value) keeps its position
    and takes the running `#delegate-N` / `#service-N` number, so ids stay
    stable when an unrelated entry is revoked;
  - an entry with `validTo ≤ head.timestamp` is removed (ethr-did-resolver
    uses `<`; we follow the on-chain `validDelegate`);
  - `DIDOwnerChanged` to 0x0, or MOBI's `DIDRevoked`, sets
    `deactivated: true` and stops the replay.
* Document mapping:
  - `#controller` (EcdsaSecp256k1RecoveryMethod2020, `blockchainAccountId`
    = current owner); doc-level `controller` = the owner's did:ethr;
  - `#controllerKey` for a public-key DID whose owner is unchanged;
  - veriKey delegates go to assertionMethod; sigAuth delegates go to
    assertionMethod and authentication;
  - `did/pub/<algo>/<veriKey|sigAuth|enc>/<hex|base58|base64>` maps via
    ethr-did-resolver's legacy type map; `enc` goes to keyAgreement;
  - `did/svc/<type>` becomes a service (JSON or string endpoint).
* `versionId` = the latest change block; `updated` = that block's timestamp.
* **Fail closed.** These all return an error with `didDocument: null` and
  empty document metadata, never a document:
  - RPC failure, or no contract at the registry address → `internalError`;
  - a replayed owner that disagrees with `identityOwner()` → `internalError`;
  - a broken chain → `internalError`;
  - a configured `chain_id` the node does not report → `internalError`;
  - a DID on another chain → `notFound` (the DID Resolution meaning:
    "unable to find the DID document").
* On-chain results are cached only when `cache_ttl_s` is set.

**did:mobi: option (a), on-chain only.** The method-specific id is the
32-byte salted VIN hash (`birth_certificate.salted_vin_hash`), which the
registry is keyed by. Resolution:

1. `lookupByVINHash` gives the vehicle (0x0 → `notFound`).
2. `getVehicleDID` must name that vehicle on this chain (else
   `internalError`).
3. The vehicle's ERC-1056 state in the MOBI registry is replayed as above.
   The controller is the current owner (`firstOwner` after birth, moved by
   `transferVehicleOwnership`), and `alsoKnownAs` is the did:ethr.
4. A raw VIN is rejected with `invalidDid`, and the error message does not
   echo it.
5. No VIN appears in any output. The tests assert this.

(a) was clean because MOBIVIDRegistry *is* an ERC-1056 registry, so the
reader serves both methods. One difference: MOBI's `revokeDelegate` emits
`validTo = now` instead of 0, and `validTo ≤ now` covers it.

**Not done: the offline `did:mobi:<VIN>` placeholder stays (labelled).**
Removing it is the honest end state, but it trips the STOP rule:

* the internal checker would go from 94.3 % to **84.1 %**, below the floor
  of 93.0 (scratch run, not committed). The 3.1, 5.1.1, 5.4, 7.1.2 and
  7.1.3 checks resolve `did:mobi:<VIN>`;
* the unchanged suite generator asserts that this vector succeeds.

**Author decision:** retire the offline did:mobi vector in the checker
(`dids["mobi"]`) and the generator (`METHODS["mobi"]`), then make offline
did:mobi return `methodNotSupported`.

**Limitations (disclosed).**

* `EthereumDIDRegistry.changeOwner(0x0)` makes `identityOwner()` return the
  identity again, so on-chain the identity key can re-take control. The
  resolver treats the deactivation as permanent, as ethr-did-resolver does.
* Delegate types and attribute names are decoded as right-padded ASCII
  bytes32 (ethr-did-resolver). The contract NatSpec's `keccak256("veriKey")`
  form is ignored.
* Attributes with an unknown encoding are skipped. ethr-did-resolver would
  emit `value`.
* There is no `versionId` / `versionTime` historical resolution.
* did:nft and did:key stay offline-synthesised (and labelled) in on-chain
  mode too.

**Callers that had to adapt:** none. Checked:

* `w3c_compliance_checker.py`: offline, the score is unchanged;
* `vc_verifier._document_keys`: reads `blockchainAccountId`, which the
  on-chain documents carry;
* `attack_scenarios.py`: its "did:mobi:<VIN> exists" note is still true
  offline;
* the CI job "All Python suites": it already compiles `1_blockchain-identity`
  and the new tests start their own node on 8560.

## Tests (`2_w3c-ssi-layer/did-resolution/tests/`)

| File | Tests | Fail on `ffb71b0` |
|---|---|---|
| `test_did_resolver_onchain_ethr.py` | 22 | 21 (one guard: errors carry no mode) |
| `test_did_resolver_onchain_mobi.py` | 12 | 12 |

**ethr cases:**

* an untouched identity controls itself;
* `changeOwner` moves the controller and sets `versionId` / `updated`;
* sigAuth `addDelegate` → it appears in authentication; `revokeDelegate` →
  it is gone;
* a veriKey delegate is assertion-only;
* ids are stable after an unrelated revoke;
* `setAttribute` veriKey and `did/svc` → a key and a service appear;
* sigAuth attribute then `revokeAttribute`;
* expiry (`evm_increaseTime`);
* `changeOwner(0x0)` → deactivated;
* a public-key DID gets `#controllerKey`;
* the cache does not hide a change;
* wrong chain → `notFound`; configured chain ≠ node → `internalError`;
* RPC down → `internalError` from `resolve` and from
  `resolve_representation` (empty stream);
* no contract at the address → `internalError`;
* half-configuration → `ValueError`; a mobi-only resolver gives
  `methodNotSupported` for did:ethr;
* offline label on ethr, nft and key.

**mobi cases:**

* birth → controller is firstOwner, `alsoKnownAs` is the did:ethr;
* `transferVehicleOwnership`;
* delegate add and revoke;
* `revokeIdentity` → deactivated;
* the same controller as did:ethr resolved against the MOBI registry;
* unknown hash → `notFound`; raw VIN → `invalidDid` without echo;
* RPC down, and no contract at the address;
* an ethr-only resolver gives `methodNotSupported`;
* offline label; `create_did(vin_hash=)`.

**Node handling.** The node is started once per process by
`resolver_chain_helpers.node_url()` (port `$DID_RESOLVER_TEST_RPC_PORT`,
default 8560) and stopped by process group at exit. The tests skip only when
no node can be started, the same pattern as the MOBI suite. It is not a
`conftest.py`: a first version used one, and it shadowed
`cv2x-testbed/tests`' `from conftest import deploy` in the combined CI
invocation (6 collection errors, fixed in `d902864`).

**Results:**

* `python3 -m pytest 2_w3c-ssi-layer -q`: **260 passed, 0 skipped**. The
  base gave 226 passed after a compile, 199 passed + 27 skipped without
  artifacts.
* `pytest 2_w3c-ssi-layer cv2x-testbed/tests` collects 392 tests with no
  errors.

## External suite (939b31d, fresh clone): old → new

| Set | 2026-10-04b | 2026-10-15 |
|---|---|---|
| Offline (register #24, generator unchanged) | 335/336 | **335/336**: identical test by test (335 pass→pass, 1 R5′ fail→fail) |
| On-chain (new, separate) | – | **311/311**: identifier 2/2, core 59/59, production 32/32, consumption 2/2, resolution 216/216 (ethr 117/117, mobi 99/99), incl. notFound and deactivated tests |
| Control | 347/347 | 347/347 |

## Internal checker

The score is **94.3 % before and 94.3 % after** (41 PASS, 1 PARTIAL,
2 FAIL). The checker was not changed. In a hypothetical run with offline
did:mobi made an error (not committed) it would be 84.1 %.

## Proposed register text (`docs/MEASUREMENT_CONDITIONS.md`, not edited)

**#24, append to Status:**

> Re-run 2026-10-15 (stream H-R, `d902864`): offline set **335/336**, test
> by test identical to 2026-10-04b. Inputs differ only in timestamps and the
> new non-standard `cvinResolutionMode: "offline-synthesized"` property,
> which the suite does not penalise. Control 347/347. A separate on-chain set
> (`generate_implementations_onchain.py`, Hardhat: ERC-1056 + MOBIVIDRegistryV2,
> incl. notFound and deactivated executions) scores **311/311** (resolution
> 216/216). It is a different inventory and is not to be summed with or
> compared to 335/336 as a percentage. Raw: `docs/conformance/reports/**/*-2026-10-15.*`;
> W3C_DID_TEST_SUITE.md §10.

**#4, append to Status:**

> 2026-10-15 (H-R): unchanged at 94.3 %. The checker still runs the offline
> resolver only, so it measures the synthesised documents, now labelled
> `offline-synthesized`. Its did:mobi vector is the raw-VIN placeholder:
> retiring it would read 84.1 % without a checker change.

**#40 (new, optional):** on-chain `resolve()` latency, local Hardhat over HTTP,
web3.py 8.0.0, n=300 after 20 warm-up resolutions, shared 4-core host (other
agents' nodes running), cache off:

* did:ethr with 5 change blocks: median 58.5 ms, p95 75.6 ms;
* untouched did:ethr: median 28.6 ms, p95 41.3 ms;
* did:mobi (birth, 1 change block): median 53.7 ms, p95 74.1 ms;
* offline: median 0.08 ms.

Status **S** (single run, shared host; script `/tmp/hr_scratch/latency.py`,
not committed). Confirm on a quiet host before citing.

## Proposed checklist changes (`docs/MOBI_VID_CHECKLIST.md`, not edited)

* **VID-R1:** Partial → **Met in on-chain mode.** Finding (b) is fixed:
  with a registry configured, `_resolve_ethr` replays ERC-1056 and the
  vehicle's document names the current owner (`firstOwner` after
  `registerVehicleBirth`) as controller. `getVehicleDID`'s output resolves,
  and is used and cross-checked by did:mobi resolution. Tested in
  `test_did_resolver_onchain_{ethr,mobi}.py`. Caveat: offline mode (the
  default) still synthesises the document, but now says so in metadata.
* **did:mobi placeholder (`RES:_resolve_mobi`):** Open → **Partly resolved.**
  On-chain `did:mobi:<salted VIN hash>` resolves through `lookupByVINHash` →
  `getVehicleDID` → ERC-1056 state, with no VIN in the DID or the output and
  no placeholder key or endpoints. The offline `did:mobi:<VIN>` placeholder
  remains, labelled `offline-synthesized`, pending the author decision above
  (checker and generator vectors).

## Commits (local, not pushed)

* `f61b3c3`: on-chain did:ethr, offline label, ethr tests.
* `d902864`: did:mobi via the MOBI registry, mobi tests, node helper.
* `b170707`: offline re-run inputs and reports, on-chain generator, set and
  reports, runner `onchain` mode.
* The next commit: W3C §10 and this file.
