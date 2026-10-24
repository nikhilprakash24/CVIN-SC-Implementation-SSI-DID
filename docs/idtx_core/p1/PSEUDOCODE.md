# WP 1.4 — Pseudocode Listings

**Home:** Appendix G-D · **Produced:** 2026-10-24 (WP 1.4) · verify each listing line-by-line against the cited `file:line` range.

Conventions. UPPERCASE names (`EMIT`, `RECOVER`, `HASH`, `NOW`, `REVERT`) are primitive operations. `require(cond, msg)` means "revert the whole transaction with `msg` unless `cond` holds" (revert-on-false; state changes in the transaction are discarded). `LOAD x` and `STORE x ← v` denote SLOAD / SSTORE-level reads and writes of persistent contract state; a plain `let` is a memory-only local. `identity` is always an address that is a DID by construction. Where a lifecycle capability is realised as an *adapter pattern over a generic write primitive* (no dedicated Solidity symbol — see WP 1.1 FUNCTION_MAP §method note), the listing says so and cites the primitive it abstracts. Generic lifecycle listings are grounded in the ERC-1056 registry (`EthereumDIDRegistry.sol`) and the thesis hybrid (`CVINCombinedIdentity.sol`) as the two representative substrates. The home of this appendix is Appendix G-D.

Path keys: `DIDReg` = `1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol`; `CVIN` = `1_blockchain-identity/contracts/CVINCombined/CVINCombinedIdentity.sol`; `IDTx` = `phase2/idtx/contracts/IdtxExecutor.sol`; `ZkGate` = `5_zkp-agent-identity/contracts/ZkVinGate.sol`.

---

## 2. Generic identity lifecycle (ERC-1056 + CVIN-Combined substrates)

### 2.1 createDID — implicit creation

`DIDReg:105–111` (identityOwner default) · `CVIN:164–170` (same pattern)

```
# No create transaction exists. Every address IS a DID.
# "Creation" is the first state-changing op that sets an owner override;
# until then the identity is self-owned.
function identityOwner(identity) -> address:          # view
    let owner = LOAD owners[identity]
    if owner != address(0):
        return owner
    return identity                                   # self-owned by default
```
Note: identity creation is zero-cost / implicit — there is no `createDID` symbol; the DID exists the moment an address exists, which is why WP 1.1 lists ERC-1056 createDID as "implicit".

### 2.2 resolve — owner (R1) and document (R3)

`DIDReg:105–111` (R1 owner) · R3 document rebuilt off `changed`/`previousChange` event chain (`DIDReg:30–66, 74`)

```
# R1 (owner): on-chain, O(1).
function resolveOwner(identity) -> address:           # view
    return identityOwner(identity)

# R3 (DID document): NOT an on-chain call. An off-chain resolver reads
# changed[identity] (last-change block), then walks the event log backward
# via each event's previousChange field to block 0, replaying
# DIDOwnerChanged / DIDDelegateChanged / DIDAttributeChanged into a document.
function resolveDocument(identity):                   # off-chain
    let blk = LOAD changed[identity]
    collect events at blk, follow previousChange ... until 0
    fold events -> DID document
```
Note: attribute *values* are in events only; no contract can read them on-chain (the AR-1 limitation — see IDTx §4). R3 is therefore an off-chain log replay, not an EVM read.

### 2.3 changeOwner (U1 / controller rotation)

`DIDReg:136–143` · `CVIN:173–180`

```
function changeOwner(identity, newOwner):
    require(msg.sender == identityOwner(identity), "unauthorized")
    STORE owners[identity] ← newOwner
    EMIT DIDOwnerChanged(identity, newOwner, LOAD changed[identity])
    STORE changed[identity] ← CURRENT_BLOCK_NUMBER
```
Note: `previousChange` carried in the event is the *old* `changed` value, forming the backward-linked event chain that 2.2 walks. ERC-1056 also offers `changeOwnerSigned` (`DIDReg:153–179`) — same effect via an ecrecover'd meta-tx with a per-owner nonce.

### 2.4 addDelegate / revokeDelegate / validDelegate (U2 / R4 / D1)

`DIDReg:190–206` add · `256–270` revoke · `120–127` validDelegate · (CVIN `185–215`)

