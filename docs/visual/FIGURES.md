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

**V-11 · One message, anatomised** · `figures/packet_anatomy/F7_packet_anatomy.png` (+ `.svg`, sizes in `.json`)
> One real signed BSM per population, built by the harness's own identity
> layers (`python3 cv2x-testbed/sumo/viz/packet_anatomy.py --seed 1`). The SSI package is
> 1,739 bytes: 134 payload, 132 signature, 57 sender DID and **1,408 credential**.
> The PKI package is 882 bytes: 135 payload, 144 signature and 558 certificate.
> These are compact-JSON sizes as the harness packages them in-process, not
> over-the-air sizes, since 1609.2 and J2735 use ASN.1 UPER. The composition is
> the point. The harness attaches the W3C credential to every message, but a
> receiver needs it only at first contact. Chapter 6 should state the
> bandwidth cost of that choice, and the alternative of sending the credential
> on first contact or on request.

**V-12 · Replay video** · `replay/replay_20s.mp4` (H.264, 1500 px, 10 fps), `replay/replay_10s.gif` (720 px, seconds 10–20)
> Twenty seconds of seed 6 at real time. Each frame is one 100 ms step of the
> embedded replay, captured deterministically by scrubbing, not screen-recorded.
> The GIF covers the EEBL at t = 15 s.


**V-10 · Interactive replay** · `replay/replay_sim_median.html`, `replay/replay_sumo.html`; stills in `figures/replay/`
> Offline pages with the trace embedded. Space plays, → steps, a click opens a
> vehicle's identity card. The footer carries the schema, mobility, seed,
> commit and radio caveat.

**From the trunk, unchanged** (`cv2x-testbed/sumo/results/figures/README.md`):
the space-time plot, the latency plot, the animation GIF and the revocation
figure for seed 1 with RSUs. Use the animation in the defence beside V-10.

---

### Phase 5 — the attacker on the road

Traces at commit `3dddf6c`: `traces/sim_50v_20s_seed6_rogue_{uncredentialed,replay,tamper}.jsonl.gz`
(seed 6, 50 vehicles, 20 s, mock mobility). The rogue joins at t = 10 s and
drives at 25 m/s in the middle lane. It broadcasts every step to its 8 nearest
vehicles within 300 m.

```bash
cd cv2x-testbed/sumo
python3 sumo_identity_integration.py --simulate --duration 20 --vehicles 50 --seed 6 --rogue uncredentialed \
    --stage-timers --results /tmp/r.json --trace ../../docs/visual/traces/sim_50v_20s_seed6_rogue_uncredentialed.jsonl.gz
# replay and tamper: same, --rogue replay / --rogue tamper, without --stage-timers
cd ../.. && V=cv2x-testbed/sumo/viz
python3 $V/thesis_figures.py docs/visual/traces/sim_50v_20s_seed6_rogue_uncredentialed.jsonl.gz --t 12 --focus rogue_001 --only F1 F2 F8 F9 --receiver veh_035
python3 $V/thesis_figures.py docs/visual/traces/sim_50v_20s_seed6_rogue_replay.jsonl.gz --only F9
python3 $V/thesis_figures.py docs/visual/traces/sim_50v_20s_seed6_rogue_tamper.jsonl.gz --only F9
```

| Mode | Rogue messages | Receptions | Rejected (reason) | Accepted |
|---|--:|--:|---|--:|
| uncredentialed (valid key and DID, no credential) | 100 | 617 | 617 (no_credential) | 0 |
| replay (nearest genuine package re-sent verbatim, same step) | 100 | 517 | 500 (replay) | **17** |
| tamper (nearest genuine package, position moved 50 m) | 100 | 517 | 500 (signature) + 17 (binding) | 0 |

**V-13 · The rogue on the road** · `figures/sim_50v_20s_seed6_rogue_uncredentialed/F1_road_frame_t012.png`
> t = 12 s. The rogue (ink, orange outline) holds a valid secp256k1 key and a
> `did:ethr` DID but no credential. All six of its links in this step are
> rejected; genuine traffic around it continues unchanged.

**V-14 · Rejected, and why** · `…/F9_rejections.png` for each mode
> Every receiver-side rejection by the verifier's reason, plus any rogue
> message that was accepted. **In replay mode, 17 replays were accepted.** They
> reached receivers that had not received the original, because those
> receivers were not among the original sender's 8 nearest, and the replay
> was inside the freshness window. Sixteen of the 17 were warm: the receiver
> already knew the genuine sender. The content is genuine and fresh, so
> authenticity holds. The rogue extends the message's reach, and the verifier
> has no position-plausibility check. All accepted replays fall in the first
> 1.6 s after the rogue joins.

**V-15 · Where cold latency goes** · `…/F8_cold_stages.png`
> Median per stage of successful first-contact verifications (`--stage-timers`).
> SSI: credential verification and DID binding 0.259 ms; signature recovery
> 0.167 ms. PKI: X.509 chain, validity and CRL 0.126 ms; ECDSA verify 0.097 ms.
> The stage timers add their own overhead, so the figure shows proportions; the
> results of record are #27.

**V-16 · A receiver hit by the rogue** · `…/F2_contact_matrix_veh_035.png`
> One receiver's peers over time. The rogue appears from t = 10 s as a row of
> rejections, never cached.

**Replay** · `replay/replay_rogue_replay.html`: the replay-mode run offline,
with the per-reason rejection counter.

## Not yet drawn


