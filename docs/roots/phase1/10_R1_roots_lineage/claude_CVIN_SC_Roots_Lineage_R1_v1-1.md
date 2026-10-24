# Roots Lineage R1 — The Layered History of the Technologies That Enable Bitcoin, Blockchains, Secure I2I Communication and Decentralised Identity

**Reference report · v1.1 · 2026-09-15 · CVIN-SC Research Programme · Thread G-R1 (provisional), document R1**
**Companion visual:** `claude_CVIN_SC_Roots_Lineage_R1_v1-1.svg` (eight layers, two timeline columns)
**Supersedes:** `Bitcoin_Technology_Lineage_Report_v1-0.md` (L0–L5 content carried unchanged; §§10–11 and the L6/L7 rows are new). Tags `T-01`–`T-24` are frozen from v1.0; identity-lineage tags `T-I01`–`T-I22` are assigned here.

---

## 0. Purpose and how to use this document

Bitcoin (2008–09) did not invent a single new primitive. Its contribution was *composition*: it assembled roughly forty years of prior work in cryptography, distributed systems, and digital-cash design into one system that solved a problem none of its predecessors had — decentralised, double-spend-resistant electronic cash without a trusted issuer.

This report organises that prior work as a layered stack, bottom to top. v1.0 stopped at Bitcoin (**L0–L5**). v1.1 adds the two layers the programme actually works in — **L6 identity** and **L7 application / I2I** — and the second lineage that feeds them: the forty years of authentication, secure-channel, and privacy-cryptography work that ran in parallel to the digital-cash lineage and converged with it in decentralised identity. Each layer is enabled by the layer beneath it and secured by it. When a later document needs to say "function X is secured by Y", the layer identifiers (**L0–L7**) and the dated technology identifiers (**T-xx**, **T-Ixx**) can be cited directly.

| Layer | Name | What it provides | Secured by |
|---|---|---|---|
| **L0** | Communication substrate | Nodes can find and talk to each other | Physical network; not cryptographic |
| **L1** | Cryptographic primitives | Hashing, signatures, key pairs | Mathematical hardness assumptions |
| **L2** | Authenticated data structures | Tamper-evident ordering and membership | L1 (collision resistance) |
| **L3** | Distributed agreement | Many mutually distrusting nodes agree on one history | L2 + L4 |
| **L4** | Economic / anti-abuse mechanisms | Cost to participate; incentive to behave | L1 (preimage resistance) + game theory |
| **L5** | Digital-cash design (ledger semantics) | Ownership, transfer, ordering, and the no-double-spend rule; generalises to "state transition with a global order" | L1–L4 together |
| **L6** | Identity | Binding a key to a subject; proving control; delegation; credential issue / present / verify / revoke; recovery | L1 (signatures, ZKP), L2 (registries, accumulators), L5 (ordered, non-equivocable state) |
| **L7** | Application / I2I | Authenticated, confidential, ordered exchange of messages and transactions between two identified endpoints | L6 (who), L1 (channel crypto), L0 (transport) |

Bitcoin sits at the top of L5 as the first system where L0–L5 close into a working loop. Decentralised identity sits at L6 and reuses that loop as its *registry*; the I2I channel at L7 reuses L6 as its *authentication* and L1 as its *confidentiality*. The identity lineage (§10) supplies what the cash lineage never needed: attribute binding, selective disclosure, unlinkability, and revocation.

---

## 1. Layer L0 — Communication substrate

### T-01 · Packet-switched internetworking (TCP/IP, 1974–1983)
Cerf and Kahn's 1974 paper *A Protocol for Packet Network Intercommunication* and the 1983 ARPANET cut-over to TCP/IP provided a global, best-effort, sender-agnostic transport. Bitcoin's networking layer is deliberately primitive: unencrypted TCP on port 8333, with no reliance on any transport-layer security. This is a design choice — the system must survive on a hostile, untrusted network, so all security is pushed up into L1–L4.

### T-02 · Peer-to-peer overlay networks (1999–2002)
- **Napster (1999)** — file-sharing with a central index; demonstrated demand and legal fragility of a central point.
- **Gnutella (2000)** — fully decentralised flooding/gossip; no central index at all. Bitcoin's transaction and block propagation is essentially a Gnutella-style gossip flood.
- **BitTorrent (2001)** — Bram Cohen's protocol introduced *tit-for-tat* incentive design: peers that upload get better download. First widely deployed system to make a P2P network self-sustaining through incentives rather than altruism. Direct conceptual ancestor of Bitcoin's incentive layer (L4).
- **Kademlia (2002)** — Maymounkov and Mazières' DHT gave structured, provably efficient peer discovery. Bitcoin does not use a DHT (it uses DNS seeds and address gossip), but Kademlia established that large open networks could self-organise without coordination.

### T-03 · The Sybil problem (Douceur, 2002)
John Douceur's paper *The Sybil Attack* proved that in an open network without a trusted identity authority, one entity can present arbitrarily many identities, so any "one node, one vote" scheme is defeated. This is the central obstacle Bitcoin had to overcome, and it explains *why* proof-of-work exists: it replaces "one identity, one vote" with "one CPU, one vote" — voting weight bound to a scarce physical resource rather than to identities.

