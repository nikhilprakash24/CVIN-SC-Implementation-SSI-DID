'use strict';
/**
 * ERC-4337 adapter — wraps 1_blockchain-identity/contracts/ERC4337/CVINVehicleAccount.sol and
 * CVINMinimalEntryPoint.sol (artifacts "CVINVehicleAccount", "CVINMinimalEntryPoint") behind the
 * uniform IdentityOption interface. Identity = one smart-contract account; id = account address.
 *
 * Creation note (counterfactual vs explicit): in canonical ERC-4337 the account address is
 * counterfactual (CREATE2 via an AccountFactory + initCode) and can receive credentials before any
 * transaction — the manifest records this as "Off-chain creation: implemented". THIS research
 * implementation has no factory and the entry point rejects initCode, so the adapter's create() is an
 * explicit direct deployment (identity creation == constructor cost, as the gas benchmark measures it);
 * it does NOT return { implicit: true }. The asymmetry is reported in capabilities().notes.
 *
 * Method -> contract function mapping (cited by the thesis as the per-option asymmetry note):
 *
 *   deploy            new CVINMinimalEntryPoint()         shared infrastructure, deployed once (registry analogue).
 *                                                          NOT the canonical v0.7 EntryPoint: single op, no bundler
 *                                                          batching / paymaster / deposits / gas accounting.
 *   create            new CVINVehicleAccount(entryPoint, owner)   one account per identity; VIN is not bound
 *                                                          on-chain (manifest: VIN linkage not-applicable); callers may
 *                                                          setAttribute('cvin/vehicle/vin', vin) afterwards.
 *   changeController  transferOwnership(newController)     [owner key, direct call]  signing-key rotation; the identity
 *                                                          (account address) is unchanged.
 *   addKeyOrDelegate  setGuardian(key)                     [owner key]  social-recovery guardian = recovery-delegate
 *                                                          analogue; `purpose`/`validitySeconds` not representable.
 *                                                          Returns keyId = "<account>:guardian".
 *   setAttribute      setAttribute(keccak256(key), bytes(value))   [owner key, direct]  ERC-725Y-flavoured store.
 *   addClaim          NotApplicable                       no on-chain claim model in ERC-4337.
 *   revoke(id)        NotApplicable                       no identity-level revocation: the account persists.
 *   revoke(keyId)     setGuardian(address(0))              [owner key]  delegate (guardian) revocation.
 *   transfer          transferOwnership(to)                (== changeController) an account is not a token; "transfer"
 *                                                          of the identity is the key rotation.
 *   resolve           owner, guardian, entryPoint, EntryPoint.nonces(account), AttributeChanged logs + getAttribute
 *   signedOp          EntryPoint.handleOp(PackedUserOperation)  -> validateUserOp (ecrecover of the EIP-191 envelope
 *                                                          over getUserOpHash) -> account callData. Sent by the deployer
 *                                                          acting as bundler; signed by the CURRENT owner key when
 *                                                          `signature` is empty, else the given 65-byte signature is used.
 *                                                          `op` forms: 'changeOwner' | 'transferOwnership' | 'setGuardian'
 *                                                          | 'setAttribute' (defaults), { fn, args } (account function),
 *                                                          { target, value, data } (execute()).
 */
const { NotApplicable } = require('../../lib/identity_option');

const ACCOUNT = 'CVINVehicleAccount';
const ENTRY_POINT = 'CVINMinimalEntryPoint';

const NA = Object.freeze({
  addClaim: 'no on-chain claim/credential model in ERC-4337: the account validates UserOperations and stores attributes, it does not hold claims (manifest: Claims / credentials not-applicable)',
  revoke: 'no identity-level revocation in ERC-4337: the account contract persists; only the recovery guardian can be cleared via setGuardian(0) (manifest: Revocation / status not-applicable)',
});

