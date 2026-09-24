# Internal Audit 01 — Drift From the Original Research Goals

**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Date:** 2026-09-24
**Scope:** trunk `nikhilprakash24/CVIN-SC-Implementation-SSI-DID`, branch
`claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy`
**Status:** first audit in a series. Findings are ranked by examiner risk.
**Companions:** `PROJECT_SUMMARY.md` (what exists), `AFTER_ACTION_REPORT.md`
(integration plan), `RESEARCH_THRUSTS_REPORT.md` (thrusts H1–H5).

---

## 0. Why this audit exists

The project has produced a great deal of implementation across three parallel
streams (this trunk, an earlier analysis lineage held in a git bundle, and
external notebooks). Volume creates a specific risk: the work drifts from the
questions it was started to answer, and the drift is invisible because every
session log reports "complete". This audit measures the trunk against the
goals **as they were first written**, then against what an examining committee
and the empirical-research community expect, and names what was missed.

The audit method is deliberately conservative:

1. Take the earliest goal statements in the repository (`README.md` research
   questions, hypothesis, and contributions; `CV2X_REALISTIC_ROADMAP.md`
   success criteria; `cv2x-testbed/V2_DESIGN.md` research questions).
2. For each, ask: is there **trunk-traceable evidence** (a script that runs
   here, today, and produces the number)? Assertions in session summaries do
   not count as evidence.
3. Compare the resulting picture against external yardsticks: UBC ECE MASc
   examination practice, ACM SIGSOFT empirical standards, the W3C DID test
   suite, SAE J2945/1, and two published comparative evaluations of DID
   methods.

---

## 1. Goal register: original statement → current evidence → verdict

### 1.1 Research questions (README.md, the canonical statement)

| # | Original question | Trunk evidence today | Verdict |
|---|---|---|---|
| RQ1 | How do the standards compare on **transaction cost, latency, and throughput**? | Gas for 4 ERC-1056 ops measured today (78,034 / 68,854 / 72,219 / 51,126). No latency-under-load or throughput measurement on the trunk. Only ERC-721, ERC-725, ERC-1056 have contracts here. | **Partially addressed.** Cost: 3 of 9 standards. Latency/throughput: not measured. |
| RQ2 | Which architecture gives the **strongest security guarantees for V2X**? | 10 use-case scripts and a PKI baseline exist. No attack-scenario results table on the trunk; the formal threat model (Dolev–Yao, A1–A4, G1–G8) is in the bundle lineage, not here. | **Not evidenced on trunk.** |
| RQ3 | Can blockchain identity achieve **full W3C SSI compliance** while meeting **MOBI VID**? | 89.6% on a self-authored 67-check list (verified today). MOBI VID V2 registry + provider exist. No external conformance run. | **Addressed, self-scored.** "Full" is not achieved (DID Core 75%) and the checker is not independent. |
| RQ4 | Is blockchain identity **viable for real-time safety-critical V2V**? | DID resolution 0.05 ms (today). VC verify timing not measured on trunk. No SUMO run producing latency distributions on trunk. | **Not evidenced on trunk.** |

### 1.2 The hypothesis

> "Lightweight blockchain identity standards (ERC-1056) can provide sufficient
> security and W3C compliance for vehicle identity management while
> maintaining performance suitable for real-time V2V safety applications,
> offering a viable alternative to centralized PKI systems."

This is a **compound** hypothesis with four conjuncts (security, compliance,
real-time performance, PKI-alternative). Compound hypotheses are a known
examiner target: they cannot be falsified cleanly, because failing one
conjunct is ambiguous about the whole. The thrusts document (H1–H5) already
decomposes it, which is the right move, but the README still presents the
compound form as the thesis claim. **The two must be reconciled** so the
thesis has one hypothesis structure throughout.

