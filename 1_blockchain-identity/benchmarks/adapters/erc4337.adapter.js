"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

const DEAD = "0x000000000000000000000000000000000000dEaD";
const ZERO32 = "0x" + "00".repeat(32);

/**
 * ERC-4337 smart account (research harness: CVINMinimalEntryPoint + CVINVehicleAccount).
 * ONE ACCOUNT CONTRACT PER IDENTITY (its address is the DID); the owner key rotates
 * without changing the identity. Realisations:
 *  - attributes: the account's ERC-725Y-flavoured setAttribute(bytes32,bytes), one key
 *    per tx (no batch) — C2 = deploy + 8 attribute txs
 *  - U5 meta-tx is the standard's headline path: the owner signs a PackedUserOperation
 *    (EIP-191 over userOpHash) whose callData is execute(self, 0, setAttribute(..)),
 *    and a relayer calls EntryPoint.handleOp
 *  - "delegate" = the social-recovery GUARDIAN (single slot, can install a new owner);
 *    it is a recovery key, not a signing delegate — a documented semantic stretch
 *  - no VIN index (R2 n/a); no deactivate primitive (transferOwnership(0xdEaD))
 *  - credential status lives in the ISSUER's own account (V1/V3/V5/V6), as for ERC-725xy
 */
class ERC4337Adapter extends IdentityAdapter {
  static id = "erc4337";
  static label = "ERC-4337";
  static family = "smart account + entry point (contract per identity)";

  constructor(opts) {
    super(opts);
    Object.assign(this.unsupported, { R2_resolve_by_vin: "no on-chain VIN index (off-chain index assumed)" });
    const k = (s) => this.ethers.keccak256(this.ethers.toUtf8Bytes(s));
    this.KEYS = { vin: k("cvin:vin"), make: k("cvin:make"), model: k("cvin:model"), year: k("cvin:year"), color: k("cvin:color"), engineNumber: k("cvin:engineNumber"), manufacturingDate: k("cvin:manufacturingDate"), autonomyLevel: k("cvin:autonomyLevel") };
    this.issuerAccounts = new Map();
  }

  async deploy() {
    const { ethers, actors } = this;
    const EP = await ethers.getContractFactory("CVINMinimalEntryPoint", actors.deployer);
    const entryPoint = await EP.deploy();
    await entryPoint.waitForDeployment();
    this.entryPoint = entryPoint;
    this.epAddress = await entryPoint.getAddress();
    this.factory = await ethers.getContractFactory("CVINVehicleAccount", actors.deployer);
    const iss = await this.factory.connect(actors.issuer).deploy(this.epAddress, actors.issuer.address);
    await iss.waitForDeployment();
    this.issuerAccounts.set(actors.issuer.address, iss);
    this.contracts = { entryPoint };
    return [{ name: "CVINMinimalEntryPoint", contract: entryPoint }, { name: "CVINVehicleAccount (issuer account)", contract: iss }];
  }
  async prepareIssuer(issuer) {
    if (this.issuerAccounts.has(issuer.address)) return;
    const acc = await this.factory.connect(issuer).deploy(this.epAddress, issuer.address);
    await acc.waitForDeployment();
    this.issuerAccounts.set(issuer.address, acc);
  }
  _k(name) { return this.ethers.keccak256(this.ethers.toUtf8Bytes(name)); }
  _b(s) { return this.ethers.toUtf8Bytes(s); }

  async _deployAccount(owner) {
    const acc = await this.factory.connect(owner).deploy(this.epAddress, owner.address);
    const deployTx = acc.deploymentTransaction();
    await acc.waitForDeployment();
    return { acc, deployTx };
  }
  async createIdentity(v, owner) {
    const { acc, deployTx } = await this._deployAccount(owner);
    const tx2 = await acc.connect(owner).setAttribute(this.KEYS.vin, this._b(v.vin));
    return { txs: [deployTx, tx2], result: { id: acc, address: await acc.getAddress(), vin: v.vin, controller: owner, attrKeys: {} } };
  }
  async createIdentityWithAttributes(v, owner) {
    const { acc, deployTx } = await this._deployAccount(owner);
    const K = this.KEYS;
    const pairs = [[K.vin, v.vin], [K.make, v.make], [K.model, v.model], [K.year, String(v.year)], [K.color, v.color], [K.engineNumber, v.engineNumber], [K.manufacturingDate, String(v.manufacturingDate)], [K.autonomyLevel, v.autonomyLevel]];
    const txs = [deployTx];
    for (const [key, val] of pairs) txs.push(await acc.connect(owner).setAttribute(key, this._b(val)));
    return { txs, result: { id: acc, address: await acc.getAddress(), vin: v.vin, controller: owner, attrKeys: {} } };
  }

