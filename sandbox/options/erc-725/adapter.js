'use strict';
/**
 * ERC-725 (basic proxy account) adapter (slug: erc-725).
 *
 * Contract: 1_blockchain-identity/contracts/ERC725/CVIN_DID_ERC725.sol, contract name
 * CVIN_SCBasedAccOrID_DID_ERC725Basic. There is NO shared registry: every identity is its
 * own proxy-account contract, so deploying one proxy IS identity creation and its
 * deployment gas IS the creation cost (benchmark_ops.createIdentity). Identity id = the
 * proxy's contract address; the deployer (msg.sender of the constructor) is the owner
 * (the ERC-734 MANAGEMENT-key role).
 *
 * Method -> contract function mapping (the thesis cites this table):
 *   deploy            nothing to deploy (no registry) -> { ok, address: null, gasUsed: 0n }
 *   create            new CVIN_SCBasedAccOrID_DID_ERC725Basic() sent by `owner`'s signer (constructor
 *                     sets msg.sender as owner). If `owner` is not a local signer the deployer deploys
 *                     and then transferOwnership(owner); gasUsed is the sum. The VIN is not stored
 *                     (this variant has no data store; VIN linkage: not-applicable).
 *   changeController  transferOwnership(newOwner) sent by owner()
 *   addKeyOrDelegate  addKey(keyId, purpose, keyType=1 ECDSA) where keyId = keccak256(abi.encode(address))
 *                     (ERC-734 key-id convention) and purpose maps management=1, action/veriKey/sigAuth=2,
 *                     claim=3, encryption=4 (numbers pass through). ERC-725 keys carry NO validity:
 *                     validitySeconds is ignored and the note says so.
 *   setAttribute      NotApplicable: no attribute/data store in this basic variant (see erc-725xy for
 *                     ERC-725Y setData).
 *   addClaim          NotApplicable: claims live in the companion ERC-735 claim holder (erc-735 option).
 *   revoke            removeKey(keyId): bare id -> the most recent key this adapter added for that
 *                     identity; { id, key } -> that key. Identity-level revocation does not exist
 *                     (manifest: Revocation/status not-applicable) -> NotApplicable when no key is known.
 *   transfer          NotApplicable: the identity is a contract account, not a token; ownership moves
 *                     with transferOwnership (= changeController). approve(uint256,bool) is an
 *                     unimplemented stub.
 *   signedOp          execute(operationType=0 CALL, to, value, data) sent by owner(). This is the
 *                     "delegated execution" surface of the manifest, but it is msg.sender-gated: no
 *                     signature is verified (the signature argument is ignored) and in this basic
 *                     variant execute only emits Executed -- it performs no call, so the encoded
 *                     operation is not applied. op 'changeOwner' is encoded as transferOwnership(newOwner)
 *                     calldata against the identity itself; { op: 'execute', to, value, data } is generic.
 *   resolve           on-chain reads only: owner(), getKeys(), getKey(keyId) for each key.
 *   capabilities      mirrors manifest.yaml
 */
const { NotApplicable } = require('../../lib/identity_option');

const CONTRACT = 'CVIN_SCBasedAccOrID_DID_ERC725Basic';
const PURPOSES = { management: 1, action: 2, verikey: 2, sigauth: 2, claim: 3, encryption: 4 };
const PURPOSE_NAMES = { 1: 'MANAGEMENT', 2: 'ACTION', 3: 'CLAIM', 4: 'ENCRYPTION' };
const KEY_TYPES = { 1: 'ECDSA', 2: 'RSA' };

