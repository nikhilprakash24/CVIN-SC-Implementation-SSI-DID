# FINDINGS (running log of measured deviations and insights)
1. O1 createDID ≈162–179K gas vs spec <100K target — explicit-DID storage vs pure
   event-sourcing; interface uniformity has measurable cost on the lightest standard.
2. Spec erratum: `CredentialRevoked` declared as both error and event (collision);
   event renamed CredentialRevokedEvent. For formal spec v1.1.
3. "Family E" label collision between v2-0 addendum (E1/E2/E3 SSI) and
   building-paths doc (agentic protocols). Build repo uses v2-0 meaning;
   agentic layer = "Agentic Frontier". Thesis-consistency item.

## VID layer pass (2026-10-04, operator-directed; traces vid_minimal_O1_ERC1056_1791157391842, vid_lifecycle_O1_ERC1056_1791157402169)
4. **F-VID-1 — the minimal interface proves status, not content binding.** `verifyCredential` (F6)
   returns (valid, issuer, revoked, expired) but not the anchored hash, and O1 exposes no getter.
   A verifier holding the off-chain credential cannot ask the chain "is *this* content what was
   anchored under this credentialId" through IMinimalSSI alone. The VID layer closes the gap two
   ways, both beside the interface: the issuer's off-chain signature over the typed anchor
   (zero gas), or TypedCredentialRegistry.declare (T1, 150,463 gas measured). Spec v1.1 candidate:
   either return the hash from F6 or state that content binding is an off-chain obligation.
5. **F-VID-2 — F6 ties credential validity to issuer liveness.** After the OEM plant DID is
   deactivated (F4), its VID birth-certificate anchor reports valid=false although the
   endorsement record still reads true. Correct for licences; wrong for immutable birth
   certificates whose issuer may legitimately cease to exist. Needs an archival-issuer policy
   (issue from a long-lived OEM root, or verifier policy "valid at issuance"). Design item, not a bug.
6. **F-VID-3 — stale-cache acceptance is real and measurable.** After F7 revoked the registration,
   the off-chain verifier with an unrefreshed cache still returned ok=true (trace seq 50) until the
   F6 refresh (seq 51). The staleness window is the security parameter of every cached read path.
7. **F-VID-4 — endorsement is the most expensive governance write.** endorseIssuer (G2) measured
   151,437–182,800 gas (higher when the endorser is non-root, because the chain walk runs in the
   write); registerIssuer (G1) 76,800–76,812; revokeEndorsement (G3) 55,597; addRoot 47,604.
   These are per-issuer-per-type, not per-credential, so they amortise; isEndorsed (G4) is a view.
8. **F-VID-5 — Merkle batching measured at 11:1.** Eleven lifecycle events anchored individually
   cost 1,431,745 gas (4×130,151 + 7×130,163); one Merkle-root anchor over the same eleven cost
   130,151. Price: per-event on-chain revocation and per-event F6 status are lost for batched events.
9. **F-VID-6 — expiry costs a storage slot.** F5 with non-zero validUntil measured 150,087–150,099
   vs 130,151–130,163 with validUntil=0 (≈19.9K, one SSTORE-class difference).
10. **F-VID-7 — F5 is issuer-agnostic.** An unendorsed owner anchored a MAINTENANCE event and F6
    reported valid=true; only the endorsement read (G4) distinguishes it. Entitlement is not in the
    twelve functions — the empirical case for the governance extension.

## Slice 1 pass (2026-10-14; traces batch_anchor_O1_ERC1056_1792035482337, delayed_write_O1_ERC1056_1792035487512)
11. **F-VID-8 — a dedicated batch anchor is cheaper than a root through F5 and buys on-chain inclusion.**
    BatchAnchorRegistry.anchorBatch measured 122,127–122,139 gas against 130,151–130,163 for the same
    root pushed through F5 (≈6% less), while adding what F5 cannot give: a gas-free on-chain inclusion
    check (4-hash, 128-byte proof for 11 leaves) and batch-level revocation (55,267). Eleven per-leaf
    F5 anchors: 1,431,769 → ratios A/B 11.00, A/C 11.72. Per-leaf revocation remains unavailable in
    both batched patterns; that is the fixed price of batching, not of the contract.
