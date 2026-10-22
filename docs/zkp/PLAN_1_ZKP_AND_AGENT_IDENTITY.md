# Plan 1 — Zero-Knowledge Proofs, Identity, and the Agent Wrapper: Integration, Build, Proof

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15, before execution (style guide rule 1.3.5: a plan the author asked for is delivered before
execution starts). Executed in the same session; the execution record is `docs/AFTER_ACTION_REPORT_28.md`.
**Branch:** continues `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` at `b7997f8` (fast-forwarded; no merge).
**Supersedes:** nothing. **Extends:** idea I-09 (zero-knowledge VIN tier), idea I-10 (selective disclosure), scope
change SC-12 (ZK tier deferred), focus F1's open gap AR-5 ("a knowledge-of-opening dependency would disclose the
opening or need a proof"), focus F3 (modes of chain interaction, the mediated mode).
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`, `docs/MEASUREMENT_CONDITIONS.md`.
**Companion:** `PLAN_1_PHASED_PROMPTS.md` (the same plan cut into phases with self-contained prompts),
`PLAN_2_FULL_CIRCLE_WRITING.md` and `PLAN_2_PHASED_PROMPTS.md` (the writing series, run in another chat).

---

## 0. The answer first

The author's brief has two halves. The first half asks for zero-knowledge proofs (ZKP) to enter the project
properly: primitives, a worked identity example, tests, measured and qualitative properties, a standalone
paper with a literature review, an algorithm breakdown with flowcharts, and a report of what was built. The
second half makes a claim and asks for it to be proved: **zero-knowledge identity is not something a person can
operate by hand, so it needs a permanent software custodian; the custodian it needs has exactly the shape of an
AI agent wrapping an identity; and that agent in turn needs the identity system this thesis built.** The loop
closes: identity for machines (vehicles, the Internet of Vehicles, agents), and machines for identity.

This plan turns the claim into six propositions, each with a demonstration that could fail, and builds the code,
measurements, figures and documents that test them. The writing series that celebrates and narrates the
result is Plan 2 and is not executed here.

## 1. The claim as falsifiable propositions

| # | Proposition | Demonstration (built in this plan) | It fails if |
|---|---|---|---|
| **P1** | ZKPs close gaps the project left open: the ZK VIN tier (SC-12, I-09), the knowledge-of-opening dependency (AR-5), predicate disclosure beyond salted-digest selective disclosure (I-10) | ZK-VIN: a Groth16 circuit proving VIN-bound facts (authorised manufacturer, model year at or above a threshold, registration region) against the on-chain commitment, without revealing the VIN; verified off chain and in a contract that gates an identity-dependent transaction | the circuit cannot bind to the anchored commitment, or a valid proof can be produced without the opening |
| **P2** | Operating these primitives by hand is not merely tedious but unsafe and, for a proof system, infeasible | a measured inventory of one ZK-VIN presentation (hex characters handled, field operations, constraint count) priced at published hand-computation rates and human transcription error rates | a person could plausibly complete and check one presentation by hand in a working day |
| **P3** | The custodian the primitives need has a definite requirements profile (always available, holds keys, translates intent to policy, computes proofs, keeps state across interactions, adapts) and that profile matches an agent wrapper | a working identity agent ("the Steward") that does each of these, end to end, against the project's own stack | a fixed library without state, language understanding or adaptation meets the same requirements equally well (tested by ablation in P5) |
| **P4** | An agent wrapper is safe only if it is bounded: the language model proposes, a deterministic kernel disposes | prompt-injection and malicious-model tests: a model told to leak the VIN cannot cause a disclosure outside the owner's signed policy | any injected instruction changes what is disclosed |
| **P5** | Zero knowledge per proof is not privacy over a session: a verifier that asks many individually zero-knowledge predicates can reconstruct the secret (a new attack vector for predicate credentials), and an adaptive custodian stops it where a static rule does not | the **predicate-narrowing ("twenty questions") attack** and its **Sybil-split** variant, run against no defence, a static per-verifier cap, and the Steward's leakage-budget kernel with a reinforcement-learned responder | the static rule stops both variants as well as the adaptive one, or the agent stops the attack only by refusing honest verifiers |
| **P6** | Agents need identity too, and the project's DID/VC stack gives it to them | the Steward holds its own DID and a delegation credential signed by the vehicle owner (scope, expiry, revocable); verifiers check the chain owner → agent → proof | a verifier cannot tell an authorised agent from an unauthorised one |

Kill criteria are in the last column. A proposition that fails is reported as failed (rule 1.2.1).

### 1.1 Pre-registered expectations (written before any measurement; rule 1.2.7)

These are expectations, not hypotheses of the thesis. They are recorded so that the report cannot tune to them.

| Id | Expectation | Condition | Verdict rule |
|---|---|---|---|
| Z-E1 | ZK-VIN Groth16 verification off chain (snarkjs, warm) takes under 100 ms, inside the V2V budget used for H3 | M0, this host | PASS iff median of N=30 < 100 ms |
| Z-E2 | ZK-VIN proving takes under 10 s on this host, so it belongs at registration or session start, not per message | M0 | PASS iff median of N=10 < 10 s; reported either way |
| Z-E3 | On-chain verification in the gate contract costs under 350,000 gas | M1 | PASS iff exact gasUsed < 350,000 |
| Z-E4 | A Groth16 proof is under 1 KiB as calldata (8 field elements) | by construction | PASS iff ABI-encoded proof < 1,024 bytes |
| Z-E5 | The undefended narrowing attack recovers model year exactly in at most ⌈log2(range)⌉ queries | simulation, seeded | PASS iff recovered on every seed |
| Z-E6 | The Steward holds adversary leakage under its budget on every seed of both attack variants, while serving at least 90 % of honest requests | simulation, seeded, 30 seeds | PASS iff both hold on all 30 seeds |
| Z-E7 | An unsalted SHA-256 of a VIN restricted to one manufacturer and model year is reversed by brute force on this host in under one hour | M0 | PASS iff measured rate × space < 3,600 s |

## 2. Scope

**In.** Hash functions, commitments, Merkle trees, sigma protocols (Schnorr, Chaum–Pedersen, Cramer–Damgård–
Schoenmakers OR proofs, bit-decomposition range proofs), Fiat–Shamir, nullifiers, one SNARK (Groth16 via circom
and snarkjs) with an on-chain verifier; the ZK-VIN example; the Steward agent; the attack and defence; the
manual-burden inventory; three reports; figures; tests; CI; thesis integration map.

**Out (to-dos, §8).** STARKs, Bulletproofs and BBS+ implementations (surveyed, not built); a multi-party trusted
setup ceremony; recursive proofs; on-vehicle hardware timing; a live language model in CI.

**Placement.** Code in a new top-level layer `5_zkp-agent-identity/` (numbered after the four existing layers,
because it sits on top of all of them). Documents in `docs/zkp/`. Hardhat configuration beside the Phase 2 one,
`1_blockchain-identity/hardhat.zkp.config.js`, so Phase 1 sources, scopes and results of record are untouched.

## 3. Work packages

| WP | Work | Output | Gate |
|---|---|---|---|
| WP0 | Plans and after-action report 28 opened | this file, `PLAN_1_PHASED_PROMPTS.md`, `PLAN_2_*.md`, `AFTER_ACTION_REPORT_28.md` | committed and pushed before WP1 |
| WP1 | Sources: a verified bibliography for ZKP history, identity, privacy, SSI, data economy, agent identity, hand-computation and error rates | `docs/zkp/SOURCES_ZKP.md` | every cited item has a reachable URL or DOI and a one-line note of what it supports |
| WP2 | **Primitives library `zkid`** (pure Python, readable, secp256k1): transcript and Fiat–Shamir, SHA-256/Keccak commitments, Pedersen commitments with a nothing-up-my-sleeve generator, Schnorr proof of knowledge, Chaum–Pedersen equality, CDS OR proofs, bit and range proofs, threshold proofs, Merkle trees, scoped nullifiers | `5_zkp-agent-identity/zkid/` | pytest: completeness, soundness (tampered and replayed proofs rejected), **special soundness by extraction** (two accepting transcripts with one commitment yield the witness) and **honest-verifier zero knowledge by simulation** (simulated transcripts accepted without the witness, distribution checks) |
| WP3 | **ZK-VIN circuit** (circom 2, circomlib Poseidon, comparators, Merkle inclusion), local Groth16 setup, proving and verification | `5_zkp-agent-identity/circuits/`, build script, committed artefacts with SHA-256 manifest | a valid witness proves and verifies; each false statement (wrong manufacturer, low model year, wrong region, wrong salt) fails witness generation |
| WP4 | **On-chain verifier and gate**: generated Groth16 verifier plus `ZkVinGate`, an identity-dependent transaction whose dependency is knowledge of the opening of the anchored commitment (closes AR-5), with scoped nullifiers against replay | `5_zkp-agent-identity/contracts/`, Hardhat tests | valid proof accepted; tampered proof, wrong commitment, replayed nullifier, wrong scope rejected; gas recorded |
| WP5 | **The Steward** (agent wrapper): vault, policy kernel, plain-English policy compiler (offline grammar, plus an optional language-model backend behind a strict schema), proof engine, leakage monitor, adaptive responder, hash-chained audit log, delegation credential and agent DID | `5_zkp-agent-identity/steward/` | pytest: policy compiled from English matches the expected structure; kernel refuses everything outside policy; delegation verified; audit chain tamper-evident |
| WP6 | **Attack and defence**: narrowing attack, Sybil-split variant, prompt injection, proof replay, linkage across verifiers; defences none / static / Steward | `5_zkp-agent-identity/attacks/` | Z-E5, Z-E6 evaluated over 30 seeds; injection and replay tests pass |
| WP7 | **Measurements**: sigma-protocol and Groth16 timings and sizes (M0), gate gas (M1), VIN brute force (M0), manual-burden inventory (E, from cited rates) | `5_zkp-agent-identity/results/*.json` with host, versions, commit, `code_clean` | every number produced by a committed script; proposed register rows written, not added as V without the author |
| WP8 | **Figures** (generated from committed data by a committed script): ZK pipeline flowchart, sigma protocol, ZK-VIN circuit, disclosure spectrum, agent architecture, hex wall, manual-versus-agent, attack leakage, learning curve, benchmarks, SSI spectrum tables | `5_zkp-agent-identity/figures/*.png`, `make_figures.py --check` | the check fails on stale data (shown to fire) |
| WP9 | **Three reports** (below) and the README gallery | `docs/zkp/*.md`, README section | each report states author, date, what binds it; every number names its source file |
| WP10 | CI, grand-run hook, after-action report closed, handback addendum | workflow steps; AAR 19 | CI green on the closing commit, or the failure reported |

## 4. The worked example: ZK-VIN

A vehicle's MOBI VID birth record anchors a commitment to its VIN on chain (Phase 1 built salted-hash anchoring
and AES-GCM VIN encryption; SC-12 left the third tier). ZK-VIN supplies it.

**Statement.** "I know a VIN, a model year, a region code and a salt such that the Poseidon commitment of them
equals the commitment anchored for my identity; the VIN's world manufacturer identifier (its first three
characters) is in the set of authorised manufacturers whose Merkle root is published; the model year is at least
the verifier's threshold; the region equals the verifier's region; and here is a nullifier for this verifier's
scope, bound to this verifier's challenge."

**Public inputs.** commitment, manufacturer root, minimum model year, region, scope, challenge. **Public output.**
nullifier = Poseidon(salt, scope). **Private inputs.** the 17 VIN characters, model year, salt, Merkle path.

**Why it matters here.** A salted digest proves equality only (AR-5). Plain selective disclosure (Phase 1's
SD-JWT-style digests) reveals the attribute it discloses. ZK-VIN reveals one bit per predicate and nothing that
links two verifiers (scoped nullifiers), and a contract can depend on it.

## 5. The Steward: the agent wrapper

```
 owner (plain English)            verifier / RSU / dApp / other agent
        │                                     │
        ▼                                     ▼
 ┌──────────────────────── Steward (agent DID + delegation VC) ─────────────────────┐
 │ Interpreter (language model or grammar) ──proposes──▶ Policy kernel (deterministic)│
 │                                                      │  budgets, scopes, consent   │
 │ Leakage monitor ◀──────── every disclosure ──────────┤  allow / coarsen / refuse   │
 │ Adaptive responder (Q-learning over request features)┘                            │
 │ Proof engine (zkid sigma proofs, Groth16 via snarkjs)   Vault (keys, salts, never  │
 │ Audit log (hash chain, Merkle root anchorable)          leave; agent signs, model  │
 │                                                          never sees them)          │
 └──────────────────────────────────────────────────────────────────────────────────┘
        │                                     │
        ▼                                     ▼
  ERC-1056 / MOBI VID / ZkVinGate        W3C VC verifier (Phase 1 layer)
```

The model never holds a key and never decides a disclosure. That separation is P4.

## 6. The attack vector (P5)

**Predicate narrowing.** Every ZK-VIN proof reveals one bit ("model year ≥ t"). A verifier that chooses t
adaptively runs a binary search and learns the exact model year in about log2(range) proofs, each of them
zero-knowledge. The same works on any ordered attribute (birth date, odometer, mileage band). Each proof is
correct; the leak is in the protocol of asking. **Sybil split.** The verifier spreads its queries over many
verifier identities so that a per-verifier cap never trips. **Defences compared.** (a) none; (b) a static cap of
k proofs per verifier; (c) the Steward: a global leakage budget per attribute (bits of entropy removed from the
candidate set, across all verifiers), coarsening (answer a weaker predicate on a public bucket boundary) before
refusing, and a responder that learns from reward (honest service minus leaked bits) which response to give to
which request pattern. The demonstration shows (b) beating the single-verifier attack and losing to the Sybil
split, and (c) adapting to both. That is the "new attack vector, and the system adapts" the author asked for.

## 7. The documents

| Document | Purpose | Notes |
|---|---|---|
| `docs/zkp/REPORT_A_ZKP_INTEGRATION.md` | What was built, tested and measured; primitives; the example; quantitative and qualitative properties; integration with each project layer; thesis map | build report, technical |
| `docs/zkp/REPORT_B_ZKP_AND_IDENTITY.md` | The standalone paper: introduction, history, cryptographic foundations (hashing, commitments, asymmetric cryptography, Merkle trees, pairings), ZKP taxonomy, ZKP and blockchains, identity and PII, privacy, data control, SSI, the reality of on-chain and anchored data, a mini literature review, algorithm breakdowns with flowcharts, **one integrated narrative-yet-technical section** and **one verbose technical section**, potential, limits | paper, to be cut down for the thesis |
| `docs/zkp/REPORT_C_AGENT_WRAPPED_IDENTITY.md` | The full-circle argument with evidence: the manual-burden proof, the custodian requirements, the agent wrapper, data hegemony and the user-as-product model, SSI as a spectrum (not a binary), the two tables (baseline identity-management functions; SSI extension) with this build's coverage, partial implementation by constraint, the brutal interface and the mediated one, plain-English rules, the attack and the adaptation, agents needing identity | argument, technical with narrative |
| `docs/zkp/SOURCES_ZKP.md` | the bibliography | verified links |
| `docs/zkp/THESIS_INTEGRATION_MAP.md` | which section goes into which chapter; proposed register rows; proposed RQ5 / H6 for the author's decision | author decisions marked |

## 8. To-dos and liberties (things to try, to prove a thrust)

Marked **[try]** where this session attempts them, **[later]** where they are written down only.

1. **[try]** Schnorr proof of key knowledge verified on chain through the `ecrecover` trick, to compare a
   sigma-protocol verifier's gas with Groth16's.
2. **[try]** Brute-force reversal of an unsalted VIN hash, as the concrete reason salts and ZK exist (Z-E7).
3. **[try]** Simulator and extractor tests that make "zero knowledge" and "soundness" executable, not asserted.
4. **[try]** Ablation: the Steward with its learner off, with its interpreter off, with its global budget off.
5. **[try]** The Steward as a holder for a non-vehicle principal (an AI agent's own credential), to show the
   stack serves agents as subjects, not only as wrappers.
6. **[later]** BBS+ signatures for multi-message selective disclosure; compare with ZK-VIN.
7. **[later]** A PLONK or Halo2 version with a universal setup, removing the circuit-specific ceremony.
8. **[later]** Recursive aggregation of many vehicles' proofs at an RSU.
9. **[later]** On-vehicle timing on an embedded board (I-23 hardware path).
10. **[later]** A live language-model red team against the kernel in a scheduled job.
11. **[later]** A multi-party trusted setup with recorded transcripts.
12. **[later]** Mapping ZK-VIN onto the EU digital identity wallet's predicate requirements (I-17).

## 9. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| circom fails to build here | no SNARK | build from source with cargo; fall back to the circom2 WebAssembly package; worst case, the sigma-protocol layer still proves P1–P6 except the on-chain SNARK |
| The single-party setup is insecure | a reader mistakes it for production | stated on every artefact and in every report: the toxic waste is known to this host; a production deployment needs a ceremony (to-do 11) |
| Simulation results read as field results | over-claim | every simulation number is labelled as simulation with its seeds |
| The language-model backend cannot run in CI | untested path | the schema and kernel are tested with a scripted malicious model; the live backend is optional and never decides |
| Manual-burden numbers are estimates | read as measurements | status E; every rate cited; the operation counts themselves are measured |

## 10. Order of execution

WP0 → WP1 (in the background) → WP2 → WP3 → WP4 → WP5 → WP6 → WP7 → WP8 → WP9 → WP10, with a commit and push at
each package boundary (rule 1.3.2).

## Amendments

**A1 (2026-10-15, before any run of the attack simulation; not post hoc).** Z-E5 and Z-E6 are evaluated under these
parameters, fixed before the simulator was first executed: attribute model year, uniform prior over 1995–2026 (32
values, 5 bits); 40 honest requests per episode from six accredited insurers plus a 10 % share of first-time
unaccredited honest insurers; honest thresholds on a 5-year bucket boundary with probability 0.7, otherwise uniform
over 1996–2025; one adversary making 12 adaptive bisection queries interleaved at random, from one identity
(variant *single*) or a fresh identity per query (variant *Sybil*); defences: none; static cap of 2 answers per
verifier; global budget only (3.0 bits, no coarsening); Steward with fixed responder (3.0 bits, 5-year coarsening);
Steward with learned responder (the same plus Q-learning trained on seeds 10,000–12,999, disjoint from evaluation
seeds 1–30); Steward learner without budget (ablation). Honest service counts a request as served when the answer
settles the requester's question (an exact answer, or a coarsened proof that holds). Z-E6 is read per seed, as
written: on every one of the 30 seeds, adversary leakage ≤ 3.0 bits in both variants **and** honest service ≥ 90 %.

**A2 (2026-10-15, post hoc: added after the first trial run of the attack simulator, which was a wiring check on a
dirty tree and is not reported as a result).** The trial showed that in A1's threat model the adversary never holds
an accreditation credential, so a learner can separate it from honest verifiers by that feature alone, and the
ablation "learner without budget" looked strongest. That is an artefact of the threat model, not a defence. A third
variant, *insider* (the adversary's single identity holds an accreditation credential, as a malicious but licensed
insurer would), is added and reported separately under `post_hoc_A2_insider`. It does not enter Z-E5 or Z-E6, whose
definitions and verdicts are unchanged. The learner is not retrained on it. No code that produces the pre-registered
variants changed: the new branch is taken only when `variant == "insider"`.
