'use strict';
/**
 * MOBI VID — family "Claims / credentials" (manifest: measured-in-comparison via attestEvent).
 * VID II: an authorised issuer with a ROLE records a lifecycle EVENT (the claim: event type +
 * odometer + IPFS data hash + VC hash + jurisdiction, stored on-chain, verified flag by role); any
 * other authorised party can ATTEST it with an EIP-191 signature that the contract recovers and
 * binds to (registry, chainId, vehicle, eventId) — the on-chain signature check added as a fix.
 * This demo authorises all 8 roles, records all 11 EventTypes each by a correct role, checks the
 * role matrix and the verified flag, exercises attestEvent positive/negative (foreign signer,
 * raw digest, unauthorised, nonexistent) and issuer revocation.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/claims.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('mobi-vid', 'claims');
const EVENT = { MAINTENANCE: 0, REPAIR: 1, ACCIDENT: 2, RECALL: 3, INSPECTION: 4, MODIFICATION: 5, THEFT_REPORT: 6, RECOVERY: 7, INSURANCE_CLAIM: 8, REGISTRATION: 9, DECOMMISSION: 10 };
const ROLE = { NONE: 0, MANUFACTURER: 1, DEALER: 2, SERVICE_CENTER: 3, INSURANCE_COMPANY: 4, GOVERNMENT_DMV: 5, POLICE: 6, INSPECTION_STATION: 7, OWNER: 8 };
const EVENT_NAMES = Object.keys(EVENT);
const ROLE_NAMES = Object.keys(ROLE);
/** EventType -> IssuerRoles allowed (from _initializeAllowedIssuers). */
const MATRIX = {
  MAINTENANCE: ['DEALER', 'SERVICE_CENTER', 'OWNER'], REPAIR: ['DEALER', 'SERVICE_CENTER'], ACCIDENT: ['POLICE', 'INSURANCE_COMPANY', 'OWNER'], RECALL: ['MANUFACTURER'],
  INSPECTION: ['INSPECTION_STATION', 'GOVERNMENT_DMV'], MODIFICATION: ['SERVICE_CENTER', 'OWNER'], THEFT_REPORT: ['POLICE', 'OWNER'], RECOVERY: ['POLICE'],
  INSURANCE_CLAIM: ['INSURANCE_COMPANY', 'OWNER'], REGISTRATION: ['GOVERNMENT_DMV'], DECOMMISSION: ['MANUFACTURER', 'GOVERNMENT_DMV'],
};
const VERIFIED_ROLES = ['MANUFACTURER', 'GOVERNMENT_DMV', 'POLICE', 'DEALER', 'INSPECTION_STATION'];

