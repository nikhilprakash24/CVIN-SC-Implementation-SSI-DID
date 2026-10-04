# App 2 "Inkwell Kids": Game Adaptations and Age Bands

**Read this if...** you are designing or building how Name Place Animal Thing (NPAT) and Word Chain change for children in the three bands (Sprouts 5 to 7, Explorers 8 to 10, Navigators 11 to 13): categories, letters, timers, hints, forgiving validation, celebration, cooperative and solo modes, pass-and-play, non-manipulative progression, kid-safe content curation, accessibility for dyslexia and motor challenges, and the classroom case. It ends with 27 edge cases and debates.

**Document status:** Draft v0.1, 2026-10-04, owner **[GAME — Game Designer, "Kenji Watanabe"]** with **[KIDS — Child UX & Learning Specialist, "Dr. Amara Nwosu"]** and **[DATA — Content & Dictionary Engineer, "Omar Haddad"]**.

---

## Table of contents

1. Design stance: same games, different tempo
2. Band matrix: one table for everything
3. Categories per band, including the silly ones
4. Letter selection
5. Timers
6. Hint systems
7. Forgiving validation: tolerance tiers
8. Celebration and feedback
9. Modes: cooperative, solo vs bots, pass-and-play
10. Progression that does not manipulate
11. Difficulty ramp
12. Kid-safe dictionary and category lists
13. Accessibility for dyslexia and motor challenges
14. Teacher and classroom use
15. Edge cases and team debates (27)
16. Decisions and open questions
17. Sources

---

## 1. Design stance: same games, different tempo

The rules of NPAT and Word Chain do not change. A letter is drawn; you write a name, a place, an animal, a thing. The last letter of my word starts your word. What changes for children is the tempo (slower or no clock), the surface area (big tiles, few choices), the tolerance (we accept what the child meant), and the emotional register (nothing is a failure, everything is a try). The shared engine from App 1 (`IWCore` plus `IWRules` in the architecture document; "GameEngine" in the brief) supplies the state machine; App 2 supplies a `KidsRuleSet` configuration per band and a `KidsValidator` that wraps the App 1 dictionary (`IWContent`) with tolerance tiers.

> **[GAME]** The hard constraint I set for myself: a 10-year-old who learned the game here should be able to sit down with a pencil and play the real paper game with cousins. We are teaching the actual game, with training wheels that come off.

> **[KIDS]** And my constraint: no child should ever learn a wrong spelling from us. Forgiveness in scoring, honesty in feedback.

---

## 2. Band matrix: one table for everything

| Parameter | Sprouts 5 to 7 | Explorers 8 to 10 | Navigators 11 to 13 |
|---|---|---|---|
| NPAT categories per round | 2 to 3 (Animal, Thing, plus one fun category) | 4 classic plus optional fun ones | 4 to 6 including custom |
| Letter pool | 16 letters: A B C D E F G H L M P R S T W plus one of (K, N, O) rotated | 22 letters, excluding Q X Z (and J by default) | Full 26, with Q X Z weighted low and a "spicy letters" toggle |
| Timer default | Off | Gentle: 90 seconds per round, soft start | Standard: 60 seconds, option for 45 |
| Timer presentation | None, or a sleeping sun that slowly wakes (no numbers) | A filling ink line, no numbers until the last 15 seconds | Numeric with a calm ring |
| Hints | Always available: picture, first two letters, spoken example | Available, cost nothing but shown in the recap | Available, cost 2 points of the 10 |
| Validation tier | Tier 3 (phonetic plus category intent) | Tier 2 (one-edit tolerance) | Tier 1 (exact, with a "did you mean" nudge) |
| Scoring | Stars, not numbers: one star per filled category | Classic 10/5/0 shown as stars and numbers | Classic 10/5/0 with house rules |
| Input | Large on-screen letter keyboard (custom), voice optional | Custom keyboard or system keyboard | System keyboard with autocorrect off |
| Word Chain lives | Unlimited; a wrong answer passes the turn | 3 lives | 1 life or points mode |
| Word Chain categories | Animals, Foods, Things in a House | plus Countries, Cities (with hints), Movies (curated) | plus any curated list and custom lists |
| Bots | One friendly bot who makes mistakes | Two bots with personalities and skill levels | Bots with adjustable skill and a "no mercy" setting |
| Session shape | 1 round, then a sticker and a natural stop | 3 rounds, then recap | Configurable |
| Reading support | Auto-read everything | Tap-to-hear | Off by default, available |

> **[JOBS]** This table is the product. Every other section is footnotes to it. If it does not fit on one screen in a review meeting it is too complicated.

---

## 3. Categories per band, including the silly ones

### 3.1 Classic categories by band

