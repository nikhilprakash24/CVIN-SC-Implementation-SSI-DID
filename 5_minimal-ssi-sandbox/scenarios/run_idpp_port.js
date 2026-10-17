// Scenario S5 — ID Porting Protocol (IDPP): identity + credentials ported O1 (ERC-1056) → O8 (Indy-on-Besu).
//
// Operationalises the 2020 CVIN paper's IDPP concept (Local CVINs derived from a Global CVIN;
// porting an identity between ledgers). Steps:
//   1. On the SOURCE option: vehicle DID (F1), a VID birth credential (F5), a delegate (F11).
//   2. Export: the holder's off-chain state (credential objects, keys) plus the source anchors.
//   3. On the TARGET option: new DID (F1) for the same controller; re-anchor the SAME credential
//      objects (same typed hash) under the issuer's target DID (F5); re-establish the delegate (F11).
//   4. Continuity: the source DID is deactivated (F4) after a pointer attribute (F3) that names
//      the target DID — "ported-to" — so a resolver following the source finds the target; the
//      target carries a "ported-from" attribute. The credential hash is identical on both sides,
//      so an off-chain verification against either anchor is the same check.
//   5. Assertions: source deactivated and still resolvable; target active; credential verifies on
//      target (F6) and is unchanged off-chain; delegate valid on target (F12), invalid on source.
//
// Run: SRC=O1_ERC1056 DST=O8_LFDT npx hardhat run scenarios/run_idpp_port.js
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");

const SRC = process.env.SRC || "O1_ERC1056";
const DST = process.env.DST || "O8_LFDT";
const B32 = (s) => ethers.id(s);

