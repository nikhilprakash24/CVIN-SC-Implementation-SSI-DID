# IDTx Core — Live Progress

**Updated:** 2026-10-24 · **Decision:** A+ (thesis is home; overflow → Appendix G / companion SP-9, returnable)

## Phase roadmap

```
Phase 1  function set, IDTx, benchmark gap   [■■■■■■■■■□]  ~85%   IN PROGRESS
Phase 2  compare to other ID systems         [□□□□□□□□□□]    0%   planned
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
| 1.9 | Thesis drafts (Ch 3 §3.x, Ch 6 §6.8, Ch 2 §2.6, App. G) | ED | ✅ done → `p1/THESIS_DRAFT.md` |
| 1.10 | Examiner pass (draft only) | SK | ✅ done → `p1/EXAMINER_REVIEW.md` (4 FATAL, 8 MAJOR) |
| 1.11 | CI: figure + link checks | ED | ⬜ queued |

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
