"use strict";
// S6 — L6: verifier-side read path after a realistic lifecycle.
const { runLifecycle } = require("./lifecycle");
const { credHash, log } = require("./common");

async function run(ctx) {
  const rows = [];
  const { n, warmup } = ctx.opts;
  for (const adapterId of ctx.adapterIds) {
    log(ctx, `[resolve] ${adapterId}`);
    const { adapter, actors, handle } = await runLifecycle(ctx, adapterId, "resolve-setup");
    const c = credHash(ctx, adapterId, "lifecycle", "reg2");
    const rd = async (op, fn) => {
      if (!adapter.supports(op)) { rows.push({ adapter: adapterId, scenario: "resolve", op, supported: false, reason: adapter.unsupported[op] }); return; }
      const row = await ctx.collector.repeatRead({ adapter: adapterId, scenario: "resolve", op }, fn, { n, warmup });
      const { latencySamples, ...rest } = row;
      rows.push({ ...rest, supported: true, latencySamples });
      log(ctx, `${op.padEnd(22)} rpc=${row.readRpcCalls} bytes=${row.readBytes} med=${row.latency.median}ms p95=${row.latency.p95}ms`);
    };
    await rd("R3_resolve_document", () => adapter.resolveDocument(handle));
    await rd("R1_resolve_owner", () => adapter.resolveOwner(handle));
    await rd("R4_verify_delegate", () => adapter.verifyDelegate(handle, actors.delegateKey));
    await rd("V6_status_check", () => adapter.statusCheck(handle, c));
  }
  return rows;
}

module.exports = { run };
