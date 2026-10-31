# Plan — Grand Sandbox, Per-Option Sandboxes, Layered Test Suites

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-03
**Inputs:** `docs/REVIEW_02_STATE_AND_PARALLEL_WORK.md`, `docs/FEATURE_ASYMMETRY_MATRIX.md`
**Principle:** sandboxes **reference** the canonical code, they never copy it. The plan adds
manifests, adapters, suites and demos around the existing 17 contracts, 5 providers and
279 tests; it does not move contracts.

---

## 1. Target structure

```
sandbox/
  README.md                      # what a sandbox is; how to run any option at any layer
  grand/                         # the grand sandbox: one runner for all options × all layers
    run.py                       # cvin-sandbox <option|all> <L1|L2|L3|L4|demos|matrix>
    manifest.yaml                # the union: every capability family, every option's stance
    report/                      # generated: asymmetry table, per-layer results, timings
  options/
    erc-1056/                    # one directory per option (10) + baselines (2)
      manifest.yaml              # features: implemented | measured-in-comparison | not-applicable (+ reason)
      adapter.js                 # uniform IdentityOption interface over the option's contracts
      adapter.py                 # same interface over the option's provider (where one exists)
      demos/                     # one script per capability family, exercising EVERY relevant feature
      README.md                  # the option's asymmetry notes (on/off-chain, crypto, automation)
    erc-721/ erc-725/ erc-725xy/ erc-735/ erc-1155/ erc-4337/ lsp8/ cvin-combined/ mobi-vid/
    baseline-pki/ baseline-centralized/
  suites/ -> ../1_blockchain-identity/test  (symlink: Hardhat test files must resolve chai/hardhat from inside the project)
    L1-identity-mechanisms/      # uniform cross-option suite driven by the adapters
    L2-identity-system/          # registries, roles, lookups, history, signed ops, entry points
    L3-ssi/                      # DID resolution, VC, MOBI-as-VC, conformance hooks
    L4-exemplar-interactions/    # use cases as tests, V2V harness smoke, experiment reproducibility
```

Existing trees stay where they are; `sandbox/` points into them. Each `manifest.yaml`
is the per-option feature ledger; `grand/manifest.yaml` is their union and is the
source for the thesis's asymmetry table (replacing the regex heuristics of the
generated matrix with declared, reviewed stances).

### The uniform `IdentityOption` interface (adapter contract)
```
deploy()                       -> handle            # or attach(address)
create(identity, {vin, owner}) -> receipt|None      # None = implicit creation (0 gas)
changeController(id, new)      -> receipt
addKeyOrDelegate(id, key, purpose, validity) -> receipt | NotApplicable
setAttribute(id, key, value)   -> receipt | NotApplicable
addClaim(id, topic, data, sig) -> receipt | NotApplicable
revoke(id|claim)               -> receipt
transfer(id, to)               -> receipt | NotApplicable
resolve(id)                    -> DIDDocument-like dict
signedOp(id, op, signature)    -> receipt | NotApplicable   # off-chain-authorised execution
capabilities()                 -> manifest subset           # what the adapter claims to support
```
`NotApplicable(reason)` is a first-class result: L1 records it, never skips silently.

## 2. Steps, each with its acceptance check

