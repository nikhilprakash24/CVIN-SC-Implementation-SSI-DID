# Milestones — how the work is cut

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-10 (after-action report 12, step W1)

Two kinds of milestone, nested.

| Kind | What it is | Identified by | Who closes it | Examples |
|---|---|---|---|---|
| **Overall milestone** | a version of the research artefact that the author releases: a state the thesis can cite | a version tag (`v0.7.0`, `v0.8.0`, next `v0.9.0`) and a CHANGELOG section | the author (tags are an author decision, N-11) | `v0.9.0`: cut on the merged trunk with a Sepolia witness (`docs/MILESTONE_NEXT.md`) |
| **Work milestone** (WM-n) | a coherent block of passes inside an overall milestone: one plan executed, reviewed and audited | a commit range on the trunk, a report (`WM-n_REPORT.md`) and an audit; a tag `wm-n` only once N-11 is decided | the orchestrator, by the closing pass's gates; the author by accepting the report | WM-1 below |

**What closes a work milestone** (all must hold):
1. every item of the plan it executed has a status (done / changed / deferred / not done, with the reason);
2. a detailed report in this directory, drafted before the audit so the audit checks the report too;
3. an audit by reviewers that do not share the orchestrator's context, with a findings register in
   which every finding has a disposition;
4. the confirmed findings fixed and re-verified, or deferred with an owner;
5. grand run ALL OK and CI green on the closing commit;
6. a reformulated plan for the next work milestone;
7. a consolidated handback that supersedes the period's handback and its addenda.

## Work milestones

| WM | Passes | Commit range | Dates | Theme | Report | Audit |
|---|---|---|---|---|---|---|
| **WM-1** | 8–11 (closed by pass 12) | `db6c381..291bbca` (27 commits); closing pass 12 `3e19e72..8c9fe6b` | 2026-10-09 → 2026-10-10 | close the merge; generated dashboard and registers; crux register; infrastructure messaging (V2I/I2I) designed, pre-registered, built, measured, reviewed and hardened; run-identity and stale-figure tooling | `WM-1_REPORT.md` | `docs/AFTER_ACTION_REPORT_12.md` §4 (88 findings; briefs and reports in `audit_WM-1/`), and the pass-11 review (`review_pass11/`) |
| WM-2 | from pass 12's close | — | — | `docs/PLAN_WM-2.md` | — | — |

Before WM-1 the work was organised by passes and lineages (sandbox, review-2, onboarding), recorded in
`docs/SESSION_MANIFEST_2026-09.md`, `docs/DEVELOPMENT_HISTORY.md` and the handbacks; those periods are not
renumbered retroactively.
