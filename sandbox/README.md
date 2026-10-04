# Sandbox — the grand sandbox and the per-option sandboxes

The sandbox is a **layer of declaration** over the existing code (plan:
`docs/PLAN_SANDBOX_AND_SUITES.md`; rationale: `docs/META_COMMENTARY_2026-10.md`). It never
copies contracts or providers; it points at them.

- `options/<slug>/manifest.yaml` — the option's feature ledger: every capability family
  with a stance (`measured-in-comparison` / `implemented` / `not-applicable`), the
  functions behind it, a reason, and `reviewed: false` until a human has looked at it.
  Generated skeletons come from `grand/make_manifests.py` (ABIs + benchmark notes +
  provider methods); review means editing the stance/reason and flipping `reviewed`.
- `grand/manifest.yaml` — the union of all options; `grand/run.py matrix` renders
  `grand/report/asymmetry.md`; `grand/run.py check` fails on any empty cell.
- `suites/L1..L4` — the layered test suites (plan S3–S6), added step by step.
- `options/<slug>/adapter.js|py`, `demos/` — plan S2, S7.

Twelve options: ten on-chain (the two ERC-1056 variants named in
`docs/MEASUREMENT_CONDITIONS.md` §1.1, ERC-721, 725, 725xy, 735, 1155, 4337, LSP8,
CVIN-Combined, MOBI VID) and two in-process baselines (PKI, centralized registry).

Regenerate after any contract or benchmark change:
```
python3 4_comparison-framework/feature-matrix/make_feature_matrix.py
python3 sandbox/grand/make_manifests.py      # keeps reviewed flags? no — see below
python3 sandbox/grand/run.py matrix
```
Regeneration overwrites manifests; reviewed edits must be re-applied or the generator
extended to merge them (plan S1 follow-up). Until then, review in a separate commit.
