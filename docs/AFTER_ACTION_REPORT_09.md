# After-Action Report 09 — Executing the Plan of 2026-10-09 under its Defaults

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-09, before any change; updated per step; closed at the end
**Trunk at start:** `0f1dbc5`, clean
**Brief:** "go with the defaults and continue" — the author approved `docs/PLAN_2026-10-09.md`
with every default in its §2.

## 0. The defaults, as they bind this pass
| Q | Default taken | Consequence for this pass |
|---|---|---|
| Q1 | infrastructure messaging = V2I and infrastructure-to-infrastructure; start with signed SPaT from a DID-identified RSU | P4.3 delivers the design note; code waits for its audit (plan §1 P4.3 gate) |
| Q2 | no SUMO install | P2a (design and trace schema) only; P2b not started |
| Q3 | update the existing dashboard link | P1.4 republishes to the 2026-09-24 URL |
| Q4 | onboarding lineage: documents only | P3.5 imports documents under `docs/prior-survey/` |
| Q5 | merge decisions M-A…M-L stand | no contract change |
| Q6 | no branch change | — |
| Q7 | adversarial review reserved for a later session under a different assistant configuration | recorded in the handback |
| Q8 | the second remote is treated as superseded | recorded |

## 1. Plan (the order of plan §3)
P0.1–P0.6 → P1.1–P1.2 → P4.1–P4.2 → P1.3–P1.4 → P3.1–P3.6 → P2a → P4.3 (design) → close.

## 2. Execution log
- 2026-10-09 — report opened (`7a9a996`).
- **P0.3 started first, in isolation.** The metrics harness takes 14 minutes and records whether the
  tree was clean, so it ran in a separate worktree at `7a9a996` (`node_modules` symlinked and
  excluded locally). Run `2026-10-09T02-09-36Z_7a9a996`, `dirty: false`; frontier and dominance
  unchanged (CVIN-Combined dominated only by ERC-4337). Register #34–#36 annotated (`f976e57`).
- **P0.1 (delegated, accepted by the grand run).** Four option READMEs brought to the merged
  contracts; coverage 20/20, 50/50, 21/21, 57/57; 41 demos ok (`aef16af`). The agent reported
  that K-11 has no demo step and that three functions are covered only inside combined step labels;
  both are stated in the READMEs.
- **P1.1–P1.2, P4.1 (orchestrator).** `docs/figures/make_dashboard_data.py` builds the snapshot only
  from committed files and the register; `docs/thesis/cruxes.yaml` → `CRUX_REGISTER.md` (eight cruxes:
  C3 infrastructure messaging is a **gap**, the other seven **partial**); `--check` in CI (`ca3a44d`).
  Generating the snapshot exposed register faults the eye had missed: row #26 still opened with
  "**B**", rows #40/#41 said "superseded" in the claim and "V" in the status, row #6's status was
  unparseable, rows #25/#26 quoted superseded figures in their own claim text. All corrected.
- **P2a and P4.3 (orchestrator).** `docs/PLAN_SUMO_VISUALISATION.md` (trace schema, renderers,
  steps V1–V5) and `docs/design/INFRASTRUCTURE_MESSAGING.md` (RSU and controller identities as DIDs,
  signed SPaT/MAP, I2I back-haul, pre-registered I1–I5, grounding in SAE J2735, IEEE 1609.2, ETSI
  TS 103 097/102 941, CAMP SCMS, NTCIP 1202/1211). Both stop at design, per the defaults (`3a2a806`).
- **P3.5 (delegated, accepted by reading).** Onboarding lineage imported under `docs/prior-survey/`
  as provenance: seven documents verbatim below a source header, a reconciliation note mapping its
  three tracks and hazards H1–H10 to the trunk. H1 (an Infura credential) is absent from the trunk
  but public on the lineage's branches: rotation recommended. H9 (a `git+ssh://` lockfile entry) is
  on the trunk; CI installs succeed with it (`3a2a806`). I checked the import for credentials myself.
- **P3.1 (orchestrator).** `docs/testing/build_register.py`: 305 TC entries derived from the L1
  records, the strict security harness and the demos, without renaming a single test; option ×
  family coverage matrix (T 91, N 78, G 13; every G is on the two Python baselines, which have no
  demos by design); CI-checked (`aef16af`).
- **P3.3 (orchestrator).** Stamp inventory: 11 of 25 results of record carried a complete stamp. A
  shared helper now stamps the four JS producers. First re-run exposed a fault in my own helper:
  each producer's output dirtied the tree for the next. The flag now covers the producing code paths
  only, as the harness's `dirtyMeasured` does; the guide states it. Re-run: all four `dirty: false`
  at `d0cc19c`, no gas or sweep cell moved; 16 of 25 stamped (`d54178e`).
- **P3.4 (checker by the orchestrator, fixes delegated).** `stale_numbers.yaml` + `check_docs_numbers.py`
  found 82 superseded figures in 12 citing documents; all fixed (test totals now cite the grand report);
  five sentences now name ERC-735 as the heaviest create; the 94.3 % residual now includes its PARTIAL;
  checker in CI (`5a83bc2`, `8885a7f`).
