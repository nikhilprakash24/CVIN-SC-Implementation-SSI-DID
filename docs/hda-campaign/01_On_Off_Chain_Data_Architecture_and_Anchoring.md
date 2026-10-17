CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**On/Off-Chain Data Architecture and Anchoring**

**The data-placement analysis of the identity system: where every datum lives, how it is written, how it is read, how its integrity is proven later, and what each choice costs — per function and per object**

Document 2 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable (core) · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose + Type B tables-data → Chapter 4, §4.4 (new subsection "Data placement and anchoring"); hooks into Chapter 2, §2.4 and Chapter 5, §5.1*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 1. The question stated precisely

**Claim.** Every candidate identity system in the thesis inventory can be reduced, for evaluation purposes, to a single table with one row per datum and six columns: where the datum lives, who can read it, how a write to it is made durable, how its integrity is proven at some later time by some party who was not present when it was written, what the finality semantics of the write are, and what each of those choices costs and who pays. Systems that look very different at the level of standards (an EVM registry, an AnonCreds ledger, a centralised Security Credential Management System, SCMS) differ mostly in how they fill in this table. The thesis's central empirical finding — that no EVM standard natively implements createPresentation (F8), that EVM options optimise identity anchoring (Set A) and defer selective disclosure to off-chain middleware, and that AnonCreds reaches the Set B coverage ceiling by anchoring only credential definitions and revocation accumulators — is, at bottom, a statement about which rows of that table each family chooses to put on a ledger.

**Reasoning.** An identity system for connected and autonomous vehicles (CAVs) handles a small number of distinct data kinds: identifiers and their control keys; the documents that describe those keys; credentials that bind attributes to identifiers; the status of those credentials; presentations that disclose some of those attributes to a verifier under a challenge; the session keys of secure channels opened after presentation; attestations of reputation; and records of what was done. For each such datum the designer must answer the six questions above. Two of the answers are constrained by physics and law rather than by taste. Physics: a vehicle at Tier 1 (<100 ms) or Tier 2 (100–500 ms) cannot wait for a block, so anything on the Tier 2 critical path must be readable without a fresh chain write and, ideally, without a fresh chain read. Law: a credential's content, and in the strict reading even a per-credential hash of that content, may be personal data, so the question "who can read it" is not a performance question but a compliance question with a jurisdiction-dependent answer [10], [14]. The remaining answers — durability, integrity proof, finality, cost — are engineering trade-offs, and it is exactly on those trade-offs that the families of the inventory disagree.

Consider the three archetypes the thesis compares. A centralised PKI such as SCMS [6], [28] places everything in the operator's database: keys, certificates, revocation lists. Reads are fast and cheap, writes are durable to the extent the operator's backups are, integrity is proven by the operator's signature, finality is immediate, and cost is borne by the operator. What it cannot offer is a proof of history that does not depend on the operator's continued honesty — the accountability gap identified in Chapter 1. An EVM registry such as ERC-1056 [23] moves the key-material history and the credential anchors onto a replicated ledger: durability and integrity now come from consensus rather than from an operator, at the price of a write that costs gas, finalises in seconds to minutes, and is public. The LFDT/AnonCreds line [22], [25] makes a third choice: it keeps every credential and every presentation off-chain and puts on the ledger only the schema, the issuer's credential definition (the public key material), and a revocation accumulator, so that the verifier can check a zero-knowledge proof against public parameters without any per-credential datum ever having been written to the chain.

Read as a data-placement decision, the Set A/Set B decomposition (contribution C3) becomes sharp. Set A functions (F1–F4, F9–F12) manage data that *must* be on a shared, tamper-evident substrate if the system is to answer "what is the history of the keys of vehicle V" — the identifier, its controller, its verification methods, its delegates, its deactivation flag. Set B functions (F5–F8) manage data that *must not* be on that substrate in the clear — credential content, holder attributes, presentation contents — and about which the only question is what minimal residue (a hash, a root, a status bit, an accumulator value, a commitment) is anchored. The EVM families have rich native mechanics for Set A because Set A is state; they have none for Set B because Set B is not state but attestation, and the only state Set B needs is the anchor. AnonCreds has weak Set A mechanics (its DID lifecycle is a ledger adapter) and the strongest Set B mechanics because it was designed from the anchor side inward. The thesis draft's phrase that "EVM optimises identity anchoring and defers selective disclosure to off-chain middleware" is therefore a description of two placement policies, and the "best of both worlds" hybrid designed in 03 is the composition of the EVM Set A placement with the AnonCreds Set B placement, on one substrate, with an explicit rule for what crosses the boundary.

**Evidence and what would produce it.** The measured evidence available today is a single scenario trace on one option (sandbox v1.3, O1_ERC1056, scenario S1, trace `traces/i2i_O1_ERC1056_1780620182135.jsonl`, 22 entries, 12/12 functions, Hardhat local EVM, solc 0.8.24). That trace is used throughout this document as the only source of measured gas. Everything else is a target, a hypothesis, or a formula with named variables. The scenario scripts S7 (`run_vid_minimal.js`) and S8 (`run_vid_lifecycle.js`) named in the brief, §7, are the instruments that would extend the evidence to the credential families this document places; §11 states which assertions they must carry.

## 2. A data-placement taxonomy

**Claim.** There are ten places a datum can live in this system, and they are not interchangeable: each has a distinct profile of durability, availability, integrity guarantee, privacy exposure, read and write cost, finality, and payer. Design errors in identity systems are, in the author's reading of the inventory, most often placement errors — a datum in a location whose profile does not match the datum's requirements — rather than cryptographic errors.

**The ten locations.** Table 2.1 states the profile of each. Cost columns are qualitative by design; the parametric model of §7 quantifies the on-chain rows using measured gas, and the DIGEST-LEVEL EVM constants (SSTORE new slot 20,000 gas; SLOAD 2,100 cold / 100 warm under EIP-2929; calldata 16 gas per non-zero byte and 4 per zero byte; LOG data 8 gas per byte plus topic costs; EIP-4844 blobs retained on the order of eighteen days) are cited from the brief with that label [NEW-2], [NEW-3].

**Table 2.1 — Placement taxonomy**

| Location | Durability | Availability | Integrity guarantee | Privacy exposure | Read cost / latency | Write cost / latency | Finality | Who bears cost |
|---|---|---|---|---|---|---|---|---|
| L1 contract storage (SSTORE) | Permanent while chain exists; state is what full nodes must hold | Any node, any time; view calls free | Consensus; state root in every header; provable by Merkle-Patricia proof | Fully public, forever | Free via node RPC; ≈2,100 gas cold if read inside a tx; ms if local node, 100s of ms remote | Highest: ≈20,000 gas per new slot plus 21,000 base; block time to inclusion | Probabilistic (PoW) or deterministic after finality epoch (PoS / QBFT) | Writer (sender of tx) |
| Event log (LOG) | Permanent in history; not in state — full nodes may prune receipts | Requires an archive or indexed node; not readable from within a contract | Consensus; receipts root in header | Fully public | Free but O(n) over history without an index; seconds to minutes to rebuild | ≈8 gas/byte + 375/topic (DIGEST-LEVEL); far cheaper than SSTORE | Same as storage | Writer |
| Calldata | Permanent in history (block bodies) | Same as logs | Consensus; transactions root | Public | Same as logs | 16 / 4 gas per byte (DIGEST-LEVEL); the dominant L2 cost component | Same as storage | Writer |
| EIP-4844 blob | Ephemeral (≈18 days, DIGEST-LEVEL) | Only during retention window; then only from whoever archived it | KZG commitment in header; permanent commitment, ephemeral data | Public during window | Free during window | Separate blob-gas market; much cheaper than calldata per byte | Same as L1 | Writer (rollup sequencer typically) |
| L2 / sidechain state | As durable as the L2's data-availability commitment to L1 (rollup) or as its validator set (sidechain) | L2 nodes; withdrawal to L1 delayed (optimistic: days; validity: minutes to hours) | Rollup: L1-enforced (fraud or validity proof). Sidechain: its own consensus only; backbone anchoring adds a periodic checkpoint | Public on the L2 | Free view calls; typically faster block times | Execution gas × small multiplier plus amortised L1 data cost | L2 soft finality in seconds; L1-hard finality after proof/challenge window | Writer, subsidised by sequencer economics |
| Off-chain content-addressed (IPFS / Arweave) | IPFS: only while pinned. Arweave: endowment-funded permanence (DIGEST-LEVEL) | Depends on pinning / gateway | Content hash is the identifier: integrity is intrinsic, existence-at-time is not | Public to anyone with the CID; encryption is the caller's job | Network fetch, 100s of ms to seconds | Pinning fee or one-off endowment | None (no ordering) | Publisher |
| Off-chain enterprise DB | Operator's backups | Operator's uptime | Operator's signature or none; no third-party proof unless anchored | Access-controlled by operator; auditable by operator | ms | ms | Immediate, local | Operator |
| Holder wallet / edge (OBU) | Device lifetime; lost with the device unless backed up | Always to the holder; to nobody else | Issuer signature carried inside the object | Private to holder | µs–ms, offline | µs–ms, offline | Immediate, local, non-authoritative for anyone else | Holder (OEM in practice) |
| Issuer store | Issuer's backups | Issuer's uptime | Issuer's own records; authoritative for status only if not anchored | Access-controlled by issuer | ms | ms | Immediate | Issuer |
| Verifier cache | Until invalidated | Verifier's own | Copy of an anchored or signed datum; correct only within the staleness window | Verifier-local | µs | n/a (populated by a read) | Derivative | Verifier |

