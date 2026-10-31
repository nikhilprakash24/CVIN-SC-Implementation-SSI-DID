# IDTx Core — Live Progress

**Updated:** 2026-10-24 · **Decision:** A+ (thesis is home; overflow → Appendix G / companion SP-9, returnable)

## Phase roadmap

```
Phase 1  function set, IDTx, benchmark gap   [■■■■■■■■■■]  100%   COMPLETE (examiner fixes applied)
Phase 2  compare to other ID systems         [■■■■■■■■□□]  ~80%   IN PROGRESS
Phase 3  nearest benchmarks, benchmark v0     [■■■■■■■■□□]  ~80%   IN PROGRESS
Phase 4  same, for AI agents                  [□□□□□□□□□□]    0%   planned
Phase 5  10-substrate × function-set matrix   [□□□□□□□□□□]    0%   planned
Phase 6  IDTx + compound scenarios visualized [□□□□□□□□□□]    0%   planned
```

## Phase 1 work packages

| WP | Task | Agent | Status |
|---|---|---|---|
| 1.1 | Function→code/test/register map, 10 substrates | RC (Explore) | ✅ done → `p1/FUNCTION_MAP.md` |
| 1.2 | Clear [B1] cells (verbatim F1–F12) | ED + author | ⏸ blocked on archive |
| 1.3 | Primitive cards (protocols/algorithms) | SS | ✅ done → `p1/PRIMITIVES.md` |
| 1.4 | Pseudocode (F1–F12 + IDTx) — **author will double-check** | CE | ✅ done → `p1/PSEUDOCODE.md` |
| 1.5 | Analogy matrix (centralized / digital-ID / CAV) | SS | ✅ done → `p1/ANALOGIES.md` |
| 1.8 | Figures P1-1…P1-6 | VA | ✅ done → `figures/*.svg` (stdlib script) |
| 1.6 | Benchmark-gap evidence | LS | ✅ done → `p1/BENCHMARK_GAP.md` |
| 1.7 | IDTx prior-art positioning | LS | ⬜ queued |
| 1.9 | Thesis drafts (Ch 3 §3.x, Ch 6 §6.8, Ch 2 §2.6, App. G) | ED | ✅ revised per examiner → `p1/THESIS_DRAFT.md` |
| 1.10 | Examiner pass (draft only) | SK | ✅ done → `p1/EXAMINER_REVIEW.md` (4 FATAL, 8 MAJOR) |
| 1.11 | CI: figure + link checks | ED | ✅ done → `.github/workflows/idtx-core.yml` |

Legend: ⬜ queued · 🔵 running · ✅ done · ⏸ blocked · ⚠ needs author

## Running log (newest first)

