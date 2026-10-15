# Follow-up stream H-K: freshness-k, full vs probe refresh, same host back to back

**Date:** 2026-10-15 · **Author:** Nikhil Prakash
**Input:** `docs/AFTER_ACTION_REPORT_06.md` (stream H-K); `docs/review02/FOLLOWUP_FD.md` §3 (register #32);
`docs/review02/FOLLOWUP_GK.md` §3 (register #37); `docs/LATENCY_BUDGET.md` §4 and its two notes.
**Base:** `ffb71b0`. Local commits, not pushed. The shared docs (register, README, handoffs, index,
after-action reports, LATENCY_BUDGET) are not edited here. §7 holds the proposed register row and the §4 text.

## 1. Commits

| Commit | Scope |
|---|---|
| `331d55c` | Code: `cv2x-testbed/scripts/summarize_freshness_k_samehost.py` (reads the per-replicate files, measures nothing); `cv2x-testbed/tests/test_freshness_k_samehost.py` |
| `0cf6c3a` `7a836dd` `364ad1e` `0a1b7b7` | Results r1–r4 (full, probe, probe, full) |
| `a7baac0` | Code: summarizer reports foreign CPU per replicate |
| `b151082` `3100e2a` `e3284ee` `7f41781` `9ede056` `b3d3f65` `676db30` `a81faae` | Results r5–r12 (probe, full, full, probe, probe, full, full, probe) |
| `04ecea6` | Code: summarizer separates clean replicates (foreign-CPU rule, exclusion list); tests 9 in total |
| `ba86973` | Results: `cv2x-testbed/results/freshness_k_samehost.{json,csv,md,png}`, plus the as-run driver in `results/freshness_k_samehost/driver/` |
| (this file) | report |

- **The measuring code is unchanged.** `experiment_freshness_k.py` and `ERC1056Provider` are exactly as #37 ran them
  (`f660402`). No flag was needed: each replicate writes its own `--out-name r<i>_<mode>` into
  `results/freshness_k_samehost/`.
- **#32's and #37's files are untouched.** The summarizer only reads them, for the comparison table.
- **Clean tree.** Each result file was written from a clean committed tree (`git_dirty: false` in all 12). The
  results of each replicate were committed before the next one started.
- **Tests:**
  - `tests/test_freshness_k_samehost.py`: 9 offline tests. They cover the knee arithmetic (#32's 146 and
    LATENCY_BUDGET's 25 are reproduced), "not reached", pooling, the staleness check, the clean rule, a mode-name
    mismatch and the writers.
  - Together with `test_freshness_k.py` and `test_freshness_k_probe.py`: 37 passed, 18 skipped. The skipped tests are
    the on-chain ones, and no test node was running.
- **Check against earlier results.** Run on #37's files, the summarizer reproduces #37's t_local, t_chain and P\*.

## 2. Method

- **Same protocol as #32/#37:**
  - `experiment_freshness_k.py --deploy --rotation --refresh-mode {full,probe} --n 250 --warmup 3 --ks 1,5,25,inf`;
  - a fresh verifier per k and one sender;
  - revocation staleness for every phase m_pre ∈ 1..k, then a key rotation mid-stream (Part 3).
- **Fresh node per replicate.** Each replicate started its own `hardhat node --port 8562` from
  `/home/user/CVIN-SC-Implementation-SSI-DID/1_blockchain-identity`. It was checked at block 0, and it was killed by PID
  (process group) when the replicate ended. The script deploys the registry on that node. All four parts of the
  replicate (latency, staleness, rotation, probe and isRevoked references) run on that node.
- **Interleaved order.** The 12 replicates ran in ABBA blocks, 6 per mode:

  F P P F | P F F P | P F F P

  Total time 05:05–05:29 UTC.
- **Planned and actual replicate counts.**
  - The plan was 2 replicates per mode (ABBA).
  - Replicates r1–r4 ran with other sessions busy, so more were added under the load rule (§4).
  - The final count is 6 + 6.
- **Constants:** the definitions are unchanged.
  - t_local = median verify at k = ∞;
  - t_chain = median at k = 1 − t_local;
  - P\*(0.5) = ⌊50 ms / mean⌋ per k.
- **Knee.** The knee is t_chain / (0.5 − t_local). It is "not reached" when t_local ≥ 0.5 ms, and the ceiling
  P\*(0.5) at k = ∞ is then quoted. The smallest tested k with measured P\*(0.5) ≥ 100 is also reported.
- **Pooled figures.** These concatenate the samples of the replicates of a mode, n = 250 × replicates per k.
- **Load recording.** The driver records `/proc/loadavg` at the start and end of every replicate. From r2 onwards it
  also takes a 2 s sampler with three readings:
  - loadavg;
  - **foreign CPU**: all busy jiffies minus those of this replicate's node and experiment;
  - steal, from r11 onwards.

  From r5 onwards a gate waited for under 0.7 busy CPUs over 5 s before the node was started.

## 3. Environment

| Item | Value |
|---|---|
| CPU | Intel Xeon Processor @ 2.80 GHz, 4 vCPU, Linux 6.18.44 (the same class as #37's host; #32 ran on 2.10 GHz) |
| Python / web3 / cryptography / numpy / matplotlib | 3.11.15 / 8.0.0 / 49.0.0 / 2.4.6 / 3.11.2 |
| Node / Hardhat | v22.22.0 / HardhatNetwork 2.28.6 (EDR 0.3.8), chain 31337, automine |
| Contracts | the tracked cv2x `ERC1056Registry` artifact. `scripts/check_artifacts_fresh.js` exit 0 before the runs. Deploy 927,756 gas; **bytecode sha256 `8ca9cfe5d607106f9b0ce09920b8d11db6aeccf66d57344ee209ec7cc9bc5812`** (= #32 = #37), identical in all 12 replicates. Stream H-A's MOBI changes do not touch this contract |
| T-9 policy | 1.0 s past / 0.1 s future, replay cache 65,536 (unchanged) |
| Measured code | `experiment_freshness_k.py` / `ERC1056Provider` as at `f660402` (unchanged since #37) |

## 4. Host load and contamination

**What load1 includes.** load1 counts this replicate's own node + Python, which keep about 1.0 CPU busy (`own_cpu`
0.92–1.01). On its own it therefore overstates load from other sessions. **Foreign CPU** is the cleaner measure, so the
*clean* rule is: foreign-CPU mean ≤ 0.5, and the replicate is not on the exclusion list.

| rep | mode | UTC | load1 start / end / max | foreign CPU mean / max | clean? |
|---:|---|---|---|---|---|
| 1 | full | 05:05:16–05:05:42 | 1.30 / 1.68 / 1.68 | not sampled (another session's pytest seen) | no |
| 2 | probe | 05:09:02–05:09:23 | 1.04 / 1.54 / 1.54 | 1.00 / 2.21 | no |
| 3 | probe | 05:10:40–05:10:58 | 0.99 / 1.76 / 1.76 | 1.56 / 2.13 | no |
| 4 | full | 05:21:13–05:21:40 | 1.22 / 2.00 / 1.99 | 1.86 / 2.17 | **no**: overlaps the session lead's M4 run (Hardhat :8559, ≈05:17–05:21:35 UTC) |
| 5 | probe | 05:22:57–05:23:20 | 1.22 / 1.29 / 1.35 | 0.27 / 0.45 | yes |
| 6 | full | 05:23:50–05:24:17 | 1.00 / 1.41 / 1.45 | 0.71 / 1.35 | no |
| 7 | full | 05:24:38–05:25:04 | 1.09 / 1.47 / 1.52 | 0.21 / 0.72 | yes (load1 1.52 is its own) |
| 8 | probe | 05:25:26–05:25:47 | 1.12 / 1.16 / 1.18 | 0.14 / 0.17 | yes |
| 9 | probe | 05:26:06–05:26:28 | 0.83 / 0.87 / 0.93 | 0.15 / 0.22 | yes |
| 10 | full | 05:26:45–05:27:12 | 0.68 / 0.75 / 0.75 | 0.15 / 0.24 | yes |
| 11 | full | 05:27:58–05:28:26 | 0.43 / 0.66 / 0.66 | 0.15 / 0.21 (steal 0.055) | yes |
| 12 | probe | 05:28:47–05:29:10 | 0.55 / 0.62 / 0.62 | 0.13 / 0.20 (steal 0.036) | yes |

- **Load rule.** Under the >1.5 rule, r1–r4 and r7 exceeded it, and extra replicates were added. 5 of the 12 are
  not clean.
- **Clean set.** It holds **3 full (r7, r10, r11) and 4 probe (r5, r8, r9, r12)**, all from the second half of the
  sequence.
- **r4.** It ran fully inside the lead's notified M4 window, so it is excluded by name, as well as by its foreign CPU.
- **Headline.** The headline figures are the clean pools. The all-replicate pools are reported too; they differ by at
  most 3 in P\*.

## 5. Results (ms, Hardhat local, M1)

### 5.1 Per mode, clean pooled (full: r7+r10+r11; probe: r5+r8+r9+r12)

| k | full mean / median / p95 | **full P\*(0.5)** | probe mean / median / p95 | **probe P\*(0.5)** | probe / full |
|---|---|---:|---|---:|---:|
| 1 | 20.38 / 19.50 / 28.19 | **2** | 7.32 / 6.47 / 10.68 | **6** | 3.0× |
| 5 | 4.73 / 0.87 / 22.91 | **10** | 1.94 / 0.68 / 6.81 | **25** | 2.5× |
| 25 | 1.46 / 0.64 / 1.32 | **34** | 0.91 / 0.62 / 1.39 | **54** | 1.6× |
| ∞ | 0.83 / 0.70 / 1.27 | **60** | 0.71 / 0.63 / 1.19 | **70** | 1.2× |
| **t_local** | **0.699** | | **0.629** | | |
| **t_chain** | **18.80** (4 RPCs) | | **5.85** (1 RPC) | | full / probe 3.2× |

- **Per-replicate ranges (clean):**

  | | full | probe |
  |---|---|---|
  | t_local | 0.612–0.963 | 0.607–0.667 |
  | t_chain | 17.9–19.9 | 5.40–6.84 |
  | P\*(0.5) k = 1 | 2 | 6–7 |
  | P\*(0.5) k = 5 | 9–11 | 24–28 |
  | P\*(0.5) k = 25 | 30–38 | 47–60 |
  | P\*(0.5) k = ∞ | 53–70 | 63–75 |

- **All 12 replicates pooled:** full t_local 0.676, t_chain 17.92, P\* 2 / 10 / 33 / 63; probe t_local 0.635,
  t_chain 5.49, P\* 7 / 25 / 52 / 69.
- **Refresh accounting.** Every window held n/k refreshes. Probe mode needed 0 full resolutions in all 6 probe
  replicates.
- **Direct references, per replicate:**
  - the probe call alone: 3.3–4.9 ms median;
  - `isRevoked` through web3: 10.2–14.9 ms.
- **Fit.** The means lie +0.5 % to +8 % above t_local + t_chain/k at k = 5 and 25 in both modes.

### 5.2 Knee (P\*(0.5) = 100), with t_local

| mode | knee, clean pooled | per replicate | measured: smallest tested k with P\*(0.5) ≥ 100 | ceiling at k = ∞ |
|---|---|---|---|---:|
| full | **not reached** (t_local 0.699 ms ≥ 0.5) | not reached in all 6 (t_local 0.612–0.963) | none | 60 (53–75) |
| probe | **not reached** (t_local 0.629 ms ≥ 0.5) | not reached in all 6 (t_local 0.607–0.667) | none | 70 (63–75) |

**Sensitivity only (it mixes hosts).** At #32's t_local of 0.428 ms, these t_chain values would give a knee of
≈261 (full) and ≈81 (probe).

### 5.3 Staleness bound

- **Revocation and rotation, every replicate and both modes:** max 0 / 4 / 24 for k = 1 / 5 / 25, which is k − 1. At
  k = ∞ the value is ≥ 50 (the cap).
- **Trials.** All 840 finite-k trials equal the phase prediction: 12 replicates × (35 revocation + 35 rotation).
- After each refresh the revoked identity stays rejected and the old key is rejected.

## 6. Comparison with #32 and #37

Recomputed by the summarizer from their files, with the same definitions:

| run | host | mode | t_local | t_chain | P\*(0.5) k = 1 / 5 / 25 / ∞ | knee |
|---|---|---|---:|---:|---|---|
| #32 | 2.10 GHz | full | 0.428 | 10.52 | 4 / 21 / 58 / 110 | k ≈ 146 |
| #37 r1 / r2 | 2.80 GHz shared | full | 0.529 / 0.516 | 14.38 / 10.28 | 3 / 13 / 40 / 77; 4 / 18 / 50 / 80 | not reached |
| #37 r1 / r2 | 2.80 GHz shared | probe | 0.540 / 0.490 | 2.76 / 2.89 | 13 / 40 / 71 / 78; 12 / 31 / 63 / 87 | not reached / ≈279 |
| **#40 clean** | 2.80 GHz shared, same host back to back | full | **0.699** | **18.80** | **2 / 10 / 34 / 60** | **not reached** |
| **#40 clean** | same | probe | **0.629** | **5.85** | **6 / 25 / 54 / 70** | **not reached** |

**What holds (#37 confirmed on one host, interleaved):**
- **No finite k reaches P\*(0.5) = 100 in either mode.** t_local is above 0.5 ms in every one of the 12 replicates.
- **The probe refresh is strictly better at every finite k:** 3.0× at k = 1, 2.5× at k = 5 and 1.6× at k = 25.
- **The staleness bound is k − 1 in both modes.**
- **t_chain, full / probe = 3.2×**, just below #37's 3.6–5.2× band. The two modes now share host time, so this is
  the better-controlled figure.

**What does not hold:**
- **Absolute ms do not transfer across sessions on the "same" host class.** In this session every chain-touching
  figure is ≈1.3–2× #37's:
  - t_chain_probe 5.85 vs 2.8 ms;
  - the probe call alone 3.3–4.9 vs 2.3–2.8 ms;
  - `isRevoked` 10–15 vs 7 ms.
- **t_local rose from ≈0.5 to ≈0.63–0.70 ms**, even in replicates with ≤ 0.15 foreign CPU and ≤ 0.06 steal. This
  shifts every P\* down; the k = ∞ ceiling is 60–70 here, against 77–87 in #37 and 110 in #32.
- **#37's "k = 1 probe ≈ 3.5× full" becomes 3.0×** here. #37's probe P\* values (12–13 at k = 1) are not reproduced:
  this session gives 6–7.
- **Conclusion: the knee remains host-and-session dependent.** Only within-session ratios and the staleness bound
  are stable.

**Threats:**
1. **The full mode's t_local is 0.07 ms above the probe mode's.** The cached path is the same code in both modes,
   and r11 (0.963) inflates the full pool. Read this as noise, not a mode effect.
2. **Clean set.** It is 3 vs 4 replicates, all in the second half of the sequence. Their order, P F P P F F P, still interleaves the two modes.
3. **Foreign CPU** counts steal and any short-lived process as foreign, and r1 has no sampler data.
4. **M1 only, K-5 (cv2x registry), one sender, unchanged identity in the sweep.** These are as in #37.

## 7. Proposed register row and LATENCY_BUDGET §4 text (session to apply)

**#40 (new): Freshness-k, full vs probe refresh, same host back to back (stream H-K).**
- **Claim:** 12 interleaved replicates (ABBA, 6 per mode), each on a fresh Hardhat node, n = 250 per k. Headline =
  clean pool (foreign CPU ≤ 0.5): full r7, r10, r11; probe r5, r8, r9, r12.
  - **full:** t_local **0.699**, t_chain **18.80 ms** (4 RPCs).
  - **probe:** t_local **0.629**, t_chain **5.85 ms** (1 RPC). Full / probe = 3.2×.
  - P\*(0.5) by k, full vs probe:

    | k | full | probe |
    |---|---:|---:|
    | 1 | 2 | 6 |
    | 5 | 10 | 25 |
    | 25 | 34 | 54 |
    | ∞ | 60 | 70 |

  - **P\*(0.5) = 100 is not reached at any k in either mode, in any of the 12 replicates** (t_local 0.61–0.96 ms).
  - Staleness = k − 1 for revocation and rotation in 840/840 finite-k trials.
- **Condition:**
  - M0/M1; Hardhat 2.28.6, chain 31337, automine; one 2.80 GHz Xeon session, shared;
  - load is recorded per replicate. r1–r4 and r6 are not clean; r4 overlaps the session lead's M4 run.
- **Source:**
  - `cv2x-testbed/scripts/experiment_freshness_k.py --deploy --rotation --refresh-mode {full,probe}`, code
    `f660402` (unchanged);
  - per-replicate files `cv2x-testbed/results/freshness_k_samehost/r<i>_<mode>.*`; summary
    `results/freshness_k_samehost.{json,csv,md,png}` via `scripts/summarize_freshness_k_samehost.py`
    (`04ecea6`). Results `0cf6c3a`…`a81faae` and `ba86973`;
  - registry sha256 `8ca9cfe5…5812`.
- **Status:** **V** for:
  - the within-session mode comparison (ratios);
  - "no knee on this host class";
  - the staleness bound.

  Absolute ms are **session-dependent** (≈1.3–2× #37 on the same CPU model).
- **Consequence:**
  - supersedes #37's cross-replicate mode comparison;
  - LATENCY_BUDGET §4's #37 note is replaced by the text below.

**LATENCY_BUDGET §4: replace the "Update (register #37)" paragraph with:**

> **Update (registers #37, #40).** A one-call probe refresh cuts t_chain by ≈3× (one RPC instead of four) and keeps
> the k − 1 staleness bound. A same-host, back-to-back comparison of both modes (#40: 12 interleaved replicates, each
> on a fresh node) gives:
>
> - **P\*(0.5), probe vs full:** 6 vs 2 at k = 1, 25 vs 10 at k = 5, 54 vs 34 at k = 25, 70 vs 60 at k = ∞;
> - **no k reaches P\*(0.5) = 100 in either mode**, because t_local is 0.63 ms (probe) / 0.70 ms (full), above the
>   0.5 ms that P\*(0.5) = 100 requires.
>
> The knee therefore exists only where t_local < 0.5 ms (#32's 2.10 GHz host: k ≈ 146, full refresh). It must
> always be quoted with its t_local, and absolute values differ between sessions on the same host class.
