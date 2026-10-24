#!/usr/bin/env python3
"""R7 v0-1 scratch calculator. Every number in R7 is printed here with its equation and inputs.
Run: python3 r7_calc.py   (numpy, scipy).
Print labels are working labels; final R7 tags: A->R4 re-checks, B->PF-38, C/C2->PF-40, D->PF-43,
E/F->PF-44, G->PF-41/42, H->PF-47/53, I->PF-48, J->PF-49..52, K->PF-54/55, L->PF-32/33/36/60. Inputs marked M = register row, S = standard, E = estimated, P = parameter."""
import math, numpy as np
from scipy import stats
rng = np.random.default_rng(42)
def p(tag, eq, val, inputs=""): print(f"[{tag}] {eq} = {val}   {inputs}")
def binom_tail(N, j, pc): return sum(math.comb(N,i)*pc**i*(1-pc)**(N-i) for i in range(j,N+1))

print("== A. Phase-1 R4 re-checks ==")
p("R4 PF-02","sqrt(2*2^160*1e-12)",f"{math.sqrt(2*2**160*1e-12):.3e}")
n=1.5e9*1040*20; p("R4 PF-04","n=V*K*Y",f"{n:.3e}"); p("R4 PF-04","n^2/2^161",f"{n**2/2**161:.2e}")
p("R4 PF-24 fleet","n/(20 y)",f"{n/(20*365.25*86400):.3e} /s")
for Nv in (4,7,10,13,16,22):
    fB=(Nv-1)//3; print(f"  PF-16 Nv={Nv} fB={fB}: "+"  ".join(f"{pc}:{binom_tail(Nv,fB+1,pc):.2e}" for pc in (0.01,0.05,0.10,0.20)))
def nak(q,z):
    pp=1-q; lam=z*q/pp; s=1.0
    for k in range(z+1): s-=math.exp(-lam)*lam**k/math.factorial(k)*(1-(q/pp)**(z-k))
    return s
for q in (0.1,0.3,0.4): print(f"  PF-19 q={q}: "+" ".join(f"z{z}:{nak(q,z):.2e}" for z in (1,3,6,12,24,48)))
for q in (0.1,0.3): print(f"  PF-19 min z for <1e-6 at q={q}:", next(z for z in range(1,200) if nak(q,z)<1e-6))

print("\n== B. QBFT message complexity (PF-37) ==")
for Nv in (4,7,10,13,16,22):
    fB=(Nv-1)//3; Q=math.ceil(2*Nv/3)  # QBFT quorum ceil(2N/3)
    pre=Nv-1; prep=Nv*(Nv-1); com=Nv*(Nv-1); rc=Nv*(Nv-1)
    tot=pre+prep+com
    print(f"  Nv={Nv:2d} fB={fB} quorum={Q} nakamoto(safety)={fB+1}  pre-prepare={pre} prepare={prep} commit={com} total/round={tot}  round-change={rc}  +RC={tot+rc}")
    # bytes per round at 200 B/message (E)
    print(f"        bytes/round @200B = {tot*200/1e3:.1f} kB; per s at Δ=2s = {tot*200/2/1e3:.1f} kB/s")

print("\n== C. Time-to-confirm (PF-38) ==")
# QBFT: include U(0,Δ) + commit Δc; round change: proposer faulty w.p. phi per round, timeout t_rc*2^r
def qbft_sample(Delta, Dc, phi, trc, M=400000):
    inc=rng.uniform(0,Delta,M); extra=np.zeros(M); r=np.zeros(M,int); alive=np.ones(M,bool)
    for k in range(20):
        fail=alive & (rng.random(M)<phi)
        extra[fail]+=trc*2**k; alive=fail
        if not alive.any(): break
    return inc+Dc+extra
