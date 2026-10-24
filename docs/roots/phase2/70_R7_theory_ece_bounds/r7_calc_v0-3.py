#!/usr/bin/env python3
"""R7 v0-3 calculator (copy of r7_calc_v0-2.py with R9 v0-2 PN-34/PN-37 applied; earlier scripts kept unchanged).

Every number in R7 v0-3 is printed here with its equation and inputs. Print labels are the
document's PF numbering, one to one (PN-10). The final section reads the v0-3 document and
asserts that every PF tag it prints appears in this output, and that every R7-owned PF tag
printed here appears in the document.

Run: python3 r7_calc_v0-3.py      (python3, numpy, scipy; seeds fixed per Monte-Carlo block)
Exit status 0 only if the self-check passes.

Header map (v0-1 working label -> v0-2 document PF), per R9 PN-10:
  32/33 RNG -> PF-41/42 | 34 verify load -> PF-43 | 35 composition -> PF-36
  36 airtime -> PF-44   | 36b PC5 capacity -> PF-44 | 36c reselection -> PF-45 (new split)
  37 QBFT messages -> PF-38 | 38 t_conf -> PF-40 | 39/40/41 GNSS -> PF-47 (window) and PF-53 (cache)
  42 backhaul -> PF-48 | 43/44 gas -> PF-49/50 | 45 Groth16 -> PF-51 | 46 storage -> PF-52
  47/48/49 freshness -> PF-54/55/56 | 50 gossip -> dropped as a PF (no P2P in repo; PAR-37)
  51 HHI -> PF-60 | 52 VIN entropy -> PF-33/PF-62 | new: PF-46 (PC5 loss bracket), PF-63..66 (R8 request)
Inputs: M = register row / result file, S = standard, E = estimated, P = parameter (R8 PAR-nn)."""
import math, os, re, sys, json, io, contextlib
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "claude_CVIN_SC_Roots_Theory_ECE_Bounds_R7_v0-3.md")
META = os.path.normpath(os.path.join(HERE, "../../../../1_blockchain-identity/results/metrics/latest/meta.json"))

_buf = io.StringIO()
class Tee:
    def write(self, s): sys.__stdout__.write(s); _buf.write(s)
    def flush(self): sys.__stdout__.flush()
sys.stdout = Tee()

def p(tag, eq, val, inputs=""): print(f"[{tag}] {eq} = {val}   {inputs}")
def binom_tail(N, j, pc): return sum(math.comb(N, i) * pc**i * (1 - pc)**(N - i) for i in range(j, N + 1))

# ---------------------------------------------------------------- A
print("== A. Phase-1 R4 re-checks and R4 PFs cited by R7 ==")
p("PF-02", "sqrt(2*2^160*1e-12)", f"{math.sqrt(2*2**160*1e-12):.3e}", "R4 re-check")
n = 1.5e9 * 1040 * 20
p("PF-04", "n=V*K*Y", f"{n:.3e}", "V=1.5e9 (PAR-42, E), K=1040 (PAR-22, E), Y=20")
p("PF-04", "n^2/2^161", f"{n**2/2**161:.2e}")
rate = n / (20 * 365.25 * 86400)
p("PF-24", "fleet rate n/(20 y)", f"{rate:.3e} /s")
for Nv in (4, 7, 10, 13, 16, 22):
    fB = (Nv - 1) // 3
    print(f"[PF-16] Nv={Nv} fB={fB}: " + "  ".join(f"pc={pc}:{binom_tail(Nv, fB+1, pc):.2e}" for pc in (0.01, 0.05, 0.10, 0.20)))
def nak(q, z):
    pp = 1 - q; lam = z * q / pp; s = 1.0
    for k in range(z + 1): s -= math.exp(-lam) * lam**k / math.factorial(k) * (1 - (q / pp)**(z - k))
    return s
for q in (0.1, 0.3, 0.4): print(f"[PF-19] q={q}: " + " ".join(f"z{z}:{nak(q, z):.2e}" for z in (1, 3, 6, 12, 24, 48)))
for q in (0.1, 0.3): p("PF-19", f"min z for <1e-6 at q={q}", next(z for z in range(1, 200) if nak(q, z) < 1e-6))
# R4 PFs that R7 cites but does not recompute (so the self-check can see every cited tag):
for t, what in (("PF-01", "R4 range start PF-01..31 (consumed, frozen)"), ("PF-06", "effective security min(2^128, 2^kappa) (R4)"), ("PF-07", "two-signature nonce reuse (R4)"),
                ("PF-09", "BHT quantum collision 2^85 (R4)"), ("PF-10", "BN254 ~100-bit after TNFS (R4; LIM-R7-06)"),
                ("PF-11", "multi-party setup p_s^t_s (R4)"), ("PF-13", "public anchoring detection (R4)"),
                ("PF-15", "resolver staleness sigma (R4)"), ("PF-17", "liveness timer (R4)"),
                ("PF-25", "fault-free t_conf 1.5*Delta (R4; recovered in PF-40)"), ("PF-28", "W composition, W_0=8.5 s (R4, DESIGN)"),
                ("PF-29", "status-list anonymity set (1-rho)m (R4)"), ("PF-30", "governance key analogue (R4)"),
                ("PF-31", "RPC read O(10-200 ms) (R4)")):
    print(f"[{t}] cited from R4, not recomputed here: {what}")

