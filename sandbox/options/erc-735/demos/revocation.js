'use strict';
/**
 * erc-735 / revocation — sub-identity only: removeClaim by the owner (holder-side) or by the
 * issuer (issuer-side), plus (D25a) revokeIssuer, which withdraws an issuer's right to issue
 * going forward without touching its existing claims; no identity-level revocation and no
 * claim expiry.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/revocation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-735';
const FAMILY = 'revocation';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const reverts = async (step, fn, p, reason, note) => {
  let msg = null;
  try { const t = await p; if (t && typeof t.wait === 'function') await t.wait(); } catch (e) { msg = String(e.message || e); const d = e.data || (e.error && e.error.data); if (typeof d === 'string' && d.startsWith('0x08c379a0')) { try { msg += ' | ' + ethers.AbiCoder.defaultAbiCoder().decode(['string'], '0x' + d.slice(10))[0]; } catch (_) { /* not Error(string) */ } } }
  if (msg === null) throw new Error(`${step}: expected revert "${reason}" but the call succeeded`);
  if (!msg.includes(reason)) throw new Error(`${step}: expected revert "${reason}", got: ${msg}`);
  out(step, fn, true, 0, `reverted as expected ("${reason}"): ${note}`);
};
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const eventsOf = (receipt, c, name) => receipt.logs.map((l) => { try { return c.interface.parseLog(l); } catch (_) { return null; } }).filter((e) => e && e.name === name);
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINVehicleClaimHolder';
const VIN = '5YJ3E1EA7KF317000';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger, manufacturer, inspector, insurer] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy(VIN);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle claim holder');
  const id = await c.getAddress();
  const sign = (signer, topic, data) => signer.signMessage(ethers.getBytes(ethers.solidityPackedKeccak256(['address', 'uint256', 'bytes'], [id, topic, data])));
  const claimId = (issuer, topic) => ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer, topic]);
  // three inspections by three issuers on the same topic, to exercise index compaction
  const issuers = [inspector, insurer, manufacturer];
  for (const [i, s] of issuers.entries()) {
    await tx(`authorizeIssuer-${i}`, `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(s.address, 3), `D25: issuers must be authorised per topic — issuer #${i} ${short(s.address)} admitted for INSPECTION`);
    const d = b(`APK:${2024 + i}:PASS`);
    await tx(`addClaim-INSPECTION-${i}`, `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(3, 1, s.address, await sign(s, 3, d), d, ''), `inspection claim #${i} by ${short(s.address)}`);
  }
  assert((await view('index-before', `${CONTRACT}.getClaimIdsByTopic`, c.getClaimIdsByTopic(3), (v) => `getClaimIdsByTopic(INSPECTION) -> ${v.length}`)).length === 3, '3 claims');

  const r1 = await tx('removeClaim-owner-side', `${CONTRACT}.removeClaim`, c.connect(vehicleOwner).removeClaim(claimId(inspector.address, 3)),
    'MEASURED (benchmark revoke; L1 revoke 69,438): the holder drops a claim (first in the index -> swap-and-pop moves the last one forward)');
  const ev = eventsOf(r1, c, 'ClaimRemoved');
  assert(ev.length === 1 && ev[0].args.issuer === inspector.address, 'ClaimRemoved');
  const idx = await view('index-compacted', `${CONTRACT}.getClaimIdsByTopic`, c.getClaimIdsByTopic(3), (v) => `index now ${v.length}: [${v.map(short).join(', ')}] (order changed: not a stable list)`);
  assert(idx.length === 2 && idx[0] === claimId(manufacturer.address, 3), 'compacted');
  assert((await view('getClaim-removed', `${CONTRACT}.getClaim`, c.getClaim(claimId(inspector.address, 3)), (v) => `getClaim(removed) -> issuer=${v[2]} topic=${v[0]}: zeros, no tombstone — "revoked" and "never issued" are indistinguishable on-chain; the ClaimRemoved event is the only audit trail`)) [2] === ethers.ZeroAddress, 'zeros');
  await reverts('removeClaim-twice', `${CONTRACT}.removeClaim`, c.connect(vehicleOwner).removeClaim(claimId(inspector.address, 3)), 'claim does not exist', 'idempotence guard');

  await reverts('issuer-cannot-remove-others', `${CONTRACT}.removeClaim`, c.connect(insurer).removeClaim(claimId(manufacturer.address, 3)), 'caller is not owner nor issuer', 'an issuer may only withdraw its OWN claim');
  await tx('removeClaim-issuer-side', `${CONTRACT}.removeClaim`, c.connect(insurer).removeClaim(claimId(insurer.address, 3)), 'issuer-side revocation: the issuer withdraws without the holder\'s cooperation (the CRL analogue, pushed on-chain)');
  await reverts('stranger-cannot-remove', `${CONTRACT}.removeClaim`, c.connect(stranger).removeClaim(claimId(manufacturer.address, 3)), 'caller is not owner nor issuer', 'access');
  assert((await c.getClaimIdsByTopic(3)).length === 1, '1 left');

  // issuer-level revocation (D25a): forward-looking, distinct from claim removal
  await tx('revokeIssuer-manufacturer', `${CONTRACT}.revokeIssuer`, c.connect(vehicleOwner).revokeIssuer(manufacturer.address, 3), 'D25a: the holder withdraws issuer #2\'s right to issue INSPECTION claims (IssuerRevoked)');
  assert((await view('isAuthorizedIssuer-after-revoke', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(manufacturer.address, 3), (v) => `isAuthorizedIssuer(issuer #2, INSPECTION) == ${v}`)) === false, 'revoked');
  assert((await view('claim-survives-revokeIssuer', `${CONTRACT}.claimExists`, c.claimExists(manufacturer.address, 3), (v) => `claimExists(issuer #2, INSPECTION) == ${v}: revokeIssuer is FORWARD-LOOKING — the claim it already issued stays live until removeClaim; revoking an issuer is not revoking its claims`)) === true, 'claim stays');
  const dLate = b('APK:2027:PASS');
  await reverts('addClaim-after-revokeIssuer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(3, 1, manufacturer.address, await sign(manufacturer, 3, dLate), dLate, ''), 'issuer not authorized for topic', 'a later claim (or in-place update) by the revoked issuer is rejected despite a valid signature');
  out('no-expiry', `${CONTRACT}.getClaim`, true, 0, 'claims have NO validity window: an inspection from 2024 stays "valid" on-chain until someone removes it — currency must be judged from the data payload off-chain (contrast ERC-1056 validTo)');
  assert(typeof c.isRevoked === 'undefined', 'no identity revocation');
  out('no-identity-revocation', `${CONTRACT}.owner`, true, 0, 'no identity-level revocation and no renounce: a stolen/scrapped vehicle keeps a live claim holder; the best available signal is "all claims removed" (compare ERC1056Registry.revokeIdentity)');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const na = await ad.revoke(id);
  assert(na.notApplicable === true, 'bare id N/A');
  out('adapter-revoke-bare', 'adapter.revoke', true, 0, `adapter.revoke(id) -> NotApplicable: ${na.reason}`);
  const rv = await ad.revoke({ id, issuer: manufacturer.address, topic: 3 });
  out('adapter-revoke-claim', `${CONTRACT}.removeClaim`, true, rv.gasUsed, `adapter.revoke({ id, issuer, topic }) -> ${rv.note} (the revoked issuer's surviving claim is removed by the owner — the two revocation levels compose)`);
  assert((await c.getClaimIdsByTopic(3)).length === 0, 'all removed');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
