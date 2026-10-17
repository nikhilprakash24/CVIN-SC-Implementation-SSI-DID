CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Identity-to-Identity Secure Communication and the Cruxes It Exposes**

**The I2I secure channel as the thesis's core demonstration: what scenario S1 proves, the protocol specified properly, the eight cruxes with stances and settling tests, channel data placement, CAV and agent scenario pairs, relation to existing protocols, and the demonstration plan**

Document 9 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose → Chapter 5, §5.2 (I2I generalisation to agents); Chapter 4 (S1 scenario analysis); Memo A §4/§5 promotion*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 0. Scope and claim

This document takes the one scenario the sandbox has actually executed end to end, S1 "end-to-end secure identity-to-identity (I2I) channel", and asks what it would take to turn it from a demonstration into a design. The claim is that the I2I channel is the correct *core demonstration* of the thesis, because it is the only artefact that exercises all twelve functions of the minimal specification in one causal chain and because it is where the on-chain/off-chain split (01), selective disclosure (02) and the hybrid placement rules (03) all become operational at once: a channel is exactly the object that must read on-chain identity state, must not wait on the chain to carry traffic, and must react when that state changes.

The argument runs in seven steps. §1 reads the S1 trace and separates what it proves from what it does not. §2 specifies the I2I protocol properly, phase by phase, saying for every message what is signed, encrypted and anchored. §3 treats the eight cruxes the protocol exposes, each with a stance and the test that would settle it. §4 places every datum of the channel on-chain, off-chain or in cache, and gives the per-session cost as a formula whose only measured terms are S1's gas numbers. §5 gives two CAV and two agent scenarios built on the channel. §6 relates the design to DIDComm v2, TLS, Noise, IEEE 1609.2 and the A2A/MCP transports, isolating what the thesis contributes. §7 is the demonstration plan. Nothing here alters `IMinimalSSI`; everything sits beside it.

Two rules from the campaign brief govern the register. No number is presented as measured unless it is in the S1 trace file `traces/i2i_O1_ERC1056_1780620182135.jsonl`; every other quantity is a target, a budget, or a formula with variables. And where the design is clever, the assumption that makes it work and the condition that breaks it are stated together.

---

## 1. What S1 already proves, and what it does not

### 1.1 The trace as evidence

S1 (`scenarios/run_i2i.js`, sandbox v1.3, option O1_ERC1056, Hardhat local EVM, solc 0.8.24) produced a 22-entry JSONL trace covering 12/12 functions with real gas. The trace is the evidentiary artefact; the script is the procedure. Read in order, it is a single causal story: three identities are created, two credentials are issued, one identity provisions signing and key-agreement material and delegates signing authority to an on-board unit (OBU), the two identities mutually authenticate by reading chain state, one of them anchors a presentation bound to a channel hello, an off-chain authenticated-encryption channel is established, and the issuer revokes the credential mid-session, after which the verifier observes the revocation and the channel is torn down; the negative lifecycle then completes with key removal, document update, and deactivation.

| seq | kind | fn (F-tag) | identity | measured | note |
|---|---|---|---|---|---|
| 1 | deploy | — | — | — | O1_ERC1056 deployed |
| 2 | tx | createDID (F1) | Registry | 178,935 gas | issuer root |
| 3 | tx | createDID (F1) | IdentityA | 161,835 gas | |
| 4 | tx | createDID (F1) | IdentityB | 161,823 gas | |
| 5 | tx | issueCredential (F5) | Registry → A | 130,163 gas | hash `MOBI-VID:A`, validUntil 0 |
| 6 | tx | issueCredential (F5) | Registry → B | 130,163 gas | hash `MOBI-VID:B` |
| 7 | tx | addVerificationMethod (F9) | IdentityA | 59,607 gas | secp256k1 signing key |
| 8 | tx | addVerificationMethod (F9) | IdentityA | 59,607 gas | X25519 key-agreement key |
| 9 | tx | addDelegate (F11) | IdentityA | 54,227 gas | OBU, sigAuth, 3,600 s |
| 10–13 | view | resolveDID (F2), verifyCredential (F6) ×2 each way | B checks A; A checks B | gas-free | doc 96 bytes; valid=true |
| 14 | view | validDelegate (F12) | IdentityB | gas-free | OBU delegate=true |
| 15 | tx | createPresentation (F8) | IdentityA | 62,441 gas | challenge = keccak(I2I-HELLO) |
| 16 | offchain | secure-channel | A→B | — | ECDH P-256 + AES-256-GCM, ct 42 B, tag 16 B |
| 17 | tx | revokeCredential (F7) | Registry | 32,980 gas | |
| 18 | view | verifyCredential (F6) | IdentityB | gas-free | valid=false, revoked=true → channel torn down |
| 19 | tx | removeVerificationMethod (F10) | IdentityA | 36,478 gas | removes X25519 key |
| 20 | tx | updateDID (F3) | IdentityB | 44,760 gas | service endpoint, 86,400 s; 2 events |
| 21 | tx | deactivateDID (F4) | IdentityA | 55,127 gas | |
| 22 | summary | — | — | — | 12/12 functions |

The `ts` fields span 1780620182075 to 1780620182135, sixty milliseconds of wall clock for the whole run. That figure is a property of an in-process, auto-mining Hardhat node with no network and must not be read as a latency; it is cited here only because §7 relies on the `ts` field existing and being usable once a real transport is inserted.

### 1.2 What the trace proves

Four things are established by S1 and can be carried into Chapter 4 as findings rather than hypotheses.

*Mutual authentication is a pure read path.* Entries 10–14 are all `view` calls: each side resolves the other's DID document (F2), checks the other's credential (F6), and B checks that A's OBU is a valid signing delegate (F12). No transaction is needed to authenticate; the chain is consulted, not written. This is the read/write asymmetry that 01 makes the central placement axis, observed rather than argued.

*The presentation binds the channel to on-chain state.* Entry 15 anchors a presentation whose challenge is the keccak-256 digest of the channel's hello message (type, from, to, nonce). The presentation identifier therefore commits, on-chain, to a specific channel instance and cannot be replayed for another (the interface's F8 contract includes challenge replay prevention). This is the thesis's structural contribution to the channel and is treated at length in §2.5 and §6.

*The secure channel is off-chain by construction.* Entry 16 is the only `offchain` entry and it is where the traffic goes: P-256 ECDH, SHA-256 key derivation, AES-256-GCM with a 12-byte IV and a 16-byte tag over a 42-byte plaintext. The chain never sees the session key, the payload, or the ciphertext. This instantiates the Memo A rule that content and logs are off-chain with anchors on-chain.

*Revocation tears down a live channel through the same read path that established it.* Entries 17–18: the issuer revokes, the verifier re-reads F6 and sees `revoked=true`, and the scenario declares the channel torn down. The mechanism is symmetric with the handshake, which is what makes the cache-invalidation rule of §3(a) natural: the same call that admits a peer is the call that expels it.

A fifth observation is a cost finding rather than a security one: of the twelve functions, the ones the channel *itself* needs at runtime are F2, F6, F12 (free) and F8 (62,441 gas on O1). Everything else in the trace is lifecycle set-up or tear-down that happens at Tier 3 frequencies. §4 builds the per-session cost model on exactly this split.

### 1.3 What the trace does not prove

Honesty about the gaps is what turns S1 into a plan. The following are absent, and each reappears as a design element in §2 or a measurement in §7.

*No real transport.* Both identities are signers in one Node.js process. There are no sockets, no framing, no loss, no reordering, and no adversary on the wire. The "channel" is a key derivation and one encryption.

*No forward secrecy ratchet and no rotation.* One ECDH exchange yields one key which encrypts one message. There is no ephemeral-plus-static construction, no rekeying, and no per-message key evolution; compromise of the single P-256 private key would expose the single message.

*No DIDComm or other framing.* The hello is an ad-hoc JSON object; there is no envelope, no message identifier, no thread, no `from`/`to` resolution against verification methods. The key-agreement verification method added at entry 8 (`X25519KeyAgreementKey2020`, placeholder bytes `0x04c3d4`) is *not* the key used for the ECDH at entry 16, which is a freshly generated P-256 pair. The trace therefore shows the two halves of the design, an on-chain key reference and an off-chain key agreement, without yet joining them. Joining them is §2.4.

*No latency measurement.* The `ts` fields exist but measure process time. Handshake latency, teardown latency after revocation, and the effect of chain round trips are all unmeasured.

*A single chain, single option.* O1 only; no L2, no sidechain, no reorg, no delayed finality.

*No offline mode.* Every F2/F6/F12 call succeeds synchronously. The scenario cannot say what happens when a peer cannot reach the chain, which is the normal condition of a vehicle.

*No group, no dispute, no log.* Two parties, no third; no signed execution trace, no anchored log root; the teardown is the end of the story, with no dispute path.

Each of these is a crux or a demonstration step below.

---

## 2. The I2I protocol, specified

### 2.1 Design principles and notation

The channel is designed under five principles inherited from the memos and from 03. (i) The chain is a *root of trust and a registry*, never a message bus: no protocol message is a transaction, and the only transactions are lifecycle events and anchors. (ii) Authentication derives from the DID document (F2) and delegate state (F12); authorisation derives from credentials (F6) and endorsements (G4); the transport carries neither. (iii) Every message is bound to a channel instance so that nothing can be replayed across instances. (iv) Cache invalidation is synchronised with revocation state (Memo A), which makes the staleness window a declared security parameter rather than an accident. (v) Nothing assumes a particular transport; §3(e) lists what the identity layer may and may not presuppose.

