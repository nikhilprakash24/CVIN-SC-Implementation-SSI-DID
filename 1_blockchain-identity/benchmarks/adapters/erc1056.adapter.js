"use strict";
const { IdentityAdapter } = require("./IdentityAdapter");

const MAX_UINT = (1n << 256n) - 1n;

/**
 * ERC-1056: the controller address IS the DID (did:ethr:<address>). The
 * CVINVehicleDIDRegistry wrapper only adds the VIN mapping and manufacturer gate.
 * DID Document state lives in the event log, linked by `changed`/`previousChange`.
 */
class ERC1056Adapter extends IdentityAdapter {
  static id = "erc1056";
  static label = "ERC-1056";
  static family = "event-log registry (shared)";

  constructor(opts) {
    super(opts);
    const { keccak256, toUtf8Bytes } = this.ethers;
    this.K = {
      veriKey: keccak256(toUtf8Bytes("veriKey")),
      attr: keccak256(toUtf8Bytes(this.payloads.attributeName)),
      deactivated: keccak256(toUtf8Bytes(this.payloads.deactivatedName)),
      make: keccak256(toUtf8Bytes("did/vehicle/make")),
    };
  }

  async deploy() {
    const { ethers, actors } = this;
    const Reg = await ethers.getContractFactory("EthereumDIDRegistry", actors.deployer);
    const registry = await Reg.deploy();
    await registry.waitForDeployment();
    const Wrap = await ethers.getContractFactory("CVINVehicleDIDRegistry", actors.deployer);
    const wrapper = await Wrap.deploy(await registry.getAddress());
    await wrapper.waitForDeployment();
    await (await wrapper.setAuthorizedManufacturer(actors.manufacturer.address, true)).wait();
    this.contracts = { registry, wrapper };
    this.registryAddress = await registry.getAddress();
    return [{ name: "EthereumDIDRegistry", contract: registry }, { name: "CVINVehicleDIDRegistry", contract: wrapper }];
  }

  _reg(signer) { return this.contracts.registry.connect(signer); }
  _wrap(signer) { return this.contracts.wrapper.connect(signer); }

  // ---- CREATE ---------------------------------------------------------------
  async createIdentity(v, owner) {
    const tx = await this._wrap(this.actors.manufacturer).createVehicleDID(
      v.vin, owner.address, "", "", 0, "", "", 0, ""
    );
    return { txs: [tx], result: { did: owner.address, vin: v.vin, controller: owner, attrs: {} } };
  }

  // Pure did:ethr mode: the controller publishes the VID-I attribute set directly on
  // the registry (one event per attribute). The wrapper's single-tx
  // setVehicleAttributes needs the wrapper to hold ERC-1056 control of the DID
  // (wrapper-controlled mode); that variant is a separate adapter (future work).
  async createIdentityWithAttributes(v, owner) {
    const tx1 = await this._wrap(this.actors.manufacturer).createVehicleDID(
      v.vin, owner.address, v.make, v.model, v.year, v.color, v.engineNumber, v.manufacturingDate, v.autonomyLevel
    );
    const reg = this._reg(owner);
    const { toUtf8Bytes, keccak256 } = this.ethers;
    const attrs = [
      ["did/vehicle/vin", v.vin], ["did/vehicle/make", v.make], ["did/vehicle/model", v.model], ["did/vehicle/year", String(v.year)],
      ["did/vehicle/color", v.color], ["did/vehicle/engineNumber", v.engineNumber], ["did/vehicle/manufacturingDate", String(v.manufacturingDate)], ["did/vehicle/autonomyLevel", v.autonomyLevel],
    ];
    const txs = [tx1];
    for (const [k, val] of attrs) txs.push(await reg.setAttribute(owner.address, keccak256(toUtf8Bytes(k)), toUtf8Bytes(val), this.payloads.ttlSeconds));
    return { txs, result: { did: owner.address, vin: v.vin, controller: owner, attrs: {} } };
  }

  // ---- READ -----------------------------------------------------------------
  async resolveOwner(h) { return this.contracts.registry.identityOwner(h.did); }
  async resolveByVin(vin) { return this.contracts.wrapper.getDIDFromVIN(vin); }
  async verifyDelegate(h, key) { return this.contracts.registry.validDelegate(h.did, this.K.veriKey, key.address); }

  /** Walk the `changed` linked list over eth_getLogs (as ethr-did-resolver does). */
  async resolveDocument(h) {
    const reg = this.contracts.registry;
    const iface = reg.interface;
    const topicId = this.ethers.zeroPadValue(h.did, 32);
    let block = Number(await reg.changed(h.did));
    const events = [];
    const visited = new Set();
    while (block > 0 && !visited.has(block)) {
      visited.add(block);
      const logs = await this.ethers.provider.getLogs({
        address: this.registryAddress, fromBlock: block, toBlock: block, topics: [null, topicId],
      });
      let prev = 0;
      for (const log of logs) {
        const parsed = iface.parseLog(log);
        events.push({ name: parsed.name, args: parsed.args });
        const pc = Number(parsed.args.previousChange);
        if (pc < block && pc > prev) prev = pc;
      }
      block = prev;
    }
    const owner = await reg.identityOwner(h.did);
    const now = Math.floor(Date.now() / 1000);
    const doc = {
      "@context": ["https://www.w3.org/ns/did/v1"],
      id: `did:ethr:31337:${h.did}`,
      controller: `did:ethr:31337:${owner}`,
      verificationMethod: [{ id: "#controller", type: "EcdsaSecp256k1RecoveryMethod2020", controller: `did:ethr:31337:${h.did}`, blockchainAccountId: `eip155:31337:${owner}` }],
      authentication: ["#controller"],
      service: [],
      attributes: {},
    };
    for (const e of events.reverse()) {
      if (e.name === "DIDDelegateChanged" && Number(e.args.validTo) > now) {
        doc.verificationMethod.push({ id: `#delegate-${e.args.delegate}`, type: "EcdsaSecp256k1RecoveryMethod2020", blockchainAccountId: `eip155:31337:${e.args.delegate}` });
      } else if (e.name === "DIDAttributeChanged") {
        const validTo = e.args.validTo;
        doc.attributes[e.args.name] = validTo === 0n ? null : e.args.value;
      }
    }
    return doc;
  }

