# Replay viewer

`replay.html` plays back a V2V identity event trace
(`docs/visual/TRACE_SCHEMA.md`) in a browser. It has no dependencies.

## Open

| Situation | How |
|---|---|
| Offline, anywhere | open a built page such as `replay_sim_median.html` (trace embedded) |
| Any trace, from disk | open `replay.html`, use the file picker, choose a `.jsonl` from `docs/visual/traces/` |
| Served over HTTP | `python3 -m http.server -d docs/visual` then `http://localhost:8000/replay/replay.html?trace=../traces/sumo_traci_60s.jsonl` |

## Controls

- **Space** plays or pauses. **→** steps one snapshot. The slider scrubs.
- **Click a vehicle** to see its identity card: identity layer, VIN, DID or
  certificate note, position, and what it has verified as a receiver so far.
- **Follow selected** keeps a SUMO-mode view centred on the selected vehicle.

## What the marks mean

| Mark | Meaning |
|---|---|
| blue box | SSI / MOBI VID vehicle (W3C credential, secp256k1) |
| ochre box | PKI vehicle (X.509 pseudonym certificate, ECDSA P-256) |
| thick ink line | cold: first contact, full credential verification |
| thin grey line | warm: signature check against the cached key |
| red dashed line | rejected verification |
| orange line and ring | FCW / EEBL emergency broadcast |

Counters are exact over every broadcast up to the current time, even in a
page whose position snapshots were thinned.

## Rebuild the embedded pages

```bash
python3 cv2x-testbed/sumo/viz/build_replay.py docs/visual/traces/sim_50v_20s_median.jsonl docs/visual/replay/replay_sim_median.html
python3 cv2x-testbed/sumo/viz/build_replay.py docs/visual/traces/sumo_traci_60s.jsonl docs/visual/replay/replay_sumo.html
```

## Video for slides

`replay_20s.mp4` and `replay_10s.gif` were captured from `replay_sim_median.html`
by stepping the scrubber one 100 ms step per frame in headless Chromium and
encoding with ffmpeg at 10 fps. The script is in `docs/visual/VISUAL_PHASES_PROMPTS.md`
Phase 3, item 3. Frames are deterministic, so the video is real time.
