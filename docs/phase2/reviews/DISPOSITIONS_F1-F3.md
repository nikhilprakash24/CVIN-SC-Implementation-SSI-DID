# Dispositions — Academic Review of the Phase 2 Focus Packages F1–F3

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (after-action report 16). **Disposes of:** `ACADEMIC_REVIEW_F1-F3.md` §2 (41 findings: 11 H, 25 M,
5 L). **Rule:** every finding gets a disposition; none is closed by assertion. "Fixed" means changed in the files
named and checked: generated documents regenerated, the stale-figure check clean, the tests and mutants run.

**Outcome:** 40 fixed, 1 fixed in part (AR-13: the plan is fixed, the code fix is deferred to F1-S3); none rejected. The five questions for the author (review §5) are
recorded as decisions with the reviewer's defaults (`../DECISIONS.md`, P2-D8, P2-D10; the scope reconciliation's
D-12 correction).

| ID | Sev | Disposition | Where |
|---|---|---|---|
| AR-1 | H | fixed: "cannot be read directly; only through a carried receipt proof, unmeasured" | F1 README, ANALYSIS §1, §2, §4.4; test 12 title; register #49 dated correction |
| AR-2 | H | fixed: one definition (review §3.3) adopted as P2-D8's default; CAPTURE's working definition marked superseded | F1 ANALYSIS §4.1; README; prototype header; PHASE2_PROGRAMME §5; chat brief |
| AR-3 | H | fixed: inventory re-classified in six classes; `payToll` added; 4 of 26 are IDTx | F1 ANALYSIS §4.2 |
| AR-4 | H | fixed: the predicate is about the named identity, not the caller; documented, with a new test where a third party executes | `IdtxExecutor.sol`; test 2; EXECUTION |
| AR-5 | M | fixed: renamed "registered-commitment validity"; no knowledge claimed | contract header; tests 4–5; ANALYSIS §2, §4.4 |
| AR-6 | M | fixed: commitments record their setter and stop counting when it no longer owns the identity; test 6 and a mutant | `IdentityCommitments`; test 6; `mutate_idtx.sh` |
| AR-7 | M | fixed: three axes; each IDTx placed in exactly one cell | F1 ANALYSIS §4.4 |
| AR-8 | M | fixed: L4 allows dependency on content carried in the transaction | F1 ANALYSIS §2, §5 |
| AR-9 | M | fixed: D51 attached to #32 and #37, not #46 | F1 README, ANALYSIS §3 |
| AR-10 | M | fixed: the re-check closes the gap inside execution, not the ordering race | F1 ANALYSIS §4.4, §4.5; README |
| AR-11 | M | fixed: point predictions with bands per kind; "dominated" defined; control `executePlain` named; compile target and execution fork both recorded | F1 PLAN E-F1-1 |
| AR-12 | M | fixed: correctness half is tests 9–10; measurement half under interval mining | F1 PLAN E-F1-3 |
| AR-13 | M | fixed in the plan: E-F1-4 measures enumeration cost; the D64 fix is designed with a uniqueness mechanism first. The fix itself is **deferred** (F1-S3, WM-2 D1) | F1 PLAN §2 |
| AR-14 | M | fixed: 5 gate mutants committed and run in CI | `phase2/idtx/mutate_idtx.sh`; `.github/workflows/test-contracts.yml` |
| AR-15 | M | fixed: register #51 adds the R3 cells for all columns | register #51; FIGURES F1-2 |
| AR-16 | L | fixed: pointers to scope reconciliation §3.1 | F1 README, ANALYSIS header |
| AR-17 | L | fixed: "MOBI V2 stored event structs and roles" | F1 ANALYSIS §2 |
| AR-18 | H | fixed: gas transfer re-stated with its conditions and a tolerance; dated correction appended under the M2 tag | F2 README, ANALYSIS §2, PLAN E-F2-3; register §1 |
| AR-19 | H | fixed: #33's "equal once cached" FAIL reported as failed; the explanation labelled post hoc; the freshness cost stated | F2 README, ANALYSIS §4; F1 ANALYSIS §3; PHASE2_PROGRAMME |
| AR-20 | M | fixed: labelled a design argument | F2 README, ANALYSIS; PHASE2_PROGRAMME |
| AR-21 | M | fixed: transfer-table rows re-stated with conditions; D52 added | F2 ANALYSIS §2 |
| AR-22 | M | fixed: owner derived from the journal; keyed VIN hash; tests for tail truncation and owner tampering; claims narrowed | `sqlite_lifecycle.py`; tests; F2 EXECUTION, README |
| AR-23 | M | fixed: point predictions with defined measures; the N − 1 window reported | F2 PLAN |
| AR-24 | M | fixed: separate predictions for execution gas and each fee component | F2 PLAN E-F2-4 |
| AR-25 | M | fixed: verdict rules and kill criteria; E-F3-4 relabelled a design step | F2 PLAN, F3 PLAN |
| AR-26 | L | fixed: the run named whenever #33's range is quoted | F2 README, ANALYSIS; F1 ANALYSIS |
| AR-27 | L | fixed: table marked as literature for chapter 2; challenge-period and validium cells corrected | F2 ANALYSIS §3 |
| AR-28 | H | fixed: cross-row span removed; each row with its condition and host | F3 README, ANALYSIS; FIGURES F3-2 table |
| AR-29 | H | fixed: the budget stated per path and host; the scope reconciliation's D-12 withdrawn by a dated correction | F3 README, ANALYSIS; SCOPE_RECONCILIATION corrections |
| AR-30 | H | fixed: "out of cellular coverage, only Mode C"; labelled an argument from the standard | F3 README, ANALYSIS; PHASE2_PROGRAMME |
| AR-31 | M | fixed: the unit defined; writes classified by who signs and pays the outer transaction, reads by who produced the trusted bytes; transport and timing are attributes; the thesis uses the six-cell frame | F3 ANALYSIS |
| AR-32 | M | fixed: detached write defined by t₁ − t₀; ERC-1056 signed operations recognised as detached; the ERC-4337 payer corrected; the F2 anchor marked unbuilt | F3 ANALYSIS, README, EXECUTION |
| AR-33 | M | fixed: E-F3-2 proves storage reads against an independent light client; log resolution scoped out | F3 PLAN |
| AR-34 | M | fixed: cross-tabulation added (178 reads and 238 expected reverts of the 700 flagged steps); the signing class renamed "local computation" | `classify_modes.py`; MODE_CLASSIFICATION §3 |
| AR-35 | M | fixed: the thesis uses the six-cell frame; A/B/C is for P4 | F3 README |
| AR-36 | L | fixed: "between a half and four fifths more", with the payer named | F3 README, ANALYSIS |
| AR-37 | H | fixed: dot plot on a log axis with all six rows, the FAIL marked, both conditions named, the database series labelled as a lower bound | FIGURES F2-1 |
| AR-38 | H | fixed: figure withdrawn; replaced by a table naming each row's unit, condition and host | FIGURES F3-2 |
| AR-39 | M | fixed: excluded totals hatched; the axis labelled as SSTORE opcodes; the code-deposit caveat in the caption | FIGURES F1-1 |
| AR-40 | M | fixed: ERC-725xy replaces ERC-1155 | FIGURES F1-2 |
| AR-41 | M | fixed: all three READMEs and the consolidated document follow the review's §4.1 placements | F1–F3 READMEs; PHASE2_PROGRAMME §3 |

**Deferred, with owners.**
- **AR-13, the D64 fix itself** (the one finding fixed only in part). Plan step F1-S3. The design comes first; then the code under WM-2 D1.
- **The review's literature list (§3.1).** Every entry is recalled, not read. Reading them at source is chat-workspace
  package W1 (`../CHAT_WORKSPACE_BRIEF.md`), then chapter 2.

The second item is not a finding. It is recorded here so that it is not lost.
