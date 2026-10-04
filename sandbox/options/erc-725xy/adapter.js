'use strict';
/**
 * ERC-725 X+Y smart-account adapter (slug: erc-725xy).
 *
 * Contracts (1_blockchain-identity/contracts/ERC725xy):
 *   CVINVehicleERC725XY   per-vehicle ERC-725X executor + ERC-725Y data store, single owner
 *   CVINExecuteTarget     test helper only: observable side effect for the execute() demonstration
 * There is NO shared registry: each identity is its own account contract, so deploying one
 * IS identity creation and its deployment gas IS the creation cost. Identity id = the
 * account's contract address; constructor(initialOwner) sets the controlling key.
 *
 * Method -> contract function mapping (the thesis cites this table):
 *   deploy            nothing to deploy (no registry) -> { ok, address: null, gasUsed: 0n }
 *   create            new CVINVehicleERC725XY(owner) by the deployer, then setData(VIN_KEY, bytes(vin))
 *                     sent by owner (VIN anchored in the ERC-725Y store; skipped with a note when
 *                     `owner` is not a local signer). gasUsed = deploy + setData; the note gives both.
 *   changeController  transferOwnership(newOwner) sent by owner() (controlling-key rotation; the
 *                     account address / identity is unchanged)
 *   addKeyOrDelegate  NotApplicable: ERC-725 X/Y has a single owner and no key/delegate model
 *                     (benchmark_ops.addDelegateOrClaim). The manifest lists OPERATION_DELEGATECALL
 *                     under "Key / delegate management", but that is an executor opcode, not a
 *                     delegation of identity authority — reported as a manifest inconsistency.
 *   setAttribute      setData(keccak256(key), bytes(value)) sent by owner() (a bytes32 key is used as-is)
 *   addClaim          NotApplicable: no claim model (claims live in the ERC-735 claim holder)
 *   revoke            no identity-level revocation primitive (manifest: not-applicable). The
 *                     non-standard analogue setData(key, 0x) clears an attribute: { id, key } clears
 *                     that key; a bare id clears the most recent attribute this adapter set for the
 *                     identity, else NotApplicable.
 *   transfer          NotApplicable: the identity is a contract account, not a token; ownership moves
 *                     with transferOwnership (= changeController).
 *   signedOp          execute(OPERATION_CALL=0, target, 0, setValue(n)) sent by owner() against a
 *                     CVINExecuteTarget (deployed lazily by the deployer; its gas is reported in the
 *                     note, not in gasUsed). The call is REAL: the adapter checks
 *                     target.lastCaller() == identity afterwards. execute is msg.sender-gated: no
 *                     signature is verified (argument ignored). { op: 'execute', to, value, data,
 *                     operationType } runs a generic operation; any other op name (e.g. 'changeOwner')
 *                     runs the CVINExecuteTarget demonstration (transferOwnership cannot be routed
 *                     through execute: the account is not its own owner).
 *   resolve           on-chain reads only: owner(), getDataBatch([VIN_KEY, MAKE_KEY, MODEL_KEY,
 *                     YEAR_KEY]), getData for keys set through this adapter, supportsInterface.
 *   capabilities      mirrors manifest.yaml
 */
const { NotApplicable } = require('../../lib/identity_option');

const CONTRACT = 'CVINVehicleERC725XY';
const TARGET = 'CVINExecuteTarget';
const OPERATION_CALL = 0;

