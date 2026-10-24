# WP 1.9 — Thesis Draft Sections (Phase 1)

**Produced:** 2026-10-24 (Editor). **Status:** draft for the author and the examiner pass (WP 1.10).
**Placement:** per `DETAILED_PLAN.md` §1. Each block below is headed with its home chapter/section.
**Evidence discipline:** claims carry the source tags from the WP files (`[src]` primary-verified, `[sec]` secondary-only,
`[recalled]` not yet verified — stated as open, never as fact). Numbers cite register rows in `docs/MEASUREMENT_CONDITIONS.md`.

---

## A. Chapter 3 — new §3.x "The ID-system function set" (HOME)

### 3.x.1 Why a function set, not a standard, is the unit of comparison

A comparison of identity substrates needs a common unit. Comparing whole standards (ERC-1056 against ERC-735 against
ERC-4337) compares bundles that draw their boundaries differently; comparing single opcodes compares mechanism, not
capability. This thesis takes the unit to be a **shared set of identity-system functions** — the capability surface on
which the substrates are compared, independent of how any one substrate realises them. It is *not* claimed to be a
proven-minimal or necessary set: the agent-proxy (`execute`) and the relayed/sponsored operation have no analogue in
the centralized, national, or V2X identity worlds (`ANALOGIES.md`); they are blockchain-account capabilities, so the
set reflects what these EVM substrates expose for comparison, not a per-function necessity argument (examiner obj. 1).

The set is the canonical sandbox's `IMinimalSSI` interface (`docs/BASIC_ID_SET_EXTENSION.md` §1), split into
**Set A — identity and keys** and **Set B — credentials**, with an optional **Set C** agent layer. A substrate is
*admitted* to the comparison when it passes the compliance suite on a **pass-or-justified-`n/a`** basis: a substrate
need not implement every function natively, only either support it or carry a recorded `n/a` where the standard lacks
the primitive (Appendix G-A records native vs pattern vs absent per substrate — only ERC-4337 is natively complete;
delegate and `create presentation` are `n/a` on several token substrates, and ERC-725 `execute` is a stub). Admission
is therefore *not* "implements all twelve"; the earlier "admission = compliance" shorthand is corrected here (examiner
obj. 8). The measurement catalogue then adds cost, lifecycle, read path and scale over the admitted set (§3.x.4).

> Function-numbering note. Three sources number the twelve functions differently (`ANALOGIES.md`,
> `BASIC_ID_SET_EXTENSION.md`, and the `cvin-sandbox-v1.3` canon archive, which is not in this repository). This thesis
> refers to functions by **name and set**, not by a contested F-number. Verbatim signatures are reproduced in
> Appendix G-B once the archive is available (marked **[B1]**).

### 3.x.2 The function set

The exact count and numbering are pending the canon archive (G-B, **[B1]**); the operations the substrates are compared
on are listed below. `BASIC_ID_SET_EXTENSION.md` groups them as Set A (identity and keys) + Set B (credentials) — the
`IMinimalSSI` interface — with the relayed/sponsored operation a *separate* programme addition on top. The eleven rows
below are the lifecycle operations this draft can name distinctly; whether the canonical interface numbers them as
twelve (and exactly how) is deferred to the G-B archive, so this draft does not assert a "twelve" count. The last two
(execute, relayed op)
have *no analogue* in the centralized, national, or V2X identity worlds (`ANALOGIES.md`); they are blockchain-account
capabilities, not operations an identity must have, so the set is best read as **the capability surface these
substrates expose for comparison**, not as a proven minimal or necessary set (examiner obj. 1).

| Set | Function (by name) | What it does |
|---|---|---|
| A | create identity (`createDID`) | mint an identifier bound to a controlling key (and, in the vehicle profile, to a VIN) |
| A | resolve | map an identifier to its current document — keys, delegates, attributes, service endpoints |
| A | rotate controller (`changeOwner`) | move control of an identity to a new key |
| A | add / revoke delegate | grant and withdraw time-boxed sub-keys (session or verification keys) |
| A | set / revoke attribute | write and clear identity-document state |
| A | execute (agent proxy) | let the identity itself act — send a call as the identity |
| A | deactivate | end the identity's life |
| B | issue credential | an issuer attests a claim about a subject |
| B | verify credential | check a credential's signature and status |
| B | revoke credential | invalidate an issued claim |
| B | create presentation | a holder discloses a credential to a verifier, replay-protected |
| (opt.) | relayed / sponsored operation (meta-tx) | submit an operation whose gas another party pays — a programme addition, no identity-world analogue |

`execute` sits in Set A because the canon interface places it there (`BASIC_ID_SET_EXTENSION.md`); the **optional Set C**
is the separate ERC-8004 *agent* layer (and the layer-5 `ZkVinGate`), not the plain `execute` primitive (examiner obj. 17).