- **P0.2.** Grand run on the merged trunk ALL OK: Hardhat 536, Python layers 260, 92 demos / 1,752
  steps (`8885a7f`).
- **P1.3–P1.4.** Dashboard page rendered from the snapshot by template; one headless look at desktop
  (light) and phone (dark): no overflow, no script error; published to the 2026-09-24 link as
  version 3: https://claude.ai/artifact/1C5X9GpPcEwyCRDMYxYhpa.
- **P0.5–P0.6.** `docs/HANDBACK_2026-10-09.md` supersedes both handbacks (the plan called it
  `…_2026-10-06.md`; it is dated the day it was written); report 07 closed.
- **P3.6 (delegated, accepted by reading its citations).** The TSR second-pass sheet pre-filled to
  version 1.1: of 30 D-decisions, 6 decided on the trunk, 4 partly, 20 left to the author; 9 of 15
  verifications checked; of 20 inventory findings, 15 still hold, 4 partly resolved, 1 resolved.
  The agent found six defects in this pass's own outputs, five fixed at once: the coverage matrix used
  X for "failing" (TSR reserves X for out of scope; now F); the register classed security cells S (TSR:
  S is scale, A adversarial; now A); `docs/INDEX.md` said "#1–#31"; the CI header said "47 tests pass";
  the scope log said both SC-15…SC-20 and SC-15…SC-21; a tool-attribution line in `TEST_ONBOARDING.md`
  (from the review-2 lineage) broke the no-AI-attribution rule and was removed. Left for the author:
  D-02 (the register keys tests by records, not by titles, and does not yet include the Python suites);
  `3_cv2x-testbed/README.md` still carries July counts outside the checker's scope.

## 3. Decisions
- **E-A.** Long measurements run in a separate worktree, so the parallel editing of documents cannot
  dirty them.
- **E-B.** The test register derives TC identifiers from existing records instead of editing test titles:
  other tools parse those titles, and the TSR plan's own principle is "tag, do not relocate".
- **E-C.** The run stamp's `dirty` covers producing code only (contracts, scripts, configuration,
  lockfile); `dirtyAnyFile` is kept beside it for transparency.
- **E-D.** The stale-figure fixes replace a superseded figure only where the sentence states it as
  current; test totals cite the generated report instead of a new hand-typed number.
- **E-E.** Register claim cells that quoted superseded figures were brought to current values with a
  dated note, because the crux register quotes them verbatim.

## 4. Closing

**Done.** Every phase the defaults allowed: the merge pass closed (P0), the results dashboard
generated, CI-checked and republished (P1), the SUMO visualisation designed (P2a), the parallel work
on structured tests and results incorporated (P3.1, P3.3, P3.4, P3.5, P3.6), the crux register
built and the infrastructure-messaging design written (P4.1–P4.3). No contract changed, no result
of record moved, and the hypotheses' verdicts are unchanged.

**Not done, by the defaults.** P2b (SUMO install and runs) waits for S-b; the trace recorder waits
for S-a; the infrastructure experiment waits for I-a. TSR phases 4–8 (charters, statistical rules,
promote/superseded, the remaining 9 unstamped producers, the presentation plan) are the next pass.

**What the generators found that reading had not.** Building outputs from sources forced every
number through the register once more: five register rows were inconsistent with themselves, 82
superseded figures sat in the citing documents, and two figures in the crux register were stale
because the register's own claim cells were. None of this changed a result; all of it would have
reached a chapter.

### 4.1 How the team structure performed (the author asked for this assessment)
| Role in this pass | Work | Outcome | Acceptance gate the orchestrator re-ran |
|---|---|---|---|
| Orchestrator | plan order, worktree isolation, generators, register fixes, stamping, design notes, dashboard, reports | all steps closed | grand run, CI-equivalent checks, headless render |
| Contracts engineer (agent) | four option READMEs | accepted | grand run, 92/92 demos |
| Industry/provenance analyst (agent) | onboarding-lineage import | accepted | credential scan, byte comparison claimed by the agent and spot-checked |
| Thesis methodologist (agent) | 82 stale figures in 12 documents | accepted with two items returned to the author (X-1, X-2) | stale-figure checker exit 0; diff sample read |
| Measurement methodologist (agent) | TSR second-pass sheet pre-fill | accepted; it found six defects in the orchestrator's own outputs, five fixed | sheet citations read |
| Adversarial reviewer | — | reserved (Q7) | — |

What worked: work split by file ownership, never two agents on one file; agents given a gate command
and a report format; every acceptance re-run by the orchestrator. What did not: the orchestrator's own
first stamping helper was wrong and was caught only because the gate (the stamped `dirty` flag) was read
rather than assumed. The structure's independence remains procedural: the same assistant configuration
played every role, which is why the adversarial review waits for a different one.
