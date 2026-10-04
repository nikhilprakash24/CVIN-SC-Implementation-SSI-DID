'use strict';
/**
 * erc-735 / lifecycle-history — the claim lifecycle as events: ClaimRequested + ClaimAdded on
 * first anchoring, ClaimChanged on re-add, ClaimRemoved (with the full claim) on removal,
 * OwnershipTransferred on sale; no changed pointer, so history = a log scan per identity.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/lifecycle-history.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-735';
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
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const utf8 = (x) => ethers.toUtf8String(x);

const CONTRACT = 'CVINVehicleClaimHolder';
const VIN = 'WVWZZZ1KZBW123456';

async function main() {
  const [, vehicleOwner, newOwner, , , , inspector] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy(VIN);
  const r0 = await c.deploymentTransaction().wait();
  out('deploy-identity', `${CONTRACT}.constructor`, true, r0.gasUsed, 'history entry 0: VehicleIdentityCreated + OwnershipTransferred(0, owner)');
  const id = await c.getAddress();
  const sign = (signer, topic, data) => signer.signMessage(ethers.getBytes(ethers.solidityPackedKeccak256(['address', 'uint256', 'bytes'], [id, topic, data])));
  const cid = ethers.solidityPackedKeccak256(['address', 'uint256'], [inspector.address, 3]);

  const d1 = b('APK:2024-03-01:PASS:odo=120000');
  const r1 = await tx('h1-addClaim', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(3, 1, inspector.address, await sign(inspector, 3, d1), d1, ''), 'first anchoring');
  assert(eventsOf(r1, c, 'ClaimRequested').length === 1 && eventsOf(r1, c, 'ClaimAdded').length === 1, 'requested+added');
  const d2 = b('APK:2025-03-05:PASS:odo=141500');
  const r2 = await tx('h2-addClaim-update', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(3, 1, inspector.address, await sign(inspector, 3, d2), d2, ''), 'yearly re-inspection: same (issuer, topic) -> update in place');
  const chg = eventsOf(r2, c, 'ClaimChanged');
  assert(chg.length === 1 && utf8(chg[0].args.data) === utf8(d2) && eventsOf(r2, c, 'ClaimAdded').length === 0, 'ClaimChanged only');
  out('ClaimChanged-decoded', `${CONTRACT}.addClaim`, true, 0, `ClaimChanged(claimId, topic=${chg[0].args.topic}, issuer, data="${utf8(chg[0].args.data)}"): the PREVIOUS value is not in the event — a verifier reconstructs the history by ordering ClaimAdded/ClaimChanged logs`);
  const r3 = await tx('h3-transferOwnership', `${CONTRACT}.transferOwnership`, c.connect(vehicleOwner).transferOwnership(newOwner.address), 'sale');
  const d3 = b('APK:2026-03-02:FAIL:brakes');
  const r4 = await tx('h4-addClaim-update-by-buyer', `${CONTRACT}.addClaim`, c.connect(newOwner).addClaim(3, 1, inspector.address, await sign(inspector, 3, d3), d3, ''), 'the new owner anchors the next (failed) inspection — the holder changed, the issuer did not');
  const r5 = await tx('h5-removeClaim', `${CONTRACT}.removeClaim`, c.connect(inspector).removeClaim(cid), 'issuer withdraws; ClaimRemoved carries the FULL last claim (signature, data, uri) so the log alone proves what was revoked');
  const rem = eventsOf(r5, c, 'ClaimRemoved')[0];
  assert(utf8(rem.args.data) === utf8(d3) && rem.args.signature.length === 132, 'full claim in ClaimRemoved');

  const added = await c.queryFilter(c.filters.ClaimAdded(), 0, 'latest');
  const changed = await c.queryFilter(c.filters.ClaimChanged(), 0, 'latest');
  const removed = await c.queryFilter(c.filters.ClaimRemoved(), 0, 'latest');
  const requested = await c.queryFilter(c.filters.ClaimRequested(), 0, 'latest');
  const owners = await c.queryFilter(c.filters.OwnershipTransferred(), 0, 'latest');
  const timeline = [...added, ...changed, ...removed].sort((x, y) => x.blockNumber - y.blockNumber).map((e) => `${e.fragment.name}@${e.blockNumber}:${utf8(e.args.data)}`);
  out('timeline-from-logs', `${CONTRACT}.getClaimIdsByTopic`, true, 0, `log scan: ClaimRequested=${requested.length} ClaimAdded=${added.length} ClaimChanged=${changed.length} ClaimRemoved=${removed.length} OwnershipTransferred=${owners.length}; inspection timeline: ${timeline.join(' -> ')}`);
  assert(added.length === 1 && changed.length === 2 && removed.length === 1 && owners.length === 2, 'counts');
  assert([r1, r2, r3, r4, r5].every((r) => r.status === 1), 'all ok');
  assert((await view('current-state', `${CONTRACT}.getClaimIdsByTopic`, c.getClaimIdsByTopic(3), (v) => `getClaimIdsByTopic(INSPECTION) -> ${v.length} now: current state forgets the 3 inspections; only the log remembers (no changed pointer, no linked list: O(chain) scan per contract address)`)).length === 0, 'empty now');
  out('history-not-measured', `${CONTRACT}.getClaim`, true, 0, 'the comparison measures addClaim/removeClaim gas and never the history read; ClaimChanged is listed in the manifest as the only lifecycle marker');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
