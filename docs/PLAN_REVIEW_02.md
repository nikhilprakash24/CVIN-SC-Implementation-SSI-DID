# Plan — Review 02 Remediation (2026-10-03)

**Input:** `docs/REVIEW_02_CODEBASE.md` (finding IDs K, H, S, T, Q).
**Rules:**
- every fix carries a regression test where it can be tested;
- no test is weakened or skipped;
- a fix that moves a cited number re-runs that experiment, and records the old row as S
  with the reason;
- author decisions (review §3) are not taken by the session.

## Pass 1 — Critical and High, plus the cheap items next to them

Four streams run in parallel, each in its own worktree on disjoint files, and are merged
in this order.

| Stream | Findings | Deliverable | Gate |
|---|---|---|---|
| **P1-K contracts** | K-1, K-2, K-3, K-4, K-11, K-13 (+ K-16 dead copies, Q-10 npm scripts) | Fixes with a Hardhat regression test per finding (each fails before the fix); re-run `benchmark_gas.js` + `generate_tables.py`; before/after delta of every changed cell | Hardhat green; the CI determinism gate passes against the regenerated JSON |
| **P1-H harness** | H-1, H-2, H-3, H-4, H-5, H-7, H-8 (rename), H-10 | Fresh issuer per V-op iteration; deterministic wallets; forward-replay resolver with a conformance assertion; R4 on the real delegate; `normalCdf` + unit test; lifecycle counts k1 and ERC-721 single-approve; conditions block corrected | Conformance green; two consecutive runs give identical gas tables |
| **P1-S SSI layer** | S-1, S-2, S-4, S-5, S-6, S-7, S-9, S-10 (cache copy + method errors), T-3 | Holder binding; fail-closed status with an issuer-bound registry; datetime parsing; proof-metadata whitelist; challenge required; low-s; explicit trusted-issuer list in the SUMO layer; negative test per PoC | 60+ Python green; `test_use_cases.py` and the SUMO `--simulate` path still run |
| **P1-T testbed** | T-1, T-2, T-4, T-5, T-6, T-11 (label) | CA signature check in both PKI providers; forward-replay key resolution; MOBI provider key from the registry; redundant RPC removed; RPC snapshot moved; then **re-run `experiment_pki_vs_erc1056.py`** | PoC attacks fail; new #21 results on a clean tree |

**Then (session, after merging):**
- Q-1, Q-2, Q-12 (CI triggers, MOBI-VID tests in CI, determinism set-equality);
- the full suites;
- a fresh `npm run metrics` promoted to `results/metrics/latest`;
- register rows #21, #22, #25, #29–#31 updated, with #5, #9 and #16–#19 marked S;
- HANDOFF §3 numbers corrected (H-6).

## Pass 2 — adversarial re-review of the Pass 1 diff, then Medium items

1. Re-review the Pass 1 diff with fresh lenses. What would make CI reject it? Did a fix
   change behaviour the chapters depend on?
2. Medium items that need no author decision:
   - Q-5, Q-6, Q-7, Q-11 (claims surface);
   - Q-8 (security harness asserts the expected revert reason);
   - Q-13 (conformance post-state);
   - Q-9 (untrack stale testbed artifacts);
   - K-6, K-8 (event chain, LSP8 data);
   - T-6, T-9 (sign and check timestamp; `success` gated on validity);
   - S-3 (documented as offline key binding, plus a chain-id check);
   - H-9, H-11, H-12 (definitions and labels).
3. Each Medium that changes gas re-runs the gate as in Pass 1.

## Pass 3 — only if Pass 2 surfaces new High findings, or CI is red

## Not in scope (author decisions, review §3)
- T-7 checker strictness and the CI floor (#4);
- H1 restatement in README and chapters (Q-3);
- K-12 hardening of the upstream registry;
- K-5 rebuilding the cv2x registry on `EthereumDIDRegistry`;
- K-7, K-9, K-10 redesigns, which change what a standard's column means. These are
  documented as threats to validity, not changed.

## Exit criteria
- No open session-owned Critical or High.
- CI green on the pushed head.
- Every moved number has a register row with its old value and reason.
- `HANDBACK_2026-10-03.md` and `review02/AAR_REVIEW2_03.md` closed.
