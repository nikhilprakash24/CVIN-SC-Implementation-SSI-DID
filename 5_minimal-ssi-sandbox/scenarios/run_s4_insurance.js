// Scenario S4 — High-tier lifecycle: insurance credential (ICBC example from the 2020 paper),
// vehicle-history attestation, ownership transfer with key rotation.
//
// All synchronous chain writes (Tier 3). The ownership transfer is the interesting part: the
// interface has no controller-transfer function (F-note in HDA 04), so transfer = the new owner's
// DID receives a fresh registration while the old owner's delegate authority is withdrawn by
// expiry/rotation; the VEHICLE DID itself persists (it is the vehicle's, not the owner's), its
// keys are rotated (F9/F10) and the old owner's sigAuth delegate lapses.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_s4_insurance.js
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");

const IMPL = process.env.IMPL || "O1_ERC1056";
const B32 = (s) => ethers.id(s);
const YEAR = 365 * 24 * 3600;
const INSURANCE = ethers.id("cvin.insurance.policy.v1");

async function main() {
  const T = makeTrace(IMPL);
  const [adminS, ministryS, dmvS, icbcS, vehicleS, owner1S, owner2S, svcS] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const reg = await (await ethers.getContractFactory("EndorsementRegistry")).connect(adminS).deploy(await ssi.getAddress(), await adapter.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL} + adapter + EndorsementRegistry` });
  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;
  const issue = async (s, label, issuer, subject, cred, until, note) => T.parseEvent(ssi, await T.tx("issueCredential", "F5", label, ssi.connect(s).issueCredential(issuer, subject, cred.anchor, until), { note }), "CredentialIssued").credentialId;

  const ministry = await mk(ministryS, "Ministry"), dmv = await mk(dmvS, "DMV"), icbc = await mk(icbcS, "ICBC"), svc = await mk(svcS, "ServiceCenter");
  const vehicle = await mk(vehicleS, "Vehicle"), owner1 = await mk(owner1S, "Owner1"), owner2 = await mk(owner2S, "Owner2");
  await T.tx("addRoot", "G0", "Admin", reg.addRoot(ministry));
  for (const [s, did, role] of [[dmvS, dmv, V.ROLES.GOVERNMENT_DMV], [icbcS, icbc, V.ROLES.INSURANCE_COMPANY], [svcS, svc, V.ROLES.SERVICE_CENTER]])
    await T.tx("registerIssuer", "G1", "issuer", reg.connect(s).registerIssuer(did, role));
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.VEHICLE_REGISTRATION, YEAR, false));
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, icbc, INSURANCE, YEAR, false), { note: "ICBC licensed for commercial vehicle insurance" });
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, svc, V.TYPES.EV_MAINTENANCE, YEAR, false));

  // Owner1 era: registration, owner delegate on the vehicle DID, ICBC policy (the 2020 paper's example credential)
  const now = Math.floor(Date.now() / 1000);
  const reg1 = await V.signCredential(dmvS, V.vehicleRegistration({ dmvDid: dmv, vehicleDid: vehicle, plate: "GM 7781", jurisdiction: "CA-BC", ownerDid: owner1, validFrom: "2026-02-24", validUntil: "2027-02-24" }));
  const reg1Id = await issue(dmvS, "DMV", dmv, vehicle, reg1, now + YEAR, "registration → Owner1");
  await T.tx("addDelegate", "F11", "Vehicle", ssi.connect(vehicleS).addDelegate(vehicle, B32("owner"), owner1S.address, YEAR), { note: "Owner1 as 'owner' delegate of the vehicle DID" });
  const policy = await V.signCredential(icbcS, V.buildCredential({ tId: INSURANCE, issuerDid: icbc, subjectDid: vehicle,
    claims: { manufacturedBy: "General Motors of Canada", model: "GMC Savana Cargo", insuranceType: "Non-Fleet Commercial Vehicle Insurance Type C", insuranceExpiration: "2027-02-24", coverage: ["Extended Third Party Liability", "Collision", "Comprehensive Freight and Cargo"], policyHolder: owner1 } }));
  const policyId = await issue(icbcS, "ICBC", icbc, vehicle, policy, now + YEAR, "ICBC commercial policy (2020 paper, Fig. 5)");
  // History attestation
  const maint = await V.signCredential(svcS, V.lifecycleEvent({ tId: V.TYPES.EV_MAINTENANCE, issuerDid: svc, issuerRole: V.ROLES.SERVICE_CENTER, vehicleDid: vehicle, occurredAt: "2026-08-01", odometerKm: 41_200, details: { services: ["brakes"] } }));
  const maintId = await issue(svcS, "ServiceCenter", svc, vehicle, maint, 0, "history attestation");
  for (const [l, id] of [["registration", reg1Id], ["policy", policyId], ["maintenance", maintId]]) T.view("verifyCredential", "F6", "Buyer", `${l}: valid=${(await ssi.verifyCredential(id))[0]}`);

  // Sale: Owner1 → Owner2. Keys rotated, Owner1 delegate withdrawn (interface has no early
  // delegate revocation: re-issued with validity 0 → expired), registration + policy re-issued.
  const rcK = await T.tx("addVerificationMethod", "F9", "Vehicle", ssi.connect(vehicleS).addVerificationMethod(vehicle, B32("EcdsaSecp256k1VerificationKey2019"), "0x04" + crypto.randomBytes(8).toString("hex")), { note: "new vehicle key post-sale" });
  const newKey = T.parseEvent(ssi, rcK, "VerificationMethodAdded").keyId;
  const rcOld = await T.tx("addVerificationMethod", "F9", "Vehicle", ssi.connect(vehicleS).addVerificationMethod(vehicle, B32("EcdsaSecp256k1VerificationKey2019"), "0x04deadbeef"), { note: "(old key, registered for the demo)" });
  await T.tx("removeVerificationMethod", "F10", "Vehicle", ssi.connect(vehicleS).removeVerificationMethod(vehicle, T.parseEvent(ssi, rcOld, "VerificationMethodAdded").keyId), { note: "old key removed" });
  await T.tx("addDelegate", "F11", "Vehicle", ssi.connect(vehicleS).addDelegate(vehicle, B32("owner"), owner1S.address, 0), { note: "Owner1 delegate re-issued with validity 0 = withdrawn (no native early revocation)" });
  await T.tx("addDelegate", "F11", "Vehicle", ssi.connect(vehicleS).addDelegate(vehicle, B32("owner"), owner2S.address, YEAR), { note: "Owner2 as owner delegate" });
  await T.tx("updateDID", "F3", "Vehicle", ssi.connect(vehicleS).updateDID(vehicle, B32("cvin.owner"), ethers.getBytes(owner2), 0), { note: "owner attribute → Owner2" });
  await T.tx("revokeCredential", "F7", "DMV", ssi.connect(dmvS).revokeCredential(reg1Id), { note: "Owner1 registration revoked" });
  await T.tx("revokeCredential", "F7", "ICBC", ssi.connect(icbcS).revokeCredential(policyId), { note: "Owner1 policy cancelled" });
  const reg2 = await V.signCredential(dmvS, V.vehicleRegistration({ dmvDid: dmv, vehicleDid: vehicle, plate: "GM 7781", jurisdiction: "CA-BC", ownerDid: owner2, validFrom: "2026-10-19", validUntil: "2027-10-19" }));
  const reg2Id = await issue(dmvS, "DMV", dmv, vehicle, reg2, now + YEAR, "registration → Owner2");
  const policy2 = await V.signCredential(icbcS, V.buildCredential({ tId: INSURANCE, issuerDid: icbc, subjectDid: vehicle, claims: { ...policy.body.credentialSubject, policyHolder: owner2, insuranceExpiration: "2027-10-19" } }));
  const policy2Id = await issue(icbcS, "ICBC", icbc, vehicle, policy2, now + YEAR, "policy re-issued to Owner2");

  // After: old owner powerless, new owner in control, history intact, keys rotated
  T.view("validDelegate", "F12", "Verifier", `Owner1=${await ssi.validDelegate(vehicle, B32("owner"), owner1S.address)} Owner2=${await ssi.validDelegate(vehicle, B32("owner"), owner2S.address)}`);
  T.view("verifyCredential", "F6", "Verifier", `old reg valid=${(await ssi.verifyCredential(reg1Id))[0]} new reg valid=${(await ssi.verifyCredential(reg2Id))[0]} old policy valid=${(await ssi.verifyCredential(policyId))[0]} new policy valid=${(await ssi.verifyCredential(policy2Id))[0]} maintenance (history) valid=${(await ssi.verifyCredential(maintId))[0]}`);
  const [doc] = await ssi.resolveDID(vehicle);
  T.view("resolveDID", "F2", "Verifier", `vehicle DID persists across the sale; document ${doc.length / 2 - 1}B; newKey=${newKey.slice(0, 10)}…`);
  T.off("summary", "Analyst", "Tier 3 lifecycle: 8 F5, 2 F7, 2 F9, 1 F10, 3 F11, 1 F3 — all synchronous; FINDING: transfer needs re-issuance + delegate expiry because IMinimalSSI has neither controller transfer nor early delegate revocation (HDA 04, 05)");
  T.write("s4_insurance");
}
main().catch(e => { console.error(e); process.exit(1); });
