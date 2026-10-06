# Review 03 — Two Trunks: the Sandbox Lineage and the Review-2 Lineage (2026-10-06)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Purpose:** the clean review that precedes any merge. Between 2026-09-30 and 2026-10-06 the
repository grew two independent trunks from the same commit, worked in parallel by different
sessions for the same author. This document says what each is, where they agree, where they
measured the same thing differently, where they contradict each other, and what the TSR plan of
2026-10-06 adds on top. The plan that follows it is `docs/PLAN_MERGE_LINEAGES.md`. The three
read-only analyses this review distils are kept verbatim under `docs/reconciliation/`
(`RECON_DOCS.md` — documents, claims, registers; `RECON_CODE.md` — contracts, tests, scripts,
results, merge-tree conflicts; `RECON_TSR.md` — the testing-suite plan against the sandbox).
Every number below carries its source there.

## 1. The lineage facts

| | Sandbox lineage (this branch) | Review-2 lineage (parallel trunk) |
|---|---|---|
| Branch | `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` @ `b70081c` | `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` @ `fa6188e` — **the repository's default branch** |
| Common base | `3203ee8` (the 2026-09-30 handback) | `3203ee8`, merged at `434669d` into a *third* lineage, the data-collection harness (`084edfd`…) |
| Commits since base | 35 | 155 (incl. 4 harness commits) |
| What it did | passes 03–06: MOBI checklist (preview), resolver fixes → 335/336, lifecycle parity, freshness-k; the **grand sandbox** (13 manifests, 11 adapters, 92 demos, L1–L4 layered suites); **defect log D1–D27** with fixes D7–D25; results re-executed twice with per-cell delta files; chapter 5 regenerated | "Review 2": a five-lens code review (64 findings, 3 Critical, 13 High) fixed in passes P1/P2/P3 with regression tests; two follow-up passes (F-A…F-E, G-R/G-M/G-K); the **metrics harness for all nine standards** (18-op catalogue, `npm run metrics`), an analysis layer (H5 dominance), an HTTP-RPC condition; re-runs of #21/#22/#24/#26/#27/#28; M4/M5 experiments |
| Tests at head | 386 Hardhat + 94 Python; 92 demos / 1,722 steps; CI green | 369 Hardhat / 23 pending + 358 Python (0 skipped); CI green with four more workflows |
| Register rows added | #29–#32 | #29–#39 (**collision**) |
| Same-named files, different content | `AFTER_ACTION_REPORT_03/04/05.md`, `MOBI_VID_CHECKLIST.md`, `experiment_freshness_k.py`, `experiment_lifecycle_parity.py`, `results/freshness_k.*`, `results/lifecycle_parity.*` | same |
| Thesis chapters | chapter 5 regenerated from the results of record; ch. 6/7 cells | unchanged since base (stale-figure list left for the author) |
| Handback | `HANDBACK_2026-09-30.md` + addenda 0–0d | `HANDBACK_2026-10-04.md`, which declares itself "now the single trunk" — true only up to `3203ee8` |

Two more branches: `claude/testing-suite-organization-z5j7dc` (2026-10-06) is one commit on
the review-2 trunk adding a **Testing Suite & Results plan (TSR v1.0)**, a second-pass decision
sheet and an as-found inventory; `claude/npat-game-planning-…` carries the review-2 lineage up to
`f646e88` plus an unrelated planning project under `npat-planning/` ("Inkwell") — it should live
in its own repository.

Neither lineage contains a single commit of the other. `git merge-tree` reports **64 conflicted
paths**: 10 contracts (incl. the byte-identical MOBI mirrors), the resolver, both testbed
providers, 23 result/artifact files, 18 documents, two add/add experiment scripts, and 8
rename/delete conflicts on the research copies.

## 2. Where the two lineages agree (reached independently)

- **The MOBI `getVehicleDID` fix is byte-identical** (our D10 `65a143f`, their K-15 `27a2184`).
- **External W3C DID suite 335/336**, same denominator (336), same single `did:nft` failure, by two
  different resolver rewrites (ours 2026-10-03; their R1–R4). Only ours also ran it on a
  registry-minted DID.
- **Compliance checker 94.3 %** on both — but through *opposite* resolver/checker pairings
  (ours keeps `contentType` in-process on `resolve()`; theirs removed it and corrected the checker's
  7.1.2 check). Mixing halves reads 92.0 %.
- **Revocation is terminal** (our D21/decision D-F ≡ their K-3) and `revokeIdentity` single-shot.
- **The ERC-1056 wrapper overflow** (our D18 ≡ their K-1 root cause), though theirs also changed
  the ABI.