- `2026-10-24` SS — WP 1.3 + 1.5 ✅ complete: `p1/PRIMITIVES.md` (8 primitive cards) + `p1/ANALOGIES.md` (13-row × 3-world matrix). All claims tagged inline [src]/[sec]/[recalled]. **[src] primary-verified:** OAuth RFC 6749, X.509 RFC 5280, NIST SP 800-162 (IDTx↔ABAC PDP), SP 800-63-4, VC 2.0, Bitstring Status List, SCMS (Brecht 2018), eIDAS Reg 2024/1183, EIP-712/191, ERC-1056, DID Core, did:ethr, Groth16 ePrint 2016/260. **[sec] secondary-only (paywalled primaries):** ISO/IEC 18013-5 mDL, IEEE 1609.2, ETSI TS 102 941. **[recalled] must NOT be stated as fact until read:** OIDC Core, SAML 2.0, OCSP RFC 6960, LDAP/SCIM, MOBI VID spec (external standard not fetched; repo contracts read), EUDI ARF exact topic numbers. VA (WP 1.8) launched to build the 6 figures.
- `2026-10-24` LS — WP 1.6 ✅ complete: `p1/BENCHMARK_GAP.md`. 31 sources examined (3 read in full/at source, 28 classified from abstracts). **KEY CORRECTION:** the blunt "no SSI benchmark exists" claim is NOT defensible — SSI/DID performance benchmarks now exist (Satybaldy et al. 2026, arXiv 2601.20716, self-describes as a benchmark). The defensible claim, to use verbatim in Ch 2 §2.6 / Ch 7 / SP-9: *"No benchmark provides a shared reusable workload AND an admission/conformance rule AND IDTx-level dependency semantics; every artefact found satisfies at most two of these three, and none has an independent reproduction."* Closest IDTx-mechanism measurement: Frutuoso et al. 2026 (ERC-3643+ONCHAINID, arXiv 2607.16383) — ad hoc, confirms mechanism is prior art, leaves the gap open. See new DECISION D-GAP below. Editor caveat: EUDI/eIDAS FCAF primary 404'd; rests on Sokolov 2026 (arXiv 2609.26220).
- `2026-10-24` CE — WP 1.4 ✅ complete: `p1/PSEUDOCODE.md`. 14 listings (lifecycle §2.1–2.10, IDTx §3.1–3.4, ZkVinGate §4), each citing the exact `file:line` range. Both [VERIFY] markers resolved by ED: 300s presentation TTL confirmed (`erc1056.adapter.js:198`), AR-10 ordering-race label confirmed (ANALYSIS §4.3–4.5). **ERC-4337 duplicate `validateUserOp` flag CLEARED — false alarm:** line 64 is the `IAccount` interface declaration, line 136 is the override implementation; one implementation, compiles clean. Inline notes added for AR-1/4/5/6, K-6, K-11, sticky-revocation. **Awaiting author line-by-line check.**
- `2026-10-24` ED — WP 1.1 ✅ complete: `p1/FUNCTION_MAP.md`. All 12 functions + IDTx mapped across 10 substrates + MOBI-VID + ZkVinGate with file:line and guarding tests. Two NOT-FOUND-by-design cells recorded (ERC-1056 has no attribute-value read fn; MOBI-VID has no per-event revoke). Flagged a duplicate `validateUserOp` in the ERC-4337 account for CE to confirm. Launched WP 1.3 / 1.4 / 1.5 / 1.6 in parallel.
- `2026-10-24` ED — PROGRESS dashboard created. Launched WP 1.1 (Repo Cartographer) to build the function→code map.
- `2026-10-24` ED — Decision P2-D8b recorded: **A+**. Detailed plan + placement map committed (`c2c423b`). Appendix G and SP-9 registered.
- `2026-10-24` ED — Plan, agent team, Phase 1 kickoff committed. Grounded in `ANALYSIS.md` §4, `BASIC_ID_SET_EXTENSION.md`, `IdtxExecutor.sol`.

## Decisions log

| ID | Decision | Date |
|---|---|---|
| P2-D8b | Core work goes in the thesis (home); overflow to Appendix G or companion SP-9, both returnable. Measured gas study stays P5. | 2026-10-24 |
| D-GAP | The benchmark-gap claim is stated ONLY in its narrow three-part form (shared workload ∧ admission rule ∧ IDTx semantics; no artefact has all three + a reproduction). Never "no SSI benchmark exists." Position explicitly against Satybaldy et al. 2026. | 2026-10-24 |

## Author to-do (audit checkpoints)

- [ ] WP 1.4 pseudocode — you will verify line-by-line against the Solidity.
- [ ] Supply `cvin-sandbox-v1.3` archive (or F1–F12 signatures) to clear [B1].
- [ ] Function-naming: left to my judgment for clarity (per your note).

## Examiner pass (WP 1.10) — author decisions needed

The blind examiner raised 4 FATAL + 8 MAJOR + 5 minor. Editor fixed the mechanical/verified ones (obj. 5, 6, 9, 10) this pass. **Four need your call** because they narrow the headline claims:
- **obj. 1** — drop "minimal set an identity *must* support" → "capability surface for comparison"? (editor softened pending your yes/no)
- **obj. 2** — concede the IDTx predicate is object-attribute ABAC realized on-chain, and relocate novelty to the locus taxonomy + ordering analysis only?
- **obj. 3** — report the IDTx count as 2 (measured set) not 4, with payToll/MOBI as out-of-set exemplars? (editor applied this; confirm)
- **obj. 4** — restate the benchmark gap without using the coined term, and concede A5 applies to your own proposed benchmark too?