| Category | Sprouts | Explorers | Navigators | Notes |
|---|---|---|---|---|
| Name | Later (unlocks after 5 rounds) | Yes | Yes | Names are proper nouns; see 12.4 |
| Place | No (replaced by "Somewhere you can go") | Yes, with picture hints | Yes | Young children do not reliably know countries; "the park" is a fine place |
| Animal | Yes | Yes | Yes | Richest kid vocabulary |
| Thing | Yes | Yes | Yes | Broadest; hardest to validate |
| Food | Yes | Yes | Yes | Second richest kid vocabulary |
| Color | Yes (very small set; allow repeats across rounds) | Optional | No | Only works for a handful of letters |
| Movie or Show | No | Curated family titles | Curated, broader | Licensing-safe: titles are facts, but keep lists to widely known family titles |
| Brand | No | No | Optional | Avoids advertising feel; off by default |
| Body part | Yes | Yes | Yes | Kids love it; curated to non-anatomical-sensitive list |
| Job | No | Yes | Yes | |
| Sport or Game | Optional | Yes | Yes | |

### 3.2 Silly categories (the real engine of fun)

Children in playtests of similar word games laugh most at categories that invite absurd or gross answers, and that invite debate. These are curated allow-lists like everything else, but with permissive "Thing" fallbacks (see tier rules in section 7).

Sprouts: Things that are sticky; Things that are soft; Something you can wear on your head; Things in a lunchbox; Animals that are small; Things that go fast; Things that make a noise.

Explorers: Things that smell; Things a pirate would say (phrases allowed); Things you should not put in your mouth; Things you find under a bed; Superpowers; Things that are round; Things a dog would want; Things you would pack for the moon.

Navigators: Things that are overrated; Inventions that do not exist yet; Band names (made-up allowed in party mode); Excuses for not doing homework; Things in a wizard's pocket; Things that are both a verb and a noun (word-nerd tier).

> **[GAME]** "Things you should not put in your mouth" is the single best category I have ever tested with eight-year-olds. The validator problem is that almost everything is a valid answer. That is fine; the fun is in reading them aloud in the recap.

> **[DATA]** For open-ended silly categories, validation collapses to "is it a real, kid-safe word that starts with the letter". I will implement them as Thing-category fallbacks with the kid-safe allow-list, plus the category name for recap display. No separate list to curate.

> **[KIDS]** Agreed, with one guard: "Things a pirate would say" admits phrases, which means a free-text field. All free text must pass the local safety filter before it is shown to another player in pass-and-play. See section 12.5.

**DECISION:** Silly categories ship in all bands. Open-ended ones validate against the kid-safe general allow-list; phrase categories exist only in Explorers and Navigators and route through the local safety filter before display.

---

## 4. Letter selection

Letters are drawn from a per-band pool with weights. The App 1 engine already supports letter exclusion (the X/Q/Z house rule); App 2 extends that with weights derived from how many kid-safe words exist per category per letter.

| Rule | Sprouts | Explorers | Navigators |
|---|---|---|---|
| Excluded | J K N O Q U V X Y Z (rotate K, N, O back in after 10 rounds played) | Q X Z (J optional) | None by default |
| Weighted down | I, U (few kid animals) | V, Y, U | Q, X, Z weighted to 1 in 60 |
| No-repeat window | Last 5 letters | Last 8 letters | Last 10 letters |
| Picture cue | Always: letter shown with an illustrated animal whose name starts with it (A with an alligator) | On request | Off |
| Letter sound | Played on draw (letter name and phoneme: "B, buh") | On tap | Off |

> **[DATA]** I ran a count on the draft kid-safe lists: for Animal, the letters with fewer than 5 kid-safe entries are Q, X, U (umbrella bird does not count), V (vulture, viper, and not much), Y (yak). For Food, X and Q are empty, Z has zucchini. The Sprouts pool is chosen so every category has at least 8 candidates per letter.

> **[KIDS]** The picture cue matters more than people think. A Sprout who sees "B" with a bear has both a phoneme anchor and an example that is explicitly not allowed to be their answer. We should say "B, like bear. Can you think of a different animal?"

> **[GAME]** Rotating K, N, O back in after 10 rounds is the first visible difficulty ramp. We say "New letter unlocked!" and it feels like a reward even though it is harder.

**DECISION:** Per-band weighted pools as tabled. Minimum 8 kid-safe candidates per category per letter is a content acceptance criterion for Sprouts, 5 for Explorers.

---

## 5. Timers

Timers are the most anxiety-producing element of the adult game and the first thing we soften.

| Band | Default | Options | Visual | Audio |
|---|---|---|---|---|
| Sprouts | Off | "Sleepy sun" soft timer of 3 minutes that never ends the round, only suggests moving on | A sun drifting across the top; no digits | A gentle yawn at the end, no beeps |
| Explorers | 90 seconds, gentle | Off, 90, 60; "stop rule" off | Ink line fills; digits appear only at 15 seconds left | Soft tick in last 10 seconds, can be turned off |
| Navigators | 60 seconds | Off, 90, 60, 45, Blitz 30 | Calm ring with digits | Optional tick |

