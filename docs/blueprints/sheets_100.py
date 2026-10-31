"""100-series: primitives and engines (the anchor sheets)."""
from bplib import *  # noqa: F401,F403
from data import D, raw, lens1, lens2  # noqa: E402  (P2: every measured value comes from data.py)

CREATE_GAS = [  # register #25, re-executed 2026-10-04, M1 cancun
    ("CVIN-Combined", raw("gas.CVIN-Combined.createIdentity"), "shared registry · event log + claims"),
    ("ERC-1056", raw("gas.ERC-1056.createIdentity"), "shared registry · event log"),
    ("ERC-1155", raw("gas.ERC-1155.createIdentity"), "shared · soulbound balances"),
    ("LSP8", raw("gas.LSP8.createIdentity"), "shared collection · bytes32 token (minimal)"),
    ("MOBI-VID-V2", raw("gas.MOBI-VID-V2.createIdentity"), "application profile · birth anchor"),
    ("ERC-725", raw("gas.ERC-725.createIdentity"), "contract per identity · key map"),
    ("ERC-721", raw("gas.ERC-721.createIdentity"), "shared · token = identity, rich struct"),
    ("ERC-4337", raw("gas.ERC-4337.createIdentity"), "account per identity (minimal EntryPoint)"),
    ("ERC-735", raw("gas.ERC-735.createIdentity"), "contract per identity · claim store"),
    ("ERC-725xy", raw("gas.ERC-725xy.createIdentity"), "contract per identity · X executor + Y store"),
]


def bp101():
    s = Sheet("BP-101", "Cryptographic primitive library", "Exploded view and parts list — the parts every higher sheet is built from",
              notes=["The adversary is assumed unable to break any part on this sheet (THREAT_MODEL §2). Everything above is conditional on that.",
                     "Parts ①–⑤ are the same parts a value transfer on the same chain uses: a vehicle's claim and a $2B transfer are verified by the same ecrecover.",
                     "Parts ⑦–⑨ are application-layer additions (MOBI VID privacy); they are not inherited from the ledger."],
              parts=[(1, "keccak256", "EVM native hash; claim digests, contentHash, claimId, eventId"),
                     (2, "secp256k1 keygen", "EOA = identity; coincurve / eth-account; vehicle, issuer, owner keys"),
                     (3, "ECDSA sign (secp256k1)", "off-chain; VC proof, BSM signature, meta-tx, attestations"),
                     (4, "ecrecover", "EVM precompile 0x01, 3,000 gas; on-chain signer recovery (G1, G2)"),
                     (5, "EIP-191 envelope + EIP-155 chain id", "\\x19Ethereum Signed Message; domain + chain binding (G3)"),
                     (6, "canonical JSON", "deterministic serialisation before hashing/signing (deviation: not URDNA2015)"),
                     (7, "SHA-256 salted hash", "vinHash = sha256(vin || ':' || salt32); only this reaches chain"),
                     (8, "HKDF-SHA256", "32-byte AES key from per-vehicle owner secret, salted by vinSalt"),
                     (9, "AES-256-GCM (AEAD)", "VIN ciphertext bound to on-chain vinHash via associated data"),
                     (10, "nonce / challenge", "replay protection: registry nonce, VP challenge+domain, presentation key"),
                     (11, "time (block.timestamp)", "delegate TTL, attribute validTo, credential temporal check")],
              parts_width=720,
              refs=["1_blockchain-identity/contracts/** (④ ⑤ ① in Solidity)", "2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py, vc_verifier.py (② ③ ⑥ ⑩ ⑪)",
                    "2_w3c-ssi-layer/mobi-vid/birth_certificate.py, tests/test_vin_cipher.py (⑦ ⑧ ⑨)"])
    # exploded view: a key pair at centre, parts radiating
    cx, cy = 1000, 300
    s.circle(cx, cy, 82, sw=2.4)
    s.text(cx, cy - 8, "secp256k1", size=14, anchor="middle", weight="bold", mono=True)
    s.text(cx, cy + 12, "(sk, pk)", size=12, anchor="middle", mono=True, color=LINE_SOFT)
    s.text(cx, cy + 30, "addr=keccak(pk)[12:]", size=9, anchor="middle", mono=True, color=LINE_SOFT)
    s.balloon(2, cx + 70, cy - 70)
    # ring of parts
    ring = [(1, "keccak256", -90), (3, "ECDSA sign", -30), (4, "ecrecover", 30), (5, "EIP-191/155", 90), (10, "nonce", 150), (11, "time", 210)]
    for n, name, ang in ring:
        a = math.radians(ang)
        px, py = cx + 210 * math.cos(a), cy + 125 * math.sin(a)
        s.rect(px - 60, py - 18, 120, 36, sw=1.8, fill=GROUND_DK)
        s.text(px, py + 5, name, size=12, anchor="middle", mono=True)
        s.line(cx + 82 * math.cos(a), cy + 82 * math.sin(a), px - 60 * math.cos(a) * 1.0, py - 18 * math.sin(a) * 1.0, stroke=LINE_SOFT, sw=1.0)
        s.balloon(n, px + 70, py - 24, r=11)
    # the signing / verifying chain (what every proof on every sheet does)
    bx, by = 560, 470
    s.section_label(bx, by, "DETAIL A — THE ONE MECHANISM EVERY PROOF USES")
    steps = [("message m", "VC, BSM, claim, userOp"), ("canonical bytes", "⑥ canonical JSON / abi.encodePacked"), ("digest", "① keccak256 (or ⑤ EIP-191 prefix first)"),
             ("signature (r,s,v)", "③ sign with sk, off-chain"), ("recovered addr", "④ ecrecover(digest, v, r, s)"), ("compare", "== expected signer → accept")]
    x = bx
    for i, (t, sub) in enumerate(steps):
        s.rect(x, by + 20, 150, 56, sw=1.8, fill=GROUND_DK if i in (2, 4) else "none")
        s.text(x + 75, by + 42, t, size=11, anchor="middle", weight="bold")
        s.wrap(x + 75, by + 58, sub, width_chars=22, size=9, lh=11, anchor="middle", color=LINE_SOFT, mono=True)
        if i < len(steps) - 1:
            s.arrow(x + 150, by + 48, x + 168, by + 48, head=7)
        x += 168
    s.text(bx, by + 100, "Identical on-chain (Solidity ecrecover, 3,000 gas) and off-chain (coincurve recovery, " + D("v2v.ssi.warm") + " ms warm verify #27).", size=10, color=ACCENT, mono=True)
    # privacy sub-assembly
    px, py = 560, 585
    s.section_label(px, py, "DETAIL B — VIN PRIVACY SUB-ASSEMBLY (MOBI VID I, see BP-204)")
    s.rect(px, py + 18, 100, 34, sw=1.6); s.text(px + 50, py + 40, "VIN", size=12, anchor="middle", mono=True)
    s.rect(px + 160, py + 18, 130, 34, sw=1.6); s.text(px + 225, py + 40, "salt (32 B)", size=12, anchor="middle", mono=True)
    s.arrow(px + 100, py + 35, px + 160, py + 35, head=6)
    s.rect(px + 340, py + 18, 150, 34, sw=1.8, fill=GROUND_DK); s.text(px + 415, py + 40, "sha256 → vinHash", size=11, anchor="middle", mono=True)
    s.arrow(px + 290, py + 35, px + 340, py + 35, head=6)
    s.balloon(7, px + 500, py + 10, r=11)
    s.rect(px + 160, py + 70, 130, 34, sw=1.6); s.text(px + 225, py + 92, "owner secret", size=12, anchor="middle", mono=True)
    s.rect(px + 340, py + 70, 150, 34, sw=1.8, fill=GROUND_DK); s.text(px + 415, py + 92, "HKDF → key32", size=11, anchor="middle", mono=True)
    s.arrow(px + 290, py + 87, px + 340, py + 87, head=6)
    s.balloon(8, px + 500, py + 62, r=11)
    s.rect(px + 540, py + 40, 170, 46, sw=1.8, fill=GROUND_DK); s.text(px + 625, py + 59, "AES-256-GCM", size=11, anchor="middle", mono=True, weight="bold")
    s.text(px + 625, py + 75, "AAD = vinHash", size=10, anchor="middle", mono=True, color=LINE_SOFT)
    s.arrow(px + 490, py + 35, px + 540, py + 55, head=6); s.arrow(px + 490, py + 87, px + 540, py + 70, head=6)
    s.balloon(9, px + 720, py + 32, r=11)
    s.text(px + 540, py + 110, "to chain: vinHash only  ·  never: VIN, salt, key, secret", size=10, color=ACCENT, mono=True)
    return s