Notation. `A`, `B` are DIDs (`bytes32`). `doc(A)` is A's resolved document with version identifier `v(A)`. `sk_A^sig`, `pk_A^sig` are a signing key pair registered via F9 (or a delegate key registered via F11). `pk_A^ka` is A's static key-agreement public key registered via F9 with key type `X25519KeyAgreementKey2020` (or a P-256 `EcdsaSecp256r1` key where hardware dictates; §2.4). `e_A` is an ephemeral key-agreement pair generated per channel. `H` is keccak-256 on-chain and SHA-256 off-chain, as the sandbox already does; `KDF` is HKDF-SHA256. `cid` is the channel identifier, `pid` a presentation identifier returned by F8, `sid` a session policy identifier. Sig(k, m) is a signature; AEAD(k, n, ad, m) is authenticated encryption with associated data.

The phases follow Memo A's A2A sequence: discovery → handshake → session policy → interaction (with logging) → revocation/dispute signalling.

### 2.2 Phase 0: discovery

The claim is that discovery must resolve a *peer DID to a set of endpoints and keys* without a synchronous chain read on the critical path, and that the chain's role is to make the cached answer verifiable rather than to serve it.

For vehicles, discovery is physical: a broadcast or a roadside unit (RSU) beacon carries the peer's DID (in the pseudonymous mode of §3(d), a pairwise DID) and, optionally, a compact *DID document digest* `H(doc(B)) ‖ v(B)`. For agents, discovery is a directory lookup or an ERC-8004 identity registry entry [19] whose service endpoint is read through F2's `updateDID`-set `service` attribute (as S1 entry 20 does with a service value and 86,400 s validity).

A `DISCOVER` message is unsigned and unencrypted and contains only `{B, endpoints, docDigest, v(B)}`. It is not trusted; it is a hint. The verifier resolves `doc(B)` either from cache, if the cached version matches `v(B)` and the cache is within the staleness window of §3(a), or from the chain via F2. The chain is authoritative; the beacon is an index. What breaks this is a beacon that advertises a *stale but valid* version to force use of a since-rotated key; §3(b) treats that downgrade.

### 2.3 Phase 1: handshake

The handshake is four messages. Its purpose is mutual authentication (F2, F6, F12 on each side), key agreement (§2.4), and channel binding to an anchored presentation (§2.5). The structure is a Noise-style XX pattern with the static keys being DID verification methods and the "certificate" being a challenge-bound presentation.

| # | Message | Contents | Signed by | Encrypted | Anchored |
|---|---|---|---|---|---|
| 1 | HELLO (A→B) | `cid`, `A`, `v(A)`, `e_A`, `n_A`, transport capabilities, policy request | `sk_A^sig` or OBU delegate key | no | no |
| 2 | HELLO-ACK (B→A) | `cid`, `B`, `v(B)`, `e_B`, `n_B`, transport selection, `pid_B` (optional, §2.5) | `sk_B^sig` | no | `pid_B` via F8 if present |
| 3 | AUTH (A→B) | presentation `VP_A` (credential ids, disclosed claims or ZK proof per 02), `pid_A`, session policy proposal | `sk_A^sig` | yes, under `k_hs` | `pid_A` via F8 |
| 4 | AUTH-ACK (B→A) | `VP_B`, `pid_B`, session policy acceptance, `sid` | `sk_B^sig` | yes, under `k_hs` | `pid_B` via F8 |

On receipt of HELLO, B performs the read path S1 already exercises: `resolveDID(A)` (F2), then checks that the signature on HELLO verifies under a key in `doc(A)` or, if the signer is an OBU address, that `validDelegate(A, sigAuth, obu)` (F12) is true. B then derives the handshake key `k_hs` from the ephemeral exchange and both static key-agreement keys (§2.4). AUTH is the first encrypted message; it carries A's presentation and, after B verifies `verifyCredential` (F6) for every credential it references and `isEndorsed` (G4) for each issuer against the credential type, the handshake is complete from B's side. AUTH-ACK mirrors it.

S1 entries 10–15 are messages 1–3 collapsed: the resolve/verify/validDelegate views are B's processing of HELLO, and `createPresentation` at entry 15 is the anchoring of `pid_A` with `challenge = H(HELLO)`. What S1 lacks is message 4 (B never presents to A, so the binding is one-sided) and the encryption of message 3.

### 2.4 Key agreement from DID verification methods

The claim is that the key-agreement key must be *the one the DID document says it is*, and that a per-channel ephemeral must be mixed in so that the static key's compromise does not expose past sessions.

Static keys. Each identity registers a key-agreement verification method via F9 with type `X25519KeyAgreementKey2020` (preferred: constant-time, 32-byte keys, ubiquitous in DIDComm v2 and Noise) or `EcdsaSecp256r1VerificationKey2019` for P-256 where the OBU's hardware security module only exposes NIST curves (the sandbox's `crypto.createECDH("prime256v1")` is the P-256 path). F9 returns a `keyId`; the DID document lists it; F10 removes it (S1 entry 19). The trace's entry 8 is precisely this registration, with placeholder bytes; the design requires the real public key bytes there and requires that the channel's ECDH use *that* key. This is the single largest edit to S1 (§7 step 2).

Delegate keys. An OBU does not hold the vehicle's controller key. It holds a delegate key registered via F11 with type `sigAuth` and a validity (3,600 s in S1). For key agreement the OBU needs a key-agreement capability too; the spec's delegate types are `sigAuth` and `veriKey`, and neither is a key-agreement type. Two options exist without touching the interface: (i) the OBU's key-agreement key is registered by the controller via F9 as a verification method whose `keyId` is referenced in the OBU's HELLO, with authorisation to *use* it proven by the F12-valid signing delegate signing the HELLO; (ii) the ephemeral-only pattern, where the OBU's static contribution is omitted and authentication rests entirely on the F12-valid signature over the ephemeral. Option (i) is chosen: it preserves the Noise XX property that both static keys enter the key schedule, and it keeps the interface untouched. The cost is one extra F9 per OBU key (59,607 gas on O1, S1 entries 7–8) at provisioning time, not per session.

Derivation. With ephemeral pairs `e_A`, `e_B` and statics `s_A`, `s_B`:

```
ck0 = HKDF-Extract(salt = "CVIN-I2I-v1" ‖ cid, IKM = DH(e_A, e_B))
ck1 = HKDF-Extract(salt = ck0, IKM = DH(e_A, s_B))      // A knows B is B
ck2 = HKDF-Extract(salt = ck1, IKM = DH(s_A, e_B))      // B knows A is A
k_hs, k_send_A, k_send_B = HKDF-Expand(ck2, transcript_hash, 96)
```

`transcript_hash` is `H(HELLO ‖ HELLO-ACK)` and therefore includes `v(A)`, `v(B)`, both nonces and `cid`. Any mismatch between the version a party believes and the version its peer signed changes the transcript and fails the handshake; that is the first line of downgrade defence (§3(b)).

The assumption that makes this work is that the static key bytes on-chain are correct and current. What breaks it is a verifier using a cached document after F10 has removed the key: the cache rule of §3(a) and the versioned-document rule of §3(b) exist to bound that exposure.

### 2.5 Channel binding to the presentation challenge

The claim is that binding the presentation's challenge to the handshake transcript, and anchoring the presentation with F8, gives the channel a property no transport-layer protocol provides: an on-chain, replay-protected commitment that *this* identity presented *these* credentials for *this* channel.

The F8 signature is `createPresentation(holder, credentialIds[], challenge, domain) → presentationId`, and the interface requires holder-ownership verification and challenge replay prevention. Set

```
challenge = H("CVIN-I2I-bind" ‖ cid ‖ transcript_hash ‖ e_A ‖ e_B)
domain    = "i2i:" ‖ transport-label   (S1 uses "i2i-sandbox")
```

Because `transcript_hash` commits to both ephemerals and both nonces, the challenge is unique per channel instance; because F8 rejects a repeated challenge, an attacker who captured AUTH cannot re-anchor it; because `pid_A` is returned by the chain and included in AUTH-ACK's transcript, both parties end the handshake agreeing on the same anchored commitment. This is the analogue of TLS channel binding via exporter values (RFC 9266, DIGEST-LEVEL) with the difference that the bound value lives in a public registry rather than in the endpoints' memories, so a third party can later verify that the channel existed and who authenticated on it, without learning what was said.

Whether the anchor is written per session or per epoch is a cost decision (§4). The binding construction is the same in either case: per epoch, `pid` is replaced by a Merkle leaf of `challenge` under an epoch root anchored once, and AUTH carries the inclusion path. S1 uses the per-session form.

### 2.6 AEAD, forward secrecy, and rotation

Interaction traffic uses AES-256-GCM (as in S1) or ChaCha20-Poly1305 where the OBU lacks AES hardware, with a 96-bit nonce constructed as `direction ‖ epoch ‖ counter` and never random (random 96-bit nonces have an unacceptable collision bound at Tier 2 message rates over long sessions). Associated data is `cid ‖ sid ‖ msg_seq ‖ msg_type`, so a ciphertext cannot be moved between channels, sessions, or positions.

Forward secrecy comes in two layers. The handshake ephemerals give per-session forward secrecy: compromise of a static key after the session does not expose it. Within a session, a symmetric ratchet (`k_{i+1} = KDF(k_i, "ratchet")`, delete `k_i`) gives per-message forward secrecy at negligible cost, and an optional Diffie–Hellman ratchet every `R` messages or `T` seconds (Signal-style, DIGEST-LEVEL) gives post-compromise security. The choice of `R`, `T` is transport-dependent: on PC5 with sub-100 ms budgets the DH ratchet is deferred to idle periods; on HTTP for agents it can run every message.

