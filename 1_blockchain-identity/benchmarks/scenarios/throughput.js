"use strict";
// S5 — L5: single-node throughput for the U3 op.
// Hardhat automine cannot queue nonces, so the burst is measured as
// queue (automine off) → mine: `sendSec` is the node's accept rate,
// `mineSec` the EVM execution rate for the whole burst, tx/s over both.
const { freshAdapter, log } = require("./common");
const { summarize } = require("../lib/stats");

async function run(ctx) {
  const rows = [];
  const { burstSenders, burstPerSender, bursts } = ctx.opts;
  const np = ctx.hre.network.provider;
  for (const adapterId of ctx.adapterIds) {
    log(ctx, `[throughput] ${adapterId}`);
    const { adapter, actors } = await freshAdapter(ctx, adapterId, "throughput");
    const senders = actors.all.slice(10, 10 + burstSenders);
    const entries = await adapter.prepareThroughputSenders(senders);
    const burstRows = [];
    for (let b = 0; b < bursts; b++) {
      // Nonces are keyed by sender address: substrates with a single writing
      // authority (LSP8) share one sender across entries.
      const nonceOf = new Map();
      for (const e of entries) if (!nonceOf.has(e.sender.address)) nonceOf.set(e.sender.address, await ctx.ethers.provider.getTransactionCount(e.sender.address, "latest"));
      const nextNonce = (addr) => { const n = nonceOf.get(addr); nonceOf.set(addr, n + 1); return n; };
      await np.send("evm_setAutomine", [false]);
      const t0 = process.hrtime.bigint();
      // Fixed gas/fee fields so the client makes no estimateGas/feeData round-trips:
      // the queue phase then measures the node's accept rate, not ethers' populate path.
      const fees = { gasLimit: 500000n, maxFeePerGas: 100_000_000_000n, maxPriorityFeePerGas: 1_000_000_000n, type: 2 };
      const txs = [];
      for (let i = 0; i < burstPerSender; i++) {
        for (let s = 0; s < entries.length; s++) txs.push(await adapter.throughputOp(entries[s], b * burstPerSender + i, { ...fees, nonce: nextNonce(entries[s].sender.address) }));
      }
      const t1 = process.hrtime.bigint();
      let blocks = 0;
      while ((await np.send("eth_getBlockTransactionCountByNumber", ["pending"])) !== "0x0") { await np.send("evm_mine", []); blocks++; }
      const t2 = process.hrtime.bigint();
      await np.send("evm_setAutomine", [true]);
      const receipts = await Promise.all(txs.map((t) => ctx.ethers.provider.getTransactionReceipt(t.hash)));
      const seconds = Number(t2 - t0) / 1e9;
      const gas = receipts.reduce((a, r) => a + Number(r.gasUsed), 0);
      burstRows.push({ burst: b, txCount: txs.length, sendSec: Number(t1 - t0) / 1e9, mineSec: Number(t2 - t1) / 1e9, seconds, txPerSec: txs.length / seconds, gasPerSec: gas / seconds, gasTotal: gas, blocks });
      log(ctx, `burst ${b}: ${txs.length} tx queued in ${(Number(t1 - t0) / 1e9).toFixed(3)}s, mined in ${(Number(t2 - t1) / 1e9).toFixed(3)}s (${blocks} block) → ${(txs.length / seconds).toFixed(1)} tx/s`);
    }
    rows.push({
      adapter: adapterId, scenario: "throughput", op: "U3_set_attribute", senders: entries.length, txPerBurst: burstSenders * burstPerSender,
      bursts: burstRows,
      txPerSec: summarize(burstRows.map((r) => r.txPerSec)),
      gasPerSec: summarize(burstRows.map((r) => r.gasPerSec)),
      mineTxPerSec: summarize(burstRows.map((r) => r.txCount / r.mineSec)),
      note: "single in-process Hardhat node; queue then mine; upper bound on execution, not a public-chain figure",
    });
  }
  return rows;
}

module.exports = { run };
