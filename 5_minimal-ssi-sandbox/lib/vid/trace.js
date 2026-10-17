// Shared JSONL trace emitter for VID scenarios (S7, S8, S14, S16, S17). Schema: traces/SCHEMA.md.
// Extension tags used beyond F1–F12:
//   G0 addRoot · G1 registerIssuer · G2 endorseIssuer · G3 revokeEndorsement · G4 isEndorsed
//   T1 declare (on-chain typing) · T2 verifyTyped (composite view)
//   B1 anchorBatch · B2 verifyInclusion · B3 revokeBatch · C1–C4 Set C (harness)
//   kind=offchain entries record signature verification, cache reads, queued writes and
//   credential construction that deliberately never touch the chain.
//
// Timing (schema v1.1, additive): latencyMs = wall-clock from submission to receipt (tx) or
// from call to return (view), measured in this process. On the Hardhat in-process network it
// is a LOWER BOUND on any real network and must never be cited as a latency result — it exists
// so the same scripts yield comparable numbers on Besu QBFT or a remote node (HDA doc 05 §7).
const fs = require("fs");

function makeTrace(impl) {
  const trace = [];
  let step = 0;
  function log(entry) {
    trace.push({ seq: ++step, impl, ts: Date.now(), ...entry });
    const tag = entry.fnId ? `${entry.fnId} ` : "";
    console.log(`[${step}] ${tag}${entry.fn || entry.phase}: ${entry.note || ""}`);
  }
  async function tx(label, fnId, identity, promise, extra = {}) {
    const t0 = performance.now();
    const t = await promise;
    const rc = await t.wait();
    const latencyMs = +(performance.now() - t0).toFixed(2);
    log({ kind: "tx", fn: label, fnId, identity, txHash: rc.hash, gasUsed: rc.gasUsed.toString(),
          events: rc.logs.length, latencyMs, note: `gas=${rc.gasUsed}${extra.note ? " · " + extra.note : ""}` });
    return rc;
  }
  function view(label, fnId, identity, note, latencyMs) {
    log({ kind: "view", fn: label, fnId, identity, ...(latencyMs !== undefined ? { latencyMs } : {}), note });
  }
  // timedView: wraps a view-call promise and records its round-trip.
  async function timedView(label, fnId, identity, promise, noteFn) {
    const t0 = performance.now();
    const r = await promise;
    const latencyMs = +(performance.now() - t0).toFixed(2);
    view(label, fnId, identity, typeof noteFn === "function" ? noteFn(r) : noteFn, latencyMs);
    return r;
  }
  function off(phase, identity, note) { log({ kind: "offchain", phase, identity, note }); }
  function write(name) {
    const covered = new Set(trace.filter(e => e.fnId).map(e => e.fnId));
    const fset = [...covered].filter(x => /^F\d+$/.test(x)).length;
    log({ kind: "summary", phase: "done", note: `tags covered: ${[...covered].sort().join(",")} (F: ${fset}/12)` });
    const out = `traces/${name}_${impl}_${Date.now()}.jsonl`;
    fs.writeFileSync(out, trace.map(e => JSON.stringify(e)).join("\n"));
    console.log(`\nTrace written: ${out} (${trace.length} entries)`);
    return out;
  }
  function parseEvent(c, rc, name) {
    return rc.logs.map(l => { try { return c.interface.parseLog(l); } catch { return null; } })
      .find(e => e && e.name === name).args;
  }
  return { log, tx, view, timedView, off, write, parseEvent, trace };
}

module.exports = { makeTrace };
