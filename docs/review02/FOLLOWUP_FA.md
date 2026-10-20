# Follow-up F-A: re-running register rows #26 (Exp. C/D) and #27

**Stream:** F-A of `docs/AFTER_ACTION_REPORT_04.md` (input: `docs/HANDBACK_2026-10-04.md` §4,
"Next session" item 1).
**Date:** 2026-10-04. **Base:** `d2e6a58`.
**Scope:** register #27 (V2V latency, N=30 seeded runs) and #26 Exp. C/D (verify latency vs claim
count; V2V saturation vs neighbour density). Exp. A/B were regenerated in review 02 and are not
touched. The table generator rewrote their outputs byte-identically, so they do not appear in any
commit here.
**Mobility:** simulated (`--simulate`; no SUMO binary). The identity cryptography is real. This
follows the existing convention: *simulated mobility, real identity crypto*.

## 1. Commits

| Commit | Content |
|---|---|
| `58a6513` | Code: environment header (date, commit, clean-tree flag, CPU, Python, library versions) in `run_v2v_stats.py`, `run_verify_scaling.py` and `run_verify_richness.py`; stale caveat fixed (see §2) |
| `d78e344` | #27 results: `cv2x-testbed/sumo/results/v2v_latency_stats.json` (+ last-seed `v2v_latency.json`) |
| `fd25d05` | #26 Exp. C run of record: `4_comparison-framework/results/scaling_verify.json` (+ repeats 1–5) |
| `38909df` | #26 Exp. D run of record: `v2v_density` block of the same file |
| `d12f868` | C/D tables and figures regenerated; Exp. D repeats 1–5 |
| `f1c2399` | Exp. C confirmation block declared **before** it ran (§5.2) |
| `05803c3` | Exp. C confirmation repeats R6–R10 + summary; same-host A/B baseline data (`docs/review02/followup_fa_data/`) |

Every run of record and every confirmation repeat ran on a clean tree. Each JSON records
`tree_clean: true` and the commit it ran on (`58a6513`, `d78e344`, `fd25d05`, `f1c2399`).
Nothing is pushed.

## 2. Script changes (minimal)

The scripts were not broken: they ran unchanged. Two problems were fixed:

1. **Stale caveat.** `run_v2v_stats.py` wrote into its output that the failures are "exclusively the
   3 injected attacks per run". Since T-9 (`8518809`), `sumo_identity_integration.py` injects
   **5** attacks: tampered PKI, tampered SSI, stale PKI, stale SSI and an uncredentialed SSI
   sender. The total is 150 = 5 × 30, all rejected. The caveat text now says so.
2. **Environment header.** `MEASUREMENT_CONDITIONS.md` §1 requires an environment header for
   latency figures, and none of the three drivers recorded one. Each now writes an `environment`
   block (`environment_richness` for Exp. C) to its JSON.

No measurement logic, seed or pre-registered parameter changed.

## 3. Environment and commands

| | Value |
|---|---|
| CPU | Intel(R) Xeon(R) Processor @ 2.10GHz, 4 logical CPUs (shared cloud VM) |
| OS | Linux 6.18.44-fc-v64, glibc 2.39 |
| Python | 3.11.15 |
| Libraries | coincurve 21.0.0 · eth-account 0.14.0 · eth-keys 0.8.0 · cryptography 49.0.0 · numpy 2.4.6 · web3 8.0.0 · matplotlib 3.11.2 |
| Load | 1-min load 0.4–1.9. Other agent sessions shared the host: a Hardhat node on :8554 and a pytest run were seen during #27. Runs were serial, with no CPU pinning. |
| July run of record | kernel 6.18.5-fc-v15, Python 3.11.15. Library versions were not recorded. Review 02 found cryptography 41.0.7 in the 2026-09 runs (`PASS1_T.md` §4). |

Commands (from the repo root):

```
python3 cv2x-testbed/sumo/run_v2v_stats.py --runs 30 --duration 20 --vehicles 50     # #27
python3 4_comparison-framework/performance-metrics/run_verify_richness.py           # Exp C (300 runs/pt, 50 warm-up)
python3 cv2x-testbed/sumo/run_verify_scaling.py                                      # Exp D (300 intervals/P, 50 warm-up)
python3 4_comparison-framework/performance-metrics/generate_scaling_tables.py       # C/D tables
```

