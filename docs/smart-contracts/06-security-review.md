# 06 — Security review: exploitability check, fixes and static analysis

Phase 1 annotation listed caveats per contract (`@custom:security` in the sources, "caveats" in docs
01–05). Phase 3 re-checked the serious ones: for each, is there a realistic path from a real caller
to a broken invariant? Each verdict below is a fix, an open item kept documented, or "not
exploitable". The rule followed was to change contract code only where the path is real and the
fix is proportionate, because every bytecode change can move gas results of record.

## 1. Verdicts

| Finding | Contract | Verdict | Reasoning |
|---|---|---|---|
| Re-entrancy in `mintVehicle` | `CVINVehicleNFT` | **Fixed** | `_safeMint` called the recipient's `onERC721Received` before `vinToTokenId` was written. A receiver holding `MANUFACTURER_ROLE` could re-enter with the same VIN and pass the "VIN already minted" check, giving two identities for one vehicle. Reproduced by `test/L2-identity-system/per-option/ERC721/mintReentrancy.regression.test.js`, using `contracts/test/ReentrantVinReceiver.sol`; the test failed before the fix and passes after. Fix: write the VIN maps before `_safeMint` (checks-effects-interactions). Execution gas is unchanged: ERC-721 `create` stays at 545,197 in `sandbox/grand/report/L1-asymmetry.md`, and every non-deployment cell reproduces. ERC-721 deployment moved by +12 gas, from 2,787,276 to 2,787,288, because the source edit changed the metadata hash. The gas results of record were re-run for this (register rows #25, #31, #34). |
| Action not bound into the ZK proof | `ZkVinGate` | **Open (documented)** | Public signals are `[nullifier, commitment, mfrRoot, minModelYear, region, scope, challenge]`; `action` is not among them. Anyone who sees a pending `admit` can resubmit the proof with another action and spend the nullifier first. That is griefing: the vehicle loses its one admission per scope. Fixing it needs `action` (or `msg.sender`) as a circuit input, which means a new trusted setup, a new hash-pinned `Groth16Verifier.sol` and a re-measured 301,163-gas `admit` result of record. That is a dedicated change, not a patch. |
| Single-party Groth16 setup | `Groth16Verifier` | **Open (documented)** | Research setup with fixed entropy, so whoever ran it can forge proofs. Production would need a multi-party ceremony. This is out of scope for code changes. |
| Guardian can take over instantly | `CVINVehicleAccount` | **Open (design)** | `recoverOwner` is the intended social-recovery path: the owner chooses the guardian. A time-lock or veto window would be a design change to the option being compared, not a bug fix. |
| `updateOwnershipMapping` callable by anyone | `CVINVehicleDIDRegistry` | **Not exploitable** | It succeeds only if `identityOwner(oldOwnerDID) == newOwnerDID`. Only the ERC-1056 owner can establish that, using `changeOwner`. Any caller can therefore only carry out the sync the owner already authorised. The stale in-body comment is flagged in NatSpec. |
| No EIP-2 low-s check | `CVINVehicleAccount`, `CVINCombinedIdentity` | **Not exploitable** | Malleability only matters if signature bytes act as a replay key. The 4337 account consumes a nonce per operation; claims are keyed by `keccak256(issuer, topic)`, and Combined's revocation key is the digest. |

## 2. Test-gap fix: ZkVinGate mutation probe

`5_zkp-agent-identity/mutate_zkvin_gate.sh` removes each of `ZkVinGate`'s 12 guards in turn. The
layer-5 suite must fail on each mutant; this is the same pattern as `phase2/idtx/mutate_idtx.sh`.
On its first run **3 mutants survived**: no test covered the governor-only `setService`, the
unknown-service revert or the region-signal check. One new test in
`5_zkp-agent-identity/test-contracts/zkvin_gate.test.js` now catches all three (0 of 12 survive).
CI runs the probe in `zkp-layer5.yml`.

## 3. Static analysis (Slither 0.11.6, main project)

Run with
`cd 1_blockchain-identity && npx hardhat compile && slither . --hardhat-ignore-compile --filter-paths "node_modules|_research-copies|contracts/test"`
(`contracts/test` is filtered out because it holds only the test attacker contract). Result on the
Phase 3 tree, after removing duplicates: 66 findings, of which 3 High, 2 Medium, 21 Low, 37
Informational and 3 Optimization. Every High and Medium finding is triaged below, together with the
Low items that touch the findings above:

| Detector (impact) | Where | Triage |
|---|---|---|
| arbitrary-send-eth (High) | `CVINVehicleERC725XY._executeCall` | **By design.** ERC-725X `execute` with operation CALL; only the owner can call it (`onlyOwner`). |
| controlled-delegatecall, delegatecall-loop (High) | `CVINVehicleERC725XY._executeDelegateCall` | **By design.** ERC-725X operation DELEGATECALL is owner-only, as the standard intends; doc 04 already notes that it lets the owner overwrite storage. |
| uninitialized-local (Medium) | `CVINVehicleCredential1155.credentialTypesOf` (`count`, `k`) | **False positive.** Solidity zero-initialises locals, and the code relies on that. |
| events-access (Low) | `MOBIVIDRegistry.transferRegistryAuthority` | **Known** (doc 02): the authority handover emits no event. Left as is, because adding an event changes MOBI bytecode, the testbed artifacts and gas. |
| missing-zero-check (Low) | `CVINVehicleAccount.setGuardian` / `execute`, `CVIN_DID_ERC725.transferOwnership` | Owner-only setters. Setting the guardian to zero is the documented way to disable recovery. The ERC-725 stub is not compared on security. |
| reentrancy-events (Low) | `CVIN_NFT_DID_ERC721.payToll`, `CVINMinimalEntryPoint.handleOp`, `CVINVehicleAccount.execute` | An event is emitted after an external call. No state is at risk: `payToll` writes no storage after forwarding the toll to the operator, `execute` is owner/EntryPoint-gated, and the EntryPoint is a single-op test harness. |
| timestamp, calls-loop, assembly, naming, … (Low/Info) | various | Expected for expiry-based identity (ERC-1056 validity) and the hand-written verifiers. |

Slither raised nothing about the `mintVehicle` re-entrancy: its reentrancy detectors do not model
`_safeMint`'s receiver callback into a role-gated function. That gap is why the verdicts in
section 1 were reached by tracing call paths rather than by trusting a tool.

## 4. Guards added so this stays true

| Guard | What it enforces | Where it runs |
|---|---|---|
| `tools/check_natspec.js` | Every project contract has NatSpec on each contract, public/external function, event, modifier and public state variable, with `@param`/`@return` coverage. Generated `Groth16Verifier.sol` is exempt. | `zkp-layer5.yml` (contracts job) |
| `tools/bytecode_manifest.js --check` | The executable bytecode and ABI of all project contracts match `docs/smart-contracts/bytecode-manifest.json`, ignoring the metadata tail. Comment edits pass; any code change must update the manifest in the same PR, which makes re-measuring gas a visible review item. | `zkp-layer5.yml` (contracts job) |
| `5_zkp-agent-identity/mutate_zkvin_gate.sh` | Each `ZkVinGate` guard is covered by a test. | `zkp-layer5.yml` (contracts job) |
