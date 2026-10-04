'use strict';
/**
 * ERC-1155 adapter — wraps 1_blockchain-identity/contracts/ERC1155/CVINVehicleCredential1155.sol
 * (artifact "CVINVehicleCredential1155") behind the uniform IdentityOption interface.
 *
 * Identity model of the contract: each token id is a CREDENTIAL TYPE (BIRTH_CERT=1, REGISTRATION=2,
 * INSPECTION_CERT=3, INSURANCE_CERT=4, MAINTENANCE_BADGE=5); "a vehicle" is the ADDRESS that holds
 * a soulbound BIRTH_CERT. Because an issuer-mediated re-binding (issuerTransferCredential of the
 * BIRTH_CERT) moves the identity to another address, the holder address is not a stable handle.
 * This adapter therefore uses the contract's own uniqueness index as the id:
 *   id = keccak256(bytes(vin))  (bytes32 hex)  ->  vinHashToVehicle(id) = current vehicle address.
 * Every method dereferences the current holder on-chain; resolve() reports it as `vehicleAddress`.
 *
 * Method -> contract function mapping (cited by the thesis as the per-option asymmetry note):
 *
 *   deploy            new CVINVehicleCredential1155()     constructor grants DEFAULT_ADMIN_ROLE + ISSUER_ROLE
 *                                                          to the deployer (no further setup needed).
 *   create            registerVehicle(vehicle=owner, vin) [ISSUER_ROLE]  mints 1 soulbound BIRTH_CERT to the
 *                                                          owner address and binds vehicleVIN / vinHashToVehicle.
 *   changeController  issuerTransferCredential(current, newController, BIRTH_CERT) [ISSUER_ROLE]
 *                                                          re-binds the VIN index to the new address; the identity
 *                                                          ADDRESS changes (holder == identity). No-op if already held
 *                                                          (a from==to call would delete the VIN mapping on-chain).
 *   addKeyOrDelegate  NotApplicable                       ERC-1155 has no key / delegate model (approvals only).
 *   setAttribute      setTokenURI(BIRTH_CERT, value)      [ISSUER_ROLE]  closest write: a COLLECTION-WIDE per-credential-
 *                                                          type metadata URI; not per-identity, `key` not representable.
 *   addClaim          issueCredential(vehicle, credentialType=topic, 1) [ISSUER_ROLE]  claim == credential token mint;
 *                                                          topic 1 (BIRTH_CERT, reserved for registerVehicle) is mapped
 *                                                          to INSPECTION_CERT. `data`/`signature` have no on-chain form.
 *                                                          Returns claimId = "<id>:<credentialType>".
 *   revoke(id)        revokeCredential(vehicle, BIRTH_CERT, 1) [ISSUER_ROLE]  burns the birth cert = deregisters the
 *                                                          identity (VIN mappings deleted on-chain).
 *   revoke(claimId)   revokeCredential(vehicle, credentialType, 1) [ISSUER_ROLE]  burns one credential unit.
 *   transfer          issuerTransferCredential(current, to, BIRTH_CERT) (== changeController). Credentials are
 *                                                          SOULBOUND: holder-initiated safeTransferFrom reverts by design.
 *   resolve           vinHashToVehicle, vehicleVIN, isRegistered, balanceOfBatch(1..5), uri(1..5)  (views only)
 *   signedOp          NotApplicable                       no signed / meta-transaction entry point.
 */
const { NotApplicable } = require('../../lib/identity_option');

const CONTRACT = 'CVINVehicleCredential1155';
const BIRTH_CERT = 1n;
const INSPECTION_CERT = 3n;
const TYPE_NAMES = { 1: 'BIRTH_CERT', 2: 'REGISTRATION', 3: 'INSPECTION_CERT', 4: 'INSURANCE_CERT', 5: 'MAINTENANCE_BADGE' };

const NA = Object.freeze({
  addKeyOrDelegate:
    'no key/delegate model on ERC-1155: setApprovalForAll() is an operator approval for token moves, not a verification key (manifest: Key / delegate management not-applicable)',
  signedOp:
    'no off-chain-authorised execution on ERC-1155: no permit, meta-transaction or signed entry point (manifest: Delegated / signed execution not-applicable)',
});

