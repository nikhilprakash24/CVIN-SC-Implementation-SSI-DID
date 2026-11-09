# Supervisor update, November 2026 — the research side — handoff

**Author:** Nikhil Prakash (MASc, UBC ECE). **Prepared:** 2026-11-05 (v0-1, v0-2) and 2026-11-09 (v0-3), as the companion to the code-side folder `docs/outreach/2026-11-05_supervisor-update/` (branch `claude/cool-dirac-uavun2`). **Thread tag:** G-SU1. **Version:** v0-3 (hygiene pass carrying the corrections owed by the sister notes of 5 Nov; v0-1 and v0-2 kept under `_passes/` for lineage).
**Purpose of this folder:** the same six deliverables as the code-side folder, written from the non-code side — the project knowledge store (168 filed documents) and the hub repository `nikhilprakash24/cvin-sc` — so that the supervisors receive one picture, not two.

```
Research-side update   [██████████████████░░]  v0-3 — D-01…D-12 + H-01…H-04 applied; exports rebuilt; pushed to the branch beside the code-side folder
Unified thesis (D-R9)  [████████████░░░░░░░░]  both sides drafted; merge steps 2–10 not started; AI-use brief not sent
```

## What is here

| File | What it is | Code-side counterpart | Send to professors? |
|---|---|---|---|
| `01_THESIS_ON_ONE_PAGE.md` | The hub thesis on one page: working title (decision 5), RQ1–RQ3 with the answer as it stands and its status word, the unified seven chapters and what each rests on on this side, five decisions, and the table that maps the code side's RQ1–RQ5 / H1–H6 into this page's questions | `01_THESIS_ON_ONE_PAGE.md` | yes, as PDF — **together with** or **instead of** the code-side page, never without it (see 04) |
| `02_THE_WORK_SO_FAR.md` | What the research side does that I have not found elsewhere (ten items, each with its status), headline results with their evidence keys, the freeze, the three sides, the corpus by category, the drafts and what comes next | `02_THE_WORK_SO_FAR.md` | yes, as PDF |
| `03_THE_RESEARCH_PROGRAMME.md` | How the written research was done: the method rules, the lanes (figure), the working papers, the iteration instruments, the writing as a record of judgement (narrowings, the K-15 worked example, the provenance layer), the parallel-lane method, what is not in the store | `03_THE_RESEARCH_PROGRAMME.md` | yes, as PDF |
| `04_EMAIL.md` | Two variants: A, one email carrying both sides (if the code-side email has not gone); B, a follow-up (if it has). Both carry the AI-use disclosure the first email omitted | `04_EMAIL.md` | the email itself |
| `05_INTEGRATION_MAP.html` | Lane × unified-chapter map of the research side with in / on / gap state; where each thing lives (store, hub, chat, notebooks); where the two maps meet (D-R9 rules of record); the research-side decisions board; integration order | `05_INTEGRATION_MAP.html` | no (available on request) |
| `figures/research-side-map.png` | The ten research-side lanes around the dissertation, with filed / chat-only / outside-corpus states | `figures/research-programme-map.png` | inside 03 |

## Pass log (v0-2 → v0-3, 2026-11-09 — corrections owed by the sister notes)

| # | Source | Finding | Fix | Where |
|---|---|---|---|---|
| H-01 | Eight Lines note D-07 / G-SU1C U-04 | "panel", "lens", "examiner", "review" are AI roles; nothing in 01–04 said so | One sentence in 01 (decision 4), 02 (before the ten items), 03 (method paragraph), 04 (both variants) | 01–04 |
| H-02 | Eight Lines note §4 | Roots row lacked the Phase 2 count | "51 + 42 = 93 breaking points" in 02 corpus table and 03 working papers | 02, 03 |
| H-03 | G-P2 v0-2 | The §2.5 eleven-run disclosure paragraph now exists (v1-2, 201 words, drafted 5 Nov; trace keys to confirm at source) — 01, 02, 05 still said "owed" | Reworded as drafted-not-appended | 01, 02, 05 |
| H-04 | G-SU1C v0-3 | The code-side folder's revised zip (v0-3) is prepared but not on the branch; this folder's README must not imply the branch copy is current | Note added under "Known inconsistencies" | README |

## Pass log (v0-1 → v0-2)

