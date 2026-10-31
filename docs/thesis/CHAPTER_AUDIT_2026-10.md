# Chapter Audit Against the Claim Register (2026-10)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-23 (after-action report 37)
**Mode:** read-only. Nothing in the chapters was changed; this file is the only output.

**Sources of truth:** `docs/MEASUREMENT_CONDITIONS.md` (claim register, rows #1 to #62, status V / E / S / U / B),
`docs/testing/LATENCY_CHARTER.md` (rows #26, #31, #39, #57 are descriptive only), `docs/testing/claims.yaml`
(stable ids are `c<row>-...`, e.g. `c27-v2v-ssi-verify-warm`; cited below by row number).

**Chapters audited:** `chapter1-introduction/README.md`, `chapter2-literature-review/README.md` and
`DRAFT_SECTIONS_2026-10-20.md`, `chapter4-implementation/README.md`, `chapter6-discussion/README.md`,
`DRAFT_6.8_IDTX_2026-10-20.md` and `section-feature-asymmetry.md`, `chapter7-conclusion/README.md`. The two
`DRAFT_*_2026-10-20.md` files are absorbed stubs with no content of their own; nothing to audit.

**Classes:** OK (matches a V row in value, units, conditions); MISMATCH (value, units or conditions differ from the
row); OVERSTATED (rests on an S/E/U row but phrased as established, or a descriptive-only latency compared across
runs/hosts); UNSOURCED (no register row supports it); STALE (matches a value the register has since replaced).
Only problems checked against the register text are reported.

**Test counts.** Current: Hardhat 563 passing (`sandbox/grand/report/GRAND_REPORT.md`, L1+L2), Python layers 376.
Chapters 1, 4 and 7 defer the totals to the grand report (good). Chapter 4 still quotes per-suite counts (VC 28, MOBI 32,
VIN cipher 6 / 9) and cites register #5 as "current totals", but #5 is **S** (it records the superseded 28/28 and
369 / 358).

## Summary

| Chapter | OK | MISMATCH | OVERSTATED | UNSOURCED | STALE |
|---|--:|--:|--:|--:|--:|
| Ch. 1 Introduction | 5 | 5 | 0 | 2 | 0 |
| Ch. 2 Literature review | 5 | 1 | 0 | 1 | 0 |
| Ch. 4 Implementation | 6 | 4 | 0 | 2 | 4 |
| Ch. 6 Discussion (README) | 13 | 7 | 0 | 5 | 3 |
| Ch. 6 Feature asymmetry draft | 2 | 1 | 0 | 3 | 4 |
| Ch. 7 Conclusion | 8 | 4 | 2 | 3 | 2 |
| **Total** | **39** | **22** | **2** | **16** | **13** |

**Most serious, in order.**
1. **H5 / hybrid frontier.** Ch. 1 (H5 "supported outright", contribution 5), Ch. 6 §6.5 and §6.7 ("Pareto-optimal",
   "sits on the frontier", "all five hypotheses supported") contradict #36 (V): CVIN-Combined is dominated by ERC-4337
   on all six criteria and by five substrates on cost alone. Ch. 7 already carries the #36 qualifier; Ch. 1 and Ch. 6 do not.
2. **V2V latency stale in Ch. 6 and Ch. 7.** 0.153 ms [0.151, 0.154], cold 0.399, PKI 0.094, "150 = 5 attacks x 30",
   "~650x" are the earlier #27 values; the row now reads 0.142 [0.141, 0.143], cold 0.363, PKI 0.090, 210 = 7 x 30.
3. **attestEvent gas stale/mixed** (Ch. 4, Ch. 6 §6.1): 121k -> 193k and "192,749 -> 222,082" mix July,
   superseded sweep and receipt figures; #28 now gives 198,694 execution gas, receipt 222,058 to 222,082.
4. **W3C checker conditions** (Ch. 1, 4, 6, 7): CI floor quoted as >= 90 % (register: 94.0 %); "two deviations"
   (register: a third, the thesis-defined `credentialStatus` type); Ch. 1 / Ch. 6 omit the required "structural self-score" label.
5. **Ch. 4 resolver description stale:** says the resolver reads no chain state "to be changed in WM-2 C1"; #4 / #24 record C1 done (2026-10-15).

---

## Chapter 1: Introduction

| Location | Claim | Row | Class | Suggested fix |
|---|---|---|---|---|
| §1.3 H1, "on update the ratio is 3.4x over ERC-721 and 3.9x over ERC-725 (register #25)" | update ratios | #25 | UNSOURCED | #25 claim text gives no update ratio. The csv's 3.41 / 3.90 are relative to the cheapest (CVIN-Combined 35,116), not ERC-1056 (35,494 gives 3.37 / 3.86). Add the ratio to #25 or cite the csv column and its baseline. |
| §1.3 Preview, "all five hypotheses supported ... H1, H2, H3, and H5 are supported outright" | H5 and H1 verdicts | #36; #25 | MISMATCH | #36: CVIN-Combined dominated by ERC-4337 on all six criteria; and H1's own note says the update half is not supported. Restate as Ch. 7 does (H5 only on the fidelity-per-gas plane; H1 creation only). |
| §1.4 item 5, "landing on the fidelity-per-gas and security/performance frontiers" | hybrid on frontiers | #36 | MISMATCH | Drop "security/performance frontier"; add "not on the six-criterion harness frontier (#36)". |
| §1.4 item 2, "measures 94.3% aggregate compliance against DID Core v1.0 and VC Data Model v2.0" | 94.3 % | #4 | MISMATCH | #4 requires the wording "structural self-score" on the internal checker (offline, synthesised documents). Use it. |
| §1.5 Demo-scope, "The two W3C compliance deviations ..." | two deviations | #4 | MISMATCH | #4 records a third deviation (thesis-defined `credentialStatus` type, ch. 5 §5.5). Say three. |
| §1.1.4 Cost, "differ by more than an order of magnitude" | create spread | #25 | OK | 33.7x. |
| §1.4 item 1 / §1.5, "reproduced across N=30 runs", "byte-identical across N=30 runs" | determinism | #25 | OK | |
| §1.4 item 3, "more than a million verifications with every injected attack caught", "two to three orders of magnitude" | V2V | #27 | OK | 1,650,318 verifies; 210 rejected; 100 / 0.142 = ~700x. |
| §1.4 item 6, "12/12 lifecycle use cases" | use-case count | none | UNSOURCED | No register row. Add a row or point to the grand report. |
| §1.5 Gas, "identical across EVM chains for identical bytecode and calldata, the comparison ... is valid on any chain" | cross-chain gas | §1 correction (AR-18) | MISMATCH | Register: holds for execution gas only under identical bytecode, calldata, pre-state and fork; cross-network gas reported within a stated tolerance (100 gas). Add the tolerance. |
| §1.5 Gas, Sepolia "not yet been executed" | M2 status | tag M2 | OK | |
| §1.4 item 4, attestEvent found and fixed | fix | #28 | OK | |

## Chapter 2: Literature Review

| Location | Claim | Row | Class | Suggested fix |
|---|---|---|---|---|
| §2.4.5 Vehicular revocation, "accepted for at most k - 1 further messages (#46, #32)" | k - 1 bound | #46, #32 | OK | |
| §2.4.5 What this thesis adds, "in 280 of 280 trials (#37)" | staleness trials | #37 | OK | |
| §2.4.5, "the absolute knee is a property of the host, not of the policy (#52)" | host attribution | #52 | OK | |
| §2.7 storage locus, "(#49, #51) ... at depth 50 (#31)" | storage / read cost | #49, #51, #31 | OK | No latency value quoted, so #31's descriptive class is not engaged. |
| §2.7 evaluation point, "+46,830 gas per operation, #25" | 4337 indirection | #25 | OK | |
| §2.7 What is new, "4 of 26 Phase 1 gates qualify" | gate count | none | UNSOURCED | Not a register row (cites DISPOSITIONS_F1-F3). Add a row or mark as a classification, not a result. |
| §2.8, "applies ... the same W3C compliance checklist to nine substrates" | checker scope | #4 | MISMATCH | #4: the checker scores offline-synthesised documents of the resolver's methods, not nine substrates. Rephrase. |

## Chapter 4: Implementation

| Location | Claim | Row | Class | Suggested fix |
|---|---|---|---|---|
| §4.1, "it synthesises the document from the identifier and reads no chain state ... to be changed in WM-2 step C1" | resolver behaviour | #4, #24 notes (WM-2 C1, 2026-10-15) | STALE | C1 (chain-reading resolver) is done; the offline mode is now labelled `offline-synthesized`. Describe both modes. |
| §4.3.3, "(cost rose 121k -> 193k gas)" | attestEvent gas | #28 | STALE | 121,110 -> 192,718 is the July build. Current: 198,694 execution gas (receipt 222,058 to 222,082). |
| §4.3.2 / §4.6 table, "28-test suite", "W3C Verifiable Credentials 28" | VC test count | #5 | STALE | #5 (S) supersedes "VC layer 28/28". Quote grand-report totals (Hardhat 563, Python 376). |
| §4.6, "current totals in ... GRAND_REPORT.md, register #5" | test totals | #5 | STALE | #5 is S and records 369 / 358. Cite the grand report only, or update #5. |
| §4.3.3 / §4.6, "9 cipher tests ... (part of the 32 MOBI VID Python tests)" vs table "VIN cipher 6" | MOBI / cipher counts | none | UNSOURCED | No row, and the text (9) and table (6) disagree. Reconcile against the suite. |
| §4.4.2 / §4.6, "12/12 passing" | use cases | none | UNSOURCED | As Ch. 1. |
| §4.5 item 3 and §4.6 CI, "CI-gated at >=90%", "the >=90% compliance gate" | CI floor | #4 | MISMATCH | Floor is 94.0 % (`COMPLIANCE_FLOOR`; "93.0" corrected 2026-10-10). |
| §4.5 item 3, "the two documented deviations" | deviations | #4 | MISMATCH | Three (add `credentialStatus` type). |
| §4.5 item 4, Sepolia would "confirm the local numbers ... EVM gas is a deterministic function of opcodes" | cross-chain gas | §1 correction (AR-18) | MISMATCH | Confirmation is within the 100-gas tolerance of `validate_sepolia.js`. |
| §4.2 table, ERC-725xy "the heaviest to deploy (a complete account per identity)" | ERC-725xy rank | #25 | MISMATCH | #25: ERC-735 create 1,757,881 is heaviest; ERC-725xy 1,680,816 second. |
| §4.6, "54 scenarios, 43/43 applicable cells defended" | security | #28 | OK | 43/43 DEFENDED + 11 N/A. |
| §4.6, "byte-identical across N=30 runs (sigma=0)" | determinism | #25 | OK | |
| §4.2 ERC-1056, "implicitly its own did:ethr at zero on-chain cost"; "Cheapest lifecycle" | creation 0 gas; lifetime | #47, #35 | OK | |
| §4.8.2, "3,498 constraints (1,667 non-linear, 1,831 linear), 3,505 wires ..." | circuit size | #56 | OK | |
| §4.8.3, Schnorr "at a small fraction of the gas (register #58)" | 28,775 vs 301,163 | #58 | OK | |
| §4.8.1, operation counts "(register #59, #62)" | counts | #59, #62 | OK | Counts V; times in #62 are E, not claimed here. |

## Chapter 6: Discussion (README)

| Location | Claim | Row | Class | Suggested fix |
|---|---|---|---|---|
| §6.1, "CVIN-Combined and ERC-1056, both ~52k gas" | create | #25, #6 | OK | 52,216 / 52,594. |
| §6.1 Recovery, ERC-4337 "at the second-highest creation cost" | rank | #25 | MISMATCH | 759,088 is third, after ERC-735 1,757,881 and ERC-725xy 1,680,816. |
| §6.1, "attestEvent rising from 121,110 to 192,718 gas (192,749 ... -> 222,082 since WM-2 C2) ... extra ~72k gas" | attestEvent gas | #28; #25 notes | STALE | Mixes the July pair, the superseded sweep 192,749 and one end of the receipt range. Use #28: 198,694 execution gas, receipt 222,058 to 222,082. |
| §6.2 table, "Cheapest creation (~52k gas), ~10x under NFT/proxy designs" | ratio | #6 | MISMATCH | #6 requires the operation definition with the ratio: 10.4x is bare ERC-1056 vs `mintVehicle`; VIN-bound headline is 6.9x. State which. |
| §6.2 / §6.5, "5/5 fidelity"; "421,263 gas, against 798,621 ... and 870,577" | backend sweep | none (#43 mentions only "fidelity scores unchanged") | UNSOURCED | No register row; also differs from current `mobi_vid_backends.csv` (423,352 / 821,781 / 885,808), itself pre-C2 (MOBI attestation now 222,058). Add a row and re-quote. |
| §6.3, "warm-verify median of 0.153 ms and cold ... 0.399 ms"; "0.153 ms vs 0.094 ms" | V2V latency | #27 | STALE | Now 0.142 [0.141, 0.143], cold 0.363, PKI 0.090 (A5, 2026-10-23). |
| §6.3, "exactly the 150 injected attacks (5 per run x 30 runs; register #27)" | failures | #27 | STALE | 210 = 7 per run x 30. |
| §6.3, "1.65M verifications", "CIs non-overlapping", "about 1.6x" | V2V | #27 | OK | Within-run comparison (L-within). 0.142 / 0.090 = 1.58x still rounds to 1.6x. |
| §6.4, "94.3% aggregate ... residual gap is confined to three documented items (two deliberate deviations and one PARTIAL)" | score and residual | #4 | MISMATCH | Add "structural self-score"; the deviations are three (`credentialStatus` type). |
| §6.4, "DID Core 14/15 ... VC Data Model 93.1% (27/29) (register #4)"; "the PARTIAL is the did:mobi placeholder key (register #4)" | per-spec split | #4 | UNSOURCED | #4 gives only 41 PASS / 1 PARTIAL / 2 FAIL of 44 and DID Core 7.1.2 history; no split, no PARTIAL attribution. Add to #4 or cite the result file. |
| §6.4, "a checker that runs against the real VC layer and DID resolver" | checker scope | #4 | MISMATCH | #4: offline resolver only, synthesised documents; 7 of 8 security mutants left the score unchanged. Say so. |
| §6.5 title and body, "Pareto-optimal", "sits on [the frontier]", "exactly consistent with H5" | hybrid | #36 | MISMATCH | #36: dominated by ERC-4337 on all six criteria; the fidelity-per-gas plane has no register row. Scope it and add the #36 qualifier. |
| §6.5, create 52,216 vs 52,594, update and transfer "at ERC-1056 cost" | gas | #25 | OK | Values match; "statistically indistinguishable" is the wrong word for deterministic gas (say "within 1 %"). |
| §6.5, "~290k gas for addClaim" | claim gas | #25 | OK | 291,977. |
| §6.6.3, "Gas is deterministic across EVM chains, so the comparison ... is valid" | cross-chain | §1 correction (AR-18) | MISMATCH | Add the tolerance statement. |
| §6.7, "All five hypotheses (H1-H5) are supported" | verdicts | #36; H1 note | MISMATCH | H5 not supported under #36; H1 update half not supported. Align with Ch. 7 table. |
| §6.8.3, "of 26 gates inventoried, 4 are identity-dependent transactions ..." | gate counts | none | UNSOURCED | As Ch. 2. |
| §6.8.3, "29,333 gas ... (#28: execution gas 169,361 -> 198,694)" | D54/C2 cost | #28 | OK | |
| §6.8.4, "149 new storage slots ... ERC-1056 pays 8 (#49)", "most expensive ... (#35)", "constant 3 RPC calls (#51)" | footprint | #49, #35, #51 | OK | #35's ERC-735 total excludes 3 n/a events; say so. |
| §6.8.4, "112 RPC calls and 87 KB at depth 50 (#31, #51)" | read cost | #31, #51 | OK | Counts only; no descriptive latency quoted. |
| §6.8.4, "+46,830 gas over the direct call (#25)" | 4337 | #25 | OK | |
| §6.8.5, "280 of 280 trials (#37)", "(#46)", "(#52)" | freshness | #37, #46, #52 | OK | |
| §6.9.1, "301,163 gas per admission (register #58)" | gate gas | #58 | OK | |
| §6.9.2, "proving takes 398.6 ms against a ~100 ms budget; register #57" | prove time | #57 | OK | Descriptive-only, but compared with a budget, not across runs or hosts. Add "descriptive only (N = 10)". |
| §6.9.1, "reversed in seconds on one core" | brute force | #60 | OK | 3.58 s. |
| §6.9.3, "copies a 1,300-character presentation" | character count | #62 | UNSOURCED | #62's text gives no 1,300 figure. Add it to the row or cite `manual_burden.json`. |
| §6.9.3, "the learner without the kernel's budget was broken outright by an accredited adversary (register #61)" | insider result | #61 | UNSOURCED | #61 says only that the insider variant is post hoc and leakage <= 3.0 bits under the Steward. Add the result to #61. |
| §6.9.3 Risk table, "honest service below 90 % on some runs (Z-E6)" | Z-E6 | #61 | OK | |

## Chapter 6: Feature asymmetry draft (`section-feature-asymmetry.md`, dated 2026-10-04)

| Location | Claim | Row | Class | Suggested fix |
|---|---|---|---|---|
| §6.x.2 Creation, "records creation at 0 gas" | implicit creation | #47 | OK | |
| §6.x.2, "the vehicle-profile registry's explicit `registerVehicle` costs 54,639" | register gas | #22 | STALE | #22: 54,868 (54,844 to 54,868); earlier 54,860. |
| §6.x.2, "103,849 (ERC-1155), 149,430 (LSP8), 542,474 (ERC-721, VIN-bound)" | mint gas | #25 | STALE | Current #25 table: 107,729 / 152,644 / 545,101. |
| §6.x.2, "1,371,394 (ERC-735)" | ERC-735 create | #25 | STALE | #25 lists 1,371,394 as pre-K-2 history; now 1,757,881. |
| §6.x.2, "1,730,753 (ERC-725xy with its VIN key)" next to #25 figures | ERC-725xy create | #34 vs #25 | MISMATCH | 1,730,753 is the M1-H harness (#34); #25 (M1) is 1,680,816. §5 forbids mixing M1-H and M1 in one list. |
| §6.x.2, "519,384 (ERC-725)", "759,088 (ERC-4337)" | create | #25 | OK | |
| §6.x.2, "P-256 ... 0.054 ms; secp256k1 signing costs 0.401 ms (register #21)" | sign times | #21 | UNSOURCED | #21 reports verify/resolve/register/issue/revoke, no signing times. Remove the citation or add a row. |
| §6.x.3, "deployment size (ERC-721 2,751,406 gas; MOBI VID V2 3,952,603)" | deploy gas | #25 | STALE | Current: ERC-721 2,787,288; MOBI-VID-V2 4,370,878. |
| §6.x.2, "changeOwnerSigned, 96,053 gas; ... 69,405; ... 76,352; ... 28,358" | signed-path gas | none | UNSOURCED | No register row (grand-report L1 table). Add a row or cite the run. |
| §6.x.1 / §6.x.3, "92 demos, 1,625 contract calls", "88/88", "26 latent defects ... 20 ... six" | sandbox counts | none | UNSOURCED | No register row; draft predates many fixes (D11, D22). Re-generate and cite the report commit. |

## Chapter 7: Conclusion

| Location | Claim | Row | Class | Suggested fix |
|---|---|---|---|---|
| §7.2 RQ1, "~34x ... from 52,216 gas (CVIN-Combined) to 1,757,881 gas (ERC-735)" | spread | #25 | OK | 33.7x. |
| §7.2 RQ1, "ERC-1056 (52,594) is ~10x cheaper than ... ERC-721 (545,101) and ERC-725 (519,384)" | ratio | #6, #25 | OK | Operation definition is given in §7.7. ERC-725 is 9.9x. |
| §7.2 RQ1 / §7.4, "46,830 gas per operation" | 4337 | #25 | OK | |
| §7.2 RQ2 / §7.4, "43/43 applicable attack cells", "54-scenario" | security | #28 | OK | |
| §7.2 RQ3, "94.3% on the internal executable checker, a structural self-score" | score | #4 | OK | |
| §7.2 RQ3, "above the >=90% CI gate" | CI floor | #4 | MISMATCH | Floor 94.0 %. |
| §7.2 RQ3 / §7.3 H2, "two documented, deliberate deviations" | deviations | #4 | MISMATCH | Three. |
| §7.2 RQ3 / §7.3 H2, "DID Core v1.0 14/15 ... VC Data Model v2.0 93.1%, 27/29; register #4" | split | #4 | UNSOURCED | As Ch. 6 §6.4. |
| §7.2 RQ4 / §7.3 H3 / §7.4, "0.153 ms [0.151, 0.154]", "cold 0.399 ms", "PKI baseline (0.094 ms)", "~650x", "25x" | V2V latency | #27 | STALE | Now 0.142 [0.141, 0.143], cold 0.363, PKI 0.090; margin ~700x; cold vs 10 ms target ~27x. |
| §7.4, "all 5 injected attack types rejected in every run (150 of 150)" | failures | #27 | STALE | 7 per run x 30 = 210 of 210. |
| §7.1, "latency figures are wall-clock medians with bootstrap 95% confidence intervals over N=30 seeded runs" | latency method | Charter; #26, #31, #39, #57 | OVERSTATED | True for #27 only. #26, #31, #39 and #57 are descriptive only (one sweep, N = 10, no CPU recorded). Scope the sentence. |
| §7.2 RQ4, "clears a 10 ms signature-check target" | target | #14 (E) | OK | Phrased as a target, as E requires. |
| §7.2 RQ5 / §7.3 H6, 3,498 constraints, 398.6 ms, 18.42 ms, 301,163 gas, 3.58 s, <= 3.0 bits, 25 of 60 | layer 5 | #56 to #61 | OK | 398.6 ms is descriptive only (#57); compared with a budget only. |
| §7.3, "All five hypotheses are supported" | verdicts | #36; Ch. 1 H1 note | MISMATCH | The table itself limits H5 to the fidelity-per-gas plane (not supported under #36) and H1 to creation. Change the lead sentence. |
| §7.3 H5 / §7.4 / §7.7, "on the fidelity-per-gas frontier among the 5 MOBI backends" | sweep frontier | none | UNSOURCED | No register row for the backend sweep's fidelity scores or sums. Add one. |
| §7.5, "the comparison transfers to any EVM chain" | cross-chain | §1 correction (AR-18) | MISMATCH | Add the tolerance. |
| §7.6 item 3, "Extend beyond 50 vehicles / 10 Hz" | SUMO 50 vehicles | #15 (E) | OVERSTATED | #15: configured, not run. Say "configured for 50 vehicles, not run". |
| §7.1 item 4, "12/12 lifecycle use cases" | use cases | none | UNSOURCED | As Ch. 1. |
| §7.1, "byte-identical across N=30 runs (sigma = 0)" | determinism | #25 | OK | |