  async resolveOwner(h) { return h.id.owner(); }
  async resolveByVin() { this.notSupported("R2_resolve_by_vin"); }
  async verifyDelegate(h, key) { return (await h.id.guardian()) === key.address; }
  async resolveDocument(h) {
    const keys = [...Object.values(this.KEYS), ...Object.values(h.attrKeys)];
    const [owner, guardian, ...values] = await Promise.all([h.id.owner(), h.id.guardian(), ...keys.map((k) => h.id.getAttribute(k))]);
    const data = Object.fromEntries(keys.map((k, i) => [k, values[i]]));
    const vm = [{ id: "#owner", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${owner}` }];
    if (guardian !== this.ethers.ZeroAddress) vm.push({ id: "#guardian", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${guardian}`, role: "recovery" });
    return {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:erc4337:31337:${h.address}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: vm,
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
  async addDelegate(h, key /* ttl: guardian has no expiry */) {
    const tx = await h.id.connect(h.controller).setGuardian(key.address);
    return { txs: [tx] };
  }
  async revokeDelegate(h) {
    const tx = await h.id.connect(h.controller).setGuardian(this.ethers.ZeroAddress);
    return { txs: [tx] };
  }
  async rotateDelegate(h, oldKey, newKey) { return this.addDelegate(h, newKey); } // single slot: replace
  async setAttribute(h, name, value) {
    const key = this._k(name);
    const tx = await h.id.connect(h.controller).setAttribute(key, this._b(value));
    h.attrKeys[name] = key;
    return { txs: [tx] };
  }
  async revokeAttribute(h, name) {
    const tx = await h.id.connect(h.controller).setAttribute(this._k(name), "0x");
    return { txs: [tx] };
  }
  async deactivate(h) {
    const tx = await h.id.connect(h.controller).transferOwnership(DEAD);
    return { txs: [tx] };
  }

  /** The 4337 path: owner-signed UserOperation relayed through the EntryPoint. */
  async metaTxSetAttribute(h, name, value, relayer) {
    const key = this._k(name);
    const inner = h.id.interface.encodeFunctionData("setAttribute", [key, this._b(value)]);
    const callData = h.id.interface.encodeFunctionData("execute", [h.address, 0, inner]);
    const userOp = {
      sender: h.address, nonce: await this.entryPoint.nonces(h.address), initCode: "0x", callData,
      accountGasLimits: ZERO32, preVerificationGas: 0, gasFees: ZERO32, paymasterAndData: "0x", signature: "0x",
    };
    const hash = await this.entryPoint.getUserOpHash(userOp);
    userOp.signature = await h.controller.signMessage(this.ethers.getBytes(hash));
    const tx = await this.entryPoint.connect(relayer).handleOp(userOp);
    h.attrKeys[name] = key;
    return { txs: [tx] };
  }

  async anchorIssuerKey(issuer, key) {
    const acc = this.issuerAccounts.get(issuer.address);
    const tx = await acc.connect(issuer).setAttribute(this._k("cvin:issuerKey:" + key.address), "0x01");
    return { txs: [tx] };
  }
  async anchorStatus(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const tx = await this.issuerAccounts.get(issuer.address).connect(issuer).setAttribute(credHash, this._b("active"));
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const tx = await this.issuerAccounts.get(issuer.address).connect(issuer).setAttribute(credHash, "0x");
    return { txs: [tx] };
  }
  async statusCheck(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const v = await this.issuerAccounts.get(issuer.address).getAttribute(credHash);
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
    return entry.handle.id.connect(entry.sender).setAttribute(this._k(`tp:${i}`), this._b(this.payloads.attributeValue), overrides);
  }
}

module.exports = { ERC4337Adapter };
