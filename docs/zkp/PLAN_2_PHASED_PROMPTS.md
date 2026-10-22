# Plan 2, Phased — Prompts for the Full-Circle Writing Series

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15, alongside `PLAN_2_FULL_CIRCLE_WRITING.md`. Run one prompt per fresh chat, in order.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `PLAN_2_FULL_CIRCLE_WRITING.md` §3 (shared requirements).

## Common preamble (prepend to every prompt)

> Repository `nikhilprakash24/CVIN-SC-Implementation-SSI-DID`. Work on the branch you are given; if it is behind
> the branch that holds `docs/zkp/` (the Plan 1 outputs), fast-forward first. Read, in order:
> `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/zkp/PLAN_2_FULL_CIRCLE_WRITING.md` (the series, the master metaphor, the
> shared requirements); `docs/zkp/REPORT_A_ZKP_INTEGRATION.md` (especially its verdict table for P1–P6 and
> Z-E1..Z-E7); `docs/zkp/REPORT_C_AGENT_WRAPPED_IDENTITY.md`; `docs/zkp/GLOSSARY.md` if it exists. Every number you
> write must come from `5_zkp-agent-identity/results/`, the claim register (`docs/MEASUREMENT_CONDITIONS.md` §3) or
> `docs/zkp/SOURCES_ZKP.md`, with its condition tag; estimates are called estimates. "Proves" and "demonstrates" only
> where Report A's verdict table supports it. Commits authored as Nikhil Prakash, no AI trailers, no model names in
> any file. Write the document's header (author, date, what binds it, what it supersedes). When done, run an
> independent review agent over your piece for number fidelity, overclaiming and prose quality, give every finding a
> written disposition in `docs/zkp/series/REVIEWS.md`, then commit and push. The writing must be smooth,
> sophisticated and academically grounded, confident where the evidence is strong, plain where it is not.

---

## W0 — Evidence pack, glossary and the author interview

> Create `docs/zkp/series/` and in it: (1) `EVIDENCE_PACK.md`: every number the series may use, in one table
> (value, unit, condition, source file, register row or source key, status); generate it with a committed script
> `docs/zkp/series/build_evidence_pack.py` reading `5_zkp-agent-identity/results/*.json` and the register, with a
> `--check` mode for CI. (2) `GLOSSARY.md` (moved to `docs/zkp/GLOSSARY.md`): every term the series uses (DID,
> VC, ZKP, SNARK, Groth16, circuit, witness, nullifier, commitment, Merkle root, Fiat–Shamir, leakage budget,
> coarsening, custodian, agent wrapper, delegation credential, Steward, IDTx, SSI spectrum), one or two sentences
> each, consistent with Reports A–C. (3) `INTERVIEW.md`: twenty questions for the author about the six years (when
> the agent-identity idea first came up and why it was set aside; the moment zero knowledge became necessary; what
> felt like dead ends; what the author wants the reader to feel), with empty answer slots. Stop and ask the author
> to answer the interview before W-5 if possible; otherwise mark the gaps for later.

## W-5 — The Chronicle (first, because every narrative piece takes its dates from it)

> Write `docs/zkp/series/W5_CHRONICLE.md`: the research history from the repository's records
> (`docs/DEVELOPMENT_HISTORY.md`, `docs/RESEARCH_THRUSTS_REPORT.md`, `docs/ORIGINAL_PROMPT_AND_DIRECTION.md`, the
> after-action reports 01–19, the handbacks, `docs/phase2/`, `git log`) and the author's interview answers. For
> each thrust: dated start, the question, what was built, what was learned, what it fed into, and whether it was
> continued, parked or closed. End with a section "Where the loop closes" that traces two threads forward to Plan 1:
> the privacy thread (salted hashes → SD digests → SC-12 deferral → ZK-VIN) and the machine thread (vehicles as
> principals → automated agents in IDTx → the parked agent-identity idea → the Steward). Add a timeline figure from a
> committed YAML (`series/timeline.yaml`) via `series/make_series_figures.py`. 5,000–8,000 words.

## W-2 — The technical capstone paper

> Write `docs/zkp/series/W2_TECHNICAL_CAPSTONE.md`, a venue-ready paper, *Agent-Wrapped Self-Sovereign Identity:
> Necessity, Construction and Evidence*, 9,000–12,000 words, following `PLAN_2_FULL_CIRCLE_WRITING.md` §2.2. Develop
> formally: (a) session privacy for predicate credentials, with leakage as the reduction in entropy of the attribute
> given all answers to all colluding verifiers; (b) the observation that per-proof zero knowledge does not imply
> session privacy, with the narrowing attack as the counterexample and Denning's tracker and Dinur–Nissim as the
> lineage; (c) the custodian requirement profile R1–R7 and the structured necessity argument from the manual-burden
> evidence; (d) the budgeted custodian's guarantee and its measured cost. Include the system and threat models, the
> construction, the security analysis per adversary, the evaluation (every Z-E verdict, gas, timing, attacks over 30
> seeds, ablations), related work from `SOURCES_ZKP.md`, limitations, conclusion. Produce a LaTeX version too
> (`series/latex/w2.tex`) using the figures in `5_zkp-agent-identity/figures/`.

## W-1 — The Keystone (the heroic document)

