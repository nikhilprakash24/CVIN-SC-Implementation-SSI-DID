# V2V Latency Budget: Derivation and Measured Position

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-09-24
**Closes:** the analytic half of audit recommendation 7 (F7). The simulation
half (full pipeline under SUMO with N/median/p95) is pending a SUMO
installation.

---

## 1. Where the budget comes from

SAE J2945/1 (On-Board System Requirements for V2V Safety Communications)
fixes the Basic Safety Message (BSM) cadence at **10 Hz**, i.e. a **100 ms
inter-message interval**, and bounds the end-to-end delay for safety
applications (the standard's maximum inter-transmission time and
application-level latency requirements; specific applications such as
pre-crash warning are tighter, on the order of 20 ms). Two consequences:

1. A receiving vehicle must, on average, finish all processing of the BSMs
   it receives from *every* neighbour within one 100 ms interval, or its
   backlog grows without bound.
2. The identity-related part of that processing is **receive → resolve the
   sender's key → verify the signature → check revocation → trust
   decision**. Only this part is in scope for the thesis; sensor fusion
   and application logic consume the rest of the budget and are treated as
   external.

The thesis therefore defines the **identity budget** as a fraction *f* of
the 100 ms interval, with *f* = 0.5 as the working assumption (leaving 50 ms
for everything else), and reports results for *f* ∈ {0.25, 0.5, 1.0} so the
conclusion does not hinge on the choice.

## 2. Neighbour saturation: the quantity that matters

If per-neighbour identity processing costs *t* ms, the number of neighbours
a vehicle can service within the budget is

    P*(f) = floor( f · 100 ms / t )

Dense-traffic scenarios in the literature and in the project's own SUMO
configuration place a vehicle within radio range of tens to low hundreds of
transmitters, so P* must comfortably exceed ~100 for a design to be viable
in dense traffic, and exceed ~10 for it to be viable at all.

## 3. Measured position of each design (claim register #21, Hardhat local)

Per-neighbour cost *t* = verify_message median (which already includes key
resolution and the revocation check for the ERC-1056 provider):

| Design | Condition | *t* (median) | *t* (p95) | P*(0.25) | P*(0.5) | P*(1.0) | Verdict |
|---|---|---|---|---|---|---|---|
| PKI, cert travels with message | M0, in-process | 0.321 ms | 0.366 ms | 77 | **155** | 311 | viable, dense traffic |
| ERC-1056, key + revocation read from chain **at message time**, uncached | M1, local RPC, 7 round trips | 18.158 ms | 23.741 ms | 1 | **2** | 5 | not viable |
| ERC-1056, keys pre-resolved, one `changed()` freshness call per message | M1 (analytic: one round trip ≈ 2.5 ms floor measured for `check_revocation`) | ≈2.5 ms (estimate) | — | 10 | **20** | 40 | marginal |
| ERC-1056, keys pre-resolved and cached, verification fully off-chain | M0 (analytic: signature check only; secp256k1 verify measured within `sign`/`verify` paths ≈0.4 ms) | ≈0.4 ms (estimate) | — | 62 | **125** | 250 | viable, dense traffic |

Verdicts use P*(0.5). The two "estimate" rows are derived from measured
components and are labelled **E** in the claim register until measured
directly (the next experiment: a cached-verifier variant of
`experiment_pki_vs_erc1056.py`).

## 4. What this says about H3

H3 states that off-chain verification of pre-issued credentials fits the
budget and that designs reading the chain at message time do not. The
measured rows support both halves:

- reading the chain at message time gives P*(0.5) = 2 — a vehicle could
  service two neighbours per interval, which fails even sparse traffic;
- fully off-chain verification is within a small factor of PKI
  (≈0.4 vs 0.32 ms), i.e. the identity substrate is not the bottleneck once
  the chain is off the hot path.

The interesting engineering question, which the thesis should answer, is
the **freshness trade-off**: how stale may a cached key/revocation state be?
Each additional chain round trip per message divides P* by roughly
(1 + 2.5 ms / 0.4 ms) ≈ 7 on this setup. A design that refreshes revocation
state every *k* messages rather than every message has

    t_eff ≈ 0.4 ms + 2.5 ms / k

which crosses P*(0.5) = 100 at *k* ≈ 25 (one refresh per 2.5 s at 10 Hz).
This is the design point to evaluate under SUMO.

## 5. Caveats

- All ERC-1056 latencies are from a local Hardhat node (≈2.5 ms per round
  trip). A public network adds tens of milliseconds per read and at least
  one block interval per write; this makes the "uncached" verdict *worse*,
  not better, and does not change the off-chain rows.
- The PKI baseline is in-process (no OCSP/CRL fetch), a lower bound on
  deployed PKI. A PKI that checked OCSP per message would fall into the
  same "round trip at message time" trap.
- P* assumes serial processing on one core; parallel verification scales
  P* by the core count for the off-chain rows but not for the RPC-bound
  rows (which serialize on the node).
- The bundle lineage reported an off-chain warm verify of 0.165 ms
  (N=30) and a saturation of ≈772 neighbours at 0.130 ms/neighbour; those
  figures are consistent in shape with the rows above but are **B** (not
  re-executed on this trunk).

## 6. Sources

- SAE J2945/1, On-Board System Requirements for V2V Safety Communications —
  https://saemobilus.sae.org/content/j2945/1_201603
- Claim register #21 — `docs/MEASUREMENT_CONDITIONS.md`;
  `cv2x-testbed/results/pki_vs_erc1056.md`
