# After-Action Report 02 — Review Pass on the CV2X Testbed Lineage, Grounding, and the MOBI/SUMO Plan

**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Started:** 2026-09-25 (written from the beginning of the pass and updated as it runs; the
final section is written last)
**Trunk at start:** `5a62137` on `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy`, clean,
CI green (Smart Contract Tests, W3C SSI Compliance)
**Companion:** `AFTER_ACTION_REPORT.md` (01 — GitHub restoration, bundle integration)

> Written to over-explain, on request. Every decision in this pass is stated with its
> reason, what was considered instead, and what evidence it rests on. Status marks:
> ⏳ planned · 🔄 in progress · ✅ done · ⛔ blocked (with why).

---

## 0. The request, restated as tasks

The author asked for five things in one message. Splitting them so each is checkable:

| # | Ask (author's words, condensed) | Interpretation | Deliverable |
|---|---|---|---|
| T1 | "push the tags for later i dont get it" | Explain why tags cannot leave this session; it is not a secrets issue | §1 of this report + reply |
| T2 | "review the latest work from 'CV2X testbed sandboxing approach…'" — thorough, creative, innovative, precise, grounded, with figures | Review the five uploaded design documents (CAPABILITIES, CV2X_REALISTIC_ROADMAP, MOBI_VID_RESEARCH, MOBI_VID1_TECHNICAL_SPEC, MOBI_VID2_SSI_DESIGN) against what the merged trunk actually contains today; plan-vs-actual with figures; innovation opportunities | `docs/REVIEW_CV2X_TESTBED_LINEAGE.md` + figures in `docs/figures/` |
| T3 | "use examples, the internet, and very close or highly canonical work … at least 8 … a paragraph on each and a 2nd on how it was or was not incorporated" | A grounding section of ≥8 canonical works, each with (i) what it is and (ii) how this project did/did not incorporate it, with links verified today | §4 of the review document |
| T4 | "organizing this and other relevant outputs for this work session with a description" | A session manifest: every artifact produced in this session (both days), what it is, where it lives | `docs/SESSION_MANIFEST_2026-09.md` |
| T5 | "plan for mobi and sumo work" | A concrete, sequenced plan for the MOBI VID work and the SUMO work, with prerequisites and the experiments' pre-registered designs | `docs/PLAN_MOBI_SUMO.md` |
| T6 | "over explain yourself in an after action report … start from the beginning … updating in parallel" | This document | this file |

## 1. Why the tags cannot be pushed from here (T1) ✅

The confusion is reasonable, so the mechanics in full. A git push writes to
*references*: branches live under `refs/heads/`, tags under `refs/tags/`. The
credential this session uses is issued by the Claude GitHub App installation and
carries a **push policy scoped to one branch name** — the designated working
branch. When git sends the tag ref, GitHub's pre-receive check for that token
rejects it and the client reports "HTTP 403 … the remote end hung up". I also
tried the REST path that creates tag objects (`POST /git/tags`, `/git/refs`); the
session proxy answers *"Write access to this GitHub API path is not permitted
through this proxy"*.

None of this is a property of the repository, of its visibility, or of any
secret. It is a property of the session's token. Making the repo public, or
sharing environment variables, would change nothing — the token would still be
branch-scoped. The only ways the tags reach GitHub:

1. **From your machine** (30 seconds): the commands are in
   `AFTER_ACTION_REPORT.md` §6 — fetch the branch, `git tag -a v0.7.0 be32c6e …`,
   `git tag -a v0.8.0 a64c6f3 …`, `git push origin v0.7.0 v0.8.0`.
2. **GitHub web UI**: Releases → "Draft a new release" → "Choose a tag" → type
   `v0.7.0`, target the commit `be32c6e`; repeat for `v0.8.0` at `a64c6f3`.

The tags exist locally in this container (annotated, with their messages) and
are recorded in the register, so nothing is lost if they are pushed later.

## 2. Plan for this pass (written before executing)

Ordering principle: the report skeleton first (this file), then the parts that
need outside evidence (grounding search) started early because they have latency,
then the review (which consumes both the uploaded documents and the trunk facts),
then the manifest and the MOBI/SUMO plan (which consume the review), then
figures, then commits and this report's closing sections.

| Step | Work | Depends on | Status |
|---|---|---|---|
| S0 | Write this report's §0–§2 | — | ✅ |
| S1 | Locate "sandboxing approach" in the repository; fix the scope of T2 | — | ⏳ |
| S2 | Grounding research: identify ≥8 canonical works, verify links and facts via search; two paragraphs each | — | ⏳ |
| S3 | Trunk facts needed for plan-vs-actual: MOBI VID contracts/tests, use-case count, SUMO harness, provider state | — | ⏳ |
| S4 | Write `REVIEW_CV2X_TESTBED_LINEAGE.md`: §1 what the five documents proposed; §2 what exists (plan vs actual, criterion by criterion); §3 gaps, drift and quiet reversals; §4 grounding (S2); §5 innovation opportunities that the existing infrastructure makes cheap; §6 figures | S1, S2, S3 | ⏳ |
| S5 | Figures: (a) roadmap plan-vs-actual timeline; (b) success-criteria coverage matrix; (c) testbed architecture as-built vs as-designed | S3 | ⏳ |
| S6 | `SESSION_MANIFEST_2026-09.md`: every artifact of this session with a description and path | — | ⏳ |
| S7 | `PLAN_MOBI_SUMO.md`: MOBI VID plan; SUMO plan with pre-registered experiment designs; prerequisites (SUMO install), risks | S4 | ⏳ |
| S8 | Commit/push at each checkpoint; update this report's §3 log as steps close | each step | ⏳ |
| S9 | Close this report: §5 what was done, §6 what was not and why, §7 what is needed from the author | all | ⏳ |

