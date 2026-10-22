# Sources for the ZKP, Identity and Agent-Wrapped Identity Work

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Compiled:** 2026-10-15 for Plan 1 (WP1), by two research passes whose every entry was checked against a reachable
URL or DOI in the same session (Crossref metadata, the landing page, or the PDF), then merged and reviewed here.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md` rule 1.3.8. **Used by:** `REPORT_A_*`, `REPORT_B_*`, `REPORT_C_*`,
code comments in `5_zkp-agent-identity/`. Reports cite as `[@KEY]`; `docs/zkp/check_citations.py` fails on a key
that is not defined below.

"Verified: yes" means the primary record was fetched or its DOI resolved with matching metadata. "Partial" means a
secondary source or search record only; a partial entry never carries a number into a report without saying so.

---

# Part A. Zero-knowledge proofs, credentials, blockchains, vehicles
## A1. ZKP origins and theory

### [GMR85] Goldwasser, S., Micali, S., Rackoff, C. (1985). The knowledge complexity of interactive proof-systems. Proc. 17th ACM STOC, pp. 291-304.
- URL/DOI: https://doi.org/10.1145/22145.22178
- Verified: yes (Crossref metadata)
- Supports: This is the conference paper that first introduced interactive proofs and "knowledge complexity" (zero knowledge). Cite it for the 1985 origin of ZKPs.

### [GMR89] Goldwasser, S., Micali, S., Rackoff, C. (1989). The Knowledge Complexity of Interactive Proof Systems. SIAM Journal on Computing 18(1):186-208.
- URL/DOI: https://doi.org/10.1137/0218012
- Verified: yes (Crossref metadata; McGill-hosted scan of the journal version seen in search)
- Supports: The journal version of the formal ZK definition. A note in the paper says a preliminary version appeared in 1985 (STOC). This paper shared the 1993 Gödel Prize (see [GODEL93]).

### [GMW91] Goldreich, O., Micali, S., Wigderson, A. (1991). Proofs that yield nothing but their validity or all languages in NP have zero-knowledge proof systems. Journal of the ACM 38(3):690-728 (some indexes give 691-729).
- URL/DOI: https://doi.org/10.1145/116825.116852
- Verified: yes (Crossref metadata; free PDF at people.csail.mit.edu)
- Supports: Shows that every language in NP has a zero-knowledge proof, assuming one-way functions exist, using a ZK proof for graph 3-colouring. This is the theoretical basis for general-purpose ZK over arbitrary circuits.

### [FS86] Fiat, A., Shamir, A. (1987). How To Prove Yourself: Practical Solutions to Identification and Signature Problems. CRYPTO '86, LNCS 263, pp. 186-194.
- URL/DOI: https://doi.org/10.1007/3-540-47721-7_12
- Verified: yes (Crossref metadata)
- Supports: Gives the identification and signature schemes behind the "Fiat-Shamir heuristic". The heuristic hashes the transcript to replace the verifier's random challenge, which turns a public-coin interactive proof into a non-interactive proof or signature. Security rests on the difficulty of factoring.

### [BR93] Bellare, M., Rogaway, P. (1993). Random oracles are practical: a paradigm for designing efficient protocols. Proc. 1st ACM CCS, pp. 62-73.
- URL/DOI: https://doi.org/10.1145/168588.168596
- Verified: yes (Crossref metadata)
- Supports: Formalises the random-oracle model, which is used to justify Fiat-Shamir and hash-based NIZKs.

### [PS00] Pointcheval, D., Stern, J. (2000). Security Arguments for Digital Signatures and Blind Signatures. Journal of Cryptology 13:361-396.
- URL/DOI: https://doi.org/10.1007/s001450010003
- Verified: yes (Crossref metadata)
- Supports: Gives the random-oracle security proof (forking lemma) for Fiat-Shamir-type signatures such as Schnorr. The original 1986 scheme had no such proof.

### [Sch89] Schnorr, C.P. (1990). Efficient Identification and Signatures for Smart Cards. CRYPTO '89, LNCS 435, pp. 239-252.
- URL/DOI: https://doi.org/10.1007/0-387-34805-0_22
- Verified: yes (Crossref metadata)
- Supports: Conference version of the Schnorr identification protocol, a 3-move sigma protocol proving knowledge of a discrete logarithm.

### [Sch91] Schnorr, C.P. (1991). Efficient signature generation by smart cards. Journal of Cryptology 4(3):161-174.
- URL/DOI: https://doi.org/10.1007/BF00196725
- Verified: yes (Crossref metadata; Frankfurt repository PDF seen)
- Supports: Journal version of the Schnorr protocol and signature. Its goal is to minimise "the message dependent amount of computation the smart card has to perform" for each signature.

### [CP92] Chaum, D., Pedersen, T.P. (1993). Wallet Databases with Observers. CRYPTO '92, LNCS 740, pp. 89-105.
- URL/DOI: https://doi.org/10.1007/3-540-48071-4_7
- Verified: yes (Crossref metadata)
- Supports: Introduces the Chaum-Pedersen proof of equality of discrete logarithms, which is widely used in e-cash, mix-nets and verifiable decryption.

### [CDS94] Cramer, R., Damgård, I., Schoenmakers, B. (1994). Proofs of Partial Knowledge and Simplified Design of Witness Hiding Protocols. CRYPTO '94, LNCS 839, pp. 174-187.
- URL/DOI: https://doi.org/10.1007/3-540-48658-5_19
- Verified: yes (Crossref metadata)
- Supports: Introduces OR-proofs and threshold proofs. A prover can show knowledge of "at least d out of n solutions without revealing which d instances are involved."

### [Ped91] Pedersen, T.P. (1992). Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing. CRYPTO '91, LNCS 576, pp. 129-140.
- URL/DOI: https://doi.org/10.1007/3-540-46766-1_9
- Verified: yes (Crossref metadata)
- Supports: Source of the Pedersen commitment C = g^m h^r, which is perfectly hiding and computationally binding. Used in Bulletproofs, Zcash and anonymous credentials.

### [QQQ89] Quisquater, J.-J., Guillou, L.C., et al. (1990). How to Explain Zero-Knowledge Protocols to Your Children. CRYPTO '89, LNCS 435, pp. 628-631.
- URL/DOI: https://doi.org/10.1007/0-387-34805-0_60
- Verified: yes (Crossref metadata)
- Supports: The "Ali Baba cave" analogy for ZK, a standard teaching illustration.

### [BFM88] Blum, M., Feldman, P., Micali, S. (1988). Non-interactive zero-knowledge and its applications. Proc. 20th ACM STOC, pp. 103-112.
- URL/DOI: https://doi.org/10.1145/62212.62222
- Verified: yes (Crossref metadata)
- Supports: Introduces non-interactive ZK (NIZK) in the common reference string model, the ancestor of all zk-SNARK CRS/trusted-setup designs.

### [Kil92] Kilian, J. (1992). A note on efficient zero-knowledge proofs and arguments. Proc. 24th ACM STOC, pp. 723-732.
- URL/DOI: https://doi.org/10.1145/129712.129782
- Verified: yes (Crossref metadata)
- Supports: Builds succinct arguments from PCPs plus Merkle-tree commitments, an early basis for succinct proofs.

### [Mic00] Micali, S. (2000). Computationally Sound Proofs. SIAM Journal on Computing 30(4):1253-1298.
- URL/DOI: https://doi.org/10.1137/S0097539795284959
- Verified: yes (Crossref metadata)
- Supports: CS proofs, a non-interactive succinct argument built from PCPs in the random-oracle model. This is the conceptual forerunner of SNARKs and STARKs.

### [AS98] Arora, S., Safra, S. (1998). Probabilistic checking of proofs: a new characterization of NP. Journal of the ACM 45(1):70-122.
- URL/DOI: https://doi.org/10.1145/273865.273901
- Verified: yes (Crossref metadata)
- Supports: One of the two PCP theorem papers. NP = PCP(log n, log n).

### [ALMSS98] Arora, S., Lund, C., Motwani, R., Sudan, M., Szegedy, M. (1998). Proof verification and the hardness of approximation problems. Journal of the ACM 45(3):501-555.
- URL/DOI: https://doi.org/10.1145/278298.278306
- Verified: yes (Crossref metadata)
- Supports: Completes the PCP theorem (NP = PCP(log n, O(1))). NP proofs can be checked by reading a constant number of bits.

### [GODEL93] ACM SIGACT / EATCS (1993). 1993 Gödel Prize.
- URL/DOI: https://sigact.org/prizes/g%C3%B6del/1993.html
- Verified: yes (fetched)
- Supports: The 1993 Gödel Prize was shared by Babai & Moran (Arthur-Merlin games) and by Goldwasser, Micali & Rackoff for "The knowledge complexity of interactive proof systems" (SIAM J. Comput. 1989).

### [TURING12] ACM (2013). Goldwasser, Micali Receive ACM Turing Award for Advances in Cryptography (press release, 13 March 2013).
- URL/DOI: https://www.acm.org/media-center/2013/march/goldwasser-micali-receive-acm-turing-award-for-advances-in-cryptography
- Verified: partial (search result. The amturing.acm.org page is behind a Cloudflare check)
- Supports: Goldwasser and Micali received the 2012 ACM A.M. Turing Award, announced March 2013. The citation covers work that turned cryptography "from an art into a science", including probabilistic encryption and zero-knowledge proofs.

### [Thaler22] Thaler, J. (2022). Proofs, Arguments, and Zero-Knowledge. Foundations and Trends in Privacy and Security 4(2-4):117-660.
- URL/DOI: https://doi.org/10.1561/3300000030 (free draft: https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html)
- Verified: yes (Crossref metadata)
- Supports: A standard textbook on interactive proofs, SNARKs and their implementations, about 540 pages.

---

## A2. Modern SNARKs / STARKs and tooling

### [BCCT12-SNARKsC] Ben-Sasson, E., Chiesa, A., Genkin, D., Tromer, E., Virza, M. (2013). SNARKs for C: Verifying Program Executions Succinctly and in Zero Knowledge. CRYPTO 2013, LNCS 8043, pp. 90-108.
- URL/DOI: https://doi.org/10.1007/978-3-642-40084-1_6
- Verified: yes (Crossref metadata)
- Supports: An early practical zk-SNARK for general programs, and the basis of libsnark and Zerocash.

### [GGPR13] Gennaro, R., Gentry, C., Parno, B., Raykova, M. (2013). Quadratic Span Programs and Succinct NIZKs without PCPs. EUROCRYPT 2013, LNCS 7881, pp. 626-645.
- URL/DOI: https://doi.org/10.1007/978-3-642-38348-9_37
- Verified: yes (Crossref metadata)
- Supports: Introduces QAPs/QSPs, the arithmetisation behind Pinocchio and Groth16 (R1CS to QAP).

### [PHGR13] Parno, B., Howell, J., Gentry, C., Raykova, M. (2013). Pinocchio: Nearly Practical Verifiable Computation. IEEE S&P 2013, pp. 238-252.
- URL/DOI: https://doi.org/10.1109/SP.2013.47
- Verified: yes (Crossref metadata)
- Supports: The first nearly practical implementation of a QAP-based zk-SNARK, with constant-size proofs and fast verification.

### [Groth16] Groth, J. (2016). On the Size of Pairing-Based Non-interactive Arguments. EUROCRYPT 2016, LNCS 9666, pp. 305-326.
- URL/DOI: https://doi.org/10.1007/978-3-662-49896-5_11 ; ePrint https://eprint.iacr.org/2016/260
- Verified: yes (Crossref and ePrint abstract fetched)
- Supports: "a proof is only 3 group elements". Verification checks one pairing-product equation "using 3 pairings in total". Needs a circuit-specific trusted setup. Used by circom/snarkjs and Zcash Sapling.

### [PLONK19] Gabizon, A., Williamson, Z.J., Ciobotaru, O. (2019). PLONK: Permutations over Lagrange-bases for Oecumenical Noninteractive arguments of Knowledge. IACR ePrint 2019/953.
- URL/DOI: https://eprint.iacr.org/2019/953
- Verified: yes (fetched)
- Supports: A universal SNARK "with fully succinct verification, and significantly lower prover running time" than Sonic. One universal, updatable SRS serves all circuits up to a size bound.

### [Marlin20] Chiesa, A., Hu, Y., Maller, M., Mishra, P., Vesely, N., Ward, N. (2020). Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS. EUROCRYPT 2020, LNCS 12105, pp. 738-768.
- URL/DOI: https://doi.org/10.1007/978-3-030-45721-1_26
- Verified: yes (Crossref metadata)
- Supports: Universal and updatable SRS through algebraic holographic proofs plus polynomial commitments. An alternative to per-circuit Groth16 setup.

### [Halo19] Bowe, S., Grigg, J., Hopwood, D. (2019). Recursive Proof Composition without a Trusted Setup. IACR ePrint 2019/1021.
- URL/DOI: https://eprint.iacr.org/2019/1021
- Verified: yes (fetched)
- Supports: Halo is "the first practical example of recursive proof composition without a trusted setup", using discrete-log assumptions over cycles of curves.

### [Halo2] Electric Coin Company / Zcash. The halo2 Book.
- URL/DOI: https://zcash.github.io/halo2/
- Verified: yes (landing page title fetched)
- Supports: Documentation for halo2, a PLONKish proving system with no trusted setup, used in Zcash Orchard and by Scroll and others.

### [BBBPWM18] Bünz, B., Bootle, J., Boneh, D., Poelstra, A., Wuille, P., Maxwell, G. (2018). Bulletproofs: Short Proofs for Confidential Transactions and More. IEEE S&P 2018, pp. 315-334.
- URL/DOI: https://doi.org/10.1109/SP.2018.00020
- Verified: yes (Crossref metadata)
- Supports: Transparent (no trusted setup) range proofs and arithmetic-circuit proofs, with logarithmic proof size, built on Pedersen commitments. Verification time is linear.

### [STARK18] Ben-Sasson, E., Bentov, I., Horesh, Y., Riabzev, M. (2018). Scalable, transparent, and post-quantum secure computational integrity. IACR ePrint 2018/046.
- URL/DOI: https://eprint.iacr.org/2018/046
- Verified: yes (fetched)
- Supports: ZK-STARKs are transparent ("no reliance on any trusted party"), hash-based and plausibly post-quantum. Verification scales exponentially faster than database size.

### [Nova22] Kothapalli, A., Setty, S., Tzialla, I. (2022). Nova: Recursive Zero-Knowledge Arguments from Folding Schemes. CRYPTO 2022, LNCS 13510, pp. 359-388.
- URL/DOI: https://doi.org/10.1007/978-3-031-15985-5_13
- Verified: yes (Crossref metadata)
- Supports: Introduces folding schemes for incrementally verifiable computation, which give cheap recursion without a full SNARK verifier at each step.

### [Poseidon21] Grassi, L., Khovratovich, D., Rechberger, C., Roy, A., Schofnegger, M. (2021). Poseidon: A New Hash Function for Zero-Knowledge Proof Systems. 30th USENIX Security Symposium, pp. 519-535.
- URL/DOI: https://www.usenix.org/conference/usenixsecurity21/presentation/grassi ; ePrint https://eprint.iacr.org/2019/458
- Verified: yes (USENIX page fetched)
- Supports: "Poseidon uses up to 8x fewer constraints per message bit than Pedersen Hash". The paper notes that SHA-256 inside circuits "caused a huge computational penalty".

### [Circom23] Bellés-Muñoz, M., Isabel, M., Muñoz-Tapia, J.L., Rubio, A., Baylina, J. (2023). Circom: A Circuit Description Language for Building Zero-Knowledge Applications. IEEE Transactions on Dependable and Secure Computing 20(6):4733-4751.
- URL/DOI: https://doi.org/10.1109/TDSC.2022.3232813
- Verified: yes (Crossref metadata; published online Dec 2022, issue Nov/Dec 2023)
- Supports: The peer-reviewed description of the circom DSL. Circom compiles arithmetic circuits to R1CS for use with Groth16/PLONK provers such as snarkjs.

### [circom-docs] iden3. Circom 2 Documentation.
- URL/DOI: https://docs.circom.io/ ; repo https://github.com/iden3/circom
- Verified: yes (fetched title)
- Supports: Official documentation for the circom compiler toolchain.

### [snarkjs] iden3. snarkjs: zkSNARK implementation in JavaScript & WASM (GitHub repository).
- URL/DOI: https://github.com/iden3/snarkjs
- Verified: partial (URL reachable; contents not parsed by script)
- Supports: A JS/WASM implementation of Groth16, PLONK and FFLONK proving and verification, plus Powers-of-Tau ceremony tooling. It can export Solidity verifier contracts.

### [ZKProof] ZKProof Standards. ZKProof Community Reference / standards effort.
- URL/DOI: https://zkproof.org ; reference document https://docs.zkproof.org/reference.pdf
- Verified: yes (homepage title "ZKProof Standards" fetched); partial for the PDF
- Supports: An open industry-academic initiative to standardise ZKP terminology, security and interoperability.

### [BGM17] Bowe, S., Gabizon, A., Miers, I. (2017). Scalable Multi-party Computation for zk-SNARK Parameters in the Random Beacon Model. IACR ePrint 2017/1050.
- URL/DOI: https://eprint.iacr.org/2017/1050
- Verified: yes (fetched)
- Supports: The "Powers of Tau" MPC for Groth16 CRS generation, which needs no precommitment round so participants need not be fixed in advance. Used for the Zcash Sapling ceremony. The ePrint abstract names only "Zcash", not Sapling.

---

## A3. ZK and blockchain

### [Nakamoto08] Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.
- URL/DOI: https://bitcoin.org/bitcoin.pdf
- Verified: yes (PDF reachable, application/pdf)
- Supports: The original public blockchain design, in which full transparency of transactions motivates later privacy work such as Zerocash.

### [Zerocash14] Ben-Sasson, E., Chiesa, A., Garman, C., Green, M., Miers, I., Tromer, E., Virza, M. (2014). Zerocash: Decentralized Anonymous Payments from Bitcoin. IEEE S&P 2014, pp. 459-474.
- URL/DOI: https://doi.org/10.1109/SP.2014.36
- Verified: yes (Crossref metadata)
- Supports: The first deployed-scale use of zk-SNARKs for private payments, and the basis of Zcash.

### [ZcashSpec] Hopwood, D., Bowe, S., Hornby, T., Wilcox, N. Zcash Protocol Specification.
- URL/DOI: https://zips.z.cash/protocol/protocol.pdf
- Verified: partial (PDF reachable, not parsed)
- Supports: The normative spec for Sprout, Sapling (Groth16 over BLS12-381) and Orchard (Halo 2).

### [SaplingMPC] Zcash Sapling Powers-of-Tau ceremony (2017-2018).
- URL/DOI: https://zkproof.org/2021/06/30/setup-ceremonies/ ; NCC Group audit https://www.nccgroup.com/uk/research-blog/security-considerations-of-zk-snark-parameter-multi-party-computation/
- Verified: partial (search results only)
- Supports: Secondary sources report "90+" contributors to the Sapling Powers-of-Tau ceremony. Do not cite an exact number such as 87 without a primary source.

### [EIP196] Reitwiessner, C. (2017). EIP-196: Precompiled contracts for addition and scalar multiplication on the elliptic curve alt_bn128.
- URL/DOI: https://eips.ethereum.org/EIPS/eip-196
- Verified: yes (fetched title)
- Supports: Adds the ECADD (0x06) and ECMUL (0x07) precompiles on BN254, activated in Byzantium. Needed for on-chain zk-SNARK verification.

### [EIP197] Buterin, V., Reitwiessner, C. (2017). EIP-197: Precompiled contracts for optimal ate pairing check on the elliptic curve alt_bn128.
- URL/DOI: https://eips.ethereum.org/EIPS/eip-197
- Verified: yes (fetched)
- Supports: Pairing-check precompile at 0x08, created 2017-02-06, activated in Byzantium. The original cost was 80,000·k + 100,000 gas for k pairs.

### [EIP1108] Salazar Cardozo, A., Williamson, Z. (2018). EIP-1108: Reduce alt_bn128 precompile gas costs.
- URL/DOI: https://eips.ethereum.org/EIPS/eip-1108
- Verified: yes (fetched)
- Supports: Reprices the BN254 precompiles:
  - ECADD: 500 to 150 gas
  - ECMUL: 40,000 to 6,000 gas
  - Pairing: 80,000·k + 100,000 to 34,000·k + 45,000 gas
  - Created 2018-05-21.

### [EIP1679] Ethereum (2019). EIP-1679: Hardfork Meta: Istanbul.
- URL/DOI: https://eips.ethereum.org/EIPS/eip-1679
- Verified: yes (fetched)
- Supports: Istanbul includes EIP-152, 1108, 1344, 1884, 2028 and 2200, and activated at mainnet block 9,069,000. News reports date this to 8 Dec 2019 (Decrypt).

### [GrothGas] Derived from [EIP1108] and [Groth16].
- URL/DOI: see above. A secondary analysis is at https://www.horizenlabs.io/blog/zk-analysis-the-true-cost-of-zk-verification
- Verified: partial (the arithmetic is from verified sources; the Horizen post was seen as a search result only)
- Supports: Groth16 verification uses a 4-pair pairing check on-chain (3 pairings plus the precomputed e(α,β) term, as snarkjs verifiers do). That costs 45,000 + 4×34,000 = 181,000 gas, plus about 6-7k gas per public input (ECMUL+ECADD) and the 21,000 tx base. Measured totals are typically about 200-250k gas. A BN254 Groth16 proof is 256 bytes uncompressed.

### [GuoBench24] Guo, H., Feng, Y., Wu, C., Li, Z., Xu, J. (2024). Benchmarking ZK-Friendly Hash Functions and SNARK Proving Systems for EVM-compatible Blockchains. arXiv:2409.01976.
- URL/DOI: https://arxiv.org/abs/2409.01976
- Verified: yes (abstract fetched). Partial for gas numbers: search snippet reports about 219k gas for a snarkjs Groth16 verify call and about 209k for Fflonk, not confirmed in the abstract.
- Supports: Benchmarks Groth16, PLONK and Fflonk verifiers and ZK-friendly hashes on EVM chains. Poseidon2 "reduces on-chain costs by 73%".

### [zkSync] Matter Labs. ZKsync Docs.
- URL/DOI: https://docs.zksync.io/
- Verified: yes (fetched)
- Supports: ZKsync is "a network of interoperable chains, secured by ZK". Its chains are ZK rollups settling on Ethereum.

### [Starknet] StarkWare / Starknet Foundation. Starknet Documentation.
- URL/DOI: https://docs.starknet.io/
- Verified: yes (fetched)
- Supports: Starknet is a Cairo-based ZK (STARK) L2 for scaling Ethereum. The page itself does not say "validity rollup".

### [PolygonZkEVM] Polygon Labs. Polygon zkEVM documentation.
- URL/DOI: https://docs.polygon.technology/zkEVM/
- Verified: partial (the URL now redirects to "Polygon CDK" docs; zkEVM content has been reorganised)
- Supports: Polygon's zkEVM rollup, now folded into Polygon CDK. Cite with care.

### [Scroll] Scroll. Scroll Documentation.
- URL/DOI: https://docs.scroll.io/en/home/
- Verified: yes (fetched)
- Supports: "Ethereum scaled, using zero knowledge." A zkEVM rollup.

### [Aztec] Aztec Labs. Aztec Network.
- URL/DOI: https://aztec.network
- Verified: yes (title fetched)
- Supports: Self-described as "The first decentralized, privacy-preserving L2 on Ethereum". Aztec's team co-authored PLONK.

### [Semaphore] Privacy & Scaling Explorations (Ethereum Foundation). Semaphore documentation.
- URL/DOI: https://docs.semaphore.pse.dev/ ; repo https://github.com/semaphore-protocol/semaphore
- Verified: yes (fetched)
- Supports: "a zero-knowledge protocol that allows you to cast a message" as a member of a group without revealing identity, with nullifiers to prevent double-signalling.

### [MACI] Privacy & Scaling Explorations. Minimal Anti-Collusion Infrastructure (MACI).
- URL/DOI: https://maci.pse.dev/
- Verified: yes (fetched)
- Supports: "a private, on-chain, voting system". Tallying is done off-chain and "ZK-proofs are submitted and verified on-chain".

### [WorldID] World (Tools for Humanity). World ID documentation.
- URL/DOI: https://docs.world.org/world-id/overview ; https://world.org/world-id
- Verified: yes (fetched)
- Supports: World ID lets people prove they are a unique human using ZK proofs generated on-device, "unlinkable across apps". It uses MPC for uniqueness checks.

### [zkLogin24] Baldimtsi, F., Chalkias, K., Ji, Y., Lindstrøm, J., Maram, D., Riva, B., Roy, A., Sedaghat, M., Wang, J. (2024). zkLogin: Privacy-Preserving Blockchain Authentication with Existing Credentials. ACM CCS 2024, pp. 3182-3196.
- URL/DOI: https://doi.org/10.1145/3658644.3690356
- Verified: yes (Crossref metadata)
- Supports: Deployed on Sui. Users authenticate to a blockchain with OpenID Connect JWTs (e.g. Google) via a Groth16 proof, without linking their OAuth identity on-chain.

### [zkEmail] ZK Email. Documentation; and Suegami, S. et al. (2026). Zero-Knowledge Proofs of Generalized Regular Expression Matching for Anonymized Email Verification. PoPETs 2026(4):740-771.
- URL/DOI: https://docs.zk.email/architecture/dkim-verification ; https://doi.org/10.56553/popets-2026-0143
- Verified: partial (search results; docs landing page reachable)
- Supports: ZK circuits verify an email's DKIM signature and regex-extract fields, so selected email content can be proven without revealing the whole email.

### [OFAC22] U.S. Department of the Treasury (2022). U.S. Treasury Sanctions Notorious Virtual Currency Mixer Tornado Cash (press release jy0916, 8 Aug 2022).
- URL/DOI: https://home.treasury.gov/news/press-releases/jy0916
- Verified: yes (fetched)
- Supports: Treasury says Tornado Cash "has been used to launder more than $7 billion worth of virtual currency since its creation in 2019", including over $455M stolen by the Lazarus Group.

### [VanLoon24] Van Loon v. Department of the Treasury, No. 23-50669 (5th Cir. Nov. 26, 2024).
- URL/DOI: judgment https://storage.courtlistener.com/recap/gov.uscourts.ca5.215798/gov.uscourts.ca5.215798.124.0.pdf
- Verified: partial. The judgment PDF is reachable (application/pdf). The holding was confirmed through secondary summaries (Justia, Jones Day/JD Supra, Mayer Brown).
- Supports: A unanimous panel (Jolly, Willett, Engelhardt) held that Tornado Cash's immutable smart contracts are not "property" under IEEPA, so OFAC exceeded its authority. It reversed and remanded.

### [OFAC25] U.S. Treasury (2025). Tornado Cash delisting (21 March 2025).
- URL/DOI: https://www.steptoe.com/en/news-publications/international-compliance-blog/treasury-department-delists-tornado-cash-following-the-fifth-circuits-decision.html (secondary). Primary Treasury release reportedly "sb0057", not fetched.
- Verified: partial
- Supports: OFAC removed Tornado Cash from the SDN list on 21 March 2025, after Van Loon. Developer Roman Semenov remained sanctioned.

---

## A4. ZK and identity / credentials

### [CL01] Camenisch, J., Lysyanskaya, A. (2001). An Efficient System for Non-transferable Anonymous Credentials with Optional Anonymity Revocation. EUROCRYPT 2001, LNCS 2045, pp. 93-118.
- URL/DOI: https://doi.org/10.1007/3-540-44987-6_7
- Verified: yes (Crossref metadata)
- Supports: The foundational anonymous-credential system, in which users prove possession of credentials in ZK, unlinkably across showings.

### [CL02] Camenisch, J., Lysyanskaya, A. (2003). A Signature Scheme with Efficient Protocols. SCN 2002, LNCS 2576, pp. 268-289.
- URL/DOI: https://doi.org/10.1007/3-540-36413-7_20
- Verified: yes (Crossref metadata)
- Supports: CL signatures, with efficient ZK proofs of knowledge of a signature on committed values. This is the basis of Idemix and Hyperledger AnonCreds ("CL" credential definitions).

### [Idemix02] Camenisch, J., Van Herreweghen, E. (2002). Design and implementation of the idemix anonymous credential system. Proc. 9th ACM CCS, pp. 21-30.
- URL/DOI: https://doi.org/10.1145/586110.586114
- Verified: yes (Crossref metadata)
- Supports: IBM's Idemix implementation of CL-based anonymous credentials.

### [UProve] Paquin, C., Zaverucha, G. (2013; rev. 5 2023). U-Prove Cryptographic Specification V1.1. Microsoft.
- URL/DOI: https://www.microsoft.com/en-us/research/project/u-prove/
- Verified: partial (search results; the Microsoft page returned an error to the script)
- Supports: Microsoft's Brands-based minimal-disclosure tokens. The core scheme is standardised in ISO/IEC 18370-2:2016. Revision 5 is dated March 2023.

### [BBS04] Boneh, D., Boyen, X., Shacham, H. (2004). Short Group Signatures. CRYPTO 2004, LNCS 3152, pp. 41-55.
- URL/DOI: https://doi.org/10.1007/978-3-540-28628-8_3
- Verified: yes (Crossref metadata)
- Supports: The origin of the "BBS" signature, later extended (BBS+) to multi-message signatures with ZK selective disclosure.

### [BBS-IRTF] Looker, T., Kalos, V., Whitehead, A., Lodder, M., Bernstein, G. (2026). The BBS Signature Scheme. draft-irtf-cfrg-bbs-signatures-13 (IRTF CFRG Internet-Draft).
- URL/DOI: https://datatracker.ietf.org/doc/draft-irtf-cfrg-bbs-signatures/
- Verified: yes (fetched; v13 dated 13 Oct 2026)
- Supports: Signs multiple messages into one constant-size signature. A holder can prove possession of the signature while disclosing any subset of messages, with zero-knowledge, unlinkable proofs. This is still an Internet-Draft, not an RFC.

### [VC-BBS] Bernstein, G., Sporny, M. (eds.) (2026). Data Integrity BBS Cryptosuites v1.0. W3C Candidate Recommendation Draft, 10 Sep 2026.
- URL/DOI: https://www.w3.org/TR/vc-di-bbs/
- Verified: yes (fetched)
- Supports: "utilizes BBS signatures to provide selective disclosure and unlinkable derived proofs" for W3C VCs.

### [RFC9901] Fett, D., Yasuda, K., Campbell, B. (2025). Selective Disclosure for JSON Web Tokens (SD-JWT). RFC 9901, IETF, November 2025.
- URL/DOI: https://www.rfc-editor.org/rfc/rfc9901.html
- Verified: yes (title fetched; number confirmed as RFC 9901)
- Supports: The salted-hash-based selective disclosure standard for JWTs. Its hashed digests are not zero-knowledge and are linkable across presentations unless batch-issued.

### [VCDM2] Sporny, M. et al. (eds.) (2025). Verifiable Credentials Data Model v2.0. W3C Recommendation, 15 May 2025.
- URL/DOI: https://www.w3.org/TR/vc-data-model-2.0/
- Verified: yes (fetched)
- Supports: Defines a VC as "A tamper-evident credential whose authorship can be cryptographically verified". It also defines selective disclosure and allows ZK-derived presentations.

### [DIDCore] Sporny, M., Longley, D., Sabadello, M., Reed, D., Steele, O., Allen, C. (eds.) (2022). Decentralized Identifiers (DIDs) v1.0. W3C Recommendation, 19 July 2022.
- URL/DOI: https://www.w3.org/TR/did-core/
- Verified: yes (fetched)
- Supports: A DID is "A globally unique persistent identifier that does not require a centralized registration authority".

### [AnonCreds] Curran, S., Philipp, A., Yildiz, H., et al. AnonCreds Specification v1.0 (Draft). Hyperledger / OpenWallet Foundation.
- URL/DOI: https://anoncreds.github.io/anoncreds-spec/ (the hyperledger.github.io URL redirects here)
- Verified: yes (fetched)
- Supports: Uses CL signatures ("CL-RSA signatures over a block of L messages") and supports ZK predicates (<, <=, >, >=). An example is proving age over 18 without revealing the date of birth.

### [iden3] iden3. Iden3 Documentation (protocol, circuits).
- URL/DOI: https://docs.iden3.io/
- Verified: yes (title fetched)
- Supports: The iden3 protocol and circom circuits underlying Polygon ID / Privado ID: Merkle-tree identity state and ZK credential queries.

### [PrivadoID] Privado ID (formerly Polygon ID). Privado ID Documentation.
- URL/DOI: https://docs.privado.id/
- Verified: yes (fetched)
- Supports: Users can prove facts from a credential "without revealing the underlying data" and choose which fields to share. Verification can happen off-chain or on-chain.

### [zkcreds23] Rosenberg, M., White, J., Garman, C., Miers, I. (2023). zk-creds: Flexible Anonymous Credentials from zkSNARKs and Existing Identity Infrastructure. IEEE S&P 2023, pp. 790-808.
- URL/DOI: https://doi.org/10.1109/SP46215.2023.10179430
- Verified: yes (Crossref metadata)
- Supports: Builds anonymous credentials from general-purpose zkSNARKs over existing documents (e.g. passports), with no issuer changes needed.

### [FrigoShelat24] Frigo, M., shelat, a. (2024). Anonymous credentials from ECDSA. IACR ePrint 2024/2010 (Communications in Cryptology, 2026).
- URL/DOI: https://eprint.iacr.org/2024/2010
- Verified: yes (fetched)
- Supports: ZK proofs over existing ECDSA-signed ISO mdoc credentials, using sumcheck and Ligero with SHA-256 as the only assumption. "ECDSA proofs can be generated in about 20 ms". mdoc presentation proofs take "a few hundred milliseconds" on phones. The example application is proving age >18.

### [GoogleZK25] Stapelberg, A. (Google) (2025). Opening up 'Zero-Knowledge Proof' technology to promote privacy in age assurance. Google blog, 3 July 2025.
- URL/DOI: https://blog.google/technology/safety-security/opening-up-zero-knowledge-proof-technology-to-promote-privacy-in-age-assurance/ ; code https://github.com/google/longfellow-zk
- Verified: partial (search result showing the blog content; repo URL reachable)
- Supports: Google open-sourced its ZKP libraries (longfellow-zk) for age assurance in Google Wallet. The post cites eIDAS encouragement of ZKP in EU Digital Identity Wallets.

### [AppleID25] Apple Digital ID (passport-based, Apple Wallet), launched 12 Nov 2025. Coverage: TechCrunch.
- URL/DOI: https://techcrunch.com/2025/11/12/apple-launches-digital-id-a-way-to-carry-your-passport-on-your-phone-for-use-at-tsa-checkpoints
- Verified: partial (search results only)
- Supports: Apple Digital ID supports selective-disclosure age checks (e.g. over 21 without name or birthday) at TSA and in apps. Sources describe selective disclosure, not ZK proofs, so do not claim Apple uses ZKPs.

### [EUDI-ARF] European Commission. EUDI Wallet Architecture and Reference Framework (ARF), v3.0.0, 21 July 2026.
- URL/DOI: https://eudi.dev/latest/ (redirect from eu-digital-identity-wallet.github.io/eudi-doc-architecture-and-reference-framework/latest/)
- Verified: yes (fetched)
- Supports: The ARF index lists discussion topic "G - Zero Knowledge Proof" and technical specification TS4, "Specification of Zero-Knowledge Proof (ZKP) Implementation in EUDI Wallet", plus related TS13 (zkSNARK) and TS14. Earlier analyses note that the ARF's baseline formats (SD-JWT VC, mdoc) are linkable.

### [AEPD-TopicG] Agencia Española de Protección de Datos. Response to ARF Topic G (Zero Knowledge Proof).
- URL/DOI: https://www.aepd.es/documento/topicg-aepd-response.pdf
- Verified: partial (search result)
- Supports: Spain's data protection authority (AEPD) recommends making ZKP the default for EUDI Wallet transactions, revealing identity only where a use case requires it.

### [ISO18013-5] ISO/IEC 18013-5:2021. Personal identification. ISO-compliant driving licence. Part 5: Mobile driving licence (mDL) application.
- URL/DOI: https://www.iso.org/standard/69084.html
- Verified: partial (the ISO page is behind a bot check; content confirmed via secondary sources, e.g. https://pomcor.com/2023/10/27/overview-of-iso-iec-18013-5-innovations-and-vulnerabilities-in-the-mdl-standard/)
- Supports: mDL selective disclosure works by salted hashing in a signed Mobile Security Object, with each element requested and released individually. It does not give full unlinkability against issuer-verifier collusion.

### [Mazzocca25] Mazzocca, C., Acar, A., Uluagac, S., Montanari, R., Bellavista, P., Conti, M. (2025). A Survey on Decentralized Identifiers and Verifiable Credentials. IEEE Communications Surveys & Tutorials 27(6):3641-3671.
- URL/DOI: https://doi.org/10.1109/COMST.2025.3543197
- Verified: yes (Crossref metadata)
- Supports: A comprehensive survey of DIDs and VCs beyond human SSI, including IoT and edge entities, covering threats, implementations and adoption.

### [Yang20] Yang, X., Li, W. (2020). A zero-knowledge-proof-based digital identity management scheme in blockchain. Computers & Security 99:102050.
- URL/DOI: https://doi.org/10.1016/j.cose.2020.102050
- Verified: yes (Crossref metadata)
- Supports: BZDIMS uses ZKP and smart contracts so users can selectively disclose ownership of attributes with identity unlinkability.

### [Dieye23] Dieye, M., Valiorgue, P., Gelas, J.-P., Diallo, E.-H., Ghodous, P., Biennier, F., et al. (2023). A Self-Sovereign Identity Based on Zero-Knowledge Proof and Blockchain. IEEE Access 11:49445-49455.
- URL/DOI: https://doi.org/10.1109/ACCESS.2023.3268768
- Verified: yes (Crossref metadata)
- Supports: A discrete-log ZKP-based SSI protocol claimed to be eIDAS/GDPR compliant, with zero disclosure to service providers.

### [zkSSI24] Hoang, A.-T., Ileri, C.U., Sanders, W., Schulte, S. (2024). zkSSI: A Zero-Knowledge-Based Self-Sovereign Identity Framework. IEEE Blockchain 2024, pp. 276-285.
- URL/DOI: https://doi.org/10.1109/Blockchain62396.2024.00043
- Verified: yes (Crossref metadata)
- Supports: zk-SNARK-based SSI that supports compound logical predicates over VCs, verified on- or off-chain. It is compared against Polygon ID and zk-creds.

---

## A5. Vehicle / V2X privacy and ZK

### [RayaHubaux07] Raya, M., Hubaux, J.-P. (2007). Securing vehicular ad hoc networks. Journal of Computer Security 15(1):39-68.
- URL/DOI: https://doi.org/10.3233/JCS-2007-15103
- Verified: yes (Crossref metadata)
- Supports: A foundational VANET security architecture using large sets of anonymous (pseudonymous) keys for privacy.

### [Petit15] Petit, J., Schaub, F., Feiri, M., Kargl, F. (2015). Pseudonym Schemes in Vehicular Networks: A Survey. IEEE Communications Surveys & Tutorials 17(1):228-255.
- URL/DOI: https://doi.org/10.1109/COMST.2014.2345420
- Verified: yes (Crossref metadata)
- Supports: The standard survey of pseudonym-certificate schemes and their linkability limits in V2X.

### [Whyte13] Whyte, W., Weimerskirch, A., Kumar, V., Hehn, T. (2013). A security credential management system for V2V communications. IEEE VNC 2013, pp. 1-8.
- URL/DOI: https://doi.org/10.1109/VNC.2013.6737583
- Verified: yes (Crossref metadata)
- Supports: The original SCMS proposal (USDOT/CAMP). It uses butterfly keys and short-lived pseudonym certificates so that no single component can link a vehicle's certificates.

### [Brecht18] Brecht, B., Therriault, D., Weimerskirch, A., Whyte, W., Kumar, V., Hehn, T., Goudy, R. (2018). A Security Credential Management System for V2X Communications. IEEE Trans. Intelligent Transportation Systems 19(12):3850-3871.
- URL/DOI: https://doi.org/10.1109/TITS.2018.2797529
- Verified: yes (Crossref metadata)
- Supports: The full journal description of the SCMS design adopted in US V2X deployments.

### [IEEE1609.2] IEEE Std 1609.2-2022. IEEE Standard for Wireless Access in Vehicular Environments: Security Services for Application and Management Messages.
- URL/DOI: https://standards.ieee.org/ieee/1609.2/10258/
- Verified: partial (IEEE page behind Cloudflare; metadata via ANSI webstore and search results)
- Supports: Defines WAVE secure message formats and certificates (including pseudonym certificates). Published 3 Dec 2022, it supersedes 1609.2-2016, 2a-2017 and 2b-2019. Companion standard IEEE 1609.2.1 covers certificate management.

### [MOBI-VID] MOBI (Mobility Open Blockchain Initiative) (2019). MOBI announces first Vehicle Identity (VID) standard on blockchain.
- URL/DOI: https://dlt.mobi/mobi-announces-the-first-vehicle-identity-vid-standard-on-blockchain-in-collaboration-with-groupe-renault-ford-and-bmw-among-others/
- Verified: partial (search results of the press release; July 2019)
- Supports: VID Phase I gives new vehicles a blockchain "birth" digital identity anchored to the VIN. The working group was chaired by Groupe Renault and Ford, with BMW, GM, Honda and others.

### [Rasheed20] Rasheed, A.A., Mahapatra, R.N., Hamza-Lup, F.G. (2020). Adaptive Group-Based Zero Knowledge Proof-Authentication Protocol in Vehicular Ad Hoc Networks. IEEE Trans. ITS 21(2):867-881.
- URL/DOI: https://doi.org/10.1109/TITS.2019.2899321
- Verified: yes (Crossref metadata)
- Supports: A group-based ZKP authentication protocol (AGZKP-AP) for VANETs with tunable privacy levels.

### [Terzi20] Terzi, S., Savvaidis, C., Votis, K., Tzovaras, D., Stamelos, I. (2020). Securing Emission Data of Smart Vehicles with Blockchain and Self-Sovereign Identities. IEEE Blockchain 2020, pp. 462-469.
- URL/DOI: https://doi.org/10.1109/Blockchain50366.2020.00067
- Verified: yes (Crossref metadata)
- Supports: Hyperledger Indy SSI (AnonCreds-based ZKP) for vehicles on a Hyperledger Fabric network for emissions certification. An early SSI-for-vehicles paper.

### [Feng20] Feng, Q., He, D., Zeadally, S., Liang, K. (2020). BPAS: Blockchain-Assisted Privacy-Preserving Authentication System for Vehicular Ad Hoc Networks. IEEE Trans. Industrial Informatics 16(6):4146-4155.
- URL/DOI: https://doi.org/10.1109/TII.2019.2948053
- Verified: yes (Crossref metadata)
- Supports: Blockchain-assisted VANET authentication with conditional tracing and dynamic revocation, needing no online registration centre.

### [Parameswarath22] Parameswarath, R.P., Gope, P., Sikdar, B. (2022). User-empowered Privacy-preserving Authentication Protocol for Electric Vehicle Charging Based on Decentralized Identity and Verifiable Credential. ACM TMIS 13(4):1-21.
- URL/DOI: https://doi.org/10.1145/3532869
- Verified: yes (Crossref metadata)
- Supports: DID/VC-based anonymous EV-charging authentication with ZKP-style security.

### [LiBDRA23] Li, X., Jing, T., Li, R., Li, H., Wang, X., Shen, D. (2023). BDRA: Blockchain and Decentralized Identifiers Assisted Secure Registration and Authentication for VANETs. IEEE Internet of Things Journal 10(14):12140-12155.
- URL/DOI: https://doi.org/10.1109/JIOT.2022.3164147
- Verified: yes (Crossref metadata)
- Supports: Uses DIDs for decentralised vehicle registration. Reports cross-section re-registration that "reduces the communication time by 30%".

### [LiPlatoon23] Li, W., Meese, C., Guo, H., Nejad, M. (2023). Aggregated Zero-Knowledge Proof and Blockchain-Empowered Authentication for Autonomous Truck Platooning. IEEE Trans. ITS 24(9):9309-9323.
- URL/DOI: https://doi.org/10.1109/TITS.2023.3271436
- Verified: yes (Crossref metadata)
- Supports: Aggregated ZKP identity verification for joining truck platoons on Hyperledger. Reports "a constant verification time of 500 milliseconds regardless of the number of proofs".

### [Shahrouz24] Shahrouz, J.K., Analoui, M. (2024). An anonymous authentication scheme with conditional privacy-preserving for Vehicular Ad hoc Networks based on zero-knowledge proof and Blockchain. Ad Hoc Networks 154:103349.
- URL/DOI: https://doi.org/10.1016/j.adhoc.2023.103349
- Verified: yes (Crossref metadata)
- Supports: Simulation-extractable zk-SNARKs for VANET anonymity. Notes that zk-SNARK proof generation time "poses a major obstacle" in time-sensitive VANETs, and caches repeated computations on-chain to mitigate this.

### [Jiang24] Jiang, W., Lv, X. (2024). A Distributed Internet of Vehicles Data Privacy Protection Method Based on Zero-Knowledge Proof and Blockchain. IEEE Trans. Vehicular Technology 73(5):6332-6345.
- URL/DOI: https://doi.org/10.1109/TVT.2023.3345272
- Verified: yes (Crossref metadata)
- Supports: Non-interactive Schnorr ZKP for vehicle-RSU authentication with IPFS and Fabric. Vehicle authentication overhead is "only 1728 bits".

### [Liu24ATRC] Liu, Y., He, D., Luo, M., Wang, H., Liu, Q. (2024). ATRC: An Anonymous Traceable and Revocable Credential System Using Blockchain for VANETs. IEEE Trans. Vehicular Technology 73(2):2482-2494.
- URL/DOI: https://doi.org/10.1109/TVT.2023.3312547
- Verified: yes (Crossref metadata)
- Supports: Decentralised anonymous credentials for vehicles, with traceability and a Merkle-tree whitelist for revocation.

### [Zhang24] Zhang, X., Chen, X., Liu, Y., Zhong, H. (2024). Anonymous Authentication and Information Sharing Scheme Based on Blockchain and Zero Knowledge Proof for VANETs. IEEE Trans. Vehicular Technology 73(12):18043-18058.
- URL/DOI: https://doi.org/10.1109/TVT.2024.3432553
- Verified: yes (Crossref metadata)
- Supports: zk-SNARK plus blockchain/IPFS for anonymous V2R/V2V task sharing with pseudonyms from a trusted authority.

### [AlMarshoud24] AlMarshoud, M., Sabir Kiraz, M., Al-Bayatti, A.H. (2024). Security, Privacy, and Decentralized Trust Management in VANETs: A Review of Current Research and Future Directions. ACM Computing Surveys 56(10):1-39.
- URL/DOI: https://doi.org/10.1145/3656166
- Verified: yes (Crossref metadata)
- Supports: A survey of decentralised (blockchain, wallet, threshold-key) approaches versus PKI/SCMS in VANETs.

### [ZhangTIFS25] Zhang, J., Wang, et al. (2025). A Decentralized Threshold Credential Management With Fine-Grained Authentication for VANETs. IEEE Trans. Information Forensics and Security 20:5818-5831.
- URL/DOI: https://doi.org/10.1109/TIFS.2025.3577433
- Verified: yes (Crossref metadata)
- Supports: Threshold-issued anonymous credentials for vehicles with selective attribute disclosure, aggregation and randomisation.

### [Chen25] Chen, X., Zhang, X., Zhong, H., Liu, Y. (2025). Anonymous authentication based on blockchain and zero-knowledge proof for vehicular ad hoc networks. The Journal of Supercomputing (Oct 2025).
- URL/DOI: https://doi.org/10.1007/s11227-025-07912-5
- Verified: yes (Crossref metadata)
- Supports: zk-SNARK + ECC + blockchain/IPFS anonymous vehicle identity verification that reduces RSU and vehicle costs.

### [Hasan26] Hasan, M., Vassilev, A., Griffor, E., Gamage, T. (2026). Hermes' Seal: Zero-Knowledge Assurance for Autonomous Vehicle Communications. IEEE Security & Privacy.
- URL/DOI: https://doi.org/10.1109/MSEC.2026.3735626
- Verified: yes (Crossref metadata)
- Supports: A zk-SNARK framework for V2V/V2I proofs of AV perception computations. Reports "8 ms proof generation and 1 ms verification on a GPU".

---

## A6. Benchmarks

### [zkBench23] Ernstberger, J., Chaliasos, S., Kadianakis, G., Steinhorst, S., Jovanovic, P., Gervais, A., Livshits, B., Orrù, M. (2023). zk-Bench: A Toolset for Comparative Evaluation and Performance Benchmarking of SNARKs. IACR ePrint 2023/1503.
- URL/DOI: https://eprint.iacr.org/2023/1503
- Verified: yes (fetched)
- Supports: Benchmarks 13 elliptic curves in 9 libraries and 5 ZKP tools (including circom/snarkjs). Its PlonK estimator is accurate to 6-32%.
- (Also see [GuoBench24], [GrothGas], [EIP1108] in section 3.)

### [Hashcat4090] hashcat forum (2025). NVIDIA RTX 4090 Benchmark, hashcat v7.0.0.
- URL/DOI: https://hashcat.net/forum/post-63595.html
- Verified: yes (fetched)
- Supports: A single RTX 4090 reaches the following rates. This shows unsalted fast hashes of low-entropy identifiers (e.g. VINs) can be brute-forced.

  | Hash (mode) | Rate |
  |---|---|
  | SHA2-256 (1400) | 22,138.4 MH/s (about 22 GH/s) |
  | MD5 (0) | 163.4 GH/s |
  | SHA2-512 (1700) | 7,532.9 MH/s |
  | bcrypt (3200) | 212.6 kH/s |

---

## A7. Hashing / crypto foundations

### [FIPS180-4] NIST (2015). FIPS PUB 180-4: Secure Hash Standard (SHS). August 2015.
- URL/DOI: https://doi.org/10.6028/NIST.FIPS.180-4 ; https://csrc.nist.gov/pubs/fips/180-4/upd1/final
- Verified: yes (fetched)
- Supports: Specifies the SHA-1 and SHA-2 family (including SHA-256).

### [FIPS202] NIST (2015). FIPS PUB 202: SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions. August 2015.
- URL/DOI: https://doi.org/10.6028/NIST.FIPS.202
- Verified: yes (fetched)
- Supports: Specifies SHA3-224/256/384/512, SHAKE128/256 and the Keccak-p permutation. Ethereum's Keccak-256 is the pre-standard Keccak padding, not SHA3-256.

### [SEC2] Certicom Research (2010). SEC 2: Recommended Elliptic Curve Domain Parameters, Version 2.0, 27 Jan 2010.
- URL/DOI: https://www.secg.org/sec2-v2.pdf
- Verified: yes (PDF downloaded; title page read)
- Supports: Defines secp256k1 (used by Bitcoin/Ethereum keys) and other curves.

### [Merkle87] Merkle, R.C. (1988). A Digital Signature Based on a Conventional Encryption Function. CRYPTO '87, LNCS 293, pp. 369-378.
- URL/DOI: https://doi.org/10.1007/3-540-48184-2_32
- Verified: yes (Crossref metadata)
- Supports: Introduces the hash-tree (Merkle tree) authentication used in blockchains and in ZK membership proofs. (Merkle's 1979 Stanford thesis/patent was not verified.)

### [DH76] Diffie, W., Hellman, M. (1976). New directions in cryptography. IEEE Trans. Information Theory 22(6):644-654.
- URL/DOI: https://doi.org/10.1109/TIT.1976.1055638
- Verified: yes (Crossref metadata)
- Supports: The founding paper of public-key cryptography and Diffie-Hellman key exchange.

### [RSA78] Rivest, R., Shamir, A., Adleman, L. (1978). A method for obtaining digital signatures and public-key cryptosystems. Communications of the ACM 21(2):120-126.
- URL/DOI: https://doi.org/10.1145/359340.359342
- Verified: yes (Crossref metadata)
- Supports: The RSA public-key cryptosystem and signatures.

# Part B. Human computation, data economy, SSI, agents, inference attacks, analogies

## B1. Hand computation, human error, checksums

### [SHIRRIFF2014] Shirriff, K. (2014). Mining Bitcoin with pencil and paper: 0.67 hashes per day. Ken Shirriff's blog (righto.com), Sept 2014.
- URL/DOI: http://www.righto.com/2014/09/mining-bitcoin-with-pencil-and-paper.html
- Verified: yes
- Supports: Manual SHA-256 is infeasible. "Completing this round took me 16 minutes, 45 seconds"; a full block hash "would take 1.49 days, for a hash rate of 0.67 hashes per day"; hardware is "about a quintillion times faster"; ~10^16 less energy efficient.

### [BARCHARD2011] Barchard, K. A., & Pace, L. A. (2011). Preventing human error: The impact of data entry methods on data accuracy and statistical results. Computers in Human Behavior, 27(5), 1834–1839.
- URL/DOI: https://doi.org/10.1016/j.chb.2011.04.004 (abstract PDF: https://online210.psych.wisc.edu/wp-content/uploads/PSY-210_Unit_Materials/PSY-210_Unit05_Materials/Barchard_abstract_CHB_2011.pdf)
- Verified: yes (abstract text extracted from PDF)
- Supports: Humans mis-transcribe data. 195 participants; "Visual checking resulted in 2958% more errors than double entry, and was not significantly better than single entry"; 66% of visual-checkers got coefficient alpha wrong. (2958% = ~30x, consistent with the authors' lab summary of "roughly 30 times as many errors".)

### [GOLDBERG2008] Goldberg, S. I., Niemierko, A., & Turchin, A. (2008). Analysis of data errors in clinical research databases. AMIA Annual Symposium Proceedings 2008, 242–246.
- URL/DOI: https://pmc.ncbi.nlm.nih.gov/articles/PMC2656002/ (PMID 18998889)
- Verified: yes (abstract)
- Supports: Real-world manual entry errors are high: "Error rates detected by the double-entry method ranged from 2.3 to 26.9%"; constraint-based alarms "prevent only a small fraction of errors."

### [NAHM2008] Nahm, M. L., Pieper, C. F., & Cunningham, M. M. (2008). Quantifying data quality for clinical trials using electronic data capture. PLoS ONE, 3(8), e3049.
- URL/DOI: https://doi.org/10.1371/journal.pone.0003049 (PMC2516178)
- Verified: yes (abstract)
- Supports: Even professional, audited entry errs: source-to-database error rate 14.3 errors per 10,000 fields; published CRF-to-database average ~14 per 10,000 fields.

### [PANKO-BASIC] Panko, R. R. (n.d., maintained). Human Error Website – Basic error rates (Table 1).
- URL/DOI: http://panko.com/HumanErr/SimpleNontrivial.html
- Verified: partial (compilation page; underlying studies not individually fetched; page's in-text and reference-list years disagree)
- Supports: Classic per-character keying error baseline: "Residual typing errors per character" 0.6% (Shaffer & Hardwick); entering a mail code 0.5% (Baddeley & Longman); 10 digits into a calculator 5%.

### [SOUKOREFF2003] Soukoreff, R. W., & MacKenzie, I. S. (2003). Metrics for text entry research: An evaluation of MSD and KSPC, and a new unified error metric. Proc. CHI 2003, 113–120.
- URL/DOI: https://doi.org/10.1145/642611.642632 (author page: https://www.yorku.ca/mack/chi03.html)
- Verified: yes (bibliographic + abstract)
- Supports: Methodological citation for measuring human text-entry error: defines a "unified total error rate" combining corrected and not-corrected errors.

### [EIP55] Buterin, V., & Van de Sande, A. (2016). EIP-55: Mixed-case checksum address encoding. Ethereum Improvement Proposals.
- URL/DOI: https://eips.ethereum.org/EIPS/eip-55
- Verified: yes
- Supports: Checksums mitigate but do not eliminate human address errors: "the net probability that a randomly generated address if mistyped will accidentally pass a check is 0.0247%." Created 2016-01-14.

### [BIP173] Wuille, P., & Maxwell, G. (2017). BIP-173: Base32 address format for native v0-16 witness outputs (Bech32).
- URL/DOI: https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
- Verified: yes
- Supports: BCH checksum "guarantees detection of any error affecting at most 4 characters" and has <1 in 10^9 chance of missing more; 2024 note: not robust to insert/delete of <5 consecutive characters.

### [BASE58CHECK] Base58Check encoding (Bitcoin legacy addresses), 4-byte double-SHA256 checksum.
- URL/DOI: https://hub.bsvblockchain.org/wiki/addresses-and-wallets/bitcoin-address/base58check-encoding ; https://www.spark.money/glossary/checksum
- Verified: partial (secondary technical references; Bitcoin Wiki page not fetched)
- Supports: 32-bit checksum → undetected random error ≈ 1 in 2^32 (~4.29 billion), with no structured guarantee about error patterns.

### [BIP39] Palatinus, M., Rusnak, P., Voisine, A., & Bowe, S. (2013). BIP-39: Mnemonic code for generating deterministic keys.
- URL/DOI: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
- Verified: yes
- Supports: Human-facing key backup burden: 2,048-word list; 12–24 words encode 128–256 bits + ENT/32 checksum; purpose is "to transport computer-generated randomness with a human-readable transcription."

---

## B2. Crypto loss, scams, wallet UX, account abstraction, passkeys

### [CHAINALYSIS-LOST] Chainalysis (2020, June). Lost-bitcoin estimate (≈3.7M BTC unmoved ≥5 yrs), as reported by Decrypt (Phillips, 3 Jan 2021) and Cointelegraph (6 Feb 2022).
- URL/DOI: https://decrypt.co/37171/lost-bitcoin-3-7-million-bitcoin-are-probably-gone-forever ; https://cointelegraph.com/news/lost-bitcoin-may-be-a-donation-but-is-it-hindering-adoption
- Verified: partial (Chainalysis primary blog post not retrievable; figure confirmed via two outlets citing it)
- Supports: "around 3.7 million BTC hasn't been touched for at least half a decade" ≈ 20% of supply; Chainalysis' Kim Grauer called it "a bit old" (2022). Earlier Chainalysis range: 2.78–3.79M BTC (17–23%); a later Chainalysis framing 2.3–3.7M. Cite as an estimate, not a fact.

### [TSUCHIYA2025] Tsuchiya, T., Dong, J.-D., Soska, K., & Christin, N. (2025). Blockchain Address Poisoning. 34th USENIX Security Symposium.
- URL/DOI: https://www.usenix.org/conference/usenixsecurity25/presentation/tsuchiya ; arXiv:2501.16681
- Verified: yes
- Supports: Address-copying UX is attacked at scale: 270M on-chain attack attempts targeting 17M victims; 6,633 incidents causing ≥ US$83.8M losses (Ethereum + BSC, Jul 2022–Jun 2024).

### [WBTC-POISON-2024] Cointelegraph (May 2024). WBTC address poisoner returns all funds after negotiations.
- URL/DOI: https://cointelegraph.com/news/wbtc-address-poisoner-all-funds-negotiations
- Verified: partial (news report; date reported as 3 May (Cyvers) or 5 May 2024)
- Supports: Single victim sent 1,155 WBTC (~US$68M) to a look-alike address; ~22,960 ETH later returned after negotiation.

### [SCAMSNIFFER2024] Scam Sniffer (2025, Jan). 2024 Web3 Phishing Attacks Report – Wallet drainers drain $494 million.
- URL/DOI: https://drops.scamsniffer.io/?p=971 (mirror: https://defihacklabs.substack.com/p/scam-sniffer-2024-web3-phishing-attacks)
- Verified: partial (vendor report)
- Supports: Signing-prompt phishing: ~US$494M stolen from 332,000 addresses in 2024 (+67% YoY); 30 cases >$1M; largest single loss ~$55.5M.

### [CHAINALYSIS2025] Chainalysis Team (2025, 15 Jan). 2025 Crypto Crime Trends / 2025 Crypto Crime Report.
- URL/DOI: https://www.chainalysis.com/blog/2025-crypto-crime-report-introduction/
- Verified: yes
- Supports: "value received by illicit cryptocurrency addresses to a total of $40.9 billion" (lower bound, 2024); "Stolen funds increased by approximately 21% YoY to $2.2 billion"; private-key compromises 43.8% of stolen crypto (report body, via The Block).

### [ESKANDARI2015] Eskandari, S., Barrera, D., Stobert, E., & Clark, J. (2015). A first look at the usability of Bitcoin key management. NDSS Workshop on Usable Security (USEC 2015). arXiv:1802.04351.
- URL/DOI: https://arxiv.org/abs/1802.04351 ; https://www.ndss-symposium.org/ndss2015/ndss-2015-usec-programme/first-look-usability-bitcoin-key-management
- Verified: yes
- Supports: Bitcoin forces users onto "public key cryptography, which has a number of security and usability challenges"; evaluated six clients; keys must be accessible yet protected from theft and loss.

### [KROMBHOLZ2016] Krombholz, K., Judmayer, A., Gusenbauer, M., & Weippl, E. (2016). The other side of the coin: User experiences with Bitcoin security and privacy. Financial Cryptography and Data Security 2016, LNCS 9603, 555–580.
- URL/DOI: https://doi.org/10.1007/978-3-662-54970-4_33 ; https://eprints.cs.univie.ac.at/6493
- Verified: yes (abstract)
- Supports: Survey of 990 users: "22% of our participants have already lost money due to security breaches or self-induced errors"; ~46% use web-hosted (custodial) wallets.

### [VOSKOBOJNIKOV2021] Voskobojnikov, A., Wiese, O., Mehrabi Koushki, M., Roth, V., & Beznosov, K. (2021). The U in Crypto Stands for Usable: An empirical study of user experience with mobile cryptocurrency wallets. CHI 2021, 642:1–642:14.
- URL/DOI: https://doi.org/10.1145/3411764.3445407 ; lab page https://lersse.ece.ubc.ca/?p=944
- Verified: partial (DOI + DBLP confirmed; ACM page 403; abstract figures via secondary summary)
- Supports: 45,821 app reviews of top-5 wallets, 6,859 analysed; UX issues "might lead to dangerous errors and irreversible monetary losses"; some users wrongly believed transactions reversible. (UBC lab – local relevance.)

### [METAMASK-MAU] Decrypt / Blockworks (2023). MetaMask passes 30 million monthly active users (ConsenSys).
- URL/DOI: https://decrypt.co/95039/metamask-consensys-30-million-users ; https://www.blockworks.com/news/metamask-monthly-active-users-blockaid
- Verified: partial (company-reported figure via press)
- Supports: Scale of self-custody UX burden: >30M MAU (peak 31.7M in Jan 2022), active = opened extension/app once per rolling 30 days.

### [ERC4337] Buterin, V., Weiss, Y., Tirosh, D., Nacson, S., Forshtat, A., Gazso, K., & Hess, T. (2021). ERC-4337: Account Abstraction Using Alt Mempool.
- URL/DOI: https://eips.ethereum.org/EIPS/eip-4337
- Verified: yes
- Supports: Industry moving key custody into programmable software: lets users "use Smart Contract Accounts containing arbitrary verification logic" instead of EOAs, enabling "custom recovery", multisig, paymasters. Created 2021-09-29.

### [WEBAUTHN3] W3C (2026). Web Authentication: An API for accessing Public Key Credentials, Level 3. W3C Recommendation, 25 Aug 2026.
- URL/DOI: https://www.w3.org/TR/webauthn-3/
- Verified: yes
- Supports: Standard for "strong, attested, scoped, public key-based credentials"; spec use-case describes "phishing-resistant sign in" – keys handled by authenticator software, never by the human.

### [FIDO-PASSKEYS] FIDO Alliance (n.d.). Passkeys.
- URL/DOI: https://fidoalliance.org/passkeys/
- Verified: yes
- Supports: "Passkeys are phishing resistant and secure by design"; FIDO-commissioned 2024 survey: 53% enabled passkeys on ≥1 account (vendor claim).

---

## B3. Data economy, regulation, breaches, connected cars

### [ZUBOFF2019] Zuboff, S. (2019). The Age of Surveillance Capitalism: The Fight for a Human Future at the New Frontier of Power. New York: PublicAffairs. ISBN 9781610395694.
- URL/DOI: https://www.hachettebookgroup.com/titles/shoshana-zuboff/the-age-of-surveillance-capitalism/9781610395694/
- Verified: partial (publisher listing; book text not fetched — quotes below are via reviews)
- Supports: Surveillance capitalism claims "human experience as free raw material" for prediction; "behavioral surplus" = behavioral data available for uses beyond service improvement. On sale 15 Jan 2019.

### [QI-PRODUCT] Quote Investigator (2017, 16 Jul). "You're not the customer; you're the product."
- URL/DOI: https://quoteinvestigator.com/2017/07/16/product/
- Verified: yes
- Supports: Origin: Serra & Schoolman's 1973 video "Television Delivers People" ("You are the product of t.v."); exact modern wording by MetaFilter user blue_beetle (Andrew Lewis), 26 Aug 2010: "If you are not paying for it, you're not the customer; you're the product being sold."

### [FB-CA-2018] Schroepfer, M. (2018, 4 Apr). An update on our plans to restrict data access on Facebook. Meta Newsroom.
- URL/DOI: https://about.fb.com/news/2018/04/restricting-data-access/
- Verified: yes
- Supports: Cambridge Analytica: "the Facebook information of up to 87 million people — mostly in the US —" may have been improperly shared (up from the earlier 50M).

### [GDPR] Regulation (EU) 2016/679 (General Data Protection Regulation). OJ L 119, 4.5.2016.
- URL/DOI: https://eur-lex.europa.eu/eli/reg/2016/679/oj (text checked via https://gdpr-info.eu/art-5-gdpr/, /art-17-gdpr/, /art-25-gdpr/)
- Verified: yes (article text via gdpr-info.eu mirror; EUR-Lex page did not render in fetcher)
- Supports: Art. 5(1)(c) data "adequate, relevant and limited to what is necessary"; Art. 17 "Right to erasure ('right to be forgotten')"; Art. 25 "Data protection by design and by default" – "by default, only personal data which are necessary for each specific purpose".

### [CNIL2018] CNIL (2018, Sept). Blockchain and the GDPR: Solutions for a responsible use of the blockchain in the context of personal data.
- URL/DOI: https://www.cnil.fr/en/blockchain-and-gdpr-solutions-responsible-use-blockchain-context-personal-data
- Verified: partial (page returned 503 at fetch time; content confirmed via search extract and IAPP: https://iapp.org/resources/article/first-elements-analysis-of-the-cnil-blockchain/)
- Supports: GDPR "does not aim at regulating technologies per se" but how actors use them; recommends DPIA and identifying controllers for on-chain personal data.

### [EDPB-2025] European Data Protection Board (2025). Guidelines 02/2025 on processing of personal data through blockchain technologies (adopted for consultation 14 Apr 2025; v2 final July 2026).
- URL/DOI: https://www.edpb.europa.eu/news/news/2025/edpb-adopts-guidelines-processing-personal-data-through-blockchains-and-ready_en ; v2 PDF https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202502_blockchain_v2_en.pdf
- Verified: yes (press release); partial for v2 content (via search extract)
- Supports: "storing personal data in a blockchain should be avoided" where it conflicts with DP principles; erasure "technically impracticable" on-chain → keep data off-chain, put only commitments/hashes on-chain (supports ZK + off-chain wallet design).

### [EIDAS2] Regulation (EU) 2024/1183 of 11 April 2024 amending Regulation (EU) No 910/2014 as regards establishing the European Digital Identity Framework. OJ L, 2024/1183, 30.4.2024.
- URL/DOI: https://eur-lex.europa.eu/eli/reg/2024/1183/oj
- Verified: partial (ELI/OJ reference and dates confirmed via EUR-Lex search result + Wikipedia; full text did not render in fetcher)
- Supports: Member States must offer EU Digital Identity Wallets (free to natural persons, voluntary); in force 20 May 2024 — i.e., the state itself is mandating a *software wallet* as the identity custodian.

### [EQUIFAX-FTC2019] U.S. Federal Trade Commission (2019, 22 Jul). Equifax to pay $575 million as part of settlement with FTC, CFPB, and States related to 2017 data breach.
- URL/DOI: https://www.ftc.gov/news-events/news/press-releases/2019/07/equifax-pay-575-million-part-settlement-ftc-cfpb-states-related-2017-data-breach
- Verified: yes
- Supports: Centralized identity-data honeypot: 2017 breach affected "approximately 147 million people"; settlement ≥$575M up to $700M.

### [MOZILLA-CARS-2023] Caltrider, J., Rykov, M., & MacDonald, Z. (2023, 6 Sept). "It's official: Cars are the worst product category we have ever reviewed for privacy." Mozilla Foundation, *Privacy Not Included.
- URL/DOI: https://www.mozillafoundation.org/en/privacynotincluded/articles/its-official-cars-are-the-worst-product-category-we-have-ever-reviewed-for-privacy/ ; press release https://www.mozillafoundation.org/en/blog/privacy-nightmare-on-wheels-every-car-brand-reviewed-by-mozilla-including-ford-volkswagen-and-toyota-flunks-privacy-test/
- Verified: partial (primary page 403 to fetcher; claims confirmed via Mozilla press-release search extract + KBB/Schneier coverage)
- Supports: "All 25 car brands we researched earned our *Privacy Not Included warning label"; 84% reserve right to share, 76% to sell data; none met Minimum Security Standards; 600 research hours.

### [HILL2024-NYT] Hill, K. (2024, 11 Mar). Automakers are sharing consumers' driving behavior with insurance companies. The New York Times.
- URL/DOI: https://www.nytimes.com/2024/03/11/technology/carmakers-driver-tracking-insurance.html
- Verified: partial (paywalled; date/content confirmed via multiple secondary reports; URL slug not independently fetched)
- Supports: GM OnStar Smart Driver data flowed via LexisNexis to insurers; one driver's LexisNexis report listed 640 trips with speeding/hard-braking events.

### [FTC-GM-2025] U.S. FTC (2025, 16 Jan). FTC takes action against General Motors for sharing drivers' precise location and driving behavior data without consent. (Final order: 14 Jan 2026.)
- URL/DOI: https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-takes-action-against-general-motors-sharing-drivers-precise-location-driving-behavior-data ; final: https://www.ftc.gov/news-events/news/press-releases/2026/01/ftc-finalizes-order-settling-allegations-gm-onstar-collected-sold-geolocation-data-without-consumers
- Verified: yes
- Supports: Data collected "without adequately notifying consumers and obtaining their affirmative consent"; GM/OnStar "banned for five years from disclosing consumers' sensitive geolocation and driver behavior data" to consumer reporting agencies.

### [PIPEDA] Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5 (Canada).
- URL/DOI: https://laws-lois.justice.gc.ca/eng/acts/P-8.6/
- Verified: yes (title and citation)
- Supports: Canadian private-sector privacy baseline applicable to connected-vehicle data in a UBC/Canadian context.

### [BILLC27] Fasken (2025, Jan). Prorogation's digital impact: Canada's digital bills set to die on the Order Paper (Bill C-27, Digital Charter Implementation Act, 2022).
- URL/DOI: https://fasken.com/en/knowledge/2025/01/prorogations-digital-impact ; https://thewirereport.ca/2025/01/10/four-cyber-bills-dead-as-parliament-prorogued
- Verified: partial (law-firm/trade-press sources)
- Supports: Bill C-27 (introduced June 2022; would have replaced PIPEDA Part 1 with the Consumer Privacy Protection Act) died on prorogation, 6 Jan 2025 — Canada's privacy modernisation remains unfinished.

### [DATABROKER-MKT] SNS Insider (2025, 18 Feb). Data Brokers Market to USD 441.4 Billion by 2032 (press release, GlobeNewswire).
- URL/DOI: https://www.globenewswire.com/fr/news-release/2025/02/18/3028050/0/en/Data-Brokers-Market-to-USD-441-4-Billion-by-2032-Owing-to-Increasing-Demand-for-Targeted-Marketing-and-Consumer-Insights-Research-by-SNS-Insider.html
- Verified: partial (commercial market-research estimate; estimates vary widely by vendor)
- Supports: Data broker market valued at ~US$257.2B (2023), projected $441.4B by 2032 (7.4% CAGR). Use as an order-of-magnitude indicator only.

---

## B4. SSI foundations, standards, critiques

### [ALLEN2016] Allen, C. (2016, 26 Apr). The Path to Self-Sovereign Identity. Life With Alacrity.
- URL/DOI: https://www.lifewithalacrity.com/article/the-path-to-self-soverereign-identity/
- Verified: yes
- Supports: Ten principles: Existence, Control, Access, Transparency, Persistence, Portability, Interoperability, Consent, Minimalization, Protection; "Users must control their identities."

### [CAMERON2005] Cameron, K. (2005, May). The Laws of Identity. identityblog.com (Microsoft).
- URL/DOI: https://www.identityblog.com/?p=352
- Verified: yes
- Supports: Law 1: "Technical identity systems must only reveal information identifying a user with the user's consent." Law 2 (Minimal Disclosure): least disclosure "is the most stable long-term solution." Also Law 6 "Human Integration" (human as a component of the system).

### [TOBIN2016] Tobin, A., & Reed, D. (2016, 29 Sep; v2 2017 with Windley). The Inevitable Rise of Self-Sovereign Identity. Sovrin Foundation white paper.
- URL/DOI: https://sovrin.org/library/inevitable-rise-of-self-sovereign-identity/
- Verified: yes (library page/version history)
- Supports: Internet lacks a native identity layer; distributed ledgers enable identities that individuals, organizations or things fully control.

### [PREUKSCHAT2021] Preukschat, A., & Reed, D. (Eds.) (2021). Self-Sovereign Identity: Decentralized digital identity and verifiable credentials. Manning. ISBN 9781617296598.
- URL/DOI: https://www.manning.com/books/self-sovereign-identity
- Verified: yes (publisher listing)
- Supports: Standard practitioner reference for SSI architecture (wallets/agents, DIDs, VCs); 504 pp.

### [MUHLE2018] Mühle, A., Grüner, A., Gayvoronskaya, T., & Meinel, C. (2018). A survey on essential components of a self-sovereign identity. Computer Science Review, 30, 80–86.
- URL/DOI: https://doi.org/10.1016/j.cosrev.2018.10.002 (resolves to Elsevier PII S1574013718301217); arXiv:1807.06346
- Verified: yes
- Supports: Identifies essential SSI components (identification, authentication, verification, privacy).

### [SCHARDONG2022] Schardong, F., & Custódio, R. (2022). Self-Sovereign Identity: A systematic review, mapping and taxonomy. Sensors, 22(15), 5641.
- URL/DOI: https://doi.org/10.3390/s22155641
- Verified: yes
- Supports: Systematic review of >80 papers/standards/patents; proposes SSI taxonomy and open challenges (incl. usability/key management).

### [WUST2018] Wüst, K., & Gervais, A. (2018). Do you need a blockchain? Crypto Valley Conference on Blockchain Technology (CVCBT), 45–54.
- URL/DOI: https://doi.org/10.1109/CVCBT.2018.00011
- Verified: partial (DOI from DBLP/BibTeX record; not resolved live)
- Supports: Decision framework showing many applications do not need a (permissionless) blockchain vs. a central database.

### [MOXIE2022] Marlinspike, M. (2022, 7 Jan). My first impressions of web3. moxie.org.
- URL/DOI: https://moxie.org/2022/01/07/web3-first-impressions.html
- Verified: yes
- Supports: Decentralisation re-centralises around intermediaries: "People do not want to run their own servers"; "Almost all dApps use either Infura or Alchemy" — i.e., users delegate to software/services.

### [W3C-VC2] W3C (2025, 15 May). Verifiable Credentials Data Model v2.0. W3C Recommendation.
- URL/DOI: https://www.w3.org/TR/vc-data-model-2.0/
- Verified: yes
- Supports: Holder = "A role an entity might perform by possessing one or more verifiable credentials" — the role the proposed custodian agent performs.

### [W3C-DID] W3C (2022, 19 Jul). Decentralized Identifiers (DIDs) v1.0. W3C Recommendation.
- URL/DOI: https://www.w3.org/TR/did-core/
- Verified: yes
- Supports: "DIDs have been designed so that they may be decoupled from centralized registries."

### [NIST-800-63-4] Temoshok, D., et al. (2025, July). NIST SP 800-63-4, Digital Identity Guidelines (+63A-4, 63B-4, 63C-4).
- URL/DOI: https://doi.org/10.6028/NIST.SP.800-63-4 ; https://csrc.nist.gov/pubs/sp/800/63/4/final
- Verified: yes
- Supports: Final Rev. 4 released 31 Jul 2025; volumes cover identity proofing & enrollment (63A), authentication & authenticator management (63B), federation (63C).

### [ISO24760] ISO/IEC 24760-1:2019. IT security and privacy — A framework for identity management — Part 1: Terminology and concepts (2nd ed., 2019-05).
- URL/DOI: https://webstore.iec.ch/publication/65242 ; preview: https://www.vde-verlag.de/iec-normen/preview-pdf/info_isoiec24760-1{ed2.0}en.pdf
- Verified: partial (scope/edition confirmed; lifecycle/enrolment clause text is paywalled, not verified)
- Supports: Defines core IdM concepts "applicable to any information system that processes identity information." Do not quote specific lifecycle-function wording without the full text.

### [GMR1989] Goldwasser, S., Micali, S., & Rackoff, C. (1989). The knowledge complexity of interactive proof systems. SIAM Journal on Computing, 18(1), 186–208.
- URL/DOI: https://doi.org/10.1137/0218012 (PDF: https://crypto.cs.mcgill.ca/~crepeau/COMP647/2007/TOPIC02/GMR89.pdf)
- Verified: partial (journal/vol/pages confirmed; DOI suffix consistent but not resolved live)
- Supports: Origin of zero-knowledge proofs (preliminary version STOC 1985).

### [CL2001] Camenisch, J., & Lysyanskaya, A. (2001). An efficient system for non-transferable anonymous credentials with optional anonymity revocation. EUROCRYPT 2001, LNCS 2045, 93–118.
- URL/DOI: https://doi.org/10.1007/3-540-44987-6_7 ; ePrint 2001/019
- Verified: yes
- Supports: Anonymous credentials allowing a user to show a credential "unlinkably many times" — the cryptographic basis of predicate/ZK credentials.

### [ETSI-TR119476] ETSI (2025, Aug). TR 119 476-1 V1.3.1: Selective disclosure and zero-knowledge proofs applied to Electronic Attestation of Attributes; Part 1: Feasibility study.
- URL/DOI: https://www.etsi.org/deliver/etsi_tr/119400_119499/11947601/01.03.01_60/tr_11947601v010301p.pdf
- Verified: yes (PDF text extracted)
- Supports: Even with unlinkability, a verifier can still link "beyond what is possible solely based on the disclosed attribute values" only if correlatable data is removed — i.e., disclosed predicate *values themselves* remain a residual leakage channel; defines colluding-verifier and issuer-verifier threat sets; EUDI example "age_over_21".

### [HESSE2023] Hesse, J., Singh, N., & Sorniotti, A. (2023). How to bind anonymous credentials to humans. USENIX Security 2023.
- URL/DOI: https://www.usenix.org/system/files/usenixsecurity23-hesse.pdf ; ePrint 2023/853
- Verified: partial (PDF located; author list from ePrint listing not separately confirmed in this session)
- Supports: Anonymous credentials offer "unlinkability across multiple presentation, selective disclosure of attributes (or predicates on them)" — but binding them to a human remains an open problem.

---

## B5. AI agents and identity; agent security

### [CHAN2024-IDS] Chan, A., Kolt, N., Wills, P., Anwar, U., Schroeder de Witt, C., Rajkumar, N., Hammond, L., Krueger, D., Heim, L., & Anderljung, M. (2024). IDs for AI Systems. arXiv:2406.12137 (RegML @ NeurIPS 2024).
- URL/DOI: https://arxiv.org/abs/2406.12137
- Verified: yes
- Supports: AI-system IDs "seem most warranted in settings where AI systems could have a large impact upon the world," e.g., financial transactions, contacting real humans.

### [CHAN2024-VIS] Chan, A., Ezell, C., Kaufmann, M., et al. (2024). Visibility into AI Agents. ACM FAccT 2024, 958–973. arXiv:2401.13138.
- URL/DOI: https://arxiv.org/abs/2401.13138
- Verified: yes
- Supports: Assesses "three categories of measures to increase visibility into AI agents": agent identifiers, real-time monitoring, activity logging.

### [SOUTH2025] South, T., Marro, S., Hardjono, T., Mahari, R., Whitney, C. D., Greenwood, D., Chan, A., & Pentland, A. (2025). Position: AI Agents Need Authenticated Delegation. ICML 2025 (PMLR). Preprint: "Authenticated Delegation and Authorized AI Agents," arXiv:2501.09674.
- URL/DOI: https://arxiv.org/abs/2501.09674 ; https://icml.cc/virtual/2025/poster/40172
- Verified: yes
- Supports: Proposes "extending OAuth 2.0 and OpenID Connect with agent-specific credentials and metadata" and "translating flexible, natural language permissions into auditable access control configurations."

### [OIDF2025] South, T., et al. / OpenID Foundation AI Identity Management Community Group (2025, 7 Oct). Identity Management for Agentic AI: The new frontier of authorization, authentication, and security for an AI agent world. arXiv:2510.25819.
- URL/DOI: https://openid.net/new-whitepaper-tackles-ai-agent-identity-challenges/ ; https://arxiv.org/abs/2510.25819
- Verified: yes
- Supports: Agent protocols such as MCP "highlight the demand for clarified best practices in authentication and authorization"; current OAuth/OIDC suffice for simple single-domain agents but not cross-domain/autonomous ones (gaps: recursive delegation, consent fatigue, impersonation).

### [MCP2024] Anthropic (2024, 25 Nov). Introducing the Model Context Protocol.
- URL/DOI: https://www.anthropic.com/news/model-context-protocol
- Verified: yes
- Supports: MCP is "an open standard that enables developers to build secure, two-way connections" between data sources and AI tools.

### [MCP-AUTH] Model Context Protocol (2025-06-18). Specification – Authorization.
- URL/DOI: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
- Verified: yes
- Supports: MCP server "acts as an OAuth 2.1 resource server"; MUST implement RFC 9728 Protected Resource Metadata; clients MUST use RFC 8707 resource indicators; token passthrough forbidden; PKCE mandatory.

### [A2A2025] Google for Developers (2025, 9 Apr). Announcing the Agent2Agent Protocol (A2A).
- URL/DOI: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- Verified: yes
- Supports: Open agent-to-agent protocol with "more than 50 technology partners"; "secure by default," enterprise-grade authN/authZ parity with OpenAPI schemes.

### [LF-A2A2025] Linux Foundation (2025, 23 Jun). Linux Foundation launches the Agent2Agent Protocol Project.
- URL/DOI: https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents
- Verified: yes (via LF press listing)
- Supports: A2A moved to neutral governance with >100 supporting companies; >150 organisations and v1.0 by April 2026.

### [KYA-SKYFIRE] Skyfire (2025). Know Your Agent (KYA).
- URL/DOI: https://skyfire.xyz/know-your-agent-kya/ ; see also https://www.vouched.id/learn/blog/know-your-agent-framework
- Verified: partial (vendor proposals; no standards-body KYA spec found)
- Supports: Industry is extending KYC to agents: KYA is "identity verification system tailored specifically for AI agents" (Skyfire); Vouched proposes a "Digital Agent Passport."

### [MASTERCARD-AGENTPAY] Mastercard (2025, 29 Apr). Mastercard unveils Agent Pay, pioneering agentic payments technology to power commerce in the age of AI.
- URL/DOI: https://www.mastercard.com/us/en/news-and-trends/press/2025/april/mastercard-unveils-agent-pay-pioneering-agentic-payments-technology-to-power-commerce-in-the-age-of-ai.html
- Verified: yes (search extract of primary release)
- Supports: Introduces "Agentic Tokens"; trusted AI agents "must be registered and verified before they can make secure payments."

### [VISA-VIC] Visa (2025, 30 Apr). Find and Buy with AI: Visa unveils new era of commerce (Visa Intelligent Commerce).
- URL/DOI: https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21361.html
- Verified: yes (search extract of primary release)
- Supports: AI-Ready Cards replace card details with tokenized credentials and confirm "a consumer's chosen agent is allowed to act on the consumer's behalf"; consumers set spending limits.

### [OWASP-LLM01] OWASP GenAI Security Project (2025). LLM01:2025 Prompt Injection. OWASP Top 10 for LLM Applications 2025.
- URL/DOI: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- Verified: yes
- Supports: #1 LLM risk; "Indirect prompt injections occur when an LLM accepts input from external sources, such as websites or files."

### [GRESHAKE2023] Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., & Fritz, M. (2023). Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. AISec '23 (ACM CCS workshop), 79–90.
- URL/DOI: https://arxiv.org/abs/2302.12173 (DOI 10.48550/arXiv.2302.12173)
- Verified: yes (arXiv); partial for ACM DOI (not found)
- Supports: "LLM-Integrated Applications blur the line between data and instructions."

### [WILLISON2023] Willison, S. (2023, 25 Apr). The Dual LLM pattern for building AI assistants that can resist prompt injection.
- URL/DOI: https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
- Verified: yes
- Supports: Privileged LLM handles trusted input and tools; Quarantined LLM processes untrusted content and "does not have access to tools."

### [DEBENEDETTI2025] Debenedetti, E., et al. (2025). Defeating Prompt Injections by Design (CaMeL). arXiv:2503.18813.
- URL/DOI: https://arxiv.org/abs/2503.18813
- Verified: yes
- Supports: Separating control from data flow with capabilities: "77% of tasks with provable security (compared to 84% with an undefended system)" in AgentDojo.

### [AGENTDOJO2024] Debenedetti, E., Zhang, J., Balunović, M., Beurer-Kellner, L., Fischer, M., & Tramèr, F. (2024). AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents. arXiv:2406.13352 (NeurIPS 2024 Datasets & Benchmarks track — venue not confirmed on arXiv page).
- URL/DOI: https://arxiv.org/abs/2406.13352
- Verified: yes (arXiv); partial (venue)
- Supports: Benchmark of 97 realistic tasks and 629 security test cases.

### [BEURERKELLNER2025] Beurer-Kellner, L., Buesser, B., Creţu, A.-M., et al. (2025). Design Patterns for Securing LLM Agents against Prompt Injections. arXiv:2506.08837.
- URL/DOI: https://arxiv.org/abs/2506.08837
- Verified: yes
- Supports: Proposes "principled design patterns for building AI agents with provable resistance to prompt injection" (six patterns, ten case studies); once untrusted input is ingested, it must be impossible for it to trigger consequential actions.

### [ZKGATEWAY2026] Subbabhatta Gopalakrishna, A. (2026, 30 Aug). Zero-Knowledge Predicate Proofs Between AI Agents: A measured, cross-protocol gateway and the source-integrity gap. arXiv:2608.30083.
- URL/DOI: https://arxiv.org/abs/2608.30083
- Verified: yes (arXiv abstract; preprint, not peer-reviewed)
- Supports: Directly adjacent prior art: ZK predicate proofs over MCP and A2A; 32-bit threshold predicate proves in 6.2 ms, verifies in 1.0 ms, 608-byte Bulletproof; notes predicate binds to committed value, not system of record.

### [EFF-ZKP-2026] Barnett, D. (2026, 18 Aug). Zero-Knowledge Proofs aren't age verification silver bullets. EFF Deeplinks.
- URL/DOI: https://www.eff.org/deeplinks/2026/08/zkps-arent-age-verification-silver-bullets
- Verified: yes
- Supports: Issuer "could track every time that credential is used"; researcher made an EU app "repeatedly accepting the same 'over-18' token" — ZK alone does not solve operational privacy.

---

## B6. Query-based reconstruction / inference attacks

### [DENNING1979] Denning, D. E., Denning, P. J., & Schwartz, M. D. (1979). The tracker: A threat to statistical database security. ACM TODS, 4(1), 76–96.
- URL/DOI: https://faculty.nps.edu/dedennin/publications/TrackerThreat.pdf (DOI not confirmed in this session; likely 10.1145/320064.320068 — verify)
- Verified: yes (author-hosted PDF); partial (DOI)
- Supports: Refusing small query sets is insufficient: "Almost all databases have a general tracker, and general trackers are almost always easy to find" — direct analogue of predicate-narrowing.

### [ADAM1989] Adam, N. R., & Wortmann, J. C. (1989). Security-control methods for statistical databases: A comparative study. ACM Computing Surveys, 21(4), 515–556.
- URL/DOI: https://doi.org/10.1145/76894.76895
- Verified: yes (bibliographic)
- Supports: Taxonomy: conceptual, query restriction (size/overlap control, auditing, partitioning, cell suppression), data perturbation, output perturbation.

### [DINUR2003] Dinur, I., & Nissim, K. (2003). Revealing information while preserving privacy. PODS 2003, 202–210.
- URL/DOI: https://doi.org/10.1145/773153.773173 (PDF: https://www.cs.cornell.edu/~shmat/courses/cs6431/dn03.pdf)
- Verified: yes
- Supports: Reconstruction attack: answering subset-sum queries with noise o(√n) lets an adversary reconstruct almost the whole database; privacy requires Ω(√n) noise.

### [KENTHAPADI2005] Kenthapadi, K., Mishra, N., & Nissim, K. (2005). Simulatable auditing. PODS 2005, 118–127.
- URL/DOI: https://doi.org/10.1145/1065167.1065183
- Verified: yes (bibliographic + abstract)
- Supports: "query denials may leak information" — a wallet that refuses some predicates leaks via refusal unless decisions are simulatable.

### [DWORK2006] Dwork, C., McSherry, F., Nissim, K., & Smith, A. (2006). Calibrating noise to sensitivity in private data analysis. TCC 2006, LNCS 3876, 265–284.
- URL/DOI: https://doi.org/10.1007/11681878_14
- Verified: yes (bibliographic via DBLP)
- Supports: Founding differential-privacy paper (Laplace mechanism calibrated to sensitivity).

### [DWORKROTH2014] Dwork, C., & Roth, A. (2014). The Algorithmic Foundations of Differential Privacy. Foundations and Trends in TCS, 9(3–4), 211–407.
- URL/DOI: https://doi.org/10.1561/0400000042 (free PDF: https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)
- Verified: yes (bibliographic)
- Supports: Composition theorems → cumulative "privacy budget": privacy loss grows linearly (basic) or ~√k (advanced) with number of queries — basis for a per-verifier disclosure budget.

### [SWEENEY2000] Sweeney, L. (2000). Simple demographics often identify people uniquely. Carnegie Mellon University, Data Privacy Working Paper 3.
- URL/DOI: https://dataprivacylab.org/projects/identifiability ; https://kilthub.cmu.edu/articles/journal_contribution/Simple_Demographics_Often_Identify_People_Uniquely/6625769
- Verified: yes
- Supports: "87% (216 million of 248 million)" of the US population likely unique on {5-digit ZIP, gender, date of birth} (1990 census).

### [GOLLE2006] Golle, P. (2006). Revisiting the uniqueness of simple demographics in the US population. ACM WPES 2006.
- URL/DOI: https://crypto.stanford.edu/~pgolle/papers/census.html
- Verified: partial (author page; WPES venue not confirmed in this session)
- Supports: Correction: ZIP+gender+DOB uniquely identifies ~63% (2000 census), not 87% — cite both to be precise.

### [SWEENEY2002] Sweeney, L. (2002). k-anonymity: A model for protecting privacy. Int. J. Uncertainty, Fuzziness and Knowledge-Based Systems, 10(5), 557–570.
- URL/DOI: https://doi.org/10.1142/S0218488502001648
- Verified: yes (bibliographic)
- Supports: Formal k-anonymity model for releasing data so individuals cannot be re-identified.

### [DEMONTJOYE2013] de Montjoye, Y.-A., Hidalgo, C. A., Verleysen, M., & Blondel, V. D. (2013). Unique in the Crowd: The privacy bounds of human mobility. Scientific Reports, 3, 1376.
- URL/DOI: https://doi.org/10.1038/srep01376
- Verified: yes
- Supports: "four spatio-temporal points are enough to uniquely identify 95% of the individuals" (1.5M people, 15 months, hourly antenna data); uniqueness decays only as ~1/10 power of resolution. Highly relevant to vehicle location data.

---

## B7. Reinforcement learning / adaptation

### [SUTTONBARTO2018] Sutton, R. S., & Barto, A. G. (2018). Reinforcement Learning: An Introduction (2nd ed.). MIT Press. ISBN 9780262039246.
- URL/DOI: http://incompleteideas.net/book/the-book-2nd.html (author site not fetched); ISBN confirmed via catalogs
- Verified: partial (bibliographic via retailer/library records)
- Supports: Standard RL reference (MDPs, TD learning, UCB, policy gradients).

### [LATTIMORE2020] Lattimore, T., & Szepesvári, C. (2020). Bandit Algorithms. Cambridge University Press.
- URL/DOI: https://doi.org/10.1017/9781108571401
- Verified: yes
- Supports: Multi-armed bandit theory (stochastic, adversarial, contextual) for online exploration/exploitation, e.g., adaptive disclosure-policy selection.

### [NGUYEN2021] Nguyen, T. T., & Reddi, V. J. (2021). Deep reinforcement learning for cyber security. IEEE Transactions on Neural Networks and Learning Systems.
- URL/DOI: https://doi.org/10.1109/TNNLS.2021.3121870 ; arXiv:1906.05799
- Verified: yes (bibliographic)
- Supports: Survey of DRL for CPS security, autonomous intrusion detection and multi-agent game-theoretic defense.

### [HAMMAR2020] Hammar, K., & Stadler, R. (2020). Finding effective security strategies through reinforcement learning and self-play. CNSM 2020.
- URL/DOI: https://doi.org/10.23919/CNSM50824.2020.9269092 ; arXiv:2009.08120
- Verified: yes
- Supports: Attacker–defender Markov game; effective defensive policies emerge from RL self-play without human intervention.

### [ADAWADKAR2022] Adawadkar, A. M. K., & Kulkarni, N. (2022). Cyber-security and reinforcement learning — A brief survey. Engineering Applications of Artificial Intelligence, 114, 105116.
- URL/DOI: https://doi.org/10.1016/j.engappai.2022.105116
- Verified: partial (DOI redirects to Elsevier PII S0952197622002512; abstract via search)
- Supports: Reviews RL in IDS, IPS, IoT and Identity & Access Management; notes few datasets/publications for RL in IAM — a gap the thesis can claim.

---

## B8. Analogies

### [CENTRING-WIKI] Wikipedia contributors. Centring (arch construction).
- URL/DOI: https://en.wikipedia.org/wiki/Centring
- Verified: yes (tertiary source)
- Supports: "Until the keystone is inserted an arch has no strength and needs the centring" to hold the voussoirs in place.

### [PETROSKI2012] Petroski, H. (2012). Overarching problems. American Scientist, 100(6), 458.
- URL/DOI: https://doi.org/10.1511/2012.99.458
- Verified: partial (search extract)
- Supports: Falsework was knocked out "only after the keystone was seated," leaving the arch self-supporting — scholarly support for the keystone analogy.

### [HERZOG-CARABINER] climbing-history.org (n.d.). Otto Herzog. (Compiles accounts from Mountain 33 (1974), 29–30, incl. Toni Hiebeler.)
- URL/DOI: https://climbing-history.org/climber/3043 ; see also https://grivel.com/blogs/grivel-stories/the-history-of-carabiners
- Verified: partial (secondhand recollections; date disputed 1910 vs 1911; Bigwall Gear doubts the story)
- Supports: Hiebeler: "The evolution of the karabiner is closely associated with the name of Otto Herzog" ('Rambo'), who adapted fire-brigade pear-shaped karabiners for climbing in Munich c. 1910.

### [THOMPSON1984] Thompson, K. (1984). Reflections on trusting trust. Communications of the ACM, 27(8), 761–763.
- URL/DOI: https://doi.org/10.1145/358198.358210 (PDF: https://www.cl.cam.ac.uk/teaching/2223/R209/Reflections-Trusting-Trust.pdf)
- Verified: yes (bibliographic; ACM page 403, PDF mirror available)
- Supports: Turing Award lecture: a compiler Trojan survives clean source — trust ultimately rests on the toolchain/its authors. (The often-quoted line "You can't trust code that you did not totally create yourself" is in the paper's moral section; check the PDF before quoting verbatim.)

### [RFC1951] Deutsch, L. P. (1996, May). RFC 1951: DEFLATE Compressed Data Format Specification version 1.3. IETF.
- URL/DOI: https://www.rfc-editor.org/rfc/rfc1951
- Verified: yes
- Supports: "Phil Katz designed the deflate format." Example of an algorithm everyone uses but nobody executes by hand.

### [PKZIP-HISTORY] Wikipedia contributors. ZIP (file format) / PKZIP.
- URL/DOI: https://en.wikipedia.org/wiki/ZIP_(file_format) ; https://en.wikipedia.org/wiki/PKZIP
- Verified: partial (tertiary)
- Supports: ZIP format introduced 1989 in PKWARE's PKZIP (Phil Katz); spec published as APPNOTE.TXT; DEFLATE most common method.

# Part C. Added during writing

### [ALSHIEKH2018] Alshiekh, M., Bloem, R., Ehlers, R., Könighofer, B., Niekum, S., Topcu, U. (2018). Safe Reinforcement Learning via Shielding. Proc. AAAI-18, 32(1).
- URL/DOI: https://ojs.aaai.org/index.php/AAAI/article/view/11797
- Verified: yes (AAAI proceedings page and ACM DL abstract)
- Supports: a shield "monitors the actions from the learner and corrects them only if the chosen action causes a violation of the specification"; the Steward's kernel plays this role for its responder.
