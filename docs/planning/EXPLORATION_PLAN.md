# Exploration Plan — Related Work, Prior-Art Code, and Tooling

**Date:** 2026-10-15 · **Baseline:** HEAD `fa6188e` (v0.8.0, 739 tests green)
**Goal:** systematically survey (a) the academic literature, (b) existing code bases,
and (c) tools that could make CVIN more rigorous, then turn what we find into
(1) a verified Chapter 2 + bibliography and (2) a prioritized, register-tracked
improvement backlog.

## Ground rules (inherit the repo's existing discipline)

1. **No unverified citation enters the repo.** Every reference needs a resolvable
   DOI, arXiv ID, standards-body URL, or archived URL, and a one-line note of *what
   it actually claims* (read from the paper, not the abstract alone, for anything
   cited in a comparison).
2. **Every search is logged** (`docs/related-work/SEARCH_LOG.md`: date, tool, query,
   hits, kept) so the literature review is reproducible (PRISMA-style counts).
3. **New measurements follow the register.** Anything a tool produces that becomes a
   thesis number gets a `docs/MEASUREMENT_CONDITIONS.md` entry, pre-registered where
   it is a hypothesis test.
4. **Phase outputs are files in the repo**, not chat. Each phase ends with a short
   after-action note appended to `docs/related-work/README.md`.

## Tool map (what is actually available in this environment)

| Need | Tool | Notes |
|---|---|---|
| arXiv CS/crypto/networking papers, full text | alphaXiv MCP | search, read full text, save to library folders |
| Peer-reviewed (IEEE/ACM/Elsevier) discovery | Consensus MCP, Firecrawl research search | Semantic Scholar/OpenAlex coverage; citation graph expansion via `firecrawl_research_related_papers` |
| Public code, issues, READMEs | Firecrawl developer search, alphaXiv GitHub reader | GitHub MCP is scoped to this repo only, so outside repos go through these or a clone |
| Public web pages (specs, EIPs, W3C, docs) | Firecrawl scrape, headless Chromium (Playwright) in this container | No logins |
| Login-gated pages (UBC library proxy, IEEE Xplore, SAE, MOBI member area, faucets with captcha) | **Your** browser via Claude in Chrome (run from a local/desktop session), or you fetch and drop the PDFs in `docs/related-work/pdfs/` (git-ignored) | This cloud container cannot sign in as you |
| Running tools (Slither, Foundry, Echidna, Veins…) | Bash in this container | Network goes through the proxy; installs may need the environment's network policy |
| Long-running watch for new papers | Scheduled task (weekly) | Phase 7 |

---

## Phase 0 — Workspace and baseline (½ session)

**Do:** create `docs/related-work/` with `refs.bib`, `matrix.csv` (one row per
paper: venue, year, identity substrate, V2X?, testbed, metrics reported, closest
RQ, overlap/threat to our gap claim), `repos.csv` (one row per code base),
`tools.csv` (one row per tool with a try-it result), `SEARCH_LOG.md`, and
`.gitignore` for `pdfs/`. Re-run the full test suite once so later phases start from
a verified green baseline.

**Prompt:**
> Phase 0 of docs/planning/EXPLORATION_PLAN.md: scaffold docs/related-work/ with the
> files and column schemas the plan lists, run the full Hardhat + pytest suites, and
> record the pass counts and commit in docs/related-work/README.md. Don't change any
> existing results.

**Exit:** scaffold committed; baseline test counts recorded.

---

## Phase 1 — Systematic literature discovery (2–3 sessions, parallelizable)

Eight query clusters, each mapped to an RQ/hypothesis so every paper has a reason
to be there:

| # | Cluster | Feeds |
|---|---|---|
| L1 | SSI / DID / VC for vehicles, IoV, automotive (incl. MOBI VID, Citopia, Catena-X, EBSI-style wallets for cars) | Ch2 §2.1, §2.3, gap claim |
| L2 | Blockchain-based V2X authentication & key management (permissioned and public chains) | Ch2 §2.4, RQ2 |
| L3 | Comparative/benchmark studies of DID methods and Ethereum identity standards (gas, resolution latency) | RQ1, H1, the "no same-testbed comparison exists" gap |
| L4 | IEEE 1609.2 / SCMS / ETSI ITS PKI performance: signing/verify latency, certificate size, revocation (CRL/LA) | H3, PKI baseline validity |
| L5 | Pseudonym schemes and linkability in V2X; on-chain unlinkability | M5 pseudonym pool (#38), SP-3 |
| L6 | Credential revocation & freshness (status lists, accumulators, caching vs staleness) | freshness-k (#32, #37) |
| L7 | Smart-contract identity security: signature replay, ERC-4337 costs/attacks, soulbound tokens | RQ2, SP-1, SP-2 |
| L8 | VC/DID conformance and interoperability testing methods | H2, SP-8, the "self-scored checker" risk R4 |

**Method per cluster:** 3–6 seed queries on alphaXiv + Consensus → keep 10–25 →
forward/backward citation expansion from the 3 most central papers → dedupe → read
and fill `matrix.csv` → BibTeX with DOI. Save kept papers into an alphaXiv folder
named `CVIN/L<n>` so you can browse them too.

**Prompt (run one per cluster, or all eight in parallel):**
> Phase 1, cluster L3 of docs/planning/EXPLORATION_PLAN.md. Use alphaXiv, Consensus
> and Firecrawl research search (citation expansion from the top 3 seeds). Log every
> query in SEARCH_LOG.md. For each kept paper add a verified BibTeX entry (DOI or
> arXiv ID checked) to refs.bib and a row to matrix.csv, and flag any paper that
> already does a same-testbed comparison of Ethereum identity standards, because that
> would weaken our gap claim. No entry without a resolved identifier.

To run all eight at once, say "use a workflow" with the prompt above and the cluster
list. That's about 8 research agents plus one merge/dedupe step.

**Exit:** ≥80 screened, ~40–70 kept, PRISMA counts, and a one-paragraph **gap
verdict**: does the Ch2 §2.5 claim survive, need narrowing, or need rewording?

---

## Phase 2 — Prior-art code bases (1–2 sessions)

Find out what already exists, what we could reuse or compare against, and what
reviewers will ask "why didn't you use X?" about.

| Area | Candidates to inspect |
|---|---|
| did:ethr / ERC-1056 stack | uport-project/ethr-did-registry, decentralized-identity/ethr-did-resolver, Veramo |
| General SSI frameworks | Hyperledger Aries/ACA-Py, walt.id, SpruceID (didkit/ssi), Sphereon SSI-SDK, Credo |
| DIF / W3C infrastructure | Universal Resolver drivers, did-test-suite (already used), VC DM 2.0 + Data Integrity test suites, Bitstring Status List |
| Account abstraction / LUKSO | eth-infinitism/account-abstraction (real EntryPoint), lukso-network/lsp-smart-contracts, ERC725Alliance |
| V2X security stacks | Vanetza (ETSI ITS security), Artery, OpenC2X, USDOT/CAMP SCMS reference code, 1609.2 ASN.1 codecs |
| V2X simulation | SUMO, Veins (OMNeT++), ns-3 5G-LENA / ms-van3t (C-V2X Mode 4), CARLA co-sim |
| Vehicle identity / data | MOBI public repos/specs, Catena-X / Eclipse Tractus-X (SSI for automotive supply chain), Gaia-X wallets |

**For each repo:** license, last commit, language, what it implements, test
coverage, whether it reproduces any of our operations, and a **reuse decision**:
(a) adopt as a dependency, (b) use as an external comparison point, (c) cite only,
(d) ignore with reason.

**Prompt:**
> Phase 2 of docs/planning/EXPLORATION_PLAN.md. For each candidate in the Phase 2
> table, inspect the repo (Firecrawl developer search / alphaXiv GitHub reader;
> shallow-clone into the scratchpad only if needed) and fill repos.csv with license,
> activity, scope, overlap with CVIN operations, and a reuse decision with one-line
> rationale. Then write docs/related-work/CODEBASES.md: the top 5 "reviewers will
> ask about this" items and what we'd do about each.

**Exit:** `repos.csv` + `CODEBASES.md`. Expected high-value finding: whether the
real eth-infinitism EntryPoint and a real 1609.2 implementation (Vanetza) can
replace our representative harnesses as comparison points.

---

## Phase 3 — Tooling trials to strengthen the build (2 sessions)

Each tool gets a timeboxed trial in a scratch branch: install, run on our tree,
record the result in `tools.csv`, and decide adopt / don't adopt.

| Category | Tools | What it would add to the thesis |
|---|---|---|
| Static analysis | Slither, Aderyn, Mythril | Independent security lens #3; findings vs our 43 attack cells |
| Fuzzing / invariants | Foundry (forge invariant tests), Echidna, Medusa | Property-based evidence for access control, soulbound, replay protections |
| Symbolic / formal | Halmos, (Certora if a free tier exists), SMTChecker | Formal claims for 1–2 critical properties (e.g. `attestEvent` signer binding) |
| Gas methodology | forge gas snapshots, hardhat-gas-reporter, Anvil vs Hardhat vs Geth dev | Cross-client check that gas numbers aren't Hardhat-specific |
| Cost realism | L2 testnets (Optimism/Base/Arbitrum Sepolia), EIP-4844 fee model | Answers "what does this cost on a real deployment in 2026?" |
| Conformance | VC DM 2.0 test suite, Data Integrity (ecdsa-rdfc/jcs) suites, Universal Resolver driver | External H2 evidence beyond the self-scored checker (risk R4) |
| Python rigor | Hypothesis, mutmut, coverage.py | Mutation score for the VC verifier and freshness logic |
| Reproducibility | CITATION.cff, Zenodo DOI per release, Docker/Nix pin, Software Heritage | Archival artifact for the thesis and side papers |

**Prompt:**
> Phase 3 of docs/planning/EXPLORATION_PLAN.md, category "Static analysis". On a
> scratch branch, install and run Slither and Aderyn over 1_blockchain-identity/
> contracts. Triage every finding as true positive, false positive or by design,
> cross-reference our attack cells, and record install friction, runtime and
> verdict in tools.csv. Fix nothing yet. Propose CI integration only if
> signal-to-noise is good.

**Exit:** `tools.csv` with a verdict per tool; a short list of adopted tools with
CI cost estimates.

---

## Phase 4 — Browser-driven tasks (needs you for logged-in parts)

| Task | Who drives | Output |
|---|---|---|
| Pull paywalled PDFs found in Phase 1 via the UBC library proxy | You (or Claude in Chrome on your machine) | PDFs in `docs/related-work/pdfs/` (git-ignored); I read them and fill `matrix.csv` |
| MOBI VID / Citopia member specs (check the latest VID I/II versions against our implementation) | You (member login) | Spec diff → `docs/MOBI_VID_CHECKLIST.md` |
| SAE J2735 / J2945/1, IEEE 1609.2-2022 text for exact latency/size numbers | You (library access) | Citable numbers for `docs/LATENCY_BUDGET.md` |
| Sepolia: RPC key (Alchemy/Infura), faucet, funded test key into a CI secret | You (captcha + secrets); I run `validate_sepolia.js` | Closes the biggest open validation item |
| Google Scholar "cited by" chains, Connected Papers / ResearchRabbit maps | Me, headless, for public pages; you for anything rate-limited | Extra seeds for Phase 1 |
| UBC FoGS thesis formatting requirements + `ubc-thesis-template` | Me (public pages) | Checklist in `docs/thesis/README.md` |
| Venue CFPs and deadlines (IEEE VNC, VTC, ICBC, IEEE T-ITS, IoT-J, Vehicular Communications, ACM AsiaCCS workshops) | Me (public pages) | Dated venue table in `SIDE_PAPERS.md` |

**Prompt (public-page part):**
> Phase 4 public tasks of docs/planning/EXPLORATION_PLAN.md: using headless browsing
> and Firecrawl, collect current CFPs and deadlines for the venues listed, matched
> to SP-1..SP-8, plus the UBC FoGS thesis formatting requirements. Write them into
> SIDE_PAPERS.md and docs/thesis/README.md with access dates.

---

## Phase 5 — Synthesis: Chapter 2 and positioning (2 sessions)

1. Draft Chapter 2 §2.1–2.5 from `matrix.csv` only, so every claim is cited to
   `refs.bib`.
2. A **positioning table** (ours vs the ~10 closest works: substrates compared,
   same testbed?, gas?, V2V latency?, W3C conformance?, MOBI?, open artifact?).
3. Rewrite §2.5 (research gap) to match the Phase 1 gap verdict.
4. Update `SOURCES.md` §5 (prior work) and wire `refs.bib` into the UBC LaTeX
   template.

**Prompt:**
> Phase 5 of docs/planning/EXPLORATION_PLAN.md: draft Chapter 2 in
> docs/thesis/chapter2-literature-review/ strictly from refs.bib and matrix.csv,
> with every factual sentence cited. Build the positioning table, rewrite the gap
> statement per the Phase 1 verdict, and list any claim you wanted to make but
> couldn't source, so I can decide on it.

---

## Phase 6 — Turn findings into project improvements (ongoing)

Rank every candidate improvement from Phases 1–4 by **(thesis impact × reviewer
risk reduced) ÷ effort**, then run the top ones through the repo's normal
pre-register → run → register loop. Likely top items, to be confirmed by the
earlier phases:

1. **Real 1609.2 baseline** (Vanetza or similar) replacing or validating our PKI
   model in the H3 comparison: removes the strongest "strawman baseline" objection.
2. **Sepolia + one L2 testnet run**: closes the public-chain validation gap and
   adds real fee numbers.
3. **External conformance** (VC DM 2.0 / Data Integrity suites) beside the internal
   94.3%: retires risk R4.
4. **Slither + Foundry invariants in CI**: a third, tool-based security lens.
5. **Real EntryPoint comparison** for the SP-2 "account-abstraction tax".
6. **Real SUMO / Veins run** with a channel model: moves H3 beyond crypto-only cost.
7. **Archival release** (Zenodo DOI + CITATION.cff) before any submission.

**Prompt:**
> Phase 6 of docs/planning/EXPLORATION_PLAN.md: score every candidate from
> CODEBASES.md, tools.csv and the Phase 1 gap verdict, write
> docs/planning/IMPROVEMENT_BACKLOG.md, and for the top item draft a
> pre-registration (prediction, band, script, register row) without running it.

---

## Phase 7 — Keep it current

A weekly scheduled task: run the Phase 1 cluster queries restricted to the last 7
days on alphaXiv and Consensus, append new candidates to
`docs/related-work/INBOX.md`, and only notify you when something threatens the gap
claim or a measured result.

**Prompt:**
> Set up the Phase 7 weekly literature watch from docs/planning/EXPLORATION_PLAN.md
> (Mondays, my time zone), writing to docs/related-work/INBOX.md.

---

## Suggested order and effort

| Order | Phase | Sessions | Depends on |
|---|---|---|---|
| 1 | P0 scaffold | 0.5 | — |
| 2 | P1 literature (parallel) + P2 code bases (parallel) | 3 | P0 |
| 3 | P3 tooling trials | 2 | P0 (can run alongside P1/P2) |
| 4 | P4 browser tasks | rolling | P1 output for PDFs; you for logins |
| 5 | P5 Chapter 2 | 2 | P1, P4 |
| 6 | P6 backlog + top improvements | ongoing | P2, P3, P5 |
| 7 | P7 watch | set once | P1 query set |

## Open decisions for the author

- **Canonical remote:** earlier docs call `origin` (this repo) stale and say the
  mirror `nikhilprakash-cvin/2_miniature-waffle-...` is current. This session can
  only reach `origin`, so confirm which one exploration commits should go to.
- **Scope of Phase 6 item 1:** a real 1609.2 baseline is the highest-value and
  highest-effort change. Decide whether it's in scope for the thesis or goes to
  future work.
- **Citation manager:** plain `refs.bib` in the repo, or Zotero group library as
  the source of truth with exported BibTeX.
