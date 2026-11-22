# One Ledger, One Guarantee — Security Inheritance for Vehicle Identity

**Author:** Nikhil Prakash · **Date:** 2026-10-22 · **Drawings:** BP-001, BP-101, BP-102, BP-402, BP-403

## 1. The claim

A vehicle-identity operation in this system is an ordinary transaction. `changeOwner`, `addClaim`, `registerBirth` and `attestEvent` are signed with the same secp256k1 keys, carry the same EIP-155 chain id, enter the same mempool, are ordered by the same validators, are executed by the same EVM under the same gas schedule, and reach the same finality as a transfer of value. The ledger cannot tell them apart.

So whatever security a public chain gives to the value it settles, it gives in the same measure to the identity records it carries. If you trust the chain enough to send a large transfer across it, the same chain is guaranteeing that a vehicle's ownership change was authorised by the key that controlled it, happened in the order recorded, and cannot be silently rewritten.

This is the strongest argument for putting the identity substrate on a public DLT rather than on a bespoke registry. The comparison is not "is our registry secure?". It is "does our registry inherit the security the market already relies on for value?". It does, up to a line.

## 2. What is inherited (deck L2–L3 → L4, BP-402 detail B)

| Property | Value transfer | Identity operation |
|---|---|---|
| Ordering and finality | a final transfer cannot be reordered or undone | a final ownership change cannot be reordered or undone |
| Immutable history | the ledger's history | the event log the resolver walks *is* that history (BP-103, BP-201) |
| Deterministic execution | balance checks run as written for everyone | `onlyOwner`, role gates and `ecrecover` run as written for everyone |
| Transaction signature and replay protection | EIP-155 + account nonce | same, plus the application's own nonces (§3) |
| Liveness and censorship resistance | whatever the chain offers | the same |
| Economic security | attacking the transfer means attacking the chain | attacking the identity means attacking the chain that secures X in value |

**X is a parameter.** The value a given chain secures changes daily and is not a thesis result. When the figure is cited, cite it with a dated source and label it `param`. The structure of the argument does not depend on X; only its rhetorical weight does.

## 3. What is NOT inherited (BP-402 detail C)

The ledger guarantees that the code ran as written. It does not guarantee that the code was right. Above the waterline on BP-001 the guarantee is the application's own, and it must be earned and measured. These are the seven obligations, each with what discharges it in this repository.

| Obligation | Discharged by |
|---|---|
| Authorization logic (G1, G4) | 54-cell executable suite, 43/43 applicable defended, with a differential control (BP-403, `test/security/`) |
| Claim-level signature binding (G2) | digests bind registry, identity, topic and data; the `attestEvent` gap was found and fixed (121,110 → 192,718 gas, #28) |
| Payload-level replay (G3) | registry nonces, VP challenge and domain, nonce-keyed presentation anchors |
| Key custody (T3) and recovery (G6) | out of scope for custody; recovery native on ERC-4337 only (matrix) |
| Issuer honesty at issuance (T2) | not detectable by any substrate; it is an assumption, stated |
| Off-chain cache staleness | freshness-k bounds revocation lag at k − 1 messages (#32) |
| Verifier correctness (T4) | 94.3% conformance is a measure of conformance, not proof of a correct verifier |

A contract bug is executed faithfully by the most secure chain in the world. That is why the security suite exists, and why it is the half of the argument the thesis actually measures.

## 4. Precise wording for the thesis

Use this:

> Identity operations are ordinary transactions on the ledger that carries them, and therefore inherit its ordering, finality, immutability and economic security in exactly the measure that value transfers do (T1). The application-layer guarantees — authorization, claim binding, payload replay protection, cache freshness — are not inherited; they are this thesis's measured contribution (§5.6).

Avoid these:

- "As secure as Bitcoin/Ethereum." It erases §3.
- "Secured by $N trillion." It states a parameter as a result and implies the chain's total value protects one record.
- Any statement that the identity system is secure because the chain is secure.

## 5. Why it matters for the comparison

Every one of the nine substrates inherits the same L2–L3 guarantee, because they all run on the same EVM. So inheritance does not rank them. What ranks them is cost (BP-501), latency (BP-502) and the application-layer barriers (BP-403). Inheritance is the floor all nine share; the thesis measures what sits above it.

For the baselines this is a real difference. The PKI baseline and the centralised registry inherit nothing from a public ledger. Their integrity rests on the operator of the CA or the database. The DLT substrates replace that operator with the chain's consensus, which is the same consensus the market already trusts with value.