More importantly, the fourth conjunct, "viable alternative to centralized
PKI", requires a **measured PKI baseline**. `cv2x-testbed/identity/standard/pki_identity.py`
exists (442 lines), but no PKI-vs-blockchain comparison table is produced by
any script on the trunk. This is the single largest gap between the
hypothesis and the evidence.

### 1.3 Claimed contributions (README.md §Research Contributions)

| # | Claim | Audit finding |
|---|---|---|
| C1 | "**First comprehensive comparison of 9** blockchain identity standards for automotive" | The trunk's `1_blockchain-identity/` promises nine directories (ERC-721, 725, 735, 725xy, 1056, 1155, LSP8, 4337, CVIN-Combined). **Contracts exist for three** (721, 725, 1056); 725xy is notes only; **735, 1155, LSP8, 4337 and CVIN-Combined have no implementation on this trunk.** The nine-standard measurements exist only in the bundle lineage. Until merged, the headline contribution is not supported by the canonical repository. |
| C2 | "First working implementation" of real-time V2V + blockchain identity | Priority claims ("first") are hard to defend and invite a literature counter-example. At least one 2025 Springer chapter presents an SSI-based V2V authentication system (see §4). Reframe as "an open, reproducible implementation" rather than "first". |
| C3 | MOBI VID + W3C bridge | Supported (VID V2 registry, provider, VC layer). |
| C4 | Hybrid architecture | Design exists in `CVIN-SSI-ARCHITECTURE.md`; the CVIN-Combined contract is **not on the trunk**. |
| C5 | Open-source reproducible testbed | Undermined until today: the trunk **did not compile as received** (solc/OpenZeppelin mismatch, fixed in `b0934a8`) and the contract suite had 14 failing tests, since reconciled to 47/47. The reconciliation exposed three latent defects (unreachable wrapper functions, an NFT balance-accounting bug, a signing-scheme mismatch) that "✅ complete" session logs had hidden. Reproducibility is a property you demonstrate, not declare. |

### 1.4 Roadmap success criteria (CV2X_REALISTIC_ROADMAP.md)

| Criterion | Target | Trunk evidence | Verdict |
|---|---|---|---|
| BSM signing | < 100 ms | not measured on trunk | open |
| BSM verification | < 10 ms | not measured on trunk | open |
| Identity resolution | < 50 ms | 0.05 ms (in-process, no chain read) | met, but see §2.3 on what was measured |
| SUMO | 50+ vehicles | harness exists; no results file | open |
| Safety-app latency | < 100 ms end-to-end | not measured | open |
| Sybil prevention | yes | asserted via MOBI VID; no scenario result | open |
| Position-falsification detection | > 95 % | not attempted | **dropped silently** |
| Replay prevention | 100 % | not evidenced on trunk | open |
| Centralized-vs-MOBI VID gap | quantified | not produced | open |
| Privacy analysis | complete | not produced | **dropped silently** |
| Cost analysis | complete | partial (ERC-1056 only) | partial |
| Trust-model comparison | documented | `CVIN-SSI-ARCHITECTURE.md` covers it qualitatively | partial |

Two criteria were dropped without a recorded decision (position
falsification, privacy analysis). Dropping scope is legitimate in a MASc; not
recording the decision is not. Each dropped item needs a one-line entry in a
scope-change log with a reason, so the thesis can say "out of scope, because".

### 1.5 V2 design questions (cv2x-testbed/V2_DESIGN.md)

Ten questions were posed (7 DID methods in V2X latency; revocation vs CRL;
DID rotation privacy; 1000+ vehicles; safety-app impact; Sybil; PKI–DID
hybrid; ML misbehaviour; 5G NR-V2X). The trunk addresses none of them with a
results artifact. Most are PhD-scale. **They should be formally demoted to
"future work" in the thesis**, with the three that the built infrastructure
can actually answer (latency across methods, revocation vs CRL, 1000-vehicle
scaling) promoted into the experimental plan.

---

## 2. Findings ranked by examiner risk

