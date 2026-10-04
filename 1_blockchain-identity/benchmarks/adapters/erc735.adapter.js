"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

const DEAD = "0x000000000000000000000000000000000000dEaD";
const ECDSA_SCHEME = 1;
const TOPIC = { VIN_ATTESTATION: 1n, MANUFACTURER_CERT: 2n, INSPECTION: 3n, INSURANCE: 4n };

/**
 * ERC-735 claim holder: ONE CONTRACT PER IDENTITY; deployment is identity creation.
 * The contract owner plays the ERC-734 MANAGEMENT-key role (the draft's key
 * management is absent), so:
 *  - no delegate keys (U2/D1/R4 n/a), no signed/relayed entry point (U5 n/a)
 *  - the issuer's "key" is its EOA address, there is nothing to anchor (V1 n/a)
 *  - attributes are self-issued claims (owner signs, owner anchors); credentials
 *    are issuer-signed claims anchored by the OWNER (addClaim is onlyOwner) and
 *    revoked by the ISSUER (removeClaim, sticky); one claim per (issuer, topic),
 *    so each credential uses topic = uint256(credentialHash)
 *  - no deactivate primitive: realised as transferOwnership(0xdEaD) (claims stay readable)
 *  - no on-chain VIN index (R2 n/a); resolution enumerates claims from the event log
 */
class ERC735Adapter extends IdentityAdapter {
  static id = "erc735";
  static label = "ERC-735";
  static family = "claim holder (contract per identity)";

  constructor(opts) {
    super(opts);
    Object.assign(this.unsupported, {
      R2_resolve_by_vin: "no on-chain VIN index (off-chain index assumed)",
      R4_verify_delegate: "no delegate keys: single MANAGEMENT key (owner)",
      U2_add_delegate: "no key management (ERC-734 absent); owner is the only key",
      D1_revoke_delegate: "no key management (ERC-734 absent)",
      U5_meta_tx: "no signed entry point",
      V1_issuer_key_anchor: "issuer key is the issuer EOA; nothing to anchor on-chain",
    });
  }

  async deploy() {
    this.factory = await this.ethers.getContractFactory("CVINVehicleClaimHolder", this.actors.deployer);
    return []; // no shared contract: every identity is its own deployment
  }

  _digest(identity, topic, data) {
    return this.ethers.solidityPackedKeccak256(["address", "uint256", "bytes"], [identity, topic, data]);
  }
  async _sign(signer, identity, topic, data) {
    return signer.signMessage(this.ethers.getBytes(this._digest(identity, topic, data)));
  }
  _claimId(issuer, topic) {
    return this.ethers.solidityPackedKeccak256(["address", "uint256"], [issuer, topic]);
  }
  _topicOf(name) { return BigInt(this.ethers.keccak256(this.ethers.toUtf8Bytes(name))); }

  async createIdentity(v, owner) {
    const holder = await this.factory.connect(owner).deploy(v.vin);
    const deployTx = holder.deploymentTransaction();
    await holder.waitForDeployment();
    return { txs: [deployTx], result: { id: holder, address: await holder.getAddress(), vin: v.vin, controller: owner, attrs: {} } };
  }

  async createIdentityWithAttributes(v, owner) {
    const { txs, result } = await this.createIdentity(v, owner);
    // VID-I birth certificate = one manufacturer-signed MANUFACTURER_CERT claim
    const data = this.ethers.AbiCoder.defaultAbiCoder().encode(
      ["string", "string", "uint16", "string", "string", "uint256", "string"],
      [v.make, v.model, v.year, v.color, v.engineNumber, v.manufacturingDate, v.autonomyLevel]
    );
    const m = this.actors.manufacturer;
    const sig = await this._sign(m, result.address, TOPIC.MANUFACTURER_CERT, data);
    txs.push(await result.id.connect(owner).addClaim(TOPIC.MANUFACTURER_CERT, ECDSA_SCHEME, m.address, sig, data, v.metadataURI));
    return { txs, result };
  }

  async resolveOwner(h) { return h.id.owner(); }
  async resolveByVin() { this.notSupported("R2_resolve_by_vin"); }
  async verifyDelegate() { this.notSupported("R4_verify_delegate"); }

  /** Claims are not enumerable on-chain (no topic list): replay Claim* events from the log. */
  async resolveDocument(h) {
    const iface = h.id.interface;
    const [owner, vin, logs] = await Promise.all([
      h.id.owner(), h.id.vin(),
      this.ethers.provider.getLogs({ address: h.address, fromBlock: 0, toBlock: "latest" }),
    ]);
    const claims = new Map();
    for (const log of logs) {
      let p; try { p = iface.parseLog(log); } catch { continue; }
      if (!p) continue;
      if (p.name === "ClaimAdded" || p.name === "ClaimChanged") {
        claims.set(p.args.claimId, { claimId: p.args.claimId, topic: p.args.topic.toString(), issuer: p.args.issuer, data: p.args.data, uri: p.args.uri });
      } else if (p.name === "ClaimRemoved") {
        claims.delete(p.args.claimId);
      }
    }
    return {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:erc735:31337:${h.address}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: [{ id: "#owner", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${owner}` }],
      authentication: ["#owner"],
      service: [],
      attributes: { vin },
      claims: [...claims.values()],
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
    const topic = this._topicOf(name);
    const data = this.ethers.toUtf8Bytes(value);
    const sig = await this._sign(h.controller, h.address, topic, data);
    const tx = await h.id.connect(h.controller).addClaim(topic, ECDSA_SCHEME, h.controller.address, sig, data, "");
    h.attrs[name] = { topic, issuer: h.controller.address };
    return { txs: [tx] };
  }
  async revokeAttribute(h, name) {
    const a = h.attrs[name];
    const tx = await h.id.connect(h.controller).removeClaim(this._claimId(a.issuer, a.topic));
    return { txs: [tx] };
  }
  async deactivate(h) {
    const tx = await h.id.connect(h.controller).transferOwnership(DEAD);
    return { txs: [tx] };
  }

  async anchorIssuerKey() { this.notSupported("V1_issuer_key_anchor"); }
  async anchorStatus(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const topic = BigInt(credHash);
    const data = this.ethers.getBytes(credHash);
    const sig = await this._sign(issuer, h.address, topic, data);
    const tx = await h.id.connect(h.controller).addClaim(topic, ECDSA_SCHEME, issuer.address, sig, data, "");
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    const tx = await h.id.connect(issuer).removeClaim(this._claimId(issuer.address, BigInt(credHash)));
    return { txs: [tx] };
  }
  async statusCheck(h, credHash, issuerArg) {
    const issuer = this._issuer(issuerArg);
    return (await h.id.claimExists(issuer.address, BigInt(credHash))) ? "active" : "revoked";
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
    const topic = this._topicOf(`tp:${i}`);
    const data = this.ethers.toUtf8Bytes(this.payloads.attributeValue);
    const sig = await this._sign(entry.sender, entry.handle.address, topic, data);
    return entry.handle.id.connect(entry.sender).addClaim(topic, ECDSA_SCHEME, entry.sender.address, sig, data, "", overrides);
  }
}

module.exports = { ERC735Adapter, TOPIC };
