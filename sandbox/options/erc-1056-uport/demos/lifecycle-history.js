'use strict';
/**
 * erc-1056-uport / lifecycle-history — the changed[] linked list: every mutation emits an event
 * carrying previousChange, so a resolver walks changed -> previousChange -> … -> 0 and never
 * scans the whole log. Wrapper-only state (VIN mapping) is NOT in that history.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/lifecycle-history.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
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

const VIN = 'WVWZZZ1KZBW123456';
const CAR = ['Volkswagen', 'Golf', 2011, 'Blue', 'CBZB-2011-0092', 1293840000, 'L0'];
const ONE_YEAR = 31536000;

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared did:ethr registry');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, (await wrapper.deploymentTransaction().wait()).gasUsed, 'VIN wrapper');
  const id = vehicleOwner.address;

  await tx('createVehicleDID', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN, id, ...CAR), 'wrapper creation');
  assert((await view('changed-after-wrapper-create', 'EthereumDIDRegistry.changed', registry.changed(id), (v) => `changed == ${v}: wrapper creation leaves no trace in the ERC-1056 history (VehicleDIDCreated is a wrapper event outside the linked list)`)) === 0n, 'changed 0');

  const r1 = await tx('op1-setAttribute', 'EthereumDIDRegistry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, h('did/pub/secp256k1/veriKey'), ethers.hexlify(ethers.randomBytes(33)), ONE_YEAR), 'history entry 1 (previousChange = 0)');
  const r2 = await tx('op2-addDelegate', 'EthereumDIDRegistry.addDelegate', registry.connect(vehicleOwner).addDelegate(id, h('sigAuth'), delegate.address, ONE_YEAR), 'history entry 2');
  const r3 = await tx('op3-changeOwner', 'EthereumDIDRegistry.changeOwner', registry.connect(vehicleOwner).changeOwner(id, newOwner.address), 'history entry 3 (vehicle sale)');
  const r4 = await tx('op4-setAttribute-by-new-owner', 'EthereumDIDRegistry.setAttribute', registry.connect(newOwner).setAttribute(id, h('did/svc/telematics'), b('https://telematics.example/' + VIN), ONE_YEAR), 'history entry 4, written by the new controller');
  const r5 = await tx('op5-revokeDelegate', 'EthereumDIDRegistry.revokeDelegate', registry.connect(newOwner).revokeDelegate(id, h('sigAuth'), delegate.address), 'history entry 5: the new owner removes the seller\'s delegate');
  const blocks = [r1, r2, r3, r4, r5].map((r) => BigInt(r.blockNumber));

  const head = await view('changed-head', 'EthereumDIDRegistry.changed', registry.changed(id), (v) => `changed == ${v} == block of the last mutation (head of the linked list)`);
  assert(head === blocks[4], 'head is last block');

  // walk the list exactly like a did:ethr resolver
  const walk = [];
  let block = head;
  const seen = new Set();
  while (block !== 0n && !seen.has(block)) {
    seen.add(block);
    const n = Number(block);
    const [o, d, a] = await Promise.all([
      registry.queryFilter(registry.filters.DIDOwnerChanged(id), n, n),
      registry.queryFilter(registry.filters.DIDDelegateChanged(id), n, n),
      registry.queryFilter(registry.filters.DIDAttributeChanged(id), n, n),
    ]);
    const evs = [...o, ...d, ...a];
    assert(evs.length >= 1, `block ${n} has an event`);
    let prev = block;
    for (const ev of evs) { if (ev.args.previousChange < prev) prev = ev.args.previousChange; walk.push({ block: n, name: ev.fragment.name, previousChange: Number(ev.args.previousChange) }); }
    block = prev;
  }
  out('walk-linked-list', 'EthereumDIDRegistry.changed', true, 0, `walked ${walk.length} events via previousChange: ${walk.map((w) => `${w.name}@${w.block}->${w.previousChange}`).join(', ')}; terminated at 0 — O(#changes) log queries, no full-chain scan (resolution is not measured by the comparison)`);
  assert(walk.length === 5 && block === 0n, 'five linked events ending at 0');
  assert(walk.map((w) => w.block).join() === blocks.slice().reverse().map(Number).join(), 'blocks in reverse order');
  const names = walk.map((w) => w.name);
  assert(names.includes('DIDOwnerChanged') && names.includes('DIDDelegateChanged') && names.includes('DIDAttributeChanged'), 'all three event kinds');

  const all = await registry.queryFilter(registry.filters.DIDAttributeChanged(id), 0, 'latest');
  out('full-scan-comparison', 'EthereumDIDRegistry.changed', true, 0, `a naive full scan of DIDAttributeChanged(identity) returns ${all.length} events; the linked list gives the same set without knowing the range — the ownership history (${walk.filter((w) => w.name === 'DIDOwnerChanged').length} DIDOwnerChanged) is part of the same chain`);
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach({ registry: await registry.getAddress(), wrapper: await wrapper.getAddress() });
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-uses-walk', 'adapter.resolve', true, 0, `adapter.resolve replays the same walk: events=${doc.meta.events}, ownerHistory=${doc.meta.ownerHistory.length}, controller=${doc.controller.slice(0, 10)}…`);
  assert(doc.meta.events === 5 && doc.controller === newOwner.address, 'adapter walk matches');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
