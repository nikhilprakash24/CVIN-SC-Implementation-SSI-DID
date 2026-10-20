CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Change Log, Corrections Ledger, and Meta Commentary**

**The record of how this pass was made, what it corrects in the existing programme, what the build settled and what it did not, and an honest account of where the suite is strong and where it is thin**

Document 15 of 16 · Hybrid Data Architecture (HDA) Campaign · Support document (S3) · Suite v1.0 · October 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type B (log, ledger, register) → Admin; §6 is Type C framing and is the document the researcher should read before deciding what of this suite enters the thesis*

---

## 1. Version log entry

| Field | Value |
|---|---|
| Suite | Hybrid Data Architecture (HDA) Campaign, v1.0 |
| Date | 2026-10-04 (brief compiled 2026-09-03; build executed and documents 00, 04, 05, 10, S1, S2, S3 written 2026-10-04) |
| Documents | 16 (00–11 primary, S1–S3 support, 99 companion) |
| Build | `5_minimal-ssi-sandbox/` VID layer, work order WO-V, in `CVIN-SC-Implementation-SSI-DID` branch `vid-build`, **local and unpushed** |
| Code added (WO-V, 10-04) | 5 Solidity files (2 governance, 3 credentials), 2 JS libraries, 2 scenarios, 1 test file |
| Code added (Slice 1, 10-14) | 2 Solidity files (`BatchAnchorRegistry`, `harness/SetCHarness`), 2 JS libraries (`merkle`, `offline`), 3 scenarios (S14, S16, S17), 2 test files, `latencyMs` in the trace emitter |
| Code added (Slice 2b, 10-15) | `lib/vid/bbs.js`, scenario S19, `test/bbs.js`; one new dependency (`@mattrglobal/bbs-signatures` 1.4.0) |
| Code added (Slice 2c, 10-15) | `circuits/AgeGate.circom`, `zk/` ceremony artefacts, `contracts/zk/ZKAgeGate.sol`, scenario S20, tests; four new pins (`circom2` 0.2.8 WASM, `snarkjs` 0.7.5, `circomlib` 2.0.5, `circomlibjs` 0.1.7) |
| Tests | **32 passing** (12 compliance unchanged + 7 VID + batch/offline + Set C harness + BBS+ + ZK) |
| Traces | **11 on file** (2 × S1, 2 × S7, 2 × S8, S14, S16, S17, S19, S20 — S7/S8 duplicated because they were re-emitted under schema v1.1) |
| Findings | **F-VID-1 to F-VID-18** (`docs/FINDINGS.md`); 8–11 from Slice 1, 13–14 from Slice 2(b), 16–17 from Slice 2(c) |
| Corrections raised | K-HDA-1 to K-HDA-19 (§4) |
| Slice status (00 §7) | Slice 0, **Slice 1 complete** (1a–1e), **Slice 2 complete except (d)** — (a) salted digests in repo, (b) BBS+, (c) Groth16 predicate with on-chain verification. Open: 2(d) anoncreds-rs (Rust/Python FFI; needs a repository decision); Slice 3 (other options, Besu); Slice 4 (hardware) |
| Interface changes | **None.** `IMinimalSSI`, `ISetA/B/C`, `O1_ERC1056` byte-identical to canon v1.3 |
| Open decisions | D1–D8 (00 §8) |

**What changed in the programme's state.** Before this pass the programme had one measured scenario (S1, architect pass, June) and no implementation of the specification's §6 governance extension. After the 2026-10-04 pass it had four traces, a measured governance and typing layer, a first operator-machine rerun of S1, seven findings of which two are specification errata candidates, and a sixteen-document argument for data placement as the thesis's organising axis.

**After Slices 1 and 2 (2026-10-14/15) it has substantially more**, and the shape of the gain is worth stating because it is not what the pass set out to produce: eleven traces, thirty-two tests, eighteen findings, and — the part that matters — **all three disclosure paths measured on the same credential** (hash, BBS+, Groth16 predicate), which is the comparison the thesis's central finding about `createPresentation` has always needed and never had. Two of the suite's standing digest-level quantities have been retired by measurement (the Groth16 gas range, K-HDA-6) or contradicted by it (the VehiclePassport timing, §6.4). It also has, for the first time, a written account of what it cannot yet claim (§5), and that account has now been corrected three times by its own builds, which is the account working as intended.

## 2. How this pass was run, and why in that order

The pass was organised against the programme's known failure mode, which the September cross-verification identified plainly: documents that outrun their evidence. Five steps, in this order, each chosen to make the next one harder to fake.

**Step 1 — compile a single verified brief before writing anything.** `_CONTEXT_BRIEF.md` was assembled from the programme's own files (specification, canonical sandbox v1.3, narrative synthesis and content registry v11.3, three supervisor memos, the 2020 CVIN paper, the suite-architecture convention) and fixes the vocabulary, the twelve-function semantics, the measured numbers, the writing rules, and the reference numbering. Its most consequential clause is rule 1: real numbers come only from the brief §5 or from a trace the author has read. Every document in the suite was written against it, and the brief is the reason the suite's unverified quantities are labelled rather than laundered.

**Step 2 — write the nine analysis and scenario documents.** 01 (placement), 02 (proofs), 03 (hybrid), 06–09 (scenarios and the federated-learning argument), 11 (thesis integration), 99 (primers). At this point the build did not exist, so these documents treat S7 and S8 as pending and cite only the S1 trace. They were written in parallel, which is the origin of the identifier collisions in §4.

**Step 3 — build the smallest thing that could falsify the argument.** The placement argument predicts three specific things: that credential content can leave the chain without losing verifiability, that batching changes cost by the batch factor, and that entitlement is absent from the twelve functions. A minimal VID layer with endorsement was built to test those three predictions rather than to demonstrate a product. All three were confirmed, and five further findings emerged that nobody had predicted (§3).

**Step 4 — write the build record and the front door against the real numbers.** 10 reports only what code produced. 00 maps every demand to its answer and states what the pass cannot claim. 04 and 05 were written last, after the measurements existed, and are the only scenario documents that cite measured figures natively rather than through a post-build note.

**Step 5 — reconcile rather than rewrite.** The nine step-2 documents were **not** rewritten after the build. Each received a post-build note pointing at 10 §5 and at §3 below. This was a deliberate choice and it is the most criticisable methodological decision in the pass; §6.3 argues both sides.

