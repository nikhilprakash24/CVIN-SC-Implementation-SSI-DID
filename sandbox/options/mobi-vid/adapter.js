'use strict';
/**
 * MOBI VID adapter — wraps 1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol (artifact
 * "MOBIVIDRegistryV2": VID II lifecycle events) which extends MOBIVIDRegistry.sol (VID I birth
 * certificate) which extends the vehicle-profile ERC1056Registry.sol, behind the uniform
 * IdentityOption interface. Identity = an ERC-1056 identity address (the vehicle DID); id = that address.
 *
 * The adapter derives the vehicle identity address deterministically from the VIN
 * (address(uint160(keccak256("cvin-mobi-vid:" + vin)))) — a key-less DID whose ERC-1056 owner is the
 * first owner, exactly as registerVehicleBirth sets owners[vehicleIdentity] = firstOwner.
 *
 * Method -> contract function mapping (cited by the thesis as the per-option asymmetry note):
 *
 *   deploy            new MOBIVIDRegistryV2()              constructor (no args): deployer = registryAuthority and
 *                                                          auto-authorised manufacturer; allowedIssuers table initialised.
 *                                                          Setup txs (not counted in gasUsed, reported as setupGasUsed):
 *                                                          authorizeManufacturer(deployer) only if not already,
 *                                                          authorizeIssuer(deployer, SERVICE_CENTER) for addClaim.
 *   create            registerVehicleBirth(vehicleIdentity, vinHash=keccak256(vin), encryptedVIN(placeholder),
 *                                          birthCertHash, firstOwner=owner, birthAttributes="0x")   [authorised manufacturer]
 *                                                          MOBI VID I birth certificate; birthAttributes left empty to
 *                                                          mirror the benchmark's measured op (V1 overflow bug now fixed).
 *   changeController  transferVehicleOwnership(identity, newController, 0, "SANDBOX") [owner]  (K-3, merged 2026-10-06:
 *                                                          the public changeOwner reverts for born vehicles)
 *                                                          (DIDOwnerChanged only; no ownership-history record).
 *   addKeyOrDelegate  addDelegate(identity, bytes32(purpose), key, validitySeconds)   [owner]  inherited ERC-1056
 *                                                          (event-only). Returns keyId = "<id>:<purposeBytes32>:<key>".
 *   setAttribute      setAttribute(identity, bytes32(key), bytes(value), 365 days)   [owner]  inherited ERC-1056
 *                                                          attribute (event-only; name = encodeBytes32String(key) when
 *                                                          <= 31 chars else keccak256(key)).
 *   addClaim          recordLifecycleEvent(identity, EventType=topic, odometer=0, dataHash=keccak256(data),
 *                                          credentialHash=keccak256(signature|data), jurisdiction="SANDBOX")
 *                                                          [authorised issuer = deployer as SERVICE_CENTER]  MOBI VID II
 *                                                          event; stored struct. The issuer role gates which EventTypes
 *                                                          are allowed (SERVICE_CENTER: MAINTENANCE, REPAIR, MODIFICATION).
 *                                                          Returns claimId = eventId. attestEvent (multi-party, on-chain
 *                                                          EIP-191 verification) is a separate follow-up call, not wrapped.
 *   revoke(id)        revokeIdentity(identity)             [owner]  inherited ERC-1056 extension: permanent DID revocation
 *                                                          (decommissioning). The VID II DECOMMISSION event is not used
 *                                                          (needs MANUFACTURER/GOVERNMENT_DMV issuer).
 *   revoke(keyId)     revokeDelegate(identity, purpose, key)   [owner]
 *   revoke(eventId)   NotApplicable                       lifecycle events are append-only.
 *   transfer          transferVehicleOwnership(identity, to, odometer=0, authority="SANDBOX")   [owner]  appends an
 *                                                          odometer-stamped OwnershipTransfer record + ERC-1056 changeOwner.
 *   resolve           getIdentityInfo, getVehicleDID, vehicleExists, getVehicleBirth, lookupByVINHash, getOwnershipHistory,
 *                     getVehicleEvents, DIDDelegateChanged / DIDAttributeChanged logs (ERC-1056 document replay)
 *   signedOp          NotApplicable                       the base ERC1056Registry declares `nonce` but implements no
 *                                                          *Signed variants (no changeOwnerSigned / addDelegateSigned /
 *                                                          setAttributeSigned); attestEvent verifies a signature but is a
 *                                                          role-gated direct call by the attester, not delegated execution.
 */