**Prose on the rows that matter most.** Three contrasts carry most of the design weight.

Contract storage versus event log is the ERC-1056 question. ERC-1056 is event-sourced: attributes and delegates are written as logs and the DID document is reconstructed by an indexer that replays them [23]. In the sandbox's O1 implementation the design is deliberately mixed: identity existence, controller, deactivation flag, key count, delegate expirations and the credential anchors are in storage (so that view functions F2, F6 and F12 can answer without an indexer and never revert), whereas attribute updates under F3 are pure events (`DIDAttributeChanged` plus `DIDUpdated`, two logs, 44,760 gas measured). This is why createDID measures 161,823–178,935 gas against a <100K target: the explicit-DID storage that gives the interface its uniform, indexer-free read path costs several fresh SSTORE slots. The trade is honest and measurable: F3 (event-only, 44,760 gas) is the cheapest state change in the trace after revocation, and F1 (storage-heavy) is the most expensive. It is also the first placement finding of the campaign: within one contract the same design axis — state versus log — produces a factor of roughly 3.6 between the cheapest and dearest lifecycle write (44,760 versus 161,835 gas), and the difference buys a read path that needs no indexer.

Contract storage versus off-chain content is the Set B question. F5 stores six fields per credential (issuer, subject, content hash, validUntil, revoked, exists) and measures 130,163 gas. The credential itself — the W3C-shaped JSON with the driver's name or the vehicle's VIN — is never on the chain. This single rule, "content off-chain, only the hash on-chain," is what the brief calls the shared anchor pattern and what the Building Paths preface calls hash-on-chain as integrity without disclosure. Section 3 refines it, because a per-credential content hash is the weakest form of that pattern for privacy and the most expensive for cost.

Holder wallet versus verifier cache is the Tier 2 question. If the datum the verifier needs at a toll gantry is already in the vehicle's on-board unit (OBU) as a signed credential, and the verifier's view of revocation state is cached with a known staleness window, then no chain access sits on the critical path at all. The whole hybrid design of 03 is an argument that this is safe under stated assumptions, and §4 below is where those assumptions are named.

## 3. The anchoring pattern family

**Claim.** "Put a hash on the chain" is not one design but a family of at least seven, and they differ in what is proven, what is not, what it costs, and when it fails. Choosing among them is the second-largest lever on cost after the L1/L2 decision, and the only lever on the GDPR question.

Each pattern is stated in the same form: what the anchor proves to a later verifier, what it does not prove, what it costs (in terms of the measured O1 points where a function corresponds), and the failure mode.

**3.1 Hash anchor (per object).** The issuer computes H = keccak256(canonical(object)) and writes H, together with subject, issuer and validity, into storage. This is F5 as implemented in O1: 130,163 gas measured. *Proves:* that an object with exactly this content existed and was registered by this issuer no later than the block time, and that it has not been revoked as of the read. *Does not prove:* that the object's content is true, that the holder still controls the subject DID (that is F2/F12's job), or anything about the content to a party who does not hold the pre-image. *Fails when:* canonicalisation differs between issuer and verifier (§6.3), when the pre-image is lost (the anchor becomes a permanent orphan), or, legally, when the hash is held to be personal data because the pre-image is low-entropy and enumerable — a licence number salted with nothing is a dictionary attack away from re-identification.

**3.2 Merkle root anchor (batch).** The issuer collects b objects, builds a Merkle tree over their hashes, and writes one root [NEW-4]. Each holder receives their leaf's authentication path (log2 b sibling hashes). *Proves:* the same existence-by-time claim as 3.1 for every leaf, given the path. *Does not prove:* anything per-object on-chain; there is no per-credential row to revoke, so revocation must come from a separate mechanism (3.6 or 3.5). *Costs:* one write for b objects. The write is not an F5 call — F5's signature takes one credentialHash and returns one credentialId — so a batch anchor is an extension beside the interface (spec §6 "batch ops"), and its gas is a hypothesis until measured; the EVM constants suggest a floor of one fresh SSTORE (20,000) plus base transaction (21,000) plus one event, that is, on the order of 45–70K gas per root — labelled here as a design estimate, not a result. Per object that is 45–70 gas at b = 1,000. *Fails when:* the holder loses their path (the issuer must retain the tree or the holder is unprovable), when the batching delay exceeds the tier's write-latency budget (a birth certificate can wait an hour for a batch; an accident report that a police officer must be able to cite in court can also wait, but a toll receipt disputed at the next gantry cannot), and when a batch mixes credentials of different issuers, which breaks the issuer-only revocation semantics of F7.

