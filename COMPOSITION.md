# The Composition — Master Through-Line

*A single long-form document that tags along the entire project. It weaves the
thesis's argument, its measured evidence, and its provenance into one continuous
narrative, and it carries the writing discipline every chapter is held to. It is
**living**: it grows and is re-threaded each session, and it is the place to read
"what the thesis actually argues" end to end.*

**Held for:** Nikhil Prakash — MASc, University of British Columbia, Electrical &
Computer Engineering, Blockchain Interdisciplinary Research Cluster.
**Status:** v0.9.0-dev · 6/7 chapters drafted · all five hypotheses measured-supported.

---

## Part I — The Through-Line (the argument, as one continuous piece)

Connected and autonomous vehicles are, increasingly, networked identities. Before a
vehicle can trust a safety message from a neighbour, prove its provenance to an
insurer, or carry a tamper-evident lifecycle across owners and borders, it needs an
identity that is verifiable without a single trusted authority. Self-Sovereign
Identity (SSI) — anchored in W3C Decentralized Identifiers and Verifiable
Credentials — offers that model, and blockchains offer a substrate for it. But the
field proposes *substrates in isolation*: an NFT here, a lightweight registry there,
a claim-holder elsewhere, each argued on its own terms. No one has put them on the
same bench, under the same automotive constraints, and measured what the choice
actually costs.

This thesis does exactly that. It implements **nine** blockchain identity standards
— ERC-721, ERC-725, ERC-725xy, ERC-735, ERC-1056, ERC-1155, ERC-4337, LSP8, and a
purpose-built hybrid (CVIN-Combined) — as interchangeable vehicle-identity substrates
on one testbed, lifts each to W3C DID/VC conformance, exercises them against the MOBI
VID vehicle-identity profile, and measures four things that matter to a vehicle: how
much an identity operation *costs* (gas), whether it can be verified *fast enough* for
safety-critical V2V, how *secure* it is against a V2X threat model, and how *compliant*
it is with the open SSI standards it must interoperate with.

The argument runs in five measured claims, each a hypothesis held from the outset and
then tested:

- **The substrate choice is a ~33× cost decision, and the minimal one wins the common
  path (H1).** Creating an identity ranges from 52,178 gas (the hybrid) to 1,704,992
  (a full ERC-725 account); the lightweight event-log substrate (ERC-1056) is ~10×
  cheaper than the NFT and proxy designs. The decision to build on ERC-1056 was made
  *first*; the measurement confirms it.
- **No single standard dominates — security and performance are the same decision seen
  twice (H5).** The cheapest identities are the most Sybil-exposed (permissionless
  self-registration); the issuer-gated ones resist Sybil but cost more. Recovery is
  ERC-4337's alone; soulbound theft-resistance is ERC-1155's alone; on-chain VIN
  privacy is MOBI VID's alone. Standards occupy a frontier, and selection is a
  requirements-driven move along it.
- **Blockchain-credential verification fits the V2V safety budget (H3).** With real
  cryptography over thirty seeded runs and 1.65 million verifications, a
  blockchain-rooted credential verifies in 0.165 ms (95% CI [0.162, 0.168]) against a
  ~100 ms budget — a ~600× margin — while catching every injected attack. The cost of
  blockchain identity lives at issuance, not at verification.
- **Open-standard compliance is a bounded last mile (H2).** A blockchain-rooted
  identity reaches 93.2% measured W3C DID/VC conformance; the residual is two
  deliberate, documented deviations, not a structural incompatibility.
- **A hybrid sits on the favourable corner of the frontier (H4/H5).** Composing a
  cheap event-log identity with on-chain claims (CVIN-Combined) reaches full MOBI VID
  fidelity at the lowest total gas of any full-fidelity backend — paying the cheap
  price for the common path and the claim price only when a verifiable claim is needed.

The contribution is therefore not a new standard but a *decision framework*, grounded
in measurement: the first same-testbed empirical comparison of nine blockchain identity
substrates for vehicles, with a reproducible open framework and a hybrid that
demonstrates the frontier's favourable corner. Where the work found a real
vulnerability — an unverified on-chain attestation signature — it fixed it and reports
the before/after as evidence rather than hiding it.

*(This section is the spine; each chapter expands one movement of it. It is rewritten
as the chapters mature.)*

---

## Part II — Writing Discipline (the standard every chapter is held to)

This is a **research MASc thesis in ECE**, not a system report. The writing is held to:

1. **Claim → evidence → interpretation, in that order.** Every quantitative claim
   names its measured source (a committed artifact in `SOURCES.md §6`) before it is
   interpreted. Results (Ch. 5) report; Discussion (Ch. 6) interprets; they never
   blur.
