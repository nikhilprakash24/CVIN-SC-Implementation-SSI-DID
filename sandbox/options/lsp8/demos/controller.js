'use strict';
/**
 * LSP8 — family "Ownership / controller change" (manifest: implemented, not measured; the
 * comparison measures the 5-arg transfer as "transfer"/"controller-change"). Token ownership IS
 * control. Exercises tokenOwnerOf, the LSP8 transfer(from, to, tokenId, force, data) with both
 * force values (EOA vs contract recipients; LSP1 universal-receiver probing is OMITTED so a
 * code-bearing recipient is never asked), every transfer guard, tokenIdsOf bookkeeping, and the
 * separate collection-level transferOwnership (issuing authority hand-over).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/controller.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, deployEchoReceiver, VINS } = require('./_lib');

const d = demo('lsp8', 'controller');

d.run(async () => {
  const [authority, vehicleOwner, buyer, stranger, newAuthority] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleLSP8', authority)).deploy('CVIN Vehicle Identity LSP8', 'CVIN-LSP8');
  await c.waitForDeployment();
  const cAddr = await c.getAddress();
  await c.mintVehicle(vehicleOwner.address, VINS.vw);
  await c.mintVehicle(vehicleOwner.address, VINS.honda);
  const t1 = await c.tokenIdForVIN(VINS.vw);
  const t2 = await c.tokenIdForVIN(VINS.honda);
  const receiver = await deployEchoReceiver(authority);
  d.offchain('setup', 'CVINVehicleLSP8.mintVehicle', `two vehicles minted to vehicleOwner; a contract recipient (echo receiver) at ${receiver.address}`);

  await d.view('token-owner-of', 'CVINVehicleLSP8.tokenOwnerOf', c.tokenOwnerOf(t1), 'controller == token owner', (v) => assert.equal(v, vehicleOwner.address));
  await d.view('owner-authority', 'CVINVehicleLSP8.owner', c.owner(), 'collection owner = issuing authority, a different role from the vehicle controller', (v) => assert.equal(v, authority.address));
  await d.reverts('authority-cannot-move', 'CVINVehicleLSP8.transfer', () => c.connect(authority).transfer(vehicleOwner.address, buyer.address, t1, true, '0x'), 'caller is not the token owner', 'the authority can mint and revoke but NOT transfer a vehicle (no operators implemented)');
  await d.reverts('stranger-cannot-move', 'CVINVehicleLSP8.transfer', () => c.connect(stranger).transfer(vehicleOwner.address, buyer.address, t1, true, '0x'), 'caller is not the token owner', 'control enforced');
  await d.reverts('wrong-from', 'CVINVehicleLSP8.transfer', () => c.connect(vehicleOwner).transfer(buyer.address, stranger.address, t1, true, '0x'), 'transfer from incorrect owner', '`from` must be the owner');
  await d.reverts('to-zero', 'CVINVehicleLSP8.transfer', () => c.connect(vehicleOwner).transfer(vehicleOwner.address, ethers.ZeroAddress, t1, true, '0x'), 'transfer to zero address', 'burn only via revokeVehicle');
  await d.reverts('to-self', 'CVINVehicleLSP8.transfer', () => c.connect(vehicleOwner).transfer(vehicleOwner.address, vehicleOwner.address, t1, true, '0x'), 'cannot transfer to self', 'LSP8 forbids self-transfer (the adapter turns this into a no-op)');
  await d.reverts('force-false-to-eoa', 'CVINVehicleLSP8.transfer', () => c.connect(vehicleOwner).transfer(vehicleOwner.address, buyer.address, t1, false, '0x'), 'recipient is an EOA (use force=true)', 'LSP8 semantics: force=false refuses code-less recipients (meant to steer tokens to Universal Profiles)');

  const r1 = await d.tx('transfer-force-true', 'CVINVehicleLSP8.transfer', c.connect(vehicleOwner).transfer(vehicleOwner.address, buyer.address, t1, true, ethers.toUtf8Bytes('sale#2026-10-04')),
    'MEASURED (transferOwnership): owner moves vehicle 1 to the buyer with force=true and a data payload -> Transfer(operator, from, to, tokenId, force, data)');
  const ev = eventArgs(c, r1, 'Transfer'); assert.equal(ev.operator, vehicleOwner.address); assert.equal(ev.force, true); assert.equal(ethers.toUtf8String(ev.data), 'sale#2026-10-04');
  await d.view('owner-after', 'CVINVehicleLSP8.tokenOwnerOf', c.tokenOwnerOf(t1), 'buyer controls', (v) => assert.equal(v, buyer.address));
  await d.view('token-ids-of-both', 'CVINVehicleLSP8.tokenIdsOf', Promise.all([c.tokenIdsOf(vehicleOwner.address), c.tokenIdsOf(buyer.address)]), 'swap-and-pop enumeration updated on both sides', (v) => { assert.deepEqual([...v[0]], [t2]); assert.deepEqual([...v[1]], [t1]); });
  await d.tx('transfer-force-false-to-contract', 'CVINVehicleLSP8.transfer', c.connect(vehicleOwner).transfer(vehicleOwner.address, receiver.address, t2, false, '0x'),
    'force=false to a contract passes the code-length check; NO LSP1 universalReceiver call is made (hook omitted in this implementation)');
  await d.view('contract-owns', 'CVINVehicleLSP8.tokenOwnerOf', c.tokenOwnerOf(t2), 'a contract holds vehicle 2', (v) => assert.equal(v, receiver.address));
  await c.mintVehicle(vehicleOwner.address, VINS.acura);
  const t3 = await c.tokenIdForVIN(VINS.acura);
  await d.tx('transfer-force-false-to-collection', 'CVINVehicleLSP8.transfer', c.connect(vehicleOwner).transfer(vehicleOwner.address, cAddr, t3, false, '0x'),
    'OBSERVATION: force=false to the collection contract itself also succeeds — without LSP1 probing the force flag cannot protect against a recipient that can never move the token (vehicle 3 is now stuck)');
  await d.view('stuck', 'CVINVehicleLSP8.tokenOwnerOf', c.tokenOwnerOf(t3), 'owner is the collection; only revokeVehicle (authority) can get it out, by burning', (v) => assert.equal(v, cAddr));

  const r2 = await d.tx('transfer-authority', 'CVINVehicleLSP8.transferOwnership', c.connect(authority).transferOwnership(newAuthority.address), 'collection-level: issuing authority handed to a new address -> OwnershipTransferred (no vehicle changes hands)');
  assert.equal(eventArgs(c, r2, 'OwnershipTransferred').newOwner, newAuthority.address);
  await d.reverts('old-authority-mint', 'CVINVehicleLSP8.mintVehicle', () => c.connect(authority).mintVehicle(buyer.address, VINS.fiat), 'caller is not the contract owner', 'old authority lost minting');
  await d.tx('new-authority-mint', 'CVINVehicleLSP8.mintVehicle', c.connect(newAuthority).mintVehicle(buyer.address, VINS.fiat), 'new authority mints');
  await d.reverts('transfer-authority-zero', 'CVINVehicleLSP8.transferOwnership', () => c.connect(newAuthority).transferOwnership(ethers.ZeroAddress), 'new owner is zero address', 'no renounce: the authority can never be removed, only replaced');
  await d.reverts('transfer-authority-unauthorised', 'CVINVehicleLSP8.transferOwnership', () => c.connect(authority).transferOwnership(authority.address), 'caller is not the contract owner', 'guard');
});
