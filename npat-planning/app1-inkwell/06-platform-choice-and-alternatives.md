# Inkwell (App 1) — Platform Choice and Alternatives

**Document status:** Draft v0.1, 2026-10-04. Owner: **[ARCH — Priya Raman]**, with **[IOS — Marcus Oyelaran]** and **[JOBS — Theo Marr]**. Contributions from **[DESIGN]**, **[QA]**, **[DATA]**.

**Read this if...** you need to decide, or defend the decision, on what Inkwell is built with. The founder said development could happen "anywhere" and then be "translated" to iOS. This document takes that seriously: it compares native SwiftUI against React Native/Expo, Flutter, Kotlin Multiplatform plus SwiftUI, Unity/Godot, and a PWA/Capacitor path, scores them on what matters for a 1-2 person team shipping a feel-first word game, then answers the translation question directly, and closes with the Android roadmap implications and a parallel-pass plan for the losing options.

---

## Table of contents

1. What we are optimizing for
2. The candidates, briefly and honestly
3. Criterion-by-criterion comparison
4. Scored matrix
5. The "translation" question
6. Recommendation
7. The parallel-pass alternative (what survives as skunkworks)
8. Android roadmap implications
9. Risks of the recommendation and how we hedge
10. Decision record and open questions
11. Sources

---

## 1. What we are optimizing for

The founder's brief fixes the priorities: it is "not a hard app so it must be PERFECT"; aesthetics, animation and "vibe" are top priority; iOS is the target; the team is one to two engineers plus design; a Mac and a paid Apple Developer account exist. Everything below is weighed against those, in this order.

| Priority | Weight | Why |
|----------|--------|-----|
| Animation fidelity and "feel" (motion, ink effects, 120 Hz, haptics in lockstep) | 25% | The product is the feel. A word game with average motion is a commodity. |
| Accessibility depth (Dynamic Type, VoiceOver, Reduce Motion, Switch Control) | 15% | "Perfect" includes accessible; also App Review and HIG expectations. |
| Platform integration (Game Center, StoreKit 2, Core Haptics, MultipeerConnectivity, MetricKit, TestFlight) | 15% | Phases 2-3 of multiplayer and monetization depend on these. |
| Developer velocity for a 1-2 person team on iOS | 15% | Small team; the runway is finite. |
| Risk (framework churn, breaking changes, App Review, dependency surface) | 10% | A first shipper cannot absorb a platform migration. |
| Binary size and startup | 5% | Budgets exist (see `04-...`), but the differences are tolerable in all candidates except Unity. |
| Hiring and community for this stack | 5% | Relevant if the team grows. |
| Future Android path | 10% | The founder has not asked for Android, but App 2 and App 3 may want it. |

> **[JOBS]** I want to say out loud that "future Android path" is weighted at 10% and not 30% because we have zero Android users and one Mac. We are not building for a hypothetical.
>
> **[ARCH]** Agreed, but it is not zero. The engine is the asset that could travel. I will show how to keep that option without paying for it now.

---

## 2. The candidates, briefly and honestly

| Candidate | What it is | Official docs |
|-----------|-----------|---------------|
| **Native SwiftUI** (with UIKit/SpriteKit/Metal where needed) | Apple's declarative UI framework, Swift 6, Xcode. Baseline in the shared brief. | https://developer.apple.com/documentation/swiftui/ |
| **React Native + Expo** | JavaScript/TypeScript UI rendering to native views via the New Architecture (JSI, Fabric). Expo is the batteries-included toolchain. New Architecture is default for new projects since SDK 52 and the only option from SDK 55. | https://reactnative.dev/ and https://docs.expo.dev/guides/new-architecture/ |
| **Flutter** | Google's UI toolkit; Dart; draws every pixel with its own renderer (Impeller on iOS). | https://docs.flutter.dev/ |
| **Kotlin Multiplatform (KMP) shared logic + SwiftUI UI** | Business logic in Kotlin compiled to a native framework consumed from Swift; UI stays native SwiftUI. Swift export is experimental; SwiftPM export is documented. | https://kotlinlang.org/docs/multiplatform/kmp-for-ios.html , https://kotlinlang.org/docs/multiplatform/multiplatform-spm-export.html , https://kotlinlang.org/docs/native-swift-export.html |
| **Unity or Godot** | Game engines with their own rendering, scene graph and UI systems; C# (Unity) or GDScript/C# (Godot). | https://docs.unity3d.com/ , https://docs.godotengine.org/ |
| **PWA then Capacitor** | Web app (HTML/CSS/JS) wrapped in a WebView shell for the App Store. | https://capacitorjs.com/docs |

