# Measurement Conditions and Claim Register

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-09-24
**Closes:** audit finding F3 (`docs/AUDIT_01_ORIGINAL_GOALS.md`)
**Merged 2026-10-03 (review 2, Phase 1):** the data-collection lineage created a file of the
same name defining the metrics harness's conditions of record. It now lives here as
tag **M1-H** (§5) with register rows #29–#31; nothing from either file was dropped.

Every quantitative claim in the thesis carries three things: a **condition
tag** (which environment produced it), a **source path** (the script and the
results file), and a **commit**. A number without all three is a *target* or
an *estimate* and is labelled as such. This file defines the tags and keeps
the register of claims found in the repository, with their status.

---

## 1. Condition tags

| Tag | Name | What it means | Use for |
|---|---|---|---|
| **M0** | In-process | Python or JS code path with **no chain access**: DID document construction from an address, signature verification, VC proof checks, cache hits. Timed with `perf_counter_ns`. | The V2V hot path (H3). Nothing here depends on a network. |
| **M1** | Hardhat local | Hardhat in-process EVM, chain id 31337, solc 0.8.24, optimizer 200 + viaIR, evm `cancun`, `allowUnlimitedContractSize`. Gas from the receipt. Latency includes the local JSON-RPC hop only. | All **gas** figures (deterministic, single run is exact). Latency here is *not* public-network latency and must not be presented as such. |
| **M1-H** | Hardhat local, metrics harness | M1 run by `1_blockchain-identity$ npm run metrics` (adapter per standard, fixed dataset seed 42, fresh account per identity, `debug_traceTransaction` storage counts). Conditions in §5; every run stamped in `results/metrics/latest/meta.json`. | Cross-substrate **operation-catalogue** and **lifecycle** comparisons (C1–V6, L1–L6). Not interchangeable with M1 test-suite or `benchmark_gas.js` figures, which use different accounts and operation definitions (§5.D). |
| **M2** | Public testnet | Sepolia (chain id 11155111) via an RPC provider. Latency includes network and block inclusion. | External-validity check of M1 gas (must match to the unit) and *the only* legitimate source of "resolution with blockchain lookup" latency. Not yet run on this trunk. |

Rules that follow from the tags:

- **Gas** (M1/M2) is deterministic for a fixed contract, compiler settings and
  input: report a single exact value, the compiler settings, and the commit.
  No confidence intervals.
- **Latency** (any tag) is not deterministic: report **N ≥ 30** warm
  repetitions after 3 discarded warm-ups, with **median and p95** (mean, min,
  max optional), and an environment header (CPU model, Python/Node versions,
  date, commit). Never a bare "~x ms".
- A figure produced by one tag must not be compared to a target set for
  another. The SAE J2945/1 budget constrains the **receive → verify → trust
  decision** path, which is M0; it does not constrain M2 resolution.
- Figures from the unmerged bundle lineage are cited as *"bundle lineage,
  unverified on trunk"* until re-executed here.

Current trunk results of record: `docs/figures/results_snapshot.json`
(commit `708302a`).

---

## 2. Reconciliation of the DID-resolution latency

The same quantity appears with four values in the repository. They are
different measurements, not disagreements, and only one is currently
evidenced:

| Value | Where it appears | What it actually is | Tag | Status |
|---|---|---|---|---|
| **0.009 ms cold / 0.002 ms warm** (median; p95 0.013 / 0.003) | `docs/figures/resolution_latency_M0.json`, commit `f602fdf` | Construct a DID document in-process, N=30 after 3 warm-ups, per method (`did:ethr`, `did:mobi`, `did:nft`). *Cold* = resolver cache cleared before each call; *warm* = cache hit. Intel Xeon 2.10 GHz, Python 3.11.15 | M0 | **verified** (chapter-grade) |
| 0.05 ms | CLI single run, 2026-09-24 | Same path plus CLI printing and metadata formatting, one sample | M0 | superseded by the row above |
| 0.23 ms | `QUICKSTART.md` example output | `did:mobi` example, same code path | M0 | example output, not a result |
| ~0.8 ms / "<1 ms" | `RESEARCH_THRUSTS_REPORT.md` | earlier session, different code state and hardware; no script on trunk | M0 | **superseded** |
| 50–100 ms | `README.md`, `CAPABILITIES.md`, `docs/thesis/README.md` | design-time estimate for resolution *with a blockchain RPC lookup* | M2 | **estimate / target — never measured** |

