'use strict';
/**
 * erc-1056-vehicle / lifecycle-history — changed / lastChanged and the previousChange linked
 * list; DIDRevoked carries no previousChange, so revocation CUTS the list and a resolver must
 * fall back to a range scan. nonce is declared but never consumed.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/lifecycle-history.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
const FAMILY = 'lifecycle-history';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));

async function walk(registry, id) {
  const head = await registry.changed(id);
  const seen = new Set();
  const events = [];
  let block = head;
  let cut = false;
  while (block !== 0n && !seen.has(block)) {
    seen.add(block);
    const n = Number(block);
    const [o, d, a, r] = await Promise.all([
      registry.queryFilter(registry.filters.DIDOwnerChanged(id), n, n),
      registry.queryFilter(registry.filters.DIDDelegateChanged(id), n, n),
      registry.queryFilter(registry.filters.DIDAttributeChanged(id), n, n),
      registry.queryFilter(registry.filters.DIDRevoked(id), n, n),
    ]);
    let prev = block;
    for (const ev of [...o, ...d, ...a]) { events.push(ev.fragment.name + '@' + n); if (ev.args.previousChange < prev) prev = ev.args.previousChange; }
    for (const ev of r) events.push(ev.fragment.name + '@' + n);
    if (prev === block) { cut = r.length > 0; break; }
    block = prev;
  }
  return { head, events, cut, stoppedAt: block };
}

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('ERC1056Registry', deployer)).deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared registry');
  const id = vehicleOwner.address;

  assert((await view('nonce-unused', 'ERC1056Registry.nonce', registry.nonce(id), (v) => `nonce[id] == ${v}: declared for meta-transactions but no *Signed function exists, so it is never incremented (dead state)`)) === 0n, 'nonce 0');
  const r1 = await tx('op1-registerVehicle', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, '0x04' + 'ab'.repeat(64)), 'history entry 1');
  const r2 = await tx('op2-addDelegate', 'ERC1056Registry.addDelegate', registry.connect(vehicleOwner).addDelegate(id, h('sigAuth'), delegate.address, 86400), 'history entry 2');
  const r3 = await tx('op3-setAttribute', 'ERC1056Registry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, h('did/svc/telematics'), b('mqtts://v2x.example'), 86400), 'history entry 3');
  const r4 = await tx('op4-changeOwner', 'ERC1056Registry.changeOwner', registry.connect(vehicleOwner).changeOwner(id, newOwner.address), 'history entry 4');
  const c = await view('changed', 'ERC1056Registry.changed', registry.changed(id), (v) => `changed == ${v} (block of op4)`);
  assert(c === BigInt(r4.blockNumber), 'head');
  assert((await view('lastChanged', 'ERC1056Registry.lastChanged', registry.lastChanged(id), (v) => `lastChanged == ${v} (MEASURED under #21/#29 as the history read; alias of changed)`)) === c, 'alias');
  const w1 = await walk(registry, id);
  out('walk-before-revoke', 'ERC1056Registry.changed', true, 0, `linked-list walk: ${w1.events.join(', ')} -> stopped at ${w1.stoppedAt} (complete, ${w1.events.length} events, blocks ${[r1, r2, r3, r4].map((r) => r.blockNumber).join('/')})`);
  assert(w1.events.length === 4 && w1.stoppedAt === 0n && !w1.cut, 'complete chain');

  const r5 = await tx('op5-revokeIdentity', 'ERC1056Registry.revokeIdentity', registry.connect(newOwner).revokeIdentity(id), 'history entry 5: DIDRevoked(identity, revokedAt) — NOTE: this event has no previousChange field');
  assert((await registry.changed(id)) === BigInt(r5.blockNumber), 'changed moved to revoke block');
  const w2 = await walk(registry, id);
  out('walk-after-revoke-CUT', 'ERC1056Registry.changed', true, 0, `walk from the new head: ${w2.events.join(', ')} -> cut=${w2.cut}: POTENTIAL DEFECT — changed now points at a block whose only event (DIDRevoked) carries no previousChange, so the did:ethr linked list is severed and the ${w1.events.length} earlier events are unreachable by pointer-walking; a resolver must fall back to a full range scan (the S2 adapter does exactly that)`);
  assert(w2.cut === true && w2.events.length === 1, 'chain cut');
  const scan = await registry.queryFilter(registry.filters.DIDAttributeChanged(id), 0, 'latest');
  out('fallback-range-scan', 'ERC1056Registry.changed', true, 0, `fallback scan of DIDAttributeChanged(id) over the whole chain finds ${scan.length} events — O(chain) instead of O(#changes)`);
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(await registry.getAddress());
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-after-cut', 'adapter.resolve', true, 0, `adapter.resolve (with its DIDRevoked fallback) still reconstructs events=${doc.meta.events}, revoked=${doc.status.revoked}, controller=${doc.controller.slice(0, 10)}…`);
  assert(doc.meta.events === 5 && doc.status.revoked === true, 'adapter fallback works');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
