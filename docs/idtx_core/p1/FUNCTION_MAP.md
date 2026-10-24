# WP 1.1 — Function → Implementation Map

**Home:** Appendix G-A (support table) · **Produced:** 2026-10-24 by Repo Cartographer (Explore)
**Status:** draft; `file:line` citations to be spot-checked by CE during WP 1.4.

Path keys:
- `C/` = `1_blockchain-identity/contracts/`
- `A/` = `1_blockchain-identity/benchmarks/adapters/` (the symbol realising a capability when the substrate has no dedicated contract primitive — wraps a generic primitive)
- `CONF` = `1_blockchain-identity/test/benchmarks/adapters.conformance.test.js` — the parametrized gate that runs the same `it()` over all 10 adapters (loop at line 31); primary guard for the 10 substrates.

**Method note.** For the registry/account substrates (ERC-1056 pure+wrapper, ERC-725, ERC-725xy, ERC-4337, CVIN-Combined) most Set-B functions and presentation are **patterns over a generic write primitive** (`setAttribute`/`setData`/`addClaim`), not dedicated symbols — so the implementing symbol is the adapter method, with the underlying contract primitive in Notes. MOBI-VID and ZkVinGate are outside the 10-adapter gate and have their own suites.

---

### F: createDID (C1/C2 create identity)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1056 pure | `A/erc1056.adapter.js:50` → `C/ERC1056/CVINVehicleDIDRegistry.sol:156` createVehicleDID | CONF:43 | identity implicit (every addr self-owned); wrapper binds VIN |
| ERC-1056 wrapper | `C/ERC1056/CVINVehicleDIDRegistry.sol:156` createVehicleDID | CONF:43 | adapter `A/erc1056w.adapter.js:34` |
| ERC-721 | `C/ERC721/CVINVehicleNFT.sol:112` mintVehicle | CONF:43 | adapter `A/erc721.adapter.js:48` |
| ERC-725 | `A/erc725.adapter.js:45` (deploys CVIN_DID_ERC725) | CONF:43 | identity = contract instance |
| ERC-735 | `A/erc735.adapter.js:55` (deploys ClaimHolder) | CONF:43 | identity = `C/ERC735/CVINVehicleClaimHolder.sol` instance |
| ERC-1155 | `C/ERC1155/CVINVehicleCredential1155.sol:94` registerVehicle | CONF:43 | adapter `A/erc1155.adapter.js:65` |
| ERC-725xy | `A/erc725xy.adapter.js:59` (deploys account) | CONF:43 | identity = contract instance |
| LSP8 | `C/LSP8/CVINVehicleLSP8.sol:171` mintVehicle | CONF:43 | adapter `A/lsp8.adapter.js:49` |
| ERC-4337 | `A/erc4337.adapter.js:75` (deploys account) | CONF:43 | identity = contract instance |
| CVIN-Combined | `A/cvin.adapter.js:59` → `C/CVINCombined/CVINCombinedIdentity.sol:254` addClaim | CONF:43 | implicit identity + VIN attestation claim |
| MOBI-VID | `C/MOBI/MOBIVIDRegistry.sol:227` registerVehicleBirth | `.../MOBIVID/MOBIVIDRegistry.test.js:89` | birth certificate |
| ZkVinGate | n/a | n/a | gate over an existing ERC-1056 identity; creates no DIDs |

### F: resolve (R1 owner / R2 by VIN / R3 document)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1056 pure | `C/ERC1056/EthereumDIDRegistry.sol:105` identityOwner; VIN `C/ERC1056/CVINVehicleDIDRegistry.sol:363` getDIDFromVIN | CONF:52 (R2); R3 CONF:65/92 | R3 doc rebuilt off eth_getLogs `A/erc1056.adapter.js:89` |
| ERC-1056 wrapper | `C/ERC1056/CVINVehicleDIDRegistry.sol:389` vehicleOwnerOf; `:363` getDIDFromVIN | CONF:52 | |
| ERC-721 | ownerOf (inherited); `C/ERC721/CVINVehicleNFT.sol:301` getTokenIdFromVIN | CONF:52 | |
| ERC-725 | `C/ERC725/CVIN_DID_ERC725.sol:33` owner | CONF:52 | R2 n/a (off-chain VIN index) |
| ERC-735 | `C/ERC735/CVINVehicleClaimHolder.sol:434` owner (Ownable) | CONF:52 | R2 n/a |
| ERC-1155 | `A/erc1155.adapter.js:72`; `C/ERC1155/...1155.sol:285` vehicleForVIN | CONF:52 | |
| ERC-725xy | `C/ERC725xy/CVINVehicleERC725XY.sol:120` owner; `:140` getData | CONF:52 | R2 n/a |
| LSP8 | `C/LSP8/CVINVehicleLSP8.sol:143` tokenOwnerOf; `:156` tokenIdForVIN | CONF:52 | |
| ERC-4337 | `C/ERC4337/CVINVehicleAccount.sol` owner() | CONF:52 | R2 n/a |
| CVIN-Combined | `C/CVINCombined/CVINCombinedIdentity.sol:164` identityOwner | CONF:52 | R2 n/a (VIN in a claim) |
| MOBI-VID | `C/MOBI/MOBIVIDRegistry.sol:506` lookupByVINHash; `:562` getVehicleInfo; `:598` getVehicleDID | `MOBIVIDRegistry.test.js:171,:287` | |

