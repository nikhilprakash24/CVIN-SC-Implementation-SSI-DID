# Research Expansion — Sources

**Date:** 2026-10-15
**Method:** A literature and standards sweep with Firecrawl and web search. Every URL below appeared in a search result during the sweep. Items marked *(secondary)* were confirmed only through a secondary or vendor page; cite the primary text before they enter a chapter. Section 13 lists claims that could **not** be verified. Do not cite those.

The rule from `COMPOSITION.md` still holds: never fabricate a citation. These entries are leads for the author to confirm, not finished bibliography entries.

## 1. Zero-knowledge and anonymous credentials
- **S1** — W3C VC WG, *Data Integrity BBS Cryptosuites v1.0* (CRD, 2026-09-10). https://www.w3.org/TR/vc-di-bbs/
- **S2** — Looker et al., *The BBS Signature Scheme*, draft-irtf-cfrg-bbs-signatures-12 (2026-09-28). https://datatracker.ietf.org/doc/draft-irtf-cfrg-bbs-signatures/. Blind-signature extension: https://datatracker.ietf.org/doc/draft-irtf-cfrg-bbs-blind-signatures/
- **S3** — IETF, *RFC 9901: Selective Disclosure for JWTs (SD-JWT)*. https://www.rfc-editor.org/info/rfc9901/
- **S4** — PSE / Ethereum Foundation, *Semaphore*. Docs: https://semaphore.pse.dev/learn. Code: https://github.com/semaphore-protocol/semaphore
- **S5** — iden3, *snarkjs* (Groth16, Solidity verifier export). https://github.com/iden3/snarkjs
- **S6** — *Longfellow-zk* (ZK over ECDSA-signed mdoc). Code: https://github.com/longfellow-zk/longfellow-zk. IETF 124 slides: https://datatracker.ietf.org/meeting/124/materials/slides-124-dispatch-longfellow-zero-knowledge-credentials-00
- **S7** — Microsoft Research, U-Prove extensions. https://www.microsoft.com/en-us/research/?p=167028
- **S8** — Vullers & Alpár, Idemix efficiency, IFIP IDMAN 2013. https://dl.ifip.org/db/conf/idman/idman2013/VullersA13.pdf
- **S9** — *Performance Analysis of Groth16 zkSNARK (Circom-snarkjs)*. https://computingonline.net/computing/article/view/4329

## 2. Driving licence, wallets, status, protocols
- **S10** — ISO/IEC 18013-5:2021 (mDL). https://www.iso.org/standard/69084.html
- **S11** — ISO/IEC TS 18013-7:2025 (online presentation). https://www.iso.org/standard/91154.html. Explainer *(secondary)*: https://learn.mattr.global/docs/concepts/iso-mdoc-standards
- **S12** — ISO/IEC TS 23220. Part 2: https://www.iso.org/obp/ui#!iso:std:iso-iec:ts:23220:-2:ed-2:v1:en. Part 5: https://www.iso.org/standard/86786.html
- **S13** — AAMVA, *mDL Implementation Guidelines v1.6* (June 2026). https://aamva.org/getmedia/8ad69f13-9650-49aa-92bd-eafb205917cd/MobileDLGuidelines-1-6.pdf
- **S14** — EUDI Wallet Architecture and Reference Framework. https://github.com/eu-digital-identity-wallet/eudi-doc-architecture-and-reference-framework and https://eudi.dev/1.1.0/arf/
- **S15** — EU driving-licence directive revision. Council text: https://data.consilium.europa.eu/doc/document/ST-8353-2025-REV-1/en/pdf. Commission news: https://transport.ec.europa.eu/news-events/news/commission-welcomes-provisional-agreement-modernised-driving-licences-rules-2025-03-25_de. *Publication in the Official Journal is unconfirmed; check EUR-Lex.*
- **S16** — W3C, *Bitstring Status List v1.0*. https://www.w3.org/TR/vc-bitstring-status-list/
- **S17** — W3C, *VC Data Model v2.0* (Recommendation, 2025-05-15). https://www.w3.org/TR/vc-data-model-2.0/
- **S18** — OpenID Foundation: OpenID4VP 1.0, OpenID4VCI 1.0, HAIP 1.0 (Final). https://www.openid.net/tag/openid4vc/, https://openid.net/tag/digital-credentials-protocols/, https://openid.net/tag/haip/
- **S19** — ISO/IEC 18013-5, 2nd edition (DIS; adds revocation). https://www.iso.org/standard/91081.html

