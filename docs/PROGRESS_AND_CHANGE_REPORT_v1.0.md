# CVIN-ID/TEST — Progress & Change Report

**v1.1 · 2026-09-24 · supersedes v1.0 (2026-06-20; superseded sections retained in git history)**
**Pass:** WO-S0 → P1 complete + parallel-work integration + handoff · **Branch:** `sandbox-onboarding` · **Status:** Provisional

> v1.1 update: written after (a) execution of plan phases P0–P1, (b) integration of the canonical `cvin-sandbox-v1.3`, (c) the architect handoff, and (d) discovery that the **sister repo [`nikhilprakash24/CVIN-SC-Implementation-SSI-DID`](https://github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID)** carries an active parallel implementation stream (commits through 2026-09-24). This branch now also lives there as `sandbox-onboarding`.

---

## 1. The three streams (read this first)

| Stream | What it is | State |
|---|---|---|
| **A. TEST onboarding** (this repo/branch) | Gated WO-S characterisation of the original survey repo | WO-S0 ✅, P0–P1 ✅, WO-S1 gated on D1/D2/D4 |
| **B. Canonical sandbox** (`cvin-sandbox-v1.3`, 2026-06-05) | IMinimalSSI F1–F12 + 12-test compliance canon; O1_ERC1056 12/12; gates G0–G6 | Architect-pass baseline only; G1–G6 unrun; WO-0 blocking-open |
| **C. Sister implementation** (`CVIN-SC-Implementation-SSI-DID`) | Thesis implementation repo: 9 ERC standard impls, **`CVINVehicleDIDRegistry`** (ERC-1056 wrapper — the first *actual CVIN logic* in the programme), ERC-721 DID variant, **47/47 reconciled test suite**, gas figures, W3C compliance checker + CI, audits (`docs/AUDIT_01_ORIGINAL_GOALS.md`), MOBI VID specs | Active — autonomous sessions through **2026-09-24** |

**⚠️ New reconciliation item (architect-level):** streams B and C now embody **two different compliance regimes** — canon's 12-test "Admission = compliance" IMinimalSSI suite (O1 only) vs. the sister repo's own 47/47 suite + Python W3C checker. They are not yet mapped to each other. Ruled by the architect, not here. (Also noted: the sister README references a further repo, `nikhilprakash-cvin/2_miniature-waffle-CV2X-Testbed-MOBI-VID`.)

**Scoped correction to v1.0's headline:** "no CVIN logic exists anywhere" remains true **of CVIN-ID/TEST as-found** — but no longer of the programme: stream C's `CVINVehicleDIDRegistry.sol` (+ tests) is real, working CVIN vehicle-identity code.

## 2. Work completed since v1.0

| Phase | Outcome | Evidence/PR |
|---|---|---|
| **P0 freeze** | WO-S0 artifacts committed; baseline tag `asfound/pre-onboarding` @ `0ab45bb`; secret sweeps clean | [PR #1](https://github.com/CVIN-ID/TEST/pull/1) |
| **PRs opened** | 4 cross-fork PRs into `CVIN-ID/TEST` (org write denied → fork `nikhilprakash24/TEST`) | [#1](https://github.com/CVIN-ID/TEST/pull/1) [#2](https://github.com/CVIN-ID/TEST/pull/2) [#3](https://github.com/CVIN-ID/TEST/pull/3) [#4](https://github.com/CVIN-ID/TEST/pull/4) |
| **P1.1 solc vendored** | 0.8.17/0.8.19/0.8.24, exe+wasm **release** builds, all checksums MATCH (incl. documented correction of a nightly mis-grab) | `evidence/P1_solc_vendor_*` |
| **P1.2 provenance pinned** | Upstream `ERC725Alliance/ERC725` commit **`3b1b4935`** = 13/13 byte-match of Build-III contracts + contains the missing `custom/`/`interfaces/`/`helpers/` dirs | `evidence/P1_upstream_diff_*` |
| **P1.3 H9/H10 defused** | `ssh://`/`git://`→`https://` insteadOf rewrites (logged, reversible) | `evidence/P1_git_insteadof_*` |
| **P1.4 offline npm proven** | Build-III (Node 16, 1109 pkgs) + V7 (Node 18, 576 pkgs): online `npm ci --ignore-scripts` **and** `--offline` replay exit 0; lockfiles hash-unchanged; zero lifecycle scripts | `evidence/P1_*_npmci_*` |
| **Root README** | Repo had none (verified); comprehensive one added | [PR #4](https://github.com/CVIN-ID/TEST/pull/4) |
| **Canon integration** | `cvin-sandbox-v1.3` read; **D5 resolved** (verbatim solidity block; solc-js override; full F1–F12 ISetA/B/C signatures); 5 corrections + 3 upstream risks logged | `FINDINGS.md` §G |
| **Architect handoff** | Paste-ready handback with 6 numbered architect questions | `docs/HANDOFF_TO_ARCHITECT_v1.0.md` |
| **Sister-repo integration** *(v1.1)* | Stream C discovered/read; this branch pushed to the sister repo; cross-reference doc added there | this report §1 |

## 3. Corrections adopted since v1.0 (logged in FINDINGS §G, not smoothed)

Gates are **G0–G6** (not G0–G5); **G0/G1 are operator-executed** (only G2–G5 are WO-encoded); `createPresentation` (F8) is *declared and anchor-implemented* on O1 (62,441 gas) — the structural finding is "no ERC provides it **natively**"; SP-1 = "ERC-1056 anchor **+ credential anchor pattern**"; ERC-740 attribution stays unresolved token **[R1]**; canon's `solc: ^0.8.24` caret is unpinned (float risk — our checksummed vendored soljson can harden it); canonical sandbox needs **Node ≥ 20** (system Node 24 serves it; portable 16/18 are for TEST's legacy builds only).

## 4. Foundation status (verified, unchanged since P1)

Portable Node **16.19.0** + **18.20.4** in `toolchain\` (system Node untouched); 6 vendored solc release binaries; upstream ERC725 clone with pinned restore commit; warm npm caches proven offline; extracted canon at `toolchain\parallel-work\cvin-sandbox-v1.3\` (read-only); `use-node16.ps1`/`use-node18.ps1` activation.

## 5. Open gates & next steps

| Gate | Owner | State |
|---|---|---|
| **D1 / [TS-4]** — rotate leaked Infura key (`cvin-v6/index.js:19`, public since first commit) | **Operator** | **OPEN — standing reminder** |
| **D2** — ratify Build-III restore from `3b1b4935` (byte-proven completion-not-modification) | Operator | Open |
| **D4** — V7 `hardhat-toolbox@^2` pinned deviation | Operator | Open |
| Architect answers (6 Qs incl. WO-0 sequencing, solc pinning, gate credit) | Architect | Open — see handoff |
| **NEW: B↔C compliance-regime reconciliation** | Architect | Open — §1 |

**On D1+D2 (+D4):** P2 egress lockdown → WO-S1 (as-found failing log → provenance-stamped restore → Build-III build+test @ Node 16 → V7 scaffold check) → WO-S2 @ canon-verbatim 0.8.24 → WO-S3 matrices @ full F1–F12 → WO-S4 ADR.

## 6. Where everything lives

- **Sister repo (working home):** [`nikhilprakash24/CVIN-SC-Implementation-SSI-DID`](https://github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID) — implementation stream on its `claude/*` branches; this onboarding stream on branch **`sandbox-onboarding`**; cross-reference doc at repo root.
- **Upstream PRs:** `CVIN-ID/TEST` #1–#4 (via fork `nikhilprakash24/TEST`).
- **Machine:** `C:\Users\nikhilp\Desktop\CVIN-2026-Sanbox1_v6\` (clone, toolchain, evidence, handoff copy at root).
- **Evidence:** `evidence/` — 9 files + `EVIDENCE_MANIFEST.txt` (SHA-256, append-only).
