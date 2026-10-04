"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

const SCHEME_ECDSA = 1;
const TOPIC = { VIN: 1n, MANUFACTURER: 2n, INSPECTION: 3n };
const PERMANENT_VALIDITY = (1n << 256n) - 1n - (1n << 40n);

/**
 * CVIN-Combined (the thesis hybrid): one shared contract = ERC-1056-style
 * event registry (every address is an identity; owner/delegates/attributes as
 * events with a `changed` chain) + ERC-735-style on-chain claims for the
 * safety-critical subset (issuer-signed over a RAW digest, verified at add time,
 * O(1) reads). Realisations:
 *  - C1 = manufacturer-signed VIN attestation claim (topic 1) anchored by the owner;
 *    C2 = C1 + manufacturer claim (topic 2) carrying the ABI-encoded VID-I fields
 *  - U3/D2 = event attributes (cheap); U1/U4 = changeOwner; U2/D1/R4 = delegates
 *  - credentials are issuer-signed claims (topic = uint(credHash)) anchored by the
 *    owner, revoked (sticky) by the issuer, checked with hasValidClaim (O(1))
 *  - no signed meta-tx entry points (U5 n/a); no VIN index (R2 n/a); no deactivate
 *    primitive (permanent "did/deactivated" attribute, as for ERC-1056)
 *  - R3 walks the ERC-1056 `changed` chain for DID events (claims do not advance
 *    it, K-6) plus one ClaimAdded/ClaimRemoved log query per identity; validity is
 *    judged against the latest block timestamp (revokeDelegate sets validTo = now)
 */
class CVINCombinedAdapter extends IdentityAdapter {
  static id = "cvin";
  static label = "CVIN-Combined";
  static family = "hybrid: event registry + on-chain claims (shared)";

  constructor(opts) {
    super(opts);
    Object.assign(this.unsupported, {
      R2_resolve_by_vin: "no on-chain VIN index (VIN lives in a claim; off-chain index assumed)",
      U5_meta_tx: "no signed entry point in the hybrid contract",
    });
    const { keccak256, toUtf8Bytes } = this.ethers;
    this.K = { veriKey: keccak256(toUtf8Bytes("veriKey")), attr: keccak256(toUtf8Bytes(this.payloads.attributeName)), deactivated: keccak256(toUtf8Bytes(this.payloads.deactivatedName)) };
  }

  async deploy() {
    const F = await this.ethers.getContractFactory("CVINCombinedIdentity", this.actors.deployer);
    const c = await F.deploy();
    await c.waitForDeployment();
    this.contracts = { reg: c };
    this.addr = await c.getAddress();
    return [{ name: "CVINCombinedIdentity", contract: c }];
  }
  _reg(signer) { return this.contracts.reg.connect(signer); }
  _digest(identity, topic, data) {
    return this.ethers.solidityPackedKeccak256(["address", "address", "uint256", "bytes"], [this.addr, identity, topic, data]);
  }
  _signRaw(signer, identity, topic, data) {
    const sig = signer.signingKey.sign(this._digest(identity, topic, data));
    return this.ethers.concat([sig.r, sig.s, this.ethers.toBeHex(sig.v, 1)]);
  }
  _claimId(issuer, topic) { return this.ethers.solidityPackedKeccak256(["address", "uint256"], [issuer, topic]); }

  async createIdentity(v, owner) {
    const m = this.actors.manufacturer;
    const data = this.ethers.toUtf8Bytes(v.vin);
    const tx = await this._reg(owner).addClaim(owner.address, TOPIC.VIN, SCHEME_ECDSA, m.address, this._signRaw(m, owner.address, TOPIC.VIN, data), data, "");
    return { txs: [tx], result: { did: owner.address, vin: v.vin, controller: owner, attrs: {} } };
  }
  async createIdentityWithAttributes(v, owner) {
    const { txs, result } = await this.createIdentity(v, owner);
    const m = this.actors.manufacturer;
    const data = this.ethers.AbiCoder.defaultAbiCoder().encode(
      ["string", "string", "uint16", "string", "string", "uint256", "string"],
      [v.make, v.model, v.year, v.color, v.engineNumber, v.manufacturingDate, v.autonomyLevel]
    );
    txs.push(await this._reg(owner).addClaim(owner.address, TOPIC.MANUFACTURER, SCHEME_ECDSA, m.address, this._signRaw(m, owner.address, TOPIC.MANUFACTURER, data), data, v.metadataURI));
    return { txs, result };
  }

  async resolveOwner(h) { return this.contracts.reg.identityOwner(h.did); }
  async resolveByVin() { this.notSupported("R2_resolve_by_vin"); }
  async verifyDelegate(h, key) { return this.contracts.reg.validDelegate(h.did, this.K.veriKey, key.address); }

