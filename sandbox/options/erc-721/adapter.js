'use strict';
/**
 * ERC-721 adapter — wraps 1_blockchain-identity/contracts/ERC721/CVINVehicleNFT.sol
 * (compiled artifact "CVINVehicleNFT") behind the uniform IdentityOption interface
 * (sandbox/lib/identity_option.js). Identity = one NFT; id = tokenId (decimal string).
 *
 * Method -> contract function mapping (cited by the thesis as the per-option asymmetry note):
 *
 *   deploy            new CVINVehicleNFT()                 constructor grants DEFAULT_ADMIN_ROLE +
 *                                                          MANUFACTURER_ROLE to the deployer. Setup txs
 *                                                          (grantManufacturerRole if missing, and
 *                                                          grantServiceCenterRole so setAttribute can run)
 *                                                          are NOT counted in gasUsed (reported as setupGasUsed).
 *   create            mintVehicle(to, vin, make, model, year, color, metadataURI)   [MANUFACTURER_ROLE]
 *                                                          VIN-bound: vinToTokenId / tokenIdToVIN written on-chain.
 *                                                          The contract requires a 17-char VIN (ISO 3779); shorter
 *                                                          VINs are right-padded with '0' (noted in the result).
 *   changeController  safeTransferFrom(currentOwner, newController, tokenId)   [sent by current ownerOf]
 *                                                          Ownership IS control for an NFT: there is no separate
 *                                                          controller concept, so this is identical to transfer().
 *   addKeyOrDelegate  NotApplicable                       approve()/setApprovalForAll() delegate TRANSFER rights
 *                                                          only, not a verification key or DID delegate.
 *   setAttribute      addServiceRecord(tokenId, "<key>=<value>")   [SERVICE_CENTER_ROLE]
 *                                                          Closest metadata write: append-only string list
 *                                                          (no keyed overwrite; key/value packed into one string).
 *   addClaim          NotApplicable                       no claim/credential model (roles + unsigned records only).
 *   revoke            deactivateVehicle(tokenId)          [DEFAULT_ADMIN_ROLE]  marks inactive; token NOT burned.
 *   transfer          safeTransferFrom(currentOwner, to, tokenId)   [sent by current ownerOf] (== changeController)
 *   resolve           ownerOf, tokenIdToVIN, vehicleMetadata, tokenURI, getApproved, getServiceRecords,
 *                     getTransferHistory, getOwnershipChain, isVehicleActive, getVehicleDID  (views only)
 *   signedOp          NotApplicable                       no permit / meta-transaction / signed entry point.
 *
 * Sibling contracts in the same option directory (NOT used by this adapter, see capabilities().notes):
 *   CVIN_NFT_DID_ERC721.sol            Ownable + ERC-2981 royalties; owner-only mint(to, tokenId, uri);
 *                                      toll scenario (recordEntry / getEntryTimestamp / payToll).
 *   CVIN_NFT_DID_ERC721_Monolithic.sol hand-rolled ERC-721 + ERC-2981 in one file (no OZ inheritance).
 * CVINVehicleNFT is the one with VIN linkage, roles, service records and transfer history, hence the interface.
 */
const { NotApplicable } = require('../../lib/identity_option');

const CONTRACT = 'CVINVehicleNFT';

const NA = Object.freeze({
  addKeyOrDelegate:
    'no key/delegate model on ERC-721: approve()/setApprovalForAll() delegate transfer rights only, not a verification key (manifest: Key / delegate management not-applicable)',
  addClaim:
    'no claim/credential model on ERC-721: inspector/service-center roles write unsigned records, there is no signed claim (manifest: Claims / credentials not-applicable)',
  signedOp:
    'no off-chain-authorised execution on ERC-721: no permit, meta-transaction or signed entry point (manifest: Delegated / signed execution not-applicable)',
});