class Erc725Adapter {
  static get slug() { return 'erc-725'; }

  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.identities = new Map(); // id -> Contract (handle only; state is always read on-chain)
    this._keys = new Map();      // id -> [keyId] added through this adapter (for bare-id revoke)
  }

  // ---------- helpers ----------
  _allSigners() { return Object.values(this.signers).flat().filter(Boolean); }
  _signerFor(addr, required = true) {
    const a = String(addr).toLowerCase();
    const s = this._allSigners().find((x) => x.address.toLowerCase() === a);
    if (!s && required) throw new Error(`erc-725: no local signer for ${addr}`);
    return s || null;
  }
  async _contract(id) {
    const k = String(id).toLowerCase();
    if (!this.identities.has(k)) this.identities.set(k, await this.ethers.getContractAt(CONTRACT, id, this.signers.deployer));
    return this.identities.get(k);
  }
  async _ownerSigner(c) { return this._signerFor(await c.owner()); }
  _keyId(key) {
    if (this.ethers.isHexString(key, 32)) return key;
    if (this.ethers.isAddress(key)) return this.ethers.keccak256(this.ethers.AbiCoder.defaultAbiCoder().encode(['address'], [key]));
    return this.ethers.keccak256(this.ethers.toUtf8Bytes(String(key)));
  }
  _purpose(p) {
    if (typeof p === 'number' || typeof p === 'bigint') return Number(p);
    if (/^\d+$/.test(String(p))) return Number(p);
    return PURPOSES[String(p).toLowerCase()] || 2;
  }

  // ---------- interface ----------
  async deploy() {
    return { ok: true, address: null, gasUsed: 0n, note: 'no shared registry; each identity is its own proxy, deployed by create()' };
  }

  async attach(address) {
    await this._contract(address);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner } = {}) {
    const target = owner || this.signers.vehicleOwner.address;
    const ownerSigner = this._signerFor(target, false);
    const F = await this.ethers.getContractFactory(CONTRACT, ownerSigner || this.signers.deployer);
    const c = await F.deploy();
    const r1 = await c.deploymentTransaction().wait();
    const id = await c.getAddress();
    this.identities.set(id.toLowerCase(), c);
    let gasUsed = r1.gasUsed;
    let note = `proxy deployment is the creation cost (owner = deployer of the proxy); vin=${vin || '-'} not stored (no data store)`;
    if (!ownerSigner) {
      const r2 = await (await c.connect(this.signers.deployer).transferOwnership(target)).wait();
      gasUsed += r2.gasUsed;
      note += `; +transferOwnership(${target.slice(0, 8)}…)=${r2.gasUsed}`;
    }
    return { ok: true, id, receipt: r1, gasUsed, note };
  }

  async changeController(id, newController) {
    const c = await this._contract(id);
    const receipt = await (await c.connect(await this._ownerSigner(c)).transferOwnership(newController)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'transferOwnership' };
  }

  async addKeyOrDelegate(id, key, purpose = 'action', validitySeconds) {
    const c = await this._contract(id);
    const keyId = this._keyId(key);
    const p = this._purpose(purpose);
    const receipt = await (await c.connect(await this._ownerSigner(c)).addKey(keyId, p, 1)).wait();
    const k = String(id).toLowerCase();
    if (!this._keys.has(k)) this._keys.set(k, []);
    this._keys.get(k).push(keyId);
    return {
      ok: true, receipt, gasUsed: receipt.gasUsed, keyId,
      note: `addKey(purpose=${p} ${PURPOSE_NAMES[p] || ''}, type=1 ECDSA); no expiry — validitySeconds${validitySeconds != null ? `=${validitySeconds}` : ''} ignored`,
    };
  }

  async setAttribute() {
    return new NotApplicable('no attribute/data store in the ERC-725 basic proxy (ERC-725Y setData is the erc-725xy option)');
  }

  async addClaim() {
    return new NotApplicable('no claim storage; claims live in the companion ERC-735 claim holder (erc-735 option)');
  }

  async revoke(target) {
    let id;
    let keyId;
    if (typeof target === 'object' && target !== null) {
      id = target.id;
      keyId = target.key != null ? this._keyId(target.key) : undefined;
    } else {
      id = target;
      keyId = (this._keys.get(String(id).toLowerCase()) || []).pop();
    }
    if (!id || !keyId) {
      return new NotApplicable('ERC-725 has no identity-level revocation; removeKey revokes a key (none known for this id — pass { id, key })');
    }
    const c = await this._contract(id);
    const receipt = await (await c.connect(await this._ownerSigner(c)).removeKey(keyId)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'removeKey (key revoked; array compacted)' };
  }

  async transfer() {
    return new NotApplicable('identity is a contract account, not a token; ownership moves with transferOwnership (changeController); approve() is an unimplemented stub');
  }

  async signedOp(id, op = 'execute', _signature = '0x') {
    const c = await this._contract(id);
    const owner = await c.owner();
    const signer = this._signerFor(owner);
    let to = id;
    let value = 0n;
    let data = '0x';
    let opType = 0;
    let label;
    if (typeof op === 'object' && op !== null && op.op === 'execute') {
      to = op.to || id; value = BigInt(op.value || 0); data = op.data || '0x'; opType = Number(op.operationType || 0);
      label = 'execute(custom)';
    } else {
      const name = typeof op === 'string' ? op : op.op;
      const newOwner = (typeof op === 'object' && op.newOwner) || owner;
      if (name === 'changeOwner') {
        data = c.interface.encodeFunctionData('transferOwnership', [newOwner]);
        label = `execute(CALL, self, 0, transferOwnership(${newOwner.slice(0, 8)}…))`;
      } else {
        data = '0x';
        label = `execute(CALL, self, 0, 0x) for op '${name}'`;
      }
    }
    const receipt = await (await c.connect(signer).execute(opType, to, value, data)).wait();
    return {
      ok: true, receipt, gasUsed: receipt.gasUsed,
      note: `${label}; owner-gated by msg.sender, signature ignored; basic variant only emits Executed (no call performed)`,
    };
  }

  async resolve(id) {
    const c = await this._contract(id);
    const [owner, keyIds, net] = await Promise.all([c.owner(), c.getKeys(), this.ethers.provider.getNetwork()]);
    const did = `did:erc725:0x${net.chainId.toString(16)}:${id}`;
    const vm = [{ id: `${did}#owner`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${net.chainId}:${owner}`, role: 'owner (MANAGEMENT)' }];
    const keys = [];
    let i = 0;
    for (const kid of keyIds) {
      const [purpose, keyType, key] = await c.getKey(kid);
      const p = Number(purpose);
      keys.push({ keyId: key, purpose: p, purposeName: PURPOSE_NAMES[p] || String(p), keyType: Number(keyType) });
      vm.push({ id: `${did}#key-${++i}`, type: KEY_TYPES[Number(keyType)] || `keyType-${keyType}`, controller: did, keyId: key, purpose: PURPOSE_NAMES[p] || p });
    }
    const value = {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: owner,
      verificationMethod: vm,
      authentication: [`${did}#owner`],
      keys,
      meta: { contract: CONTRACT, address: id, keyCount: keyIds.length },
    };
    return { ok: true, value, note: `owner=${owner.slice(0, 8)}… keys=${keyIds.length}` };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: true,
      setAttribute: 'no attribute/data store in the basic ERC-725 proxy',
      addClaim: 'claims live in the companion ERC-735 claim holder',
      revoke: true,
      transfer: 'contract account, not a token; ownership moves via transferOwnership',
      signedOp: true,
      resolve: true,
      capabilities: true,
    };
  }
}

module.exports = Erc725Adapter;
