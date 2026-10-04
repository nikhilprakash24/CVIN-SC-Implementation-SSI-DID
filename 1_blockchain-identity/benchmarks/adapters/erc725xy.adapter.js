"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

/**
 * ERC-725 X+Y smart account: ONE CONTRACT PER IDENTITY (the account address is the
 * DID); a single owner is the controlling key; attributes live in the ERC-725Y
 * key/value store. Without a key manager (LSP6) there are no delegate keys and no
 * signed entry point (U2/D1/R4/U5 n/a); there is no on-chain VIN index (R2 n/a).
 * Credential status is kept in the ISSUER's own account (one per issuer):
 * V1 = issuer records its signing key, V3/V5 = setData(credHash, "active" | 0x).
 */
class ERC725XYAdapter extends IdentityAdapter {
  static id = "erc725xy";
  static label = "ERC-725xy";
  static family = "ERC-725 X+Y smart account (contract per identity)";

  constructor(opts) {
    super(opts);
    Object.assign(this.unsupported, {
      R2_resolve_by_vin: "no on-chain VIN index (off-chain index assumed)",
      R4_verify_delegate: "single owner key; no key manager (LSP6) in ERC-725 X+Y",
      U2_add_delegate: "no key manager; owner is the only key",
      D1_revoke_delegate: "no key manager",
      U5_meta_tx: "execute()/setData() are owner-only; no signed entry point",
    });
    const k = (s) => this.ethers.keccak256(this.ethers.toUtf8Bytes(s));
    this.KEYS = { vin: k("cvin:vin"), make: k("cvin:make"), model: k("cvin:model"), year: k("cvin:year"), color: k("cvin:color"), engineNumber: k("cvin:engineNumber"), manufacturingDate: k("cvin:manufacturingDate"), autonomyLevel: k("cvin:autonomyLevel") };
    this.issuerAccounts = new Map();
  }

  async deploy() {
    this.factory = await this.ethers.getContractFactory("CVINVehicleERC725XY", this.actors.deployer);
    const iss = await this.factory.connect(this.actors.issuer).deploy(this.actors.issuer.address);
    await iss.waitForDeployment();
    this.issuerAccounts.set(this.actors.issuer.address, iss);
    return [{ name: "CVINVehicleERC725XY (issuer account)", contract: iss }];
  }
  async prepareIssuer(issuer) {
    if (this.issuerAccounts.has(issuer.address)) return;
    const acc = await this.factory.connect(issuer).deploy(issuer.address);
    await acc.waitForDeployment();
    this.issuerAccounts.set(issuer.address, acc);
  }
  _k(name) { return this.ethers.keccak256(this.ethers.toUtf8Bytes(name)); }
  _b(s) { return this.ethers.toUtf8Bytes(s); }

  async createIdentity(v, owner) {
    const acc = await this.factory.connect(owner).deploy(owner.address);
    const deployTx = acc.deploymentTransaction();
    await acc.waitForDeployment();
    const tx2 = await acc.connect(owner).setData(this.KEYS.vin, this._b(v.vin));
    return { txs: [deployTx, tx2], result: { id: acc, address: await acc.getAddress(), vin: v.vin, controller: owner, attrKeys: {} } };
  }
  async createIdentityWithAttributes(v, owner) {
    const acc = await this.factory.connect(owner).deploy(owner.address);
    const deployTx = acc.deploymentTransaction();
    await acc.waitForDeployment();
    const K = this.KEYS;
    const tx2 = await acc.connect(owner).setDataBatch(
      [K.vin, K.make, K.model, K.year, K.color, K.engineNumber, K.manufacturingDate, K.autonomyLevel],
      [this._b(v.vin), this._b(v.make), this._b(v.model), this.ethers.AbiCoder.defaultAbiCoder().encode(["uint256"], [v.year]), this._b(v.color), this._b(v.engineNumber), this.ethers.AbiCoder.defaultAbiCoder().encode(["uint256"], [v.manufacturingDate]), this._b(v.autonomyLevel)]
    );
    return { txs: [deployTx, tx2], result: { id: acc, address: await acc.getAddress(), vin: v.vin, controller: owner, attrKeys: {} } };
  }

  async resolveOwner(h) { return h.id.owner(); }
  async resolveByVin() { this.notSupported("R2_resolve_by_vin"); }
  async verifyDelegate() { this.notSupported("R4_verify_delegate"); }
  async resolveDocument(h) {
    const keys = [...Object.values(this.KEYS), ...Object.values(h.attrKeys)];
    const [owner, values] = await Promise.all([h.id.owner(), h.id.getDataBatch(keys)]);
    const data = Object.fromEntries(keys.map((k, i) => [k, values[i]]));
    return {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:erc725:31337:${h.address}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: [{ id: "#owner", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${owner}` }],
      authentication: ["#owner"],
      service: [],
      attributes: { vin: this.ethers.toUtf8String(data[this.KEYS.vin] || "0x") },
      data,
    };
  }

  async rotateController(h, newOwner) {
    const tx = await h.id.connect(h.controller).transferOwnership(newOwner.address);
    h.controller = newOwner;
    return { txs: [tx] };
  }
  async transferVehicle(h, to) { return this.rotateController(h, to); }
  async addDelegate() { this.notSupported("U2_add_delegate"); }
  async revokeDelegate() { this.notSupported("D1_revoke_delegate"); }
  async rotateDelegate() { this.notSupported("U2_add_delegate"); }
  async setAttribute(h, name, value) {
    const key = this._k(name);
    const tx = await h.id.connect(h.controller).setData(key, this._b(value));
    h.attrKeys[name] = key;
    return { txs: [tx] };
  }
  async revokeAttribute(h, name) {
    const tx = await h.id.connect(h.controller).setData(this._k(name), "0x");
    return { txs: [tx] };
  }
  async deactivate(h) {
    const tx = await h.id.connect(h.controller).renounceOwnership();
    return { txs: [tx] };
  }

  async anchorIssuerKey(issuer, key) {
    const acc = this.issuerAccounts.get(issuer.address);
    const tx = await acc.connect(issuer).setData(this._k("cvin:issuerKey:" + key.address), "0x01");
    return { txs: [tx] };
  }
  async anchorStatus(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const tx = await this.issuerAccounts.get(issuer.address).connect(issuer).setData(credHash, this._b("active"));
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const tx = await this.issuerAccounts.get(issuer.address).connect(issuer).setData(credHash, "0x");
    return { txs: [tx] };
  }
  async statusCheck(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const v = await this.issuerAccounts.get(issuer.address).getData(credHash);
    return v && v !== "0x" ? "active" : "revoked";
  }

  async prepareThroughputSenders(senders) {
    const out = [];
    for (let i = 0; i < senders.length; i++) {
      const { result, txs } = await this.createIdentity(this.dataset[900 + i], senders[i]);
      await txs.at(-1).wait();
      out.push({ sender: senders[i], handle: result });
    }
    return out;
  }
  async throughputOp(entry, i, overrides) {
    return entry.handle.id.connect(entry.sender).setData(this._k(`tp:${i}`), this._b(this.payloads.attributeValue), overrides);
  }
}

module.exports = { ERC725XYAdapter };
