"use strict";
// S3 — L3: marginal cost vs registry population N and per-identity history h.
const { freshAdapter, freshOwner, log } = require("./common");

async function run(ctx) {
  const rows = [];
  const Ns = ctx.opts.scaleN;
  const Hs = ctx.opts.scaleH;
  const P = ctx.payloads;

  for (const adapterId of ctx.adapterIds) {
    for (const N of Ns) {
      log(ctx, `[scale] ${adapterId} N=${N}`);
      const { adapter, actors } = await freshAdapter(ctx, adapterId, "scale");
      for (let i = 0; i < N; i++) {
        const r = await adapter.createIdentity(ctx.dataset[i], await freshOwner(ctx));
        await r.txs.at(-1).wait();
      }
      const tags = (op) => ({ adapter: adapterId, scenario: "scale", axis: "N", value: N, op });
      const v = ctx.dataset[N];
      const owner = await freshOwner(ctx);
      const c2 = await ctx.collector.measureTx(tags("C2_create_with_attributes"), () => adapter.createIdentityWithAttributes(v, owner));
      const h = c2.result;
      const u3 = await ctx.collector.measureTx(tags("U3_set_attribute"), () => adapter.setAttribute(h, P.attributeName, P.attributeValue));
      const u4 = await ctx.collector.measureTx(tags("U4_transfer_vehicle"), () => adapter.transferVehicle(h, actors.newOwner));
      const r3 = await ctx.collector.repeatRead(tags("R3_resolve_document"), () => adapter.resolveDocument(h), { n: 10, warmup: 2 });
      for (const r of [c2, u3, u4]) rows.push(pickTx(r));
      rows.push(pickRead(r3));
      log(ctx, `C2=${c2.gasUsed} U3=${u3.gasUsed} U4=${u4.gasUsed} R3.med=${r3.latency.median}ms rpc=${r3.readRpcCalls}`);
    }

    // history axis: one identity, h prior attribute writes + h prior transfers
    for (const H of Hs) {
      log(ctx, `[scale] ${adapterId} h=${H}`);
      const { adapter, actors } = await freshAdapter(ctx, adapterId, "scale");
      const owners = [await freshOwner(ctx), actors.newOwner, actors.thirdOwner];
      const r0 = await adapter.createIdentityWithAttributes(ctx.dataset[0], owners[0]);
      await r0.txs.at(-1).wait();
      const h = r0.result;
      for (let i = 0; i < H; i++) {
        await (await adapter.setAttribute(h, "svc/record/" + i, P.serviceRecordURI)).txs.at(-1).wait();
        await (await adapter.transferVehicle(h, owners[(i + 1) % owners.length])).txs.at(-1).wait();
      }
      const tags = (op) => ({ adapter: adapterId, scenario: "scale", axis: "h", value: H, op });
      const u3 = await ctx.collector.measureTx(tags("U3_set_attribute"), () => adapter.setAttribute(h, P.attributeName, P.attributeValue));
      const u4 = await ctx.collector.measureTx(tags("U4_transfer_vehicle"), () => adapter.transferVehicle(h, owners[(H + 1) % owners.length]));
      const r3 = await ctx.collector.repeatRead(tags("R3_resolve_document"), () => adapter.resolveDocument(h), { n: 10, warmup: 2 });
      rows.push(pickTx(u3), pickTx(u4), pickRead(r3));
      log(ctx, `U3=${u3.gasUsed} U4=${u4.gasUsed} R3.med=${r3.latency.median}ms rpc=${r3.readRpcCalls} bytes=${r3.readBytes}`);
    }
  }
  return rows;
}

function pickTx(r) {
  const { txs, result, ...rest } = r;
  return rest;
}
function pickRead(r) {
  const { latencySamples, ...rest } = r;
  return rest;
}

module.exports = { run };
