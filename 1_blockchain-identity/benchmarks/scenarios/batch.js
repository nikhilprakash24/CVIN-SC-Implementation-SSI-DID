"use strict";
// S2 — L4: cost of creating k identities in one go. Substrates with a native
// batch primitive expose adapter.createBatch(vehicles, owner); the three
// substrates on trunk have none, so they are measured as k sequential txs
// (mode = "sequential") to give a comparable "cost of 100" column.
const { freshAdapter, freshOwner, log } = require("./common");

const SIZES = [1, 10, 100];

async function run(ctx) {
  const rows = [];
  for (const adapterId of ctx.adapterIds) {
    for (const k of SIZES) {
      const { adapter, actors } = await freshAdapter(ctx, adapterId, "batch");
      const vehicles = ctx.dataset.slice(0, k);
      const owners = [];
      for (let i = 0; i < k; i++) owners.push(await freshOwner(ctx));
      const native = typeof adapter.createBatch === "function";
      const row = await ctx.collector.measureTx(
        { adapter: adapterId, scenario: "batch", op: "C1_create_identity", batchSize: k, mode: native ? "native" : "sequential" },
        async () => {
          if (native) return adapter.createBatch(vehicles, owners);
          const txs = [];
          for (let i = 0; i < k; i++) txs.push(...(await adapter.createIdentity(vehicles[i], owners[i])).txs);
          return { txs };
        }
      );
      const { txs, result, ...rest } = row;
      rows.push({ ...rest, gasPerItem: Math.round(row.gasUsed / k), latencyPerItemMs: row.latencyMs / k });
      log(ctx, `[batch] ${adapterId} k=${k} mode=${rest.mode} gas=${row.gasUsed} per-item=${Math.round(row.gasUsed / k)}`);
    }
  }
  return rows;
}

module.exports = { run, SIZES };