for (Delta,phi,trc) in ((2,0.0,10),(2,0.25,10),(2,1/7,10),(5,0.25,10)):
    s=qbft_sample(Delta,Delta,phi,trc)
    print(f"  QBFT Δ={Delta} phi={phi:.3f} t_rc={trc}: E={s.mean():.2f}s p99={np.percentile(s,99):.2f}s p999={np.percentile(s,99.9):.2f}s")
# analytic expected extra: sum_k phi^(k+1) trc 2^k = trc*phi/(1-2phi) for phi<1/2
for phi in (0.25,1/7): p("PF-38","E_extra=t_rc*phi/(1-2phi)",f"{10*phi/(1-2*phi):.3f} s",f"phi={phi:.3f}, t_rc=10")
# PoW: z blocks Erlang(z, 600)
for z in (6,11):
    p("PF-38 PoW",f"Erlang(z={z},600s) mean / p99",f"{z*600/3600:.2f} h / {stats.gamma.ppf(0.99,z,scale=600)/3600:.2f} h")
# Ethereum L1 finality ~ 2 epochs 64 slots*12 s
p("PF-38 L1","2 epochs*32 slots*12 s",f"{2*32*12} s")

print("  -- C2 round-robin exact: c consecutive crashed proposers from height start -> extra t_rc*(2^c-1)")
def rr(Nv, crashed, trc=10, Delta=2):
    ex=[]
    for i in range(Nv):
        c=0
        while ((i+c)%Nv) in crashed and c<Nv: c+=1
        ex.append(trc*(2**c-1))
    return 1.5*Delta+sum(ex)/Nv, 2*Delta+max(ex)
for Nv,cr in ((4,{0}),(7,{0}),(7,{0,1}),(10,{0,1,2}),(22,set(range(7)))):
    E,Wc=rr(Nv,cr); print(f"  Nv={Nv} crashed(adjacent)={len(cr)}: E[t_conf]=1.5Δ+mean extra={E:.2f}s  worst=2Δ+max extra={Wc:.0f}s (Δ=2,t_rc=10)")
print("\n== D. Verification load (PF-34, PF-35) ==")
classes={ # t_ver ms, status
 "Xeon 2.10GHz Python SSI warm (M, #27)":0.14225,
 "Xeon PKI warm (M, #27)":0.0904,
 "V2X security ASIC/HSM (E)":0.25,   # ~4,000 verif/s class
 "Automotive app-processor sw, Cortex-A53 class (E)":1.0,
 "Automotive MCU HSM (Cortex-M/EVITA-full class) (E)":5.0,
}
neigh=(50,100,200,300)
for name,t in classes.items():
    vmax=1000/t
    row=f"  {name}: t_ver={t} ms, v_max=1/t={vmax:,.0f}/s, P_max(f=1)=1/(10Hz*t)={int(100/t)}, P*(0.5)={int(50/t)} | rho at "
    row+=", ".join(f"{P}:{P*10*t/1000:.2f}" for P in neigh)
    print(row)
for P in neigh: print(f"  load lambda=10Hz*{P} = {10*P}/s")
# M/D/1 waiting at rho
for t in (0.25,1.0):
    for P in (100,200,300):
        rho=P*10*t/1000
        if rho<1: print(f"  M/D/1 t={t}ms P={P}: rho={rho:.2f} Wq=rho*t/(2(1-rho))={rho*t/(2*(1-rho)):.3f} ms, sojourn={t+rho*t/(2*(1-rho)):.3f} ms")
        else: print(f"  M/D/1 t={t}ms P={P}: rho={rho:.2f} >= 1 unstable")
# verify-on-demand fraction phi_v needed
for t in (1.0,5.0):
    for P in (200,300):
        print(f"  verify-on-demand: t={t} P={P}: fraction verifiable at f=0.5 = min(1, 0.5/(P*10*t/1000)) = {min(1,0.5/(P*10*t/1000)):.3f}")
