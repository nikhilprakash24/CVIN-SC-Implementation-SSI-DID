'use strict';
/**
 * CVIN-Combined (ERC-1056 + ERC-735 hybrid) adapter (slug: cvin-combined).
 *
 * Contract: 1_blockchain-identity/contracts/CVINCombined/CVINCombinedIdentity.sol — one shared
 * registry that composes an ERC-1056-style event-based identity (identityOwner / changeOwner /
 * addDelegate / setAttribute, `changed` pointer) with ERC-735-style on-chain claim storage
 * whose issuer signature is verified at addClaim time. Identity id = the vehicle owner's
 * address: every address is an identity and owns itself until changeOwner, so creation is
 * implicit and costs 0 gas (the manifest marks "Identity creation (explicit)" and "Off-chain
 * creation" not-applicable by the auto heuristic; the contract header and benchmark_ops say
 * implicit/zero-cost — reported as a manifest inconsistency).
 *
 * Claim signature scheme (test/CVINCombined/CVINCombinedIdentity.test.js): the issuer signs the
 * RAW digest keccak256(abi.encodePacked(registry, identity, topic, data)) with
 * signingKey.sign (no EIP-191 envelope); the contract recovers it with a bare ecrecover.
 * claimId = keccak256(abi.encodePacked(issuer, topic)). The adapter holds a local issuer
 * wallet (ethers.Wallet.createRandom, exposed as this.issuer) playing the manufacturer /
 * inspection authority; it only signs, it never sends transactions.
 *
 * Method -> contract function mapping (the thesis cites this table):
 *   deploy            CVINCombinedIdentity()
 *   create            no call: { ok, id: owner, implicit: true, gasUsed: 0n }. The VIN is not anchored
 *                     here; anchor it with addClaim(id, CLAIM_TOPIC_VIN=1, vin) (issuer-signed, O(1)
 *                     on-chain verifiable) or setAttribute(id, 'did/vehicle/vin', vin) (event-only).
 *                     create({ anchorVin: true }) does the addClaim and reports its gas.
 *   changeController  changeOwner(identity, newOwner) sent by identityOwner(identity)
 *   addKeyOrDelegate  addDelegate(identity, keccak256(purpose), key, validitySeconds) (storage + event)
 *   setAttribute      setAttribute(identity, keccak256(name), bytes(value), validity) (event-only)
 *   addClaim          addClaim(identity, topic, scheme=1, issuer, signature, data, uri) sent by
 *                     identityOwner. Empty signature -> adapter signs the raw digest with this.issuer;
 *                     otherwise issuer = opts.issuer or ethers.recoverAddress(digest, signature).
 *   revoke            bare id -> the most recent revocable this adapter created for it: a delegate ->
 *                     revokeDelegate(identity, type, delegate); a claim -> removeClaim(identity, claimId);
 *                     an attribute -> revokeAttribute(identity, name, value). Explicit forms:
 *                     { id, delegate, purpose } / { id, claimId } / { id, key, value }. No identity-level
 *                     revocation exists -> NotApplicable when nothing is known.
 *   transfer          NotApplicable: no token; control moves with changeOwner (= changeController)
 *   signedOp          NotApplicable: no *Signed meta-transaction entry points (the hybrid keeps the
 *                     ERC-1056 ownership model but not its signed variants); claim signatures are
 *                     verified on-chain in addClaim, which is issuer authorisation, not execution.
 *   resolve           on-chain reads only: identityOwner, changed, validDelegate, the event walk
 *                     (DIDOwnerChanged / DIDDelegateChanged / DIDAttributeChanged along
 *                     changed -> previousChange), getClaimIdsByTopic + getClaim for topics 1..3
 *                     (and any topic used through this adapter), hasValidClaim.
 *   capabilities      mirrors manifest.yaml
 */
const { NotApplicable } = require('../../lib/identity_option');

