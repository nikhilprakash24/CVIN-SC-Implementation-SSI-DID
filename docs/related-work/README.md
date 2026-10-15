# Related Work Workspace

Working files for `docs/planning/EXPLORATION_PLAN.md`.

| File | Holds |
|---|---|
| `refs.bib` | Verified BibTeX only (resolved DOI / arXiv ID / standards URL) |
| `matrix.csv` | One row per kept paper: what it claims, how it was measured, which RQ it touches, and whether it threatens the gap claim (Ch2 §2.5) |
| `repos.csv` | One row per inspected code base, with a reuse decision |
| `tools.csv` | One row per tool trial, with a verdict |
| `SEARCH_LOG.md` | Every query run, with hit / screened / kept counts |
| `pdfs/` | Local only (git-ignored): PDFs fetched through library access |

## PRISMA counts

| Stage | Count |
|---|---|
| Records identified | 0 |
| After de-duplication | 0 |
| Screened (title/abstract) | 0 |
| Full text assessed | 0 |
| Included | 0 |

## Phase log

### Phase 0 — baseline (2026-10-15)

Run from branch `claude/exploration-plan` on top of `fa6188e`, in the cloud
container (Node 22.22.0, Python 3.13.16), using the same steps as CI:

| Check | Result |
|---|---|
| `npx hardhat compile` | 47 Solidity files, evm cancun |
| `npx hardhat test` | **369 passing**, 23 pending |
| `check_artifacts_fresh.js` (cv2x-testbed) | fresh |
| `pytest 2_w3c-ssi-layer cv2x-testbed/tests` (Hardhat node on :8548) | **358 passed**, 0 skipped |
| `w3c_compliance_checker.py` | **94.3%** |

369 + 358 = 727; with the 12/12 lifecycle use cases that matches the README's 739.

**Note on "no skips":** the 23 pending Hardhat tests are capability-gated
`this.skip()` calls in `test/benchmarks/adapters.conformance.test.js`. When an
adapter doesn't support an operation (`R2_resolve_by_vin`, `U2_add_delegate`,
`D2_revoke_attribute`, `U5_meta_tx`), its test for that operation is skipped. This
is intended, but the README's "no skips" is strictly true only of the Python
suites, where CI fails on any skip. Suggest rewording to "no unexplained skips
(23 capability-gated adapter cases)".
