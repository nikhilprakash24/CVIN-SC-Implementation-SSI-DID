# §6.x Feature asymmetry: the union versus the intersection (draft, 2026-10-04)

*Draft section for the discussion chapter. Every number below is taken from a file the
grand sandbox generates (`sandbox/grand/report/`) or from the claim register
(`docs/MEASUREMENT_CONDITIONS.md`), and is reproducible with
`python3 sandbox/grand/run.py all`. Status markers in the register apply.*

## 6.x.1 Why the comparison alone is not the result

The comparison of Chapter 5 measures an **intersection**: six operations — deploy, create,
update, delegate-or-claim, revoke, transfer — that every one of the nine standards can be
made to perform, so that gas and latency can be set side by side. That is the correct
instrument for the cost question, and it answers it. But it is silent about the
property that actually distinguishes the standards: what each one *also* does, what it
refuses to do, and what the difference costs. The per-option sandboxes make that
**union** explicit. Thirteen options (the nine standards, with ERC-1056 split into its
uPort-style and vehicle-profile variants, the MOBI VID application profile, and the two
in-process baselines) were each given a feature manifest derived from the compiled
interface, a uniform adapter, a demo for every implemented capability family, and the
same nine identity mechanisms under test. The three artifacts that result are the data
of this section: the declared union (`report/asymmetry.md`, 13 × 14 = 182 cells), the
observed mechanism table (`report/L1-asymmetry.md`, 11 × 9 = 99 records, 88/88
agreements with the manifests), and the exercised surface (`report/demos.md`: 92 demos,
1,625 contract calls, 100 % of every contract's public functions).

The headline is a size asymmetry of an order of magnitude. `MOBIVIDRegistryV2` exposes
54 public functions, `CVINVehicleNFT` 52 across its three contracts, the ERC-1155
credential contract 29; the uPort-style ERC-1056 registry exposes 16 and performs its
most important act — bringing an identity into existence — with **no function at all**.
The comparison's six operations touch between 1 and 7 of each option's fourteen
capability families; the rest is surface the comparison never priced.

## 6.x.2 Three axes of the asymmetry

**Creation: implicit, minted, or deployed.** The same word names three mechanisms with
three cost classes and three trust models. Under the uPort-style ERC-1056 registry and
the CVIN-Combined hybrid an address *is* an identity before any transaction — the L1
suite records creation at **0 gas** — and the vehicle-profile registry's explicit
`registerVehicle` costs 54,639. The token-shaped options require a mint by an
authorised party: 103,849 (ERC-1155), 149,430 (LSP8), 542,474 (ERC-721, VIN-bound).
The account-shaped options require a contract deployment per identity: 519,384
(ERC-725), 1,371,394 (ERC-735), 1,730,753 (ERC-725xy with its VIN key), 759,088
(ERC-4337 account; counterfactual in principle, explicit in this harness because the
minimal EntryPoint accepts no `initCode`). An operator choosing a substrate is choosing
which of these three things "creating a vehicle identity" means.

**Veracity and automation: what the chain enforces versus what a verifier must run.**
Five of eleven options hold claims on-chain (ERC-735, ERC-1155, LSP8, MOBI VID,
CVIN-Combined); the two ERC-1056 variants, ERC-721, ERC-725 and ERC-4337 do not, and
rely on off-chain verifiable credentials. On-chain claims are facts any party can read
and the contract enforces who may write them (MOBI VID's 11 × 9 issuer-role matrix is
checked in 88 demo steps); off-chain credentials are private and cheap but true only
when a verifier runs — and the sandbox showed what that difference means in practice:
the MOBI provider's `verify_message` trusts the key *inside* the message
(`docs/DEFECT_LOG.md` D11, open at the time of writing), so an impostor signing under a
vehicle's DID passes until the key is bound to the registry — exactly the failure the
on-chain form cannot have. Revocation shows the same
split: identity-level revocation exists on the ERC-1056 registries, ERC-721, ERC-1155,
LSP8 and MOBI VID; the account-shaped options can only revoke sub-identities (a key, a
claim, a data key), and ERC-4337 cannot revoke at all — the account persists and the
guardian is the only recourse (D15).

**Cryptography as a design surface.** Signed, off-chain-authorised execution is
available on four of eleven options (ERC-1056 uPort-style `changeOwnerSigned`, 96,053
gas; ERC-4337 UserOperations through the EntryPoint, 69,405; ERC-725xy `execute`,
76,352; ERC-725's `execute` at 28,358 — which the demos showed to be a stub that emits
an event and performs no call, D23). Where it exists, the signature scheme is not
uniform: ERC-1056 verifies a raw secp256k1 signature over its own digest, ERC-4337 an
EIP-191 hash of the UserOperation, ERC-735 an EIP-191 message while CVIN-Combined
rejects EIP-191 and requires the raw digest (D25) — so the two claim contracts are
mutually incompatible for the same claim. Hashing choices carry the same weight: keccak
attribute keys, salted SHA-256 VIN hashes with an AES-256-GCM-encrypted VIN on the MOBI
registry, and a VIN that is case-sensitive on three token options so that a
lower-cased VIN mints a second identity (D13). The baselines add the curve question:
the IEEE 1609.2-style PKI uses P-256 and signs a BSM in 0.054 ms; secp256k1 signing
costs 0.401 ms (register #21) — a sevenfold difference on the hot path that is a
consequence of choosing Ethereum's curve, not of blockchain as such.

## 6.x.3 The asymmetry budget

Rather than ask what an operation costs, the sandbox allows the inverted question: what
does it cost to be *able* to do something the V2V hot path never uses? Each option's
`report/demos.md` row sums the gas of every implemented feature exercised; the
comparison's six operations are a subset of those rows. The gap — royalties and toll
payment in an NFT identity, guardian recovery in an account, batch credential
transfers, LSP data keys — is capability the vehicle carries and pays for in
deployment size (ERC-721 2,751,406 gas; MOBI VID V2 3,952,603) and in attack surface.
The defect log quantifies the second: of 26 latent defects found in the research code
by the verification passes and the demos, 20 live in features outside the measured
intersection, and six are rated high because they touch a thesis claim (an unreachable
birth record, D18; two ways the `did:ethr` change list is severed, D21–D22; the
impostor-accepting verifier, D11; a non-conformant `did:ethr` string, D10; duplicate
identities from VIN case, D13). "Implemented" surface is not free even when it is
never called.

## 6.x.4 What follows for the choice of substrate

The comparison's cost ranking and this section's capability map do not point the same
way, and that is the finding. The cheapest creation (implicit, 0 gas) belongs to the
option with the smallest union and no on-chain claims; the richest union (MOBI VID V2,
54 functions, 7 measured families) is the most expensive to deploy and the most
exposed. The CVIN-Combined hybrid sits where Chapter 5 placed it — implicit creation,
on-chain claims, 18 functions — and the sandbox adds the qualification that its claim
operations currently sever the change list a resolver relies on (D22), a defect that is
a one-event fix and a reminder that a hybrid inherits the invariants of both parents.
The recommendation of Chapter 7 is therefore stated in terms of the three axes rather
than the ranking: choose the creation class the deployment can afford, the veracity
model the verifiers can run, and one signature scheme across every contract the
vehicle will meet.

*Tables for this section: `report/asymmetry.md` (declared union), `report/L1-asymmetry.md`
(observed mechanisms with gas), `report/demos.md` (exercised surface); defect references
`docs/DEFECT_LOG.md`; measurement conditions and status `docs/MEASUREMENT_CONDITIONS.md`.*
