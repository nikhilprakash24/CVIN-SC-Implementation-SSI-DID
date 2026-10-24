# CVIN-SC · Roots Thread (G-R1, provisional) — Three-Prompt Execution Set

**Purpose:** decompose one very large request — the technology stack beneath secure/private I2I communication and decentralised/SSI identity, tied to the Bitcoin roots, with figures, breaking points, solutions, proofs, and meta-commentary — into three sessions that each fit one context window and hand state forward without loss.

v0.1 · 2026-09-06 · CVIN-SC Research Programme · UBC ECE MASc
Thread ID **G-R1** is provisional (assign at the next Scaffolding roll). All keys namespaced `-R#` per the P-thread rule.

---

## 0. The five deliverables and where they land

| # | Deliverable | Lands in | File name |
|---|---|---|---|
| D1 | Bitcoin/blockchain roots (exists, v1.0) → extended v1.1 with identity-relevant primitives | Prompt 1 | `claude_CVIN_SC_Roots_Lineage_R1_v1-1.md` + `.svg` |
| D3 | Integration scan: one index that places every corpus artefact, primitive, and solution on the stack | Prompt 1 | `claude_CVIN_SC_Roots_Integration_Scan_R2_v0-1.md` |
| D2 | The main document: I2I + identity/SSI stack, breaking points at every layer, solutions, ≥6 figures | Prompt 2 | `claude_CVIN_SC_Roots_I2I_Identity_Stack_R3_v0-1.md` + `FIG-R*.svg` |
| D5 | Proof / math / security / numbers, with own symbols and `PF-` tags | Prompt 3 | `claude_CVIN_SC_Roots_Proof_and_Bounds_R4_v0-1.md` |
| D4 | Meta-commentary in the S3 five-part form | Prompt 3 | `claude_CVIN_SC_Roots_PassRecord_MetaCommentary_R5_v0-1.md` |

Order of execution is D1+D3 → D2 → D5+D4. The scan (D3) goes first, as you specified, so the big document is written *against* an integrated map rather than producing one afterwards.

## 1. Shared tag namespaces (fixed now, used by all three prompts)

| Tag | Meaning | Example |
|---|---|---|
| `L0`–`L5` | Stack layers from the Bitcoin roots report; extended with **`L6` identity layer** and **`L7` application/I2I layer** in Prompt 1 | `L3` = distributed agreement |
| `T-xx` | Root technology (dated primitive); `T-01`–`T-24` already assigned | `T-08` Merkle trees |
| `T-Ixx` | Identity-lineage technology added in Prompt 1 | `T-I04` X.509 / PKI 1988 |
| `BP-Lx-nn` | Breaking point at layer x | `BP-L1-02` ECDSA nonce reuse |
| `SOL-nn` | A solution the programme has built or adopted | `SOL-03` Besu QBFT hybrid with public anchoring |
| `PF-nn` | A proof, bound, or derivation in D5 | `PF-04` address-collision bound |
| `SYM-nn` | A symbol defined by us in D5 (own notation) | `SYM-02` \(\kappa\) = effective key-space entropy |
| `FIG-Rn` | Figure in the R-suite | `FIG-R3` trilemma-with-solutions |
| `KD-R#`, `CEV-R#`, `Q-R#`, `LIM-R#`, `MC-R#` | Programme-standard record keys, R-namespaced | as in P-4 |

Rule: a later document never redefines a tag; it cites it. A second pass may *correct* a tag's content and logs the correction as `KD-R#`.

## 2. The context-carry block (paste at the top of Prompts 2 and 3)

Each prompt ends by emitting a **HANDOFF** block of ≤400 words. It contains: files issued (exact names), tag ranges consumed (e.g. "T-I01–T-I19 assigned"), the five most load-bearing decisions, open `Q-R#` questions, and any `KD-R#` corrections. The next prompt begins with that block pasted in. This is what keeps context without relying on the model remembering the prior session.

---

## PROMPT 1 — Roots v1.1 and the Integration Scan (D1 + D3)