**Evolution after Bitcoin:** Bitcoin later added BIP 150/151 (encryption proposals, not adopted), BIP 324 (v2 encrypted transport, 2023), compact blocks (BIP 152), Erlay (bandwidth-efficient relay), and Tor/I2P peer support. Ethereum adopted a Kademlia-derived discovery protocol (discv4/discv5) and the libp2p stack.

---

## 2. Layer L1 — Cryptographic primitives

### T-04 · Public-key cryptography (1976–1978)
- **Diffie–Hellman (1976)** — *New Directions in Cryptography* introduced the public/private key split and key exchange. (GCHQ's Ellis, Cocks and Williamson had discovered equivalent ideas in 1969–73, declassified 1997.)
- **RSA (1977, published 1978)** — Rivest, Shamir, Adleman: the first practical public-key system supporting both encryption and **digital signatures**. The signature is the concept Bitcoin actually needs: a coin is spent by producing a signature that only the private-key holder can produce.

### T-05 · Digital signatures as a formal object (1976–1988)
Diffie and Hellman named the concept; Goldwasser, Micali and Rivest (1988) gave the security definition still used today (existential unforgeability under chosen-message attack). This is the formal guarantee behind "only the owner can spend".

### T-06 · Elliptic-curve cryptography (1985) and ECDSA (1992–2000)
Koblitz and Miller independently proposed elliptic curves for public-key crypto in 1985 — same security as RSA with far shorter keys and signatures. ECDSA was proposed by Vanstone (1992), standardised in ANSI X9.62 (1999) and FIPS 186-2 (2000). Bitcoin uses ECDSA over the curve **secp256k1** (Certicom's SEC 2 standard, 2000). The choice of secp256k1 over the NIST P-256 curve is unusual and has been read as Satoshi avoiding curves with unexplained constants.

### T-07 · Cryptographic hash functions (1979–2001)
- Merkle (1979) formalised one-way hash functions in his thesis.
- MD4 (1990), MD5 (1992), SHA-0 (1993), SHA-1 (1995) — the Rivest/NSA lineage; all later broken.
- **SHA-2 family (NIST, 2001)** — SHA-256 is Bitcoin's workhorse: block hashing, proof-of-work, Merkle trees, transaction IDs (applied twice, "double-SHA256").
- **RIPEMD-160 (1996)** — Dobbertin, Bosselaers, Preneel. Bitcoin addresses are `RIPEMD-160(SHA-256(pubkey))`, combining two independent hash families so a break in one does not expose keys.

Properties Bitcoin depends on: **preimage resistance** (proof-of-work is meaningful), **second-preimage resistance** (a block cannot be silently swapped), **collision resistance** (Merkle proofs are sound).

**Evolution after Bitcoin:** Schnorr signatures (Schnorr 1989, patent expired 2008; adopted in Bitcoin via BIP 340, Taproot, 2021) enabling key and signature aggregation; BLS signatures (2001) used by Ethereum's beacon chain; SHA-3/Keccak (2012/2015) used by Ethereum; post-quantum schemes (NIST FIPS 203–205, 2024) not yet deployed in Bitcoin.

---

## 3. Layer L2 — Authenticated data structures

### T-08 · Merkle trees (1979, patent 1982)
Ralph Merkle's hash tree lets a single 32-byte root commit to an arbitrarily large set, with logarithmic-size membership proofs. In Bitcoin, every block header carries the Merkle root of its transactions. This is what makes **Simplified Payment Verification** (whitepaper §8) possible: a light client can verify a transaction is in a block with ~1 KB of proof rather than the full block.

### T-09 · Linked timestamping / hash chains (Haber & Stornetta, 1991–92)
Stuart Haber and W. Scott Stornetta's 1991 paper *How to Time-Stamp a Digital Document* is the direct ancestor of the blockchain data structure. Each timestamp certificate includes the hash of the previous certificate, so altering any record requires altering every later one. Their 1992 follow-up with Dave Bayer added Merkle trees so many documents could share one chain entry. Their company **Surety (1995)** published the weekly root hash in the *New York Times* classifieds — an early "public anchoring" of a hash chain. The Bitcoin whitepaper cites Haber and Stornetta in three of its eight references.

### T-10 · Append-only logs and the "chain of blocks"
The blockchain proper is T-09 plus T-08 plus T-11 (proof-of-work) combined: a hash-linked chain of Merkle roots, where extending the chain is costly. Note that Satoshi never used the word "blockchain" in the whitepaper; the term appears as "chain of blocks" and "block chain" (two words) in early code and forum posts.

**Evolution after Bitcoin:** Patricia–Merkle tries (Ethereum state), Verkle trees, Merkle Mountain Ranges, Certificate Transparency logs (Google, 2013 — a non-cryptocurrency descendant of Haber–Stornetta), and Utreexo (hash-based UTXO accumulator).

---

## 4. Layer L3 — Distributed agreement

### T-11 · Byzantine fault tolerance (Lamport, Shostak, Pease, 1980–82)
*The Byzantine Generals Problem* (1982) formalised agreement among nodes where some may be arbitrarily malicious, proving that with authenticated messages agreement is possible if fewer than one-third of participants are faulty. It also proved that in a synchronous setting the problem is solvable; Fischer, Lynch and Paterson (**FLP impossibility, 1985**) then proved that deterministic consensus is impossible in a fully asynchronous system with even one crash fault — which is why every practical consensus protocol, Bitcoin included, makes some timing or probabilistic assumption.

### T-12 · Practical BFT (Castro & Liskov, 1999)
PBFT made BFT usable in real systems with a closed, known set of replicas. Its limitation is exactly the Sybil problem (T-03): it requires knowing *who* the participants are. PBFT is the ancestor of every permissioned-ledger consensus (Tendermint, HotStuff, QBFT, RBFT, Raft-derived variants).

### T-13 · Nakamoto consensus (2008)
Bitcoin's novelty at this layer. Instead of a vote among known identities, agreement emerges from the **heaviest-proof-of-work chain rule**: nodes accept whichever valid chain embodies the most cumulative work. Properties:
- **Open membership** — anyone can join or leave; no identity registry.
- **Probabilistic finality** — a block is never absolutely final, only exponentially unlikely to be reverted as more work is built on it (the "six confirmations" convention).
- **Leader election by lottery** — whoever finds a valid hash proposes the next block; no election protocol, no view changes.
- **Security bound** — safe while honest hashpower exceeds 50%; formally analysed by Garay, Kiayias and Leonardos (*The Bitcoin Backbone Protocol*, 2015) and Pass, Seeman and shelat (2017).

**Evolution after Bitcoin:** GHOST (2013) and inclusive protocols; proof-of-stake (Peercoin 2012, Ethereum Casper/Gasper 2022); hybrid BFT-with-open-membership designs (Tendermint 2014, Algorand 2017, HotStuff 2018); DAG-based orderings (IOTA, Avalanche, Narwhal/Bullshark).

---

## 5. Layer L4 — Economic and anti-abuse mechanisms

### T-14 · Proof-of-work as a pricing function (Dwork & Naor, 1992)
*Pricing via Processing or Combatting Junk Mail* proposed forcing a sender to solve a moderately hard puzzle before a message is accepted — cheap for legitimate use, expensive at spam scale. This is the origin of the idea that computation can substitute for identity or payment as an admission cost.

### T-15 · Hashcash (Adam Back, 1997; paper 2002)
Back's Hashcash made proof-of-work concrete: find a nonce such that `SHA-1(header ‖ nonce)` has *n* leading zero bits. Verification is one hash; production is ~2ⁿ hashes. Bitcoin's mining is Hashcash with SHA-256, a dynamically adjusted target, and a block header as the payload. Back is cited in the whitepaper.

### T-16 · Reusable Proofs of Work (Hal Finney, 2004)
RPOW let a Hashcash token be exchanged for a new one via a trusted server running in an IBM 4758 secure coprocessor, so proof-of-work could circulate as a bearer token. It established the idea of PoW *as a scarce, transferable asset* — but still depended on one trusted server. Finney later received the first Bitcoin transaction (12 January 2009).

### T-17 · Incentive-compatible protocol design
- BitTorrent's tit-for-tat (T-02) showed a P2P protocol could be self-enforcing.
- Mechanism-design results (Vickrey 1961; Nash 1950) supply the vocabulary: Bitcoin's block subsidy and fee market are designed so that following the protocol is a miner's best response.
- The whitepaper's §6 *Incentive* is the first cryptographic protocol paper to make "rational actors will follow the rules because it pays" a core security assumption rather than an afterthought.

### T-18 · Difficulty adjustment (Bitcoin, 2009)
Every 2016 blocks the target is retuned so blocks arrive every ~10 minutes regardless of total hashpower. This closed-loop control is what keeps the L4 cost function stable as participation changes — a genuinely new mechanism.

**Evolution after Bitcoin:** ASIC-resistant hash functions (Scrypt, Ethash, RandomX); proof-of-stake slashing economics; MEV and fee-market redesign (EIP-1559, 2021); proof-of-space/time (Chia).

---

## 6. Layer L5 — Digital-cash design

### T-19 · Blind signatures and eCash (David Chaum, 1982–1998)
Chaum's *Blind Signatures for Untraceable Payments* (1982) let a bank sign a coin without seeing its serial number, giving payer anonymity. **DigiCash (1990)** and its **eCash** product deployed it with Mark Twain Bank (1995) and Deutsche Bank; DigiCash went bankrupt in 1998. Crucial lesson: eCash solved anonymity but not decentralisation — the bank was still the sole issuer and the sole double-spend arbiter. Chaum's 1982 paper is the intellectual origin of "cryptographic money"; his 1985 *Security Without Identification* framed the privacy agenda the cypherpunks inherited.

### T-20 · The cypherpunk movement (1992– )
Eric Hughes, Tim May and John Gilmore founded the cypherpunks mailing list in 1992. May's *Crypto Anarchist Manifesto* (1988/1992) and Hughes' *A Cypherpunk's Manifesto* (1993) set the goal explicitly: privacy and freedom of transaction through cryptography rather than law. Nearly every name in L4–L5 — Back, Dai, Szabo, Finney, and Satoshi — published on or emerged from this list. The Bitcoin whitepaper was announced on the *cryptography* mailing list (metzdowd.com), a direct descendant.

### T-21 · b-money (Wei Dai, 1998)
Dai's proposal described (a) a currency created by solving computational problems, (b) a broadcast network where every participant keeps a ledger of everyone's balances, and (c) contract enforcement by a quorum of servers with posted collateral. It is the first written design with a *shared ledger maintained by all participants* and is the first citation in the Bitcoin whitepaper. It was never implemented; it lacked a mechanism to resolve conflicting ledgers.

### T-22 · bit gold (Nick Szabo, 1998; published 2005)
Szabo proposed a chain in which each proof-of-work solution is timestamped and signed, and the *next* puzzle is derived from the previous solution — a proof-of-work chain. Ownership was tracked in a Byzantine-fault-tolerant "title registry". bit gold is the closest structural ancestor of Bitcoin; its unsolved problem was the same as b-money's: how to make the registry decentralised. Szabo's earlier work on **smart contracts (1994–97)** is also the origin of that term.

### T-23 · Centralised digital currencies as cautionary cases (1996–2013)
e-gold (1996), Liberty Reserve (2006) and others demonstrated real demand for online value transfer and were each shut down by prosecution or regulatory action. Together with DigiCash (T-19), they established empirically that a central issuer is a single point of legal and operational failure — the problem statement Bitcoin's first sentence addresses.

### T-24 · The double-spend problem
The core unsolved problem across T-19–T-23. A digital token is a string of bits and can be copied; some authority must decide which copy is valid. Every pre-Bitcoin system either used a central server (Chaum, Finney) or left the problem open (Dai, Szabo). Bitcoin's answer is that the *order* of transactions is fixed by the proof-of-work chain (L2 + L3 + L4), so the first spend to be buried in the chain is the valid one and any later conflicting spend is rejected by every node.

---

## 7. Bitcoin: the synthesis (2008–2009)

| Date | Event |
|---|---|
| 18 Aug 2008 | `bitcoin.org` domain registered |
| 31 Oct 2008 | *Bitcoin: A Peer-to-Peer Electronic Cash System* posted to the cryptography mailing list |
| 3 Jan 2009 | Genesis block mined; coinbase text quotes *The Times* headline on bank bailouts |
| 9 Jan 2009 | Bitcoin v0.1 released on SourceForge |
| 12 Jan 2009 | First transaction, Satoshi → Hal Finney (block 170) |
| 22 May 2010 | First documented purchase of goods (two pizzas, 10,000 BTC) |
| Apr 2011 | Satoshi's last known communication |

### 7.1 What each layer contributes to Bitcoin
- **L0** — gossip flood of transactions and blocks; DNS seeds for bootstrap.
- **L1** — ECDSA/secp256k1 for ownership; SHA-256 for everything else; RIPEMD-160 for addresses.
- **L2** — Merkle root per block; hash-linked headers; the chain itself.
- **L3** — heaviest-chain rule; probabilistic finality.
- **L4** — Hashcash-style PoW; block subsidy (halving every 210,000 blocks); fees; difficulty adjustment.
- **L5** — UTXO model (coins as unspent outputs, not account balances); Script (a deliberately non-Turing-complete Forth-like language) for spending conditions; the 21 million supply schedule.

### 7.2 What was actually new
Only three things in Bitcoin have no direct predecessor:
1. **Nakamoto consensus** (T-13) — resolving the Sybil problem by binding voting weight to proof-of-work and choosing the heaviest chain.
2. **Difficulty adjustment** (T-18) — a feedback controller keeping block production stable.
3. **The closed incentive loop** — PoW both secures the ledger *and* issues the currency that pays for the PoW. Neither bit gold nor b-money closed this loop.

Everything else is cited, reused, or lightly adapted prior art. This is worth stating precisely in academic writing: Bitcoin is a *systems* contribution, not a *cryptographic* one.

---

## 8. Evolution after Bitcoin (brief, for cross-reference)

| Year | Development | Layer affected |
|---|---|---|
| 2011 | Namecoin — first altcoin; first use of the chain as a name registry (proto-identity use) | L5 |
| 2012 | Peercoin — first proof-of-stake | L3/L4 |
| 2012 | Ripple/XRP — federated consensus without PoW | L3 |
| 2013 | Ethereum whitepaper (Buterin); launched July 2015 — Turing-complete contracts, account model | L5 |
| 2013 | Certificate Transparency — Haber–Stornetta logs for TLS, no currency | L2 |
| 2014 | Tendermint — BFT with bonded stake, ancestor of Cosmos | L3 |
| 2015 | Hyperledger project founded (Linux Foundation); Fabric 1.0 in 2017 — permissioned, PBFT-family | L3 |
| 2015–18 | Lightning Network paper and mainnet — payment channels, off-chain scaling | L5 |
| 2016 | Zcash — zk-SNARKs in a live currency (Groth16 shortly after) | L1/L5 |
| 2017 | SegWit (BIP 141) — transaction malleability fix, block weight | L2/L5 |
| 2021 | Taproot (BIPs 340–342) — Schnorr signatures, MAST | L1/L5 |
| 2022 | Ethereum Merge — PoW → PoS (Gasper) | L3/L4 |
| 2023 | BIP 324 — encrypted P2P transport | L0 |

---

## 9. Key primary sources

1. Nakamoto, S. (2008). *Bitcoin: A Peer-to-Peer Electronic Cash System.*
2. Diffie, W. & Hellman, M. (1976). New Directions in Cryptography. *IEEE Trans. Inf. Theory* 22(6).
3. Rivest, R., Shamir, A. & Adleman, L. (1978). A Method for Obtaining Digital Signatures and Public-Key Cryptosystems. *CACM* 21(2).
4. Merkle, R. (1979). *Secrecy, Authentication, and Public Key Systems.* PhD thesis, Stanford.
5. Chaum, D. (1982). Blind Signatures for Untraceable Payments. *CRYPTO '82.*
6. Lamport, L., Shostak, R. & Pease, M. (1982). The Byzantine Generals Problem. *ACM TOPLAS* 4(3).
7. Fischer, M., Lynch, N. & Paterson, M. (1985). Impossibility of Distributed Consensus with One Faulty Process. *JACM* 32(2).
8. Haber, S. & Stornetta, W. S. (1991). How to Time-Stamp a Digital Document. *J. Cryptology* 3(2).
9. Bayer, D., Haber, S. & Stornetta, W. S. (1992). Improving the Efficiency and Reliability of Digital Time-Stamping. *Sequences II.*
10. Dwork, C. & Naor, M. (1992). Pricing via Processing or Combatting Junk Mail. *CRYPTO '92.*
11. Back, A. (2002). *Hashcash — A Denial of Service Counter-Measure.*
12. Dai, W. (1998). *b-money.* (weidai.com)
13. Szabo, N. (2005). *Bit Gold.* (unenumerated.blogspot.com; concept 1998)
14. Castro, M. & Liskov, B. (1999). Practical Byzantine Fault Tolerance. *OSDI '99.*
15. Douceur, J. (2002). The Sybil Attack. *IPTPS '02.*
16. Finney, H. (2004). *RPOW — Reusable Proofs of Work.*
17. Garay, J., Kiayias, A. & Leonardos, N. (2015). The Bitcoin Backbone Protocol. *EUROCRYPT '15.*
18. Narayanan, A. & Clark, J. (2017). Bitcoin's Academic Pedigree. *CACM* 60(12). — the best single secondary survey of this lineage.

---

*Accuracy note: dates are publication or release dates as generally recorded; where concept and publication dates differ (Szabo, Back, Ellis/Cocks) both are given. Verify against the Accuracy Ledger before citing in the thesis.*

---

## 10. The identity lineage (new in v1.1): T-I01 – T-I22

The cash lineage (§§1–7) needed only *ownership*: whoever holds the key spends the coin. Identity needs more — a key bound to a subject, attributes bound to the key, disclosure of some attributes without others, unlinkability across disclosures, and a way to revoke. Those requirements were solved on a separate track, mostly in authentication and privacy cryptography, and converged with the ledger track only in 2016–2022. The entries below follow the v1.0 discipline: what it provides, what secures it, and which layer it lives on.

### 10.1 Authentication and public-key infrastructure

#### T-I01 · Needham–Schroeder and Kerberos (1978; MIT Athena 1988) — L6/L7
Needham and Schroeder's 1978 protocol introduced the *authentication server* that vouches for principals by issuing keyed tickets; Kerberos (v4 1988, v5 RFC 1510 1993, RFC 4120 2005) deployed it at scale. Establishes the pattern every later identity system either copies or rejects: a trusted third party binds a name to a key and issues time-limited proofs of that binding. Secured by symmetric cryptography and the server's secrecy. Decentralised identity is defined largely by *removing* this server.

#### T-I02 · X.509 and the certificate-authority PKI (ITU-T 1988; PKIX RFC 2459 1999, RFC 5280 2008) — L6
A certificate is a signed statement `(subject name, public key, validity, issuer)`. Chains of certificates terminate in a root CA that must be trusted a priori. Secured by digital signatures (T-04/T-05). Provides: key-to-name binding, expiry, revocation via CRL (1988) and OCSP (RFC 2560, 1999). Breaking record: DigiNotar (2011), Comodo (2011), Symantec distrust (2017) — a compromised or negligent CA can mint a valid certificate for any name. **Certificate Transparency (RFC 6962, 2013; RFC 9162, 2021)** repaired this by publishing every issued certificate to append-only Merkle logs (T-08/T-09) — the first large-scale non-currency use of the Haber–Stornetta structure, and the direct precedent for "public anchoring" of identity state.

#### T-I03 · Web of trust — PGP (Zimmermann 1991; OpenPGP RFC 2440 1998, RFC 4880 2007) — L6
Replaces the CA hierarchy with peer signatures on keys: trust is a graph, not a tree. Provides the first working decentralised key-binding scheme. Failure mode: key-signing parties do not scale, revocation is best-effort, and usability collapsed adoption. SSI's "trust registries" and "issuer accreditation" are a middle path between T-I02 and T-I03.

#### T-I04 · SSL / TLS (SSL 2.0 1995, SSL 3.0 1996, TLS 1.0 RFC 2246 1999, TLS 1.2 RFC 5246 2008, TLS 1.3 RFC 8446 2018) — L7
The authenticated, confidential channel for the web: X.509 for server identity, Diffie–Hellman (T-04) for key agreement, AEAD for confidentiality and integrity. TLS 1.3 removed static-RSA key exchange and made forward secrecy mandatory. This is the reference point for what an I2I channel must provide; DIDComm (T-I18) is best understood as "TLS where both ends are DIDs rather than CA-certified names".

#### T-I05 · Vehicular PKI — IEEE 1609.2 (2006; -2016; -2022) and ETSI TS 102 941; butterfly keys and implicit certificates — L6 (CAV grounding)
The CAV domain's own identity stack: compact ECC certificates, **implicit certificates (ECQV)** that carry a public-key reconstruction value instead of a full key and signature, **pseudonym certificates** rotated to prevent tracking, and **butterfly key expansion** (SCMS, 2013–) that lets a vehicle obtain many unlinkable pseudonym certificates from one request. Solves linkability at Tier 1 (sub-100 ms) with no ledger. The programme's Pass 4 treats this as the incumbent that a ledger-based system must not degrade; it is the L6 baseline for the vehicular scenario.

### 10.2 Secure messaging and the I2I channel

#### T-I06 · Off-the-Record messaging (Borisov, Goldberg, Brewer 2004) — L7
First protocol to combine authentication with **deniability** and **forward secrecy** in a chat setting, using per-message Diffie–Hellman re-keying. Established that an I2I channel can be authenticated without producing a non-repudiable transcript — a property vehicular and privacy-sensitive identity flows sometimes want and sometimes must avoid (audit).

#### T-I07 · Signal protocol — X3DH and the Double Ratchet (Marlinspike & Perrin 2013–2016; formal analysis Cohn-Gordon et al. 2017) — L7
X3DH gives asynchronous authenticated key agreement from published prekeys; the Double Ratchet gives per-message forward secrecy and post-compromise security. Adopted by WhatsApp (2016), and later the IETF MLS group-messaging standard (RFC 9420, 2023). This is the modern state of the art for L7 confidentiality between two long-term identities and is what DIDComm's encryption envelope approximates.

#### T-I08 · Noise protocol framework (Perrin 2016; rev. 34 2018) — L7
A family of Diffie–Hellman handshake patterns (NK, XX, IK…) with a small, analysable state machine. Used by WireGuard (2017), Lightning's transport (BOLT 8), and libp2p. Relevance: Noise is the cleanest existing formalisation of "authenticated channel from two static keys plus ephemerals", which is precisely what an I2I channel between two DIDs is.

#### T-I09 · Transport-independent envelopes — JOSE (JWS RFC 7515 / JWE RFC 7516, 2015) and COSE (RFC 8152 2017, RFC 9052 2022) — L7
Signed and encrypted JSON / CBOR objects that survive any transport. W3C Verifiable Credentials in JWT form, DIDComm v2 envelopes, and ISO 18013-5 mobile driving licences all ride on these. Secured by L1; they add no cryptography, only interoperable framing.

### 10.3 Privacy cryptography

#### T-I10 · Zero-knowledge proofs — GMR 1985; Fiat–Shamir 1986; Schnorr identification 1989 — L1
Goldwasser, Micali and Rackoff defined interactive proofs where the verifier learns nothing beyond the statement's truth. Fiat–Shamir made them non-interactive by replacing the verifier's challenge with a hash (T-07). Schnorr's identification scheme is the simplest concrete instance and the seed of every "prove I know the key without showing it" construction. This is the primitive that lets identity be *proved* rather than *disclosed*.

#### T-I11 · Pairing-based cryptography — Boneh–Lynn–Shacham 2001; Camenisch–Lysyanskaya 2002/2004; BBS 2004 → BBS+ 2016 → IETF BBS draft 2022– — L1
Bilinear pairings on elliptic curves (T-06) enable **signatures on committed messages** and **proofs of knowledge of a signature** — the mathematical heart of anonymous credentials. CL signatures (2002, RSA-based; 2004, pairing-based) underlie Idemix and AnonCreds v1; BBS+ underlies the newer W3C Data Integrity BBS cryptosuite. Provides: sign a bundle of attributes once, later prove possession of any subset, unlinkably. Secured by the q-SDH / LRSW assumptions rather than plain ECDLP — a stronger, less battle-tested assumption, which is a cost the thesis must state.

#### T-I12 · Cryptographic accumulators — Benaloh & de Mare 1993; Camenisch & Lysyanskaya 2002; Nguyen 2005 (bilinear) — L2
A constant-size value that commits to a set, with short membership *and non-membership* witnesses. This is how a credential can be proved *not revoked* without revealing which credential it is. AnonCreds revocation registries are CL-style accumulators; the programme's HAA-1 Profile AC is exactly this. Secured by the strong-RSA or q-SDH assumption. Cost: witness updates must be distributed when the set changes — the origin of the revocation-latency window *W*.

#### T-I13 · Anonymous credentials — Chaum 1985 (concept); Brands 2000 / U-Prove; Camenisch & Van Herreweghen 2002 / IBM Idemix — L6
Chaum's *Security Without Identification* (1985) stated the goal: credentials that can be shown without linking the shows to each other or to issuance. Brands built it on discrete-log blind signatures (single-show); Idemix built it on CL signatures (multi-show, unlinkable). Both had working code by 2002–2010 and almost no deployment — the same fate as DigiCash (T-19), for the same reason: no shared, neutral registry for issuer keys, schemas and revocation state. That registry is what the ledger lineage supplied.

#### T-I14 · Succinct proofs — zk-SNARKs (Groth 2016 "Groth16"; Pinocchio 2013; PLONK 2019) and Bulletproofs (Bünz et al. 2018) — L1
Constant-size or logarithmic proofs of arbitrary statements. Groth16 needs a trusted setup and has ~200-byte proofs verifiable in ~250k gas on the EVM (the programme's U-17 re-argument prices this); Bulletproofs need no setup but verify linearly. Deployed first in Zcash (2016). For identity: lets a presentation prove an arbitrary predicate over attributes ("age ≥ 18", "licence class ∈ {C, D}") rather than the attribute itself. Paladin (O15) provides an on-chain Groth16 verifier.

#### T-I15 · Commitments — Pedersen 1991; hash commitments — L1
`C = g^m · h^r` hides *m* perfectly and binds it computationally. The EDPB's July 2026 blockchain guidelines (¶53) name perfectly-hiding commitments as the acceptable on-chain form for personal data references; the HAA-1 anchor is in commitment form for exactly that reason. A hash commitment `H(m ‖ r)` is the cheaper, computationally-hiding alternative (¶52 salted/keyed hashes).

### 10.4 Decentralised naming and registries

#### T-I16 · Namecoin (2011) and Zooko's triangle (2001) — L5/L6
Zooko Wilcox-O'Hearn's conjecture: a naming system can be at most two of *decentralised*, *secure*, *human-meaningful*. Namecoin — the first Bitcoin fork — claimed all three by putting name→value bindings in a blockchain. It proved the mechanism and failed on governance and squatting. It is the first *identity-flavoured* use of a ledger and the conceptual origin of "a blockchain as a verifiable data registry".

#### T-I17 · W3C Decentralised Identifiers and Verifiable Credentials (DID Core 1.0, July 2022; VC Data Model 1.0 2019, 1.1 2022, 2.0 2025) — L6
The standards layer. A **DID** is a URI resolving to a **DID document** (verification methods, service endpoints) via a **DID method** that names the registry (`did:ethr`, `did:indy`, `did:web`, `did:key`…). A **VC** is a signed set of claims by an issuer about a subject; a **verifiable presentation** is a holder-constructed disclosure of one or more VCs. The data model is *already hybrid by construction*: the verifiable data registry holds identifiers, keys, schemas and revocation; holders hold credentials. The programme's twelve-function `IMinimalSSI` interface is derived from this model (Set A = DID operations; Set B adds the four credential operations).

#### T-I18 · DIDComm (v1 Aries RFC 0019/0160, 2019; v2 DIF spec, 2022) — L7
Transport-agnostic, mutually authenticated, encrypted messaging *between DIDs*. v2 uses JWE envelopes (T-I09) with ECDH-1PU for sender authentication and anonymous-sender modes. Protocols layered on it (Issue Credential, Present Proof, Trust Ping, Mediation) are the L7 realisation of Set B. Option O16 in the programme.

#### T-I19 · Sidetree (DIF 2020; ION on Bitcoin 2021) — L2/L6
Batches thousands of DID operations off-chain (IPFS), anchors one hash per batch on a public chain (Bitcoin). Demonstrates the *anchoring* pattern at scale: the ledger supplies ordering and non-equivocation only; content availability is a separate concern. This is the public-chain end of the settlement spectrum HAA-1 spans.

#### T-I20 · AnonCreds (Sovrin/Indy 2017; LFDT AnonCreds v1.0 specification 2023; anoncreds-rs) — L6
The deployed anonymous-credential system: CL signatures (T-I11), accumulator revocation (T-I12), predicate proofs, and a ledger-backed registry for schemas, credential definitions and revocation registries. The only evaluated option scoring 12/12 Set B in the programme (O12), and the sole native implementation of `createPresentation` — the crux X2 finding.

#### T-I21 · Hyperledger / LF Decentralized Trust stack — Indy (2016), Aries (2019), Besu (2019), AnonCreds (2023), Paladin (2025) — L3–L7
The institutional convergence: a permissioned identity ledger with RBFT consensus (Indy, O10), its EVM re-implementation on Besu QBFT (Indy-Besu, O11), agent frameworks (ACA-Py / Credo-TS, O17), and a privacy overlay with private transaction groups and on-chain Groth16 verification (Paladin, O15). The programme's Family E.

#### T-I22 · Agent identity — ERC-8004 (Draft; mainnet reference deployment January 2026), A2A, MCP — L6/L7
Extends the subject of identity from vehicle or person to *software agent*: Identity, Reputation and Validation registries on-chain, capability advertisement via A2A/MCP. Introduces delegation chains and the confused-deputy problem as first-class identity concerns. Family D (O9) and the programme's Set C.

### 10.5 What the identity lineage adds that the cash lineage lacked

| Requirement | Absent in Bitcoin because… | Supplied by |
|---|---|---|
| Attribute binding | a coin has no attributes | T-I02 certificates → T-I17 VCs |
| Selective disclosure | a spend reveals everything | T-I10/T-I11/T-I14 |
| Unlinkability across uses | addresses are pseudonymous, not unlinkable | T-I05 pseudonym certs, T-I11 BBS+/CL, T-I13 |
| Revocation with a bound | UTXOs are spent, never revoked | T-I02 CRL/OCSP → T-I12 accumulators, status lists |
| Non-equivocation of a *registry* (not just a ledger) | Bitcoin orders spends, not key histories | T-I16 → T-I17 DID methods, T-I19 anchoring |
| Authenticated confidential channel | Bitcoin's P2P is unauthenticated and plaintext | T-I04, T-I07, T-I08 → T-I18 |
| Recovery / delegation | lose the key, lose the coin | T-I17 DID document controllers, ERC-4337 social recovery, Set A `addDelegate` |

---

## 11. Layers L6 and L7 stated in the v1.0 discipline

### 11.1 L6 — Identity

**Delivers upward:** a resolvable identifier bound to controllable keys; issuer-signed attribute bundles; holder-constructed disclosures; a revocation oracle with a stated latency; delegation and recovery.

**Secured by:** L1 signatures (control), L1 ZKP/pairing primitives (disclosure), L2 registries and accumulators (membership/non-membership), L5 ordered non-equivocable state (key history cannot be rewritten or forked per-verifier), and L3/L4 for the registry's own liveness and safety.

**Programme instantiation:** `IMinimalSSI` — Set A (`createDID`, `resolveDID`, `updateDID`, `deactivateDID`, `addVerificationMethod`, `removeVerificationMethod`, `addDelegate`, `validDelegate`) is the registry face; Set B adds `issueCredential`, `verifyCredential`, `revokeCredential`, `createPresentation`; Set C is the agent extension.

### 11.2 L7 — Application / I2I

**Delivers upward (to the use case):** two endpoints, each identified at L6, exchange messages or transactions with authenticity, integrity, confidentiality, replay protection and — as a policy choice — either non-repudiation (audit) or deniability.

**Secured by:** L6 for *who*, L1 for the channel (DH key agreement, AEAD), L0 for delivery; and, for transactions that must be globally ordered (a credential anchor, a key rotation), L5 for ordering.

**Programme instantiation:** DIDComm v2 (O16) for messaging; the V2X message path at Tier 1/2 running against *cached* L6 state, with only Tier-3 writes touching the ledger (G-C1 / HAA-1 read-path completeness rule).

---

## 12. Additional primary sources for §10

19. Needham, R. & Schroeder, M. (1978). Using Encryption for Authentication in Large Networks of Computers. *CACM* 21(12).
20. ITU-T X.509 (1988); Cooper et al., RFC 5280 (2008).
21. Laurie, B., Langley, A. & Kasper, E. (2013). Certificate Transparency. RFC 6962.
22. Rescorla, E. (2018). TLS 1.3. RFC 8446.
23. IEEE Std 1609.2-2022; Whyte, W. et al. (2013). A Security Credential Management System for V2V Communications. *IEEE VNC*.
24. Borisov, N., Goldberg, I. & Brewer, E. (2004). Off-the-Record Communication. *WPES '04*.
25. Cohn-Gordon, K. et al. (2017). A Formal Security Analysis of the Signal Messaging Protocol. *EuroS&P*.
26. Perrin, T. (2018). The Noise Protocol Framework, rev. 34.
27. Goldwasser, S., Micali, S. & Rackoff, C. (1985/89). The Knowledge Complexity of Interactive Proof Systems. *SIAM J. Comput.* 18(1).
28. Boneh, D., Lynn, B. & Shacham, H. (2001). Short Signatures from the Weil Pairing. *ASIACRYPT*.
29. Camenisch, J. & Lysyanskaya, A. (2002). A Signature Scheme with Efficient Protocols. *SCN*; (2004) Signature Schemes and Anonymous Credentials from Bilinear Maps. *CRYPTO*.
30. Au, M. H., Susilo, W. & Mu, Y. (2006). Constant-Size Dynamic k-TAA. *SCN* (BBS+).
31. Benaloh, J. & de Mare, M. (1993). One-Way Accumulators. *EUROCRYPT*.
32. Chaum, D. (1985). Security Without Identification. *CACM* 28(10).
33. Groth, J. (2016). On the Size of Pairing-Based Non-interactive Arguments. *EUROCRYPT*.
34. Bünz, B. et al. (2018). Bulletproofs. *IEEE S&P*.
35. Pedersen, T. (1991). Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing. *CRYPTO*.
36. W3C (2022). Decentralized Identifiers (DIDs) v1.0; W3C (2025). Verifiable Credentials Data Model v2.0.
37. DIF (2022). DIDComm Messaging v2.0; DIF (2020). Sidetree Protocol.
38. LF Decentralized Trust (2023). AnonCreds Specification v1.0.
39. EDPB (2026). Guidelines 02/2025 on the processing of personal data through blockchain technologies, v2.0 (7 July 2026).

*Accuracy note (v1.1): dates for T-I entries are publication/RFC dates as generally recorded; where a concept predates its standard (BBS 2004 vs BBS+ 2006/2016, Idemix 2002 vs release 2010) both are given. RFC 9420 (MLS) and the 2026 EDPB adoption were confirmed against the corpus (P-4 KD-P1). Verify the rest against the Accuracy Ledger before thesis citation.*
