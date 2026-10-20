# W3C DID Method Rubric v2.0 — Mapping for the Compared Standards

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-09-24
**Closes:** audit recommendation 9 (adopt the rubric as the qualitative axis so
the comparison is commensurable with Fdhila et al. 2021 and other
rubric-based evaluations).
**Rubric:** W3C DID Method Rubric v2.0, W3C Group Note, 22 September 2026 —
https://www.w3.org/TR/did-rubric/ (45 criteria in 7 groups).

The rubric is **qualitative** and method-level. The thesis contribution is
the **measured** axis (gas, latency, message size, conformance). This file
defines how the two axes combine: each compared standard gets a rubric
profile (this file), and the measured results feed the rubric criteria that
are quantitative in nature (marked ▲). Cells marked *to assess* are open;
cells marked *n/a (trunk)* are for standards not implemented on this branch
(SC-07) and are filled after the bundle merge.

An important scoping note: all nine standards are **Ethereum smart-contract
methods** (registries on the same ledger), so the Rulemaking, Operation,
Enforcement, Adoption and most Security criteria are answered **identically**
by the underlying ledger and do not discriminate between them. The rubric
therefore separates cleanly into:

- **Ledger-level criteria** (answered once for Ethereum L1 / a chosen L2):
  3.1.1–3.1.6, 3.3.1, 3.3.4–3.3.8, 3.4.2–3.4.6, 3.5.1–3.5.4, 3.6.2–3.6.6, 3.6.8.
- **Method-level criteria that discriminate** between the standards:
  3.2.1–3.2.9 (Design), 3.3.2–3.3.3 (resource needs), 3.4.1 (auditability),
  3.4.7–3.4.8 (verification relationships, authentication model), 3.6.1,
  3.6.7 (crypto, provenance), 3.7.1–3.7.2 (privacy).

This separation is itself a finding: a comparison of ERC identity standards
is a comparison **within one ledger's rubric envelope**, and the thesis
should say so in chapter 3.

---

## 1. Method-level profile (the discriminating criteria)