Rotation of *static* keys is a lifecycle event, not a channel event: F9 adds the new key, F10 removes the old, and the document version increments. A live channel keyed to the removed static continues, because its session keys were derived from ephemerals; a *new* handshake must use the new key. The policy question of whether a live channel should be torn down on static-key removal is the same question as revocation propagation and is answered the same way (§3(a)): the channel's liveness is conditioned on a periodically refreshed read of chain state, and key removal is one of the conditions.

### 2.7 Session policy as a credential-derived object

The claim, which matters most for agents (§3(h)), is that what a channel is *allowed to carry* must be computed from verified credentials and endorsements, never from text exchanged on the channel.

A session policy `P` is a JSON object built by the verifier from the peer's verified presentation:

```
P = { sid, cid, peer: B,
      scopes: [ derived from (credentialType, disclosedClaims, issuerEndorsedFor) ],
      limits: { maxMsgs, maxBytes, maxDuration, maxValue },
      revocationCheck: { interval, staleMax, sources },
      logging: { level, anchorEpoch } ,
      expiresAt }
```

Each scope is a deterministic function of the tuple (credential type, the claims actually disclosed, and the endorsement state of the issuer for that type at issuance time, G4). A charging-tariff credential yields the scope `charge:session:start`; a fleet-operator credential with `authority=dispatch` yields `dispatch:*`; an agent's tool-access credential yields the tool names and rate limits it lists. `P` is signed by both parties in AUTH/AUTH-ACK, hashed into the session's associated data, and enforced by the receiver on every message: a message whose type is outside `P.scopes` is dropped and logged. Nothing in `P` can be widened by a message on the channel; widening requires a new presentation and a new `sid`.

The assumption is that credential schemas map to scopes unambiguously; that mapping is the `lib/vid/` policy table of 10 and is data, not code. What breaks it is a credential whose claims are natural-language strings — the mapping must reject them, which is §3(h)'s prompt-injection stance.

### 2.8 Interaction and logging

