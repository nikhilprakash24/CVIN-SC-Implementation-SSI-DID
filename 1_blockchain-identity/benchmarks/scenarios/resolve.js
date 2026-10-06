"use strict";
// S6 — L6: verifier-side read path after a realistic lifecycle.
const { runLifecycle } = require("./lifecycle");
const { credHash, log } = require("./common");

async function run(ctx) {
  const rows = [];
  const { n, warmup } = ctx.opts;
  for (const adapterId of ctx.adapterIds) {
    log(ctx, `[resolve] ${adapterId}`);
    // R4 queries k2, the delegate the lifecycle's rotation installed (review 02, H-7;
    // it used to query actors.delegateKey, which was never a delegate of the vehicle).
    // `answer` records what the read returned, so a row cannot silently measure the
    // negative path: ERC-721 answers false because the later transfers clear the
    // token approval (ERC-721 semantics), ERC-1056/725 delegates survive transfers.
    const { adapter, handle, delegateKey } = await runLifecycle(ctx, adapterId, "resolve-setup");
    const c = credHash(ctx, adapterId, "lifecycle", "reg2");
    const rd = async (op, fn, answerOf) => {
      if (!adapter.supports(op)) { rows.push({ adapter: adapterId, scenario: "resolve", op, supported: false, reason: adapter.unsupported[op] }); return; }
      const row = await ctx.collector.repeatRead({ adapter: adapterId, scenario: "resolve", op }, fn, { n, warmup });
      const { latencySamples, ...rest } = row;
      const extra = answerOf ? { answer: answerOf(await fn()) } : {};
      rows.push({ ...rest, ...extra, supported: true, latencySamples });
      log(ctx, `${op.padEnd(22)} rpc=${row.readRpcCalls} bytes=${row.readBytes} med=${row.latency.median}ms p95=${row.latency.p95}ms${answerOf ? " answer=" + extra.answer : ""}`);
    };
    await rd("R3_resolve_document", () => adapter.resolveDocument(handle));
    await rd("R1_resolve_owner", () => adapter.resolveOwner(handle), (x) => x);
    await rd("R4_verify_delegate", () => adapter.verifyDelegate(handle, delegateKey), (x) => x);
    await rd("V6_status_check", () => adapter.statusCheck(handle, c), (x) => x);
  }
  return rows;
}

module.exports = { run };
