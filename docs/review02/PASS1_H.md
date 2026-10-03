# Pass 1 — stream P1-H (measurement harness)

**Findings:** H-1, H-2, H-3, H-4, H-5, H-7, H-8, H-10, H-12 (label), Q-13.
**Base:** `d0fe9f0`. **Run of record:** `2026-10-03T23-16-23Z_6620ac7` (clean tree, N = 30),
promoted to `1_blockchain-identity/results/metrics/latest/`.
**Compared with:** the previous `latest`, run `2026-09-30T23-34-57Z_3b786c2`.
**Gates:** `npm run test:conformance` 29 passing / 4 pending (was 22 / 4).
`npx hardhat test` 252 passing / 4 pending (baseline 242 / 4). The 4 pending tests are
the declared-n/a skips.

**Determinism verdict: met.** Three runs in a row of commit `6620ac7`
(`23-10-07Z`, `23-13-05Z`, `23-16-23Z`) gave byte-identical tables:
- `crud_gas`, `crud_txcount`, `crud_storage`, `crud_logbytes`, `crud_calldata`;
- `lifecycle_gas`, `lifecycle_totals`;
- `scale`, `batch`.

The read RPC counts and bytes, the resolve answers and the per-burst throughput gas
totals were identical too.

## Commits (local, not pushed)

| Commit | Findings | Content |
|---|---|---|
| `aa80db6` | H-5 | `normalCdf` fixed; `test/benchmarks/stats.test.js` |
| `6304483` | H-8, H-10, H-12 | slot metric renamed; `meta.json` records hardfork, gas limit and sampling; `run_gas_stats.py` `ci95` → `range_min_max` |
| `2efb364` | H-1, H-3 | fresh issuer per V-op iteration; seed-derived keys; fixed D3 validity |
| `3ec242c` | H-4, Q-13 | forward-replay resolver; conformance post-state assertions |
| `5504f94` | H-2, H-7 | k1 add measured as event 11; `rotateDelegate` (ERC-721 = one approve); R4 on k2 |
| `6620ac7` | H-3 | `scale` table deterministic only; latency moved to `scale_latency` |
| `0aed1bf` | — | run of record as `results/metrics/latest` |

## Per finding

**H-1 — shared issuer.**
- **Change.** `scenarios/common.js` `freshIssuer()` gives every V1/V3/V5 iteration its
  own funded issuer.
  - The issuer's identity (`IdentityAdapter.prepareIssuer`; ERC-725 deploys the issuer
    contract) and one signing key are created in an unmeasured precondition. That is
    the state the shared issuer was in before the first iteration.
  - The crud read block uses its own issuer, for V6.
  - `anchorStatus`, `revokeCredential` and `statusCheck` take an optional `issuer`,
    which defaults to `actors.issuer`. Lifecycle and resolve are unchanged.
- **Verified.**
  - ERC-725 V5 is 43,388 at `METRICS_N=5` and at `METRICS_N=30` (it was 214,099 at
    N = 30 and 71,243 at N = 5).
  - ERC-1056 V6 read bytes fell from 92,656 to 852.
- **Residual N-dependence of encoding width, not state** (it moves the cell by
  12 gas, or 1 byte, with N):
  - ERC-721 V3/V5 carry `tokenId` in calldata: 142,897 at N = 5 vs 142,909 at N = 30,
    as more tokens exist.
  - ERC-1056 V6 `readBytes` includes hex block numbers: 851 B vs 852 B.

**H-3 — random wallets.**
- **Change.** `Wallet.createRandom()` is replaced by
  `sk_i = keccak256(abi.encode("cvin-bench/fresh-key/v1", 42, i))`.
  - The counter restarts on every chain reset, so a cell does not depend on which
    scenarios or adapters ran.
  - Addresses that contain a `0x00` byte are skipped.
  - `credHash` salts away zero bytes.
- **Other nondeterminism found and fixed.**
  - ERC-1056 `deactivate` used a validity derived from `Date.now()`, which put a
    different calldata value in every run. It is now a fixed constant with no zero
    byte: `2^256 − 1 − 2^40`.
  - `scale.csv` printed read latency (ms) in the same cells as gas. Gas and RPC/bytes
    stay in `scale`; latency moved to `scale_latency`.