### F1 — The headline claim is not supported by the canonical repository (critical)
Nine standards are claimed; three are implemented on the trunk. The
nine-standard results live in an unmerged bundle. A committee member who
clones the repository will find the gap in under ten minutes. **Action:** merge
Direction B (bundle) before any chapter cites nine standards, or rewrite the
claim to match the trunk.

### F2 — No PKI baseline result, yet the hypothesis is "alternative to PKI" (critical)
The comparison the hypothesis requires is not produced by any script. The
PKI provider exists; the experiment does not. **Action:** a single script that
runs identical operations through `pki_identity.py` and `erc1056_provider.py`
and writes one CSV is the highest-value experiment remaining.

### F3 — The same quantity is reported with three different values (high)
Identity-resolution latency appears as "50–100 ms" (`docs/thesis/README.md`
RQ1 answer), "~0.8 ms" (`RESEARCH_THRUSTS_REPORT.md`), and 0.05 ms (measured
today). All three are probably "true" for different things (chain RPC vs
cached vs in-process). An examiner will read this as carelessness. **Action:**
define the measurement conditions once (what is resolved, from where, cache
state), and let only trunk-generated numbers appear in chapters.

### F4 — Reproducibility was asserted while the build was broken (high)
Fixed today (build, then 47/47 tests), but the lesson matters: every session
summary marked components "✅ complete" while the contract project could not
compile with a fresh install, and the ERC-1056 wrapper's service-endpoint and
delegate functions were unreachable by construction. The wrapper is the
substrate that H1 favours; a defect there that no test could reach is the
strongest possible argument for CI gating. **Action:** make the CI workflows that already exist
(`test-contracts.yml`, `benchmark.yml`, `w3c-compliance.yml`) actually run on
the trunk and gate on green. Reproducibility then becomes a badge, not a
sentence.

### F5 — Compliance is self-graded (high)
89.6% comes from a checker the project wrote. The W3C DID Working Group
maintains a public conformance test suite with 46 submitted implementations
and an auto-generated implementation report; the VC Data Model has an
equivalent. **Action:** run the resolver against the W3C DID test suite and
report *that* number alongside the internal one. If the external suite cannot
be run, say why in the limitations section. Note also that the internal
checker targets VC Data Model **v1.1**, while the project elsewhere claims
**v2.0**; pick one and state it.

### F6 — The compound hypothesis has not been decomposed in the primary text (medium)
See §1.2. The thrust document has the decomposition; the README and the
thesis README do not. One structure, everywhere.

### F7 — Real-time claims lack a defined latency budget (medium)
SAE J2945/1 fixes the BSM cadence at 10 Hz (100 ms inter-message) and defines
an end-to-end bound for safety applications; sub-cases (e.g. pre-crash) are
tighter. The project's "< 100 ms end-to-end" target is reasonable but is
never derived from the standard in the text, and the measured quantity
(in-process resolution) is not the quantity the standard bounds
(receive → verify → trust decision). **Action:** write the budget derivation
once (chapter 3), then measure the pipeline that the budget constrains.

### F8 — Statistics are absent (medium)
Gas on a deterministic EVM is exact, so confidence intervals are not needed
*for gas*. Latency is not deterministic. Any latency figure in a chapter needs
N, median, p95, and the environment. The V2 design promised "statistical
validation"; nothing on the trunk delivers it.

### F9 — Threats to validity are written after the fact (medium)
The empirical-software-engineering community's own review of practice finds
threats to validity are "mostly considered as an enforced afterthought rather
than an active concern of the research design". This project matches that
pattern: `RESEARCH_AUDIT.md` (bundle lineage) lists threats, but none of the
experiment scripts were designed around them. **Action:** for each of H1–H5,
pre-register the threat you are controlling *in the script header*.

### F10 — Scope changes are not logged (low, but cumulative)
Position-falsification detection and privacy analysis vanished between the
roadmap and the trunk. A one-file scope-change log with date and reason
protects the candidate at the defence.

---

