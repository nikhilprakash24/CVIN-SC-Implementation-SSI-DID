# Measurement Conditions and Claim Register

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-09-24
**Closes:** audit finding F3 (`docs/AUDIT_01_ORIGINAL_GOALS.md`)

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

Current trunk results of record: `docs/figures/results_snapshot.json`.

### 1.1 Option naming: the two ERC-1056 variants (decision of 2026-10-04, plan S0)

Two different contracts on the trunk are both called "ERC-1056". From this date every
figure names the variant:

| Sub-option | Contract | Character | Measured in |
|---|---|---|---|
| **ERC-1056 / uPort-style** | `1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol` (+ `CVINVehicleDIDRegistry` wrapper) | implicit identities (creation is free), `changeOwner(Signed)`, delegates with `validTo`, attributes, `changed()` linked list — the DIF `ethr-did-registry` lineage | #1–#3 (wrapper gas), #25 (nine-standard table), scaling, security harness |
| **ERC-1056 / vehicle profile** | `cv2x-testbed/contracts/ERC1056Registry.sol` (mirrored in `1_blockchain-identity/contracts/MOBI/`) | explicit `registerVehicle`, `isRevoked` / `revokeIdentity`, `getIdentityInfo`, `lastChanged` — the testbed's vehicle-specific profile, also the base the MOBI VID registries extend | #21 (PKI vs ERC-1056), #29 (freshness-k), #30 (lifecycle parity, as MOBI's base) |

