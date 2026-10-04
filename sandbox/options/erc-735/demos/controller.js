'use strict';
/**
 * erc-735 / controller — owner / transferOwnership: the single owner plays the ERC-734
 * MANAGEMENT key; a sale rotates it, claims stay with the contract; no renounce exists.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/controller.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-735';
const FAMILY = 'controller';
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
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINVehicleClaimHolder';
const VIN = '1HGCM82633A004352';

async function main() {
  const [, vehicleOwner, newOwner, , stranger, manufacturer] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy(VIN);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle claim holder');
  const id = await c.getAddress();
  const data = ethers.toUtf8Bytes(VIN);
  const digest = ethers.solidityPackedKeccak256(['address', 'uint256', 'bytes'], [id, 2, data]);
  const sig = await manufacturer.signMessage(ethers.getBytes(digest));
  await tx('authorizeIssuer-manufacturer', `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(manufacturer.address, 2), 'D25: issuers must be authorised per topic — the first owner admits the OEM for MANUFACTURER_CERT');
  await tx('addClaim-manufacturer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(2, 1, manufacturer.address, sig, data, 'ipfs://cert'), 'a claim anchored by the first owner (to show it survives the sale)');
  const claimId = ethers.solidityPackedKeccak256(['address', 'uint256'], [manufacturer.address, 2]);

  assert((await view('owner', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)}; identity == ${short(id)}`)) === vehicleOwner.address, 'owner');
  await reverts('transferOwnership-by-stranger', `${CONTRACT}.transferOwnership`, c.connect(stranger).transferOwnership(stranger.address), 'caller is not the owner', 'owner-gated');
  await reverts('transferOwnership-to-zero', `${CONTRACT}.transferOwnership`, c.connect(vehicleOwner).transferOwnership(ethers.ZeroAddress), 'new owner is zero address', 'zero guard: there is NO renounceOwnership in this contract — an identity can never be made ownerless');
  const r = await tx('transferOwnership', `${CONTRACT}.transferOwnership`, c.connect(vehicleOwner).transferOwnership(newOwner.address),
    'MEASURED (benchmark transferOwnership; L1 controller-change 28,690): vehicle sale = owner rotation; OwnershipTransferred');
  assert(eventsOf(r, c, 'OwnershipTransferred')[0].args.newOwner === newOwner.address, 'event');
  assert((await view('owner-after', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)}`)) === newOwner.address, 'rotated');
  assert((await view('claims-survive', `${CONTRACT}.claimExists`, c.claimExists(manufacturer.address, 2), (v) => `claimExists(manufacturer, MANUFACTURER_CERT) == ${v}: claims belong to the identity, not to the owner`)) === true, 'claim survives');
  assert((await view('issuer-authorisation-survives', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(manufacturer.address, 2), (v) => `isAuthorizedIssuer(manufacturer, MANUFACTURER_CERT) == ${v}: D25a authorisations belong to the VEHICLE too — they survive the sale; the buyer may revokeIssuer`)) === true, 'auth survives');
  await reverts('old-owner-cannot-revoke-issuer', `${CONTRACT}.revokeIssuer`, c.connect(vehicleOwner).revokeIssuer(manufacturer.address, 2), 'caller is not the owner', 'the registry is MANAGEMENT-key state: the seller can no longer admit or revoke issuers');
  await reverts('old-owner-locked-out', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(2, 1, manufacturer.address, sig, data, ''), 'caller is not the owner', 'previous owner cannot anchor claims any more');
  await reverts('old-owner-cannot-remove', `${CONTRACT}.removeClaim`, c.connect(vehicleOwner).removeClaim(claimId), 'caller is not owner nor issuer', '… nor remove them (only owner or issuer)');
  await tx('new-owner-removes', `${CONTRACT}.removeClaim`, c.connect(newOwner).removeClaim(claimId), 'the buyer may drop the seller-era claim');
  await tx('new-owner-revokes-issuer', `${CONTRACT}.revokeIssuer`, c.connect(newOwner).revokeIssuer(manufacturer.address, 2), '… and withdraw the seller-era issuer authorisation (IssuerRevoked)');
  assert(typeof c.renounceOwnership === 'undefined', 'no renounce');
  out('no-renounce', `${CONTRACT}.owner`, true, 0, 'no renounceOwnership and no zero transfer: unlike ERC-725/725xy this identity cannot be frozen; decommissioning is not expressible (revocation family: claims only)');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
