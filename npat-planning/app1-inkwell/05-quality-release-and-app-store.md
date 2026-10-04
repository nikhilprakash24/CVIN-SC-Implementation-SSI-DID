# Inkwell (App 1) — Quality, Release and App Store Plan

**Document status:** Draft v0.1, 2026-10-04. Owner: **[QA — Lena Fischer]**, with **[IOS — Marcus Oyelaran]**. Contributions from **[JOBS]**, **[ARCH]**, **[DESIGN]**, **[DATA]**, **[KIDS]**.

**Read this if...** you are responsible for whether Inkwell ships, when it ships, and whether it is allowed to be called finished. The founder's standard is explicit: it is not a hard app, so it has to be perfect. This document turns that sentence into a test strategy, a device matrix, numeric budgets, a beta program, an App Store Review readiness checklist mapped to specific guideline sections, the privacy label plan, export compliance, age rating expectations, the release train, phased rollout and hotfix process, the product page plan, a launch-day runbook, post-launch monitoring, the support loop, and a 48-item "perfect app" quality bar.

---

## Table of contents

1. Quality philosophy
2. Test strategy pyramid
3. Device and OS matrix
4. Crash-free and performance budgets
5. Beta program design
6. App Store Review readiness checklist (mapped to guideline sections)
7. App Privacy nutrition label plan
8. Export compliance
9. Age rating questionnaire expectations
10. Release train and versioning
11. Staged rollout and phased release
12. Hotfix process
13. App Store product page plan
14. Launch-day runbook
15. Post-launch monitoring
16. Support and feedback loop
17. The "perfect app" quality bar (48 items)
18. Risk register
19. Decisions and open questions
20. Sources

---

## 1. Quality philosophy

> **[JOBS]** "Not a hard app, so it needs to be perfect" means: there is no feature so complex that we are allowed to ship it rough. A word game that stutters, mislabels a button for VoiceOver, or loses a match on a phone call is not a word game with bugs. It is a bad word game.
>
> **[QA]** Then quality is not a phase at the end. It is a set of gates that run on every pull request, a device matrix we actually own, and a beta with real families. I will write down every gate and every budget as a number, because "feels great" is not a release criterion I can enforce.
>
> **[IOS]** And "perfect" is bounded by scope. The way we make a small app perfect is to keep it small. Every feature we add multiplies the test matrix.

Three operating rules:

1. **Every bug report becomes a fixture.** The event-sourced match log (see `04-...`) is attached to every gameplay bug; the fix includes a replay test.
2. **Gates, not opinions.** Each release gate is a measurable threshold listed in this document and enforced in CI or by a named person.
3. **Accessibility and Reduce Motion are release blockers**, not polish items.

---

## 2. Test strategy pyramid

| Layer | What | Tooling | Where it runs | Target coverage / count | Owner |
|-------|------|---------|---------------|-------------------------|-------|
| **Engine unit tests** | Reducer transitions, scoring, state machines, timer semantics (manual clock), undo, log hash chain | Swift Testing (`@Test`, parameterized) | Linux + macOS CI on every PR | 95%+ line coverage of `IWCore` and `IWRules`; every `MatchEvent` has at least one test per legal state | ARCH |
| **Property-based tests for rules** | Invariants: total score bounds; symmetry of shared-answer scoring; normalization idempotence; replay(fold(log)) == state; undo then redo restores state; no sequence of events can reach an impossible state | swift-testing with a small generator library (or `SwiftCheck`) | CI every PR, 1,000 iterations; nightly 50,000 | All invariants listed in `docs/engine-spec/invariants.md` | ARCH/GAME |
| **Replay fixtures** | Real match logs from beta and bug reports, with expected final state | Swift Testing, fixture directory | CI | Grows with every bug; minimum 50 at launch | QA |
| **Dictionary tests** | Lookup correctness vs. golden lists; normalization; fuzzy suggestions; profanity filter never matches allow-listed words; pack signature verification | Swift Testing, golden files | CI | 100% of category lists sampled (1%), full ENABLE validity set once nightly | DATA |
| **Snapshot tests for the design system** | Every component in every state, light/dark, Dynamic Type xSmall/large/accessibility3, Reduce Motion on/off, RTL pseudo-locale | swift-snapshot-testing (pointfreeco) against a fixed simulator (iPhone 16, iOS 18.x) | macOS CI every PR | Full `PreviewGallery` | DESIGN/IOS |
| **Snapshot tests for screens** | Home, lobby, round (each phase), results, settings | same | CI | All screens, 3 type sizes | IOS |
| **UI tests for critical flows** | First launch to first round in under 3 taps; full pass-and-play match; Word Chain elimination; resume after kill; purchase (StoreKit testing configuration); restore purchases; settings toggles persist | XCUITest with accessibility identifiers; StoreKit Testing in Xcode | macOS CI nightly and pre-release | 12 flows | QA |
| **Accessibility audits** | Automated: XCUITest `performAccessibilityAudit()` on every screen (iOS 17+); contrast check on tokens at build time. Manual: VoiceOver script per screen, Switch Control pass, Dynamic Type at accessibility5, Reduce Motion walkthrough | Xcode Accessibility Inspector; XCTest audits; human script | Automated per PR; manual per release candidate | 0 audit failures; manual script signed off by two people | QA/IOS |
| **Performance tests** | Launch time, round transition hitches, dictionary load, memory | `XCTApplicationLaunchMetric`, `XCTOSSignpostMetric`, `XCTMemoryMetric` with baselines | nightly on simulator; weekly on physical devices | Within budgets in Section 4 | IOS |
| **Localization pseudo-locale tests** | Double-length pseudo-locale, RTL pseudo-locale, accented strings; truncation and clipping detection via snapshots | Xcode scheme options (Double-Length Pseudolanguage, Right-to-Left Pseudolanguage) + snapshot tests | CI | 0 clipped strings on supported sizes | QA |
| **Device integration tests** | MultipeerConnectivity 8-device session (Phase 2); Game Center sandbox (Phase 3); haptics timing (video) | manual with scripted scenarios | per release candidate | scripted checklist complete | QA/IOS |
| **Exploratory and "feel" sessions** | 30-minute sessions by **[JOBS]**, **[DESIGN]**, **[GAME]** on device, weekly | none | weekly | notes filed as issues within 24 h | JOBS |

