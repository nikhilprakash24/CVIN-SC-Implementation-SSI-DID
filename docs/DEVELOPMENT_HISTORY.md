# Development History

**Scope.** This document consolidates and supersedes four earlier point-in-time
session logs (`AUTONOMOUS_DEV_LOG.md`, `AUTONOMOUS_SESSION_SUMMARY.md`,
`AUTONOMOUS_SESSION2_SUMMARY.md`, `AUTONOMOUS_TASK_TRACKER.md`), which have been
removed from the working tree (they remain recoverable from git history). It
records the project's development chronology with **corrected attribution**.

---

## Attribution & Contributions Statement

This thesis is the work of **Nikhil Prakash** (MASc, University of British
Columbia, Electrical & Computer Engineering, Blockchain Interdisciplinary
Research Cluster). The **research direction, the choice of standards to compare,
the research questions, the hypotheses H1–H5 (including the H4/H5 sub-hypotheses
on the fidelity-per-gas frontier), and the architectural design decisions**
originate with the researcher.

AI development tooling (including autonomous coding sessions in November 2025 and
assistant-driven implementation/measurement passes in 2026) acted as an
**implementation and measurement instrument under the researcher's direction** —
writing code to the researcher's specification, running experiments, collecting
measured data, and drafting documentation for the researcher's review. It did not
originate the research contributions.

> **Record correction.** The superseded session logs described the tooling as an
> "Autonomous Development System" and, in one place, recorded the decision to use
> ERC-1056 as the base DID substrate as *"TD-001 … Approved By: Autonomous System
> (CTO role)."* That framing is incorrect and is corrected here: **TD-001 and all
> design decisions below are the researcher's**; the tooling implemented and
> justified them, it did not authorize them. The empirical work later *confirmed*
> these prior decisions and hypotheses (e.g. the H1 gas advantage of the
> ERC-1056-class substrate, and the H4/H5 fidelity-per-gas results) — confirmation
> of a pre-existing hypothesis, not its origination.

---

## Timeline

### Phase 0 — Prior work (pre-2025)
The smart-contract groundwork descends from the researcher's earlier repository
**CVIN-ID-SCs** (a Truffle/Ganache-based identity-contracts codebase). Its
contracts and tests were later renamed/restructured into `1_blockchain-identity/`.

### Session 1 — Research & Design (2025-11-10, ~4 h)
Under the researcher's direction, the tooling synthesized the MOBI VID
specifications and W3C DID compliance requirements and drafted an initial
architecture for a MOBI VID 1.0 implementation.
- Research synthesis: MOBI VID I (vehicle birth certificate) and VID II
  (lifecycle events); W3C DID Core alignment; SSI principles.
- Initial 4-layer architecture drafted; a 14-task board established.
- **Design decisions (researcher's; rationale developed with the tooling):**
  TD-001 ERC-1056 as the base substrate (minimal gas); TD-002 test-driven
  development; TD-003 event-based DID-document resolution; TD-004/TD-005 VIN
  privacy via salted hashing (searchable, no PII); TD-006 off-chain storage for
  large birth-certificate payloads; TD-008 manufacturer authorization for
  issuance.

### Session 2 — Implementation of MOBI VID 1.0 (2025-11-10, ~2.5 h)
- `MOBIVIDRegistry` smart contract and a `MOBIVIDProvider` Python class drafted,
  with a deployment script and a test suite.
- Additional design decisions: TD-009 tiered VIN privacy (public salted hash →
  owner-decryptable ciphertext → ZK proofs as future work); TD-011 ownership-
  transfer history tracking.

### Session 3 — Use cases & SUMO integration (2025-11-11)
Lifecycle use cases and a SUMO V2V integration were added. (See
`SESSION_3_SUMMARY.md`, which already carries its own correction banner.)

### Thesis integration & restructure (2026-06-21)
The repository was reorganized into the numbered thesis structure
(`1_blockchain-identity/ … 4_comparison-framework/`) and connected to GitHub.
(See `SESSION_THESIS_INTEGRATION.md`.)

### Integration, verification & rigor passes (2026-07)
Assistant-driven passes, under the researcher's direction, audited and hardened
the parallel-session work: real W3C VC verification replacing mocked checks; all
nine identity standards implemented and tested; the MOBI VID VID I/II layer with
on-chain `attestEvent` signature verification and AES-256-GCM VIN encryption; the
9-standard gas benchmark (N=30, deterministic); the real-crypto V2V latency study
(N=30 with confidence intervals); the two-lens security analysis; the executable
W3C compliance checker (93.2%); the multi-backend MOBI VID fidelity sweep (H4);
and drafts of thesis Chapters 1, 3–7. Milestones are tagged `v0.7.0` and `v0.8.0`;
see `CHANGELOG.md` for the itemized record.

---

## How this maps to the empirical results
The design decisions above were **hypotheses to be tested**, and the later
measured results (Chapter 5) are their test:
- TD-001 (ERC-1056 base) ↔ **H1** — the minimal event-log substrate is ~10×
  cheaper for identity creation (measured; §5.2).
- The event-log-plus-claims hybrid intuition ↔ **H5 / CVIN-Combined** —
  Pareto-optimal on fidelity-per-gas (measured; §5.3, §5.3.1).
- TD-004/005/009 (hash-and-encrypt VIN privacy) ↔ the on-chain PII-leakage
  finding — MOBI VID is the only compared family that avoids plaintext VINs
  (measured; §5.6).
- Portability of the MOBI VID profile across substrates ↔ **H4** — supported with
  a documented fidelity gradient (measured; §5.3.1).

The point of this consolidation pass is precisely to make that lineage explicit:
the ideas came first (the researcher's), and the measurements confirmed them.
