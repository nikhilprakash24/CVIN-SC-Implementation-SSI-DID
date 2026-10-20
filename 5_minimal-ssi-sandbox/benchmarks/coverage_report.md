# Coverage matrix (declared per option from implementation NatSpec; trace-checked)

| Option | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | native | assisted | anchor | absent | Set B path | Set C | ran 12/12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O1_ERC1056 | N | N | N | N | H | H | H | H | N | N | N | N | 8 | 0 | 4 | 0 | anchor + adapters (SD-JWT digests, BBS+ S19, Groth16 S20, PresentationAnchor) | harness (SetCHarness) | yes |
| O2_ERC721 | N | N | A | A | H | H | H | H | A | A | A | A | 2 | 6 | 4 | 0 | anchor + adapters | — | yes |
| O3_ERC725 | N | N | N | N | H | H | H | H | N | N | A | A | 6 | 2 | 4 | 0 | anchor (issuer 725Y store) + adapters | — | yes |
| O4_ERC725xy | N | N | N | N | N | N | N | H | N | N | A | A | 9 | 2 | 1 | 0 | ERC-735 claims (native object, no expiry) + adapters | — | yes |
| O5_ERC1155 | N | N | A | A | N | N | N | H | A | A | A | A | 5 | 6 | 1 | 0 | credential tokens (native object, no expiry) + adapters | — | yes |
| O6_ERC4337 | N | N | A | A | H | H | H | H | N | N | N | N | 6 | 2 | 4 | 0 | anchor + adapters | — | yes |
| O7_ERC8004 | N | N | N | A | H | H | H | H | A | A | A | A | 3 | 5 | 4 | 0 | anchor + adapters | native | yes |
| O8_LFDT | N | N | N | N | N | N | N | — | N | N | — | — | 9 | 0 | 0 | 3 | definition anchor (AnonCreds posture: no per-credential hash) + off-ledger presentations | — | yes |

N = native · A = assisted (sandbox-side state beside the standard) · H = hash-anchor pattern · — = absent in the standard (sandbox supplies).

## Notes per option

- **O1_ERC1056**: event-sourced did:ethr pattern; explicit DID storage for interface uniformity (FINDINGS 1)
- **O2_ERC721**: soulbound mint/ownerOf native; no lifecycle, key or delegate model in ERC-721 (burn != deactivate, F-O2-3)
- **O3_ERC725**: contract-per-identity; document and keys are 725Y data; anchors in the issuer's store; no delegate concept (expiry as 725Y data)
- **O4_ERC725xy**: F5–F7 are ERC-735 claims on the subject (the only native credential object on the EVM; no expiry/revocation state in ERC-735 → registry index, F-O4-3); F9/F10 ERC-734 keys; delegates = ACTION key + 725Y expiry
- **O5_ERC1155**: identity and credentials are tokens (issue = mint, revoke = burn, verify = balance); no lifecycle/key/delegate model
- **O6_ERC4337**: smart account = DID; validation keys = verification methods; session keys with validUntil = delegates (native expiry); attributes as account data
- **O7_ERC8004**: agent NFT + setMetadata native; no deactivation, key or delegate model (ERC-721 operators are the native delegation, honoured for authorisation); Set C (C1–C4) native via Reputation/Validation registries — the only option with native Set C
- **O8_LFDT**: did:indy nym/attrib/deactivate; F5 = schema/cred-def/rev-reg (definition anchor, no per-credential hash); F7 = revocation entry; F8 off-ledger in AnonCreds (sandbox anchor stands in); no delegation in did:indy (sandbox-side)

## Readings

- Set B (F5–F8) is native on no EVM option except through ERC-735 claims (O4) and ERC-1155 tokens (O5), neither of which carries expiry or a presentation; F8 is an anchor everywhere and off-ledger on Indy — the createPresentation finding, now per option.
- Set A (F1–F4, F9–F12) is fully native on O1, O3, O6, O8 only; O2/O5/O7 lack a lifecycle and key model and are assisted.
- Set C is native only on O7.
