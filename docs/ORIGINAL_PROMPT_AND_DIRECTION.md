# Original Prompt and Direction — What This Research Was Asked to Be

**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Compiled:** 2026-09-30, from the repository history and the author's directives
across the working sessions
**Purpose:** one place that records, verbatim where possible, (A) the research
direction as it was first written, (B) the working directives the author gave for how
the work is to be done, and (C) how each has been carried forward — so that any later
reader (examiner, collaborator, a fresh session) can check the current work against
the original intent rather than against a paraphrase of it.

The research ideas, hypotheses, thrusts and design decisions below are the author's.
The tooling implemented, measured and documented against them.

---

## A. The research direction, as first written

### A.1 The sandbox that started it — `CVIN-sandbox-fullstack-completefunc-guide.md`, first commit `b23bc4c` (2025-11-10)

> "…a two stage sandbox is the most effective approach … The executable Python code
> placeholder is for both an LLM-interface as well as the off-chain interaction
> components of the identity system. Hence the two stages of the sandbox and inclusion
> of cloud/db/api calls to represent generically a call to read something like a
> credential or identity on- or off-chain and then either do something on-chain … or
> something off chain (… the base crux or kernel case of verified secure communication
> using a verifiable identity)."

Stages 0–10 as listed there: requirements → basic sandbox → Web3 → database → cloud →
generic API hook → integration → LLM → custom LLM → unified base case → presentation
"to build and test anything necessary … (such as the 6 implementation variations of
CVIN-ID)".

### A.2 The first testbed research questions — `cv2x-testbed/README.md`, commit `24b60c4` (2025-11-10)

> 1. How does DID-based authentication compare to PKI in terms of latency?
> 2. What is the overhead of blockchain queries vs CRL checks?
> 3. How do privacy mechanisms compare (pseudonym certificates vs DIDs)?
> 4. What is the impact on network performance?

### A.3 The V2 mission — `cv2x-testbed/V2_DESIGN.md`, commit `3143dea` (2025-11-10)

> "…transforming it from a proof-of-concept into a **research-grade platform** suitable
> for a university Connected Vehicles Lab."

with the named V1 gaps: no real traffic simulation (SUMO), oversimplified channel
model — and ten V2 research questions (seven DID methods in V2X latency; gas at scale;
revocation vs CRL; DID-rotation privacy; 1000+ vehicles; safety-app impact; Sybil;
PKI–DID hybrid; ML misbehaviour; 5G NR-V2X).

### A.4 The roadmap mission and research questions — `CV2X_REALISTIC_ROADMAP.md` (2025-11-10)

> "Build a comprehensive testbed that demonstrates how **vehicle identity systems**
> (centralized PKI vs blockchain-based MOBI VID) integrate with **real CV2X protocols**
> for safety-critical connected vehicle applications."

> 1. **Performance**: How much slower is blockchain identity vs centralized? —
>    Hypothesis: 10–100× slower for writes, similar for reads.
> 2. **Security**: Does MOBI VID prevent more attacks than PKI? — Hypothesis: Yes,
>    prevents Sybil and improves misbehavior tracking.
> 3. **Privacy**: Does blockchain expose more data than centralized? — Hypothesis: No,
>    VIN encryption prevents exposure.
> 4. **Scalability**: Can MOBI VID handle 1000s of vehicles? — Hypothesis: Off-chain
>    caching enables scale.
> 5. **Trust**: Do drivers trust blockchain more than central authority? — User study
>    (future work).

Success criteria: BSM signing < 100 ms; BSM verification < 10 ms; identity resolution
< 50 ms; SUMO 50+ vehicles; safety-app latency < 100 ms end-to-end; Sybil prevention;
position-falsification detection > 95 %; replay prevention 100 %; misbehaviour
reporting; centralized-vs-MOBI gap quantified; privacy analysis; cost analysis;
trust-model comparison.

