# Team Structure — How the Work Is Organised as an Agentic Team

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-09
**Purpose:** the author asked that the work be done by a team of specialists from each field
the thesis touches, orchestrated by one engineer-researcher-architect, and that the structure
itself be reported for audit. This file is that report. It states the roles, what each owns,
how work moves between them, how results are accepted, and what the structure learned in the
sessions of 2026-10-03 to 2026-10-06.

## 1. The shape

One orchestrator plans, owns the trunk, writes the after-action report and accepts or rejects
every delegated result. Specialists work in bounded tasks with named files they may change,
and return a report. The orchestrator re-runs each gate before anything is committed.

```
                      Orchestrator
     (engineer, researcher, inventor, architect: owns plan, trunk, acceptance)
                            |
   +-----------+-----------+-----------+-----------+-----------+
   |           |           |           |           |           |
 Contracts   SSI/W3C     V2X and     Security    Measurement  Thesis
 engineer    standards   simulation  and crypto  and stats    methodology
   |           |           |           |           |           |
   +----- Reproducibility/CI ----- Visualisation ----- Industry standards (MOBI) ---+
                            |
                  Adversarial reviewer
       (independent; reviews the orchestrator's own work)
```

## 2. Roles

| Role | Field | Owns | Typical task | Gate the orchestrator re-runs |
|---|---|---|---|---|
| **Orchestrator** | software engineering, research design, systems architecture, invention | the plan, the trunk, merge decisions, the after-action report, the handback | decompose, decide, integrate, accept | everything below |
| Contracts engineer | Solidity, EVM, ERC/LSP standards | `1_blockchain-identity/contracts`, Hardhat tests | fix a defect with a regression test | `npx hardhat test` 0 failing; MOBI copies byte-identical |
| SSI/W3C standards specialist | DID Core, DID Resolution, VC Data Model, CAIP-10 | `2_w3c-ssi-layer`, `docs/conformance` | resolver fix, external suite run | checker score; external suite totals |
| V2X and traffic-simulation specialist | SAE J2945/1, IEEE 1609.2, ETSI ITS, SUMO/TraCI, Veins | `cv2x-testbed/sumo`, `cv2x-testbed/identity` | message-path experiments, mobility, RSU models | harness run with seed; results file with environment header |
| Security and cryptography specialist | threat modelling, ECDSA/secp256k1, replay, revocation | security harness, threat matrix | attack scenario, strict-revert cell | strict harness 0 unexpected reverts |
| Measurement and statistics methodologist | experimental design, pre-registration, CIs, effect sizes | register rows, experiment scripts | pre-register, run, write the row | clean tree, condition tag, register status V |
| Thesis methodology specialist | MASc examiner lens, claims discipline | chapters, `COMPOSITION.md`, scope log | narrow a claim, write a section | every number has a V row |
| Reproducibility and CI engineer | GitHub Actions, toolchain pinning, artifact freshness | `.github/workflows`, lockfiles | add a gate, fix drift | all workflows green |
| Visualisation engineer | data visualisation, dashboards | `docs/figures`, dashboard artifact | figure or dashboard from committed data | a check that every displayed number matches its source |
| Industry-standards analyst | MOBI VID I/II, automotive identity practice | `docs/MOBI_VID_CHECKLIST.md`, scope log | clause-level check | every clause cited to the public text |
| Adversarial reviewer | all of the above, independently | nothing; read-only | review a pass after it closes | findings logged; none silently dropped |

The orchestrator also does specialist work directly when the task is small or when the
decision and the change cannot be separated.

## 3. How work moves

1. **Plan.** The orchestrator writes the plan with steps, gates and owners, and delivers it to
   the author when the author asked to audit first.
2. **Delegate.** A specialist gets one bounded task: the goal, the exact files it may edit, the
   files it must not touch, the gate command, and the report format. Tasks that touch the same
   files are never run in parallel.
3. **Report.** The specialist returns what changed, the gate output and anything it could not do.
4. **Accept.** The orchestrator re-runs the gate itself. Only then is the work committed, by
   explicit path, with the author as committer.
5. **Record.** The after-action report logs the step, the gate result and any decision. A
   decision that is the author's is written with its default and goes into the handback.

## 4. What the structure learned (2026-10-03 to 2026-10-06)

| Lesson | Evidence | Rule it produced |
|---|---|---|
| An agent's report can be right about its own scope and wrong about the whole | the demo agent reported 18/18 green; the grand run later found demos the merge had broken elsewhere | re-run the full grand runner after any accepted change, not only the agent's files |
| An agent can stop mid-task | the merge-demo agent was cut off by a usage limit after editing nine demos and before the READMEs | small tasks; commit at each accepted boundary; record partial state in the after-action report |
| Read-only analyses scale well in parallel | three reconciliation analyses ran at once and produced 740 lines of cross-checked findings | fan out reading; serialise writing |
| A leftover process can poison a later gate | a node from an analysis worktree answered on port 8548 and failed the Python fixtures | stop every started process by recorded pid; check ports before a gate |
| Two sessions can fix the same defect identically without knowing it | D10 and K-15 produced byte-identical code | fetch all branches at the start of every pass |
| Local and CI toolchains can differ silently | OpenZeppelin 5.4.0 in the testbed install vs 5.0.2 in CI changed one artifact | reproduce CI's exact install before regenerating tracked artifacts |

## 5. Limits of the structure, stated plainly
- The specialists are instances of the same assistant with different instructions. Their
  independence is procedural, not epistemic. The adversarial reviewer is most useful when run
  by a different assistant configuration or by the author.
- Domain grounding (SAE, IEEE, ETSI, MOBI texts) is only as good as the sources the session can
  reach. Member-only texts stay unverified and are labelled so.
- The orchestrator's acceptance gate catches regressions, not wrong research questions. That
  check is the author's.