- **Within-run spread that remains** (reported as the mode, with `gasUsedRange`).
  These are deterministic between runs.
  - ERC-1056 U5: ECDSA r/s zero bytes.
  - ERC-725 C1/C2: keccak key ids.
  - ERC-721 D3/U1/C1: tokenId width. U1 also pays for a cold receiver balance, and
    C1's iteration 0 is the contract's first mint, 2,800 gas less. That case is now
    visible because the issuer pre-mint is gone.
- **Gone.** The 3-gas ERC-725 D1 spread.

**H-4 — ERC-1056 resolver.**
- **Change.** Events are collected with `(blockNumber, logIndex)`, sorted ascending and
  replayed forward.
  - A delegate or attribute event with `validTo <= now` (including 0) deletes the entry.
  - A later event overrides an earlier one.
- **RPC pattern unchanged** (`changed` + one `getLogs` per linked block +
  `identityOwner`). R3 is still 22 / 16,936 B after the lifecycle, 12 / 8,592 B in crud,
  and 112 RPC at h = 50.
- **Test.** After `addDelegate` then `revokeDelegate`, the document does not mention the
  delegate; after the add, it does. **This fails on the old resolver** (checked by
  swapping the old file back in). After `setAttribute` then `revokeAttribute`, the
  attribute is absent.

**H-5.** Φ(x) = ½(1 + erf(x/√2)), with erf by A&S 7.1.26. The unit tests check:
- Φ(0) = 0.5, Φ(1) = 0.8413, Φ(1.96) = 0.97500 ± 1e-3;
- symmetry;
- the Mann–Whitney textbook p = 1.571e-4.

They run under `npx hardhat test`.

**H-7.**
- `runLifecycle` returns `delegateKey` (k2), and resolve R4 queries it.
- Resolve rows now record `answer`: ERC-1056 true, ERC-725 true, **ERC-721 false**.
  ERC-721 transfers clear the approval, which is ERC-721 semantics, and the row says so
  instead of hiding it.
- ERC-725 R4 went from 2 RPC / 264 B (the negative path ran a second `owner()` call) to
  1 RPC / 196 B.

**H-2.**
- `addDelegate(k1)` is now measured as lifecycle **event 11**, so there are **17
  events**.
- Rotation (event 12) uses the new `IdentityAdapter.rotateDelegate(old, new)`. The
  default is U2 + D1. ERC-721 overrides it with a single `approve(k2)`: its one approval
  slot means `approve` replaces k1. The old `approve(k2)` + `approve(0)` left **no**
  delegate.
- A conformance test checks, for all three adapters, that k2 is valid and k1 is invalid
  after the rotation.

**H-8.**
- Key `newSlotsEstimate` → `zeroToNonzeroSstores`.
- `lifetimeNewSlots` → `lifetimeZeroToNonzeroSstores`.
- Label "Zero→nonzero SSTOREs".
- `stateFootprintBytes` is dropped, because it was the same misreading × 32.
- No old-key alias is kept, because nothing in the repo reads it.

**H-10.**
- `meta.json` now records:
  - `network.hardfork` = `osaka` (the compile target stays `evmVersion` = `cancun`);
  - `blockGasLimit` read from the node (60,000,000);
  - `datasetSize` 1,100;
  - the sampling scheme for each scenario;
  - the key derivation;
  - the issuer precondition.
- Table footers read "target cancun … executes osaka".

**H-12.**
- `run_gas_stats.py` now writes `range_min_max`, and the text says it is not a CI. The
  committed `gas_benchmark_stats.json` keeps `ci95` until the P1-K re-run regenerates
  it.
- The `benchmark_scaling.js` "stale 52,612" is in `scaling_lifetime.json`. It was
  computed before `gas_benchmark.json` moved to 52,594, so it is fixed by re-running
  the script after P1-K, not by a code change. The script was not edited.