async function main() {
  const T = makeTrace(`${SRC}_to_${DST}`);
  const [oemS, vehicleS, obu] = await ethers.getSigners();
  const src = await (await ethers.getContractFactory(SRC)).deploy();
  const dst = await (await ethers.getContractFactory(DST)).deploy();
  T.log({ kind: "deploy", phase: "deploy", note: `source ${SRC} @ ${await src.getAddress()} · target ${DST} @ ${await dst.getAddress()} (two ledgers simulated as two registries)` });

  const mk = async (c, s, l) => T.parseEvent(c, await T.tx("createDID", "F1", l, c.connect(s).createDID(s.address)), "DIDCreated").did;

  // ---- 1. source ledger ----
  const oemSrc = await mk(src, oemS, "OEM@source");
  const vehSrc = await mk(src, vehicleS, "Vehicle@source");
  const vin = "2HGFC2F59NH123456", vinSalt = crypto.randomBytes(16).toString("hex");
  const birth = await V.signCredential(oemS, V.vidBirth({ oemDid: oemSrc, vehicleDid: vehSrc, vin, vinSalt, make: "Honda", model: "Civic", modelYear: 2026, productionDate: "2026-05-02", plantCode: "ALLISTON-01" }));
  const rcB = await T.tx("issueCredential", "F5", "OEM@source", src.connect(oemS).issueCredential(oemSrc, vehSrc, birth.anchor, 0), { note: "VID_BIRTH anchored on source" });
  const credSrc = T.parseEvent(src, rcB, "CredentialIssued").credentialId;
  await T.tx("addDelegate", "F11", "Vehicle@source", src.connect(vehicleS).addDelegate(vehSrc, B32("sigAuth"), obu.address, 7200), { note: "OBU delegate on source" });
  T.view("verifyCredential", "F6", "Verifier", `source: valid=${(await src.verifyCredential(credSrc))[0]}`);

  // ---- 2. export (off-chain) ----
  const wallet = new V.Wallet(vehSrc); wallet.store(credSrc, birth);
  const exportBundle = { sourceDid: vehSrc, sourceRegistry: await src.getAddress(), credentials: wallet.list().map(([id, c]) => ({ sourceCredentialId: id, anchor: c.anchor, body: c.body, proof: c.proof })), delegates: [{ type: "sigAuth", address: obu.address }] };
  const bundleHash = V.contentHash(exportBundle);
  T.off("export", "Vehicle", `holder bundle: ${exportBundle.credentials.length} credential(s), ${exportBundle.delegates.length} delegate(s); bundleHash=${bundleHash.slice(0, 12)}… (content never on-chain)`);

  // ---- 3. target ledger: re-anchor ----
  const oemDst = await mk(dst, oemS, "OEM@target");
  const vehDst = await mk(dst, vehicleS, "Vehicle@target");
  // The credential object is re-signed by the issuer under its target DID? No: the ORIGINAL object and
  // signature are kept (same bytes, same typed hash); only the anchor is re-created on the target by
  // the issuer's target DID. Issuer-side continuity: oemSrc ↔ oemDst is itself a ported pair.
  const rcB2 = await T.tx("issueCredential", "F5", "OEM@target", dst.connect(oemS).issueCredential(oemDst, vehDst, birth.anchor, 0), { note: "SAME typed hash re-anchored on target" });
  const credDst = T.parseEvent(dst, rcB2, "CredentialIssued").credentialId;
  await T.tx("addDelegate", "F11", "Vehicle@target", dst.connect(vehicleS).addDelegate(vehDst, B32("sigAuth"), obu.address, 7200), { note: "OBU delegate re-established" });
  await T.tx("updateDID", "F3", "Vehicle@target", dst.connect(vehicleS).updateDID(vehDst, B32("cvin.portedFrom"), ethers.concat([ethers.getBytes(vehSrc), ethers.getBytes(ethers.zeroPadValue(await src.getAddress(), 32))]), 0), { note: "ported-from pointer (source DID + registry)" });

  // ---- 4. source: pointer then deactivate ----
  await T.tx("updateDID", "F3", "Vehicle@source", src.connect(vehicleS).updateDID(vehSrc, B32("cvin.portedTo"), ethers.concat([ethers.getBytes(vehDst), ethers.getBytes(ethers.zeroPadValue(await dst.getAddress(), 32))]), 0), { note: "ported-to pointer (target DID + registry)" });
  await T.tx("deactivateDID", "F4", "Vehicle@source", src.connect(vehicleS).deactivateDID(vehSrc), { note: "source identity retired; history retained" });

  // ---- 5. continuity assertions ----
  const [docS, metaS] = await src.resolveDID(vehSrc);
  const mS = ethers.AbiCoder.defaultAbiCoder().decode(["tuple(uint256,uint256,bool,uint256)"], metaS)[0];
  const [docD, metaD] = await dst.resolveDID(vehDst);
  const mD = ethers.AbiCoder.defaultAbiCoder().decode(["tuple(uint256,uint256,bool,uint256)"], metaD)[0];
  const [vS] = await src.verifyCredential(credSrc);
  const [vD, issD, revD] = await dst.verifyCredential(credDst);
  const delS = await src.validDelegate(vehSrc, B32("sigAuth"), obu.address);
  const delD = await dst.validDelegate(vehDst, B32("sigAuth"), obu.address);
  const cache = new V.VerifierCache(60000); cache.putController(oemSrc, oemS.address);
  const off = V.verifyOffline(birth, cache);
  const checks = {
    sourceResolvable: docS.length > 2, sourceDeactivated: mS[2] === true, targetActive: mD[2] === false && docD.length > 2,
    credentialHashIdentical: birth.anchor === exportBundle.credentials[0].anchor,
    sourceCredentialStillValidOnChain: vS, // F6 on source: issuer (OEM@source) still active → true; policy must follow the pointer
    targetCredentialValid: vD && issD === oemDst && !revD,
    offchainVerifyUnchanged: off.ok, delegateInvalidOnSource: delS === false, delegateValidOnTarget: delD === true,
  };
  for (const [k, v] of Object.entries(checks)) T.view("assert", "P1", "IDPP", `${k}=${v}`);
  const pass = Object.values(checks).every(Boolean);
  T.off("continuity", "IDPP", `${pass ? "PASS" : "FAIL"}: identity retired on ${SRC} with pointer, re-anchored on ${DST}; same credential bytes verify off-chain and on target. FINDING: the source anchor stays F6-valid after the port (issuer not deactivated) — a verifier must honour the ported-to pointer; IMinimalSSI has no 'superseded' status (spec v1.1 candidate)`);
  T.write("idpp_port");
}
main().catch(e => { console.error(e); process.exit(1); });
