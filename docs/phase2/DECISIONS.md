# Phase 2 Decisions — Author Decisions and Architecture Decision Records

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-14 (Phase 2, P2.0, session 1). **Binds:** `docs/phase2/README.md` (principle 3).
**Rule:** an author decision is recorded here before the work it changes. Defaults are the orchestrator's and
labelled so; they stand until the author overturns them. An overridden default stays in the table with its
date and the replacement.

## 1. Author decisions
| # | Decision | Orchestrator default (until decided) | Needed by | Status |
|---|---|---|---|---|
| P2-D0 | Start Phase 2 now, as documents only, alongside WM-2 | yes: the author asked for it ("start the PHASE 2 Ideation, Architect, Planning and Brainstorming", 2026-10-14) | P2.0 | **decided by the author** |
| P2-D1 | Which programme (PG-alpha, beta, gamma, delta, or a mix), and which ideas inside it | none chosen; P2.1 briefs the top five ideas after intake and runs the adversarial brainstorm | G1 (session 4) | open |
| P2-D2 | Phase 2's time box and its relation to the defence (Q-P2-1) | both: the first build wave may feed the thesis; the rest follows it | G1 | open |
| P2-D3 | Accept the session-1 scores and ideas as the starting register (Q-P2-5) | yes, as orchestrator estimates | P2.1a | open (default in force) |
| P2-D4 | SUMO install (N-4) and Sepolia (N-11) for Phase 2 (Q-P2-3) | Phase 1 defaults unchanged (no) | before I-01 / I-03 build | open |
| P2-D5 | C8 framing and whether Phase 2 gives it a hypothesis (Q-P2-4) | unchanged | P2.1 | open |
| P2-D6 | Where Phase 2 code lives (ADR-0001) | option B, a plug-in layer (`ARCHITECTURE.md` §3); the F1 prototype and the F2 backend already live in `phase2/` under it (reversible) | G2 | proposed |
| P2-D7 | The three modes of chain interaction (F3) | two options, mapped onto each other: the academic adviser's for the thesis (write: direct, relayed, account-abstracted; read: on demand, cached, offline; all six cells measured), and the orchestrator's single axis as Phase 2's analytic frame (A direct, B-submit / B-serve, C detached) | before chapter 6's F3 section | open (both defaults stated) |
| P2-D8 | The name and definition of the identity-dependent transaction | name IDTx (IDDTx and IDBTx retired, academic adviser's D-6); definition: the academic review's §3.3 (`reviews/ACADEMIC_REVIEW_F1-F3.md`), excluding sender authentication and identity administration, with "identity-dependent decision" for the off-chain counterpart (review Q1) | before any writing that names it | open (default in force) |
| P2-D9 | Install a permissioned EVM client for F2's substrate study | no, until after the defence | E-F2-1 | open |
| P2-D10 | Adopt the scope reconciliation's Scope v3 and its decisions D-1 to D-15 (`SCOPE_RECONCILIATION.md` §6) | as recommended there | WM-2 D1 (chapters) | open |

## 2. Architecture decision records
| ADR | Title | Status | Context and decision |
|---|---|---|---|
| ADR-0001 | Where Phase 2 code lives | **proposed** (decided at G2) | Options A in place, B plug-in layer, C separate repository (`ARCHITECTURE.md` §3). Proposed: B, so that Phase 1 results of record stay stable and every interface carve-out is a small Phase 1 step with a regression gate. |
| ADR-0002 | Every Phase 2 producer is a registered producer of record from its first commit | **accepted** (follows from Phase 1 rules) | Phase 2 producers are listed in `tools/run_identity/producers.json`, write to `runs/` and reach a tracked result path only through `promote.py` (WM-2 A2, A4). No exception for exploratory runs: those stay in `runs/` and are never cited. |
| ADR-0003 | The implementation of each interface is recorded in the result's stamp | **proposed** | `ARCHITECTURE.md` §2 contract 2: mobility, channel, ledger target, credential suite and revocation policy are named in every result. Open question AQ-1: how the scope resolver sees run-time-selected implementations. |