The full function→implementation map across the ten substrates — the symbol that realises each function and the test
that guards it — is Appendix G-A; the per-function pseudocode is Appendix G-D. Two structural findings fall out of the
map and matter for the thesis:

1. **Most functions are patterns, not primitives.** On the registry and account substrates (ERC-1056, ERC-725/xy,
   ERC-4337, CVIN-Combined) the Set-B functions and `create presentation` are realised as patterns over a single
   generic write (`setAttribute`/`setData`/`addClaim`), not as dedicated operations (Appendix G-A). This is precisely
   why the function set, not any one standard's surface, is the right axis.
2. **No ERC provides `create presentation` natively** (`BASIC_ID_SET_EXTENSION.md` §1); it is realised everywhere as a
   replay-protected on-chain anchor. `execute` is native only on the account substrates (ERC-725xy, ERC-4337); on
   ERC-725 it is a stub that emits an event and performs no call (Appendix G-A).

### 3.x.3 The primitives beneath the functions

The functions rest on a small stack of cryptographic and protocol primitives (Appendix G-C gives one card per
primitive, with the spec section read at source and the alternatives):

- **secp256k1 ECDSA with EIP-191/EIP-712 domain separation** `[src]` — the authentication-and-attestation primitive;
  domain separation is what stops a signature from one context being replayed in another. **Caveat:** this holds for the
  EIP-712/191 paths, *not* for `addClaim`/`attestEvent`, which recover a **raw keccak digest** (no EIP-191, no chain-id,
  no nonce; `CVINCombinedIdentity.sol`) — so those two carried-signature paths, which are the measured "true IDTx",
  carry a cross-chain replay exposure (D52) the thesis does not claim to have closed (Appendix G-C card 1, item e′).
- **did:ethr over ERC-1056, event-sourced resolution** `[src]` — the document is reconstructed from the event log, not
  stored; this is the source of ERC-1056's low write cost and its history-dependent read cost (register #31, #51).
- **W3C DID Core 1.0** `[src]` and **Verifiable Credentials Data Model 2.0** `[src]` — the identifier/document and the
  credential/presentation models.
- **Credential status (Bitstring Status List)** `[src]` — revocation as a status bit, off-chain, anchored on-chain.
- **Salted-hash commitment** — the L3 VIN-privacy pattern; it gates by *equality* with a public value and proves no
  knowledge of the committed value (`ANALYSIS.md` §4.4, AR-5).
- **Groth16 zk-SNARK with a nullifier** `[src]` — the ZK-VIN tier (`ZkVinGate`); the nullifier makes an admission
  one-time *within* a scope and hides the VIN/year/mfr. It does **not** make admissions unlinkable across scopes: the
  built `admit` emits the identity address in clear (`ZkVinGate.sol:113`) and re-checks the same anchored commitment
  every scope, so an identity's admissions are linkable. Cross-identity unlinkability would need a Semaphore-style
  anonymity set, not built here (Appendix G-C card 7).

### 3.x.4 The extension to a full SSI system

The basic set asks one question per substrate — does it implement the twelve functions? The measurement catalogue keeps
that question as the conformance gate and adds what the thesis needs and the basic set does not: **cost and footprint
per function** (L1), **composition over a vehicle's 17-event life** (L2), **marginal cost in population and history**
(L3), the **read path a verifier actually pays** (L6), and **breadth** — the same functions on ten substrates so the
admitted set can be ranked (`BASIC_ID_SET_EXTENSION.md` §2). Figure P1-6 shows the twelve functions as the core and
these five axes as the extension.

---

## B. Chapter 6 — §6.8 expansion "The identity-dependent transaction" (HOME; builds on `DRAFT_6.8_IDTX_2026-10-20.md`)

### 6.8.1 Definition

The thesis adopts, verbatim and unaltered (decision AR-2), the definition of `ANALYSIS.md` §4.1:

> An **identity-dependent transaction (IDTx)** is a transaction whose admissibility or effect is a function of the
> state of an identity that the transaction names. That state is evaluated during execution, either from ledger state
> or from an attestation or proof that the transaction carries and verifies. Two cases are excluded: authentication of
> the transaction's own sender, and a check whose only subject is the identity record that the transaction itself
> modifies (identity administration).
>
> An off-chain decision that depends on identity state, such as a verifier accepting a message, is an
> **identity-dependent decision**. It shares the freshness dimension but is not a transaction.

Where the twelve functions are the identity *lifecycle*, the IDTx is identity *used as a precondition by other
transactions*. That distinction is the section's load-bearing idea, and it is why the function set alone does not
capture the contribution: no function in Set A or Set B is, by itself, an IDTx.

### 6.8.2 The inventory: the mechanism is rare

