# 10. Phase 0 Kickoff Package (App 1, "Inkwell")

**Document status:** Draft v0.1, 2026-10-04, owner persona: **[ARCH — Principal Architect, "Priya Raman"]**, co-owned by **[QA — Lena Fischer]** (gates and test tooling) and **[IOS — Marcus Oyelaran]** (Xcode, signing, TestFlight). Contributions from JOBS, DESIGN, DATA, GAME.

**Read this if...** the founder has signed off, or is about to, and you need to know what happens on Monday morning. This is the "day one" package. It turns the delivery plan (03), the architecture (04), the quality plan (05) and the design foundations (07, 09) into a checklist of accounts, settings, folders, scripts and Friday demos for the first six weeks: Phase 0 (W1 to W2) and Phase 1 (W3 to W6). Nothing here introduces a new product decision; where a decision is the founder's, Section 2 lists it with the team's recommendation and a blank column. Kickoff is assumed to be Monday 2026-10-12, matching the Gantt in 03 Section 12.

## Table of contents

1. How to use this package
2. Founder sign-off sheet
3. Accounts and tooling setup checklist
4. Repository skeleton and dependency rules
5. Week-by-week plan for Phase 0 and Phase 1
6. The first three Friday demos in detail
7. Engineering conventions
8. Content pipeline bootstrap (W1 to W3)
9. Design bootstrap and the W4 direction gate
10. Risks specific to the first four weeks
11. Team debates
12. Decisions and open questions
13. Sources

---

## 1. How to use this package

Print Section 2 and get it signed. Work through Section 3 on the founder's MacBook in the order written; most steps depend on the one above. Section 4 is what the repository looks like at the end of day two. Sections 5 and 6 are the calendar. Sections 7 to 9 are the rules the team works by from the first commit. Section 10 is what to watch.

> **[JOBS]** This is the only document in the folder I want to be boring. If a page here is interesting, something upstream was not decided.
>
> **[ARCH]** Boring on purpose. Every step here has been done before. The risk is not difficulty, it is forgetting one.

---

## 2. Founder sign-off sheet

The twelve decisions from the register (00-DECISIONS-AND-OPEN-QUESTIONS.md, Section 5) with the team recommendation repeated. Phase 0 can start with F1 to F6 and F11 signed; the rest are needed by the end of W2 because they shape Phase 1 planning and the device purchase.

| # | Decision | Team recommendation | Needed by | Founder choice / date |
|---|---|---|---|---|
| F1 | App 1 name | Keep Inkwell; trademark attorney in W1; reserve the App Store Connect record; fallbacks Nib, Letterhead, Foolscap in order | W1 Mon | |
| F2 | App 1 business model | Free plus one-time Pro via StoreKit 2; no ads, subscription or consumables | W1 Mon | |
| F3 | Pro price and intro price | $6.99 with a $4.99 launch price for four weeks; confirm after the Phase 5 beta | W2 Fri | |
| F4 | iOS minimum | iOS 17.0 for 1.0; re-evaluate at 1.1 | W1 Mon | |
| F5 | Default visual direction | Paper & Ink as identity, confirmed on device at W4 against Night Lounge; Swiss Editorial free, Night Lounge Pro, Playful Pop parked, Quiet Minimal skeleton | W1 Mon provisional, W4 Fri confirmed | |
| F6 | Theme scope for 1.0 | Paper & Ink and Swiss Editorial in 1.0; Night Lounge reduced to tokens and sound or moved to 1.1 | W2 Fri | |
| F7 | Online multiplayer in v1 | Yes, async over Game Center in Phase 5 behind Pro, Word Chain first, pre-approved as the first cut | W2 Fri | |
| F8 | Nearby multiplayer in v1 | Yes in Phase 4 behind Pro, contingent on the W5 to W6 spike; four-device cap rather than slip | W2 Fri | |
| F9 | Kids app name | Inkling if clean, "Kids" in the subtitle; else Inkwell Kids; never "Jr." | W2 Fri | |
| F10 | Kids app pricing | Paid up front, Family Sharing on, no IAP in v1 | W2 Fri | |
| F11 | Date versus scope | Fixed W23 submission; scope flexes through the ordered cut list in 03 Section 18 | W1 Mon | |
| F12 | Second engineer commitment | 100 percent in Phases 4 and 5, or accept today that nearby or async will be cut | W2 Fri | |

Signature: ______________________ (founder), date __________. The signed sheet is scanned into `docs/decisions/` and referenced from ADR-000 (Section 7.3).

> **[JOBS]** I will sign F1 to F6 and F11 on day one. F12 I will sign honestly, which may mean signing the cut. Better to know in week two that NPAT async is gone than to discover it in week nineteen.

---

## 3. Accounts and tooling setup checklist

Assumes one Apple silicon MacBook, a paid Apple Developer Program membership with the founder as Account Holder, and a GitHub organization. Steps are in dependency order; each names an owner and a check.

### 3.1 Apple Developer account, identifiers and the bundle ID strategy