Each interaction message is `AEAD(k_dir, n, ad, payload)` with `ad` as in §2.6. Each party keeps an *execution log*: an append-only list of `(msg_seq, direction, H(payload), ts, type)`; the payloads themselves are retained or not according to `P.logging.level`. Every `P.logging.anchorEpoch` messages or seconds the party computes the Merkle root of its log since the last anchor, signs it, and either exchanges it with the peer (mutual acknowledgement, no chain) or anchors it (F3 `updateDID` with a log-root attribute, or an event-only anchor on a sidechain, per 01's placement rules). Anchoring is by policy, not by default; at Tier 2 it is per epoch or per dispute, never per message (§4).

### 2.9 Revocation and dispute signalling

Revocation reaches a live channel by two routes that must agree. The *pull* route is the one S1 shows: the verifier re-reads F6 (and F12, and F2's version) on a schedule fixed by `P.revocationCheck.interval`. The *push* route is a `REVOKE-NOTICE` message, signed by the issuer or by the peer, carrying the revocation event's transaction hash; the receiver treats it as a hint that forces an immediate pull. Push shortens the window; pull bounds it. §3(a) makes this precise.

Teardown is a signed `CLOSE` message with reason code (`revoked`, `expired`, `policy`, `keyRemoved`, `peerRequest`) and the final log root. A dispute is a `DISPUTE` message, or an out-of-band claim, that names a `cid`, a `pid`, and a log root; resolution consists in checking that the `pid` exists on-chain (F8 event), that the log root was mutually acknowledged or anchored, and then opening the relevant log entries under selective disclosure (02). The channel's on-chain footprint is therefore exactly what a dispute needs and nothing more.

### 2.10 Replay and equivocation defences

Replay is defeated at four levels: nonces in HELLO/HELLO-ACK (fresh transcript), F8's challenge-uniqueness (fresh anchor), the per-message counter nonce with strict monotonicity on receipt (fresh message), and `cid`/`sid` in associated data (no cross-channel migration). Equivocation — a party telling two peers two different things about its own state — is defeated on-chain by the fact that DID document version, credential state and delegate state have single global values, and off-chain by including `v(A)`, `v(B)` in the transcript so that a peer that later finds the version was stale has a signed statement of what the other party claimed. For logs, equivocation is defeated by mutual acknowledgement of roots; a party that later presents a different log has contradicted its own signature.

---

## 3. The cruxes

Each crux below states the problem, the candidate solutions, the chosen stance, what it costs, and the test that settles it. The tests are all runnable in the sandbox with the S1 extensions of §7, except where hardware is named.

### 3(a) Revocation propagation

*Problem.* A credential, delegate, or key can be revoked or removed while a channel is live. S1 shows the mechanism (revoke, re-read, tear down) but not the *time*: between the revocation transaction and the verifier's next read, the channel is carrying traffic on authority that no longer exists. That interval is the staleness window `W`.

*Candidates.* Poll: the verifier re-reads F6/F12/F2 every `I` seconds; `W ≤ I + t_read`. Push: the issuer or registry notifies subscribers; `W ≈ t_notify`, but push is unreliable over the transports of §3(e) and requires the issuer to know who to notify, which conflicts with unlinkability. Epoch: revocation state is published as a signed digest (status list [NEW-1] or accumulator, 02) at fixed epochs; `W ≤ epoch + t_fetch`, with the advantage that one fetch serves all peers and the digest can be pre-fetched (§3(c)). Event subscription on the chain itself: the verifier watches `CredentialRevokedEvent`/`DelegateAdded`/`VerificationMethodRemoved` logs; this is push with the chain as the notifier and works only where the verifier has a live chain connection.

*Stance.* Poll with epochs, push as accelerator. The channel policy carries `revocationCheck.interval = I` and `staleMax = W_max`; the verifier must have read a revocation state no older than `W_max` to *send or accept* a message, otherwise it enters the read-only degraded mode of 03 (accept nothing that changes state; keep the channel alive for safety traffic only). Push notices (`REVOKE-NOTICE`, chain event subscriptions) reset the timer to zero when they arrive but are never required. `W_max` is therefore a *security parameter of the session policy*, chosen per credential type: a toll credential might tolerate 300 s; a dispatch authority credential 10 s; a Tier 1 safety stream is out of scope and remains under SCMS [6], [28].

The rule that makes this coherent is Memo A's "cache invalidation synchronised with revocation state": the verifier's cache of `(doc(B), v(B), F6 results, F12 results)` carries a single timestamp `t_state` = the block time of the last state it read, and every cache entry is valid exactly while `now − t_state ≤ W_max`. There is no per-entry TTL; there is one clock. Revocation storms (an issuer revoking a whole fleet after a supply-chain compromise) are then not a special case: every verifier's next poll returns the new state, the cost is one read per verifier per epoch regardless of how many credentials changed, and the epoch digest is what keeps that read bounded.

*Trade-off.* Smaller `W_max` means more reads per session (or more epoch fetches), which at Tier 2 frequencies over cellular is a bandwidth cost and, on a public chain via an RPC provider, a rate-limit cost. Larger `W_max` means longer exposure. The design refuses to pick a single number; it makes the number a per-type policy and measures the consequence.

*Test.* S1 extension: insert a mock transport with configurable delay; run revocation at a random point mid-session with `I ∈ {1, 5, 30, 300}` s; record `ts` of the F7 transaction and `ts` of the first `CLOSE`; assert `teardown ≤ I + t_read + t_transport` and report the distribution. A second run with a push notice measures the improvement. The storm test revokes `N` credentials in one block and measures that verifier read cost is independent of `N`.

### 3(b) Key agreement from on-chain identity without a synchronous read

*Problem.* Resolving the peer's key-agreement key by calling F2 during the handshake puts a chain round trip on the Tier 2 critical path. Caching removes the round trip but admits a downgrade: an attacker who has compromised a key that has since been removed by F10 replays the old document.

*Candidates.* Always read (safe, slow). Cache with TTL (fast, unsafe by the TTL). Cache with version: the peer states `v(B)` in HELLO, signed; the verifier compares with its cached version; if equal and within `W_max`, use the cache; if the peer's version is newer, read; if the peer's version is *older* than the cache, reject (the peer is either stale or lying, and both are handshake failures). Signed document snapshots: the controller signs `(doc, v, t)` and the peer carries the snapshot; the verifier checks the signature against a key in its own cached document, which is circular unless the version rule is applied as well.

*Stance.* Cache with version, plus the one-clock rule of §3(a). The peer's signed `v(B)` in HELLO makes any downgrade attempt a signed statement: to use a removed key, the attacker must sign a HELLO claiming version `v_old`, and the verifier's cache, if it has ever seen `v_new`, rejects it. The residual exposure is a verifier that has *never* seen `v_new` and is within `W_max` of its last read; that is the same window as §3(a), by design, because a key removal is a lifecycle event of the same kind as a revocation. The ERC-1056 event-sourced model (O1) makes versions cheap: the document version is the block number of the last `DIDUpdated`/`VerificationMethodAdded`/`VerificationMethodRemoved`/`DelegateAdded` event for that DID, which is exactly what the `changed` pointer in the reference registry [23] tracks.

*Trade-off.* The peer must know its own version, which for an OBU means the vehicle's controller must push document updates to the OBU (a Tier 3 provisioning task). A peer that does not know its version cannot use the fast path and falls back to always-read.

*Test.* S1 extension: after the first handshake, remove A's key-agreement key via F10 (as entry 19 already does), then attempt a second handshake from an attacker process holding the old key and claiming the old version; assert rejection at B whether B's cache is fresh or stale, and measure the one case where the attack succeeds (B never observed the removal and is inside `W_max`), confirming that it is bounded by `W_max` and by nothing else.

### 3(c) Offline or partitioned peers

*Problem.* Two vehicles meet where neither can reach the chain. Mutual authentication requires reading the other's document, credential state and delegate state. The naive answer, "no chain, no channel", is unacceptable for Tier 2 operations that are safety-adjacent (cooperative manoeuvre negotiation, 05).

*Candidates.* Refuse. Trust-on-first-use (no). Pre-fetched signed state: each party carries its own document snapshot, its credentials' status-list or accumulator witness as of epoch `E`, and the issuer's signed epoch digest; the verifier checks signatures against issuer keys it already trusts (endorser roots, G2, are few and change slowly, so they are cached indefinitely) and accepts state no older than `W_max^offline`. Leases: an RSU that *does* have chain access issues a short-lived signed lease "as of block `b`, DID `A` has document version `v`, credential `c` unrevoked, delegate `d` valid until `t`", which A carries and presents; verifiers trust the RSU's key (itself an endorsed DID) for the lease duration.

*Stance.* Pre-fetched signed state for credentials (status list epoch digests and accumulator witnesses, whichever 02 selects per credential type), leases for delegate and document state (which change more often and are per-DID rather than per-issuer), and an explicit *offline policy class* in `P`: state-changing scopes are disabled, value limits are zero, logging is mandatory and the log root must be anchored at the next connectivity (the delayed-write mode of 06). The channel is therefore never refused for lack of chain access; it is narrowed.

What makes this work is that issuer and endorser keys are long-lived and the number of issuers is small, so their keys and their epoch digests can be cached without a version race. What breaks it is a compromised issuer key during the partition: revocation of the issuer itself (F4 on the issuer DID, or G3 revocation of its endorsement) cannot reach the offline verifier, and every credential from that issuer is trusted for up to `W_max^offline`. This is the irreducible cost of offline operation and must be stated as such in Chapter 4.

*Test.* S1 extension with a mock chain provider that returns "unreachable" for all F2/F6/F12 calls after a configurable block; assert that a handshake with pre-fetched state succeeds with the narrowed policy, that a handshake without pre-fetched state fails closed, that a state-changing message is refused, and that the deferred log root is anchored (F3) when the provider returns.

### 3(d) Pseudonymity versus accountability in the channel

*Problem.* SCMS achieves pseudonymity by rotating certificates; the accountability gap is that no one can answer "what did vehicle V do" [6]. A DID-anchored channel answers it too well: if the channel uses the vehicle's public DID, every RSU can link every session.

*Candidates.* Public DID always (accountable, linkable). Pairwise DID per peer (unlinkable across peers, but a pairwise DID with credentials needs the issuer to issue to each pairwise DID, or needs ZK presentations that prove credential holdership without revealing the subject DID, 02). Pseudonymous stream with escrowed linkability: the channel uses a pairwise or ephemeral DID; the presentation is a ZK proof of holdership under an accumulator; the presentation additionally carries an *escrow token* `Enc_pk_forensic(A ‖ cid)` signed under the pseudonym, so that a forensic tier holding the escrow key can link the channel to the public DID, and no one else can.

*Stance.* The 2020 paper's dual-mode identity [5] made operational: Tier 1 is out of scope (SCMS pseudonym certificates). Tier 2 channels default to pairwise DIDs with ZK presentations and an escrow token; Tier 3 channels (registration, insurance, payment settlement) use the verinym (public DID with MOBI VID [27]). The escrow key is held by the forensic authority under governance (an endorser-set decision, G2), and the *use* of the escrow key is itself an on-chain event (a `requestValidation` under Set C, C3, with the forensic authority as validator), so that de-anonymisation is accountable. The channel binding of §2.5 then still works under a pseudonym because F8 verifies holder ownership of the pseudonymous DID, which was created by F1 with the same controller.

*Trade-off.* Pairwise DIDs multiply F1 calls (161–179K gas each on O1, S1 entries 3–4), which at fleet scale forces them onto an L2 or sidechain (01, 03); the escrow token adds one public-key encryption per handshake and a governance procedure. Cross-peer unlinkability is also only as good as the transport: a PC5 MAC address or a cellular identifier that persists across pairwise DIDs undoes the work, which is §3(e)'s "must not assume".

*Test.* Sandbox: create `k` pairwise DIDs under one controller (F1 ×k), issue one credential to the public DID, run `k` handshakes each presenting under a different pairwise DID with an escrow token, and assert (i) no verifier can link two channels from the F8 events alone, (ii) the forensic key links all `k`, (iii) the linkage attempt appears as a C3 event. The ZK presentation component depends on 02's chosen cryptosuite and is out of the sandbox's current scope.

### 3(e) Transport diversity

*Problem.* The channel must run over DSRC or C-V2X PC5 (broadcast-capable, small MTU, no IP by default, tens of milliseconds), cellular Uu (IP, hundreds of milliseconds, metered), Wi-Fi (IP, opportunistic), and, for agents, HTTP/WebSocket or DIDComm over HTTP. The identity layer must not bake in any one.

*Stance.* The identity layer assumes: an unreliable datagram service with a maximum transmission unit `MTU ≥ 512` bytes; that the receiver can buffer at least one handshake message; that the sender can obtain a coarse time within `±W_max/2`. It must *not* assume: ordering, reliability, IP addressing, a persistent link-layer identifier, symmetric latency, or that both directions exist (broadcast discovery is one-directional). Consequences: HELLO and HELLO-ACK must fit in one datagram each, so presentations are deferred to AUTH and, on PC5, AUTH is fragmented with a per-fragment MAC under `k_hs`; the counter nonce with a receive window replaces ordering; the coarse time bound is what makes `W_max` enforceable offline.

Budgets are stated as targets, not results. For PC5 at Tier 2 the handshake budget is the tier ceiling, 500 ms, less two RSU or peer processing times; three datagram round trips at PC5 latencies (DIGEST-LEVEL, 3GPP PC5 studies report tens of milliseconds per hop, not read at source) leave room only if no chain read is on the path, which is why §3(b)'s cached fast path is not an optimisation but a requirement. For cellular Uu the same handshake fits in budget with one chain read if the RPC endpoint is edge-deployed (the 2020 paper's RSU-as-edge-server and MEC framing [5]). For agents over HTTP, latency budgets are Tier 3 and the constraint is instead bytes and message count, because agent sessions are long and many.

*Test.* Mock transport with parameters `(MTU, loss, delay, reorder)`; run the handshake under `{PC5-like, Uu-like, HTTP-like}` profiles; assert completion within the tier budget for the profiles where the design claims it, and report bytes on the wire per handshake (§7 metrics). Only hardware shows real PC5 numbers.

### 3(f) Multi-party and group channels

*Problem.* Platoons, intersections, and agent swarms are groups. Pairwise channels scale as `n²`; a group needs a shared key, a membership proof, and a way to remove a member whose credential is revoked.

*Candidates.* Pairwise mesh (simple; `n²` handshakes and F8 anchors). Leader-keyed group: the leader runs `n` pairwise handshakes and distributes a group key under each; `O(n)` handshakes, single point of compromise. Tree-based group key agreement (MLS, RFC 9420, DIGEST-LEVEL): `O(log n)` per membership change, forward secrecy and post-compromise security preserved, but heavier state per member. Membership proofs: each member's F8 presentation binds it to the *group* `cid`; the group's on-chain footprint is the set of `pid`s or a single Merkle root of them.

*Stance.* Leader-keyed for platoons and intersections (there is always a natural leader: the platoon head or the RSU, and the group is small and short-lived), MLS-style for agent swarms (long-lived, larger, no natural leader). In both, membership is *credential-gated*: joining requires a presentation whose challenge includes the group `cid` and the current membership epoch, and the group's revocation policy is the strictest `W_max` of any member's credential type. Removal on revocation is a rekey: leader-keyed groups rekey by `n−1` messages; MLS groups by `O(log n)`. The group's anchor is one F8 per member per join (or one Merkle-batched anchor per epoch), never per message.

*Trade-off.* Leader-keyed groups lose forward secrecy against a compromised leader for the group's lifetime, which is acceptable for a platoon of minutes and unacceptable for a swarm of days; hence two designs.

*Test.* Sandbox: `n = 5` identities, one leader, `n` handshakes, group key distribution, one member's credential revoked (F7), assert the rekey excludes the revoked member and that the remaining members' traffic continues; measure messages per join and per removal as a function of `n` (a count, not a latency).

### 3(g) Chain faults

*Problem.* The channel binds to on-chain state via `pid`, `v(A)`, `v(B)` and revocation epochs. Reorganisations can un-include a `createPresentation`; delayed finality can leave a revocation visible but not final; partitions can make two verifiers see different states.

*Stance.* The channel distinguishes *observed* from *final* state and behaves conservatively in the gap. A `pid` from an unfinalised block is accepted for the handshake (the alternative is a finality delay on every Tier 2 session, which is disqualifying on probabilistic-finality chains) but the session policy is marked `provisional` with reduced limits until the anchor is final; if the anchor is reorganised out, the presenter must re-anchor (F8 with the same challenge fails by replay prevention, so the challenge is re-derived with a fresh nonce, which in practice means a re-handshake). Revocations are acted on when *observed*, not when final: a false positive (a reorganised-out revocation) costs one unnecessary teardown; a false negative costs `W_max` of unauthorised traffic, and the design prefers the former. Under partition, a verifier that cannot reach a quorum of its configured chain endpoints treats itself as offline (§3(c)). On deterministic-finality chains (QBFT Besu, the E1 substrate of 03) the provisional state lasts one block; on probabilistic chains it lasts the confirmation depth the governance sets.

*Trade-off.* "Act on observed revocation" gives an attacker who can mount a reorg a denial-of-service lever; the mitigation is that the attacker must also forge an issuer signature to *cause* the revocation, so the lever is limited to un-doing legitimate ones, which the conservative teardown already handles.

*Test.* Hardhat supports snapshot/revert; the S1 extension anchors F8, snapshots, reverts (simulating a reorg), and asserts the channel detects the missing `PresentationCreated` event on its next state read and re-handshakes; a second test delays the verifier's view by `d` blocks and shows the provisional-policy limits apply until `d` is reached.

### 3(h) Agent-specific cruxes

The generalisation from vehicles to agents [11] changes what flows on the channel (tool calls, negotiations, delegated authority) and introduces attacks with no vehicular analogue.

*Confused deputy across delegation chains.* An agent acting for a principal acting for an organisation holds a chain of F11 delegations. The confused-deputy problem (Hardy 1988, DIGEST-LEVEL) is that the agent can be induced to use authority from one link of the chain for a purpose another link never granted. Stance: the session policy `P` is computed from the *intersection* of the scopes along the whole chain, not the union, and every F11 delegation carries a validity that the channel checks by F12 at each policy refresh. A delegate that is `sigAuth` for a DID can authenticate as it; it cannot inherit that DID's credentials unless a credential names the delegate's own DID as subject, which is what "credentials as portable attestations" means in Memo A. The channel does not carry authority; it carries proofs of authority whose scopes are intersected.

*Prompt-injection-resistant policy binding.* An agent's peer may send text designed to be interpreted as an instruction. Stance: the channel enforces `P`, and `P` is derived from credentials (F6-verified, G4-endorsed), never from message content. A message that says "you are now authorised to transfer funds" changes nothing, because authorisation is a scope in `P` and `P` cannot be widened on-channel (§2.7). The mapping from credential claims to scopes rejects free-text claims; a schema whose scope is described in natural language is not admissible as a policy source. This is the credential-layer analogue of separating data from control, and it is the strongest argument for putting agents on this identity system rather than on bearer tokens whose scopes are strings.

*Tool-call authorisation.* An agent-to-tool session (§5.4) is a channel where each message is a tool invocation. Each invocation is checked against `P.scopes` (tool name, argument constraints, rate, value limits) before execution; the check is local and needs no chain read; the credential that produced the scope is re-verified at `revocationCheck.interval`. Revoking the agent's tool credential (F7) therefore stops further calls within `W_max`, which is the same guarantee the vehicle channel has and is measured by the same test.

*Execution-trace logging with Merkle anchoring and selective-disclosure audit.* Memo A requires agents to leave signed execution traces. The channel log of §2.8 is that trace: per message, `(seq, direction, H(payload), ts, type, scope_used)`; per epoch, a Merkle root signed and mutually acknowledged, and anchored (F3 attribute or sidechain event) at the policy's cadence. An audit opens specific leaves under selective disclosure (02): the auditor is shown the entries relevant to the dispute with inclusion paths to the anchored root, and nothing else. This is operational transparency, not algorithmic transparency, in the sense of the Building Paths preface: the audit shows what the agent did and under what authority, not why.

*Test.* Sandbox agent scenario (§5.4): a delegation chain of depth 3 with narrowing scopes; assert `P` equals the intersection; send a message whose payload contains an "authorisation" string and assert no scope changes; revoke the tool credential mid-session and measure calls after revocation `≤ ⌈W_max / call_interval⌉`; anchor a log root and verify one leaf's inclusion against the anchored value.

---

## 4. Data placement of the channel and cost per session

### 4.1 Placement

The rule from 01 and 03 applies unchanged: on-chain holds discovery and lifecycle state and integrity anchors; off-chain holds content; cache holds verified copies with one clock. Applied to the channel:

| Datum | Placement | Written by | Read by | Notes |
|---|---|---|---|---|
| DID documents, verification methods, delegates | on-chain (F1, F3, F9, F10, F11) | controllers, Tier 3 | F2, F12 at handshake and refresh | versioned by last event |
| Credential anchors and revocation state | on-chain (F5, F7) | issuers | F6 at handshake and refresh | content off-chain |
| Endorsements | on-chain (G1–G3) | endorsers | G4 at handshake | roots of trust; cached long |
| Presentation identifier `pid` | on-chain (F8) per session, or Merkle-batched per epoch | presenter | dispute; peer during handshake | the channel binding |
| Log roots | on-chain per epoch or per dispute (F3 attribute or sidechain event) | each party | auditors | optional by policy |
| Escrow token, forensic unlock | token off-chain in AUTH; unlock request on-chain (C3) | presenter; forensic authority | forensic tier | §3(d) |
| Session keys, ratchet state | off-chain, in memory only | both | both | never persisted |
| Payloads, ciphertexts | off-chain | both | both | retained per `P.logging.level` |
| Execution log entries | off-chain | both | auditors under selective disclosure | hashes only until audit |
| Session policy `P` | off-chain, signed by both | verifier | both | hash in AEAD associated data |
| Status-list epoch digests, accumulator witnesses | cached, signed by issuer | issuers | verifiers, offline | §3(c) |
| Cached DID documents, F6/F12 results | cached with `t_state` | verifiers | handshake fast path | one clock, `W_max` |

### 4.2 Cost per session, parametric

Let a session between two parties at Tier 2 involve `p ∈ {0, 1, 2}` on-chain presentations (S1 has `p = 1`), `r` revocation re-reads, `a` log-root anchors, and `m` messages. Then

```
Gas_session   = p · G_F8  +  a · G_anchor
Reads_session = 2·(F2 + F6 + G4) + F12 + r·(F6 + F12 + F2_version)   — gas-free, latency-bearing
Bytes_session = B_handshake + m · (B_header + B_payload + 16)          — 16 = AES-GCM tag
```

The only measured term is `G_F8 = 62,441` gas (O1, S1 entry 15). `G_anchor` via F3 on O1 is 44,760 gas for a 2-byte value (S1 entry 20); a 32-byte root would cost more calldata (16 gas per non-zero byte, DIGEST-LEVEL, EIP-2028/1559 family) and is a target, not a result. `B_handshake` is unmeasured until the transport exists (§7).

At fleet scale the formula is decisive without any further measurement. With `N` vehicles each opening `s` Tier 2 sessions per day and `p = 1`, the daily on-chain gas is `N · s · 62,441`. Taking the DIGEST-LEVEL figure of roughly 33 million registered vehicles in Canada and an assumed `s = 4`, the arithmetic gives about `8.2 × 10^12` gas per day — this is arithmetic on an assumption, not a measurement — which exceeds any public L1's daily gas budget by orders of magnitude (public L1 block gas limits are in the tens of millions per ~12 s block; UNVERIFIED as to the current value, not needed for the conclusion). Three consequences follow, all of them design stances in 03: per-session F8 anchoring belongs on an L2, sidechain, or Local CVIN shard [5]; at Tier 2 the default is per-epoch Merkle batching (`p_effective = 1/k` for `k` sessions per epoch, with the inclusion path carried in AUTH); and the on-chain per-session write becomes *optional*, used when a party wants a dispute-grade anchor (payment, gated access, 06) and skipped when it does not (a routine RSU report). The read path is unaffected by any of this: authentication is free of gas whatever the write policy, which is the asymmetry that makes the hybrid viable.

---

## 5. Scenario pairs on the I2I channel

Each scenario states actors, objects, the function sequence with F-tags, tier, placement, failure modes, and the problems-solved tail, followed by the test that validates it. Cross-references: latency-tier framing in 05; payment, gated access and low-connectivity variants in 06.

### 5.1 CAV: V2I charging handshake

*Actors.* Vehicle DID `V` (controller: owner wallet; OBU delegate via F11); charging station DID `CS` (operator-controlled); tariff issuer DID `T` (charging network); DMV DID `D` (issues VEHICLE_REGISTRATION); ministry endorser DID `M` (G2 endorses `D` for VEHICLE_REGISTRATION and `T` for TARIFF_ACCOUNT).

*Objects.* Credentials: VEHICLE_REGISTRATION (subject `V`, issuer `D`), TARIFF_ACCOUNT (subject `V`, issuer `T`, claims: plan, credit limit), STATION_CERT (subject `CS`, issuer `T`). Presentations: `VP_V` (registration + tariff, selectively disclosed: plan yes, plate no), `VP_CS` (station cert). Channel `cid`; policy `P` with scope `charge:session:*` and `maxValue` from the credit-limit claim; receipt (signed by both, log root anchored).

*Tier.* 2 (charging session initiation, 100–500 ms budget for the handshake; the session itself is minutes).

| Step | Action | F-tags | Placement |
|---|---|---|---|
| 1 | Station beacons `DISCOVER {CS, v(CS), endpoint}` over PC5 or Wi-Fi | — | off-chain |
| 2 | OBU sends HELLO signed with its F11 delegate key | (F12 by CS) | off-chain |
| 3 | CS resolves `V` from cache or chain; checks delegate | F2, F12 | read; cached with `t_state` |
| 4 | CS sends HELLO-ACK with `e_CS`, `v(CS)` | — | off-chain |
| 5 | OBU resolves `CS`, verifies STATION_CERT, checks `T` endorsed for STATION_CERT | F2, F6, G4 | read |
| 6 | OBU anchors `VP_V` with challenge bound to transcript (per-session, because a receipt will depend on it) | F8 | on-chain (or L2) |
| 7 | AUTH: `VP_V` under `k_hs`; CS verifies both credentials and endorsements | F6 ×2, G4 ×2 | read |
| 8 | AUTH-ACK: `VP_CS`, `P` with `maxValue`; session keys derived | — | off-chain, signed |
| 9 | Charging messages (start, meter readings, stop) under AEAD; ratchet every 60 s | — | off-chain |
| 10 | Every `I = 60` s CS re-reads V's tariff credential status | F6 | read |
| 11 | Stop: both sign receipt; log root exchanged; CS anchors root (dispute-grade) | F3 | on-chain per session |
| 12 | Settlement off-channel (06 payment scenario) references `pid_V` and root | — | Tier 3 |

*Failure modes.* Tariff credential revoked mid-charge (F7): CS observes at next `I`, sends `CLOSE(revoked)`, charging stops; energy delivered in the last `≤ I` seconds is the exposure, and the receipt covers it. OBU delegate expired (F11 validity elapsed): F12 false at refresh; `CLOSE(keyRemoved)`; the vehicle must re-provision (Tier 3). Chain unreachable at the station: §3(c) offline policy, `maxValue` reduced to the station's offline float, root anchored on reconnection. Station cert unendorsed (G4 false): the OBU refuses; a rogue station cannot open a channel. Reorg removes `pid_V`: provisional policy until re-anchor; charging continues at reduced `maxValue`.

*Problems solved / further functionality.* The same channel is the toll-authorisation channel (06) with the tariff credential replaced by a toll account and the receipt becoming the toll record; it is the pay-per-use road channel with meter readings replaced by distance attestations; the anchored receipt roots are what a reputation attestation about the station or the vehicle can cite as evidence (C1 with `evidenceURI` pointing to the root; 09).

*Test.* `scenarios/run_v2i_charge.js` on the S1 extensions: assert F8 challenge equals `H(transcript)`; assert `P.maxValue` equals the disclosed credit claim; revoke at a random step and assert `CLOSE` within `I + t_read`; assert receipt root anchored equals the locally computed Merkle root. Metrics: handshake latency under the Wi-Fi mock profile, teardown latency, gas per session (`G_F8 + G_F3`, both from trace).

### 5.2 CAV: RSU report channel

*Actors.* Vehicle pairwise DID `V'` (created by F1 under the same controller as `V`, §3(d)); RSU DID `R` (edge server, controlled by the road operator); road operator DID `O` endorses `R` for RSU_ROLE; forensic authority DID `F` holds the escrow key.

*Objects.* Credentials: VEHICLE_CLASS (subject `V`, issuer `D`, claims: class, sensor grade), presented under `V'` by ZK holdership proof (02) or, in the sandbox, by an issuer-signed pairwise re-issuance; RSU_ROLE (subject `R`). Presentations `VP_V'` with escrow token; `VP_R`. Channel policy scope `report:road:*`, `maxMsgs` high, `maxValue` 0, logging `hash-only`, anchoring per epoch of 1,000 sessions.

*Tier.* 2 for the handshake; the reports are Tier 2/3 (road and traffic conditions are not safety-critical at the sub-100 ms level).

| Step | Action | F-tags | Placement |
|---|---|---|---|
| 1 | RSU beacons `DISCOVER` | — | off-chain |
| 2 | Vehicle sends HELLO as `V'`; RSU resolves `V'` | F2 | read (cache) |
| 3 | RSU HELLO-ACK; vehicle resolves `R`, verifies RSU_ROLE, checks `O` endorsed | F2, F6, G4 | read (cache, long-lived) |
| 4 | Vehicle's presentation is a leaf under the RSU's epoch root (batched; no per-session F8) | (F8 per epoch, by RSU) | on-chain per epoch |
| 5 | AUTH with `VP_V'` + escrow token; RSU verifies class credential | F6 | read |
| 6 | Reports (hazard, congestion, surface) under AEAD | — | off-chain |
| 7 | RSU aggregates; at epoch end anchors Merkle root of all session challenges and report hashes | F8 (once), F3 (once) | on-chain per epoch |
| 8 | Forensic request (rare): `requestValidation(F, "unlock", cid)`; `F` decrypts escrow, links `V'` to `V` | C3, C4 | on-chain event |

*Failure modes.* Sybil reports from many pairwise DIDs of one controller: unlinkable by design at the RSU, so the defence is the credential (one VEHICLE_CLASS per vehicle, presented by holdership proof; the accumulator or status list prevents a revoked credential from being reused) plus the reputation layer's weighting (09). RSU compromised: its reports are only as trusted as `O`'s endorsement; G3 revocation of the endorsement makes every vehicle refuse it at their next cache refresh, which is a revocation-storm case handled by the one-clock rule. Escrow key misuse: every unlock is a C3 event; an unlock without a corresponding dispute is auditable.

*Problems solved / further functionality.* This is the road and traffic reporting channel of the brief's checklist and the ingestion path for the federated learning and cooperative perception cases of 09: the epoch roots are what let a model-training round prove that its inputs came from credentialed vehicles without learning which vehicles. The pay-per-use variant adds a distance claim and turns the report into a billing record under the verinym.

*Test.* `scenarios/run_rsu_report.js`: `k = 20` pairwise DIDs, one epoch, assert one F8 and one F3 per epoch regardless of `k` (gas per session = measured F8 + F3 divided by `k`); assert the escrow unlock links all `k` and emits `k` C3 events; assert that no two `cid`s can be linked from on-chain data alone.

### 5.3 Agent: agent-to-agent negotiation

*Actors.* Buyer agent DID `BA` (delegate of principal DID `PB` via F11, `sigAuth`, validity 24 h); seller agent DID `SA` (delegate of `PS`); marketplace registry DID `MK` (ERC-8004 identity registry [19]; G2 endorses agent operators for AGENT_MANDATE); reputation registry (Set C).

*Objects.* Credentials: AGENT_MANDATE (subject `BA`, issuer `PB`, claims: budget ceiling, categories, expiry; issuer `PB` endorsed by `MK`); AGENT_MANDATE for `SA`; OPERATOR_KYB for both principals (Tier 3, not disclosed on-channel beyond a holdership proof). Presentations `VP_BA`, `VP_SA`. Policy `P` scopes: `negotiate:offer`, `negotiate:accept` with `maxValue = min(budget claims)`. Execution logs on both sides, Merkle-anchored per session (dispute-grade, because money follows).

*Tier.* 3 (administrative latencies; the constraint is bytes and auditability, not milliseconds).

| Step | Action | F-tags | Placement |
|---|---|---|---|
| 1 | `BA` reads `SA`'s endpoint from the registry; resolves `SA` | F2 | read |
| 2 | HELLO/HELLO-ACK over HTTPS or DIDComm; each checks the other is a valid delegate of its principal | F12 ×2 | read |
| 3 | Each checks the other's reputation as a gating input | C2 ×2 | read |
| 4 | Each anchors its presentation per session | F8 ×2 | on-chain (L2) |
| 5 | AUTH/AUTH-ACK: mandates verified; issuers' endorsement checked; `P` computed as intersection of the two mandates | F6 ×2, G4 ×2 | read |
| 6 | Offers and counter-offers under AEAD; each logged; injected "instructions" in offer text have no effect on `P` | — | off-chain |
| 7 | Accept: both sign the agreement hash; log roots exchanged and anchored | F3 ×2 | on-chain |
| 8 | Post-session: principals attest each other's agent | C1 ×2 | on-chain |
| 9 | Dispute (rare): `requestValidation` with the agreement hash and log root; validator opens leaves under selective disclosure | C3, C4 | on-chain event; off-chain audit |

*Failure modes.* Principal revokes the mandate mid-negotiation (F7): the counterpart observes within `W_max`; any acceptance after the revocation block is unenforceable, and the anchored log root plus the F7 event timestamp settles which side of the line it fell. Delegate validity expires: F12 false; `CLOSE(keyRemoved)`. Confused deputy: `BA` also holds a delegation from a second principal; `P` is computed only from the mandate presented on *this* channel, so the second principal's budget is never in scope. Reputation manipulation: C1 attestations are from principals, weighted by issuer quality (09); the channel itself does not depend on reputation for authentication, only for admission policy.

*Problems solved / further functionality.* The agreement hash and roots are the input to the payment scenario (06); the reputation attestations feed 09; the same channel with `SA` replaced by a data provider is the federated learning coordinator channel where mandates specify data categories and the log proves what was contributed.

*Test.* `scenarios/run_a2a_negotiate.js` (the sandbox's deferred S6 made concrete): assert `P.maxValue = min(budgets)`; inject a scope-widening string and assert `P` unchanged; revoke mid-session and assert no post-revocation acceptance is signed; verify a leaf against the anchored root. Gas: `2·G_F8 + 2·G_F3 + 2·G_C1`; the C1 cost is unmeasured until O7 or the Set C adapter on O1 is traced.

### 5.4 Agent: agent-to-tool session

*Actors.* Agent DID `AG` (delegate of principal `PA`); tool service DID `TL` (a database, a payment API, or another agent's tool interface exposed over MCP [NEW-8]); tool operator DID `OT` (G2 endorses `PA` for TOOL_ACCESS on this tool); auditor DID `AU`.

*Objects.* Credential TOOL_ACCESS (subject `AG`, issuer `PA`, claims: tool names, argument constraints, rate limit, value limit, expiry); TOOL_CERT (subject `TL`, issuer `OT`). Policy `P` scopes are the tool names with constraints. Execution log per call; Merkle root per 100 calls or 10 minutes; anchored per epoch.

*Tier.* 3 for the handshake; per-call latency budgets are application-defined and the identity layer adds no chain read per call.

| Step | Action | F-tags | Placement |
|---|---|---|---|
| 1 | Handshake as §2.3; `TL` checks `AG` is a valid delegate; `AG` checks `TL`'s cert and `OT`'s endorsement | F2 ×2, F12, F6, G4 | read |
| 2 | `AG` anchors presentation (per session; tool sessions are long) | F8 | on-chain |
| 3 | `TL` verifies TOOL_ACCESS and its issuer's endorsement; builds `P` | F6, G4 | read |
| 4 | Tool calls under AEAD; each checked against `P` locally; each logged | — | off-chain |
| 5 | Every `I` seconds `TL` re-reads TOOL_ACCESS status and `AG`'s delegate validity | F6, F12 | read |
| 6 | Epoch: log root signed by both; `TL` anchors | F3 | on-chain per epoch |
| 7 | Audit: `AU` requests leaves for a call range; `TL` discloses those leaves with inclusion paths | — | off-chain, selective |

*Failure modes.* Principal revokes TOOL_ACCESS (F7): calls stop within `W_max`; the number of calls executed after revocation is bounded by `⌈W_max / call_interval⌉` and is measured. Agent attempts a call outside `P` (a hijacked agent following injected instructions): dropped and logged; the log leaf is evidence for the principal. Tool cert revoked or endorsement withdrawn (F7 or G3): `AG` refuses at its next refresh, so a compromised tool cannot keep receiving calls from well-behaved agents. Chain unreachable at `TL`: offline policy narrows `P` to read-only tools until reconnection.

*Problems solved / further functionality.* This is the tool-call authorisation crux of §3(h) made concrete, and it is the pattern by which the identity system extends to any back-end service (07): the tool is a legacy system behind a DID-holding adapter, and the channel's `P` is the bridge between credential scopes and the legacy access-control model.

*Test.* `scenarios/run_a2t_session.js`: 200 calls with `call_interval = 100 ms` and `I = 1 s`; revoke at call 100; assert post-revocation calls `≤ 10`; assert one out-of-scope call is dropped; anchor root and verify one leaf. Metrics: calls after revocation, bytes per call, gas per session (`G_F8 + G_F3` per epoch).

---

## 6. Relation to existing protocols

The claim is that the I2I channel reuses the cryptographic core of established protocols and contributes two things they lack: the challenge-bound presentation as a channel binding to *public registry* state, and the revocation-synchronised cache rule.

*DIDComm v2* [NEW-6] (DIGEST-LEVEL; DIF specification, not read at source) provides DID-keyed envelopes (ECDH-1PU and ECDH-ES with HPKE-like key wrapping, RFC 9180 family, DIGEST-LEVEL), message threading, and transport agnosticism. The I2I handshake can be *carried* in DIDComm envelopes for agents, and the key-agreement verification methods of §2.4 are exactly DIDComm's `keyAgreement` entries. What DIDComm does not provide is credential-conditioned session policy, revocation-synchronised liveness, or an on-chain binding; it delivers messages between DIDs and leaves trust decisions to the application. Reuse: envelopes, key types, threading. Contribution: §2.5, §2.7, §3(a).

*TLS 1.3 with DID-bound certificates* (RFC 8446, DIGEST-LEVEL) gives a mature handshake, forward secrecy, and channel binding via exporters (RFC 9266). A DID-bound certificate profile (the certificate's subject alternative name carries the DID and its key matches a verification method) makes TLS usable as the transport layer for agents over Uu/HTTP. What TLS lacks is a revocation model tied to a registry (OCSP/CRL are issuer services with their own staleness windows and no on-chain anchor) and any notion of presenting *credentials* rather than a single certificate. Reuse: the handshake as a transport for agents. Contribution: the presentation replaces the certificate as the trust object, and the binding is to the registry.

*Noise Protocol Framework* (DIGEST-LEVEL) supplies the XX pattern and the chaining-key discipline used in §2.4. The I2I key schedule is Noise XX with static keys drawn from DID documents, which is precisely how WireGuard and others specialise Noise. Reuse: the key schedule wholesale. Contribution: the static keys are versioned registry entries, and the version enters the transcript.

*IEEE 1609.2 secured messages* [28] and the SCMS [6] provide Tier 1 authentication with pseudonym certificates and are out of the I2I channel's scope by the thesis's own framing. The I2I channel's relation to them is the escrow token of §3(d): SCMS achieves pseudonymity by certificate rotation and accountability by misbehaviour reporting with linkage authorities; the I2I channel achieves pseudonymity by pairwise DIDs and accountability by escrowed linkability whose use is an on-chain event. The two can coexist on the same vehicle: 1609.2 secures the BSM stream; the I2I channel secures Tier 2 sessions; the vehicle's public DID anchors the key history that answers the accountability question the SCMS cannot [6].

*A2A and MCP transports* [NEW-7], [NEW-8] (DIGEST-LEVEL) define agent discovery (agent cards), task lifecycles, and tool schemas over HTTP/JSON-RPC. They are the payload layer of §5.3 and §5.4: an A2A task or an MCP tool call is a message under `P`. Neither defines an identity or revocation model beyond bearer tokens; the I2I channel supplies one, and the ERC-8004 registries [19] supply discovery and reputation. Reuse: message schemas, discovery cards. Contribution: credential-derived `P` as the authorisation model, and the execution log as the accountability primitive.

The two contributions, stated once. First, *channel binding to on-chain state*: the F8 challenge is derived from the handshake transcript, F8's replay prevention makes the anchor unique per channel, and the anchor is public, so a channel's existence and its authenticated parties are verifiable by third parties after the fact without any disclosure of content. No transport-layer protocol offers this because none has a public registry to bind to. Second, *the revocation-synchronised cache rule*: one clock `t_state` per verifier, one policy parameter `W_max` per credential type, cache validity defined as `now − t_state ≤ W_max`, and channel liveness conditioned on cache validity. This turns "how fast does revocation propagate" from an implementation property into a declared, per-type security parameter with a measurable teardown bound, which is the answer Memo A asked for.

---

## 7. Demonstration plan

The plan extends S1 in place, one step at a time, so that each step produces a new trace file and no committed trace is altered. The order is chosen so that every step is testable in the sandbox without hardware, with hardware-only claims isolated at the end.

| Step | Extension | New trace assertions | Metric produced |
|---|---|---|---|
| 1 | Mock transport: in-process message queue with `(MTU, loss, delay, reorder)` parameters; HELLO/HELLO-ACK/AUTH/AUTH-ACK as real messages | four `offchain` entries with `phase: handshake-<n>`; `bytes` field per message | bytes on the wire per handshake |
| 2 | Key agreement from F9: entry 8's placeholder replaced by the real X25519 or P-256 public key; ECDH uses the resolved key; ephemeral mixed per §2.4 | `offchain` entry names the `keyId` used; a run with the wrong key fails the transcript check | correctness only |
| 3 | Challenge = `H(transcript)`; AUTH encrypted under `k_hs`; both sides anchor (F8 ×2) | F8 challenge in trace equals recomputed value; second F8 with the same challenge reverts | gas per session (`2·G_F8`) |
| 4 | Forward-secrecy ratchet: symmetric per message, DH every `R` | `offchain` entries per ratchet; a post-session key-dump test cannot decrypt earlier messages | messages per DH ratchet |
| 5 | Revocation propagation timing: F7 at a random step; verifier polls at `I`; `CLOSE` emitted; `ts` of F7 tx and of `CLOSE` recorded | `ts_close − ts_revoke ≤ I + t_read + t_delay` | teardown latency after revocation, distribution over runs |
| 6 | Push notice: `REVOKE-NOTICE` on the mock transport | teardown latency with push < without | improvement ratio |
| 7 | Offline mode: mock provider returns unreachable after block `b`; pre-fetched state and leases | handshake succeeds with narrowed `P`; state-changing message refused; F3 anchor emitted on reconnection | count of deferred anchors |
| 8 | Reorg: Hardhat snapshot/revert around F8 | missing `PresentationCreated` detected; re-handshake | re-handshake count |
| 9 | Session policy and agent tests: delegation chain depth 3; injected text; tool-call revocation | `P` equals intersection; `P` unchanged after injection; post-revocation calls `≤ ⌈W_max / call_interval⌉` | calls after revocation |
| 10 | Group channel: `n = 5`, leader-keyed; one revocation | rekey excludes revoked member | messages per join/removal vs `n` |
| 11 | Scenario scripts §5.1–5.4 on top of 1–10 | as listed per scenario | per-scenario gas, latency, bytes |

Trace schema additions (versioned per the sandbox rule): `bytes` (int, for `offchain` message entries), `phase` values `handshake-1..4`, `interaction`, `ratchet`, `close`, `notice`; and a `latencyMs` field computed from `ts` pairs in `summary` entries. These are additive and do not break the explorer contract.

Metrics, and where each comes from: *handshake latency* from `ts` of HELLO to `ts` of AUTH-ACK under each mock profile (sandbox; hardware for real PC5/Uu); *teardown latency after revocation* from step 5 (sandbox; the network component from hardware); *bytes on the wire* from step 1 (sandbox is exact for the identity layer; transport headers from hardware); *on-chain gas per session* from steps 3 and 11 (sandbox is exact for O1; other options when ported).

What only hardware can show: real PC5 and Uu latencies and loss; whether the handshake fits the 500 ms Tier 2 budget on an actual OBU with an HSM-backed key; the power and compute cost of the ratchet on OBU-class hardware; RSU-as-edge chain-read latency; and any claim about the link-layer identifier persistence that §3(d)'s unlinkability depends on. None of these is required for the thesis's structural claims, all of which are about ordering, binding, and bounds that the sandbox can establish; they are required before any claim about *fitness for deployment*, and Chapter 5's limitations must say so.

---

## 8. Sources used in this document

| Ref | Source | Verification state | How used |
|---|---|---|---|
| S1 trace | `5_minimal-ssi-sandbox/traces/i2i_O1_ERC1056_1780620182135.jsonl` (22 entries) | VERIFIED AT SOURCE | all gas figures; entry ordering; byte sizes; `ts` fields (§1, §4, §7) |
| S1 script | `5_minimal-ssi-sandbox/scenarios/run_i2i.js` | VERIFIED AT SOURCE | procedure; key types; challenge construction; ECDH/AEAD parameters |
| Architecture | `5_minimal-ssi-sandbox/docs/ARCHITECTURE.md` v1.1 | VERIFIED AT SOURCE | scenario catalog (S1–S6), Set A/B/C, verified state, gas targets |
| Trace schema | `5_minimal-ssi-sandbox/traces/SCHEMA.md` | VERIFIED AT SOURCE | field list; schema additions in §7 |
| Campaign brief | `_CONTEXT_BRIEF.md` | VERIFIED AT SOURCE | spec, memos' A2A phases and cache rule, tiers, rules |
| [5] | Prakash, Michelson, Feng, CVIN, IEEE VTC2020-Spring | VERIFIED AT SOURCE (programme's own paper) | tiers; dual identity modes; RSU as edge; Local CVINs |
| [6] | Brecht et al., SCMS, IEEE T-ITS 2018 | DIGEST-LEVEL | pseudonymity and accountability gap (§3(d), §6) |
| [8] | W3C DID Core 1.0 | DIGEST-LEVEL | verification methods, key agreement entries |
| [9] | W3C VC Data Model 1.1 | DIGEST-LEVEL | presentations, challenge/domain |
| [11] | Rodriguez Garzon et al., AI agents with DIDs and VCs, 2026 | DIGEST-LEVEL | agent generalisation (§3(h), §5.3–5.4) |
| [19] | De Rossi et al., ERC-8004 | DIGEST-LEVEL | agent discovery and reputation registries |
| [23] | ERC-1056 | DIGEST-LEVEL | `changed` pointer as document version (§3(b)) |
| [27] | MOBI VID I–II | DIGEST-LEVEL | verinym for Tier 3 channels |
| [28] | IEEE 1609.2-2022 | DIGEST-LEVEL | Tier 1 secured messages out of scope; coexistence (§6) |
| NEW-1 | W3C Bitstring Status List v1.0 | DIGEST-LEVEL | epoch digests for revocation (§3(a), §3(c)) |
| NEW-2 | Noise Protocol Framework (Perrin) | DIGEST-LEVEL | XX pattern and key schedule (§2.4, §6) |
| NEW-3 | RFC 8446 TLS 1.3; RFC 9266 channel bindings for TLS 1.3 | DIGEST-LEVEL | channel-binding analogy (§2.5, §6) |
| NEW-4 | Signal Double Ratchet specification | DIGEST-LEVEL | symmetric and DH ratchet (§2.6) |
| NEW-5 | RFC 9420 Messaging Layer Security | DIGEST-LEVEL | tree-based group keys for swarms (§3(f)) |
| NEW-6 | DIF DIDComm Messaging v2 | DIGEST-LEVEL | envelopes, key agreement types (§6) |
| NEW-7 | Google A2A protocol | DIGEST-LEVEL | agent discovery cards, task lifecycle (§6) |
| NEW-8 | Anthropic Model Context Protocol | DIGEST-LEVEL | tool schemas as payload (§5.4, §6) |
| NEW-9 | RFC 9180 HPKE | DIGEST-LEVEL | escrow token encryption; DIDComm ECDH-ES basis (§3(d)) |
| NEW-10 | Hardy, 'The Confused Deputy', 1988 | DIGEST-LEVEL | delegation-chain crux (§3(h)) |
| NEW-11 | 3GPP TS 23.287 / PC5 latency studies | UNVERIFIED (not read at source) | transport budgets (§3(e)), stated as targets only |
| NEW-12 | Ethereum calldata pricing (EIP-2028/EIP-1559 lineage); L1 block gas limit | DIGEST-LEVEL (calldata) / UNVERIFIED (current block limit) | §4.2 cost formula; the block-limit value is not relied on |
| DIGEST | Canada ≈33 M registered vehicles | DIGEST-LEVEL (brief §5) | illustrative arithmetic only (§4.2) |

---

## 9. Registry delta rows

| Content Block | T | Source | Ch. | Ready % | Notes |
|---|---|---|---|---|---|
| S1 trace reading: proves/does-not-prove table | A | 08 §1 | 4 | 90 | Direct from trace; carries the seven declared gaps |
| I2I protocol specification: four-message handshake with signed/encrypted/anchored matrix | A+B | 08 §2.3 | 5 §5.2 | 75 | Design; validated by §7 steps 1–3 |
| Key agreement from F9 verification methods with F11 delegate pattern (option (i)) | A | 08 §2.4 | 5 §5.2 | 70 | Interface-preserving; needs §7 step 2 |
| Challenge-bound presentation as channel binding to on-chain state | A | 08 §2.5, §6 | 5 §5.1–5.2 | 80 | The thesis contribution; S1 partially demonstrates |
| Session policy as credential-derived object; scope intersection rule | A | 08 §2.7, §3(h) | 5 §5.2 | 65 | Needs policy table in `lib/vid/` (10) |
| Revocation-synchronised cache rule: one clock, `W_max` per type | A | 08 §3(a) | 4, 5 | 80 | Memo A rule made operational; test defined |
| Versioned-document downgrade defence | A | 08 §3(b) | 4 | 70 | Uses ERC-1056 `changed` semantics |
| Offline policy class with pre-fetched state and leases; irreducible issuer-compromise exposure | A | 08 §3(c) | 4, 5 | 65 | Pairs with 03 degraded modes and 06 low-connectivity |
| Dual-mode channel with escrowed linkability and C3-audited unlock | A | 08 §3(d) | 5 | 60 | Depends on 02 cryptosuite choice |
| Transport assumptions list (must/must-not) | B | 08 §3(e) | 4 | 75 | Hardware-dependent budgets flagged |
| Group channel stances: leader-keyed vs MLS-style | A | 08 §3(f) | 5 | 55 | Sandbox test defined; no build yet |
| Chain-fault behaviour: observed vs final, provisional policy | A | 08 §3(g) | 4 | 65 | Hardhat snapshot test defined |
| Agent cruxes: confused deputy, injection-resistant policy, tool authorisation, anchored execution log | A | 08 §3(h) | 5 §5.2 | 70 | Core of C14 argument |
| Channel data-placement table | B | 08 §4.1 | 4 | 85 | Consistent with 01/03 |
| Per-session cost formula with measured `G_F8`, `G_F3` | B | 08 §4.2 | 4 | 80 | Only measured terms from trace; fleet arithmetic labelled |
| Scenario: V2I charging handshake | A+B | 08 §5.1 | 4 | 70 | Step table; test named |
| Scenario: RSU report channel with epoch batching and escrow | A+B | 08 §5.2 | 4, 5 | 65 | Feeds 09 |
| Scenario: agent-to-agent negotiation (S6 made concrete) | A+B | 08 §5.3 | 5 | 65 | Set C gas unmeasured |
| Scenario: agent-to-tool session | A+B | 08 §5.4 | 5 | 65 | Bridge to 07 legacy adapters |
| Protocol relation matrix: DIDComm/TLS/Noise/1609.2/A2A-MCP reuse vs contribution | A+B | 08 §6 | 5 §5.2, 3 | 75 | Two contributions isolated |
| S1 extension plan (11 steps) with trace assertions and metrics | B | 08 §7 | 4 | 80 | Executable work order for 10 |

---

## 10. Open questions for the researcher

1. *Per-type `W_max` values.* The design makes the staleness window a per-credential-type policy parameter and refuses to choose numbers. The thesis needs at least three declared values (a safety-adjacent Tier 2 type, a commercial Tier 2 type, a Tier 3 type) to run the §7 step 5 measurement against. Only the researcher can set these, because they encode a risk posture, not a technical fact.

2. *Per-session versus per-epoch anchoring as the default.* §4.2 shows per-session F8 is infeasible on a public L1 at fleet scale and proposes epoch batching as the Tier 2 default with per-session anchoring reserved for dispute-grade sessions. This changes what S1 demonstrates (S1 is per-session). Should the canonical S1 be re-specified as per-epoch, or should the thesis present both as two profiles of the same channel?

3. *Delegate key agreement without touching the interface.* §2.4 chooses option (i) (controller registers the OBU's key-agreement key via F9; the F12-valid delegate proves the right to use it). The alternative is to propose a `keyAgreement` delegate type for spec v1.1, which would be cleaner but is an interface change and therefore belongs in the erratum list with `CredentialRevokedEvent`. Which does the thesis argue for?

4. *Escrowed linkability governance.* §3(d) puts the forensic escrow key under an endorser-set decision and makes every unlock a C3 event. Whether this is acceptable to the SCMS community, and whether it should be framed as extending the SCMS linkage authority or replacing it for Tier 2, is an argument the researcher must make in Chapter 5 against [6] and [28]; it also determines whether Set C is optional or required in the CAV profile.

5. *Acting on observed versus final revocation.* §3(g) prefers false teardowns to unauthorised traffic. On a QBFT Besu deployment (E1 substrate) the distinction is one block and the question is moot; on a public L2 with probabilistic finality it is not. Does the thesis commit to deterministic-finality substrates for the CAV profile, which would simplify Chapter 4 but narrow the standards inventory?

6. *What the trace schema may grow.* §7 proposes additive fields (`bytes`, new `phase` values, `latencyMs`). The sandbox rule is that schema changes are versioned; the researcher must decide whether the explorer contract is bumped to v2 for this campaign or the additions wait for the angle pass on I2I.
