"""400-series: hull integrity — threat model, guarantee inheritance, attack matrix."""
from bplib import *  # noqa: F401,F403
from data import D, raw, lens1, lens2  # noqa: E402  (P2: every measured value comes from data.py)


def bp401():
    s = Sheet("BP-401", "Threat model — adversaries, trust bulkheads, security goals", "Hull-integrity schematic of docs/THREAT_MODEL.md: who attacks where, what is assumed, what must hold",
              notes=["Computationally bounded adversary: cannot forge secp256k1 / P-256 signatures or find keccak256 / SHA-256 pre-images (BP-101 parts are unbreakable by assumption).",
                     "Explicitly out of scope: consensus-level (51%) attacks, primitive breaks, verifier or HSM compromise, side channels, MEV / fee-market manipulation, governance attacks on upgradeable contracts (the tested contracts are non-upgradeable).",
                     "Lens 1 (executable reverts, " + D("sec.cells") + " scenarios) proves G1–G4 with a differential control: the authorized action succeeds, the attack reverts with the named reason. Lens 2 (matrix) scores G5–G8."],
              notes_width=1060,
              refs=["docs/THREAT_MODEL.md §1–§6", "1_blockchain-identity/test/security/securityScenarios.test.js (Lens 1) · 4_comparison-framework/security-analysis/results/security_matrix.json (Lens 2)"])
    # hull: a long rounded shape with bulkheads; adversaries outside pressing in
    hx, hy, hw, hh = 90, 300, 1300, 290
    s.rect(hx, hy, hw, hh, sw=2.6, rx=40)
    s.text(hx + 20, hy - 10, "PRESSURE HULL — THE SYSTEM MODEL (§1): identities and the credentials bound to them, on one of nine substrates", size=11, weight="bold")
    comps = [("ISSUERS", "manufacturer, DMV, insurer, service centre", "create identities, issue credentials"),
             ("OWNERS", "vehicle / owner keys, delegates", "control identity, present credentials"),
             ("ATTESTORS", "third parties", "vouch for lifecycle events"),
             ("VERIFIERS", "DMV, insurer, peer vehicle", "relying parties; run the pipeline"),
             ("THE CHAIN", "EVM ledger executing the substrate", "T1: integrity assumed")]
    cw = hw / len(comps)
    for i, (n, who, does) in enumerate(comps):
        cx = hx + i * cw
        if i:
            s.line(cx, hy + 10, cx, hy + hh - 10, sw=2.0)  # bulkhead
            s.text(cx + 4, hy + hh - 14, "bulkhead", size=8, color=LINE_FAINT, mono=True)
        s.text(cx + cw / 2, hy + 40, n, size=13, anchor="middle", weight="bold")
        s.wrap(cx + cw / 2, hy + 64, who, width_chars=28, size=10, lh=13, anchor="middle", color=LINE_SOFT, mono=True)
        s.wrap(cx + cw / 2, hy + 110, does, width_chars=28, size=10, lh=13, anchor="middle")
    # trust assumptions inside the hull
    tas = [("T1", "chain integrity — faithful execution, immutable history"), ("T2", "issuer honesty at issuance (t=0 only)"), ("T3", "key custody by owners (A3 models its failure)"), ("T4", "verifier correctness (conformance ≠ compromise)")]
    for i, (t, d) in enumerate(tas):
        s.rect(hx + 30 + i * 320, hy + 190, 300, 70, sw=1.4, fill=GROUND_DK)
        s.text(hx + 40 + i * 320, hy + 212, t, size=14, weight="bold", mono=True, color=ACCENT)
        s.wrap(hx + 80 + i * 320, hy + 212, d, width_chars=34, size=10, lh=13)
    s.text(hx + 30, hy + 180, "TRUST ASSUMPTIONS (§3) — the keel the hull sits on", size=10, color=ACCENT, mono=True)
    # adversaries outside, arrows pressing in
    advs = [("A1", "network / message (Dolev–Yao)", "observe, replay, reorder, inject V2V msgs and txs", 250, hy - 90, 250, hy),
            ("A2", "malicious registered party", "rogue owner / dealer / attestor acting beyond role", 650, hy - 90, 650, hy),
            ("A3", "key compromise", "holds a victim's private key; takeover vs recovery", 1050, hy - 90, 1050, hy),
            ("A4", "passive on-chain observer", "reads all state/events; seeks VIN / linkability", 1320, hy + hh + 90, 1320, hy + hh)]
    for a, n, d, x, y, tx, ty in advs:
        s.rect(x - 130, y - 30, 260, 56, sw=1.8, stroke=WARN)
        s.text(x - 120, y - 10, f"{a}  {n}", size=11, weight="bold", color=WARN)
        s.text(x - 120, y + 8, d, size=8, mono=True, color=WARN)
        s.arrow(x, y + 26 if ty > y else y - 30, tx, ty, stroke=WARN, sw=2.0, head=10)
    # goals as the bulkhead integrity checks
    gx, gy = 90, 650
    s.section_label(gx, gy, "SECURITY GOALS (§4) — WHAT EACH BULKHEAD MUST HOLD, AND WHICH LENS PROVES IT")
    rows = [("G1", "authenticity: only the controlling key creates / modifies / issues on behalf", "A1 A2", "Lens 1: attribute write, hijack"),
            ("G2", "non-forgeability: claim / attestation verifies only if signed by an authorized issuer over the bound context", "A2", "Lens 1: delegate / claim; attestEvent fix"),
            ("G3", "replay resistance: nonce / domain / chain binding", "A1", "Lens 1: signature replay (" + D("sec.col5.total") + ")"),
            ("G4", "authorization integrity: no acting beyond role (issue / attest / revoke)", "A2", "Lens 1: issuance, revocation"),
            ("G5", "Sybil cost: N identities cost / gate ∝ N", "A2", "Lens 2: issuance cost / gating"),
            ("G6", "recoverability after key compromise", "A3", "Lens 2: ERC-4337 only (guardian)"),
            ("G7", "PII confidentiality: VIN never plaintext on-chain", "A4", "Lens 2: MOBI family only"),
            ("G8", "theft resistance: token / key transfer ≠ identity transfer where forbidden", "A2 A3", "Lens 2: ERC-1155 soulbound")]
    s.table(gx, gy + 14, [("G", 40), ("GOAL", 640), ("COUNTERS", 90), ("PROVEN BY", 300)], rows, size=9, lh=21, cell_colors=lambda ri, ci, v: ACCENT if ci == 0 else (WARN if ci == 2 else None))
    return s


