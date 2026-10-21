# After-Action Report 25 — TDP Runbook Phase 10: Thesis Adaptation Map onto Chapter 3

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-21, after report 24 closed at `b7ea6f4` (CI 8/8 green on `46f8d1f`) and report 20 closed at
`a9b03c2`; closed at the end of this pass
**Brief (the author, 2026-10-21):** run runbook phase 10 and map the package onto chapter 3; continue; integrate
deeply with the recent work (passes 21 to 24).

## 1. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| P10 | `docs/tdp/TDP-010_THESIS_ADAPTATION_MAP.md`: every shall-statement of TDP-002 mapped to the chapter 3 section that carries its commitment (or chapters 5 to 7 where the commitment is a result, an interpretation or a limitation), with the state of the current chapter 3 text against it (carries, absent, contradicts, with the line), and the sentence that would carry it in the thesis register; a drift table of chapter 3 against the register and passes 21 to 24; a proposed chapter 3 outline v2 | orchestrator; thesis methodologist | every number a V row; stale-figure checker clean; no chapter file edited (phase 10 writes the map, WM-2 D1 edits the chapters) |
| R | Index row in TDP-000; runbook phase 10 marked executed; handback addendum; manifest; `tools/prepush_check.sh` before the push; CI read and recorded | orchestrator | CI green on the closing commit |

**Defaults (the author may overturn).**
| # | Decision | Default |
|---|---|---|
| P10-a | Chapter 3 is not edited in this pass | the map carries the sentences ready to paste; D1 (WM-2) makes the edits once D-1 to D-15 are decided, so a sentence is not written twice |
| P10-b | Where a current chapter 3 sentence contradicts the register, the map says so with the line number | no softening; the sentence that replaces it cites the row |
| P10-c | The recent work enters chapter 3 as method, not result | C1 (resolver reads the chain with a provider), C2 (consent rule for attestation), the I-05 model and the I-24 positioning each get a method sentence; their numbers stay in chapters 5 and 6 |

## 2. Execution log
- 2026-10-21 — report opened.
- **P10, the map.** `docs/tdp/TDP-010_THESIS_ADAPTATION_MAP.md`. Chapter 3 was read in full (539 lines). Each of the
  36 requirements is mapped to a section with the state of the current text: 2 carry, 6 partial, 5 contradict, 23
  absent. The five contradictions are the hypothesis wordings of lines 51, 53 to 55 and 259 to 260 (the ten-times
  claim, the end-to-end budget and the ten-millisecond target, the hybrid on the frontier) and line 398 ("not a
  self-scored checklist" against the register's "internal and self-scored"). The largest omissions are the whole
  message-path hardening of passes 9 to 16 (freshness window, replay, the re-check cadence, the clock rule), the
  infrastructure method (I1 to I5), the metrics harness, the pre-registered parity and pseudonym experiments, and the
  evidence machinery. One factual slip in chapter 3 is recorded as drift item 6: it says three attacks are injected
  per run and expects 3 × N failures; the run of record injects five and records 150 failures over 30 runs (#27).
- **Integration with passes 21 to 24.** C1 enters as the second half of the STD-01 sentence (the resolver reads the
  registry when given a provider; the checker and suite inputs resolve without one, so #4 and #24 did not move; N-24).
  C2 enters as the SEC-05 sentence (owner or `veriKey` delegate, once per event) with its gas left to chapter 5. The
  I-24 brief enters as one limit sentence in 3.2.3 (no identity-dependent transaction is measured) and nothing more,
  because the brief itself places the taxonomy in chapter 6 and the positioning in chapter 2. The I-05 brief enters as
  the method's model in the new 3.4.7, labelled fitted to #32 and tested out of sample at the next run. The decision
  sheet is cited at each sentence that waits on a decision (D-1, D-4, D-12).
- **Records.** TDP-000 index row; runbook phase 10 marked executed; TDP-PLAN revision line; handback section 16;
  manifest. `tools/prepush_check.sh` was run: its feature-matrix step fails in this container because no compiled
  artifacts exist here (the generator shrank the tracked file, restored with `git checkout`); every other document
  check passes, including the progress appendix after regeneration.

## 3. Closing
The pass delivered P10 and R. CI result on the closing commit: recorded in the "Report 25 closed" commit.

**No chapter was edited.** The map holds 36 sentences ready to paste and a sixteen-item drift table; WM-2 D1 applies
them once D-1 to D-15 are decided (the decision sheet's section A). Five of the sixteen drift items are
contradictions between chapter 3 and the register; eleven are omissions. None needs a new measurement.

**Next:** the author's answers on the decision sheet; then WM-2 D1 with this map as its worksheet; for the package,
runbook phases 8, 9, 11 and 12.
