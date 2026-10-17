# Identity Sandbox Explorer (next visual pass)

React artifact (Stage 14 lineage) that REPLAYS JSONL traces from `traces/`
instead of simulating. Panels: identity cards (DID, keys, delegates, VCs +
revocation state), transaction timeline (gas, F1–F12 tags), I2I channel pane
(handshake sequence + teardown on revocation), and a 12-function coverage
tracker driven by `fnId` fields. Input: paste or upload a trace file.
