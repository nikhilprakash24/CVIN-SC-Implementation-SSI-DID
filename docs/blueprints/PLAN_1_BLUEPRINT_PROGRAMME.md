# Plan 1 — The Blueprint Programme

**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Date:** 2026-10-15
**Status:** v1.0 — the plan written *before* the sheets were drawn; the sheets in `sheets/` are its execution.
**Rule (same as the rest of the repository):** every number on a sheet traces to a row in `docs/MEASUREMENT_CONDITIONS.md` or to a committed artifact. A sheet never invents a figure. Where a value is a parameter and not a measurement (the fiat value a chain secures, for example) the sheet says so.

---

## 0. The idea in one paragraph

Treat the identity system the way a naval architect treats a submarine: one vessel, drawn as a numbered set of sheets, from the general arrangement down to the detail drawing of a single valve. The "vessel" here is the vehicle-identity system. Its "engines" are the cryptographic and EVM primitives; its "assemblies" are the registries, the resolver, the credential pipeline, the MOBI VID profile; its "operations" are the sequences a vehicle, an issuer and a verifier actually run; its "hull integrity" is the threat model and the attack matrix; and its "deck plan" is the layer ladder it rests on — contracts on an EVM, the EVM on consensus, consensus on a network of nodes, nodes on people and compute and electricity. The point of the format is not decoration. A drawing set with a title block, a revision block, zone references, numbered balloons and a parts list forces every component to be named, located, versioned and traced — exactly the discipline the thesis holds its numbers to. The same format also carries the thesis's strongest claim without a word of marketing: the identity operations are ordinary transactions on the same ledger that settles value, so they inherit the ledger's security, and the sheets show precisely where that inheritance ends and the application layer's own defences begin.

## 1. What a blueprint actually is — two families, drawn in parallel

Two different disciplines use the word, and the programme draws both.

### 1.1 Machine blueprints (naval / aerospace / defence drawing practice)

| Sheet type | What it shows | Our use |
|---|---|---|
| **General arrangement (GA)** — inboard profile, plan views, sections | The whole vessel, every compartment located, cut along one plane | BP-001: the layer ladder as a cutaway |
| **Section / detail drawing** | One component at scale, with every feature dimensioned | BP-103 ERC-1056 registry, BP-105 CVIN-Combined |
| **Exploded view + parts list (bill of materials)** | Every part numbered with a balloon; the list names, counts and specifies each | BP-101 crypto primitives, BP-102 EVM primitives, BP-104 the basic digital-ID set |
| **Schematic (piping / electrical / hydraulic)** | Flow between components with standard symbols, no geometry | BP-201 resolver, BP-202 credential pipeline |
| **Wiring / interconnect diagram** | Which terminal connects to which | BP-601 deployment and test harness |

Conventions taken from the drawing-practice standards (ASME Y14.1 sheet size and format, adopted for US DoD use in 1995; Y14.100 for title-block content; Y14.35 for revisions):

- a **border with zone references** — letters along the vertical edges, numbers along the horizontal edges, so a note can say "see zone C4";
- a **title block** in the lower-right corner: drawing number, title, sheet *n* of *N*, revision, scale, date, drawn / checked / approved;
- a **revision block** in the upper-right corner: rev letter, description, date, approval;
- **general notes** numbered in the upper-left (or left margin);
- **balloons** (numbered circles) tying each drawn part to a **parts list**;
- a **distribution / classification band** top and bottom. Ours reads `UNCLASSIFIED // THESIS RESEARCH — MEASURED` and the programme name is the thesis's own (`CVIN-SSI PROGRAMME`); nothing on a sheet imitates a real service or agency.

Naval general-arrangement drawings (the A-class submarine *Aeneas* GA at the National Maritime Museum; the H. L. Hunley cutaway at the Naval History and Heritage Command) add two things worth copying: the **inboard profile** (one long cut through the hull showing every compartment in order) and **sections** at named frames. BP-001 is an inboard profile; the 100-series sheets are sections through it.

### 1.2 Software blueprints (architecture-description practice)