## 3. V2X security and PKI
- **S20** — IEEE 1609.2-2022 (superseded by 1609.2-2025). https://webstore.ansi.org/standards/ieee/ieee16092022-2498125
- **S21** — IEEE 1609.2.1 (certificate management for end entities). https://standards.ieee.org/ieee/1609.2.1/11855/
- **S22** — ETSI TS 102 941 V2.1.1. https://etsi.org/deliver/etsi_TS/102900_102999/102941/02.01.01_60/ts_102941v020101p.pdf
- **S23** — EU CCMS. JRC CPOC protocol: https://cpoc.jrc.ec.europa.eu/data/documents/CPOC_Protocol_Release1.pdf. BSI overview: https://bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Automotive/Kooperative_Intelligente_Verkehrssysteme/Kooperative_Intelligente_Verkehrssysteme.html
- **S24** — Boldyreva, Kumar & Sun, butterfly key mechanism security. https://eprint.iacr.org/2024/1674.pdf
- **S25** — Petit et al., *Pseudonym Schemes in Vehicular Networks: A Survey*, IEEE COMST. https://ris.utwente.nl/ws/files/6470958/2014-xx-ieee-comm-sat-pseudonym.pdf
- **S26** — Boualouache et al., *A Survey on Pseudonym Changing Strategies for VANETs*, IEEE COMST 2018. https://arxiv.org/pdf/1704.00679
- **S27** — Misbehaviour detection:
  - ETSI TR 103 460 V2.1.1. https://www.etsi.org/deliver/etsi_tr/103400_103499/103460/02.01.01_60/tr_103460v020101p.pdf
  - 5GAA report. https://5gaa.org/content/uploads/2022/07/5GAA-Misbehaviour-detection-Final.pdf
  - Car2Car Consortium WP. https://www.car-2-car.org/fileadmin/documents/General_Documents/C2CCC_WP_2092_MisbehaviourDetection_and_Reporting_V1.0.pdf
- **S28** — ERC-4337 (account abstraction, paymasters). https://eips.ethereum.org/EIPS/eip-4337
- **S29** — SAE J2945/1 (paywalled; values not verified here). https://saemobilus.sae.org/content/J2945/1_202004
- **S30** — 3GPP TS 22.186 (eV2X requirements) *(secondary summaries)*. https://whatthespec.net/3gpp/spec/22.186 and https://www.itecspec.com/3gpp/22.186/s/5.5
- **S31** — *Towards a Zero Trust Decentralized Identity Management System for Secure AVs* (2025). https://arxiv.org/pdf/2509.25566. **This is the closest prior art; read it before claiming novelty.**
- **S32** — Scopelliti et al., *Efficient and Timely Revocation of V2X Credentials*, NDSS. https://www.ndss-symposium.org/ndss-paper/efficient-and-timely-revocation-of-v2x-credentials/
- **S33** — SECMACE VPKI. https://ar5iv.labs.arxiv.org/html/1707.05518
- **S34** — SCMS pseudonym batch sizes:
  - CHES 2014 invited talk: 20 certificates per week, switched about every 5 min. https://iacr.org/workshops/ches/ches2014/presentations/CHES_2014_Invited.pdf
  - USDOT ITS KRS: 60 per week in the NYC pilot. https://www.itskrs.its.dot.gov/2019-l00889

