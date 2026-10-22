<!-- Source: branch origin/sandbox-onboarding (tip 96bb269), path docs/HANDOFF_TO_ARCHITECT_v1.0.md, last changed in commit 29cda06, blob 080c8a5. Imported 2026-10-09 as provenance; not maintained. -->
# Handoff: TEST-Repo Onboarding → Architect Chat

**CVIN-SC Research Programme · CLI-agent handback per Directions §8 · v1.0 · 2026-07-05**
**From:** CLI agent (Claude Code session "Build CV2X testbed for connected vehicles") · **To:** Architect (planning chat) · **Via:** Operator (Nikhil)

*Paste-ready context for the architect chat. Self-contained: assumes the architect has the directions sheet (`CVIN-TEST_Sandboxing_Build_Directions_v1-0`) but no access to this machine. Everything empirical below is backed by a committed evidence file; nothing is asserted from documentation alone.*

---

## 1. Executive state

**WO-S0 is complete and ferried; P0–P1 of the CLI-side plan are executed; WO-S1 is provisioned but gated on three operator/architect decisions.** All artifacts are pushed as four reviewable PRs against `CVIN-ID/TEST` (via fork `nikhilprakash24/TEST` — the operator's GitHub account has no org write access):

| PR | Contents |
|---|---|
| [#1](https://github.com/CVIN-ID/TEST/pull/1) | `evidence/` (9 files + SHA-256 manifest), `FINDINGS.md` (hazards H1–H10, tokens, P1 + integration records) |
| [#2](https://github.com/CVIN-ID/TEST/pull/2) | `docs/UNDERSTANDING_TEST_REPO.md` (Provisional, per-§4-template) |
| [#3](https://github.com/CVIN-ID/TEST/pull/3) | `docs/PROGRESS_AND_CHANGE_REPORT_v1.0.md`, `docs/NEXT_STEPS_PLAN_v1.0.md`, this handoff |
| [#4](https://github.com/CVIN-ID/TEST/pull/4) | Comprehensive root `README.md` (repo had none) |

Baseline frozen: tag `asfound/pre-onboarding` at the original single commit `0ab45bb`.

## 2. Headline findings (each evidence-backed)

1. **The repo is a survey, not a system.** `CVIN_ERC725.sol` is byte-identical to standard ERC-725 — the "CVIN-modified" label is a filename prefix. No vehicle/VIN logic exists anywhere. (Understanding Report §Build-0.)
2. **Build-III is the best asset but broken as checked in** (H3): core contracts import `custom/`, `interfaces/`, `helpers/` — absent from the repo. **Restore source now byte-pinned:** upstream `ERC725Alliance/ERC725` commit **`3b1b4935db8c…`** matches all 13/13 checked-in contracts byte-identically *and* contains the missing dirs (evidence `P1_upstream_diff_*`). It is a **develop-branch commit** (`v3.2.0-112-g3b1b493`), not the v6.0.0 tag — consistent with the folder name "ERC725-develop".
3. **Two install blockers the directions didn't anticipate:** H9 — Build-III's lockfile resolves `ethereumjs-abi` via `git+ssh://` (hard-fails without SSH auth; **defused** by logged `insteadOf` rewrites, install proven). H10 — Build-II pins `websocket` over the dead `git://` protocol → its native install is unrecoverable; **downgraded to source-only triage**.
4. **The leaked Infura credential ([TS-4])** at `cvin-v6/index.js:19` sits in the *public* repo's only commit — treat as compromised; rotation remains **open, operator-only** (D1).
5. **Offline readiness achieved:** solc 0.8.17/0.8.19/0.8.24 vendored (exe+wasm **release** builds, all checksums MATCH vs `binaries.soliditylang.org`); npm caches for Build-III (Node 16, 1109 pkgs) and V7 (Node 18, 576 pkgs) proven by `npm ci --offline` replay, lockfiles hash-unchanged, zero lifecycle scripts executed.

## 3. Parallel-work integration (read: `cvin-sandbox-v1.3`, 2026-06-05)

The operative canon is **v1.3** (directions referenced v1.1). Canonical state: **one architect-pass baseline** (O1_ERC1056 12/12; single S1 trace 2026-06-05 with real gas); **no operator-executed gate on record; G1–G6 not run; WO-0 ingest BLOCKING-open; all canonical WOs open.**

**Recovered inputs the WO-S pass was missing (former [TS-blockers], now resolved from canon):**
- Full **ISetA/ISetB/ISetC + IMinimalSSI F1–F12 exact signatures** (Set A = F1–F4, F9–F12; Set B = F5–F8; ISetC = optional ERC-8004 layer). WO-S3 matrices can now be built at full F-granularity.
- **Pinned toolchain verbatim:** `0.8.24, optimizer {enabled, runs:200}`, no evmVersion (→ `paris`), offline solc via the in-config `TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD` override returning npm solc-js.
- **Compliance mechanics:** parameterized 12-test suite, "Admission = compliance," O2–O8 are named empty port slots ("Do not stub functions to pass tests").

**Corrections we logged against our own sheet/plan (Standing Rule: logged, not smoothed):** gates are **G0–G6** (not G0–G5); **G0/G1 are operator-executed**, only G2–G5 are WO-encoded; `createPresentation` is *declared and anchor-implemented* (62441 gas on O1) — the structural finding is "no ERC provides it **natively**" (AnonCreds = Set B ceiling), recorded in ARCHITECTURE §1/§9 + ISetB NatSpec, not in the sandbox FINDINGS; SP-1 = "ERC-1056 anchor **+ credential anchor pattern**"; ERC-740 attribution is unresolved token **[R1]**, never fact.

**Risks flagged upward (architect action suggested):**
- Canon dep `"solc": "^0.8.24"` is an **unpinned caret** — a fresh install may float to a later 0.8.x, silently shifting the reproducibility envelope. Recommend pinning exact `0.8.24` (or adopting our checksummed `soljson-v0.8.24+commit.e11b9ed9.js`, evidence `P1_solc_vendor_*`).
- Canonical sandbox needs **Node ≥ 20**; the TEST repo's legacy builds need Node 16/18 (portable, provisioned). Two runtimes, cleanly separated on this machine.
- Sandbox `package.json` has no wired scripts; the documented `IMPL=… npx hardhat run` form needs `$env:IMPL` on PowerShell hosts.

**Fold-in map (TEST → canon):**
| TEST output | Canon slot |
|---|---|
| Build-III operator bring-up (restored, Node 16) | **First operator-executed G0 on record** → BUILD_LOG closeout |
| Fresh `IMPL=O1_ERC1056` S1 run on operator hardware | **G1** (compare vs 2026-06-05 trace; re-log the known createDID 162–179K vs <100K deviation) |
| Build-II Origin ERC-735 claims pattern | **T-735 / G4** material under WO-1a/1b (SP-2 composite) |
| Build-0 `CVIN_ERC725.sol` | Port-for-history reference; **carry the "not actually CVIN-modified" debunk** into any citation |
| V6 off-chain `did:ethr` demo | SP-1 off-chain reference; retarget off Goerli later; [TS-4] first |
| TEST inventory/plan docs | Enter canon **only via WO-0** ingest (documentary; may never resolve empirical tokens) |
| WO-S2 compatibility table (pending) | **G2** deliverable, unblocks WO-1a |

## 4. Token & decision register (state at handoff)

| Token/Decision | Status | Needs |
|---|---|---|
| [TS-1] Build-III suite at Node 16 | Open — restore source byte-pinned, install proven | **D2** ratification → run WO-S1 |
| [TS-2]/[TS-3] 0.8.24 compat / port | Open — compiler + scratch plan provisioned | WO-S2 execution |
| [TS-4] Infura key | **Open — operator-only (D1)** | Rotate at dashboard + usage review |
| [TS-5] SP-2 anchor choice | Open (architect) | WO-S4 ADR after WO-S2 |
| [TS-6] V7 → SP-1 host scope | Open (architect + later WO) | — |
| [TS-7] LSP0 scope | Open (architect/supervisor) | — |
| D4 V7 `hardhat-toolbox@^2` deviation | Awaiting operator OK | one pinned devDep commit |
| **New (this pass):** WO-0 sequencing | Canon WO-0 is BLOCKING-open | Architect: ingest order vs TEST-pass continuation, or logged waiver |

## 5. Questions for the architect (answerable in one message)

1. **D2** — Ratify: byte-verified restoration of Build-III's missing dirs from upstream commit `3b1b4935` = *completion, not modification*? (Evidence: 13/13 byte-match.)
2. **[TS-5] preview** — Any objection to the expected shape: SP-2 anchor = restored Build-III X/Y + Build-II ERC-735 claims pattern, Build-0 as history-only?
3. **WO-0** — May the TEST pass proceed to WO-S1/S2 while WO-0 (v2-0 DOCX + LFDT Addendum ingest) remains open, with the dependency logged? Or ingest first?
4. **solc pinning** — Adopt exact-pin (or checksummed vendored soljson) for canon's `^0.8.24` caret?
5. **Gate credit** — Confirm the fold-in map above (TEST bring-up = operator G0; fresh S1 = G1) so evidence lands in BUILD_LOG under the right gates.
6. **[TS-7]** — LSP0: park with tracked follow-up, per our recommendation?

## 6. Where everything lives

- **Repo/PRs:** `github.com/CVIN-ID/TEST` PRs #1–#4 (from fork `nikhilprakash24/TEST`); integration branch `sandbox-onboarding`; tag `asfound/pre-onboarding`.
- **Machine:** `C:\Users\nikhilp\Desktop\CVIN-2026-Sanbox1_v6\` — `TEST\` (working clone), `toolchain\` (portable Node 16/18, vendored solc, upstream ERC725 clone, warm npm cache, extracted `parallel-work\cvin-sandbox-v1.3`), `use-node16/18.ps1`.
- **Evidence:** `TEST\evidence\` (9 files + `EVIDENCE_MANIFEST.txt`, SHA-256, append-only).
- **Canon:** `toolchain\parallel-work\cvin-sandbox-v1.3\cvin-sandbox\` (read-only extraction of the Downloads zip).

*On D1+D2 (+optionally D4), the CLI agent executes: P2 egress lockdown → WO-S1 (as-found failing log → provenance-stamped restore commit → Build-III build+test at Node 16 → V7 scaffold check) → WO-S2 compatibility triage at the canon-verbatim 0.8.24 config → WO-S3 matrices at full F1–F12 granularity → WO-S4 ADR. Reality over expectation; deviations to FINDINGS.*