### A.5 The MOBI VID direction — `MOBI_VID_RESEARCH.md`, `MOBI_VID1_TECHNICAL_SPEC.md`, `MOBI_VID2_SSI_DESIGN.md` (2025-11-10)

ERC-1056 as the base DID method; VID I as the immutable birth-certificate anchor tied
to the VIN with three-tier VIN privacy (hash on-chain, encrypted off-chain, ZK proof);
VID II as the lifecycle log (10 event types, 8 issuer roles) issued as W3C Verifiable
Credentials; a centralized registry with feature parity as the control baseline; ten
lifecycle use cases; a W3C compliance checklist.

### A.6 The thesis statement — `README.md`, commit `0ab6672` (2026-06-21)

> **Research Questions**
> 1. **Performance**: How do different blockchain identity standards compare in terms
>    of transaction cost, latency, and throughput for vehicle identity management?
> 2. **Security**: Which identity architecture provides the strongest security
>    guarantees for V2X (Vehicle-to-Everything) communication?
> 3. **Compliance**: Can blockchain-based identity systems achieve full W3C
>    Self-Sovereign Identity compliance while meeting automotive industry requirements
>    (MOBI VID)?
> 4. **Practical Feasibility**: Are blockchain identity systems viable for real-time
>    safety-critical V2V (Vehicle-to-Vehicle) communication?
>
> **Hypothesis**
> Lightweight blockchain identity standards (ERC-1056) can provide sufficient security
> and W3C compliance for vehicle identity management while maintaining performance
> suitable for real-time V2V safety applications, offering a viable alternative to
> centralized PKI systems.
>
> **Novel Contributions**
> 1. First comprehensive comparison of 9 blockchain identity standards for automotive
>    applications
> 2. Real-time V2V integration with blockchain identity verification (first working
>    implementation)
> 3. MOBI VID + W3C compliance — bridging automotive and web identity standards
> 4. Hybrid architecture combining strengths of multiple ERC standards
> 5. Open-source testbed for reproducible vehicular identity research

### A.7 The five thrusts and H1–H5 — `docs/RESEARCH_THRUSTS_REPORT.md` (2026-07-05)

The author's decomposition of A.6 into five thrusts with falsifiable hypotheses:
H1 cost (minimal vs rich-state standards), H2 compliance (≥ 90 % achievable, minimal
standards need off-chain augmentation), H3 real time (off-chain verification meets the
budget; chain reads at message time do not), H4 industry (MOBI VID maps most
economically to event-log standards and most faithfully to claim-based ones; the hybrid
sits on the fidelity-per-gas frontier), H5 security (no standard dominates; the
ERC-1056 + ERC-735 hybrid lies on the Pareto frontier).

---

## B. The author's working directives (how the work is to be done)

Given across the sessions; recorded here in substance so they bind future sessions
too.

1. **Attribution.** Commits are authored by the author (nikhil.prakash1995@gmail.com),
   no AI co-author trailers — academic integrity. The hypotheses, sub-hypotheses,
   thrusts and design decisions (e.g. ERC-1056 as the base substrate) are the author's
   from the beginning; the tooling implemented and measured. Provenance is corrected
   wherever earlier logs said otherwise (`PROVENANCE.md`, `docs/DEVELOPMENT_HISTORY.md`).
2. **Version everything; push often.** Every checkpoint is committed and pushed; when
   push was impossible, a git bundle was the durable backup. Tags mark milestones
   (v0.7.0, v0.8.0; v0.9.0 to be cut on the merge with a Sepolia witness).
3. **A base good enough for a thesis on its own, before adding the notebooks.** The
   author has "a couple notebooks full" of parallel research; the base is stabilised
   and made examiner-defensible first, then extension slots receive that material —
   some of which may never be integrated.
4. **Think at the level of an ECE research master's.** Not implementation volume —
   which is already over-complete — but the writing discipline and methodology of a
   MASc: hypotheses that can fail, measured evidence with conditions, threats to
   validity designed in, claims that survive an examiner.
