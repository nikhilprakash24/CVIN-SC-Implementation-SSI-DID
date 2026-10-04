"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

const TYPE = { BIRTH_CERT: 1n, REGISTRATION: 2n, INSPECTION_CERT: 3n, INSURANCE_CERT: 4n, MAINTENANCE_BADGE: 5n };
const TYPE_NAMES = ["BIRTH_CERT", "REGISTRATION", "INSPECTION_CERT", "INSURANCE_CERT", "MAINTENANCE_BADGE"];

/**
 * ERC-1155 multi-token credentials: shared registry; the VEHICLE ADDRESS is the
 * identity and its token balances are the credentials it holds (soulbound:
 * only ISSUER_ROLE may move them). Consequences for the catalogue:
 *  - no per-vehicle attribute store (uri() is per credential TYPE): VID-I
 *    attributes stay off-chain, so C2 = C1; U3/D2 are realised as issuing /
 *    burning one MAINTENANCE_BADGE (the payload is not stored)
 *  - no delegate keys (U2/D1/R4 n/a), no signed entry point (U5 n/a)
 *  - controller rotation == ownership transfer == the issuer re-binds the
 *    BIRTH_CERT AND every credential type the vehicle holds to the new address
 *    (issuerTransferCredential moves one type per tx, so a resale costs
 *    1 + #held-types transactions; K-13: the receiver must hold no BIRTH_CERT,
 *    so repeated-iteration scenarios need a fresh receiver — `freshReceiverPerIteration`)
 *  - each credential is its own token type (type = uint256(credentialHash)),
 *    issued/burned by an ISSUER_ROLE holder; V1 = granting ISSUER_ROLE to the key
 *  - the contract exposes no batch registration although ERC-1155 has mintBatch
 */
class ERC1155Adapter extends IdentityAdapter {
  static id = "erc1155";
  static label = "ERC-1155";
  static family = "multi-token credentials (shared registry; vehicle = address)";
  freshReceiverPerIteration = true;

  constructor(opts) {
    super(opts);
    Object.assign(this.unsupported, {
      R4_verify_delegate: "no delegate keys; credentials are soulbound to the vehicle address",
      U2_add_delegate: "no key management; operators cannot move soulbound credentials",
      D1_revoke_delegate: "no key management",
      U5_meta_tx: "no signed entry point",
    });
    this.attributesOffchain = true;
  }

  async deploy() {
    const { ethers, actors } = this;
    const F = await ethers.getContractFactory("CVINVehicleCredential1155", actors.deployer);
    const reg = await F.deploy();
    await reg.waitForDeployment();
    this.ISSUER_ROLE = await reg.ISSUER_ROLE();
    for (const a of [actors.manufacturer, actors.issuer, actors.serviceCenter]) {
      await (await reg.grantRole(this.ISSUER_ROLE, a.address)).wait();
    }
    this.contracts = { reg };
    this.regAddress = await reg.getAddress();
    return [{ name: "CVINVehicleCredential1155", contract: reg }];
  }

  _reg(signer) { return this.contracts.reg.connect(signer); }

  async prepareIssuer(issuer) {
    if (!(await this.contracts.reg.hasRole(this.ISSUER_ROLE, issuer.address))) {
      await (await this._reg(this.actors.deployer).grantRole(this.ISSUER_ROLE, issuer.address)).wait();
    }
  }

  async createIdentity(v, owner) {
    const tx = await this._reg(this.actors.manufacturer).registerVehicle(owner.address, v.vin);
    return { txs: [tx], result: { vehicle: owner.address, vin: v.vin, controller: owner, held: new Map() } };
  }
  // No per-vehicle attribute store: the birth certificate's attributes live in the
  // (per-type) metadata URI, i.e. off-chain. C2 therefore costs exactly C1.
  async createIdentityWithAttributes(v, owner) { return this.createIdentity(v, owner); }

