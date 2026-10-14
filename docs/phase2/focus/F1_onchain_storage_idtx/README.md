# F1: On-Chain Storage Versus Not, and the Identity-Dependent Transaction (IDTx)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (Phase 2, focus F1) · **Binds:** `docs/phase2/README.md`

## Executive summary
**The question.** Where should a vehicle's identity data live, and what does each choice buy, cost and forbid?

**Recommendation** (scope reconciliation §4). In the thesis, F1 becomes a chapter 6 section built on existing evidence:
the storage-locus table, the measured trade-off, and the IDTx definition and taxonomy. No new experiment is needed.
The measured IDTx study becomes the first paper after the thesis.

**Key terms.**
- A *register row* (#n) is a row of the claim register, `docs/MEASUREMENT_CONDITIONS.md`.
- An *event log* is data a contract emits into a transaction's receipt. Nodes keep it; no contract can read it.
- *k* is the re-check interval of a caching verifier: it asks the chain on every k-th message.
- An **identity-dependent transaction (IDTx)** is a state transition whose execution is conditioned on identity state
  held by a ledger, evaluated at execution time.

**What Phase 1 already shows** (register rows; no new run).

| Finding | Evidence |
|---|---|
| **Writing state is what costs gas.** Over one 17-event vehicle lifecycle, the nine standards create between 8 storage slots (ERC-1056) and 149 (ERC-735). Lifetime gas follows, from 1,050,809 to 5,797,549. | #49, #35 |
| **Not writing state moves the cost to every reader.** ERC-1056 keeps attributes in event logs. Resolving one of its documents after 50 lifecycle events takes 112 RPC calls and 87 KB. | #31 |
| **Caching recovers the read cost at a bounded staleness.** A verifier accepts at most k − 1 messages after a revocation. Since the D51 fix, the check is made in chain time. | #46 |
| **A database is far faster and offers no third-party verification.** On-chain writes are about 1,600 to 6,000 times slower than an in-process registry. | #33 |

**What Phase 1 did not ask.** Phase 1 never asked what a storage choice *forbids*. The IDTx is that half of the
storage question. The analysis draws three consequences:
- **Event-held data cannot condition a contract.** A datum kept only in event logs can never be the condition of an
  on-chain action, because no contract can read a log. So the cheapest standard is cheap partly because no contract
  can depend on its attributes.
- **Encrypted data can condition an action only by equality**, through a commitment, unless a zero-knowledge proof is
  added.
- **Off-chain evaluation opens a time-of-check to time-of-use (TOCTOU) gap.** Only an on-chain re-check closes it.

**What this pass did.**

| Step | Output |
|---|---|
| Capture | Phase 1 evidence, including 25 IDTx instances already present in Phase 1 |
| Analysis | a six-locus storage taxonomy, the IDTx definition, a five-axis IDTx taxonomy, a threat table, a cost model and the benefits table |
| Plan | four experiments, as a pre-registration draft |
| Execution | an IDTx prototype (`phase2/idtx/`) that runs against the unmodified Phase 1 ERC-1056 registry, with 10 behaviour tests. It covers same-transaction and next-transaction dependencies, plaintext and encrypted commitments, and the TOCTOU guard |
| Defect found on the way | D64: a VIN-derived vehicle identity undoes the VIN-privacy claim in the testbed |

## Files

| File | What it holds |
|---|---|
| `CAPTURE.md` | Phase 1 evidence: where each standard stores each datum; measured costs; 25 IDTx instances; gaps |
| `ANALYSIS.md` | storage loci; the IDTx definition, taxonomy, threats and cost model; benefits, costs and what each choice forbids |
| `PLAN.md` | four experiments (pre-registration draft) and their steps |
| `EXECUTION.md` | what was built and tested in this pass |
| `../FIGURES.md`, `../figures/f1_*.svg` | figures F1-1 (state written vs lifetime gas) and F1-2 (read cost vs history), generated |
