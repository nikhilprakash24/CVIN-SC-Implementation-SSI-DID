# CVIN-SC · R4 — Proofs, Bounds and Numbers for the Identity Stack

**The quantitative spine of the Roots suite: our own symbols defined once, the standard results we lean on cited once, and every `PF-⟦n⟧` placeholder from R3 filled with a derivation that prints its arithmetic — so that a later document can change one variable (the chain, the curve, the validator count) and cite one tag rather than re-derive.**

Document 4 of the Roots suite (thread G-R1, provisional) · v0.1 · 2026-09-15 · CVIN-SC Research Programme · UBC ECE MASc
Consumes: R1 v1.1, R2 v0.1 (symbol-collision list §4.3), R3 v0.1 (BP- tags; the 31 PF placeholders and their variables; Part IV flows), G-B (measurands, arms, clock boundaries), G-C1 §2.7 (the W decomposition), Pass 3 CEV format, the formal specification.
Assigns: `SYM-01`–`SYM-24`, `PF-01`–`PF-31`. Status vocabulary: **DERIVED** (from stated equations and inputs) · **MEASURED** (from a programme trace, cited) · **ESTIMATED** (inputs assumed; marked) · **STANDARD-RESULT** (cited theorem, not re-proved).
Discipline: definitions first, derivations second, numbers last; no bare value without its equation and inputs; every number reproducible from §0 with a calculator. Arithmetic was recomputed in a scratch script before canonisation (MC-P-1 lesson).
Open inputs: Q-R5 (which manoeuvre-class W budgets to target) — PF-28 is therefore expressed as a function, with an illustrative budget marked.

---

## 0. Notation

### 0.1 Our symbols (SYM-)

Thesis notation reused, not redefined: **W** (revocation-latency window, G-C1 §2.7) and **σ** (cache-staleness bound, HAA-1). Per R2 §4.3, bare `A`, `f`, `N` are avoided.

| SYM | Symbol | Name | Units | Maps to standard | Default / where set |
|---|---|---|---|---|---|
| SYM-01 | *k* | nominal key length | bits | key size | 256 (secp256k1, Ed25519) |
| SYM-02 | *κ* | effective key-generation entropy | bits | min-entropy of the RNG output | ≤ *k*; = *k* for a sound RNG |
| SYM-03 | *h* | hash output length | bits | — | 256 (SHA-256, keccak-256) |
| SYM-04 | *a* | identifier (address) length | bits | — | 160 (EVM address; Bitcoin P2PKH); **128 (did:indy / did:sov NYM = first 16 bytes of the verkey ⟦verify at source, EA-⟧)** |
| SYM-05 | *n* | number of distinct keys or identifiers ever generated in a namespace | count | — | fleet model, PF-04 |
| SYM-06 | *S* | size of the identifier space | count | 2^*a* or group order | — |
| SYM-07 | *N_v* | validator count (permissioned) | count | *n* in BFT literature | Option A deployment |
| SYM-08 | *f_B* | tolerated Byzantine validators | count | *f* in BFT literature | ⌊(*N_v*−1)/3⌋ |
| SYM-09 | *p_c* | probability that one validator is compromised or colludes, independently | — | — | ESTIMATED 0.01–0.20 |
| SYM-10 | *α* | honest fraction of hashpower (PoW) | — | *p* in Nakamoto §11 | 0.6, 0.7, 0.9 |
| SYM-11 | *q* | adversary fraction of hashpower | — | *q* in Nakamoto §11 | 1 − *α* |
| SYM-12 | *z* | confirmation depth | blocks | *z* in Nakamoto §11 | — |
| SYM-13 | *Δ* | block interval of Plane A | s | block period | 2 s (Besu QBFT sandbox default ⟦confirm from genesis manifest⟧) |
| SYM-14 | *τ_a* | checkpoint (anchoring) interval to the public chain | s | — | deployment parameter; illustrative 3600 s |
| SYM-15 | *t_pub* | public-chain finality time for the checkpoint tx | s | — | Option C Bitcoin: 6·600 s; Ethereum L1: ≈ 768 s (2 epochs) |
| SYM-16 | *r* | replication factor of an off-chain artefact | count | — | Plane D policy |
| SYM-17 | *p_ℓ* | per-replica annual loss probability | yr⁻¹ | — | ESTIMATED 0.01 |
| SYM-18 | *γ* | selfish miner's share of honest nodes that adopt its block in a tie | — | *γ* in Eyal–Sirer | 0–1 |
| SYM-19 | *m* | status-list size (entries) | count | — | 131,072 (P3 §2.2) |
| SYM-20 | *ρ* | revoked fraction of a status list | — | — | scenario |
| SYM-21 | (*t*, *m_r*) | recovery threshold: *t* of *m_r* guardians | count | threshold scheme | option-specific |
| SYM-22 | *G* | block gas budget of Plane A | gas | block gas limit | 30 M / 100 M ⟦genesis manifest⟧ |
| SYM-23 | *g_op* | gas of one identity operation in a declared arm | gas | G-B exact integer | MEASURED per option/arm |
| SYM-24 | *B_tier* | latency budget of a tier | ms | X4 | Tier 1 < 100; Tier 2 100–500; Tier 3 unbounded |

