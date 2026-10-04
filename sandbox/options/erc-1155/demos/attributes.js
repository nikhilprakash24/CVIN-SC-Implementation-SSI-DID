'use strict';
/**
 * ERC-1155 — family "Attributes / data store" (manifest: implemented, not measured; the comparison's
 * updateAttribute analogue is setTokenURI). The only writable "attribute" is the per-credential-TYPE
 * metadata URI: collection-wide, not per vehicle. Exercises setTokenURI, uri (default {id}
 * template vs override), the CredentialURIUpdated event and the never-emitted standard URI event.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/attributes.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, VINS } = require('./_lib');

const d = demo('erc-1155', 'attributes');

d.run(async () => {
  const [issuer, vehicleA, vehicleB] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  await c.registerVehicle(vehicleA.address, VINS.tesla);
  await c.registerVehicle(vehicleB.address, VINS.toyota);
  d.offchain('setup', 'CVINVehicleCredential1155.registerVehicle', 'two vehicles registered');

  await d.view('uri-default', 'CVINVehicleCredential1155.uri', c.uri(1), 'OZ base URI with the literal "{id}" placeholder: ERC-1155 clients substitute the hex id OFF-chain', (v) => assert.equal(v, 'ipfs://cvin-vehicle-credentials/{id}.json'));
  await d.view('uri-default-any-id', 'CVINVehicleCredential1155.uri', c.uri(999), 'same template for every id, even types that do not exist', (v) => assert.equal(v, 'ipfs://cvin-vehicle-credentials/{id}.json'));
  const r = await d.tx('set-token-uri', 'CVINVehicleCredential1155.setTokenURI', c.connect(issuer).setTokenURI(3, 'ipfs://cvin/inspection-cert-v2.json'),
    'MEASURED (updateAttribute analogue): per-credential-TYPE URI override, applies to every vehicle holding an INSPECTION_CERT');
  assert.equal(eventArgs(c, r, 'CredentialURIUpdated').newURI, 'ipfs://cvin/inspection-cert-v2.json');
  assert.equal(eventCount(c, r, 'URI'), 0);
  d.offchain('uri-event-never-emitted', 'CVINVehicleCredential1155.URI', 'OBSERVATION: the standard ERC-1155 URI(value,id) event (listed in the manifest) is never emitted; only the custom CredentialURIUpdated is — standard indexers will not notice the change');
  await d.view('uri-override', 'CVINVehicleCredential1155.uri', c.uri(3), 'override wins over the template', (v) => assert.equal(v, 'ipfs://cvin/inspection-cert-v2.json'));
  await d.view('uri-other-type-unchanged', 'CVINVehicleCredential1155.uri', c.uri(1), 'other types keep the template', (v) => assert.equal(v, 'ipfs://cvin-vehicle-credentials/{id}.json'));
  await d.tx('set-token-uri-overwrite', 'CVINVehicleCredential1155.setTokenURI', c.connect(issuer).setTokenURI(3, 'ipfs://cvin/inspection-cert-v3.json'), 'overwrite (no history on-chain beyond the event)');
  await d.tx('set-token-uri-clear', 'CVINVehicleCredential1155.setTokenURI', c.connect(issuer).setTokenURI(3, ''), 'empty string clears the override (falls back to the template)');
  await d.view('uri-cleared', 'CVINVehicleCredential1155.uri', c.uri(3), 'back to the template', (v) => assert.equal(v, 'ipfs://cvin-vehicle-credentials/{id}.json'));
  await d.tx('set-token-uri-unknown-type', 'CVINVehicleCredential1155.setTokenURI', c.connect(issuer).setTokenURI(42, 'ipfs://cvin/custom-type.json'), 'OBSERVATION: any uint256 is a valid credential type; no registry of types exists');
  await d.reverts('set-token-uri-unauthorised', 'CVINVehicleCredential1155.setTokenURI', () => c.connect(vehicleA).setTokenURI(1, 'ipfs://mine'), 'AccessControlUnauthorizedAccount', 'ISSUER_ROLE only; a vehicle cannot describe itself');
  d.offchain('no-per-vehicle-attributes', 'CVINVehicleCredential1155', 'asymmetry: there is no per-identity key/value store at all — vehicle A and vehicle B share every URI; per-vehicle facts must live in the (off-chain) credential documents');
});
