# IDTx / ID-function-set figures — data tables (Phase 1, P1-1 … P1-6)

**Generated** by `docs/idtx_core/figures/make_idtx_figures.py`; do not edit. Each table is the data behind one figure in this directory (the table view of the SVG). The script is Python-stdlib only (no matplotlib) and emits deterministic SVG. **Author:** Nikhil Prakash (MASc, UBC ECE).

Sources: `PLAN.md` §4.2/§4.4, `p1/FUNCTION_MAP.md`, `p1/ANALOGIES.md`, `docs/phase2/focus/F1_onchain_storage_idtx/ANALYSIS.md` §4.2/§4.4, `BASIC_ID_SET_EXTENSION.md` §2. F-numbers are not used as labels because they are inconsistent across these sources (see the P1-6 note); functions are named and grouped by set.

## P1-1 Lifecycle ring (`p1_1_lifecycle_ring.svg`)
Set A is the identity lifecycle; Set B is a credential side loop whose presentation feeds an IDTx gate.

| Set | Stage / function | Role |
|---|---|---|
| A | 1 createDID | mint identifier + key |
| A | 2 resolve | identifier -> DID document |
| A | 3 rotate / delegate / attribute | maintain the document |
| A | 4 execute | the identity acts (agent proxy) |
| A | 5 deactivate | end of life |
| B (loop) | issueCredential -> verifyCredential -> revokeCredential | credential status |
| B (loop) | createPresentation | holder discloses; feeds an IDTx gate |

## P1-2 Primitive stack (`p1_2_primitive_stack.svg`)
Read bottom-up; each layer is built from the one below.

| # | Layer | Built from the layer below |
|---:|---|---|
| 1 | keys / signatures | asymmetric key pair; a signature proves control |
| 2 | identifier | a key/contract that is itself a DID |
| 3 | DID document | resolve() -> keys, delegates, attributes, services |
| 4 | credential | off-chain signed claim; issuer key + status anchored (L4) |
| 5 | presentation | holder discloses a credential, replay-protected (no native ERC) |
| 6 | IDTx | a transaction gated on a NAMED identity's state |

## P1-3 IDTx three-axis taxonomy (`p1_3_three_axis_taxonomy.svg`)
Axes: dependency kind x locus/encoding x evaluation point (ANALYSIS.md §4.4). Every IDTx falls in exactly one cell.

| IDTx | Dependency kind | Locus (encoding) | Evaluation point |
|---|---|---|---|
| T5 MOBI birth | attribute (VIN uniqueness) | L3 salted hash | in the transaction |
| T10 ERC-735 addClaim | claim value + issuer status | L4 attestation (+ L0 issuer auth) | in the transaction |
| T11 CVIN-Combined addClaim | claim value + issuer status | L4 attestation (+ L0 sticky revocation) | in the transaction |
| payToll | ownership | L0 plaintext | in the transaction |
| prototype execute | ownership / delegate / commitment | L0 or L3 | in the transaction |
| prototype createIntent + fulfil | same | same | off chain, re-checked later |

No Phase-1 IDTx evaluates *at admission*: admission-time checks are excluded (sender authentication).

## P1-4 Same decision, three worlds (`p1_4_three_worlds.svg`)
Decision: "admit a toll payment from this vehicle" (ANALOGIES.md IDTx row + closing section).

| World | Actors (lifelines) | Where the identity state is evaluated | Trust / freshness / ordering |
|---|---|---|---|
| A Centralized ABAC | Requester, PEP, PDP | a trusted PDP, off chain, once | decision by a trusted PDP on the caller's attributes |
| B V2X PKI (1609.2) | Sender vehicle, Receiver, trust list | in-message, offline at the receiver | no live authority; freshness via CRL / short certs |
| C On-chain IDTx | Caller/keeper, Contract, ledger state | inside execution, on a NAMED identity | no PDP; ordering race left open (§4.5) |

## P1-5 Inventory funnel 26 -> 6 -> 4 (`p1_5_inventory_funnel.svg`)
The Phase-1 inventory re-classified under the P2-D8 definition (ANALYSIS.md §4.2). 26 = 25 CAPTURE.md §5 instances + payToll.

| Stage | Item | Count |
|---|---|---:|
| gates | candidate identity gates | 26 |
| class | IDTx (cross-dependent) — kept | 4 |
| class | identity admin / sender authorisation | 10 |
| class | admission-time authentication | 4 |
| class | enabling view (no transaction) | 1 |
| class | identity-dependent decision (off chain) | 5 |
| class | not a dependency | 2 |
| IDTx | T5 MOBI birth; T10 ERC-735 addClaim; T11 CVIN addClaim; payToll | 4 |

## P1-6 Minimal set -> full SSI extension (`p1_6_minimal_to_full.svg`)
The 12 IMinimalSSI functions are the core (admission = passes all 12); the catalogue extends them along five axes (BASIC_ID_SET_EXTENSION.md §2).

| Extension axis | What the catalogue adds over the basic set |
|---|---|
| Cost & footprint | gas, zero->nonzero writes, calldata, log bytes — per function (L1) |
| Lifecycle | the MOBI VID I+II 17-event vehicle life (L2) |
| Read path | the resolution a verifier actually pays (L6) |
| Scale | marginal cost in population and history (L3) |
| Breadth | the same functions on 10 substrates; rank the admitted set |

Core functions — Set A: createDID; resolve; changeOwner / rotate; add / revoke delegate; set / revoke attribute; execute (agent proxy); deactivate. Set B: issueCredential; verifyCredential; revokeCredential; createPresentation; + relayed / sponsored op (U5 meta-tx).

**F-number note.** The source documents number the 12 functions differently (ANALOGIES.md F1–F12; BASIC_ID_SET_EXTENSION.md Set A = F1–F4, F9–F12 and Set B = F5–F8 with F8 = createPresentation; the canon archive `cvin-sandbox-v1.3` numbers them yet again, marked [B1]). The figures therefore label functions by name and set, not by contested F-number.
