# IDTx Core — Live Progress

**Updated:** 2026-10-24 · **Decision:** A+ (thesis is home; overflow → Appendix G / companion SP-9, returnable)

## Phase roadmap

```
Phase 1  function set, IDTx, benchmark gap   [■■■■■■■■■■]  100%   COMPLETE (examiner fixes applied)
Phase 2  compare to other ID systems         [■■■■■□□□□□]  ~45%   IN PROGRESS
Phase 3  nearest benchmarks, benchmark v0     [□□□□□□□□□□]    0%   planned
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
| 2.4 | Figures (heat map; trade-off radar) | VA | 🔵 running |
| 2.3b | Verify ERC-3643/ONCHAINID + eIDAS columns (free primaries) | SS | 🔵 running |
| 2.5 | Examiner pass | SK | ⬜ queued |

- `2026-10-31` ED — Phase 2 launched. One Standards-Scholar agent doing 2.1–2.3 (grounded in the sourced ANALOGIES matrix; evidence tags carried forward). Figures + examiner to follow.

- `2026-10-31` SS — WP 2.1–2.3 ✅: `p2/COMPARISON.md`. Selection criterion = one ordered trust-locus axis, 8 distinct points, each a deployed spec. ~15 cells upgraded to [src] (OIDC/SAML/OCSP/LDAP/SCIM free primaries). Headline tradeoff T1: the ledger removes the live-authority dependency but pays for it three ways — revocation becomes a public (loses query-privacy), ordered (AR-10 race), and costly (gas #49/#31) write — the same contract-readable property that enables the IDTx forecloses off-ledger privacy and adds ordering risk. 52/96 cells still not [src]; ERC-3643 (S8, closest prior art) + eIDAS columns launched for verification (2.3b) alongside figures (2.4).
