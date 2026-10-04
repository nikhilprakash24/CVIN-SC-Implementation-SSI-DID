'use strict';
/**
 * erc-735 / vin-linkage — the VIN is immutable constructor state (vin, vinHash) and can be
 * ATTESTED by a manufacturer via a VIN_ATTESTATION claim whose data must equal vin().
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/vin-linkage.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-735';
const FAMILY = 'vin-linkage';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const utf8 = (x) => ethers.toUtf8String(x);
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINVehicleClaimHolder';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, , manufacturer] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy(VIN);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, `VIN ${VIN} fixed at deployment`);
  const id = await c.getAddress();
  const sign = (signer, topic, data) => signer.signMessage(ethers.getBytes(ethers.solidityPackedKeccak256(['address', 'uint256', 'bytes'], [id, topic, data])));

  assert((await view('vin', `${CONTRACT}.vin`, c.vin(), (v) => `vin() == ${v}: self-asserted (whoever deploys picks the VIN; no format/uniqueness check; no setter — immutable)`)) === VIN, 'vin');
  const vh = await view('vinHash', `${CONTRACT}.vinHash`, c.vinHash(), (v) => `vinHash() == ${short(v)} == keccak256(bytes(vin)): the indexed key in VehicleIdentityCreated, usable for an off-chain VIN -> contract index`);
  assert(vh === ethers.keccak256(ethers.toUtf8Bytes(VIN)), 'hash');
  const VA = await view('VIN_ATTESTATION', `${CONTRACT}.VIN_ATTESTATION`, c.VIN_ATTESTATION(), (v) => `VIN_ATTESTATION topic == ${v}`);
  assert((await view('no-attestation-yet', `${CONTRACT}.claimExists`, c.claimExists(manufacturer.address, VA), (v) => `claimExists(manufacturer, VIN_ATTESTATION) == ${v}: self-asserted VIN only`)) === false, 'none');
  const r = await tx('addClaim-VIN_ATTESTATION', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, manufacturer.address, await sign(manufacturer, VA, b(VIN)), b(VIN), ''),
    'manufacturer attests the VIN: the signature binds (this contract address, topic 1, VIN bytes) — the attestation is non-transferable to another contract');
  void r;
  const g = await view('getClaim-vin', `${CONTRACT}.getClaim`, c.getClaim(ethers.solidityPackedKeccak256(['address', 'uint256'], [manufacturer.address, VA])), (v) => `claim data "${utf8(v[4])}" == vin() ${utf8(v[4]) === VIN}: a verifier cross-checks the attested VIN against the self-asserted one (the contract does NOT enforce equality)`);
  assert(utf8(g[4]) === VIN, 'attested equals asserted');
  await tx('addClaim-VIN_ATTESTATION-mismatch', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, deployer.address, await sign(deployer, VA, b('WBA3A5C58DF586741')), b('WBA3A5C58DF586741'), ''),
    'OBSERVATION: an attestation for a DIFFERENT VIN is accepted on this identity — addClaim does not compare data with vin() even on topic 1; the verifier must');
  const c2 = await (await ethers.getContractFactory(CONTRACT, newOwner)).deploy(VIN);
  await c2.deploymentTransaction().wait();
  out('duplicate-vin-identity', `${CONTRACT}.vin`, true, 0, `a second claim holder ${short(await c2.getAddress())} deployed with the SAME VIN: per-vehicle contracts cannot enforce VIN uniqueness; only the manufacturer attestation (which binds the contract address) disambiguates`);
  assert((await c2.vin()) === VIN, 'dup');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-vin', 'adapter.resolve', true, 0, `resolve -> vehicle.vin=${doc.vehicle.vin} vinHash=${short(doc.vehicle.vinHash)} claims=${doc.claims.length} (VIN_ATTESTATION x${doc.claims.filter((x) => x.topic === 1).length})`);
  assert(doc.vehicle.vin === VIN, 'resolve');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