# measured slope #26
p("#26 check","P*(0.5)=50/0.164",f"{50/0.164:.1f}"); p("#26","P*(1)=100/0.164",f"{100/0.164:.1f}")
# ledger side per vehicle: refresh every k messages
for k in (1,25,90):
    for P in (100,300): print(f"  ledger reads/s per vehicle = 10*P/k: k={k} P={P}: {10*P/k:.1f}")
# signing
for name,ts in (("ASIC/HSM (E)",0.5),("MCU HSM (E)",10.0)):
    p("PF-34 sign",f"duty = 10Hz*t_sig ({name})",f"{10*ts/1000:.3f}",f"t_sig={ts} ms")

print("\n== E. Airtime 802.11p (PF-36) ==")
# 10 MHz, 6 Mb/s QPSK 1/2: preamble+SIGNAL 40us, symbol 8us, 48 data bits/symbol; PSDU bits = 16+8L+6
def t11p(L,rate=6):
    bits_per_sym={3:24,6:48,12:96}[rate]
    return 40+8*math.ceil((16+8*L+6)/bits_per_sym)
MAC=36  # MAC hdr 24(+QoS 2)+LLC 8 +FCS 4 approx (E) -> 38? use 36
WSMP=6
core=40   # J2735 BSM part I ~ 39-40 B UPER (E)
sec={"no security":0,"1609.2 digest signer (E 86 B)":86,"1609.2 implicit cert (E 86+76=162 B)":162,"1609.2 explicit cert (E 86+124=210 B)":210,
     "repo JSON ERC-1056 msg (M #23, 596 B total)":None,"repo JSON PKI msg (M #23, 1,110 B total)":None}
AIFS=58  # AC_VO 802.11p 10MHz: SIFS 32 + 2*13 (E/S)
for name,s in sec.items():
    if s is None:
        L= 596 if "ERC" in name else 1110
        L+=MAC
    else: L=core+s+WSMP+MAC
    T=t11p(L)+AIFS
    Nfit=0.6/(10*T*1e-6)
    print(f"  {name}: MPDU={L} B, T_air={t11p(L)} us (+AIFS {AIFS}) = {T} us; CBR per vehicle@10Hz={10*T*1e-6:.4f}; vehicles at CBR 0.6 = {Nfit:.0f}")
print("  share of identity bytes digest vs explicit cert: ", end="")
Td=t11p(core+86+WSMP+MAC)+AIFS; Te=t11p(core+210+WSMP+MAC)+AIFS; T0=t11p(core+WSMP+MAC)+AIFS
print(f"T0={T0} Td={Td} Te={Te}; security share digest={(Td-T0)/Td:.2f}, explicit={(Te-T0)/Te:.2f}")
# 1-in-5 certificate inclusion (common practice: cert once per second or on new neighbour)
Tmix=0.2*Te+0.8*Td; p("PF-36","T_mix=0.2*T_cert+0.8*T_digest",f"{Tmix:.0f} us; vehicles at CBR .6 = {0.6/(10*Tmix*1e-6):.0f}")

print("\n== F. PC5 mode 4 (PF-36b) ==")
# 10 MHz = 50 PRB, subchannel 10 PRB -> 5 subchannels/subframe, 1000 subframes/s
# bytes per subchannel ~ 190 B at MCS ~ 7-9 incl. 2 PRB SCI (E, literature 3GPP R1 eval)
B_SC=190
for name,L in (("no security",core+WSMP+20),("digest",core+86+WSMP+20),("implicit cert",core+162+WSMP+20),("explicit cert",core+210+WSMP+20),("repo JSON ERC-1056",596),("repo JSON PKI",1110)):
    nsc=math.ceil(L/B_SC); cap=5//nsc*1000 if nsc<=5 else 0
    print(f"  {name}: L={L} B, subchannels={nsc}, packets/s per 10MHz={cap}, vehicles@10Hz CBR1={cap/10:.0f}, @CBR0.6={0.6*cap/10:.0f}")
