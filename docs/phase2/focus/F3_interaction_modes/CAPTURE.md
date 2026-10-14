# F3 Capture — Modes of Communication with the Chain in Phase 1

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F3, capture; research agent draft, verified by the orchestrator)
**Binds:** docs/phase2/README.md

## Summary

1. Phase 1 never defines "three modes" of chain communication. It evidences at least four independent dimensions: transport (in-process EVM, localhost HTTP JSON-RPC, public provider), write authorisation (EOA transaction, relayed signed operation, ERC-4337 UserOperation), read path (state read, event-log history reconstruction, cache or credential with no chain contact) and the grand runner's three-way step classification (mined transaction, on-chain call with no gas, off-chain).
2. Every measured chain interaction is local: M1 or M1-H in-process, or a localhost Hardhat node over HTTP (#21, #32, #33, #37, and #39, which is status U). No public provider (M2, Sepolia) and no WebSocket or subscription path was run or implemented; no indexer exists.
3. Relayed writes exist in exactly two substrates: ERC-1056 / uPort-style (`*Signed` functions) and ERC-4337 (`handleOp`). Measured overhead over the direct write: ERC-1056 U5 62,646 vs U3 35,024 gas (+27,622); ERC-4337 U5 141,767 vs U3 94,651 (+47,116; nine-standard table +46,830, #25). The relayer is always a trusted local role wallet.
4. Reads split three ways by cost: one `eth_call` (R1, 1 RPC), event-log replay that grows with history (ERC-1056 R3: 14 / 32 / 112 RPC at h = 1 / 10 / 50, #31), and in-process cached verification with no chain contact (V2V warm 0.153 ms, M0, #27).
5. Freshness-k (#32, #37, #46) is a dial between "chain on every message" (k = 1) and "never" (k = ∞), so on the read side the evidence describes a continuum, not three discrete modes. Revocation staleness is bounded by k − 1 messages.
6. The recorded security consequences are D52 (ERC-1056 signed digest lacks the chain id; the minimal EntryPoint binds it), D51 (cached key validity decided by the verifier's wall clock beyond 900 s), relayer linkability (#38 B2) and D15 (EntryPoint nonce rollback).
7. The C-V2X "Mode 3 / Mode 4" is a radio resource-allocation notion. It matters to F3 only because a vehicle on sidelink alone has no path to any chain node; in the testbed Mode 3 is a placeholder and no measurement uses a radio.
8. Four candidate three-mode taxonomies are listed in §7, including the orchestrator's direct / mediated / anchored-offline proposal, which fits the evidence on writes and on the V2V hot path but has an unmeasured read side for "mediated" and a thin, partly contradictory write side for "anchored-offline".

Sources of record: claim register `docs/MEASUREMENT_CONDITIONS.md` (rows cited as #n), harness run `2026-10-09T02-09-36Z_7a9a996` (`1_blockchain-identity/results/metrics/latest/meta.json`, `dirty: false`, Hardhat 2.28.6), grand report `sandbox/grand/report/` (generated at `b02ea17`, committed in `4b2b30c`). Every `path:line` refers to commit `dc1ef41`; at the time of writing the working tree carried uncommitted edits by the WM-2 C0 stream to `cv2x-testbed/identity/erc1056_provider.py`, `cv2x-testbed/sumo/infrastructure_layer.py` and `cv2x-testbed/sumo/sumo_identity_integration.py` (D51 fix, verifier v3), so line numbers in those files may move.

## 1. Dimension (a): transport and connection

### 1.1 What Phase 1 implements

| Transport | Implemented where | Condition tag | Status |
|---|---|---|---|
| In-process EVM (Hardhat Network, EIP-1193 provider inside the Node process; still JSON-RPC methods, no socket) | `npx hardhat test`, `npm run metrics` default; `docs/MEASUREMENT_CONDITIONS.md:23-24`, §5.A line 190 ("in-process (no HTTP)") | M1, M1-H | measured (all gas rows) |
| Localhost Hardhat node over HTTP JSON-RPC, JS client | `1_blockchain-identity/hardhat.config.js:66` (`localhost`, `http://127.0.0.1:8545`); harness `--network localhost` | M1-H/HTTP (`MEASUREMENT_CONDITIONS.md:25`) | measured once, pre-merge contracts (#39, **U**) |
| Localhost node over HTTP, Python web3 client | `cv2x-testbed/identity/erc1056_provider.py:63,72` (`Web3.HTTPProvider`, default `http://127.0.0.1:8545`); `cv2x-testbed/identity/mobi_vid_provider.py:56,65`; `cv2x-testbed/identity/lifecycle_backends.py:113,122` | M1 (testbed rows) | measured (#21, #22, #32, #33, #37) |
| Public provider (Sepolia, chain id 11155111) | `1_blockchain-identity/hardhat.config.js:68-70` (`SEPOLIA_RPC_URL`, `PRIVATE_KEY` from env); `1_blockchain-identity/scripts/validate_sepolia.js` (writes `4_comparison-framework/results/sepolia_validation.json`) | M2 (`MEASUREMENT_CONDITIONS.md:26`) | **not run**: no `sepolia_validation.json` in `4_comparison-framework/results/`; idea "Public-chain witness and rollup economics" (`docs/phase2/ideas.yaml:47-53`) waits on author decision N-11 |
| Other configured networks (Goerli, mainnet, Polygon) | `hardhat.config.js:74-85` | none | configured only |
| WebSocket, `eth_subscribe`, contract event listeners, filters | none found (search of `*.py`, `*.js`, `*.ts` outside `node_modules` for websocket, `ws://`, `eth_subscribe`, `contract.on(`, `create_filter`) | none | **not implemented** |
| Indexer (subgraph or equivalent) | none; only demo notes say "an indexer can build the identity from this log alone" (`sandbox/options/erc-721/demos/creation.js:38`, `sandbox/options/mobi-vid/demos/vin-linkage.js:46`) | none | **not implemented** |
| No transport (in-process verification, no chain access) | `cv2x-testbed/sumo/sumo_identity_integration.py:251,309` (SSI layer), `cv2x-testbed/sumo/infrastructure_layer.py:89-109` | M0 (`MEASUREMENT_CONDITIONS.md:22`) | measured (#26 C/D, #27, #44-#46, #48) |

### 1.2 What was measured on transport

| Quantity | In-process (M1-H) | HTTP localhost | Source |
|---|---|---|---|
| Gas | identical by construction | identical (all ten columns byte-identical) | #39 |
| U3 tx median, ERC-1056 | 8.0 ms (pre-merge run) / 8.841 ms (run of record) | 18.1 ms (pre-merge) | #39; `tables/crud_latency_tx.csv` |
| R1 read median | 0.9 ms (pre-merge) | 2.0 ms | #39 |
| Per-call HTTP overhead | none | "≈1–2 ms here" per JSON-RPC call | `MEASUREMENT_CONDITIONS.md:25` |
| Python client HTTP floor | n/a | "≈2.5 ms floor" per localhost round trip | `MEASUREMENT_CONDITIONS.md:230-233` (§5.C) |
| R3 at h = 50, ERC-1056 | 103.177 / 134.283 ms (median / p95, run of record) | 203 / 238 ms (pre-merge) | `tables/scale_latency.csv`; #39 |
| R3 at h = 50, ERC-1155 | 3.267 / 4.030 ms | 5.3 / 6.4 ms | same |
| Throughput (queue + mine) | 78–202 tx/s (pre-merge); 79.24–170.01 tx/s (run of record, U3) | 43–98 tx/s | #39; `tables/throughput.md` |

Not measured: WAN latency, block inclusion time, provider rate limits, provider-side caching, any public-network figure. The 50–100 ms "resolution with blockchain lookup" remains an estimate (#10, status **E**).

**Discrepancy to resolve (orchestrator).** Register #31 gives ERC-1056 R3 at h = 50 as "median ≈65–71 ms in-process", citing the run of record; that run's committed `scale_latency.csv` reads 103.177 ms median. The RPC count (112) and bytes (87,033) agree. Which latency the register intends is unverified.

The two HTTP overhead statements (≈1–2 ms per call in §1, ≈2.5 ms floor in §5.C) refer to different clients (ethers in the harness, web3.py in the testbed) and are not reconciled in the register.

## 2. Dimension (b): write authorisation path

### 2.1 Paths implemented

| Path | Who signs | Who submits and pays | Where (path:line) | Substrates |
|---|---|---|---|---|
| Direct EOA transaction (`msg.sender` gated) | controller key | controller (must hold ETH) | every adapter's C/U/D ops; Python `ERC1056Provider._send_tx` `cv2x-testbed/identity/erc1056_provider.py:381-396` (signs a raw tx with the vehicle's own account; "must hold ETH for gas", line 500) | all ten harness columns |
| Relayed signed operation (meta-transaction, ERC-1056 `*Signed`) | controller signs `keccak256(0x19 ‖ 0x00 ‖ registry ‖ nonce[owner] ‖ identity ‖ op ‖ args)` | any third party (relayer) | contract `1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol:153-175` (`changeOwnerSigned`), `:211`, `:275`, `:328-354` (`setAttributeSigned`), `:379`; harness `1_blockchain-identity/benchmarks/adapters/erc1056.adapter.js:158-176` (relayer = `actors.verifier`, `benchmarks/scenarios/crud.js:47`); sandbox `sandbox/options/erc-1056-uport/adapter.js:40,260-264` (relayer = deployer) | ERC-1056 / uPort-style (pure) only |
| ERC-4337 UserOperation via EntryPoint | owner signs EIP-191 over `getUserOpHash` | relayer acting as bundler calls `handleOp` | `1_blockchain-identity/contracts/ERC4337/CVINMinimalEntryPoint.sol:45-60` (hash), `:69-91` (`handleOp`); `CVINVehicleAccount.sol`; harness `erc4337.adapter.js:13-15,129-140`; sandbox `sandbox/options/erc-4337/adapter.js:34,192-194,245` | ERC-4337 only |
| Owner-called `execute` (ERC-725 / 725xy) | none (signature argument ignored) | owner | `sandbox/options/erc-725/adapter.js:32-35,161`; `sandbox/options/erc-725xy/adapter.js:31-34,173` | ERC-725, ERC-725xy. **Not a relayed path**, though the L1 sandbox table lists it under "signed-op" (`sandbox/grand/report/L1-asymmetry.md:16`) |
| No write at all (implicit identity) | key generated offline | nobody | `sandbox/options/erc-1056-uport/demos/offchain-creation.js:3,34` ("this address IS the DID; no transaction, no gas") | ERC-1056 / uPort-style; RSU identity creation 0 gas (#47) |

The minimal EntryPoint is a research harness, not the canonical one: no bundler mempool, no `handleOps` batching, no paymaster, no deposit or prefund, plain sequential nonces, inner revert reverts the whole transaction (`CVINMinimalEntryPoint.sol:8,17-26`; demo step `harness-limits` in `demos.json`).

### 2.2 Which standards support a relayed write (harness capability table)

From `1_blockchain-identity/results/metrics/latest/tables/analysis_capabilities.csv` (row `U5_meta_tx (optional)`) and `crud_gas.csv` (row `U5_meta_tx`):

| Substrate | U5 relayed | U5 gas | U3 direct gas | Overhead | U5 / U3 latency, median / p95 ms (M1-H) |
|---|---|---:|---:|---:|---|
| ERC-1056 (pure) | ✓ | 62,646 | 35,024 | +27,622 | 13.326 / 19.83 vs 8.841 / 12.475 |
| ERC-4337 | ✓ | 141,767 | 94,651 | +47,116 | 18.845 / 27.292 vs 7.881 / 12.294 |
| ERC-1056 wrapper, ERC-721, ERC-725, ERC-735, ERC-1155, ERC-725xy, LSP8, CVIN-Combined | ✗ (`n/a` in all eight cells) | n/a | 44,677 … 318,054 | n/a | n/a |

Register #34 states the finding ("only ERC-1056 (pure) and ERC-4337 have a relayed path") and #25 gives the nine-standard EntryPoint indirection as **+46,830** gas/op (M1). The default `IdentityAdapter.metaTxSetAttribute` throws `notSupported("U5_meta_tx")` (`benchmarks/adapters/IdentityAdapter.js:47`). The L1 sandbox `signed-op` row gives ERC-1056 / uPort 96,065 and ERC-4337 69,393 gas for a different operation (signed controller change and a signed op on a fresh deploy; `L1-asymmetry.md:16`), not comparable with U5.

The U5 latency includes the client's pre-reads (ERC-1056: `identityOwner` and `nonce`, `erc1056.adapter.js:163-164`; ERC-4337: `nonces` and `getUserOpHash`, `erc4337.adapter.js:134,137`) and the signing, because the timer wraps the whole adapter call (`benchmarks/lib/MetricsCollector.js:117-122`). How much of the +4.5 ms (ERC-1056) and +11 ms (ERC-4337) is pre-read, signing or execution is not separated (unverified).

Sandbox demo gas for the ERC-1056 signed functions (single runs, first use of the nonce, not measured cells): `setAttributeSigned` 79,400, `addDelegateSigned` 65,578, `revokeDelegateSigned` 43,301, `revokeAttributeSigned` 45,091, `changeOwnerSigned` 61,853; ERC-4337 `handleOp → setAttribute` 90,275 (`sandbox/grand/report/demos.json`, family `signed-execution`).

### 2.3 Not measured on writes

Relayer fees and their market, bundler mempool behaviour and censorship, paymaster sponsorship, gas price, block inclusion latency, a write over a public provider, and deferred or batched anchoring (no Merkle or batch-anchor contract exists; harness L4 "batch" creates k identities sequentially, `tables/batch.md`, 30/30 cells `[sequential]`).

## 3. Dimension (c): read path

### 3.1 Read paths implemented

| Read path | Chain contact | Where | Measured | Rows |
|---|---|---|---|---|
| State read, one `eth_call` | 1 RPC | adapters' R1, R2, R4, V6; probe refresh `erc1056_provider.py:248-262` (one `getIdentityInfo` `eth_call`) | R1: 1 RPC / 68 B / 0.474–1.19 ms median, all ten columns (`tables/crud_reads.csv`); probe 2.76 / 2.89 ms (#37) | #29–#31, #37 |
| Event-log history reconstruction (walk the `changed` linked list, one `eth_getLogs` per linked block) | O(h) RPC | `erc1056.adapter.js:80-110`; `erc1056_provider.py:856,884,916` | ERC-1056 R3: 12 RPC / 8,592 B / 8.794 ms (fresh); 22 RPC / 16,936 B / 16.704 ms after the 17-event lifecycle (`tables/resolve.csv`); 14 / 32 / 112 RPC at h = 1 / 10 / 50 (`tables/scale.csv`) | #31, #36 |
| History via contract getters (state, not logs) | O(1) or small constant | ERC-1155 R3 3 RPC at every h; ERC-725xy 2; LSP8 3; ERC-735 3 (but 180,558 B at h = 50) | `tables/scale.csv` | #31, #39 |
| Uncached verify with chain lookup (Python, HTTP) | 4 RPC: `eth_chainId, eth_call, eth_chainId, eth_getLogs` | `erc1056_provider.py:600` (`verify_message`) with `refresh_every = 1` | 9.654 / 15.984 ms vs PKI 0.253 / 0.329 ms (≈38×) | #21 |
| Uncached history query (MOBI V2) | 3 + events `eth_call` | `cv2x-testbed/identity/lifecycle_backends.py:15,234` | 89.9 / 111.3 ms | #33 |
| Cached history query | 0 RPC per query (fill first); optional 2-`eth_call` staleness probe | `lifecycle_backends.py:16-18,237-251` | 0.017 / 0.019 ms (cached) | #33 |
| Freshness-k cached verifier (chain every k-th message) | 1 resolution per k messages | `erc1056_provider.py:107-113,140-200,202-233` (`refresh_every`, `refresh_mode` `full` or `probe`) | t_eff = 0.428 + 10.52/k ms; k = 1 / 5 / 25 / ∞ mean 11.76 / 2.38 / 0.85 / 0.45 ms | #32, #37, #40 (S) |
| Credential-based V2V verification, no chain | 0 RPC; VC verified on first contact against the VC layer's in-process revocation registry, then cached address | `cv2x-testbed/sumo/sumo_identity_integration.py:14-21,251,309` | SSI warm 0.153 ms [0.151, 0.154], cold 0.399 ms | #27 (M0) |
| RSU credential cache, re-check every k messages | 0 RPC; re-check of the road authority's **in-process** registry | `cv2x-testbed/sumo/infrastructure_layer.py:22-30,92-109,171-173` | SPaT warm 0.182 ms; staleness 0 / 4 / 24 messages at k = 1 / 5 / 25 | #44, #46 (M0) |
| In-process DID document synthesis (no chain read) | 0 RPC | `2_w3c-ssi-layer/did-resolution/did_resolver.py` | 0.009 / 0.002 ms cold / warm | §2 of the register, **superseded, re-measure with WM-2 C1** |

`freshness.py` (`cv2x-testbed/identity/freshness.py:100`, `FreshnessPolicy`) is the message freshness window and replay cache (1.0 s past, 0.1 s future), not the freshness-k cache; it applies to every read mode on the message path.

### 3.2 What the read measurements say

| Finding | Value | Row |
|---|---|---|
| Event-log substrates need O(h) RPC calls to resolve; getter substrates are flat | ERC-1056 112 RPC / 87,033 B at h = 50; ERC-1155 3 RPC / 908 B at every h | #31, #36, #39 |
| HTTP transport multiplies O(h) reads | ERC-1056 R3 h = 50: 203 ms over HTTP (pre-merge) | #39 (**U**) |
| Chain-in-the-loop verify is two orders slower than cached | 9.654 ms uncached vs 0.153 ms warm cached (different code and hosts; do not form a ratio across #21 and #27) | #21, #27 |
| One-call probe refresh beats full refresh | 2.76 / 2.89 ms vs 14.38 / 10.28 ms; no finite k reaches P*(0.5) = 100 on that host | #37 |
| Staleness of a cached read is a message count | at most k − 1 messages after revocation (35/35, 280/280 trials; RSU 30 runs) | #32, #37, #46 |
| "Equal once cached" for history fails | ratio 0.072 (0.041 on re-run) | #33 |

Not measured: any read through a third-party provider or indexer, light-client verification of state proofs (`eth_getProof` not used anywhere, unverified by exhaustive search), subscription-driven cache invalidation, a cached verifier whose cache is filled from a chain the vehicle cannot reach at time of use (the V2V and RSU caches are filled in-process).

## 4. Dimension (d): the grand runner's step classification

### 4.1 Definition

`sandbox/grand/run.py:111-114`: a logged demo step is a **mined transaction** if `onchain` is true and `gasUsed` is not 0; an **on-chain call with no gas** if `onchain` is true and gas is 0 ("a read or a revert", comment line 112); otherwise **off-chain**. The totals are returned at lines 125-126 and printed in `GRAND_REPORT.md` (stage `demos`: 92 demos, 1,752 steps, 594 transactions mined, 458 on-chain no gas, 700 off-chain, 62 flagged).

### 4.2 Per-option counts

Derived from the committed `sandbox/grand/report/demos.json` (generated at `b02ea17`, committed in `4b2b30c`; commit-specific) with a read-only snippet applying the rule of `run.py:113-114`:

| Option | Demos | Mined tx | On-chain, no gas | Off-chain | Steps | of which `fn` starts "offchain" |
|---|---:|---:|---:|---:|---:|---:|
| cvin-combined | 10 | 63 | 86 | 3 | 152 | 3 |
| erc-1056-uport | 11 | 89 | 110 | 5 | 204 | 3 |
| erc-1056-vehicle | 9 | 44 | 58 | 13 | 115 | 13 |
| erc-1155 | 9 | 57 | 0 | 128 | 185 | 0 |
| erc-4337 | 6 | 28 | 0 | 81 | 109 | 4 |
| erc-721 | 9 | 60 | 0 | 162 | 222 | 0 |
| erc-725 | 5 | 38 | 36 | 0 | 74 | 0 |
| erc-725xy | 7 | 48 | 77 | 0 | 125 | 0 |
| erc-735 | 7 | 54 | 91 | 2 | 147 | 2 |
| lsp8 | 8 | 35 | 0 | 108 | 143 | 3 |
| mobi-vid | 11 | 78 | 0 | 198 | 276 | 9 |
| **Total** | **92** | **594** | **458** | **700** | **1,752** | **37** |

Totals match `GRAND_REPORT.md`. Sum of gas over mined steps: 133,240,232.

### 4.3 The classification is not uniform across options

Five options (erc-1155, erc-4337, erc-721, lsp8, mobi-vid) log through a `_lib.js` whose contract is "`onchain` is true only for a mined state-changing transaction ... views, off-chain computations and expected reverts are `onchain:false, gasUsed:"0"`" (`sandbox/options/erc-721/demos/_lib.js:9-10`, identical in the other four). Their reads and reverts therefore land in "off-chain", and so do their setup transactions (for example `CVINVehicleNFT.mintVehicle` logged as setup with gas 0). The other six options log views and reverts as `onchain: true, gasUsed: 0`. Consequences:

- Only the "mined transaction" column is comparable across options.
- The "off-chain" column overstates off-chain work for those five options by their `eth_call` reads and expected reverts (steps whose note mentions a revert: erc-1155 52, erc-4337 27, erc-721 46, lsp8 32, mobi-vid 75, all in "off-chain"; in the other options 9–35 each, in "on-chain, no gas").
- Genuinely off-chain steps (function labelled `offchain:…` or `off-chain …`) number 37 of 1,752.

For F3's planned generated classification (after-action report 16, row F3), the logging contract must first be unified, or the classifier must use `fn` and `note` rather than the `onchain` flag. This is a reportable observation, not yet a defect-log entry.

## 5. Radio-level "Mode 3 / Mode 4" and its relation to F3

| Item | Source | Content |
|---|---|---|
| C-V2X resource allocation modes | `cv2x-testbed/README.md:34-37`; `cv2x-testbed/docs/CV2X_PROTOCOLS.md:21-33` | Mode 3: network-assisted, scheduled by eNodeB/gNB, "requires V2N connection"; Mode 4: autonomous sidelink, "works without infrastructure", "critical for safety applications" |
| Interfaces | `cv2x-testbed/README.md:21-22,47-48` | PC5 (sidelink, V2V direct) and Uu (V2N via cellular). The `uu/` directory listed there does not exist in `cv2x-testbed/protocols/` (only `cv2x_stack.py`) |
| Implementation state | `cv2x-testbed/V2_DESIGN.md:43` ("Only Mode 4 - Mode 3 is placeholder"); `cv2x-testbed/protocols/cv2x_stack.py:236-246` (Mode 3 picks a random PRB, "would communicate with eNodeB") | Mode 3 is a stub; no measurement row uses the radio stack (#27, #44: "mock mobility, no radio"; messages delivered in-process) |
| A second, unrelated "Mode" list | `cv2x-testbed/V2_DESIGN.md:415-428` "Hybrid Identity Modes": Mode 1 pure PKI, 2 pure DID, 3 hybrid PKI with blockchain anchoring, 4 federated DID, 5 Layer-2 DID | design text only; no `HybridIdentityManager` exists in any `.py` file |

Relation to F3. The radio mode is orthogonal to the identity interaction mode but constrains it. A vehicle with only PC5 sidelink (Mode 4, out of coverage) has no IP path to any chain node, so at time of use only a no-chain-contact read is possible, and writes can only be signed and held for later submission. With Uu (V2N) or an RSU backhaul, direct or provider-mediated chain contact becomes possible, at a cost the testbed does not model. Mode 3 needs the same cellular network that a V2N chain query would use, so "Mode 3" and "can reach a chain" are correlated but not equivalent: Mode 3 schedules sidelink resources and does not itself carry chain traffic. The freshness-k refresh (#32, #37) silently assumes a V2N path that no Phase 1 radio code provides. To avoid collision, any F3 taxonomy should not use "Mode 3" or "Mode 4" as labels; letters (A, B, C) are free in the repository.

## 6. Security implications recorded in Phase 1

| Issue | Path affected | Record | Status |
|---|---|---|---|
| ERC-1056 signed digest binds registry address and nonce but **not the chain id**: replayable on another chain with the same registry address and nonce | relayed write (ERC-1056) | D52, `docs/DEFECT_LOG.md:154`; `EthereumDIDRegistry.sol:162-165`; threat model G3 narrowed (`docs/THREAT_MODEL.md:63`) | documented; fix departs from upstream bytecode (author decision, N-9) |
| ERC-4337 hash binds EntryPoint address and `block.chainid` | relayed write (4337) | `CVINMinimalEntryPoint.sol:29,60`; demo `get-user-op-hash` | by design; contrast with D52 |
| `changeOwnerSigned` for identity 0x0 accepts v = 27, r = s = 0 | relayed write (ERC-1056) | D53, `DEFECT_LOG.md:155` | open, WM-2 C2 |
| Minimal EntryPoint rolls back the nonce on inner revert; guardian persists as super-owner | 4337 | D15, `DEFECT_LOG.md:43,61` | documented as harness property |
| Replay of a signed op on the same chain | both relayed paths | nonce moves (demos `replay-rejected`, `replay-same-nonce`) | defended |
| Relayer linkability: a relayed pseudonym is linked to the relayer's client set; anonymity set = relayer's population (trivially 1 in the run) | relayed write | #38 (1,586,908 gas/epoch relayed vs 1,454,728 self-funded); `4_comparison-framework/results/pseudonym_pool.md:70,87`; `docs/SCOPE_CHANGES.md:46` | measured (chain layer only) |
| Relayer trust, censorship, fee extraction | relayed write | none: relayer is a trusted Hardhat role wallet in every run | **not analysed** |
| Cached key validity decided by the verifier's wall clock when `validTo` is more than 900 s away; a verifier >15 min behind chain accepts a revoked key | cached or chain-assisted read (Python ERC-1056 provider) | D51, `DEFECT_LOG.md:153`; `erc1056_provider.py:43-50` (`CLOCK_SKEW_S = 900`), `:965-985` (`_ValidityClock`) | open, high; rows #21, #32, #37 hold only under "verifier clock within 900 s of chain time" (`MEASUREMENT_CONDITIONS.md:99-103`) |
| Revocation staleness of a cache | cached read | ≤ k − 1 messages (#32, #37, #46); unbounded at k = ∞ | measured |
| `refresh_every` accepts nan, inf, 1.5, True (nan disables the re-check) | RSU cache | D39, `DEFECT_LOG.md:141` | open, verifier v3 |
| Replay inside the freshness window; residual: a fresh message relayed to a receiver that never heard it | message path, all modes | D29, `DEFECT_LOG.md:115`; #45 "not covered" | fixed (per-receiver cache); residual by design |
| V2V SSI layer has no replay cache | no-chain read | `sumo_identity_integration.py:142-146` | limitation, documented |

## 7. Candidate three-mode taxonomies

Each candidate must cover reads and writes. None is chosen here.

### 7.1 Candidate T1 (orchestrator): direct / mediated / anchored-offline

| Mode | Reads in Phase 1 | Writes in Phase 1 |
|---|---|---|
| A, direct (own client or node) | R1/R3 `eth_call` and `eth_getLogs` against Hardhat in-process or localhost (#29–#31, #21, #33) | EOA transactions, every substrate (#25, #29, #34, #35); Python `_send_tx` |
| B, mediated (a third party relays or serves) | none measured: no public provider (M2 not run), no indexer | ERC-1056 `*Signed` relayed (U5 +27,622), ERC-4337 `handleOp` (U5 +47,116; #25 +46,830) |
| C, anchored-offline (no chain contact at time of use) | V2V cached verify (#27), RSU cache (#44, #46), cached history (#33), freshness-k between refreshes (#32, #37) | implicit identity creation (0 gas, #47); VC issuance off-chain (`erc-1056-vehicle` demos `offchain-*`); an op signed now and relayed later (digest computable offline, ERC-4337 demo `recompute-hash-offchain`) |

Critical assessment against the evidence:

1. **B conflates two axes.** "Third party relays" (who submits and pays) and "third party serves" (whose node answers) are independent. An EOA transaction sent through a public provider is A by authorisation and B by transport; a relayed `setAttributeSigned` sent by the relayer to its own node is B by authorisation and A by transport. Phase 1 measured only the authorisation half of B. The definition needs one axis, or B must be split.
2. **B has no read evidence.** Every Phase 1 read goes to a local node. The only transport measurement (#39) is a localhost node, which is the vehicle's "own" node in T1's sense, and it is status U. B for reads would rest entirely on Phase 2 work (Sepolia, an indexer).
3. **C on reads is well evidenced but "anchored" is often nominal.** The V2V SSI path (#27) checks the VC layer's in-process revocation registry, and the RSU cache (#46) re-checks an in-process authority registry; neither cache was filled from a chain. Only the ERC-1056 freshness-k cache (#32, #37) and the MOBI cached history (#33) were anchored on a chain earlier. A claim that Mode C is "chain-anchored" holds for those rows only.
4. **Reads form a continuum, not a partition.** Freshness-k mixes A and C per sender: k = 1 is A on every message (in probe mode the state is cached but probed on every message), k = ∞ is pure C, and the probe refresh is a cheap A step inside C. T1 needs a rule for which mode a k-cached verifier is in (for example "C with refresh period k").
5. **C on writes is thin and partly contradicts "no chain contact".** No deferred or batch anchoring exists. Implicit creation is "no write ever", not "anchored later". An ERC-1056 signed op needs the current nonce, read from the chain (`erc1056.adapter.js:164`); a signature prepared offline goes stale as soon as another signed op consumes that nonce. When the held op is finally submitted, it travels through Mode B (a relayer) or Mode A. So "signed now, anchored later" is a timing property layered on A or B, not a third path.
6. **Fit with security records.** T1 localises the recorded issues cleanly: D52, D53, D15 and relayer linkability (#38) are B; D51 and k − 1 staleness are C; replay-window issues (D29) are on the message path in every mode.
7. **Fit with the thesis's central result.** T1 makes the H3 finding (the chain is off the V2V hot path, `docs/LATENCY_BUDGET.md` §4) the definition of Mode C, which is clear but risks circularity if C is then used to argue H3.

### 7.2 Candidate T2: by chain contact at time of use (transaction / query / none)

| Mode | Reads | Writes | Phase 1 instrument |
|---|---|---|---|
| 1, state-changing transaction (gas, mined) | n/a | every C/U/D op, direct or relayed | `run.py:113` "mined transaction"; 594 steps |
| 2, chain query, no gas | `eth_call`, `eth_getLogs`, probe | expected reverts, gas estimation (unverified) | `run.py:114` "on-chain call with no gas"; 458 steps (non-uniform, §4.3) |
| 3, no chain contact | cache, credential, in-process synthesis | off-chain signing, VC issuance, implicit creation | `run.py` "off-chain"; 37 genuinely off-chain steps |

Assessment: directly generatable from committed data, which suits the F3 execution step, and aligns with the M1 / M0 tag split. It does not distinguish relayed from direct writes or local from provider reads, so the meta-tx and ERC-4337 evidence (§2) and all transport evidence (§1) fall inside one mode. The demo logging contract must be unified first (§4.3).

### 7.3 Candidate T3: by authority over the write and source of the read (self / delegated / none)

| Mode | Writes | Reads |
|---|---|---|
| Self | controller signs and submits (EOA) | verifier queries chain state itself (R1, R3) |
| Delegated | controller signs, a relayer or bundler submits and pays (ERC-1056 `*Signed`, ERC-4337) | verifier trusts a party that queried for it (provider, indexer, RSU, issuer of a credential) |
| None at time of use | no write (implicit identity) or held signature | credential or cache verified in-process (#27, #46) |

Assessment: close to T1, but defines B as delegation of trust in both directions, which places a VC issuer's attestation (cold path of #27) in "delegated" rather than "offline". The read side of "delegated" is again unmeasured except through the credential path.

### 7.4 Candidate T4: by temporal coupling to the chain (synchronous / periodic / detached)

| Mode | Reads | Writes | Phase 1 rows |
|---|---|---|---|
| Synchronous | chain consulted per use (k = 1; uncached verify 9.654 ms) | tx sent and receipt awaited (harness latency = send → receipt) | #21, #29, #32 k = 1 |
| Periodic | cache refreshed every k uses or by probe | queued and mined in bursts (throughput queue + mine) | #32, #37, #46; `tables/throughput.md` |
| Detached | k = ∞, credential only | signed and held, or none | #27, #32 k = ∞, #47 |

Assessment: maps onto the one dial Phase 1 measured most thoroughly (freshness-k, with a staleness bound) and onto the radio question (detached is the only mode open to a sidelink-only vehicle, §5). It treats relaying as orthogonal (a relayed write can be synchronous or periodic), so the meta-tx and ERC-4337 gas evidence becomes a cross-cutting attribute rather than a mode. "Periodic" for writes rests on throughput bursts, which were not designed as a write mode.

### 7.5 Observations common to all candidates

- Transport (in-process, localhost HTTP, public provider) is itself a three-level ladder (M1 / M1-H/HTTP / M2), but it excludes the no-chain path and two of its three levels are local, so it is better kept as a measurement condition than a mode.
- Any choice should state, per mode, which register rows evidence it and which half (read or write) is unmeasured; under every candidate the "mediated read" or "provider read" cell is empty in Phase 1.
- The F3 generated classification of "every Phase 1 operation and demo step" (after-action report 16, row F3) can be built from `demos.json` (§4) plus the harness operation catalogue (`1_blockchain-identity/benchmarks/lib/operations.js`, e.g. line 16 `U5_meta_tx` "Relayed signed attribute update").