  // ---- UPDATE ---------------------------------------------------------------
  async rotateController(h, newOwner) {
    const tx = await this._reg(h.controller).changeOwner(h.did, newOwner.address);
    h.controller = newOwner;
    return { txs: [tx] };
  }
  async addDelegate(h, key, ttl) {
    const tx = await this._reg(h.controller).addDelegate(h.did, this.K.veriKey, key.address, ttl);
    return { txs: [tx] };
  }
  async setAttribute(h, name, value) {
    const nameHash = this.ethers.keccak256(this.ethers.toUtf8Bytes(name));
    const tx = await this._reg(h.controller).setAttribute(h.did, nameHash, this.ethers.toUtf8Bytes(value), this.payloads.ttlSeconds);
    h.attrs[name] = value;
    return { txs: [tx] };
  }
  async transferVehicle(h, to) {
    // did:ethr semantics: identifier persists, controller changes (1 tx).
    return this.rotateController(h, to);
  }
  async metaTxSetAttribute(h, name, value, relayer) {
    const { ethers } = this;
    const reg = this.contracts.registry;
    const nameHash = ethers.keccak256(ethers.toUtf8Bytes(name));
    const valueBytes = ethers.toUtf8Bytes(value);
    const owner = await reg.identityOwner(h.did);
    const nonce = await reg.nonce(owner);
    const digest = ethers.keccak256(ethers.concat([
      "0x19", "0x00", this.registryAddress,
      ethers.zeroPadValue(ethers.toBeHex(nonce), 32),
      h.did,
      ethers.toUtf8Bytes("setAttribute"),
      nameHash, valueBytes,
      ethers.zeroPadValue(ethers.toBeHex(this.payloads.ttlSeconds), 32),
    ]));
    const sig = h.controller.signingKey.sign(digest);
    const tx = await reg.connect(relayer).setAttributeSigned(h.did, sig.v, sig.r, sig.s, nameHash, valueBytes, this.payloads.ttlSeconds);
    return { txs: [tx] };
  }

  // ---- DELETE ---------------------------------------------------------------
  async revokeDelegate(h, key) {
    const tx = await this._reg(h.controller).revokeDelegate(h.did, this.K.veriKey, key.address);
    return { txs: [tx] };
  }
  async revokeAttribute(h, name) {
    const nameHash = this.ethers.keccak256(this.ethers.toUtf8Bytes(name));
    const tx = await this._reg(h.controller).revokeAttribute(h.did, nameHash, this.ethers.toUtf8Bytes(h.attrs[name] || ""));
    return { txs: [tx] };
  }
  async deactivate(h) {
    // ERC-1056 has no deactivate primitive (owner=0x0 resolves to self): publish a permanent attribute.
    const tx = await this._reg(h.controller).setAttribute(h.did, this.K.deactivated, this.ethers.toUtf8Bytes("true"), MAX_UINT - BigInt(Math.floor(Date.now() / 1000)) - 10_000_000n);
    return { txs: [tx] };
  }

  // ---- CREDENTIAL ANCHORS ---------------------------------------------------
  async anchorIssuerKey(issuer, key) {
    const tx = await this._reg(issuer).addDelegate(issuer.address, this.K.veriKey, key.address, this.payloads.ttlSeconds);
    return { txs: [tx] };
  }
  async anchorStatus(h, credHash) {
    // status attribute keyed by credential hash on the *issuer's* DID
    const issuer = this.actors.issuer;
    const tx = await this._reg(issuer).setAttribute(issuer.address, credHash, this.ethers.toUtf8Bytes("active"), this.payloads.ttlSeconds);
    return { txs: [tx] };
  }
  async revokeCredential(h, credHash) {
    const issuer = this.actors.issuer;
    const tx = await this._reg(issuer).revokeAttribute(issuer.address, credHash, this.ethers.toUtf8Bytes("active"));
    return { txs: [tx] };
  }
  async statusCheck(h, credHash) {
    const issuer = this.actors.issuer.address;
    const logs = await this.ethers.provider.getLogs({
      address: this.registryAddress, fromBlock: 0, toBlock: "latest",
      topics: [this.contracts.registry.interface.getEvent("DIDAttributeChanged").topicHash, this.ethers.zeroPadValue(issuer, 32)],
    });
    let status = "unknown";
    for (const log of logs) {
      const p = this.contracts.registry.interface.parseLog(log);
      if (p.args.name === credHash) status = p.args.validTo === 0n ? "revoked" : "active";
    }
    return status;
  }

  // ---- THROUGHPUT -----------------------------------------------------------
  async prepareThroughputSenders(senders) {
    return senders.map((s) => ({ sender: s, handle: { did: s.address, controller: s } }));
  }
  async throughputOp(entry, i, overrides) {
    const reg = this._reg(entry.sender);
    return reg.setAttribute(entry.handle.did, this.K.attr, this.ethers.toUtf8Bytes(this.payloads.attributeValue), this.payloads.ttlSeconds, overrides);
  }
}

module.exports = { ERC1056Adapter };
