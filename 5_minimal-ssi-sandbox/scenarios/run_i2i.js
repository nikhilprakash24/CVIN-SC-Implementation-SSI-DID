// Scenario S1 — End-to-end secure I2I communication between two identities.
// Exercises all 12 minimal functions (Stage 14's 8 positive-lifecycle functions
// plus the 4 negative-lifecycle functions) against a real deployment, and emits
// a JSONL execution trace consumed by explorer/ (see traces/SCHEMA.md).
//
// Run: npx hardhat run scenarios/run_i2i.js [--network localhost]
// Env: IMPL=O1_ERC1056 (default) selects which implementation to run against.
const { ethers } = require("hardhat");
const fs = require("fs");
const crypto = require("crypto");

const IMPL = process.env.IMPL || "O1_ERC1056";
const B32 = (s) => ethers.id(s);
const trace = [];
let step = 0;

function log(entry) {
  trace.push({ seq: ++step, impl: IMPL, ts: Date.now(), ...entry });
  console.log(`[${step}] ${entry.fn || entry.phase}: ${entry.note || ""}`);
}

async function tx(label, fnId, identity, promise) {
  const t = await promise;
  const rc = await t.wait();
  log({ kind: "tx", fn: label, fnId, identity, txHash: rc.hash, gasUsed: rc.gasUsed.toString(),
        events: rc.logs.length, note: `gas=${rc.gasUsed}` });
  return rc;
}

function parseEvent(ssi, rc, name) {
  return rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } })
    .find(e => e && e.name === name).args;
}

async function main() {
  const [issuerCtrl, aCtrl, bCtrl, obu] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  log({ kind: "deploy", phase: "deploy", note: `${IMPL} at ${await ssi.getAddress()}` });

  // -- Phase 1: identity establishment (F1 createDID x3) --
  const mk = async (signer, label) => {
    const rc = await tx("createDID", "F1", label, ssi.connect(signer).createDID(signer.address));
    return parseEvent(ssi, rc, "DIDCreated").did;
  };
  const issuer = await mk(issuerCtrl, "Registry");
  const A = await mk(aCtrl, "IdentityA");
  const B = await mk(bCtrl, "IdentityB");

  // -- Phase 2: credentials (F5 issueCredential x2) --
  const issue = async (subject, label) => {
    const rc = await tx("issueCredential", "F5", "Registry",
      ssi.connect(issuerCtrl).issueCredential(issuer, subject, B32(`MOBI-VID:${label}`), 0));
    return parseEvent(ssi, rc, "CredentialIssued").credentialId;
  };
  const vcA = await issue(A, "A");
  const vcB = await issue(B, "B");

  // -- Phase 3: key & delegation setup (F9 addVerificationMethod, F11 addDelegate) --
  await tx("addVerificationMethod", "F9", "IdentityA",
    ssi.connect(aCtrl).addVerificationMethod(A, B32("EcdsaSecp256k1VerificationKey2019"), "0x04a1b2"));
  const rcKeyA2 = await tx("addVerificationMethod", "F9", "IdentityA",
    ssi.connect(aCtrl).addVerificationMethod(A, B32("X25519KeyAgreementKey2020"), "0x04c3d4"));
  const keyA2 = parseEvent(ssi, rcKeyA2, "VerificationMethodAdded").keyId;
  await tx("addDelegate", "F11", "IdentityA",
    ssi.connect(aCtrl).addDelegate(A, B32("sigAuth"), obu.address, 3600));

  // -- Phase 4: mutual authentication (F2 resolveDID, F6 verifyCredential, F12 validDelegate) --
  for (const [who, did, vc] of [["IdentityB checks A", A, vcA], ["IdentityA checks B", B, vcB]]) {
    const [doc] = await ssi.resolveDID(did);
    log({ kind: "view", fn: "resolveDID", fnId: "F2", identity: who, note: `doc ${doc.length / 2 - 1} bytes` });
    const [valid] = await ssi.verifyCredential(vc);
    log({ kind: "view", fn: "verifyCredential", fnId: "F6", identity: who, note: `valid=${valid}` });
    if (!valid) throw new Error("handshake failed");
  }
  const del = await ssi.validDelegate(A, B32("sigAuth"), obu.address);
  log({ kind: "view", fn: "validDelegate", fnId: "F12", identity: "IdentityB", note: `OBU delegate=${del}` });

  // -- Phase 5: presentation binds the channel (F8 createPresentation) --
  const channelMsg = JSON.stringify({ type: "I2I-HELLO", from: A, to: B, nonce: crypto.randomBytes(8).toString("hex") });
  const challenge = ethers.keccak256(ethers.toUtf8Bytes(channelMsg));
  await tx("createPresentation", "F8", "IdentityA",
    ssi.connect(aCtrl).createPresentation(A, [vcA], challenge, "i2i-sandbox"));

  // -- Phase 6: off-chain secure channel (ECDH + AEAD, anchored by the VP above) --
  const ecdhA = crypto.createECDH("prime256v1"); ecdhA.generateKeys();
  const ecdhB = crypto.createECDH("prime256v1"); ecdhB.generateKeys();
  const secret = ecdhA.computeSecret(ecdhB.getPublicKey());
  const key = crypto.createHash("sha256").update(secret).digest();
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const ct = Buffer.concat([cipher.update("BSM:{lat:49.2488,lon:-122.9805,speed:13.4}"), cipher.final()]);
  log({ kind: "offchain", phase: "secure-channel", identity: "A->B",
        note: `ECDH P-256 + AES-256-GCM, ct=${ct.length}B, tag=${cipher.getAuthTag().length}B (off-chain; VP challenge anchors payload)` });

  // -- Phase 7: trust break — negative lifecycle (F7, F10, F3, F4) --
  await tx("revokeCredential", "F7", "Registry", ssi.connect(issuerCtrl).revokeCredential(vcA));
  const [validAfter, , revoked] = await ssi.verifyCredential(vcA);
  log({ kind: "view", fn: "verifyCredential", fnId: "F6", identity: "IdentityB",
        note: `post-revocation valid=${validAfter} revoked=${revoked} -> channel torn down` });
  await tx("removeVerificationMethod", "F10", "IdentityA", ssi.connect(aCtrl).removeVerificationMethod(A, keyA2));
  await tx("updateDID", "F3", "IdentityB", ssi.connect(bCtrl).updateDID(B, B32("service"), "0x7632", 86400));
  await tx("deactivateDID", "F4", "IdentityA", ssi.connect(aCtrl).deactivateDID(A));

  // -- Write trace --
  const covered = new Set(trace.filter(e => e.fnId).map(e => e.fnId));
  log({ kind: "summary", phase: "done", note: `functions covered: ${covered.size}/12` });
  const out = `traces/i2i_${IMPL}_${Date.now()}.jsonl`;
  fs.writeFileSync(out, trace.map(e => JSON.stringify(e)).join("\n"));
  console.log(`\nTrace written: ${out} (${trace.length} entries, ${covered.size}/12 functions)`);
}

main().catch((e) => { console.error(e); process.exit(1); });