| Framework / notation | Views | Our use |
|---|---|---|
| **DoDAF 2.02** (the US DoD architecture framework) | OV-1 high-level operational concept; SV-1 systems interface description; SV-4 systems functionality description (functions allocated to resources); SV-10c systems event-trace (sequence); CV-2 capability taxonomy | OV-1 → BP-001; SV-1 → BP-601; SV-4 → BP-104; SV-10c → 300-series; CV-2 → BP-104 Set A / Set B |
| **C4 model** | Context, Container, Component, Code + dynamic (sequence) supplements | Container = BP-001 layer ladder; Component = 200-series; Code = 100-series |
| **UML** | Sequence, state machine, class/structure | Sequence → BP-301–303; state machine → BP-304; structure → BP-202 VC structure |
| **IDEF0** | Function boxes with inputs (left), controls (top), outputs (right), mechanisms (bottom) | BP-202 verify pipeline stages are IDEF0 boxes: input VC, control schema/registry, output verdict, mechanism secp256k1 |
| **Kruchten 4+1** | Logical, process, development, physical, scenarios | the series split: 100/200 logical, 300 process, 601 physical, 300 scenarios |
| **Data-flow diagram** | Processes, stores, flows, external entities | BP-204 VIN privacy data flow (what reaches the chain, what never does) |

The DoDAF SV-10c "systems event-trace description" is simply a sequence diagram with military drawing discipline (every message numbered, every participant a named system). That is the notation for the 300-series.

### 1.3 The synthesis — one drawing-set, both grammars

Every sheet is drawn as a *machine* sheet (border, zones, title block, revision block, balloons, parts list) whose *content* uses the right *software* notation (sequence, state, IDEF0, structure). A reader who knows engineering drawings can navigate; a reader who knows architecture descriptions can read the content. The combination is what gives the higher-order argument its weight: the primitives sheet looks like a parts list because it *is* one.

## 2. The layer ladder (the inboard profile)

The system is drawn resting on what it rests on. From the keel up:

| Deck | Layer | What is there | Trust assumption it supplies |
|---|---|---|---|
| L0 | Physics, compute, energy | CPUs, HSMs, entropy sources, electricity | computational boundedness of the adversary (THREAT_MODEL §2) |
| L1 | Network and people | peer-to-peer gossip, validators/operators, economic stake, governance | liveness; honest-majority / stake-majority |
| L2 | Consensus and ledger (DLT) | block production, finality, immutable history, fee market | **T1 chain integrity** |
| L3 | Execution (EVM) | deterministic state machine, gas metering, `SSTORE`/`LOG`/`CALL`, `ecrecover` precompile | faithful contract execution |
| L4 | Identity substrate (contracts) | the nine standards + MOBI VID registry; the basic digital-ID set F1–F12 | G1–G4 authorization barriers (measured, 54 scenarios) |
| L5 | SSI layer (W3C) | DID resolver, VC issuer/holder/verifier, selective disclosure, revocation | T4 verifier correctness; T2 issuer honesty at t=0 |
| L6 | Application | vehicle, owner wallet, issuer portals, V2V BSM path at 10 Hz | SAE J2945/1 latency budget |

Each deck is a sheet (or a group). Each deck's sheet names what it inherits from the deck below and what it adds. That is the "and so on" the programme was asked for, made explicit.

## 3. The sheet list (the drawing index)