Re-classified under the definition, the twenty-six candidate gates of Phase 1 (twenty-five from `CAPTURE.md` §5, plus
`payToll`, which the capture missed) fall into **six classes** (`ANALYSIS.md` §4.2; Figure P1-5): **4** true IDTx,
**10** identity administration or sender authorisation, **4** admission-time authentication, **1** enabling view (T3
`validDelegate` — state any contract could depend on, but a gate by itself is not a transaction), **5** off-chain
identity-dependent *decisions*, and **2** that are not dependencies at all (4+10+4+1+5+2 = 26). The four true IDTx are
the MOBI birth (VIN uniqueness against other identities), the two `addClaim` paths (issuer authorisation and claim
status), and `payToll` (a payment gated on the named vehicle's owner).

**Boundary caveat (examiner obj. 3).** Only the two `addClaim` paths lie inside the ten *measured* substrates; `payToll`
is in an ERC-721 research copy (`CVIN_NFT_DID_ERC721.sol`, not the measured substrate, no register row) and the MOBI
birth is in MOBI-VID, outside the ten-adapter conformance gate (Appendix G-A). Over the measured set the count is
therefore **2**, with `payToll` and the MOBI birth as out-of-set exemplars. The count is also sensitive to the
definition's exact wording (T5's dependency is on the *set* of identities, not one the transaction names in the
narrowest reading). The robust claim is the weaker one: **the guard-on-execution mechanism is used overwhelmingly for
administration and authentication, and the richest identity dependencies live off-chain as decisions** — not a precise
headcount.

### 6.8.3 The three-axis taxonomy

Every IDTx falls in exactly one cell of three axes (`ANALYSIS.md` §4.4; Figure P1-3): **dependency kind** (ownership /
delegate or key validity / attribute or claim value / revocation status / history property); **locus with encoding**
(L0 plaintext, L3 registered commitment, L4 carried attestation, L1 carried receipt proof — the last unmeasured); and
**evaluation point** (in the transaction / at admission / off-chain then re-checked). None of the four true IDTx use
the "at admission" point — that is the excluded sender-authentication class — which the figure shows as a deliberately
empty facet.

> Prototype scope (examiner obj. 15). The `IdtxExecutor` prototype's `execute`/`fulfil` demonstrate the *admissibility
> predicate* (they revert unless the identity dependency holds) but emit rather than enact an external effect, so the
> artifact evidences the "admissibility" half of §6.8.1, not the "effect" half. Positioning against **capability-based
> security** (obj. 13): a capability is unforgeable bearer authority the holder presents; an IDTx instead *reads* the
> named identity's current ledger state at execution, so it reflects revocation and rotation immediately, where a bearer
> capability, once issued, does not — that freshness coupling, not possession of a token, is the distinguishing property.

Three constraints connect the axes, each a finding in its own right: **L1 rules out direct evaluation** (an ERC-1056
attribute can be depended on only through a receipt proof Phase 1 never built — the registry exposes no attribute-value
read, `idtx.test.js:138`); **a commitment is equality-only** (it proves no knowledge of what it commits to, AR-5); and
**a later re-check leaves an ordering race** (`fulfil` re-checks on-chain and so closes the time-of-check/time-of-use
gap *inside execution*, but not the mempool ordering race between the dependency's change and the dependent
transaction, AR-10).

### 6.8.4 Position against prior art

The guard-on-execution mechanism is **not new, and the thesis says so first.** More strongly, the *predicate semantics*
are not new either: an IDTx evaluates the attributes of the object/resource identity named in the request, which is
**object-attribute ABAC** (NIST SP 800-162 §3.2 evaluates subject, object, and environment attributes — object-attribute
policies gate precisely on the state of the named resource, not only the caller). The earlier framing that "ABAC gates
the caller whereas an IDTx names another identity" is withdrawn as a mischaracterisation of ABAC (examiner obj. 2).
Permissioned tokens over an identity registry — ERC-3643 with ONCHAINID — are the closest on-chain prior art, and the
one place an IDTx-class workload has actually been *measured* is Frutuoso et al. (2026, arXiv 2607.16383), ad hoc and
with no shared workload.

The contribution claimed here is therefore narrow and explicit: **the IDTx is object-attribute ABAC realised on-chain**,
and what is new is (i) the **storage-locus × encoding × evaluation-point taxonomy** (§6.8.3), which classifies *where*
the depended-on identity state lives and *when* it is evaluated — a dimension ABAC's policy model does not address
because it assumes a trusted PDP with direct attribute access; and (ii) the **on-chain freshness and ordering analysis**
(the staleness bound for off-chain decisions, and the mempool ordering race a later re-check leaves open, AR-10), which
arises only because the PDP is itself a transaction on a public ledger. The definition (§6.8.1) earns its place by
drawing the boundary these two analyses need, not by claiming a new access-control concept.

