# Inkwell (working title): Product Vision and Brief

**Document status:** Draft v0.1, 2026-10-04, owner persona: **[JOBS — Product Lead, "Theo Marr"]**. Contributors: ARCH, IOS, DESIGN, GAME, QA, DATA.

**Read this if...** you need to understand what App 1 is, who it is for, why it deserves to exist on a phone that already has a thousand word games, what we are deliberately refusing to build in v1, how we will know it worked, what we might call it, who we are up against, and how it makes money. This is the document every other App 1 document hangs off. If a feature is not justified here, it does not get built.

## Table of contents

1. The pitch
2. Why these two paper games deserve a perfect phone version
3. Who it is for (personas)
4. Jobs-to-be-done
5. The first 60 seconds
6. What we will NOT build in v1 (kill list)
7. Success metrics
8. Naming options
9. Positioning vs. competitors
10. Monetization
11. Team debate: free vs. paid
12. Decisions and open questions

---

## 1. The pitch

**One sentence:** Inkwell is the two best paper-and-pencil word games you already know (Name Place Animal Thing and Word Chain), rebuilt as the most beautiful, fastest-to-start, zero-friction party app on iPhone, playable with nobody, one phone, or every phone at the table.

**Two-sentence version for the App Store subtitle slot:** "Pick a letter. Fill the page." The games your grandmother taught you, finally done right.

> **[JOBS]** Read the pitch again. It does not say "AI", "social", "leaderboards" or "platform". It says two games, beautiful, zero friction. If anyone writes a sentence about this product that needs more than those ideas, they have added something we should probably cut.

> **[GAME]** I want to register that "two games" is already a scope decision. Most competitors ship one. Two is defensible because they share a dictionary, a letter system and a party-game loop, but they are not the same game, and I will push for them to feel like siblings rather than twins.

> **[ARCH]** Two games sharing one engine is also the cheapest way to prove the engine is actually modular, which matters for App 2 (Kids). Agree with the scope.

## 2. Why these two paper games deserve a perfect phone version

### 2.1 The games are already loved

Name Place Animal Thing (NPAT) is played in school notebooks in India, Pakistan, Nigeria, the UK and across the Commonwealth. The same mechanic is Scattergories in North America, Stop or Tutti Frutti in Latin America, Stadt Land Fluss in Germany, Panstwa-Miasta in Poland, and Baccalauréat in France. Word Chain is Shiritori in Japan, Antakshari (with songs) in India, and the "last letter" car game everywhere else. These are not niche. They are among the most widely played games on earth, and they have no canonical digital home.

### 2.2 The existing apps are not good

Our competitor audit (Section 9) found the field splits into three groups:

1. **Big free-to-play category games** (Fanatee's Stop, the various Scattergories apps) that are ad-funded, online-first, and built around retention mechanics: energy, hints, coins, daily streaks. They are competent and popular, but they feel like slot machines wearing a word game costume.
2. **Tiny indie NPAT apps** with low ratings (one Play Store NPAT app we checked sits at a 1.9 star rating from over a thousand reviews), inconsistent validation, and no care given to the feel.
3. **Shiritori and word-chain apps** that are either Japanese-language learning tools or bare utility apps.

Nobody has built the version that a design-literate person would be proud to hand to a friend at a dinner table.

### 2.3 The phone fixes the paper game's real problems

| Paper problem | Phone solution | Why it matters |
|---|---|---|
| Someone has to be the referee and people argue about whether "Xylophone" is a Thing | Dictionary plus a fair, fast challenge vote | Arguments are 40 percent of the fun and 100 percent of the friction. We keep the fun part. |
| Someone has to keep score and always gets it wrong | Instant, animated, auditable scoring | Scoring reveals are the best moment of the game. Paper buries it in arithmetic. |
| Nobody has paper | Every pocket has a phone | Obvious, but it is the whole premise. |
| The letter is picked by someone reciting the alphabet in their head while another person says "stop" | A delightful letter draw, weighted so nobody gets X three times | Fairness and ceremony in one animation. |
| Timers are a phone anyway | Make the timer part of the aesthetic rather than a stopwatch bolted on | The clock is the heartbeat of the round. |
| Remote friends cannot play | Async play keeps a game going across days | Long-distance friends are a real persona (Section 3). |

### 2.4 What "perfect" means for a game this simple

> **[JOBS]** The founder said it: "not a hard app so it needs to be PERFECT." Here is what I take that to mean, in order. One: it opens into a game in under three seconds. Two: every tap, letter reveal, timer tick and score reveal feels like ink on paper, intentional and physical. Three: there are no dead ends, no settings you need to understand before playing, and no account. Four: it never, ever crashes or loses a round. Five: a stranger can learn it by watching one round. Everything else is decoration.

> **[DESIGN]** I would add a sixth: it has a point of view. "Ink on paper" is a visual thesis, not a skin. Most competitors have no thesis. That is our wedge.

> **[QA]** And a seventh that nobody wants to hear: it behaves perfectly when the network is gone, the phone is at 2 percent battery, the user has Dynamic Type at the largest accessibility size, and VoiceOver is on. Perfect includes the edges.

## 3. Who it is for

| Persona | Scenario | Device context | What they need from us | What kills it for them |
|---|---|---|---|---|
| **The family road trip** (parents 35 to 50, kids 8 to 14) | Three hours in a car, one adult phone passed around or two kids' phones in the back seat | Patchy network, bright sunlight, motion | Pass-and-play on one phone with a clear "hand to next player" moment; nearby mode across two or three phones with no Wi-Fi; a kid-safe default dictionary | Needing an account; any ad; any network dependency; small text |
| **Friends at a bar** (22 to 35, four to six people) | Loud, drinks on the table, phones out anyway | Everyone has their own phone, one Wi-Fi or none, dim light | A room code or nearby join in under ten seconds; a loud, funny scoring reveal; challenge votes that resolve arguments quickly; dark theme by default in low light | Slow join; a lobby that needs a host to babysit; any tutorial longer than one card |
| **The commuter, solo** (any age) | Twelve minutes on a train, one hand, standing | One hand, interrupted constantly, headphones | Solo vs. clock with a tight loop; a bot opponent for Word Chain; resume-anywhere; silent by default with haptics | Modes that need two hands; sessions that cannot be abandoned and resumed; pressure to go online |
| **The classroom teacher** (primary and middle school) | Ten minutes of a lesson, projecting a phone or iPad, 25 kids shouting answers | iPad on a projector, no student devices, school Wi-Fi blocked | A projector-friendly big-letter display; a long gentle timer; custom categories tied to the lesson (Rivers, Scientists, Verbs); a profanity-safe dictionary | Login; anything the school IT department would flag; a scoring system that humiliates the slow kid |
| **Long-distance friends** (25 to 45, two to four people) | A standing group chat, different time zones | Each on their own phone, asynchronous | Async rounds that take 90 seconds to play and can wait a day; a scoreboard that persists; a share sheet that goes to the group chat | Real-time-only play; needing everyone online at once; friend lists and social graphs we invent |

> **[KIDS]** A note from the App 2 side: the family road trip persona overlaps my audience. App 1 should not try to be the kids app, but its default dictionary and its default content must never embarrass a parent who hands the phone to a nine year old. That is a Day 1 requirement for App 1, not a Kids-app feature.

> **[JOBS]** Agreed, and it costs nothing. DATA owns a "family-safe by default" dictionary profile. Explicit mode is an adult opt-in behind a toggle.

> **[DATA]** Taking it. "Family-safe" means profanity and slurs are excluded from everything the app shows or suggests: hints, "did you mean" corrections, bot answers, leaderboards and share images. Players can still type whatever they like at their own table and it scores like any other real word; the app just will not promote it or carry it outside the table. (Reconciled 2026-10-04 with the game design spec, 02 edge case 34; this line first said the app would not validate such words.)

## 4. Jobs-to-be-done

Written as "When I..., I want to..., so I can...".

1. When I am with people and we have a lull, I want to start a game in seconds so I can turn a quiet moment into a laughing one.
2. When I am alone and bored for ten minutes, I want a fast mental sprint so I can feel sharp rather than scrolled.
3. When my friend wrote "Quokka" for Animal and I do not believe it exists, I want the app to settle it fairly so we can keep playing instead of googling.
4. When the round ends, I want the scoring to be a show so I can enjoy winning or losing publicly.
5. When we play again next week, I want our scores and our rules to be remembered so I do not have to set it up again.
6. When I am far from my friends, I want a game that fits into our chat rhythm so we keep a shared thing going.
7. When I hand my phone to a child, I want to trust what the app will show so I do not have to supervise.
8. When I play with a group that has house rules, I want to switch them on so the app plays our way, not the designer's way.

> **[GAME]** Job 8 is the one that quietly decides the architecture: house rules have to be first-class in the engine, not an afterthought in the settings screen. See the game design spec.

> **[JOBS]** Job 8 is also the one I will police the hardest in the UI. House rules exist. They are not on the first screen.

## 5. The first 60 seconds

This is the single most important spec in the program. We treat it like a film storyboard.

| Time | What the player sees | What the player does | What must be true |
|---|---|---|---|
| 0:00 | App icon tap. Launch screen is the paper texture that becomes the home screen; no logo splash, no loading bar. | Nothing | Cold launch to interactive Lobby under 800 ms p90 on an iPhone SE 3rd gen (the release gate) and never above 1.5 s on the iPhone SE 2nd gen, the oldest supported device (05 Section 4; reconciled 2026-10-04). |
| 0:01 | Home: a sheet of paper. Two large cards, NPAT and Word Chain, each with a one-line description and a small moving ink detail. One small "How to play" link. No login, no permission prompts, no notification ask. | Taps NPAT | Zero modals before first game. Zero. |
| 0:03 | "Who's playing?" with one big default option: "Just me" is preselected; "Pass the phone" and "Nearby" are visible as one-tap alternatives. A single "Play" button. | Taps Play (or adds names first) | Default path is two taps from launch to a round. |
| 0:05 | The letter draw. The alphabet rolls past like a wheel of inked tiles, slows, and lands. The letter stamps onto the paper with a haptic thud. | Watches (the first draw on a device is the full 1.2 s ceremony; every later draw is the 600 ms stroke-by-stroke write from 09, M01, scaled by preset; always skippable with a tap) | The draw is the ceremony. It must feel physical. Reduce Motion variant is a simple crossfade with the same haptic. |
| 0:07 | The round. Four lines on paper: Name, Place, Animal, Thing. The keyboard is up. The timer is an ink line draining along the top edge. | Types | Keyboard appears with the first field focused. Return key advances. Autocorrect off, no predictive bar. |
| 0:07 to 1:07 | Typing, with a small ink-dry effect as each field is confirmed. At 10 s remaining the ink line turns darker and the haptic pulses once per second. | Types, submits early or runs out | No modal on timeout. The paper simply "lifts" to reveal scoring. |
| ~1:00 | Scoring reveal: each answer is checked off, line by line, with a stamp sound and a +10 that floats up. Total lands last. For solo, a "beat your best" line. For a group, the duplicates are revealed with a wink and the 5s appear. | Watches; can tap to speed up | The reveal is the "juice" payoff. No ad, no rating prompt, no upsell here. Ever. |
| ~1:05 | One big "Next round" button, a small "Change rules" link. | Taps Next round | Second round starts in one tap. |

> **[JOBS]** Every competitor I installed showed me between two and five modals before I could play: notifications, tracking consent, a login wall, a starter pack, a daily reward. We will show zero. If we need a permission, we ask the moment it is relevant, with a single sentence, and we live with "no". This is the spec. It is not a goal.

> **[IOS]** Two things make this hard. One, the keyboard: SwiftUI focus management and keyboard avoidance on iOS 17 are fine but have sharp edges, and the first-field focus must be deterministic. Two, cold launch budget: a Metal ink shader warming up on launch can blow 1.5 s on older devices. I want the launch to use the plain SwiftUI paper and warm the shader off the critical path.

> **[DESIGN]** The 1.2 s letter draw is my favorite thing in the spec and also the first thing a bored repeat player will hate. Skippable after the first time, remembered per device. First-time players get the full ceremony.

> **[QA]** I will instrument the first 60 seconds as an automated UI test with timing assertions, run on the oldest supported device nightly. If launch to interactive exceeds budget, the build is red.

**DECISION:** The first-60-seconds table above is a binding acceptance spec for v1. Any PR that adds a modal before the first round is rejected on sight.

## 6. What we will NOT build in v1 (kill list)

| Feature | Verdict | JOBS rationale | Survives as? |
|---|---|---|---|
| Accounts, logins, profiles | **Killed** for local and solo play. Online play uses the Apple ID via Game Center only, no custom account. | Accounts are the first modal and the first support ticket. Nobody has ever said "I love creating accounts." | OPEN for post-launch if cross-device sync demands it. |
| Friend lists and a social graph | **Killed** | We do not have the users to make a graph valuable, and the users we have already have a group chat. Share a link. | Not planned. |
| In-game chat | **Killed** | Moderation cost, Kids compliance exposure, App Review friction, and the players are literally sitting together. | A fixed set of reaction stamps ("!", "no way", "nice") is allowed in online modes as a skunkworks pass. |
| Ads | **Killed** permanently | Ads are the single biggest reason the competitors feel cheap. We are selling feel. | Never. |
| Energy, lives-as-currency, coins, daily login rewards, streak freezes | **Killed** permanently | These are retention mechanics that punish players for having a life. Word Chain "lives" are a game rule, not a currency. | Never. |
| Hint purchases | **Killed** | Buying an answer is cheating with extra steps. Hints exist in the Kids app as a learning aid. | Not in App 1. |
| Real-time online multiplayer with voice | **Deferred** | Real-time is the hardest engineering, the highest infra cost and the smallest v1 audience. Async covers long-distance friends. | Phase 7 candidate; see delivery plan debate. |
| Public matchmaking with strangers | **Deferred** | Strangers plus free text plus no moderation is a Kids Category and 1.2 safety problem. | Post-launch, online async only, with name-only answers and no free chat. |
| Android | **Deferred** | One platform, done perfectly. The founder has a Mac and an Apple developer account. | Revisit after App 2 ships. |
| iPad-optimized layout | **Deferred** with a floor | The classroom persona wants iPad. v1 ships a "runs well on iPad" layout (readable, no stretched phone UI), not a bespoke iPad design. | Phase 7 bespoke pass. |
| Apple Watch, widgets, Live Activities | **Killed** for v1 | A Live Activity for an async turn is cute. Cute is not a reason. | Post-launch skunkworks. |
| Multiple languages | **Deferred** | Letter semantics change by script; this is App 3's problem. v1 is English with a UI prepared for localization. | App 3 story plan. |
| User-generated public category packs | **Killed** | Custom categories are local to a device or a game. Publishing them is a moderation product. | Not planned. |
| Themes beyond a light and dark paper | **Trimmed** | v1 ships two or three themes done perfectly, not twelve done adequately. | Pro unlock expands later. |
| Achievements and Game Center leaderboards | **Trimmed** | A global leaderboard for a game with house rules is meaningless. Solo "vs. clock" personal bests only. | Game Center achievements as a cheap post-launch add. |
| Tutorial videos or multi-screen onboarding | **Killed** | If the game needs a tutorial, the game is wrong. One "How to play" card per game, plus the first round teaches itself. | Never. |

> **[GAME]** I fought for achievements and lost, and I think that is right for v1. I want to flag that solo vs. clock needs some progression or it has no reason to be opened a second time. Personal bests per letter and per mode are the minimum.

> **[JOBS]** Personal bests are in. A screen of badges is not.

> **[IOS]** One flag on "no accounts": Game Center authentication is silent when the user is already signed in, and shows a system sheet when they are not. That sheet is Apple's, not ours, and it only appears when the user chooses an online mode. It does not violate the first-60-seconds spec because online is never the default path.

**DECISION:** The kill list is binding for v1. Reopening any killed item requires a written one-page case and a demo of the existing product with and without it.

## 7. Success metrics

Targets are for the first 90 days after public launch, measured with on-device, privacy-preserving analytics (no third-party SDK that requires App Tracking Transparency; see ARCH's architecture document).

| Metric | Target | Floor (we have a problem) | Why this number |
|---|---|---|---|
| D1 retention | 40 percent | 30 percent | Casual word games typically land in the 25 to 35 percent range; a zero-friction first run should beat the category. |
| D7 retention | 20 percent | 12 percent | Party games are event-driven; we expect a weekend spike pattern rather than daily use. |
| D30 retention | 10 percent | 6 percent | A paid or Pro-unlocked app with no streak manipulation should hold a loyal core. |
| Median session length | 6 to 9 minutes | Under 3 minutes | Three to five NPAT rounds or one Word Chain game. Longer is not better; it means friction. |
| Rounds per session (NPAT) | 4 or more | Under 2 | Fewer than two rounds means the scoring reveal did not pull people back in. |
| Second-round rate | 85 percent of first rounds lead to a second | 70 percent | The single best signal that the core loop works. |
| Pass-and-play share of sessions in month 1 | 35 percent or more | Under 15 percent | Validates the party premise. |
| App Store rating | 4.7 or higher with 200 or more ratings by day 90 | Under 4.3 | We ask for a rating only after a completed multi-round session, never during one. |
| Crash-free sessions | 99.8 percent | 99.5 percent | The founder's "perfect" standard; a party app that crashes during scoring is unforgivable. |
| Cold launch to interactive Lobby (p90) | Under 800 ms on iPhone SE 3rd gen; under 1.5 s on iPhone SE 2nd gen | Over 1.5 s on the SE 3rd gen or over 2.5 s on the SE 2nd gen | First-60-seconds spec; 05 Section 4 is the gate. |
| Pro conversion (if free plus Pro model) | 4 percent of D7 retained users | 1.5 percent | Comparable premium-unlock casual apps land between 2 and 5 percent. |
| Support tickets per 1,000 downloads | Under 2 | Over 8 | Friction shows up here first. |

> **[QA]** Crash-free at 99.8 percent is achievable for an offline-first app with no third-party SDKs. The moment we add a networking stack for async play that number gets harder. I want it tracked per mode.

> **[ARCH]** Analytics will be a first-party event log, batched, no IDFA, no fingerprinting, with a privacy manifest that says exactly that. Apple requires privacy manifests for listed SDKs and reasons for required-reason APIs; staying first-party keeps this trivial. Official docs root: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files

> **[JOBS]** The only metric I will look at daily for the first two weeks is second-round rate. If it is under 70 percent, we stop building features and fix the loop.

## 8. Naming options

Naming is open. Criteria: distinctive in App Store search, pronounceable, not a generic term we cannot own, no obvious conflict with an existing word-game app, works for a Kids sibling ("X Kids" or "X Jr."), and carries the ink-on-paper aesthetic.

Trademark notes below are from a quick public check and are **not** legal advice. Before committing, run a USPTO TESS search, a UK IPO search, an EUIPO search, and an App Store name search in the top ten storefronts, and have a trademark attorney do a clearance search on the final two.

| Candidate | Pros | Cons | Trademark / conflict notes | App Store search notes |
|---|---|---|---|---|
| **Inkwell** | Evokes pen and paper; warm; obvious Kids sibling ("Inkwell Jr."); the whole visual language falls out of it. | "Inkwell" is a common English word; several apps and products use it (note-taking, fonts, a well-known iOS UI library). | Common word, many existing uses in software. Likely only registrable in a narrow games class with a logo. Clearance needed. | Weak for discovery: nobody searches "inkwell" wanting a word game. Rely on subtitle keywords. |
| **Scribble** | Playful, physical, kid-friendly. | Extremely common; drawing apps and a well known party drawing game use it. | High conflict risk. | Search is dominated by drawing apps. Poor. |
| **Letterhead** | A pun on letters and paper; sounds like a brand. | Slightly corporate; "letterhead" means stationery. | Common word; low conflict in games but clearance needed. | Unique enough to own the term in search. Moderate. |
| **Quill** | Short, elegant, ink metaphor. | Generic; many Quill apps (writing tools, a text editor library). | Common word, crowded. | Crowded. Poor to moderate. |
| **Stop!** | Literally the name of the game in half the world; instantly understood by Latin American and German players. | Fanatee's hugely successful "Stop - Categories Word Game" owns this term in the App Store; we would look like a clone and 4.3 spam risk rises. | Direct conflict with an established app's brand. Avoid. | We would never rank. Terrible. |
| **Blot** | Short, ink, slightly cheeky; "Blot Jr." works. | Negative connotation (a blot on your record); hard to say warmly. | Short word, some conflicts, clearance needed. | Distinctive enough to own. Moderate. |
| **Foolscap** | Deeply "paper"; nobody else has it; memorable once learned. | Obscure outside the UK and Commonwealth; sounds like "fool". | Likely clear in games class. | Unique, but zero organic search volume. Depends entirely on brand. |
| **Margin** | Where you doodle in a notebook; calm; modern. | Fintech connotation; generic. | Common word, many uses. | Weak. |
| **Dash** | The "dash" you write when you leave a line blank; fast; two-syllable Kids sibling "Dash Jr." | Very generic; many apps named Dash. | Crowded. | Poor. |
| **Categoria** | Describes the game; Latin feel travels across languages (useful for App 3). | Describes only NPAT, not Word Chain; "Categories" is also a Fanatee subtitle keyword. | Descriptive terms are hard to register. | Would compete directly with "categories" search terms. Moderate. |
| **Pen Pal** | Warm, social, paper; a nice twist for the async long-distance mode. | Two words; implies messaging; some existing apps. | Common phrase. | Moderate; confusion with messaging apps. |
| **Nib** | The tip of a pen; three letters; unusual; "Nib Kids" is adorable. | Hard to search; sounds like "nip". | Short word; clearance needed but likely workable in games. | Distinctive. Zero organic volume. |

**Recommendation:**

> **[JOBS]** Keep **Inkwell** as the working title and brand thesis, and take it to a trademark attorney first. If it clears in the games class, ship it with the subtitle carrying the search terms: "Inkwell: Name Place Animal Thing". If it does not clear, the fallback order is **Nib**, then **Letterhead**, then **Foolscap**. All three keep the paper thesis. We do not pick a name for search volume; we pick a name we can love and then buy the search terms with the subtitle and keywords field.

> **[DESIGN]** Strong agree. Inkwell gives me a palette (iron gall black, india blue, oxblood), a texture (laid paper), a motion language (ink bleed, dry, blot) and a sound language (nib scratch, stamp). Nib does the same. Letterhead is colder. Foolscap is a lovely word that nobody can spell.

> **[DATA]** One practical note: the App Store subtitle and keyword field should include "name place animal thing", "scattergories" is a registered trademark of Hasbro and must not be used in our metadata, and "categories" and "word chain" are generic and fine. I will produce a keyword sheet.

> **[IOS]** App Store Connect will also reject a name that is already taken in the storefront even if trademarks are fine. We should reserve the app record early, in Phase 0, so we know.

**DECISION:** Working title stays Inkwell. App Store name reservation and trademark clearance are Phase 0 tasks. Fallbacks ranked: Nib, Letterhead, Foolscap.

**OPEN (closed by the App 2 brief):** Does the Kids sibling use "Jr." or "Kids"? The Kids vision document decided: never "Jr." (babyish to 11 to 13); working name Inkwell Kids, launch first choice "Inkling" with "Kids" in the subtitle, pending a trademark search.

## 9. Positioning vs. competitors

All listings below were checked on 2026-10-04 via web search; ratings and counts are as surfaced in store search snippets at that time and will drift. Where a figure is quoted it is from the store page snippet we saw.

### 9.1 Category games (NPAT / Scattergories / Stop / Stadt Land Fluss / Tutti Frutti)

| App | Store link | What it is | Strengths | Weaknesses we exploit |
|---|---|---|---|---|
| **Stop - Categories Word Game** (Fanatee) | https://apps.apple.com/us/app/stop-categories-word-game/id687877464 and Google Play https://play.google.com/store/apps/details?id=com.fanatee.stop (4.2 stars, roughly 244k ratings on Play at check time) | The market leader: five categories, one letter, 60 seconds, turn-based online vs. friends or randoms; was an App Store Editor's Choice in many countries per its own description. Also localized as "Stadt Land Fluss - Wörterspiel" in Germany (same app id, https://apps.apple.com/de/app/stadt-land-fluss-w%C3%B6rterspiel/id687877464). A sequel, Stop 2, exists on Play (https://play.google.com/store/apps/details?id=com.fanatee.stop2). | Massive install base, polished F2P loop, many languages, online matchmaking, hints. | Ad- and coin-driven; online-first (no real pass-and-play party mode); a 2013-era visual identity; hints undermine the "you versus your own brain" core. |
| **Scattergories** (Magmic, Hasbro license) | The historical listing https://apps.apple.com/us/app/scattergories/id1011376303 now surfaces under the title "That's so...Trivia", suggesting the licensed Scattergories app has been rebranded or wound down. Magmic developer page: https://apps.apple.com/us/developer/magmic-inc/id302049357 | The official licensed digital version of the Hasbro board game. | Brand recognition. | Appears to be no longer actively positioned as Scattergories; the brand is a Hasbro trademark we cannot use, but the gap it leaves is real. |
| **Scattergories** (newer third-party listing) | https://apps.apple.com/us/app/scattergories/id6787198440 | A free online Scattergories-style game with friends, AI and public matchmaking. | Free, online. | Generic presentation; trademark-adjacent naming that may not survive. |
| **Name Place Animal Thing** (various small devs) | iOS: https://apps.apple.com/us/app/name-place-animal-thing/id6756037441 and https://apps.apple.com/be/app/name-place-animal-thing-game/id6759839512 ; Play: https://play.google.com/store/apps/details?id=aris.kots.nameanimalplantobject (1.9 stars from about 1,173 ratings at check time) and https://play.google.com/store/apps/details?id=com.haquegames.napt ; web: https://nameplaceanimalthing.online/ | Direct NPAT implementations, mostly solo or simple multiplayer. | They own the exact search phrase. | Low ratings, inconsistent validation, no design thesis, little or no party mode. This is the gap we fill first. |
| **StopotS** | https://apps.apple.com/us/app/stopots-the-categories-game/id1451540497 (also the German storefront as "StopotS - Stadt, Land, Fluss") | Real-time online categories game, popular in Brazil and Germany. | Real-time rooms, multi-language. | Online-only; web-game aesthetic; player-vote validation can be chaotic with strangers. |
| **Stadt Land Fluss 2 - Stop**, **Stadt Land Fluss Multiplayer**, **Stadt, Land** | https://apps.apple.com/de/app/stadt-land-fluss-2-stop/id1581869942 ; https://apps.apple.com/lc/app/stadt-land-fluss-multiplayer/id890869197 ; https://apps.apple.com/us/app/stadt-land/id1596457858 | German-market category games; the last is a pure "letter and timer" companion for paper play. | Local-language dictionaries; the companion-app idea is clever and cheap. | German-only; dated UI. Confirms demand for a "companion to paper" mode (see OPEN below). |
| **Tutti Frutti** apps | Play: https://play.google.com/store/apps/details?id=com.bogdan.tuttifrutti (4.3 stars, about 5,278 ratings) ; https://play.google.com/store/apps/details?id=com.simplicity.panstwa_miasta ; iOS: https://apps.apple.com/ni/app/tutti-frutti-online/id1320614060 | Spanish-language category games, including LAN/Bluetooth local play and online tables with chat. | Local wireless play exists and is valued in reviews. | Android-leaning; chat and strangers; dated visuals. |

### 9.2 Word chain games

| App | Store link | What it is | Notes |
|---|---|---|---|
| **Shiritori** (classic iOS app) | https://apps.apple.com/us/app/shiritori/id540209774 | Japanese-language word chain vs. character opponents. | Shows the bot-opponent pattern works; Japanese only. |
| **Japanese Word Chain: Shiritori** | https://apps.apple.com/bz/app/japanese-word-chain-shiritori/id6802028933 | Vocabulary challenge. | Language-learning framing. |
| **Word Chain - Shiritori** (Android) | https://play.google.com/store/apps/details?id=kr.co.neoandroid.neoshiritori | Timed and open battle types vs. AI. | Validates "timed vs. relaxed" as a mode split, which our spec adopts. |
| **Word Chain - Word Game** | https://apps.apple.com/us/app/id1367829723 | Simple last-letter chain. | Utility-grade. |
| **WordChain: Last Letter Game** | https://apps.apple.com/us/app/-/id6739948858 | Online multiplayer last-letter game. | Online-first. |
| **Cuspart: Word Chain** | https://apps.apple.com/py/app/cuspart-word-chain/id6754160917?l=en-GB | 60-second solo chains. | Solo blitz pattern. |
| **ChainLink - Words Chain**, **Words Chain Classic** | https://apps.apple.com/app/id6749650303 ; https://apps.apple.com/us/app/id1142872216 | Single-rule chain games. | Confirms the niche is small, utility-grade and undesigned. |

### 9.3 Positioning statement

For people who love the paper games and are tired of being treated like a wallet, Inkwell is the only category-and-chain word game that is built like a beautiful object: no ads, no coins, no account, a party mode that actually works at a table, and scoring that is a show. Unlike Stop and the Scattergories clones, which are online-first ad businesses, Inkwell is offline-first and local-first, and it charges honestly once.

> **[GAME]** The honest competitive risk is Fanatee's Stop. It is good, it is huge, and it has hints and matchmaking we will never match. We win on feel, on local play and on fairness. We do not win on content volume or on online scale, and we should never pretend to.

> **[ARCH]** The "Stadt, Land" companion app is worth a sentence in our roadmap: a mode that only draws the letter and runs the timer, for people who still want to play on paper. It is nearly free to build on our engine and it is a clever on-ramp.

**OPEN:** "Paper companion" mode (letter plus timer only). JOBS inclined to say yes if it costs under one engineer-week and lives behind the NPAT card, not on the home screen.

## 10. Monetization

| Option | How it works | Pros | Cons | Fit with "perfect" | Recommendation |
|---|---|---|---|---|---|
| **A. Paid up front** ($3.99 to $5.99) | One price, everything included. | Simplest; no IAP code; aligns with "no manipulation"; attracts the right users. | Paid apps have far lower download volume; party games spread by "download this now" at the table, and a price kills that moment; no trial. | High | Not recommended as the primary model for a party game. |
| **B. Free plus one-time Pro unlock** ($4.99 to $7.99, StoreKit 2 non-consumable) | Free: both games, solo and pass-and-play, classic rules, default theme, unlimited rounds. Pro: nearby and online modes, extra categories packs, house rules, extra themes, stats. | The table can all download it free; the host buys Pro; honest; one purchase; Family Sharing works for non-consumables. | Deciding the paywall line is delicate; some reviewers rate free apps lower for "locked features". | High if the free tier is genuinely complete. | **Recommended.** |
| **C. Cosmetic themes only** | Everything free; sell paper and ink themes as non-consumables. | Zero gameplay paywall; feels generous. | Revenue likely too small to sustain; themes are costly to make well. | High | Fold into B as part of Pro and as a la carte extras later. |
| **D. Subscription** | Monthly or yearly for "everything plus new content packs". | Recurring revenue; funds content. | Players hate subscriptions for simple games; App Review scrutiny; churn; Kids-app optics. | Low | Not recommended. The brief itself says "probably not". Agreed. |
| **E. Ads** | Interstitials or rewarded video. | Revenue from free users. | Destroys the thesis; ATT prompts; Kids Category exposure. | None | Killed permanently. |

**Recommended pricing frame:** Free download. **Inkwell Pro** one-time purchase at $6.99 (US) with introductory launch price $4.99 for the first four weeks, Family Sharing enabled. Everything a solo player or a one-phone family needs is free forever. Pro buys multi-phone play, house rules, category packs and themes, and the Pro purchaser's phone unlocks nearby and online sessions for everyone at the table (the host pays, the guests play free in that session).

> **[IOS]** "Host pays, guests play free" is the right call for the party dynamic and it is simple with StoreKit 2: entitlement is checked on the host device at session creation; guests do not need the entitlement to join. For online async, the match creator needs Pro; invitees do not. Game Center turn-based matches support this because the creator starts the match. Doc: https://developer.apple.com/documentation/gamekit/gkturnbasedmatch

> **[ARCH]** Cost side: with offline-first and Game Center for online, our infra bill is close to zero. That is what makes a one-time purchase viable. If we ever move online play to our own backend, the economics change and we revisit.

> **[DATA]** Category packs as Pro content means packs must be built to a quality bar (coverage per letter, validation lists). I will size each pack at roughly two to three days of content work including QA.

## 11. Team debate: free vs. paid

> **[JOBS]** I want to make the case for paid up front one last time so it is on the record. A $4.99 app with no IAP is the purest product. One decision for the buyer, one for us. No paywall UX, no "locked" badges, no conversion funnel to optimize. The people who pay for a word game are exactly the people who will leave five-star reviews.

> **[GAME]** And it kills the table moment. "Everyone download this" works when the answer is free. "Everyone pay five dollars" means two people download it and the rest watch. Party games spread by being free to join.

> **[IOS]** From the store side: paid apps get a fraction of the impressions and installs of free ones, and the App Store's own merchandising overwhelmingly features free-with-IAP. Our ranking in "name place animal thing" searches will depend on download velocity. Paid up front makes that an uphill walk.

> **[DESIGN]** I care about what the free tier looks like. If the free app is a demo with locks everywhere, it will feel cheap and we lose the thesis anyway. If the free app is complete for solo and pass-and-play, with Pro as "unlock the table and the toolbox", it can be as elegant as a paid app.

> **[QA]** Paid up front has one underrated benefit: far fewer StoreKit edge cases to test. Restore purchases, Family Sharing propagation, refund handling, offline entitlement cache. That is real test surface. I can own it, but it is not free.

> **[ARCH]** StoreKit 2 makes the entitlement check a few lines and the transaction listener handles restore and refunds; it is well-trodden. I estimate one engineer-week including a paywall screen and tests. That is cheap compared to the download delta.

> **[JOBS]** Then here is what I will hold you to. The free tier is a complete, proud product: both games, solo and pass-and-play, classic rules, the default theme, no limits on rounds, no nag screens. The Pro screen appears only when a player taps a Pro feature, once per session at most, and it is beautiful. And we never, ever show it in the first 60 seconds. On those terms, free plus Pro.

**DECISION:** Free download with a one-time **Inkwell Pro** non-consumable unlock via StoreKit 2. Free tier is complete for solo and pass-and-play. Pro unlocks nearby and online modes, house rules, category packs, extra themes and stats. Host-pays model for multi-phone sessions. No ads, no subscription, no consumables, ever.

**OPEN:** Exact price point ($4.99 vs. $6.99) and whether to run an introductory price. Decide after TestFlight feedback in Phase 5.

**OPEN:** Whether custom categories (user-typed) are free or Pro. GAME argues free (classroom persona); JOBS leans Pro (it is a "toolbox" feature). Decide with the house-rules paywall line in Phase 3.

## 12. Decisions and open questions (consolidated)

**DECISIONS**

1. App 1 ships exactly two games: NPAT and Word Chain.
2. The first-60-seconds table is a binding acceptance spec; zero modals before the first round.
3. The kill list in Section 6 is binding for v1.
4. Working title Inkwell; trademark clearance and App Store name reservation in Phase 0; fallbacks Nib, Letterhead, Foolscap.
5. Monetization: free plus one-time Pro unlock; no ads, no subscription, no consumables.
6. Family-safe dictionary profile is the default in App 1; explicit content is an adult opt-in. The profile governs what the app shows and promotes; a private table's typed words are scored on their merits (02 edge case 34).
7. Second-round rate is the headline health metric for launch.
8. Cold launch gate: 800 ms p90 to interactive Lobby on iPhone SE 3rd gen, 1.5 s never-exceed on iPhone SE 2nd gen (05 Section 4).
9. Letter draw: the full 1.2 s ceremony once per device, then 600 ms per draw scaled by preset, always tap-to-skip (09 M01; master 6.8).

**OPEN**

1. Kids sibling naming ("Jr." vs. "Kids"): closed by the App 2 brief ("Kids", or Inkling pending trademark).
2. Paper-companion mode (letter plus timer only) in v1 if under one engineer-week.
3. Exact Pro price and introductory pricing.
4. Custom categories free or Pro.
5. Whether cross-device sync (and therefore some form of account) is ever needed; revisit post-launch.

---

### Sources

- Apple, App Store support page with iOS usage as measured on June 7, 2026: https://developer.apple.com/support/app-store/
- Apple, App Review Guidelines (4.2 Minimum Functionality, 4.3 Spam): https://developer.apple.com/app-store/review/guidelines/
- Apple, Human Interface Guidelines root: https://developer.apple.com/design/human-interface-guidelines/
- Apple, GKTurnBasedMatch: https://developer.apple.com/documentation/gamekit/gkturnbasedmatch
- Apple, Privacy manifest files: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- Fanatee, Stop - Categories Word Game: https://apps.apple.com/us/app/stop-categories-word-game/id687877464 ; https://play.google.com/store/apps/details?id=com.fanatee.stop
- Magmic developer page: https://apps.apple.com/us/developer/magmic-inc/id302049357 ; former Scattergories listing: https://apps.apple.com/us/app/scattergories/id1011376303
- Third-party Scattergories: https://apps.apple.com/us/app/scattergories/id6787198440
- NPAT apps: https://apps.apple.com/us/app/name-place-animal-thing/id6756037441 ; https://apps.apple.com/be/app/name-place-animal-thing-game/id6759839512 ; https://play.google.com/store/apps/details?id=aris.kots.nameanimalplantobject ; https://play.google.com/store/apps/details?id=com.haquegames.napt ; https://nameplaceanimalthing.online/
- StopotS: https://apps.apple.com/us/app/stopots-the-categories-game/id1451540497
- Stadt Land Fluss apps: https://apps.apple.com/de/app/stadt-land-fluss-2-stop/id1581869942 ; https://apps.apple.com/lc/app/stadt-land-fluss-multiplayer/id890869197 ; https://apps.apple.com/us/app/stadt-land/id1596457858
- Tutti Frutti apps: https://play.google.com/store/apps/details?id=com.bogdan.tuttifrutti ; https://play.google.com/store/apps/details?id=com.simplicity.panstwa_miasta ; https://apps.apple.com/ni/app/tutti-frutti-online/id1320614060
- Shiritori and word chain apps: https://apps.apple.com/us/app/shiritori/id540209774 ; https://apps.apple.com/bz/app/japanese-word-chain-shiritori/id6802028933 ; https://play.google.com/store/apps/details?id=kr.co.neoandroid.neoshiritori ; https://apps.apple.com/us/app/id1367829723 ; https://apps.apple.com/us/app/-/id6739948858 ; https://apps.apple.com/py/app/cuspart-word-chain/id6754160917?l=en-GB ; https://apps.apple.com/app/id6749650303 ; https://apps.apple.com/us/app/id1142872216
