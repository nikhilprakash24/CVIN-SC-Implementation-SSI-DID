# App 2 "Inkwell Kids": Vision and Kid Design Principles

**Read this if...** you need to understand why we are building a second, separate app for children instead of a "kids mode" inside App 1, who it is for (ages roughly 5 to 13 in three bands), what we promise parents, what we refuse to build, how we will know it is working, and what the app might be called. This is the north-star document for App 2; the game adaptations, phased plan, design directions and compliance docs (02 to 05) all hang off it.

**Document status:** Draft v0.1, 2026-10-04, owner **[JOBS — Product Lead, "Theo Marr"]** with **[KIDS — Child UX & Learning Specialist, "Dr. Amara Nwosu"]**.

---

## Table of contents

1. The pitch in one breath
2. Why a separate app and not a mode (the debate)
3. Audience and age bands, with developmental notes
4. Design principles for kids (each with a test)
5. What we refuse to build
6. Success metrics appropriate for kids
7. Naming options and brand relationship to App 1
8. Decisions and open questions
9. Sources

---

## 1. The pitch in one breath

Name Place Animal Thing and Word Chain are the two word games every family already knows how to play at a kitchen table with a pencil. App 2 is those two games made for a child's hands and a child's reading level: big letters, gentle time, hints when you are stuck, silly categories, and an app that celebrates a six-year-old spelling "zebra" as "zebrah" without lying to her about the spelling. No ads, no chat, no strangers, no accounts for kids. A parent can hand over a phone for twelve minutes and not think about it.

> **[JOBS]** The pitch has to survive a parent reading it on a store page in four seconds. "Word games your kid can actually play, safely." If we cannot say it that plainly we do not understand what we are building.

> **[KIDS]** And the second sentence for the parent who reads on: "Built to the Kids Category rules, no third-party analytics, nothing your child types ever leaves the device." That sentence is a product requirement, not marketing copy. See doc 05.

---

## 2. Why a separate app and not a mode (the debate)

The founder's brief says App 2 is a separate app, not a toggle. We still owe the decision a real argument, because a mode is cheaper and the team should know what we are paying for.

### 2.1 Options

| Option | Description | Discoverability | Compliance isolation | Brand and trust | Maintenance cost |
|---|---|---|---|---|---|
| A. Kids mode inside App 1 | A "Kids" toggle in App 1 settings that swaps content and loosens validation | Poor: App 1 cannot use "For Kids" in metadata or appear in the Kids Category without itself meeting every Kids Category rule (App Store Review Guidelines 1.3 and 2.3.8) | Poor: the whole app inherits Kids rules, including no third-party analytics and no link-outs without a gate | Confusing: parents do not trust a "mode" in an adult game | Lowest |
| B. Separate app, shared engines (recommended) | Second App Store listing, own bundle, own design system, same engine and dictionary packages (`IWCore`, `IWRules`, `IWContent` in the App 1 architecture document; GameEngine and Dictionary in the brief) | Excellent: listed in Kids Category with an age band, "Kids" in the name | Excellent: Kids rules apply only to App 2; App 1 keeps normal analytics and online play | Strong: a dedicated promise to parents; separate icon and store page | Medium: two targets, two release trains, shared packages absorb most logic |
| C. Separate app, forked codebase | Copy App 1 and diverge | Excellent | Excellent | Strong | Highest: every engine bug fixed twice |
| D. Kids-only product first, no App 1 | Skip App 1 | n/a | n/a | n/a | Rejected by founder brief: App 1 ships first |

### 2.2 The team debate

> **[ARCH]** Let me make the honest case for a mode. A single binary with a `kidsMode` flag is one target, one release, one crash dashboard. Engines are identical either way. The incremental cost of option B is a second Xcode target, a second App Store listing, a second review pipeline and a second design system package. I estimate that at 25 to 35 percent of the App 1 engineering budget for the parts that are not the engines.

> **[KIDS]** The mode fails on the rule that matters most. Guideline 1.3 says once customers expect your app to follow Kids Category requirements it must keep following them in later updates, and guideline 2.3.8 reserves "For Kids" and "For Children" in metadata for the Kids Category. A mode inside App 1 cannot be found by a parent browsing the Kids Category, and if App 1 did enter the Kids Category, App 1 would lose third-party analytics, would need a parental gate in front of every link-out and purchase, and would have to treat its online multiplayer as a children's feature. We would be dragging App 1 into COPPA scope to save a target. Sources: https://developer.apple.com/app-store/review/guidelines/ and https://developer.apple.com/app-store/kids-apps/

