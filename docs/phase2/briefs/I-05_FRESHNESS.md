# I-05 Deep-Dive Brief: A Theory of Revocation Freshness (k, Time Bounds and Their Optimum)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-20 (Phase 2 session 3, after-action report 23)
**Idea:** I-05, track T (`docs/phase2/ideas.yaml`)
**Anchors:** C4, N-17, D51, register rows #32, #37, #46, #52
**Sources:** 15 cited entries (14 documents), listed in §3 and in `docs/phase2/briefs/I-05_sources.json`; 7 not read (§8)

---

## 1. Question and the Phase 1 model as it stands

**Question (ideas.yaml, I-05).** "Given a revocation rate, a verification cost and a chain-read cost, which
re-check policy minimises cost subject to a bound on accepting a revoked credential, and does the measured knee
(#32, #37) match it?"

**The Phase 1 model.** A verifier caches each sender's identity state (key, revocation flag) and re-reads it from
the chain every k-th message from that sender (`ERC1056Provider.set_refresh_every`,
`cv2x-testbed/identity/erc1056_provider.py`). `cv2x-testbed/scripts/experiment_freshness_k.py` models the amortised
per-message verify cost as

    t_eff(k) = t_local + t_chain / k

where t_local is the median verify on the cached path (k = ∞: freshness check and ECDSA verify, zero RPCs) and
t_chain is the median verify at k = 1 minus t_local (the added cost of one refresh). The freshness window and replay
cache in `cv2x-testbed/identity/freshness.py` run before the cache and are identical for every k; they bound the age
of a *message*, not the age of the cached *identity state*.

**Capacity.** `docs/LATENCY_BUDGET.md` §2 defines P*(f) = floor(f · 100 ms / t): the number of neighbours whose
10 Hz BSMs one verifier can check inside a fraction f of the 100 ms interval. The working point is f = 0.5. The
**knee** is the smallest k with P*(0.5) ≥ 100, that is t_eff(k) ≤ 0.5 ms, so

    k_knee = ceil( t_chain / (0.5 ms − t_local) ),   defined only when t_local < 0.5 ms.

This is the expression the script computes (`derive()`, `k_for_Pstar_0.5_ge_100_*`).

**Staleness.** After a revocation is mined, a message-bounded verifier accepts at most k − 1 further messages from
that sender. The per-trial prediction is k − 1 − ((m_pre − 1) mod k) for m_pre messages accepted before the
revocation (`predicted_after()` in the script). Style guide rule 1.1.9 (`docs/STYLE_AND_RIGOUR_GUIDE.md`) forbids
reading this as a time: "A bound on messages is not a bound on time unless the time was measured".

**Register rows (all status V; quoted with their caveats).**

| Row | What it establishes | Conditions | Caveats in the row |
|---|---|---|---|
| #32 | Means fit t_eff = 0.428 + 10.52/k ms within ±7 %; full-refresh knee at k ≈ 146; staleness 0 / 4 / 24 messages for k = 1 / 5 / 25 (= k − 1, 35/35 trials) | M0/M1, Hardhat 2.28.6, automine, host 1 | K-5, M1 only, one sender |
| #37 | Probe refresh (one `getIdentityInfo` eth_call) t_chain_probe 2.76 / 2.89 ms; no finite k in the sweep reaches P*(0.5) = 100 on host 2 (t_local 0.49–0.54 ms); staleness ≤ k − 1 in 280/280 trials, revocation and rotation | M0/M1, host 2 | absolute ms and the knee are host-dependent; never mix with #32 |
| #46 | RSU case (I3, PASS): at most k − 1 SPaT accepted after revocation (0 / 4 / 24 for k = 1 / 5 / 25, N = 30 runs); "a message count, not a time" | M0, SUMO, in-process registry | cache does not expire; no propagation delay; lookup cost not modelled |
| #52 | #32 and #37 code re-run on one host: the gap between them is the host's. Full t_chain 6.94–8.15 ms, probe 2.03–2.20 ms, t_local 0.326–0.339 ms; full-refresh knee k ≈ 40–49; probe reaches P*(0.5) ≥ 100 at k = 25; staleness = prediction in 30/30 k-rows | M0/M1, host 3 (Xeon 2.30 GHz × 4) | D51 fix not measured (A3b); absolute ms host-dependent |

## 2. Phase 1 anchor: established and open

**Established (V rows only).**
- The amortised form t_local + t_chain/k fits the measured means on one host (#32, ±7 %).
- The message-count staleness bound k − 1 holds exactly for revocation and key rotation, for vehicles and RSUs
  (#32, #37, #46, #52).
- The probe refresh beats the full refresh at every finite k on two hosts (#37, #52).
- The difference in the knee between #32 and #37 is the host's, not the code's, under the rule committed before the
  run (#52; `docs/AFTER_ACTION_REPORT_19.md` §1a, §2).

**Open.**
1. **The knee is host-dependent** (#52). After-action report 19 §2 states the reason: "The knee depends on
   0.5 − `t_local`, so it is the most host-sensitive figure in both rows." No row gives a rule for choosing k that
   survives a change of host.
2. **Message-bounded versus time-bounded caches.** The provider has a message-count policy only (`refresh_every`);
   no cache entry expires (N-17 in `docs/MILESTONE_NEXT.md`: "the cache does not expire, so a time bound also needs a
   cache lifetime"). A thesis claim about how long a revoked key is honoured needs a time-bounded policy or a measured
   inter-message time.
3. **Chain time (D51).** `docs/DEFECT_LOG.md` D51: key validity was decided against the verifier's wall clock, so a
   verifier >15 min behind the chain accepted a revoked key. The fix (`7d08dce`) judges validity against the latest
   block timestamp and adds one `eth_getBlockByNumber` per full resolution. Its cost on t_chain is unmeasured (A3b),
   and a residual on the probe path (D63) remains. Any time bound must say whose clock it is in.
4. **The choice of k** for C4 and N-17 is still a decision without a rule.

## 3. Literature

All sources below were fetched at their origin in this session. PDF text was extracted from the downloaded file;
quotes are exact apart from PDF ligatures (fi, ff) and line-break hyphens, which are normalised.

### 3.1 Certificate revocation: freshness against the cost of checking

| Id | Source | What it says that matters here | Quote (fetched text) |
|---|---|---|---|
| S01 | Rivest, "Can we eliminate certificate revocation lists?", Financial Cryptography (FC '98), LNCS, Springer, 1998, pp. 178–183. URL: https://link.springer.com/chapter/10.1007/BFb0055482 | The founding argument that CRLs can give way to other freshness mechanisms. The fetched page is the abstract only. | "We briefly consider certificate revocation lists (CRLs), and ask whether they could, and should, be eliminated, in favor of other mechanisms. In most cases, the answer seems to be “yes.”" |
| S02 | McDaniel and Rubin, "A Response to 'Can We Eliminate Certificate Revocation Lists?'", Financial Cryptography (FC 2000), LNCS, Springer, 2001, pp. 245–258. URL: https://link.springer.com/chapter/10.1007/3-540-45472-1_17 | The best mechanism depends on the environment; their case analysis identifies the trade-offs between revocation technologies. | "The lessons learned from our case studies are applied to a realistic PKI environment. The result, revocation on demand, is a CRL based mechanism providing timely revocation information." |
| S03 | Santesson et al., "X.509 Internet PKI Online Certificate Status Protocol - OCSP", IETF RFC 6960, June 2013. URL: https://www.rfc-editor.org/rfc/rfc6960.txt | OCSP status carries thisUpdate and nextUpdate, and validity is judged against the relying party's local clock: a time bound, in the verifier's time. This is D51's question for a chain. | "Responses whose nextUpdate value is earlier than the local system time value SHOULD be considered unreliable. Responses whose thisUpdate time is later than the local system time SHOULD be considered unreliable." |
| S05 | Liu et al., "An End-to-End Measurement of Certificate Revocation in the Web's PKI", ACM IMC '15, Tokyo, 2015. URL: https://mislove.org/publications/SSLClient-IMC.pdf | The cost of fetching status is what makes relying parties skip it; the paper measures that cost and that browsers often do not check. | "Using 74 full IPv4 HTTPS scans, we find that a surprisingly large fraction (8%) of the certificates served have been revoked, and that obtaining certificate revocation information can often be expensive in terms of latency and bandwidth for clients." |
| S04 | Larisch et al., "CRLite: A Scalable System for Pushing All TLS Revocations to All Browsers", IEEE S&P, 2017. URL: https://www.ieee-security.org/TC/SP2017/papers/567.pdf | Push instead of pull: clients download a compact aggregate on a period and check locally, which makes the per-check cost local and the staleness a time bound set by the update period. | "In this paper, we present CRLite, an efficient and easily-deployable system for proactively pushing all TLS certificate revocations to browsers. CRLite servers aggregate revocation information for all known, valid TLS certificates on the web, and store them in a space-efficient filter cascade data structure." |

### 3.2 Revocation in V2X (IEEE 1609.2 and SCMS)

| Id | Source | What it says that matters here | Quote (fetched text) |
|---|---|---|---|
| S06 | Brecht, Therriault, Weimerskirch, Whyte, Kumar, Hehn and Goudy, "A Security Credential Management System for V2X Communications", arXiv:1802.05323 (accepted version, IEEE Trans. ITS), 2018. URL: https://arxiv.org/abs/1802.05323 | The SCMS baseline is a periodically distributed CRL, with linkage values to keep it small. A footnote notes that frequent re-certification could replace CRLs if connectivity allowed (Rivest's position, in V2X). | "The SCMS enforces revocation by periodically distributing a Certificate Revocation List (CRL) with an updated list of entries. Devices use the CRL to identify and reject messages from revoked devices." |
| S07 | Papadimitratos, Mezzour and Hubaux, "Certificate Revocation List Distribution in Vehicular Communication Systems", ACM VANET '08 (short paper), 2008. URL: https://people.kth.se/~papadim/publications/fulltext/certificate-revocation-list-distribution-vanet-short.pdf | Vehicular CRL push through RSUs reaches a region in minutes. This sets the scale against which a chain-read policy with a staleness of k − 1 messages is compared. | "Our scheme can distribute large CRLs across wide VC regions within minutes, by utilizing a bandwidth of only a few Kbps at each road-side infrastructure unit." |

The IEEE 1609.2 standard text itself was not read (§8); the brief relies on S06 for the SCMS model.

### 3.3 W3C credential status

| Id | Source | What it says that matters here | Quote (fetched text) |
|---|---|---|---|
| S08 | Sporny, Longley, Prorock and Alkhraishi (eds.), "Bitstring Status List v1.0", W3C Recommendation, 15 May 2025. URL: https://www.w3.org/TR/vc-bitstring-status-list/ | The W3C status method states freshness as a time-to-live in milliseconds, not as a message count, and sets no default. | "The ttl is an OPTIONAL property that indicates the "time to live" in milliseconds before a refresh SHOULD be attempted. If not present, no default value is assumed." |
| S09 | Same document, §3 (validation). URL as S08. | Verifiers are told to cache, and caching is tied to retrieval privacy; the cache lifetime is left to the verifier. | "Verifiers SHOULD cache the retrieved status list and SHOULD use proxies or other mechanisms, such as Oblivious HTTP, that hide retrieval behavior from the issuer." |

A status list is an aggregate: one fetch covers every credential in the list. Its cost does not grow with the number
of neighbours, unlike a per-sender chain read. This gives the theory a third policy class (§7.3).

### 3.4 TTL cache consistency and polled freshness

| Id | Source | What it says that matters here | Quote (fetched text) |
|---|---|---|---|
| S10 | Jung, Berger and Balakrishnan, "Modeling TTL-based Internet Caches", IEEE INFOCOM 2003. URL: https://people.csail.mit.edu/awberger/papers/modeling_ttl_based_internet_caches_infocom2002.pdf | A closed-form hit rate of a TTL cache when request inter-arrivals are i.i.d.: the cost side of a time-bounded identity cache. | "TTL-based consistency, as exemplified by DNS and Web caches, is a policy in which a data item, once retrieved, remains valid for a period known as the “time-to-live”. Cache systems using large TTL periods are known to have high hit rates and scale well, but the effects of using shorter TTL periods are not well understood." |
| S11 | Fielding, Nottingham and Reschke (eds.), "HTTP Caching", IETF RFC 9111 (STD 98), June 2022. URL: https://www.rfc-editor.org/rfc/rfc9111.txt | The standard vocabulary: freshness is age against a lifetime. | "A "fresh" response is one whose age has not yet exceeded its freshness lifetime. Conversely, a "stale" response is one where it has." |
| S12 | Cho and Garcia-Molina, "Synchronizing a database to Improve Freshness", Stanford preprint dated 25 October 1999 (fetched copy; the SIGMOD 2000 version was not read). URL: https://www.kth.se/social/files/554f1d5bf27654514fd00393/synchronizing-a-database-to-improve-freshness.pdf | Freshness and age of a polled local copy under Poisson changes, with expected freshness e^(−λt) between synchronisations. This is the closest analytic template: the verifier is the copy, the chain is the source. | "In many cases, the remote source is updated independently without pushing updates to the client that has a copy, so the client must periodically poll the source to detect changes and refresh its copy." |

### 3.5 Age of Information as a formal frame

| Id | Source | What it says that matters here | Quote (fetched text) |
|---|---|---|---|
| S13 | Kaul, Gruteser, Rai and Kenney, "Minimizing Age of Information in Vehicular Networks", IEEE SECON 2011 (venue from the first author's CV; author copy fetched). URL: https://www.winlab.rutgers.edu/~gruteser/papers/SECON2011_minAge.pdf | AoI was introduced for vehicular status messages; the optimum is interior, between throughput and timeliness. The knee has the same structure. | "We show that information age is minimized at an optimal operating point that lies between the extremes of maximum throughput and minimum delay." |
| S14 | Yates, Sun, Brown III, Kaul, Modiano and Ulukus, "Age of Information: An Introduction and Survey", arXiv:2007.08564, 2020. URL: https://arxiv.org/abs/2007.08564 | The general frame: timeliness at a monitor under a resource budget. | "These applications desire status updates at the recipients to be as timely as possible; however, this is typically constrained by limited system resources." |
| S15 | Maatouk, Kriouile, Assaad and Ephremides, "The Age of Incorrect Information: A New Performance Metric for Status Updates", arXiv:1907.06604, 2019. URL: https://arxiv.org/abs/1907.06604 | AoII penalises only the time the monitor's copy is wrong. Revocation exposure has this shape: a cached state is harmless until a revocation makes it wrong. | "This new metric deals with the shortcomings of both the Age of Information (AoI) and the conventional error penalty functions as it neatly extends the notion of fresh updates to that of fresh "informative" updates. The word informative in this context refers to updates that bring new and correct information to the monitor side." |

### 3.6 What the literature gives I-05

| Element of I-05 | Prior work | What is left for I-05 |
|---|---|---|
| Freshness as a time bound in the verifier's clock | OCSP (S03), HTTP caching (S11), Bitstring Status List ttl (S08) | the chain's clock against the verifier's (D51, D63) |
| Cost of a TTL cache | Jung et al. (S10) | applying the hit-rate model to per-sender identity state at 10 Hz |
| Polling a changing source | Cho and Garcia-Molina (S12) | revocation is a one-way change with a security cost, not a freshness score |
| Push versus pull | CRLite (S04), SCMS (S06), VANET CRL (S07) | a chain registry offers per-sender pull and (with a status list) aggregate pull; their cost scaling with N |
| Interior optimum, staleness metric | AoI (S13, S14), AoII (S15) | the message-bounded policy, where the "sampling" is driven by the sender's own traffic |

The mathematics of every piece is known. The brief did not find in the fetched texts the message-count bound under
an adversarial sender, the knee's sensitivity to t_local, or the chain-time question; those are where I-05 adds.

## 4. Tooling

| Need | What exists | How it plugs in |
|---|---|---|
| Analytic model | plain Python (`t_eff`, `p_star` in `experiment_freshness_k.py`) | a new `cv2x-testbed/scripts/freshness_model.py` that reads the results JSON (`freshness_k*.json`, `results/freshness_k_c3/*.json`), takes t_local and t_chain with their replicate ranges, and writes the predicted knee interval and the policy table of §7 |
| Message-bounded measurement | `experiment_freshness_k.py` with `--ks` (any list, e.g. `1,5,10,12,14,16,25,inf`), `--refresh-mode {full,probe}`, `--rotation` | no code change for the held-out-k test in §7.4 |
| Staleness prediction | `predicted_after(k, m_pre)` in the script | reused unchanged for the message-bounded policy |
| Time-bounded cache | none: `ERC1056Provider` has `refresh_every` only, no entry lifetime | add a `refresh_ttl_s` option (lazy expiry checked on lookup, against a pluggable clock as in `FreshnessPolicy(clock=...)`) and a Part 2b in the script that revokes mid-stream and records the time from inclusion to first rejection |
| Hybrid policy | none | refresh at min(k messages, τ seconds); one condition in the same lookup |
| Discrete-event simulation of N senders with varying rates | none in the repo; SUMO traces exist (`cv2x-testbed/sumo/`) | a small event loop in Python (no new dependency) driving the provider with per-sender arrival times taken from a SUMO run (`run_infra_stats.py`, `run_v2v_stats.py`), to measure exposure in time when rates vary |
| Chain time | D51 fix reads the latest block timestamp on every full resolution | the time-bounded policy measures age in chain time when it has one, and reports the verifier-clock offset beside it |

## 5. Size

**First step: 3 sessions.**
1. Session 1: the model of §7 on paper and as `freshness_model.py`; the predictions of §7.4 committed before any run.
2. Session 2: the held-out-k run (§7.4, prediction P1) on one host, at current code, with the probe and full modes;
   scoring against the committed interval.
3. Session 3: the `refresh_ttl_s` option, its tests, and the time-bounded staleness run.

**What keeps it MASc-sized.**
- One verifier, one registry, M0/M1 only. No public-network timing (M2) in the first step.
- The model is three closed-form policies (message, time, hybrid) plus the aggregate status list as a cost line, not
  a general stochastic control problem. AoI and AoII are the frame and the vocabulary, not a new derivation.
- The deliverable is a rule for choosing k (and τ) from measured inputs on the target host, with its error stated,
  which C4 and N-17 need. A general theory of revocation freshness is not claimed.

## 6. Risk

| Risk | Effect | Answer |
|---|---|---|
| **Already known.** The cost model is the TTL hit-rate model (S10) and the square-root optimum of a holding-against-ordering trade-off; the staleness bound is arithmetic. | Novelty claim fails if stated as "a theory". | Claim an applied model with three specific results: the message-bound versus time-bound distinction under an adversarial sender, the knee's condition number t_local/(B − t_local) as the explanation of host dependence, and exposure in chain time. Cite S10, S12, S15 as the frame. |
| **The knee is ill-conditioned near t_local = B.** On host 2 (#37) t_local is 0.49–0.54 ms against B = 0.5 ms. | The model's interval for the knee becomes unbounded, so "the model predicts the knee" is empty on such a host. | State it as a result: the model predicts *where* it cannot predict. The kill test uses a host with t_local well below B (host 3, #52). |
| **Mean versus median.** The script derives t_local and t_chain from medians, but P* in the register is computed on means; refreshes add tail (`docs/LATENCY_BUDGET.md` §4). | A systematic bias at small k, where refreshes dominate the mean. | Fit the model on means as well as medians and commit to one before scoring. |
| **No revocation-rate or loss data.** The unconstrained optimum needs a revocation rate λ and a loss per accepted revoked message L, which no source here gives for vehicles. | The square-root k is unusable as a number. | Use the constrained form (§7.2): minimise exposure subject to the capacity budget, or maximise k subject to an exposure cap. Neither needs L. |
| **Time bound needs inter-message times.** Rule 1.1.9. | A message bound cannot be turned into seconds from the model alone. | Measure time to first rejection with a TTL policy, and take arrival times from SUMO for the message policy. |

**Kill criterion read against the literature.** ideas.yaml: "If the model cannot predict the measured knee within its
own stated error, report the mismatch and use it to choose k by rule, not to claim a theory." Two consequences
follow. First, "its own stated error" must be written before the run: §7.4 propagates the replicate ranges of
t_local and t_chain into a knee interval. Second, the literature already supplies the form of the model, so passing
the test proves the inputs are measured well enough, not that the theory is new. The kill criterion is sound. The
brief adds that the claim must be "a rule for k with stated error", whether the test passes or fails.

## 7. First step and first experiment

### 7.1 The cost model and its assumptions

Notation (per verifier, per sender): r message rate (Hz); N neighbours; T = 100 ms BSM interval; f = 0.5 budget
share; B = f·T/N_target per-message budget (B = 0.5 ms for N_target = 100); λ revocation rate; L loss per revoked
message accepted; w weight per ms of verify time.

Assumptions.
- A1. Verify cost is t_local on a hit and t_local + t_chain on a refresh, independent of k (the #32 fit).
- A2. Refreshes are independent across senders; one verifier serves N senders at rate r each.
- A3. A revocation is visible to a refresh as soon as it is included (automine; inclusion delay D_incl = 0 in M1).
- A4. The verifier judges key validity in chain time (the D51 fix).
- A5. A revocation arrives at a uniformly random phase of the sender's refresh cycle.
- A6. A sender's message rate is bounded by r_max (channel and congestion control) but otherwise free; a revoked
  sender may slow down or speed up.

### 7.2 Message-bounded cache (refresh every k messages)

- Cost per message: t_eff(k) = t_local + t_chain / k.
- Exposure per revocation, in messages: E ≤ k − 1; mean (k − 1)/2 under A5.
- Exposure in time: W = (sum of the next k − 1 inter-arrival gaps). Under A6 this has no upper bound: a sender that
  goes quiet keeps a revoked key valid until it sends k − 1 more messages. That is the formal content of rule 1.1.9.
- Unconstrained optimum: J(k) = w·r·(t_local + t_chain/k) + λ·L·(k − 1)/2 gives
  k_opt = sqrt(2·w·r·t_chain / (λ·L)). Revocations are rare (λ small), so k_opt is large and the exposure cap binds
  in practice.
- **Constrained optimum (the one the thesis can use).** The feasible set is
  k_min = ceil(t_chain / (B − t_local)) ≤ k ≤ k_max = E_max + 1, with E_max the accepted-message cap.
  Exposure grows with k and cost falls with it, so the freshest feasible policy is **k = k_min, the knee**. If
  k_min > k_max, or t_local ≥ B, no message-bounded policy is feasible and the remedy is a smaller t_chain (the
  probe) or a smaller N_target. The knee is the optimal policy under this formulation, not only a capacity figure.
- Sensitivity: (dk_min/k_min) / (dt_local/t_local) = t_local / (B − t_local). This is the condition number of the
  knee and the model's account of #52's host dependence.

### 7.3 Time-bounded cache (entry lifetime τ, lazy expiry) and the alternatives

- Cost per message: under Poisson arrivals at rate r, the hit fraction of a lazy TTL cache is rτ/(1 + rτ)
  (renewal argument, the setting of S10), so t_eff(τ) = t_local + t_chain / (1 + rτ). With periodic arrivals the
  refresh comes every floor(rτ) + 1 messages, which reduces to the message-bounded form.
- Exposure: in time W ≤ τ (in chain time under A4; plus D_incl on a live chain); in messages E ≤ ceil(r_max·τ).
- Constrained optimum: τ_max = W_max (the time cap) and τ_min from 1 + rτ ≥ t_chain / (B − t_local). The freshest
  feasible τ is τ_min.
- **Hybrid** (refresh at k messages or τ seconds, whichever comes first): E ≤ min(k − 1, ceil(r_max·τ)) and W ≤ τ.
  It is the only policy here that bounds both. It refreshes at least as often as either single bound, so its cost is
  at least the larger of the two.
- **Aggregate status** (a Bitstring Status List or CRL fetched every P seconds, S04, S06, S08): per-verifier chain
  cost t_list / P, independent of N; exposure W ≤ P. Per-sender pull costs N·r·t_chain / k per second. The crossover
  N at which aggregate status becomes cheaper is a model output to compute, not a Phase 1 result.

| Policy | Cost per message | Bound in messages | Bound in time | Needs |
|---|---|---|---|---|
| message, k | t_local + t_chain/k | k − 1 (V: #32, #37, #46, #52) | none under A6 | nothing new |
| time, τ | t_local + t_chain/(1 + rτ) (Poisson) | ceil(r_max·τ) | τ (chain time) | `refresh_ttl_s` |
| hybrid, (k, τ) | ≥ either | min(k − 1, ceil(r_max·τ)) | τ | one condition |
| aggregate, P | t_local + (t_list/P)/(N·r) | ceil(r_max·P) | P | a status list on chain |

### 7.4 Predictions, committed before re-reading the measurements

These are **predictions from the model**, with inputs taken from register row #52 (status V, host 3). They are not
results.

| Id | Condition | Inputs (#52) | Model | Predicted knee |
|---|---|---|---|---|
| P0 (in-sample check) | full refresh, pre-D51 code, host 3 | t_chain 6.94–8.15 ms; t_local 0.326–0.339 ms | ceil(t_chain / (0.5 − t_local)) | k = 40 to 51 |
| **P1** | probe refresh, host 3 | t_chain_probe 2.03–2.20 ms; t_local as above | same | **k = 12 to 14** |
| **P2** | full refresh with the D51 fix (A3b), host 3 | as P0, plus one RPC δ; assumption: δ equals the probe's one eth_call, 2.03–2.20 ms | ceil((t_chain + δ) / (0.5 − t_local)) | **k = 52 to 65** |
| P3 | sensitivity | t_local 0.326–0.339 (host 3); 0.428 (#32, host 1); 0.49 (#37, host 2) | t_local / (0.5 − t_local) | ≈ 1.9–2.1; ≈ 5.9; ≈ 49 |

P0 uses the same runs that produced #52's knee (40–49 in the register), so it is a consistency check, not a
prediction. **P1 and P2 are out of sample:** #52 measured the probe at k = 5 and 25 only, and the D51 provider has
not been timed. The stated error of each interval is the replicate range of its inputs on that host.

**What falsifies the model.**
- P1: a run on host 3 at `--refresh-mode probe --ks 1,8,10,11,12,13,14,15,16,18,25,inf`, two replicates, whose first
  k with P*(0.5) ≥ 100 (on the mean) falls outside 12–14 in both replicates. If the run moves to another host, the
  interval is recomputed from that run's own k = 1 and k = ∞ rows before the intermediate k are read.
- P2: the A3b run of the D51 provider on host 3 with a full-refresh knee outside 52–65. A knee inside the interval
  with a measured δ far from the probe cost falsifies assumption δ, not the model, and is reported as such.
- Time bound: a TTL run in which any post-revocation acceptance occurs later than τ after inclusion, in chain time.
  This tests the claim that a TTL bound is a time bound, which the message policy cannot give (§7.2).
- A failure triggers the kill criterion as written: report the mismatch and choose k by rule (k = k_min computed
  from the target host's own k = 1 and k = ∞ rows, with the hybrid τ as the time cap), without claiming a theory.

## 8. Sources not read

| Source | Why it is listed | Why not read |
|---|---|---|
| IEEE Std 1609.2 (security services for WAVE), current edition | the normative CRL and certificate validity rules for US V2X | paywalled; S06 is used for the SCMS model instead |
| W3C CCG, "Status List 2021" | the predecessor of Bitstring Status List | the fetched URL redirects to a moved repository; S08 is the Recommendation that replaces it |
| Kaul, Yates and Gruteser, "Real-time status: How often should one update?", IEEE INFOCOM 2012 | the paper usually cited as the origin of AoI | no open copy found; S13 and S14 cover the frame |
| Cho and Garcia-Molina, SIGMOD 2000 final version of S12 | the version of record | only the 1999 preprint was fetched |
| Yates et al., published version of S14; Maatouk et al., published version of S15 | versions of record | only the arXiv versions were fetched; venues are not cited |
| Khodaei and Papadimitratos, vehicle-centric CRL distribution (arXiv:1807.02706) | a later vehicular CRL freshness scheme | found by search, not fetched |
| Rivest, FC '98 full text (https://people.csail.mit.edu/rivest/pubs/Riv98b.pdf) | the full argument behind S01 | the file is a scanned image with no extractable text; only the abstract (S01) was read |

**Orchestrator's re-check (2026-10-20, report 23).** Nine of the 15 cited entries were re-fetched at their URLs and
their quotes found in the fetched text (S05, S06 from its PDF, S09, S10, S11, S12 exact or whole but for markup
whitespace). S01 and S02 are Springer pages: the research agent read them at origin, but the orchestrator's re-fetch was
served a block page, so those two are not independently re-verified.