5. **Composition document that travels with the work** (`COMPOSITION.md`): the argument
   and the writing discipline, updated as results land; more code, execution and
   analysis feeding it, so the thesis can be written out "no problem".
6. **Interim internal reports and audits**, honestly critical, at the author's request;
   the author audits and inputs at checkpoints.
7. **Mind token usage; never end abruptly** — leave things at a hand-off, with a living
   meta-commentary/handback document, and over-explain in after-action reports that are
   started at the beginning of a pass and updated in parallel.
8. **Use the internet and canonical work** to check and ground insight; prefer
   verified sources to memory; when grounding, give examples with a paragraph each and
   a second on incorporation.
9. **Open-source testbed.** The project (at least this part) is open; there is no
   secret to protect in the repository — the only access limits are the session's,
   not the author's.
10. **Figures where they help; organise the outputs of each session** with a manifest
    and descriptions.

---

## C. How the direction has been carried forward (pointers, not paraphrase)

| Original element | Where it stands now | Record |
|---|---|---|
| A.1 sandbox's generic API/DB/cloud hooks | Became the `IdentityProvider` abstraction (PKI, centralized, ERC-1056, MOBI VID) — the most reused design decision | review §3.1 |
| A.1 LLM interface | Never built; re-scoped as a possible defence demo, not a contribution | review §5.8 |
| A.2 RQ1 (DID vs PKI latency) | Measured: `cv2x-testbed/results/pki_vs_erc1056.md`; register #21 | `MEASUREMENT_CONDITIONS.md` |
| A.2 RQ2 (chain query vs CRL) | Measured as check-revocation 7.7 ms vs 0.001 ms (local) | #21 |
| A.2 RQ3 (pseudonyms vs DIDs privacy) | Deferred (SC-02); bounded experiment planned (M5) | `SCOPE_CHANGES.md`, `PLAN_MOBI_SUMO.md` |
| A.2 RQ4 (network performance) | Out of scope by design (no channel model; Veins/MOSAIC named as the traded fidelity) | review §4.3–4.4 |
| A.3 V2 ten questions | Three promoted (latency across methods, revocation vs CRL, 1000-vehicle scaling → S4); seven demoted to future work (SC-03) | audit §1.5 |
| A.4 roadmap RQ1 hypothesis (10–100× writes) | Answered on a different axis: on/off the hot path, not read/write | review §2 |
| A.4 success criteria | 13 met, 9 partial, 1 open, 2 dropped (SC-01, SC-02) | `docs/figures/review_criteria_matrix.png` |
| A.5 three-tier VIN privacy | Two tiers built and tested; ZK tier future work (SC-12) | `SCOPE_CHANGES.md` |
| A.5 centralized parity baseline | Built; lifecycle-parity comparison pending (SC-13, M4) | plan |
| A.6 compound hypothesis | Replaced by H1–H5 everywhere (README, thesis README) | audit F6 |
| A.6 "first" contributions | Reworded to measured, domain-constrained, reproducible (SC-04) | audit §1.3 |
| A.6 nine standards | On the trunk since the merge (SC-07 resolved); gas re-executed | register #25 |
| A.7 H1–H5 | H1 supported with the operation-definition caveat (#6); H2 93.2 % internal / 74.4 % external DID; H3 supported in structure (#21, `LATENCY_BUDGET.md`); H4 five-backend fidelity gradient; H5 hybrid non-dominance proven in the analysis lineage | `PROJECT_SUMMARY.md` §2 |
| B.1 attribution | Every commit of the sessions under the author's name | `git log` |
| B.2 versioning | 105 commits on the trunk; tags local, pending the author's push | `AFTER_ACTION_REPORT.md` §6 |
| B.3 base first | Base verified end to end; notebook index still awaited | handback |
| B.7 handback | `docs/HANDBACK_2026-09-30.md` | — |
