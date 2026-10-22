"""300-series: operations — sequences (SV-10c) and the lifecycle state machine."""
from bplib import *  # noqa: F401,F403


def bp301():
    s = Sheet("BP-301", "Sequence — vehicle birth registration", "SV-10c event trace: manufacturer issues, chain anchors, owner holds, DMV verifies (use case 1)",
              notes=["Every message is numbered; solid = on-chain transaction or trusted call, dashed = off-chain / untrusted transport.",
                     "Pass/fail in the use-case suite is computed: a forged or replayed birth certificate fails at message 12 (12/12 use cases; test_use_cases.py, no register row).",
                     "MOBI-VID-V2 birth: 14.13 ms median (#33, M4 parity harness); gas 299,143 (#25 definition; #33 measures 398,298 under its own definition, never mix)."],
              notes_width=1060,
              refs=["cv2x-testbed/scripts/test_use_cases.py — use case 1 (manufacturing & birth registration)", "2_w3c-ssi-layer/mobi-vid/birth_certificate.py · BP-204 (data flow) · BP-202 (verify pipeline)"])
    x0, y0, y1 = 100, 215, 820
    cols = [("MANUFACTURER", "issuer key (did:ethr)", x0 + 80), ("VC ISSUER", "vc_issuer.py", x0 + 340), ("REGISTRY", "MOBIVIDRegistryV2 / CVIN", x0 + 600),
            ("LEDGER", "EVM, consensus (L2–L3)", x0 + 840), ("OWNER WALLET", "vc_holder.py", x0 + 1080), ("VERIFIER (DMV)", "vc_verifier.py", x0 + 1340)]
    for name, sub, cx in cols:
        s.lifeline(cx, y0, y1, name, sub, w=170)
    X = {n: cx for n, _, cx in cols}
    y = y0 + 70
    y = s.msg(X["MANUFACTURER"], X["VC ISSUER"], y, 1, "issue_birth_certificate(vehicle, VIN, make, model, year…)") + 30
    y = s.msg(X["VC ISSUER"], X["VC ISSUER"], y, 2, "salt32; vinHash = sha256(vin:salt)  [BP-204 ②③]", self_call=True) + 24
    y = s.msg(X["VC ISSUER"], X["VC ISSUER"], y, 3, "VC: claimDigests; sign EIP-191 over canonical JSON", self_call=True) + 24
    y = s.msg(X["VC ISSUER"], X["VC ISSUER"], y, 4, "contentHash = keccak256(signed VC)", self_call=True) + 30
    y = s.msg(X["VC ISSUER"], X["REGISTRY"], y, 5, "registerBirth(vehicle, vinHash, contentHash)", note="tx signed by manufacturer key; role MANUFACTURER") + 36
    y = s.msg(X["REGISTRY"], X["LEDGER"], y, 6, "SSTORE vinHash, birthCertHash, manufacturer; LOG", note="ordinary transaction: same validators, same finality as a value transfer") + 40
    y = s.msg(X["LEDGER"], X["VC ISSUER"], y, 7, "receipt: gasUsed 299,143 (#25), block n", dash="6,4") + 32
    y = s.msg(X["VC ISSUER"], X["OWNER WALLET"], y, 8, "envelope {VC, disclosures, vinSalt, VIN ciphertext}", dash="6,4", note="off-chain delivery; nothing here is on the ledger") + 40
    y = s.msg(X["VERIFIER (DMV)"], X["OWNER WALLET"], y, 9, "challenge, domain", dash="6,4") + 30
    y = s.msg(X["OWNER WALLET"], X["VERIFIER (DMV)"], y, 10, "VP {VC, disclosures[S], challenge, domain}  [BP-203]", dash="6,4") + 30
    y = s.msg(X["VERIFIER (DMV)"], X["LEDGER"], y, 11, "read vinHash, birthCertHash, manufacturer (eth_call)", note="the only chain touch at verification: three reads") + 36
    y = s.msg(X["VERIFIER (DMV)"], X["VERIFIER (DMV)"], y, 12, "6-stage pipeline + 3 anchor checks [BP-204 ⑧] → ok / fail", self_call=True, left=True) + 30
    s.activation(X["REGISTRY"], y0 + 70 + 30 + 24 + 24 + 30 + 36 - 10, y0 + 70 + 30 + 24 + 24 + 30 + 36 + 40 + 20)
    s.text(x0, y1 + 24, "Trust boundary: messages 5–7 and 11 cross into the ledger (L2–L3, the inherited guarantee).", size=10, mono=True, color=ACCENT)
    s.text(x0, y1 + 40, "Messages 1–4, 8–10 and 12 are the application's own (L5–L6, the measured guarantee).", size=10, mono=True, color=ACCENT)
    return s


