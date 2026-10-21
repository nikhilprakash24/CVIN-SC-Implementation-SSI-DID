# Visual work — phases and prompts to run one at a time

**Use:** open a fresh chat per phase, paste the prompt block verbatim, let it
run, check the acceptance list, then move on. Each phase is self-contained and
tells the assistant where things are. Phases 0–2 are the thesis minimum;
3–5 make it good; 6–8 are the awesome rung.

Conventions every prompt relies on:

- Repository root is `CVIN-SC-Implementation-SSI-DID`; the branch for this work
  is `claude/simulation-visual-plan-gp4exp` (or a branch off it).
- Never overwrite `cv2x-testbed/sumo/results/v2v_latency.json`; traced runs pass
  `--results` to a scratch path.
- Every figure comes from `cv2x-testbed/sumo/viz/render_trace.py` or SUMO-GUI
  via `--screenshot-dir`; no manual screenshots of live windows.
- Palette and two-register rule: `docs/visual/VISUAL_PLAN.md` §4.

---

## Phase 0 — Confirm the environment (15 min)

**Goal:** the simulation, the renderer, the replay and real SUMO all run on this
machine before anything is drawn.

**Prompt:**
```
Read docs/visual/VISUAL_PLAN.md §0–§1 and docs/visual/TRACE_SCHEMA.md. Then verify the visual toolchain on this machine, step by step, reporting each result:
1. pip install -r cv2x-testbed/requirements.txt (at least: cryptography, eth-account, eth-keys, coincurve, matplotlib) and pip install eclipse-sumo; print sumo --version.
2. cd cv2x-testbed/sumo && python3 sumo_identity_integration.py --simulate --duration 5 --vehicles 20 --results /tmp/v2v_check.json --trace /tmp/check.jsonl ; confirm 7/7 attacks rejected and the trace has meta/enroll/snap/tx/safety/attack/summary events (count each).
3. netconvert -c net_src/netconvert.cfg and then sumo -c simulation.sumocfg --end 10 --no-step-log ; confirm it loads with no errors and inserts vehicles.
4. python3 sumo_identity_integration.py --duration 10 --results /tmp/v2v_traci.json --trace /tmp/traci.jsonl ; confirm "Mode: SUMO" and "SUMO started (sumo)".
5. python3 viz/render_trace.py /tmp/check.jsonl --out /tmp/figs ; confirm 7 PNGs.
6. If Xvfb exists: xvfb-run -a -s "-screen 0 1600x900x24" python3 sumo_identity_integration.py --gui --duration 8 --screenshot-dir /tmp/frames --screenshot-every 40 --gui-zoom 1500 --gui-track platoon_leader --results /tmp/v2v_gui.json ; confirm PNG frames of 1600x900.
Do not change any source file. End with a table: step, pass/fail, one-line note. If a step fails, show the exact error and stop there.
```

**Accept when:** all six rows pass, or the failing row has a concrete error you
can act on. `git status` shows no changes.

---

## Phase 1 — Reference traces for the thesis (1–2 h, mostly machine time)

**Goal:** the traces every chapter figure will be drawn from: the median seed of
the N=30 `--simulate` set and a 60 s TraCI run, plus per-seed traces so "worst
seed" figures are possible.

**Prompt:**
```
Context: docs/visual/VISUAL_PLAN.md (Rung 0–1), docs/visual/TRACE_SCHEMA.md, docs/MEASUREMENT_CONDITIONS.md row #27 (the V2V latency result of record), cv2x-testbed/sumo/run_v2v_stats.py (the N=30 driver).
Task:
1. Read run_v2v_stats.py. Add an optional --trace-dir DIR argument that, when set, passes --trace DIR/seed_<seed>.jsonl and --results DIR/seed_<seed>.json to each seeded run, so traced runs never touch results/v2v_latency.json. Keep the default behaviour byte-identical (run the driver once without the flag on a tiny duration and diff its output format against the committed results/v2v_latency_stats.json keys).
2. Run the driver with --trace-dir docs/visual/traces/n30/ for the registered configuration (50 vehicles, 60 s, seeds as in the driver). Report the median seed by SSI warm p95 and the worst seed.
3. Copy or symlink the median-seed trace to docs/visual/traces/sim_50v_60s_median.jsonl and write its seed into docs/visual/traces/README.md with the command that made it, the git commit, python and coincurve versions.
4. Run one TraCI trace: python3 sumo_identity_integration.py --duration 120 --results /tmp/v2v_traci.json --trace docs/visual/traces/sumo_traci_120s.jsonl and record the same provenance.
5. If the n30 directory exceeds 100 MB, gzip the per-seed traces (keep the median and worst uncompressed) and note that render_trace.py needs gunzip first; otherwise leave them plain.
6. Add a short "Traced runs" paragraph to cv2x-testbed/sumo/README.md pointing to docs/visual/TRACE_SCHEMA.md.
Commit with a message that lists the seeds and the median/worst choice. Do not change any latency number in README.md or MEASUREMENT_CONDITIONS.md.
```

