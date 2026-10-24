# After-Action Report 33 — WM-2 A3b and A6 on the One Trunk (Plan 5, phase 8)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened and closed:** 2026-10-22 to 2026-10-23. **Plan:** `docs/PLAN_WM-2_A3B.md`, written and pushed before any run.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md` (rules 1.1.4–1.1.7, 1.1.10).

## 1. Outcome by batch (each from a clean commit, one producer at a time, no other load)

| Batch | Commit | Outcome |
|---|---|---|
| G gas | `ddb9b05` | nine-standard table, MOBI sweep, scaling, infrastructure gas (seed 1 and 1–30), pseudonym pool reproduce; attestation figures inside the documented 222,058–222,082 calldata range; the 30-run determinism record now on the C2 contracts (30/30) |
| L latency | `0b39570` | #21: ERC-1056 verify 15.5 ms, 5 RPCs (D51 adds a block read); #26 D: 0.156 ms/neighbour, P* ≈ 641; #27 at the recorded 20 s: SSI warm 0.142 ms; #44 I1 1.197 **at the band edge** (1.226 outside it before; not re-rolled); #45, #46 PASS; #48 0.805 ms |
| L3 freshness | `f1f3596` | staleness ≤ k − 1 everywhere; full refresh 5 RPCs; at t_local 0.35–0.40 ms both modes reach P*(0.5) ≥ 100 (probe k ≈ 26–31, full ≈ 90–114), so "no finite k on this host" is history; crux C4 now ties a knee to t_local |
| H harness | `1f4ace0` | A6 first: `dirtyMeasured` from the shared helper. Harness and HTTP-RPC: every gas cell identical; frontiers unchanged |

## 2. Findings
- **The Exp. D driver broke silently when the replay cache became the default** (`8c325cc`, clone lineage): it restarted simulation time at each neighbour count, so repeated timestamps were refused as replays. Fixed in `0b39570` with a regression test that fails on the old driver; the first batch-L outputs were discarded.
- **A producer default drifted from its run of record:** `run_v2v_stats.py` defaults to 30 s; #27 was recorded at 20 s. Re-run with `--duration 20`; the message counts then match the record exactly.
- **The I1 verdict is not robust.** Its ratio sits at the band's upper edge and lands either side between runs; reported as such, with both runs.
- **A claim tied to a host.** #37's "no finite k" depended on t_local; recorded as host-dependent rather than overturned.
- **One unverified explanation caught before commit:** "two attack cases added" (for 7 failures per run against 5) was not checked and was replaced by the observed counts.

## 3. Not re-run, disclosed
`infrastructure_gas_run1.json` (pre-seeding history); Exp. C in `scaling_verify.json` (its producer did not change; the file's stamp is shared with Exp. D).

## 4. Next
WM-2 A5 (claims.yaml with every quoted number checked against its result file), then A7, B3, D1.