# ---------------------------------------------------------------- B
print("\n== B. QBFT quorums (PF-37) and message complexity (PF-38) -- DESIGN ==")
for Nv in (4, 7, 10, 13, 16, 22):
    fB = (Nv - 1) // 3; Q = math.ceil(2 * Nv / 3)
    print(f"[PF-37] Nv={Nv:2d} fB={fB} quorum ceil(2N/3)={Q} validators to break safety=halt liveness=fB+1={fB+1}")
for Nv in (4, 7, 10, 13, 16, 22):
    pre = Nv - 1; prep = Nv * (Nv - 1); com = Nv * (Nv - 1); rc = Nv * (Nv - 1); tot = pre + prep + com
    assert tot == (Nv - 1) * (2 * Nv + 1)
    print(f"[PF-38] Nv={Nv:2d} pre={pre} prepare={prep} commit={com} M=(N-1)(2N+1)={tot} +RC={tot+rc} "
          f"kB/round@200B(E)={tot*200/1e3:.1f} kB/s@Delta=2s(PAR-05)={tot*200/2/1e3:.1f} verifies/validator/height=2N-1={2*Nv-1}")

# ---------------------------------------------------------------- C
print("\n== C. Hardhat automine as N_v = 1 (PF-39) ==")
try:
    meta = json.load(open(META)); net = meta["network"]
    p("PF-39", "meta.json network", f"automine={net['automine']} chainId={net['chainId']} blockGasLimit={net['blockGasLimit']} hardfork={net['hardfork']}", f"runId={meta['runId']} (M)")
    G_HH = int(net["blockGasLimit"]); HARDFORK = net["hardfork"]
    assert net["automine"] is True
except Exception as e:
    p("PF-39", "meta.json not readable; using recorded constant", 60_000_000, f"({e})"); G_HH = 60_000_000; HARDFORK = "osaka"
p("PF-39", "N_v=1, f_B=0: P(safety failure)=p_c (one operator); t_finalise", "0 (no Delta exists)")

print("\n== D. Time-to-confirm under round changes (PF-40) and metric (PF-57) -- DESIGN ==")
rng = np.random.default_rng(42)
def qbft_sample(Delta, Dc, phi, trc, M=400000):
    inc = rng.uniform(0, Delta, M); extra = np.zeros(M); alive = np.ones(M, bool)
    for k in range(30):
        fail = alive & (rng.random(M) < phi); extra[fail] += trc * 2**k; alive = fail
        if not alive.any(): break
    return inc + Dc + extra
for (Delta, phi, trc) in ((2, 0.0, 10), (2, 0.25, 10), (2, 1/7, 10), (5, 0.25, 10)):
    s = qbft_sample(Delta, Delta, phi, trc)
    print(f"[PF-40] MC seed 42: Delta={Delta} phi={phi:.3f} t_rc={trc}: E={s.mean():.2f}s p99={np.percentile(s,99):.2f}s p999={np.percentile(s,99.9):.2f}s")
for phi in (0.25, 1/7): p("PF-40", "E_extra=t_rc*phi/(1-2phi)", f"{10*phi/(1-2*phi):.3f} s", f"phi={phi:.3f}, t_rc=10 (PAR-31)")
def rr(Nv, crashed, trc=10, Delta=2):
    ex = []
    for i in range(Nv):
        c = 0
        while ((i + c) % Nv) in crashed and c < Nv: c += 1
        ex.append(trc * (2**c - 1))
    return 1.5 * Delta + sum(ex) / Nv, 2 * Delta + max(ex)
for Nv, cr in ((4, {0}), (7, {0}), (7, {0, 1}), (10, {0, 1, 2}), (22, set(range(7)))):
    E, Wc = rr(Nv, cr); print(f"[PF-40] round-robin exact Nv={Nv} adjacent crashed={len(cr)}: E[t_conf]={E:.2f}s worst={Wc:.0f}s (Delta=2, t_rc=10)")
p("PF-40", "fault-free E / max", "3.0 s / 4.0 s", "1.5*Delta / 2*Delta, Delta=2 (recovers R4 PF-25)")
for z in (6, 11):
    p("PF-57", f"PoW comparison Erlang(z={z},600 s) mean / p99", f"{z*600/3600:.2f} h / {stats.gamma.ppf(0.99, z, scale=600)/3600:.2f} h")
