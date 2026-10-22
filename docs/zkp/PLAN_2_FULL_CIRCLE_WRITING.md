# Plan 2 — Full Circle: The Writing Series That Closes the Research Loop

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15, before execution. **Executed:** not in this session; the author runs it in other chats with
`PLAN_2_PHASED_PROMPTS.md`.
**Depends on:** Plan 1's outputs (`docs/zkp/REPORT_A_*`, `REPORT_B_*`, `REPORT_C_*`, `SOURCES_ZKP.md`,
`THESIS_INTEGRATION_MAP.md`, `5_zkp-agent-identity/results/`, `5_zkp-agent-identity/figures/`), the thesis drafts in
`docs/thesis/`, the claim register (`docs/MEASUREMENT_CONDITIONS.md` §3), and the history documents
(`docs/DEVELOPMENT_HISTORY.md`, `docs/RESEARCH_THRUSTS_REPORT.md`, `docs/ORIGINAL_PROMPT_AND_DIRECTION.md`,
`SIDE_PAPERS.md`, `docs/phase2/IDEA_REGISTER.md`).
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md` for every number and every claim. Rhetoric is allowed in framing and
voice; it is never allowed in evidence. A sentence may be beautiful; it may not be inflated.

---

## 0. What this series is for

Six years of work on identity for connected and autonomous vehicles produced nine contract standards measured
against each other, a W3C layer, MOBI VID realised on five backends, a V2X testbed with real cryptography in the
message path, a claims register that refuses to round up, and a Phase 2 that opened twenty-six ideas. It also
produced a question that was parked because it looked too large: **if machines are going to act in the world,
they need identities and reputations too, and that includes AI agents.** That thought was set aside.

Plan 1 found the other end of the same rope. Zero-knowledge proofs are the right tool for the privacy the
vehicle identity work kept deferring (the ZK VIN tier, the knowledge-of-opening dependency, predicate
disclosure). But zero-knowledge identity cannot be operated by a person: it is hexadecimal strings, field
arithmetic, nonces, nullifiers, Merkle paths, a policy over every disclosure ever made, and a defence against
verifiers who ask clever sequences of questions. It needs a custodian that never sleeps, holds keys without
exposing them, understands what the owner means in plain language, computes what no person can, keeps
memory across interactions and adapts to new attacks. That custodian has the shape of an AI agent wrapping an
identity. And that agent, to be trusted, needs exactly the identity system the thesis built: a DID, a
delegation credential, revocation, an audit trail anchored to a ledger.

**Identity for machines; machines for identity.** The loop closes. The writing series exists to say so well, to
prove it carefully, to tell how it happened, and to turn the closure into the structure that finishes the thesis.
It also exists to put a fence around everything else: the other fruits become papers, projects and post-graduate
work, after the thesis is done.

## 1. The master metaphor

The series needs one image that carries the argument. Candidates were weighed; the recommendation is the
**keystone**, with the **carabiner** as the author's own image and the **pressure suit** as the image for the
agent wrapper.

| Image | What it carries | Why it fits | Use |
|---|---|---|---|
| **Keystone** | An arch cannot stand while it is being built; it rests on scaffolding (centring) until the last, wedge-shaped stone is set at the crown. Then the arch carries itself, and the centring is removed. The keystone is held in place by the very stones it locks. | Six years of stones (standards, measurements, W3C, MOBI, V2X) stood on scaffolding (deferrals, future-work notes). ZK plus the agent is the wedge at the crown; it is held by the stones it locks (the agent needs the DID stack it completes). After it is set, the scaffolding (the "future work" holding up chapter 7) can come down. | Master metaphor for the heroic document and the thesis conclusion. |
| **Carabiner** | A gate that is closed and locked becomes a full loop that carries load; open, it is a hook. | The author's image. The research was a hook (identity for vehicles) until the gate closed (machines for identity). | The essay's turn; the moment of recognition. |
| **Pressure suit** | A person cannot survive vacuum; the suit is not a convenience but the condition of being there at all. It is personal, fitted, and carries its own life support and limits. | The chain is a hostile environment (irreversible, public, adversarial). The agent wrapper is the suit: bounded, personal, the condition of a human acting there safely. | Report C and the narrative chapter on the interface. |
| **Ouroboros** | The snake eating its tail. | Closure, but also endlessness; risky because it suggests futility. | Mention and reject. |
| **Pencil-and-paper miner** | One SHA-256 hash by hand takes most of a day; Bitcoin needs quintillions per second. | The concrete proof of P2: some algorithms are not for hands. | The opening image of the dramatic piece. |
| **Zip and unzip** | Nobody runs DEFLATE by hand; we trust a tool and verify by result. | Ordinary precedent for delegating an algorithm to software. | A grounding example, so the argument is not exotic. |
| **Ariadne's thread** | The thread that lets one walk back out of the labyrinth. | The audit log and the claims register. | A minor image for provenance. |

## 2. The series

Four principal pieces (the author's "four beautiful pieces") and six supporting pieces. The heroic document is
piece W-1. The two pieces the author asked for explicitly ("one technical and one with rhetoric and narrative")
are W-2 and W-3.

| Id | Title (working) | Kind | Audience | Length | Voice |
|---|---|---|---|---|---|
| **W-1** | *The Keystone: Identity for Machines, Machines for Identity* | heroic document, braided technical and narrative | committee, examiners, future readers of the thesis, the field | 15,000–20,000 words | confident, academic, with set pieces |
| **W-2** | *Agent-Wrapped Self-Sovereign Identity: Necessity, Construction and Evidence* | technical capstone paper | examiners, reviewers at a venue (e.g. IEEE TIFS, ACM CCS workshop, IEEE ICBC) | 9,000–12,000 words | formal, propositional |
| **W-3** | *The Resting Point* | rhetorical and narrative essay | the author's community, supervisor, a general technical reader | 5,000–7,000 words | personal, rhetorical, dramatic in places |
| **W-4** | *The Bridge: How the Closed Loop Finishes the Thesis* | structural plan in prose | the author and supervisor | 6,000–8,000 words | direct, decisive |
| W-5 | *The Chronicle: Six Years of Thrusts* | research history | examiners (methods), the author | 5,000–8,000 words | factual, dated |
| W-6 | *The Analogy Atlas and "A Day Without the Steward"* | illustrated analogies and a dramatised vignette | general reader, talk audiences | 3,000–5,000 words | vivid |
| W-7 | *The Portfolio: Papers, Projects and Post-Graduate Work After the Thesis* | ranked programme | the author, future collaborators | 3,000–5,000 words | planning |
| W-8 | *Pitches: Abstract, Executive Summary, Three-Minute Thesis, Defence Opening* | short forms | everyone | 1,500–3,000 words total | crisp |
| W-9 | *The Defence Dossier: Objections and Answers* | anticipated critique | examiners | 4,000–6,000 words | adversarial, fair |
| W-10 | *The Visual Essay* | figure-led page (artifact or PDF) | talk audiences, README visitors | 20–30 figures with captions | visual |

### 2.1 W-1 — The Keystone (the heroic document)

**Thesis of the piece.** The research has reached a resting point that was not planned and that is nevertheless
the correct one: identity infrastructure for machines turns out to require machines to operate it, and the machine
that operates it requires the infrastructure. The loop is closed by construction, demonstrated by code, and bounded
by evidence.

**Structure.**

| § | Title | Content | Evidence anchors |
|---|---|---|---|
| Prologue | *The arch on its centring* | The image of an arch under construction; six years of stones; what was holding it up (the deferrals: SC-12, I-09, AR-5, chapter 7's future work) | `docs/SCOPE_CHANGES.md`, chapter 7 draft |
| 1 | *Why vehicles needed identity* | the original problem, RQ1–RQ4, H1–H5, what was found | README hypotheses, register rows |
| 2 | *What the stones are* | nine standards, the W3C layer, MOBI VID I and II, the V2X testbed, the comparison framework; each as a stone with its measured shape | chapter 5, result cards |
| 3 | *The question that was set aside* | agent identities and reputation: why it was obvious, why it looked like too much | the author's recollection (interview prompt in W0), `docs/ORIGINAL_PROMPT_AND_DIRECTION.md` |
| 4 | *Zero knowledge: the missing tier* | ZK in plain terms, then precisely; ZK-VIN; what it closes | Report B, Report A, `results/` |
| 5 | *The wall of hex* | the manual-burden demonstration; the pencil-and-paper miner; the hex wall figure; why this is a safety argument, not a convenience argument | Report C §manual burden, figures |
| 6 | *The custodian's shape* | the requirements profile; why it is an agent; the pressure suit | Report C |
| 7 | *The suit must have limits* | LLM proposes, kernel disposes; prompt injection fails; the owner's signature is the only widening | tests, Report C |
| 8 | *The twenty questions* | the new attack vector, the Sybil split, the static rule failing, the agent adapting; the learning curve | `results/attacks.json`, figures |
| 9 | *The keystone set* | the agent needs a DID, a delegation credential, revocation and an anchored audit: the thesis stack. Identity for machines, machines for identity | Report C §agents need identity, delegation tests |
| 10 | *Not everything on chain* | SSI as a spectrum; the two tables; partial realisation by constraint, not by control; strict SSI compatibility as an option the build keeps open | Report C tables |
| 11 | *Against the user as product* | data hegemony, the surveillance model, and what changes when the custodian works for the owner | Report C, sources |
| 12 | *What remains true and what remains open* | limits stated plainly: simulation, single-party setup, estimates labelled E, no field trial | Report A limits, register |
| 13 | *Taking down the centring* | how this finishes the thesis; what becomes papers and post-graduate work | W-4, W-7 |
| Epilogue | *The arch carries itself* | return to the image | — |

**Set pieces** (written with care, one per major section): the arch on its centring; a person copying a 64-character
private key by hand at a published error rate; the pencil-and-paper miner's day; the verifier who asks twenty
questions; the agent declining politely and the attacker's entropy staying put; the moment the agent itself is
asked for its credential.

**Must include:** the six propositions P1–P6 and how each fared (from Report A's verdict table, never from memory);
at least six figures from `5_zkp-agent-identity/figures/`; the two SSI tables; a timeline figure; a closing
paragraph that names what is *not* claimed.

### 2.2 W-2 — The technical capstone

**Form:** a paper. Abstract; introduction with contributions (numbered); background (DIDs, VCs, ZK, agents);
system model and threat model (adversaries: curious verifier, Sybil verifier set, malicious model output, replay,
linkage); definitions (custodian, requirement profile R1–R7, leakage budget, coarsening, scoped nullifier,
delegation credential); the necessity argument (P2 → P3 as a structured argument with premises and evidence);
construction (zkid, ZK-VIN, ZkVinGate, the Steward); security analysis (per adversary: what is prevented, what is
detected, what remains); evaluation (Z-E1..Z-E7 verdicts, gas, timing, attack outcomes with confidence over seeds,
ablations); related work (anonymous credentials, ZK identity on chain, agent identity, query auditing, prompt
injection defences); limitations; conclusion. Venue-ready figures and tables. Every number from `results/`.

**Formal content to develop** (the phase prompt asks for these explicitly): a definition of session privacy for
predicate credentials (leakage measured as reduction in min-entropy or Shannon entropy of the attribute given all
answers to all colluding verifiers); a statement that per-proof zero knowledge does not imply session privacy, with
the narrowing attack as the counterexample; the budgeted custodian's guarantee (leakage never exceeds budget B
against any set of verifiers that the custodian cannot distinguish, because the budget is global per attribute);
the cost of the guarantee (honest service rate) as measured.

### 2.3 W-3 — The Resting Point (rhetoric and narrative)

**Arc.** (1) The question everyone asks at the end of a long project: is it finished? (2) Six years, told as
thrusts: what each was for, what it taught, where it pointed. (3) The parked idea: identities for agents; why it was
put down. (4) Zero knowledge arrives as a *technical* need, not a fashion. (5) The turn: you cannot do this by
hand; the wall of hex; the pencil-and-paper miner. (6) Recognition: the thing that must operate the identity is an
agent; the agent needs the identity. The carabiner gate closes. (7) Why it feels *correct*: three tests of a
right answer (it was not sought; it uses what was already built; it makes the remaining work smaller, not larger).
(8) The discipline of stopping: many good things remain; the thesis comes first. (9) Coda: the arch.

**Rhetorical devices to use deliberately:** anaphora in the turn ("It needs…", six times, one per requirement);
a periodic sentence at the recognition; antithesis ("identity for machines, machines for identity"); a concrete
number at each emotional peak (never an invented one); one quotation from canonical literature per section at
most; a short dramatic present-tense passage (the miner, or the verifier's twenty questions).

**Guardrails:** the essay may say "this feels right"; it may not say "this proves" unless Report A shows it.
Drama is in the telling, not in the claims.

### 2.4 W-4 — The Bridge to the thesis

**Content.** (1) The thesis as it stands: title, RQ1–RQ4, H1–H5, chapter status (from `docs/thesis/README.md`).
(2) Three options for absorbing the closed loop, with a recommendation: (a) ZK and the agent as a final results
section and discussion (smallest change); (b) a new RQ5 and H6 with a dedicated chapter between results and
discussion (recommended); (c) a retitled thesis whose conclusion is the loop (largest change). (3) A chapter-by-
chapter fill plan with page budgets and the documents each chapter draws from. (4) The "fence": what is out of the
thesis and where it goes (W-7). (5) A dated schedule to submission. (6) The author's decisions, each with a
default.

**Proposed RQ5 and H6 (for the author's decision).**
- RQ5. *Can zero-knowledge proofs provide the deferred VIN privacy tier and identity-dependent knowledge checks
  within the budgets of RQ1 and RQ4, and what does operating them require?*
- H6. *Zero-knowledge vehicle identity is feasible at registration and session time (not per message), and its
  safe operation requires a bounded, adaptive custodian (an agent wrapper) whose own trust rests on the same
  decentralized identity stack.* The pre-registered expectations Z-E1..Z-E7 are its measurable part.

### 2.5 W-5 — The Chronicle

Dated history from the repository's own records: the first prototypes, the nine-standard benchmark, review 02,
the merges of lineages, the sandbox and suites, WM-1 and WM-2, Phase 2, Plan 1. For each thrust: question, what was
built, what was learned, what it fed. A timeline figure generated from a committed YAML of dates. Source discipline:
every date from a commit, a report or the author's interview notes, labelled as such.

### 2.6 W-6 — The Analogy Atlas and the vignette

One page per analogy in §1, each with: the image, the mapping (a two-column table), where it breaks, and a
figure brief. Then a dramatised vignette, *A Day Without the Steward*: an owner tries to sell a car, prove its model
year to an insurer, pay a toll, and answer an RSU, by hand, with keys and hex; then the same day with the Steward.
Present tense, short scenes, every technical detail correct, the numbers taken from Report C.

### 2.7 W-7 — The Portfolio

Every idea that is not the thesis, ranked and routed: the 26 Phase 2 ideas (I-01..I-26), the side papers
(SIDE_PAPERS.md), Plan 1's [later] to-dos, and agent-identity programmes (agent reputation, agent-to-agent
credential exchange, agent delegation revocation at machine speed, insurance for agent actions). For each: venue
or vehicle (paper, open-source project, grant, post-graduate thesis), first step, kill criterion.

### 2.8 W-8 — Pitches

A 150-word abstract and a 350-word abstract; a one-page executive summary; a three-minute thesis script (about 450
spoken words) with one slide; a five-minute defence opening; a ten-slide outline; a one-sentence and a
one-paragraph statement of contribution.

### 2.9 W-9 — The Defence Dossier

At least twenty-five objections in four groups (cryptography, systems, AI safety, SSI ideology), each with the
strongest form of the objection, the answer, the evidence file, and what is conceded. Examples: "This is just a
wallet." "An LLM with keys is a liability." "Groth16's setup makes it centralised." "Simulation is not deployment."
"SSI is ideology." "Why a blockchain at all?" "Your attack is just differential privacy's old result." "Your
manual-burden numbers are estimates." "Agents will be phished instead of people."

### 2.10 W-10 — The Visual Essay

A figure-led page: the arch, the stones, the hex wall, the manual-versus-agent chart, the circuit, the
architecture, the leakage curves, the learning curve, the two SSI tables, the timeline, the loop diagram. Each
figure with a caption of at most three sentences. Published as a private artifact page and exported to PDF.

## 3. Shared requirements for every piece

1. **Evidence.** Numbers only from `5_zkp-agent-identity/results/`, the claim register, or a cited source; each
   with its condition tag. Status E numbers are called estimates in the sentence that uses them.
2. **Verbs.** "Shows", "demonstrates", "proves" only where Report A's verdict table supports it. Otherwise
   "indicates", "suggests", "in simulation".
3. **Consistency.** One glossary (`docs/zkp/GLOSSARY.md`, made in phase W0) for all ten pieces.
4. **Attribution.** Author, date, what binds it, what it supersedes, at the top of each piece.
5. **No model names** in any file; commits authored by the author with no AI trailers.
6. **Grounding.** At least one canonical source per major section of W-1, W-2 and W-3, from `SOURCES_ZKP.md`.
7. **Figures.** Reused from Plan 1; new ones (timeline, arch, loop) generated by a committed script.
8. **Review.** Each principal piece reviewed by an independent agent on a frozen checkout for (a) number
   fidelity, (b) overclaiming, (c) prose quality; every finding gets a disposition.

## 4. Order and dependencies

W0 (evidence pack, glossary, interview) → W-5 Chronicle → W-2 Technical capstone → W-1 Keystone → W-3 Resting
Point → W-4 Bridge → W-9 Defence → W-7 Portfolio → W-6 Atlas and vignette → W-8 Pitches → W-10 Visual essay →
cross-read and publish. The Chronicle comes first because every narrative piece draws its dates from it; the
technical capstone comes before the heroic document so that the heroic document can cite rather than re-derive.

## 5. Acceptance

The series is done when: all ten pieces exist with headers; every number traces; the independent reviews are
dispositioned; the thesis README links W-4's chapter plan; the author has taken or deferred each decision in W-4;
and the visual essay is published.
