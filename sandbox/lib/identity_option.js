'use strict';
/**
 * The uniform IdentityOption interface every per-option adapter implements
 * (docs/PLAN_SANDBOX_AND_SUITES.md §1). Adapters wrap the canonical contracts in
 * 1_blockchain-identity/contracts via their compiled artifacts; they never copy code.
 *
 * Every method returns a Result:
 *   { ok: true,  receipt?, gasUsed?, value?, note? }           — the operation ran
 *   NotApplicable(reason)                                        — the option has no such
 *                                                                  capability (first-class,
 *                                                                  never an exception)
 * Adapters must not throw for unsupported capabilities; they may throw for real errors.
 *
 * Ids are strings: the identity's address, token id, or contract address, as the
 * option defines identity. `create` returns the id. For options where identity is
 * implicit (no transaction), `create` returns { ok: true, implicit: true, gasUsed: 0n }.
 */

class NotApplicable {
  constructor(reason) { this.ok = false; this.notApplicable = true; this.reason = reason; }
  toString() { return `NotApplicable(${this.reason})`; }
}

/** Method names and their meaning; adapters implement all of them. */
const METHODS = Object.freeze({
  deploy:            'deploy() -> { ok, address, gasUsed }  (or attach(address))',
  create:            'create({ vin, owner }) -> { ok, id, receipt, gasUsed } | { ok, id, implicit: true, gasUsed: 0n }',
  changeController:  'changeController(id, newController) -> Result',
  addKeyOrDelegate:  'addKeyOrDelegate(id, key, purpose, validitySeconds) -> Result | NotApplicable',
  setAttribute:      'setAttribute(id, key, value) -> Result | NotApplicable',
  addClaim:          'addClaim(id, topic, data, signature) -> Result | NotApplicable',
  revoke:            'revoke(id | claimId) -> Result',
  transfer:          'transfer(id, to) -> Result | NotApplicable',
  resolve:           'resolve(id) -> { ok, value: didDocumentLike }',
  signedOp:          'signedOp(id, op, signature) -> Result | NotApplicable   (off-chain-authorised execution)',
  capabilities:      'capabilities() -> { [method]: true | string reason }   (mirrors the manifest)',
});

/** Minimal conformance check used by the smoke runner and L1. */
function assertImplements(adapter, name) {
  const missing = Object.keys(METHODS).filter((m) => typeof adapter[m] !== 'function');
  if (missing.length) throw new Error(`${name}: adapter lacks ${missing.join(', ')}`);
}

function isNA(r) { return r && r.notApplicable === true; }

module.exports = { NotApplicable, METHODS, assertImplements, isNA };