def bp302():
    s = Sheet("BP-302", "Sequence — V2V BSM verification at 10 Hz", "SV-10c: sender signs, receiver verifies from cache, refreshes chain state every k messages (freshness-k)",
              notes=["Budget: SAE J2945/1 fixes the BSM interval at 100 ms; the identity share is f·100 ms with f = 0.5 working assumption (LATENCY_BUDGET §1). P*(f) = floor(f·100 / t) neighbours.",
                     "Measured: SSI warm verify 0.153 ms [0.151, 0.154], cold 0.399 ms, PKI 0.094 ms (#27, N=30, 1,650,318 verifications, 150 failures = 5 injected attacks × 30 runs, all rejected).",
                     "Freshness-k sweep (#32): t_eff = 0.428 ms + 10.52 ms / k (full 4-RPC refresh); P*(0.5)=100 at k ≈ 146 (full refresh). One-call probe refresh 2.76 ms, but on the #37 host no finite k reaches P* = 100 (host-dependent knee). Revocation staleness ≤ k − 1 messages (≤ 14.5 s at k = 146, 10 Hz).",
                     "Excluded: radio / MAC / PHY latency; mobility is simulated. Identity verification is not the V2V bottleneck once the chain is off the hot path (H3)."],
              notes_width=1060,
              refs=["cv2x-testbed/sumo/sumo_identity_integration.py --simulate · run_v2v_stats.py (N=30) · results/freshness_k*.md", "docs/LATENCY_BUDGET.md §2–§4 · cv2x-testbed/identity/freshness.py (T-9 policy) · erc1056_provider.py (refresh_every=k)"])
    x0, y0, y1 = 100, 225, 745
    cols = [("SENDER VEHICLE", "did:ethr; delegate key", x0 + 90), ("RADIO (sim)", "CV2X stack, 10 Hz", x0 + 360), ("RECEIVER VERIFIER", "ERC1056Provider(k)", x0 + 640),
            ("KEY / REVOCATION CACHE", "did → (key, validTo, block)", x0 + 940), ("LEDGER (RPC)", "changed(), getLogs", x0 + 1240)]
    for name, sub, cx in cols:
        s.lifeline(cx, y0, y1, name, sub, w=190)
    X = {n: cx for n, _, cx in cols}
    y = y0 + 70
    y = s.msg(X["SENDER VEHICLE"], X["SENDER VEHICLE"], y, 1, "BSM{pos, speed, heading, t}; sig = ECDSA(sk_delegate, keccak(BSM))", self_call=True) + 26
    y = s.msg(X["SENDER VEHICLE"], X["RADIO (sim)"], y, 2, "broadcast BSM + sig + did  (every 100 ms)", dash="6,4") + 28
    y = s.msg(X["RADIO (sim)"], X["RECEIVER VERIFIER"], y, 3, "receive (A1 may replay / inject here)", dash="6,4") + 30
    y = s.msg(X["RECEIVER VERIFIER"], X["RECEIVER VERIFIER"], y, 4, "T-9 freshness: |t − now| ≤ 1.0 s; replay cache 65,536", self_call=True) + 26
    y = s.msg(X["RECEIVER VERIFIER"], X["KEY / REVOCATION CACHE"], y, 5, "lookup(did)") + 26
    # branch box
    bx, by = x0 + 560, y
    s.rect(bx, by, 820, 150, sw=1.4, dash="6,4"); s.text(bx + 8, by + 14, "alt  [msg count mod k == 0  or  miss]  — refresh", size=10, mono=True, color=ACCENT)
    y = by + 36
    y = s.msg(X["KEY / REVOCATION CACHE"], X["LEDGER (RPC)"], y, 6, "changed(did) probe (1 RPC, 2.76 ms #37) or full resolve (4 RPC, 10.5 ms #32)") + 28
    y = s.msg(X["LEDGER (RPC)"], X["KEY / REVOCATION CACHE"], y, 7, "head block / events → key, validTo, revocation", dash="6,4") + 24
    s.line(bx, y + 4, bx + 820, y + 4, stroke=LINE_SOFT, sw=0.8, dash="3,3"); s.text(bx + 8, y + 18, "[else] — hit: 0 RPC", size=10, mono=True, color=ACCENT)
    y = by + 150 + 30
    y = s.msg(X["KEY / REVOCATION CACHE"], X["RECEIVER VERIFIER"], y, 8, "key, valid? (validTo > now)", dash="6,4") + 28
    y = s.msg(X["RECEIVER VERIFIER"], X["RECEIVER VERIFIER"], y, 9, "ecrecover(keccak(BSM), sig) == key → accept  (0.153 ms warm #27)", self_call=True) + 26
    # instrument strip
    ix, iy = 100, y1 + 20
    rows = [("per-neighbour cost t", "0.153 ms warm / 0.399 cold", "#27"), ("t_eff(k) full refresh", "0.428 + 10.52 / k  ms", "#32 (±7 %)"), ("k for P*(0.5) = 100", "≈ 146 full; none on #37 host", "#32 / #37"),
            ("P*(0.5) at k = ∞", "110 (mean) · 609 extrap. (#26)", "#32, #26"), ("staleness bound", "≤ k − 1 msgs; 14.5 s at k=146", "#32")]
    s.table(ix, iy, [("QUANTITY", 220), ("VALUE", 300), ("ROW", 120)], rows, size=10, lh=19)
    s.text(ix + 660, iy + 20, "Uncached (k = 1): 10.9 ms, P*(0.5) = 4", size=10, mono=True, color=WARN)
    s.text(ix + 660, iy + 36, "→ not viable even in sparse traffic.", size=10, mono=True, color=WARN)
    s.text(ix + 660, iy + 60, "Cached (k → ∞): 0.45 ms mean, P*(0.5) = 110", size=10, mono=True, color=OK)
    s.text(ix + 660, iy + 76, "→ viable in dense traffic.", size=10, mono=True, color=OK)
    s.text(ix + 660, iy + 100, "Cost lives at issuance, not at", size=10, mono=True, color=ACCENT)
    s.text(ix + 660, iy + 114, "verification (COMPOSITION Part I).", size=10, mono=True, color=ACCENT)
    return s