const { NotApplicable } = require('../../lib/identity_option');

const CONTRACT = 'MOBIVIDRegistryV2';
const EVENT_TYPES = ['MAINTENANCE', 'REPAIR', 'ACCIDENT', 'RECALL', 'INSPECTION', 'MODIFICATION', 'THEFT_REPORT', 'RECOVERY', 'INSURANCE_CLAIM', 'REGISTRATION', 'DECOMMISSION'];
const ISSUER_ROLE = { NONE: 0, MANUFACTURER: 1, DEALER: 2, SERVICE_CENTER: 3, INSURANCE_COMPANY: 4, GOVERNMENT_DMV: 5, POLICE: 6, INSPECTION_STATION: 7, OWNER: 8 };
const ONE_YEAR = 365 * 24 * 60 * 60;

const NA = Object.freeze({
  signedOp:
    'no signed (meta-transaction) execution: the ERC1056Registry base declares nonce but implements no changeOwnerSigned/addDelegateSigned/setAttributeSigned; attestEvent verifies an EIP-191 signature but is a role-gated direct call by the attester (manifest lists this family as implemented via `nonce` only)',
  revokeEvent:
    'lifecycle events (MOBI VID II) are append-only; revocation is identity-level (revokeIdentity) or a DECOMMISSION event, not per-event',
});

