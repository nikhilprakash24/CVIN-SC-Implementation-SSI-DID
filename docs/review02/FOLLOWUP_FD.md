# Follow-up stream F-D: freshness-k sweep and M4 lifecycle parity

**Date:** 2026-10-04 · **Author:** Nikhil Prakash
**Input:** `docs/review02/AAR_REVIEW2_04.md` (stream F-D); `docs/REVIEW_CV2X_TESTBED_LINEAGE.md` §5.1 and
§3.3; `docs/LATENCY_BUDGET.md` §4; `docs/PLAN_MOBI_SUMO.md` M4 and its pre-registration (§A.2);
`docs/MEASUREMENT_CONDITIONS.md` §1 and rows #21–#23; `docs/review02/PASS2_T.md`.
**Base:** `d2e6a58`. Local commits, not pushed. The shared docs (register, README, handoffs, index,
after-action reports) are not edited here; §6 holds the proposed register text.

## 1. Commits

| Commit | Scope |
|---|---|
| `8216507` | Code: `ERC1056Provider(refresh_every=k)`; `identity/lifecycle_backends.py`; `scripts/experiment_freshness_k.py`; `scripts/experiment_lifecycle_parity.py`; `tests/test_freshness_k.py` (22), `tests/test_lifecycle_parity.py` (6) |
| `bcff389` | Results: `cv2x-testbed/results/freshness_k.{json,csv,md,png}`, generated from clean tree `8216507` |
| `0a667ec` | Results: `cv2x-testbed/results/lifecycle_parity.{json,csv,md}`, generated from clean tree `bcff389` |
| (this file) | report |

Both scripts are **siblings** of `experiment_pki_vs_erc1056.py`. They import its harness (`measure`,
`summarize`, `RPCCounter`, `environment`, `deploy_registry`, `configure_freshness`, `make_bsm`)
without changing it. The #21 script and its results (`results/pki_vs_erc1056.*`) are untouched. The
provider's default is `refresh_every=1`, which is the #21 code path plus one counter increment and one
comparison. A test asserts that k = 1 keeps #21's RPC pattern: `eth_call` + `eth_getLogs`, with no
`isRevoked` call.

Tests: the full `cv2x-testbed/tests` suite passes against the node: 104 passed (76 before this
stream, plus 28 new). It was run with `CV2X_TEST_RPC_URL=http://127.0.0.1:8554` and the default
`CV2X_TEST_ARTIFACTS_DIR`. The new tests import `set_refresh_every`, `lifecycle_backends` and the two
scripts, so without the feature they fail.

## 2. Environment (both runs)