p("PF-57", "Gasper finality 2 epochs*32 slots*12 s", f"{2*32*12} s")

# ---------------------------------------------------------------- E
print("\n== E. Cryptographic bounds (PF-32..36) ==")
for lq in (64, 80, 100): p("PF-32", "GGM Adv<=q^2/n_G", f"2^{2*lq-256}", f"q=2^{lq}")
for b in (1, 2, 4, 8): p("PF-32", f"nonce bias b={b}: order of signatures ~256/b", 256 // b, "(E, order of magnitude)")
p("PF-33", "VIN serial min-entropy log2(1e6)", f"{math.log2(1e6):.2f} bits")
p("PF-33", "enumeration time 1e6/279587 hashes/s", f"{1e6/279587:.2f} s", "(#60, M)")
p("PF-34", "hash-commitment binding <= Adv^CR", "2^-128", "hiding = min-entropy of salt||x; unsalted VIN = 19.93 bits")
p("PF-35", "repo setup single-party: P(trapdoor known)", "p_s (t_s=1)", "(#57: single-party, insecure)")
eL4 = binom_tail(4, 2, 0.05)
terms = {"sig (computational)": 2**-128, "hash CR (computational)": 2**-128,
         "ledger equivocation Nv=4 pc=.05 (governance prior)": eL4, "resolver integrity (implementation prior, assumed)": 1e-6}
for k, v in terms.items(): p("PF-36", f"eps[{k}]", f"{v:.3e}")
p("PF-36", "union bound over failure events, Nv=4", f"{sum(terms.values()):.3e}")
p("PF-36", "orders of magnitude ledger vs one crypto term log10(eL/2^-128)", f"{math.log10(eL4/2**-128):.1f}")
terms1 = dict(terms); terms1["ledger equivocation Nv=4 pc=.05 (governance prior)"] = 0.0
p("PF-36", "executed instance Nv=1: eps_L = p_c", "0.05", "p_c=0.05 (E)")
p("PF-36", "union bound, Nv=1", f"{sum(terms1.values()) + 0.05:.3e}")
nD = 3.12e13
p("PF-36", "multi-user loss log2(n_D)", f"{math.log2(nD):.1f} bits -> 128-{math.log2(nD):.1f} = {128-math.log2(nD):.1f} bits")
bits = min(128, 128, -math.log2(eL4), -math.log2(1e-6)) - math.log2(4)
p("PF-59", "bits = min_i(-log2 eps_i) - log2(#terms=4), Nv=4", f"{bits:.2f}", "(ledger-dominated)")

# ---------------------------------------------------------------- F
print("\n== F. RNG and key generation (PF-41, PF-42) -- ESTIMATED illustrations (DRP-07) ==")
for kap in (32, 40, 48, 128, 256):
    c = -math.expm1(-n * (n - 1) / 2 / 2**kap) if kap >= 48 else 1.0
    pairs = "  ".join(f"devices={nv:.1e}:{nv**2/2**(kap+1):.3e}" for nv in (1e6, 1.5e9))
    print(f"[PF-41] kappa={kap}: P(shared key among n={n:.2e}) = {c:.3e}; expected colliding pairs n^2/2^(k+1): {pairs}")
for H in (1.0, 0.5, 0.1): p("PF-42", "RCT cut-off C=1+ceil(20/H)", 1 + math.ceil(20 / H), f"alpha=2^-20, H={H} (S: SP 800-90B)")
for r_, H in ((1e6, 0.5), (1e4, 0.5), (100, 0.8)): p("PF-42", "seed time (256+64)/(r*H)", f"{(256+64)/(r_*H):.4g} s", f"r={r_}/s H={H} (E)")

# ---------------------------------------------------------------- G
print("\n== G. Verification load (PF-43) ==")
classes = {"Xeon software SSI warm (#27, M)": 0.142, "Xeon software PKI warm (#27, M)": 0.090,
           "V2X ASIC/HSM class (E)": 0.25, "Cortex-A53-class software (E)": 1.0, "MCU HSM EVITA-full class (E)": 5.0}
neigh = (50, 100, 200, 300)
for name, t in classes.items():
    print(f"[PF-43] {name}: t_ver={t} ms v_max={1000/t:,.0f}/s P*(0.5)=floor(50/t)={int(50/t)} P*(1)={int(100/t)} rho at "
          + ", ".join(f"P={P}:{P*10*t/1000:.2f}" for P in neigh))
S26 = 0.156  # register #26 slope, ms/neighbour (re-stated 2026-10-23, A3b Exp. D at 0b39570; PN-34)
p("PF-43", f"#26 linear model P*(0.5)=floor(50/{S26}) (M model, lead figure)", f"{int(50/S26)} ({50/S26:.1f})", f"register #26 ({S26} ms/neighbour, R^2 1.0000)")
p("PF-43", f"#26 linear model P*(1)=floor(100/{S26})", f"{int(100/S26)} ({100/S26:.1f})", "register P* ~ 641; linear extrapolation beyond P<=80 (DRP-03)")
for t in (0.25, 1.0):
    for P in (100, 200, 300):
        rho = P * 10 * t / 1000
        if rho < 1: p("PF-43", f"M/D/1 t={t} P={P} rho={rho:.2f} sojourn=t+rho*t/(2(1-rho))", f"{t+rho*t/(2*(1-rho)):.3f} ms")
        else: p("PF-43", f"M/D/1 t={t} P={P}", f"rho={rho:.2f} >= 1 unstable")
for t in (1.0, 5.0):
    for P in (200, 300): p("PF-43", f"verify-on-demand phi_v=min(1,f/rho) t={t} P={P}", f"{min(1, 0.5/(P*10*t/1000)):.3f}", "(E, practice)")
for k in (1, 25, 90):
    for P in (100, 300): p("PF-43", f"ledger reads/s per verifier=10*P/k k={k} P={P}", f"{10*P/k:.1f}")
tl, tc = 0.346, 13.94   # #32 A3b re-run
for P in (100, 300):
    p("PF-43", f"refresh-load criterion k_f >= r*P*t_chain/f_id, P={P} (PN-11 corrected)", f"{10*P*tc/1000/0.5:.1f}", "r=10 Hz, t_chain=13.94 ms, f_id=0.5")
    p("PF-43", f"v0-1 erroneous form r*P*t_chain/(f_id/r), P={P}", f"{10*P*tc/1000/(0.5/10):.1f}", "extra factor r (s^-1)")
    budget = 0.5 * 100 / P
    kk = math.ceil(tc / (budget - tl)) if budget > tl else None
    p("PF-43", f"total-budget criterion k_f >= t_chain/(f_id/(r*P) - t_local), P={P}", kk if kk else "infeasible (t_local exceeds per-message share)", f"per-message share {budget:.3f} ms")
for name, ts in (("ASIC/HSM (E)", 0.5), ("MCU HSM (E)", 10.0)): p("PF-43", f"signing duty 10 Hz*t_sig ({name})", f"{10*ts/1000:.3f}", f"t_sig={ts} ms")

# ---------------------------------------------------------------- H
print("\n== H. Channel airtime and capacity (PF-44) ==")
def t11p(L, rate=6):
    bps = {3: 24, 6: 48, 12: 96}[rate]; return 40 + 8 * math.ceil((16 + 8 * L + 6) / bps)
MAC, WSMP, core, AIFS = 36, 6, 40, 58
sec = [("none", 0), ("1609.2 digest", 86), ("1609.2 implicit cert", 162), ("1609.2 explicit cert", 210),
       ("repo JSON ERC-1056 (#23 596 B)", None), ("repo JSON PKI (#23 1,110 B)", None)]
for name, s in sec:
    L = ((596 if "ERC" in name else 1110) + MAC) if s is None else core + s + WSMP + MAC
    T = t11p(L) + AIFS
    print(f"[PF-44] 802.11p {name}: MPDU={L} B T_air={t11p(L)} us +AIFS {AIFS} = {T} us CBR/vehicle@10Hz={10*T*1e-6:.4f} N_fit@CBR0.6={0.6/(10*T*1e-6):.0f}")
T0 = t11p(core+WSMP+MAC)+AIFS; Td = t11p(core+86+WSMP+MAC)+AIFS; Te = t11p(core+210+WSMP+MAC)+AIFS
p("PF-44", "security share of airtime digest / explicit", f"{(Td-T0)/Td:.2f} / {(Te-T0)/Te:.2f}")
Tmix = 0.2 * Te + 0.8 * Td
p("PF-44", "T_mix=0.2*T_cert+0.8*T_digest", f"{Tmix:.0f} us; N_fit@0.6 = {0.6/(10*Tmix*1e-6):.0f}")
Tj = t11p(596+MAC)+AIFS; Tp = t11p(1110+MAC)+AIFS
p("PF-44", "repo JSON airtime / digest airtime", f"{Tj/Td:.1f}x (ERC-1056), {Tp/Td:.1f}x (PKI)")
B_SC = 190
for name, L in (("none", core+WSMP+20), ("digest", core+86+WSMP+20), ("implicit cert", core+162+WSMP+20),
                ("explicit cert", core+210+WSMP+20), ("repo JSON ERC-1056", 596), ("repo JSON PKI", 1110)):
    nsc = math.ceil(L / B_SC); cap = 5 // nsc * 1000 if nsc <= 5 else 0
    print(f"[PF-44] PC5 {name}: L={L} B subchannels={nsc} packets/s/10MHz={cap} vehicles@10Hz CBR1={cap/10:.0f} CBR0.6={0.6*cap/10:.0f}"
          + ("  (exceeds one sub-frame at this MCS)" if nsc > 5 else ""))

# ---------------------------------------------------------------- I
print("\n== I. PC5 SPS resource reselection and RF linkability (PF-45; split from PF-44, PN-12) ==")
RRI, Cs = 0.1, np.arange(5, 16)
def persist_exact(pk, x, nmax=400):
    """P(resource still held x s after a uniformly random instant) = E[(L-x)+]/E[L], L = lifetime of one
    resource = RRI * sum of N counters, N ~ Geometric(1-pk), counters iid U{5..15}. Exact via pmf convolution."""
    pmf1 = np.zeros(16); pmf1[5:16] = 1 / 11            # in units of RRI
    tot = np.zeros(16 * nmax); cur = np.array([1.0]); w = 1 - pk
    for m in range(1, nmax + 1):
        cur = np.convolve(cur, pmf1); tot[:len(cur)] += w * cur; w *= pk
        if w < 1e-16: break
    L = np.arange(len(tot)) * RRI
    return (np.maximum(L - x, 0) * tot).sum() / (L * tot).sum(), (L * tot).sum()
mc = np.random.default_rng(2026)
for pk in (0.0, 0.4, 0.8):
    pe, EL = persist_exact(pk, 1.0)
    M = 400000; Lm = np.zeros(M); alive = np.ones(M, bool)
    while alive.any():
        Lm[alive] += RRI * mc.integers(5, 16, alive.sum()); alive &= mc.random(M) < pk
    pmc = np.maximum(Lm - 1.0, 0).mean() / Lm.mean()
    p("PF-45", f"P_keep={pk}: E[lifetime]=E[C]*RRI/(1-P_keep)", f"{EL:.3f} s")
    p("PF-45", f"P_keep={pk}: P(same resource 1 s after pseudonym change)=E[(L-1)+]/E[L] exact", f"{pe:.3f}", f"(MC seed 2026, 4e5 draws: {pmc:.3f}; v0-1 exp approx {math.exp(-1/EL):.3f})")
    p("PF-45", f"P_keep={pk}: persistence at x = 0.1 / 0.5 / 2 s", " / ".join(f"{persist_exact(pk, x)[0]:.3f}" for x in (0.1, 0.5, 2.0)))

# ---------------------------------------------------------------- J
print("\n== J. PC5 packet-loss bracket vs load (PF-46; first-order, no propagation) ==")
for s, label in ((1, "digest (1 sub-channel)"), (2, "certificate (2 sub-channels)")):
    Rs = 100 * (5 // s)   # non-overlapping resources per 100 ms RRI
    for nveh in (100, 200, 300):
        cbr = nveh * s / (Rs * s)  # occupied fraction of resources
        if nveh >= Rs: p("PF-46", f"{label} n={nveh}", "CBR >= 1: offered load exceeds resources per RRI (no bracket)"); continue
        hd = 1 - (1 - 1 / 100) ** (nveh - 1) if False else 1 / 100    # receiver's own sub-frame (half duplex), per link
        rnd = 1 - (1 - 1 / Rs) ** (nveh - 1)
        pr = (1 - 0.0) / 10   # reselection per RRI at P_keep=0, E[C]=10
        free = max(Rs * (1 - cbr), 1)
        sen = min(1 - (1 - pr / free) ** (nveh - 1), 1 - hd)
        p("PF-46", f"{label} n={nveh} CBR={cbr:.2f}: P_loss ~ P_HD + P_coll in [sensing-ideal, random]",
          f"[{hd+sen:.3f}, {hd+rnd:.3f}]", f"R={Rs}/RRI, P_HD=1/100, p_resel=0.1 (E)")

# ---------------------------------------------------------------- K
print("\n== K. GNSS clock window (PF-47) and replay cache (PF-53) ==")
for d in (0.5, 2, 20, 50):
    T = 0.1 / (2 * d * 1e-6); p("PF-47", "T_hold=T_max,fut/(2 d_clk)", f"{T:.0f} s = {T/3600:.2f} h", f"d={d} ppm")
p("PF-47", "GNSS-locked margin 0.1 s / 1e-7 s", f"{0.1/1e-7:.0e}x", "(E)")
for v in (14, 30, 40): p("PF-47", "position staleness v*T_max,age", f"{v*1.0:.0f} m", f"v={v} m/s")
for P in (50, 100, 300, 600): p("PF-53", "entries=10*P*1.1", f"{10*P*1.1:.0f}", f"P={P}")
p("PF-53", "senders without eviction 65536/11", f"{65536//11}")
p("PF-53", "docstring check 65536/(10*1.1*10)", f"{65536/(10*1.1*10):.0f}", "(docstring says ~650; CA-08)")

# ---------------------------------------------------------------- L
print("\n== L. RSU backhaul renewal model (PF-48) -- DESIGN ==")
rng2 = np.random.default_rng(42); W0 = 8.5; maxdev = 0.0
for mu_off in (10, 60, 600):
    for A in (0.99, 0.95, 0.90):
        M = 2_000_000
        down = rng2.random(M) > A; W = W0 + np.where(down, rng2.exponential(mu_off, M), 0.0)
        EW = W0 + (1 - A) * mu_off
        p99 = W0 if (1 - A) <= 0.01 + 1e-12 else W0 + mu_off * math.log((1 - A) / 0.01)
        p999 = W0 + mu_off * math.log((1 - A) / 0.001) if (1 - A) > 0.001 else W0
        m99, m999 = np.percentile(W, 99), np.percentile(W, 99.9)
        for a, b, q_ in ((EW, W.mean(), None), (p99, m99, 0.99), (p999, m999, 0.999)):
            if q_ is not None and abs((1 - A) - (1 - q_)) < 1e-9: continue   # quantile sits on the atom edge: degenerate
            maxdev = max(maxdev, abs(a - b) / a)
        print(f"[PF-48] mu_off={mu_off}s A_L={A}: E[W]={EW:.2f}s (MC {W.mean():.2f}) p99={p99:.1f}s (MC {m99:.1f}) p99.9={p999:.1f}s (MC {m999:.1f})")
p("PF-48", "max relative MC deviation, non-degenerate cells (2e6 draws, seed 42)", f"{100*maxdev:.2f} %")
for cv in (0, 1, 2): p("PF-48", "E[resid]=mu_off*(1+cv^2)/2", f"{(1+cv**2)/2:.1f}*mu_off", f"cv={cv}")
for Tp in (1, 10, 60): p("PF-48", "poll period adds mean T_p/2, max T_p", f"{Tp/2} / {Tp} s")

# ---------------------------------------------------------------- M
print("\n== M. Gas, capacity, Groth16, storage (PF-49..52) ==")
g = {"C1 create (ERC-1056)": 76830, "U1 changeOwner": 51754, "U2 addDelegate": 55143, "U3 setAttribute": 35024,
     "U5 setAttributeSigned": 62646, "D1 revokeDelegate": 32868, "D2 revokeAttribute": 34576, "V3 anchor status": 33918,
     "V5 revoke credential": 33470, "P1 presentation": 34206, "RSU anchor key (#47)": 52606, "pseudonym addDelegate (#38)": 54807,
     "CVIN-Combined C1": 271402, "ERC-4337 U5": 141767, "MOBI attestEvent (#28)": 198694, "ZkVinGate.admit (#58)": 301163, "ERC-735 C1": 1757881}
for name, go in g.items():
    print(f"[PF-49] G={G_HH/1e6:.0f}M {name}: g={go:,} ops/block={G_HH//go:,} ops/s D=1:{G_HH/go:,.0f} D=2:{G_HH/go/2:,.0f} D=5:{G_HH/go/5:,.0f} D=12:{G_HH/go/12:,.0f}")
for GG in (30e6, 60e6, 100e6):
    print(f"[PF-49] G={GG/1e6:.0f}M (PAR-06), Delta=2 s (PAR-05): C1 {GG/76830/2:,.0f} ops/s; U3 {GG/35024/2:,.0f}; V5 {GG/33470/2:,.0f}; admit {GG/301163/2:,.0f}")
for GG in (30e6, 60e6, 100e6):
    p("PF-50", f"fleet ratio addDelegate at G={GG/1e6:.0f}M, Delta=2", f"{rate*54807/(GG/2):.1f}x", "upper bound on a privacy-excluded design (BP-L7.2-01)")
p("PF-50", "fleet ratio C1 at 60M, Delta=2", f"{rate*76830/(G_HH/2):.1f}x")
p("PF-50", "blocks/day needed vs available (60M, Delta=2)", f"{rate*54807*86400/G_HH:,.0f} vs {86400/2:,.0f}")
p("PF-50", "#38 route 1.5e9*1,096,368 gas/week / (G per 2 s)", f"{1.5e9*1096368/(G_HH*7*86400/2):.1f}x")
p("PF-50", "did:ethr creation gas (#47)", 0)
k = 4; npub = 7; pair = 45000 + 34000 * k; ecm = 6000 * npub + 150 * npub; cdb = 4 + 256 + 32 * npub; cd = 16 * cdb
tot = pair + ecm + cd + 21000
p("PF-51", "pairing 45000+34000k", pair, "k=4 (S: EIP-1108)"); p("PF-51", "ecMul+ecAdd 6150*n_pub", ecm, "n_pub=7")
p("PF-51", f"calldata <= 16*{cdb} B", cd); p("PF-51", "model total incl. 21000", tot)
p("PF-51", "measured verifyProof view 256,038 (#58) - model", 256038 - tot, f"({100*(256038-tot)/256038:.1f} %)")
p("PF-51", "admit 301,163 - view 256,038 (gate storage+event)", 301163 - 256038)
p("PF-51", "admit / ERC-1056 C1", f"{301163/76830:.2f}x")
p("PF-52", "SSTORE zero->nonzero cold 20000+2100", 22100)
for kb in (1, 2, 5):
    B = 1024 * kb; st = math.ceil(B / 32) * 22100; lg = 375 + 3 * 375 + 8 * B; cdg = 16 * B
    p("PF-52", f"{kb} kB storage ceil(B/32)*22100", f"{st:,}")
    p("PF-52", f"{kb} kB LOG3 375+3*375+8B (PN-13 corrected)", f"{lg:,}")
    p("PF-52", f"{kb} kB ratio execution-only storage/log", f"{st/lg:.1f}x")
    p("PF-52", f"{kb} kB ratio with calldata 16/B both sides (EIP-2028 basis)", f"{(st+cdg)/(lg+cdg):.1f}x")
    floor = 40 * B   # EIP-7623 floor (Prague+): 10 gas/token, 4 tokens per non-zero byte
    log_tx = max(cdg + lg, floor); st_tx = max(cdg + st, floor)
    p("PF-52", f"{kb} kB ratio under EIP-7623 floor (hardfork {HARDFORK}), excl. 21000", f"{st_tx/log_tx:.1f}x", f"log tx pays floor {floor:,} > {cdg+lg:,}")
p("PF-52", "U3 log 288 B data, 2 topics 375+2*375+8*288", 375 + 750 + 8 * 288)
# PN-37: EIP-7623 gas = 21000 + max(4*tokens + g_exec, 10*tokens), tokens = z + 4n  =>  floor binds iff g_exec < 6*tokens = 6z + 24n
p("PF-52", "EIP-7623 floor binds iff g_exec < 6*tokens = 6z+24n; bare LOG3 1500+8B < 24B iff B >", f"{1500/16:.2f} B")
for wname, sw in (("first write (0->nonzero, cold) 20000+2100", 22100), ("later write (nonzero->nonzero, cold) 2900+2100", 5000)):
    lo = (sw + 1125 + 8 * 160 - 6 * 656) / 16; hi = (sw + 1125 + 8 * 160 - 6 * 164) / 16
    p("PF-52", f"setAttribute {wname}: floor binds for value V > (S_w+1125+1280-6*T_h)/16, T_h in [164,656]", f"{lo:.0f}..{hi:.0f} B", "lower bound (dispatch/access overhead raises it)")
p("PF-52", "U3 35,024 - 21,000 < 22,100 => later write; V=128 B below later-write threshold", "floor does not bind for U3", "#29")

# ---------------------------------------------------------------- N
print("\n== N. Freshness (PF-54..56) ==")
for kk in (1, 5, 25, 90, 146):
    te = tl + tc / kk
    p("PF-54", f"t_eff(k_f={kk})=t_local+t_chain/k", f"{te:.3f} ms", f"P*(0.5)={int(50/te)} staleness<= {kk-1} msgs = {(kk-1)/10} s @10 Hz")
p("PF-54", "knee ceil(t_chain/(0.5-t_local))", math.ceil(tc / (0.5 - tl)), "(register #32: k ~ 90)")
for rs in (10, 1, 0.1): p("PF-54", "sigma_k=(k_f-1)/r_s at k_f=25", f"{24/rs:g} s", f"r_s={rs} Hz")
for sig in (1, 2.5, 10):
    kk = math.floor(10 * sig) + 1
    p("PF-55", f"k_f*=floor(r_s*sigma_max)+1, sigma_max={sig}", kk, f"t_eff={tl+tc/kk:.3f} ms P*(0.5)={int(50/(tl+tc/kk))}")
p("PF-55", "knee k_f=90 at 10 Hz -> revoked-key acceptance (k_f-1)/r_s", "8.9 s")
p("PF-56", "W = ledger terms + t_propagate + sigma + backhaul term", "table (DERIVED)", "no number")

# ---------------------------------------------------------------- O
print("\n== O. Measurement-dimension metrics (PF-57a, PF-58..62) ==")
for Nv in (4, 7):
    fB = (Nv - 1) // 3; q = math.ceil(2 * Nv / 3)
    p("PF-57a", f"write availability P(>= {q} of {Nv} up), unavail 0.01", f"{1-binom_tail(Nv, Nv-q+1, 0.01):.6f}")
p("PF-58", "T coordinate -log10 PF-16(Nv=4, pc=.05)", f"{-math.log10(eL4):.2f}")
p("PF-60", "HHI all-Hardhat / two equal clients", "1.0 / 0.5"); p("PF-60", "Shannon 3 equal clients ln 3", f"{math.log(3):.3f}")
p("PF-60", "Nakamoto coefficient executed system", 1, "N_v=1")
p("PF-61", "(c) kill rate IDTX gate mutants / (d) attack matrix", "5/5 / 43/43 defended (11 N/A)", "(EXECUTION.md; #28)")
p("PF-62", "anonymity bits log2(131072) / log2(124518)", f"17 / {math.log2(124518):.2f}")
p("PF-62", "on-chain pseudonym pool k_A", 1, "(#38: 60/60 linked by one eth_getLogs)")

# ---------------------------------------------------------------- P
print("\n== P. Bounds supplied on R8/R9 request (PF-63..66) ==")
p("PF-63", "kappa = H(vehicle_id | adversary); key = SHA-256(vehicle_id)", "kappa = H(id), not 256", "erc1056_provider.py vehicle_account (TEST-ONLY)")
for name, space in (("id known to adversary (broadcast in DID/BSM)", 1), ("sequential ids BENCH_<type>_<i>, 3 types x 1000", 3000),
                    ("VIN, serial-only unknown (#60)", 1e6), ("VIN, plant+serial unknown (E)", 3e7), ("uniform 128-bit id", 2**128)):
    k_ = math.log2(space) if space > 1 else 0.0
    t_ = space / 279587
    p("PF-63", f"kappa for {name}", f"{k_:.2f} bits; enumeration at 279,587 SHA-256/s = {t_:.3g} s", "contrast R4 PF-06 min(2^128,2^kappa)")
p_lie = 1e-3
p("PF-64", "k=1 endpoint, no proof: P(accept false state)", f"{p_lie:.1e}", "p_lie per endpoint (E); repo today")
for (kq, nq) in ((2, 3), (3, 5)):
    v = binom_tail(nq, kq, p_lie)
    p("PF-64", f"{kq}-of-{nq} agreement, independent endpoints", f"{v:.2e}", f"p_lie={p_lie}")
    for rho in (0.1,):
        p("PF-64", f"{kq}-of-{nq} with common provider share rho={rho}", f"{rho*p_lie + (1-rho)*v:.2e}", "correlation collapses toward p_lie")
p("PF-64", "eth_getProof against trusted header: P(accept false)", "<= Adv^CR_keccak + P(header untrusted) ~ 2^-128 + p_hdr", "(DESIGN; not used in repo)")
for Nv in (4, 7, 10):
    fB = (Nv - 1) // 3; base = binom_tail(Nv, fB + 1, 0.05)
    for pcm in (0.0, 0.01, 0.05):
        p("PF-65", f"P(safety loss) = p_cm + (1-p_cm)*Binom tail, Nv={Nv}, pc=.05, p_cm={pcm}", f"{pcm + (1-pcm)*base:.3e}", "HHI=1 -> p_cm = p_bug(single client)")
for rho in (0.1, 0.3):
    a = 0.05 * (1 - rho) / rho; b = 0.95 * (1 - rho) / rho
    p("PF-65", f"beta-binomial variant Nv=4 pc=.05 rho_c={rho}", f"{stats.betabinom.sf(1, 4, a, b):.3e}")
pk = 0.01
for (m_, n_) in ((1, 1), (2, 3), (3, 5)):
    p("PF-66", f"{m_}-of-{n_} single-period compromise, p_key={pk}", f"{binom_tail(n_, m_, pk):.2e}")
for (m_, n_) in ((1, 1), (2, 3)):
    pc_ = binom_tail(n_, m_, pk); pd = 0.9
    p("PF-66", f"{m_}-of-{n_} with time-lock, P(detect+veto in window)={pd}", f"{pc_*(1-pd):.2e}", "time-lock T_lock >= detection time (E)")

# ---------------------------------------------------------------- Q self-check
print("\n== Q. Self-check: document PF tags vs script output ==")
out = _buf.getvalue()
pat = re.compile(r"PF-(\d{2})([a-z]?)(?![\d])")
script_tags = {f"PF-{a}{b}" for a, b in re.findall(r"\[PF-(\d{2})([a-z]?)\]", out)}
ok = True
try:
    doc = open(DOC, encoding="utf-8").read()
except OSError as e:
    print(f"SELF-CHECK FAIL: cannot read document ({e})"); sys.exit(1)
doc_tags = {f"PF-{a}{b}" for a, b in pat.findall(doc)}
missing = sorted(doc_tags - script_tags)
own = lambda t: 32 <= int(t[3:5]) <= 66
extra = sorted(t for t in script_tags - doc_tags if own(t))
print(f"document PF tags: {len(doc_tags)}; script PF labels: {len(script_tags)}")
if missing: ok = False; print("FAIL document tags absent from script output:", ", ".join(missing))
if extra: ok = False; print("FAIL R7-owned script labels absent from document:", ", ".join(extra))
if ok: print(f"SELF-CHECK PASS: all {len(doc_tags)} document PF tags appear in the output; all R7-owned labels (PF-32..66) appear in the document.")
sys.exit(0 if ok else 1)