### F: changeOwner / rotate controller (U1/U4)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1056 pure | `C/ERC1056/EthereumDIDRegistry.sol:136` changeOwner (signed `:153`) | CONF:150 | |
| ERC-1056 wrapper | `C/ERC1056/CVINVehicleDIDRegistry.sol:259` transferVehicleOwnership | CONF:150 | |
| ERC-721 | transferFrom/safeTransferFrom (OZ) `A/erc721.adapter.js:87` | CONF:150 | ownership == control |
| ERC-725 | `C/ERC725/CVIN_DID_ERC725.sol:37` transferOwnership | CONF:150 | |
| ERC-735 | `C/ERC735/CVINVehicleClaimHolder.sol:434` transferOwnership | CONF:150 | |
| ERC-1155 | `A/erc1155.adapter.js:105` rotateController | CONF:150 | soulbound; via issuer re-mint |
| ERC-725xy | `C/ERC725xy/CVINVehicleERC725XY.sol:128` transferOwnership | CONF:150 | |
| LSP8 | `C/LSP8/CVINVehicleLSP8.sol:244` transfer (token) | CONF:150 | |
| ERC-4337 | `C/ERC4337/CVINVehicleAccount.sol:208` transferOwnership (+`:228` recoverOwner) | CONF:150 | |
| CVIN-Combined | `C/CVINCombined/CVINCombinedIdentity.sol:173` changeOwner | CONF:150 | |
| MOBI-VID | `C/MOBI/MOBIVIDRegistry.sol:448` transferVehicleOwnership | `MOBIVIDRegistry.test.js:185,:239` | |

### F: add / revoke delegate (U2/R4/D1)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1056 pure | `C/ERC1056/EthereumDIDRegistry.sol:190` addDelegate / `:256` revokeDelegate / `:120` validDelegate | CONF:61; rotate CONF:74 | |
| ERC-1056 wrapper | `C/ERC1056/CVINVehicleDIDRegistry.sol:333` addVerificationDelegate / `:348` revoke / `:414` isValidDelegate | CONF:61 | |
| ERC-721 | approve/getApproved (inherited) `A/erc721.adapter.js:60,92` | CONF:61 | single approved addr |
| ERC-725 | `C/ERC725/CVIN_DID_ERC725.sol:59` addKey(ACTION) / `:66` removeKey | CONF:61 | |
| ERC-735 | n/a | CONF:61 (n/a) | single MANAGEMENT key |
| ERC-1155 | n/a | CONF:61 (n/a) | no delegate keys |
| ERC-725xy | n/a | CONF:61 (n/a) | no LSP6 key manager |
| LSP8 | n/a | CONF:61 (n/a) | operators not implemented |
| ERC-4337 | `C/ERC4337/CVINVehicleAccount.sol:218` setGuardian | CONF:61 | revoke = setGuardian(0) |
| CVIN-Combined | `C/CVINCombined/CVINCombinedIdentity.sol:185` addDelegate / `:198` revoke / `:209` validDelegate | CONF:61 | |
| MOBI-VID | `C/MOBI/MOBIVIDRegistry.sol:333` addDelegate / `:344` revokeDelegate / `:356` validDelegate | MOBI suite | |