| Criterion | ERC-1056 (`did:ethr`-class) | ERC-721 (NFT identity) | ERC-725 (proxy account) | Measured input |
|---|---|---|---|---|
| 3.2.1 Permissioned operation | none; any address is an identity by default | minting policy set by contract owner (`onlyOwner` in `CVINVehicleNFT`) | account creation open; key policy per account | — |
| 3.2.2 Interoperability | `did:ethr` resolvers and wallets exist (uPort/Veramo lineage); registry ABI is a de-facto standard | no standard DID method; project-specific `did:nft` | ERC-725 v2 / LSP0 ecosystem; project-specific resolution | conformance result (F5) |
| 3.2.3 Scope of usage | general | asset-bound identity | general, account-centric | — |
| 3.2.4 Cryptocurrency | ETH for gas on every write | same | same | — |
| 3.2.5 Offline creation | **yes** — identity exists before any transaction (implicit owner) | no — requires a mint transaction | no — requires deployment | ▲ register gas / deploy gas |
| 3.2.6 Update scalability | bounded by ledger throughput; one tx per update | same | same | ▲ SC-05 throughput decision |
| 3.2.7 Creation cost ▲ | 0 gas (implicit) / 54,860 (registry register) / 78,068 (wrapper with VIN) | 102,804 avg mint (+1,325,111 deploy once) | *to assess* (no test on trunk) | claim register #1, #3, #22 |
| 3.2.8 Update & deletion cost (out-of-pocket) ▲ | changeOwner 68,854 · setAttribute 51,126 · addDelegate 72,219 · revoke 75,044 | transfer *to assess* | *to assess* | register #2, #22 |
| 3.2.9 Update cost (in-kind) | none | none | none | — |
| 3.3.2 Limited-resource resolution | light: one storage read + event walk from `changed()` | one `ownerOf` + metadata read | account state read | ▲ resolve latency, RPC calls (#21) |
| 3.3.3 Limited-resource registration | any funded EOA | any funded EOA + minter permission | contract deployment | — |
| 3.4.1 Auditability ▲ | full: linked `previousChange` event chain | transfer events | key-change events | ▲ event-walk cost in resolve (#21) |
| 3.4.7 Verification relationships | authentication, assertionMethod (delegate types `veriKey`, `sigAuth`); keyAgreement via attribute only | via NFT ownership only | per-key purposes | internal checker DID-Core 4.4 FAIL/PARTIAL items |
| 3.4.8 Authentication model | key-based (secp256k1), delegate-based | ownership-based | key-based with roles | signing-scheme finding (§2.3 item 3, summary) |
| 3.6.1 Robust crypto | secp256k1 ECDSA, keccak-256 | same | same | — |
| 3.6.7 Provenance | registry contract address + chain id in the DID | contract + token id | contract address | — |
| 3.7.1 Per-DID visibility | all state public; VIN only as hash (MOBI VID) | token metadata public | account state public | SC-02 observability section |
| 3.7.2 Incentives for multicontext DIDs | cheap (implicit) → many DIDs per vehicle is free until first write | expensive (mint per identity) | expensive (deploy per identity) | ▲ creation cost |

## 1a. All nine standards (2026-10-04): measured inputs and the qualitative cells for the six added substrates

The quantitative cells (▲) for **all ten columns** are now generated from the harness run of
record by `npm run metrics:analyze` → `1_blockchain-identity/results/metrics/latest/tables/analysis_rubric_inputs.{md,csv,tex}`
(run `2026-10-04T09-50-29Z_0eef6af`; register #34–#36). That table supersedes the three-column
numbers quoted in §1 (which came from the test suite and the cv2x registry, register #1/#3/#22, and
are **not** the harness's operation definitions — see `MEASUREMENT_CONDITIONS.md` §5.D). The
qualitative method-level cells for the substrates not in §1:

| Criterion | ERC-735 (claim holder) | ERC-1155 (credential tokens) | ERC-725xy (X+Y account) | LSP8 (identifiable asset) | ERC-4337 (smart account) | CVIN-Combined (hybrid) |
|---|---|---|---|---|---|---|
| 3.2.1 Permissioned operation | open: anyone deploys their own holder; owner anchors, issuer revokes | **permissioned**: ISSUER_ROLE registers, issues, re-binds, burns; holders cannot transfer (soulbound) | open: anyone deploys an account | **permissioned**: a single contract owner mints, writes data and revokes | open: anyone deploys an account behind the EntryPoint | open: any address is an identity; claims gated to the identity owner and the issuer |
| 3.2.2 Interoperability | ERC-735 is an unfinalised draft; project-specific `did:erc735` | ERC-1155 wallets/indexers read balances; no DID method; project-specific `did:erc1155` | ERC-725 v2 / LSP0 ecosystem (resolvers for LSP0 Universal Profiles); project-specific here | LUKSO LSP8 tooling (representative implementation omits LSP1 hooks and operators) | ERC-4337 bundlers/wallets (harness EntryPoint is minimal, not canonical v0.7) | ERC-1056 half is `did:ethr`-compatible; claim half project-specific |
| 3.2.3 Scope of usage | attestation-centric identity | credential-holding identity | general smart account | asset-bound identity (collection-scoped) | general smart account with recovery | general identity + safety-critical attestations |
| 3.2.5 Offline creation | no (deploy) | no (issuer registers) | no (deploy) | no (authority mints) | no (deploy; counterfactual initCode omitted) | **yes** (implicit; C1 binds the VIN by claim) |
| 3.3.3 Limited-resource registration | contract deployment by the owner | none for the vehicle (issuer pays) | contract deployment | none for the vehicle (authority pays) | contract deployment (or sponsored via EntryPoint/initCode, not measured) | funded EOA (owner anchors the VIN claim) |
| 3.4.7 Verification relationships | owner only (ERC-734 keys absent) | vehicle address only | owner only (no LSP6 key manager) | token owner only (operators absent) | owner + **recovery guardian** (can install a new owner) | owner + delegates with TTL (`veriKey`, `sigAuth`) |
| 3.4.8 Authentication model | key-based; issuer signatures (EIP-191) verified on-chain at add time | role-based issuance; holder is the address | key-based (owner); executor for on-chain action | ownership-based; authority-written data | key-based; UserOperation signature validated by the account (EIP-191 over userOpHash) | key/delegate-based; raw-digest issuer signatures verified at add time |
| 3.6.7 Provenance | per-identity contract address (VIN in constructor) | registry address + vehicle address | account address | collection address + keccak(VIN) token id | account address + EntryPoint address | registry address + identity address + chain id in the claim digest |
| 3.7.1 Per-DID visibility | all claims public incl. signatures and data | balances public (credential types visible; one type per credential hash) | key/value store public | per-token data public | attributes public | events + claims public |
| 3.7.2 Incentive for multicontext DIDs | expensive (1.54 M deploy per identity) | cheap-ish (104 k register, but issuer-gated) | expensive (1.73 M per identity) | moderate (133 k mint, authority-gated) | expensive (0.81 M per identity) | cheap (267 k VIN claim; identity itself free) |

Where the rubric asks for a method *rule* (3.2.1, 3.3.3) the answer for ERC-1155 and LSP8 is
"permissioned", which is a different trust model from the open substrates and must be weighed
against their cost advantage in chapter 6: their cheap reads and writes are bought with a single
writing authority.

## 2. Ledger-level envelope (answered once)

To be written once for the deployment target (Ethereum L1 vs an L2), citing
the rubric's own worked examples for `did:ethr` where they exist. Criteria:
3.1.1–3.1.6, 3.3.1, 3.3.4–3.3.8, 3.4.2–3.4.6, 3.5.1–3.5.4, 3.6.2–3.6.6,
3.6.8. *Status: to assess.* Note that 3.6.8 (US federal compliance) is
unlikely to be relevant for a Canadian thesis and can be marked not
applicable with a sentence.

## 3. How this enters the thesis

- Chapter 3: one paragraph on the rubric, the ledger-envelope observation,
  and the list of discriminating criteria.
- Chapter 5: the method-level table above with all nine standards after the
  merge, the ▲ cells populated from the results files, and the internal
  compliance items cross-referenced to 3.4.7.
- Chapter 6: the rubric profile is the qualitative half of the Pareto
  argument (H5); the measured axis is the quantitative half.