def bp102():
    s = Sheet("BP-102", "EVM primitives and the gas schedule", "What a registry operation actually spends — the metering the cost results stand on",
              notes=["Condition M1: solc 0.8.24, optimizer 200 + viaIR, evm cancun, Hardhat local; gas is deterministic for fixed calldata and pre-state (N=30, CI width 0).",
                     "Gas is dimensionless; a fiat figure needs a gas price and a token price and is deliberately not drawn (param).",
                     "The schedule explains BP-501: event-log designs pay ③ and ④, storage designs pay ①, contract-per-identity designs pay ⑥ once per vehicle."],
              parts=[(1, "SSTORE zero→non-zero", "20,000 gas class; a new slot the identity leaves behind (stateFootprint)"),
                     (2, "SSTORE non-zero→non-zero", "2,900 gas class (warm); overwrite, e.g. changed[identity]"),
                     (3, "LOG0..LOG4 (event)", "375 + 375/topic + 8/byte; the ERC-1056 attribute path"),
                     (4, "calldata", "4 gas/zero byte, 16/non-zero; part of the 21,000+ intrinsic"),
                     (5, "SLOAD", "2,100 cold / 100 warm; the read path a verifier pays"),
                     (6, "CREATE (deploy)", "32,000 + 200/code byte; contract-per-identity standards pay it per vehicle"),
                     (7, "CALL / STATICCALL", "external call; ERC-4337 EntryPoint indirection = +" + D("gas.4337.indirection") + " gas/op (#25)"),
                     (8, "ecrecover precompile", "3,000 gas; attestEvent fix " + D("attest.before") + " → " + D("attest.july") + " (July); " + D("attest.now") + " current build (#28)"),
                     (9, "msg.sender / block.timestamp", "authorization and TTL inputs; zero cost"),
                     (10, "tx intrinsic", "21,000 gas base per transaction; txCount matters (U4 on ERC-1056 = 2 tx)")],
              parts_width=700,
              refs=["docs/MEASUREMENT_CONDITIONS.md §3 (conditions), rows #25, #28, #29–#31", "docs/CVIN-DATA-COLLECTION-FRAMEWORK.md §2.3 (fields recorded per op)",
                    "1_blockchain-identity/benchmarks/lib/MetricsCollector.js"])
    # a transaction anatomy drawing
    x, y = 560, 150
    s.section_label(x, y, "DETAIL A — ANATOMY OF ONE REGISTRY TRANSACTION (setAttribute on ERC-1056, " + D("gas.ERC-1056.updateAttribute") + " gas #25; split is illustrative, E)")
    segs = [("intrinsic 21,000", 21000, 10), ("calldata", 1500, 4), ("auth: SLOAD owner", 2100, 5), ("LOG3 event", 3000, 3), ("SSTORE changed", 2900, 2), ("exec / memory", raw("gas.ERC-1056.updateAttribute") - 30500, 9)]
    total = sum(g for _, g, _ in segs)
    xx = x
    width = 860
    for name, g, n in segs:
        wseg = width * g / total
        s.rect(xx, y + 24, wseg, 44, sw=1.6, fill=GROUND_DK if n in (3, 2) else "none")
        if wseg > 60:
            s.text(xx + wseg / 2, y + 42, name, size=10, anchor="middle", mono=True)
            s.text(xx + wseg / 2, y + 58, f"{g:,}", size=10, anchor="middle", mono=True, color=ACCENT)
        s.balloon(n, xx + wseg / 2, y + 84, r=10)
        xx += wseg
    s.dim(x, y + 110, x + width, y + 110, "" + D("gas.ERC-1056.updateAttribute") + " gas total (#25, gas_benchmark.json updateAttribute); segment split = E")
    # cost classes
    cx, cy = 560, 300
    s.section_label(cx, cy, "DETAIL B — WHY THE SUBSTRATES SPREAD " + D("gas.create.spread") + " (BP-501): WHICH PRIMITIVE EACH DESIGN PAYS AT CREATE")
    rows = [("event-log registry (ERC-1056, CVIN)", "③ LOG + ② one pointer", "no new slots for attributes", "" + D("span.event") + ""),
            ("shared token / balance (1155, LSP8, 721)", "① several new slots", "struct / history arrays", "" + D("span.shared") + ""),
            ("contract per identity (725, 735, 725xy)", "⑥ CREATE per vehicle + ①", "code bytes × 200 + storage", "" + D("span.contract") + ""),
            ("account abstraction (4337)", "⑥ CREATE + ⑦ CALL per op", "EntryPoint indirection", "" + D("span.4337") + " (+" + D("gas.4337.indirection") + "/op)")]
    s.table(cx, cy + 14, [("DESIGN FAMILY", 300), ("PRIMITIVE PAID", 220), ("STATE LEFT BEHIND", 220), ("CREATE GAS #25", 140)], rows, size=10, lh=22)
    # gas schedule mini-table
    gx, gy = 560, 450
    s.section_label(gx, gy, "DETAIL C — SCHEDULE (cancun), THE CONSTANTS BEHIND EVERY MEASURED CELL")
    rows = [("SSTORE 0→x", "20,000"), ("SSTORE x→y (warm)", "2,900"), ("SLOAD cold / warm", "2,100 / 100"), ("LOG base / topic / byte", "375 / 375 / 8"),
            ("calldata byte 0 / ≠0", "4 / 16"), ("CREATE base + per byte", "32,000 + 200"), ("ecrecover", "3,000"), ("tx intrinsic", "21,000")]
    s.table(gx, gy + 14, [("OPCODE / ITEM", 260), ("GAS", 140)], rows, size=10, lh=20)
    s.text(gx + 420, gy + 60, "These constants are the EVM's, not the thesis's.", size=11, color=LINE_SOFT)
    s.text(gx + 420, gy + 80, "They are the same for a value transfer and for a", size=11, color=LINE_SOFT)
    s.text(gx + 420, gy + 100, "vehicle identity: the ledger does not know the difference.", size=11, color=LINE_SOFT)
    s.text(gx + 420, gy + 130, "Exact where the EVM is exact; statistical where it is not", size=11, color=ACCENT)
    s.text(gx + 420, gy + 148, "(latency: N=30, median, p95). Framework §0 rule 3.", size=11, color=ACCENT)
    return s


