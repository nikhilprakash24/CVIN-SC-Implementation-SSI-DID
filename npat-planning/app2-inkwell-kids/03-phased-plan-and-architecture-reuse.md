# App 2 "Inkwell Kids": Phased Plan and Architecture Reuse

**Read this if...** you are the engineer or architect who will build App 2 after App 1 ships, and you need to know exactly which App 1 packages are reused unchanged, which are forked, which are new, how the repository is organized, how the phases run from Phase 0 to launch in roughly 12 to 16 weeks, what each phase demos, what the risks are, how we test with real children, and what the go/no-go checklist is before we submit to the Kids Category.

**Document status:** Draft v0.1, 2026-10-04, owner **[ARCH — Principal Architect, "Priya Raman"]** with **[QA — Quality & Release Lead, "Lena Fischer"]**.

---

## Table of contents

1. Assumptions inherited from App 1
2. Reuse map: shared, forked, new
3. Repository decision: mono-repo or multi-repo
4. Shared content pipeline
5. Analytics, telemetry and crash reporting
6. Build and release differences
7. Phased plan (Phase 0 to launch)
8. Risk register
9. Test strategy additions, including kid usability testing
10. Go/no-go checklist for Kids Category submission
11. Decisions and open questions
12. Sources

---

## 1. Assumptions inherited from App 1

- App 1 ships first, iOS 17+ minimum, SwiftUI-first, Swift 6 strict concurrency, Xcode 16+.
- App 1 is organized as Swift packages: `GameEngine` (deterministic NPAT and Word Chain state machines, scoring, timers as injected event sources), `Dictionary` (word lists, validation, fuzzy matching), `DesignSystem` (tokens, components, motion), `Networking` (Game Center, nearby, any backend client), `Persistence` (local store, profiles, history), plus the app target. Naming note: this document keeps the brief's short names; App 1's architecture document (04) names them `IWCore` plus `IWRules` (GameEngine), `IWContent` (Dictionary), `IWDesignSystem`, `IWMultiplayer` (Networking), `IWPersistence`, `IWAnalytics`, `IWFeatureFlags` and `IWFeatures`. Read every short name below as its `IW` counterpart.
- App 1 has at least 90 percent unit coverage on `GameEngine` (the App 1 definition of done; its test pyramid targets 95 percent) and a snapshot-test suite on `DesignSystem` components.
- The team is one to two engineers plus the design director and part-time specialists.

> **[ARCH]** If App 1 does not actually land with the engine as a standalone package with injected timers and injected dictionaries, App 2's plan collapses into a fork. The App 1 architecture docs must treat "GameEngine has zero UI and zero dictionary dependencies" as a hard acceptance criterion, partly because of this document.

> **[QA]** I will add a check to the App 1 release train: "GameEngine builds and passes tests on Linux via `swift test`". If it does, it has no UIKit or SwiftUI leaks.

---

## 2. Reuse map: shared, forked, new

