# CVIN-SC: The Thesis on One Page

Nov 4, 2026 · @Nikhil Prakash

## The thesis

**Comparative Analysis of Self-Sovereign Identity Systems for Connected and Autonomous Vehicles.** Working title; see decision 5. MASc, Electrical and Computer Engineering, UBC. Nikhil Prakash.

Nine blockchain identity standards and the MOBI Vehicle Identity standard are implemented as working systems and compared on one vehicle-identity operation set: cost, security, W3C conformance and real-time V2V feasibility, each measured rather than asserted. The thesis finds that lightweight standards are an order of magnitude cheaper to create, that a translation layer reaches W3C conformance, that credential verification fits the V2V safety budget by two orders of magnitude, and that no single standard dominates on security. An extension adds zero-knowledge VIN privacy and shows where it fits (session time, not per message) and what operating it safely demands: an agent whose own trust rests on the same identity stack.

## Research questions, hypotheses, verdicts

Every hypothesis was stated so the data could contradict it. The verdicts below are the ones the measured evidence supports, including where it falls short of the claim as first stated.

| RQ | Hypothesis | Verdict | Evidence |
| --- | --- | --- | --- |
| RQ1 Cost. How do the nine standards compare on gas for an identical operation set? | H1: minimal-state standards are at least 10x cheaper than rich-state standards for creation and update | Supported for creation; not for update | Creation spans 34x (52,216 to 1,757,893 gas); ERC-1056 is 10.4x cheaper than ERC-721. On update the ratio is 3.4x to 3.9x. N=30, zero variance. |
| RQ2 Security. Which architecture best resists the V2X threat model? | H5: no single standard dominates; a hybrid sits on the frontier | Supported on the fidelity-per-gas plane only | 43 of 43 applicable attack cells defended; only ERC-4337 offers on-chain key recovery; a real attestation gap was found and fixed. CVIN-Combined leads on fidelity per gas but is dominated by ERC-4337 on the six-criterion harness. |
| RQ3 Conformance. Can blockchain-rooted identity reach W3C DID and VC conformance? | H2: at least 90% through a translation layer | Supported | 94.3% structural self-score on the executable checker; 335 of 336 on the external W3C DID test suite; residual gaps are three documented, deliberate deviations. |
| RQ4 Real time. Does identity plus credential verification fit the V2V safety budget? | H3: off-chain verification of pre-issued credentials meets the 100 ms budget | Supported | 0.142 ms warm against 100 ms; 1.65 million verifications over 30 runs; PKI measured on the same path at 0.090 ms. Cryptographic cost only; radio and network stack excluded. |
| RQ4 Industry. Does MOBI VID port across backends? | H4: realisable across multiple backends | Supported, with a fidelity gradient | Birth and lifecycle native on all five backends; native multi-party attestation on three of five. |
| RQ5 Privacy. Can zero-knowledge proofs give VIN privacy within the RQ1 and RQ4 budgets, and what does operating them safely require? | H6: feasible at registration and session time, not per message; safe operation needs a bounded custodian on the same identity stack | Partly supported | Prove 399 ms, verify 18 ms, 301,163 gas on chain. Six of seven pre-registered expectations pass; Z-E6 (the custodian's honest-service floor) fails and is reported as a failure. |

## The seven chapters

All seven exist as a first full draft (about 45,000 words). Chapters 3 to 7 read their numbers from committed result files through a 63-row claim register.

| Chapter | What it argues | What it rests on |
| --- | --- | --- |
| 1 Introduction | Vehicle identity is the open problem under V2X security; the standards have not, as far as I have found, been compared on one footing | The gap positioned in chapter 2 |
| 2 Literature review | SSI and W3C; the nine standards; MOBI VID; V2X security and PKI; ZKPs and anonymous credentials; agent identity; the identity-dependent transaction | Verified sources only; two absence claims awaiting sign-off |
| 3 Methodology | Identical-operation comparison; exact gas at N=30; cold and warm V2V timing with intervals; two-lens security; executable conformance; pre-registered expectations | Measurement conditions named per claim |
| 4 Implementation | The five layers: nine standards, the W3C layer, the V2X testbed, the comparison framework, ZK-VIN and the Steward | 563 passing contract tests; 376 Python tests |
| 5 Results | RQ1 to RQ5 answered from measured artifacts; a hypotheses summary; threats to validity | Register rows #1 to #62 |
| 6 Discussion | Which standard when; the security, cost and fidelity frontier; V2V viability; on-chain reality and SSI as a spectrum; the identity-dependent transaction; the agent wrapper and its risks | Chapter 5 |
| 7 Conclusion | Answers, verdicts, contributions, limitations (local gas, simulated mobility, insecure ZK setup), future work (public testnet, real SUMO, anonymity set, setup ceremony, live red team) | Chapters 5 and 6 |

This draft is one take: one method and one ordering of the argument. I'll produce a few more from different angles, then write the final version myself. The work is frozen at 31 October 2026 so that can happen: the thesis reads from the results of record as of that date, and anything later, in the field or in my own work, goes to the programme around the thesis rather than into it.

## Decisions I'd like your view on

1. **Does RQ5 belong in the thesis or in the companion paper?** It is adopted as an extension now (one chapter section each in 3 to 7). The alternative is to keep the thesis to RQ1 to RQ4 and publish the ZK and agent work as its own paper.
2. **Which side paper goes out first?** Eight are registered. The two readiest are the silent-signature security note (the attestation gap found and fixed in MOBI VID) and the V2V feasibility study. Either could be submitted before the defence.
3. **Public-testnet validation.** Gas is measured locally and is exact; a Sepolia run would add external witness at the cost of a few weeks. Is it worth it for the defence?
4. **A target date.** Integration of the parallel work into one branch starts now; figures and the chapter audit follow. I'd like to set a defence window with you once you've seen the shape.
5. **The title.** The current one promises a comparison of SSI systems; the work compares identity substrates on one vehicle lifecycle. The proposed replacement is *Measured Trade-offs of Ethereum Identity Standards for Connected Vehicles: Cost, Credential Structure and Real-Time Verification*. Keep, replace, or something between?