| # | Step | Done when |
|---|---|---|
| S0 ✅ 2026-10-04 | **Name the ERC-1056 fork and pin the MOBI copies.** Document `EthereumDIDRegistry` (uPort-style) vs `ERC1056Registry` (vehicle profile) in `docs/MEASUREMENT_CONDITIONS.md` as two sub-options; add a CI check that `contracts/MOBI/*.sol` equals `cv2x-testbed/contracts/*.sol` byte for byte | register note merged; CI job fails on divergence |
| S1 ✅ 2026-10-04 | **Manifests.** Write the 13 `manifest.yaml` (the two ERC-1056 variants from S0, eight other on-chain options, MOBI VID, 2 baselines) from the generated matrix §3 lists plus the providers; three stances per capability family with a one-line reason | `grand/run.py matrix` renders the union table with no empty cells |
| S2 ✅ 2026-10-04 | **Adapters (JS).** `adapter.js` per on-chain option implementing the interface over the G2 contracts; `NotApplicable` where the manifest says so | a smoke script creates/changes/resolves one identity per option |
| S3 ✅ 2026-10-04 | **L1 suite.** One mocha file per L1 mechanism, parameterised over all adapters; asserts behaviour where supported, records N/A otherwise; emits `report/L1-asymmetry.json` | runs green across 10 options; the N/A table matches the manifests |
| S4 ◐ 2026-10-04 (re-home done; signed-op table pending) | **L2 suite.** Re-home the existing registry/role/entry-point/security tests under `suites/L2-identity-system/` via mocha config (no rewrites); add a uniform signed-operation test across the options that declare it | 219 Hardhat tests still pass from the new layout; signed-op coverage table emitted |
| S5 ✅ 2026-10-04 | **L3 suite.** Re-home the 60 pytest; add the external DID test-suite run as a pytest that reads `docs/conformance/reports/` and asserts no regression below 335/336; make the internal checker a pytest asserting ≥ 94.3 | `pytest sandbox/suites/L3-ssi` green; conformance regression caught |
| S6 ✅ 2026-10-04 | **L4 suite.** Turn the 12 use cases into pytest cases (each use case = one test with its own fixture chain); add a V2V harness smoke test (`--simulate`, 10 vehicles, 2 s) and reproducibility tests for the three experiments (`--render-only` + schema checks) | `pytest sandbox/suites/L4-exemplar-interactions` green in < 3 min |
| S7 ✅ 2026-10-04 | **Demos.** Per option, one script per capability family exercising every relevant feature the manifest marks "implemented" — including the ones the comparison never uses (royalties, toll, guardian recovery, batch credentials, LSP data keys, execute(), signed ops) — printing gas and the on/off-chain stance | every "implemented" manifest entry has a demo that runs |
| S8 ✅ 2026-10-04 | **Grand runner.** `run.py` orchestrates deploy → L1–L4 → demos → report for one or all options; the report is the asymmetry chapter's data | `python3 sandbox/grand/run.py all` completes and writes `report/` |
| S9 ✅ 2026-10-04 (contract job collects L1+L2; python-layers job covers L3+L4; nightly benchmark separate) | **CI.** One job per layer; L4 nightly; the matrix generator and the grand report as artifacts | four green jobs |
| S10 ◐ 2026-10-04 (draft section written; chapter placement is decision 3) | **Thesis.** Chapter 6 (or a new chapter 5 section) "Feature asymmetry: the union versus the intersection" written from `grand/report` | section drafted with the table and the on/off-chain discussion |

Order: S0 → S1 → S2 → S3 (the first visible result: the cross-option L1 table) → S4/S5
(re-homing, low risk) → S6 (closes the L4 gap) → S7 → S8 → S9 → S10.
Effort: S0–S3 ≈ 2 days; S4–S6 ≈ 2 days; S7 ≈ 2–3 days (it is the "every feature" ask);
S8–S10 ≈ 2 days.

## 3. What the author decides (nothing else blocks S0–S9)

1. **Naming the fork**: keep both ERC-1056 variants as sub-options ("ERC-1056 /
   uPort-style" and "ERC-1056 / vehicle profile") — recommended — or unify on one.
2. **G1 research copies**: archive under `1_blockchain-identity/_research-copies/` with a
   README (recommended) or leave in place.
3. **Where the asymmetry discussion lives**: a section of chapter 6, or its own chapter.

## 4. Risks and guards
- Scope creep in S7 ("every relevant feature"): bounded by the manifests — a feature is
  demoed only if it is in the option's manifest, and the manifest is reviewed first (S1).
- A fourth copy of contracts: forbidden by the reference-only principle; adapters import
  artifacts from `1_blockchain-identity/artifacts`.
- Re-homing breaking CI: S4/S5 move files only after the mocha/pytest configs prove
  the moved suites still collect the same number of tests.
- Host/condition drift in L4 reproducibility tests: they check *schema and sanity*,
  not numbers, so they do not fail on a different CPU.
