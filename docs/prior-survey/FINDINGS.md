<!-- Source: branch origin/sandbox-onboarding (tip 96bb269), path FINDINGS.md, last changed in commit 76e2a94, blob 9d169f5. Imported 2026-10-09 as provenance; not maintained. -->
# FINDINGS — CVIN-ID/TEST Sandbox Onboarding

**Status:** Provisional · **Pass:** WO-S0 (inventory & safety sweep) · **Branch:** `sandbox-onboarding` · **Date:** 2026-06-20
**Scope rule:** This file logs *deviations and hazards only* (Standing Rule 4). Empirical compile/test results land here from WO-S1/WO-S2. No secret value is printed (Standing Rule 7) — locations only.

---

## A. Hazards (WO-S0 — surfaced, not acted on)

| # | Hazard | Location (only) | Severity | Action owner | Token |
|---|---|---|---|---|---|
| H1 | **Leaked credential** — Infura RPC key embedded in source | `CVIN-Implementation-II-ERC1056/CVIN-Implementation-1056Testbed-V6/cvin-v6/index.js:19` | High (rotate regardless of liveness) | **Operator** | [TS-4] |
| H2 | **Deprecated network** — code targets Goerli (retired) | `…/cvin-v6/index.js:9,19,20,28` (`chainNameOrId='goerli'`, infura goerli, publicnode goerli) | Med (resolution will fail) | Architect (retarget later) | — |
| H3 | **Broken imports** — Build-III core contracts import `./custom/`, `./interfaces/`, `contracts/helpers/` which are **absent** | `…/Build-III-…/ERC725-develop/implementations/contracts/*.sol` | High (blocks compile) | CLI agent (WO-S1) | [TS-1] |
| H4 | **Duplicate source** — flat copy of Build-III contracts | `…/Build-III-…/SmartContracts/*.sol` (byte-identical to `…/implementations/contracts/`) | Low (double-count risk) | Evaluate one only | — |
| H5 | **Empty shell, not a build** — V7 `contracts/` holds only the Hardhat `Lock.sol` scaffold | `…/cvin-v7/contracts/Lock.sol` | Info (intended SP-1 host, empty today) | Confirm; do not fill this pass | [TS-6] |
| H6 | **Plugin/version mismatch** — V7 config + tests require `@nomicfoundation/hardhat-toolbox` (absent from `package.json`); `deploy.js` uses ethers v6 syntax while ethers is pinned v5 | `…/cvin-v7/hardhat.config.js`, `…/test/Lock.js`, `…/scripts/deploy.js`, `…/package.json` | Med (blocks `hardhat` cmds as-is) | CLI agent (WO-S1) | — |
| H7 | **Non-functional dApp** — `react-dapp` imports a nonexistent `Greeter` artifact, `ethers` not declared, CRA `index.js` entrypoint overwritten | `…/cvin-v7/react-dapp/src/index.js`, `index_template_base.js`, `package.json` | Low (out of scope this pass) | Park | — |
| H8 | **Unbuilt branch** — LSP0 track has no build system; `LSP0ERC725Account/` empty; `LSP2Utils.sol` imports uninstalled `@erc725/smart-contracts` | `CVIN-Implementation-III-LSP0/` | Info | Park | [TS-7] |
| H9 | **git+ssh transitive dep** — Build-III lockfile resolves `ethereumjs-abi` via `git+ssh://git@github.com/…` → `npm ci` hard-fails without GitHub SSH auth; git deps carry no npm integrity hash | `…/ERC725-develop/implementations/package-lock.json` | High (blocked install) | **Defused** via git `insteadOf` rewrite (P1.3, logged deviation); resolution proven by pass-1 exit 0 + offline replay | — |
| H10 | **Dead protocol dep** — Build-II lockfile pins `websocket` to a personal fork over `git://` (protocol retired by GitHub 2022) → native install unrecoverable as-pinned | `…/erc725-master/package-lock.json` | Med | Build-II downgraded to **source-only triage** in WO-S2 (D6) | — |

> H1 — **Operator only** acts on the key (rotate/remove + move to untracked `.env`). The CLI agent does not echo, commit, or transact with it.

---

## B. Deviations observed at inventory (expectation vs. reality)

- **"CVIN-modified" is a misnomer.** `Build-0/SmartContracts/CVIN_ERC725.sol` is byte-for-byte the standard ERC-725 v1 identity interface (only a trailing newline differs vs the Build-II copy). Contract is still declared `contract ERC725`, pragma `0.4.24`, standard key-purpose constants. **No VIN/vehicle field or logic exists.** The `CVIN_` is a filename prefix only.
- **No subfolder is at the pinned toolchain.** Pragmas span `0.4.24` (Build-0, Build-II), `^0.8.0/^0.8.5/^0.8.17` (Build-III), `^0.8.9 / 0.8.19` (V7). Evaluation target is **solc 0.8.24, offline-pinned**. ⇒ central task is *compatibility triage*, not bring-up.
- **Build-III is reference-only as checked in** (H3) — repo-content gap, not a toolchain issue.
- **V7 is a stock `npx hardhat init` scaffold** — `Lock.sol`, `test/Lock.js`, `scripts/deploy.js`, README are unmodified samples; no ERC-1056 / DID-registry Solidity present.
- **V6 is the verbatim ethr-did quick-start** — DID *creation* runs offline; *resolve()/lookupOwner()* depend on live (dead) Goerli.