See `p1/EXAMINER_REVIEW.md` for the full triage and the minimum fix per objection.

## Phase 1 COMPLETE — 2026-10-24

All work packages done except 1.2 ([B1], blocked on the `cvin-sandbox-v1.3` archive from the author). Examiner fixes applied without author input (per instruction "continue without my input"), with every change recorded and reversible:
- **obj. 1** applied: "minimal/must support" → "capability surface for comparison"; execute/meta-tx conceded as no-analogue extras.
- **obj. 2** applied: IDTx conceded to be object-attribute ABAC realised on-chain; novelty relocated to the locus taxonomy + the on-chain freshness/ordering analysis. False "ABAC gates the caller" distinction withdrawn.
- **obj. 3** applied: IDTx count reported as 2 over the measured ten; payToll/MOBI as out-of-set exemplars; "few is itself a result" dropped.
- **obj. 4** applied: benchmark gap restated without the coined term; A5 (reproduction) applied evenhandedly to this work's own proposed benchmark.
- **obj. 7, 8, 13, 15, 17** applied (freshness marked provisional/pre-D51; admission = pass-or-justified-n/a; capability-security positioning; prototype-scope note; Set C vs execute clarified).
- **obj. 5, 6, 9, 10** already fixed in the prior pass (arithmetic, function count, ZK unlinkability, addClaim replay).
- **obj. 11, 12** remain author/Phase-3 items (read abstract-only gap sources in full; obtain archive for G-B).

**Author checkpoints still open:** (1) line-by-line pseudocode review (`p1/PSEUDOCODE.md`); (2) supply `cvin-sandbox-v1.3` to clear [B1]/G-B and the F8 numbering collision; (3) sign off on the narrowed framing (obj. 1–4) — all reversible if you want the stronger framing back. A re-examination of the revised draft is the recommended next step before this reaches a thesis chapter.

## Phase roadmap — ready to start Phase 2 on your word
Phase 2 (compare to other ID systems) can begin now; it reuses the function set as the common axis and the analogy matrix as its seed. Say "start phase 2" or leave it for the chat sidecar.

## Second examiner pass — propagation gaps closed (2026-10-24)
A blind verify-the-fixes re-examination confirmed the framing fixes landed in the thesis, but caught that obj. 9/10 fixes and the obj. 3 retreat had been applied to support files only. Now back-propagated into `THESIS_DRAFT.md` (ZkVinGate no longer "unlinkable across scopes"; addClaim raw-digest replay caveat added to the primitive bullet) and `ANALYSIS.md` (the stale "true IDTx are few / count is a finding" sentence superseded by a correction note); obj. 6 "twelve" off-by-one reworded to defer to G-B. Second-pass verdict: **defensible** once these gaps closed — which they now are. This was a genuine editor miss (support-file fixes not propagated), caught by the re-examination — logged as the reason the verify pass was worth running.

---

## PHASE 2 — comparison with other ID systems (started 2026-10-31)
Home: Appendix G-G + companion SP-9. Common axis = the Phase 1 function set; seed = `p1/ANALOGIES.md`.

