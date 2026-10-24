'use strict';
/**
 * ERC-1056 / uPort-style adapter (slug: erc-1056-uport).
 *
 * Contracts (1_blockchain-identity/contracts/ERC1056):
 *   EthereumDIDRegistry      shared ERC-1056 registry, did:ethr semantics (event-based DID doc)
 *   CVINVehicleDIDRegistry   VIN wrapper: vinToDID / didToVIN, VehicleDIDCreated, vehicleOwnerOf
 * Identity id = the vehicle owner's address (in ERC-1056 the address IS the DID).
 *
 * IMPLICIT CREATION. In EthereumDIDRegistry every address already is a DID:
 * identityOwner(x) defaults to x, so an identity exists at 0 gas before any transaction
 * and changeOwner/addDelegate/setAttribute work on it immediately. create() below takes
 * the EXPLICIT, VIN-bound path (CVINVehicleDIDRegistry.createVehicleDID, which stores the
 * vin<->DID mapping and emits VehicleDIDCreated); pass { implicit: true } to create() to
 * take the 0-gas path. capabilities() reports implicitSupported: true.
 *
 * Method -> contract function mapping (the thesis cites this table):
 *   deploy            EthereumDIDRegistry() then CVINVehicleDIDRegistry(registry); gasUsed = sum.
 *                     The deployer is the wrapper's owner and first authorized manufacturer.
 *   create            CVINVehicleDIDRegistry.createVehicleDID(vin, owner, make, model, year, color,
 *                     engineNumber, manufacturingDate, autonomyLevel) [onlyAuthorizedManufacturer];
 *                     VIN is normalised to the 17 chars the contract requires.
 *                     { implicit: true } -> no call, { implicit: true, gasUsed: 0n }.
 *   changeController  EthereumDIDRegistry.changeOwner(identity, newOwner) sent by identityOwner(identity)
 *   addKeyOrDelegate  EthereumDIDRegistry.addDelegate(identity, keccak256(purpose), key, validitySeconds)
 *                     (purpose 'veriKey' | 'sigAuth' | any string; a bytes32 is used as-is)
 *   setAttribute      EthereumDIDRegistry.setAttribute(identity, keccak256(name), bytes(value), validity)
 *                     (event-only storage: DIDAttributeChanged; default validity 1 year)
 *   addClaim          NotApplicable: ERC-1056 stores no claims on-chain. The manifest's "Claims"
 *                     family is only the SVC_CREDENTIAL_SERVICE endpoint constant, i.e. a service
 *                     attribute pointing at off-chain credentials (use setAttribute for it).
 *   revoke            EthereumDIDRegistry.revokeDelegate(identity, type, delegate) or
 *                     revokeAttribute(identity, name, value). A bare identity id revokes the most
 *                     recent delegate/attribute this adapter added for it (ERC-1056 has no
 *                     identity-level revocation); explicit forms: { id, delegate, purpose } /
 *                     { id, key, value }.
 *   transfer          NotApplicable: no token; the DID is the address and control moves with
 *                     changeOwner (= changeController). CVINVehicleDIDRegistry.transferVehicleOwnership
 *                     exists but only after the owner hands ERC-1056 control to the wrapper.
 *   signedOp          EthereumDIDRegistry.changeOwnerSigned(identity, v, r, s, newOwner), relayed by
 *                     `deployer` (meta-transaction). The controller signs the RAW secp256k1 digest
 *                     keccak256(0x19 || 0x00 || registry || nonce[identityOwner] || identity ||
 *                     "changeOwner" || newOwner) -- no EIP-191 prefix -- exactly as in
 *                     test/ERC1056/EthereumDIDRegistry.test.js. With an empty signature the
 *                     adapter signs with the controller's key, derived from the Hardhat account
 *                     mnemonic (hre.config.networks.<net>.accounts, or the default test mnemonic).
 *                     Pass { op: 'changeOwner', newOwner } to pick the target (default: current
 *                     controller, i.e. a signed self-rotation that proves the path end-to-end).
 *   resolve           on-chain reads only: identityOwner, changed, nonce, validDelegate, plus the
 *                     did:ethr event walk (DIDOwnerChanged / DIDDelegateChanged / DIDAttributeChanged
 *                     following the changed -> previousChange chain) and the wrapper's
 *                     getVINFromDID / vehicleOwnerOf.
 *   capabilities      mirrors manifest.yaml (+ implicitSupported: true)
 *
 * Wrapper functions not used here (they require the wrapper to be the ERC-1056 owner of the
 * DID first): setVehicleAttributes, setServiceEndpoint, addVerificationDelegate,
 * revokeVerificationDelegate, transferVehicleOwnership, updateOwnershipMapping.
 */
