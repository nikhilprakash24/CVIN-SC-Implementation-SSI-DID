# After-Action Report 16 — Phase 2 Focus Areas F1–F3, Scope Reconciliation, Writing Team, WM-2 C0

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-14, after report 15 closed at `5509b6a` (CI 8/8 green on `4b2b30c`); closed at the end of this pass
**Brief (the author, 2026-10-14):** accept defaults and continue to the next executable; output the Phase 2
document with an accompanying document for hand-off to a chat workspace with tools; coalesce Phase 2 with the
thesis scope; results sections, written work, figures, tables and executive summaries that allow a seamless
first reading; work agentically, with a technical writer and a career ECE academic on the team. Three major
focuses, each with separate analysis, capture of previous work, planning and start of execution:
**F1** on-chain data storage versus not, and the **identity-dependent transaction** (the author's term, "IDTx",
also "IDDTx" or "IDBTx"); **F2** public and private blockchains and other databases; **F3** three modes or
methods of communication with the chain for reads and writes.

## 1. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| K | Capture of Phase 1 evidence for F1, F2, F3 and for the thesis scope history, by four research agents in parallel (read-only) | research agents; career ECE academic (scope) | every claim cites a file or a register row; the orchestrator spot-checks numbers against the register |
| F1 | `docs/phase2/focus/F1_onchain_storage_idtx/`: executive summary, capture, analysis (storage locus taxonomy; IDTx definition, taxonomy, threat and cost model), plan (pre-registration draft), start of execution (an IDTx prototype with tests; no reported numbers) | orchestrator; contracts engineer; SSI specialist | prototype tests pass and fail on a broken gate; no Phase 2 number reported as a result |
| F2 | `…/F2_chains_and_databases/`: same five parts; start of execution: a database lifecycle backend beside the in-memory and on-chain ones, behind the same interface, with parity tests | orchestrator; measurement methodologist | parity tests pass; the backend registers as a producer before any run |
| F3 | `…/F3_interaction_modes/`: same five parts; the three-mode taxonomy proposed as a default (author decision); start of execution: every Phase 1 operation and demo step classified by mode, generated from committed code and data | orchestrator; V2X specialist | the classification is generated and checked in CI |
| FIG | Figures and tables for the three focuses, generated from committed data by one script, per the visualisation rules | visualisation engineer | `--check` in CI; figures render; palette validated |
| SC | Scope reconciliation: the thesis scope across its revisions, Phase 2 placed against it (thesis / paper / future work / handed to others), with justification | career ECE academic | every placement justified; author decision listed |
| W | Writing review: a technical writer edits the executive summaries and the consolidated document for a seamless first reading; the academic reviews claims, framing and scope discipline | technical writer; career ECE academic | every review item applied or answered |
| P2 | The consolidated Phase 2 document and the chat-workspace hand-off brief | orchestrator; technical writer | the brief is self-contained and names what to bring back and in which format |
| C0 | WM-2 C0: verifier v3 (D37–D42) and the D51 provider fix; dated pre-registration amendment first; each fix with a test that fails on the old code; I1–I3 re-run on a clean tree, alone on the host | orchestrator; security specialist | as `docs/PLAN_WM-2.md` C0 |
| R | Records, grand run last, CI | orchestrator | CI green on the closing commit |

## 2. Execution log
- 2026-10-14 — report opened.
