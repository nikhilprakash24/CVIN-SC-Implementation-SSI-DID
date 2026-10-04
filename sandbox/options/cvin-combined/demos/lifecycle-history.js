'use strict';
/**
 * cvin-combined / lifecycle-history — the shared `changed` pointer: ERC-1056 events link via
 * previousChange, but addClaim / removeClaim bump `changed` WITHOUT an ERC-1056 event, so a
 * did:ethr-style walk is cut at every claim operation.
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
    const [o, d, a] = await Promise.all([
      reg.queryFilter(reg.filters.DIDOwnerChanged(id), n, n),
      reg.queryFilter(reg.filters.DIDDelegateChanged(id), n, n),
      reg.queryFilter(reg.filters.DIDAttributeChanged(id), n, n),
    ]);
    let prev = block;
    for (const ev of [...o, ...d, ...a]) { events.push(`${ev.fragment.name}@${n}`); if (ev.args.previousChange < prev) prev = ev.args.previousChange; }
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
  const r3 = await tx('h3-addClaim', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 2, 1, issuer.address, raw(2, b('TYPE-APPROVAL')), b('TYPE-APPROVAL'), ''), 'ERC-735 side: ClaimAdded (NO previousChange field) and changed := this block');
  assert((await view('changed-after-claim', `${CONTRACT}.changed`, reg.changed(id), (v) => `changed == ${v} == addClaim block ${r3.blockNumber}: the pointer moved to a block that holds no ERC-1056 event`)) === BigInt(r3.blockNumber), 'moved');
  const w2 = await walk(reg, id);
  out('walk-cut-by-claim', `${CONTRACT}.changed`, true, 0, `walk from head: events=[${w2.events.join(', ')}] cut at block ${w2.cutAt}: POTENTIAL DEFECT — a did:ethr resolver following previousChange finds NOTHING; the ${w1.events.length} earlier ERC-1056 events are unreachable by pointer (the S2 adapter falls back to a range scan)`);
  assert(w2.events.length === 0 && w2.cutAt === r3.blockNumber, 'cut');
  const r4 = await tx('h4-changeOwner', `${CONTRACT}.changeOwner`, reg.connect(vehicleOwner).changeOwner(id, newOwner.address), 'ERC-1056 event #3: its previousChange points at the addClaim block …');
  const w3 = await walk(reg, id);
  out('walk-resumes-then-cuts', `${CONTRACT}.changed`, true, 0, `walk: ${w3.events.join(', ')} -> cut at ${w3.cutAt}: … so the walk sees DIDOwnerChanged, follows previousChange into the claim block, and stops there again`);
  assert(w3.events.length === 1 && w3.cutAt === r3.blockNumber, 'cut again');
  const r5 = await tx('h5-removeClaim', `${CONTRACT}.removeClaim`, reg.connect(newOwner).removeClaim(id, ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer.address, 2])), 'removeClaim also bumps changed without an ERC-1056 event');
  assert((await reg.changed(id)) === BigInt(r5.blockNumber), 'moved again');
  const claimLogs = [...await reg.queryFilter(reg.filters.ClaimAdded(null, id), 0, 'latest'), ...await reg.queryFilter(reg.filters.ClaimRemoved(null, id), 0, 'latest')];
  out('claim-events-indexed-by-identity', `${CONTRACT}.getClaimIdsByTopic`, true, 0, `ClaimAdded/ClaimRemoved ARE indexed by identity (${claimLogs.length} found by filter) but carry no previousChange: a hybrid resolver must merge two event families and cannot use one linked list — the thesis should state the resolver contract`);
  assert(claimLogs.length === 2, 'claim logs');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(regAddr);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-fallback', 'adapter.resolve', true, 0, `adapter.resolve reconstructs events=${doc.meta.events} ownerHistory=${doc.meta.ownerHistory.length} via its range-scan fallback (blocks ${[r1, r2, r4].map((r) => r.blockNumber).join('/')})`);
  assert(doc.meta.events === 3 && doc.meta.ownerHistory.length === 1, 'fallback');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