| Item | Value |
|---|---|
| CPU | Intel Xeon Processor @ 2.10 GHz, 4 vCPU; Linux 6.18.44 |
| Python / numpy / matplotlib | 3.11.15 / 2.4.6 / 3.11.2 |
| cryptography / web3 | 49.0.0 / 8.0.0 |
| Node / Hardhat | v22.22.0 / 2.28.6 (lockfile version, §5.E), started from `1_blockchain-identity` on :8554 and killed by PID |
| Chain | id 31337, **automine, no interval mining**, fresh node (block 0) before the freshness-k run; the M4 run followed on the same node |
| Contracts | tracked `cv2x-testbed/artifacts` (solc 0.8.20, opt 200, paris), confirmed fresh by `scripts/check_artifacts_fresh.js` (exit 0) before the runs. ERC1056Registry deploy **927,756** gas (= #22), bytecode sha256 `8ca9cfe5…5812`. MOBIVIDRegistryV2 deploy **5,023,352** gas. The tracked artifacts carry no build-info, so `registry_compiler`/`mobi_compiler` read `None`; the freshness check covers this |
| T-9 policy | 1.0 s past / 0.1 s future, replay cache on (65,536), installed identically on every verifier |
| git | `git_dirty: false` in both result files (commits `8216507`, `bcff389`) |

Development runs of both scripts were made before these runs: freshness-k at n = 50 and M4 at n = 30.
They were written to a scratch directory and not committed. They are disclosed because M4 is
pre-registered as "a single full run". The M4 operationalisation constants (§4.1) were in the script
before the first development run and were not changed afterwards. One post-hoc diagnostic row was
added after it (§4.3).

## 3. Freshness-k (review §5.1, LATENCY_BUDGET §4)

### 3.1 Method
- **Parameter.** `ERC1056Provider(refresh_every=k)` re-reads a sender's state from the registry every
  k messages **per sender** (keyed by canonical DID). The state is the key plus the revocation flag,
  read via `getIdentityInfo` + `eth_getLogs` replay. Message 1 resolves; messages 2..k use the cache;
  message k+1 resolves again. k = 1 never caches. k = ∞ (`None`) resolves once.
- **T-9 runs first, for every k.** A replay or stale packet is rejected before the cache and before any
  RPC. This is tested.
- **Latency.** For each k there is a fresh verifier and one registered sender. There are 3 discarded
  warm-ups, then **n = 250** consecutive genuine messages. 250 is divisible by 1, 5 and 25, so each
  window holds exactly n/k refreshes. Median, p95 and **mean** are reported. The mean is the amortised
  per-message cost, which is what t_eff and P* describe.
- **Constants recomputed from this run.**
  - t_local = median verify at k = ∞: the cached path, with the T-9 check and secp256k1 verify, 0 RPCs.
  - t_chain = median verify at k = 1 − t_local.
  - As a reference, one registry `eth_call` (`isRevoked`) was measured too. This is the quantity
    LATENCY_BUDGET's 2.5 ms stood for.
- **Staleness.** For every phase m_pre ∈ 1..k (5 trials for k = 1; m_pre ∈ {1, 5, 25} for ∞):
  1. Register a fresh sender and accept m_pre messages.
  2. Call `revokeIdentity` and wait for the receipt, so the revocation is mined.
  3. Verify fresh, genuine, in-window messages until the first rejection. The cap is k + 5, or 50 for ∞.
  4. Check that 2 further messages are also rejected.

### 3.2 Results (ms; Hardhat local, M1)

| k | median | p95 | **mean** | analytic t_local + t_chain/k (this run) | mean / analytic | LATENCY_BUDGET 0.4 + 2.5/k | refreshes in window | RPCs: refresh / cached |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 10.946 | 16.153 | **11.756** | 10.946 | 1.07 | 2.900 | 250/250 | 4 / – |
| 5 | 0.456 | 10.479 | **2.379** | 2.532 | 0.94 | 0.900 | 50/250 | 4 / 0 |
| 25 | 0.425 | 0.764 | **0.850** | 0.849 | 1.00 | 0.500 | 10/250 | 4 / 0 |
| ∞ | 0.428 | 0.631 | **0.453** | 0.428 | 1.06 | 0.400 | 0/250 | – / 0 |

- **Constants, this run:**
  - **t_local = 0.428 ms** (LATENCY_BUDGET: 0.4).
  - **t_chain = 10.518 ms** (LATENCY_BUDGET: 2.5). The provider-internal resolution time at k = 1 has
    a median of 10.258 ms.
  - One `isRevoked` eth_call costs **6.809 / 10.292 ms** (median / p95, 3 RPCs including web3's two
    `eth_chainId`).
- **Why t_chain is 4× LATENCY_BUDGET's figure:**
  - A refresh here is a *full resolution* (4 RPCs), not a single `changed()` probe.
  - One eth_call on this host costs 6.8 ms, not 2.5 ms. The #21 run measured 5.81 ms for the same call.
- **Model fit.** The analytic curve matches the measured **means** within −6 % / +7 % at every k.

**P\*(f) = ⌊f · 100 ms / t⌋, from the measured mean:**

| f | k = 1 | k = 5 | k = 25 | k = ∞ |
|---|---:|---:|---:|---:|
| 0.25 | 2 | 10 | 29 | 55 |
| **0.5** | **4** | **21** | **58** | **110** |
| 1.0 | 8 | 42 | 117 | 220 |

For comparison, P\*(0.5) under the other estimates:

| Estimate | k = 1 | k = 5 | k = 25 | k = ∞ |
|---|---:|---:|---:|---:|
| Analytic, this run | 4 | 19 | 58 | 116 |
| Analytic, LATENCY_BUDGET constants | 17 | 55 | 100 | 125 |
| Analytic, hypothetical one-call refresh (t_local + 6.81/k; not implemented) | 6 | 27 | 71 | 116 |

**What this does to LATENCY_BUDGET §4:**
- **The shape holds.** t_eff = t_local + t_chain/k is confirmed, and the measured means sit on the curve.
- **The design point does not hold on this host.** §4 put the knee (P\*(0.5) = 100) at k ≈ 25. With
  this run's constants it sits at:
  - **k ≈ 146** for a full-resolution refresh;
  - **k ≈ 95** for a one-call refresh.
- **At k = 25 the measured P\*(0.5) is 58, not 100.**
- **Cause.** t_local (0.428 ms) leaves only 0.07 ms of headroom under the 0.5 ms per message that
  P\*(0.5) = 100 needs. Fully cached (k = ∞), P\*(0.5) is 110: just above the dense-traffic threshold.

### 3.3 Staleness bound (revoke the key mid-stream)

| k | trials | messages accepted **after** the revocation was mined (m_pre = 1, 2, …) | max | bound | within bound | = prediction k−1−((m_pre−1) mod k) | rejected thereafter |
|---|---:|---|---:|---:|:---:|:---:|:---:|
| 1 | 5 | 0, 0, 0, 0, 0 | **0** | 0 | yes | yes | yes |
| 5 | 5 | 4, 3, 2, 1, 0 | **4** | 4 | yes | yes | yes |
| 25 | 25 | 24, 23, …, 1, 0 | **24** | 24 | yes | yes | yes |
| ∞ | 3 | 50+, 50+, 50+ (cap) | **≥ 50** | none | – | – | – |

**The security trade-off, stated:**
- **k = 1.** A revocation takes effect at the very next message.
- **k > 1.** It takes effect at the sender's next refresh, so up to **k − 1 messages** from a revoked
  vehicle are still accepted. The measured maximum equals k − 1 exactly, and every trial matches the
  phase prediction. At 10 Hz BSMs this is a window of up to:
  - **0.4 s at k = 5**;
  - **2.4 s at k = 25**;
  - **≈ 14.5 s at the knee k ≈ 146**.
- **k = ∞.** A verifier that has cached a sender never sees its revocation.
- **Rotations.** A key rotation is subject to the same bound: the old key keeps verifying and the new
  key fails until the next refresh. It was not measured separately.
- **T-9 does not cover this.** T-9's 1.0 s window bounds message *age*, not *state* staleness; the two
  are independent.

## 4. M4 lifecycle parity (PLAN_MOBI_SUMO §A.2)

### 4.1 Pre-registration and operationalisation

**Pre-registered (verbatim from §A.2):**
- **Hypothesis:** "the centralized registry is ≥10× faster than MOBI-VID-V2 for birth and lifecycle
  writes (local), equal for history queries once the chain history is cached".
- **Metric:** median/p95 ms, n = 50, plus gas for chain writes.
- **Stopping rule:** none; a single full run.
- **Threat:** the centralized registry is in-process.

The pre-registration gives no numeric test, so the script fixes one (before any run):
- **≥10×:** the ratio of medians, MOBI / centralized, is ≥ 10. It is judged per write.
- **Lifecycle writes:** the lifecycle event and the ownership transfer.
- **Equal:** the median ratio lies in **[0.5, 2.0]**.
- **"Cached":** the MOBI history rendered from a local copy of the chain history, with no RPC.

**Backends** (`identity/lifecycle_backends.py`, one interface):
- **`centralized_registry`:** `CentralizedVehicleRegistry`, in-process.
- **`mobi_vid_v2`:**
  - birth is `MOBIVIDProvider.register_vehicle_birth`: salted VIN hash, HKDF + AES-GCM VIN, then the
    `registerVehicleBirth` transaction;
  - `recordLifecycleEvent` (by an authorised service centre), `transferVehicleOwnership` (signed by the
    current owner) and the history getters are called directly on `MOBIVIDRegistryV2`.

**Inputs:**
- Events and transfers each run on one vehicle, with n + 3 operations.
- History is queried on a vehicle with **10 events and 2 transfers**.

### 4.2 Results (ms; gas = receipt)

| Operation | centralized median / p95 | MOBI-VID-V2 median / p95 | MOBI RPCs | MOBI gas | ratio (median) | ratio (p95) |
|---|---:|---:|---:|---:|---:|---:|
| birth | 0.0028 / 0.0076 | 14.131 / 20.765 | 6 | 398,298 (398,274–398,298) | ≈4,980× | ≈2,740× |
| lifecycle_event | 0.0064 / 0.0109 | 11.860 / 14.883 | 5 | 255,267 (255,243–255,267) | ≈1,850× | ≈1,360× |
| ownership_transfer | 0.0019 / 0.0033 | 11.509 / 14.843 | 5 | 182,144 | ≈5,930× | ≈4,560× |
| history_query, MOBI uncached | 0.2403 / 0.2863 | 89.904 / 111.269 | 39 | – | 374× | 389× |
| history_query, MOBI cached | 0.2403 / 0.2863 | 0.0174 / 0.0189 | 0 | – | **0.072×** | 0.066× |
| history_query, MOBI cached + validated (2 eth_calls) | 0.2403 / 0.2863 | 12.086 / 16.455 | 6 | – | 50× | 57× |
| *post-hoc diagnostic:* centralized history without `asdict` | 0.0005 / 0.0007 | (cached) 0.0174 | – | – | 33× | 25× |

Gas notes:
- The spreads are EIP-2028 calldata pricing, as in #22: up to 24 gas from random hashes and addresses.
- These are the cv2x-testbed `MOBIVIDRegistryV2` (solc 0.8.20/paris), not the `1_blockchain-identity`
  MOBI-VID-V2 of #25/#30.

### 4.3 Pre-registered verdicts (reported as measured)

| Claim | Verdict |
|---|---|
| Centralized ≥10× faster: **birth** | **PASS** (≈4,980×) |
| Centralized ≥10× faster: **lifecycle event** | **PASS** (≈1,850×) |
| Centralized ≥10× faster: **ownership transfer** | **PASS** (≈5,930×) |
| **Equal** for history queries once cached | **FAIL**: ratio 0.072, outside [0.5, 2.0]. The cached MOBI history is ≈14× *faster* than the centralized query |

**Why the history claim fails (post-hoc reading; not part of the pre-registration):**
- **Both paths are local.** The ratio is set by local serialisation code, not by the substrate.
- **The centralized side.** `get_vehicle_history` serialises with `dataclasses.asdict` + isoformat,
  which takes 0.24 ms. The adapter's MOBI rendering of the cached tuples is a plain dict comprehension,
  which takes 0.017 ms.
- **The diagnostic row reverses the order.** It was added after a development run showed this. Without
  `asdict` the centralized lookup takes 0.0005 ms, 33× faster than MOBI cached. "Equal" therefore fails
  in either direction, depending on serialisation.
- **The substantive point.** Once cached, both are ≤ 0.25 ms. This is two or more orders of magnitude
  below any chain read: 12 ms with a 2-call staleness probe, 90 ms uncached.
- **Proposed re-statement (new, post hoc, to be labelled as such):** *"once the chain history is
  cached, a history query costs the same order as a centralized in-memory query (sub-0.25 ms, set by
  serialisation); the chain cost returns whenever freshness must be checked (≈50× with a 2-call probe,
  ≈370× uncached)."*

### 4.4 Threats
1. **Pre-registered.** The centralized registry runs in-process: Python dicts, with no database, no
   network and no caller authentication.
   - Its timings are a *lower bound* on a deployed registry, so every write ratio is an *upper bound*
     on the centralized advantage.
   - A deployed REST + DB call (≈1–10 ms) would bring the write ratio down to roughly 1–15×. The
     ≥10× verdicts are therefore specific to the in-process baseline.
2. **Hardhat automine.** On a public chain a write waits at least one block interval (seconds), which
   makes the write ratios larger.
3. **Unequal work, as shipped.**
   - MOBI birth also encrypts the VIN, hashes the birth certificate and generates a key pair. The
     centralized baseline stores the plain VIN.
   - MOBI events store hashes, not the event body.
4. **"Cached" is a condition, not a provider mechanism.** The validated variant shows what detecting
   change costs.
5. **Baseline defect noticed.** Centralized event IDs are `sha256(vehicle, type, int(time.time()))[:16]`,
   so same-type events on one vehicle within one second collide. Uniqueness is not enforced. Timing
   is unaffected.
6. **Run conditions.** Single host, serial, one run. Development runs are disclosed in §2.

## 5. Threats common to both experiments
- **M1 only.** All chain figures come from localhost Hardhat. Absolute ms do not transfer to a public
  network; the structure (RPCs per operation, refresh fraction, staleness count) does.
- **K-5.** The freshness-k registry is the cv2x `ERC1056Registry`, not `EthereumDIDRegistry`. The
  refresh cost is that of a 1-hop identity.
- **Comparison with #21.** The k = 1 median is 10.95 ms here against #21's 9.654 ms on the same code
  path (plus a counter). PASS2_T §4 showed a run-to-run node spread of 8.98–11.16 ms for this cell.
  Quote k = 1 from #21, and use this run only for the within-run k sweep.
- **Sweep order.** k was swept in a fixed order (1, 5, 25, ∞), each with a fresh verifier. Drift across
  the sweep is not randomised.

## 6. Proposed register rows (session to apply; `MEASUREMENT_CONDITIONS.md` not edited)

**#32 (new): Freshness-k ERC-1056 verify.**
- **Claim:** n = 250 per k, mean (amortised) / median / p95 ms:

  | k | mean | median | p95 | P\*(0.5) |
  |---|---:|---:|---:|---:|
  | 1 | 11.76 | 10.95 | 16.15 | 4 |
  | 5 | 2.38 | 0.46 | 10.48 | 21 |
  | 25 | 0.85 | 0.43 | 0.76 | 58 |
  | ∞ | 0.45 | 0.43 | 0.63 | 110 |

  - The means match t_eff = t_local + t_chain/k within ±7 %, with this run's constants t_local = 0.428
    and t_chain = 10.52 ms. LATENCY_BUDGET §4's 0.4 + 2.5/k under-states t_chain because its refresh
    is one eth_call (6.81 ms here), not a full resolution.
  - The P\*(0.5) = 100 knee is at k ≈ 146 (full refresh) or ≈ 95 (one-call refresh), not k ≈ 25.
- **Staleness after a mid-stream `revokeIdentity`:** at most **0 / 4 / 24** messages accepted for
  k = 1 / 5 / 25 (= k − 1, matching the phase prediction in all 35 trials); ≥ 50 (unbounded) for k = ∞.
- **Condition:** M0 (cached path) / M1 (refresh), Hardhat 2.28.6, chain 31337, automine. T-9 is
  identical across k.
- **Source:** `cv2x-testbed/scripts/experiment_freshness_k.py --deploy`, code `8216507` (git_dirty
  false), results `bcff389`.
- **Status:** **V**, with caveats K-5, M1-only and one sender.
- **Consequence:** `LATENCY_BUDGET.md` §3 row "keys pre-resolved and cached" moves from E to V
  (0.428 ms median, P\*(0.5) = 110 at k = ∞). §4's "k ≈ 25" becomes S and is replaced by the measured
  knee.

**#33 (new): M4 lifecycle parity, centralized registry vs MOBI-VID-V2 (pre-registered, PLAN_MOBI_SUMO §A.2).**
- **Claim:** n = 50, median / p95 ms:

  | Operation | centralized | MOBI | MOBI gas |
  |---|---:|---:|---:|
  | birth | 0.0028 / 0.0076 | 14.13 / 20.77 | 398,298 |
  | lifecycle event | 0.0064 / 0.0109 | 11.86 / 14.88 | 255,267 |
  | ownership transfer | 0.0019 / 0.0033 | 11.51 / 14.84 | 182,144 |
  | history query (10 events, 2 transfers) | 0.240 / 0.286 | 89.9 / 111.3 uncached; 0.017 / 0.019 cached; 12.1 / 16.5 cached + 2-call probe | – |

- **Verdicts:**
  - ≥10× for writes: **PASS** ×3 (≈1,850–5,930×).
  - "Equal once cached": **FAIL** (ratio 0.072; set by serialisation code, see FOLLOWUP_FD §4.3).
- **Condition:** M0 (centralized, in-process) / M1 (MOBI), Hardhat 2.28.6, chain 31337, automine.
  `MOBIVIDRegistryV2` is the cv2x-testbed build (solc 0.8.20/paris, deploy 5,023,352).
- **Source:** `cv2x-testbed/scripts/experiment_lifecycle_parity.py --deploy`, code `8216507`, run tree
  `bcff389` (git_dirty false), results `0a667ec`.
- **Status:** **V**, with the caveats below.
  - The centralized figures are an in-process lower bound, so the write ratios are upper bounds.
  - The cv2x MOBI contract is not the `1_blockchain-identity` one of #25/#30.
  - Development runs are disclosed.

## 7. SC-13 closure note (for `docs/SCOPE_CHANGES.md`)

> **SC-13 — closed 2026-10-04 (stream F-D).** The lifecycle-parity comparison against
> `centralized_vehicle_registry.py` was run as pre-registered (M4, PLAN_MOBI_SUMO §A.2): birth,
> lifecycle event, ownership transfer, history query, n = 50, single full run. Results:
> `cv2x-testbed/results/lifecycle_parity.*`; register row #33.
>
> **Verdicts as measured:**
> - the centralized registry is ≥10× faster for all three writes (PASS);
> - "equal for history queries once cached" FAILS on the pre-fixed [0.5, 2] band. The cached MOBI
>   history is faster than the centralized query, and the gap is a serialisation artefact.
>
> **Chapter 5** reports both verdicts. It states that the centralized baseline is in-process, so the
> write ratios are upper bounds on its advantage, and gives the post-hoc re-statement of the history
> claim, labelled as post hoc.