The five W terms (`t_include`, `t_finalise`, `t_propagate`, `t_cache`, `t_poll`) are thesis notation from G-C1 §2.7 and are used unchanged.

### 0.2 Standard results relied on (cited, not re-proved)

| ID | Result | Statement | Source |
|---|---|---|---|
| SR-A | Birthday bound | For *n* uniform draws from a space of size *S*, P(any collision) = 1 − exp(−*n*(*n*−1)/(2*S*)) ≈ *n*²/(2*S*) when *n*² ≪ *S*; hence *n* for a target *p* is *n* ≈ √(2*S p*) | standard |
| SR-B | Targeted preimage | Expected trials to hit any one of *n* existing *a*-bit identifiers = 2^*a*/*n* | standard |
| SR-C | Generic DLP | Pollard-rho solves a DLP in a group of prime order ≈ 2^*k* in ≈ √(π·2^*k*/2) ≈ 2^(*k*/2) operations; secp256k1 → ≈ 2^128 | Pollard 1978; van Oorschot–Wiener 1999 |
| SR-D | Nakamoto catch-up | With honest fraction *α* = *p*, adversary *q* < *p*, depth *z*, λ = *z q*/*p*: P(reversal) = 1 − Σ_{k=0}^{z} (λ^k e^{−λ}/k!)·(1 − (*q*/*p*)^(*z*−*k*)) | Nakamoto 2008 §11 |
| SR-E | BFT bound | Safety and liveness of PBFT/QBFT require *N_v* ≥ 3*f_B* + 1 under partial synchrony; safety fails if > *f_B* validators are Byzantine | Lamport–Shostak–Pease 1982; Castro–Liskov 1999; Moniz 2020 (IBFT) |
| SR-F | FLP | No deterministic consensus in a fully asynchronous system with one crash fault | Fischer–Lynch–Paterson 1985 |
| SR-G | Selfish mining | Profitable for attacker share > (1−*γ*)/(3−2*γ*): 1/3 at *γ*=0, 1/4 at *γ*=½, 0 at *γ*=1 | Eyal–Sirer 2014 |
| SR-H | Grover / BHT | Quantum preimage on an *h*-bit hash costs ≈ 2^(*h*/2); quantum collision ≈ 2^(*h*/3) (BHT) | Grover 1996; Brassard–Høyer–Tapp 1998 |
| SR-I | Shor | ECDLP and factoring solvable in polynomial time on a cryptographically relevant quantum computer; any *exposed* public key is then forgeable | Shor 1994 |
| SR-J | Pairing-curve security | BN-254 ≈ 100 bits after TNFS (down from 128); BLS12-381 ≈ 117–120 bits | Barbulescu–Duquesne 2019; Guillevic 2020 |
| SR-K | Binomial tail | P(at least *j* of *N* independent events each of probability *p*) = Σ_{i=j}^{N} C(*N*,*i*) *p*^i (1−*p*)^(N−i) | standard |

---

## 1. Identity-creation collision bounds (PF-01 … PF-04)

**PF-01 · Key-pair collision.** Keys are scalars in [1, *n_G*) with *n_G* ≈ 2^256 for secp256k1 (exactly 2^256 − 432420386565659656852420866394968145599; the deficit is negligible). With κ = 256, SR-A gives P(collision among *n* keys) ≈ *n*²/2^257.
- *n* = 10^18 keys: (10^18)² / 2^257 = 10^36 / 2.32×10^77 = **4.3 × 10⁻⁴²**. Status: DERIVED.
- If κ < *k* (BP-L1-01), replace 2^256 by 2^κ. At κ = 64 (a broken RNG), *n* = 10^9 already gives 10^18/2^65 ≈ 2.7×10⁻² — a 3 % collision chance across a billion keys. **The bound is entirely a statement about κ, not about the curve.**