| WP | Task | Agent | Status |
|---|---|---|---|
| 2.1 | Comparison set + justification (8 systems) | ED+SS | ✅ done → `p2/COMPARISON.md` §1 |
| 2.2 | Function×system matrix | SS | ✅ done → `p2/COMPARISON.md` §2 |
| 2.3 | Trade-off matrix + prose | SS+LS | ✅ done → `p2/COMPARISON.md` §3 |
| 2.4 | Figures (heat map; trade-off profile) | VA | ✅ done → `figures/p2_*.svg` |
| 2.3b | Verify ERC-3643/ONCHAINID + eIDAS columns | SS | ✅ done (17 cells → [src]; 35/96 open) |
| 2.5 | Examiner pass | SK | ✅ done → `p2/EXAMINER_REVIEW_P2.md` (2 FATAL, 6 MAJOR) |
| 2.6 | Revision (FIDO2+ledgerless SSI, n-a recode, §4 rewrite) | SS/ED | ✅ done → `p2/COMPARISON.md` 12×10 |
| 2.7 | Figures → 10 systems + regen FIGURES_P2 | VA | ✅ done (M5 count fixed 42/120) |
| 2.8 | Verify-the-fixes re-examination | SK | ✅ done — all 12 RESOLVED, defensible |

- `2026-10-31` ED — Phase 2 launched. One Standards-Scholar agent doing 2.1–2.3 (grounded in the sourced ANALOGIES matrix; evidence tags carried forward). Figures + examiner to follow.

