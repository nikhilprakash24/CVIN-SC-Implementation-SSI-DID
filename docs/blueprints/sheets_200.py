"""200-series: assemblies (the W3C SSI layer and MOBI VID)."""
from bplib import *  # noqa: F401,F403
from data import D, raw, lens1, lens2  # noqa: E402  (P2: every measured value comes from data.py)


def bp201():
    s = Sheet("BP-201", "DID resolution assembly", "Schematic: did:ethr identifier → event-log walk → W3C DID Core document; four methods, one resolver",
              notes=["Resolution is offline/local for the address-bearing methods; caching amortises repeats. In-process M0 cold resolve: " + D("m0.resolve.ethr.cold") + " ms median (docs/figures/resolution_latency_M0.json; no register row).",
                     "Over HTTP RPC (M1-H/HTTP), at history h = 50 the ERC-1056 walk takes " + D("http.r3.erc1056.h50") + " ms median, over the J2945/1 budget (#39; descriptive only, never compared with the in-process run) — the reason BP-302 caches.",
                     "External W3C DID test suite: " + D("w3c.ext") + " generated tests (#24; never compare with the old /441 denominator); internal checker " + D("w3c.score") + " (#4). Documents carry @context, verificationMethod (EcdsaSecp256k1VerificationKey2019, blockchainAccountId) and the relationships."],
              parts=[(1, "DIDResolver.resolve(did)", "entry; returns DIDResolutionResult {didDocument, didResolutionMetadata, didDocumentMetadata}"),
                     (2, "method dispatch", "did:ethr → ERC-1056 · did:nft → ERC-721 · did:key → ERC-725 · did:mobi → MOBI VID"),
                     (3, "changed[did] read", "1 SLOAD / eth_call: head of the linked list (BP-103 ②)"),
                     (4, "eth_getLogs per hop", "filter identity + block = previousChange; hops = number of changes"),
                     (5, "document builder", "owner → controller; delegates → verificationMethod + authentication; attributes → service / keys"),
                     (6, "validity filter", "validTo > latest block timestamp; revoked (validTo = 0) dropped"),
                     (7, "cache", "did → (document, block); refreshed by a changed() probe (BP-302 freshness-k)"),
                     (8, "resolution metadata", "contentType, error (invalidDid / notFound / methodNotSupported)")],
              parts_width=760,
              refs=["2_w3c-ssi-layer/did-resolution/did_resolver.py (_resolve_ethr/_resolve_nft/_resolve_key/_resolve_mobi)", "docs/conformance/W3C_DID_TEST_SUITE.md (#24) · docs/figures/resolution_latency_M0.json",
                    "1_blockchain-identity/benchmarks/scenarios/resolve.js (L6 read path: RPC calls, bytes, ms)"])
    # pipeline left→right
    x, y = 560, 170
    s.section_label(x, y, "SCHEMATIC — RESOLUTION PIPELINE (did:ethr path drawn; other methods substitute ③④ with view calls)")
    stages = [("did:ethr:0x1:0xAB…", "identifier", 1), ("parse + dispatch", "method, chainId, address", 2), ("changed(id)", "head block", 3), ("getLogs ×h", "walk previousChange", 4),
              ("build document", "controller / keys / services", 5), ("validity filter", "TTL, revocations", 6), ("DID document", "+ metadata ⑧", 8)]
    xx = x
    for i, (t, sub, n) in enumerate(stages):
        w = 128
        on = n in (3, 4)
        s.rect(xx, y + 20, w, 58, sw=1.8, fill=GROUND_DK if on else "none", dash=None if on else None)
        s.wrap(xx + w / 2, y + 42, t, width_chars=18, size=10, lh=12, anchor="middle", mono=True, color=LINE)
        s.text(xx + w / 2, y + 70, sub, size=8, anchor="middle", mono=True, color=LINE_SOFT)
        s.balloon(n, xx + w - 8, y + 12, r=10)
        if i < len(stages) - 1:
            s.arrow(xx + w, y + 49, xx + w + 14, y + 49, head=6)
        xx += w + 14
    s.line(x + 290, y + 90, x + 560, y + 90, stroke=ACCENT, sw=1.2)
    s.text(x + 425, y + 104, "on-chain reads (the only part that touches the ledger)", size=9, anchor="middle", color=ACCENT, mono=True)
    # cache loop
    s.elbow(x + 6 * 142 + 64, y + 78, x + 6 * 142 + 64, y + 130, head=False)
    s.rect(x + 6 * 142 - 40, y + 130, 208, 34, sw=1.6, dash="6,4"); s.text(x + 6 * 142 + 64, y + 152, "cache ⑦ (did → document)", size=10, anchor="middle", mono=True)
    s.elbow(x + 6 * 142 - 40, y + 147, x + 70, y + 147, head=False); s.arrow(x + 70, y + 147, x + 70, y + 82, head=7)
    s.text(x + 90, y + 160, "hit: 0 RPC, ≈0.4 ms verify (BP-302); miss: 1 + h RPC (10.5 ms at h≈4, #32)", size=9, mono=True, color=LINE_SOFT)
    # method table
    tx, ty = 560, 360
    s.section_label(tx, ty, "METHOD TABLE — FOUR DID METHODS, ONE RESOLVER ②")
    rows = [("did:ethr", "did:ethr:<chainId>:<address>", "ERC-1056 event walk", "any EOA; no creation tx"),
            ("did:nft", "did:nft:<chainId>:<contract>:<tokenId>", "ERC-721 ownerOf / tokenURI / metadata", "token holder = controller"),
            ("did:key", "did:key:<chainId>:<address>", "ERC-725 getKeys / getKey", "contract per identity"),
            ("did:mobi", "did:mobi:<VIN>  (testbed form)", "MOBI VID registry; VID-I uses did:ethr so the id never carries the VIN", "see BP-204 note")]
    s.table(tx, ty + 14, [("METHOD", 90), ("IDENTIFIER FORM", 300), ("BACKED BY", 400), ("NOTE", 190)], rows, size=10, lh=22)
    # document anatomy
    dx, dy = 560, 500
    s.section_label(dx, dy, "DETAIL A — DOCUMENT ANATOMY (DID Core v1.0) AND WHERE EACH FIELD COMES FROM")
    rows = [("@context", "https://www.w3.org/ns/did/v1", "constant"), ("id", "did:ethr:<chainId>:<address>", "input"), ("controller", "identityOwner(id)", "① ③ owners map"),
            ("verificationMethod[]", "EcdsaSecp256k1VerificationKey2019 + blockchainAccountId", "owner key + valid delegates ⑥"), ("authentication / assertionMethod", "references into verificationMethod", "delegateType sigAuth / veriKey"),
            ("service[]", "from did/svc/* attributes", "DIDAttributeChanged ④"), ("(did/vp/<hash>)", "presentation anchor P1", "BP-203 / BP-104 F8")]
    s.table(dx, dy + 14, [("FIELD", 200), ("VALUE", 420), ("SOURCE", 300)], rows, size=10, lh=21)
    return s


