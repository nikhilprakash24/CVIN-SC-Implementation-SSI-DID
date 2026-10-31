# WP 1.3 — Primitive Cards

**Home:** Appendix G-C · **Produced:** 2026-10-24 by Explore (primitives pass)
**Scope:** one card per cryptographic/protocol primitive the `IMinimalSSI` F1–F12 set and the IDTx pattern depend on. Each card: (a) what it is, (b) protocol/algorithm, (c) why it is used here / property provided, (d) primary spec read at source (section), (e) where it appears in this repo (`FUNCTION_MAP.md` symbols), (f) alternatives and the tradeoff.

**Sourcing convention.** Section numbers and claims marked below were read at the primary source during this pass. Anything I could not verify at source is tagged **[recalled]** and must not be relied on as fact. Repo symbols cite `docs/idtx_core/p1/FUNCTION_MAP.md` (abbreviated `FM`), which in turn carries `file:line`.

---

## 1. secp256k1 ECDSA signatures (+ EIP-191 / EIP-712 domain separation)

- **(a) What it is.** The elliptic-curve digital-signature scheme Ethereum accounts use. A private key signs a 32-byte digest; `ecrecover` recovers the signer address from the `(r, s, v)` signature on chain.
- **(b) Protocol/algorithm.** ECDSA over the secp256k1 curve, signing `sign(keccak256(message))`; the signature is 65 bytes `(r, s, v)` per the Yellow Paper Appendix F, `v` carrying the EIP-155 chain id. **EIP-191** frames signed-but-not-transaction payloads as `0x19 ‖ <version byte> ‖ <version data> ‖ <data>` (version `0x00` intended-validator, `0x45`/"E" personal_sign, `0x01` → EIP-712). **EIP-712** signs typed structured data: `0x19 0x01 ‖ domainSeparator ‖ hashStruct(message)`, where `domainSeparator = hashStruct(EIP712Domain{name,version,chainId,verifyingContract,salt})`.
- **(c) Why here / property.** It is the on-chain authentication and attestation primitive: every signed write and every meta-transaction is an ECDSA signature the contract recovers. EIP-712/EIP-191 domain separation binds a signature to one contract and one chain, which is exactly the mitigation for the "cross-chain replay" threat in `ANALYSIS.md` §4.5 (chain-bound digests, idea I-08).
- **(d) Primary spec (read at source).** EIP-712 §"Specification" / §"Definition of domainSeparator" / §"Security Considerations → Replay attacks" (eips.ethereum.org/EIPS/eip-712); EIP-191 §"Specification" + version-byte registry (eips.ethereum.org/EIPS/eip-191). Curve/`(r,s,v)` format: EIP-712 references Yellow Paper Appendix F (curve name secp256k1 not stated verbatim in EIP-712 text).
- **(e) In this repo.** The signed variants throughout `FM`: ERC-1056 `changeOwnerSigned`/signed `addDelegate`/`setAttribute` (`EthereumDIDRegistry.sol:153`), ERC-4337 `validateUserOp` (`CVINVehicleAccount.sol:136`, the override; `:64` is the `IAccount` interface declaration — not a duplicate, cleared in WP 1.4), and meta-transaction op U5.
- **(e′) Limitation — `addClaim`/`attestEvent` are NOT EIP-191/712 domain-separated (examiner obj. 10).** Verified at `CVINCombinedIdentity.sol`: `addClaim` recovers a **raw keccak digest** (`_recoverRawDigest` over `_claimDigest(identity, topic, data)`), which binds `address(this)` (contract) but **not the chain id** and carries **no nonce/expiry**. So these two carried-signature paths — which are half of the measured "true IDTx" — have the cross-chain replay exposure (D52, `ANALYSIS.md` §4.5) that EIP-712 would close, and an older never-revoked claim can be re-anchored. Domain separation as described in (b)–(c) applies to the EIP-712/191 paths, **not** to `addClaim`/`attestEvent` as currently written.
- **(f) Alternatives / tradeoff.** Ed25519 (faster, no `ecrecover` in EVM — needs a precompile or expensive verification); BLS (aggregatable, pairing cost); secp256r1/P-256 (EIP-7212 precompile, aligns with WebAuthn/mDL but newer). secp256k1 ECDSA is chosen because `ecrecover` is a native EVM precompile — on-chain verification is cheap and universal.