def bp103():
    s = Sheet("BP-103", "ERC-1056 registry — section through the engine", "EthereumDIDRegistry: three storage maps, three events, one linked list, one nonce",
              notes=["Every address is an identity; creation is implicit (no transaction). Owner defaults to self when owners[id] == 0x0.",
                     "Attributes are never stored — only emitted. The resolver (BP-201) rebuilds the document by walking changed → previousChange.",
                     "Signed variants bind (0x19, 0x00, this, nonce[owner], identity, name, …) and increment the nonce: replay-proof meta-transactions (U5)."],
              parts=[(1, "owners[identity]", "mapping address→address; explicit override only"),
                     (2, "changed[identity]", "block number of last DID event — head of the linked list"),
                     (3, "nonce[owner]", "meta-tx replay counter (signed functions)"),
                     (4, "delegates[id][type][addr]", "validity expiry timestamp; validDelegate = expiry > now"),
                     (5, "DIDOwnerChanged", "(identity, owner, previousChange)"),
                     (6, "DIDDelegateChanged", "(identity, delegateType, delegate, validTo, previousChange)"),
                     (7, "DIDAttributeChanged", "(identity, name, value, validTo, previousChange) — value is event-only"),
                     (8, "onlyOwner(identity, actor)", "actor == identityOwner(identity) — the G1 barrier"),
                     (9, "ecrecover (signed paths)", "signer == identityOwner; nonce++ (G3)"),
                     (10, "block.timestamp", "validTo = now + validity for ④ and ⑦")],
              parts_width=640,
              refs=["1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol", "CVINVehicleDIDRegistry.sol (VIN wrapper: createVehicleDID, " + D("gas.vinbound.createVehicleDID") + " gas #6)",
                    "create " + D("gas.ERC-1056.createIdentity") + " · setAttribute " + D("gas.ERC-1056.updateAttribute") + " · addDelegate " + D("gas.ERC-1056.addDelegateOrClaim") + " · changeOwner " + D("gas.ERC-1056.transferOwnership") + " (all #25)"])
    # engine block: storage on left, functions middle, events right
    x, y = 480, 150
    s.section_label(x, y, "SECTION A-A — STORAGE")
    st = [("owners", "address → address", 1), ("changed", "address → uint", 2), ("nonce", "address → uint", 3), ("delegates", "addr→bytes32→addr→uint", 4)]
    for i, (n, t, b) in enumerate(st):
        yy = y + 20 + i * 54
        s.rect(x, yy, 230, 44, sw=2.0, fill=GROUND_DK)
        s.text(x + 10, yy + 18, n, size=12, weight="bold", mono=True)
        s.text(x + 10, yy + 35, t, size=10, mono=True, color=LINE_SOFT)
        s.balloon(b, x + 215, yy + 10, r=10)
    fx = x + 300
    s.section_label(fx, y, "FUNCTIONS (12: 6 direct + 6 signed)")
    fn = [("identityOwner / validDelegate", "view", ["① / ④"]), ("changeOwner(Signed)", "U1 / U4", ["⑧⑨ → ① ② ⑤"]), ("addDelegate(Signed)", "U2 / V1", ["⑧⑨ → ④ ② ⑥"]),
          ("revokeDelegate(Signed)", "D1", ["⑧⑨ → ④ ② ⑥"]), ("setAttribute(Signed)", "U3 / V3 / P1", ["⑧⑨ → ② ⑦ (no attr store)"]), ("revokeAttribute(Signed)", "D2 / V5", ["⑧⑨ → ② ⑦ validTo=0"])]
    for i, (n, op, eff) in enumerate(fn):
        yy = y + 20 + i * 40
        s.rect(fx, yy, 300, 32, sw=1.6)
        s.text(fx + 8, yy + 14, n, size=11, weight="bold", mono=True)
        s.text(fx + 8, yy + 27, f"op {op}   effect {eff[0]}", size=9, mono=True, color=LINE_SOFT)
    ex = fx + 340
    s.section_label(ex, y, "EVENTS (the DID document lives here)")
    ev = [("DIDOwnerChanged", 5), ("DIDDelegateChanged", 6), ("DIDAttributeChanged", 7)]
    for i, (n, b) in enumerate(ev):
        yy = y + 20 + i * 54
        s.rect(ex, yy, 230, 44, sw=2.0, dash="6,4")
        s.text(ex + 10, yy + 27, n, size=12, mono=True, weight="bold")
        s.balloon(b, ex + 215, yy + 10, r=10)
    s.text(ex, y + 190, "dashed = emitted, not stored:", size=10, color=LINE_SOFT, mono=True)
    s.text(ex, y + 206, "readable off-chain only (R3 walk, BP-201)", size=10, color=LINE_SOFT, mono=True)
    # linked list detail
    lx, ly = 480, 430
    s.section_label(lx, ly, "DETAIL B — THE changed → previousChange LINKED LIST (one hop per on-chain change)")
    bx = lx
    blocks = [("block 1,204", "DIDAttributeChanged", "prev = 1,180"), ("block 1,180", "DIDDelegateChanged", "prev = 991"), ("block 991", "DIDOwnerChanged", "prev = 0")]
    s.rect(bx, ly + 22, 120, 40, sw=1.8, fill=GROUND_DK); s.text(bx + 60, ly + 40, "changed[id]", size=11, anchor="middle", mono=True); s.text(bx + 60, ly + 55, "= 1,204", size=10, anchor="middle", mono=True, color=ACCENT)
    px = bx + 160
    for i, (b, e, p) in enumerate(blocks):
        s.rect(px, ly + 22, 200, 40, sw=1.6, dash="6,4")
        s.text(px + 8, ly + 38, b, size=11, mono=True, weight="bold"); s.text(px + 8, ly + 54, f"{e} · {p}", size=9, mono=True, color=LINE_SOFT)
        s.arrow(px - 40 if i else bx + 120, ly + 42, px, ly + 42, head=7)
        px += 240
    s.text(lx, ly + 90, "Resolver cost: hops = number of changes; eth_getLogs per hop. Measured read path at h=50: " + D("http.r3.erc1056.h50") + " ms median over HTTP RPC, over the J2945/1 budget (#39) — hence the cache on BP-302.", size=10, color=ACCENT, mono=True)
    # signed envelope
    sx, sy = 480, 560
    s.section_label(sx, sy, "DETAIL C — SIGNED (META-TX) ENVELOPE, ERC-1056 REFERENCE PATTERN")
    s.rect(sx, sy + 20, 980, 36, sw=1.6, fill=GROUND_DK)
    s.text(sx + 10, sy + 43, 'hash = keccak256( 0x19 ‖ 0x00 ‖ address(this) ‖ nonce[identityOwner(id)] ‖ id ‖ "setAttribute" ‖ name ‖ value ‖ validity )', size=11, mono=True)
    s.text(sx, sy + 78, "require(ecrecover(hash, v, r, s) == identityOwner(id)); nonce[signer]++   →  the relayer pays gas; the vehicle signs.", size=10, color=LINE_SOFT, mono=True)
    s.text(sx, sy + 94, "Binding: this registry (address), this owner's nonce, this identity, this verb — a captured signature cannot be replayed elsewhere (G3).", size=10, color=LINE_SOFT, mono=True)
    return s


