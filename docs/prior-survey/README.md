# Prior survey: the onboarding lineage (reconciliation note)

Written 2026-10-09 for plan step P3.5 of `docs/PLAN_2026-10-09.md` (default Q4: documents only).
Trunk read at `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` @ `7a9a996`.
Lineage read at `origin/sandbox-onboarding` @ `96bb269` with `git show`; nothing was checked out or merged.

## The answer

- The onboarding lineage is a **survey of three identity standards** (ERC-725/735, ERC-1056, LUKSO LSP0) taken from the `CVIN-ID/TEST` repository. Its code is vendored upstream samples with no vehicle logic (source: `FINDINGS.md` section B).
- It shares **no history and no file content** with the trunk: no common commit, and no blob in `git ls-tree -r` of the lineage tip appears in the trunk tree (checked 2026-10-09).
- Its documents are imported here **as provenance only**. Its code is not imported.
- **H1 must be rotated by the author.** An Infura credential is embedded at `CVIN-Implementation-II-ERC1056/CVIN-Implementation-1056Testbed-V6/cvin-v6/index.js:19` on that lineage. It is public on `CVIN-ID/TEST` and on the five lineage branches of this repository's `origin`. Rotate it at the Infura dashboard regardless of the repository being open source. The trunk does not contain it (see the hazard table).
- Of the ten hazards, **one (H9) still exists on the trunk** in the same form, **one (H2) survives as a dead config entry**, and the other eight do not apply to the trunk.

## What was imported

| File here | Source path on the lineage | Last changed in | Blob |
|---|---|---|---|
| `README_onboarding.md` | `README.md` | `b5bd0bc` (2026-07-05) | `f56c111` |
| `FINDINGS.md` | `FINDINGS.md` | `76e2a94` (2026-07-05) | `9d169f5` |
| `UNDERSTANDING_TEST_REPO.md` | `docs/UNDERSTANDING_TEST_REPO.md` | `0272f81` (2026-07-05) | `1d7fb67` |
| `PROGRESS_AND_CHANGE_REPORT_v1.0.md` | `docs/PROGRESS_AND_CHANGE_REPORT_v1.0.md` (content is v1.1) | `5de1834` (2026-09-24) | `7973bcf` |
| `NEXT_STEPS_PLAN_v1.0.md` | `docs/NEXT_STEPS_PLAN_v1.0.md` (v1.0 plus v1.1 addendum) | `5de1834` (2026-09-24) | `0cf11fd` |
| `HANDOFF_TO_ARCHITECT_v1.0.md` | `docs/HANDOFF_TO_ARCHITECT_v1.0.md` | `29cda06` (2026-07-05) | `080c8a5` |
| `EVIDENCE_MANIFEST.txt` | `evidence/EVIDENCE_MANIFEST.txt` | `91c6e1a` (2026-07-05) | `605c790` |

Each file is byte-identical to its source after one prepended HTML comment line naming the branch, path, commit and blob (verified with `cmp`).
No redaction was needed: none of the seven documents contains the H1 key value (checked by matching the 32-character key against every file; zero hits). They name its location only, as the lineage's Standing Rule 7 required.

**Not imported:** the eight evidence logs under `evidence/` and all code under `CVIN-Implementation-*`. The secrets sweep `evidence/WO-S0_network_secrets_20260620-224319.txt` was read: it already masks the key (`<REDACTED-INFURA-KEY [TS-4]>`) and a 64-hex DID fragment, but it is skipped because it is an index of where the secrets sit and the plan imports the manifest only. The manifest's SHA-256 lines let a reader verify those logs on the lineage branch.

## Inventory of the lineage

Root: `0ab45bb` "first commit", author `CVIN-ID`, 2023-11-07 (tag `asfound/pre-onboarding` points to it). All branch tips descend from it alone.

| Branch | Commits after `0ab45bb` | Files it adds |
|---|---|---|
| `wo-s0/understanding-report` | `0272f81` (2026-07-05) | `docs/UNDERSTANDING_TEST_REPO.md` |
| `wo-s0/evidence-and-findings` | `2ed9bcf`, `91c6e1a`, `76e2a94` (2026-07-05) | `FINDINGS.md`, `.gitignore` edit, `evidence/` (9 files) |
| `wo-s0/onboarding-plans` | `2312190`, `29cda06` (2026-07-05), `5de1834` (2026-09-24) | the progress report, next-steps plan and handoff |
| `docs/root-readme` | `b5bd0bc` (2026-07-05) | `README.md` |
| `sandbox-onboarding` | merges of all four, last `96bb269` (2026-09-24) | all of the above (130 files in its tree) |

`sandbox-onboarding` is the most complete version. Every imported document is identical there and on the branch that wrote it (`git diff --quiet`, all seven).

## What the lineage is