class Erc721Adapter {
  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.contract = null;
    this.address = null;
  }

  // ---- helpers -------------------------------------------------------------

  _signerFor(address) {
    const want = address.toLowerCase();
    for (const s of Object.values(this.signers)) if (s && s.address.toLowerCase() === want) return s;
    throw new Error(`${CONTRACT}: no signer available for current token owner ${address}`);
  }

  _c(signer) { return signer ? this.contract.connect(signer) : this.contract; }

  static _normalizeVin(vin) {
    const v = String(vin);
    if (v.length === 17) return { vin: v, padded: false };
    if (v.length > 17) throw new Error(`${CONTRACT}: VIN longer than 17 chars (${v.length}) cannot be minted`);
    return { vin: v.padEnd(17, '0'), padded: true };
  }

  async _chainId() { return (await this.ethers.provider.getNetwork()).chainId; }

  // ---- interface -----------------------------------------------------------

  async deploy() {
    const F = await this.ethers.getContractFactory(CONTRACT, this.signers.deployer);
    this.contract = await F.deploy();
    await this.contract.waitForDeployment();
    const receipt = await this.contract.deploymentTransaction().wait();
    this.address = await this.contract.getAddress();

    // Setup (excluded from deploy gas, like the benchmark): make sure the deployer holds the
    // manufacturer role (constructor already grants it; this is the explicit grant the plan asks
    // for) and the service-center role needed for addServiceRecord (= setAttribute).
    let setupGasUsed = 0n;
    const d = this.signers.deployer;
    const MANUFACTURER_ROLE = await this.contract.MANUFACTURER_ROLE();
    if (!(await this.contract.hasRole(MANUFACTURER_ROLE, d.address))) {
      setupGasUsed += (await (await this._c(d).grantManufacturerRole(d.address)).wait()).gasUsed;
    }
    setupGasUsed += (await (await this._c(d).grantServiceCenterRole(d.address)).wait()).gasUsed;

    return { ok: true, address: this.address, receipt, gasUsed: receipt.gasUsed, setupGasUsed,
      note: 'roles: MANUFACTURER (constructor) + SERVICE_CENTER (setup tx) on deployer' };
  }

  async attach(address) {
    this.address = address;
    this.contract = await this.ethers.getContractAt(CONTRACT, address, this.signers.deployer);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner }) {
    const { vin: vin17, padded } = Erc721Adapter._normalizeVin(vin);
    const tx = await this._c(this.signers.deployer).mintVehicle(
      owner, vin17, 'CVIN', 'Sandbox', 2024, 'none', `ipfs://cvin-vehicle/${vin17}.json`,
    );
    const receipt = await tx.wait();
    const tokenId = await this.contract.vinToTokenId(vin17);
    return { ok: true, id: tokenId.toString(), receipt, gasUsed: receipt.gasUsed,
      vin: vin17, note: padded ? `VIN padded to 17 chars (${vin} -> ${vin17})` : undefined };
  }

  async changeController(id, newController) {
    const from = await this.contract.ownerOf(id);
    const tx = await this._c(this._signerFor(from))['safeTransferFrom(address,address,uint256)'](from, newController, id);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'ownership IS control for an NFT (== transfer)' };
  }

  async addKeyOrDelegate(/* id, key, purpose, validitySeconds */) {
    return new NotApplicable(NA.addKeyOrDelegate);
  }

  async setAttribute(id, key, value) {
    const record = `${key}=${value}`;
    const tx = await this._c(this.signers.deployer).addServiceRecord(id, record);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'addServiceRecord (append-only list, no keyed overwrite)' };
  }

  async addClaim(/* id, topic, data, signature */) {
    return new NotApplicable(NA.addClaim);
  }

  async revoke(id) {
    if (!/^\d+$/.test(String(id))) {
      return new NotApplicable(`revoke(claimId): ${NA.addClaim}`);
    }
    const tx = await this._c(this.signers.deployer).deactivateVehicle(id);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'deactivateVehicle: active=false, token not burned' };
  }

  async transfer(id, to) {
    const from = await this.contract.ownerOf(id);
    const tx = await this._c(this._signerFor(from))['safeTransferFrom(address,address,uint256)'](from, to, id);
    const receipt = await tx.wait();
    return { ok: true, receipt, gasUsed: receipt.gasUsed,
      note: from.toLowerCase() === to.toLowerCase() ? 'self-transfer (already owner; OZ permits, history entry appended)' : undefined };
  }

  async signedOp(/* id, op, signature */) {
    return new NotApplicable(NA.signedOp);
  }

  async resolve(id) {
    const c = this.contract;
    const chainId = await this._chainId();
    const [owner, did, vin, meta, uri, approved, records, history, chain, active] = await Promise.all([
      c.ownerOf(id), c.getVehicleDID(id), c.tokenIdToVIN(id), c.vehicleMetadata(id), c.tokenURI(id),
      c.getApproved(id), c.getServiceRecords(id), c.getTransferHistory(id), c.getOwnershipChain(id), c.isVehicleActive(id),
    ]);
    const vm = { id: `${did}#owner`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did,
      blockchainAccountId: `eip155:${chainId}:${owner}` };
    return { ok: true, note: `owner=${owner.slice(0, 8)}… vin=${vin} active=${active} records=${records.length}`, value: {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: owner,
      verificationMethod: [vm],
      authentication: [vm.id],
      service: records.map((r, i) => ({ id: `${did}#service-record-${i}`, type: 'ServiceRecord', serviceEndpoint: r })),
      vin,
      status: { active, deactivated: !active },
      metadata: { make: meta.make, model: meta.model, year: Number(meta.year), color: meta.color,
        manufacturer: meta.manufacturer, mintTimestamp: Number(meta.mintTimestamp), tokenURI: uri },
      transferApproved: approved,
      ownershipChain: [...chain],
      transferHistory: history.map((h) => ({ from: h.from, to: h.to, timestamp: Number(h.timestamp), blockNumber: Number(h.blockNumber) })),
      option: 'erc-721', contract: this.address, tokenId: String(id), chainId: Number(chainId),
    } };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: NA.addKeyOrDelegate,
      setAttribute: true,
      addClaim: NA.addClaim,
      revoke: true,
      transfer: true,
      resolve: true,
      signedOp: NA.signedOp,
      capabilities: true,
      notes: [
        'interface contract: CVINVehicleNFT.sol (AccessControl roles, VIN<->tokenId, service records, transfer history, deactivate).',
        'variant not wrapped: CVIN_NFT_DID_ERC721.sol — Ownable + ERC-2981 royalty, owner-only mint(to,tokenId,uri), toll scenario (recordEntry/getEntryTimestamp/payToll).',
        'variant not wrapped: CVIN_NFT_DID_ERC721_Monolithic.sol — single-file hand-rolled ERC-721 + ERC-2981 (no OpenZeppelin inheritance), same royalty/toll surface.',
        'changeController == transfer (safeTransferFrom): ownership is control; revoke == deactivateVehicle (no burn).',
      ],
    };
  }
}

module.exports = Erc721Adapter;