**Accept when:** `docs/visual/traces/README.md` names the median seed and the
commands; the results of record are unchanged (`git diff --stat` shows no
`results/v2v_latency*.json`).

---

## Phase 2 — Chapter figures with captions (2 h)

**Goal:** the F1–F6 set for chapter 5 rendered from the median trace and the
TraCI trace, each with a caption that cites its register row, placed in the
thesis tree.

**Prompt:**
```
Context: docs/visual/VISUAL_PLAN.md §2 (Rung 1) and §3 (shot list S2–S8), docs/thesis/chapter5-results/README.md, docs/MEASUREMENT_CONDITIONS.md.
Task:
1. Render the full F1–F6 set from docs/visual/traces/sim_50v_60s_median.jsonl with --t 0 15 and the EEBL instant (find it in the trace's safety events), --focus the first SSI vehicle, and --svg. Render F2, F3 and F5 from docs/visual/traces/sumo_traci_120s.jsonl.
2. Look at every PNG. For each, check: title counts match the trace (recount with a short python snippet), legend names every colour, footer present, nothing overlaps. Fix the renderer if anything is wrong; do not hand-edit images.
3. Write docs/thesis/chapter5-results/FIGURES.md: for each figure, the file path, the exact render command, a caption of 2–4 sentences in the thesis voice, the register row it supports (#27 for latency; the attack-rejection rows for F4), and the mock/real statement from VISUAL_PLAN.md §1 that the caption must carry (e.g. "compute latency only; no channel modelled").
4. Add an F7 "one message, anatomised" figure to render_trace.py: take one real SSI package and one real PKI package from a 2 s --simulate run (add a --dump-packages N flag that writes the first N signed packages of each population to JSON, without touching the measured path), and draw the two as labelled stacks with field names and byte sizes (json.dumps length). Caption it as a diagram of real packets.
5. Update docs/visual/VISUAL_PLAN.md §8 with what changed.
Commit. Do not edit chapter prose beyond FIGURES.md.
```

**Accept when:** FIGURES.md exists with one entry per figure; every entry's
command reproduces its PNG; `git status` clean after commit.

---

## Phase 3 — The replay as a deliverable (1–2 h)

**Goal:** a single self-contained HTML you can open anywhere, plus a short
video of it for slides.

**Prompt:**
```
Context: docs/visual/replay/replay.html (single-file viewer; loads a trace by file picker, ?trace= when served, or an embedded <script id="embedded-trace"> block), docs/visual/VISUAL_PLAN.md Rung 2.
Task:
1. Write cv2x-testbed/sumo/viz/build_replay.py: given a trace path and an output path, copy replay.html and inject the trace text into the embedded-trace script block (escape "</script>" sequences), so the output opens from file:// with no picker. Add --thin N to keep every Nth snap event (never thin tx) if the file would exceed 25 MB.
2. Build docs/visual/replay/replay_sim_median.html from docs/visual/traces/sim_50v_60s_median.jsonl and docs/visual/replay/replay_sumo.html from the TraCI trace. Open each in headless Chromium with Playwright (executablePath /opt/pw-browsers/chromium if present), scrub to t=15, click the vehicle nearest the canvas centre, and screenshot to docs/visual/figures/replay/. Confirm zero page errors.
3. Record a 20 s clip: with Playwright, load the embedded sim replay, press Play at speed 1, capture a frame every 100 ms for 20 s into a scratch dir, then ffmpeg them into docs/visual/replay/replay_20s.mp4 (H.264, 1500 px wide, 10 fps) and a 10 s GIF at 720 px. If ffmpeg is missing, pip install imageio-ffmpeg and use its binary.
4. In replay.html: add keyboard hints to the bar, make the identity card show the peer's cold/warm state as seen from the selected vehicle (count cold events where the selected vehicle is the receiver), and keep the file under 40 KB. Test again.
5. Add docs/visual/replay/README.md: how to open, how to rebuild, the keyboard controls, what each colour means.
Commit.
```

