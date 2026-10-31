# Phase 2 Session Log

**Author:** Nikhil Prakash (MASc, UBC ECE). **Rule:** one entry per Phase 2 session, newest last. The last
entry's "Next session" block is the brief for the next session (`docs/phase2/README.md` §4).

## Session 1 — 2026-10-14 (P2.0 ideation; after-action report 15)
**Done.**
- Charter, name space, principles, sub-phases with gates, session protocol (`README.md`).
- Evidence base: Phase 1 assets, 18 seeds with sources, chapter 7 future work mapped, cruxes mapped
  (`EVIDENCE_BASE.md`).
- Idea register as data: 23 ideas in 7 tracks, each anchored and killable, scored (orchestrator estimates),
  5 candidate programmes. Generated `IDEA_REGISTER.md`, with `build_phase2.py --check` in CI.
- Architecture sketch: seven planes mapped to Phase 1 code, six interfaces with reference implementations,
  three structural options, five open questions (`ARCHITECTURE.md`).
- Roadmap with session plan, dependencies on Phase 1, risks (`ROADMAP.md`).
- Brainstorm 1: method, 25 divergent items, 5 parked, 3 register gaps, 5 questions for the author.
- Decisions: P2-D0 decided by the author; P2-D1…D6 open with defaults; ADR-0001 proposed, ADR-0002 accepted,
  ADR-0003 proposed.

**Register state.** Top five by computed total: I-05, I-16, I-01, I-03, I-13 (`IDEA_REGISTER.md`).

**Next session (session 2, P2.1a–b).**
1. Read `README.md` §4 and `DECISIONS.md`. Apply any author answers to Q-P2-1…5. Record overrides first,
   then edit `ideas.yaml` and rebuild.
2. Write deep-dive briefs `docs/phase2/briefs/I-05.md`, `I-16.md`, `I-01.md`. Each covers canonical sources
   actually read, the state of the art, the first experiment and its prediction (written before any run),
   size in sessions, and the kill criterion re-checked.
3. Do not start any build. Phase 1's next step (WM-2 C0) keeps priority if the session is shared.
4. Close with an entry here naming session 3's work (briefs for I-03 and I-13; adversarial brainstorm P2.1c).

## Session 2 — 2026-10-14 (the author's three focuses; after-action report 16)
**Done.**
- **Focuses.** F1 (on-chain storage and the IDTx), F2 (chains and databases) and F3 (interaction modes), each with
  capture (research agents, verified), analysis, a pre-registration draft and a started execution:
  - F1: an IDTx prototype, 10 tests, 3 mutants caught;
  - F2: a database backend with a hash-chained journal, 6 tests;
  - F3: a generated mode classification, in CI.
- **Figures.** Five generated figures with table views (CI-checked).
- **Scope reconciliation** by the academic adviser: Scope v3, placements, an 8-paper map, examiner questions and
  15 decisions.
- **Writing review.** A technical writer edited the executive summaries and analyses; an academic review of F1–F3 is
  in `reviews/`.
- **Consolidated document and hand-off.** `PHASE2_PROGRAMME.md` and the chat-workspace brief with its inbox.
- **Register.** Ideas I-24 to I-26 and programme PG-focus (author-designated). Register rows #49 and #50 added from the
  existing run of record.
- **Phase 1 findings made on the way:** defects D58–D64, among them D64 (the testbed derives vehicle identity from an
  unsalted VIN hash).

**Next session (session 3).**
1. Dispose of any academic-review findings left open (`reviews/ACADEMIC_REVIEW_F1-F3.md`); apply the author's answers
   to P2-D7 to P2-D10.
2. If the author returns inbox files, run the intake (`CHAT_WORKSPACE_BRIEF.md` §5).
3. Write deep-dive briefs for I-24 (IDTx) and I-05 (freshness theory), each citing sources read at origin.
4. If the author adopts D-15, start chapter 2's IDTx positioning from the W1 literature.
5. Phase 1's next step (WM-2 B1) keeps priority in a shared session.


## Session 3 — 2026-10-20 (deep-dive briefs; after-action report 23)
**Done.**
- **Briefs** in `docs/phase2/briefs/`, each by a research agent and accepted after the orchestrator re-fetched a third
  or more of its sources at origin and found each quote in the fetched text:
  - **I-24, IDTx** (18 sources, 8 not read). Findings for the author: the mechanism is not new (ERC-3643 checks the
    receiver's identity claims on transfer; Luu et al. 2016 proposed guarded transactions); "named identity, not
    caller" does not separate IDTx from attribute-based access control (NIST SP 800-162); E-F1-1 alone cannot decide
    the kill criterion, so the brief proposes tying it to E-F1-2 and E-F1-3 before the F1 plan is locked.
  - **I-05, freshness theory** (15 entries, 7 not read; two Springer sources not re-verifiable from the container).
    It derives the optimal policy under a capacity budget and an exposure cap (the knee itself,
    k_min = ceil(t_chain / (B − t_local))), explains the host dependence found in #52, and states predictions P1 and
    P2 as predictions with their inputs from V rows and one unchecked assumption (equal RPC cost after D51).
- **Register:** I-24's first step corrected to 12 behaviour tests.
- Items 1, 2 and 4 of session 2's list: no review finding is open beyond AR-13 (deferred by decision); the inbox is
  empty; D-15 is not yet adopted, so chapter 2's positioning waits.

**Next session (session 4).**
1. The author's decisions on the I-24 findings (keep the paper, or IDTx as a taxonomy) and P2-D1, P2-D7 to P2-D10.
2. If the author adopts P2-D1 with I-05: write the cost model's assumptions into F3's plan and pre-register P1.
3. Inbox intake if files arrive; D-15 positioning if adopted.
4. Phase 1 keeps priority: the cross-model check of passes 16–22, then WM-2 A3.
