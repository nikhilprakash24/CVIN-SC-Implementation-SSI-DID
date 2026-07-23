# Chapter 7 — Conclusion (Working Draft)

**Status**: working draft. This chapter closes the thesis: it restates what
was built and measured, answers each research question and adjudicates each
hypothesis against the evidence, consolidates the contributions, states the
limitations honestly, and lays out future work. Every quantitative claim
here is a back-reference to a measured result reported in Chapter 5 (which is
itself traceable to a committed artifact); no new numbers are introduced.
Where a result rests on a simulated, representative, or local-only
realization, this chapter repeats that caveat rather than rounding it off —
the honesty caveats are load-bearing.

---

## 7.1 Summary of the Work

This thesis set out to answer a practical question for connected and
autonomous vehicles (CVs/CAVs): *which blockchain identity standard should
ground a self-sovereign identity (SSI) system for vehicles, and on what
evidence?* Prior work treats these standards in isolation or on paper. This
thesis instead delivers, to our knowledge, the **first systematic, empirical,
same-testbed comparison of nine blockchain identity standards** for automotive
SSI, in which every standard is implemented, tested, and benchmarked under
identical conditions rather than compared by specification.

The work comprises four integrated artifacts:

1. **A nine-standard on-chain implementation.** ERC-1056, ERC-721, ERC-725,
   ERC-725xy (full ERC-725X+Y account), ERC-735, ERC-1155, ERC-4337 (minimal
   representative EntryPoint + account with guardian recovery), LSP8 (minimal
   representative), and CVIN-Combined — the thesis's own ERC-1056 + ERC-735
   hybrid — each realized as a real Solidity contract and gas-benchmarked on
   an identical Hardhat runtime (solc 0.8.24, OpenZeppelin 5.0.2). MOBI VID V2
   is measured alongside as an application profile.

2. **A W3C-compliant SSI layer.** A DID resolver (four methods: `did:ethr`,
   `did:nft`, `did:key`, `did:mobi`) and a full Verifiable Credentials stack
   (issuer, holder wallet, six-stage offline verifier, ten automotive schemas,
   SD-JWT-style selective disclosure, revocation registry, EIP-191 secp256k1
   Data Integrity proofs), lifting blockchain-rooted identities to W3C DID/VC
   conformance.

3. **A real-cryptography CV2X testbed.** A V2V simulation carrying real ECDSA
   (PKI/IEEE 1609.2 baseline) and real W3C VC (SSI) verification in the
   message path at 10 Hz BSM, twelve end-to-end lifecycle use cases with
   genuine cryptographic checks (forged and replayed credentials actually
   fail), and MOBI VID's VID I birth certificate + VID II lifecycle events
   with on-chain `attestEvent` signature verification and AES-256-GCM VIN
   encryption.

4. **A reproducible, open comparison framework.** A gas benchmark, two
   complementary security lenses, and table generators that regenerate every
   figure in Chapter 5 from source. The whole is exercised by **~295
   automated tests, all green** (217 Hardhat contract tests + 28 W3C VC + 32
   MOBI VID + 6 VIN-cipher + 12/12 lifecycle use cases).

The central methodological commitment throughout is *measured, not asserted*:
gas figures are exact `receipt.gasUsed`, verified byte-identical across N=30
runs (σ = 0); latency figures are wall-clock medians with bootstrap 95%
confidence intervals over N=30 seeded runs; compliance is an executable,
CI-gated checker; security is an executable revert suite plus a reasoned
threat matrix. This reproducibility is itself a contribution: the comparison
can be re-run and independently checked.

---

## 7.2 Answers to the Research Questions

**RQ1 — Performance (cost).** *How do blockchain identity standards compare
in on-chain cost?* Identity-creation gas spans **~33×** across the nine
standards, from 52,178 gas (CVIN-Combined) to 1,704,992 gas (ERC-725xy).
Minimal event-log designs are cheapest and full smart-account / on-chain-claim
designs are most expensive; concretely, **ERC-1056 (52,612) is ~10× cheaper**
than the NFT/proxy designs ERC-721 (542,429) and ERC-725 (528,647), and the
ERC-4337 EntryPoint indirection adds a measured 46,862 gas per operation. Gas
is deterministic (byte-identical across N=30), so the ranking is exact, not a
sampling artifact (§5.2).

