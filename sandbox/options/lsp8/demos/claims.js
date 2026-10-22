'use strict';
/**
 * LSP8 — family "Claims / credentials" (manifest: implemented via the reserved DATA_KEY_INSPECTION
 * slot; the comparison measures the adapter's addClaim = setDataForTokenId(DATA_KEY_INSPECTION)).
 * LSP8 has no claim model: an attestation is bytes in a per-token data key, written by the
 * authority, with the issuer's signature STORED but never verified on-chain. This demo issues a
 * signed inspection off-chain, stores it, verifies it off-chain (what a verifier must do), shows
 * that a forged signature is stored just as happily, and clears the slot as revocation.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/claims.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');
const Lsp8Adapter = require('../adapter');

const d = demo('lsp8', 'claims');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, delegate, inspector, forger] = await ethers.getSigners();
  const { assert } = d;
  const adapter = new Lsp8Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await adapter.deploy();
  const c = adapter.contract;
  const { id: tokenId } = await adapter.create({ vin: VINS.volvo, owner: vehicleOwner.address });
  const K_INSP = await c.DATA_KEY_INSPECTION();
  d.offchain('setup', 'adapter.deploy + adapter.create', `collection + vehicle ${VINS.volvo} (tokenId ${tokenId.slice(0, 10)}…) via the adapter`);
  await d.view('reserved-key', 'CVINVehicleLSP8.DATA_KEY_INSPECTION', Promise.resolve(K_INSP), 'the contract reserves one well-known key for inspection attestations (its only nod to credentials)', (v) => assert.equal(v, ethers.id('CVIN_INSPECTION')));

  const inspection = { vin: VINS.volvo, result: 'PASS', date: '2026-10-04', station: 'TUEV-SUED-M-01', odometerKm: 51234 };
  const payload = ethers.toUtf8Bytes(JSON.stringify(inspection));
  const digest = ethers.keccak256(payload);
  const sig = await inspector.signMessage(ethers.getBytes(digest));
  d.offchain('inspector-signs', 'off-chain EIP-191 sign', `inspection station ${inspector.address.slice(0, 10)}… signs keccak256(payload) with the personal_sign envelope (scheme chosen by the application, not the contract)`);
  const coder = ethers.AbiCoder.defaultAbiCoder();
  const encoded = coder.encode(['bytes', 'bytes'], [payload, sig]);
  const r1 = await d.tx('store-attestation', 'CVINVehicleLSP8.setDataForTokenId', c.connect(deployer).setDataForTokenId(tokenId, K_INSP, encoded),
    'MEASURED (addDelegateOrClaim analogue): the AUTHORITY (not the inspector) stores abi.encode(payload, signature) under DATA_KEY_INSPECTION — the chain checks who wrote, not who signed');
  assert.equal(eventArgs(c, r1, 'TokenIdDataChanged').dataKey, K_INSP);
  const stored = await d.view('read-attestation', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(tokenId, K_INSP), 'raw bytes back', (v) => assert.equal(v, encoded));
  const [p2, s2] = coder.decode(['bytes', 'bytes'], stored);
  const recovered = ethers.verifyMessage(ethers.getBytes(ethers.keccak256(p2)), s2);
  assert.equal(recovered, inspector.address);
  assert.deepEqual(JSON.parse(ethers.toUtf8String(p2)), inspection);
  d.offchain('verify-offchain', 'off-chain ecrecover', `verifier decodes, recovers ${recovered.slice(0, 10)}… and must decide OFF-chain whether that address is a trusted inspection station (no on-chain issuer registry)`);

  const forged = coder.encode(['bytes', 'bytes'], [ethers.toUtf8Bytes(JSON.stringify({ ...inspection, result: 'PASS', odometerKm: 20000 })), await forger.signMessage('garbage')]);
  await d.tx('store-forged-attestation', 'CVINVehicleLSP8.setDataForTokenId', c.connect(deployer).setDataForTokenId(tokenId, K_INSP, forged), 'OBSERVATION: a payload with a signature by a random key over unrelated data is stored without complaint — veracity is entirely off-chain');
  const [p3, s3] = coder.decode(['bytes', 'bytes'], await c.getDataForTokenId(tokenId, K_INSP));
  const rec3 = ethers.verifyMessage(ethers.getBytes(ethers.keccak256(p3)), s3);
  assert.notEqual(rec3, inspector.address);
  d.offchain('verify-forged', 'off-chain ecrecover', `recovers ${rec3.slice(0, 10)}… (not the inspector): only a verifier that checks signatures catches it`);
  await d.reverts('inspector-cannot-write', 'CVINVehicleLSP8.setDataForTokenId', () => c.connect(inspector).setDataForTokenId(tokenId, K_INSP, encoded), 'caller is not the contract owner', 'the issuer of the claim has no write access; it must go through the authority');

  const claim = await adapter.addClaim(tokenId, 'inspection', payload, sig);
  d.offchain('add-claim-via-adapter', 'adapter.addClaim -> setDataForTokenId(DATA_KEY_INSPECTION)', `adapter path re-stores the genuine attestation (gas ${claim.gasUsed}); claimId ${claim.claimId.slice(0, 20)}…`);
  const claim2 = await adapter.addClaim(tokenId, 'insurance', ethers.toUtf8Bytes('ALLIANZ:POL-7781'), '0x');
  d.offchain('add-claim-custom-topic', 'adapter.addClaim -> setDataForTokenId(keccak256("CVIN_CLAIM/insurance"))', `non-inspection topics get a derived key (gas ${claim2.gasUsed}); one slot per topic, so a second insurance claim overwrites the first`);
  const rv = await adapter.revoke(claim.claimId);
  d.offchain('revoke-claim-via-adapter', 'adapter.revoke(claimId) -> setDataForTokenId(key, 0x)', `revocation = clearing the slot (gas ${rv.gasUsed}); no revocation event distinct from a data change`);
  await d.view('slot-cleared', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(tokenId, K_INSP), 'inspection slot empty', (v) => assert.equal(v, '0x'));
  d.offchain('no-claim-model', 'CVINVehicleLSP8', 'asymmetry: no topic/scheme/issuer fields, no signature check, one value per key — ERC-735-style claims are emulated by convention in the data store');
});
