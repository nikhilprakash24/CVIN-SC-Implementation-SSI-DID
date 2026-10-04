'use strict';
/**
 * MOBI VID — family "Attributes / data store" (manifest: implemented, not measured; the comparison's
 * updateAttribute is recordLifecycleEvent, not this). Inherited ERC-1056 attributes:
 * setAttribute / revokeAttribute are EVENT-ONLY (DIDAttributeChanged with validTo); there is no
 * getter, so a DID document is built by log replay. Shows naming conventions (bytes32 names,
 * did/pub & did/svc prefixes), validity windows, revocation, the PERMANENT constant and the
 * `changed` / `lastChanged` pointer.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/attributes.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('mobi-vid', 'attributes');

d.run(async () => {
  const [authority, owner, stranger] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const vehicle = ethers.Wallet.createRandom().address;
  await reg.registerVehicleBirth(vehicle, ethers.sha256(ethers.toUtf8Bytes(VINS.ford)), 'enc:placeholder', ethers.id('cert'), owner.address, '0x');
  const YEAR = 365n * 24n * 3600n;
  const name = (s) => (ethers.toUtf8Bytes(s).length <= 31 ? ethers.encodeBytes32String(s) : ethers.id(s));
  d.offchain('setup', 'MOBIVIDRegistryV2.registerVehicleBirth', 'vehicle born; attribute names: bytes32 (short names packed, long names keccak256 — the adapter\'s convention)');

  assert.equal(reg.interface.fragments.filter((f) => f.type === 'function' && /getAttribute|attributes/.test(f.name)).length, 0);
  d.offchain('no-getter', 'MOBIVIDRegistryV2 (ABI)', 'no getAttribute: attribute values exist only in DIDAttributeChanged logs (ERC-1056 design: cheap writes, verifier-side resolution)');
  await d.reverts('set-attribute-unauthorised', 'MOBIVIDRegistryV2.setAttribute', () => reg.connect(stranger).setAttribute(vehicle, name('did/svc/telematics'), ethers.toUtf8Bytes('https://x'), YEAR), 'Only owner can perform this action', 'owner-only: an issuer cannot attach data to a vehicle via attributes (that is what lifecycle events are for)');
  const r1 = await d.tx('set-service-endpoint', 'MOBIVIDRegistryV2.setAttribute', reg.connect(owner).setAttribute(vehicle, name('did/svc/telematics'), ethers.toUtf8Bytes('https://telematics.example/v/1'), YEAR),
    'did/svc/* attribute -> DID document service entry; DIDAttributeChanged(identity, name, value, validTo, previousChange); nothing stored');
  const e1 = eventArgs(reg, r1, 'DIDAttributeChanged');
  assert.equal(ethers.decodeBytes32String(e1.name), 'did/svc/telematics');
  assert.equal(e1.validTo, BigInt((await ethers.provider.getBlock(r1.blockNumber)).timestamp) + YEAR);
  await d.tx('set-public-key', 'MOBIVIDRegistryV2.setAttribute', reg.connect(owner).setAttribute(vehicle, name('did/pub/Secp256k1/veriKey/hex'), ethers.getBytes(ethers.SigningKey.computePublicKey(ethers.Wallet.createRandom().privateKey, true)), YEAR), 'did/pub/* attribute -> verificationMethod (33-byte compressed key as value)');
  const PERM = await reg.PERMANENT_ATTRIBUTE_VALIDITY();
  await d.tx('set-permanent', 'MOBIVIDRegistryV2.setAttribute', reg.connect(owner).setAttribute(vehicle, name('mobi/vid/colour'), ethers.toUtf8Bytes('Oxford White'), PERM), 'PERMANENT_ATTRIBUTE_VALIDITY (100y) as "forever" — type(uint256).max would panic in block.timestamp + validity');
  await d.tx('overwrite', 'MOBIVIDRegistryV2.setAttribute', reg.connect(owner).setAttribute(vehicle, name('did/svc/telematics'), ethers.toUtf8Bytes('https://telematics.example/v/2'), YEAR), 'same name again: the newer event supersedes the older in replay (nothing is overwritten on-chain)');
  await d.tx('set-expired', 'MOBIVIDRegistryV2.setAttribute', reg.connect(owner).setAttribute(vehicle, name('did/svc/diagnostics'), ethers.toUtf8Bytes('https://diag.example'), 0n), 'validity 0: validTo == now, i.e. already expired when mined (allowed)');
  await d.reverts('revoke-attribute-unauthorised', 'MOBIVIDRegistryV2.revokeAttribute', () => reg.connect(stranger).revokeAttribute(vehicle, name('mobi/vid/colour'), ethers.toUtf8Bytes('Oxford White')), 'Only owner can perform this action', 'owner-only');
  const r2 = await d.tx('revoke-attribute', 'MOBIVIDRegistryV2.revokeAttribute', reg.connect(owner).revokeAttribute(vehicle, name('mobi/vid/colour'), ethers.toUtf8Bytes('Oxford White')), 'revocation = DIDAttributeChanged with validTo = now; the VALUE must be repeated (the contract cannot look it up)');
  assert.equal(eventArgs(reg, r2, 'DIDAttributeChanged').validTo, BigInt((await ethers.provider.getBlock(r2.blockNumber)).timestamp));
  await d.tx('revoke-wrong-value', 'MOBIVIDRegistryV2.revokeAttribute', reg.connect(owner).revokeAttribute(vehicle, name('did/pub/Secp256k1/veriKey/hex'), ethers.toUtf8Bytes('not the key')), 'OBSERVATION: revoking with a DIFFERENT value is accepted; a replayer keyed by name alone will treat the key as revoked, one keyed by (name,value) will not — ambiguity left to the resolver');

  const now = BigInt((await ethers.provider.getBlock('latest')).timestamp);
  const logs = await reg.queryFilter(reg.filters.DIDAttributeChanged(vehicle), 0, 'latest');
  const latest = new Map();
  for (const l of logs) latest.set(l.args.name, { value: l.args.value, validTo: l.args.validTo });
  const current = [...latest.entries()].filter(([, v]) => v.validTo > now).map(([k, v]) => `${ethers.decodeBytes32String(k)}=${k === name('did/pub/Secp256k1/veriKey/hex') ? '<bytes>' : ethers.toUtf8String(v.value)}`);
  assert.deepEqual(current.sort(), ['did/svc/telematics=https://telematics.example/v/2'].sort());
  d.offchain('replay-attributes', 'MOBIVIDRegistryV2.DIDAttributeChanged (logs)', `${logs.length} attribute events; replay keyed by name, latest wins, keep validTo > now: ${JSON.stringify(current)} (colour revoked, diagnostics expired, key "revoked" by the wrong-value event)`);
  await d.view('changed', 'MOBIVIDRegistryV2.changed', reg.changed(vehicle), 'head of the previousChange chain: a resolver can walk backwards block by block instead of scanning all logs', (v) => assert.equal(v, BigInt(r2.blockNumber + 1)));
  await d.view('last-changed', 'MOBIVIDRegistryV2.lastChanged', reg.lastChanged(vehicle), 'same value via the view', (v) => assert.equal(v, BigInt(r2.blockNumber + 1)));
  await d.tx('revoke-identity', 'MOBIVIDRegistryV2.revokeIdentity', reg.connect(owner).revokeIdentity(vehicle), 'decommission');
  await d.reverts('set-after-revoke', 'MOBIVIDRegistryV2.setAttribute', () => reg.connect(owner).setAttribute(vehicle, name('x'), '0x01', YEAR), 'Identity is revoked', 'no new attributes on a revoked identity');
  await d.tx('revoke-after-revoke', 'MOBIVIDRegistryV2.revokeAttribute', reg.connect(owner).revokeAttribute(vehicle, name('did/svc/telematics'), ethers.toUtf8Bytes('https://telematics.example/v/2')), 'attribute revocation still allowed (cleanup)');
});