### F: set / revoke attribute (U3/R3, D2)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1056 pure | `C/ERC1056/EthereumDIDRegistry.sol:314` setAttribute / `:367` revokeAttribute | CONF:88, CONF:96 | |
| ERC-1056 wrapper | `C/ERC1056/CVINVehicleDIDRegistry.sol:315` setServiceEndpoint | CONF:88 | D2 n/a — no revokeAttribute |
| ERC-721 | `C/ERC721/CVINVehicleNFT.sol:197` addServiceRecord | CONF:88 | append-only; D2 n/a |
| ERC-725 | `C/ERC725/CVIN_DID_ERC725.sol:59` addKey(ATTRIBUTE) / `:66` removeKey | CONF:88,96 | attr encoded as a key |
| ERC-735 | `C/ERC735/CVINVehicleClaimHolder.sol:225` addClaim / `:290` removeClaim | CONF:88,96 | self-issued claim |
| ERC-1155 | `A/erc1155.adapter.js:118` setAttribute → issueCredential (badge) | CONF:88 | no free-form attr store |
| ERC-725xy | `C/ERC725xy/CVINVehicleERC725XY.sol:159` setData (revoke = setData(…,0x)) | CONF:88,96 | |
| LSP8 | `C/LSP8/CVINVehicleLSP8.sol:297` setDataForTokenId | CONF:88,96 | authority-written only |
| ERC-4337 | `C/ERC4337/CVINVehicleAccount.sol:239` setAttribute (revoke = …,0x) | CONF:88,96 | |
| CVIN-Combined | `C/CVINCombined/CVINCombinedIdentity.sol:224` setAttribute / `:235` revokeAttribute | CONF:88,96 | |
| MOBI-VID | `C/MOBI/MOBIVIDRegistry.sol:389` anchorVehicleKey; `C/MOBI/MOBIVIDRegistryV2.sol:244` recordLifecycleEvent | `MOBIVIDRegistry.test.js:116`; V2 `:381` | lifecycle events = attribute-like state |

### F: execute / agent-proxy (X1)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-725xy | `C/ERC725xy/CVINVehicleERC725XY.sol:216` execute (`:228` executeBatch) | CONF:140 | OPERATION_CALL |
| ERC-4337 | `C/ERC4337/CVINVehicleAccount.sol:186` execute | CONF:140 | account can act (A6: only native 12/12) |
| ERC-725 | `C/ERC725/CVIN_DID_ERC725.sol:80` execute | CONF:140 (n/a) | **stub**: emits Executed, performs no call |
| all others | n/a | CONF:140 (n/a) | registries/tokens cannot act |

### F: deactivate (D3)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-721 | `C/ERC721/CVINVehicleNFT.sol:260` deactivateVehicle | CONF:157 | only dedicated primitive |
| ERC-1056 pure | `A/erc1056.adapter.js:189` → setAttribute("did/deactivated") PERMANENT | CONF:157 | no native primitive |
| ERC-1056 wrapper | `A/erc1056w.adapter.js:70` → setServiceEndpoint(deactivated) | CONF:157 | |
| ERC-725 | `C/ERC725/CVIN_DID_ERC725.sol:43` renounceOwnership | CONF:157 | |
| ERC-725xy | `C/ERC725xy/CVINVehicleERC725XY.sol:134` renounceOwnership | CONF:157 | |
| ERC-735 | `A/erc735.adapter.js:133` → transferOwnership(0xdEaD) | CONF:157 | claims stay readable |
| ERC-4337 | `A/erc4337.adapter.js:135` → transferOwnership(0xdEaD) | CONF:157 | |
| ERC-1155 | `A/erc1155.adapter.js:128` → revokeCredential(all, incl BIRTH_CERT) | CONF:157 | burn credentials |
| LSP8 | `C/LSP8/CVINVehicleLSP8.sol:276` revokeVehicle | CONF:157 | |
| CVIN-Combined | `A/cvin.adapter.js:165` → setAttribute(deactivated) PERMANENT | CONF:157 | |
| MOBI-VID | revoke/freeze path in `C/MOBI/MOBIVIDRegistry.sol` (K-3 frozen-identity guard) | `MOBIVIDRegistry.test.js:255` | revoked identity frozen |