```
You are continuing the CVIN-SC Research Programme (UBC ECE MASc). Thread G-R1 (provisional), Prompt 1 of 3.

INPUTS (read at source, in this order):
1. Bitcoin_Technology_Lineage_Report_v1-0.md and its SVG — the base layer model L0–L5, tags T-01–T-24.
2. Project knowledge, sampled by search, not read whole: the Terminology Freeze (G-D2-D3-H2), Building Paths v1.1 preface, Family E v2.0, the Placement Thread P2/P3 (hybrid anchored architecture), Security campaign G-C1, the formal spec (SSI-Minimal-Function-Specification-Formal.md), CVIN Native Sandbox Build methodology, Status Board 2026-08-18.

TASK A — Roots Lineage v1.1 (extend, do not rewrite):
- Add layers L6 (identity: identifiers, keys-as-identity, credentials, revocation) and L7 (application / I2I messaging and transaction).
- Add the identity-relevant lineage as T-I01 onward, dated, one paragraph each, same "what it provides / secured by" discipline: Kerberos, X.509/PKI 1988, PGP web-of-trust 1991, SSL/TLS 1995→1.3 2018, Diffie–Hellman ratcheting → OTR 2004 → Signal/X3DH/Double Ratchet 2013–16, Noise framework 2016, zero-knowledge proofs (GMR 1985; Schnorr ID 1989; Fiat–Shamir 1986; zk-SNARK/Groth16 2016; Bulletproofs 2018), pairing-based crypto (BLS 2001, CL 2002, BBS 2004 → BBS+), cryptographic accumulators (Benaloh–de Mare 1993; Camenisch–Lysyanskaya 2002), anonymous credentials (Idemix 2002, U-Prove), DHT-based naming (Namecoin 2011), W3C DID Core / VC-DM (2019–2022), DIDComm v2, Sidetree, AnonCreds, IEEE 1609.2 implicit certificates and butterfly keys (vehicular PKI, for the CAV grounding).
- Update the SVG to eight layers (L0–L7) with the identity lineage in a second timeline column. Keep colours and identifiers stable.

TASK B — Integration Scan (D3):
- Produce ONE table that places every artefact in the corpus (each project file), every T-/T-I primitive, every option O1–O18, every family A–F, and every programme solution on the L0–L7 stack. Columns: item · layer(s) · what it enables above · what secures it below · corpus source · tag(s).
- Assign SOL-01… to the solutions the programme has actually built or specified: local/native sandbox chain; public chain; public anchoring (hash/commitment on public chain); Besu QBFT public–private hybrid; LFDT stack (Indy/Aries/AnonCreds/Besu); the IMinimalSSI Set A/B/C functions; anything in P3's hybrid anchored architecture. One paragraph each: what it is, which layers it lives on, which BP- it will later be shown to address (leave BP numbers as ⟦placeholders⟧ for Prompt 2).
- Close with a "gaps in the map" list: primitives with no corpus artefact, artefacts with no primitive.

CONSTRAINTS: British spelling per the Terminology Freeze; no bare values — show dates with source; do not write thesis prose; no subagents; verify any date you are not sure of with one search and mark it. If you must cut, cut breadth of T-I entries, never the scan table.

OUTPUTS: claude_CVIN_SC_Roots_Lineage_R1_v1-1.md, claude_CVIN_SC_Roots_Lineage_R1_v1-1.svg, claude_CVIN_SC_Roots_Integration_Scan_R2_v0-1.md. Present all three. End with the HANDOFF block (≤400 words): files, tag ranges consumed, SOL- list with one-line definitions, five load-bearing decisions, open Q-R#.
```

---

## PROMPT 2 — The Main Document: I2I and Identity Stack with Breaking Points and Solutions (D2)

