# Style and Rigour Guide

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-09, consolidating rules given across the sessions of 2025-11 to 2026-10.
**Binds:** every session, every assistant configuration, every agent working in this repository.
**Sources:** `docs/ORIGINAL_PROMPT_AND_DIRECTION.md` §B (the author's working directives),
`docs/MEASUREMENT_CONDITIONS.md` §2 (reporting rules), `HANDBACK_2026-09-30.md` §7 and
`HANDBACK_2026-10-04.md` §7 (standing rules), and the writing rules used for reports since
2026-10-03. Where this file and a source disagree, the source wins and this file is corrected.

## 1. Rigour

### 1.1 Numbers
1. No number is fabricated, estimated in place of a measurement, or copied from memory.
2. A number enters a chapter only with a claim-register row of status **V**
   (`docs/MEASUREMENT_CONDITIONS.md`). Status letters: V verified, E estimate, S superseded,
   U unverified, B bundle lineage awaiting re-run.
3. Every number travels with its condition tag (M0 in-process, M1 Hardhat local, M1-H harness,
   M1-H/HTTP over HTTP-RPC, M2 public testnet) and its source file.
4. When code changes move a result, the result is re-executed and the old value is kept as a
   superseded row or in a delta file (`gas_moved_by_*.json`). Values are never frozen against
   the code they no longer describe (decision D-E).
5. Two measurements of one quantity that disagree are resolved by re-execution on one tree and
   one host. A number is never chosen.
6. A run of record comes from a clean tree: the code that produced it (contracts, scripts,
   configuration, lockfile) equals the commit it names. A run with `dirty: true` is discarded,
   and the discard is written down. Results files do not count toward the flag.
7. Latency is compared only within a run. Host, library versions and toolchain are recorded
   with every latency figure.
8. Gas is exact `receipt.gasUsed`. Its N is a determinism check, not a confidence interval.

### 1.2 Claims
1. Hypotheses can fail and are reported as they fell. A pre-registered verdict that failed is
   reported as failed; a post-hoc explanation is labelled post-hoc.
2. Claims are as narrow as the evidence. "Compliant" needs the standard's text and a
   clause-level check; otherwise the claim is "inspired by" or "checked against".
3. Threats to validity are designed in, not appended.
4. Every defect found is logged (`docs/DEFECT_LOG.md`) with severity and status. A high-severity
   defect blocks every chapter claim that depends on its path until fixed or narrowed.
5. A fix lands only with a regression test in the layer that owns the path, the affected demos
   green, the grand runner green, and every moved result regenerated or annotated.
6. No test is skipped or weakened. A skip fails the job.

### 1.3 Process
1. Commits are authored by the author, with no AI co-author trailers (academic integrity).
   No model or assistant identifier appears in any repository artifact.
2. Commit and push at every step boundary. The session's push scope is one branch.
3. An after-action report is opened before a pass and closed at its end. It records the plan,
   every step with its gate result, decisions with their alternatives, and what was not done.
4. Never end abruptly: leave a handback that states the verified state, what is pending and
   whose it is, and how to resume.
5. A plan the author asked to audit is written and delivered before execution starts.
6. Nothing from another branch is merged before it is read and its relation to the trunk is
   written down. Unrelated work stays out of the thesis repository.
7. Delegated work is accepted only after the orchestrator's own re-run of its gate. An agent's
   report is evidence of intent, not of result.
8. Ground insight in canonical work and the internet; prefer verified sources to memory. When
   grounding, give each example a paragraph, and a second paragraph on how it was or was not
   incorporated.
9. The project is open source; the session's limits are the only access limits. Credentials
   found in history are still reported for rotation.
10. Figures are generated from committed data by committed scripts.

## 2. Style

### 2.1 Reports and documents
1. Lead with the answer or outcome. If something could not be verified, say so first.
2. One idea per sentence. A sentence beats a label with a colon.
3. Prefer short paragraphs and tables over long prose. Use a table for parallel facts with
   several attributes, a list for parallel items, prose for an argument.
4. State facts and conclusions; name the file, commit or register row that carries each.
5. Over-explain in after-action reports: the reader is an examiner or a future session that did
   not watch the work.
6. Expand uncommon acronyms on first use in each document.
7. Mark the author's decisions clearly as the author's, with the default that was taken and the
   right to overturn it.
8. Every document says who wrote it, when, what it supersedes and what binds it.

### 2.2 Messages to the author
1. Lead with the outcome. Short sentences with verbs. No em-dashes, no parentheticals,
   no arrows.
2. Keep code, file names and numbers out of prose where possible; put measurements in a short
   table and commands in a code block.
3. No headers in a message under about 500 words.
4. End when the content ends; no closing offer.

## 3. Checklist before a pass is closed
- [ ] Every number cited in a changed document has a register row of status V.
- [ ] Every result moved by the pass is regenerated or annotated.
- [ ] Hardhat suite, both Python bodies and the grand runner pass; CI is green on the last commit.
- [ ] The after-action report is closed, the handback has an addendum, the session manifest lists
      the outputs.
- [ ] Open decisions are listed with their defaults.