d.run(async () => {
  const signers = await ethers.getSigners();
  const [authority, owner, oem, dealer, serviceCenter, insurer, dmv, police, station] = signers;
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const regAddr = await reg.getAddress();
  const chainId = (await ethers.provider.getNetwork()).chainId;
  const vehicle = ethers.Wallet.createRandom().address;
  await reg.registerVehicleBirth(vehicle, ethers.sha256(ethers.toUtf8Bytes(VINS.hyundai)), 'enc:placeholder', ethers.id('cert'), owner.address, '0x');
  const bySigner = { MANUFACTURER: oem, DEALER: dealer, SERVICE_CENTER: serviceCenter, INSURANCE_COMPANY: insurer, GOVERNMENT_DMV: dmv, POLICE: police, INSPECTION_STATION: station, OWNER: owner };
  d.offchain('setup', 'MOBIVIDRegistryV2.registerVehicleBirth', `vehicle ${vehicle.slice(0, 10)}… born; 8 issuer accounts prepared`);

  // ---- issuer authorisation (all 8 roles) ----
  await d.reverts('authorise-none', 'MOBIVIDRegistryV2.authorizeIssuer', () => reg.connect(authority).authorizeIssuer(dealer.address, ROLE.NONE), 'Invalid role', 'NONE cannot be granted');
  await d.reverts('authorise-unauthorised', 'MOBIVIDRegistryV2.authorizeIssuer', () => reg.connect(dealer).authorizeIssuer(dealer.address, ROLE.DEALER), 'Only registry authority', 'only the registry authority appoints issuers');
  for (const role of ROLE_NAMES.slice(1)) {
    const r = await d.tx(`authorise-${role.toLowerCase()}`, 'MOBIVIDRegistryV2.authorizeIssuer', reg.connect(authority).authorizeIssuer(bySigner[role].address, ROLE[role]), `IssuerAuthorized(${role}) — one role per address`);
    assert.equal(Number(eventArgs(reg, r, 'IssuerAuthorized').role), ROLE[role]);
  }
  await d.view('authorized-issuers-raw', 'MOBIVIDRegistryV2.authorizedIssuers', reg.authorizedIssuers(police.address), 'raw mapping address -> role enum', (v) => assert.equal(Number(v), ROLE.POLICE));
  const matrix = [];
  for (const ev of EVENT_NAMES) for (const role of ROLE_NAMES.slice(1)) {
    const allowed = await reg.allowedIssuers(EVENT[ev], ROLE[role]);
    assert.equal(allowed, MATRIX[ev].includes(role), `${ev}/${role}`);
    if (allowed) matrix.push(`${ev}:${role}`);
  }
  d.offchain('allowed-issuers-matrix', 'MOBIVIDRegistryV2.allowedIssuers', `11 EventTypes x 8 roles read (88 views); ${matrix.length} allowed pairs match the constructor table, e.g. RECALL only MANUFACTURER, RECOVERY only POLICE, REGISTRATION only GOVERNMENT_DMV`);
  await d.view('is-authorized-issuer', 'MOBIVIDRegistryV2.isAuthorizedIssuer', Promise.all([reg.isAuthorizedIssuer(police.address, EVENT.THEFT_REPORT), reg.isAuthorizedIssuer(police.address, EVENT.RECALL), reg.isAuthorizedIssuer(signers[12].address, EVENT.MAINTENANCE)]),
    'role x event-type check used by the recordLifecycleEvent modifier (police: theft yes, recall no; unknown address: no)', (v) => assert.deepEqual(v, [true, false, false]));

  // ---- one event of every type by a correct role ----
  const plan = [
    ['MAINTENANCE', 'SERVICE_CENTER', 15000, 'DE-BY'], ['REPAIR', 'DEALER', 22000, 'DE-BY'], ['ACCIDENT', 'INSURANCE_COMPANY', 31000, 'DE-BY'], ['RECALL', 'MANUFACTURER', 31000, 'EU'],
    ['INSPECTION', 'INSPECTION_STATION', 45000, 'DE-BY'], ['MODIFICATION', 'OWNER', 47000, 'DE-BY'], ['THEFT_REPORT', 'POLICE', 52000, 'DE-BY'], ['RECOVERY', 'POLICE', 52500, 'AT-W'],
    ['INSURANCE_CLAIM', 'INSURANCE_COMPANY', 53000, 'DE-BY'], ['REGISTRATION', 'GOVERNMENT_DMV', 60000, 'DE-BY'], ['DECOMMISSION', 'GOVERNMENT_DMV', 180000, 'DE-BY'],
  ];
  const eventIds = {};
  for (const [ev, role, odo, juris] of plan) {
    const data = { vin: VINS.hyundai, type: ev, odometerKm: odo, jurisdiction: juris, issuer: role, date: '2026-10-04' };
    const dataHash = ethers.sha256(ethers.toUtf8Bytes(JSON.stringify(data)));
    const credentialHash = ethers.sha256(ethers.toUtf8Bytes(JSON.stringify({ '@context': 'https://www.w3.org/2018/credentials/v1', type: ['VerifiableCredential', `${ev}Credential`], credentialSubject: data })));
    const r = await d.tx(`record-${ev.toLowerCase()}`, 'MOBIVIDRegistryV2.recordLifecycleEvent', reg.connect(bySigner[role]).recordLifecycleEvent(vehicle, EVENT[ev], odo, dataHash, credentialHash, juris),
      `${ev} by ${role}${ev === 'MAINTENANCE' ? ' — MEASURED (updateAttribute)' : ''}: struct stored (issuer, odometer, SHA-256 data hash, SHA-256 VC hash, jurisdiction, verified=${VERIFIED_ROLES.includes(role)}) -> LifecycleEventRecorded`);
    const e = eventArgs(reg, r, 'LifecycleEventRecorded');
    eventIds[ev] = e.eventId;
    // NB: `reg.getEvent` would resolve to ethers' BaseContract.getEvent(key); address the contract function by signature.
    const stored = await reg['getEvent(address,bytes32)'](vehicle, e.eventId);
    assert.equal(stored.verified, VERIFIED_ROLES.includes(role), `${ev} verified flag`);
    assert.equal(stored.issuer, bySigner[role].address);
  }
  d.offchain('verified-flag', 'MOBIVIDRegistryV2.LifecycleEvent.verified', 'verified=true only for MANUFACTURER/GOVERNMENT_DMV/POLICE/DEALER/INSPECTION_STATION issuers; SERVICE_CENTER, INSURANCE_COMPANY and OWNER events are recorded as unverified');
  await d.reverts('record-wrong-role', 'MOBIVIDRegistryV2.recordLifecycleEvent', () => reg.connect(serviceCenter).recordLifecycleEvent(vehicle, EVENT.RECALL, 1, ethers.id('x'), ethers.id('y'), 'DE'), 'Not authorized to issue this event type', 'a service centre cannot issue a RECALL (role matrix enforced on-chain)');
  await d.reverts('record-no-role', 'MOBIVIDRegistryV2.recordLifecycleEvent', () => reg.connect(signers[12]).recordLifecycleEvent(vehicle, EVENT.MAINTENANCE, 1, ethers.id('x'), ethers.id('y'), 'DE'), 'Not authorized to issue this event type', 'unknown address');
  await d.reverts('record-unregistered-vehicle', 'MOBIVIDRegistryV2.recordLifecycleEvent', () => reg.connect(dealer).recordLifecycleEvent(signers[13].address, EVENT.REPAIR, 1, ethers.id('x'), ethers.id('y'), 'DE'), 'Vehicle not registered', 'events need a birth certificate');
  await d.tx('owner-role-on-any-vehicle', 'MOBIVIDRegistryV2.recordLifecycleEvent', (async () => {
    const other = ethers.Wallet.createRandom().address;
    await (await reg.registerVehicleBirth(other, ethers.sha256(ethers.toUtf8Bytes(VINS.volvo)), 'enc', ethers.id('c2'), dealer.address, '0x')).wait();
    return reg.connect(owner).recordLifecycleEvent(other, EVENT.MAINTENANCE, 1, ethers.id('x'), ethers.id('y'), 'DE');
  })(), 'OBSERVATION: the OWNER role is a registry-wide role, not checked against identityOwner(vehicle): an "owner" issuer can record owner events on a vehicle it does not own');

  // ---- attestEvent: multi-party, on-chain signature verification ----
  const accident = eventIds.ACCIDENT;
  const digest = (v, id) => ethers.solidityPackedKeccak256(['address', 'uint256', 'address', 'bytes32'], [regAddr, chainId, v, id]);
  const policeSig = await police.signMessage(ethers.getBytes(digest(vehicle, accident)));
  d.offchain('attester-signs', 'off-chain EIP-191 sign', 'police signs keccak256(abi.encodePacked(registry, chainId, vehicle, eventId)) under the "\\x19Ethereum Signed Message:\\n32" envelope — domain-separated against other registries, chains, vehicles and events');
  const r1 = await d.tx('attest-event', 'MOBIVIDRegistryV2.attestEvent', reg.connect(police).attestEvent(accident, vehicle, policeSig),
    'MEASURED (attestEvent): ECDSA.recover(toEthSignedMessageHash(digest), sig) must equal msg.sender; attestation {attester, role, signature, timestamp} stored -> EventAttested');
  const ae = eventArgs(reg, r1, 'EventAttested'); assert.equal(ae.attester, police.address); assert.equal(Number(ae.role), ROLE.POLICE);
  const ownerSig = await owner.signMessage(ethers.getBytes(digest(vehicle, accident)));
  await d.tx('attest-by-owner', 'MOBIVIDRegistryV2.attestEvent', reg.connect(owner).attestEvent(accident, vehicle, ownerSig), 'a second attester (OWNER role) on the same event: attestations accumulate');
  await d.view('get-event-attestations', 'MOBIVIDRegistryV2.getEventAttestations', reg.getEventAttestations(accident), 'both attestations with their stored signatures', (v) => { assert.equal(v.length, 2); assert.equal(v[0].signature, policeSig); assert.equal(v[1].attester, owner.address); });
  await d.view('event-attestations-raw', 'MOBIVIDRegistryV2.eventAttestations', reg.eventAttestations(accident, 0), 'raw getter (eventId, index)', (v) => assert.equal(v.attester, police.address));
  const recovered = ethers.verifyMessage(ethers.getBytes(digest(vehicle, accident)), (await reg.eventAttestations(accident, 0)).signature);
  assert.equal(recovered, police.address);
  d.offchain('reverify-offchain', 'off-chain ecrecover', 'a verifier can re-check the stored signature later without trusting the registry\'s role table at the time of attestation');
  await d.reverts('attest-foreign-signature', 'MOBIVIDRegistryV2.attestEvent', () => reg.connect(dmv).attestEvent(accident, vehicle, policeSig), 'Invalid attestation signature', 'DMV submits the police signature: recovered != msg.sender (the fix: before, any role-holder could store any bytes)');
  const rawSig = ethers.HDNodeWallet.fromPhrase('test test test test test test test test test test test junk', '', "m/44'/60'/0'/0/6").signingKey.sign(digest(vehicle, accident)).serialized;
  assert.equal(ethers.recoverAddress(digest(vehicle, accident), rawSig), signers[6].address);
  await d.reverts('attest-raw-digest', 'MOBIVIDRegistryV2.attestEvent', () => reg.connect(signers[6]).attestEvent(accident, vehicle, rawSig), 'Invalid attestation signature', 'the right key signing the RAW digest (no EIP-191 prefix) is rejected: the envelope is part of the scheme (signers[6] = dmv in this run)');
  const dealerSigWrongEvent = await dealer.signMessage(ethers.getBytes(digest(vehicle, eventIds.REPAIR)));
  await d.reverts('attest-signature-for-other-event', 'MOBIVIDRegistryV2.attestEvent', () => reg.connect(dealer).attestEvent(accident, vehicle, dealerSigWrongEvent), 'Invalid attestation signature', 'a signature over another eventId does not transfer (eventId is in the digest)');
  await d.reverts('attest-unauthorised', 'MOBIVIDRegistryV2.attestEvent', async () => reg.connect(signers[12]).attestEvent(accident, vehicle, await signers[12].signMessage(ethers.getBytes(digest(vehicle, accident)))), 'Not authorized to attest', 'a valid signature by an address with no role is refused');
  await d.reverts('attest-nonexistent', 'MOBIVIDRegistryV2.attestEvent', () => reg.connect(police).attestEvent(ethers.id('nope'), vehicle, policeSig), 'Event does not exist', 'eventId must exist for that vehicle');
  await d.reverts('attest-malformed', 'MOBIVIDRegistryV2.attestEvent', () => reg.connect(police).attestEvent(accident, vehicle, '0x1234'), 'ECDSAInvalidSignatureLength', 'OZ ECDSA rejects malformed signatures with a custom error');
  await d.tx('attest-same-party-twice', 'MOBIVIDRegistryV2.attestEvent', reg.connect(police).attestEvent(accident, vehicle, policeSig), 'OBSERVATION: the same attester can attest the same event repeatedly with the same signature (no per-attester dedup; the signature has no nonce)');

  // ---- issuer revocation ----
  const r2 = await d.tx('revoke-issuer', 'MOBIVIDRegistryV2.revokeIssuerAuthorization', reg.connect(authority).revokeIssuerAuthorization(insurer.address), 'authority revokes the insurer -> IssuerAuthorizationRevoked');
  assert.equal(eventArgs(reg, r2, 'IssuerAuthorizationRevoked').issuer, insurer.address);
  await d.reverts('revoked-issuer-cannot-record', 'MOBIVIDRegistryV2.recordLifecycleEvent', () => reg.connect(insurer).recordLifecycleEvent(vehicle, EVENT.INSURANCE_CLAIM, 1, ethers.id('x'), ethers.id('y'), 'DE'), 'Not authorized to issue this event type', 'locked out');
  await d.reverts('revoked-issuer-cannot-attest', 'MOBIVIDRegistryV2.attestEvent', async () => reg.connect(insurer).attestEvent(accident, vehicle, await insurer.signMessage(ethers.getBytes(digest(vehicle, accident)))), 'Not authorized to attest', 'locked out of attestation too');
  await d.view('revoked-issuer-events-survive', 'MOBIVIDRegistryV2.getEvent', reg['getEvent(address,bytes32)'](vehicle, accident), 'OBSERVATION: the insurer\'s ACCIDENT and INSURANCE_CLAIM events stay valid-looking (no per-event revocation; issuer status is not re-checked on read)', (v) => assert.equal(v.issuer, insurer.address));
  await d.reverts('revoke-issuer-twice', 'MOBIVIDRegistryV2.revokeIssuerAuthorization', () => reg.connect(authority).revokeIssuerAuthorization(insurer.address), 'Issuer not authorized', 'idempotence guard');
});