12. **F-VID-9 — delayed write reconciles correctly with "revocation wins", with zero writes during the outage.**
    Three events queued across READ_ONLY and PARTITIONED modes; the DMV revoked the registration during
    the partition; on reconnect the dependent toll-pass event was rejected and the two telemetry events
    anchored in one write (122,127). The stale-acceptance window (F-VID-3) is reproduced at seq 19.
    The reconciliation rule is a policy; what the trace shows is that the rule is implementable from
    the twelve functions plus a batch anchor, and that the gate admitted a vehicle on cached state
    whose settlement was later denied — the dispute path the design must carry (doc 06 §3).
13. **F-VID-10 — ungated reputation is worse than no reputation (S16, trace fl_round_O1_ERC1056_1792035691983).**
    Toy federated round, 6 honest clients (≈80) and 4 Sybils (20). Unweighted mean error ≈23.7–24.4.
    GATED harness (only an endorsed REPUTATION_ATTESTER may score): Sybils' mutual scores revert
    (NotEntitled), Sybils carry floor weight 0.05, weighted error 1.87. UNGATED harness: 12 mutual
    collusion scores accepted (83,493–117,693 gas each), Sybils reach reputation 100/3, weighted error
    27.59 — worse than unweighted. Reputation without entitlement-gated attesters amplifies Sybils;
    the gate is the endorsement registry. Toy model, harness Set C (not O7); the ordering of the
    effect, not its magnitude, is the result (HDA doc 09 §4–§5).
14. **F-VID-11 — ISetC has no validation-response write.** C3 requestValidation and C4 validationStatus
    exist, but nothing in ISetC lets a validator set the status; the harness adds resolveValidationAs,
    gated by endorsement. Spec/ISetC v1.1 candidate (also noted in HDA doc 04).
15. **Schema v1.1.** `latencyMs` added to tx/view entries by lib/vid/trace.js (additive). Values on the
    Hardhat in-process network are lower bounds and are not latency results.

## Slice 2 stage (b) (2026-10-15; trace bbs_presentation_O1_ERC1056_1792062147559)
16. **F-VID-12 — BBS+ selective disclosure changes nothing on-chain.** The same DRIVER_LICENCE object
    is hash-anchored via F5 (130,151) and additionally BBS+-signed off-chain (112 B over 9 claim
    messages); three verifier policies (9/9, 2/9, 1/9 claims) each produce an unlinkable proof
    (384–640 B) verified with the issuer's public key only, and F8 commits to the presentation
    nonce at the same 62,470 gas as a hash-path presentation. The issuer's BBS+ key is published
    through F9 (60,967 gas, 96 B key). Laptop timings: prove 93–116 ms, verify 59–116 ms (WASM,
    @mattrglobal/bbs-signatures 1.4) — instrumentation only, not OBU figures.
17. **F-VID-13 — proof size grows as disclosure shrinks.** 384 B (reveal all) → 608 B (reveal 2) →
    640 B (reveal 1): hidden messages cost ~32 B each in the proof. Minimal disclosure is the
    expensive case on the wire; the chain cost is flat.
18. **F-VID-14 — a BBS+ proof proves issuance, not currency.** After F7 the proof still verifies;
    only the status read (F6) or an accumulator/status-list witness carries revocation. Stage (d)
    item; confirms the 02 §6 split.

## Slice 2 stage (c) (2026-10-15; trace zk_age_gate_O1_ERC1056_1792062543673)
19. **F-VID-15 — on-chain Groth16 verification measured: admit() 250,283 gas.** AgeGate circuit
    (Poseidon commitment + LessEqThan, 256 constraints, 2 public signals), snarkjs-exported
    verifier, bn128, Hardhat. admit() includes the pairing check, one SSTORE (replay flag) and an
    event; the bare verifier cost is below that (not isolated; the view path check() is free).
    This is the first measured point for the DIGEST-LEVEL "≈200–350K" figure the thesis carried
    (K-HDA-6): it sits at the low end of that range, for a 2-signal circuit. Calldata 705 B.
20. **F-VID-16 — proving cost dwarfs verification cost.** Laptop, WASM witness generator, first
    call: prove 3,999.9 ms, off-chain verify 645.3 ms (includes WASM/curve initialisation; warm
    figures are lower and were not measured). Against BBS+ (S19: ~100 ms prove, ~60–116 ms verify)
    and the hash path (microseconds), the predicate proof is two orders of magnitude more
    expensive to produce — the Tier 2 question is prover placement (OBU vs pre-computation).
