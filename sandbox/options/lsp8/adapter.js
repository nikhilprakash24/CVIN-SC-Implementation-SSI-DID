'use strict';
/**
 * LSP8 adapter — wraps 1_blockchain-identity/contracts/LSP8/CVINVehicleLSP8.sol (artifact
 * "CVINVehicleLSP8", a representative LSP8 implementation without the LUKSO package) behind the
 * uniform IdentityOption interface. Identity = one bytes32 token; id = tokenId = keccak256(bytes(VIN)).
 *
 * Access model of the contract: contract `owner` (= deployer, the issuing authority) mints, revokes and
 * writes per-token data; the token owner (vehicle owner) transfers the token.
 *
 * Method -> contract function mapping (cited by the thesis as the per-option asymmetry note):
 *
 *   deploy            new CVINVehicleLSP8(name, symbol)    deployer becomes the issuing authority (owner).
 *   create            mintVehicle(owner, vin)              [authority]  tokenId = keccak256(vin); VIN stored under
 *                                                          DATA_KEY_VIN in the per-token LSP2-style data store.
 *   changeController  transfer(from=tokenOwnerOf, to, tokenId, force=true, "0x")   [sent by token owner]
 *                                                          ownership IS control for an LSP8 token (== transfer()).
 *                                                          force=true: no LSP1 universal-receiver probing here.
 *                                                          No-op when `to` already owns it (contract reverts on self-transfer).
 *   addKeyOrDelegate  NotApplicable                       authorizeOperator/revokeOperator are not implemented in this
 *                                                          representative LSP8; no key/delegate model.
 *   setAttribute      setDataForTokenId(tokenId, keccak256(key), bytes(value))   [authority]  ERC-725Y-style per-token key.
 *   addClaim          setDataForTokenId(tokenId, claimKey(topic), abi.encode(bytes data, bytes signature))  [authority]
 *                                                          LSP8 has no native claim model: a claim is an attestation
 *                                                          stored under a per-token data key (the contract reserves
 *                                                          DATA_KEY_INSPECTION for this purpose); the signature is stored,
 *                                                          NOT verified on-chain. claimKey = DATA_KEY_INSPECTION when the
 *                                                          topic is 'inspection', else keccak256("CVIN_CLAIM/<topic>").
 *                                                          Returns claimId = "<tokenId>:<dataKey>".
 *   revoke(id)        revokeVehicle(tokenId, "0x")         [authority or token owner]  burns the token (Transfer to 0 +
 *                                                          VehicleRevoked); data entries stay readable, tokenId ceases to exist.
 *   revoke(claimId)   setDataForTokenId(tokenId, dataKey, "0x")   [authority]  clears the attestation slot.
 *   transfer          transfer(from, to, tokenId, true, "0x")  (== changeController)
 *   resolve           exists, tokenOwnerOf, getDataForTokenId(DATA_KEY_VIN/REGISTRATION/INSPECTION/INSURANCE),
 *                     TokenIdDataChanged logs (key enumeration) + getDataForTokenId, owner (authority), name, symbol
 *   signedOp          NotApplicable                       no signed / meta-transaction entry point.
 */
const { NotApplicable } = require('../../lib/identity_option');

const CONTRACT = 'CVINVehicleLSP8';

const NA = Object.freeze({
  addKeyOrDelegate:
    'no key/delegate model: operator authorization (authorizeOperator/revokeOperator) is not implemented in this representative LSP8, and operators would delegate token moves, not verification keys (manifest: Key / delegate management not-applicable)',
  signedOp:
    'no off-chain-authorised execution on LSP8: no permit, meta-transaction or signed entry point (manifest: Delegated / signed execution not-applicable)',
});