### F: issueCredential (V1 issuer-key anchor + V3 status anchor)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1155 | `C/ERC1155/CVINVehicleCredential1155.sol:121` issueCredential | CONF:110,119 | only native issue primitive |
| ERC-1056 pure | `A/erc1056.adapter.js:207` anchorStatus → setAttribute; V1 `:203` addDelegate | CONF:110 | pattern on `EthereumDIDRegistry.sol:314` |
| ERC-1056 wrapper | setServiceEndpoint pattern `A/erc1056w` | CONF:110 | |
| ERC-725 | `A/erc725.adapter.js:131` anchorStatus → addKey/setData | CONF:110 | |
| ERC-725xy | `A/erc725xy.adapter.js:126` → `C/ERC725xy/…:159` setData(credHash,"active") | CONF:110 | |
| ERC-4337 | `A/erc4337.adapter.js:161` → `C/ERC4337/…:239` setAttribute | CONF:110 | |
| ERC-735 | `A/erc735.adapter.js:147` → `C/ERC735/…:225` addClaim (+`:405` authorizeIssuer) | CONF:110 | V1 n/a (issuer key = EOA) |
| LSP8 | `A/lsp8.adapter.js:112` → `C/LSP8/…:297` setDataForTokenId | CONF:110 | V1 n/a (single authority) |
| CVIN-Combined | `A/cvin.adapter.js:180` → `C/CVINCombined/…:254` addClaim; V1 `:176` addDelegate | CONF:110 | |
| MOBI-VID | `C/MOBI/MOBIVIDRegistryV2.sol:338` attestEvent (+`:185` authorizeIssuer) | `MOBIVIDRegistry.test.js:381`; `attestEventRegression.test.js` | attestation = credential |

### F: verifyCredential (V6 status check + R4 issuer key)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| CVIN-Combined | `C/CVINCombined/CVINCombinedIdentity.sol:395` hasValidClaim | CONF:110 | on-chain read; off-chain proof in VC layer |
| ERC-735 | `C/ERC735/CVINVehicleClaimHolder.sol:392` claimExists | CONF:110 | |
| ERC-1155 | `C/ERC1155/CVINVehicleCredential1155.sol:252` hasCredential | CONF:110 | |
| LSP8 | `A/lsp8.adapter.js:121` → `C/LSP8/…:309` getDataForTokenId | CONF:110 | |
| ERC-725xy | getData read (verifyStatus) `A/erc725xy.adapter.js` | CONF:110 | |
| ERC-4337 | `C/ERC4337/CVINVehicleAccount.sol:245` getAttribute | CONF:110 | |
| ERC-1056 pure/wrapper | log/attribute read `A/erc1056.adapter.js:218`+ | CONF:110 | **NOT FOUND (by design):** ERC-1056 exposes no attribute-value read fn (IDTx AR-1, `idtx.test.js:138`) |
| ERC-725 | `C/ERC725/CVIN_DID_ERC725.sol:50` getKey read | CONF:110 | |
| MOBI-VID | `C/MOBI/MOBIVIDRegistryV2.sol:435` getEventAttestations / `:218` isAuthorizedIssuer | `attestEventRegression.test.js` | |

### F: revokeCredential (V5)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1155 | `C/ERC1155/CVINVehicleCredential1155.sol:137` revokeCredential | CONF:110,119 | |
| ERC-1056 pure | `A/erc1056.adapter.js:213` → `EthereumDIDRegistry.sol:367` revokeAttribute | CONF:110 | |
| ERC-735 | `A/erc735.adapter.js:160` → `C/ERC735/…:290` removeClaim (+`:325` revokeClaimContent) | CONF:110 | |
| CVIN-Combined | `A/cvin.adapter.js:187` → `C/CVINCombined/…:303` removeClaim (+`:336` revokeClaimContent) | CONF:110 | |
| ERC-725xy | `A/erc725xy.adapter.js:131` → setData(credHash, 0x) | CONF:110 | |
| ERC-4337 | `A/erc4337.adapter.js:166` → setAttribute(credHash, 0x) | CONF:110 | |
| LSP8 | `A/lsp8.adapter.js:116` → setDataForTokenId(credHash, 0x) | CONF:110 | |
| ERC-725 | `A/erc725.adapter.js:136` → removeKey | CONF:110 | |
| ERC-1056 wrapper | setServiceEndpoint expiry pattern `A/erc1056w` | CONF:110 | |
| MOBI-VID | `C/MOBI/MOBIVIDRegistryV2.sol:200` revokeIssuerAuthorization (issuer-level) | MOBI suite | **NOT FOUND:** no per-event revoke |