FSET = [  # (F, set, function, catalogue ops, where realised)
    ("F1", "A", "createDID", "C1 · C2", "all 10 (ERC-1056 implicit; wrapper binds VIN)"),
    ("F2", "A", "resolve identifier / document", "R1 · R2 · R3", "all 10 (event walk, view calls, getData)"),
    ("F3", "A", "changeOwner (controller rotation)", "U1 · U4", "all 10"),
    ("F4", "A", "delegates (session / verification keys)", "U2 · D1 · R4", "1056, 725, 4337(guardian), CVIN — n/a 721/1155/735/725xy/LSP8"),
    ("F9", "A", "attributes / document state", "U3 · D2", "all (D2 n/a on 721, 1056w)"),
    ("F10", "A", "execute (agent proxy)", "X1", "725xy, 4337 only — registries cannot act"),
    ("F11", "A", "deactivate", "D3", "all (several as documented workaround)"),
    ("F12", "A", "relayed / sponsored op (programme addition)", "U5", "1056 (signed), 4337 (userOp)"),
    ("F5", "B", "issueCredential", "V1 · V2 · V3", "VC signed off-chain (all); anchor per substrate"),
    ("F6", "B", "verifyCredential", "V4 · V6 · R4", "6-stage pipeline (BP-202) + on-chain status"),
    ("F7", "B", "revokeCredential", "V5", "all (event, burn, removeClaim, setData 0x)"),
    ("F8", "B", "createPresentation", "P1", "holder anchors nonce-keyed hash: 1056, CVIN, 735, 725, 725xy, 4337 — n/a 721/1155/LSP8"),
]


