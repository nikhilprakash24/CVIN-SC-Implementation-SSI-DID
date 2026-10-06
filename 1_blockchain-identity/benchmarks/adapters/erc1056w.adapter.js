"use strict";
const { ERC1056Adapter } = require("./erc1056.adapter");

// Same fixed "permanent" validity as the pure adapter (no zero byte, no overflow).
const PERMANENT_VALIDITY = (1n << 256n) - 1n - (1n << 40n);

/**
 * ERC-1056, CVIN wrapper-controlled mode: at creation the vehicle owner hands
 * ERC-1056 control of the DID to CVINVehicleDIDRegistry (changeOwner(did, wrapper)).
 * All later mutations go through the wrapper, which tracks the vehicle owner in
 * `vehicleOwners` and gates on it (vehicleOwnerOf). Trade-offs vs pure did:ethr mode:
 *  + VID-I attributes in one tx (setVehicleAttributes), one-tx ownership transfer
 *  - no meta-tx path (the wrapper has no signed entry points)
 *  - no attribute revocation entry point (D2 is n/a)
 *  - ownership transfers do not emit DIDOwnerChanged on the registry: a plain
 *    did:ethr resolver reports the wrapper as controller (fidelity gap, T2)
 * Credential ops (issuer side) are inherited: the issuer uses the registry directly.
 */
class ERC1056WrapperAdapter extends ERC1056Adapter {
  static id = "erc1056w";
  static label = "ERC-1056 (wrapper)";
  static family = "event-log registry (shared), wrapper-controlled";

  constructor(opts) {
    super(opts);
    this.unsupported["U5_meta_tx"] = "wrapper holds ERC-1056 control; no signed entry point";
    // setServiceEndpoint(validity 0) only yields validTo = block.timestamp ("expire now"
    // relative to chain time), not the validTo = 0 that revokeAttribute emits; the
    // wrapper has no revoke entry point, so D2 is reported as n/a rather than approximated.
    this.unsupported["D2_revoke_attribute"] = "wrapper exposes no revokeAttribute; setServiceEndpoint cannot emit validTo = 0";
  }

  async createIdentity(v, owner) {
    const tx1 = await this._wrap(this.actors.manufacturer).createVehicleDID(v.vin, owner.address, "", "", 0, "", "", 0, "");
    const tx2 = await this._reg(owner).changeOwner(owner.address, await this.contracts.wrapper.getAddress());
    return { txs: [tx1, tx2], result: { did: owner.address, vin: v.vin, controller: owner, attrs: {} } };
  }

  async createIdentityWithAttributes(v, owner) {
    const { txs, result } = await this.createIdentity(v, owner);
    txs.push(await this._wrap(owner).setVehicleAttributes(owner.address, v.make, v.model, v.year, v.color, v.engineNumber, v.manufacturingDate, v.autonomyLevel));
    return { txs, result };
  }

  async resolveOwner(h) { return this.contracts.wrapper.vehicleOwnerOf(h.did); }
  async verifyDelegate(h, key) { return this.contracts.wrapper.isValidDelegate(h.did, this.K.veriKey, key.address); }

  async rotateController(h, newOwner) {
    const tx = await this._wrap(h.controller).transferVehicleOwnership(h.did, newOwner.address);
    h.controller = newOwner;
    return { txs: [tx] };
  }
  async transferVehicle(h, to) { return this.rotateController(h, to); }

  async addDelegate(h, key, ttl) {
    const tx = await this._wrap(h.controller).addVerificationDelegate(h.did, key.address, this.K.veriKey, ttl);
    return { txs: [tx] };
  }
  async revokeDelegate(h, key) {
    const tx = await this._wrap(h.controller).revokeVerificationDelegate(h.did, key.address, this.K.veriKey);
    return { txs: [tx] };
  }
  async setAttribute(h, name, value) {
    const nameHash = this.ethers.keccak256(this.ethers.toUtf8Bytes(name));
    const tx = await this._wrap(h.controller).setServiceEndpoint(h.did, nameHash, value, this.payloads.ttlSeconds);
    h.attrs[name] = value;
    return { txs: [tx] };
  }
  async revokeAttribute() { this.notSupported("D2_revoke_attribute"); }
  async deactivate(h) {
    const tx = await this._wrap(h.controller).setServiceEndpoint(h.did, this.K.deactivated, "true", PERMANENT_VALIDITY);
    return { txs: [tx] };
  }
  async metaTxSetAttribute() { this.notSupported("U5_meta_tx"); }

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
    return this._wrap(entry.sender).setServiceEndpoint(entry.handle.did, this.K.attr, this.payloads.attributeValue, this.payloads.ttlSeconds, overrides);
  }
}

module.exports = { ERC1056WrapperAdapter };
