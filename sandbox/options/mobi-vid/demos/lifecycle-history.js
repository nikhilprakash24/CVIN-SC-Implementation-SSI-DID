'use strict';
/**
 * MOBI VID — family "Lifecycle events / history" (manifest: measured-in-comparison via
 * recordLifecycleEvent, attestEvent, getCompleteHistory, changed). The richest on-chain history
 * of all options: stored event structs with per-type counters, ordered id lists, odometer series
 * and attestations, next to the ERC-1056 event chain. Exercises every history getter (checked and
 * raw), getCompleteHistory, getEventsByType, getOdometerHistory (and off-chain rollback
 * detection), the counters, and the ERC-1056 previousChange linked list.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/lifecycle-history.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('mobi-vid', 'lifecycle-history');
const EVENT = { MAINTENANCE: 0, REPAIR: 1, ACCIDENT: 2, INSPECTION: 4, REGISTRATION: 9 };

d.run(async () => {
  const [authority, owner, buyer, serviceCenter, police, station, dmv] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const regAddr = await reg.getAddress();
  const chainId = (await ethers.provider.getNetwork()).chainId;
  const vehicle = ethers.Wallet.createRandom().address;
  const vinHash = ethers.sha256(ethers.toUtf8Bytes(VINS.toyota));
  const rb = await (await reg.registerVehicleBirth(vehicle, vinHash, 'enc:placeholder', ethers.id('cert'), owner.address, '0x')).wait();
  await reg.authorizeIssuer(serviceCenter.address, 3); await reg.authorizeIssuer(police.address, 6); await reg.authorizeIssuer(station.address, 7); await reg.authorizeIssuer(dmv.address, 5);
  d.offchain('setup', 'MOBIVIDRegistryV2.registerVehicleBirth+authorizeIssuer', `vehicle born in block ${rb.blockNumber}; 4 issuers`);

  const rec = async (step, signer, type, odo, note) => {
    const r = await d.tx(step, 'MOBIVIDRegistryV2.recordLifecycleEvent', reg.connect(signer).recordLifecycleEvent(vehicle, type, odo, ethers.sha256(ethers.toUtf8Bytes(`${step}:${odo}`)), ethers.sha256(ethers.toUtf8Bytes(`vc:${step}`)), 'DE-BY'), note);
    return eventArgs(reg, r, 'LifecycleEventRecorded').eventId;
  };
  await d.view('complete-history-empty', 'MOBIVIDRegistryV2.getCompleteHistory', reg.getCompleteHistory(vehicle), 'MEASURED (view): (birth, eventCount=0, lastEvent=0x0)', (v) => { assert.equal(v.eventCount, 0n); assert.equal(v.lastEvent, ethers.ZeroHash); });
  const e1 = await rec('maintenance-15000', serviceCenter, EVENT.MAINTENANCE, 15000, 'life: first service');
  const e2 = await rec('registration-15100', dmv, EVENT.REGISTRATION, 15100, 'life: registered');
  const e3 = await rec('inspection-33000', station, EVENT.INSPECTION, 33000, 'life: inspection');
  await d.tx('sale-40000', 'MOBIVIDRegistryV2.transferVehicleOwnership', reg.connect(owner).transferVehicleOwnership(vehicle, buyer.address, 40000, 'KBA'), 'life: sold at 40000 km (odometer goes into the OwnershipTransfer record, NOT into the lifecycle events)');
  const e4 = await rec('accident-41000', police, EVENT.ACCIDENT, 41000, 'life: accident');
  const e5 = await rec('repair-28000', serviceCenter, EVENT.REPAIR, 28000, 'life: repair with a ROLLED-BACK odometer (accepted on-chain)');
  const e6 = await rec('maintenance-45000', serviceCenter, EVENT.MAINTENANCE, 45000, 'life: second service');
  const sig = await station.signMessage(ethers.getBytes(ethers.solidityPackedKeccak256(['address', 'uint256', 'address', 'bytes32'], [regAddr, chainId, vehicle, e4])));
  await d.tx('attest-accident', 'MOBIVIDRegistryV2.attestEvent', reg.connect(station).attestEvent(e4, vehicle, sig), 'MEASURED (attestEvent): inspection station co-signs the accident');

  await d.view('get-vehicle-events', 'MOBIVIDRegistryV2.getVehicleEvents', reg.getVehicleEvents(vehicle), 'ordered id list (checked getter)', (v) => assert.deepEqual([...v], [e1, e2, e3, e4, e5, e6]));
  await d.view('vehicle-event-ids-raw', 'MOBIVIDRegistryV2.vehicleEventIds', reg.vehicleEventIds(vehicle, 3), 'raw array getter (identity, index)', (v) => assert.equal(v, e4));
  await d.view('vehicle-event-count', 'MOBIVIDRegistryV2.vehicleEventCount', reg.vehicleEventCount(vehicle), 'counter', (v) => assert.equal(v, 6n));
  // NB: `reg.getEvent` would resolve to ethers' BaseContract.getEvent(key); address the contract function by signature.
  const getEvent = reg['getEvent(address,bytes32)'];
  await d.view('get-event', 'MOBIVIDRegistryV2.getEvent', getEvent(vehicle, e5), 'full struct: eventId, eventType, issuer, timestamp, odometer, dataHash, credentialHash, verified, jurisdiction, blockNumber',
    (v) => { assert.equal(Number(v.eventType), EVENT.REPAIR); assert.equal(v.issuer, serviceCenter.address); assert.equal(Number(v.odometer), 28000); assert.equal(v.verified, false); assert.equal(v.jurisdiction, 'DE-BY'); });
  await d.view('lifecycle-events-raw', 'MOBIVIDRegistryV2.lifecycleEvents', reg.lifecycleEvents(vehicle, e4), 'raw nested-mapping getter', (v) => { assert.equal(v.issuer, police.address); assert.equal(v.verified, true); });
  await d.reverts('get-event-unknown', 'MOBIVIDRegistryV2.getEvent', () => getEvent(vehicle, ethers.id('nope')), 'Event does not exist', 'checked');
  await d.reverts('get-events-unregistered', 'MOBIVIDRegistryV2.getVehicleEvents', () => reg.getVehicleEvents(buyer.address), 'Vehicle not registered', 'checked');
  await d.view('get-event-type-count', 'MOBIVIDRegistryV2.getEventTypeCount', Promise.all([reg.getEventTypeCount(vehicle, EVENT.MAINTENANCE), reg.getEventTypeCount(vehicle, EVENT.ACCIDENT), reg.getEventTypeCount(vehicle, 10)]), 'per-type counters: 2 maintenance, 1 accident, 0 decommission', (v) => assert.deepEqual(v, [2n, 1n, 0n]));
  await d.view('event-type-count-raw', 'MOBIVIDRegistryV2.eventTypeCount', reg.eventTypeCount(vehicle, EVENT.MAINTENANCE), 'raw getter', (v) => assert.equal(v, 2n));
  await d.view('get-events-by-type', 'MOBIVIDRegistryV2.getEventsByType', reg.getEventsByType(vehicle, EVENT.MAINTENANCE), 'filtered id list (linear scan on-chain, sized by the counter)', (v) => assert.deepEqual([...v], [e1, e6]));
  const odo = await d.view('get-odometer-history', 'MOBIVIDRegistryV2.getOdometerHistory', reg.getOdometerHistory(vehicle), '(readings[], timestamps[]) over lifecycle events only', (v) => assert.deepEqual(v[0].map(Number), [15000, 15100, 33000, 41000, 28000, 45000]));
  const readings = odo[0].map(Number);
  const rollbacks = readings.map((r, i) => (i > 0 && r < readings[i - 1] ? `${readings[i - 1]}->${r}` : null)).filter(Boolean);
  assert.deepEqual(rollbacks, ['41000->28000']);
  d.offchain('odometer-rollback-detection', 'off-chain scan of getOdometerHistory', `rollback(s) found: ${rollbacks.join(', ')} — the chain stores the series, the verifier does the fraud check; the 40000 km from the sale is NOT in this series (OwnershipTransfer records are a separate list)`);
  await d.view('complete-history', 'MOBIVIDRegistryV2.getCompleteHistory', reg.getCompleteHistory(vehicle), 'MEASURED (getCompleteHistory): (birth struct, eventCount=6, lastEvent=e6) — VID I + VID II in one call', (v) => { assert.equal(v.birth.vinHash, vinHash); assert.equal(v.eventCount, 6n); assert.equal(v.lastEvent, e6); });
  await d.reverts('complete-history-unregistered', 'MOBIVIDRegistryV2.getCompleteHistory', () => reg.getCompleteHistory(buyer.address), 'Vehicle not registered', 'checked');
  await d.view('ownership-history', 'MOBIVIDRegistryV2.getOwnershipHistory+getOwnershipHistoryCount', Promise.all([reg.getOwnershipHistory(vehicle), reg.getOwnershipHistoryCount(vehicle)]), 'the parallel ownership list (1 sale at 40000)', (v) => { assert.equal(v[1], 1n); assert.equal(Number(v[0][0].odometer), 40000); });

  // ---- ERC-1056 event chain ----
  const changed = await d.view('changed', 'MOBIVIDRegistryV2.changed', reg.changed(vehicle), 'MEASURED (view): block of the last ERC-1056 change (the sale\'s changeOwner)', (v) => assert.ok(v > BigInt(rb.blockNumber)));
  const chain = [];
  let block = changed;
  while (block > 0n) {
    const logs = (await Promise.all([reg.queryFilter(reg.filters.DIDOwnerChanged(vehicle), Number(block), Number(block)), reg.queryFilter(reg.filters.DIDAttributeChanged(vehicle), Number(block), Number(block)), reg.queryFilter(reg.filters.DIDDelegateChanged(vehicle), Number(block), Number(block)), reg.queryFilter(reg.filters.DIDRevoked(vehicle), Number(block), Number(block))])).flat();
    chain.push(`${block}:${logs.map((l) => l.fragment.name).join('+')}`);
    const prev = logs.find((l) => l.args.previousChange !== undefined);
    block = prev ? prev.args.previousChange : 0n;
  }
  assert.equal(chain.length, 2);
  d.offchain('walk-previous-change', 'MOBIVIDRegistryV2.DIDOwnerChanged.previousChange (logs)', `ERC-1056 linked list walked from changed(): ${chain.join(' <- ')} (sale, then birth) — only ERC-1056 events are chained; VID II events are not`);
  const [lifecycle, attested, transfers] = await Promise.all([reg.queryFilter(reg.filters.LifecycleEventRecorded(vehicle), 0, 'latest'), reg.queryFilter(reg.filters.EventAttested(e4), 0, 'latest'), reg.queryFilter(reg.filters.VehicleOwnershipTransferred(vehicle), 0, 'latest')]);
  assert.equal(lifecycle.length, 6); assert.equal(attested.length, 1); assert.equal(transfers.length, 1);
  d.offchain('replay-vid2-events', 'MOBIVIDRegistryV2.LifecycleEventRecorded+EventAttested+VehicleOwnershipTransferred', `${lifecycle.length} lifecycle, ${attested.length} attestation, ${transfers.length} transfer logs agree with storage: this option keeps history in BOTH storage and logs (most expensive, most queryable)`);
});