`--duration 20` matches the July run of record (`sim_duration_s_per_run: 20`). The script default
is 30, and the July commit message records 20. The message, verify and attack totals match July
exactly: 300,591 sent and 1,650,318 verified, so the mobility workload is identical.

**Same-host A/B.** The host and libraries changed since July. To separate code effects from
environment effects, the pre-review-02 merged trunk `781dc0b` was exported with `git archive` and
the same three drivers were run from it on this host, right after the new runs. Data:
`docs/review02/followup_fa_data/ab_781dc0b_*.json`.

## 4. #27 V2V latency: old → new

N=30 seeded runs (seeds 1–30). Each run is one subprocess. The statistic is the median of the 30
per-run medians, with a 95 % percentile-bootstrap CI (10,000 resamples, seed 20260719). p95 is the
95th percentile **of the 30 run medians**, not a pooled per-message p95. Times in ms.

**Deviation from §1, noted.** `sumo_identity_integration.py` does not discard 3 warm-ups per run.
Instead it separates each sender's first contact (counted as *cold*) from cached-peer messages
(*warm*). Each run has tens of thousands of warm samples, so discarding three would not move a
median. The rule's N ≥ 30 is met by the 30 independent runs.

| Metric | July (`9269d96`) median [CI] · p95 | A/B: `781dc0b` on this host | **New (`58a6513`)** median [CI] · p95 | New vs July | Code effect (new vs A/B) |
|---|---|---|---|---|---|
| SSI warm verify | 0.1649 [0.1625, 0.1684] · 0.1748 | 0.1492 [0.1481, 0.1514] | **0.1528 [0.1513, 0.1538] · 0.1578** | −7.3 % | +2.4 % |
| SSI cold verify | 0.4005 [0.3924, 0.4049] · 0.4393 | 0.3661 [0.3536, 0.3792] | **0.3991 [0.3809, 0.4107] · 0.4419** | −0.3 % | +9.0 % |
| SSI sign | 0.2410 [0.2380, 0.2433] · 0.2528 | 0.2195 | **0.2241 [0.2214, 0.2271] · 0.2307** | −7.0 % | +2.1 % |
| PKI warm verify | 0.1022 [0.1014, 0.1036] · 0.1076 | 0.0906 [0.0899, 0.0912] | **0.0939 [0.0930, 0.0945] · 0.0965** | −8.1 % | +3.6 % |
| PKI cold verify | 0.4498 [0.4471, 0.4593] · 0.4755 | 0.2156 [0.2085, 0.2192] | **0.2203 [0.2182, 0.2230] · 0.2488** | −51 % | +2.2 % |
| PKI sign | 0.0834 [0.0818, 0.0853] · 0.0911 | 0.0696 | **0.0776 [0.0754, 0.0783] · 0.0824** | −7.0 % | +11.6 % |
| Failures | 90 (3 × 30) | 90 | **150 (5 × 30)**, all injected | | +2 stale-BSM probes (T-9) |

How to read the table:
- **The review-02 code made every path slightly slower, as predicted.** Measured on the same host,
  the code effect is +2–4 % on the warm paths and +9 % on SSI cold, which is the path that runs the
  credential checks. PKI sign is +12 % because the signed bytes now include the timestamp.
- **The absolute figures fell anyway, because the environment changed.** PKI cold verify halved.
  That matches review 02's finding that cryptography 41.0.7 → 49.0.0 sped up X.509 object access
  2–4× (`PASS1_T.md` §4). The −7 % on the secp256k1 paths is a host/kernel and library difference
  that this pass cannot attribute further. Under `MEASUREMENT_CONDITIONS.md` §5.E, these are
  toolchain effects, not code effects.
- **Was the prediction met?** The handback expected the verifier changes to add "≈+6 %" (HANDBACK
  §4, PASS1_S §7: `verify_credential` +0.013 ms):
  - SSI cold verify, the path that runs `verify_credential`-style checks: same-host code effect
    **+9.0 %**, the same order as predicted.
  - SSI warm verify, which per PASS2_T should change by "a few hundred ns": **+3.6 µs (+2.4 %)**.
    Small, but about 10× the stated estimate.
  - The CIs of the A/B and the new run only just touch (0.1514 vs 0.1513). The effect is resolved,
    but only barely.