2. **Hypotheses are falsifiable and stated up front.** H1–H5 are declared in Ch. 1 and
   Ch. 3 as testable propositions; Ch. 5 renders verdicts; nothing is asserted that a
   measurement could not have refuted.
3. **Honesty is load-bearing.** Threats to validity, representative-vs-full
   implementations (ERC-4337 EntryPoint, LSP8), simulated mobility, the pending Sepolia
   run, and documented compliance deviations are stated in the body, not buried. An
   examiner who goes looking for the caveat finds it already there.
4. **Attribution is exact.** The research questions, hypotheses (including the
   sub-hypotheses), and design decisions are the researcher's; the tooling implemented
   and measured. `PROVENANCE.md` and `docs/DEVELOPMENT_HISTORY.md` are the record.
5. **Reproducibility is a first-class result.** Determinism (N=30, σ=0 for gas),
   confidence intervals (bootstrap for latency), a committed lockfile, and CI gates are
   part of the argument, not an appendix afterthought.
6. **Citations are never fabricated.** Chapter 2 remains a stub until the researcher
   supplies the reference set; every external claim traces to `SOURCES.md`.
7. **Voice.** Precise, active, hedge-free where the data is firm and explicitly
   uncertain where it is not. Define terms once, at first use. Figures and tables carry
   the load; prose points at them.

Every chapter draft is measured against this list before it is called done.

---

## Part III — Evidence Ledger (claim ↔ data)

| Claim | Hypothesis | Measured source | Chapter |
|---|---|---|---|
| ~33× gas spread; ERC-1056 ~10× cheaper | H1 | `gas_benchmark.json` (N=30, σ=0) | §5.2 |
| Hybrid Pareto-optimal on fidelity-per-gas | H5 | `gas_benchmark.json`, `mobi_vid_backends.json` | §5.3, §5.3.1 |
| MOBI VID portable across 5 backends (fidelity gradient) | H4 | `mobi_vid_backends.json` | §5.3.1 |
| SSI warm verify 0.165 ms ≪ 100 ms | H3 | `v2v_latency_stats.json` (N=30, bootstrap CI) | §5.4 |
| 93.2% W3C compliance | H2 | `w3c_compliance_checker.py` (live; snapshot pending) | §5.5 |
| No standard dominates; found-and-fixed attestation gap | H5/security | `security_matrix.json`, `attack_results.json` | §5.6 |
| Marginal cost O(1) (no history degradation); lifetime cost reverses point ranking; hybrid tunable via claim fraction *f* | H5 (lifetime) | `scaling_marginal.json`, `scaling_lifetime.json` | §5.9 |
| Verify O(1) in claims, linear in peers; V2V saturation P\*≈772 ≫ realistic | H3 (scaling) | `scaling_verify.json` | §5.9 |

---

## Part IV — Composition State (living log)

- **Done:** implementation over-complete (all 9 standards, W3C SSI + MOBI VID layers,
  CV2X testbed, ~295 tests, all measured results); 6/7 chapters drafted; provenance
  spine (`DEVELOPMENT_HISTORY`, `SOURCES`, `PROVENANCE`, `SIDE_PAPERS`, scaffold).
- **The real remaining discipline:** writing the thesis *as a thesis* — turning the
  grounded chapter drafts into examiner-grade academic prose under Part II, and Ch. 2's
  literature review (needs the researcher's citations).
- **Alternating flow (agreed):** interleave — (a) code/execution/analysis, (b) per-source
  artifacts in batches (local + external), (c) thesis-writing passes — rather than any
  one straight through; this Composition is re-threaded at each pass so the whole is
  always coherent before more is added.
- **Next passes (candidates, not yet run):** persist the W3C-compliance JSON snapshot;
  strengthen one chapter to examiner-grade as a writing exemplar; continue artifact
  Wave A; real Sepolia witness when access lands.

---

## Part V — Versioning & Push Plan (for the coming full GitHub access)

**Goal:** version everything and push the full history + all milestone versions once
access is granted (full access, not a token).

- **Branch:** `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` (all work).
- **Tags to push:** `v0.7.0` (integration), `v0.8.0` (rigor); cut `v0.9.0` after the
  real Sepolia witness. This consolidation pass is `0.9.0-dev`.
- **On access:** `git push --all` + `git push --tags` to the granted remote; then keep
  pushing per commit. Until then: every deliverable is committed and captured in the
  rolling git bundle delivered to the researcher (the durable backup).
- **Checklist maintained in** `META_COMMENTARY.md`.