```
[PASTE HANDOFF BLOCK FROM PROMPT 1]

CVIN-SC, thread G-R1, Prompt 2 of 3. Inputs: the three Prompt-1 files (read fully) plus project knowledge by search as needed (G-C1 security campaign, Building Paths preface on finality/hash-on-chain/audit, P3 hybrid architecture, Pass 4 CAV grounding, Crux Compendium X1–X6).

WRITE claude_CVIN_SC_Roots_I2I_Identity_Stack_R3_v0-1.md — long form, narrative first, in this structure:

Part I · The crux. State in one page what a "secure and private I2I transaction or message" requires (authenticity, integrity, confidentiality, non-repudiation where wanted, unlinkability where wanted, availability, ordering) and what an identity system must add (binding a key to a subject, proving control, delegation, credential issuance/verification/revocation, recovery). Map each requirement to the layer that delivers it and the T-/T-I primitive that delivers it. This is the narrative spine; everything else hangs off it.

Part II · Layer by layer, L0–L7. For each layer: (a) what it delivers upward, in one paragraph; (b) the BREAKING POINTS, tagged BP-Lx-nn, each with attack, precondition, consequence upward, and the primitive/mechanism that closes it — cite the T-/T-I tag and, where the programme has built it, the SOL- tag. Minimum coverage: L0 eclipse/partition/Sybil; L1 key generation entropy, nonce reuse, hash breaks, quantum; L2 second-preimage on Merkle, chain reorg; L3 the 1/3 and 1/2 bounds, liveness vs safety, FLP, long-range attacks; L4 51%, selfish mining, fee-market failure, validator collusion in permissioned sets; L5 double-spend, replay, malleability; L6 key loss, issuer compromise, revocation latency window, correlation/linkability, confused deputy in delegation; L7 endpoint compromise, metadata leakage, oracle trust. Leave the NUMBERS to Prompt 3: write "bound given in PF-⟦n⟧" and let Prompt 3 fill it.

Part III · The trilemma and the solutions. Present decentralisation/security/scalability as the cost surface, then place SOL-01…SOL-n on it. For each SOL: which BP- it closes, which it accepts as residual, what it costs (latency tier, gas, governance). Make the public-anchoring and Besu QBFT hybrid the analytical centre, since that is what the programme built; local sandbox is the baseline, public chain the upper bound.

Part IV · From roots to identity transactions. Trace three concrete flows end-to-end down the stack: (1) createDID + first key rotation; (2) issue → present → verify a credential with selective disclosure; (3) revoke and observe the latency window. Each flow is a numbered sequence naming the layer and tag at every step.

FIGURES (SVG, each also referenced in text as FIG-R1…): FIG-R1 eight-layer stack with the I2I requirement arrows; FIG-R2 breaking-point heat-map (layers × attack classes, cell = BP tag); FIG-R3 trilemma surface with SOL- points placed; FIG-R4 hybrid-anchored architecture (Besu private + public anchor) with the trust boundary drawn; FIG-R5 the three flows as sequence diagrams down the stack; FIG-R6 the "who secures whom" dependency graph (T-/T-I nodes, edges = secured-by). Mobile-readable: viewBox ≤ 900 wide, ≥10pt text.

CONSTRAINTS: every claim of the form "X is secured by Y" carries a tag pair. No numeric bounds in this document — they belong to Prompt 3. British spelling; Terminology Freeze names (LFDT, QBFT, IMinimalSSI, Set A/B/C, Tier 1/2/3). No subagents. If length forces a cut, cut Part IV flow 3 before anything else and say so.

OUTPUTS: the .md plus six .svg files. End with the HANDOFF block: BP- tag ranges assigned per layer, the SOL- → BP- closure table in compact form, the list of "PF-⟦n⟧" placeholders Prompt 3 must fill (with a one-line spec of each: what quantity, what variables), open Q-R#.
```

---

## PROMPT 3 — Proofs, Bounds and Numbers (D5) and the Pass Record / Meta-Commentary (D4)

