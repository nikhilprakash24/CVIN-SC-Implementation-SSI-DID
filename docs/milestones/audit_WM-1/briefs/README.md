# Audit briefs for WM-1 (frozen checkout `d61a284`) - index

Written by the brief-writer, not by the orchestrator whose work is audited. Each brief is self-contained
(common context, 19-22 numbered checks, allowed commands, mandatory output format). Auditors work in parallel,
read-only on the frozen checkout, writing only to `audit_scratch/brief-<n>/`.

| Brief | Title | Why it is a separate brief |
|---|---|---|
| 1 | Claims, numbers and thesis chapters versus the register and the committed data | Where a wrong number or overclaim would sit: register rows #44-#48 and the rows WM-1 edited, recomputation of I1-I5 from per-run JSON, crux register, dashboard, chapters 1/4/5/6/7 (never reviewed), stale figures outside the Markdown-only checker, and the report's own arithmetic. |
| 2 | Code and security of what WM-1 built | The infrastructure verifier is the new security-relevant code and was reviewed once, by reviewers briefed by its author. Briefed for PoC attacks the 13-check set omits (conditional field binding, issuer-key binding, replay-cache poisoning, clocks), for an independent mutation set (the orchestrator's 26 mutants are not committed), for the "flags off changes nothing" gate, timed-region changes under the #27 result, `code_clean` scope, secrets, trace content. |
| 3 | Tooling, CI and reproducibility from a clean checkout | WM-1's main product is guards (generators, `--check` modes, stamps, probe, stale-figure checker, grand runner). The report admits several were never mutation-tested. This brief tests whether each guard can fail, whether "CI-checked / byte-identical / ALL OK" is true from a fresh clone, CI history per commit, clean installs, and the commit a generated number really belongs to. |
| 4 | Process and documents: report, plans, reports, logs | The milestone report was written before the audit and is itself in scope. Checks existence of everything cited, closing conditions, plan-status recount, ID cross-references, timeline vs git, findings-register dispositions, defect-log completeness, "what went wrong" completeness, decision attribution (author vs default), independence and disclosure facts, scope and deferred-item bookkeeping. |
| 5 | The code nobody has audited: Python suites outside L3, the contracts, and the tests that certify them | The known gap of the previous review. WM-1's "ALL OK", 536/291 tests, 94.3 % W3C score, 43/43 attacks, 335/336 external suite and the fixed-defect list all rest on this code; it also holds the infrastructure verifier's trust root (VC layer) and the I4 target contract. Checks test power (mutants, regression tests failing on old code, strict vs lenient reverts, checker self-reference), the external-suite object, contract access control, deployability, gas definitions, baseline fairness, crypto misuse. |

## How the scope was split, and why

- Suggested split kept (claims / code / tooling / process / at-risk) because the failure modes differ: wrong
  numbers (1), wrong behaviour (2), guards that cannot fail or results that cannot be regenerated (3),
  false statements about what was done (4), certifications resting on code no one has read (5).
- Brief 5 takes the "most at risk" slot and is the largest: WM-1's own adversarial review explicitly excluded the
  Python suites outside L3, the contracts and the chapters (open item N-22). Because the contracts were
  not changed in WM-1 (to be verified, Brief 4 C-checks and Brief 1 C18), their audit is justified not by
  the diff but by dependence: every register security and conformance row cites them.
- Chapters 1, 4, 6, 7 (and the statement-of-what-was-done parts of 2 and 3) are in Brief 1, not a separate
  chapter brief, because the question is the same as for the register: does each number/verification
  statement have a V row and the right value. Chapter 4 is also compared with the code (Brief 1 C15).
- Overlaps are deliberate where one auditor's blind spot is another's focus: run-identity flags (2 C14, 3 C15),
  CI history (3 C12, 4 C2), commit-to-number mapping (1 C8/C21, 3 C6/C11, 4 C5), the 94.3 % score and 335/336
  (1 C14, 5 C4/C5), secrets (2 C16, 4 C11 for the disclosure question).
- Facts already spotted while writing the briefs (leads, not findings; auditors must verify): the report and plan
  refer to a consolidated `HANDBACK_2026-10-10.md` that does not exist in the checkout; the plan says P3.2 is
  carried to "B4" while PLAN_WM-2 has it as A5; the grand report is generated at `601e1de` but cited as
  `291bbca`; "26 of 26 mutants killed" has no committed mutant set; `_binding_ok` skips the station check when a
  message has no `rsu` key; the warm-path expiry uses `time.time()` rather than the injected clock; the plan-status
  counts (25 items, 18 done) do not obviously match the table rows; the audit-section of the report and AAR 12
  §3-§6 are empty at `d61a284`; presentation documents promised in AAR 12 do not exist; CI history shows only
  closing commits in the report.

## Deliberately left out

- Re-running any long experiment (I1-I3 30-run sweeps, V2V stats, scaling, `npm run metrics`): recomputation from
  committed JSON only. Consequence: a wrong measurement that is internally consistent in JSON would not be found;
  only its recomputation, provenance and stamping are audited.
- Thesis chapter 2 (literature review) correctness and citations, and the accuracy of bibliographic claims;
  chapter 3 only where it states procedures the experiments should follow.
- The upstream standards' content beyond the cited statements (SAE/IEEE/ETSI/NTCIP text itself; auditors may
  note an obviously wrong attribution only).
- `docs/prior-survey/` (imported onboarding material) except for secrets; vendored upstream code; the
  `_research-copies` beyond divergence checks; `docs/review02/` and AAR 01-07 beyond what WM-1 cites.
- Real SUMO/TraCI behaviour (not installed; deferred as SC-22), Sepolia / M2 results (not run), radio/channel realism.
- The presentation report (not yet written), slide decks, the published artifact versions v3-v5 (only the repo's
  HTML page is checked, not the hosted copy).
- Formal verification, gas-optimality of contracts, UX/style of documents, naming preferences.
- Independent judgement of the thesis' research questions or hypotheses; only whether the evidence supports the
  wording.