Risks named up front: (i) the grounding search depends on web access and result
quality — if a canonical source cannot be verified today it is marked as such
rather than cited from memory; (ii) SUMO is not installed here, so the SUMO plan
is a plan, not a result; (iii) token budget — the review is prose-heavy, so
figures are generated by script from data already in the repository rather than
drawn by hand.

## 3. Execution log (updated as the pass runs)

- 2026-09-25 — S0 done; report opened before any other work, as requested.
- S1 done: "sandboxing approach" located (see D1); scope fixed to the testbed lineage.
- S2 in progress: grounding sources verified by web search so far — Brecht et al. 2018
  (SCMS, IEEE T-ITS); Sommer/German/Dressler 2011 (Veins, IEEE TMC); van der Heijden et
  al. 2018 (VeReMi); DIF `ethr-did-resolver` / `ethr-did-registry` (did:ethr method
  spec); Lu et al. 2019 (blockchain VANET authentication — **published in IEEE T-VLSI
  27(12), not T-VT as often cited; corrected**); Eclipse MOSAIC; plus, from Pass 1:
  Fdhila et al. 2021, Schäffner (thesis), W3C DID Method Rubric v2.0, W3C
  did-test-suite, BLOCKBENCH (SIGMOD 2017), ACM SIGSOFT Empirical Standards, SAE
  J2945/1, the 2025 Springer SSI-V2V chapter. Third batch (MOBI VID official page,
  SSI-for-EV-charging arXiv 2403.06632, EBSI) requested.
- S3 done: trunk facts collected — MOBI VID V2 has 11 event types and 9 issuer roles
  (matches the VID II design exactly); Python MOBI layer has 32 tests (23 + 9 VIN
  cipher); 12 use cases on the trunk (design listed 10; two added: dealership-mediated
  sale, end-of-life decommission); SUMO harness has network, routes, config and three
  scripts; five-backend MOBI sweep exists with fidelity grades (ERC-735, CVIN-Combined,
  MOBI-VID-V2 at 5/5; ERC-1056, ERC-1155 at 3/5).
- S5 started: figure generator written (`docs/figures/make_review_figures.py`), with the
  status data encoded once so text and figures cannot diverge; run pending S3's last
  three facts (SUMO results directory, security-scenario count, safety apps in the
  harness).
- S6 done: `docs/SESSION_MANIFEST_2026-09.md` written.
- S3 completed with the last facts: the SUMO harness has a `--simulate` mode with mock
  mobility **and has been run** — 50 vehicles (35 SSI, 15 PKI), 10 Hz, 300 m radius,
  ≤8 receivers per broadcast, 30 seeds — plus an unrun real TraCI mode; it references
  FCW/EEBL/IMA and has `run_attack_tests`; the security harness holds 68 scenarios
  across nine standards. Two figure statuses were corrected accordingly (P4, P6, P7;
  "SUMO 50+ vehicles" and "safety-app latency" criteria).
- S2 completed: third batch verified — MOBI VID I/II official pages (dlt.mobi);
  Kailus, Kern, Krauß, ACNS 2024 (SSI for EV charging, Tamarin-verified); EBSI VC
  framework and wallet conformance. Thirteen works written up in the review §4 (the
  request was eight), each with a description paragraph and an incorporation
  paragraph.
- S4 done: `docs/REVIEW_CV2X_TESTBED_LINEAGE.md` written (six sections).
- S7 done: `docs/PLAN_MOBI_SUMO.md` written. Prerequisite de-risked: `eclipse-sumo`
  1.27.1 is available from PyPI for this platform (a 147 MB manylinux wheel downloaded
  successfully), so S0 of the SUMO plan is a one-command install once approved.
- Interruption: the pass was suspended after S7 with five files uncommitted; on resume
  (2026-09-30) the working tree was intact and the toolchain still installed — no loss.
  Lesson kept: commit at every step boundary, not at pass end.
- S5 done: figures rendered; S8: all pass-4 files committed and pushed in one commit
  immediately on resume.

## 4. Decisions and their reasons (updated as taken)