# reselection
for Pk in (0.0,0.4,0.8):
    life=10*0.1/(1-Pk); p("PF-36c","E[resource lifetime]=E[C]*RRI/(1-P_keep)",f"{life:.2f} s",f"E[C]=10 (U[5,15]), RRI=0.1s, P_keep={Pk}")
    # prob a resource survives a pseudonym change at a random instant within a window of x=0 i.e. same resource before/after
    # P(no reselection in next T seconds) ~ exp(-T/life)
    print(f"      P(same resource persists 1 s after pseudonym change) ~ exp(-1/life) = {math.exp(-1/life):.3f}")

print("\n== G. RNG (PF-32, PF-33) ==")
nkeys=n
for kap in (32,48,64,80,128,256):
    c=-math.expm1(-nkeys*(nkeys-1)/2/2**kap) if kap>=48 else 1.0
    print(f"  kappa={kap}: P(any shared key among n={nkeys:.2e}) = 1-exp(-n^2/2^(k+1)) = {c:.3e}")
for nv in (1e6,1.5e9):
    for kap in (32,40,48):
        print(f"  n={nv:.1e} devices kappa={kap}: expected colliding pairs n^2/2^(k+1) = {nv**2/2**(kap+1):.3e}")
# SP 800-90B RCT cutoff C = 1+ceil(20/H) for alpha=2^-20
for H in (1.0,0.5,0.1): p("PF-33 RCT","C=1+ceil(-log2(alpha)/H)",1+math.ceil(20/H),f"alpha=2^-20,H={H}")
for rate,H in ((1e6,0.5),(1e4,0.5),(100,0.8)):
    t=(256+64)/(rate*H); p("PF-33 seed time","(256+64)/(r*H)",f"{t:.4g} s",f"r={rate} samples/s, H={H}")
# nonce bias lattice: bits of bias b -> signatures needed ~ (256/b) * small constant (E)
for b in (1,2,4,8): print(f"  nonce bias b={b} bits: lattice dimension ~256/b = {256//b} signatures (order of magnitude, E)")

print("\n== H. GNSS time and freshness (PF-39..41) ==")
max_age=1.0; max_fut=0.1
for d_ppm in (0.5,2,20,50):
    T=max_fut/(2*d_ppm*1e-6); p("PF-40","T_holdover=max_future/(2d)",f"{T:.0f} s = {T/3600:.2f} h",f"d={d_ppm} ppm")
p("PF-39","replay window w=max_age+max_future",f"{max_age+max_fut} s")
for P in (50,100,300,600):
    p("PF-39 cache","entries=10*P*w",f"{10*P*1.1:.0f}",f"P={P}")
p("freshness.py docstring check","senders = 65536/(10Hz*1.1s*margin10)",f"{65536/(10*1.1*10):.0f}  (docstring says ~650)")
p("PF-39","max senders no eviction = 65536/(10*1.1)",f"{65536/11:.0f}")
for v in (14,30,40): p("PF-41","position staleness = v*max_age",f"{v*max_age:.0f} m",f"v={v} m/s")
p("PF-41","GNSS-locked eps_t ~ 1e-7 s vs 0.1 s window: margin",f"{0.1/1e-7:.0e}x")

print("\n== I. RSU backhaul renewal model (PF-42) ==")
def W_rsu(mu_on,mu_off,W0, M=400000):
    # alternating renewal, exponential; revocation arrives at stationary random time
    A=mu_on/(mu_on+mu_off)
    down=rng.random(M)>A
    resid=rng.exponential(mu_off,M)
    W=W0+np.where(down,resid,0.0)
    return A,W
