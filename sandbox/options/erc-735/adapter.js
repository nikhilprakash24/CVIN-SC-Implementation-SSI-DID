'use strict';
/**
 * ERC-735 claim-holder adapter (slug: erc-735).
 *
 * Contract: 1_blockchain-identity/contracts/ERC735/CVINVehicleClaimHolder.sol. There is NO
 * shared registry: one claim-holder contract = one vehicle identity, so deploying it IS
 * identity creation and its deployment gas IS the creation cost (constructor stores vin +
 * vinHash, msg.sender becomes owner = the ERC-734 MANAGEMENT-key role). Identity id = the
 * claim holder's contract address.
 *
 * Claim signature scheme (test/ERC735/CVINVehicleClaimHolder.test.js): the issuer signs
 * keccak256(abi.encodePacked(identityAddress, topic, data)) WITH the EIP-191
 * "\x19Ethereum Signed Message:\n32" prefix (ethers signMessage), and addClaim verifies it
 * on-chain with ecrecover. claimId = keccak256(abi.encodePacked(issuer, topic)).
 *
 * Method -> contract function mapping (the thesis cites this table):
 *   deploy            nothing to deploy (no registry) -> { ok, address: null, gasUsed: 0n }
 *   create            new CVINVehicleClaimHolder(vin) sent by `owner`'s signer. If `owner` is not a
 *                     local signer the deployer deploys and then transferOwnership(owner); gasUsed is
 *                     the sum.
 *   changeController  transferOwnership(newOwner) sent by owner()
 *   addKeyOrDelegate  NotApplicable: no key/delegate model (the draft defers keys to ERC-734; here a
 *                     single owner plays the MANAGEMENT key)
 *   setAttribute      NotApplicable: no attribute store (the closest analogue is a claim)
 *   addClaim          addClaim(topic, scheme=1 ECDSA, issuer, signature, data, uri) sent by owner().
 *                     With an empty signature the adapter signs as issuer with `deployer`
 *                     (signMessage, EIP-191). With a signature, the issuer is opts.issuer or is
 *                     recovered with ethers.verifyMessage. Returns claimId. Re-adding (issuer, topic)
 *                     updates in place (ClaimChanged).
 *   revoke            removeClaim(claimId) sent by owner() (the issuer may also call it). A bytes32
 *                     argument is a claimId; { id, claimId } / { id, issuer, topic } are explicit; a
 *                     bare identity id removes the most recent claim this adapter added for it.
 *                     Identity-level revocation does not exist (manifest: not-applicable) ->
 *                     NotApplicable when no claim is known.
 *   transfer          NotApplicable: the identity is a contract, not a token; ownership moves with
 *                     transferOwnership (= changeController)
 *   signedOp          NotApplicable: no meta-transaction / execute surface in ERC-735
 *   resolve           on-chain reads only: vin(), vinHash(), owner(), getClaimIdsByTopic(t) for the
 *                     four vehicle topics (VIN_ATTESTATION, MANUFACTURER_CERT, INSPECTION, INSURANCE)
 *                     plus any topic used through this adapter, getClaim(claimId) for each.
 *   capabilities      mirrors manifest.yaml
 */
const { NotApplicable } = require('../../lib/identity_option');

const CONTRACT = 'CVINVehicleClaimHolder';
const ECDSA_SCHEME = 1;
const TOPICS = { 1: 'VIN_ATTESTATION', 2: 'MANUFACTURER_CERT', 3: 'INSPECTION', 4: 'INSURANCE' };

class Erc735Adapter {
  static get slug() { return 'erc-735'; }

  constructor({ ethers, signers }) {
    this.ethers = ethers;
    this.signers = signers;
    this.identities = new Map();  // id -> Contract handle
    this._claims = new Map();     // id -> [claimId] added through this adapter
    this._topics = new Set([1, 2, 3, 4]);
  }

