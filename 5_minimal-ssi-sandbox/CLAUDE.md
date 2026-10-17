# CLAUDE.md — CVIN-SC Identity Sandbox (build agent instructions)

You are the build agent for the CVIN-SC identity sandbox, the experimental
environment of a UBC ECE MASc thesis on blockchain-based Self-Sovereign
Identity for connected vehicles, IoT, and AI agents. The architecture was
decided in the Main Build Chat; your job is faithful build-out, not redesign.

## Read first, in order
1. `docs/ARCHITECTURE.md` — what is tested (Set A/B/C), on what (families/options), scenario catalog, verified state
2. `docs/BRINGUP.md` — environment, bring-up sequence, expected outputs
3. `BUILD_DIRECTIONS/BUILD_PLAN.md` — your ordered work orders (WO-0 … WO-9)
4. `traces/SCHEMA.md` — the trace contract; never break it without versioning it

## Project commands
```
npm install                          # toolchain (hardhat 2.x + local solc-js)
npx hardhat compile                  # must stay green at every commit
npx hardhat test                     # 12-test compliance suite per enabled option
IMPL=<Name> npx hardhat run scenarios/run_i2i.js    # S1; writes traces/*.jsonl
```
Compilation uses the npm-installed solc-js via a subtask override in
`hardhat.config.js` (binaries.soliditylang.org may be unreachable). Do not
remove that override.

## Hard rules (violations = stop and report)
1. **Spec is normative.** `contracts/interfaces/IMinimalSSI.sol` (+ ISetA/ISetB/ISetC)
   implement the formal specification. Never alter interface signatures, errors,
   or events to make an implementation pass. If a standard genuinely cannot
   satisfy a function natively, implement the documented anchor/adapter pattern
   and annotate the coverage consequence — do not stub to green.
2. **Native patterns, never wrapped registries.** Each option uses its standard's
   own mechanics: O1 event-sourced; O2 actually mints soulbound ERC-721; O3 uses
   ERC-725Y getData; O4 adds ERC-735 claims + key purposes; O5 enforces soulbound
   ERC-1155; O6 routes authorization through validateUserOp-style validation keys;
   O7 implements the three ERC-8004 registries (Identity/Reputation/Validation);
   O8/E1 adapts Indy nymTx semantics to Solidity. A generic registry with eight
   façades would invalidate the comparative evaluation.
3. **Family F (CVIN Combined) is a Stage 3 output.** Never scaffold or implement
   it; it is synthesized from gap analysis only.
4. **Admission = compliance.** An option enters `IMPLEMENTATIONS` in
   `test/compliance.js` only when all 12 tests pass unmodified.
5. **Traces are evidence.** Every scenario emits JSONL per `traces/SCHEMA.md`.
   Real gas only — never fabricate, estimate, or copy gas numbers between options.
   Committed traces are immutable; new runs are new files.
6. **Deviations are findings.** When measurements miss spec §5.3 gas targets or
   prior scoring anchors (ARCHITECTURE.md §2.1) by a wide margin, record it in
   `docs/FINDINGS.md` with the cause — do not silently optimize the deviation
   away if the cause is architectural (e.g., O1 explicit-DID storage cost).
7. **No scope invention.** Anything not in a work order goes to
   `BUILD_DIRECTIONS/PROPOSALS.md` as a proposal, not code.

## Conventions
- Solidity 0.8.24, optimizer 200 runs; custom errors over require-strings;
  events on every state change; view functions return structured data and
  never revert on absent records (resolveDID/verifyCredential/validDelegate).
- One option per file: `contracts/implementations/O<N>_<Standard>.sol`.
- OpenZeppelin allowed for token bases (O2/O5); pin versions in package.json.
- Tests: extend the parameterized suite; never per-option forks of it.
- Scenario scripts go in `scenarios/`, named `run_<id>.js` matching the catalog
  IDs (S1…S6) in `docs/ARCHITECTURE.md` §4.
- Update `docs/FINDINGS.md` and the relevant doc tables in the same commit as
  the code that produces the result.

## Definition of done (every WO)
compile green → compliance green for all enabled options → scenario(s) rerun
with fresh traces → docs updated (status tables + findings) → one-paragraph
summary appended to `BUILD_DIRECTIONS/BUILD_LOG.md` (date, WO, what changed,
gas/coverage numbers, surprises).
