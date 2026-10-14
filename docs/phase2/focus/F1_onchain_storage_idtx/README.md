# F1: On-Chain Storage Versus Not, and the Identity-Dependent Transaction (IDTx)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (Phase 2, focus F1) · **Binds:** `docs/phase2/README.md`
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-1,
AR-2, AR-3, AR-5, AR-9, AR-16, AR-41

## Executive summary
**The question.** Where should a vehicle's identity data live, and what does each choice buy, cost and forbid?

**Recommendation** (the review's §4.1; scope reconciliation §3.1).

| Item | In the thesis? | Where |
|---|---|---|
| The storage-locus table, with locus and encoding merged (analysis §2, §4.4) | **keep** | chapter 6, one section together with the IDTx |
| The IDTx definition, three-axis taxonomy and re-classified inventory (analysis §4.1, §4.2, §4.4), labelled conceptual | **keep** | the same section; a mapping table in chapter 4 |
| The threat table, rows with defect evidence (analysis §4.5) | **keep** | chapter 6 |
| The cost model, the plan's experiments, the prototype | **cut** | one future-work paragraph; the prototype cited as an artefact; the measured study is paper P5 |

**Key terms.**
- A *register row* (#n) is a row of the claim register, `docs/MEASUREMENT_CONDITIONS.md`.
- An *event log* is data a contract emits into a transaction's receipt. Anyone off chain can read it. A contract
  cannot read it directly.
- *k* is the re-check interval of a caching verifier: it asks the chain on every k-th message.
- An **identity-dependent transaction (IDTx)** is a transaction whose admissibility or effect is a function of the
  state of an identity that the transaction names. That state is evaluated during execution, from ledger state or
  from an attestation or proof the transaction carries. It excludes two cases: authentication of the sender, and
  administration of the record the transaction itself modifies. The off-chain counterpart is an
  **identity-dependent decision**. (Analysis §4.1, adopting the review's §3.3 as the default of decision P2-D8.)

**What Phase 1 already shows** (register rows; no new run).

| Finding | Evidence |
|---|---|
| **Writing state is the part of gas the storage choice controls.** Over one 17-event lifecycle, zero→nonzero SSTOREs range from 8 (ERC-1056) to 149 (ERC-735), and lifetime gas from 1,050,809 to 5,797,549. This is an association, not a cause: some standards' cost is mostly per-identity contract code. | #49, #35 |
| **Not writing state moves the cost to every reader.** ERC-1056 keeps attributes in event logs. Resolving one of its documents after 50 lifecycle events takes 112 RPC calls and 87 KB. State-storing standards stay flat in calls, while their bytes grow. | #31, #51 |
| **Caching recovers the read cost at a bounded staleness.** The ERC-1056 cached verifier accepts at most k − 1 messages after a revocation. These rows predate the D51 fix, which now decides validity in chain time; they are due for re-run (A3b). | #32, #37 |
| **A database is faster, and the cache did not match it as pre-registered.** On the 2026-10-04 re-run, on-chain writes were about 1,600 to 6,000 times slower. The "equal once cached" test **failed** (ratio 0.041). Keeping the cache fresh costs 15.403 ms and 6 RPC calls. | #33 |

**What Phase 1 did not ask: what a storage choice forbids.** The IDTx makes that question precise, with three
consequences:
- **Event-held data cannot be read by a contract directly.** It can condition an on-chain action only through a
  receipt proof the transaction carries, which Phase 1 never built or measured. So the cheapest standard is cheap
  partly because a contract cannot depend on its attributes without that extra proof.
- **A commitment gates by equality only.** A registered commitment proves no knowledge of the value behind it;
  that would need the opening disclosed or a zero-knowledge proof.
- **A re-check in the transaction closes the gap inside execution, not the ordering race.** It closes the
  time-of-check to time-of-use gap within execution. The race between the dependency's change and the dependent
  transaction stays open, and Phase 1 did not measure it.

**What this pass did.**

| Step | Output |
|---|---|
| Capture | Phase 1 evidence; 25 instances captured. Re-classified under the definition, together with `payToll`, only **4 of 26 are IDTx**: the rest are administration, authentication, enabling views, or decisions taken off chain |
| Analysis | storage loci; the definition; a three-axis taxonomy; threats; the cost model's shape; benefits, costs and what each choice forbids |
| Plan | four experiments with point predictions, verdict rules and kill criteria; the D64 fix designed with a uniqueness mechanism first |
| Execution | an IDTx prototype (`phase2/idtx/`) against the unmodified Phase 1 ERC-1056 registry, with 12 behaviour tests; 5 gate mutants run in CI |
| Defect found on the way | D64: a VIN-derived vehicle identity undoes the VIN-privacy claim in the testbed |

## Files
| File | What it holds |
|---|---|
| `CAPTURE.md` | Phase 1 evidence: where each standard stores each datum; measured costs; 25 dependency instances (its working definition is superseded by analysis §4.1); gaps |
| `ANALYSIS.md` | storage loci; the IDTx definition, inventory, taxonomy, threats and cost shape; benefits, costs and what each choice forbids |
| `PLAN.md` | four experiments (pre-registration draft); the D64 fix design |
| `EXECUTION.md` | what was built and tested |
| `../FIGURES.md`, `../figures/f1_*.svg` | figures F1-1 (state written vs lifetime gas) and F1-2 (read cost vs history), generated |
