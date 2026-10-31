'use strict';
/**
 * erc-725xy / creation — deploying CVINVehicleERC725XY(initialOwner) is the creation, the
 * birth record goes into the ERC-725Y store (setVehicleBirthAttributes), and the account can
 * itself CREATE / CREATE2 contracts (ContractCreated) — an identity that deploys.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/creation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725xy';
const FAMILY = 'creation';
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

const CONTRACT = 'CVINVehicleERC725XY';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const F = await ethers.getContractFactory(CONTRACT, deployer);
  await reverts('deploy-zero-owner', `${CONTRACT}.constructor`, F.deploy(ethers.ZeroAddress), 'owner is the zero address', 'constructor guard');
  const c = await F.deploy(vehicleOwner.address);
  const r = await c.deploymentTransaction().wait();
  const id = await c.getAddress();
  out('deploy-identity', `${CONTRACT}.constructor`, true, r.gasUsed, `MEASURED (createIdentity = account deployment; L1 create 1,730,753 incl. the VIN write): constructor(initialOwner) — the deployer (manufacturer) can create an account owned by someone else; identity id = ${short(id)}`);
  const ev = eventsOf(r, c, 'OwnershipTransferred');
  assert(ev.length === 1 && ev[0].args.newOwner === vehicleOwner.address, 'OwnershipTransferred');
  assert((await view('owner', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)} (vehicle owner, not the deployer)`)) === vehicleOwner.address, 'owner');
  const code = await ethers.provider.getCode(id);
  out('bytecode-size', `${CONTRACT}.constructor`, true, 0, `runtime bytecode ${(code.length - 2) / 2} bytes per vehicle (full ERC-725X executor + ERC-725Y store), ~3.3x the basic ERC-725 proxy`);

  const rb = await tx('setVehicleBirthAttributes', `${CONTRACT}.setVehicleBirthAttributes`, c.connect(vehicleOwner).setVehicleBirthAttributes(VIN, 'Honda', 'Accord', 2003),
    'birth record (VIN, make, model, year) written into the ERC-725Y store as 4 DataChanged + 4 cold SSTOREs in one tx; not measured (the comparison writes only VIN_KEY via setData)');
  const dc = eventsOf(rb, c, 'DataChanged');
  assert(dc.length === 4, '4 DataChanged');
  assert((await view('getVehicleVIN', `${CONTRACT}.getVehicleVIN`, c.getVehicleVIN(), (v) => `getVehicleVIN() == ${v} (readable on-chain by any contract)`)) === VIN, 'vin');

  // the identity deploys contracts: OPERATION_CREATE / OPERATION_CREATE2
  const OP_CREATE = await view('OPERATION_CREATE', `${CONTRACT}.OPERATION_CREATE`, c.OPERATION_CREATE(), (v) => `OPERATION_CREATE == ${v}`);
  const OP_CREATE2 = await view('OPERATION_CREATE2', `${CONTRACT}.OPERATION_CREATE2`, c.OPERATION_CREATE2(), (v) => `OPERATION_CREATE2 == ${v}`);
  const T = await ethers.getContractFactory('CVINExecuteTarget', deployer);
  const bytecode = T.bytecode;
  await reverts('create-with-recipient', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OP_CREATE, deployer.address, 0, bytecode), 'CREATE requires empty recipient', 'spec guard');
  await reverts('create-empty-bytecode', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OP_CREATE, ethers.ZeroAddress, 0, '0x'), 'no contract bytecode provided', 'spec guard');
  const r1 = await tx('execute-CREATE', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OP_CREATE, ethers.ZeroAddress, 0, bytecode),
    'the vehicle identity deploys a child contract (e.g. its own telemetry log) via CREATE; ContractCreated(1, addr, 0, 0); the child\'s deployer is the identity, not an EOA; not measured');
  const cc1 = eventsOf(r1, c, 'ContractCreated');
  assert(cc1.length === 1 && cc1[0].args.operationType === OP_CREATE, 'ContractCreated CREATE');
  const child1 = cc1[0].args.contractAddress;
  assert((await ethers.provider.getCode(child1)).length > 2, 'child deployed');
  const expected1 = ethers.getCreateAddress({ from: id, nonce: 1 });
  assert(child1 === expected1, 'CREATE address = keccak(rlp(identity, nonce 1))');
  out('child-address-CREATE', `${CONTRACT}.execute`, true, 0, `child ${short(child1)} == getCreateAddress(identity, nonce=1): the account has its own nonce like an EOA`);
  const salt = ethers.id('cvin:telemetry:' + VIN);
  const r2 = await tx('execute-CREATE2', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OP_CREATE2, ethers.ZeroAddress, 0, ethers.concat([bytecode, salt])),
    'CREATE2 with the erc725 convention (last 32 bytes of data = salt): deterministic child address derivable from (identity, salt, initcode) before deployment; ContractCreated(2, addr, 0, salt); not measured');
  const cc2 = eventsOf(r2, c, 'ContractCreated');
  assert(cc2.length === 1 && cc2[0].args.salt === salt, 'ContractCreated CREATE2');
  const expected2 = ethers.getCreate2Address(id, salt, ethers.keccak256(bytecode));
  assert(cc2[0].args.contractAddress === expected2, 'CREATE2 address matches');
  out('child-address-CREATE2', `${CONTRACT}.execute`, true, 0, `child ${short(cc2[0].args.contractAddress)} == getCreate2Address(identity, salt, keccak(initcode)) — counterfactual deployment from an identity`);
  await reverts('create2-short-data', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OP_CREATE2, ethers.ZeroAddress, 0, '0x1234'), 'CREATE2 needs bytecode + salt', 'spec guard');

  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const a = await ad.create({ vin: 'WBA3A5C58DF586741', owner: newOwner.address });
  out('adapter-create', `${CONTRACT}.setData`, true, a.gasUsed, `adapter.create = deploy + setData(VIN_KEY): ${a.note}`);
  out('creation-asymmetry', `${CONTRACT}.constructor`, true, 0, 'creation is DEPLOYED per vehicle (heaviest of all options) but yields an account that can hold ETH, call, and deploy — the comparison prices the deployment and never uses what it buys');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
