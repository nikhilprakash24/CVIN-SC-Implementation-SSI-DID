# IDTx Core — Live Progress

**Updated:** 2026-10-24 · **Decision:** A+ (thesis is home; overflow → Appendix G / companion SP-9, returnable)

## Phase roadmap

```
Phase 1  function set, IDTx, benchmark gap   [■■■□□□□□□□]  ~30%   IN PROGRESS
Phase 2  compare to other ID systems         [□□□□□□□□□□]    0%   planned
Phase 3  nearest benchmarks, benchmark v0     [□□□□□□□□□□]    0%   planned
Phase 4  same, for AI agents                  [□□□□□□□□□□]    0%   planned
Phase 5  10-substrate × function-set matrix   [□□□□□□□□□□]    0%   planned
Phase 6  IDTx + compound scenarios visualized [□□□□□□□□□□]    0%   planned
```

## Phase 1 work packages

| WP | Task | Agent | Status |
|---|---|---|---|
| 1.1 | Function→code/test/register map, 10 substrates | RC (Explore) | ✅ done → `p1/FUNCTION_MAP.md` |
| 1.2 | Clear [B1] cells (verbatim F1–F12) | ED + author | ⏸ blocked on archive |
| 1.3 | Primitive cards (protocols/algorithms) | SS | 🔵 running |
| 1.4 | Pseudocode (F1–F12 + IDTx) — **author will double-check** | CE | 🔵 running |
| 1.5 | Analogy matrix (centralized / digital-ID / CAV) | SS | 🔵 running |
| 1.6 | Benchmark-gap evidence | LS | 🔵 running |
| 1.7 | IDTx prior-art positioning | LS | ⬜ queued |
| 1.8 | Figures P1-1…P1-6 | VA | ⬜ queued |
| 1.9 | Thesis drafts (Ch 3 §3.x, Ch 6 §6.8, Ch 2 §2.6, App. G) | ED | ⬜ queued |
| 1.10 | Examiner pass (draft only) | SK | ⬜ queued |
| 1.11 | CI: figure + link checks | ED | ⬜ queued |

Legend: ⬜ queued · 🔵 running · ✅ done · ⏸ blocked · ⚠ needs author

## Running log (newest first)

- `2026-10-24` ED — WP 1.1 ✅ complete: `p1/FUNCTION_MAP.md`. All 12 functions + IDTx mapped across 10 substrates + MOBI-VID + ZkVinGate with file:line and guarding tests. Two NOT-FOUND-by-design cells recorded (ERC-1056 has no attribute-value read fn; MOBI-VID has no per-event revoke). Flagged a duplicate `validateUserOp` in the ERC-4337 account for CE to confirm. Launched WP 1.3 / 1.4 / 1.5 / 1.6 in parallel.
- `2026-10-24` ED — PROGRESS dashboard created. Launched WP 1.1 (Repo Cartographer) to build the function→code map.
- `2026-10-24` ED — Decision P2-D8b recorded: **A+**. Detailed plan + placement map committed (`c2c423b`). Appendix G and SP-9 registered.
- `2026-10-24` ED — Plan, agent team, Phase 1 kickoff committed. Grounded in `ANALYSIS.md` §4, `BASIC_ID_SET_EXTENSION.md`, `IdtxExecutor.sol`.

## Decisions log

| ID | Decision | Date |
|---|---|---|
| P2-D8b | Core work goes in the thesis (home); overflow to Appendix G or companion SP-9, both returnable. Measured gas study stays P5. | 2026-10-24 |

## Author to-do (audit checkpoints)

- [ ] WP 1.4 pseudocode — you will verify line-by-line against the Solidity.
- [ ] Supply `cvin-sandbox-v1.3` archive (or F1–F12 signatures) to clear [B1].
- [ ] Function-naming: left to my judgment for clarity (per your note).
