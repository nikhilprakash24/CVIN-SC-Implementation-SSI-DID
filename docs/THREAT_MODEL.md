# Threat Model

*Formal adversary model for the security analysis (addresses `RESEARCH_AUDIT.md` §4.7:
"the threat model is informal"). It states the system model, adversary capabilities,
trust assumptions, security goals, and out-of-scope items **before** the results, so the
54 executable attack scenarios (Chapter 5 §5.6, `test/security/securityScenarios.test.js`)
and the comparative threat matrix (`security-analysis/results/security_matrix.json`) can
be read as tests *against a stated model* rather than an ad-hoc list. Intended for
Chapter 3 (Methodology).*

## 1. System model

The assets are **vehicle identities** and the **credentials/attestations** bound to
them (birth certificates, lifecycle events, ownership, claims), realized on one of the
nine substrates and verified by relying parties (a DMV, an insurer, a peer vehicle).
Actors: **manufacturers/issuers** (create identities, issue credentials), **owners**
(control an identity, present credentials), **attestors** (third parties who vouch for
events), **verifiers** (relying parties), and **the chain** (an EVM ledger executing the
substrate contract). Off-chain, vehicles exchange signed V2V safety messages whose
sender identity must be verifiable (§5.4).

## 2. Adversary model

We assume a **computationally bounded** adversary (cannot forge ECDSA secp256k1 / P-256
signatures or find keccak256/SHA-256 pre-images) with the following capabilities:

- **A1 — Network/message adversary (Dolev–Yao at the message layer):** can observe,
  replay, reorder, drop, and inject V2V messages and on-chain transactions; can present
  copied credentials/presentations to verifiers.
- **A2 — Malicious registered party:** controls one or more *legitimately registered*
  identities/keys (a rogue owner, dealer, or attestor) and tries to act beyond its
  authorization (forge a claim, attest without authority, rewrite another identity's
  state, over-issue Sybil identities where issuance is ungated).
- **A3 — Key-compromise adversary:** has obtained the private key of a victim identity
  (theft, leak) and attempts takeover, or — conversely — the victim seeks recovery after
  compromise.
- **A4 — Passive on-chain observer:** reads all public chain state/events and attempts
  to recover PII (notably the VIN) or link identities.

**Explicitly assumed *not* available:** breaking the cryptographic primitives; a 51% /
consensus-level attack on the underlying chain (chain integrity is trusted — see §3);
compromise of the verifier's own code; physical/side-channel attacks on the vehicle HSM.

## 3. Trust assumptions

- **T1 — Chain integrity:** the EVM ledger executes contracts faithfully and its history
  is immutable (standard L1/consortium assumption). Consensus attacks are out of scope.
- **T2 — Issuer honesty at issuance:** an authorized issuer's *first* attestation of a
  fact (e.g. a manufacturer's birth certificate) is trusted; the model defends against
  *unauthorized* issuance and *post-hoc* forgery/replay, not an authorized issuer lying
  at t=0.
- **T3 — Key custody:** owners protect their private keys; A3 models the failure of this
  assumption and asks what recovery each substrate offers.
- **T4 — Verifier correctness:** relying parties run correct verification logic (the
  §5.5 compliance work concerns *conformance*, not verifier compromise).

## 4. Security goals

| ID | Goal | Adversary countered |
|---|---|---|
| G1 — Authenticity | Only the controlling key can create/modify an identity or issue on its behalf | A1, A2 |
| G2 — Non-forgeability of claims | A claim/attestation verifies only if signed by an authorized issuer over the bound context | A2 |
| G3 — Replay resistance | A captured signed operation/presentation cannot be re-used out of context (nonce/domain/chain binding) | A1 |
| G4 — Authorization integrity | A party cannot act beyond its role (issue/attest/revoke) | A2 |
| G5 — Sybil cost | Creating N identities imposes a cost/gate proportional to N | A2 |
| G6 — Recoverability | A compromised key need not mean permanent identity loss | A3 |
| G7 — PII confidentiality | The VIN and linkable PII do not appear in plaintext on-chain | A4 |
| G8 — Theft resistance | Transferring/stealing a token or key does not silently transfer the whole identity where the design forbids it | A2, A3 |

## 5. Mapping to the executed analysis

The two-lens security analysis (§5.6) tests this model directly:

- **Lens 1 — executable revert suite** (54 scenarios, `securityScenarios.test.js`): each
  scenario instantiates an A1/A2 attack against a goal and asserts it is **defended**
  (reverts), with a **differential control** that the *authorized* action succeeds — so a
  DEFENDED verdict proves the authorization/signature/replay barrier (G1–G4), not an
  unrelated failure. 43/43 applicable cells defended.
- **Lens 2 — comparative threat matrix** (`security_matrix.json`): scores the softer
  goals a revert-test cannot express — **G5** (Sybil, via issuance cost/gating), **G6**
  (recovery availability), **G7** (on-chain PII), **G8** (theft/transfer semantics) —
  across all substrates, yielding the "no standard dominates" frontier (H5).

Threat-goal coverage by attack category (Lens 1 labels → goals): unauthorized issuance →
G1/G4; unauthorized attribute write → G1; unauthorized delegate/claim → G2/G4; signature
replay → G3; unauthorized revocation → G4; identity hijack → G8. The found-and-fixed
MOBI `attestEvent` gap (§5.6) was a **G2/G3 violation** (an attestation accepted without
verifying the attester's signature) — now closed with domain-separated `ecrecover`
(EIP-191 + EIP-155 chain binding).

## 6. Out of scope (stated, not hidden)

Consensus-level (51%) attacks; cryptographic primitive breaks; verifier or HSM
compromise; physical/side-channel attacks; economic/MEV manipulation of the fee market;
governance attacks on upgradeable contracts (the evaluated contracts are non-upgradeable
in the tested configuration). These bound the security claims to the **application/
contract layer**, which is the thesis's scope.