def bp402():
    s = Sheet("BP-402", "Security-guarantee inheritance", "What the identity system inherits from the ledger that settles value, what it adds on top, and where the inheritance stops",
              notes=["An identity operation is a transaction. It enters the same mempool, is ordered by the same validators, pays the same fee market and reaches the same finality as a transfer of value. The ledger cannot tell them apart.",
                     "The fiat value a given chain secures (X) is a parameter, not a thesis result: insert it with a dated source when citing. The structure of the inheritance does not depend on X.",
                     "What is NOT inherited is drawn on the right. Those are the application layer's own obligations — and they are the ones this repository measures (BP-403)."],
              refs=["docs/THREAT_MODEL.md T1 (chain integrity assumed) · §6 (out of scope)", "docs/blueprints/SECURITY_GUARANTEE_INHERITANCE.md (the argument in prose, with its limits)",
                    "BP-101 (same primitives) · BP-102 (same gas schedule) · BP-301 msgs 5–7 (same transaction path)"],
              notes_width=1060)
    # two parallel pipes: value transfer vs identity op, through identical stages
    x, y = 90, 215
    s.section_label(x, y, "DETAIL A — TWO TRANSACTIONS, ONE PATH (the ledger does not know which is which)")
    stages = ["sign with sk\n(secp256k1)", "serialize + chainId\n(EIP-155)", "mempool / p2p\n(L1)", "ordered in a block\n(L2 consensus)", "executed by EVM\n(L3, deterministic)", "finalized\n(immutable history)"]
    for row, (lab, color, ex) in enumerate([("VALUE TRANSFER", LINE, "transfer(to, 2 000 000 000 USD-equivalent)  — param"), ("IDENTITY OPERATION", ACCENT, "changeOwner(did, newOwner) · addClaim(…) · registerBirth(…)")]):
        yy = y + 24 + row * 110
        s.text(x, yy + 30, lab, size=11, weight="bold", color=color)
        s.text(x, yy + 48, ex, size=9, mono=True, color=LINE_SOFT)
        xx = x + 300
        for i, st in enumerate(stages):
            s.rect(xx, yy, 150, 60, sw=1.8, stroke=color, fill=GROUND_DK if row else "none")
            for j, l in enumerate(st.split("\n")):
                s.text(xx + 75, yy + 24 + j * 16, l, size=10, anchor="middle", mono=True, color=color)
            if i < len(stages) - 1:
                s.arrow(xx + 150, yy + 30, xx + 170, yy + 30, head=7, stroke=color)
            xx += 170
    s.rect(x + 290, y + 14, 6 * 170 - 10, 190, sw=1.0, dash="6,4", stroke=LINE_SOFT)
    s.text(x + 300, y + 200, "identical machinery: same keys, same validators, same finality, same gas schedule (BP-101, BP-102)", size=10, mono=True, color=LINE_SOFT)
    # inheritance ladder
    lx, ly = 90, 470
    s.section_label(lx, ly, "DETAIL B — INHERITED FROM THE LEDGER (T1)", color=OK)
    inh = [("ordering and finality", "an identity change cannot be reordered or undone once final"),
           ("immutability of history", "the event log a resolver walks is the chain's own history"),
           ("deterministic execution", "the authorization check runs exactly as written, for everyone"),
           ("tx-level signature + replay protection", "EIP-155 chainId + account nonce; same as for value"),
           ("censorship resistance / liveness", "whatever the chain offers to value, it offers to identity"),
           ("economic security (X secured)", "attacking an identity means attacking the chain that carries X — param")]
    for i, (a, b) in enumerate(inh):
        yy = ly + 18 + i * 40
        s.rect(lx, yy, 620, 34, sw=1.4, stroke=OK)
        s.text(lx + 8, yy + 15, a, size=10, weight="bold", color=OK)
        s.text(lx + 8, yy + 29, b, size=9, mono=True, color=LINE_SOFT)
    rx = 780
    s.section_label(rx, ly, "DETAIL C — NOT INHERITED: THE APPLICATION'S OWN OBLIGATIONS (measured here)", color=WARN)
    own = [("authorization logic (G1, G4)", "onlyOwner / role gates — " + D("sec.cells") + " scenarios, " + D("sec.total") + " defended (BP-403)"),
           ("claim-level signature binding (G2)", "digest = (registry, identity, topic, data); attestEvent fix"),
           ("payload-level replay (G3)", "registry nonce, VP challenge + domain, presentation key"),
           ("key custody (T3) and recovery (G6)", "HSM out of scope; recovery native on ERC-4337 only"),
           ("issuer honesty at t=0 (T2)", "a lying manufacturer is not detected by any substrate"),
           ("off-chain cache staleness", "freshness-k: revocation honoured within ≤ k−1 messages (BP-302)"),
           ("verifier correctness (T4)", "conformance " + D("w3c.score") + " is not the same as a correct verifier")]
    for i, (a, b) in enumerate(own):
        yy = ly + 18 + i * 40
        s.rect(rx, yy, 680, 34, sw=1.4, stroke=WARN)
        s.text(rx + 8, yy + 15, a, size=10, weight="bold", color=WARN)
        s.text(rx + 8, yy + 29, b, size=9, mono=True, color=LINE_SOFT)
    s.rect(lx, ly + 18 + 6 * 40 + 4, 620, 66, sw=1.2, stroke=ACCENT, dash="6,4")
    s.lines(lx + 8, ly + 18 + 6 * 40 + 22, ["The sentence this sheet licenses: 'A vehicle's claim is carried by the same",
                                             "guarantee as a $2B transfer on this chain — up to the waterline (BP-001).",
                                             "Above it, the guarantee is ours, and it is measured (BP-403).'"], size=10, lh=15, mono=True, color=ACCENT)
    return s


