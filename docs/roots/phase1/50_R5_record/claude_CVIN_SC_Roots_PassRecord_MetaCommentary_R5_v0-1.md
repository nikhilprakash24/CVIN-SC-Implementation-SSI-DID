# CVIN-SC · R5 — Roots Thread Pass Record: Version Control, Method, Corrections, Unresolved Register, and Meta-Commentary

**The audit trail of the Roots thread (G-R1, Prompts 1–3): what was read, what was derived, what was found, what is owed to the SSoT, and the questions only the researcher can close.**

Document 5 of the Roots suite · v0.1 · 2026-09-15 · CVIN-SC Research Programme · UBC ECE MASc
Series note: continues the programme's meta-commentary line (Passes 1–5, Pass P). Pass number **provisional — "Pass R(oots)"**; keys `KD-R#`, `CEV-R#`, `Q-R#`, `LIM-R#`, `MC-R#`, `F-R#` are namespaced provisional and re-key at the next Scaffolding roll with a mapping table.
Form: the S3 five-part form (Deliverable Suite Architecture §3.3). Each meta-commentary part closes with one load-bearing question under the test: *if the model can answer it, rewrite it.*

---

## 1. Version-control entry

| Field | Entry |
|---|---|
| Suite | Roots suite, thread G-R1 (provisional) |
| Session scope | Three prompts executed in one thread (the researcher chose to run Prompts 2 and 3 in-thread against the protocol's recommendation; noted, no consequence observed except length pressure at Prompt 3) |
| Request fulfilled | The five deliverables of the 2026-09-06 brief: roots lineage extended (D1), integration scan (D3), the I2I/identity stack document with figures (D2), proofs and bounds (D5), this record (D4) |
| Documents issued | `claude_CVIN_SC_Roots_Lineage_R1_v1-1.md` + `.svg` · `claude_CVIN_SC_Roots_Integration_Scan_R2_v0-1.md` · `claude_CVIN_SC_Roots_I2I_Identity_Stack_R3_v0-1.md` + `FIG-R1`…`FIG-R6.svg` · `claude_CVIN_SC_Roots_Proof_and_Bounds_R4_v0-1.md` · this document. Also issued earlier in the thread: `claude_CVIN_SC_Roots_Thread_Prompt_Set_G-R1_v0-1.md` and `claude_CVIN_SC_Large_Command_Protocol_v1-0.md` |
| Supersedes | `Bitcoin_Technology_Lineage_Report_v1-0.md` and its SVG → R1 v1.1 (content carried, not changed) |
| Registry effect | New tag namespaces: `L6`, `L7`; `T-I01`–`T-I22`; `SOL-01`–`SOL-09`; `BP-L0-01`…`BP-L7-07` (51); `SYM-01`–`SYM-24`; `PF-01`–`PF-31`; `FIG-R1`–`FIG-R6`. No existing tag altered. |
| Numbering note | All provisional. `T-01`–`T-24` frozen from v1.0. R3's `PF-⟦n⟧` placeholders map 1:1 to R4's `PF-n` except that R3's ⟦1⟧–⟦4⟧ became `PF-01′`–`PF-04′` in R4 §2 because `PF-01`–`PF-04` were pre-assigned to the collision bounds by the prompt; the mapping is: R3 ⟦1⟧→PF-01′, ⟦2⟧→PF-02′, ⟦3⟧→PF-03′, ⟦4⟧→PF-04′, ⟦5⟧→PF-05, ⟦6⟧→PF-06 … ⟦31⟧→PF-31. **Re-key at the Scaffolding roll to remove the primes.** |

## 2. Methodology notes

**Method.** In-thread, configured model, no subagents. Corpus sampled by project search rather than read whole (Terminology Freeze; Building Paths v1.1 preface; Family E v2.0; P1–P4; G-B; G-C1 fragments; Pass 3-Deep; Ch. 3 sectioning; Scaffolding v0.4; Narrative Synthesis Ch. 4; S1 Reference Index). No web search was run: every date and result in R1 §10 and R4 §0.2 is from training knowledge and is so marked (R1 accuracy note; R4 status column). This is a deliberate scope choice for a lineage document and a *limitation* for a thesis citation — see LIM-R1.

**Arithmetic.** Every number in R4 was computed in a scratch script (Python: `scipy.stats.binom`, `poisson`; closed-form birthday and Nakamoto §11) before being written, and the equation and inputs are printed beside it. The MC-P-1 lesson (a fetched constant mis-subtracted) was applied prophylactically.

**Figures.** Six SVGs generated programmatically from the same tag lists as the prose, so a tag in a figure is guaranteed to exist in the document. Validated as well-formed XML. Mobile constraint (viewBox ≤ 900) respected; FIG-R5 is tall (1000) by necessity.

**What was not done.** No thesis prose. No measurement. No change to any frozen count or name. No reading of `ISetC.sol` (Q-R2 open). No Pass 4 fleet numbers retrieved (PF-04 uses an order-of-magnitude global parc).

## 3. Corrections ledger (KD-R)

| Key | What | Correction | Propagate to |
|---|---|---|---|
| KD-R1 | R1 v1.0 §7 and R2 §3.3 carried "ERC-8004 mainnet January 29 2026" from Family E v2.0 | Use the S1 ledger wording: "reference contracts deployed" with retrieval date; never "standard finalised" (ERC-8004 is Draft) | R1 §8 table row 2026; R2 §3.3 O9 row; Family E v2.0 at harvest |
| KD-R2 | R3 HANDOFF numbered the first four PF placeholders 1–4, colliding with the prompt's pre-assignment of PF-01–04 to collision bounds | R4 uses PF-01′–PF-04′ for the L0 bounds; re-key at the roll (see §1 numbering note) | R3 Part II L0 table "Bound" column; R4 §2 |
| KD-R3 | R1 v1.0 stated Merkle root "committing to an arbitrarily large set" without the domain-separation caveat | R3 BP-L2-01 adds CVE-2012-2459-class leaf/node confusion as a breaking point; R1 unchanged (historical register) | R3 only |

No corrections to the reconciled corpus (K-, RK-, KD-P) were found necessary; none were made.

## 4. Unresolved register

### 4.1 Questions for the researcher (Q-R)

| Key | Question | Blocks |
|---|---|---|
| Q-R1 | Is SCMS butterfly-key unlinkability at Tier 1 (T-I05) a requirement the ledger design must *match*, or out of scope because the ledger is out of scope at Tier 1 (X4)? | R3 Table I.2 R5 row; PF-24's conclusion that Tier-1 pseudonym issuance stays off-ledger |
| Q-R2 | Does `ISetC.sol` exist with named functions? | R3 I4 row, BP-L6-06; R2 SOL-06 paragraph |
| Q-R3 | Add Certificate Transparency (T-I02) to Related Work as the anchoring precedent? | G-D1 audit; R3 Part III SOL-03 |
| Q-R4 | Which message classes are deniable vs auditable (BP-L7-06)? DIDComm `authcrypt` vs `anoncrypt` is the mechanism; the policy is the researcher's | R3 R4/R4′ rows |
| Q-R5 | Which manoeuvre-class W budgets from G-C1 §2.7 are the targets for PF-28, and what are the Pass 4 fleet sizes for PF-04? | R4 PF-02′, PF-04, PF-28, §3 |
| Q-R6 | Confirm Δ and *G* from the sandbox genesis manifest, and *g_op* per option/arm from the traces, to convert PF-24/25/28 from ESTIMATED to DERIVED | R4 §2 L4, §3 |

### 4.2 Findings needing verification (F-R) and their CEV rows

| Key | Finding | Verification state |
|---|---|---|
| F-R1 | `did:indy` / `did:sov` identifiers are 128-bit (first 16 bytes of the verkey), so the Indy namespace reaches a 10⁻¹² accidental-collision probability at ≈ 2.6×10^13 identifiers — the order of the 20-year fleet — while the EVM 160-bit namespace does not until 1.7×10^18. Not an attack; a namespace-integrity defect worth one sentence in Ch. 3 and a row in the Family E finality/archival comparison | **PENDING** — verify the 16-byte rule at the did:indy method spec |
| F-R2 | Under Grover, a 160-bit address preimage costs 2^80 — the weakest post-quantum figure in the stack, below the 2^85 hash-collision figure | STANDARD-RESULT arithmetic; the *relevance* (does an address preimage matter when the key is exposed anyway?) is the open point |
| F-R3 | The AnonCreds 12/12 ranking rests on an assumption class with concrete security ≤ ECDLP by 8–28 bits (PF-10) | STANDARD-RESULT (Barbulescu–Duquesne; Guillevic) — cite at harvest |
| F-R4 | The fleet-scale write rate (4.9×10^4 creations/s, PF-24) exceeds any single Plane-A configuration by two orders — capacity, not address space, is the scaling constraint | DERIVED from ESTIMATED inputs; becomes a thesis claim only with Q-R5/Q-R6 inputs |

**CEV-R rows (DERIVED / MEASURED only):**

| CEV-R | Claim | Evidence | Verification | Residual |
|---|---|---|---|---|
| CEV-R1 | Collision bounds PF-01/02/04 | SR-A; arithmetic in R4 §1 | DERIVED; recomputed | inputs *V*, *K*, *Y* ESTIMATED |
| CEV-R2 | BFT collusion table PF-16 | SR-K; script | DERIVED | independence assumption — the correlated validator–issuer row is the counter-case |
| CEV-R3 | Nakamoto reversal table PF-19 | SR-D; script | DERIVED | raw *q*, not selfish-adjusted |
| CEV-R4 | W under Option A ≈ 3 s + σ (PF-28) | G-C1 §2.7 decomposition; Δ = 2 s | DERIVED on ⟦Δ⟧ | Δ unconfirmed (Q-R6) |
| CEV-R5 | Rotation race ≤ 2Δ (PF-25) | QBFT finality; G-B §1.4 | DERIVED | same |
| CEV-R6 | Recovery threshold always weaker than key (PF-30 vs PF-06) | SR-K vs SR-C | DERIVED | none |
| CEV-R7 | The hybrid trades prevention for detection (R3 III.3; PF-13) | P3 §2.3; PF-13 arithmetic | DERIVED | — |

### 4.3 Limitations (LIM-R)

| Key | Limitation |
|---|---|
| LIM-R1 | R1 §10 dates and R4 §0.2 results are from training knowledge, unsearched. Adequate for a lineage; each must pass the Accuracy Ledger before thesis citation. |
| LIM-R2 | R3 assigned 51 breaking points from the "secured by below" walk; it is not a formal threat model and does not claim completeness. G-C1's adversaries A1–A6 were referenced but not enumerated row-by-row against BP-. |
| LIM-R3 | R4's ESTIMATED rows (05, 20, 21, 23, 24 inputs, 28 σ, 31) are placeholders with stated inputs; they are not results. |
| LIM-R4 | The protocol's recommendation (fresh session per prompt) was not followed for Prompts 2–3. The observable cost was length discipline, not correctness; the unobservable cost is unknown. |

## 5. Meta-commentary (MC-R)

**MC-R-1 · The attractive error this pass was the *reassuring* number.** The first draft of PF-04 stopped at "3.3×10⁻²² — the address space is not a constraint" and was about to move on. The next line of the same script, computing the *write rate* the same fleet implies, gave 4.9×10⁴ creations per second — two orders above any Plane-A row. The comfortable bound and the uncomfortable one came from the *same inputs*; only one of them was asked for. The lesson generalises the MC-P-1 rule from "show the arithmetic" to "**run the arithmetic on the adjacent quantity before declaring the first one settled**": a bound that reassures should be followed by the bound it displaces attention from. *Load-bearing question:* is the fleet model (*V*, *K*, *Y*) even the right frame — does the thesis's deployment scenario create identifiers per pseudonym (K ≈ 10³/yr, ledger-infeasible) or per vehicle (K ≈ 1, trivially feasible), and is that choice already made in Pass 4 or is it made here?

**MC-R-2 · The find of the pass is a namespace, not a cipher.** F-R1 (128-bit Indy DIDs) emerged from a routine parameterisation of PF-03 by DID method. Nothing in the corpus's Family E comparison — which is careful about finality models and archival guarantees — mentions identifier width, because identifier width is a *data-model* property and the comparison is framed as a *consensus* comparison. The Roots framing (layer of residence, R2 rule 1) put the identifier at L6 next to the address at L6 and the difference became visible. *Load-bearing question:* is the 16-byte rule actually what `did:indy` (as opposed to legacy `did:sov`) specifies, and if the newer method uses the full 32-byte verkey the finding evaporates — which spec version does the thesis cite?

**MC-R-3 · What resisted: the trilemma.** The brief asked for the trilemma "tied together with the solutions". The slogan form resisted every attempt to place nine solutions on it, because three unlabelled vertices give no coordinates. It yielded only when *security was fixed* at the level identity requires and the remaining two axes were given the operational names the corpus already uses (trust base; finality latency and variance). Once that was done, the hybrid's move became a *vector* (FIG-R3) rather than a claim — and the honest sentence "prevention traded for detection" fell out of the geometry. The general lesson: a triangle with unlabelled vertices is a figure of speech; fix one vertex and it becomes a plane you can plot on. *Load-bearing question:* does the thesis want the trilemma at all, given that its own security thread already uses trust base and finality as first-class axes — or is the triangle only a Ch. 1 gesture to the reader's expectations?

**MC-R-4 · The residual that the numbers made unavoidable.** PF-16 says a four-validator set is not a security configuration at any plausible *p_c*; PF-13 says checkpointing bounds *undetected* rewrite to *τ_a* + *t_pub*; together they say the consortium's security is *governance diversity plus a public clock*, and the cryptography contributes ordering only. That is a stronger and less comfortable statement than "Besu QBFT provides deterministic finality" and it is the one an examiner will press on. The pass did not soften it. *Load-bearing question:* what *N_v* and what independence argument does the deployment narrative actually assume — is there a named consortium, and can its members be argued non-correlated on the validator–issuer axis?

**MC-R-5 · On process: running three prompts in one thread.** The researcher chose to run in-thread. Prompt 1 benefited (the base report was already in context). Prompt 2 was long but complete. Prompt 3 was written against pressure and shows it in one place: R4 §2 is terser at L1 than at L3–L6, and PF-20/21/23 are more skeletal than PF-16/19/28. Nothing was cut, but the *evenness* suffered, which a fresh session would not have shown. The protocol's rule stands; the exception was affordable once. *Load-bearing question:* for the second pass on R4 (blind re-derivation), will the researcher open a fresh session with only the SYM table and PF statements — the one place where a shared context would actively *harm* the check by leaking the first derivation?

---

## HANDOFF — for the second pass on R4 (definitions audit, fresh session)

Give the fresh session **only**: R4 §0.1 (the SYM table), §0.2 (the standard results), and the *statement* column of §5 for the items below — **not** the derivations. Ask it to derive each independently and print arithmetic. Then diff against R4 v0.1; discrepancies become `KD-R#`.

Items to re-derive blind: PF-01, PF-02, PF-03 (state the *a* per method from the spec, not from R4), PF-04 (with Q-R5 inputs if available), PF-13, PF-16 (full table), PF-19 (full table), PF-24, PF-25, PF-28 (as a function, then Option A numeric), PF-29, PF-30.
Items to leave: STANDARD-RESULT rows (07, 09, 10, 22) — check the citation, not the number.
Inputs to supply if known: Δ, *G*, *g_op* per option/arm (Q-R6); W budgets and fleet sizes (Q-R5); `did:indy` identifier width (F-R1).

Expected discrepancy classes: (a) rounding at the third figure — accept; (b) a different λ convention in SR-D — check against Nakamoto §11 verbatim; (c) a different independence model in PF-16 — the *more* conservative wins and is logged.

*End of R5 v0.1. The thread claims five documents, one finding pending verification, three standard-result citations owed, six researcher questions, and no change to the reconciled corpus.*