def bp303():
    s = Sheet("BP-303", "Sequence — ownership transfer and key rotation", "SV-10c: resale (U4) with device key rotation (U2 + D1), re-registration (V3) and revocation of the old insurance (V5)",
              notes=["Lifecycle events 11–15 of the MOBI VID II sequence (framework §4.4): key rotation, ownership transfer, re-registration credential, revoke old insurance, second transfer.",
                     "On ERC-1056 U4 is two transactions (changeOwner + updateOwnershipMapping) or one via the wrapper (transferVehicleOwnership); txCount is recorded per op (BP-102 ⑩).",
                     "Authorization at every step is msg.sender == identityOwner (G1) or an issuer role (G4); the 54-scenario suite asserts the unauthorized variant of each step reverts (BP-403)."],
              notes_width=1060,
              refs=["cv2x-testbed/scripts/test_use_cases.py — use case 3 (used-car sale), 11 (dealer-mediated)", "1_blockchain-identity/benchmarks/scenarios/lifecycle.js (events 11–15) · contracts/ERC1056/CVINVehicleDIDRegistry.sol"])
    x0, y0, y1 = 100, 215, 800
    cols = [("SELLER (owner A)", "controls did", x0 + 90), ("BUYER (owner B)", "new controller", x0 + 350), ("REGISTRY", "ERC-1056 / wrapper", x0 + 620), ("LEDGER", "L2–L3", x0 + 860),
            ("ISSUER (DMV)", "registration VC", x0 + 1100), ("INSURER", "old policy", x0 + 1340)]
    for name, sub, cx in cols:
        s.lifeline(cx, y0, y1, name, sub, w=170)
    X = {n: cx for n, _, cx in cols}
    y = y0 + 70
    y = s.msg(X["SELLER (owner A)"], X["REGISTRY"], y, 1, "revokeDelegate(did, veriKey, oldDeviceKey)   [D1, event 11]", note="old telematics key dies immediately (validTo = now)") + 40
    y = s.msg(X["SELLER (owner A)"], X["REGISTRY"], y, 2, "changeOwner(did, B)   [U1/U4, event 12]", note="onlyOwner(did, msg.sender): A == identityOwner(did)") + 40
    y = s.msg(X["REGISTRY"], X["LEDGER"], y, 3, "owners[did] = B; DIDOwnerChanged(did, B, prev); changed[did] = block") + 30
    y = s.msg(X["SELLER (owner A)"], X["REGISTRY"], y, 4, "updateOwnershipMapping (wrapper) — 2nd tx on pure mode", dash="6,4", note="or one tx: transferVehicleOwnership (wrapper-controlled)") + 40
    y = s.msg(X["BUYER (owner B)"], X["REGISTRY"], y, 5, "addDelegate(did, veriKey, newDeviceKey, ttl)   [U2, event 11]", note="now B == identityOwner; A's call here reverts") + 40
    y = s.msg(X["ISSUER (DMV)"], X["ISSUER (DMV)"], y, 6, "issue RegistrationCredential VC (subject did, holder B)", self_call=True) + 26
    y = s.msg(X["ISSUER (DMV)"], X["REGISTRY"], y, 7, "V3 anchor credential status on issuer identity   [event 13]") + 30
    y = s.msg(X["INSURER"], X["REGISTRY"], y, 8, "V5 revoke old insurance credential   [event 14]", note="issuer-only; owner cannot un-revoke (sticky on CVIN)") + 40
    y = s.msg(X["BUYER (owner B)"], X["BUYER (owner B)"], y, 9, "holds: VC (registration), disclosures; presents on demand [BP-203]", self_call=True) + 26
    s.text(x0, y1 + 30, "Adversary checks drawn from BP-403: A (after 2) calling 5 → revert; replaying 2's signature on another identity → revert (nonce/identity-bound); insurer revoking a credential it did not issue → revert.", size=10, mono=True, color=ACCENT)
    return s