---

## C. Placeholder token register (TS-#)

| Token | Class | Question | Authority | Status |
|---|---|---|---|---|
| [TS-1] | Empirical | Build-III ERC725 passes X/Y suite at Node 16.19.0? | CLI agent (WO-S1) + operator | **Open** — restore source now **pinned**: upstream `ERC725Alliance/ERC725` commit `3b1b4935db8c8576647bd064bf9c9c2f8724721e` byte-matches all 13/13 checked-in contracts AND contains the missing `custom/`/`interfaces/`/`helpers/` dirs (evidence `P1_upstream_diff_*`); awaiting **D2** ratification, then WO-S1 runs |
| [TS-2] | Empirical | ERC-725 X/Y compiles at 0.8.24 offline unmodified or only after mechanical port? | CLI agent (WO-S2) | **Open** |
| [TS-3] | Empirical | `CVIN_ERC725.sol` (0.4.24) ports cleanly to 0.8.24; what changes? | CLI agent (WO-S2) | **Open** |
| [TS-4] | Documentary→action | Is in-repo Infura key live? (Rotate regardless.) | **Operator** | **Open** — H1 |
| [TS-5] | Design | Canonical SP-2 ERC-725/735 anchor in `cvin-sandbox-v1.x`? | **Architect** (WO-S4) | **Open** |
| [TS-6] | Design | Minimal scope to make V7 the SP-1 on-chain ERC-1056 host? | Architect + CLI (later WO-1) | **Open** |
| [TS-7] | Scope | Is LSP0 in the evaluation window or parked? | Architect / supervisor | **Open** |

*No documentary source may resolve [TS-1], [TS-2], [TS-3] — these graduate only from an actual offline compile/test log.*

---

## D. Compatibility table @ solc 0.8.24 (offline) — **WO-S2, pending**

| Candidate set | Native pragma | Compiles unmodified | Compiles after mechanical port | Blocked (reason) | Evidence |
|---|---|---|---|---|---|
| Build-III ERC725 X/Y | ^0.8.x | _pending_ | _pending_ | (H3 must be resolved first) | — |
| Build-0 `CVIN_ERC725.sol` | 0.4.24 | _pending_ | _pending_ (expect 0.4→0.8 port) | — | — |
| Build-II Origin contracts | 0.4.24 | _pending_ | _pending_ | — | — |

*(Port notes to capture per row: constructor syntax, `constant`→`view`, explicit visibility, storage-array returns, SPDX header, integer/overflow semantics.)*

---

## E. Evidence index (immutable, timestamped)

- `evidence/WO-S0_filetree_<ts>.txt` — full file tree (excl. `.git`).
- `evidence/WO-S0_pragmas_<ts>.txt` — every `pragma solidity` with path:line.
- `evidence/WO-S0_network_secrets_<ts>.txt` — RPC/network references in source (`.js`/`.ts`), **secret values redacted**.
- `evidence/P1_solc_vendor_<ts>.txt` — solc 0.8.17/0.8.19/0.8.24 vendoring, exe+wasm **release** builds, all checksums MATCH vs `binaries.soliditylang.org` list.json (includes a documented correction: first wasm pass mis-grabbed nightlies).
- `evidence/P1_upstream_diff_<ts>.txt` — Build-III provenance: upstream commit `3b1b493…` = 13/13 byte-match + missing dirs present.
- `evidence/P1_git_insteadof_<ts>.txt` — environment deviation: `ssh://`→`https://`, `git://`→`https://` rewrites (H9/H10), reversible via `--unset-all`.
- `evidence/P1_buildIII_npmci_<ts>.log` / `evidence/P1_v7_npmci_<ts>.log` — `npm ci --ignore-scripts` online pass + **offline replay** both exit 0; lockfile SHA-256 unchanged (before=after recorded in-log).
- `evidence/EVIDENCE_MANIFEST.txt` — append-only SHA-256 manifest of every evidence file.

*Append-only. A new run is a new file (Standing Rule 6). Log convention: header block (UTC, command, cwd, node/npm versions, git HEAD), exit-code lines, native output captured via shell redirection.*

---

## F. P1 provisioning record (2026-07-05, online window)