| # | Step | Owner | Done when |
|---|---|---|---|
| 1 | Founder confirmed as Account Holder; IOS added as Admin, ARCH as Developer, QA as App Manager in App Store Connect Users and Access; two-factor on every account | Founder | Invitations accepted |
| 2 | Register explicit App IDs for App 1 and App 2 under Certificates, Identifiers and Profiles, with Game Center and In-App Purchase enabled on App 1 (https://developer.apple.com/help/account/identifiers/register-an-app-id/) | IOS | Identifiers visible in the portal |

**Bundle ID strategy.** Apple states that once a build has been uploaded to App Store Connect the bundle ID cannot be changed; a new record would be needed (https://developer.apple.com/documentation/xcode/changing-the-bundle-identifier). The marketing name is still pending a trademark search, so the identifier must not carry it. The team's recommendation is a neutral reverse-DNS identifier on a domain the founder controls: `com.<founderdomain>.npat` for App 1 and `com.<founderdomain>.npatkids` for App 2. TestFlight builds use the same bundle ID as the App Store build because TestFlight distributes builds of the same app record; there is no separate beta identifier. Local Debug builds that need to sit next to a TestFlight build on one phone use a third explicit App ID with a `.dev` suffix, never uploaded.

### 3.2 App Store Connect records

| # | Step | Owner | Done when |
|---|---|---|---|
| 3 | Create the App 1 record: platform iOS, name "Inkwell" (availability is checked at creation), primary language English (U.S.), bundle ID from step 2, SKU `INKWELL-IOS-001`. The SKU cannot be changed later; the primary language can (https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app/ and https://developer.apple.com/help/app-store-connect/reference/app-information/app-information/). If the name is taken, try Nib, Letterhead, Foolscap per F1 and record the outcome in ADR-000 | IOS with founder | Record exists; name outcome known |
| 4 | Create the App 2 record with the F9 working name so it is reserved; leave it empty | IOS | Record exists |
| 5 | Enable Game Center on the App 1 version in App Store Connect and add the Game Center capability in Xcode's Signing and Capabilities tab (https://developer.apple.com/help/app-store-connect/configure-game-center/overview-of-game-center/) | IOS | Entitlement present |
| 6 | Create one non-consumable, product ID `com.<founderdomain>.npat.pro`, at the F3 price; mirror it in a local `Inkwell.storekit` configuration so purchase flows run offline (StoreKit Testing in Xcode, https://developer.apple.com/videos/play/wwdc2020/10659/) | IOS | A StoreKitTest unit test purchases Pro |
| 7 | Draft App Privacy answers as "Data Not Collected" per ADR-012; do not submit | QA | Draft saved |
| 8 | TestFlight groups: `Team` and `Lab Devices` (internal), `Friends and Family`, `Beta 1`, `Beta 2` (external, empty until Phases 2 and 5). Apple allows up to 100 internal and 10,000 external testers per app (https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/) | QA | Five groups visible |

### 3.3 Xcode, signing and the MacBook

| # | Step | Owner | Done when |
|---|---|---|---|
| 9 | Install the current release Xcode. At the time of writing Apple's SDK table lists Xcode 26.x, which requires macOS Sequoia 15.6 or later and ships the Swift 6.2 compiler with Swift 6 language mode (https://developer.apple.com/xcode/system-requirements/). Pin the exact version in `docs/runbooks/toolchain.md` and select the same version in every Xcode Cloud workflow | IOS | `xcodebuild -version` recorded |
| 10 | Sign in to Xcode with the Admin account; enable "Automatically manage signing" on both targets. Xcode creates certificates and profiles as needed; no manual profiles (https://developer.apple.com/help/account/provisioning-profiles/create-a-development-provisioning-profile/) | IOS | Debug build installs on the founder's iPhone |
| 11 | Register the lab devices from 03 Section 4 (iPhone SE 2nd gen, iPhone 12, iPhone 15 or newer, one iPad, the founder's phone) | IOS | All run the W1 build |
| 12 | Homebrew, then `swiftlint`, `swiftformat`, `gh`, `python@3.12`, `uv`; versions in the toolchain runbook | ARCH | `make doctor` passes |
| 13 | `PrivacyInfo.xcprivacy` in the app target: no tracking, no tracking domains, required-reason entries only for APIs actually used (https://developer.apple.com/documentation/bundleresources/privacy-manifest-files) | QA | Archive validates clean |

### 3.4 CI: Xcode Cloud plus GitHub Actions, as decided in ADR-014

04 Section 18 decided a hybrid. Xcode Cloud builds the app, runs the iOS test plan and uploads TestFlight; the Developer Program includes 25 compute hours per month, with 100 hours at US$49.99 per month if exceeded (https://developer.apple.com/xcode-cloud/get-started/). GitHub Actions Linux runners build and test the platform-pure packages on every pull request.

| # | Step | Owner | Done when |
|---|---|---|---|
| 14 | Connect the repository to Xcode Cloud from Xcode's Integrate menu; grant the Xcode Cloud GitHub app access to this one repository | IOS | First build runs |
| 15 | Workflow "PR Verify": start on Pull Request Changes targeting `main`; Build and Test with the `Inkwell-PR` plan (unit, snapshot, accessibility audits); no archive (https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions) | IOS | Green check on a test PR |
| 16 | Workflow "Main to TestFlight": start on Branch Changes to `main`; Build, Test, Archive as "TestFlight (Internal Testing Only)"; post-action distribute to `Team` and `Lab Devices` (https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution) | IOS | Build in TestFlight after one merge |
| 17 | Workflow "Nightly": scheduled on `main`; `Inkwell-Nightly` plan (UI smoke tests on SE 3rd gen and iPhone 16 simulators, performance baselines) | QA | First result reviewed Tue W2 |
| 18 | Workflow "Release": start on tag `release/*`; archive as "TestFlight and App Store"; external groups as post-action; dry run with a throwaway tag in W2 | QA | Dry run passes |
| 19 | `ci_scripts/ci_post_clone.sh` installs SwiftLint and runs the token generator so Xcode Cloud sees generated Swift (custom build scripts, https://developer.apple.com/videos/play/wwdc2021/10269/) | ARCH | Script output in a build log |
| 20 | GitHub Actions `packages-linux.yml`: `swift build` and `swift test` for `IWCore`, `IWRules`, `IWContent` on `ubuntu-latest` with the Swift 6.2 container; `content-pack.yml`: builds the English pack, checks budgets, runs golden tests; `lint.yml`: SwiftLint, SwiftFormat `--lint`, token generator diff | ARCH, DATA | All green on PR #1 |
| 21 | Monthly reminder to read Xcode Cloud usage; alarm at 20 of 25 hours | QA | Reminder exists |

### 3.5 GitHub repository settings

| Setting | Value |
|---|---|
| Default branch | `main`, trunk-based per 05 Section 10 |
| Ruleset on `main` | Pull request required, one approval, dismiss stale approvals, conversation resolution required, no force push, no deletion (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) |
| Required status checks | `linux-packages`, `content-pack` (skipped counts as passing when `Content/` is untouched), `lint`, and the Xcode Cloud "PR Verify" check; branches must be up to date (strict) |
| Ruleset on `release/*` | Same, plus pushes restricted to QA and IOS |
| Merge method | Squash only; PR title becomes the commit subject |
| Issue templates | `bug.md` (match log attachment required), `feel-note.md` (weekly feel session output, 05 Section 2), `adr-proposal.md` |
| Labels | `phase-0` to `phase-7`, `skunkworks`, `cut-list`, `a11y`, `perf`, `feel`, `content` |

### 3.6 Code quality tooling

| Tool | Configuration | Enforced where |
|---|---|---|
| SwiftLint (https://github.com/realm/SwiftLint) | `.swiftlint.yml`: `force_unwrapping` and `implicitly_unwrapped_optional` as errors; `todo` must carry an issue number; custom rules `no_literal_color` and `no_literal_duration` outside `IWDesignSystem`, `no_dispatch_queue` everywhere, `forbidden_import` per Section 4.1 (ADR-009, ADR-015) | Pre-commit hook and the `lint` job |
| SwiftFormat (https://github.com/nicklockwood/SwiftFormat) | `.swiftformat`: 2-space indent, width 120, `--wraparguments before-first`; `--lint` mode in CI | Same |
| swift-snapshot-testing (https://github.com/pointfreeco/swift-snapshot-testing) | Pinned minor version; reference device iPhone 16, iOS 18.x simulator per 05 Section 2; references under `Tests/Snapshots`; CI fails on a missing snapshot rather than recording | Xcode Cloud "PR Verify" |
| Swift Testing (https://developer.apple.com/documentation/testing) | `@Test`, `#expect`, `#require`, parameterized tests for everything new; XCTest only for XCUITest flows and `measure` blocks | All test targets |
| Token generator | `Design/tools/gen-tokens.py` reads `Design/tokens.json`, writes `Tokens.swift` and an asset catalog; CI fails if generated output differs from committed output | `lint` job, `ci_post_clone.sh` |

### 3.7 Design, motion and sound tooling

| Tool | Phase 0 setup | Owner |
|---|---|---|
| Figma (Professional, variables and Dev Mode) | One project "Inkwell", four files: `00 Foundations` (primitive and semantic variables, type ramp, spacing, radius, elevation, icon grid), `01 Components` (the 31 components from 07 Section 12 with state matrices), `02 Screens App 1` (pages per screen family), `03 Directions` (one page per direction, used at the W4 gate). Variables export to `Design/tokens.json` (https://help.figma.com/hc/articles/15023124644247) | DESIGN |
| Rive (free tier) | Account in W2; one file "M01 letter" for the W7 to W8 bake-off (09 Section 5.3). No runtime in the app until the bake-off decides (https://rive.app/docs/runtimes/apple) | DESIGN |
| Lottie (LottieFiles free tier, After Effects trial) | Account in W2; used only for the bake-off comparisons; `lottie-ios` not added before the bake-off (https://github.com/airbnb/lottie-ios) | DESIGN |
| Principle or Origami Studio | Installed W2 for timing studies (09 Section 9.1) | DESIGN |
| Sound and haptics | `Design/sound/` with the three directions from 09 Section 6; clips named `s_<role>_<theme>.wav`, peak -1 dBTP, under 400 ms except the ambient bed; AHAP files in `Design/haptics/` keyed by role (Core Haptics, https://developer.apple.com/documentation/corehaptics) | DESIGN with IOS |
| Fastlane | Local only, `snapshot` and `deliver`, from Phase 5 (ADR-014) | QA |

---

## 4. Repository skeleton and dependency rules

The layout is 04 Section 19 made exact, created on day one by ARCH with placeholder public APIs and one passing test per package so the "CI green on a PR touching every package" exit criterion is testable from the start. Content sources and build scripts live in the same mono-repo under `Content/`; there is no separate content repository in v1, because the pack build is a CI job that must version with the engine that reads it.

```
inkwell/
  Inkwell.xcworkspace          # the only thing you open
  Makefile                     # doctor, lint, gen-tokens, pack, test-linux
  Apps/
    Inkwell/                   # App 1 target: entry, AppRouter, DI wiring, PrivacyInfo.xcprivacy, Inkwell.storekit
    InkwellKids/               # App 2 target, created empty in W2 so the record and bundle ID exist
  Packages/
    IWCore/                    # MatchState, MatchEvent, reducer, state machines, scoring, ledger, replay (Foundation only)
    IWRules/                   # presets and house rules for NPAT and Word Chain, validators
    IWContent/                 # DAWG and list loading, normalization, validation, fuzzy, profanity, pack manifest
    IWDesignSystem/            # generated tokens, components, haptics abstraction, Reduce Motion alternatives, PreviewGallery
    IWPersistence/             # GRDB MatchStore, migrations, settings, pack registry
    IWMultiplayer/             # LocalTransport now; NearbyTransport and GameCenterTransport later
    IWAnalytics/               # first-party aggregate counters, local only
    IWFeatureFlags/            # typed flags, debug menu
    IWFeatures/                # HomeFeature, NPATFeature, WordChainFeature, ResultsFeature, SettingsFeature, LobbyFeature
  Content/
    sources/                   # raw lists (ENABLE, SCOWL, WordNet, GeoNames), licenses, curation CSVs
    tools/                     # Python: fetch, normalize, build_dawg, build_list, curate, sign, measure
    packs/                     # built, signed packs (en-base from W3); never hand-edited
    golden/                    # DATA's 500-answer golden set with expected states
  Design/
    tokens.json                # Figma variables export, single source for color, type, spacing, motion
    tools/gen-tokens.py        # generator to Swift and asset catalog
    haptics/  sound/           # AHAP files and clips by role
  Tests/
    Fixtures/matchlogs/        # replay fixtures from bug reports
    Snapshots/                 # swift-snapshot-testing references
    TestPlans/                 # Inkwell-PR.xctestplan, Inkwell-Nightly.xctestplan
  docs/
    adr/                       # ADR-000 (kickoff), ADR-001 to ADR-016 copied from 04, new ones appended
    decisions/  runbooks/      # signed founder sheet; toolchain, release, device-lab, xcode-cloud runbooks
    engine-spec/invariants.md  # property-test invariants from 05 Section 2
  ci/workflows/                # GitHub Actions: packages-linux.yml, content-pack.yml, lint.yml
  ci_scripts/ci_post_clone.sh  # Xcode Cloud: install SwiftLint, run gen-tokens
  fastlane/                    # snapshot and deliver lanes, from Phase 5
```

### 4.1 Package dependency rules

Anything not listed is forbidden, caught by the Linux build for the pure three and by the `forbidden_import` lint rule elsewhere.

| Package | May depend on | May import | Must never import | Linux lane |
|---|---|---|---|---|
| `IWCore` | nothing | Foundation | SwiftUI, UIKit, Combine, GameKit, any package | Yes |
| `IWRules` | `IWCore` | Foundation | UI frameworks, `IWContent` | Yes |
| `IWContent` | nothing | Foundation, Compression (zlib fallback behind a protocol on Linux) | UI frameworks, `IWCore` | Yes |
| `IWDesignSystem` | nothing | SwiftUI, CoreHaptics, AVFoundation | `IWCore`, `IWFeatures`, GRDB | No |
| `IWPersistence` | `IWCore`, GRDB.swift | Foundation | SwiftUI, `IWFeatures` | No (macOS tests) |
| `IWMultiplayer` | `IWCore` | Foundation, MultipeerConnectivity, GameKit (`@preconcurrency`, ADR-009) | SwiftUI, `IWFeatures` | No |
| `IWAnalytics`, `IWFeatureFlags` | nothing | Foundation (flags: SwiftUI for the debug menu view) | everything else | No |
| `IWFeatures` | all eight above | SwiftUI | no literal colors or durations (lint) | No |
| `Apps/Inkwell` | `IWFeatures` plus DI needs | SwiftUI, StoreKit | `IWCore` types in views (go through features) | No |
| `Apps/InkwellKids` | `IWCore`, `IWRules`, `IWContent`, `IWPersistence`, `IWFeatureFlags`, primitive tokens only from `IWDesignSystem` | SwiftUI | `IWFeatures`, `IWMultiplayer`, `IWAnalytics` (Kids 03; register row I) | No |

The one snippet in this document is the shape of a pure package manifest, because the `platforms` line and the language-mode setting are the two things people get wrong on day one:

```swift
// Packages/IWCore/Package.swift
let package = Package(
  name: "IWCore",
  platforms: [.iOS(.v17), .macOS(.v14)],
  products: [.library(name: "IWCore", targets: ["IWCore"])],
  targets: [
    .target(name: "IWCore",
            swiftSettings: [.swiftLanguageMode(.v6)]),
    .testTarget(name: "IWCoreTests", dependencies: ["IWCore"],
                resources: [.copy("Fixtures")])
  ]
)
```

> **[ARCH]** The macOS entry lets the engine tests run without a simulator. It costs nothing and buys a ten-second test cycle.
>
> **[IOS]** And `IWFeatures` starts as one package with six library products, per 04's OPEN. We split only if a clean build passes three minutes on the MacBook.

---

## 5. Week-by-week plan for Phase 0 and Phase 1

Durations follow 03: Phase 0 is W1 to W2 (3 EW), Phase 1 is W3 to W6 (7 EW). Dates assume kickoff Monday 2026-10-12. Week 1 is day-level; weeks 2 to 6 are task-level. Every Friday demo is a build on a phone.

### 5.1 Week 1 (Oct 12 to 16), day by day

| Day | Task | Owner | Acceptance test |
|---|---|---|---|
| Mon | Founder signs F1 to F6 and F11; trademark attorney engaged for Inkwell plus two fallbacks (01 Section 8); ARCH creates the repo with the Section 4 skeleton, `Makefile`, rulesets and labels; IOS completes steps 1 to 3 (roles, App IDs, record and name check) | Founder, ARCH, IOS | `make doctor` passes; `main` protected; App IDs registered; name outcome known |
| Tue | Nine `Package.swift` files with placeholder APIs and one `@Test` each; `Apps/Inkwell` shows a "hello paper" view painting `color.canvas` from a hand-written token; `linux-packages` and `lint` workflows live. DESIGN creates the Figma project and seeds `00 Foundations` with the spacing, radius, elevation and type tables from 07 Section 11 | ARCH, IOS, DESIGN | PR #1 touching every package is green on Linux and lint; variables visible in Dev Mode |
| Wed | Xcode Cloud connected; "PR Verify" and "Main to TestFlight" workflows; automatic signing on both targets; lab devices registered. DATA's `fetch.py` downloads ENABLE, SCOWL and GeoNames with checksums; license texts filed | IOS, DATA | A merge to `main` produces an internal TestFlight build on the founder's phone; `make fetch` reproducible |
| Thu | `gen-tokens.py` v0 reads a hand-written `tokens.json` for Quiet Minimal (the skeleton, 07 Section 9) and emits `Tokens.swift`; "hello paper" switches to generated tokens; `no_literal_color` turned on. DATA's `build_dawg.py` v0 builds a DAWG from ENABLE and a Swift test loads it | ARCH, DESIGN, DATA | Changing a hex in JSON changes the screen with no Swift edit; lint fails a deliberate literal; DAWG test passes on Linux and macOS |
| Fri | Nightly workflow; `toolchain.md`, `device-lab.md` and ADR-000 written; Demo 1 on the iPhone SE 2nd gen | QA, ARCH | Demo 1 delivered (Section 6.1) |

### 5.2 Weeks 2 to 6

| Week | Phase | Tasks | Owner | Acceptance test | Friday demo |
|---|---|---|---|---|---|
| W2 (Oct 19 to 23) | 0 | `IWDesignSystem` v0: eight components (button, text field, chip, card, list row, letter glyph view, timer ring shell, toast) with previews at xSmall, large and accessibility3, light and dark, Reduce Motion on and off; `PreviewGallery` and first snapshot corpus; `IWFeatureFlags` with debug menu; `IWPersistence` skeleton with GRDB migration 001; App 2 record and empty target; IAP product and `.storekit` file; TestFlight groups; release dry run; Rive and Lottie accounts; `haptic.stamp` AHAP wired; founder signs F7 to F10 and F12 | IOS, DESIGN, QA, ARCH | 03 Phase 0 exit: CI green on a PR touching every package; internal TestFlight on all lab devices; tokens consumed in light and dark; name outcome known | Demo 2 (Section 6.2) |
| W3 (Oct 26 to 30) | 1 | `simulate` command-line target (due Monday); `IWCore` NPAT state machine (lobby, round, answering, reveal, challenge, committed), reducer, ledger; seeded letter draw with availability weighting and exclusions (02 Section 6); `MatchSession` actor; property tests for scoring and normalization idempotence; functional letter draw and timer in `NPATFeature`; en-base pack v0 (ENABLE DAWG plus Animal list) under the 12 MB Phase 1 target | ARCH, IOS, DATA, GAME | 1,000 random games replay to identical ledgers; over 10,000 draws X, Q, Z each under 2 percent | Demo 3 (Section 6.3) |
| W4 (Nov 2 to 6) | 1 | Answer sheet with keyboard handling (autocorrect, predictive text and paste off per 02 Section 12); functional scoring reveal; self-judge for unsure answers; solo round end to end; Paper & Ink and Night Lounge as previews of Home and Round with M01 at 600 ms and 1.2 s; direction gate Friday | IOS, DESIGN, JOBS | A full solo round completes with Classic scoring; both directions run on the SE 3rd gen without a hitch | Full solo round plus the two directions side by side; F5 confirmed; letter draw duration decided (register row J) |
| W5 (Nov 9 to 13) | 1 | Dictionary live in the round (three-state validation, fuzzy "did you mean"); GeoNames Place list; Name list v0; personal bests per preset; local analytics events; nearby spike starts (ARCH, W5 to W6) | DATA, IOS, ARCH | Golden set: at least 95 percent correct for Thing and Animal, 85 percent for Place, zero false REJECTs for Name | Dictionary live, personal bests; spike status |
| W6 (Nov 16 to 20) | 1 | Cold-launch harness on the SE 2nd and 3rd gen; 100 consecutive solo rounds script; keyboard focus bug bash; `IWContent` perf tests (load under 150 ms, lookup under 1 ms p99); M1 exit review | IOS, QA, GAME | All 03 Phase 1 exit criteria green; JOBS plays five rounds unprompted and asks for a sixth | First-60-seconds stopwatch demo on the SE; nearby spike keep/kill writeup |

> **[QA]** Two W6 exit criteria depend on register rows A (cold launch number) and D (floor device) being closed in Phase 0. Both go on the W2 Friday agenda so W6 measures one number on one device.
>
> **[ARCH]** My proposal for that agenda: 800 ms p90 to the interactive Home on the SE 3rd gen as the gate, 1.5 s never-exceed on the SE 2nd gen, measured nightly by `XCTApplicationLaunchMetric`. The row owners close it; this document does not.

---

## 6. The first three Friday demos in detail

Each demo is given on a physical phone in the founder's hand, never mirrored to a screen. The presenter says nothing for the first thirty seconds. We note what the founder does and says, then what the instruments say.

### 6.1 Demo 1, Friday W1: "The repo builds on a phone and shows paper"

**On screen.** The app launches from TestFlight on the SE 2nd gen. One screen: a canvas in the Quiet Minimal tokens with a single line of body text ("Hello, paper.") in the generated `font.body`. Switching the system appearance to dark switches the canvas live. A triple-tap debug menu shows the build number, git SHA and the Xcode Cloud build link.

**What the founder should feel.** Nothing yet, and that is the point. The feeling to notice is the absence of friction: the build is on their phone, a merge produced it, and the color came from a JSON file a designer owns.

**What we measure.** Merge to TestFlight availability (target under 25 minutes); Xcode Cloud minutes used in W1 (under 4 hours); Linux package test wall time (under 90 seconds); every lab device received the build.

### 6.2 Demo 2, Friday W2: "The design-system sampler on an iPhone SE"

**On screen.** `PreviewGallery` as a screen in the app on the SE 2nd and 3rd gen. It scrolls the type ramp (ten roles from 07 Section 11.4), the color roles with contrast ratios printed beside them, the spacing scale as ruled bars, and the eight W2 components in every state. A control row switches theme between Quiet Minimal and the first Paper & Ink token pass, Dynamic Type between xSmall, large and accessibility3, and Reduce Motion on and off. Tapping the letter glyph fires `haptic.stamp`.

**What the founder should feel.** The stamp: one haptic, correctly weighted, landing with the visual. And that the type ramp at accessibility3 still reads as designed with nothing truncated. If the founder reaches for the theme switch unprompted, the token architecture has made its point.

**What we measure.** Haptic-to-visual latency under 20 ms by slow-motion video (04 Section 12); zero snapshot failures across the gallery; contrast ratios meeting 07 Section 11.5 in both themes (QA's script); eight of eight components with all states in both Figma and previews.

### 6.3 Demo 3, Friday W3: "Letter draw and timer on device"

**On screen.** Home with one button. Tap: a functional letter draw (a plain `Shape.trim` stroke, no final motion) and a 60-second timer ring in `font.numeric`. The letter comes from the seeded engine; the debug menu shows the seed, offers "replay this seed" (same letter), and shows the last 50 draws as a histogram.

**What the founder should feel.** Anticipation at the draw even unstyled, and trust in the timer: no stutter, and backgrounding behaves per GAME's ruling on register row F (solo pauses). The founder should want to type an answer and be slightly annoyed there is no field yet. That annoyance is Demo 4's pull.

**What we measure.** Letter distribution over 10,000 simulated draws; replay determinism over 1,000 games; frame time during the draw under 16.6 ms on the SE 2nd gen; engine suite under 20 seconds on Linux; the `simulate` score distribution handed to GAME.

> **[JOBS]** Demo 3 is the first one where I will have an opinion. If the timer ring makes me anxious in a bad way rather than a good way, that goes into the Phase 2 motion brief, not into W4.
>
> **[GAME]** The histogram is for me. If Classic weighting makes E and S feel too frequent, I want the numbers that week, not in Phase 3.

---

## 7. Engineering conventions

### 7.1 Coding standards summary

- Swift 6 language mode and strict concurrency complete in every package from the first commit (ADR-009). No `DispatchQueue`, no `@unchecked Sendable` without an ADR note, no `Task.detached` outside the app entry.
- Value types for engine state; the reducer is a free function `(State, Event) -> (State, [Effect])` (ADR-002). Randomness and time enter as events or injected protocols, never as globals (ADR-003).
- One public `View` and one `@Observable` model per feature; features never import each other (04 Section 10.3).
- No literal colors, fonts or durations outside `IWDesignSystem`; everything comes from generated tokens (ADR-015).
- Every component and screen state has a preview at xSmall, large and accessibility3, light and dark, Reduce Motion on and off (04 Section 10.4). Previews are the design review surface.
- Force unwraps are lint errors. `fatalError` is allowed only in `IWCore` for violated invariants, each with a property test showing legal events cannot reach it.
- `make doctor`, `make lint`, `make gen-tokens`, `make pack`, `make test-linux` are the only commands anyone must remember.

### 7.2 Commit and pull request conventions

- Branches `<persona>/<phase>-<topic>`, for example `ios/p1-answer-sheet`; squash merge; PR title becomes the commit subject.
- Subject prefixes `feat`, `fix`, `perf`, `a11y`, `design`, `content`, `test`, `ci`, `docs`, `adr`, with the package in parentheses: `feat(IWCore): NPAT round state machine with seeded draw`.
- PR template, all sections required: What and why; device screenshots or recording in light and dark for anything visible; accessibility checklist (7.6); performance checklist (7.7); tests added; flags touched; ADR touched or "none".
- One approval. IOS reviews `IWFeatures` and `Apps/`; ARCH reviews `IWCore`, `IWRules`, `IWPersistence`, `IWMultiplayer`; DATA reviews `Content/` and `IWContent`; DESIGN approves every snapshot diff; CI never re-records.
- An engine bug fix includes a replay fixture under `Tests/Fixtures/matchlogs/` (05 Section 1, rule 1).

### 7.3 ADR process

ADRs live in `docs/adr/` as `ADR-NNN-short-title.md` with Context, Options considered, Decision, Consequences and Status. ADR-001 to ADR-016 are copied from 04 Section 20 on day one; ADR-000 records the kickoff (founder sheet, name outcome, bundle IDs, toolchain pin). A decision needs an ADR when it changes a package boundary, adds a dependency, changes a budget, or adds an exception to a convention. Proposed via the `adr-proposal.md` template, discussed in the PR that adds the file, accepted by the owning persona plus one other. Superseding writes a new ADR and edits only the old Status line. The program register (00-DECISIONS-AND-OPEN-QUESTIONS.md) stays the top-level record; an ADR that closes a register row names it.

### 7.4 Feature flag naming

Flags are a typed `enum Flag: String, CaseIterable` (ADR-013) with raw values `<area>.<feature>[.<variant>]`: `multiplayer.nearby`, `multiplayer.gameCenterAsync`, `store.proUnlock`, `theme.nightLounge`, `motion.inkShader`, `debug.slowMotion10x`, `debug.reduceMotionOverride`. Each declares a default, an owner persona, the phase it flips on and the phase it is deleted. A flag two phases past its flip date fails a unit test that lists stale flags. Flags never gate the rules of a saved match.

### 7.5 Design token JSON schema outline

`Design/tokens.json` is the contract between Figma and Xcode (07 Section 10, ADR-015). The three layers map to three top-level objects.

| Key | Shape | Example |
|---|---|---|
| `meta` | `version` (semver), `exportedAt`, `figmaFileKey` | `"version": "0.3.0"` |
| `primitives` | groups `color`, `space`, `radius`, `duration`, `spring`, `fontFamily`, `fontSize`; leaves are `{ "value", "type" }` | `"color.paper.cream.100": { "value": "#F6F1E7", "type": "color" }` |
| `themes` | one object per theme id (`quietMinimal`, `paperInk`, `swissEditorial`, `nightLounge`), each with `appearance.light`, `.dark`, `.increasedContrast`, plus `type`, `motion`, `material`, `sound`, `haptic` | `"color.canvas": { "ref": "color.paper.cream.100" }` |
| `components` | component tokens referencing semantic tokens only | `"button.primary.background": { "ref": "color.accent" }` |
| type roles | `{ "ref", "weight", "textStyle" (Dynamic Type style), "minPointSize"?, "clamp"? }` | `"font.letter": { "textStyle": "largeTitle", "clamp": [96, 220] }` |
| motion roles | `{ "duration": ref, "spring": { "duration", "bounce" }, "reduceMotion": "crossfade" or "none" }` | per 09 Section 2 |

Generator rules: every `ref` resolves within the file; a theme missing any semantic token fails generation; each color role carries its 07 Section 11.5 contrast requirement and the generator computes the ratio against `color.canvas` and fails under threshold; `space` and `radius` may not appear under `themes`.

### 7.6 Accessibility checklist per PR (visible changes)

1. Every interactive element has a label, a value where state matters, and an identifier for XCUITest.
2. Previews at accessibility3 attached; nothing truncates.
3. Reduce Motion alternative implemented for any new animation, with its final-frame snapshot committed.
4. Color is never the only carrier of state.
5. Tap targets at least 44 by 44 pt.
6. `performAccessibilityAudit()` extended for any new screen and passing (05 Section 2).
7. VoiceOver walkthrough done on device by the author; non-default focus order noted.
8. Haptics and sound are additive, never the only signal.

### 7.7 Performance budget checks per PR

| Check | Threshold (04 Section 12) | Verified how |
|---|---|---|
| Cold launch | the gate chosen under register row A (proposal: 800 ms p90 on the SE 3rd gen) | Nightly `XCTApplicationLaunchMetric` baseline must not regress more than 5 percent |
| Round frame time | 16.6 ms at 60 Hz, zero hitches over 50 ms | Any PR adding an animation attaches an Animation Hitches trace from the SE 2nd gen |
| Dictionary | load under 150 ms, lookup under 1 ms p99 | `IWContent` perf tests when `Content/` or `IWContent` changes |
| Memory | under 150 MB steady in a round | Nightly `XCTMemoryMetric`; PRs touching images or packs state the delta |
| Binary size | under 40 MB, alert at 30 | QA reads App Store Connect size per TestFlight build; a new dependency states its delta |
| Content pack | base pack 6 MB compressed | `content-pack` job fails over budget |

---

## 8. Content pipeline bootstrap (W1 to W3)

Owner: **[DATA — Omar Haddad]**. The goal is an English base pack good enough for Phase 1's solo loop and a pipeline that is boring to re-run. Sources and licenses are those verified in 04 Section 6.5; Wiktionary is excluded from shipped packs (ADR-007).

| Source | License | W1 to W5 use | Attribution |
|---|---|---|---|
| ENABLE | Public domain, courtesy credit requested | Core validity DAWG; Thing fallback | Credit in `notices.txt` |
| SCOWL (sizes 35 to 70) | MIT-like | Variant spellings (colour/color); sized tiers later for Kids | Copyright notice in `notices.txt` |
| WordNet 3.x | WordNet license | Build-time seeding of the Animal list (hyponyms of "animal"); Food list in Phase 3 | Notice in `notices.txt` |
| GeoNames | CC BY 4.0 | Countries plus cities with population 100,000 or more and all capitals, for the W5 Place list | `notices.txt` and Settings > About > Licenses |
| Hand-curated CSVs | Ours | Name list v0 (never used to REJECT), Animal additions, aliases ("USA" to "United States") | n/a |
| Wikidata | CC0, to verify (ADR-007 OPEN) | Not before Phase 3 | n/a |

**Scripts to write** (all in `Content/tools/`, Python 3.12, run by `make pack`):

| Script | Week | What it does | Test |
|---|---|---|---|
| `fetch.py` | W1 | Downloads each source with a pinned URL and SHA-256; refuses on mismatch | Checksums committed |
| `normalize.py` | W1 | NFKC, case fold, strip diacritics for the match key while keeping the display form, strip punctuation, apply the SCOWL variant map (04 Section 6.2) | Idempotence over all of ENABLE |
| `build_dawg.py` | W1 | Minimal acyclic DAWG serialized as a compact byte array with a header | Round trip on 1,000 known and 1,000 unknown words in Swift and Python |
| `build_list.py` | W2 | Category lists as sorted UTF-8 arrays with front coding and a block index, LZFSE-compressed, plus an uncompressed fixture for the Linux lane | Random access by index equals source; prefix walk equals linear scan |
| `curate.py` | W2 | Merges curated CSVs with generated lists, applies aliases and popularity tiers, flags collisions | Every alias resolves |
| `profanity.py` | W2 | Blocklist from an open list plus in-house additions; the App 1 policy (score it, never promote it, mask it in shared images) follows register row G and is closed by DATA, GAME and JOBS before W3 | Never matches the common Animal and Thing allow-list |
| `sign.py` | W3 | Writes `manifest.json` (id, version, language, notices, checksums, min engine version) and signs it with an Ed25519 key in the founder's Keychain; public key embedded in `IWContent` | Swift test accepts a signed pack and rejects a tampered one |
| `measure.py` | W3 | Compressed and in-memory sizes per blob; fails over budget | Runs in `content-pack` |

**Golden tests.** `Content/golden/npat-500.csv` is the 500-answer golden set from 03 Section 5: 125 answers per category across letters, mixing valid, misspelled, alias and unknown cases, each with its expected state (`valid`, `suggested(correction)`, `unknown`, `rejected`). A parameterized Swift Testing test runs the set against the built pack. Phase 1 exit: at least 95 percent correct for Thing and Animal, 85 percent for Place, zero false REJECTs for Name. The set grows with every dictionary bug and is never pruned.

**Size targets.** ENABLE DAWG under 1 MB (to be measured); Animal list under 200 KB; Place list under 1.5 MB compressed; Name list under 200 KB; en-base total under 12 MB in Phase 1 (03 scope) and 6 MB compressed at launch (04 Section 6.4), enforced in CI from the W14 freeze; under 25 MB loaded in memory.

> **[DATA]** The 12 MB Phase 1 target is generous on purpose: it lets me ship an unoptimized Place list in W5 and still have the solo loop testable. The 6 MB launch budget is the one CI enforces from W14.
>
> **[ARCH]** Fine, but `content-pack` prints both numbers from W3 so nobody is surprised at the freeze.

---

## 9. Design bootstrap and the W4 direction gate

Owner: **[DESIGN — Sofia Lindqvist]** with **[IOS]**. Design runs one phase ahead: Phase 0 for design is foundations plus the direction race; Phase 1 for design is the Phase 2 motion brief.

| Week | Figma | SwiftUI previews | Parity check |
|---|---|---|---|
| W1 | `00 Foundations`: primitive variables (paper, ink and accent palettes; space 1 to 8; radius xs to pill; duration and spring presets from 09 Section 2); semantic collection with modes Light, Dark, Increased Contrast; type ramp mapped to Dynamic Type names | Hand-written `tokens.json` for Quiet Minimal, generated `Tokens.swift`, "hello paper" | Hex values equal across Figma, JSON and Swift; by eye in W1, by export from W2 |
| W2 | `01 Components`: the eight W2 components with 07 Section 12.2 state matrices; `03 Directions`: Paper & Ink and Night Lounge pages | The same eight components with previews; `PreviewGallery` | Each snapshot beside its Figma frame in the W2 record (the only slides allowed, for the record, not for the demo) |
| W3 | `02 Screens App 1`: Home and Round (letter draw plus answer sheet) in both directions; motion brief for M01 with both durations (600 ms and 1.2 s) and the Reduce Motion alternative | Home and Round previews using semantic tokens only, switchable between themes; M01 as `Shape.trim` with a duration token | Switching theme changes nothing but tokens and assets |
| W4 | Gate assets: the same two screens, two themes, two phones | A TestFlight build with a theme switch in the debug menu, from one commit | The gate below |

Rules carried from 07 Section 10: layout primitives are not themeable; every theme ships light, dark and increased contrast and passes the contrast script; themes switch live with a 350 ms canvas cross-fade and nothing else moves; custom fonts scale with `Font.custom(_:size:relativeTo:)` and the handwriting face carries a `minPointSize` token.

**The W4 direction gate (Friday Nov 6).** Two SE 3rd gens side by side, one in Paper & Ink, one in Night Lounge, both from the same commit. The founder plays Home to letter draw to answer sheet on both, twice: at 600 ms and at 1.2 s. Nobody speaks for the first two minutes. The gate answers F5 (confirm or reverse the identity), register row J (draw duration, with the master reference's preset scaling applying either way) and whether Night Lounge earns its reduced Pro slot under F6. Measured: zero hitches over 50 ms on either theme; contrast script results in all three appearances; Home tap to first keystroke under 10 s (08 FR-01); the founder's unprompted statements, written down verbatim by QA. Outputs: DECISION lines in 07 Section 16 and 09 Section 4, an ADR if the identity reverses, and the Phase 2 motion brief.

> **[DESIGN]** I am building Night Lounge to lose gracefully. If it wins on a phone in the founder's hand, we change the plan and I will be delighted.
>
> **[IOS]** One constraint: both builds come from the same commit. If Paper & Ink has an extra week of polish, the comparison is worthless.

---

## 10. Risks specific to the first four weeks

| # | Risk | Likelihood | Impact | Tripwire | Mitigation | Owner |
|---|---|---|---|---|---|---|
| K1 | "Inkwell" taken in App Store Connect on day one | Medium | Low | Record creation fails Mon W1 | Fallback order ready (F1); bundle IDs are name-neutral | Founder |
| K2 | Xcode Cloud connection or signing fails for more than a day | Medium | Medium | No TestFlight build by Wed W1 evening | Fastlane `pilot` upload from the MacBook as a bridge; GitHub Actions macOS as the fallback named in 03 | IOS |
| K3 | Swift 6 strict concurrency stalls the first UI feature | Medium | Medium | Any `IWFeatures` PR open more than three days in W3 | Pair IOS and ARCH on the first two features; patterns in `docs/runbooks/concurrency.md`; exceptions only via ADR-009 | IOS |
| K4 | Figma export shape drifts and the token generator needs hand edits | Medium | Medium | Two consecutive exports hand-edited | Freeze the Section 7.5 schema at W2 Fri; replace the plugin with a script on Figma's variables API if needed | ARCH, DESIGN |
| K5 | `IWContent` cannot build on Linux (Compression framework) | High | Low | `linux-packages` red on the first `IWContent` PR | Decoder behind a protocol; uncompressed fixtures on Linux (04 Section 2) | DATA |
| K6 | Cold launch number and floor device still open at W6 (register rows A and D) | Medium | High | Not closed on the W2 Friday agenda | ARCH's proposal in Section 5.2 becomes the default if the row owners offer nothing better | QA, IOS |
| K7 | Design foundations lag code at 80 percent designer time | Medium | Medium | Fewer than six components have both frames and previews by Wed W2 | Reduce W2 to the six the Round screen needs; the rest move to W3 | DESIGN |
| K8 | Direction gate becomes a slideshow | Low | High | Any gate asset not in TestFlight by Thu W4 | 09 Section 9 rule: a projector review did not happen; the gate moves to Monday rather than being held on slides | JOBS |
| K9 | Second engineer under 60 percent in Phase 1 | Medium | Medium | ARCH logs under 19 hours in W3 | Move `simulate` and the nearby spike later; reopen F12 | ARCH |
| K10 | SwiftUI text field autocorrect-off and focus handling flaky on iOS 17.0 | Medium | High | Any dropped keystroke in the W6 100-round script | UIKit-backed field behind a SwiftUI wrapper as the planned fallback; tested on the SE 2nd gen on iOS 17.0 in W4 | IOS |
| K11 | Lab devices late | Low | Medium | Not all in hand by Wed W1 | Personal phones cover W1 and W2; the SE 2nd gen on iOS 17.0 must not slip past W3 | Founder, QA |

---

## 11. Team debates

### 11.1 Debate: neutral bundle IDs versus the product name

> **[IOS]** The bundle ID is forever once we upload. Naming is not settled until the attorney answers. So the identifier should say nothing about the name: `npat`, `npatkids`. Ugly, invisible, permanent.
>
> **[JOBS]** I hate shipping a product whose identifier is an acronym nobody will say. But I hate renaming a store record more. Convince me nobody sees it.
>
> **[IOS]** Nobody does. It appears in crash logs and provisioning. Universal Links use the domain, not the bundle ID.
>
> **[ARCH]** Second reason: App 2 shares packages and the signing identity; a neutral prefix for both keeps the App IDs predictable when we add the `.dev` suffix.
>
> **[QA]** And App Review does not care; there is nothing on identifiers in the guidelines.
>
> **[JOBS]** Fine. Neutral identifiers, and the attorney hears about the name, not the string.

**DECISION:** `com.<founderdomain>.npat`, `com.<founderdomain>.npatkids`, `com.<founderdomain>.npat.dev`. Recorded in ADR-000.

### 11.2 Debate: how much design system before the first game screen

> **[DESIGN]** Phase 0 promises "design system v0". That is thirty-one components in 07. I cannot build thirty-one with states in two weeks at 80 percent and also run two directions. I can build twelve; the Round screen needs eight.
>
> **[JOBS]** Then build eight. The Round screen is the product. Nobody has ever fallen in love with a segmented control.
>
> **[IOS]** Eight is enough for the W2 gallery to prove the token architecture: text field, button, chip, card, list row and the letter glyph show state and theme switching; the timer ring shell and toast make it a Round screen kit. Settings components slide to W3.
>
> **[QA]** Eight components in all states at three sizes and two appearances is already over two hundred snapshots. Enough to catch regressions, small enough to review.

**DECISION:** W2 ships eight components with full state matrices; the other twenty-three follow the screens that need them. K7 is the tripwire.

### 11.3 Short debate: a throwaway game screen in Phase 0

> **[GAME]** Two Fridays without a single playable thing worries me. Could W2 include a crude letter and timer?
>
> **[ARCH]** 03 is explicit: Phase 0 scope out is "any game screen", because a crude screen built before the engine exists becomes the engine's shape by accident.
>
> **[JOBS]** Both right. Compromise: the `simulate` target lands Monday W3, not Friday, so GAME has numbers three days earlier. No screen.

**DECISION:** No game screen in Phase 0. `simulate` is the first Phase 1 deliverable, due Monday W3.

**OPEN:** Whether the debug histogram (Demo 3) stays in TestFlight builds for beta testers. QA, by Phase 5.

---

## 12. Decisions and open questions

**DECISION:** Kickoff Monday 2026-10-12; W1 day plan per Section 5.1; founder sheet signed in two tranches (F1 to F6 and F11 on day one; the rest by W2 Friday).
**DECISION:** Neutral bundle IDs; one App Store Connect record per app; TestFlight shares the record; a `.dev` App ID for local side-by-side builds.
**DECISION:** Hybrid CI per ADR-014: four Xcode Cloud workflows (PR Verify, Main to TestFlight, Nightly, Release) and three GitHub Actions workflows (`linux-packages`, `content-pack`, `lint`); required checks per Section 3.5.
**DECISION:** Content sources and tools live in the mono-repo under `Content/`; no separate content repository in v1.
**DECISION:** The Section 7.5 token schema is frozen at W2 Friday; changes need an ADR.
**DECISION:** W2 design-system scope is eight components.
**DECISION:** Flag names follow `<area>.<feature>[.<variant>]` with declared flip and delete phases.
**OPEN:** Cold launch gate and floor device (register rows A and D); QA with IOS; close W2 Friday; default proposal in Section 5.2.
**OPEN:** Profanity policy for App 1 (register row G); DATA with GAME and JOBS; close before dictionary v0 in W3.
**OPEN:** Exact Xcode version pin; IOS records it in `docs/runbooks/toolchain.md` on Monday W1 from Apple's current SDK table.
**OPEN:** Figma plugin or REST script as the long-term token exporter; ARCH and DESIGN after two exports (K4).
**OPEN:** Debug histogram in TestFlight builds; QA by Phase 5.

---

## 13. Sources

Apple pages were checked on 2026-10-04. Where an exact page could not be confirmed, the official root is given and marked.

- Xcode Cloud compute hours and pricing: https://developer.apple.com/xcode-cloud/get-started/
- Xcode Cloud workflow actions: https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions
- Xcode Cloud distribution workflow and TestFlight post-actions: https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution
- Xcode Cloud custom build scripts (WWDC21): https://developer.apple.com/videos/play/wwdc2021/10269/
- Xcode SDKs and system requirements (Xcode 26.x, macOS Sequoia 15.6 or later, Swift 6.2): https://developer.apple.com/xcode/system-requirements/ and https://developer.apple.com/documentation/xcode-release-notes/xcode-26-release-notes
- Register an App ID: https://developer.apple.com/help/account/identifiers/register-an-app-id/
- Changing the bundle identifier: https://developer.apple.com/documentation/xcode/changing-the-bundle-identifier
- App Store Connect, add a new app: https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app/ ; app information reference (SKU, primary language): https://developer.apple.com/help/app-store-connect/reference/app-information/app-information/
- TestFlight overview and tester limits: https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/ and https://developer.apple.com/testflight/
- Automatic signing: https://developer.apple.com/help/account/provisioning-profiles/create-a-development-provisioning-profile/
- Game Center configuration overview: https://developer.apple.com/help/app-store-connect/configure-game-center/overview-of-game-center/
- StoreKit Testing in Xcode (WWDC20): https://developer.apple.com/videos/play/wwdc2020/10659/
- Privacy manifest files: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- Swift Testing: https://developer.apple.com/documentation/testing
- Core Haptics (official root; AHAP pages sit under it): https://developer.apple.com/documentation/corehaptics
- GitHub rulesets and required status checks: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- SwiftLint: https://github.com/realm/SwiftLint ; SwiftFormat: https://github.com/nicklockwood/SwiftFormat ; swift-snapshot-testing: https://github.com/pointfreeco/swift-snapshot-testing
- Figma variables and Dev Mode: https://help.figma.com/hc/articles/15023124644247
- Rive Apple runtime: https://rive.app/docs/runtimes/apple ; Lottie iOS: https://github.com/airbnb/lottie-ios
- Word list licenses as verified in 04 Section 6.5: ENABLE README https://sources.debian.org/src/scowl/6-2/r/enable/README ; SCOWL http://wordlist.aspell.net/ ; WordNet https://wordnet.princeton.edu/license-and-commercial-use ; GeoNames https://wiki.creativecommons.org/wiki/GeoNames