**3.3 Signed-then-anchored.** The issuer signs the credential (EIP-191 over canonical JSON in the repository's VC layer, or a W3C Data Integrity proof [NEW-6]); the signature is the proof of issuance; the chain anchors only existence and time, and optionally status. *Proves:* the signature proves authorship and integrity anywhere, offline, forever; the anchor proves existence-at-time and current status. *Does not prove:* that the issuer was authorised to issue this type at that time — that is what the endorsement registry (G1–G4) adds, and it is why endorsement must be time-indexed (the verification policy is "F6 valid AND issuer endorsed for that type at issuance time"). *Costs:* the same as 3.1 or 3.2 depending on how the anchor is batched; the signature itself is free of gas. *Fails when:* the issuer's key is compromised and no on-chain key-history exists to bound the compromise in time — which is exactly why Set A must be on-chain for issuers even when credentials are not.

**3.4 Commitment then reveal.** The writer anchors a commitment c = H(value ‖ r) with random r, and reveals (value, r) later to whoever needs it. *Proves:* the value was fixed before the block time, without disclosing it. *Does not prove:* that a reveal will ever occur. *Costs:* one anchor write now (as 3.1 or 3.2), no write at reveal. *Fails when:* r is lost, or when the value space is small enough that the commitment leaks (a properly random r closes this). This is the pattern that makes a per-credential anchor GDPR-defensible: with a 128-bit salt inside the pre-image, the anchored hash is not a dictionary-attackable identifier. The repository's SD-JWT-style salted claim digests are a per-claim instance of the same idea; F8's presentationId is a commitment over (holder, credentialIds, challenge, domain) that is revealed to exactly one verifier.

**3.5 Accumulator anchor (revocation).** The issuer maintains a cryptographic accumulator over the set of non-revoked credential identifiers and anchors the accumulator value [12], [22]. Holders carry a witness; verifiers check membership against the anchored value. *Proves:* non-revocation as of the anchored epoch, without revealing which credential is being checked. *Does not prove:* anything about credentials whose witnesses have not been updated since the last epoch — witness update is the operational cost and the staleness source. *Costs:* one anchor write per epoch regardless of the number of revocations; witness-update bandwidth off-chain proportional to the revocation rate. *Fails when:* the holder cannot fetch a fresh witness (the low-connectivity case of 06), or when the issuer stops publishing epochs.

**3.6 Status-list anchor (bitstring).** The issuer publishes a compressed bitstring with one bit per credential and anchors its hash or serves it from a URL named in the credential's `credentialStatus` [NEW-1]. *Proves:* the status bit for index i, to anyone who can fetch the list. *Does not prove:* privacy — the verifier learns the index, and the issuer learns which lists are fetched (herd privacy from the list size mitigates but does not remove this). *Costs:* one list update and, if anchored, one small write per epoch; verifier fetch cost of the list (kilobytes, cacheable). *Fails when:* the list URL is unavailable (the fallback is the last cached list, with an explicit staleness window). O1's F7 is a per-credential storage flag (32,980 gas measured — the cheapest write in the trace, because it flips one already-allocated slot and emits one event). A status list amortises that to a fraction of a gas per credential but moves the read to an off-chain fetch. Memo A's stance — status lists for simpler proofs, accumulators for holder privacy, both with measured revocation latency, staleness windows and verification cost — is the comparison 02 §5 carries out.

**3.7 Credential-definition anchor (AnonCreds style).** Nothing per credential is written. The chain holds the schema, the issuer's credential definition (public key material for the CL or BBS+ signature scheme) and the revocation registry definition and accumulator [22], [25], [NEW-6]. *Proves:* that a presentation was derived from a credential signed under this definition, and that the credential is not revoked as of the accumulator epoch — all in zero knowledge. *Does not prove:* that a specific credential exists (there is no way to enumerate issued credentials from the chain, which is the point). *Costs:* one write per issuer per credential type, ever, plus accumulator epochs; per-credential on-chain cost is exactly zero. *Fails when:* the issuer needs an on-chain proof of issuance count or an on-chain per-credential audit trail (some regulated registries do), or when a verifier without ZK tooling must check a credential — in which case a signed-then-anchored fallback (3.3) is needed alongside. The GDPR nuance the Building Paths preface records is precisely the reason this pattern exists: the credential-definition hash is not personal data, whereas a per-credential content hash may be.

**Table 3.1 — The anchoring family compared**

| Pattern | On-chain writes | Per-credential on-chain datum | Proves existence-at-time | Native revocation | Privacy of anchor | Offline verifiability | Measured point (O1) |
|---|---|---|---|---|---|---|---|
| 3.1 Hash anchor | 1 per credential | Yes (hash + status) | Yes | Yes (F7) | Weak unless salted | Signature only | F5 130,163; F7 32,980 |
| 3.2 Merkle root | 1 per batch | No | Yes, with path | No (needs 3.5/3.6) | Root leaks nothing | Signature + path | none (extension) |
| 3.3 Signed-then-anchored | as 3.1 or 3.2 | Optional | Yes | as underlying | as underlying | Full (signature) | as underlying |
| 3.4 Commit/reveal | 1 per commitment | Commitment only | Yes | No | Strong | Reveal needed | F8 62,441 (presentation commitment) |
| 3.5 Accumulator | 1 per epoch | No | No | Yes, private | Strong | Witness needed | none |
| 3.6 Status list | 1 per epoch (optional) | Bit index off-chain | No | Yes, index visible | Herd only | Cached list | none |
| 3.7 Credential definition | 1 per issuer-type | None | No | Via 3.5 | Strongest | ZK proof needed | none |

The measured column is deliberately sparse. Only three patterns have a measured point, all from O1's S1 trace, and only for the per-credential variants. The batch, accumulator, status-list and definition anchors are exactly what S7/S8 and the later option ports must measure.

## 4. Read paths

**Claim.** The identity system has five distinct read paths, they have latencies spanning six orders of magnitude (microseconds for a cached signature check, minutes for an unindexed event replay), and the three-tier latency framework (contribution C6) is at bottom a rule about which read path is permitted at which tier.

**4.1 Direct view call.** F2 resolveDID, F6 verifyCredential and F12 validDelegate are `view` functions: gas-free, executed by any node against current state, never reverting on absent records (they return empty bytes or false). In the S1 trace they appear at seq 10–14 and 18 with no gasUsed field, as the schema requires for `kind=view`. *Latency:* dominated by the RPC round-trip — sub-millisecond against a co-located node, tens of milliseconds against a roadside unit (RSU) acting as an edge node, hundreds of milliseconds against a remote provider over a cellular link. *Trust assumption:* the node answers honestly about current state; a malicious or lagging node can serve a stale or false answer with no proof. *Tier fit:* Tier 3 always; Tier 2 only against an edge node (the thesis's own qualifier, "viable if edge-deployed"); never Tier 1. Note that because O1 keeps existence, controller, deactivation and delegate expiry in storage, F2/F6/F12 are complete without an indexer — this is what the explicit-DID gas premium buys.

**4.2 Indexer / event reconstruction.** Anything O1 writes only as an event — the F3 attribute values, and in canonical ERC-1056 the whole document — must be reconstructed by scanning logs. Without an index this is O(n) in the identity's history; with an indexer it is a database lookup, but now the indexer is a trusted off-chain component whose correctness is not proven by the chain. *Latency:* seconds to minutes unindexed; milliseconds indexed. *Trust assumption:* the indexer replayed every relevant log and none it should not have. *Tier fit:* Tier 3, or Tier 2 only via a pre-warmed cache. The interface's `resolveDID` returns a document and metadata from the contract precisely so that Set A does not depend on this path for its core fields; the price is that the O1 document is minimal (96 bytes in the trace: did, controller, keyCount) and the richer attribute set is indexer-only.

**4.3 Light-client / Merkle-proof reads.** A reader who holds only block headers can verify a storage slot (via a Merkle-Patricia proof against the state root) or a batch leaf (via the issuer's Merkle path against an anchored root) without trusting the serving node [NEW-4]. *Latency:* one header sync plus one proof verification — milliseconds of computation once the proof is in hand, but the proof must be fetched. *Trust assumption:* the header chain is honest (the consensus assumption only, not the node assumption). *Tier fit:* Tier 2 if proofs are pre-fetched with the credential, Tier 3 otherwise. This is the read path an OBU should use when it must check chain state through an RSU it does not fully trust; 08 §3 relies on it for the revocation-propagation crux.

**4.4 Cached reads with revocation-synchronised invalidation.** Memo A's rule — off-chain verification avoids block-time delays; only lifecycle events and anchors on-chain; cache invalidation synchronised with revocation state — defines this path. The verifier (a toll operator, a charging station, an RSU) caches F2/F6/F12 answers and the endorsement state, and subscribes to `CredentialRevokedEvent`, `DIDDeactivated`, `DelegateAdded` (for expiry) and endorsement-revocation events to invalidate entries. *Latency:* microseconds on hit. *Trust assumption:* the event subscription is live and the cache's clock is within a stated staleness window W of chain time. The S1 trace demonstrates the invalidation half in miniature: seq 17 revokes, seq 18 re-verifies and observes `valid=false revoked=true`, and the channel is torn down. What the trace does not measure — and what 08 and 06 need — is the propagation delay between the revocation block and the moment every cache has invalidated; that is a testnet quantity (§11). *Tier fit:* Tier 2 — this is the primary Tier 2 read path of the hybrid design (03 §4).

**4.5 Fully offline reads.** A verifier with no connectivity verifies the issuer's signature on a credential the holder presents from the OBU, checks expiry from the credential's own `validUntil`, and checks the endorsement and revocation status against whatever it last cached. *Latency:* microseconds to a few milliseconds (one secp256k1 recovery in the repository's EIP-191 cryptosuite; the DIGEST-LEVEL VehiclePassport figure of sub-5 ms verification for a vehicular attribute proof [NEW-8] bounds the ZK variant). *Trust assumption:* nothing has been revoked since the verifier's last sync — the staleness window is the whole risk. It is essential to state what breaks: an offline verifier will accept a credential revoked within W, and a deactivated issuer's credentials within W. The mitigations are short-lived credentials (small `validUntil`, so that expiry does the work revocation would), signed status snapshots with timestamps that the verifier can bound, and, for high-value actions, refusal to act offline. 06 instantiates these as the read-only and delayed-write scenarios. *Tier fit:* the only path available at Tier 1 and the fallback at Tier 2.

**Table 4.1 — Read paths**

| Path | Functions served | Latency (order) | Trust assumption | Staleness | Tier fit |
|---|---|---|---|---|---|
| 4.1 Direct view | F2, F6, F12, G4, C2, C4 | 1–500 ms by node locality | Serving node honest about state | None (current block) | 3; 2 if edge node |
| 4.2 Indexer | F3 attributes, full DID doc, history | ms indexed; s–min raw | Indexer complete and honest | Indexer lag | 3 |
| 4.3 Light-client proof | Any storage slot; batch leaves | ms compute + fetch | Consensus only | Header lag | 2 (pre-fetched) / 3 |
| 4.4 Cached + revocation sync | F2, F6, F12, G4 | µs on hit | Event feed live; clock within W | ≤ W | 2 (primary) |
| 4.5 Offline signature | Credential validity (signature, expiry) | µs–ms | Nothing revoked within W | W, unbounded if never re-synced | 1 fallback, 2 fallback |

## 5. Write paths

**Claim.** Writes are the scarce resource. Every write costs gas, waits for a block, and is exposed to reorganisation until finality; a vehicle is often unable to write at all. The system must therefore be designed so that no Tier 1 or Tier 2 action *requires* a write on its critical path, and so that writes that must eventually happen can be deferred, batched, sponsored, or delegated to a sidechain without losing ordering or attributability.

**5.1 Direct transaction.** The controller's key signs a transaction calling F1, F3, F4, F5, F7, F8, F9, F10 or F11 directly. All ten `kind=tx` entries in the S1 trace are of this form. *Ordering:* by block inclusion and, within a block, by the sequencer's or proposer's choice — two writes from different identities have no guaranteed order unless one depends on the other's state. *Finality:* the block's. *Reorg exposure:* until finality, the write may vanish and be re-included later or not at all; an F7 revocation that is reorged out leaves a window in which caches that saw the event have invalidated while the chain has not. *Fit:* Tier 3 administrative writes (registration, licence issuance, decommission) and any write where the vehicle itself is not the sender.

**5.2 Batched / Merkle write.** Section 3.2's pattern. One issuer accumulates b credentials over a batching window T_b and anchors one root. *Ordering:* the batch fixes a set, not a sequence; if ordering within the batch matters (odometer monotonicity across two service events), the credential content must carry the issuer's sequence number and the batch leaf order must be canonical. *Finality:* the root's block. *Reorg exposure:* one reorg reorders b credentials at once, so batch anchors should be confirmed to finality before holders are told their credential is anchored. *Fit:* Tier 3 issuance at scale — the OEM's birth certificates, the DMV's registrations, the service network's maintenance records.

**5.3 Meta-transaction / sponsored write.** The vehicle signs a message; a relayer submits the transaction and pays the gas [NEW-11]; the contract recovers the vehicle's key from the signature. ERC-1056 has this natively (its `*Signed` variants); ERC-4337 generalises it with paymasters [24]. The IMinimalSSI interface has no signed variants and must not be changed, so in the sandbox this is an extension contract that verifies a signature and calls the interface as the vehicle's registered delegate (F11 with a `sigAuth` delegate is the hook: addDelegate measured 54,227 gas for a 3,600 s validity). *Ordering:* the relayer chooses; a nonce inside the signed message prevents replay and enforces per-vehicle order. *Finality and reorg:* as 5.1. *Fit:* every write the vehicle originates — a vehicle should hold no gas token, both for UX and because a funded OBU is a theft target. Who pays is then explicit: the OEM, the fleet, or a jurisdictional sponsor (§7.5).

**5.4 Delayed write (queue on OBU, anchor on reconnect).** The OBU signs the write with a signed timestamp and a monotonically increasing per-OBU sequence number, queues it, and a relayer submits it when connectivity returns. *Ordering:* two orders exist and must be kept distinct — the OBU's claimed order (signed timestamps and sequence numbers, attributable but unverifiable at the time of claim) and the chain's inclusion order (verifiable but late). A verifier who cares which happened first must decide which order it trusts; the chain can prove the anchor was made no later than block time, and the signed timestamp asserts it was made no earlier than the OBU's clock — the interval between them is the uncertainty. *Finality:* deferred. *Reorg exposure:* as 5.1 once submitted. *Fit:* the low-connectivity scenarios of 06, and any Tier 2 action that produces a record (a toll passage, a charging session) where the action proceeds on the offline read path (4.5) and the record is anchored later. The clever part and its assumption, stated plainly: a delayed write lets the vehicle act now and prove later, *provided* the counter-party is willing to accept a signed, unanchored record as sufficient at the time — which is a policy of the counter-party, not a property of the system.

**5.5 Sidechain / L2 write with backbone anchoring.** The 2020 CVIN paper's design [5]: most transactions on a sidechain (or, in modern terms, a rollup or a jurisdictional Local CVIN), few on the backbone chain; Local CVINs derived from a Global CVIN through ID Porting Protocols (IDPPs) so that jurisdiction-specific policy runs on a smaller shard with lower lookup latency. In placement terms: Set A roots (F1, F4, key history for issuers and for vehicles' long-lived verinym DIDs) on the backbone; Set B anchors and high-frequency Set A operations (F11 delegate rotation for OBUs, F8 presentation commitments) on the Local CVIN; periodic checkpoints of the Local CVIN's state root on the backbone. *Ordering:* within the Local CVIN by its consensus; across Local CVINs only via backbone checkpoints. *Finality:* two-level — Local finality in seconds (QBFT-style deterministic finality is the sandbox's E1 substrate), backbone finality at checkpoint. *Reorg exposure:* a sidechain with its own validator set can fork independently of the backbone; a rollup cannot fork against L1 but can have its sequencer censor. *Fit:* this is the structural recommendation of 03, and the S5 IDPP scenario (O1 → O8 port) is its first testable instance.

**5.6 The write-availability problem.** A vehicle that cannot write but must still act is the normal case, not the exception, under the 2020 paper's wireless constraints (scarce compute, variable load, unreliable links, intermittent coverage). The system's answer has to be layered: (i) every Tier 1 and Tier 2 action is designed so that the *action* needs only a read path (4.4 or 4.5) and a signed off-chain exchange (the S1 ECDH/AES-256-GCM channel, seq 16 in the trace, is exactly such an exchange: the F8 presentation anchors the challenge, the channel is off-chain); (ii) any *record* of the action is a delayed write (5.4); (iii) any *revocation* the vehicle would want to trigger (say, of its own compromised delegate key) is pre-authorised to a guardian who can write on its behalf (an F11 delegate of the vehicle's controller, or the OEM as recovery key under the spec's recovery extension). What breaks: if the vehicle's own controller key is compromised while it is offline, nothing can revoke the delegate until the guardian learns of it; the exposure window is the guardian's detection latency, and the delegate validity chosen at F11 time bounds the damage (the S1 trace uses 3,600 s).

**Table 5.1 — Write paths**

| Path | Who signs | Who pays | Ordering guarantee | Finality | Reorg exposure | Tier fit |
|---|---|---|---|---|---|---|
| 5.1 Direct tx | Controller | Controller | Block inclusion | Chain's | Until finality | 3 |
| 5.2 Batched / Merkle | Issuer | Issuer | Set, not sequence (carry seq in content) | Root's block | Whole batch at once | 3 (issuance at scale) |
| 5.3 Meta-tx / sponsored | Vehicle (message) | Relayer / sponsor | Per-vehicle nonce | Chain's | As 5.1 | 2→3 records, all vehicle-originated writes |
| 5.4 Delayed write | Vehicle (signed ts + seq) | Relayer on reconnect | Claimed order vs inclusion order (distinct) | Deferred | As 5.1 once submitted | 2 records, 06 low-connectivity |
| 5.5 Sidechain / L2 + backbone anchor | Any | Any, at L2 rates | Local consensus; cross-shard via checkpoint | Two-level | Sidechain: independent forks; rollup: none vs L1 | 2 anchors, 3 roots |

## 6. Verifiable data integrity

**Claim.** Integrity in this system comes from two sources that must never be confused: the issuer's key (which proves who said it) and the chain (which proves when it was said and whether it has since been withdrawn). Every verification policy in the suite is a conjunction of one proof from each source, and every failure analysis is a question of which source has been compromised.

**6.1 The instruments.** Five instruments appear, with different scopes. A *signature* proves authorship and integrity of one object to anyone holding the public key, offline, without disclosure control (the whole object is signed). A *hash* proves integrity of one object to anyone holding the pre-image, and existence-at-time if anchored, with no authorship (anyone can hash). A *Merkle proof* proves membership of one object in an anchored set, with the same authorship gap, at logarithmic proof size. An *accumulator* proves membership or non-membership without revealing which member, at constant proof size, with a witness-maintenance cost. A *zero-knowledge proof* proves a predicate over signed data without revealing the data, at generation cost of milliseconds to seconds and verification cost that is either tiny off-chain or, on-chain, on the order of 200–350K gas for a Groth16 pairing check (DIGEST-LEVEL, thesis draft) — 02 §3 develops this fully and this document only places it: on-chain ZK verification is a Tier 3 tool for disputes and governance, never a Tier 2 read path.

**6.2 Content addressing.** When the credential content is stored off-chain in a content-addressed store, the anchored hash and the storage identifier coincide, and the "pre-image lost" failure of 3.1 becomes a pinning problem rather than a cryptographic one. For personal data, content addressing is a liability: a public CID is a public pointer to encrypted-or-not content, and the encryption key becomes the real access control. Memo A's stance — IPFS/Arweave or enterprise storage depending on regulation — resolves as: content-addressed for public artefacts (schemas, credential definitions, governance documents, execution-trace hashes), enterprise or holder-held for anything with a data subject.

**6.3 Canonicalisation.** A hash is only as reproducible as the byte string it was computed over. The repository's VC layer (`2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py`) canonicalises with deterministic JSON — sorted keys, minimal separators, UTF-8 — over the proof-less document, concatenates the canonical proof options, hashes with SHA-256 and signs with EIP-191 personal-sign under a thesis-defined cryptosuite `eip191-secp256k1-recovery-2024`. Its README records two deviations from the W3C stack: JSON-LD canonicalisation (URDNA2015) is not implemented, and the cryptosuite is not W3C-registered. The choice is defensible — Ethereum-native, offline-verifiable by any EVM tool, and free of the JSON-LD context-resolution dependency that would itself be a network read on the verification path — but its consequence must be stated: a credential issued by this layer cannot be verified by a conforming W3C Data Integrity verifier without an adapter, and the F5 `credentialHash` computed by `lib/vid/` (keccak256 over canonical JSON, per the brief §7) is a different hash from the SHA-256 the VC proof signs. Two hashes of one document is not an error, but it is a place where a verifier can be confused, and S7 should assert that both are recomputed from the same canonical bytes. A migration path to RFC 8785 JSON Canonicalization Scheme [NEW-13] would keep the deterministic-JSON property while adopting a published canonical form.

**6.4 Timestamp authority.** The chain is the system's timestamp authority: block time bounds when an anchor existed. Its precision is the block interval and its accuracy is the validators' clock discipline, neither of which is fine enough for Tier 2 event ordering (two toll passages 200 ms apart). Fine ordering therefore comes from signed OBU and RSU timestamps (5.4), with the chain providing the coarse, non-repudiable envelope. Where a legal timestamp is required, an RFC 3161-style authority [NEW-12] can countersign the anchor, and the countersignature can itself be anchored — a two-source timestamp.

**6.5 The forensic audit trail.** The Building Paths preface's formulation — blockchain does not prevent attacks, it makes them permanently visible and attributable — is a placement rule. For it to hold, three data kinds must be on-chain in a form that cannot be quietly rewritten: key-material history (F9/F10/F11 events and the controller in storage), credential lifecycle events (`CredentialIssued`, `CredentialRevokedEvent`) and presentation commitments (`PresentationCreated` with the challenge). Nothing else needs to be. In particular the *content* of what was presented, the *content* of the channel, and the *content* of an agent's execution trace can all be off-chain, provided their hashes are in the on-chain events or are recoverable from them. For agents this is the operational-transparency-not-algorithmic-transparency argument: the chain records that agent A presented credential c to verifier V under challenge x at block t and later signed action hash h; what A computed to decide on h is not on the chain and need not be.

**6.6 Where integrity comes from.** Table 6.1 states, per datum, which source is load-bearing.

**Table 6.1 — Source of integrity per datum**

| Datum | From the issuer's / holder's key | From the chain | Both required for |
|---|---|---|---|
| DID controller, deactivation | — | Storage (F2) | Authorisation checks |
| Verification methods, delegates | — | Storage + events (F9–F12) | Bounding key compromise in time |
| Credential content | Signature (EIP-191 / Data Integrity) | Hash anchor (F5) | Existence-at-time and current status |
| Credential status | — | F7 flag, status list, or accumulator epoch | Revocation |
| Issuer authority for a type | — | Endorsement registry (G2/G4), time-indexed | Verification policy |
| Presentation | Holder's signature over VP | F8 commitment (challenge, domain) | Replay prevention with audit |
| Channel contents | AEAD tag under session key | Nothing (by design) | — |
| Reputation attestation | Attester's signature | C1 anchor with evidence URI | Sybil-resistance via issuer weighting |
| Execution trace | Agent's signature | Hash of trace in an event or anchor | Dispute |

## 7. Cost model

**Claim.** The order of magnitude of the system's cost is determined by three choices — L1 or L2, per-credential or batched anchoring, and who pays — and not by the per-function gas figures, which vary by at most a factor of about five across the interface. The model below is parametric; the only measured points are O1's S1 gas figures; all other quantities are labelled assumptions.

**7.1 On-chain cost per function.** For a function f with measured gas g_f, gas price p (in gwei) and token price P (in currency units per token),

  C_f = g_f × p × 10⁻⁹ × P × m,

where m is the L1/L2 multiplier: m = 1 on L1, and m ≪ 1 on a rollup, where the execution gas is cheap and the dominant term is amortised L1 data cost — so that on L2 a better model is C_f = (g_f × p_L2 + d_f × p_data) × 10⁻⁹ × P with d_f the calldata bytes the function posts to L1. Since d_f has not been measured for any option, this document uses a single multiplier m as a stated hypothesis and flags it for measurement.

**Table 7.1 — Measured gas (O1_ERC1056, S1 trace) and cost at illustrative parameters**

| Function | Measured gas g_f | Spec target (ERC-1056) | Cost at p = 10 gwei, P = US$3,000/ETH, m = 1 (ILLUSTRATIVE ASSUMPTION) | Same at m = 0.02 (HYPOTHESIS) |
|---|---|---|---|---|
| F1 createDID | 161,823 / 161,835 / 178,935 | <100K (missed; recorded deviation) | US$4.85–5.37 | US$0.10–0.11 |
| F3 updateDID | 44,760 | <80K | US$1.34 | US$0.027 |
| F4 deactivateDID | 55,127 | <50K (missed by ≈10%) | US$1.65 | US$0.033 |
| F5 issueCredential | 130,163 | <120K (missed by ≈8%) | US$3.90 | US$0.078 |
| F7 revokeCredential | 32,980 | <50K | US$0.99 | US$0.020 |
| F8 createPresentation | 62,441 (one credential) | <150K | US$1.87 | US$0.037 |
| F9 addVerificationMethod | 59,607 | <100K | US$1.79 | US$0.036 |
| F10 removeVerificationMethod | 36,478 | <50K | US$1.09 | US$0.022 |
| F11 addDelegate | 54,227 | <60K | US$1.63 | US$0.033 |
| F2, F6, F12 (view) | 0 | <10K / <10K / <5K | 0 | 0 |

The gas column is the only measured content of this table. The gas price of 10 gwei and the token price of US$3,000 are illustrative parameters chosen for round arithmetic and are not observations of any market; readers should substitute current values. Three targets are missed (F1 by a factor of ≈1.6–1.8, F4 and F5 by under 10%), and the F1 miss is the architectural one already recorded in `docs/FINDINGS.md` of the sandbox. Note also that F8's measured gas is for a single credential id; the loop in `createPresentation` performs one storage read of the credential struct per id, so the cost grows linearly in the number of presented credentials by roughly the cold-SLOAD cost per struct field touched — a hypothesis until an S7 run presents two or three credentials at once.

**7.2 Off-chain cost.** Three off-chain terms dominate and none is measured in the repository: storage of credential content and batch trees (bytes per credential s_c, on the order of one to a few kilobytes for the UC1–UC10 schemas; retention years R; storage price per GB-year p_s); indexer operations (one process per chain per operator, tracking every relevant event; its cost is a fixed operational term plus a per-event term proportional to event volume); and bandwidth (status-list or witness fetches per verification, on the order of kilobytes; presentation exchange per interaction, on the order of a kilobyte plus the ZK proof size if used). At the volumes of §7.3 these are small in currency terms and large in operational terms: the indexer and the status-list server are the availability-critical components of the read path 4.4, and their outage is the failure that turns Tier 2 into Tier 3.

**7.3 Lifecycle cost per vehicle-year.** Let N be the fleet size, e the anchored events per vehicle-year (lifecycle credentials plus registrations plus delegate rotations plus presentations that are anchored), b the batch factor (credentials per anchor write), g_a the gas of one anchor write, and g_dir the gas of one direct per-event write. Then annual on-chain cost is

  C_year = N × e × (g_dir / 1 if unbatched, else g_a / b) × p × 10⁻⁹ × P × m,

plus the one-time onboarding cost N × g_F1 × p × 10⁻⁹ × P × m.

**Table 7.2 — Worked examples (all parameters are labelled assumptions except the O1 gas)**

| Variable | Value | Label |
|---|---|---|
| N | 33,000,000 | DIGEST-LEVEL (Canada registered vehicles, per brief) |
| e | 4 anchored events per vehicle-year | ASSUMPTION (e.g., 1 registration renewal, 2 maintenance, 1 inspection) |
| g_dir | 130,163 gas (F5) | MEASURED, O1 |
| g_a | 60,000 gas per batch anchor | DESIGN ESTIMATE (base 21K + 1 SSTORE 20K + event + overhead) |
| b | 1,000 | ASSUMPTION |
| p | 10 gwei | ILLUSTRATIVE |
| P | US$3,000 / ETH | ILLUSTRATIVE |
| m | 1 (L1) or 0.02 (L2) | HYPOTHESIS for L2 |

| Configuration | Per credential | Per vehicle-year | Fleet-year (N = 33 M) | One-time onboarding (F1, N × 161,835 gas) |
|---|---|---|---|---|
| A. L1, per-credential F5 anchor | US$3.90 | US$15.62 | ≈ US$515 M | ≈ US$160 M |
| B. L2 (m = 0.02), per-credential F5 anchor | US$0.078 | US$0.31 | ≈ US$10.3 M | ≈ US$3.2 M |
| C. L1, Merkle batch b = 1,000 | US$0.0018 | US$0.0072 | ≈ US$0.24 M | ≈ US$160 M (unbatched F1) |
| D. L2, Merkle batch b = 1,000 | ≈ US$0.00004 | ≈ US$0.00014 | ≈ US$5 K | ≈ US$3.2 M |
| E. Credential-definition anchor (3.7), any chain | 0 | 0 | 0 (plus accumulator epochs) | as above |

The arithmetic is transparent: 130,163 gas × 10 gwei = 0.00130163 ETH ≈ US$3.90; × 4 events ≈ US$15.62; × 33 M ≈ US$515 M. The conclusions do not depend on the illustrative prices: moving from A to B is a factor of 1/m, from A to C a factor of roughly g_a/(b × g_dir) ≈ 1/2,200, and from C to E the per-credential term vanishes. Configuration A is unaffordable at national scale and configuration C is trivially affordable, and the difference is entirely a placement decision. The onboarding column is the reminder that Set A does not batch: every vehicle needs its own F1, and the recorded F1 deviation (explicit-DID storage) is worth about US$160 M at L1 across the Canadian fleet under these parameters, or US$3.2 M on an L2 — which is the strongest argument in the campaign for placing vehicle DIDs on a Local CVIN (5.5) rather than on a public L1.

**7.4 What batching costs elsewhere.** Batching moves cost, it does not remove it. The issuer must retain the tree (storage) or the holder must retain the path (wallet bytes); revocation cannot use F7's per-credential flag and needs a status list or accumulator (epoch writes plus fetch bandwidth); the anchoring delay T_b becomes a write-latency term that must fit the tier (§5.2). The full accounting for a design is therefore C_year(on-chain) + C(storage) + C(indexer) + C(bandwidth) + the latency cost of T_b, and 03 §6 carries the composite budget for the hybrid.

**7.5 Who pays.** Five candidate payers, with the write paths that make each feasible: the *OEM* (pays F1 for the vehicle DID and the birth-certificate anchor at manufacture, via 5.2 batching — the natural payer for Set A onboarding); the *DMV or ministry* (pays registration and licence anchors, via 5.2, and endorsement writes G1–G3, which are rare and can be direct 5.1); the *driver* (should pay nothing on-chain; presentation writes under F8 are the only vehicle-originated write on the Tier 2 path and should be sponsored, 5.3, or replaced by an off-chain VP with only a periodic batch commitment); the *fleet operator* (pays for its vehicles' delegate rotations F11 and lifecycle anchors, and is the natural relayer for 5.3/5.4); and a *sponsor* (a paymaster in ERC-4337 terms, or the jurisdiction operating the Local CVIN, absorbing sidechain fees as a public-infrastructure cost). The design consequence is that the interface's `msg.sender == controller` authorisation model (O1's `onlyController`) forces the payer to be the controller or a delegate, which is why sponsored writes require the F11 delegate hook or an extension contract; this is a constraint of the normative interface and it is respected, not altered.

## 8. Per-function placement matrix

**Claim.** Each of the twelve functions, the four Set C functions and the four governance functions has a definite answer to what it puts on-chain, what stays off-chain, what may be cached, which tier it serves, and what breaks when the vehicle is offline. Table 8.1 records these answers for O1 as built and, where the hybrid of 03 would differ, says so in the notes.

**Table 8.1 — Per-function placement (O1 as built; hybrid deltas noted)**

| F | Function | On-chain | Off-chain | Cached at verifier | Tier served | Breaks offline | Notes |
|---|---|---|---|---|---|---|---|
| F1 | createDID | Identity struct (controller, timestamps, flags, keyCount) in storage; DIDCreated event | Key generation on OBU/HSM; DID method string | DID → controller | 3 | Cannot create; pre-provision at manufacture | Storage-heavy: 161–179K measured. Hybrid: vehicle DIDs on Local CVIN, issuer/endorser DIDs on backbone |
| F2 | resolveDID | View over storage (96-byte doc) | Full document via indexer for F3 attributes | Yes, invalidated on DIDUpdated/Deactivated | 2 (edge) / 3 | Serves from cache within W | No indexer needed for core fields |
| F3 | updateDID | Events only (DIDAttributeChanged, DIDUpdated); versionId in storage | Attribute value semantics; service endpoints | Attribute values | 3 | Queue as delayed write | Cheapest lifecycle write, 44,760 |
| F4 | deactivateDID | Flag in storage; event | — | Yes (terminal) | 3 | Guardian must write | Irreversible; cache must treat as terminal |
| F5 | issueCredential | Six-field anchor struct; CredentialIssued | Credential JSON, signature, salts (holder + issuer) | credentialId → (valid, issuer) | 3 | Issuer offline: sign now, anchor later | Hybrid: Merkle batch or definition anchor; F5 retained for singleton high-value credentials |
| F6 | verifyCredential | View: existence, revoked, expired, issuer deactivated | Signature check, schema check, endorsement policy | Yes, invalidated on CredentialRevokedEvent / DIDDeactivated | 2 (cached) / 3 | Serves from cache; accepts revoked-within-W | Does not check issuer authority (that is G4) |
| F7 | revokeCredential | Flag flip; event | Reason, evidence | Triggers invalidation | 3 | Issuer offline: revocation delayed, W grows | 32,980 measured; hybrid: status list / accumulator epoch |
| F8 | createPresentation | Commitment + used-challenge flag; event | VP contents, selective disclosure, ZK proof, signature | presentationId | 2 only if sponsored + edge; else 3 | Cannot anchor; VP verified off-chain by signature, commitment queued | Anchor-implemented, not native; hybrid: off-chain VP with optional later commitment |
| F9 | addVerificationMethod | Key id flag, keyCount; event | Public key bytes (in calldata, indexable) | Key set | 3 | Queue | 59,607 measured |
| F10 | removeVerificationMethod | Flag clear, keyCount; event | — | Key set | 3 | Queue; compromised key stays valid until anchored | 36,478 measured; never removes last key |
| F11 | addDelegate | Expiration in storage; event | Delegate key on OBU | delegate → expiry | 3 (rotation), enables 2 | Cannot rotate; existing delegate valid to expiry | 54,227 measured; the sponsored-write hook |
| F12 | validDelegate | View over storage | — | Yes, expiry known locally | 2 (cached) / 3 | Serves from cache; expiry is local arithmetic | Best-behaved offline: validity is self-describing |
| C1 | attestReputation | Score, attester, evidence URI hash | Evidence content | Aggregate | 3 | Queue | 09 §4 |
| C2 | getReputation | View aggregate | Per-attester detail via indexer | Yes | 2 (cached) / 3 | Serves from cache | — |
| C3 | requestValidation | Request id, type, payload hash | Payload; validator computation (zkML/TEE) | — | 3 | Cannot request | — |
| C4 | validationStatus | View | Validator's report | Yes | 3 | Serves from cache | — |
| G1 | registerIssuer | Issuer DID → role | Governance documents | Role | 3 | n/a (governance is never offline-critical) | Rare writes; direct tx |
| G2 | endorseIssuer | (endorser, issuer, type, validity) | Endorsement rationale | Endorsement set with validity | 3, read at 2 | Serves from cache | Must be time-indexed for "at issuance time" policy |
| G3 | revokeEndorsement | Flag; event | Reason | Triggers invalidation of all credentials of that issuer-type issued after revocation | 3 | Propagation delayed | The most cache-expensive revocation in the system |
| G4 | isEndorsed | View | — | Yes | 2 (cached) / 3 | Serves from cache | Policy conjunct with F6 |

The column "breaks offline" is the honest one. Read-type functions (F2, F6, F12, C2, C4, G4) degrade gracefully to cached answers with a staleness window; write-type functions either queue (F3, F5 from the issuer side, F9, F10, F11, C1) or require a guardian (F4, F7). The two that cannot be papered over are F10 — a compromised key remains valid until the removal is anchored — and F8 as an on-chain write, which is why the hybrid keeps presentations off-chain on the Tier 2 path.

## 9. Per-object placement matrix

**Claim.** Placing the objects, rather than the functions, exposes the two objects that most tempt designers into error: the vehicle DID (which must be on-chain but must not be the Tier 1 pseudonymous identity) and the presentation (which must be off-chain in content but on-chain in commitment when audit is required).

**Table 9.1 — Per-object placement**

| Object | On-chain | Off-chain (where) | Anchoring pattern | Privacy note | Offline behaviour |
|---|---|---|---|---|---|
| Vehicle DID (verinym) | Identity struct, key history, delegates | DID document extras in indexer; private keys in OBU HSM | Storage (Set A) | Long-lived, linkable by design; use only for commercial/administrative transactions (dual-mode, [5]) | Resolvable from cache; cannot rotate keys |
| Vehicle pseudonymous stream DIDs | Optionally nothing; or a batch commitment to a set of pairwise DIDs | OBU | 3.4 commit / none | Tier 1 identities stay under SCMS [6], [28]; the DID system extends, not replaces | Fully local |
| Driver DID | Identity struct, key history | Wallet app / OBU pairing | Storage | One DID per driver is linkable; pairwise DIDs per verifier for privacy-critical uses | Resolvable from cache |
| Organisation DIDs (OEM, DMV, ministry, insurer, police, service centre, fleet) | Identity struct, key history, endorsements, roles | Enterprise HSM | Storage, backbone chain | Public by intent | Cached; these are the roots of trust and must be highly available |
| VID birth certificate (MOBI VID I) | Anchor (F5 or batch root); on the cv2x-testbed registry also vinHash + encrypted VIN + birthCertHash | Full certificate at OEM and in OBU | 3.2 batch by OEM; 3.4 salted VIN hash | VIN is quasi-personal (links to owner); salt it; never plaintext | Signature-verifiable offline forever; immutable, so W is irrelevant |
| Vehicle registration ("car ID") | Anchor; status | DMV store; OBU; owner wallet | 3.1 or 3.2 by DMV; 3.6 status list for renewal/lapse | Plate + owner DID is personal; content off-chain | Offline-verifiable; lapse risk within W; short validity preferred |
| Driver's licence | Anchor; status | DMV store; driver wallet | 3.2 + 3.5 or 3.6; ZK predicates (class, age) per 02 | Highly personal; per-credential hash must be salted (3.4) or replaced by definition anchor (3.7) | Offline-verifiable; suspension within W is the residual risk |
| Lifecycle events (11 types) | Anchor per event or per batch; issuer role via endorsement | Service/insurer/police/DMV stores; OBU copy | 3.2 by issuer; odometer monotonicity checked off-chain across events | Repair history is commercially sensitive, not legally personal in most readings; accident/theft records may be | Recorded offline as delayed writes (5.4); order by signed sequence |
| Endorsements (G2) | Full tuple (endorser, issuer, type, validity) | Rationale documents | Storage, backbone | Public by intent | Cached; revocation propagation is the crux (08 §3) |
| Presentations (F8 / VP) | Commitment + challenge flag when anchored; nothing on the Tier 2 path | VP object at holder and verifier | 3.4 | The presentation is the most privacy-sensitive object in the system; ZK per 02 | Verified by signature offline; commitment queued |
| Channel keys (I2I) | Nothing | Ephemeral in both endpoints; forward-secret | none | Never anchored | Fully local; torn down on revocation observed via 4.4 |
| Reputation attestations (C1) | Score, attester, evidence hash | Evidence at attester; aggregate in indexer | 3.1 (small) | Attester weighting handles Sybil; score is about a DID, so the DID's linkability governs | Aggregate cached |
| Oracle-fed data (odometer, telematics, sensor summaries) | Oracle's signed report hash or aggregate; not raw data | Oracle nodes; OEM telematics | 3.3 signed-then-anchored by the oracle set | Raw telemetry is personal; anchor only aggregates or predicates | Unavailable offline; the last anchored value is the fallback |
| Execution traces (agent actions; sandbox JSONL) | Hash of the trace, or of each signed action, in an event | Trace file at operator; at the agent | 3.2 per session | Operational transparency; contents may be commercially sensitive | Written locally, anchored later |

Two entries deserve a sentence each. The pseudonymous stream row is where the extension-not-replacement framing becomes a placement rule: Tier 1 identities are SCMS pseudonym certificates, and the DID system's only obligation toward them is a possible commitment linking a batch of pseudonyms to a verinym under sealed conditions (the accountability hook), never an on-chain per-pseudonym record. The oracle row is where the 2020 paper's distributed-oracle concept lands: an oracle set's signed aggregate is a signed-then-anchored datum whose issuer is the oracle set, and whose authority is an endorsement of that oracle set for the data type — so oracles are just issuers under G2 and need no separate trust machinery.

## 10. The decision framework

**Claim.** The analysis above compresses into eleven placement rules, each of the form "if the datum has property X then place it at Y," each with a one-line reason, and each traceable to a section of this document. 03 instantiates these rules as the hybrid's tiered placement; 04–08 apply them scenario by scenario.

1. **If a datum is needed to answer "who controls DID d, and who controlled it at time t" — place it in contract storage with an event (Set A on-chain).** Reason: the accountability gap is a key-history question and only consensus-backed storage answers it without trusting an operator (§1, §6.5).
2. **If a datum has a data subject — never place its content on any chain; place its content at the holder and at the issuer, and place only an anchor.** Reason: chains are public and permanent; erasure is impossible (§2, §3).
3. **If the anchor of a datum with a data subject is per-object — salt the pre-image (commit/reveal) or move to a definition anchor.** Reason: an unsalted hash of enumerable content is personal data in the strict reading (§3.4, §3.7).
4. **If a datum is issued at volume by one issuer — batch its anchors under a Merkle root and carry the issuer sequence in the content.** Reason: cost falls by roughly g_a/(b × g_dir) and ordering within the batch is otherwise undefined (§3.2, §5.2, §7.3).
5. **If a datum is read on a Tier 2 critical path — place a copy at the verifier's cache with revocation-synchronised invalidation and at the holder's wallet with the issuer's signature; never require a chain read or write at interaction time.** Reason: block time and RPC round-trips exceed the tier budget; the cache and the signature together cover the read (§4.4, §4.5).
6. **If a datum's validity can be self-described — give it an expiry short enough that expiry substitutes for revocation within the acceptable staleness window.** Reason: F12's offline good behaviour comes from expiry being local arithmetic; the same design makes any credential offline-safe (§4.5, Table 8.1).
7. **If a datum must be revoked and privacy of the check matters — anchor an accumulator epoch; if simplicity and cacheability matter more — anchor a status list.** Reason: the two revocation models trade holder privacy against verifier simplicity and neither costs a per-credential write (§3.5, §3.6; 02 §5).
8. **If a write originates at the vehicle — sponsor it (meta-transaction via an F11 delegate or an extension contract) and permit it to be delayed with a signed timestamp and sequence number.** Reason: vehicles must hold no gas token and are intermittently connected; the interface's controller-only authorisation forces the delegate hook (§5.3, §5.4, §7.5).
9. **If a datum is a high-frequency vehicle operation (delegate rotation, presentation commitment, lifecycle anchor) — place it on a Local CVIN / L2 with periodic backbone checkpoints; if it is a root of trust (issuer DID, endorsement, credential definition) — place it on the backbone.** Reason: the two-level finality matches the two-level trust, and it is the 2020 architecture made concrete (§5.5).
10. **If integrity of a datum must be checkable by a party with no chain access — sign it; if its existence-at-time or current status must be checkable — anchor it; if both — do both, and state which source each verifier relies on.** Reason: the two integrity sources are independent and neither substitutes for the other (§6, Table 6.1).
11. **If a datum is the content of a channel, a presentation, or an agent's computation — place nothing of it on-chain except a hash in an event when audit is required.** Reason: operational transparency is served by the commitment; algorithmic and content transparency are neither required nor desirable (§6.5, Table 9.1).

The rules are consistent with the normative interface: none requires changing a signature, error or event, and every extension they imply (batch anchor, sponsored write, endorsement, status list, accumulator) lives beside IMinimalSSI as spec §6 permits.

## 11. What to build and measure

**Claim.** Every open quantity in this document can be assigned to one of three resolution authorities: the sandbox's S7/S8 scenario scripts (resolvable now, on Hardhat), a public or permissioned testnet run (resolvable with modest effort), or hardware in a vehicle or RSU (not resolvable in this campaign). Table 11.1 makes the assignment so that 00 can schedule it and 10 can report it.

**Sandbox-resolvable (S7 `run_vid_minimal.js`, S8 `run_vid_lifecycle.js`, `test/vid.js`).** The trace assertions proposed for S7 are: (a) gas of G1, G2, G3 and of F5 for each of VID_BIRTH, VEHICLE_REGISTRATION and DRIVER_LICENCE, recorded with `fnId` tags F5 and G1–G4 per the schema; (b) gas of F8 with one, two and three credential ids, to test the linear-growth hypothesis of §7.1; (c) a `kind=offchain` entry per off-chain verification recording that signature check, hash recomputation (keccak256 over canonical JSON, and the SHA-256 the VC proof signs, both from the same canonical bytes, §6.3) and endorsement policy all passed, with wall-clock ms in `ts` deltas; (d) a post-revocation F6 view showing `revoked=true` and a post-G3 G4 view showing `false`, in that order, to fix the invalidation semantics; (e) for the theft-to-recovery chain in S8, the ordering assertion that a RECOVERY credential's issuer sequence exceeds the THEFT_REPORT's, checked off-chain, and that odometer values are non-decreasing across MAINTENANCE/REPAIR/INSPECTION events. A proposed extension scenario, S9 "batch anchor," would add a Merkle-root anchor contract beside the interface and measure g_a and the per-leaf verification cost off-chain, converting the design estimate of §7.3 into a measured point; it is listed as a proposal, not a commitment.

**Testnet-resolvable.** The L2 multiplier m and the calldata term d_f (§7.1); the revocation-propagation delay from F7 block to cache invalidation across k subscribers (§4.4; the 08 crux); the reorg exposure of an F7 in practice on a probabilistic-finality chain versus a QBFT chain (§5.1); the RPC latency distribution of F2/F6/F12 against local, edge and remote nodes (§4.1), which is the empirical content of the "viable if edge-deployed" qualifier. Caliper workloads over the twelve functions, already planned in the sandbox architecture, are the instrument.

**Hardware-only.** OBU-side signature and ZK proof generation latency under automotive compute budgets; the staleness window W actually achieved by a vehicle over a drive cycle with realistic coverage; the delayed-write queue depth and reconnection behaviour; the SUMO-harness interaction of the cv2x-testbed with real radio links. These cannot be settled in this campaign and are stated as such.

**Table 11.1 — Open quantities and their resolution authority**

| Quantity | Section | Authority | Instrument | Proposed metric / assertion |
|---|---|---|---|---|
| Gas of G1–G4, F5 per credential type | 7.1, 8 | Sandbox | S7 | gasUsed per fnId; compare to O1 F5 130,163 |
| F8 gas vs number of credentials | 7.1 | Sandbox | S7 | gasUsed at n = 1, 2, 3; slope ≈ cold-SLOAD cost per struct |
| Batch anchor gas g_a; per-leaf proof size | 3.2, 7.3 | Sandbox | S9 (proposed) | gasUsed; bytes of path at b = 10, 100, 1,000 |
| Two-hash consistency (keccak vs SHA-256 over same canonical bytes) | 6.3 | Sandbox | S7, test/vid.js | Assertion passes |
| Off-chain verification time | 4.5 | Sandbox (indicative only) | S7 offchain entries | ts delta, ms; labelled as desktop, not OBU |
| Revocation propagation delay | 4.4 | Testnet | k subscribers + Caliper | Block-to-invalidation ms, p50/p95 |
| L2 multiplier m, calldata d_f | 7.1 | Testnet | Rollup deployment of O1 | Measured cost ratio per function |
| View-call latency by node locality | 4.1 | Testnet | RPC probes | ms, local / edge / remote |
| Reorg exposure of F7 | 5.1 | Testnet | Probabilistic vs QBFT chain | Observed reorg depth, count |
| OBU proof and signature latency; W over drive cycle | 4.5, 5.6 | Hardware | Not in scope | — |

---

## Sources used in this document

| Ref | Source | Verification state | How used |
|---|---|---|---|
| [5] | Prakash, Michelson, Feng, 'CVIN: Connected vehicle information network,' IEEE VTC2020-Spring | VERIFIED AT SOURCE (author's own paper, as summarised in the brief) | Latency tiers, sidechain/backbone, Local CVIN/IDPP, oracles, dual identity modes, wireless constraints (§1, §5.5, §9) |
| [6] | Brecht et al., SCMS, IEEE T-ITS 2018 | DIGEST-LEVEL | Centralised-PKI archetype (§1, §9) |
| [8] | W3C DID Core 1.0, 2022 | DIGEST-LEVEL | Set A semantics (§1, §8) |
| [9] | W3C VC Data Model 1.1, 2022 | DIGEST-LEVEL | Credential/presentation object model (§3, §9) |
| [10] | W3C VC Data Model 2.0, 2025 | DIGEST-LEVEL | Privacy considerations on status and hashes (§1) |
| [12] | Camenisch & Lysyanskaya, CRYPTO 2004 | DIGEST-LEVEL | Accumulator basis (§3.5, §6.1) |
| [14] | Fett, Yasuda, Campbell, SD-JWT, RFC 9901, Nov 2025 | DIGEST-LEVEL | Salted claim digests as per-claim commitment (§3.4) |
| [22] | Dunphy, blockchain trilemma / Indy, arXiv:2204.05784 | DIGEST-LEVEL | Definition-anchor and accumulator placement in Indy (§1, §3.7) |
| [23] | ERC-1056 | VERIFIED AT SOURCE via O1_ERC1056.sol and the brief; standard text DIGEST-LEVEL | Event-sourced design, signed variants (§2, §5.3) |
| [24] | ERC-4337 | DIGEST-LEVEL | Paymaster-sponsored writes (§5.3) |
| [25] | LFDT, Indy on Besu joins did:indy | DIGEST-LEVEL | E1 substrate, QBFT finality (§3.7, §5.5) |
| [28] | IEEE 1609.2-2022 | DIGEST-LEVEL | Tier 1 identities remain SCMS (§9) |
| NEW-1 | W3C Bitstring Status List v1.0 | DIGEST-LEVEL (not read at source) | Status-list anchor (§3.6) |
| NEW-2 | EIP-2929 (gas cost increases for state access) | DIGEST-LEVEL (constants from the brief) | SLOAD/SSTORE constants (§2, §7) |
| NEW-3 | EIP-4844 (shard blob transactions) | DIGEST-LEVEL (retention figure from the brief) | Blob row of the taxonomy (§2) |
| NEW-4 | Merkle, 'A digital signature based on a conventional encryption function,' CRYPTO 1987; light-client proof literature | UNVERIFIED (not read at source for this document) | Merkle anchors and light-client reads (§3.2, §4.3) |
| NEW-5 | IPFS (Benet 2014) / Arweave whitepaper | UNVERIFIED | Content-addressed storage row (§2, §6.2) |
| NEW-6 | W3C Data Integrity / BBS Cryptosuite | DIGEST-LEVEL | Signed-then-anchored and definition anchors (§3.3, §3.7) |
| NEW-8 | VehiclePassport, arXiv:2509.06133 | DIGEST-LEVEL (figures from the brief) | Bound on offline ZK verification latency (§4.5) |
| NEW-11 | ERC-2771 secure protocol for native meta-transactions | UNVERIFIED | Meta-transaction pattern (§5.3) |
| NEW-12 | RFC 3161 time-stamp protocol | UNVERIFIED | Two-source timestamp (§6.4) |
| NEW-13 | RFC 8785 JSON Canonicalization Scheme | UNVERIFIED | Migration path from deterministic JSON (§6.3) |
| Repo | `5_minimal-ssi-sandbox/contracts/implementations/O1_ERC1056.sol`, `contracts/interfaces/IMinimalSSI.sol`, `traces/SCHEMA.md`, `traces/i2i_O1_ERC1056_1780620182135.jsonl`, `docs/ARCHITECTURE.md`; `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py` and README | VERIFIED AT SOURCE (read for this document) | All measured gas; storage/event design; canonicalisation deviation |
| Brief | `_CONTEXT_BRIEF.md` (memos A/B, Technical Memo 2, Building Paths preface, spec §5.3 targets, Canada fleet figure) | VERIFIED AT SOURCE (the brief); underlying memos DIGEST-LEVEL | Framing sentences, targets, DIGEST-LEVEL constants |

## Registry delta rows

| Content Block | T | Source | Ch. | Ready % | Notes |
|---|---|---|---|---|---|
| The six-question data-placement framing and its reduction of Set A/Set B to a placement finding | A | 01 §1 | 4 §4.4; hook 2 §2.4 | 80 | Argument complete; awaits S7/S8 numbers |
| Placement taxonomy (ten locations, eight attributes) | B | 01 Table 2.1 | 4 §4.4 | 85 | EVM constants DIGEST-LEVEL |
| Storage-vs-event finding within O1 (F3 44,760 vs F1 161,835; factor ≈3.6) | A/B | 01 §2, trace | 4 §4.2, §4.4 | 95 | Measured |
| Anchoring pattern family (seven patterns) with measured/unmeasured column | A/B | 01 §3, Table 3.1 | 4 §4.4 | 80 | Measured only for 3.1, 3.4, 3.6-as-flag |
| Read-path catalogue and tier fit | B | 01 Table 4.1 | 4 §4.5 (latency) | 80 | Propagation delay unmeasured |
| Write-path catalogue incl. delayed write with dual ordering | A/B | 01 §5, Table 5.1 | 4 §4.4; 5 §5.1 | 75 | Sponsored-write extension unbuilt |
| Two-source integrity table | B | 01 Table 6.1 | 4 §4.4 | 85 | — |
| Canonicalisation deviation and two-hash consistency assertion | A | 01 §6.3 | 4 §4.1 (compliance) | 90 | Assertion to be added to S7 |
| Parametric cost model with worked examples A–E | B | 01 §7, Tables 7.1–7.2 | 4 §4.2, §4.4 | 70 | g_a, m are estimates/hypotheses |
| "Who pays" analysis tied to controller-only authorisation | A | 01 §7.5 | 4 §4.4; 5 §5.1 | 80 | — |
| Per-function placement matrix (F1–F12, C1–C4, G1–G4) | B | 01 Table 8.1 | 4 §4.4 | 85 | Hybrid deltas to be confirmed by 03 |
| Per-object placement matrix | B | 01 Table 9.1 | 4 §4.4 | 85 | — |
| Eleven placement rules | A | 01 §10 | 5 §5.1 | 85 | Instantiated by 03 |
| Open-quantity resolution table | B | 01 Table 11.1 | 4 §4.4; S3 | 90 | Feeds 00 schedule and 10 |

## Open questions for the researcher

1. **Which anchoring pattern is the default for DRIVER_LICENCE in the VID build: salted per-credential F5 anchor (keeps O1 unmodified, measurable now) or a credential-definition anchor (AnonCreds-style, zero per-credential writes, requires ZK tooling that O1 lacks)?** This decides whether 03's hybrid treats F5 as the primary issuance path or as the fallback for singleton high-value credentials, and it cannot be decided by measurement — it is a stance on GDPR exposure versus toolchain realism.
2. **Is S9 (batch anchor beside the interface) in scope for this pass, or does the campaign carry g_a as a design estimate into the thesis?** Every fleet-scale cost claim in §7.3 rests on that one number.
3. **Should the F1 explicit-DID deviation be accepted as the price of an indexer-free read path (and argued as such in Chapter 4), or should a leaner O1 variant be built to recover the <100K target and the indexer-dependence be accepted instead?** The two positions are both defensible; the thesis should hold exactly one.
4. **Does the campaign commit to the two-hash arrangement (keccak256 for F5, SHA-256 for the VC proof) as permanent, or is RFC 8785 plus a single hash the intended end state?** This affects the compliance matrix's deviation count and the verifier's complexity.
5. **For delayed writes, which order does the thesis declare authoritative for lifecycle events — the OBU's signed sequence or chain inclusion?** 06 and 08 both need the answer, and it is a legal/policy position, not an engineering one.
6. **Who is the assumed payer for vehicle-originated writes in the reference scenarios — OEM, fleet, or a jurisdictional sponsor operating a Local CVIN?** The answer sets the L1/L2 assumption for every worked example in 04–07.