### F: createPresentation (F8 / P1 — anchor pres. hash, replay-protected; NO ERC native)
| Substrate | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| ERC-1056 pure | `A/erc1056.adapter.js:196` → `EthereumDIDRegistry.sol:314` setAttribute(key, presHash, 300s) | CONF:130 | holder-written |
| ERC-1056 wrapper | `A/erc1056w.adapter.js:75` → setServiceEndpoint(key, presHash, 300) | CONF:130 | |
| ERC-725 | `A/erc725.adapter.js:26` → `C/ERC725/…:59` addKey(presHash, PURPOSE.PRESENTATION) | CONF:130 | |
| ERC-725xy | `A/erc725xy.adapter.js:32` → `C/ERC725xy/…:159` setData(key, presHash) | CONF:130 | |
| ERC-4337 | `A/erc4337.adapter.js:35` → `C/ERC4337/…:239` setAttribute(key, presHash) | CONF:130 | |
| ERC-735 | `A/erc735.adapter.js:138` → `C/ERC735/…:225` addClaim(self) | CONF:130 | |
| CVIN-Combined | `A/cvin.adapter.js:170` → `C/CVINCombined/…:224` setAttribute(key, presHash, 300) | CONF:130 | |
| ERC-721 | n/a | CONF:130 (n/a) | holder has no write path |
| ERC-1155 | n/a | CONF:130 (n/a) | soulbound, issuer-minted |
| LSP8 | n/a | CONF:130 (n/a) | only authority writes |

### IDTx pattern (F1 §4 — identity-dependent action; same-tx + next-tx intent)
| Component | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| Dependency predicate eval | `phase2/idtx/contracts/IdtxExecutor.sol:121` holds | `phase2/idtx/test/idtx.test.js:38,51,63,74,85` | Kinds: Owner / Delegate / registered Commitment |
| Same-tx execute | `IdtxExecutor.sol:129` execute | `idtx.test.js:38` (owner), `:44` (third-party keeper AR-4), `:51` (delegate) | caller not part of predicate |
| Next-tx intent create | `IdtxExecutor.sol:135` createIntent | `idtx.test.js:106` | |
| Next-tx fulfil | `IdtxExecutor.sol:143` fulfil | `idtx.test.js:106,113,120,129` | no on-chain TOCTOU: transfer/revoke/expiry between intent & fulfil fails |
| Commitment store set/revoke | `IdtxExecutor.sol:62` setCommitment / `:73` revokeCommitment (contract `IdentityCommitments:44`) | `idtx.test.js:95,101` | owner-only; stops counting when setter loses ownership (AR-6, `:85`) |
| ERC-1056 read limitation (AR-1) | — (gates on commitment, VIN not on chain) | `idtx.test.js:63,74,138` | motivates the commitment store |

### ZkVinGate (layer 5, agent/ZK — not a basic-set fn; adjacent to execute/presentation)
| Capability | Implementing symbol (file:line) | Guarding test | Notes |
|---|---|---|---|
| anchor commitment (owner-only) | `5_zkp-agent-identity/contracts/ZkVinGate.sol:80` anchorCommitment | `5_zkp-agent-identity/test-contracts/zkvin_gate.test.js:80` | only ERC-1056 owner anchors |
| set service policy | `ZkVinGate.sol:86` setService | `zkvin_gate.test.js` | |
| scoped ZK admission (nullifier, once per scope) | `ZkVinGate.sol:92` admit | `zkvin_gate.test.js:41,49,57,63` | scope-bound, unlinkable per scope |

---

## Cross-cutting notes
- A6 native-capability matrix and the "no ERC provides F8 natively" finding: `docs/BASIC_ID_SET_EXTENSION.md` §§ lines 59–90.
- Primary parametrized guard = the one conformance file looped over all adapters; per-option suites under `test/L2-identity-system/per-option/<substrate>/`; L1 mechanism tests `test/L1-identity-mechanisms/01-09-*.test.js`.
- Two ERC-721 variants: `CVINVehicleNFT.sol` is the measured substrate; `CVIN_NFT_DID_ERC721.sol` / `_Monolithic.sol` are research copies carrying `payToll` (the IDTx inventory item).
- **Flag for CE (WP 1.4):** `C/ERC4337/CVINVehicleAccount.sol` appears to have a duplicated `validateUserOp` (lines 64 and 136) — confirm which is live before any pseudocode or measurement cites it.

## NOT FOUND / n/a-by-design
- No dedicated on-chain `verifyCredential` read primitive for ERC-1056 pure/wrapper (verification = log replay + off-chain proof).
- No per-event `revokeCredential` on MOBI-VID (only issuer-authorization revoke).