One process note on provenance. The canonical sandbox's standing rules route unplanned scope to a proposals file, not to code. This build was operator-directed and is logged in `BUILD_LOG.md` as WO-V with that provenance; `BUILD_PLAN.md` was left untouched so that the architect can ratify or re-scope it (decision D2). The rules were bent knowingly and the bend is recorded, which is the behaviour the rules exist to produce.

## 3. Pre-build and post-build reconciliation

This is the table the post-build notes in 01, 02, 03, 06, 07, 08, 09 and 11 point to. Each row states what the document assumed while the build was pending, what the build settled, and what still stands unsettled. Where a row says a claim is *unchanged*, that is a statement that the measurement did not bear on it, not that it has been confirmed.

**Verification note on this table.** It was compiled from each document's post-build note, from 10 §5–§6, and from sampled sections of the nine documents — not from a complete re-reading of all nine. Rows marked ⚠ are the ones a complete re-reading should check first, because they are where a pre-build sentence is most likely to have been left in a form the measurement now contradicts.

| Doc | Assumed while pending | Settled by the build | Still unsettled |
|---|---|---|---|
| **01** On/off-chain and anchoring | Cost model's batching prediction (anchor write constant in leaf count) was a formula; per-credential off-chain sizes were estimates; placement columns for O1 derived from the S1 trace only | **Batching confirmed at 11:1**, exactly the batch size (10 §5.3) — the cost model's central prediction. **Off-chain credential sizes measured** at 813–850 bytes against a 32-byte anchor. **Zero-chain-read verification demonstrated** (S7 seq 32–34). On-chain typing priced at 150,463 gas, which the document had not costed at all | Cross-option placement (O2–O8); rollup and blob multipliers; the per-credential-hash GDPR question; ⚠ any sentence that gives a dollar figure rather than a ratio |
| **02** ZKP and verifiable data | All proof costs digest-level; the salted-digest path assumed realisable | **Salted-digest selective disclosure built** in `lib/vid/credentials.js` and exercised in S8 — stage (a) of its own roadmap is done. **The `birthYearCommitment` hook exists** in the licence credential, so the age-predicate example is now anchored in a real object | *As of 2026-10-04:* **no zero-knowledge proof was generated or verified**; stages (b)–(d) all open. **Stages (b) and (c) settled 2026-10-15.** (S19) BBS+ generated, sized, verified, unlinkable, timed — and it refuted 05 §3.2's "cryptography is not the problem" (§6.4). (S20) Groth16 range predicate proven and verified on-chain at 250,283 gas, retiring K-HDA-6's borrowed range and reframing the cost question from verifier gas to prover placement. All three disclosure paths are now measured on one credential. **Still open:** stage (d) AnonCreds comparison and accumulator revocation privacy; the warm verification figure (§5.1 item 3a) |
| **03** Hybrid design | Anchor·Cache·Attest·Reconcile was a design; staleness windows were parameters; degraded modes were specified | **Cache staleness is now an observation, not a parameter**: a cached verifier accepted a revoked credential and needed a refresh to correct itself (F-VID-3, S7 seq 50–51). **The attest and anchor verbs are built.** The batching trade-off is priced | **Reconcile is unbuilt** — the delayed-write rules of §3.3 remain a design (S14). Revocation-storm behaviour (S18); finality depths; the policy-selected disclosure case (S19); ⚠ §3.3's claim that the rules are implementable |
| **06** Reputation, payment, access, connectivity | Set C costs were targets; the gated-access offline path assumed workable; batched receipts assumed cheap | **The offline verifier path is demonstrated** (rung 0, zero chain reads). **Batched anchoring priced.** **Endorsement-revocation semantics measured**: F6 valid while G4 false (S7 seq 53), which the access designs depend on | *As of 2026-10-04:* **Set C is interface only** — every C1–C4 figure in the document is still a target; delayed-write reconciliation unbuilt. **Both settled by Slice 1** (§3.1): the harness supplies C1–C4 (harness costs, not ERC-8004 costs) and S14 demonstrates reconciliation with "revocation wins". ⚠ The §3.2 anchoring-granularity rule (no per-passage anchors with the vehicle as subject) forbids a pattern the earlier catalog may have intended; the document's own open question 4 asks whether the catalog entry should be revised |
| **07** Beyond-CAV back-end systems | Licence and registration credentials were designs; the deed and repair-history analogies rested on them | **The licence and the registration are built and measured** (825 and 850 bytes; registration anchored with on-chain expiry at 150,087 gas; T1 declared at 150,463). **Repair history is built** as the eleven-type lifecycle family with transitive endorsement. The document's central analogy now rests on executed code rather than on design | Deeds, corporate registries, legacy-integration adapters: all designs (S15). The archival-issuer policy that a deed or a birth certificate needs is **surfaced but unresolved** (F-VID-2, decision D5) |
| **08** I2I secure communication | The channel was specified; revocation propagation was the named crux | **Replay prevention measured**: a reused presentation challenge reverts (S7 seq 45). **The off-chain channel steps appear in traces** as `kind=offchain`, which is the architectural demonstration the memo asked for. **The revocation-propagation crux is now evidenced** rather than asserted, by F-VID-3 | Propagation *latency* — the quantity that would fix the staleness bound — is unmeasured and needs Besu plus hardware. Mid-session teardown at scale; the push-infrastructure design |
| **09** Reputation, identity, federated learning | The chain FL→reputation→identity→this-system was an argument; the Sybil-cost claim rested on endorsement being realisable | **Endorsement is realisable and priced** (151K–183K per issuer per type, amortised — F-VID-4), so the Sybil-cost premise is no longer hypothetical. **F-VID-7 is the strongest support the argument received**: F5 is issuer-agnostic, so without endorsement anyone can anchor anything and reputation has nothing to bind to | The **toy federated round with Sybil injection (S16) was not built**, so the central claim remains an argument. Needs the Set C harness first (00 §7 step 1d). Byzantine-aggregation figures stay DIGEST-LEVEL |
| **11** Thesis integration | §5.3's narrowed-claim sentences were written for claims with no evidence | **Three narrowed claims are now dischargeable**: VID-layer realisability, endorsement gating verified on O1, and the trace-length correction. The endorsement argument of §2 gained its empirical anchor in F-VID-7 | The Tier 2 latency claim, the cross-option claim, and the ZKP cost claim **must stay narrowed**. ⚠ §5.4's "today versus after the build" split is now out of date in the document's favour and should be rewritten before any committee use |

