# TDP-008 — Configuration Baseline (As Built)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** B.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000). **Supersedes:** nothing; the
authoritative baseline for any single figure is its register row and the stamp in its result file. This document
collects them in one place and adds nothing.
**Format:** MIL-STD-498 software version description, reduced to: identification, the configuration items with their
versions, the runs of record with their identities, the toolchain pins, the build and reproduction procedure.

## 1. Identification

| Item | Value |
|---|---|
| Repository | `nikhilprakash24/CVIN-SC-Implementation-SSI-DID` (public, MIT) |
| Trunk branch | `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` |
| Version file | `VERSION` reads `0.9.0-dev`; last tag pushed is an author decision (N-11) |
| Baseline of this package | the commit that closes after-action report 20 (recorded in its closing section) |
| Parallel work at the time of writing | WM-2 C1 (the resolver reads the chain) closed 2026-10-15 at `7ae268a`; #4 and #24 unchanged |

## 2. Configuration items

| Item | Path | Version or identity |
|---|---|---|
| Contracts, nine standards and MOBI profile | `1_blockchain-identity/contracts/` | tree hash recorded per harness run (`meta.measured.contractsTree`) |
| Metrics harness | `1_blockchain-identity/benchmarks/` | `meta.measured.benchmarksTree`; re-run at A6 (`1f4ace0`) |
| Gas benchmark producer | `1_blockchain-identity/scripts/benchmark_gas.js` | run of record commit `d0cc19c` (`gas_benchmark.json` metadata, dirty false) |
| cv2x contracts | `cv2x-testbed/contracts/` (`ERC1056Registry.sol`, `MOBIVIDRegistry.sol`, `MOBIVIDRegistryV2.sol`) | solc 0.8.20 per `cv2x-testbed/hardhat.config.js`; artifacts checked fresh in CI |
| W3C layer | `2_w3c-ssi-layer/` | resolver, VC issuer/holder/verifier, MOBI VID I/II |
| Testbed | `cv2x-testbed/` | identity providers, experiments, SUMO harness with mock mobility, infrastructure layer (verifier v3 at `7d08dce`) |
| Sandbox | `sandbox/` | 13 option manifests, L1 to L4 suites, 92 demos, grand runner |
| Evidence tools | `tools/run_identity/` | `stamp.py`, `promote.py`, `producers.json` (20 producers), `scopes.json` (generated) |
| Layer 5 (ZKP and agent-wrapped identity) | `5_zkp-agent-identity/`; `1_blockchain-identity/hardhat.zkp.config.js` | circom 2.2.2 (#56); snarkjs 0.7.6, node v22.22.0 (#57); Groth16 keys from a single-party setup, insecure for deployment (#57); artefact SHA-256 in `artifacts/MANIFEST.json`, checked in CI |
| Documents | `docs/` | register, charters, generated pages, this package |
| CI | `.github/workflows/` | `test-contracts.yml` (1 job), `w3c-compliance.yml` (4 jobs), `benchmark.yml` (3 jobs), `zkp-layer5.yml` (3 jobs); CI Python packages pinned in `ci/requirements-ci.txt` |

## 3. Runs of record and their identities

| Register rows | Producer | Code commit | Result commit or run id | Identity fields |
|---|---|---|---|---|
| #25 | `benchmark_gas.js` | `d0cc19c` | `4_comparison-framework/results/gas_benchmark.json` | `metadata.dirty` false; 30 of 30 runs byte-identical |
| #29, #30, #31, #34, #35, #36, #49, #50, #51 | `benchmarks/run.js` | `1f4ace0` | run `2026-10-23T00-49-12Z_1f4ace0` (`results/metrics/latest/`; was `2026-10-09T02-09-36Z_7a9a996`) | `measured.{benchmarksTree, contractsTree, hardhatConfigBlob, lockfileBlob}`; `dirty` false; Hardhat 2.28.6, Node v22.22.0, ethers 6.17.0 |
| #21, #22, #23 | `experiment_pki_vs_erc1056.py` | `0b39570` (A3b) | results `f1f3596` | `git_dirty` false; cryptography 50.0.1; Python 3.13.16; Xeon 2.10 GHz |
| #27 | `run_v2v_stats.py` | `0b39570` (A3b) | results `f1f3596` (`cv2x-testbed/sumo/results/v2v_latency_stats.json`) | 30 seeded runs, Xeon 2.10 GHz x 4; A3b re-run done (was `58a6513`, pre-merge lineage) |
| #32 | `experiment_freshness_k.py` | `f1f3596` (A3b) | results `1f21007` | `git_dirty` false; host Xeon 2.10 GHz; D51 block-time read |
| #33 | `experiment_lifecycle_parity.py` | `2051159` (re-run 2026-10-22) | results `63a8ab9` | `git_dirty` false |
| #37 | `experiment_freshness_k.py --refresh-mode` | `f1f3596` (A3b) | results `1f21007` | host Xeon 2.10 GHz x 4 |
| #38 | `experiment_pseudonym_pool.js` | `e49bcb4` | results `439b118` | `git_dirty` false |
| #44, #45, #46, #48 | `run_infra_stats.py` | `7d08dce` (verifier v3); A3b re-run `0b39570` | `infrastructure_stats.json`, `infrastructure_revocation.json`; run logs `run_logs/2026-10-14_7d08dce/` | `code_clean` true; clean worktree |
| #47 | `infrastructure_gas.js` | `a950cdf` | `infrastructure_gas.json`, `infrastructure_gas_runs/` | seeds 1 to 30 declared; seed 1 exact |
| #52 | `experiment_freshness_k.py` at `8216507` and `f660402` | both | `cv2x-testbed/results/freshness_k_c3/` with manifest (order, commits, sha256) | copied with a manifest as a declared deviation (old-commit runs cannot pass promote) |
| #4 | `w3c_compliance_checker.py` | review-02 tree | `w3c_compliance.json` | self-scored; unchanged by C1 (resolves without a provider; N-24) |
| #24 | external suite `939b31d` | — | `docs/conformance/reports/**/*-2026-10-04b.*` | 335 of 336; unchanged by C1 (resolves without a provider; N-24) |
| #28 | `securityScenarios.test.js` | merged tree | `attack_results.json`, `security_matrix.*` | strict harness; promoted through `promote.py` since A4 |
| #56 to #61 (layer 5) | `bench/run_all.sh` (`prove_and_verify.js`, `measure_gas.js`, `sigma_bench.py`, `vin_bruteforce.py`, `run_attacks.py`) | `978988e` | `5_zkp-agent-identity/results/` | `code_clean` true, `tree_clean` false; producers unchanged on the merged trunk except a citation-key comment |
| #62 (layer 5) | `bench/manual_burden.py` | `e780d40` | `5_zkp-agent-identity/results/manual_burden.json` | `code_clean` and `tree_clean` true; values identical to the `978988e` run |

Rows whose producing code changed after their stamp (D50; #21, #26 in part, #27, #32, #33, #37, #38) were re-run
at A3b (2026-10-22/23); the register rows #21, #26, #27, #32, #33 and #37 carry the A3b notes.

## 4. Toolchain pins

| Component | Pin | Where |
|---|---|---|
| Node | 22 (CI); v22.22.0 at the harness run of record | workflows; `meta.json` |
| Hardhat | 2.28.6 at every run of record (2.29.1 moved two ERC-721 cells by 12 and 25 gas, section 5.E) | `package-lock.json`; `meta.json` |
| ethers | 6.17.0 | `meta.json` |
| solc | 0.8.24, optimizer 200, viaIR, EVM cancun (executed under the node's default hardfork, recorded as `network.hardfork`) | `hardhat.config.js`; `meta.json` |
| OpenZeppelin | 5.0.2 (contracts and upgradeable); the testbed must regenerate tracked artifacts with the root `node_modules` as CI does | `package.json`; handback gotcha |
| Python | 3.11 (CI); 3.13.16 at the A3b runs of record | workflows; result headers |
| web3 | 6.11.0 pinned in `2_w3c-ssi-layer/requirements.txt`; 8.0.0 observed in the freshness run header; CI now pins 8.0.0 through `ci/requirements-ci.txt` (installs read `"$GITHUB_WORKSPACE/ci/requirements-ci.txt"`) | requirements file; result header |
| cryptography | 41.0.7 pinned in the requirements file and in `ci/requirements-ci.txt`; 50.0.1 at the A3b runs of record, so CI and the runs of record differ (PKI cold verify halves between 41 and 49, #27 note) | same |
| Chain | id 31337, automine, block gas limit 60,000,000 | `meta.json`; result headers |

Two pins are known to disagree between the requirements file and the runs of record (web3, cryptography); the plan's
hygiene item G makes the file installable and complete. Until then a chapter cites the run header, not the file.

## 5. Build and reproduction

```bash
git clone https://github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID && cd CVIN-SC-Implementation-SSI-DID
git checkout claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy
(cd 1_blockchain-identity && npm ci && npx hardhat compile)
pip install -r ci/requirements-ci.txt
python3 sandbox/grand/run.py all                                   # every suite; stage table in sandbox/grand/report/
python3 docs/figures/make_dashboard_data.py --check                # generated documents (all twelve --check commands: DWG-005)
python3 docs/tdp/make_vcrm.py --check && python3 docs/tdp/make_fmeca.py --check && python3 docs/tdp/make_blueprints.py --check
```

A result of record is reproduced by running its producer from `producers.json` at its code commit in a clean
worktree, with a fresh node started by path, and promoted with `tools/run_identity/promote.py`; the promote step
refuses a run whose stamp is not HEAD, so an earlier-commit reproduction is compared, not promoted.

## 6. Change control

- A change under the four measured paths of the harness (`benchmarks/`, `contracts/`, `hardhat.config.js`,
  `package-lock.json`) requires a new harness run of record (register section 5.F).
- A change to a verifier requires a dated pre-registration amendment before the re-run (A6 before C0).
- A change to any file a generated document reads requires regeneration in the same commit; CI compares.
- A new producer is registered in `producers.json` before its first run; `stamp.py --write` then `--check`.
- A toolchain change is a conditions change: re-run and re-promote; never mix cells from runs with different
  `meta.hardhat`.

## Revision history

| Rev | Date | Change |
|---|---|---|
| B | 2026-10-24 | corrected from docs/tdp/REVIEW_2026-10.md (after-action report 38): C1 closed, harness re-run at A6, CI four workflows and pinned CI packages, Node v22.22.0, A3b commits for #21, #27, #32, #33, #37 and #44 to #48, Python 3.13.16 and cryptography 50.0.1, layer-5 item, runs and pins |