| # | Lens | Finding in v0-1 | Fix in v0-2 | Where |
|---|---|---|---|---|
| D-01 | Research methods | 01 and 02 said the eleven pre-registration runs are "disclosed by a dated note"; the §2.5 v1-1 note discloses only the WO-1…9 deviation — the eleven are identified (FIND-R4) but not yet listed | Reworded: identified, still to be listed by a dated amendment; the integration map gains a row for it | 01 Ch4 row; 02 item 6; 05 join table |
| D-02 | Identity / external | 02 item 10 made a precedence claim for the January memos ("before the current wave of agent-identity work") | Replaced by the project-listing date (25 Jan 2026) and a rule that precedence is claimed only from dated artefacts | 02 item 10 |
| D-03 | Technical writer | The code side's "45,000 words" and the merge proposal's "38,900 incl. working notes" were both in play unreconciled | Both figures carried with their basis; 60,200 stated as prose-only | 01 chapters; 02 drafts; README |
| D-04 | Software / systems | "twelve-category document corpus" — the hub INDEX runs 00–12 (thirteen) | Corrected in 02, 05 | 02 corpus; 05 where-things-live |
| D-05 | Programme manager | "168 filed documents" was tied to the 31 October freeze; the count is of 4–5 November | Dated to the time of writing, with the note that only reporting instruments were added after the freeze | 02 freeze |
| D-06 | Research methods | "28 corrections" / "K-1…K-28" implied a dense numbering; the ledger is numbered to K-28 with gaps and unnumbered withdrawals | "numbered to K-28" everywhere | 03 instruments and judgement; figure |
| D-07 | Technical writer | Registry "3 rolls" skipped v12.0 | v11.3 → v12.0 → v13.1 | 03 instruments |
| D-08 | CAV / V2X | 03 said the June O1 measurement "has stood since" without saying it was re-run under a pin | Added "(June 2026; re-run under a pinned compiler in October)" | 03 lanes |
| D-09 | Technical writer | 04 Variant A said the two decision lists "overlap on purpose" without saying what to do where they differ | One clause added: the research-side page says which ruling was taken and why | 04 A |
| D-10 | Technical writer | Figure: two arrows crossed the Roots and Code-side boxes | Boxes moved outward, arrows re-routed; legend text unchanged | figures/ |
| D-11 | Integrity chair | README did not say that the code-side documents, if already sent, are themselves undisclosed AI-assisted drafts under the UBC rule | Stated under "Corrections and reconciliations"; 04 Variant B already covers it | README |
| D-12 | DLT | 01 "the code side's seven" (possessive) and inconsistent "code side"/"code-side" | Normalised: noun "code side", adjective "code-side" | 01, 02, 03 |

**Keep-out sweep, v0-2:** no "first" priority claim survives (the January-memo sentence was the one, D-02); "validation" appears only in the technical sense and in "validation ladder"; "unique minimum" appears only in its negation; "complete" is always qualified; no Lineage B figure is used as a result; no comparison is drawn across the two sides' gas; no Tier-1 claim; no currency figure. **Pass.**

## How the documents were checked

Every number in the three documents was taken from a filed document of record or the hub repository at `main` @ `d9f9fa3` (2026-10-31), not from the code-side documents and not from memory. Sources used, in order of weight:

- `STATUS.md` (rulings D-R1…D-R9; solc pin; key closure; CI; D-R7/D-R8 execution; push status)
- `docs/07_audits_plans/claude_CVIN_SC_Thesis_Hub_Spoke_Comparison_and_Merge_Proposal_v0-1.md` (inventory A.1/A.2; overlaps O-1…O-13; conflicts C-1…C-17; unified outline C.2; unified RQs C.3; numbers-of-record rule C.4; decisions M-1…M-12)
- `docs/10_drafts/claude_CVIN_SC_Thesis_Ch1_Introduction_DRAFT_v1-1.md` (RQ1–RQ3 verbatim; Table 1.1 C1–C14, C16/C17 proposed, C15 withdrawn)
- Project: `CVIN_SC_Precursor_Report_JulOct_Overhaul_G-PRE_v0-2.md` (five changes; function table; O1 gas table; CEV-16…18; closure; placement; scale arithmetic; corrections K-15…; cruxes; ranked solidify list)
- Project: `CVIN_SC_Phase1_Consolidated_Record_Implementation_Evidence_Argument_G-P1_v0-2.md` (boundary `f5f9fdc`; census 65 files / 1,543 tx; canonical O1 record; eight-option S1 table; coverage counts; findings catalogue; admissibility classes A–D; HDA 18 docs / 166,664 words; drift register)
- Project: `CVIN_SC_Programme_Atlas_Chat_Inventory_G-VIZ_v0-3.md` (97 chats to 14 Oct; lanes L0–L9; decisions board D-01…D-25; document register 101 files at that date)
- Project: `CVIN_SC_Supervisor_Draft_Master_Plan_G-SD1_v0-2.md` (UBC G+PS GenAI requirements, verified 2026-11-01; origin classes; R-0 gate)
- Project: `CVIN_SC_Take1_Panel_Note_PassLog_and_Roadmap_G-T1_v0-2.md` (Take 1 ≈27k words, 93 placeholders, 14 deltas; roadmap)
- Project listing: 168 documents; knowledge 1,924,884 of 2,000,000 bytes
- Code-side folder (read for the join only): README, 01–05

Corrections and reconciliations made during the first pass, so the second pass and the next session do not reintroduce them:

| Was written (somewhere in the corpus) | Is at source |
|---|---|
| "nine traces pre-date the pre-registration" (Precursor, cover briefs) | **eleven** O1 runs pre-date P, two within ten minutes (Phase 1 record §2, G-RIM FIND-R4); the Precursor's "nine" is superseded |
| HDA campaign "≈154k words" (STATUS) / "≈166,700" (Precursor) | **166,664** words, 18 files, recomputed (Phase 1 record §8) |
| "deployment gas not recorded" (Precursor, cover briefs, 22 Oct) | recorded 2026-10-23 at N = 5 on all 14 rows (STATUS; `protocol_deploy_gas_v2.csv`) |
| Hub prose "≈60,200 words" vs reading copy 80,506 `wc` | 60,200 is **prose only**, author notes excluded (merge proposal A.1); 80,506 counts notes |
| "Groth16 ≈350,000 gas" (spring drafts) | ≈181,000 + 6,150 per public input (K-18); hub age-gate `admit` measured 250,283 incl. SSTORE and event; the code side's ZkVinGate 301,163 is a different circuit — never compared |
| Code-side 01: "the thesis … seven chapters … 45,000 words" presented as the thesis | under D-R9 the unified thesis is seven chapters on the **hub** spine, ≈68,000 words; the code side's seven become Chapter 6 and parts of 2, 4, 7 |
| Code-side 04: no mention of AI assistance | UBC G+PS requires written disclosure and approval before drafts (including drafts to advisors) are relied on; both email variants in 04 now carry it, and Variant B asks that the already-sent code-side documents be treated as covered |
| Code-side 01: "≈45,000 words" for the spoke draft; merge proposal: "≈38,900 incl. working notes" at the 31 Oct text of record | both carried with their basis; the hub's 60,200 is prose only (notes excluded) |

## Known inconsistencies left standing (not fixed here)

- **Join-label swap in sister lanes (erratum filed 9 Nov, `CVIN_SC_Join_Labels_Erratum_RQ2b_RQ2c_G-SU1_v1-0.md`, copy in this folder):** G-SU1C v0-4 and the Take 1 Planning Log entry 5 record the join as "spoke RQ2→RQ2b, RQ3→RQ2c"; the hub's §C.3 (D-R9) has RQ2b = conformance (spoke RQ3) and RQ2c = security (spoke RQ2). This folder's 01 and 05 match §C.3 and are unchanged; the code-side 01 v0-4 join column and Take 1 Table 1.0 need the one-line fix before either is sent or pushed.

- The code-side folder on this branch is still the as-pushed `e2ab746` version; its revised v0-3 (G-SU1C: D-R9 reframe, 45,000 → 37,329/38,665 words, IDTx definition, AI-role sentence) exists as a drop-in zip in chat and has not been pushed. Until it is, the two folders on the branch disagree on what the thesis is; the research-side 01 is the one that matches ruling D-R9.

- `STATUS.md` still carries the stale "hub is still unpushed" sentence beside "Pushed 2026-10-20" (drift register item 2).
- Scaffolding: v0.4 is the filed SSoT; a v2.1 roll is cited by chats but unfiled (D-06).
- The Precursor's "C11 should be retitled" is a recommendation; Q-XD-2 is still the candidate's ruling.
- Dr Michelson: the January 2026 memos say he stepped away from supervision; the Precursor and cover briefs (October) still address him by lens. The email keeps `[A]`/`[B]` placeholders; the candidate confirms the recipients.

## State of the research side at the freeze (2026-10-31) and the integration order

Filed instruments are at v0-2 almost everywhere; 20 documents from the 15 August suite are at v0-1 only. The hub has five drafted chapters (Ch. 3 partial at v0-9). Take 1 exists in chat and in the repo. The drafting programmes G-GD1 and G-SD1 are planned (0/10 each); G-SD1 is gated on the AI-use agreement. Sixty-one output sets are unfiled (21 at P0). The ERC census is provisional. Two Chapter 4 lineages exist and must be re-based onto one.

Integration order (research side; the code-side map's order runs in parallel): (1) AI-use brief sent; (2) D-18 filed and R-F4 authorised; (3) one-line rulings; (4) ERC census dated and the §2.5 amendment written; (5) one Chapter 4 lineage; recompute scale arithmetic by arm; (6) D-R9 migration steps 2–4; (7) Takes 2 and 3, then G-SD1 on the unified spine; (8) the submission draft cut from the best take. Details: `05_INTEGRATION_MAP.html`.

## What the next session needs from the author

- The reply from the supervisors on the five decisions (both pages), and the AI-use agreement acknowledgement (R-0).
- The Thesis-B trunk and the Sessions B–F drafts pasted or filed (D-18), and R-F4 authorised (D-1).
- Rulings: Q16 (RQ adoption), D-04/RIM-Q15 (contributions), Q-XD-2, Q-XD-6, D-06, D-23, the title.
- Confirmation of the recipients and of whether the code-side email has already gone (which decides 04 variant A or B).
- The March–May notebooks and the three-circle framing, when ready — document 03 holds their place.