**PF-02 · Address collision (EVM 160-bit, Bitcoin 160-bit).** *S* = 2^160 = 1.46×10^48. P ≈ *n*²/2^161.
- *n* = 10^9: 10^18 / 2.92×10^48 = **3.4 × 10⁻³¹**. DERIVED.
- Solve *n* for target *p* (SR-A, *n* = √(2·2^160·*p*)): *p* = 10⁻¹⁸ → **1.71 × 10¹⁵**; 10⁻¹² → **1.71 × 10¹⁸**; 10⁻⁹ → **5.41 × 10¹⁹** addresses. DERIVED.
- Targeted (SR-B): an attacker seeking *any* existing address among *n* = 3.1×10^13 (PF-04's fleet) needs 2^160/3.1×10^13 ≈ **2^115** trials — still far beyond feasibility; the 160-bit address does not weaken the 128-bit ECDLP security by more than the *n* factor.

**PF-03 · DID collision by method.**
- `did:ethr` (O1, O11-EVM-style): identifier = address → PF-02 applies unchanged.
- `did:indy` / `did:sov` (O10): identifier = base58 of the first 16 bytes of the verkey → *a* = 128 ⟦verify at source⟧. *S* = 2^128 = 3.4×10^38. *n* for *p* = 10⁻¹⁸ → **2.61 × 10¹⁰**; 10⁻¹² → 2.61×10^13; 10⁻⁹ → 8.25×10^14. DERIVED on the ⟦⟧ premise.
- **Finding F-R1:** if the 128-bit premise holds, the Indy namespace reaches a 10⁻¹² collision probability at ≈ 2.6×10^13 identifiers — the same order as the 20-year global fleet key count in PF-04 — whereas the EVM namespace does not reach it until 1.7×10^18. A *random* collision is still not an attack (the colliding party cannot sign for the other's verkey), but it is a *namespace-integrity* defect: two subjects claiming one DID string. R3 Part IV flow 1 step 2 should carry this per method. → CEV-R1.

**PF-04 · Scale statement for the CAV fleet.** Model *n* = *V* · *K* · *Y* with *V* vehicles, *K* keys per vehicle per year, *Y* years. Inputs, all ESTIMATED and to be replaced by the Pass 4 fleet sizes ⟦Q-R5 owner⟧: *V* = 1.5×10^9 (global light-vehicle parc, order of magnitude), *K* = 1,040 (SCMS pseudonym-certificate budget of 20 per week, T-I05), *Y* = 20.
- *n* = 1.5×10^9 × 1,040 × 20 = **3.12 × 10¹³** identifiers.
- P(collision) at *a* = 160: (3.12×10^13)² / 2^161 = 9.73×10^26 / 2.92×10^48 = **3.3 × 10⁻²²**. At *a* = 256 (raw keys): **4.2 × 10⁻⁵¹**. At *a* = 128: **1.4 × 10⁻¹²** (F-R1). DERIVED from ESTIMATED inputs.
- Interpretation: at 160 bits the global fleet over two decades sits ~9 orders of magnitude below a 10⁻¹² target and ~13 below 10⁻⁹; the address space is not the scaling constraint. The scaling constraints are capacity (PF-24) and propagation (PF-28).

---

## 2. Per-layer security bounds (PF-05 … PF-27, PF-30)

### L0
**PF-01′ (R3 PF-⟦1⟧) · Eclipse.** With *d* outbound peers chosen independently from a population in which fraction *β* is adversarial, P(all *d* adversarial) = *β*^*d*. *d* = 8, *β* = 0.3 → 6.6×10⁻⁵; *β* = 0.5 → 3.9×10⁻³. Under Option A the peer set is the authenticated consortium and *β* is bounded by *f_B*/*N_v*; for a verifier reading *k_V* independent Plane-V instances the analogous bound is P(all stale/adversarial) = *β_V*^*k_V*. DERIVED; inputs ESTIMATED. — closes the number for BP-L0-01.

**PF-02′ (R3 PF-⟦2⟧) · Partition stall before W is exceeded.** Let *W_B* be the manoeuvre-class budget and *W_0* the sum of the four non-consensus terms. The tolerable stall is *t_stall,max* = *W_B* − *W_0* − *t_include*. Liveness is lost when ≥ *f_B*+1 validators are unreachable (SR-E); the stall then lasts until reachability returns. The design consequence: **no revocation budget can be met during a partition longer than *W_B* − *W_0***; the honest statement is that Option A fails *safe* (no forks) and *late* (revocation late), never *wrong* (no false acceptance beyond the stale-cache bound σ). DERIVED as a function; numeric once Q-R5 supplies *W_B*.

**PF-03′ (R3 PF-⟦3⟧) · Network-Sybil cost.** Under open membership the cost is zero (T-03) — the reason Options B/C push Sybil resistance to L4 (PF-21). Under Option A the cost is admission to the consortium: not a number but a governance event. STANDARD-RESULT (Douceur) + design statement.

**PF-04′ (R3 PF-⟦4⟧) · Anonymity set of an anchor batch.** A checkpoint that commits *b* subject-level updates behind one root gives an observer of the public chain an anonymity set of size *b* for "which subject changed state in this interval". *b* = (writes per second) × *τ_a*; at 10 writes/s and *τ_a* = 3600 s, *b* = 36,000. Relay submission (Option B) adds the mixnet's set. DERIVED; inputs ESTIMATED.

**PF-05 · Off-chain artefact loss.** With *r* independent replicas each lost with annual probability *p_ℓ*, P(all lost in a year) = *p_ℓ*^*r*. *p_ℓ* = 0.01: *r* = 1 → 10⁻²; *r* = 2 → 10⁻⁴; *r* = 3 → **10⁻⁶**; *r* = 5 → 10⁻¹⁰. Independence is the assumption an availability *owner* is there to make true (R3 BP-L0-05). DERIVED.

### L1
**PF-06 · Effective entropy.** Security of a *k*-bit ECDSA key against generic attack is min(2^128, 2^κ) — the ECDLP bound (SR-C) or the RNG bound, whichever is smaller. Any device with κ < 128 has a key weaker than the curve. The 2013 Android SecureRandom failure had κ effectively tens of bits. DERIVED from SR-C.

**PF-07 · Nonce reuse.** Two ECDSA signatures with the same nonce *k_n* on messages *m₁*, *m₂* give the private key algebraically: *k_n* = (*z₁* − *z₂*)/(*s₁* − *s₂*), then *d* = (*s₁ k_n* − *z₁*)/*r*. Cost: one modular inversion. Bias of even a few bits across hundreds of signatures suffices (lattice attacks). Bound: **two signatures**. STANDARD-RESULT. Defence: RFC 6979 or Schnorr.

**PF-08 · Hash collision / second preimage.** Generic collision on SHA-256: 2^128 work (SR-A at *S* = 2^256); second preimage: 2^256. For *N_obj* committed objects, accidental collision ≈ *N_obj*²/2^257; at *N_obj* = 10^15 (every leaf ever anchored): 10^30/2.3×10^77 ≈ 4×10⁻⁴⁸. DERIVED.

**PF-09 · Quantum.** SR-H/SR-I. Grover halves the exponent: SHA-256 preimage → 2^128; collision → 2^85 (BHT); a 160-bit address preimage → **2^80**, which is at the edge of the classical-feasible range and is the weakest post-quantum figure in the stack ⟦flag for EA-05 extension⟧. Shor breaks every secp256k1 / BLS12-381 key whose public key is exposed. **Exposure window:** on an EVM registry the public key is recoverable from the first signature and remains on-chain forever, so the window for a signed DID is unbounded; the mitigation is not shorter exposure but migration to a PQ verification method (T-I17 allows multiple) before a CRQC exists. Hash-based structures (Merkle, commitments with *h* ≥ 256) survive with the Grover-adjusted margin. STANDARD-RESULT + design statement.

**PF-10 · Pairing-curve security.** SR-J: BN-254 ≈ 100 bits; BLS12-381 ≈ 117–120 bits. AnonCreds v1 (CL, RSA-based 2048–3072-bit) ≈ 112–128 bits classical. Therefore the 12/12 Set B ranking of O12 (R2 decision 5) rests on an assumption class whose *concrete* security is ≤ that of the EVM options' ECDLP (128) — by 8–28 bits depending on the curve. STANDARD-RESULT; the sensitivity is stated in §4.

**PF-11 · Trusted setup.** With *t_s* ceremony participants of whom each retains its randomness with probability *p_s* independently, P(all collude/retain) = *p_s*^*t_s*; *p_s* = 0.1, *t_s* = 6 → 10⁻⁶. The Groth16 verifier in O15 inherits this; Bulletproofs/STARKs remove it at higher verification gas (U-17). DERIVED.

**PF-12 · Side-channel window.** Bounded by the rotation period *T_rot*: an extracted key is useful for at most *T_rot* + PF-26. Design, not a probability.

### L2
**PF-13 · Rewrite-detection latency.** A rewrite of Plane-A history after checkpoint *c_i* is detectable once checkpoint *c_{i+1}* is final on the public chain. *t_detect* ≤ *τ_a* + *t_pub*. Illustrative: *τ_a* = 3,600 s; Option C (Bitcoin, 6 blocks) *t_pub* = 3,600 s → ≤ **7,200 s**; Ethereum L1 *t_pub* ≈ 768 s → ≤ **4,368 s**; Option B rollup *t_pub* ≈ seconds soft, minutes to L1-hard. DERIVED. Note this is *detection*, not prevention (R3 decision 1); and it bounds the window in which a colluding validator set could rewrite *undetected* — which is exactly why *τ_a* is a security parameter, not a cost parameter.

**PF-14 · Accumulator witness update cost.** For a CL/bilinear accumulator, each holder's witness must be updated per change to the set; with *c* changes per epoch and *H* holders, update work is O(*c*·*H*) distributed, or O(*c*) per holder. At *c* = 1,000 revocations/day and *H* = 10^6, 10^9 witness operations/day distributed — the reason Profile AC pushes witnesses to Plane D and Profile SL exists. DERIVED; WO-P3 prices the crossover.

**PF-15 · Cache staleness σ.** A verifier that polls every *t_poll* and caches for *t_cache* observes state at most σ = *t_cache* + *t_poll* old, plus *t_propagate*. σ is therefore a *chosen* term of W, and the P3 rule "ttl from the W budget" is the statement σ ≤ *W_B* − (*t_include* + *t_finalise* + *t_propagate*). DERIVED.

### L3
**PF-16 · BFT collusion probability.** SR-K with *N* = *N_v*, *j* = *f_B*+1, independent *p_c*. Safety fails with probability P(≥ *f_B*+1 compromised):

| *N_v* | *f_B* | *p_c* = 0.01 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|---|
| 4 | 1 | 5.9×10⁻⁴ | 1.4×10⁻² | 5.2×10⁻² | 1.8×10⁻¹ |
| 7 | 2 | 3.4×10⁻⁵ | 3.8×10⁻³ | 2.6×10⁻² | 1.5×10⁻¹ |
| 10 | 3 | 2.0×10⁻⁶ | 1.0×10⁻³ | 1.3×10⁻² | 1.2×10⁻¹ |
| 13 | 4 | 1.2×10⁻⁷ | 2.9×10⁻⁴ | 6.5×10⁻³ | 9.9×10⁻² |
| 16 | 5 | 7.4×10⁻⁹ | 8.1×10⁻⁵ | 3.3×10⁻³ | 8.2×10⁻² |
| 22 | 7 | 2.8×10⁻¹¹ | 6.6×10⁻⁶ | 8.8×10⁻⁴ | 5.6×10⁻² |

DERIVED. Reading: (i) the four-validator sandbox-lineage minimum is not a security configuration at any *p_c*; (ii) the *independence* assumption is the whole result — the correlated validator–issuer row (G-C1) is the statement that *p_c* is not independent across validators sharing an interest, which is why SOL-02 requires governance *diversity*; (iii) at *p_c* = 0.2 no practical *N_v* is adequate, which is the regime SOL-03's detectability (PF-13) is for. **Liveness** fails at ≥ *f_B*+1 *unavailable*; same table with *p_c* read as unavailability.

**PF-17 · Round timeout vs propagation.** QBFT round-change fires at timeout *t_rc*; liveness needs *t_rc* > *D_g*·*t_hop* where *D_g* is the gossip diameter of the validator graph and *t_hop* the per-hop latency. For a fully connected consortium *D_g* = 1 and *t_rc* of a few seconds suffices; the sandbox default should be recorded from the genesis manifest. DERIVED as an inequality.

**PF-18 · Long-range attack.** P(fabricated history accepted by a fresh client) ≤ P(≥ *f_B*+1 *historical* validator keys leaked) × P(client syncs without a trusted checkpoint). The first factor is PF-16 with *p_c* replaced by the key-leak probability over the ledger's lifetime; the second is zero if clients pin the latest public checkpoint (SOL-03) — the weak-subjectivity role. DERIVED.

**PF-19 · PoW reversal at depth z (Option C).** SR-D:

| *q* (α) | *z*=1 | 3 | 6 | 12 | 24 | 48 |
|---|---|---|---|---|---|---|
| 0.1 (0.9) | 2.1×10⁻¹ | 1.3×10⁻² | 2.4×10⁻⁴ | 9.0×10⁻⁸ | 1.3×10⁻¹⁴ | <10⁻¹⁵ |
| 0.3 (0.7) | 6.3×10⁻¹ | 3.3×10⁻¹ | 1.3×10⁻¹ | 2.4×10⁻² | 8.1×10⁻⁴ | 1.0×10⁻⁶ |
| 0.4 (0.6) | 8.3×10⁻¹ | 6.6×10⁻¹ | 5.0×10⁻¹ | 3.1×10⁻¹ | 1.2×10⁻¹ | 2.0×10⁻² |

DERIVED. Depth for P < 10⁻⁶: *z* = 11 at *q* = 0.1; *z* = 49 at *q* = 0.3. With Bitcoin's Δ = 600 s these are 1.8 h and 8.2 h — the reason Option C is unusable for identity *writes* on the W path and acceptable only for checkpoints (where PF-13 absorbs the delay). Note the *effective* *q* under selfish mining (PF-22) is higher than the raw share.

**PF-20 · Forced-inclusion delay (Option B).** A censored transaction can be forced via L1 after the rollup's inclusion-delay parameter *t_FI* (typically hours on current rollups). *t_finalise* ≤ *t_FI* + *t_pub*. Bound is the rollup parameter; ESTIMATED until a specific rollup is named (SR-16).

### L4
**PF-21 · 51 % cost.** To reach *q* ≥ 0.5 against honest hashrate *H_h* for duration *T*: cost ≥ price(*H_h*) × *T*. For Bitcoin at ~7×10^20 H/s and ~$0.05/TH-hour, one hour ≈ **$35 M**; a day ≈ $0.8 B — ESTIMATED (market inputs; retrieval date required). For Option C checkpoints the relevant exposure is *τ_a* + *t_pub* (PF-13), so the attacker's cost is bounded below by price × that window.

**PF-22 · Selfish-mining threshold.** SR-G: (1−*γ*)/(3−2*γ*) → 33 % (*γ*=0), 25 % (*γ*=½), 0 % (*γ*=1). STANDARD-RESULT. Feeds PF-19 by raising the effective *q*.

**PF-23 · Fee percentile vs W (Options B/C).** Let *F*(*g*) be the CDF of the gas price at which a transaction is included within *t_include* ≤ *t_I*. The revocation budget is met with probability *F*(*g_bid*). The U-17 finding restated: the risk is not E[*g*] but the tail — the 99th-percentile congestion cost is what a bounded-W design must pay, so the *variance* of *F* is the cost driver. Formal; numeric requires a fee dataset (ESTIMATED; WO-P2 territory).

**PF-24 · Capacity ceiling M-T2.** Ops per block = *G*/*g_op*; ops per second = *G*/(*g_op*·Δ).

| *G* | *g_op* | ops/block | ops/s (Δ = 2 s) |
|---|---|---|---|
| 30 M | 50 k | 600 | 300 |
| 30 M | 100 k | 300 | 150 |
| 30 M | 180 k | 167 | 83 |
| 100 M | 50 k | 2,000 | 1,000 |
| 100 M | 180 k | 556 | 278 |

DERIVED with *g_op* ESTIMATED; replace by G-B exact integers per option and arm (cold/first-write vs warm/rewrite are two rows, never averaged). Against the PF-04 fleet: 3.12×10^13 identifiers over 20 years = 4.9×10^4 creations/s sustained — **two orders above any row**, which proves the point R2 gap 4.1 raised: the address space is not the constraint, capacity is, and it forces either sharding of Plane A, batching (Sidetree-style, T-I19), or keeping Tier-1 pseudonym issuance off-ledger (T-I05, Q-R1).

**PF-25 · Rotation race window.** Under Option A, the window between a rotation being submitted and being final is *t_include* + *t_finalise* ≈ Δ/2 + Δ = 1.5Δ expected, ≤ 2Δ; at Δ = 2 s: **3 s expected, 4 s worst-case**. No public mempool, so an attacker cannot *see* the pending rotation to race it (BP-L5-05 closed); the residual race is between two parties who *both* already hold the key, decided by inclusion order and recorded (R-R3). DERIVED.

**PF-26 · Rotation window per option.** Option A: as PF-25. Option B: seconds soft + *t_FI* worst. Option C: *z*·Δ_pub with *z* from PF-19 (1.8–8 h at the 10⁻⁶ level). DERIVED.

**PF-27 · Issuer-rotation propagation.** Identical to W (PF-28) with the status update replaced by the DID-document update; same five terms.

**PF-30 · Recovery threshold.** SR-K with *N* = *m_r*, *j* = *t*:

| (*t*, *m_r*) | *p* = 0.01 | 0.05 | 0.10 |
|---|---|---|---|
| (2, 3) | 3.0×10⁻⁴ | 7.3×10⁻³ | 2.8×10⁻² |
| (3, 5) | 9.9×10⁻⁶ | 1.2×10⁻³ | 8.6×10⁻³ |
| (4, 7) | 3.4×10⁻⁷ | 1.9×10⁻⁴ | 2.7×10⁻³ |
| (5, 9) | 1.2×10⁻⁸ | 3.3×10⁻⁵ | 8.9×10⁻⁴ |

DERIVED. The recovery path must be no weaker than the key it recovers: compare each cell with the PF-06 figure for the primary key (2⁻¹²⁸ ≈ 3×10⁻³⁹) — no social-recovery threshold approaches it, so BP-L6-10 is always the weaker path and needs time-locks and on-chain recording (non-repudiation), not just a threshold.

### L6 · the revocation window

**PF-28 · W under settlement options and profiles.**
W = *t_include* + *t_finalise* + *t_propagate* + *t_cache* + *t_poll* (G-C1 §2.7).

| Term | Option A (QBFT, Δ = 2 s) | Option B (rollup) | Option C (L1 PoW) | Owner |
|---|---|---|---|---|
| *t_include* | E = Δ/2 = 1 s; ≤ Δ | seconds (sequencer) | E = Δ_pub/2 = 300 s | Plane A |
| *t_finalise* | ≈ Δ = 2 s (quorum commit) | soft: seconds; hard: batch to L1 (≈ 768 s+) | *z*·Δ_pub: 6,600 s at *z*=11 (PF-19) | Plane A |
| *t_propagate* | gossip to Plane V: *D_g*·*t_hop*, ≈ 0.1–1 s | same | same | L0 / Plane V |
| *t_cache* + *t_poll* | = σ, chosen ≤ *W_B* − above | same | same | Plane V / verifier |
| **Profile SL adds** | list re-fetch on root change (bandwidth, not latency) | | | Plane V |
| **Profile AC adds** | witness delivery to the holder before its next presentation (PF-14) — can exceed all other terms if the holder is offline | | | Plane D |

Illustrative Option A total with σ = 5 s: W ≈ 1 + 2 + 0.5 + 5 = **8.5 s expected, ≈ 10 s worst-case** — DERIVED with σ ESTIMATED. Whether 8.5 s meets a manoeuvre class is Q-R5's budget; the structural result is that **under Option A the ledger contributes ≈ 3 s of W and the rest is the programme's own cache policy**, whereas under Option C the ledger alone contributes hours. PF-13 (checkpointing) adds nothing to W in any option.

**PF-29 · Status-list anonymity set.** A verifier that fetches the *whole* list of *m* entries reveals to the list server only "one of *m*"; *k* = *m* = 131,072 = 2^17. For a *valid* credential the effective set is the unrevoked entries (1−*ρ*)*m*: *ρ* = 0.05 → 124,518; *ρ* = 0.2 → 104,858. A verifier that fetches by *index* has *k* = 1 — the design rule is therefore "whole-list fetch or AC", never index fetch. DERIVED. Profile AC: the holder proves non-membership itself; the server learns nothing per check (*k* = ∞ for that channel), which is the qualitative reason AC is the privacy-maximum profile.

**PF-31 · Tier budget vs read path.** *B_tier*: Tier 1 < 100 ms; Tier 2 100–500 ms. A local cache read is O(10 µs–1 ms); a Plane-V RPC read is O(10–200 ms) depending on network; a Plane-A JSON-RPC read against a remote node is the same order plus node load; any *write* is ≥ PF-25 (≈ 3,000 ms). Hence: Tier 1 admits only local cache; Tier 2 admits a Plane-V read if the network RTT is bounded; Tier 3 admits writes. ESTIMATED orders; measured M-L1/M-L2 from G-B replace them. This is the numeric form of the HAA-1 read-path rule and of BP-L7-07.

---

## 3. The cost surface in numbers

| SOL | Trust base (who must collude) | Finality (*t_include* + *t_finalise*) | Cost / write | Capacity | Source of the number |
|---|---|---|---|---|---|
| SOL-01 sandbox | *N_v* = 1 — none | ≈ Δ (scheduling only, G-B §1.4) | *g_op* exact, free | *G*/*g_op* per block | MEASURED (traces) |
| SOL-02 Option A | > *f_B* of *N_v* (PF-16) | ≈ 1.5Δ = 3 s | free-gas | PF-24: 83–1,000 ops/s | DERIVED |
| SOL-03 anchoring | adds public-chain detectability | +0 to W; PF-13 to detection | one tx per *τ_a* (negligible, WO-P4) | — | DERIVED |
| SOL-04 Option B | sequencer + L1 | seconds soft / ≥ 768 s hard | sub-cent–cents | rollup-bound | ESTIMATED |
| SOL-04 Option C | > 50 % hashpower (PF-21) | 1.8–8 h at 10⁻⁶ (PF-19) | fee tail (PF-23) | L1-bound | DERIVED / ESTIMATED |
| SOL-05 HAA-1 | = SOL-02 + detection | = SOL-02 | = SOL-02 + SOL-03 | = SOL-02 | composition |
| SOL-09 SL vs AC | — | SL: +list fetch; AC: +witness delivery (PF-14) | — | SL: O(*m*) bandwidth; AC: O(*c*·*H*) | WO-P3 |

---

## 4. Sensitivity: which variable dominates each bound, and what changes with the chain

| PF | Dominant variable | Besu QBFT (A) | Public L2 (B) | Public L1 (C) | Indy RBFT (O10) |
|---|---|---|---|---|---|
| 01–04 collision | *a*, κ | *a* = 160 | 160 | 160 | **128** (F-R1) |
| 05 loss | *r* | Plane D policy | + blob DA expiry (~18 days) | — | no archive guarantee (Family E finding) |
| 09 quantum | *h*, key exposure | exposed forever on-chain | same | same | same |
| 10 pairing | curve | — | — | — | CL RSA-2048 ≈ 112 bits |
| 13 detection | *τ_a*, *t_pub* | *τ_a* + *t_pub* | same | *t_pub* large | needs an external anchor too |
| 16 collusion | *N_v*, independence | governance | diluted | diluted | stewards (named) |
| 19 reversal | *q*, *z* | n/a | n/a (batch) | hours | n/a |
| 24 capacity | *G*, *g_op*, Δ | ops/s table | rollup TPS | ~15–30 TPS | 300–1,000 TPS (vendor) |
| 25/26 rotation | Δ, *z* | 3 s | s / *t_FI* | hours | ≈ per-tx finality |
| 28 W | *t_finalise*, σ | ≈ 3 s + σ | s–min + σ | hours + σ | ≈ s + σ |
| 29 anonymity | *m*, profile | SL/AC | same | same | AC native |

The abstraction hook: a later document that swaps the chain changes the column, not the equation; it cites the PF and the new input.

---

## 5. PF index

| PF | Statement (one line) | Variables | Assumptions | Status | Bounds BP | Used by SOL |
|---|---|---|---|---|---|---|
| 01 | key collision ≈ *n*²/2^(κ+1) | *n*, κ | uniform RNG | DERIVED | L1-01 | all |
| 02 | address collision; *n* for target *p* | *n*, *a* | uniform hash | DERIVED | L1-03, L6 namespace | all EVM |
| 03 | per-method DID collision; F-R1 | *a* per method | did:indy *a* = 128 ⟦verify⟧ | DERIVED | L6-01 namespace | 07 |
| 04 | fleet-scale collision 3.3×10⁻²² at 160 bits | *V*, *K*, *Y* | fleet model | DERIVED / EST | — | — |
| 05 | off-chain loss *p_ℓ*^*r* | *r*, *p_ℓ* | independence | DERIVED | L0-05, L2-04 | 05 |
| 06 | security = min(2^128, 2^κ) | κ | SR-C | DERIVED | L1-01 | all |
| 07 | nonce reuse: two signatures | — | ECDSA | STANDARD | L1-02 | all |
| 08 | hash collision 2^128; accidental *N*²/2^257 | *N_obj* | SR-A | DERIVED | L1-03, L2-01 | 03 |
| 09 | Grover: 2^128 / 2^85 / **2^80 (160-bit)**; Shor: exposed keys | *h*, *a* | SR-H/I | STANDARD | L1-04 | all |
| 10 | BN-254 ≈ 100, BLS12-381 ≈ 120, CL-RSA ≈ 112 bits | curve | SR-J | STANDARD | L1-05 | 07 |
| 11 | setup collusion *p_s*^*t_s* | *t_s*, *p_s* | independence | DERIVED | L1-06 | 05 (O15) |
| 12 | side-channel ≤ *T_rot* + PF-26 | *T_rot* | — | design | L1-07 | — |
| 13 | detection ≤ *τ_a* + *t_pub* | *τ_a*, *t_pub* | checkpoint final | DERIVED | L2-02, L4-04 | 03 |
| 14 | witness work O(*c*·*H*) | *c*, *H* | CL accumulator | DERIVED | L2-03 | 09 AC |
| 15 | σ = *t_cache* + *t_poll* ≤ *W_B* − ledger terms | σ | — | DERIVED | L2-05, L7-03 | 05 |
| 16 | BFT collusion table | *N_v*, *f_B*, *p_c* | independence | DERIVED | L3-01, L4-04 | 02 |
| 17 | *t_rc* > *D_g*·*t_hop* | timeout | partial synchrony | DERIVED | L3-03 | 02 |
| 18 | long-range ≤ PF-16(leak) × P(no checkpoint) | — | — | DERIVED | L3-04 | 03 |
| 19 | Nakamoto reversal table; *z* = 11 / 49 | *q*, *z* | SR-D | DERIVED | L3-05 | 04 C |
| 20 | forced inclusion ≤ *t_FI* + *t_pub* | rollup | — | ESTIMATED | L3-06 | 04 B |
| 21 | 51 % cost ≈ price × *H_h* × *T* | market | — | ESTIMATED | L4-01 | 04 C |
| 22 | selfish threshold (1−γ)/(3−2γ) | γ | SR-G | STANDARD | L4-02 | 04 C |
| 23 | budget met with prob *F*(*g_bid*); variance drives | *F* | fee data | ESTIMATED | L4-03 | 04 |
| 24 | ops/s = *G*/(*g_op*·Δ); fleet needs 4.9×10⁴/s | *G*, *g_op*, Δ | *g_op* EST | DERIVED/EST | L4-05 | 02 |
| 25 | rotation race 1.5Δ ≈ 3 s, ≤ 2Δ | Δ | QBFT | DERIVED | L5-05, L6-02 | 02 |
| 26 | rotation window per option | Δ, *z* | — | DERIVED | L6-02 | 02/04 |
| 27 | = PF-28 for DID updates | — | — | DERIVED | L6-03 | 05 |
| 28 | W table; A ≈ 3 s + σ | five terms | Δ = 2 s | DERIVED/EST | L6-04 | 05, 09 |
| 29 | *k* = (1−ρ)*m*; index fetch *k* = 1 | *m*, ρ | whole-list fetch | DERIVED | L6-05 | 09 |
| 30 | recovery threshold table; always weaker than key | *t*, *m_r*, *p* | independence | DERIVED | L6-10 | — |
| 31 | tier admits cache / RPC / write by order of magnitude | *B_tier* | latency orders EST | ESTIMATED | L7-07 | 05 |

---

*End of R4 v0.1. Every number above is a function of a §0 symbol and an §0.2 result; nothing is asserted bare. The three inputs the researcher owns — Q-R5's W budgets, the genesis manifest's Δ and G, and the Pass 4 fleet sizes — convert the ESTIMATED rows to DERIVED without touching an equation.*
