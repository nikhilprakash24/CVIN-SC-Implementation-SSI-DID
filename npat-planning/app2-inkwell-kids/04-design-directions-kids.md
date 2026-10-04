# App 2 "Inkwell Kids": Design Directions

**Read this if...** you are designing or implementing the look, motion, sound and voice of the kids app. This document sets kid-specific visual principles, lays out four fully specified visual directions as parallel passes, compares them and recommends one, then fixes the kid motion rules, the touch target and layout numbers, the parent area's distinct adult language, parental gate pattern options, the component inventory versus App 1, and 30 example microcopy strings including gentle failure messages.

**Document status:** Draft v0.1, 2026-10-04, owner **[DESIGN — Design Director, "Sofia Lindqvist"]** with **[KIDS — Child UX & Learning Specialist, "Dr. Amara Nwosu"]**.

---

## Table of contents

1. Kid visual principles
2. Four visual directions (parallel passes)
3. Comparison matrix and recommendation
4. Kid-specific motion rules
5. Touch targets and layout rules, with numbers
6. Typography for early readers
7. How letters, the grid and the chain look
8. The parent area: a distinct adult language
9. Parental gate pattern options
10. Component inventory differences from App 1
11. Microcopy voice and 30 example strings
12. Decisions and open questions
13. Sources

---

## 1. Kid visual principles

