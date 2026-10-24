# CVIN-SC · Roots Thread G-R1 · Phase 2 — R9 Professors' Panel Review, Disposition Pass

| Field | Value |
|---|---|
| Document | **R9** Professors' Panel Review |
| Version | **v0-2** (disposition pass; v0-1 kept unchanged beside it) |
| Date | 2026-10-23 |
| Branch / tree read | `roots/G-R1-phase2`, working tree as found (no commit made, no branch switched) |
| Consumes | **R6 v0-2** (Full-Stack Atlas), **R7 v0-2** and `r7_calc_v0-2.py` (executed for this pass; self-check PASS), **R8 v0-2** and `r8_coverage.py` (executed; 311 rows, 0 placeholders), R9 v0-1; repo spot-checks: `docs/DEFECT_LOG.md` (D15–D26, D51–D54, D63–D65), `docs/MEASUREMENT_CONDITIONS.md` rows #26, #27, #38, #57 and the M2 condition class, `docs/STATUS_2026-10-22.md` l. 112, `EthereumDIDRegistry.sol` l. 160–172, `MOBI/ERC1056Registry.sol` l. 18, 52, 261, `CVIN_NFT_DID_ERC721.sol` `payToll`, `CVINMinimalEntryPoint.sol`, both Hardhat configs, `freshness.py` l. 47, `results/metrics/latest/meta.json`, `test/L2-identity-system/per-option/**` |
| Assigns | dispositions of **PN-01..PN-33**; new findings **PN-34..PN-39**; final **SLD-01..SLD-18**; final **DRP-01..DRP-12**; final **NC-01..NC-13**; final **CA-01..CA-24**; final **PRM** lock checklist (§5); rulings **RL-01..RL-06** |
| Panel | **DS** distributed systems and blockchain · **CR** applied cryptography and security · **TCS** theoretical computer science · **ECE** wireless/V2X and embedded hardware · **ITS** CAV/ITS transportation systems · **STD** identity standards and policy · **MTH** thesis writing and research methods |
| Status scale | suite-wide (PN-32): **M** · **Dv** · **I** · **Ds** · **E** · **S** · **—** |

`Progress ▓▓▓▓▓▓▓▓▓░ 90 %`. Every PN has been dispositioned with evidence, the six rulings requested are made, the SLD list is final, and the lock checklist is ready to tick. The remaining 10 % is outside this thread: the author's answers to the §5 checklist, and the v0-3 mechanical sweep of R6 and R8 (PN-35).

**How to read.** §1 is the disposition table: one row per v0-1 finding, followed by the six explicit rulings. §2 lists what the second passes themselves got wrong or left inconsistent. §3 audits the namespaces after re-keying. §4 is the panel's final output: what the thesis says, where it says it, and what has to happen first. §5 is the primitives checklist for the parallel chat. §6 lists repository actions. §7 is the HANDOFF.

**Verdict in three lines.** The second passes are good work. 26 of 33 findings are closed, 4 are partly closed, 2 are disputed by the writers and the panel accepts both disputes with conditions, and 1 (PN-33, the Phase 1 erratum at source) is still open. The three Phase 2 conclusions from R9 v0-1 §1 stand unchanged: the executed chain is *N_v* = 1, the OBU and channel saturate before the ledger, and the code carries real replay-scope and linkability findings. One input has moved under the documents since they were written. Register row #26 was re-stated on 2026-10-23 (WM-2 A5), so R7's lead figure *P*\*(0.5) = 305 is now history and the lead becomes **320** (PN-34).

---

## 1. Disposition of PN-01..PN-33

Key: **CLOSED**, the fix is applied and verified. **PARTLY CLOSED**, the fix is applied with a residual that is named. **OPEN**, not applied. **DISPUTED-ACCEPTED**, the writer departed from the panel's fix and the panel accepts the departure, possibly with conditions. **DISPUTED-REJECTED**, the writer departed and the panel does not accept. Evidence cites the v0-2 section, plus a repository line where the ruling depends on a fact.

### 1.1 Table