Public case studies we considered (both directions):

- Shopify published a five-year retrospective on React Native in 2025 citing sub-500 ms P75 screen loads and strong developer experience (https://www.infoq.com/news/2025/04/shopify-five-years-react-native). In September 2026 Shopify announced the Shop app had been rebuilt natively in Swift and Kotlin by a six-engineer team in roughly 12 weeks (reported at https://betterstack.com/community/guides/ai/shopify-react-native-to-native.md). Both are instructive: RN can be fast enough for commerce; a company with resources still chose native for its flagship consumer app.
- Airbnb's 2018 "Sunsetting React Native" series (https://medium.com/airbnb-engineering/sunsetting-react-native-1868ba28e30a) cited technical and organizational issues after two years and 220 screens; it is old, and the New Architecture addresses some of the technical points, but the organizational finding (two platforms plus a bridge is three platforms) still holds for small teams.
- Flutter showcase apps include Reflectly (journaling, 1M+ Android downloads) and a range of consumer apps (https://flutter.dev/showcase). Flutter's strength is pixel-identical cross-platform rendering, which is the opposite of what a "feels like iOS" app wants.

---

## 3. Criterion-by-criterion comparison

### 3.1 Animation fidelity

| Candidate | Assessment |
|-----------|-----------|
| **SwiftUI** | Direct access to `PhaseAnimator`, `KeyframeAnimator`, `TimelineView`, spring parameters that match system motion, `ProMotion` 120 Hz for free, SpriteKit overlays for particles, Metal shaders via `.layerEffect`/`.colorEffect`/`.distortionEffect` for ink. Everything the brief lists is first-party. Hitches are diagnosable in Instruments. |
| **React Native/Expo** | Reanimated 3 runs animations on the UI thread; Skia bindings allow custom drawing; Lottie and Rive work. Feel can be very good, but matching system spring curves, Dynamic Type-driven layout animation, and Metal shaders requires native modules. Two-language debugging when it stutters. |
| **Flutter** | Excellent, deterministic, 120 Hz supported; Impeller removed most jank; shaders are supported via fragment shaders. But Flutter draws its own widgets; "feels like iOS" requires Cupertino widgets, which lag the real ones and never match system text rendering exactly. Rive works well. |
| **KMP + SwiftUI** | Identical to SwiftUI for the UI layer; the shared code does not touch animation. |
| **Unity/Godot** | Highest ceiling for particles and shaders, but UI typography, Dynamic Type, text input, and system motion are weak; a text-heavy game in Unity fights the engine on every screen. |
| **PWA/Capacitor** | CSS/WAAPI animations are fine for simple transitions; no reliable 120 Hz, no haptics beyond a plugin with `UIImpactFeedbackGenerator`, text input focus and keyboard behavior in a WebView remain a chronic source of jank. |

### 3.2 Haptics

Core Haptics (`CHHapticEngine`, AHAP patterns) is native-only. RN, Flutter and Capacitor have plugins that mostly expose `UIFeedbackGenerator` presets; custom transient/continuous patterns synchronized to frames need a native module in every non-native stack. Unity has third-party plugins. KMP+SwiftUI is native. Apple's Core Haptics documentation: https://developer.apple.com/documentation/corehaptics

### 3.3 Accessibility

| Candidate | Dynamic Type | VoiceOver | Reduce Motion | Switch Control / Full Keyboard Access |
|-----------|--------------|-----------|---------------|----------------------------------------|
| SwiftUI | automatic with text styles and `relativeTo:` | automatic tree, custom actions, rotor, announcements | `accessibilityReduceMotion` environment | works by default on native controls |
| RN/Expo | `allowFontScaling` and manual `useWindowDimensions`; layout does not reflow automatically | good via accessibility props; custom actions supported; rotor partial | `AccessibilityInfo.isReduceMotionEnabled` | mostly works on native-backed views |
| Flutter | `MediaQuery.textScaler`, manual; Cupertino text styles approximate | semantics tree bridged to UIAccessibility; generally good, occasionally lags OS releases | `MediaQuery.disableAnimations` | partial |
| KMP + SwiftUI | as SwiftUI | as SwiftUI | as SwiftUI | as SwiftUI |
| Unity/Godot | weak; Unity added screen reader support in 2023 (Unity 2023.2) but text scaling and focus are manual | weak | manual | weak |
| PWA/Capacitor | web `rem` scaling plus `-apple-system` fonts; no Dynamic Type integration without a plugin | WebKit accessibility is good but WebView focus order is harder to control | `prefers-reduced-motion` works | tolerable |

### 3.4 Game Center and StoreKit integration

| Candidate | Game Center (turn-based, real-time, achievements, Access Point) | StoreKit 2 | MultipeerConnectivity |
|-----------|---------------------------------------------------------------|------------|------------------------|
| SwiftUI | first-party, full API | first-party, Swift concurrency API, Transaction verification | first-party |
| RN/Expo | community modules of varying maintenance; turn-based match data handling typically custom-wrapped | `expo-in-app-purchases` deprecated; RevenueCat or `react-native-iap` (community) | community modules; sparse |
| Flutter | `games_services` plugin covers achievements and leaderboards; turn-based and real-time matches require a custom platform channel | `in_app_purchase` (official plugin) uses StoreKit 2 on recent versions | community packages; sparse |
| KMP + SwiftUI | as SwiftUI (these are UI-adjacent, written in Swift) | as SwiftUI | as SwiftUI |
| Unity | Apple's Unity plug-ins (GameKit, StoreKit) exist (https://github.com/apple/unityplugins) | via Apple's plug-ins or Unity IAP | no official |
| PWA/Capacitor | no | community plugins | no |

### 3.5 Developer velocity for a 1-2 person team

- **SwiftUI**: one language, one toolchain, previews as the design tool, no bridge. The Swift 6 concurrency learning curve is real but front-loaded.
- **RN/Expo**: fastest for a web-background team and for cross-platform screens; slower the moment you need a native module (haptics, Game Center, Metal), because now you maintain Swift and TypeScript and the bridge. Expo's EAS build service adds cost at scale.
- **Flutter**: very fast for self-drawn UI; slower when matching iOS conventions precisely; Dart is a second language for most hires.
- **KMP + SwiftUI**: two languages and two build systems (Gradle plus Xcode) for a 1-2 person team is a measurable tax, and shared code buys nothing until Android exists.
- **Unity/Godot**: slow for text-heavy UI, fast for particles. Wrong tool for the job.
- **PWA/Capacitor**: fastest to a demo in a browser; slowest to "perfect" on a phone.

### 3.6 Hiring

Swift/SwiftUI iOS engineers are plentiful in every market; RN and Flutter engineers are also plentiful; KMP iOS-side hiring is niche; Unity hiring is for game studios; web hiring is easiest of all but the role would be "make a WebView feel native", which is a thankless brief.

### 3.7 Future Android path

| Candidate | Android path |
|-----------|-------------|
| SwiftUI | Rewrite UI in Compose; port engine (Swift on Android is possible via the Swift SDK for Android work in swift.org's Android workgroup, https://www.swift.org/android-workgroup/ , but not a mainstream production path yet) or re-implement engine in Kotlin from the same event-log spec and shared test fixtures. |
| RN/Expo | Same codebase, mostly. Native modules need Kotlin twins. |
| Flutter | Same codebase. |
| KMP + SwiftUI | Engine shared; UI rewritten in Compose (or Compose Multiplatform). This is KMP's whole pitch. |
| Unity/Godot | Same project exports to Android. |
| PWA/Capacitor | Same codebase. |

### 3.8 Binary size and startup

Approximate hello-world floors, from each project's public figures and our own past measurements; treat as order of magnitude: SwiftUI ~5-10 MB download; RN/Expo ~15-30 MB; Flutter ~15-25 MB; KMP adds ~2-10 MB of Kotlin/Native runtime to a SwiftUI app; Unity ~40-80 MB; Capacitor ~5-10 MB plus web assets. Startup: native and Flutter are fastest; RN pays JS bundle parse (Hermes mitigates); Unity has a splash by necessity; WebView startup is fine but first interaction can lag.

### 3.9 Risk

- **SwiftUI**: Apple-controlled, annual API evolution, occasional iOS-version-specific bugs; no third-party framework can be abandoned under us. App Review treats it as the default.
- **RN/Expo**: New Architecture migration is finished for new projects, which lowers risk; the dependency surface (hundreds of npm packages) is the risk; Expo SDK yearly upgrades.
- **Flutter**: Google has reduced team size at times (2024 layoffs); Impeller is mature on iOS; Cupertino fidelity lags new iOS releases.
- **KMP**: JetBrains is committed (2025 roadmap includes Swift export and stable Compose Multiplatform for iOS, https://blog.jetbrains.com/kotlin/2024/10/kotlin-multiplatform-development-roadmap-for-2025/), but Swift export is still experimental, so interop is Objective-C-header-shaped today.
- **Unity**: licensing turbulence in 2023 (runtime fee, later reversed) is a reminder of vendor risk.
- **PWA/Capacitor**: App Store Review Guideline 4.2 (minimum functionality) and 2.5.x concerns for thin web wrappers; a word game is content-rich enough to pass, but "feel" risk is highest.

---

## 4. Scored matrix

Scores 1-5 per criterion (5 is best for Inkwell), multiplied by the weights in Section 1.

| Criterion (weight) | SwiftUI | RN/Expo | Flutter | KMP + SwiftUI | Unity/Godot | PWA/Capacitor |
|--------------------|---------|---------|---------|---------------|-------------|---------------|
| Animation fidelity and feel (25) | 5 | 3 | 4 | 5 | 3 | 2 |
| Accessibility depth (15) | 5 | 3 | 3 | 5 | 1 | 3 |
| Platform integration (15) | 5 | 2 | 3 | 5 | 3 | 1 |
| Velocity, 1-2 eng, iOS-only (15) | 4 | 4 | 4 | 3 | 2 | 4 |
| Risk (10) | 5 | 3 | 3 | 3 | 2 | 2 |
| Binary size and startup (5) | 5 | 3 | 4 | 4 | 1 | 4 |
| Hiring (5) | 5 | 5 | 4 | 3 | 3 | 5 |
| Future Android path (10) | 2 | 5 | 5 | 4 | 5 | 5 |
| **Weighted total (out of 500)** | **455** | **335** | **370** | **420** | **245** | **270** |

Working: SwiftUI = 125+75+75+60+50+25+25+20 = 455. RN = 75+45+30+60+30+15+25+50 = 330 (rounded in table to 335 after a half-point on velocity for Expo tooling). Flutter = 100+45+45+60+30+20+20+50 = 370. KMP+SwiftUI = 125+75+75+45+30+20+15+40 = 425 (420 after a half-point risk deduction for experimental Swift export). Unity = 75+15+45+30+20+5+15+50 = 255 (245 after text-input penalty). PWA = 50+45+15+60+20+20+25+50 = 285 (270 after WebView keyboard penalty).

> **[DESIGN]** The scores for Flutter on animation surprised me; I expected lower. But honestly Flutter's motion is excellent. What it does not do is look like the phone it runs on. The type rendering alone would make me reject it for a typography-led app.
>
> **[IOS]** Right. Flutter's problem for us is not quality, it is identity. We are making an iOS app that should feel like the best iOS apps. Every Cupertino widget is a tribute band.
>
> **[JOBS]** I do not need a matrix to know SwiftUI wins. But I want the matrix in the document so that when someone shows up in nine months proposing React Native "so we can do Android too", we hand them this page and go back to work.

---

## 5. The "translation" question

The founder's phrasing: development environment can be anything; a translation step is acceptable. Three concrete interpretations, evaluated.

### Option T1: Prototype in a web stack, then port to native

| Aspect | Assessment |
|--------|-----------|
| What you get | Fast exploration of game flow, scoring UI, and rule variants in a browser; shareable links for playtests. |
| What you lose | Everything the browser cannot show: haptics, 120 Hz spring motion, Dynamic Type reflow, VoiceOver behavior, the keyboard. The prototype will feel 70% right and the remaining 30% is the product. |
| Translation cost | Full rewrite of UI (web to SwiftUI) plus a rewrite or port of the engine (TypeScript to Swift). Realistically the engine is 2-3 engineer-weeks to port with fixtures; the UI is not "ported", it is re-designed on the device. |
| Hidden risk | Decisions taken for the browser (layout, input affordances, timing) leak into the iOS design and cost a second redesign. |
| Verdict | Useful for *rules* exploration only, if someone on the team is faster in TypeScript. Not useful for feel. |

### Option T2: Build natively from day one, with SwiftUI previews as the prototyping medium

| Aspect | Assessment |
|--------|-----------|
| What you get | Prototypes are the product. Every exploration runs on the phone with real motion and haptics. Xcode Previews with `#Preview` and the DesignSystem gallery provide hot-reload-like iteration. TestFlight internal distribution to 100 team members needs no review (https://developer.apple.com/testflight/). |
| What you lose | Non-iOS collaborators cannot run the prototype without a device and a TestFlight invite. Browser-shareable links do not exist. |
| Translation cost | Zero. |
| Hidden risk | Over-investing in polish during exploration. Mitigated by the "paper, then ugly build, then one beautiful pass" cadence in the UX plan. |
| Verdict | Default. |

### Option T3: Build the engine in a portable form, UI natively

| Aspect | Assessment |
|--------|-----------|
| Variants | (a) Engine in Kotlin via KMP, consumed from SwiftUI. (b) Engine in Rust via UniFFI, consumed from Swift (and later Kotlin). (c) Engine in Swift, written as a pure package with a portable *specification*: the event schema (JSON), the reducer semantics, and a corpus of replay fixtures that any future implementation must pass. |
| What you get | (a)/(b): shared engine for Android later. (c): the *option* of a shared engine later at near-zero cost now, since the fixtures and schema are the portable asset, not the binary. |
| What you lose | (a): two toolchains, Gradle in a two-person iOS shop, experimental Swift export (today interop is Objective-C-header-shaped), Kotlin/Native runtime in the binary. (b): Rust toolchain, UniFFI bindings, debugging across the FFI, a third language. (c): nothing today; a Kotlin reimplementation later (estimated 3-4 engineer-weeks for an engine of this size, since the fixtures already define correctness). |
| Verdict | (c). The engine in `04-...` is already designed as pure value types plus a reducer, serialized events, and replay fixtures. That is a portable engine in every sense that matters for a 1-2 person iOS team. |

> **[ARCH]** I want to be precise about (c). "Portable in spirit" is hand-waving unless we commit to artifacts. The artifacts are: `MatchEvent` JSON schema versioned in `docs/engine-spec/`, a `fixtures/` directory of replay logs with expected final states, and a conformance test runner that any implementation can execute. Those three things make a Kotlin port a bounded task rather than archaeology.
>
> **[JOBS]** How much does that cost us this quarter?
>
> **[ARCH]** Nothing we were not already doing for testing and multiplayer. The fixtures are the bug-report format. The schema is the wire format. The runner is the unit test.
>
> **[IOS]** And if Swift on Android matures through the swift.org Android workgroup, the Swift package itself may simply compile for Android, and the fixtures prove it.
>
> **[JOBS]** Then the "translation step" the founder asked about is this: we translate *tests and schemas*, not code, and only when Android is real.

**DECISION:** Build natively from day one (T2). Keep the engine portable through artifacts, not a second language (T3c). Web prototyping (T1) is permitted for rules experiments by **[GAME]** only, with a rule that nothing from it is "ported"; it is reference material.

---

## 6. Recommendation

**Native SwiftUI, iOS 17 minimum, Swift 6, Xcode 16+, Swift Packages**, exactly as the shared brief assumes, with these refinements:

1. **UIKit where SwiftUI is not enough**, via `UIViewRepresentable`: text input in the round screen if `TextField` focus timing proves unreliable; `UIFeedbackGenerator` fallback when Core Haptics is unavailable.
2. **SpriteKit overlay** for ink particles (as `SpriteView` inside SwiftUI), with the Reduce Motion fallback being a static illustration. **Metal shaders via SwiftUI `.layerEffect`** for the ink-bleed on letter reveal (iOS 17+). Lottie or Rive are allowed only for authored illustrations, not for interactive state (keeps the engine-state-to-UI mapping in SwiftUI). Rive (https://rive.app/) is kept as a parallel pass for the letter-reveal animation because designers can author state machines directly; evaluate licensing and runtime size before adoption.
3. **iOS 17 minimum at launch**, re-evaluated in the quarter before launch. If a motion feature requires iOS 18 APIs (for example newer `TextRenderer` effects or mesh gradients), and iOS 18 adoption exceeds roughly 85% of active devices by Apple's own measurement at the time (Apple publishes adoption at https://developer.apple.com/support/app-store/), raise the minimum. Supporting a version almost nobody uses costs test time and holds back the feel.

> **[QA]** From a testing standpoint, each minimum OS version we keep adds a column to the device matrix. iOS 17 to 18 is one extra column; I can live with it. Below 17 is not on the table.

---

## 7. The parallel-pass alternative (what survives as skunkworks)

The founder asked for alternatives to be laid out as options or parallel passes. The ones worth a bounded exploration:

| Parallel pass | Scope (time-boxed) | What question it answers | Kill criteria |
|---------------|--------------------|---------------------------|---------------|
| **Rive letter-reveal** | 3 days, **[DESIGN]** + **[IOS]** | Can a designer-authored state machine beat hand-written SwiftUI keyframes for the ink reveal, at acceptable runtime size and with a Reduce Motion variant? | Runtime adds > 3 MB, or hitches on iPhone 11, or no clean Reduce Motion path. |
| **Engine conformance runner in Kotlin** | 2 days, **[ARCH]**, only after Phase 1 ships | Does the fixture corpus fully specify the engine? (Write a stub Kotlin reducer that passes 10 fixtures.) | Not run before App 1 launch. Pure insurance. |
| **Web rules sandbox** | 2 days, **[GAME]** | Fast iteration on scoring variants and house rules with non-engineers. | Never shipped; never "ported". |
| **Flutter Cupertino smoke test** | Not approved | Would reveal nothing we do not know. | n/a |
| **React Native shared-UI pass** | Not approved | Only becomes relevant if Android is a committed roadmap item with a web-heavy hire. | n/a |

> **[JOBS]** Two approved parallel passes and one deferred. That is a healthy skunkworks. Everything else is procrastination dressed as research.

---

## 8. Android roadmap implications

If Android becomes a goal (most plausibly for App 2, Kids, where Android share among families is significant in many markets):

| Path | Cost estimate (engineer-weeks) | Preconditions | Notes |
|------|-------------------------------|---------------|-------|
| **Kotlin + Compose reimplementation, engine ported from spec** | Engine 3-4; UI 10-14 for parity with App 1 v1; content packs reused as-is (data format is platform-neutral) | Fixture corpus and schema complete | Highest quality on Android; two codebases to maintain. |
| **Swift on Android** (swift.org Android workgroup) for the engine, Compose UI | Engine 1-2 if the package builds; UI 10-14 | Swift Android SDK production-ready for our dependencies (GRDB would need replacing or compiling SQLite) | Promising but not committed; check status at the time. |
| **KMP from day one** | +2-3 now; saves 3-4 later | Commit to Kotlin for the engine now | Rejected: pays now for a maybe. |
| **Flutter/RN rewrite of both** | 20+ | Abandon the native iOS app | Rejected; destroys the product's edge. |

The content pipeline (DAWG files, front-coded lists, signed manifests, licenses) is platform-neutral by construction and is the second portable asset after the engine spec. The design token file (`tokens.json`) is the third.

**DECISION:** Android is not on the 12-month roadmap. The three portable assets (engine spec plus fixtures, content packs, tokens) are maintained as if it were, because they cost nothing extra.

---

## 9. Risks of the recommendation and how we hedge

| Risk | Hedge |
|------|-------|
| SwiftUI bug in a specific iOS point release breaks a core screen (historically: `NavigationStack` and `TextField` focus issues) | UIKit escape hatches via representables; QA device matrix includes the oldest supported point release; phased release with pause. |
| Swift 6 strict concurrency slows UI work | Patterns documented in `04-...` Section 11; one engineer owns the concurrency conventions; `@preconcurrency` exceptions are listed. |
| Team member leaves; replacement is web-first | SwiftUI hiring is easy; the architecture docs and ADRs are the onboarding. |
| Apple changes a first-party API we depend on (Game Center, StoreKit) | Protocol boundaries in `IWMultiplayer` and the purchase layer; Apple deprecates slowly and announces at WWDC. |
| Founder later wants Android quickly | Section 8 paths; the portable assets make the engine a 3-4 week port rather than a rewrite. |

---

## 10. Decision record and open questions

**DECISION (ADR-001, confirmed):** Native SwiftUI on iOS 17+, Swift 6, Swift Packages. No cross-platform UI framework. No shared-logic framework in another language. Engine portability via schema, fixtures and conformance runner.

**DECISION:** Approved parallel passes: Rive letter-reveal (3 days), web rules sandbox (2 days, **[GAME]** only). Deferred: Kotlin conformance stub (post-launch).

**OPEN:** iOS 18 minimum at launch (decide in the quarter before submission based on Apple's published adoption).
**OPEN:** Rive adoption after the parallel pass.
**OPEN:** Whether App 2 (Kids) targets Android; if yes, start the Kotlin engine port concurrently with App 2 design, not after.

> **[JOBS]** Closing note. The founder said development could be anywhere and translated. The right answer is: development happens on the device, in the language of the device, and the only thing we "translate" is our test suite when we finally need another platform. That is what shipping at any cost looks like when the cost you refuse to pay is the feel.

---

## 11. Sources

- SwiftUI documentation: https://developer.apple.com/documentation/swiftui/
- Core Haptics: https://developer.apple.com/documentation/corehaptics
- Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Expo New Architecture guide: https://docs.expo.dev/guides/new-architecture/
- React Native: https://reactnative.dev/
- Flutter docs: https://docs.flutter.dev/ ; showcase: https://flutter.dev/showcase
- Kotlin Multiplatform for iOS: https://kotlinlang.org/docs/multiplatform/kmp-for-ios.html ; SwiftPM export: https://kotlinlang.org/docs/multiplatform/multiplatform-spm-export.html ; Swift export (experimental): https://kotlinlang.org/docs/native-swift-export.html ; KMP 2025 roadmap: https://blog.jetbrains.com/kotlin/2024/10/kotlin-multiplatform-development-roadmap-for-2025/
- Apple Unity plug-ins: https://github.com/apple/unityplugins
- Capacitor docs: https://capacitorjs.com/docs
- Swift Android workgroup: https://www.swift.org/android-workgroup/
- Shopify, five years of React Native (2025): https://www.infoq.com/news/2025/04/shopify-five-years-react-native ; Shopify Shop app rebuilt natively (2026 report): https://betterstack.com/community/guides/ai/shopify-react-native-to-native.md
- Airbnb, Sunsetting React Native (2018): https://medium.com/airbnb-engineering/sunsetting-react-native-1868ba28e30a
- TestFlight: https://developer.apple.com/testflight/
- App Store Review Guidelines (4.2 minimum functionality, 2.5 software requirements): https://developer.apple.com/app-store/review/guidelines/
- Apple platform adoption measurements: https://developer.apple.com/support/app-store/
- Rive: https://rive.app/