**RQ2 — Security.** *Which architecture is most secure for V2X?* **No single
standard dominates**; the standards occupy distinct points on a
security/performance trade-off frontier rather than one being universally
best. The cheapest identities (ERC-1056, CVIN-Combined) are the most
Sybil-vulnerable; only **ERC-4337** offers genuine on-chain key recovery
(guardian `recoverOwner`); **ERC-1155** uniquely resists identity theft via a
soulbound transfer override; and MOBI VID is the only family that hashes and
encrypts the VIN rather than exposing it on-chain. The executable revert suite
defends **43/43 applicable attack cells**, and the analysis surfaced and then
fixed a real `attestEvent` signature-verification gap (§5.6).

**RQ3 — W3C compliance.** *Can blockchain-rooted identity meet W3C SSI
standards while serving automotive needs?* Yes — **93.2% aggregate compliance
is achievable and measured** by an executable checker (DID Core v1.0 93.3%,
13/15; VC Data Model v2.0 93.1%, 27/29), above the ≥90% CI gate. The residual
~7% is two documented, deliberate deviations (deterministic sorted-key JSON
rather than URDNA2015 canonicalization; a thesis-defined, Ethereum-native
cryptosuite), i.e. registration/canonicalization choices, not any structural
incompatibility (§5.5).

**RQ4 — Real-time feasibility.** *Are blockchain identities viable for
safety-critical, real-time V2V?* Yes, for the cryptographic path. SSI warm
verification is **0.165 ms [0.162, 0.168]** (N=30) against the ~100 ms
end-to-end V2V budget — a ~600× margin — and even the cold full-credential
path (0.400 ms) clears a 10 ms signature-check target by 25×. SSI costs ~1.6×
the PKI baseline (0.102 ms) per warm message, but both are immaterial at the
safety timescale: the cost of blockchain identity is at issuance (RQ1 gas),
not at verification time. Caveat: these bound the *cryptographic* cost and
exclude radio/MAC/network-stack latency; mobility is simulated (§5.4).

---

## 7.3 Hypotheses — Verdicts

All five hypotheses are **supported**, with H4 carrying a documented nuance.

| # | Hypothesis | Verdict | Evidence (one line) |
|---|---|---|---|
| **H1** | Minimal-state standards are ≥10× cheaper for identity creation | **Supported** | ERC-1056 52,612 vs ERC-721 542,429 = 10.3× (§5.2). |
| **H2** | ≥90% W3C compliance is achievable via a translation layer | **Supported** | 93.2% measured; the two gaps are canonicalization/cryptosuite only (§5.5). |
| **H3** | Off-chain credential verification meets the V2V real-time budget | **Supported** | SSI warm 0.165 ms ≪ 100 ms (~600× margin), N=30 (§5.4). |
| **H4** | MOBI VID's semantics are realizable across backends | **Supported (fidelity gradient)** | Birth + lifecycle native on all 5 backends; multi-party attestation native on 3/5 (ERC-735, CVIN-Combined, MOBI-VID-V2 = 5/5), only partial on ERC-1056/ERC-1155 (3/5) (§5.3.1). |
| **H5** | A hybrid design can sit on the cost/capability frontier | **Supported** | CVIN-Combined pays ERC-1056 identity cost yet adds on-chain claims; Pareto-optimal among 5/5 backends (§5.3, §5.3.1, §5.6). |

The H4 nuance is substantive and worth stating plainly: MOBI VID's semantics
*port*, but not uniformly. Birth (VID I) and lifecycle (VID II) writes are
native on all five backends, whereas genuine multi-party third-party
attestation — core to MOBI VID — is natively on-chain only on the
claim-capable/purpose-built backends and degrades to off-chain VCs or an
unlinked approximation on the pure event-log (ERC-1056) and token (ERC-1155)
backends. H4 is therefore supported *with a fidelity gradient*, not as a flat
"works everywhere" claim.

---

## 7.4 Contributions

- **First systematic nine-standard empirical comparison** of blockchain
  identity standards for automotive SSI, all implemented and benchmarked on
  one identical testbed rather than compared on paper.
- **Exact, deterministic performance data** (gas across all nine standards,
  N=30, byte-identical, σ=0), quantifying a ~33× cost spread and the ~10×
  minimal-vs-NFT gap, plus an isolated 46,862-gas ERC-4337 indirection tax.
- **A W3C-compliant SSI layer for blockchain vehicle identity** achieving 93.2%
  executable, CI-gated compliance (DID Core + VC Data Model) with a full
  offline VC pipeline and four-method DID resolver.
- **A real-cryptography CV2X testbed** demonstrating that blockchain identity
  verification fits the V2V safety budget with ~600× margin (SSI warm
  0.165 ms), with attacks caught at zero false-negative/positive over 1.65 M
  verifications.
