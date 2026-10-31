# TDP-010 — Thesis Adaptation Map: the Specification onto Chapter 3

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-21 (after-action report 25; runbook phase 10). **Revision:** B (2026-10-31, report 39).
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000). **Supersedes:** nothing.
**What this is.** Each shall-statement of TDP-002 mapped to the section of chapter 3 (`docs/thesis/chapter3-methodology/README.md`,
539 lines at `b7ea6f4`; 632 lines at `b50864c`, where sections 3.1 to 3.8 are unchanged line for line and a new section 3.9 on the zero-knowledge extension was appended, so every line reference below still holds) that carries its commitment, with the state of the current text against it and the sentence
that would carry it in the thesis register. Where the commitment is a result, an interpretation or a limitation, the
map names chapter 5, 6 or 7 instead. Section 3 lists the places where chapter 3 now contradicts the register or omits
what passes 16 to 24 established. Section 4 says how the recent work (C1, C2, the I-24 and I-05 briefs, the decision
sheet) enters chapter 3 as method. **No chapter is edited by this document** (phase 10 rule; WM-2 D1 makes the edits
after decisions D-1 to D-15). Every number carries its register row and is status V.

## 1. Reading rule for the map

| Column | Meaning |
|---|---|
| State | **carries**: the current text states the commitment. **absent**: nothing in chapter 3 states it. **contradicts**: the current text says something the register does not hold, with the line number. **partial**: present without its limit |
| Sentence | the sentence to paste, in the thesis register (declarative, no hedging adverb, the row in brackets). A sentence is written once here and not again in D1 |
| Chapter | 3.x the chapter 3 section (existing, or "new 3.10" and "new 3.11" per the outline in section 5; the chapter's own 3.9 is the zero-knowledge extension added 2026-10-22); 5, 6, 7 when the commitment is not method |

## 2. The map

### 2.1 System and scope (SYS)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| SYS-01 identical operation set, n/a never emulated | 3.2 | carries (lines 79 to 137) | keep; add after line 132: "Totals that exclude events a substrate lacks are marked 'excl. n/a' and are not compared with full totals [#35]." |
| SYS-02 one evidence register | new 3.10 | absent | "Every number in chapters 5 to 7 is a row of the claim register with status V, carrying its condition tag, source path and commit; a number without a row is labelled an estimate or a target [`docs/MEASUREMENT_CONDITIONS.md` section 2]." |
| SYS-03 declared condition tags | 3.1.3 | partial (lines 60 to 75 name the platform, not the tags) | "Measurements are tagged M0 (in-process, no chain), M1 (Hardhat local), M1-H (the metrics harness), M1-H/HTTP (over a local JSON-RPC hop) or M2 (public testnet); no M2 measurement exists in this thesis [register section 1]." |

### 2.2 Cost and storage (PRF, RQ1)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| PRF-01 nine-standard gas, 30 runs byte-identical | 3.3.1, 3.3.2 | carries, with one correction (section 3, item 5) | "The nine-standard benchmark is re-run 30 times on a fresh in-process network; every cell is byte-identical across the 30 runs [#25]." |
| PRF-02 the create ratio under its definition | 3.2.2 and 5 | contradicts at line 51 (H1 "≥10×") | "The create-identity ratio between ERC-1056 and ERC-721 is reported under each operation definition: 10.4 with bare creation against a VIN-bound mint, 6.9 with the VIN bound on both sides [#6, #25]; H1's creation half is tested under the stated definition and its lifetime half against the seventeen-event lifecycle [#35]." |
| PRF-03 lifecycle gas over 17 events | new 3.3.4 (the metrics harness) | absent (the harness is not in chapter 3) | "A second instrument, the metrics harness, drives every substrate through one declared catalogue and a seventeen-event MOBI VID lifecycle, recording exact gas, storage opcodes, log bytes and read cost per operation; its run of record is identified by the tree hashes of the measured code, not by a commit [register section 5]." |
| PRF-04 lifetime model with band | 3.3 (new paragraph) and 5.9 | absent in 3 | "A fifteen-year lifetime model aggregates the measured per-event gas over an assumed event profile, with a sensitivity band of plus or minus 50 percent on recurring events; it is a model over an assumed profile, not a fleet measurement [#26]." |
| PRF-05 footprint and read cost against history | new 3.3.4 | absent | "The harness records, per substrate, the storage writes and log bytes of the lifecycle and the RPC calls and bytes needed to resolve a document at history depths 1, 10 and 50; the counter counts SSTORE opcodes, not net slots [#49, #51]." |
| PRF-06 dominance on declared criteria | 3.3 (method) and 5.3 | contradicts at lines 54 to 55 (H4 and H5 "the hybrid dominates", "sits on it") | "The hybrid's position is evaluated on six declared criteria from the harness; the O(1) on-chain credential check among them is a design property assigned per adapter, not a measurement [#36]. H5 is tested as two statements: that no substrate dominates, and where the hybrid falls." |
| PRF-07 relayed and account-abstracted writes | 3.2.1 (line 101) | partial (the ERC-4337 indirection is named; the ERC-1056 relayed path is not) | "Two write paths exist beside the owner's direct transaction: a relayed signed operation (ERC-1056) and an account-abstracted operation through an entry point (ERC-4337); both are measured against the direct write on the same substrate [#50]." |

### 2.3 Security and observability (SEC, RQ2)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| SEC-01 strict revert harness | 3.5.1 | partial (reverts are asserted; the reason is not) | "A cell is DEFENDED only when the transaction reverts with the documented expected reason; the on-chain script accepts any revert and is not the instrument of record [#28]." |
| SEC-02 signed generation time, window, replay | new 3.4.6 | absent | "Every verifier signs the generation time with the payload, rejects a message older than 1.0 s or more than 0.1 s in the future, and rejects a repeated signed digest within that window; both bounds are project choices tied to the 100 ms interval and are constructor arguments [`cv2x-testbed/identity/freshness.py`; #21, #45]." |
| SEC-03 staleness bounded by k | new 3.4.7 | absent | "A verifier that re-checks a sender's revocation state every k messages is tested for the bound of at most k minus 1 accepted messages after revocation, for vehicles and roadside units; the bound is a message count, not a time [#32, #46]." |
| SEC-04 revoked key under clock skew | new 3.4.7 and 7.5 | absent | "The provider evaluates key validity in chain time, not the verifier's wall clock; the defect that let a revoked key verify when the verifier's clock lagged the chain by more than 900 s was found at WM-1 and fixed at WM-2 C0, and the freshness rows measured before the fix are re-run at A3b (D51)." |
| SEC-05 attestation authority | 3.5 (new paragraph) and 5.6 | absent (C2 landed 2026-10-17) | "An on-chain lifecycle attestation is accepted only from an attester that holds a role and is the vehicle's current owner or its `veriKey` delegate, once per event; the consent rule is the owner's delegation stored in the registry, as the canonical ERC-1056 registry stores it [report 22; #28]." |
| SEC-06 VIN confidentiality on chain | 3.8 (line 525) | partial (architecture stated; the testbed's unsalted hash is not) | "The MOBI registries store a salted VIN hash and an AES-256-GCM ciphertext, never the plaintext; the cv2x testbed derives a vehicle's identity from an unsalted VIN hash, which is a recorded defect, not the design (D64)." |
| SEC-07 pseudonym pool observability | new 3.5.4 | absent | "Pseudonymity on a public registry is measured as the number of pseudonyms one log query returns for a delegate pool of 20 per five-minute epoch, with its gas, under a pre-registered band [#38]; radio, timing and position linkability are out of scope (SC-02)." |

### 2.4 Standards expression (STD, RQ3)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| STD-01 internal structural checker | 3.6.1, 3.6.3 | contradicts at line 398 ("not a self-scored checklist") against the register ("internal and self-scored") | "The internal checker is executable and self-authored; it scores the structure of resolved documents and credentials against DID Core v1.0 and VC Data Model v2.0 and is reported as a structural self-score, not as conformance [#4]. Until WM-2 C1 the `did:ethr` document was synthesised from the identifier; with a provider the resolver now reads owner, delegates, attributes, chain-time validity and deactivation from the registry, and the checker's inputs still resolve without a provider, so the score did not move (report 21; N-24)." |
| STD-02 external DID test suite | 3.6 (new paragraph) | absent | "The resolver is run against the W3C DID test suite at commit `939b31d`; 336 tests are generated and reported individually; DID-URL dereferencing is not run [#24]." |
| STD-03 MOBI lifecycle on several backends | 3.7 | carries, with the wording of SC-14a missing | "The profile is MOBI-VID-inspired and checked clause by clause against the public MOBI VID I v2.0 and VID II texts; 2 of 8 VID I MUSTs are met, and the unmet ones are recorded deviations [`docs/MOBI_VID_CHECKLIST.md`]." |
| STD-04 database parity | new 3.7.3 | absent | "The lifecycle writes of the MOBI V2 registry are compared with an in-process registry under a pre-registered band, and the verdict is reported as it fell: writes at least ten times dearer on chain, PASS; 'equal once cached', FAIL [#33]." |

### 2.5 Real-time verification (RTV, RQ4)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| RTV-01 warm verify inside the identity share | 3.4.2 | contradicts at lines 259 to 260 ("100 ms end-to-end budget and a 10 ms per-message target") and line 53 (H3 "~100 ms end-to-end") | "The identity share of the 100 ms interval is f of it, with f equal to 0.5 as the working point; the quantity judged is P*(f), the number of neighbours serviceable inside that share, and the threshold is P*(0.5) of at least 100, which is a per-message cost of at most 0.5 ms [`docs/LATENCY_BUDGET.md`; #27]. No end-to-end latency is measured." |
| RTV-02 uncached chain read reported beside PKI | 3.4 (new paragraph) | absent | "On identical operations, the certificate baseline and the uncached chain-backed verifier are timed in the same run; the chain column is the cv2x registry, not the benchmark's registry, so it is not compared with the gas tables [#21]." |
| RTV-03 freshness-k curve, both modes, host stated | new 3.4.7 | absent | "Amortised verification cost is measured as a function of the re-check cadence k for a full-resolution refresh and a one-call probe refresh; each run states its host and its local cost, because the knee depends on the difference between the 0.5 ms share and the local cost [#32, #37, #52]." |
| RTV-04 message size | 3.4 (new sentence) | absent | "Signed message sizes are reported for the certificate-carrying and the credential-referencing designs; no channel model follows from them [#23]." |

### 2.6 Infrastructure messaging (INF)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| INF-01 to INF-05 | new 3.4.8 (V2I and I2I method) and 5.4.1 | absent (chapter 3 has no infrastructure method; chapter 5 section 5.4.1 has the results) | "Roadside units, signal controllers and a traffic-management centre are `did:ethr` identities credentialed by a road authority; SPaT is signed at 10 Hz and verified with the same window, replay, binding and revocation rules as a BSM; five questions were pre-registered with bands and falsifiers before any run, and every departure is a dated amendment [`docs/design/INFRASTRUCTURE_PREREG.md`; #44 to #48]. The back-haul is in-process and the revocation registry has no propagation delay." |

### 2.6a Layer 5 (L5) and the basic-set coverage (SYS-04)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| L5-01 to L5-07 | 3.9 (as written 2026-10-22) and 5.10 | carries (3.9.1 states Z-E1 to Z-E7 with conditions and verdict rules; 3.9.2 the amendments; 3.9.3 the tags M0, M1, Sim, E; 3.9.4 the manual-burden method) | keep; one addition to 3.9.3: "All layer-5 runs of record are at commit `978988e` with the producing code clean; the manual-burden run at `e780d40` reproduces them [#57 to #62]." |
| SYS-04 basic-set coverage | 3.2 (new 3.2.4) | absent | "The catalogue is mapped onto the basic digital-ID function set, Set A for identity and keys and Set B for credentials; coverage is reported per substrate under two counts, strict (every mapped function present) and native (every mapped function a native primitive), which admit different substrates [#53, #54]." |

### 2.7 Evidence and reproducibility (EVD)

| Req | Chapter | State | Sentence |
|---|---|---|---|
| EVD-01 run stamp with scope | new 3.10 | absent | "Every producer stamps its output with the commit, a dirty flag computed over its resolved import closure and declared inputs, and the whole-tree flag beside it; a run with a dirty producing-code flag is discarded and the discard recorded [`tools/run_identity/stamp.py`]." |
| EVD-02 promote from a clean run | new 3.10 | absent | "A result reaches its tracked path only through a promote step that refuses a dirty run, another commit, a changed scope, an edited output or an undeclared destination [`tools/run_identity/promote.py`]." |
| EVD-03 pre-registration, dated amendments | new 3.11; the chapter's 3.9 already carries it for layer 5 | partial (3.9.1 and 3.9.2 state the protocol for Z-E1 to Z-E7 and amendments A1, A2; the Phase 1 pre-registrations I1 to I5, M4, M5 are not stated) | "Pre-registered experiments commit their questions, measures, bands and falsifiers before the first run; departures are dated amendments marked post hoc where made after the run; verdicts are reported as they fell, including the two FAIL verdicts and the one ratio outside its band [#33, #38, #44]." |
| EVD-04 generated documents | new 3.10 | absent | "Figures, registers and tables are generated from committed data by committed scripts and compared in continuous integration; none is edited by hand." |
| EVD-05 every guard shown to fire | new 3.10 | absent | "Every guard has a probe that fails on the broken version and runs in continuous integration; a guard never seen to trip is not treated as evidence." |
| EVD-06 full suite, no skips | 3.1.3 or new 3.9 | absent | "The contract suite, the Python suites and the demo runner run in continuous integration with a skipped test counted as a failure and the test count gated against the grand report." |

## 3. Chapter 3 against the register and passes 16 to 24: the drift table

| # | Line(s) | Chapter 3 now says | The evidence says | Replace with |
|---|---|---|---|---|
| 1 | 51 | H1: ERC-1056 "≥10× cheaper … for identity creation/update" | creation 10.4 or 6.9 by definition [#6]; lifecycle margins 1.20 to 5.52 [#35] | the PRF-02 sentence; H1 as a split verdict (decision D-4) |
| 2 | 53, 259 to 260 | H3 against "~100 ms end-to-end"; "10 ms per-message signature-check target" | the identity share f of the interval and P*(0.5) of at least 100, so 0.5 ms per message [`LATENCY_BUDGET.md`]; nothing end to end is measured | the RTV-01 sentence; delete "end-to-end" everywhere (cut list, scope reconciliation section 2.5) |
| 3 | 54 | H4: "the hybrid dominates the fidelity-per-gas frontier" | the hybrid is dominated by ERC-4337 on all six harness criteria [#36]; it stands on the fidelity-per-gas plane among the MOBI backends only | the PRF-06 sentence; H4 and H5 split (D-4) |
| 4 | 55 | H5: "the hybrid sits on it" | as item 3 | as item 3 |
| 5 | 163 to 180 | determinism rests on "fixed signing keys"; "byte-identical gasUsed across all 30 runs is the expected result" | true for the nine-standard benchmark [#25]; the harness has 27 of 110 cells that vary across iterations from per-iteration keys, reported by mode with the range beside [`docs/testing/GAS_CHARTER.md`]; incidental inputs are seeded through `CVIN_SEED`, and an input that is the thing measured is reported as a range over declared seeds [#47; guide 1.1.10] | add the harness paragraph (PRF-03) and the seeding rule; keep 3.3.2 for the benchmark |
| 6 | 284 to 290 | "three injected attacks … exactly 3 × N failures" | five injected attacks per run, 150 failures over 30 runs, all rejected [#27] | "Five attacks are injected per run and every one is rejected; the failure count equals 5 × N [#27]." |
| 7 | 221 to 318 | no freshness window, no replay cache, no re-check cadence, no clock rule | T-9, the freshness-k method, D51 [#21, #32, #37, #52] | new 3.4.6 and 3.4.7 (SEC-02, SEC-03, SEC-04, RTV-03) |
| 8 | whole chapter | no V2I or I2I method | I1 to I5 pre-registered, built, hardened to verifier v3 and measured [#44 to #48] | new 3.4.8 (INF-01 to INF-05) |
| 9 | 326 to 341 | "asserts that it reverts" | DEFENDED requires the documented reason [#28] | the SEC-01 sentence |
| 10 | 321 to 392 | no consent rule for attestation; no chain-id note | C2: owner or `veriKey` delegate, once per event (report 22); ERC-1056 signed operations omit the chain id (D52, threat model G3) | the SEC-05 sentence; one sentence on D52 as a stated limit |
| 11 | 398 | "not a self-scored checklist" | the register calls #4 "internal and self-scored"; the checks test document structure | the STD-01 sentence |
| 12 | 409 to 412 | the resolver as one instrument | C1: with a provider the resolver reads the registry; without one it returns the default document, stated as not read from a chain (C1-d1); the suite and checker inputs resolve without a provider (N-24) | the STD-01 sentence's second half |
| 13 | 450 to 486 | H4 method only | M4 database parity pre-registered and run, with a FAIL half [#33]; M5 pseudonym pool [#38] | new 3.7.3 (STD-04) and 3.5.4 (SEC-07) |
| 14 | 490 to 533 | five threats | missing: the clock rule (D51), host dependence of the knee [#37, #52], in-process back-haul and registry [#46], one host per latency run, the two pins that differ from the runs of record (TDP-008 section 4), the unsalted VIN hash (D64), no RSU-to-RSU path (SC-21) | add each as one bullet, in the order of TDP-009 |
| 15 | whole chapter | no evidence-discipline section | the register, stamps, promote, generated documents, probes, pre-registration protocol (WM-1 report section 3; TDP-002 EVD) | new 3.9 and 3.10 |
| 16 | 41 to 55 | RQ1 to RQ4 in their first-attempt wording | Scope v3 restates each to the evidence (scope reconciliation section 2.2; decision D-1) | replace the table's question column with the restated questions once D-1 is decided |

Items 1 to 4 and 11 are contradictions; the rest are omissions. None requires a new measurement.

## 4. How the recent work enters chapter 3

| Work | Where it stands | Enters chapter 3 as | Not in chapter 3 |
|---|---|---|---|
| WM-2 C1, the resolver reads the chain (report 21) | done at `7ae268a`; #4 and #24 unchanged; chain-backed suite run deferred (N-24) | the STD-01 sentence's second half; a 3.6 provenance line naming the provider argument | the chain-path latency (N-24, a future row) |
| WM-2 C2, attestation consent (report 22) | done; D54 fixed; `attestEvent` execution gas 198,694 [#28]; the testbed copies differ until A3b (N-25) | the SEC-05 sentence in 3.5; one 3.8 bullet for N-25 | the gas delta is a chapter 5 sentence |
| I-24 brief (IDTx) | the mechanism is prior work (guarded transactions, identity-gated transfers); the contribution is the locus-keyed taxonomy and the staleness window; kill criterion to be tied to E-F1-2 and E-F1-3 | one sentence in 3.2.3: "The comparison measures no transaction whose admissibility depends on another identity's state; such identity-dependent transactions are defined and classified in chapter 6 and measured in later work [`docs/phase2/briefs/I-24_IDTX.md`]." | the taxonomy (chapter 6), the positioning (chapter 2) |
| I-05 brief (freshness theory) | the model t_eff(k) = t_local + t_chain / k and k_knee = ceil(t_chain / (0.5 ms − t_local)); predictions committed before the next run | the model stated in new 3.4.7 as the method's model, labelled as fitted to #32 and tested out of sample at the next run; the staleness prediction k − 1 − ((m_pre − 1) mod k) as the per-trial expectation | the predictions' verdicts (a future chapter 5 sentence) |
| Decision sheet (2026-10-20) | 26 open decisions; D-1 to D-15, D-12, N-23 block chapter text | each sentence above that depends on a decision names it: D-1 (item 16), D-4 (items 1, 3, 4), D-12 (the k sentence of RTV-03 states the policy and the host condition together), N-23 (front matter, outside chapter 3) | the decisions themselves |
| Progress report (report 24) | section 4 lists what was measured, re-measured and withdrawn | its withdrawn figures are the ones the drift table replaces; no new sentence | — |
| `tools/prepush_check.sh` (report 24) | the CI document guards, locally | the EVD-05 sentence covers it | — |

## 5. Chapter 3 outline v2 (proposed; the author decides with D-1)

| Section | Content | Requirements carried |
|---|---|---|
| 3.1 Research design | design; Scope v3 questions with their hypotheses stated as split where the evidence splits them; platform with condition tags | SYS-03 |
| 3.2 The comparative framework | the operation catalogue; mapping; n/a never faked; the basic-set coverage; the identity-dependent limit | SYS-01, SYS-04, PRF-07 |
| 3.3 Cost measurement | 3.3.1 exact gas; 3.3.2 determinism for the benchmark; 3.3.3 the public-testnet witness (not run); **3.3.4 the metrics harness** (catalogue, lifecycle, storage, read cost, run identity by tree hash, the gas charter and the seeding rule); 3.3.5 the lifetime model | PRF-01 to PRF-06 |
| 3.4 Message-path measurement | 3.4.1 what is measured; 3.4.2 cold and warm; 3.4.3 the seeded protocol; 3.4.4 injected attacks (five); 3.4.5 mobility and scope; **3.4.6 freshness window and replay**; **3.4.7 revocation freshness: the re-check cadence, the two refresh modes, the model, the clock rule**; **3.4.8 infrastructure messaging: identities, SPaT, I2I, the five pre-registered questions** | RTV-01 to RTV-04, SEC-02 to SEC-04, INF-01 to INF-05 |
| 3.5 Security method | 3.5.1 the strict-reason harness; 3.5.2 taxonomy; 3.5.3 threat matrix; **3.5.4 observability: the pseudonym pool**; the consent rule and the chain-id limit | SEC-01, SEC-05, SEC-07 |
| 3.6 Standards expression | the structural self-score; the external suite; the resolver with and without a provider | STD-01, STD-02 |
| 3.7 Lifecycle profile | the backend sweep; fidelity; **3.7.3 database parity**; the MOBI-VID-inspired wording | STD-03, STD-04 |
| 3.8 Threats to validity | the current five plus the eight of drift item 14, in the order of TDP-009 | SEC-06 and every limit column of TDP-002 |
| 3.9 Zero-knowledge extension | as written: pre-registration, amendments, conditions, the manual-burden method | L5-01 to L5-07 |
| **3.10 Evidence discipline** | register, condition tags, stamps, promote, generated documents, probes, the pre-push guard, no skips | SYS-02, EVD-01, EVD-02, EVD-04 to EVD-06 |
| **3.11 Pre-registration** | the protocol generalised from 3.9 to I1 to I5, M4 and M5; amendments; verdicts as they fell | EVD-03 |

Sections 3.10 and 3.11 are the two the examiner will not find in a conventional methodology chapter and will ask
about first (scope reconciliation section 5, question 15 and the audit's "how do you know your numbers are current").

## 6. What this map does not do

- It edits no chapter: WM-2 D1 pastes the sentences after D-1 to D-15 are decided, in one pass with the stale check.
- It adds no sentence to chapters 5 to 7 beyond naming where a commitment's result or limit belongs.
- It does not restate the IDTx taxonomy or the freshness theory; both have their briefs.
- It carries no number that is not a V row; the two FAIL verdicts and the one outside-band ratio appear because the
  method sentence that reports verdicts as they fell is incomplete without them.

## 7. Revision history

| Rev | Date | Change |
|---|---|---|
| A | 2026-10-21 | initial issue (report 25) |
| B | 2026-10-31 | chapter 3 re-read at `b50864c` (632 lines; 3.1 to 3.8 unchanged, 3.9 added for layer 5); proposed sections renumbered 3.10 and 3.11; section 2.6a for L5-01 to L5-07 and SYS-04; EVD-03 partial; drift item 15 (report 39) |