ATTACKS = ["Unauthorized issuance", "Unauthorized attribute write", "Unauthorized delegate/claim", "Unauthorized revocation", "Identity hijack", "Signature replay"]
THREATS = ["Spoofing", "Tampering", "Spoofing / Elevation", "Denial of service", "Elevation of privilege", "Replay"]
GOALS = ["G1 G4", "G1", "G2 G4", "G4", "G8", "G3"]
LENS1 = {  # from attack_results.csv (2026-07-19 run of record for the matrix)
    "ERC-1056": ["—", "D", "D", "D", "D", "D"], "ERC-721": ["D", "D", "D", "D", "D", "—"], "ERC-725": ["—", "D", "D", "D", "D", "—"],
    "ERC-735": ["—", "D", "D", "D", "D", "D"], "ERC-1155": ["D", "D", "D", "D", "D", "—"], "ERC-4337": ["—", "D", "D", "D", "D", "D"],
    "LSP8": ["D", "D", "—", "D", "D", "—"], "MOBI-VID-V2": ["D", "D", "D", "D", "D", "—"], "CVIN-Combined": ["—", "D", "D", "D", "D", "D"],
}
LENS2 = {  # security_matrix.csv: impersonation, replay, identity_theft, sybil, recovery, privacy
    "ERC-1056": ["D", "D", "P", "V", "V*", "D"], "ERC-721": ["D", "N*", "V", "D", "V*", "V"], "ERC-725": ["D", "N*", "P", "P", "V*", "D"],
    "ERC-735": ["D", "P", "P", "P", "V*", "V"], "ERC-1155": ["D", "N*", "D", "D", "P", "V"], "ERC-4337": ["D", "D", "P", "P", "D", "P"],
    "LSP8": ["D", "N*", "V", "D", "P", "V"], "MOBI-VID-V2": ["D", "D*", "P", "D", "V*", "D"], "CVIN-Combined": ["D", "P", "P", "V", "V*", "P"],
}
# P2: the tables above are replaced by the CSVs of record; the literals stay only as
# the expected shape, and generation fails if the CSV columns stop matching ATTACKS.
_hdr = __import__("data")._attack_rows()[0]
assert [h.lower() for h in _hdr] == [a.lower() for a in ATTACKS], f"attack_results.csv columns changed: {_hdr}"
LENS1 = lens1()
LENS2 = lens2()
L2COLS = ["impersonation", "replay", "identity theft (G8)", "Sybil (G5)", "recovery (G6)", "privacy (G7)"]


