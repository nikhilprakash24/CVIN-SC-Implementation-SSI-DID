# 09. Motion, Sound and Haptics (App 1, "Inkwell")

**Document status:** Draft v0.1, 2026-10-04. Owner: **[DESIGN — Design Director, "Sofia Lindqvist"]** with **[IOS — Lead iOS Engineer, "Marcus Oyelaran"]**. Contributors: JOBS, GAME, QA, ARCH.

**Read this if...** you are designing or implementing any animation, transition, sound or haptic in Inkwell, choosing between SwiftUI's animation APIs, Lottie, Rive, SpriteKit and Metal shaders, setting the frame budget, or planning how motion prototypes move from a designer's tool into Xcode. This document sets the motion principles with concrete numbers, catalogs 30 named animations with Reduce Motion alternatives, compares the implementation stacks with a bake-off plan, lays out three sound directions, maps haptics to Apple APIs, defines performance guardrails and describes the prototyping and handoff workflow. It depends on the directions and tokens in 07 and the screens in 08.

## Table of contents

1. Motion principles
2. Timing and easing tokens
3. Choreography rules
4. Animation catalog (30 animations)
5. Implementation stack comparison and bake-off
6. Sound design: three directions
7. Haptics map and API patterns
8. Performance guardrails
9. Prototyping plan and handoff
10. Team debates, decisions and open questions
11. Sources

---

## 1. Motion principles

Apple's HIG Motion page asks for animation that keeps people oriented, gives feedback and helps them learn, without overwhelming them, and the WWDC18 session "Designing Fluid Interfaces" adds that good motion is responsive, interruptible and redirectable. Sources: https://developer.apple.com/design/human-interface-guidelines/motion and https://developer.apple.com/videos/play/wwdc2018/803/

| # | Principle | Rule | Test |
|---|-----------|------|------|
| 1 | **One hero per screen** | Each screen has exactly one signature animation; everything else uses the standard transition set. | Count distinct custom animations when the screen appears. More than one, fail. |
| 2 | **Input is never blocked** | No animation delays a tap. Hero animations run while controls are live. | Tap the primary button during the hero. If the tap is ignored or queued, fail. |
| 3 | **Interruptible and redirectable** | Springs, not timed curves, for anything the user can interrupt; state-driven, not fire-and-forget. | Trigger a transition and reverse it halfway. If it snaps or finishes first, fail. |
| 4 | **Physical weight matches meaning** | 10 points lands harder than 5; a duplicate is a soft collision; a strike is a scratch. Visual, haptic and sound weights agree. | Describe the event with eyes closed from the haptic alone. Mismatch, fail. |
| 5 | **Reduce Motion is a design, not a switch** | Every animation has a named alternative that preserves the information (what changed) while removing movement. Flicker, parallax, scale-from-zero and large translations are removed, not shortened. | Enable Reduce Motion. Is every state change still perceivable? If information was lost, fail. |
| 6 | **Durations are tokens** | Only the values in section 2 are used. A new duration requires a new token and a design review. | Grep for literal durations in UI code. Any literal, fail. |
| 7 | **Nothing loops forever on a play screen** | Ambient loops are allowed only on the Lobby and Summary, and stop under Reduce Motion or Low Power Mode. | Leave the Round screen idle for 30 s. If anything is still moving other than the timer, fail. |

> **[JOBS]** Principle 2 is non-negotiable. I have never once enjoyed waiting for an app to finish being pretty. The letter writes itself, and if I am already typing before it finishes, good.
>
> **[DESIGN]** Principle 5 is where most apps cheat by making animations faster under Reduce Motion. Faster is still motion. We replace, we do not accelerate.

---

## 2. Timing and easing tokens

Research-backed ranges: roughly 100 ms reads as instant, 200 to 500 ms is the comfortable range for interface animation, and 1 s is the upper limit of a user's flow of thought. Source: Val Head's summary of Nielsen Norman Group and Model Human Processor findings, https://valhead.com/?p=2978. Apple's spring API uses `duration` and `bounce` parameters, per WWDC23 "Animate with springs": https://developer.apple.com/videos/play/wwdc2023/10158/

### 2.1 Duration tokens

| Token | Value | Use |
|-------|-------|-----|
| duration.instant | 0.08 s | pressed-state scale, selection ticks |
| duration.fast | 0.18 s | field focus, chip toggle, small fades |
| duration.base | 0.28 s | standard transitions, card flip |
| duration.slow | 0.42 s | hero entrances, sheet presentation |
| duration.hero | 0.60 s | the letter draw, totals tally |
| duration.reveal | 0.35 s per beat | reveal cadence per answer |
| duration.ambient | 6 to 12 s | Lobby background drift (Night Lounge only) |

### 2.2 Spring presets (SwiftUI `.spring(duration:bounce:)`)

| Token | duration | bounce | Feel | Use |
|-------|----------|--------|------|-----|
| spring.crisp | 0.28 | 0.05 | nearly critical, no overshoot | layout changes, field expand |
| spring.settle | 0.40 | 0.15 | one subtle overshoot | cards arriving, sheets |
| spring.bouncy | 0.55 | 0.35 | visible bounce | Playful Pop only; sticker drop |
| spring.snap | 0.22 | 0.20 | quick, tactile | chain link snap, chip pop |
| spring.heavy | 0.50 | 0.00 | overdamped, weighty | Night Lounge glass, totals |