| PN | Sev | Finding (short) | Disposition | Evidence (v0-2 section; repo check) | Residual action |
|---|---|---|---|---|---|
| PN-01 | HIGH | R6 stale defect statuses (D18, D21, D22) | **CLOSED** | R6 §2.L5.2 SCF-CVDR-03 (D18 fixed `65a143f`), SCF-VPR-07 (D21 fixed), SCF-CMB-03/06/07 (D22 part), IMP-L2.1-04, BP-L2.1-02 "historical; closed"; new "Dn @ 10-22" column. Repo: `ERC1056Registry.sol` l. 18/52/261 (`DIDRevoked` carries `previousChange`); `DEFECT_LOG.md` l. 46 (100-year validity), l. 49 (open: `updateVehicleKey`), l. 50 and l. 68 (D22 rest open) | none; R6 marks D22 "part", which matches l. 68 |
| PN-02 | MED | ALG-21→23 cross-ref; ALG-17/21 annotation; PRO-13x/y/z | **CLOSED** | R6 key-change table; L1.1 ALG-17; L4.1 ALG-21; L7.2 PRO-23/24/25 with strike-through | none |
| PN-03 | MED | eight unbounded PF placeholders; ⟦15⟧ ill-posed | **CLOSED** | R6 §8 (each placeholder resolved, re-posed, "qualitative" or requested); BP-L5.2-01 restates ⟦15⟧ as a precondition. R7 §7.1 supplies PF-63..66 | R6 still says "requested" for PF-63..66 → PN-35 sweep |
| PN-04 | MED | D52 precondition understated | **CLOSED** | R6 BP-L5.2-01 and Trace 2: default Hardhat accounts on 31337 and 1337; same deployer, deployment nonce and signer nonce; caveat that the testbed does not compile EDR. Repo: `1_blockchain-identity/hardhat.config.js` l. 62 (31337), `cv2x-testbed/hardhat.config.js` l. 16 (1337); `EthereumDIDRegistry.sol` l. 160–172 (digest = 0x19‖0x00‖this‖nonce‖identity‖"changeOwner"‖newOwner, no chain id) | executing the test is Phase 3 (CA-02); until then the claim stays source-read (I) |
| PN-05 | MED | access-control and reentrancy audits promissory | **CLOSED** | R6 §4.2 CEI table (four surfaces), Q-R6-06 closed; §2.L5.2 "Neg." column over 44 rows. Repo: `payToll` reads checks → `call` → `require(sent)` → event, no state after the call (verified) | negative-test gap carried as Q-R6-07 → CA-19 (RL-05) |
| PN-06 | LOW | two gas figures for `changeOwner` | **CLOSED** | R6 §6 Trace 1 (68,854 #2 test context; 51,754 harness U1, run `1f4ace0`) | none |
| PN-07 | LOW | test counts | **CLOSED** | R6 IMP-L7.1-01/02 (562 / 376, STATUS §5 addendum). Repo: STATUS l. 112 confirms | none |
| PN-08 | MED | missing BPs found by R7 | **CLOSED** | R6 §4.1 BP-L0.1-02, BP-L7.2-03, BP-L7.2-04 with bounds | BP-L0.1-02's bound is now **PF-45**, not "PF-44c" → PN-35 |
| PN-09 | MED | SOL inflation (SOL-12/15/16/17) | **DISPUTED-ACCEPTED** (conditions) | R6 §5: SOL-12, -15, -17 demoted to mechanisms; SOL-16 kept as SOL, with argument. Ruling RL-01 below | R8 RV-READ-03 and RV-ALG-09 still say "SOL-16 (mechanism, PN-09)" → PN-35 |
| PN-10 | HIGH | script PF labels ≠ document | **CLOSED** | R7 header and §13 item 2; panel ran `r7_calc_v0-2.py`: exit 0, "SELF-CHECK PASS: all 54 document PF tags appear … all R7-owned labels (PF-32..66) appear in the document" | none |
| PN-11 | HIGH | dimensional error in ledger-bottleneck condition | **CLOSED** | R7 §4.2 "Two criteria". Script prints `[PF-43] refresh-load criterion … P=100 = 27.9`. Panel hand check: 10 × 100 × 0.01394 / 0.5 = 27.88. The total-budget knee 0.01394/(0.0005 − 0.000346) = 90.5 → 91 reconciles #32's "*k* ≈ 90" | the *t_local* = 0.346 ms input comes from #32 and is unaffected by PN-34 |
| PN-12 | MED | PF-44c exponential approximation wrong | **CLOSED** | R7 §4.4, now **PF-45**: exact residual-life computation plus seeded MC, 0.136 / 0.449 / 0.805. Script lines 155/158/161 agree. Panel v0-1 simulation gave 0.135 / 0.449 / 0.804, within MC noise. The closed form at *P_keep* = 0, (1+…+5)/11 × 0.1 = 0.1364, was checked by hand | R6 and R8 still cite "PF-44c" → PN-35 |
| PN-13 | MED | PF-52 storage-vs-log ratio overstated | **DISPUTED-ACCEPTED** (qualified) | R7 §5.4 and §12: LOG3 9,692 (script l. 243); 27.7× on the EIP-2028 basis (l. 245); 17.7× under the EIP-7623 floor on `osaka` (l. 246). Repo: `meta.json` `"hardfork": "osaka"`. Ruling RL-02 below | add the floor-binding condition (PN-37); LIM-R7-08 receipt (CA-20) |
| PN-14 | MED | KD-R4-01/04 chimera with 60 M | **CLOSED** | R7 §5.1 capacity at *G* ∈ {30, 60, 100} M; §10 KD-R7-01/04 QUALIFIED; R6 L4.3 IMP-L4.3-01 "instrument value"; R8 PAR-06 | none |
| PN-15 | MED | PF-50 sizes a privacy-excluded design | **CLOSED** | R7 §5.2, where the exclusion sentence leads | none |
| PN-16 | LOW | precision beyond register; lead with 305 | **PARTLY CLOSED** | R7 §4.2 quotes 0.142 / 0.090 at register precision, leads with 305 and gives 352 as the crypto-only ceiling. Repo: #26 was re-stated on 2026-10-23 (WM-2 A5, Exp. D `0b39570`); 0.156 ms/neighbour and *P*\* ≈ 641 are now current, and "the earlier 0.164 … and *P*\* ≈ 609 are history" | lead becomes **320** (50/0.156) → PN-34 |
| PN-17 | LOW | MC agreement overstated | **CLOSED** | R7 §4.8: 2×10⁶ draws, max 1.34 % on non-degenerate cells; one edge cell excluded with a reason | none |
| PN-18 | MED | unfetched citations carry load | **PARTLY CLOSED** | R7 §11 LIM-R7-01..08; verify-on-demand → E (LIM-R7-04) | Accuracy Ledger fetch not yet run; each SLD that rests on a LIM is gated (§4) |
| PN-19 | LOW | PF-36 heterogeneous sum | **CLOSED** | R7 §2.5 term-nature table; *N_v* = 1 instance (5.00×10⁻²); 36.7 orders (panel: log₁₀(1.402×10⁻²/2.94×10⁻³⁹) = 36.68) | blind re-derivation still gates SLD-10 |
| PN-20 | LOW | KD-R4-08/09 are confirmations | **CLOSED** | R7 §10 CEV-R7-01/02 | none |
| PN-21 | MED | run-of-record ambiguity | **CLOSED** | R7 §5 provenance rule (register row = authority, run id = provenance; values identical across runs `1f4ace0`, `7a9a996`, `a9e2a28`, `9bdf451` where checked); R6 Trace 1 | SLD-02 keeps the Cost-thread confirmation as a precondition |
| PN-22 | HIGH | R8 wrong option mapping | **CLOSED** | R8 §0 mapping table and §3.9 O-column: 1056→O1, 1155→O2, 721→O3, 725→O5, 725xy/735→O6, 4337→O7, LSP8 none, Combined O18 precursor. Matches R6 §3 row for row | none |
| PN-23 | HIGH | R8 status upgrades by assertion | **CLOSED** | (a) RV-SCF-32 → "— (stub; D23)"; (b) RV-IDTX-14 → SCF-E725XY-04, SCF-E4337A-02, with new RV-SCF-43/44; (c) RV-SIG-12 → Ds, RV-SCN-12 → "M (#38): negative result, linkable"; (d) RV-HW-10 CPU only, RV-HW-12 RNG "—". Repo: D23 l. 51 confirms the stub; #38 confirms "Linkability verdict PASS (fully …)" | none |
| PN-24 | MED | message vs state freshness conflated | **CLOSED** | R8 RV-READ-03, RV-ALG-09, RV-SVC-02 re-anchored to `erc1056_provider.py`; RV-ALG-10 kept on `freshness.py`; KD-R8-06. R6 adds IMP-L7.2-04 | none |
| PN-25 | MED | MDs cite only Phase 1 PFs | **PARTLY CLOSED** | R8 §1: every MD bound to an R7 PF per Table C′ | MD-09 cites "PF-44c" (now PF-45); MD-02/MD-20 say "req PF-65/66" although both now exist → PN-35 |
| PN-26 | MED | PAR collision | **CLOSED** | R8 §2 sole owner, PAR-01..43, mapping table; R7 §8 cites R8 numbers only, and declares no PAR | R8 PAR-37 "gossip PF to be assigned"; R7 has dropped it → PN-35 |
| PN-27 | MED | ● conflates M with Dv | **CLOSED** | R8 §5 four-code matrix computed by `r8_coverage.py`. Panel re-run: **● 77 · ◐ 3 · ○ 115 · · 223** (418 cells, 311 rows) | FIG-R11 not yet regenerated (CA-24) |
| PN-28 | MED | consequential findings lack RV rows | **CLOSED** | R8 RV-THR-11..15, RV-PROT-16, RV-READ-14; RV-GOV-06 cites #57 | none |
| PN-29 | LOW | counts drift | **CLOSED** | RV-MET-01 "62 numbered rows" (panel count of `MEASUREMENT_CONDITIONS.md`: 62); RV-MET-02/03 562/376 | none |
| PN-30 | LOW | licence chain as illustrative | **CLOSED** | R8 §4.1 lead chain = revocation (measured parts); §4.5 licence chain kept as Ds | none |
| PN-31 | HIGH | record-key collisions | **PARTLY CLOSED** | All three documents carry "re-keyed per R9 §3.1" and retirement lines; §3 below finds no live collision | R7's KD range is stated two ways (PN-38); R8 header still reads "R7 PF-32..62" (PN-35) |
| PN-32 | MED | divergent status vocabularies | **CLOSED** | identical scale lines in R6 header, R7 header and R8 §0 | none |
| PN-33 | MED | Phase 1 numbers not re-labelled at source | **OPEN** | All three v0-2 headers point to "R9 §3.4 X-1..X-9", but no R4 v0-2 and no erratum note exists under `docs/roots/phase1/` (panel grep: no "erratum" outside Phase 2) | write `docs/roots/phase1/PHASE1_ERRATUM_v1-0.md` (Roots thread), covering X-1..X-9 (CA-21). Thesis-blocking for any chapter that cites R4 PF-24/25/28 |

**Disposition counts (33):** CLOSED **26** · PARTLY CLOSED **4** (PN-16, 18, 25, 31) · OPEN **1** (PN-33) · DISPUTED-ACCEPTED **2** (PN-09, PN-13) · DISPUTED-REJECTED **0**.

### 1.2 The six rulings requested

**RL-01 — R6 keeps SOL-16 as a solution (PN-09). DISPUTED-ACCEPTED, with three conditions.**
*R6's argument (R6 §5):* the *k*-refresh cache with its one-call probe is the repository's realisation of HAA-1's read rule. It moves a design along the finality–latency axis by trading bounded staleness for latency, so it is a trilemma move, not hardening.
*Panel view.* DS and ITS accept the argument. R9 v0-1 §1 point 2 itself uses this move ("once a verifier caches identity state … the ledger is off the Tier-1 path"), so a demotion would be inconsistent with the panel's own reasoning. MTH and CR raise one objection: the trilemma move belongs to SOL-05 (HAA-1), which is Phase 1's solution. SOL-16 is its measured instance. Counted as a separate contribution, it would double-count one idea.
*Ruling.* SOL-16 stays a SOL under these conditions:
- (i) It is written "SOL-16, the measured realisation of SOL-05's read rule". The contribution list counts SOL-05 and SOL-16 as **one** contribution, "cached-read identity verification, designed (SOL-05) and measured (SOL-16)".
- (ii) Every citation carries the time-bound caveat in the same sentence: staleness is bounded in messages (≤ *k_f* − 1, #32/#46) and is unbounded in seconds until a TTL exists (BP-L7.2-03, CA-07).
- (iii) R8 v0-3 removes "mechanism" from RV-READ-03 and RV-ALG-09 (PN-35).
SOL-12, -15 and -17 stay demoted as R6 proposes. The resulting contribution list is SOL-10, SOL-11, SOL-13, SOL-14 and SOL-05/16 (SLD-18).

**RL-02 — R7's 18–28× storage-vs-log ratio under EIP-7623 (PN-13), and LIM-R7-08. DISPUTED-ACCEPTED, qualified.**
*Facts checked.* `meta.json` records `"hardfork": "osaka"`. Osaka follows Prague, which activated EIP-7623, so the calldata floor (10 gas per token; a non-zero byte is 4 tokens, i.e. 40 gas) is part of the executed fork's rules, provided Hardhat 2.28.6 implements it. That proviso is LIM-R7-08. The script reproduces: storage 707,200 + calldata 16,384 = 723,584; log 9,692 + 16,384 = 26,076 < floor 40,960, so the log transaction pays the floor and 723,584/40,960 = 17.7×.
*Panel qualification (CR, DS).* The floor binds only when a transaction's execution gas is below 24 gas per non-zero calldata byte (40 − 16). At 1 kB that threshold is 24,576 gas. A *bare* LOG3 (9,692) is under it. A *real* ERC-1056 `setAttribute` also writes `changed[identity]`: a cold zero→non-zero SSTORE (22,100) on an identity's first write, or ≈ 5,000 on later writes, plus dispatch and memory. The first write therefore sits above the threshold and pays the EIP-2028 price (ratio ≈ 28× or less), while later writes sit below it and pay the floor (≈ 18×). The 18–28× bracket is right, but it is a statement about the **mechanism** (storage word vs log byte). It is not a statement about any one function.
*Ruling.* The thesis says: "Writing a document as event data is roughly 18–28× cheaper than storage at 1–5 kB; the lower figure applies where the EIP-7623 calldata floor binds (execution gas < 24 gas per non-zero byte), the upper where it does not." It quotes no single ratio for a named function until one measured receipt exists. **LIM-R7-08 is accepted as a gate on the lower figure only.** CA-20 discharges it by deploying a contract that emits one LOG3 with 1,024 non-zero bytes on Hardhat 2.28.6/`osaka`, then comparing `gasUsed` with 21,000 + 40,960 (floor) and 21,000 + 16,384 + 9,692 + overhead (no floor). The direction of the trade and R8's PF-58 reading are unchanged.

**RL-03 — R8 moving Sepolia rows M → I. CLOSED; the move is correct.**
*Facts checked.* `MEASUREMENT_CONDITIONS.md` defines M2 (Sepolia, chain 11155111) as a condition class (l. 26), with an AR-18 correction note (l. 29). Its only M2 numbered row is #10, status **E** ("never measured", l. 85, 157). No numbered row with status V carries a Sepolia gas figure, and R6 L0.4 PRO-15 records that `sepolia_validation.json` was never committed. R8's Rule 2 says M needs a V row, so RV-IMPL-05 and RV-MET-12 cannot be M.
*Is "I" the right label?* Yes. The script `scripts/validate_sepolia.js` and the procedure exist and have run, but no number is in the register. STD notes that "I" for an *executed-but-unrecorded* run stretches the definition ("implemented, unmeasured"). The panel accepts it with the row text "gas witness; JSON not committed".
*Path to M:* commit the JSON, add a register row with status V, restricted to execution gas under identical bytecode and fork (AR-18). Even then it evidences MD-07 only, never MD-01 or MD-12 (NC-07).

**RL-04 — R8's "aa,bb / cc" MD notation (KD-R8-02). CLOSED (adopted suite-wide), with two conditions.**
*Why it is right (MTH, TCS).* v0-1's headline let one M row on, say, MD-07 paint ● in every MD that row listed, including MD-01. The slash makes the evidence claim explicit per dimension, and `r8_coverage.py` parses it. The fall from 128 ● to 77 ● is the honest number. No measurement was lost; R8 §5 says so, and the panel agrees after re-running the script.
*Conditions.*
- (i) Every reproduction of an RV table, in a thesis appendix or in FIG-R11, carries the one-line legend from R8 §0.
- (ii) R6 §7 adopts the same convention, or states that its "M" column is per sub-layer and not per MD (Q-R8-05, PN-39). SLD-12 then cites the two artefacts as complementary, not as the same count.
**The thesis headline is 77 ● / 3 ◐ / 115 ○ / 223 · over 418 cells.** The v0-1 figure (128/83/207) is retired.

**RL-05 — R6's finding that 20 of 44 state-changing functions lack negative access-control tests (Q-R6-07). ACCEPTED as a test-evidence gap, not a code defect; it gates PF-61(a).**
*Panel recount from R6's "Neg." column:* 24 Y · 9 st (state-gating only) · 11 N = 44. So 20 rows lack a test that calls the function as a non-authorised party. The key-change table's "19 of 44" is a typo (PN-36).
The 11 N rows are SCF-EDR-04, -06, -07, -08, -12; SCF-MOBI1-01, -02, -03; SCF-MOBI2-02; SCF-CMB-03, -05. Spot-check: the only registry-authority negative in `MOBIVID/MOBIVIDRegistry.test.js` is l. 545 (`authorizeIssuer` by an outsider, which is SCF-MOBI2-01, marked Y). No outsider test for `authorizeManufacturer`, `revokeManufacturerAuthorization` or `transferRegistryAuthority` was found. That confirms the three MOBI1 N cells.
*Severity (CR).* The access check is present in source for all 20, so no security claim is weakened. What is weakened is any claim of the form "the attack matrix covers access control". #28's 43/43 is a matrix of named attacks, not coverage of the SCF register.
*Ruling.* PF-61(a) is reported as "access checks present in source for 44/44 rows; negative tests for 24/44 (55 %)". The thesis may not say "access control is fully tested". CA-19 (twenty negative tests, about one day of work) would raise it to 44/44, and is **thesis-blocking only for SLD-16's (a) component**.

**RL-06 — R7's lead figure for *P*\*(0.5). Superseded by the repository; see PN-34.**

---

## 2. New findings from the second pass

| PN | Sev | Raised by | Finding | Evidence | Required action (owner) |
|---|---|---|---|---|---|
| **PN-34** | MED | MTH, ITS | **Register row #26 changed under R7.** The row was re-stated on 2026-10-23 (WM-2 A5) from the A3b Exp. D re-run (`0b39570`): V2V warm verification is **0.156 ms/neighbour** (R² 1.0000) and *P*\* ≈ **641** by linear extrapolation. The row's last sentence says "the earlier 0.164 ms/neighbour (R² 0.9998) and *P*\* ≈ 609 are history". The "internal inconsistency" that R9 v0-1 X-13/CA-09 and R7 §4.2 describe is therefore a superseded value with a dated note, not a defect. R7's lead *P*\*(0.5) = 305 (= 50/0.164) is stale, and the correct lead is **320** (50/0.156 = 320.5). R7's statement that 641 is "the row's head and inconsistent" is also stale | `MEASUREMENT_CONDITIONS.md` #26 (fold of l. 148; last commit `cdfabe0`, 2026-10-22 20:28 −0700) | R7 v0-3: PF-43 lead → 320 (M model, #26 current); *P*\*(1) → 641; 352 stays the crypto-only ceiling (from #27); delete the CA-09 sentence. **CA-09 closed by the repository.** R8 RV-MET deepen-next line (CA-09) to be deleted. (Roots) |
| **PN-35** | MED | MTH | **Stale cross-references, because the three second passes ran in parallel.** R6 v0-2 still writes "PF-44c (value under correction)" (8×), "PF-46 reserved", "PF-63..66 requested", "PN-11 being corrected" and "≈ 28×" for PF-52. R8 v0-2 still writes "PF-44c" (5×), "PF-46 reserved" (2×), "req PF-63/64/65/66" (8×), "R7 PF-32..62" (header, §0 PF column), "PAR-37: gossip PF to be assigned", "SOL-16 (mechanism, PN-09)", and a §9 open-bound table listing four rows R7 has now bounded. RV-SCF deepen-next asks for the CEI check that R6 §4.2 has already done. None of these changes a number. All of them would mislead a reader who greps a tag | panel grep counts above | one mechanical v0-3 sweep of R6 and R8, by this table: PF-44c → **PF-45**; "PF-46 reserved" → **PF-46**; "req PF-6x"/"requested" → **PF-63/64/65/66**; R7 range → **PF-32..66**; PAR-37 "no PF (dropped)"; SOL-16 → "SOL-16 (realises SOL-05)"; R8 §9 shrinks to the IDTX gas, relay-overhead and "qual." rows; R6 PF-52 → "18–28× by basis" (Roots) |
| **PN-36** | LOW | MTH | Q-R6-07 is stated as "19 of 44" (R6 key-change table) and as "20" (§2.L5.2, HANDOFF). The panel recount is 20 | R6 l. 32 vs l. 585 | correct to 20 (11 none + 9 state-gating only) |
| **PN-37** | MED | CR, DS | **The EIP-7623 floor condition is unstated.** R7 §5.4 presents 17.7× as "independent of size", which holds only for a bare log. Whether the floor binds depends on execution gas per calldata byte (RL-02) | EIP-7623 floor arithmetic; ERC-1056 `setAttribute` writes `changed[identity]` | R7 v0-3 adds the binding condition (execution gas < 24 × non-zero bytes) and the first-write / later-write split |
| **PN-38** | LOW | MTH | R7's KD range is "KD-R7-01..07 (07 merged)" in the header and §0, but "KD-R7-01..06 (07 retired)" in §13 and §14. R6 §0.2 says the defect log runs "D1–D66", but the log ends at **D65** (panel grep: no D66) | R7 l. 12, 28, 685, 700; `DEFECT_LOG.md` | write "KD-R7-01..06 issued; KD-R7-07 retired by merge"; R6 "D1–D65" |
| **PN-39** | LOW | MTH | **Two measured-vs-designed artefacts with different granularity.** R6 §7 is per sub-layer and pools every MD. R8 §5 is per category × MD under the slash rule. Both feed SLD-12, so without a stated relation an examiner will see two "measured" counts | R6 §7; R8 §5; Q-R8-05 | R6 v0-3 adds one sentence: "§7 lists *what* was measured per sub-layer; the per-dimension evidence count is R8 §5 (77 ● of 418)" |

No new HIGH finding. PN-34 is the only one that changes a number the thesis would print.

---

## 3. Cross-document consistency after re-keying

The panel grepped each v0-2 document for every namespace and checked the owner rule from R9 v0-1 §3.1/§3.2.

| Namespace | Owner | State in v0-2 | Verdict |
|---|---|---|---|
| **Q-R6-01..07** | R6 | R6 issues 01..07 (07 new, 06 closed). R8 cites Q-R6-02/04; R7 cites none | consistent |
| **Q-R7-01..08** | R7 | unchanged; R6 and R8 cite Q-R7-03/04/07/08 correctly | consistent |
| **Q-R8-01..05** | R8 | 01..04 re-keyed; 05 new (slash notation in R6 §7). The only remaining "Q-R7 (R8)" is the struck-through retirement line | consistent |
| **Q-R9-01..04** | R9 | answered here: Q-R9-01 → RL-01; Q-R9-02 → §5 step 11; Q-R9-03 → yes, appendix "H" (SLD-13); Q-R9-04 → the Roots thread runs the blind re-derivation in a fresh session (SLD-10) | closed by this document |
| **KD-R6-01, -03, -04** | R6 | 02 → KD-R7-02, 05 → KD-R6-01, as planned | consistent |
| **KD-R7-01..06** | R7 | 07 merged into 02; the range is stated two ways | PN-38 |
| **KD-R8-01..06** | R8 | new in v0-2; no collision | consistent |
| **CEV-R7-01/02, LIM-R7-01..08** | R7 | new | consistent |
| **PAR-01..43** | R8 (sole) | R7 §8 declares none and cites R8 numbers in every row; R6 cites PAR-06 | consistent, except PAR-37's stale "PF to be assigned" (PN-35) |
| **PF-32..66** | R7 | R7 assigns 32..66, with 45/46 filled and 63..66 new; script self-check PASS over 54 document tags. R6 and R8 still use retired "PF-44c" and "requested" wording | **inconsistent in R6/R8 wording only** (PN-35) |
| **SOL-10..17** | R6 | R6: SOL-10, 11, 13, 14, 16 are SOLs; 12, 15, 17 are "mechanism", numbers reserved. R7 cites SOL-11 only. R8 cites SOL-12 and SOL-17 as mechanisms (matches) and **SOL-16 as mechanism (does not match)** | PN-35 / RL-01 |
| **PRO-23..25** | R6 | R8 RV-PROT-01/10/11 cite PRO-25/23 with "(was PRO-13x/z)" | consistent |
| **RV-, MD-01..22** | R8 | 311 rows, unique (script) | consistent |
| **PN-, SLD-, DRP-, NC-, CA-, PRM-, B-** | R9 | cited, never redefined, by R6/R7/R8 | consistent |
| **⟦⟧ placeholders** | — | R8: **0** (script). R6: 25 occurrences, all in struck-through retirement entries, the §8 heading or change-log text, none in use. R7: 7 occurrences, all quoting R6's retired PF-⟦n⟧ names in change tables | **no placeholder in use** |

**Remaining inconsistencies (complete list):** PN-34 (#26 lead value), PN-35 (stale R6/R8 wording; ten substitution patterns), PN-36 (19 vs 20), PN-38 (KD range; D65), PN-39 (two coverage artefacts). All are mechanical. None needs a further panel pass. The Roots thread can apply them as R6 v0-3 and R8 v0-3, with R7 v0-3 for PN-34/37/38, and record the result in the Phase 2 README.

---

## 4. FINAL "What to solidify for the thesis"

**Rule for the chapters.** A locked statement enters the thesis in the words below, or tighter. It is cited by its tag (SLD-nn, plus the PF/register row it stands on), and the numbers are never restated in new words. "Pre-citation condition" is what must be true before the sentence is pasted into a chapter. Thesis locations follow the section headings in `docs/thesis/` (ch5 §5.1 Experimental Setup … §5.10 RQ5; ch6 §6.1 … §6.8). Chapters 1, 3, 4 and 7 cite their READMEs' structure. "Appendix H" is new (RL ruling on Q-R9-03).

### 4.1 Locked statements

| SLD | v0-1 → final | Locked statement (as it should appear) | Thesis location | Evidence status | Pre-citation condition | Owner |
|---|---|---|---|---|---|---|
| **SLD-01** | kept | "All on-chain results were produced on Hardhat 2.28.6 with automine (one validator, chain 31337, block gas limit 60 M, hardfork `osaka`, no block interval). Gas is portable to any EVM network for identical bytecode, state and fork; measured latency is client plus RPC plus execution and is not a time to confirm." | ch1 scope; ch3 experimental platform; **ch5 §5.1**, **§5.8**; ch6 §6.6.3 | M (config, `meta.json`) + Dv (PF-39) | none | Roots |
| **SLD-02** | kept (revised) | "Cost is a per-function vector: for each standard and catalogue operation we report execution gas with its GAS_CHARTER class (register #29, #34, #50, #54); operations per block and per second are derived at G ∈ {30, 60, 100} M and Δ as declared parameters (PF-49)." | **ch5 §5.2**, §5.9; Appendix A | M (gas) / Dv (capacity) | Cost thread confirms that each table cites one register row and one run id (PN-21) | Cost · Scale |
| **SLD-03** | kept (revised value) | "On the cached path the vehicle's verifier and the channel, not the ledger, bind first. Measured software verification on a server-class host is linear at 0.156 ms per neighbour (#26), so at half the 100 ms interval it supports about 320 neighbours (crypto-only ceiling 352 from #27). Estimated automotive classes support 200 (security ASIC), 50 (application processor) and 10 (MCU HSM) neighbours. The ledger is not the bottleneck whenever the state re-check period satisfies k_f ≥ r_BSM·P·t_chain/f_id (27.9 at P = 100)." | **ch6 §6.3**; ch5 §5.4 (measured software row only) | M (sw, #26/#27) / E (hw) / Dv (PF-43) | R7 v0-3 applies PN-34 (lead 320); hardware rows labelled E until Q-R7-02 sources them (LIM-R7-03) | Latency |
| **SLD-04** | kept | "The repository's messages are research JSON: 596 B (DID-carrying) and 1,110 B (PEM-carrying) (#23). On a 10 MHz 802.11p channel at CBR 0.6 they fit about 63 and 37 vehicles, against about 182 for a digest-signed 1609.2-style BSM, i.e. 2.9× to 5.0× the airtime. The encoding is not deployable at density." | ch5 §5.4 (as a consequence of #23); **ch6 §6.3**; ch7 limitations | M (size) / Dv (airtime) / E (PHY and 1609.2 overheads) | LIM-R7-02 and LIM-R7-07 sourced, or every overhead labelled "E, 1609.2-style" | Latency |
| **SLD-05** | kept (wording tightened) | "The repository bounds identity-state staleness in messages, not seconds: a verifier accepts at most k_f − 1 further messages on stale state (#32, #46). In time, the bound is (k_f − 1)/r_s only for a sender at known constant rate, and it is unbounded for a quiet sender, because the state cache has no TTL. The optimal re-check period under a staleness budget σ_max is k_f* = ⌊r_s·σ_max⌋ + 1; the measured knee k ≈ 90 corresponds to about 8.9 s of revoked-key acceptance at 10 Hz." | ch5 §5.4 and crux C4; **ch6 §6.3**; ch3 method ("messages, not seconds") | M (#32, #37, #46) / Dv (PF-54/55) | either CA-07 (TTL) is implemented and measured, or the "unbounded for a quiet sender" clause stays verbatim. Message freshness (`freshness.py`) is cited separately, never as this bound | Latency + code |
| **SLD-06** | kept (status explicit) | "Across the nine signature-verifying contracts the repository uses three schemes (raw-digest ecrecover, EIP-191-prefixed ecrecover, OpenZeppelin ECDSA). Only `attestEvent` and the ERC-4337 EntryPoint bind the chain id. ERC-1056 signed operations bind the registry address and nonce but not the chain id, so they are replayable across chains where the same deployer created the registry at the same nonce, which is the default in this repository (D52). A zero signature seizes DID 0x0 (D53). Low-s is enforced in two contracts." | **ch5 §5.6**; ch4 honesty caveats; Appendix B | **I** (source-read) → M after CA-02 | author decision B-02 recorded (fix vs documented G3 narrowing); the sentence says "source-read" until CA-02 runs | Security campaign G-C1 |
| **SLD-07** | kept (merged with RF result) | "Pseudonymity fails at two layers by construction. On chain, pseudonyms held as ERC-1056 delegates of one DID are fully linkable: one `eth_getLogs` links 60 of 60 (#38). On the radio, a pseudonym change that does not force sidelink resource reselection is linkable with probability about 0.14–0.80 one second later, depending on P_keep (PF-45); MAC loss at CBR 0.6 is roughly 15–46 % per neighbour (PF-46)." | **ch5 §5.6**, crux C7; ch6 privacy discussion; ch7 limitations | M (#38) / Dv (PF-45, PF-46, E inputs) | Q-R6-04 + Q-R8-04 answered (§5 step 11). The RF clause stays Dv until CA-22 (SPS counter) runs | G-C1 · Latency (radio) |
| **SLD-08** | kept | "Every non-ZK VIN path in the repository is enumerable: the testbed address is an unsalted SHA-256 of the VIN (D64); ERC-1155 and LSP8 token identifiers are unsalted keccak(VIN); `getVINFromDID`, `getVehicleVIN` and `getVINFromTokenId` return the VIN in plaintext. A serial-unknown VIN hash is reversed in 3.58 s (#60). The ZK-VIN commitment is the only hiding path." | **ch5 §5.6**, **§5.10.3**; ch6 (GDPR/EDPB commitment form); ch2 motivation only | M (#60) / I (getters, source-read) | CA-10 inventory merged into D64; STD wording checked against the EDPB guidelines on blockchain (fetched through the Accuracy Ledger) | G-MV1 · G-C1 |
| **SLD-09** | kept | "On-chain Groth16 verification costs 181,000 + 6,150·n_pub + calldata gas, a model within 1.3 % of the measured 256,038 (#58); proving takes 398.6 ms median (#57). The trusted setup is single-party and insecure, so no production soundness is claimed." | **ch5 §5.10.1–5.10.2**; ch4; ch7 limitations | M / Dv (PF-51) | setup caveat in the same sentence (non-negotiable); CA-06 logged | G-C1 · G-RIM |
| **SLD-10** | kept (gated) | "Identity binding is bounded by a union over failure events: ε_Σ + ε_H (computational, ≈ 2⁻¹²⁸ each) + ε_L (a governance prior on ledger equivocation) + ε_R (an implementation prior on the resolver) + the revocation window. At four validators the ledger term exceeds the cryptographic terms by about 37 orders of magnitude; on the executed system it equals trust in one operator. With a single client, a common-mode term dominates once the collusion tail falls below it (PF-65)." | ch3 security argument framing, or **ch6 §6.1** | Dv (PF-36, PF-65; E inputs) | **blind re-derivation in a fresh session agrees** (Q-R9-04: Roots thread); LIM-R7-01 for SR names | Roots |
| **SLD-11** | kept | "The repository measures Families A–C and a Family F precursor; it adds four artefacts outside the option list (LSP8, CVIN-Combined, the MOBI VID profile, ZK-VIN/IDTX); it executes nothing from Families D or E." | ch2 §2.2 opening; ch3 option mapping | I (source-read; mapping per R2 §3.3) | Terminology Freeze re-read through the Project (Q-R6-01) | Roots · G-RIM |
| **SLD-12** | kept (count replaced) | "The measured-versus-designed table (one row per sub-layer) lists what was executed. Per dimension, 77 of 418 category × dimension cells are evidenced by measurement, 3 by derivation only, 115 are targeted by design and 223 are empty. Time to confirm, decentralisation, trilemma position, availability, auditability, regulatory posture, recoverability and ordering races have no measured cell, because one node mines." | ch1 scope and honesty; **ch5 §5.8**; Appendix E | M (as an inventory; `r8_coverage.py`) | PN-39 sentence in R6 §7; FIG-R11 regenerated (CA-24); legend per RL-04 | Roots · G-RIM |
| **SLD-13** | kept | "Consensus bounds (QBFT quorums, per-round messages, time to confirm with round changes and its tail) are design-only and appear in Appendix H; no executed trace exists." | **Appendix H (new)**; one ch6 paragraph; ch7 future work | Dv / Ds (PF-37, 38, 40, 57) | each caption carries "DESIGN — no executed trace" | Scale |
| **SLD-14** | kept | "Revocation latency over an intermittent backhaul is stated as tail quantiles, not availability: at 99 % availability with 10-minute outages the mean is 14.5 s but the 99.9th percentile is about 23 minutes (PF-48, design model)." | ch6 revocation discussion; ch7 future work | Dv / Ds | label DESIGN; the "< 3 %" MC agreement is quoted with its value (1.34 %) | Latency |
| **SLD-15** | kept | "The basic identity set used for every comparison is the frozen `PRIMITIVES_LOCK v1.0` (IMinimalSSI functions with IMS-F numbers and semantics per PRM tag)." | ch3 identical operation set; ch4 | I (source-read) / M (#53, #54) | §5 checklist complete; canon F1–F12 fetched (B-01) | primitives chat · G-RIM |
| **SLD-16** | kept (components fixed) | "Contract security vector over 117 register functions: (a) access checks present in source for 44/44 checked state-changing rows, negative tests for 24/44; (b) replay protection: chain-bound in 2 of 9 signature-verifying contracts; (c) IDTX gate mutants 5/5 killed; (d) 43/43 named attacks defended (#28); (e) no external audit; CEI holds on the four external-call surfaces (source-read)." | **ch5 §5.6**; Appendix B | M (c, d) / I (a, b, CEI) | CA-19 if (a) is to read 44/44; (b) tabulated as stated; "no external audit" verbatim | G-C1 |
| **SLD-17** | **new** | "ERC-1056 writes are cheap because the DID document lives in event logs: storing a document is about 18–28× dearer than logging it at 1–5 kB, depending on whether the EIP-7623 calldata floor binds. The saving is paid on reads, which grow with history (112 RPC calls / 87 KB at history 50, #31)." | ch5 §5.9; **ch6 §6.1** (frontier) | S / Dv (PF-52) + M (#31, #49) | RL-02 wording; CA-20 for any single-function ratio | Cost |
| **SLD-18** | **new** | "The repository contributes five solutions: identity-dependent transactions with caller-independent predicates (SOL-10, implemented, unmeasured), the ZK-VIN commitment and gate (SOL-11), the MOBI VID registries (SOL-13), the Steward agent (SOL-14), and cached-read verification as the measured realisation of HAA-1's read rule (SOL-05/16). Other hardened components are mechanisms." | ch1 contributions; ch6 §6.8 (SOL-10) | mixed, stated per item | RL-01 conditions; SOL-10 quoted as I with no number (DRP-05) | Roots |

**Merged or retired.** No v0-1 SLD is dropped. SLD-07 absorbs the PF-46 loss figure. SLD-10 absorbs PF-65. SLD-12's count is replaced. The two additions (SLD-17, SLD-18) close gaps that v0-1 left in ch6 §6.1 and in the contribution list.

### 4.2 Final DROP / DEMOTE (DRP)

| DRP | Item | Action |
|---|---|---|
| DRP-01 | Any Besu/QBFT/Sepolia latency or finality as a result | Appendix H, DESIGN |
| DRP-02 | Fleet "two orders above any row" (R4) and PF-50 as claims | one ch6 sentence: "on-chain per-pseudonym anchoring fails on privacy before capacity" |
| DRP-03 | *P*\* ≈ 641 (and the retired 609) as "capacity" | "linear extrapolation beyond the tested *P* ≤ 80" only |
| DRP-04 | "IEEE 1609.2 baseline" | rename "X.509 P-256 pseudonym-certificate baseline (1609.2-style)" (KD-R6-03) |
| DRP-05 | IDTX gas or latency | drop until E-F1-1 runs; IDTX = definition + mechanism + status I |
| DRP-06 | "SUMO with 50 vehicles" | drop (#15 E) |
| DRP-07 | RNG seeding/fleet tables (PF-41/42) | one ch6 sentence on hardware preconditions |
| DRP-08 | Pre-EIP-1108 703,500 gas comparison | dropped (done in R7 v0-2) |
| DRP-09 | SOL-12, SOL-15, SOL-17 as solutions | mechanisms (cite ALG/IMP); SOL-16 kept under RL-01 |
| DRP-10 | Licence-endorsement chain as the illustrative chain | replaced by the revocation chain (R8 §4.1) |
| **DRP-11** (new) | v0-1 coverage headline 128 ● / 83 ○ / 207 · | retired; use 77 / 3 / 115 / 223 |
| **DRP-12** (new) | *P*\*(0.5) = 305 and "0.164 ms/neighbour" | retired by #26's re-statement; use 320 and 0.156 (PN-34) |

### 4.3 Final DO-NOT-CLAIM (NC)

| NC | Do not claim |
|---|---|
| NC-01 | any time to finality, consensus latency, decentralisation level or Nakamoto coefficient of the executed system other than "*N_v* = 1" |
| NC-02 | that the freshness window resists clock manipulation; it inherits GNSS integrity |
| NC-03 | that ERC-1056 delegate pseudonyms are unlinkable |
| NC-04 | production soundness of any ZK-VIN admission |
| NC-05 | any HSM, ECU or OBU figure as measured |
| NC-06 | that did:ethr resolution resists a lying RPC endpoint (fails closed on errors, not lies; PF-64) |
| NC-07 | any Sepolia latency; Sepolia gas only after a V row exists (RL-03) |
| NC-08 | that salted `vinHash` + AES-GCM hides the VIN in the repository's realisation (D64) |
| NC-09 | cross-chain replay protection for ERC-1056 signed operations (D52) |
| NC-10 | that the repository's messages are deployable on a 10 MHz channel at density |
| **NC-11** (new) | that access control is "fully tested" (24/44 negative tests; RL-05) |
| **NC-12** (new) | a single storage-vs-log ratio for a named function without a measured receipt (RL-02) |
| **NC-13** (new) | that state revocation is bounded in seconds, unless a TTL is implemented and measured (SLD-05) |

**Panel record.** DS/ITS vs MTH/CR on SLD-13 is resolved as in v0-1 (appendix plus one ch6 paragraph). TCS's gate on SLD-10 stands. STD asks that SLD-08's EDPB sentence be the last one fetched before submission, because the guidance is the most likely of all cited sources to have moved.

---

## 5. DID / DID-system primitives lock checklist (final)

*What this does for the level above:* SLD-15 and every "identical operation set" comparison rest on it. *What it trusts from below:* L1 primitives and L5.2 registry state, as read in R6 §2.L5.2. It merges R9 v0-1 §6 with R8 v0-2 §7. Work through it in order in the parallel primitives chat. Each step names its blocking question, the panel's **recommended answer**, the evidence to cite, and the PRM/RV rows it locks. Tick a step when the author records the answer. Step 14 freezes `PRIMITIVES_LOCK v1.0`.

| ☐ | Step | Blocking question | Recommended answer | Evidence to cite | Locks |
|---|---|---|---|---|---|
| ☐ | 1 | **B-01** F-number order inside Sets A/B; prose collision with F-R1..4 | fetch canon F1–F12 signatures from `cvin-sandbox-v1.3`; adopt the canon order unchanged; write "IMS-F*n*" in prose | `BASIC_ID_SET_EXTENSION.md` l. 10, 20–21 ([B1]) | PRM-L6.3-01; RV-IDTX-01..14 names |
| ☐ | 2 | **B-04** Is D2 revokeAttribute a Set A op, and is D1 revokeDelegate folded into it? | yes and no: keep D1 and D2 as separate Set A members, and report admission as 11/11 or 10/11 per substrate exactly as #53 measured. Do not fold to raise a count | #53 (wrapper and ERC-721 fail only D2) | PRM-L5.2-04/05; RV-IDTX-06/07/09 |
| ☐ | 3 | **B-15** X1 `execute` in Set A? | yes, with the rule "a real executor is required": counts only for ERC-725xy and ERC-4337; ERC-725 basic records "stub (D23)" | #54; D23 | PRM-L6.3-02; RV-IDTX-14, RV-SCF-43/44 |
| ☐ | 4 | **B-02** D52 chain-id binding: fix or document | **document**, keeping upstream bytecode for O1 fidelity: narrowed G3 sentence in ch5 §5.6, SLD-06 and NC-09; run CA-02 so the narrowing is reproduced, not asserted. A chain-bound variant can be a separately named contract later | `EthereumDIDRegistry.sol` l. 160–172; DEFECT_LOG l. 154 ("author decision") | PRM-L5.2-03; RV-THR-11 |
| ☐ | 5 | **B-07** `changeOwner(0)` (D26) and zero signer (D53) | reject both: `newOwner != 0` and `signer != 0` (CA-03, CA-15) in the repo's own contracts. For upstream EDR, document D53 alongside D52 | D26 l. 54; D53 l. 155 | PRM-L5.2-03; RV-SIG-03, RV-THR-12 |
| ☐ | 6 | **B-03** one signature scheme for claims and attestations | **EIP-712 with a domain that includes chainId and verifyingContract**, using OZ ECDSA (low-s, non-zero). MOBI2's `attestEvent` is the in-repo model | D25c; R6 register summary | PRM-L1.1-01; RV-SIG-01/02 |
| ☐ | 7 | **B-05** salted VIN commitment everywhere | salt ≥ 128 bits, generated in the owner's wallet and held by the owner (Steward vault where present). The did:mobi identifier is derived from the *salted* hash. Unsalted keccak(VIN) token ids are retired | D64; #60; PF-33/34 | PRM-L1.1-03, PRM-L6.1-03; RV-PRIM-04, RV-READ-10 |
| ☐ | 8 | **B-06** canonical createDID for cost tables | report **both**: implicit (0 gas, #47) as did:ethr's createDID, and explicit `registerVehicle` (54,868, #22) as the vehicle-profile createDID, never pooled | #22, #47 | PRM-L5.2-02; RV-IDTX-01 |
| ☐ | 9 | **B-10** deactivation in the minimal set | yes, as a Set A member with semantics "terminal; history walk preserved (`previousChange`)". Pure EDR records "absent" | SCF-VPR-07; D21 fixed | PRM-L5.2-06; RV-IDTX-04 |
| ☐ | 10 | **B-08** BSM digest; **B-16** TTL | keep SHA-256 for BSMs (no on-chain check consumes them; KD-R6-04) and say so. Add TTL: state refresh = min(*k_f* messages, *T_ttl*) (CA-07) | `sign_message`; PF-54/55 | PRM-L1.1-02, PRM-L7.2-01/02; RV-ALG-09/10, RV-READ-14 |
| ☐ | 11 | **Q-R6-04 + Q-R8-04 (Q-R9-02)** is 1609.2-style pseudonymity in scope? | **out of scope as an implementation, in scope as a stated requirement.** Retire the M5 on-chain pool as a design (CA-11), keep #38 as a negative result, and cite 1609.2 butterfly keys as the reference design (RV-SIG-12 Ds) | #38; PF-45 | RV-SCN-12, RV-THR-14 |
| ☐ | 12 | **B-11** CAIP-10; **B-13** cryptosuite; **B-14** status anchoring | B-11 recorded as conformant (D27 fixed). B-13: keep the thesis-defined suite as a *declared deviation*, with no W3C conformance claim beyond #4/#24. B-14: status is off-chain (memory/JSON), so revocation claims cite #46 (on-chain revoke), not the VC status file | D27; `vc_issuer.py` l. 12–14; IMP-L2.3-01 | PRM-L6.1-01, PRM-L6.2-01/02 |
| ☐ | 13 | **B-09** setup; **B-12** lying endpoint | both are stated assumptions: "single-party setup, research only" (NC-04) and "the RPC endpoint is trusted; proof-carrying reads are future work" (NC-06, PF-64) | #57; BP-L0.4-02 | PRM-L1.1-04, PRM-L6.1-02 |
| ☐ | 14 | freeze | lock the two no-blocker rows first (PRM-L6.2-03 createPresentation, PRM-L6.3-03 IDTX dependency kinds), then write `PRIMITIVES_LOCK v1.0`. From then on, chapters cite PRM tags or IMS-F numbers only | R8 §7 | SLD-15 |

Steps 1, 2, 4 and 7 unblock the most rows (R8 §7). Steps 4–7 also fix the security sentences of SLD-06 and SLD-08.

---

## 6. Code actions for the repository (final; defect log / WM-2)

Repository files are not edited here. **TB** = thesis-blocking: a locked SLD cannot be cited as worded until the action is done (or its "stated absence" alternative is written).

| CA | D | Action | Sev | Status @ 2026-10-23 | TB? |
|---|---|---|---|---|---|
| CA-01 | **D52** | record the author decision (recommended: document, keep upstream; §5 step 4) | M | open (decision) | **TB** for SLD-06 wording |
| CA-02 | (new test) | two-chain replay of `*Signed` ops: deploy EDR on 31337 and on a 1337 node from the default deployer, replay one `changeOwnerSigned` | M | open | no (SLD-06 stays I without it); **Phase 3** |
| CA-03 | **D53** | `signer != address(0)` in raw-ecrecover paths of repo contracts (CMB `addClaim`); document for upstream EDR | L | open | no |
| CA-04 | **D22 rest, D25c** | one scheme (EIP-712 + chainId) and low-s guard in CMB and 4337 account | M | open | no |
| CA-05 | **D15** | guardian recovery: time-lock/threshold; clear the guardian on recovery | M | open | no |
| CA-06 | (new) | log the single-party Groth16 setup as a deployment-blocking defect (next free number, **D66**) | M | open | no (SLD-09 caveat suffices) |
| CA-07 | (new, **D67**) | `ERC1056Provider` state cache: `min(k, T_ttl)`, plus one measurement of staleness in seconds | M | open | **TB** for SLD-05 unless the "unbounded for a quiet sender" clause is kept |
| CA-08 | (new, **D68**) | `freshness.py` l. 47 docstring: "about 650 senders" → "5,958 (596 with a margin of ten)" | L | **open (verified: text unchanged)** | no |
| CA-09 | (register) | #26 consistency | L | **closed by the repository** (WM-2 A5 re-statement, 2026-10-23; PN-34) | — |
| CA-10 | **D64 (extend)** | VIN exposure inventory: unsalted token ids (ERC-1155 `vinHashOf`, LSP8 `tokenIdForVIN`), plaintext getters (CVDR, 725xy, 721) | M | open | **TB** for SLD-08 |
| CA-11 | (new, **D69**) | record the M5 on-chain pseudonym pool as a design defect with the off-chain alternative | M | open | **TB** for SLD-07 (after §5 step 11) |
| CA-12 | (new) | `ZkVinGate` static per-service challenge | L | open | no |
| CA-13 | (new) | `SchnorrEcrecoverVerifier.prove` no replay guard | L | open | no |
| CA-14 | **D51/D63** | probe path expiry vs last-learned chain time + 900 s | L | D63 documented | no |
| CA-15 | **D26** | `changeOwner(id, 0)`: reject (§5 step 5) | M | open | no |
| CA-16 | **D16 rest** | emit an event on `transferRegistryAuthority`; multisig/time-lock note (PF-66) | L | open | no |
| CA-17 | (audit) | CEI review of four external-call surfaces | L | **closed** (R6 §4.2, source-read, I; `payToll` verified by the panel) | — |
| CA-18 | (hygiene) | refuse SHA-256(vehicle_id) keys outside a test chain id; bind 8545 to loopback in compose | L | open | no |
| **CA-19** | (new, tests) | twenty negative access-control tests (11 N + 9 st rows, RL-05) | L | open | **TB** only for SLD-16(a) "44/44" |
| **CA-20** | (new, measurement) | one LOG3 1 kB receipt on Hardhat 2.28.6/`osaka` to confirm or refute the EIP-7623 floor (LIM-R7-08) | L | open | no (RL-02 bracket wording suffices); **Phase 3** |
| **CA-21** | (Roots doc) | `docs/roots/phase1/PHASE1_ERRATUM_v1-0.md`: X-1..X-9 at source (R4 PF-24/25/28 → DESIGN; SOL-01 lineage; 1609.2 naming) | M | open (PN-33) | **TB** for any chapter citing R4 PF-24/25/28 |
| **CA-22** | (enhancement) | SPS reselection counter and *P_keep* in `cv2x_stack.py` (Q-R7-04), so PF-45 can be measured | M | open | no (SLD-07 RF clause stays Dv); **Phase 3** |
| **CA-23** | (evidence) | commit `sepolia_validation.json` and add a V row for execution gas, or drop RV-IMPL-05 (RL-03) | L | open | no |
| **CA-24** | (figures) | regenerate FIG-R11 from `r8_coverage.py` (four cell codes, legend) | L | **in progress**: `figures/FIG-R11_coverage_matrix_v0-2.svg` appeared (untracked) during this pass, not yet checked against 77/3/115/223 | **TB** for SLD-12's figure |

D-numbers D66–D69 are *suggested* next free numbers (the log ends at D65). The defect-log owner assigns the final numbers. Further enhancements, not defects: RSU propagation delay in I3 (Q-R7-05); E-F1-1 IDTX gas (Q-R7-03); a second client for MD-02.

**Thesis-blocking set:** CA-01, CA-07, CA-10, CA-11, CA-21, CA-24, plus CA-19 for one component of SLD-16. All except CA-07 are documents or decisions, not code.

---

## 7. HANDOFF (R9 v0-2, ≤ 400 words)

**Files.** `docs/roots/phase2/90_R9_panel_review/claude_CVIN_SC_Roots_Panel_Review_R9_v0-2.md` (this). Nothing else written. `r7_calc_v0-2.py` (self-check PASS) and `r8_coverage.py` (311 rows, 0 placeholders, 77/3/115/223) were executed read-only.

**What Phase 2 now claims.** (1) Every on-chain result is single-node Hardhat automine: gas is portable, latency is not time to confirm (SLD-01). (2) On the vehicle path, verification hardware and airtime bind before the ledger: 320 neighbours in server software, 10 on an MCU HSM, and JSON messages at 2.9–5.0× a 1609.2-style BSM's airtime (SLD-03/04). (3) Staleness is bounded in messages, not seconds (SLD-05). (4) Replay scope, pseudonym linkability and VIN enumerability are honest negative results (SLD-06/07/08). (5) The contribution list is five solutions (SLD-18). Dispositions: 26 closed, 4 partly closed, 1 open, 2 disputed-accepted, 0 rejected. Six new findings (PN-34..39), none HIGH.

**Left for Phase 3.**
- A multi-node Besu/QBFT run with a committed genesis (≥ 4 validators, round-change injection), which would fill MD-01, MD-02, MD-03 and MD-10 (Q-R7-01, Q-R8-02): **Scale thread**.
- One measured LOG3 receipt for LIM-R7-08 (CA-20): **Cost thread**.
- The two-chain D52 replay test (CA-02): **Security campaign G-C1**.
- Twenty negative access-control tests (CA-19): **G-C1**.
- SPS reselection counter (CA-22) and TTL measurement (CA-07): **Latency thread**.
- E-F1-1 IDTX gas: **IDTX chats**.
- Sepolia V row or drop (CA-23): **Scale**.
- Primary sources for LIM-R7-01..08 and HSM *t_ver*: **Accuracy Ledger / Latency**.
- Blind re-derivation of PF-36 (SLD-10): **Roots, fresh session**.

**Who picks up what now.**
- Roots: R6/R8 v0-3 sweep (PN-35, 36, 39), R7 v0-3 (PN-34, 37, 38), Phase 1 erratum (CA-21), Phase 2 README.
- Primitives chat: §5 checklist → `PRIMITIVES_LOCK v1.0`.
- G-MV1: CA-10, CA-11.
- G-RIM: SLD-11/12/15 placement and FIG-R11 (CA-24).
- Defect-log owner: CA-06/07/08/11 numbering.

**Retired here.** v0-1 coverage headline; *P*\*(0.5) = 305; CA-09 and CA-17 (closed); X-13 (resolved by the repository).
