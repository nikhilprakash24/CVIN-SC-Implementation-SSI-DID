# CVIN-SC · Erratum — the RQ2b / RQ2c join labels are swapped in two lanes

**Document ID:** `CVIN_SC_Join_Labels_Erratum_RQ2b_RQ2c_G-SU1_v1-0` · **Thread:** G-SU1 (cross-lane) · **Date:** 2026-11-09 · **Status:** erratum of record; one fix, three places to apply it.

## The finding

The source of record for the unified sub-questions is the hub's merge proposal, adopted by ruling D-R9 (30 Oct):

> `docs/07_audits_plans/claude_CVIN_SC_Thesis_Hub_Spoke_Comparison_and_Merge_Proposal_v0-1.md` §C.3 —
> RQ2a (spoke RQ1/H1) gas · **RQ2b (spoke RQ3/H2) conformance** · **RQ2c (spoke RQ2/H5) security** · RQ2d (spoke T4/H4) MOBI VID · RQ3a (spoke RQ5/H6, custodian half) · RQ-V (spoke RQ4/H3) · RQ-V2 (spoke RQ5, feasibility half).

On the code side, **spoke RQ2 is Security and spoke RQ3 is Conformance** (`docs/outreach/2026-11-05_supervisor-update/01_THESIS_ON_ONE_PAGE.md` L18–19, as pushed at `e2ab746`). So the correct join is **RQ2b ← conformance (spoke RQ3)** and **RQ2c ← security (spoke RQ2)**.

Two lanes recorded the join as "spoke RQ1→RQ2a, **RQ2→RQ2b, RQ3→RQ2c**, H4→RQ2d, RQ4→RQ-V, RQ5→RQ-V2 + RQ3a", which maps security to RQ2b and conformance to RQ2c — the reverse of §C.3:

| Where | What it says | Status |
|---|---|---|
| `CVIN_SC_SupUpdate_CodeSide_Revision_Panel_Note_and_Thesis_Version_Ruling_G-SU1C_v0-4.md` §1 (and the v0-3/v0-4 code-side 01 join column it describes, flagged ⟦to check against the research-side 01⟧) | RQ2→RQ2b, RQ3→RQ2c | **swapped** |
| `CVIN_SC_Take1_Planning_Log_G-T1_v0-3.md` entry 5 ("Table 1.0 re-written to them") and therefore Take 1 v0-3/v0-4 Table 1.0 | RQ2→RQ2b, RQ3→RQ2c | **swapped** |
| Research-side `01_THESIS_ON_ONE_PAGE.md` join table and `05_INTEGRATION_MAP.html` join row (G-SU1 v0-1…v0-3) | RQ3 conformance → RQ2b; RQ2 security → RQ2c | matches §C.3 — no change |

The swap is a label error, not a content error: in every document the *descriptions* (gas, conformance, security, VID) are attached to the right spoke results; only the letters b and c are crossed. It matters because the research-side one-pager and the code-side one-pager would reach the supervisors disagreeing on which sub-question is which, and because Take 1's Table 1.0 would seed Takes 2–4 with the swap.

## The fix (one line, three places)

Wherever the join is stated, write it as **spoke RQ1→RQ2a · spoke RQ3→RQ2b · spoke RQ2→RQ2c · H4→RQ2d · spoke RQ4→RQ-V · spoke RQ5→RQ-V2 + RQ3a**, or — safer — name the topic beside each letter (RQ2a gas · RQ2b conformance · RQ2c security · RQ2d MOBI VID) so the spoke numbering never has to be remembered.

1. **G-SU1C code-side folder (v0-4 zip, unpushed):** the join column on 01 and the §1 sentence of the panel note; re-export 01. Record as U-05 in `PASS_LOG_G-SU1C.md`.
2. **G-T1 / G-T2:** Take 1 v0-4 Table 1.0 (and any Take 2 chapter that quotes it); log as the next Planning Log entry.
3. **Anything downstream that copied the shorthand** (G-GD1 Charter/TOC v0-3 if it carries a join line; G-SCR committee report v0-2 if it does) — grep for "RQ2→RQ2b".

No ruling is needed: §C.3 is already the ruling. Research-side folder: unchanged.

## Why it happened

The shorthand "RQ2→RQ2b, RQ3→RQ2c" reads naturally in sequence and was carried between lanes as text rather than checked against §C.3, where the lettering follows the *hub's* reading order (cost, conformance, security, VID), not the spoke's question numbers. Rule for the migration (D-R9 step 2, re-label RQs): **never state a join by numbers alone; always pair the letter with its topic.**