> **[JOBS]** Also, taste. A kid app that is secretly an adult app with a sticker on it feels like one. The letter tiles are the wrong size. The timer is the wrong tempo. The failure copy is the wrong register. The first-run experience is a settings toggle. No.

> **[IOS]** From a review standpoint, a mode is also a liability. App Review tests the whole binary. If App 1 has Game Center online play and a Kids toggle, the reviewer will ask why a children's experience sits next to open multiplayer, and we have no clean answer.

> **[DESIGN]** The design system argument is decisive for me. Kids need different type scale, different target sizes, different motion tempo and a different illustration language. If both live in one DesignSystem package we get a tangle of `if kids` branches in every component. Two packages that share tokens where sensible is cleaner.

> **[QA]** One concern with option B: two release trains for a one-to-two engineer team. I want the shared packages to carry the test weight so that App 2 releases are mostly content and UI verification, not engine regression.

> **[ARCH]** Agreed on all of that. The honest conclusion is that option B's extra cost buys the only thing a kids app must have, which is isolation. Shared Swift packages (GameEngine, Dictionary core, Persistence) keep the engine fixed once. I withdraw the mode.

**DECISION:** Option B. Separate app, separate bundle identifier, listed in the Kids Category, built on the shared engine packages. Option C is rejected outright. Option A does not survive as a parallel pass.

**OPEN:** Whether App 1 ever gets a "Family" preset (looser timers, simpler categories) that is explicitly not marketed to children and not in the Kids Category. This is a feature question for App 1, not App 2.

### 2.3 What separation buys the parent