**Q-13.** Conformance assertions added:
- R2 equals the identity created for the VIN.
- U3 attribute is present in R3.
- D2 attribute is absent.
- U5 relayed attribute is present.
- D3 post-state for each substrate: ERC-1056 `did/deactivated` attribute, ERC-721
  `active = false`, ERC-725 owner = 0.

**Housekeeping.** I appended `/1_blockchain-identity/node_modules` to the shared
`.git/info/exclude`. The worktree's `node_modules` symlink otherwise made every run
`dirty: true`.

## Old → new (`3b786c2` → `6620ac7`)

| Quantity | Old | New | Cause |
|---|---|---|---|
| ERC-725 V5 | 214,099 | **43,388** | H-1 |
| ERC-1056 V6 crud read | 1 RPC / 92,656 B / 23.9 ms | 1 / **852 B** / 1.5 ms | H-1 |
| ERC-721 U1 / U4 | 179,482 / 182,399 | 179,470 / 182,374 | H-3 |
| Batch k=100 (ERC-1056 / ERC-721) | 7,678,480 / 39,981,504 | 7,678,600 / 39,981,600 | H-3 |
| Lifecycle events | 16 | **17** | H-2 |
| Lifetime gas (ERC-1056 / 721 / 725) | 995,586 / 2,681,137 / 3,035,251 | **1,050,765 / 2,701,239 / 3,155,103** | H-2 |
| Lifetime ratio 721 : 1056 / 725 : 1056 | 2.69× / 3.05× | **2.57× / 3.00×** | H-2 |
| Transactions | 25 / 17 / 25 | 26 / 17 / 26 | H-2 |
| Log bytes | 6,272 / 4,288 / 2,944 | 6,464 / 4,288 / 3,072 | H-2 |
| Zero→nonzero SSTOREs (was "new slots") | 7 / 91 / 79 | 8 / 92 / 83 | H-2, H-8 |
| ERC-721 rotation event | 57,376 (2 tx) | 31,214 (1 tx) | H-2 |
| R3 after lifecycle (RPC / B) | 22 / 16,936 · 7 / 5,724 · 17 / 4,100 | unchanged | H-4 |
| R3 after lifecycle, median ms | 18.4 / 6.4 / 12.8 | 15.9 / 7.6 / 13.5 (3 runs: 14.8–15.9 / 6.4–7.6 / 12.7–13.5) | timing |
| R4 after lifecycle | 1/68 · 2/136 · 2/264, negative path | 1/68 true · 2/136 false · 1/196 true | H-7 |
| Throughput, tx/s median | 131 / 140 / 151 | 153 / 170 / 185 (3 runs: 153–172 / 170–177 / 185–189) | timing |
| Gas/s median | 4.25 M / 17.6 M / 18.1 M | 4.98 M / 21.3 M / 22.2 M | timing |
| Scale h=50 ERC-1056 R3 | 112 RPC / 87,033 B / 79.9 ms | 112 / 87,033 / 64.7 ms (3 runs: 64.7–71.4) | timing |
| ERC-721 shared deploy | 2,751,406 (11,863 B) | 2,721,476 (11,724 B) | contract on the merged tree, not this stream |

All other crud gas cells are unchanged.

## Proposed replacement text — `MEASUREMENT_CONDITIONS.md` §5.A