**The one row that is not merely additive.** For 03 and 06, the build did not only supply numbers; it changed the status of the staleness window from a design parameter to a demonstrated failure. Before S7 seq 50, "the cache may be stale" was a caveat. After it, stale acceptance is something the system was observed doing, and every document that relies on a cached read path is relying on a mechanism whose failure mode is on record. That is a strictly better position to argue from and a strictly worse one to gloss over.

### 3.1 Slice 1 addendum (2026-10-14)

After this section was written, Slice 1 of 00 §7 ran: S17 batch anchor (anchorBatch 122,139 gas; A/B 11.00, A/C 11.72), S14 delayed write (3 queued, 1 rejected by revocation-wins, 1 write on reconnect), latencyMs instrumentation (schema v1.1, lower bound only), the Set C harness (not O7), and S16 (GATED weighted error 1.87 vs UNGATED 27.59, toy model). Findings F-VID-8 to F-VID-11. Test suite 26 passing; eight traces. Pre-build statements in 01 §7 (g_a estimate), 06 §5/§7 and 09 §9 (scripts pending) are superseded by 10 Addenda A and B.

### 3.2 Slice 2 addendum (2026-10-15)

Stages (b) and (c) of 02 §10 ran: S19 BBS+ selective disclosure (proofs 384–640 B, laptop ~60–116 ms, F8 commitment unchanged at 62,470 gas) and S20 Groth16 age-gate predicate (256-constraint circuit; **on-chain verification 250,283 gas** including replay flag and event; prove ≈4.0 s, off-chain verify ≈0.65 s, laptop cold start). Findings F-VID-12 to F-VID-18. Test suite 32 passing; ten traces. Consequences for the pre-build documents: 02 §2 and §9 now have one measured verifier point (K-HDA-6 partly dischargeable); 05's Tier 2 budgets must treat prover placement, not verifier gas, as the binding term; 01 §8's F8 row gains the split "proof off-chain, commitment on-chain, optional ≈250K on-chain admit". Stage (d) anoncreds-rs not started.

## 4. Corrections ledger (K-HDA-1 to K-HDA-21)

K-HDA-1 to K-HDA-7 are raised in 11 §5.2 against the existing programme documents and are reproduced here in one line each; the full statements are in 11. **K-HDA-8 to K-HDA-19 are raised by this suite against itself or against the programme's own records** — eight of the twelve were found not by reading but by merging or by building, which is the §6.5 point in evidence. All nineteen are provisional numbers pending merge into the programme's K-ledger.

| # | Target | Correction | Raised in | State |
|---|---|---|---|---|
| K-HDA-1 | Synthesis v11.3 §3.1; registry Ch.5 | Family F is a Stage 3 **data-architecture** specification realisable over more than one contract set, not a composite assembled from the best components; never a Stage 1 sandbox | 11 §5.2 | Open |
| K-HDA-2 | v11.3 §4.4 | The 75K `createDID` figure is the ERC-1056 reference registry's `setAttribute` cost (DIGEST-LEVEL) and is a **target**; measured O1 is 161,823–178,935. Keep the Canadian-scale estimate as a formula, not a dollar figure | 11 §5.2; **now confirmed by 10 §5.2** | Open; evidence in hand |
| K-HDA-3 | Thesis draft Table 4.1 vs sandbox | Two incompatible O-numbering schemes. Until one is chosen, name the standard, not the number | 11 §5.2 | Open (decision owed) |
| K-HDA-4 | v11.3 §2.3 | AnonCreds v1 uses CL signatures, not Groth16; §3.2 is already correct and §2.3 contradicts it | 11 §5.2 | Open |
| K-HDA-5 | Content registry | The O1 trace is 22 entries, not 18 | 11 §5.2; **confirmed by 10 §5.1** | Dischargeable now |
| K-HDA-6 | v11.3 §3.2 | Groth16 verification ≈200–350K gas is DIGEST-LEVEL with a range and a source, not a fact | 11 §5.2; **measured 2026-10-15** | **Dischargeable with a measurement.** S20 gives 250,283 gas for `admit` on a two-signal bn128 circuit inclusive of a storage write — a point at the low end of the quoted range, so the range was right and was being asserted for the wrong reason. The suite can now state a measured figure with its circuit and its conditions instead of a borrowed range |
| K-HDA-7 | v11.3 §4.4 | Endorsement is a **cross-family** property available beside any option; Indy is the native instance, not the only one | 11 §5.2; **strengthened by the build**, which realised it on an EVM option | Open; evidence in hand |
| K-HDA-8 | This suite, documents 01, 03, 06, 07, 09 | Several documents independently proposed the identifier **"S9"** for different scripts. The canonical register in 00 §6 governs (S9 = CAV full coverage; the others renumbered S14–S18) | 00 §6 | **Resolved by the register**; per-document text not rewritten |
| K-HDA-9 | This suite, 00 §6 and 05 | The register lists the six tier scenarios as **"T1/T2/T3-CAV, -AGT"**, colliding with the typing tags T1 `declare` and T2 `verifyTyped` used in 04, 05 and 10. 05 writes them **TS1/TS2/TS3** with `-CAV`/`-AGT` suffixes | 05 (notice 2) | **Resolved in 05**; 00 §6 register row should be updated |
| K-HDA-10 | This suite, documents 01, 02, 03, 06, 07, 08, 09 | The per-document **`NEW-n` source series collide across the suite** in at least eleven places: `NEW-1` is the Bitstring Status List in 01/03/06/08, GDPR in 02, eIDAS 2.0 in 07 and McMahan's FedAvg in 09; `NEW-2` and `NEW-8` and `NEW-11` each collide four ways. No document is wrong internally; the suite is unusable as a corpus | S1 §1 | **Resolved in S1**: merged H1–H48 numbering plus the `NEW-n` crosswalk in S1 §6 |
| K-HDA-11 | v11.3 §4.1 | Describes sandbox v1.1 as Hardhat and Foundry with a Besu QBFT node; the sandbox on file (v1.3) is Hardhat only on the Hardhat network, Besu planned (WO-8) | 11 | Open |
| K-HDA-12 | Master Document Index §C; Audit Playbook sheet 0.1 | Names `CVIN-ID/CVIN-ID-SCs` as the sandbox repository; that repository (last push Aug 2024) holds the older per-standard folders. The sandbox exists as the v1.3 zip extraction and, from this pass, in `CVIN-SC-Implementation-SSI-DID` branch `vid-build` | 00 §9; S3 §6.5 | Open — decision D1/D2 |
| K-HDA-13 | Spec §5.3 reading in brief §3 | createDID is not the only O1 target miss: deactivateDID (55,127 vs <50K) and issueCredential (130,151–150,099 vs <120K) also miss | 10 §5.2; sandbox FINDINGS | Dischargeable now |
| K-HDA-14 | 01 §3, 03 | Cite [12] (Camenisch–Lysyanskaya CRYPTO 2004, CL signatures) for accumulators; accumulator-based revocation is Camenisch–Lysyanskaya CRYPTO 2002 (new source for S1) | 02; S1 | Open |
| K-HDA-15 | 00, 10, S2, BUILD_LOG (first issue) | S1 rerun first recorded as 2026-10-04; the rerun trace is dated 2026-09-03 local. Corrected in all four | — | Discharged |
| K-HDA-16 | 01, 03, 05, 06, 08; lib/vid | The staleness window is named W, τ and W_max across documents and its Tier 2 default differs (03: 300 s; S7/S14 scripts: 60–120 s). One symbol and one declared default owed; neither is a measurement | 03 §3 | Open |
| K-HDA-17 | 01, 06 | VehiclePassport (arXiv:2509.06133) timings used as realisability evidence; one preprint relayed through the brief — UNVERIFIED context, not a bound | S1 debt list | Open |
| K-HDA-18 | 01 §7 Table 7.2 | Batch-anchor write estimated at 60,000 gas; measured anchorBatch 122,127–122,139 and root-via-F5 130,151–130,163 (S17, 10 Addendum A). Table 7.2 configuration C/D ratios overstate the saving by ≈2× | 10 Addendum A; FINDINGS F-VID-8 | Dischargeable now |
| K-HDA-19 | 00 §6 register (first issue), 04, 06, 09 | S14, S16, S17 listed as designs; built 2026-10-14 with traces (10 Addenda A, B). ISetC lacks a validation-response write (F-VID-11) — 04's finding confirmed in code | 00 §6 (updated); 06 §7, 09 §9 | Dischargeable now |
| K-HDA-20 | v11.3 §3.2; 02 §2–§3 | Groth16 verification "≈350,000 gas" / "≈200–350K": first measured point 250,283 gas for a 2-signal circuit incl. storage write and event (S20). State as measured with its scope; the bare pairing cost was not isolated | 10 Addendum D; FINDINGS F-VID-15 | Partly discharged |
| K-HDA-21 | 05 (tier budgets); 02 §9 | Cost models weight verifier cost; measured prover cost (≈4 s cold, laptop) exceeds verifier cost by two orders of magnitude. Rewrite Tier 2 budgets around prover placement | 10 Addendum D; F-VID-16 | Open |

