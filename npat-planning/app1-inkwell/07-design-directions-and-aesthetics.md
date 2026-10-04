# 07. Design Directions and Aesthetics (App 1, "Inkwell")

**Document status:** Draft v0.1, 2026-10-04. Owner: **[DESIGN — Design Director, "Sofia Lindqvist"]** with **[JOBS — Product Lead, "Theo Marr"]** as co-owner of taste decisions. Contributors: IOS, GAME, QA, ARCH.

**Read this if...** you are deciding what Inkwell should look and feel like, building the `IWDesignSystem` Swift package (called DesignSystem in this document for short), choosing fonts and colors, or arguing about whether the app should feel like a notebook, a magazine, a toy, a bar, or a system app. This document lays out five complete visual directions as parallel passes, compares them, recommends a default, and defines the design-system foundations (tokens, type ramp, spacing, components, states) that every direction must be expressible in. Read 08 for screens and flows, 09 for motion, sound and haptics.

## Table of contents

1. Design principles (with a test for each)
2. How to read the five directions
3. Direction A: Paper & Ink
4. Direction B: Swiss Editorial
5. Direction C: Playful Pop
6. Direction D: Night Lounge
7. Direction E: Quiet Minimal
8. Comparison matrix
9. Recommendation: default direction, themes, parallel passes
10. Theming architecture
11. Design-system foundations
12. Component inventory and state matrix
13. Iconography grid and app icon
14. Naming options (brief)
15. Risks
16. Decisions and open questions
17. Sources

---

## 1. Design principles

Each principle comes with a test you can apply to any screen in a design review. If a screen fails the test, it is not done.

| # | Principle | What it means | The test |
|---|-----------|---------------|----------|
| 1 | **The letter is the hero** | In NPAT the drawn letter is the whole game; in Word Chain the last letter of the previous word is the whole game. Nothing on screen may compete with it. | Squint at the screen. Is the active letter the first thing you see? If the timer, a button or a banner wins, fail. |
| 2 | **Play in ten seconds, no account** | First-run must reach a live round within ten seconds with no sign-in, no permission prompt, no tutorial carousel. | Stopwatch from app-icon tap to the first editable field. Over 10 s, fail. Any modal before play, fail. |
| 3 | **One hero moment per screen** | Each screen earns exactly one signature animation or visual flourish. Everything else is quiet. | Count the things that move or glow when the screen appears. More than one, fail. |
| 4 | **Legible at Accessibility XXXL** | Every screen must remain usable at the largest Dynamic Type size and with Bold Text on. Layout reflows; it never truncates game-critical text. | Set Dynamic Type to AX5 in Settings. Can you still play a full NPAT round? If any field or score is clipped, fail. |
| 5 | **Honest materials** | Paper looks like paper only where it behaves like paper (it can be written on). Glass is glass only where content passes behind it. No decoration that lies about affordance. | Point at any texture or material and ask "what does this do?" If the answer is "it looks nice", fail. |
| 6 | **Feedback is physical** | Every submit, duplicate, score and timer event has a matched visual, haptic and (optional) sound. The three never disagree in weight. | Trigger an event with sound on and eyes closed. Does the haptic alone tell you what happened? If not, fail. |
| 7 | **Themes change clothes, not bones** | A theme may change color, type, texture, motion flavor and sound. It may not change layout, hierarchy, or interaction. | Swap themes mid-screen. Did any tap target move? If yes, fail. |

> **[JOBS]** Principle 2 is the one I will personally test on every build. If I tap the icon and see a sign-in sheet, a notification permission prompt or a "swipe to learn more" carousel, the build is rejected. I do not care how pretty it is.
>
> **[DESIGN]** Agreed, and principle 7 is the one that protects us from ourselves. Five directions sounds like five apps. It is one app with one skeleton and five skins. If a direction cannot be expressed as tokens over the same skeleton, it is not a theme, it is a fork, and we do not ship forks.
>
> **[IOS]** Principle 4 is the expensive one. Five directions times three Dynamic Type bands times light and dark is 30 visual states per screen. We need the token architecture in section 10 before anyone opens Figma, otherwise we will hand-tune 30 variants.
>
> **DECISION:** Principles 1 to 7 adopted as review gates. Each screen in 08 lists which principle tests it has passed.

Reference: Apple's Human Interface Guidelines foundations, especially [Typography](https://developer.apple.com/design/human-interface-guidelines/typography), [Color](https://developer.apple.com/design/human-interface-guidelines/color), [Materials](https://developer.apple.com/design/human-interface-guidelines/materials), [Layout](https://developer.apple.com/design/human-interface-guidelines/layout), [Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode), [Motion](https://developer.apple.com/design/human-interface-guidelines/motion) and [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility). If any of these paths move, start from the HIG root at https://developer.apple.com/design/human-interface-guidelines/.

---

## 2. How to read the five directions

Each direction is specified on the same template so they can be compared honestly:

- Name and one-line vibe
- Mood references (real products, cited)
- Color palette (hex, light and dark)
- Typography (iOS system fonts or licensable faces, with fallbacks)
- Materials and texture
- Iconography and illustration
- Signature motion idea (detailed in 09)
- Sound and haptic character (detailed in 09)
- How the NPAT grid and the Word Chain chain are represented
- Risks and effort

Every direction must satisfy the design-system foundations in section 11 and must pass all seven principle tests. The directions differ in tokens, not in structure.

> **[GAME]** One framing before the tour. NPAT and Word Chain have different emotional shapes. NPAT is a pressure cooker: one letter, a countdown, four blanks, and then a reveal where you find out who else wrote "Paris". Word Chain is a relay: calm, turn by turn, and tension comes from the chain getting long. A direction that nails the pressure cooker may undersell the relay. Watch for that in each pass.

---

## 3. Direction A: Paper & Ink

**One-line vibe:** The notebook you played this in at school, remembered better than it was.

