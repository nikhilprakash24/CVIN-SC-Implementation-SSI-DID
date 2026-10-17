// Scenario S7 — Minimal VID layer with endorsement.
//
// Actors (DIDs): Ministry (root of trust) · OEM root · OEM plant (issuer, endorsed by OEM root)
//                · DMV (issuer, endorsed by Ministry) · Vehicle · Driver · Verifier (charging operator)
// Objects: VID birth certificate (MOBI VID I), vehicle registration ("car id"), driver's licence,
//          endorsements, presentations, verifier cache.
// Tiers: issuance and endorsement at Tier 3 (synchronous writes); verification at Tier 2 via the
//        off-chain path (signature + cache) with a chain status read; presentation bound by challenge.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_vid_minimal.js
// Every measurement below is emitted to traces/vid_minimal_<IMPL>_<ts>.jsonl.
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");

const IMPL = process.env.IMPL || "O1_ERC1056";
const B32 = (s) => ethers.id(s);
const YEAR = 365 * 24 * 3600;

async function main() {
  const T = makeTrace(IMPL);
  const [ministryS, oemRootS, plantS, dmvS, vehicleS, driverS, verifierS] = await ethers.getSigners();

  // ---- deploy: SSI option + adapter + governance + typed registry ----
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const reg = await (await ethers.getContractFactory("EndorsementRegistry")).deploy(await ssi.getAddress(), await adapter.getAddress());
  const typed = await (await ethers.getContractFactory("TypedCredentialRegistry")).deploy(await ssi.getAddress(), await reg.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL}=${await ssi.getAddress()} adapter=${await adapter.getAddress()} endorsements=${await reg.getAddress()} typed=${await typed.getAddress()}` });

  // ---- F1: identities ----
  const mk = async (signer, label) => {
    const rc = await T.tx("createDID", "F1", label, ssi.connect(signer).createDID(signer.address));
    return T.parseEvent(ssi, rc, "DIDCreated").did;
  };
  const ministry = await mk(ministryS, "Ministry");
  const oemRoot = await mk(oemRootS, "OEMRoot");
  const plant = await mk(plantS, "OEMPlant");
  const dmv = await mk(dmvS, "DMV");
  const vehicle = await mk(vehicleS, "Vehicle");
  const driver = await mk(driverS, "Driver");
  const verifier = await mk(verifierS, "ChargingOperator");

  // ---- governance bootstrap: roots (admin = deployer = ministry signer) ----
  await T.tx("addRoot", "G0", "RegistryAdmin", reg.addRoot(ministry), { note: "Ministry = root of trust" });
  await T.tx("addRoot", "G0", "RegistryAdmin", reg.addRoot(oemRoot), { note: "OEM root = root of trust" });

  // ---- G1: issuers register their roles (permissionless self-declaration) ----
  await T.tx("registerIssuer", "G1", "OEMPlant", reg.connect(plantS).registerIssuer(plant, V.ROLES.MANUFACTURER));
  await T.tx("registerIssuer", "G1", "DMV", reg.connect(dmvS).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV));

  // ---- G2: endorsement = entitlement to issue a credential TYPE ----
  await T.tx("endorseIssuer", "G2", "OEMRoot", reg.connect(oemRootS).endorseIssuer(oemRoot, plant, V.TYPES.VID_BIRTH, YEAR, false), { note: "OEM root → plant : VID_BIRTH" });
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.VEHICLE_REGISTRATION, YEAR, false), { note: "Ministry → DMV : VEHICLE_REGISTRATION" });
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.DRIVER_LICENCE, YEAR, false), { note: "Ministry → DMV : DRIVER_LICENCE" });
  // Negative: an unendorsed issuer (DMV) cannot endorse anyone — it is not a root nor transitive.
  try { await reg.connect(dmvS).endorseIssuer(dmv, plant, V.TYPES.DRIVER_LICENCE, YEAR, false); throw new Error("should revert"); }
  catch (e) { T.off("negative", "DMV", `DMV cannot endorse (NotTransitiveEndorser) → ${/NotTransitiveEndorser/.test(e.message) ? "reverted as expected" : e.message}`); }

  // ---- G4: entitlement reads (views; gas-free) ----
  for (const [who, did, t] of [["OEMPlant", plant, "VID_BIRTH"], ["DMV", dmv, "VEHICLE_REGISTRATION"], ["DMV", dmv, "DRIVER_LICENCE"], ["OEMPlant", plant, "DRIVER_LICENCE"]]) {
    const [ok, by] = await reg.isEndorsed(did, V.TYPES[t]);
    T.view("isEndorsed", "G4", "Verifier", `${who} for ${t}: ${ok}${ok ? " by " + (by === ministry ? "Ministry" : "OEMRoot") : ""}`);
  }

  // ---- Off-chain: build the three minimal credentials ----
  const vin = "1HGBH41JXMN109186", vinSalt = crypto.randomBytes(16).toString("hex");
  const birth = await V.signCredential(plantS, V.vidBirth({ oemDid: plant, vehicleDid: vehicle, vin, vinSalt, make: "Honda", model: "Civic", modelYear: 2026, productionDate: "2026-08-14", plantCode: "ALLISTON-01" }));
  const regn = await V.signCredential(dmvS, V.vehicleRegistration({ dmvDid: dmv, vehicleDid: vehicle, plate: "CVN 001", jurisdiction: "CA-BC", ownerDid: driver, validFrom: "2026-09-01", validUntil: "2027-09-01" }));
  const now = Math.floor(Date.now() / 1000);
  const lic = await V.signCredential(dmvS, V.driverLicence({ dmvDid: dmv, holderDid: driver, licenceClass: "5", restrictions: [], jurisdiction: "CA-BC", validFrom: "2026-09-01", validUntil: "2031-09-01", birthYear: 1995, birthSalt: crypto.randomBytes(8).toString("hex") }));
  T.off("build-credentials", "Issuers", `3 credentials built + EIP-191 signed off-chain; canonical bytes: birth=${V.canonicalize(birth.body).length}B reg=${V.canonicalize(regn.body).length}B lic=${V.canonicalize(lic.body).length}B; on-chain will see 32B anchors only`);

  // ---- F5: anchor (typed hash only) ----
  const anchor = async (signer, label, issuerDid, subjectDid, cred, validUntil, note) => {
    const rc = await T.tx("issueCredential", "F5", label, ssi.connect(signer).issueCredential(issuerDid, subjectDid, cred.anchor, validUntil), { note });
    return T.parseEvent(ssi, rc, "CredentialIssued").credentialId;
  };
  const birthId = await anchor(plantS, "OEMPlant", plant, vehicle, birth, 0, "VID_BIRTH anchor (immutable, no expiry)");
  const regId = await anchor(dmvS, "DMV", dmv, vehicle, regn, now + YEAR, "VEHICLE_REGISTRATION anchor (1y)");
  const licId = await anchor(dmvS, "DMV", dmv, driver, lic, now + 5 * YEAR, "DRIVER_LICENCE anchor (5y)");

  // ---- T1: optional on-chain typing for ONE credential (to measure the extra write) ----
  await T.tx("declare", "T1", "DMV", typed.connect(dmvS).declare(regId, regn.typeId, regn.schemaHash, regn.contentHash), { note: "on-chain typing path (queryable type) — cost of queryability" });

  // ---- holder wallets (off-chain) ----
  const vehicleWallet = new V.Wallet(vehicle); vehicleWallet.store(birthId, birth); vehicleWallet.store(regId, regn);
  const driverWallet = new V.Wallet(driver); driverWallet.store(licId, lic);
  T.off("wallets", "Holders", "vehicle wallet: VID_BIRTH + VEHICLE_REGISTRATION; driver wallet: DRIVER_LICENCE (content never on-chain)");

  // ---- Verifier warms its cache with reads (F2 via adapter, G4) — Tier 3 prefetch ----
  const cache = new V.VerifierCache(60_000);
  for (const [label, did] of [["OEMPlant", plant], ["DMV", dmv]]) {
    const addr = await adapter.controllerOf(did);
    cache.putController(did, addr);
    T.view("resolveDID→controllerOf", "F2", "ChargingOperator", `cache ${label} controller ${addr.slice(0, 10)}…`);
  }
  for (const [did, t] of [[plant, "VID_BIRTH"], [dmv, "VEHICLE_REGISTRATION"], [dmv, "DRIVER_LICENCE"]]) {
    const [ok] = await reg.isEndorsed(did, V.TYPES[t]); cache.putEndorsed(did, V.TYPES[t], { ok });
    T.view("isEndorsed", "G4", "ChargingOperator", `cache ${t}: ${ok}`);
  }

  // ---- Tier 2 verification: OFF-CHAIN first (no chain access), then a chain status read ----
  for (const [label, cred] of [["VID_BIRTH", birth], ["VEHICLE_REGISTRATION", regn], ["DRIVER_LICENCE", lic]]) {
    const r = V.verifyOffline(cred, cache);
    T.off("verify-offline", "ChargingOperator", `${label}: integrity=${r.integrity} issuerSig→controller=${r.issuerBound} cacheFresh=${r.cacheFresh} expired=${r.expired} ⇒ ok=${r.ok} (zero chain reads)`);
  }
  for (const [label, id] of [["VID_BIRTH", birthId], ["VEHICLE_REGISTRATION", regId], ["DRIVER_LICENCE", licId]]) {
    const [valid, , revoked, expired] = await ssi.verifyCredential(id);
    cache.putStatus(id, { valid, revoked, expired });
    T.view("verifyCredential", "F6", "ChargingOperator", `${label}: valid=${valid} revoked=${revoked} expired=${expired} (status read; content never read)`);
  }
  // ---- T2: composite typed verification (status ∧ endorsement ∧ optional on-chain type binding) ----
  for (const [label, id, cred] of [["VEHICLE_REGISTRATION (declared)", regId, regn], ["DRIVER_LICENCE (undeclared)", licId, lic]]) {
    const [sv, en, tb, iss] = await typed.verifyTyped(id, cred.typeId, cred.schemaHash, cred.contentHash);
    T.view("verifyTyped", "T2", "ChargingOperator", `${label}: status=${sv} endorsed=${en} typeBoundOnChain=${tb} issuer=${iss === dmv ? "DMV" : iss.slice(0, 10)}`);
  }

  // ---- Delegation: vehicle OBU key as sigAuth delegate (F11/F12) ----
  const obu = ethers.Wallet.createRandom().connect(ethers.provider);
  await T.tx("addDelegate", "F11", "Vehicle", ssi.connect(vehicleS).addDelegate(vehicle, B32("sigAuth"), obu.address, 3600), { note: "OBU key, 1h" });
  T.view("validDelegate", "F12", "ChargingOperator", `OBU is sigAuth delegate of Vehicle: ${await ssi.validDelegate(vehicle, B32("sigAuth"), obu.address)}`);

  // ---- F8: challenge-bound presentation of registration + licence to the charging operator ----
  const nonce = crypto.randomBytes(8).toString("hex");
  const ch = V.presentationChallenge({ verifierDid: verifier, holderDid: vehicle, credentialIds: [regId], purpose: "ev-charging-session", nonce, domain: "cvin-sandbox" });
  await T.tx("createPresentation", "F8", "Vehicle", ssi.connect(vehicleS).createPresentation(vehicle, [regId], ch, "cvin-sandbox"), { note: "VP(registration) bound to operator challenge" });
  const ch2 = V.presentationChallenge({ verifierDid: verifier, holderDid: driver, credentialIds: [licId], purpose: "ev-charging-session", nonce, domain: "cvin-sandbox" });
  await T.tx("createPresentation", "F8", "Driver", ssi.connect(driverS).createPresentation(driver, [licId], ch2, "cvin-sandbox"), { note: "VP(licence) bound to same session nonce" });
  // Selective disclosure sample: driver discloses licenceClass only (digests for the rest)
  const salts = Object.fromEntries(Object.keys(lic.body.credentialSubject).map(k => [k, crypto.randomBytes(8).toString("hex")]));
  const dig = V.disclosureDigests(lic.body.credentialSubject, salts);
  T.off("selective-disclosure", "Driver", `discloses licenceClass=${lic.body.credentialSubject.licenceClass} + ${Object.keys(dig).length - 1} salted digests (SD-JWT-style; BBS+/ZK path in doc 02)`);
  // Replay of the same challenge must fail on-chain
  try { await ssi.connect(vehicleS).createPresentation(vehicle, [regId], ch, "cvin-sandbox"); throw new Error("should revert"); }
  catch (e) { T.off("negative", "Vehicle", `replayed challenge → ${/InvalidCredential|revert/.test(e.message) ? "reverted (replay prevented)" : e.message}`); }

  // ---- Key rotation on the DMV (F9/F10) does not disturb issued anchors ----
  const rcK = await T.tx("addVerificationMethod", "F9", "DMV", ssi.connect(dmvS).addVerificationMethod(dmv, B32("EcdsaSecp256k1VerificationKey2019"), "0x04beef"));
  const keyId = T.parseEvent(ssi, rcK, "VerificationMethodAdded").keyId;
  await T.tx("removeVerificationMethod", "F10", "DMV", ssi.connect(dmvS).removeVerificationMethod(dmv, keyId));
  await T.tx("updateDID", "F3", "DMV", ssi.connect(dmvS).updateDID(dmv, B32("service"), ethers.toUtf8Bytes("https://dmv.example/status"), 86400), { note: "service endpoint attribute (event-sourced)" });

  // ---- Trust break 1: registration revoked (F7) → cache invalidation → offline verify still 'ok' until refreshed ----
  await T.tx("revokeCredential", "F7", "DMV", ssi.connect(dmvS).revokeCredential(regId), { note: "registration revoked (e.g. plate cancelled)" });
  const stale = V.verifyOffline(regn, cache);
  T.off("verify-offline", "ChargingOperator", `VEHICLE_REGISTRATION after revocation, cache NOT refreshed: ok=${stale.ok} — the staleness window is the security parameter (doc 06 §5)`);
  const [v2, , r2] = await ssi.verifyCredential(regId); cache.putStatus(regId, { valid: v2, revoked: r2 });
  T.view("verifyCredential", "F6", "ChargingOperator", `VEHICLE_REGISTRATION after cache refresh: valid=${v2} revoked=${r2} ⇒ session refused`);

  // ---- Trust break 2: Ministry revokes DMV's licence endorsement (G3) → existing licence status stays valid, entitlement fails ----
  await T.tx("revokeEndorsement", "G3", "Ministry", reg.connect(ministryS).revokeEndorsement(ministry, dmv, V.TYPES.DRIVER_LICENCE));
  const [sv3, en3] = await typed.verifyTyped(licId, lic.typeId, lic.schemaHash, lic.contentHash);
  T.view("verifyTyped", "T2", "ChargingOperator", `DRIVER_LICENCE after endorsement revoked: status=${sv3} endorsed=${en3} ⇒ policy decides (F6 alone would accept; endorsement gating rejects)`);

  // ---- F4: plant deactivated → its VID_BIRTH anchors report issuer-deactivated ----
  await T.tx("deactivateDID", "F4", "OEMPlant", ssi.connect(plantS).deactivateDID(plant), { note: "plant closed" });
  const [v4] = await ssi.verifyCredential(birthId);
  const [en4] = await reg.isEndorsed(plant, V.TYPES.VID_BIRTH);
  T.view("verifyCredential+isEndorsed", "F6", "ChargingOperator", `VID_BIRTH after plant deactivation: valid=${v4} endorsed=${en4} — FINDING: F6 ties credential validity to issuer liveness; birth certificates need an archival-issuer policy (doc 01 §9, doc 07 §4)`);

  T.write("vid_minimal");
}

main().catch((e) => { console.error(e); process.exit(1); });