Rules in all bands: the timer never flashes, never turns red, never accelerates its sound. When time runs out, the round ends on the next completed field, not mid-word (the engine's "grace completion" state from App 1). The "stop rule" (first finisher ends the round) is off by default in Sprouts and Explorers because it rewards speed over thought and creates sibling conflict.

> **[GAME]** I pushed back on timer-off as default for Sprouts because without time pressure NPAT loses its tension. Kenji from six months ago would have been wrong. Testing with young kids on other games shows the tension comes from "can I think of one" not "can I think of one in time".

> **[KIDS]** The sleepy sun is a timer that cannot be lost. It is a pacing cue for the parent and a story for the child.

> **[ARCH]** Engine note: the App 1 timer is a state-machine input event, so "off", "soft", and "hard" are different event emitters feeding the same engine. No fork required.

**DECISION:** As tabled. Stop rule off by default below Navigators.

---

## 6. Hint systems

Hints exist to prevent the blank-field freeze that ends a young child's session. Three hint types, available by band.

| Hint type | How it works | Sprouts | Explorers | Navigators |
|---|---|---|---|---|
| Picture hint | Shows an illustration of a valid answer, no text; the child still has to name and spell it | Free, unlimited | Free, logged in recap | Not offered |
| First two letters | Fills the first two letters of a valid answer in the field | Free | Free, logged | Costs 2 of 10 points |
| Category example | Speaks and shows an example that does not start with the letter ("A place is somewhere you can go, like the park") | Free | Free | Free |
| Letter sounds | Replays the letter name and phoneme | Free | Free | Free |
| "Give me one" | Fills a complete valid answer; scores zero but keeps the round moving | Free, after 20 seconds of inactivity, offered not forced | Available, scores 0 | Available, scores 0 |

Hint rules: hints never pick the most common answer (so "ant" is not the picture for A, Animal, every time); the hint pool excludes the letter's picture cue; hints used are shown in the recap as little lightbulbs, never as a penalty for Sprouts and Explorers.

> **[KIDS]** The "Give me one" hint is essential for Sprouts. A frozen child with a blank field and a parent saying "come on, think" is the worst possible outcome. The app offers a way out before the parent does.

> **[GAME]** For Navigators, hints must cost something or the game has no edge. Two points is enough to make a 12-year-old think twice and not enough to make them never use it.

**DECISION:** As tabled.

---

## 7. Forgiving validation: tolerance tiers

This is the hardest design problem in the app: accept what the child meant without teaching them that the wrong spelling is right.

### 7.1 Tiers

| Tier | Name | What it accepts | Feedback shown | Used by |
|---|---|---|---|---|
| 1 | Exact | Exact match against the category allow-list, case-insensitive, diacritics folded | None needed | Navigators |
| 2 | Near | Tier 1 plus one edit (Damerau-Levenshtein distance 1) for words of 4 or more letters, as long as the result is unique in the list | "Yes! It is spelled G-I-R-A-F-F-E" with the corrected word written in | Explorers |
| 3 | Phonetic | Tier 2 plus phonetic match (Double Metaphone or a kid-tuned variant) against the list, with the first letter required to match the drawn letter | "Elephant! Spelled E-L-E-P-H-A-N-T" with letters animating into place | Sprouts |
| 0 | Intent | Tier 3 plus category intent: a valid word that starts with the letter but is in the wrong category is accepted in the silly or Thing fallback with a gentle note | "A banana is a food, and it is a thing too!" | Sprouts only |

Hard rules at every tier:
- The first letter typed must match the drawn letter. Forgiveness never extends to the letter, because the letter is the game.
- The accepted word shown back to the child is always the correct spelling. We never echo the misspelling as if it were right.
- Scoring in Sprouts does not depend on tier; a tier 3 match earns the same star as exact. In Explorers, tier 2 matches earn full points in untimed mode and full points in timed mode too (we considered a 1-point penalty and rejected it, see edge case 7).
- In Navigators, a tier 2 near-miss is not accepted automatically; the app asks "Did you mean GIRAFFE?" and the child confirms, earning 8 of 10.

### 7.2 Avoiding "rewarding wrong spellings"

The risk is that a child learns that "elefant" works. Mitigations:
1. The correction animation: the child's letters morph into the correct letters one at a time, with the changed letters briefly highlighted. This is the only "teaching moment" in the app and it is quick.
2. In the recap, the child's original attempt is never shown; only the correct word.
3. The parent area shows "words your child spelled a new way" with both forms, so the parent can decide whether to work on it.
4. Over time (on-device), if the same misspelling recurs 3 times, Sprouts and Explorers show the first-two-letters hint pre-filled for that word next time it is a candidate.

> **[DATA]** Phonetic matching against a 400-word kid animal list is trivial on device and fast. The failure mode is false positives: "cat" and "kit" both phonetically near "ket". The first-letter constraint removes most of these; requiring the match to be unique within the category list removes most of the rest. Where two candidates remain, we show both as picture choices and let the child tap.

> **[KIDS]** That tap-to-choose fallback is good pedagogy too. The child sees two real words and picks the one they meant.

> **[GAME]** One more scoring edge: duplicates. If two kids both write "elephant", one as "elefant", classic rules give 5 each. We treat them as the same answer after correction. Fair.

**DECISION:** Tiers as tabled. Corrections always shown; attempts never echoed as correct. Duplicate detection runs after correction.

---

## 8. Celebration and feedback

| Moment | Sprouts | Explorers | Navigators |
|---|---|---|---|
| Valid answer entered | Letters wiggle, a soft chime, the category creature nods | Tick with a small ink splash | Subtle tick |
| Round complete | Confetti of letters, 1.5 seconds, sticker reveal | Score tally with stars flying in, 2 seconds | Score tally, personal best callout if any |
| Blank or no answer | "That is a tricky one! Want a hint next time?" with the creature shrugging | "No answer for Place. It happens!" | Blank shows 0, no copy |
| Wrong letter | "Ooh, that starts with T. We need a B word!" with the B glowing | "Needs to start with B" | Field outline, no copy |
| Duplicate with another player | "You and Maya both said cat! Great minds!" | "Shared answer: 5 points" | "5" |
| Game won | Everyone claps, no "loser" named | Winner announced, "Great game, everyone" | Winner, scores, rematch button |
| Game lost (Word Chain elimination) | Not possible in Sprouts (unlimited lives) | "Out this round! You can still cheer" | "Out" |

Rules: no red, no buzzer, no sad faces, no "wrong" in Sprouts copy. Celebrations never require a tap to dismiss. The Reduce Motion alternative is a static sticker with a chime. Every sound has a visual equivalent. Haptics are soft (a single light tap for success, none for failure).

> **[DESIGN]** Celebration length is the number I will police: under 2 seconds and the next action is enabled during the animation, not after.

> **[JOBS]** Also: the first-ever valid answer a child enters gets the biggest celebration the app will ever show. The first thirty seconds decide whether the child plays again.

**DECISION:** As tabled. First-ever-answer celebration is a specified moment in the design directions (doc 04).

---

## 9. Modes: cooperative, solo vs bots, pass-and-play

### 9.1 Cooperative modes (new to App 2)

- **Family vs the Clock (NPAT):** everyone shouts answers and one person types; the family tries to fill all categories before the sleepy sun sets. No individual scores. Designed for a parent and a Sprout.
- **Team vs the App (Word Chain):** the family takes turns against a bot; the family wins by outlasting the bot. The bot's skill is set by band.
- **Build the Longest Chain:** cooperative Word Chain with no opponent; the goal is a longer chain than last time. Progress saved per profile.

### 9.2 Solo vs friendly bot characters

Bots are characters with names, personalities and visible "thinking". They make mistakes at band-appropriate rates and sometimes explain their answers ("Narwhal! It is a whale with a horn!"). Bot answers are drawn only from the kid-safe allow-list.

| Bot | Band | Personality | Skill |
|---|---|---|---|
| Pip (a small inkblot) | Sprouts | Enthusiastic, often wrong, laughs at itself | Answers 60 percent of categories, slow |
| Wren (a bird with glasses) | Explorers | Thoughtful, gives a fact with each answer | Answers 80 percent |
| Rook (a cool raven) | Explorers, Navigators | Competitive, teases gently | Answers 90 percent, fast |
| The Librarian | Navigators | Dry, encyclopedic, "no mercy" option | Answers 100 percent at max |

> **[GAME]** The bot must lose sometimes to a Sprout. Pip is designed to be beatable by a six-year-old roughly two rounds in three. That ratio is the thing we tune in playtests.

> **[KIDS]** Bots also model good behavior: Pip says "good one!" when the child answers. Children copy what characters do.

### 9.3 Pass-and-play on a family phone

Pass-and-play is the primary multiplayer mode. Flow: choose players (profiles with avatars), the letter is drawn, Player 1 fills in, taps "Pass to Maya", a handoff screen hides answers and shows Maya's avatar large with "Your turn, Maya!" spoken aloud, Maya taps to begin. Answers are compared only at the recap. Timers in pass-and-play are per player and pause during handoff. Up to 6 profiles.

Nearby play (MultipeerConnectivity) is a post-launch stretch, outside the 16-week plan (doc 03): it transmits only answers and profile nicknames between devices on the local network, never to a server, and the nicknames go through the safety filter.

Online play does not exist in App 2.

**DECISION:** Pass-and-play and cooperative modes in v1. Nearby play is a post-launch stretch. No online play, ever, in App 2.

---

## 10. Progression that does not manipulate

Progression exists to give a sense of growth and collection, not to drive return visits.

- **Letter creatures:** 26 collectible creatures, one per letter (A is an alligator, and so on). A creature is earned by producing a valid answer for that letter in each of three categories, across any number of sessions. All 26 are reachable with no time limit, no randomness and no purchase.
- **Sticker book:** a sticker per round completed, from a deterministic sequence; duplicates do not exist; the book has pages per category. Stickers can be placed on a "my page" canvas for fun.
- **Badges:** a small set (12 at launch) for things like "First chain of 10", "Tried every silly category", "Played with a grown-up". No badge is for consecutive days. No badge is visible as "locked" with a countdown or a cost. Unearned badges appear as faint outlines with a plain description of how to earn them.
- **Personal bests (Navigators):** longest chain, fastest full round, most unique answers in a game.

Explicit non-features: no daily rewards, no streaks, no "come back tomorrow for", no limited-time events, no currency of any kind, no random drops, no "you are so close" spend prompts.

> **[JOBS]** The sticker book will be the thing kids show their parents. Treat it like the app's trophy room and make placing stickers feel physical.

> **[GAME]** I want to register that I asked for a soft currency (ink drops) to buy sticker book pages and was told no. On reflection the team is right: a currency is the first step toward every pattern in doc 01's refusal list.

> **[KIDS]** The ICO Children's Code standard 13 on nudge techniques and the FTC dark patterns report are both explicit that reward and continuity mechanics aimed at children are a regulatory risk, not just a taste question. See doc 05.

**DECISION:** Letter creatures, sticker book, 12 badges, personal bests for Navigators. No currency, no streaks, no timed anything.

---

## 11. Difficulty ramp

Within a band, difficulty rises through content, not through pressure.

| Stage | Sprouts | Explorers | Navigators |
|---|---|---|---|
| Start | 2 categories (Animal, Food), 16-letter pool, all hints | 4 classic categories, 22 letters, 90 seconds | 4 categories, 26 letters, 60 seconds |
| After 5 rounds | Add a silly category; unlock Name | Add silly categories; offer 60 seconds | Offer Blitz |
| After 10 rounds | Rotate K, N, O into the pool with "New letter!" | Offer J | Offer 6 categories |
| After 20 rounds | Offer Explorers preview ("Try the next level?") visible to the parent only | Offer Navigators preview to the parent | Custom categories |

Band changes happen only through the parent area. The child can never accidentally promote or demote.

> **[KIDS]** The band is a parent decision because parents know their child's reading. We can suggest, in the parent area, "Maya has had 20 rounds with no hints; Explorers might be fun" and leave it there.

**DECISION:** Content-driven ramp; band change gated to parents; suggestion shown in the parent area only.

---

## 12. Kid-safe dictionary and category lists

### 12.1 Allow-lists, not block-lists

App 1 validates against large open dictionaries (ENABLE, SCOWL, WordNet-seeded and curated category lists, GeoNames; Wiktionary-derived data is excluded from App 1's v1 packs per its ADR-007). For App 2 the default is inverted: a word is valid only if it appears on a curated kid-safe allow-list for the category. A block-list approach cannot be made safe for children because the space of offensive or inappropriate words, phrases and near-spellings is unbounded and new ones appear constantly. An allow-list makes the safe set finite and reviewable.

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| Block-list over App 1 dictionary | Broad vocabulary, little curation | Impossible to make complete; phonetic tolerance makes it worse (a misspelling of a slur can match) | Rejected for kids |
| Allow-list per category (recommended) | Finite, reviewable, every word has been seen by a human | Rejects legitimate rare words; needs a curation workflow | Adopted |
| Allow-list plus "ask a grown-up" escape | Allow-list, with unknown words set aside for parent approval in the parent area | Adds a workflow but recovers rare words | Adopted as an addition |

### 12.2 List sizes and sources

| Category | Target size (Sprouts / Explorers / Navigators) | Seed sources | Curation notes |
|---|---|---|---|
| Animal | 400 / 900 / 1500 | WordNet animal hyponyms, children's dictionary word lists, public domain picture dictionaries | Remove breeds with brand-like names, remove anything with an unfortunate homonym |
| Food | 300 / 700 / 1200 | WordNet food hyponyms, school lunch vocabularies | Include international foods; mark dishes vs ingredients |
| Thing | 1500 / 4000 / 8000 | Age-graded word lists (Dolch, Fry high-frequency lists for Sprouts), SCOWL size 35 and below filtered by human review | Largest effort; reviewed in batches |
| Place | 0 (uses "Somewhere you can go") / 600 / 1500 | Countries, capitals, large cities, landmarks, generic places (park, beach) | Proper nouns, see 12.4 |
| Name | 300 / 1500 / 3000 | Public national name registries (for example US SSA baby names, UK ONS), filtered | Proper nouns, see 12.4; inclusive of many cultures |
| Silly categories | Fall back to Thing | | |

Licensing: WordNet (Princeton license, permissive), ENABLE (public domain), SCOWL (permissive). Government name lists are public data. Any list derived from Wiktionary carries CC BY-SA and must be attributed in the parent area's "About" screen. **[DATA]** will keep a license manifest per list in the KidsContent package.

### 12.3 Curation workflow

1. Seed: generate candidate lists from sources with scripts in the content pipeline (shared with App 1, doc 03).
2. Filter: remove words on a conservative profanity and sensitive-topic list (weapons beyond toy level, drugs, sexual, death-related, slurs, and words with common offensive homophones).
3. Human review: every word in Sprouts and Explorers lists is seen by two reviewers (one must be **[KIDS]** or a delegate with child-development background). Navigators lists are reviewed by one plus spot checks.
4. Phonetic collision audit: run the tier 3 matcher over the list against itself and against the profanity list; any kid word whose phonetic key collides with a blocked word is flagged and either removed or marked exact-only.
5. Picture hint coverage: every Sprouts word needs an illustration or is marked no-hint.
6. Sign-off: lists are versioned; a release includes a content changelog.
7. Post-launch: parent-approved words from the "ask a grown-up" queue are reviewed quarterly for inclusion in the next list version. Parent approvals never leave the device; inclusion in the global list happens only if a parent explicitly chooses "suggest this word" (doc 05 covers the consent and the fact that only the word itself is sent).

### 12.4 Proper nouns for Names and Places

Names: we seed from public name registries and include names across cultures, because a child named Oluwaseun must be able to write their own name. Names are matched at tier 2 in all bands (one edit), since spelling variants are common and legitimate (Sara, Sarah). A child's own profile nickname is always a valid Name answer for its first letter, even if not on the list.

Places: generic places (park, zoo, beach, school) are valid in Explorers and above as well as proper places. Countries and capitals come with picture hints (flags) for Explorers. We avoid contested names and territories in the kid lists by including only UN member states and widely recognized cities; the Navigators list may add more with **[KIDS]** review.

### 12.5 When a kid types something inappropriate

It will happen. A seven-year-old will type a bathroom word and giggle. Design:
- The word is checked locally against the allow-list first. Not on the list means not valid, which covers most cases with no special message.
- The word is additionally checked against the local sensitive list. If it matches, the field clears and the creature says "Let's try a different word" with no further reaction. No red, no lecture, no reward of a special animation that makes the behavior fun to repeat.
- Nothing is logged about the attempt beyond an on-device counter the parent can see ("3 words were skipped by the safety filter this week"). The words themselves are not stored.
- In pass-and-play, any typed text shown to another child (phrase categories, nicknames) passes the same filter before display.
- Nothing is ever transmitted. There is no server to transmit to.

> **[KIDS]** The rule is: boring response. The moment the app reacts strongly, the behavior is rewarded.

> **[DATA]** The sensitive list is the one block-list we maintain, and it is used only to pick the response, never to decide validity. Validity is allow-list only.

**DECISION:** Allow-lists per category per band; "ask a grown-up" queue for unknown words; boring response to inappropriate input; nothing transmitted.

---

## 13. Accessibility for kids with dyslexia or motor challenges

- **Font option:** a "friendlier letters" toggle in the parent area switches to a font with distinct b/d/p/q forms and generous spacing. We will offer OpenDyslexic as one option because some families specifically ask for it, but the evidence does not show it improves reading: Rello and Baeza-Yates' eye-tracking study found OpenDyslexic produced neither better nor worse readability than standard fonts and participants preferred Verdana and Helvetica (https://link.springer.com/article/10.1007/s11881-016-0127-1, summarized at https://www.dwrl.utexas.edu/?p=1193), and Wery and Diliberto found no improvement in reading rate or accuracy (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5629233/). Our default kid font therefore prioritizes what the evidence does support: sans serif, wide letter spacing, large size, roman not italic. Doc 04 specifies.
- **Letter spacing and size:** kid text is 20 points minimum body, 28 points for letter tiles, with increased tracking. Dynamic Type is supported up to the largest accessibility size without truncation in the core play screens.
- **Letter confusion support:** the custom Sprouts keyboard shows b and d with their creature pictures as a visual anchor (a bear facing right, a dog facing left) when the "friendlier letters" option is on.
- **Motor:** minimum 60-point targets everywhere, 72 for Sprouts keys, 12-point spacing; no drag required; no time pressure by default; Switch Control and Full Keyboard Access are verified in QA. Children have documented difficulty with drag gestures on touchscreens (Brown and Anthony, https://lisa-anthony.com/wp-content/uploads/2012/03/brown-and-anthony-chi2012eist.pdf).
- **Voice input:** considered. On-device speech recognition (Apple's `SFSpeechRecognizer` with on-device recognition) could let a non-typing child say "elephant". The privacy and compliance analysis is in doc 05; the design position is that voice input would be a parent-enabled option, on-device only, with no audio stored. **OPEN** pending the compliance review and a feasibility spike.
- **VoiceOver:** every element labeled with kid-friendly labels; the auto-read for Sprouts is built on the same accessibility announcements, so VoiceOver users get the same experience.
- **Color:** never the sole carrier of meaning; all states have a shape or icon.

> **[IOS]** On-device speech recognition requires the microphone permission prompt, which in a Kids Category app must sit behind a parental gate. It is feasible and fully local when `requiresOnDeviceRecognition` is set. The accuracy on young children's speech is the real unknown; we need a spike.

> **[KIDS]** Even if accuracy is mediocre, voice as a hint entry ("say the word, we show the first two letters") could be the right shape. Spike should test that framing too.

**DECISION:** Friendlier-letters option (including OpenDyslexic as a user choice with honest copy), 60/72-point targets, no drag required. Voice input is an OPEN item for a Phase 2 spike.

---

## 14. Teacher and classroom use

Scenario: a Year 2 teacher has six classroom iPads managed through Apple School Manager and wants a five-minute word warm-up. Shared iPad lets several students sign in to one device and keeps their data per user; students under 13 in schools use Managed Apple Accounts created by the school (https://www.jamf.com/blog/what-are-shared-ipads-in-education/).

What we build for this in v1 (cheaply): a "Classroom" preset in the parent area that sets the band, disables sounds by default, enables a projector-friendly "big letter" mode so one iPad can be mirrored to a screen, and allows up to 30 named profiles with a quick "clear all profiles" action for the end of the lesson. A printable one-page teacher guide lives on the Trust page (doc 05).

What we do not build in v1: a teacher dashboard, class rosters, any cloud sync, any integration with school systems. **OPEN:** whether a post-launch "Classroom edition" is worth a separate SKU, which would also have to consider FERPA and school procurement.

> **[JOBS]** Teachers are the best free distribution a kids app can have, and they want the thing to just work on a projected iPad. Big-letter mode is one afternoon of work and worth it.

**DECISION:** Classroom preset and big-letter mode in v1; nothing cloud-based.

---

## 15. Edge cases and team debates (27)

Each item records the situation, the discussion, and the outcome.

1. **Child types a valid word in the wrong category (Sprouts).** "Banana" under Animal. Outcome: tier 0 accepts into the Thing fallback with a note. **DECISION:** Sprouts only.
2. **Child's nickname is not on the Name list.** Outcome: a profile's nickname is always a valid Name for its first letter. **DECISION.**
3. **Child's nickname fails the safety filter.** A parent sets "Poopy" as a joke. Outcome: the filter applies to nicknames at creation, the parent (behind the gate) sees "That name will not be shown to other players" and can override for their own device only. **DECISION.**
4. **Two kids, same answer, different spellings.** Treated as duplicates after correction; both get 5 in Explorers. **DECISION.**
5. **Phonetic match returns two candidates.** Show both as pictures; child taps. If neither, the field stays and a hint is offered. **DECISION.**
6. **Phonetic match hits a blocked word.** The collision audit should prevent this; if it happens at runtime the blocked word is never shown and the response is the boring "Let's try a different word". **DECISION.**
7. **Should a tier 2 near-miss cost a point in Explorers?** **[GAME]** wanted a 1-point cost to reward careful spellers. **[KIDS]** argued that an 8-year-old with dyslexia would be systematically penalized for a disability. **DECISION:** no cost in Explorers; Navigators ask-to-confirm at 8 of 10.
8. **Child enters a plural or a verb form.** "Cats", "running". Outcome: lemmatize before matching; accept "cats" for Animal and show "cat"; verbs are not Things. **DECISION.**
9. **Multi-word answers.** "Polar bear", "New York". Outcome: allowed; the first letter of the first word counts, which matches classic rules. **DECISION.**
10. **Articles.** "The park", "a dog". Outcome: strip leading articles before matching, never count "T" for "the". **DECISION.**
11. **Child types the picture-cue example.** The B is shown with a bear; the child writes "bear". **[GAME]**: it is a valid animal; penalizing it teaches nothing. **[KIDS]**: but the hint said "a different animal". **DECISION:** accept it with a wink: "Bear! That was my example, you cheeky thing. Can you find another next time?" Full credit in Sprouts; in Explorers the cue is not shown by default.
12. **Timer runs out mid-word.** Grace completion: the current field may be finished. **DECISION** (inherited from App 1 engine).
13. **Sibling grabs the phone during pass-and-play.** Handoff screen hides answers; nothing to do beyond that. **DECISION:** no further mitigation.
14. **Child wants to be a different band than the parent set.** The child cannot change the band. A 10-year-old set to Sprouts will complain; the parent area shows a suggestion. **DECISION.**
15. **Parent sets Navigators for a 6-year-old.** Allowed; the parent knows their child. The app shows no warning. **DECISION.**
16. **The app is opened by a child under 5.** Must be harmless: no reading required to reach a round, nothing to buy, nothing to break. The first-run flow is parent-first (doc 04). **DECISION.**
17. **Word Chain: child repeats a word already used.** Sprouts: "We already had cat! Can you think of another?" and the turn continues. Explorers: lose a life. **DECISION.**
18. **Word Chain: last letter is a hard letter.** "Fox" ends in X. Outcome: the kid-safe engine checks whether the next letter has at least N candidates in the category; if not, the child's answer is still valid but the next player draws a "wildcard" and may start with any letter. Sprouts N is 8, Explorers 5, Navigators 0 (no wildcard). **DECISION.**
19. **Word Chain: the bot gets stuck.** Pip says "I cannot think of one! You win this one!" in Sprouts. Rook concedes with grace. **DECISION.**
20. **Child enters a real word that is not on the allow-list (a rare animal, "axolotl").** The field shows "I do not know that one yet! Ask a grown-up?" and the word goes to the parent queue; the parent can approve it on the device, after which it is valid for that profile. **DECISION.** OPEN: whether approved words should count retroactively for the round's score (**[GAME]** says yes if approved within the session).
21. **Custom categories (Navigators) with no allow-list.** Custom categories validate against the general kid-safe Thing list only. A custom category named something inappropriate by the child is filtered. **DECISION.**
22. **Autocorrect on the system keyboard changes the child's word.** Autocorrect and predictive text are disabled in all kid text fields so the app, not iOS, does the correcting and shows it. **DECISION.**
23. **Child uses an emoji.** Stripped before matching. **DECISION.**
24. **Dynamic Type at the largest accessibility size breaks the 4-category layout.** Layout switches to one category per screen with swipe, which is also the Sprouts default. **DECISION.**
25. **Reduce Motion is on.** Every celebration has a static alternative; the sleepy sun becomes a static sun with a changing expression. **DECISION.**
26. **A parent asks for a leaderboard among siblings.** **[JOBS]**: a per-device "Family board" of personal bests with no ranking would satisfy most parents. **[KIDS]**: ranking siblings creates a loser. **DECISION:** Family board shows each child's own bests, side by side, unranked, in the parent area only. OPEN: whether to show it to children at all.
27. **Should we ship a "spelling test" mode where correctness is scored strictly?** Several parents in early interviews asked. **[KIDS]**: this turns a game into homework and the stated pedagogy of invented spelling says not to. **[JOBS]**: it is also a different product. **DECISION:** No. Learning signals in the parent area cover the parent's need.

---

## 16. Decisions and open questions

**DECISIONS** (collected)
- Band matrix in section 2 is the configuration contract for `KidsRuleSet`.
- Timers off for Sprouts; sleepy sun as a soft pacing cue; stop rule off below Navigators.
- Validation tiers 0 to 3 as specified; corrections always shown; misspellings never echoed.
- Hints free below Navigators; "Give me one" after 20 seconds of inactivity in Sprouts.
- Letter creatures, sticker book, 12 badges; no currency, streaks or timed rewards.
- Allow-lists per category per band; "ask a grown-up" queue; boring response to inappropriate input.
- Pass-and-play and co-op in v1; nearby later; online never.
- Classroom preset and big-letter mode in v1.

**OPEN**
- Voice input spike (Phase 2) and its compliance review.
- Retroactive scoring for parent-approved words.
- Whether the Family board is visible to children.
- Whether a Classroom edition SKU is worth pursuing post-launch.
- Exact phonetic algorithm tuning for young children's spellings (Double Metaphone vs a custom grapheme-to-phoneme table built from common invented spellings).

---

## 17. Sources

- Reading Rockets, invented spelling and spelling development (Gentry's stages): https://www.readingrockets.org/topics/spelling-and-word-study/articles/invented-spelling-and-spelling-development
- Reading Rockets, typical reading development (Chall): https://www.readingrockets.org/reading-101/how-children-learn-read/typical-reading-development
- Rello and Baeza-Yates, "Good fonts for dyslexia" / "The effect of font type on screen readability by people with dyslexia": https://link.springer.com/article/10.1007/s11881-016-0127-1 (summary: https://www.dwrl.utexas.edu/?p=1193)
- Wery and Diliberto, "The effect of a specialized dyslexia font, OpenDyslexic, on reading rate and accuracy": https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5629233/
- Brown and Anthony, children's touch interactions: https://lisa-anthony.com/wp-content/uploads/2012/03/brown-and-anthony-chi2012eist.pdf; INIT lab Fitts' law for children: https://init.cise.ufl.edu/?p=3232
- Sesame Workshop tablet best practices for preschoolers: https://joanganzcooneycenter.org/?p=19607
- Sherwin and Nielsen, Children's UX (NN/g): https://www.nngroup.com/articles/childrens-websites-usability-issues/
- Apple, Kids apps and parental gates: https://developer.apple.com/app-store/kids-apps/
- Apple HIG Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Jamf, Shared iPad in education: https://www.jamf.com/blog/what-are-shared-ipads-in-education/
- ICO Children's Code (nudge techniques, standard 13): https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/age-appropriate-design-a-code-of-practice-for-online-services/
- FTC, Bringing Dark Patterns to Light: https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf
- WordNet license and data: https://wordnet.princeton.edu/ ; SCOWL: http://wordlist.aspell.net/ ; Wiktionary licensing (CC BY-SA): https://en.wiktionary.org/wiki/Wiktionary:Copyrights