**Mood references**
- Letterpress by Loren Brichter (atebits), for how a word game can be tactile and spare at the same time, with tiles that tilt and jiggle when picked up. Source: Game Developer, "7 design lessons from Letterpress", https://www.gamedeveloper.com/business/7-design-lessons-from-i-letterpress-i-
- Monument Valley (ustwo), for restraint in palette and the idea that every screen is a composed picture. Source: https://ustwo.com/work/monument-valley/
- Field Notes memo books and Leuchtturm dot-grid paper (print references, not apps): warm off-white stock, faint grid, one accent color on the cover.
- Baba Is You, for proof that a wobbly, hand-drawn feel can read as deliberate rather than cheap. Source: PC Gamer review, https://www.pcgamer.com/baba-is-you-review/

**Color palette**

| Role | Light | Dark |
|------|-------|------|
| Canvas (paper) | `#F6F1E7` warm cream | `#1C1A17` charcoal paper |
| Canvas grid lines | `#E6DFD0` | `#2A2723` |
| Ink (primary text) | `#1F2A44` blue-black fountain-pen ink | `#E9E2D3` |
| Ink secondary | `#5B6378` | `#A9A294` |
| Accent (red pencil) | `#C8472F` | `#E0674F` |
| Accent 2 (highlighter) | `#F2D56B` | `#B89C3A` |
| Success (green pen) | `#2E7D5B` | `#5BB38A` |
| Duplicate (pencil smudge) | `#8E8A80` | `#6F6A60` |
| Danger | `#B3261E` | `#F2766B` |

Contrast check: ink on cream is 12.4:1; red pencil on cream is 5.2:1; both exceed WCAG AA for text. Dark pairs are tuned the same way and must be re-verified when swatches change.

**Typography**
- Display and letter: a handwriting face for the drawn letter and headers. Candidate: Caveat (Google Fonts, SIL Open Font License 1.1, free to bundle). Source: https://fonts.google.com/specimen/Caveat and the OFL text at https://www.fontsquirrel.com/license/caveat. Alternative: a licensed script such as a Fontspring or Adobe Fonts face if we want something less familiar; cost is a one-time app license.
- Body and UI: New York (Apple system serif, available via `Font.Design.serif` in SwiftUI, no licensing) for a bookish feel. Fallback: SF Pro. Source: Apple Fonts, https://developer.apple.com/fonts/
- Numerals (timer, scores): SF Pro with tabular figures so digits do not jitter.

**Materials and texture**
- Subtle paper grain at 3 to 4 percent opacity, baked as a tiled PNG or generated by a Metal `colorEffect` shader (see 09). The grain is static; it never scrolls with content, which keeps it from reading as dirt.
- Ink bleed on submit: text edge softens by 1 to 2 pt for 150 ms then snaps crisp. This is the one place where the material behaves like a material.
- No drop shadows. Elevation is expressed as a slightly darker sheet behind the active card, as if one page sits on another.

**Iconography:** hand-drawn single-stroke icons at 1.75 pt weight, slight imperfection, 24 pt grid. Where SF Symbols are used (settings, share), they are rendered in the ink color and the custom set matches their optical weight.

**Illustration:** sparse. A doodled animal in the margin for Word Chain Animals category; small pencil scribbles as empty states. Never a full-bleed illustration.

**Signature motion:** the letter draw. The round's letter is written on the page stroke by stroke (animated path trim, 600 ms), with a faint pen-scratch haptic. See 09, animation M01.

**Sound and haptic character:** pencil on paper, page turn, a soft "tock" for duplicates. Haptics are dry and short (transient events, sharpness high, intensity low).

**NPAT grid:** four ruled lines on the page, each labeled in handwriting in the margin (Name, Place, Animal, Thing). The player's typed text is set in the handwriting face. The results table is a hand-ruled grid with a red-pencil tick for 10, a half tick for 5, a dash for 0.

**Word Chain chain:** a vertical list down the page like a shopping list, each word's last letter underlined in red pencil and connected with a short pen stroke to the first letter of the next word. At scale, older words fade as if the page scrolled.

**Risks:** skeuomorphism fatigue; handwriting fonts fail legibility at small sizes and in non-Latin scripts (App 3 problem); grain shaders can cost GPU on older devices; the look can feel precious if overdone.

**Effort:** 3.5 to 4.5 engineer-weeks beyond the shared skeleton (shader, letter-path assets for 26 letters, custom icon set, two font licenses or bundles).

> **[JOBS]** This is the one I feel in my gut. It is also the one most likely to turn into a Hallmark card. The grain stays under five percent or it goes.
>
> **[DESIGN]** The grain is a test case for principle 5. It stays only because the ink bleed makes the paper behave like paper. Remove the bleed and the grain is decoration, and it goes.

---

## 4. Direction B: Swiss Editorial

**One-line vibe:** A magazine spread about words. Big type, hard grid, one color.

**Mood references**
- NYT Games (Wordle, Spelling Bee, Connections) for a typographic, grid-first word-game family that reads as serious and adult. Source: https://www.nytimes.com/games
- Threes! (Sirvo) for the discipline of one tile, one number, one face, and for proving that a sliding-numbers game can feel designed rather than decorated. Source: https://en.wikipedia.org/wiki/Threes
- Josef Müller-Brockmann grid systems and Massimo Vignelli's NYC subway signage (print references), for strict modular grids and Helvetica-era confidence.

**Color palette**

| Role | Light | Dark |
|------|-------|------|
| Canvas | `#FFFFFF` | `#0B0B0C` |
| Surface 2 | `#F2F2F2` | `#161618` |
| Text primary | `#0B0B0C` | `#F5F5F5` |
| Text secondary | `#5F5F63` | `#A4A4A8` |
| Accent (one only) | `#FF3B1F` international orange | `#FF5A3C` |
| Success | `#1E8E5A` | `#3DBF84` |
| Duplicate | `#9A9A9E` | `#6E6E72` |
| Danger | `#D8261B` | `#FF6B5E` |

The accent is used for exactly one thing per screen: the active letter, or the primary button, never both.