  // ---------- helpers ----------
  _bytes(v) {
    if (v == null) return '0x';
    if (v instanceof Uint8Array) return this.ethers.hexlify(v);
    return this.ethers.isHexString(v) ? v : this.ethers.hexlify(this.ethers.toUtf8Bytes(String(v)));
  }
  _allSigners() { return Object.values(this.signers).flat().filter(Boolean); }
  _signerFor(addr, required = true) {
    const a = String(addr).toLowerCase();
    const s = this._allSigners().find((x) => x.address.toLowerCase() === a);
    if (!s && required) throw new Error(`erc-735: no local signer for ${addr}`);
    return s || null;
  }
  async _contract(id) {
    const k = String(id).toLowerCase();
    if (!this.identities.has(k)) this.identities.set(k, await this.ethers.getContractAt(CONTRACT, id, this.signers.deployer));
    return this.identities.get(k);
  }
  async _ownerSigner(c) { return this._signerFor(await c.owner()); }
  _claimDigest(id, topic, data) {
    return this.ethers.solidityPackedKeccak256(['address', 'uint256', 'bytes'], [id, topic, data]);
  }
  _claimId(issuer, topic) {
    return this.ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer, topic]);
  }

  // ---------- interface ----------
  async deploy() {
    return { ok: true, address: null, gasUsed: 0n, note: 'no shared registry; each identity is its own claim holder, deployed by create()' };
  }

  async attach(address) {
    await this._contract(address);
    return { ok: true, address, gasUsed: 0n };
  }

  async create({ vin, owner } = {}) {
    const target = owner || this.signers.vehicleOwner.address;
    const v = vin || `VIN-${Date.now()}`;
    const ownerSigner = this._signerFor(target, false);
    const F = await this.ethers.getContractFactory(CONTRACT, ownerSigner || this.signers.deployer);
    const c = await F.deploy(v);
    const r1 = await c.deploymentTransaction().wait();
    const id = await c.getAddress();
    this.identities.set(id.toLowerCase(), c);
    let gasUsed = r1.gasUsed;
    let note = `claim-holder deployment is the creation cost (vin=${v} stored in constructor)`;
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

  async addKeyOrDelegate() {
    return new NotApplicable('no key/delegate model in ERC-735 (keys are deferred to ERC-734; a single owner plays the MANAGEMENT key)');
  }

  async setAttribute() {
    return new NotApplicable('no attribute store in ERC-735; the closest analogue is a claim (addClaim)');
  }

  async addClaim(id, topic = 1, data = '0x', signature = '0x', opts = {}) {
    const E = this.ethers;
    const c = await this._contract(id);
    const t = Number(topic);
    const bytes = this._bytes(data);
    const digest = this._claimDigest(id, t, bytes);
    let sig = signature;
    let issuer = opts.issuer;
    let how;
    if (!sig || sig === '0x') {
      const issuerSigner = opts.issuerSigner || this.signers.deployer;
      sig = await issuerSigner.signMessage(E.getBytes(digest)); // EIP-191 prefixed, as the contract expects
      issuer = issuerSigner.address;
      how = `issuer=${issuer.slice(0, 8)}… (adapter-signed, EIP-191)`;
    } else {
      if (!issuer) issuer = E.verifyMessage(E.getBytes(digest), sig);
      how = `issuer=${issuer.slice(0, 8)}… (caller-supplied signature)`;
    }
    const receipt = await (await c.connect(await this._ownerSigner(c)).addClaim(t, ECDSA_SCHEME, issuer, sig, bytes, opts.uri || '')).wait();
    const claimId = this._claimId(issuer, t);
    const k = String(id).toLowerCase();
    if (!this._claims.has(k)) this._claims.set(k, []);
    this._claims.get(k).push(claimId);
    this._topics.add(t);
    return { ok: true, receipt, gasUsed: receipt.gasUsed, value: claimId, claimId, note: `addClaim topic=${t} ${TOPICS[t] || ''} ${how}` };
  }

  async revoke(target) {
    let id;
    let claimId;
    if (typeof target === 'object' && target !== null) {
      id = target.id;
      claimId = target.claimId || (target.issuer && target.topic != null ? this._claimId(target.issuer, Number(target.topic)) : undefined);
    } else if (this.ethers.isHexString(target, 32)) {
      claimId = target;
      for (const [k, list] of this._claims) if (list.includes(claimId)) { id = k; break; }
    } else {
      id = target;
      claimId = (this._claims.get(String(id).toLowerCase()) || []).pop();
    }
    if (!id || !claimId) {
      return new NotApplicable('ERC-735 has no identity-level revocation; removeClaim(claimId) revokes a claim (none known for this id — pass { id, claimId })');
    }
    const c = await this._contract(id);
    const receipt = await (await c.connect(await this._ownerSigner(c)).removeClaim(claimId)).wait();
    const list = this._claims.get(String(id).toLowerCase());
    if (list) { const i = list.indexOf(claimId); if (i >= 0) list.splice(i, 1); }
    return { ok: true, receipt, gasUsed: receipt.gasUsed, note: 'removeClaim (claim deleted; topic index compacted)' };
  }

  async transfer() {
    return new NotApplicable('identity is a contract, not a token; ownership moves with transferOwnership (changeController)');
  }

  async signedOp() {
    return new NotApplicable('no meta-transaction or execute surface in ERC-735; all mutations are owner msg.sender-gated');
  }

  async resolve(id) {
    const E = this.ethers;
    const c = await this._contract(id);
    const [vin, vinHash, owner, net] = await Promise.all([c.vin(), c.vinHash(), c.owner(), E.provider.getNetwork()]);
    const claims = [];
    for (const t of [...this._topics].sort((a, b) => a - b)) {
      const ids = await c.getClaimIdsByTopic(t);
      for (const cid of ids) {
        const [topic, scheme, issuer, signature, data, uri] = await c.getClaim(cid);
        let dataText = data;
        try { dataText = E.toUtf8String(data); } catch (_) { /* keep hex */ }
        claims.push({ claimId: cid, topic: Number(topic), topicName: TOPICS[Number(topic)] || String(topic), scheme: Number(scheme), issuer, signature, data, dataText, uri });
      }
    }
    const did = `did:erc735:0x${net.chainId.toString(16)}:${id}`;
    const value = {
      '@context': ['https://www.w3.org/ns/did/v1'],
      id: did,
      controller: owner,
      verificationMethod: [{ id: `${did}#owner`, type: 'EcdsaSecp256k1RecoveryMethod2020', controller: did, blockchainAccountId: `eip155:${net.chainId}:${owner}` }],
      authentication: [`${did}#owner`],
      vehicle: { vin, vinHash },
      claims,
      meta: { contract: CONTRACT, address: id, claimCount: claims.length },
    };
    return { ok: true, value, note: `owner=${owner.slice(0, 8)}… vin=${vin} claims=${claims.length}` };
  }

  capabilities() {
    return {
      deploy: true,
      create: true,
      changeController: true,
      addKeyOrDelegate: 'no key/delegate model (deferred to ERC-734; single owner)',
      setAttribute: 'no attribute store; claims are the data model',
      addClaim: true,
      revoke: true,
      transfer: 'contract, not a token; ownership moves via transferOwnership',
      signedOp: 'no meta-transaction / execute surface',
      resolve: true,
      capabilities: true,
    };
  }
}

module.exports = Erc735Adapter;
