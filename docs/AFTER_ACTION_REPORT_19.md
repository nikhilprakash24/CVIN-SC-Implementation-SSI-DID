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