| No. | Title | Family / notation | Source of truth |
|---|---|---|---|
| BP-000 | Drawing index, legend and how to read a sheet | index | this plan |
| BP-001 | General arrangement — the layer ladder, inboard profile | GA / OV-1 / C4 container | §2 above; THREAT_MODEL §3 |
| BP-101 | Cryptographic primitive library — parts list | exploded view + BoM | contracts, `vc_issuer.py`, `birth_certificate.py` |
| BP-102 | EVM primitives and the gas schedule the registries pay | exploded view + BoM | solc 0.8.24 / cancun; MEASUREMENT_CONDITIONS §3 |
| BP-103 | ERC-1056 registry — section through the engine | section / detail | `EthereumDIDRegistry.sol` |
| BP-104 | The basic digital-ID set — IMinimalSSI F1–F12 and the catalogue ops | SV-4 / CV-2 + BoM | `BASIC_ID_SET_EXTENSION.md` §1–2, framework §2 |
| BP-105 | CVIN-Combined hybrid — section through the thesis's own engine | section / detail | `CVINCombinedIdentity.sol` |
| BP-106 | Nine substrates — comparative sections, state model and create gas | comparative section | `gas_benchmark.json` (register #25) |
| BP-201 | DID resolution assembly — did:ethr event walk to DID document | schematic | `did_resolver.py`; framework L6 |
| BP-202 | Verifiable credential — structure and the six-stage verify pipeline | structure + IDEF0 | `vc_verifier.py` |
| BP-203 | Selective disclosure and presentation — challenge and domain binding | schematic | `vc_holder.py`, `vc_verifier.py` |
| BP-204 | MOBI VID I birth certificate — VIN privacy data flow | DFD | `birth_certificate.py`, `MOBIVIDRegistryV2.sol` |
| BP-205 | MOBI VID II lifecycle event and on-chain attestation (found-and-fixed) | detail + sequence | `lifecycle_events.py`, `attestEvent` |
| BP-301 | Sequence — vehicle birth registration | SV-10c | use case 1 |
| BP-302 | Sequence — V2V BSM verification at 10 Hz with freshness-k cache | SV-10c | LATENCY_BUDGET, register #27/#32 |
| BP-303 | Sequence — ownership transfer and key rotation | SV-10c | lifecycle events 11–12 |
| BP-304 | State machine — vehicle identity over its life (17 events, roles) | UML state | framework §4.4 |
| BP-401 | Threat model — adversaries, trust bulkheads, security goals | hull-integrity schematic | THREAT_MODEL |
| BP-402 | Security-guarantee inheritance — what the ledger gives, what the application adds | inheritance ladder | THREAT_MODEL T1; `SECURITY_GUARANTEE_INHERITANCE.md` |
| BP-403 | Attack matrix — 54 cells, 43/43 applicable defended | matrix | `security_matrix.json`, `attack_results.json` |
| BP-501 | Gas ladder — create-identity cost across the ten substrates | instrument panel | register #25 |
| BP-502 | Latency budget — J2945/1 100 ms, P*(f), the freshness-k curve | instrument panel | LATENCY_BUDGET §1–4, register #32/#37 |
| BP-601 | Deployment and test harness — the shipyard | SV-1 / wiring | README, CI workflows |

Twenty-three sheets. The 100-series is the anchor: it is where the "figure on primitives and functions" lives, and every higher sheet references its balloons.

## 4. Conventions (normative for every sheet)

1. **Sheet:** 1600 × 1000 px (16:10 landscape), cyanotype palette (Prussian-blue ground, white line), zone grid A–F × 1–8.
2. **Title block** lower right; **revision block** upper right; **general notes** upper left; **parts list** where there are balloons.
3. **Balloons** are numbered per sheet; a balloon referenced from another sheet is written `BP-101/③`.
4. **Line weights:** 2.4 px object line, 1.2 px hidden / data flow, 0.8 px grid and dimension. Dashed = off-chain or untrusted; solid = on-chain or trusted.
5. **Measured numbers** carry their register row in small type (`#25`). Estimates carry `E`. Parameters carry `param`.
6. **No real insignia, service names or agency formats.** The programme name and the classification band are the thesis's own.
7. Every sheet is generated by `make_blueprints.py` from data in the script, so a sheet and the repository cannot drift apart silently; regenerating is one command.

## 5. Execution order

1. Library: sheet frame, title/revision/notes blocks, balloons, parts list, boxes, arrows, lifelines, tables. (`make_blueprints.py`)
2. BP-000, BP-001 — the frame and the inboard profile.
3. 100-series — the primitives (anchor).
4. 200-series, 300-series, 400-series, 500-series, 601.
5. PNG render through Chromium; index page; commit.
6. Plans 2 and 3; the security-inheritance note; the integration note.

Iteration is allowed and expected: a sheet that does not read well is redrawn, and the plan is amended in place rather than preserved as written.

## 6. Sources consulted for the format

- ASME Y14.1 / Y14.1M sheet size and format (DoD adoption 1995): https://www.asme.org/getmedia/8767825a-ffd0-4743-b1e4-84df93a34588/34087.pdf
- ASME Y14.35 revision practice (NDIA presentation): https://ndia.dtic.mil/wp-content/uploads/2008/technical/GastonEngineeringDrawingsY14_35.pdf
- Drawing structure and conventions (zones, title block, revision block): https://open-exam-prep.com/study-guides/asq-cqi/ch6/blueprint-structure-conventions
- DoDAF 2.02 SV-1 and SV-4: https://dodcio.defense.gov/DoDAF/dodaf20_sv1.aspx , https://dodcio.defense.gov/DoDAF/dodaf20_sv4.aspx
- DoDAF SV-10c event trace: https://acqnotes.com/acqnote/tasks/sv-10c-systems-event-trace-description
- C4 model abstraction levels and 4+1: https://www.baeldung.com/cs/c4-model-abstraction-levels
- A-class submarine *Aeneas* general arrangement, National Maritime Museum: https://www.rmg.co.uk/collections/objects/rmgc-object-49304
- H. L. Hunley cutaway, Naval History and Heritage Command: https://ibiblio.org/hyperwar/OnlineLibrary/photos/images/h58000/h58769c.htm
