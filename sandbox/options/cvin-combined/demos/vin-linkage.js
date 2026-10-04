'use strict';
/**
 * cvin-combined / vin-linkage — the VIN is anchored as a CLAIM_TOPIC_VIN claim signed by the
 * manufacturer (O(1) readable, issuer-verified) or as an event-only attribute; there is no
 * VIN -> identity index in the registry.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/vin-linkage.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'vin-linkage';
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
const utf8 = (x) => ethers.toUtf8String(x);
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINCombinedIdentity';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const d = await ad.deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, d.gasUsed, 'shared hybrid registry');
  const reg = ad.registry;
  const id = vehicleOwner.address;

  const VT = await view('CLAIM_TOPIC_VIN', `${CONTRACT}.CLAIM_TOPIC_VIN`, reg.CLAIM_TOPIC_VIN(), (v) => `CLAIM_TOPIC_VIN == ${v}`);
  const c = await ad.create({ vin: VIN, owner: id, anchorVin: true });
  out('create-anchorVin', `${CONTRACT}.addClaim`, true, c.gasUsed, `adapter.create({ anchorVin }): ${c.note} — identity still implicit, the VIN is a manufacturer-signed claim`);
  const claimId = ethers.solidityPackedKeccak256(['address', 'uint256'], [ad.issuer.address, VT]);
  const g = await view('getClaim-vin', `${CONTRACT}.getClaim`, reg.getClaim(id, claimId), (v) => `getClaim -> topic=${v[0]} issuer=${short(v[2])} data="${utf8(v[4])}" uri=${v[5]}: any contract can read the attested VIN and who attested it`);
  assert(utf8(g[4]) === VIN, 'vin claim');
  assert((await view('hasValidClaim-vin', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, VT, ad.issuer.address), (v) => `hasValidClaim(id, VIN, manufacturer) == ${v}`)) === true, 'valid');
  const ra = await tx('setAttribute-vin', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, h('did/vehicle/vin'), b(VIN), 31536000 * 20), 'the alternative: VIN as an event-only, self-asserted attribute (did:ethr style)');
  out('vin-two-ways', `${CONTRACT}.setAttribute`, true, 0, `claim ${c.gasUsed} gas (issuer-signed, stored, O(1) verifiable) vs attribute ${ra.gasUsed} gas (self-asserted, event-only): the hybrid's defining choice; the comparison measures addClaim but never frames it as VIN anchoring`);
  assert(typeof reg.getDIDFromVIN === 'undefined' && typeof reg.vinToDID === 'undefined', 'no index');
  out('no-reverse-index', `${CONTRACT}.getClaimIdsByTopic`, true, 0, 'no VIN -> identity mapping (unlike CVINVehicleDIDRegistry): resolving a VIN requires scanning ClaimAdded(topic=1) events off-chain; uniqueness of a VIN across identities is not enforced');
  const c2 = await ad.create({ vin: VIN, owner: newOwner.address, anchorVin: true });
  out('same-vin-second-identity', `${CONTRACT}.addClaim`, true, c2.gasUsed, `the same manufacturer key attests the SAME VIN for a second identity ${short(newOwner.address)}: accepted — the issuer, not the chain, must keep VINs unique`);
  assert((await reg.hasValidClaim(newOwner.address, VT, ad.issuer.address)) === true, 'dup');
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-vin', 'adapter.resolve', true, 0, `resolve -> vehicle.vin=${doc.vehicle.vin} (taken from the topic-1 claim) attributes=${JSON.stringify(doc.vehicle.attributes)}`);
  assert(doc.vehicle.vin === VIN, 'resolve');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
