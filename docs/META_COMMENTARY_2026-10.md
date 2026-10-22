# Meta-Commentary — October 2026 (thinking out loud)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-03
**Nature:** not a report. This is the place to think in the open: what the pieces want
to become, where the real organising work is, what I am unsure about, and what I would
do first. The earlier `META_COMMENTARY.md` (bundle era) is kept as history; the
handback and this file are current.

---

## 1. The thing I keep circling back to: the repository has become three repositories

Reading the trunk as one system (Review 02 §1), the honest description is: a research
clone (G1), a Hardhat laboratory (G2) and a Python testbed with its own contracts (G3),
stitched by a merge. They were built by the same hands with the same hypotheses, but
each solved "what is an ERC-1056 identity?" in its own way, and the measurements split
along that seam without anyone deciding they should. The two-ERC-1056s fact is the
small visible tip of it.

The author's sandbox ask is, I think, the right organising move precisely because it is
*not* a refactor. A grand sandbox plus per-option sandboxes is a **layer of
declaration** over the three generations: each option gets one place that *says* what
it is (manifest), *knows* how to drive it (adapter), *shows* everything it can do
(demos), and *proves* it at four layers (suites). Nothing has to move for that to be
true. Once it exists, the question "which ERC-1056?" has an answer the code enforces.

## 2. The asymmetry is the thesis, not a caveat

The comparison framework measured the intersection of what nine options can do. That
was the correct first move — you cannot compare what you cannot align — but the
intellectual content of the thesis lives in the **difference between union and
intersection**: what each standard *also* does, what it refuses to do, and what that
costs. The author said this asymmetry "has to be discussed at length"; I agree, and I
would go further: the asymmetry discussion is where the thesis stops being a benchmark
paper and becomes a design argument.

Three axes keep recurring when I list the differences, and I think they are the
chapter's structure:

1. **Creation** — implicit (an address *is* an identity; ERC-1056, ERC-4337 accounts
   before first use) versus minted (someone with a role creates it; ERC-721, 1155, LSP8)
   versus deployed (the identity *is* a contract; ERC-725, 725xy, 735). Three cost
   classes, three trust models, one word.
2. **Veracity and automation** — a fact on chain is automatically enforced and
   universally auditable but public and expensive; a fact in a VC is cheap and private
   but true only when a verifier runs. The measured numbers (#21: 18 ms chain-read vs
   0.3 ms off-chain; #30: 10³× on writes) put magnitudes on this axis; the sandboxes put
   *capabilities* on it.
3. **Cryptography as a design surface** — keccak keys, salted VIN hashes, AES-GCM VIN
   cipher, EIP-191 versus raw `ecrecover`, secp256k1 versus P-256. Each is a decision
   with a measured cost and an interoperability consequence; the signing-scheme
   mismatch found in September is the proof that these choices bite.

A possible organising device: an **asymmetry budget** per option — the gas and
latency a vehicle *pays* for capabilities it never uses in the V2V hot path (royalty
logic in an NFT identity, a guardian in a 4337 account). It inverts the usual question
("what does it cost to do X?") into "what does it cost to be *able* to do X?", which is
exactly the question a fleet operator choosing a substrate would ask.

## 3. Brainstorm (unfiltered, to be pruned)

- **Capability ledger as data, not prose.** `manifest.yaml` per option with three
  stances (implemented / measured / not-applicable + reason) is the smallest thing that
  makes the asymmetry *computable*. The generated matrix is a bootstrap for it; the
  manifests should replace the regex heuristics within a week.
- **`NotApplicable` as a first-class test result.** The L1 suite should *record* what an
  option cannot do rather than skip it. The N/A table that falls out is the asymmetry
  table, produced by tests — which means it is kept honest by CI.
- **Union-versus-intersection figure.** One figure per option: the full surface as a
  ring, the measured intersection as the inner disc, families as sectors. Generated from
  the manifests. I would put it at the top of the asymmetry chapter.
- **Property-based tests across options.** "Revoking an identity makes every subsequent
  verification fail" is a property every option must satisfy if it supports revocation;
  stating it once and running it over all adapters is stronger than ten bespoke tests.
- **The grand runner as the defence demo.** `run.py all` on a laptop, producing the
  asymmetry table live, is a better demonstration than any slide; it also *is* the
  reproducibility artifact.
- **Pseudonym pools as the SCMS bridge.** Still the most promising privacy experiment
  (plan M5): it turns SC-02 from "deferred" into a measurement with a clear verdict
  ("delegates give key rotation, not unlinkability").
- **Where the LLM-interface idea from the 2025 sandbox guide goes.** Not into the
  thesis. Possibly into the grand runner as a query front-end for the demo — later, if
  ever.
- **A thing I would *not* do:** build a fourth contract tree "for the sandboxes". The
  reference-only principle is the guard against the repository becoming four
  repositories.

## 4. What I am unsure about

- Whether the per-option sandboxes should be JS-first (contracts) with Python adapters
  only where a provider exists, or Python-first via web3. JS-first keeps gas exact and
  reuses Hardhat; Python-first matches the experiments. I lean JS for L1/L2 and Python
  for L3/L4, with the manifest shared.
- How far "every relevant feature" goes for the big surfaces (54 functions in MOBI V2).
  My proposal: one demo per *capability family*, not per function; the manifest lists
  functions, the demo exercises each family end to end.
- Whether to keep both ERC-1056s. I would — the vehicle-profile registry is a genuine
  design variant and the pair makes a nice within-standard asymmetry case — but it must
  be named and the register split.

## 5. Risks to the argument, said plainly

- The asymmetry chapter could become a catalogue. Guard: every family discussed must
  tie to a measured cost or a tested behaviour; the manifests make "implemented but
  undiscussed" visible.
- Re-homing 279 tests is where a careless move breaks CI quietly. Guard: move only after
  the config collects the same count.
- The author's notebooks still sit outside everything above. The sandbox manifests are
  also the slots where notebook material lands ("this option also supports X — measured
  in notebook N"); the one-page index is still the ask.

## 6. What I would do first, tomorrow

S0 (name the fork, pin the MOBI copies in CI) and S1 (the twelve manifests). They are
cheap, they are pure organisation, and once they exist every later step has a
specification to be checked against. S3 — the cross-option L1 suite with its N/A table
— is the first thing worth showing the author, because it is the asymmetry made
visible by tests rather than by prose.
