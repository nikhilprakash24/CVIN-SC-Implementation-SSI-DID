# F1 — On-Chain Storage Versus Not, and the Identity-Dependent Transaction (IDTx)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (Phase 2, focus F1) · **Binds:** `docs/phase2/README.md`

## Executive summary
**The question.** Where should a vehicle's identity data live, and what does each choice buy, cost and forbid?

**What Phase 1 already shows** (register rows; no new run):
- **Writing state is what costs gas.** Over one 17-event vehicle lifecycle, the nine standards create between 8
  storage slots (ERC-1056) and 149 (ERC-735). Lifetime gas follows, from 1,050,809 to 5,797,549 (#49, #35).
- **Not writing state moves the cost to every reader.** ERC-1056 keeps attributes in event logs. Resolving one of its
  documents after 50 lifecycle events takes 112 RPC calls and 87 KB (#31).
- **Caching recovers the read cost at a bounded staleness:** at most k − 1 messages after a revocation (#46). Since
  the D51 fix, the check is made in chain time.
- **A database is far faster and offers no third-party verification.** On-chain writes are about 1,600 to 6,000 times
  slower than an in-process registry (#33).

**The new idea: the identity-dependent transaction (IDTx).** An IDTx is a state transition whose execution is
conditioned on identity state held by a ledger, evaluated at execution time. It is the half of the storage question
Phase 1 did not ask: what a storage choice *forbids*.
- **Event-held data cannot condition a contract.** A datum kept only in event logs can never be the condition of an
  on-chain action, because no contract can read a log. So the cheapest standard is cheap partly because no contract
  can depend on its attributes.
- **Encrypted data can condition an action only by equality**, through a commitment, unless a zero-knowledge proof is
  added.
- **Off-chain evaluation opens a time-of-check to time-of-use gap**, which only an on-chain re-check closes.

**What was done in this pass.**
- **Capture.** Phase 1 evidence was captured, with 25 IDTx instances already present in Phase 1.
- **Analysis.** A six-locus storage taxonomy, a definition, a five-axis IDTx taxonomy, a threat table, a cost model
  and the benefits table.
- **Plan.** Four experiments, as a pre-registration draft.
- **Execution.** An IDTx prototype (`phase2/idtx/`) runs against the unmodified Phase 1 ERC-1056 registry, with
  10 behaviour tests. It covers same-transaction and next-transaction dependencies, plaintext and encrypted
  commitments, and the time-of-check to time-of-use guard.
- **A Phase 1 flaw found on the way:** D64, a VIN-derived vehicle identity that undoes the VIN-privacy claim in the
  testbed.

**Recommendation** (scope reconciliation §4). In the thesis, F1 becomes a chapter 6 section using existing evidence:
the storage-locus table, the measured trade-off, the IDTx definition and taxonomy. No new experiment is needed. The
measured IDTx study becomes the first paper after the thesis.

## Files
| File | What it holds |
|---|---|
| `CAPTURE.md` | Phase 1 evidence: where each standard stores each datum; measured costs; 25 IDTx instances; gaps |
| `ANALYSIS.md` | storage loci; the IDTx definition, taxonomy, threats and cost model; benefits, costs and what each choice forbids |
| `PLAN.md` | four experiments (pre-registration draft) and their steps |
| `EXECUTION.md` | what was built and tested in this pass |
| `../FIGURES.md`, `../figures/f1_*.svg` | figures F1-1 (state written vs lifetime gas) and F1-2 (read cost vs history), generated |