- **MOBI verify binds to the registered key** (our D11 ≡ their T-4); ours goes further (D11b anchors
  the key on-chain, which theirs called "a design gap, out of scope").
- **Principles**: generated over typed, no skipped tests, n/a is a result, conditions travel with
  numbers, author-attributed commits.

## 3. Where they measured the same quantity differently

| Quantity | Sandbox lineage | Review-2 lineage | Why they differ |
|---|---|---|---|
| Nine-standard create spread | 52,170 → 1,680,816 (ERC-735 1,598,928; ERC-1155 deploy 2,871,435) | 52,216 → 1,680,816 (ERC-735 1,535,776; ERC-1155 deploy 2,304,865) | different fix sets on the same contracts (D7/D8/D13/D22/D25 vs K-1/K-2/K-3/K-4/K-11/K-13); both M1 cancun, both 2026-10-04 |
| Freshness-k | #29: one-`changed()` probe, k=1 2.697 ms, n=200, **dirty tree**, 2.80 GHz | #32 full refresh k=1 10.95 ms (knee k≈146), #37 probe t_chain 2.76–2.89 ms, n=250, clean tree, two hosts | different refresh instrument, host, statistic; their probe ≈ our k=1 — the instruments agree, the conclusions ("k≈25–100" vs "no k reaches P*=100 on the second host") differ |
| Lifecycle parity (M4) | #30: event 306,567 gas; cached half untested; `attest_event` row | #33: event 255,267; cached half **FAIL** as pre-registered; no `attest_event` | different scripts under one name, different operation inputs |
| MOBI backend sweep (H4) | re-run pass 06 after repairing the script (broken since D25) | re-run after P1-K and G-M | different contracts; fidelity scores identical |
| Scaling A/B lifetime | ERC-1155 1,865,183; CVIN 9,839,660; ERC-735 11,443,652 | 1,757,399; 9,677,232; 11,272,809 | different contracts; ranking identical on both |
| V2V latency #27 | left at base 0.165 ms (status B) | re-run **0.153 ms**, 150 = 5 attacks × 30 | only theirs re-ran it |
| PKI vs ERC-1056 #21 | left at base 0.321 vs 18.158 ms | re-run 0.253 vs 9.654 ms (≈38×) after T-1/T-2/T-5/T-9 | only theirs re-ran it; their fixes removed a redundant RPC and stale bytecode |
| `createVehicleDID` #1 | 78,068 | 78,090 (+22 from the K-1 ABI change) | ABI change on theirs |