def bp104():
    s = Sheet("BP-104", "The basic digital-ID set — IMinimalSSI F1–F12", "SV-4 functional allocation: twelve functions, the catalogue ops that measure them, who has them",
              notes_width=560,
              notes=["The canon (cvin-sandbox-v1.3, 2026-06-05) admits a substrate when all twelve pass. This repository keeps that gate and adds exact cost per function (BASIC_ID_SET_EXTENSION §2–3).",
                     "F-numbers F1–F4, F9–F12 are quoted as the branch documents give them; exact numbering of the canon archive is [B1] pending. Function names are exact.",
                     "Strict admission (every mapped op native): ERC-1056 pure, ERC-725, ERC-4337, CVIN-Combined. Others are measured with the gap carried as a finding, never excluded.",
                     "No ERC provides F8 natively — the canon's structural finding; P1 realises it as a replay-protected anchor pattern (" + D("canon.p1") + " gas on the canon's O1 trace, non-comparable condition)."],
              refs=["docs/BASIC_ID_SET_EXTENSION.md §1–§4 (mapping, coverage A6, reconciliation)", "docs/CVIN-DATA-COLLECTION-FRAMEWORK.md §2 (catalogue), §2.2c (P1, X1)",
                    "1_blockchain-identity/results/metrics/latest/tables/analysis_basic_set.md (A6, run of record)"])
    x, y = INNER[0] + 10, INNER[1] + 300
    s.section_label(x, y, "FUNCTIONAL ALLOCATION — SET A (ISetA) ROWS F1–F12 / SET B (ISetB) ROWS F5–F8")
    rows = [(f, fn, ops, where) for f, st, fn, ops, where in FSET]
    s.table(x, y + 14, [("F", 44), ("FUNCTION (IMinimalSSI)", 280), ("CATALOGUE OPS", 110), ("REALISED ON / GAPS", 440)], rows, size=10, lh=24,
            cell_colors=lambda ri, ci, v: ACCENT if ci == 0 else (WARN if ("n/a" in v or "only" in v) and ci == 3 else None))
    # balloon-style function block diagram on the right: a vehicle identity as a machine with 12 ports
    mx, my = 1250, 420
    s.rect(mx - 110, my - 150, 220, 300, sw=2.4, fill=GROUND_DK)
    s.text(mx, my - 120, "VEHICLE IDENTITY", size=12, anchor="middle", weight="bold")
    s.text(mx, my - 104, "one substrate instance", size=9, anchor="middle", mono=True, color=LINE_SOFT)
    ports_l = [("F1 create", "C1"), ("F2 resolve", "R1–R3"), ("F3 rotate", "U1/U4"), ("F4 delegate", "U2/D1/R4"), ("F9 attribute", "U3/D2"), ("F10 execute", "X1"), ("F11 deactivate", "D3"), ("F12 relay", "U5")]
    ports_r = [("F5 issue", "V1–V3"), ("F6 verify", "V4/V6"), ("F7 revoke", "V5"), ("F8 present", "P1")]
    for i, (n, op) in enumerate(ports_l):
        yy = my - 90 + i * 30
        s.line(mx - 110, yy, mx - 150, yy, sw=1.4)
        s.circle(mx - 150, yy, 4, fill=LINE)
        s.text(mx - 160, yy + 4, f"{n}  [{op}]", size=10, anchor="end", mono=True)
    for i, (n, op) in enumerate(ports_r):
        yy = my - 60 + i * 44
        s.line(mx + 110, yy, mx + 150, yy, sw=1.4)
        s.circle(mx + 150, yy, 4, fill=LINE)
        s.text(mx + 160, yy + 4, f"[{op}]  {n}", size=10, mono=True)
    s.text(mx, my + 128, "Set A ports: 8    Set B ports: 4", size=10, anchor="middle", mono=True, color=ACCENT)
    s.text(mx, my + 170, "Admission = all 12 ports present.", size=10, mono=True, color=LINE_SOFT, anchor="middle")
    s.text(mx, my + 184, "Ranking = measured cost per port (BP-501).", size=10, mono=True, color=LINE_SOFT, anchor="middle")
    # coverage strip
    cx, cy = x, y + 14 + 24 * 13 + 24
    s.section_label(cx, cy, "COVERAGE A6 (RUN OF RECORD) — SET A OPS / SET B OPS NATIVE")
    cov = [("ERC-1056 pure · ERC-725 · ERC-4337 · CVIN", "11/11", "4/4", "ADMITTED"), ("ERC-1056 wrapper · ERC-721", "10/11 (no D2)", "4/4", "not admitted (strict)"),
           ("ERC-1155 · ERC-725xy", "8/11 (no U2/R4/D1)", "4/4", "no delegate primitive"), ("ERC-735 · LSP8", "8/11", "3/4 (no V1)", "no delegates, no issuer-key anchor")]
    s.table(cx, cy + 14, [("SUBSTRATE", 330), ("SET A", 150), ("SET B", 110), ("VERDICT", 240)], cov, size=10, lh=22,
            cell_colors=lambda ri, ci, v: OK if v == "ADMITTED" else (WARN if ci == 3 else None))
    return s


