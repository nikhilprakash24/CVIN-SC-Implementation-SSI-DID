# WP 1.10 — Examiner Pass: Objections and Dispositions

**Produced:** 2026-10-24. The examiner saw only the draft + support files, with no hypothesis from the editor.
**Disposition key:** FIXED (done this pass) · AUTHOR (a framing decision only the author should make) · VERIFY (needs a run or the archive).

## Headline
The examiner's most dangerous chain: concede the predicate is object-attribute ABAC (obj. 2) + the mechanism is already
conceded not-new (§6.8.4) + the freshness evidence is superseded (obj. 7) ⇒ the contribution shrinks to a storage-locus
taxonomy over 2–4 instances, only 2 of which are in the measured ten (obj. 3). **The defensible core — the
locus × encoding × evaluation-point taxonomy and the on-chain ordering-race analysis — is real but smaller than the
draft's framing.** The mechanical slips (obj. 5, 6, 9, 10) are fixed below; the framing FATALs need author decisions.

## FATAL

| # | Objection | Disposition |
|---|---|---|
| 1 | "Minimal set an identity *must* support" is refuted by the author's own matrix (execute/meta-tx have "no analogue" in any identity world) | **AUTHOR.** Recommend: reframe as "the capability surface these substrates expose for comparison," drop "minimal/must support," concede execute+meta-tx as optional (Set C-ish). Editor has softened the wording this pass pending your call. |
| 2 | IDTx novelty collapses into object-attribute ABAC; the ABAC characterization is wrong and the refuting cite (NIST 800-162) is tagged [src] | **AUTHOR + FIX.** The claim "ABAC gates on the caller; IDTx names another identity" is not a safe distinction — 800-162 ABAC evaluates object/resource attributes too. Editor will relocate the novelty explicitly to (a) the locus/encoding taxonomy and (b) the on-chain freshness/ordering analysis, and state plainly the predicate is object-ABAC realized on-chain. Needs your sign-off because it narrows the headline. |
| 3 | "Only 4 of 26 are IDTx" is boundary-sensitive; 2 of the 4 (payToll, MOBI birth) are outside the measured ten; T5 may fail the "names" test | **AUTHOR + FIX.** Editor will report the count over the measured ten (2 `addClaim` paths) and footnote payToll/MOBI as out-of-set exemplars, and drop "that the true IDTx are few is itself a result" unless you want to defend the boundary. |
| 4 | Benchmark gap is a gerrymandered Venn; two conjuncts (IDTx semantics; independent reproduction) are not independent of the contribution | **AUTHOR + FIX.** Editor will (i) restate the gap as a concrete missing capability ("a shared, reusable identity-gating workload with an admission rule") not defined via the coined term, and (ii) apply A5 evenhandedly — concede the thesis's own proposed benchmark also lacks a reproduction at publication. Needs your call on how hard to claim the gap. |

## MAJOR

| # | Objection | Disposition |
|---|---|---|
| 5 | §6.8.2 enumeration lists 5 classes = 25, drops the enabling-view class (T3) → should be 6 classes = 26 | **FIXED** (added enabling-view class, count now 26). |
| 6 | "The twelve functions" heading over an 11-row table (missing relayed/sponsored op) | **FIXED** (reworded; 12th entry added as optional; count tied to the pending G-B archive). |
| 7 | Freshness contribution cites register #32/#37, which ANALYSIS §3 marks superseded by the D51 fix | **VERIFY.** Editor has flagged #32/#37 as pre-D51 and provisional in the draft; the contribution no longer leans on them. A clean re-run under chain-time (A3b) is the real fix — out of Phase 1 scope, logged for the measured study (P5). |
| 8 | "admission = compliance" is false (only ERC-4337 is native 12/12; others have n/a rows) and circular | **AUTHOR + FIX.** Editor will restate admission as "pass-or-justified-n/a" and report native vs pattern vs absent per substrate (data already in G-A). |
| 9 | ZkVinGate "unlinkable across scopes" overclaim — `admit` emits `Admitted(identity,…)` in clear; same anchored commitment every scope | **FIXED** (verified at `ZkVinGate.sol:113`; restated as "per-scope one-time admission with VIN/year/mfr hidden, admitted identity public and linkable across scopes"). |
| 10 | `addClaim` uses raw keccak (`_recoverRawDigest`), no EIP-191/chain-id — contradicts the domain-separation primitive card; cross-chain replay (D52) on a counted IDTx | **FIXED** (verified at `CVINCombinedIdentity.sol`; card 1 no longer claims domain separation for addClaim; raw-digest, contract-bound-not-chain-bound replay exposure flagged as a limitation). |
| 11 | Gap table's ✗ cells are absence-claims drawn from abstracts, violating the doc's own sourcing rule | **AUTHOR + VERIFY.** Editor will mark abstract-only ✗ cells "not determinable from abstract" and show the gap holds on the fully-read subset (Satybaldy26). Reading the rest in full is a Phase 3 task. |
| 12 | "F8" = issueCredential in ANALOGIES but createPresentation in BASIC_ID_SET_EXTENSION; G-B cannot be produced (archive absent) | **AUTHOR/VERIFY.** Needs the `cvin-sandbox-v1.3` archive. Until then the draft refers by name and carries one authoritative name↔set table; F-number cross-refs are suppressed, not guessed. |

## MINOR (editor to absorb; none blocks)
13 capability-based security row — **will add** to ANALOGIES positioning · 14 ERC-4337 duplicate validateUserOp — **already cleared** (false alarm, interface decl + override; see WP 1.4 log) · 15 prototype demonstrates the admissibility predicate only (emit, not effect) — **will state** · 16 numbers without a register row (94.3%, 46 impls, 17-event) — **will cite or drop** · 17 Set C vs execute-in-Set-A — **will state once**.

## What the editor fixed this pass (mechanical, verified-correct)
obj. 5, 6, 9, 10, plus softening of obj. 1/2/3 wording pending author sign-off. Framing FATALs 1–4 and MAJORs 8, 11, 12 are surfaced to the author.

## Second examiner pass (verify-the-fixes) — propagation gaps closed 2026-10-24
A blind re-examination confirmed the framing fixes (obj. 1, 2, 3, 4, 7, 8) were made correctly *in the thesis draft*,
but found three fixes applied only to support files and not back-propagated. All three now closed:
- **obj. 9** — THESIS §3.x.3 still said "unlinkable across scopes"; **corrected** to match the contract and card 7.
- **obj. 10** — THESIS §3.x.3 domain-separation bullet lacked the `addClaim` raw-digest caveat; **added**.
- **obj. 3** — `ANALYSIS.md` §4.2 still said "true IDTx are few … that count is itself a finding"; **superseded** by an inline correction note pointing here.
- **obj. 6** — the "Set A + Set B = twelve" sentence was off by one; **reworded** to defer the count to G-B (no "twelve" asserted).
Second-pass overall verdict: the reframed core (object-attribute ABAC on-chain; novelty = locus taxonomy + ordering/freshness analysis) is defensible once these propagation gaps are closed — which they now are. Remaining open: obj. 11 (read abstract-only gap sources in full — Phase 3), obj. 12 / G-B (archive), and the author's pseudocode review.
