# Opening Message for the Check Session

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-20 (after-action report 23).
Paste the block below as the first message of a new session on branch `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy`.
The session must be new: it reads only the repository and the hand-off, not any earlier conversation. No other
session may push to the branch while it runs.

---

You are starting a fresh session on the branch `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` of this
repository. Your task is an independent check of after-action reports 16 to 22. Do this, in order, and nothing else
until it is done:

1. Read `docs/STYLE_AND_RIGOUR_GUIDE.md`, then `docs/HANDBACK_2026-10-14.md` §7, then `docs/HANDOFF_2026-10-17.md`,
   then `docs/milestones/check_passes_16-22/CHECK_BRIEF.md`. Follow the brief exactly.
2. Open the next free after-action report (`docs/AFTER_ACTION_REPORT_NN.md`, the first number not yet used) with a
   plan for the check, and commit it before any other change. Commits are under my name only:
   `git -c user.name="Nikhil Prakash" -c user.email="nikhil.prakash1995@gmail.com" commit`. No co-author trailer,
   and no assistant or model name in any tracked file.
3. Run every claim K1 to K13 as the brief says. Record agreement in one line each and disagreement as a finding.
   Report; do not fix. If a command cannot be run as written, that is a finding.
4. Look beyond the list, especially at the places the brief's §4 names.
5. Write `docs/milestones/check_passes_16-22/FINDINGS.md` in the brief's §5 format. Commit and push it, read CI,
   and close the report with CI's result.
6. Finish with a message to me that leads with the count of findings by severity and the single most important one.

Rules that apply throughout: run checks unpiped; a delegated agent's report is accepted only after its gate is re-run;
fetch before every push and rebase onto what arrived; stop a Hardhat node by its process ID, never with a pattern
that matches your own command line.