- **H3 margin:** 100 ms / 0.1528 ms ≈ **654×** (was ≈600×). SSI/PKI warm ratio: 1.63× (was 1.61×).

## 5. #26 Exp. C: verify latency vs claim count

### 5.1 Run of record (repeat 1, `fd25d05`, clean tree at `d78e344`)

| N | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| July median (p95) | 0.1637 (0.209) | 0.1644 (0.213) | 0.1601 (0.198) | 0.1621 (0.205) | 0.1666 (0.216) | 0.1717 (0.209) |
| New median (p95) | 0.1898 (0.244) | 0.1867 (0.247) | 0.1860 (0.249) | 0.1895 (0.269) | **0.2341 (0.503)** | **0.3011 (0.538)** |

Selective disclosure (N=16, k = 1/2/4/8/16):
- July: 0.1745 / 0.1782 / 0.1869 / 0.1979 / 0.2217.
- New: **0.3622** / 0.2182 / 0.2181 / 0.2321 / 0.2463.

The script's own `scaling_verdict()` labels the run of record "O(N)" for richness (spread 1.62,
R² 0.96). It labels selective disclosure "sub-linear" (k=1 outlier). The regenerated
`scaling_verify_richness.{csv,tex,png}` therefore print **"O(N)"**.

Repeats 2–5 ran back to back. I decided to run them after seeing repeat 1, so they are not
pre-declared. They do not reproduce the N=16/32 rise or the k=1 outlier. Single-run medians on this
shared host vary by up to 0.06 ms per point.

### 5.2 Confirmation block R6–R10 (declared in `f1c2399` before running)

Five fresh repeats ran on a clean tree at `f1c2399` with the pre-registered parameters. The
statistic is the median of the five repeat medians per point, and the order is judged by the
script's own `scaling_verdict()`. Summary file:
`4_comparison-framework/results/scaling_verify_repeats/C_confirmation_R6-R10_summary.json`.

| N | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| Median of 5 (ms) | 0.1775 | 0.1714 | 0.1771 | 0.1863 | 0.1887 | 0.1951 |
| A/B `781dc0b`, median of 3 | 0.1712 | 0.1657 | 0.1766 | 0.1694 | 0.1720 | 0.1766 |

| Quantity | July | New, confirmation block |
|---|---|---|
| Richness fit | 0.1616 + 0.000298·N, R² 0.76, spread 1.07 → O(1) | 0.1756 + 0.000673·N, R² 0.82, spread 1.14, relative slope 0.0038 → **O(1)** |
| Selective disclosure | 0.1726 + 0.00310·k, R² 0.996 → O(k) | medians 0.1963 / 0.2057 / 0.2091 / 0.2283 / 0.2589; 0.1945 + 0.00405·k, R² 0.992 → **O(k)** |
| Max p95, any point, any repeat | 0.328 ms | 0.516 ms (≪ 10 ms) |

The **code effect** is new vs A/B, same host: about +4 % for N ≤ 4 and about +10 % for N ≥ 8, so
roughly **+6 % on average**. That is the predicted figure. It looks mildly N-dependent, which is
plausible because the new proof-metadata and temporal checks touch the payload. Even so, it stays
inside the O(1) criterion.

**Pre-registered predictions** (`SCALING_EXPERIMENTS.md` Exp. C):
- "Fit latency(N); report the scaling order and whether it stays ≪ the 10 ms target": **held**.
  The order is O(1) in N (confirmation block), and p95 ≤ 0.54 ms everywhere, about 18× under the
  target.
- Selective disclosure is linear in k (one salted-hash recompute per disclosed claim): **held**.

## 6. #26 Exp. D: V2V saturation vs neighbour density

Run of record `38909df` (clean tree at `fd25d05`): 300 timed 100 ms intervals per P after 50
warm-ups, with pre-cached peers (warm path: secp256k1 recovery + cached-address compare + T-9
timestamp check).

| P | 5 | 10 | 20 | 40 | 80 |
|---|---|---|---|---|---|
| July median (p95), ms | 0.637 (0.890) | 1.271 (1.438) | 2.539 (2.799) | 5.070 (5.375) | 10.363 (12.335) |
| New median (p95), ms | 0.817 (0.949) | 1.609 (1.940) | 3.187 (4.080) | 6.399 (8.888) | **13.134 (17.632)** = 13.1 % of budget |

