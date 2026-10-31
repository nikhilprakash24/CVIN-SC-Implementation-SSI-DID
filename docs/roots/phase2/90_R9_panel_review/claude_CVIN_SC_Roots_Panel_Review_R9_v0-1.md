# CVIN-SC · Roots Thread G-R1 · Phase 2 — R9 Professors' Panel Review

| Field | Value |
|---|---|
| Document | **R9** Professors' Panel Review |
| Version | **v0-1** (first pass; v0-2 after the R6/R7/R8 second passes land) |
| Date | 2026-10-23 |
| Branch / tree read | `roots/G-R1-phase2`, working tree as found (no commit made) |
| Consumes | R6 v0-1 (Full-Stack Atlas), R7 v0-1 (Theory and ECE Bounds) and `r7_calc.py` (executed for this review), R8 v0-1 (Reverse Anchor Register); Phase 2 shared brief v1.0; Phase 1 README, R2 §3.3, R3, R4; repo: `docs/MEASUREMENT_CONDITIONS.md`, `docs/DEFECT_LOG.md`, `docs/STATUS_2026-10-22.md`, `docs/thesis/CRUX_REGISTER.md`, `docs/BASIC_ID_SET_EXTENSION.md`, contracts and providers cited per finding |
| Assigns | **PN-01..PN-33** (panel findings) · **SLD-01..SLD-16** (solidify directives) · **DRP-01..DRP-10** (drop/demote) · **NC-01..NC-10** (do-not-claim) · **CA-01..CA-18** (code-level actions) · **PRM-<sublayer>-nn** (primitive lock list, §6) · the Phase 2 re-keying scheme (§3.1) |
| Panel | **DS** distributed systems and blockchain · **CR** applied cryptography and security · **TCS** theoretical computer science · **ECE** wireless/V2X and embedded hardware · **ITS** CAV/ITS transportation systems · **STD** identity standards and policy (W3C, eIDAS, GDPR/EDPB) · **MTH** thesis writing and research methods |

`Progress ▓▓▓▓▓▓▓▓░░ 80 %` — all eight sections written; every finding carries evidence; v0-2 to re-check after the three second passes and to absorb the author's answers to the §6 checklist.

**How to read.** §1 is the verdict for a reader with five minutes. §2 reviews each document and numbers every finding (PN-nn) with severity, the panel member who raised it, the evidence and the fix. §3 is the bookkeeping that makes Phase 2 citable: the re-keying scheme, the placeholder resolution, the contradictions and which source wins. §4 is the panel's main output — what to lock into the thesis, where, and what must happen first. §5 lists repository actions for the defect log. §6 is the primitive lock list for the author's parallel chat. §7 is a work order for the v0-2 writers. §8 is the HANDOFF.

---

## 1. Verdict in one page

**What Phase 2 achieved.** Phase 1 reasoned about primitives and architectures; Phase 2 descended to the code and the silicon and came back with three things Phase 1 could not have produced. First, a register of the repository's actual contract functions (R6 §2.L5.2, 117 SCF rows over 22 contract prefixes; count verified by the panel) with their access control and signature discipline read from source. Second, a quantitative floor below L0 (R7 §4) showing where the Tier-1 path actually saturates. Third, a 301-row reverse register (R8; uniqueness verified by script) that turns "the programme does X" into "X stands on these tags, can be judged on these dimensions, and is evidenced to this status". Most of the arithmetic reproduces. The panel re-ran `r7_calc.py` and checked fourteen numbers by hand: twelve reproduce exactly and two are wrong (PN-12, PN-13). The honesty discipline holds in most places, but not everywhere (PN-01, PN-24).

**The three things the thesis must now say differently.**

1. **The executed chain is a single automining Hardhat process, so every finality, consensus-latency and decentralisation statement is DESIGN.** `1_blockchain-identity/results/metrics/latest/meta.json` records `"automine": true`, `"chainId": 31337`, `"blockGasLimit": 60000000`. No Besu or QBFT configuration, genesis or trace exists anywhere in the tree (panel grep: the only hits outside documents are the two Phase 2 scripts). R7 PF-39 states this precisely: the run has *N_v* = 1, there is no Δ, and t_finalise ≡ 0. **Gas is portable; latency is client plus RPC plus execution and nothing else.** Chapters 3, 5 and 6 must carry this sentence, and any Δ = 2 s figure must be labelled DESIGN (DS, MTH: unanimous).

