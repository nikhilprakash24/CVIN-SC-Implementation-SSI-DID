const { expect } = require("chai");
const hre = require("hardhat");
const { ADAPTERS } = require("../../benchmarks/adapters");
const { makeActors } = require("../../benchmarks/lib/actors");
const { makeDataset, PAYLOADS } = require("../../benchmarks/lib/dataset");

// Gate for entering the comparative study (framework §5): every core catalogue
// op must execute on the substrate and leave the identity in the expected state.
describe("Benchmark adapter conformance", function () {
  const dataset = makeDataset(20, 42);
  const { keccak256, toUtf8Bytes, hexlify, ZeroAddress } = hre.ethers;

  /** Does the resolved document carry attribute (name, value)? Substrate-specific encoding. */
  function hasAttribute(id, doc, name, value) {
    switch (id) {
      case "erc1056": return doc.attributes[keccak256(toUtf8Bytes(name))] === hexlify(toUtf8Bytes(value));
      case "erc721": return doc.serviceRecords.includes(value);
      case "erc725": return doc.keys.some((k) => k.key === keccak256(toUtf8Bytes(`attr:${name}:${value}`)));
      default: throw new Error(`no attribute probe for ${id}`);
    }
  }
  /** Does the resolved document mention `address` (delegate / approved key)? */
  function mentions(doc, address) {
    return JSON.stringify(doc).toLowerCase().includes(address.slice(2).toLowerCase());
  }

  for (const [id, Adapter] of Object.entries(ADAPTERS)) {
    describe(id, function () {
      let adapter, actors, h, key;
      const wait = async (r) => { for (const t of r.txs) await t.wait(); return r; };

      before(async function () {
        await hre.network.provider.send("hardhat_reset");
        actors = makeActors(hre.ethers);
        adapter = new Adapter({ ethers: hre.ethers, actors, dataset, payloads: PAYLOADS });
        const deployed = await adapter.deploy();
        expect(deployed.length).to.be.greaterThan(0);
      });

      it("C1/C2 create identity", async function () {
        const r1 = await wait(await adapter.createIdentity(dataset[0], actors.vehicleOwner));
        expect(r1.txs.length).to.be.greaterThan(0);
        const r2 = await wait(await adapter.createIdentityWithAttributes(dataset[1], actors.vehicleOwner));
        h = r2.result;
        expect(await adapter.resolveOwner(h)).to.equal(actors.vehicleOwner.address);
      });

      it("R2 resolve by VIN (or declared n/a)", async function () {
        if (!adapter.supports("R2_resolve_by_vin")) return this.skip();
        const v = await adapter.resolveByVin(dataset[1].vin);
        // Q-13: equality with the identity that was created for this VIN, not just non-zero.
        const expected = id === "erc1056" ? actors.vehicleOwner.address : id === "erc721" ? h.tokenId : undefined;
        expect(expected !== undefined, `no R2 expectation for ${id}`).to.equal(true);
        expect(v).to.equal(expected);
      });

      it("U2/R4/D1 delegate lifecycle; R3 drops a revoked delegate", async function () {
        key = hre.ethers.Wallet.createRandom();
        expect(await adapter.verifyDelegate(h, key)).to.equal(false);
        await wait(await adapter.addDelegate(h, key, PAYLOADS.ttlSeconds));
        expect(await adapter.verifyDelegate(h, key)).to.equal(true);
        expect(mentions(await adapter.resolveDocument(h), key.address), "delegate in document after add").to.equal(true);
        await wait(await adapter.revokeDelegate(h, key));
        expect(await adapter.verifyDelegate(h, key)).to.equal(false);
        // H-4: the resolved document must not resurrect the revoked delegate.
        expect(mentions(await adapter.resolveDocument(h), key.address), "delegate in document after revoke").to.equal(false);
      });

      it("rotateDelegate: new key valid, old key invalid (H-2)", async function () {
        const k1 = hre.ethers.Wallet.createRandom();
        const k2 = hre.ethers.Wallet.createRandom();
        await wait(await adapter.addDelegate(h, k1, PAYLOADS.ttlSeconds));
        await wait(await adapter.rotateDelegate(h, k1, k2, PAYLOADS.ttlSeconds));
        expect(await adapter.verifyDelegate(h, k2)).to.equal(true);
        expect(await adapter.verifyDelegate(h, k1)).to.equal(false);
        const doc = await adapter.resolveDocument(h);
        expect(mentions(doc, k2.address)).to.equal(true);
        expect(mentions(doc, k1.address)).to.equal(false);
        await wait(await adapter.revokeDelegate(h, k2));
      });

      it("U3/R3 attribute appears in resolved document", async function () {
        await wait(await adapter.setAttribute(h, PAYLOADS.attributeName, PAYLOADS.attributeValue));
        const doc = await adapter.resolveDocument(h);
        expect(doc.id).to.be.a("string");
        expect(JSON.stringify(doc)).to.include("did:");
        expect(hasAttribute(id, doc, PAYLOADS.attributeName, PAYLOADS.attributeValue)).to.equal(true);
      });

      it("D2 revoke attribute (or declared n/a): attribute absent from R3", async function () {
        if (!adapter.supports("D2_revoke_attribute")) return this.skip();
        await wait(await adapter.revokeAttribute(h, PAYLOADS.attributeName));
        // Q-13 + H-4: post-state, after setAttribute then revokeAttribute.
        expect(hasAttribute(id, await adapter.resolveDocument(h), PAYLOADS.attributeName, PAYLOADS.attributeValue)).to.equal(false);
      });

      it("U5 meta-tx (or declared n/a): relayed attribute appears in R3", async function () {
        if (!adapter.supports("U5_meta_tx")) return this.skip();
        const value = "https://relayed.example.org/v1/vehicles/0000000000000000/000000";
        await wait(await adapter.metaTxSetAttribute(h, PAYLOADS.attributeName, value, actors.verifier));
        expect(hasAttribute(id, await adapter.resolveDocument(h), PAYLOADS.attributeName, value)).to.equal(true);
      });

      it("V1/V3/V6/V5 credential anchor + status", async function () {
        await wait(await adapter.anchorIssuerKey(actors.issuer, actors.delegateKey));
        const c = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("cred-" + id));
        await wait(await adapter.anchorStatus(h, c));
        expect(await adapter.statusCheck(h, c)).to.equal("active");
        await wait(await adapter.revokeCredential(h, c));
        expect(await adapter.statusCheck(h, c)).to.equal("revoked");
      });

      it("V1/V3/V5 with a separate issuer (prepareIssuer) do not touch the default issuer", async function () {
        const iss = actors.extras[0];
        await adapter.prepareIssuer(iss);
        await wait(await adapter.anchorIssuerKey(iss, actors.extras[1]));
        const c = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("cred2-" + id));
        await wait(await adapter.anchorStatus(h, c, iss));
        expect(await adapter.statusCheck(h, c, iss)).to.equal("active");
        await wait(await adapter.revokeCredential(h, c, iss));
        expect(await adapter.statusCheck(h, c, iss)).to.equal("revoked");
      });

      it("U1/U4 controller rotation and transfer", async function () {
        await wait(await adapter.rotateController(h, actors.newOwner));
        expect(await adapter.resolveOwner(h)).to.equal(actors.newOwner.address);
        await wait(await adapter.transferVehicle(h, actors.thirdOwner));
        expect(await adapter.resolveOwner(h)).to.equal(actors.thirdOwner.address);
      });

      it("D3 deactivate: identity reads as deactivated", async function () {
        await wait(await adapter.deactivate(h));
        // Q-13: post-state per substrate's deactivation semantics.
        if (id === "erc1056") {
          const doc = await adapter.resolveDocument(h);
          expect(doc.attributes[keccak256(toUtf8Bytes(PAYLOADS.deactivatedName))]).to.equal(hexlify(toUtf8Bytes("true")));
        } else if (id === "erc721") {
          expect((await adapter.resolveDocument(h)).attributes.active).to.equal(false);
        } else if (id === "erc725") {
          expect(await adapter.resolveOwner(h)).to.equal(ZeroAddress);
        } else {
          throw new Error(`no D3 post-state check for ${id}`);
        }
      });
    });
  }
});
