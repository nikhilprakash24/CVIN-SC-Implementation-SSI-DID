# Phase 2 Roadmap — Sub-Phases, Session Plan, Dependencies on Phase 1, Risks

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, P2.0, session 1). **Binds:** `docs/phase2/README.md` (§3 gates).
**Status:** P2.0 done in session 1. P2.1 begins next session under the defaults in `DECISIONS.md`.

## 1. Sub-phases in detail
### P2.0 Ideation (session 1, done)
Deliverables: charter, evidence base, idea register (23 ideas, generated and checked), architecture sketch,
this roadmap, the session-1 brainstorm, the decision list, the session log. Gate G0: the author has them.

### P2.1 Brainstorm and select (sessions 2–4)
| Step | Work | Output | Gate |
|---|---|---|---|
| P2.1a | Author intake: notebook threads (I-20 template) and overrides of scores, tracks or ideas | `ideas.yaml` updated; overrides logged in `DECISIONS.md` | every override recorded |
| P2.1b | Deep-dive briefs for the five highest-ranked ideas after intake, and for any idea the author names. Each brief: canonical sources (literature, specifications, tools), what is already known, the first experiment and its prediction, size in sessions, the kill criterion re-checked | `docs/phase2/briefs/I-nn.md` | each brief cites sources it read, not recalled |
| P2.1c | A second, adversarial brainstorm: for each candidate programme, the strongest reason not to do it (a reviewer agent on a different model, per `TEAM_STRUCTURE.md` §4a) | `BRAINSTORM_02.md` | every objection answered or accepted |
| P2.1d | The author chooses the programme and the time box | P2-D1, P2-D2 recorded | G1 |

### P2.2 Architecture (sessions 4–7)
ADRs for the chosen programme only: ADR-0001 (code location, default option B), then one ADR per interface
the programme needs (`ARCHITECTURE.md` §2), each with its determinism class (AQ-3) and its time model (AQ-2).
A spike per risky interface (for example the TraCI adapter for I-01; the two-vehicle simulator coupling for I-02),
evaluated against its kill criterion. Gate G2: ADRs accepted; spikes evaluated.

### P2.3 Planning (sessions 7–8)
WM-P2-1 written in the WM-2 format: steps, gates, owners, pre-registrations for every measurement, the
interface carve-outs as Phase 1 steps with regression gates. Reviewed by fresh-context reviewers. Gate G3.

### P2.4 Build waves (WM-P2-1, WM-P2-2, …)
Each wave is a work milestone, closed by `docs/milestones/README.md`'s seven conditions, including an
independent audit. The first wave builds the interface carve-outs and the first experiment of the chosen
programme. No Phase 2 number enters a thesis chapter before its register row is V.

### P2.5 Write-up
A thesis extension chapter (if the author's timeline allows), the future-work evidence otherwise; side papers
(I-21); the open release (I-19).

## 2. Session plan (the next six sessions, under defaults)
| Session | Sub-phase | Work | Needs from the author |
|---|---|---|---|
| 2 | P2.1a–b | apply intake if any; deep-dive briefs for I-05, I-16, I-01 | notebook threads (optional); score overrides (optional) |
| 3 | P2.1b–c | briefs for I-03, I-13; adversarial brainstorm on the five programmes | — |
| 4 | P2.1d → P2.2 | programme choice; ADR-0001 | **P2-D1, P2-D2** |
| 5–6 | P2.2 | interface ADRs and spikes for the chosen programme | spike go/no-go if a kill criterion fires |
| 7–8 | P2.3 | WM-P2-1 plan and its review | plan acceptance |

Phase 1 sessions continue in between, since WM-2 is not closed. A session may do one Phase 1 step and one
Phase 2 step, recorded in the same after-action report, as session 1 did.

## 3. Dependencies on Phase 1
| Phase 2 idea | Waits for (Phase 1) | Why |
|---|---|---|
| I-05, I-13 | WM-2 C0 (verifier v3 and the D51 fix) | the model must be checked against the fixed provider, and must rediscover D51 on the unfixed one |
| I-16 | WM-2 C1 (resolver reads the chain) | I-16 is the external re-run of C1's resolver |
| I-08, I-12 | WM-2 C2 (restricted attestation; non-zero signer) | the properties are stated against the fixed contracts, with D53 as the must-find target on the old ones |
| I-01, I-11, I-07 | author decision N-4 (SUMO install) | no real mobility without it |
| I-03 | author decision N-11 (Sepolia secrets) | no public-chain witness without it |
| every build wave | WM-2 A4 (promote step, done), A5 (`claims.yaml`) | Phase 2 producers start on the promote path and the claim cross-check |

## 4. Risks
| Risk | Likelihood | Effect | Mitigation |
|---|---|---|---|
| Phase 2 crowds out WM-2 and the defence | medium | the thesis slips | P2.0–P2.3 are documents only; P2-D2 sets the time box; Phase 1 steps keep priority in a shared session |
| A programme chosen by score, not by the research question | medium | weak thesis contribution | the ranking orders the conversation only; the author decides (principle 3); adversarial brainstorm P2.1c |
| Integration cost of simulators (I-01, I-02) | high for I-02 | sessions consumed by tooling | spikes with kill criteria before any plan; calibrated-model fallback for I-02 |
| Phase 2 edits churn Phase 1 results ("code changed since") | high under option A | register noise; re-runs | option B (ADR-0001 default); interface carve-outs as Phase 1 steps with regression gates |
| Ideas drift from their evidence | low with the checker | ungrounded proposals | `build_phase2.py --check` in CI; anchors must exist |
| Scores read as findings | medium | false precision | scores are labelled orchestrator estimates; the generated register says so in its header |
| Continuity lost across sessions and models | medium | repeated or contradictory work | the session protocol (`README.md` §4); the session log's last entry is the brief; the handoff file |