```
function addDelegate(identity, delegateType, delegate, validity):
    require(msg.sender == identityOwner(identity), "unauthorized")
    let validTo = NOW + validity
    STORE delegates[identity][delegateType][delegate] ← validTo
    EMIT DIDDelegateChanged(identity, delegateType, delegate, validTo, changed[identity])
    STORE changed[identity] ← CURRENT_BLOCK_NUMBER

function revokeDelegate(identity, delegateType, delegate):
    require(msg.sender == identityOwner(identity), "unauthorized")
    STORE delegates[identity][delegateType][delegate] ← 0      # CVIN:203 stores NOW, not 0
    EMIT DIDDelegateChanged(identity, delegateType, delegate, 0, changed[identity])
    STORE changed[identity] ← CURRENT_BLOCK_NUMBER

function validDelegate(identity, delegateType, delegate) -> bool:   # view
    return LOAD delegates[identity][delegateType][delegate] > NOW
```
Note: delegate validity is a stored expiry timestamp, so `validDelegate` IS an on-chain read (unlike attributes) — this is why IDTx accepts Delegate as a dependency kind. CVIN's revoke writes `block.timestamp` rather than `0` (`CVIN:203`); both make `validDelegate` false immediately.

### 2.5 setAttribute / revokeAttribute (U3 / D2)

`DIDReg:314–323` set · `367–374` revoke · (CVIN `224–242`)

```
function setAttribute(identity, name, value, validity):
    require(msg.sender == identityOwner(identity), "unauthorized")
    let validTo = NOW + validity
    EMIT DIDAttributeChanged(identity, name, value, validTo, changed[identity])
    STORE changed[identity] ← CURRENT_BLOCK_NUMBER        # only the pointer is stored

function revokeAttribute(identity, name, value):
    require(msg.sender == identityOwner(identity), "unauthorized")
    EMIT DIDAttributeChanged(identity, name, value, 0, changed[identity])   # validTo = 0
    STORE changed[identity] ← CURRENT_BLOCK_NUMBER
```
Note: no attribute storage write occurs — only the event and the `changed` pointer. Hence there is no getter returning an attribute value (AR-1); verification of an attribute requires off-chain log replay or a proof carried by the transaction.

### 2.6 issueCredential — on-chain claim anchor (V1 + V3)

`CVIN:254–298` addClaim

```
function addClaim(identity, topic, scheme, issuer, signature, data, uri) -> claimId:
    require(msg.sender == identityOwner(identity), "unauthorized")     # owner anchors
    require(scheme == SCHEME_ECDSA, "unsupported scheme")
    require(issuer != address(0), "zero issuer")
    let digest = HASH(address(this), identity, topic, data)            # raw keccak, no EIP-191
    require(RECOVER(digest, signature) == issuer, "invalid claim signature")
    require(not LOAD revokedClaims[HASH(issuer, digest)], "claim revoked by issuer")
    claimId = HASH(issuer, topic)
    if LOAD _claims[identity][claimId].issuer == address(0):
        STORE _claimIdsByTopic[identity][topic].push(claimId)         # index on first insert
    STORE _claims[identity][claimId] ← Claim(topic, scheme, issuer, signature, data, uri)
    EMIT ClaimAdded(...);  EMIT DIDClaimChanged(identity, claimId, topic, false, changed[identity])
```
Note: the issuer signature is verified ONCE here (at add time); `changed[identity]` is deliberately NOT advanced (K-6) so the DID-document walk in 2.2 never lands on a claim-only block. `claimId = HASH(issuer, topic)` means re-adding the same (issuer, topic) overwrites in place. No nonce/expiry in the signed payload, so an older never-revoked claim can be re-anchored (documented limitation, `CVIN:46–49`).

### 2.7 verifyCredential — hasValidClaim (V6)

`CVIN:395–406`

```
function hasValidClaim(identity, topic, issuer) -> bool:     # view, O(1)
    if issuer == address(0):
        return false                                         # empty slot is never valid (K-11)
    let claimId = HASH(issuer, topic)
    let claim = LOAD _claims[identity][claimId]
    return claim.issuer == issuer AND claim.topic == topic
```
Note: this is a pure on-chain existence check — it does not re-verify the signature (that was done at add time, 2.6) and does not check any expiry (none is stored). Freshness/semantic validity beyond existence is an off-chain VC-layer concern.

### 2.8 revokeCredential (V5)

`CVIN:303–323` removeClaim · `336–344` revokeClaimContent

```
function removeClaim(identity, claimId):
    let claim = LOAD _claims[identity][claimId]
    require(claim.issuer != address(0), "claim not found")
    require(msg.sender == identityOwner(identity) OR msg.sender == claim.issuer, "unauthorized")
    if msg.sender == claim.issuer:                           # issuer removal is STICKY
        STORE revokedClaims[HASH(claim.issuer,
                 HASH(address(this), identity, claim.topic, claim.data))] ← true
    deleteClaim(identity, claimId, claim.topic, claim.issuer)   # swap-pop index, delete, EMIT

function revokeClaimContent(identity, topic, data):          # issuer, even if not anchored
    STORE revokedClaims[HASH(msg.sender, claimDigest(identity, topic, data))] ← true
    let claimId = HASH(msg.sender, topic)
    if anchored AND keccak(stored.data) == keccak(data):  deleteClaim(...)
```
Note: an *owner* removal records nothing and is reversible by re-anchoring; an *issuer* removal (and `revokeClaimContent`) writes `revokedClaims` so `addClaim`'s require at 2.6 blocks the content permanently. `revokeClaimContent` needs no access control — it can only ever block content signed by `msg.sender` itself.

