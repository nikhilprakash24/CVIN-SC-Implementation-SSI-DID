'use strict';
/**
 * erc-725xy / lifecycle-history — history is the event log only (DataChanged, Executed,
 * ContractCreated, OwnershipTransferred): there is no changed pointer / linked list, so a
 * verifier must range-scan; current state is a view, past values are events.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/lifecycle-history.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725xy';
const FAMILY = 'lifecycle-history';
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

const CONTRACT = 'CVINVehicleERC725XY';
const VIN = 'WVWZZZ1KZBW123456';

async function main() {
  const [deployer, vehicleOwner, newOwner] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(vehicleOwner.address);
  const r0 = await c.deploymentTransaction().wait();
  out('deploy-identity', `${CONTRACT}.constructor`, true, r0.gasUsed, 'OwnershipTransferred(0, owner) is history entry 0');
  const id = await c.getAddress();
  const ODO = h('cvin:odometerKm');
  const target = await (await ethers.getContractFactory('CVINExecuteTarget', deployer)).deploy();
  await target.deploymentTransaction().wait();

  await tx('h1-setData-VIN', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(await c.VIN_KEY(), b(VIN)), 'DataChanged #1');
  await tx('h2-setData-odo-12000', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(ODO, ethers.AbiCoder.defaultAbiCoder().encode(['uint256'], [12000])), 'DataChanged #2');
  await tx('h3-setData-odo-35000', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(ODO, ethers.AbiCoder.defaultAbiCoder().encode(['uint256'], [35000])), 'DataChanged #3 (overwrites #2 in storage)');
  await tx('h4-execute', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(0, await target.getAddress(), 0, target.interface.encodeFunctionData('setValue', [1])), 'Executed #1');
  await tx('h5-transferOwnership', `${CONTRACT}.transferOwnership`, c.connect(vehicleOwner).transferOwnership(newOwner.address), 'OwnershipTransferred #2 (sale)');
  await tx('h6-setData-odo-36000-by-buyer', `${CONTRACT}.setData`, c.connect(newOwner).setData(ODO, ethers.AbiCoder.defaultAbiCoder().encode(['uint256'], [36000])), 'DataChanged #4 by the new owner');
  await tx('h7-execute-CREATE', `${CONTRACT}.execute`, c.connect(newOwner).execute(1, ethers.ZeroAddress, 0, (await ethers.getContractFactory('CVINExecuteTarget')).bytecode), 'ContractCreated #1');

  assert(typeof c.changed === 'undefined', 'no changed pointer');
  out('no-changed-pointer', `${CONTRACT}.getData`, true, 0, 'the ABI has no changed()/lastChanged(): nothing on-chain says WHEN or HOW OFTEN the identity changed; only the current value is a view');
  const cur = await view('getData-current', `${CONTRACT}.getData`, c.getData(ODO), (v) => `getData(odometer) == ${ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], v)[0]} km (current state only)`);
  assert(ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], cur)[0] === 36000n, 'current');
  const dcs = await c.queryFilter(c.filters.DataChanged(ODO), 0, 'latest');
  out('scan-DataChanged-odometer', `${CONTRACT}.setData`, true, 0, `range scan DataChanged(dataKey=odometer) over the whole chain: ${dcs.map((e) => ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], e.args.dataValue)[0]).join(' -> ')} km — the odometer history exists only in logs (an odometer ROLLBACK would be visible here but not in getData)`);
  assert(dcs.length === 3, '3 odometer events');
  const all = await c.queryFilter(c.filters.DataChanged(), 0, 'latest');
  const exs = await c.queryFilter(c.filters.Executed(), 0, 'latest');
  const ccs = await c.queryFilter(c.filters.ContractCreated(), 0, 'latest');
  const ots = await c.queryFilter(c.filters.OwnershipTransferred(), 0, 'latest');
  out('scan-all-events', `${CONTRACT}.execute`, true, 0, `DataChanged=${all.length} Executed=${exs.length} ContractCreated=${ccs.length} OwnershipTransferred=${ots.length}; keys touched: ${[...new Set(all.map((e) => e.args.dataKey))].length}; no linked list — O(chain) scan per identity (ERC-1056 walks O(#changes))`);
  assert(all.length === 4 && exs.length === 1 && ccs.length === 1 && ots.length === 2, 'event counts (a CREATE via execute emits ContractCreated, not Executed)');
  const vinEv = all.find((e) => utf8(e.args.dataValue) === VIN);
  assert(vinEv, 'vin event');
  out('executed-is-selector-only', `${CONTRACT}.execute`, true, 0, `Executed carries only the 4-byte selector (${exs[0].args.selector}), not the calldata: the full action is reconstructible only from the transaction input, not from the log (ERC-725 canonical shape)`);
  out('history-not-measured', `${CONTRACT}.getDataBatch`, true, 0, 'the comparison never reads history; L1 "resolve" reads getDataBatch (current state) at 0 gas');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