  async resolveDocument(h) {
    const reg = this.contracts.reg;
    const iface = reg.interface;
    const topicId = this.ethers.zeroPadValue(h.did, 32);
    const [latest, head] = await Promise.all([this.ethers.provider.getBlock("latest"), reg.changed(h.did)]);
    const now = BigInt(latest.timestamp);
    let block = Number(head);
    const events = [];
    const visited = new Set();
    while (block > 0 && !visited.has(block)) {
      visited.add(block);
      const logs = await this.ethers.provider.getLogs({ address: this.addr, fromBlock: block, toBlock: block, topics: [null, topicId] });
      let prev = 0;
      for (const log of logs) {
        let p; try { p = iface.parseLog(log); } catch { continue; }
        if (!p || p.args.previousChange === undefined) continue; // claim events carry no previousChange (0n is a valid value)
        events.push({ name: p.name, args: p.args, blockNumber: Number(log.blockNumber), logIndex: Number(log.index) });
        const pc = Number(p.args.previousChange);
        if (pc < block && pc > prev) prev = pc;
      }
      block = prev;
    }
    events.sort((a, b) => a.blockNumber - b.blockNumber || a.logIndex - b.logIndex);
    const delegates = new Map(), attributes = new Map();
    for (const e of events) {
      if (e.name === "DIDDelegateChanged") {
        const k = `${e.args.delegateType}|${e.args.delegate}`;
        if (BigInt(e.args.validTo) > now) delegates.set(k, e.args.delegate); else delegates.delete(k);
      } else if (e.name === "DIDAttributeChanged") {
        if (BigInt(e.args.validTo) > now) attributes.set(e.args.name, e.args.value); else attributes.delete(e.args.name);
      }
    }
    // claims: one log query each for ClaimAdded / ClaimRemoved on this identity
    const [added, removed, owner] = await Promise.all([
      this.ethers.provider.getLogs({ address: this.addr, fromBlock: 0, toBlock: "latest", topics: [iface.getEvent("ClaimAdded").topicHash, null, topicId] }),
      this.ethers.provider.getLogs({ address: this.addr, fromBlock: 0, toBlock: "latest", topics: [iface.getEvent("ClaimRemoved").topicHash, null, topicId] }),
      reg.identityOwner(h.did),
    ]);
    const claimLog = [...added.map((l) => ({ ...iface.parseLog(l), block: Number(l.blockNumber), idx: Number(l.index) })), ...removed.map((l) => ({ ...iface.parseLog(l), block: Number(l.blockNumber), idx: Number(l.index) }))]
      .sort((a, b) => a.block - b.block || a.idx - b.idx);
    const claims = new Map();
    for (const p of claimLog) {
      if (p.name === "ClaimAdded") claims.set(p.args.claimId, { claimId: p.args.claimId, topic: p.args.topic.toString(), issuer: p.args.issuer, data: p.args.data, uri: p.args.uri });
      else claims.delete(p.args.claimId);
    }
    const doc = {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:cvin:31337:${h.did}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: [{ id: "#controller", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${owner}` }],
      authentication: ["#controller"],
      service: [],
      attributes: {},
      claims: [...claims.values()],
    };
    for (const d of delegates.values()) doc.verificationMethod.push({ id: `#delegate-${d}`, type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${d}` });
    for (const [name, value] of attributes) doc.attributes[name] = value;
    return doc;
  }

  async rotateController(h, newOwner) {
    const tx = await this._reg(h.controller).changeOwner(h.did, newOwner.address);
    h.controller = newOwner;
    return { txs: [tx] };
  }
  async transferVehicle(h, to) { return this.rotateController(h, to); }
  async addDelegate(h, key, ttl) {
    const tx = await this._reg(h.controller).addDelegate(h.did, this.K.veriKey, key.address, ttl);
    return { txs: [tx] };
  }
  async revokeDelegate(h, key) {
    const tx = await this._reg(h.controller).revokeDelegate(h.did, this.K.veriKey, key.address);
    return { txs: [tx] };
  }
  async setAttribute(h, name, value) {
    const nameHash = this.ethers.keccak256(this.ethers.toUtf8Bytes(name));
    const tx = await this._reg(h.controller).setAttribute(h.did, nameHash, this.ethers.toUtf8Bytes(value), this.payloads.ttlSeconds);
    h.attrs[name] = value;
    return { txs: [tx] };
  }
  async revokeAttribute(h, name) {
    const nameHash = this.ethers.keccak256(this.ethers.toUtf8Bytes(name));
    const tx = await this._reg(h.controller).revokeAttribute(h.did, nameHash, this.ethers.toUtf8Bytes(h.attrs[name] || ""));
    return { txs: [tx] };
  }
  async deactivate(h) {
    const tx = await this._reg(h.controller).setAttribute(h.did, this.K.deactivated, this.ethers.toUtf8Bytes("true"), PERMANENT_VALIDITY);
    return { txs: [tx] };
  }

  async anchorIssuerKey(issuer, key) {
    const tx = await this._reg(issuer).addDelegate(issuer.address, this.K.veriKey, key.address, this.payloads.ttlSeconds);
    return { txs: [tx] };
  }
  async anchorStatus(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const topic = BigInt(credHash);
    const data = this.ethers.getBytes(credHash);
    const tx = await this._reg(h.controller).addClaim(h.did, topic, SCHEME_ECDSA, issuer.address, this._signRaw(issuer, h.did, topic, data), data, "");
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const tx = await this._reg(issuer).removeClaim(h.did, this._claimId(issuer.address, BigInt(credHash)));
    return { txs: [tx] };
  }
  async statusCheck(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    return (await this.contracts.reg.hasValidClaim(h.did, BigInt(credHash), issuer.address)) ? "active" : "revoked";
  }

  async prepareThroughputSenders(senders) {
    return senders.map((s) => ({ sender: s, handle: { did: s.address, controller: s } }));
  }
  async throughputOp(entry, i, overrides) {
    return this._reg(entry.sender).setAttribute(entry.handle.did, this.K.attr, this.ethers.toUtf8Bytes(this.payloads.attributeValue), this.payloads.ttlSeconds, overrides);
  }
}

module.exports = { CVINCombinedAdapter, TOPIC };
