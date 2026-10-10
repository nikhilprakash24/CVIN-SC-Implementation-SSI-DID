# Plan — SUMO Visualisation of the Identity-Verified Message Path

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Status:** **APPROVED by the author 2026-10-09 with defaults S-a (approve), S-b (no SUMO install), S-c (one trace of record per figure).** Design written under plan 2026-10-09 P2a. **P2b, which installs SUMO and runs it, waits for the author's
go-ahead (default Q2: no install).** The trace recorder works with the mock mobility too, so most of
this plan is executable without SUMO once the design is approved.
**Written:** 2026-10-09. **Serves:** cruxes C2 and C3 (`docs/thesis/CRUX_REGISTER.md`), thrust 3, the
defence.

## 1. What exists and what is missing
| Exists | Missing |
|---|---|
| `cv2x-testbed/sumo/sumo_identity_integration.py`: 50 vehicles, 10 Hz BSM, real PKI and SSI signing and verification, five injected attacks; TraCI path written but SUMO absent; `--simulate` mock mobility | any per-step record: results keep only aggregates (`results/v2v_latency*.json`) |
| a SUMO network and route file (`highway_intersection.net.xml`, `routes.rou.xml`, `simulation.sumocfg`) | rendering of that network |
| `eclipse-sumo` 1.24.0 wheel available through the proxy (95 MB; probed 2026-10-09, not installed) | an approved install |

## 2. What the visualisation must show, and must say
**Show:** vehicles moving on the network, coloured by identity population (PKI or SSI); each
broadcast and its receivers; each verification as cold, warm or rejected, with its measured
latency; injected attacks and their rejection; later, RSUs and SPaT (design note
`docs/design/INFRASTRUCTURE_MESSAGING.md`).

**Say, in the frame itself:** mobility source (mock or SUMO/TraCI), "no radio channel, no MAC,
in-process delivery to the 8 nearest neighbours within 300 m", the seed, the commit, the host.
A visual is the most persuasive figure in a defence, and this one carries the weakest fidelity in
the thesis, so its caveats travel with it.

## 3. Trace schema (JSON Lines, off by default)
`--trace PATH` writes one header line, then one line per event. Recording must not change the
aggregates: the gate is that a run with `--trace` reproduces the results file of the same seed
without it.

```json
{"type":"header","schema":"cvin-v2v-trace/1","commit":"…","dirty":false,"seed":42,"mobility":"mock|traci","step_ms":100,"vehicles":50,"radius_m":300,"max_receivers":8,"host":{"cpu":"…","python":"…","cryptography":"…"},"net":"highway_intersection.net.xml"}
{"type":"step","t":12.3,"vehicles":[{"id":"v07","x":1530.2,"y":12.0,"speed":27.1,"heading":90.0,"pop":"ssi"}]}
{"type":"tx","t":12.3,"msg":"m1834","from":"v07","kind":"BSM","attack":null}
{"type":"rx","t":12.3,"msg":"m1834","to":"v11","path":"cold|warm","ok":true,"reason":null,"verify_ms":0.398}
{"type":"rx","t":12.3,"msg":"m1835","to":"v11","path":"cold","ok":false,"reason":"tampered|unknown_sender|stale|replay","verify_ms":0.402}
```
Positions are written every step; tx/rx events as they happen. A 20 s, 50-vehicle run is about
10⁴ tx and 6·10⁴ rx events, a few MB uncompressed; traces of record are gzipped.

## 4. Renderers (all from a committed trace, one command each)
| Output | Use | Tool | Content |
|---|---|---|---|
| Static figures (PNG/SVG, 300 dpi) | thesis ch. 5 | matplotlib | (a) the network drawn from the `.net.xml` lane shapes, with vehicle tracks coloured by population; (b) a time × vehicle heat strip of verify latency, cold and warm separated; (c) attack markers on the timeline with rejection reason |
| Animation (GIF/MP4) | defence | matplotlib animation | vehicles moving, broadcast rings, receiver links green (verified) or red (rejected), latency counter, caveat banner |
| Interactive panel | results dashboard | inline JS, no external data calls | time slider, play/pause, click a vehicle to see its DID, its credential and its last ten verifications; the trace is down-sampled for the page |

Colour carries meaning only with a text label (PKI / SSI; verified / rejected), following the
dashboard's palette.

## 5. Steps and gates
| Step | Work | Gate | Needs |
|---|---|---|---|
| V1 | Implement `--trace` in the harness (mock and TraCI paths) | trace written; aggregates of the same seed identical with and without `--trace` | design approval |
| V2 | `cv2x-testbed/sumo/render_trace.py`: static figures and animation | figures regenerate byte-stable from the committed trace | V1 |
| V3 | Dashboard panel from a down-sampled trace | renders at phone width; caveat banner visible | V1, P1 |
| V4 | Install SUMO from the wheel; run the pre-registered S1–S3 (`docs/PLAN_MOBI_SUMO.md`) with TraCI mobility; record traces | register rows for S1–S3; `--simulate` results labelled as such | **Q2 go-ahead** |
| V5 | RSU layer (SPaT broadcasts, infrastructure identities) in trace and renderers | I1–I3 traces render | design note approval (I-a), V1 |

## 6. Decisions for the author
| # | Decision | Default |
|---|---|---|
| S-a | Approve the trace schema and the renderers as specified | — (blocks V1) |
| S-b | Install SUMO (V4) | no (Q2) |
| S-c | Commit traces of record (gzipped, a few MB each), or regenerate on demand from seed and commit | commit one trace per figure; others on demand |

## 7. Status at the close of work milestone WM-1 (2026-10-10)
| Step | Status | Evidence |
|---|---|---|
| V1 `--trace` | done for the mock mobility; the TraCI path is written but untested (no SUMO, S-b) | `47c3314`; no-change gate on seed 7 |
| V2 renderers | done; gate re-checked 2026-10-10: all five outputs regenerate byte-identically from the committed traces | `cv2x-testbed/sumo/results/figures/README.md` |
| V3 dashboard panel | done (message-path replay) | dashboard v3–v5 |
| V4 SUMO install and S1–S3 | deferred (S-b; SC-22; N-4) | — |
| V5 RSU layer | done; I3 revocation figure | `f1f9e37` traces |
| Not built from §4 | the network drawing from `highway_intersection.net.xml` and the per-vehicle inspector (both need real mobility to mean anything) | WM-2 plan |