## 3. What a UBC ECE MASc examination will apply pressure on

The UBC ECE MASc thesis examination is a supervisor, one committee member,
and a chair (who also examines), with a presentation of at most 30 minutes
followed by 15–20 minutes of questions per examiner, and the thesis must be
with the committee at least one week before. Three examiners, roughly an hour
of questions, on a document read cold. The questions that this audit
predicts, given the current state:

1. "You say nine standards. Show me the ERC-735 contract." (F1)
2. "Your hypothesis says 'alternative to PKI'. Where is the PKI number?" (F2)
3. "Resolution is 50–100 ms on page 12 and 0.05 ms on page 40. Which?" (F3)
4. "Who wrote the compliance checker?" (F5)
5. "What does 100 ms mean here, and which part of it did you measure?" (F7)
6. "How many runs is that latency figure, and what is the spread?" (F8)
7. "Why did privacy analysis leave the scope?" (F10)
8. "What is new relative to Fdhila et al. and the W3C rubric-based
   evaluations?" (§4)

Every one of these is answerable with work the infrastructure already
supports. None is answerable from session summaries.

---

## 4. Position against comparable work (differentiation check)

Two published comparative evaluations of DID methods define the field's
baseline:

- **Fdhila, Stifter, Kostal, Saglam, Sabadello (BPM 2021 Blockchain Forum),
  "Methods for Decentralized Identities: Evaluation and Insights"** — evaluates
  DID methods against the categorisation in the **W3C DID Method Rubric**.
- **Schäffner, "Analysis and Evaluation of Blockchain-based Self-Sovereign
  Identity Systems"** (master's thesis) — literature-driven criteria, then a
  comparative evaluation of representative DID methods.

Both are **criteria/rubric-based**, not measurement-based, and neither is
domain-constrained. That is exactly the space this thesis can own:
**measured** cost/latency **under an automotive constraint** (J2945/1
cadence, MOBI VID lifecycle events), with a PKI baseline. Two implications:

1. The thesis should **adopt the W3C DID Method Rubric** as the qualitative
   axis (so it is comparable to prior work) and add the **measured** axis as
   the contribution. Not using the rubric at all makes the qualitative
   comparison look home-made next to Fdhila et al.
2. The "first" claims (C1, C2) should be replaced with "measured" and
   "domain-constrained" claims, which are both defensible and more accurate.
   A 2025 Springer chapter already presents an SSI-based authentication
   system for V2V; the differentiator is not existence, it is measurement
   breadth and reproducibility.

The blockchain-benchmarking literature (BLOCKBENCH and its successors)
measures throughput, latency, scalability and fault tolerance as distinct
dimensions. RQ1 names throughput; nothing on the trunk measures it. Either
measure it (a Hardhat local node can produce a transactions-per-second figure
for each registry) or remove the word from RQ1.

---

## 5. Methodological standards the thesis should cite and follow

- **ACM SIGSOFT Empirical Standards** — the community's evidence standards;
  their benchmarking discussion is the closest thing to a checklist for
  performance comparisons. Adopt: explicit workload definition, environment
  specification, repetition, and artifact availability.
- **Threats to validity as design input** (ESEM 2024) — construct, internal,
  external, conclusion validity, each addressed *in the experiment design*.
- **W3C DID test suite / implementation report** — external conformance, and
  the model for how conformance is reported (every normative statement tested,
  ≥2 independent implementations).
- **SAE J2945/1** — the source of the timing budget; derive, do not assume.
- **W3C DID Method Rubric** — the qualitative comparison frame used by prior
  work.

---

## 6. Recommendations, in order