---

## 2. Ethereum DID method / `did:ethr` + ERC-1056 event-sourced resolution

- **(a) What it is.** A DID method whose identifier is an Ethereum address (or compressed secp256k1 key), resolved against the ERC-1056 `EthereumDIDRegistry`. No on-chain creation step: every account is a DID by default.
- **(b) Protocol/algorithm.** ERC-1056 stores only the latest-change block per identity (`changed` mapping) and emits `DIDOwnerChanged` / `DIDDelegateChanged` / `DIDAttributeChanged`, each carrying a `previousChange` block pointer. A resolver walks the `previousChange` chain backward and replays events to rebuild the DID document (owner → `#controller`, delegates → `authentication`/`assertionMethod`, attributes → keys/services). `did:ethr` maps address delegates to `EcdsaSecp256k1RecoveryMethod2020` verification methods.
- **(c) Why here / property.** This is the identity substrate under the whole F1–F4/F9–F12 Set A. The event-sourced model is precisely the "L1 event log" locus of `ANALYSIS.md` §2: cheap writes (8 SSTOREs over a 17-event lifecycle, #49), reads that grow with history (112 RPC calls at h=50, #31). ERC-1056 exposing **no attribute-value read function** is the "AR-1 read limitation" that motivates the IDTx commitment store.
- **(d) Primary spec (read at source).** ERC-1056: §"Identity ownership", §"Delegate management", §"Attribute management", §"Events", §"Efficient lookup of events through linked identity events" (eips.ethereum.org/EIPS/eip-1056; marked *Stagnant*). `did:ethr`: §"Relationship to ERC1056", §"CRUD Operation Definitions → Read (Resolve) → Enumerating Contract Events" (decentralized-identity/ethr-did-resolver did-method-spec.md).
- **(e) In this repo.** `FM` F:createDID / resolve / changeOwner / delegate / attribute rows: `CVINVehicleDIDRegistry.sol:156` createVehicleDID, `EthereumDIDRegistry.sol:105` identityOwner / `:136` changeOwner / `:190` addDelegate / `:314` setAttribute; R3 document rebuilt off `eth_getLogs` (`erc1056.adapter.js:89`); AR-1 at `idtx.test.js:138`.
- **(f) Alternatives / tradeoff.** `did:key` (no registry, no rotation/revocation), `did:web` (DNS/HTTPS trust, mutable, centralized), `did:pkh`/`did:ion` (BTC/sidetree). `did:ethr`+ERC-1056 is chosen for on-chain, contract-readable controller/delegate state and key rotation without a central operator; the cost is history-growing resolution and no native privacy.

---

## 3. W3C DID Core 1.0 (identifier + DID-document model)

- **(a) What it is.** The abstract data model for decentralized identifiers: the `did:method:id` syntax and the DID document (verification methods, verification relationships, services).
- **(b) Protocol/algorithm.** Not an algorithm — a data model and a resolution contract. A DID resolves to a DID document; verification methods (public keys) are referenced by verification relationships (`authentication`, `assertionMethod`, `keyAgreement`, …) that say what each key may do.
- **(c) Why here / property.** It is the interoperability target: every substrate's R3 "full document" output is a DID-Core document, so ten heterogeneous contracts are compared against one model. It supplies the vocabulary (controller, verification method, service) the `did:ethr` resolver emits and the W3C DID test suite (335/336, register #24) checks.
- **(d) Primary spec (read at source).** W3C DID Core 1.0, **W3C Recommendation 19 July 2022**: §3.1 DID Syntax; §4 Data Model; §5.1.1 DID Subject; §5.2 Verification Methods; §5.3 Verification Relationships (5.3.1 Authentication, 5.3.2 Assertion, 5.3.3 Key Agreement); §5.4 Services; §7.1 DID Resolution (w3.org/TR/did-core/).
- **(e) In this repo.** `FM` resolve rows (R3 document, CONF:65/92); the external W3C DID test-suite pass noted in `BASIC_ID_SET_EXTENSION.md` §3 (register #24) and the Python W3C checker (94.3%).
- **(f) Alternatives / tradeoff.** Bare X.509/PKIX identity (no self-describing document, no relationship model); plain Ethereum address with off-chain metadata (no standard resolution). DID Core is chosen for cross-substrate comparability; the cost is an abstract layer that each substrate must synthesize (several have no native document and rebuild it in the adapter).

---

## 4. W3C Verifiable Credentials Data Model 2.0 (issue / verify / present; proofs)

- **(a) What it is.** The data model for verifiable credentials (VCs) and verifiable presentations (VPs): issuer-signed claims about a subject, and holder-assembled presentations of them.
- **(b) Protocol/algorithm.** A credential carries `issuer`, `credentialSubject`, optional `credentialStatus`, secured by a *securing mechanism* — either an embedded Data Integrity proof or an enveloping JOSE/COSE (e.g. SD-JWT) proof. Roles: issuer → holder → verifier. The VC itself is signed off-chain; only its anchor lives on chain here.
- **(c) Why here / property.** It is the Set B (F5–F8) credential model. The repo splits it per the L4 locus (`ANALYSIS.md` §2): the signed VC stays off chain in `2_w3c-ssi-layer`, while the issuer key (V1) and status (V3) are anchored on chain, and the carried issuer signature is verified in-transaction by `addClaim`/`attestEvent`. F8 `createPresentation` has **no native ERC** — realised as a replay-protected on-chain anchor (the canon's structural finding).
- **(d) Primary spec (read at source).** W3C VC Data Model 2.0, **W3C Recommendation 15 May 2025**: §3 Core Data Model (3.1 Claims, 3.2 Credentials, 3.3 Presentations); §4.7 Issuer; §4.8 Credential Subject; §4.10 Status; §4.12 Securing Mechanisms; §4.13 Verifiable Presentations; §1.2 Ecosystem Overview (issuer/holder/verifier roles) (w3.org/TR/vc-data-model-2.0/).
- **(e) In this repo.** `FM` issueCredential (V1+V3), verifyCredential (V6+R4), revokeCredential (V5), createPresentation (F8/P1) rows; off-chain proof check in the VC layer (register #21/#27); P1 anchor at `erc1056.adapter.js:196` et al.
- **(f) Alternatives / tradeoff.** AnonCreds (CL-signatures, ZK selective disclosure, not a W3C Rec); ISO 18013-5 mdoc (see ANALOGIES col B/C); raw JWT claims (no presentation model). VC 2.0 is chosen for the open proof-format choice and broad tooling; the cost is that the presentation/anchor split must be hand-built per substrate.

---

## 5. Credential status / revocation (Bitstring Status List; on-chain status anchor)

- **(a) What it is.** The mechanism a verifier uses to learn whether an issued credential is still valid (revoked / suspended), without contacting the issuer per check.
- **(b) Protocol/algorithm.** W3C Bitstring Status List: each credential's `credentialStatus` is a `BitstringStatusListEntry` with a `statusListIndex` and a `statusPurpose` (`revocation` irreversible, `suspension` reversible, also `refresh`/`message`); the issuer publishes a `BitstringStatusListCredential` whose `encodedList` is a ≥131,072-bit bitstring, GZIP-compressed and multibase-base64url-encoded. Verifier: dereference, verify proof, expand, read the bit at the index (0 = valid). The repo's on-chain analogue anchors status as an attribute/claim slot that a contract can read directly (L0/L3).
- **(c) Why here / property.** It gives the freshness dimension of `ANALYSIS.md`: a caching verifier accepts at most k−1 messages after a revocation (#32, #37). On-chain status (V3/V6) is directly contract-readable; the Bitstring list is the off-chain (L4) counterpart whose privacy property (verifier cannot reveal *which* credential) the on-chain anchor trades away.
- **(d) Primary spec (read at source).** W3C **Bitstring Status List v1.0**, "Privacy-preserving status information for Verifiable Credentials", **W3C Recommendation 15 May 2025** (First CR 21 May 2024): §2.1 BitstringStatusListEntry; §2.2 BitstringStatusListCredential; §3.2 Validate algorithm; §3.3/§3.4 bitstring generate/expand (w3.org/TR/vc-bitstring-status-list/). The widely-cited name "StatusList2021" was the predecessor; the 2021 date now appears only in examples.
- **(e) In this repo.** `FM` issueCredential V3 status anchor, verifyCredential V6 status check, revokeCredential V5 (e.g. `CVINVehicleCredential1155.sol:137` revokeCredential; `cvin.adapter.js:187` removeClaim + sticky `:336` revokeClaimContent); MOBI issuer-level revoke (`MOBIVIDRegistryV2.sol:200`, no per-event revoke — NOT FOUND in `FM`).
- **(f) Alternatives / tradeoff.** OCSP/CRL (PKI, see ANALOGIES col A); accumulator-based revocation (ZK, constant-size, complex); short-lived credentials (no revocation list, re-issue cost). On-chain anchor is chosen for direct contract-readability (enables IDTx); the cost is permanence and loss of the bitstring's query-privacy.

---

## 6. Salted-hash commitment (the L3 VIN-privacy pattern) — equality-only, no knowledge proof

- **(a) What it is.** A public hash of a secret plaintext (VIN) with a salt, stored on chain so a contract can bind to the value without revealing it.
- **(b) Protocol/algorithm.** `commitment = H(salt ‖ plaintext)` (keccak-256 in-EVM), registered in a commitment store. A later transaction gates an action by **equality** with a registered value ("registered-commitment validity", AR-5). It is a hiding+binding commitment only — it proves *no knowledge* of the opening.
- **(c) Why here / property.** This is the L3 locus of `ANALYSIS.md` §2 and §4.4: public binding without disclosure, equality dependencies, one slot per commitment, salt management off chain. Its crucial limit (§4.4): "a commitment is equality-only" — a knowledge or computation dependency on the hidden VIN would need the opening disclosed or a ZK proof (idea I-09). It also carries the leakage threat D64: if the identifier itself is VIN-derived, a VIN-hash dependency becomes a VIN oracle (§4.5).
- **(d) Primary spec (read at source).** No single external standard — this is a commitment-scheme pattern (hiding/binding). The authoritative statement for this repo is `ANALYSIS.md` §2 (L3 row), §4.4 ("A commitment is equality-only", AR-5), §4.5 (D64 leakage), §5 (L3 buys/costs/forbids). Keccak-256 underlies the hash (card 8). *(Commitment-scheme formalism itself: **[recalled]** — not re-read at an external source this pass.)*
- **(e) In this repo.** `FM` IDTx rows: `IdtxExecutor.sol:62` setCommitment / `:73` revokeCommitment, store `IdentityCommitments:44`; owner-only, stops counting when setter loses ownership (AR-6, `idtx.test.js:85`); MOBI `vinHash` (`ANALYSIS.md` §2 L3 instances).
- **(f) Alternatives / tradeoff.** Plaintext on chain (L0 — contract-readable, no privacy); Pedersen commitment (homomorphic, supports range proofs); ZK membership (card 7). Salted keccak commitment is chosen as the cheapest hiding binding the EVM can check by equality; the cost is that it supports *only* equality, forbidding any predicate over the hidden value.

---

## 7. Groth16 zk-SNARK (ZkVinGate ZK-VIN tier) + nullifier for one-time scoped admission

- **(a) What it is.** A succinct zero-knowledge proof that the prover knows a secret (e.g. a VIN opening / membership witness) satisfying a circuit, verified on chain in constant time, revealing nothing about the witness. A nullifier is a deterministic, one-time tag that prevents re-use within a scope.
- **(b) Protocol/algorithm.** Groth16: a pairing-based preprocessing zk-SNARK for arithmetic-circuit (QAP) satisfiability. **Proof = 3 group elements**; verification is a single pairing-product equation using 3 pairings; requires a per-circuit common reference string (trusted setup). The nullifier `= H(secret ‖ scope)` is published with the proof; a second admission in the same scope reuses the nullifier and is rejected → one-time within a scope. **Correction (examiner obj. 9):** admissions are *not* unlinkable across scopes in the built artifact — `admit` emits `Admitted(address indexed identity, …)` with the identity in clear (`ZkVinGate.sol:113`) and the same anchored `commitmentOf[identity]` is checked in every scope, so a verifier can link an identity's admissions across scopes. The nullifier hides *which VIN/year/mfr* and prevents double-admission; it does not hide *which identity*. True cross-identity unlinkability needs a Semaphore-style anonymity set, which the contract comment says is not built here.
- **(c) Why here / property.** This is the answer to the commitment's equality-only limit (card 6, idea I-09): ZkVinGate admits an identity by *knowledge* of a committed VIN without disclosing it, and the per-scope nullifier gives one-time, replay-proof scoped admission with the VIN/year/mfr hidden — the predicate-privacy property L3 cannot provide (but the admitted identity is public; see (b) correction).
- **(d) Primary spec (read at source).** Jens Groth, "On the Size of Pairing-based Non-interactive Arguments", EUROCRYPT 2016, IACR ePrint 2016/260 — abstract/construction read at source: pairing-based SNARK for arithmetic-circuit satisfiability, **"a proof is only 3 group elements"**, verification by a single pairing-product equation (3 pairings), zero-knowledge (eprint.iacr.org/2016/260). *(QAP reduction and CRS/trusted-setup detail: stated in the paper body; "QAP"/"CRS" not verbatim-confirmed in the abstract text read — treat those two labels as **[recalled]**.)*
- **(e) In this repo.** `FM` ZkVinGate rows: `ZkVinGate.sol:80` anchorCommitment (owner-only), `:86` setService, `:92` admit (scoped, nullifier, once per scope); tests `zkvin_gate.test.js:41,49,57,63`. Layer 5, outside the 10-adapter conformance gate.
- **(f) Alternatives / tradeoff.** PLONK/Halo2 (universal/updatable setup, larger proofs); Bulletproofs (no trusted setup, logarithmic size, slower verify); STARKs (transparent, post-quantum, large proofs). Groth16 is chosen for the smallest proof and cheapest on-chain verifier; the cost is a per-circuit trusted setup and a fixed circuit.

---

## 8. Keccak-256 hashing (identifier / VIN hashing)

- **(a) What it is.** The 256-bit cryptographic hash used everywhere in the EVM — for addresses, storage-slot derivation, event topics, commitments, and the VIN hash.
- **(b) Protocol/algorithm.** Keccak-256: the sponge construction over the Keccak-f[1600] permutation, as submitted to the SHA-3 competition. It differs from NIST FIPS 202 SHA3-256 **only in the padding/domain byte** (Keccak pads `0x01`, FIPS 202 SHA3 pads `0x06`), so the two produce different digests for the same input; the permutation and sponge are identical.
- **(c) Why here / property.** Collision/preimage resistance underpins the salted-hash commitment (card 6), the nullifier (card 7), the EIP-712 `hashStruct`/`domainSeparator` and EIP-191 digests (card 1), and MOBI's `vinHash`. It is the one hash the EVM exposes as a cheap primitive (`keccak256`), so every on-chain binding uses it.
- **(d) Primary spec (read at source).** Keccak vs SHA-3 padding difference confirmed via technical secondary sources (ConsenSys; cryptologie.net; mojoauth) this pass; the Ethereum Yellow Paper specifies "Keccak-256 hash function (as per the winning entry to the SHA-3 contest)". *(FIPS 202 and the original Keccak submission were **not** re-opened at source this pass — the `0x01`/`0x06` padding bytes are from secondary sources; treat the exact byte values as corroborated-secondary, verify against FIPS 202 §B.2 and the Keccak reference if cited in the thesis.)*
- **(e) In this repo.** Underlies `FM` MOBI `vinHash` / `lookupByVINHash` (`MOBIVIDRegistry.sol:506`), the IDTx commitment store (card 6), and all signed-write digests. No dedicated symbol — it is the EVM `keccak256` opcode.
- **(f) Alternatives / tradeoff.** SHA-256 (FIPS 180-4, cheaper in some HSMs, not the EVM-native word); Poseidon/MiMC (SNARK-friendly, far cheaper *inside* a circuit — relevant to card 7's ZkVinGate circuit); FIPS 202 SHA3-256 (standards-aligned but not EVM-native, different digest). Keccak-256 is chosen because it is the EVM's native hash; the tradeoff is that it is expensive inside a zk-SNARK circuit, which is why ZK tiers prefer a SNARK-friendly hash.

---

## Status
- Eight cards written, all with at least one primary source read at source this pass.
- `[recalled]` / corroborated-secondary flags: card 6 (commitment-scheme formalism), card 7 (QAP/CRS labels), card 8 (FIPS 202 padding bytes — secondary only). These must be read at FIPS 202 / the Keccak reference / the Groth16 body before the thesis states them as fact.
- Cross-refs: `FUNCTION_MAP.md` (symbols, `file:line`), `BASIC_ID_SET_EXTENSION.md` (F-set), `ANALYSIS.md` §2 (loci), §4.4–4.5 (IDTx axes/threats).