W0=8.5
for mu_off in (10,60,600):
    for A in (0.99,0.95,0.90):
        mu_on=A*mu_off/(1-A)
        _,W=W_rsu(mu_on,mu_off,W0)
        EW=W0+(1-A)*mu_off
        # analytic tail: P(W>W0+x)=(1-A)exp(-x/mu_off); p99: if 1-A<=0.01 -> W0 else W0+mu_off*ln((1-A)/0.01)
        p99=W0 if (1-A)<=0.01 else W0+mu_off*math.log((1-A)/0.01)
        p999=W0+mu_off*math.log((1-A)/0.001) if (1-A)>0.001 else W0
        print(f"  mu_off={mu_off}s A={A}: E[W]=W0+(1-A)mu_off={EW:.2f}s (MC {W.mean():.2f}); p99={p99:.1f}s (MC {np.percentile(W,99):.1f}); p99.9={p999:.1f}s (MC {np.percentile(W,99.9):.1f})")
# general OFF distribution: residual mean = E[X^2]/(2E[X]); deterministic OFF D: D/2; lognormal cv=2: (1+cv^2)/2*mu
for cv in (0,1,2): p("PF-42 general","E[resid]=mu_off*(1+cv^2)/2",f"{(1+cv**2)/2:.1f}*mu_off",f"cv={cv}")
# poll-based RSU: poll every T_p adds U(0,T_p)
for Tp in (1,10,60): p("PF-42 poll","E add T_p/2, max T_p",f"{Tp/2} / {Tp} s")

print("\n== J. Gas and capacity (PF-43..46) ==")
G=60_000_000  # M: results/metrics/latest/meta.json network.blockGasLimit
g={ "C1 create (ERC-1056)":76830,"U1 rotate/changeOwner":51754,"U2 addDelegate":55143,"U3 setAttribute":35024,
    "U5 meta-tx setAttributeSigned":62646,"D1 revokeDelegate":32868,"D2 revokeAttribute":34576,"V3 anchor status":33918,
    "V5 revoke credential":33470,"P1 presentation":34206,"CVIN C1":271402,"ERC-735 C1":1757881,"ERC-4337 U5":141767,
    "ZkVinGate.admit":301163,"MOBI attestEvent exec (#28)":198694,"RSU anchor key (#47)":52606,"pseudonym addDelegate steady (#38)":54807}
for name,go in g.items():
    opb=G//go; print(f"  {name}: g={go:,}  ops/block={opb:,}  ops/s Δ=1:{G/go/1:,.0f} Δ=2:{G/go/2:,.0f} Δ=5:{G/go/5:,.0f} Δ=12:{G/go/12:,.0f}")
for GG in (30e6,100e6):
    print(f"  G={GG/1e6:.0f}M: ERC-1056 C1 ops/s Δ=2 = {GG/76830/2:,.0f}; V5 = {GG/33470/2:,.0f}")
rate=n/(20*365.25*86400)
for name,go in (("addDelegate pseudonym",54807),("C1 76,830",76830),("did:ethr implicit (0 gas, #47)",0)):
    need=rate*go; print(f"  fleet {rate:.3e}/s x {go} = {need:.3e} gas/s vs G/Δ(2s)={G/2:.3e}: ratio={need/(G/2) if go else 0:.1f}x")
p("fleet","blocks/day needed at 60M for addDelegate",f"{rate*54807*86400/G:,.0f} vs {86400/2:,.0f} available (Δ=2)")
# 20 pseudonyms per epoch row #38 : 1,096,368 gas/epoch/vehicle
p("#38","per vehicle per week (20 pseudo) gas",f"{1096368:,}"); p("#38 fleet","1.5e9 vehicles * 1,096,368 gas / week / (G per 2s)",f"{1.5e9*1096368/(G*7*86400/2):.1f}x capacity")
# EIP-1108
k=4; pair=45000+34000*k; npub=7; ecmul=6000*npub; ecadd=150*npub
cd_bytes=4+256+32*npub; cd=16*cd_bytes
tot=pair+ecmul+ecadd+cd+21000
p("PF-45","pairing 45000+34000k",pair,"k=4"); p("PF-45","ecMul 6000*n_pub + ecAdd 150*n_pub",ecmul+ecadd,"n_pub=7")
p("PF-45","calldata<=16*(4+256+32*7)",cd,f"{cd_bytes} B"); p("PF-45","precompile+calldata+21000",tot)
p("PF-45","measured view estimate 256,038 (#58) - model",256038-tot)
p("PF-45","admit 301,163 - verify view 256,038",301163-256038)
p("PF-45 pre-1108","100000+80000k + 40000 n_pub + 500 n_pub (Byzantium)",100000+80000*k+40000*npub+500*npub)
p("PF-45","Groth16 vs ERC-1056 C1",f"{301163/76830:.2f}x")
# storage
p("PF-46","SSTORE zero->nonzero cold = 20000+2100",22100)
p("PF-46","log cost U3 288 B data, 2 topics est: 375+375*2+8*288",375+750+8*288)
for kb in (1,2,5):
    p("PF-46",f"{kb} kB DID doc in storage = ceil(1024*kb/32)*22100",f"{math.ceil(1024*kb/32)*22100:,}")
    p("PF-46",f"{kb} kB as event data = 8*1024*kb + 375*3",f"{8*1024*kb+1125:,}")
