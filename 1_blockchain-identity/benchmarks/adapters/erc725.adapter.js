"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

const PURPOSE = { MANAGEMENT: 1, ACTION: 2, CLAIM: 3, ATTRIBUTE: 4, VIN: 5, STATUS: 6 };
const KEYTYPE_ECDSA = 1;

/**
 * ERC-725 (key-manager flavour on trunk): ONE CONTRACT PER IDENTITY.
 * Creating an identity is a contract deployment; every attribute/delegate is a key.
 * There is no VIN→identity mapping on-chain (an off-chain index is assumed).
 */
class ERC725Adapter extends IdentityAdapter {
  static id = "erc725";
  static label = "ERC-725";
  static family = "proxy identity (contract per identity)";

  constructor(opts) {
    super(opts);
    this.unsupported["R2_resolve_by_vin"] = "no on-chain VIN index (off-chain index assumed)";
    this.unsupported["U5_meta_tx"] = "no signed-operation primitive";
    this.vinIndex = new Map();
    this.issuerContracts = new Map();
  }

  async deploy() {
    const { ethers, actors } = this;
    this.factory = await ethers.getContractFactory("CVIN_SCBasedAccOrID_DID_ERC725Basic", actors.deployer);
    // Issuer identity contract (shared fixed cost of the credential layer).
    const issuerId = await this.factory.connect(actors.issuer).deploy();
    await issuerId.waitForDeployment();
    this.issuerContracts.set(actors.issuer.address, issuerId);
    this.contracts = { issuerIdentity: issuerId };
    return [{ name: "CVIN_DID_ERC725 (issuer identity)", contract: issuerId }];
  }

  _k(s) { return this.ethers.keccak256(this.ethers.toUtf8Bytes(s)); }
  _addrKey(a) { return this.ethers.zeroPadValue(a, 32); }

  async createIdentity(v, owner) {
    const id = await this.factory.connect(owner).deploy();
    const deployTx = id.deploymentTransaction();
    await id.waitForDeployment();
    const tx2 = await id.connect(owner).addKey(this._k("vin:" + v.vin), PURPOSE.VIN, KEYTYPE_ECDSA);
    this.vinIndex.set(v.vin, await id.getAddress());
    return { txs: [deployTx, tx2], result: { id, address: await id.getAddress(), vin: v.vin, controller: owner } };
  }
  async createIdentityWithAttributes(v, owner) {
    const { txs, result } = await this.createIdentity(v, owner);
    const attrs = { make: v.make, model: v.model, year: String(v.year), color: v.color, engineNumber: v.engineNumber, manufacturingDate: String(v.manufacturingDate), autonomyLevel: v.autonomyLevel };
    for (const [k, val] of Object.entries(attrs)) {
      txs.push(await result.id.connect(owner).addKey(this._k(`attr:${k}:${val}`), PURPOSE.ATTRIBUTE, KEYTYPE_ECDSA));
    }
    return { txs, result };
  }

  async resolveOwner(h) { return h.id.owner(); }
  async resolveByVin(vin) { return this.vinIndex.get(vin) || null; } // no RPC: off-chain index
  async verifyDelegate(h, key) {
    const k = await h.id.getKey(this._addrKey(key.address));
    return Number(k.purpose) === PURPOSE.ACTION || (await h.id.owner()) === key.address;
  }
  async resolveDocument(h) {
    const owner = await h.id.owner();
    const keys = await h.id.getKeys();
    const entries = [];
    for (const k of keys) entries.push(await h.id.getKey(k));
    return {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:erc725:31337:${h.address}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: [{ id: "#owner", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${owner}` },
        ...entries.filter((e) => Number(e.purpose) === PURPOSE.ACTION).map((e) => ({ id: `#key-${e.key.slice(0, 10)}`, type: "EcdsaSecp256k1RecoveryMethod2020", key: e.key }))],
      authentication: ["#owner"],
      service: [],
      keys: entries.map((e) => ({ key: e.key, purpose: Number(e.purpose), keyType: Number(e.keyType) })),
    };
  }

  async rotateController(h, newOwner) {
    const tx = await h.id.connect(h.controller).transferOwnership(newOwner.address);
    h.controller = newOwner;
    return { txs: [tx] };
  }
  async addDelegate(h, key /* ttl: no expiry primitive */) {
    const tx = await h.id.connect(h.controller).addKey(this._addrKey(key.address), PURPOSE.ACTION, KEYTYPE_ECDSA);
    return { txs: [tx] };
  }
  async setAttribute(h, name, value) {
    const tx = await h.id.connect(h.controller).addKey(this._k(`attr:${name}:${value}`), PURPOSE.ATTRIBUTE, KEYTYPE_ECDSA);
    h.lastAttr = { name, value };
    return { txs: [tx] };
  }
  async transferVehicle(h, to) { return this.rotateController(h, to); }
  async revokeDelegate(h, key) {
    const tx = await h.id.connect(h.controller).removeKey(this._addrKey(key.address));
    return { txs: [tx] };
  }
  async revokeAttribute(h, name) {
    const value = h.lastAttr && h.lastAttr.name === name ? h.lastAttr.value : "";
    const tx = await h.id.connect(h.controller).removeKey(this._k(`attr:${name}:${value}`));
    return { txs: [tx] };
  }
  async deactivate(h) {
    const tx = await h.id.connect(h.controller).renounceOwnership();
    return { txs: [tx] };
  }

  async anchorIssuerKey(issuer, key) {
    const id = this.issuerContracts.get(issuer.address);
    const tx = await id.connect(issuer).addKey(this._addrKey(key.address), PURPOSE.CLAIM, KEYTYPE_ECDSA);
    return { txs: [tx] };
  }
  async anchorStatus(h, credHash) {
    const id = this.issuerContracts.get(this.actors.issuer.address);
    const tx = await id.connect(this.actors.issuer).addKey(credHash, PURPOSE.STATUS, KEYTYPE_ECDSA);
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash) {
    const id = this.issuerContracts.get(this.actors.issuer.address);
    const tx = await id.connect(this.actors.issuer).removeKey(credHash);
    return { txs: [tx] };
  }
  async statusCheck(h, credHash) {
    const id = this.issuerContracts.get(this.actors.issuer.address);
    const k = await id.getKey(credHash);
    return Number(k.purpose) === PURPOSE.STATUS ? "active" : "revoked";
  }

  async prepareThroughputSenders(senders) {
    const out = [];
    for (let i = 0; i < senders.length; i++) {
      const { result } = await this.createIdentity(this.dataset[900 + i], senders[i]);
      out.push({ sender: senders[i], handle: result });
    }
    return out;
  }
  async throughputOp(entry, i, overrides) {
    return entry.handle.id.connect(entry.sender).addKey(this._k(`attr:tp:${i}`), PURPOSE.ATTRIBUTE, KEYTYPE_ECDSA, overrides);
  }
}

module.exports = { ERC725Adapter, PURPOSE };
