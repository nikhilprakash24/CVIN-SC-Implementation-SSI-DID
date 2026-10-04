'use strict';
/**
 * erc-735 / vin-linkage — the VIN is immutable constructor state (vin, vinHash) and can be
 * ATTESTED by an authorised manufacturer via a VIN_ATTESTATION claim; since D25b the contract
 * enforces that the payload's trailing bytes(vin).length bytes hash to vinHash (an attestation
 * for another VIN, a truncated VIN or a VIN followed by further bytes is rejected).
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
const reverts = async (step, fn, p, reason, note) => {
  let msg = null;
  try { const t = await p; if (t && typeof t.wait === 'function') await t.wait(); } catch (e) { msg = String(e.message || e); const d = e.data || (e.error && e.error.data); if (typeof d === 'string' && d.startsWith('0x08c379a0')) { try { msg += ' | ' + ethers.AbiCoder.defaultAbiCoder().decode(['string'], '0x' + d.slice(10))[0]; } catch (_) { /* not Error(string) */ } } }
  if (msg === null) throw new Error(`${step}: expected revert "${reason}" but the call succeeded`);
  if (!msg.includes(reason)) throw new Error(`${step}: expected revert "${reason}", got: ${msg}`);
  out(step, fn, true, 0, `reverted as expected ("${reason}"): ${note}`);
};
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
  await reverts('addClaim-VIN_ATTESTATION-unauthorised', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, manufacturer.address, await sign(manufacturer, VA, b(VIN)), b(VIN), ''), 'issuer not authorized for topic', 'D25a: a correct VIN attestation from an OEM the owner has not admitted is rejected — the registry check precedes the VIN check');
  await tx('authorizeIssuer-manufacturer', `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(manufacturer.address, VA), 'D25: issuers must be authorised per topic — the owner admits the OEM for VIN_ATTESTATION');
  assert((await view('isAuthorizedIssuer', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(manufacturer.address, VA), (v) => `isAuthorizedIssuer(manufacturer, VIN_ATTESTATION) == ${v}`)) === true, 'authorised');
  const r = await tx('addClaim-VIN_ATTESTATION', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, manufacturer.address, await sign(manufacturer, VA, b(VIN)), b(VIN), ''),
    'manufacturer attests the VIN: the signature binds (this contract address, topic 1, VIN bytes) — the attestation is non-transferable to another contract; the bare bytes(vin) payload satisfies the D25b trailing-bytes rule');
  void r;
  const g = await view('getClaim-vin', `${CONTRACT}.getClaim`, c.getClaim(ethers.solidityPackedKeccak256(['address', 'uint256'], [manufacturer.address, VA])), (v) => `claim data "${utf8(v[4])}" == vin() ${utf8(v[4]) === VIN}: FIXED (D25b) — the contract now enforces this equality at addClaim time, so a verifier may trust any stored topic-1 claim to name THIS vehicle's VIN`);
  assert(utf8(g[4]) === VIN, 'attested equals asserted');
  await reverts('addClaim-VIN_ATTESTATION-mismatch', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, manufacturer.address, await sign(manufacturer, VA, b('WBA3A5C58DF586741')), b('WBA3A5C58DF586741'), ''), 'VIN attestation does not match holder VIN',
    'FIXED (D25b): an attestation for a DIFFERENT VIN is REJECTED on this identity even from the authorised OEM — formerly addClaim accepted any topic-1 payload and the verifier had to compare it with vin()');
  await reverts('addClaim-VIN_ATTESTATION-truncated', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, manufacturer.address, await sign(manufacturer, VA, b(VIN.slice(0, 16))), b(VIN.slice(0, 16)), ''), 'VIN attestation does not match holder VIN', 'D25b encoding rule: a payload shorter than bytes(vin).length cannot encode the VIN');
  await reverts('addClaim-VIN_ATTESTATION-suffixed', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, manufacturer.address, await sign(manufacturer, VA, b(`${VIN}:2003`)), b(`${VIN}:2003`), ''), 'VIN attestation does not match holder VIN', 'D25b encoding rule: the VIN must be the TRAILING field — a VIN followed by further bytes is rejected (structured JSON/ABI payloads belong on the other topics)');
  await tx('authorizeIssuer-second-attester', `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(deployer.address, VA), 'a second attester (e.g. the registration authority) admitted for VIN_ATTESTATION');
  const prefixed = b(`VIN:${VIN}`);
  await tx('addClaim-VIN_ATTESTATION-prefixed', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(VA, 1, deployer.address, await sign(deployer, VA, prefixed), prefixed, ''),
    'D25b encoding rule: an application prefix BEFORE the VIN ("VIN:" + vin, as the L2 test and the gas benchmark use) is accepted — only the trailing bytes(vin).length bytes are compared with vinHash');
  assert((await c.getClaimIdsByTopic(VA)).length === 2, 'two attestations');
  const c2 = await (await ethers.getContractFactory(CONTRACT, newOwner)).deploy(VIN);
  await c2.deploymentTransaction().wait();
  out('duplicate-vin-identity', `${CONTRACT}.vin`, true, 0, `a second claim holder ${short(await c2.getAddress())} deployed with the SAME VIN: per-vehicle contracts cannot enforce VIN uniqueness (D25b binds a topic-1 claim to ITS holder's VIN, not the VIN to one holder); only the manufacturer attestation (which binds the contract address) disambiguates`);
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