**Disposition.** One is discharged (K-HDA-15). Three are resolved in the documents themselves (K-HDA-9 in 05, K-HDA-10 in S1, and K-HDA-19 in 00 §6 plus the Slice-1 notes added to 04 and 05 on 2026-10-15). Five are dischargeable immediately from artefacts already on disk — K-HDA-5, K-HDA-2's evidential half, K-HDA-13, K-HDA-18 and the remainder of K-HDA-19 — and the only thing standing between them and discharge is someone editing the canonical documents. Ten remain open, of which K-HDA-3 (O-numbering), K-HDA-12 (which repository is the sandbox) and K-HDA-16 (one symbol and one default for the staleness window) need a decision rather than work.

K-HDA-8 is resolved by fiat rather than by correction, which is a compromise: the register governs, but a reader of 03 §3 will still meet an "S9" that means something else. K-HDA-9 and K-HDA-10 are the same problem caught later and fixed properly — in the documents, not only in the register — which is the better pattern and is what a second pass should do for K-HDA-8.

**The pattern across the ledger.** Five of the nineteen (K-HDA-2, 13, 18, 19, and half of 7) are cases where the programme **stated a hypothesis as a result and the build then contradicted the figure** — the 75K `createDID`, the unnoticed `deactivateDID` and `issueCredential` target misses, the 60,000-gas batch-anchor estimate that measured twice that, the scenarios listed as designs after they were built. That is not a drafting problem; it is the signature of a programme whose documents run ahead of its measurements, and it is the same diagnosis §6.5 reaches from the other direction. The corrective is mechanical: **no quantity enters a canonical document without a label, and every labelled target is revisited when the corresponding measurement lands.**

## 5. Unresolved items, verification debt, and the next pass

### 5.1 What is owed, by kind

**Measurement debt (nothing in the suite can discharge it; only code can).**

*Updated 2026-10-15 after Slice 1. Four of the seven moved; the three that did not are the three that need a new dependency or new hardware.*

| # | Owed | Blocks | State after Slice 1 |
|---|---|---|---|
| 1 | Any latency figure at all | Every tier claim in 05, 03 §3.4, 06, 08 | **Instrumented, not measured.** `latencyMs` landed as additive schema v1.1; S7/S8 re-emitted; S14/S16/S17 timed from birth. Hardhat values are a lower bound and are not results. **Open sub-item, and the cheapest thing left in the programme: nobody has extracted the non-network component bound from the traces already on disk** (05 §7 step 2, 05 open question 5) |
| 2 | Set C costs (C1–C4) | 04 §2.7–§2.8 and all of §3; 06 §2; 09 §9 | **Discharged for mechanism, open for comparison.** The harness gives C1 at 83,493–117,693 gas, explicitly *not* ERC-8004 costs. Comparison against O7 still needs O7 |
| 3 | One generated zero-knowledge proof | 02's quantitative half; 03 §7 | **Discharged for stages (b) and (c), 2026-10-15.** (S19, F-VID-13/14) BBS+ generated, sized, verified, unlinkable, timed — it produced the suite's first self-contradiction (§6.4). (S20, F-VID-16/17) A Groth16 range predicate proven and verified on-chain at 250,283 gas, retiring K-HDA-6's borrowed range. **Open:** stage (d) anoncreds-rs and accumulator revocation privacy |
| 3a | **The warm Groth16 verification time** (new, 2026-10-17) | Whether predicate proofs are usable at Tier 2 at all (05 §3.2.1) | **The cheapest decision-relevant measurement in the programme.** 645.3 ms is a cold snarkjs first call; if the warm figure is tens of milliseconds, the pre-computation placement rescues predicates for gated access, and if it is not, predicates are Tier 3 only. One benchmarking line against artefacts already on disk |
| 4 | Delayed-write reconciliation behaviour | 03 §3.3; 06 §5 | **Discharged** (S14, F-VID-9): queue, reconcile, "revocation wins", zero writes during outage, one on reconnect. The link model is a flag in a script, not a network |
| 5 | On-chain Merkle inclusion | 01 §11; 04 §2.6 batching's on-chain half | **Discharged** (S17, F-VID-8), and it corrected 01 §7's estimate by ≈2× (K-HDA-18) |
| 6 | Cross-option placement (O2–O8) | 01's comparison columns; the "beside, not inside" argument's strongest form | **Unchanged.** WO-1 ports, then one controller adapter per option. Now the biggest single lever on the thesis's existing contributions |
| 7 | Revocation-propagation latency | The staleness bound that 05 §5 says couples every tier | **Unchanged.** Besu QBFT (WO-8), then hardware. S14 sharpened *why* it matters without measuring it |
| 8 | **Attenuated delegation** (new, 2026-10-15) | 04 §3.5, §4; the C14 agent wrapper's security story | **Not in any slice plan.** The only structural gap left in either full-coverage scenario (04 §5). A registry beside the interface, shaped like the endorsement registry |

