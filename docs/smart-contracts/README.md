# Smart-contract catalog

Annotated reference for every Solidity contract in this repo: the standards (EIPs/ERCs/LSPs/W3C specs)
each one implements and how faithfully, a per-function table, design and security caveats, and
**where, when and how** each contract is used (deploy scripts, Hardhat tests, sandbox adapters,
benchmarks, Python layers, docs).

Two layers of annotation:
- **Inline NatSpec in every compiled `.sol` file** (`@notice`/`@dev`/`@param`/`@return`, plus
  `@custom:standard`, `@custom:security`, `@custom:see` and `@custom:note`). This is the short
  version, visible in IDEs, `solc --userdoc/--devdoc` and block explorers. Exceptions: the
  snarkjs-generated, hash-pinned `Groth16Verifier.sol`, and the uncompiled `_research-copies/`.
- **These docs:** the long version, with standards fidelity, usage maps, Mermaid diagrams and ethers examples.

The **[API reference](api/README.md)** (one page per source, generated from the NatSpec by
`tools/make_contract_api_docs.js` and checked in CI) lists every public function, event, error,
modifier and state variable with its parameters.

Start with [00 – Architecture](00-architecture.md): the overall diagram, the standards → contracts
matrix, the NatSpec conventions, and how the comments-only claim was verified (bytecode is identical
once the metadata is stripped).

| Doc | Contracts | Standards / protocols |
|---|---|---|
| [00 – Architecture](00-architecture.md) | all | overview, matrix, conventions |
| [01 – ERC-1056 DID registry](01-erc1056-did-registry.md) | `1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol`, `CVINVehicleDIDRegistry.sol` | ERC-1056, did:ethr, W3C DID Core (resolver in `2_w3c-ssi-layer/did-resolution`) |
| [02 – MOBI VID](02-mobi-vid.md) | `1_blockchain-identity/contracts/MOBI/{ERC1056Registry,MOBIVIDRegistry,MOBIVIDRegistryV2}.sol` (identical copies in `cv2x-testbed/contracts/`) | MOBI VID I/II, ERC-1056, did:ethr, W3C VC, EIP-191 |
| [03 – Token standards](03-token-standards-erc721-erc1155-lsp8.md) | `ERC721/{CVINVehicleNFT,CVIN_NFT_DID_ERC721,CVIN_NFT_DID_ERC721_Monolithic}.sol`, `ERC1155/CVINVehicleCredential1155.sol`, `LSP8/CVINVehicleLSP8.sol`, `_research-copies/ERC721` | ERC-721, ERC-1155, ERC-165, ERC-2981, LUKSO LSP8, ISO 3779 |
| [04 – Account & claim identity](04-account-claim-identity-erc725-735-4337-combined.md) | `ERC725/CVIN_DID_ERC725.sol`, `ERC725xy/{CVINVehicleERC725XY,CVINExecuteTarget}.sol`, `ERC735/CVINVehicleClaimHolder.sol`, `ERC4337/{CVINVehicleAccount,CVINMinimalEntryPoint}.sol`, `CVINCombined/CVINCombinedIdentity.sol` | ERC-725 (v1, X/Y), ERC-735, ERC-4337, EIP-191 |
| [05 – ZKP & IDTx](05-zkp-and-idtx.md) | `5_zkp-agent-identity/contracts/{Groth16Verifier,SchnorrEcrecoverVerifier,ZkVinGate}.sol`, `phase2/idtx/contracts/IdtxExecutor.sol` (+ `IdentityCommitments`) | Groth16 / snarkjs, EIP-196/197, circom + Poseidon, Schnorr-via-ecrecover, ERC-1056 |
| [06 – Security review](06-security-review.md) | all | Exploitability verdicts, the `mintVehicle` fix, Slither triage, CI guards (NatSpec lint, bytecode manifest, ZkVinGate mutants) |

## Cross-cutting usage map

| Consumer | What it does with the contracts |
|---|---|
| `sandbox/options/*/adapter.js` (+ `manifest.yaml`, `demos/`) | One adapter per option wraps a contract behind the uniform `sandbox/lib/identity_option.js` interface; each header maps methods → contract functions (see `sandbox/options/ADAPTER_CONVENTIONS.md`). Run via `sandbox/grand/smoke.js` / `run.py`. |
| `1_blockchain-identity/test/` | L1/L2 Hardhat tests per option. |
| `1_blockchain-identity/scripts/` | `benchmark_gas.js`, `benchmark_scaling.js`, `security_scenarios.js`, `infrastructure_gas.js`, `mobi_vid_backend_sweep.js`, `validate_sepolia.js`, `deployERC1056.js`. |
| `4_comparison-framework/` | Consumes gas/security results; `feature-matrix/make_feature_matrix.py`. |
| `cv2x-testbed/` | `deploy.js` / `deploy_mobi_vid.js`; Python providers in `identity/` talk to `ERC1056Registry` / `MOBIVIDRegistryV2`. |
| `5_zkp-agent-identity/`, `phase2/idtx/` | Own Hardhat configs (`hardhat.zkp.config.js`, `hardhat.phase2.config.js`); reuse the compiled `EthereumDIDRegistry` artifact. |

## Notable findings surfaced during annotation

Details and line refs are in each doc. Highlights:
- Stub/partial implementations: `CVIN_DID_ERC725` (`execute` only emits, `approve` is empty), LSP8 subset (no LSP1 hooks/operators/ERC-165), minimal 4337 EntryPoint.
- Spec deviations: hashed attribute/delegate names in the ERC-1056 wrappers and MOBI (invisible to a stock did:ethr resolver); 1155 transfers always revert (soulbound).
- Security caveats, re-checked for exploitability in Phase 3 (see [06 – Security review](06-security-review.md)):
  - **Fixed:** the re-entrancy window in `CVINVehicleNFT.mintVehicle` (a manufacturer-role receiver could mint one VIN twice; there is now a regression test).
  - **Open, documented:**
    - `ZkVinGate`'s action is not bound into the proof, so a copied proof can be front-run and burn the nullifier (griefing). The fix needs a circuit change.
    - Groth16 single-party setup.
    - The 4337 guardian can take over instantly (a recovery-design choice).
  - **Not exploitable:**
    - `updateOwnershipMapping` is callable by anyone, but the ERC-1056 owner already fixed the outcome.
    - There is no low-s check in the 4337 account or Combined, but the nonce and the issuer/topic claim ids already prevent replay.
- Stale material: `_research-copies/ERC721` monolithic balance bug; stale NatSpec in `CVINCombinedIdentity` (L119-127); draft contract embedded in `MOBI_VID*` root specs.
