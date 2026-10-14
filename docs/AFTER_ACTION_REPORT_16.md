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
- **K, capture (four agents in parallel).** The F1, F2 and F3 captures and the scope reconciliation were written by
  research agents and verified by the orchestrator against the files they cite. Their verified findings on Phase 1:
  - **D58:** #31 quoted ≈65–71 ms; its run of record says 103.177 ms. Re-stated.
  - **D59:** chapter 6 said 90 injected attacks; the source says 150. Fixed.
  - **D60:** #33's headline values are from the first run.
  - **D61:** the demo flag is not comparable across options.
  - **D62:** SC-13 cited the wrong row. A correction is appended.
  - **D64:** the testbed derives a vehicle's identity from an unsalted VIN hash, which undoes the VIN-privacy
    claim there.
  - The stale-figure checker gained entries for each changed value, and each was shown to fire.
- **Register.** Rows **#49** (on-chain footprint), **#50** (relayed writes) and **#51** (read cost against history)
  were added from the existing run of record `7a9a996`, with no new run. Rows #49 and #50 make F1 and F3 quotable.
  Row #51 came from the review (AR-15).
- **C0.** WM-2 step C0:
  - **Amendment A6** was committed (`c7e333f`) before any verifier change.
  - **Verifier v3** fixes D37, D38, D39 and D41, documents D40, and adds the D42 gate (`7d08dce`). Each of its 26 tests
    failed on v2; the 100,000-deep message segfaulted the v2 process (D37 reproduced). The mutation script now covers
    both test files and kills 39 of 39 mutants.
  - **D51 fixed.** Validity is decided in chain time, at one more `eth_getBlockByNumber` per full resolution. Two
    tests fail on the old provider; three pinned RPC patterns were updated. The testbed suite (134 tests) passes on a
    genuinely fresh node and on one 2,000 s ahead.
  - **A slip, caught.** My first "fresh node" run had gone to the old node: killing npx's wrapper left the node alive,
    and the restart could not bind the port. A port check caught it. The correct procedure is now in the handback.
- **C0 runs of record.** These ran in a clean worktree at `7d08dce`.
  - **I1 = 1.226 [1.219, 1.238], outside the band and not falsified.** It was 1.096 PASS on v2. SPaT warm moved
    0.182 → 0.184 ms, while BSM warm, which v3 does not touch, moved 0.166 → 0.149 ms on a different host build. The
    cause is **not isolated**. The verdict is reported as it fell, with no re-run to chase the band. The verifier walks
    a credential it does not use on the warm path; that is logged as D65, and its effect is not isolated.
  - **I2 PASS:** 15 checks, with the warm variants verified warm.
  - **I3 PASS:** 0, 4 and 24 messages accepted after a revocation at k = 1, 5 and 25.
  - **I5:** 0.900 ms.
  - Rows #44–#46 and #48 were re-stated with their old values as history. The README, the thesis README, chapter 5,
    the presentation (and its "attacks"/"checks" wording) and the scope reconciliation were updated, with stale
    entries for 1.096 and 0.886 ms.
- **F1–F3 packages.** Each has a README (executive summary), CAPTURE, ANALYSIS, PLAN and EXECUTION.
  - **F1 execution:** an IDTx prototype against the unmodified ERC-1056 registry.
  - **F2 execution:** a SQLite lifecycle backend with a hash-chained, append-only journal.
  - **F3 execution:** a generated mode classification.
  - **Shared:** five figures with table views (now four, after AR-38), the consolidated `PHASE2_PROGRAMME.md`, and the
    chat-workspace brief with its inbox.
- **Writing team.**
  - **Technical writer:** edited the READMEs, analyses and the scope executive summary. Its script showed every
    number, ID and path unchanged.
  - **Career ECE academic:** wrote the scope reconciliation and a review of F1–F3. The review had 41 findings, 11 of
    them H. It judged none of the three packages defensible as written: the summaries had been written ahead of their
    captures.
  - **Dispositions:** 40 fixed, 1 fixed in part (`docs/phase2/reviews/DISPOSITIONS_F1-F3.md`).
  - **Main corrections:**
    - one IDTx definition, under which only 4 of 26 Phase 1 gates are IDTx;
    - "no contract can read a log" narrowed to direct reads;
    - #33's FAIL restored;
    - the cross-run read-mode ratio and its figure withdrawn;
    - "only Mode C fits" stated per path and host;
    - the radio claim made an argument;
    - gas transfer stated with its conditions;
    - the prototype's caller semantics and the commitment's setter binding;
    - the database's limits made explicit (rewrite, tail truncation).

    The F2 and F3 rewrites were delegated to an agent and checked by targeted searches; one cell, the validium row,
    turned out to be already present.
- **Grand run (last).** ALL OK: smoke 11 adapters, L1 99, Hardhat 537, Python layers **331**, 92 demos / 1,752 steps
  (594 mined transactions). Python layers rose from 305 by the 26 verifier-v3 tests; the commit message of `7d08dce`
  and parts of the first records said 25, which was a miscount, corrected in the register (#45), the plan and this
  report. Generated documents were regenerated after the run, including the F3 mode classification.
- **A container restart and a usage-limit pause** interrupted the pass. The working tree survived both. The C0 run logs
  were preserved as `.txt` because `*.log` is ignored. Part 1 of the review fixes was committed at `d881f02`.

## 3. Closing
The pass delivered every step of §1.

**C0 is done.** I1 is reported as it fell (outside the band, not falsified), and I2 and I3 pass on verifier v3. D51 is
fixed in code; rows #21, #32 and #37 keep their assumption until A3b.

**The three focuses are each a complete package.** Each has a capture, an analysis, a plan and a first executed step,
and each has been reviewed and corrected.

The most useful outcome was the review itself. It found the packages overclaiming in the summary layer, and the
corrections made the IDTx a sharper concept: 4 of 26 Phase 1 gates qualify, not 25. An unchecked F1 lead also
uncovered a real privacy flaw in the testbed (D64).

**Next:**
- Phase 1, WM-2 step B1 (deterministic gas or ranges).
- Phase 2 session 3 (`docs/phase2/sessions/SESSION_LOG.md`).
- The author's decisions P2-D7 to P2-D10, D-1 to D-15, and N-23.

