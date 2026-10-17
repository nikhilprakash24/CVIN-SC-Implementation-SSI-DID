// BBS+ selective-disclosure layer over the VID credential objects (HDA doc 02 §2, §10 stage b).
//
// The issuer signs the credential's claims as an ordered message vector with a BLS12-381 BBS+
// key (one signature over all messages). The holder later derives an unlinkable *proof* that
// reveals only a chosen subset of messages, bound to a verifier nonce. The verifier checks the
// proof against the issuer's public key alone — no chain access, and nothing on-chain changes
// versus the hash-anchored path: the SAME typed anchor (keccak over canonical JSON) is still
// what F5 commits to, so the BBS+ signature is an additional proof object held off-chain.
//
// Library: @mattrglobal/bbs-signatures 1.4 (WASM in Node). Timings reported by the scenario
// are laptop figures and are labelled as such; they are not OBU/RSU measurements.
const bbs = require("@mattrglobal/bbs-signatures");
const { canonicalize } = require("./credentials");

const enc = (s) => new TextEncoder().encode(s);

// Flatten credentialSubject into an ordered [name, canonicalValue] message list.
function messagesOf(credBody) {
  const subj = credBody.credentialSubject;
  const keys = Object.keys(subj).sort();
  return keys.map(k => `${k}=${canonicalize(subj[k])}`);
}

async function issuerKeyPair() {
  const bls = await bbs.generateBls12381G2KeyPair();
  return bls; // {publicKey, secretKey} (Uint8Array)
}

async function sign(keyPair, credBody) {
  const messages = messagesOf(credBody);
  const bbsKey = await bbs.bls12381toBbs({ keyPair, messageCount: messages.length });
  const signature = await bbs.blsSign({ keyPair, messages: messages.map(enc) });
  return { messages, signature, publicKey: keyPair.publicKey, bbsPublicKey: bbsKey.publicKey };
}

async function verifySignature(signed) {
  const r = await bbs.blsVerify({ publicKey: signed.publicKey, messages: signed.messages.map(enc), signature: signed.signature });
  return r.verified;
}

// Holder derives a proof revealing only `revealNames` (claim names), bound to `nonce`.
async function createProof(signed, revealNames, nonce) {
  const revealed = signed.messages.map((m, i) => (revealNames.includes(m.split("=")[0]) ? i : -1)).filter(i => i >= 0);
  const proof = await bbs.blsCreateProof({ signature: signed.signature, publicKey: signed.publicKey, messages: signed.messages.map(enc), nonce: enc(nonce), revealed });
  return { proof, revealedIndices: revealed, revealedMessages: revealed.map(i => signed.messages[i]), messageCount: signed.messages.length };
}

// Verifier checks the proof with only the issuer public key, the revealed messages, and the nonce.
async function verifyProof(publicKey, derived, nonce) {
  const r = await bbs.blsVerifyProof({ proof: derived.proof, publicKey, messages: derived.revealedMessages.map(enc), nonce: enc(nonce) });
  return r.verified;
}

module.exports = { messagesOf, issuerKeyPair, sign, verifySignature, createProof, verifyProof };