21. **F-VID-17 — predicate proofs need a circuit-friendly commitment.** The hash-anchored licence
    uses keccak for birthYearCommitment; the circuit needs Poseidon. S20 issues a licence whose
    commitment is Poseidon; a credential schema that must serve both paths carries both (two
    32-byte values), with no change to the anchor rule or to the interface.
22. **F-VID-18 — the under-age case is not a rejected proof but a non-existent one.** Witness
    generation fails at the constraint; a verifier never sees a "false" proof for a true holder.

## WO-1 start: O2_ERC721 port (2026-10-17; traces i2i_O2_ERC721_1792279382879, vid_minimal_O2_ERC721_1792279388171, vid_lifecycle_O2_ERC721_1792279393778)
23. **F-O2-1 — O2 admitted 12/12 unmodified; S1, S7, S8 run on it without a single line changed.**
    The VID layer (endorsement, typing, off-chain library) is implementation-agnostic in fact,
    not only by construction: the controller adapter is reused because O2 returns the same
    resolveDID document layout (did, controller, keyCount). Convention recorded for O3-O8.
24. **F-O2-2 — token-as-identity costs +6.4K on creation and is marginally cheaper elsewhere.**
    O2 vs O1 (S1 trace): createDID 185,326/168,226 vs 178,935/161,835 (+6,391: the mint's
    balance/owner slots and the Locked event); issueCredential 128,393 vs 130,163 (-1,770);
    addDelegate 52,495 vs 54,227; createPresentation 60,729 vs 62,441; deactivateDID 53,280 vs
    55,127; revokeCredential 33,087 vs 32,980 (+107). The ERC-721 option's low Set A anchor
    (15/24) is a semantics gap (no native deactivate-with-history, no key management), not a
    gas gap: the port had to add per-token state to close it, and that state is what O1
    already carries. Gas does not discriminate between these two options; coverage does.
25. **F-O2-3 — burn is not deactivate, enforced.** O2 refuses burn and transfer (Soulbound) and keeps
    the token after deactivateDID so the DID remains resolvable with its flag (DID Core 7.3). The
    structural weakness recorded for ERC-721 in Building Paths is closable in the port, at the
    cost of not using the token's native lifecycle primitive at all.
