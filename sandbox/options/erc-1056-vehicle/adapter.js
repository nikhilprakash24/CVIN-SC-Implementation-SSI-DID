'use strict';
/**
 * ERC-1056 / vehicle profile adapter (slug: erc-1056-vehicle).
 *
 * Contract: 1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol (byte-identical to
 * cv2x-testbed/contracts/ERC1056Registry.sol, the registry behind erc1056_provider.py).
 * Identity id = the vehicle's own account address. Unlike the uPort registry this profile
 * keeps NO delegate storage (addDelegate is event-only) and adds an identity-level
 * revocation flag (revoked / revokedAt / DIDRevoked) that gates addDelegate/setAttribute.
 *
 * Creation is explicit: registerVehicle(vehicleIdentity, publicKey) is guarded by
 * onlyOwner(identity, msg.sender) and identityOwner defaults to the identity, so the
 * registration transaction MUST be sent from the vehicle's own account (self-sovereign
 * registration; see cv2x-testbed/scripts/deploy.js). registerVehicle is one setAttribute
 * of "did/pub/secp256k1/veriKey/base64" with 1-year validity; it refuses an identity that
 * already has an explicit owner or is revoked.
 *
 * Method -> contract function mapping (the thesis cites this table):
 *   deploy            ERC1056Registry()
 *   create            ERC1056Registry.registerVehicle(owner, publicKey) sent BY `owner`'s signer.
 *                     publicKey defaults to the account's uncompressed secp256k1 key when it
 *                     can be derived from the Hardhat mnemonic, else a 0x04-prefixed placeholder.
 *                     The VIN is not anchored (VIN linkage: not-applicable in the manifest);
 *                     it is reported in the note only.
 *   changeController  ERC1056Registry.changeOwner(identity, newOwner) sent by identityOwner(identity)
 *   addKeyOrDelegate  ERC1056Registry.addDelegate(identity, keccak256(purpose), key, validity) (event-only)
 *   setAttribute      ERC1056Registry.setAttribute(identity, keccak256(name), bytes(value), validity)
 *   addClaim          NotApplicable: no on-chain claim function; the manifest's Claims family is the
 *                     provider's off-chain W3C VC handling (update/get/revoke_credential in
 *                     cv2x-testbed/identity/erc1056_provider.py).
 *   revoke            bare id -> ERC1056Registry.revokeIdentity(identity) (the measured operation);
 *                     { id, delegate, purpose } -> revokeDelegate; { id, key, value } -> revokeAttribute
 *                     (both emit validTo = block.timestamp, i.e. "expired now").
 *   transfer          NotApplicable: no token; control moves with changeOwner (= changeController).
 *   signedOp          NotApplicable: the contract declares a `nonce` mapping but no *Signed
 *                     meta-transaction entry point (no changeOwnerSigned/addDelegateSigned/...);
 *                     the nonce is never consumed.
 *   resolve           on-chain reads only: getIdentityInfo (owner, lastChanged, isRevoked, revokedAt)
 *                     plus the event walk DIDOwnerChanged / DIDDelegateChanged / DIDAttributeChanged /
 *                     DIDRevoked along the changed -> previousChange chain (delegates and attributes
 *                     exist only as events in this profile).
 *   capabilities      mirrors manifest.yaml
 *
 * Not used: updateVehicleKey (key rotation = setAttribute of the same key name; use setAttribute).
 */
const { NotApplicable } = require('../../lib/identity_option');

const ONE_YEAR = 31536000;
const DEFAULT_MNEMONIC = 'test test test test test test test test test test test junk';
const KEY_NAME = 'did/pub/secp256k1/veriKey/base64';
const KNOWN_NAMES = [
  KEY_NAME, 'did/pub/secp256k1/veriKey', 'did/pub/Ed25519/veriKey', 'did/svc/telematics',
  'did/svc/CredentialService', 'did/vehicle/vin',
];

