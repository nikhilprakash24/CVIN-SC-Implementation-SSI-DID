"use strict";
// S1 — L1 baseline: every catalogue op on fresh state, 1 exact + warmup + N latency samples.
const { OPERATIONS } = require("../lib/operations");
const { freshAdapter, credHash, freshKey, freshOwner, freshIssuer, log } = require("./common");

async function run(ctx) {
  const rows = [];
  const { n, warmup } = ctx.opts;
  for (const adapterId of ctx.adapterIds) {
    log(ctx, `[crud] ${adapterId}`);
    const { adapter, actors, deployRows } = await freshAdapter(ctx, adapterId, "crud");
    const P = ctx.payloads;
    let vi = 0;
    const vehicle = () => ctx.dataset[vi++];

    // Credential ops (V1/V3/V5/V6) get a FRESH issuer per iteration, created and
    // key-anchored in an unmeasured precondition (common.freshIssuer). A shared
    // issuer accumulated keys/attributes across iterations, which made ERC-725 V5
    // (O(keys) removeKey) and ERC-1056 V6 read bytes depend on N (review 02, H-1).

    const tx = async (opId, iteration) => {
      if (!adapter.supports(opId)) {
        rows.push({ adapter: adapterId, scenario: "crud", op: opId, kind: "tx", supported: false, reason: adapter.unsupported[opId] });
        return;
      }
      const row = await ctx.collector.repeatTx({ adapter: adapterId, scenario: "crud", op: opId }, iteration, { n, warmup });
      row.supported = true;
      rows.push(row);
      log(ctx, `${opId.padEnd(28)} gas=${row.gasUsed} txs=${row.txCount} sstore=${row.sstoreCount} z2nz=${row.zeroToNonzeroSstores} log=${row.logBytes}B  lat.med=${row.latency.median}ms`);
    };

    const setupIdentity = async () => {
      const r = await adapter.createIdentityWithAttributes(vehicle(), await freshOwner(ctx));
      await r.txs.at(-1).wait();
      return r.result;
    };

    await tx("C1_create_identity", async () => { const o = await freshOwner(ctx); return { fn: () => adapter.createIdentity(vehicle(), o) }; });
    await tx("C2_create_with_attributes", async () => { const o = await freshOwner(ctx); return { fn: () => adapter.createIdentityWithAttributes(vehicle(), o) }; });
    // ERC-1155 re-binds the BIRTH_CERT to the receiver, who may hold none (K-13): such
    // adapters declare freshReceiverPerIteration; all others keep the fixed receiver.
    const receiver = async () => (adapter.freshReceiverPerIteration ? freshOwner(ctx) : actors.newOwner);
    await tx("U1_rotate_controller", async () => { const h = await setupIdentity(); const to = await receiver(); return { fn: () => adapter.rotateController(h, to) }; });
    await tx("U2_add_delegate", async () => { const h = await setupIdentity(); const k = freshKey(ctx); return { fn: () => adapter.addDelegate(h, k, P.ttlSeconds) }; });
    await tx("U3_set_attribute", async () => { const h = await setupIdentity(); return { fn: () => adapter.setAttribute(h, P.attributeName, P.attributeValue) }; });
    await tx("U4_transfer_vehicle", async () => { const h = await setupIdentity(); const to = await receiver(); return { fn: () => adapter.transferVehicle(h, to) }; });
    await tx("U5_meta_tx", async () => { const h = await setupIdentity(); return { fn: () => adapter.metaTxSetAttribute(h, P.attributeName, P.attributeValue, actors.verifier) }; });
    await tx("D1_revoke_delegate", async () => {
      const h = await setupIdentity(); const k = freshKey(ctx);
      await (await adapter.addDelegate(h, k, P.ttlSeconds)).txs.at(-1).wait();
      return { fn: () => adapter.revokeDelegate(h, k) };
    });
    await tx("D2_revoke_attribute", async () => {
      const h = await setupIdentity();
      await (await adapter.setAttribute(h, P.attributeName, P.attributeValue)).txs.at(-1).wait();
      return { fn: () => adapter.revokeAttribute(h, P.attributeName) };
    });
    await tx("D3_deactivate_identity", async () => { const h = await setupIdentity(); return { fn: () => adapter.deactivate(h) }; });
    await tx("V1_issuer_key_anchor", async () => {
      const iss = await freshIssuer(ctx, adapter); const k = freshKey(ctx);
      return { fn: () => adapter.anchorIssuerKey(iss, k) };
    });
    await tx("V3_anchor_status", async (i) => {
      const h = await setupIdentity(); const iss = await freshIssuer(ctx, adapter);
      return { fn: () => adapter.anchorStatus(h, credHash(ctx, adapterId, "V3", i), iss) };
    });
    await tx("V5_revoke_credential", async (i) => {
      const h = await setupIdentity(); const iss = await freshIssuer(ctx, adapter); const c = credHash(ctx, adapterId, "V5", i);
      await (await adapter.anchorStatus(h, c, iss)).txs.at(-1).wait();
      return { fn: () => adapter.revokeCredential(h, c, iss) };
    });

    // ---- reads on one identity with realistic state (own issuer: V6 is independent of N) ----
    const h = await setupIdentity();
    const k = freshKey(ctx);
    if (adapter.supports("U2_add_delegate")) await (await adapter.addDelegate(h, k, P.ttlSeconds)).txs.at(-1).wait();
    await (await adapter.setAttribute(h, P.attributeName, P.attributeValue)).txs.at(-1).wait();
    const readIssuer = await freshIssuer(ctx, adapter);
    const c = credHash(ctx, adapterId, "read");
    await (await adapter.anchorStatus(h, c, readIssuer)).txs.at(-1).wait();

    const rd = async (opId, fn) => {
      if (!adapter.supports(opId)) {
        rows.push({ adapter: adapterId, scenario: "crud", op: opId, kind: "read", supported: false, reason: adapter.unsupported[opId] });
        return;
      }
      const row = await ctx.collector.repeatRead({ adapter: adapterId, scenario: "crud", op: opId }, fn, { n, warmup });
      row.supported = true;
      rows.push(row);
      log(ctx, `${opId.padEnd(28)} rpc=${row.readRpcCalls} bytes=${row.readBytes} lat.med=${row.latency.median}ms p95=${row.latency.p95}ms`);
    };
    await rd("R1_resolve_owner", () => adapter.resolveOwner(h));
    await rd("R2_resolve_by_vin", () => adapter.resolveByVin(h.vin));
    await rd("R3_resolve_document", () => adapter.resolveDocument(h));
    await rd("R4_verify_delegate", () => adapter.verifyDelegate(h, k));
    await rd("V6_status_check", () => adapter.statusCheck(h, c, readIssuer));

    for (const d of deployRows) rows.push({ ...d, op: "DEPLOY_" + d.contract, supported: true });
  }
  // keep catalogue order
  const order = Object.fromEntries(OPERATIONS.map((o, i) => [o.id, i]));
  rows.sort((a, b) => (a.adapter < b.adapter ? -1 : a.adapter > b.adapter ? 1 : (order[a.op] ?? 99) - (order[b.op] ?? 99)));
  return rows;
}

module.exports = { run };