const ONE_YEAR = 31536000;
const SCHEME_ECDSA = 1;
const TOPICS = { 1: 'CLAIM_TOPIC_VIN', 2: 'CLAIM_TOPIC_MANUFACTURER', 3: 'CLAIM_TOPIC_INSPECTION' };
const KNOWN_NAMES = [
  'did/pub/secp256k1/veriKey', 'did/pub/Ed25519/veriKey', 'did/svc/telematics', 'did/svc/CredentialService',
  'did/vehicle/vin', 'did/vehicle/firmwareHash',
];

class CvinCombinedAdapter {
  static get slug() { return 'cvin-combined'; }

  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.registry = null;
    this.issuer = ethers.Wallet.createRandom(); // off-chain claim issuer (manufacturer role); signs only
    this._revocables = new Map();               // id -> [{ kind, ... }]
    this._topics = new Set([1, 2, 3]);
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
    if (!s && required) throw new Error(`cvin-combined: no local signer for ${addr}`);
    return s || null;
  }
  async _controllerSigner(id) { return this._signerFor(await this.registry.identityOwner(id)); }
  _track(id, item) {
    const k = String(id).toLowerCase();
    if (!this._revocables.has(k)) this._revocables.set(k, []);
    this._revocables.get(k).push(item);
  }
  async _claimDigest(id, topic, data) {
    return this.ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [await this.registry.getAddress(), id, topic, data]);
  }
  _claimId(issuer, topic) { return this.ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer, topic]); }

  // ---------- interface ----------
  async deploy() {
    const F = await this.ethers.getContractFactory('CVINCombinedIdentity', this.signers.deployer);
    this.registry = await F.deploy();
    const receipt = await this.registry.deploymentTransaction().wait();
    return { ok: true, address: await this.registry.getAddress(), gasUsed: receipt.gasUsed, note: 'single shared hybrid registry' };
  }

  async attach(address) {
    this.registry = await this.ethers.getContractAt('CVINCombinedIdentity', address, this.signers.deployer);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner, anchorVin = false } = {}) {
    const id = owner || this.signers.vehicleOwner.address;
    if (anchorVin && vin) {
      const r = await this.addClaim(id, 1, vin, '0x', { uri: 'cvin:vin' });
      return { ok: true, id, implicit: true, receipt: r.receipt, gasUsed: r.gasUsed, note: `identity implicit (0 gas); VIN anchored as CLAIM_TOPIC_VIN claim = ${r.gasUsed}` };
    }
    return { ok: true, id, implicit: true, gasUsed: 0n, note: `identity is the address (identityOwner defaults to self); vin=${vin || '-'} not anchored (use addClaim topic 1 or setAttribute)` };
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

  async addClaim(id, topic = 1, data = '0x', signature = '0x', opts = {}) {
    const E = this.ethers;
    const t = Number(topic);
    const bytes = this._bytes(data);
    const digest = await this._claimDigest(id, t, bytes);
    let sig = signature;
    let issuer = opts.issuer;
    let how;
    if (!sig || sig === '0x') {
      const wallet = opts.issuerWallet || this.issuer;
      sig = E.Signature.from(wallet.signingKey.sign(digest)).serialized; // raw digest, no EIP-191 prefix
      issuer = wallet.address;
      how = `issuer=${issuer.slice(0, 8)}… (adapter-signed raw digest)`;
    } else {
      if (!issuer) issuer = E.recoverAddress(digest, sig);
      how = `issuer=${issuer.slice(0, 8)}… (caller-supplied signature)`;
    }
    const signer = await this._controllerSigner(id);
    const receipt = await (await this.registry.connect(signer).addClaim(id, t, SCHEME_ECDSA, issuer, sig, bytes, opts.uri || '')).wait();
    const claimId = this._claimId(issuer, t);
    this._track(id, { kind: 'claim', claimId });
    this._topics.add(t);
    return { ok: true, receipt, gasUsed: receipt.gasUsed, value: claimId, claimId, note: `addClaim topic=${t} ${TOPICS[t] || ''} ${how}` };
  }

  async revoke(target) {
    let id;
    let item;
    if (typeof target === 'object' && target !== null) {
      id = target.id;
      if (target.delegate) item = { kind: 'delegate', type: this._b32(target.purpose || 'veriKey'), delegate: target.delegate };
      else if (target.claimId) item = { kind: 'claim', claimId: target.claimId };
      else if (target.key) item = { kind: 'attribute', name: this._b32(target.key), value: this._bytes(target.value) };
    } else {
      id = target;
      item = (this._revocables.get(String(id).toLowerCase()) || []).pop();
    }
    if (!id || !item) {
      return new NotApplicable('no identity-level revocation in the hybrid; revoke a delegate, claim or attribute (nothing known for this id — pass { id, delegate | claimId | key })');
    }
    const signer = await this._controllerSigner(id);
    const reg = this.registry.connect(signer);
    let receipt;
    let note;
    if (item.kind === 'delegate') { receipt = await (await reg.revokeDelegate(id, item.type, item.delegate)).wait(); note = 'revokeDelegate'; }
    else if (item.kind === 'claim') { receipt = await (await reg.removeClaim(id, item.claimId)).wait(); note = 'removeClaim (storage refund applies)'; }
    else { receipt = await (await reg.revokeAttribute(id, item.name, item.value)).wait(); note = 'revokeAttribute'; }
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note };
  }

  async transfer() {
    return new NotApplicable('no token in the hybrid; control moves with changeOwner (changeController)');
  }

  async signedOp() {
    return new NotApplicable('no *Signed meta-transaction entry points in CVINCombinedIdentity; issuer signatures are verified in addClaim (authorisation of a claim, not delegated execution)');
  }

  async resolve(id) {
    const E = this.ethers;
    const reg = this.registry;
    const provider = E.provider;
    const [controller, changed, net, latest] = await Promise.all([reg.identityOwner(id), reg.changed(id), provider.getNetwork(), provider.getBlock('latest')]);
    const now = BigInt(latest.timestamp);
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
      // addClaim/removeClaim also bump `changed` without an ERC-1056 event: if nothing links back
      // from this block, scan the identity's earlier ERC-1056 events once and stop.
      if (prev === block) {
        if (b > 0) {
          const [po, pd, pa] = await Promise.all([
            reg.queryFilter(reg.filters.DIDOwnerChanged(id), 0, b - 1),
            reg.queryFilter(reg.filters.DIDDelegateChanged(id), 0, b - 1),
            reg.queryFilter(reg.filters.DIDAttributeChanged(id), 0, b - 1),
          ]);
          events.push(...po, ...pd, ...pa);
        }
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
    const claims = [];
    let vin = '';
    for (const t of [...this._topics].sort((x, y) => x - y)) {
      for (const cid of await reg.getClaimIdsByTopic(id, t)) {
        const [topic, scheme, issuer, signature, data, uri] = await reg.getClaim(id, cid);
        let dataText = data;
        try { dataText = E.toUtf8String(data); } catch (_) { /* keep hex */ }
        const valid = await reg.hasValidClaim(id, Number(topic), issuer);
        claims.push({ claimId: cid, topic: Number(topic), topicName: TOPICS[Number(topic)] || String(topic), scheme: Number(scheme), issuer, signature, data, dataText, uri, valid });
        if (Number(topic) === 1 && !vin) vin = dataText;
      }
    }
    const value = {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller,
      verificationMethod: vm,
      authentication,
      assertionMethod,
      service,
      claims,
      vehicle: { vin, attributes: attrs },
      meta: { registry: await reg.getAddress(), changed, ownerHistory: owners, events: events.length },
    };
    return { ok: true, value, note: `controller=${controller.slice(0, 8)}… delegates=${i} services=${service.length} claims=${claims.length}` };
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
      transfer: 'no token; control moves via changeOwner',
      signedOp: 'no *Signed meta-transaction entry points',
      resolve: true,
      capabilities: true,
      implicitSupported: true,
    };
  }
}

module.exports = CvinCombinedAdapter;
