# Inkwell Program: Decisions and Open Questions Register

**Document status:** Draft v0.1, 2026-10-04, owner: Program (editor-in-chief pass over all seventeen documents; every persona contributes to the round-table in Section 6).

**Read this if...** you want to know what the team has actually decided across the whole program without reading 110,000 words, where two documents written in parallel disagreed and how the disagreement was resolved, what is still open and who owns closing it, and which decisions only the founder can make before Phase 0 starts. The source documents remain the authority for detail; this register is the index of outcomes. When a source document and this register disagree, the "Reconciled decision" column here records the editor's resolution and names the document that now carries it.

## Table of contents

1. How this register was built
2. Editor's cross-document review: inconsistencies found and how they were resolved
3. Consolidated DECISION register
4. Consolidated OPEN register
5. Founder decisions needed before Phase 0
6. Closing team round-table

---

## 1. How this register was built

Seventeen Markdown documents were written in parallel by five writers on 2026-10-04: the README and team charter, nine App 1 documents (01 to 09), five App 2 Kids documents (01 to 05), the App 3 short story plan, and the master reference. The editor read all of them end to end, then:

1. Fixed inconsistencies in place with minimal edits (Section 2, column "Resolution"), always choosing a canonical document per topic: the architecture document (04) for package names and persistence, the delivery plan (03) for phasing and iOS minimum, the product brief (01) for monetization and naming, the game design spec (02) for rules and validation, the design directions document (07) for visual direction, the Kids vision (Kids 01) for age bands.
2. Left larger contradictions as OPEN items rather than silently choosing a side (Section 2, rows marked OPEN, and Section 4).
3. Collected every DECISION line, deduplicated it, and assigned a confidence: **Firm** (decided with reasoning and no contrary statement anywhere), **Provisional** (decided, but depends on a spike, a bake-off, or beta data), **Needs founder sign-off** (the team recommends, the founder decides).
4. Collected every OPEN line with an owner persona and the phase by which it must close.

Confidence levels are the editor's judgment from the documents, not a vote.

---

## 2. Editor's cross-document review

### 2.1 Inconsistencies fixed in place

| # | Topic | Where the documents disagreed | Resolution (canonical source) | Files edited |
|---|---|---|---|---|
| 1 | Package names | 04 uses `IWCore`, `IWRules`, `IWContent`, `IWDesignSystem`, `IWPersistence`, `IWMultiplayer`, `IWAnalytics`, `IWFeatureFlags`, `IWFeatures`. 02, 03, 07, Kids 01 to 03, App 3 and the master reference use the brief's GameEngine, Dictionary, DesignSystem, Networking, Persistence, plus an `InkwellKit` umbrella (03) that 04 never defines. | 04's `IW*` names are canonical. Direct renames where a single mention made it cheap (02, 03 scope bullets, 03 RACI and definition of done); one-line mapping notes where the short names are used throughout (Kids 03, master reference, 07 component table, App 3). `InkwellKit` removed; App 2 links the `IW*` packages directly. | 02, 03, 07, Kids 01, Kids 02, Kids 03, App 3, master |
| 2 | Persistence | 04 decided GRDB.swift behind a `MatchStore` protocol (ADR-004). Master reference 5.1, 5.5 and 5.8 decided SwiftData; R9 and Kids 05 assumed "SQLite or SwiftData". | GRDB per 04. Master 5.8 now carries a DECISION (superseded and reconciled) line; the surviving parts (event log canonical, rebuildable store, debug rebuild command) are kept. Kids 05 names GRDB and allows it in the Kids dependency audit as a source-only offline package. | master, Kids 05 |
| 3 | Multiplayer phasing and phase numbering | 03 puts nearby in Phase 4 and async in Phase 5, both in 1.0 behind Pro, real-time out of v1. 04 and 05 use "Phase 1 (launch), Phase 2 (Nearby), Phase 3 (Game Center)" as transport phases, which read as if nearby and async were post-launch. 08 shows Nearby "disabled v1" and Online "hidden v1". Master 4.1 and 5.4 list nearby and async under "v1.x". | 03 governs. 04's table now labels transport phases with their delivery phases and adds a numbering note; 04's and 05's "Phase 2" for CDN, remote config and diagnostics endpoint now read "post-launch 1.x" because 1.0 has zero servers. 05's privacy-label and checklist rows renamed. 08 setup modes now say Nearby (Pro, Phase 4) and Online (Pro, async only, Phase 5). Master 4.1 and 5.4 moved nearby and async into v1.0. | 04, 05, 08, master |
| 4 | Monetization | 01 decided free plus one-time Pro, no ads, subscriptions or consumables; themes inside Pro. Master 4.4 recommended cosmetic themes as a separate IAP add-on and kept a subscription "Puzzle Club" parallel pass; idea 17 said "v1.0 with two themes" as IAP; 05's 3.1.1 row said "Pro unlock and cosmetic ink themes" as separate non-consumables; 08's paywall listed a different Pro feature set. Kids 05 decided paid up front, no IAP. | 01 governs. Master 1, 4.4 and idea 17 now say themes are in Pro for v1, a la carte theme packs are a later option, subscription is rejected with no parallel pass, and the "Ink" currency (idea 18) is explicitly rejected for both apps. 05's 3.1.1 row names one Pro non-consumable. 08's paywall lists 01's Pro set. | 05, 08, master |
| 5 | Minimum iOS | 03 decided iOS 17.0 and re-evaluation at 1.1. 04 (ADR-001, open question 1) and 06 (recommendation 3, OPEN) still proposed raising to iOS 18 before launch. | 03 governs. 04 and 06 OPEN items marked closed; ADR-001 and 06's recommendation point at 03 Section 19.2. Master 1 and 5.6 say iOS 17.0 re-evaluated at 1.1. | 04, 06, master |
| 6 | Kids age band names | Kids 01 to 05 use Sprouts 5 to 7, Explorers 8 to 10, Navigators 11 to 13. Master 1, 4.2 and the glossary gave only the numbers. | Names added in master 1, 4.2 and the glossary. | master |
| 7 | Naming | 01 decided Inkwell pending clearance, fallbacks Nib, Letterhead, Foolscap, and rejected Stop!, Quill and Scribble. Master 4.1 listed Pens Down, Quill, Stop!, Scribble Table and had JOBS favor Pens Down; master 1 called Kids "Inkwell Jr., Little Inkwell". 07 Section 14 listed its own candidates and said naming is owned by the master reference. Kids 01 decided Inkling first choice, Inkwell Kids fallback, never "Jr.", which closes 01's OPEN. | 01 owns App 1 naming, Kids 01 owns App 2 naming. Master 4.1 rewritten to the decided list; master 1 and the README and charter carry Inkling pending trademark; 07 Section 14 points at 01; 01's OPEN marked closed. Kids 01 now says trademark search in Phase 2, decision in Phase 3 (it previously said the gate was Phase 2, while Kids 03 placed the decision in Phase 3). | 01, 07, Kids 01, README, charter, master |
| 8 | Default visual direction | 07 decided Paper & Ink default, Swiss Editorial free, Night Lounge Pro, Playful Pop skunkworks, Quiet Minimal skeleton. Master 6.2 used different names (Ink and Paper, Neon Night, Swiss Grid, Playroom, Letterpress Studio), made Swiss a Pro theme and Neon the first paid theme, had no Quiet Minimal skeleton, and said Playroom was "handed to Kids", while Kids 04 chose Bright Blocks with crayon-styled characters. | 07 governs. Master 6.2 table and DECISION rewritten with 07's names and roles; Letterpress Studio noted as surviving only as the tile idea; Kids direction stated. Master 6.6 "Neon Night" renamed. | master |
| 9 | Validation policy | 02 decided hybrid three-state dictionary plus non-author majority vote in every mode, including async (24 h window, fallback to dictionary state). Master 3.6 decided `.dictionaryFinal(allowDispute: true)` as the async default; master 3.1 had "the host can overrule"; 04 Section 6.6 had solo unknowns counting as invalid unless an "I insist" token; 04 Section 8 and 08 Section 7.2 had tie rules different from 02 (to the submitter, to the writer). | 02 governs. Master 3.6 DECISION rewritten as reconciled; master 3.1 step 4 now describes the vote and the Designated judge house rule; 04 Section 6.6 and 8 and 08 Section 7.2 now use 02's tie rule, solo self-judging and two-player challenger rule; the "I insist" OPEN in 04 is closed. | 04, 08, master |
| 10 | Rules details that drifted | Master 3.1: letter exclusion of Q X Z "on by default" (02: Classic excludes nothing, weights availability); timer presets 120/60/30/15 (02: 120/60/45/30); up to 10 categories (02: 3 to 8); long-word bonus +2 at 8 letters (02: +1 per letter beyond six, max +5); Word Chain "wild tail" rule (02: Reroll default); bot tier "Expert" (02: Ruthless). 08: timer presets 90/60/30, rounds 3/5/10, bot tiers Easy/Normal/Hard, stop-rule grace 10 s (02: 5 s), 04: grace 3 s. | 02 governs. All listed values aligned in master 3.1, 3.2, 3.4, 3.5 and the glossary, and in 08 Sections 3.2, 3.7, 4.2 and 11, and 04 Section 8. | 04, 08, master |
| 11 | Anti-cheese rules in the UX plan | 08 Section 5.4 had autocorrect on and paste allowed during rounds; 01's first-60-seconds spec and 02 Section 12 require autocorrect, predictive text and paste off in timed rounds. | 02 governs; 08 edited, with the fuzzy "did you mean" path named as where corrections happen. | 08 |
| 12 | Word list licensing | 04 ADR-007 excludes Wiktionary-derived data from v1 packs because of ShareAlike. 02 Section 9.2 and 11.1, 03's go/no-go licenses line, Kids 02 Section 12.1, Kids 03 Section 4 and master 5.3 all still listed Wiktionary as an App 1 source. | 04 governs for App 1 v1. Each mention now notes the exclusion; Animals and Foods seed from WordNet plus curation; Wikidata CC0 is being verified for Movies and Brands; Wiktionary stays reserved for App 3 packs with published derived lists. | 02, 03, Kids 02, Kids 03, master |
| 13 | Theme scope in the delivery plan | 03 Phase 2 shipped "light paper and dark paper" and Phase 4 a "third theme (Pro): one more paper and ink combination", with cut-list item 3 "Pro has two themes". 07 ships Paper & Ink plus Swiss Editorial (free) plus Night Lounge (Pro). | 07 governs for which themes; 03 Phase 4 scope and cut-list item 3 renamed to Swiss Editorial and Night Lounge. The effort gap is left OPEN (Section 2.2, row B). | 03 |
| 14 | App 1 facts stated in Kids documents | Kids 03 said App 1 allows a third-party analytics SDK and third-party crash reporting (04: none in production; Sentry in TestFlight only; label "Data Not Collected"); App 1 coverage "at least 80 percent" (03: 90 percent gate; 05: 95 percent target); App 1 release cadence "every 2 to 3 weeks" (05: every 4 weeks; master said two weeks). Kids 02 placed nearby play in "Phase 4" and a Classroom edition in "Phase 5" of Kids 03, which has nearby as a post-launch stretch and no Phase 5. | 04, 03 and 05 govern. Kids 03 table cells corrected; master 5.7 cadence corrected to four weeks; Kids 02 phase references corrected. | Kids 02, Kids 03, master |
| 15 | Kids reuse of DesignSystem | Master 4.2 and 4.3 said Kids reuses "the core of DesignSystem"; Kids 03 decided tokens only, with a separate `KidsDesignSystem`. Master 6.3 planned Rive for Kids characters; Kids 04 decided no third-party animation runtime in v1. | Kids 03 and Kids 04 govern. Master 4.2, 4.3 (diagram) and 6.3 edited. | master |
| 16 | First-run time standard | Master checklist item 1 said "under 20 seconds"; 07 and 08 standardize on 10 seconds; 01's storyboard reaches a round at about 5 s. | 08 governs the acceptance test (FR-01, under 10 s on iPhone 12). Master item 1 edited. | master |
| 17 | iPad in v1 | 05 left "iPad as a v1 target" OPEN with JOBS saying no; 01's kill list already decided "runs well on iPad" floor with bespoke deferred; 03's device lab includes an iPad. | 01 governs. 05's OPEN narrowed to the Phase 7 large-canvas question; one physical iPad smoke pass per release candidate added. | 05 |
| 18 | Em-dashes and README links | Scan found em-dashes only in H1 titles and persona tags, which the brief permits. README's only unresolved link pointed at this file. | No prose edits needed. This file resolves the link. README and charter gained a naming sentence. | README, charter |

