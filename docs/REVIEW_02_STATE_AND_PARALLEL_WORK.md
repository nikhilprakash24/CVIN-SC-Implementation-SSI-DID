# Review 02 — The State of the Work and the Parallel Work, as One Picture

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-03
**Scope:** everything on the trunk at `394373c` after the 2026-09-24 merge of the analysis
lineage onto the testbed lineage, read as a single system; what it is, where it is
duplicated, what it tests at which layer, and what feature surface each identity option
really has versus what the comparison measures. The author's notebooks are not in the
repository and are outside this review.
**Companions:** `docs/FEATURE_ASYMMETRY_MATRIX.md` (generated), `docs/PLAN_SANDBOX_AND_SUITES.md`,
`docs/META_COMMENTARY_2026-10.md`, `docs/AFTER_ACTION_REPORT_04.md`.

---

## 1. One picture: three generations of the same thing, now on one trunk

| Generation | Where | What | Status |
|---|---|---|---|
| **G1 — research copies** (Nov 2025, from the CVIN-ID-SCs clone) | `1_blockchain-identity/_research-copies/` (ERC721, ERC725, ERC725xy, ERC1056 notes, ERC1055; archived 2026-10-04, plan S0) | 4 Solidity files + Truffle-era tests + the ERC-1056 comparison notes | not compiled, not run; **source material** |
| **G2 — the Hardhat tree** (Nov 2025 → Sep 2026, incl. the merged analysis lineage) | `1_blockchain-identity/contracts/` (17 `.sol`, 10 options), `test/` (14 files, 219 tests incl. 68 security scenarios), `scripts/` (deploy, `benchmark_gas.js`, `benchmark_scaling.js`) | the **canonical** contracts and the gas/scaling results of record | compiled, green, CI-gated |
| **G3 — the testbed copies** (Nov 2025) | `cv2x-testbed/contracts/` (`ERC1056Registry.sol`, `MOBIVIDRegistry.sol`, `MOBIVIDRegistryV2.sol`, solc 0.8.20) + `scripts/deploy*.js` | the contracts the **Python providers and experiments** talk to | compiled separately, used by #21/#29/#30 |

Around them: the **SSI layer** (`2_w3c-ssi-layer/`: DID resolver, VC issuer/holder/verifier,
MOBI VID Python; 60 pytest), the **providers** (`cv2x-testbed/identity/`: PKI, centralized,
centralized registry, ERC-1056, MOBI VID; `base.py` as the uniform interface), the
**experiments** (`cv2x-testbed/scripts/experiment_*.py` → `cv2x-testbed/results/`), the
**comparison framework** (`4_comparison-framework/`: gas tables, scaling, MOBI backends,
security analysis, now the feature matrix), the **SUMO harness** (`cv2x-testbed/sumo/`),
and the **use cases** (`cv2x-testbed/scripts/test_use_cases.py`, 12, a script not a suite).

### 1.1 The duplication the merge left behind — the one fact to act on
There are **two different contracts both called "ERC-1056"** on the trunk:

| | `EthereumDIDRegistry` (G2) | `ERC1056Registry` (G3, also copied to `contracts/MOBI/`) |
|---|---|---|
| Lineage | uPort/DIF-style registry: implicit identities, `changeOwner(Signed)`, delegates with `validTo`, attributes, `changed()` linked list | a project-specific registry: explicit `registerVehicle`, `isRevoked`, `revokeIdentity`, `getIdentityInfo`, `lastChanged` |
| Measured in | nine-standard gas table (#25), scaling, security harness | PKI-vs-ERC-1056 (#21), freshness-k (#29), the MOBI backend sweep base |
| Resolver | `did_resolver.py` builds `did:ethr` documents | `erc1056_provider.py` walks `getIdentityInfo` + events |

Every "ERC-1056" number in the thesis must say which. This is not a defect — the
G3 registry is the vehicle-specific profile the testbed needed — but it is an
unrecorded design fork, and the sandbox plan's first decision is how to name it.

Second duplication: `contracts/MOBI/` in G2 holds copies of G3's three contracts so the
gas benchmark can deploy MOBI-VID-V2 ("copied from cv2x-testbed, unmodified" per the
benchmark script). Two copies of a contract that must stay identical is the kind of
thing CI should check (plan S0).

## 2. The parallel work: what each lineage contributed, and where they overlap

| Capability | Testbed lineage (this branch's original history) | Analysis lineage (merged from the bundle) | Overlap / tension |
|---|---|---|---|
| Contracts | ERC-721, 725, 1056 (+ G3 trio) | ERC-735, 1155, 4337, 725xy, LSP8, CVIN-Combined, MOBI copies | none in files; the ERC-1056 fork above |
| Tests | ERC-721/1056 suites, VC 28 | 9 option suites, security harness, MOBI python 32 | the ERC-1056 wrapper test had to be restored from the trunk at merge |
| Measurements | PKI-vs-ERC-1056, freshness-k, lifecycle parity, external DID suite (all post-merge, on this trunk) | nine-standard gas, scaling, MOBI backends, V2V 0.165 ms (register B until re-run) | different hosts and different ERC-1056s — compare within runs |
| Providers / experiments | all of `cv2x-testbed/identity`, `scripts/experiment_*` | — | — |
| Documents | roadmap, VID specs, capabilities, RESEARCH_THRUSTS | COMPOSITION, PROVENANCE, SOURCES, THREAT_MODEL, SCALING, RESEARCH_AUDIT, dossiers, chapters | reconciled in `docs/INDEX.md` |

The two lineages were complementary rather than competing: one built the *testbed and
baselines*, the other the *breadth of standards and the analysis*. The seam between
them is exactly the ERC-1056 fork and the MOBI copies.

## 3. Test coverage by the four layers the author named

| Layer | Meaning | What exists today | Gap |
|---|---|---|---|
| **L1 — identity mechanisms** | create, owner/controller change, key or delegate management, attribute/data, revoke, transfer — per option | inside each option's Hardhat suite, written per contract with different vocabularies | no *uniform* cross-option suite; "not applicable" is implicit (a missing test), not recorded |
| **L2 — identity-system mechanisms** | registries, authorisation and roles, lookups (VIN↔DID), events/history, signed (off-chain-authorised) operations, entry points | ERC-1056 registry tests, MOBI issuer matrix (`test_allowed_roles_match_contract_matrix`), ERC-4337 EntryPoint tests, the 68 security scenarios | mixed into L1 files; signed-operation coverage differs per option |
| **L3 — SSI** | DID resolution, VC issue/present/verify, selective disclosure, status/revocation, MOBI VID as VCs | pytest 60 (VC 28, MOBI 23, VIN cipher 9); external W3C DID suite 335/336; internal checker 94.3 % | the external suite is a manual run, not a test; the checker is not a test |
| **L4 — exemplar complex interactions** | lifecycle use cases, V2V message path, multi-party attestation, cross-backend sweeps | 12 use cases (script), SUMO harness (`--simulate` results), three experiments | none is a *test*; a regression in a use case would not fail CI |

Count today: 219 Hardhat + 60 pytest = 279 automated tests, all in L1–L3 with the
layers interleaved; L4 has zero automated tests.

## 4. The feature asymmetry — the union versus the intersection

The comparison measures an **intersection**: six operations (deploy, create, update,
delegate/claim, revoke, transfer) that every option can be made to perform. The
options' real surfaces are **unions** that differ by an order of magnitude
(`docs/FEATURE_ASYMMETRY_MATRIX.md` §1): `MOBIVIDRegistryV2` exposes 54 functions,
`CVINVehicleNFT` 45, `CVINVehicleDIDRegistry` 32, `CVINVehicleCredential1155` 29, while
`EthereumDIDRegistry` exposes 16 and does its most important thing — creating an
identity — with **no function at all** (identity is implicit in the address; creation
costs 0 gas). The thesis has to discuss that asymmetry at length, and the matrix gives
it the evidence. The families that carry the discussion:

- **Creation: implicit vs explicit.** ERC-1056 and ERC-4337 accounts exist before any
  transaction (0 gas, off-chain); ERC-721/1155/LSP8 require a mint by an authorised
  party; ERC-725/735/725xy require a contract deployment per identity (≈0.5–1.7 M
  gas). Same word, three mechanisms, three cost classes.
- **Veracity: on-chain state vs signed assertion.** ERC-735 claims and MOBI attestations
  are on-chain facts anyone can read; VCs are off-chain assertions whose truth is a
  signature plus a status check. The on-chain form is automated and auditable; the
  off-chain form is private and cheap. The matrix's "Claims / credentials" row counts
  on-chain claim machinery; the VC layer is its off-chain mirror and is absent from the
  matrix by construction.
- **Automation: contracts enforce, verifiers must be run.** Issuer-role matrices
  (MOBI V2), `onlyManufacturer`, guardian recovery (ERC-4337), execution through
  `execute()` (ERC-725/725xy) are enforcement the chain performs; the VC flow enforces
  nothing until a verifier checks.
- **Off-chain-authorised execution.** `changeOwnerSigned`/`setAttributeSigned` (ERC-1056),
  UserOperations through the EntryPoint (ERC-4337), ERC-2612-style permits where
  present: the capability to act on-chain from an off-chain signature is unevenly
  available and changes who pays gas.
- **Cryptography and hashing choices.** keccak-256 attribute keys and VIN hashes
  (salted, `salted_vin_hash`), AES-GCM VIN cipher, EIP-191 proofs in the VC layer versus
  raw `ecrecover` over the ERC-1056 digest (the signing-scheme mismatch found on
  2026-09-24), secp256k1 everywhere versus P-256 in the PKI baseline. These are
  design choices with measured costs (secp256k1 signing 0.40 ms vs P-256 0.054 ms in
  #21) and they belong in the asymmetry chapter, not in a footnote.
- **Token economics** (approvals, royalties, toll payment) exist only in the
  NFT-shaped options and are "features not used in the comparison" by definition — the
  clearest example of what the author asked to be implemented in each sandbox anyway.

## 5. What is left (feeds the plan)

1. A **canonical home per option** that references (never copies) its contracts,
   providers and tests, and carries a **feature manifest** (implemented / measured in
   comparison / not applicable, with the reason) — the per-option sandbox.
2. A **grand sandbox**: one runner that can deploy any option, run L1–L4 against it,
   and emit the asymmetry table and results — the original sandbox guide's "base to
   build and test anything", made real.
3. **Layered suites** L1–L4 with the 279 tests re-homed and the L4 gap closed (use cases
   as tests; experiments as reproducibility checks).
4. **Feature demos** per option covering every relevant feature, including the ones the
   comparison does not use.
5. **The ERC-1056 fork named**, and the MOBI contract copies checked for identity in CI.
6. The **asymmetry section** of the thesis written from the matrix and the demos.
