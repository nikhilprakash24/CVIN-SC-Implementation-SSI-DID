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