## 4. Tolling, payments, machine economy
- **S35** — ISO 17573-1 (EFC architecture; DIS revision). https://www.iso.org/standard/91673.html
- **S36** — *AnonymousTollPass* (ring signatures, blockchain tolling). https://khazna.ku.ac.ae/en/publications/anonymoustollpass-a-blockchain-based-privacy-preserving-electroni/
- **S37** — *A DLT-based Infrastructure for Smart Transportation* (µRaiden channels for tolls). https://arxiv.org/pdf/1910.03280
- **S38** — *MOTIVE: Micropayments for trusted vehicular services*. https://arxiv.org/pdf/1904.01630
- **S39** — Unterweger et al., *Low-risk Privacy-preserving EV Charging with Payments*, NDSS AutoSec 2021. https://dev.ndss-symposium.org/wp-content/uploads/autosec2021_23001_paper.pdf
- **S40** — *On M2M Micropayments: A Case Study of Electric Autonomous Vehicles*. https://arxiv.org/pdf/1804.08964
- **S41** — ISO 15118-20 Plug & Charge PKI *(vendor and consortium pages)*:
  - Hubject: https://www.hubject.com/blog-posts/hubjects-plug-charge-team-is-first-to-launch-iso15118-20-public-key-infrastructure-in-their-free-testing-environment
  - CharIN: https://www.charin.global/news/europe-is-ready-to-further-roll-out-plug-charge/
  - Tesla: https://developer.tesla.com/docs/charging/public-key-infrastructure
- **S42** — EIP-712 (typed structured data signing). https://eips.ethereum.org/EIPS/eip-712
- **S43** — ERC-2612 (permit). https://eips.ethereum.org/EIPS/eip-2612
- **S44** — EIP-7702 (set code for EOAs; live in Pectra, May 2025). https://eips.ethereum.org/EIPS/eip-7702

## 5. Oracles and legacy data sources
- **S45** — Zhang et al., *DECO*, ACM CCS 2020. https://arxiv.org/abs/1909.00938
- **S46** — Zhang et al., *Town Crier*, ACM CCS 2016. https://eprint.iacr.org/2016/168
- **S47** — TLSNotary:
  - Review paper: https://arxiv.org/html/2409.17670v1
  - Proxy mode: https://tlsnotary.org/blog/2026/04/22/proxy-mode
- **S48** — Chainlink documentation:
  - Overview: https://docs.chain.link/llms.txt
  - Functions: https://docs.chain.link/chainlink-functions/resources.md
  - CCIP: https://docs.chain.link/ccip/tutorials/offchain.md
- **S49** — NHTSA vPIC VIN decoder API. https://vpic.nhtsa.dot.gov/api/
- **S50** — NMVTIS (US DOJ / AAMVA). https://www.aamva.org/nmvtis
- **S51** — Catena-X / Eclipse Tractus-X SSI:
  - CX-0013: https://www.weboftrust.org/standard/cx-0013_identity_of_member_company-18
  - Eclipse project: https://projects.eclipse.org/node/30273
  - SSI docs: https://github.com/eclipse-tractusx/ssi-docu/pull/12/files
- **S52** — EU Battery Regulation 2023/1542 and ESPR *(secondary)*:
  - https://climate-laws.org/document/regulation-eu-2023-1542-of-the-european-parliament-and-of-the-council-of-12-july-2023-concerning-batteries-and-waste-batteries-new-battery-regulation_c58c
  - https://www.osborneclarke.com/insights/what-eu-digital-product-passport-and-who-it
- **S53** — MOBI:
  - VID v1.0 preview: https://dlt.mobi/wp-content/uploads/2020/04/Preview-MOBI-Vehicle-Identity-Standard-v1.0.pdf
  - 2024 milestones (Battery Birth Certificate, Global Battery Passport): https://dlt.mobi/2024-milestones/