def bp105():
    s = Sheet("BP-105", "CVIN-Combined hybrid — section through the thesis engine", "ERC-1056 event side for the common path, ERC-735 claim side for the safety-critical subset, one owner gate",
              notes=["Design rule: events are cheap (common path); safety-critical claims must be O(1) readable on-chain by another contract (a road-side unit cannot walk a log inside the EVM).",
                     "Claim signature is over the RAW digest keccak256(this, identity, topic, data): bound to this registry and this subject. Verified with ecrecover at ADD time, so getClaim is O(1) with no re-verification.",
                     "Issuer revocation is sticky (REVIEW_02 K-2): keccak256(issuer, digest) is recorded; re-anchoring the same signed content reverts. Claims do not advance changed[] (K-6).",
                     "Cheapest create measured (" + D("gas.CVIN-Combined.createIdentity") + " gas #25) while keeping claims: the favourable corner of the frontier (H5)."],
              parts=[(1, "identityOwner / changeOwner", "ERC-1056 semantics; the single gate for both halves"),
                     (2, "delegates + DIDDelegateChanged", "session keys with TTL (U2 / D1 / R4)"),
                     (3, "setAttribute → DIDAttributeChanged", "event-only attributes (U3 / D2 / P1)"),
                     (4, "changed[identity]", "DID-event chain head; claims never move it"),
                     (5, "addClaim", "onlyIdentityOwner; verifies issuer sig then stores; ClaimAdded"),
                     (6, "_claimDigest", "keccak256(address(this), identity, topic, data)"),
                     (7, "_recoverRawDigest", "ecrecover over raw digest, v ∈ {27,28}, 65-byte sig"),
                     (8, "revokedClaims", "keccak256(issuer, digest) → bool; sticky issuer revocation"),
                     (9, "getClaim / hasValidClaim", "O(1) read for on-chain verifiers (RSU, another contract)"),
                     (10, "topics 1/2/3", "VIN attestation · manufacturer / type approval · periodic inspection")],
              parts_width=660,
              refs=["1_blockchain-identity/contracts/CVINCombined/CVINCombinedIdentity.sol", "test/CVINCombined/, test/security/securityScenarios.test.js (CVIN cells)",
                    "docs/REVIEW_02_CODEBASE.md K-2, K-6, K-11 (fixes drawn here)"])
    # two halves
    x, y = 480, 160
    s.rect(x, y, 470, 330, sw=2.4)
    s.text(x + 12, y + 22, "ERC-1056 SIDE — EVENT LOG (common path)", size=12, weight="bold")
    s.rect(x + 20, y + 40, 200, 40, sw=1.6, fill=GROUND_DK); s.text(x + 120, y + 64, "_owners · delegates", size=11, anchor="middle", mono=True); s.balloon(1, x + 230, y + 50, r=10); s.balloon(2, x + 230, y + 76, r=10)
    s.rect(x + 20, y + 100, 200, 40, sw=1.6, fill=GROUND_DK); s.text(x + 120, y + 124, "changed[identity]", size=11, anchor="middle", mono=True); s.balloon(4, x + 230, y + 110, r=10)
    s.rect(x + 20, y + 160, 420, 110, sw=1.6, dash="6,4")
    s.text(x + 30, y + 182, "events only — DIDOwnerChanged / DIDDelegateChanged / DIDAttributeChanged", size=10, mono=True)
    s.text(x + 30, y + 202, "attribute value never stored; resolver rebuilds the DID document", size=10, mono=True, color=LINE_SOFT)
    s.text(x + 30, y + 222, "cost class: LOG + one SSTORE overwrite (BP-102 ③ ②)", size=10, mono=True, color=ACCENT)
    s.balloon(3, x + 430, y + 170, r=10)
    s.text(x + 30, y + 300, "ops: C1 (implicit) · U1 U2 U3 U4 · D1 D2 D3 · P1 · R1 R3 R4", size=10, mono=True, color=LINE_SOFT)
    x2 = x + 500
    s.rect(x2, y, 470, 330, sw=2.4)
    s.text(x2 + 12, y + 22, "ERC-735 SIDE — ON-CHAIN CLAIMS (safety-critical subset)", size=12, weight="bold")
    s.rect(x2 + 20, y + 40, 220, 40, sw=1.6, fill=GROUND_DK); s.text(x2 + 130, y + 64, "_claims[id][claimId]", size=11, anchor="middle", mono=True); s.balloon(5, x2 + 250, y + 50, r=10)
    s.rect(x2 + 20, y + 100, 220, 40, sw=1.6, fill=GROUND_DK); s.text(x2 + 130, y + 124, "revokedClaims[k]", size=11, anchor="middle", mono=True); s.balloon(8, x2 + 250, y + 110, r=10)
    s.rect(x2 + 20, y + 160, 420, 110, sw=1.6)
    s.text(x2 + 30, y + 182, "stored struct: topic, scheme, issuer, signature, data, uri", size=10, mono=True)
    s.text(x2 + 30, y + 202, "claimId = keccak256(issuer, topic); indexed by topic", size=10, mono=True, color=LINE_SOFT)
    s.text(x2 + 30, y + 222, "cost class: several SSTORE 0→x (BP-102 ①); paid only when a claim is needed", size=10, mono=True, color=ACCENT)
    s.balloon(9, x2 + 430, y + 170, r=10)
    s.text(x2 + 30, y + 300, "ops: C1/C2 (VIN + manufacturer claims) · V3 V5 V6 · topics ⑩", size=10, mono=True, color=LINE_SOFT)
    # shared gate
    s.rect(x + 180, y + 340, 600, 36, sw=2.0, fill=GROUND_DK)
    s.text(x + 480, y + 363, "onlyIdentityOwner(identity): msg.sender == identityOwner(identity)   — the one gate both halves share (G1)", size=11, anchor="middle", mono=True)
    s.arrow(x + 300, y + 340, x + 300, y + 332, head=7); s.arrow(x + 660, y + 340, x + 660, y + 332, head=7)
    # addClaim detail
    ax, ay = 480, 610
    s.section_label(ax, ay, "DETAIL A — addClaim VERIFICATION PATH (verified once, read forever)")
    steps = ["scheme == ECDSA", "issuer ≠ 0x0", "digest = ⑥", "ecrecover(digest, sig) == issuer  ⑦", "!revokedClaims[keccak(issuer,digest)]  ⑧", "store + ClaimAdded  ⑤", "changed[] untouched  ④"]
    xx = ax
    for i, t in enumerate(steps):
        w = 110 if len(t) < 16 else 140 if len(t) < 28 else 165
        s.rect(xx, ay + 18, w, 40, sw=1.6, fill=GROUND_DK if "ecrecover" in t else "none")
        s.wrap(xx + w / 2, ay + 36, t, width_chars=int(w / 7), size=9, lh=11, anchor="middle", mono=True)
        if i < len(steps) - 1:
            s.arrow(xx + w, ay + 38, xx + w + 14, ay + 38, head=6)
        xx += w + 14
    s.text(ax, ay + 84, "Frontier placement: pay the event price on the common path, the storage price only for the claim.", size=10, mono=True, color=ACCENT)
    s.text(ax, ay + 100, "Lifetime cost is tunable through the claim fraction f (§5.9, scaling_lifetime #31).", size=10, mono=True, color=ACCENT)
    return s


