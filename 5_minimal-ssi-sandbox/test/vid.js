// VID layer tests — EndorsementRegistry (G1–G4), O1ControllerAdapter, TypedCredentialRegistry,
// and the off-chain credential library. Runs alongside the untouched 12-test compliance suite.
const { expect } = require("chai");
const { ethers } = require("hardhat");
const V = require("../lib/vid/credentials");

const YEAR = 365 * 24 * 3600;

describe("VID layer — endorsement, typing, off-chain credentials (on O1_ERC1056)", function () {
  let ssi, adapter, reg, typed, admin, ministryS, oemS, plantS, dmvS, vehicleS, other;
  let ministry, oem, plant, dmv, vehicle;

  const mk = async (s) => {
    const rc = await (await ssi.connect(s).createDID(s.address)).wait();
    return rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "DIDCreated").args.did;
  };

  beforeEach(async () => {
    [admin, ministryS, oemS, plantS, dmvS, vehicleS, other] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O1_ERC1056")).deploy();
    adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
    reg = await (await ethers.getContractFactory("EndorsementRegistry")).connect(admin).deploy(await ssi.getAddress(), await adapter.getAddress());
    typed = await (await ethers.getContractFactory("TypedCredentialRegistry")).deploy(await ssi.getAddress(), await reg.getAddress());
    ministry = await mk(ministryS); oem = await mk(oemS); plant = await mk(plantS); dmv = await mk(dmvS); vehicle = await mk(vehicleS);
    await reg.addRoot(ministry);
  });

  it("adapter resolves controller and activity through F2 only", async () => {
    expect(await adapter.controllerOf(dmv)).to.equal(dmvS.address);
    expect(await adapter.controllerOf(ethers.id("nope"))).to.equal(ethers.ZeroAddress);
    expect(await adapter.isActive(dmv)).to.equal(true);
    await ssi.connect(dmvS).deactivateDID(dmv);
    expect(await adapter.isActive(dmv)).to.equal(false);
  });

  it("G1 registerIssuer: only the DID's controller (or ENDORSE delegate) may register", async () => {
    await expect(reg.connect(other).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV)).to.be.revertedWithCustomError(reg, "NotAuthorized");
    await expect(reg.connect(dmvS).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV)).to.emit(reg, "IssuerRegistered");
    // delegate path via F11: dmv delegates `other` as ENDORSE_DELEGATE
    await ssi.connect(dmvS).addDelegate(dmv, ethers.id("endorse"), other.address, 3600);
    await expect(reg.connect(other).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV)).to.emit(reg, "IssuerRegistered");
  });

  it("G2/G4: root endorses issuer for a type; isEndorsed is type-specific and time-bounded", async () => {
    await reg.connect(dmvS).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV);
    await expect(reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.DRIVER_LICENCE, 100, false)).to.emit(reg, "IssuerEndorsed");
    let [ok, by] = await reg.isEndorsed(dmv, V.TYPES.DRIVER_LICENCE);
    expect(ok).to.equal(true); expect(by).to.equal(ministry);
    [ok] = await reg.isEndorsed(dmv, V.TYPES.VEHICLE_REGISTRATION);
    expect(ok).to.equal(false); // type-specific
    await ethers.provider.send("evm_increaseTime", [200]); await ethers.provider.send("evm_mine");
    [ok] = await reg.isEndorsed(dmv, V.TYPES.DRIVER_LICENCE);
    expect(ok).to.equal(false); // expired
  });

  it("G2: non-root endorser needs a transitive endorsement; chain depth is bounded", async () => {
    await reg.connect(oemS).registerIssuer(oem, V.ROLES.MANUFACTURER);
    await reg.connect(plantS).registerIssuer(plant, V.ROLES.MANUFACTURER);
    await expect(reg.connect(oemS).endorseIssuer(oem, plant, V.TYPES.VID_BIRTH, YEAR, false)).to.be.revertedWithCustomError(reg, "NotTransitiveEndorser");
    await reg.connect(ministryS).endorseIssuer(ministry, oem, V.TYPES.VID_BIRTH, YEAR, false); // non-transitive
    await expect(reg.connect(oemS).endorseIssuer(oem, plant, V.TYPES.VID_BIRTH, YEAR, false)).to.be.revertedWithCustomError(reg, "NotTransitiveEndorser");
    await reg.connect(ministryS).endorseIssuer(ministry, oem, V.TYPES.VID_BIRTH, YEAR, true); // transitive
    await expect(reg.connect(oemS).endorseIssuer(oem, plant, V.TYPES.VID_BIRTH, YEAR, false)).to.emit(reg, "IssuerEndorsed");
    const [ok, by] = await reg.isEndorsed(plant, V.TYPES.VID_BIRTH);
    expect(ok).to.equal(true); expect(by).to.equal(oem);
    await expect(reg.connect(ministryS).endorseIssuer(ministry, ethers.id("unknown"), V.TYPES.VID_BIRTH, 1, false)).to.be.revertedWithCustomError(reg, "UnknownIssuer");
    await expect(reg.connect(ministryS).endorseIssuer(ministry, ministry, V.TYPES.VID_BIRTH, 1, false)).to.be.revertedWithCustomError(reg, "SelfEndorsement");
  });

  it("G3: revoking an endorsement, or deactivating the endorser DID (F4), voids entitlement", async () => {
    await reg.connect(oemS).registerIssuer(oem, V.ROLES.MANUFACTURER);
    await reg.connect(plantS).registerIssuer(plant, V.ROLES.MANUFACTURER);
    await reg.connect(ministryS).endorseIssuer(ministry, oem, V.TYPES.VID_BIRTH, YEAR, true);
    await reg.connect(oemS).endorseIssuer(oem, plant, V.TYPES.VID_BIRTH, YEAR, false);
    expect((await reg.isEndorsed(plant, V.TYPES.VID_BIRTH))[0]).to.equal(true);
    await expect(reg.connect(other).revokeEndorsement(oem, plant, V.TYPES.VID_BIRTH)).to.be.revertedWithCustomError(reg, "NotAuthorized");
    await reg.connect(oemS).revokeEndorsement(oem, plant, V.TYPES.VID_BIRTH);
    expect((await reg.isEndorsed(plant, V.TYPES.VID_BIRTH))[0]).to.equal(false);
    // re-endorse then deactivate the OEM DID: chain breaks at the deactivated endorser
    await reg.connect(oemS).endorseIssuer(oem, plant, V.TYPES.VID_BIRTH, YEAR, false);
    expect((await reg.isEndorsed(plant, V.TYPES.VID_BIRTH))[0]).to.equal(true);
    await ssi.connect(oemS).deactivateDID(oem);
    expect((await reg.isEndorsed(plant, V.TYPES.VID_BIRTH))[0]).to.equal(false);
  });

  it("typed anchor: off-chain typing costs nothing on-chain; on-chain declare binds type; verifyTyped composes F6 ∧ G4 ∧ binding", async () => {
    await reg.connect(dmvS).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV);
    await reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.VEHICLE_REGISTRATION, YEAR, false);
    const cred = await V.signCredential(dmvS, V.vehicleRegistration({ dmvDid: dmv, vehicleDid: vehicle, plate: "T 1", jurisdiction: "CA-BC", ownerDid: vehicle, validFrom: "2026-01-01", validUntil: "2027-01-01" }));
    const rc = await (await ssi.connect(dmvS).issueCredential(dmv, vehicle, cred.anchor, 0)).wait();
    const id = rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "CredentialIssued").args.credentialId;
    let [sv, en, tb, iss] = await typed.verifyTyped(id, cred.typeId, cred.schemaHash, cred.contentHash);
    expect(sv).to.equal(true); expect(en).to.equal(true); expect(tb).to.equal(false); expect(iss).to.equal(dmv);
    await expect(typed.connect(other).declare(id, cred.typeId, cred.schemaHash, cred.contentHash)).to.be.revertedWithCustomError(typed, "NotAuthorized");
    await expect(typed.connect(dmvS).declare(id, cred.typeId, cred.schemaHash, cred.contentHash)).to.emit(typed, "CredentialDeclared");
    [sv, en, tb] = await typed.verifyTyped(id, cred.typeId, cred.schemaHash, cred.contentHash);
    expect(tb).to.equal(true);
    // wrong content → no binding
    [, , tb] = await typed.verifyTyped(id, cred.typeId, cred.schemaHash, ethers.id("tampered"));
    expect(tb).to.equal(false);
    // unknown credential → structured false, no revert
    const r = await typed.verifyTyped(ethers.id("nope"), cred.typeId, cred.schemaHash, cred.contentHash);
    expect(r[0]).to.equal(false); expect(r[3]).to.equal(ethers.ZeroHash);
    // endorsement revoked → status still valid, endorsed false
    await reg.connect(ministryS).revokeEndorsement(ministry, dmv, V.TYPES.VEHICLE_REGISTRATION);
    [sv, en] = await typed.verifyTyped(id, cred.typeId, cred.schemaHash, cred.contentHash);
    expect(sv).to.equal(true); expect(en).to.equal(false);
  });

  it("off-chain library: canonical hashing, EIP-191 issuer binding, tamper detection, staleness", async () => {
    const cred = await V.signCredential(dmvS, V.driverLicence({ dmvDid: dmv, holderDid: vehicle, licenceClass: "5", restrictions: [], jurisdiction: "CA-BC", validFrom: "2026-01-01", validUntil: "2031-01-01", birthYear: 1995, birthSalt: "s" }));
    expect(V.recoverIssuerAddress(cred)).to.equal(dmvS.address);
    const cache = new V.VerifierCache(1000);
    cache.putController(dmv, dmvS.address);
    expect(V.verifyOffline(cred, cache).ok).to.equal(true);
    const tampered = { ...cred, body: { ...cred.body, credentialSubject: { ...cred.body.credentialSubject, licenceClass: "1" } } };
    expect(V.verifyOffline(tampered, cache).integrity).to.equal(false);
    cache.putController(dmv, other.address);
    expect(V.verifyOffline(cred, cache).issuerBound).to.equal(false);
    // key-order independence of canonicalisation
    expect(V.contentHash({ b: 1, a: [2, { d: 1, c: 2 }] })).to.equal(V.contentHash({ a: [2, { c: 2, d: 1 }], b: 1 }));
    // typed hash matches the Solidity library encoding (abi.encode of three bytes32)
    const sol = await (await ethers.getContractFactory("TypedHashProbe")).deploy();
    expect(await sol.probe(cred.typeId, cred.schemaHash, cred.contentHash)).to.equal(cred.anchor);
  });
});
