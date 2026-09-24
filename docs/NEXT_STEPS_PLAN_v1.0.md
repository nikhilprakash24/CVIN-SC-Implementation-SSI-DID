# CVIN-ID/TEST — Next-Steps Plan (Lead-Architect Synthesis)

**CVIN-SC Research Programme · CLI-agent plan for operator/architect review · v1.0 · 2026-06-20**
**Status: PROVISIONAL — awaiting operator comparison against their own plan; nothing herein has been executed.**

*Synthesis of a four-lens senior review (PI/evidentiary-integrity, build/release-engineering, security/threat-model, plan-critic) run against the on-disk state: the architect's directions, `FINDINGS.md`, `UNDERSTANDING_TEST_REPO.md`, and the WO-S0 progress report. Where the lenses conflicted, the resolution and its reasoning are stated — nothing is silently averaged.*

---

## 0. Executive summary — my read as lead

WO-S0 is done and clean, but the pass is **not ready to "just run WO-S1."** The review found that the architect's plan, executed verbatim, fails **before** the known H3 blocker is even reached, and that three structural protections are missing:

1. **The evidence base has no anchor.** Nothing is committed; the "immutable" WO-S0 evidence is one accidental edit away from silent loss. Freeze first.
2. **The network window is a strategic asset we're about to waste.** The evaluation target is *offline*; everything the offline phases need (three solc binaries, the upstream ERC725 restore source, warm npm caches proven by offline replay) must be vendored **now, while we're online** — or WO-S1/WO-S2 dead-end later.
3. **Two unlogged install blockers exist ahead of H3:** Build-III's lockfile resolves `ethereumjs-abi` via **`git+ssh://`** (hard-fails without GitHub SSH auth → new hazard **H9**), and Build-II's lockfile pins `websocket` to a personal fork over **`git://`** — a protocol GitHub retired in 2022, making Build-II's native install **unrecoverable as-pinned** (downgrade it to source-only triage → new hazard **H10**).

The plan below sequences six phases (P0–P5) by dependency and reversibility, resolves a genuine conflict inside the architect's own directions (restore-vs-don't-fix), and ends each phase at an operator gate. Estimated critical path to a resolved [TS-1]: **P0 → P1 → P2 → P3**, with P1 the only phase that needs the network.

---

## 1. The strategic frame (unchanged, restated)

- `CVIN-ID/TEST` is **raw material** — a survey of three identity standards, not a built system. The output of this pass is a **verified compatibility baseline + consolidation recommendation**, not features.
- Standing rules bind everything: no interface alteration; real measurements only; deviations logged, not smoothed; secrets by location only; offline local EVM only; ask before irreversibility; unresolved tokens are acceptable outputs.
- Roles: **operator** (you) holds gate authority and the key rotation; **architect** ratifies design tokens; **CLI agent** (me) executes and evidences.

---

## 2. Phase plan

### P0 — Freeze the baseline & clear the decision gate *(S effort, fully reversible, no network)*