class Erc1155Adapter {
  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.contract = null;
    this.address = null;
  }

  _issuer() { return this.contract.connect(this.signers.deployer); }

  async _vehicleOf(id) {
    const v = await this.contract.vinHashToVehicle(id);
    if (v === this.ethers.ZeroAddress) throw new Error(`${CONTRACT}: no registered vehicle for VIN hash ${id} (never registered or deregistered)`);
    return v;
  }

  static _credentialType(topic) {
    let t = typeof topic === 'string' && !/^\d+$/.test(topic) ? BigInt(0) : BigInt(topic);
    if (t === BIRTH_CERT || t === 0n) t = INSPECTION_CERT; // BIRTH_CERT reserved for registerVehicle
    return t;
  }

  async deploy() {
    const F = await this.ethers.getContractFactory(CONTRACT, this.signers.deployer);
    this.contract = await F.deploy();
    await this.contract.waitForDeployment();
    const receipt = await this.contract.deploymentTransaction().wait();
    this.address = await this.contract.getAddress();
    return { ok: true, address: this.address, receipt, gasUsed: receipt.gasUsed, note: 'deployer = DEFAULT_ADMIN + ISSUER (constructor)' };
  }

  async attach(address) {
    this.address = address;
    this.contract = await this.ethers.getContractAt(CONTRACT, address, this.signers.deployer);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner }) {
    const tx = await this._issuer().registerVehicle(owner, vin);
    const receipt = await tx.wait();
    const id = this.ethers.keccak256(this.ethers.toUtf8Bytes(vin));
    return { ok: true, id, receipt, gasUsed: receipt.gasUsed, vehicleAddress: owner,
      note: 'id = keccak256(vin) (vinHashToVehicle index); identity address = holder of BIRTH_CERT' };
  }

  async _rebind(id, to, label) {
    const from = await this._vehicleOf(id);
    if (from.toLowerCase() === to.toLowerCase()) {
      return { ok: true, gasUsed: 0n, note: `no-op: ${to} already holds the BIRTH_CERT (a from==to issuerTransferCredential would delete the VIN mapping)` };
    }
    const tx = await this._issuer().issuerTransferCredential(from, to, BIRTH_CERT);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `${label}: issuer-mediated BIRTH_CERT re-binding ${from} -> ${to} (soulbound; holder cannot self-transfer)` };
  }

  async changeController(id, newController) { return this._rebind(id, newController, 'changeController'); }

  async addKeyOrDelegate(/* id, key, purpose, validitySeconds */) { return new NotApplicable(NA.addKeyOrDelegate); }

  async setAttribute(id, key, value) {
    await this._vehicleOf(id); // assert the identity exists; the write itself is collection-wide
    const tx = await this._issuer().setTokenURI(BIRTH_CERT, String(value));
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `setTokenURI(BIRTH_CERT): collection-wide credential-type URI, not per-identity; key "${key}" not representable` };
  }

  async addClaim(id, topic /* , data, signature */) {
    const vehicle = await this._vehicleOf(id);
    const credentialType = Erc1155Adapter._credentialType(topic);
    const tx = await this._issuer().issueCredential(vehicle, credentialType, 1n);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, claimId: `${id}:${credentialType}`,
      note: `issueCredential(type=${credentialType} ${TYPE_NAMES[Number(credentialType)] || 'custom'}); data/signature have no on-chain representation` };
  }

  async revoke(idOrClaimId) {
    const s = String(idOrClaimId);
    if (s.includes(':')) {
      const [id, type] = s.split(':');
      const vehicle = await this._vehicleOf(id);
      const tx = await this._issuer().revokeCredential(vehicle, BigInt(type), 1n);
      const receipt = await tx.wait();
      return { ok: true, receipt, gasUsed: receipt.gasUsed, note: `revokeCredential(type=${type}) burn` };
    }
    const vehicle = await this._vehicleOf(s);
    const tx = await this._issuer().revokeCredential(vehicle, BIRTH_CERT, 1n);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'revokeCredential(BIRTH_CERT) burn = identity deregistered (VIN mappings deleted)' };
  }

  async transfer(id, to) { return this._rebind(id, to, 'transfer'); }

  async signedOp(/* id, op, signature */) { return new NotApplicable(NA.signedOp); }

  async resolve(id) {
    const c = this.contract;
    const chainId = (await this.ethers.provider.getNetwork()).chainId;
    const vehicle = await c.vinHashToVehicle(id);
    const registered = vehicle !== this.ethers.ZeroAddress && (await c.isRegistered(vehicle));
    const types = [1n, 2n, 3n, 4n, 5n];
    const balances = registered ? await c.balanceOfBatch(types.map(() => vehicle), types) : types.map(() => 0n);
    const uris = await Promise.all(types.map((t) => c.uri(t)));
    const vin = registered ? await c.vehicleVIN(vehicle) : '';
    const did = `did:cvin:erc1155:${chainId}:${this.address}:${id}`;
    const vm = registered ? [{ id: `${did}#holder`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did,
      blockchainAccountId: `eip155:${chainId}:${vehicle}` }] : [];
    const held = types.filter((_, i) => balances[i] > 0n).map((t) => TYPE_NAMES[Number(t)]);
    return { ok: true, note: `registered=${registered} vehicle=${registered ? vehicle.slice(0, 8) + '…' : '-'} vin=${vin || '-'} credentials=[${held.join(',')}]`, value: {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: registered ? vehicle : null,
      vehicleAddress: registered ? vehicle : null,
      verificationMethod: vm,
      authentication: vm.map((v) => v.id),
      service: [],
      vin,
      status: { registered, deactivated: !registered },
      credentials: types.map((t, i) => ({ credentialType: Number(t), name: TYPE_NAMES[Number(t)], balance: Number(balances[i]), uri: uris[i] })),
      option: 'erc-1155', contract: this.address, vinHash: id, chainId: Number(chainId),
      note: 'no on-chain DID helper; did string formed by the adapter. Identity = BIRTH_CERT holder address (changes on re-binding).',
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
        'id = keccak256(vin) (contract vinHashToVehicle index) because the identity address itself changes on issuerTransferCredential.',
        'transfer == changeController == issuerTransferCredential(BIRTH_CERT): soulbound, issuer-mediated only.',
        'setAttribute == setTokenURI(BIRTH_CERT): collection-wide per-credential-type URI, not per identity.',
        'addClaim == issueCredential; revoke(id) burns BIRTH_CERT (deregisters), revoke("<id>:<type>") burns that credential.',
      ],
    };
  }
}

module.exports = Erc1155Adapter;
