'use strict';
/**
 * ERC-4337 — family "Attributes / data store" (manifest: implemented, not measured; the benchmark
 * records setAttribute direct and via the entry point as updateAttribute / updateAttributeVia4337).
 * ERC-725Y-flavoured bytes32 -> bytes store on the account: direct owner write (cold / warm
 * slot), the same write through a UserOperation (indirection overhead), reads, clears, guards,
 * and the entryPoint() binding that decides who may write.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-4337/demos/attributes.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-4337', 'attributes');

async function signedOp(ep, acct, signer, callData) {
  const sender = await acct.getAddress();
  const op = { sender, nonce: await ep.nonces(sender), initCode: '0x', callData, accountGasLimits: ethers.ZeroHash, preVerificationGas: 0, gasFees: ethers.ZeroHash, paymasterAndData: '0x', signature: '0x' };
  op.signature = await signer.signMessage(ethers.getBytes(await ep.getUserOpHash(op)));
  return op;
}

d.run(async () => {
  const [bundler, owner, stranger] = await ethers.getSigners();
  const { assert } = d;
  const ep = await (await ethers.getContractFactory('CVINMinimalEntryPoint', bundler)).deploy();
  await ep.waitForDeployment();
  const acct = await (await ethers.getContractFactory('CVINVehicleAccount', bundler)).deploy(await ep.getAddress(), owner.address);
  await acct.waitForDeployment();
  const K_VIN = ethers.id('cvin/vehicle/vin');
  const K_FW = ethers.id('cvin/vehicle/firmwareHash');
  const K_MAKE = ethers.id('cvin/vehicle/make');
  d.offchain('setup', 'CVINVehicleAccount.constructor', 'account deployed; keys are keccak256 of a namespaced name (ERC-725Y style), values are raw bytes');

  await d.view('entry-point', 'CVINVehicleAccount.entryPoint', acct.entryPoint(), 'who besides the owner may write: the immutable entry point (and the account itself via execute)', (v) => assert.equal(v, ep.target));
  await d.view('get-attribute-empty', 'CVINVehicleAccount.getAttribute', acct.getAttribute(K_VIN), 'unset key reads as empty bytes', (v) => assert.equal(v, '0x'));
  const r1 = await d.tx('set-vin-direct', 'CVINVehicleAccount.setAttribute', acct.connect(owner).setAttribute(K_VIN, ethers.toUtf8Bytes(VINS.volvo)),
    'MEASURED (updateAttribute, cold slot): owner binds the VIN as an attribute -> AttributeChanged(key, value); this is the ONLY VIN linkage this option has');
  assert.equal(ethers.toUtf8String(eventArgs(acct, r1, 'AttributeChanged').value), VINS.volvo);
  await d.view('get-vin', 'CVINVehicleAccount.getAttribute', acct.getAttribute(K_VIN).then(ethers.toUtf8String), 'read back as UTF-8', (v) => assert.equal(v, VINS.volvo));
  const r2 = await d.tx('set-vin-overwrite', 'CVINVehicleAccount.setAttribute', acct.connect(owner).setAttribute(K_VIN, ethers.toUtf8Bytes(VINS.volvo)), 'same value again: warm slot, cheaper than the cold first write (no validity, no history)');
  assert.ok(r2.gasUsed < r1.gasUsed);
  await d.tx('set-firmware-hash', 'CVINVehicleAccount.setAttribute', acct.connect(owner).setAttribute(K_FW, ethers.sha256(ethers.toUtf8Bytes('ecu-firmware-v4.2.1.bin'))), 'a 32-byte value: SHA-256 of the ECU firmware image (what a V2X verifier would compare against)');
  await d.tx('set-make', 'CVINVehicleAccount.setAttribute', acct.connect(owner).setAttribute(K_MAKE, ethers.toUtf8Bytes('Volvo')), 'free-form string attribute');

  const op = await signedOp(ep, acct, owner, acct.interface.encodeFunctionData('setAttribute', [K_MAKE, ethers.toUtf8Bytes('Volvo Cars')]));
  const r3 = await d.tx('set-make-via-userop', 'CVINMinimalEntryPoint.handleOp -> validateUserOp -> setAttribute', ep.connect(bundler).handleOp(op),
    `MEASURED (updateAttributeVia4337): the same write as a UserOperation; overhead vs the direct warm write = ${'see gasUsed'} (ecrecover + nonce + two external calls)`);
  d.offchain('indirection-overhead', 'CVINMinimalEntryPoint.handleOp', `userOp write ${r3.gasUsed} gas vs direct overwrite ${r2.gasUsed} gas: +${r3.gasUsed - r2.gasUsed} for the 4337 path (excludes real bundler/paymaster accounting)`);
  await d.view('get-make', 'CVINVehicleAccount.getAttribute', acct.getAttribute(K_MAKE).then(ethers.toUtf8String), 'value written through the entry point', (v) => assert.equal(v, 'Volvo Cars'));

  await d.reverts('set-attribute-unauthorised', 'CVINVehicleAccount.setAttribute', () => acct.connect(stranger).setAttribute(K_MAKE, '0x00'), 'not owner or entryPoint', 'third parties (issuers, inspectors) cannot write: every attribute is self-asserted by the vehicle');
  await d.tx('clear-attribute', 'CVINVehicleAccount.setAttribute', acct.connect(owner).setAttribute(K_FW, '0x'), 'clearing = writing empty bytes (no delete function, no revocation event distinct from a change)');
  await d.view('get-cleared', 'CVINVehicleAccount.getAttribute', acct.getAttribute(K_FW), 'empty again; indistinguishable from never-set', (v) => assert.equal(v, '0x'));
  d.offchain('no-enumeration', 'CVINVehicleAccount.getAttribute', 'asymmetry: keys cannot be enumerated on-chain; a resolver must replay AttributeChanged logs to learn which keys exist, then re-read each (what the adapter does)');
});
