# Follow-up stream G-K: one-call freshness-k refresh and M5 pseudonym pool

**Date:** 2026-10-04 · **Author:** Nikhil Prakash
**Input:** `docs/AFTER_ACTION_REPORT_05.md` (stream G-K); `docs/review02/FOLLOWUP_FD.md` §3 (register #32);
`docs/LATENCY_BUDGET.md` §4 and its 2026-10-04 note; `docs/PLAN_MOBI_SUMO.md` M5 and §A.2;
`docs/REVIEW_CV2X_TESTBED_LINEAGE.md` §5 item 4; `docs/MEASUREMENT_CONDITIONS.md` §1 rules, rows #2, #22 (K-5), #32.
**Base:** `f73e81e`. Local commits, not pushed. The shared docs (register, README, handoffs, index,
after-action reports, LATENCY_BUDGET) are not edited here; §6 holds the proposed register text.

## 1. Commits

| Commit | Scope |
|---|---|
| `f660402` | Code: `ERC1056Provider(refresh_mode='full'|'probe')`; `experiment_freshness_k.py --refresh-mode/--rotation` + probe micro-benchmark; `cv2x-testbed/tests/test_freshness_k_probe.py` (24) |
| `dd31d22` | Results: `cv2x-testbed/results/freshness_k_probe_fullref.*` (full mode, replicate 1), from clean tree `f660402` |
| `fbbb4e9` | Results: `cv2x-testbed/results/freshness_k_probe.*` (probe mode, replicate 1), from clean tree `dd31d22` |
| `e49bcb4` | Code: `1_blockchain-identity/scripts/experiment_pseudonym_pool.js`; `test/ERC1056/PseudonymPool.test.js` (8) |
| `439b118` | Results: `4_comparison-framework/results/pseudonym_pool.{json,md}`, from clean tree `e49bcb4` |
| `22a556f` | Results: `freshness_k_probe_r2.*` (probe, replicate 2), from clean tree `439b118` |
| `4355630` | Results: `freshness_k_probe_fullref_r2.*` (full, replicate 2), from clean tree `22a556f` |
| (this file) | report |

**#32's run of record (`cv2x-testbed/results/freshness_k.*`) is untouched.** All new runs went to new files.

Tests:
- `cv2x-testbed/tests`: 132 passed against a node on :8557 (the 24 new ones included).
  - Run against the previous provider and script (`f73e81e`), all 24 new tests fail.
  - The #32 tests (`test_freshness_k.py`, incl. "k = 1 keeps #21's RPC pattern") pass unchanged. A new test pins
    the same pattern for `refresh_mode='full'`.
- `1_blockchain-identity`: `test/ERC1056/*.js` 51 passing (8 new). The new test `require`s the experiment
  module, so it fails without it.

## 2. Environment

| Item | Value |
|---|---|
| CPU | Intel Xeon Processor **@ 2.80 GHz**, 4 vCPU; Linux 6.18.44. **#32 ran on a 2.10 GHz host.** |
| Python / web3 / cryptography / numpy | 3.11.15 / 8.0.0 / 49.0.0 / as in #32 |
| Node / Hardhat | v22.22.0 / 2.28.6 (from `1_blockchain-identity`) |
| Chain (freshness-k) | `hardhat node --port 8557`, id 31337, automine. A fresh node (block 0) before each of the 4 runs, killed by PID. `hardhat_version` reads `None` in the result files: the script looks in `cv2x-testbed/node_modules`, which does not exist |
| Contracts (freshness-k) | tracked cv2x artifacts. `scripts/check_artifacts_fresh.js` exit 0 before the runs. ERC1056Registry deploy 927,756 gas, bytecode sha256 `8ca9cfe5…5812` (= #32) |
| Chain (M5) | Hardhat in-process network. `EthereumDIDRegistry` compiled solc 0.8.24, optimizer 200, viaIR, cancun; deploy 958,726 gas |
| git | `git_dirty: false` in all five result files |
| Host load | **Other sessions shared the host.** Replicate 1 of freshness-k ran at load ≈1.7 on 4 vCPU, with parallel Hardhat benchmark jobs. Replicate 2 ran at load ≈0.5, after those jobs ended. Both modes were run in each replicate, in opposite order (r1: full then probe; r2: probe then full) |

**Development runs, disclosed:**
- M5: two development runs, with the same results file path. Their outputs were deleted before the
  run of record.
  - The first run had the pre-registered band, query and schemes already fixed.
  - The second run replaced a described (not executed) funding query with an executed transaction-layer scan.
  - The gas figures were identical in both.
- Freshness-k: none beyond the test suite.

## 3. One-call refresh for freshness-k

### 3.1 Method
- **Probe mode.** `refresh_mode='probe'` changes only what a refresh does. Message counting, the k schedule and T-9
  (run first, before the cache and any RPC) are unchanged.
  - At a sender's refresh the verifier sends **one** JSON-RPC `eth_call` of `getIdentityInfo(identity)`. The call is
    pre-encoded and sent straight to the HTTP provider, so web3's middleware cannot add two `eth_chainId` requests.
    The result is decoded locally.
  - It returns owner, the `changed` block, the revoked flag and revokedAt in that single call.
  - If owner, `changed` and revoked equal the cached values, the cache is kept and its counter restarts.
  - Otherwise the full resolution runs (the `eth_getLogs` walk), reusing the probe's result.
  - A cached key whose `validTo` lies within `CLOCK_SKEW_S` of the wall clock is never kept on a probe. Time-based
    expiry does not move `changed`.
  - With k = 1 the state is cached but probed on every message, so there is zero staleness.
- **Why one probe sees every change.** Every write to an identity in the cv2x registry moves `changed`. This covers
  `revokeIdentity`, `updateVehicleKey`, set/revoke attribute and owner/delegate changes. Tests cover the first three
  on chain.
- **Default unchanged.** The default stays `'full'`, which is #32's code path.
- **Sweep.** The F-D protocol, unchanged:
  - k ∈ {1, 5, 25, ∞}, n = 250 per k, 3 discarded warm-ups, a fresh verifier per k, one sender;
  - revocation staleness for every phase m_pre ∈ 1..k (5 trials for k = 1; {1, 5, 25} for ∞).
- **New: Part 3 (key rotation).** `updateVehicleKey` is called mid-stream:
  - count the new-key messages rejected before the first acceptance;
  - then check that an old-key message is rejected.
- **Constants (unchanged definitions).** t_local = median at k = ∞; t_chain = median at k = 1 − t_local. In probe
  mode t_chain is therefore **t_chain_probe**.
- **Direct probe micro-benchmark.** The refresh call alone, n = 250, reported next to #32's `isRevoked` reference.

### 3.2 Results (ms, Hardhat local, M1)

**Constants per run:**

| Run | mode | t_local | t_chain | RPCs per refresh | probe call alone, median / p95 (1 RPC) | `isRevoked` via web3 (3 RPCs) |
|---|---|---:|---:|---:|---:|---:|
| r1 | full | 0.529 | 14.377 | 4 | 2.786 / 4.724 | 8.874 |
| r1 | **probe** | 0.540 | **2.758** | **1** | 2.289 / 4.188 | 7.023 |
| r2 | **probe** | 0.490 | **2.888** | **1** | 2.489 / 4.377 | 6.965 |
| r2 | full | 0.516 | 10.284 | 4 | 2.335 / 3.219 | 7.762 |
| #32 (2.10 GHz host) | full | 0.428 | 10.518 | 4 | – | 6.809 |

- **t_chain_probe = 2.76–2.89 ms** (in-sweep), and **2.29–2.79 ms** for the probe call alone.
- That is **3.6–5.2× cheaper than a full refresh** in the same replicate (10.3–14.4 ms).
- It is also **2.4–2.8× cheaper than the "one eth_call" (6.8 ms) behind FOLLOWUP_FD's ≈95 prediction**. That
  prediction used `isRevoked` through web3's contract wrapper: 3 HTTP requests, two of them `eth_chainId`.

**Measured mean and P\*(0.5) = ⌊50 / mean⌋:**

| k | full r1 | full r2 | **probe r1** | **probe r2** | #32 (full) |
|---|---:|---:|---:|---:|---:|
| 1 | 15.48 → **3** | 11.40 → **4** | 3.65 → **13** | 4.02 → **12** | 11.76 → 4 |
| 5 | 3.69 → **13** | 2.71 → **18** | 1.24 → **40** | 1.58 → **31** | 2.38 → 21 |
| 25 | 1.24 → **40** | 0.99 → **50** | 0.70 → **71** | 0.79 → **63** | 0.85 → 58 |
| ∞ | 0.65 → **77** | 0.62 → **80** | 0.64 → **78** | 0.57 → **87** | 0.45 → 110 |

- **Refresh accounting** (all four runs): the window holds exactly n/k refreshes.
  - In probe mode **0** of them needed a full resolution.
  - The unchanged identity was answered by the probe each time; the full resolution ran only at first contact,
    during warm-up.
- **Medians and p95 per k** are in the `.md`/`.csv` files.
- **Fit.** The measured means lie **above** the analytic t_local + t_chain/k by +4 % to +48 %, every one of them.
  This is looser than #32's ±7 %, for two reasons:
  - medians feed the constants, and on the shared host the means carry a jitter tail (k = ∞: +17 to +23 %);
  - in probe r2 a refresh inside a cached stream (k = 5/25: median 4.8 ms) cost more than one at k = 1 (3.4 ms).
    The worst case is k = 5 in probe r2, at +48 %.

  The P\* values below use the measured means, not the curve.

### 3.3 The P\* = 100 knee

| Estimate | full refresh | one-call (probe) refresh |
|---|---|---|
| FOLLOWUP_FD (#32 constants) | ≈146 | **≈95 predicted** (t_chain = 6.81) |
| This stream, measured t_local | **none**: no k reaches P\*(0.5) = 100 in r1 or r2 (t_local 0.529 / 0.516 ≥ 0.5 ms) | **none** in r1 (t_local 0.540); **≈279** in r2 (t_local 0.490, 2.888 / 0.010: ill-conditioned) |
| This stream's t_chain with #32's t_local 0.428 (sensitivity, mixes runs) | 143–200 | **38–40** |
| Measured P\*(0.5) at k = ∞ (the ceiling) | 77 / 80 | 78 / 87 |

**Verdict on the "≈95" prediction: not confirmed as stated.**
- **The refresh did better than predicted:** 2.8 ms rather than 6.8 ms.
- **But on this host no finite k reaches P\*(0.5) = 100 in either mode.** Even k = ∞ gives 77–87.
  - The knee formula t_chain / (0.5 − t_local) is dominated by the cached-path cost t_local, which here sits at
    0.49–0.54 ms, not by the refresh.
  - At #32's t_local (0.428 ms) the one-call knee would be ≈40.
  - **Conclusion:** the dense-traffic threshold is decided by t_local (T-9 check + secp256k1 verify in Python), and
    "the knee" should not be quoted as a single k without the t_local it was computed with.
- **What the one-call refresh does buy, robustly in both replicates:**
  - **k = 1 with zero staleness goes from P\*(0.5) = 3–4 to 12–13** (≈3.5×);
  - k = 5 goes from 13–18 to 31–40;
  - k = 25 goes from 40–50 to 63–71.

### 3.4 Staleness bound (both modes, both replicates)

| Change mid-stream | k = 1 | k = 5 | k = 25 | k = ∞ |
|---|---|---|---|---|
| `revokeIdentity`: max accepted after it was mined | 0 | 4 | 24 | ≥ 50 (cap) |
| `updateVehicleKey`: max new-key messages rejected before refresh | 0 | 4 | 24 | ≥ 50 (cap) |

- **Bound = k − 1, and it holds in every run.** All 35 finite-k trials per change, per mode, per replicate (140
  revocation + 140 rotation trials) equal the phase prediction k − 1 − ((m_pre − 1) mod k).
- After each refresh the revoked identity stays rejected, and an old-key message is rejected.
- The probe therefore detects `revokeIdentity` and key changes at the next refresh. It is exactly as stale as the
  full refresh, and no staler.
- The tests add `revokeAttribute` on the signing key: rejected at the very next probe (k = 1).

### 3.5 Threats
1. **Different host from #32** (2.80 vs 2.10 GHz vCPU), and it shares the CPU with other sessions.
   - t_local rose from 0.428 to 0.49–0.54 ms, which by itself removes the P\* = 100 knee.
   - **Between-run absolute numbers are not comparable with #32.** Compare modes within a replicate only.
   - The probe/full ratio of t_chain (3.6–5.2×) and the P\* gains are consistent across the two replicates; the
     absolute values are not.
2. **Part of the gain is client overhead.** About half the full-refresh RPCs are web3's `eth_chainId` calls. The
   probe avoids them by calling the HTTP provider directly, and the full path still pays them. A full resolution
   rewritten the same way would also be cheaper; this was not measured.
3. **M1 only.** On a public RPC endpoint a refresh is one network round trip in probe mode, versus 2+ for a full
   resolution. The ordering holds there; the ms values do not.
4. **K-5.** This is the cv2x `ERC1056Registry`. On `EthereumDIDRegistry` the same probe is `changed(identity)`
   alone. There is no registry revoked flag there; revocation = attribute/owner change, which also moves `changed`.
5. **Unchanged identity in the latency sweep.** The sweep measures the common case. A sender that changes often pays
   probe + full resolution (> full) at those refreshes.
6. **Expiry guard.** A key within 900 s of its `validTo` forces full resolutions. The registered keys here are far
   from expiry, so this path is not in the timings.

## 4. M5 pseudonym pool on ERC-1056 (pre-registered)

### 4.1 Pre-registration and operationalisation

**Pre-registered (verbatim from PLAN_MOBI_SUMO §A.2):**
- **Hypothesis:** "a 20-delegate pseudonym pool costs ≈20 × addDelegate (≈1.44 M gas) per rotation epoch and is
  fully linkable from chain data (all delegates hang off one identity) — i.e. ERC-1056 delegates give *key*
  rotation, not *identity* unlinkability, unlike SCMS pseudonyms".
- **Metric:** gas; linkability yes/no with the linking query shown.
- **Consequence:** the privacy section states that SSI-on-Ethereum needs per-pseudonym identities.

**Fixed in the script before the first run:**
- **"≈1.44 M":** every epoch lies within **±10 % of 20 × 72,219 = 1,444,380**. 72,219 is register row #2's
  addDelegate.
- **"Fully linkable":** both of the following hold.
  1. One `eth_getLogs` (DIDDelegateChanged, topic1 = identity) returns all 20 pseudonyms of every epoch.
  2. One pseudonym address alone leads to the others.

**Setup:**
- Standard `EthereumDIDRegistry` (`1_blockchain-identity/contracts/ERC1056/`).
- Pool of 20 `veriKey` delegates with `validity = 300 s`, rotated every 5 min of simulated time
  (`evm_increaseTime` + `evm_mine`), over 3 epochs.
- Pseudonym keys are deterministic, so gas is reproducible to the unit.

### 4.2 Results

**Gas per epoch (delegate pool):**

| epoch | addDelegate gas | epoch gas | ÷ 1,444,380 |
|---:|---|---:|---:|
| 0 | 71,919 (identity's first change) + 19 × 54,807–54,819 | **1,113,456** | 0.771 |
| 1 | 20 × 54,807–54,819 | **1,096,368** | 0.759 |
| 2 | 20 × 54,807–54,819 | **1,096,368** | 0.759 |

- **Why ≈54.8 k, not 72 k:**
  - Only an identity's first registry write pays `changed` 0 → non-zero (≈ +17.1 k).
  - Every later addDelegate rewrites a non-zero `changed`.
  - The pre-registration priced all 20 at the first-write price.
- **Spread:** the 12-gas steps are EIP-2028 zero bytes in the pseudonym address.
- **Steady state:** ≈1.10 M gas per vehicle per 5 min (≈316 M gas per vehicle-day), plus 20 storage slots per epoch
  that are never cleared.
- **Rotation works:** each epoch's 20 delegates were valid during it, and all had expired after the next
  `evm_increaseTime(300)`.

**The linking query (scheme A):**

```
eth_getLogs { address: <registry>, fromBlock: 0, toBlock: "latest",
              topics: [ keccak("DIDDelegateChanged(address,bytes32,address,uint256,uint256)"),
                        0x000…00<vehicle identity> ] }
```

- It returned **60 logs = 60 distinct pseudonyms** (20/20 per epoch).
- **From one pseudonym:**
  - scan all DIDDelegateChanged logs for `delegate == P`; this finds 1 identity (the vehicle);
  - the identity query above then reaches all 60.
- **Linkable: YES.**

**Alternative: per-pseudonym identities.** Each pseudonym is its own `did:ethr:<P>`, created implicitly at 0 gas.

| variant | on chain per pseudonym | epoch gas (20) | same query links? | residual chain-layer linkage (executed scan of every block's transactions) |
|---|---|---:|:---:|---|
| B0 no attributes | nothing | **0** | **no** | none: no transaction touches any pseudonym |
| B1 self-sent attribute | vehicle transfer (21,000) + `setAttribute` (51,728–51,740) | 1,454,728 | **no** | **linkable by funding**: 60/60 pseudonyms funded by one address |
| B2 relayed attribute | relayer's `setAttributeSigned` (79,328–79,352) | 1,586,908 | **no** | linked to the relayer (60 writes, one sender). The anonymity set is the relayer's client population (1 here) |

- For every pseudonym the identity query and an "all registry events with topic1 = P" query return only P's own
  events: 0 for B0, 1 for B1/B2. None mentions another pseudonym.
- `identityOwner(P) == P` for all.

### 4.3 Verdicts (as measured)

| Pre-registered claim | Measured | Verdict |
|---|---|---|
| ≈20 × addDelegate ≈ 1.44 M gas per epoch (±10 %) | 1,113,456 / 1,096,368 / 1,096,368 (0.76–0.77×) | **FAIL**: ≈23 % cheaper, because only the first write per identity pays the `changed` 0 → non-zero cost |
| Fully linkable from chain data | YES: one query returns all 20 per epoch (60/60); one pseudonym reaches all 60 | **PASS** |
| Consequence: per-pseudonym identities instead, "cheap since creation is implicit" | creation 0 gas, and the same query links nothing (B0/B1/B2) | **Supported, with two qualifications**: (a) cheap only while no attribute is written. With a per-pseudonym attribute it costs *more* than the delegate pool (1.45–1.59 M vs 1.10 M per epoch). (b) A self-funded write re-links the pseudonyms through the funding transfers; a relayer moves the link to the relayer's anonymity set |

**Comparison with SCMS (structural, not measured):**
- SCMS pseudonym certificates are unlinkable to outsiders by construction: butterfly key expansion, with linkage
  values split across two linkage authorities.
- They cost nothing on chain.
- ERC-1056 delegates provide key rotation only.
- B0 matches SCMS's outsider-unlinkability at the chain layer, but **without** SCMS's revocation-by-linkage-seed. A
  B0 pseudonym cannot be revoked as a group: there is nothing on chain to revoke.

### 4.4 Threats
1. **Chain layer only.** Radio identifiers, timing and position traces are outside the test.
   - With a delegate pool, a V2V message must name the identity DID for the delegate to be checked, so off-chain
     linkage is total anyway.
2. **The ±10 % band is this stream's operationalisation**, fixed before the first run. With any band narrower than
   ±23 % the gas verdict is FAIL; with a wider one it is PASS.
3. **72,219 vs 71,919.** Row #2's addDelegate was measured by `benchmark_gas.js` with other inputs. The 300-gas
   difference from this run's first-write figure was not analysed.
4. **B2's anonymity set** is 1 vehicle in the simulation. B1's funding link could be broken by funding through a mixer
   or exchange; that was not modelled.
5. **M1.** Gas is exact and transfers to a public chain at the same compiler settings.

## 5. SC-02 note (for `docs/SCOPE_CHANGES.md`)

> **SC-02 — partially closed 2026-10-04 (stream G-K, M5).** A bounded on-chain observability analysis for
> pseudonymity was run as pre-registered (PLAN_MOBI_SUMO §A.2): `4_comparison-framework/results/pseudonym_pool.*`,
> register row #37.
>
> - **The 20-delegate pool on the standard ERC-1056 registry is fully linkable.** A passive observer needs one
>   `eth_getLogs` by identity topic. The pool costs ≈1.10 M gas per 5-minute epoch, not the pre-registered ≈1.44 M
>   (gas claim FAIL).
> - **Per-pseudonym `did:ethr` identities are not linkable by that query.** They cost 0 gas while they need no
>   on-chain attribute.
> - **Once an attribute is written,** pseudonyms are re-linked by their funding transactions when self-funded, or
>   share a relayer's anonymity set when relayed. Either way they cost more than the pool.
>
> **Still deferred:** radio/timing/position linkability, group revocation for implicit pseudonyms, and a measured
> SCMS baseline. These stay future work.

## 6. Proposed register rows (session to apply; `MEASUREMENT_CONDITIONS.md` not edited)

**#36 (new): Freshness-k with a one-call (probe) refresh, cv2x ERC-1056 verify.**
- **Claim:** a refresh is one `getIdentityInfo` eth_call (1 RPC), with full resolution only when the identity moved.
  - **t_chain_probe = 2.76 / 2.89 ms**, against 14.38 / 10.28 ms for the full refresh in the same replicates (r1 / r2).
  - Measured P\*(0.5) from the mean, probe vs full, by k:

    | k | probe | full |
    |---|---:|---:|
    | 1 | 13 / 12 | 3 / 4 |
    | 5 | 40 / 31 | 13 / 18 |
    | 25 | 71 / 63 | 40 / 50 |
    | ∞ | 78 / 87 | 77 / 80 |

  - **No finite k reaches P\*(0.5) = 100 on this host in either mode**, because t_local = 0.49–0.54 ms. FOLLOWUP_FD's
    "≈95 for one-call" is not confirmed. At #32's t_local (0.428 ms) this t_chain_probe gives ≈40.
- **Staleness:** revocation and key rotation are seen at the next refresh, at most k − 1 = 0 / 4 / 24 messages late.
  Every one of the 280 finite-k trials equals the phase prediction, in both modes.
- **Condition:** M0/M1, Hardhat 2.28.6, chain 31337, automine. The host is a 2.80 GHz Xeon shared with other sessions
  (≠ #32's host).
- **Source:** `cv2x-testbed/scripts/experiment_freshness_k.py --deploy --refresh-mode {probe,full} --rotation`, code
  `f660402`. Results:
  - `results/freshness_k_probe{,_r2}.*` (`fbbb4e9`, `22a556f`);
  - `results/freshness_k_probe_fullref{,_r2}.*` (`dd31d22`, `4355630`).
- **Status:** **V** for the within-replicate mode comparison and the staleness bound. Absolute ms and the knee are
  **host-dependent**: do not mix with #32. Caveats K-5, M1-only, one sender, unchanged identity in the latency sweep.
- **Consequence:**
  - LATENCY_BUDGET §4 should quote the knee together with its t_local;
  - the probe refresh becomes the recommended verifier design (k = 1 probe: zero staleness at ≈3.5× the P\* of the
    full refresh).

**#37 (new): M5 pseudonym pool on `EthereumDIDRegistry` (pre-registered, PLAN_MOBI_SUMO §A.2).**
- **Claim, delegate pool:** 20 `addDelegate` per 5-min epoch cost **1,113,456** gas (first epoch), then
  **1,096,368** per epoch. Per call: 71,919 for the identity's first write, then 54,807–54,819.
- **Gas verdict: FAIL.** The measured epoch is 0.76× the pre-registered ≈1.44 M, outside ±10 %.
- **Linkability verdict: YES (PASS).** One `eth_getLogs` (DIDDelegateChanged, topic1 = identity) returns all 20
  pseudonyms per epoch (60/60), and one pseudonym reaches all 60 through its identity.
- **Alternative, per-pseudonym `did:ethr`:**
  - 0 gas, and not linkable by the same query;
  - with a per-pseudonym attribute: 1,454,728 (self-funded; re-linked by funding transfers) or 1,586,908 (relayed;
    linked to the relayer) gas per epoch.
- **Condition:** M1, solc 0.8.24 / opt 200 / viaIR / cancun, Hardhat 2.28.6 in-process.
- **Source:** `1_blockchain-identity/scripts/experiment_pseudonym_pool.js` and `test/ERC1056/PseudonymPool.test.js`
  (pins the gas), code `e49bcb4`. Results `4_comparison-framework/results/pseudonym_pool.{json,md}` (`439b118`,
  git_dirty false).
- **Status:** **V** (gas exact). Linkability is chain-layer only, and the SCMS comparison is structural.
- **Consequence:** SC-02 partially closed (§5). The privacy section states:
  - delegates give key rotation, not unlinkability;
  - per-pseudonym identities are unlinkable on chain only while they write nothing, or write through a shared relayer.
