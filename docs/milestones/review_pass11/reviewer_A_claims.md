> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`. Dispositions: after-action report 11 §4.

## Findings

No wrong number turned up. Every figure in rows #44–#48 traces to its source JSON. The problems are the I5 definition, a revocation-cost omission behind I1, process breaches of the pre-registration, and overclaiming wording.

**F1 | medium | `docs/AFTER_ACTION_REPORT_10.md` §3 F-A; `docs/MEASUREMENT_CONDITIONS.md:130`; `docs/thesis/chapter5-results/README.md:332` | "The cost of re-checking is visible in I3"; "SPaT costs what a BSM costs"**
- I3 reports counts only. `infrastructure_revocation.json` has no latency field, and `main_i3` records no timings. The statement in F-A is false.
- The re-check is `authority.revocation_registry.is_revoked(id)` (`2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py:148`), an in-memory `dict` lookup. So re-check cost is about zero at every k in this harness.
- Register #40 (`freshness_k.json`) measured k=1 at 2.7 ms against 0.44 ms for k=∞ when the re-check is a chain read. A real registry lookup is therefore the dominant term, and I1 with k=∞ is the cheapest case.
- F-A is defensible for a like-for-like warm path, but its bias is never stated.
- Fix: scope I1 to "warm, no re-check". Add "revocation-lookup cost not modelled (registry is in-process)" to #44, #46, §5.4.1 and C3. Correct the F-A sentence.

**F2 | medium | `docs/design/INFRASTRUCTURE_PREREG.md` §4 ("none"); `AFTER_ACTION_REPORT_10.md` | The pre-registration says any later change is appended as a dated amendment**
- It was not edited: `git log --follow` shows only `cfbdcbc`, and `git diff cfbdcbc 0ba7c6c` on it is empty.
- But three departures are recorded only in the after-action report and the register, never as amendments:
  - F-A (k=∞ for I1; the pre-registration was silent).
  - The I4 operation (the pre-registration named "revocation of the RSU identity").
  - The I5 statistic (see F3).
- Fix: append dated amendments, or state in the pre-registration that deviations are logged in the after-action report.

**F3 | medium | `run_infra_stats.py` (`i5_backhaul_ms`, `i5_tmc_hop_ms`); `INFRASTRUCTURE_PREREG.md` I5; `MEASUREMENT_CONDITIONS.md:134` | Undisclosed deviation from the pre-registered I5 measure, and a loose definition in the register**
- The pre-registration says "per run: median (controller sign + RSU verify + RSU SPaT sign + vehicle warm SPaT verify)". That is the median of the per-message sum.
- The code adds four per-run medians: `ctrl_sign + ctrl_verify_warm + spat_sign + spat_warm`. The statistic is the sum of medians. The reported 0.840 ms is then the median across runs of that sum (I confirmed 0.8396 by recomputation).
- Row #48 says "the sum of per-run medians … 0.840" without saying a median across runs follows.
- What I5 is: a notional serial sum of four independent per-operation median costs. Warm paths only.
- What I5 is not:
  - It is not a path latency. In `infrastructure_step`, the RSU SPaT phase comes from `_signal_phase(sim_time)`. It never consumes the controller's verified update, so there is no causal chain in the simulation.
  - It has no tail (p95/p99).
  - It excludes cold paths.
  - It excludes the 1 s controller-update period and the 0.1 s SPaT period. Those set real staleness at 0.1 to 1.1 s, orders of magnitude above 0.84 ms.
  - It excludes serialization and network.
  - The TMC hop rests on about 12 warm samples per run (4 plans × 3 warm).
- Fix: rename to "sum of four median crypto operation costs". Say it is not an end-to-end latency. Disclose the deviation from the pre-registration.

**F4 | medium | `chapter5-results/README.md:357`; `AFTER_ACTION_REPORT_10.md` N-17 ("2.4 s at k = 25"); `META_COMMENTARY_2026-10-09.md:~84` | "staleness of (k − 1) × 0.1 s"**
- I3 bounds a message count, not time. The cache in `infrastructure_layer.py` (`_cache[receiver][did]`) never expires.
- A vehicle that cached `rsu_1`, drove out of range and returned later still accepts up to k−1 messages. Under the 8-nearest cap a vehicle may also receive fewer than 10 Hz.
- So 2.4 s is a lower bound on the time to receive 24 messages under full reception, not a bound on trust duration.
- Fix: say "message count; 0.1 s per message only if every SPaT is received; no cache expiry modelled".

**F5 | medium | `MEASUREMENT_CONDITIONS.md:132`; `chapter5-results/README.md:~352` | "the bound is reached, not just respected"**
- Accurate as a maximum over 30 runs × all receivers (0/4/24).
- Per-run maxima from the JSON:
  - k=5: bound reached in 16 of 30 runs.
  - k=25: bound reached in only 6 of 30 runs; per-run maxima were {0, 8, 13…24}.
- The bound follows arithmetically from the `seen % k` counter, so the experiment checks the implementation's phase logic, not a security property. The revocation registry is in-process, so propagation delay is zero. The pre-registration also made I3 unable to FAIL unless the code was buggy.
- The register should say it is a conformance check of the counter.
- The "4–14 vehicles in range" figure counts receivers that got at least one `rsu_1` SPaT after revocation. That includes cold first-contact vehicles that were rejected and are not cached-trust cases.

**F6 | medium | `MEASUREMENT_CONDITIONS.md:130`; `chapter5-results/README.md:337-339` | "not comparable with #27 (49.0.0)"; chapter 5 attributes the offset to the `cryptography` library**
- The SSI warm path does not use `cryptography`. `eth-account`'s `Requires` list (via `pip show`) does not include it, and the SSI verify path is eth-account/coincurve.
- The BSM warm value moved from 0.1528 ms (#27) to 0.1637 ms, +7%, on the same SSI code path. The kernel string also differs: `fc-v64` in `v2v_latency_stats.json`, `fc-v80` here. This is a different VM, so the cause is host or VM, not the library.
- Register #27 itself says the PKI cold time halved with cryptography 41→49. That is PKI, not SSI.
- Fix: say "different host/VM and library set; cause not isolated". Do not imply the library is the cause.
- Related: Python env drift (cryptography 49→41) between runs of record is itself unexplained.

**F7 | medium | `chapter5-results/README.md:323`; `META_COMMENTARY_2026-10-09.md:76,80`; `cruxes.yaml` C3 question | Overclaiming wording**
- README line 323 says both result files were produced "with a clean tree". `infrastructure_revocation.json` has `tree_clean: false`. This is disclosed in #46 and F-C but contradicts the chapter.
- Meta commentary line 76: "costs **exactly** what a BSM costs". The CI is [0.995, 1.001] and the median is 0.996. That is roughly equal, warm path only, k=∞, mock mobility.
- Meta commentary line 80: "the same layer secures V2I and I2I is now a measured sentence". What was measured: warm crypto cost, 7 injected attacks, and a counter bound. "Secures" was not measured.
- Replay is not tested. `_bsm_freshness` and the infra layer use `replay_cache=False`, and the module docstring says duplicates inside the window are accepted. "Every infrastructure attack" is the chapter heading for I2 (line 340); the text says "seven injected".
- Meta commentary line 76 says "no new mechanism". The pass added a 168-line `InfrastructureLayer` with a permitted-type check and a revocation counter.
- README line 336: "the check is free at this resolution". The SPaT message is smaller than a BSM, so the ratio of 0.996 confounds payload size with the permitted-type check. The permitted-type check is neither isolated nor shown to be free.
- Fix: soften these to what was measured.

**F8 | low | `sumo_identity_integration.py:807-840` (`run_infrastructure_attacks`) | I2 counts any rejection**
- The harness records `not verify()[0]` and does not check the rejection reason. In-run, an attack could be rejected for the wrong reason (for example `stale` or `error:*`) and still count.
- The reasons are asserted only in the L3 tests, with a different setup.
- Each attack is deterministic and run once per run. "30/30" is 30 repetitions of a deterministic check, not a statistical rate.

**F9 | low | `run_v2v_stats.py:62`; `run_infra_stats.py:main_i1` | One `random.Random(20260719)` is shared across the `agg()` calls**
- Reproducible given the fixed call order. But the CIs for later quantities depend on how many draws earlier calls consumed, so adding or reordering an `agg` changes them.
- The I1 ratio CI is the first call, so it equals a fresh seed. I reproduced [0.99456, 1.000931] exactly with the repo function.
- `agg()` silently drops `None` values, so N could shrink without a flag.

**F10 | low | `MEASUREMENT_CONDITIONS.md:133` | I4 is a single run**
- `infrastructure_gas.json` is one Hardhat execution. Other gas rows rely on 30/30 byte-identical determinism runs.
- Its metadata has `dirty: false` but `dirtyAnyFile: true`.
- The I4 run (03:55:19) overlapped with the I3 run, which started 03:54:55. Counts are unaffected.
- I1 timings were taken while the author was writing the renderer. No host-load record exists. This is mitigated by the within-run ratio.

**F11 | low | `cruxes.yaml` C4 | `evidence_rows` now include #46 (V)**
- C4's claim is about a revoked vehicle key and "latency cost". #46 covers an RSU credential in an in-memory registry and has no latency. It is weak evidence for C4.

## Checked and found sound

- **Rows #44–#48 numbers** all match the JSON:
  - I1: median 0.996037; CI [0.99456, 1.000931], which rounds to [0.995, 1.001].
  - SPaT warm 0.1634, BSM warm 0.16365, SPaT cold 0.45205, SPaT sign 0.2498.
  - 138,895 verified, 0 rejected, 24,000 sent; 30/30 attacks.
  - I3 maxima 0/4/24/100.
  - Mean totals 0 / 6.73 / 40.97 / 496.23.
  - Receivers 4–14.
  - I5: 0.8396 [0.8322, 0.8454]; TMC 0.4327 [0.4128, 0.43975].
  - I4 gas values 0, 52,594, 34,050, 51,754, 35,498, 35,050.
- **I1 recomputation.** The median of per-run ratios is 0.99604. The ratio of medians is 0.99847. The per-run ratio equals `spat_warm/bsm_ssi_warm` per run. Percentile bootstrap is implemented correctly (10,000 resamples, linear-interpolation percentiles). "Median of per-run ratios" matches the pre-registration. Both statistics are far inside the [0.80, 1.20] band, so the verdict is not sensitive to the choice.
- **Pre-registration timing.** `cfbdcbc` (03:42:04) is before the code (47c3314, 03:47:46) and the runs (I1 header 03:48:03). The file was never edited.
- **Producer code.** `git diff 1e690c3 9006d4c` shows no change to `sumo`, `identity`, `2_w3c-ssi-layer` or `1_blockchain-identity` except the added `render_trace.py`, which is not a producer for these results. This supports #46's run-identity disclosure.
- **Conditions match the code.** 30 seeds, 20 s, 50 vehicles, 4 RSUs at x = 625/1875/3125/4375, 10 Hz SPaT to the ≤8 nearest within 300 m, controller every 10 steps, TMC every 50 steps, revocation at t = 10.0 s.
- **I3 accounting.**
  - Revocation is applied at the start of `infrastructure_step`, before that step's SPaT, so the exact-step messages are counted.
  - Cold-path receivers after revocation are rejected and not counted as accepted.
  - The bound ≤ k−1 follows from the `seen % k` logic.
  - I found no undercount path except the time-versus-count issue in F4.
- **No-change gate.** Re-running seed 7 for 10 s with flags off, into scratch, gives sent 5,011, delivered 26,877, verified 26,877, failures 5, safety events 11. This matches AAR 10.
- **Commit ids and counts.** All commits cited in the register, AAR and handback exist. The grand report shows 536, 276 and 92 demos / 1,752 steps. CI shows 8 of 8 green on 94c2b7c, 9006d4c and 577a5ab (via `gh api`). Wall-clock 412 s and 1,690 s match "6 min" and "28 min".
- **Pass-9 register rows.**
  - #6: 10.3×, 6.9× and 10.4× recomputed correctly.
  - #25: 52,216, 1,757,881, 33.7× and 1,680,816 match `gas_benchmark.json`.
  - #26: the five lifetime totals match `scaling_lifetime.json`; 0.164 ms/neighbour and P* 609.2 match the density CSV.
  - #27: 0.1528, 1,650,318 and 150 match.
  - #35: the margin ratios 1.10, 1.43, 2.1, 2.4, 2.6, 3.0 and 5.1 are correct.
- **Register #34, #36, #40, #41 and the status changes.** Not recomputed against raw files. They are annotation or status edits and were read for internal consistency only.
- **Crux register.** Eight cruxes, all partial, none a gap; C3 evidence rows #44–#48 are all V.

## Not checked

- Whether the numbers in #34 and #36 (metrics-harness run 2026-10-09T02-09-36Z) match `results/metrics/latest`. Out of scope for the infrastructure rows and not recomputed.
- The dashboard "version 4" and the republish claim (external artifact).
- The "stamp inventory 19/28" and the "290 KB gzipped, 5,011 tx" trace claims in AAR 10 (renderer and trace scope).
- The 16 L3 tests were read but not re-run; the grand report asserts 276 passed.
- Whether the I1 timing runs shared the host with other load. No record exists.