def bp202():
    s = Sheet("BP-202", "Verifiable credential — structure and verify pipeline", "VC Data Model 2.0 with an Ethereum-native securing mechanism; six IDEF0 stages from envelope to verdict",
              notes=["Proof: DataIntegrityProof, cryptosuite eip191-secp256k1-recovery-2024 — EIP-191 personal-sign over deterministic canonical JSON. The signing key is the key that controls the issuer's on-chain identity.",
                     "Verification is offline: secp256k1 public-key recovery, no chain round-trip (the V2V requirement). Warm verify " + D("v2v.ssi.warm") + " ms [" + D("v2v.ssi.warm.lo") + ", " + D("v2v.ssi.warm.hi") + "], cold " + D("v2v.ssi.cold") + " ms (#27).",
                     "Negative checks are first-class: forged proof, tampered disclosure, wrong challenge, expired, revoked — all fail (28 tests + review-02 negatives). Documented deviations: canonical JSON (not URDNA2015), thesis-defined cryptosuite."],
              parts=[(1, "@context / type", "VerifiableCredential + one of 10 automotive types (vc_schemas.py)"),
                     (2, "issuer", "did:ethr derived from the issuer key (CredentialIssuer.with_ethr_did)"),
                     (3, "credentialSubject", "id = subject DID; claimDigests (salted, BP-203) — never raw claims in the signed VC"),
                     (4, "validFrom / validUntil", "birth certificates do not expire; others validity_days"),
                     (5, "credentialSchema", "one of 10 schemas: BirthCertificate, OwnershipTransfer, InsuranceClaim, Maintenance, Recall, Theft, Registration, Decommission, V2VSafety, Emissions"),
                     (6, "credentialStatus", "RevocationRegistry (memory / JSON file); MOBI VID adds the on-chain anchor"),
                     (7, "proof", "DataIntegrityProof · proofPurpose assertionMethod · verificationMethod · proofValue"),
                     (8, "disclosures", "envelope side-car: (claim, salt) pairs the holder may reveal")],
              parts_width=760,
              refs=["2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py, vc_holder.py, vc_verifier.py, vc_schemas.py", "tests/test_vc_layer.py (28), test_review02_negative.py, test_s3_key_binding.py",
                    "cv2x-testbed/scripts/w3c_compliance_checker.py — " + D("w3c.score") + " (" + D("w3c.checks") + " checks: " + D("w3c.pass") + " PASS, " + D("w3c.partial") + " PARTIAL, " + D("w3c.fail") + " FAIL) #4"])
    # structure (left of centre)
    x, y = 560, 150
    s.section_label(x, y, "STRUCTURE — THE SIGNED ENVELOPE")
    fields = [("@context, type", 1), ("issuer: did:ethr:…", 2), ("credentialSubject { id, claimDigests[] }", 3), ("validFrom / validUntil", 4), ("credentialSchema", 5), ("credentialStatus", 6), ("proof { DataIntegrityProof }", 7)]
    s.rect(x, y + 16, 380, 20 + 30 * len(fields), sw=2.2)
    for i, (f, n) in enumerate(fields):
        yy = y + 30 + i * 30
        s.rect(x + 10, yy, 330, 24, sw=1.2, fill=GROUND_DK if n == 7 else "none")
        s.text(x + 18, yy + 16, f, size=10, mono=True)
        s.balloon(n, x + 360, yy + 12, r=10)
    s.rect(x, y + 16 + 20 + 30 * len(fields) + 8, 380, 28, sw=1.4, dash="6,4"); s.text(x + 18, y + 16 + 20 + 30 * len(fields) + 27, "disclosures[] (not signed; side-car)", size=10, mono=True, color=LINE_SOFT)
    s.balloon(8, x + 360, y + 16 + 20 + 30 * len(fields) + 22, r=10)
    s.dim(x + 390, y + 30, x + 390, y + 30 + 30 * len(fields) - 6, "signed bytes = canonical JSON of ①–⑥", off=4)
    # IDEF0 pipeline (right)
    px, py = 1010, 150
    s.section_label(px, py, "IDEF0 — SIX-STAGE VERIFY PIPELINE (any FAIL short-circuits to reject)")
    stages = [("1 structure", "required fields, types, context", "—"), ("2 schema", "credentialSchema ⑤ vs claims", "vc_schemas"), ("3 temporal", "validFrom ≤ now ≤ validUntil", "clock"),
              ("4 revocation", "credentialStatus ⑥ in registry?", "RevocationRegistry"), ("5 signature", "ecrecover(EIP-191(canonical)) == issuer key", "secp256k1 / DID key"), ("6 disclosure", "recompute hash(salt‖claim) == digest", "disclosures ⑧")]
    for i, (t, inp, ctrl) in enumerate(stages):
        yy = py + 18 + i * 74
        s.rect(px + 60, yy, 300, 52, sw=1.8, fill=GROUND_DK if i == 4 else "none")
        s.text(px + 70, yy + 20, t, size=12, weight="bold")
        s.text(px + 70, yy + 38, inp, size=9, mono=True, color=LINE_SOFT)
        # control from top, mechanism from bottom (IDEF0)
        s.arrow(px + 400, yy + 26, px + 360, yy + 26, head=6, stroke=LINE_SOFT); s.text(px + 406, yy + 30, ctrl, size=9, mono=True, color=LINE_SOFT)
        if i < len(stages) - 1:
            s.arrow(px + 210, yy + 52, px + 210, yy + 72, head=7)
            s.text(px + 220, yy + 66, "OK", size=9, color=OK, mono=True)
        s.arrow(px + 60, yy + 26, px + 30, yy + 26, head=6, stroke=WARN); s.text(px + 24, yy + 30, "FAIL", size=9, anchor="end", color=WARN, mono=True)
    s.rect(px + 110, py + 18 + 6 * 74, 200, 30, sw=2.0, stroke=OK); s.text(px + 210, py + 18 + 6 * 74 + 20, "VerificationResult ok", size=11, anchor="middle", color=OK, mono=True)
    s.text(px, py + 18 + 6 * 74 + 56, "report['credentials'][i]['checks'] → {structure, schema, temporal, revocation, signature, disclosure}", size=9, mono=True, color=LINE_SOFT)
    return s