| Priority | Action | Closes |
|---|---|---|
| 1 | Merge the bundle lineage (nine-standard contracts + results) onto the trunk, or rewrite C1 | F1 |
| 2 | Write and run the PKI-vs-ERC-1056 identical-operations script; one CSV | F2 |
| 3 | Create `docs/MEASUREMENT_CONDITIONS.md`; purge unsourced numbers from chapter drafts | F3 |
| 4 | Make the three CI workflows run green on the trunk | F4, C5 |
| 5 | Run the W3C DID test suite against the resolver; report externally and internally | F5 |
| 6 | Unify the hypothesis structure (H1–H5) across README, thesis README, chapters | F6 |
| 7 | Derive the J2945/1 budget in chapter 3; measure the full verify pipeline under SUMO with N, median, p95 | F7, F8 |
| 8 | Add a `SCOPE_CHANGES.md` log; record the two silent drops with reasons | F10 |
| 9 | Adopt the W3C DID Method Rubric as the qualitative axis | §4 |
| 10 | Replace "first" with "measured, domain-constrained, reproducible" in contribution claims | C1, C2 |

Items 2, 3, 4 and 8 need no external input and can be done immediately. Item
1 needs the bundle. Item 5 needs a decision on which resolver interface to
expose to the suite.

---

## 7. What was *not* missed (so the audit is balanced)

- The decomposition into H1–H5 with a method per thrust is correct and ahead
  of most MASc proposals.
- The VC layer is a real, tested implementation (28/28), with a defensible
  proof choice (EIP-191 ECDSA as Data Integrity) and an honest selective-
  disclosure limitation.
- MOBI VID I/II mapping onto VCs is a genuine bridge that prior comparative
  work does not attempt.
- The decision to measure the CVIN-Combined hybrid as a first-class candidate
  (rather than only as a conclusion) is methodologically sound.
- The repository now has a durable remote and a versioned audit trail, which
  is the precondition for everything above.

---

## 8. Sources consulted for this audit

- UBC ECE, Master of Applied Science (MASc) programme and thesis-examination
  practice — https://ece.ubc.ca/graduate/programs/master-applied-science/ ;
  https://www.grad.ubc.ca/prospective-students/graduate-degree-programs/master-of-applied-science-electrical-computer-engineering
- ACM SIGSOFT Empirical Standards — https://www2.sigsoft.org/EmpiricalStandards/
- "Benchmarking as Empirical Standard in Software Engineering Research" (EASE 2021) — https://dl.acm.org/doi/10.1145/3463274.3463361
- "Threats to Validity in Software Engineering – hypocritical paper section or essential analysis?" (ESEM 2024) — https://dl.acm.org/doi/10.1145/3674805.3686691
- W3C DID Test Suite and Implementation Report — https://github.com/w3c/did-test-suite ; https://w3c.github.io/did-test-suite/
- W3C Decentralized Identifiers (DIDs) v1.0 — https://www.w3.org/TR/did/
- SAE J2945/1, On-Board System Requirements for V2V Safety Communications — https://saemobilus.sae.org/content/j2945/1_201603
- Fdhila et al., "Methods for Decentralized Identities: Evaluation and Insights" (BPM 2021 Blockchain Forum) — https://eprint.iacr.org/2021/1087
- Schäffner, "Analysis and Evaluation of Blockchain-based Self-Sovereign Identity Systems" (master's thesis) — https://github.com/Bartkeeper/thesis
- "An Authentication System Based on Self-sovereign Identity for V2V Communications" (Springer, 2025) — https://link.springer.com/chapter/10.1007/978-3-031-81928-5_2
- "Self-sovereign identity on the blockchain: contextual analysis and quantification of SSI principles implementation" (Frontiers in Blockchain, 2024) — https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2024.1443362/full
- "A Survey on Decentralized Identifiers and Verifiable Credentials" (arXiv 2402.02455) — https://arxiv.org/html/2402.02455v1
- BLOCKBENCH: A Framework for Analyzing Private Blockchains (SIGMOD 2017) — https://dl.acm.org/doi/10.1145/3035918.3064033

*Next audit (02) should cover the bundle lineage after merge: whether the
nine-standard gas table, the scaling model and the dominance proof survive
re-execution on the trunk.*