> Freshness-evidence caveat (examiner obj. 7). The k−1-message staleness bound (register #32, #37) predates the D51
> chain-time fix and is marked for re-run in `ANALYSIS.md` §3 (A3b). It is cited here as **pre-fix and provisional**;
> the contribution rests on the *existence and shape* of the bound, not on the superseded numbers, and the clean
> measurement belongs to the post-thesis study (P5).

---

## C. Chapter 2 — §2.6 ending, and Chapter 7 — contribution/future-work (HOME of the gap claim)

The benchmark-gap claim is stated in a form that a neutral reader can recognise as a gap *before* reading Chapter 6 —
i.e. without invoking the thesis's own coined term (decision D-GAP, revised per examiner obj. 4; evidence in
Appendix G-F, 31 sources):

> No existing benchmark pairs a **shared, reusable identity-gating workload** — operations whose admissibility depends
> on the state of a named identity — with an **admission/conformance rule**. Performance benchmarks that exist measure
> the identity *lifecycle* (create/resolve/update/deactivate) with no gating workload; conformance suites supply a
> workload and an admission rule but measure spec conformance, not cost; and the one study that measures an
> identity-gating workload (Frutuoso et al. 2026) is ad hoc, with no reusable harness.

Two honesty constraints the examiner pressed and the thesis accepts: the gap is **not** defined as "no one has
benchmarked an IDTx" (that would be trivially true of any new term); and independent reproduction is **not** used as a
discriminator against prior art, because the benchmark this thesis itself proposes (below) also lacks a reproduction at
publication — reproduction is named as a *maturity milestone* for any candidate, this work included, not as a gap only
others fail.

The thesis does **not** claim that no SSI or decentralized-identity benchmark exists — one does (Satybaldy et al. 2026,
arXiv 2601.20716, which self-describes as a benchmark and ships a replication package). The thesis positions against it
explicitly: that work benchmarks the DID *lifecycle* (create/resolve/update/deactivate over three DID methods), which
in the terms of §6.8.1 is exactly the administration/authentication classes that are *excluded* from being IDTx. The
qualitative aids (W3C DID Method Rubric) give no workload; the conformance suites (W3C DID/VC, DIF, eIDAS/EUDI) give a
workload and an admission rule but measure spec conformance, not performance; general blockchain benchmarks (BLOCKBENCH,
DIABLO, Caliper) satisfy all five axes but carry no identity workload. The gap this thesis names is therefore specific:
a measured workload whose unit is an identity-dependent *transaction*, with an admission rule and an independent
reproduction. Chapter 7 proposes the ingredients of such a benchmark (the twelve functions + the IDTx classes + the
17-event lifecycle as the workload; the twelve-test suite as the admission rule; the register's measurement conditions
as the metrics; this repository as the harness) and issues it as future work.

---

## D. Appendix G skeleton — "The ID-System Function Set and IDTx"

| § | Title | Source file | Status |
|---|---|---|---|
| G-A | Function → implementation map (12 fns + IDTx × 10 substrates) | `p1/FUNCTION_MAP.md` | drafted |
| G-B | Verbatim `IMinimalSSI` F1–F12 signatures | — | **[B1]** blocked on `cvin-sandbox-v1.3` |
| G-C | Primitive cards (8 primitives) | `p1/PRIMITIVES.md` | drafted |
| G-D | Pseudocode (lifecycle + IDTx + ZkVinGate) | `p1/PSEUDOCODE.md` | drafted; **author to verify** |
| G-E | Three-worlds analogy matrix | `p1/ANALOGIES.md` | drafted (CAV cells `[sec]`) |
| G-F | Benchmark-gap evidence (31 sources) | `p1/BENCHMARK_GAP.md` | drafted |
| G-G | Phase 2 trade-off matrix (other ID systems) | — | Phase 2 |
| G-H | Phase 5 per-substrate measured tables | register | Phase 5 |
| G-I | Phase 6 IDTx + compound-scenario diagrams | — | Phase 6 |

Figures P1-1…P1-6 (`docs/idtx_core/figures/`) are referenced from §3.x (P1-1, P1-2, P1-6), §6.8 (P1-3, P1-5), and
§2.6 (P1-4).

---

## Open items carried into the examiner pass (WP 1.10)
- The `[recalled]` analogy cells (OIDC, SAML, OCSP, LDAP/SCIM, MOBI VID external spec) must be read or dropped before final.
- G-B stays blocked until the archive is supplied.
- Pseudocode (G-D) awaits the author's line-by-line check.
- The EUDI/eIDAS FCAF cell rests on a secondary source (Sokolov 2026); chase the primary if the examiner presses.
