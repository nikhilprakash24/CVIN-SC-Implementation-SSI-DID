// Scenario S3 — Medium-tier commercial: EV-charging session.
//
// verinym handshake (cached reads) → tariff credential presented by the OPERATOR to the vehicle
// (mutual: the vehicle checks the operator too) → challenge-bound presentations both ways →
// off-chain session (metering messages, AEAD) → payment-anchored receipt: the operator issues a
// "paid session" credential to the vehicle whose hash commits to the metering log and the
// payment reference; nothing about price, energy or location is on-chain.
// Tier 2 on the critical path = reads from cache + off-chain crypto only; the two F8 commits and
// the receipt anchor (F5) are asynchronous (doc 05 §3; doc 06 §3).
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_s3_evcharging.js
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");

const IMPL = process.env.IMPL || "O1_ERC1056";
const B32 = (s) => ethers.id(s);
const YEAR = 365 * 24 * 3600;

async function main() {
  const T = makeTrace(IMPL);
  const [adminS, ministryS, dmvS, utilS, vehicleS, opS] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const reg = await (await ethers.getContractFactory("EndorsementRegistry")).connect(adminS).deploy(await ssi.getAddress(), await adapter.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL} + adapter + EndorsementRegistry` });
  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;

  // Tier 3 setup: roots, endorsements, registration (vehicle) and tariff licence (operator)
  const ministry = await mk(ministryS, "Ministry"), dmv = await mk(dmvS, "DMV"), utility = await mk(utilS, "UtilityRegulator");
  const vehicle = await mk(vehicleS, "Vehicle"), op = await mk(opS, "ChargingOperator");
  await T.tx("addRoot", "G0", "Admin", reg.addRoot(ministry));
  const TARIFF = ethers.id("cvin.charging.tariff-licence.v1");
  for (const [s, did, role] of [[dmvS, dmv, V.ROLES.GOVERNMENT_DMV], [utilS, utility, ethers.id("role.utility-regulator")], [opS, op, ethers.id("role.charging-operator")]])
    await T.tx("registerIssuer", "G1", "issuer", reg.connect(s).registerIssuer(did, role));
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.VEHICLE_REGISTRATION, YEAR, false));
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, utility, TARIFF, YEAR, true), { note: "regulator may license operators (transitive)" });
  await T.tx("endorseIssuer", "G2", "UtilityRegulator", reg.connect(utilS).endorseIssuer(utility, op, TARIFF, YEAR, false), { note: "operator licensed to publish tariffs" });

  const regn = await V.signCredential(dmvS, V.vehicleRegistration({ dmvDid: dmv, vehicleDid: vehicle, plate: "EV 3301", jurisdiction: "CA-BC", ownerDid: vehicle, validFrom: "2026-01-01", validUntil: "2027-01-01" }));
  const regId = T.parseEvent(ssi, await T.tx("issueCredential", "F5", "DMV", ssi.connect(dmvS).issueCredential(dmv, vehicle, regn.anchor, 0)), "CredentialIssued").credentialId;
  const tariff = await V.signCredential(opS, V.buildCredential({ tId: TARIFF, issuerDid: op, subjectDid: op, claims: { operatorDid: op, pricePerKWh: 0.32, currency: "CAD", maxKW: 150, validUntil: "2026-12-31" } }));
  const tariffId = T.parseEvent(ssi, await T.tx("issueCredential", "F5", "ChargingOperator", ssi.connect(opS).issueCredential(op, op, tariff.anchor, 0)), "CredentialIssued").credentialId;

  // Tier 2: handshake from caches (warmed earlier; here warmed inline and timed as instrumentation)
  const vCache = new V.VerifierCache(300_000), oCache = new V.VerifierCache(300_000);
  oCache.putController(dmv, await adapter.controllerOf(dmv)); vCache.putController(op, await adapter.controllerOf(op));
  { const [ok] = await reg.isEndorsed(dmv, V.TYPES.VEHICLE_REGISTRATION); oCache.putEndorsed(dmv, V.TYPES.VEHICLE_REGISTRATION, { ok }); }
  { const [ok] = await reg.isEndorsed(op, TARIFF); vCache.putEndorsed(op, TARIFF, { ok }); }
  { const [v] = await ssi.verifyCredential(regId); oCache.putStatus(regId, { valid: v }); }
  { const [v] = await ssi.verifyCredential(tariffId); vCache.putStatus(tariffId, { valid: v }); }
  T.view("prefetch", "F6", "both", "caches warmed: controllers, endorsements (G4), credential status (F6)");
  let t0 = performance.now();
  const vehOk = V.verifyOffline(regn, oCache).ok && oCache.endorsed.get(dmv + V.TYPES.VEHICLE_REGISTRATION).ok && oCache.status.get(regId).valid;
  const opOk = V.verifyOffline(tariff, vCache).ok && vCache.endorsed.get(op + TARIFF).ok && vCache.status.get(tariffId).valid;
  T.off("handshake", "Vehicle↔Operator", `mutual auth from caches: vehicle ok=${vehOk}, operator ok=${opOk} in ${(performance.now() - t0).toFixed(2)} ms laptop, zero chain reads (Tier 2 critical path)`);

  // Off-chain session: ECDH + AEAD metering messages; log Merkle-rooted at the end
  const ecdhA = crypto.createECDH("prime256v1"); ecdhA.generateKeys();
  const ecdhB = crypto.createECDH("prime256v1"); ecdhB.generateKeys();
  const key = crypto.createHash("sha256").update(ecdhA.computeSecret(ecdhB.getPublicKey())).digest();
  const log = [];
  for (let i = 0; i < 12; i++) {
    const iv = crypto.randomBytes(12), c = crypto.createCipheriv("aes-256-gcm", key, iv);
    const msg = JSON.stringify({ t: i * 300, kWh: +(i * 3.1).toFixed(2) });
    const ct = Buffer.concat([c.update(msg), c.final()]);
    log.push({ iv: iv.toString("hex"), ct: ct.toString("hex"), tag: c.getAuthTag().toString("hex") });
  }
  const sessionNonce = crypto.randomBytes(8).toString("hex");
  const meterRoot = V.contentHash(log);
  T.off("session", "Vehicle↔Operator", `12 AEAD metering messages (5-minute cadence), 37.2 kWh; log root ${meterRoot.slice(0, 12)}… (off-chain)`);

  // Asynchronous commits: both presentations (challenge-bound to the session nonce)
  const chV = V.presentationChallenge({ verifierDid: op, holderDid: vehicle, credentialIds: [regId], purpose: "charging", nonce: sessionNonce, domain: "cvin-sandbox" });
  await T.tx("createPresentation", "F8", "Vehicle", ssi.connect(vehicleS).createPresentation(vehicle, [regId], chV, "cvin-sandbox"), { note: "async commit of the vehicle's presentation" });
  const chO = V.presentationChallenge({ verifierDid: vehicle, holderDid: op, credentialIds: [tariffId], purpose: "charging", nonce: sessionNonce, domain: "cvin-sandbox" });
  await T.tx("createPresentation", "F8", "ChargingOperator", ssi.connect(opS).createPresentation(op, [tariffId], chO, "cvin-sandbox"), { note: "async commit of the operator's tariff presentation" });

  // Payment (rail is out of scope) → receipt credential anchored: commits to meter log + payment ref
  const paymentRef = "x402:" + crypto.randomBytes(6).toString("hex");
  const receipt = await V.signCredential(opS, V.buildCredential({ tId: ethers.id("cvin.charging.receipt.v1"), issuerDid: op, subjectDid: vehicle,
    claims: { sessionNonce, meterLogRoot: meterRoot, kWh: 37.2, amount: 11.9, currency: "CAD", paymentRef, tariffCredential: tariffId } }));
  const rcR = await T.tx("issueCredential", "F5", "ChargingOperator", ssi.connect(opS).issueCredential(op, vehicle, receipt.anchor, 0), { note: "payment-anchored receipt (amount/energy/location off-chain)" });
  const receiptId = T.parseEvent(ssi, rcR, "CredentialIssued").credentialId;
  T.view("verifyCredential", "F6", "Auditor", `receipt valid=${(await ssi.verifyCredential(receiptId))[0]}; disputes replay the AEAD log against meterLogRoot (doc 06 §3)`);
  T.off("summary", "Analyst", "Tier 2 path: 0 chain reads, 0 writes; Tier 3 asynchronous: 2×F8 + 1×F5; on-chain learns: two presentations happened and a receipt exists");
  T.write("s3_evcharging");
}
main().catch(e => { console.error(e); process.exit(1); });