### 2.9 createPresentation — replay-protected anchor (F8 / P1)

Adapter pattern (no ERC-native symbol) over `DIDReg:314–323` setAttribute (adapter `A/erc1056.adapter.js:196`, per WP 1.1 §createPresentation)

```
# Holder anchors a hash of the presentation as a SHORT-LIVED attribute.
function createPresentation(identity, presHash):
    let key = PRESENTATION_KEY
    setAttribute(identity, key, presHash, 300)      # 300s TTL (confirmed: erc1056.adapter.js:198)
    # -> EMIT DIDAttributeChanged(identity, key, presHash, NOW+300, changed[identity])
    # Verifier (off-chain) replays the log, checks presHash matches the VP it
    # was given AND that validTo has not passed -> bounds the replay window.
```
Note: no ERC provides a native presentation primitive; this is `setAttribute` with a short validity. Replay protection is the TTL (an anchored presentation is only acceptable within its window), enforced by the off-chain verifier reading `validTo`, not by an on-chain nonce. The identity (holder) must own the DID, since `setAttribute` is owner-gated.

### 2.10 deactivate (D3)

Adapter pattern (no ERC-1056 native primitive) over `DIDReg:314–323` setAttribute (adapter `A/erc1056.adapter.js:189`; CVIN `A/cvin.adapter.js:165`)

```
function deactivate(identity):
    # Permanent "did/deactivated" marker: a non-expiring attribute event.
    setAttribute(identity, keccak("did/deactivated"), "true", PERMANENT)
    # PERMANENT = a validity so large the attribute never expires.
    # Resolvers (2.2) that see this marker treat the DID document as deactivated.
```
Note: ERC-1056 has no native deactivate; it is an attribute convention consumed off-chain. ERC-721/LSP8 substrates instead have dedicated primitives (`deactivateVehicle` / `revokeVehicle`) — see WP 1.1 §deactivate.

---

## 3. IDTx patterns (`IdtxExecutor.sol`)

### 3.1 holds() — the identity predicate

`IDTx:121–126` holds · commitment store `IDTx:80–85` valueOf

```
# Pure function of the NAMED identity's current chain state. Does NOT read
# msg.sender (AR-4): the caller is not part of the predicate.
function holds(d: Dependency) -> bool:                # view
    if d.kind == Owner:
        return registry.identityOwner(d.identity) == d.party
    if d.kind == Delegate:
        return registry.validDelegate(d.identity, d.key, d.party)
    # Commitment kind:
    let v = commitments.valueOf(d.identity, d.key)    # IDTx:80–85
    return v != 0 AND v == d.expected

# valueOf returns the stored commitment ONLY IF still valid AND its setter
# still owns the identity (AR-6), else 0:
function valueOf(identity, key) -> bytes32:           # view
    if LOAD validUntil[identity][key] <= NOW:            return 0
    if registry.identityOwner(identity) != LOAD setBy[identity][key]: return 0
    return LOAD _value[identity][key]
```
Note: Owner and Delegate are read directly from the registry because both are stored state; the Commitment kind exists *because* ERC-1056 attribute values cannot be read on-chain (AR-1), so a salted hash / ciphertext digest is kept in a side store. The predicate proves *registered-commitment validity*, not knowledge of the opening (AR-5).

### 3.2 execute() — same-transaction IDTx

`IDTx:129–132`

```
function execute(d: Dependency, action):
    require(holds(d), "identity dependency not met")   # predicate and action are ATOMIC
    EMIT Executed(action, d.identity, d.kind, msg.sender)
```
Note: predicate and effect are in one transaction, so there is no time-of-check/time-of-use gap at all. Any caller may submit (keeper, insurer, toll) — tested at `idtx.test.js:44` (AR-4).

### 3.3 setCommitment / revokeCommitment — commitment store

`IDTx:62–71` set · `73–78` revoke (contract `IdentityCommitments`, `IDTx:44`)

