"use strict";

class NotSupported extends Error {
  constructor(adapter, op, reason) {
    super(`${adapter}: ${op} not supported (${reason})`);
    this.notSupported = true;
    this.reason = reason;
  }
}

/**
 * Substrate adapter contract (framework §5). Mutating methods return
 * { txs: TransactionResponse[], result? }. Read methods return plain values.
 * `handle` is opaque to callers and carries whatever the substrate needs.
 */
class IdentityAdapter {
  static id = "abstract";
  static label = "abstract";
  static family = "abstract";

  constructor({ ethers, actors, dataset, payloads }) {
    this.ethers = ethers;
    this.actors = actors;
    this.dataset = dataset;
    this.payloads = payloads;
    this.contracts = {};
    this.unsupported = {}; // opId -> reason
  }

  supports(opId) { return !this.unsupported[opId]; }
  _issuer(issuer) { return issuer || this.actors.issuer; }
  notSupported(op) { throw new NotSupported(this.constructor.id, op, this.unsupported[op] || "no primitive"); }

  /** Deploy shared contracts. Returns [{name, contract}] for deployment accounting. */
  async deploy() { throw new Error("deploy not implemented"); }

  async createIdentity(vehicle, owner) { throw new Error("C1"); }
  async createIdentityWithAttributes(vehicle, owner) { throw new Error("C2"); }
  async resolveOwner(handle) { throw new Error("R1"); }
  async resolveByVin(vin) { throw new Error("R2"); }
  async resolveDocument(handle) { throw new Error("R3"); }
  async verifyDelegate(handle, key) { throw new Error("R4"); }
  async rotateController(handle, newOwner) { throw new Error("U1"); }
  async addDelegate(handle, key, ttl) { throw new Error("U2"); }
  async setAttribute(handle, name, value) { throw new Error("U3"); }
  async transferVehicle(handle, to) { throw new Error("U4"); }
  async metaTxSetAttribute(handle, name, value, relayer) { this.notSupported("U5_meta_tx"); }
  async revokeDelegate(handle, key) { throw new Error("D1"); }
  /**
   * Key rotation: `newKey` becomes a delegate and `oldKey` stops being one.
   * Default = U2(newKey) + D1(oldKey). A substrate whose delegate slot is
   * single-valued (ERC-721 `approve` replaces the previous approval) overrides
   * this with its one-tx primitive (review 02, H-2).
   */
  async rotateDelegate(handle, oldKey, newKey, ttl) {
    const a = await this.addDelegate(handle, newKey, ttl);
    const b = await this.revokeDelegate(handle, oldKey);
    return { txs: [...a.txs, ...b.txs] };
  }
  async revokeAttribute(handle, name) { throw new Error("D2"); }
  async deactivate(handle) { throw new Error("D3"); }

  // Credential layer. `issuer` defaults to actors.issuer; the crud scenario passes a
  // fresh issuer per iteration so cells do not depend on N (review 02, H-1).
  /** Unmeasured precondition: make `issuer` an issuer identity on this substrate. */
  async prepareIssuer(issuer) { /* default: an address is an identity */ }
  async anchorIssuerKey(issuer, key) { throw new Error("V1"); }
  async anchorStatus(handle, credHash, issuer) { throw new Error("V3"); }
  async revokeCredential(handle, credHash, issuer) { throw new Error("V5"); }
  async statusCheck(handle, credHash, issuer) { throw new Error("V6"); }

  /** Optional: prepare N senders for the throughput scenario; returns [{sender, handle}]. */
  async prepareThroughputSenders(senders) { throw new Error("throughput not implemented"); }
  async throughputOp(entry, i, overrides) { throw new Error("throughput not implemented"); }
}

module.exports = { IdentityAdapter, NotSupported };
