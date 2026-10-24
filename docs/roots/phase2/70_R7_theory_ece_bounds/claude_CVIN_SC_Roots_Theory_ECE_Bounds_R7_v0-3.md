# CVIN-SC · R7 — Theory and ECE Bounds for the Full Identity Stack

**This document sets the quantitative floor under the Phase 2 atlas. It covers five things: the security reductions the identity stack rests on, stated as games or cited theorems; the distributed-computing conditions under which the ledger terms of W exist at all; the hardware, radio and clock bounds below L0 that decide whether the ledger is ever the bottleneck; the repository's measured gas converted into capacity; and the metric definitions that R8 cites as measurement dimensions.**

| Field | Value |
|---|---|
| Document | R7 of the Roots suite, Phase 2 (thread G-R1) |
| Version | **v0-3** (consistency sweep; applies R9 v0-2 PN-34, PN-37, PN-38). v0-1, v0-2, `r7_calc.py` and `r7_calc_v0-2.py` are kept unchanged beside it. |
| Date | 2026-10-24 |
| Re-keying | **re-keyed per R9 §3.1** (Q-R7-nn kept; KD-R4-nn → KD-R7-nn; KD-R4-08/09 → CEV-R7-01/02; PAR → R8 numbers; script labels → document PF numbering). Phase 1 erratum pointer: R9 §3.4 X-1..X-9. |
| Consumes | R4 v0.1 (SYM-01..24, PF-01..31, SR-A..K, frozen); R3 v0.1 (BP- tags); Phase 1 README (SOL-01..09); `PHASE2_SHARED_BRIEF.md` v1.0; R6 v0-1 (HW-, ALG-, IMP-, SCF-, BP-LH/Lx.y, SOL-10..17); R8 v0-1/v0-2 (MD-, PAR-); R9 v0-1 (PN-, SLD-, DRP-, NC-, CA-); claim register `docs/MEASUREMENT_CONDITIONS.md` (rows written #n); `docs/LATENCY_BUDGET.md`; `cv2x-testbed/identity/freshness.py`, `erc1056_provider.py`; `cv2x-testbed/protocols/cv2x_stack.py`; `5_zkp-agent-identity/`; `docs/testing/GAS_CHARTER.md`; `1_blockchain-identity/results/metrics/latest/` |
| Assigns | `SYM-25`–`SYM-58`, `SR-L`–`SR-T`, `PF-32`–`PF-66` (PF-45, PF-46 filled in v0-2; PF-63..66 added at R8/R9 request), `Q-R7-01`–`Q-R7-08`, `KD-R7-01..06` issued; `KD-R7-07` retired by merge, `CEV-R7-01`–`02`, `LIM-R7-01`–`08`. **PAR- is no longer assigned here**: R8 owns it (R7's 26 parameters map onto R8 PAR-02..26 and PAR-31..43; §8). |
| Status scale (suite-wide, PN-32) | **M** MEASURED (register row or result file) · **Dv** DERIVED (equation + inputs) · **I** IMPLEMENTED-UNMEASURED · **Ds** DESIGN (specified, not built) · **E** ESTIMATED · **S** STANDARD (cited specification or theorem) · **—** not used. A status is never upgraded. |
| Reproducibility | Every number below is printed, with its equation and inputs, by `r7_calc_v0-3.py` in this folder (python3, numpy, scipy; seeds 42 and 2026). Print labels are this document's PF numbers, one to one. The script ends with a self-check that reads this file and fails (exit 1) if any PF tag printed here is absent from its output, or if any R7-owned label it prints is absent here. |

Progress ▓▓▓▓▓▓▓▓▓▓ 95 % (v0-3: R9 v0-2 PN-34/37/38 applied; PF-43 lead re-based on register #26 as re-stated 2026-10-23; EIP-7623 floor condition stated. Open items are primary-source checks logged as LIM-R7-nn, the LIM-R7-08 receipt (CA-20) and the blind re-derivation of PF-36, SLD-10.)

**How to read.** §0 lists what changed since v0-1 and why. §1 extends the notation. §2 (cryptography) and §3 (distributed computing) are the *theory* half: what the identity binding is as strong as, and when the ledger's terms of W are defined at all. §4 (hardware, radio, clocks) and §5 (EVM) are the *engineering* half: where the real bottlenecks are. §6 formalises freshness. §7 gives R8 one formula per measurement dimension. §8 maps R7's parameters onto R8's PAR numbers. §9 indexes every PF with a one-line "So what". §10 records the repository-vs-Phase-1 corrections, §11 the citation limits, §12 the dispositions of R9's findings and §13 the change log. §14 is the HANDOFF. **Read PF-39 (§3.4) before quoting any latency number measured in this repository.**

**What a thesis reader should take away from the whole document, in four sentences.** (1) Everything on chain was executed on a single automining Hardhat process. Gas therefore transfers to any EVM network, but no latency number is a time-to-confirm (PF-39). (2) On the vehicle's safety-message path, verification hardware and channel airtime bind long before the ledger does. The repository's JSON messages are 2.9–5.0× too large for the channel (PF-43, PF-44). (3) Freshness in this repository is bounded in messages, not seconds, until a TTL is added (PF-54). (4) Identity binding is only as strong as its weakest link. Today that link is ledger governance, not cryptography (PF-36, PF-65).

---

## 0a. Change log v0-2 → v0-3 (consistency sweep; R9 v0-2 §2)

| # | Change | Where | PN |
|---|---|---|---|
| V3-01 | PF-43 lead *P*\*(0.5) 305 → **320** (= ⌊50/0.156⌋; #26 re-stated 2026-10-23); *P*\*(1) 610 → **641**; 352 stays the crypto-only ceiling (#27); the CA-09 "internal inconsistency" sentence deleted (CA-09 closed by the repository) | §4.2 text and table, §9 row 43, §14 | PN-34 |
| V3-02 | `r7_calc_v0-3.py`: #26 slope 0.164 → 0.156 (prints 320.5 / 641.0), CA-09 note removed, EIP-7623 floor condition and `setAttribute` first/later-write thresholds printed; self-check reads v0-3 | script | PN-34, PN-37 |
| V3-03 | EIP-7623 floor-binding condition (*g_exec* < 6·*z* + 24·*n*) and the ERC-1056 `setAttribute` first-write / later-write split | §5.4 | PN-37 |
| V3-04 | KD range written "KD-R7-01..06 issued; KD-R7-07 retired by merge" everywhere | header, §0, §13, §14 | PN-38 |
| V3-05 | Header: version v0-3, date 2026-10-24, progress bar, script name | header | — |

Historical records are left as written: §12 row PN-16 and §13 row 9 record the v0-2 response (305 = 50/0.164), which PN-34 supersedes.

---

## 0. Key changes v0-1 → v0-2

| Item | v0-1 | v0-2 | Why (R9 ref) |
|---|---|---|---|
| Correction keys | KD-R4-01..07 | **KD-R7-01..06 issued; KD-R7-07 retired by merge** (into KD-R7-02) | issuer namespacing (§3.1, PN-31) |
| Confirmation keys | KD-R4-08, KD-R4-09 | **CEV-R7-01, CEV-R7-02** | confirmations, not corrections (PN-20) |
| Parameters | PAR-01..26 (R7-owned) | R8 numbers: PAR-02, 04, 05, 06, 10, 12, 16, 18, 19, 20, 22, 24, 25, 26, 11, and new **PAR-31..43** | R8 owns PAR- (PN-26, Table B) |
| Script labels | working labels (PF-32..52 meant other things) | identical to document PF numbering; header map in the script | PN-10 |
| PF-44 item c (reselection) | inside PF-44, exponential approximation | **PF-45**, exact residual-life computation + seeded MC | PN-12; reserved slot filled |
| PF-46 | reserved | **PC5 packet-loss bracket vs load** | R9 Table A′ (PF-⟦5⟧ P_loss(CBR)) |
| PF-63..66 | — | deterministic test-key entropy; lying-RPC false read; common-mode decentralisation term; governance m-of-n | R8 v0-2 request; R9 Table A′ (PF-⟦2⟧, ⟦4⟧, ⟦12⟧, ⟦14⟧) |
| Gossip "PF-50" (script only) | printed, no document PF | dropped as a PF; fan-out is R8 PAR-37 | PN-10 last clause |
| Placeholders | ⟦ALG-??⟧, ⟦HW-??⟧, ⟦IMP-L3.2-?? Besu⟧, ⟦SCF-ERC1056-??⟧, ⟦BP-LH-??⟧, ⟦R6⟧, ⟦MD-??⟧ | resolved per R9 Table B′ / C′ | §3.3 |
| Unfetched citations | load-bearing, unflagged | **LIM-R7-01..08** | PN-18 |

---

## 1. Notation extension (SYM-25 onward)

*What this means for the level above:* nothing in R4 is redefined, so a thesis chapter can cite R4 and R7 symbols together without a translation table. R4 §0 stays in force (W, σ, *N_v*, *f_B*, Δ, *G*, *g_op*, *B_tier*, the five W terms). Bare `A`, `f` and `N` remain avoided. Availability is *A_L*, a budget fraction is *f_id* (the repo's "*f*" in `LATENCY_BUDGET.md` §1), and a neighbour count is *P*. Parameter cells now cite R8's PAR numbers.

| SYM | Symbol | Name | Units | Standard symbol | Default / where set |
|---|---|---|---|---|---|
| SYM-25 | *H_∞* | min-entropy per raw RNG sample | bits/sample | *H* (NIST SP 800-90B) | device-specific; PAR-34 |
| SYM-26 | *r_RNG* | raw noise-source sample rate | samples/s | — | device-specific |
| SYM-27 | *t_sig* | one signature generation on the signing unit | ms | — | HW class (PAR-33) |
| SYM-28 | *t_ver* | one signature verification (warm, key cached) | ms | — | M 0.142 ms software SSI (#27, register precision); HW class otherwise |
| SYM-29 | *v_max* | verifications per second of one unit | s⁻¹ | — | 1/*t_ver* |
| SYM-30 | *f_id* | identity share of the BSM interval | — | *f* in `LATENCY_BUDGET.md` §1 | 0.5 (repo working point; PAR-24) |
| SYM-31 | *P* | neighbours whose BSMs a verifier must check | count | — | 50–300 scenario (PAR-25) |
| SYM-32 | *r_BSM* | BSM rate per sender | Hz | — | 10 (SAE J2945/1, S) |
| SYM-33 | *ρ_v* | verifier utilisation | — | *ρ* (queueing) | *P*·*r_BSM*·*t_ver* |
| SYM-34 | *φ_v* | fraction of received BSMs verified (verify-on-demand) | — | — | 1 (verify-all) |
| SYM-35 | CBR | channel busy ratio | — | CBR (SAE J2945/1, ETSI TS 102 687) | target ≤ 0.6 (E congestion-control knee) |
| SYM-36 | PRR | packet reception ratio at distance *d* | — | PRR | radio-dependent |
| SYM-37 | *P_keep* | PC5 mode 4 resource-keep probability at reselection | — | *probResourceKeep* (3GPP TS 36.321) | 0–0.8 |
| SYM-38 | *T_air* | channel time of one BSM incl. access gap | µs | — | §4.3 |
| SYM-39 | *L_sec* | 1609.2 security overhead per message | B | — | digest ≈ 86, cert ≈ 162–210 (E; LIM-R7-02) |
| SYM-40 | *a_msg* | message age at the receiver | s | — | — |
| SYM-41 | *ε_t* | absolute receiver clock error (vs UTC) | s | — | GNSS-locked ≈ 10⁻⁷ (E) |
| SYM-42 | *d_clk* | oscillator drift in holdover | ppm | — | 0.5–50 |
| SYM-43 | *T_max,age* / *T_max,fut* | freshness window (past / future) | s | — | 1.0 / 0.1 (`freshness.py`; PAR-38) |
| SYM-44 | *C_rc* | replay-cache capacity | entries | — | 65,536 (`freshness.py`; PAR-40) |
| SYM-45 | RTT | network round-trip time on the read path | ms | — | localhost ≈ 1–2 ms (#39); WAN PAR-26 |
| SYM-46 | *F_g* | gossip fan-out | peers | fan-out | PAR-37 |
| SYM-47 | *t_rc* | QBFT base round-change timeout | s | *requestTimeoutSeconds* (Besu, IMP-L3.2-01) | Ds; PAR-31 |
| SYM-48 | *g_F* | measured gas of IMinimalSSI / IDTX function *F* | gas | — | register #29/#34/#50/#54 (authority); run `2026-10-23T00-49-12Z_1f4ace0` (provenance) |
| SYM-49 | *G_HH* | Hardhat block gas limit of record (*instrument* value) | gas | `blockGasLimit` | **60,000,000** M (`meta.json` → network.blockGasLimit; equals Hardhat's development default) |
| SYM-50 | *π* | Groth16 proof size (calldata) | B | — | 256 B M (#57) |
| SYM-51 | *t_prove* / *t_vzk* | proving / off-chain verifying time | ms | — | 398.6 / 18.42 median M (#57) |
| SYM-52 | *g_vzk* | on-chain Groth16 verification gas | gas | — | 256,038 view estimate; 301,163 gated tx M (#58) |
| SYM-53 | *n_C* | circuit constraint count | count | R1CS size | 3,498 M (#56) |
| SYM-54 | *k_f* | state re-check period in messages | messages | — | `ERC1056Provider.set_refresh_every`; PAR-19. Distinct from SYM-01 *k*. |
| SYM-55 | *t_local*, *t_chain* | cached-path verify; added cost of one refresh | ms | — | 0.346 / 13.94 ms (#32, A3b re-run) |
| SYM-56 | *A_L* | link availability of RSU backhaul | — | *A* (renewal theory) | PAR-39 |
| SYM-57 | *μ_on*, *μ_off* | mean up / down sojourn of the backhaul | s | — | PAR-39 |
| SYM-58 | *W_0* | W excluding backhaul outage | s | — | R4 PF-28 illustrative 8.5 s (Ds) |

**Standard results added (SR-L onward; cited, not re-proved; bibliographic details unverified in this pass, LIM-R7-01).**

| ID | Result | Statement | Source |
|---|---|---|---|
| SR-L | ECDSA in the GGM | ECDSA is EUF-CMA if the group is generic and the conversion and hash satisfy stated properties; advantage ≲ *q*²/*n_G* for *q* group operations | Brown (GGM); Fersch–Kiltz–Poettering |
| SR-M | Keccak as ROM | sponge indifferentiable from a RO up to ≈ 2^(*c*/2) queries; keccak-256 *c* = 512 → 2^256 generic bound; collision 2^128 by SR-A | Bertoni et al. |
| SR-N | Groth16 knowledge soundness | knowledge-sound in the generic bilinear group / AGM under q-DLOG; *requires* the CRS trapdoor be unknown | Groth; Fuchsbauer–Kiltz–Loss |
| SR-O | Pedersen commitment | perfectly hiding; computationally binding under DLOG | Pedersen |
| SR-P | QBFT/IBFT | safety for *N_v* ≥ 3*f_B*+1 under asynchrony; liveness under partial synchrony with round change | Moniz; Saltini–Hyland-Wood |
| SR-Q | DLS partial synchrony | consensus solvable once delays are bounded after an unknown GST | Dwork–Lynch–Stockmeyer |
| SR-R | CAP / PACELC | under partition choose C or A; else trade latency vs consistency | Gilbert–Lynch; Abadi |
| SR-S | Renewal-reward / residual life | stationary alternating renewal: P(down) = *μ_off*/(*μ_on*+*μ_off*); mean residual down-time E[*X*²]/(2E[*X*]) | standard (Ross) |
| SR-T | EIP-1108 gas schedule | BN254 ecAdd 150, ecMul 6,000, pairing 45,000 + 34,000·*k* | EIP-1108 |

---

## 2. Security reductions, stated properly

*What this means for the level above.* A thesis reader should conclude that "the message came from the vehicle whose DID it names" is a **conditional** statement. It holds only if the signature, the hash, the ledger and the resolver all behave as assumed. Under current assumptions the weakest link is the ledger's governance, not the cryptography. A system designer should spend effort on validator independence and resolver integrity before touching curve choice. *What this level trusts from below:* that the primitives' idealised models (GGM, ROM, AGM) are adequate, and that keys are generated with enough entropy (PF-41, PF-63). This section gives R8 an assumption class and a tightness for each functionality in place of the word "secure".

### 2.1 PF-32 · ECDSA secp256k1 / P-256 unforgeability

**Game EUF-CMA.** The challenger draws (*sk*, *pk*). The adversary 𝒜 gets *pk* and a signing oracle, and wins with a valid (*m*\*, *σ*\*) for an *m*\* it never queried. **Statement (S, SR-L):** in the generic group model, Adv^EUF-CMA_ECDSA(𝒜) ≤ O(*q*²/*n_G*) + Adv_H, with *n_G* ≈ 2^256. At *q* = 2^64 this gives 2⁻¹²⁸; at 2^80, 2⁻⁹⁶; at 2^100, 2⁻⁵⁶.

Caveats that matter to this programme:
1. *The GGM is not a real-curve proof.* No standard-model reduction of ECDSA to ECDLP exists. The bound is heuristic evidence (S with stated idealisation).
2. *Malleability.* (*r*, −*s* mod *n*) is a second valid signature. The repository's replay cache keys on SHA-256 of the *signed bytes*, not on the signature (`freshness.py` docstring §3), and that is the defence. EVM `ecrecover` callers rely on the low-*s* rule (EIP-2), which only some contracts enforce (R6 BP-L1.1-02).
3. *Nonce.* EUF-CMA assumes uniform nonces. R4 PF-07 and its lattice extension bound the *implementation* failure: a *b*-bit bias needs on the order of 256/*b* signatures (E, order of magnitude). That failure dominates the GGM figure by more than 100 orders of magnitude. ethers signs deterministically (RFC 6979), which closes PF-07 in the harness but not on a vehicle.
4. *Entropy.* Effective security is min(2^128, 2^κ) (R4 PF-06). PF-41 and PF-63 make κ a hardware or code-path quantity.

### 2.2 PF-33 · Keccak-256 collision resistance and low-entropy preimages

**Statement (S, SR-M).** Generic collision resistance is 2^128 and second-preimage resistance is 2^256. EVM addresses truncate to 160 bits, which changes the *namespace* bound (R4 PF-02) but not the commitment bound. A commitment that stores the full 256-bit digest (`IdentityCommitments`, `IdtxExecutor.sol`; the ZK-VIN anchor, #58) inherits 2^128 collision security, or 2^85 under BHT (R4 PF-09). The Fiat–Shamir proofs in `5_zkp-agent-identity/zkid` (#59) are ROM proofs.

**Low-entropy preimages are not covered.** A VIN with only the 6-digit serial unknown has log₂ 10⁶ = 19.93 bits of min-entropy. Its unsalted hash falls to enumeration in 3.58 s (M #60: 10⁶ / 279,587 hashes/s). This is a hiding failure, not a collision failure, and it is why PF-34 exists.

### 2.3 PF-34 · Commitments: binding and hiding

- **Hash commitment** *C* = H(*x* ‖ *s*). Binding ≤ Adv^CR_H ≈ 2⁻¹²⁸. Hiding holds in the ROM iff *s* has ≥ λ bits of min-entropy. With *s* empty, hiding equals the min-entropy of *x* (19.93 bits for the VIN serial). Dv.
- **Pedersen** *C* = *g*^*x* *h*^*s* (#59). Perfectly hiding; binding under DLOG (SR-O). If anyone knows log_g *h*, binding is void. That is a setup assumption of the same type as Groth16's (PF-35).

### 2.4 PF-35 · Groth16 knowledge soundness and the setup assumption

**Statement (S, SR-N).** For the ZK-VIN circuit (*n_C* = 3,498 constraints, 6 public inputs and 1 public output; #56), Groth16 over BN254 is knowledge-sound in the AGM under q-DLOG, given an honestly generated CRS. Concrete security is capped by the curve at roughly 100 bits after TNFS (R4 PF-10; LIM-R7-06). The R1CS is assumed sound. No formal under-constraint audit exists (R6 BP-L1.2-03), and PF-61(e) records that.

**The setup term, with the repository's actual ceremony.** R4 PF-11 bounds a multi-party ceremony by *p_s*^*t_s*. The repository's setup is **single-party and explicitly insecure** (#57). So *t_s* = 1 and P(trapdoor known) = *p_s*: every `ZkVinGate.admit` (SCF-ZKG-03) is sound only if one machine is trusted. → KD-R7-05. Status: M (setup type) + Dv. A leaked trapdoor breaks soundness, not zero-knowledge.

### 2.5 PF-36 · Composition lemma: identity binding as a union bound over failure events

Define **BIND-FAIL**: a verifier *V* accepts *m* as sent by subject DID *D* at time *t*, although *D*'s controller (as fixed by the ledger's final state at *t* − σ) did not sign *m*. The stack consists of signature scheme Σ (PF-32); hash *H* (PF-33); ledger *L* with *non-equivocation* (PF-37, R4 PF-16); and resolver *R* with *integrity*, meaning it returns the document the ledger state implies, at most σ old (R4 PF-15, PF-54).

**Lemma (PF-36).** For any efficient 𝒜,

  P(BIND-FAIL) ≤ ε_Σ + ε_H + ε_L + ε_R + P(revocation inside σ),

which is a **union bound over failure events**. The terms differ in nature, and the reader must not read them as one kind of quantity (PN-19):

| Term | Event | Nature | Worked value |
|---|---|---|---|
| ε_Σ | forgery under EUF-CMA | **computational** advantage (SR-L) | 2⁻¹²⁸ ≈ 2.94×10⁻³⁹ |
| ε_H | hash collision binding *m* or the document | **computational** advantage (SR-M) | 2⁻¹²⁸ |
| ε_L | two honest readers see conflicting final states | **governance prior** (collusion probability, R4 PF-16) — not an adversary advantage | *N_v* = 4, *p_c* = 0.05: 1.40×10⁻² |
| ε_R | resolver returns a wrong document | **implementation prior** (assumed bug/lie rate; PF-64) | 10⁻⁶ (assumed) |
| σ-term | revoked key accepted within σ | **design window** (BP-L6-04) | PF-54 |

*Proof sketch (hybrids).* H₀ is the real experiment. H₁ replaces the resolver output by the document computed from the ledger's final state at *t* − σ; the difference is ε_R. H₂ replaces "the state any reader sees" by "the unique final state"; the difference is ε_L (for QBFT this means two finalised blocks at one height, i.e. more than *f_B* Byzantine validators). H₃ replaces H by an injective map; the difference is ε_H. In H₃ an accepting (*m*, *σ*) not produced by the controller is a forgery, so success ≤ ε_Σ. The reduction embeds the challenge key as *D*'s key and guesses *D* among *n_D* subjects, which costs a factor *n_D*. ∎

**Worked instances (Dv from E inputs).** With *N_v* = 4, the sum is 1.40×10⁻². The ledger term exceeds each cryptographic term by **36.7 orders of magnitude** (1.40×10⁻² vs 2.94×10⁻³⁹). **Executed instance (*N_v* = 1, Hardhat):** ε_L = *p_c* of one operator. At an assumed *p_c* = 0.05 the bound is 5.00×10⁻², i.e. the binding is exactly as strong as trust in the person running the node.

**Tightness.** The multi-user loss is *n_D* = 3.12×10¹³ ≈ 2^44.8. That leaves ≈ 83.2 bits from a 128-bit scheme in the loose worst-case bound. Combined with the ledger term, the concrete bits (PF-59) at *N_v* = 4 are min_i(−log₂ ε_i) − log₂ 4 = **4.16 bits**, which is a ledger-dominated figure and not a cryptographic one.

*Gate (SLD-10):* this lemma does not enter a chapter until a blind re-derivation in a fresh session agrees. The statement to hand that session is the event definition, the five-term bound and the hybrid order above.

---

## 3. Distributed-computing theory

*What this means for the level above.* A thesis reader should conclude that **every consensus, finality and decentralisation number in the programme is Ds**. The repository executed none of them, and the one system it did execute (Hardhat automine) has *N_v* = 1 and no block interval (PF-39). A system designer gets the conditions and costs a QBFT consortium would face (PF-37, PF-38, PF-40). These belong in a design-only appendix (SLD-13), not in results. *What this level trusts from below:* bounded message delay after GST (L0), authenticated channels (L1), and the validator count and independence that governance (L4.2) supplies.

### 3.1 PF-37 · QBFT/IBFT safety and liveness conditions (S / Ds)

With *N_v* validators of which at most *f_B* are Byzantine (SR-E, SR-P, SR-Q):
- *Safety* holds for *N_v* ≥ 3*f_B* + 1 **without any timing assumption**. Two commit quorums of ⌈2*N_v*/3⌉ intersect in ≥ *f_B* + 1 validators, at least one of them honest.
- *Liveness* requires partial synchrony and a round-change timer *t_rc*·2^*r* that eventually exceeds one honest round (R4 PF-17).

| *N_v* | *f_B* | commit quorum ⌈2*N_v*/3⌉ | validators to break safety (*f_B*+1) | validators to halt liveness (*f_B*+1) |
|---|---|---|---|---|
| 4 | 1 | 3 | 2 | 2 |
| 7 | 2 | 5 | 3 | 3 |
| 10 | 3 | 7 | 4 | 4 |
| 13 | 4 | 9 | 5 | 5 |
| 16 | 5 | 11 | 6 | 6 |
| 22 | 7 | 15 | 8 | 8 |

### 3.2 FLP and how each client sidesteps it

| Client / mode | Escape route | Consequence for W | Status in repo |
|---|---|---|---|
| Besu QBFT (IMP-L3.2-01; ALG-20) | partial synchrony: liveness after GST; safety always | *t_finalise* unbounded during asynchrony (PF-40) | Ds |
| Geth Clique (IMP-L3.2-03) | gives up finality (longest chain among signers) | depth choice, like R4 PF-19 | — |
| Ethereum Gasper (Sepolia) | synchrony for LMD-GHOST; FFG finality needs 2/3 stake | ≈ 768 s when live | harness exists; M2 latency not run (NC-07) |
| Bitcoin Nakamoto | probabilistic agreement + synchrony | R4 PF-19 depth | — |
| **Hardhat automine (IMP-L3.2-02; ALG-19)** | **no distributed agreement**: *N_v* = 1 | §3.4 | **the executed chain** |

### 3.3 PF-38 · Message complexity per QBFT round (Dv / Ds)

Per height in the normal case there are three phases: PRE-PREPARE (*N_v* − 1 messages), PREPARE and COMMIT (*N_v*(*N_v* − 1) each). A ROUND-CHANGE adds another *N_v*(*N_v* − 1). The total is *M*(*N_v*) = (*N_v* − 1)(2*N_v* + 1) = Θ(*N_v*²). Message size is 200 B (E) and Δ = 2 s (PAR-05, Ds).

| *N_v* | pre-prepare | prepare | commit | *M* per round | + round change | kB/round | kB/s at Δ = 2 s |
|---|---|---|---|---|---|---|---|
| 4 | 3 | 12 | 12 | 27 | 39 | 5.4 | 2.7 |
| 7 | 6 | 42 | 42 | 90 | 132 | 18.0 | 9.0 |
| 10 | 9 | 90 | 90 | 189 | 279 | 37.8 | 18.9 |
| 13 | 12 | 156 | 156 | 324 | 480 | 64.8 | 32.4 |
| 16 | 15 | 240 | 240 | 495 | 735 | 99.0 | 49.5 |
| 22 | 21 | 462 | 462 | 945 | 1,407 | 189.0 | 94.5 |

Each validator verifies 2*N_v* − 1 signatures per height (43 at *N_v* = 22), which takes under 1 ms at 0.142 ms each. **Consensus messaging is not the bottleneck at consortium sizes.** Capacity (PF-49) and round-change latency (PF-40) are.

### 3.4 PF-39 · Hardhat automine is a degenerate *N_v* = 1 system (critical honesty point)

The run of record states `"automine": true`, `"chainId": 31337`, `"blockGasLimit": 60000000`, `"hardfork": "osaka"` (`1_blockchain-identity/results/metrics/latest/meta.json`, read by the script at run time). Register rule M1 says latency "includes the local JSON-RPC hop only". Formally:
- *N_v* = 1 and *f_B* = 0, so P(safety failure) = *p_c* of one operator. There is no quorum, no gossip and no round change, and *t_finalise* ≡ 0.
- **There is no block interval Δ.** Automine seals one block per transaction. Every R4 expression with Δ = 2 s (PF-24, PF-25, PF-28) is therefore **Ds**. → KD-R7-02.
- The measured latencies are client + RPC + EVM execution. Examples: U3 `setAttribute` median 7.828 ms in-process (M1-H) and 17.2 ms over localhost HTTP (#39). These are **lower bounds on *t_include*** and say nothing about *t_finalise*.
- **Gas is portable.** It is deterministic for identical bytecode and state (`SEPOLIA_VALIDATION.md`; #39 shows HTTP and in-process gas identical). So gas feeds Dv capacity bounds (§5), while latency feeds only the read-path and client-overhead terms. *G_HH* = 60 M is the instrument's development default, not a design input (PN-14).

*So what (SLD-01):* chapters 3, 5 and 6 carry the sentence "All on-chain results come from Hardhat automine (*N_v* = 1, chain 31337, *G* = 60 M, no block interval); gas is portable, latency is client + RPC + execution only and is not a time-to-confirm."

### 3.5 PF-40 · Time-to-confirm under round changes (Dv / Ds)

Model (Ds): t_include ~ U(0, Δ), commit takes Δ, and each round with a down proposer adds *t_rc*·2^*r*. With round-robin selection (PAR-32) and *c* adjacent crashed proposers, the extra delay is *t_rc*(2^*c* − 1). Exact averages are taken over the starting proposer (Δ = 2 s, PAR-05; *t_rc* = 10 s, PAR-31):

| *N_v* | crashed (adjacent) | E[t_conf] | worst case 2Δ + max extra |
|---|---|---|---|
| 4 | 1 | 5.50 s | 14 s |
| 7 | 1 | 4.43 s | 14 s |
| 7 | 2 | 8.71 s | 34 s |
| 10 | 3 | 14.00 s | 74 s |
| 22 | 7 (= *f_B*) | 115.27 s | 1,274 s |

Fault-free, E = 1.5Δ = 3 s and the maximum is 4 s (R4 PF-25 recovered). With independent failures (probability φ < ½ per round), E[extra] = *t_rc*·φ/(1 − 2φ): 5.0 s at φ = 0.25 and 2.0 s at φ = 1/7. A Monte Carlo at φ = 0.25 (seed 42) gives p99 ≈ 73 s and p99.9 ≈ 312 s. **The tail is the design quantity.** It grows as *t_rc*·2^*f_B*, so larger consortia have longer liveness tails. For comparison, Bitcoin *z* = 6 / 11 confirmations average 1.00 / 1.83 h (p99 2.18 / 3.36 h), and Gasper finality is 768 s.

### 3.6 CAP / PACELC placement of SOL-01..09

| SOL | Under partition | Else | Note |
|---|---|---|---|
| 01 sandbox (Hardhat) | n/a (partition = total unavailability) | L | degenerate, PF-39 |
| 02 Option A (QBFT) | **C** (halts below quorum) | C | Ds |
| 03 public anchoring | C for the anchor | L | detection only, R4 PF-13 |
| 04 Option B rollup | A (soft) / C at settlement | L | Ds |
| 04 Option C L1 PoW | A (forks continue) | L | R4 PF-19 |
| 05 HAA-1 | write C; **read A** (cached, bounded by σ) | read L, write C | the split that makes Tier 1 feasible |
| 06 IMinimalSSI | inherits | inherits | interface |
| 07 LFDT (Indy RBFT) | C | C | Ds |
| 08 Family F | per component | per component | Ds |
| 09 SL / AC | A at the verifier | L | σ / witness freshness |

The programme's safety-critical path is **PA/EL by design** (cached reads at the verifier), sitting on a **PC/EC** write plane. PF-54 bounds the cost of that availability choice as σ.

---

## 4. ECE, hardware and wireless bounds

*What this means for the level above.* A thesis reader should conclude that the repository's V2V feasibility result (#27, 0.142 ms on a Xeon) is a *software-on-server* fact, not a vehicle fact. Under automotive-class hardware and a 10 MHz channel, **OBU verification throughput and airtime bind long before the ledger does** (SLD-03, SLD-04, NC-05, NC-10). A system designer should size the HSM and the message encoding before arguing about the ledger. *What this level trusts from below:* physics, silicon and the radio standards. Hardware timings are E classes (PAR-33) unless a register row is cited.

### 4.1 PF-41, PF-42 · Hardware RNG preconditions (one table; DRP-07)

These are E illustrations. They support one ch6 sentence ("no key generation before the DRBG reports full seeding") and are not results.

| Quantity | Formula | Values |
|---|---|---|
| PF-41 shared-key pairs in fleet | *n*²/2^(κ+1); P(any) = 1 − exp(−*n*(*n*−1)/2^(κ+1)) | κ = 48: ≈ 4.0×10³ pairs among 1.5×10⁹ devices (1.8×10⁻³ among 10⁶); κ = 40: 1.0×10⁶ / 0.45; κ = 32: 2.6×10⁸ / 116; κ = 128 over *n* = 3.12×10¹³ keys: 1.43×10⁻¹² |
| PF-42 RCT cut-off (SP 800-90B, S) | *C* = 1 + ⌈20/*H_∞*⌉ at α = 2⁻²⁰ | 21 / 41 / 201 at *H_∞* = 1.0 / 0.5 / 0.1 |
| PF-42 seeding time | 320/(*r_RNG*·*H_∞*) | 0.64 ms (10⁶/s, 0.5); 64 ms (10⁴/s, 0.5); 4 s (100/s, 0.8) |

Embedded devices that shared keys because of boot-time entropy starvation are documented in the literature (Heninger et al., "Mining your Ps and Qs"; LIM-R7-05). The bound sits on BP-LH-01.

### 4.2 PF-43 · Verification load: when verification, not the ledger, is the bottleneck

Load is λ = *P*·*r_BSM* verifications/s, and utilisation is *ρ_v* = λ·*t_ver*. The budget-feasible neighbour count is *P*\*(*f_id*) = ⌊*f_id*·(1/*r_BSM*)/*t_ver*⌋ (`LATENCY_BUDGET.md` §2). M/D/1 mean wait is *W_q* = *ρ_v t_ver*/(2(1 − *ρ_v*)) (S).

**Lead figure (M model, PN-16, PN-34): *P*\*(0.5) = 320** from the register's measured linear model (#26, re-stated 2026-10-23 from the A3b Exp. D re-run at `0b39570`: 0.156 ms per neighbour, R² 1.0000). Arithmetic: *P*\*(0.5) = ⌊50 ms / 0.156 ms⌋ = ⌊320.5⌋ = **320**; *P*\*(1) = ⌊100 / 0.156⌋ = ⌊641.0⌋ = **641**, the register's *P*\* ≈ 641, a linear extrapolation beyond the tested *P* ≤ 80 (DRP-03). The table's software rows are the crypto-only ceiling at register precision.

| Verifier class | *t_ver* | *v_max* | *P*\*(0.5) | *ρ_v* at *P* = 50 / 100 / 200 / 300 | Status |
|---|---|---|---|---|---|
| Software SSI warm, Xeon 2.10 GHz | 0.142 ms | 7,042 /s | 352 (crypto-only ceiling; 320 by #26 model) | 0.07 / 0.14 / 0.28 / 0.43 | M (#27) |
| Software PKI warm, same run | 0.090 ms | 11,111 /s | 555 | 0.04 / 0.09 / 0.18 / 0.27 | M (#27) |
| V2X security ASIC / HSM class | 0.25 ms | 4,000 /s | 200 | 0.12 / 0.25 / 0.50 / 0.75 | E (LIM-R7-03) |
| Automotive app processor, software (Cortex-A53 class) | 1.0 ms | 1,000 /s | 50 | 0.50 / **1.00** / 2.00 / 3.00 | E |
| Automotive MCU HSM (EVITA-full class) | 5.0 ms | 200 /s | 10 | **2.50** / 5.00 / 10.00 / 15.00 | E |

At *ρ_v* ≥ 1 the queue is unstable. For the ASIC class, M/D/1 sojourn is 0.292 / 0.375 / 0.625 ms at *P* = 100 / 200 / 300, well inside the 100 ms Tier-1 budget.

**Verify-on-demand (E, deployment practice; no normative clause cited, LIM-R7-04; PN-18).** When *ρ_v* > *f_id*, a receiver verifies only *φ_v* = min(1, *f_id*/*ρ_v*) of BSMs: 0.250 / 0.167 at 1 ms (*P* = 200 / 300) and 0.050 / 0.033 at 5 ms. *φ_v* < 1 is a security parameter (unverified BSMs feed only non-actuating logic) and belongs in R8's tier-fit dimension (MD-13).

**When is the ledger not the bottleneck? Two criteria (PN-11 corrected).**
- *Refresh-load criterion.* Refreshes alone must use at most the identity budget. The refresh load per verifier-second is (*r_BSM P*/*k_f*)·*t_chain*, and requiring ≤ *f_id* gives **k_f ≥ r_BSM·P·t_chain / f_id**. At *P* = 100 that is ≥ **27.9**; at *P* = 300, ≥ 83.6 (*t_chain* = 13.94 ms, *f_id* = 0.5). v0-1 printed *r_BSM P t_chain*/(*f_id*/*r_BSM*), which carries an extra factor *r_BSM* (s⁻¹) and gives 278.8 at *P* = 100. That is dimensionally wrong.
- *Total-budget criterion (the register's knee).* The whole amortised per-message cost must fit the per-message share of the budget: *t_local* + *t_chain*/*k_f* ≤ *f_id*/(*r_BSM P*), i.e. *k_f* ≥ *t_chain*/(*f_id*/(*r_BSM P*) − *t_local*). At *P* = 100 the share is 0.500 ms, so *k_f* ≥ **91**, which is #32's measured knee "*k* ≈ 90". At *P* = 300 the share (0.167 ms) is below *t_local* (0.346 ms), so no *k_f* suffices: the cached path itself is over budget on this host.
- *When each applies.* The first criterion asks whether the *ledger* is the bottleneck, i.e. whether refreshes alone exceed the budget. The second asks whether the *whole identity path* fits. The thesis cites the second for #32 and the first for the sentence "the ledger is not the bottleneck". Under HAA-1 (*k_f* → ∞) both reduce to *t_local* ≤ *f_id*/(*r_BSM P*), a pure verification-hardware condition.

Ledger reads per verifier are 10·*P*/*k_f* per second: 1,000 / 3,000 at *k_f* = 1 (*P* = 100 / 300), 40 / 120 at 25, and 11.1 / 33.3 at 90. With *k_f* = ∞ an MCU-class HSM saturates at *P* = 20 (*f_id* = 1), an order of magnitude below dense-traffic *P*. Signing duty *r_BSM*·*t_sig* is 0.005 (ASIC) or 0.100 (MCU HSM), so signing one's own BSMs is never the bottleneck.

### 4.3 PF-44 · Channel airtime and how many vehicles fit

**IEEE 802.11p** (10 MHz, 6 Mb/s QPSK ½; S PHY timing). *T_air* = 40 µs + 8 µs × ⌈(16 + 8*L* + 6)/48⌉, plus AIFS(AC_VO) = 58 µs. BSM part I is ≈ 40 B, WSMP 6 B and MAC+LLC+FCS 36 B (all E, LIM-R7-07). *L_sec* is ≈ 86 / 162 / 210 B (E, LIM-R7-02). *N_fit* = 0.6/(*r_BSM*·*T_air*).

| Identity payload | MPDU | *T_air* + AIFS | CBR per vehicle | *N_fit* at CBR 0.6 | Status |
|---|---|---|---|---|---|
| none | 82 B | 218 µs | 0.0022 | 275 | Dv / E sizes |
| 1609.2 digest | 168 B | 330 µs | 0.0033 | 182 | Dv / E |
| 1609.2 implicit cert | 244 B | 434 µs | 0.0043 | 138 | Dv / E |
| 1609.2 explicit cert | 292 B | 498 µs | 0.0050 | 120 | Dv / E |
| digest 4 of 5, cert 1 of 5 | — | 364 µs | 0.0036 | 165 | Dv |
| **repo JSON, ERC-1056** | 632 B | 946 µs | 0.0095 | **63** | size M (#23: 596 B) |
| **repo JSON, PKI (PEM cert)** | 1,146 B | 1,634 µs | 0.0163 | **37** | size M (#23: 1,110 B) |

Security is 34 % of a digest-signed BSM's airtime and 56 % of an explicit-certificate one. **The repository's JSON encoding costs 2.9× (ERC-1056) to 5.0× (PKI) the airtime of a digest-signed 1609.2 BSM.** The encoding is research JSON and is not deployable at density (NC-10). The register row (#23) is a *size* finding; the capacity is its Dv consequence.

**LTE-V2X PC5 mode 4** (S structure, E link budget): 50 PRB, five 10-PRB sub-channels per 1 ms sub-frame, ≈ 190 B per sub-channel (E, LIM-R7-07).

| Payload | *L* | sub-channels | packets/s | vehicles at CBR 0.6 |
|---|---|---|---|---|
| digest | 152 B | 1 | 5,000 | 300 |
| implicit / explicit cert | 228 / 276 B | 2 | 2,000 | 120 |
| repo JSON ERC-1056 | 596 B | 4 | 1,000 | 60 |
| repo JSON PKI | 1,110 B | 6 | — | does not fit one sub-frame at this MCS |

### 4.4 PF-45 · SPS resource reselection and RF-layer pseudonym linkability (filled; split from PF-44)

In sensing-based SPS a vehicle holds its resource for a counter *C* ~ U{5..15} reservations at RRI = 100 ms. At expiry it keeps the resource again with probability *P_keep*. One resource's lifetime is *L* = RRI·(*C*₁ + … + *C_N*), with *N* ~ Geometric(1 − *P_keep*), and E[*L*] = E[*C*]·RRI/(1 − *P_keep*) = 1.00 / 1.67 / 5.00 s.

If a pseudonym changes at a uniformly random instant, the probability that the same resource is still held *x* seconds later is the residual-life survival **E[(*L* − *x*)⁺]/E[*L*]** (SR-S, length-biased sampling). The script computes it exactly by convolving the *C* distribution and cross-checks it with a seeded Monte Carlo (seed 2026, 4×10⁵ draws):

| *P_keep* | E[*L*] | P(same resource 1 s after change) — v0-2 exact | MC | v0-1 exp approx | at *x* = 0.1 / 0.5 / 2 s |
|---|---|---|---|---|---|
| 0.0 | 1.000 s | **0.136** | 0.136 | 0.368 | 0.900 / 0.500 / 0.000 |
| 0.4 | 1.667 s | **0.449** | 0.449 | 0.549 | 0.940 / 0.700 / 0.186 |
| 0.8 | 5.000 s | **0.805** | 0.805 | 0.819 | 0.980 / 0.900 / 0.646 |

At *P_keep* = 0 the exact value is (1+2+3+4+5)/11 × 0.1 = 0.1364. **A pseudonym change that does not also force resource reselection is linkable at L0.1 with probability ≈ 0.14–0.80 one second later, and ≈ 0.90–0.98 one RRI later.** This is an identity-privacy breaking point below every DID mechanism (R6 BP-L0.1-02; SLD-07). `cv2x_stack.py` has no reselection counter, so the testbed cannot measure it yet (Q-R7-04). Status Dv / E.

### 4.5 PF-46 · PC5 packet loss vs load (filled; first-order bracket)

R6's PF-⟦5⟧ asks for P_loss(CBR). Without propagation (so this is an upper bound on PRR), loss at a receiver has two parts. The first is the half-duplex term *P_HD* = 1/100: the receiver transmits in the same sub-frame, with 100 sub-frames per RRI. The second is the collision term, bracketed by two extremes. At the *random-selection* extreme, 1 − (1 − 1/*R*)^(*n*−1). At the *ideal-sensing* extreme only reselecting vehicles collide, choosing among the free resources: 1 − (1 − *p_r*/(*R*(1 − CBR)))^(*n*−1), with *p_r* = 0.1 per RRI at *P_keep* = 0. *R* is the number of resources per RRI. Values are E (inputs) / Dv:

| Payload (*R*) | *n* | CBR | P_loss bracket [ideal sensing, random] |
|---|---|---|---|
| digest (*R* = 500) | 100 | 0.20 | [0.034, 0.190] |
| digest | 200 | 0.40 | [0.074, 0.339] |
| digest | 300 | 0.60 | [0.149, 0.460] |
| certificate (*R* = 200) | 100 | 0.50 | [0.104, 0.401] |
| certificate | ≥ 200 | ≥ 1 | offered load exceeds resources; no bracket |

*Reading.* Even at CBR 0.6 with ideal sensing, roughly 1 in 7 BSMs is lost to a given neighbour from MAC effects alone. A freshness policy that needs *consecutive* messages (*k_f* counting) must budget for that loss. Congestion-control dynamics (CBR → transmit parameters) remain out of scope (Q-R7-04).

### 4.6 PF-47 · GNSS time error, clock holdover and freshness windows

The receiver accepts a message iff −*T_max,fut* ≤ *t_rx* − *t_g* ≤ *T_max,age* (`freshness.py`). Dv conditions:
1. No false rejection requires |ε_r − ε_s| ≤ 0.1 s.
2. Holdover lasts *T_hold* = *T_max,fut*/(2*d_clk*): **27.78 h** at 0.5 ppm, 6.94 h at 2 ppm, 0.69 h at 20 ppm, **0.28 h** at 50 ppm.
3. While locked, ε_t ≈ 100 ns (E) gives a 10⁶× margin. **Holdover in tunnels and urban canyons is the constraint, not GNSS time.**
4. A spoofer shifting the clock by δ_s widens replay acceptance by δ_s. The freshness window therefore inherits GNSS integrity (BP-LH-04; NC-02). It is not cryptographically self-sufficient.
5. A 1.0 s-old BSM misplaces a vehicle by 14 / 30 / 40 m at 14 / 30 / 40 m/s.

### 4.7 PF-53 · Replay-cache sizing

Within *w* = 1.1 s a receiver must hold *r_BSM*·*P*·*w* entries: 550 / 1,100 / 3,300 / 6,600 at *P* = 50 / 100 / 300 / 600. The default *C_rc* = 65,536 holds ⌊65,536/11⌋ = **5,958 senders** without eviction, or **596** with the docstring's margin of ten. The docstring says "about 650", which is wrong (CA-08; Q-R7-06). Dv.

### 4.8 PF-48 · RSU backhaul intermittency and revocation latency (Ds model)

The backhaul is modelled as a stationary alternating renewal process (*μ_on*, *μ_off*, *A_L* = *μ_on*/(*μ_on*+*μ_off*)). A revocation sees the link down with probability 1 − *A_L* and then waits the residual down-time (SR-S):

  W = *W_0* + 𝟙{down}·*R*,  E[W] = *W_0* + (1 − *A_L*)·E[*X*²]/(2E[*X*]).

For exponential down-times the tail is P(W > *W_0* + *x*) = (1 − *A_L*)e^(−*x*/*μ_off*), so the *q*-quantile is *W_0* + *μ_off*·ln((1 − *A_L*)/(1 − *q*)) when 1 − *A_L* > 1 − *q*, and *W_0* otherwise. Mean residual is 0.5 / 1.0 / 2.5·*μ_off* for CV = 0 / 1 / 2. With *W_0* = 8.5 s (R4 PF-28, Ds), a Monte Carlo of 2×10⁶ draws (seed 42) agrees within **1.34 %** on every non-degenerate cell, and so within the "< 3 %" PN-17 asked for. The cell *A_L* = 0.99, *q* = 0.99 sits exactly on the edge of the atom at *W_0*: its empirical p99 (10.4 s) is a sampling artefact of that edge, so it is excluded.

| *μ_off* | *A_L* | E[W] | p99 | p99.9 |
|---|---|---|---|---|
| 10 s | 0.99 | 8.60 s | 8.5 s | 31.5 s |
| 10 s | 0.95 | 9.00 s | 24.6 s | 47.6 s |
| 60 s | 0.95 | 11.50 s | 105.1 s | 243.2 s |
| 60 s | 0.90 | 14.50 s | 146.7 s | 284.8 s |
| 600 s | 0.99 | 14.50 s | 8.5 s | 1,390.1 s |
| 600 s | 0.95 | 38.50 s | 974.2 s | 2,355.7 s |
| 600 s | 0.90 | 68.50 s | 1,390.1 s | 2,771.6 s |

**Revocation-latency guarantees must be stated as tail quantiles of the down-time distribution, not as availability percentages.** At 99 % availability with 10-minute outages, the mean is 14.5 s but p99.9 is 23 minutes. A poll-based RSU (period *T_p*) adds 0.5 / 5 / 30 s on average and 1 / 10 / 60 s at most for *T_p* = 1 / 10 / 60 s. The repo's RSU rows (#46) bound staleness in messages, with no propagation model (Q-R7-05).

---

## 5. Smart-contract and EVM quantification

*What this means for the level above.* A thesis reader should conclude that **cost is a per-function vector, not one number per standard**, and that gas, being MEASURED and portable, is the repository's most transferable result. A system designer should read every ops/s figure as a function of two undecided parameters, *G* (PAR-06) and Δ (PAR-05), both Ds because the executed chain has no Δ. *What this level trusts from below:* the EVM gas schedule (L5.1, S) and the block budget (L4.3). **Provenance (PN-21):** the register rows are the authority (#29, #34, #50, #54, status V). The run `2026-10-23T00-49-12Z_1f4ace0` (current `meta.json`) is provenance. Values checked (U3 35,024; U5 62,646; P1 34,206) are identical across that run and the runs cited by #50 (`7a9a996`), #39 (`a9e2a28`) and #54 (`9bdf451`).

### 5.1 PF-49 · Capacity per function as a function of *G* and Δ

ops/block = ⌊*G*/*g_F*⌋ and ops/s = *G*/(*g_F*·Δ). At the instrument's *G_HH* = 60 M:

| Function (ERC-1056 pure unless stated) | *g_F* | Source | ops/block | ops/s Δ=1 | Δ=2 | Δ=5 | Δ=12 |
|---|---|---|---|---|---|---|---|
| C1 create identity (SCF-EDR, with VIN binding) | 76,830 | #29/#34 | 780 | 781 | 390 | 156 | 65 |
| U1 `changeOwner` (SCF-EDR-03) | 51,754 | crud_gas | 1,159 | 1,159 | 580 | 232 | 97 |
| U2 `addDelegate` (SCF-EDR-05) | 55,143 | crud_gas | 1,088 | 1,088 | 544 | 218 | 91 |
| U3 `setAttribute` (SCF-EDR-09) | 35,024 | #29 | 1,713 | 1,713 | 857 | 343 | 143 |
| U5 `setAttributeSigned` (SCF-EDR-10) | 62,646 | #50 | 957 | 958 | 479 | 192 | 80 |
| D1 `revokeDelegate` (SCF-EDR-07) | 32,868 | crud_gas | 1,825 | 1,825 | 913 | 365 | 152 |
| D2 `revokeAttribute` (SCF-EDR-11) | 34,576 | crud_gas | 1,735 | 1,735 | 868 | 347 | 145 |
| V3 anchor status | 33,918 | crud_gas | 1,768 | 1,769 | 884 | 354 | 147 |
| V5 revoke credential | 33,470 | #29 | 1,792 | 1,793 | 896 | 359 | 149 |
| P1 create presentation | 34,206 | #54 | 1,754 | 1,754 | 877 | 351 | 146 |
| RSU anchors key | 52,606 | #47 | 1,140 | 1,141 | 570 | 228 | 95 |
| pseudonym `addDelegate`, steady | 54,807 | #38 | 1,094 | 1,095 | 547 | 219 | 91 |
| CVIN-Combined C1 | 271,402 | #34 | 221 | 221 | 111 | 44 | 18 |
| ERC-4337 U5 (UserOp) | 141,767 | #34 | 423 | 423 | 212 | 85 | 35 |
| MOBI `attestEvent` (SCF-MOBI2-04) | 198,694 | #28 | 301 | 302 | 151 | 60 | 25 |
| `ZkVinGate.admit` (SCF-ZKG-03) | 301,163 | #58 | 199 | 199 | 100 | 40 | 17 |
| ERC-735 C1 | 1,757,881 | #34 | 34 | 34 | 17 | 7 | 3 |

**Capacity across *G* (PN-14; Δ = 2 s, both PAR):**

| *G* | meaning | C1 ops/s | U3 | V5 | admit |
|---|---|---|---|---|---|
| 30 M | R4 design scenario | 195 | 428 | 448 | 50 |
| 60 M | Hardhat instrument value (M as config, not a design input) | 390 | 857 | 896 | 100 |
| 100 M | R4 design scenario | 651 | 1,428 | 1,494 | 166 |

The measured ERC-1056 functions span 32,868–76,830 gas, which is *below* R4's assumed 50k–180k band. CVIN-Combined, ERC-4337, ERC-735 and the ZK gate sit inside or far above it (KD-R7-03). The IDTX functions (SCF-IDTX-02/03/04) have **no measured gas** (status **I**). E-F1-1 predicts +5,700–7,000 over the action but has not been run, so IDTX is omitted (Q-R7-03; DRP-05).

### 5.2 PF-50 · Fleet anchoring under measured gas — an upper bound on an excluded design

**Privacy exclusion first (PN-15).** PF-50 is an upper bound on a design excluded on privacy grounds. On-chain per-pseudonym delegates are fully linkable (#38: 60/60 by one `eth_getLogs`; BP-L7.2-01; NC-03). A 1609.2-style off-chain pseudonym scheme anchors nothing per pseudonym. Keep the number only as the argument that **on-chain pseudonyms fail twice, on privacy before capacity** (DRP-02).

R4 PF-24's fleet of 3.12×10¹³ identifiers over 20 years is 4.943×10⁴ operations/s. A did:ethr identity costs **0 gas** to create (#47). Anchoring pseudonyms by `addDelegate` (54,807 gas, #38) demands 2.71×10⁹ gas/s:

| *G* (PAR-06), Δ = 2 s (PAR-05) | fleet ratio |
|---|---|
| 30 M | 180.6× |
| 60 M | **90.3×** (3,901,388 blocks/day needed vs 43,200) |
| 100 M | 54.2× |

With C1 (76,830 gas) instead, the ratio at 60 M is 126.6×. The register's per-vehicle route (1,096,368 gas per 20-pseudonym epoch, #38; 1.5×10⁹ vehicles per week) gives 90.6× at 60 M, so the two routes agree. The correct sentence is "≈ 90× over one chain at *G* = 60 M, Δ = 2 s (both PAR), for a privacy-excluded anchoring design, with creation itself free" → KD-R7-04 (QUALIFIED).

### 5.3 PF-51 · Groth16 on-chain verification: EIP-1108 model vs measured gas

The snarkjs verifier (SCF-G16; ALG-12) performs one 4-pairing check and an MSM over *n_pub* = 7 public signals (#57). By SR-T: pairing 45,000 + 34,000·4 = 181,000; ecMul + ecAdd 6,150·7 = 43,050; calldata ≤ 16 × 484 B = 7,744; plus the 21,000 base, for **252,794 gas** (Dv, upper bound on calldata). The measured view estimate is **256,038** (#58). The residual of **3,244 gas (1.3 %)** is memory expansion, field checks and dispatch. The cost model is therefore 181,000 + 6,150·*n_pub* + calldata, constant in *n_C*. The gated `admit` (301,163) adds 45,125 for gate storage and the event, and one ZK admission costs 3.92× an ERC-1056 C1. **Setup caveat in the same sentence (SLD-09):** the setup is single-party and insecure (#57; BP-L1.2-04; NC-04). Precompile correctness is a client assumption (BP-L1.2-02).

### 5.4 PF-52 · Storage vs event-log cost of a DID document (PN-13 corrected)

Cold zero→non-zero SSTORE costs 20,000 + 2,100 = 22,100 gas per 32-byte word (S). LOG3 costs 375 base + 3 × 375 topics + 8 gas/byte. v0-1 omitted the 375 base. Each byte must also arrive as calldata at 16 gas per non-zero byte (EIP-2028), on both paths.

| Size | storage (execution) | LOG3 (execution) | ratio, execution only | ratio, calldata both sides (EIP-2028 basis) | ratio under EIP-7623 floor |
|---|---|---|---|---|---|
| 1 kB | 707,200 | **9,692** (v0-1: 9,317) | 73.0× | **27.7×** | 17.7× |
| 2 kB | 1,414,400 | **17,884** (v0-1: 17,509) | 79.1× | 28.6× | 17.7× |
| 5 kB | 3,536,000 | **42,460** (v0-1: 42,085) | 83.3× | 29.1× | 17.7× |

*Comparison basis.* The like-for-like figure is the calldata-inclusive one, **≈ 28×** at 1–2 kB (agreeing with R9). There is one further correction that R9 did not make. The executed hardfork is `osaka` (`meta.json`), and from Prague onward EIP-7623 imposes a calldata floor of 10 gas per token, i.e. 40 gas per non-zero byte. A log-only transaction carrying 1 kB then pays the floor (40,960) rather than 16,384 + 9,692 = 26,076, and the ratio falls to ≈ **17.7×**, independent of size. Two caveats: whether Hardhat 2.28.6 applies the floor is not verified against a measured receipt (LIM-R7-08), and the figure excludes the 21,000 base. The thesis should quote "≈ 18–28× depending on the calldata pricing rule (pre-/post-EIP-7623)". The direction of the trade is unchanged.

*When the floor binds (PN-37; Dv from the EIP-7623 text).* EIP-7623 counts tokens = *z* + 4·*n* for *z* zero and *n* non-zero calldata bytes, and charges gas = 21,000 + max(4·tokens + *g_exec*, 10·tokens), where *g_exec* is execution gas (plus contract-creation cost, none here). The floor therefore binds iff 4·tokens + *g_exec* < 10·tokens, that is

  **floor binds ⇔ *g_exec* < 6·tokens = 6·*z* + 24·*n***, i.e. execution gas below 24 gas per non-zero calldata byte (6 per zero byte).

For the bare LOG3 of *B* non-zero bytes, *g_exec* = 1,500 + 8·*B* < 24·*B* ⇔ *B* > 93.75, so the floor binds for every log of ≥ 94 B; that is the domain in which 17.7× is "independent of size". The storage path has *g_exec* ≈ 22,100·⌈*B*/32⌉ ≈ 690·*B* ≫ 24·*B* and never meets the floor.

*ERC-1056 `setAttribute`: first write vs later write (PN-37).* The function writes `changed[identity] = block.number` as well as the log, so its *g_exec* contains one SSTORE whose price depends on history: a **first write** (slot zero → non-zero, cold) costs 20,000 + 2,100 = **22,100**; a **later write** in a new transaction (non-zero → non-zero, cold) costs 2,900 + 2,100 = **5,000** (S: EIP-2929/3529). With *V* non-zero value bytes, a LOG2 of 160 + *V* data bytes (375 + 2 × 375 + 8·(160 + *V*)), and *T_h* tokens for the 164 B of ABI head (164 ≤ *T_h* ≤ 656), the condition *g_exec* < 6·*T_h* + 24·*V* gives, before dispatch and access-check overhead (which only raise the threshold): first write **binds only for *V* ≳ 1,286–1,470 B**; later write **binds for *V* ≳ 217–401 B**. Measured U3 (35,024 gas, #29) is a later write, since a first write's SSTORE alone (22,100) exceeds 35,024 − 21,000; its 288 B log (*V* = 128 B padded) lies below both thresholds, so **the floor does not bind for U3** and its gas is EIP-7623-neutral. A single-function storage-vs-log ratio still needs a measured receipt (RL-02, NC-12, CA-20).

This mechanism explains the measured footprint ranking. ERC-1056 U3 does 1 SSTORE and writes 288 B of log (375 + 2 × 375 + 8 × 288 = 3,429 gas of log), whereas ERC-735 does 13 SSTOREs (#49). It also explains the read-side price: ERC-1056 resolution grows to 112 RPC calls / 87 KB at history 50 (#31). Write cheapness is bought with read cost linear in history, which is the trade R8's trilemma coordinate (PF-58) records.

---

## 6. Freshness and time

*What this means for the level above.* A thesis reader should conclude that the repository bounds **how many messages** a verifier may accept on stale identity state, not **how many seconds**. A sender that goes quiet makes the time bound infinite until a TTL exists (CA-07; NC-02 neighbour). A system designer should set *k_f* from the security budget σ_max, not from cost (PF-55). *What this level trusts from below:* clocks (PF-47), the ledger's finality (§3) and the verifier's cache policy. There are two freshness notions, and they must not be confused (PN-24). **Message freshness** lives in `freshness.py`: the message is ≤ *T_max,age* old and not replayed. **State freshness** lives in `ERC1056Provider.set_refresh_every(k)` and `_probe_identity_info`: cached identity state is ≤ *k_f* − 1 messages old.

### 6.1 PF-54 · State staleness vs read path

- Staleness in messages is ≤ *k_f* − 1 (M exactly, #32: 0 / 4 / 24 at *k_f* = 1 / 5 / 25, 35/35 trials; #46 for RSUs).
- Staleness in time is σ_k = (*k_f* − 1)/*r_s* **only if *r_s* is known and constant**. At *k_f* = 25 it is 2.4 s at 10 Hz, 24 s at 1 Hz and 240 s at 0.1 Hz. → KD-R7-06.
- The amortised cost *t_eff* = *t_local* + *t_chain*/*k_f* (M fit within 1–4 %, #32) is 14.286 / 3.134 / 0.904 / 0.501 / 0.441 ms at *k_f* = 1 / 5 / 25 / 90 / 146, giving *P*\*(0.5) = 3 / 15 / 55 / 99 / 113. The knee ⌈*t_chain*/(0.5 − *t_local*)⌉ = 91 reproduces "*k* ≈ 90". This is the total-budget criterion of PF-43 at *P* = 100.
- Under *k_f* counting, PF-46 losses make *k_f* messages span more wall-clock time than *k_f*/*r_s*.

**Bound (Dv).** Identity-state age ≤ σ_k + *t_include* + *t_finalise* + *t_propagate*, provided σ_k is capped by a TTL. Recommended policy: min(*k_f* messages, *T_ttl* seconds) (PAR-19 + PAR-20), so that σ ≤ min((*k_f* − 1)/*r_s*, *T_ttl*). The provider has no TTL today (CA-07; Q-R7-07).

### 6.2 PF-55 · Optimal re-check period under a staleness budget

Minimise *t_eff*(*k_f*) subject to (*k_f* − 1)/*r_s* ≤ σ_max. Because *t_eff* decreases in *k_f*, **k_f\* = ⌊r_s·σ_max⌋ + 1** (Dv). At 10 Hz: σ_max = 1 s → 11 (1.613 ms, *P*\* = 30); 2.5 s → 26 (0.882 ms, 56); 10 s → 101 (0.484 ms, 103). **The measured knee (*k_f* ≈ 90) corresponds to accepting ≈ 8.9 s of revoked-key messages at 10 Hz** (SLD-05). On average a revocation lets (*k_f* − 1)/2 revoked messages through.

### 6.3 PF-56 · What each repo component bounds

| Term | Bounded by | Repo evidence | Status |
|---|---|---|---|
| message age | *T_max,age* + \|ε_r − ε_s\| | `freshness.py` 1.0 / 0.1 s | M (code) / Dv (PF-47) |
| replay | *C_rc* ≥ *r_BSM*·*P*·*w* | 65,536 → 5,958 senders | Dv (PF-53) |
| state staleness (messages) | *k_f* − 1 | #32, #37, #46, #52 | M |
| state staleness (time) | min((*k_f*−1)/*r_s*, *T_ttl*) | no TTL in the provider | Ds (PF-54) |
| ledger terms | t_include + t_finalise | Hardhat only | Ds (PF-39, PF-40) |
| backhaul | (1 − *A_L*)·residual | none | Ds (PF-48) |

On the executed system the dominant *measured* contributor to W is σ_k.

---

## 7. Measurement-dimension metric definitions (for R8)

*What this means for the level above.* R8's register can judge any functionality on a dimension only if that dimension has a formula whose inputs are register rows or PARs. Each PF below is such a formula. Statuses refer to the inputs as the repo stands. MD bindings follow R9 Table C′.

| PF | MD | Dimension | Formula / metric | Inputs | Status today |
|---|---|---|---|---|---|
| **PF-57** | MD-01 | Time to confirm | E and tail of *t_conf* from PF-40 (BFT), Erlang(*z*, Δ_pub) (PoW), 768 s (Gasper); on Hardhat, client + RPC only | PAR-04, 05, 31, 32; M1-H latency | Ds / M (client) |
| **PF-57a** | MD-10 | Availability | write = P(≥ ⌈2*N_v*/3⌉ up) (0.999408 at *N_v* = 4, unavailability 0.01); read = 1 − P(miss)(1 − *A_L*); revocation tail = PF-48 | PAR-04, 39 | Ds |
| **PF-58** | MD-03 | Trilemma position | (*T*, *L*, *C*) = (−log₁₀ PF-16, log₁₀ E[t_conf], log₁₀ ops/s PF-49); *T* = 1.85 at *N_v* = 4, *p_c* = 0.05 | PF-57, PF-49 | Dv |
| **PF-59** | MD-05 | Protocol security | (assumption class, reduction loss, bits = min_i(−log₂ ε_i) − log₂ terms − log₂ *n_D*) | PF-32..36 | Dv |
| **PF-60** | MD-02 | Decentralisation confidence | *NC* = *f_B* + 1; PF-16 (with PF-65 common-mode term); HHI = Σ*s_c*²; Shannon; governance diversity | PAR-02, 04 | Dv / Ds; today HHI = 1.0, *NC* = 1 |
| **PF-61** | MD-04 | Smart-contract security | (a) access-check coverage; (b) replay-protection coverage (nonce + domain incl. chain id); (c) mutation kill rate; (d) attack-matrix pass; (e) audit status | (c) IDTX 5/5 gate mutants (CI); (d) 43/43 defended, 11 N/A (#28); (b) D52; (a), (e) to tabulate (Q-R7-08) | M for (c), (d) |
| **PF-62** | MD-09 | Privacy | anonymity set *k_A*, linkability ℓ, hiding bits: status list (1 − ρ)*m* (R4 PF-29; 17 bits at 131,072); ℓ_RF from PF-45; chain pool *k_A* = 1 (#38); unsalted VIN 19.93 bits (PF-33, #60) | R4 PF-29, PF-45, #38, #60 | M / Dv |
| **PF-32..35** | MD-06 | Cryptographic strength | per-primitive bits and assumption class | §2 | S |
| **PF-49** | MD-07, MD-11 | Capacity | ops/s = *G*/(*g_F*Δ); fleet ratio (PF-50) | crud_gas; PAR-05, 06 | M gas / Dv |
| **PF-52** | MD-08 | Cost (storage) | storage vs log, stated basis | §5.4 | S / Dv |
| **PF-43** | MD-11, MD-13 | Tier fit | Tier 1: *ρ_v* ≤ *f_id*, cache read, *φ_v* reported; Tier 2: RTT + server ≤ 500 ms; Tier 3: any | PAR-33, 25, 26 | M (sw) / E (hw) |
| **PF-48, 54, 55** | MD-14, MD-15 | Revocation latency / freshness | §4.8, §6 | PAR-19, 20, 39 | Dv / Ds |
| **PF-63..66** | MD-06, MD-09, MD-02, MD-20 | key-derivation entropy; false-read; common-mode; governance | §7.1 | — | Dv |

Rules for R8: cite the PF, not the number; quote gas with its GAS_CHARTER class; never place a Hardhat latency in a time-to-confirm cell (PF-39).

### 7.1 Bounds added at R8/R9 request (PF-63..66)

*What these mean for the level above:* each turns a "the repo does X with one key / one endpoint / one client" observation into a probability that a reader can compare across designs. All four are Dv, with E inputs.

**PF-63 · Effective entropy of deterministic test-key derivation (RV-THR-15; BP-LH-02).** `ERC1056Provider.vehicle_account` sets the controller key to SHA-256(vehicle_id) (marked TEST-ONLY in source). The key's effective entropy against an adversary is **κ = H(vehicle_id | adversary's knowledge)**, not 256 bits. R4 PF-06's min(2^128, 2^κ) collapses to 2^κ. Enumeration time is 2^κ/279,587 SHA-256 per second (one core, #60 rate):

| id space | κ | enumeration |
|---|---|---|
| id known to adversary (it is public: it names the DID / appears in messages) | 0 bits | one hash |
| sequential bench ids `BENCH_<type>_<i>`, 3 types × 1,000 | 11.55 bits | 0.0107 s |
| VIN, serial unknown (#60) | 19.93 bits | 3.58 s |
| VIN, plant + serial unknown (E) | 24.84 bits | 107 s |
| uniform 128-bit id | 128 bits | 1.22×10³³ s |

*So what:* any path that reuses this derivation outside the test chain gives every vehicle a key that anyone can derive (CA-18).

**PF-64 · False or stale state from a lying RPC endpoint (RV-READ-13, RV-THR-13; BP-L0.4-02).** Let *p_lie* be the probability that one endpoint returns false state (E, 10⁻³ illustratively). With one endpoint and no proof (the repository today), P(accept) = *p_lie* = 1.0×10⁻³. With *k*-of-*n* agreement over independent endpoints, P = Binom tail(*n*, *k*, *p_lie*): 2-of-3 gives 3.00×10⁻⁶ and 3-of-5 gives 9.99×10⁻⁹. Independence is the whole benefit: if a fraction ρ = 0.1 of queries share a provider, P ≈ ρ·*p_lie* + (1 − ρ)·tail ≈ 1.0×10⁻⁴ for both. A Merkle-proof-backed read (`eth_getProof` against a trusted header) gives P ≤ Adv^CR_keccak + P(header untrusted) ≈ 2⁻¹²⁸ + *p_hdr*, which moves the trust to header acquisition (Ds; not used). *So what:* fail-closed resolution protects against errors, not lies (NC-06). Only proofs remove the *p_lie* term.

**PF-65 · Common-mode term for decentralisation confidence (MD-02; BP-L3.2-01).** This extends R4 PF-16 with a common-mode failure probability *p_cm* (a single client implementation, or a shared host or cloud): P(safety loss) ≈ *p_cm* + (1 − *p_cm*)·Binom tail(*N_v*, *f_B*+1, *p_c*). At *p_c* = 0.05:

| *N_v* | *p_cm* = 0 | 0.01 | 0.05 |
|---|---|---|---|
| 4 | 1.40·10⁻² | 2.39·10⁻² | 6.33·10⁻² |
| 7 | 3.76×10⁻³ | 1.37×10⁻² | 5.36×10⁻² |
| 10 | 1.03×10⁻³ | 1.10×10⁻² | 5.10×10⁻² |

A correlated-collusion (beta-binomial) variant at *N_v* = 4 gives 3.20×10⁻² (ρ_c = 0.1) and 4.94×10⁻² (ρ_c = 0.3), tending to *p_c* as ρ_c → 1. *So what:* with HHI = 1, adding validators stops helping once the binomial tail falls below *p_cm*. That already happens at *N_v* = 7 for *p_cm* = 0.01. Client diversity, not validator count, is the lever.

**PF-66 · Governance single-key compromise vs m-of-n (MD-20; RV-DLT-05, RV-GOV-07; BP-L4.2-02).** `registryAuthority`, `governor` and `ISSUER_ROLE` are single keys. With independent per-period compromise probability *p_key* = 0.01 (E), P(compromise) is 1.00×10⁻² for 1-of-1, 2.98×10⁻⁴ for 2-of-3 and 9.85×10⁻⁶ for 3-of-5. A time-lock that lets honest parties detect and veto with probability *p_d* = 0.9 multiplies each by (1 − *p_d*): 1.00×10⁻³ for 1-of-1 and 2.98×10⁻⁵ for 2-of-3, valid if *T_lock* ≥ detection time. *So what:* a 2-of-3 multisig buys ≈ 34× and a time-lock ≈ 10× on these inputs. Both are cheap compared with the single-key status quo (CA-16).

---

## 8. Parameters: R7 → R8 PAR map (R8 owns PAR-)

*What this means for the level above:* one parameter, one number, suite-wide. R7 declares no PAR of its own. Each input R7 uses is listed with the R8 PAR that now carries it; PAR-31..43 were appended to R8 at R7's request. **Undecided choices are left undecided.**

| v0-1 R7 PAR | Meaning | **R8 PAR** | Feeds PF | Current default and source | Decided? |
|---|---|---|---|---|---|
| ~~PAR-01~~ | validator count *N_v* | **PAR-04** | 36, 37, 38, 40, 57, 60, 65 | 1 (Hardhat, executed); 4 (R4 lineage, Ds) | no |
| ~~PAR-02~~ | block interval Δ | **PAR-05** | 40, 49, 50, 57 | none on automine; 2 s in R4 (Ds) | no |
| ~~PAR-03~~ | block gas limit *G* | **PAR-06** | 49, 50 | 60 M instrument (M config); design 30 M / 100 M | no |
| ~~PAR-04~~ | round-change timeout *t_rc* | **PAR-31** | 40, 57 | none in repo | no |
| ~~PAR-05~~ | proposer selection | **PAR-32** | 40 | round-robin assumed | no |
| ~~PAR-06~~ | client(s) and shares *s_c* | **PAR-02** | 60, 65 | Hardhat 2.28.6 only | no |
| ~~PAR-07~~ | sign/verify hardware class | **PAR-33** | 43 | software on Xeon (#27) | no |
| ~~PAR-08~~ | RNG min-entropy, seeding | **PAR-34** | 41, 42, 63 | host CSPRNG; testbed SHA-256(id) | no |
| ~~PAR-09~~ | V2X signature curve | **PAR-10** | 32, 43 | secp256k1 (SSI); P-256 (PKI arm) | no |
| ~~PAR-10~~ | radio technology | **PAR-16** | 44, 45, 46 | PC5 model in `cv2x_stack.py`; no 802.11p model | no |
| ~~PAR-11~~ | MCS / data rate | **PAR-35** | 44, 46 | 6 Mb/s; ≈ 190 B/sub-channel (E) | no |
| ~~PAR-12~~ | encoding and 1609.2 profile | **PAR-36** | 44 | JSON (#23) | no |
| ~~PAR-13~~ | identity budget fraction *f_id* | **PAR-24** | 43, 54, 55 | 0.5 (working) | working |
| ~~PAR-14~~ | read-path RTT class | **PAR-26** | 43, 57, 64 | localhost (#39) | no |
| ~~PAR-15~~ | gossip fan-out | **PAR-37** | — (gossip PF dropped) | none | no |
| ~~PAR-16~~ | freshness window | **PAR-38** | 47, 53 | 1.0 / 0.1 s | default |
| ~~PAR-17~~ | backhaul availability model | **PAR-39** | 48, 57a | none | no |
| ~~PAR-18~~ | *k_f* and TTL | **PAR-19 + PAR-20** | 54, 55 | *k_f* configurable; no TTL | no |
| ~~PAR-19~~ | replay-cache size | **PAR-40** | 53 | 65,536 | default |
| ~~PAR-20~~ | revocation profile | **PAR-12** | 62 | SOL-09 both | no |
| ~~PAR-21~~ | proof system and setup | **PAR-11 + PAR-41** | 35, 51 | Groth16 BN254; single-party setup | no |
| ~~PAR-22~~ | pseudonym budget *K* | **PAR-22** | 50 | 1,040/yr (R4, E); 20 per 5 min (#38) | no |
| ~~PAR-23~~ | fleet size *V* | **PAR-42** | 50 | 1.5×10⁹ (E) | no |
| ~~PAR-24~~ | settlement option | **PAR-18** | 57 | Hardhat executed; A/B/C Ds | no |
| ~~PAR-25~~ | manoeuvre-class W budgets | **PAR-43** | 48, 54 | open since Phase 1 | no |
| ~~PAR-26~~ | neighbour density *P* | **PAR-25** | 43, 44, 46, 53 | 50–300 | no |

---

## 9. PF index with "So what"

| PF | Statement (one line) | Status | Bounds BP | Used by | So what |
|---|---|---|---|---|---|
| 32 | ECDSA EUF-CMA ≤ q²/n_G (GGM); malleability, nonce, entropy caveats | S | L1-01, L1-02, BP-L1.1-02 | all | The signature is not the weak link; nonce and entropy handling are. |
| 33 | keccak CR 2^128; unsalted VIN serial = 19.93 bits → 3.58 s (#60) | S / M | L1-03, BP-L6.1-01 | 03, 05, SOL-11 | Hashing a VIN does not hide it; only salted or ZK paths do (SLD-08). |
| 34 | hash commitment binds at 2⁻¹²⁸, hides iff salted; Pedersen perfectly hiding | Dv | L1-03, BP-L6.1-01 | SOL-11 | Every low-entropy attribute needs a ≥ 128-bit salt (PRM-L1.1-03). |
| 35 | Groth16 sound only with honest CRS; repo setup single-party ⇒ P = *p_s* | S / M (setup) | BP-L1.2-03, BP-L1.2-04 | SOL-11 | No production soundness claim for ZK-VIN until a ceremony (NC-04). |
| 36 | union bound over failure events (computational, governance, implementation); *N_v* = 1 instance = *p_c* | Dv (gated, SLD-10) | L6-02, L6-04, L3-01 | 05, 06 | Binding is as strong as ledger governance; better curves buy nothing yet. |
| 37 | QBFT safety N_v ≥ 3f_B+1 (async), liveness after GST | S / Ds | L3-01..03 | 02 | Design-appendix table; the executed system has none of it (SLD-13). |
| 38 | QBFT messages (N_v−1)(2N_v+1): 27…945 for N_v 4…22 | Dv / Ds | L3-02 | 02 | Consensus traffic is never the consortium bottleneck. |
| 39 | Hardhat automine: N_v = 1, no Δ, t_finalise ≡ 0; gas portable, latency not | M (config) / Dv | L3-01, L7-07, BP-L3.2-02 | 01 | Quote repo latency only as client + RPC cost (SLD-01; NC-01). |
| 40 | t_conf: 3 s fault-free; 5.50 s (N_v = 4, one crash); worst t_rc·2^f_B | Dv / Ds | L3-02, L3-03 | 02 | Liveness tails, not means, decide consortium design. |
| 41 | RNG κ → shared-key pairs (≈ 4.0×10³ at κ = 48, 1.5×10⁹ devices) | Dv / E | BP-LH-01 | all | Key quality is decided in silicon before any protocol runs. |
| 42 | SP 800-90B RCT 21/41/201; seeding 0.64 ms–4 s | Dv / E | BP-LH-01 | all | No key generation before full DRBG seeding (one ch6 sentence). |
| 43 | ρ_v = P·10·t_ver; P\*(0.5) = 320 (#26 model) / 352 sw ceiling / 200 ASIC / 50 A53 / 10 MCU; ledger criteria k_f ≥ rPt_chain/f_id (27.9) and total-budget knee 91 | M (sw) / E (hw) / Dv | L7-07 | 05 | On the cached path the OBU, not the ledger, saturates first (SLD-03). |
| 44 | airtime: N_fit 182 (digest) … 63 / 37 (repo JSON) at CBR 0.6; PC5 300/120/60 | Dv / E | L0-04, BP-L7.2-04 | 05 | Repo messages are 2.9–5.0× too big for the channel (SLD-04; NC-10). |
| 45 | SPS reselection: P(same resource 1 s after pseudonym change) = 0.136 / 0.449 / 0.805 | Dv / E | BP-L0.1-02, L6-05 | 05 | Pseudonym change must force reselection, or the radio links it (SLD-07). |
| 46 | PC5 P_loss bracket: [0.149, 0.460] at CBR 0.6 (digest) | Dv / E | BP-L0.1-01 | 05 | Count-based freshness must budget for ≈ 15 %+ MAC loss at density. |
| 47 | holdover T = T_fut/(2d): 27.8 h…0.28 h; spoofing widens replay | Dv | BP-LH-04, L7-03 | 05 | The freshness window inherits GNSS integrity (NC-02). |
| 48 | RSU backhaul: E[W] = W_0 + (1−A_L)·resid; p99.9 up to 2,772 s | Dv / Ds | L6-04, BP-L0.2-01 | 05, 09 | State revocation latency as tail quantiles (SLD-14). |
| 49 | ops/s = G/(g_F·Δ) per function; G ∈ {30, 60, 100} M | M gas / Dv | L4-05 | 02, 06 | Cost and capacity are per-function vectors with G, Δ as PAR (SLD-02). |
| 50 | fleet anchoring 54–181× over capacity (90.3× at 60 M); creation 0 gas; privacy-excluded design | Dv | L4-05, BP-L7.2-01 | 02 | On-chain pseudonyms fail on privacy before capacity (DRP-02). |
| 51 | Groth16 gas 181,000 + 6,150·n_pub + calldata = 252,794 vs 256,038 M (1.3 %) | Dv / M | BP-L1.2-02, BP-L1.2-04 | SOL-11 | ZK admission cost is understood to the opcode; setup is the caveat (SLD-09). |
| 52 | storage 22,100 gas/word vs LOG3 9,692/kB; ≈ 28× with calldata, ≈ 18× under EIP-7623 | S / Dv | L2-04, L4-05 | 06 | Event-only attributes are 18–28× cheaper to write and pay on reads. |
| 53 | replay cache ≥ 10·P·1.1; default holds 5,958 senders (596 with margin) | Dv | BP-L2.3-02, L7-03 | 05 | The default cache is ample; fix the docstring (CA-08). |
| 54 | state staleness ≤ k_f−1 msgs (M); time only with TTL; knee 91 | M / Dv | L6-04, BP-L7.2-03 | 05, 09 | Without a TTL, a quiet sender's stale key is accepted indefinitely (CA-07). |
| 55 | k_f\* = ⌊r_s·σ_max⌋+1 (11 / 26 / 101); knee ≈ 8.9 s revoked-key acceptance | Dv | L6-04 | 05 | Choose *k_f* from the security budget, not from cost (SLD-05). |
| 56 | freshness-term table | Dv | L6-04 | 05 | σ_k is the dominant measured term of W. |
| 57 | time-to-confirm metric (+57a availability) | Ds / Dv | L3-02 | R8 MD-01, MD-10 | MD-01 cells stay empty for the executed system. |
| 58 | trilemma coordinates (T, L, C) | Dv | — | R8 MD-03 | Places each option on R3's surface from three PFs. |
| 59 | protocol-security triple (class, loss, bits); 4.16 bits at N_v = 4 | Dv | — | R8 MD-05 | A "128-bit" system is ledger-limited to a few bits of confidence. |
| 60 | NC = f_B+1, PF-16, HHI, Shannon, governance score; today NC = 1, HHI = 1 | Dv | L3-01, L4-04 | R8 MD-02 | The executed system has no decentralisation to report (NC-01). |
| 61 | SC security vector (access, replay, kill rate, attacks, audit) | M partial | BP-L5.2-01..06 | R8 MD-04 | Tabulate (a), (b), (e) before citing (SLD-16). |
| 62 | privacy: k_A, ℓ, hiding bits | M / Dv | L6-05, BP-L0.1-02 | R8 MD-09 | One number per layer: chain *k_A* = 1, RF ℓ up to 0.8, VIN 19.93 bits. |
| 63 | test-key κ = H(vehicle_id): 0 – 19.93 bits for realistic id spaces | Dv | BP-LH-02 | R8 RV-THR-15 | Deterministic keys are public keys; guard by chain id (CA-18). |
| 64 | false-read P: p_lie (k = 1) → 3.0×10⁻⁶ (2-of-3) → ≈ 2⁻¹²⁸ + p_hdr (proof) | Dv / E | BP-L0.4-02, BP-LH-06 | R8 RV-READ-13 | Fail-closed is not lie-proof; only proofs or independent endpoints help (NC-06). |
| 65 | P(safety loss) ≈ p_cm + (1−p_cm)·Binom tail | Dv / E | BP-L3.2-01, BP-L1.2-02 | R8 MD-02 | Under monoculture, client diversity beats adding validators. |
| 66 | governance compromise 10⁻² (1-of-1) → 3.0×10⁻⁴ (2-of-3); ×(1 − p_d) with time-lock | Dv / E | BP-L4.2-01, BP-L4.2-02 | R8 MD-20 | Single-key roles are the cheapest governance fix in the repo (CA-16). |

PF-45 and PF-46 are no longer reserved. Their v0-1 placeholder meanings (verify-on-demand policy model; congestion-control dynamics) are retired: verify-on-demand stays inside PF-43, and congestion-control dynamics remain Q-R7-04. The gossip calculation the v0-1 script printed has no PF and is dropped (fan-out is PAR-37).

---

## 10. Corrections to Phase 1 and confirmations (re-keyed)

| New key | Old key | Corrects / confirms | Content | Disposition (R9 §3.4) |
|---|---|---|---|---|
| **KD-R7-01** | ~~KD-R4-01~~ | corrects R4 PF-24 *G* | Hardhat's 60,000,000 is the *instrument's* development default (M as config). R4's 30 M / 100 M are design scenarios, not errors. PF-49/50 report all three, with *G* as PAR-06. | **QUALIFIED** (X-2; PN-14) |
| **KD-R7-02** | ~~KD-R4-02~~ (+ ~~KD-R4-07~~, + KD-R6-02) | corrects R4 PF-24, PF-25, PF-28 and R4 §3 SOL-01 "finality ≈ Δ" | The executed chain has no Δ and finality ≡ 0. R4's Δ = 2 s rows are Ds. | **ACCEPT** (X-1) |
| **KD-R7-03** | ~~KD-R4-03~~ | corrects R4 *g_op* 50k–180k (E) | measured per function: ERC-1056 32,868–76,830; other standards up to 1,757,881 (§5.1) | **ACCEPT** (X-3) |
| **KD-R7-04** | ~~KD-R4-04~~ | corrects R4 PF-24 fleet "two orders above any row" | ≈ 90× at *G* = 60 M, Δ = 2 s (both PAR), 54–181× across *G*; privacy-excluded design; creation 0 gas | **QUALIFIED** (X-4; PN-14, PN-15) |
| **KD-R7-05** | ~~KD-R4-05~~ | corrects R4 PF-11 *p_s*^*t_s* | repo setup single-party: P = *p_s* (#57) | **ACCEPT** (X-5) |
| **KD-R7-06** | ~~KD-R4-06~~ | corrects R4 σ = 5 s (time) | repo bounds staleness in messages (*k_f* − 1); time only with TTL | **ACCEPT** (X-6) |
| ~~KD-R7-07~~ | ~~KD-R4-07~~ | — | merged into KD-R7-02 (number retired, not reused) | merged (X-1) |
| **CEV-R7-01** | ~~KD-R4-08~~ | confirms R4 PF-31 | RPC read O(10–200 ms) consistent with 15.513 ms uncached local (#21), 91.113 ms at history 50 (#31), probe 3.2 ms (#37); history-dependent | confirmation (PN-20) |
| **CEV-R7-02** | ~~KD-R4-09~~ | confirms R4 PF-02, PF-04, PF-16, PF-19 | re-computed by `r7_calc_v0-2.py` §A; all reproduce | confirmation (PN-20) |

---

## 11. Citation limits (LIM-R7-nn; PN-18)

Each row goes through the Accuracy Ledger before the dependent number is cited in a chapter.

| LIM | Unfetched or unverified source | Carries | Effect until fetched |
|---|---|---|---|
| LIM-R7-01 | SR-L..T author lists and years | §1 SR table | cite by result name only |
| LIM-R7-02 | IEEE 1609.2 overhead sizes 86 / 162 / 210 B | PF-44 rows, SYM-39 | E; label "1609.2-style" |
| LIM-R7-03 | HSM, ASIC and ECU *t_ver* classes (0.25 / 1 / 5 ms) | PF-43 rows | E; Q-R7-02 |
| LIM-R7-04 | verify-on-demand as 1609.2 practice | PF-43 *φ_v* | E (practice), was "S in kind" |
| LIM-R7-05 | Heninger et al., "Mining your Ps and Qs" (2012) | PF-41 reading | illustrative only |
| LIM-R7-06 | BN254 ≈ 100-bit after TNFS | PF-35 | via R4 PF-10 only |
| LIM-R7-07 | BSM part I 40 B, MAC overhead 36 B, PC5 190 B/sub-channel | PF-44, PF-46 | E |
| LIM-R7-08 | EIP-7623 calldata floor applied by Hardhat 2.28.6 under `osaka` | PF-52 last column | Dv conditional; confirm by one measured log-only receipt |

---

## 12. Dispositions of R9 findings against R7

Each disputed number was re-derived independently in `r7_calc_v0-2.py` before the panel's value was accepted.

| PN | Finding | Re-derivation | Disposition |
|---|---|---|---|
| PN-10 | script labels ≠ document PFs | header map + labels re-written; self-check reads this file | **ACCEPT**; self-check exits non-zero on any mismatch |
| PN-11 | units error in the ledger-bottleneck condition | refresh-load: 10·100·0.01394/0.5 = 27.88; v0-1 form ×10 = 278.8 | **ACCEPT** (27.9). Added: the #32 knee is the *total-budget* criterion, 0.01394/(0.0005 − 0.000346) → ⌈90.5⌉ = 91; at *P* = 300 it is infeasible |
| PN-12 | reselection linkability | exact E[(*L*−1)⁺]/E[*L*]; at *P_keep* = 0: 1.5/11 = **0.1364** | **ACCEPT with refinement**: 0.136 / 0.449 / 0.805 (panel 0.135 / 0.449 / 0.804 is within MC noise); moved to PF-45 |
| PN-13 | LOG base cost; calldata basis | 375 + 1,125 + 8,192 = 9,692; (707,200 + 16,384)/(9,692 + 16,384) = 27.7× | **ACCEPT, and go further**: under `osaka` (EIP-7623 floor, 40 gas per non-zero byte) the log tx pays 40,960, so the ratio is 723,584/40,960 = **17.7×**. This disagrees with both v0-1 (76–84×) and the panel (28×); quoted as 18–28× pending LIM-R7-08 |
| PN-14 | KD on 60 M / fleet | 30/60/100 M rows computed | **ACCEPT**: KD-R7-01 and KD-R7-04 QUALIFIED |
| PN-15 | PF-50 sizes an excluded design | — | **ACCEPT**; exclusion sentence leads §5.2 |
| PN-16 | precision beyond register | 50/0.142 = 352.1; 50/0.090 = 555.6; 50/0.164 = 304.9 | **ACCEPT**; 305 leads; 352 is the crypto-only ceiling (v0-1's 351 came from 0.14225) |
| PN-17 | MC "< 2 %" overstated | 2×10⁶ draws: max 1.34 % on non-degenerate cells | **ACCEPT** "< 3 %", satisfied at 1.34 %; one degenerate cell excluded with reason |
| PN-18 | unfetched citations | — | **ACCEPT**; LIM-R7-01..08; verify-on-demand → E |
| PN-19 | heterogeneous sum in PF-36 | log₁₀(1.402×10⁻²/2.939×10⁻³⁹) = 36.68 | **ACCEPT**; term-nature table; *N_v* = 1 instance added; "37 orders" restated as 36.7 |
| PN-20 | KD-R4-08/09 are confirmations | — | **ACCEPT**; CEV-R7-01/02 |
| PN-21 | run-of-record ambiguity | values identical where checked | **ACCEPT**; register row = authority, run id = provenance |
| PN-25, PN-26, PN-31, PN-32 | MD binding; PAR and key collisions; status scale | — | **ACCEPT**; §7, §8, §10, header |
| PN-03, PN-08 (R6-facing) | PF requests | — | supplied PF-45 (BP-L0.1-02), PF-46 (PF-⟦5⟧), PF-54 (BP-L7.2-03), PF-44 (BP-L7.2-04), PF-63..66 (PF-⟦2⟧, ⟦4⟧, ⟦12⟧, ⟦14⟧) |
| DRP-07, DRP-08 | shorten RNG; drop Byzantium comparison | — | **ACCEPT**; §4.1 is one table; the pre-EIP-1108 figure is removed |

**Where I disagree with the panel:** only PN-13's final figure. The panel's 28× is correct for pre-Prague calldata pricing. On the executed hardfork the EIP-7623 floor lowers the ratio to ≈ 18×, conditional on LIM-R7-08. Everything else is accepted as stated or refined within Monte Carlo noise.

---

## 13. Change log v0-1 → v0-2

| # | Change | PN / R9 ref |
|---|---|---|
| 1 | Header: v0-2, re-keyed line, unified status scale, progress 90 %, Assigns updated (no PAR) | §7.2.1, PN-31, PN-32 |
| 2 | Script `r7_calc_v0-2.py`: labels = document PFs; header map; self-check; reads `meta.json` | PN-10 |
| 3 | PF-43 refresh condition corrected; total-budget knee reconciled with #32 | PN-11 |
| 4 | Reselection split to PF-45; exact residual-life computation + seeded MC; range 0.14–0.80 | PN-12 |
| 5 | PF-46 filled (PC5 loss bracket) | R9 Table A′ (PF-⟦5⟧) |
| 6 | PF-52: LOG base cost; calldata basis; EIP-7623 column | PN-13 |
| 7 | KD-R7-01/04 QUALIFIED; capacity at G ∈ {30, 60, 100} M | PN-14 |
| 8 | PF-50 privacy-exclusion sentence | PN-15 |
| 9 | Register precision (0.142 / 0.090); 305 leads | PN-16 |
| 10 | Backhaul MC raised to 2×10⁶ draws; "< 3 %" stated with value | PN-17 |
| 11 | LIM-R7-01..08; verify-on-demand → E | PN-18 |
| 12 | PF-36 rewritten as a labelled union bound; *N_v* = 1 instance; SLD-10 gate | PN-19, SLD-10 |
| 13 | KD-R4-08/09 → CEV-R7-01/02; KD-R4-01..07 → KD-R7-01..06 issued; KD-R7-07 retired by merge | PN-20, §3.1 |
| 14 | Provenance rule for gas | PN-21 |
| 15 | PAR map to R8 numbers | PN-26 |
| 16 | MD bindings per R9 Table C′ | PN-25 |
| 17 | ⟦…⟧ resolved per R9 Table B′; no unresolved R7 placeholder remains (the only ⟦⟧ left quote R6's PF-⟦n⟧ request names) | §3.3, §7.4 |
| 18 | PF-63..66 added at R8/R9 request | PN-03, R8 v0-2 |
| 19 | §4.1–4.2 collapsed to one table; Byzantium comparison removed | DRP-07, DRP-08 |
| 20 | Each section opens with what it means for the level above; PF index carries "So what" | brief §5 |

---

## 14. HANDOFF (R7 v0-3)

**Files.** `docs/roots/phase2/70_R7_theory_ece_bounds/claude_CVIN_SC_Roots_Theory_ECE_Bounds_R7_v0-3.md` (this document) and `…/r7_calc_v0-3.py` (prints every number; seeds 42 and 2026; the self-check against this file passes, exit 0). v0-1, v0-2, `r7_calc.py` and `r7_calc_v0-2.py` are untouched.

**Tags.** Assigned: SYM-25..58; SR-L..T; PF-32..66 (45/46 filled; 63..66 new); Q-R7-01..08; KD-R7-01..06 issued; KD-R7-07 retired by merge; CEV-R7-01..02; LIM-R7-01..08. Retired: ~~KD-R4-01..09~~ (R7-issued), ~~R7 PAR-01..26~~ → R8 PAR (§8), the v0-1 script working labels, the reserved meanings of PF-45/46. Consumed: R4 PF/SYM/SR; R6 HW-, ALG-, IMP-, SCF-, BP-, SOL-11; R8 MD-, PAR-; R9 PN-, SLD-, DRP-, NC-, CA-.

**Five load-bearing decisions.**
1. PF-39: the executed system is *N_v* = 1 with no Δ. Gas is portable; latency is client + RPC only.
2. PF-43/44/45: on Tier 1, OBU verification, airtime and SPS resource persistence bind before the ledger. Repo JSON is 2.9–5.0× too large.
3. PF-54/55: freshness is a message count until a TTL exists; *k_f*\* is set by σ_max.
4. PF-36/65/66: binding is a union bound dominated by governance and common-mode terms, not cryptography.
5. *G* = 60 M is an instrument value. Capacity is reported over *G* ∈ {30, 60, 100} M with *G* and Δ as PAR.

**Open questions.** Q-R7-01 Besu genesis; Q-R7-02 HSM/ECU *t_ver*; Q-R7-03 IDTX gas (E-F1-1); Q-R7-04 SPS counter and 802.11p model in `cv2x_stack.py`; Q-R7-05 RSU propagation; Q-R7-06 docstring 650 → 596; Q-R7-07 provider TTL; Q-R7-08 tabulate PF-61(a),(e). Also: confirm the EIP-7623 floor on one receipt (LIM-R7-08); blind re-derivation of PF-36 (SLD-10, owner per Q-R9-04).

**Corrections issued.** PF-43 condition (278.8 → 27.9); reselection linkability (0.368/0.549/0.819 → 0.136/0.449/0.805); LOG3 per kB (9,317 → 9,692) and storage/log ratio (76–84× → 18–28× by basis); software *P*\*(0.5) 351 → 352 (crypto-only ceiling; 320 leads from #26, PN-34); ledger-vs-crypto gap "37" → 36.7 orders.