class Erc4337Adapter {
  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.entryPoint = null;
    this.address = null; // entry point address
  }

  _signerFor(address) {
    const want = address.toLowerCase();
    for (const s of Object.values(this.signers)) if (s && s.address.toLowerCase() === want) return s;
    throw new Error(`${ACCOUNT}: no signer available for current owner key ${address}`);
  }

  async _account(id, signer) {
    return this.ethers.getContractAt(ACCOUNT, id, signer || this.signers.deployer);
  }

  async _ownerSigner(id) {
    const acct = await this._account(id);
    return { acct: acct.connect(this._signerFor(await acct.owner())), owner: await acct.owner() };
  }

  _toBytes(value) {
    const e = this.ethers;
    if (value instanceof Uint8Array) return e.hexlify(value);
    if (typeof value === 'string' && e.isHexString(value)) return value;
    return e.hexlify(e.toUtf8Bytes(String(value)));
  }

  _key(key) {
    const e = this.ethers;
    return typeof key === 'string' && e.isHexString(key, 32) ? key : e.keccak256(e.toUtf8Bytes(String(key)));
  }

  async deploy() {
    const F = await this.ethers.getContractFactory(ENTRY_POINT, this.signers.deployer);
    this.entryPoint = await F.deploy();
    await this.entryPoint.waitForDeployment();
    const receipt = await this.entryPoint.deploymentTransaction().wait();
    this.address = await this.entryPoint.getAddress();
    return { ok: true, address: this.address, receipt, gasUsed: receipt.gasUsed, note: 'minimal research EntryPoint (not canonical v0.7)' };
  }

  async attach(address) {
    this.address = address;
    this.entryPoint = await this.ethers.getContractAt(ENTRY_POINT, address, this.signers.deployer);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner }) {
    const F = await this.ethers.getContractFactory(ACCOUNT, this.signers.deployer);
    const acct = await F.deploy(this.address, owner);
    await acct.waitForDeployment();
    const receipt = await acct.deploymentTransaction().wait();
    const id = await acct.getAddress();
    return { ok: true, id, receipt, gasUsed: receipt.gasUsed,
      note: `direct deployment (no factory/initCode -> not counterfactual here); VIN ${vin} not bound on-chain` };
  }

  async changeController(id, newController) {
    const { acct } = await this._ownerSigner(id);
    const receipt = await (await acct.transferOwnership(newController)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'signing-key rotation; account address unchanged' };
  }

  async addKeyOrDelegate(id, key /* , purpose, validitySeconds */) {
    const { acct } = await this._ownerSigner(id);
    const receipt = await (await acct.setGuardian(key)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, keyId: `${id}:guardian`,
      note: 'setGuardian: recovery delegate (can recoverOwner); purpose/validity not representable' };
  }

  async setAttribute(id, key, value) {
    const { acct } = await this._ownerSigner(id);
    const receipt = await (await acct.setAttribute(this._key(key), this._toBytes(value))).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'direct owner call (not via EntryPoint)' };
  }

  async addClaim(/* id, topic, data, signature */) { return new NotApplicable(NA.addClaim); }

  async revoke(idOrKeyId) {
    const s = String(idOrKeyId);
    if (s.endsWith(':guardian')) {
      const id = s.slice(0, -':guardian'.length);
      const { acct } = await this._ownerSigner(id);
      const receipt = await (await acct.setGuardian(this.ethers.ZeroAddress)).wait();
      return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'setGuardian(0): guardian (recovery delegate) revoked' };
    }
    return new NotApplicable(NA.revoke);
  }

  async transfer(id, to) {
    const { acct } = await this._ownerSigner(id);
    const receipt = await (await acct.transferOwnership(to)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'account is not a token: transfer == transferOwnership (key rotation)' };
  }

  /** Build callData for `op` against the account at `id`. */
  async _callDataFor(id, op) {
    const acct = await this._account(id);
    const iface = acct.interface;
    if (typeof op === 'string') {
      const defaults = {
        changeOwner: ['transferOwnership', [this.signers.newOwner.address]],
        transferOwnership: ['transferOwnership', [this.signers.newOwner.address]],
        setGuardian: ['setGuardian', [this.signers.delegate.address]],
        setAttribute: ['setAttribute', [this._key('did/svc/signed-probe'), '0x01']],
      };
      if (!defaults[op]) throw new Error(`${ACCOUNT}: unknown signedOp shorthand "${op}"`);
      const [fn, args] = defaults[op];
      return { callData: iface.encodeFunctionData(fn, args), desc: `${fn}(${args.join(',')})` };
    }
    if (op && op.fn) return { callData: iface.encodeFunctionData(op.fn, op.args || []), desc: `${op.fn}(...)` };
    if (op && op.target) {
      return { callData: iface.encodeFunctionData('execute', [op.target, op.value || 0, op.data || '0x']), desc: `execute(${op.target})` };
    }
    throw new Error(`${ACCOUNT}: unsupported op shape ${JSON.stringify(op)}`);
  }

  async signedOp(id, op, signature) {
    const { callData, desc } = await this._callDataFor(id, op);
    const userOp = {
      sender: id,
      nonce: await this.entryPoint.nonces(id),
      initCode: '0x',
      callData,
      accountGasLimits: this.ethers.ZeroHash, // hashed, not enforced by the minimal entry point
      preVerificationGas: 0,
      gasFees: this.ethers.ZeroHash,
      paymasterAndData: '0x',
      signature: '0x',
    };
    const userOpHash = await this.entryPoint.getUserOpHash(userOp);
    if (signature && signature !== '0x' && this.ethers.dataLength(signature) === 65) {
      userOp.signature = signature;
    } else {
      const { owner } = await this._ownerSigner(id);
      userOp.signature = await this._signerFor(owner).signMessage(this.ethers.getBytes(userOpHash)); // EIP-191 over userOpHash
    }
    const receipt = await (await this.entryPoint.connect(this.signers.deployer).handleOp(userOp)).wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, userOpHash,
      note: `handleOp -> validateUserOp(ecrecover) -> ${desc}; bundler=deployer` };
  }

  async resolve(id) {
    const e = this.ethers;
    const acct = await this._account(id);
    const chainId = (await e.provider.getNetwork()).chainId;
    const [owner, guardian, entryPoint, nonce] = await Promise.all([
      acct.owner(), acct.guardian(), acct.entryPoint(), this.entryPoint.nonces(id),
    ]);
    const logs = await acct.queryFilter(acct.filters.AttributeChanged(), 0, 'latest');
    const keys = [...new Set(logs.map((l) => l.args.key))];
    const attributes = await Promise.all(keys.map(async (k) => ({ key: k, value: await acct.getAttribute(k) })));
    const did = `did:pkh:eip155:${chainId}:${id}`;
    const vm = [{ id: `${did}#owner`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${chainId}:${owner}` }];
    if (guardian !== e.ZeroAddress) {
      vm.push({ id: `${did}#guardian`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${chainId}:${guardian}`, relationship: 'recovery' });
    }
    return { ok: true, note: `owner=${owner.slice(0, 8)}… guardian=${guardian === e.ZeroAddress ? 'none' : guardian.slice(0, 8) + '…'} attrs=${attributes.length} userOpNonce=${nonce}`, value: {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: owner,
      verificationMethod: vm,
      authentication: [vm[0].id],
      capabilityDelegation: guardian !== e.ZeroAddress ? [`${did}#guardian`] : [],
      service: [],
      attributes,
      status: { revoked: false },
      entryPoint, userOpNonce: Number(nonce),
      option: 'erc-4337', account: id, chainId: Number(chainId),
      note: 'no on-chain DID helper; did:pkh form chosen by the adapter. Attribute keys enumerated from AttributeChanged logs, values re-read via getAttribute.',
    } };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: true,
      setAttribute: true,
      addClaim: NA.addClaim,
      revoke: NA.revoke,
      transfer: true,
      resolve: true,
      signedOp: true,
      capabilities: true,
      notes: [
        'create() is an explicit direct deployment: this harness has no AccountFactory/initCode, so the counterfactual (CREATE2) creation the manifest lists is not exercised.',
        'changeController == transfer == transferOwnership (signing-key rotation; identity address stable).',
        'addKeyOrDelegate == setGuardian (recovery delegate); revoke("<account>:guardian") == setGuardian(0); revoke(id) is not applicable.',
        'signedOp == EntryPoint.handleOp with a real owner signature (EIP-191 over getUserOpHash); minimal EntryPoint, no bundler/paymaster accounting.',
      ],
    };
  }
}

module.exports = Erc4337Adapter;
