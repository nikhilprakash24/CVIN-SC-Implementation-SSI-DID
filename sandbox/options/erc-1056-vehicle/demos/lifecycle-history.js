'use strict';
/**
 * erc-1056-vehicle / lifecycle-history — changed / lastChanged and the previousChange linked
 * list, walked through a revocation: since the D21 fix DIDRevoked carries previousChange like the
 * three ERC-1056 events, so the walk reaches genesis with no gap (formerly the list was CUT at the
 * revoke block and a resolver had to fall back to a range scan). nonce is declared but never consumed.
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
    // all four event kinds carry previousChange (DIDRevoked since the D21 fix), so one rule covers them
    for (const ev of [...o, ...d, ...a, ...r]) { events.push(ev.fragment.name + '@' + n); if (ev.args.previousChange < prev) prev = ev.args.previousChange; }
    if (prev === block) { cut = true; break; } // a block on the list whose events point nowhere earlier: the list is severed
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

  const r5 = await tx('op5-revokeIdentity', 'ERC1056Registry.revokeIdentity', registry.connect(newOwner).revokeIdentity(id), 'history entry 5: DIDRevoked(identity, revokedAt, previousChange) — the previousChange field was added by the D21 fix');
  assert((await registry.changed(id)) === BigInt(r5.blockNumber), 'changed moved to revoke block');
  const rev = (await registry.queryFilter(registry.filters.DIDRevoked(id), r5.blockNumber, r5.blockNumber))[0];
  assert(rev.args.previousChange === BigInt(r4.blockNumber), 'DIDRevoked.previousChange == block of op4');
  const w2 = await walk(registry, id);
  out('walk-after-revoke', 'ERC1056Registry.changed', true, 0, `walk from the new head: ${w2.events.join(', ')} -> stopped at ${w2.stoppedAt}, cut=${w2.cut}: FIXED (D21) — DIDRevoked.previousChange == ${rev.args.previousChange} (block of op4), so the did:ethr linked list continues through the revocation and all ${w2.events.length} events are reachable by pointer-walking from changed(); formerly DIDRevoked carried no previousChange and the walk found only the revoke block (the S2 adapter had to range-scan)`);
  assert(!w2.cut && w2.stoppedAt === 0n && w2.events.length === 5 && w2.events[0] === 'DIDRevoked@' + r5.blockNumber, 'walk reaches genesis through the revocation');
  const scan = await registry.queryFilter(registry.filters.DIDAttributeChanged(id), 0, 'latest');
  out('range-scan-cross-check', 'ERC1056Registry.changed', true, 0, `a full range scan of DIDAttributeChanged(id) finds ${scan.length} event(s), the same as the pointer walk — the O(chain) fallback is no longer needed for correctness`);
  assert(scan.length === w2.events.filter((e) => e.startsWith('DIDAttributeChanged')).length, 'scan agrees with walk');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(await registry.getAddress());
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-after-revoke', 'adapter.resolve', true, 0, `adapter.resolve reconstructs events=${doc.meta.events}, revoked=${doc.status.revoked}, controller=${doc.controller.slice(0, 10)}… (its pre-fix DIDRevoked fallback is now redundant but harmless)`);
  assert(doc.meta.events === 5 && doc.status.revoked === true, 'adapter resolves the full history');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
