"use strict";
// S4 — L2: MOBI VID I + II event sequence for one vehicle (framework §4.4).
const { freshAdapter, credHash, freshKey, log } = require("./common");

const FLEETS = [1, 1000, 1000000];

/** Returns the event list executed; each event: {n, event, op, actor, fn}. */
function sequence(ctx, adapter, actors, state) {
  const P = ctx.payloads;
  const v = ctx.dataset[0];
  const c = (tag) => credHash(ctx, adapter.constructor.id, "lifecycle", tag);
  const ev = [];
  ev.push({ n: 1, event: "VID-I birth certificate", op: "C2_create_with_attributes", actor: "manufacturer",
    fn: async () => { const r = await adapter.createIdentityWithAttributes(v, actors.vehicleOwner); state.h = r.result; return r; } });
  ev.push({ n: 2, event: "Issuer key anchor", op: "V1_issuer_key_anchor", actor: "issuer",
    fn: () => adapter.anchorIssuerKey(actors.issuer, actors.delegateKey) });
  ev.push({ n: 3, event: "Registration credential anchored", op: "V3_anchor_status", actor: "issuer", fn: () => adapter.anchorStatus(state.h, c("reg1")) });
  ev.push({ n: 4, event: "Insurance credential anchored", op: "V3_anchor_status", actor: "issuer", fn: () => adapter.anchorStatus(state.h, c("ins1")) });
  ev.push({ n: 5, event: "Service endpoint published", op: "U3_set_attribute", actor: "owner", fn: () => adapter.setAttribute(state.h, P.attributeName, P.attributeValue) });
  for (let i = 0; i < 5; i++) {
    ev.push({ n: 6 + i, event: `Service record ${i + 1}`, op: "U3_set_attribute", actor: "serviceCenter", fn: () => adapter.setAttribute(state.h, "svc/record/" + i, P.serviceRecordURI) });
  }
  // Review 02, H-2: the delegate that the rotation retires is added as its own
  // measured event (it was an unmeasured precondition), and the rotation uses the
  // adapter's rotateDelegate (ERC-721: one approve(k2), which replaces k1).
  ev.push({ n: 11, event: "Delegate key added (k1)", op: "U2_add_delegate", actor: "owner",
    fn: () => adapter.addDelegate(state.h, state.k1, P.ttlSeconds) });
  ev.push({ n: 12, event: "Key rotation (k1 to k2)", op: "rotate_delegate (U2+D1)", actor: "owner",
    fn: () => adapter.rotateDelegate(state.h, state.k1, state.k2, P.ttlSeconds) });
  ev.push({ n: 13, event: "Ownership transfer (resale)", op: "U4_transfer_vehicle", actor: "owner→newOwner", fn: () => adapter.transferVehicle(state.h, actors.newOwner) });
  ev.push({ n: 14, event: "Re-registration credential", op: "V3_anchor_status", actor: "issuer", fn: () => adapter.anchorStatus(state.h, c("reg2")) });
  ev.push({ n: 15, event: "Credential revocation (old insurance)", op: "V5_revoke_credential", actor: "issuer", fn: () => adapter.revokeCredential(state.h, c("ins1")) });
  ev.push({ n: 16, event: "Second ownership transfer", op: "U4_transfer_vehicle", actor: "newOwner→thirdOwner", fn: () => adapter.transferVehicle(state.h, actors.thirdOwner) });
  ev.push({ n: 17, event: "End-of-life deactivation", op: "D3_deactivate_identity", actor: "admin/owner", fn: () => adapter.deactivate(state.h) });
  return ev;
}

/**
 * Execute the lifecycle on an adapter.
 * Returns {adapter, actors, events, handle, deployRows, delegateKey}, where
 * `delegateKey` is k2, the key the rotation installed (used by resolve R4, H-7).
 */
async function runLifecycle(ctx, adapterId, scenario = "lifecycle") {
  const { adapter, actors, deployRows } = await freshAdapter(ctx, adapterId, scenario);
  const state = { k1: freshKey(ctx), k2: freshKey(ctx) };
  const events = [];
  for (const e of sequence(ctx, adapter, actors, state)) {
    const row = await ctx.collector.measureTx({ adapter: adapterId, scenario, op: e.op, event: e.event, eventNo: e.n, actor: e.actor }, e.fn);
    events.push(row);
    log(ctx, `#${String(e.n).padStart(2)} ${e.event.padEnd(38)} gas=${row.gasUsed} txs=${row.txCount}`);
  }
  return { adapter, actors, events, handle: state.h, deployRows, delegateKey: state.k2 };
}

async function run(ctx) {
  const out = [];
  for (const adapterId of ctx.adapterIds) {
    log(ctx, `[lifecycle] ${adapterId}`);
    const { events, deployRows } = await runLifecycle(ctx, adapterId);
    const lifetimeGas = events.reduce((a, e) => a + e.gasUsed, 0);
    const deployGas = deployRows.reduce((a, d) => a + d.gasUsed, 0);
    const perIdentityDeployGas = events.filter((e) => e.deploysContract).reduce((a, e) => a + e.txs.filter((t) => t.isCreate).reduce((s, t) => s + t.gasUsed, 0), 0);
    out.push({
      adapter: adapterId,
      events: events.map((e) => ({ eventNo: e.eventNo, event: e.event, op: e.op, actor: e.actor, gasUsed: e.gasUsed, txCount: e.txCount, logBytes: e.logBytes, sstoreCount: e.sstoreCount, zeroToNonzeroSstores: e.zeroToNonzeroSstores, latencyMs: e.latencyMs })),
      lifetimeGas,
      lifetimeTxCount: events.reduce((a, e) => a + e.txCount, 0),
      lifetimeLogBytes: events.reduce((a, e) => a + e.logBytes, 0),
      // Σ SSTOREs that wrote a zero slot to non-zero. NOT net state left behind:
      // a slot later cleared (e.g. a revoked key) is still counted (review 02, H-8).
      lifetimeZeroToNonzeroSstores: events.reduce((a, e) => a + (e.zeroToNonzeroSstores || 0), 0),
      sharedDeployGas: deployGas,
      perIdentityDeployGas,
      apportioned: Object.fromEntries(FLEETS.map((f) => [f, Math.round(lifetimeGas + deployGas / f)])),
    });
    log(ctx, `lifetime=${lifetimeGas} sharedDeploy=${deployGas} perIdentityDeploy=${perIdentityDeployGas}`);
  }
  return out;
}

module.exports = { run, runLifecycle, FLEETS };