Executed per `docs/NEXT_STEPS_PLAN_v1.0.md` P1; scope = the 2-of-5 install set (Build-III, V7). **Deviations, all logged and reversible:** (1) global git `insteadOf` rewrites (H9/H10); (2) `--ignore-scripts` posture on all installs (zero lifecycle scripts executed); (3) npm cache relocated to `toolchain\npm-cache` (sandbox-local). **Provisioned:** 6 checksum-verified solc release binaries; upstream ERC725 clone with the restore commit pinned by byte-diff; warm npm caches proven by offline replay; `node_modules` left in place for WO-S1 (gitignored). **Not done (gated):** Build-III source restore (awaits **D2**); V7 `hardhat-toolbox` addition (awaits **D4**); any compile/test (WO-S1/P3). Key rotation **[TS-4]/D1 remains open — operator action**.

---

## G. Parallel-work integration record (2026-07-05, exploration pass)

**Located & read (read-only, staged at `toolchain\parallel-work\`):** `cvin-sandbox-v1.3` (canonical sandbox, 2026-06-05, from Downloads zip), `METHODOLOGY.md` (byte-identical twin of the sandbox copy), plus programme docs (thesis registries v11.3, Building Paths Unified v4.0, Native Sandbox Methodology v1.0). The directions referenced *v1.1*; **v1.3 is the operative canon.**

**Canonical state (from BUILD_LOG/traces/BUILD_PLAN):** one architect-pass baseline only — O1_ERC1056 12/12 compliant, single S1 trace `i2i_O1_ERC1056_1780620182135.jsonl` (2026-06-05, real gas: createDID 178935, issueCredential 130163, createPresentation 62441…). **No operator-executed gate on record; G1–G6 not run; WO-0 (source-doc ingest) is BLOCKING and open; canonical WO-0..9 + WO-1a/1b/WO-R all open.** Gates are **G0–G6** (seven; G6 = architect evidence-merge/graduation).

**[D5 RESOLVED — architect inputs recovered from canon]:**
- *Solidity settings (verbatim)*: `solidity: { version: "0.8.24", settings: { optimizer: { enabled: true, runs: 200 } } }` — **no evmVersion** (default → `paris`), no metadata knobs.
- *Offline solc mechanism*: in-config `TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD` subtask override returning npm-installed **solc-js** (`node_modules/solc/soljson.js`, `isSolcJs: true`) for 0.8.24 only; CLAUDE.md: "Do not remove that override."
- *ISetA/B/C + F1–F12*: full exact signatures extracted (Set A = F1–F4 + F9–F12; Set B = F5–F8; ISetC = optional ERC-8004 layer, no F-numbers). Compliance = parameterized 12-test suite; **"Admission = compliance"**; O2–O8 are empty PORT-TARGET slots.

**Corrections to our onboarding docs (logged, not smoothed — NEXT_STEPS_PLAN v1.0 & Understanding Report stand as written, superseded on these points):**
1. Gate count: our plan said G0–G5; canon is **G0–G6**.
2. G0/G1 are **operator-executed** gates (Operator Guide), not CLI-agent work orders; only G2–G5 are WO-encoded (WO-1a/1b/WO-R).
3. `createPresentation` (F8): **declared in ISetB and implemented on O1** as a replay-protected on-chain anchor (62441 gas measured). The structural finding is "**no ERC provides it natively**" (AnonCreds = Set B coverage ceiling) — recorded in ARCHITECTURE.md §1/§9 + ISetB NatSpec, **not** in the sandbox's FINDINGS.md. Our Understanding Report's "expected absent" phrasing → refine to "no native ERC support; satisfied via anchor pattern."
4. SP-1 = "ERC-1056 anchor **+ credential anchor pattern**" (not bare ERC-1056); SP-2's ClaimIssuerRegistry is attributed to ERC-740 only as unresolved token **[R1]** — never state as fact.
5. WO-S namespace stays external to canon (as the directions intended); TEST outputs fold in as **evidence**, not new O-numbers.

**New risks flagged upstream (for architect):**
- Canon's `solc: ^0.8.24` is a **caret range with no commit pin** — a fresh install could float to a later 0.8.x solc-js. Our checksum-verified vendored `soljson-v0.8.24+commit.e11b9ed9.js` (evidence `P1_solc_vendor_*`) can harden this to an exact artifact.
- Canonical sandbox requires **Node ≥ 20** (BRINGUP §2) — system Node 24 serves it; our portable Node 16/18 remains correct for the TEST repo's legacy builds only.
- Sandbox `package.json` has no runnable scripts (`npm test` = exit-1 stub); commands are `npx …`; the documented `IMPL=<Name> npx hardhat run …` env-prefix form needs `$env:IMPL='…'` on PowerShell.

**Fold-in map (TEST → canon):** Build-III operator bring-up → the first **operator-executed G0** on record; a fresh `IMPL=O1_ERC1056` S1 run on this machine → **G1** (compare against the 2026-06-05 trace; expect and re-log the known createDID 162–179K vs <100K deviation); Build-II Origin/ERC-735 claims → **T-735 / G4** material under WO-1a/1b; TEST inventory/plan docs → enter canon only via **WO-0** ingest (documentary evidence; may never resolve empirical tokens).
