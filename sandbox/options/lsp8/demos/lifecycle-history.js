'use strict';
/**
 * LSP8 — family "Lifecycle events / history" (manifest: implemented via the DataChanged and
 * TokenIdDataChanged events). The contract stores only the latest value per key and the current
 * owner; history exists only in logs: TokenIdDataChanged / DataChanged (data), Transfer
 * (mint, moves, burn), VehicleMinted / VehicleRevoked, OwnershipTransferred (authority). This
 * demo lives a vehicle, replays the logs into a timeline and shows the adapter's resolve()
 * doing the same for data keys. Since the merge (K-8, 2026-10-06) revokeVehicle bumps the token's
 * data generation, so after the burn every getDataForTokenId read is empty and the odometer
 * rollback survives only in the logs — the chain's answer to the stale-data half of D12.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/lifecycle-history.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');
const Lsp8Adapter = require('../adapter');

const d = demo('lsp8', 'lifecycle-history');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const { assert } = d;
  const adapter = new Lsp8Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await adapter.deploy();
  const c = adapter.contract;
  const { id: t } = await adapter.create({ vin: VINS.ford, owner: vehicleOwner.address });
  const K_ODO = ethers.id('CVIN_ODOMETER_KM');
  const [K_REG, K_INSP] = await Promise.all([c.DATA_KEY_REGISTRATION(), c.DATA_KEY_INSPECTION()]);
  d.offchain('setup', 'adapter.deploy + adapter.create', `vehicle ${VINS.ford} minted`);

  await d.tx('registration', 'CVINVehicleLSP8.setDataForTokenId', c.setDataForTokenId(t, K_REG, ethers.toUtf8Bytes('DE:B-CV 1234')), 'life: registered');
  await d.tx('odometer-1', 'CVINVehicleLSP8.setDataForTokenId', c.setDataForTokenId(t, K_ODO, ethers.toBeHex(15000, 32)), 'life: odometer 15000');
  await d.tx('inspection', 'CVINVehicleLSP8.setDataForTokenId', c.setDataForTokenId(t, K_INSP, ethers.toUtf8Bytes('PASS 2025-04-01')), 'life: inspection');
  await d.tx('odometer-2', 'CVINVehicleLSP8.setDataForTokenId', c.setDataForTokenId(t, K_ODO, ethers.toBeHex(62000, 32)), 'life: odometer 62000');
  await d.tx('sale', 'CVINVehicleLSP8.transfer', c.connect(vehicleOwner).transfer(vehicleOwner.address, newOwner.address, t, true, '0x'), 'life: sold');
  await d.tx('odometer-3', 'CVINVehicleLSP8.setDataForTokenId', c.setDataForTokenId(t, K_ODO, ethers.toBeHex(40000, 32)), 'life: odometer ROLLBACK to 40000 (accepted — latest value wins)');
  await d.tx('re-registration', 'CVINVehicleLSP8.setDataBatchForTokenIds', c.setDataBatchForTokenIds([t, t], [K_REG, K_INSP], [ethers.toUtf8Bytes('DE:M-XY 777'), ethers.toUtf8Bytes('PASS 2026-10-04')]), 'life: re-registered and re-inspected in one batch');
  await d.tx('authority-handover', 'CVINVehicleLSP8.transferOwnership', c.transferOwnership(delegate.address), 'life: the issuing authority changes');

  await d.view('state-before-burn', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(t, K_ODO).then((v) => Number(BigInt(v))), 'state just before the burn: the odometer slot says 40000 (the rollback — latest value wins)', (v) => assert.equal(v, 40000));
  await d.tx('end-of-life', 'CVINVehicleLSP8.revokeVehicle', c.connect(newOwner).revokeVehicle(t, ethers.toUtf8Bytes('scrapped')), 'life: owner burns the identity; K-8: the token record\'s data generation is bumped');
  await d.view('state-after', 'CVINVehicleLSP8.exists+getDataForTokenId+getDataBatchForTokenIds', Promise.all([c.exists(t), c.getDataForTokenId(t, K_ODO), c.getDataBatchForTokenIds([t, t], [K_REG, K_INSP])]),
    'FIXED (K-8 / D12 second half): token gone AND every data read is empty — the generation bump retires the whole store (odometer, registration, inspection) in one SSTORE; the rollback value 40000 now exists only in TokenIdDataChanged logs', (v) => { assert.equal(v[0], false); assert.equal(v[1], '0x'); assert.deepEqual([...v[2]], ['0x', '0x']); });
  const [data, generic, transfers, minted, revoked, authority] = await Promise.all([
    c.queryFilter(c.filters.TokenIdDataChanged(t), 0, 'latest'), c.queryFilter(c.filters.DataChanged(), 0, 'latest'), c.queryFilter(c.filters.Transfer(null, null, null, t), 0, 'latest'),
    c.queryFilter(c.filters.VehicleMinted(t), 0, 'latest'), c.queryFilter(c.filters.VehicleRevoked(t), 0, 'latest'), c.queryFilter(c.filters.OwnershipTransferred(), 0, 'latest'),
  ]);
  assert.equal(data.length, 8); assert.equal(generic.length, 8); assert.equal(transfers.length, 3); assert.equal(minted.length, 1); assert.equal(revoked.length, 1); assert.equal(authority.length, 2);
  const odo = data.filter((l) => l.args.dataKey === K_ODO).map((l) => Number(BigInt(l.args.dataValue)));
  assert.deepEqual(odo, [15000, 62000, 40000]);
  d.offchain('replay-data', 'CVINVehicleLSP8.TokenIdDataChanged+DataChanged', `${data.length} TokenIdDataChanged for this token (incl. the VIN at mint) mirrored by ${generic.length} DataChanged (not token-indexed: useless for per-vehicle queries); odometer series ${odo.join(' -> ')} exposes the rollback — and since K-8 the logs are the ONLY place the burned vehicle's history survives (no generation is encoded in the events: a replayer must split the series at the Transfer-to-zero log)`);
  d.offchain('replay-transfers', 'CVINVehicleLSP8.Transfer+VehicleMinted+VehicleRevoked', `${transfers.length} Transfer logs for the token = mint (from 0), sale, burn (to 0) with force/data payloads; app-level VehicleMinted ${minted.length}, VehicleRevoked ${revoked.length}`);
  d.offchain('replay-authority', 'CVINVehicleLSP8.OwnershipTransferred', `${authority.length} authority events (constructor + handover): who could write data at each point in time is itself a log question`);
  const K_VIN = await c.DATA_KEY_VIN();
  const timeline = [...data.filter((l) => l.args.dataKey !== K_VIN).map((l) => ({ b: l.blockNumber, i: l.index, t: 'data' })), ...transfers.map((l) => ({ b: l.blockNumber, i: l.index, t: l.args.from === ethers.ZeroAddress ? 'mint' : l.args.to === ethers.ZeroAddress ? 'burn' : 'sale' })), ...authority.slice(1).map((l) => ({ b: l.blockNumber, i: l.index, t: 'authority' }))]
    .sort((a, b) => a.b - b.b || a.i - b.i).map((x) => x.t);
  assert.deepEqual(timeline, ['mint', 'data', 'data', 'data', 'data', 'sale', 'data', 'data', 'data', 'authority', 'burn']);
  d.offchain('timeline', 'logs merged by block', timeline.join(' -> '));

  const res = await adapter.resolve(t);
  assert.equal(res.value.status.exists, false);
  assert.equal(res.value.data.length, 4);
  assert.ok(res.value.data.every((x) => x.value === '0x'), 'all re-read values empty after the generation bump');
  d.offchain('resolve-via-adapter', 'adapter.resolve (exists, tokenOwnerOf, TokenIdDataChanged logs + getDataForTokenId, owner, name, symbol)', `DID document after burn: exists=false, ${res.value.data.length} data keys still enumerated from logs (VIN, registration, inspection, odometer) but every re-read value is empty (K-8): the resolver sees the key set the vehicle once had and must take the values from the logs`);
});
