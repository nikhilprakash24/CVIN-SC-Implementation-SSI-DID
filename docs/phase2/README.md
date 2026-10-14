# Phase 2 — Charter, Index and Session Protocol

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-14 (after-action report 15, step P2). **Sub-phase now:** P2.0, ideation (session 1 done).
**Supersedes:** nothing; this is the first Phase 2 document. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`,
`docs/TEAM_STRUCTURE.md` (roles; review protocol §4a), `docs/milestones/README.md` (what closes a work milestone).
**Read first in every Phase 2 session:** this file, then `sessions/SESSION_LOG.md` (the last entry says what
to do next).

## 1. What Phase 2 is
**Phase 1** is the thesis artefact: nine Ethereum identity standards compared on one vehicle lifecycle,
a W3C credential layer, a V2V and V2I verification testbed under mock mobility, and the evidence machinery
that makes each number checkable (claim register, run stamps, generated documents, audits). It runs to the
thesis defence through work milestones WM-1 (closed), WM-2 (in progress) and the version tags v0.9.0 and v1.0.

**Phase 2** is the research and engineering programme that starts from what Phase 1 established and left
open. It is built across many sessions and is itself phased: ideation → architecture → planning → build
waves. Phase 2 does not change Phase 1's results of record. Where it needs a Phase 1 change, that change
goes into the Phase 1 plan (`docs/PLAN_WM-2.md` or its successor) and follows Phase 1's rules.

**Name space.** Older documents use "Phase 2" for their own internal steps (`cv2x-testbed/V2_DESIGN.md`
phases 1–5, the testing-suite plan's phase 2, the 2025 project summary). In this repository from now on,
**"Phase 2" means this programme**, and its parts carry the ids below.

| Id form | What | Where |
|---|---|---|
| P2.0 … P2.5 | sub-phases (§3) | `ROADMAP.md` |
| I-nn | an idea | `ideas.yaml` → `IDEA_REGISTER.md` (generated) |
| PG-name | a candidate programme (a bundle of ideas) | same |
| P2-Dn | an author decision for Phase 2 | `DECISIONS.md` |
| ADR-nnnn | an architecture decision record | `DECISIONS.md` §2 |
| B1-nn | a brainstorm item of session 1 | `BRAINSTORM_01.md` |
| S-nn | a seed: a Phase 1 open item Phase 2 can start from | `EVIDENCE_BASE.md` |

## 2. Principles (Phase 1's rules, plus four for Phase 2)
Phase 1's guide applies in full (no fabricated numbers; a number enters a chapter only with a V row;
pre-registrations are amended, never edited; every guard shown to fire; author-only commits). Phase 2 adds:

1. **Anchored.** Every idea cites the Phase 1 artefact it starts from (a register row, crux, defect, deferred
   item, side paper or scope change) and a file it builds on. `build_phase2.py --check` enforces it in CI.
2. **Killable.** Every idea states a first step small enough for one or two sessions, and a kill criterion
   written before the first step runs. A killed idea stays in the register with its result.
3. **Decided by the author.** The ranking orders the conversation. The author chooses the programme (P2-D1)
   and every scope change. Orchestrator defaults are labelled as such, never as the author's.
4. **No Phase 2 number before its plan.** Ideation and architecture produce designs, sizes and predictions,
   not results. The first Phase 2 measurement comes from a pre-registered plan in a build wave (P2.4).

## 3. Sub-phases and their gates
| Sub-phase | Work | Closes when (gate) | Sessions (estimate) |
|---|---|---|---|
| **P2.0 Ideation** | evidence base; broad idea register; candidate programmes; first architecture sketch; roadmap; decisions list | the author has the register and the decision list (G0) | 1 (this one) |
| **P2.1 Brainstorm and select** | deep-dive briefs for the top ideas (literature, tooling, size, risk, first experiment); the author's notebook threads taken in (I-20); programme chosen | author decision P2-D1 recorded (G1) | 2–3 |
| **P2.2 Architecture** | ADRs for the chosen programme; interface specifications (§4 of `ARCHITECTURE.md`); spikes that prove each risky interface | each ADR accepted; each spike's kill criterion evaluated (G2) | 2–4 |
| **P2.3 Planning** | a work-milestone plan WM-P2-1 in the WM-2 format: steps, gates, pre-registrations, owners | plan reviewed per `TEAM_STRUCTURE.md` §4a (G3) | 1–2 |
| **P2.4 Build waves** | WM-P2-1, WM-P2-2, …, each closed like a Phase 1 work milestone | `docs/milestones/README.md` conditions (G4…) | per plan |
| **P2.5 Write-up** | thesis extension chapter or future-work evidence, side papers, release | author | per plan |

Phase 2 runs in parallel with Phase 1 only while it produces documents (P2.0–P2.3). A build wave that needs
the same code paths as an open Phase 1 step waits for that step (`ROADMAP.md` §3).

## 4. Session protocol (how a session picks up, across chats)
1. Read this file, the last entry of `sessions/SESSION_LOG.md`, and `DECISIONS.md` (open decisions).
2. Open the session's after-action report (the Phase 1 series continues; Phase 2 work is a step in it).
3. Do the step the last log entry names. If the author changed direction, record that first in `DECISIONS.md`.
4. Edit ideas only in `ideas.yaml`, then run `python3 docs/phase2/build_phase2.py`. Never edit `IDEA_REGISTER.md`.
5. Close with a log entry: what was done, what changed in the register (ids), what the next session does.
6. Run the document checks unpiped (`build_phase2.py --check` and the Phase 1 checks), commit, push, read CI.

## 5. Documents
| File | What it holds | State |
|---|---|---|
| `README.md` | this charter, index and protocol | P2.0 |
| `EVIDENCE_BASE.md` | what Phase 1 established, what it left open, as seeds S-nn with their Phase 1 sources | P2.0 |
| `ideas.yaml`, `IDEA_REGISTER.md` | 23 ideas in 7 tracks, scored, anchored; 5 candidate programmes | P2.0, scores are orchestrator estimates |
| `build_phase2.py` | generator and checker (CI) | P2.0 |
| `ARCHITECTURE.md` | reference architecture (planes), the interfaces Phase 2 would add, three structural options | P2.0 sketch; P2.2 decides |
| `ROADMAP.md` | sub-phases in detail, session plan, dependencies on Phase 1, risks | P2.0 |
| `BRAINSTORM_01.md` | session 1: method, divergent list, parked ideas, cross-cutting questions, questions for the author | P2.0 |
| `DECISIONS.md` | author decisions P2-D1… with defaults; ADR log | P2.0 |
| `sessions/SESSION_LOG.md` | one entry per Phase 2 session; the last entry is the next session's brief | P2.0 |
| `PHASE2_PROGRAMME.md` | **the consolidated document**: Phase 2 in one reading, with the three focuses and the scope | session 2 |
| `SCOPE_RECONCILIATION.md` | the thesis scope across its revisions; Scope v3; where Phase 2 belongs; paper map; examiner questions; 15 decisions | session 2 (academic adviser) |
| `focus/F1_onchain_storage_idtx/`, `focus/F2_chains_and_databases/`, `focus/F3_interaction_modes/` | the three author-designated focuses: README (executive summary), CAPTURE, ANALYSIS, PLAN, EXECUTION | session 2 |
| `focus/FIGURES.md`, `focus/figures/`, `focus/make_focus_figures.py` | five generated figures with their table views (CI-checked) | session 2 |
| `reviews/` | the review team's reviews of Phase 2 documents | session 2 |
| `CHAT_WORKSPACE_BRIEF.md`, `inbox/` | the hand-off for literature, standards and drafting work in a chat workspace with tools, and where its results return | session 2 |
