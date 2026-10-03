# After-Action Report 03 — Executing the Handback's "Next Session" List

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Started:** 2026-10-03, before any work of the pass; updated as it runs; closed at the end
**Trunk at start:** `3203ee8`, clean, CI green
**Input:** `docs/HANDBACK_2026-09-30.md` §4 "Next session (executable now, in this order)"

## 0. The brief
The author said "continue". Nothing new was requested, so the pass executes the
handback's list of work that needs no author input, in the order written there:

| # | Item | Source | Status |
|---|---|---|---|
| N1 | M1 — clause-level reconciliation of the MOBI VID implementation with the standard text | `PLAN_MOBI_SUMO.md` M1 | ⏳ |
| N2 | Resolver fixes for the five external-conformance root causes; re-run the W3C DID test suite | `docs/conformance/W3C_DID_TEST_SUITE.md` | ⏳ |
| N3 | M4 — lifecycle-parity comparison against the centralized registry (closes SC-13) | plan M4 | ⏳ |
| N4 | Freshness-k cached-verifier experiment (review §5.1) | `LATENCY_BUDGET.md` §4 | ⏳ |

Not in this pass (need the author): SUMO install (S0), chapter framing edits, Sepolia.

## 1. Plan
- N2 and N4 are bounded code-plus-measurement tasks with clear acceptance criteria
  (suite pass count goes up; a P* vs k table exists). They run as two delegated
  tasks in parallel. Acceptance is checked by re-running their outputs here, not by
  trusting their reports.
- N1 is done directly: fetch the MOBI VID I preview text, build the clause table
  against contracts/Python/tests, record out-of-scope clauses in `SCOPE_CHANGES.md`.
- N3 follows N4 (same experiment script; avoids two edits colliding).
- Commit at every step boundary; this report's §2 log is updated at each.

## 2. Execution log
- 2026-10-03 — report opened; state check, MOBI text fetch and two delegations
  requested in the same step.
- State check: trunk `3203ee8` clean and synced; both node_modules trees, the Python
  deps and the did-test-suite clone survived — no re-provisioning needed.
- N1: the MOBI VID I PDF (213 KB) could not be read by the fetch tool; extracted with
  pdfminer (pypdf was blocked by the cryptography/cffi conflict seen earlier). Result:
  it is the **public preview** — front matter, TOC, foreword, introduction; the
  normative sections are member-only. That is the central M1 finding (SC-14):
  conformance can only be claimed at the level of published concepts, and the
  standard's vocabulary (UVI, Entity/Revocation Certificate, Roles 1–4, DVM) was never
  mapped. `docs/MOBI_VID_CHECKLIST.md` written: coverage map against the TOC,
  vocabulary mapping, thesis changes. N1 done to the extent the public text allows.
- N2, N4 delegated (resolver conformance; freshness-k measurement) — running.
- N2 done and accepted here: official suite 328/441 → **335/336** (resolution 193/194; the one failure is a suite vector generically valid under the 3.1 ABNF), internal checker 93.2% → **94.3%**, VC tests 60/60 unchanged; malformed DIDs now yield `invalidDid`, unknown methods `methodNotSupported`, success results carry no error keys, `resolveRepresentation` exists. CI floor raised 93.0 → 94.0; register #4/#24, summary and README updated.
- N4 done and accepted here (anchor rows reproduced on a fresh node, n=60: k=1 3.10 ms / 1 RPC, k=∞ 0.456 ms / 0 RPC): the budget's two estimate rows are now measured (0.44 and 2.70 ms vs 0.40 and 2.5 estimated); the k-sweep shows median P* saturating at ≈110 from k=5 and the mean-based crossing of P*(0.5)=100 between k=25 and k=100; revocation bound holds for every finite k. Register #29; host-speed caveat recorded (2.80 vs 2.10 GHz). Default provider path unchanged (freshness off).

## 3. Decisions
- **D1** — follow the handback order for N1 but run N2 and N4 concurrently, because
  they touch disjoint files (`2_w3c-ssi-layer/did-resolution/` vs
  `cv2x-testbed/scripts/`, `cv2x-testbed/identity/`) and both are latency-bound.

## 4. Closing sections — *(written last)*