- **Dates.** Code as found: 2023-11-07. Inventory pass WO-S0: 2026-06-20 (dates inside `FINDINGS.md`, `UNDERSTANDING_TEST_REPO.md`). Commits and online provisioning P1: 2026-07-05. v1.1 update: 2026-09-24 (`PROGRESS_AND_CHANGE_REPORT_v1.0.md` header).
- **Method** (source: `README_onboarding.md`, `NEXT_STEPS_PLAN_v1.0.md`):
  - gated work orders WO-S0 to WO-S4 (inventory, native bring-up, solc 0.8.24 compatibility triage, F1 to F12 expectation matrices, consolidation ADR);
  - operator and architect gates, decision register D1 to D6;
  - typed placeholder tokens `[TS-1]` to `[TS-7]` that graduate only on captured evidence;
  - an append-only, SHA-256-manifested evidence log;
  - standing rules: offline local EVM only, no interface alteration, secrets by location only.
- **How far it got.** WO-S0 and P0 to P1 were done. WO-S1 never ran: it was gated on D1 (key rotation), D2 (Build-III restore) and D4 (V7 toolbox), all still open at 2026-09-24 (`PROGRESS_AND_CHANGE_REPORT_v1.0.md` section 5). No compile or test result exists on the lineage; FINDINGS section D is all "pending".
- **Its view of the trunk.** v1.1 found this repository as "stream C" and called `CVINVehicleDIDRegistry` "the first actual CVIN logic in the programme" (`PROGRESS_AND_CHANGE_REPORT_v1.0.md` section 1).

## The three tracks and the trunk's options

As-found state is from `UNDERSTANDING_TEST_REPO.md` and `README_onboarding.md`. Trunk state is from `sandbox/options/<option>/README.md` and the contract files named.