> **[GAME]** Property-based testing of scoring is where I expect to find the embarrassing bugs: a 5-point shared answer that became 10 because one player capitalized differently. The normalization idempotence invariant covers that.
>
> **[QA]** And the "replay(fold(log)) == state" invariant is the multiplayer insurance. If that ever fails we have a desync bug waiting to happen.

**DECISION:** Swift Testing for new tests; XCUITest for UI flows; pointfreeco snapshot testing for the design system; accessibility audits automated per PR and manual per release candidate.

---

## 3. Device and OS matrix

| Tier | Devices (physical, owned) | OS versions | Purpose |
|------|---------------------------|-------------|---------|
| **A: must be flawless** | iPhone 16 Pro (120 Hz), iPhone 15, iPhone SE (3rd gen, 4.7-inch, 60 Hz) | latest iOS 18.x and iOS 26 (current major at launch) | Primary feel and performance targets; small screen; ProMotion |
| **B: must work, minor visual tolerance** | iPhone 11 or XR (oldest common A13 class), iPhone 13 mini (smallest modern), iPhone 16 Plus/Pro Max (largest, 6.9-inch) | iOS 17.x latest point release, iOS 18.x | Lower bound on performance; smallest and largest layouts |
| **C: simulator only** | iPad (any current), iPhone 14, 15 Pro | current | iPad is not a v1 target but must not be broken if the app is run on iPad in compatibility mode; snapshot variety |
| **Accessibility rigs** | Any Tier A device with VoiceOver, Switch Control (external switch), Bold Text, Increase Contrast, Reduce Motion, Dynamic Type accessibility5 | current | Manual audits |

Rules: the oldest supported iOS point release is tested on at least one physical device per release candidate. Each new iOS beta is installed on one Tier B device the week it ships so regressions are found before the public release.

**OPEN:** iPad as a v1 target. **[JOBS]** says no ("one device, perfect"). **[DESIGN]** wants the large-canvas pass-and-play experience. Decision deferred to the UX plan; this matrix keeps iPad in Tier C.

---

## 4. Crash-free and performance budgets

| Metric | Release gate | Measurement |
|--------|--------------|-------------|
| Crash-free sessions | >= 99.8% in TestFlight external beta for 7 days; >= 99.9% target in production at 30 days | Xcode Organizer crashes (opted-in users), MetricKit `MXCrashDiagnostic` |
| Hang rate | < 0.1% of sessions with a hang > 250 ms on the main thread | MetricKit `MXHangDiagnostic`; Organizer Hangs |
| Cold launch p90 | <= 800 ms (target 500 ms) on iPhone SE 3 | MetricKit `applicationLaunchMetrics`, XCTest launch metric |
| Hitches in a round | 0 hitches > 50 ms in a 60 s NPAT round on iPhone 11; hitch ratio < 5 ms/s on Tier A | Instruments Animation Hitches; `MXAnimationMetric` |
| Memory steady | <= 150 MB in a round; no growth across 20 consecutive rounds (leak check) | Instruments Leaks, Allocations |
| Binary download size | <= 40 MB | App Store Connect |
| Battery | Energy impact "Low" for a 10-minute session | Instruments Energy |
| Data loss | 0 lost in-progress matches across 100 scripted force-quits and 20 simulated low-memory terminations | XCUITest with app termination |
| Accessibility audit | 0 failures from `performAccessibilityAudit()` across all screens | XCTest |

> **[IOS]** 99.9% crash-free sounds easy for a small app and it is not. The usual culprits for us will be Swift runtime traps (force unwraps, out-of-range indices in the engine) and SwiftUI state races. The engine is pure so it gets property tests; the UI gets strict concurrency. That is how we buy the 99.9.

---

## 5. Beta program design