  async resolveOwner(h) {
    return (await this.contracts.reg.isRegistered(h.vehicle)) ? h.vehicle : this.ethers.ZeroAddress;
  }
  async resolveByVin(vin) { return this.contracts.reg.vinHashToVehicle(this.ethers.keccak256(this.ethers.toUtf8Bytes(vin))); }
  async verifyDelegate() { this.notSupported("R4_verify_delegate"); }
  async resolveDocument(h) {
    const reg = this.contracts.reg;
    const ids = Object.values(TYPE);
    const [vin, balances, uri] = await Promise.all([
      reg.vehicleVIN(h.vehicle), reg.balanceOfBatch(ids.map(() => h.vehicle), ids), reg.uri(TYPE.BIRTH_CERT),
    ]);
    const credentials = Object.fromEntries(TYPE_NAMES.map((n, i) => [n, Number(balances[i])]));
    return {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:erc1155:31337:${this.regAddress}:${h.vehicle}`,
      controller: `did:ethr:31337:${h.vehicle}`,
      verificationMethod: [{ id: "#vehicle", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${h.vehicle}` }],
      authentication: ["#vehicle"],
      service: [{ id: "#birth-cert-metadata", type: "CredentialMetadata", serviceEndpoint: uri }],
      attributes: { vin, active: credentials.BIRTH_CERT > 0 },
      credentials,
    };
  }

  _hold(h, type, delta) {
    const k = type.toString();
    const n = (h.held.get(k) || 0) + delta;
    if (n > 0) h.held.set(k, n); else h.held.delete(k);
  }
  async rotateController(h, newOwner) {
    const reg = this._reg(this.actors.manufacturer);
    const txs = [await reg.issuerTransferCredential(h.vehicle, newOwner.address, TYPE.BIRTH_CERT)];
    for (const k of h.held.keys()) txs.push(await reg.issuerTransferCredential(h.vehicle, newOwner.address, BigInt(k)));
    h.vehicle = newOwner.address;
    h.controller = newOwner;
    return { txs };
  }
  async transferVehicle(h, to) { return this.rotateController(h, to); }
  async addDelegate() { this.notSupported("U2_add_delegate"); }
  async revokeDelegate() { this.notSupported("D1_revoke_delegate"); }
  async rotateDelegate() { this.notSupported("U2_add_delegate"); }

  async setAttribute(h /* name, value: not storable */) {
    const tx = await this._reg(this.actors.serviceCenter).issueCredential(h.vehicle, TYPE.MAINTENANCE_BADGE, 1);
    this._hold(h, TYPE.MAINTENANCE_BADGE, 1);
    return { txs: [tx] };
  }
  async revokeAttribute(h) {
    const tx = await this._reg(this.actors.serviceCenter).revokeCredential(h.vehicle, TYPE.MAINTENANCE_BADGE, 1);
    this._hold(h, TYPE.MAINTENANCE_BADGE, -1);
    return { txs: [tx] };
  }
  async deactivate(h) {
    const tx = await this._reg(this.actors.manufacturer).revokeCredential(h.vehicle, TYPE.BIRTH_CERT, 1);
    return { txs: [tx] };
  }

  async anchorIssuerKey(issuer, key) {
    const tx = await this._reg(this.actors.deployer).grantRole(this.ISSUER_ROLE, key.address);
    return { txs: [tx] };
  }
  async anchorStatus(h, credHash, issuerArg) {
    const tx = await this._reg(this._issuer(issuerArg)).issueCredential(h.vehicle, BigInt(credHash), 1);
    this._hold(h, BigInt(credHash), 1);
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash, issuerArg) {
    const tx = await this._reg(this._issuer(issuerArg)).revokeCredential(h.vehicle, BigInt(credHash), 1);
    this._hold(h, BigInt(credHash), -1);
    return { txs: [tx] };
  }
  async statusCheck(h, credHash) {
    return (await this.contracts.reg.hasCredential(h.vehicle, BigInt(credHash))) ? "active" : "revoked";
  }

  async prepareThroughputSenders(senders) {
    const out = [];
    for (let i = 0; i < senders.length; i++) {
      await this.prepareIssuer(senders[i]);
      const { result, txs } = await this.createIdentity(this.dataset[900 + i], senders[i]);
      await txs.at(-1).wait();
      out.push({ sender: senders[i], handle: result });
    }
    return out;
  }
  async throughputOp(entry, i, overrides) {
    return this._reg(entry.sender).issueCredential(entry.handle.vehicle, TYPE.MAINTENANCE_BADGE, 1, overrides);
  }
}

module.exports = { ERC1155Adapter, TYPE };