**Typography**
- Display: Space Grotesk (OFL 1.1, free to bundle, https://fonts.google.com/specimen/Space+Grotesk) or Fraunces for a warmer editorial serif alternative (OFL 1.1, https://fonts.google.com/specimen/Fraunces). Both verified OFL via Font Squirrel license pages.
- UI and body: SF Pro (system), which keeps Dynamic Type behavior free.
- Letter: display face at 160 to 220 pt, optically kerned, set flush left to the margin with the category labels hanging in a narrow column.

**Materials and texture:** none. Flat surfaces, 1 pt hairline rules, generous whitespace. Elevation is expressed by a hairline and a change of surface tone, never by shadow or blur.

**Iconography:** SF Symbols, regular weight, monochrome. Custom glyphs only where no symbol exists (the chain link, the letter die).

**Illustration:** none. Typography is the illustration. Empty states are a single large glyph in the surface-2 tone.

**Signature motion:** the type slam. The letter arrives at full size with a 220 ms spring (bounce 0.15) and the category labels follow in a 40 ms stagger. The reveal of scores is a column of numbers counting with `contentTransition(.numericText())`. See 09, M02 and M14.

**Sound and haptic character:** quiet. A single clean click on submit, a lower click on duplicate, no music by default. Haptics are medium impact, used sparingly.

**NPAT grid:** four rows of a modular grid, label column at 25 percent width, answer column at 75 percent. Results view is a true table with hairline rules; duplicates are struck through in the accent color.

**Word Chain chain:** a horizontal ribbon of words set in a single typographic line that scrolls left as the chain grows, with the shared letter between words set in the accent color so "PARI**S**PAIN" reads as one typographic object. On narrow widths the ribbon wraps into a justified paragraph.

**Risks:** can feel cold for a party game; bold display type at Accessibility sizes overflows quickly; one-accent discipline is hard to hold once marketing wants badges and sales ribbons.

**Effort:** 2 to 2.5 engineer-weeks beyond the skeleton (one bundled font, typographic layout tuning, few assets).

> **[GAME]** This is the one that undersells NPAT's party chaos. Six people yelling "I wrote Paris too" is not a Swiss grid. It is excellent for Word Chain solo.
>
> **[DESIGN]** Fair. But it is the best direction for the results table, because the results table is a table. We should steal its results view regardless of which direction wins.

---

## 5. Direction C: Playful Pop

**One-line vibe:** A toy box with a brain. Round, saturated, bouncy, never childish.

**Mood references**
- Two Dots (Playdots), for saturated accents on deep navy, cozy illustration and clear focal contrast. Source: Pratt IxD write-up, https://ixd.prattsi.org/2015/02/two-dots-iphone-app-good-design/
- Heads Up! (Warner Bros, originally built by the Clear team), for party-game energy and gesture-driven pace. Source: https://apps.apple.com/us/app/id623592465
- Jackbox Party Pack, for the idea that a party game's visual identity can be irreverent and still cohesive. Source: Jackbox Games, https://www.jackboxgames.com/
- CapWords, Apple Design Award 2025 winner in Delight and Fun, for sticker-like playful UI. Source: https://developer.apple.com/design/awards/2025/

**Color palette**

| Role | Light | Dark |
|------|-------|------|
| Canvas | `#FFF8EE` | `#141A2B` deep navy |
| Surface | `#FFFFFF` | `#1E2640` |
| Text primary | `#1B1F3A` | `#F7F7FB` |
| Accent A (coral) | `#FF6B5B` | `#FF7A6B` |
| Accent B (sunflower) | `#FFC53D` | `#FFD166` |
| Accent C (mint) | `#3DD6A3` | `#56E6B5` |
| Accent D (violet) | `#7C6BFF` | `#9A8CFF` |
| Duplicate | `#B8B6C8` | `#6B6F8C` |
| Danger | `#E63946` | `#FF5C6A` |

Each NPAT category owns an accent (Name coral, Place sunflower, Animal mint, Thing violet). Custom categories cycle through a secondary ramp.

**Typography**
- Display and UI: SF Pro Rounded (system, `Font.Design.rounded`, no license). Source: https://developer.apple.com/fonts/
- Optional licensed alternative: Nunito (OFL 1.1, https://fonts.google.com/specimen/Nunito) if we want a rounder, friendlier display weight than SF Rounded Black.
- Letter: SF Pro Rounded Black at 180 pt in the category's accent, on a tilted sticker card.

**Materials and texture:** soft, matte, 3D-ish pills with a 2 pt inner highlight and a 6 pt offset flat shadow in a darker tint of the same hue (no blur). Cards are stickers with a 1.5 degree random tilt. No grain, no glass.

**Iconography:** filled, rounded, two-tone icons on a 24 pt grid with 2.5 pt strokes. SF Symbols used with `.fill` variants and the palette rendering mode.

**Illustration:** yes, generous. A small cast of letter characters (the letter has eyes when idle; this is the direction's mascot system), confetti shapes, category stickers. Illustration is flat vector, 2 to 3 tones per asset.

**Signature motion:** the sticker drop. The letter card falls in from above with a spring (duration 0.55, bounce 0.35), lands with a squash, and the category pills pop in with staggered bounces. Duplicate answers collide and bounce apart. See 09, M03 and M12.

**Sound and haptic character:** bright and musical. Marimba plinks for correct, a comedic "boing" for duplicate, a rising arpeggio for the score tally. Haptics are soft impacts with longer continuous events on the tally.

**NPAT grid:** four colored pill fields stacked, each with its category sticker on the left. Results view is a stack of sticker cards per player that fan out; duplicates get a "Twins!" sticker.

**Word Chain chain:** a chain of beads along a gently curving path (a spiral option is explored in 08) where each bead is a word in its category color and the shared letter is a smaller bead between them. The chain physically sways when a new bead snaps on.

**Risks:** crosses into kid territory and blurs the line with App 2 (Inkwell Kids); heavy illustration workload and asset management; bouncy motion must have real Reduce Motion alternatives; the mascot can become cringe.

**Effort:** 4.5 to 6 engineer-weeks beyond skeleton (illustration production, sticker component system, particle layer, sound design).

> **[KIDS]** Flagging the obvious: this is very close to what I would propose for Inkwell Kids. If App 1 ships Pop as default, App 2 has nowhere to go. I would rather App 1 own a grown-up look and App 2 own the toy box.
>
> **[JOBS]** Agree. Pop is a theme, not the default. And the mascot with eyes is cut from App 1. No eyes.

---

## 6. Direction D: Night Lounge

**One-line vibe:** Bar trivia at midnight. Dark, neon, a little dangerous, a lot of fun.

**Mood references**
- Balatro (LocalThunk), Apple Design Award 2025 winner, for juicy feedback on a dark table and a CRT shader layered over flat vector cards. Source: design breakdown at https://blakecrosley.com/guides/design/balatro and the awards page at https://developer.apple.com/design/awards/2025/
- Jackbox Party Pack's late-night TV framing, for dark backgrounds with saturated highlight colors and announcer energy. Source: https://www.jackboxgames.com/
- Neon signage and cocktail menus (print and signage references): saturated pink and cyan on near-black, chrome highlights, scripted display type.

**Color palette**

| Role | Dark (primary) | Light (secondary, for daylight) |
|------|----------------|-------------------------------|
| Canvas | `#0D0B14` | `#F4F1F8` |
| Surface | `#171427` | `#FFFFFF` |
| Text primary | `#F4F0FF` | `#17132A` |
| Text secondary | `#9E97B8` | `#5E5876` |
| Neon pink | `#FF3D9A` | `#D61E78` |
| Neon cyan | `#2EE6FF` | `#0E8FA3` |
| Neon amber | `#FFB84D` | `#B86E00` |
| Success | `#55F2A5` | `#1F8F5B` |
| Duplicate | `#6A6487` | `#8E88A8` |
| Danger | `#FF4D5E` | `#C8182B` |

This is the only direction where dark is primary. Light mode exists for daylight use and must still pass contrast, but the theme picker labels it "best in the dark".

**Typography**
- Display: a condensed or scripted display face licensed for app embedding; candidates include Monument Extended (Pangram Pangram, commercial license) or a free alternative such as Bebas Neue (OFL, https://fonts.google.com/specimen/Bebas+Neue). Final choice requires a licensing check; the brief says do not assume licenses.
- UI: SF Pro (system), with SF Pro Display weights at the top of the ramp.
- Letter: display face at 200 pt with a soft outer glow (8 pt blur, 40 percent) in the round's neon color.

**Materials and texture:** dark glass. Cards use `.ultraThinMaterial` over a slowly drifting gradient so the surface breathes. A subtle scanline shader is offered as an optional "CRT" toggle inside the theme (off by default, off under Reduce Motion). Neon glow is a real material here because it signals the active element.

**Iconography:** thin-line icons at 1.5 pt with glow on the active state. SF Symbols in `.hierarchical` rendering with the neon tint.

**Illustration:** minimal; abstract neon shapes and signage-style word marks for categories. No characters.

**Signature motion:** the neon flicker on. The letter flickers to full brightness in three quick steps over 420 ms (a KeyframeAnimator track for opacity and glow radius), with a matching three-tap haptic. See 09, M04.

**Sound and haptic character:** low, warm, electric. A synth pad under the round, a bass thump on submit, a buzzer for time-up, a chime for a clean chain. Haptics are deeper and longer (continuous events with decaying intensity).

**NPAT grid:** four glass bar-tab rows on the dark table, each lighting its own neon color when active. Results view is a scoreboard like a bar's trivia screen, with player names in marquee style and duplicates revealed by both rows pulsing together.

**Word Chain chain:** a horizontal neon tube that lights up segment by segment as words are added; each word is a lit sign hanging on the tube, and the shared letter is the glowing junction. When someone breaks the chain, the tube flickers out from the break point.

**Risks:** glow and blur are expensive on older GPUs and can look muddy in sunlight; neon on black fails contrast easily for secondary text; the vibe excludes kids and some adult players who want a daytime look; Reduce Motion must disable flicker completely (flicker is a photosensitivity concern).

**Effort:** 4 to 5 engineer-weeks beyond skeleton at full scope (material and glow tuning, optional shader, licensed display face, sound design). The 1.0 reduced scope (tokens, display face, static glow, S3 sound; no shader, no animated materials, no ambient drift) is about 1.25 engineer-weeks of engineering plus design time; see Section 9.

> **[IOS]** Materials over animated gradients plus glow on every active element is the single most expensive combination in this document. I want a frame budget per screen before we commit; see 09 section 7. Also, a flicker animation has to be killed under Reduce Motion, not softened.
>
> **[QA]** And it has to be tested outdoors. Dark themes with low-contrast secondary text are our most common accessibility bug class in other apps I have shipped.

---

## 7. Direction E: Quiet Minimal

**One-line vibe:** Looks like Apple made it. Pure HIG, system materials, zero custom type.

**Mood references**
- Things 3 (Cultured Code), two-time Apple Design Award winner, for what a system-native app looks like when every detail is polished. Source: https://culturedcode.com/things/
- Apple's own Notes and Reminders apps, for system materials, Dynamic Type purity and SF Symbols discipline.
- Alto's Odyssey (Snowman and Team Alto), for calm, impressionistic restraint in a game that still feels alive. Source: https://www.itsnicethat.com/news/altos-odyssey-snowman-game-digital-220218

**Color palette**

| Role | Light | Dark |
|------|-------|------|
| Canvas | system `systemBackground` (`#FFFFFF`) | `#000000` |
| Grouped surface | `secondarySystemGroupedBackground` | same |
| Text | `label`, `secondaryLabel` | same |
| Accent | `systemIndigo` (`#5856D6`) by default, user may choose any system tint | elevated variant |
| Success | `systemGreen` | same |
| Duplicate | `systemGray` | same |
| Danger | `systemRed` | same |

All colors are semantic system colors so they adapt to Dark Mode, Increase Contrast and Smart Invert for free. Hex values above are the current iOS defaults and are not hard-coded in the app.

**Typography:** SF Pro and SF Pro Rounded only, via text styles (Large Title through Caption 2). The letter is `largeTitle` scaled with `@ScaledMetric` to roughly 140 pt at default size. No bundled fonts.

**Materials and texture:** system materials (`.regularMaterial`, `.thinMaterial`) for bars and overlays, system shadows, system corner radii via `.rect(cornerRadius:)` with continuous curvature. No custom texture.

**Iconography:** SF Symbols exclusively, matching text weight via `.imageScale` and font-relative sizing. Source: https://developer.apple.com/design/human-interface-guidelines/sf-symbols

**Illustration:** none. Empty states use a large SF Symbol and one line of text, as in Apple's own apps.

**Signature motion:** the system spring. All transitions use SwiftUI's default springs and the iOS 18 zoom transition where available (see WWDC24 session 10145). The one custom moment is the letter's `numericText`-style roll when drawn. See 09, M05.

**Sound and haptic character:** system sounds and `sensoryFeedback(.success)`, `.impact`, `.selection` only. No music.

**NPAT grid:** a grouped inset list with four text fields, exactly as Settings would render it. Results view is a grouped list per player with a trailing score and a secondary label "same as Priya" for duplicates.

**Word Chain chain:** a plain vertical `List` of words, newest at the bottom, with the shared letter shown in the accent tint. Chain length shown as a navigation subtitle.

**Risks:** indistinct in the App Store; weak "vibe", which is the founder's top priority; little to theme later; may read as a utility, not a game.

**Effort:** 1 to 1.5 engineer-weeks beyond skeleton. This is also the fallback if any other direction slips.

> **[JOBS]** This is not a direction. It is the floor. Every other direction must be at least this good at accessibility and system behavior, and then add a soul. We build this first as the skeleton, we never ship it as the face.
>
> **[ARCH]** Which is exactly why it is valuable. If the DesignSystem package can render Quiet Minimal from semantic tokens, then every other direction is a token file plus assets. It also gives QA a reference rendering to diff against.

---

## 8. Comparison matrix

Scores are 1 (weak) to 5 (strong). Effort is engineer-weeks beyond the shared skeleton for a 1 to 2 engineer team.

| Criterion | A Paper & Ink | B Swiss Editorial | C Playful Pop | D Night Lounge | E Quiet Minimal |
|-----------|:---:|:---:|:---:|:---:|:---:|
| Distinctiveness in App Store | 5 | 4 | 4 | 5 | 1 |
| Fits NPAT (pressure, party) | 4 | 3 | 5 | 5 | 2 |
| Fits Word Chain (relay, calm) | 5 | 5 | 3 | 3 | 4 |
| Adult but not cold | 5 | 3 | 3 | 4 | 3 |
| Separation from Inkwell Kids | 4 | 5 | 1 | 5 | 4 |
| Dynamic Type resilience | 3 | 2 | 3 | 3 | 5 |
| Dark mode quality | 4 | 5 | 4 | 5 | 5 |
| GPU and battery cost | 3 | 5 | 3 | 2 | 5 |
| Reduce Motion story | 4 | 5 | 2 | 2 | 5 |
| Localization and script risk (App 3) | 2 | 4 | 4 | 3 | 5 |
| Asset production load | 3 | 5 | 1 | 3 | 5 |
| Themeability later | 4 | 3 | 4 | 4 | 2 |
| Effort (eng-weeks) | 3.5 to 4.5 | 2 to 2.5 | 4.5 to 6 | 4 to 5 | 1 to 1.5 |
| **Weighted total (vibe x2, a11y x1.5)** | **49.5** | 44 | 41.5 | 45 | 40 |

Weights: distinctiveness, NPAT fit, Word Chain fit and adult-not-cold count double (vibe is the founder's top priority); Dynamic Type and Reduce Motion count 1.5; the rest count once.

---

## 9. Recommendation

**Default direction: A, Paper & Ink,** with the results table borrowed from B.

Reasons: it scores highest on the founder's stated priority (vibe), it is the only direction that gives both games a natural home (a notebook page works for a timed scribble and for a long list), it keeps clear distance from Inkwell Kids, and its one honest material (ink bleed on paper) gives us a signature that no competitor has.

**Ship as selectable themes in v1 (Pro unlock, see 08 purchase flow):** B Swiss Editorial and D Night Lounge. Both are tokens plus one bundled font and a small asset set. B is cheap and gives the serious solo player a home. D is the "party at night" theme and sells the Pro unlock.

**DECISION (reconciled 2026-10-04):** the effort figures in this document are design plus engineering including asset production; the delivery plan's figures are engineering only. Reconciled with 03 Section 8: Paper & Ink and Swiss Editorial ship in 1.0 at full scope; Night Lounge ships in 1.0 at reduced scope (tokens, display face, static glow, the S3 sound pack; no CRT shader, no animated materials, no ambient drift) inside a 2 EW Phase 4 theme budget; if the W14 capacity review cannot fund it, cut-list item 3 moves Night Lounge to 1.1 as the first Pro content drop. Master idea 17 says the same. Needs founder sign-off (register F6).

**Parallel pass (skunkworks, not in v1):** C Playful Pop. It is the most expensive, it collides with App 2, and the founder's "no eyes" rule removes its mascot. Keep a Figma file alive, revisit after Inkwell Kids defines its own look so the two do not converge.

**Skeleton, never shipped as a theme:** E Quiet Minimal. Built first as the semantic-token reference rendering and QA baseline.

> **[JOBS]** Paper & Ink as default, Night Lounge as the thing you pay for. Swiss for free so nobody says we charge for dark mode. Pop is parked. Minimal is the plumbing. Done.
>
> **[DESIGN]** One amendment: the theme picker in v1 ships with exactly three themes. Not five. A picker with two paid tiles and one free tile reads clearly. A picker with five tiles reads like a settings page.
>
> **[GAME]** I want it on record that Night Lounge should also unlock a "house rules" preset (blitz timers, stop rule on) so the theme changes the feel of play, not just the colors. Theme as mood, not just skin.
>
> **[ARCH]** That violates principle 7 (themes change clothes, not bones) unless the preset is a suggestion, not a forced rule change. Suggest it on first selection, do not apply it silently.
>
> **DECISION:** Default A. Free theme B. Paid theme D. C parked as skunkworks. E is the skeleton. Night Lounge offers (does not force) a blitz house-rules preset on first selection.
>
> Closed (reconciled 2026-10-04): D's optional CRT scanline shader does not ship in 1.0 (reduced-scope Night Lounge); revisited for 1.1 after the bake-off in 09.

---

## 10. Theming architecture

Themes are data, not code paths. The DesignSystem package exposes semantic tokens; a theme is a complete set of token values plus an asset bundle. UI code references only semantic tokens.

**Token layers**

1. **Primitive tokens:** raw values. `paper.cream.100 = #F6F1E7`, `space.4 = 16`, `radius.m = 12`, `duration.fast = 0.18`.
2. **Semantic tokens:** roles. `color.canvas`, `color.ink.primary`, `color.accent.letter`, `color.state.duplicate`, `font.letter`, `font.body`, `motion.hero`, `sound.submit`, `haptic.duplicate`. Each resolves to a primitive per theme and per appearance (light, dark, increased contrast).
3. **Component tokens:** `button.primary.background = color.accent`, `field.answer.border.focused = color.ink.primary`. Components never read primitives.

**Theme bundle contents**

| Part | Format | Notes |
|------|--------|-------|
| Color tokens | JSON (light, dark, high-contrast) | Loaded into an asset catalog at build time so the system handles appearance switching |
| Type tokens | JSON mapping roles to font family, weight, design, and a Dynamic Type text style | Custom fonts scale via `Font.custom(_:size:relativeTo:)` so they track Dynamic Type |
| Motion flavor | JSON with spring presets (duration, bounce) per role | 09 defines the roles |
| Materials | enum: none, paperGrain, glass, sticker | Component decides how to render; theme only names it |
| Icon set | SF Symbols configuration plus optional custom symbol set | Custom symbols authored as SF Symbol templates so weights match |
| Sounds and haptics | AHAP files plus audio clips, keyed by semantic event | See 09 |

**Rules**
- A theme cannot change layout constants (spacing, radius scale, tap target sizes). Those are shared primitives, not theme values. This enforces principle 7.
- Every theme must ship light, dark and increased-contrast variants and pass automated contrast tests in CI (QA owns the script).
- Themes switch live without relaunch; a theme change is a state change animated with a 350 ms cross-fade of the canvas, nothing else moves.
- The HIG advises against app-specific appearance toggles that fight the system setting; we follow the system light or dark setting and let themes define both. Source: https://developer.apple.com/design/human-interface-guidelines/dark-mode

> **[ARCH]** The token JSON is the contract between Figma and Xcode. Figma variables export to the same JSON shape; a build step generates the asset catalog and a Swift enum. No hand-copied hex values anywhere.
>
> **[IOS]** Agreed, with one caution: `Font.custom(_:size:relativeTo:)` scales correctly but the handwriting face in A needs its own minimum size clamp, because at Caption 2 it is unreadable. Component tokens can carry a `minPointSize`.
>
> **DECISION:** Three-layer token model, JSON source of truth, generated Swift. Layout primitives are not themeable.

---

## 11. Design-system foundations

### 11.1 Spacing scale (shared, not themeable)

| Token | Points | Use |
|-------|--------|-----|
| space.1 | 4 | icon-to-label gaps, hairline insets |
| space.2 | 8 | inside compact controls |
| space.3 | 12 | between related items |
| space.4 | 16 | standard content inset (matches system margins) |
| space.5 | 24 | between groups |
| space.6 | 32 | section spacing |
| space.7 | 48 | hero spacing around the letter |
| space.8 | 64 | top-of-screen breathing room |

Minimum tap target 44 by 44 pt, per HIG Layout guidance: https://developer.apple.com/design/human-interface-guidelines/layout

### 11.2 Radius scale

| Token | Points | Use |
|-------|--------|-----|
| radius.xs | 4 | tags, hairline chips |
| radius.s | 8 | text fields, list rows |
| radius.m | 12 | cards |
| radius.l | 20 | sheets, large buttons |
| radius.pill | 999 | pills and segmented controls |

All radii use continuous (squircle) curvature. Themes may not override; Pop's "sticker" look uses radius.l, not a custom value.

### 11.3 Elevation

| Level | Name | Expression (per theme) |
|-------|------|------------------------|
| 0 | canvas | the page |
| 1 | raised | A: darker sheet behind; B: hairline and surface-2; C: flat offset shadow; D: thin material; E: system grouped background |
| 2 | floating | A: sheet plus 2 pt offset; B: surface-2 plus 1 pt rule; C: offset shadow 6 pt; D: regular material plus glow; E: system shadow |
| 3 | modal | system sheet presentation in every theme (never custom) |

### 11.4 Type ramp mapped to Dynamic Type

Base sizes are the iOS defaults at the Large (default) content size; all scale with the system. Source: HIG Typography, https://developer.apple.com/design/human-interface-guidelines/typography, and the WWDC20 session "The details of UI typography", https://developer.apple.com/videos/play/wwdc2020/10175/

| Role token | System text style | Default pt | Theme may change | Notes |
|------------|------------------|-----------:|------------------|-------|
| font.letter | custom, relative to largeTitle | 160 (clamped 96 to 220) | family, weight | the hero |
| font.display | largeTitle | 34 | family, weight | screen titles |
| font.title | title1 | 28 | family | section heads |
| font.heading | title3 | 20 | family | card titles |
| font.body | body | 17 | family | answers, lists |
| font.bodyEmphasis | headline | 17 semibold | weight | primary labels |
| font.secondary | subheadline | 15 | none | helper text |
| font.caption | footnote | 13 | none | timestamps, legal |
| font.micro | caption2 | 11 | none | badges only, never alone |
| font.numeric | body, monospaced digits | 17 | none | timers, scores |

At Accessibility sizes (AX1 to AX5) the letter clamps at 220 pt and the four NPAT fields switch from a stacked layout to one-field-at-a-time (see 08 deep dive). Nothing truncates; everything reflows.

### 11.5 Color roles

| Role | Purpose | Contrast requirement |
|------|---------|---------------------|
| color.canvas | page background | n/a |
| color.surface, color.surface2 | raised and floating | n/a |
| color.ink.primary | main text | 7:1 on canvas |
| color.ink.secondary | helper text | 4.5:1 on canvas |
| color.accent | primary action and active letter | 4.5:1 on canvas; 3:1 as a large glyph |
| color.accent.onAccent | text on accent | 4.5:1 |
| color.state.success | valid, unique answer | 4.5:1 |
| color.state.duplicate | matched answer | 4.5:1 and never the only signal |
| color.state.danger | invalid, time up, eliminated | 4.5:1 |
| color.state.focus | focused field ring | 3:1 against adjacent |
| color.category.name/place/animal/thing/custom | category identity | decorative; text on them must pass |

Color is never the only carrier of state: duplicate rows also show an icon and a label (principle 6, and HIG Accessibility guidance on conveying information with more than color).

### 11.6 Iconography grid

24 pt artboard, 2 pt padding, 20 pt live area, 1.75 pt stroke default (theme may set 1.5 or 2.5), round caps and joins, optical centering. Custom icons are authored as SF Symbol templates with Small, Medium and Large scales and nine weights so they align with system text. Source: HIG SF Symbols, https://developer.apple.com/design/human-interface-guidelines/sf-symbols, and HIG Icons, https://developer.apple.com/design/human-interface-guidelines/icons

Custom glyphs required in v1: letter die, chain link, chain broken, ink drop, timer sand, duplicate twins, stop hand (stop rule), pass phone (pass-and-play), theme swatch, Pro badge.

---

## 12. Component inventory and state matrix

### 12.1 Inventory (31 components)

Package column key, using the architecture document's names: "DesignSystem" is `IWDesignSystem`; "GameUI" and "Store" are feature modules inside `IWFeatures` (`NPATFeature`, `WordChainFeature`, `SettingsFeature`).

| # | Component | Package | Notes |
|---|-----------|---------|-------|
| 1 | LetterHero | DesignSystem | the drawn letter, per-theme motion |
| 2 | RoundTimer | DesignSystem | ring or bar, per theme |
| 3 | AnswerField | DesignSystem | labeled text field with category |
| 4 | AnswerFieldStack | DesignSystem | four fields or paged single field |
| 5 | CategoryChip | DesignSystem | selectable category |
| 6 | PrimaryButton | DesignSystem | one per screen |
| 7 | SecondaryButton | DesignSystem | |
| 8 | TertiaryButton (text) | DesignSystem | |
| 9 | IconButton | DesignSystem | 44 pt target |
| 10 | SegmentedControl | DesignSystem | mode and timer presets |
| 11 | Stepper | DesignSystem | player count, round count |
| 12 | Toggle | DesignSystem | system toggle, tinted |
| 13 | PlayerAvatar | DesignSystem | initials or glyph, color |
| 14 | PlayerRow | DesignSystem | name, avatar, score |
| 15 | ScoreTally | DesignSystem | animated numeric |
| 16 | ResultsTable | DesignSystem | borrowed from B |
| 17 | DuplicateBadge | DesignSystem | icon plus label |
| 18 | ChainView | GameUI | vertical, ribbon, or spiral renderer |
| 19 | ChainLink | GameUI | one word in the chain |
| 20 | LifeIndicator | GameUI | hearts or pips |
| 21 | TurnBanner | GameUI | "Pass to Priya" |
| 22 | PassPhoneInterstitial | GameUI | full-screen handoff |
| 23 | ChallengeSheet | GameUI | dispute an answer |
| 24 | Card | DesignSystem | elevation 1 container |
| 25 | Sheet | DesignSystem | system sheet with theme chrome |
| 26 | Toast | DesignSystem | transient, non-blocking |
| 27 | EmptyState | DesignSystem | glyph plus one line plus one action |
| 28 | ThemeSwatch | DesignSystem | preview tile in picker |
| 29 | ProBadge and Paywall | Store | StoreKit 2 views |
| 30 | SettingsRow | DesignSystem | grouped list row |
| 31 | OnboardingHint | DesignSystem | inline coach mark, one at a time |

### 12.2 State matrix for key components

| Component | Default | Focused | Pressed | Disabled | Loading | Error | Success | Reduce Motion |
|-----------|---------|---------|---------|----------|---------|-------|---------|---------------|
| AnswerField | ruled line, placeholder category | ring in color.state.focus, caret, keyboard up | n/a | ink.secondary text, no caret | n/a | shake 2 cycles, danger underline, helper text | ink bleed then crisp, check glyph | no shake; underline color change plus helper text only |
| PrimaryButton | accent fill | focus ring (keyboard, Switch Control) | scale 0.97, 90 ms | 40 percent opacity, no haptic | spinner replaces label, width held | n/a | check replaces label 600 ms | no scale; opacity dip to 0.85 |
| RoundTimer | full ring | n/a | n/a | hidden when timer off | n/a | last 5 s: pulse and color to danger | n/a | no pulse; color change and numeric only |
| ChainLink | word in ink | n/a | long-press: challenge | n/a | validating: dotted underline | invalid: strikethrough and danger | valid: link snap | no snap; fade in |
| DuplicateBadge | hidden | n/a | n/a | n/a | n/a | n/a | appears with collision | appears with fade |
| ThemeSwatch | tile with miniature letter | ring | scale 0.96 | locked: Pro badge overlay | n/a | purchase failed: toast | selected: check | no scale |
| PassPhoneInterstitial | "Pass to X", hold-to-reveal | n/a | hold progress | n/a | n/a | n/a | reveals field | hold progress as fill, no motion blur |

Every component has a VoiceOver label, value and hint defined in 08, and every animated state has a Reduce Motion alternative defined in 09.

---

## 13. App icon

The app icon is a single drawn letter on the theme's canvas. Default (Paper & Ink) is a cream square with an ink "I" written with a visible stroke, red-pencil underline. Alternate icons ship per theme (Swiss: black "I" on white with the orange dot; Night Lounge: neon "I" on near-black) and are selectable from the theme picker using `setAlternateIconName`. Source: HIG App icons, https://developer.apple.com/design/human-interface-guidelines/app-icons

> **[JOBS]** The icon is a letter. Not a quill, not an inkwell, not a notebook. A letter. If I see a feather I will delete it myself.
>
> **OPEN:** Whether the icon letter is always "I" (for Inkwell) or changes daily like a drawn letter (not possible without a widget; icons are static). Parked; static "I".

---

## 14. Naming options (brief)

The working title is Inkwell. Naming is owned by the product brief (01, Section 8), which decided: keep Inkwell pending trademark clearance in Phase 0, with fallbacks ranked Nib, Letterhead, Foolscap. This document only notes that Paper & Ink is the direction most reinforced by the name Inkwell (Nib works equally well), and that Night Lounge would suit a sub-brand ("Inkwell After Dark") for the paid theme.

---

## 15. Risk register (design)

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| Handwriting face unreadable at small sizes | High | Medium | minPointSize clamp; body in New York, handwriting only for letter and headers | DESIGN |
| Paper grain shader costs frames on A12 and older | Medium | Medium | static tiled PNG fallback; bake-off in 09 | IOS |
| Night Lounge contrast failures outdoors | High | High | CI contrast tests; light variant; QA outdoor pass | QA |
| Flicker animation and photosensitivity | Low | High | hard-disable under Reduce Motion; cap flicker to 3 steps, no strobing under 3 Hz | DESIGN, IOS |
| Five directions drift into five layouts | Medium | High | layout primitives not themeable; weekly token diff | ARCH |
| Pop theme collides with Inkwell Kids | High | Medium | Pop parked until Kids direction is set | KIDS |
| Licensed display font blocks release | Low | High | OFL alternatives pre-selected for every slot | DESIGN |
| Review gate fatigue (seven tests per screen) | Medium | Low | checklist baked into Figma template and PR template | QA |

---

## 16. Decisions and open questions

**DECISIONS**
1. Seven design principles adopted as review gates.
2. Default direction A (Paper & Ink); B free theme; D paid theme; C parked skunkworks; E skeleton.
3. Three-layer token model, JSON source of truth, generated Swift; layout primitives are not themeable.
4. Night Lounge suggests, never forces, a blitz house-rules preset.
5. App icon is a single letter; alternate icons per theme.
6. Results table design borrowed from Swiss Editorial across all themes.
7. No mascot with eyes in App 1.

8. Night Lounge ships in 1.0 at reduced scope (no shader, no animated materials) within a 2 EW Phase 4 theme budget, or moves to 1.1 via cut-list item 3 (reconciled with 03; founder sign-off).

**OPEN**
1. Closed: the CRT scanline shader is not in 1.0; revisit for 1.1 (IOS bake-off).
2. Final licensed display face for Night Lounge versus OFL fallback (DESIGN, by end of Phase 1).
3. Whether custom theme sounds ship with the theme or are a separate Pro feature (GAME, DESIGN).
4. Grain: shader versus static tile, pending performance numbers (IOS).

---

## 17. Sources

- Apple HIG root: https://developer.apple.com/design/human-interface-guidelines/
- HIG Typography: https://developer.apple.com/design/human-interface-guidelines/typography
- HIG Color: https://developer.apple.com/design/human-interface-guidelines/color
- HIG Materials: https://developer.apple.com/design/human-interface-guidelines/materials
- HIG Layout: https://developer.apple.com/design/human-interface-guidelines/layout
- HIG Dark Mode: https://developer.apple.com/design/human-interface-guidelines/dark-mode
- HIG Motion: https://developer.apple.com/design/human-interface-guidelines/motion
- HIG Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- HIG SF Symbols: https://developer.apple.com/design/human-interface-guidelines/sf-symbols
- HIG Icons: https://developer.apple.com/design/human-interface-guidelines/icons
- HIG App icons: https://developer.apple.com/design/human-interface-guidelines/app-icons
- Apple Fonts (SF Pro, SF Pro Rounded, New York): https://developer.apple.com/fonts/
- WWDC20 "The details of UI typography": https://developer.apple.com/videos/play/wwdc2020/10175/
- WWDC24 "Enhance your UI animations and transitions": https://developer.apple.com/videos/play/wwdc2024/10145/
- Apple Design Awards 2025: https://developer.apple.com/design/awards/2025/
- Letterpress design lessons: https://www.gamedeveloper.com/business/7-design-lessons-from-i-letterpress-i-
- Monument Valley (ustwo): https://ustwo.com/work/monument-valley/
- Alto's Odyssey: https://www.itsnicethat.com/news/altos-odyssey-snowman-game-digital-220218
- Threes!: https://en.wikipedia.org/wiki/Threes
- Two Dots design analysis: https://ixd.prattsi.org/2015/02/two-dots-iphone-app-good-design/
- Heads Up!: https://apps.apple.com/us/app/id623592465
- Jackbox Games: https://www.jackboxgames.com/
- Balatro design breakdown: https://blakecrosley.com/guides/design/balatro
- Baba Is You review: https://www.pcgamer.com/baba-is-you-review/
- Things 3: https://culturedcode.com/things/
- NYT Games: https://www.nytimes.com/games
- Caveat (OFL): https://fonts.google.com/specimen/Caveat and https://www.fontsquirrel.com/license/caveat
- Fraunces (OFL): https://fonts.google.com/specimen/Fraunces and https://www.fontsquirrel.com/license/fraunces
- Space Grotesk (OFL): https://fonts.google.com/specimen/Space+Grotesk
- Nunito (OFL): https://fonts.google.com/specimen/Nunito
- Bebas Neue (OFL): https://fonts.google.com/specimen/Bebas+Neue