| Parameter | Value | Recorded in |
|---|---|---|
| Network | Hardhat Network, in-process (no HTTP), `chainId 31337`, automine on (except throughput: queue → mine) | `meta.network` |
| EVM | Compiled for `cancun` (`meta.evmVersion`). **Executed under `osaka`**, the Hardhat 2.28/2.29 default (`meta.network.hardfork`) | `meta.evmVersion`, `meta.network.hardfork` |
| Compiler | solc `0.8.24`, optimizer on, `runs = 200`, `viaIR = true` | `meta.solc`, `meta.optimizerRuns`, `meta.viaIR` |
| Block gas limit | 60 000 000, read from the node | `meta.network.blockGasLimit` |
| Actors | Role wallets come from the Hardhat default mnemonic (`benchmarks/lib/actors.js`). Every fresh controller, delegate or issuer key is `sk_i = keccak256(abi.encode("cvin-bench/fresh-key/v1", 42, i))`. `i` restarts at each chain reset, and addresses with a `0x00` byte are skipped | `meta.conditions.freshKeys` |
| Dataset | `benchmarks/lib/dataset.js`, seed 42, **1 100 VINs**, string fields padded to fixed widths | `meta.conditions.datasetSeed`, `datasetSize` |
| Preconditions | Every crud tx op runs on a fresh identity. V1/V3/V5/V6 run on a **fresh issuer per iteration** (issuer identity + one anchored key, unmeasured), so no cell depends on N | `meta.conditions.credentialIssuer` |
| Repetitions | crud tx ops: 1 exact + **5** warm-up + N = 30 latency samples. crud and resolve reads: 5 warm-up + 30. Scale reads: 2 warm-up + 10. Lifecycle, batch and scale tx: one measurement each (gas is exact). Throughput: 3 bursts × 200 tx | `meta.conditions.sampling` |
| Clock | `process.hrtime.bigint()`; latency = send → last receipt, in-process | code |
| Tracing | `debug_traceTransaction` (memory/stack/storage disabled) after the receipt; does not affect measured gas or latency | `meta.conditions.trace` |
| Reproducibility | Two runs of one commit give byte-identical `crud_*` (except latency), `lifecycle_*`, `scale` and `batch` tables (checked on three runs of `6620ac7`) | — |

## Proposed replacement text — §5.B (changed rows only)

| Quantity | Definition | Deterministic? |
|---|---|---|
| `gasUsed` | Σ `receipt.gasUsed` over the transactions a semantic op needs; in crud, the **mode** over all 1 + 5 + 30 iterations, with the spread in `gasUsedRange` | Yes, between runs. Within a cell, iterations can differ by 12 gas per zero byte in values the harness does not choose (ECDSA r/s in U5, keccak key ids in ERC-725 C1/C2, ERC-721 tokenId width) and by first-write effects (ERC-721 C1 first mint, U1 cold receiver). The REPORT lists every cell with more than one execution value |
| `gasExecution` | `gasUsed − (21 000 + calldata gas [+ 32 000 + initcode words × 2 for CREATE])`, **net of refunds** | Yes |
| `zeroToNonzeroSstores` (was `newSlotsEstimate`) | `SSTORE` steps with `gasCost ≥ 20 000`, i.e. writes of a zero slot to non-zero. **Not net state left behind**: a slot cleared later (a revoked key, a cleared approval) still counts. Lifecycle total = Σ over events | Yes |
| `sstoreCount`, `sloadCount`, `zeroToNonzeroSstores`, `logBytes` in crud | Taken from **iteration 0** (the exact iteration) | Yes |
| `readRpcCalls`, `readBytes` | JSON-RPC calls made, and JSON bytes returned, while resolving | Yes for a given chain state. `readBytes` includes hex block numbers and hashes, so it can move by a byte with chain height |
| `answer` (resolve R1/R4/V6) | The value the read returned. R4 queries k2, the delegate the lifecycle rotation installed. ERC-721 answers `false` because the later transfers clear the approval | Yes |

## Proposed register rows #29–#31