class MobiVidAdapter {
  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.contract = null;
    this.address = null;
  }

  _signerFor(address) {
    const want = address.toLowerCase();
    for (const s of Object.values(this.signers)) if (s && s.address.toLowerCase() === want) return s;
    throw new Error(`${CONTRACT}: no signer available for current identity owner ${address}`);
  }

  async _asOwner(id) {
    const owner = await this.contract.identityOwner(id);
    return this.contract.connect(this._signerFor(owner));
  }

  _bytes32Name(key) {
    const e = this.ethers;
    if (typeof key === 'string' && e.isHexString(key, 32)) return key;
    const s = String(key);
    return e.toUtf8Bytes(s).length <= 31 ? e.encodeBytes32String(s) : e.keccak256(e.toUtf8Bytes(s));
  }

  _toBytes(value) {
    const e = this.ethers;
    if (value instanceof Uint8Array) return e.hexlify(value);
    if (typeof value === 'string' && e.isHexString(value)) return value;
    return e.hexlify(e.toUtf8Bytes(String(value)));
  }

  _identityFor(vin) {
    const e = this.ethers;
    return e.getAddress(e.dataSlice(e.keccak256(e.toUtf8Bytes(`cvin-mobi-vid:${vin}`)), 12));
  }

  static _eventType(topic) {
    if (typeof topic === 'string' && EVENT_TYPES.includes(topic.toUpperCase())) return EVENT_TYPES.indexOf(topic.toUpperCase());
    const n = Number(topic);
    if (!Number.isInteger(n) || n < 0 || n >= EVENT_TYPES.length) throw new Error(`${CONTRACT}: topic ${topic} is not a MOBI VID II EventType (0..${EVENT_TYPES.length - 1})`);
    return n;
  }

  async deploy() {
    const d = this.signers.deployer;
    const F = await this.ethers.getContractFactory(CONTRACT, d);
    this.contract = await F.deploy();
    await this.contract.waitForDeployment();
    const receipt = await this.contract.deploymentTransaction().wait();
    this.address = await this.contract.getAddress();

    let setupGasUsed = 0n;
    if (!(await this.contract.authorizedManufacturers(d.address))) {
      setupGasUsed += (await (await this.contract.connect(d).authorizeManufacturer(d.address)).wait()).gasUsed;
    }
    setupGasUsed += (await (await this.contract.connect(d).authorizeIssuer(d.address, ISSUER_ROLE.SERVICE_CENTER)).wait()).gasUsed;

    return { ok: true, address: this.address, receipt, gasUsed: receipt.gasUsed, setupGasUsed,
      note: 'deployer = registryAuthority + manufacturer (constructor) + SERVICE_CENTER issuer (setup tx)' };
  }

  async attach(address) {
    this.address = address;
    this.contract = await this.ethers.getContractAt(CONTRACT, address, this.signers.deployer);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner }) {
    const e = this.ethers;
    const id = this._identityFor(vin);
    const vinHash = e.keccak256(e.toUtf8Bytes(vin));
    const birthCertHash = e.keccak256(e.toUtf8Bytes(`cvin-birth-certificate:${vin}`));
    const tx = await this.contract.connect(this.signers.deployer).registerVehicleBirth(
      id, vinHash, 'encrypted:sandbox-placeholder', birthCertHash, owner, '0x',
    );
    const receipt = await tx.wait();
    return { ok: true, id, receipt, gasUsed: receipt.gasUsed, vinHash,
      note: 'registerVehicleBirth (VID I); identity address derived from VIN; birthAttributes empty' };
  }

  async changeController(id, newController) {
    // Review-2 K-3 (merged 2026-10-06): the public ERC-1056 changeOwner is closed for born
    // vehicles ("MOBIVID: use transferVehicleOwnership"), so a controller change on this option
    // IS an ownership transfer with its odometer-stamped history record.
    const receipt = await (await (await this._asOwner(id)).transferVehicleOwnership(id, newController, 0n, 'SANDBOX')).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'transferVehicleOwnership (K-3: changeOwner reverts for born vehicles); appends an OwnershipTransfer record + ERC-1056 DIDOwnerChanged' };
  }

  async addKeyOrDelegate(id, key, purpose, validitySeconds) {
    const purposeB32 = this._bytes32Name(purpose || 'veriKey');
    const receipt = await (await (await this._asOwner(id)).addDelegate(id, purposeB32, key, BigInt(validitySeconds || ONE_YEAR))).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, keyId: `${id}:${purposeB32}:${key}`, note: 'ERC-1056 addDelegate (event-only)' };
  }

  async setAttribute(id, key, value) {
    const receipt = await (await (await this._asOwner(id)).setAttribute(id, this._bytes32Name(key), this._toBytes(value), BigInt(ONE_YEAR))).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'ERC-1056 setAttribute (event-only, 1-year validity)' };
  }

  async addClaim(id, topic, data, signature) {
    const e = this.ethers;
    const eventType = MobiVidAdapter._eventType(topic);
    const issuer = this.signers.deployer;
    if (!(await this.contract.isAuthorizedIssuer(issuer.address, eventType))) {
      throw new Error(`${CONTRACT}: issuer role SERVICE_CENTER may not record ${EVENT_TYPES[eventType]} events (allowed: MAINTENANCE, REPAIR, MODIFICATION)`);
    }
    const dataHash = e.keccak256(this._toBytes(data || '0x'));
    const credentialHash = e.keccak256(this._toBytes(signature && signature !== '0x' ? signature : (data || '0x')));
    const tx = await this.contract.connect(issuer).recordLifecycleEvent(id, eventType, 0n, dataHash, credentialHash, 'SANDBOX');
    const receipt = await tx.wait();
    let eventId = null;
    for (const log of receipt.logs) {
      try { const p = this.contract.interface.parseLog(log); if (p && p.name === 'LifecycleEventRecorded') { eventId = p.args.eventId; break; } } catch (_) { /* foreign log */ }
    }
    return { ok: true, receipt, gasUsed: receipt.gasUsed, claimId: eventId,
      note: `recordLifecycleEvent(${EVENT_TYPES[eventType]}) by SERVICE_CENTER issuer; VC hash stored, signature not verified (attestEvent is separate)` };
  }

  async revoke(idOrKeyIdOrEventId) {
    const e = this.ethers;
    const s = String(idOrKeyIdOrEventId);
    if (s.includes(':')) {
      const [id, purposeB32, key] = s.split(':');
      const receipt = await (await (await this._asOwner(id)).revokeDelegate(id, purposeB32, key)).wait();
      return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'ERC-1056 revokeDelegate (validTo = now)' };
    }
    if (e.isHexString(s, 32)) return new NotApplicable(NA.revokeEvent);
    const receipt = await (await (await this._asOwner(s)).revokeIdentity(s)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'revokeIdentity: permanent DID revocation (DIDRevoked)' };
  }

  async transfer(id, to) {
    const receipt = await (await (await this._asOwner(id)).transferVehicleOwnership(id, to, 0n, 'SANDBOX')).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'transferVehicleOwnership: odometer-stamped OwnershipTransfer record + ERC-1056 changeOwner' };
  }

  async signedOp(/* id, op, signature */) { return new NotApplicable(NA.signedOp); }

  async resolve(id) {
    const e = this.ethers;
    const c = this.contract;
    const chainId = (await e.provider.getNetwork()).chainId;
    const now = BigInt((await e.provider.getBlock('latest')).timestamp);
    const [info, did, exists] = await Promise.all([c.getIdentityInfo(id), c.getVehicleDID(id), c.vehicleExists(id)]);
    const owner = info[0];
    let birth = null, ownershipHistory = [], events = [];
    if (exists) {
      const b = await c.getVehicleBirth(id);
      birth = { vinHash: b.vinHash, encryptedVIN: b.encryptedVIN, birthCertHash: b.birthCertHash, timestamp: Number(b.timestamp),
        manufacturer: b.manufacturer, firstOwner: b.firstOwner, blockNumber: Number(b.blockNumber) };
      ownershipHistory = (await c.getOwnershipHistory(id)).map((h) => ({ from: h.from, to: h.to, timestamp: Number(h.timestamp), odometer: Number(h.odometer), registrationAuthority: h.registrationAuthority }));
      events = [...(await c.getVehicleEvents(id))];
    }
    // ERC-1056 document replay: latest validTo per delegate / attribute wins; keep those still valid.
    const delegates = new Map();
    for (const l of await c.queryFilter(c.filters.DIDDelegateChanged(id), 0, 'latest')) {
      delegates.set(`${l.args.delegateType}:${l.args.delegate}`, { delegateType: l.args.delegateType, delegate: l.args.delegate, validTo: l.args.validTo });
    }
    const attributes = new Map();
    for (const l of await c.queryFilter(c.filters.DIDAttributeChanged(id), 0, 'latest')) {
      attributes.set(l.args.name, { name: l.args.name, value: l.args.value, validTo: l.args.validTo });
    }
    const decodeName = (b32) => { try { return e.decodeBytes32String(b32); } catch (_) { return b32; } };
    const vm = [{ id: `${did}#controller`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${chainId}:${owner}` }];
    for (const d of delegates.values()) if (d.validTo > now) {
      vm.push({ id: `${did}#delegate-${d.delegate.slice(2, 10)}`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${chainId}:${d.delegate}`, delegateType: decodeName(d.delegateType), validTo: Number(d.validTo) });
    }
    const service = [];
    const attrs = [];
    for (const a of attributes.values()) if (a.validTo > now) {
      const name = decodeName(a.name);
      let value; try { value = e.toUtf8String(a.value); } catch (_) { value = a.value; }
      attrs.push({ name, value, validTo: Number(a.validTo) });
      if (name.startsWith('did/svc/')) service.push({ id: `${did}#${name.slice('did/svc/'.length)}`, type: name.slice('did/svc/'.length), serviceEndpoint: value });
    }
    return { ok: true, note: `owner=${owner.slice(0, 8)}… registered=${exists} revoked=${info[2]} delegates=${vm.length - 1} attrs=${attrs.length} events=${events.length} transfers=${ownershipHistory.length}`, value: {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: owner,
      verificationMethod: vm,
      authentication: [vm[0].id],
      service,
      attributes: attrs,
      status: { registered: exists, revoked: info[2], revokedAt: Number(info[3]), lastChangedBlock: Number(info[1]) },
      birthCertificate: birth,
      ownershipHistory,
      lifecycleEventIds: events,
      option: 'mobi-vid', contract: this.address, identity: id, chainId: Number(chainId),
    } };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: true,
      setAttribute: true,
      addClaim: true,
      revoke: true,
      transfer: true,
      resolve: true,
      signedOp: NA.signedOp,
      capabilities: true,
      notes: [
        'changeController == ERC-1056 changeOwner; transfer == transferVehicleOwnership (adds odometer-stamped history record, then changeOwner).',
        'addClaim == recordLifecycleEvent (VID II) by the deployer authorised as SERVICE_CENTER (MAINTENANCE/REPAIR/MODIFICATION only); attestEvent not wrapped.',
        'revoke(id) == revokeIdentity; revoke("<id>:<purpose>:<key>") == revokeDelegate; revoke(eventId) not applicable (append-only).',
        'manifest marks "Delegated / signed execution" implemented via `nonce`, but no *Signed function exists on the base registry; adapter reports NotApplicable.',
      ],
    };
  }
}

module.exports = MobiVidAdapter;
