# Master Update — full status for audit & parallel research

*One self-contained reference to consult while you do parallel research. It consolidates
everything: what exists, what it argues, how defensible it is, exactly what I need from
you, and how to push. Detailed sources are cross-referenced; this is the entry point.*

**Version:** 0.9.0-dev · tags `v0.7.0`, `v0.8.0` · ~50 commits, all local + in the git
bundle (push pending — see §6). **Not yet on GitHub past `be32c6e`.**

---

## 1. TL;DR

- **Implementation is over-complete** (more than a MASc needs): all 9 identity standards
  + MOBI VID, W3C VC/DID layers, CV2X testbed, ~295 automated tests, every result measured.
- **All five hypotheses (H1–H5) supported by measured data**, plus a new scaling study
  (§3) that reframes the cost question to a vehicle *lifetime* — with a genuinely novel
  finding (the cost ranking *reverses* over a lifetime).
- **The real remaining work is thesis *writing*** (ECE-MASc discipline) and the Ch. 2
  literature review — the things that need *your* input (§5).
- **The base is examiner-defensible**: most audit validity objections are closed (§4).
- **Provenance is corrected**: the research ideas/hypotheses/decisions are attributed to
  *you*; the toolchain implemented and measured (`PROVENANCE.md`, `docs/DEVELOPMENT_HISTORY.md`).

## 2. What exists (deliverable inventory)

**Code / experiments** (all committed, tests green):
- 9 standards + MOBI VID contracts; 217 Hardhat tests. `1_blockchain-identity/`.
- W3C VC layer (28 tests), DID resolver, MOBI VID VID I/II (32 tests), VIN cipher (6).
- CV2X testbed: 12 lifecycle use cases (real crypto), SUMO V2V sim. `cv2x-testbed/`.
- Benchmarks: gas (9-standard, N=30 deterministic), scaling (marginal, lifetime, verify,
  saturation), sensitivity (optimizer, calldata), MOBI multi-backend, V2V latency (N=30),
  two-lens security, W3C compliance checker (93.2%), Sepolia harness. `4_comparison-framework/`.

**Thesis** (`docs/thesis/`): Chapters 1, 3, 4, 5, 6, 7 drafted; **Ch. 2 stub (needs your
citations)**; `SCAFFOLD.md`; appendices index; `chapter5-results/` is the measured anchor
(now incl. §5.9 scaling and §5.9.4 sensitivity).

**Provenance & framing:** `COMPOSITION.md` (master through-line + writing discipline),
`SOURCES.md`, `PROVENANCE.md`, `DEVELOPMENT_HISTORY.md`, `SIDE_PAPERS.md` (8 candidates),
`docs/THREAT_MODEL.md`, `docs/RESEARCH_AUDIT.md`, `docs/SCALING_EXPERIMENTS.md`,
`META_COMMENTARY.md`, and **29 provenance dossiers** (`docs/artifacts/*.html`).

## 3. The research argument + all findings

Nine substrates on one testbed, measured against cost / real-time / security / W3C
conformance. Findings (each honestly bounded):

- **H1 (cost):** ~33× spread; ERC-1056 ~10× cheaper to create than ERC-721/725. §5.2.
- **H2 (compliance):** 93.2% W3C DID/VC (self-assessed; external vectors pending). §5.5.
- **H3 (real-time):** credential *verification* is not the V2V bottleneck — 0.165 ms warm
  (N=30), ≤ the 10 ms auth budget; verification is O(1) in credential richness and linear
  in traffic with a saturation point P\*≈772 neighbours (≫ realistic). *Excludes the
  network stack.* §5.4, §5.9.3.
- **H4 (portability):** MOBI VID realized on 5 backends with a fidelity gradient. §5.3.1.
- **H5 (hybrid):** CVIN-Combined is *proven* non-dominated on (cost, fidelity) and spans
  the frontier as claim-fraction *f* varies. §5.3, §5.9.2.
- **Scaling headline (new, novel):** no standard degrades with history (all O(1)); but
  the **lifetime cost ranking reverses** the creation ranking — ERC-1056 cheapest over 15
  years, the hybrid's value is *tunability*, not being cheapest. §5.9.
- **Security:** two-lens (54 attacks, 43/43 defended) + threat matrix; a found-and-fixed
  on-chain attestation vulnerability. §5.6, `THREAT_MODEL.md`.

**The one-sentence contribution:** *the first same-testbed empirical comparison shows the
substrate choice is a coupled cost/security/fidelity frontier — not a winner — and a
tunable hybrid occupies its favourable corner across the vehicle lifecycle.*

## 4. Audit scorecard (validity — read `docs/RESEARCH_AUDIT.md` for detail)