26. **Governance gas on O2** (S7): registerIssuer 75,326; endorseIssuer 149,975; revokeEndorsement
    54,123; declare 148,740 - within ~1.5K of O1, as expected (the registry's own storage dominates).

## WO-1: O3_ERC725 port (2026-10-17; traces i2i_O3_ERC725_1792279664711, vid_minimal_O3_ERC725_1792279669808, vid_lifecycle_O3_ERC725_1792279675063)
27. **F-O3-1 — contract-per-identity measured: createDID 764,090 / 746,978 gas**, above the spec's
    <600K ERC-725 target by ~25%. The cost is the ERC725Account deployment (owner, manager, four
    initial setData writes). Every per-identity datum is thereafter an external call into the
    account: addVerificationMethod 169,101 (the key bytes are stored and queryable, vs 59,607 on
    O1 where only the keyId flag is stored), updateDID 178,398 (attribute value stored, vs 44,760
    event-only on O1), addDelegate 85,306, deactivateDID 92,675, revokeCredential 74,587. F5
    142,377 and F8 79,084 are closer to O1 (+12K/+17K) because they add one external write each.
    O3 pays for queryability on every write; O1 pays for it off-chain in an indexer (doc 01 §4).
28. **F-O3-2 — read-path cost propagates into governance writes.** On O3, registerIssuer 111,002
    (vs 76,800 O1, 75,326 O2), endorseIssuer 185,519 (vs 151,449 / 149,975), revokeEndorsement
    89,667 (vs 55,597 / 54,123), declare 183,850 (vs 150,463 / 148,740). The registry code is
    identical; the delta (~34K) is the adapter's controllerOf/isActive resolving through four
    cold external getData calls. Any layer that authorises BY DID inherits the option's read
    cost — the first measured cross-layer effect of data placement.
29. **F-O3-3 — the layer ran unchanged on a third option.** Same document layout convention;
    no script or contract above the interface was touched. Three options now carry S1/S7/S8.

## WO-1: O4_ERC725xy port (2026-10-17; traces i2i_O4_ERC725xy_1792279894803, vid_minimal_O4_ERC725xy_1792279900331, vid_lifecycle_O4_ERC725xy_1792279905881)
30. **F-O4-1 — the only native credential object on the EVM costs 2.4x the anchor pattern.**
    issueCredential on O4 = 308,310 (an ERC-735 claim written on the SUBJECT's account: claim
    struct with dynamic bytes, topic index, plus the registry index and the ClaimAdded event
    carrying the bytes) vs 130,163 (O1), 128,393 (O2), 142,377 (O3). With validUntil: 328,270.
    revokeCredential = removeClaim = 75,518 (vs 32,980 O1). The claim IS a queryable credential
    record (getClaim from the subject, no indexer) - the thesis's "claims-assisted" Set B path
    priced for the first time. F8 stays an anchor (72,625; no ERC provides presentation).
31. **F-O4-2 — createDID 1,633,094 / 1,615,982**: ClaimHolderAccount deployment (725Y store + 734
    keys + 735 claims + indices) is 2.2x O3's account and 9x O1. Key ops: addVerificationMethod
    180,375 first / 163,275 next (ERC-734 addKey + purpose index), addDelegate 214,107 (an ACTION
    key AND a 725Y expiry record, because ERC-734 has no expiry - annotated hybrid). Nine of the
    eleven spec ERC-725 targets are missed; architectural, recorded not optimised.
32. **F-O4-3 — ERC-735 has no expiry and no revocation state.** A removed claim is indistinguishable
    from a never-made one at the account; the registry index supplies existence and validUntil.
    This is exactly why F5-F7 stay "assisted": the native object lacks two of the VC Data Model's
    status fields. Governance writes on O4 track O3 (+~34K over O1: registerIssuer 111,474,
    endorseIssuer 185,991, revokeEndorsement 90,139) - the adapter read-path effect (F-O3-2) again.

## WO-1 complete (O5, O6) and WO-5 first run (2026-10-17; traces i2i/vid_minimal/vid_lifecycle for O5_ERC1155 and O6_ERC4337; benchmarks/gas_report.md)
33. **F-O5-1 — credential-as-token is the dearest anchor among the light options.** O5 issueCredential
    160,562 (a second ERC-1155 mint to the subject + record) vs 130,163 O1 / 128,393 O2; revoke =
    burn 40,788 (vs 32,980). createDID 207,354/190,242 (+28K over O1: the 1155 balance slot and
    TransferSingle event). Everything else matches O1/O2 within 1%: once lifecycle, keys and
    delegates are added as per-token state, the three light options are gas-indistinguishable.
    The ERC-1155 batch advantage is not reachable through IMinimalSSI (no batch functions) -
    a coverage-matrix note, not a measurement.
34. **F-O6-1 — the smart account's native expiry is the cheapest delegation of the contract
    options.** O6 addDelegate 60,318 = setSessionKey(validAfter, validUntil) on the account, vs
    85,306 O3 and 214,107 O4; validDelegate reads the account's session window - ERC-4337
    validationData semantics with no registry-side bookkeeping. createDID 1,096,819/1,079,707
    (SmartAccount deployment: ecrecover validation, key sets, data store). addVerificationMethod
    193,265 first / 176,165 next when the key is a 20-byte validation key (full authority), the
    one place where F9 changes who may act. test/o5_o6_native.js shows validateUserOp over a real
    signed op returning 0 (owner), 1 (stranger), and packed validUntil/validAfter (session key),
    and that the direct path agrees with it.
35. **F-WO5-1 — the gas matrix is generated, not typed.** benchmarks/gas_matrix.js aggregates all
    26 trace files into gas_matrix.csv and gas_report.md (6 options x 19 tags). Spec §5.3 misses
    by minimum observed value: O1 3, O2 3, O5 3 (all F1, F4, F5), O3 7, O4 8, O6 4. F1 is missed
    by every option; the <100K/<600K targets assumed implicit identity creation (pure
    event-sourcing / no deployment), which interface uniformity rules out - spec v1.1 item.
36. **F-WO5-2 — governance read-path tax by option** (registerIssuer): O1 76.8K, O2 75.3K, O5 76.7K,
    O6 84.3K, O3 111.0K, O4 111.5K. The adapter's resolveDID cost is the whole difference;
    O6 is cheap because owner() and validationKeyCount() are two warm reads, O3/O4 need four
    getData calls. This column belongs in the per-function placement matrix (HDA doc 01 §8).

## WO-2 (O7 ERC-8004) and WO-3 (O8 Indy-on-Besu) (2026-10-17; traces i2i/vid_minimal/vid_lifecycle for O7_ERC8004 and O8_LFDT)
37. **F-O7-1 — ERC-8004's interface does not fit legacy codegen.** giveFeedback (8 arguments, four
    dynamic strings) and the 11-argument NewFeedback event exceed the stack without the IR
    pipeline. The two ERC-8004 files compile with a per-file viaIR override (hardhat.config.js);
    every other contract keeps the global envelope. O7 gas is therefore a viaIR measurement and is
    labelled so. Logged as a deviation, not smoothed.