## 6. Regulation and safety engineering
- **S55** — UN R155 (CSMS):
  - EUR-Lex: https://eur-lex.europa.eu/eli/reg/2025/5/oj/eng
  - UN Treaty Collection: https://treaties.un.org/doc/Publication/MTDSG/Volume%20I/Chapter%20XI/XI-B-16-155.en.xml
- **S56** — UN R156 (SUMS) *(secondary)*:
  - https://www.itemis.com/en/glossary/unece-r156/
  - https://www.ul.com/sis/insights/software-update-management-systems-according-unece-r156
- **S57** — ISO/SAE 21434:2021. https://saemobilus.sae.org/standards/isosae21434-road-vehicles-cybersecurity-engineering
- **S58** — Uptane Standard v2.1.0. https://uptane.org/docs/2.1.0/standard/uptane-standard
- **S59** — EU AI Act and automotive *(secondary analysis)*. https://www.squirepattonboggs.com/insights/publications/the-eu-ai-act-and-the-automotive-sector/
- **S60** — EDPB Guidelines 02/2025 on blockchain processing (consultation version; check whether a final version was adopted). https://www.edpb.europa.eu/our-work-tools/documents/public-consultations/2025/guidelines-022025-processing-personal-data_de?page=7

## 7. Transition: PKI ↔ DID bridging and trust registries
- **S66** — did:x509, draft-birkholz-did-x509-03. https://www.ietf.org/archive/id/draft-birkholz-did-x509-03.html. Note: V2X certificates use the IEEE 1609.2 format, not X.509, so an adaptation is required.
- **S67** — did:web: https://github.com/w3c-ccg/did-method-web. did:webs (ToIP): https://trustoverip.org/news/2023/12/15/announcing-public-review-of-the-didwebs-method-specification/
- **S68** — *Combination of X.509 and DID/VC for inheritance of trust*, Open Identity Summit 2022: https://dl.gi.de/items/9f5d8f3f-f1e7-4205-871a-7ad10d2e194a/full. SSI-powered PKI/OIDC: https://arxiv.org/pdf/2006.04754
- **S69** — CDPI, DIDs and PKI in VCs. https://docs.cdpi.dev/technical-notes/data-and-credentialing-infra/verifiable-credentials/dids-and-pki-in-verifiable-credentials
- **S70** — ToIP Trust Registry Query Protocol v2.0. https://trustoverip.org/wp-content/uploads/TRQPv2.0-Archival-PDF-2026.04.23.pdf
- **S71** — EBSI Trusted Issuers Registry. https://hub.ebsi.eu/api/trusted-issuers-registry/
- **S72** — ToIP Technology Architecture Specification V1.0 PR1. https://trustoverip.org/wp-content/uploads/ToIP-Technical-Architecture-Specification-V1.0-PR1-2022-11-14.pdf
- **S73** — *A Survey of SSI Ecosystem*: https://arxiv.org/pdf/2111.02003. ENISA, *Digital Identity: Leveraging the SSI Concept*: https://enisa.europa.eu/publications/digital-identity-leveraging-the-ssi-concept-to-build-trust/@@download/fullReport

## 8. Post-quantum
- **S74** — NIST FIPS 204 (ML-DSA): https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf. RFC 9881: https://rfc-editor.org/rfc/rfc9881
- **S75** — *Hybrid PQC + ECC Certificates: SCMS case study*. https://arxiv.org/pdf/2501.07028
- **S76** — *Deployment Feasibility of PQ Signatures in C-V2X*. https://arxiv.org/pdf/2608.05087
- **S77** — ML-DSA/Falcon on Raspberry Pi as an ECU proxy. https://eprint.iacr.org/2026/2149

