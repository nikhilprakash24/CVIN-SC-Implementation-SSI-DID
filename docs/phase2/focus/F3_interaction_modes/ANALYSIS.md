# F3 Analysis — Three Modes of Communicating with the Chain, for Reads and Writes

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F3, analysis). **Builds on:** `CAPTURE.md` (verified), `MODE_CLASSIFICATION.md`
(generated), `docs/phase2/SCOPE_RECONCILIATION.md` §4. **Binds:** `docs/phase2/README.md`. **Numbers:** register rows only.

## 1. The question, and a naming caution
The author speaks of three modes or methods by which a party communicates with the blockchain, for reads and
writes. The repository never defined them. The capture found four coherent ways to cut the space, and one naming
clash: in this repository **"Mode 3" and "Mode 4" already mean C-V2X radio resource modes** (network-assisted and
autonomous sidelink; `cv2x-testbed/README.md`). F3's modes are therefore lettered, A, B and C.

## 2. The proposed taxonomy (the orchestrator's default; the author decides, P2-D7)
One question decides the mode, and it applies to reads and writes alike: **who carries the request to the chain at
the moment it is needed?**

| Mode | Carried by | Writes | Reads | Phase 1 evidence |
|---|---|---|---|---|
| **A, direct** | the party itself: its own key and its own node connection | an EOA transaction | `eth_call` for state; `eth_getLogs` for history | every harness write except U5; every harness read; the testbed's uncached verification (#21) |
| **B, mediated** | a third party | **B-submit:** a relayer sends a signed operation and pays (ERC-1056 `*Signed`), or a bundler sends a UserOperation (ERC-4337) | **B-serve:** an RPC provider or an indexer answers | B-submit measured (#50, #34); B-serve never measured (no provider, no indexer; M2 not run) |
| **C, detached** | nobody, at the moment of use | signed now, anchored later (no Phase 1 instance; the F2 journal anchoring is the first prototype) | a credential, cache or proof obtained earlier is checked in-process | V2V and V2I verification (#27, #44); the freshness cache between re-checks (#32, #37, #46) |

The capture's critique is adopted. "Mediated" mixes two different trust relations, so B is split into **B-submit**
(someone else submits and pays: trusted for liveness and ordering, not for content, which the signature fixes) and
**B-serve** (someone else answers a read: trusted for the content, unless the answer carries a proof). Two finer
points from the capture are kept as well:
- **Mode C is a dial, not a point.** A freshness re-check every k messages makes a verifier Mode C for k − 1 messages
  and Mode A for one (#32).
- **Phase 1 has no detached write.** The ERC-1056 signed digest includes the current nonce, so an operation signed
  offline goes stale once that nonce is used.

The three other cuts the capture found, and how they map, so the author can choose any of them:

| Alternative cut | Its three modes | Maps to the default as |
|---|---|---|
| Chain contact at time of use | synchronous, periodic, none | A, C with finite k, C with k = ∞ |
| Who acts | self, delegated, none | A, B, C |
| Transport | in-process, node over RPC, public provider | sub-cases of A (M1, M1-H/HTTP) and B-serve (M2) |

## 3. What each mode costs and implies, from the evidence
**Writes.** The same attribute update costs 35,024 gas sent directly by the owner (Mode A), and 62,646 gas when the
owner signs and a relayer submits (B-submit, +27,622). An ERC-4337 UserOperation costs 141,767 against a direct 94,651
(+47,116) (#50, #34; figure F3-1). Only two of the ten harness columns have any relayed path. So B-submit is available
for ERC-1056 and ERC-4337 only, and costs between a third and four fifths more gas. What it buys is that the vehicle's
key need not hold funds or reach the chain itself.

**Reads.** Verifying one vehicle message spans three orders of magnitude by mode (figure F3-2):
- **C:** 0.153 ms, a cached credential with no chain contact (#27).
- **A, cheapest check:** 2.76 ms, a probe that confirms the identity is unchanged (#37).
- **A, full:** 9.654 ms, the key replayed from event logs (#21).

The last two predate the D51 fix, which adds one call to a full resolution, and are due for re-run (A3b). Only Mode C
fits a 10 Hz safety-message budget at density. Modes A and B belong to set-up, renewal and the periodic re-check.

**Trust, privacy and availability.**

| Concern | A, direct | B-submit | B-serve | C, detached |
|---|---|---|---|---|
| Who must be trusted for correctness | the party's own node | nobody for content (the signature fixes it) | the provider, unless the read is proven (state proofs, a light client) | the issuer of the credential, and the freshness rule |
| Who can censor or delay | the party's network | the relayer or bundler | the provider | nobody at use time; the issuer at renewal |
| Who learns what is being looked up | the party's node | the relayer learns the operation | the provider learns every query: a linkability channel | nobody |
| Staleness | none at the read | none | as fresh as the provider | bounded: k − 1 messages (#46), and a clock assumption (D51, now in chain time) |
| Replay across chains | — | D52: the ERC-1056 signed digest lacks the chain id | — | — |

**Radio coupling.** C-V2X's autonomous sidelink (radio Mode 4) gives a vehicle no network path at the moment of use,
so on the safety path chain Mode C is not a choice: it is forced. Network-assisted operation (radio Mode 3) makes A and
B available when coverage exists. This is the strongest single argument for the cached, anchored design Phase 1 built.

## 4. What this means for the thesis and beyond
- **Thesis (existing evidence).** The taxonomy, the write and read tables and the radio coupling fit chapter 6 with
  rows #21, #27, #34, #37, #46 and #50. Choosing the taxonomy is the author's decision (P2-D7).
- **Small addition, if the author wants it.** B-serve is the one mode with no measurement. The Sepolia run (N-11)
  through a public provider would give it one data point.
- **Paper after the thesis.** Mode selection per message class, with a verified B-serve (state proofs) and a detached
  write (signed offline, anchored later).
