"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

/**
 * LSP8 identifiable digital asset (representative implementation): one shared
 * collection whose contract owner is the single ISSUING AUTHORITY; the vehicle is
 * a bytes32 token (keccak256(VIN)) with a per-token key/value data store.
 *  - only the authority mints, revokes and writes token data: attributes,
 *    service records and credential status are all authority writes
 *    (the issuer/service-centre actors cannot write; the authority writes on
 *    their behalf — V1 is n/a, there is one issuer)
 *  - operators (authorizeOperator) are not implemented: U2/D1/R4 n/a; U5 n/a
 *  - the token owner transfers the vehicle (transfer(from,to,id,force=true,data))
 *  - no batch mint; setDataBatchForTokenIds is a data batch, used for C2
 */
class LSP8Adapter extends IdentityAdapter {
  static id = "lsp8";
  static label = "LSP8";
  static family = "LSP8 identifiable asset (shared collection, single authority)";

  constructor(opts) {
    super(opts);
    Object.assign(this.unsupported, {
      R4_verify_delegate: "operators not implemented in this LSP8 representative; token owner is the only key",
      U2_add_delegate: "authorizeOperator not implemented",
      D1_revoke_delegate: "revokeOperator not implemented",
      U5_meta_tx: "no signed entry point",
      V1_issuer_key_anchor: "single issuing authority (contract owner); issuer keys are not modelled",
    });
    const k = (s) => this.ethers.keccak256(this.ethers.toUtf8Bytes(s));
    this.KEYS = { vin: k("CVIN_VIN"), make: k("CVIN_MAKE"), model: k("CVIN_MODEL"), year: k("CVIN_YEAR"), color: k("CVIN_COLOR"), engineNumber: k("CVIN_ENGINE"), manufacturingDate: k("CVIN_MFG_DATE"), autonomyLevel: k("CVIN_AUTONOMY") };
  }

  async deploy() {
    const F = await this.ethers.getContractFactory("CVINVehicleLSP8", this.actors.deployer);
    const c = await F.deploy("CVIN Vehicle Identity LSP8", "CVIN-LSP8");
    await c.waitForDeployment();
    this.contracts = { lsp8: c };
    this.addr = await c.getAddress();
    return [{ name: "CVINVehicleLSP8", contract: c }];
  }
  _auth() { return this.contracts.lsp8.connect(this.actors.deployer); }
  _k(name) { return this.ethers.keccak256(this.ethers.toUtf8Bytes(name)); }
  _b(s) { return this.ethers.toUtf8Bytes(s); }
  _tokenId(vin) { return this.ethers.keccak256(this.ethers.toUtf8Bytes(vin)); }

  async createIdentity(v, owner) {
    const tx = await this._auth().mintVehicle(owner.address, v.vin);
    return { txs: [tx], result: { tokenId: this._tokenId(v.vin), vin: v.vin, controller: owner, attrKeys: {} } };
  }
  async createIdentityWithAttributes(v, owner) {
    const { txs, result } = await this.createIdentity(v, owner);
    const K = this.KEYS;
    const keys = [K.make, K.model, K.year, K.color, K.engineNumber, K.manufacturingDate, K.autonomyLevel];
    const vals = [this._b(v.make), this._b(v.model), this._b(String(v.year)), this._b(v.color), this._b(v.engineNumber), this._b(String(v.manufacturingDate)), this._b(v.autonomyLevel)];
    txs.push(await this._auth().setDataBatchForTokenIds(keys.map(() => result.tokenId), keys, vals));
    return { txs, result };
  }

  async resolveOwner(h) {
    return (await this.contracts.lsp8.exists(h.tokenId)) ? this.contracts.lsp8.tokenOwnerOf(h.tokenId) : this.ethers.ZeroAddress;
  }
  async resolveByVin(vin) {
    const id = this._tokenId(vin);
    return (await this.contracts.lsp8.exists(id)) ? id : null;
  }
  async verifyDelegate() { this.notSupported("R4_verify_delegate"); }
  async resolveDocument(h) {
    const c = this.contracts.lsp8;
    const keys = [...Object.values(this.KEYS), ...Object.values(h.attrKeys)];
    const [exists, values] = await Promise.all([c.exists(h.tokenId), c.getDataBatchForTokenIds(keys.map(() => h.tokenId), keys)]);
    const owner = exists ? await c.tokenOwnerOf(h.tokenId) : this.ethers.ZeroAddress;
    const data = Object.fromEntries(keys.map((k, i) => [k, values[i]]));
    return {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:lsp8:31337:${this.addr}:${h.tokenId}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: [{ id: "#owner", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${owner}` }],
      authentication: ["#owner"],
      service: [],
      attributes: { vin: this.ethers.toUtf8String(data[this.KEYS.vin] || "0x"), active: exists },
      data,
    };
  }

  async rotateController(h, newOwner) {
    const tx = await this.contracts.lsp8.connect(h.controller).transfer(h.controller.address, newOwner.address, h.tokenId, true, "0x");
    h.controller = newOwner;
    return { txs: [tx] };
  }
  async transferVehicle(h, to) { return this.rotateController(h, to); }
  async addDelegate() { this.notSupported("U2_add_delegate"); }
  async revokeDelegate() { this.notSupported("D1_revoke_delegate"); }
  async rotateDelegate() { this.notSupported("U2_add_delegate"); }
  async setAttribute(h, name, value) {
    const key = this._k(name);
    const tx = await this._auth().setDataForTokenId(h.tokenId, key, this._b(value));
    h.attrKeys[name] = key;
    return { txs: [tx] };
  }
  async revokeAttribute(h, name) {
    const tx = await this._auth().setDataForTokenId(h.tokenId, this._k(name), "0x");
    return { txs: [tx] };
  }
  async deactivate(h) {
    const tx = await this._auth().revokeVehicle(h.tokenId, "0x");
    return { txs: [tx] };
  }

  async anchorIssuerKey() { this.notSupported("V1_issuer_key_anchor"); }
  async anchorStatus(h, credHash) {
    const tx = await this._auth().setDataForTokenId(h.tokenId, credHash, this._b("active"));
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash) {
    const tx = await this._auth().setDataForTokenId(h.tokenId, credHash, "0x");
    return { txs: [tx] };
  }
  async statusCheck(h, credHash) {
    const v = await this.contracts.lsp8.getDataForTokenId(h.tokenId, credHash);
    return v && v !== "0x" ? "active" : "revoked";
  }

  // The authority is the only writer: every burst tx comes from one sender
  // (the scenario keys nonces by sender address), one token per entry.
  async prepareThroughputSenders(senders) {
    const out = [];
    for (let i = 0; i < senders.length; i++) {
      const { result, txs } = await this.createIdentity(this.dataset[900 + i], senders[i]);
      await txs.at(-1).wait();
      out.push({ sender: this.actors.deployer, handle: result });
    }
    return out;
  }
  async throughputOp(entry, i, overrides) {
    return this._auth().setDataForTokenId(entry.handle.tokenId, this._k(`tp:${i}`), this._b(this.payloads.attributeValue), overrides);
  }
}

module.exports = { LSP8Adapter };
