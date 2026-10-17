# Native Sandbox Build and Verification Methodology

**CVIN-SC Research Programme · v1.0 · June 2026**
*Repository twin of the formal methodology document (CVIN_Native_Sandbox_Build_and_Verification_Methodology_v1-0.docx). Registry: Type A/B → Ch. 4 Methodology; Appendix fallback.*

This document records the method by which every empirical claim in this
repository is produced. It is written so that an independent researcher can
re-execute the evaluation campaign from the repository alone.

## 1. Principles

The methodology rests on three rules. Every quantitative claim is reproducible
from a committed JSONL execution trace; the trace, not the prose, is the
evidentiary artifact. No claim graduates from expectation to verdict except by
passing a named verification gate whose procedure and evidence output are
specified in advance. Unresolved knowledge is carried as enumerated placeholder
tokens with declared resolution authorities, so provisional documents can
circulate without provisional content masquerading as fact.

## 2. Two-layer, trace-driven design

Layer 1 is this Hardhat project: every option implemented against the shared
interface set (IMinimalSSI, decomposed into ISetA, ISetB, ISetC), with scenario
scripts emitting traces per `traces/SCHEMA.md` (function ID F1–F12, acting
principal, tx hash, gas, events, reverts). Layer 2 is visualization, which
replays traces and never simulates. Committed traces are immutable; new runs
are new files.

## 3. Verification gates

A gate has four declared components: purpose, executor, procedure, and
evidence output. Two evidence classes flow through gates. Documentary evidence
(repository states, package versions) resolves research tokens. Empirical
evidence (compile compatibility, behavioural verdicts, gas) resolves test
tokens, and no documentary source may resolve an empirical token: what
documentation claims about compatibility is subordinate to whether the code
compiles in the pinned toolchain.

| Gate | Purpose | Executor | Evidence output |
|---|---|---|---|
| G0 | Bring-up: install, compile, 12/12 baseline | Operator | Compile log, test output |
| G1 | SP-1 control rerun on operator hardware | Operator | Fresh S1 trace |
| G2 | Package compatibility at 0.8.24 | CLI agent | Compatibility table (FINDINGS.md) |
| G3 | T-725 series: container, key purposes, deactivation | CLI agent | Verdicts, gas |
| G4 | T-735 series: claims-as-credentials, holder-removal | CLI agent | Verdicts |
| G5 | T-740 series: registry gating, delegate expiry; full compliance + scenario | CLI agent | Verdict file, SP-2 trace |
| G6 | Evidence merge; document graduation Provisional → Final | Architect | Final document, verdict tables |

Operator-facing commands and verbatim CLI prompts live in the companion
Operator Guide; work orders WO-1a, WO-1b, and WO-R in
`BUILD_DIRECTIONS/BUILD_PLAN.md` are the executable form of gates G2–G5.

## 4. Solution paths

The Stage 1 evaluation unit is a single option or a solution path: a named
composition of an EVM identity anchor with the Family E credential stack.
SP-1 (ERC-1056 anchor + credential anchor pattern) is the verified control.
SP-2 (ERC-725/735 composite + claim-issuer registry [R1]) carries an
expectation matrix until gates G3–G5 deliver verdicts. Solution paths reuse
existing option numbers; they never extend the master table.

## 5. Behavioural test design

Where a standard's native semantics diverge from the specification's
assumptions, behavioural test series settle the question: T-725 (container and
key purposes, last-management-key guard, deactivation irreversibility), T-735
(issuer binding, revocation symmetry, the holder-removal question), T-740
(issuer-registry gating of verification, registry-level revocation, expiry over
purpose-2 keys). Each test writes a typed verdict (F/P/×) to
`traces/sp2_verdicts.json`; verdict files, not test prose, update coverage
matrices. Expectation-versus-verdict deviations are findings and are logged to
`docs/FINDINGS.md`.

## 6. Division of labour

Three roles. The architect (persistent planning agent) owns design, documents,
and the evidence merge, and never fabricates measurements. The operator (the
researcher) owns gate execution authority and is the human checkpoint between
the coding agent and the evidentiary record. The CLI agent (bound by
`CLAUDE.md`) owns implementation and tests under standing rules: no interface
alteration, native patterns only, real gas only, deviations logged as findings.

## 7. Reproducibility envelope

Toolchain pinning (solc vendored via npm and loaded through the Hardhat
subtask override, so builds are identical in air-gapped and CI contexts),
trace immutability, the placeholder register, and gate artifacts together
allow the evaluation chapters to cite repository artifacts the way
experimental sciences cite instrument readings.