def bp403():
    s = Sheet("BP-403", "Attack matrix — two lenses", "Lens 1: " + D("sec.cells") + " executable cells, " + D("sec.total") + " applicable DEFENDED. Lens 2: the softer goals a revert test cannot express",
              notes=["Lens 1 cell = malicious transaction reverted with the documented expected reason of the named defence, with a differential control that the authorized action succeeds. '—' = structurally N/A for that standard's model (" + D("sec.na") + " cells).",
                     "Lens 2 legend: D defended · P partial · V vulnerable · N n/a; * = reasoned from the verified source (structural absence), others executed. Sybil cost proxy = create gas (BP-501).",
                     "Reading: no column is all-D in Lens 2 — no standard dominates (H5). Recovery is ERC-4337's alone; soulbound theft resistance is ERC-1155's; on-chain VIN privacy is MOBI's."],
              refs=["4_comparison-framework/security-analysis/results/attack_results.csv / .json (Lens 1, solc 0.8.24, OZ 5.0.2, hardhat-local)", "4_comparison-framework/security-analysis/results/security_matrix.csv (Lens 2) · docs/THREAT_MODEL.md §5"],
              notes_width=1060)
    def colour(v):
        return {"D": OK, "P": ACCENT, "V": WARN, "N": LINE_FAINT, "—": LINE_FAINT}.get(v[0], LINE)
    x, y = 90, 215
    s.section_label(x, y, "LENS 1 — EXECUTABLE REVERT SUITE (securityScenarios.test.js)")
    cw, rh, lw = 115, 30, 150
    for j, a in enumerate(ATTACKS):
        cx = x + lw + j * cw
        s.rect(cx, y + 14, cw, 58, sw=1.0, fill=GROUND_DK)
        s.wrap(cx + cw / 2, y + 30, a, width_chars=14, size=8, lh=10, anchor="middle", mono=True, color=ACCENT)
        s.text(cx + cw / 2, y + 66, GOALS[j], size=8, anchor="middle", mono=True, color=LINE_SOFT)
    for i, (std, cells) in enumerate(LENS1.items()):
        ry = y + 72 + i * rh
        s.rect(x, ry, lw, rh, sw=0.8); s.text(x + 6, ry + 19, std, size=10, mono=True)
        for j, v in enumerate(cells):
            cx = x + lw + j * cw
            s.rect(cx, ry, cw, rh, sw=0.8, stroke=LINE_SOFT)
            if v == "D":
                s.rect(cx + 4, ry + 4, cw - 8, rh - 8, sw=1.4, stroke=OK, fill="none"); s.text(cx + cw / 2, ry + 19, "DEFENDED", size=9, anchor="middle", mono=True, color=OK)
            else:
                s.hatch_rect(cx + 4, ry + 4, cw - 8, rh - 8); s.text(cx + cw / 2, ry + 19, "n/a", size=9, anchor="middle", mono=True, color=LINE_SOFT)
    ty = y + 72 + 9 * rh
    s.rect(x, ty, lw + 6 * cw, rh, sw=1.4, fill=GROUND_DK)
    s.text(x + 6, ty + 19, "TOTAL", size=10, mono=True, weight="bold")
    for j, t in enumerate([D(f"sec.col{j}.total") for j in range(6)]):
        s.text(x + lw + j * cw + cw / 2, ty + 19, t, size=10, anchor="middle", mono=True, color=OK, weight="bold")
    s.text(x + lw + 6 * cw + 12, ty + 19, "" + D("sec.total").replace("/", " / ") + " applicable (" + D("sec.cells") + " cells, " + D("sec.na") + " N/A)", size=11, mono=True, color=OK, weight="bold")
    # lens 2
    x2, y2 = 90, ty + 56
    s.section_label(x2, y2, "LENS 2 — COMPARATIVE THREAT MATRIX (security_matrix.csv)")
    cw2 = 115
    for j, a in enumerate(L2COLS):
        cx = x2 + lw + j * cw2
        s.rect(cx, y2 + 14, cw2, 36, sw=1.0, fill=GROUND_DK)
        s.wrap(cx + cw2 / 2, y2 + 30, a, width_chars=14, size=8, lh=10, anchor="middle", mono=True, color=ACCENT)
    rh2 = 22
    for i, (std, cells) in enumerate(LENS2.items()):
        ry = y2 + 50 + i * rh2
        s.rect(x2, ry, lw, rh2, sw=0.8); s.text(x2 + 6, ry + 15, std, size=10, mono=True)
        for j, v in enumerate(cells):
            cx = x2 + lw + j * cw2
            s.rect(cx, ry, cw2, rh2, sw=0.8, stroke=LINE_SOFT)
            s.text(cx + cw2 / 2, ry + 15, v, size=10, anchor="middle", mono=True, color=colour(v), weight="bold")
    # right side: frontier commentary
    fx, fy = 1000, 290
    s.section_label(fx, fy, "READING THE HULL")
    s.lines(fx, fy + 26, ["Lens 1 is binary and complete for G1–G4:", "every applicable attack reverts, and the", "authorized twin succeeds (differential control).", "",
                          "Lens 2 is where the frontier appears:", "  cheap self-registration ⇒ Sybil-exposed", "  issuer-gated ⇒ Sybil-resistant, costlier", "  recovery: ERC-4337 only (guardian slot)",
                          "  theft-resistant: ERC-1155 (soulbound)", "  VIN privacy: MOBI VID (hash + encrypt)", "", "Selection is a requirements-driven move", "along this frontier, not a winner (H5)."], size=11, lh=16)
    s.rect(fx, fy + 330, 520, 70, sw=1.4, stroke=ACCENT)
    s.text(fx + 10, fy + 352, "Found-and-fixed, reported as evidence:", size=11, weight="bold", color=ACCENT)
    s.text(fx + 10, fy + 370, "MOBI attestEvent accepted unverified signatures (G2/G3). Fixed with ecrecover;", size=10, mono=True)
    s.text(fx + 10, fy + 386, "" + D("attest.before") + " → " + D("attest.july") + " gas (July), " + D("attest.now") + " current build (#28). Replay passes.", size=10, mono=True)
    return s


SHEETS = [bp401, bp402, bp403]
