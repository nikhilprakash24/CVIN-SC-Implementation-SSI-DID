# CVIN-SC · R7 — Theory and ECE Bounds for the Full Identity Stack

**The quantitative floor under the Phase 2 atlas: the security reductions the identity stack actually rests on, stated as games or cited theorems; the distributed-computing conditions under which the ledger terms of W exist at all; the hardware, radio and clock bounds that sit *below* L0 and decide whether the ledger is ever the bottleneck; the repository's measured gas converted into capacity; and the metric definitions that R8 will cite as measurement dimensions.**

| Field | Value |
|---|---|
| Document | R7 of the Roots suite, Phase 2 (thread G-R1) |
| Version | v0-1 (first pass) |
| Date | 2026-10-23 |
| Consumes | R4 v0.1 (SYM-01..24, PF-01..31, SR-A..K, frozen); R3 v0.1 (BP- tags, flows IV.1–IV.3); Phase 1 README (SOL-01..09); `PHASE2_SHARED_BRIEF.md` v1.0; claim register `docs/MEASUREMENT_CONDITIONS.md` (rows cited as #n); `docs/LATENCY_BUDGET.md`; `docs/SCALING_EXPERIMENTS.md`; `docs/THREAT_MODEL.md`; `docs/phase2/briefs/I-05_FRESHNESS.md`, `I-24_IDTX.md`; `cv2x-testbed/identity/freshness.py`; `cv2x-testbed/protocols/cv2x_stack.py`; `5_zkp-agent-identity/` (circuit, results); `docs/testing/GAS_CHARTER.md`; `1_blockchain-identity/results/metrics/latest/` |
| Assigns | `SYM-25`–`SYM-58`, `SR-L`–`SR-T`, `PF-32`–`PF-62`, `PAR-01`–`PAR-26`, `Q-R7-01`–`Q-R7-08`, `KD-R4-01`–`KD-R4-09` |
| Cites, not owned | `⟦ALG-??⟧`, `⟦HW-??⟧`, `⟦IMP-L3.2-?? Besu⟧`, `⟦SCF-ERC1056-??⟧` (R6); `⟦MD-??⟧` (R8) |
| Status vocabulary | MEASURED (register row or result file) · DERIVED (equation + inputs) · DESIGN (specified, not built) · ESTIMATED · STANDARD (cited specification or theorem). A status is never upgraded. |
| Reproducibility | Every number below is printed, with its equation and inputs, by `docs/roots/phase2/70_R7_theory_ece_bounds/r7_calc.py` (python3, numpy 2.5, scipy 1.18; seed 42 for the two Monte-Carlo checks). Section letters A–L in its output are cited as `calc §X`. |

Progress ▓▓▓▓▓▓▓░░░ 70 % (v0-1: all sections drafted and computed; v0-2 to resolve R6 tags, check the ESTIMATED radio and HSM figures against primary sources, and take panel comments from R9.)

**How to read.** §1 extends the notation; nothing from R4 is redefined. §2 (cryptography) and §3 (distributed computing) are the *theory* half: what the identity binding is as strong as, and when the ledger's terms of W are defined. §4 (hardware, radio, clocks) and §5 (EVM) are the *engineering* half: where the real bottlenecks are. §6 formalises freshness. §7 is written for R8: one PF per measurement dimension, as a formula with inputs. §8 declares the parameters that depend on choices not yet made. §9 indexes every PF; §10 is the handoff, including the places where the repository contradicts Phase 1 (KD-R4-01..09). Read §3.4 before quoting any latency number measured in this repository.

---

## 1. Notation extension (SYM-25 onward)

R4 §0 stays in force (W, σ, *N_v*, *f_B*, *Δ*, *G*, *g_op*, *B_tier*, the five W terms). Bare `A`, `f`, `N` remain avoided; availability is *A_L*, a budget fraction is *f_id* (the repo's "*f*" in `LATENCY_BUDGET.md` §1), a neighbour count is *P*.

| SYM | Symbol | Name | Units | Standard symbol | Default / where set |
|---|---|---|---|---|---|
| SYM-25 | *H_∞* | min-entropy per raw RNG sample | bits/sample | *H* (NIST SP 800-90B) | device-specific; PAR-08 |
| SYM-26 | *r_RNG* | raw noise-source sample rate | samples/s | — | device-specific |
| SYM-27 | *t_sig* | one signature generation on the signing unit | ms | — | HW class (PAR-07) |
| SYM-28 | *t_ver* | one signature verification (warm, key cached) | ms | — | MEASURED 0.14225 ms software SSI (#27); HW class otherwise |
| SYM-29 | *v_max* | verifications per second of one unit | s⁻¹ | — | 1/*t_ver* |
| SYM-30 | *f_id* | identity share of the BSM interval | — | *f* in `LATENCY_BUDGET.md` §1 | 0.5 (repo working point) |
| SYM-31 | *P* | neighbours whose BSMs a verifier must check | count | — | 50–300 scenario |
| SYM-32 | *r_BSM* | BSM rate per sender | Hz | — | 10 (SAE J2945/1, STANDARD) |
| SYM-33 | *ρ_v* | verifier utilisation | — | *ρ* (queueing) | *P*·*r_BSM*·*t_ver* |
| SYM-34 | *φ_v* | fraction of received BSMs verified (verify-on-demand) | — | — | 1 (verify-all) |
| SYM-35 | CBR | channel busy ratio | — | CBR (SAE J2945/1, ETSI TS 102 687) | target ≤ 0.6 (ESTIMATED congestion-control knee) |
| SYM-36 | PRR | packet reception ratio at distance *d* | — | PRR | radio-dependent |
| SYM-37 | *P_keep* | PC5 mode 4 resource-keep probability at reselection | — | *probResourceKeep* (3GPP TS 36.321) | 0–0.8 |
| SYM-38 | *T_air* | channel time of one BSM incl. access gap | µs | — | §4.3 |
| SYM-39 | *L_sec* | 1609.2 security overhead per message | B | — | digest ≈ 86, cert ≈ 162–210 (ESTIMATED) |
| SYM-40 | *a_msg* | message age at the receiver | s | — | — |
| SYM-41 | *ε_t* | absolute receiver clock error (vs UTC) | s | — | GNSS-locked ≈ 10⁻⁷ (ESTIMATED) |
| SYM-42 | *d_clk* | oscillator drift in holdover | ppm | — | 0.5–50 |
| SYM-43 | *T_max,age* / *T_max,fut* | freshness window (past / future) | s | — | 1.0 / 0.1 (`freshness.py` DEFAULT_MAX_AGE_S / DEFAULT_MAX_FUTURE_S) |
| SYM-44 | *C_rc* | replay-cache capacity | entries | — | 65,536 (`freshness.py` DEFAULT_REPLAY_CACHE_SIZE) |
| SYM-45 | RTT | network round-trip time on the read path | ms | — | localhost ≈ 1–2 ms (#39); WAN PAR-14 |
| SYM-46 | *F_g* | gossip fan-out | peers | fan-out | PAR-15 |
| SYM-47 | *t_rc* | QBFT base round-change timeout | s | *requestTimeoutSeconds* (Besu) | DESIGN; PAR-04 |
| SYM-48 | *g_F* | measured gas of IMinimalSSI / IDTX function *F* | gas | — | crud_gas run `2026-10-23T00-49-12Z_1f4ace0`; refines SYM-23 per function |
| SYM-49 | *G_HH* | Hardhat block gas limit of record | gas | `blockGasLimit` | **60,000,000** MEASURED (`results/metrics/latest/meta.json` → network.blockGasLimit) |
| SYM-50 | *π* | Groth16 proof size (calldata) | B | — | 256 B MEASURED (#57) |
| SYM-51 | *t_prove* / *t_vzk* | proving / off-chain verifying time | ms | — | 398.6 / 18.42 median MEASURED (#57) |
| SYM-52 | *g_vzk* | on-chain Groth16 verification gas | gas | — | 256,038 view estimate; 301,163 gated tx MEASURED (#58) |
| SYM-53 | *n_C* | circuit constraint count | count | R1CS size | 3,498 MEASURED (#56) |
| SYM-54 | *k* (freshness) | re-check period in messages | messages | — | `ERC1056Provider.set_refresh_every`; I-05. **Distinct from SYM-01 *k*** — written *k_f* where both appear. |
| SYM-55 | *t_local*, *t_chain* | cached-path verify; added cost of one refresh | ms | — | 0.346 / 13.94 ms (#32, A3b re-run) |
| SYM-56 | *A_L* | link availability of RSU backhaul | — | *A* (renewal theory) | PAR-17 |
| SYM-57 | *μ_on*, *μ_off* | mean up / down sojourn of the backhaul | s | — | PAR-17 |
| SYM-58 | *W_0* | W excluding backhaul outage | s | — | R4 PF-28 illustrative 8.5 s (DESIGN) |

**Standard results added (SR-L onward; cited, not re-proved).**

| ID | Result | Statement | Source |
|---|---|---|---|
| SR-L | ECDSA in the GGM | ECDSA is EUF-CMA if the group is generic and the conversion and hash satisfy stated properties; advantage ≲ *q*²/*n_G* for *q* group operations | Brown 2005 (GGM); Fersch–Kiltz–Poettering 2016 |
| SR-M | Keccak as ROM | Sponge indifferentiable from a RO up to ≈ 2^(*c*/2) queries; keccak-256 capacity *c* = 512 → 2^256 generic bound; collision 2^128 by SR-A | Bertoni et al. 2008 |
| SR-N | Groth16 knowledge soundness | Knowledge-sound in the generic bilinear group / under q-PKE-type knowledge assumptions; in the AGM reducible to q-DLOG; *requires* the CRS trapdoor be unknown | Groth 2016; Fuchsbauer–Kiltz–Loss 2018 |
| SR-O | Pedersen commitment | Perfectly hiding; computationally binding under DLOG | Pedersen 1991 |
| SR-P | QBFT/IBFT | Safety for *N_v* ≥ 3*f_B*+1 under asynchrony; liveness under partial synchrony with round-change; IBFT 1.0 had a liveness defect fixed in IBFT 2.0/QBFT | Moniz 2020; Saltini–Hyland-Wood 2019 |
| SR-Q | DLS partial synchrony | Consensus solvable once message delays are bounded after an unknown GST | Dwork–Lynch–Stockmeyer 1988 |
| SR-R | CAP / PACELC | Under partition choose C or A; else trade latency vs consistency | Gilbert–Lynch 2002; Abadi 2012 |
| SR-S | Renewal-reward / residual life | For a stationary alternating renewal process, P(down) = *μ_off*/(*μ_on*+*μ_off*); residual down-time mean = E[*X*²]/(2E[*X*]) | standard (Ross) |
| SR-T | EIP-1108 gas schedule | BN254 ecAdd 150, ecMul 6,000, pairing 45,000 + 34,000·*k* | EIP-1108 (Istanbul) |

---

## 2. Security reductions, stated properly

*What this level does for the level above:* L6 (DID method, credential) and L7 (V2X message, IDTX) claim that "the message came from the vehicle whose DID it names". *What it trusts from below:* that the signature, the hash and the ledger behave as their assumptions say. This section makes the "as strong as" relation explicit, so that R8 can attach an assumption class and a tightness to each functionality instead of the word "secure".

### 2.1 PF-32 · ECDSA secp256k1 / P-256 unforgeability

**Game EUF-CMA.** Challenger draws (*sk*, *pk*); adversary 𝒜 gets *pk* and a signing oracle; wins on a valid (*m*\*, *σ*\*) with *m*\* never queried. **Statement (STANDARD, SR-L):** in the generic group model with hash *H* modelled appropriately, Adv^EUF-CMA_ECDSA(𝒜) ≤ O(*q*²/*n_G*) + Adv_H, *n_G* ≈ 2^256. Numbers (calc §L): *q* = 2^64 → 2⁻¹²⁸; *q* = 2^80 → 2⁻⁹⁶; *q* = 2^100 → 2⁻⁵⁶.

**Caveats that matter to this programme (each a link to an existing BP):**
1. *The GGM is not a real-curve proof.* No standard-model reduction of ECDSA to ECDLP exists; the bound is heuristic evidence, the same class as R4 SR-C. Status: STANDARD with stated idealisation.
2. *Malleability.* ECDSA is not strongly unforgeable: (*r*, −*s* mod *n*) is a second valid signature. The repository's replay cache keys on sha256 of the *signed bytes*, not the signature (`freshness.py` docstring §3), which is exactly the defence; EVM `ecrecover` callers rely on the low-*s* rule (EIP-2). MEASURED as a design property, not a number.
3. *Nonce.* EUF-CMA assumes uniform nonces; R4 PF-07 (two signatures) and its lattice extension (calc §G: a *b*-bit bias needs on the order of 256/*b* signatures, ESTIMATED order of magnitude) bound the *implementation* failure, which dominates the GGM figure by more than 100 orders of magnitude. ethers signs RFC 6979-deterministically (`GAS_CHARTER.md` §2), which closes PF-07 in the harness, not on a vehicle.
4. *Entropy.* Effective security is min(2^128, 2^κ) (R4 PF-06); PF-41 below makes κ a hardware quantity.

### 2.2 PF-33 · Keccak-256 collision resistance and the ROM

keccak-256 is a sponge with capacity *c* = 512. **Statement (STANDARD, SR-M):** generic collision 2^128 (SR-A at *S* = 2^256), second preimage 2^256 bounded by min(2^256, 2^(*c*/2)) = 2^256. EVM addresses truncate to *a* = 160 bits, which changes the *namespace* bound (R4 PF-02) but not the commitment bound: a commitment that stores the full 256-bit digest (`IdentityCommitments._value`, `phase2/idtx/contracts/IdtxExecutor.sol`; the ZK-VIN anchor, #58) inherits 2^128 collision security. Quantum: 2^85 (BHT, R4 PF-09). The ROM idealisation is used by every Fiat–Shamir step in `5_zkp-agent-identity/zkid` (Schnorr, Chaum–Pedersen, CDS-OR; #59) — those proofs are ROM proofs, not standard-model ones.

**Low-entropy preimages are not covered.** The ROM bound is over uniformly distributed inputs. A VIN with only a 6-digit serial unknown has log₂ 10⁶ = 19.93 bits of min-entropy, and an unsalted hash of it falls to enumeration in 3.58 s (MEASURED #60; 10⁶ / 279,587 hashes/s, calc §L). This is a hiding failure, not a collision-resistance failure, and is the reason for PF-34.

### 2.3 PF-34 · Commitments: binding and hiding

Two commitment forms appear in the repository: (i) hash commitments *C* = H(*x* ‖ *s*) with salt *s* (ZK-VIN anchor; `IdentityCommitments`); (ii) Pedersen *C* = *g*^*x* *h*^*s* in `zkid` (#59).
- **Hash commitment.** Binding ≤ Adv^CR_H ≈ 2^−128 (PF-33). Hiding is computational and holds in the ROM iff *s* has ≥ λ bits of min-entropy; with *s* empty, hiding reduces to the min-entropy of *x* (19.93 bits for the VIN serial, PF-33). DERIVED.
- **Pedersen.** Perfectly hiding; binding under DLOG in the group (SR-O); if log_g *h* is known to anyone, binding is void — a setup assumption of the same type as Groth16's (PF-35).

### 2.4 PF-35 · Groth16 knowledge soundness and the setup assumption

**Statement (STANDARD, SR-N).** For the ZK-VIN circuit (*n_C* = 3,498 constraints, 1,667 non-linear; 3,505 wires; 6 public inputs and 1 public output; #56), Groth16 over BN254 is knowledge-sound in the AGM under q-DLOG, given an honestly generated CRS. Concrete security is capped by the curve: BN254 ≈ 100 bits after TNFS (R4 PF-10, SR-J).

**The setup term, with the repository's actual ceremony.** R4 PF-11 bounds a multi-party ceremony by *p_s*^*t_s*. The repository's setup is **single-party and explicitly insecure** (#57: "the insecure single-party setup ... rules out production use"). Then *t_s* = 1 and P(trapdoor known) = *p_s*, i.e. the soundness of every on-chain `ZkVinGate.admit` is *conditional on trusting one machine*. → KD-R4-05. Status: MEASURED (setup type) + DERIVED.

**Zero-knowledge** of Groth16 is perfect given the simulator's trapdoor; it is *not* affected by a leaked trapdoor (a leak breaks soundness, not privacy). Proof size *π* = 256 B as calldata (#57) is constant in *n_C*; verification is constant in *n_C* and linear in the public-input count (PF-51).

### 2.5 PF-36 · Composition lemma: identity binding is as strong as its weakest link

Define the event **BIND-FAIL**: a verifier *V* accepts a message *m* as sent by subject DID *D* at time *t*, while *D*'s controller (as fixed by the ledger's final state at *t* − σ) did not sign *m*. Let the stack be: signature scheme Σ (PF-32), hash *H* used to bind *m* and the DID document (PF-33), registry ledger *L* with *non-equivocation* — no two honest readers see conflicting final states for *D* (PF-16 / §3), and resolver *R* with *integrity* — *R* returns the document the ledger state implies, at most σ old (PF-15, PF-54).

**Lemma (PF-36).** For any efficient adversary 𝒜,

  Adv^BIND(𝒜) ≤ Adv^EUF-CMA_Σ(ℬ₁) + Adv^CR_H(ℬ₂) + Adv^EQUIV_L(ℬ₃) + Adv^INT_R(ℬ₄) + P(revocation inside σ),

and therefore, up to the additive form, binding is **as strong as min(signature, registry non-equivocation, resolver integrity)** in security-bits terms: −log₂ Adv^BIND ≥ min_i(−log₂ ε_i) − log₂ 5.

*Proof sketch.* Hybrid argument over the verifier's acceptance path. H₀: real experiment. H₁: replace the resolver's output by the document computed directly from the ledger's final state at *t* − σ; the difference is Adv^INT_R (ℬ₄ runs 𝒜 and outputs the mismatch). H₂: replace "the ledger state any reader sees" by "the unique final state"; the difference is the probability that two readers see different final states, Adv^EQUIV_L (ℬ₃ outputs the two conflicting views — for QBFT, two finalised blocks at one height, i.e. > *f_B* Byzantine validators, PF-16). H₃: replace H(document) / H(*m*) by an injective map; the difference is Adv^CR_H (ℬ₂ outputs the colliding pair). In H₃ the verification key is fixed by the unique, correctly resolved document; an accepting (*m*, *σ*) not produced by the controller is a forgery, so 𝒜's success in H₃ is ≤ Adv^EUF-CMA_Σ (ℬ₁ embeds the challenge key as *D*'s key, guessing *D* among *n_D* subjects if needed — a multiplicative *n_D* loss, the tightness caveat). The residual term is the legitimate window: a key revoked within σ is still accepted (BP-L6-04). ∎

**Worked instance (calc §L, DERIVED from ESTIMATED inputs).** ε_Σ = 2⁻¹²⁸, ε_H = 2⁻¹²⁸, ε_L = PF-16 at *N_v* = 4, *p_c* = 0.05 = 1.40×10⁻², ε_R = 10⁻⁶ (an assumed resolver-bug rate): sum = 1.40×10⁻². **The ledger term exceeds the cryptographic terms by about 37 orders of magnitude (1.40×10⁻² vs 2.9×10⁻³⁹)**; strengthening the curve buys nothing until *N_v* and governance independence move. This is the formal form of R4's reading of PF-16 and of SOL-02's governance-diversity requirement.

**Tightness.** The reduction to Σ loses a factor *n_D* (subjects) in the multi-user setting; for *n_D* = 3.12×10¹³ (R4 PF-04) that is ≈ 2^44.8, leaving ≈ 83 bits from a 128-bit scheme in the worst-case multi-user bound. Tight multi-user ECDSA bounds exist in idealised models; this document states the loose one. R8's "reduction tightness" (PF-59) uses this loss figure.

---

## 3. Distributed-computing theory

*What this level does for the level above:* it is what makes *t_include* and *t_finalise* well-defined terms of W, and what makes ε_L in PF-36 small. *What it trusts from below:* bounded message delay after GST (L0), authenticated channels (L1), and the validator count and independence that governance (L4.2) supplies. **Every QBFT number in this section is DESIGN** — the repository has no executed Besu or QBFT trace (`PHASE2_SHARED_BRIEF.md` §2; `docs/phase2/focus/F2_chains_and_databases/CAPTURE.md` row 5 and line 220: "Not deployed, configured or measured").

### 3.1 PF-37 · QBFT/IBFT safety and liveness conditions

**Statement (STANDARD, SR-E, SR-P, SR-Q).** With *N_v* validators of which at most *f_B* are Byzantine:
- *Safety* (no two conflicting finalised blocks at one height) holds for *N_v* ≥ 3*f_B* + 1 **without any timing assumption**: two commit quorums of size ⌈2*N_v*/3⌉ intersect in ≥ *f_B* + 1 validators, at least one honest, and an honest validator never commits two values at one height.
- *Liveness* requires partial synchrony: after GST, message delay ≤ δ, and the round-change timer *t_rc*·2^*r* eventually exceeds the time for one honest proposer's round (R4 PF-17).
- *Round change.* A round fails if the proposer is crashed or Byzantine or the timer fires; QBFT doubles the timeout per round (exponential back-off), which is what guarantees that some round eventually exceeds the unknown δ.

Quorums and the safety Nakamoto threshold for the requested sizes (calc §B):

| *N_v* | *f_B* | commit quorum ⌈2*N_v*/3⌉ | validators to break safety (*f_B*+1) | validators to halt liveness (*f_B*+1) |
|---|---|---|---|---|
| 4 | 1 | 3 | 2 | 2 |
| 7 | 2 | 5 | 3 | 3 |
| 10 | 3 | 7 | 4 | 4 |
| 13 | 4 | 9 | 5 | 5 |
| 16 | 5 | 11 | 6 | 6 |
| 22 | 7 | 15 | 8 | 8 |

### 3.2 FLP and how each client sidesteps it

FLP (SR-F) forbids deterministic consensus in full asynchrony with one crash. Each relevant L3.2 client escapes it differently, and the escape route is the assumption a measurement must state:

| Client / mode | Escape route | Consequence for W | Status in repo |
|---|---|---|---|
| ⟦IMP-L3.2-?? Besu⟧ QBFT | partial synchrony (DLS): liveness only after GST; safety always | *t_finalise* unbounded during asynchrony, bounded after (PF-40) | DESIGN |
| Geth Clique (PoA) | gives up finality: longest-chain among authorised signers, probabilistic | *t_finalise* is a depth choice, like PF-19 | not used |
| Ethereum Gasper (Sepolia) | synchrony for LMD-GHOST liveness; Casper FFG finality needs 2/3 stake; can stall finality under asynchrony | *t_finalise* ≈ 768 s (2 epochs) when live | Sepolia harness exists (`1_blockchain-identity/SEPOLIA_VALIDATION.md`); register M2 rows "not yet run on this trunk" |
| Bitcoin Nakamoto | probabilistic agreement + synchrony | PF-19 depth | not used |
| **Hardhat automine** | **no distributed agreement at all**: *N_v* = 1, a single process orders transactions | see §3.4 | **the executed chain** |

### 3.3 PF-38 · Message complexity per QBFT round

Per height in the normal case: PRE-PREPARE (proposer → *N_v* − 1), PREPARE (all-to-all, *N_v*(*N_v* − 1)), COMMIT (all-to-all, *N_v*(*N_v* − 1)); a ROUND-CHANGE adds *N_v*(*N_v* − 1). Total *M*(*N_v*) = (*N_v* − 1)(2*N_v* + 1) = Θ(*N_v*²). DERIVED; per-message size 200 B ESTIMATED (calc §B):

| *N_v* | pre-prepare | prepare | commit | *M* per round | + round change | kB/round @ 200 B | kB/s at Δ = 2 s |
|---|---|---|---|---|---|---|---|
| 4 | 3 | 12 | 12 | 27 | 39 | 5.4 | 2.7 |
| 7 | 6 | 42 | 42 | 90 | 132 | 18.0 | 9.0 |
| 10 | 9 | 90 | 90 | 189 | 279 | 37.8 | 18.9 |
| 13 | 12 | 156 | 156 | 324 | 480 | 64.8 | 32.4 |
| 16 | 15 | 240 | 240 | 495 | 735 | 99.0 | 49.5 |
| 22 | 21 | 462 | 462 | 945 | 1,407 | 189.0 | 94.5 |

Reading: consensus traffic is below 100 kB/s at every size, negligible against any server backhaul (LH.5); the quadratic term matters for *signature verification* per validator — (2*N_v* − 1) ECDSA verifies per height per validator (43 at *N_v* = 22), < 1 ms of CPU at *t_ver* = 0.14 ms. **Consensus messaging is not the bottleneck at consortium sizes**; capacity (PF-49) and round-change latency (PF-40) are.

### 3.4 PF-39 · Hardhat automine is a degenerate *N_v* = 1 system (critical honesty point)

The run of record states `"automine": true`, `"blockGasLimit": 60000000`, `"hardfork": "osaka"` (`1_blockchain-identity/results/metrics/latest/meta.json`); register M1 says latency "includes the local JSON-RPC hop only ... must not be presented as" public-network latency (`MEASUREMENT_CONDITIONS.md` §1). Formally:

- *N_v* = 1, *f_B* = 0: PF-16 gives P(safety failure) = *p_c* (one operator). There is no quorum, no gossip, no round change; t_include = scheduling of one process; t_finalise ≡ 0 (instant and trivially "final").
- **There is no block interval Δ.** Automine seals one block per transaction; Δ is not a parameter of the measured system. Every expression in R4 that uses Δ = 2 s (PF-24, PF-25, PF-28) is therefore **DESIGN**, not a property of SOL-01. → KD-R4-02.
- What the measured latencies *are*: the cost of the client, the JSON-RPC hop and EVM execution — e.g. U3 `setAttribute` tx median 7.828 ms / p95 10.715 ms in-process (`tables/crud_latency_tx.md`, M1-H), 17.2 ms over localhost HTTP (#39). These are **lower bounds on *t_include*** for any real chain and say nothing about *t_finalise*.
- **Consequence for every claim.** A latency or finality number measured on Hardhat may be quoted only as "client + RPC + execution cost, *N_v* = 1, no consensus". Gas, by contrast, *is* portable: it is deterministic across EVM networks for identical bytecode and state (`SEPOLIA_VALIDATION.md`; #39 shows HTTP vs in-process gas identical on all common cells). So the repository's **gas** feeds DERIVED capacity bounds (§5); its **latency** feeds only the read-path and client-overhead terms (PF-31, PF-54), never t_finalise.

### 3.5 PF-40 · Time-to-confirm under round changes (expected and tail)

Model (DESIGN): a transaction arrives uniformly within a height (t_include ~ U(0, Δ)), commit takes Δ, and each round whose proposer is down adds *t_rc*·2^*r* (*r* = 0, 1, …). With round-robin proposer selection and *c* consecutive crashed proposers starting at the height's first proposer, the extra delay is *t_rc*(2^*c* − 1). Exact averages over the starting proposer (calc §C2; Δ = 2 s, *t_rc* = 10 s, both PAR):

| *N_v* | crashed (adjacent in rotation) | E[t_conf] | worst case 2Δ + max extra |
|---|---|---|---|
| 4 | 1 | 5.50 s | 14 s |
| 7 | 1 | 4.43 s | 14 s |
| 7 | 2 | 8.71 s | 34 s |
| 10 | 3 | 14.00 s | 74 s |
| 22 | 7 (= *f_B*) | 115.27 s | 1,274 s |

With no faults E[t_conf] = 1.5Δ = 3 s, max 2Δ = 4 s (R4 PF-25 recovered). An independent-failure approximation (each round's proposer down with probability φ < ½) gives E[extra] = *t_rc*·φ/(1 − 2φ): 5.0 s at φ = 0.25 and 2.0 s at φ = 1/7; Monte Carlo p99 = 72.97 s and p99.9 = 312.02 s at φ = 0.25 (calc §C). **The tail, not the mean, is the design quantity:** with *f_B* adjacent crashed proposers the worst case grows as *t_rc*·2^*f_B*, so larger consortia have *longer* liveness tails unless *t_rc* or proposer ordering is tuned. For comparison (DERIVED, calc §C): Bitcoin *z* = 6 / 11 confirmations ~ Erlang(*z*, 600 s): mean 1.00 / 1.83 h, p99 2.18 / 3.36 h; Ethereum L1 finality 2 × 32 × 12 s = 768 s.

### 3.6 CAP / PACELC placement of SOL-01..09

| SOL | Under partition (P) | Else (E) | Note |
|---|---|---|---|
| 01 sandbox (Hardhat) | n/a (single node: partition = total unavailability) | L (one process, no replication) | degenerate, §3.4 |
| 02 Option A (QBFT) | **C** (halts below quorum; fails safe and late, R4 PF-02′) | C | DESIGN |
| 03 public anchoring | C for the anchor (inherits public chain) | L (anchoring off the W path) | detection only, PF-13 |
| 04 Option B rollup | A (sequencer keeps accepting; soft confirmations) / C at L1 settlement | L (soft) | |
| 04 Option C L1 PoW | A (forks continue) | L at the cost of probabilistic C | PF-19 |
| 05 HAA-1 | write plane C; **read plane A** (cached reads continue, bounded by σ) | read L, write C | the split that makes Tier 1 feasible |
| 06 IMinimalSSI | inherits substrate | inherits | interface, not a system |
| 07 LFDT stack (Indy RBFT) | C | C | |
| 08 Family F composite | per component | per component | |
| 09 SL / AC profiles | A at the verifier (stale list or witness) | L | σ / witness freshness |

The structural reading: the programme's safety-critical path is **PA/EL by design** (cached reads at the verifier) sitting on a **PC/EC** write plane; PF-54 bounds the cost of that availability choice as σ.

---

## 4. ECE, hardware and wireless bounds

*What this level does for the level above:* LH and L0.1 decide whether a V2X message is *generated, carried and verified* in time; if they fail, no ledger property matters. *What it trusts from below:* physics, silicon and the radio standards. The point of this section is quantitative: **under realistic hardware, verification throughput and channel airtime bind long before the ledger does on the Tier-1 path.** Hardware latency figures are ESTIMATED classes (PAR-07) unless a register row is cited; the only measured verify times in the repository are software on Xeon hosts (#27, #26).

### 4.1 PF-41 · Hardware RNG entropy and key-generation failure

Let a device generate keys with effective entropy κ (R4 SYM-02). For *n* keys, P(any two equal) = 1 − exp(−*n*(*n*−1)/2^(κ+1)) (SR-A); expected colliding pairs ≈ *n*²/2^(κ+1). With the fleet *n* = 3.12×10¹³ (R4 PF-04) (calc §G):

| κ (bits) | P(shared key in fleet) | colliding pairs, 10⁶ devices | colliding pairs, 1.5×10⁹ devices |
|---|---|---|---|
| 32 | ≈ 1 | 116 | 2.6×10⁸ |
| 40 | ≈ 1 | 0.45 | 1.0×10⁶ |
| 48 | ≈ 1 | 1.8×10⁻³ | 4.0×10³ |
| 128 | 1.43×10⁻¹² | — | — |
| 256 | 4.20×10⁻⁵¹ | — | — |

**Reading.** A κ = 48 RNG (a plausibly bad boot-time seed on an ECU) produces ≈ 4,000 shared-key pairs across one key per vehicle in the global parc — a *real* failure mode, as the 2012 "Mining your Ps and Qs" survey of shared RSA/DSA keys showed for embedded devices. At κ = 128 the fleet-wide risk is 1.4×10⁻¹². κ is a hardware property (LH.1/LH.2), so PF-06's min(2^128, 2^κ) is decided below L0. DERIVED; κ PAR-08.

### 4.2 PF-42 · Entropy-source health and seeding time

NIST SP 800-90B repetition-count test cut-off *C* = 1 + ⌈−log₂ α / *H_∞*⌉ with α = 2⁻²⁰ (STANDARD): *H_∞* = 1.0 → 21; 0.5 → 41; 0.1 → 201 identical samples before alarm. Time to accumulate a 256-bit security strength plus 64-bit margin: *t_seed* = 320/(*r_RNG*·*H_∞*): 0.64 ms at 10⁶ samples/s, *H_∞* = 0.5; 64 ms at 10⁴; **4 s** at 100 samples/s, *H_∞* = 0.8 (calc §G). Reading: a slow jitter source on a microcontroller that issues its first key within 4 s of cold boot is the boot-time κ failure of PF-41; the design rule is "no key generation before the DRBG reports full seeding". DERIVED; inputs ESTIMATED.

### 4.3 PF-43 · Verification load: when verification, not the ledger, is the bottleneck

Per-verifier load is λ = *P*·*r_BSM* verifications/s; utilisation *ρ_v* = λ·*t_ver*; budget-feasible neighbour count *P*\*(*f_id*) = ⌊*f_id*·(1/*r_BSM*)/*t_ver*⌋ (the repo's `LATENCY_BUDGET.md` §2 formula, with 100 ms = 1/*r_BSM*). With Poisson-like arrivals and deterministic service (M/D/1), mean wait *W_q* = *ρ_v t_ver*/(2(1 − *ρ_v*)) (STANDARD). Values (calc §D):

| Verifier class | *t_ver* | *v_max* = 1/*t_ver* | *P*\*(0.5) | *ρ_v* at *P* = 50 / 100 / 200 / 300 | Status |
|---|---|---|---|---|---|
| Software SSI warm, Xeon 2.10 GHz | 0.14225 ms | 7,030 /s | 351 | 0.07 / 0.14 / 0.28 / 0.43 | MEASURED (#27) |
| Software PKI warm, same run | 0.0904 ms | 11,062 /s | 553 | 0.05 / 0.09 / 0.18 / 0.27 | MEASURED (#27) |
| V2X security ASIC / HSM class | 0.25 ms | 4,000 /s | 200 | 0.12 / 0.25 / 0.50 / 0.75 | ESTIMATED |
| Automotive application processor, software (Cortex-A53 class) | 1.0 ms | 1,000 /s | 50 | 0.50 / **1.00** / 2.00 / 3.00 | ESTIMATED |
| Automotive MCU HSM (EVITA-full class) | 5.0 ms | 200 /s | 10 | **2.5** / 5 / 10 / 15 | ESTIMATED |

Load λ = 500 / 1,000 / 2,000 / 3,000 verifications/s at *P* = 50 / 100 / 200 / 300. At *ρ_v* ≥ 1 the queue is unstable: the backlog grows without bound (the repo's consequence 1, `LATENCY_BUDGET.md` §1). For the ASIC class, M/D/1 sojourn is 0.292 / 0.375 / 0.625 ms at *P* = 100 / 200 / 300 — comfortably inside the 100 ms Tier-1 budget (*B_tier*, SYM-24).

The repo's measured linear model (#26: 0.164 ms/neighbour, R² 0.9998) gives *P*\*(0.5) = 50/0.164 = 304.9 and *P*\*(1) = 609.8 — the register's "≈305 at f = 0.5" and "P\* ≈ 609" reproduce (calc §D; the register itself flags *P*\* as a linear extrapolation beyond the tested *P* ≤ 80).

**Verify-on-demand (IEEE 1609.2 practice; STANDARD in kind, numbers DERIVED).** When *ρ_v* > *f_id*, a receiver can verify only a fraction *φ_v* = min(1, *f_id*/*ρ_v*) of BSMs — in practice those from vehicles a safety application is about to act on. At *t_ver* = 1 ms: *φ_v* = 0.250 (*P* = 200), 0.167 (*P* = 300); at 5 ms: 0.050 / 0.033. *φ_v* < 1 is a security parameter (unverified BSMs feed only non-actuating logic), and belongs in R8's tier-fit dimension.

**Compare the ledger side.** On the cached path the ledger is touched once per *k_f* messages per sender: 10·*P*/*k_f* reads/s per vehicle, i.e. 1,000 / 3,000 at *k_f* = 1 (*P* = 100 / 300), 40 / 120 at *k_f* = 25, 11.1 / 33.3 at *k_f* = 90 (calc §D). With *k_f* = ∞ (HAA-1 read rule) the ledger is off the Tier-1 path entirely and **verification throughput on the OBU is the binding constraint**: an MCU-class HSM saturates at *P* = 20 neighbours (*f_id* = 1), an order below dense-traffic *P*. This is the quantitative answer to "when is the ledger not the bottleneck": whenever *k_f* ≥ *r_BSM*·*P*·*t_chain*/(*f_id*/*r_BSM*), and always under HAA-1.

**Signing side.** Duty cycle *r_BSM*·*t_sig*: 0.005 at *t_sig* = 0.5 ms (ASIC), 0.100 at 10 ms (MCU HSM) — signing is never the bottleneck for one's own BSMs (calc §D). DERIVED; *t_sig* ESTIMATED.

### 4.4 PF-44 · Channel airtime and how many vehicles fit

**IEEE 802.11p (10 MHz, 6 Mb/s QPSK ½; STANDARD PHY timing).** *T_air* = 40 µs (preamble + SIGNAL) + 8 µs × ⌈(16 + 8*L* + 6)/48⌉, plus an AC_VO access gap AIFS = 32 + 2 × 13 = 58 µs. Payload sizes: BSM part I ≈ 40 B (J2735 UPER, ESTIMATED), WSMP 6 B, MAC + LLC + FCS 36 B (ESTIMATED); 1609.2 overhead *L_sec* ≈ 86 B with a digest signer, ≈ 162 B with an implicit (ECQV) certificate, ≈ 210 B with an explicit certificate (ESTIMATED orders from the 1609.2 structures). Vehicles that fit at CBR = 0.6: *N_fit* = 0.6/(*r_BSM*·*T_air*) (calc §E):

| Identity payload | MPDU | *T_air* + AIFS | CBR per vehicle | *N_fit* at CBR 0.6 | Status |
|---|---|---|---|---|---|
| none | 82 B | 218 µs | 0.0022 | 275 | DERIVED / EST sizes |
| 1609.2 digest | 168 B | 330 µs | 0.0033 | 182 | DERIVED / EST |
| 1609.2 implicit cert | 244 B | 434 µs | 0.0043 | 138 | DERIVED / EST |
| 1609.2 explicit cert | 292 B | 498 µs | 0.0050 | 120 | DERIVED / EST |
| digest 4 of 5, cert 1 of 5 | — | 364 µs (mix) | 0.0036 | 165 | DERIVED |
| **repo JSON, ERC-1056 (DID only)** | 632 B | 946 µs | 0.0095 | **63** | size MEASURED (#23: 596 B) |
| **repo JSON, PKI (PEM cert)** | 1,146 B | 1,634 µs | 0.0163 | **37** | size MEASURED (#23: 1,110 B) |

Security is 34 % of a digest-signed BSM's airtime and 56 % of an explicit-certificate one. **The repository's message encoding (JSON) costs 2.9× (ERC-1056) to 5.0× (PKI) the airtime of a compact 1609.2 digest BSM**; the 596 B vs 1,110 B comparison in #23 is real but both are far from deployable sizes. The register row is a *size* finding; channel capacity is this DERIVED consequence.

**LTE-V2X PC5 mode 4 (STANDARD structure, ESTIMATED link budget).** 10 MHz = 50 PRB; with 10-PRB sub-channels, 5 per 1 ms sub-frame, 1,000 sub-frames/s; ≈ 190 B per sub-channel at a typical MCS including SCI (ESTIMATED). Sub-channels per packet ⌈*L*/190⌉: digest-signed BSM (152 B) → 1 sub-channel → 5,000 packets/s → 500 vehicles at 10 Hz (CBR 1) or 300 at CBR 0.6; implicit/explicit certificate (228–276 B) → 2 → 120 at CBR 0.6; repo JSON ERC-1056 (596 B) → 4 → 60; repo JSON PKI (1,110 B) → 6 sub-channels, **exceeds one 10 MHz sub-frame** at this MCS (does not fit without a higher MCS). DERIVED.

**Resource reselection and pseudonym linkability (PF-44c).** In sensing-based SPS a vehicle keeps its resource for a counter *C* ~ U[5, 15] reservations at RRI = 100 ms, then keeps it again with probability *P_keep*. Expected resource lifetime E[*C*]·RRI/(1 − *P_keep*) = 1.00 / 1.67 / 5.00 s at *P_keep* = 0 / 0.4 / 0.8; probability the same resource persists 1 s after a pseudonym change ≈ exp(−1/lifetime) = 0.368 / 0.549 / 0.819 (calc §F, exponential approximation). **A pseudonym change that does not also force resource reselection is linkable at L0.1 with probability ≈ 0.37–0.82** — an identity-privacy breaking point below every DID-layer mechanism (R6 should place it as a BP-L0.1; here it is PF-44c). `cv2x_stack.py` models a 50-PRB × 4-sub-channel grid and computes CBR as occupied/total (lines 128–202) but has no reselection counter, so this is not measurable on the testbed as it stands (Q-R7-04).

### 4.5 PF-47 · GNSS time error, clock holdover and freshness windows

The receiver accepts a message with generation time *t_g* iff −*T_max,fut* ≤ *t_rx* − *t_g* ≤ *T_max,age* (`freshness.py`, FreshnessPolicy.check). With sender and receiver clock errors ε_s, ε_r, the measured age is *a_msg* + (ε_r − ε_s). Conditions (DERIVED):
1. *No false reject of fresh messages* requires |ε_r − ε_s| ≤ *T_max,fut* = 0.1 s.
2. *Holdover.* Two clocks drifting oppositely at *d_clk* diverge at 2*d_clk*; the window survives GNSS loss for *T_hold* = *T_max,fut*/(2*d_clk*): **27.78 h** at 0.5 ppm (TCXO), 6.94 h at 2 ppm, 0.69 h at 20 ppm, **0.28 h** at 50 ppm (uncompensated crystal) (calc §H).
3. *GNSS-locked margin.* ε_t ≈ 100 ns (ESTIMATED) against a 0.1 s window is a 10⁶× margin; **GNSS time is not the constraint while locked — oscillator holdover in tunnels and urban canyons is.**
4. *Spoofing.* A spoofer who shifts the receiver's clock by δ_s widens the acceptance of replays by δ_s; the replay cache (PF-53) is the only defence once δ_s > *T_max,age*. The freshness window therefore inherits GNSS integrity (LH.4) as an assumption; it is not cryptographically self-sufficient.
5. *Physical meaning of T_max,age.* A 1.0 s-old BSM places a vehicle 14 / 30 / 40 m behind its true position at 14 / 30 / 40 m/s (calc §H) — the window is a safety parameter as much as a security one.

### 4.6 PF-53 · Replay-cache sizing

Within the window *w* = *T_max,age* + *T_max,fut* = 1.1 s, a receiver must hold *r_BSM*·*P*·*w* entries: 550 / 1,100 / 3,300 / 6,600 at *P* = 50 / 100 / 300 / 600. The default *C_rc* = 65,536 holds ⌊65,536/11⌋ = **5,958 senders** with no live eviction. The `freshness.py` docstring says "about 650 senders at 10 Hz for 1.1 s, with a margin of ten"; the arithmetic is 65,536/(10 × 1.1 × 10) = **596** (calc §H). Minor repository-internal inconsistency, reported, not a Phase 1 contradiction (Q-R7-06). DERIVED.

### 4.7 PF-48 · RSU backhaul intermittency and revocation latency W as a renewal process

Model (DESIGN): an RSU learns revocations over a backhaul that alternates up/down as a stationary alternating renewal process with means *μ_on*, *μ_off*; availability *A_L* = *μ_on*/(*μ_on* + *μ_off*). A revocation event arriving at a random time sees the link down with probability 1 − *A_L* and then waits the residual down-time *R* (SR-S). Then

  W = *W_0* + 𝟙{down}·*R*,  E[W] = *W_0* + (1 − *A_L*)·E[*X*²]/(2E[*X*]),

which for exponential down-times is *W_0* + (1 − *A_L*)·*μ_off*, with tail P(W > *W_0* + *x*) = (1 − *A_L*)·e^(−*x*/*μ_off*), so the *q*-quantile is *W_0* + *μ_off*·ln((1 − *A_L*)/(1 − *q*)) when 1 − *A_L* > 1 − *q*, else *W_0*. Down-time variability raises the mean residual: deterministic 0.5·*μ_off*, exponential 1.0·*μ_off*, coefficient of variation 2 → 2.5·*μ_off*. With *W_0* = 8.5 s (R4 PF-28, DESIGN) (calc §I; Monte Carlo 400,000 draws agrees to < 2 %):

| *μ_off* | *A_L* | E[W] | p99 | p99.9 |
|---|---|---|---|---|
| 10 s | 0.99 | 8.60 s | 8.5 s | 31.5 s |
| 10 s | 0.95 | 9.00 s | 24.6 s | 47.6 s |
| 60 s | 0.95 | 11.50 s | 105.1 s | 243.2 s |
| 60 s | 0.90 | 14.50 s | 146.7 s | 284.8 s |
| 600 s | 0.99 | 14.50 s | 8.5 s | 1,390.1 s |
| 600 s | 0.95 | 38.50 s | 974.2 s | 2,355.7 s |
| 600 s | 0.90 | 68.50 s | 1,390.1 s | 2,771.6 s |

**Reading.** The *mean* hides the problem: at 99 % availability and 10-minute outages E[W] is only 14.5 s but the p99.9 is 23 minutes. **Revocation-latency guarantees must be stated as tail quantiles of the backhaul's down-time distribution, not as availability percentages.** A poll-based RSU (period *T_p*) adds U(0, *T_p*): +0.5 / 5 / 30 s mean, +1 / 10 / 60 s max at *T_p* = 1 / 10 / 60 s. Measured RSU behaviour in the repo bounds staleness in *messages* (k − 1 SPaT, #46) with "no propagation delay; lookup cost not modelled" — PF-48 is the missing time model (Q-R7-05).

---

## 5. Smart-contract and EVM quantification

*What this level does for the level above:* fixes the cost and throughput of each identity function, which the cost and capacity dimensions in R8 cite. *What it trusts from below:* the EVM gas schedule (L5.1, STANDARD) and the block budget (L4.3). **This section replaces R4's ESTIMATED *g_op* with MEASURED per-function gas** from the run of record `2026-10-23T00-49-12Z_1f4ace0` (`1_blockchain-identity/results/metrics/latest/tables/crud_gas.md`, condition M1-H, register rows #29/#34/#54 for the values; gas class G-exact or G-mode per `docs/testing/GAS_CHARTER.md` §2). **Gas is MEASURED; ops/s is DERIVED; every Δ is a PAR (DESIGN)** because the executed chain has no Δ (PF-39).

### 5.1 PF-49 · Capacity for the repository's actual block gas limit

*G_HH* = 60,000,000 (MEASURED, `meta.json`). ops/block = ⌊*G*/*g_F*⌋; ops/s = *G*/(*g_F*·Δ) (R4 PF-24 equation unchanged) (calc §J):

| Function (ERC-1056 pure column unless stated) | *g_F* (gas) | Source | ops/block | ops/s Δ=1 | Δ=2 | Δ=5 | Δ=12 |
|---|---|---|---|---|---|---|---|
| C1 create identity (with VIN binding) | 76,830 | #29/#34 | 780 | 781 | 390 | 156 | 65 |
| U1 rotate controller (`changeOwner`) | 51,754 | crud_gas | 1,159 | 1,159 | 580 | 232 | 97 |
| U2 add delegate | 55,143 | crud_gas | 1,088 | 1,088 | 544 | 218 | 91 |
| U3 set attribute | 35,024 | #29 | 1,713 | 1,713 | 857 | 343 | 143 |
| U5 relayed `setAttributeSigned` | 62,646 | #50 | 957 | 958 | 479 | 192 | 80 |
| D1 revoke delegate | 32,868 | crud_gas | 1,825 | 1,825 | 913 | 365 | 152 |
| D2 revoke attribute | 34,576 | crud_gas | 1,735 | 1,735 | 868 | 347 | 145 |
| V3 anchor status | 33,918 | crud_gas | 1,768 | 1,769 | 884 | 354 | 147 |
| V5 revoke credential | 33,470 | #29 | 1,792 | 1,793 | 896 | 359 | 149 |
| P1 create presentation | 34,206 | #54 | 1,754 | 1,754 | 877 | 351 | 146 |
| RSU anchors key (seed 1) | 52,606 | #47 | 1,140 | 1,141 | 570 | 228 | 95 |
| pseudonym `addDelegate`, steady | 54,807 | #38 | 1,094 | 1,095 | 547 | 219 | 91 |
| CVIN-Combined C1 | 271,402 | #34 | 221 | 221 | 111 | 44 | 18 |
| ERC-4337 U5 (UserOp) | 141,767 | #34 | 423 | 423 | 212 | 85 | 35 |
| MOBI `attestEvent` (execution gas) | 198,694 | #28 | 301 | 302 | 151 | 60 | 25 |
| `ZkVinGate.admit` (Groth16 on chain) | 301,163 | #58 | 199 | 199 | 100 | 40 | 17 |
| ERC-735 C1 | 1,757,881 | #34 | 34 | 34 | 17 | 7 | 3 |

At R4's 30 M / 100 M rows and Δ = 2 s, ERC-1056 C1 gives 195 / 651 ops/s and V5 448 / 1,494 ops/s. Note the measured ERC-1056 functions span 32,868–76,830 gas, **below** R4's assumed 50k–180k band, whereas CVIN-Combined, ERC-4337, ERC-735 and the ZK gate lie inside or far above it; one *g_op* per option was never adequate — capacity is a per-function vector. The IDTX functions (`IdtxExecutor.execute`, `createIntent`, `fulfil`) have **no measured gas**: `phase2/idtx/test/idtx.test.js` line 1 says "Behaviour only: no gas or latency here is a result"; E-F1-1 (I-24 brief §7.1) predicts +5,700–6,500 (Owner) and +6,000–7,000 (Delegate) over the action, unrun. They are therefore ESTIMATED and omitted from the table (Q-R7-03).

### 5.2 PF-50 · Fleet scenario of R4 PF-04 under measured gas

R4 PF-24 converted the fleet's 3.12×10¹³ identifiers over 20 years into 4.943×10⁴ creations/s. Two repository facts change its interpretation (calc §J):
1. **A `did:ethr` identity costs 0 gas to create** (#47: "identity creation 0 (did:ethr is implicit)"). Creation is off-ledger; the ledger load is whatever *anchoring* the design requires.
2. The measured anchoring operation for pseudonyms is `addDelegate` at 54,807 gas steady state (#38). Demand = 4.943×10⁴ × 54,807 = **2.71×10⁹ gas/s** against *G_HH*/Δ = 3.0×10⁷ gas/s at Δ = 2 s: **90.3× over capacity**; equivalently 3,901,388 blocks/day needed against 43,200 available. With C1 (76,830 gas) instead: 126.6×. The register's per-vehicle figure — 1,096,368 gas per 20-pseudonym epoch (#38) — scaled to 1.5×10⁹ vehicles per week gives **90.6×** capacity: the two routes agree.

DERIVED from MEASURED gas and ESTIMATED fleet inputs. R4's qualitative conclusion stands (capacity, not the address space, binds), but the correct numeric statement is "~90× at the repo's 60 M gas limit and Δ = 2 s, for anchoring, with creation itself free", not "two orders above any row" at 30 M. → KD-R4-04.

### 5.3 PF-51 · Groth16 on-chain verification: EIP-1108 model vs measured gas

A snarkjs Groth16 verifier performs one 4-pairing check and one multi-scalar multiplication over the public inputs (the repository's `Groth16Verifier.sol` issues `staticcall` to precompiles 6, 7 and the pairing check, and declares 16 IC constants). With *k* = 4 pairings and *n_pub* = 7 public signals (#57), SR-T gives (calc §J):

  pairing 45,000 + 34,000·4 = 181,000; ecMul 6,000·7 + ecAdd 150·7 = 43,050; calldata ≤ 16 × 484 B = 7,744; + 21,000 base ⇒ **252,794 gas** (DERIVED upper bound on calldata).

Measured `verifyProof` view estimate (includes 21,000): **256,038** (#58). Residual **3,244 gas** (1.3 %) is memory expansion, field checks and dispatch. **The model and the measurement agree to 1.3 %**, so the verifier cost is understood opcode-by-opcode and scales as 181,000 + 6,150·*n_pub* + calldata. The gated `admit` (301,163) adds 45,125 gas for the gate's storage and event. Under the pre-EIP-1108 (Byzantium) schedule the same verification would cost 703,500 gas in precompiles alone. One ZK admission costs 3.92× an ERC-1056 C1. Constant in *n_C* = 3,498: a larger circuit costs proving time (398.6 ms median, #57), not gas.

### 5.4 PF-52 · Storage cost of a DID document

Cold zero→non-zero SSTORE = 20,000 + 2,100 (EIP-2929 cold access) = 22,100 gas per 32-byte word (STANDARD). A document stored as contract state costs ⌈*L*/32⌉ × 22,100: **707,200 gas** for 1 kB, 1,414,400 for 2 kB, 3,536,000 for 5 kB. Emitted as event data (LOG3: 375 + 3 × 375 + 8 gas/byte) it costs 9,317 / 17,509 / 42,085 gas — a factor ≈ 76–84 cheaper (calc §J). This is the mechanism behind the measured footprint ranking: ERC-1056 U3 executes 1 SSTORE with 0 zero→non-zero and 288 B of event log, ERC-735 13 SSTOREs (12 zero→non-zero) and 1,024 B (#49); and behind the read-side price — ERC-1056 resolution grows to 112 RPC calls / 87 KB at history 50, median 91.113 ms in-process (#31). Write cheapness is bought with read-path cost linear in history: the cost-surface trade that R8's trilemma coordinate (PF-58) records.

---

## 6. Freshness and time

*What this level does for the level above:* turns "the verifier's view of the identity is recent enough" into a bound that L7 can budget. *What it trusts from below:* clocks (PF-47), the ledger's finality (§3), and the cache policy of the verifier. Two freshness notions exist in the repo and must not be confused (I-05 brief §1): **message freshness** (`freshness.py`: the *message* is ≤ *T_max,age* old and not replayed) and **state freshness** (`ERC1056Provider.set_refresh_every(k)`: the cached *identity state* is ≤ *k_f* − 1 messages old).

### 6.1 PF-54 · State staleness vs read path

**Definition.** For a verifier refreshing a sender's state every *k_f* messages, with sender message rate *r_s*:
- staleness in messages ≤ *k_f* − 1 (MEASURED exactly, #32: 0 / 4 / 24 at *k_f* = 1 / 5 / 25, 35/35 trials; #46 for RSUs);
- staleness in time σ_k = (*k_f* − 1)/*r_s* **only if *r_s* is known and constant** — the style rule 1.1.9 ("a bound on messages is not a bound on time unless the time was measured", I-05 brief §1). At *k_f* = 25: 2.4 s at 10 Hz, 24 s at 1 Hz, 240 s at 0.1 Hz (calc §K). A sender that goes quiet makes a message-bounded cache *unbounded in time*; this is why R4's σ (a time) and the repo's *k_f* (a count) are different quantities. → KD-R4-06.
- amortised cost *t_eff*(*k_f*) = *t_local* + *t_chain*/*k_f* (MEASURED fit within 1–4 %, #32), with *t_local* = 0.346 ms, *t_chain* = 13.94 ms (A3b re-run): *t_eff* = 14.286 / 3.134 / 0.904 / 0.501 / 0.441 ms and *P*\*(0.5) = 3 / 15 / 55 / 99 / 113 at *k_f* = 1 / 5 / 25 / 90 / 146. The knee ⌈*t_chain*/(0.5 − *t_local*)⌉ = 91 reproduces the register's "*k* ≈ 90" (calc §K).

**PF-54 bound (DERIVED).** Total identity-state age at the verifier ≤ σ_k + *t_include* + *t_finalise* + *t_propagate*, i.e. W (R4 PF-28) with σ = σ_k, **provided σ_k is bounded by a time-to-live as well as by *k_f***. The recommended policy is min(*k_f* messages, *T_ttl* seconds), which gives σ ≤ min((*k_f* − 1)/*r_s*, *T_ttl*) and removes the quiet-sender hole.

### 6.2 PF-55 · Optimal re-check period under a staleness budget

Minimise *t_eff*(*k_f*) subject to (*k_f* − 1)/*r_s* ≤ σ_max. Since *t_eff* decreases in *k_f*, the optimum is the boundary *k_f*\* = ⌊*r_s*·σ_max⌋ + 1 (DERIVED). At *r_s* = 10 Hz: σ_max = 1 s → *k_f*\* = 11 (*t_eff* = 1.613 ms, *P*\*(0.5) = 30); 2.5 s → 26 (0.882 ms, 56); 10 s → 101 (0.484 ms, 103) (calc §K). **The security budget σ_max, not cost, chooses *k_f*; the measured knee (*k_f* ≈ 90) corresponds to accepting ≈ 9 s of revoked-key acceptance at 10 Hz.** This answers I-05's question in closed form for the deterministic-rate case; revocation-rate dependence enters only through the expected number of revoked-message acceptances, (*k_f* − 1)/2 per revocation on average.

### 6.3 PF-56 · Relation of freshness to σ and W, and what each repo component bounds

| Term | Bounded by | Repo evidence | Status |
|---|---|---|---|
| message age | *T_max,age* + |ε_r − ε_s| | `freshness.py` 1.0 s / 0.1 s | MEASURED (code) / DERIVED (PF-47) |
| replay | *C_rc* ≥ *r_BSM*·*P*·*w* | default 65,536 → 5,958 senders | DERIVED (PF-53) |
| state staleness (messages) | *k_f* − 1 | #32, #37, #46, #52 | MEASURED |
| state staleness (time) σ | min((*k_f*−1)/*r_s*, *T_ttl*) | no TTL in the provider | DESIGN (PF-54) |
| ledger terms | t_include + t_finalise | Hardhat only | DESIGN (PF-39, PF-40) |
| backhaul | (1 − *A_L*)·residual | none | DESIGN (PF-48) |

W = (ledger terms) + *t_propagate* + σ + backhaul term. On the executed system the ledger terms are client overhead only (PF-39); the dominant *measured* contributor is σ_k.

---

## 7. Measurement-dimension metric definitions (for R8)

*What this section does for the level above:* R8 defines the measurement dimensions `⟦MD-??⟧`; it needs, for each, one formula whose inputs are register rows or PARs. Each PF below is that formula. Statuses refer to the *formula's inputs* as the repo stands.

| PF | Dimension | Formula / metric | Inputs (where from) | Status today |
|---|---|---|---|---|
| **PF-57** | Time to confirm (expected, tail) | E[t_conf] = E[t_include] + E[t_finalise] + E[round-change extra]; tail Q_q(t_conf) from PF-40 (BFT), Erlang(*z*, Δ_pub) (PoW), fixed 768 s (Gasper); on Hardhat report only "client+RPC" t_tx | Δ, *t_rc*, *N_v*, proposer-failure model (PAR-02..05); M1-H `crud_latency_tx` for client cost | DESIGN (consensus) / MEASURED (client) |
| **PF-58** | Trilemma position | coordinates (*T*, *L*, *C*) on R3's cost surface: *T* = −log₁₀ PF-16(*N_v*, *p_c*) (decentralisation-security), *L* = log₁₀ E[t_conf] (latency), *C* = log₁₀ of ops/s from PF-49 (scalability) | PF-16, PF-57, PF-49 | DERIVED |
| **PF-59** | Protocol security | (assumption class, reduction loss, concrete bits): class ∈ {GGM, ROM, AGM+q-DLOG, BFT-count, setup-trust}; bits = min_i(−log₂ ε_i) − log₂(terms) − log₂ *n_D* | PF-32..36 | DERIVED |
| **PF-60** | Decentralisation confidence | (i) Nakamoto coefficient *NC* = *f_B* + 1 (validators to break safety; same for liveness) ; (ii) collusion probability PF-16; (iii) client diversity HHI = Σ *s_c*² over client shares (1.0 for all-Hardhat; 0.5 for two equal clients) and Shannon *H* = −Σ *s_c* ln *s_c* (ln 3 = 1.099 for three equal); (iv) governance-diversity score = number of distinct controlling organisations among validators ÷ *N_v* | *N_v*, *p_c*, client shares, operator registry (PAR-01, PAR-06) | DERIVED / DESIGN; today HHI = 1.0, *NC* = 1 |
| **PF-61** | Smart-contract security | vector: (a) fraction of state-changing functions with an access check (`onlyIdentityOwner`-style or signature) ; (b) fraction with replay protection (nonce + domain incl. chain id); (c) mutation kill rate = killed / total; (d) attack-matrix pass rate; (e) audit status (none / internal / external) | (c) IDTX 5/5 gate mutants caught in CI (`docs/phase2/focus/F1_onchain_storage_idtx/EXECUTION.md`); ZK 5 mutants (`5_zkp-agent-identity/README.md`); L3-SSI 30/30 (`AFTER_ACTION_REPORT_12.md`); (d) 43/43 DEFENDED, 11 N/A (#28); (b) ERC-1056 signed ops bind registry + nonce, chain-id binding narrowed (D52, `THREAT_MODEL.md` G3); (a), (e) not yet tabulated | MEASURED for (c), (d); open for (a), (e) |
| **PF-62** | Privacy | anonymity set *k_A* and linkability *ℓ*: status list *k_A* = (1 − ρ)*m* (R4 PF-29); anchor batch *b* (R4 PF-04′); L0.1 linkability ℓ_RF = exp(−Δt/lifetime) (PF-44c); chain-layer linkability of pseudonym pools = 60/60 via one `eth_getLogs` (#38); hiding entropy of committed attributes (19.93 bits for an unsalted VIN serial, PF-33/#60); report min-entropy bits log₂ *k_A* (17 bits at *m* = 131,072) | R4 PF-29, PF-44, #38, #60, #61 | MEASURED / DERIVED |
| **PF-57a** | Availability | write availability = P(≥ ⌈2*N_v*/3⌉ validators up) (PF-16 with unavailability); read availability = 1 − P(cache miss)·(1 − *A_L*); revocation availability tail = PF-48 quantiles | *N_v*, *A_L*, *μ_off* | DESIGN |
| **PF-49** | Capacity | ops/s per function = *G*/(*g_F*·Δ); fleet ratio = demand·*g_F*/(*G*/Δ) | `crud_gas`, *G_HH* = 60 M, Δ (PAR) | MEASURED gas / DERIVED |
| **PF-43** | Tier fit | Tier 1: *ρ_v* = *P*·*r_BSM*·*t_ver* ≤ *f_id* and read path = cache (R4 PF-31) and *φ_v* reported; Tier 2: RTT + server time ≤ 500 ms; Tier 3: t_conf any | *t_ver* (#27 or HW class), *P*, RTT | MEASURED (sw) / ESTIMATED (HW) |
| **PF-52** / **PF-50** | Cost | gas per function *g_F* (G-class stated); lifetime gas (#35); storage vs log ratio | `crud_gas`, #35, #49 | MEASURED |

Rules for R8: cite the PF, not the number; quote gas with its GAS_CHARTER class; never place a Hardhat latency in a time-to-confirm cell (PF-39).

---

## 8. Parameters to declare (PAR-)

Every input that depends on an implementation choice. **Undecided choices are left undecided**; "current default" is what the repository or Phase 1 *uses*, with its status.

| PAR | Name | Symbol | Unit | Feeds PF | Current default and source | Decided? |
|---|---|---|---|---|---|---|
| PAR-01 | Validator count | *N_v* | count | 16, 36, 37, 38, 40, 57, 60 | 1 (Hardhat, executed); 4 (R4 sandbox lineage, DESIGN) | no |
| PAR-02 | Block interval | Δ | s | 24, 25, 28, 40, 49, 57 | none on automine (PF-39); 2 s in R4 (DESIGN, unsourced genesis) | no |
| PAR-03 | Block gas limit | *G* | gas | 24, 49, 50 | 60,000,000 MEASURED (`meta.json`) for Hardhat; Besu genesis absent | partly |
| PAR-04 | QBFT round-change base timeout | *t_rc* | s | 17, 40, 57 | none in repo | no |
| PAR-05 | Proposer selection policy | — | — | 40 | none (round-robin assumed) | no |
| PAR-06 | Client implementation(s) and shares | *s_c* | — | 60 | Hardhat 2.28.6 only (#21, `meta.json`) | no |
| PAR-07 | Signing / verifying hardware class | *t_sig*, *t_ver* | ms | 34, 43, 57 | software on Xeon (#27); ECU/HSM unspecified | no |
| PAR-08 | RNG min-entropy and seeding policy | *H_∞*, κ | bits | 41, 42 | host OS CSPRNG (harness keys are deterministic keccak-derived, register §5.A) | no |
| PAR-09 | Signature curve for V2X | — | — | 32, 43 | secp256k1 (ERC-1056, coincurve); P-256 for PKI arm (#27) | no |
| PAR-10 | Radio technology and channel | — | — | 44 | `cv2x_stack.py` PC5 mode 4 model (50 PRB × 4 sub-channels); no 802.11p model | no |
| PAR-11 | MCS / data rate | — | Mb/s | 44 | 6 Mb/s (802.11p calc); ≈190 B/sub-channel (PC5 calc), both ESTIMATED | no |
| PAR-12 | Message encoding and 1609.2 profile | *L_sec* | B | 44 | JSON (596 B / 1,110 B, #23) | no |
| PAR-13 | Identity budget fraction | *f_id* | — | 43, 54, 55 | 0.5 (`LATENCY_BUDGET.md` §1, project choice) | yes (working) |
| PAR-14 | Read-path RTT class | RTT | ms | 31, 43, 57 | localhost 1–2 ms (#39); WAN none (M2 not run) | no |
| PAR-15 | Gossip fan-out / topology | *F_g*, *D_g* | — | 17, 28 | none | no |
| PAR-16 | Freshness window | *T_max,age*, *T_max,fut* | s | 47, 53 | 1.0 / 0.1 (`freshness.py`, project choice) | yes (default) |
| PAR-17 | RSU backhaul availability model | *A_L*, *μ_off*, CV | —, s | 48, 57a | none | no |
| PAR-18 | Re-check period and TTL | *k_f*, *T_ttl* | msgs, s | 54, 55 | *k_f* configurable; no TTL | no |
| PAR-19 | Replay-cache size | *C_rc* | entries | 53 | 65,536 (`freshness.py`) | yes (default) |
| PAR-20 | Revocation profile | SL / AC | — | 29, 62 | Phase 1 SOL-09 both | no |
| PAR-21 | Proof system and setup | — | — | 35, 51 | Groth16 BN254, single-party insecure setup (#57) | no (prototype only) |
| PAR-22 | Pseudonym budget | *K* | per year | 04, 50 | 1,040 (R4, ESTIMATED); 20 per 5-min epoch in #38 experiment | no |
| PAR-23 | Fleet size | *V* | vehicles | 04, 50 | 1.5×10⁹ (R4, ESTIMATED) | no |
| PAR-24 | Settlement option | A / B / C | — | 26, 28, 57 | Hardhat executed; Sepolia harness; A/B/C DESIGN | no |
| PAR-25 | Manoeuvre-class W budgets | *W_B* | s | 02′, 15, 48, 54 | Q-R5 (open since Phase 1) | no |
| PAR-26 | Neighbour density scenario | *P* | count | 43, 44, 53 | 50–300 (this document); SUMO 50 configured, not run (#15) | no |

---

## 9. PF index (continuing R4's format)

| PF | Statement (one line) | Variables | Assumptions | Status | Bounds BP | Used by SOL |
|---|---|---|---|---|---|---|
| 32 | ECDSA EUF-CMA ≤ q²/n_G in GGM; malleability, nonce, entropy caveats | *q*, κ | GGM, uniform nonce | STANDARD | L1-01, L1-02 | all |
| 33 | keccak CR 2^128 (ROM/sponge); low-entropy preimage 19.93 bits → 3.58 s (#60) | *c*, *H_∞* | ROM | STANDARD / MEASURED | L1-03, L6-05 | 03, 05, ZK |
| 34 | hash commitment binding 2^−128, hiding iff salted; Pedersen perfect hiding, DLOG binding | *s*, setup of *h* | ROM / DLOG | DERIVED | L1-03, L6-05 | 03, ZK |
| 35 | Groth16 knowledge-sound (AGM, q-DLOG, honest CRS); repo setup single-party ⇒ P = *p_s* | *t_s*, *p_s* | SR-N | STANDARD / MEASURED setup | L1-05, L1-06 | ZK (SOL-10+ ⟦R6⟧) |
| 36 | composition: Adv^BIND ≤ Σ ε (sig, CR, equivocation, resolver) + σ-window; *n_D* loss | ε_i, *n_D* | hybrids | DERIVED | L6-02, L6-04, L3-01 | 05, 06 |
| 37 | QBFT safety N_v ≥ 3f_B+1 (async), liveness after GST; quorum ⌈2N_v/3⌉ | *N_v*, *f_B* | SR-P, SR-Q | STANDARD / DESIGN | L3-01, L3-02, L3-03 | 02 |
| 38 | QBFT messages (N_v−1)(2N_v+1) per round; 27…945 for N_v 4…22 | *N_v* | normal case | DERIVED | L3-02 | 02 |
| 39 | Hardhat automine = N_v = 1, no Δ, t_finalise ≡ 0; latency = client+RPC only; gas portable | — | `meta.json` | MEASURED (config) / DERIVED | L3-01, L7-07 | 01 |
| 40 | t_conf with round changes: E 3 s fault-free; 5.50 s (N_v=4, 1 crash); worst t_rc·2^f_B | Δ, *t_rc*, φ | round-robin | DERIVED / DESIGN | L3-02, L3-03, L6-04 | 02 |
| 41 | RNG κ → fleet shared-key pairs (4.0×10³ at κ=48; 1.43×10⁻¹² at κ=128) | κ, *n* | SR-A | DERIVED | L1-01 (LH.1 ⟦BP-LH-??⟧) | all |
| 42 | 90B RCT cut-off 21/41/201; seeding 0.64 ms–4 s | *H_∞*, *r_RNG* | SP 800-90B | DERIVED / EST | L1-01 | all |
| 43 | verify load ρ_v = P·10·t_ver; P*(0.5) 351 sw, 200 ASIC, 50 A53, 10 MCU; φ_v | *t_ver*, *P* | M/D/1 | MEASURED sw / EST hw | L7-07 | 05 |
| 44 | airtime: N_fit 182 (digest) … 63 (repo JSON) at CBR 0.6; PC5 300/120/60; reselection linkability 0.37–0.82 | *L*, MCS, *P_keep* | PHY timing STANDARD | DERIVED / EST | L0-04, L6-05 | 05 |
| 47 | GNSS/clock: holdover T = T_fut/(2d): 27.8 h…0.28 h; spoofing widens replay | *d_clk*, ε_t | GNSS integrity | DERIVED | L0-01, L7-03 | 05 |
| 48 | RSU backhaul renewal: E[W] = W_0 + (1−A_L)·resid; p99.9 up to 2,772 s | *A_L*, *μ_off*, CV | SR-S | DERIVED / DESIGN | L6-04, L0-02 | 05, 09 |
| 49 | capacity ops/s = G/(g_F·Δ) per function at G = 60 M MEASURED | *g_F*, *G*, Δ | Δ PAR | MEASURED gas / DERIVED | L4-05 | 02, 06 |
| 50 | fleet anchoring 90.3× over capacity (60 M, Δ=2); creation 0 gas | *V*, *K*, *g_F* | fleet EST | DERIVED | L4-05 | 02 |
| 51 | Groth16 gas 181,000 + 6,150·n_pub + calldata = 252,794 vs 256,038 MEASURED (1.3 %) | *k*, *n_pub* | SR-T | DERIVED / MEASURED | L5-0x ⟦R6⟧ | ZK |
| 52 | storage 22,100 gas/word (707,200 / kB) vs log ≈ 9,317 / kB | *L* | EIP-2929 | STANDARD / DERIVED | L2-04, L4-05 | 06 |
| 53 | replay cache ≥ 10·P·1.1; default holds 5,958 senders (docstring 650 → 596) | *C_rc*, *P* | — | DERIVED | L7-03 | 05 |
| 54 | state staleness ≤ k_f−1 msgs (MEASURED); time only with r_s or TTL; t_eff fit, knee 91 | *k_f*, *r_s*, *T_ttl* | — | MEASURED / DERIVED | L2-05, L6-04, L7-03 | 05, 09 |
| 55 | optimal k_f* = ⌊r_s·σ_max⌋+1 (11 / 26 / 101) | σ_max, *r_s* | deterministic rate | DERIVED | L6-04 | 05 |
| 56 | freshness term table: what each component bounds | — | — | DERIVED | L6-04 | 05 |
| 57 | time-to-confirm metric (+57a availability) | Δ, *t_rc*, *N_v*, *A_L* | — | DESIGN / DERIVED | L3-02 | R8 |
| 58 | trilemma coordinates (T, L, C) | PF-16/57/49 | — | DERIVED | — | R8 |
| 59 | protocol-security triple (class, loss, bits) | ε_i | — | DERIVED | — | R8 |
| 60 | decentralisation: NC = f_B+1, PF-16, HHI, Shannon, governance score | *s_c*, *N_v* | — | DERIVED | L3-01, L4-04 | R8 |
| 61 | SC security vector (access, replay, kill rate, attacks, audit) | repo tests | — | MEASURED partial | L5-01..05 | R8 |
| 62 | privacy: k_A, ℓ, hiding bits | *m*, ρ, *P_keep* | — | MEASURED / DERIVED | L6-05, L0-04 | R8 |

(PF-45 and PF-46 are reserved: PF-45 for the 1609.2 verify-on-demand policy model and PF-46 for PC5 congestion-control (CBR→transmit-parameter) dynamics, both deferred to v0-2 per Q-R7-04; PF-44 currently carries the PC5 and reselection rows.)

---

## 10. HANDOFF

**Files.** `docs/roots/phase2/70_R7_theory_ece_bounds/claude_CVIN_SC_Roots_Theory_ECE_Bounds_R7_v0-1.md` (this); `docs/roots/phase2/70_R7_theory_ece_bounds/r7_calc.py` (prints every number; seed 42).

**Tags assigned.** SYM-25–SYM-58; SR-L–SR-T; PF-32–PF-62 (PF-45, PF-46 reserved); PAR-01–PAR-26; Q-R7-01–08; KD-R4-01–09. Consumed: R4 SYM/PF/SR, R3 BP-, SOL-01–09; R6 tags as ⟦⟧.

**Five load-bearing decisions.**
1. Hardhat automine is formalised as *N_v* = 1 with no Δ (PF-39): repo latency is client+RPC only; gas is portable and drives every capacity number.
2. Composition lemma PF-36: binding ≤ Σ ε; the ledger-equivocation term dominates the cryptographic ones by ≈ 37 orders at *N_v* = 4.
3. On the Tier-1 path, OBU verification throughput (PF-43) and airtime (PF-44) bind before the ledger; HAA-1's *k_f* = ∞ moves the bottleneck to silicon.
4. Freshness is a message count unless a TTL exists (PF-54); the optimum *k_f* is set by σ_max (PF-55).
5. Revocation latency under intermittent backhaul must be quoted as tail quantiles (PF-48).

**Open questions.** Q-R7-01 Besu genesis (Δ, *G*, *t_rc*) for any DESIGN row; Q-R7-02 HSM/ECU *t_ver* measurements (PAR-07); Q-R7-03 run E-F1-1 for IDTX gas; Q-R7-04 add SPS reselection and 802.11p airtime to `cv2x_stack.py`; Q-R7-05 RSU propagation delay in I3; Q-R7-06 `freshness.py` docstring 650 vs 596; Q-R7-07 add a TTL to the provider; Q-R7-08 tabulate PF-61(a),(e).

**KD-R4 corrections (repo contradicts Phase 1).**
- KD-R4-01: *G* default 30 M/100 M → measured **60,000,000** (`meta.json`).
- KD-R4-02: Δ = 2 s "sandbox default" has no source; executed chain has no Δ; R4 PF-24/25/28 Option A rows are DESIGN.
- KD-R4-03: *g_op* 50k–180k ESTIMATED → measured ERC-1056 32,868–76,830; other standards to 1,757,881 (§5.1).
- KD-R4-04: fleet "two orders above any row" → 90.3× at 60 M/Δ = 2 s for anchoring; did:ethr creation 0 gas (#47).
- KD-R4-05: PF-11 *p_s*^*t_s* = 10⁻⁶ → repo setup single-party, P = *p_s* (#57).
- KD-R4-06: σ ESTIMATED 5 s → repo bounds staleness in messages (*k_f* − 1), not time.
- KD-R4-07: R4 §3 SOL-01 "finality ≈ Δ" → finality ≡ 0, no Δ (automine).
- KD-R4-08: PF-31 RPC read O(10–200 ms) → measured 15.513 ms uncached local (#21), 91.113 ms at history 50 (#31), probe 3.2 ms (#37): consistent at localhost, but history-dependent.
- KD-R4-09: R4 PF-16/PF-19/PF-02/PF-04 re-computed: all reproduce.