### 2.2 Contradictions judged too large to fix silently (left OPEN)

| # | Topic | The contradiction | Why it is not an edit | Recommended owner and phase |
|---|---|---|---|---|
| A | Cold launch budget | 01: under 1.5 s on iPhone 12, under 1.0 s on current devices. 03: p90 under 1.5 s on iPhone SE 2nd gen. 04: 800 ms p90 (target 500) on iPhone 11 or SE 3rd gen. 05: 800 ms p90 on SE 3rd gen. 09: under 400 ms on iPhone 12. Five numbers, three device baselines. | A single number must be chosen against a single device, and the choice changes the Phase 1 exit criterion and the nightly CI gate. | QA with IOS, close in Phase 0. Recommendation: 800 ms p90 to interactive Lobby on the oldest Tier A device as the release gate (05), 1.5 s as the never-exceed floor on the oldest supported device (03), and retire the 400 ms and 1.0 s figures. |
| B | Theme effort versus schedule | 07 estimates Paper & Ink at 3.5 to 4.5 EW, Swiss Editorial 2 to 2.5 EW and Night Lounge 4 to 5 EW beyond the skeleton (roughly 10 to 12 EW). 03 budgets Phase 2 "feel" at 7 EW for everything and the Pro theme at 0.5 EW. Master idea 17 assumed 1 week per theme. | Reconciling means either cutting a theme from 1.0 or adding weeks to a plan with zero slack. That is a founder-level scope call. | JOBS with DESIGN and ARCH, close in Phase 0 planning. Recommendation: Paper & Ink and Swiss Editorial in 1.0; Night Lounge reduced to a token-and-sound pass (no CRT shader, no animated glass) or moved to 1.1 as the first Pro content drop. |
| C | Beta program length versus the 24-week calendar | 05's four-stage beta (3 + 3 + 4 + 1 weeks, up to 2,000 testers) is eleven weeks; 03 fits two external betas into Phase 5's four weeks with 200 to 500 testers. Master said 50 to 200 weekly. | The quality plan and the delivery plan cannot both be true; QA explicitly wants two betas two weeks apart as the minimum, which 03 already honors. | QA with ARCH and JOBS, close by W10. Recommendation: adopt 03's two external betas inside Phase 5 as the committed plan; treat 05's open beta stage as what happens if the date moves by the cut list, not as the baseline. |
| D | Performance floor device | 03: iPhone SE 2nd generation (A13) on iOS 17 is the floor and is in the device lab. 04 and 05: iPhone 11 or SE 3rd generation (A15) is the baseline, SE 3 is Tier A. | Picking the device changes what "no dropped frames" means for the ink effects and what the lab buys. | IOS with QA, close in Phase 0. Recommendation: SE 2nd gen stays the launch-time floor (it is the oldest A13 class on iOS 17); SE 3rd gen is the Tier A "flawless" device for motion. |
| E | Nearby host loss behavior | 02 and 03: on host disconnect, pause 30 s then offer "continue as pass-and-play" with the ledger intact. 04 Section 8: host migration after a 5 s timeout to the lowest `PeerID`, with log rebroadcast. | Host migration is more code and more test surface, and it changes the nearby state machine in 02. Both are defensible; one must be chosen before the W5 spike. | ARCH with GAME and IOS, close by the nearby spike (W6). Recommendation: ship 02's pause-then-fallback in 1.0 (fewer message types, matches the "degrade to pass-and-play without losing a point" promise); keep host migration as the 1.1 improvement if beta shows frequent host drops. |
| F | Timer behavior when the app is backgrounded | 02 Section 12: the timer keeps running on wall-clock time (anti-peeking), with a "left the table" mark. 02 edge case 13 and 04 Section 4.1: pause on interruption is default on for pass-and-play and solo. 08: solo pauses; pass-and-play is OPEN. | Three statements in two documents from the same owner; the right answer may differ by mode and by "phone call" versus "switched apps", which is a rules decision. | GAME, close in Phase 1 before the first solo build. Recommendation: solo pauses (no one to cheat); pass-and-play pauses on system interruptions (calls) but keeps running on app switching with the mark; nearby and async never pause. |
| G | Family-safe profile: reject or suppress profanity | 01 (DATA): profanity is excluded from the valid list, the app will not validate it. 02 edge case 34: a profane word is validated for scoring like any other word, never suggested or shown in share images. Master 5.3: the blocklist never applies to private in-game entries. | This is a product stance about the adult app (is "ass" a valid Animal?) with App Review and family-persona implications, and the two statements are both DATA's. | DATA with GAME and JOBS, close in Phase 1 before dictionary v0. Recommendation: 02's position (score it, never promote it, mask it in anything shared) because the family-safe promise in 01 is about what the app shows and suggests, not about policing a private table. |
| H | Localization package | App 3 and the master reference depend on a Localization package (units, collation, category names) that 04's nine-package list does not include; App 3's seven constraints are added to App 1 acceptance criteria. | Adding a tenth package or folding the `WritingSystem` protocol into `IWCore` is an architecture decision with CI implications (the non-Latin unit test). | ARCH, close in Phase 0. Recommendation: `WritingSystem` protocol in `IWCore`, English implementation in `IWContent`'s base pack, no tenth package until App 3 Phase A. |
| I | Kids app and `IWFeatures` | 04's dependency diagram has the InkwellKids target consuming `IWFeatures` and `IWDesignSystem`; Kids 03 decided tokens only and its own kid feature code. | The diagram is a design statement, not a typo; 04 should be amended by its owner. | ARCH, close in App 1 Phase 0 (so the package graph is right from day one). Recommendation: Kids 03 is right; amend 04's diagram. |
| J | Letter draw duration | 01 and master: 1.2 s ceremony, tap to skip, scaled by preset (1200/700/400 ms). 07 and 09: M01 Letter Draw is 600 ms, with 09 as the governing catalog. | A 2x difference in the single most important animation; it is a taste decision JOBS and DESIGN must make on a device, not in a register. | DESIGN with JOBS, close at the W4 direction demo. Recommendation: build both; 09's catalog is updated to whatever wins, and the preset scaling from master 6.8 applies either way. |
| K | Share card content | Master idea 3: spoiler-free card with no words (10/5/0 glyph grid). 03 Phase 2 and 08 Section 3.6: an image of the final ledger with names. | Trademark exposure in shared cards (master R4) versus the "show your friends what you wrote" loop are different product goals. | DESIGN with DATA and JOBS, close in Phase 2. Recommendation: ledger with names and words by default (it is the party's record), with a one-tap spoiler-free variant for public posting. |
| L | Dictionary size budget | 02: ARCH 12 MB total versus DATA 18 MB. 04: 6 MB base pack in bundle plus up to 12 MB optional downloaded on demand. Master: under 6 MB. 1.0 has no download path. | Depends on whether Movies and Cities ship in the bundle in 1.0, which is also cut-list item 6. | DATA with ARCH, close at the dictionary freeze (W14). Recommendation: 6 MB base plus Movies and Cities in the bundle if they fit under 12 MB total; otherwise cut-list item 6 applies. |
| M | Bot tiers and personalities | 02: three data-driven tiers (Casual, Clever, Ruthless), plus a Kids "Buddy" row. Master idea 19 (in the v1.0 list): three named bots with ink portraits. Kids 02: four named characters (Pip, Wren, Rook, The Librarian). | Named adult bots are a design and copy commitment on top of the engine; the engine design is unaffected. | GAME with DESIGN, close in Phase 3. Recommendation: tiers stay data; names and portraits for App 1 are a Phase 3 nice-to-have that falls to 1.1 if Phase 3 is tight. |

---

## 3. Consolidated DECISION register

Confidence: **Firm**, **Provisional**, **Founder** (needs founder sign-off). "Source" gives the document path and section. Where two documents decided the same thing differently, the reconciled decision is shown and both sources are listed.

### 3.1 Product and scope

| # | Decision | Source | Confidence |
|---|---|---|---|
| P1 | App 1 ships exactly two games: NPAT and Word Chain. | app1-inkwell/01 §12; master §1 | Firm |
| P2 | The first-60-seconds storyboard is a binding acceptance spec; zero modals before the first round; any PR that adds one is rejected. | app1-inkwell/01 §5; app1-inkwell/08 §2 | Firm |
| P3 | The kill list is binding for v1: no accounts, friend lists, chat, ads, energy or currencies, hint purchases, public matchmaking, Android, Watch, UGC category marketplace, multi-screen onboarding. Reopening requires a one-page case and a demo. | app1-inkwell/01 §6 | Firm |
| P4 | First run goes straight into a solo NPAT round with inline hints; no prompts of any kind in session one. | app1-inkwell/08 §2 | Firm |
| P5 | The Lobby is two cards plus one nav-bar icon; each card may show one line of recent-play context; no promotional surfaces. | app1-inkwell/08 §1 | Firm |
| P6 | Working title Inkwell; trademark clearance and App Store name reservation in Phase 0; fallbacks ranked Nib, Letterhead, Foolscap. Master reference and 07 now defer to this. | app1-inkwell/01 §8; master §4.1 (reconciled) | Founder |
| P7 | Monetization: free download plus one-time Inkwell Pro non-consumable via StoreKit 2. Free tier complete for solo and pass-and-play with classic rules, default theme, unlimited rounds. Pro unlocks nearby, online async, house rules, category packs, Night Lounge theme, stats. Host-pays for multi-phone sessions. No ads, no subscription, no consumables, ever. Themes are inside Pro for v1; a la carte theme packs are a later option. | app1-inkwell/01 §11; app1-inkwell/07 §9; master §4.4 (reconciled) | Founder |
| P8 | Recommended price frame: Pro at $6.99 US with a $4.99 introductory price for four weeks, Family Sharing on. | app1-inkwell/01 §10 | Founder |
| P9 | The "Ink" soft currency is rejected for both apps. | master §7 idea 18; app2-inkwell-kids/02 §10 | Firm |
| P10 | Family-safe dictionary profile is the default in App 1; explicit content is an adult opt-in, device-level. | app1-inkwell/01 §12; app1-inkwell/02 §8 | Firm (what it means for validity is OPEN G) |
| P11 | Second-round rate is the headline health metric for launch; under 70 percent stops feature work. | app1-inkwell/01 §7 | Firm |
| P12 | Success targets: D1 40 percent, D7 20 percent, D30 10 percent, crash-free 99.8 percent, rating 4.7 or higher, Pro conversion 4 percent of D7 users. | app1-inkwell/01 §7 | Provisional |
| P13 | Online async is in the Phase 5 plan behind Pro, Word Chain async first, NPAT async second; real-time online is out of v1 and demoted to a flag-gated skunkworks experiment; async is the pre-approved first cut if Phase 5 slips. | app1-inkwell/03 §19.1; app1-inkwell/04 §7.1; master §4.1 (reconciled) | Founder |
| P14 | iPad: v1 ships a "runs well on iPad" layout; a bespoke iPad design is a Phase 7 pass. | app1-inkwell/01 §6; app1-inkwell/05 §3 (narrowed) | Firm |
| P15 | Android is not on the 12-month roadmap; the three portable assets (engine spec plus fixtures, content packs, tokens) are maintained as if it were. | app1-inkwell/06 §8 | Firm |
| P16 | Build natively from day one; keep the engine portable through schema, replay fixtures and a conformance runner, not a second language; web prototyping is allowed for rules experiments only and nothing from it is "ported". | app1-inkwell/06 §5 | Firm |
| P17 | v1.0 ships master ideas 1 (ink-wheel draw), 3 (result cards), 17 (themes inside Pro), 19 (bot personalities, see OPEN M), 21 (pens-down hand-off), 22 (dispute screen), 24 (no A to Z in code). v1.1 takes 2, 4, 5, 7, 8, 10. v1.2 takes 13, 15 (link sharing only), 16. Parallel passes: 6, 11, 14. Skunkworks: 9, 12, 23, the tactile tile. Killed: the marketplace and the currency. | master §7.1 | Provisional |
| P18 | App 3 is design-for-now, build-later; its seven App 1 constraints (no hardcoded A to Z, grapheme iteration, normalize before compare, leading/trailing layout, locale-aware hero glyph, category identifiers, unit-keyed dictionary format) are App 1 acceptance criteria. | app3-multilingual §7 | Firm |

### 3.2 Game rules

| # | Decision | Source | Confidence |
|---|---|---|---|
| G1 | The engine is a pure, seeded, deterministic state machine; timers, network and UI are effects outside it. | app1-inkwell/02 §1, §17; app1-inkwell/04 §1, §3 | Firm |
| G2 | Classic NPAT scoring 10/5/0 is the default; Strict, Scattered, long-word, alliteration, speed and perfect-sheet bonuses are toggles. | app1-inkwell/02 §5; master §3.5 (reconciled) | Firm |
| G3 | No first-to-stop bonus by default; a +3 speed bonus exists as an off-by-default toggle only with the Stop rule. | master §3.5; app1-inkwell/02 §5.1 (reconciled) | Firm |
| G4 | Letter draw is availability-weighted with no repeats in a game; Classic uses square-root flattening and excludes nothing; Gentle excludes Q, X, Z and letters under 0.15 availability; Hard is uniform; exclusions are visible on the wheel. | app1-inkwell/02 §6; master §3.1 (reconciled) | Firm |
| G5 | Default timers: NPAT 60 s (Relaxed 120, Quick 45, Blitz 30, Off); Word Chain 30 s pass-and-play, 15 s solo, 7 s Blitz, Off allowed. | app1-inkwell/02 §7; app1-inkwell/08 §3 (reconciled) | Firm |
| G6 | Game length presets: Quick 3, Classic 5, Long 8, Marathon 13 rounds, or first to 150. | app1-inkwell/02 §7.3 | Firm |
| G7 | House rules (24 toggles) live on one screen, never in the default flow, each explained in one sentence; stored per "table" so a group's rules persist. | app1-inkwell/02 §8 | Firm |
| G8 | Validation is fully on-device with three visible states (accept, unsure, reject); hybrid adjudication: any non-author may challenge during the reveal window, majority of non-authors decides, ties fall back to the dictionary state; two players: the challenger decides with a three-lost-challenges limit; solo self-judges and records it; async uses the same vote with a 24 h window and falls back to the dictionary state when unresolved. Challenge mode house rule: Vote (default), Dictionary only, Honor system, Designated judge. | app1-inkwell/02 §9.5, §16; master §3.6 (reconciled); app1-inkwell/04 §6.6, §8 (reconciled) | Firm |
| G9 | Names are never REJECTed by the dictionary, only UNSURE; Places unlisted are UNSURE; fictional places accepted only with the house rule. | app1-inkwell/02 §9.3 | Firm |
| G10 | Duplicate keys fold case, diacritics, whitespace and hyphens, possessives, and by default plurals and leading articles; synonym and abbreviation folds are off by default. Duplicates are detected before validation is final; a surviving answer of a rejected pair is re-scored unique. | app1-inkwell/02 §10 | Firm |
| G11 | Fuzzy tolerance: Off, Gentle (auto-correct distance 1 at 5+ letters), Standard (propose at the reveal, default). | app1-inkwell/02 §9.4 | Firm |
| G12 | Word Chain default is Lives mode (3 lives) with Reroll on dead-end letters (Use letter and Last vowel as options); link letter comes from the word as typed; bot tiers (Casual, Clever, Ruthless) are data rows. | app1-inkwell/02 §11; master §3.2, §3.4 (reconciled) | Firm |
| G13 | Autocorrect, predictive text and paste are disabled in timed rounds; timing uses a monotonic clock; answers are sealed by hash commitment in nearby play. | app1-inkwell/02 §12; app1-inkwell/08 §5.4 (reconciled) | Firm |
| G14 | The scoring reveal is the protected "juice" moment and is never cut; it runs category by category, player by player, duplicates after each category, totals last, tap anywhere to skip, 6 s cap at four players, 8 s at eight. | app1-inkwell/02 §13, §17; app1-inkwell/08 §7 | Firm |
| G15 | The first round is the tutorial: one-line card descriptions, faint placeholders, one-time inline captions, a "How to play" sheet under 120 words per game; no carousel. | app1-inkwell/02 §14; app1-inkwell/08 §2 | Firm |
| G16 | Host-authoritative event ordering plus commit-reveal for answers in every networked mode; no CRDTs because every mode has a single orderer. | app1-inkwell/04 §8, §9 | Firm (host-loss behavior is OPEN E) |
| G17 | Stop-rule grace defaults to 5 s (0, 5, 10 s options); stop requires every field non-empty. | app1-inkwell/02 §2.2, §8; app1-inkwell/04 §8 and app1-inkwell/08 §4.2 (reconciled) | Firm |
| G18 | Word Chain in the UX plan: vertical list with a lifted hero-letter strip; ribbon rendering only for Swiss Editorial with a VoiceOver list alternative; spiral is skunkworks. | app1-inkwell/08 §6 | Firm |
| G19 | NPAT answer entry: Layout 3 (hybrid expanding stack) default; Layout 2 (paged) at AX3 and above and as a setting; no live dictionary validation; a quiet letter-mismatch helper is allowed; no swipe-to-dismiss; explicit Quit with confirmation. | app1-inkwell/08 §5 | Firm (helper in v1 is OPEN) |
| G20 | One joke in the app: the bot's concession line. | app1-inkwell/08 §10 | Firm |

### 3.3 Platform and architecture

| # | Decision | Source | Confidence |
|---|---|---|---|
| A1 | Native SwiftUI, iOS 17.0 minimum for 1.0, Swift 6 strict concurrency, Xcode 16+, Swift Packages; the current shipping iOS is the primary design and test target; re-evaluate the minimum at 1.1 with App Store Connect data. Shared packages keep an iOS 17 deployment target for App 2. | app1-inkwell/03 §19.2; app1-inkwell/04 ADR-001; app1-inkwell/06 §6, §10; master §5.6 (all reconciled) | Founder |
| A2 | P1 (pure deterministic engine) governs; conflicts between principles resolve in favor of P1, then P2 (offline-first, account-free local play). | app1-inkwell/04 §1 | Firm |
| A3 | Nine packages: `IWCore`, `IWRules`, `IWContent`, `IWDesignSystem`, `IWPersistence`, `IWMultiplayer`, `IWAnalytics`, `IWFeatureFlags`, `IWFeatures`; the first three are platform-pure and built on Linux in CI. Other documents' GameEngine, Dictionary, Networking map onto these. | app1-inkwell/04 §2, ADR-005; app1-inkwell/03 §4 (reconciled) | Firm (Localization is OPEN H) |
| A4 | Reducer `(State, Event) -> (State, [Effect])` with an event-sourced, hash-chained match log as the source of truth; derived state is a cache with snapshots every 25 events; undo is an event. | app1-inkwell/04 §3, ADR-002 | Firm |
| A5 | Engine time is monotonic ticks; `ContinuousClock` behind a protocol; `timerExpired` carries the deadline tick; no `Timer`. | app1-inkwell/04 §4, ADR-003 | Firm |
| A6 | Persistence: GRDB.swift over SQLite behind a `MatchStore` protocol, WAL mode, explicit SQL migrations, schema v1 as specified; SwiftData is a parallel pass for the iCloud era; no iCloud sync in v1. | app1-inkwell/04 §5.3, ADR-004; master §5.5, §5.8 (reconciled) | Firm |
| A7 | Content packs: DAWG plus front-coded lists, LZFSE, Ed25519-signed manifests; bundle-only in 1.0; static CDN post-launch; a server-side validation API is never planned. | app1-inkwell/04 §6.3, ADR-006 | Firm |
| A8 | Shipped packs contain only public-domain, MIT-like, WordNet-licensed and CC BY data with in-app attribution; Wiktionary-derived data is excluded from v1 packs; Wikidata CC0 to verify for Movies and Brands. | app1-inkwell/04 §6.5, ADR-007; app1-inkwell/02 §9.2 (reconciled) | Firm |
| A9 | Multiplayer phasing: pass-and-play, then nearby over MultipeerConnectivity (delivery Phase 4), then Game Center turn-based (delivery Phase 5); real-time is flag-gated skunkworks; a custom server is not in the 12-month plan. | app1-inkwell/04 §7.1, ADR-008; app1-inkwell/03 §19.1 | Firm |
| A10 | All transports carry the same `SignedEvent` through a `MatchTransport` protocol; pass-and-play runs through `LocalTransport` so multiplayer code is exercised by every local test. | app1-inkwell/04 §7.2 | Firm |
| A11 | Single `NavigationStack`, rounds as full-screen covers, no `TabView` in v1; protocol DI via `Environment`; previews mandatory per component state. | app1-inkwell/04 §10, ADR-016 | Firm |
| A12 | Design tokens are generated from `tokens.json`; a lint rule forbids literal colors and durations in feature code. | app1-inkwell/04 §10.4, ADR-015; app1-inkwell/07 §10 | Firm |
| A13 | Swift 6 strict concurrency everywhere; two actors (`MatchSession`, `Dictionary`); `@preconcurrency` exceptions documented in ADR-009. | app1-inkwell/04 §11 | Firm |
| A14 | Performance budgets as in 04 §12 and 05 §4 are CI gates, verified weekly on devices. | app1-inkwell/04 §12; app1-inkwell/05 §4 | Provisional (cold launch number is OPEN A) |
| A15 | Dual-definition motion tokens (full and reduced) and model-owned accessibility descriptions; accessibility audits are release gates. | app1-inkwell/04 §13 | Firm |
| A16 | No third-party analytics SDK in v1; first-party local counters only; privacy label target "Data Not Collected"; a compile-time `KidsMode` removes `IWAnalytics`'s network sink. | app1-inkwell/04 §14, ADR-012; app1-inkwell/05 §7 | Firm |
| A17 | Feature flags: local typed flags with a debug menu for v1; signed remote JSON post-launch; a flag never alters a saved match's rules. | app1-inkwell/04 §15, ADR-013 | Firm |
| A18 | Observability: MetricKit plus Xcode Organizer in production; Sentry in TestFlight builds only; 30-day post-launch review. | app1-inkwell/04 §16, ADR-011 | Provisional |
| A19 | Build pipeline: Xcode Cloud for app builds and TestFlight; GitHub Actions Linux runners for the pure packages; Fastlane for screenshots and metadata only. | app1-inkwell/04 §18, ADR-014 | Firm |
| A20 | Approved platform parallel passes: Rive letter-reveal (3 days), web rules sandbox (2 days, GAME only); Kotlin conformance stub deferred to post-launch; Flutter and React Native passes not approved. | app1-inkwell/06 §7, §10 | Firm |
| A21 | Zero servers in 1.0; infrastructure cost target $0 per month beyond the developer program fee. | app1-inkwell/03 §1; app1-inkwell/04 §7 | Firm |

### 3.4 Design and motion

| # | Decision | Source | Confidence |
|---|---|---|---|
| D1 | Seven design principles (letter is the hero; play in ten seconds; one hero moment per screen; legible at AX5; honest materials; physical feedback; themes change clothes not bones) are review gates. | app1-inkwell/07 §1 | Firm |
| D2 | Default direction A Paper & Ink; B Swiss Editorial ships free; D Night Lounge ships in Pro; C Playful Pop is parked skunkworks until Kids has defined its look; E Quiet Minimal is the skeleton, built first, never shipped as a face. The theme picker has exactly three tiles. | app1-inkwell/07 §9; master §6.2 (reconciled) | Founder |
| D3 | Night Lounge suggests, never forces, a blitz house-rules preset on first selection. | app1-inkwell/07 §9 | Firm |
| D4 | Three-layer token model (primitive, semantic, component), JSON source of truth, generated Swift; layout primitives (spacing, radius, tap targets) are not themeable; every theme ships light, dark and increased-contrast variants with CI contrast tests; themes follow the system appearance. | app1-inkwell/07 §10 | Firm |
| D5 | The results table design is borrowed from Swiss Editorial across all themes. | app1-inkwell/07 §9, §16 | Firm |
| D6 | App icon is a single drawn letter ("I"), static; alternate icons per theme; no quill, inkwell or feather. | app1-inkwell/07 §13 | Firm |
| D7 | No mascot with eyes in App 1. | app1-inkwell/07 §5 | Firm |
| D8 | Seven motion principles with concrete tests; durations, springs, curves and staggers are tokens; a new duration requires a new token and a review. | app1-inkwell/09 §1, §2 | Firm |
| D9 | SwiftUI-first animation stack (core, PhaseAnimator, KeyframeAnimator); SpriteKit overlay for particles; SwiftUI Shader for ink bleed, grain and ambient drift with static fallbacks; Lottie only for small illustrative loops; Rive is skunkworks; at most one third-party animation runtime in the shipping binary, possibly none; the bake-off decides M01 and shader fallbacks. | app1-inkwell/09 §5; master §6.3 (reconciled) | Provisional |
| D10 | Springs for interactive and layout motion; authored curves only for the letter-draw path trim and the reveal cadence. | app1-inkwell/09 §10 | Firm |
| D11 | The animation catalog is capped at 32 entries for v1; a new entry requires retiring one. | app1-inkwell/09 §10 | Firm |
| D12 | Letter draw duration scales with the timer preset and is always tap-to-skip, always a live glyph, with a 120 ms cross-fade under Reduce Motion. The absolute duration is OPEN J. | master §6.8; app1-inkwell/09 §4 | Provisional |
| D13 | Sound: S1 Foley is the default pack, S2 Tonal ships with Swiss and as the fallback, S3 Electric ships with Night Lounge in Pro; sound packs are theme bundle contents, not separate purchases; no sound on launch, ever; no music during a round. | app1-inkwell/09 §6 | Firm |
| D14 | Haptics: system patterns via `sensoryFeedback` where they fit, Core Haptics AHAP files for the eight roles with a pattern identity; AHAP files live in the theme bundle keyed by role; intensity setting Off, Light, Standard; no haptic without a visual. | app1-inkwell/09 §7; app1-inkwell/08 §8 | Firm |
| D15 | Prototyping: Figma for tokens and screens, Principle or Origami for timing studies, Xcode Previews for the truth; hidden developer menu with 10x slow motion and a Reduce Motion override in internal builds. | app1-inkwell/09 §9 | Firm |
| D16 | Timer VoiceOver announcements at 30, 20, 10, 5 to 1 and "Time's up"; one-field-at-a-time is automatic at AX3 and above and a setting otherwise. | app1-inkwell/08 §9 | Firm |
| D17 | Copy voice: a sharp, warm friend; short sentences; no "Oops", no emoji, at most one exclamation mark in celebrations; the 30 reference strings in 08 §10 are the style guide. | app1-inkwell/08 §10 | Firm |

### 3.5 Quality and release

| # | Decision | Source | Confidence |
|---|---|---|---|
| Q1 | 24-week plan to submission (range 20 to 26), 44 engineer-weeks against 44 of capacity, buffer inside Phases 5 and 6 spent only via the ordered cut list; phase order Foundations, Engine plus NPAT solo, Pass-and-play plus feel, Word Chain plus rules plus dictionary freeze, Nearby plus Pro, Async plus beta plus polish, Launch, Post-launch. | app1-inkwell/03 §3, §20 | Provisional |
| Q2 | Friday demo every week; a demo is a build on a phone; no phase exits on slides. | app1-inkwell/03 §1, §20; charter §5 | Firm |
| Q3 | Skunkworks items are time-boxed and die if not demoed by their Friday. | app1-inkwell/03 §13 | Firm |
| Q4 | Date-driven schedule with a non-negotiable quality bar; every date move pairs with a cut from the ordered list and is announced at a Friday demo. | app1-inkwell/03 §19.3 | Firm |
| Q5 | Never cut: scoring reveal, letter draw ceremony, pass-and-play, challenge flow, Reduce Motion alternatives, VoiceOver support, family-safe default, first-60-seconds spec, two betas. | app1-inkwell/03 §18 | Firm |
| Q6 | Dictionary v1 freezes at W14; later fixes ride point releases except offensive-content fixes, which ship immediately. | app1-inkwell/03 §7, §20 | Firm |
| Q7 | Test pyramid: Swift Testing for new tests, XCUITest for twelve critical flows, pointfreeco snapshot tests for the design system, property tests at 1,000 iterations per PR and 50,000 nightly, replay fixtures from every bug, accessibility audits automated per PR and manual per release candidate. Coverage gate 90 percent on the pure packages, target 95 percent. | app1-inkwell/05 §2; app1-inkwell/03 §16 (reconciled) | Firm |
| Q8 | Device matrix Tiers A, B, C with iPad in Tier C plus one physical iPad smoke pass per release candidate; the oldest supported iOS point release is tested on a physical device per release candidate. | app1-inkwell/05 §3 (narrowed) | Firm (floor device is OPEN D) |
| Q9 | Crash-free sessions at or above 99.8 percent in external beta for seven days is the gate; 99.9 percent is the production target at 30 days; hang rate under 0.1 percent; zero lost matches across 100 force-quits. | app1-inkwell/05 §4 | Firm |
| Q10 | Two external TestFlight betas inside Phase 5 as the committed minimum, recruited through the five personas and family groups; Sentry in TestFlight builds only; beta consent note tells parents children may be present and never asks for a child's name. | app1-inkwell/03 §9; app1-inkwell/05 §5 | Provisional (program length is OPEN C) |
| Q11 | App Store Review checklist executed with evidence per submission, mapped to guideline sections; the live guidelines are re-read before each submission; review notes include a demo video, a sandbox Pro account and the challenge-vote explanation. | app1-inkwell/05 §6; app1-inkwell/03 §17 | Firm |
| Q12 | Privacy label "Data Not Collected" at launch; `ITSAppUsesNonExemptEncryption = NO`; any SDK that would change the label needs an ADR. | app1-inkwell/05 §7, §8 | Firm |
| Q13 | Age rating: answer the questionnaire conservatively and accept the computed result (likely 9+ or 13+ for peer-visible typed words). | app1-inkwell/05 §9 | Firm |
| Q14 | Release train: semantic versioning, minor release every four weeks after launch, trunk-based with `release/*` branches, five-day code freeze, manual release control, phased release on every update, hotfix process with expedited review. | app1-inkwell/05 §10 to §12; master §5.7 and app2-inkwell-kids/03 §6 (reconciled) | Firm |
| Q15 | Five-day soft launch in two small English-speaking storefronts, then worldwide on day six. | app1-inkwell/05 §14 | Firm |
| Q16 | The 48-item "perfect app" bar is adopted; six items (Reduce Motion alternatives, zero accessibility audit failures, VoiceOver full match, purchase and restore in production, privacy label matches behavior, 99.8 percent crash-free in beta) are non-waivable. | app1-inkwell/05 §17 | Firm |
| Q17 | Rating prompt, if shown, only after a completed multi-round session with a positive signal, never during a round or on first launch, at most once per version. | app1-inkwell/03 §9; app1-inkwell/05 §16 | Provisional (whether to show it at all is OPEN) |
| Q18 | App 2 Phase 0 starts at W25 on the shared packages, after App 1 ships. | app1-inkwell/03 §11; app2-inkwell-kids/03 §7 | Firm |

### 3.6 Kids edition

| # | Decision | Source | Confidence |
|---|---|---|---|
| K1 | Separate app, separate bundle identifier, listed in the Kids Category, built on the shared engine packages; a kids mode inside App 1 and a forked codebase are both rejected. | app2-inkwell-kids/01 §2 | Firm |
| K2 | Three product bands: Sprouts 5 to 7, Explorers 8 to 10, Navigators 11 to 13, chosen around literacy and mapped to Apple's store bands; master reference and glossary now use these names. | app2-inkwell-kids/01 §3; master §4.2 (reconciled) | Firm |
| K3 | Twelve kid design principles with tests; auto-read on screen entry for Sprouts, a single screen-level speaker plus tap-to-hear on categories for older bands. | app2-inkwell-kids/01 §4 | Firm |
| K4 | The refusal list is a contract: no ads (including house ads), chat, open social, loot boxes, streaks, variable rewards, push notifications, accounts, third-party analytics, link-outs from kid screens, energy systems, review prompts to children, scary imagery. Letter of the day is allowed with no missed-day record and no notifications. | app2-inkwell-kids/01 §5 | Firm |
| K5 | No remote analytics in v1; playtest-measured joy signals; on-device learning signals shown to the parent; parent NPS through a gated optional form. | app2-inkwell-kids/01 §6; app2-inkwell-kids/03 §5 | Firm |
| K6 | Working name Inkwell Kids; launch first choice Inkling pending trademark search in Phase 2, decision in Phase 3; "Jr." rejected. | app2-inkwell-kids/01 §7 | Founder |
| K7 | The band matrix (categories, letter pool, timer, hints, validation tier, scoring, input, lives, bots, session shape, reading support) is the configuration contract for `KidsRuleSet`. | app2-inkwell-kids/02 §2 | Firm |
| K8 | Silly categories ship in all bands; open-ended ones validate against the kid-safe general allow-list; phrase categories exist only in Explorers and Navigators and pass the local safety filter before display. | app2-inkwell-kids/02 §3 | Firm |
| K9 | Per-band weighted letter pools; minimum 8 kid-safe candidates per category per letter for Sprouts, 5 for Explorers, as content acceptance criteria. | app2-inkwell-kids/02 §4 | Firm |
| K10 | Timers off for Sprouts with the "sleepy sun" soft pacing cue; 90 s gentle for Explorers; 60 s for Navigators; timers never flash, redden or accelerate; the stop rule is off below Navigators. | app2-inkwell-kids/02 §5 | Firm |
| K11 | Hints (picture, first two letters, category example, letter sounds, "give me one") are free below Navigators and cost 2 of 10 points in Navigators; "give me one" is offered after 20 s of inactivity in Sprouts. | app2-inkwell-kids/02 §6 | Firm |
| K12 | Validation tiers 0 to 3 (intent, phonetic, near, exact) per band; the first letter is never forgiven; the correct spelling is always shown and the misspelling never echoed as correct; duplicate detection runs after correction; no point cost for near-misses in Explorers; Navigators confirm a near-miss at 8 of 10. | app2-inkwell-kids/02 §7, §15 | Firm |
| K13 | Celebrations under two seconds, never requiring dismissal; no red, buzzer or sad face in Sprouts; the first-ever valid answer gets the biggest celebration in the app. | app2-inkwell-kids/02 §8 | Firm |
| K14 | Pass-and-play and cooperative modes in v1; nearby play is a post-launch stretch; online play never exists in App 2. | app2-inkwell-kids/02 §9 | Firm |
| K15 | Progression: 26 letter creatures, a deterministic sticker book, 12 badges, personal bests for Navigators; no currency, streaks or timed rewards. | app2-inkwell-kids/02 §10 | Firm |
| K16 | Content-driven difficulty ramp; band changes only through the parent area, with suggestions shown to the parent only. | app2-inkwell-kids/02 §11 | Firm |
| K17 | Allow-lists per category per band (block-lists rejected for validity); two-reviewer human review for Sprouts and Explorers; phonetic collision audit in CI; "ask a grown-up" queue for unknown words; a boring, flat response to inappropriate input; the typed text is never stored. | app2-inkwell-kids/02 §12; app2-inkwell-kids/05 §14 | Firm |
| K18 | Accessibility: 60 pt minimum targets (72 pt Sprouts keys), tap-only core play, "friendlier letters" option including OpenDyslexic with honest copy; voice input is a Phase 2 spike. | app2-inkwell-kids/02 §13; app2-inkwell-kids/04 §5 | Firm |
| K19 | Classroom preset and big-letter mode in v1; nothing cloud-based. | app2-inkwell-kids/02 §14 | Firm |
| K20 | Reuse map: `IWCore`/`IWRules` and `IWContent` core shared unchanged and never forked; `IWPersistence` shared with a `KidProfile` schema; `IWDesignSystem` shares primitive tokens only; `IWMultiplayer` and `IWAnalytics` not linked; new packages `KidsDesignSystem`, `ParentalGate`, `KidsContent`, `KidsValidator`, optional `Speech`. | app2-inkwell-kids/03 §2 | Firm |
| K21 | One code mono-repo with both apps; a separate `inkwell-content` repository for both apps' word lists and assets, consumed as a versioned bundle. | app2-inkwell-kids/03 §3 | Firm |
| K22 | Content bundled in the app, never downloaded; vector illustrations for picture hints. | app2-inkwell-kids/03 §4 | Firm |
| K23 | Kids phases 0 to 4 over 12 to 16 calendar weeks and 18 to 24 engineer-weeks; Phase 1 exit (a six-year-old completes a round unaided) is the key gate; zero engine changes budgeted. | app2-inkwell-kids/03 §7 | Provisional |
| K24 | A "no escape" UI test from every kid screen and a gate robustness test (60 s of random taps, replay of a prior answer) are release gates. | app2-inkwell-kids/03 §6, §10 | Firm |
| K25 | Kid usability protocol: five children per band per round, three rounds, written parental consent and child assent, pseudonymous notes, recordings only with consent and deleted within 30 days. | app2-inkwell-kids/03 §9 | Firm |
| K26 | Direction C Bright Blocks as the system, with A-styled crayon-outlined characters (Pip and the letter creatures) and a D-disciplined Navigators skin; A survives as a post-launch theme skunkworks; B and D are not pursued for App 2. | app2-inkwell-kids/04 §3 | Founder |
| K27 | Kid motion rules (300 to 450 ms transitions, zero flashing, idle loops 3 s or slower, one thing moves at a time); no third-party animation runtime in v1. | app2-inkwell-kids/04 §4 | Firm |
| K28 | Touch target and layout numbers per band, enforced by a CI layout audit. | app2-inkwell-kids/04 §5 | Firm |
| K29 | Atkinson Hyperlegible as the default kid UI and tile face; Andika single-story forms evaluated as an alternate; OpenDyslexic opt-in; no serifs or italics on anything a child reads. | app2-inkwell-kids/04 §6 | Firm |
| K30 | The parent area uses App 1's adult design language; the settings list in Kids 04 §8 is the v1 scope. | app2-inkwell-kids/04 §8 | Firm |
| K31 | Default parental gate: spelled-out arithmetic with rotating problems and a spoken "ask a grown-up" prompt; optional device authentication for shared devices; the gate wraps the whole parent area, every link-out, mail sheet, review request and permission prompt; re-asked after five minutes; answers never stored; the `ParentalGate` package is the single implementation. | app2-inkwell-kids/04 §9; app2-inkwell-kids/05 §6 | Firm |
| K32 | The 30 microcopy strings and voice rules are the reference set; every new string is reviewed against them by KIDS. | app2-inkwell-kids/04 §11 | Firm |
| K33 | Compliance strategy: collect nothing, transmit nothing, make it verifiable with a network proxy; zero collection; network and dependency audits are release gates. | app2-inkwell-kids/05 §1, §2 | Firm |
| K34 | Guidelines 1.3 and 5.1.4 are hard requirements across the whole binary including the parent area; no advertising, no third-party analytics, no SDK with network behavior. | app2-inkwell-kids/05 §3, §4 | Firm |
| K35 | Age rating target 4+; the store band choice is deferred to Phase 3; Apple's Declared Age Range API is not used in v1. | app2-inkwell-kids/05 §5 | Firm |
| K36 | Data map as tabled; the device backup includes the container and the Trust page says so; no iCloud sync; no server; no accounts, Game Center or Sign in with Apple in any planned version. | app2-inkwell-kids/05 §7, §8, §17.1 | Firm |
| K37 | Kids monetization: paid up front, Family Sharing enabled, no in-app purchases in v1; free-with-unlock survives as a parallel pass for v2; a bundle with App 1 is a cross-sell on App 1's side only. | app2-inkwell-kids/05 §9 | Founder |
| K38 | Design to the UK Children's Code from v1; write the DPIA and GDPR notice before any UK or EU launch; legal review per territory. | app2-inkwell-kids/05 §10 | Firm |
| K39 | Privacy label "Data Not Collected" with release-time review; incident matrix with 24 to 48 hour targets for P0 and P1; the parent sees only a count of filtered words, never the text. | app2-inkwell-kids/05 §12, §13, §17.3 | Firm |
| K40 | "Suggest this word", if shipped, is a parent-initiated mail-compose sheet carrying the word only, never an app network call. | app2-inkwell-kids/05 §17.4 | Provisional |

### 3.7 Multilingual (App 3)

| # | Decision | Source | Confidence |
|---|---|---|---|
| M1 | App 3 is design-for-now, build-later; no engineering committed; it most likely ships as language packs inside App 1 (option B), with a separate app (A) decided after App 1 reaches 1.2 and a Kids bilingual mode (C) surviving as a feature once a pack exists. | app3-multilingual §5, §7 | Firm |
| M2 | "Letter" generalizes to a `Unit` supplied by a language pack through a `WritingSystem` protocol (draw pool, first unit, last unit, normalization, collation, layout direction); the engine never inspects a unit beyond equality. | app3-multilingual §3 | Firm (package home is OPEN H) |
| M3 | Prioritized language list: Spanish, German, French, Hindi, Japanese, Portuguese (Brazil), Korean, Arabic, Chinese (research only). | app3-multilingual §4 | Provisional |
| M4 | Phased story: Research (2 EW plus consultants), Spanish pilot (5 to 6 EW), Scale (17 to 20 EW over releases); each pack gets native-speaker QA. | app3-multilingual §6 | Provisional |

---

## 4. Consolidated OPEN register

"Close by" uses App 1 delivery phases unless marked Kids or App 3.

### 4.1 Product and scope

| # | Open question | Source | Owner | Close by |
|---|---|---|---|---|
| O1 | Exact Pro price ($4.99 versus $6.99) and whether to run an introductory price. | app1-inkwell/01 §11; master §9.2 | JOBS | Phase 5 (after TestFlight feedback) |
| O2 | Custom categories (user-typed) free or Pro; the house-rules paywall line. | app1-inkwell/01 §11; master §4.4 | JOBS with GAME | Phase 3 |
| O3 | "Any English word" Word Chain category free or Pro, and its download size. | app1-inkwell/02 §17; app1-inkwell/03 §20 | GAME with DATA | Phase 3 |
| O4 | Paper-companion mode (letter plus timer only) in 1.0 if under one engineer-week and behind the NPAT card. | app1-inkwell/01 §9; app1-inkwell/03 §13 | JOBS with IOS | Phase 5 (W19 skunkworks demo) |
| O5 | Whether cross-device sync (and therefore some form of account) is ever needed. | app1-inkwell/01 §12 | JOBS | Post-launch |
| O6 | Daily letter in 1.0 as the hook for result cards, or 1.1. | master §7.1, §9.2 | JOBS with GAME | Phase 3 |
| O7 | Game Center async versus iMessage turn cards as the primary async path for 1.2. | master §9.2 | ARCH with IOS | Phase 7 (1.2 planning) |
| O8 | Whether to pursue Apple editorial featuring at 1.0 or after 1.1. | master §9.2 | JOBS | Phase 6 |
| O9 | Android demand threshold that would turn the KMP skunkworks into a project; whether App 2 targets Android. | master §9.2; app1-inkwell/06 §10 | ARCH with JOBS | Post-launch |
| O10 | Whether App 1 gets a non-marketed "Family" preset (looser timers, simpler categories). | app2-inkwell-kids/01 §2, §8 | JOBS with KIDS | Phase 3 |
| O11 | Pre-order versus scheduled release for 1.0. | app1-inkwell/03 §20 | JOBS | Phase 5 (W20) |
| O12 | Whether the ratings prompt is shown at all in 1.0. | app1-inkwell/05 §19 | JOBS with QA | Phase 5 |
| O13 | Share card content: full ledger with names versus spoiler-free glyph grid (editor OPEN K). | master §7 idea 3; app1-inkwell/08 §3.6 | DESIGN with DATA | Phase 2 |
| O14 | Named bot personalities for App 1 in 1.0 or 1.1 (editor OPEN M). | master §7 idea 19; app1-inkwell/02 §11.4 | GAME with DESIGN | Phase 3 |

### 4.2 Game rules

| # | Open question | Source | Owner | Close by |
|---|---|---|---|---|
| O15 | Feed successful overturns of a dictionary REJECT back to DATA (silent, on-device aggregation only, opt-in). | app1-inkwell/02 §16, §17; master §3.6 | DATA with JOBS | Phase 3 |
| O16 | Designated-judge mode in App 1 v1 (classroom persona) or only in App 2. | app1-inkwell/02 §16, §17 | GAME with JOBS | Phase 3 (demo first) |
| O17 | Whether the "Stop!" rule is on by default for Blitz presets. | app1-inkwell/02 §17 | GAME | Phase 3 |
| O18 | Stop-rule grace in pass-and-play: per remaining player or immediate end. | app1-inkwell/08 §12 | GAME | Phase 2 |
| O19 | Backgrounding during a round: pause or forfeit, by mode (editor OPEN F). | app1-inkwell/08 §12; app1-inkwell/02 §12, §15; app1-inkwell/04 §4.1 | GAME | Phase 1 |
| O20 | A 2-second grace window for late submissions in nearby play to absorb drift. | app1-inkwell/04 §4, §22 | GAME with ARCH | Phase 5 (beta data) |
| O21 | Nearby host-loss behavior: pause-then-pass-and-play versus host migration (editor OPEN E). | app1-inkwell/02 §4.3; app1-inkwell/04 §8 | ARCH with GAME | Phase 1 (W6 spike) |
| O22 | Family-safe profile: reject profanity for scoring or only suppress it from suggestions and shares (editor OPEN G). | app1-inkwell/01 §3; app1-inkwell/02 §15; master §5.3 | DATA with GAME, JOBS | Phase 1 |
| O23 | Live letter-mismatch helper: ship in v1 or hold for a usability test. | app1-inkwell/08 §12 | DESIGN with GAME | Phase 2 |
| O24 | Final on-device dictionary size budget (12 versus 18 MB; bundle-only in 1.0) (editor OPEN L). | app1-inkwell/02 §17; app1-inkwell/04 §6.4 | DATA with ARCH | Phase 3 (W14 freeze) |
| O25 | Whether accepted async disputes feed the shared curation queue or only the local house dictionary. | master §3.6, §9.2 | DATA | Post-launch |

### 4.3 Platform and architecture

| # | Open question | Source | Owner | Close by |
|---|---|---|---|---|
| O26 | Analytics upload path: tiny first-party endpoint (breaks zero-infra) versus App Store Connect metrics only versus on-device aggregation with opt-in export. | app1-inkwell/03 §20; app1-inkwell/04 §14 | ARCH | Phase 2 (W10) |
| O27 | Nearby device cap for 1.0 (8 versus 4) pending the W6 spike. | app1-inkwell/03 §20 | ARCH with IOS | Phase 3 (W14 planning) |
| O28 | Whether the Metal ink shader ships in 1.0 (pending the W11 demo on the SE). | app1-inkwell/03 §20; app1-inkwell/09 §10 | IOS | Phase 3 (W11) |
| O29 | Whether the second engineer can commit to 100 percent in Phases 4 and 5; if not, the cut list is invoked at W14. | app1-inkwell/03 §20 | JOBS | Phase 3 (W14) |
| O30 | Wikidata (CC0) as the source for Movies and Brands; record in ADR-007. | app1-inkwell/04 §6.5, §22 | DATA | Phase 1 |
| O31 | Game Center sign-in friction and parental restrictions tolerance for async. | app1-inkwell/04 §7.1, §22 | ARCH with IOS | Phase 5 (beta) |
| O32 | iCloud sync of match history in 1.x and which persistence path. | app1-inkwell/04 §5.3, §22; master §5.8, §9.2 | ARCH | Post-launch |
| O33 | Sentry in production after the 30-day review. | app1-inkwell/04 §16, §22; app1-inkwell/05 §19 | QA with ARCH | Post-launch (30 days) |
| O34 | `IWFeatures` as one package with many products or many packages. | app1-inkwell/04 §2 | ARCH | Phase 1 |
| O35 | Where the `WritingSystem` protocol and Localization live: inside `IWCore`/`IWContent` or a tenth package (editor OPEN H). | app3-multilingual §3; master §5.1 | ARCH | Phase 0 |
| O36 | Amend 04's dependency diagram so InkwellKids does not consume `IWFeatures` (editor OPEN I). | app1-inkwell/04 §2; app2-inkwell-kids/03 §2 | ARCH | Phase 0 |
| O37 | Cold launch budget and baseline device: one number, one device (editor OPEN A, D). | app1-inkwell/01, 03, 04, 05, 09 | QA with IOS | Phase 0 |
| O38 | Rive adoption after the parallel pass; M01 implementation (SwiftUI trim versus Rive). | app1-inkwell/06 §10; app1-inkwell/09 §10 | DESIGN with IOS | Phase 2 (W8 bake-off) |
| O39 | iOS 18 zoom transition (M31) dual path or iOS 17 fallback only. | app1-inkwell/09 §10 | IOS | Phase 2 |

### 4.4 Design and motion

| # | Open question | Source | Owner | Close by |
|---|---|---|---|---|
| O40 | Night Lounge CRT scanline shader in v1 or later (GPU budget and photosensitivity review). | app1-inkwell/07 §9, §16; app1-inkwell/09 §10 | IOS with DESIGN | Phase 3 |
| O41 | Final licensed display face for Night Lounge versus the OFL fallback. | app1-inkwell/07 §16 | DESIGN | Phase 1 |
| O42 | Whether custom theme sounds ship with the theme or are a separate Pro feature (reconciled default: with the theme, per 09 §6). | app1-inkwell/07 §16; app1-inkwell/09 §6 | GAME with DESIGN | Phase 2 |
| O43 | Paper grain: shader versus static tile, pending battery numbers. | app1-inkwell/07 §16; app1-inkwell/09 §10 | IOS | Phase 2 (bake-off step 3) |
| O44 | Timer tick haptic default on or off (TestFlight survey). | app1-inkwell/09 §10 | GAME with QA | Phase 5 |
| O45 | Letter draw duration: 600 ms (09) versus 1.2 s scaled (01, master) (editor OPEN J). | app1-inkwell/09 §4; master §6.8 | DESIGN with JOBS | Phase 1 (W4 demo) |
| O46 | Whether the letter is announced to VoiceOver immediately or at the end of the draw for parity. | master §6.8, §9.2 | DESIGN with IOS | Phase 2 |
| O47 | Share image letter style: handwriting face for all themes or the theme's own letter. | app1-inkwell/08 §12 | DESIGN | Phase 2 |
| O48 | Theme scope versus schedule: Night Lounge in 1.0 at reduced scope or 1.1 (editor OPEN B). | app1-inkwell/03 §8; app1-inkwell/07 §8 | JOBS with DESIGN, ARCH | Phase 0 |

### 4.5 Quality and release

| # | Open question | Source | Owner | Close by |
|---|---|---|---|---|
| O49 | Beta program length versus the 24-week calendar (editor OPEN C). | app1-inkwell/03 §9; app1-inkwell/05 §5 | QA with ARCH, JOBS | Phase 2 (W10) |
| O50 | Final app name and keyword set after legal check. | app1-inkwell/05 §19; app1-inkwell/01 §8 | JOBS | Phase 0 (reserve), Phase 3 (final by W14) |
| O51 | Whether the age rating questionnaire computes 9+ or 13+ for peer-visible typed words; accept the result. | app1-inkwell/05 §19 | QA | Phase 5 |
| O52 | iPad large-canvas pass-and-play layout (Phase 7 bespoke pass). | app1-inkwell/05 §3; app1-inkwell/01 §6 | DESIGN | Phase 7 |

### 4.6 Kids edition

| # | Open question | Source | Owner | Close by |
|---|---|---|---|---|
| O53 | Which single Apple Kids Category band to select at submission (6 to 8 versus 9 to 11). | app2-inkwell-kids/01 §3, §8; app2-inkwell-kids/03 §11; app2-inkwell-kids/05 §5 | KIDS with JOBS | Kids Phase 3 |
| O54 | Trademark and App Store availability search for "Inkling". | app2-inkwell-kids/01 §7 | JOBS | Kids Phase 2 |
| O55 | Whether Navigators deserve a theme pack that removes Pip entirely. | app2-inkwell-kids/01 §8; app2-inkwell-kids/04 §12 | DESIGN with KIDS | Kids Phase 2 |
| O56 | Voice input spike (on-device recognition, microphone behind the gate) and its compliance review. | app2-inkwell-kids/02 §13; app2-inkwell-kids/03 §11; app2-inkwell-kids/05 §17.2 | IOS with KIDS | Kids Phase 2 |
| O57 | Retroactive scoring for parent-approved words within a session. | app2-inkwell-kids/02 §15, §16 | GAME | Kids Phase 2 |
| O58 | Whether the Family board of personal bests is visible to children. | app2-inkwell-kids/02 §15, §16 | KIDS | Kids Phase 2 |
| O59 | Whether a post-launch Classroom edition SKU is worth pursuing (FERPA, procurement). | app2-inkwell-kids/02 §14, §16 | JOBS with KIDS | Kids post-launch |
| O60 | Phonetic algorithm tuning for young children's spellings (Double Metaphone versus a custom grapheme-to-phoneme table). | app2-inkwell-kids/02 §16 | DATA | Kids Phase 2 |
| O61 | Whether an engine rule-set extension is needed for the wildcard letter. | app2-inkwell-kids/03 §11 | ARCH | Kids Phase 0 |
| O62 | Whether iPad is the primary screenshot device for the store page. | app2-inkwell-kids/03 §11 | DESIGN | Kids Phase 4 |
| O63 | Custom rounded display face versus an open-license face. | app2-inkwell-kids/04 §6, §12 | DESIGN | Kids Phase 2 |
| O64 | Alphabetical versus QWERTY default for the Sprouts keyboard. | app2-inkwell-kids/04 §12 | KIDS with DESIGN | Kids Phase 2 (test both) |
| O65 | Illustration format for picture hints (vector preferred; confirm quality). | app2-inkwell-kids/04 §12; app2-inkwell-kids/03 §4 | DESIGN | Kids Phase 2 |
| O66 | "Suggest this word" inclusion in v1 (mail-compose only). | app2-inkwell-kids/05 §2, §17.4 | DATA with KIDS | Kids Phase 3 |
| O67 | Exact 2025 COPPA Rule text review with counsel (effective and compliance dates). | app2-inkwell-kids/05 §2, §17.6 | KIDS | Kids Phase 3 |
| O68 | Whether to pursue a COPPA Safe Harbor certification for the Trust page. | app2-inkwell-kids/05 §17.6 | KIDS with JOBS | Kids post-launch |
| O69 | Which single Kids band ships first if the Kids schedule compresses. | master §9.2 | JOBS with KIDS | Kids Phase 0 |

### 4.7 Multilingual

| # | Open question | Source | Owner | Close by |
|---|---|---|---|---|
| O70 | Separate app versus in-app language packs (design for packs now; decide after App 1 reaches 1.2). | app3-multilingual §7 | JOBS with ARCH | App 1 at 1.2 |
| O71 | First pilot language: Spanish (market size) or German (clean rules, classroom demand). | app3-multilingual §7 | DATA with JOBS | App 3 Phase A |
| O72 | Whether the Kids bilingual mode (option C) deserves its own short plan once a pack exists. | app3-multilingual §7 | KIDS | After App 3 Phase B |

---

## 5. Founder decisions needed before Phase 0

These are the calls only the founder can make. Each carries the team's one-line recommendation. Everything else in Section 4 has a persona owner and a phase.

| # | Decision | Team recommendation |
|---|---|---|
| F1 | App 1 name | Keep Inkwell; send it to a trademark attorney in week 1 and reserve the App Store record; if it fails, Nib, then Letterhead, then Foolscap. Do not pick for search volume; buy search with the subtitle. |
| F2 | App 1 business model | Free plus one-time Pro via StoreKit 2, host pays, no ads, no subscription, no consumables. The free tier must be a complete, proud product. |
| F3 | Pro price point and introductory pricing | $6.99 with a $4.99 launch price for four weeks; confirm after Phase 5 TestFlight feedback. |
| F4 | iOS minimum | iOS 17.0 for 1.0; re-evaluate at 1.1 with real usage data; never adopt an API because it is new. |
| F5 | Default visual direction | Paper & Ink as the identity, confirmed on a device at the W4 demo against Night Lounge; Swiss Editorial free, Night Lounge in Pro, Playful Pop parked, Quiet Minimal as the skeleton. |
| F6 | Theme scope for 1.0 versus the schedule | Paper & Ink and Swiss Editorial in 1.0; Night Lounge either reduced to tokens and sound (no shader, no animated glass) or moved to 1.1 as the first Pro content drop. The 44 EW plan cannot absorb 07's full theme estimates. |
| F7 | Online multiplayer in v1 at all | Yes to async over Game Center in Phase 5 behind Pro, Word Chain first; it is pre-approved as the first cut if Phase 5 slips. No real-time online in v1 under any circumstances. |
| F8 | Nearby multiplayer in v1 | Yes in Phase 4 behind Pro, contingent on the W5 to W6 spike; accept a four-device cap rather than slip. |
| F9 | Kids app name | Inkling if the trademark search is clean, with "Kids" in the subtitle; otherwise Inkwell Kids. Never "Jr.". |
| F10 | Kids app pricing | Paid up front, Family Sharing on, no in-app purchases in v1. "There is nothing to buy in this app" is the review story and the parent story. |
| F11 | Date versus scope | Fixed W23 submission with a non-negotiable quality bar; scope flexes through the ordered cut list; every date move pairs with a cut and is announced on a Friday. |
| F12 | Second engineer commitment | Commit the second engineer to 100 percent in Phases 4 and 5, or accept today that nearby or async will be cut; the plan has zero slack otherwise. |

---

## 6. Closing team round-table

> **[JOBS]** Seventeen documents and about a hundred decisions, and the product still fits in one sentence: two paper games, zero friction, scoring that is a show. I am proud of that. I am also on record disagreeing with two of my own colleagues. I think DESIGN's three-theme plan is one theme too many for a 44-engineer-week schedule with no slack, and I will cut Night Lounge to 1.1 before I cut a frame of the reveal. And I still think the ratings prompt should not exist in 1.0; QA will win that argument with data and I will lose it gracefully, but not before launch.

> **[ARCH]** The plan is sound because one idea holds it up: a pure, deterministic engine with an event log as the only truth. Everything that looked like a contradiction between documents, the SwiftData debate, the host-migration question, the validation policy, turned out to be a detail that the engine design does not care about. My honest disagreement is with the delivery plan's capacity math. Forty-four engineer-weeks of work against forty-four of capacity is not a plan with buffer inside two phases, it is a plan that will invoke the cut list, and I would rather we say so now and pre-cut NPAT async than discover it at W19.

> **[DESIGN]** The thesis survived the editing pass intact: paper and ink, one hero per screen, themes that change clothes and never bones. I accept that Night Lounge may slip to 1.1, and I will say plainly that I disagree with JOBS about why. The Pro theme is not decoration; it is the reason the Pro screen is beautiful instead of a feature list. If it slips, Pro launches selling plumbing. My other open worry is the letter draw: 600 milliseconds in my catalog, 1.2 seconds in the brief. We settle it on a phone at W4, not in a register.

> **[GAME]** The rules are now in one place and every other document defers to the spec, which is how it should be. I lost two arguments I still believe in: the "Any English word" category deserves to be free because it is the purest Word Chain, and bots deserve names in 1.0 because a table needs faces. I won the ones that mattered: the hybrid validation that keeps the online game the same game, the duplicate collision that makes the room laugh, and a Kids edition where a six-year-old is never told she is wrong. On Kids I will keep arguing for timer tension in Explorers; the sleepy sun is right for Sprouts and I suspect it is a year too young for an eight-year-old.

> **[KIDS]** The Kids plan is the one I would defend in front of a regulator and a parent on the same afternoon, because it collects nothing and says so. Three bands with real names, allow-lists instead of block-lists, a boring response to a rude word, and a Trust page that invites an audit. My remaining disagreement is with JOBS about Playful Pop in App 1: parking it is right, but keeping the Figma file alive is a temptation, and the day App 1 ships a sticker theme is the day our two apps start to blur. I would delete the file.

> **[QA]** Every gate is now a number and every number has an owner, which is the only way "perfect" becomes a release criterion. I have two unresolved fights. First, five cold-launch budgets across five documents is five too many, and I want one number on one device before anyone writes a performance test. Second, my eleven-week beta does not fit the four-week Phase 5, and the editor is right to call it out; I will take two betas two weeks apart as the floor, but if the second beta shows a crash cluster, the date moves and I will say so on a Friday.

> **[DATA]** The dictionary story is honest now: public-domain, MIT-like, WordNet and CC BY data only, Wiktionary out of v1, names never rejected, three visible states instead of a verdict. I still carry one unresolved question that is really a product question: does the family-safe profile refuse to score "ass" as an animal, or just refuse to suggest it? The brief says one thing and the spec says another, and both are mine. I lean toward the spec, score it and never promote it, because a dictionary that lies about a real word is a worse dictionary. I expect JOBS to disagree, and I would like that fight before dictionary v0, not after a review.

> **[IOS]** The stack is right: SwiftUI first, iOS 17, Swift 6 strict from day one, GRDB, no third-party SDK in production, maybe no animation runtime at all. What worries me is not the architecture, it is the two places where we are betting on frameworks that are famous for betraying small teams: MultipeerConnectivity in a crowded room and SwiftUI keyboard focus on iOS 17. The spike and the UIKit escape hatch are in the plan, and I want both treated as insurance we expect to use, not as skunkworks we hope to skip. If the W6 spike is ugly, nearby goes to Phase 5 and async goes to 1.1, and I would rather we all agree to that sentence today.