class Erc1056VehicleAdapter {
  static get slug() { return 'erc-1056-vehicle'; }

  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.registry = null;
    this._names = new Map();
    for (const n of KNOWN_NAMES) this._names.set(this._h(n), n);
  }

  // ---------- helpers ----------
  _h(s) { return this.ethers.keccak256(this.ethers.toUtf8Bytes(s)); }
  _b32(s) { return this.ethers.isHexString(s, 32) ? s : this._h(s); }
  _bytes(v) {
    if (v == null) return '0x';
    if (v instanceof Uint8Array) return this.ethers.hexlify(v);
    return this.ethers.isHexString(v) ? v : this.ethers.hexlify(this.ethers.toUtf8Bytes(String(v)));
  }
  _allSigners() { return Object.values(this.signers).flat().filter(Boolean); }
  _signerFor(addr, required = true) {
    const a = String(addr).toLowerCase();
    const s = this._allSigners().find((x) => x.address.toLowerCase() === a);
    if (!s && required) throw new Error(`erc-1056-vehicle: no local signer for ${addr}`);
    return s || null;
  }
  async _controllerSigner(id) { return this._signerFor(await this.registry.identityOwner(id)); }
  /** Public key of a Hardhat account, derived from the network's mnemonic (for registerVehicle). */
  _publicKeyFor(address) {
    const E = this.ethers;
    let h = null;
    try { h = typeof hre !== 'undefined' ? hre : global.hre; } catch (_) { /* no hre */ }
    let acc = null;
    try { acc = h.config.networks[h.network.name].accounts; } catch (_) { /* fall through */ }
    const want = String(address).toLowerCase();
    if (Array.isArray(acc)) {
      for (const k of acc) {
        const w = new E.Wallet(typeof k === 'string' ? k : k.privateKey);
        if (w.address.toLowerCase() === want) return w.signingKey.publicKey;
      }
      return null;
    }
    const cfg = acc && typeof acc === 'object' && acc.mnemonic
      ? acc : { mnemonic: DEFAULT_MNEMONIC, path: "m/44'/60'/0'/0", initialIndex: 0, count: 20, passphrase: '' };
    const path = cfg.path || "m/44'/60'/0'/0";
    for (let i = 0; i < (cfg.count || 20); i++) {
      const w = E.HDNodeWallet.fromPhrase(cfg.mnemonic, cfg.passphrase || '', `${path}/${(cfg.initialIndex || 0) + i}`);
      if (w.address.toLowerCase() === want) return w.signingKey.publicKey;
    }
    return null;
  }

  // ---------- interface ----------
  async deploy() {
    const F = await this.ethers.getContractFactory('ERC1056Registry', this.signers.deployer);
    this.registry = await F.deploy();
    const receipt = await this.registry.deploymentTransaction().wait();
    return { ok: true, address: await this.registry.getAddress(), gasUsed: receipt.gasUsed };
  }

  async attach(address) {
    this.registry = await this.ethers.getContractAt('ERC1056Registry', address, this.signers.deployer);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner, publicKey } = {}) {
    const id = owner || this.signers.vehicleOwner.address;
    const vehicleSigner = this._signerFor(id); // registerVehicle must come from the vehicle's own account
    const pk = publicKey || this._publicKeyFor(id) || ('0x04' + '00'.repeat(64));
    const receipt = await (await this.registry.connect(vehicleSigner).registerVehicle(id, pk)).wait();
    return {
      ok: true, id, receipt, gasUsed: receipt.gasUsed,
      note: `registerVehicle sent by the vehicle account (1-year ${KEY_NAME}); vin=${vin || '-'} not anchored (VIN linkage N/A)`,
    };
  }

  async changeController(id, newController) {
    const signer = await this._controllerSigner(id);
    const receipt = await (await this.registry.connect(signer).changeOwner(id, newController)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'changeOwner' };
  }

  async addKeyOrDelegate(id, key, purpose = 'veriKey', validitySeconds = ONE_YEAR) {
    const signer = await this._controllerSigner(id);
    const type = this._b32(purpose);
    const receipt = await (await this.registry.connect(signer).addDelegate(id, type, key, validitySeconds)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `addDelegate(${purpose}, ${validitySeconds}s) event-only` };
  }

  async setAttribute(id, key, value, validitySeconds = ONE_YEAR) {
    const signer = await this._controllerSigner(id);
    const name = this._b32(key);
    if (!this.ethers.isHexString(key, 32)) this._names.set(name, key);
    const receipt = await (await this.registry.connect(signer).setAttribute(id, name, this._bytes(value), validitySeconds)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'setAttribute (event-only)' };
  }

  async addClaim() {
    return new NotApplicable('no on-chain claim function; credentials are off-chain W3C VCs handled by erc1056_provider.py (update/get/revoke_credential)');
  }

  async revoke(target) {
    if (typeof target === 'object' && target !== null) {
      const signer = await this._controllerSigner(target.id);
      let receipt;
      if (target.delegate) {
        receipt = await (await this.registry.connect(signer).revokeDelegate(target.id, this._b32(target.purpose || 'veriKey'), target.delegate)).wait();
        return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'revokeDelegate' };
      }
      if (target.key) {
        receipt = await (await this.registry.connect(signer).revokeAttribute(target.id, this._b32(target.key), this._bytes(target.value))).wait();
        return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'revokeAttribute' };
      }
      target = target.id;
    }
    const signer = await this._controllerSigner(target);
    const receipt = await (await this.registry.connect(signer).revokeIdentity(target)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'revokeIdentity (identity-level, permanent)' };
  }

  async transfer() {
    return new NotApplicable('ERC-1056 has no token to transfer; control moves with changeOwner (changeController)');
  }

  async signedOp() {
    return new NotApplicable('ERC1056Registry declares a nonce mapping but exposes no *Signed meta-transaction entry point (no changeOwnerSigned / addDelegateSigned / setAttributeSigned)');
  }

  async resolve(id) {
    const E = this.ethers;
    const reg = this.registry;
    const provider = E.provider;
    const [info, net, latest] = await Promise.all([reg.getIdentityInfo(id), provider.getNetwork(), provider.getBlock('latest')]);
    const controller = info[0];
    const changed = info[1];
    const isRevoked = info[2];
    const revokedAt = info[3];
    const now = BigInt(latest.timestamp);
    const events = [];
    const seen = new Set();
    let block = changed;
    while (block !== 0n && !seen.has(block)) {
      seen.add(block);
      const b = Number(block);
      const [o, d, a, r] = await Promise.all([
        reg.queryFilter(reg.filters.DIDOwnerChanged(id), b, b),
        reg.queryFilter(reg.filters.DIDDelegateChanged(id), b, b),
        reg.queryFilter(reg.filters.DIDAttributeChanged(id), b, b),
        reg.queryFilter(reg.filters.DIDRevoked(id), b, b),
      ]);
      let prev = block;
      for (const ev of [...o, ...d, ...a]) { events.push(ev); if (ev.args.previousChange < prev) prev = ev.args.previousChange; }
      for (const ev of r) events.push(ev);
      // DIDRevoked carries no previousChange: if it was the only event in this block the chain is cut
      // here and we fall back to scanning the identity's earlier events once.
      if (prev === block && r.length && !o.length && !d.length && !a.length) {
        const [po, pd, pa] = await Promise.all([
          reg.queryFilter(reg.filters.DIDOwnerChanged(id), 0, b - 1),
          reg.queryFilter(reg.filters.DIDDelegateChanged(id), 0, b - 1),
          reg.queryFilter(reg.filters.DIDAttributeChanged(id), 0, b - 1),
        ]);
        events.push(...po, ...pd, ...pa);
        prev = 0n;
      }
      block = prev;
    }
    events.sort((x, y) => (x.blockNumber - y.blockNumber) || (x.index - y.index));
    const delegates = new Map();
    const attributes = new Map();
    const owners = [];
    for (const ev of events) {
      const n = ev.fragment.name;
      if (n === 'DIDDelegateChanged') delegates.set(`${ev.args.delegateType}|${ev.args.delegate}`, { type: ev.args.delegateType, delegate: ev.args.delegate, validTo: ev.args.validTo });
      else if (n === 'DIDAttributeChanged') attributes.set(`${ev.args.name}|${ev.args.value}`, { name: ev.args.name, value: ev.args.value, validTo: ev.args.validTo });
      else if (n === 'DIDOwnerChanged') owners.push({ owner: ev.args.owner, block: ev.blockNumber });
    }
    const did = `did:ethr:0x${net.chainId.toString(16)}:${id}`;
    const vm = [{ id: `${did}#controller`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${net.chainId}:${controller}` }];
    const authentication = [`${did}#controller`];
    const assertionMethod = [];
    let i = 0;
    for (const d of delegates.values()) {
      if (d.validTo <= now) continue;
      const vid = `${did}#delegate-${++i}`;
      const purpose = d.type === this._h('sigAuth') ? 'sigAuth' : d.type === this._h('veriKey') ? 'veriKey' : d.type;
      vm.push({ id: vid, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${net.chainId}:${d.delegate}`, purpose, validTo: d.validTo });
      (purpose === 'sigAuth' ? authentication : assertionMethod).push(vid);
    }
    const service = [];
    const attrs = {};
    for (const a of attributes.values()) {
      if (a.validTo <= now) continue;
      const name = this._names.get(a.name) || a.name;
      let value = a.value;
      try { value = E.toUtf8String(a.value); } catch (_) { /* keep hex */ }
      if (name.startsWith('did/svc/')) service.push({ id: `${did}#${name.slice(8)}`, type: name.slice(8), serviceEndpoint: value, validTo: a.validTo });
      else if (name.startsWith('did/pub/')) vm.push({ id: `${did}#${name.slice(8).replace(/\//g, '-')}`, type: name, controller: did, publicKeyHex: a.value, validTo: a.validTo });
      else attrs[name] = value;
    }
    const value = {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller,
      verificationMethod: vm,
      authentication,
      assertionMethod,
      service,
      status: { revoked: isRevoked, revokedAt },
      vehicle: { attributes: attrs },
      meta: { registry: await reg.getAddress(), changed, ownerHistory: owners, events: events.length },
    };
    return { ok: true, value, note: `controller=${controller.slice(0, 8)}… revoked=${isRevoked} delegates=${i} services=${service.length}` };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: true,
      setAttribute: true,
      addClaim: 'no on-chain claim function; credentials are off-chain VCs in erc1056_provider.py',
      revoke: true,
      transfer: 'no token; control moves via changeOwner',
      signedOp: 'nonce mapping only; no *Signed entry points',
      resolve: true,
      capabilities: true,
    };
  }
}

module.exports = Erc1056VehicleAdapter;