| Quantity | July (`d7c611c`) | **New, run of record** | New, repeats 1–5 (median; range) | A/B `781dc0b`, 3 runs (median; range) |
|---|---|---|---|---|
| Slope, ms/neighbour | 0.1296 | **0.1643** | 0.1643; 0.1593–0.1706 | 0.1618; 0.1539–0.1643 |
| Intercept, ms | −0.042 | −0.063 | | |
| R² | 0.9999 | **0.9998** | 0.9993–0.9998 | 0.9971–0.9996 |
| Per-message median, ms | 0.121–0.131 | 0.152–0.156 | | 0.151–0.154 |
| Saturation within P ≤ 80 | none | **none** | none | none |
| Extrapolated P\* (100 ms budget, f = 1) | ≈772 | **≈609** | 609; 586–627 | 618; 610–648 |

- **P\* is still an extrapolation.** It comes from a linear fit beyond the tested range. The largest
  tested P is 80, which used 13 % of the budget. P\* ≈ 609 is about 7.6× beyond the tested range.
  The linearity (R² ≥ 0.999) makes the extrapolation reasonable, but it remains an extrapolation.
- **The move from 772 to 609 is environmental, not code.** On the same host, the pre-review-02 code
  gives a slope of 0.162 ms/neighbour and P\* ≈ 618; the new code gives 0.164 and 609. The +1.5 %
  difference is inside the run-to-run range. The per-message warm cost on this host is about
  0.153 ms, not July's ≈0.12 ms.
- **The figure now agrees with #27.** Exp. D's per-message median (0.153–0.156 ms) matches the new
  SUMO SSI warm median (0.153 ms). In July they differed: 0.12 vs 0.165.
- **Budget fractions.** `LATENCY_BUDGET.md` uses the budget fraction f. With the new slope,
  P\*(0.25) ≈ 152, P\*(0.5) ≈ 305, P\*(1.0) ≈ 609. All three exceed the ~100-neighbour
  dense-traffic bar.
