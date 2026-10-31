# Blind Re-derivation PF-36: BIND-FAIL bound

Written blind. I opened no project proofs or reviews. All arithmetic was done in python3.

## 1. Definitions

The probability space is joint. It covers (i) the coins of a PPT adversary A that runs in time T and makes q_s signing queries and q_H hash queries, and (ii) the non-computational infrastructure events: validator compromise, resolver faults and key theft. These follow priors that are fixed independently of A's coins.

- **ε_Σ (computational).** This is the advantage of A in multi-user EUF-CMA (MU-EUF-CMA) against Σ over n_D public keys, where A can make adaptive signing queries. A wins if it outputs (i, m*, s*) that verifies under pk_i, where m* was never queried for pk_i. Single-user EUF-CMA is not enough here; see §3.
- **ε_H (computational).** This is A's advantage in finding x ≠ x' with H(x) = H(x'). Two places use it: the message digest that Σ signs, and the commitment of the DID document. Caveat: if Σ is defined as "ECDSA-with-H", then EUF-CMA already includes the message-digest collision. In that case ε_H should count only the DID-document commitment (a resolver serving a document that collides with the committed one). Otherwise the collision is counted twice. This is harmless to the bound, but it is not tidy.
- **ε_L (non-computational prior).** This is the probability that non-equivocation fails: honest readers see diverging or forged final states. For QBFT this is P(#compromised ≥ f_B + 1) = Σ_{k=f_B+1}^{N_v} C(N_v,k) p_c^k (1−p_c)^{N_v−k}, assuming independent compromise. This term is not an adversary advantage. It is an assumption about operators, and it does not shrink with key size. Strictly, a BFT safety violation needs ≥ f_B + 1 colluding faulty validators. Using "compromised" for "colluding Byzantine" is conservative.
- **ε_R (non-computational prior).** This is the probability that R returns a document that differs from the one L's final state implies, or one older than σ. The cause can be a lie or a bug.
- **Revocation term (corrected).** The stated term P(revocation inside σ) is the wrong event. A revocation by itself causes no BIND-FAIL. If the honest owner revoked a key and still signs with it inside σ, the controller as fixed at t−σ did sign, so the event did not happen. The harmful event is ε_K := P(the controller key fixed at t−σ was **compromised (stolen) and used by the attacker** during the window). The window runs from compromise until V's view reflects the revocation, which is up to σ plus the time to detect and revoke. With a key-theft rate λ per key and detection-plus-revocation latency δ, ε_K ≈ λ(σ+δ) per targeted subject. Over the fleet, this is about n_D·λ(σ+δ) for "any subject". The bound as stated also has no key-theft term outside revocation, and needs one: key theft is a non-cryptographic path to forgery.

## 2. Proof (union bound via games)

- **G0.** This is the real experiment. BIND-FAIL means V accepts (D, m, s, t), but sk_D (the key fixed by L at t−σ) never signed m.
- **G1.** Replace "the key R returned" with pk* = the key implied by the common honest final state of L at t−σ. The games differ only if L equivocates or R deviates or is stale. By the difference lemma, |P0 − P1| ≤ ε_L + ε_R.
- **G2.** Additionally require that the document V accepted has the committed hash. The games differ only on a collision for the commitment or the digest, so |P1 − P2| ≤ ε_H.
- **G3.** Exclude the runs in which sk* was stolen (the run is not a cryptographic forgery). The games differ by at most ε_K.
- **In G3,** V accepts a valid signature under pk* on an m that the honest key holder never signed, and sk* is secret. This is a forgery. Build the reduction B: it receives n_D challenge keys and embeds them as the subjects' keys, simulates L and R honestly, and answers signing queries through its oracle. Then P3 ≤ Adv^{MU-EUF-CMA}_Σ(B) = ε_Σ^{(n_D)}.

Result:
**P(BIND-FAIL) ≤ ε_Σ^{(n_D)} + ε_H + ε_L + ε_R + ε_K.**

The sum is valid even though L and R are dependent (R reads L), because the union bound does not need independence. A product such as ε_L·ε_R would be valid only if failure required both events to occur. Here either event alone is enough, so a product would be wrong.

## 3. Multi-user tightness

In the generic reduction, B guesses the target index i ∈ [n_D], so ε_Σ^{(n_D)} ≤ n_D·ε_Σ^{(1)}. For n_D = 3.12×10^13, log2 n_D = 44.83, which leaves 128 − 44.83 ≈ **83.2 bits** of proven security.

The best known generic attack, one-out-of-n discrete log, costs about √(q/n). That gives roughly 128 − 44.83/2 ≈ **105.6 bits** of practical security.

Tight multi-user results exist for Schnorr (via key re-randomisation). For ECDSA the position is weaker, and related-key or additive derivation is a known hazard. So the thesis should state the 83-bit proven figure, or cite a specific MU result for ECDSA. It should not state 128 bits.

## 4. Worked instances

**(a) N_v = 4, f_B = 1, p_c = 0.05.**
- ε_L = 1 − 0.95⁴ − 4(0.05)(0.95³) = 1 − 0.81450625 − 0.171475 = **0.01401875**.
- Total bound = 0.01401875 + 10⁻⁶ + 2·2⁻¹²⁸ = **0.01401975**, which is about 1.40×10⁻².
- log10(ε_L / 2⁻¹²⁸) = −1.853 + 38.532 = **36.68**, so ε_L exceeds ε_Σ by about 37 orders of magnitude. With the n_D loss, ε_Σ is about 2⁻⁸³ ≈ 10⁻²⁵, and the gap is still about 23 orders.

**(b) N_v = 1, f_B = 0, p_c = 0.05.**
- ε_L = P(≥1 of 1 compromised) = 0.05.
- Total bound = **0.050001**.

**(c) Concrete security bits.**
- (a): −log2(0.01401975) = **6.16 bits**.
- (b): −log2(0.050001) = **4.32 bits**.

No cryptographic improvement can change these figures materially, whether larger curves, post-quantum signatures or a better hash. The total is dominated by ε_L. In (a), ε_R = 10⁻⁶ is the next largest term, at about 20 bits. The figure moves only through governance: a larger N_v, a lower p_c, or uncorrelated operators. Calling these figures "bits of security" mixes a computational advantage with an operational prior. They should be reported as probabilities, labelled as such, and conditional on the priors assumed.

## 5. What the thesis may claim

May claim: under EUF-CMA (multi-user), collision resistance, ledger non-equivocation, resolver integrity and no key theft, BIND-FAIL is bounded by the sum of the corresponding terms, and the cryptographic terms are negligible (about 2⁻⁸³ or better, with the multi-user loss).

Must also state: the end-to-end assurance is set by trust assumptions, not by cryptography. With the stated priors it is about 10⁻² for a 4-validator QBFT ledger and 5×10⁻² for the single-node ledger actually executed.

Must not claim: "128-bit security" end to end; that the bound uses a revocation-probability term (it is key compromise within the revocation window); or that the single-node deployment has the non-equivocation property against its own operator.

## VERDICT

**AGREE-WITH-CORRECTIONS**
1. The term "P(revocation inside σ)" is the wrong event. Replace it with ε_K = P(the controller key at t−σ is compromised and used before V's view reflects the revocation), which is about λ(σ+δ) per subject. This also adds the missing key-theft term.
2. ε_Σ must be multi-user: ε_Σ^{(n_D)} ≤ n_D·ε_Σ, which leaves about 83.2 proven bits (about 105.6 bits against the best generic attack), not 128.
3. ε_L and ε_R are non-computational priors, not advantages. Label them as such. Keep the sum, not a product (union bound, no independence needed).
4. ε_H double-counts the digest if Σ is ECDSA-with-H. Restrict ε_H to the DID-document commitment.
5. "Security bits" for the total figure must be presented as operational probability, not cryptographic strength.

Numbers:
- (a) ε_L = 0.01401875; total ≈ 1.402×10⁻²; log10(ε_L/ε_Σ) ≈ 36.68.
- (b) total = 0.050001.
- (c) about 6.16 bits for (a) and 4.32 bits for (b). These are dominated by ε_L, so no cryptographic change can improve them.