Register numbering: theirs #29–#39 are referenced from 16 review-2 files; ours #29–#32 from
our reports, defect log, latency budget and chapter 5. Keep theirs; append ours as #40–#43
(ours #29/#30 marked superseded-by-instrument, #31/#32 as history rows).

## 4. Where they contradict each other (decisions the merge must make)

1. **CVIN-Combined claim operations — mutually exclusive designs.** Theirs (K-6): claim ops no
   longer advance `changed[]`. Ours (D22): claim ops advance `changed[]` and emit
   `DIDClaimChanged(…, previousChange)`. Both repair the resolver walk. Recommendation: K-6
   semantics (claims are not DID-document state; matches ethr-did-resolver) **and keep emitting
   `DIDClaimChanged` without advancing the pointer** so claim history stays indexable.
2. **`DIDRevoked` signature.** Ours three-arg with `previousChange` (removes the chain-cut
   caveat K-5); theirs kept two-arg deliberately. Recommendation: ours; their walk already
   tolerates it; regenerate their testbed artifacts and reword their test docstring.
3. **`setVehicleAttributes` ABI** (their K-1 adds `address did`). Recommendation: theirs; update
   our six call sites (regression test, demo).
4. **Research copies**: deleted (K-16) vs archived (`_research-copies/`, decision D-C).
   Recommendation: keep the archive; it is cited by `REVIEW_02_STATE_AND_PARALLEL_WORK.md`.
5. **Test layout**: flat `test/<Std>/` with repointed npm scripts (Q-10) vs layered
   `test/L1-identity-mechanisms` + `test/L2-identity-system/{per-option,security}`.
   Recommendation: layered (CI green, imports intact, the TSR tags work on either); their new
   files land in the layered directories; fix their `test:*` globs.
6. **Resolver/checker pair.** Theirs (decimal CAIP-10 chain id = our open D27, cache TTL, 75
   tests) with the corrected 7.1.2 check. Recommendation: theirs for both halves, then one floor.
7. **ERC-735**: their K-2 sticky issuer revocation and our D25a/b issuer whitelist + VIN binding are
   complementary — union; every one of their 18 ERC-735 `addClaim` test calls needs
   `authorizeIssuer` setup (the same breakage our pass 06 found in the sweep script).
8. **ERC-1155**: their K-13 is a strict subset of our D7/D8 (they listed the operator bypass as a
   Low residual; ours closed it as High). Take ours; their harness adapter must move identities
   with `issuerTransferIdentity`.
9. **LSP8**: their K-8 generation-versioned data store (fixes half of our open D12) and our D13
   VIN normalisation — union by hand in `mintVehicle`.
10. **MOBI**: their K-3 (public `changeOwner` reverts for born vehicles — what our D16-rest
    deferred), K-4 (pristine identity at birth) and OWNER scoping, plus our `anchorVehicleKey` —
    union; our regression test at two lines expects the pre-K-3 behaviour.
11. **MOBI VID source texts.** Ours wrote SC-14 believing the normative text member-only; theirs
    found VID I v2.0 TS/2024 public in full and wrote a clause-level checklist (2 of 8 MUSTs met,
    7 of 15 birth-certificate fields) proposing "a MOBI-VID-inspired profile". Theirs supersedes
    ours; SC-14's rationale must be corrected.
12. **Their `SCOPE_CHANGES.md` is truncated** (16 lines; `760913c` dropped SC-01…SC-13). Rebuild
    from ours plus their two notes; their proposed SC-14…SC-20 become SC-15…SC-21.
13. **Compliance floor** 94.0 (ours) vs 93.0 (theirs). One value after the merge, measured.
14. **Stale text in both READMEs** (ours: "217 Hardhat", "93.2 %", "0.165"; theirs: "90 failures =
    3 attacks × 30", INDEX "#1–#31").

## 5. What only one side has (to be kept, not re-done)

**Review-2 lineage only:** the metrics harness for all nine standards and its run of record; the
analysis layer; the HTTP-RPC condition; toolchain pinning and measured-code run identity; the
64-finding review and its stream reports; VC-verifier hardening S-1…S-9/T-3; PKI CA-signature
verification T-1 (forged certificates had been accepted); forward-replay key resolution T-2 and
the freshness/replay policy T-9; the #21/#22/#23/#27 re-runs; M3 `attestEvent` pin; M4
pre-registered verdicts; **M5 pseudonym pool** (gas FAIL, linkability PASS); the clause-level MOBI
checklist; the strict security harness with exact expected reverts; CI jobs for all Python suites
with "a skip fails the job".

**Sandbox lineage only:** the grand runner, manifests with review flags, adapters over one
interface with `NotApplicable` first-class, L1 uniform-mechanism suite, 92 demos covering 100 %
of every public surface, the ABI-generated feature-asymmetry matrix with CI freshness gate, the
MOBI byte-identity gate, the defect log and its §C of author decisions, fixes D7/D8/D9/D11b/D13/
D21/D22/D25, per-cell gas-delta files after every fix pass, the external suite on a
registry-minted DID, chapter 5 regenerated from the results of record, the two ERC-1056 variants
named in the register.

## 6. The TSR plan (2026-10-06) against the sandbox

TSR v1.0 is a taxonomy-and-register plan written for the harness trunk: five-dimension test
identifiers (`TC-<SUT>-<OP>-<CLASS>`), generated test/results/claims registers, a coverage
matrix with `T/N/G/P/X(+W)` cells, an evidence ladder E0–E7, run stamping and `runs/`→promote,
charters per property class, statistical rules, a chapter-5 presentation plan and a paper-intake
protocol. It does not know the sandbox exists. They do not contradict on principle; they conflict
on five names (test location, suite root, "L1–L4" suite layers vs the harness's "L1–L8" scenario
levels, cell vocabulary, SUT identifiers) and on register numbering. The cheapest reconciliation:
keep the sandbox layout and runner as the executable half, adopt TSR's identifiers, registers,
stamping, charters and statistics as the documentation half, and feed TSR's register builder from
the sandbox manifests and the L1/demo JSON so the coverage matrix and the asymmetry matrix are two
views of one source. TSR's inventory findings that hold on both lineages: ERC-725xy absent from
the security suite, weak legacy ERC-721 tests, use-case oracle = "returns without raising", stale
`sensitivity.*`, unpinned Python dependencies, a "47 tests" CI header.

## 7. Verdict

The two trunks are both sound and both incomplete, in complementary ways: review 2 hardened the
SSI/testbed layers and built the measurement harness; the sandbox exercised every contract surface
and fixed what that found. Neither can be discarded. The merge is a real pass, not a `git merge`:
ten of the conflicts are design decisions, every result of record must be re-executed once on the
merged contracts, and the register, scope log, chapters and handbacks must be rewritten once from
the merged state. The plan is `docs/PLAN_MERGE_LINEAGES.md`.
