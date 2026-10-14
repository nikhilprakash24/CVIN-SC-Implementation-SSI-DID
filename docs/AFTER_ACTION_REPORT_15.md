# After-Action Report 15 — WM-2 Step A4 (Promote Step), Phase 2 Opened, Handoff to the Next Model

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-14, after report 14 closed at `2756c2c` (CI 8/8 green on `1f3cd8f`); closed at the end of this pass
**Brief:** the author's "accept defaults and continue to the next executable — then we will switch back to
[the next assistant model] so write a handoff on that … in addition to the other docs … start the PHASE 2 Ideation, Architect,
Planning and Brainstorming where you will begin to construct (across multiple chats) … phased … deeply
integrated and useful work".

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| A4 | WM-2 step A4: a promote step. A producer writes to an untracked `runs/<producer>/<run-id>/` with a manifest (stamp, outputs, hashes); `tools/run_identity/promote.py` copies to the tracked result path only if the stamp is clean, the commit is HEAD, the producer's scope is unchanged and still clean, and every output matches its hash and a declared result path. Piloted on the security matrix (`securityScenarios.test.js`), which today rewrites a tracked file on every `npx hardhat test` (D56) | a dirty run refuses to promote (test), and so do the other refusal cases; `npx hardhat test` leaves the tracked tree unchanged |
| P2 | Phase 2 opened: a phase charter and a first set of ideation, architecture, planning and brainstorming documents under `docs/phase2/`, built across sessions, each tied to the Phase 1 evidence (register rows, cruxes, defects, deferred items) it extends | every Phase 2 idea cites the Phase 1 artefact it starts from; a session protocol says how the next session picks up |
| H | Handoff for the switch to the next model: what is verified, the rules, the traps, the next steps, the Phase 2 entry point | the handoff names a starting command and a first task |
| R | Records: plan, deferred list, handback, session manifest, this report; grand run last; CI | CI green on the closing commit |

## 2. Execution log
- 2026-10-14 — report opened.
- **A4, the A2 gap found first.** The security matrix is written by the `after()` hook of
  `securityScenarios.test.js`, which calls the harness's `writeMatrix`. A2 had registered
  `attackHarness.js` as the producer. That scope left out the scenario file itself, the code that decides
  every cell: a D49-class gap in D49's own fix. Corrected in `producers.json`. The scope is now 8 paths:
  the scenario file, the harness, the stamp helper, both contract directories, the Hardhat config, `package.json` and the lockfile.
- **A4 runs and promote.** `tools/run_identity/promote.py` adds `new_run` and `write_manifest` (Python);
  `run_stamp.js` adds `newRun` and `writeManifest` (JS, same format) and `commitFull`. A run lives in the
  untracked `runs/<name>/<run-id>/` (`/runs/` in `.gitignore`) with `manifest.json`: the producer, the stamp
  taken when the run started, and each output with its sha256 and destination. Promotion needs all of:
  - a registered producer;
  - `code_dirty` false;
  - the stamp's commit is HEAD;
  - the same `scope_sha`, still clean now;
  - every output's bytes match;
  - every destination under one of the producer's declared result paths.

  `--dry-run` shows what would change.
- **A4 pilot.** `securityScenarios.test.js` stamps itself when it loads, before any scenario runs.
  `writeMatrix` writes to `runs/security-matrix/` with a manifest; the date-preserving trick that kept the
  tracked file byte-stable is gone, because the tracked file is no longer written. `npm run security:promote`
  runs promote.
  - Uncommitted tree: 60 tests passing, the tracked tree unchanged, and promote refused the run for both
    reasons (stamp dirty; code dirty now).
  - Committed tree (`1012ebd`): a clean run's dry-run says it would promote. All 54 outcome cells match the
    committed matrix; only the metadata differs (date and stamp).
  - **Not promoted:** the matrix's run of record is A3's, after C2 changes `attestEvent`.
- **A4 gate.** `tools/run_identity/test_promote.py`: 13 tests, one per refusal plus a copy and a no-copy case,
  in CI. The probe still passes (158 checks) with the corrected producer.
