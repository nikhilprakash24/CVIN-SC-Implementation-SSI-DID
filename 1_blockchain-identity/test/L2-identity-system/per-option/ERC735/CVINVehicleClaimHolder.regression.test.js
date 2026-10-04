const { expect } = require("chai");
const { ethers } = require("hardhat");

/**
 * Regression tests for docs/DEFECT_LOG.md D25 (CVINVehicleClaimHolder):
 *   D25a — no issuer whitelist: an impostor MANUFACTURER_CERT was accepted.
 *          Now: owner-managed (issuer, topic) registry; addClaim requires it,
 *          except for self-issued claims (issuer == owner).
 *   D25b — VIN_ATTESTATION (topic 1) not bound to the holder's VIN: an
 *          attestation for a different VIN was accepted.
 *          Now: the trailing bytes(vin).length bytes of `data` must hash to vinHash.
 *   D25c — signature scheme (EIP-191 here, raw digest in CVIN-Combined) is NOT
 *          changed by the fix; the "raw digest rejected" case is pinned so a
 *          later scheme decision shows up as a deliberate test change.
 */
describe("CVINVehicleClaimHolder (ERC-735) — D25 regression", function () {
    let holder, identityAddress;
    let owner, manufacturer, impostor, inspector, newOwner;

    const VIN = "1HGBH41JXMN109186";
    const OTHER_VIN = "WBA3A5C58DF586741";
    const ECDSA_SCHEME = 1;
    const VIN_ATTESTATION = 1;
    const MANUFACTURER_CERT = 2;
    const INSPECTION = 3;

    const utf8 = (s) => ethers.toUtf8Bytes(s);

    async function signClaim(issuerSigner, topic, data) {
        const digest = ethers.solidityPackedKeccak256(
            ["address", "uint256", "bytes"],
            [identityAddress, topic, data]
        );
        return issuerSigner.signMessage(ethers.getBytes(digest)); // EIP-191
    }

    async function addClaimBy(issuerSigner, topic, data, uri = "", sender = owner) {
        const sig = await signClaim(issuerSigner, topic, data);
        return holder.connect(sender).addClaim(topic, ECDSA_SCHEME, issuerSigner.address, sig, data, uri);
    }

    beforeEach(async function () {
        [owner, manufacturer, impostor, inspector, newOwner] = await ethers.getSigners();
        const F = await ethers.getContractFactory("CVINVehicleClaimHolder", owner);
        holder = await F.deploy(VIN);
        await holder.waitForDeployment();
        identityAddress = await holder.getAddress();
    });

    describe("D25a — issuer registry", function () {
        it("authorizeIssuer records the (issuer, topic) right and emits IssuerAuthorized", async function () {
            expect(await holder.isAuthorizedIssuer(manufacturer.address, MANUFACTURER_CERT)).to.be.false;
            await expect(holder.connect(owner).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT))
                .to.emit(holder, "IssuerAuthorized")
                .withArgs(manufacturer.address, MANUFACTURER_CERT);
            expect(await holder.isAuthorizedIssuer(manufacturer.address, MANUFACTURER_CERT)).to.be.true;
            // per topic: the OEM is not thereby an inspector
            expect(await holder.isAuthorizedIssuer(manufacturer.address, INSPECTION)).to.be.false;
        });

        it("an authorized issuer's claim is accepted (ClaimAdded) — gas after fix", async function () {
            await holder.connect(owner).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT);
            const cert = utf8(JSON.stringify({ vin: VIN, make: "Honda", model: "Accord", year: 2003 }));
            const tx = await addClaimBy(manufacturer, MANUFACTURER_CERT, cert, "ipfs://QmBirthCert");
            await expect(tx).to.emit(holder, "ClaimAdded");
            expect(await holder.claimExists(manufacturer.address, MANUFACTURER_CERT)).to.be.true;

            // Same call shape as the existing L2 test's "[gas] ERC-735 addClaim" line
            // (topic 1, data "VIN:<vin>", uri "ipfs://vin-attestation") for before/after.
            await holder.connect(owner).authorizeIssuer(manufacturer.address, VIN_ATTESTATION);
            const r = await (await addClaimBy(manufacturer, VIN_ATTESTATION, utf8(`VIN:${VIN}`), "ipfs://vin-attestation")).wait();
            console.log(`        [gas] ERC-735 addClaim (authorized issuer, topic 1, after D25): ${r.gasUsed.toString()}`);
        });

        it("an UNAUTHORIZED issuer's claim on the same topic reverts (the impostor MANUFACTURER_CERT)", async function () {
            await holder.connect(owner).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT);
            const fake = utf8(JSON.stringify({ vin: VIN, make: "Ferrari", model: "F8", year: 2023 }));
            // valid signature, correct topic, but the signer is not a recognised OEM
            await expect(addClaimBy(impostor, MANUFACTURER_CERT, fake))
                .to.be.revertedWith("ERC735: issuer not authorized for topic");
            expect(await holder.claimExists(impostor.address, MANUFACTURER_CERT)).to.be.false;
            expect(await holder.getClaimIdsByTopic(MANUFACTURER_CERT)).to.have.lengthOf(0);
        });

        it("authorization is per topic: an OEM authorized for MANUFACTURER_CERT cannot issue an INSPECTION", async function () {
            await holder.connect(owner).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT);
            await expect(addClaimBy(manufacturer, INSPECTION, utf8("APK:2026:PASS")))
                .to.be.revertedWith("ERC735: issuer not authorized for topic");
        });

        it("revokeIssuer makes a later claim revert; the already-anchored claim survives and the issuer may still withdraw it", async function () {
            await holder.connect(owner).authorizeIssuer(inspector.address, INSPECTION);
            await addClaimBy(inspector, INSPECTION, utf8("APK:2026-03-14:PASS"));

            await expect(holder.connect(owner).revokeIssuer(inspector.address, INSPECTION))
                .to.emit(holder, "IssuerRevoked")
                .withArgs(inspector.address, INSPECTION);
            expect(await holder.isAuthorizedIssuer(inspector.address, INSPECTION)).to.be.false;

            // forward-looking: the re-inspection (an in-place update) is refused ...
            await expect(addClaimBy(inspector, INSPECTION, utf8("APK:2027-03-10:PASS")))
                .to.be.revertedWith("ERC735: issuer not authorized for topic");
            // ... the earlier claim is untouched ...
            expect(await holder.claimExists(inspector.address, INSPECTION)).to.be.true;
            // ... and issuer-side removal is unaffected by the registry.
            const claimId = ethers.solidityPackedKeccak256(["address", "uint256"], [inspector.address, INSPECTION]);
            await expect(holder.connect(inspector).removeClaim(claimId)).to.emit(holder, "ClaimRemoved");
        });

        it("a self-issued claim (issuer == owner) needs no registry entry", async function () {
            // kept: the contract allowed owner self-issuance before the fix and ERC-735
            // allows self-claims; a verifier sees issuer == owner (self-asserted).
            await expect(addClaimBy(owner, INSPECTION, utf8("self-reported:odo=182340")))
                .to.emit(holder, "ClaimAdded");
            expect(await holder.isAuthorizedIssuer(owner.address, INSPECTION)).to.be.false;
        });

        it("authorizations survive transferOwnership; the new owner can revoke them", async function () {
            await holder.connect(owner).authorizeIssuer(inspector.address, INSPECTION);
            await holder.connect(owner).transferOwnership(newOwner.address);
            expect(await holder.isAuthorizedIssuer(inspector.address, INSPECTION)).to.be.true;
            await expect(addClaimBy(inspector, INSPECTION, utf8("APK:2026:PASS"), "", newOwner))
                .to.emit(holder, "ClaimAdded");
            // the previous owner is no longer an owner, so its self-issuance exemption is gone
            await expect(addClaimBy(owner, INSPECTION, utf8("x"), "", newOwner))
                .to.be.revertedWith("ERC735: issuer not authorized for topic");
            await holder.connect(newOwner).revokeIssuer(inspector.address, INSPECTION);
            expect(await holder.isAuthorizedIssuer(inspector.address, INSPECTION)).to.be.false;
        });

        it("registry management is onlyOwner and guards zero / duplicate / missing entries", async function () {
            await expect(holder.connect(impostor).authorizeIssuer(impostor.address, MANUFACTURER_CERT))
                .to.be.revertedWith("ERC735: caller is not the owner");
            await expect(holder.connect(manufacturer).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT))
                .to.be.revertedWith("ERC735: caller is not the owner");
            await expect(holder.connect(owner).authorizeIssuer(ethers.ZeroAddress, MANUFACTURER_CERT))
                .to.be.revertedWith("ERC735: issuer is zero address");

            await holder.connect(owner).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT);
            await expect(holder.connect(owner).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT))
                .to.be.revertedWith("ERC735: issuer already authorized");
            await expect(holder.connect(impostor).revokeIssuer(manufacturer.address, MANUFACTURER_CERT))
                .to.be.revertedWith("ERC735: caller is not the owner");
            await expect(holder.connect(owner).revokeIssuer(impostor.address, MANUFACTURER_CERT))
                .to.be.revertedWith("ERC735: issuer not authorized");
        });
    });

    describe("D25b — VIN attestation bound to the holder's VIN", function () {
        beforeEach(async function () {
            await holder.connect(owner).authorizeIssuer(manufacturer.address, VIN_ATTESTATION);
        });

        it("a topic-1 claim whose data is the holder's VIN is accepted (bare VIN and 'VIN:' prefixed)", async function () {
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, utf8(VIN)))
                .to.emit(holder, "ClaimAdded");
            // the L2 test / gas benchmark payload shape — an in-place update here
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, utf8(`VIN:${VIN}`)))
                .to.emit(holder, "ClaimChanged");
        });

        it("a topic-1 claim for ANOTHER VIN reverts, even from an authorized issuer", async function () {
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, utf8(OTHER_VIN)))
                .to.be.revertedWith("ERC735: VIN attestation does not match holder VIN");
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, utf8(`VIN:${OTHER_VIN}`)))
                .to.be.revertedWith("ERC735: VIN attestation does not match holder VIN");
            expect(await holder.getClaimIdsByTopic(VIN_ATTESTATION)).to.have.lengthOf(0);
        });

        it("a truncated VIN, a VIN with trailing bytes, or an opaque payload is rejected on topic 1", async function () {
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, utf8(VIN.slice(1))))
                .to.be.revertedWith("ERC735: VIN attestation does not match holder VIN");
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, utf8(`${VIN}X`)))
                .to.be.revertedWith("ERC735: VIN attestation does not match holder VIN");
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, "0x01"))
                .to.be.revertedWith("ERC735: VIN attestation does not match holder VIN");
        });

        it("the binding applies only to topic 1: other topics carry any payload", async function () {
            await holder.connect(owner).authorizeIssuer(manufacturer.address, MANUFACTURER_CERT);
            await expect(addClaimBy(manufacturer, MANUFACTURER_CERT, utf8(JSON.stringify({ vin: OTHER_VIN }))))
                .to.emit(holder, "ClaimAdded");
        });

        it("check order: signature, then issuer authorization, then VIN binding", async function () {
            // forged signature on a wrong-VIN payload: the signature check fires first
            const forged = await signClaim(impostor, VIN_ATTESTATION, utf8(OTHER_VIN));
            await expect(
                holder.connect(owner).addClaim(VIN_ATTESTATION, ECDSA_SCHEME, manufacturer.address, forged, utf8(OTHER_VIN), "")
            ).to.be.revertedWith("ERC735: invalid issuer signature");
            // valid signature by an unauthorized signer on a wrong-VIN payload: authorization next
            await expect(addClaimBy(impostor, VIN_ATTESTATION, utf8(OTHER_VIN)))
                .to.be.revertedWith("ERC735: issuer not authorized for topic");
            // valid signature by the authorized issuer: only the binding is left to fail
            await expect(addClaimBy(manufacturer, VIN_ATTESTATION, utf8(OTHER_VIN)))
                .to.be.revertedWith("ERC735: VIN attestation does not match holder VIN");
        });
    });

    describe("D25c — signature scheme (unchanged by the fix; pinned)", function () {
        it("still accepts EIP-191 and still rejects a raw-digest (CVIN-Combined style) signature", async function () {
            await holder.connect(owner).authorizeIssuer(manufacturer.address, VIN_ATTESTATION);
            const data = utf8(VIN);
            const digest = ethers.solidityPackedKeccak256(["address", "uint256", "bytes"], [identityAddress, VIN_ATTESTATION, data]);
            // hardhat signers expose no signingKey; use a deterministic wallet, authorized like any issuer
            const rawWallet = new ethers.Wallet("0x" + "11".repeat(32));
            await holder.connect(owner).authorizeIssuer(rawWallet.address, VIN_ATTESTATION);
            const rawSig = ethers.Signature.from(rawWallet.signingKey.sign(digest)).serialized; // no EIP-191 prefix
            await expect(
                holder.connect(owner).addClaim(VIN_ATTESTATION, ECDSA_SCHEME, rawWallet.address, rawSig, data, "")
            ).to.be.revertedWith("ERC735: invalid issuer signature");
            const eip191 = await rawWallet.signMessage(ethers.getBytes(digest));
            await expect(
                holder.connect(owner).addClaim(VIN_ATTESTATION, ECDSA_SCHEME, rawWallet.address, eip191, data, "")
            ).to.emit(holder, "ClaimAdded");
        });
    });
});