def bp304():
    s = Sheet("BP-304", "State machine — vehicle identity over its life", "UML state diagram of the MOBI VID I + II lifecycle sequence (17 events) with the actor that fires each transition",
              notes=["States are the identity's observable condition on-chain; transitions are the catalogue ops (BP-104) with the actor who may fire them (role gate G4).",
                     "Lifetime gas over this sequence is the L2 result (#30/#31): ranking by lifetime reverses the point ranking for some pairs; the hybrid is tunable via the claim fraction f.",
                     "DECOMMISSIONED is terminal; several substrates lack a native deactivate and realise D3 as a documented workaround (attribute flag, transfer to 0xdEaD, burn)."],
              notes_width=1060,
              refs=["docs/CVIN-DATA-COLLECTION-FRAMEWORK.md §4.4 (lifecycle event table)", "4_comparison-framework/results/scaling_lifetime.json (#31) · 1_blockchain-identity/results/metrics/latest/tables/lifecycle_gas.md (#30)"])
    # states laid out left→right in two rows
    S = {}
    def st(key, x, y, name, sub=""):
        S[key] = (x, y, 190, 56); s.state(x, y, 190, 56, name, sub)
    st("unborn", 90, 300, "UNBORN", "address exists, no VIN")
    st("born", 360, 300, "REGISTERED", "VID-I birth · C2")
    st("cred", 630, 300, "CREDENTIALED", "V1 V2 V3 · events 2–4")
    st("service", 900, 300, "IN SERVICE", "U3 × 6 · events 5–10")
    st("rotated", 1170, 300, "KEY ROTATED", "U2 + D1 · event 11")
    st("owned2", 1170, 520, "TRANSFERRED", "U4 · event 12 (and 15)")
    st("rereg", 900, 520, "RE-REGISTERED", "V3 · event 13 · V5 · 14")
    st("decom", 630, 520, "DECOMMISSIONED", "D3 · event 16/17 · terminal")
    def tr(a, b, label, actor, via="h", dy=0):
        ax, ay, aw, ah = S[a]; bx, by, bw, bh = S[b]
        if ay == by:
            s.arrow(ax + aw, ay + ah / 2 + dy, bx, by + bh / 2 + dy, head=7)
            s.text((ax + aw + bx) / 2, ay - 10 + dy, label, size=9, anchor="middle", mono=True)
            s.text((ax + aw + bx) / 2, ay + ah + 16 + dy, actor, size=9, anchor="middle", mono=True, color=ACCENT)
        elif ax == bx:
            s.arrow(ax + aw / 2, ay + ah, bx + bw / 2, by, head=7)
            s.text(ax + aw / 2 + 8, (ay + ah + by) / 2, f"{label}  ·  {actor}", size=9, mono=True)
        else:
            s.arrow(ax, ay + ah / 2, bx + bw, by + bh / 2, head=7)
            s.text((ax + bx + bw) / 2, ay + ah / 2 - 8, label, size=9, anchor="middle", mono=True)
            s.text((ax + bx + bw) / 2, ay + ah / 2 + 18, actor, size=9, anchor="middle", mono=True, color=ACCENT)
    s.circle(40, 328, 8, fill=LINE); s.arrow(48, 328, 90, 328, head=7)
    tr("unborn", "born", "C2 birth certificate", "manufacturer")
    tr("born", "cred", "V1 · V2+V3 · V3", "issuer")
    tr("cred", "service", "U3 endpoint; 5 × service", "owner / service centre")
    tr("service", "rotated", "U2 + D1", "owner")
    tr("rotated", "owned2", "U4 transfer", "owner → newOwner")
    tr("owned2", "rereg", "V3 re-reg · V5 revoke", "issuer")
    tr("rereg", "decom", "D3 end-of-life", "admin / owner")
    # second transfer loop
    s.poly([(1265, 576), (1265, 640), (995, 640), (995, 576)], stroke=LINE_SOFT, sw=1.2, dash="5,4")
    s._head(995, 600, 995, 578, LINE_SOFT, 7)
    s.text(1130, 656, "U4 second transfer (event 15): newOwner → third", size=9, anchor="middle", mono=True, color=LINE_SOFT)
    # terminal
    s.circle(560, 548, 10, sw=2.0); s.circle(560, 548, 5, fill=LINE); s.arrow(630, 548, 572, 548, head=7)
    # self loops on IN SERVICE
    s.poly([(995, 300), (995, 250), (1060, 250), (1060, 300)], stroke=LINE_SOFT, sw=1.2); s._head(1060, 290, 1060, 300, LINE_SOFT, 7)
    s.text(1028, 240, "U3 / addServiceRecord × 5 (service centre)", size=9, anchor="middle", mono=True, color=LINE_SOFT)
    # table of events (compact) bottom-left
    tx, ty = 90, 690
    rows = [("1", "C2", "manufacturer"), ("2", "V1", "issuer"), ("3–4", "V2+V3, V3", "issuer"), ("5–10", "U3 ×6", "owner, service"), ("11", "U2+D1", "owner"), ("12", "U4", "owner"), ("13", "V3", "issuer"), ("14", "V5", "issuer"), ("15", "U4", "newOwner"), ("16", "D3", "admin/owner")]
    s.table(tx, ty, [("#", 50), ("OP", 110), ("ACTOR", 130)], rows[:5], size=9, lh=16)
    s.table(tx + 310, ty, [("#", 50), ("OP", 110), ("ACTOR", 130)], rows[5:], size=9, lh=16)
    s.text(tx + 640, ty + 20, "Lifetime total = Σ events; apportioned deploy cost per fleet size {1, 10³, 10⁶}", size=10, mono=True, color=LINE_SOFT)
    s.text(tx + 640, ty + 38, "decides whether contract-per-identity standards can ever compete (framework §4.4).", size=10, mono=True, color=LINE_SOFT)
    return s


SHEETS = [bp301, bp302, bp303, bp304]