38. **F-O7-2 — the compliance layer over three registries measured.** O7 createDID 240,154 / 223,042
    (ERC-721 mint + Registered + agentWallet metadata); updateDID 168,285, addVerificationMethod
    186,362, addDelegate 113,444 and deactivateDID 90,622 are all setMetadata writes with string
    keys and dynamic values (the spec's on-chain metadata hook), three to four times O1. Set B is
    the anchor pattern (136,362). ISetC is native: attestReputation = giveFeedback(value = score,
    decimals 0, tag1 "starred") by the CALLER as client; owner/operator feedback reverts
    SelfFeedback (spec MUST); getReputation = getSummary over all recorded clients;
    requestValidation / validationStatus map onto the Validation Registry (validator named in the
    payload; status 0/1/2/3 from response >= 50). Agents are transferable: a transfer changes the
    controller and clears agentWallet, as the spec says. The one option where the identity is an
    asset, not a binding. Mainnet fidelity: IdentityRegistry 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432,
    ReputationRegistry 0x8004BAa17C55a88189AE136b182e5fdA19dE9b63 (erc-8004/erc-8004-contracts,
    2026-10-06); Validation Registry reported not production-deployed (DIGEST-LEVEL).
39. **F-O8-1 — the credential-definition anchor, priced.** O8's first issueCredential by an issuer
    costs 697,203 gas (lazy SCHEMA + CLAIM_DEF + REVOC_REG_DEF creation plus the index); every
    subsequent credential 164,966, of which the ledger-side write is an index allocation and a
    RevocationRegistryEntry event. The per-credential CONTENT HASH IS NOT STORED (AnonCreds
    posture: the credential is bound to the definition by the issuer's signature off-ledger).
    revokeCredential 66,016 = registry entry (accumulator stand-in update). This is the placement
    HDA doc 01 §3.7 describes, now measured beside the anchor pattern: amortised, O8 issuance is
    ~27% dearer than O1 because the sandbox index (issuer, subject, validUntil, revIndex) is what
    the interface's F6 obliges it to keep; pure Indy stores less.
40. **F-O8-2 — did:indy stores the document; did:ethr logs it.** O8 updateDID 168,952 (document
    rewrite, Indy ATTRIB semantics) vs O1 44,760 (event only); addVerificationMethod 78,521
    (document rewrite) vs 59,607. Delegation is non-native (annotated); F8 remains an anchor.
    AnonCreds presentations never touch the ledger, which is the Set B ceiling restated from the
    ledger side: the option with the richest off-chain credential model is the one whose on-chain
    F5–F8 carry the least per-credential state.
41. **F-WO5-3 — eight-option matrix.** benchmarks/gas_report.md regenerated from 32 traces. Spec
    §5.3 misses: O7 five (F3, F4, F9, F10, F11), O8 three (F3, F5, F7). Every option misses F1
    except O7/O8 against the 725 column (223K and 255K are under 600K; both are over the 100K
    light target, so the F1 verdict depends on which column applies: spec v1.1 item).

## WO-7 S5 IDPP port and WO-5 coverage matrix (2026-10-17; traces idpp_port_O1_ERC1056_to_O8_LFDT_1792281220403, idpp_port_O8_LFDT_to_O1_ERC1056_1792281224976)
42. **F-S5-1 — the 2020 ID Porting Protocol is executable with the twelve functions alone.** An
    identity with a VID birth credential and an OBU delegate was ported O1 → O8 and O8 → O1 in one
    script with no interface extension: F1 on the target, F5 re-anchoring the SAME typed hash
    under the issuer's target DID, F11 re-establishing the delegate, F3 writing a ported-from
    pointer on the target and a ported-to pointer on the source (target DID + registry address),
    F4 retiring the source. Nine continuity assertions pass both ways: source resolvable and
    deactivated, target active, credential hash identical, off-chain verification unchanged,
    target F6 valid, delegate invalid on source and valid on target. Port cost O1 → O8 = target
    createDID 254,829 + first-issuance 697,203 (lazy definitions; 164,966 thereafter) + delegate
    54,113 + pointers 191,835 (O8 document rewrite) and 45,558 (O1 event) + deactivate 55,127.
43. **F-S5-2 — IMinimalSSI has no "superseded" status.** After the port the SOURCE anchor still
    reports valid=true from F6 (its issuer is active; only the subject was deactivated). A
    verifier must follow the ported-to pointer and policy, which the interface neither expresses
    nor enforces. Candidate for spec v1.1: either F6 consults the subject's deactivation, or a
    pointer-aware status (superseded) is added beside validity. Design item; also bears on
    Local CVIN shards (HDA doc 03 §4).
44. **F-WO5-4 — coverage matrix generated (benchmarks/coverage.js → coverage_matrix.csv,
    coverage_report.md).** Declared per option from implementation NatSpec, trace-checked that
    every option ran all twelve functions. Readings: Set B is native on no EVM option except via
    ERC-735 claims (O4) and ERC-1155 tokens (O5), neither carrying expiry or a presentation; F8
    is anchor on every EVM option and off-ledger on Indy — the createPresentation finding per
    option; Set A fully native on O1, O3, O6, O8 only; Set C native only on O7. Native counts /12:
    O4 9, O8 9, O1 8, O3 6, O6 6, O5 5, O7 3, O2 2 — a different ordering from the gas ranking,
    which is the point the thesis makes with two matrices rather than one.

## WO-4: scenario catalog S2–S4 on all eight options (2026-10-19; 24 traces s2_dualmode/s3_evcharging/s4_insurance × O1–O8)
45. **F-S2-1 — dual-mode identity is realisable with the twelve functions; the pseudonym–verinym
    link never touches the chain.** Three pseudonym DIDs created by unrelated signers, each with an
    epoch authorisation anchored by the misbehaviour authority (F5) and a BSM delegate key (F11);
    100 BSMs verified against cached delegate validity and authorisation status with zero chain
    reads (375 ms for 100 on a laptop, signature + cache; not a Tier 1 timing claim). The
    verinym→pseudonym mapping exists only in the off-chain authorisation credential held by the
    vehicle and the authority (escrowed linkability, HDA 02 §8). Revoking one epoch (F7) leaves the
    verinym and other epochs valid; the retired pseudonym is deactivated, not deleted.
46. **F-S3-1 — the Tier 2 critical path has no chain entries.** EV-charging: mutual authentication
    from warmed caches (49.65 ms laptop, 0 chain reads), AEAD metering session off-chain, then two
    asynchronous F8 commits and one receipt anchor (F5) whose hash commits to the metering-log
    root and the payment reference. On-chain learns that two presentations happened and a receipt
    exists; price, energy and location do not appear. The operator's tariff licence is itself an
    endorsement-gated credential (regulator endorsed transitively by the ministry).
47. **F-S4-1 — ownership transfer is re-issuance plus delegate expiry, because IMinimalSSI has
    neither controller transfer nor early delegate revocation.** The vehicle DID persists across
    the sale; Owner1's "owner" delegate is withdrawn by re-issuing it with validity 0; keys rotate
    (F9/F10); registration and the ICBC policy (the 2020 paper's Fig. 5 credential) are revoked
    and re-issued to Owner2; the maintenance history remains valid. Confirms HDA 04/05's reading
    from code: two spec v1.1 candidates (transferController; revokeDelegate).
48. **F-WO4-1 — S2–S4 ran on all eight options with no per-option code**; 24 traces. Per-tier
    coverage summarised in benchmarks/tier_coverage.md (generated). Generic-schema fallback added
    to lib/vid/credentials.js for scenario-local credential types (tariff, receipt, insurance).