| # | Step | Acceptance |
|---|---|---|
| P0.1 | **Pre-commit secret sweep** of all staged artifacts: scan for 32-hex (Infura-shape) and 64-hex patterns, lockfile-hash contexts allowlisted | Sweep log in `evidence/`, zero un-redacted matches |
| P0.2 | **Commit WO-S0 artifacts** on `sandbox-onboarding` (FINDINGS, Understanding Report, evidence/) — one commit per work order from here on | Commit exists; SHA recorded |
| P0.3 | **Tag the as-found baseline** (`asfound/WO-S0`, annotated) and seed `evidence/EVIDENCE_MANIFEST.txt` with SHA-256 of every evidence file (append-only) | Tag SHA + file hashes in FINDINGS §E |
| P0.4 | **Adopt the evidence convention** (fixes an internal contradiction in the directions): timestamped filenames `WO-Sx_<step>_<utc-ts>.log`; every log opens with a header block (UTC, exact command, cwd, `node -v`, `npm -v`, git HEAD SHA, solc longVersion) and closes with the exit code; capture native output via `cmd /c "... > log 2>&1"` (PowerShell 5.1 stderr-wrapping workaround) | Convention written into FINDINGS §E |
| P0.5 | **Log new hazards H9/H10** (git+ssh dep; dead git:// protocol) and the **directory contract**: `TEST/` = as-found, frozen behind the tag; all ported/scratch work lives outside it | FINDINGS updated |

**Design decision (PI vs build lens conflict, resolved):** the PI lens wanted a physically separate `reconstructed/` tree; the build lens wanted restoration as a commit inside `TEST/`. **I choose git-based separation**: the as-found state is frozen by the *tag*, the Build-III restore (P3.2) is its *own clearly-labeled commit*, and every log header records the git SHA it ran against — so any compile log is unambiguous about which bytes it exercised. Only the WO-S2 port/scratch project is physically external (`compat-0824\`), because ported sources must never enter the surveyed repo at all. Rationale: one tree + tags is auditable with standard git tooling; two parallel trees invite the very H4-style duplicate drift we're guarding against.

### P1 — Online provisioning window *(S–M effort, reversible, the ONLY network phase)*

Everything the offline phases will ever need, fetched and **proven** now:

| # | Step | Acceptance |
|---|---|---|
| P1.1 | **Vendor solc** — 0.8.24 (pinned target) **plus 0.8.17 and 0.8.19** (native toolchains; the directions forgot these) into `toolchain\solc\`: native win exe + wasm soljson each, checksums read from `binaries.soliditylang.org` list.json (never from memory) and verified locally | Vendor evidence file: filename, list.json sha256, local SHA-256, MATCH per file |
| P1.2 | **Vendor the Build-III restore source**: clone `ERC725Alliance/ERC725`, checkout `v6.0.0` (search nearby develop commits if the tag doesn't byte-match), into `toolchain\upstream\`. **The npm tarball is insufficient** — `package.json#files` excludes `contracts/helpers/`. Byte-diff the 13 checked-in contracts against candidate commits to identify the exact provenance SHA | Diff evidence identifying one commit where all 13 files match (or closest + deltas as a finding) |
| P1.3 | **Defuse H9/H10 without touching lockfiles**: `git config` `insteadOf` rewrites (`ssh://git@github.com/` → `https://github.com/`; `git://` → `https://`), logged as environment deviations | Rewrites active + logged |
| P1.4 | **Warm npm caches + prove offline replay**: for Build-III (Node 16) and V7 (Node 18) only — `npm ci` online once with a sandbox-local `npm_config_cache`, wipe `node_modules`, re-run **`npm ci --offline`**; only exit-0 on the offline replay proves the cache is complete (git deps land in cacache only after first pack). Zip green `node_modules` snapshots as belt-and-braces | Online + offline logs both exit 0, per project |
| P1.5 | Hardened install posture for both installs: per-project `.npmrc` with `ignore-scripts=true` (all 19 install-script packages across the two lockfiles are prebuilt natives that load without their scripts; the host lacks build tools anyway), `HARDHAT_DISABLE_TELEMETRY_PROMPT=true` | .npmrc present; zero lifecycle scripts executed |

**Install scope is 2 of 5, deliberately** (security lens): Build-III `implementations/` and V7 `cvin-v7/` only. `cvin-v6`, `react-dapp`, and Build-II stay **uninstalled** — an uninstalled `cvin-v6` *physically cannot* make the forbidden Goerli call, converting the no-run rule from discipline into state.

### P2 — Egress lockdown *(S effort, reversible, one UAC elevation)*

- Program-scoped **Windows Firewall outbound Block rules** on the two portable `node.exe` paths (npm/npx/hardhat all execute through them), dropped-packet logging on. Docker is absent; this is the surgical default-deny this host offers.
- Verify: HTTPS probe from each portable node fails; probe + `pfirewall.log` extract captured as evidence. Future "supervised install windows" = operator disables rules, install runs, rules re-enabled, window timestamps logged.
- Record the **no-Docker isolation posture** (baseline controls, Windows Sandbox as named escalation, accepted residual) in FINDINGS for architect sign-off at WO-S4.

### P3 — WO-S1: native bring-up *(M effort, evidence-first, offline-verified)*

| # | Step | Acceptance |
|---|---|---|
| P3.1 | **Build-III as-found run** (Node 16): `npm ci` (from cache), `npm run build` — **expected ❌ on H3 missing imports**. This failing log is *evidence that the restore was necessary*, not a defect of the pass | Failing compile log with header block, quoted error |
| P3.2 | **Gated restore** (needs D2 below): copy *only* `contracts/custom/`, `interfaces/`, `helpers/` from the P1.2-identified upstream commit into Build-III; **single commit** whose message embeds the upstream repo/tag/SHA; diff proving the 13 pre-existing files untouched | Restoration commit + diff evidence; H3 → mitigated-with-provenance |
| P3.3 | **Build-III restored run**: `npm run build`, then `npm test` — capture real X/Y pass/fail counts verbatim. If tests fail at Node 16: **stop-and-report**, no patching upstream | **[TS-1] graduates only from this log** |
| P3.4 | **V7 scaffold check** (Node 18): add `@nomicfoundation/hardhat-toolbox@^2` (the ethers-v5-compatible major) as an **exact-pinned, logged deviation commit** (D4); `npx hardhat compile` + `test` on the stock Lock scaffold; **no contracts added** (H5); ethers v5/v6 clash stays a finding for [TS-6] | V7 compile/test logs; deviation logged with lockfile before/after hashes |
| P3.5 | All runs executed **with firewall rules ON** (solc 0.8.17/0.8.19 pre-seeded in P1's window) — "offline" becomes a verified property, not an assertion | `pfirewall.log` shows zero allowed egress during runs |

### P4 — WO-S2: compatibility triage @ solc 0.8.24 offline *(L effort, disposable scratch)*

- Scratch Hardhat project at **`CVIN-2026-Sanbox1_v6\compat-0824\`** (outside TEST/), Node 18, minimal deps, lockfile committed, cache-warmed.
- Compiler wired via a **`TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD` subtask override** pointing at the vendored 0.8.24 binary — explicit and committable, *not* a pre-seeded user-profile cache (invisible state that silently falls back to downloading). Smoke-test with an empty Hardhat compiler cache + firewall on to **prove** zero download.
- Triage per candidate → exactly one of *compiles unmodified / compiles after declared mechanical port / blocked*:
  - **Build-III X/Y** (pragmas ^0.8.x — expect unmodified; record verbatim) → **[TS-2]**
  - **Build-0 `CVIN_ERC725.sol`** and **Build-II Origin contracts** → mechanical 0.4→0.8 port from a **fixed checklist only** (SPDX; pragma; explicit visibility; `constant`→`view/pure`; `constructor` keyword; `emit`; `memory/calldata` locations; `keccak256(abi.encodePacked(…))`; `throw`→`revert()`; `now`→`block.timestamp`; `payable` conversions; `.call{value:}()` tuple handling; `abstract/virtual/override`), each change recorded per-file in `PORT_NOTES.md` → **[TS-3]**
  - Anything beyond the checklist = **blocked → WO-1 finding**, never forced.
- **No-interface-alteration made machine-checkable** (my favorite output of the review): extract function-selector and event-topic sets from the compiled ports and diff against the 0.4 originals — **selector/topic equality is the pass condition** for Standing Rule 1.
- SafeMath vs 0.8 checked-math semantic delta (revert string vs Panic 0x11) is **logged as a finding**, not smoothed.
- Fill FINDINGS §D; publish **baseline-invalidation conditions** (compiler-hash change, any solc network fetch, upstream-SHA drift, OZ/Node pin change, any logic-altering edit) so "is the baseline still valid?" is answerable, not a judgment call.

### P5 — WO-S3 + WO-S4 *(M effort, documentation, architect-gated)*

- **WO-S3**: F1–F12 expectation matrices for the ERC-725 and ERC-1056 anchors — **blocked on D5** (architect must ferry in the ISetA/B/C signatures; without them the matrix is explicitly pattern-level, logged as such, not guessed). `createPresentation` recorded as *expected absent for EVM anchors but possibly available off-chain via did-jwt for V6* — an open question, not a pre-seeded checkmark (anchoring-bias guard from the critic).
- **WO-S4**: `docs/ADR-0001_TEST_consolidation.md` (Provisional) — one disposition per build, **each explicitly conditional on its WO-S2 evidence row** (no optimism-graduation of a blocked build). Expected shape: SP-2 = Build-III X/Y (Graduate, iff P3 passed) + Build-II claims pattern (Port) + Build-0 (Port-for-history, **carrying the "not actually CVIN-modified" debunk forward** so the programme never cites it as bespoke work); SP-1 = V6 (Reference; key rotated; retarget later) + V7 (WO-1 host); LSP0 (Park). Tokens [TS-5]/[TS-6]/[TS-7] presented for architect ratification, never self-resolved. No O-number renumbering.

---

## 3. Decision register (what I need from you — a & b live here)

| ID | Decision | My recommendation | Authority |
|---|---|---|---|
| **D1** | **[TS-4] Infura key** | **Rotate NOW, before anything else.** The key sits in the only commit of a *public* GitHub repo — treat as actively compromised (secret scanners scrape public pushes in minutes), and review the Infura dashboard for abuse since exposure. Replacement (if any) lives in an untracked `.env`. **Hard gate: no push of this branch until D1 closes** — FINDINGS pinpoints the key's exact line and would otherwise be a targeting aid | Operator |
| **D2** | **Build-III restore** | **Approve, with the ratified framing:** byte-verified restoration of files upstream *shipped* but the checkout *lacks* is **completion, not modification** — this resolves the genuine conflict between WO-S1's "don't fix upstream" and the H3 reality. Provenance-pinned (tag+SHA+per-file hashes), single revertible commit. If no upstream commit byte-matches the 13 present files, [TS-1] **stays blocked** rather than forced | Operator ratifies; CLI executes |
| **D3** | **Commit WO-S0 now** | **Yes** — P0 is the precondition for every later evidence claim; on the branch, fully reversible | Operator |
| **D4** | **V7 toolbox deviation** | **Approve** `@nomicfoundation/hardhat-toolbox@^2` as a pinned, logged devDependency commit — smallest change satisfying WO-S1's own acceptance; the alternative (rewriting hardhat.config to the waffle plugins) touches more as-found surface | Operator |
| **D5** | **Architect inputs needed before P4/P5** | Request from architect: (1) ISetA/B/C F1–F12 signatures; (2) the sandbox's exact **solidity settings block** (optimizer enabled/runs, evmVersion) — solc version alone doesn't determine bytecode/gas, and this is unpinned everywhere; (3) confirmation the P4 subtask-override recipe matches cvin-sandbox-v1.1's pinning pattern | Architect |
| **D6** | **Build-II expectation downgrade** | Accept: native install is unrecoverable as-pinned (H10, dead `git://` protocol) → Build-II is **source-only triage** in P4; its "runnable-in-principle" label in the Understanding Report gets corrected | Operator ack |

---

## 4. Consolidated risk register (top 8 of 22 reviewed)

| Risk | L×I | Mitigation (phase) |
|---|---|---|
| Build-III `npm ci` dies on git+ssh dep before H3 is even reached | H×H | insteadOf rewrite + offline-replay proof (P1.3/P1.4) |
| npm cache incomplete for git deps, discovered after network window closes | M×H | offline `npm ci --offline` gate NOW + node_modules snapshots (P1.4) |
| Install-time lifecycle-script execution from stale transitive deps (no Docker boundary) | M×H | ignore-scripts posture + 2-of-5 scope + non-elevated shell + egress deny (P1.5/P2) |
| Leaked key abused; FINDINGS push pinpoints it pre-rotation | H×M | D1 first; push gated on closure (P0.1/D1) |
| Hardhat silently downloads solc, contaminating the "offline" baseline | M×H | vendored binaries + subtask override + firewall-on smoke test (P1.1/P4) |
| Restore from wrong upstream version silently shifts the baseline | M×H | byte-diff provenance pin; no match → stay blocked (P1.2/P3.2) |
| "Mechanical port" quietly crosses into logic alteration | L×H | fixed checklist + **selector/event-topic equality check** (P4) |
| Expectation matrix hardens into a verdict downstream | M×M | expectation-not-verdict stamps; zero numbers; open questions stay open (P5) |

---

## 5. Where my plan may differ from yours (comparison hooks)

1. **I put an online provisioning phase (P1) ahead of WO-S1** — the directions never schedule one, but the offline pin makes it existential.
2. **I resolve restore-vs-don't-fix via D2's "completion, not modification" framing** — the architect's plan leaves this genuinely contradictory.
3. **I scope installs to 2 of 5** and leave V6 structurally unrunnable rather than relying on discipline.
4. **I make Standing Rule 1 machine-checkable** (selector/topic equality) instead of assert-only.
5. **I keep one git tree with tags** rather than a physically duplicated `reconstructed/` tree.
6. **I gate the branch push on key rotation**, not just "rotate eventually."

If your plan differs on any of these, that's exactly the comparison worth having before P0 executes.

---

## 6. Prompt primers (pin this altitude in every prompt)

**Universal (add to any prompt):**
> *Operate as the lead researcher and principal architect on this programme: verify the on-disk state before asserting, sequence by dependency and reversibility, tie every claim to captured evidence, surface deviations and decisions instead of smoothing them, and stop at my gates.*

**Task-tuned variants:**
- **Execution passes (WO-S1/S2):** *Execute under the standing rules — pinned toolchain, offline verified by evidence not assertion, full logs with environment headers, expected failures captured as findings, never patched.*
- **Review/critique passes:** *Before agreeing, adversarially attack this for under-specification, missing acceptance criteria, ordering hazards, and unverifiable claims — and return the minimal fix as a decision for me, not a silent change.*
- **Design/ADR passes (WO-S3/S4):* *Recommend, don't implement: one conditional disposition per item, each tied to its evidence row, open questions left open, and my ratification tokens left unresolved.*

---

## 7. Startup guide (fresh terminal, after decisions land)

```powershell
cd C:\Users\nikhilp\Desktop\CVIN-2026-Sanbox1_v6
git -C .\TEST status; git -C .\TEST branch --show-current   # sandbox-onboarding, artifacts present
# P0 (after D1/D3): secret sweep → commit → tag asfound/WO-S0 → manifest
# P1 (network up): vendor solc 0.8.17/0.8.19/0.8.24 → vendor ERC725 v6.0.0 → insteadOf rewrites → npm ci + offline replay (Build-III @ node16, V7 @ node18)
. .\use-node16.ps1    # or use-node18.ps1 — dot-source, per shell
# P2: firewall rules (one UAC) → probe evidence
# P3: as-found failing log → D2 restore commit → restored build+test → V7 toolbox+scaffold check
```
**Standing safety:** V6 (`index.js`) and `react-dapp` are never executed this pass; Build-II is never installed; all chain work is in-process Hardhat only.

---

*End of plan. Reality observed during execution supersedes this document — differences get recorded in FINDINGS, not smoothed. On your word: we execute P0 (a: decisions D1–D4) and then P1–P3 (b: WO-S1).*

---

## Addendum v1.1 (2026-09-24) — execution status & corrections

**Executed since v1.0:** P0 ✅ (freeze, tag `asfound/pre-onboarding`, secret sweeps, 4 PRs to `CVIN-ID/TEST`); P1 ✅ (solc 0.8.17/19/24 vendored checksum-MATCH; Build-III restore provenance byte-pinned to upstream `3b1b4935`; H9/H10 defused via logged insteadOf; npm caches proven by offline replay, lockfiles unchanged). **D5 RESOLVED** by reading canonical `cvin-sandbox-v1.3` (verbatim solidity block `{0.8.24, optimizer runs:200}`+paris default; npm solc-js subtask override; full ISetA/B/C F1–F12 signatures). **D6 confirmed** (H10 dead `git://` → Build-II source-only).

**Corrections (see FINDINGS §G):** gates are **G0–G6**; G0/G1 are operator-executed; `createPresentation` framing refined (anchor-implemented; gap = *native* ERC support); SP-1 = anchor **+ credential anchor pattern**; ERC-740 = unresolved [R1]. §2's P4/P5 text and the §5 comparison stand as written for the record; where they conflict with FINDINGS §G, §G governs.

**New since v1.0:** canonical WO-0 (source-doc ingest) is BLOCKING-open — sequencing question raised to architect (handoff Q3). **Sister repo `nikhilprakash24/CVIN-SC-Implementation-SSI-DID`** carries an active parallel implementation stream (CVINVehicleDIDRegistry, 47/47 suite, W3C checker CI, through 2026-09-24) — **B↔C compliance-regime reconciliation** added as an architect item; this branch is pushed there as `sandbox-onboarding`.

**Still gated:** D1/[TS-4] key rotation (operator, OPEN); D2 restore ratification; D4 V7 toolbox. P2→P3 fire on those words.