| Item | Status |
|---|---|
| gas "N=30" mislabeled as CIs (§4.3) | ✅ relabeled reproducibility |
| V2V "600× margin" scope (§4.4) | ✅ claim narrowed (analytic budget figure needs citations) |
| latency CI = repeatability (§4.5) | ✅ framed as repeatability |
| informal threat model (§4.7) | ✅ `THREAT_MODEL.md` |
| no scaling/sensitivity (§4.8) | ✅ §5.9 + §5.9.4 |
| "Pareto-optimal" loose (§4.9) | ✅ proven non-dominance |
| gas = relative work / calldata (§4.1) | ✅ reframed + 12 gas/byte quantified |
| mechanistic gas (§4.2) | ◐ cold-storage + calldata explained; full opcode/ref-impl open |
| external W3C conformance (§4.6) | ○ open — needs official vectors (may revise 93.2%) |
| implementation confound (representative ERC-4337/LSP8) | ◐ stated as threat; ref-impl deltas open |

**Net:** the two claims an examiner attacks hardest (V2V margin, "cheapest hybrid") are
both now defensible. Remaining gaps need citations or a decision from you.

## 5. What I need from you — EXPANDED

Ordered by how much each unblocks.

1. **Chapter 2 citation set (biggest unblock).** A reference list — BibTeX, a Zotero
   export, or even rough author/title/year lines — covering: prior blockchain-SSI-for-
   vehicles work; comparative studies of identity standards; W3C DID/VC and MOBI VID
   literature; V2X identity/security (to also source the §4.4 analytic V2V budget and the
   §4.6 conformance references). *With this I draft Ch. 2 and the analytic V2V-budget
   figure, both against `SOURCES.md`.*
2. **A one-page index of your notebooks.** Not the content — just *what's in them*
   (topics, experiments, datasets, any new results or directions). *Why:* so I shape the
   thesis scaffold's extension slots to receive your material cleanly, avoid rebuilding
   what you already have, and tell you which of your material strengthens the base vs.
   belongs in a side-paper. You said you may not even integrate all of it — the index
   lets us decide what makes the base and what doesn't.
3. **Decisions only you can make (research framing):**
   - Which **hypotheses are load-bearing** for your committee, so I concentrate the
     examiner-grade polish there.
   - Whether to run **external W3C conformance** (§4.6) — it strengthens H2 but could
     revise 93.2% down; your call since it changes an outward claim.
   - Whether to add a **fee-market cost scenario** (§4.1) — turns relative gas into a
     fiat cost range (L1 vs L2 vs consortium), or keep the cleaner "relative work" claim.
4. **Access:** GitHub push (§6) and, when convenient, **Sepolia creds** (an RPC URL + a
   funded *test-only* key) so the validation harness produces a real public-testnet
   witness and I cut `v0.9.0`.
5. **Your audit verdict** on `docs/RESEARCH_AUDIT.md` — confirm the narrowed claims, or
   direct me to invest in broadening any of them further.

## 6. How to push (GitHub — the current roadblock)

Push is blocked at the session level (403, both remotes; fetch works) — I cannot change
it from inside the container. **Reliable path (from your computer, using your own
credentials):**
```bash
git clone cvin-thesis-latest.bundle CVIN-thesis && cd CVIN-thesis
git remote set-url origin <your GitHub repo SSH/HTTPS URL>
git push -u origin claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy
git push origin --tags
```
Alternatively, re-authorize this environment's GitHub write access from the Claude Code
web UI and tell me — I'll `git push --all && git push --tags` from here. Until then, the
rolling **git bundle** (delivered to you at every checkpoint) is the durable backup and
contains the complete history + tags.

## 7. Plan forward — how your notebooks integrate

1. **Now (me, ungated):** finished — scaling, sensitivity, threat model, dominance,
   claim reframes, artifacts. Base is stabilized.
2. **You:** citations + notebook index + access + framing decisions (§5).
3. **Then (me):** Ch. 2 written; each chapter lifted to examiner-grade prose; LaTeX
   thesis assembled (UBC template) with **labeled slots** for your notebook material.
4. **Then:** integrate the notebook material into the slots — strengthening a base that
   is *already good enough for a thesis on its own*, exactly your stated goal.

## 8. Detailed sources (where to read more)
`COMPOSITION.md` (argument + writing discipline) · `docs/RESEARCH_AUDIT.md` (validity) ·
`docs/thesis/chapter5-results/` (measured results) · `docs/thesis/SCAFFOLD.md` (outline) ·
`SIDE_PAPERS.md` · `docs/THREAT_MODEL.md` · `SOURCES.md` / `PROVENANCE.md` (provenance) ·
`META_COMMENTARY.md` (living handoff).
