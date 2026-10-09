'use strict';
/**
 * cvin-combined / lifecycle-history — the `changed` pointer is the ERC-1056 DID-event chain head
 * ONLY: DIDOwnerChanged / DIDDelegateChanged / DIDAttributeChanged link via previousChange, and
 * since the merge (K-6 / decision M-A, 2026-10-06) addClaim / removeClaim do NOT advance
 * `changed`, so a did:ethr-style walk never visits a claim block and is never cut by one
 * (formerly — defect D22 — the claim ops bumped `changed` without a linked event; our D22 fix
 * kept the bump and added DIDClaimChanged as a link, the merged K-6 design drops the bump).
 * DIDClaimChanged(identity, claimId, topic, removed, previousChange) is still emitted next to
 * ClaimAdded / ClaimRemoved: its last argument is the chain head AT THE TIME of the claim op,
 * for correlation with the DID history, not a pointer the walk follows. Claim history is found
 * by its own identity-indexed filter.
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

/** A plain did:ethr resolver walk: the three ERC-1056 events only (what ethr-did-resolver does). */
async function walk(reg, id) {
  let block = await reg.changed(id);
  const seen = new Set();
  const events = [];
  const blocks = [];
  let cutAt = null;
  while (block !== 0n && !seen.has(block)) {
    seen.add(block);
    const n = Number(block);
    blocks.push(n);
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
  return { events, blocks, cutAt };
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
  const r3 = await tx('h3-addClaim', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 2, 1, issuer.address, raw(2, b('TYPE-APPROVAL')), b('TYPE-APPROVAL'), ''), 'ERC-735 side: ClaimAdded (no previousChange field) + DIDClaimChanged(identity, claimId, topic, removed=false, previousChange = current chain head); changed is NOT advanced');
  const cc = eventsOf(r3, reg, 'DIDClaimChanged');
  assert(cc.length === 1 && cc[0].args.removed === false && cc[0].args.topic === 2n && cc[0].args.previousChange === BigInt(r2.blockNumber), 'DIDClaimChanged carries the chain head at the time (the addDelegate block)');
  assert((await view('changed-unmoved-by-claim', `${CONTRACT}.changed`, reg.changed(id), (v) => `changed == ${v} == addDelegate block ${r2.blockNumber}, not the addClaim block ${r3.blockNumber}: FIXED (K-6 / M-A) — the pointer stays on the last DID event; DIDClaimChanged.previousChange == ${cc[0].args.previousChange} records which DID-document state the claim was added under`)) === BigInt(r2.blockNumber), 'not moved');
  const w2 = await walk(reg, id);
  out('walk-skips-claim', `${CONTRACT}.changed`, true, 0, `walk from head: events=[${w2.events.join(', ')}] blocks=[${w2.blocks.join(',')}] cut=${w2.cutAt}: FIXED (K-6 / M-A) — a did:ethr resolver following previousChange never lands on the claim block ${r3.blockNumber} and is not cut by it (formerly — D22 — the claim op moved the pointer to a block with no linked event and the walk found NOTHING)`);
  assert(w2.events.length === 2 && w2.cutAt === null && !w2.blocks.includes(r3.blockNumber), 'walk unchanged by the claim op');
  const r4 = await tx('h4-changeOwner', `${CONTRACT}.changeOwner`, reg.connect(vehicleOwner).changeOwner(id, newOwner.address), 'ERC-1056 event #3: its previousChange points at the addDelegate block, skipping the claim block entirely');
  assert(eventsOf(r4, reg, 'DIDOwnerChanged')[0].args.previousChange === BigInt(r2.blockNumber), 'owner change links to the previous DID event');
  const w3 = await walk(reg, id);
  out('walk-after-owner-change', `${CONTRACT}.changed`, true, 0, `walk: ${w3.events.join(', ')} -> cut=${w3.cutAt}: DIDOwnerChanged.previousChange == ${r2.blockNumber} (addDelegate), so the three DID events form one unbroken list`);
  assert(w3.events.length === 3 && w3.cutAt === null, 'complete after owner change');
  const r5 = await tx('h5-removeClaim', `${CONTRACT}.removeClaim`, reg.connect(newOwner).removeClaim(id, ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer.address, 2])), 'removeClaim emits ClaimRemoved + DIDClaimChanged(removed=true, previousChange = current chain head) and leaves changed alone (K-6)');
  assert((await reg.changed(id)) === BigInt(r4.blockNumber), 'still not moved');
  const cr = eventsOf(r5, reg, 'DIDClaimChanged');
  assert(cr.length === 1 && cr[0].args.removed === true && cr[0].args.previousChange === BigInt(r4.blockNumber), 'removeClaim records the chain head at the time (the changeOwner block)');
  const w4 = await walk(reg, id);
  out('walk-full-history', `${CONTRACT}.changed`, true, 0, `walk after removeClaim: ${w4.events.join(', ')} -> ${w4.events.length} DID events, no gap, claim blocks ${r3.blockNumber}/${r5.blockNumber} never visited (DID blocks ${[r1, r2, r4].map((r) => r.blockNumber).join('/')})`);
  assert(w4.events.length === 3 && w4.cutAt === null && !w4.blocks.includes(r3.blockNumber) && !w4.blocks.includes(r5.blockNumber), 'full DID history by pointer, claim blocks skipped');
  const claimMarks = await reg.queryFilter(reg.filters.DIDClaimChanged(id), 0, 'latest');
  assert(claimMarks.length === 2 && claimMarks[0].args.removed === false && claimMarks[1].args.removed === true, 'claim markers');
  assert(claimMarks.map((e) => e.args.previousChange).every((p, i) => p === BigInt([r2, r4][i].blockNumber)), 'markers correlate to the DID chain head of their time');
  out('claim-history-own-filter', `${CONTRACT}.DIDClaimChanged`, true, 0, `claim history is found by its own identity-indexed filter: ${claimMarks.map((e) => `${e.args.removed ? 'removed' : 'added'}@${e.blockNumber}(head=${e.args.previousChange})`).join(', ')} — previousChange here is the DID chain head when the claim op happened (addDelegate block ${r2.blockNumber}, changeOwner block ${r4.blockNumber}), which tells a verifier under which controller/keys the claim was anchored or removed; it is not followed by the walk (M-A)`);
  const claimLogs = [...await reg.queryFilter(reg.filters.ClaimAdded(null, id), 0, 'latest'), ...await reg.queryFilter(reg.filters.ClaimRemoved(null, id), 0, 'latest')];
  out('claim-events-indexed-by-identity', `${CONTRACT}.getClaimIdsByTopic`, true, 0, `ClaimAdded/ClaimRemoved ARE indexed by identity (${claimLogs.length} found by filter) and carry no previousChange themselves; a hybrid resolver runs two filters — the DID walk and the claim filter — and merges them by block, instead of one chain through both halves`);
  assert(claimLogs.length === 2, 'claim logs');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(regAddr);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve', 'adapter.resolve', true, 0, `adapter.resolve reconstructs the ${doc.meta.events} ERC-1056 events and ownerHistory=${doc.meta.ownerHistory.length} (blocks ${[r1, r2, r4].map((r) => r.blockNumber).join('/')}) by the plain pointer walk; its range-scan fallback stays idle`);
  assert(doc.meta.events === 3 && doc.meta.ownerHistory.length === 1, 'adapter resolves');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
