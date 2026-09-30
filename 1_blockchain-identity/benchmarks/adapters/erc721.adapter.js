"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

/**
 * ERC-721: the token is the identity (did:nft:erc721:<contract>:<tokenId>).
 * Ownership == control. Attributes are stored in a struct at mint; the only
 * post-mint attribute channel is the service-record array (SERVICE_CENTER_ROLE).
 */
class ERC721Adapter extends IdentityAdapter {
  static id = "erc721";
  static label = "ERC-721";
  static family = "NFT registry (shared, rich storage)";

  constructor(opts) {
    super(opts);
    this.unsupported["U5_meta_tx"] = "no signed-operation primitive";
    this.unsupported["D2_revoke_attribute"] = "service records are append-only; no retract primitive";
    this.issuerHandles = new Map();
  }

  async deploy() {
    const { ethers, actors } = this;
    const F = await ethers.getContractFactory("CVINVehicleNFT", actors.deployer);
    const nft = await F.deploy();
    await nft.waitForDeployment();
    await (await nft.grantManufacturerRole(actors.manufacturer.address)).wait();
    await (await nft.grantServiceCenterRole(actors.serviceCenter.address)).wait();
    this.contracts = { nft };
    this.nftAddress = await nft.getAddress();
    return [{ name: "CVINVehicleNFT", contract: nft }];
  }

  _nft(signer) { return this.contracts.nft.connect(signer); }

  async _tokenIdFromReceipt(tx) {
    const rc = await tx.wait();
    for (const log of rc.logs) {
      try {
        const p = this.contracts.nft.interface.parseLog(log);
        if (p && p.name === "VehicleMinted") return p.args.tokenId;
      } catch { /* other event */ }
    }
    throw new Error("VehicleMinted not found");
  }

  async createIdentity(v, owner) {
    const tx = await this._nft(this.actors.manufacturer).mintVehicle(owner.address, v.vin, "", "", 0, "", "");
    const tokenId = await this._tokenIdFromReceipt(tx);
    return { txs: [tx], result: { tokenId, vin: v.vin, controller: owner } };
  }
  async createIdentityWithAttributes(v, owner) {
    const tx = await this._nft(this.actors.manufacturer).mintVehicle(owner.address, v.vin, v.make, v.model, v.year, v.color, v.metadataURI);
    const tokenId = await this._tokenIdFromReceipt(tx);
    return { txs: [tx], result: { tokenId, vin: v.vin, controller: owner } };
  }

  async resolveOwner(h) { return this.contracts.nft.ownerOf(h.tokenId); }
  async resolveByVin(vin) { return this.contracts.nft.getTokenIdFromVIN(vin); }
  async verifyDelegate(h, key) {
    const [owner, approved] = await Promise.all([this.contracts.nft.ownerOf(h.tokenId), this.contracts.nft.getApproved(h.tokenId)]);
    return owner === key.address || approved === key.address;
  }
  async resolveDocument(h) {
    const nft = this.contracts.nft;
    const [owner, meta, uri, history, records, active, approved] = await Promise.all([
      nft.ownerOf(h.tokenId), nft.vehicleMetadata(h.tokenId), nft.tokenURI(h.tokenId),
      nft.getTransferHistory(h.tokenId), nft.getServiceRecords(h.tokenId), nft.isVehicleActive(h.tokenId), nft.getApproved(h.tokenId),
    ]);
    return {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:nft:erc721:${this.nftAddress}:${h.tokenId}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: [
        { id: "#owner", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${owner}` },
        ...(approved !== this.ethers.ZeroAddress ? [{ id: "#approved", type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${approved}` }] : []),
      ],
      authentication: ["#owner"],
      service: [{ id: "#metadata", type: "VehicleMetadata", serviceEndpoint: uri }],
      attributes: { vin: meta.vin, make: meta.make, model: meta.model, year: Number(meta.year), color: meta.color, active },
      transferHistory: history.map((t) => ({ from: t.from, to: t.to, block: Number(t.blockNumber) })),
      serviceRecords: records,
    };
  }

  async rotateController(h, newOwner) {
    const tx = await this._nft(h.controller).transferFrom(h.controller.address, newOwner.address, h.tokenId);
    h.controller = newOwner;
    return { txs: [tx] };
  }
  async addDelegate(h, key /*, ttl ignored: ERC-721 approvals have no expiry */) {
    const tx = await this._nft(h.controller).approve(key.address, h.tokenId);
    return { txs: [tx] };
  }
  async setAttribute(h, name, value) {
    const tx = await this._nft(this.actors.serviceCenter).addServiceRecord(h.tokenId, value);
    return { txs: [tx] };
  }
  async transferVehicle(h, to) {
    const tx = await this._nft(h.controller)["safeTransferFrom(address,address,uint256)"](h.controller.address, to.address, h.tokenId);
    h.controller = to;
    return { txs: [tx] };
  }
  async revokeDelegate(h) {
    const tx = await this._nft(h.controller).approve(this.ethers.ZeroAddress, h.tokenId);
    return { txs: [tx] };
  }
  async revokeAttribute() { this.notSupported("D2_revoke_attribute"); }
  async deactivate(h) {
    const tx = await this._nft(this.actors.deployer).deactivateVehicle(h.tokenId);
    return { txs: [tx] };
  }

  // Issuer identity is itself an NFT; the issuer's key is ownerOf(issuerToken).
  async anchorIssuerKey(issuer, key) {
    const vin = "ISS" + key.address.slice(2, 16).toUpperCase(); // 17 chars, unique per key
    const tx = await this._nft(this.actors.manufacturer).mintVehicle(key.address, vin, "issuer", "", 0, "", "");
    const tokenId = await this._tokenIdFromReceipt(tx);
    this.issuerHandles.set(issuer.address, { tokenId, controller: key });
    return { txs: [tx] };
  }
  async anchorStatus(h, credHash) {
    const tx = await this._nft(this.actors.serviceCenter).addServiceRecord(h.tokenId, "vc:active:" + credHash);
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash) {
    const tx = await this._nft(this.actors.serviceCenter).addServiceRecord(h.tokenId, "vc:revoked:" + credHash);
    return { txs: [tx] };
  }
  async statusCheck(h, credHash) {
    const records = await this.contracts.nft.getServiceRecords(h.tokenId);
    let status = "unknown";
    for (const r of records) {
      if (r === "vc:active:" + credHash) status = "active";
      if (r === "vc:revoked:" + credHash) status = "revoked";
    }
    return status;
  }

  async prepareThroughputSenders(senders) {
    const out = [];
    for (let i = 0; i < senders.length; i++) {
      await (await this._nft(this.actors.deployer).grantServiceCenterRole(senders[i].address)).wait();
      const v = this.dataset[900 + i];
      const { result } = await this.createIdentity(v, senders[i]);
      out.push({ sender: senders[i], handle: result });
    }
    return out;
  }
  async throughputOp(entry, i, overrides) {
    return this._nft(entry.sender).addServiceRecord(entry.handle.tokenId, this.payloads.serviceRecordURI, overrides);
  }
}

module.exports = { ERC721Adapter };
