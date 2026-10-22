# Lineage Relation, 2026-10-22: the cv2x-testbed Workspace (W) and the Trunk (T)

**Author:** Nikhil Prakash (MASc, UBC ECE). **Plan 5, phase 1** (guide rule 1.3.6: read the other branch and write
down its relation before merging). **Written before** any merge commit.

## 1. The two lineages

- **Common base:** `b7997f8` ("Report 18 closed").
- **W** = `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy`, head `ec7e19b` (22:05 UTC, active): 49 commits.
- **T** = the default branch `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt`, head `4005a60` (PR #5): 82 commits
  since the base (layer 5 and Plans 1–4, plus the clone lineage merged in PR #3).
- **Files changed on both sides:** 53; a trial merge leaves **43 conflicted** (§4).

## 2. What W did (reports 19–27, numbered on W)

| W report | Work | Overlaps T? |
|---|---|---|
| 19 | Contribution record; **WM-2 C3**: #32 and #37 at their own code on one host, two replicates in opposite order (register **#52**) | yes: T's #54 (clone lineage H-K) measures the same question by a different design |
| 20 | Technical Data Package (TDP-001…010) in an engineering register | no |
| 21 | **WM-2 C1**: did:ethr resolution reads ERC-1056 when given a provider (`blockchain_provider`, `registries={chain: address}`) | yes: T's H-R resolver (`blockchain_provider`/`rpc_url` + `ethr_registry`/`mobi_registry`; did:ethr and did:mobi on chain; change-chain walk; external suite 311/311) |
| 22 | **WM-2 C2** (D54): `MOBIVIDRegistry` stores delegations (`validDelegate`); `attestEvent` requires the vehicle's owner or a `veriKey` delegate, once; D54 **fixed** | yes, and conflicting: T's H-A (OWNER role must be the owner; organisational roles keep registry-wide scope; D54 narrowed, open) |
| 23 | Phase 2 session 3: deep-dive briefs I-24 (IDTx), I-05 (freshness theory) | touches `ideas.yaml`, `IDEA_REGISTER.md` (T added `status` entries) |
| 24 | Decision sheet, `tools/prepush_check.sh`, progress report | no |
| 25 | TDP runbook phase 10: thesis adaptation map onto chapter 3 | chapter 3 (T added §3.9) |
| 26 | Chapter 2 draft sections 2.4a and 2.6 (separate file); chapter 6 §6.8 IDTx (separate file) | yes: T's full chapter 2 and T's §6.8 (layer 5) in the README |
| 27 | TDP runbook phases 8 and 9: requirement-to-test trace, ICD gate `check_icd.py` in CI | no |

## 3. The design question: C2 (decides phase 3)

| | T (H-A) | W (C2, report 22) |
|---|---|---|
| Who may attest | any role-holder; an OWNER-role attester must be the current owner | the vehicle's owner or its stored `veriKey` delegate, and holding a role |
| Organisational roles | registry-wide (by design) | only as the owner's delegate |
| Duplicates | `hasAttested`, "Already attested by this attester" | `hasAttested`, "Already attested" |
| Delegation storage | none in MOBI (events only, K-5) | stored in `MOBIVIDRegistry` (`addDelegate` +22,346 gas) |
| D54 | narrowed, open | fixed |

W's rule implies T's (an owner-or-delegate attester that is OWNER-role is the owner), so taking W loses no protection
T has. It removes the organisational roles' registry-wide scope, which T kept as a design choice; W's report 22
records that choice as the defect. **Resolution (default I-a):** W's design; T's H-A tests are kept where they still
hold (previous owner refused, duplicate refused) with W's revert strings, and the "organisational role attests any
vehicle" expectation is rewritten to W's rule with the reason stated. The auto-merge of the contract keeps *both*
checks and the duplicate guard twice; it must be resolved by hand.

## 4. Conflicted files and their resolution

| Group | Files | Resolution |
|---|---|---|
| Contracts | `MOBIVIDRegistryV2.sol` (both copies) | W's `attestEvent`; one `hasAttested`; testbed copy byte-identical (CI) |
| Contract tests | `attestEventRegression.test.js`, `MOBIVIDRegistry.test.js` (auto-merged), `securityScenarios.test.js` (auto-merged) | W's pin method, re-measured on the merged bytecode; H-A cases adapted (§3) |
| Resolver | `did_resolver.py` (5 hunks) | T's engine (did:mobi, change walk, D21 event) behind both constructor forms: W's `registries={chain: addr}` and T's `ethr_registry`/`rpc_url`; both test suites must pass |
| Demo | `sandbox/options/mobi-vid/demos/claims.js` | W's revert string |
| Registers | `MEASUREMENT_CONDITIONS.md`, `DEFECT_LOG.md`, `THREAT_MODEL.md`, `PLAN_WM-2.md` | W's rows and entries kept; T's rows **#52–#61 → #53–#62**; D54 "fixed" (W) with H-A recorded as the superseded design; C1/C2/C3 entries from W, T's A3 and pass-22 notes appended |
| Reports | `AFTER_ACTION_REPORT_19…22.md` (add/add) | W's keep the numbers; T's become **28–31**, each with a renumbering note; T's report text referring to "report 20/21/22" updated |
| Handback, manifest | `HANDBACK_2026-10-14.md`, `SESSION_MANIFEST_2026-09.md` | both sides' addenda kept, ordered by date, renumbered sections |
| Tooling | `check_stamps.py`, `make_result_cards.py`, `test_register.yaml` | union of both sides' entries; card and class numbers follow the renumbering |
| Generated | results JSON/CSV/TeX, artifacts, dashboards, cards, presentation, grand report, matrices, stamp inventory, crux register, mode classification | either side, then regenerated on the merged tree (phases 4–5) |

## 5. Renumbering (T → merged)

| Item | T | Merged |
|---|---|---|
| Register rows (basic set, P1/X1, same-host freshness, layer 5) | #52, #53, #54, #55–#61 | **#53, #54, #55, #56–#62** |
| After-action reports (Plan 1, PR #3 merge, Plan 3, Plan 4) | 19, 20, 21, 22 | **28, 29, 30, 31** (this pass: **32**) |
| Chapter 6 layer-5 section | §6.8 | **§6.9** (W's IDTx keeps §6.8) |
| Chapter 2 | T's full draft §2.1–§2.7 | W's §2.4a (revocation freshness) and its §2.6 (IDTx) merged into T's §2.4 and §2.6 by topic, sources unioned |

## 6. What each side's tests assert that the other may break
- W's `test_did_resolver_chain.py` (constructor with `registries`) against T's resolver: fails unless both forms exist.
- T's `test_did_resolver_onchain_{ethr,mobi}.py` against W's resolver: fails (no did:mobi chain path).
- T's H-A tests against W's contract: the organisational-role case and the revert strings fail.
- W's C2 tests against a merged contract with H-A's extra OWNER check: pass (the check is implied) but the gas pin moves.
- Every gas row that includes MOBI moves (W measured addDelegate 57,667, attestation 222,082 on its tree).
