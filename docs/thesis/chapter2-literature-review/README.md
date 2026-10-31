# Chapter 2 — Literature Review (Working Draft)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Drafted:** 2026-10-22. **Supersedes:** the Chapter 2 stub of the same file, which held the planned
structure and the citation policy.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`, in particular rule 1.3.8 (ground claims in verified
sources, never in memory) and the project's standing rule that no citation is fabricated.

**About the sources.** Every work cited in this chapter is registered in one of two places. Keys
written as `[@KEY]` are defined in `docs/zkp/SOURCES_ZKP.md`, the verified register compiled for the
zero-knowledge and agent-identity work. Standards named with a section of `SOURCES.md` (for example
"ERC-1056, `SOURCES.md` §1") are the entries of the root source register. Keys written as
`[Author21, S7]` are prior academic works added to `SOURCES.md` §7 for this chapter; each was checked on
2026-10-22 against its DOI metadata record (title, authors, year and venue). Keys written as `[Author25, S8]` were added on 2026-10-31
(`SOURCES.md` §8), checked against Crossref or, without a DOI, against the opened PDF. This set is a working
set. The researcher's own reference set may extend or replace any of these sources before
submission, and where a claim still lacks a source it is marked `[SOURCE NEEDED: ...]` rather than
filled from memory.

**What the chapter does.** It positions the thesis in eight steps. Section 2.1 reviews self-sovereign
identity (SSI) and the World Wide Web Consortium (W3C) standards that make it interoperable. Section
2.2 reviews the Ethereum identity standards that serve as the nine comparison substrates. Section 2.3
reviews vehicle identity work, including the Mobility Open Blockchain Initiative (MOBI) Vehicle
Identity (VID) standard. Section 2.4 reviews vehicle-to-everything (V2X) security and the public key
infrastructure (PKI) baseline. Sections 2.5 and 2.6 review the two strands behind the extension
(RQ5, H6): zero-knowledge proofs with anonymous credentials, and the identity of software agents
that act on a principal's behalf. Section 2.7 positions the identity-dependent transaction (IDTx), the
notion the on-chain storage results rest on, against prior work. Section 2.8 states the gap the thesis fills, in the same terms as
Section 1.2.

---

## 2.1 Self-Sovereign Identity and the W3C Standards

### 2.1.1 From centralised to self-sovereign identity

Digital identity has moved through three broad models: centralised accounts held by each service,
federated identity in which a provider vouches for a user across services, and user-centric or
self-sovereign identity in which the subject holds its own identifiers and credentials
[@ALLEN2016; @MUHLE2018; Soltani21, S7]. Cameron's "Laws of Identity" set out the design pressure
early: identity systems should disclose only what a use needs and only to parties with a justified
need [@CAMERON2005]. Allen's essay gave the term "self-sovereign identity" its common meaning and
listed ten principles, among them existence, control, access, transparency, persistence,
portability, interoperability, consent, minimisation and protection [@ALLEN2016]. Tobin and Reed
tied that programme to distributed ledgers as a root of trust that no single operator controls
[@TOBIN2016].

These principles are not a settled definition. Ferdous, Chowdhury and Alassafi observed that the
literature held different notions of what SSI means, and gave the first formal, mathematical
treatment of its properties and of how they map onto the identity lifecycle [Ferdous19, S7]. Toth
and Anderson-Priddy validated nine properties of self-sovereignty proposed by earlier sources and
proposed five more [Toth19, S7]. The practitioner critique of web3 by Marlinspike, which observed that
almost all decentralised applications reach the chain through a few hosted providers [@MOXIE2022], is a reminder that "self-sovereign" is a
claim about control that a given architecture may or may not deliver. Wüst and Gervais give the
standard test for whether a blockchain is needed at all: it is justified when several mutually
distrusting writers must share state without a trusted third party [@WUST2018]. Vehicle identity, with
manufacturers, owners, registries, insurers and workshops writing to one record over a long life,
is a case that passes that test on its face; whether it passes it in practice is a design question
that this thesis treats empirically.

### 2.1.2 Surveys and taxonomies of SSI

A large survey literature now exists. Mühle et al. identified four essential components of
blockchain-based SSI (identifiers, authentication, verifiable claims and their storage) and
distinguished an *identifier registry model* from a *claim registry model* [@MUHLE2018]. That
distinction maps directly onto the substrates of Section 2.2: ERC-1056 is an identifier registry,
while ERC-735 and the CVIN-Combined hybrid also register claims. Čučko and Turkanović's systematic
mapping study found that solution proposals and validation research dominate the field and that
few studies examine usability or good practice [Cucko21, S7]. Schardong and Custódio produced a
systematic review and taxonomy [@SCHARDONG2022], Satybaldy, Ferdous and Nowostawski a taxonomy of
open challenges [Satybaldy24, S7], and Ahmed et al. a survey of blockchain identity management that
names authentication, integrity, privacy, trust and simplicity as essential components and reviews
adversarial threats [Ahmed22, S7]. Kuperberg compared blockchain identity products against
enterprise requirements, including mobility, overhead and standardisation [Kuperberg20, S7].
Mazzocca et al. survey DIDs and VCs beyond human SSI, including cloud, edge and Internet of Things
(IoT) entities, which is the class a vehicle belongs to [@Mazzocca25].

Two comparative studies are closest in form to this thesis, and both are qualitative. Nokhbeh Zaeem
et al. compiled functional and non-functional SSI requirements and compared a large set of SSI
solutions against them [NokhbehZaeem21, S7]. Pava-Díaz, Gil-Ruiz and López-Sarmiento compared nine
frameworks (Sovrin, uPort, Jolocom, ShoCard, Litentry, Civic, KILT, Idena and ION) for how far they
implement SSI principles [PavaDiaz24, S7]. Kondova and Erbguth compared Sovrin, uPort and Jolocom
for their implications under the General Data Protection Regulation (GDPR) [Kondova20, S7]. These
studies compare *platforms* by features and principles. None of them deploys the candidates on one
testbed and measures cost, latency and attack outcomes for an identical workload, which is the
method of this thesis (Chapter 3).

### 2.1.3 Decentralized Identifiers (DID Core v1.0)

The W3C Decentralized Identifiers (DIDs) v1.0 Recommendation defines a DID as "a globally unique
persistent identifier that does not require a centralized registration authority" [@DIDCore]
(`SOURCES.md` §2). A DID resolves to a DID document that lists verification methods (keys),
verification relationships (such as authentication and assertion), and service endpoints. The
specification separates the data model from the *DID method*, which defines how a particular
registry creates, reads, updates and deactivates DIDs. This separation is what allows an Ethereum
contract to serve as a DID registry: the `did:ethr` method, for example, reads the ERC-1056 registry
[@DIDCore] (ERC-1056, `SOURCES.md` §1). Chapter 4 describes the four methods the thesis resolves
(`did:ethr`, `did:nft`, `did:key` and the thesis's `did:mobi`), and Chapter 5 reports the measured
conformance.

Interoperability between methods is not automatic. Yildiz et al. define interoperability for SSI and
give a reference model of the components on which it depends, noting that different technical
stacks routinely fail to interoperate [Yildiz23, S7]. Buțincu and Alexandrescu discuss architectures for a DID
and SSI infrastructure and its storage layer [Butincu24, S7]. The thesis's resolver addresses one
narrow part of this problem: whether identities rooted in nine different contract designs can be
lifted to one W3C document model.

### 2.1.4 Verifiable Credentials (VC Data Model v2.0)

The W3C Verifiable Credentials Data Model v2.0 defines a verifiable credential as "a tamper-evident
credential whose authorship can be cryptographically verified" [@VCDM2] (`SOURCES.md` §2). It sets
out the roles of issuer, holder and verifier, the structure of credentials and presentations, and
the hooks for status (revocation) and proofs. Two properties matter most for vehicles. First, a
credential can be verified offline from the issuer's public key, without a call to the issuer at
verification time. Second, the model allows selective disclosure and presentations derived by
zero-knowledge proofs (Section 2.5). The first property is what Hypothesis H3 tests against the
V2V latency budget; the second is what the RQ5 extension builds on.

Neither DID Core nor the VC model says which ledger, if any, should anchor identifiers, keys and
revocation. That choice is left to methods and implementations. For vehicles, it is the substrate
question of this thesis.

### 2.1.5 SSI in transport and mobility

SSI has been proposed for several transport settings. Stockburger et al. elicited requirements for
cross-operator public-transport ticketing in Europe and built a low-fidelity SSI prototype
[Stockburger21, S7]. Kailus, Kern and Krauß replaced the PKI of ISO 15118 Plug-and-Charge
electric-vehicle charging with SSI credentials, implemented it, and analysed it formally with the
Tamarin prover [Kailus24, S7]. Parameswarath, Gope and Sikdar proposed a DID/VC-based
privacy-preserving authentication protocol for electric-vehicle charging [@Parameswarath22]. These
works show that SSI fits mobility services. They each adopt one identity stack; none compares
substrates. Section 2.3 returns to SSI applied to the vehicle itself.

---

## 2.2 Blockchain Identity Standards: the Nine Substrates

The Ethereum community has produced a family of standards that can each carry an identity. They were
written for different purposes, and their specifications describe interfaces, not costs or threat
resistance. This section reviews each substrate as specified, in the order of `SOURCES.md` §1, and
then the academic work that has measured any of them.

### 2.2.1 Identifier registries: ERC-1056

ERC-1056, the "lightweight identity" registry, keeps identity state minimal. An identity is any
Ethereum address; the registry records an owner and emits events for delegates and attributes, so
that a DID document is reconstructed by replaying logs rather than read from storage (ERC-1056,
`SOURCES.md` §1). It is the registry behind `did:ethr` [@DIDCore]. In Mühle et al.'s terms it is a
pure identifier registry [@MUHLE2018]. It is the thesis's minimal baseline in Hypothesis H1.

### 2.2.2 Token-based identity: ERC-721, ERC-1155 and LSP8

ERC-721 defines non-fungible tokens (NFTs): each token has a unique identifier and a single owner,
and transfer is a first-class operation (ERC-721, `SOURCES.md` §1). This makes it a natural model of a
vehicle as an owned, transferable asset, and several vehicle-lifecycle systems use it (Section
2.3.2). ERC-1155 is a multi-token standard in which one contract manages many token types, fungible
or not; restricted to non-transferable balances it can model credentials held by an identity, the
"soulbound" pattern (ERC-1155, `SOURCES.md` §1). LUKSO's LSP8 Identifiable Digital Asset is a
token standard for uniquely identifiable assets from the LUKSO standards family (LSP8, `SOURCES.md` §1). The token standards model *ownership* well and
*claims about* the vehicle less directly; how much that costs in gas and fidelity is part of RQ1
and H4.

### 2.2.3 Account and claim identity: ERC-725, ERC-725X/Y and ERC-735

ERC-725 defines a proxy account whose owner can execute calls and store arbitrary key-value data;
its later split into ERC-725X (a generic executor) and ERC-725Y (a generic data store) gives a full
smart-account identity (ERC-725 and ERC-725xy, `SOURCES.md` §1). ERC-735 (a draft) defines a claim
holder: third parties add signed claims about an identity on-chain, and verifiers check the
issuer's signature and the claim's presence (ERC-735, `SOURCES.md` §1). This is Mühle et al.'s claim
registry model [@MUHLE2018]. Košubienė and Masteika built an SSI system on the related ERC-734/ERC-735 pair
on the Sepolia testnet and reported functional alignment with the European Digital Identity
architecture while noting that privacy mechanisms such as zero-knowledge proofs would be needed for
full compliance [Kosubiene25, S7]. Košubienė and Masteika's study is the nearest
prior use of a claim-holder standard for regulated identity, and it measures one standard only.

### 2.2.4 Account abstraction: ERC-4337

ERC-4337 provides account abstraction without a consensus change: users submit "user operations" to
an alternative mempool, bundlers package them, and a singleton EntryPoint contract calls each
smart account's validation logic [@ERC4337] (ERC-4337, `SOURCES.md` §1). Validation logic is
programmable, so an account can implement guardian recovery, multi-key policies and spending
limits. For vehicle identity, this is the substrate that speaks most directly to key compromise and
recovery over a long service life (RQ2). Wang and Chen describe the mechanism, review accounts,
wallets and related standards, and give a qualitative security evaluation [WangChen23, S7]. Lin et
al. measured deployed ERC-4337 contracts on Ethereum mainnet and found that account creation and
basic transfers cost several times the gas of an externally owned account transaction, concluding
that gas cost remains an obstacle to adoption [Lin24, S7]. The thesis's ERC-4337 implementation is a
minimal representative (Section 1.5), so its figures are a lower bound on a full deployment.

### 2.2.5 Signing conventions: EIP-191 and EIP-155

Two further proposals do not define identities but shape every substrate. EIP-191 fixes the format
of signed data so that a signature over a message cannot be replayed as a transaction, and EIP-155
binds signatures to a chain identifier (EIP-191 and EIP-155, `SOURCES.md` §1). The thesis uses both to
domain-separate VC proofs and the MOBI attestation digest; the defect reported in Chapter 5, where
an attestation signature was stored but never verified on-chain, is a failure at exactly this
layer.

### 2.2.6 Measured work on these substrates

Academic measurement of these standards is sparse and piecemeal. Lin et al. measured ERC-4337 alone
[Lin24, S7]. Wang et al.'s Hades is a decentralised identity system for the Ethereum Virtual Machine
(EVM) with accountability and Sybil resistance, and reports gas for its own design against prior
systems [Wang23Hades, S7]. Vehicle-lifecycle systems report gas for one bespoke contract built on
ERC-721 or ERC-1155 (Section 2.3.2). Studies of gas cost drivers analyse contracts in general, not
identity standards. The search for this chapter found no study that implements several of these
identity standards for one workload and compares their gas, security and W3C conformance side by
side. The closest benchmark compares one Ethereum method, Ethr-DID, with DID methods on two other ledgers
for latency, cost and metadata leakage [Satybaldy25, S8]: a comparison across ledgers, not across Ethereum
standards `[SOURCE NEEDED: the researcher's own search should confirm the absence of a multi-standard Ethereum
identity benchmark; this draft's searches (Consensus, Crossref, web indexes; 2026-10-22 and 2026-10-31,
SOURCES.md §8) did not reach IEEE Xplore, ACM DL or Google Scholar directly]`.
That absence is the first half of the gap in Section 2.8.

| Substrate | Identity model | Native claims on-chain | Recovery story | Register entry |
|---|---|---|---|---|
| ERC-1056 | Identifier registry, event log | Attributes as events | Owner change | `SOURCES.md` §1 |
| ERC-721 | Owned unique token | No | Transfer | `SOURCES.md` §1 |
| ERC-1155 | Multi-token, soulbound use | Credential balances | None native | `SOURCES.md` §1 |
| LSP8 | Identifiable digital asset | Not specified here | None native | `SOURCES.md` §1 |
| ERC-725 | Proxy account with data | Key-value data | Owner change | `SOURCES.md` §1 |
| ERC-725X/Y | Smart account (executor + store) | Key-value data | Owner change | `SOURCES.md` §1 |
| ERC-735 | Claim holder | Signed third-party claims | Key management | `SOURCES.md` §1 |
| ERC-4337 | Abstracted smart account | Not specified | Programmable (guardians) | `SOURCES.md` §1, [@ERC4337] |
| CVIN-Combined | ERC-1056 identity + ERC-735 claims | Signed claims | Owner change | `SOURCES.md` §1 (this thesis) |

The table restates the specifications only. What each design costs and resists is a Chapter 5
result.

---

## 2.3 Vehicle Identity and Industry Standards

### 2.3.1 Blockchain for vehicle records

Blockchain proposals for vehicles began with the vehicle's *record*, not its identity. Brousmiche et
al. built a consortium-blockchain ledger for vehicle data and processes, motivated by odometer fraud
and by vehicle data spread across stakeholders who do not trust each other [Brousmiche18, S7].
Notheisen, Cholewa and Shanmugam used design science to build a prototype that trades vehicles as
real-world assets and keeps a tamper-evident history, and named scalability and privacy as the open
problems [Notheisen17, S7]. These works establish the multi-writer, long-lived record that Section
2.1.1 identified as the case for a ledger.

### 2.3.2 Vehicles as tokens

A second line represents the vehicle as a token. López-Pimentel et al.'s NFT-Vehicle is a
hierarchical smart contract on a modified ERC-721, with stakeholder methods validated against a
finite-state machine; they estimated the ether a vehicle's lifecycle would cost [LopezPimentel23,
S7]. Butera et al. stored vehicle history on-chain and used NFTs for a decentralised second-hand
market with ownership transfer on payment [Butera23, S7]. Das, Dasgupta and Biswas proposed a
blockchain-based vehicle identity management framework for intelligent transportation systems,
focused on the validity of the personal identification information behind an identity [Das23, S7].
Each of these picks one substrate and measures it alone. None asks whether a claim-holder or
event-log design would serve the same lifecycle better.

### 2.3.3 Self-sovereign identity for vehicles

A third line applies SSI to the vehicle. Terzi et al. integrated Hyperledger Indy SSI with a
Hyperledger Fabric network to certify vehicle emissions [@Terzi20], and in follow-up work used SSI
and blockchain to decentralise identity management and vehicle-rights delegation among owners,
drivers and workshops, with feasibility measurements [Terzi21, S7]. Zeydan et al. proposed an SSI
methodology for vehicular networks and compared SSI-based and NFT-based blockchain solutions
qualitatively [Zeydan23, S7]. Li et al.'s BDRA uses DIDs for decentralised registration and
authentication in vehicular ad hoc networks (VANETs) [@LiBDRA23]. Feng et al.'s BPAS uses a
blockchain to support privacy-preserving VANET authentication with conditional tracing and
revocation [@Feng20]. AlMarshoud, Kiraz and Al-Bayatti review decentralised trust management in
VANETs against PKI and SCMS approaches [@AlMarshoud24].

Zeydan et al.'s SSI-versus-NFT comparison is the closest prior comparison of substrates for vehicles,
and it is qualitative and covers two families [Zeydan23, S7]. No work in this line was found that
compares more than two families of substrate, or that measures them.

### 2.3.4 MOBI Vehicle Identity (VID I and VID II)

MOBI is an industry consortium of manufacturers and mobility firms. Its VID standard, announced in
2019 with a working group chaired by Groupe Renault and Ford, gives a new vehicle a
blockchain-anchored "birth certificate" tied to its Vehicle Identification Number (VIN) [@MOBI-VID]
(MOBI VID I, `SOURCES.md` §3), now published as technical specification VID0002/TS/2024, version 2.0.
VID II extends the model to lifecycle events; the thesis implements
eleven event types and a multi-party attestation model from it; its public document is the use-case
and business-requirements specification VID0003/UC/2021, version 1.3, while the reference implementation
architecture (VID0004/RI/2024) is open to MOBI members only (MOBI VID II, `SOURCES.md` §3). The thesis has
not yet mapped its profile clause by clause against these documents, so it claims its MOBI profile is
"checked against" the VID model as described, not "compliant" with it (rule 1.2.2 of the style guide).

What matters for this review is the shape of the standard. MOBI VID specifies *what* a vehicle
identity contains and *how its lifecycle is structured*. It does not prescribe the substrate. The
academic literature found here contains no evaluation of MOBI VID across blockchain backends. The nearest
work is the author's own earlier design of MOBI VID on Hyperledger Indy and Aries, which proposed an
evaluation but reported no measurements [Prakash20, S8]; other papers found cite the standard without
implementing it. Hypothesis H4 tests
exactly that portability.

---

## 2.4 V2X Security and the PKI Baseline

### 2.4.1 Standards: IEEE 1609.2, IEEE 1609.2.1 and SAE J2735

V2X safety applications exchange messages defined by SAE J2735, notably the Basic Safety Message
broadcast by every equipped vehicle (SAE J2735_202409, issued 2024-09-15, `SOURCES.md` §3). Those messages are signed and
verified under IEEE 1609.2, which defines the secure message formats and certificate formats,
including pseudonym certificates; its 2022 edition supersedes the 2016 edition and its amendments
[@IEEE1609.2] (IEEE 1609.2, `SOURCES.md` §3). The companion IEEE 1609.2.1 standard specifies
certificate management, including certificate request, issuance and revocation [@IEEE1609.2;
ChenSCMS23, S7]. The
register marks the IEEE entry partial because the IEEE page could not be fetched; clause-level
statements about 1609.2 should cite the standard text.

### 2.4.2 The Security Credential Management System

The PKI that implements these standards in North America is the Security Credential Management
System (SCMS). Whyte et al. proposed it for V2V communications, with butterfly key expansion and
short-lived pseudonym certificates so that no single component can link a vehicle's certificates
[@Whyte13]. Brecht et al. give the full design developed by the Crash Avoidance Metrics Partners
under a cooperative agreement with the United States Department of Transportation: four use cases
(bootstrapping, certificate provisioning, misbehaviour reporting and revocation), a split of
certificate generation across organisations for privacy, and efficient revocation of many
pseudonym certificates per vehicle as the main challenge [@Brecht18]. Raya and Hubaux set the
earlier foundation of VANET security on large sets of anonymous keys [@RayaHubaux07], and Petit et
al.'s survey covers pseudonym schemes and their linkability limits [@Petit15].

The SCMS has been analysed and measured. Simplicio et al. described and fixed two birthday attacks
on its revocation process and proposed removing the linkage authorities [Simplicio21, S7]. Barreto
et al. showed that the butterfly-key provisioning is vulnerable to existential forgery under certain
conditions and proposed a Schnorr-based implicit certification fix [Barreto21, S7]. Chen et al.
implemented an SCMS and end entities to IEEE 1609.2 and 1609.2.1 and timed each action to find
bottlenecks [ChenSCMS23, S7], and compared the North American (IEEE 1609.2.1) and European (ETSI TS
102 941) credential management systems in implementation [ChenCompare24, S7]. Haidar, Kaiser and
Lonc measured certificate reloading on a vehicular PKI proof of concept and found the end-to-end
latency between vehicle and PKI non-negligible [Haidar17, S7].

### 2.4.3 Decentralised alternatives within V2X

Recent work moves parts of the PKI's role to the vehicle or to a ledger. Cai et al.'s PSP lets
vehicles generate and bind pseudonyms from an anonymous credential without a central authorisation
authority, with selective disclosure, one pseudonym per epoch against Sybil attacks, and tracing
for accountability [Cai25, S7]. Blockchain-assisted VANET authentication schemes [@Feng20;
@LiBDRA23] and the anonymous-credential schemes of Section 2.5 belong to the same move.

### 2.4.4 What the baseline means for this thesis

The thesis uses the IEEE 1609.2-style PKI as its V2V latency baseline (Chapter 3). The literature
supports two observations that frame that comparison. First, PKI verification of a signed message
is fast; the cost of the PKI lies in provisioning, linkage and revocation, which the literature
treats as the hard problems [@Brecht18; Simplicio21, S7; Haidar17, S7]. Second, SSI does not remove
those problems; it relocates trust anchoring and revocation to a ledger and to the holder. A fair
comparison therefore times the per-message path of both, which is what RQ4 measures, and treats the
provisioning and revocation story as a security question (RQ2), not a latency one. No prior work
found here places SSI credential verification and PKI verification in the same simulated V2V
message path. The closest work uses verifiable credentials for C-V2X authentication and compares their
overhead with other blockchain schemes, not with IEEE 1609.2 [Borges25, S8] `[SOURCE NEEDED: confirm by the
researcher's own search; coverage to date in SOURCES.md §8]`.

### 2.4.5 Revocation freshness: the cost of knowing

A verifier that accepts a message must decide whether the sender's credential is still good. Every revocation scheme
answers the same question in a different place on one trade: how much the verifier pays per check against how long a
revoked credential keeps working.

*Merged on 2026-10-22 from the companion draft of 2026-10-20; citation keys `[A-*]` and `[F-*]` are listed in
Section 2.9.*

**The PKI debate.** Rivest asked whether certificate revocation lists could be eliminated in favour of other
mechanisms and answered that in most cases they could [F-S01]. McDaniel and Rubin replied that the right mechanism
depends on the environment, and proposed revocation on demand, a CRL-based scheme that still gives timely
information [F-S02]. OCSP settled the online side of the argument: a status response carries `thisUpdate` and
`nextUpdate`, and the relying party judges them against its own clock [F-S03]. That judgement in the verifier's time
is the same question the testbed met as defect D51, where a verifier's clock, not the chain's, decided whether a key
was still valid (`docs/DEFECT_LOG.md`). Measurement of the web's PKI found both that revocation is common (8 % of
served certificates in one scan set) and that fetching status is often expensive enough that clients skip it
[F-S05]. CRLite's answer was to change the direction of the traffic: push a compact aggregate of all revocations to
every client on a period, so the per-check cost is local and the staleness is a time bound set by the update period
[F-S04].