- **Pre-registered prediction** (Exp. D: "the density P\* at which per-interval verification exceeds
  the 100 ms budget, if within range"): **not within range.** As in July, there is no saturation
  for P ≤ 80, and P\* is reported as an extrapolation. The qualitative verdict "P\* ≫ realistic
  density" **holds**.

## 7. Old → new for every cited number

| Cited figure | Register row | Old | New | Status |
|---|---|---|---|---|
| V2V SSI warm verify | #27, #17 | 0.165 ms [0.162, 0.168], N=30 | **0.153 ms [0.151, 0.154]**, p95 0.158, N=30 | moved (environment; code +2.4 %) |
| V2V SSI cold verify | #27 context, ch. 5 | 0.400 [0.392, 0.405] | **0.399 [0.381, 0.411]** | unchanged within CI |
| V2V PKI warm verify | #27 context | 0.102 [0.101, 0.104] | **0.094 [0.093, 0.095]** | moved (environment) |
| V2V PKI cold verify | ch. 5 table | 0.450 [0.447, 0.459] | **0.220 [0.218, 0.223]** | moved (cryptography 49) |
| Attack failures | ch. 5, INVENTORY | 90 = 3 × 30 | **150 = 5 × 30** | T-9 added two probes |
| Exp. C verify vs N | #26 | ≈0.16 ms flat, O(1), slope 0.0003 ms/claim | **≈0.17–0.20 ms, O(1)** (confirmation block; slope 0.0007 ms/claim) | order held; level +8–14 % vs July |
| Exp. C selective disclosure | #26 | O(k), 0.0031 ms/claim | **O(k), 0.0041 ms/claim** | order held |
| Saturation P\* | #26, #17 | ≈772 | **≈609** (repeats 586–627); extrapolated beyond P ≤ 80 | moved (environment) |
| Slope | #26, LATENCY_BUDGET §5 | 0.130 ms/neighbour | **0.164 ms/neighbour** (0.159–0.171) | moved (environment) |
| R² | #26 | 0.9999 | **0.9998** (0.9992–0.9998) | unchanged |
| P = 80 load | ch. 5 §5.9 | 10.4 ms (10 %) | **13.1 ms (13 %)** | moved |

## 8. Proposed register text (for the owning session to apply; this pass edits no register file)

**#27**
> V2V SSI verify warm **0.153 ms [0.151, 0.154]** (median of 30 seeded-run medians, 95 % bootstrap
> CI; p95 of run medians 0.158), cold 0.399 [0.381, 0.411]; PKI warm 0.094 [0.093, 0.095], cold
> 0.220 [0.218, 0.223]. 1,650,318 verifies; 150 failures = the 5 injected attacks × 30, all rejected.
> M0, *simulated mobility (`--simulate`), real identity crypto*; Xeon 2.10 GHz × 4, Python 3.11.15,
> cryptography 49.0.0, coincurve 21.0.0; commit `58a6513`, results `d78e344`. **V.**
>
> The old 0.165 [0.162, 0.168] is **S**. On the same host, the review-02 code adds +2.4 % (warm) and
> +9 % (cold) over `781dc0b`. The fall from July is environmental (host and libraries; PKI cold
> halves with cryptography 41 → 49, §5.E). This is the cached/off-chain verify; compare #21's
> uncached 9.7 ms. Source: `docs/review02/FOLLOWUP_FA.md`.

**#26** (replace the Exp. C/D clause; the A/B text is unchanged)
> … verify **O(1) in claim count**: about 0.17–0.20 ms over N = 1…32 (median of 5 pre-declared
> repeats, 300 warm runs/point; spread 1.14). Selective disclosure is O(k) at 0.004 ms/claim; p95
> ≤ 0.54 ms everywhere. V2V warm verification is linear in neighbours at **0.164 ms/neighbour**
> (R² = 0.9998; repeats 0.159–0.171). There is no saturation for P ≤ 80 (13.1 ms = 13 % of the
> 100 ms budget at P = 80). The saturation point **P\* ≈ 609 (repeats 586–627) is a linear
> extrapolation beyond the tested range**. At f = 0.5 it is ≈305. M0, simulated mobility, real
> crypto, commits `fd25d05`/`38909df`/`05803c3`. **V** for Exp. C/D.
>
> The old 0.130 ms/neighbour and P\* ≈ 772 are **S**: on the same host, the pre-review-02 code gives
> 0.162 ms/neighbour (P\* ≈ 618), so the change is environmental. The Exp. C run-of-record table
> (`scaling_verify_richness.tex`) prints "O(N)" from a noisy single run (repeat 1). Cite the
> confirmation block (`scaling_verify_repeats/C_confirmation_R6-R10_summary.json`), not that table's
> label.

**#17** (stays S; update its pointer)
> **S**: the bundle-lineage 0.165 ms and P\* ≈ 772 are superseded by #27 (0.153 ms
> [0.151, 0.154]) and #26 (P\* ≈ 609, extrapolated), both re-executed on trunk 2026-10-04
> (`docs/review02/FOLLOWUP_FA.md`).

**Also stale, not edited here** (owned elsewhere):
- `LATENCY_BUDGET.md` §5 cites "0.165 ms … ≈772 neighbours at 0.130 ms/neighbour".
- 0.165 ms is also cited in `README.md`, `CAPABILITIES.md`, `COMPOSITION.md`, `INVENTORY.md`,
  `QUICKSTART.md`, `MASTER_UPDATE.md`, `CHANGELOG.md`, `SIDE_PAPERS.md` and thesis chapters 5–6.
- The "90 failures = 3 attacks" wording in `INVENTORY.md` and chapter 5 is also stale.
- The chapter text needs the author's framing approval.

## 9. Limitations
- The host is shared with other agent sessions, and the CPU is not pinned. This is the main source
  of Exp. C's single-run noise. Repeats and a same-host A/B are reported for that reason.
- The A/B baseline ran after the new runs, not interleaved, so a slow drift in host load would bias
  the code-effect estimates. They are small (+2–10 %) and should be read as approximate.
- The July library versions are not recorded, so the environment shift cannot be split between
  host and library.
- The #27 "p95" is the 95th percentile of run medians, as defined in the script. It is not a
  per-message tail.
- Exp. D measures crypto load only: no radio, MAC or queueing, and no replay cache in the SUMO
  layer (PASS2_T §6).
