# Project Genealogy (Provenance)

A chronological record of the **researcher's inputs, framing, and decisions** and
what each produced — the intellectual lineage of the thesis. Its purpose is to make
explicit that the research contributions (questions, hypotheses, design decisions)
**originated with the researcher**, and that the tooling implemented and measured
them. It complements `SOURCES.md` (what the work draws on) and
`docs/DEVELOPMENT_HISTORY.md` (the corrected development chronology).

**Privacy.** Conversations and materials are referenced by **topic and date only**.
Any credentials the researcher shared in-session (e.g. access tokens) are
deliberately **not recorded here** and are not committed anywhere in the repository.

---

## Lineage

### 0. Prior work — the starting point (pre-2025)
The researcher's earlier **CVIN-ID-SCs** repository (Truffle/Ganache identity
contracts) established the smart-contract groundwork and the intent to study
blockchain vehicle identity. → restructured into `1_blockchain-identity/`.

### 1. The research framing (researcher-originated, from the outset)
The **comparative research design** — evaluate a set of blockchain identity
standards as SSI substrates for connected/autonomous vehicles, against W3C DID/VC
and MOBI VID — is the researcher's. So are:
- the **research questions** (performance, security, W3C compliance, real-time V2V);
- the **hypotheses H1–H5**, including the **sub-hypotheses** on the
  fidelity-per-gas frontier (the event-log-cheapest / claim-based-faithful /
  hybrid-optimal intuition) that the H4/H5 measurements later confirmed;
- the **base-substrate decision** (ERC-1056-class minimal identity), recorded in the
  early logs as "TD-001" and now correctly attributed in `DEVELOPMENT_HISTORY.md`.

> This is the crux of this provenance pass: the sub-hypothesis was the researcher's
> from the beginning; the project only *confirmed* it empirically late (H4,
> `§5.3.1`). Confirmation ≠ origination — hence the record correction.

### 2. MOBI VID build (Nov 2025)
Under the researcher's direction, autonomous coding sessions synthesized the MOBI
VID / W3C DID material and implemented MOBI VID 1.0 (registry contract + provider +
tests) and, later, lifecycle use cases and a SUMO V2V integration.

### 3. Thesis integration & GitHub (2026-06-21)
Researcher input: connect the work to a new thesis GitHub account; *"this is part
of the thesis and integration needs to be done."* → repository reorganized into the
numbered four-layer thesis structure; remotes configured.

### 4. Directed build-out (2026-06/07)
Researcher requests, each producing a deliverable set:
- Four tasks: continue the CV2X testbed, a thesis README, CI/CD, thesis docs.
- A "second pass" with explicit deliverables: an inventory, a capabilities
  description, a startup guide, and a plan (→ `INVENTORY.md`, `CAPABILITIES.md`,
  `QUICKSTART.md`, `SECOND_PASS_PLAN.md`).
- Decision: commits remain under the **researcher's name/identity** for academic
  attribution (declined the tooling's default committer identity).

### 5. Integration audit & rigor (2026-07)
Researcher direction to reconcile parallel-session work and harden it. Findings and
fixes (all measured; Chapter 5): real VC verification replacing mocked checks; all
nine standards implemented; the found-and-fixed MOBI `attestEvent` signature gap;
AES-256-GCM VIN privacy; N=30 gas determinism; N=30 V2V latency with CIs; the
two-lens security analysis; the executable 93.2% W3C compliance checker; the
Sepolia validation harness; the H4 multi-backend fidelity sweep; drafts of
Chapters 1, 3–7. Milestones `v0.7.0`, `v0.8.0`.

### 6. Durability episodes (2026-07)
An ephemeral-container reset re-cloned a stale designated origin and the session's
push access was lost (both remotes 403). Researcher direction: keep working
locally, commit + bundle each step, push later. Work is preserved on the mirror
remote (through the tags) and in the git bundles delivered to the researcher.

### 7. Documentation refresh (2026-07)
Researcher direction to revise the guide and all complementary docs to the true
current state → all five living docs refreshed; a real `package-lock.json`
reproducibility bug fixed.

### 8. This consolidation pass (2026-07)
Researcher direction: **source every piece of material and conversation; correct
attribution; scaffold the thesis and separate side-paper material; write some
content blocks; keep a meta-commentary handoff; and only then plan expansion** —
because confirming the sub-hypothesis this late means the intellectual record must
be made concrete before adding new material.

---

## Attribution summary
| Contribution class | Origin |
|---|---|
| Research questions, hypotheses (incl. sub-hypotheses), comparative design | **Researcher** |
| Standard selection, base-substrate & privacy design decisions (TD-001…) | **Researcher** |
| Implementation, experiments, measurement, drafting | AI tooling, under researcher direction |
| Empirical confirmation of the above | Measured results (Chapter 5) |
