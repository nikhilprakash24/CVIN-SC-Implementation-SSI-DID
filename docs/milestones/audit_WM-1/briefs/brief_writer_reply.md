> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`. Dispositions: after-action report 12 §4.

The five briefs and the index are written to `$SCRATCH/audit_briefs/`: `brief_1.md` … `brief_5.md` and `README.md`. I did not run any of the checks; the briefs only direct the auditors. Each brief is self-contained, has 19–22 numbered checks, lists the allowed commands, and requires the F-numbered findings format. I kept your suggested split.

**Briefs**
1. **Claims, numbers and thesis chapters vs the register and committed data.**
   - It has the auditor recompute I1–I5 (rows #44–#48) from the per-run JSON and check that the pre-registered bands were not edited after the lock.
   - It also covers the register status counts, crux register and dashboard, and chapters 1/4/5/6/7. Chapters 1, 4, 6 and 7 have never been reviewed. The brief also checks stale figures in non-Markdown files and the report's own arithmetic.
2. **Code and security of what WM-1 built.**
   - It has the auditor write proof-of-concept attacks against the infrastructure verifier. Examples are the conditional field binding, issuer-key binding, replay-cache poisoning and clock handling.
   - It asks for an independent mutation set, since the "26 mutants" are not committed. It also re-runs the "flags off changes nothing" gate and checks timed-region changes under #27, the scope of `code_clean`, secrets in the tree, and trace and figure content.
3. **Tooling, CI and reproducibility from a clean checkout.**
   - It tests whether each guard (generators, `--check` modes, stale-figure checker, probe, grand runner) fails on a mutated input. The report admits several were never tested this way.
   - It also covers byte-identical figures, the stamp inventory, CI history per commit via `gh`, clean installs, determinism claims, and which commit each generated number belongs to.
4. **Process and documents.**
   - It checks that everything the report and plans name exists, and applies the milestone's seven closing conditions literally. It recounts the plan status table and checks the timeline against git.
   - It checks the pass-11 findings-register dispositions and whether the defect log and "what went wrong" section are complete.
   - It also covers decisions credited to the author versus defaults, and independence and AI-disclosure facts.
5. **The unaudited code: Python suites outside L3, the contracts, and the tests that certify them.**
   - It covers test power: mutants, regression tests that must fail on the old code, strict vs lenient revert assertions, and the self-referential W3C checker (94.3 %).
   - It checks what the 335/336 external suite actually tests, then contract access control, deployability (EIP-170 contract size), gas definitions, baseline fairness, VIN cipher misuse, open-defect exploitability, and the demos.

**Leads I noticed while writing the briefs** (listed in the README as leads for the auditors to verify, not findings)
- The report and plan cite `HANDBACK_2026-10-10.md`, which does not exist.
- The plan carries P3.2 to "B4", but `PLAN_WM-2` has it as A5.
- The grand report was generated at `601e1de` but is cited as `291bbca`.
- "26 of 26 mutants killed" has no committed mutant set.
- `_binding_ok` skips the station check when a message has no `rsu` key.
- Warm-path expiry uses `time.time()` instead of the injected clock.
- The plan status counts (25 items, 18 done) do not obviously match the table.
- Report §14 and after-action report 12 §3–§6 are empty.
- The promised presentation documents do not exist.

**Deliberately left out**
- Re-running any long experiment: a measurement that is wrong but internally consistent in the JSON would not be found.
- Chapter 2 correctness and citations, and the text of the SAE/IEEE/ETSI standards.
- `docs/prior-survey/` apart from secrets, plus vendored code, `docs/review02/` and after-action reports 01–07 beyond what WM-1 cites.
- Real SUMO behaviour, Sepolia results, and radio realism.
- The presentation report (not yet written) and the hosted artifact versions v3–v5.
- Formal verification and gas-optimality of the contracts, document style, and the merits of the research questions.
