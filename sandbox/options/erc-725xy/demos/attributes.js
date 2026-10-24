'use strict';
/**
 * erc-725xy / attributes — the ERC-725Y generic key/value store: setData / getData, the batch
 * variants, the CVIN convenience setter, the well-known data keys, DataChanged, and the guards.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/attributes.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725xy';
const FAMILY = 'attributes';
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
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const utf8 = (x) => ethers.toUtf8String(x);
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINVehicleERC725XY';
const VIN = '5YJ3E1EA7KF317000';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(vehicleOwner.address);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle account');
  const id = await c.getAddress();

  const K = {};
  for (const [n, s] of [['VIN_KEY', 'cvin:vin'], ['MAKE_KEY', 'cvin:make'], ['MODEL_KEY', 'cvin:model'], ['YEAR_KEY', 'cvin:year']]) {
    K[n] = await view(`const-${n}`, `${CONTRACT}.${n}`, c[n](), (v) => `${n} = keccak256("${s}") = ${short(v)}`);
    assert(K[n] === h(s), n);
  }
  assert((await view('getData-empty', `${CONTRACT}.getData`, c.getData(K.VIN_KEY), (v) => `getData(VIN_KEY) == ${v} (empty bytes before any write)`)) === '0x', 'empty');

  const r1 = await tx('setData-VIN', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(K.VIN_KEY, b(VIN)),
    'MEASURED (benchmark updateAttribute; L1 attribute 95,166): cold SSTORE of a 17-byte value + DataChanged(key, value); unlike ERC-1056 the value is READABLE on-chain afterwards');
  const dc = eventsOf(r1, c, 'DataChanged');
  assert(dc.length === 1 && utf8(dc[0].args.dataValue) === VIN, 'DataChanged');
  assert(utf8(await view('getData-VIN', `${CONTRACT}.getData`, c.getData(K.VIN_KEY), (v) => `getData(VIN_KEY) -> "${utf8(v)}"`)) === VIN, 'read back');
  const r2 = await tx('setData-VIN-rewrite', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(K.VIN_KEY, b(VIN)), 'warm same-value rewrite: shows the cold/warm asymmetry the comparison hides by measuring only the first write');
  assert(r2.gasUsed < r1.gasUsed, 'warm cheaper');
  await reverts('setData-by-stranger', `${CONTRACT}.setData`, c.connect(stranger).setData(K.MAKE_KEY, b('Evil')), 'caller is not the owner', 'owner-gated');

  const r3 = await tx('setDataBatch', `${CONTRACT}.setDataBatch`, c.connect(vehicleOwner).setDataBatch([K.MAKE_KEY, K.MODEL_KEY, K.YEAR_KEY], [b('Tesla'), b('Model 3'), ethers.AbiCoder.defaultAbiCoder().encode(['uint256'], [2019])]),
    'three attributes in one tx: 3 DataChanged; per-attribute cost lower than 3 separate setData (shared 21k base); not measured');
  assert(eventsOf(r3, c, 'DataChanged').length === 3, '3 DataChanged');
  const batch = await view('getDataBatch', `${CONTRACT}.getDataBatch`, c.getDataBatch([K.VIN_KEY, K.MAKE_KEY, K.MODEL_KEY, K.YEAR_KEY]), (v) => `getDataBatch -> vin="${utf8(v[0])}" make="${utf8(v[1])}" model="${utf8(v[2])}" year=${ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], v[3])[0]} (one eth_call for the whole record)`);
  assert(utf8(batch[1]) === 'Tesla', 'batch read');
  await reverts('setDataBatch-mismatch', `${CONTRACT}.setDataBatch`, c.connect(vehicleOwner).setDataBatch([K.MAKE_KEY], [b('a'), b('b')]), 'keys/values length mismatch', 'guard');
  await reverts('setDataBatch-empty', `${CONTRACT}.setDataBatch`, c.connect(vehicleOwner).setDataBatch([], []), 'empty arrays', 'guard');

  const r4 = await tx('setVehicleBirthAttributes', `${CONTRACT}.setVehicleBirthAttributes`, c.connect(vehicleOwner).setVehicleBirthAttributes(VIN, 'Tesla', 'Model 3', 2019),
    'CVIN convenience: VIN+make+model+year with a fixed encoding (strings as UTF-8 bytes, year abi-encoded uint256); all warm rewrites here');
  assert(eventsOf(r4, c, 'DataChanged').length === 4, '4 DataChanged');
  await reverts('setVehicleBirthAttributes-by-stranger', `${CONTRACT}.setVehicleBirthAttributes`, c.connect(stranger).setVehicleBirthAttributes(VIN, 'x', 'y', 1), 'caller is not the owner', 'owner-gated');

  // arbitrary keys and the payable quirk
  const FW = h('cvin:firmwareHash');
  await tx('setData-custom-key', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(FW, ethers.keccak256(b('fw-2025.09.1'))), 'any bytes32 key / bytes value (firmware hash): the store is schema-free; ERC-725Y schemas (LSP2) are an off-chain convention');
  const bal0 = await ethers.provider.getBalance(id);
  await tx('setData-with-value', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(h('cvin:note'), b('funded'), { value: ethers.parseEther('0.5') }), 'setData is payable (ERC-725Y spec): ETH sent along is kept by the account');
  const bal1 = await ethers.provider.getBalance(id);
  assert(bal1 - bal0 === ethers.parseEther('0.5'), 'value kept');
  out('account-balance', `${CONTRACT}.getData`, true, 0, `account balance ${ethers.formatEther(bal1)} ETH after the payable setData: the identity is also a wallet`);
  out('no-expiry', `${CONTRACT}.getData`, true, 0, 'no validity/expiry on data keys (ERC-1056 attributes carry validTo): a stale inspection date must be interpreted by the verifier');

  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const a = await ad.setAttribute(id, 'cvin:color', 'White');
  out('adapter-setAttribute', `${CONTRACT}.setData`, true, a.gasUsed, `adapter: ${a.note}`);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve', 'adapter.resolve', true, 0, `resolve via getDataBatch: vin=${doc.vehicle.vin} make=${doc.vehicle.make} year=${doc.vehicle.year} attrs=${JSON.stringify(doc.vehicle.attributes)}`);
  assert(doc.vehicle.vin === VIN && doc.vehicle.year === 2019, 'resolve');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
