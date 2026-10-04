'use strict';
/**
 * erc-735 / creation — one claim-holder contract per vehicle: deploying
 * CVINVehicleClaimHolder(vin) IS the creation; the constructor stores vin + vinHash, makes
 * msg.sender the owner (MANAGEMENT-key role) and emits VehicleIdentityCreated.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/creation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-735';
const FAMILY = 'creation';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
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
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const F = await ethers.getContractFactory(CONTRACT, vehicleOwner);
  await reverts('deploy-empty-vin', `${CONTRACT}.constructor`, F.deploy(''), 'empty VIN', 'constructor guard: a VIN is mandatory (length is not checked beyond non-empty)');
  const c = await F.deploy(VIN);
  const r = await c.deploymentTransaction().wait();
  const id = await c.getAddress();
  out('deploy-identity', `${CONTRACT}.constructor`, true, r.gasUsed, `MEASURED (createIdentity = claim-holder deployment; L1 create 1,371,394): identity id = ${short(id)}; constructor stores vin + keccak256(vin), owner = msg.sender`);
  const ev = eventsOf(r, c, 'VehicleIdentityCreated');
  assert(ev.length === 1 && ev[0].args.vin === VIN && ev[0].args.owner === vehicleOwner.address && ev[0].args.vinHash === ethers.keccak256(ethers.toUtf8Bytes(VIN)), 'VehicleIdentityCreated');
  out('event-VehicleIdentityCreated', `${CONTRACT}.constructor`, true, 0, `VehicleIdentityCreated(vinHash=${short(ev[0].args.vinHash)}, vin=${VIN}, owner=${short(vehicleOwner.address)}) + OwnershipTransferred(0, owner) in the deployment receipt`);
  assert(eventsOf(r, c, 'OwnershipTransferred').length === 1, 'OwnershipTransferred');
  assert((await view('vin', `${CONTRACT}.vin`, c.vin(), (v) => `vin() == ${v} (immutable: no setter exists)`)) === VIN, 'vin');
  assert((await view('vinHash', `${CONTRACT}.vinHash`, c.vinHash(), (v) => `vinHash() == ${short(v)} == keccak256(bytes(vin)) — stable 32-byte identifier for indexes`)) === ethers.keccak256(ethers.toUtf8Bytes(VIN)), 'vinHash');
  assert((await view('owner', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)} (plays the ERC-734 MANAGEMENT key)`)) === vehicleOwner.address, 'owner');
  for (const [t, n] of [[1, 'VIN_ATTESTATION'], [2, 'MANUFACTURER_CERT'], [3, 'INSPECTION'], [4, 'INSURANCE']]) {
    assert((await c.getClaimIdsByTopic(t)).length === 0, `${n} empty`);
  }
  out('no-claims-at-birth', `${CONTRACT}.getClaimIdsByTopic`, true, 0, 'all four vehicle topics are empty at creation: the identity asserts a VIN but holds no attestation of it yet (the VIN_ATTESTATION claim comes from a manufacturer, see vin-linkage)');
  const code = await ethers.provider.getCode(id);
  out('bytecode-size', `${CONTRACT}.constructor`, true, 0, `runtime bytecode ${(code.length - 2) / 2} bytes per vehicle; the VIN string costs 1 extra slot (<=31 bytes)`);
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const a = await ad.create({ vin: 'WBA3A5C58DF586741', owner: newOwner.address });
  out('adapter-create', `${CONTRACT}.constructor`, true, a.gasUsed, `adapter.create: ${a.note}`);
  const a2 = await ad.create({ vin: '5YJ3E1EA7KF317000', owner: ethers.Wallet.createRandom().address });
  out('adapter-create-foreign-owner', `${CONTRACT}.transferOwnership`, true, a2.gasUsed, `owner without local signer -> deploy + transferOwnership: ${a2.note}`);
  out('creation-asymmetry', `${CONTRACT}.constructor`, true, 0, 'creation is DEPLOYED per vehicle and carries the VIN in the constructor (vs ERC-1056: implicit, VIN in a wrapper mapping; vs ERC-725xy: deployed, VIN written afterwards)');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