| Lineage track (as found) | Trunk option(s) | What the trunk later built |
|---|---|---|
| **I, Build-0**: `CVIN_ERC725.sol`, ERC-725 v1 interface, solc 0.4.24, byte-identical to the standard ("CVIN-modified" is a filename prefix) | `erc-725` | `contracts/ERC725/CVIN_DID_ERC725.sol` (from the trunk's first commit `b23bc4c`, 2025-11-10, a clone of `CVIN-ID-SCs`, a different repo): a 0.8.20 basic proxy with an ERC-734-style key store; 9/9 functions covered by demos; `execute` is a stub |
| **I, Build-II**: Origin/Fractal `KeyHolder` + `ClaimHolder` + `ClaimVerifier`, solc 0.4.24, install dead (H10) | `erc-735` | `contracts/ERC735/CVINVehicleClaimHolder.sol` (added `157a640`, 2026-07-13): one holder per vehicle, on-chain EIP-191 issuer-signature check, per-topic issuer registry and VIN binding (D25a/b fixed 2026-10-04) |
| **I, Build-III**: ERC725Alliance `@erc725/smart-contracts` X+Y, broken as checked in (H3), duplicated (H4) | `erc-725xy` | `contracts/ERC725xy/CVINVehicleERC725XY.sol` (added `9b03300`, 2026-07-19): self-contained, spec-faithful X+Y with all five operation types, written instead of inheriting the vendored package because of an OZ4/OZ5 conflict (comment in the contract, lines 30 to 45) |
| **II, V6**: `ethr-did` quick-start, `did:ethr` creation offline, resolution on Goerli, holds the H1 key | `erc-1056-uport` | `contracts/ERC1056/EthereumDIDRegistry.sol` + `CVINVehicleDIDRegistry.sol` (both `25da1a6`, 2025-11-10): the uPort registry plus a VIN/manufacturer wrapper, run on the local Hardhat network |
| **II, V7**: stock Hardhat `Lock.sol` scaffold, "intended SP-1 on-chain host", empty (H5) | `erc-1056-vehicle` | `contracts/MOBI/ERC1056Registry.sol` (`4a815ba`, 2025-11-10): a vehicle-profile ERC-1056 with `registerVehicle` and a terminal `revokeIdentity` (D21 fixed); the same registry backs the cv2x testbed |
| **III, LSP0**: `LSP2Utils.sol`, `LSP3Constants.sol`, empty `LSP0ERC725Account/`, no build (H8) | `lsp8` | `contracts/LSP8/CVINVehicleLSP8.sol` (`157a640`, 2026-07-13): an LSP8 token per vehicle with a per-token ERC-725Y-style store. This is a **loose mapping**: LSP8 is a digital-asset standard, not the LSP0 account the lineage started; LSP1 and the collection-level store are omitted (`sandbox/options/lsp8/README.md`) |

Note on dates. The trunk's ERC-1056 and ERC-725 contracts (2025-11-10) predate the onboarding documents (2026-06 onward). They do not predate the surveyed code (2023-11-07). The trunk did not build on the lineage's files: no blob is shared.

## Hazards H1 to H10 against the trunk

Hazard text from `FINDINGS.md` section A. Trunk checks run 2026-10-09 on `7a9a996` with `git grep` and `git log -S`.

| # | Hazard on the lineage | On the trunk? | Evidence |
|---|---|---|---|
| H1 | Infura key in `cvin-v6/index.js:19` | **No.** Key absent from the tree and from trunk history | `git grep` of the key value on `HEAD`: 0 files; `git log -S<key> HEAD`: 0 commits. Present on all five lineage branches of `origin` |
| H2 | Code targets retired Goerli | **Residue only.** A `goerli` network entry reads `GOERLI_RPC_URL` (default empty); `.env.example` has a placeholder `YOUR_INFURA_KEY`; no code path runs on it. Live validation targets Sepolia | `1_blockchain-identity/hardhat.config.js:73-77,111`; `1_blockchain-identity/.env.example:7`; `1_blockchain-identity/SEPOLIA_VALIDATION.md` |
| H3 | Build-III imports missing `custom/`, `interfaces/`, `helpers/` | **No.** The trunk's ERC-725 and X+Y contracts have no imports | `grep '^import'` on `contracts/ERC725/*.sol` and `contracts/ERC725xy/*.sol`: none |
| H4 | Flat duplicate of Build-III sources | **Analogue, contained.** One file is duplicated: `contracts/ERC725/CVIN_DID_ERC725.sol` = `_research-copies/ERC725/contracts/CVIN_DID_ERC725.sol` (blob `9d072a5`). The copy is outside `paths.sources` and marked "not compiled, not tested and not measured" | `1_blockchain-identity/_research-copies/README.md`; `hardhat.config.js` `paths.sources: "./contracts"` |
| H5 | V7 holds only the `Lock.sol` sample | **No.** No `Lock` contract on the trunk; two ERC-1056 registries exist | `git grep 'contract Lock'`: none |
| H6 | `hardhat-toolbox` missing; ethers v5 pin vs v6 syntax | **No.** Toolbox `^4.0.0` and ethers `^6.10.0` declared | `1_blockchain-identity/package.json:58,65` |
| H7 | `react-dapp` imports a nonexistent `Greeter` | **No.** No `react-dapp`, no `Greeter` | `git grep Greeter`: none |
| H8 | LSP0 track unbuilt | **No LSP0 at all.** The trunk chose LSP8 instead (row above) | no `LSP0`/`LSP2Utils`/`LSP3` path in `git ls-tree -r HEAD` |
| H9 | Lockfile resolves `ethereumjs-abi` over `git+ssh://` | **Yes, same entry.** `node_modules/ethereumjs-abi` 0.6.8 resolves to `git+ssh://git@github.com/ethereumjs/ethereumjs-abi.git#ee39946…`; CI runs `npm ci`. Whether it breaks a clean install without SSH auth was not tested in this pass | `1_blockchain-identity/package-lock.json:5681-5683`; `.github/workflows/test-contracts.yml:33` |
| H10 | Build-II pins `websocket` over dead `git://` | **No.** Zero `git://` URLs in either trunk lockfile | `grep -c 'git://'` on `1_blockchain-identity/package-lock.json` and `cv2x-testbed/package-lock.json`: 0 |

Follow-ups this suggests (not done here; for the author): delete the dead `goerli` entries (H2), and test `npm ci` with no SSH agent or add an `insteadOf` note (H9).

## What the thesis can use it for

- **Provenance of the standards survey.** The lineage's code (2023-11-07) is the earliest record in reach of the programme comparing an account-per-identity model (ERC-725/735), a shared lightweight registry (ERC-1056) and a LUKSO profile (LSP0). The trunk's nine-standard comparison descends from that question, not from these files.
- **Why ERC-1056.** The lineage does not state a decision. It records the ground for one: ERC-1056 is the track with "gas-free identity creation, key rotation, delegates" (`README_onboarding.md`, track table), and the canonical sandbox it read had admitted only `O1_ERC1056` (12/12) (`FINDINGS.md` section G). Cite it as context for the choice, with the trunk's own gas figures as the evidence.
- **A caution the thesis should carry.** "CVIN-modified" ERC-725 is the unmodified standard (`FINDINGS.md` section B). No chapter should cite the TEST repo as bespoke CVIN work.
- **Method precedent.** The token-graduation rule and the append-only evidence manifest are a documented precedent for the trunk's own evidence discipline.

It cannot supply measurements: the lineage has no compile, test or gas result of its own.

## Not reachable: the second remote

`docs/planning/NEXT_STAGES_PLAN.md` (lines 10 and 161) names a second remote, `nikhilprakash-cvin/2_miniature-waffle-CV2X-Testbed-MOBI-VID`. This session's only remote is `origin` (`nikhilprakash24/CVIN-SC-Implementation-SSI-DID`), and the second repository is not reachable from it. Per plan Q8's default it is **treated as superseded by the trunk**. If the author knows of work there that the trunk lacks, that is a separate import.

## Maintenance

Nothing in this directory is maintained. The lineage branches stay unmerged by design (`docs/HANDOFF_2026-10-03_REVIEW2.md`). The existing pointer at the repository root is `TEST_ONBOARDING.md`.
