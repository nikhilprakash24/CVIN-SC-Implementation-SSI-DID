# Figures — captions, commands and what each may claim

Caption source for the visual figures (Phase 2 of `VISUAL_PHASES_PROMPTS.md`).
Chapter 5 already states the rule: figures from traces *illustrate one seed;
the evidence is the 30-run statistics* (§5.4, register #27 and #44–#48). Every
caption below keeps to it. Numbers in captions are counts and per-run
summaries from the named trace, not register values.

All traces are at commit `61d7157`, `code_dirty: false`
(`traces/README.md`). Commands run from the repository root.

```bash
V=cv2x-testbed/sumo/viz
python3 $V/thesis_figures.py docs/visual/traces/sim_50v_20s_seed6.jsonl.gz --t 0 10 15 --focus veh_001 --svg
python3 $V/thesis_figures.py docs/visual/traces/sim_50v_20s_seed1.jsonl.gz --only F3 F5
python3 $V/thesis_figures.py docs/visual/traces/sumo_traci_60s.jsonl.gz --t 15 45 --focus platoon_leader
python3 $V/sumo_views.py coldmap docs/visual/traces/sumo_traci_60s.jsonl.gz
python3 $V/sumo_views.py pairs docs/visual/traces/sumo_gui_45s.jsonl.gz docs/visual/sumo_frames
```

**Caveat every caption carries:** mobility source (mock or SUMO/TraCI); no
radio channel and no MAC, with in-process delivery to the 8 nearest within
300 m; latencies are compute time of identity verification on one host.

---

### Chapter 4 — the message path

**V-1 · The road at t = 0 s** · `figures/sim_50v_20s_seed6/F1_road_frame_t000.png`
> One 100 ms step of a 50-vehicle run (35 SSI, 15 PKI; mock mobility, seed 6).
> Each line is a receiver-side verification that ran. At t = 0 every
> neighbour is a first contact, so links are cold: full credential
> verification. Illustrates the message path of §4.x; no radio channel is
> modelled.

**V-2 · The road at t = 15 s** · `…/F1_road_frame_t015.png`
> The same run fifteen seconds in, during the emergency brake light from
> `veh_001`. Steady-state links are warm: one signature check against a cached
> key. The EEBL broadcast in this step is signed and verified like every other
> BSM. The static frame draws it as ordinary links; the replay (V-10) marks it in
> orange.

**V-3 · SUMO beside the identity layer** · `figures/pairs/pair_t030.png` (also t = 10, 20, 40)
> Left: a SUMO-GUI 1.28 frame from a TraCI run (20 vehicles, view tracking
> `platoon_leader`; blue SSI, ochre PKI). Right: the identity layer of the
> same run at the same instant, drawn from its trace. The two panels share one
> run and one clock.

**V-4 · Where trust is paid for** · `figures/sumo_coldmap/coldmap_sumo_traci_60s.png`
> Every first-contact verification of a 60 s TraCI run (252 cold
> verifications; 26 vehicles), placed at the receiver's position on the
> network read from `highway_intersection.net.xml`. First contacts cluster
> where vehicles enter the highway, not at the intersection; in 60 s few
> vehicles reach the junction.

### Chapter 5 — §5.4 (RQ4 / H3) and the attack results

**V-5 · Verify once, check every message** · `figures/sim_50v_20s_seed6/F2_contact_matrix_veh_045.png`
> One receiver and every peer it heard over 20 s. Each peer's credential is
> verified once at first contact; every later 10 Hz message is one signature
> check. PKI peers re-enter cold when their pseudonym certificate rotates every
> 100 messages, while an SSI peer's DID binding is verified once. Illustrates the
> cold/warm split behind #27.

**V-6 · Every verification against the budget** · `…/F3_latency_strip.png`
> All 50,818 receiver-side verifications of seed 6, on a log scale, against the
> 10 ms signature-check target and the 100 ms V2V budget. In this run the
> 95th-percentile warm SSI verification was 0.315 ms. The worst seed of the
> N=30 set (seed 1, `figures/sim_50v_20s_seed1/F3_latency_strip.png`) looks
> the same. The across-run statistic is #27.

**V-7 · Cold vs warm** · `…/F5_cold_warm_hist.png`
> Latency distributions in seed 6. The per-run medians are listed below; the
> across-run medians with CIs are in #27.

| Population | Path | n | Median (ms) | p95 (ms) |
|---|---|--:|--:|--:|
| SSI | cold | 219 | 0.436 | 0.613 |
| SSI | warm | 37,064 | 0.183 | 0.315 |
| PKI | cold | 152 | 0.260 | 0.344 |
| PKI | warm | 13,383 | 0.110 | 0.167 |

**V-8 · Attack board** · `…/F4_attack_board.png`
> The seven V2V attacks injected after the run, each rejected by the
> receiver's real verification path: tampered (PKI, SSI), stale (PKI, SSI),
> replayed (PKI, SSI) and uncredentialed sender. The 30/30-run result is in the
> attack rows of the register; the infrastructure attacks (I2, #45) are drawn by
> the trunk renderer.

**V-9 · Safety messages ride the verified path** · `…/F6_safety_events.png`
> In seed 6, 23 forward-collision warnings and one emergency brake light were
> raised, with the receivers that verified each. FCW is evaluated on highway
> lanes only.

### Defence and appendix

**V-10 · Interactive replay** · `replay/replay_sim_median.html`, `replay/replay_sumo.html`; stills in `figures/replay/`
> Offline pages with the trace embedded. Space plays, → steps, a click opens a
> vehicle's identity card. The footer carries the schema, mobility, seed,
> commit and radio caveat.

**From the trunk, unchanged** (`cv2x-testbed/sumo/results/figures/README.md`):
the space-time plot, the latency plot, the animation GIF and the revocation
figure for seed 1 with RSUs. Use the animation in the defence beside V-10.

---

## Not yet drawn

- **F7 · one message, anatomised.** The signed SSI and PKI packages with field
  sizes. Needs a `--dump-packages` flag; Phase 2 item 4.
- **F8 · where cold latency goes** (per-stage timers) and **F9 · rejections by
  reason** (rogue vehicle). Phase 5.
