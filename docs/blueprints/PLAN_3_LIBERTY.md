# Plan 3 — The Liberty Plan (what to build beyond the drawing set)

**Author:** Nikhil Prakash · **Date:** 2026-10-22
**Stance:** these are the moves that turn a good set of figures into a durable research instrument. Items marked **DONE** were executed in this session. The rest are ranked by value per hour.

## L1 — Drawings generated from code, not drawn by hand — **DONE (partially)**

The whole set is produced by `make_blueprints.py` with a small pure-SVG library (`bplib.py`). No drawing tool, no binary source files, one command to regenerate. Numbers are still typed into the sheet modules with their register row next to them. Plan 2 P2 closes the gap by loading them from the result files and failing CI on drift. When that lands, a sheet cannot show a number the repository does not produce. That property is what gives the military-drawing format its credibility. It is the same discipline as `MEASUREMENT_CONDITIONS.md`, extended to figures.

## L2 — The primitives atlas as the anchor figure

BP-101, BP-102 and BP-104 are the most important sheets in the set. They show that the whole system is built from about a dozen primitives (keccak256, secp256k1, ecrecover, EIP-191/155, SSTORE, LOG, CALL, CREATE, time, nonce, SHA-256, HKDF, AES-GCM). Every higher function is a composition of them. Plan 2 P3 merges them into one poster, BP-100. That poster is the figure to open the thesis defence with. It answers "what is this made of?" before anyone asks "does it work?".

## L3 — Security inheritance, stated with its limits — **DONE**

`SECURITY_GUARANTEE_INHERITANCE.md` and BP-402 make the point that an identity operation travels the same path as a value transfer and gets the same guarantee. They also draw the waterline where the inheritance stops. The limit is what makes the claim defensible in front of an examiner. Plan 2 P7 extends this to BP-404 and BP-405.

## L4 — An executable blueprint

Each sequence sheet (BP-301 … BP-303) describes a code path. The next step is to make each sheet a test: a pytest that runs the use case, records the actual call order through a tracing shim, and asserts it matches the message list in the sheet module. A sequence diagram that fails CI when the code changes is worth more than one that is merely accurate today. Estimated effort is one day for the shim and one hour per sequence.

## L5 — Live instrument panels

BP-501 and BP-502 are static. A small HTML page could read `gas_benchmark.json` and `freshness_k.json` and let a reader drag *k* and *f* to watch P*(f) and staleness move. That turns the latency budget from an argument into a tool a reviewer can test. Build it after P2, from the same data loader.

## L6 — The same set for the baselines

Draw BP-8xx for the PKI baseline (IEEE 1609.2 CA hierarchy, enrolment and pseudonym certificates, CRL) and the centralised registry, in identical format. Side by side with BP-001, the reader sees exactly which deck each design trusts. The PKI trusts a CA operator where the DLT trusts consensus. That contrast is the core of the "alternative to PKI" hypothesis.

## L7 — A side paper

"Engineering drawings for decentralised identity systems: a reproducible, measurement-bound figure set" is a short, publishable methods contribution. It would cover the format, the generation-from-code rule, the waterline idea, and the primitives atlas. Add it to `SIDE_PAPERS.md` as a candidate.

## Ranked next actions

1. Plan 2 P1 and P2: number audit, then data-bound generation with a CI check.
2. Plan 2 P3: the primitives atlas BP-100.
3. L4: make BP-301 executable as the proof of concept.
4. Plan 2 P7: BP-404 and BP-405, with sourced `param` values for the chains named.
5. L6: the baseline sheets.