def bp203():
    s = Sheet("BP-203", "Selective disclosure and presentation", "SD-JWT-style salted digests; presentation bound to challenge (replay) and domain (audience)",
              notes=["The signed VC carries only claimDigests = hash(salt ‖ claim). The holder reveals chosen (claim, salt) pairs; the verifier recomputes each digest against the signed list.",
                     "A presentation binds challenge (NonceStore, ttl 300 s, consumed once) and domain; proofPurpose authentication; verify_presentation(vp, challenge, domain).",
                     "F8 createPresentation has no native ERC primitive; P1 anchors a nonce-keyed presentation hash on-chain where the holder has a write path (BP-104)."],
              parts=[(1, "claimDigests[]", "per claim: hash(salt32 ‖ canonical(claim)); order-independent"),
                     (2, "disclosures", "holder-held (claim, salt) side-car; subset chosen per verifier"),
                     (3, "HolderWallet", "store_credential(envelope) → cid; create_presentation([cid], challenge, domain)"),
                     (4, "VerifiablePresentation", "holder DID, verifiableCredential[], proof{challenge, domain, proofPurpose authentication}"),
                     (5, "NonceStore", "issue() → nonce; consume(nonce) once within ttl (replay)"),
                     (6, "domain", "audience binding: a VP for dmv.gov.bc.ca is rejected by an insurer"),
                     (7, "P1 anchor (optional)", "setAttribute(did, keccak('did/vp/'‖hash), hash, 300 s) — replay-protected by key")],
              parts_width=700,
              refs=["2_w3c-ssi-layer/verifiable-credentials/vc_holder.py, vc_verifier.py (NonceStore, verify_presentation)", "use case 10 — autonomous-vehicle data sharing (selective disclosure), cv2x-testbed/scripts/test_use_cases.py",
                    "docs/CVIN-DATA-COLLECTION-FRAMEWORK.md §2.2c (P1)"])
    x, y = 560, 160
    s.section_label(x, y, "SCHEMATIC — ISSUE, HOLD, PRESENT, VERIFY")
    # issuer
    s.box(x, y + 20, 250, 120, "ISSUER", ["claims {vin, make, model, year…}", "salt_i ← random(32) per claim", "digest_i = hash(salt_i ‖ claim_i)  ①", "sign VC over digests only"], bsize=9)
    s.arrow(x + 250, y + 60, x + 330, y + 60, label="envelope {VC, disclosures ②}", lsize=9, head=7)
    s.box(x + 330, y + 20, 250, 120, "HOLDER WALLET ③", ["store(envelope) → cid", "choose subset S of claims", "VP = {VC, disclosures[S],", "  challenge ⑤, domain ⑥}  ④"], bsize=9)
    s.arrow(x + 580, y + 60, x + 660, y + 60, label="VP", lsize=9, head=7)
    s.box(x + 660, y + 20, 300, 120, "VERIFIER", ["challenge: fresh? consumed once ⑤", "domain == mine? ⑥", "VC pipeline (BP-202 stages 1–5)", "∀ s∈S: hash(salt_s‖claim_s) == digest_s"], bsize=9)
    s.arrow(x + 790, y + 20, x + 790, y - 20, head=False); s.text(x + 800, y - 8, "challenge issued first (verifier → holder)", size=9, mono=True, color=LINE_SOFT)
    # what the verifier learns
    lx, ly = 560, 330
    s.section_label(lx, ly, "DETAIL A — WHAT CROSSES THE WIRE VS WHAT THE VERIFIER LEARNS (use case 10)")
    rows = [("signed VC", "digests of all n claims", "nothing about undisclosed claim values"), ("disclosures[S]", "|S| (claim, salt) pairs", "exactly S, each provably in the signed set"),
            ("challenge", "nonce from verifier", "this VP was built for this request (no replay)"), ("domain", "verifier identifier", "this VP was built for this verifier (no relay)"),
            ("P1 anchor (optional)", "keccak(VP) under did/vp/<hash>", "on-chain evidence the holder presented, 300 s")]
    s.table(lx, ly + 14, [("ITEM", 170), ("CONTENT", 260), ("GUARANTEE", 470)], rows, size=10, lh=22)
    # failure modes
    fx, fy = 560, 500
    s.section_label(fx, fy, "DETAIL B — FAILURE MODES EXERCISED (all must reject)", color=WARN)
    fails = ["tampered disclosure → digest mismatch (stage 6)", "forged proof → recovered key ≠ issuer (stage 5)", "reused challenge → NonceStore.consume false",
             "wrong domain → audience mismatch", "expired / revoked VC → stages 3 / 4"]
    for i, f in enumerate(fails):
        s.rect(fx, fy + 16 + i * 26, 560, 22, sw=1.2, stroke=WARN); s.text(fx + 8, fy + 31 + i * 26, f, size=10, mono=True, color=WARN)
    s.text(fx + 580, fy + 60, "28 VC tests + review-02 negatives:", size=10, color=OK, mono=True)
    s.text(fx + 580, fy + 76, "pass/fail computed, not asserted.", size=10, color=OK, mono=True)
    return s