def bp106():
    s = Sheet("BP-106", "Nine substrates — comparative sections", "Identity model, state model and create gas side by side (register #25, condition M1)",
              notes=["Sections are schematic: each box is one substrate's on-chain footprint for ONE vehicle. Hatched = the part the standard lacks (reported as n/a, never blank).",
                     "ERC-4337 EntryPoint and LSP8 are deliberately minimal representatives; their gas is a lower bound.",
                     "MOBI-VID-V2 is an application profile measured alongside, not a tenth base standard."],
              refs=["4_comparison-framework/results/gas_benchmark.json (#25, N=30, CI width 0)", "docs/CVIN-DATA-COLLECTION-FRAMEWORK.md §1.1 (substrate table), §2.2a–b (realisations)",
                    "docs/DID_METHOD_RUBRIC.md (qualitative cells)"])
    x0, y0 = INNER[0] + 10, INNER[1] + 110
    cw, ch = 290, 170
    cells = [
        ("ERC-1056", raw("gas.ERC-1056.createIdentity"), "address is DID", "event log", ["owners", "changed", "delegates"], ["attrs (events)"], []),
        ("CVIN-Combined", raw("gas.CVIN-Combined.createIdentity"), "address is DID", "event log + claims", ["owners", "changed", "delegates", "claims"], ["attrs (events)"], []),
        ("ERC-1155", raw("gas.ERC-1155.createIdentity"), "address is DID", "soulbound balances", ["balances[type]", "vinHash maps"], [], ["delegates", "attributes"]),
        ("LSP8", raw("gas.LSP8.createIdentity"), "token = keccak(VIN)", "per-token key/value", ["tokenOwner", "data[token][key]"], [], ["operators", "delegates"]),
        ("ERC-721", raw("gas.ERC-721.createIdentity"), "token = identity", "rich struct", ["owner", "metadata struct", "history[]", "service[]"], [], ["delegate TTL", "D2"]),
        ("ERC-725", raw("gas.ERC-725.createIdentity"), "contract / identity", "key map", ["keys[]", "key purposes", "owner"], [], ["execute (stub)"]),
        ("ERC-4337", raw("gas.ERC-4337.createIdentity"), "account / identity", "storage + EntryPoint", ["owner", "guardian", "attributes"], ["userOp path ⑦"], ["bundler/paymaster"]),
        ("ERC-735", raw("gas.ERC-735.createIdentity"), "contract / identity", "claim store", ["owner", "claims struct", "topic index"], [], ["delegates", "V1 anchor"]),
        ("ERC-725xy", raw("gas.ERC-725xy.createIdentity"), "contract / identity", "X executor + Y store", ["owner", "data[key]", "execute"], [], ["delegates (no LSP6)"]),
    ]
    for i, (name, gas, idm, stm, stored, emitted, missing) in enumerate(cells):
        cx = x0 + (i % 3) * (cw + 20)
        cy = y0 + (i // 3) * (ch + 18)
        s.rect(cx, cy, cw, ch, sw=2.0, fill=GROUND_DK if gas < 60000 else "none")
        s.text(cx + 10, cy + 20, name, size=13, weight="bold")
        s.text(cx + cw - 10, cy + 20, f"{gas:,}", size=13, anchor="end", mono=True, color=ACCENT)
        s.text(cx + cw - 10, cy + 34, "create gas #25", size=8, anchor="end", mono=True, color=LINE_SOFT)
        s.text(cx + 10, cy + 36, f"{idm} · {stm}", size=9, mono=True, color=LINE_SOFT)
        yy = cy + 50
        for st in stored:
            s.rect(cx + 10, yy, 130, 18, sw=1.0); s.text(cx + 16, yy + 13, st, size=9, mono=True); yy += 22
        yy = cy + 50
        for em in emitted:
            s.rect(cx + 150, yy, 130, 18, sw=1.0, dash="4,3"); s.text(cx + 156, yy + 13, em, size=9, mono=True); yy += 22
        for ms in missing:
            s.hatch_rect(cx + 150, yy, 130, 18); s.text(cx + 156, yy + 13, ms, size=9, mono=True, color=LINE_SOFT); yy += 22
    s.text(x0, y0 + 3 * (ch + 18) + 10, "solid = stored (SSTORE) · dashed = emitted (LOG) · hatched = no primitive (n/a) · dark fill = cheapest family. Spread " + D("gas.CVIN-Combined.createIdentity") + " → " + D("gas.ERC-725xy.createIdentity") + " = " + D("gas.create.spread") + ".", size=10, mono=True, color=ACCENT)
    return s


SHEETS = [bp101, bp102, bp103, bp104, bp105, bp106]