class Erc725xyAdapter {
  static get slug() { return 'erc-725xy'; }

  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.identities = new Map();   // id -> Contract handle
    this.target = null;            // CVINExecuteTarget (lazy)
    this._attrKeys = new Map();    // id -> [{ key, name }] set through this adapter
    this._names = new Map();       // dataKey -> name (display aid)
    for (const n of ['cvin:vin', 'cvin:make', 'cvin:model', 'cvin:year']) this._names.set(this._h(n), n);
  }

  // ---------- helpers ----------
  _h(s) { return this.ethers.keccak256(this.ethers.toUtf8Bytes(s)); }
  _b32(s) { return this.ethers.isHexString(s, 32) ? s : this._h(s); }
  _bytes(v) {
    if (v == null) return '0x';
    if (v instanceof Uint8Array) return this.ethers.hexlify(v);
    return this.ethers.isHexString(v) ? v : this.ethers.hexlify(this.ethers.toUtf8Bytes(String(v)));
  }
  _allSigners() { return Object.values(this.signers).flat().filter(Boolean); }
  _signerFor(addr, required = true) {
    const a = String(addr).toLowerCase();
    const s = this._allSigners().find((x) => x.address.toLowerCase() === a);
    if (!s && required) throw new Error(`erc-725xy: no local signer for ${addr}`);
    return s || null;
  }
  async _contract(id) {
    const k = String(id).toLowerCase();
    if (!this.identities.has(k)) this.identities.set(k, await this.ethers.getContractAt(CONTRACT, id, this.signers.deployer));
    return this.identities.get(k);
  }
  async _ownerSigner(c) { return this._signerFor(await c.owner()); }

  // ---------- interface ----------
  async deploy() {
    return { ok: true, address: null, gasUsed: 0n, note: 'no shared registry; each identity is its own ERC-725 account, deployed by create()' };
  }

  async attach(address) {
    await this._contract(address);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner } = {}) {
    const target = owner || this.signers.vehicleOwner.address;
    const F = await this.ethers.getContractFactory(CONTRACT, this.signers.deployer);
    const c = await F.deploy(target);
    const r1 = await c.deploymentTransaction().wait();
    const id = await c.getAddress();
    this.identities.set(id.toLowerCase(), c);
    let gasUsed = r1.gasUsed;
    let note = `deploy=${r1.gasUsed} (account deployment is the creation cost; owner=${target.slice(0, 8)}…)`;
    const ownerSigner = this._signerFor(target, false);
    if (vin && ownerSigner) {
      const r2 = await (await c.connect(ownerSigner).setData(await c.VIN_KEY(), this._bytes(vin))).wait();
      gasUsed += r2.gasUsed;
      note += ` +setData(VIN_KEY)=${r2.gasUsed}`;
    } else if (vin) {
      note += '; VIN not written (owner is not a local signer)';
    }
    return { ok: true, id, receipt: r1, gasUsed, note };
  }

  async changeController(id, newController) {
    const c = await this._contract(id);
    const receipt = await (await c.connect(await this._ownerSigner(c)).transferOwnership(newController)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'transferOwnership (controlling-key rotation; account address unchanged)' };
  }

  async addKeyOrDelegate() {
    return new NotApplicable('ERC-725 X/Y has a single owner and no key/delegate model; OPERATION_DELEGATECALL is an executor opcode, not identity delegation');
  }

  async setAttribute(id, key, value) {
    const c = await this._contract(id);
    const dataKey = this._b32(key);
    if (!this.ethers.isHexString(key, 32)) this._names.set(dataKey, key);
    const receipt = await (await c.connect(await this._ownerSigner(c)).setData(dataKey, this._bytes(value))).wait();
    const k = String(id).toLowerCase();
    if (!this._attrKeys.has(k)) this._attrKeys.set(k, []);
    this._attrKeys.get(k).push({ key: dataKey, name: key });
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'setData (ERC-725Y store, DataChanged)' };
  }

  async addClaim() {
    return new NotApplicable('no claim model in ERC-725 X/Y; claims live in the ERC-735 claim holder');
  }

  async revoke(target) {
    let id;
    let dataKey;
    let name;
    if (typeof target === 'object' && target !== null) {
      id = target.id;
      if (target.key != null) { dataKey = this._b32(target.key); name = target.key; }
    } else {
      id = target;
      const last = (this._attrKeys.get(String(id).toLowerCase()) || []).pop();
      if (last) { dataKey = last.key; name = last.name; }
    }
    if (!id || !dataKey) {
      return new NotApplicable('ERC-725 has no identity-level revocation primitive; setData(key, 0x) clears an attribute (none known for this id — pass { id, key }) and renounceOwnership abandons control');
    }
    const c = await this._contract(id);
    const receipt = await (await c.connect(await this._ownerSigner(c)).setData(dataKey, '0x')).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `setData(${name}, 0x) — non-standard attribute clear, not an identity revocation` };
  }

  async transfer() {
    return new NotApplicable('identity is a contract account, not a token; ownership moves with transferOwnership (changeController)');
  }

  async _ensureTarget() {
    if (!this.target) {
      const F = await this.ethers.getContractFactory(TARGET, this.signers.deployer);
      this.target = await F.deploy();
      const r = await this.target.deploymentTransaction().wait();
      this._targetGas = r.gasUsed;
    }
    return this.target;
  }

  async signedOp(id, op = 'execute', _signature = '0x') {
    const c = await this._contract(id);
    const signer = await this._ownerSigner(c);
    let receipt;
    let note;
    if (typeof op === 'object' && op !== null && op.op === 'execute' && op.to) {
      receipt = await (await c.connect(signer).execute(Number(op.operationType || 0), op.to, BigInt(op.value || 0), op.data || '0x')).wait();
      note = `execute(${Number(op.operationType || 0)}, ${op.to.slice(0, 8)}…) custom`;
    } else {
      const name = typeof op === 'string' ? op : op.op;
      const t = await this._ensureTarget();
      const n = BigInt(Date.now() % 1000000);
      const data = t.interface.encodeFunctionData('setValue', [n]);
      receipt = await (await c.connect(signer).execute(OPERATION_CALL, await t.getAddress(), 0, data)).wait();
      const [caller, v] = await Promise.all([t.lastCaller(), t.value()]);
      const applied = caller.toLowerCase() === String(id).toLowerCase() && v === n;
      note = `execute(CALL, CVINExecuteTarget, 0, setValue(${n})) — real call, msg.sender==identity: ${applied}; target deploy=${this._targetGas} not counted${name !== 'execute' ? `; op '${name}' mapped to this demo` : ''}`;
    }
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `${note}; owner-gated by msg.sender, signature ignored` };
  }

  async resolve(id) {
    const E = this.ethers;
    const c = await this._contract(id);
    const [owner, vinKey, makeKey, modelKey, yearKey, net] = await Promise.all([
      c.owner(), c.VIN_KEY(), c.MAKE_KEY(), c.MODEL_KEY(), c.YEAR_KEY(), E.provider.getNetwork(),
    ]);
    const [vinB, makeB, modelB, yearB] = await c.getDataBatch([vinKey, makeKey, modelKey, yearKey]);
    const utf8 = (b) => { if (!b || b === '0x') return ''; try { return E.toUtf8String(b); } catch (_) { return b; } };
    const attributes = {};
    for (const { key, name } of this._attrKeys.get(String(id).toLowerCase()) || []) {
      const v = await c.getData(key);
      if (v && v !== '0x') attributes[name] = utf8(v);
    }
    const [x, y] = await Promise.all([c.supportsInterface('0x7545acac'), c.supportsInterface('0x629aa694')]);
    const did = `did:erc725:0x${net.chainId.toString(16)}:${id}`;
    const value = {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: owner,
      verificationMethod: [{ id: `${did}#owner`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${net.chainId}:${owner}` }],
      authentication: [`${did}#owner`],
      vehicle: {
        vin: utf8(vinB), make: utf8(makeB), model: utf8(modelB),
        year: yearB && yearB !== '0x' ? Number(E.AbiCoder.defaultAbiCoder().decode(['uint256'], yearB)[0]) : null,
        attributes,
      },
      meta: { contract: CONTRACT, address: id, erc725x: x, erc725y: y },
    };
    return { ok: true, value, note: `owner=${owner.slice(0, 8)}… vin=${utf8(vinB) || '-'} attrs=${Object.keys(attributes).length}` };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: 'single owner; no key/delegate model in ERC-725 X/Y',
      setAttribute: true,
      addClaim: 'no claim model; claims live in the ERC-735 claim holder',
      revoke: 'no identity-level revocation; setData(key, 0x) clears an attribute',
      transfer: 'contract account, not a token; ownership moves via transferOwnership',
      signedOp: true,
      resolve: true,
      capabilities: true,
    };
  }
}

module.exports = Erc725xyAdapter;
