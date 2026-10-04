'use strict';
/**
 * MOBI VID — family "Message signing / verification (off-chain hot path)" (manifest: implemented
 * via the Python provider's sign_message / verify_message in cv2x-testbed/identity/
 * mobi_vid_provider.py). No contract function is involved: this demo mirrors the provider's
 * scheme in JS — canonical JSON (sorted keys), SHA-256 digest, secp256k1 ECDSA over the RAW
 * digest (no EIP-191 envelope) — and then shows what the provider does NOT do: it verifies
 * against the public key EMBEDDED in the message, never against the chain. The second half shows
 * the chain-anchored check a verifier would need (identityOwner / delegate replay).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/offchain-messaging.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');

const d = demo('mobi-vid', 'offchain-messaging');

const canonical = (m) => JSON.stringify(m, Object.keys(m).sort());

d.run(async () => {
  const [authority, owner, telematics] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const vehicleKey = ethers.Wallet.createRandom();
  const vehicle = vehicleKey.address;
  const did = `did:ethr:0x7a69:${vehicle.toLowerCase()}`;
  await reg.registerVehicleBirth(vehicle, ethers.sha256(ethers.toUtf8Bytes(VINS.acura)), 'enc:placeholder', ethers.id('cert'), owner.address, '0x');
  d.offchain('setup', 'MOBIVIDRegistryV2.registerVehicleBirth', `vehicle ${did} born (key held by the vehicle, ERC-1056 owner = ${owner.address.slice(0, 10)}…)`);

  // ---- provider scheme: sign_message ----
  const message = { type: 'BSM', vin: VINS.acura, lat: 48.1351, lon: 11.582, speedKmh: 47, heading: 182, ts: 1759574400 };
  const digest = ethers.sha256(ethers.toUtf8Bytes(canonical(message)));
  const signature = vehicleKey.signingKey.sign(digest);
  const signed = { message, signature: signature.serialized, public_key: ethers.SigningKey.computePublicKey(vehicleKey.privateKey, false), vehicle_did: did, timestamp: Math.floor(Date.now() / 1000) };
  d.offchain('sign-message', 'provider.sign_message (mirrored)', `V2X BSM: digest = SHA-256(json.dumps(message, sort_keys=True)); ECDSA secp256k1 over the RAW digest (no EIP-191 prefix, no chain id); envelope carries message, signature (${ethers.dataLength(signature.serialized)} B), public_key (65 B uncompressed), vehicle_did, timestamp`);

  // ---- provider scheme: verify_message ----
  const verifyLikeProvider = (s) => {
    const h = ethers.sha256(ethers.toUtf8Bytes(canonical(s.message)));
    return ethers.recoverAddress(h, s.signature) === ethers.computeAddress(s.public_key);
  };
  assert.equal(verifyLikeProvider(signed), true);
  d.offchain('verify-message', 'provider.verify_message (mirrored)', 'verifier re-hashes the message and checks the signature against signed_message.public_key — a pure off-chain hot path (no RPC); cost is one hash + one ECDSA verify');
  const tampered = { ...signed, message: { ...message, speedKmh: 147 } };
  assert.equal(verifyLikeProvider(tampered), false);
  d.offchain('verify-tampered', 'provider.verify_message (mirrored)', 'a modified speed field breaks the digest: integrity holds');
  const impostor = ethers.Wallet.createRandom();
  const forged = { message, signature: impostor.signingKey.sign(digest).serialized, public_key: ethers.SigningKey.computePublicKey(impostor.privateKey, false), vehicle_did: did, timestamp: signed.timestamp };
  assert.equal(verifyLikeProvider(forged), true);
  d.offchain('verify-impostor-passes', 'provider.verify_message (mirrored)', 'POTENTIAL DEFECT: an impostor signs the same BSM with its OWN key and embeds its OWN public key while claiming the vehicle\'s DID — the provider\'s check passes because it never binds public_key to vehicle_did (no chain lookup)');

  // ---- what a chain-anchored verification must do ----
  const claimed = ethers.getAddress(forged.vehicle_did.split(':').pop());
  const signerAddr = ethers.recoverAddress(digest, forged.signature);
  const ownerOnChain = await d.view('identity-owner', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(claimed), 'step 1 of a real check: who controls the DID right now?', (v) => assert.equal(v, owner.address));
  const now = BigInt((await ethers.provider.getBlock('latest')).timestamp);
  const delegateLogs = await reg.queryFilter(reg.filters.DIDDelegateChanged(claimed), 0, 'latest');
  const validDelegates = new Map();
  for (const l of delegateLogs) validDelegates.set(l.args.delegate, l.args.validTo);
  const isAuthorised = (addr) => addr === ownerOnChain || addr === claimed || (validDelegates.get(addr) || 0n) > now;
  assert.equal(isAuthorised(signerAddr), false);
  d.offchain('chain-anchored-verify-impostor', 'MOBIVIDRegistryV2.identityOwner + DIDDelegateChanged replay', `recovered signer ${signerAddr.slice(0, 10)}… is neither the owner, the identity, nor a valid sigAuth delegate -> REJECT (what verify_message should have done)`);
  assert.equal(isAuthorised(ethers.recoverAddress(digest, signed.signature)), true);
  d.offchain('chain-anchored-verify-genuine', 'MOBIVIDRegistryV2.identityOwner + DIDDelegateChanged replay', 'the genuine message recovers to the identity address itself (did:ethr semantics: the address is a verification method) -> ACCEPT');
  await d.tx('add-telematics-delegate', 'MOBIVIDRegistryV2.addDelegate', reg.connect(owner).addDelegate(claimed, ethers.encodeBytes32String('sigAuth'), telematics.address, 3600n), 'the owner authorises a telematics unit key as sigAuth for one hour');
  const dsig = ethers.HDNodeWallet.fromPhrase('test test test test test test test test test test test junk', '', "m/44'/60'/0'/0/2").signingKey.sign(digest).serialized;
  assert.equal(ethers.recoverAddress(digest, dsig), telematics.address);
  const logs2 = await reg.queryFilter(reg.filters.DIDDelegateChanged(claimed), 0, 'latest');
  const vd2 = new Map(); for (const l of logs2) vd2.set(l.args.delegate, l.args.validTo);
  const now2 = BigInt((await ethers.provider.getBlock('latest')).timestamp);
  assert.ok((vd2.get(telematics.address) || 0n) > now2);
  d.offchain('chain-anchored-verify-delegate', 'MOBIVIDRegistryV2.DIDDelegateChanged replay', 'a BSM signed by the telematics key now verifies through the delegate list (validTo > now); when the hour passes it stops verifying with no further transaction — expiry is free');
  d.offchain('scheme-contrast', 'off-chain', 'cryptography contrast: provider = SHA-256 + raw-digest ECDSA (interoperable with non-EVM V2X stacks, replayable across contexts); attestEvent = keccak256 + EIP-191 envelope + domain separation; ERC-4337 = keccak256 userOpHash + EIP-191');
});