TestFlight facts (verified): internal testing supports up to 100 team members with no review; external testing supports up to 10,000 testers and requires a one-time Beta App Review per new version; builds expire 90 days after upload (https://developer.apple.com/testflight/ and App Store Connect Help https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview).

| Stage | Who | Size | Duration | Entry criteria | Exit criteria |
|-------|-----|------|----------|----------------|---------------|
| **Internal alpha** | Team plus founder plus 5 trusted friends added as App Store Connect users | <= 15 | continuous from first playable | Build passes CI gates | n/a |
| **Closed beta 1: "Kitchen table"** | 10 families and friend groups recruited personally (each group 3-6 people; one phone per group) | ~50 people | 3 weeks | Pass-and-play complete; crash-free >= 99.5% internal | 20 matches per group; feel survey median >= 4/5; top 5 issues fixed |
| **Closed beta 2: "Living room"** | Beta 1 groups plus 20 new groups, each with multiple iPhones | ~150 people | 3 weeks | Nearby multiplayer behind flag; Beta App Review passed | 8-device nearby session completes 20 rounds without desync in at least 10 groups; crash-free >= 99.8% |
| **Open beta (public TestFlight link)** | Public link shared in word-game communities and newsletter | up to 2,000 | 4 weeks | Beta 2 exits; product page draft ready | Crash-free >= 99.8% for 7 consecutive days; D7 retention >= 25% among testers who played once; no open P0/P1 |
| **Release candidate** | Everyone above | all | 1 week | All gates | Zero P0/P1; founder sign-off on feel |

Recruiting plan for families and friend groups:
- **[JOBS]**: "Recruit the people who already play this on paper. Parents of 8-14 year olds, college friend groups, board game night hosts." Outreach via personal network, two Reddit communities (r/boardgames, r/wordgames) only once a public link exists, and a landing page with a TestFlight public link.
- Each group gets a one-page "how to run a game night" PDF and a 10-minute onboarding call for the first ten groups.
- Incentive: a permanent "Founding Player" cosmetic ink color in the app (cheap, meaningful, no cash).

Feedback instrumentation:
- TestFlight's built-in screenshot feedback (shake or screenshot) routes to App Store Connect; we triage daily.
- In-app "Send feedback" sheet in beta builds: attaches the match log (anonymized player names), device, OS, `OSLogStore` excerpt from the last 10 minutes, and a one-tap mood (five ink blots from frown to grin). This is a `mailto:` compose, so nothing is sent without the user seeing it.
- Weekly 20-minute video call with two groups, rotating, led by **[DESIGN]** and **[GAME]**.
- Sentry enabled in TestFlight builds only (see `04-...` ADR-011) for symbolicated crashes with breadcrumbs.

> **[KIDS]** Beta groups will include children even though App 1 is not a kids app. Make sure the beta consent note tells parents that, and that the feedback form never asks for a child's name. This also warms up the family network for App 2.
>
> **[QA]** Added to the beta welcome note and the consent language.

---

## 6. App Store Review readiness checklist (mapped to guideline sections)

Canonical source: App Store Review Guidelines, https://developer.apple.com/app-store/review/guidelines/ . Section numbers below are from the current guidelines; the checklist is re-verified against the live page before each submission because Apple revises the document several times a year.

| Guideline section | Topic | What Inkwell must do | Evidence we attach |
|-------------------|-------|----------------------|--------------------|
| **1.2 User-Generated Content** | Apps with UGC need filtering, reporting, blocking, and contact info | Pass-and-play answers and custom categories are user-entered but stay on the device; nearby and Game Center sessions transmit answers to known peers. We still: (a) apply the profanity filter to any displayed text, (b) provide a "report player" path for Game Center matches (Game Center has its own reporting; we link to it), (c) allow blocking via Game Center, (d) list support contact in-app. | Review notes explaining scope of UGC; screenshots of filter and report path |
| **1.3 Kids Category** | Applies to App 2, not App 1 | App 1 is **not** submitted to the Kids Category and does not claim to be "for kids" in metadata. We avoid implying children as the primary audience (which would trigger Kids Category expectations). | Metadata review |
| **2.1 App Completeness** | No placeholders, crashes, broken links; demo account if sign-in | No sign-in in v1. All links live. Review notes include a 2-minute "how to play" video link. | Review notes; QA sign-off |
| **2.3 Accurate Metadata** (2.3.1 hidden features, 2.3.3 screenshots reflect the app, 2.3.7 keywords/titles) | Screenshots must show the actual app; no mention of other platforms; no misleading keywords | Screenshots are captured from the real build (Fastlane `snapshot`); no competitor names in keywords; feature-flagged dark features are not mentioned in metadata | Metadata checklist |
| **2.5.1 Public APIs** | Only public APIs | No private API; SPM dependencies audited (GRDB, snapshot testing is test-only) | Dependency list |
| **2.5.4 Background modes** | Only for their intended purpose | No background modes requested | Info.plist |
| **3.1.1 In-App Purchase** | Digital unlocks must use IAP; prices and content disclosed; restore purchases available | "Pro" unlock and cosmetic ink themes via StoreKit 2 non-consumables; "Restore Purchases" button in Settings; every IAP described in metadata | StoreKit configuration; screenshots of the purchase sheet |
| **3.1.2 Subscriptions** | Not used in v1 | If ever introduced, full 3.1.2 compliance (clear terms, cancellation path) | n/a |
| **3.2.2 Unacceptable business** | No artificially restricting access; no unrelated charges | Pro unlock gates only what it says | Review notes |
| **4.0 Design / 4.2 Minimum Functionality** | Apps must be more than a repackaged website; provide lasting value | Native app with two full games, solo and multiplayer; obviously not a wrapper | n/a |
| **4.3 Spam** | Avoid duplicates of popular apps without differentiation | NPAT and Word Chain apps exist; our differentiation is design quality, multiplayer and accessibility; metadata should articulate this | Product page copy |
| **4.5.4 Push notifications** | Not required for use; no marketing without consent | Phase 3 only: turn reminders via Game Center; no marketing pushes | n/a in v1 |
| **5.1.1 Data Collection and Storage** | Privacy policy link in metadata and in-app; consent for data collection; only request data the app needs | Privacy policy URL on the product page and in Settings; no collection by default; optional diagnostics switch with plain-language explanation | Privacy policy; screenshots of the switch |
| **5.1.2 Data Use and Sharing** | No repurposing or selling; no tracking without ATT prompt | No tracking, no ATT prompt (none needed), no third-party sharing | Privacy label |
| **5.1.4 Kids** | Apps aimed at kids must not include third-party analytics/advertising | App 1 is not aimed at kids; App 2 will comply fully (see App 2 plan) | n/a for App 1 |
| **5.1.5 Location Services** | Not used | No location permission | Info.plist |
| **5.3 Gaming, Gambling, Lotteries** | Not applicable: no real-money prizes, no contests with entry fees | "Founding Player" cosmetic is not a contest with purchase | n/a |
| **Game Center (GameKit guidance)** | Follow Game Center UI conventions, Access Point placement, sign-in handled by system | Phase 3: use `GKAccessPoint`, never custom sign-in | Phase 3 checklist |

> **[IOS]** From experience with reviews: the single most common rejection for apps like ours is 2.1 "we could not complete a purchase" because the reviewer's sandbox hit a StoreKit edge case, and 3.1.1 "restore purchases not found". Both are preventable with a StoreKit Testing configuration in the UI tests and a visible Restore button.
>
> **[QA]** Second most common is 2.3.3 screenshots that show a slightly older UI than the build. Our screenshots are generated from the release candidate build by Fastlane, so they cannot drift.

**DECISION:** This checklist is executed, item by item, with evidence links, in the release ticket for every App Store submission. The live guidelines page is re-read before each submission.

---

## 7. App Privacy nutrition label plan

Source: App privacy details on the App Store, https://developer.apple.com/app-store/app-privacy-details/ ; privacy manifests and required-reason APIs, https://developer.apple.com/documentation/bundleresources/privacy-manifest-files

| Phase | Data types declared | Linked to user | Used for tracking | Notes |
|-------|---------------------|----------------|-------------------|-------|
| **Launch (pass-and-play, solo, IAP)** | **None** ("Data Not Collected") | n/a | No | StoreKit transactions are Apple's; MetricKit/Organizer crash data flows via Apple's opt-in diagnostics, which Apple does not require developers to declare when the developer receives it only through Apple's aggregated channels. Confirm against the current App Privacy details page before submission. |
| **Phase 2 (Nearby)** | None | n/a | No | Display names are exchanged peer-to-peer and never leave the devices or reach us. |
| **Phase 3 (Game Center)** | Game Center data is collected by Apple as part of the Game Center service; the developer declares data *the developer* collects. We collect none. If we add a Sentry/Crashlytics SDK in production: declare "Diagnostics: Crash Data, Performance Data", not linked, not for tracking, plus the SDK's privacy manifest. | Not linked | No | |
| **If optional diagnostics endpoint is enabled** | "Diagnostics" and "Usage Data" (aggregate counters), not linked, no tracking | Not linked | No | Requires an ADR amendment and label update. |

Required-reason API audit: `UserDefaults` (reason CA92.1, app's own preferences), file timestamps if used (C617.1), disk space (none expected), system boot time (none; we use `ContinuousClock`). The app's own `PrivacyInfo.xcprivacy` lists these; GRDB does not require a manifest for our usage but we verify in each update.

**DECISION:** Launch label is "Data Not Collected". Any SDK that would change it needs an ADR.

---

## 8. Export compliance

Source: Complying with Encryption Export Regulations, https://developer.apple.com/documentation/security/complying-with-encryption-export-regulations

- Inkwell uses only Apple-provided encryption (TLS via URLSession, CryptoKit for content pack signature verification and log hashing, Keychain). These are exempt uses.
- Set `ITSAppUsesNonExemptEncryption = NO` in `Info.plist` so App Store Connect skips the per-build compliance questions (and TestFlight builds do not show "Missing Compliance").
- Re-evaluate if we ever add a custom protocol with our own cipher (not planned). Record the reasoning in the release checklist.

---

## 9. Age rating questionnaire expectations

Apple updated the age rating system in 2025: tiers are now 4+, 9+, 13+, 16+ and 18+ (replacing 12+ and 17+), with an expanded questionnaire that developers had to complete by January 31, 2026 to keep submitting updates (reported at https://mjtsai.com/blog/2025/07/28/updated-age-ratings-in-app-store-connect/ and https://ppc.land/apple-updates-app-store-age-ratings-system-with-granular-controls/ ; the authoritative reference is App Store Connect Help, https://developer.apple.com/help/app-store-connect/reference/age-ratings).

Expected answers for App 1:

| Question area | Expected answer | Notes |
|---------------|-----------------|-------|
| Violence, mature themes, profanity | None | Profanity filter on displayed user text; we do not author profane content |
| Gambling, contests | None | |
| Unrestricted web access | No | No web view |
| User-generated content / messaging | Limited: players type words shown to other players in a session; no chat, no public sharing | Likely nudges the rating to 9+ or 13+ depending on how Apple weights "users can share content"; we will answer truthfully and accept the computed rating |
| Medical/wellness | None | |
| Parental controls / in-app controls | n/a for App 1 | |
| In-app purchases | Yes (non-consumable) | Disclosed |
| Loot boxes | None | |

> **[KIDS]** Expect 9+ at minimum because of peer-visible typed words. That is fine for App 1 and is one more reason App 2 is a separate app with no typed sharing between strangers.
>
> **[JOBS]** We answer honestly, we do not game it. A 9+ or 13+ rating on a word game is not a problem. A rejected app is.

**DECISION:** Answer the questionnaire conservatively; do not set a higher-than-computed rating unless legal advice says so.

---

## 10. Release train and versioning

| Element | Decision |
|---------|----------|
| Versioning | Semantic marketing version `MAJOR.MINOR.PATCH` shown to users (1.0.0 at launch); build number is monotonically increasing and set by CI (`CURRENT_PROJECT_VERSION`). |
| Train cadence | **Minor release every 4 weeks** after launch (features behind flags are enabled, not merged, at release time). Patch releases as needed. |
| Branching | Trunk-based: `main` always shippable to TestFlight internal. `release/1.x` cut 1 week before submission; only fixes cherry-picked. Tags `v1.2.0`. |
| Code freeze | 5 working days before submission: feature code frozen; only P0/P1 fixes, metadata and localization. |
| Submission | Submit 3-5 working days before the intended release date with "Manually release this version" so that App Review timing does not dictate launch day. |
| Release notes | Written by **[JOBS]** or **[DESIGN]**, in the product's voice, under 400 characters, no "bug fixes and improvements". |

Release gates (all must be green in the release ticket): CI green on `release/*`; snapshot diffs reviewed by **[DESIGN]**; accessibility manual script signed by two people; performance baselines within budget on Tier A and B devices; zero P0/P1; App Store checklist (Section 6) complete; privacy label unchanged or ADR attached; screenshots regenerated; founder feel sign-off on a device.

---

## 11. Staged rollout and phased release

App Store Connect supports **phased release for automatic updates over 7 days**: day 1: 1%, day 2: 2%, day 3: 5%, day 4: 10%, day 5: 20%, day 6: 50%, day 7: 100% of users with automatic updates; anyone can still manually update from the App Store; the release can be paused for up to 30 days (https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases).

Policy:
- **1.0.0 launch**: phased release does not apply to a first release (there is nothing to update from), so launch is all-at-once. Mitigation is the beta program plus a soft launch window (Section 14).
- **Every update**: phased release ON. Watch crashes and hangs daily in Organizer and MetricKit. Pause if crash-free drops below 99.5% or if a P0 is confirmed. Resume or supersede with a hotfix.
- **Feature flags as the second dial**: new transports (Nearby, Game Center) ship dark and are enabled through the signed remote config (Phase 2) for 10%, 50%, 100% of launches, independent of the binary rollout.

---

## 12. Hotfix process

| Step | Owner | Time target |
|------|-------|-------------|
| 1. Confirm P0 (crash on launch, data loss, purchase failure, security) from Organizer/MetricKit/Sentry(beta)/support | QA | within 2 h of signal |
| 2. Pause phased release (if in progress); if a flag can disable the broken feature, flip it first | IOS | within 2 h |
| 3. Branch `hotfix/1.x.y` from the release tag; fix with a regression test (replay fixture if gameplay) | IOS/ARCH | 4-24 h |
| 4. Build via Xcode Cloud; TestFlight internal smoke on Tier A devices (15-minute script) | QA | 1 h |
| 5. Submit with **expedited review request** (App Store Connect "Request Expedited App Review"; Apple grants at its discretion for critical bugs, https://developer.apple.com/contact/app-store/?topic=expedite) and clear review notes | QA | same day |
| 6. Release manually when approved; phased release OFF for a hotfix that fixes a P0 (we want 100% immediately), ON otherwise | QA | on approval |
| 7. Post-mortem within 3 working days; add the gate that would have caught it | QA + whoever fixed it | 3 days |

> **[ARCH]** The ability to flip a flag before shipping a binary is the reason the signed remote config exists. For 1.0 we do not have it yet, so the launch build has fewer dark features and the kill switches are compile-time. That is acceptable for a build that was in beta for ten weeks.

---

## 13. App Store product page plan

Requirements (verified for 2025-2026): the 6.9-inch iPhone screenshot size (1320 x 2868 px portrait) is the required base for new submissions and scales down to smaller devices; app previews must be 15-30 seconds, H.264, and match the device resolution; up to 10 screenshots and 3 previews per device size (App Store Connect Help screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications ; preview specifications: https://developer.apple.com/help/app-store-connect/reference/app-preview-specifications).

### 13.1 Screenshot story (10 frames, in order)

| # | Frame | Caption (draft, **[JOBS]** to edit) |
|---|-------|--------------------------------------|
| 1 | Letter reveal mid-ink-bleed, timer ring at 0:52 | "Name. Place. Animal. Thing. Go." |
| 2 | Privacy badge frame: "No account. No tracking. Nothing collected." | "Your words stay on your phone." |
| 3 | Pass-and-play hand-off screen with four player ink colors | "One phone, the whole table." |
| 4 | Results screen with shared-answer highlighting (two players wrote "Lion") | "Same answer? Half the points. House rules." |
| 5 | Word Chain in Countries, chain of five | "Chain words. Don't repeat. Don't stall." |
| 6 | Custom categories sheet (Movies, Foods, Brands, your own) | "Your categories, your rules." |
| 7 | Dynamic Type at accessibility3 with VoiceOver focus ring visible | "Built to be played by everyone." |
| 8 | Nearby lobby with 6 phones discovered (Phase 2 only) | "Nearby play. No Wi-Fi password, no sign-in." |
| 9 | Ink themes (Pro) | "Pick your ink." |
| 10 | Reduce Motion / calm variant of the round screen | "Calmer mode, same game." |

Preview video (one, 25 seconds): cold open on the letter reveal, three quick answers typed with haptic ticks visible as ink ripples, round ends, results animate, cut to pass-and-play hand-off, end card with the name. No voice-over; captions burned in; music optional and quiet.

### 13.2 Keywords and copy

- Title (30 chars): product name plus a differentiator ("Inkwell: Word Party Games" is 25 chars; name is OPEN per the naming section elsewhere).
- Subtitle (30 chars): "Name Place Animal Thing & more".
- Keyword field (100 chars): `name place animal thing,word chain,party game,pass and play,family game,scattergories,word game,offline`. Note: competitor trademarks in keywords are a 2.3.7 risk; "scattergories" is a trademark of Hasbro and must **not** be used. Replace with "categories game".
- Description: first two lines carry the privacy and offline promise; then the two games; then multiplayer; then accessibility; then what Pro unlocks.
- Promotional text (170 chars, editable without a build): used for launch-month notes.

### 13.3 Localization of the listing

v1 ships English (US) listing only, plus English (UK) and English (Australia) copies with spelling adjusted. Listing localization for other languages waits for App 3 content. Screenshots are generated by Fastlane `snapshot` per locale so they can be regenerated in one command.

> **[DESIGN]** Screenshot 2 (the privacy badge) is a design frame, not a UI frame. Guideline 2.3.3 says screenshots should show the app in use, but Apple allows marketing framing as long as it is not misleading. We will keep the real Settings privacy screen visible inside the frame to be safe.
>
> **[JOBS]** Frame 1 must make someone feel the ink. If the still does not do that, we have the wrong frame.

---

## 14. Launch-day runbook

**T-14 days:** Release candidate tagged; App Store checklist complete; submit for review with manual release; product page final; support inbox and FAQ live; press kit (icon, screenshots, 2-paragraph description) in a public folder.

**T-7 days:** Review approved (if not, triage and resubmit; if it slips, launch date moves, not quality). Soft launch consideration: release first in 2-3 smaller English-speaking storefronts (for example New Zealand and Ireland) for 5 days using App Store Connect's country availability; watch crashes. **[JOBS]** objection noted below.

**T-1 day:** Verify IAP products are "Approved" and attached to the version; verify privacy label; verify the age rating; verify the support URL and privacy policy URL respond; freeze social copy; charge the devices.

**T-0 (launch day):**
1. 08:00 local: press "Release this version". Confirm the App Store listing renders on two devices (cache may take an hour).
2. Install from the App Store (not TestFlight) on Tier A devices; run the 15-minute smoke script including a real purchase and restore.
3. Post launch message (newsletter, social, communities); the TestFlight beta list gets a thank-you with the Founding Player note.
4. Monitor hourly: Organizer crashes, App Store Connect sales and downloads, ratings and reviews, support inbox.
5. 18:00: launch-day summary to the team; decide whether anything warrants a hotfix start.

**T+1 to T+7:** Daily 15-minute stand-up on metrics and reviews; reply to every review (App Store Connect allows developer responses); fix P1s into 1.0.1.

> **[JOBS]** I hate soft launches. They are a way of shipping without committing. If the beta did its job we do not need New Zealand to tell us what we already know.
>
> **[QA]** The beta tests the app; the soft launch tests the *store*: IAP in production, the listing, the ratings prompt, the review pipeline. Five days in two storefronts costs nothing and has caught production-only purchase bugs on every app I have shipped.
>
> **[JOBS]** Five days, two storefronts, and if it is clean we go worldwide on day six. Not a week later.

**DECISION:** 5-day soft launch in two small storefronts, then worldwide. Manual release control throughout.

---

## 15. Post-launch monitoring

| Signal | Source | Cadence | Alert threshold |
|--------|--------|---------|-----------------|
| Crashes, hangs, launch time, hitches, energy | Xcode Organizer; MetricKit payloads (https://developer.apple.com/documentation/metrickit) | daily; hourly on launch day and during phased rollouts | crash-free < 99.5% or any new crash signature > 0.1% of sessions |
| Downloads, sessions, retention (opt-in users), conversion to Pro | App Store Connect App Analytics | daily | Pro conversion < 2% at 14 days triggers a pricing/placement review, not a redesign |
| Ratings and reviews | App Store Connect | daily; reply within 48 h | average < 4.5 after 100 ratings triggers a theme review |
| Support volume and themes | support inbox (tagged) | daily | any theme with > 5 reports/week becomes a tracked issue |
| TestFlight beta crashes with breadcrumbs | Sentry (beta builds only) | daily | n/a (beta) |
| Dictionary complaints ("X should be valid") | in-app "suggest a word" (mailto) | weekly batch by **[DATA]** | > 20/week for one category triggers a content pack update |

A 30-day post-launch review decides: Sentry in production (ADR-011), the first content pack update, and the 1.1 feature set from the flagged dark features.

---

## 16. Support and feedback loop

- Support channel: a single email address plus an in-app "Help" sheet with a 10-question FAQ and a "Send feedback" action that pre-fills device, version and (with the user's consent, shown in the compose window) the last match log.
- Response SLO: 48 hours for every message; same-day for purchase problems.
- Review replies: every App Store review gets a reply within 48 hours; negative reviews about a confirmed bug get a follow-up reply when the fix ships.
- Word disputes: "Suggest a word" feeds the content pack backlog; accepted words ship in the next pack with a note in release notes ("Added 212 words you suggested, including 'axolotl' and 'Timbuktu'").
- Rating prompt: `SKStoreReviewController.requestReview` (or the SwiftUI `requestReview` environment action) at most once per version, only after a completed match with a positive outcome signal (the player tapped "Play again"), never during a round, never on first launch.

> **[GAME]** The "words you suggested" release note is the cheapest loyalty loop we have. People love seeing their word get in.

---

## 17. The "perfect app" quality bar (48 items)

Every item is checked on a physical Tier A device before each release. Owners in brackets.

**First run and navigation**
1. First launch to first letter drawn in three taps or fewer, no account, no permission prompts. [JOBS]
2. Cold launch under 800 ms p90 on iPhone SE 3; no splash screen that lingers after content is ready. [IOS]
3. No onboarding carousel; the first screen is the game. Help is discoverable, not forced. [DESIGN]
4. Every screen has exactly one primary action, visually unmistakable. [DESIGN]
5. The back/close affordance is always in the same place; a round has no back, only "Quit" with confirmation. [DESIGN]
6. State survives force-quit, phone call, low memory, and iOS update mid-round, with the remaining time preserved. [ARCH]

**Feel and motion**
7. Every animation has a Reduce Motion alternative, and the alternative is designed, not just disabled. [DESIGN]
8. No hitch above 50 ms during a round on iPhone 11. [IOS]
9. 120 Hz where available; animations use spring curves from the token file, never ad hoc durations. [IOS]
10. Haptics and visuals land in the same frame (verified by slow-motion video for the letter reveal and final ticks). [IOS]
11. Haptics respect the system setting and the in-app toggle; no haptic while the device is in a call. [IOS]
12. Sounds are off by default in silent mode and never override music playback. [IOS]
13. Keyboard appears without a layout jump; the text field is focused when the round starts; return key behavior is consistent. [IOS]
14. The last five seconds of a timer feel different and are announced for VoiceOver users. [GAME]

**Correctness of play**
15. Scoring matches the stated rules in every variant; property tests pass at 50,000 iterations nightly. [GAME]
16. Shared-answer detection is case-, whitespace-, diacritic- and punctuation-insensitive and shown transparently on the results screen. [DATA]
17. Undo is available in pass-and-play and shows who undid what. [GAME]
18. Unknown words never silently pass or fail; the player always sees the verdict path (vote, insist, or reject). [GAME]
19. Letter draw respects exclusions and never repeats within a match unless the rules say so. [GAME]
20. Word Chain enforces "last letter equals first letter" with clear handling of silent letters and digraphs per the rule set. [DATA]
21. Timer drift between nearby devices under 100 ms after a 60-second round. [ARCH]
22. A disconnected peer can rejoin a nearby match and receive the full log without the host restarting. [ARCH]

**Accessibility**
23. Zero failures from automated accessibility audits on every screen. [QA]
24. Every interactive element has a label, a value where relevant, and a hint only when it adds information. [IOS]
25. VoiceOver can play a full match without sighted help (scripted test, two people sign off). [QA]
26. Dynamic Type from xSmall to accessibility5 with no clipped or overlapping text; layouts switch to list mode above accessibility1. [DESIGN]
27. All text and essential UI meet WCAG AA contrast in light, dark, and Increase Contrast modes; validated at build time. [DESIGN]
28. Color is never the only channel for valid/invalid/shared. [DESIGN]
29. Tap targets at least 44 x 44 pt; focus order sensible for Switch Control and Full Keyboard Access. [IOS]
30. Timers never auto-advance past a screen that needs input without a focusable control. [IOS]

**Content and language**
31. Profanity filter applied to any displayed user text; allow-list prevents false positives on real words (for example "Scunthorpe"). [DATA]
32. Base dictionary and category lists ship with attribution and licenses visible in Settings > About. [DATA]
33. Every user-facing string is localized through String Catalogs; pseudo-locale and RTL snapshot tests pass. [QA]
34. No lorem ipsum, placeholder icons, or TODO strings in the binary (lint rule). [QA]
35. Copy is written in the product's voice; no system-default alert text where a sentence would be kinder. [DESIGN]

**Commerce and privacy**
36. Pro purchase and restore work in sandbox, TestFlight and production; the price shows in the user's currency from StoreKit, never hard-coded. [IOS]
37. Everything paid is described before the purchase sheet; nothing is paywalled by surprise mid-round. [JOBS]
38. Privacy label is "Data Not Collected" and the app's behavior matches it; no network calls at all in pass-and-play (verified with a proxy). [ARCH]
39. Privacy policy is one page, plain language, and reachable in two taps. [QA]
40. `ITSAppUsesNonExemptEncryption` set; privacy manifest present; required-reason APIs declared. [IOS]

**Robustness**
41. Crash-free sessions above 99.8% in beta for 7 days before submission. [QA]
42. No force unwraps in `IWCore`, `IWRules`, `IWContent` (lint rule); strict concurrency with zero warnings. [ARCH]
43. Database migrations tested from every shipped schema version to current. [ARCH]
44. Works fully in Airplane Mode; no network error UI ever appears in local modes. [ARCH]
45. Memory flat across 20 consecutive rounds; no leaks in Instruments. [IOS]
46. Binary download size under 40 MB. [IOS]

**Store presence**
47. Screenshots and preview are generated from the release build and match it exactly. [QA]
48. App icon reads at 29 pt and 1024 pt; no text in the icon; dark and tinted icon variants provided. [DESIGN]

> **[JOBS]** Forty-eight items. If any one of them is red, we do not ship, and I do not want a meeting about it. The meeting is this document.
>
> **[QA]** Agreed, with one amendment: items 7, 23, 25, 36, 38 and 41 are "hard red" (no exceptions). The rest can be waived by the founder in writing, once, with the waiver recorded in the release ticket.
>
> **[JOBS]** Fine. I will not use the waiver.

**DECISION:** 48-item bar adopted; six items are non-waivable.

---

## 18. Risk register (quality and release)

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|-----------|-------|
| App Review rejection on 2.1 or 3.1.1 around purchases | Medium | Medium (1-2 week slip) | StoreKit Testing in UI tests; Restore button; review notes with video; submit two weeks early | QA |
| Beta recruiting falls short (fewer than 30 groups) | Medium | Medium | Start recruiting at first playable, not at beta start; founder's network; public link in open beta | JOBS |
| Accessibility regressions late in a release | Medium | High (hard red) | Automated audits per PR; manual script per RC; snapshot tests at accessibility sizes | QA |
| iOS major release in September breaks a SwiftUI behavior before our launch | Medium | High | Beta OS on a Tier B device from the first developer beta; UIKit escape hatches | IOS |
| Crash triage too slow without a production crash SDK | Medium | Medium | Phased release with pause; Sentry pre-wired; 30-day review | QA |
| Trademark complaint over keywords or naming | Low | High | No competitor marks in metadata; naming legal check before launch | JOBS |
| Phased rollout masks a bug that affects only a cohort (old devices) | Low | Medium | Tier B devices in the smoke script; cohort view in Organizer | QA |

---

## 19. Decisions and open questions

**DECISIONS**
- Test pyramid as in Section 2; Swift Testing, XCUITest, pointfreeco snapshots; accessibility audits automated per PR and manual per RC.
- Device matrix Tiers A/B/C; iPad in Tier C for v1.
- Budgets: crash-free 99.8% beta gate, 99.9% production target; cold launch 800 ms p90; zero hitches over 50 ms in a round on iPhone 11.
- Beta program in four stages with family and friend-group recruiting; Sentry in TestFlight builds only.
- App Store checklist executed with evidence per submission; live guidelines re-read each time.
- Privacy label "Data Not Collected" at launch; `ITSAppUsesNonExemptEncryption = NO`.
- Four-week minor release train; trunk-based; manual release; phased release on every update; hotfix process with expedited review.
- Five-day soft launch in two storefronts, then worldwide.
- 48-item quality bar with six non-waivable items.

**OPEN**
- iPad as a v1 target (UX plan decides).
- Final app name and keyword set (naming section elsewhere; legal check pending).
- Whether Apple's age rating questionnaire computes 9+ or 13+ given peer-visible typed words; accept the result.
- Sentry in production after the 30-day review.
- Whether the ratings prompt should be shown at all in 1.0 (**[JOBS]** leans no: "earn it in reviews we did not ask for"; **[QA]** notes that the prompt measurably raises rating volume and that a 4.8 with 2,000 ratings is a feature).

---

## 20. Sources

- App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- TestFlight overview: https://developer.apple.com/testflight/ ; App Store Connect Help, TestFlight: https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview
- Release a version update in phases: https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases
- App privacy details on the App Store: https://developer.apple.com/app-store/app-privacy-details/
- Privacy manifest files and required-reason APIs: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- Complying with encryption export regulations: https://developer.apple.com/documentation/security/complying-with-encryption-export-regulations
- Age ratings reference (App Store Connect Help): https://developer.apple.com/help/app-store-connect/reference/age-ratings ; coverage of the 2025 change: https://mjtsai.com/blog/2025/07/28/updated-age-ratings-in-app-store-connect/ and https://ppc.land/apple-updates-app-store-age-ratings-system-with-granular-controls/
- Screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications ; app preview specifications: https://developer.apple.com/help/app-store-connect/reference/app-preview-specifications
- Expedited App Review request: https://developer.apple.com/contact/app-store/?topic=expedite
- MetricKit: https://developer.apple.com/documentation/metrickit ; MXMetricPayload: https://developer.apple.com/documentation/metrickit/mxmetricpayload
- Xcode Cloud (25 compute hours included): https://developer.apple.com/xcode-cloud/get-started/
- Sentry vs Crashlytics comparison (vendor-authored, read critically): https://sentry.io/resources/sentry-vs-crashlytics-mobile-developers-guide/
- Human Interface Guidelines, Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- swift-snapshot-testing: https://github.com/pointfreeco/swift-snapshot-testing
- Swift Testing: https://developer.apple.com/documentation/testing