const { NotApplicable } = require('../../lib/identity_option');

const ONE_YEAR = 31536000;
const DEFAULT_MNEMONIC = 'test test test test test test test test test test test junk';
const KNOWN_NAMES = [
  'did/pub/secp256k1/veriKey', 'did/pub/secp256k1/veriKey/base64', 'did/pub/Ed25519/veriKey',
  'did/pub/secp256k1/sigAuth', 'did/svc/telematics', 'did/svc/CredentialService',
  'did/svc/MessagingService', 'did/svc/TelemetryService', 'did/vehicle/vin', 'did/vehicle/make',
  'did/vehicle/model', 'did/vehicle/year', 'did/vehicle/color', 'did/vehicle/engineNumber',
  'did/vehicle/manufacturingDate', 'did/vehicle/autonomyLevel',
];

class Erc1056UportAdapter {
  static get slug() { return 'erc-1056-uport'; }

  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.registry = null;   // EthereumDIDRegistry
    this.wrapper = null;    // CVINVehicleDIDRegistry
    this._revocables = new Map(); // id -> [{ kind, ... }] (what this adapter added; for bare-id revoke)
    this._names = new Map();      // keccak256(name) -> name (display aid for resolve)
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
    if (!s && required) throw new Error(`erc-1056-uport: no local signer for ${addr}`);
    return s || null;
  }
  async _controllerSigner(id) { return this._signerFor(await this.registry.identityOwner(id)); }
  _vin17(vin) {
    let v = String(vin || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (v.length > 17) v = v.slice(0, 12) + v.slice(-5);
    return v.padEnd(17, '0');
  }
  _track(id, item) {
    const k = id.toLowerCase();
    if (!this._revocables.has(k)) this._revocables.set(k, []);
    this._revocables.get(k).push(item);
  }
  /** Hardhat signers cannot sign raw digests; derive the matching key from the network's accounts. */
  _walletFor(address) {
    const E = this.ethers;
    const s = this._signerFor(address, false);
    if (s && s.privateKey) return new E.Wallet(s.privateKey);
    let h = null;
    try { h = typeof hre !== 'undefined' ? hre : global.hre; } catch (_) { /* no hre */ }
    if (!h) { try { h = require('hardhat'); } catch (_) { /* not resolvable from here */ } }
    let acc = null;
    try { acc = h.config.networks[h.network.name].accounts; } catch (_) { /* fall through */ }
    const want = String(address).toLowerCase();
    if (Array.isArray(acc)) {
      for (const k of acc) {
        const w = new E.Wallet(typeof k === 'string' ? k : k.privateKey);
        if (w.address.toLowerCase() === want) return w;
      }
      return null;
    }
    const cfg = acc && typeof acc === 'object' && acc.mnemonic
      ? acc : { mnemonic: DEFAULT_MNEMONIC, path: "m/44'/60'/0'/0", initialIndex: 0, count: 20, passphrase: '' };
    const path = cfg.path || "m/44'/60'/0'/0";
    const start = cfg.initialIndex || 0;
    const count = cfg.count || 20;
    for (let i = 0; i < count; i++) {
      const w = E.HDNodeWallet.fromPhrase(cfg.mnemonic, cfg.passphrase || '', `${path}/${start + i}`);
      if (w.address.toLowerCase() === want) return w;
    }
    return null;
  }

  // ---------- interface ----------
  async deploy() {
    const { deployer } = this.signers;
    const R = await this.ethers.getContractFactory('EthereumDIDRegistry', deployer);
    this.registry = await R.deploy();
    const r1 = await this.registry.deploymentTransaction().wait();
    const W = await this.ethers.getContractFactory('CVINVehicleDIDRegistry', deployer);
    this.wrapper = await W.deploy(await this.registry.getAddress());
    const r2 = await this.wrapper.deploymentTransaction().wait();
    return {
      ok: true,
      address: await this.wrapper.getAddress(),
      registryAddress: await this.registry.getAddress(),
      gasUsed: r1.gasUsed + r2.gasUsed,
      note: `registry=${r1.gasUsed} wrapper=${r2.gasUsed}`,
    };
  }

  async attach({ registry, wrapper }) {
    this.registry = await this.ethers.getContractAt('EthereumDIDRegistry', registry, this.signers.deployer);
    this.wrapper = await this.ethers.getContractAt('CVINVehicleDIDRegistry', wrapper, this.signers.deployer);
    return { ok: true, address: wrapper, registryAddress: registry, gasUsed: 0n };
  }

  async create({ vin, owner, implicit = false, make = 'CVIN', model = 'Sandbox', year = 2026, color = 'n/a',
    engineNumber = 'ENG-0', manufacturingDate = 0, autonomyLevel = 'L0' } = {}) {
    const id = owner || this.signers.vehicleOwner.address;
    if (implicit) {
      return { ok: true, id, implicit: true, gasUsed: 0n, note: 'identity is the address; no transaction' };
    }
    const vin17 = this._vin17(vin);
    const tx = await this.wrapper.connect(this.signers.deployer).createVehicleDID(
      vin17, id, make, model, year, color, engineNumber, manufacturingDate, autonomyLevel);
    const receipt = await tx.wait();
    return {
      ok: true, id, receipt, gasUsed: receipt.gasUsed, vin: vin17,
      note: `createVehicleDID vin=${vin17}${vin17 !== vin ? ' (normalised to 17 chars)' : ''}; implicit 0-gas path also available`,
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
    this._track(id, { kind: 'delegate', type, delegate: key });
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `addDelegate(${purpose}, ${validitySeconds}s)` };
  }

  async setAttribute(id, key, value, validitySeconds = ONE_YEAR) {
    const signer = await this._controllerSigner(id);
    const name = this._b32(key);
    if (!this.ethers.isHexString(key, 32)) this._names.set(name, key);
    const bytes = this._bytes(value);
    const receipt = await (await this.registry.connect(signer).setAttribute(id, name, bytes, validitySeconds)).wait();
    this._track(id, { kind: 'attribute', name, value: bytes });
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'setAttribute (event-only)' };
  }

  async addClaim() {
    return new NotApplicable('ERC-1056 stores no claims on-chain; the Claims family is only the SVC_CREDENTIAL_SERVICE endpoint attribute (use setAttribute); credentials live off-chain');
  }

  async revoke(target) {
    let item;
    let id;
    if (typeof target === 'object' && target !== null) {
      id = target.id;
      if (target.delegate) item = { kind: 'delegate', type: this._b32(target.purpose || 'veriKey'), delegate: target.delegate };
      else if (target.key) item = { kind: 'attribute', name: this._b32(target.key), value: this._bytes(target.value) };
    } else {
      id = target;
      const list = this._revocables.get(String(id).toLowerCase()) || [];
      item = list.pop();
    }
    if (!id || !item) {
      return new NotApplicable('ERC-1056 has no identity-level revocation; nothing tracked to revoke for this id (revoke a delegate or attribute explicitly)');
    }
    const signer = await this._controllerSigner(id);
    let receipt;
    if (item.kind === 'delegate') {
      receipt = await (await this.registry.connect(signer).revokeDelegate(id, item.type, item.delegate)).wait();
    } else {
      receipt = await (await this.registry.connect(signer).revokeAttribute(id, item.name, item.value)).wait();
    }
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: item.kind === 'delegate' ? 'revokeDelegate' : 'revokeAttribute' };
  }

  async transfer() {
    return new NotApplicable('ERC-1056 has no token to transfer; the DID is the address and control moves with changeOwner (changeController)');
  }

  async signedOp(id, op = 'changeOwner', signature = '0x') {
    const E = this.ethers;
    const opName = typeof op === 'string' ? op : op.op;
    if (opName !== 'changeOwner') {
      return new NotApplicable(`signedOp '${opName}' not wired by this adapter (registry also offers setAttributeSigned/addDelegateSigned/revoke*Signed; only changeOwnerSigned is demonstrated)`);
    }
    const controller = await this.registry.identityOwner(id);
    const newOwner = (typeof op === 'object' && op.newOwner) || controller;
    const nonce = await this.registry.nonce(controller);
    const digest = E.solidityPackedKeccak256(
      ['bytes1', 'bytes1', 'address', 'uint256', 'address', 'string', 'address'],
      ['0x19', '0x00', await this.registry.getAddress(), nonce, id, 'changeOwner', newOwner]);
    let sig;
    let how;
    if (signature && signature !== '0x') {
      sig = E.Signature.from(signature);
      how = 'caller-supplied signature';
    } else {
      const wallet = this._walletFor(controller);
      if (!wallet) throw new Error(`erc-1056-uport: cannot derive a signing key for controller ${controller}`);
      sig = wallet.signingKey.sign(digest); // raw secp256k1 over the ERC-1056 digest, no EIP-191 prefix
      how = 'adapter-signed raw digest';
    }
    const relayer = this.signers.deployer;
    const receipt = await (await this.registry.connect(relayer).changeOwnerSigned(id, sig.v, sig.r, sig.s, newOwner)).wait();
    return {
      ok: true, receipt, gasUsed: receipt.gasUsed,
      note: `changeOwnerSigned relayed by ${relayer.address.slice(0, 8)}… (${how}; nonce ${nonce} -> newOwner ${newOwner.slice(0, 8)}…)`,
    };
  }

  async resolve(id) {
    const E = this.ethers;
    const reg = this.registry;
    const provider = E.provider;
    const [controller, changed, nonce, net, latest] = await Promise.all([
      reg.identityOwner(id), reg.changed(id), reg.nonce(id), provider.getNetwork(), provider.getBlock('latest'),
    ]);
    const now = BigInt(latest.timestamp);
    // did:ethr event walk: changed[id] -> previousChange -> ... -> 0
    const events = [];
    const seen = new Set();
    let block = changed;
    while (block !== 0n && !seen.has(block)) {
      seen.add(block);
      const b = Number(block);
      const [o, d, a] = await Promise.all([
        reg.queryFilter(reg.filters.DIDOwnerChanged(id), b, b),
        reg.queryFilter(reg.filters.DIDDelegateChanged(id), b, b),
        reg.queryFilter(reg.filters.DIDAttributeChanged(id), b, b),
      ]);
      let prev = block;
      for (const ev of [...o, ...d, ...a]) { events.push(ev); if (ev.args.previousChange < prev) prev = ev.args.previousChange; }
      block = prev;
    }
    events.sort((x, y) => (x.blockNumber - y.blockNumber) || (x.index - y.index));
    const delegates = new Map();
    const attributes = new Map();
    const owners = [];
    for (const ev of events) {
      if (ev.fragment.name === 'DIDDelegateChanged') {
        delegates.set(`${ev.args.delegateType}|${ev.args.delegate}`, { type: ev.args.delegateType, delegate: ev.args.delegate, validTo: ev.args.validTo });
      } else if (ev.fragment.name === 'DIDAttributeChanged') {
        attributes.set(`${ev.args.name}|${ev.args.value}`, { name: ev.args.name, value: ev.args.value, validTo: ev.args.validTo });
      } else if (ev.fragment.name === 'DIDOwnerChanged') {
        owners.push({ owner: ev.args.owner, block: ev.blockNumber });
      }
    }
    const did = `did:ethr:0x${net.chainId.toString(16)}:${id}`;
    const vm = [{ id: `${did}#controller`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${net.chainId}:${controller}` }];
    const authentication = [`${did}#controller`];
    const assertionMethod = [];
    let i = 0;
    for (const d of delegates.values()) {
      if (d.validTo <= now) continue;
      if (!(await reg.validDelegate(id, d.type, d.delegate))) continue;
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
    let vin = '';
    let vehicleOwner = controller;
    if (this.wrapper) {
      [vin, vehicleOwner] = await Promise.all([this.wrapper.getVINFromDID(id), this.wrapper.vehicleOwnerOf(id)]);
    }
    const value = {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller,
      verificationMethod: vm,
      authentication,
      assertionMethod,
      service,
      vehicle: { vin, vehicleOwner, attributes: attrs },
      meta: { registry: await reg.getAddress(), wrapper: this.wrapper ? await this.wrapper.getAddress() : null, changed, nonce, ownerHistory: owners, events: events.length },
    };
    return { ok: true, value, note: `controller=${controller.slice(0, 8)}… delegates=${i} services=${service.length} vin=${vin || '-'}` };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: true,
      setAttribute: true,
      addClaim: 'no on-chain claim storage in ERC-1056 (only the SVC_CREDENTIAL_SERVICE endpoint attribute)',
      revoke: true,
      transfer: 'no token; control moves via changeOwner',
      signedOp: true,
      resolve: true,
      capabilities: true,
      implicitSupported: true,
    };
  }
}

module.exports = Erc1056UportAdapter;