- **A4 disclosure.** `attackHarness.js` changed (`writeMatrix`), and it is in the scope of
  `security_scenarios.js` (which uses only `revertDataOf`). So `onchain_security.json` will read "code changed
  since: yes" from `1012ebd` on: true by the column's definition, safe in direction, and resolved by its C2
  re-run. Not hidden by a stamp-only entry, because the change is not a stamp line.
- **P2, Phase 2 opened (P2.0).** `docs/phase2/` holds the charter, evidence base, register, architecture,
  roadmap, brainstorm, decisions and session log:
  - **Charter.** Name space, four Phase 2 principles (anchored, killable, author-decided, no number before its
    plan), sub-phases P2.0–P2.5 with gates G0–G4, and a session protocol for work across chats.
  - **Evidence base.** Assets, 18 seeds S-01…S-18 with sources, chapter 7 §7.6 mapped, cruxes mapped.
  - **Idea register as data.** `ideas.yaml` holds 23 ideas in 7 tracks, each with question, why, anchors,
    files it builds on, first step, kill criterion, dependencies and scores, plus 5 candidate programmes.
    `build_phase2.py` generates `IDEA_REGISTER.md` (ranking computed, never typed) and `--check` in CI fails on
    a missing anchor, a missing file, a dependency cycle or a stale register. Shown to fail on each of the four.
  - **Architecture sketch.** Seven planes mapped to Phase 1 code; six interfaces, each with its Phase 1
    reference implementation; three structural options with a proposed default (B, a plug-in layer); five
    open questions.
  - **Roadmap.** A session plan for sessions 2–8, dependencies on WM-2 steps and author decisions, and a risk table.
  - **Brainstorm 1.** 25 divergent items, 5 parked with what each lacks, 3 gaps in the register (C8 has no idea
    that moves it), 5 questions for the author.
  - **Decisions.** P2-D0 decided by the author; P2-D1…D6 open with labelled defaults; ADR-0001…0003.
  - The stale-figure checker now scans the eight new Markdown files (98 files; 0 stale).
  - Top five by computed total: I-05 (freshness theory), I-16 (W3C external validity on chain-backed
    documents), I-01 (real mobility), I-03 (public chain and rollups), I-13 (model checking the revocation
    protocol). These are orchestrator estimates; the author chooses (P2-D1).
- **H, handback.** `docs/HANDBACK_2026-10-14.md` supersedes the 2026-10-10 handback. Its §7 is written for a
  session on a different assistant model: what to read in which order, and the standing practice that is not
  visible in the code. No model name appears in any tracked file (rule 1.3.1). `docs/INDEX.md` points to it
  and to Phase 2.
- **Grand run (last).** ALL OK: smoke 11 adapters, L1 99, Hardhat 537, Python layers 305, 92 demos / 1,752 steps
  (594 mined transactions), the same counts as at WM-1's close. The run executes the security suite, and the
  tracked `attack_results.json` was **not** rewritten: before A4, every Hardhat run rewrote it. The L1
  CVIN-Combined `claim` cell moved again (316,439 → 316,451), within the random-input spread the WM-1 audit
  recorded (U-F11; B1, N-18). The snapshot, page, test register and presentation were regenerated from the run.

## 3. Closing
**A4 done.** Runs live in an untracked `runs/` with a manifest. A run reaches its tracked result path only
through `promote.py`, which refuses on six conditions; each refusal has a test in CI. The pilot producer, the
security matrix, no longer rewrites a tracked file. A clean run of it matches the committed matrix in all 54
cells. The pass also found and fixed a gap in A2's own table (the wrong producer file for the matrix).

**Phase 2 is open at P2.0:** ten files under `docs/phase2/`, with the idea register checked against Phase 1's
registers in CI.

**The handback for the next session**, which runs on a different assistant model, is
`docs/HANDBACK_2026-10-14.md`.

No register row changed. Disclosed: `onchain_security.json` now reads "code changed since: yes", because the
harness file in its scope changed; its C2 re-run resolves it.

**Next.**
- Phase 1: WM-2 C0, verifier v3 with the D51 fix (dated pre-registration amendment first).
- Phase 2: session 2 per `docs/phase2/sessions/SESSION_LOG.md`.