def bp204():
    s = Sheet("BP-204", "MOBI VID I birth certificate — VIN privacy data flow", "Data-flow diagram: what reaches the chain, what never does, what a verifier recomputes",
              notes=["Only sha256(vin ‖ ':' ‖ salt32) reaches the chain. The vehicle DID is did:ethr:<chainId>:<addr>, not did:mobi:<VIN>, so the identifier itself never leaks the VIN (G7).",
                     "AES-256-GCM key = HKDF-SHA256(owner secret, salt = vinSalt); ciphertext AEAD-bound to vinHash as associated data: it cannot be transplanted onto another record.",
                     "No IPFS anywhere: anchoring is content-hash (keccak256 of the canonical signed VC) into a contract field. MOBI-VID-V2 birth = " + D("gas.MOBI-VID-V2.createIdentity") + " gas (#25).",
                     "Key distribution and HSM custody are out of scope for the testbed (README caveats)."],
              parts=[(1, "VIN (17 chars)", "process input; never stored or emitted on-chain"),
                     (2, "vinSalt", "32 random bytes; disclosed off-chain to parties that must link VIN → vehicle"),
                     (3, "vinHash", "sha256(vin ‖ ':' ‖ salt); on-chain field"),
                     (4, "VehicleBirthCertificate VC", "schema-enforced; issuer = manufacturer DID; subject = vehicle did:ethr"),
                     (5, "contentHash", "keccak256(canonical signed VC); on-chain birthCertHash"),
                     (6, "registerBirth tx", "(vehicle, vinHash, birthCertHash, manufacturer) → MOBIVIDRegistryV2"),
                     (7, "vinSecret → key32", "HKDF; owner-held; VIN ciphertext off-chain, AAD = vinHash"),
                     (8, "BirthCertificateVerifier", "VC pipeline + keccak(VC)==birthCertHash + sha256(vin:salt)==vinHash + issuer==manufacturer")],
              parts_width=760,
              refs=["2_w3c-ssi-layer/mobi-vid/birth_certificate.py (BirthCertificateIssuer / Verifier)", "1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol · tests/test_vin_cipher.py (6)",
                    "docs/MOBI_VID_CHECKLIST.md · MOBI_VID1_TECHNICAL_SPEC.md"])
    # DFD: external entities (rect), processes (circle), stores (open rect)
    x, y = 560, 160
    s.section_label(x, y, "DFD — ISSUANCE (manufacturer side)")
    # entities
    s.rect(x, y + 30, 120, 40, sw=1.8); s.text(x + 60, y + 54, "MANUFACTURER", size=10, anchor="middle", weight="bold")
    s.rect(x, y + 230, 120, 40, sw=1.8); s.text(x + 60, y + 254, "OWNER", size=10, anchor="middle", weight="bold")
    # processes
    s.circle(x + 260, y + 50, 34, sw=1.8); s.text(x + 260, y + 47, "salt+hash", size=9, anchor="middle", mono=True); s.text(x + 260, y + 60, "② ③", size=9, anchor="middle", mono=True, color=ACCENT)
    s.circle(x + 430, y + 50, 34, sw=1.8); s.text(x + 430, y + 47, "issue VC", size=9, anchor="middle", mono=True); s.text(x + 430, y + 60, "④", size=9, anchor="middle", mono=True, color=ACCENT)
    s.circle(x + 600, y + 50, 34, sw=1.8); s.text(x + 600, y + 47, "keccak", size=9, anchor="middle", mono=True); s.text(x + 600, y + 60, "⑤", size=9, anchor="middle", mono=True, color=ACCENT)
    s.circle(x + 260, y + 250, 34, sw=1.8); s.text(x + 260, y + 247, "HKDF+GCM", size=9, anchor="middle", mono=True); s.text(x + 260, y + 260, "⑦", size=9, anchor="middle", mono=True, color=ACCENT)
    # flows
    s.arrow(x + 120, y + 50, x + 226, y + 50, label="VIN ①", lsize=9, head=6, dash="4,3")
    s.arrow(x + 294, y + 50, x + 396, y + 50, label="vinHash", lsize=9, head=6)
    s.arrow(x + 464, y + 50, x + 566, y + 50, label="signed VC", lsize=9, head=6, dash="4,3")
    s.arrow(x + 120, y + 250, x + 226, y + 250, label="owner secret", lsize=9, head=6, dash="4,3")
    s.arrow(x + 260, y + 84, x + 260, y + 216, label="VIN, salt", lsize=9, head=6, dash="4,3")
    # stores
    s.line(x + 760, y + 20, x + 760, y + 300, stroke=ACCENT, sw=1.6, dash="12,6")
    s.text(x + 770, y + 14, "◄ off-chain | on-chain ►", size=9, color=ACCENT, mono=True)
    s.rect(x + 790, y + 30, 230, 100, sw=2.2, fill=GROUND_DK); s.text(x + 800, y + 50, "MOBIVIDRegistryV2 ⑥", size=11, weight="bold")
    s.lines(x + 800, y + 70, ["vehicle: address (did:ethr)", "vinHash: bytes32 ③", "birthCertHash: bytes32 ⑤", "manufacturer: address"], size=9, lh=14, mono=True, color=LINE_SOFT)
    s.arrow(x + 634, y + 50, x + 790, y + 50, label="contentHash", lsize=9, head=6)
    s.arrow(x + 294, y + 34, x + 790, y + 80, head=6, stroke=LINE_SOFT)
    s.rect(x + 420, y + 220, 300, 60, sw=1.4, dash="6,4"); s.text(x + 430, y + 240, "OFF-CHAIN STORE (holder / parties)", size=10, weight="bold", color=LINE_SOFT)
    s.text(x + 430, y + 258, "signed VC ④ · disclosures · vinSalt ② · VIN ciphertext ⑦", size=9, mono=True, color=LINE_SOFT)
    s.arrow(x + 294, y + 250, x + 420, y + 250, label="ciphertext (AAD=vinHash)", lsize=9, head=6, dash="4,3")
    s.arrow(x + 464, y + 84, x + 500, y + 220, head=6, dash="4,3")
    # verifier
    vx, vy = 560, 520
    s.section_label(vx, vy, "DFD — VERIFICATION ⑧ (any party holding VC + salt; the chain supplies the anchors)")
    checks = [("VC pipeline", "BP-202 stages 1–6"), ("keccak(VC) == birthCertHash", "anchor integrity"), ("sha256(vin:salt) == vinHash", "VIN binding (salt disclosed)"), ("VC.issuer == manufacturer", "issuer consistency")]
    xx = vx
    for t, sub in checks:
        s.rect(xx, vy + 18, 230, 48, sw=1.6, stroke=OK); s.text(xx + 115, vy + 38, t, size=10, anchor="middle", mono=True, color=OK); s.text(xx + 115, vy + 56, sub, size=9, anchor="middle", color=LINE_SOFT)
        xx += 246
    s.text(vx, vy + 90, "Passive on-chain observer (A4) sees: an address, two hashes, a manufacturer address. Not the VIN, not the salt, not the key (G7 — MOBI family only, security_matrix privacy column).", size=10, mono=True, color=ACCENT)
    return s


