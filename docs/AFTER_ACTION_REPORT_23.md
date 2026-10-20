# After-Action Report 23 — Phase 2 Session 3: Deep-Dive Briefs for I-24 (IDTx) and I-05 (Freshness Theory)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-20, after report 22 closed at `bf4ca58` (CI 8/8 green on `160b425`); closed at the end of this pass
**Brief (the author, 2026-10-20):** continue.

## 1. Why this step and not A3
WM-2's next executable is the check of passes 16–22 by a different assistant model
(`docs/milestones/check_passes_16-22/CHECK_BRIEF.md`), then A3. The check is only independent if a different model
does it, and A3 turns more results into runs of record, which the check is meant to precede. This pass therefore takes
the next item that touches no result of record: Phase 2 session 3 (`docs/phase2/sessions/SESSION_LOG.md`, session 2's
"Next"). The check brief now tells the checker to use the next free report number.

## 2. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| S3-0 | Session 3's items 1, 2 and 4: open review findings, inbox intake, chapter 2 positioning | orchestrator | each item done or stated as waiting, with the reason |
| S3-1 | Deep-dive brief for **I-24** (identity-dependent transactions): literature, tooling, size, risk, first experiment | research agent (literature) with the orchestrator | every cited source fetched at its origin, with a URL, and quoted where a claim rests on it; the orchestrator re-fetches a sample of at least a third of the citations and rejects the brief if one does not say what the brief says |
| S3-2 | Deep-dive brief for **I-05** (revocation freshness theory): the same five parts | research agent (literature) with the orchestrator | the same gate |
| S3-3 | Records: session log entry 3, idea register (`ideas.yaml` → `build_phase2.py`), report closing | orchestrator | `build_phase2.py --check` and the document checks pass; CI green |

**Rules for this pass.** No Phase 2 number is a result (Phase 2 principle 4); predictions are labelled as predictions.
A source that could not be fetched is listed as not read, never cited as read. Briefs live in
`docs/phase2/briefs/`.

## 3. Execution log
- 2026-10-20 — report opened.
- **S3-1, brief I-24 accepted after its gate.** The research agent wrote `docs/phase2/briefs/I-24_IDTX.md` with 18
  cited sources (15 literature, 3 tooling) and 8 not read. I re-fetched 10 of the 18 at their URLs and checked each
  quote in the fetched text: 7 exact, 2 differing only in whitespace from stripped markup (S04, S09), and the Oyente
  PDF exact once its ligatures were joined (S01). None differed in substance. The brief's main findings: the
  mechanism is not new (ERC-3643 transfers check the receiver's identity claims; Luu et al. 2016 proposed guarded
  transactions), "named identity, not caller" does not set IDTx apart from attribute-based access control (NIST SP
  800-162), and E-F1-1 alone cannot decide the kill criterion. Those are findings for the author's decision; the plan
  is not changed here. The agent found that `ideas.yaml` said "10 behaviour tests" where the file has 12; corrected,
  register regenerated.
- **Progress report planned.** The author asked for a hand-over write-up from July onwards; the plan is in
  `docs/planning/PROGRESS_REPORT_PLAN_2026-10-20.md`, for report 24, with the two decisions it needs.
- **S3-2, brief I-05 accepted after its gate.** 15 cited entries from 14 documents, 7 not read. I re-fetched 7 sampled
  plus S06's PDF: 8 verified (6 exact, S09 whole but for markup whitespace, S06 exact from the PDF after the abstract
  page gave nothing). S01 (Rivest, Springer) could not be re-verified: three addresses each served a 2,950-byte block
  page. The brief says so in its closing note. The agent's own least-sure claims (its hit-fraction derivation, P2's
  equal-RPC-cost assumption, S13's venue from a CV) stand in the brief as stated; none is a result.
- **S3-0.** No open review finding beyond AR-13 (deferred by decision); inbox empty; D-15 not adopted, so chapter 2's
  positioning waits. Stated in the session log.
- **S3-3.** Session log entry 3, handback §14, manifest. `build_phase2.py --check` and the document checks pass.
- **No grand run this pass:** it changed no code, test, result file or register row (documents only), as report 20
  did for the same reason.
