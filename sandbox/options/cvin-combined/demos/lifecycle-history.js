'use strict';
/**
 * cvin-combined / lifecycle-history — the shared `changed` pointer: ERC-1056 events link via
 * previousChange, and since the D22 fix addClaim / removeClaim emit
 * DIDClaimChanged(identity, claimId, topic, removed, previousChange) next to ClaimAdded /
 * ClaimRemoved, so a did:ethr-style walk continues through every claim operation (formerly
 * the claim ops bumped `changed` without a linked event and the walk was cut there).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/lifecycle-history.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'lifecycle-history';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const eventsOf = (receipt, c, name) => receipt.logs.map((l) => { try { return c.interface.parseLog(l); } catch (_) { return null; } }).filter((e) => e && e.name === name);
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));

const CONTRACT = 'CVINCombinedIdentity';

async function walk(reg, id) {
  let block = await reg.changed(id);
  const seen = new Set();
  const events = [];
  let cutAt = null;
  while (block !== 0n && !seen.has(block)) {
    seen.add(block);
    const n = Number(block);
    const [o, d, a, c] = await Promise.all([
      reg.queryFilter(reg.filters.DIDOwnerChanged(id), n, n),
      reg.queryFilter(reg.filters.DIDDelegateChanged(id), n, n),
      reg.queryFilter(reg.filters.DIDAttributeChanged(id), n, n),
      reg.queryFilter(reg.filters.DIDClaimChanged(id), n, n), // the ERC-735 side's change marker (D22 fix)
    ]);
    let prev = block;
    for (const ev of [...o, ...d, ...a, ...c]) { events.push(`${ev.fragment.name}${ev.fragment.name === 'DIDClaimChanged' ? (ev.args.removed ? '(removed)' : '(added)') : ''}@${n}`); if (ev.args.previousChange < prev) prev = ev.args.previousChange; }
    if (prev === block) { cutAt = n; break; }
    block = prev;
  }
  return { events, cutAt };
}

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'shared hybrid registry');
  const id = vehicleOwner.address;
  const regAddr = await reg.getAddress();
  const issuer = ethers.Wallet.createRandom();
  const raw = (topic, data) => ethers.Signature.from(issuer.signingKey.sign(ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [regAddr, id, topic, data]))).serialized;

  assert((await view('changed-fresh', `${CONTRACT}.changed`, reg.changed(id), (v) => `changed == ${v}`)) === 0n, 'fresh');
  const r1 = await tx('h1-setAttribute', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, h('did/pub/secp256k1/veriKey'), ethers.hexlify(ethers.randomBytes(33)), 31536000), 'ERC-1056 event #1 (previousChange 0)');
  const r2 = await tx('h2-addDelegate', `${CONTRACT}.addDelegate`, reg.connect(vehicleOwner).addDelegate(id, h('sigAuth'), delegate.address, 3600), 'ERC-1056 event #2');
  const w1 = await walk(reg, id);
  out('walk-erc1056-only', `${CONTRACT}.changed`, true, 0, `walk: ${w1.events.join(', ')} -> complete (cut=${w1.cutAt})`);
  assert(w1.events.length === 2 && w1.cutAt === null, 'complete');
  const r3 = await tx('h3-addClaim', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 2, 1, issuer.address, raw(2, b('TYPE-APPROVAL')), b('TYPE-APPROVAL'), ''), 'ERC-735 side: ClaimAdded (no previousChange field) + DIDClaimChanged(identity, claimId, topic, removed=false, previousChange) and changed := this block');
  const cc = eventsOf(r3, reg, 'DIDClaimChanged');
  assert(cc.length === 1 && cc[0].args.removed === false && cc[0].args.topic === 2n && cc[0].args.previousChange === BigInt(r2.blockNumber), 'DIDClaimChanged links to the previous change (FIXED D22)');
  assert((await view('changed-after-claim', `${CONTRACT}.changed`, reg.changed(id), (v) => `changed == ${v} == addClaim block ${r3.blockNumber}: the pointer moved to a block that holds no classic ERC-1056 event, but DIDClaimChanged.previousChange == ${cc[0].args.previousChange} (the addDelegate block) keeps it on the list`)) === BigInt(r3.blockNumber), 'moved');
  const w2 = await walk(reg, id);
  out('walk-through-claim', `${CONTRACT}.changed`, true, 0, `walk from head: events=[${w2.events.join(', ')}] cut=${w2.cutAt}: FIXED (D22) — a did:ethr resolver following previousChange passes through the claim block and reaches all ${w2.events.length} events down to genesis; formerly the claim block carried no linked event, the walk found NOTHING and the S2 adapter had to range-scan`);
  assert(w2.events.length === 3 && w2.cutAt === null && w2.events[0] === `DIDClaimChanged(added)@${r3.blockNumber}`, 'walk reaches genesis through the claim op');
  const r4 = await tx('h4-changeOwner', `${CONTRACT}.changeOwner`, reg.connect(vehicleOwner).changeOwner(id, newOwner.address), 'ERC-1056 event #3: its previousChange points at the addClaim block …');
  const w3 = await walk(reg, id);
  out('walk-through-owner-change', `${CONTRACT}.changed`, true, 0, `walk: ${w3.events.join(', ')} -> cut=${w3.cutAt}: … so the walk sees DIDOwnerChanged, follows previousChange into the claim block, and continues from DIDClaimChanged.previousChange to the earlier ERC-1056 events`);
  assert(w3.events.length === 4 && w3.cutAt === null, 'complete after owner change');
  const r5 = await tx('h5-removeClaim', `${CONTRACT}.removeClaim`, reg.connect(newOwner).removeClaim(id, ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer.address, 2])), 'removeClaim bumps changed and emits DIDClaimChanged(removed=true, previousChange) next to ClaimRemoved');
  assert((await reg.changed(id)) === BigInt(r5.blockNumber), 'moved again');
  const cr = eventsOf(r5, reg, 'DIDClaimChanged');
  assert(cr.length === 1 && cr[0].args.removed === true && cr[0].args.previousChange === BigInt(r4.blockNumber), 'removeClaim links too');
  const w4 = await walk(reg, id);
  out('walk-full-history', `${CONTRACT}.changed`, true, 0, `walk after removeClaim: ${w4.events.join(', ')} -> ${w4.events.length} events, no gap (blocks ${[r1, r2, r3, r4, r5].map((r) => r.blockNumber).join('/')})`);
  assert(w4.events.length === 5 && w4.cutAt === null, 'full history by pointer');
  const claimLogs = [...await reg.queryFilter(reg.filters.ClaimAdded(null, id), 0, 'latest'), ...await reg.queryFilter(reg.filters.ClaimRemoved(null, id), 0, 'latest')];
  out('claim-events-indexed-by-identity', `${CONTRACT}.getClaimIdsByTopic`, true, 0, `ClaimAdded/ClaimRemoved ARE indexed by identity (${claimLogs.length} found by filter) and still carry no previousChange themselves; the D22 DIDClaimChanged marker is what links them into the one list, so a hybrid resolver walks one chain and reads the ERC-735 payload from the sibling ClaimAdded/ClaimRemoved log in the same block`);
  assert(claimLogs.length === 2, 'claim logs');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(regAddr);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve', 'adapter.resolve', true, 0, `adapter.resolve reconstructs the ${doc.meta.events} ERC-1056 events and ownerHistory=${doc.meta.ownerHistory.length} (blocks ${[r1, r2, r4].map((r) => r.blockNumber).join('/')}); its pre-fix range-scan fallback is now redundant`);
  assert(doc.meta.events === 3 && doc.meta.ownerHistory.length === 1, 'adapter resolves');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