Themes may remap which preset a motion role uses (for example `motion.cardArrive` is spring.settle in Paper & Ink and spring.bouncy in Playful Pop) but may not define new values.

### 2.3 Timing curves (for non-interruptible, fixed-length effects only)

| Token | Curve (cubic bezier) | Use |
|-------|----------------------|-----|
| ease.out | (0.16, 1, 0.3, 1) | entrances |
| ease.in | (0.7, 0, 0.84, 0) | exits |
| ease.inOut | (0.65, 0, 0.35, 1) | cross-fades |
| ease.draw | (0.4, 0, 0.2, 1) | path trim for the letter draw |

### 2.4 Stagger

| Token | Value | Use |
|-------|-------|-----|
| stagger.tight | 40 ms | category labels, chips |
| stagger.base | 60 ms | fields, list rows |
| stagger.reveal | 150 to 200 ms | reveal answer cards |

---

## 3. Choreography rules

1. **Enter from meaning.** Things arrive from where they come from: the next player's card from the right, the previous word from above, the letter from the pen (drawn), the score from the card it belongs to.
2. **Exit faster than you enter.** Exit durations are 70 percent of their entrance; exits never bounce.
3. **Stagger by hierarchy, not position.** The hero first, then primary content, then secondary, with the stagger tokens above. Never stagger more than 8 items; batch the rest.
4. **Shared elements persist.** The letter is a shared element between Lobby card, Round and Reveal (matchedGeometryEffect in SwiftUI; the iOS 18 zoom transition where available, per WWDC24 "Enhance your UI animations and transitions", https://developer.apple.com/videos/play/wwdc2024/10145/).
5. **Numbers roll, they do not fade.** Any changing number uses `contentTransition(.numericText())`. Source: https://developer.apple.com/documentation/swiftui/contenttransition
6. **Haptic on the landing frame.** Haptics fire when the animated object reaches its resting position, not when the animation starts, except for the letter draw which uses a pattern over the stroke.
7. **Celebrations are short.** No celebration runs longer than 1.2 s or blocks the "Play again" button.
8. **Theme motion flavor is a token.** Each theme sets `motion.flavor` (drawn, typographic, bouncy, electric, system) which selects among the catalog variants below; the triggers and information conveyed are identical across themes.

---

## 4. Animation catalog

Each entry: purpose, trigger, duration, easing or spring, Reduce Motion (RM) alternative, implementation option (first choice, then fallback). Theme variants are noted where the hero differs. "SwiftUI" means plain `withAnimation` or implicit animations; "Phase" and "Keyframe" refer to `PhaseAnimator` and `KeyframeAnimator` (https://developer.apple.com/documentation/swiftui/phaseanimator and https://developer.apple.com/documentation/swiftui/keyframeanimator, introduced in WWDC23 "Wind your way through advanced animations in SwiftUI", https://developer.apple.com/videos/play/wwdc2023/10157/). "Shader" refers to SwiftUI's `colorEffect`, `distortionEffect` and `layerEffect` Metal modifiers (https://developer.apple.com/documentation/swiftui/shader).

| ID | Name | Purpose | Trigger | Duration | Easing / spring | Reduce Motion alternative | Implementation |
|----|------|---------|---------|----------|-----------------|---------------------------|----------------|
| M01 | Letter Draw | Hero: the round's letter is written stroke by stroke | Round appears; Lobby card idle preview | 0.60 s | ease.draw on path trim, per-stroke | Letter fades in over 0.18 s with no stroke motion | SwiftUI `Shape.trim` on 26 pre-authored stroke paths; fallback Rive per-letter state machine |
| M02 | Type Slam (Swiss) | Hero variant: letter arrives at full size | Round appears | 0.22 s | spring.snap | Fade 0.18 s | SwiftUI scale 1.08 to 1.0 |
| M03 | Sticker Drop (Pop) | Hero variant: letter card falls and squashes | Round appears | 0.55 s | spring.bouncy, scaleY 0.92 on land | Fade 0.18 s | Keyframe (offsetY, scaleX, scaleY tracks) |
| M04 | Neon Flicker (Night) | Hero variant: letter flickers to full glow | Round appears | 0.42 s | Keyframe, 3 steps at 0.08, 0.20, 0.42 | Instant on, glow static; flicker fully disabled | Keyframe (opacity, glow radius); glow via `shadow` or Shader |
| M05 | System Roll (Minimal) | Hero variant: letter rolls in like a number | Round appears | 0.28 s | system default | numericText still allowed (it is a fade-roll); RM: plain fade | `contentTransition(.numericText())` |
| M06 | Fields Rise | Four answer fields appear | After M01 completes or at 0.3 s, whichever first | 0.28 s each, stagger.base | spring.crisp, offsetY 12 to 0 | Fields appear with 0.18 s fade, no offset | SwiftUI transition |
| M07 | Field Expand (Layout 3) | Focused field grows, others collapse | Focus change | 0.28 s | spring.crisp | Heights change without animation | SwiftUI layout animation |
| M08 | Letter Shrink for Keyboard | Letter clamps to 96 pt as keyboard rises | Keyboard will show/hide | 0.25 s matched to keyboard curve | system keyboard curve | Instant resize | SwiftUI with keyboard safe area |
| M09 | Timer Tension | Ring depletes; last 10 s thickens and warms; last 5 s pulses | Timer tick | continuous; pulse 0.5 s period | linear deplete; pulse ease.inOut | No pulse; color and numeral change only | SwiftUI `trim` on Circle; pulse via Phase |
| M10 | Ink Bleed on Submit | Submitted text softens then snaps crisp | Submit | 0.15 s soften, 0.10 s snap | ease.inOut | Text color deepens 0.18 s, no blur | Shader `layerEffect` blur radius 0 to 1.5 to 0; fallback `blur` modifier |
| M11 | Chain Link Snap | New word joins the chain, hero letter flips | Valid Word Chain submit | 0.22 s | spring.snap | Word fades in; hero letter cross-fades | SwiftUI offset plus `matchedGeometryEffect` |
| M12 | Duplicate Collision | Two matching answers pull together and bump | Duplicate detected (reveal or chain) | 0.40 s | spring.settle on approach, 0.08 s bump | Both items highlight with DuplicateBadge fading in | Keyframe (offsetX tracks); haptic double |
| M13 | Card Flip Reveal | Answer card turns face up | Reveal beat | 0.35 s | ease.inOut on rotation3D | Card content cross-fades | SwiftUI `rotation3DEffect` |
| M14 | Score Tally | Numbers count up to totals | Reveal end | 0.60 s | numericText with ease.out | Numbers change instantly, chip fades in | `contentTransition(.numericText())` |
| M15 | Score Chip Pop | 10 / 5 / 0 chip appears | Per card | 0.22 s | spring.snap, scale 0.6 to 1.0 | Fade 0.18 s | SwiftUI |
| M16 | Celebration: Ink Splatter (Paper) | Confetti alternative: ink drops splash and settle | Match Summary winner | 1.0 s | particles with gravity, ease.out fade | Static splatter image fades in | SpriteKit `SKEmitterNode` overlay; fallback pre-rendered Lottie |
| M17 | Celebration: Type Cascade (Swiss) | Letters of the winner's name drop into place | Summary | 0.80 s | spring.settle, stagger.tight | Name fades in | SwiftUI stagger |
| M18 | Celebration: Confetti (Pop) | Classic confetti burst | Summary | 1.2 s | particles | Static confetti image | SpriteKit emitter |
| M19 | Celebration: Neon Sign On (Night) | "WINNER" sign lights segment by segment with hum | Summary | 0.9 s | Keyframe steps | Sign on, static, no flicker | Keyframe plus glow |
| M20 | Page Turn (theme transition) | Canvas cross-fade when theme changes | Theme applied | 0.35 s | ease.inOut | Instant cut | SwiftUI opacity cross-fade on canvas only |
| M21 | Pass Hold Fill | Hold-to-start fills the button | Press and hold | 0.60 s (configurable 0.3 to 1.2) | linear | Same fill (it is user-driven, allowed) | SwiftUI `trim` or mask |
| M22 | Pass Reveal | Interstitial lifts to reveal the Round | Hold completes | 0.42 s | spring.settle, offsetY to -100 percent | Cross-fade 0.2 s | SwiftUI transition |
| M23 | Shake (invalid) | Field shakes twice | Invalid submit | 0.30 s | Keyframe offsetX 0, -6, 6, -3, 0 | No shake; underline turns danger, helper text appears | Keyframe |
| M24 | Life Pip Break | A life indicator cracks and dims | Life lost | 0.35 s | ease.in, scale 1.0 to 0.85 | Pip dims instantly with strikethrough glyph | SwiftUI; Paper theme uses a 3-frame pencil-snap Lottie |
| M25 | Bot Thinking Dots | Three ink dots pulse | Bot turn | loop, 0.9 s period, max 2.5 s | ease.inOut | Static "Thinking" text | Phase (3 phases) |
| M26 | Chip Select | Category chip toggles | Tap | 0.18 s | spring.crisp, scale 1.0 to 1.04 to 1.0 | Color change only | SwiftUI |
| M27 | Button Press | Primary button scales | Press down / up | 0.08 s down, 0.18 s up | ease.out | Opacity dip to 0.85 | SwiftUI `ButtonStyle` |
| M28 | Toast In/Out | Non-blocking message | Event | 0.28 s in, 0.20 s out, 3 s hold | spring.settle / ease.in | Fade in and out | SwiftUI transition |
| M29 | Lobby Ambient Drift (Night) | Gradient behind glass drifts slowly | Lobby idle | 8 s loop | linear, hue rotate 10 degrees | Static gradient | Shader `colorEffect` with time; off in Low Power Mode |
| M30 | Paper Grain (Paper) | Static grain at 3 to 4 percent | Always | n/a (static) | n/a | Unchanged (no motion) | Shader `colorEffect` noise; fallback tiled PNG |
| M31 | Zoom to Round | Lobby card zooms into the Round screen | Tap Play | system | iOS 18 zoom transition; iOS 17 `matchedGeometryEffect` on the letter | Cross-fade | SwiftUI `navigationTransition(.zoom)` (iOS 18) with fallback |
| M32 | Challenge Sheet Rise | Sheet presents with verdict stamp landing | Long press on a card | system sheet; stamp 0.22 s | spring.snap on stamp scale | Stamp fades in | System sheet plus SwiftUI |

Per-theme hero mapping: Paper & Ink uses M01, M10, M16, M30; Swiss uses M02, M17; Pop uses M03, M18; Night Lounge uses M04, M19, M29; Minimal uses M05 and system transitions. All other entries are shared.

> **[GAME]** M12 is the most important animation in the app after the letter draw. The duplicate collision is the moment the room laughs. It needs to be legible from across a table: the two cards must visibly move toward each other, not just highlight. Four hundred milliseconds is right; shorter and nobody sees it.
>
> **[IOS]** Noted. M12 under Reduce Motion loses the movement, so the DuplicateBadge plus a brief shared background tint must carry the moment. I will build both and we test with Reduce Motion users before locking.
>
> **[QA]** Every entry in this table becomes two test cases: motion on and Reduce Motion on. That is 64 cases plus theme variants. We automate the Reduce Motion half with snapshot tests at the final frame.

---

## 5. Implementation stack comparison and bake-off

### 5.1 Options

| Stack | What it is | Best for | Pros | Cons | Binary and asset size | Designer workflow |
|-------|-----------|----------|------|------|-----------------------|-------------------|
| **SwiftUI core** (implicit/explicit animations, springs, `matchedGeometryEffect`, transitions) | Apple's built-in animation system | Layout changes, transitions, state-driven motion (M06, M07, M11, M13, M20, M22, M26 to M28) | Zero dependencies; interruptible springs by default; Dynamic Type and theme aware; accessibility free | Hard to express multi-track, timed choreography; no designer authoring tool | 0 | Designer specs tokens in Figma; engineer implements; iterate in Xcode Previews |
| **SwiftUI PhaseAnimator / KeyframeAnimator** (iOS 17) | Multi-step and multi-track animation in SwiftUI | Timed choreography: M03, M04, M09 pulse, M12, M19, M23, M25 | Still native; keyframe tracks for position, scale, opacity; works with Reduce Motion checks | Values hand-authored in code; no visual timeline | 0 | Designer provides keyframe tables; engineer transcribes; Previews for review |
| **Lottie** (airbnb/lottie-ios) | After Effects vector animation playback | Pre-authored illustrative moments: M24 pencil snap, fallback for M16 | Mature; huge ecosystem; Core Animation rendering engine (default in 4.x) offloads playback to the render server; dotLottie compresses to a few KB | JSON can bloat for complex art; limited runtime interactivity (markers, not state machines); After Effects skill required | Library via `lottie-spm` is small; animations typically under 10 KB, dotLottie 3 to 4 KB average | Designer in After Effects with Bodymovin; exports JSON or .lottie; engineer drops into bundle |
| **Rive** (rive-app/rive-ios) | Vector animation with state machines and runtime inputs | Interactive hero: M01 letter state machine (26 letters, draw, idle, shrink), M12 collision with inputs | Binary files roughly 10 to 15 times smaller than equivalent Lottie per Rive; state machines let designers own interaction logic; Metal renderer | Extra runtime (C++ core); iOS 14+ runtime adds binary size; one more tool to learn; in-process Metal allocation shows in memory profiles | Runtime adds several MB to the app; .riv files typically tens of KB | Designer owns Rive editor and state machine; engineer binds inputs via `RiveViewModel` in SwiftUI |
| **SpriteKit particles** (`SKEmitterNode`) | Apple's 2D engine, used as an overlay view | Particles: M16, M18 | Native; Xcode particle editor; cheap for hundreds of particles | Overlay view bridging into SwiftUI; must be paused when offscreen; not for UI motion | 0 | Designer tunes in Xcode's `.sks` editor with engineer; parameters are a short table |
| **Metal via SwiftUI Shader** (`colorEffect`, `distortionEffect`, `layerEffect`) | Per-pixel effects on SwiftUI views | Ink bleed M10, paper grain M30, ambient drift M29, optional CRT in Night Lounge | GPU-cheap for full-screen effects; native; small `.metal` files | Requires shader skills; debugging is harder; `layerEffect` sampling costs scale with blur radius; must be disabled on unsupported devices | KB | Designer provides reference frames; engineer writes shader; tune parameters live in Previews |

Sources: Lottie iOS repository and SPM note, https://github.com/airbnb/lottie-ios; Lottie 4.0 Core Animation engine default, https://github.com/airbnb/lottie-ios/releases/tag/4.0.0; dotLottie compression, https://lottiefiles.com/blog/working-with-lottie-animations/optimize-lottie-files-for-faster-page-load-speeds; Rive iOS runtime, https://github.com/rive-app/rive-ios and https://rive.app/docs/runtimes/apple; Rive's file-size claim, https://rive.app/blog/rive-as-a-lottie-alternative (vendor source, verify in the bake-off); LottieFiles' comparison, https://lottiefiles.com/blog/lottie-animations/lottiefiles-or-rive (vendor source); SpriteKit emitters, https://developer.apple.com/documentation/spritekit/skemitternode and https://developer.apple.com/documentation/spritekit/creating-particle-effects; SwiftUI Shader, https://developer.apple.com/documentation/swiftui/shader.

### 5.2 Recommendation

- **Default:** SwiftUI core plus PhaseAnimator and KeyframeAnimator for everything that is UI. This covers 24 of 32 catalog entries with zero dependencies.
- **Letter Draw (M01):** SwiftUI `Shape.trim` over 26 hand-authored stroke paths is the first choice; it is native, themeable (stroke color and width from tokens) and Reduce Motion friendly. Rive is the parallel pass if the designer wants richer per-letter character (pen pressure, idle wobble).
- **Particles (M16, M18):** SpriteKit overlay, paused when not visible.
- **Ink and grain (M10, M29, M30):** SwiftUI Shader, with static image fallbacks for devices where the bake-off shows frame drops.
- **Lottie:** allowed only for small illustrative loops (M24) where After Effects is faster than code. No Lottie for anything interactive.
- **Rive:** skunkworks for the letter and the Pop sticker system. Not in the v1 critical path.

### 5.3 Bake-off plan (1.5 engineer-weeks; scheduled in the delivery plan's skunkworks track as the W7 to W8 Rive/Lottie/native bake-off and the W9 to W11 ink-shader prototype)

| Step | What | Exit criterion |
|------|------|----------------|
| 1 | Build M01 three ways: SwiftUI trim, Rive, Lottie | Side-by-side video at 120 fps on iPhone 15 Pro and 60 fps on iPhone 12; per-frame CPU and GPU in Instruments |
| 2 | Build M10 ink bleed with `layerEffect` and with the `blur` modifier | Both under 2 ms GPU per frame on iPhone 12; pick the one with the better look |
| 3 | Build M30 grain as shader and as tiled PNG | Measure battery over a 10-minute session; shader must be within 3 percent of PNG or PNG wins |
| 4 | Build M16 with SpriteKit and with Lottie pre-render | Frame time under 8 ms during the burst on iPhone 12 |
| 5 | Add Rive runtime to a test build and measure cold launch and binary size delta | Launch delta under 50 ms and binary under 6 MB added, or Rive stays skunkworks |
| 6 | Reduce Motion variants for all of the above | Snapshot tests pass; QA review with a Reduce Motion user |

> **[ARCH]** Dependency rule for v1: at most one third-party animation runtime in the shipping binary. If Rive wins the letter, Lottie goes, and vice versa. Two runtimes for one app this size is unjustifiable.
>
> **[DESIGN]** I want Rive to win because it lets me own the letter's personality without a code round-trip. But I accept the rule. If SwiftUI trim gets 90 percent of the way, we ship that and I keep Rive in the skunkworks track for v1.5.
>
> **[IOS]** SwiftUI trim will get 95 percent of the way for a monoline letter. Pen pressure variation is the 5 percent, and I can fake it with a tapered stroke shader later. Rive is a great tool; it is also a C++ runtime inside an app whose entire pitch is "perfect and tiny".
>
> **DECISION:** SwiftUI-first stack. Bake-off decides M01 and shader fallbacks. One third-party runtime maximum, chosen by the bake-off, possibly none.

---

## 6. Sound design: three directions

All directions share the rules: sound respects the silent switch and the in-app master toggle; no sound without a visual; no music during a round; sounds under 400 ms except the ambient Lobby bed; peak loudness normalized across the set; sounds are per theme and delivered as part of the theme bundle. Reference for pairing audio and haptics: WWDC19 "Designing Audio-Haptic Experiences", https://developer.apple.com/videos/play/wwdc2019/810/

### 6.1 Direction S1: Foley (Paper & Ink default)

Real recorded sounds: pencil on paper, page turn, eraser, a wooden "tock" for duplicates, paper slap for time's up. Reference: Untitled Goose Game's sound, which gets its charm from physical realism of ordinary objects and a single-instrument score that follows the action. Source: FMOD interview, https://www.fmod.com/blog/untitled-goose-game-interview

- Pros: matches the material honesty principle; ages well; unobtrusive in a room of people.
- Cons: needs real recording or licensed foley; can sound cheap if low-fidelity.
- Production: 24 clips, recorded in one session, one day of editing.

### 6.2 Direction S2: Tonal minimal (Swiss Editorial, Quiet Minimal)

Short synthesized tones: a clean click for submit, a lower click for duplicate, a two-note rise for totals, a soft chime for winner. Reference: Apple's own system sounds and the restraint of Threes!, whose audio is sparse and tuned to the tile motion. Source: https://en.wikipedia.org/wiki/Threes

- Pros: cheapest to produce; consistent across themes; never clashes with speech.
- Cons: generic; little personality.
- Production: 12 tones, one afternoon with a synth.

### 6.3 Direction S3: Electric lounge (Night Lounge)

A low synth pad on the Lobby, bass thump on submit, buzzer for time's up, neon hum under the winner sign, marimba-like plinks for correct chain links. Reference: Balatro's layered, satisfying feedback where every action has a "juicy" sound tied to a visual. Source: https://blakecrosley.com/guides/design/balatro

- Pros: strongest vibe; makes the paid theme feel premium.
- Cons: most expensive; music licensing or composition; must duck when VoiceOver speaks.
- Production: composer, 3 to 5 days, plus 20 effects.

### 6.4 Comparison and recommendation

| Criterion | S1 Foley | S2 Tonal | S3 Electric |
|-----------|:-:|:-:|:-:|
| Fits default theme | 5 | 3 | 1 |
| Party-room legibility | 4 | 3 | 5 |
| Production cost | 3 | 5 | 2 |
| VoiceOver coexistence | 5 | 5 | 3 |
| Premium feel | 4 | 2 | 5 |

**Recommendation:** S1 ships as the default sound pack. S2 ships as the pack for Swiss and as the fallback when a theme has no pack. S3 is produced for Night Lounge and ships with the Pro unlock. Sound packs are theme bundle contents, not separate purchases.

> **[GAME]** One more rule: the duplicate sound must be funny without being a cartoon. The wooden tock in S1 is right. A "boing" is wrong for App 1 and right for Kids.
>
> **[JOBS]** And no sound on launch. Ever. The first sound the user hears is caused by something they did.

---

## 7. Haptics map and API patterns

Two API layers, both documented by Apple:

- **System patterns via SwiftUI** `sensoryFeedback(_:trigger:)` (iOS 17): `.impact(weight:intensity:)`, `.selection`, `.success`, `.warning`, `.error`, `.increase`, `.decrease`, `.alignment`, `.levelChange`, `.start`, `.stop`. Source: https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:). Under UIKit these correspond to `UIImpactFeedbackGenerator`, `UISelectionFeedbackGenerator` and `UINotificationFeedbackGenerator`.
- **Custom patterns via Core Haptics**: `CHHapticEngine`, `CHHapticPattern`, `CHHapticPatternPlayer`, and AHAP files (Apple Haptic and Audio Pattern, a JSON-like format that can bundle synced audio). Sources: https://developer.apple.com/documentation/corehaptics, https://developer.apple.com/documentation/corehaptics/chhapticengine, https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files, https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file, and WWDC19 "Introducing Core Haptics", https://developer.apple.com/videos/play/wwdc2019/520/

### 7.1 Semantic haptic roles

| Role token | Pattern | API | Parameters |
|------------|---------|-----|------------|
| haptic.tap | light impact | sensoryFeedback `.impact(weight: .light)` | |
| haptic.select | selection | `.selection` | |
| haptic.submit | medium impact | `.impact(weight: .medium)` | |
| haptic.score10 | rigid impact | `.impact(weight: .rigid, intensity: 0.9)` | |
| haptic.score5 | two soft impacts | Core Haptics, 2 transients at 0 and 80 ms, intensity 0.5, sharpness 0.3 | AHAP `duplicate.ahap` |
| haptic.score0 | none | | silence is the signal |
| haptic.penScratch | three faint transients along the stroke | Core Haptics, transients at 0, 220, 440 ms, intensity 0.3, sharpness 0.8 | AHAP `pen.ahap`; theme Paper only |
| haptic.flicker | three quick taps | Core Haptics, transients at 0, 80, 200 ms, intensity 0.4 to 0.8 rising | AHAP `neon.ahap`; Night only; disabled under Reduce Motion |
| haptic.tally | continuous decaying | Core Haptics continuous event 700 ms, intensity curve 0.6 to 0.0, sharpness 0.4 | AHAP `tally.ahap` |
| haptic.linkSnap | rigid impact | `.impact(weight: .rigid)` | |
| haptic.lifeLost | error | `.error` | |
| haptic.timeUp | warning | `.warning` | |
| haptic.timerTick | light impact | `.impact(weight: .light, intensity: 0.5)` | last 10 s only; user toggle |
| haptic.holdFill | selection at start, continuous ramp, success at end | Core Haptics continuous 600 ms intensity 0.2 to 0.6 then `.success` | AHAP `hold.ahap` |
| haptic.themeApply | soft impact | `.impact(weight: .soft)` | |
| haptic.purchase | success | `.success` | |

### 7.2 Patterns and rules

- Prepare the engine on the Round screen appear (`CHHapticEngine.start()`), stop it on disappear, and handle `resetHandler` and `stoppedHandler` so audio interruptions do not leave the engine dead.
- Use system patterns wherever they fit; custom AHAP only for the eight roles that have a pattern identity (pen, duplicate, flicker, tally, hold and three theme variants).
- Haptic intensity has a user setting (Off, Light, Standard) that scales custom pattern intensity and maps system patterns down one weight at Light.
- No haptic fires without a visual counterpart; no two haptics within 60 ms except the designed duplicate double.
- Devices without a Taptic Engine (iPad) get no haptics and no visual change; sound carries the weight.

> **[IOS]** AHAP files live in the theme bundle next to sounds, keyed by role. The haptic role table above is literally the dictionary keys. That gives DESIGN the ability to tune a theme's haptics without a code change.

---

## 8. Performance guardrails

| Guardrail | Budget | How we measure |
|-----------|--------|----------------|
| Frame time, any screen, iPhone 12 (60 Hz) | under 16.7 ms p99; under 8 ms p50 | Instruments Animation Hitches and Core Animation FPS; CI run of a scripted reveal |
| Frame time, iPhone 15 Pro (120 Hz ProMotion) | under 8.3 ms p99 | same |
| Hitches during hero animations | 0 per hero | Hitch trace in Instruments |
| GPU time for shaders (M10, M29, M30) | under 2 ms per frame on iPhone 12 | Metal System Trace |
| Particles (M16, M18) | 300 particles max; emitter stops at 1.2 s; node removed at 2 s | Code review and SpriteKit debug stats |
| Cold launch to interactive Lobby | under 400 ms on iPhone 12 | XCTest launch metrics |
| Added binary size for animation runtimes | under 6 MB total | App thinning report |
| Memory during reveal with 8 players | under 150 MB | Memory Graph |
| Battery, 10-minute session, grain shader on | within 3 percent of shader off | Energy Log |

When to pre-render instead of animating live: any effect that is identical every time (M24 pencil snap, Paper celebration splatter shape) is a candidate for a Lottie or image sequence; any effect that depends on content (letter, words, names, scores) is always live. Shaders are disabled automatically in Low Power Mode and on devices below A12 (ARCH to confirm the device floor with the iOS 17 minimum).

> **[QA]** Performance tests run on real devices in CI, not simulators. A simulator frame time is a rumor.
>
> **[IOS]** And every hero animation ships with a debug toggle that slows it 10x so DESIGN can review easing in Previews and QA can take frame-accurate snapshots.

---

## 9. Prototyping plan and handoff

### 9.1 Tools by purpose

| Tool | Use in Inkwell | Strength | Limit |
|------|----------------|----------|-------|
| Figma (with variables and Dev Mode) | Static screens, tokens, component states, redlines | Source of truth for layout and tokens; Dev Mode exposes specs and variables to engineers. Source: https://help.figma.com/hc/articles/15023124644247 | Weak for physics and timing |
| Principle | Quick timing studies for single interactions (field expand, chip pop) | Fast; imports from Figma; good for communicating easing. Source: https://principleformac.com/ | Not physically based; export is video only |
| Origami Studio | Gesture-driven prototypes (pass hold, chain swipe) with real springs and sensor input | Patch-based; built for exactly this kind of fluid interaction work. Source: https://origami.design/documentation/ | Learning curve; prototypes do not ship |
| Rive editor | Letter state machine exploration and the Pop sticker system (skunkworks) | Designer-owned interactive motion; runtime-ready | Ships only if the bake-off approves the runtime |
| Xcode Previews with SwiftUI | The actual motion, reviewed on device via Previews on iPhone | Reviewing the real thing; theme and Dynamic Type switches live | Requires an engineer or a designer comfortable editing token values |

### 9.2 Process

1. **Motion brief** (DESIGN): one page per hero animation with the catalog row, a reference video and the Reduce Motion alternative.
2. **Timing study** (DESIGN in Principle or Origami): 2 to 3 variants; team picks one in a 15-minute review on device, not on a projector.
3. **Token transcription** (DESIGN plus IOS): durations, springs and keyframe tables go into the theme JSON; no literal numbers in code.
4. **Implementation in Previews** (IOS): the animation is built as a SwiftUI Preview with a slow-motion toggle and a Reduce Motion toggle.
5. **Side-by-side review** (DESIGN, IOS, JOBS): prototype and implementation on two phones. Differences are logged as token changes or as accepted deviations.
6. **Lock** (QA): snapshot tests for Reduce Motion final frames; hitch tests for motion; the catalog row is marked Locked.

### 9.3 Handoff artifacts

- Theme JSON with motion tokens, exported from Figma variables.
- Letter stroke paths as SVG (26 files) with stroke order metadata.
- AHAP files and sound clips named by role.
- A motion spec sheet per hero (Figma page) linking to the Preview.
- Particle `.sks` files for M16 and M18.

> **[JOBS]** Demos, not slides. Every motion review happens on a phone in someone's hand. If the review is a Keynote with a GIF, it did not happen.
>
> **[DESIGN]** Agreed, with one ask: give me the slow-motion toggle in a hidden developer menu on TestFlight builds so I can review on my own phone without Xcode.
>
> **DECISION:** Figma for tokens and screens, Principle or Origami for timing studies, Xcode Previews for the truth. Hidden developer menu with 10x slow motion and Reduce Motion override in internal builds.

---

## 10. Team debates, decisions and open questions

### Debate: springs everywhere versus authored curves

> **[IOS]** Springs for everything. They are interruptible, they compose, and Apple's own apps use them. Timed curves are for video.
>
> **[DESIGN]** Springs for everything the user can interrupt. But the letter draw and the reveal cadence are performances; a spring on a path trim looks wrong, and a reveal with eight players needs a fixed cadence or it drifts. Authored curves for those two.
>
> **[GAME]** The reveal cadence is a rhythm. Rhythms are fixed. Side with DESIGN on the reveal.
>
> **DECISION:** Springs for interactive and layout motion; authored curves only for the letter draw path trim and the reveal cadence. Both are listed in section 2.3.

### Debate: how much motion is too much for a party game

> **[JOBS]** I watched a build where every chip, every row and every badge bounced. It felt like a slot machine. The letter and the duplicate collision are the show. Everything else should be furniture.
>
> **[DESIGN]** That is principle 1. The catalog has 32 entries, but a given screen shows one hero and a handful of standard transitions. The Reveal is the exception: it is a choreographed sequence by nature, and even there each beat is small.
>
> **[QA]** From a testing view, fewer unique motions means fewer Reduce Motion variants and fewer hitches. I will push back on any new catalog entry without a removed one.
>
> **DECISION:** The catalog is capped at 32 for v1. New entries require retiring one.

### Open questions

1. **OPEN:** M01 implementation (SwiftUI trim versus Rive) pending bake-off step 1 and 5.
2. **OPEN:** Grain as shader versus static PNG pending battery measurement (step 3).
3. **OPEN:** Whether the Night Lounge CRT scanline option ships in v1 (needs its own GPU budget and a photosensitivity review).
4. **OPEN:** Timer tick haptic default on or off; GAME suspects it adds tension, QA suspects it annoys. Resolve with a small TestFlight survey.
5. **OPEN:** iOS 18 zoom transition (M31) requires iOS 18; the iOS 17 fallback is `matchedGeometryEffect`. Confirm whether the dual path is worth it or whether v1 ships the fallback only.

---

## 11. Sources

- HIG Motion: https://developer.apple.com/design/human-interface-guidelines/motion
- HIG Playing haptics: https://developer.apple.com/design/human-interface-guidelines/playing-haptics
- HIG Playing audio: https://developer.apple.com/design/human-interface-guidelines/playing-audio
- WWDC18 Designing Fluid Interfaces: https://developer.apple.com/videos/play/wwdc2018/803/
- WWDC19 Designing Audio-Haptic Experiences: https://developer.apple.com/videos/play/wwdc2019/810/
- WWDC19 Introducing Core Haptics: https://developer.apple.com/videos/play/wwdc2019/520/
- WWDC19 Visual Design and Accessibility: https://developer.apple.com/videos/play/wwdc2019/244/
- WWDC23 Animate with springs: https://developer.apple.com/videos/play/wwdc2023/10158/
- WWDC23 Wind your way through advanced animations in SwiftUI: https://developer.apple.com/videos/play/wwdc2023/10157/
- WWDC24 Enhance your UI animations and transitions: https://developer.apple.com/videos/play/wwdc2024/10145/
- SwiftUI PhaseAnimator: https://developer.apple.com/documentation/swiftui/phaseanimator
- SwiftUI KeyframeAnimator: https://developer.apple.com/documentation/swiftui/keyframeanimator
- SwiftUI Shader (colorEffect, distortionEffect, layerEffect): https://developer.apple.com/documentation/swiftui/shader
- SwiftUI ContentTransition: https://developer.apple.com/documentation/swiftui/contenttransition
- SwiftUI sensoryFeedback: https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:)
- SwiftUI accessibilityReduceMotion environment value: https://developer.apple.com/documentation/swiftui/environmentvalues
- Core Haptics: https://developer.apple.com/documentation/corehaptics
- CHHapticEngine: https://developer.apple.com/documentation/corehaptics/chhapticengine
- Representing haptic patterns in AHAP files: https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files
- Playing a custom haptic pattern from a file: https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file
- SpriteKit SKEmitterNode: https://developer.apple.com/documentation/spritekit/skemitternode
- SpriteKit Creating particle effects: https://developer.apple.com/documentation/spritekit/creating-particle-effects
- App Store Connect Reduced Motion evaluation criteria: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria
- Lottie iOS: https://github.com/airbnb/lottie-ios and the 4.0 release notes https://github.com/airbnb/lottie-ios/releases/tag/4.0.0
- dotLottie compression: https://lottiefiles.com/blog/working-with-lottie-animations/optimize-lottie-files-for-faster-page-load-speeds
- Rive iOS runtime: https://github.com/rive-app/rive-ios and https://rive.app/docs/runtimes/apple
- Rive as a Lottie alternative (vendor): https://rive.app/blog/rive-as-a-lottie-alternative
- LottieFiles or Rive (vendor): https://lottiefiles.com/blog/lottie-animations/lottiefiles-or-rive
- Animation duration research summary (Val Head, citing Nielsen Norman Group): https://valhead.com/?p=2978
- Figma Dev Mode: https://help.figma.com/hc/articles/15023124644247
- Origami Studio documentation: https://origami.design/documentation/
- Principle: https://principleformac.com/
- Untitled Goose Game sound (FMOD interview): https://www.fmod.com/blog/untitled-goose-game-interview
- Balatro feedback design breakdown: https://blakecrosley.com/guides/design/balatro
- Threes!: https://en.wikipedia.org/wiki/Threes