These extend doc 01's product principles into the visual layer. Apple's HIG root (https://developer.apple.com/design/human-interface-guidelines/), its Accessibility page (https://developer.apple.com/design/human-interface-guidelines/accessibility), Motion page (https://developer.apple.com/design/human-interface-guidelines/motion), Typography page (https://developer.apple.com/design/human-interface-guidelines/typography) and the newer "Designing for games" page (https://developer.apple.com/design/human-interface-guidelines/designing-for-games) are the baseline; Apple's Kids apps page (https://developer.apple.com/app-store/kids-apps/) sets the gating and safety constraints. We go further on size and slower on motion.

1. **Interactive things look touchable; decorative things do not.** NN/g's children's research warns that when everything is bright, children cannot tell what is interactive (https://www.nngroup.com/articles/childrens-websites-usability-issues/). Buttons get a raised, shadowed, "pressable" treatment; backgrounds are quiet.
2. **One hero per screen.** The letter is the hero on the play screen; the sticker is the hero on the reward screen; the avatar is the hero on the handoff screen.
3. **Faces help, but not everywhere.** A single companion character (Pip) carries emotion; category icons are objects, not faces, so the screen has one face to read.
4. **Edges are quiet.** Sesame Workshop's tablet research found preschoolers rest wrists on the bottom edge and trigger hotspots there (https://joanganzcooneycenter.org/?p=19607). Nothing interactive sits within 24 points of the bottom edge on iPad in Sprouts; the home control sits top-left.
5. **Color carries mood, shape carries meaning.** Every state has a shape or icon; color alone never distinguishes valid from pending.
6. **Letters are the art.** The letterforms themselves are the most important illustration in the app. Whatever direction we pick, the letter tile is the first component designed.
7. **Older kids are not small kids.** Navigators get a cooler, quieter theme skin from the same system, with the mascot optional.
8. **Nothing flashes.** Ever. WCAG 2.3.1 (no more than three flashes per second) is the floor (https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold); our rule is no flashing at all.

---

## 2. Four visual directions (parallel passes)

Each direction is specified enough to build a vertical slice: the play screen, the keyboard, the celebration and the sticker book. Mood references are real products or art traditions cited by their official sites; we are not copying any of them.

### 2.1 Direction A: "Crayon & Construction Paper"

- **Vibe:** a kindergarten table. Thick crayon strokes, torn-paper edges, visible paper grain, the warmth of a handmade thing. Honest, tactile, unmistakably for small hands.
- **Mood references:** the tactile, cut-paper warmth of Sago Mini's worlds (https://sagomini.com/); classic construction-paper collage in children's picture books; the hand-drawn letter energy of Endless Alphabet by Originator (https://www.originatorkids.com/).
- **Palette (hex):** Paper Cream `#FBF3E4` (background), Crayon Red `#E4573D`, Sunflower `#F6C445`, Grass `#6DBE6A`, Sky `#5BA8E5`, Grape `#8E6BC2`, Charcoal Crayon `#3B3A3C` (text), Kraft `#C9A878` (secondary surfaces). All text on Paper Cream in Charcoal meets 4.5:1.
- **Typography:** Headings in a rounded hand-lettered display face (custom or a rounded humanist like "Fredoka"); body and letter tiles in a literacy-oriented sans with single-story a and g (Andika, SIL Open Font License, designed for beginning readers with letterforms that are not mirror images of one another; https://en.wikipedia.org/wiki/Andika_(typeface)). Rationale: early readers are taught single-story a and g in school handwriting; double-story forms in most UI fonts are a small but real decoding cost.
- **Illustration and character:** flat crayon-textured shapes with a wobbly outline; Pip is a purple inkblot with crayon eyes. Letter creatures look like a child's drawing done well.
- **Motion signature:** "paper flip." Cards flip like construction paper, with a slight bounce and a soft paper rustle. Celebration: crayon scribble confetti that draws itself in 1.2 seconds. Transitions 350 to 450 ms.
- **Sound character:** acoustic and small: pencil scratches, paper rustles, a glockenspiel for success, a soft kazoo for Pip's mistakes.
- **Letters and grid:** letter tiles are torn-paper squares with a crayon letter; the NPAT grid is a sheet of lined paper with four crayon-colored rows; the Word Chain is a line of paper tiles taped together, each tape strip a different color.
- **Risks:** texture at scale can muddy legibility; crayon outlines fight small sizes; Navigators may find it babyish.
- **Effort:** medium-high. Texture pipeline (vector plus noise) needs care for Dynamic Type and for bundle size. About 4 design weeks for the system plus 26 creatures.

### 2.2 Direction B: "Friendly Monsters"

- **Vibe:** character-led. Each letter is a monster with a personality; the UI is a stage they perform on. Humor is the engine, and surprise is the reward.
- **Mood references:** the character-driven, non-verbal play of Toca Boca (https://tocaboca.com/); the letter-monsters tradition of Endless Alphabet (https://www.originatorkids.com/); the gentle expressiveness of Khan Academy Kids' animal cast (https://learn.khanacademy.org/khan-academy-kids/).
- **Palette (hex):** Night Mint `#DFF5EC` (background), Monster Teal `#1FA393`, Tangerine `#FF8A3D`, Bubblegum `#F06AA6`, Lemon `#FFD93D`, Deep Plum `#3A2A4D` (text), Cloud `#FFFFFF` (cards). Deep Plum on Night Mint exceeds 7:1.
- **Typography:** a bold, round geometric sans with large x-height for display (for example "Baloo 2" or a custom rounded face); UI and tiles in Atkinson Hyperlegible (Braille Institute, SIL Open Font License; letterforms deliberately differentiated such as l vs 1 and p vs q; https://en.wikipedia.org/wiki/Atkinson_Hyperlegible). Rationale: differentiated letterforms directly serve b/d/p/q confusion in early readers.
- **Illustration and character:** 26 monsters, each the shape of its letter, with big eyes and two or three poses (idle, cheer, shrug). Pip is the inkblot who introduces them. Smooth vector, soft shading.
- **Motion signature:** "squash and stretch." Monsters breathe at idle (slow, 3-second loop, disabled under Reduce Motion), hop when their letter is drawn, cheer with a 1.5-second jump. Transitions 300 to 400 ms with overshoot.
- **Sound character:** vocal and silly: monster giggles, a "boing," a chorus of "yay" (synthesized, not real children's voices, to avoid any recording of minors).
- **Letters and grid:** the drawn letter is the monster itself, large, center stage; category cards are stage props; the Word Chain is a conga line of monsters holding hands, each new word adding a dancer.
- **Risks:** 26 characters with poses is a lot of art; character fatigue; the "everything has a face" problem if not disciplined (principle 3); Navigators may reject it most of all directions.
- **Effort:** high. 6 to 8 design weeks for the cast plus the system; Lottie or Rive for character animation adds a dependency (must be a privacy-neutral runtime with no network).

### 2.3 Direction C: "Bright Blocks"

- **Vibe:** geometric and bold. Primary colors, thick outlines, chunky block letters, the confidence of a well-made wooden toy. Modern, gender-neutral, scales from 5 to 13 best of the four.
- **Mood references:** classic wooden alphabet blocks and the Bauhaus-leaning children's design tradition; the clean geometric UI of Khan Academy Kids' navigation (https://learn.khanacademy.org/khan-academy-kids/); PBS Kids' bold, flat interface language (https://pbskids.org/).
- **Palette (hex):** Chalk `#F7F7F2` (background), Block Blue `#2F6FED`, Block Red `#EF4444`, Block Yellow `#FACC15`, Block Green `#22A06B`, Ink `#1B1B1F` (text and outlines), Slate `#6B7280` (secondary). Navigators skin: Graphite `#2B2D33` background with the same accents at slightly reduced saturation.
- **Typography:** one family throughout, a bold rounded geometric sans with a literacy-friendly alternate set (single-story a, tailed l) enabled for Sprouts and disabled for Navigators. Candidates: a custom face, or Atkinson Hyperlegible for UI with a heavy rounded display for tiles. Rationale: one family keeps the system small and the Navigators skin credible.
- **Illustration and character:** minimal. Letter creatures are geometric animals assembled from blocks (a cat from a circle, two triangles and a rounded rectangle). Pip is a simple blue blob with a mouth. Icons are solid shapes with a 3-point outline.
- **Motion signature:** "stack and settle." Blocks drop into place with a short settle (no bounce in Navigators), tiles slide along a track in the Word Chain. Transitions 250 to 350 ms. Celebration: blocks tumble and rebuild as the word in 1.5 seconds.
- **Sound character:** wooden: clicks, clacks, a marimba for success, a hollow "donk" for a miss.
- **Letters and grid:** letter tiles are blocks with a beveled edge; the NPAT grid is four stacked shelves; the Word Chain is a row of blocks on a track where the last letter of one block is visibly shared with the next.
- **Risks:** can feel cold or generic; relies on motion and sound for warmth; less distinctive on a store page full of bright kids apps.
- **Effort:** low-medium. 3 to 4 design weeks. Pure vector, pure SwiftUI shapes; smallest bundle.

### 2.4 Direction D: "Storybook Watercolor"

- **Vibe:** soft and calm. Watercolor washes, ink linework, the feeling of a bedtime book. The closest relative of App 1's ink identity; quiet enough for a wind-down session.
- **Mood references:** classic watercolor picture-book illustration; the gentle, uncluttered pacing of Sago Mini (https://sagomini.com/); the paper-and-ink brand of App 1 itself.
- **Palette (hex):** Linen `#F6F1E8` (background), Ink Blue `#2E4A7A` (text), Wash Rose `#F2B8B5`, Wash Sage `#B9D6B3`, Wash Butter `#F7E3A1`, Wash Lavender `#CFC3E8`, Walnut `#5A4636` (secondary text). Washes are backgrounds only; text is always Ink Blue or Walnut for contrast above 4.5:1.
- **Typography:** a humanist serif for headings only (to echo App 1's ink identity), everything the child reads in a literacy sans (Andika or Atkinson Hyperlegible). Rationale: serifs on body text slow readers with dyslexia (Rello and Baeza-Yates found sans serif outperformed serif, https://link.springer.com/article/10.1007/s11881-016-0127-1), so serif is decorative and never on tiles.
- **Illustration and character:** ink line drawings with loose watercolor fill; Pip is an ink drop with a watercolor halo; letter creatures are storybook animals. The brand bridge to App 1 is strongest here.
- **Motion signature:** "bloom." Washes bloom outward when a letter is drawn (a Metal or Canvas shader shared with App 1's ink effects), lines draw themselves. Slow: 400 to 600 ms. Celebration: a watercolor bloom plus floating ink petals, 1.8 seconds.
- **Sound character:** soft: page turns, a music-box success, a quiet brush stroke.
- **Letters and grid:** letters are drawn in ink with a watercolor shadow; the NPAT grid is a notebook page with wash-colored rows; the Word Chain is a line of ink linking words along a ribbon.
- **Risks:** low energy for Explorers who want punch; watercolor at small sizes reads as blur; the ink shader must have a cheap static fallback for Reduce Motion and older iPads.
- **Effort:** medium. 4 to 5 design weeks; reuses App 1 ink shaders.

> **[DESIGN]** I want to be honest about my bias: D is the one I would hang on a wall and A is the one that would make a five-year-old grab the iPad. C is the one that ships on time and still looks good to a twelve-year-old.

> **[JOBS]** Four directions, and I will only let us build one. The question is not which is prettiest; it is which one makes the first thirty seconds feel like a toy and still works for a twelve-year-old without a second art budget.

> **[KIDS]** From the research side: A and B win on Sprouts engagement; B carries the most risk of the "everything is interactive" confusion; C has the best legibility story across bands; D is the calmest, which parents will like and Explorers may not.

> **[IOS]** Effort and risk: B needs a character animation runtime (Rive or Lottie) and the most assets; D needs a shader with a fallback; A needs a texture pipeline; C is shapes and SwiftUI. If the team is two people, C or A.

---

## 3. Comparison matrix and recommendation

Scores 1 to 5, higher is better.

| Criterion | A Crayon | B Monsters | C Blocks | D Watercolor |
|---|---|---|---|---|
| Sprouts appeal (5 to 7) | 5 | 5 | 4 | 3 |
| Explorers appeal (8 to 10) | 4 | 4 | 4 | 3 |
| Navigators appeal (11 to 13) | 2 | 1 | 4 | 4 |
| Legibility for early readers | 3 | 4 | 5 | 4 |
| Interactive vs decorative clarity | 3 | 2 | 5 | 4 |
| Brand bridge to App 1 | 2 | 1 | 3 | 5 |
| Distinctiveness on the store page | 4 | 5 | 3 | 4 |
| Reduce Motion and accessibility fit | 4 | 3 | 5 | 3 |
| Effort for a 2-person team | 3 | 1 | 5 | 3 |
| Bundle size and performance | 3 | 2 | 5 | 3 |
| Total | 33 | 28 | 43 | 36 |

**Recommendation:** Direction C "Bright Blocks" as the system, with two deliberate borrowings: Pip and the letter creatures take their warmth from Direction A (a crayon-textured outline on characters only, not on UI), and the Navigators skin takes its palette discipline from Direction D. This hybrid keeps the system small, scales across bands, and gives the characters the handmade charm that pure geometry lacks.

Parallel passes: Direction A survives as a skunkworks "theme pack" exploration for Sprouts after launch (a theme is a token swap plus character outlines if the system is built right). Direction B is parked; the monsters idea is kept as a future set of letter creatures within C. Direction D is not pursued for the kids app; its ink shader stays in App 1.

> **[JOBS]** Agreed, with one condition. Build the letter tile in C first and put it on an iPad in front of a five-year-old within a week. If she does not want to touch it, we revisit A.

> **[DESIGN]** Accepted. The tile is the first component, and the creature outline test comes with it.

**DECISION:** Direction C with A-styled characters and a D-disciplined Navigators skin. A is a post-launch theme skunkworks. B and D are not pursued for App 2.

---

## 4. Kid-specific motion rules

Apple's Motion guidance asks for purposeful motion, Reduce Motion alternatives and avoidance of flashing and vestibular triggers (https://developer.apple.com/design/human-interface-guidelines/motion). Children also track faster motion less reliably and are more likely to miss a change that happens in under 200 ms.

| Rule | Number | Why |
|---|---|---|
| Transitions are slower than App 1 | 300 to 450 ms (App 1 uses 200 to 300) | Children follow slower motion; faster feels abrupt |
| Moving things are bigger | Minimum animated element 44 points | Small moving things are not noticed |
| No flashing | Zero flashes; no luminance toggles faster than 1 Hz | WCAG 2.3.1 is the floor; we go to zero |
| Celebrate generously, briefly | Full-screen celebration allowed, under 2 seconds, never blocking input | Doc 02 rule; keeps the loop moving |
| Idle motion is slow and optional | Idle loops at 3 seconds or slower; off under Reduce Motion; off in Navigators by default | Avoid distraction from the task |
| One thing moves at a time | Never more than one primary animation plus ambient particles | Attention guidance |
| Reduce Motion alternative for every animation | Cross-fade or static state, same duration or shorter | HIG requirement |
| No parallax, no zoom-through transitions | None | Vestibular triggers |
| Haptics are soft | One light tap for success; none for failure; off by default for Sprouts on iPhone | Surprise haptics startle young children |
| Sound always has a visual twin | Every sound cue paired with a visible change | Muted devices and deaf children |

> **[IOS]** Implementation: a `KidsMotion` token set (durations, curves, spring parameters) in KidsDesignSystem, with every animation wrapped in a helper that checks `accessibilityReduceMotion` and substitutes the static alternative. Celebrations are SwiftUI with PhaseAnimator; particles via a lightweight Canvas, no SpriteKit in v1 to keep the dependency list short.

**DECISION:** Rules as tabled; motion tokens in KidsDesignSystem; no third-party animation runtime in v1.

---

## 5. Touch targets and layout rules, with numbers

Apple's general minimum is 44 by 44 points (https://developer.apple.com/design/human-interface-guidelines/accessibility). Children's touch is less precise; studies of 5 to 10 year olds show target width is the dominant predictor of success and children struggle with drag and with maintaining contact (https://init.cise.ufl.edu/?p=3232 and https://lisa-anthony.com/wp-content/uploads/2012/03/brown-and-anthony-chi2012eist.pdf).

| Element | Sprouts | Explorers | Navigators |
|---|---|---|---|
| Minimum tappable | 60 by 60 pt | 56 by 56 pt | 48 by 48 pt |
| Keyboard key (custom) | 72 by 72 pt on iPad, 56 by 64 on iPhone | 60 by 60 iPad, 48 by 56 iPhone | System keyboard |
| Spacing between targets | 12 pt minimum | 10 pt | 8 pt |
| Primary action button | 72 pt tall, full width minus margins | 64 pt | 56 pt |
| Letter tile (drawn letter) | 160 pt or 30 percent of the shorter side, whichever is larger | 120 pt | 96 pt |
| Category card | 96 pt tall | 80 pt | 64 pt |
| Edge exclusion zone (iPad bottom) | 24 pt no interactive content | 16 pt | 0 |
| Screen margins | 24 pt | 20 pt | 16 pt |
| Body text | 20 pt minimum | 18 pt | 17 pt |
| Letters in tiles | 28 pt minimum, typically much larger | 24 pt | 20 pt |
| Line length | 40 characters maximum | 50 | 60 |
| Items per screen | One category at a time (swipe or "Next" button) | Up to 4 categories | Up to 6 categories |
| Gestures required | Tap only | Tap and swipe | Tap, swipe, long press |
| Orientation | Landscape primary on iPad, portrait on iPhone | Both | Both |
| Home control | Top-left, always visible, 60 pt | Top-left | Top-left |

Dynamic Type: all kid text scales through the accessibility sizes; at the largest sizes the layout drops to one-category-per-screen in all bands and tiles scale with the text.

> **[KIDS]** The one-category-at-a-time layout for Sprouts is the most important layout decision in the app. Four empty fields is an intimidating form; one field with a big friendly prompt is a question.

**DECISION:** Numbers as tabled, enforced by a layout audit test in CI that fails on any kid-screen control under the band minimum.

---

## 6. Typography for early readers

| Need | Choice | Rationale and source |
|---|---|---|
| Letter tiles and body for Sprouts | Literacy sans with single-story a and g, distinct b/d/p/q, tailed l: Andika or Atkinson Hyperlegible | Andika was designed by SIL for beginning readers with letterforms that are not mirror images (https://en.wikipedia.org/wiki/Andika_(typeface)); Atkinson Hyperlegible differentiates confusable pairs (https://en.wikipedia.org/wiki/Atkinson_Hyperlegible) |
| "Friendlier letters" option | Adds OpenDyslexic as a user-selectable font with honest copy ("some readers like it; the research is mixed") | OpenDyslexic showed no measurable benefit in controlled studies (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5629233/ and https://link.springer.com/article/10.1007/s11881-016-0127-1), but we respect family preference |
| Default spacing | Letter spacing plus 4 percent, line height 1.5 | Rello and Baeza-Yates' broader work found spacing and size mattered more than font identity |
| Case | Lowercase for words, uppercase for the drawn letter with lowercase shown beneath in Sprouts ("B b") | Children learn both cases together; the paired display reinforces the link |
| Display headings | Rounded geometric bold | Warmth and hierarchy; never used for the words the child reads |
| Serifs | None on anything a child reads | Sans serif outperformed serif for dyslexic readers in eye tracking |
| Italic | Never | Italic hurt reading performance in the same study |
| Minimum sizes | 20 pt body Sprouts, 28 pt tile letters | Above Apple's platform minimums; children read larger text more fluently |

**DECISION:** Atkinson Hyperlegible as the default kid UI and tile face (broad glyph coverage, open license), with Andika's single-story forms evaluated as an alternate set in the Phase 2 vertical slice; OpenDyslexic as an opt-in.

**OPEN:** Whether a custom rounded display face is worth commissioning or whether an open license face suffices for v1.

---

## 7. How letters, the grid and the chain look

**The drawn letter** is the hero. In C it is a block tile, beveled, in one of the four block colors, uppercase with the lowercase small beneath for Sprouts. On draw, it drops in from above and settles (no bounce in Navigators). Tap it to hear its name and sound. The picture cue (A with an alligator) sits as a small badge on the tile's corner for Sprouts.

**The NPAT grid** is a set of shelves, one per category. For Sprouts, one shelf at a time fills the screen with the category icon (a paw for Animal, an apple for Food), the prompt ("An animal that starts with B"), the answer field and the big keyboard. For Explorers, four shelves stack on an iPad; on iPhone they scroll, with the active shelf highlighted. Each filled shelf gets a small block in the drawn letter's color.

**The Word Chain** is a track of blocks. Each word is a block; the last letter of the block is a distinct color and physically connects to the first letter of the next block, so the rule is visible without explanation. In Sprouts the track scrolls slowly as the chain grows; a counter shows the chain length as a growing stack of small blocks rather than a number.

**The keyboard** (Sprouts and Explorers) is custom: alphabetical order as an option for Sprouts (research is mixed on alphabetical versus QWERTY for young children, so both are offered; QWERTY is default for Explorers), lowercase glyphs with the uppercase on long press, keys that enlarge on touch, and a delete key that is deliberately smaller and placed away from the letters to avoid accidental erasing.

**The celebration** builds the correct word from tumbling blocks, with the corrected letters (if any) landing last and glowing briefly. Pip cheers from the corner.

**The sticker book** is a shelf of pages, one per category, with stickers as flat vector illustrations in the A-styled crayon outline. Placing a sticker makes a soft wooden click.

> **[GAME]** The visible letter connection in the Word Chain track is the single best piece of game-design communication we have. It teaches the rule without text.

---

## 8. The parent area: a distinct adult language

The parent area must read as "for grown-ups" in one glance, which also helps the child understand it is not theirs. It uses App 1's adult design language (ink, paper, serif headings, standard system controls) rather than the kids system. This is the one place the two apps look like siblings.

Settings parents actually want, from early interviews:

| Setting | Default | Notes |
|---|---|---|
| Child profiles (nickname, avatar, band) | One profile created at first run | Up to 6 (30 in classroom preset) |
| Band per profile | Chosen at setup | With the "suggestion" surfaced after 20 rounds |
| Timer mode | Band default | Off, soft, standard |
| Sounds and voice | On | Separate toggles for music, effects, auto-read voice; voice selection |
| Friendlier letters | Off | Font choice including OpenDyslexic |
| Haptics | Off for Sprouts, on otherwise | |
| Hints | Band default | Can be restricted for Navigators |
| Silly categories | On | Can be turned off per family |
| Approved words queue | | Review and approve unknown words |
| What this app stores | | A plain list: profiles, stickers, word history, settings; "Nothing leaves this device" |
| Delete a profile or everything | | One tap, confirm, done |
| Classroom preset | Off | Band, sounds off, big-letter mode, 30 profiles, clear all |
| Trust page and privacy policy | | In-app content with an external link behind the gate |
| About and licenses | | Content changelog, font and dictionary licenses |
| Rate the app | | Once, optional, adult-only |

**DECISION:** Parent area uses App 1's adult design language; the settings list above is the v1 scope.

---

## 9. Parental gate pattern options

Apple requires a parental gate ("adult-level tasks that must be completed in order to continue") before link-outs, purchases and permission requests in Kids Category apps, and suggests a voice prompt for pre-literate children (https://developer.apple.com/app-store/kids-apps/). Patterns compared:

| Pattern | Description | Pros | Cons | Robustness to random taps | Accessibility |
|---|---|---|---|---|---|
| Arithmetic with spelled-out numbers | "What is twelve plus seven? Type the answer." Numbers change each time | Widely used, reviewer-familiar; words not digits defeat young readers | A sharp 9-year-old can pass; typing needed | Good | Good with VoiceOver; needs text input |
| Hold-to-confirm | "Hold with two fingers for 3 seconds" | Fast for parents; no reading | Any child can hold | Poor alone | Poor for motor impairments |
| Year-of-birth style adult knowledge | "In what year were you born? Swipe to a year before 2008" | Hard for young kids | Leaks nothing if not stored; but feels like data collection | Medium | Good |
| Multi-step: arithmetic plus hold | Arithmetic, then hold | Strongest | Slower | Excellent | Mixed |
| Device authentication (Face ID or passcode via LocalAuthentication) | The parent's own biometric or device passcode | Strongest signal of an adult owner; zero reading; instant | A child may share the device passcode; on a child's own device the child is the enrolled user | Excellent | Excellent |

> **[IOS]** Device authentication is tempting but fails the common case: the device is the child's own iPad with the child's face enrolled. It can be an option the parent turns on for a shared family device, not the default.

> **[KIDS]** Arithmetic with spelled-out numbers remains the pragmatic default. Pair it with a spoken prompt for pre-readers ("This part is for a grown-up. Please ask one to help.") as Apple suggests, and rotate problems so the answer cannot be memorized.

> **[QA]** Test requirement: the gate must survive 60 seconds of random tapping and a replay of a previously correct answer.

**DECISION:** Default gate is spelled-out arithmetic with a spoken "ask a grown-up" prompt; optional device authentication for shared devices; the gate wraps every link-out, permission prompt and the whole parent area. ParentalGate package owns all patterns.

---

## 10. Component inventory differences from App 1

| Component | App 1 | App 2 | Shared? |
|---|---|---|---|
| Design tokens (spacing, radius, motion curve names) | Yes | Yes, same primitives, different values | Tokens package shared |
| Letter tile | Ink-on-paper, 96 pt | Block tile, 96 to 160 pt, picture cue badge, tap-to-hear | No |
| Keyboard | System | Custom big keyboard (Sprouts, Explorers) | No |
| Category card | Compact row | Shelf with icon and prompt | No |
| Timer | Ring with digits | Sleepy sun, ink line, calm ring | No |
| Score display | Numbers | Stars and blocks (Sprouts), numbers plus stars (Explorers) | No |
| Celebration | Ink splash | Block tumble, Pip cheer | No |
| Companion character | None | Pip, with idle, cheer, shrug, think | New |
| Letter creatures | None | 26 collectible | New |
| Sticker book | None | New | New |
| Handoff screen | Simple | Big avatar, spoken name | No |
| Parental gate | None | New | New |
| Parent area | Settings | Full adult area in App 1 language | Partially (App 1 components) |
| Bot presence | Minimal | Characters with speech bubbles | New |
| Hint controls | "Did you mean" | Picture, first-two-letters, example, give-me-one | New |
| Sound set | Ink and paper | Wooden clicks and marimba | No |

---

## 11. Microcopy voice and 30 example strings

Voice rules: speak to the child as a friendly older cousin, not a teacher and not a cartoon; short sentences; no exclamation stacking (one per message at most); never "wrong," "fail," "oops" in Sprouts; always point to the next thing to do; adult copy in the parent area is plain, calm and specific. All kid strings are also spoken by the auto-read voice, so they must sound natural aloud.

Kid-facing, general:
1. "Your letter is B. B is for bear. Can you think of a different animal?"
2. "Tap the letters to spell your word."
3. "Your turn, Maya!" (handoff)
4. "Pass the phone to Sam. No peeking!"
5. "Ready when you are. There is no rush."
6. "Pip is thinking... Pip says: Bunny!"
7. "Want a hint? Tap the lightbulb."
8. "Here are the first two letters: Z E"
9. "A place is somewhere you can go. Like the park."
10. "New letter unlocked! Say hello to K."

Kid-facing, success:
11. "Zebra! You spelled it Z-E-B-R-A."
12. "Elephant! Here is how it is spelled: E-L-E-P-H-A-N-T."
13. "You and Sam both said cat. Great minds!"
14. "Chain of ten! That is your longest yet."
15. "You found a sticker. Want to put it in your book?"
16. "Bear! That was my example, you cheeky thing. Can you find another next time?"

Kid-facing, gentle failure:
17. "Ooh, that starts with T. We need a B word. Want to try again?"
18. "I do not know that one yet. Want to ask a grown-up?"
19. "That is a tricky one. Skip it, or try a hint?"
20. "We already had cat. Can you think of another animal?"
21. "Let's try a different word." (safety filter, deliberately flat)
22. "Out of time for this one. It happens. Next letter!"
23. "Pip could not think of one. You win this round!"
24. "Out this round, Sam. You can still cheer for Maya."
25. "Hmm, that is not quite an animal. Banana is a food, and it is a thing too."

Kid-facing, stopping:
26. "That was a good game. See you next time."
27. "Time for a break? Your stickers will be here when you come back."

Parent-facing:
28. "This part is for grown-ups. What is fourteen plus six?"
29. "Nothing your child types leaves this device. Here is everything this app stores: 2 profiles, 31 stickers, 212 words, your settings."
30. "Delete Maya's profile? This removes her stickers and word history from this device. It cannot be undone."

> **[KIDS]** Line 21 is intentionally the most boring string in the app. Line 27 is the only "come back" message and it promises nothing and withholds nothing.

> **[JOBS]** Line 5 is the whole app in five words. Put it on the first screen.

**DECISION:** Voice rules and the 30 strings above are the reference set; all new strings are reviewed against them by KIDS.

---

## 12. Decisions and open questions

**DECISIONS**
- Direction C "Bright Blocks" with A-styled characters and a D-disciplined Navigators skin.
- Direction A survives as a post-launch theme skunkworks; B and D not pursued for App 2.
- Motion rules as tabled; no third-party animation runtime in v1.
- Touch target and layout numbers as tabled, enforced by CI layout audit.
- Atkinson Hyperlegible default, Andika alternate set evaluated, OpenDyslexic opt-in.
- Parent area uses App 1's adult language.
- Default gate: spelled-out arithmetic with spoken prompt; optional device authentication.

**OPEN**
- Custom display face versus open license face.
- Alphabetical versus QWERTY default for Sprouts keyboard (test both in Phase 2).
- Whether Navigators default skin should drop Pip entirely.
- Illustration format for picture hints (vector preferred per doc 03; confirm quality in the slice).

---

## 13. Sources

- Apple Human Interface Guidelines: root https://developer.apple.com/design/human-interface-guidelines/ ; Accessibility https://developer.apple.com/design/human-interface-guidelines/accessibility ; Motion https://developer.apple.com/design/human-interface-guidelines/motion ; Typography https://developer.apple.com/design/human-interface-guidelines/typography ; Designing for games https://developer.apple.com/design/human-interface-guidelines/designing-for-games
- Apple, Kids apps and parental gates: https://developer.apple.com/app-store/kids-apps/
- Sherwin and Nielsen, Children's UX (NN/g): https://www.nngroup.com/articles/childrens-websites-usability-issues/
- Sesame Workshop, Best Practices: Designing Touch Tablet Experiences for Preschoolers (Joan Ganz Cooney Center): https://joanganzcooneycenter.org/?p=19607
- WCAG 2.1 SC 2.3.1 Three Flashes or Below Threshold: https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold
- INIT lab, Fitts' law for children's touch: https://init.cise.ufl.edu/?p=3232 ; Brown and Anthony: https://lisa-anthony.com/wp-content/uploads/2012/03/brown-and-anthony-chi2012eist.pdf
- Andika typeface (SIL): https://en.wikipedia.org/wiki/Andika_(typeface)
- Atkinson Hyperlegible (Braille Institute): https://en.wikipedia.org/wiki/Atkinson_Hyperlegible and https://github.com/googlefonts/atkinson-hyperlegible
- Rello and Baeza-Yates, font type and dyslexia: https://link.springer.com/article/10.1007/s11881-016-0127-1
- Wery and Diliberto, OpenDyslexic study: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5629233/
- Mood references (official sites): Sago Mini https://sagomini.com/ ; Toca Boca https://tocaboca.com/ ; Originator (Endless Alphabet) https://www.originatorkids.com/ ; Khan Academy Kids https://learn.khanacademy.org/khan-academy-kids/ ; PBS Kids https://pbskids.org/
