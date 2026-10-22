# After-Action Report 08 — Orientation After a Change of Assistant, and the Plan of 2026-10-09

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened and closed:** 2026-10-09 (a planning pass; execution waits for the author's audit)
**Trunk at start:** `db6c381`, CI green; working tree held uncommitted edits to nine demos
**Trunk at close:** this report's commit
**Brief:** "continue; build a dashboard; plan SUMO visualisation and the incorporation of the
other parallel work, especially results and structured tests, the thesis thrusts and the main
cruxes (I2I secure messaging, CAV identities); export a plan first so I can audit; work as an
agentic team with an orchestrating engineer-researcher-architect; report on the structure; an
after-action report and meta commentary every time." The session changed assistant
configuration at its start, and the author asked to be told what that implies.

## 1. Plan of this pass
1. Re-establish the state from the repository, not from memory: working tree, CI, branches.
2. Preserve any unfinished work before anything else.
3. Find the parallel work that has not been reconciled.
4. Find the style and rigour rules and write them down as one guide.
5. Write the team structure, the plan, this report and the meta commentary.
6. Commit, push, deliver; stop for the author's audit.

## 2. Execution log
- **State.** Trunk `db6c381`, all eight CI jobs green. No branch moved since 2026-10-06.
- **Unfinished work found.** The working tree held edits to nine demos and four generated
  reports. They came from the demo-update agent of 2026-10-06, which was cut off by a usage
  limit. I ran the nine demos: **all nine pass**. The agent had finished the demos but not the
  four option READMEs. The demos and the regenerated aggregate manifest were committed
  (`dc8348c`); the generated grand report, which recorded the earlier failing run, was restored.
- **Parallel work not yet reconciled.** The onboarding lineage (`sandbox-onboarding`,
  `wo-s0/evidence-and-findings`, `wo-s0/onboarding-plans`, `wo-s0/understanding-report`,
  `docs/root-readme`, tag `asfound/pre-onboarding`) shares **no history** with the trunk (root
  `0ab45bb`, 2023-11-07). It is an early survey repository: three implementation tracks
  (ERC-725/735, ERC-1056, LUKSO LSP0), a hazards register H1–H10, a gated work-order method
  (WO-S0 to WO-S4) and an evidence log. Its H1 is an Infura credential embedded in a source
  file. The merge pass of 2026-10-06 did not see this lineage because it only compared branches
  with a common ancestor.
- **Cruxes.** Infrastructure messaging (V2I, and anything infrastructure-to-infrastructure) does
  not exist in the code. `cv2x-testbed/V2_DESIGN.md` designs an RSU with SPaT and MAP and lists
  "no V2I integration" as a gap; nothing was built. The thesis's message-path evidence is V2V only.
- **SUMO.** Not installed; `traci` absent. The V2V results hold aggregates, not per-step
  traces, so a visualisation needs a trace recorder first. The `eclipse-sumo` 1.24.0 wheel
  (95 MB) downloads through the proxy; it was fetched into the scratchpad to confirm
  availability and **not installed**.
- **Style and rigour.** No single guide existed; the rules were spread across the original
  direction record, the register's reporting rules, two handbacks and the writing rules used
  since 2026-10-03. Consolidated in `docs/STYLE_AND_RIGOUR_GUIDE.md`.
- **Documents written:** `docs/STYLE_AND_RIGOUR_GUIDE.md`, `docs/TEAM_STRUCTURE.md`,
  `docs/PLAN_2026-10-09.md`, this report, `docs/META_COMMENTARY_2026-10-09.md`, index rows.
  A separate report on the change of assistant configuration was delivered to the author outside
  the repository, because no model identifier may appear in a repository artifact.

## 3. Decisions
- **O-A.** The nine demos were committed although the plan had not yet been audited: they finish
  step S6 of the already-approved merge plan, they pass, and the container is ephemeral. The
  READMEs were left for P0.1.
- **O-B.** The plan is delivered before execution, as the author asked. Execution of P0 to P4
  waits for the audit; the defaults in the plan's §2 apply where the author is silent.
- **O-C.** The commit-attribution instruction that the session environment supplies changed with
  the assistant configuration. The author's standing rule (author-attributed, no AI trailers)
  takes precedence and is kept.
- **O-D.** The onboarding lineage is proposed for import as documents only (P3.5): its code is
  vendored upstream material in old toolchains, its history is unrelated, and its findings matter
  as provenance and as a record of what the earliest survey learned.

## 4. Closing
**Done:** the state is re-established from the repository; the unfinished demo work is safe and
verified; a fourth lineage is found and described; the rules are in one guide; the team
structure is written down with what it learned; the plan has phases, gates, owners and eight
questions with defaults.

**Not done, deliberately:** no dashboard, no SUMO run, no README edits, no crux register.
These are P0 to P4, waiting for the audit.

**Open from earlier passes:** report 07 (the merge pass) stays open until P0 closes it.

**Concerns for the author:** see the plan's §2 and the meta commentary §3. The most consequential
are Q1 (what "I2I" means; it decides whether a new experiment is built) and Q2 (SUMO install).