**Source debt (readable without code; the suite's own labels name it).** IEEE 1609.2-2022 is cited but was not read at source — 05 §2 depends on it for the SCMS boundary and labels it UNVERIFIED. The Groth16 and VehiclePassport figures, the Byzantine-aggregation literature, the Sybil and EigenTrust references, the vehicle-population figure, and the rollup economics are all DIGEST-LEVEL. The programme's cumulative R-series numbering lives in the Systematic Review v13.1 suite, which was not on this machine, so S1 uses provisional identifiers (H1–H48) pending merge. **S1 has since been written** (§5.3), and its §5.1 is now the authoritative source-debt register: eleven claims that are load-bearing and not read at source, with a four-session reading list in S1 §5.2. Slice 1 did not touch any of them — it added eight artefacts and no readings, so the asymmetry between verified code and unverified premises is now wider than when it was first noticed.

**Decision debt.** D1–D8 in 00 §8. Two cannot wait: **D1**, because the entire build exists on one unpushed branch on one disk, and **D7**, the empirical cut-line, because every sentence in Chapters 4 and 5 about tiers and proofs depends on where it falls.

### 5.2 Order for the next pass

*Rewritten 2026-10-15. Items 2, 3 and 4 of the original list were executed as Slice 1 on 2026-10-14 and are struck through; what follows is the list as it now stands.*

1. **Push the branch** (D1). Still first, still not research, and now more urgent: eight traces, eleven findings and 154,000 words exist on one disk. It has been the top item on this list through two work sessions without moving.
2. ~~Trace schema v2, then re-emit S1, S7, S8.~~ **Done** (Slice 1c), as additive v1.1. **Residue, and the cheapest item on this list: read the timings already recorded** and state the non-network component bound. An afternoon on data on disk.
3. ~~Set C harness, then S11 and S16.~~ **Done** (Slice 1d, 1e). It did what it was predicted to do and more: 09's central chain is now observed, and the ungated configuration turned out to be *worse than no weighting at all*, which no document in the suite had predicted (§6.4).
4. ~~S14 and the Merkle verifier.~~ **Done** (Slice 1a, 1b), and the Merkle result corrected an estimate in 01 §7 by about a factor of two.
5. **Read the four sessions of S1 §5.2**, starting with IEEE 1609.2 and Brecht et al. **Promoted to second place in substance.** Slice 1 widened the gap this addresses by adding artefacts and no readings, and the first session settles whether the thesis's problem statement — the accountability gap and the Tier 1 boundary — is correctly stated. Everything below is optional; this is not.
6. **Build the attenuated-delegation registry** (debt item 8). Small, closes the last structural gap in 04, and it is a contribution candidate rather than plumbing — but 04 §4 flags that the finding should be adversarially checked against the interface *before* it is built, not after.
7. **Then choose**: Slice 2(b) proofs, or WO-1 ports (Slice 3) for the cross-option argument. The ports strengthen the thesis's existing contributions and would let the "beside, not inside" claim be *demonstrated* rather than argued, by running the unchanged VID layer on a second option; the proofs open a new contribution and close the suite's largest remaining gap. 00 §8 D8 is that choice, and Slice 1's experience is mild evidence for taking the cheaper, more certain option first.
8. **Merge the H-series into the programme's R-series**, and apply the five dischargeable K-corrections (§4) to the canonical documents. Pure bookkeeping, and §6.5 is about why it keeps not happening.

### 5.3 What S1 added after this section was first drafted

This section originally recorded that S1, the weighted reference index, had not been written — it was the last document of the pass and the only one with no argument in it. It has since been written, and it did not merely tidy the bibliography; it produced two findings that belong in this log.

**K-HDA-10**, the `NEW-n` collision (§4), which made the suite unusable as a corpus and was invisible from inside any single document.

**The eleven exposed claims** (S1 §5.1): the sources that are load-bearing *and* not read at source. The pattern S1 found is the one this document should have predicted and did not. Four of the eleven — IEEE 1609.2, Brecht et al. on SCMS, MOBI VID I–II, and the AnonCreds specification — are the sources that define *what the thesis is about*: the Tier 1 boundary, the accountability gap, contribution C4's conformance mapping, and the Set B coverage ceiling against which the thesis's central finding is stated. None was read at source in this campaign. **The pass verified its own code thoroughly and its own premises hardly at all**, which is the inverse of the programme's usual failure and is arguably worse, because code can be re-run while a misread premise propagates silently into sixteen documents.

S1 §5.2 orders the remedy into four reading sessions, and the first of them — 1609.2 and Brecht — now outranks everything in §5.2's own next-pass plan except pushing the branch. §5.1 above remains the measurement-debt register; **S1 §5.1 is the source-debt register**, and 00 §5's pointer to "S1's verification-debt list" now resolves correctly.

## 6. Meta commentary

### 6.1 What this pass actually is

It is one build and a great deal of writing. The proportion is the first thing an honest reader should be told: roughly 140,000 words of argument rest on five Solidity files, two JavaScript libraries, nineteen tests, and four trace files, all on one option, on a local EVM, with no latency measured and no proof generated. Any reasonable supervisor's first question is whether the writing earned its length, and the defensible answer is: *in three places yes, elsewhere not yet.*

The three places are the data-placement axis (01 and 03), the endorsement argument (11 §2, built in 10), and the reputation-needs-identity chain (09). Each of those is an argument the thesis did not previously have in unified form, each reorganises material the thesis already contains rather than adding speculation to it, and two of the three now have measured anchors. Everything else in the suite is scaffolding of varying quality: useful for writing the thesis, not itself a contribution.

What makes this pass different from the programme's past failures is not restraint in volume — there was none — but that the labels hold. The brief's rule 1 was enforced, so a reader can tell at a glance which numbers are measured, which are digest-level, and which are budgets. A suite that is too long but honestly labelled is recoverable by deletion. A suite of the right length with laundered numbers is not.

### 6.2 Where the argument is strongest, and where it is thin

**Strongest.** F-VID-7 — F5 is issuer-agnostic, anyone can anchor anything, and F6 will call it valid — is the best single result of the pass, because it is a negative finding about the thesis's own central artefact, discovered by building on it, and it immediately justifies a design response that was already named in the specification's §6 but never implemented. An examiner asking "what did you learn that you could not have reasoned out in advance" has an answer. The 11:1 batching ratio is the second strongest, because it is exact, predicted by the cost model, and carries a real trade-off rather than a free win. The third is the measured staleness failure, for the reason given in §3.

**Thin.** The latency material. Five of the sixteen documents lean on the three-tier framework, and not one timing figure exists anywhere in the programme. 05 is written as a set of budgets precisely so that it degrades gracefully rather than collapsing, but a reader who wants to know whether Tier 2 is achievable will not find out, and the suite should not pretend that an argument about read paths substitutes for a measurement. The ZKP material is thin in the same way and is more honest about it, because 02 states its own staged plan and the stage that is done is the cheap one.

**Thinner than it looks** (as first written). The agent material. It is extensive, internally coherent, and rests on *no execution at all* — Set C was not built, so every agent scenario in 04, 06 and 09 is a design whose cost profile is assumed. The agent half of the thesis (C14, C15, Chapter 5 §5.2) is the part of this suite most likely to attract a question it cannot answer, and the smallest thing that would change that is the harness in §5.1 item 2.

*Revised 2026-10-15.* The harness was built, and this paragraph was right about the diagnosis and wrong about the cure's reach. C1–C4 now execute and S16 exercises them in a real sequence, so the agent material is no longer unexecuted. But the harness is explicitly not O7: it has no agent NFT and no ERC-8004 fidelity, and its gas figures must not be cited as ERC-8004 costs. So the agent half can now be *demonstrated* and still cannot be *costed*, and the exposure has moved rather than closed — from "none of this runs" to "this runs on a stand-in for the standard it claims to follow". The thing that would close it is O7 itself, which is a WO-1 port and sits in Slice 3. Meanwhile the harness found F-VID-11, which is a point in favour of building stand-ins early: it surfaced an interface gap that three documents had written around without noticing.

**Possibly wrong rather than merely unproven.** Two things. The claim that the VID layer is implementation-agnostic "by construction" is an argument from how the code was written, not an observation; it runs on one option and the controller-adapter indirection is exactly where such claims usually fail. And the attenuation finding in 04 §3.5 asserts that F11 is insufficient for chained delegation — that is a reading of the interface, made by one author in one pass, and it should be attacked before it is published.

*Resolved for the first of the two, 2026-10-17 (10 Addenda E–J).* The implementation-agnosticism claim was the one this log said should be distrusted, and it was then tested the hard way: **O2–O8 were ported and all eight options admitted the layer 12/12 unmodified, with S1, S7 and S8 running unchanged on each.** The suspect indirection — the controller adapter — held across an ERC-721 soulbound token, an ERC-1155 balance, an ERC-4337 smart account with session keys, two ERC-725 variants, the ERC-8004 registries, and an Indy-on-Besu layout that does not store a per-credential hash at all. The claim survives, and it survives as an observation rather than an argument. That is the single strongest piece of evidence the "extend beside, never inside" method has produced, because the method's whole promise is portability and portability is now measured on eight substrates rather than asserted from one.

Two things follow that are worth more than the vindication. First, **the suspicion was correct practice even though the claim turned out true** — flagging it cost a sentence and buying the test cost a work order, and the programme now has a result instead of a hope. Second, the port produced the finding the single-option build could not have: the coverage ordering and the gas ordering **rank the eight options differently** (ERC-725xy and Indy lead on coverage, ERC-1056 and ERC-721 on gas — F-WO5-4), so neither matrix alone ranks the standards, and the thing that reconciles them is the placement axis this suite exists to argue. Document 01's thesis was confirmed by an experiment designed to test something else, which is the best kind of confirmation available.

The second item, attenuation, is **still open and still should be attacked.** Nothing in the eight-option work touched it; it remains one author's reading of the delegate-grant semantics. Its status is unchanged by everything since.

### 6.3 The decision not to rewrite the nine pre-build documents

This is the pass's most criticisable methodological choice and it deserves both sides.

*For.* Rewriting nine documents after a build that touched a small part of each would have consumed the pass's remaining capacity and would have destroyed the one thing that makes the reconciliation legible: the distinction between what was predicted and what was found. A document that was written before the measurement and then silently updated to agree with it is evidence of nothing. The post-build notes plus §3 preserve the prediction and record the outcome, which is the stronger epistemic position and is the same discipline the gate-and-trace method applies to code.

*Against.* It leaves nine documents containing sentences that a reader will meet before they meet the note, and the rows marked ⚠ in §3 are the places where such a sentence is most likely to say something the measurement contradicts. The compromise is asymmetric in a way that favours the author: the burden of reconciliation has been moved onto the reader. For internal working documents that is acceptable. For anything shown to a committee it is not, and the rule should be that **no document goes to a supervisor with a post-build note still standing** — it is either rewritten or it is not sent.

### 6.4 What the build changed about the argument, and what it did not

It changed three things. The placement argument acquired a measurement at its centre rather than a formula. The endorsement argument acquired a reason to exist that is not aesthetic: without it, F5 is a free-for-all. And the staleness window moved from caveat to observation.

It changed nothing about the two claims the suite most wants to make. That the hybrid is *realisable at scale* remains unevidenced, because one option on a local EVM says nothing about scale. And that the tiers are *achievable* remains unevidenced for the reason §6.2 gives. The honest summary is that the build confirmed the suite's design reasoning about **where data goes** and left untouched its reasoning about **how fast the system is** — which maps exactly onto the division between what gas can measure and what it cannot.

**What Slice 1 then changed (2026-10-15).** Three of the four Slice 1 results confirmed what the documents predicted: reconciliation is implementable, on-chain inclusion is recoverable, Set C executes. One did not, and it is the most interesting thing the programme has produced to date. The S16 experiment was designed to show that reputation suppresses Sybils when identity is endorsement-gated, and it did — weighted error 1.87 against 23.67 unweighted in that configuration. It also showed that **without the gate, reputation-weighting is worse than not weighting at all**: 27.59 weighted against 24.35 unweighted in the ungated configuration, because the Sybils manufacture their own standing and the aggregator then trusts them more than it would have by default. No document in this suite predicted that, and it converts 09's argument from a chain of plausible necessities into something sharper — *reputation without Sybil-resistant identity is not merely insufficient, it is actively harmful.* A reader can decline the claim that identity is **needed** for reputation far more easily than the claim that reputation without it **inverts**. The magnitudes are a toy model and the Sybil fraction was chosen, so what is defensible is the ordering, not the numbers; but the ordering is the claim.

**What Slice 2(b) then changed (2026-10-15), and why it matters more than its result.** BBS+ selective disclosure was built and measured: proofs of 384–640 bytes, generated in 93–116 ms and verified in 59–116 ms on a laptop in WASM (10 Addendum C). The result is useful — the proof layer is orthogonal to the anchor, unlinkability is observed rather than argued, and the issuer key is an ordinary F9 verification method. But the important thing is what it did to an argument this suite had already made.

Document 05 §3.2 had concluded, on the strength of the one external figure available (VehiclePassport, 22 ms generate, sub-5 ms verify), that "the cryptography is not the problem — comfortably inside the budget", and had located the Tier 2 engineering risk in session setup and node locality instead. The suite's own measurement is **4–5× slower**, which puts the most selective policy at 232 ms of a 500 ms Tier 2 allowance before anything else is spent, and makes it unfittable at the 100 ms end of the tier. 05 §3.2 now withdraws that sentence for the ZK path and keeps it only for the signature-plus-digest path the build actually defaults to.

**This is the first time in the programme that the suite's own measurement refuted the suite's own argument**, and it is worth dwelling on for three reasons. First, it is the clearest possible vindication of the brief's rule 1: because the 22 ms figure had been carried as DIGEST-LEVEL with its source named, the refutation is a clean correction rather than an excavation — nobody has to work out where the number came from. Second, it inverts an exposure that S1 §5.1 had catalogued: item 3's risk was that an unread source might not support the claim resting on it, and what actually happened is that the suite's own data did not support the claim the unread source was carrying. An unverified external figure is not merely unconfirmed; it can be *actively misleading about one's own system*. Third, the replacement finding is better than the one it destroyed: **proof size and proof time both rise as disclosure falls**, so the most privacy-preserving policy is the slowest and the largest, and privacy is a latency cost that arrives precisely in the tier with the least room for it. That is a thesis-grade result, and the suite only has it because someone built the cheap thing instead of writing about it again.

**And what Slice 2(c) added (2026-10-15): the comparison the thesis has always needed.** The Groth16 range predicate was built and verified on-chain — 3,999.9 ms to prove, 645.3 ms to verify cold, 705 B of calldata, 250,283 gas as a transaction and nothing as a view. Three consequences, ranked.

*The least interesting is the one that was planned.* K-HDA-6's borrowed "≈200–350K gas" now has a measured point at the low end. The range was right; it was simply being asserted rather than known.

*The useful one is the comparison.* All three disclosure paths now exist on the same driver's licence: the hash path reveals the credential, BBS+ reveals chosen claims, the predicate reveals only a result. That is the table in 05 §3.2.1, and it is what the thesis's `createPresentation` finding has always implied but never shown — the EVM line defers disclosure to off-chain middleware, and here is what each middleware option actually costs, in one place, on one object.

*The one nobody planned is a reversal of emphasis.* The suite, the thesis draft, and most of the literature have treated **verifier gas** as the ZK cost question. The measurement says verification is the cheap end — 250,283 gas as a transaction, zero as a view — and **proving is four seconds**, two orders of magnitude more (F-VID-16). The design question is therefore not "can a chain afford to verify this" but "where does the prover live", which is a placement question and so lands squarely in this suite's own idiom (05 §3.2.1 gives three answers). Chapter 4's ZKP section is currently organised around the wrong axis.

A note on how both Slice 2 results arrived. Stage (b) refuted a claim the suite had made; stage (c) reframed a question the suite had been asking. Neither was produced by more analysis, and neither could have been — the first needed a number the suite did not have, the second needed two numbers side by side. Three sessions of building have now corrected the documents more than three sessions of writing corrected each other, which is §6.5's thesis stated as an observation rather than a worry.

One further correction to §6.2's "possibly wrong rather than merely unproven" list. It flagged the attenuation finding of 04 §3.5 as one author's reading of the interface that should be attacked before publication. Slice 1 produced an independent instance of the same species: **F-VID-11 — `ISetC` has no function by which a validator may answer a validation request**, found by trying to make the sequence run. That is now the third case of the interface describing a check while omitting the write that would make the check meaningful (F-VID-1 content binding, F-VID-7 entitlement, F-VID-11 validation answer), and attenuation would be a fourth if it survives scrutiny. Four instances is a pattern worth a paragraph in Chapter 5 rather than four scattered findings, and that reframing is the single most useful thing this log can hand the thesis.

### 6.5 What the shape of this pass reveals about the programme

Three things, offered as diagnosis rather than complaint.

**The programme writes faster than it measures, and it knows this.** The September cross-verification said so; this pass repeated the pattern while labelling it. Labelling is progress and is not a cure. The structural fix is the one in §5.2: the cheapest measurement steps are genuinely cheap — the timing schema was an afternoon, the Set C harness a day — and they had been deferred across multiple passes not because they are hard but because writing is more immediately satisfying. A rule worth adopting is that **no pass may add a document without discharging one item of measurement debt.**

*Update, 2026-10-15.* Slice 1 ran all five of its steps in a single session and discharged four of the seven measurement debts, which is the strongest available evidence that the deferral was never about difficulty. It also vindicates the rule above twice over: the cheap steps produced the pass's most interesting result (the inverted-reputation finding, §6.4) and its newest interface finding (F-VID-11), neither of which any amount of further writing would have produced. The diagnosis is confirmed and the asymmetry is unchanged in the other direction — **Slice 1 added eight artefacts and read nothing**, so the source debt of S1 §5.1 is now the programme's largest and oldest unpaid balance.

**Bookkeeping is where the findings were hiding.** S1 was the only document in this suite with no argument in it, and it was accordingly the last to be written and the first to be deferred. Writing it produced K-HDA-10 and the eleven exposed claims (§5.3) — the latter being, on reflection, among the most consequential results of the whole pass, because it identifies that the thesis's premises are less verified than its code. Neither finding was visible from inside any single document; both required the merge. The same parallel-authorship pressure produced K-HDA-8 and K-HDA-9, which are pure coordination failures. The lesson is not that bookkeeping is virtuous but that **in a corpus this size the index is an instrument**: it measures the corpus, and deferring it defers the measurement. The next pass should write its register early rather than last.

**Everything in this programme is on one disk.** D1 has been open since the branch was created. It is the only item in any of these documents whose cost of being wrong is the loss of the work itself.

## 7. Load-bearing questions

1. **Where is the empirical cut-line?** (D7.) Not "what would be nice to measure", but: which of the seven measurement debts in §5.1 will exist before the thesis is submitted, and therefore which sentences in Chapters 4 and 5 are written in the narrowed form of 11 §5.3 and which are not. Every other question here is downstream of this one.
2. **Is the suite's length a liability?** If the thesis needs three arguments from sixteen documents, the other thirteen are working material. Should the suite be pruned to the three plus the build record before anyone outside the project reads it, and if so by whom — because the author of a 140,000-word pass is the worst-placed person to cut it.
3. **Does the no-rewrite compromise survive contact with a supervisor?** §6.3 proposes that no document goes out with a post-build note still standing. Accepting that rule means rewriting 01, 03, 06 and 11 before the next supervisory meeting, starting with the ⚠ rows of §3.
4. **Is a harness enough for the agent half?** *Answered in part, 2026-10-15.* The harness was built and the agent material now executes — but on a stand-in with no ERC-8004 fidelity, so the agent scenarios can be demonstrated and not costed (§6.2, revised). The question that replaces the original: does the thesis present harness-based agent evidence as evidence, with the stand-in stated, or does it wait for the O7 port in Slice 3? Presenting it is defensible and cheap; waiting is cleaner and may not happen.
5. **Is the attenuation finding (04 §3.5) correct?** It is a single author's reading of the delegate-grant semantics, and it is being proposed as a contribution candidate. It should be adversarially checked against the interface and the did:ethr semantics before it is written into Chapter 5.
6. **Who owns the corrections ledger?** Nineteen K-corrections are raised here against documents this suite does not control. **Five can be discharged today** from artefacts already on disk, and five more are cases where the programme stated a hypothesis as a result (§4). If no one applies them, the programme's canonical documents stay wrong while a support document records that they are wrong — which is worse than not having noticed, because it converts an honest error into a known one.
7. **Push the branch.** Not a research question. It has been open longest and is the only one with an irreversible failure mode.

---

## Sources used in this document

| Id | Source | Verification state | How used |
|---|---|---|---|
| — | `_CONTEXT_BRIEF.md` (all sections) | VERIFIED AT SOURCE | Suite structure, rules, provenance of the pass |
| — | HDA 10 (all), and the four committed traces | VERIFIED AT SOURCE | §1 build record; §3 "settled" column; §6.2, §6.4 |
| — | HDA 11 §5.2, §5.3, §5.4 | VERIFIED AT SOURCE | K-HDA-1 to K-HDA-7 verbatim in summary; narrowed-claim status |
| — | HDA 00 §6–§9 | VERIFIED AT SOURCE | Scenario register, demonstration plan, decisions D1–D8, known limits |
| — | HDA 01, 02, 03, 06, 07, 08, 09 | **VERIFIED AT SOURCE for post-build notes and sampled sections; not fully re-read** | §3 reconciliation — the basis of the ⚠ marks |
| — | HDA 04, 05 | VERIFIED AT SOURCE (written in this pass) | K-HDA-9; §5.1 debts 1–2; §6.2 attenuation caveat |
| — | `BUILD_LOG.md` WO-V entry; sandbox `CLAUDE.md` standing rules | VERIFIED AT SOURCE | §2 provenance note |
| — | September 2026 programme cross-verification and status reports | DIGEST-LEVEL (recalled, not re-read in this pass) | §2 and §6.5 "writes faster than it measures" |

## Registry delta rows

| Content Block | T | Source | Ch. | Ready | Notes and status |
|---|---|---|---|---|---|
| HDA suite version log entry | B | S3 §1 | Admin | n/a | — |
| Pass methodology: five steps, brief-first, build-to-falsify | B/C | S3 §2 | 4 (method framing) | 70% | Candidate for the methodology chapter's account of Stage 1 practice |
| **Pre/post-build reconciliation table** | B | S3 §3 | Admin; 4 | 80% | The cross-reference target of eight documents' post-build notes; ⚠ rows need a full re-read |
| K-ledger K-HDA-1 to K-HDA-21 | B | S3 §4; 11 §5.2 | 2, 3, 4 | 85% | K-HDA-5 and half of K-HDA-2 dischargeable now; K-HDA-9 new |
| Measurement, source, and decision debt registers | B | S3 §5.1 | 5 (limitations, future work) | 85% | Serves as S1's verification-debt list until S1 exists |
| Ordered next-pass plan | B | S3 §5.2 | Admin | 80% | Depends on D7, D8 |
| **Five-part meta commentary** | C | S3 §6 | 5 §5.6 (limitations) | 75% | §6.2's strongest/thinnest split is directly usable as limitations prose |
| Rule candidate: no pass adds a document without discharging measurement debt | C | S3 §6.5 | Admin | n/a | Process proposal |
| Rule candidate: no document leaves the project with a post-build note standing | C | S3 §6.3 | Admin | n/a | Process proposal; implies rewriting 01, 03, 06, 11 |

## Open questions for the researcher

The seven in §7 are the open questions, and they are ordered by consequence rather than by topic. The two that cannot wait are **§7.1** (the empirical cut-line, which fixes the wording of two chapters) and **§7.7** (push the branch, which is the only item whose failure mode destroys the work).