| Package | Status for App 2 | What changes | Owner | Risk |
|---|---|---|---|---|
| `GameEngine` | Shared unchanged | None. App 2 passes a `KidsRuleSet` (letter pool, weights, categories, timer mode, lives, scoring style) through the existing rule-set protocol. Any gap found becomes an App 1 change, never a kids fork | ARCH | Low if App 1 keeps the engine pure |
| `Dictionary` (core: matching, lemmatization, Levenshtein, phonetic keys) | Shared unchanged | None. Phonetic matcher and edit distance already exist for App 1's fuzzy "did you mean"; App 2 raises the tolerance via configuration | DATA | Low |
| `Dictionary` (data: App 1 word lists) | Not used by App 2 | App 2 never loads adult lists | DATA | None |
| `Persistence` | Shared, with a kids profile schema added | Adds `KidProfile` (nickname, avatar, band, stickers, creatures, word history, approved words). No iCloud sync for kid profiles | ARCH | Low |
| `DesignSystem` | Forked into `KidsDesignSystem` | Shares only primitive tokens (spacing scale, radius scale, motion curve names, haptic names). Everything visible is new: type scale, palette, components, illustrations, motion tempo | DESIGN, IOS | Medium: temptation to share more than tokens |
| `Networking` | Not linked | App 2 has no network layer in v1. Nearby play (post-launch) would link a `Nearby` module only | ARCH | None |
| `Analytics` (App 1's first-party `IWAnalytics`, local counters only) | Not linked | App 2 uses no analytics SDK; `IWAnalytics` also has a compile-time `KidsMode` that removes its network sink, as a second guard | ARCH | None |
| `KidsDesignSystem` | New | Kid tokens, components (letter tiles, big keyboard, category cards, creature views, sticker book), motion presets, sound set | DESIGN, IOS | Medium |
| `ParentalGate` | New | Gate patterns (arithmetic, hold-to-confirm, year-of-birth-style adult knowledge), gate policy, gated navigation wrapper, Ask-to-Buy awareness | IOS, KIDS | Low: small, must be exhaustive in tests |
| `KidsContent` | New | Allow-lists per band and category, picture-hint manifests, sensitive list, license manifest, versioning | DATA, KIDS | Medium: volume of curation |
| `KidsValidator` | New, thin | Tolerance tiers over `Dictionary` core; collision-audit tooling | DATA | Low |
| `Speech` (optional) | New, Phase 2 spike | On-device text-to-speech for auto-read; on-device speech recognition for voice hint if approved | IOS | Medium |
| App target `InkwellKids` | New | Composition root, kid flows, parent area | IOS | |

Illustrative package graph:

```
InkwellKids (app)
├── KidsDesignSystem ──► DesignSystemTokens (shared primitives only)
├── ParentalGate
├── KidsContent
├── KidsValidator ──► Dictionary (core)
├── GameEngine (shared, unchanged)
└── Persistence (shared, + KidProfile)
```

> **[DESIGN]** I argued to share more of DesignSystem than tokens, because the component architecture (a tile is a tile) is good. **[IOS]** convinced me otherwise: a kid tile has different touch target, different type, different motion and a creature slot. Sharing the Swift type means `if kids` branches in App 1 forever. Tokens only.

> **[ARCH]** The one place I expect pressure to fork is GameEngine, around "unlimited lives" and "wildcard letter" in kid Word Chain. Both are expressible as rule-set parameters. If a future kid rule cannot be expressed, we extend the rule-set protocol in App 1 and App 1 simply does not use the new parameter.

**DECISION:** Reuse map as tabled. GameEngine and Dictionary core are never forked. DesignSystem shares tokens only.

---

## 3. Repository decision: mono-repo or multi-repo

| Option | Pros | Cons | Fit for a 1 to 2 engineer team |
|---|---|---|---|
| A. Mono-repo: one repository, one Xcode workspace, both app targets, all packages as local packages | Atomic changes across engine and both apps; one CI; one PR touches engine plus both callers; simplest for two people | Build times grow; a kids-only contributor sees adult content; one repo with two release cadences | Best |
| B. Multi-repo: shared packages in their own repos, consumed by version tag | Clean version boundaries; content curators work in `KidsContent` without the app | Version-bump churn for every engine fix; two people spend time on plumbing | Poor at this team size |
| C. Mono-repo for code, separate repo for `KidsContent` | Code benefits of A; content curation (which involves non-engineers and large data files) isolated with its own review rules | Two repos to keep in sync; content versions pinned in the app | Good |

> **[ARCH]** A is right for code. The content question is real: the Sprouts Thing list will have thousands of rows, reviewers who are not engineers, and a review rule (two reviewers, one from KIDS) that is different from code review. Git LFS for illustration assets also argues for separation.

> **[QA]** CI cost in A is manageable: path filters so engine changes run both app test suites and kids-content changes run only content validation.

> **[DATA]** I prefer C. Content gets its own CODEOWNERS, its own validation CI (schema, collision audit, license manifest), and I can give a reviewer access to the content repo without the code.

**DECISION:** Option C. One code mono-repo with both apps and all packages; a separate `inkwell-content` repository holding both App 1 and App 2 word lists and assets, consumed as a versioned resource bundle. Option B does not survive as a parallel pass.

---

## 4. Shared content pipeline

The content pipeline is shared with App 1 (same scripts, same formats) but App 2 adds stages.

| Stage | App 1 | App 2 additions |
|---|---|---|
| Seed | Pull from ENABLE, SCOWL, WordNet, GeoNames and curated category lists (Wiktionary excluded from v1 per App 1's ADR-007) | Pull from age-graded lists (Dolch, Fry), children's dictionaries, name registries |
| Normalize | Lowercase, strip diacritics to a folded key, lemmatize | Same |
| Filter | Profanity list removes slurs | Conservative sensitive list (broader), plus band assignment per word |
| Review | Spot checks | Mandatory two-reviewer sign-off per word for Sprouts and Explorers; tracked in the content repo via PR review requirements |
| Audit | Duplicates, encoding | Phonetic collision audit against the sensitive list; minimum-candidates-per-letter check per category per band; picture hint coverage |
| Package | Compressed binary tries per category | Per band per category; plus a hint manifest and a license manifest |
| Version | Semantic version per release | Same, plus a content changelog surfaced in the parent area's About screen |

Content is bundled in the app, never downloaded. Content updates ship as app updates. This is a deliberate simplification: no network means no content delivery network, no cache, no update prompts for children.

> **[DATA]** Bundle size estimate for App 2 content: around 6 to 10 MB for all lists in all bands as compressed tries, plus illustration assets for picture hints, which dominate. Picture hints for 400 Sprouts animals at 2 sizes could be 20 to 40 MB if raster. Vector (SVG converted to PDF or Symbol assets) keeps it under 10 MB. Doc 04 decides illustration format.

**DECISION:** Content bundled in the app. Vector illustrations preferred for hints to control bundle size.

---

## 5. Analytics, telemetry and crash reporting

| Concern | App 1 | App 2 |
|---|---|---|
| Third-party analytics SDK | None in v1 (App 1 ADR-012: first-party local counters only, label "Data Not Collected") | None. Guideline 1.3 forbids in nearly all cases, and we do not want the "limited cases" exception |
| Crash reporting | Apple (MetricKit and Xcode Organizer) in production; Sentry in TestFlight builds only (App 1 ADR-011) | Apple's crash reports via Xcode Organizer only, which depend on the user's opt-in to share analytics with developers; no SDK, not even in TestFlight |
| Product metrics | Local aggregate counters, nothing leaves the device by default | None transmitted. On-device counters shown to the parent (rounds played, words learned, hints used). Nothing leaves the device |
| App Store analytics | Apple App Store Connect aggregate | Same; this is Apple's data, not collected by us |
| Privacy manifest | Required | Required; App 2's `PrivacyInfo.xcprivacy` declares no tracking, no tracking domains, and lists required-reason API usage (file timestamps, user defaults) with the standard reasons (https://developer.apple.com/documentation/bundleresources/privacy-manifest-files.md) |
| App Privacy label | Per App 1's actual collection | "Data Not Collected" is the goal; see doc 05 for the exact plan |

> **[ARCH]** Zero analytics is not a compromise; it is the simplest architecture. No SDK, no consent flow, no retention policy for telemetry, no privacy-label complications. We trade product insight for trust and we get it back through playtests.

> **[JOBS]** We will miss the dashboards for about a week. Then we will go sit with kids, which is what we should have been doing anyway.

**DECISION:** No analytics SDK, no telemetry. Apple opt-in crash reports only.

---

## 6. Build and release differences

| Item | App 1 | App 2 |
|---|---|---|
| Bundle identifier | `com.<org>.inkwell` | `com.<org>.inkwellkids` |
| App Store category | Games, Word | Kids Category, with one age band selected (5 and under, 6 to 8, or 9 to 11) and secondary category Games |
| Age rating | Per questionnaire, likely 4+ | 4+ required; the App Store Connect questionnaire was revised in 2025 with new 13+, 16+, 18+ tiers and more questions; we answer no to all content flags, no to unrestricted web access, no to user-generated content shared with others |
| Entitlements | Game Center, iCloud possibly, network | None beyond the defaults. No Game Center, no iCloud, no push, no network |
| Info.plist usage strings | Several | Only what we use; microphone string only if voice hint ships, and only behind the gate |
| Review notes | Standard | Explain the parental gate, state "no third-party analytics or advertising; no data collected; no network access", point to the Trust page |
| Release cadence | Minor release every 4 weeks (App 1 quality plan, 05 Section 10) | Every 4 to 6 weeks; content-heavy; longer soak in TestFlight with family testers |
| TestFlight | Internal plus external | External testers are parents, who test with their children; the TestFlight build contains the same gate |
| Localization | English first, more later | English first; Spanish second because content lists are the expensive part |
| Device matrix | iPhone and iPad, iOS 17+ | iPhone and iPad, iOS 17+, with iPad treated as primary for Sprouts (landscape, both hands) and iPhone SE as the small-screen floor |

> **[IOS]** Two practical review realities. First, the reviewer will try to find any path from a kid screen to a purchase or link without a gate; we build an automated UI test that walks every reachable screen from the kid home and asserts no gate and no external URL. Second, reviewers test the gate itself; it must not be defeatable by random tapping, so the arithmetic gate must change every time and the hold gate must require a real sustained press.

> **[QA]** The review-notes field will also carry a one-paragraph description of how the gate works, because reviewers have rejected kids apps when they did not find the gate.

**DECISION:** As tabled. An automated "no escape" UI test is a release gate.

---

## 7. Phased plan (Phase 0 to launch)

Team assumption: one full-time engineer, one half-time engineer, design director roughly one third time, KIDS specialist roughly one quarter time, DATA roughly one third time during Phases 1 to 3. Estimates are engineer-weeks (ew) for the engineers only. Total 12 to 16 calendar weeks after App 1 ships, 18 to 24 engineer-weeks.

### Phase 0: Foundations and compliance scaffolding (Weeks 1 to 2; 3 ew)

Entry: App 1 shipped; GameEngine and Dictionary core pass tests on Linux; this document and doc 05 approved.
Work: new app target in the mono-repo; `KidsDesignSystem` tokens package; `ParentalGate` package with two gate patterns and full unit tests; privacy manifest; App Store Connect record created in the Kids Category (unreleased); content repo scaffolding with schema validation CI; `KidsRuleSet` for all three bands wired into GameEngine with engine tests proving unlimited lives and wildcard letter behave.
Exit: a bare app launches, shows a placeholder kid home, and a gated parent area; `swift test` green on all packages; the no-escape UI test skeleton runs.
Demo: Theo taps the parent area, fails the gate twice, passes once.

### Phase 1: Sprouts NPAT playable, ugly (Weeks 3 to 5; 5 ew)

Entry: Phase 0 exit.
Work: Sprouts NPAT loop end to end with the sleepy sun, custom big keyboard, tier 3 validation against a seed Animal and Food list (200 words each), auto-read via on-device speech synthesis, celebration placeholder, one bot (Pip) with placeholder art, pass-and-play for two profiles. Content: Sprouts Animal and Food lists curated to 400 and 300.
Exit: a 6-year-old in a moderated session completes a round without adult help; validation accepts "elefant" and shows "elephant"; the first-answer celebration exists.
Demo: a round played live on an iPad with the design director's child or a recruited family.

### Phase 2: All bands, Word Chain, design direction locked (Weeks 5 to 8; 5 ew)

Entry: Phase 1 exit; doc 04 design direction chosen.
Work: Explorers and Navigators NPAT; Word Chain for all bands with lives and wildcard rules; hint system complete; sticker book and letter creatures (data model and basic UI); bots Wren and Rook; parent area with settings parents want (band, timers, sounds, friendlier letters, profiles, data view, delete); design direction components begin replacing placeholders. Spikes: voice hint feasibility (1 ew, time-boxed), vector illustration pipeline. Content: Explorers lists for 4 classic categories, Sprouts Thing list to 1500.
Exit: all three bands playable in both games; design system components for tiles, keyboard, cards and creature slots shipped; second kid playtest round completed with at least 4 children per band.
Demo: pass-and-play Word Chain between a Sprout and an Explorer on one phone.

### Phase 3: Polish, content completion, compliance hardening (Weeks 8 to 11; 4 ew)

Entry: Phase 2 exit.
Work: motion and sound to spec; Reduce Motion alternatives; VoiceOver and Switch Control pass; Dynamic Type to the largest size; all celebrations under two seconds; classroom preset and big-letter mode; Trust page and privacy policy content integrated into the parent area; App Privacy label drafted; no-escape UI test covers all screens; phonetic collision audit green; naming decision (Inkling vs Inkwell Kids) and icon. Content: Navigators lists, Names and Places lists, silly categories mapped.
Exit: zero P1 bugs; accessibility audit complete; content acceptance criteria (minimum candidates per letter) met for all bands; third playtest round done with parents interviewed; go/no-go checklist items in section 10 all green except submission items.
Demo: the full first-run experience from install to first sticker, timed, on an iPhone SE and an iPad.

### Phase 4: Beta, submission and launch (Weeks 11 to 14, up to 16; 2 to 3 ew)

Entry: Phase 3 exit.
Work: external TestFlight with 15 to 25 families for two weeks; fix list; App Store assets (screenshots that meet 2.3.8, a preview video with no implied features); submit to the Kids Category; respond to review; launch; post-launch watch on crash reports and parent emails.
Exit: approved in the Kids Category; released; one week with crash-free sessions above 99.8 percent (from Apple's opt-in reports); no Kids Category guideline issues raised.
Demo: the App Store page, live.

### Post-launch stretch (not in the 16 weeks)

Nearby play via MultipeerConnectivity (3 ew), Spanish content (DATA-heavy), voice hint if the spike was positive and compliance signs off (3 ew), Classroom edition evaluation.

> **[JOBS]** Phase 1 exit is the only exit I care about. If a six-year-old does not finish a round smiling, nothing after it matters. I want that demo in week 5 with a real child, not a slide of a child.

> **[QA]** Phase 3 is where kids apps usually slip, because content curation and accessibility are both long tails. I have padded it and still want a weekly burn-down on the content acceptance criteria.

> **[ARCH]** The estimate assumes no GameEngine changes. Every engine change is an App 1 change with its own review, and I have budgeted zero. If we discover the engine needs a change in Phase 1, Phase 2 slips one week.

---

## 8. Risk register

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| 1 | GameEngine from App 1 has hidden UI or dictionary coupling | Medium | High: forces a fork | Linux `swift test` gate in App 1; rule-set protocol review before App 1 ships | ARCH |
| 2 | Content curation volume exceeds DATA capacity | High | Medium: slips Phase 3 | Start Sprouts lists in Phase 0; size Thing lists down for v1; silly categories fall back to Thing | DATA |
| 3 | Phonetic tolerance accepts something inappropriate or wrong | Medium | High: trust | Collision audit in CI; allow-list only validity; first-letter constraint | DATA |
| 4 | App Review rejects on parental gate or perceived data collection | Medium | High: launch delay | No-escape UI test; review notes; zero network; privacy label "Data Not Collected" | IOS, QA |
| 5 | Illustration workload for picture hints is larger than planned | High | Medium | Vector pipeline; prioritize Sprouts Animal and Food; mark others no-hint | DESIGN |
| 6 | Kid playtest recruitment slow or consent process delays | Medium | Medium | Recruit through TestFlight parent pool and local schools early; consent forms ready in Phase 0 | KIDS, QA |
| 7 | Navigators band feels babyish and is rejected by 11 to 13s | Medium | Medium | Separate theme treatment in doc 04; test with that band specifically | DESIGN, KIDS |
| 8 | Speech synthesis voice quality for auto-read sounds robotic | Medium | Low | Use the highest quality on-device voices; allow parent to pick; fall back to text | IOS |
| 9 | Bundle size grows past 100 MB with illustrations | Low | Low | Vector assets; asset catalog thinning | IOS |
| 10 | Two release trains overload a two-person team | Medium | Medium | Slower kids cadence; shared CI; shared engine fixes land once | QA |
| 11 | Regulatory change (COPPA 2025 amendments effective, state laws, UK code) alters requirements | Medium | Medium | Zero-collection architecture is robust to most changes; legal review before international launch | KIDS |
| 12 | Trademark conflict on chosen name | Medium | Low | Search in Phase 2; fallback name ready | JOBS |

---

## 9. Test strategy additions, including kid usability testing

### 9.1 Automated

- Engine: App 1's suite plus kid rule-set tests (unlimited lives, wildcard letter, soft timer never ends a round, stop rule disabled, scoring styles).
- Validator: golden tests of common invented spellings per band (a corpus of at least 300 kid misspellings collected from playtests and literature), false-positive tests against the sensitive list, uniqueness tests.
- Content CI: schema, license manifest, minimum candidates per letter per category per band, collision audit, hint coverage.
- UI: no-escape test from every kid screen; gate robustness test (random taps for 60 seconds never pass); Dynamic Type snapshots at 5 sizes; Reduce Motion snapshots; VoiceOver label audit via accessibility inspector automation.
- Performance: cold launch under 800 ms p90 on iPhone SE 3rd gen and under 1.5 seconds on iPhone SE 2nd gen (App 1's reconciled budget, 05 Section 4); celebration frame rate 60 fps on iPad 9th generation.

### 9.2 Kid usability testing protocol

Grounding: NN/g's "Usability Testing with Minors: 16 Tips" (Kendrick, 2019, https://www.nngroup.com/articles/usability-testing-minors/) and "Children's UX" (Sherwin and Nielsen, 2019, https://www.nngroup.com/articles/childrens-websites-usability-issues/). Key points we adopt: obtain signed parental consent before testing; recruit extra participants because no-shows and interruptions are higher with children; segment by maturity, not just age; keep sessions no longer than 60 to 90 minutes with breaks (we will run far shorter); use friendship pairs for ages 6 to 8 and individual sessions for younger and older children; prepare age-appropriate tasks and avoid being authoritative; expect parents and siblings to attend and offer them a place to wait or sit quietly.

| Item | Our protocol |
|---|---|
| Consent | Written parental consent plus child verbal assent explained in child language ("You can stop any time and nobody will be upset"). No recording of faces by default; audio or screen recording only with explicit consent, deleted after analysis within 30 days. Forms reviewed by KIDS and stored off the product systems. |
| Children per band per round | 5 per band per round (15 per round), recruited 7 to allow for no-shows. Three rounds (Phases 1, 2, 3) means roughly 45 child sessions. NN/g's small-sample logic applies: five users per segment surface most issues; we are segmenting three ways. |
| Session length | Sprouts 20 minutes, Explorers 30, Navigators 40, including warm-up and a break. |
| Format | Sprouts: individual with parent in the room; Explorers: friendship pairs; Navigators: individual, parent outside if the child prefers. |
| Facilitator stance | Child is the expert ("you are helping us make this better"); no hints from the facilitator for the first 20 seconds of any stuck moment, so we see what the app does. |
| Tasks (Sprouts) | "Can you play one round?"; "Can you find your sticker?"; "Pretend your sister wants a turn. What do you do?" |
| Tasks (Explorers) | "Play two rounds with your friend on one phone"; "Try to beat Wren at Word Chain"; "Find a silly category." |
| Tasks (Navigators) | "Play a timed round and tell us what felt slow"; "Is there anything here that feels like it is for little kids?"; "Try to make a custom category." |
| Measures | Task completion without adult help; time to first valid answer; stuck moments and what resolved them; laughs; requests to play again; any frustration or distress (session stops immediately). |
| Incentives | Age-appropriate (a small toy or book voucher), given regardless of performance. |
| Parent interview | 10 minutes after each session: understanding of what the app stores; reaction to the parent area; would they recommend; what they would pay. |
| Location | Family homes or a quiet room at a partner school; never a lab for Sprouts. |
| Data handling | Notes only, pseudonymous ("Sprout 3"); no names in any product system. |

> **[KIDS]** Five per band per round is the floor, not a target. If Sprouts shows disagreement among the five, we add three more before changing the design.

> **[QA]** Playtest findings are logged as issues tagged by band and principle (doc 01's numbered principles) so we can see which principle is failing most.

### 9.3 Playtest scripts (excerpt, Sprouts, Phase 1)

1. Warm-up (3 min): "What is your favorite animal? Can you spell it for me on paper?" (gives us a baseline of spelling stage).
2. First launch (parent does setup while the child watches; we observe whether the child understands "this part is for grown-ups").
3. "It is your turn now. Can you play?" Observe: does the child understand the letter cue; does the child find the keyboard; what happens at the first stuck moment; reaction to the correction animation.
4. Sticker: "Did you get anything?" Observe whether the sticker book is found and whether it is satisfying.
5. Pass-and-play prompt as above.
6. Close: "Would you want to play this again? What would you call the little inkblot?" (also feeds naming of Pip).

---

## 10. Go/no-go checklist for Kids Category submission

All items must be green before Phase 4 submission.

**Product**
- [ ] Sprouts round completed unaided by at least 4 of 5 children in the final playtest.
- [ ] Every celebration under 2 seconds; no celebration requires dismissal.
- [ ] No red, buzzer or sad-face failure states in Sprouts (audit signed by DESIGN and KIDS).
- [ ] Content acceptance criteria met: minimum 8 candidates per letter per category for Sprouts, 5 for Explorers; collision audit green; license manifest complete.

**Compliance (Kids Category, guideline 1.3 and 5.1.4; https://developer.apple.com/app-store/review/guidelines/ and https://developer.apple.com/app-store/kids-apps/)**
- [ ] No link-outs, purchase opportunities or other distractions reachable from kid screens; all such are behind the parental gate (no-escape UI test green).
- [ ] Parental gate cannot be passed by random tapping (gate robustness test green).
- [ ] No third-party analytics or advertising SDKs in the binary (dependency audit lists every linked framework).
- [ ] No personally identifiable or device information sent to any third party (network audit: the app makes zero outbound connections; verified with a proxy on the device).
- [ ] Privacy policy URL set in App Store Connect and reachable from the parent area.
- [ ] App Privacy label completed and consistent with the network audit.
- [ ] Privacy manifest present and complete.
- [ ] Age rating questionnaire answered honestly; result 4+.
- [ ] Kids Category age band selected; metadata uses "Kids" only as permitted by 2.3.8; screenshots are 4+ appropriate.
- [ ] Review notes describe the gate and the zero-collection design.
- [ ] COPPA checklist from doc 05 complete and signed by KIDS.

**Quality**
- [ ] Zero P1 bugs; fewer than 5 P2.
- [ ] Crash-free sessions above 99.8 percent across the two-week TestFlight.
- [ ] Accessibility audit: VoiceOver, Dynamic Type, Reduce Motion, Switch Control, color contrast all pass.
- [ ] Device matrix: iPhone SE (3rd gen), iPhone 15 or 16, iPad 9th gen, iPad Air, on iOS 17 and the current iOS.
- [ ] Cold launch under 800 ms p90 on iPhone SE 3rd gen and under 1.5 seconds on iPhone SE 2nd gen.

**Business**
- [ ] Name and trademark cleared; icon final.
- [ ] Trust page live (doc 05).
- [ ] Support email staffed with a response target of 2 business days.
- [ ] Parent NPS from TestFlight at or above 50.

---

## 11. Decisions and open questions

**DECISIONS**
- GameEngine and Dictionary core shared unchanged; DesignSystem shares tokens only; Networking and Analytics not linked.
- New packages: KidsDesignSystem, ParentalGate, KidsContent, KidsValidator; optional Speech.
- Code mono-repo; separate content repo consumed as a versioned bundle.
- Content bundled, no downloads, vector hint art.
- No analytics or telemetry; Apple opt-in crash reports only.
- Phases 0 to 4 as specified; Phase 1 exit (a child completes a round unaided) is the key gate.
- No-escape UI test and gate robustness test are release gates.
- Kid playtest protocol: 5 per band per round, three rounds, written consent and child assent.

**OPEN**
- Whether a GameEngine rule-set extension is needed for the wildcard letter (verify against App 1's final protocol in Phase 0).
- Voice hint spike outcome and compliance sign-off.
- Which Apple Kids band to select at submission (see doc 01).
- Whether iPad should be the primary screenshot device for the store page given Sprouts' landscape preference.

---

## 12. Sources

- App Store Review Guidelines (1.3, 2.3.6, 2.3.8, 5.1.4): https://developer.apple.com/app-store/review/guidelines/
- Apple, Kids apps and parental gates, age bands: https://developer.apple.com/app-store/kids-apps/
- Apple, Privacy manifest files: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files.md and required reason APIs: https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api.md (via https://developer.apple.com/tutorials/data/documentation/bundleresources/describing-use-of-required-reason-api.md)
- Apple, App privacy details on the App Store: https://developer.apple.com/support/app-privacy-on-the-app-store/
- Apple age rating changes 2025 (press summary): https://www.iphoneincanada.ca/2025/07/25/updated-app-store-age-ratings
- Kendrick, "Usability Testing with Minors: 16 Tips", NN/g, 2019: https://www.nngroup.com/articles/usability-testing-minors/
- Sherwin and Nielsen, "Children's UX: Usability Issues in Designing for Young People", NN/g, 2019: https://www.nngroup.com/articles/childrens-websites-usability-issues/
- NN/g Young Users topic: https://www.nngroup.com/topic/young-users/
- Bentley University UXC, usability testing with minors: https://www.bentley.edu/centers/user-experience-center/usabilitytestingwithminors
- Apple Human Interface Guidelines root: https://developer.apple.com/design/human-interface-guidelines/
- Jamf, Shared iPad in education: https://www.jamf.com/blog/what-are-shared-ipads-in-education/
