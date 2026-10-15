# After-Action Report 19 — Contribution Record and WM-2 C3 (Freshness Rows on One Host)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-15, after report 18 closed at `b7997f8` (CI 8/8 green on `aba1d7c`); closed at the end of this pass
**Brief (the author, 2026-10-15):** continue; also produce a GitHub contribution visual to show the professors the
work, without embellishment, showing the good work in the best honest light.

## 1. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| CR | Contribution record: a page generated from the git history and committed evidence. A contribution calendar (commits per day), what the commits touched (by area), milestones (tags, merged pull requests, closed after-action reports), and what the work produced (tests, demos, register rows, defects, CI jobs, pre-registered verdicts), each figure with its source | orchestrator; visualisation engineer; technical writer | every figure is computed from git or a committed file; the page states its scope (which branches, which identities, what a commit count does and does not measure); published as a private page |
| C3 | WM-2 C3: #32 and #37 back to back on one host (design in §1a) | orchestrator; V2X specialist; measurement methodologist | the decision rule in §1a written and committed before the first run; the host-dependence note in #37 replaced by a measured comparison |
| R | Records, grand run last, CI | orchestrator | CI green on the closing commit |

### 1a. C3 design (written before any run)
- **Question.** #32 (full refresh, `t_chain` 10.52 ms) and #37 (full refresh 14.38 / 10.28 ms in replicates r1 / r2;
  probe 2.76 / 2.89 ms) were measured on different hosts and different code. #37 says "never mix with #32". C3 asks
  how much of the difference is the host.
- **Code.** Each row is re-run at its own code: #32 at `8216507` (`--deploy`, default full refresh); #37 at
  `f660402` (`--deploy --refresh-mode full --rotation` and `--deploy --refresh-mode probe --rotation`). The D51
  provider fix (`7d08dce`) is not used: measuring it is A3b. Each run is in a clean worktree at that commit.
- **Host and order.** This container, alone, nothing else running. A fresh Hardhat node per run. Replicate 1 in the
  order #32, #37-full, #37-probe; replicate 2 in the reverse order. Default `n = 250`, `ks = 1,5,25,inf`.
- **Decision rule.** Let s be the spread of `t_chain` (full refresh) between the two replicates of the same
  configuration on this host. If #32-code and #37-code full-refresh `t_chain` differ on this host by no more than
  s, the register's difference between #32 and #37 is attributed to the host; otherwise to the code (or both),
  and the size of each is stated. The probe-versus-full ordering of P*(0.5) per k is reported as it falls.
- **Recording.** Outputs go to `runs/` first. The promote step requires the stamp's commit to be HEAD, which a run of
  an earlier commit cannot meet, so, as for the C0 runs, the outputs are copied to a C3 results directory with their
  commit, hashes and run logs, as a declared deviation. The rows' runs of record are not replaced: C3 adds a
  comparison, and #32 and #37 gain a note.

## 2. Execution log
- 2026-10-15 — report opened.
- **C3, runs.** Six runs, 05:00–05:01 UTC, on this container (Xeon 2.30 GHz × 4, Hardhat 2.28.6), each in a clean
  worktree at its row's code (`git_dirty` false in all six), a fresh node per run, in the declared order. Each run took
  8–12 s. Nothing else ran on the host; I wrote source files in the meantime and ran nothing heavy.
- **C3, result, under the rule in §1a.**
  - Full-refresh `t_chain`: #32 code 7.57 / 7.91 ms (r1 / r2), spread 0.34 ms; #37 code 6.94 / 8.15 ms, spread
    1.21 ms. The means differ by 0.20 ms, within either spread, so the difference between #32 (10.52 ms) and #37
    (14.38 / 10.28 ms) in the register is **attributed to the host**.
  - The rule did not say which spread to use when the two configurations have different ones. In replicate 1 alone the
    codes differ by 0.63 ms, more than the smaller spread. I report that rather than choose the reading that
    passes most cleanly.
  - P*(0.5) at k = 1 / 5 / 25 / ∞: full 5–6 / 23–28 / 65–80 / 127–149; probe 15–17 / 56–58 / 111–121 / 145–149. The
    probe beats the full refresh at every finite k, as in #37.
  - On this host `t_local` is 0.33 ms, so the probe reaches P*(0.5) ≥ 100 at k = 25. #37's host, with `t_local`
    0.49–0.54 ms, did not reach it at any finite k. The knee depends on 0.5 − `t_local`, so it is the most
    host-sensitive figure in both rows.
  - Staleness equals its prediction in 30 of 30 k-rows (revocation and rotation, k = 1, 5, 25).
- **C3, records.** The outputs are in `cv2x-testbed/results/freshness_k_c3/`, with a manifest of order, commits and
  sha256, copied from `runs/c3` as declared. `check_stamps.py` aggregates the six runs (complete stamps, 6 of 6) and
  classes the manifest. Its coverage guard fired on the new files before that, as it should. New row **#52**; #32
  and #37 have a dated note; the result cards have a card for #52; plan C3 is marked done. One slip was caught before
  commit: my note first gave the knee as k ≈ 44–49; the four runs give 40–49.
- **CR, contribution record.** `docs/figures/make_contribution_record.py` and `contribution_template.html` write
  `docs/figures/contribution_record.html`: a contribution calendar (commits per day, fixed bins 1–4, 5–14, 15–29,
  30+), month totals with a table view, milestones (release tags, merged pull requests, report openings), what the
  work produced (eight tiles, each naming its source file), the pre-registered verdicts as they fell, and commits by
  area. Published privately: https://claude.ai/artifact/6kumQ7cg1tHRjiQJy7MmAp.
  - **Scope decisions, each stated on the page.**
    - 9 commits on one branch belong to an unrelated planning project and are left out.
    - The repository's creation commit (`0ab45bb`, 2023-11-07) is counted in the totals but falls before the
      calendar, which starts in November 2025.
    - The identities are reported as git has them: 369 the author's, 23 an AI coding assistant's (the first
      implementation commits of 2025-11-10 among them), 1 the organisation account's.
    - No line counts, because generated result files would dominate them. A commit count measures activity, not
      effort. The December–May gap is shown as it is.
  - **Corrections before publishing.**
    - Three tile labels claimed more than the records show. One said every report had closed with a CI result,
      which the early reports do not have. One gave the Python layers a vaguer name. One called the 99 cells
      "tests across nine standards", when they are 11 adapters × 9 mechanisms, including declared n/a cells.
    - A verdict chip overflowed at phone width.
  - The page depends on the git history, so it is regenerated at each pass's close rather than checked in CI.
- **Records.** Handback §11 and the session manifest (`c4b35ce`). The result cards were republished with card #52.
- **Grand run (last), at `c4b35ce`.** ALL OK: smoke 11 adapters, L1 99, Hardhat 537, Python layers 331, 92 demos /
  1,752 steps (594 mined transactions). The only gas changes are the timestamp-dependent MOBI demo totals (±12 gas),
  as in pass 18. The dashboard, presentation report, result cards and contribution record were regenerated
  afterwards, and all ten document checks pass.