**Accept when:** both embedded HTMLs open from a file:// URL and play; the MP4
exists and plays; the README explains rebuilding.

---

## Phase 4 — Real SUMO, properly shown (2–3 h)

**Goal:** SUMO-GUI frames that look like the figures (big enough glyphs, paper
background), a 1:1 pairing with the trace-drawn frame, and the intersection
scenario.

**Prompt:**
```
Context: docs/visual/VISUAL_PLAN.md Rung 3 and §7 (vehicle glyph size issue), cv2x-testbed/sumo/gui_settings.xml, start_sumo() and assign_vehicle_identity() in cv2x-testbed/sumo/sumo_identity_integration.py, SUMO 1.28 GUI settings documentation (sumo.dlr.de/docs/sumo-gui.html, "Changing the appearance").
Task:
1. Make vehicles legible in captured frames. Try, in order, and keep the first that works: (a) correct attribute names for vehicle exaggeration in the <vehicles> element of gui_settings.xml for SUMO 1.28 (check the XSD at sumo/data/xsd/viewsettings_file.xsd inside the eclipse-sumo wheel), (b) traci.gui.setZoom to 3000 with --gui-track, (c) larger --window-size. Target: a vehicle at least 24 px long in a 1600x900 frame with its id readable.
2. Capture frames every 1 s for a 60 s run tracking platoon_leader, and a second run with the view fixed on the intersection (no tracking, zoom so that 400 m of each approach is visible) at 1 s. Save under docs/visual/sumo_frames/<run>/.
3. Pair them with the trace: run the same two runs with --trace, render F1 at the same t values (every 10 s), and build docs/visual/figures/pairs/pair_t<T>.png: SUMO frame on the left, F1 on the right, same t, one provenance footer. Use PIL or a small matplotlib layout; no manual editing.
4. Intersection figure: from the intersection-run trace, draw cold verifications as dots at the receiver's x,y position (not lane rows; real coordinates) over the netconvert network outline drawn with sumolib. Expect first contacts to cluster where north–south traffic meets the highway. Save as docs/visual/figures/sumo_intersection_cold_map.png with a caption line.
5. Note in docs/visual/VISUAL_PLAN.md §7 that FCW uses highway geometry only, and add a one-line guard in forward_collision_warning so it returns None for vehicles whose lane id does not start with "highway".
Commit, with the frame counts and the chosen fix for glyph size in the message.
```

**Accept when:** a frame shows readable vehicle ids and blue/ochre bodies; the
pair images line up at the same t; the intersection map shows clustered cold dots.

---

## Phase 5 — The attacker on the road and the cold path anatomised (3 h)

**Goal:** make the security result visible in motion, and show where cold
latency goes.

**Prompt:**
```
Context: run_attack_tests() in cv2x-testbed/sumo/sumo_identity_integration.py (attacks run after the loop against a probe receiver), docs/visual/replay/replay.html, docs/THREAT_MODEL.md (A1–A4), docs/PLAN_MOBI_SUMO.md S2 (per-stage timing).
Task:
1. Add a --rogue flag: in --simulate mode, insert one vehicle "rogue_001" at t=10 s that drives with the traffic, holds a valid secp256k1 key and a did:ethr DID but no credential, and broadcasts BSMs every step like the others. Its receivers must reject every message (uncredentialed sender). Add a second rogue variant --rogue-replay that re-broadcasts a captured genuine package from a neighbour every step (replay). Trace events for these must carry pop "rogue" and the existing rx format with ok=false, and a new field reason ("no_credential" | "replay" | "stale" | "tamper") taken from the verifier's failure path; if the verifier does not expose the reason, add a last_failure attribute to both identity layers without changing their return signatures.
2. Confirm the registered results are unaffected: run the default --simulate 10 s with and without --rogue and show that the pki/ssi population blocks are identical except for the rogue's receivers' failure counts.
3. Replay: colour rogue vehicles black with a spray-orange outline; draw their links red dashed; show the reason in the event log; add a "rejected" counter per reason to the HUD.
4. Renderer: add F9 "rejections by reason over time" and extend F1 to draw rogue vehicles.
5. Per-stage timers (S2): add stage boundaries inside SSIIdentityLayer.verify cold path (vc_verify_ms, did_binding_ms, sig_recover_ms) and PKI cold path (chain_ms, validity_crl_ms, ecdsa_ms), recorded only into the trace tx.rx entries as a 5th element (dict), not into the results JSON. Render F8 "where cold latency goes" as stacked bars of median stage ms per population. State in the caption that the stage timers add their own overhead and show the total vs the single-timer cold median from the same run.
Commit. Report the identical-blocks check verbatim.
```