# QBFT bytes vs gas irrelevant

print("\n== K. Freshness (PF-47..49) ==")
tl,tc=0.346,13.94   # #32 A3b
for kk in (1,5,25,90,146):
    te=tl+tc/kk; print(f"  t_eff(k={kk})={te:.3f} ms  P*(0.5)={int(50/te)}  staleness msgs<=k-1={kk-1}  time @10Hz=(k-1)/10={(kk-1)/10} s")
p("#32 knee","ceil(tc/(0.5-tl))",math.ceil(tc/(0.5-tl)))
# time-based TTL vs message-based: staleness time bound sigma_k=(k-1)/r_s; at sender rate r_s
for rs in (10,1,0.1): p("PF-47","sigma_msg=(k-1)/r_s at k=25",f"{24/rs} s",f"r_s={rs} Hz")
# optimal k: minimise cost c(k)=t_l+t_c/k s.t. (k-1)/r <= sigma_max -> k*=floor(r*sigma)+1
for sig in (1,2.5,10):
    kk=math.floor(10*sig)+1; p("PF-48","k*=floor(r_s*sigma_max)+1",kk,f"sigma_max={sig}s r_s=10Hz; t_eff={tl+tc/kk:.3f} ms")
# W composition with sigma
p("PF-49","W = ledger(Δ/2+Δ) + t_prop + sigma; Hardhat automine ledger term ~ tx latency 7.8 ms (M1-H U3 median)","DESIGN/M1")

print("\n== L. Privacy / misc ==")
p("PF-52","VIN serial entropy log2(1e6)",f"{math.log2(1e6):.2f} bits"); p("#60","1e6/279587",f"{1e6/279587:.2f} s")
p("PF-52","log2(131072)",17); p("PF-52","log2(124518)",f"{math.log2(124518):.2f}")
# ECDSA GGM bound q^2/n
for lq in (64,80,100): p("PF-32 GGM","Adv<=q^2/n",f"2^{2*lq-256}",f"q=2^{lq}")
# composition example
eps=[2**-128,2**-128,binom_tail(4,2,0.05),1e-6]
p("PF-35 comp","sum eps (sig, CR, equiv(Nv=4,pc=.05), resolver 1e-6)",f"{sum(eps):.3e}")
# gossip propagation
for Nn,F in ((100,3),(1000,4),(10000,6)):
    r=math.log(Nn)/math.log(F+1)+math.log(math.log(Nn)); p("PF-50 gossip","rounds ~ log_{F+1}N + ln ln N",f"{r:.1f}",f"N={Nn},F={F}; t_prop @50ms/hop={r*50:.0f} ms")
# Nakamoto coeff/HHI
p("PF-51","HHI client diversity all-Hardhat",1.0); p("PF-51","HHI two clients 50/50",0.5)
p("PF-51","Shannon diversity 3 equal clients ln3",f"{math.log(3):.3f}")
