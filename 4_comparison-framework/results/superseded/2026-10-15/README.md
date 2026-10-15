# Superseded result files (quarantined 2026-10-15, TSR Plan Phase 0, W0-B)

Kept for provenance; **not results of record** and not to be cited in chapters (`docs/INDEX.md` rule).

| File | Why superseded | Superseding file | Still referenced by |
|---|---|---|---|
| `sensitivity.{json,csv,tex}` | dated 2026-07-24, `evmTarget: paris` (the trunk is cancun), and no generator script exists in the repository, so it cannot be regenerated or verified | none yet; a sensitivity re-run (SN-1 optimizer runs, SN-2 calldata) needs a committed generator first (Phase 5) | `docs/thesis/chapter5-results/README.md` §provenance, `docs/SCALING_EXPERIMENTS.md` §SN |
| `w3c_compliance_2026-07-23.json` | checker output of 2026-07-23 (93.18 %, 40/2/2); the checker on HEAD reports 94.3 % (41/1/2) after the review-02 resolver fixes | `../w3c_compliance.json`, regenerated on HEAD 2026-10-15 by `cv2x-testbed/scripts/w3c_compliance_checker.py` (no commit/environment stamp yet; stamping is Phase 5) | `SOURCES.md` row "93.2% W3C compliance" |

`docs/figures/results_snapshot.json` (commit `708302a`, 89.6 %, 47 tests) is **not** moved: it is the input of `docs/figures/make_verification_figure.py`. It is a dated snapshot, not the results of record; `docs/MEASUREMENT_CONDITIONS.md` §1 still calls it "current" and is listed for Phase 7 reconciliation.
