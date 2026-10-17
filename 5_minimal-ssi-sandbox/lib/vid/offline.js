// Connectivity model for the delayed-write scenario (S14).
//
// An OBU (or edge agent) runs in one of three modes:
//   ONLINE      – reads and writes go to the chain immediately.
//   READ_ONLY   – the chain is reachable for reads but writes are refused (congested
//                 relayer, no gas sponsor, policy). Signed events are queued.
//   PARTITIONED – nothing is reachable. Reads come from the cache (within its staleness
//                 window) and signed events are queued.
// On reconnect the queue is reconciled: events are ordered by (issuer timestamp, local
// counter), checked against the chain's *current* state (a credential revoked during the
// outage invalidates events that depended on it — "revocation wins"), and the survivors are
// anchored in one batch. Everything queued is a signed off-chain object, so the trace shows
// `offchain` entries with kind=queued followed by a single `tx`.
const crypto = require("crypto");
const { ethers } = require("ethers");

const MODE = { ONLINE: "ONLINE", READ_ONLY: "READ_ONLY", PARTITIONED: "PARTITIONED" };

class Link {
  constructor() { this.mode = MODE.ONLINE; }
  set(mode) { this.mode = mode; }
  canRead() { return this.mode !== MODE.PARTITIONED; }
  canWrite() { return this.mode === MODE.ONLINE; }
}

// Queue of signed, counter-ordered events held by a principal that cannot write.
class WriteQueue {
  constructor(signer, did) { this.signer = signer; this.did = did; this.counter = 0; this.items = []; }
  async enqueue(kind, payload, dependsOn = []) {
    const item = { kind, counter: ++this.counter, localTs: Date.now(), issuer: this.did, payload, dependsOn };
    const digest = ethers.keccak256(ethers.toUtf8Bytes(JSON.stringify(item)));
    item.sig = await this.signer.signMessage(ethers.getBytes(digest));
    item.digest = digest;
    this.items.push(item);
    return item;
  }
  drain() { const out = [...this.items].sort((a, b) => a.localTs - b.localTs || a.counter - b.counter); this.items = []; return out; }
}

// Reconciliation: returns {accepted, rejected} given a predicate that consults current chain state.
async function reconcile(items, stillValid) {
  const accepted = [], rejected = [];
  for (const it of items) {
    const reasons = [];
    for (const dep of it.dependsOn) if (!(await stillValid(dep))) reasons.push(`dependency ${dep.slice(0, 10)}… no longer valid`);
    (reasons.length ? rejected : accepted).push({ ...it, reasons });
  }
  return { accepted, rejected };
}

const nonce = () => crypto.randomBytes(8).toString("hex");

module.exports = { MODE, Link, WriteQueue, reconcile, nonce };