## 9. Verifiable autonomy, agents, cross-chain
- **S78** — C2PA content credentials. https://c2pa.org/wp-content/uploads/sites/33/2026/07/Use-of-Content-Credentials-to-Identify-Synthetic-and-Non-Synthetic-Content.pdf
- **S79** — Open Profile for DICE. https://pigweed.googlesource.com/open-dice/+/refs/heads/main/docs/specification.md
- **S80** — Remote attestation for AV fleets (TPM), escar Europe 2024. https://hss-opus.ub.rub.de/opus4/frontdoor/index/index/year/2024/docId/12714
- **S81** — *A Survey of ZKP-Based Verifiable Machine Learning* (2025). https://arxiv.org/pdf/2502.18535
- **S82** — *AI Agents with DIDs and VCs*. https://arxiv.org/pdf/2511.02841
- **S83** — ERC-8004 Trustless Agents (draft): https://eips.ethereum.org/EIPS/eip-8004. Empirical liveness study: https://arxiv.org/abs/2606.26028
- **S84** — *On Addressing Isolation in Blockchain-Based SSI*. https://arxiv.org/abs/2511.18379
- **S85** — *Decentralized Identity in Practice: Benchmarking Latency, Cost, Privacy*. https://arxiv.org/pdf/2601.20716. **A direct comparator for the thesis's methodology.**

## 10. Intersections, insurance, data markets
- **S86** — Carlino, Boyles & Stone, auction-based intersection management, ITSC 2013. https://www.cs.utexas.edu/~pstone/Papers/bib2html-links/ITSC13-dcarlino.pdf
- **S87** — *Coordination of Autonomous Vehicles: Taxonomy and Survey*. https://arxiv.org/pdf/2001.02443
- **S88** — Blockchain intersection management. Chalmers thesis: https://odr.chalmers.se/handle/20.500.12380/255037. MA-AIM: https://fcrlab.unime.it/publication/a-secure-and-dependa/
- **S89** — Society of Actuaries, ZKP report (2023). https://soa.org/resources/research-reports/2023/zero-knowledge-proof. No peer-reviewed ZK-telematics UBI paper was found: this is a gap.
- **S90** — DIMO network docs. https://dimo.org/docs/introduction/what-can-you-build
- **S91** — Privacy-preserving computing in automotive (survey, 2025): https://arxiv.org/abs/2508.01798. HE in VANETs, Sensors 2020: https://pmc.ncbi.nlm.nih.gov/articles/PMC7435932
- **S92** — Ocean Protocol technical whitepaper. https://oceanprotocol.com/tech-whitepaper.pdf

## 11. Already cited elsewhere in the repo, reused here
- **S93** — Kailus, Kern & Krauß 2024, SSI for EV charging. https://arxiv.org/abs/2403.06632
- **S94** — van der Heijden et al. 2018, VeReMi. https://arxiv.org/abs/1804.06701

## 12. Quantitative anchors (cite the source, not this page)
| Fact | Value | Source |
|---|---|---|
| SCMS pseudonym certificates per week | 20 (baseline), 60 (NYC pilot) | S34 |
| Receiver verification load | ≈400–4,000 ECDSA verifications/s; RSU ≈3,500/s at rush hour | secondary, via the literature sweep; confirm before citing |
| BBS on BLS12-381 | signature 112 B; proof 368 + 32 × (hidden messages) B | MATTR library README (non-normative); confirm against S2 |
| ML-DSA-44/65/87 signatures | ≈2,420 / 3,309 / 4,627 B | secondary; confirm against S74 |
| 3GPP eV2X tightest latency | 3 ms; remote driving 5 ms at 99.999% | S30 (secondary) |
| EU battery passport | mandatory from 2027-02-18 | S52 (secondary) |

## 13. Not verified: do not cite
- An ISO 18013-5 transaction-time target. Only the clause title was found.
- SAE J2945/1 latency and rate figures, behind a paywall. The repo's existing 100 ms budget citation should be re-checked against the standard text.
- MOBI "Trusted Trip": no source surfaced.
- An official ETSI TS 103 097 PDF, and the final ESPR text on EUR-Lex.
- A dedicated zk age/range-proof paper beyond Longfellow.