- A listing in the Kids Category with a declared age band (Apple offers "5 and under, 6 to 8, or 9 to 11" in App Store Connect; source https://developer.apple.com/app-store/kids-apps/).
- A promise that nothing the child types leaves the device (see doc 05).
- No sign-in, no account, no email asked of the child.
- An icon the child recognizes as theirs and the parent recognizes as safe.

---

## 3. Audience and age bands, with developmental notes

### 3.1 Who the app is for

Primary user: a child aged roughly 5 to 13 who plays alone, with a sibling, or with a parent on one phone or tablet. Secondary user: the parent, who installs, sets the age band, controls settings behind a gate, and wants to feel good about the twelve minutes. Tertiary user: a teacher running a five-minute word warm-up on classroom iPads (doc 02 covers that scenario).

Context on usage: Common Sense Media's 2025 census of children 0 to 8 reports that 40 percent of children have their own tablet by age 2, that gaming time among 5 to 8 year olds rose from 40 to 64 minutes per day over four years, and that screen use is about 2.5 hours per day on average (https://www.commonsensemedia.org/research/the-2025-common-sense-census-media-use-by-kids-zero-to-eight). The American Academy of Pediatrics advises parents of children 5 and older to place consistent limits on time and type of media and to keep media from displacing sleep and physical activity (summarized at https://www.health.harvard.edu/blog/new-expert-recommendations-on-media-use-and-children-2016102510564; the AAP's media plan tool is at https://www.healthychildren.org/English/fmp/Pages/MediaPlan.aspx). Our takeaway is not "kids have lots of screen time so there is a market." It is "the parent is already managing a budget, so a session should be short, complete and easy to end."

> **[KIDS]** The Common Sense numbers tell us the device is in the house already. They do not tell us to compete for time. Our job is to be the thing a parent is glad the child picked.

### 3.2 Age bands

Nielsen Norman Group's children's UX research insists there is "no such thing as designing for children aged 3 to 12" as one group and segments at 3 to 5, 6 to 8 and 9 to 12 (Sherwin and Nielsen, 2019, https://www.nngroup.com/articles/childrens-websites-usability-issues/). Apple's Kids Category bands are 5 and under, 6 to 8, 9 to 11. The ICO's Children's Code uses its own developmental stages in Annex B (https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/age-appropriate-design-a-code-of-practice-for-online-services/). Our bands are chosen around literacy, because this is a spelling game, and then mapped to Apple's bands for the store.

| Band | Approx. ages | Reading stage (Chall) | Spelling stage (Gentry) | Attention for a structured task | Fine motor | What they find funny or satisfying |
|---|---|---|---|---|---|---|
| Sprouts | 5 to 7 | Stage 0 to 1: pre-reading into initial decoding; sight words, letter-sound links | Semiphonetic to phonetic; "invented spelling" is normal and healthy | Roughly 10 to 20 minutes, less when the task is adult-directed | Tapping is reliable; dragging and pinching are not; wrist rests on the bottom edge of a tablet | Animals doing people things, bodily noises, surprises, a character who gets it wrong and laughs; satisfaction from completing a set and from being told their idea was good |
| Explorers | 8 to 10 | Stage 2 to 3: fluency, then reading to learn | Transitional to correct; still frequent vowel and double-consonant errors | Roughly 15 to 30 minutes; can sustain a multi-round game | Dragging is fine; small targets are tolerable but still error-prone | Wordplay, puns, "gross" categories (Things that smell), beating a bot, collecting and completing, mild competition with siblings |
| Navigators | 11 to 13 | Stage 3: reading to learn, large vocabulary growth | Mostly correct; homophones and irregular words remain hard | 20 to 40 minutes; want depth and mastery | Adult-like | Cleverness, speed, obscure answers, personal bests, being treated like a grown-up; dislike anything "babyish" |

Sources for the developmental columns: Chall's stages as summarized by Reading Rockets (https://www.readingrockets.org/reading-101/how-children-learn-read/typical-reading-development) and IMSE (https://imse.com/journal/article/stages-of-reading-development/); Gentry's spelling stages and the normality of invented spelling (https://www.readingrockets.org/topics/spelling-and-word-study/articles/invented-spelling-and-spelling-development); the widely used 2 to 5 minutes per year of age heuristic for adult-directed attention (https://www.earlyyears.tv/attention-span-development/), which we treat as a rough planning guide rather than a measurement; children's touch accuracy and difficulty with drag gestures from the University of Florida INIT lab studies (https://init.cise.ufl.edu/?p=3232 and https://lisa-anthony.com/wp-content/uploads/2012/03/brown-and-anthony-chi2012eist.pdf); Sesame Workshop's preschool tablet best practices on tapping, landscape and wrist-rest hotspots (https://joanganzcooneycenter.org/?p=19607).

> **[KIDS]** Two things I want everyone to internalize. First, a 6-year-old writing "elefant" is not failing; she is at the phonetic stage and doing exactly what a reader her age does. The app must never make her feel she got it wrong, and it must also never tell her "elefant" is the spelling. That tension is the whole design problem of doc 02. Second, the attention heuristic says a 6-year-old gives us maybe 15 minutes. One NPAT round for Sprouts should fit in two.

> **[GAME]** The humor column is not decoration. Category names are our comedy. "Things that are sticky" is a legitimate category for Sprouts and it does more for retention than any badge.

> **[JOBS]** Navigators are the band we will most likely get wrong. An 11-year-old will delete anything that looks like it was made for a 6-year-old. The design directions in doc 04 need to pass the "would a 12-year-old be embarrassed to be seen with this" test.

### 3.3 Mapping to Apple's bands

| Our band | Apple Kids Category band | Notes |
|---|---|---|
| Sprouts 5 to 7 | 6 to 8 (and defaults chosen so "5 and under" is safe) | We will not market to under 5; pre-readers cannot play a spelling game. The app must still be harmless if a 4-year-old opens it. |
| Explorers 8 to 10 | 6 to 8 and 9 to 11 | Store listing picks one band; we recommend 6 to 8 for discoverability, with the app's own band selector covering the rest. |
| Navigators 11 to 13 | 9 to 11 | Apple's Kids bands stop at 11. Children aged 12 and 13 are still under 13 for COPPA. The app rating is 4+. |

**OPEN:** Which single Apple band to select at submission. **[KIDS]** leans 6 to 8 (broadest parent browsing). **[JOBS]** wants to look at Kids Category browse data before deciding. Decide in Phase 3 of doc 03.

---

## 4. Design principles for kids (each with a test)

Each principle carries a test that a reviewer can run on a build without asking the designer what they intended.

1. **One thing on screen.** A kid screen has one primary action. Test: cover the screen and ask a 6-year-old tester "what do you do here?"; if the answer takes more than one gesture description, fail.
2. **Tap, never pinch.** All core play is completable with single taps; drag is optional and never required. Test: complete a full NPAT round and a full Word Chain game with a stylus using only taps.
3. **Read it to me.** Every instruction and category name has a spoken version available by tapping a speaker glyph, on by default for Sprouts. Test: with the device muted and sound on, a pre-reader can start and finish a round with an adult saying nothing.
4. **Wrong is interesting, not bad.** No red X, no buzzer, no sad face. A near-miss gets curiosity ("Ooh, close! Zebra is spelled Z-E-B-R-A"). Test: audit every failure state; any state with a negative sound, red color or sad character fails.
5. **Time is a friend or absent.** Timers are off by default for Sprouts and gentle elsewhere; the clock never flashes, never beeps faster, never shrinks. Test: watch a Sprouts session; if a child looks at the clock more than once a round, the clock is too present.
6. **Celebrate big, briefly.** A success gets a generous animation that lasts under two seconds and never blocks the next action. Test: time every celebration; anything over two seconds or requiring a dismiss tap fails.
7. **Nothing to buy, nowhere to go.** The child-facing surface has zero links, zero purchase prompts, zero "tell a friend". Test: tap every pixel of every kid screen for five minutes; the app must never leave itself or show a gate.
8. **Big hands, big targets.** Minimum 60 by 60 points for anything a child taps, 72 for Sprouts letter keys, with at least 12 points of spacing; Apple's general minimum is 44 by 44 points (https://developer.apple.com/design/human-interface-guidelines/accessibility) and children need more (University of Florida touchscreen studies above). Test: automated layout audit plus a 5-year-old thumb test on an iPhone SE.
9. **No reading required to recover.** If a child is stuck or lost, a single always-visible home glyph gets them back to the start. Test: hand a stuck screen to a pre-reader; they reach home in one tap.
10. **The parent is never surprised.** Anything that changes behavior (band, timers, sounds, purchases if any) lives behind the parental gate, and the parent can see in one screen what the app stores. Test: a parent reads the parent area for 60 seconds and can answer "what does this app know about my child?" correctly ("their chosen name, their stickers, nothing else").
11. **Fair to the slow speller.** Scoring never punishes slow typing more than wrong answers; Sprouts scoring ignores spelling entirely when the intended word is recognized. Test: have two testers, one fast and one slow, with the same answers; scores must match in untimed modes.
12. **Works on the kitchen phone.** Pass-and-play on one device is first-class, with a handoff screen that hides the previous player's answers. Test: two siblings play a round on one iPhone without either seeing the other's answers.

> **[DESIGN]** Principle 1 is going to fight with principle 3. A speaker glyph on every label is clutter. Proposal: one speaker glyph per screen that reads the whole screen in order, plus tap-to-hear on category names only.

> **[KIDS]** Accepted for Explorers and Navigators. For Sprouts I want auto-read on screen entry, which removes the glyph problem.

**DECISION:** Auto-read on screen entry for Sprouts, single screen-level speaker plus tap-to-hear on categories for the older bands.

---

## 5. What we refuse to build

This list is a contract with parents and with ourselves. Each item names the pattern, why it is harmful to children, and what we do instead.

| We refuse | Why | Instead |
|---|---|---|
| Advertising of any kind, including "house ads" for App 1 | Kids Category forbids third-party advertising in nearly all cases and children cannot distinguish ads from content (NN/g found kids click cartoon ads thinking they are games) | Nothing. App 1 is mentioned only in the parent area behind the gate. |
| Chat, messaging, free-text sharing | COPPA personal information exposure; moderation impossible at our scale | Pass-and-play and nearby play with no text leaving the device |
| Open social features, friend lists, public leaderboards | Strangers, comparison pressure, personal data | Family-only "who played today" on the device; optional nearby play with a visible device name only |
| Loot boxes, gacha, random paid rewards | Gambling mechanics; the FTC's dark patterns report flags manipulative design in gaming (https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf) | Deterministic collection: play a round, earn a sticker; every sticker is reachable |
| Streak guilt, "don't lose your streak", countdown nudges | Manufactured anxiety; the ICO Children's Code standard 13 says nudge techniques must not be used against children's interests | No streaks. A calendar of "days you played" exists only in the parent area |
| Variable-ratio rewards, surprise boxes with timers | Compulsion loops | Fixed, visible progress |
| Push notifications to the child | Interrupts, re-engagement pressure | None. Zero notification permission requests in the app. |
| Accounts, logins, emails, birthdates for children | Data minimization; a game needs none of it | Local profiles with a nickname and an avatar |
| Third-party analytics or crash SDKs that transmit identifiers | Guideline 1.3 and 5.1.4 | Apple's own opt-in crash reporting and aggregated, non-identifying local counters surfaced to the parent only (doc 05) |
| Link-outs from kid screens | Guideline 1.3 | Only in the parent area, behind the gate |
| Energy systems, lives that regenerate on a timer | Artificial scarcity to drive return visits | Play as much or as little as the parent allows |
| "Rate us" or review prompts shown to the child | Deceptive to a child | Optional, once, in the parent area |
| Dark, scary or violent imagery in any band | Age appropriateness | Friendly characters, nothing frightening in failure states |

> **[JOBS]** I want this table on the Trust page verbatim. Parents respond to a company saying what it will not do.

> **[GAME]** I will defend one thing on the edge: a daily "letter of the day" that is the same for everyone. It is not a streak; missing it costs nothing. It gives a sibling pair something to compare.

> **[KIDS]** Acceptable if there is no record of missed days visible to the child and no notification. It is a fresh prompt, not a commitment.

**DECISION:** Letter of the day allowed, with no missed-day record visible to the child and no notifications.

---

## 6. Success metrics appropriate for kids

We will not optimize engagement. Daily active users and session count are the wrong goals for a children's product and the ICO's "detrimental use of data" and "nudge techniques" standards point the other way. We measure joy, learning and parent trust, with on-device, non-identifying counters that the parent can see.

### 6.1 Joy signals (measured in playtests, not telemetry)

- Laughs per session in moderated playtests (observer count).
- "Again?" rate: proportion of playtest sessions where the child asks to play another round unprompted.
- Voluntary category picks: how often children choose the silly categories versus the plain ones.
- Zero crying or frustration exits in Sprouts testing.

### 6.2 Learning signals (on-device, shown to the parent)

- New words produced: the count of distinct valid words a child has produced for the first time (local only).
- Spelling tier movement: the share of answers accepted at exact spelling versus phonetic tolerance, trending toward exact over weeks for the same child.
- Category breadth: number of distinct categories played.
- Hint reliance: hints used per round, expected to fall over time for a given band.

### 6.3 Parent trust signals (asked of adults)

- Parent NPS after two weeks, collected only in the parent area, optional, no identifiers.
- "I understand what this app stores about my child" agreement rate in parent interviews (target 95 percent).
- App Store ratings and written reviews mentioning "safe", "no ads", "calm".
- Zero App Review rejections on Kids Category grounds.

### 6.4 What we deliberately do not measure

- Retention curves on individuals (we have no individuals; there are no identifiers).
- Session length maximization. If anything we want a natural stopping point every 10 to 15 minutes for Sprouts.
- Push notification open rates (there are none).

> **[DATA]** Learning signals require storing per-profile word history on device. That is fine under COPPA because data that never leaves the device is not "collected" (FTC COPPA FAQ: "You are not collecting personal information simply because your app interacts with personal information that is stored on the device and is never transmitted", https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions). But it means the parent needs a one-tap delete.

> **[ARCH]** And it means no iCloud sync of kid profiles in v1. Sync turns on-device data into transmitted data and changes the analysis. Doc 05 has the decision.

> **[JOBS]** Metrics that we cannot see from the office will frustrate us. Good. We will learn from kids in rooms, which is how this kind of product should be built.

**DECISION:** No remote analytics in v1. Playtest-measured joy signals and on-device learning signals shown to the parent. Parent NPS collected optionally through a gated form.

---

## 7. Naming options and brand relationship to App 1

App 1's working codename is "Inkwell". App 2 should be recognizably from the same family (parents who own App 1 should find App 2) without being a diminutive that older kids reject.

| Option | Pros | Cons | Band fit |
|---|---|---|---|
| Inkwell Kids | Clear, searchable, "Kids" is permitted in Kids Category metadata | Generic; "Kids" may embarrass Navigators | Sprouts, Explorers |
| Inkwell Jr. | Family link, short | "Jr." reads as babyish to 11 to 13 | Sprouts |
| Inkwell Sprout | Warm, growth metaphor, owns the band name | Weak link to "word game"; a 12-year-old will not say it aloud | Sprouts |
| Inkling | Playful, means "a small idea", one word, shares "Ink" | Trademark crowding risk in app names; check before committing | All bands |
| Doodle Letters | Describes the crayon direction in doc 04 | No link to App 1 | Sprouts, Explorers |
| Letterbug | Character-led, works with a mascot | No link to App 1; crowded namespace | Sprouts, Explorers |
| Inkwell Play | Neutral, not babyish | Does not signal kids, which hurts Kids Category discovery | Explorers, Navigators |
| Scribble & Chain | Names both games | Long; hard to say | Explorers |

> **[JOBS]** "Inkling" is the one I would put on a billboard. It is a real word, it is small on purpose, and it does not apologize. If the trademark search is clean it is my pick, with "Inkling: word games for kids" as the subtitle so the Kids Category search still works.

> **[KIDS]** I like Inkling for the brand but want "Kids" in the subtitle, which guideline 2.3.8 permits for Kids Category apps. The 12-year-old problem is solved by the Navigators theme, not by the name.

> **[DESIGN]** Brand relationship: same wordmark family (same letterforms for "Ink"), different color world, a mascot that App 1 does not have. App 1 is ink and paper for adults; App 2 is the same ink held by a smaller hand.

**DECISION:** Working name remains "Inkwell Kids" in all planning documents. Shortlist for launch naming: Inkling (first choice pending trademark search), Inkwell Kids (fallback). Trademark search runs in Phase 2 and the naming decision is made in Phase 3 of doc 03. This also closes the App 1 brief's OPEN on "Jr." versus "Kids": "Kids" (or Inkling with "Kids" in the subtitle), never "Jr.".

**OPEN:** Trademark and App Store name availability search for "Inkling".

---

## 8. Decisions and open questions

**DECISIONS**
- Separate app, separate bundle, Kids Category, shared engine packages.
- Three product bands: Sprouts 5 to 7, Explorers 8 to 10, Navigators 11 to 13.
- No ads, no chat, no social, no accounts, no notifications, no streaks, no loot boxes, no energy systems.
- Auto-read for Sprouts; tap-to-hear for older bands.
- No remote analytics in v1; learning signals on-device and parent-visible.
- Letter of the day permitted without missed-day records or notifications.
- Working name "Inkwell Kids"; "Inkling" first choice pending trademark.

**OPEN**
- Which Apple Kids band to select at submission.
- Trademark search for "Inkling".
- Whether App 1 gets a non-marketed "Family" preset.
- Whether Navigators (11 to 13) is served well enough by one app or deserves a theme pack that removes the mascot entirely (doc 04 explores).

---

## 9. Sources

- App Store Review Guidelines, sections 1.3, 2.3.6, 2.3.8, 5.1.4: https://developer.apple.com/app-store/review/guidelines/
- Apple, "Design safe and age-appropriate experiences" (Kids apps, parental gates, age bands): https://developer.apple.com/app-store/kids-apps/
- Apple Human Interface Guidelines root: https://developer.apple.com/design/human-interface-guidelines/ and Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Sherwin and Nielsen, "Children's UX: Usability Issues in Designing for Young People", NN/g, 2019: https://www.nngroup.com/articles/childrens-websites-usability-issues/
- NN/g Young Users topic page: https://www.nngroup.com/topic/young-users/
- Common Sense Media, 2025 Census: Media Use by Kids Zero to Eight: https://www.commonsensemedia.org/research/the-2025-common-sense-census-media-use-by-kids-zero-to-eight
- AAP media guidance summary (Harvard Health): https://www.health.harvard.edu/blog/new-expert-recommendations-on-media-use-and-children-2016102510564 and AAP Family Media Plan: https://www.healthychildren.org/English/fmp/Pages/MediaPlan.aspx
- Reading Rockets, typical reading development (Chall): https://www.readingrockets.org/reading-101/how-children-learn-read/typical-reading-development
- IMSE, Chall's six stages: https://imse.com/journal/article/stages-of-reading-development/
- Reading Rockets, invented spelling and spelling development (Gentry): https://www.readingrockets.org/topics/spelling-and-word-study/articles/invented-spelling-and-spelling-development
- Attention span heuristic (planning guide only): https://www.earlyyears.tv/attention-span-development/
- University of Florida INIT lab, Fitts' law for children's touch: https://init.cise.ufl.edu/?p=3232; Brown and Anthony, children's touch interactions: https://lisa-anthony.com/wp-content/uploads/2012/03/brown-and-anthony-chi2012eist.pdf
- Sesame Workshop best practices for preschool tablets (via Joan Ganz Cooney Center): https://joanganzcooneycenter.org/?p=19607
- FTC, Complying with COPPA FAQ: https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions
- FTC, Bringing Dark Patterns to Light (2022): https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf
- ICO, Age appropriate design code: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/age-appropriate-design-a-code-of-practice-for-online-services/
