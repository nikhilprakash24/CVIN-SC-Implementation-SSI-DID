'use strict';
/**
 * LSP8 — family "Attributes / data store" (manifest: implemented, not measured; the comparison
 * measures one setDataForTokenId as updateAttribute). The ERC-725Y-style per-token key/value
 * store: well-known data keys, single and batch writes by the issuing authority, single and
 * batch reads, overwrite/clear semantics, the two events each write emits, and every guard.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/attributes.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, VINS } = require('./_lib');

const d = demo('lsp8', 'attributes');

d.run(async () => {
  const [authority, vehicleOwner] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleLSP8', authority)).deploy('CVIN Vehicle Identity LSP8', 'CVIN-LSP8');
  await c.waitForDeployment();
  await c.mintVehicle(vehicleOwner.address, VINS.hyundai);
  await c.mintVehicle(vehicleOwner.address, VINS.toyota);
  const t1 = await c.tokenIdForVIN(VINS.hyundai);
  const t2 = await c.tokenIdForVIN(VINS.toyota);
  d.offchain('setup', 'CVINVehicleLSP8.mintVehicle', 'two vehicles minted');

  const [K_VIN, K_REG, K_INSP, K_INS] = await Promise.all([c.DATA_KEY_VIN(), c.DATA_KEY_REGISTRATION(), c.DATA_KEY_INSPECTION(), c.DATA_KEY_INSURANCE()]);
  await d.view('well-known-keys', 'CVINVehicleLSP8.DATA_KEY_VIN+DATA_KEY_REGISTRATION+DATA_KEY_INSPECTION+DATA_KEY_INSURANCE', Promise.resolve([K_VIN, K_REG, K_INSP, K_INS]),
    'convenience constants = keccak256("CVIN_<NAME>"); any other bytes32 is also a valid key (LSP2-style open key space)',
    (v) => assert.deepEqual(v, [ethers.id('CVIN_VIN'), ethers.id('CVIN_REGISTRATION'), ethers.id('CVIN_INSPECTION'), ethers.id('CVIN_INSURANCE')]));
  await d.view('get-empty', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(t1, K_REG), 'unset key reads as empty bytes', (v) => assert.equal(v, '0x'));
  const r1 = await d.tx('set-registration', 'CVINVehicleLSP8.setDataForTokenId', c.connect(authority).setDataForTokenId(t1, K_REG, ethers.toUtf8Bytes('DE:B-CV 1234:2026-10-04')),
    'MEASURED (updateAttribute): authority writes a per-token key -> TokenIdDataChanged(tokenId, key, value) + DataChanged(key, value)');
  assert.equal(eventCount(c, r1, 'TokenIdDataChanged'), 1); assert.equal(eventCount(c, r1, 'DataChanged'), 1);
  assert.equal(eventArgs(c, r1, 'TokenIdDataChanged').dataKey, K_REG);
  await d.view('get-registration', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(t1, K_REG).then(ethers.toUtf8String), 'read back', (v) => assert.equal(v, 'DE:B-CV 1234:2026-10-04'));
  await d.tx('set-custom-key', 'CVINVehicleLSP8.setDataForTokenId', c.connect(authority).setDataForTokenId(t1, ethers.id('CVIN_ODOMETER_KM'), ethers.toBeHex(48210, 32)), 'custom key with a 32-byte uint value (odometer)');
  await d.tx('overwrite', 'CVINVehicleLSP8.setDataForTokenId', c.connect(authority).setDataForTokenId(t1, ethers.id('CVIN_ODOMETER_KM'), ethers.toBeHex(51000, 32)), 'overwrite: only the latest value is stored; no validity window, no history');
  await d.reverts('owner-cannot-write', 'CVINVehicleLSP8.setDataForTokenId', () => c.connect(vehicleOwner).setDataForTokenId(t1, K_INS, '0x01'), 'caller is not the contract owner', 'the vehicle owner cannot write its own token data: every attribute is authority-asserted (opposite of ERC-4337 where every attribute is self-asserted)');
  await d.reverts('write-nonexistent', 'CVINVehicleLSP8.setDataForTokenId', () => c.connect(authority).setDataForTokenId(ethers.id('nope'), K_INS, '0x01'), 'tokenId does not exist', 'existence check');

  const r2 = await d.tx('set-batch', 'CVINVehicleLSP8.setDataBatchForTokenIds', c.connect(authority).setDataBatchForTokenIds([t1, t2, t2], [K_INS, K_REG, K_INS], [ethers.toUtf8Bytes('ALLIANZ:POL-7781:2027-03-31'), ethers.toUtf8Bytes('DE:M-TY 9876:2026-10-04'), ethers.toUtf8Bytes('HUK:POL-0042:2027-01-15')]),
    'batch write across two tokens in one tx (one TokenIdDataChanged + DataChanged per entry)');
  assert.equal(eventCount(c, r2, 'TokenIdDataChanged'), 3);
  await d.view('get-batch', 'CVINVehicleLSP8.getDataBatchForTokenIds', c.getDataBatchForTokenIds([t1, t1, t2, t2], [K_VIN, K_INS, K_REG, K_INS]).then((vs) => vs.map(ethers.toUtf8String)),
    'batch read across tokens/keys', (v) => assert.deepEqual(v, [VINS.hyundai, 'ALLIANZ:POL-7781:2027-03-31', 'DE:M-TY 9876:2026-10-04', 'HUK:POL-0042:2027-01-15']));
  await d.reverts('set-batch-mismatch', 'CVINVehicleLSP8.setDataBatchForTokenIds', () => c.connect(authority).setDataBatchForTokenIds([t1], [K_INS, K_REG], ['0x01']), 'array length mismatch', 'guard');
  await d.reverts('get-batch-mismatch', 'CVINVehicleLSP8.getDataBatchForTokenIds', () => c.getDataBatchForTokenIds([t1], [K_INS, K_REG]), 'array length mismatch', 'guard');
  await d.reverts('set-batch-nonexistent', 'CVINVehicleLSP8.setDataBatchForTokenIds', () => c.connect(authority).setDataBatchForTokenIds([t1, ethers.id('nope')], [K_INS, K_INS], ['0x01', '0x01']), 'tokenId does not exist', 'whole batch reverts on one bad id (atomic)');
  await d.tx('clear', 'CVINVehicleLSP8.setDataForTokenId', c.connect(authority).setDataForTokenId(t1, K_INS, '0x'), 'clearing = writing empty bytes; a verifier cannot distinguish "never set" from "cleared" without the log');
  await d.view('get-cleared', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(t1, K_INS), 'empty', (v) => assert.equal(v, '0x'));
  await d.view('get-unknown-token', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(ethers.id('nope'), K_VIN), 'reads on nonexistent tokens do not revert (empty)', (v) => assert.equal(v, '0x'));
  d.offchain('no-enumeration', 'CVINVehicleLSP8.getDataForTokenId', 'asymmetry: keys cannot be enumerated on-chain (no LSP2 array keys here); the adapter replays TokenIdDataChanged logs to find them');
});