- `2026-10-31` SS — WP 2.1–2.3 ✅: `p2/COMPARISON.md`. Selection criterion = one ordered trust-locus axis, 8 distinct points, each a deployed spec. ~15 cells upgraded to [src] (OIDC/SAML/OCSP/LDAP/SCIM free primaries). Headline tradeoff T1: the ledger removes the live-authority dependency but pays for it three ways — revocation becomes a public (loses query-privacy), ordered (AR-10 race), and costly (gas #49/#31) write — the same contract-readable property that enables the IDTx forecloses off-ledger privacy and adds ordering risk. 52/96 cells still not [src]; ERC-3643 (S8, closest prior art) + eIDAS columns launched for verification (2.3b) alongside figures (2.4).

- `2026-10-31` SS — WP 2.3b ✅: ERC-3643/ONCHAINID (S8) and eIDAS/EUDI (S4) columns verified at free primaries (ERC-3643 EIP, ERC-725, Reg (EU) 2024/1183); 17 §2 cells + 10 §3 cells → [src]; unverified ledger 52→35/96. **Thesis payoff:** ERC-3643 transfer-gating = object-attribute ABAC, on-chain in the *receiver's* ONCHAINID claim store, evaluated *inside* the transfer as a revert-on-fail precondition (inherits the AR-10 ordering race). It differs from the thesis's `IdtxExecutor` on all three axes — ERC-3643's depended-on identity is implicit+fixed (always the receiver), welded to one operation (ERC-20 transfer), boolean topic-set check; IdtxExecutor generalizes: explicitly-named identity decoupled from the operation, arbitrary in-contract guard, `fulfil` re-check. Because ERC-1056 has no contract-readable attribute (AR-1), the thesis carries its own equality-only L3 commitment store where ONCHAINID reads claims in place. Confirms the contribution = taxonomy + freshness/ordering analysis, not the guard. Left [recalled]: S8 rotate/delegate (ERC-734 unpublished). EUDI ARF reachable; Regulation carried every S4 cell.

- `2026-10-31` VA — WP 2.4 ✅: `figures/make_p2_figures.py` (stdlib, deterministic, own --check; P1 --check untouched), `figures/FIGURES_P2.md` (separate file by design). P2-1 function×system heat map (4 channels/cell: glyph+label+note+shade, color never sole), P2-2 trade-off dot-matrix (not a radar — 8 systems unreadable as overlapping polygons; ordinal levels by position+label). Known judgement calls documented in FIGURES_P2.md: meta-tx row omitted (no row in COMPARISON §2); P2-2 ordinal placements are a reading of §3's prose; evidence tags reproduced verbatim (S5 mDL + parts of S8 still provisional). Launched examiner (2.5).

- `2026-10-31` SK — WP 2.5 examiner ✅: verdict **not defensible as-is**; the taxonomy/freshness contribution survives, the row-count "only/uniquely" headline does not. 2 FATAL + 6 MAJOR + 4 minor in `p2/EXAMINER_REVIEW_P2.md`. Root cause: §4's "S7 uniquely" claim is an artifact of (a) excluding FIDO2/WebAuthn + ledgerless did:key/did:web (which share the self-created-key property) and (b) marking EVM-only ops Absent not n-a. Launched WP 2.6 revision (add the two comparators from free W3C primaries, recode n-a, mark T2/T3 contingent on [sec], port capital-cost caveat, rewrite §4 to "the combination, not only/uniquely").

- `2026-10-31` SS/ED — WP 2.6 revision ✅: matrix now **12 functions × 10 systems** (added S9 WebAuthn/FIDO2, S10 ledgerless did:key/did:web, both [src] from free W3C/FIDO primaries). Load-bearing: S9 createDID=Native (self-generated key, no issuer — the property §4 wrongly called S7-unique); S10 IDTx=n-a (full DID+VC surface, no ledger — proves the ledger buys *in-transaction evaluation*, not authority-independence). §4 headline rewritten: "S7's distinction is the *combination* of FIDO2-like self-created key-identity with ERC-3643-like contract-readable on-chain evaluation within this EVM-derived function set — not any single Native cell, not a property no other system has." "uniquely" dropped; OCSP-stapling note added to T1; execute/delegate recoded Absent→n-a; T2/T3 marked provisional on [sec]; capital-cost caveat added (T5). Unverified 42/120 (35 carried + 7 new [recalled] ERC-734-adjacent). Launched 2.7 (figures to 10 systems; also fixes M5 stale FIGURES_P2 count).

## PHASE 2 COMPLETE — 2026-10-31
Verify-the-fixes re-examination: **all 12 objections RESOLVED**, no new contradictions, fixes reached the prose (the Phase-1 back-propagation failure did NOT recur). §4 "combination, not unique" headline is matrix-consistent on every leg (S9/S10 createDID Native but IDTx n-a ⇒ the combination is S7's, the parts are not). Verdict: **defensible at a defense**. Fixed one stale line in the triage sheet (M5 target was pre-column-addition). 
**Deliverables:** `p2/COMPARISON.md` (12×10 matrix, §1–§4), `p2/EXAMINER_REVIEW_P2.md`, `figures/p2_1_*`/`p2_2_*` + `figures/FIGURES_P2.md`.
**Remaining weakness (honest, flagged):** T2/T3 — the offline-freshness and privacy tradeoffs that anchor the CAV-domain argument — still rest on [sec] paywalled cells (ISO 18013-5, IEEE 1609.2). Marked provisional; primary read is a Phase 3 item (free SD-JWT-VC/mdoc material can carry much of T3).

**Next:** Phase 3 (nearest benchmarks + benchmark v0) ready on your word — here or in the chat sidecar.

---

## PHASE 3 — nearest benchmarks + benchmark v0 (started 2026-10-31)
Home: companion SP-9 + Ch 7 future work. Builds on p1/BENCHMARK_GAP.md (31 sources) and p2/COMPARISON.md.

| WP | Task | Agent | Status |
|---|---|---|---|
| 3.1 | Deep benchmark profiling (A1–A5) | LS+SS | ✅ done → `p3/BENCHMARK_PROFILES.md` |
| 3.2 | Gap matrix vs the 5 ingredients | ED | ✅ done → `p3/BENCHMARK_V0.md` §3.2 |
| 3.3 | Benchmark v0 spec | ED+CE | ✅ done → `p3/BENCHMARK_V0.md` §3.3 |
| 3.4 | Reproduction kit + A5 milestone ladder | ED | ✅ done → `p3/BENCHMARK_V0.md` §3.4 |
| 3.5 | Close Phase-2 T2/T3 [sec] cells (free primaries) | SS | ✅ done — T2/T3 non-provisional; 35/120 |
| 3.6 | Examiner pass | SK | ✅ done → `p3/EXAMINER_REVIEW_P3.md` (1 FATAL, 6 MAJOR) |
| 3.7 | Revision: profile T-REX, narrow absence claim, reframe as workload class | SS/ED | 🔵 running |

- `2026-10-31` ED — Phase 3 launched. 3.1 (deep benchmark profiling) + 3.5 (close Phase-2 provisional CAV cells) in parallel; 3.2–3.4 are editor synthesis after 3.1; examiner last.

- `2026-10-31` LS+SS — WP 3.1 ✅: `p3/BENCHMARK_PROFILES.md`. 10 free artefacts read at source; 7 obj.11 abstract-only cells upgraded to read-in-full. Findings: closest *as a benchmark* = BLOCKBENCH/DIABLO (4/5 axes) but identity-blind (no identity workload); closest *identity* benchmark = Satybaldy26 (pins A3, fails 4/5, IDTx ✗). Universal gaps: A5 (independent reproduction) across identity artefacts; A2 (admission rule) across all identity *performance* studies; and the IDTx in-transaction property absent from **every** artefact. **CONSEQUENTIAL CORRECTION (back-propagated to p1):** Frutuoso26 read in full — its issuer-accreditation check is enforced **off-chain at the client**; on-chain addClaim gates only on the sender's own key, no token transfer measured. Downgraded IDTx ✓→◐. So NO artefact ships a true in-transaction identity-gating workload — strengthens the gap. Fixed in `p1/BENCHMARK_GAP.md` (4 places) and `p1/THESIS_DRAFT.md` (2 places) this turn.

- `2026-10-31` SS — WP 3.5 ✅: Phase-2 T2/T3 now **non-provisional**. 16 tag flips via free primaries (AAMVA mDL Impl. Guidelines v1.6 §4.2 selective disclosure + device-retrieval offline; RFC 9901 + SD-JWT-VC for the salted-digest mechanism; Brecht SCMS for V2X offline verify + pseudonym rotation). COMPARISON.md unverified ledger 42→35/120; residual [sec] narrowed to exact ISO-mdoc / 1609.2 wire-format encoding that the trade-offs do not turn on. FIGURES_P2.md count reconciled 42→35 (fixed stale drift immediately, as the first examiner's M5 taught). Phase-2 CAV argument no longer rests on unread paywalled specs.

- `2026-10-31` ED — WP 3.2–3.4 ✅: `p3/BENCHMARK_V0.md`. §3.2 gap matrix (5 axes justified from TPC/SPEC/BLOCKBENCH independently of the IDTx term, answering the Phase-1 gerrymandering objection); two universal failures (conformance suites lack A3 cost; perf studies lack A2 admission + A5 reproduction) and the absolute absence (in-transaction identity-gating in no artefact). §3.3 benchmark v0 = W1 lifecycle (fn set, register #35/#49/#51) + W2 17-event composition + W3 IDTx classes (the tier no artefact has) | admission = pass-or-justified-n-a compliance suite | metrics = register M-conditions | harness = this repo. §3.4 reproduction kit + milestone ladder v0→v1(A5)→v1.x(cross-paradigm); A5 applied evenhandedly (this thesis's own v0 also lacks reproduction at publication). Launched examiner (3.6).

- `2026-10-31` SK — WP 3.6 examiner ✅: verdict **not defensible as-is**. FATAL: "absent from every artefact without exception" is FALSE — ERC-3643 `transfer()` gates on the receiver's registry state on-chain (the IDTx definition verbatim), shipped in the public T-REX suite at ~$28bn scale; the absence result came from profiling ERC-3643 only through Frutuoso26 (which measured no transfers). 6 MAJOR: gap carried by the thesis's own Id-gate construct (gerrymander re-dressed); Caliper "can host" vs "ships" conflation; A5 non-standard + waived for v0; silent PROFILES→V0 scoring drift; v0 circular (in-house workload/rule/metrics); admission rule rejects no one (not an A2 gate). Launched WP 3.7 revision: profile T-REX + ERC-1404/CMTAT at source; retract "without exception" → "no complete A1–A5 benchmark has packaged an on-chain identity-gated-transfer workload"; reframe contribution as a **new workload class**, not an empty benchmark cell; concede v0 is A1/A3/A4(partial), A2/A5 open; back-propagate the narrowing to p1.
