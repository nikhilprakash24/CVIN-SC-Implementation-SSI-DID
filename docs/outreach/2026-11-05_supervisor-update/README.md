# Supervisor update, November 2026 — handoff

**Author:** Nikhil Prakash (MASc, UBC ECE). **Prepared:** 2026-10-31 to 2026-11-05, in one working session.
**Purpose of this folder:** everything needed to pick this thread up in another session: the three documents sent to
the supervising professors, the email that carries them, the branch-level integration map, and the state of the work
that the documents describe.

## What is here

| File | What it is | Sent to professors? |
|---|---|---|
| `01_THESIS_ON_ONE_PAGE.md` | The dissertation on one page: title (working; decision 5), RQ1–RQ5 and H1–H6 with measured verdicts, the seven chapters and what each rests on, five decisions for the supervisors | yes, as PDF |
| `02_THE_WORK_SO_FAR.md` | What exists: ten things the work does that the author has not found elsewhere, headline results with register rows, the freeze point, the two sides not included, the repository by layer, thesis draft 1 | yes, as PDF |
| `03_THE_RESEARCH_PROGRAMME.md` | How the work was done: the lines of exploration, the research working papers, how the content iterated, the code work as a record of judgement, the parallel-stream method, what is not in the repository | yes, as PDF |
| `04_EMAIL.md` | The email text, final | the email itself |
| `05_INTEGRATION_MAP.html` | Branch-level map of every workstream against the thesis chapters, with merge state and merge order; a working document, not sent | no (available on request) |
| `figures/BP-001.png` | Blueprint sheet BP-001, the layer ladder, shown in document 02 | inside 02 |
| `figures/research-programme-map.png` | The drawn map of eight lines of exploration around the dissertation, shown in document 03 | inside 03 |

The live, editable originals are Claude Docs owned by the author (private; the Markdown here is the export of record as of
2026-11-05). Document 02's date chip reads 31 October 2026, the freeze point; 01 and 03 read 4 November 2026.

## How the documents were checked

Every number in the three documents was verified against its primary file in this repository, not against the
README or the thesis chapters (both of which carry stale values; see "Known stale values" below). Sources used:

- `docs/MEASUREMENT_CONDITIONS.md` rows #4, #24, #25, #27, #28, #36, #44, #46, #56–#62
- `docs/thesis/CHAPTER_AUDIT_2026-10.md` (92 claims: 39 OK, 53 to fix; Hardhat 563, Python 376)
- `docs/thesis/CRUX_REGISTER.md` (8 cruxes, all partial)
- `docs/SCOPE_CHANGES.md` (26 entries; **SC-04**: priority claims to be reworded as "measured, domain-constrained,
  reproducible"; **SC-14a**: MOBI VID I v2.0 checked clause by clause, 2 of 8 MUSTs met, birth certificate 7 of 15
  mandatory fields)
- `docs/DECISION_SHEET_2026-10-20.md` (**D-14**: title replacement recommended, author decision open → decision 5 in 01)
- `docs/DEFECT_LOG.md` (67 unique defect ids), `docs/AFTER_ACTION_REPORT_*.md` (numbered to 41 on the cv2x branch),
  `SIDE_PAPERS.md` (8 registered; SP-9 proposed on `claude/determined-meitner-q2at9c`)
- `docs/roots/README.md`, `docs/phase2/IDEA_REGISTER.md`, `docs/zkp/README.md`, the research-expansion README on
  `claude/cvin-research-improvements-559o01`
- Repository visibility: public. All 12 deep links sampled resolve unauthenticated.

Corrections made during the passes, so the next session does not reintroduce them:

| Was written | Is at source |
|---|---|
| Infrastructure SPaT ratio 1.226× | **1.197×** [1.193, 1.201], 2026-10-22 run of record, at the edge of the band, not falsified (#44) |
| 81 defects | **67** unique ids |
| 42 after-action reports | **41** (file 06_CLONE_LINEAGE is a duplicate-numbered addendum) |
| Nine side papers | **Eight** on the default branch, a ninth proposed on a branch |
| "about 95 sources" (research expansion) | **88** catalogued |
| "first comparison", "first working implementation" | reworded per SC-04 and SC-14a: "I have not found elsewhere"; "a working, measured implementation of MOBI VID's published concepts" |
| MOBI VID listed among the nine standards | the ninth is **LSP8**; MOBI VID is the application profile measured alongside |

## Known stale values in the repository itself (not fixed here)

`README.md` and `docs/thesis/README.md` still quote the infrastructure ratio as 1.226× and V2V warm verify as 0.153 ms.
The register says 1.197× (#44) and 0.142 ms (#27). These belong to the chapter-audit step in the merge order below,
not to this folder.

## State of the branches at the freeze (2026-10-31) and the merge order

A trial merge of every live branch into a scratch copy of `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` found:

- the default branch (`claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt`) and cv2x have diverged (cv2x 24 ahead, 5 behind);
- `claude/upbeat-hawking-9v0s2i` conflicts on 15 files, all regenerable results (register, grand report, dashboard, result
  cards, TDP-003/008, DWG-001.svg); resolve by taking its run of record (`2026-10-31T03-29-43Z_291a801`) and regenerating;
- `zkp-ai-identity-research`, `simulation-visual-plan`, `testing-suite-organization`, `determined-meitner` all merge clean;
- no thesis chapter cites any figure (BP sheets, F-series, IDTx, x-series); figure integration has not started.

Merge order, agreed: (1) settle one trunk; (2) merge upbeat-hawking by regeneration, run the stale-figure checker;
(3) merge zkp (two chapter-2 absence claims await author sign-off); (4) merge simulation visuals, place F-series and
BP sheets into chapters per `docs/blueprints/INTEGRATION.md`; (5) merge testing charters; (6) merge determined-meitner,
move the 12×10 comparison into ch. 5 / ch. 6 §6.8 / Appendix G; (7) re-run the chapter audit against the settled
register; (8) decide `vid-build` and `cvin-research-improvements` (merge, future work, or archive), then front matter
and appendices. Details and the per-branch ledger: `05_INTEGRATION_MAP.html`.

## What the next session needs from the author

- The March–May 2026 notebooks (100+ pages) and the written research side (surveys, systematic reviews, the three-circle
  framing and its seven perspectives, the 2026 update, the agentic-identity programme). Document 03 holds a place for
  them under "Not in the repository" and in the two dashed boxes of its map.
- Decisions: D-14 (title), the two chapter-2 absence claims, SC-04 wording in chapters 1 and 7, and the five decisions
  put to the supervisors in document 01, once they reply.
