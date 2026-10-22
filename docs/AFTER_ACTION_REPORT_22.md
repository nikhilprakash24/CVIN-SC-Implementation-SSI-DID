# After-Action Report 22 — Layer-5 Prose, Chapter 2, and WM-2 Resumed (Plan 4)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened and closed:** 2026-10-22. **Brief (the author):** after PR #4, do all three: the layer-5 chapter prose,
chapter 2, and the WM-2 steps. **Plan:** `docs/zkp/PLAN_4_PROSE_AND_WM2.md`, written before execution.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`.

## 1. Track P — layer-5 prose (first draft)
§3.9 pre-registration (Z-E1..Z-E7, A1, A2, conditions), §4.8 the ZK-VIN tier and the Steward, §5.10 RQ5 results
(H6 partly supported), §6.8 on-chain reality, SSI as a spectrum and the agent wrapper, chapter 7 additions to 7.2,
7.3, 7.5, 7.6 and a new §7.8 on the closed loop (≈6,100 words). Every addition is marked with its date; no drafted
text was changed. Numbers cite register #55–#61 (or #27); extrapolations and hand times are labelled E. Left out
because no register row carries them: the learning-curve values, the powers-of-tau size, test counts, the cited
GPU rate, the `set_service` gas and the salt width. Plan 2's W-4 refines this text.

## 2. Track L — chapter 2
Drafted (≈5,100 words, §2.1–§2.7) from registered sources: 85 citations to `docs/zkp/SOURCES_ZKP.md` and standards
in `SOURCES.md` §1–§3, plus **32 academic papers newly added** in `SOURCES.md` §7, each confirmed against its Crossref
DOI record (title, authors, year, venue); two spot-checked again at the close. Publisher landing pages were not
opened. **Six `[SOURCE NEEDED]` markers** remain (no multi-standard benchmark exists; MOBI VID I/II documents;
academic MOBI evaluations; the SAE J2735 edition; no prior SSI-vs-PKI same-path timing; a measured credential
custodian). The researcher's own reference set may extend or replace the sources.

## 3. Track W — WM-2
| Step | Outcome |
|---|---|
| C3 | done by the clone lineage (#54, same host, both modes); crux C4's claim rewritten from it; its stale D51 gap replaced (D51 fixed in C0; residual D63) |
| C1 | done with a gap: the resolver reads chain state (H-R); external suite on-chain 311/311 (#24); the executable checker (#4) still scores offline documents (crux C5 gap updated) |
| C2 | done with an author decision: H-A on the merged contract (#28); D54 (organisational roles) open |
| A6 | largely done by the merge re-runs (harness `2026-10-21T03-28-59Z_a9e2a28`; #39 HTTP-RPC `2026-10-21T09-02-58Z_bd55af2`); the one-line `dirtyMeasured` switch remains |
| A3 | done with a gap: the W3C checker, gas-stats driver and security-matrix producer stamp their runs; re-run on clean code: #4 94.3 % unchanged, every matrix verdict unchanged, gas 30/30 identical; the scenario matrix promoted through A4; `sensitivity.json` has no producer in the tree |

## 4. Findings and departures
- **A helper placed between a decorator and its class.** The first stamp edit to the W3C checker inserted a function
  between `@dataclass` and `ComplianceCheck`, which broke the checker; it was pushed (`68ccb9b`) before being run.
  Fixed in `db19ff2` within minutes. Lesson: run a producer once before pushing an edit to it.
- **An amended commit orphaned a running stamp.** A commit was amended (committer identity, at a repository hook's
  request; the author stays Nikhil Prakash) while its producers were running; the runs were stopped and repeated on
  the new commit.
- **The gas-stats driver again rewrote `gas_benchmark.json`;** restored from HEAD (the known gotcha).

## 5. Next and the author's decisions
- **Next executable (WM-2):** A3b — 15 result families are flagged "code changed since" in
  `docs/testing/STAMP_INVENTORY.md` (#21, #26, #27, #32, #37, #38, #47 and the infrastructure rows); each re-run
  restates its register row with the old value as history.
- **Author:** D54; C1's checker switch (and the raw-VIN did:mobi placeholder, handback item 16); the six chapter-2
  source gaps; RQ5/H6 placement defaults.
