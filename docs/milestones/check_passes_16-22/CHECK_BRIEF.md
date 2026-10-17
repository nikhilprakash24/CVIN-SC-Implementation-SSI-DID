# Check Brief: Passes 16–22

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-17 (after-action report 22).
**For:** a session on a different assistant model, as its first task (`docs/HANDOFF_2026-10-17.md` §3).
**Purpose:** passes 16–22 were done by one assistant configuration. Before WM-2 step A3 turns more results into runs of
record, a second configuration re-verifies what those passes claim. The check reports; it does not fix.

## 1. How to work
1. Read `docs/STYLE_AND_RIGOUR_GUIDE.md`, `docs/HANDBACK_2026-10-14.md` §7, and `docs/HANDOFF_2026-10-17.md`.
2. Open after-action report 23 for the check and commit it before anything else.
3. For each claim in §3, run the command, compare with the expected result, and record a finding when they disagree,
   when the command cannot be run as written, or when the claim says more than the evidence shows. Agreement is
   recorded too, as one line, so the coverage is visible.
4. Also look for what this brief does not list. Section 4 names places where judgement was used.
5. Write `FINDINGS.md` in this directory (format in §5). Commit and push it; close report 23 with CI's result.

## 2. Setup
`(cd 1_blockchain-identity && npm ci && npx hardhat compile)`; Python 3.11 with `pip install eth-account coincurve
cryptography web3 pytest numpy pyyaml`. A Hardhat node, when a command needs one, is started with
`(cd 1_blockchain-identity && node node_modules/.bin/hardhat node --port 8548 &)`, and stopped by its process ID.