Chapter text may use the M0 figure (after an N≥30 re-run) for the hot path,
and must say "not yet measured" for M2 until a Sepolia run exists.

---

## 3. Claim register

Status key: **V** verified on trunk · **E** estimate/target (label as such) ·
**S** superseded (remove or re-measure) · **U** unsupported by trunk
evidence (rewrite) · **B** bundle lineage, unverified on trunk.

| # | Claim | Location | Tag | Source on trunk | Status |
|---|---|---|---|---|---|
| 1 | createVehicleDID **78,090** gas (test-suite context, `CVINVehicleDIDRegistry.test.js`) | `PROJECT_SUMMARY.md` §2.2 | M1 | `1_blockchain-identity` tests; re-measured 2026-10-04 on the post-review-02 tree (Hardhat 2.28.6) | **V**. Was 78,068 at `708302a`; the +22 is K-1's selector-set shift in dispatch, the same as harness C1 76,786 → 76,808 (#29). `docs/figures/results_snapshot.json` is a hand-assembled snapshot of `708302a` and keeps 78,068 |
| 2 | changeOwner 68,854 · addDelegate 72,219 · setAttribute 51,126 | same | M1 | same | **V** Re-measured 2026-10-04: unchanged (the bare ERC-1056 registry's selectors did not move). |
| 3 | ERC-721 mint 102,804 (avg) | same | M1 | `gas-report.txt` | **V** |
| 4 | W3C compliance, internal checker: **94.3%** on the review-02 tree (executable score = PASS + 0.5×PARTIAL over 44 executed checks: 41 PASS, 1 PARTIAL, 2 FAIL; DID Core v1.0, VC Data Model **v2.0**; the 10 SSI-principle items are assessed qualitatively and excluded; the two FAILs are documented Data-Integrity deviations counted as FAIL by design). Was 93.2% until review 02 (S-10): the resolver now returns `methodNotSupported` for an unknown method, so DID Core 7.1.2 moved PARTIAL → PASS. The scoring was not changed. The pre-merge checker's 89.6% over 67 checks (VC DM 1.1, SSI items counted) is a different instrument and is not comparable | thesis README, summary | M0 | `cv2x-testbed/scripts/w3c_compliance_checker.py` | **V**: internal and self-scored; the external result is #24. **Author decision pending (review 02 T-7/T-8):** the malformed-DID checks accept any error code, and the DID Core checks test a synthesised document, so the score measures document *structure*. Label it so in chapter text |
| 25 | Nine-standard gas table (deploy / create / update / delegate-or-claim / revoke / transfer per standard; MOBI-VID-V2 as application profile; ERC-4337 EntryPoint indirection **+46,830** gas/op; create-identity spread **52,216** (CVIN-Combined; 52,192 after Pass 1, +24 after P2-K) → **1,680,816** (ERC-725xy) = **32.2×**) | README §Key Results; thesis README RQ1; ch. 5 | M1 (solc 0.8.24, optimizer 200 + viaIR, evm cancun, OpenZeppelin 5.0.2, Hardhat local) | `1_blockchain-identity/scripts/benchmark_gas.js` → `4_comparison-framework/results/gas_comparison.{csv,tex}`, `gas_benchmark.json` | **V**, re-executed 2026-10-03 after the review-02 contract fixes (K-2, K-3, K-4, K-11, K-13). 19 of 61 cells move, all in ERC-735, CVIN-Combined, ERC-1155 and MOBI-VID-V2: ERC-735 per-vehicle create +6.9 % (1,371,394 → 1,466,088; sticky issuer revocation); CVIN-Combined deploy +7.3 %; claim adds +2.5k; ERC-1155 and MOBI ≤ +1.8 % on deploy and ≤ +0.4 % per operation. **ERC-1056, ERC-721, ERC-725, ERC-725xy, ERC-4337 and LSP8 are unchanged.** 30/30 runs are byte-identical; the CI determinism gate passes. The old row's "52,178 → 1,704,992" and "+46,862" were July (pre-cancun) values and are S. Operation definitions per standard are in the script's `op(...)` descriptions and must accompany any cross-standard ratio (see #6). Per-standard implementation choices that bias gas are listed in `docs/REVIEW_02_CODEBASE.md` K-9/K-10 (threats to validity) **Re-executed again 2026-10-04 after review-02 P2-K** (K-6, K-8, issuer `revokeClaimContent`): 15 of 61 cells move, all in CVIN-Combined, ERC-735 and LSP8. CVIN-Combined add-claim 292,366 → 287,570 and owner claim removal 73,795 → 69,721 (claims no longer advance `changed`); CVIN-Combined deploy and ERC-735 per-vehicle create +4.8 % (ERC-735 create **1,535,776**); LSP8 deploy +1.4 %, ≤ +0.7 % per operation. All other columns unchanged; determinism gate 55/55. |
| 26 | Scaling: marginal cost O(1) in history; lifetime ranking reversal (ERC-1056 cheapest over 15 years, 1,450,824 gas); verify O(1) in claim count; V2V saturation P*≈772 at 0.130 ms/neighbour (R²=0.9999) | README; ch. 5 §5.9; `docs/SCALING_EXPERIMENTS.md` | M1 / M0 | `scripts/benchmark_scaling.js`; `cv2x-testbed/sumo/run_verify_scaling.py`, `run_v2v_stats.py` → `4_comparison-framework/results/scaling_*` | **B** until re-executed on the merged trunk; consistent in shape with `docs/LATENCY_BUDGET.md` (which derives P* from the PKI-vs-ERC-1056 run) but measured on a different code state Re-generated 2026-10-03 on the cancun trunk (`faad888`): ERC-1056 15-year lifetime **1,450,146**; slopes and ranking unchanged. **Different definition from #30** (bare `setAttribute` birth with no VIN binding and a 15-year event model, versus the harness's 17-event MOBI lifecycle); never put #26 and #30 in one table After P2-K: CVIN-Combined 15-year lifetime 9,845,068 → 9,677,232, ERC-735 11,202,285 → 11,272,809; ranking unchanged. |
| 27 | V2V SSI verify warm 0.165 ms [0.162, 0.168], N=30 | README §V2V latency | M0 | `run_v2v_stats.py` → `4_comparison-framework/results/` | **B** until re-executed. This is the *cached/off-chain* verify; compare #21's uncached 9.7 ms. Review 02 (S-2/S-4/S-5/T-3) added revocation, temporal and proof-metadata checks to the verifier (≈+6 % per verify), so the figure must be re-measured before citation |
| 28 | Security: 43/43 attacks defended; DEFENDED = reverted with the documented expected reason (strict harness, review 02 Q-8). attestEvent found-and-fixed 121,110 → 192,718 gas (July build); on the current build the fixed path costs **169,295 execution gas ± 0** (`receipt.gasUsed` 192,659–192,683 depending on calldata zero bytes; run of record 192,671; 192,718 is not reachable on this build) | README §Security; `docs/THREAT_MODEL.md` | M1 | `test/security/securityScenarios.test.js`; `test/MOBIVID/attestEventRegression.test.js` (M3) | **V**: both suites run in CI |
| 24 | **External** W3C DID test suite: **336/441 (76.2%)**: identifier 3/3, core properties 88/88, production 48/48, consumption 3/3, **resolution 194/299**; per resolver ethr 79/119, mobi 58/90, nft 57/90 | `docs/conformance/W3C_DID_TEST_SUITE.md` §8 | M0 | w3c/did-test-suite @ `939b31d`, implementations generated from `DIDResolver.resolve()` at `bd18057`; jest 26.6.3, Node 22.22.0; raw jest reports `docs/conformance/reports/jest-*/*-2026-10-04.*` | **V**, re-run 2026-10-04 after review 02 S-10 (same suite commit, same generator and runner; control 347/347; 8 tests fixed, none regressed). 105 failures, all resolution metadata: R1–R4 (104) are open and fixable in `DIDResolutionMetadata` / `DIDDocumentMetadata`; R5 (`invalidDid`) is cleared, and its one residual failure is a test-vector choice (`did:nft:0x1:0xabc` is a valid generic DID), not a resolver defect. The internal checker (#4) still misses R1–R4. The 2026-09-24 value 328/441 (resolution 186/299; ethr 77, mobi 52, nft 57) is S |
| 5 | VC layer 28/28, contracts 47/47 | summary | — | pytest / hardhat | **S**: superseded by the review-02 counts: Hardhat **293 passing / 4 pending**; Python **254** (`2_w3c-ssi-layer` + `cv2x-testbed/tests`), all run in CI with no skips |
| 6 | "ERC-1056 provides **10× gas savings over ERC-721**" | `docs/thesis/README.md` RQ1 answer; README H1 | M1 | `1_blockchain-identity/scripts/benchmark_gas.js` → `4_comparison-framework/results/gas_comparison.csv` | **V, reconciled 2026-09-24** — the ratio is a function of the operation definition, now stated wherever the claim appears: (a) bare ERC-1056 `createIdentity` 52,594 vs ERC-721 `CVINVehicleNFT.mintVehicle` 542,378 (mint + VIN mapping + metadata struct + transfer record) = **10.3×** (cancun run of 2026-09-24; July values 52,612 / 542,429 give the same ratio); (b) VIN bound on both sides, `createVehicleDID` 78,068 vs `mintVehicle` 542,378 = **6.9×**; (c) the trunk's earlier 1.32× compared `createVehicleDID` with a *bare* `CVIN_NFT_DID_ERC721.mint` (102,804), which binds no VIN and is not the create-identity operation — withdrawn as a like-for-like figure and kept only as the bare-mint cost (#3). The thesis uses (b) as the headline and reports (a) as the lower bound. |
| 7 | DID creation ~45,000 gas · attribute 50,000 · delegate 55,000 | `CAPABILITIES.md` | M1 | none | **E** — design estimates; measured values in #1–2 differ (createVehicleDID also writes the VIN attribute) |
| 8 | NFT minting ~150,000 gas · transfer ~70,000 | `CAPABILITIES.md` | M1 | none | **E** — measured mint avg 102,804 |
| 9 | ERC-725 proxy creation ~350,000 gas | `CAPABILITIES.md` | M1 | none | **S**: ERC-725 is measured on the trunk (harness C1 656,480 including the per-identity deploy, row #29; nine-standard table, row #25) |
| 10 | Resolution 50–100 ms "with blockchain lookup" | README, CAPABILITIES, thesis README | M2 | none | **E** |
| 11 | Resolution ~0.8 ms / <1 ms | `RESEARCH_THRUSTS_REPORT.md` | M0 | none | **S** |
| 12 | VC verification "5–10 ms (PKI) or 50–100 ms (blockchain)" | `CAPABILITIES.md` | M0/M2 | none | **E**: measured values are #21 (PKI 0.25 ms M0; ERC-1056 uncached 9.7 ms M1, cv2x registry) |
| 13 | VC verify "median 7.5 ms / p95 8.9 ms (offline)" | `INVENTORY.md` | M0 | none (script not on trunk) | **S** — superseded by #21 |
| 14 | "<10 ms verification" | `README.md` | M0 | none | **E** (target from roadmap) |
| 15 | SUMO simulation "with 50 vehicles" | README, thesis README, thrusts report | — | `cv2x-testbed/sumo/` config exists; no results file | **E** — configured, not run |
| 16 | Nine standards compared | README, thesis README | M1 | 3 implemented on trunk | **S**: the analysis lineage is merged (`434669d`); superseded by rows #25–#28 |
| 17 | V2V SSI warm verify 0.165 ms [0.162, 0.168], N=30; saturation P*≈772 | bundle lineage | M0 | not on trunk | **S**: the analysis lineage is merged (`434669d`); superseded by rows #25–#28 |
| 18 | ERC-1056 createIdentity 52,612 · CVIN-Combined 52,178 · ERC-725xy 1,704,992 | bundle lineage | M1 | not on trunk | **S**: the analysis lineage is merged (`434669d`); superseded by rows #25–#28 |
| 19 | Security 43/43 attacks defended | bundle lineage | — | not on trunk | **S**: the analysis lineage is merged (`434669d`); superseded by rows #25–#28 The superseding matrix (`security_matrix.json`) was regenerated 2026-10-04 with current Sybil-cost gas; outcomes are unchanged, and the identity-theft cell now also runs the S-1 own-DID thief. |
| 20 | USD costs ("~$0.50 at 30 gwei") | `CAPABILITIES.md` | — | none | **E** — gas price and ETH price are dated; report gas units only, convert in one appendix table with the date |
| 21 | PKI vs ERC-1056 identical operations, n=50 (median / p95 ms): verify **0.253 / 0.329** PKI (pki_standard; pki_centralized 0.254 / 0.325; CA signature + issuer + validity + CRL + message signature) vs **9.654 / 15.984** ERC-1056 uncached (4 RPCs: `eth_chainId, eth_call, eth_chainId, eth_getLogs`, two of them web3 client overhead) → ≈38×; resolve 0.001 vs 8.336; check-revocation 0.001 vs 5.810; register 4.1 vs 12.9; issue 0.19 vs 12.0; revoke 0.015 vs 10.8. Every verifier enforces the same T-9 freshness policy (signed generation time, 1.0 s / 0.1 s window, replay cache) | `cv2x-testbed/results/pki_vs_erc1056.{csv,json,md}` | M0 (PKI, in-process) / M1 (ERC-1056 via local RPC: Hardhat 2.28.6, chain 31337, automine; registry compiled fresh from current source, solc 0.8.20 / opt 200) | `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py --deploy`, commit `1c1b8e1` (git_dirty false), results `1d0e3a2` | **V**, with the caveats in the .md: in-process PKI is a lower bound on real PKI; ERC-1056 verify is uncached (worst case); **the ERC-1056 column is the cv2x `ERC1056Registry`, not `EthereumDIDRegistry` (K-5), so it is not comparable with #25/#29**; PKI timings depend on the `cryptography` version (49.0.0 here). The fall from 11.2 to 9.7 ms is a node-configuration effect (automine only); a same-host A/B of the T-9 code change shows PKI +0.01–0.02 ms and ERC-1056 within noise. Earlier rows are S (§5.D). Review-02 Pass 3 later bound the DID's chain segment and canonicalised the replay-cache key in ERC-1056 verify (an integer parse and an address checksum, no RPC: microseconds against 9.65 ms); not re-run for that |
| 22 | `cv2x-testbed` ERC1056Registry gas: register 54,860 · issue (attribute) 37,791 (37,767–37,791; calldata zero-byte spread) · revoke **75,257** · deploy **927,756** | same | M1 (solc 0.8.20, optimizer 200, evm paris: the testbed's own config) | same, `--deploy` receipt, results `1d0e3a2` | **V**, current source (post-K-3). The earlier 75,044 / 878,509 came from a stale tracked artifact that predated the K-3 fix (review 02 R2-H2); the tracked artifacts are now rebuilt and checked (`cv2x-testbed: npm run check:artifacts`). A *different contract* from the `1_blockchain-identity` registries in #1–2 and from `EthereumDIDRegistry` in #25/#29 (**K-5**): no `*Signed` functions, owner-only wrappers, a whole-identity revoked flag, and a `DIDRevoked` event with no `previousChange`. Do not quote these as "ERC-1056 gas" without that qualifier |
| 29 | Harness L1 per-op gas, three substrates (ERC-1056 / 721 / 725), e.g. C1 create 76,808 / 399,844 / 656,480; U3 set attribute 35,024 / 120,061 / 119,996; V5 revoke credential 33,470 / 125,821 / **43,388** | `HANDOFF-DATA-COLLECTION-FRAMEWORK.md` §3.1 | M1-H | `results/metrics/latest/tables/crud_gas.*`, run `2026-10-03T23-23-59Z_59405ff` | **V** on the review-02 tree; two runs of one commit give byte-identical gas tables. Old row (run `3b786c2`) **S**: ERC-725 V5 214,099 depended on N through a shared issuer (H-1); ERC-721 U1/U4 differ by +12/+25 between the original run and later runs because of the **toolchain** (unpinned Hardhat 2.29.1 vs lockfile 2.28.6; §5.E), not random addresses as first attributed in review 02 H-3; seeded wallets (H-3) removed the separate batch-cell drift; ERC-1056 C1/C2 +22 from the K-1 selector change |
| 30 | Harness L2 MOBI-VID lifecycle (**17 events**, including the delegate add that the rotation retires): **1,050,787 / 2,701,239 / 3,155,103** gas, ERC-1056 cheapest by **2.57× / 3.00×**; zero→nonzero SSTOREs 8 / 92 / 83 (writes, not net state) | same §3.2 | M1-H | `tables/lifecycle_*` | **V** (as #29). Old row (995,586 / 2,681,137 / 3,035,251; 2.7× / 3.0×; "7/91/79 new slots") **S**: the k1 add was unmeasured and the ERC-721 rotation left no delegate (H-2); the slot metric was mislabelled (H-8). Bears on H1: ≥10× holds for the create-identity operation only (#6), for no lifetime figure |
| 31 | Harness L3/L6: per-op gas flat in population N ≤ 1 000 (≤ 12 gas from tokenId width); ERC-1056 resolution grows linearly in history: 14 → 32 → **112 RPC calls / 87 KB at h = 50, median ≈65–71 ms** in-process; after the lifecycle R3 = 22 / 7 / 17 RPC calls, median ≈14–16 / 6–8 / 13 ms | same §3.3 | M1-H | `tables/scale.*`, `scale_latency.*`, `resolve.*` | **V** (as #29). Latency is in-process client + EVM only and varies ≈±10 % between runs. The old "≈80 ms" is **S** (timing). The R3 document is correct after revocations (H-4); RPC counts and bytes did not change. R4 queries the real delegate (H-7) |
| 23 | Signed BSM-like message size: PKI ≈1.08–1.11 kB (carries PEM cert) vs ERC-1056 596 B (carries DID only) | same | — | same | **V** (Re-confirmed 2026-10-04: 1,078 / 1,110 / 596 B; the extra byte is the chain id in the DID.) |

---

## 4. What changes in the drafts (done in the same commit as this file)

- `docs/thesis/README.md`: RQ1 answer rewritten to the measured ratio and the
  M0 figure; "SUMO with 50 vehicles" marked *configured, not run*.
- `README.md`: performance table rows marked as targets; "<10 ms
  verification" marked as target.
- `RESEARCH_THRUSTS_REPORT.md`: "~0.8 ms" and "<1 ms" replaced by the M0
  figure with its tag.
- `CAPABILITIES.md` and `INVENTORY.md`: banner added stating that their
  performance and gas figures are design-time estimates superseded by
  `docs/figures/results_snapshot.json`; the INVENTORY "measured" line
  re-labelled.

Numbers in session logs (`AUTONOMOUS_*`, `SESSION_*`) are left untouched as
historical record; nothing in a chapter may cite them.

---

## 5. Metrics-harness conditions (tag M1-H)

**Rule (audit F3, harness scope):** a number from the operation catalogue or the
lifecycle/scale/throughput/resolve scenarios may appear in a chapter only if it was
produced by `npm run metrics` under the conditions below and the chapter cites the run id
in `results/metrics/latest/meta.json`. Harness numbers carry tag M1-H and never share a
table with M1 numbers from other scripts.

### 5.A Fixed conditions (on-chain harness)

_Revised in review 02 (H-1, H-3, H-10)._

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
| Reproducibility | Two runs of one commit give byte-identical `crud_*` (except latency), `lifecycle_*`, `scale` and `batch` tables (checked on three runs of `6620ac7` and re-confirmed on `59405ff`) | — |

### 5.B What each reported quantity means

| Quantity | Definition | Deterministic? |
|---|---|---|
| `gasUsed` | Σ `receipt.gasUsed` over the transactions a semantic op needs | yes, up to calldata zero-byte pricing of generated addresses (reported as mode; range in `gasUsedRange`) |
| `gasExecution` | `gasUsed − (21 000 + calldata gas [+ 32 000 + initcode words × 2 for CREATE])` | yes (checked: run fails the determinism flag otherwise) |
| `sstoreCount`, `sloadCount` | opcode counts from the trace | yes |
| `newSlotsEstimate` | `SSTORE` steps whose `gasCost ≥ 20 000` (zero → non-zero) | yes |
| `logBytes` | Σ (32 × topics + data length) over emitted logs | yes |
| `latencyMs` (tx) | wall-clock send → receipt on the in-process node; **client + EVM execution only, no propagation or consensus** | no → median / p95 / n |
| `latencyMs` (read) | wall-clock of the adapter's resolution code incl. all JSON-RPC round-trips in-process | no → median / p95 / n |
| `readRpcCalls`, `readBytes` | JSON-RPC calls made and JSON bytes returned while resolving | yes |
| `txPerSec` | 200 queued tx ÷ (queue time + mine time) on one node | no → median of 3 |
| `costUSD` | **derived**, `gasUsed × gasPrice × ETH/USD` with the parameters printed in `meta.derivedCostParams`; illustration only | n/a |

**Revised in review 02** (these rows replace the same-named rows above; H-8, H-9):

| Quantity | Definition | Deterministic? |
|---|---|---|
| `gasUsed` | Σ `receipt.gasUsed` over the transactions a semantic op needs; in crud, the **mode** over all 1 + 5 + 30 iterations, with the spread in `gasUsedRange` | Yes, between runs. Within a cell, iterations can differ by 12 gas per zero byte in values the harness does not choose (ECDSA r/s in U5, keccak key ids in ERC-725 C1/C2, ERC-721 tokenId width) and by first-write effects (ERC-721 C1 first mint, U1 cold receiver). The REPORT lists every cell with more than one execution value |
| `gasExecution` | `gasUsed − (21 000 + calldata gas [+ 32 000 + initcode words × 2 for CREATE])`, **net of refunds** | Yes |
| `zeroToNonzeroSstores` (was `newSlotsEstimate`) | `SSTORE` steps with `gasCost ≥ 20 000`, i.e. writes of a zero slot to non-zero. **Not net state left behind**: a slot cleared later (a revoked key, a cleared approval) still counts. Lifecycle total = Σ over events | Yes |
| `sstoreCount`, `sloadCount`, `zeroToNonzeroSstores`, `logBytes` in crud | Taken from **iteration 0** (the exact iteration) | Yes |
| `readRpcCalls`, `readBytes` | JSON-RPC calls made, and JSON bytes returned, while resolving | Yes for a given chain state. `readBytes` includes hex block numbers and hashes, so it can move by a byte with chain height |
| `answer` (resolve R1/R4/V6) | The value the read returned. R4 queries k2, the delegate the lifecycle rotation installed. ERC-721 answers `false` because the later transfers clear the approval | Yes |

### 5.C Off-chain baselines (Python, `cv2x-testbed/`)

Landed on the trunk as `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py` (register #21,
conditions in `cv2x-testbed/results/pki_vs_erc1056.md`). Its ERC-1056 column goes over
HTTP JSON-RPC (a localhost round-trip, ≈2.5 ms floor) which the in-process JS harness does
not have, so the two latency columns are **not** directly comparable and must be labelled.

### 5.D Superseded numbers

| Number | Where it appeared | Status |
|---|---|---|
| "50–100 ms identity resolution" | `docs/thesis/README.md` | superseded; not trunk-generated |
| "~0.8 ms resolution" | `RESEARCH_THRUSTS_REPORT.md` | superseded; conditions unknown |
| "~45–50K gas per ERC-1056 op" | early session logs, `HANDOFF-DATA-COLLECTION-FRAMEWORK.md` v1 | superseded; see `results/metrics/latest/tables/crud_gas.md` |
| 78 068 / 68 854 / 72 219 / 51 126 gas (2026-09-24 snapshot) | `docs/figures/results_snapshot.json` | valid for its own conditions (test-suite calls on the shared `vehicleOwner` account); the harness numbers use fresh accounts and the fixed dataset, so they differ by cold/warm slot effects — cite the harness numbers |
| verify 0.321/0.366 PKI vs 18.158/23.741 ERC-1056 (7 RPC); revoke 8 RPC; resolve 0.171 vs 10.058; register 15.2 vs 16.9; issue 0.72 vs 13.5 (2026-09-24, `ed85dfd`, git_dirty) | register #21 (old); chapters citing "18.2 ms" / "0.32 ms" | **S**, review 02: PKI verify skipped the CA signature check (T-1; forged certificates were accepted); ERC-1056 verify made a redundant `isRevoked` call (T-5); RPC counts included the untimed post-check (T-6); ERC-1056 key resolution returned revoked keys (T-2). Re-run 2026-10-03 (`2032c77`), now row #21 |
| Harness run `3b786c2`: lifetime 995,586 / 2,681,137 / 3,035,251 (2.7× / 3.0×), ERC-725 V5 214,099, "7/91/79 new slots", throughput "152–164 tx/s", R3 "15.3/6.9/14.1 ms", "80 ms at h=50", "13/16 events" | `HANDOFF-DATA-COLLECTION-FRAMEWORK.md` v2 §3 | **S**, review 02 H-1/H-2/H-3/H-6/H-8; now rows #29–#31 (run `59405ff`) |
| Nine-standard "52,178 → 1,704,992", "+46,862 gas/op" | register #25 (old), README, CAPABILITIES | **S**: July pre-cancun values; now 52,192 → 1,680,816 and +46,830 |
| W3C checker 93.2 % | register #4 (old), README, CI comment | **S**: 94.3 % after review-02 S-10 (one check: unknown method → `methodNotSupported`) |
| verify 0.276/0.372 PKI vs 11.163/13.524 ERC-1056; #22 revoke 75,044, deploy 878,509 (2026-10-03, `2032c77`) | register #21/#22 (Pass 1) | **S**, review 02 Pass 2: the registry bytecode was a stale tracked artifact predating K-3 (R2-H2), and T-9 changes the signed bytes and adds a freshness check to every verify. Now rows #21/#22 (`1d0e3a2`) |

### 5.E Toolchain pinning (M1-H), observed 2026-10-04

Gas is EVM-defined, but the node that executes it is not version-free. A harness run on
commit `3ea92f7` (pre-rebase hash of `2439cd0`; identical `1_blockchain-identity` tree) with an **unpinned** `npm install` (Hardhat 2.29.1, Node 22.22.2) moved two
cells against the run of record `59405ff` (Hardhat 2.28.6): ERC-721 `U1_rotate_controller`
179,470 → 179,482 (+12) and `U4_transfer_vehicle` 182,374 → 182,399 (+25); every other cell,
including all lifecycle events, was identical. Re-running the same commit after `npm ci`
(lockfile toolchain) reproduced the run of record byte-for-byte in all shared columns
(run `2026-10-04T05-41-19Z_bca0899`, now `results/metrics/latest`). Rules:

- M1-H runs are valid only from `npm ci`; `meta.json` records `hardhat` and `node`, and a
  chapter may cite a run only if those match the lockfile.
- A toolchain change is a conditions change: re-run and re-promote `latest`; do not mix
  cells from runs with different `meta.hardhat`.
- The two moved cells are the ERC-721 ops whose cost already shows a within-run cold/warm
  receiver spread (§5.D row for `59405ff`, H-3); the cause of the +12/+25 under 2.29.1 was
  not investigated further because the pinned toolchain removes it.
