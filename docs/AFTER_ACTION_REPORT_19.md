# After-Action Report 19 — Zero-Knowledge Proofs and the Agent-Wrapped Identity (Plan 1)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-15, after report 18 closed at `b7997f8` (CI 8/8 green on `aba1d7c`); closed at the end of this pass
**Brief (the author, 2026-10-15):** continue the `cv2x-testbed-setup` line by planning and executing a full integration
of zero-knowledge proofs (primitives, a worked identity example, tests, quantitative and qualitative properties, a
standalone paper with a literature review, algorithm breakdowns and flowcharts, a build report); prove that ZK identity
needs a permanent software custodian shaped like an AI agent wrapping the identity, and that the agent needs the
identity system the thesis built; demonstrate a new attack vector and the system adapting; show the SSI spectrum with
two tables; write a second plan (the full-circle writing series) to be run in another chat, with phased prompts for both.

## 1. Plan
`docs/zkp/PLAN_1_ZKP_AND_AGENT_IDENTITY.md` (work packages WP0–WP10, propositions P1–P6, pre-registered expectations
Z-E1..Z-E7). Phased prompts: `docs/zkp/PLAN_1_PHASED_PROMPTS.md`. The writing series: `docs/zkp/PLAN_2_*.md`, not
executed here.

## 2. Execution log
- 2026-10-15 — branch fast-forwarded from `fa6188e` to `b7997f8` (the designated branch had no commits of its own; no
  merge). Plans written and pushed before WP1 (rule 1.3.5). Report opened.
- **WP1 sources.** Two research passes produced 205 entries (164 verified, 41 partial), merged into
  `docs/zkp/SOURCES_ZKP.md`; one source (Alshiekh et al., shielding) added during writing and verified.
  `docs/zkp/check_citations.py` resolves every `[@KEY]`: 316 citations, 0 unresolved. It was seen to fire on a real
  defect (a soft hyphen inside a key in Report C), fixed.
- **WP2 `zkid`.** secp256k1, Keccak-256, transcripts, Schnorr, Pedersen, Chaum–Pedersen, CDS OR, range and threshold
  proofs, Merkle, nullifiers. 24 tests, including extraction and simulation; cross-checked against libsecp256k1 and
  Ethereum's Keccak. Gate: green on first run.
- **WP3 ZK-VIN.** circom 2.2.2 built from source (cargo). 3,498 constraints. Single-party setup with fixed entropy
  (reproducible, insecure; stated on every artefact). Honest proof verifies; five false statements fail.
- **WP4 on chain.** `ZkVinGate` (IDTx with a knowledge-of-opening dependency, closes AR-5) and a Schnorr ecrecover
  verifier; 8 Hardhat tests against Phase 1's unmodified ERC-1056 registry. A trial gas run on a dirty tree was
  discarded (rule 1.1.6).
- **WP5 Steward.** policy, compiler (grammar; optional language-model backend never on the decision path), kernel,
  simulatable leakage audit, learner, vault, audit log, delegation via the Phase 1 VC layer, agent. Defects found and
  fixed before commit: an operator-precedence error in the delegation issuer check; `issue_delegation` returned the
  issuer's wrapper instead of the credential; a weak test (`test_refusals_are_value_independent`) replaced by an exact
  one.
- **WP6 attacks.** Parameters fixed before the first run (Plan amendment A1). The first run, a wiring check on a dirty
  tree, showed that A1's adversary never holds an accreditation, so a learner alone looked strongest. A post-hoc
  *insider* variant was added and reported separately (amendment A2); Z-E5/Z-E6 definitions untouched; the learner was
  not retrained.
- **WP7 runs of record** at `978988e`, `code_clean` true, by `bench/run_all.sh` (the responder's retraining reproduced
  the committed table byte for byte). Trial result files had been committed in `9d26c2a` and `978988e` before the run of
  record and were overwritten by it (`learning_curve.json` reproduced identically). After a comment-only citation-key fix in `bench/vin_bruteforce.py` and
  `bench/manual_burden.py`, only `manual_burden.json` was re-run (at `e780d40`, values identical); the other files keep
  `978988e` because no producing statement changed (`git diff 978988e` shows comments and labels only).
- **Verdicts.** Z-E1, Z-E2, Z-E3, Z-E4, Z-E5, Z-E7 PASS. **Z-E6 FAIL**: the leakage bound held on 60/60 runs, honest
  service fell below 90 % on 25/60 (minimum 70.0 %). P1, P2 (E), P4, P6 supported; P3 partly; P5 supported with a cost.
- **WP8 figures.** 12 figures by `figures/make_figures.py`, palette validated (one contrast warning, relieved by
  direct labels and shape coding), every figure rendered and inspected; six layout faults fixed, and figure 9's
  right axis widened to 80–100 % because a 0.13-point range exaggerated a negligible change. `--check` and a test that
  it fires.
- **WP9 documents.** Report A (build and verdicts), Report B (the paper, ≈ 9,250 words), Report C (the argument,
  ≈ 5,200 words), thesis integration map, layer README, docs index, root README gallery, a deterministic demo with a
  committed transcript.
- **WP10 CI.** `.github/workflows/zkp-layer5.yml`: Python tests with no skips, mutation probe (5 mutants, all caught
  locally), figures and citations checks, demo, ZK-VIN artefact manifest and prove/verify, layer 5 Hardhat tests.
  Existing dashboard and register checks re-run locally after the README edit: current.

## 3. Decisions taken by default (the author may overturn)
| Decision | Default taken | Alternative |
|---|---|---|
| Base branch | fast-forward onto `claude/cv2x-testbed-setup-…` as the brief said "continue this work" | start from the designated branch's old base |
| Placement | new layer `5_zkp-agent-identity/`, docs in `docs/zkp/` | under `phase2/` |
| Proof system | Groth16 (smallest proofs, cheapest on chain) with an honest insecure dev setup | PLONK/Halo 2 (to-do) |
| Re-run scope after the comment fix | re-run the one deterministic consumer, keep timings of record | re-time everything and re-edit every report |
| Register | rows proposed in `THESIS_INTEGRATION_MAP.md` §3, not added | add as V now |
| Commit attribution | authored as the author with no AI trailers (guide rule 1.3.1) | session trailers |

## 4. Not done
Plan 1 to-dos 6–12 (BBS+, PLONK/Halo 2, recursion, on-vehicle timing, live language-model red team, multi-party
ceremony, EUDI mapping); no live model call; Plan 2 (the writing series) is for other chats; CI for the new workflow is
not yet observed on GitHub at the time of writing.

## 5. Closed
2026-10-15, at the commit that adds this section. Handback addendum: `docs/HANDBACK_2026-10-14.md` §11.