class Lsp8Adapter {
  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.contract = null;
    this.address = null;
  }

  _signerFor(address) {
    const want = address.toLowerCase();
    for (const s of Object.values(this.signers)) if (s && s.address.toLowerCase() === want) return s;
    throw new Error(`${CONTRACT}: no signer available for current token owner ${address}`);
  }

  _authority() { return this.contract.connect(this.signers.deployer); }

  _toBytes(value) {
    const e = this.ethers;
    if (value instanceof Uint8Array) return e.hexlify(value);
    if (typeof value === 'string' && e.isHexString(value)) return value;
    return e.hexlify(e.toUtf8Bytes(String(value)));
  }

  _dataKey(key) {
    const e = this.ethers;
    return typeof key === 'string' && e.isHexString(key, 32) ? key : e.keccak256(e.toUtf8Bytes(String(key)));
  }

  async _claimKey(topic) {
    if (String(topic).toLowerCase() === 'inspection') return this.contract.DATA_KEY_INSPECTION();
    return this.ethers.keccak256(this.ethers.toUtf8Bytes(`CVIN_CLAIM/${String(topic)}`));
  }

  async deploy() {
    const F = await this.ethers.getContractFactory(CONTRACT, this.signers.deployer);
    this.contract = await F.deploy('CVIN Vehicle Identity LSP8', 'CVIN-LSP8');
    await this.contract.waitForDeployment();
    const receipt = await this.contract.deploymentTransaction().wait();
    this.address = await this.contract.getAddress();
    return { ok: true, address: this.address, receipt, gasUsed: receipt.gasUsed, note: 'deployer = issuing authority (owner)' };
  }

  async attach(address) {
    this.address = address;
    this.contract = await this.ethers.getContractAt(CONTRACT, address, this.signers.deployer);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner }) {
    const tx = await this._authority().mintVehicle(owner, vin);
    const receipt = await tx.wait();
    const id = await this.contract.tokenIdForVIN(vin); // == keccak256(bytes(vin))
    return { ok: true, id, receipt, gasUsed: receipt.gasUsed, note: 'tokenId = keccak256(vin); VIN stored under DATA_KEY_VIN' };
  }

  async _move(id, to, label) {
    const from = await this.contract.tokenOwnerOf(id);
    if (from.toLowerCase() === to.toLowerCase()) {
      return { ok: true, gasUsed: 0n, note: `no-op: ${to} already owns the token (LSP8 transfer() reverts on self-transfer)` };
    }
    const tx = await this.contract.connect(this._signerFor(from)).transfer(from, to, id, true, '0x');
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `${label}: ownership IS control (LSP8 5-arg transfer, force=true)` };
  }

  async changeController(id, newController) { return this._move(id, newController, 'changeController'); }

  async addKeyOrDelegate(/* id, key, purpose, validitySeconds */) { return new NotApplicable(NA.addKeyOrDelegate); }

  async setAttribute(id, key, value) {
    const tx = await this._authority().setDataForTokenId(id, this._dataKey(key), this._toBytes(value));
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'setDataForTokenId by the issuing authority (token owner cannot write)' };
  }

  async addClaim(id, topic, data, signature) {
    const dataKey = await this._claimKey(topic);
    const encoded = this.ethers.AbiCoder.defaultAbiCoder().encode(['bytes', 'bytes'], [this._toBytes(data || '0x'), this._toBytes(signature || '0x')]);
    const tx = await this._authority().setDataForTokenId(id, dataKey, encoded);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, claimId: `${id}:${dataKey}`,
      note: 'attestation stored as a per-token data key (no native claim model; signature stored, not verified)' };
  }

  async revoke(idOrClaimId) {
    const s = String(idOrClaimId);
    if (s.includes(':')) {
      const [tokenId, dataKey] = s.split(':');
      const tx = await this._authority().setDataForTokenId(tokenId, dataKey, '0x');
      const receipt = await tx.wait();
      return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'claim slot cleared (setDataForTokenId to empty bytes)' };
    }
    const tx = await this._authority().revokeVehicle(s, '0x');
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'revokeVehicle: token burned (Transfer to 0 + VehicleRevoked); data keys not cleared' };
  }

  async transfer(id, to) { return this._move(id, to, 'transfer'); }

  async signedOp(/* id, op, signature */) { return new NotApplicable(NA.signedOp); }

  async resolve(id) {
    const e = this.ethers;
    const c = this.contract;
    const chainId = (await e.provider.getNetwork()).chainId;
    const exists = await c.exists(id);
    const tokenOwner = exists ? await c.tokenOwnerOf(id) : null;
    const [authority, name, symbol, K_VIN, K_REG, K_INSP, K_INS] = await Promise.all([
      c.owner(), c.name(), c.symbol(), c.DATA_KEY_VIN(), c.DATA_KEY_REGISTRATION(), c.DATA_KEY_INSPECTION(), c.DATA_KEY_INSURANCE(),
    ]);
    const wellKnown = { [K_VIN]: 'CVIN_VIN', [K_REG]: 'CVIN_REGISTRATION', [K_INSP]: 'CVIN_INSPECTION', [K_INS]: 'CVIN_INSURANCE' };
    const logs = await c.queryFilter(c.filters.TokenIdDataChanged(id), 0, 'latest');
    const keys = [...new Set([K_VIN, ...logs.map((l) => l.args.dataKey)])];
    const data = await Promise.all(keys.map(async (k) => ({ dataKey: k, name: wellKnown[k] || null, value: await c.getDataForTokenId(id, k) })));
    const vinBytes = data.find((d) => d.dataKey === K_VIN).value;
    const vin = vinBytes && vinBytes !== '0x' ? e.toUtf8String(vinBytes) : '';
    const did = `did:cvin:lsp8:${chainId}:${this.address}:${id}`;
    const vm = exists ? [{ id: `${did}#owner`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${chainId}:${tokenOwner}` }] : [];
    return { ok: true, note: `exists=${exists} owner=${tokenOwner ? tokenOwner.slice(0, 8) + '…' : '-'} vin=${vin} dataKeys=${data.length}`, value: {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: tokenOwner,
      verificationMethod: vm,
      authentication: vm.map((v) => v.id),
      service: [],
      vin,
      status: { exists, revoked: !exists },
      data,
      collection: { name, symbol, issuingAuthority: authority },
      option: 'lsp8', contract: this.address, tokenId: id, chainId: Number(chainId),
      note: 'no on-chain DID helper; did string formed by the adapter. Data keys enumerated from TokenIdDataChanged logs, values re-read via getDataForTokenId.',
    } };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: NA.addKeyOrDelegate,
      setAttribute: true,
      addClaim: true,
      revoke: true,
      transfer: true,
      resolve: true,
      signedOp: NA.signedOp,
      capabilities: true,
      notes: [
        'changeController == transfer == LSP8 transfer(from,to,tokenId,force=true,data): ownership is control.',
        'setAttribute/addClaim both write per-token data keys by the issuing authority (addClaim stores an unverified attestation; DATA_KEY_INSPECTION is the contract-reserved slot).',
        'revoke(id) == revokeVehicle (burn); revoke("<tokenId>:<dataKey>") clears a claim slot.',
        'Omitted LSP8 features (LSP1 hooks, operators, ERC725Y collection store, ERC-165 id) per the contract header.',
      ],
    };
  }
}

module.exports = Lsp8Adapter;