```
function setCommitment(identity, key, commitment, until):
    require(registry.identityOwner(identity) == msg.sender, "not the identity owner")
    require(commitment != 0, "empty commitment")
    require(until > NOW, "already expired")
    STORE _value[identity][key]     ← commitment
    STORE validUntil[identity][key] ← until
    STORE setBy[identity][key]      ← msg.sender          # AR-6: owner at set time
    EMIT CommitmentSet(identity, key, commitment, until)

function revokeCommitment(identity, key):
    require(registry.identityOwner(identity) == msg.sender, "not the identity owner")
    DELETE _value[identity][key], validUntil[identity][key], setBy[identity][key]
    EMIT CommitmentRevoked(identity, key)
```
Note (AR-6): `setBy` captures the owner at set time; `valueOf` (3.1) later returns 0 once `identityOwner != setBy`. So a commitment set by a seller stops counting the instant the vehicle changes owner — "the setter loses ownership" behavior (tested `idtx.test.js:85`), even though the stored value is untouched.

### 3.4 createIntent() / fulfil() — next-transaction IDTx

`IDTx:135–140` createIntent · `143–151` fulfil

```
function createIntent(d: Dependency, action, deadline) -> id:
    require(deadline > NOW, "deadline passed")
    id = LOAD _intents.length
    STORE _intents.push(Intent(d, action, deadline, msg.sender, done=false))
    EMIT IntentCreated(id, action, d.identity, deadline)

function fulfil(id):                                    # any agent may call
    let it = LOAD _intents[id]
    require(not it.done, "already fulfilled")
    require(NOW <= it.deadline, "deadline passed")
    require(holds(it.dep), "identity dependency not met")   # <-- RE-CHECK at use time
    STORE it.done ← true
    EMIT IntentFulfilled(id, msg.sender);  EMIT Executed(it.action, it.dep.identity, it.dep.kind, msg.sender)
```
Note — in-execution gap CLOSED: `fulfil` re-evaluates `holds(it.dep)` against *current* state (`IDTx:147`), so an owner transfer, delegate revocation, commitment revocation, or expiry occurring between `createIntent` and `fulfil` makes fulfilment revert — there is no on-chain TOCTOU (tested `idtx.test.js:113,120,126,129`). The `it.done` flag + deadline give single-use, bounded-lifetime intents.

Note — ordering race REMAINS (AR-10): re-checking removes the *check-to-use* gap but not the *submission ordering* race. Because `fulfil` succeeds for whoever lands it in the valid window and the dependency can flip in an adjacent block/mempool position, the outcome still depends on transaction ordering (which of a state-change tx and a `fulfil` tx a proposer sequences first). The contract cannot close this; it is a property of the mempool, flagged as AR-10.  (confirmed: ANALYSIS §4.3–4.5, ACADEMIC_REVIEW_F1-F3 AR-10)

---

## 4. ZkVinGate.admit — scoped nullifier, once-per-scope, unlinkable

`ZkGate:92–114` admit · service store `ZkGate:86–90` · anchor `ZkGate:80–84`

```
# Public signal layout (ZkGate:36): [nullifier, commitment, mfrRoot, minYear, region, scope, challenge]
function admit(identity, serviceId, a, b, c, pub, action):
    let s = LOAD services[serviceId]
    require(s.active, "UnknownService")
    let anchored = LOAD commitmentOf[identity]
    require(anchored != 0 AND pub[COMMITMENT] == anchored,  "SignalMismatch(COMMITMENT)")
    require(pub[MFR_ROOT]  == LOAD mfrRoot,     "SignalMismatch(MFR_ROOT)")
    require(pub[MIN_YEAR]  == s.minModelYear,   "SignalMismatch(MIN_YEAR)")
    require(pub[REGION]    == s.region,         "SignalMismatch(REGION)")
    require(pub[SCOPE]     == s.scope,          "SignalMismatch(SCOPE)")
    require(pub[CHALLENGE] == s.challenge,      "SignalMismatch(CHALLENGE)")
    require(not LOAD nullifierUsed[s.scope][pub[NULLIFIER]], "NullifierUsed")   # once per scope
    require(verifier.verifyProof(a, b, c, pub), "InvalidProof")                 # Groth16
    STORE nullifierUsed[s.scope][pub[NULLIFIER]] ← true
    EMIT Admitted(identity, serviceId, pub[NULLIFIER], action)
```
Note: every public signal is pinned to an on-chain value before the (expensive) proof check; the nullifier is namespaced by `scope` (`nullifierUsed[scope][nullifier]`), so the same vehicle gets at most one admission per service scope but its nullifiers are unlinkable *across* scopes. The dependency here is *knowledge* of the commitment opening (VIN/year/mfr stay hidden), closing AR-5 via a proof. Which identity was admitted is public (it is a named IDTx); hiding that too needs an anonymity-set proof (not built — `ZkGate:20–22`).