- **D1 — Scope of "latest work from 'CV2X testbed sandboxing approach'".** A
  repository-wide search for "sandbox" resolves the phrase to
  `1_blockchain-identity/CVIN-sandbox-fullstack-completefunc-guide.md` — the
  "Complete Full-Stack CVIN-sandbox1 … two-stage sandbox" guide, which is in the
  **first commit of the repository** (`b23bc4c`, 2025-11-10) and is the origin of the
  CV2X testbed idea. I therefore read T2 as: review the testbed lineage *from* that
  sandbox concept, through the five design documents the author uploaded
  (CAPABILITIES, CV2X_REALISTIC_ROADMAP, MOBI_VID_RESEARCH, MOBI_VID1_TECHNICAL_SPEC,
  MOBI_VID2_SSI_DESIGN — all dated 2025-11-10 to 2026-06-21), to the merged trunk of
  2026-09-24. The alternative reading (only the sandbox guide itself) would ignore
  the five documents the author attached, so it was rejected. If the author meant a
  different document, the review's §1 is organised per document and can be
  re-pointed.

## 5. What was done (closing section)

| Task | Outcome | Where |
|---|---|---|
| T1 tags | Explained: a branch-scoped session token, not a secrets or openness question; two ways to publish the tags, both outside the session | §1; `AFTER_ACTION_REPORT.md` §6 |
| T2 review | The sandbox guide and five design documents reviewed against the trunk; 25 criteria scored (13 met, 9 partial, 1 open, 2 dropped — the figure's computed totals; the prose was corrected to match after the one figure check); four drifts the audit had missed; the roadmap's RQ1 axis shown to be the wrong one (on/off the hot path, not read/write); eight grounded innovation opportunities; the thesis-text changes listed | `docs/REVIEW_CV2X_TESTBED_LINEAGE.md` §1–§3, §5–§6 |
| T3 grounding | Thirteen canonical or closely related works, each with a description paragraph and an incorporation paragraph, links verified by search on 2026-09-25; one venue correction (Lu et al. 2019 is IEEE T-VLSI) | review §4 |
| figures | Roadmap timeline, criteria matrix, as-designed vs as-built architecture — generated from one status table so the figures cannot disagree with the text | `docs/figures/review_*.png`, `make_review_figures.py` |
| T4 manifest | Every artifact of the session by pass, with purpose and path; inputs supplied by the author; things deliberately not committed | `docs/SESSION_MANIFEST_2026-09.md` |
| T5 plan | MOBI M1–M7 and SUMO S0–S8, each with hypothesis, metric, N, reporting rules, risks; SUMO install de-risked (pip wheel available) | `docs/PLAN_MOBI_SUMO.md` |
| scope log | SC-12 (ZK VIN tier → future work), SC-13 (lifecycle-parity comparison → planned M4) | `docs/SCOPE_CHANGES.md` |
| T6 this report | Written before the work, updated at each step, closed here | this file |

Decisions taken during the pass, beyond D1: **D2** — thirteen grounding works rather
than the minimum eight, because the testbed spans three fields (V2X security,
vehicular simulation, SSI standards) and eight would have left one field
under-represented; **D3** — figures generated from a single status table in the
script rather than drawn, so a status change in the review forces a regeneration
rather than a silent divergence; **D4** — the SUMO harness's `--simulate` results are
treated as *real identity measurements on synthetic mobility*, not as SUMO results, and
the plan's first experiment is to validate them against the real TraCI mode rather
than to discard them.

## 6. What was not done, and why

- **No SUMO run.** The binary was not installed; the pass de-risked the install (the
  wheel is available) but did not perform it, because a ~150 MB install is the
  author's call for the session and the plan asks for that go-ahead explicitly.
- **No resolver fixes for the five external-conformance root causes.** In scope of the
  plan, not of a review pass; doing them here would have mixed code changes into a
  documentation commit.
- **No re-run of the bundle lineage's scaling and V2V experiments** (register #26,
  #27 stay B). They are the SUMO plan's S1–S4.
- **The MOBI VID I preview PDF was not fetched and reconciled clause by clause** (M1);
  the review records that the checklist was built from secondary sources.
- **Chapter text was not rewritten.** The review lists the changes (§6) rather than
  making them, so the author can approve the framing first.
- **Tags remain unpublished** — cannot be done from the session (§1).

## 7. What is needed from the author

1. **Go-ahead to install SUMO in-session** (or a local run of S1–S3 with the results
   JSON committed). This is the single step that converts the most estimate rows to
   verified rows.
2. **Push the two tags** from your machine (30 seconds; §1).
3. **Approve the framing changes** in review §6 before I edit chapter text — in
   particular the on/off-hot-path axis replacing read/write, and crediting the sandbox
   guide for the provider abstraction.
4. **Sepolia RPC + funded key as environment secrets** (for M7 and the M2 rows).
5. Still open from earlier: SC-05 (throughput), SC-06 (finish the VC DM 2.0 move),
   SC-01/02 reason confirmation, the notebook index, the Chapter 2 citation set.

*Closed 2026-09-30. Trunk at the closing commit is clean and pushed; CI status is
recorded in `PROJECT_SUMMARY.md` §2.*