**Accept when:** the replay shows a black vehicle whose every link is red with a
reason; F8 and F9 render; the population blocks are identical with/without the
rogue.

---

## Phase 6 — Defence deck and the poster (2 h)

**Goal:** slides and a poster that use only the figures above, in the two
registers.

**Prompt:**
```
Context: docs/visual/VISUAL_PLAN.md §4 (style, palette, two registers) and §6 (illustration prompts P1–P5), docs/visual/figures/, docs/visual/replay/replay_20s.mp4, COMPOSITION.md (the thesis argument).
Task:
1. Build a 12-slide defence deck (pptx via the pptx skill, or Gamma if available) with this spine: title (P5 style, or the poster hero) → the question (RQ1–RQ4 as four lines) → the message path (F1 at t=0 and t=15) → verify once, check every message (F2) → every verification against the budget (F3) → cold vs warm (F5) → the attack board (F4) → the rogue on the road (replay still + the MP4 embedded or linked) → gas: the create-identity table from README as one bar figure → the frontier (one sentence, chapter 6) → limitations in the mock/real table from VISUAL_PLAN.md §1 → one slide of what's next. Every data slide keeps the figure's footer visible. Titles in the stencil monospace voice, body text in the deck's sans.
2. Build one A1 poster (PDF, 594x841 mm) with F1 as the hero across the top, F3 as a band, F2 and F5 side by side, the attack board down the right edge, the mock/real table bottom-left, QR or short URL to the replay. Paper background, blue/ochre only, spray for stamps.
3. Export each slide to PNG into docs/visual/deck/ and the poster to docs/visual/poster/; write a one-line index.
Do not generate images with an image model in this phase; illustrations are Phase 7.
```

**Accept when:** the deck opens, every figure is the committed PNG (not a
re-drawn version), and the poster PDF is vector where the source was SVG.

---

## Phase 7 — Illustrations from prompts, and the line we don't cross (1 h)

**Goal:** chapter openers and the methodology schematic from the P1–P5 prompts,
clearly labelled as illustrations.

**Prompt:**
```
Context: docs/visual/VISUAL_PLAN.md §6 prompts P1–P5 and §4 "what is not allowed".
Task:
1. Generate P1, P2, P3 and P5 with the available image tool (or produce P3 as an SVG diagram by hand if the tool draws text badly; diagrams with many labels are usually better hand-drawn). Save to docs/visual/illustrations/ with the prompt text beside each in a .txt.
2. For each, check: palette within paper/ink/blue/ochre/spray; no numbers; no axis; legible labels. Reject and regenerate anything that invents a statistic or a logo.
3. Write docs/visual/illustrations/README.md: each file, where it is allowed to appear (chapter opener, slide, poster), and the mandatory caption suffix "(illustration)".
Do not place any illustration in docs/thesis/chapter5-results.
```

**Accept when:** every illustration has its prompt beside it and the README
says where it may be used.

---

## Phase 8 — Final visual QA (45 min)

**Prompt:**
```
Context: everything under docs/visual/ and docs/thesis/chapter5-results/FIGURES.md.
Task: audit every figure referenced by FIGURES.md and the deck.
For each figure: (1) re-run its command into a scratch dir and confirm the PNG is pixel-identical or report the diff; (2) confirm the footer names a trace that exists on the branch; (3) confirm the counts in the title match a recount from that trace; (4) confirm the caption carries the mock/real statement; (5) confirm no colour carries meaning without a word. Output one table, one row per figure, five pass/fail columns, and fix the renderer for any fail (never the image). Then update docs/INDEX.md with a row "How is the simulation shown?" pointing to docs/visual/VISUAL_PLAN.md, and docs/SCOPE_CHANGES.md with the confirmation that the pre-2026-10 SUMO network did not load in real SUMO and all earlier SUMO-labelled runs were --simulate. Commit.
```

**Accept when:** the table is all pass; INDEX and SCOPE_CHANGES carry the two
rows.

---

## If a phase goes wrong

- A figure "looks wrong": fix `render_trace.py`, rerender, never edit the PNG.
- A number in a title disagrees with the register: the register wins; the
  figure is from a different run than the result of record, so say so in the
  caption or rerender from the median trace.
- SUMO will not install: Phases 1–3 and 5–8 do not need it; mark Phase 4 "later"
  and keep the `--simulate` footers honest.
- The trace is too big: `--trace-every 5` thins positions only; counts stay exact.
