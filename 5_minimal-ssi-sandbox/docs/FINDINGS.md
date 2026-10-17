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
