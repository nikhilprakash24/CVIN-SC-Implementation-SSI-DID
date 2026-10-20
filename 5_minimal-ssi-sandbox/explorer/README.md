# Identity Sandbox Explorer (Layer 2)

`index.html` — a single static page, no build step. Open it in a browser, paste or upload any
`traces/*.jsonl` file (schema v1 or v1.1) and it REPLAYS the trace: coverage tracker (F1–F12 plus
the extension tags G/T/B/C/Z/P), identity cards (per acting principal: tx count, gas, keys,
delegates, credentials issued/revoked, presentations, deactivation), the I2I channel / off-chain
pane (off-chain steps and revocation teardowns), and the full timeline with gas and `latencyMs`.
It renders only what the trace contains; nothing is simulated. A malformed trace fails with a
schema error naming the line and the missing field (WO-6 acceptance).