## 3. Claims to verify
| # | Pass | Claim | Where recorded | Command | Expected | Falsified if |
|---|---|---|---|---|---|---|
| K1 | 16 | Verifier v3's tests fail on v2 and pass on v3; the mutation script kills every mutant | report 16; register #44–#46 | `python3 -m pytest -q sandbox/py-suites/L3-ssi/test_infrastructure_v3.py`; `python3 sandbox/py-suites/L3-ssi/mutation/mutate_infrastructure_layer.py` | all pass; 39 of 39 mutants killed | a test passes on v2, or a mutant survives |
| K2 | 16 | I1 is reported as it fell: outside the band, not falsified | register #44 | read `cv2x-testbed/sumo/results/infrastructure_stats.json` and the pre-registration `docs/design/INFRASTRUCTURE_PREREG.md` with amendments | ratio 1.226, CI [1.219, 1.238], band [0.80, 1.20], falsified above 2.0 | the verdict does not follow from the numbers and the pre-registered rule |
| K3 | 16 | Under the review's IDTx definition, 4 of 26 Phase 1 gates are IDTx; the IDTx prototype's gate mutants are all killed | `docs/phase2/reviews/DISPOSITIONS_F1-F3.md`; `docs/phase2/focus/F1_onchain_storage_idtx/` | `bash phase2/idtx/mutate_idtx.sh` | 5 of 5 mutants killed | a mutant survives, or the count of 4 does not follow from the definition |
| K4 | 17 | Seeded runs reproduce: I4 is a range over declared seeds 1–30, and seed 1 is exact | register #47 | `(cd 1_blockchain-identity && npx hardhat run scripts/infrastructure_gas.js)` on a clean tree (it rewrites `4_comparison-framework/results/infrastructure_gas*`), then `git diff` those files and restore them with `git checkout` | only stamp fields differ; every seed's gas values identical | any seed's gas value differs |
| K5 | 18 | 27 of 110 harness cells vary in total gas; the harness flag marks 14; the causes are as tabled | `docs/testing/GAS_CHARTER.md` | recount from `1_blockchain-identity/results/metrics/latest/raw.jsonl` with your own script, not `gas_charter.py` | 27 / 14 / the cause table | a different count or cause |
| K6 | 18 | Every result card's numbers are in its register row; the check fires on a wrong headline | `docs/figures/make_result_cards.py` | change one headline in `CARDS` and run `--check`; read five cards against their rows | the check fails; the cards agree with the rows | a card says more than its row |
| K7 | 19 | On one host, the code difference between #32 and #37 (full refresh) is within the replicate spread, so their register difference is the host's | register #52; report 19 §1a (rule committed before the runs) | recompute `t_chain` means and spreads from `cv2x-testbed/results/freshness_k_c3/c3_*.json` | means 7.74 and 7.55 ms; spreads 0.34 and 1.21 ms | the numbers differ, or the rule as written does not give "host" |
| K8 | 19 | The contribution record's scope: one unrelated branch excluded (9 commits), the identities as git records them, no line counts | `docs/figures/make_contribution_record.py` | `git log --all` counts by identity, with and without the excluded branch | the page's counts | a count differs, or the page claims more than the history shows |
| K9 | 21 | Of 9 chain tests, 7 fail on the old resolver; #4 and #24 do not move | report 21; register #4, #24 | the old/new procedure of report 21 §2 on a fresh node; `python3 cv2x-testbed/scripts/w3c_compliance_checker.py`; regenerate `docs/conformance/generate_implementations.py` into a scratch directory and compare | 7 fail on old, 9 pass on new; 94.3 %; inputs identical up to timestamps | a different split, a moved score, or a differing input |
| K10 | 22 | Of 4 D54 tests, 3 fail on the old contracts; `attestEvent` execution gas 198,694 ± 0 | report 22; register #28 | old/new procedure on `1_blockchain-identity/test/L2-identity-system/per-option/MOBIVID/attestEventRegression.test.js` | as stated | as stated |
| K11 | 22 | After C2 only MOBI-VID-V2 cells move, with the deltas tabled in report 22 | report 22; register #25, #26 | re-run `benchmark_gas.js`, `mobi_vid_backend_sweep.js`, `benchmark_scaling.js` on a clean tree at `92cc4d5`; diff every field against the parent commit's results | the table of report 22 | any other cell moves, or a delta differs |
| K12 | 22 | Chapter 5's comparative sentences still hold with the new MOBI values | `docs/thesis/chapter5-results/README.md` §5.3, §5.9 | recompute each ratio and ordering from the result files | "6–9×", "cheapest native attestation", lifetime dominance | any sentence no longer follows |
| K13 | 21 | CI was red from `4699f21` (parallel pass) and the fix (TDP-006 as a history document for the stale-figure checker) hides no current figure | report 21 §2 | read every line of `docs/tdp/TDP-006_FMECA.md` that holds a number the checker lists | each is a quoted history value | a current claim relies on a superseded number |

## 4. Where judgement was used (look harder here)
- Report 19 §1a's rule did not say which spread to use when the two configurations differ; the report gives both readings.
- Report 21's defaults C1-d1 to C1-d4: keeping the default document without a provider, and deferring a chain-backed
  suite run (N-24).
- Report 22's defaults C2-d1 to C2-d5: the plan's fix over review-02's narrower one; storing delegations in the
  registry; `veriKey` as the delegate type; the role still required; and leaving the testbed copies unchanged (N-25).
- The contribution record shows the repository's history to readers outside the project; whether anything on it can
  mislead.

## 5. Findings format (`FINDINGS.md`)
One table, one row per finding, most severe first.

| Column | Content |
|---|---|
| Id | F1, F2, … |
| Claim | K-number, or "new" |
| Severity | H (a result, verdict or chapter claim is wrong), M (a record is wrong or a guard does not fire), L (wording, a path, a missing note) |
| Observed | what the command gave, with the command |
| Expected | what the claim said, with its source |
| Note | one or two sentences; no fix |

Then one line per K-number that agreed ("K4: agrees; seeds 1–30 identical"), so the coverage of the check is visible.