**Vehicular revocation.** The V2X security credential management system enforces revocation by periodically
distributing a CRL that devices use to reject messages from revoked senders [F-S06; @Brecht18]; an earlier vehicular scheme
showed such lists reaching a region within minutes over road-side units at a few kilobits per second [F-S07]. Both
are push schemes with a time bound. The testbed's verifier is a pull scheme with a message bound: it re-reads the
sender's state every k messages, so a revoked sender is accepted for at most k − 1 further messages (#46, #32). The
guide's rule 1.1.9 that a message bound is not a time bound is the difference between these two families, stated
once.

**The credential layer's own parameter.** The W3C status method for verifiable credentials expresses freshness as a
time to live in milliseconds, optional and without a default, and tells verifiers to cache the status list [F-S08,
F-S09]. A W3C verifier therefore has a time bound available in the credential itself; whether to honour it is a
verifier policy, which is exactly what this thesis measures.

**Caches and polled copies as the formal setting.** HTTP caching gives the vocabulary: a response is fresh while its
age has not exceeded its freshness lifetime [F-S11]. The hit rate of a TTL cache has a closed form when request
inter-arrivals are independent [F-S10], and the freshness of a polled copy of a source that changes as a Poisson
process decays as e^(−λt) between polls [F-S12]. The verifier is the copy and the chain is the source; the chain-read
cost per poll is the testbed's t_chain and the budget is the V2V latency budget.