2. **On the safety-message path the bottleneck is verification hardware and airtime, not the ledger.** Once a verifier caches identity state (HAA-1 read rule, *k_f* → ∞), the ledger is off the Tier-1 path, and what remains is *ρ_v* = *P*·*r_BSM*·*t_ver* on the OBU and channel time per BSM. An MCU-class HSM at an ESTIMATED 5 ms per verification saturates at about 20 neighbours (R7 PF-43). The repository's JSON messages (596 B and 1,110 B, register #23) cost 2.9× to 5.0× the airtime of a compact 1609.2 digest-signed BSM, so a 10 MHz 802.11p channel at CBR 0.6 holds only 63 or 37 vehicles (PF-44, DERIVED from measured sizes). The thesis's V2V feasibility claim (#27, 0.142 ms warm on a Xeon) is real, but it applies to software on a server-class host. It is not a vehicle claim (ECE, ITS).

3. **The code has two security findings that belong in the results chapter, not a footnote.**
   (a) *Signed-operation replay scope.* `EthereumDIDRegistry` signed operations hash `0x19 ‖ 0x00 ‖ this ‖ nonce ‖ identity ‖ op ‖ args` and bind no chain id (`EthereumDIDRegistry.sol` l. 160–172; D52). Raw `ecrecover` also lets r = s = 0 seize DID 0x0 (D53). Across the nine signature-verifying contracts the repository uses three signature schemes, and only `MOBIVIDRegistryV2.attestEvent` (l. 367–377) and the minimal EntryPoint (l. 60) bind `block.chainid`.
   (b) *Pseudonym linkability.* The M5 pseudonym pool puts pseudonyms on chain as delegates of one DID, and one `eth_getLogs` returns 60 of 60 of them (register #38, "fully linkable"). Pseudonym unlinkability therefore fails *by construction* at L6. R7 adds that, unless a pseudonym change forces sidelink resource reselection, it is also linkable at L0.1 with substantial probability (PF-44c; the value needs correcting, PN-12).
   Together with the unsalted VIN derivations (D64; unsalted `keccak(VIN)` token ids in ERC-1155 and LSP8; a plaintext `getVINFromDID`), these are the thesis's honest privacy results. Today ZK-VIN (SOL-11) is the only path that hides the VIN (CR, STD).

**Overall disposition.** Accept Phase 2 as the basis for the thesis's honesty and limitations apparatus. Require a second pass of all three documents before any PF-32+ number, SCF tag or RV status is cited in a chapter. Six findings are HIGH: tag collisions, script/document PF misnumbering, one dimensional error, wrong option mapping, status upgrades in R8, and stale defect statuses in R6. All six are fixable within the v0-2 pass. None undermines the three conclusions above.

---

## 2. Per-document review

Severity: **HIGH** — would mislead an examiner or propagate a wrong number or status into a chapter. **MED** — weakens a claim or its citability. **LOW** — hygiene.

### 2.1 R6 — Full-Stack Atlas

**Strengths.** (i) It applies the "trusts from below / gives above" discipline at every sub-layer and opens each section with a narrative paragraph. This is the best abstraction-ladder writing in the Roots suite (MTH). (ii) The SCF register is read from source and keeps the two ERC-1056 contracts apart (EDR vs VPR). Every claim the panel spot-checked holds, including the signed-digest layout, the three signature schemes, the chain-id binding confined to MOBI2 and the EntryPoint, the low-s guard in `CVINVehicleClaimHolder` (l. 509), the testbed controller key = SHA-256(vehicle_id) (`erc1056_provider.py` l. 370–388), and secp256k1-over-SHA-256 BSM signing (`sign_message`, `ec.ECDSA(hashes.SHA256())`) (CR). (iii) §0.1 explains its purpose as "naming the borrowed properties the eight-layer abstraction hides": wall clock, OS randomness, endpoint chain id, one-laptop setup. That is the contribution, and it is right (TCS). (iv) The §7 measured-vs-designed table is directly reusable (SLD-12).

**Findings.**

| PN | Sev | Raised by | Finding | Evidence | Required fix for v0-2 |
|---|---|---|---|---|---|
| PN-01 | **HIGH** | CR, MTH | **Stale defect statuses presented as live faults.** R6 says `revokeIdentity` emits `DIDRevoked` with "no `previousChange`, D21" (SCF-VPR-07, IMP-L2.1-04, BP-L2.1-02). It says CMB claim ops cut the `changed` list (D22), and that `setVehicleAttributes` panics so the birth record is unreachable (SCF-CVDR-03, D18). All three are **fixed**. | `MOBI/ERC1056Registry.sol` l. 18, 264–270 (`emit DIDRevoked(identity, block.timestamp, changed[identity])`); `DEFECT_LOG.md` l. 46 (D18 fixed `65a143f`, 100-year validity), l. 49 (D21 fixed `65a143f`), l. 50 (D22 fixed, merged semantics `bd90004`; open residue is only `revokeDelegate` timestamp, low-s, no identity-level revocation) | Re-read every Dn citation against the DEFECT_LOG status column. Rewrite SCF-VPR-07, SCF-CVDR-03, SCF-CMB-03/07, IMP-L2.1-04 and BP-L2.1-02 to the current behaviour. BP-L2.1-02 becomes "historical; closed by D21/D22 fixes", with the open residue named. Add a column "defect status @ 2026-10-22". |
| PN-02 | MED | TCS | **Tag-internal inconsistencies.** IMP-L2.1-04 calls did:ethr resolution "ALG-21", but ALG-21 is the gas schedule and resolution is ALG-23. ALG-21 (gas schedule) and ALG-17 (AES-GCM) are not algorithms in the brief's sense. PRO-13x/y/z (J2735, J2945/1, DIDComm) reuse the JSON-RPC number's suffix space for unrelated protocols. | R6 l. 229, 289, 197, 603–605 | Fix the ALG-21→ALG-23 cross-reference. Keep the numbers (frozen once issued) but annotate ALG-21 as "cost model" and ALG-17 as "primitive (L1.1)". Re-tag PRO-13x/y/z as PRO-23/24/25 with a retirement note `~~PRO-13x~~ → PRO-23`. |
| PN-03 | MED | TCS, DS | **Eight of the nineteen PF placeholders have no bound anywhere in R7**, and one is badly posed. ⟦15⟧ "P(cross-chain address+nonce match)" is a deterministic condition (same deployer key and nonce sequence → same address), not a probability. | §3.3 placeholder table below; R6 §8 list vs R7 §9 index | In v0-2, resolve with the §3.3 table. For the eight unbounded ones, either request a PF from R7 v0-2 (PF-63..) or downgrade the BP's bound cell to "qualitative". Restate ⟦15⟧ as a precondition. |
| PN-04 | MED | CR | **BP-L5.2-01 (D52) precondition is understated.** R6 treats cross-chain replay as needing a coincidence. In this repository the precondition is *met by default*: the harness (chain 31337) and the testbed node (chain 1337, `cv2x-testbed/hardhat.config.js` l. 16) both deploy from Hardhat's default accounts, so the same deployer and nonce give the same registry address on both chains. The same holds for any CREATE2 or same-key deployment. | `hardhat.config.js` (both trees); `EthereumDIDRegistry.sol` l. 160–172 | State the precondition concretely. Propose an executed two-chain replay test (CA-02) so the row can move from source-based to MEASURED. Keep the "upstream fidelity" trade-off explicit. |
| PN-05 | MED | CR | **Two required audits are left as promissory notes.** Access control is "read from the source, not the tests" (§2.L5.2 preamble). BP-L5.2-06 (reentrancy in `payToll`, `_checkOnERC721Received`, 725X/4337 `execute`) is "not audited in this pass". | R6 l. 329, 688 | Either do the CEI ordering check per function in v0-2 (it is short: four functions) or remove BP-L5.2-06 from the BP table and list it as Q-R6-06. A BP with no analysis must not be cited. |
| PN-06 | LOW | MTH | **Two gas figures for the same function, unlabelled.** Trace 1 quotes `changeOwner` 68,854 (#2, test-suite/wrapper context). R7 §5.1 uses U1 = 51,754 (crud_gas, pure). | R6 §6 Trace 1; register #2 vs `crud_gas.md` U1 | Quote both with their contexts, or use the harness value with its run id. |
| PN-07 | LOW | MTH | **Counts drift.** "562 Hardhat per STATUS §5" (correct for the later STATUS section). R8 uses 541/342 from STATUS §1.1, so the two documents disagree. | `STATUS_2026-10-22.md` l. 14 vs l. 112 | Use the latest (562 Hardhat, 376 Python) and say which STATUS section is meant. |
| PN-08 | MED | ECE, ITS | **Missing breaking points that R7 found.** (a) RF-layer pseudonym linkability through SPS resource persistence (R7 PF-44c explicitly asks R6 to place it). (b) The quiet-sender hole: state staleness bounded in messages, unbounded in time (R7 PF-54). (c) Message-encoding size as a capacity breaking point (R7 PF-44). | R7 l. 284, 381–384, 280 | Add BP-L0.1-02 (resource persistence across pseudonym change), BP-L7.2-03 (no TTL on cached state), BP-L7.2-04 (encoding size vs channel capacity), each bound by the R7 PF. |
| PN-09 | MED | MTH, DS | **SOL inflation.** In Phase 1, SOL-nn were *programme solutions placed on the trilemma surface*. SOL-15 (freshness + verifier v3), SOL-16 (k-refresh probe) and SOL-17 (fail-closed resolver) are implementation mechanisms of good quality, but they are not solutions in that sense. Inflating the SOL list weakens the contribution claim. | R6 §5; Phase 1 README A.3 | Keep SOL-10 (IDTX), SOL-11 (ZK-VIN), SOL-13 (MOBI registries) and SOL-14 (Steward) as SOLs. Mark SOL-12, SOL-15, SOL-16 and SOL-17 "mechanism (cite as IMP)" with a sentence of justification, or justify them as SOLs against the trilemma. The author decides; R6 v0-2 records the decision. |

**Clarity for moving across abstraction levels.** Excellent at the section level. The one weakness is §6: the traces descend well, but they do not ascend back to the R3 requirement each trace serves (R1 authenticity, I3 rotation, and so on). One line per trace would close the loop (MTH).

### 2.2 R7 — Theory and ECE Bounds, and `r7_calc.py`

**Strengths.** (i) PF-39 formalises the executed system and draws the correct line: gas is portable, latency is not. (ii) PF-43/44 is the most consequential new result in Phase 2. It moves the thesis's real-time claim from "is the ledger fast enough" to "is the OBU and the channel fast enough", which is the question an ITS examiner will ask (ITS, ECE). (iii) PF-51 explains on-chain Groth16 cost opcode by opcode. 252,794 modelled vs 256,038 measured (#58) is a 1.3 % residual, and the panel recomputed it exactly: 181,000 + 43,050 + 7,744 + 21,000. That is thesis-grade. (iv) PF-54/55 separate message freshness from state freshness and give *k_f*\* = ⌊*r_s*σ_max⌋ + 1 in closed form. This answers the I-05 question cleanly (TCS). (v) The script prints every number with its inputs. The panel ran it without error.

**Spot-check of the script against the document** (panel recomputation by hand or independent script):

| # | Quantity | Document | Panel | Verdict |
|---|---|---|---|---|
| 1 | QBFT messages *M*(4) = (N−1)(2N+1) | 27 | 3 × 9 = 27 | ✓ |
| 2 | *P*\*(0.5) from #26 linear model | 304.9 | 50/0.164 = 304.9 | ✓ |
| 3 | 802.11p no-security *T_air* + AIFS, *N_fit* | 218 µs, 275 | ⌈678/48⌉ = 15 symbols → 160 + 58 µs; 0.6/(10 × 218 µs) = 275 | ✓ |
| 4 | Replay cache, docstring check | 596 | 65,536/110 = 595.8 | ✓ (repo docstring "650" wrong — CA-08) |
| 5 | Backhaul E[W], μ_off = 600 s, A = 0.99 | 14.50 s | 8.5 + 0.01 × 600 | ✓ |
| 6 | E[t_conf] *N_v* = 4, one crash | 5.50 s | 3 + 10/4 | ✓ |
| 7 | Groth16 model | 252,794 | as above | ✓ |
| 8 | Fleet ratio | 90.3× | 4.943×10⁴ × 54,807 / 3×10⁷ | ✓ |
| 9 | κ = 48, 1.5×10⁹ devices | 4.0×10³ pairs | 2.25×10¹⁸/2⁴⁹ = 3,997 | ✓ |
| 10 | *T_hold* at 0.5 ppm | 27.78 h | 0.1/(10⁻⁶) = 10⁵ s | ✓ |
| 11 | *k_f*\* at σ_max = 1 s | 11 | ⌊10⌋ + 1 | ✓ |
| 12 | *G_HH* | 60,000,000 | `meta.json` network.blockGasLimit | ✓ |
| 13 | Log cost of 1 kB event data | 9,317 gas | LOG3 = 375 + 3 × 375 + 8 × 1,024 = **9,692** | ✗ (PN-13) |
| 14 | P(resource persists 1 s after pseudonym change) | 0.368 / 0.549 / 0.819 | simulation, 2×10⁵ draws, C ~ U{5..15}, RRI 100 ms: **0.135 / 0.449 / 0.804** | ✗ (PN-12) |

**Findings.**

| PN | Sev | Raised by | Finding | Evidence | Required fix for v0-2 |
|---|---|---|---|---|---|
| PN-10 | **HIGH** | MTH, TCS | **The script's PF labels disagree with the document almost throughout**, not only at PF-51. A reader who greps the script for a document PF finds the wrong quantity. | Mapping (script label → document PF): PF-32/33 RNG → **PF-41/42**; PF-34 verify load → **PF-43**; PF-35 comp → **PF-36**; PF-36/36b/36c airtime, PC5, reselection → **PF-44 (and 44c)**; PF-37 QBFT messages → **PF-38**; PF-38 t_conf → **PF-40**; PF-39/40/41 GNSS → **PF-53/47/47**; PF-42 backhaul → **PF-48**; PF-43/44 gas → **PF-49/50**; PF-45 Groth16 → **PF-51**; PF-46 storage → **PF-52**; PF-47/48/49 freshness → **PF-54/55/56**; PF-50 gossip → *(no document PF; "PAR-15")*; PF-51 HHI → **PF-60**; PF-52 VIN entropy → **PF-33/62**. Only PF-02/04/16/19/24 (R4 re-checks) agree. | Re-label every `[PF-nn]` print in the script to the document's numbering. Add a header table in the script. Add a CI-style self-check that every PF cited in the document appears in the script output. Give gossip a PF (PF-63) or drop it. |
| PN-11 | **HIGH** | TCS, ECE | **Dimensional error in the "ledger is not the bottleneck" condition** (§4.3, last paragraph): "whenever *k_f* ≥ *r_BSM*·*P*·*t_chain*/(*f_id*/*r_BSM*)". The refresh load per verifier-second is (*r_BSM P*/*k_f*)·*t_chain*, and requiring it ≤ *f_id* gives *k_f* ≥ *r_BSM*·*P*·*t_chain*/*f_id*. The document's expression carries an extra factor *r_BSM* (units s⁻¹). | At *P* = 100, *t_chain* = 13.94 ms, *f_id* = 0.5: correct *k_f* ≥ 27.9; document's formula gives 278.8 | Correct the expression. Then reconcile it explicitly with the register's measured knee (#32: *k* ≈ 90 for *P*\*(0.5) = 100). That knee uses a different criterion (amortised per-message cost against the per-message share of the budget), so state both criteria and when each applies. |
| PN-12 | MED | ECE | **PF-44c's exponential approximation is wrong at low *P_keep*.** With *C* ~ U{5..15} the minimum hold is 0.5 s and the residual is far from exponential. The panel's simulation gives P(same resource 1 s after change) = 0.135 / 0.449 / 0.804 at *P_keep* = 0 / 0.4 / 0.8, not 0.368 / 0.549 / 0.819. The qualitative finding stands; the lower end of the range is about 2.7× too high. | Panel simulation (method in this row's text) | Replace the closed form with the residual-life computation for the stated *C* distribution, or simulate in the script (seeded). Restate the range as "≈ 0.14–0.80". |
| PN-13 | MED | DS | **PF-52 storage-vs-log ratio is overstated.** (a) The LOG base cost of 375 is omitted (9,692 per kB, not 9,317). (b) Event data has to arrive as calldata at 16 gas per non-zero byte, which the storage path also pays but which dominates the log path. A like-for-like comparison is ≈ (707,200 + 16,384)/(9,692 + 16,384) ≈ **28×**, not 76–84×. | `r7_calc.py` §J line "log cost … 8*1024*kb + 375*3"; EIP-2028 | Correct the arithmetic and state the comparison basis. The direction of the R8 trilemma reading is unchanged. |
| PN-14 | MED | DS, MTH | **KD-R4-01 and KD-R4-04 build a chimera.** They take Hardhat's development default gas limit (60 M, MEASURED for the instrument), combine it with the design Δ = 2 s, and present the product as a *correction* to R4's design rows. Hardhat's limit is not an input to Plane A design. R4's 30 M/100 M rows are design scenarios, not errors. | `meta.json` (`blockGasLimitConfig` 60,000,000 = dev default); R4 PF-24 | Dispose as in §3.4: KD-R7-01 is QUALIFIED, not accepted. PF-49/50 report capacity at *G* ∈ {30 M, 60 M (instrument), 100 M} with *G* as a PAR. The fleet sentence becomes "≈ 90× over one chain at *G* = 60 M, Δ = 2 s (both PAR)". |
| PN-15 | MED | CR, STD | **PF-50 sizes a design the thesis should not build.** The anchoring operation it scales is pseudonym `addDelegate` (#38). R6 BP-L7.2-01 and #38 show that design is linkable by construction. Without a sentence saying so, a capacity number for a privacy-broken design reads as a recommendation. | R7 §5.2; register #38 linkability verdict | Add: "PF-50 is an upper bound on a design excluded on privacy grounds (BP-L7.2-01); a 1609.2-style off-chain pseudonym scheme anchors nothing per pseudonym." Keep the number only as an argument for why on-chain pseudonyms fail twice. |
| PN-16 | LOW | MTH | **Precision beyond the register.** *t_ver* = 0.14225 ms and 0.0904 ms do not appear in #27 (0.142 [0.141, 0.143]; 0.090). *P*\*(0.5) = 351 is a pure-crypto derivation; the register's measured linear model gives 305 (#26). | `MEASUREMENT_CONDITIONS.md` #26, #27 | Quote at register precision. Lead with 305 (MEASURED model) and give 351 as the crypto-only ceiling. |
| PN-17 | LOW | TCS | **Monte Carlo agreement is overstated.** "Agrees to < 2 %" — at μ_off = 600 s, A = 0.95 the p99.9 values differ by 2.3 % (2,355.7 vs 2,301.4). | `r7_calc.py` §I output | Say "< 3 %", or raise the draw count and report a CI. |
| PN-18 | MED | STD, MTH | **Unfetched citations carry load.** SR-L..T authors and years; 1609.2 overhead sizes (86/162/210 B); HSM and ECU verify classes; "verify-on-demand (IEEE 1609.2 practice; STANDARD in kind)", which is deployment practice rather than a normative clause; "Mining your Ps and Qs" (2012); the BN254 ≈ 100-bit figure. | R7 SR table, §4.3, §4.4 | Log each as LIM-R7-nn and run them through the Accuracy Ledger. Change the verify-on-demand status from STANDARD to ESTIMATED (practice) until a clause is cited. |
| PN-19 | LOW | TCS | **PF-36 sums heterogeneous quantities.** It adds computational advantages (2⁻¹²⁸) to a governance prior (*p_c*-based collusion probability) and an assumed resolver-bug rate. The union bound is valid over *events*, but the reader must see that ε_L is a modelling prior, not an adversary advantage. On the executed system ε_L = *p_c* of one operator. | R7 §2.5 | Restate as a union bound over failure events with each ε's nature labelled (computational / governance / implementation). Add the *N_v* = 1 instance. The "37 orders" sentence is correct (1.40×10⁻² vs 2.9×10⁻³⁹ ≈ 36.7 orders). |
| PN-20 | LOW | MTH | **KD-R4-08 and KD-R4-09 are confirmations, not corrections.** | R7 §10 | Move them to CEV-R7-nn. |
| PN-21 | MED | MTH, DS | **Run-of-record ambiguity.** R7 cites the crud_gas values to run `2026-10-23T00-49-12Z_1f4ace0` (current `meta.json`), while the register rows it quotes cite other runs (#50: `7a9a996`; #39: `a9e2a28`; #54: `9bdf451`). The values agree where checked (U3 35,024; U5 62,646; P1 34,206), but a thesis table needs exactly one provenance. | `meta.json` runId; register #39, #50, #54 | Cite the register row (status V) as the authority and the run id as provenance, and state "values identical across runs X, Y" where true. The Cost thread confirms the register points at the current run of record (SLD-02 precondition). |

**Clarity.** The "what this level does for the level above / trusts from below" openings are present and good. §7, written for R8, is the right design, but R8 has not consumed it (PN-25). The handoff's "KD-R4-nn" keys read as "the fourth KD of R-something" rather than "corrections to R4". The re-keying in §3.1 fixes this.

### 2.3 R8 — Reverse Anchor Register

**Strengths.** (i) The downward direction is the right complement to R6. Rule 1's three states (provisionally anchored / unbounded / unevidenced) are a clean, checkable definition of "not done yet" (MTH). (ii) Adding status **I** (implemented, unmeasured) is the most useful vocabulary change in Phase 2. IdtxExecutor needs exactly that label. Adopt it suite-wide (PN-31). (iii) The coverage matrix and its headline (128 ● / 83 ○ / 207 ·; panel recount agrees) is a strong one-figure honesty statement. MD-01/02/03/10 are empty except one Dv because one node mines. (iv) The routing table (§6) maps sensibly onto the programme's threads.

**Findings.**

| PN | Sev | Raised by | Finding | Evidence | Required fix for v0-2 |
|---|---|---|---|---|---|
| PN-22 | **HIGH** | STD, MTH | **Wrong option mapping in RV-SC.** RV-SC-04 ERC-721 → "O2", RV-SC-06 ERC-725 → "O3", RV-SC-07 725xy → "O3 variant", RV-SC-08 ERC-735 → "O4", RV-SC-09 ERC-1155 → "O5". The frozen mapping (R2 §3.3, quoted by R6 §3) is O2 = ERC-1155, O3 = ERC-721 soulbound, O4 = ERC-6551 (absent from the repo), O5 = ERC-725, O6 = ERC-725xy + ERC-735. R8 is off by one or two throughout this block, and it contradicts R6. | R8 l. 322–327; R2 l. 115–119 | Replace with R6 §3's mapping. Add RV-SC rows' O-column to the v0-2 consistency check against R2. |
| PN-23 | **HIGH** | CR, MTH | **Status upgrades by assertion, contrary to R8's own Rule 2.** (a) RV-SCF-32 `CVIN_DID_ERC725.execute` "M (#54 X1)", but #54 says "ERC-725 basic `execute` is a stub", n/a, and the code emits an event and performs no call (`CVIN_DID_ERC725.sol` l. 80–84; D23). (b) RV-IDTX-14 anchors X1 to the ERC-725 stub rather than SCF-E725XY-04. (c) RV-SIG-12 "Butterfly / pseudonym keys" and RV-SCN-12 "Pseudonymous V2X" are marked **M (#38)**, but #38 measured an on-chain delegate pool and found it *fully linkable*. That evidences the *failure* of pseudonymity, not butterfly keys. (d) RV-HW-10 "CPU / RNG" is M on host timings, but the RNG was never measured. | register #54, #38; R8 l. 168, 224, 377, 467, 504 | (a) → St "— (stub; D23)". (b) → anchor SCF-E725XY-04 and SCF-E4337A-02, St M (#54, 725xy and 4337 only). (c) RV-SIG-12 → Ds (1609.2 butterfly keys not in repo). RV-SCN-12 → "M (#38): negative result — linkable". Add an RV-THR row for the linkage operation. (d) Split into CPU (M as environment) and RNG (—). |
| PN-24 | MED | ITS, TCS | **Message freshness and state freshness are conflated.** RV-READ-03 "Cached read" and RV-ALG-09 "Freshness check (k-refresh)" anchor to `freshness.py`. That module implements message freshness and the replay cache. The state cache and *k* live in `ERC1056Provider.set_refresh_every` and `_probe_identity_info`. R7 §6 warns against exactly this confusion. | `freshness.py` l. 30–63; R7 l. 375 | Re-anchor RV-READ-03 and RV-ALG-09 to `erc1056_provider.py`. Keep RV-ALG-10 on `freshness.py`. Add PF-54/55 to both. |
| PN-25 | MED | TCS | **MDs cite only Phase 1 PFs.** R7 §7 supplies PF-57..62 precisely for R8's dimensions, and R8 leaves ⟦PF-??⟧ in their place. | R8 §1 vs R7 §7 | Apply the MD↔PF map in §3.3 (table C). |
| PN-26 | MED | MTH | **PAR collision with R7** (both own PAR-01..). | §3.1 | Apply the PAR map in §3.1 (table B). R8 owns PAR-. |
| PN-27 | MED | MTH | **"●" conflates MEASURED with DERIVED-from-ESTIMATED.** The only ● on MD-02 is RV-THR-06 "Dv", derived from an ESTIMATED *p_c*. A coverage figure that will be quoted must not mix the two. | R8 §5 rule 5; RV-THR-06 | Split the cell code into ● (≥ 1 M), ◐ (Dv only), ○, ·. Recount the headline. |
| PN-28 | MED | CR, ECE | **The most consequential Phase 2 findings have no RV row.** Missing: signed-op chain-id scope (D52) and zero-signer seizure (D53) as RV-THR operations; the deterministic test-key path (BP-LH-02); TTL-less state cache (quiet sender); message encoding size vs airtime; the insecure single-party Groth16 setup as a governance item (RV-GOV-06 exists but carries St "—" with no #57 citation); the lying-RPC-endpoint read (BP-L0.4-02). | R6 §4; R7 §4.4, §6.1 | Add RV-THR-11..15 and RV-PROT-16 (message encoding), and cite #57 on RV-GOV-06 (setup type MEASURED). |
| PN-29 | LOW | MTH | **Counts drift.** RV-MET-01 "63 rows" (panel count: 62 numbered rows); RV-MET-02/03 541/342 (latest STATUS: 562/376). | `MEASUREMENT_CONDITIONS.md`; STATUS l. 112 | Correct and date-stamp. |
| PN-30 | LOW | STD | **RV-VC-03 licence endorsement and Q-R7 (supersession vs attestation).** The question is good but the row's anchors are speculative ("Ds end to end"). | R8 §4(a) | Keep as Ds. Route to a new chat (as R8 says). Do not let §4(a) be the illustrative chain in the thesis while a measured chain (§4(b) or §4(d)) exists. |

**Clarity.** Strong. The category openings place each category on the stack. The dense cells are acceptable for a v0-1 built to be deepened. The 155 ⟦⟧ placeholders are the main obstacle to use, and §3.3 resolves nearly all of them.

### 2.4 Cross-document findings

| PN | Sev | Raised by | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| PN-31 | **HIGH** | MTH | **Record-key collisions across R6/R7/R8 (confirmed).** R6 assigns Q-R7..Q-R12 and KD-R4..KD-R8. R8 assigns Q-R7..Q-R10. R7 assigns Q-R7-01..08 and KD-R4-01..09. R7 and R8 both assign PAR-01.. (R7 PAR-01..26, R8 PAR-01..30), with different meanings for the same number (R7 PAR-01 = validator count; R8 PAR-01 = DLT family). Q-R7 therefore means three different questions, and KD-R4 means two. | R6 l. 10, 792–794; R7 l. 11, 512–523; R8 l. 11, 704 | Apply §3.1. |
| PN-32 | MED | MTH | **Status vocabularies diverge.** R6 uses MEASURED / DESIGN / not used / candidate; R7 uses the brief's five; R8 uses M / Dv / Ds / E / S / I / —. | headers of all three | Adopt one scale suite-wide: MEASURED (M) · DERIVED (Dv) · IMPLEMENTED-UNMEASURED (I) · DESIGN (Ds) · ESTIMATED (E) · STANDARD (S) · not used (—). "candidate" becomes Ds with a note. |
| PN-33 | MED | DS | **Phase 1 numbers that Phase 2 shows are design-only have not been re-labelled at the source.** R4 PF-24/25/28 use Δ = 2 s and *G* = 30/100 M "sandbox defaults". R2 SOL-01 describes "single-validator Besu QBFT + Foundry", which matches no code on this tree. | R6 §5 last para; R7 KD-R4-02 | Accept the corrections per §3.4. R4 v0-2 (or a Phase 1 erratum note) re-labels those rows DESIGN. R2 SOL-01 gets a lineage note ("sandbox lineage `cvin-sandbox-v1.x`; not this tree"). |

**Severity totals: HIGH 6 (PN-01, 10, 11, 22, 23, 31) · MED 19 · LOW 8 · total 33.**

---

## 3. Cross-document consistency

### 3.1 Re-keying scheme (proposed; apply in all three v0-2 passes)

**Rule.** Phase 2 record keys are namespaced by the *issuing document*: `Q-R6-nn`, `Q-R7-nn`, `Q-R8-nn`, `Q-R9-nn`; `KD-R6-nn`, `KD-R7-nn`, `KD-R8-nn`, `KD-R9-nn`; likewise `CEV-`, `LIM-`, `MC-`, `F-`. The thing corrected is named in the row ("corrects R4 PF-24"), not in the key. Phase 1 keys (Q-R1..6, KD-R1..3, F-R1..4, CEV-R, LIM-R, MC-R) are frozen. **PAR- is owned by R8.** R7 cites R8's PAR numbers. R7's parameters that R8 lacks are appended to R8 as PAR-31..43. Each re-keyed document carries a retirement line `~~old~~ → new` for every key.

**Table A — Q and KD re-keying.**

| Old (issuer) | New | Content |
|---|---|---|
| Q-R7 (R6) | **Q-R6-01** | Terminology Freeze O1–O17 re-read |
| Q-R8 (R6) | **Q-R6-02** | add LSP8, CVIN-Combined, MOBI profile, ZK-VIN as options? |
| Q-R9 (R6) | **Q-R6-03** | SOL-01: this repo or sandbox lineage? |
| Q-R10 (R6) | **Q-R6-04** | is the M5 on-chain pseudonym pool meant to be unlinkable? |
| Q-R11 (R6) | **Q-R6-05** | D52 fix vs upstream fidelity |
| Q-R12 (R6) | **Q-R6-06** | reentrancy audit scope |
| Q-R7-01..08 (R7) | **Q-R7-01..08** (unchanged) | Besu genesis; HSM *t_ver*; IDTX gas; SPS reselection; RSU propagation; docstring 650/596; TTL; PF-61(a),(e) |
| Q-R7 (R8) | **Q-R8-01** | licence endorsement: supersession or attestation |
| Q-R8 (R8) | **Q-R8-02** | owner of MD-01/02/10 (multi-node run) |
| Q-R9 (R8) | **Q-R8-03** | measure M2 (Sepolia) latency at all? |
| Q-R10 (R8) | **Q-R8-04** | 1609.2 encoding in scope? |
| KD-R4 (R6) | **KD-R6-01** | R2 SOL-01 does not describe this tree |
| KD-R5 (R6) | **KD-R6-02** → merged into KD-R7-02 | Δ = 2 s has no executed source |
| KD-R6 (R6) | **KD-R6-03** | repo "1609.2" is X.509 P-256 in JSON |
| KD-R7 (R6) | **KD-R6-04** | SSI BSMs are secp256k1/SHA-256, not EIP-191 |
| KD-R8 (R6) | **KD-R6-05** → merged with KD-R6-01 | HAA-1 Plane A has no code |
| KD-R4-01..07 (R7) | **KD-R7-01..07** | as R7 §10 (dispositions §3.4) |
| KD-R4-08, -09 (R7) | **CEV-R7-01, -02** | confirmations, not corrections (PN-20) |

Note the overlap: Q-R6-04 (R6) and Q-R8-04 are related (pseudonymity / 1609.2 scope), and Q-R6-01 duplicates the brief's instruction to read the Freeze. The author should answer Q-R6-04 and Q-R8-04 together (§6 checklist item 11).

**Table B — PAR map (R7 → R8; R8 owns).**

| R7 PAR | Meaning | → R8 PAR | Note |
|---|---|---|---|
| 01 | validator count *N_v* | **04** | |
| 02 | block interval Δ | **05** | |
| 03 | block gas limit *G* | **06** | |
| 04 | QBFT round-change timeout *t_rc* | **31** (new) | |
| 05 | proposer selection | **32** (new) | |
| 06 | client(s) and shares *s_c* | **02** | extend R8-02 with "shares" |
| 07 | sign/verify hardware class *t_sig*, *t_ver* | **33** (new) | distinct from R8-15 key-storage class |
| 08 | RNG min-entropy, seeding policy | **34** (new) | |
| 09 | V2X signature curve | **10** | |
| 10 | radio technology | **16** | |
| 11 | MCS / data rate | **35** (new) | |
| 12 | message encoding and 1609.2 profile *L_sec* | **36** (new) | |
| 13 | identity budget fraction *f_id* | **24** | |
| 14 | read-path RTT class | **26** | extend R8-26 with RTT class |
| 15 | gossip fan-out | **37** (new) | |
| 16 | freshness window | **38** (new) | |
| 17 | backhaul availability model | **39** (new) | |
| 18 | re-check period *k_f* and TTL | **19** + **20** | |
| 19 | replay-cache size | **40** (new) | |
| 20 | revocation profile | **12** | |
| 21 | proof system and setup | **11** + **41** (new: setup ceremony) | |
| 22 | pseudonym budget *K* | **22** | |
| 23 | fleet size *V* | **42** (new) | |
| 24 | settlement option | **18** | |
| 25 | manoeuvre-class W budgets | **43** (new) | |
| 26 | neighbour density *P* | **25** | |

**Table C — other namespace corrections.** R6 PRO-13x/y/z → PRO-23/24/25 (PN-02). R7 script PF labels → document numbering (PN-10). The R8 MD↔PF bindings are in §3.3 Table C′.

### 3.2 Tag ownership confirmed

R6 owns HW-, PRO-, ALG-, IMP-, SCF-, BP-LH/Lx.y, SOL-10..17. R7 owns SYM-25..58, SR-L..T, PF-32..62. R8 owns RV-, MD-, PAR-. R9 owns PN-, SLD-, DRP-, NC-, CA-, PRM-. No other collisions were found in these namespaces. The panel checked SCF prefixes for duplicates (none) and RV ids for duplicates (none in 301).

### 3.3 Placeholder resolution

**Table A′ — R6's PF placeholders → R7.**

| R6 placeholder | Meaning | Resolves to | State |
|---|---|---|---|
| PF-⟦1⟧ | κ_eff vs boot entropy | **PF-41, PF-42** | resolved |
| PF-⟦2⟧ | κ = log₂ \|vehicle-id space\| | — | **open** → request PF-63 (deterministic-key entropy; trivially κ = H(vehicle_id)) |
| PF-⟦3⟧ | accepted replay age = max_age + δ_clock | **PF-47** (items 1, 4) | resolved |
| PF-⟦4⟧ | false-read probability vs independent endpoints | — | **open** → PF-64 request, or qualitative |
| PF-⟦5⟧ | P_loss(CBR) | PF-44 (capacity only) | **partial** → PF-46 (reserved) |
| PF-⟦6⟧ | W ≥ σ + T_off | **PF-48** | resolved |
| PF-⟦7⟧ | eclipse cost vs table size | — | **open** → qualitative (no P2P in repo) |
| PF-⟦8⟧ | p_bug × client share | **PF-60** (HHI) | partial |
| PF-⟦9⟧ | circuit soundness / audit coverage | — | **open** (PF-35 assumes a sound R1CS) → qualitative + audit status in PF-61(e) |
| PF-⟦10⟧ | log availability vs pruning | — | **open** → qualitative |
| PF-⟦11⟧ | P(evict live) | **PF-53** | resolved |
| PF-⟦12⟧ | *p_c* with correlation ρ_c | PF-60 (partial) | **open** → PF-65 request (correlated-failure extension of R4 PF-16) |
| PF-⟦13⟧ | dev-to-prod transfer factor | **PF-39** (factor undefined: latency not transferable; gas factor = 1) | resolved (as a negative statement) |
| PF-⟦14⟧ | governance key vs m-of-n | R4 PF-30 (analogue) | **open** → PF-66 request |
| PF-⟦15⟧ | cross-chain address+nonce match | — | **re-pose as precondition** (PN-03, PN-04) |
| PF-⟦16⟧ | VIN entropy vs hash rate | **PF-33, PF-34** (19.93 bits; #60) | resolved |
| PF-⟦17⟧ | on-chain anonymity set of a pseudonym pool | **PF-62** (*k_A* = 1; #38) | resolved |
| PF-⟦18⟧ | skew vs CLOCK_SKEW_S | PF-47 (partial: no CLOCK_SKEW_S term) | partial |
| PF-⟦19⟧ | oracle / issuer misreport detection | — | **open** → qualitative |

**Table B′ — R7's placeholders → R6/R8.**

| R7 placeholder | Resolves to |
|---|---|
| ⟦IMP-L3.2-?? Besu⟧ (×2) | **IMP-L3.2-01** |
| ⟦ALG-??⟧ (header list) | ALG-02 (ECDSA), ALG-03 (ecrecover), ALG-12 (Groth16), ALG-20 (QBFT), ALG-19 (automine) |
| ⟦HW-??⟧ | HW-03 (HSM), HW-08 (OBU), HW-09 (modem), HW-10 (GNSS) |
| ⟦SCF-ERC1056-??⟧ | SCF-EDR-01..12 (per function) |
| ⟦BP-LH-??⟧ (PF-41 row) | **BP-LH-01** |
| ⟦R6⟧ in PF-35 "SOL-10+" | **SOL-11** (ZK-VIN) |
| ⟦R6⟧ in PF-51 "L5-0x" | BP-L1.2-04 (setup) and BP-L1.2-02 (precompile defect) |
| ⟦MD-??⟧ | see Table C′ |
| "⟦⟧" in handoff | literal; delete |

**Table C′ — R8 MD ↔ R7 PF (replaces ⟦PF-??⟧ in R8 §1).**

| MD | ⟦PF-??⟧ in R8 | → R7 PF |
|---|---|---|
| MD-01 | QBFT finality time | **PF-40, PF-57** |
| MD-02 | Nakamoto coefficient | **PF-60** |
| MD-03 | surface map | **PF-58** |
| MD-04 | SC defect model | **PF-61** |
| MD-05 | protocol proof | **PF-36, PF-59** |
| MD-06 | — | add **PF-32..35** |
| MD-07, 08 | — | add **PF-49, PF-52** |
| MD-09 | linkability metric | **PF-62** (with PF-44c) |
| MD-10 | BFT liveness | **PF-37, PF-57a** |
| MD-11 | — | add **PF-49, PF-50, PF-43** |
| MD-13 | — | add **PF-43** (tier fit) |
| MD-14, 15 | — | add **PF-48, PF-54, PF-55** |

**Table D′ — R8's R6 placeholders → R6 tags** (covers all 155 occurrences by kind).

| R8 placeholder (as written) | → R6 tag |
|---|---|
| ⟦SCF-ERC1056-??⟧ validDelegate / changeOwner / changeOwnerSigned / addDelegate / addDelegateSigned / revokeDelegate / setAttribute / setAttributeSigned / revokeAttribute | **SCF-EDR-02 / 03 / 04 / 05 / 06 / 07 / 09 / 10 / 11** |
| ⟦SCF-CVINVDR-??⟧, ⟦SCF-CVINVehicleDIDRegistry-?? createVehicleDID⟧ — createVehicleDID / transferVehicleOwnership / addVerificationDelegate | **SCF-CVDR-02 / 04 / 07** |
| ⟦SCF-MOBI1056-??⟧, ⟦SCF-MOBI-ERC1056Registry-?? revokeIdentity⟧ — registerVehicle / revokeIdentity / updateVehicleKey | **SCF-VPR-08 / 07 / 09** |
| ⟦SCF-MOBIV1-??⟧, ⟦SCF-MOBIVIDRegistry-??⟧ — registerVehicleBirth / anchorVehicleKey / transferVehicleOwnership / authorizeManufacturer / transferRegistryAuthority / lookupByVINHash | **SCF-MOBI1-04 / 06 / 08 / 01 / 03 / 09** |
| ⟦SCF-MOBIV2-??⟧, ⟦SCF-MOBIVIDRegistryV2-??⟧ — recordLifecycleEvent / attestEvent / authorizeIssuer, revokeIssuerAuthorization / getCompleteHistory | **SCF-MOBI2-03 / 04 / 01, 02 / 05** |
| ⟦SCF-ERC735-??⟧ addClaim / removeClaim / revokeClaimContent | **SCF-E735-01 / 02 / 03** |
| ⟦SCF-ERC1155-??⟧ issueCredential / revokeCredential / issuerTransferIdentity | **SCF-E1155-02 / 03 / 04** |
| ⟦SCF-ERC721-??⟧ mintVehicle / addServiceRecord / deactivateVehicle | **SCF-E721N-01 / 02 / 03** |
| ⟦SCF-ERC721DID-??⟧, ⟦SCF-CVIN_NFT_DID_ERC721-?? payToll⟧ | **SCF-E721T-03** |
| ⟦SCF-ERC725-??⟧ addKey/removeKey; ⟦SCF-ERC725-?? execute⟧ | **SCF-E725B-02**; **SCF-E725B-03 (stub)** — for X1 use **SCF-E725XY-04** (PN-23) |
| ⟦SCF-ERC725XY-??⟧ setData | **SCF-E725XY-02** |
| ⟦SCF-4337-?? handleOp⟧, ⟦SCF-4337EP-??⟧ | **SCF-E4337EP-01** |
| ⟦SCF-4337Acct-??⟧, ⟦SCF-4337Account-?? recoverOwner⟧ | **SCF-E4337A-04, -05** |
| ⟦SCF-LSP8-??⟧ mint / revoke | **SCF-LSP8-01 / 03** |
| ⟦SCF-Combined-??⟧ addClaim / changeOwner | **SCF-CMB-06 / 01** |
| ⟦SCF-IDTX-??⟧, ⟦SCF-IdtxExecutor-??⟧ — execute / createIntent, fulfil / setCommitment, revokeCommitment | **SCF-IDTX-02 / 03, 04 / SCF-IDC-01, 02** |
| ⟦SCF-ZKVIN-??⟧, ⟦SCF-ZkVinGate-?? admit⟧ — admit / anchorCommitment | **SCF-ZKG-03 / 01** |
| ⟦SCF-??⟧ status anchor (§4(a) step 8) | SCF-E1155-03, SCF-E735-03, or IMP-L2.3-02 (status list, Ds) |
| ⟦SOL-1? IdtxExecutor⟧ / ⟦SOL-1? zk VIN⟧ / ⟦SOL-1?⟧ steward | **SOL-10 / SOL-11 / SOL-14** |
| ⟦PRO-?? JSON-RPC⟧ / devp2p / 1609.2 / Engine API (⟦PRO-??⟧ in RV-PROT-14) | **PRO-13 / PRO-11 / PRO-12 / PRO-14** |
| ⟦ALG-?? ECDSA⟧ / ecrecover / MPT proof | **ALG-02 / ALG-03 (+PRO-16) / ALG-18** |
| ⟦IMP-L3.2-??⟧ Hardhat / Besu / Geth / Anvil / RPC node | **IMP-L3.2-02 / 01 / 03 / 04 / 02 (today)** |
| ⟦IMP-L7.1-??⟧ ethers / web3.py | **IMP-L7.1-01 / 02** |
| ⟦IMP-L1.2-??⟧ snarkjs / circom | **IMP-L1.2-08 / 07** |
| ⟦IMP-L2.2-?? RocksDB/LevelDB⟧ | **IMP-L2.2-02** |
| ⟦HW-??⟧ SE / HSM / TEE / TPM / ECU-gateway / OBU / V2X modem / GNSS / node server / CPU-RNG | **HW-06 / 03 / 05 / 04 / 07 / 08 / 09 / 10 / 12 (validator), 11 (measurement host) / 01, 02** |
| ⟦BP-LH-??⟧ GNSS spoofing / SE extraction / TPM (host) | **BP-LH-04 / BP-LH-03 / BP-LH-06** |
| ⟦PF-??⟧ remaining: warm/cold access; relay overhead; dependency gas; disclosure leakage; leakage bits; prover time; HSM sign latency; PDR/CBR; log-scan cost; Poseidon | PF-52 (partial, EIP-2929); open (#50 measures, no formula); open (Q-R7-03); open (#61 measured, no PF); open; open (#57 measured; no bound needed); **PF-43** (ESTIMATED); **PF-44** (capacity) / PF-46 reserved; PF-52 read-side (partial) / open; open (ROM-class, cite as S) |

After v0-2, the panel expects zero unresolved ⟦⟧ outside the "open" rows. Each open row must say "qualitative" or carry a PF request number.

### 3.4 Contradictions and which source wins

**Rule (MTH, DS concur):** for what *exists and was executed*, the repository at 2026-10-22 wins over every Roots document. For what a *design* would do, Phase 1 stands, labelled DESIGN. Between Phase 2 documents, the owner of the tag wins on definition and the register row wins on numbers.

| # | Contradiction | Sources | Winner and disposition |
|---|---|---|---|
| X-1 | Δ = 2 s "sandbox default" vs no Δ on automine | R4 PF-24/25/28 vs `meta.json`; R7 PF-39 | Repo. R4 rows → DESIGN. **KD-R7-02 ACCEPT** (absorbs KD-R6-02 and KD-R7-07). |
| X-2 | *G* = 30/100 M vs 60 M | R4 vs `meta.json` | Both, as different things: 60 M is the *instrument's* limit, 30/100 M are design scenarios. **KD-R7-01 QUALIFY** (PN-14). |
| X-3 | *g_op* 50k–180k ESTIMATED vs measured per function | R4 vs crud_gas, #29/#34/#54 | Repo. **KD-R7-03 ACCEPT** (quote with GAS_CHARTER class and register row). |
| X-4 | Fleet "two orders above any row" vs 90.3× | R4 PF-24 vs R7 PF-50 | **KD-R7-04 QUALIFY**: G and Δ are both PAR, the design is privacy-excluded (PN-15), and did:ethr creation is 0 gas (#47). |
| X-5 | PF-11 *p_s*^*t_s* vs single-party setup | R4 vs #57 | Repo. **KD-R7-05 ACCEPT**. |
| X-6 | σ = 5 s (time) vs *k_f* − 1 (messages) | R4 vs #32, #46 | Repo. **KD-R7-06 ACCEPT**. Thesis states both units and adds a TTL (SLD-05). |
| X-7 | SOL-01 = "single-validator Besu + Foundry" | R2 vs tree | Repo. **KD-R6-01 ACCEPT** with lineage note; absorbs KD-R6-05. |
| X-8 | "IEEE 1609.2 PKI baseline" | thesis drafts and README vs `pki_identity.py` (X.509 P-256 in JSON) | Repo. **KD-R6-03 ACCEPT**: name it "X.509 P-256 pseudonym-certificate baseline (1609.2-style)". |
| X-9 | SSI BSM signature = EIP-191? | implicit in R3 flows vs `sign_message` (secp256k1/SHA-256) | Repo. **KD-R6-04 ACCEPT** (clarification). |
| X-10 | D21/D22/D18 live vs fixed | R6 vs DEFECT_LOG, contract source | Repo. Fix R6 (PN-01). |
| X-11 | Option mapping | R8 vs R2/R6 | R2 (frozen). Fix R8 (PN-22). |
| X-12 | RF linkability 0.37–0.82 vs ≈ 0.14–0.80 | R7 vs panel simulation | Panel, pending R7 v0-2 re-simulation (PN-12). |
| X-13 | Register #26 internal: 0.156 ms/neighbour, P\* ≈ 641 (head of row) vs 0.164 ms, P\* ≈ 609 (later in the same row) | `MEASUREMENT_CONDITIONS.md` #26 | Neither Roots doc is at fault. The repository must fix its own row (CA-09). R7 correctly used 0.164/609. |

---

## 4. What to solidify for the thesis

This is the panel's main output. Each directive names one locked artefact, its thesis home (per `docs/thesis/` chapter and section headings), its evidence status, the precondition before citation, and the owner thread. "Lock" means: the sentence, table or figure is frozen in its Phase 2 v0-2 form and cited by tag. Chapters do not restate the numbers in new words.

| SLD | Lock this | Thesis home | Evidence status | Before it can be cited | Owner |
|---|---|---|---|---|---|
| **SLD-01** | **Executed-system statement**: "All on-chain results come from Hardhat 2.28.6 automine (*N_v* = 1, chain 31337, *G* = 60 M, no block interval). Gas is portable across EVM networks for identical bytecode and state; latency is client + RPC + execution only and is not a time-to-confirm." (R7 PF-39; R6 L3 opening) | ch3 §3.1.3 Experimental platform; ch3 §3.3.1; ch5 §5.1; ch5 §5.8 Threats to validity; ch1 §1.5 | MEASURED (config: `meta.json`) + DERIVED | none beyond v0-2 wording; cite register M1 rule | Roots (this thread) |
| **SLD-02** | **Per-function gas vector** (ten columns × catalogue ops, incl. P1/X1) with GAS_CHARTER class, and ops-per-block at *G* as a derived column with *G* and Δ as PAR | ch5 §5.2; ch5 §5.9; Appendix A | MEASURED gas (#29, #34, #50, #54) / DERIVED capacity | reconcile run-of-record provenance (PN-21); one run id per table | Cost (gas) · Scale (capacity column) |
| **SLD-03** | **Tier-1 bottleneck result**: on the cached path, OBU verification throughput (*ρ_v* = *P r_BSM t_ver*) and airtime bind before the ledger; table of *P*\*(*f_id*) by verifier class | ch6 §6.3 Real-time V2V viability; ch5 §5.4 (only the measured software row) | MEASURED (sw, #26/#27) / ESTIMATED (HW classes) / DERIVED | primary sources for HSM/ECU *t_ver* (Q-R7-02); 1609.2 overhead sizes from the standard; fix PN-11 | Latency |
| **SLD-04** | **Message size → airtime**: #23 (596 B / 1,110 B) is 2.9×–5.0× the airtime of a digest-signed 1609.2 BSM; *N_fit* table at CBR 0.6 (802.11p) and PC5 sub-channel counts | ch5 §5.4 (as a consequence of #23); ch6 §6.3; ch7 §7.5 Limitations | MEASURED size / DERIVED airtime / ESTIMATED PHY overheads | source BSM part I and MAC overhead sizes; label the encoding "research JSON, not deployable" | Latency |
| **SLD-05** | **Freshness in two units**: message freshness (`freshness.py` window, replay cache, sizing 596/5,958) vs state staleness ≤ *k_f* − 1 messages (#32, #46); time bound only with a TTL; *k_f*\* = ⌊*r_s*σ_max⌋ + 1; the measured knee *k* ≈ 90 corresponds to ≈ 9 s revoked-key acceptance at 10 Hz | ch5 §5.4 and C4 crux text; ch6 §6.3; ch3 §3.4 (method: messages, not seconds) | MEASURED (#32, #37, #46) / DERIVED (PF-54/55) | implement TTL (CA-07) or state its absence; correct PN-11 | Latency + code |
| **SLD-06** | **Signature-scheme and replay-scope inventory**: three schemes across nine contracts; only `attestEvent` and the EntryPoint bind chain id; ERC-1056 `*Signed` bind registry + nonce only (D52); zero-signer seizure (D53); low-s status per contract | ch5 §5.6 Security analysis; ch4 §4.2 "Honesty caveats"; Appendix B | source-read (DESIGN-level fact about code) → MEASURED after CA-02 | author decision on D52 (fix vs upstream fidelity); executed two-chain replay test (CA-02); zero-signer guard (CA-03) | Security campaign G-C1 |
| **SLD-07** | **Pseudonymity negative result**: on-chain delegate pools are fully linkable (#38: 60/60 via one `eth_getLogs`); RF-layer linkability across pseudonym change unless reselection is forced (PF-44c, corrected) | ch5 §5.6 and C7 crux; ch6 (privacy discussion); ch7 §7.5 | MEASURED (#38) / DERIVED (PF-44c) | re-simulate PF-44c (PN-12); answer Q-R6-04/Q-R8-04 on scope | Security campaign G-C1 · Latency (radio) |
| **SLD-08** | **VIN hiding**: every non-ZK VIN path is enumerable (D64 address derivation; unsalted `keccak(VIN)` token ids in ERC-1155/LSP8; plaintext `getVINFromDID`, `getVehicleVIN`); #60 enumerates a serial-unknown VIN in 3.58 s; ZK-VIN is the only hiding path | ch5 §5.6; ch6 (GDPR/EDPB commitment form); ch2 §2.1 (only as motivation) | MEASURED (#60) / source-read (getters) | CA-10 (inventory of VIN exposures); STD wording check against EDPB guidance (fetch) | G-MV1 · Security campaign |
| **SLD-09** | **ZK-VIN cost model**: on-chain Groth16 = 181,000 + 6,150·*n_pub* + calldata, model vs measured within 1.3 % (PF-51, #58); proving 398.6 ms (#57); **setup single-party and insecure** | ch5 (layer-5 results section); ch4 (implementation); ch7 §7.5 | MEASURED / DERIVED | fix script labels (PN-10); state the setup caveat in the same sentence as the number | Security campaign · G-RIM |
| **SLD-10** | **Composition lemma** (PF-36): binding ≤ Σ ε over signature, hash, ledger non-equivocation, resolver integrity and the σ window. The ledger term dominates at small *N_v*. | ch3 (security argument framing) or ch6 §6.1 | DERIVED (proof sketch) | blind re-derivation in a fresh session (as Phase 1 did for R4); PN-19 rewording; Accuracy Ledger pass on SR-L..T | Roots (this thread) |
| **SLD-11** | **Repository-vs-option mapping** (R6 §3): what the repo measures (Families A–C, an F precursor), what it adds (LSP8, CVIN-Combined, MOBI profile, ZK-VIN/IDTX), what it never executes (Families D, E) | ch2 §2.2 opening; ch3 §3.2.2 | source-read | Terminology Freeze re-read via the Project (Q-R6-01) | Roots · G-RIM |
| **SLD-12** | **Measured-vs-designed table** (R6 §7, one row per sub-layer) plus R8's coverage headline (re-counted with ●/◐ split, PN-27) | ch1 §1.5 Scope and honesty; ch5 §5.8; Appendix E | MEASURED (as an inventory) | PN-01 and PN-27 fixes | Roots · G-RIM |
| **SLD-13** | **Consensus design tables** (PF-37 quorums; PF-38 messages; PF-40 t_conf incl. tail): appendix only, every cell DESIGN | new appendix (proposed **H — Design-only consensus bounds**); ch6 §6.6 / ch7 §7.6 Future work | DERIVED / DESIGN | none, but each table caption says "no executed trace" | Scale |
| **SLD-14** | **Revocation latency as tail quantiles under intermittent backhaul** (PF-48): a design rule, not a result | ch6 (revocation discussion); ch7 §7.6 | DERIVED / DESIGN | PN-17 wording | Latency |
| **SLD-15** | **IMinimalSSI primitive lock** (§6 below), so that ch3's "identical operation set" rests on fixed function names, F-numbers and semantics | ch3 §3.2.1; ch4 §4.2 | source-read; F-numbers **[B1]** pending | canon archive (`cvin-sandbox-v1.3`) F1–F12 signatures fetched; author decisions in §6 | new chat (author's parallel primitives chat) · G-RIM |
| **SLD-16** | **Contract security vector** (PF-61 a–e) over the SCF register: access-check coverage, replay-protection coverage, mutation kill rate, attack-matrix pass (43/43, #28), audit status | ch5 §5.6; Appendix B | MEASURED (c), (d) / to be tabulated (a), (b), (e) | tabulate (a), (b) from R6 §2.L5.2 (Q-R7-08); state "no external audit" | Security campaign G-C1 |

**Drop or demote (DRP).**

| DRP | Item | Action |
|---|---|---|
| DRP-01 | Any Besu/QBFT/Sepolia latency or finality as a result | demote to SLD-13 appendix, DESIGN |
| DRP-02 | R4's "fleet two orders above any row" and R7's PF-50 as thesis claims | demote to a ch6 sentence: "on-chain per-pseudonym anchoring fails on privacy before capacity" |
| DRP-03 | *P*\* ≈ 609 (and 641) as "capacity" | demote to "linear extrapolation beyond *P* ≤ 80" (the register's own caveat) |
| DRP-04 | "IEEE 1609.2 baseline" naming | rename (KD-R6-03) |
| DRP-05 | IDTX gas or latency | drop until E-F1-1 runs (Q-R7-03); IDTX stays a definition plus mechanism (ch6 §6.8) |
| DRP-06 | "SUMO with 50 vehicles" | drop (#15 E) |
| DRP-07 | PF-42 RNG seeding times, PF-41 fleet RNG table | demote to one ch6 sentence on hardware preconditions; they are ESTIMATED illustrations |
| DRP-08 | Pre-EIP-1108 703,500 gas comparison | drop (trivia) |
| DRP-09 | SOL-12, SOL-15, SOL-16, SOL-17 as "solutions" in the contribution list | demote to mechanisms unless justified (PN-09) |
| DRP-10 | R8 §4(a) licence-endorsement chain as the illustrative anchor chain | replace with §4(d) revocation (measured parts) |

**Do not claim (NC).**

| NC | Do not claim |
|---|---|
| NC-01 | any time-to-finality, consensus latency, decentralisation level or Nakamoto coefficient of the executed system other than "*N_v* = 1" |
| NC-02 | that the freshness window is secure against clock manipulation; it inherits GNSS integrity (BP-LH-04) |
| NC-03 | that ERC-1056 delegate pseudonyms are unlinkable |
| NC-04 | production soundness of any ZK-VIN admission (single-party setup) |
| NC-05 | any HSM, ECU or OBU performance figure as measured |
| NC-06 | that did:ethr resolution is secure against a lying RPC endpoint; it fails closed on errors, not lies |
| NC-07 | any M2 (Sepolia) latency; gas witness only, and the witness JSON is not committed |
| NC-08 | that salted `vinHash` plus AES-GCM hides the VIN in the repository's realisation (D64) |
| NC-09 | replay protection across chains for ERC-1056 signed operations (D52) |
| NC-10 | that the repository's messages are deployable on a 10 MHz channel at density (SLD-04) |

**Panel disagreement recorded.** DS and ITS want SLD-13 (consensus tables) kept in ch6 body text, because a CAV examiner will ask "what would QBFT give you". MTH and CR want it in an appendix to keep the results chapter clean. **Resolution:** appendix tables, with one ch6 paragraph that cites them and states the DESIGN label. TCS also asks that SLD-10 not enter the thesis until the blind re-derivation is done. The panel agrees: it is gated.

---

## 5. Code-level actions for the defect log and the WM-2 plan

The repository's files are not edited here. Each row is a suggested defect-log entry or plan item.

| CA | Existing D | Suggested title | Sev (suggested) | Source of finding |
|---|---|---|---|---|
| CA-01 | **D52** | ERC-1056 signed ops: decide chain-id binding (EIP-712 domain with `chainId`) vs upstream fidelity; record the decision | M | R6 BP-L5.2-01; PN-04 |
| CA-02 | (new, test) | Executed two-chain replay test for `*Signed` ops (31337 → 1337 with default deployer), to move D52 from source-based to reproduced | M | PN-04 |
| CA-03 | **D53** | Require `signer != address(0)` in all raw-`ecrecover` paths (EDR `*Signed`, CMB `addClaim`) | L | R6 Trace 2 |
| CA-04 | **D22 rest**, **D25c** | One signature scheme across claim contracts (EIP-191 or EIP-712), low-s guard in CMB and 4337 account | M | R6 BP-L1.1-01/02 |
| CA-05 | **D15** | Guardian recovery: time-lock and/or threshold; clear guardian on recovery | M | R6 BP-L5.2-04; `CVINVehicleAccount.sol` l. 228–234 |
| CA-06 | (new) | Groth16 setup is single-party and insecure: log as a deployment-blocking defect with the multi-party ceremony as remedy | M | #57; R6 BP-L1.2-04 |
| CA-07 | (new) | `ERC1056Provider` state cache has no TTL: a quiet sender's cached state is unbounded in time; add `min(k, T_ttl)` | M | R7 PF-54; Q-R7-07 |
| CA-08 | (new) | `freshness.py` docstring: "about 650 senders" → 596 (with margin 10), 5,958 without | L | R7 PF-53 |
| CA-09 | (register) | `MEASUREMENT_CONDITIONS.md` #26 states 0.156 ms/neighbour, P\* ≈ 641 at the head and 0.164 ms, P\* ≈ 609 later; make the row consistent | L | panel read of #26 |
| CA-10 | **D64** (extend) | VIN exposure inventory: unsalted `keccak(VIN)` token ids (ERC-1155 `vinHashOf`, LSP8 `tokenIdForVIN`), plaintext `getVINFromDID` (CVDR), `getVehicleVIN` (725xy), `getVINFromTokenId` (721) | M | R6 SCF-CVDR-09, E1155-07, LSP8-01 |
| CA-11 | (new) | M5 pseudonym pool design: on-chain delegates are linkable by construction; record as a design defect with the off-chain alternative | M | #38; R6 BP-L7.2-01 |
| CA-12 | (new) | `ZkVinGate`: static per-service challenge, bound only by `challengeSquared` | L | R6 BP-L1.2-05 |
| CA-13 | (new) | `SchnorrEcrecoverVerifier.prove`: no replay guard or context binding | L | R6 Trace 8 |
| CA-14 | **D51/D63** | Probe path judges expiry against last-learned chain time + 900 s; close D63 | L | R6 BP-L7.2-02 |
| CA-15 | **D26** | `changeOwner(id, 0)` restores self-control: decide lock vs reject | M | R6 SCF-VPR-02 |
| CA-16 | **D16 rest** | Silent `transferRegistryAuthority`: emit an event; single-key governance → multisig/timelock note | L | R6 BP-L4.2-02 |
| CA-17 | (new, audit) | CEI/reentrancy review of `payToll`, `_checkOnERC721Received`, ERC-725X and ERC-4337 `execute` | L | R6 BP-L5.2-06 |
| CA-18 | (new, hygiene) | Testbed key `SHA-256(vehicle_id)`: hard guard that refuses this path outside a test chain id; compose file binds 8545 on all interfaces | L | R6 BP-LH-02, BP-L0.4-01 |

Enhancements, not defects: SPS reselection counter and 802.11p airtime model in `cv2x_stack.py` (Q-R7-04); RSU propagation delay in I3 (Q-R7-05); run E-F1-1 IDTX gas (Q-R7-03).

---

## 6. DID and DID-system primitives to lock "pat"

*What this section does for the level above:* chapters 3–5 compare "an identical operation set" across substrates. That comparison is only as firm as the names, numbers and semantics of the operations. *What it trusts from below:* the L1 primitives and the L5 registry state. The author reviews this list in a parallel chat. Each item is tagged `PRM-<sublayer>-nn`. Blocking questions are listed with the item they block.

### 6.1 The minimal primitive set, by sub-layer

| PRM | Sub-layer | Primitive / function | Fixed semantics to lock | Repo realisation | Blocking question |
|---|---|---|---|---|---|
| PRM-L1.1-01 | L1.1 | ECDSA secp256k1, RFC 6979 nonces, low-s | which digest (keccak over EIP-191 / EIP-712 / raw) per use | ALG-02/03; three schemes in use | B-03 one scheme |
| PRM-L1.1-02 | L1.1 | keccak-256; SHA-256 | which hash for which binding (on-chain digests keccak; BSM SHA-256) | ALG-07/08 | B-08 BSM hash |
| PRM-L1.1-03 | L1.1 | salted hash commitment *C* = H(*x* ‖ *s*), \|*s*\| ≥ 128 bits | salt mandatory for any low-entropy attribute (VIN) | IdentityCommitments; ZK-VIN | **B-05 salted VIN** |
| PRM-L1.1-04 | L1.1 | Poseidon / Groth16 (only for ZK path) | setup trust stated | ALG-09/12 | B-09 setup |
| PRM-L5.2-01 | L5.2 | registry state: `owners`, `delegates[type][addr] → validTo`, `nonce`, `changed`, attributes event-only | event-only attributes are not readable on chain | SCF-EDR | — |
| PRM-L5.2-02 | L5.2 | `identityOwner(id)` default-to-self | implicit creation (0 gas) | SCF-EDR-01 | B-06 explicit vs implicit creation |
| PRM-L5.2-03 | L5.2 | `changeOwner` (+Signed) | zero-address semantics; chain-id scope | SCF-EDR-03/04 | **B-02 chain id**, B-07 zero |
| PRM-L5.2-04 | L5.2 | `addDelegate` / `revokeDelegate` (+Signed), `validDelegate` in chain time | revocation = set `validTo = now` | SCF-EDR-02/05/07 | **B-04 delegate-revocation fold** |
| PRM-L5.2-05 | L5.2 | `setAttribute` / `revokeAttribute` (+Signed) | "permanent" = 100-year validity (D18 fix) | SCF-EDR-09/11 | B-04 |
| PRM-L5.2-06 | L5.2 | deactivation (terminal revoke with `previousChange`) | absent from pure EDR; present in VPR (D21 decision D-F) | SCF-VPR-07 | B-10 deactivation in Set A |
| PRM-L6.1-01 | L6.1 | did:ethr syntax incl. chain qualifier; CAIP-10 `blockchainAccountId` | decimal chain reference | ALG-23; D27 | B-11 CAIP-10 |
| PRM-L6.1-02 | L6.1 | did:ethr resolution: event replay from `changed`, fail-closed, chain-time validity | modes: on-chain vs offline-synthesised labelled | ALG-23/23a; SOL-17 | B-12 resolver trust in endpoint |
| PRM-L6.1-03 | L6.1 | did:mobi (salted VIN hash → DID) | the salt and its custody | ALG-24 | B-05 |
| PRM-L6.2-01 | L6.2 | VC v2.0 Data Integrity with `eip191-secp256k1-recovery-2024`, deterministic JSON | declared deviation from URDNA2015 | IMP-L6.2-01/04 | B-13 cryptosuite |
| PRM-L6.2-02 | L6.2 | credential status (`credentialStatus`, registry) | anchored or not | IMP-L2.3-01 | B-14 status anchoring |
| PRM-L6.2-03 | L6.2 | createPresentation (**F8**, sourced) | salted digests; nonce/hash anchor | IMP-L6.2-02; #54 P1 | — |
| PRM-L6.3-01 | L6.3 | IMinimalSSI F1–F12, Set A (F1–F4, F9–F12) / Set B (F5–F8) | the order inside sets | `BASIC_ID_SET_EXTENSION.md` | **B-01 F-numbering** |
| PRM-L6.3-02 | L6.3 | X1 `execute` as Set A member | real executor required (ERC-725 basic is a stub) | #54 | B-15 X1 membership |
| PRM-L6.3-03 | L6.3 | IDTX dependency kinds Owner / Delegate / Commitment; caller-independent predicate | definition P2-D8 | SOL-10 | — |
| PRM-L7.2-01 | L7.2 | signed message = payload ‖ generation time; window 1.0/0.1 s; content-keyed replay cache | message freshness | IMP-L7.2-01 | B-08 |
| PRM-L7.2-02 | L7.2 | state refresh every *k_f* **and** TTL | state freshness | SOL-16; CA-07 | B-16 TTL |

### 6.2 Blocking questions

| B | Question | Why it blocks | Evidence |
|---|---|---|---|
| B-01 | **F-number order inside Set A and Set B** is [B1] (canon archive not on any branch); and "F-" collides in prose with Phase 1 findings F-R1..4 and R6's casual "F-deactivation" | ch3 cannot say "F3" | `BASIC_ID_SET_EXTENSION.md` l. 10, 20–21 |
| B-02 | **Chain-id binding of signed ops** (D52): fix (non-upstream bytecode) or document the narrowed G3 | fixes the security claim of PRM-L5.2-03 | `EthereumDIDRegistry.sol` l. 160–172 |
| B-03 | **One signature scheme** for claims and attestations (EIP-191 vs EIP-712 vs raw) | interop and replay scope | D25c; R6 summary |
| B-04 | **Delegate-revocation fold**: is attribute revocation (D2) a Set A op, and is revokeDelegate (D1) folded into it? (#53: wrapper and ERC-721 fail Set A only on D2) | changes Set A admission counts (11/11 vs 10/11) | register #53 |
| B-05 | **Salted commitment for the VIN everywhere**: salt length, custody, and whether did:mobi's identifier is salted | NC-08; SLD-08 | D64; #60 |
| B-06 | explicit (`registerVehicle`, 54,868 gas) vs implicit (0 gas) creation as the canonical createDID | cost tables and the fleet argument | #22, #47 |
| B-07 | `changeOwner(0)`: lock or reject (D26); zero-signer guard (D53) | PRM-L5.2-03 | D26, D53 |
| B-08 | BSM signature digest: SHA-256 (current) or keccak/EIP-191 for parity with on-chain checks | PRM-L7.2-01 | `erc1056_provider.py` `sign_message` |
| B-09 | ZK setup: name the ceremony required before any production claim | NC-04 | #57 |
| B-10 | Is deactivation in the minimal set (pure EDR lacks it)? | Set A completeness | SCF-VPR-07 vs SCF-EDR |
| B-11 | CAIP-10 chain reference format (D27) | conformance | D27 |
| B-12 | Resolver trust in the RPC endpoint (lying endpoint) — accept as an assumption or add proofs | NC-06 | BP-L0.4-02 |
| B-13 | Thesis-defined cryptosuite vs a registered one | W3C conformance claim (#4, #24) | `vc_issuer.py` l. 12–14 |
| B-14 | Status anchoring: in-memory/JSON file vs on-chain anchor | revocation claims | IMP-L2.3-01 |
| B-15 | X1 in Set A (only 725xy and 4337 execute) | admission counts (#54) | #54 |
| B-16 | TTL on cached state | SLD-05 | PF-54 |

### 6.3 Author's checklist (work through in order)

1. Fetch the canon F1–F12 signatures (`cvin-sandbox-v1.3`) and fix F-numbers. Adopt the prose prefix "IMS-F*n*" to avoid the F-R collision (B-01).
2. Decide B-04 and B-15. Recompute Set A admission counts from #53/#54 under the decision.
3. Decide B-02 and B-07. If "document", write the narrowed G3 sentence for ch5 §5.6. If "fix", open a WM item (CA-01, CA-03).
4. Decide B-03 (one scheme). Record the scheme per PRM-L1.1-01 use.
5. Decide B-05: salt length (≥ 128 bits), custody (owner wallet / Steward vault), and the did:mobi identifier form.
6. Decide B-06: the canonical createDID for cost tables.
7. Decide B-10: whether deactivation is in the minimal set.
8. Decide B-08 and B-16 for the V2X message profile.
9. Record B-11, B-13, B-14 as conformance caveats or fixes.
10. Record B-09 and B-12 as stated assumptions (NC-04, NC-06).
11. Answer Q-R6-04 and Q-R8-04 together: is 1609.2-style pseudonymity in scope? If yes, the M5 pool is retired as a design (CA-11).
12. Freeze the PRM table as `PRIMITIVES_LOCK v1.0`. From then on every chapter cites PRM tags or IMS-F numbers.

---

## 7. Instructions to the second-pass writers

Apply in this order. Each writer begins by applying the §3.1 re-keying with retirement lines and ends with a HANDOFF that lists every key retired.

### 7.1 R6 v0-2

1. **Re-key**: Q-R7..12 → Q-R6-01..06; KD-R4..8 → KD-R6-01..05 (merge 02 into KD-R7-02, 05 into 01); PRO-13x/y/z → PRO-23/24/25.
2. **Defect statuses (PN-01)**: re-verify every Dn against `DEFECT_LOG.md`; correct D18, D21 and D22 rows and BP-L2.1-02. Add a "status @ 2026-10-22" column to the SCF register.
3. **Fix ALG-21 → ALG-23** cross-reference; annotate ALG-17/21 (PN-02).
4. **Add BPs** BP-L0.1-02, BP-L7.2-03 and BP-L7.2-04, bound by R7 PF-44c, PF-54 and PF-44 (PN-08).
5. **BP-L5.2-01**: state the precondition concretely (default deployer, 31337/1337) and cite CA-02 (PN-04).
6. **Audit or remove BP-L5.2-06**; cross-check access control against the security suite for the 40 state-changing rows on EDR, VPR, MOBI1/2, CMB and E4337A at least (PN-05).
7. **Resolve PF placeholders** with §3.3 Table A′. Request PF-63..66 from R7 for the open ones, or mark them qualitative (PN-03).
8. **SOL decision** (PN-09): justify SOL-12/15/16/17 against the trilemma or re-label them as mechanisms.
9. Label both gas figures in Trace 1 (PN-06); use counts 562/376 (PN-07).
10. Add one "serves R3 requirement Rn/In" line to each §6 trace.
11. Adopt the unified status scale (PN-32), including **I** for IdtxExecutor.
12. Cut nothing else. The atlas is long but every row is used by R8.

### 7.2 R7 v0-2 and `r7_calc.py`

1. **Re-key**: KD-R4-01..07 → KD-R7-01..07; KD-R4-08/09 → CEV-R7-01/02. PAR references → R8 numbers (Table B). Keep Q-R7-01..08.
2. **Script labels (PN-10)**: re-label every print to the document's PF numbering. Add a header mapping and an assertion that each document PF appears in the output.
3. **Fix PF-43's condition (PN-11)** and reconcile it with the #32 knee in one paragraph.
4. **Re-simulate PF-44c (PN-12)**, seeded in the script; restate the range.
5. **Fix PF-52 (PN-13)**: LOG base cost and calldata basis.
6. **Dispose KD-R7-01/04 as QUALIFIED (PN-14)**; tabulate capacity at *G* ∈ {30 M, 60 M, 100 M}.
7. **Add the PF-50 privacy-exclusion sentence (PN-15).**
8. Quote #26/#27 at register precision and lead with 305 (PN-16); MC "< 3 %" (PN-17).
9. **Citations (PN-18)**: LIM-R7-nn rows for every unfetched source. Verify-on-demand → ESTIMATED (practice).
10. Reword PF-36 as a labelled union bound; add the *N_v* = 1 instance (PN-19). Prepare SR/PF statements for a blind re-derivation session (SLD-10).
11. Provenance (PN-21): cite register rows; give run ids as provenance.
12. Supply PF-63..66 if R6 requests them, and assign or drop the gossip PF.
13. Resolve ⟦⟧ with §3.3 Table B′; adopt the unified status scale.
14. Cut: the Byzantium comparison (DRP-08). Shorten §4.1–4.2 to one table (DRP-07).

### 7.3 R8 v0-2

1. **Re-key**: Q-R7..10 → Q-R8-01..04. Append PAR-31..43 from R7 (Table B). R8 is now PAR owner, so write that into the header.
2. **Fix the O-mapping (PN-22)** from R6 §3 / R2 §3.3.
3. **Reverse the status upgrades (PN-23)**: RV-SCF-32, RV-IDTX-14, RV-SIG-12, RV-SCN-12, RV-HW-10, as specified in the PN row.
4. **Re-anchor state freshness (PN-24)**: RV-READ-03 and RV-ALG-09 → `erc1056_provider.py`.
5. **Bind MDs to R7 PFs (PN-25)** with Table C′.
6. **Split ● into ● and ◐ (PN-27)**; recount the coverage headline and regenerate FIG-R11.
7. **Add rows (PN-28)**: RV-THR-11 cross-chain signed-op replay (D52), RV-THR-12 zero-signer seizure (D53), RV-THR-13 lying RPC endpoint, RV-THR-14 pseudonym-pool linkage (#38), RV-THR-15 deterministic test-key derivation; RV-PROT-16 message encoding size; cite #57 on RV-GOV-06; add a TTL row under RV-READ.
8. **Resolve placeholders** with Table D′ (all 155).
9. Counts (PN-29): 62 register rows; 562/376 tests.
10. Make §4(d) the lead worked chain; keep §4(a) as Ds (PN-30, DRP-10).
11. Adopt the unified status scale; R8's **I** becomes suite-wide.

### 7.4 Common to all three

Each document gets a new header line "re-keyed per R9 §3.1", a "Phase 1 erratum" pointer (to the X-1..X-9 dispositions), and a final self-check of zero ⟦⟧ except declared "open" rows. The figures (`docs/roots/phase2/figures/`) are regenerated from the corrected tag lists after all three v0-2 passes (FIG-R11 at least).

---

## 8. HANDOFF (R9 v0-1)

**Files.** `docs/roots/phase2/90_R9_panel_review/claude_CVIN_SC_Roots_Panel_Review_R9_v0-1.md` (this). Nothing else written; repository files untouched. `r7_calc.py` was executed read-only.

**Tags assigned.** PN-01..33 (HIGH 6, MED 19, LOW 8); SLD-01..16; DRP-01..10; NC-01..10; CA-01..18; PRM-L1.1-01..04, PRM-L5.2-01..06, PRM-L6.1-01..03, PRM-L6.2-01..03, PRM-L6.3-01..03, PRM-L7.2-01..02; B-01..16; contradiction ids X-1..X-13. **Consumed:** R6/R7/R8 v0-1 tags; register rows #2, #15, #20–#28, #30–#32, #37–#39, #46, #47, #50, #53, #54, #57, #58, #60; D15, D16, D18, D21–D27, D51–D54, D63, D64.

**Re-keying (summary).** Record keys are namespaced by issuer: Q-R6-01..06, Q-R7-01..08, Q-R8-01..04; KD-R6-01..05, KD-R7-01..07; R7's KD-R4-08/09 → CEV-R7-01/02. R8 owns PAR-: R7's 26 PARs map onto R8 PAR-02..26, with 13 appended as PAR-31..43. R6 PRO-13x/y/z → PRO-23/24/25. Script PF labels follow the document.

**Five load-bearing decisions.** (1) The repository wins on what exists; Phase 1 stands only as DESIGN. (2) The three verdict statements in §1 enter ch1/ch3/ch5/ch6 as locked sentences (SLD-01, -03, -06/-07). (3) KD-R7-01/04 are qualified, not accepted: the Hardhat gas limit is an instrument value, not a design input. (4) Consensus tables go to an appendix labelled DESIGN (SLD-13). (5) Status **I** and the ●/◐ split become suite-wide.

**Open questions.** Q-R9-01: does the author accept the SOL demotions (PN-09)? Q-R9-02: is 1609.2-style pseudonymity in scope (with Q-R6-04, Q-R8-04)? Q-R9-03: should the new appendix H (design-only consensus bounds) exist? Q-R9-04: who runs the blind re-derivation of PF-36 (SLD-10)?

**Corrections issued.** PN-01 (R6 stale defects), PN-10/11/12/13 (R7 arithmetic and labels), PN-22/23 (R8 mapping and statuses), CA-09 (register row #26 internal inconsistency).