| # | Claim | Where | Tag | Source | Status |
|---|---|---|---|---|---|
| 29 | Harness L1 per-op gas, three substrates, e.g. C1 76,786 / 399,844 / 656,480; U3 35,024 / 120,061 / 119,996; V5 33,470 / 125,821 / **43,388** (ERC-1056 / 721 / 725) | HANDOFF §3.1 | M1-H | `tables/crud_gas.*`, run `2026-10-03T23-16-23Z_6620ac7` | **V** on the merged tree. Two runs give byte-identical tables. The old row (run `3b786c2`) is **S**: ERC-725 V5 214,099 depended on N through a shared issuer (H-1), and ERC-721 U1/U4 moved −12/−25 gas because of random addresses (H-3). Every other cell is unchanged |
| 30 | Harness L2 MOBI-VID lifecycle (**17 events**, including the delegate add that the rotation retires): **1,050,765 / 2,701,239 / 3,155,103** gas; ERC-1056 cheapest by **2.57× / 3.00×**; zero→nonzero SSTOREs 8 / 92 / 83 (not net state) | HANDOFF §3.2 | M1-H | `tables/lifecycle_*` | **V**. The old row (995,586 / 2,681,137 / 3,035,251; 2.7× / 3.0×; "7/91/79 new slots") is **S**: the k1 add was unmeasured, ERC-721 rotation ended with no delegate (H-2), and the slot metric was mislabelled (H-8). Bears on H1: ≥10× holds for no lifetime figure |
| 31 | Harness L3/L6: per-op gas flat in population N ≤ 1 000 (≤ 12 gas from tokenId width). ERC-1056 resolution grows linearly in history: 14 → 32 → **112 RPC calls, 87 KB at h = 50; median 65–71 ms** in-process over three runs. After the lifecycle, R3 = 22 / 7 / 17 RPC calls, median ≈15 / 7 / 13 ms; R4 queries the real delegate | HANDOFF §3.3 | M1-H | `tables/scale.*`, `scale_latency.*`, `resolve.*` | **V**. Latency is in-process client + EVM only, varies about ±10 % between runs, and is not deterministic. The old "≈80 ms" is **S** (timing). The R3 document is now correct after revocations (H-4); RPC counts and bytes did not change |

## Corrected HANDOFF §3 (H-6), from run `2026-10-03T23-16-23Z_6620ac7`

- **Heading:** run `2026-10-03T23-16-23Z_6620ac7` (clean tree, commit `6620ac7`).
- **§3.1 table:** change only these cells.
  - U1 ERC-721: 179,482 → **179,470**.
  - U4 ERC-721: 182,399 → **182,374**.
  - V5 ERC-725: 214,099 → **43,388**.
  - The V5 reading becomes "ERC-1056 cheapest; 3.8× / 1.3×".
- **§3.2:** replace the "16 events" heading with "17 events".

  | | ERC-1056 | ERC-721 | ERC-725 |
  |---|---:|---:|---:|
  | Lifetime gas | **1,050,765** | 2,701,239 | 3,155,103 |
  | Transactions | 26 | 17 | 26 |
  | Zero→nonzero SSTOREs (was "new storage slots left behind") | **8** | 92 | 83 |
  | Log bytes | 6,464 | 4,288 | 3,072 |
  | Shared deployment (once) | 2,673,900 | 2,721,476 | 519,384 (+519,384 per identity) |

- **§3.3:**
  - Population and history axes as before.
  - h = 50 ERC-1056: **112 RPC calls, median ≈65–71 ms**, was "80 ms".
  - **Throughput:**
    - **153 / 170 / 185 tx/s** median, ERC-1056 / 721 / 725, in the run of record;
      153–189 over three runs. It was "152–164" in the text and 131–151 in that run's
      JSON.
    - Gas/s: **5.0 M vs 21–22 M**, was "5.1 M vs 19 M".
  - **L6 after the lifecycle:**
    - R3 = 22 / 7 / 17 RPC calls, **15.9 / 7.6 / 13.5 ms** median. It was
      15.3 / 6.9 / 14.1 in the text and 18.4 / 6.4 / 12.8 in that run's JSON.
    - R4 on the rotated-in delegate: true / **false** (the transfer cleared the ERC-721
      approval) / true.
- **§3.4:**
  - H1: "Lifetime **2.6× / 3.0×**".
  - The not-minimum list: "U1/U4 (ERC-725), U2/D1 (ERC-721), **D3 (ERC-725)**". D3 was
    misattributed to ERC-721.
  - H4: "Supported on **12/17** events (was printed 13/16; that run's JSON gave 12/16).
    The exceptions are the k1 add and the rotation (ERC-721), the two ownership
    transfers (ERC-725) and the deactivation (ERC-725)."
- **§3.5:**
  - Item 2: V6 in crud now returns **852 B**, only the read issuer's history.
  - Item 3: replace with "Within-run execution-gas spreads flagged:
    - ERC-721 U1 (154,730 vs 157,530, cold vs warm receiver balance);
    - ERC-721 C1 (iteration 0 is the contract's first mint, −2,800).

    The reported value is the mode; the spreads are identical between runs. The ERC-725
    D1 3-gas spread is gone."