**Age of information.** The vehicular networking literature introduced age of information for status messages and
showed the optimum lies between maximum throughput and minimum delay [F-S13]; the survey frames timeliness at a
monitor under a resource budget [F-S14]; and the age of incorrect information refines it to penalise only the time
the monitor's copy is wrong [F-S15]. Revocation exposure has that last shape: a cached identity state is harmless
until a revocation makes it wrong. The Phase 2 brief on freshness theory derives, in that frame, the cache setting
that is freshest within a capacity budget and an exposure cap, k_min = ceil(t_chain / (B − t_local)), and shows why
the measured knee moves between hosts: its sensitivity to t_local is t_local / (B − t_local)
(`docs/phase2/briefs/I-05_FRESHNESS.md` §7). That derivation is a prediction, not a result; the measurement that
tests it is a Phase 2 item.

**What this thesis adds.** The prior work states the trade in time and measures it for web and V2X PKI. This thesis
measures it for a chain-read verifier in message units on one testbed (#32, #37), reports the k − 1 bound as it fell
in 280 of 280 trials (#37), and shows with a same-host re-run that the absolute knee is a property of the host, not
of the policy (#52).

---

## 2.5 Zero-Knowledge Proofs and Anonymous Credentials

This section supports the extension (RQ5, H6). It is brief on theory and concentrates on what has
been deployed and measured for identity and vehicles.

### 2.5.1 Foundations

Goldwasser, Micali and Rackoff introduced zero-knowledge interactive proofs, in which a verifier
learns nothing beyond the truth of a statement [@GMR85; @GMR89]. Goldreich, Micali and Wigderson
showed that every language in NP has a zero-knowledge proof system [@GMW91]. The Fiat-Shamir
heuristic turns interactive proofs into non-interactive ones [@FS86; @BR93], and Schnorr's
identification protocol is the canonical efficient example [@Sch89; @Sch91]. Thaler's monograph
gives a modern treatment [@Thaler22].

### 2.5.2 Succinct proofs and their tooling

Succinct non-interactive arguments of knowledge (SNARKs) make verification cheap regardless of the
size of the statement. Pinocchio made them nearly practical [@PHGR13; @GGPR13], and Groth's 2016
construction remains the smallest pairing-based proof in common use [@Groth16]. Universal-setup
systems such as PLONK and Marlin reduce the trusted-setup burden [@PLONK19; @Marlin20], and
transparent systems such as STARKs and Bulletproofs avoid it [@STARK18; @BBBPWM18]. For Ethereum,
the alt_bn128 precompiles make pairing checks affordable on-chain [@EIP196; @EIP197; @EIP1108], and
Circom with snarkjs is a widely used toolchain [@Circom23; @snarkjs]. Guo et al. benchmark
ZK-friendly hash functions and proving systems for EVM chains [@GuoBench24], and Ernstberger et al.
provide a toolset for comparing SNARKs [@zkBench23].

### 2.5.3 Anonymous credentials and selective disclosure

Anonymous credentials let a holder prove possession of a credential, and selected facts about its
attributes, without revealing the rest and without being linkable across showings. Camenisch and
Lysyanskaya's system and signature scheme are the foundation [@CL01; @CL02], implemented in IBM's
Idemix [@Idemix02] and, in the self-sovereign world, in Hyperledger AnonCreds, which supports
predicates such as "age over 18" without revealing a date of birth [@AnonCreds]. BBS signatures
[@BBS04] are being standardised at the IRTF [@BBS-IRTF] and as a W3C Data Integrity cryptosuite
that gives selective disclosure and unlinkable derived proofs for VCs [@VC-BBS]. Salted-hash
selective disclosure, as in SD-JWT and the ISO mobile driving licence, is simpler but is not zero
knowledge and is linkable across presentations unless credentials are batch-issued [@RFC9901;
@ISO18013-5]. zk-creds builds anonymous credentials from general-purpose SNARKs over existing
documents [@zkcreds23], and Frigo and shelat prove statements over existing ECDSA-signed mobile
documents [@FrigoShelat24]. On the deployment side, the iden3 protocol and Privado ID use circuits
over Merkle-tree identity state [@iden3; @PrivadoID], and the EU Digital Identity Wallet
architecture now carries a zero-knowledge topic and technical specifications [@EUDI-ARF].

ZK-based SSI has its own academic line: Yang and Li's BZDIMS [@Yang20], Dieye et al.'s
discrete-log SSI protocol [@Dieye23], and zkSSI, which supports compound predicates over VCs and
compares itself with Polygon ID and zk-creds [@zkSSI24].

### 2.5.4 Zero knowledge for vehicles

Vehicle-specific work splits into authentication schemes and record-privacy schemes. Rasheed et al.
proposed group-based ZKP authentication for VANETs with tunable privacy [@Rasheed20]. Shahrouz and
Analoui use simulation-extractable zk-SNARKs and note that proof generation time "poses a major
obstacle" in time-sensitive VANETs [@Shahrouz24]. Jiang and Lv use non-interactive Schnorr proofs for
vehicle-to-roadside authentication [@Jiang24], Zhang et al. and Chen et al. combine zk-SNARKs with
blockchain for anonymous VANET authentication [@Zhang24; @Chen25], and Li et al. aggregate proofs for
autonomous truck platooning [@LiPlatoon23]. Liu et al.'s ATRC and Zhang et al.'s threshold scheme
give vehicles anonymous, traceable and revocable credentials [@Liu24ATRC; @ZhangTIFS25]. Hasan et
al.'s Hermes' Seal proves properties of autonomous-vehicle perception computations in zero knowledge
[@Hasan26].

The measured timings in this line vary by orders of magnitude with the proof system, the circuit and
the hardware, and they are reported for each scheme on its own terms. That variation is why the
extension asks *where* in the vehicle's life zero knowledge fits (registration, session, or each
message) rather than whether it is fast in general. H6 predicts registration and session but not
per-message use; the pre-registered expectations Z-E1..Z-E7 test that prediction (Chapter 3).

---

## 2.6 Agent Identity and Delegation

This section supports the second half of H6: that operating zero-knowledge identity safely needs a
bounded, adaptive custodian, and that the custodian's own trust should rest on the same
decentralised identity stack. The literature here is young; most of it is from 2024 to 2026.

### 2.6.1 Why software agents need identity

Chan et al. argue that AI systems acting in the world need identifiers that let counterparties know
what they are dealing with, and that visibility into agents (identifiers, real-time monitoring and
activity logs) is a precondition for governing them [@CHAN2024-IDS; @CHAN2024-VIS]. South et al. argue
that agents need *authenticated delegation*: a verifiable link from a human principal to the agent,
with scoped permissions, and they propose extending existing authorisation standards for it
[@SOUTH2025]. The OpenID Foundation's community group report surveys authentication and
authorisation for agentic systems and the open problems of delegation chains [@OIDF2025]. Industry
protocols for connecting agents to tools and to each other now carry their own authorisation
sections [@MCP-AUTH; @A2A2025], and payment networks have launched agent-payment programmes that
depend on knowing which agent acts for which customer [@MASTERCARD-AGENTPAY; @VISA-VIC].

### 2.6.2 Delegation on-chain

On Ethereum, delegation is already a substrate feature. ERC-1056 has native delegates
(`SOURCES.md` §1), and ERC-4337 accounts can encode which actions a delegated key may take
[@ERC4337]. Gorzny, Soureshjani and Derka propose account-abstraction smart wallets as the mechanism
that lets a user delegate some but not all actions to an AI agent, with the user's requirements
encoded in contract logic [Gorzny25, S7]. This places the agent-identity problem on the same
substrates that Section 2.2 compares, which is the link the extension exploits.

### 2.6.3 Agent security and the custodian

The main threat to an agent that holds credentials is that its inputs can direct it. Greshake et al.
demonstrated indirect prompt injection against applications built on large language models
[@GRESHAKE2023], and the OWASP project ranks prompt injection first among risks for such
applications [@OWASP-LLM01]. AgentDojo provides a benchmark of attacks and defences for agents
[@AGENTDOJO2024], and design-by-construction defences separate the component that reads untrusted
data from the one that holds authority [@WILLISON2023; @DEBENEDETTI2025; @BEURERKELLNER2025].
Subbabhatta Gopalakrishna measures zero-knowledge predicate proofs exchanged between agents across
protocols and names a "source-integrity gap": a valid proof says nothing about whether its inputs
were genuine [@ZKGATEWAY2026].

For the thesis, these works justify treating the custodian as a bounded component under test, not as
a trusted oracle. The custodian's honest-service level was pre-registered, and Chapter 5 reports it
as failed (Z-E6). The nearest measured baseline is a performance evaluation of an SSI software stack (walt.id) on a
Raspberry Pi 4 standing in for an embedded device, which reports latency, CPU, memory and scalability
[Buran25, S8]. It measures the wallet and issuer services, not an automated custodian acting for a vehicle,
so the literature reviewed here still offers no measured baseline for a credential custodian in a vehicle
setting.

## 2.7 The Identity-Dependent Transaction, Positioned

**Definition.** This thesis uses one definition, adopted from the academic review of its Phase 2 packages
(`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md` §3.3): an identity-dependent transaction (IDTx) is a transaction whose
admissibility or effect is a function of the state of an identity that the transaction names, evaluated during
execution from ledger state or from an attestation the transaction carries and verifies; authentication of the
sender and administration of the identity record itself are excluded. An off-chain decision with the same dependency,
such as a verifier accepting a message, is an identity-dependent decision, which shares the freshness dimension but is
not a transaction.

**The mechanism is prior art, and the thesis says so.** A transaction that re-checks a condition on current state
before it takes effect is the guarded transaction of Luu et al., who proposed that a transaction carry a guard g and
be dropped if the current state does not satisfy it [A-S01]. A transfer that executes only if the *receiver* holds
the required identity claims from trusted issuers is standardised in ERC-3643, whose `isVerified` runs inside
`transfer`, `transferFrom`, `mint` and `forcedTransfer` [A-S09]. Under the definition above, a T-REX transfer is an
IDTx: its admissibility depends on a named identity other than the sender. The thesis therefore does not claim the
mechanism. It claims a taxonomy and a measurement.

**What access control already covers.** Attribute-based access control evaluates attributes of the subject, the
object, the operation and the environment against policy [A-S05]. "The predicate is about the named identity, not the
caller" is ABAC with the named identity as object; it does not distinguish an IDTx from ABAC. The distinction rests on
the ledger-specific axes: where the identity state is held (storage locus), how it is encoded, when it is evaluated,
and how fresh it is. Role modifiers in contract libraries gate on the caller [A-T01] and are the excluded case.

**Why the storage locus is an axis.** The standards (Section 2.2) constrain each cell separately. ERC-1056 keeps attributes in
events, which the standard itself says are stored "exclusively for off-chain use", and exposes `validDelegate` as a
view [A-S06]: an attribute is not a contract-readable dependency, a delegation is. This thesis measured the
consequence across nine standards: what each stores, what each emits, and what a resolver must do to read it back
(#49, #51), and what the cheapest standard's history costs a reader at depth 50 (#31). `eth_getProof` gives storage a
proof form for off-chain verification but covers storage, not logs [A-S10]; a historical block-hash service bounds how
old a block can be for a contract to check a carried proof against it [A-S11]. The oracle literature frames the
carried-attestation locus: a contract sees only data already on chain or fed into it, and an oracle mediates the rest
[A-S12]. Zero-knowledge credential on-chaining gives the committed locus a published design for a hidden attribute
[A-S13]; a vehicle-domain system that has a contract verify issuer and holder signatures against another ledger is the
closest prior deployment, framed by neither locus nor freshness [A-S14].

**Why the evaluation point is an axis.** Account abstraction evaluates a user operation's validity against mutable
state, and its standard introduces simulation because another operation can change that state before inclusion
[A-S07]; its validation-scope rules limit what storage a validation may read, so that an account's validation cannot
read a registry slot keyed by another identity while a staked paymaster can [A-S08]. Admission-time evaluation of a
named identity's state is therefore constrained by a standard, not only by cost, and the thesis prices the EntryPoint
indirection it implies (+46,830 gas per operation, #25).

**Why freshness is an axis, and the race.** The dependency between an identity change and a transaction that
depends on it is a transaction-ordering dependence: the final state depends on the order the block builder chooses
[A-S01], a class measured in the wild as front-running [A-S02] and catalogued with its mitigations [A-S03]. In
software terms it is a time-of-check-to-time-of-use flaw: a check, then an action that assumes the check still holds
[A-S04]. Phase 1 holds the off-chain half of this race in message units (#32, #37, #46) and the credential layer's
time-to-live in time units [A-S15]; the on-chain half, the exposure window of an identity dependency, is not measured
by any fetched source and is the Phase 2 experiment E-F1-3 (`docs/phase2/focus/F1_onchain_storage_idtx/PLAN.md`).

**What is new, stated narrowly.** No fetched source names "identity-dependent transaction" or defines it; the
search was open-web only, so this is a negative result, not proof of absence (`docs/phase2/briefs/I-24_IDTX.md`
§3.4). What the thesis adds is: one definition that separates the dependency on a named identity from sender
authentication and identity administration; a four-axis taxonomy (locus, encoding, evaluation point, continuation)
into which the nine standards and the testbed's gates are classified from existing evidence (4 of 26 Phase 1 gates
qualify, `docs/phase2/reviews/DISPOSITIONS_F1-F3.md`); and the measured cost of each storage locus on one testbed. The
claim stops there. Whether the taxonomy earns a paper depends on E-F1-2 and E-F1-3, after the defence (scope decision
D-7).

---

## 2.8 The Research Gap

The review supports the gap stated in Section 1.2, and sharpens it in four parts.

**1. Substrates have been proposed and measured in isolation.** Section 2.2 found specifications for
nine identity designs and measurements of at most one at a time [Lin24, S7; Wang23Hades, S7].
Section 2.3 found vehicle systems that each adopt one substrate, ERC-721 or ERC-1155 or Hyperledger
Indy, and measure it alone [LopezPimentel23, S7; Butera23, S7; Terzi21, S7]. The comparative SSI
studies compare platforms by features and principles, not by measured cost or attack outcomes on an
identical workload [NokhbehZaeem21, S7; PavaDiaz24, S7; Kuperberg20, S7], and the one
vehicle-specific comparison of substrates is qualitative and covers two families [Zeydan23, S7].

**2. The industry standard leaves the substrate open.** MOBI VID specifies the content and lifecycle
of a vehicle identity but not which ledger design should carry it (Section 2.3.4). No academic
evaluation of its portability across backends was found.

**3. SSI and PKI have not been timed in the same V2X message path.** The PKI literature measures
provisioning, linkage and revocation [@Brecht18; ChenSCMS23, S7; Haidar17, S7]; the SSI-for-vehicles
literature measures its own protocols (Section 2.3.3). Neither places W3C credential verification
beside IEEE 1609.2-style verification under one latency budget.

**4. Zero-knowledge vehicle identity is studied per scheme, and its operation is not studied.**
Section 2.5.4 found many vehicle ZK schemes, each timed on its own terms, and Section 2.6 found that
agent and custodian security is studied for general software agents but not for a custodian of
vehicle credentials.

**What the thesis contributes against this gap.** It applies the same vehicle-identity operations,
the same threat model and the same W3C compliance checklist to nine substrates and the MOBI VID V2
profile, and reports measured gas, verification latency and attack outcomes (RQ1 to RQ4, H1 to H5).
It then tests where zero knowledge fits in that stack and what operating it requires (RQ5, H6). The
claim that this comparison is the first of its kind rests on the searches reported here; it is
stated as "to the author's knowledge" in Chapter 1, and the `[SOURCE NEEDED]` markers above mark the
searches the researcher should confirm before submission.

---

## 2.9 Citation keys of Sections 2.4.5 and 2.7

Keys written as `[A-*]` and `[F-*]` refer to sources fetched at their origin and quoted in
`docs/phase2/briefs/I-24_sources.json` (keys A-*) and `docs/phase2/briefs/I-05_sources.json` (keys F-*);
each key maps to the brief's id below.

| Key | Brief id | Short form |
|---|---|---|
| A-S01 | I-24 S01 | Luu et al., Making Smart Contracts Smarter, CCS 2016 |
| A-S02 | I-24 S02 | Daian et al., Flash Boys 2.0, arXiv:1904.05234, 2019 |
| A-S03 | I-24 S03 | Eskandari, Moosavi, Clark, SoK: Transparent Dishonesty, FC 2019 |
| A-S04 | I-24 S04 | Bishop and Dilger, Checking for Race Conditions in File Accesses, Computing Systems 1996 |
| A-S05 | I-24 S05 | Hu et al., NIST SP 800-162, 2014 (updated 2019) |
| A-S06 | I-24 S06 | ERC-1056, Ethereum Lightweight Identity |
| A-S07 | I-24 S07 | ERC-4337, Account Abstraction Using Alt Mempool |
| A-S08 | I-24 S08 | ERC-7562, Account Abstraction Validation Scope Rules |
| A-S09 | I-24 S09 | ERC-3643, T-REX |
| A-S10 | I-24 S10 | EIP-1186, eth_getProof |
| A-S11 | I-24 S11 | EIP-2935, Serve historical block hashes from state |
| A-S12 | I-24 S12 | Eskandari et al., SoK: Oracles, ACM AFT 2021 |
| A-S13 | I-24 S13 | Heiss et al., Non-Disclosing Credential On-chaining, arXiv:2209.09584, 2022 |
| A-S14 | I-24 S14 | Naghmouchi, Kaffel, Laurent, arXiv:2201.00231, 2022 |
| A-S15 | I-24 S15 | W3C Bitstring Status List v1.0, 2025 |
| A-T01 | I-24 T01 | OpenZeppelin Contracts 5.x, Access Control |
| F-S01 | I-05 S01 | Rivest, Can we eliminate certificate revocation lists?, FC '98 (abstract only; not re-verifiable from the build container) |
| F-S02 | I-05 S02 | McDaniel and Rubin, A Response to ..., FC 2000 (abstract only; same note) |
| F-S03 | I-05 S03 | RFC 6960, OCSP, 2013 |
| F-S04 | I-05 S04 | Larisch et al., CRLite, IEEE S&P 2017 |
| F-S05 | I-05 S05 | Liu et al., An End-to-End Measurement of Certificate Revocation, IMC 2015 |
| F-S06 | I-05 S06 | Brecht et al., A Security Credential Management System for V2X, arXiv:1802.05323, 2018 |
| F-S07 | I-05 S07 | Papadimitratos, Mezzour, Hubaux, CRL Distribution in Vehicular Communication Systems, VANET 2008 |
| F-S08, F-S09 | I-05 S08, S09 | W3C Bitstring Status List v1.0, 2025 (ttl; validation) |
| F-S10 | I-05 S10 | Jung, Berger, Balakrishnan, Modeling TTL-based Internet Caches, INFOCOM 2003 |
| F-S11 | I-05 S11 | RFC 9111, HTTP Caching, 2022 |
| F-S12 | I-05 S12 | Cho and Garcia-Molina, Synchronizing a database to Improve Freshness, 1999 preprint |
| F-S13 | I-05 S13 | Kaul et al., Minimizing Age of Information in Vehicular Networks, SECON 2011 (venue from the author's CV) |
| F-S14 | I-05 S14 | Yates et al., Age of Information: An Introduction and Survey, arXiv:2007.08564, 2020 |
| F-S15 | I-05 S15 | Maatouk et al., The Age of Incorrect Information, arXiv:1907.06604, 2019 |

**Not cited, because not read at origin:** IEEE 1609.2 itself, Status List 2021, Kaul et al. INFOCOM 2012, the
published versions of the arXiv items, Rivest's full text, and the scholarly-database search for the term (see the
briefs' §8). These are the first items for the author's reference set.

---

*Working draft. Sections 2.4.5 and 2.7 cite measured results of the thesis only by their register rows
(`#NN`, status V); every result is reported in Chapter 5 with its register row.*