```
[PASTE HANDOFF BLOCK FROM PROMPT 2]

CVIN-SC, thread G-R1, Prompt 3 of 3. Inputs: R1, R2, R3 (read R3 Part II and the PF-placeholder list fully); G-B empirical rigour protocol; Pass-3 CEV ledger for the format; the formal spec for the twelve functions.

TASK A — claude_CVIN_SC_Roots_Proof_and_Bounds_R4_v0-1.md

§0 Notation. Define OUR symbols first (SYM-01…), each with name, meaning, units, and the standard symbol it maps to if one exists. Minimum set: key length k; effective entropy κ; number of identities n; address length a; hash output length h; honest fraction of consensus power α (PoW) and honest validator count f-of-N (BFT); block interval Δ; confirmation depth z; revocation-latency window W (already in the thesis notation — reuse, do not redefine); anchoring interval τ_a; adversary compute budget C; time horizon T. Then the standard equations we rely on, cited: birthday bound, Nakamoto's z-confirmation catch-up probability (whitepaper §11), the BFT n ≥ 3f+1 condition, the ECDLP generic-group bound, Grover/Shor cost estimates.

§1 Identity-creation collision bounds. PF-01 key-pair collision probability for n keys in a 2^κ space; PF-02 address collision under RIPEMD-160(SHA-256) with a=160; PF-03 DID collision for the programme's DID method; PF-04 "scale" statement: solve for the n at which collision probability reaches 10^-18, 10^-12, 10^-9 and express as vehicles × keys × rotations per year for the CAV fleet sizes used in Pass 4. Show the arithmetic; no bare values.

§2 Per-layer security bounds, one PF- per BP- placeholder from R3. Consensus: probability of reversal at depth z for α ∈ {0.6, 0.7, 0.9}; QBFT: minimum N for tolerated f, and the collusion probability model for a permissioned validator set of known size. Anchoring: the window between private-chain commit and public anchor as a function of τ_a and public-chain finality; express the residual reversibility. Revocation: bound W in terms of anchoring interval and propagation, and state what the hybrid buys versus public-only and local-only.

§3 Cost surface. Put the trilemma in numbers: latency, throughput, and gas/storage per identity operation for SOL-01… using the programme's own measurements where they exist (cite the trace/CEV row) and marked estimates where they do not.

§4 Sensitivity. For each PF-, list the variable that dominates it and what happens when we change the blockchain (Besu → public L2 → Indy). This is the abstraction hook: later documents change one variable and cite the PF- rather than rederiving.

§5 The PF- index table: tag · statement · variables · assumptions · status (DERIVED / MEASURED / ESTIMATED / STANDARD-RESULT) · which BP- it bounds · which SOL- uses it.

TASK B — claude_CVIN_SC_Roots_PassRecord_MetaCommentary_R5_v0-1.md, in the S3 five-part form used by the programme: version-control entry; methodology notes (what was read at source, searches run); corrections ledger KD-R#; unresolved register Q-R# / LIM-R#; meta-commentary MC-R# — each part closes with one load-bearing question the researcher must answer (the test: if the model can answer it, rewrite it). Also emit the CEV-R rows for every PF- of status DERIVED or MEASURED.

CONSTRAINTS: definitions first, derivations second, numbers last; every number traceable to an equation and inputs; flag any place where our own symbol collides with a thesis symbol. British spelling. No subagents.

OUTPUTS: R4 and R5 .md. End with a HANDOFF block for the SECOND PASS on R4 (definitions audit): the list of SYM- and PF- items whose definitions should be re-derived independently without reading R4 first, so the two derivations can be diffed.
```

---

## 3. Second pass (not one of the three; run when ready)

Prompt 3 hands off a definitions-audit list. The second pass on R4 re-derives each listed `PF-` blind (a fresh session, given only the `SYM-` table and the statement of what is to be bounded, not the prior derivation), then diffs. Discrepancies become `KD-R#` entries. This is the pattern you described: first pass unconstrained by our own definitions, second pass checks them.

## 4. What to do if a prompt runs out of room

Each prompt names its own cut order (Prompt 1: breadth of T-I; Prompt 2: Part IV flow 3; Prompt 3: §3 estimates before §1–§2 derivations). If a session still truncates, reply with **"continue from ⟦last tag written⟧"** and the same HANDOFF block — never re-issue the full prompt.