> Write `docs/zkp/series/W1_THE_KEYSTONE.md`, *The Keystone: Identity for Machines, Machines for Identity*,
> 15,000–20,000 words, following the section table in `PLAN_2_FULL_CIRCLE_WRITING.md` §2.1 exactly, braiding
> narrative and technical exposition. Use the keystone as the master metaphor, the carabiner at the moment of
> recognition, the pressure suit for the agent wrapper. Cite the technical capstone (W-2) rather than re-deriving
> it. Write each set piece listed in §2.1 with care; each must carry one true number. Include at least six figures
> from `5_zkp-agent-identity/figures/` and the two SSI tables from Report C. End with "What is not claimed".
> Generate the arch and loop figures with `series/make_series_figures.py`. Tone: confident, sophisticated, earned;
> the reader should feel that the work has borne fruit because the evidence is laid out, not because adjectives say
> so.

## W-3 — The Resting Point (rhetoric and narrative)

> Write `docs/zkp/series/W3_THE_RESTING_POINT.md`, 5,000–7,000 words, following the arc and devices in
> `PLAN_2_FULL_CIRCLE_WRITING.md` §2.3. It is an essay in the author's voice about how six years of research came to
> rest at a point that was unexpected and correct: the parked idea of agent identities, the arrival of zero knowledge
> as a technical need, the recognition that the custodian is an agent and the agent needs the identity. Be dramatic
> where the material earns it (the pencil-and-paper miner in present tense; the twenty questions). Explain why the
> answer feels correct by three tests: it was not sought; it uses what was already built; it makes the remaining work
> smaller. End with the discipline of stopping: the thesis first, the other fruits after. Every number true and
> sourced; no "proves" beyond Report A.

## W-4 — The Bridge to the thesis

> Write `docs/zkp/series/W4_THE_BRIDGE.md`, 6,000–8,000 words, following §2.4. Read `docs/thesis/README.md`,
> `docs/thesis/SCAFFOLD.md`, every chapter draft and `docs/zkp/THESIS_INTEGRATION_MAP.md`. Lay out the three
> absorption options with a recommendation; a chapter-by-chapter fill plan with page budgets, sources and the
> sections of Reports A–C each chapter takes; the proposed RQ5 and H6 for the author's decision; the fence (what
> goes to W-7); and a dated schedule to submission. Then make the smallest safe edits: add a "Full-circle
> integration" row to `docs/thesis/README.md` linking W-4, and add a stub section to chapter 7's draft pointing at
> the loop, marked draft. Every decision is the author's, stated with its default.

## W-9 — The Defence Dossier

> Write `docs/zkp/series/W9_DEFENCE_DOSSIER.md`: at least 25 objections in four groups (cryptography, systems, AI
> safety, SSI ideology), each in its strongest form, with the answer, the evidence file, and what is conceded. Run
> an adversarial review agent asked to produce ten further objections the dossier missed, and answer them.

## W-7 — The Portfolio

> Write `docs/zkp/series/W7_PORTFOLIO.md`: every non-thesis idea ranked and routed (Phase 2 I-01..I-26,
> `SIDE_PAPERS.md`, Plan 1's [later] to-dos, and new agent-identity programmes: agent reputation, agent-to-agent
> credential exchange, machine-speed delegation revocation, liability and insurance for agent actions, agent
> wrappers for vehicles' own autonomous agents). For each: vehicle (paper and venue, open-source project, grant,
> post-graduate thesis), first step, kill criterion, dependency on the thesis. Close with a one-page "after the
> thesis" map.

## W-6 — The Analogy Atlas and the vignette

> Write `docs/zkp/series/W6_ANALOGY_ATLAS.md`: one page per analogy in `PLAN_2_FULL_CIRCLE_WRITING.md` §1 (keystone,
> carabiner, pressure suit, ouroboros rejected, pencil-and-paper miner, zip and unzip, Ariadne's thread), each with
> the image, a mapping table, where it breaks, and a figure brief. Then the dramatised vignette *A Day Without the
> Steward*: an owner sells a car, proves model year to an insurer, pays a toll and answers an RSU by hand, with keys
> and hex; then the same day with the Steward. Present tense, short scenes, technically exact, numbers from Report C.

## W-8 — Pitches

> Write `docs/zkp/series/W8_PITCHES.md`: 150- and 350-word abstracts; a one-page executive summary; a three-minute
> thesis script of about 450 spoken words with a one-slide brief; a five-minute defence opening; a ten-slide outline;
> one-sentence and one-paragraph contribution statements. Consistent with W-1, W-2 and W-4.

## W-10 — The Visual Essay and publication

> Build `docs/zkp/series/visual_essay.html`, a figure-led page (arch, stones, hex wall, manual versus agent, circuit,
> architecture, leakage curves, learning curve, SSI tables, timeline, loop), each figure with a caption of at most
> three sentences, all images from committed scripts. Publish it as a private artifact page. Export W-1, W-2 and W-3
> to PDF (pandoc or LaTeX). Update the README's ZKP section with links to the series.

## W-X — Cross-read and close

> Read all ten pieces in order. Check: one glossary; one set of numbers (run `build_evidence_pack.py --check`); no
> contradiction between pieces; verbs match evidence; headers present. Run a final independent review on a frozen
> checkout. Write `docs/zkp/series/README.md` (the series index with a one-paragraph description of each piece and the
> reading order for three audiences: examiner, supervisor, general reader). Close with a handback listing the
> author's open decisions.