def bp205():
    s = Sheet("BP-205", "MOBI VID II lifecycle event and on-chain attestation", "Detail of recordLifecycleEvent / attestEvent and the found-and-fixed signature gap (#28)",
              notes=["11 event types × 9 issuer roles (NONE + 8); the contract gates which role may record which type (allowedIssuers). Types with a schema are issued strict; the rest are still signed and verifiable.",
                     "Found-and-fixed (review 02): attestEvent stored a signature but never verified it (a G2/G3 violation). It now recovers the signer over a domain-separated digest and requires signer == attester; forged and replayed attestations revert.",
                     "Cost of the fix is reported as evidence: " + D("attest.before") + " → " + D("attest.july") + " gas on the July build; " + D("attest.now") + " receipt gas (" + D("attest.exec") + " execution) on the current build (#28). The MOBI Replay cell now passes."],
              parts=[(1, "EventType enum", "MAINTENANCE REPAIR ACCIDENT RECALL INSPECTION MODIFICATION THEFT_REPORT RECOVERY INSURANCE_CLAIM REGISTRATION DECOMMISSION"),
                     (2, "IssuerRole enum", "MANUFACTURER DEALER SERVICE_CENTER INSPECTION_STATION GOVERNMENT_DMV INSURANCE_COMPANY POLICE OWNER"),
                     (3, "LifecycleEvent struct", "eventId, type, issuer, timestamp, dataHash (= keccak of the event VC), odometer…"),
                     (4, "recordLifecycleEvent", "onlyAuthorizedIssuer(type) → push eventId; LifecycleEventRecorded"),
                     (5, "attestation digest", "keccak256(address(this), chainId, vehicle, eventId) — EIP-191 prefixed"),
                     (6, "attestEvent", "ecrecover(digest, sig) == attester else revert; EventAttested"),
                     (7, "LifecycleEventRecorder (py)", "issues event VC + anchors in one call; enums mirror the contract exactly"),
                     (8, "VehicleHistoryAggregator", "rebuilds verified history: anchor integrity + signature recovery + issuer consistency + odometer-rollback heuristic")],
              parts_width=820,
              refs=["1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol (attestEvent, _initializeAllowedIssuers)", "2_w3c-ssi-layer/mobi-vid/lifecycle_events.py · test/MOBIVID/attestEventRegression.test.js",
                    "docs/REVIEW_02_CODEBASE.md · docs/AFTER_ACTION_REPORT_06.md (attestEvent restriction)"])
    x, y = 560, 150
    s.section_label(x, y, "DETAIL A — attestEvent BEFORE AND AFTER (the gap and the barrier)")
    # before
    s.rect(x, y + 18, 440, 120, sw=1.6, stroke=WARN)
    s.text(x + 10, y + 38, "BEFORE (gap)", size=12, weight="bold", color=WARN)
    s.lines(x + 10, y + 58, ["attestEvent(vehicle, eventId, sig):", "  store EventAttestation{attester, sig}", "  — no recovery, no check —", "any bytes accepted as 'signature'; replay across vehicles possible"], size=9, lh=14, mono=True, color=WARN)
    s.text(x + 430, y + 130, "" + D("attest.before") + " gas", size=10, anchor="end", mono=True, color=WARN)
    # after
    s.rect(x + 480, y + 18, 480, 120, sw=1.8, stroke=OK, fill=GROUND_DK)
    s.text(x + 490, y + 38, "AFTER (fixed; G2 + G3)", size=12, weight="bold", color=OK)
    s.lines(x + 490, y + 58, ["digest = keccak256(address(this), block.chainid, vehicle, eventId)  ⑤", "signer  = ecrecover(EIP191(digest), v, r, s)", "require(signer == attester && isAuthorized(attester))  ⑥", "forged → revert · replayed on another vehicle/chain/registry → revert"], size=9, lh=14, mono=True, color=OK)
    s.text(x + 950, y + 130, "" + D("attest.july") + " July · " + D("attest.now") + " now #28", size=10, anchor="end", mono=True, color=ACCENT)
    s.arrow(x + 440, y + 78, x + 480, y + 78, head=7, stroke=ACCENT)
    # sequence mini
    sx, sy = 560, 310
    s.section_label(sx, sy, "DETAIL B — ONE LIFECYCLE EVENT, ISSUED AND ATTESTED (SV-10c excerpt)")
    cols = [("SERVICE CENTRE", sx + 80), ("RECORDER ⑦", sx + 330), ("REGISTRY V2", sx + 600), ("ATTESTER (e.g. DMV)", sx + 870)]
    for name, cx in cols:
        s.lifeline(cx, sy + 16, sy + 230, name, w=150)
    yy = sy + 76
    s.msg(sx + 80, sx + 330, yy, 1, "record_event(type, claims)"); yy += 32
    s.msg(sx + 330, sx + 330, yy, 2, "issue event VC; dataHash = keccak(VC)", self_call=True); yy += 50
    s.msg(sx + 330, sx + 600, yy, 3, "recordLifecycleEvent(vehicle, type, dataHash) ④", note="role gate: allowedIssuers[type]"); yy += 30
    s.msg(sx + 870, sx + 870, yy, 4, "sign EIP191(digest ⑤) off-chain", self_call=True, left=True); yy += 40
    s.msg(sx + 870, sx + 600, yy, 5, "attestEvent(vehicle, eventId, sig) ⑥", note="ecrecover == attester, else revert"); yy += 30
    # event / role matrix (compact)
    mx, my = 560, 580
    s.section_label(mx, my, "DETAIL C — ROLE GATE (who may record which type; contract _initializeAllowedIssuers)")
    rows = [("MAINTENANCE / REPAIR / MODIFICATION", "SERVICE_CENTER, DEALER, MANUFACTURER"), ("INSPECTION", "INSPECTION_STATION, GOVERNMENT_DMV"), ("ACCIDENT / INSURANCE_CLAIM", "INSURANCE_COMPANY, POLICE, OWNER"),
            ("RECALL", "MANUFACTURER"), ("THEFT_REPORT / RECOVERY", "POLICE, OWNER"), ("REGISTRATION / DECOMMISSION", "GOVERNMENT_DMV, DEALER")]
    s.table(mx, my + 14, [("EVENT TYPE ①", 320), ("ALLOWED ISSUER ROLES ② (as initialised; see contract for the exact list)", 560)], rows, size=10, lh=20)
    return s


SHEETS = [bp201, bp202, bp203, bp204, bp205]