- **A dual-lens security analysis** (54-scenario executable revert suite +
  threat matrix) establishing that no standard dominates and mapping the
  trade-off frontier — including surfacing and fixing a real `attestEvent`
  forgery/replay gap.
- **The CVIN-Combined hybrid**, an ERC-1056 + ERC-735 design shown to be
  Pareto-optimal: ERC-1056-level identity cost with on-chain verifiable
  claims when needed.
- **A reproducible open framework** (~295 green tests + regenerable tables)
  that lets the entire comparison be independently re-run and audited.

---

## 7.5 Limitations

The findings are stated with the following boundaries, all of which are
recorded rather than hidden:

- **Local gas, public-testnet validation pending.** Gas is measured on the
  Hardhat local network. Because EVM gas is a deterministic function of
  opcodes executed, the *comparison* transfers to any EVM chain; but a
  public-testnet (Sepolia) confirmation has not yet been executed. The
  validation harness exists (`scripts/validate_sepolia.js`,
  `SEPOLIA_VALIDATION.md`) and awaits an RPC URL and a funded test key.
- **Simulated mobility and excluded network stack.** V2V latency uses
  `--simulate` mode (no SUMO binary exercised) and measures cryptographic
  verification cost only; radio/MAC/congestion latency — the dominant term in
  a true end-to-end budget — is out of scope for this measurement.
- **Representative implementations for two standards.** The ERC-4337
  EntryPoint and LSP8 are deliberately minimal research implementations
  (documented in their contract headers); their gas is a lower bound on a
  fully-featured build, and bundler/paymaster overhead is excluded.
- **Demo-grade VIN cipher; custody out of scope.** MOBI VID's privacy *claim*
  is the architecture (hash-on-chain, ciphertext, plaintext off-chain), not
  the specific cipher; VIN-key distribution and HSM custody are out of scope
  for the testbed.
- **Single jurisdiction and use-case scope.** The comparison targets one
  application domain (automotive SSI for CVs/CAVs) under a single implied
  regulatory setting; cross-jurisdiction identity, governance, and legal
  admissibility are not evaluated.

None of these undercut the core comparative claims — which rest on
deterministic gas and real-cryptography verification — but they bound the
generality of the absolute-cost and end-to-end-latency statements.

---

## 7.6 Future Work

Ordered from smallest lift (confirmation) to largest (new research):

1. **Sepolia public-testnet validation run.** Execute the existing harness
   against a public EVM testnet to confirm the local gas figures on a live
   chain and add real block-inclusion behavior — closing the single most
   visible open item (risk R3).
2. **Real SUMO / ns-3 integration.** Drive the testbed with the actual SUMO
   binary (the TraCI code path already exists) and layer an ns-3 (or
   equivalent) radio/MAC model to convert the cryptographic-cost bound into a
   full end-to-end V2V latency budget.
3. **Larger-scale simulation.** Extend beyond 50 vehicles / 10 Hz to
   dense-traffic and adversarial-density scenarios to characterize throughput
   and verification behavior under load.
4. **Formal security analysis.** Complement the executable revert suite and
   threat matrix with formal verification / model-checking of the core
   contracts (especially recovery and attestation flows).
5. **Cross-jurisdiction and privacy (ZK) extensions.** Evaluate multi-region
   identity and governance, and integrate zero-knowledge techniques (e.g.
   selective-disclosure proofs beyond salted digests) to strengthen the
   privacy frontier that MOBI VID's hashed-VIN design begins.
6. **Standardization engagement.** Take the comparative evidence and the
   CVIN-Combined hybrid to MOBI (and related automotive-identity standards
   bodies) to inform a converged vehicle-identity profile.

---

## 7.7 Closing

The thesis converts a design debate that has largely been conducted on paper
into an empirical, reproducible comparison. The headline result is not that
one standard wins, but that **the choice is a measurable trade-off**: minimal
event-log designs are an order of magnitude cheaper, no standard dominates on
security, W3C compliance is reachable (93.2%), and blockchain identity clears
the real-time V2V bar by a wide margin. The CVIN-Combined hybrid shows that a
purpose-built design can occupy the favorable corner of that frontier. With
the Sepolia run and real network-stack modeling as the next concrete steps,
the framework is positioned to move from a rigorous local comparison to a
fully field-validated one.

---

*Working draft. All figures cited here are back-references to Chapter 5;
regenerate them with the benchmark, SUMO, and compliance commands documented
there. No new measurements are introduced in this chapter.*
