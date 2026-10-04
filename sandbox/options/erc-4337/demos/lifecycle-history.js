'use strict';
/**
 * ERC-4337 — family "Lifecycle events / history" (manifest: implemented via the AttributeChanged
 * and GuardianChanged events). The account stores only the LATEST owner, guardian and attribute
 * values; every history question is answered by log replay. This demo runs a small vehicle life
 * (attributes, guardian, rotation, recovery, executions, user operations) and then rebuilds the
 * timeline from the six event types, plus the adapter's resolve() which does the same for keys.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-4337/demos/lifecycle-history.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');
const Erc4337Adapter = require('../adapter');

const d = demo('erc-4337', 'lifecycle-history');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const { assert } = d;
  const adapter = new Erc4337Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await adapter.deploy();
  const created = await adapter.create({ vin: VINS.toyota, owner: vehicleOwner.address });
  const id = created.id;
  const acct = await ethers.getContractAt('CVINVehicleAccount', id);
  const ep = adapter.entryPoint;
  d.offchain('setup', 'adapter.deploy + adapter.create', `entry point + account ${id} via the adapter (create gas ${created.gasUsed})`);

  await d.tx('attr-vin', 'CVINVehicleAccount.setAttribute', acct.connect(vehicleOwner).setAttribute(ethers.id('cvin/vehicle/vin'), ethers.toUtf8Bytes(VINS.toyota)), 'life: VIN bound');
  await d.tx('attr-odometer-1', 'CVINVehicleAccount.setAttribute', acct.connect(vehicleOwner).setAttribute(ethers.id('cvin/vehicle/odometerKm'), ethers.toBeHex(12000, 32)), 'life: odometer 12000');
  await d.tx('guardian', 'CVINVehicleAccount.setGuardian', acct.connect(vehicleOwner).setGuardian(delegate.address), 'life: guardian named');
  const so = await adapter.signedOp(id, { fn: 'setAttribute', args: [ethers.id('cvin/vehicle/odometerKm'), ethers.toBeHex(48000, 32)] }, '0x');
  d.offchain('attr-odometer-2-userop', 'CVINMinimalEntryPoint.handleOp -> setAttribute', `life: odometer 48000 through a UserOperation (gas ${so.gasUsed})`);
  await d.tx('rotate', 'CVINVehicleAccount.transferOwnership', acct.connect(vehicleOwner).transferOwnership(newOwner.address), 'life: sold — key rotated to the buyer');
  await d.tx('execute', 'CVINVehicleAccount.execute', acct.connect(newOwner).execute(ep.target, 0, ep.interface.encodeFunctionData('nonces', [id])), 'life: an execution by the new owner');
  await d.tx('recover', 'CVINVehicleAccount.recoverOwner', acct.connect(delegate).recoverOwner(vehicleOwner.address), 'life: buyer lost the key; guardian recovers to a replacement key');
  await d.tx('attr-odometer-3', 'CVINVehicleAccount.setAttribute', acct.connect(vehicleOwner).setAttribute(ethers.id('cvin/vehicle/odometerKm'), ethers.toBeHex(30000, 32)), 'life: odometer ROLLBACK to 30000 (fraud) — accepted, storage only holds the latest');

  await d.view('state-only-latest', 'CVINVehicleAccount.getAttribute', acct.getAttribute(ethers.id('cvin/vehicle/odometerKm')).then((v) => Number(BigInt(v))), 'current odometer reads 30000; the chain state cannot show the earlier 48000', (v) => assert.equal(v, 30000));
  const [attrs, guard, owners, recov, execs, ops] = await Promise.all([
    acct.queryFilter(acct.filters.AttributeChanged(), 0, 'latest'), acct.queryFilter(acct.filters.GuardianChanged(), 0, 'latest'),
    acct.queryFilter(acct.filters.OwnershipTransferred(), 0, 'latest'), acct.queryFilter(acct.filters.OwnerRecovered(), 0, 'latest'),
    acct.queryFilter(acct.filters.Executed(), 0, 'latest'), ep.queryFilter(ep.filters.UserOperationHandled(null, id), 0, 'latest'),
  ]);
  assert.equal(attrs.length, 4); assert.equal(guard.length, 1); assert.equal(owners.length, 1); assert.equal(recov.length, 1); assert.equal(execs.length, 1); assert.equal(ops.length, 1);
  const odo = attrs.filter((l) => l.args.key === ethers.id('cvin/vehicle/odometerKm')).map((l) => Number(BigInt(l.args.value)));
  assert.deepEqual(odo, [12000, 48000, 30000]);
  d.offchain('replay-attributes', 'CVINVehicleAccount.AttributeChanged', `${attrs.length} AttributeChanged logs; odometer series ${odo.join(' -> ')} exposes the rollback that storage hides — fraud detection is a log-replay job for the verifier`);
  d.offchain('replay-keys', 'CVINVehicleAccount.GuardianChanged+OwnershipTransferred+OwnerRecovered', `${guard.length} guardian change, ${owners.length} consensual rotation, ${recov.length} guardian recovery: the two rotation kinds are distinguishable only by event name`);
  d.offchain('replay-executions', 'CVINVehicleAccount.Executed + CVINMinimalEntryPoint.UserOperationHandled', `${execs.length} Executed, ${ops.length} UserOperationHandled for this sender (the entry point log is the only place the userOpHash appears)`);
  const timeline = [...attrs.map((l) => ({ b: l.blockNumber, t: 'attr' })), ...guard.map((l) => ({ b: l.blockNumber, t: 'guardian' })), ...owners.map((l) => ({ b: l.blockNumber, t: 'rotate' })), ...execs.map((l) => ({ b: l.blockNumber, t: 'execute' })), ...recov.map((l) => ({ b: l.blockNumber, t: 'recover' }))].sort((a, b) => a.b - b.b).map((x) => x.t);
  assert.deepEqual(timeline, ['attr', 'attr', 'guardian', 'attr', 'rotate', 'execute', 'recover', 'attr']);
  d.offchain('timeline', 'logs merged by block', timeline.join(' -> '));

  const res = await adapter.resolve(id);
  assert.equal(res.value.controller, vehicleOwner.address);
  assert.equal(res.value.attributes.length, 2);
  assert.equal(res.value.capabilityDelegation.length, 1);
  d.offchain('resolve-via-adapter', 'adapter.resolve (owner, guardian, entryPoint, nonces, AttributeChanged logs + getAttribute)', `DID document: ${res.value.id}, 2 attribute keys enumerated from logs, guardian listed under capabilityDelegation; MEASURED as resolve (gas 0)`);
});