Both are kept deliberately: the pair is a within-standard asymmetry case (implicit vs
explicit creation on the same event model). A cross-variant comparison is a planned
L1 sandbox result (plan S3). Chapter text must not mix the two under one name.

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
| 1 | createVehicleDID 78,068 gas | `PROJECT_SUMMARY.md` §2.2 | M1 | `1_blockchain-identity` tests; `results_snapshot.json` | **V** |
| 2 | changeOwner 68,854 · addDelegate 72,219 · setAttribute 51,126 | same | M1 | same | **V** |
| 3 | ERC-721 mint 102,804 (avg) | same | M1 | `gas-report.txt` | **V** |
| 4 | W3C compliance, internal checker: **94.3%** after the 2026-10-03 resolver fixes (93.2% at the merge; executable score = PASS + 0.5×PARTIAL over 44 executed checks; DID Core v1.0 14/15, VC Data Model **v2.0** 27/29; the 10 SSI-principle items are assessed qualitatively and excluded; the two FAILs are documented Data-Integrity deviations counted as FAIL by design). The pre-merge checker scored 89.6% over 67 checks against VC DM 1.1 with SSI items counted — a different instrument; the two figures are not comparable and only the 93.2% is current | thesis README, summary | M0 | `cv2x-testbed/scripts/w3c_compliance_checker.py` (analysis-lineage version) | **V** — internal, self-scored; external result is #24 |
| 25 | Nine-standard gas table (deploy / create / update / delegate-or-claim / revoke / transfer per standard; MOBI-VID-V2 as application profile; ERC-4337 EntryPoint indirection +46,862 gas/op; create-identity spread 52,178 → 1,704,992 = ~33×) | README §Key Results; thesis README RQ1; ch. 5 | M1 (solc 0.8.24, optimizer 200 + viaIR, OpenZeppelin 5.0.2, Hardhat local) | `1_blockchain-identity/scripts/benchmark_gas.js` → `4_comparison-framework/results/gas_comparison.{csv,tex}`, `gas_benchmark.json` | **V** — re-executed on the merged trunk 2026-09-24 under **evm `cancun`** (the trunk's config); the July 2026 run used the default EVM target. Result: **every cell 1.0–2.8% lower** (deployments −1.0 to −2.8%, creates −1.2 to −2.3%, updates/claims/revokes/transfers <0.5%), **all relative-cost ratios unchanged to two decimals** (e.g. ERC-721 create 10.40× in both). This is a sensitivity result for ch. 5 §5.9.4 (optimizer runs, calldata, and now EVM target). Re-executed again on **2026-10-04** after the defect fixes D13, D18, D21, D22, D25 (register row #31): the JSON/CSV of that date are the results of record; 22 of 55 cells moved — ERC-721 deployRegistry 2,721,476→2,787,288; ERC-721 createIdentity 542,378→545,101; ERC-735 createIdentity 1,371,394→1,598,928; ERC-735 addDelegateOrClaim 290,177→295,805; ERC-735 updateAttribute 75,160→80,788; ERC-735 transferOwnership 28,702→28,768; ERC-1155 deployRegistry 2,277,168→2,380,231; ERC-1155 createIdentity 103,881→107,238; ERC-1155 addDelegateOrClaim 57,115→57,137; ERC-1155 revoke 30,625→30,647; ERC-1155 transferOwnership 83,608→83,748; LSP8 deployRegistry 1,592,737→1,647,805; LSP8 createIdentity 149,430→152,453; LSP8 updateAttribute 55,051→55,070; LSP8 transferOwnership 80,576→80,544; LSP8 revoke 41,838→41,812; MOBI-VID-V2 deployRegistry 3,952,603→3,966,355; MOBI-VID-V2 transferOwnership 199,810→200,023; MOBI-VID-V2 revoke 74,836→75,382; CVIN-Combined deployRegistry 1,325,604→1,372,501; CVIN-Combined addDelegateOrClaim 289,886→292,214; CVIN-Combined revoke 73,688→75,580 (`4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04.json`). README and thesis-README create-identity figures follow this file. Operation definitions per standard are in the script's `op(...)` descriptions and must accompany any cross-standard ratio (see #6). |
| 26 | Scaling: marginal cost O(1) in history; lifetime ranking reversal (ERC-1056 cheapest over 15 years, 1,450,824 gas); verify O(1) in claim count; V2V saturation P*≈772 at 0.130 ms/neighbour (R²=0.9999) | README; ch. 5 §5.9; `docs/SCALING_EXPERIMENTS.md` | M1 / M0 | `scripts/benchmark_scaling.js`; `cv2x-testbed/sumo/run_verify_scaling.py`, `run_v2v_stats.py` → `4_comparison-framework/results/scaling_*` | **V** (re-executed 2026-10-04 on the trunk after the defect fixes: marginal O(1) holds on all five, first-op cold-slot steps ×1/×2/×3 as before with ERC-1155 now ×2 because of the D8 held-type bitmap; lifetime ranking unchanged — ERC-1056 1,450,146, ERC-1155 1,865,183, CVIN-Combined 9,839,660, MOBI-VID-V2 9,848,183, ERC-735 11,443,652; the V2V saturation half is M0 and was not re-run) — was **B** until then; consistent in shape with `docs/LATENCY_BUDGET.md` (which derives P* from the PKI-vs-ERC-1056 run) but measured on a different code state |
| 27 | V2V SSI verify warm 0.165 ms [0.162, 0.168], N=30 | README §V2V latency | M0 | `run_v2v_stats.py` → `4_comparison-framework/results/` | **B** until re-executed; this is the *cached/off-chain* verify (compare #21's uncached 18.2 ms and its ≈0.4 ms off-chain estimate) |
| 28 | Security: 43/43 attacks defended (54-scenario two-lens harness); attestEvent found-and-fixed 121,110 → 192,718 gas | README §Security; `docs/THREAT_MODEL.md` | M1 | `1_blockchain-identity/test/security/securityScenarios.test.js` | **V** — the security suite is part of the merged-trunk Hardhat run |
| 29 | Freshness-k cached verifier, ERC-1056 (n=200, one sender, warm): k=off (shipped, 7 RPC) 15.026 / 20.336 ms; k=1 (one `changed()` per message) 2.697 / 3.436; k=5 0.453 / 3.210; k=25 0.464 / 0.856; k=100 0.437 / 0.505; k=∞ 0.441 / 0.500 (median / p95); PKI reference 0.338 / 0.504; revoked sender rejected after 1 / 1 / 2 / 22 / 97 / never messages; analytic 0.4 + 2.5/k within 10–35 % of the mean | `docs/LATENCY_BUDGET.md` §3–§4 | M1 (chain reads) / M0 (cache hits) | `cv2x-testbed/scripts/experiment_freshness_k.py` → `cv2x-testbed/results/freshness_k.{csv,json,md}` | **V** — reproduced here at n=60 (k=1 3.10 ms, k=∞ 0.456 ms). **Host caveat:** 2.80 GHz Xeon vs 2.10 GHz for #21; chain-bound rows ~15–20 % faster (uncached 15.0 vs 18.2 ms); compare within a run, not across #21/#29 |
| 30 | Lifecycle parity, centralized registry vs MOBI VID V2 (n=50, median / p95 ms): register_birth 0.004 / 0.006 vs 15.931 / 21.024 (397,971–397,995 gas, 6 RPC); record_lifecycle_event 0.009 / 0.016 vs 13.439 / 19.179 (306,555–306,567 gas); transfer_ownership 0.003 / 0.004 vs 11.904 / 14.151 (199,031–199,043 gas); query_history 0.054 / 0.176 vs 35.228 / 43.887 (uncached, 15 RPC); attest_event 13.137 / 16.837 (191,604–191,628 gas) with **no centralized equivalent**; V2 deploy 4,919,599 gas | `docs/PLAN_MOBI_SUMO.md` M4; ch. 5 | M1 (chain) vs in-process | `cv2x-testbed/scripts/experiment_lifecycle_parity.py` → `cv2x-testbed/results/lifecycle_parity.{csv,json,md}` | **V** — writes ≥10× (by three orders of magnitude) confirmed; the "equal once cached" half of the M4 hypothesis is **untested** (no cached history client); centralized side is in-process (lower bound); same 2.80 GHz host as #29 **Note (2026-10-04, D11b):** MOBI registration is now two transactions (`registerVehicleBirth` + `anchorVehicleKey`, ≈69.7 k gas more); the register_birth column above was measured before that change and is not re-executed in this pass (host differs from the original run — compare within a run). |
| 31 | Gas moved by the 2026-10-04 defect fixes (D13 VIN normalisation on three mint paths; D21 `revoked` check and `previousChange` on the vehicle-profile registry and the MOBI registries that extend it; D22 `DIDClaimChanged` on CVIN-Combined claim ops; D25 issuer registry + VIN binding on ERC-735 claims; D18 bounded validity on the ERC-1056 wrapper). Largest: ERC-735 deploy +227,534 (issuer registry code), ERC-1155 deploy +103,063 (normalisation bitmap), ERC-721 deploy +65,812; creates +2.7k/+3.4k/+3.0k on ERC-721/1155/LSP8; ERC-735 claims +5,628 | `4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04.json` | M1 | nine-standard benchmark re-executed 2026-10-04 | **V** — rows #1–#3, #21, #29, #30 measured before the fixes keep their values with this note: chain-bound rows differ from the current contracts by the listed deltas (vehicle-profile registry: revokeIdentity +547, changeOwner +2,213; MOBI changeOwner +2,201); latency rows are unaffected in kind |
| 32 | Gas moved by the 2026-10-04 pass-06 fixes (D7/D8 ERC-1155: standard transfers closed, held-type bitmap, `issuerTransferIdentity`; D11b MOBI `anchorVehicleKey`): 10 of 61 nine-standard cells — ERC-1155 deploy +491,204, create +491, update +2,069, add-claim +22,994 (one cold SSTORE for the bitmap on the first issuance of a type), revoke +2,402, transfer +2,550; MOBI-VID-V2 deploy +203,566 and +44/+44/+66 dispatch offsets. MOBI backend sweep (H4 table) re-executed for the first time on the trunk: all 15 cells moved (ERC-735 +2.5 k from the D25 issuer check; ERC-1155 lifecycle 57,126 → 80,131 and third-party 57,126 → 63,031 from the bitmap; the rest ±60), fidelity scores unchanged; the sweep script itself had been broken since D25 (unauthorised issuers) and was fixed. Scaling (#26) re-executed. External W3C DID suite re-run on a registry-minted `did:ethr`: 335/336, identical to the fixture run | ch. 5 §5.2, §5.3.1, §5.9; README gas table; `docs/conformance/W3C_DID_TEST_SUITE.md` §8 | M1 | `4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04_pass06.json`, `mobi_vid_backends.json`, `scaling_*.json` (all 2026-10-04); `docs/conformance/reports/registry-did-2026-10-04/` | **V** |
| 24 | **External** W3C DID test suite: **335/336** after the 2026-10-03 resolver fixes (328/441 before) — identifier 3/3, core properties 88/88, production 48/48, consumption 3/3, **resolution 193/194**; per resolver ethr 78/78, mobi 58/58, nft 57/58 (the single failure is a suite vector, `did:nft:0x1:0xabc`, that is generically valid under the DID Core 3.1 ABNF and only violates did:nft's method rule) | `docs/conformance/W3C_DID_TEST_SUITE.md` | M0 | w3c/did-test-suite @ `939b31d`, implementations generated from `DIDResolver.resolve()`; raw jest reports in `docs/conformance/reports/` | **V** — the five metadata root causes (null error keys, contentType on resolve(), null metadata keys, non-XML datetime, no ABNF validation) fixed 2026-10-03; raw reports in `docs/conformance/reports/rerun-2026-10-03/` |
| 5 | VC layer 28/28, contracts 47/47 | summary | — | pytest / hardhat | **V** |
| 6 | "ERC-1056 provides **10× gas savings over ERC-721**" | `docs/thesis/README.md` RQ1 answer; README H1 | M1 | `1_blockchain-identity/scripts/benchmark_gas.js` → `4_comparison-framework/results/gas_comparison.csv` | **V, reconciled 2026-09-24** — the ratio is a function of the operation definition, now stated wherever the claim appears: (a) bare ERC-1056 `createIdentity` 52,594 vs ERC-721 `CVINVehicleNFT.mintVehicle` 542,378 (mint + VIN mapping + metadata struct + transfer record) = **10.3×** (cancun run of 2026-09-24; July values 52,612 / 542,429 give the same ratio); (b) VIN bound on both sides, `createVehicleDID` 78,068 vs `mintVehicle` 542,378 = **6.9×**; (c) the trunk's earlier 1.32× compared `createVehicleDID` with a *bare* `CVIN_NFT_DID_ERC721.mint` (102,804), which binds no VIN and is not the create-identity operation — withdrawn as a like-for-like figure and kept only as the bare-mint cost (#3). The thesis uses (b) as the headline and reports (a) as the lower bound. |
| 7 | DID creation ~45,000 gas · attribute 50,000 · delegate 55,000 | `CAPABILITIES.md` | M1 | none | **E** — design estimates; measured values in #1–2 differ (createVehicleDID also writes the VIN attribute) |
| 8 | NFT minting ~150,000 gas · transfer ~70,000 | `CAPABILITIES.md` | M1 | none | **E** — measured mint avg 102,804 |
| 9 | ERC-725 proxy creation ~350,000 gas | `CAPABILITIES.md` | M1 | none | **E** — ERC-725 has no test on the trunk |
| 10 | Resolution 50–100 ms "with blockchain lookup" | README, CAPABILITIES, thesis README | M2 | none | **E** |
| 11 | Resolution ~0.8 ms / <1 ms | `RESEARCH_THRUSTS_REPORT.md` | M0 | none | **S** |
| 12 | VC verification "5–10 ms (PKI) or 50–100 ms (blockchain)" | `CAPABILITIES.md` | M0/M2 | none | **E** — measured values are #21 (PKI 0.32 ms M0; ERC-1056 uncached 18.2 ms M1) |
| 13 | VC verify "median 7.5 ms / p95 8.9 ms (offline)" | `INVENTORY.md` | M0 | none (script not on trunk) | **S** — superseded by #21 |
| 14 | "<10 ms verification" | `README.md` | M0 | none | **E** (target from roadmap) |
| 15 | SUMO simulation "with 50 vehicles" | README, thesis README, thrusts report | — | `cv2x-testbed/sumo/` config exists; no results file | **E** — configured, not run |
| 16 | Nine standards compared | README, thesis README | M1 | 3 implemented on trunk | **B** (audit F1) |
| 17 | V2V SSI warm verify 0.165 ms [0.162, 0.168], N=30; saturation P*≈772 | bundle lineage | M0 | not on trunk | **B** |
| 18 | ERC-1056 createIdentity 52,612 · CVIN-Combined 52,178 · ERC-725xy 1,704,992 | bundle lineage | M1 | not on trunk | **B** |
| 19 | Security 43/43 attacks defended | bundle lineage | — | not on trunk | **B** |
| 20 | USD costs ("~$0.50 at 30 gwei") | `CAPABILITIES.md` | — | none | **E** — gas price and ETH price are dated; report gas units only, convert in one appendix table with the date |
| 21 | PKI vs ERC-1056 identical operations, n=50 (median / p95 ms): verify **0.321 / 0.366** PKI vs **18.158 / 23.741** ERC-1056 uncached (7 RPC calls); resolve 0.171 vs 10.058; check-revocation 0.001 vs 7.712; register 15.2 vs 16.9; issue 0.72 vs 13.5; revoke 0.02 vs 12.6 | `cv2x-testbed/results/pki_vs_erc1056.{csv,json,md}` | M0 (PKI, in-process) / M1 (ERC-1056 via local RPC) | `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py`, commit `ed85dfd`+ | **V** — with the caveats in the .md: in-process PKI is a lower bound on real PKI; local RPC floor ≈2.5 ms per round trip; ERC-1056 verify measured uncached (worst case) |
| 22 | `cv2x-testbed` ERC1056Registry gas: register 54,860 · issue (attribute) 37,779 · revoke 75,044 · deploy 878,509 | same | M1 (solc 0.8.20) | same | **V** — a *different contract* from the `1_blockchain-identity` registries in #1–2; do not merge the two columns |
| 23 | Signed BSM-like message size: PKI ≈1.08–1.11 kB (carries PEM cert) vs ERC-1056 595 B (carries DID only) | same | — | same | **V** |

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
