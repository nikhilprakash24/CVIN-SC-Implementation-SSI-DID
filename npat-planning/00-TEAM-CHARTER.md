# Inkwell Program: Team Charter and How to Read These Documents

**Document status:** Draft v0.1, 2026-10-04, owner: Program (all personas)

**Read this if...** you are opening this folder for the first time. It explains what the program is, who the "team" voices are, how commentary is formatted, and the rules every document follows.

## 1. What this program is

Three products, planned in order of build priority:

| # | Product | Codename | Status of plan | Folder |
|---|---------|----------|----------------|--------|
| 1 | Name Place Animal Thing + Word Chain, one iOS app for teens and adults | **Inkwell** | Full plan, build first | `app1-inkwell/` |
| 2 | Kid-focused edition, separate app, kid vibe, Kids Category compliant | **Inkwell Kids** | Full plan, build second | `app2-inkwell-kids/` |
| 3 | Multilingual extension (other scripts and letter semantics) | **Inkwell Worldwide** | Short story plan only, back burner | `app3-multilingual/` |

Plus one standalone long-form document that explains the whole game, the software, the architecture, and the team's recommendations and creative contributions with sourced examples: `master-reference/INKWELL-COMPLETE-REFERENCE.md`.

Codenames are placeholders. Naming options and a recommendation live in `app1-inkwell/01-product-vision-and-brief.md` and `app2-inkwell-kids/01-vision-and-kid-design-principles.md`.

## 2. The founder's constraints, as given

- iOS is the target. The founder has a MacBook and a paid Apple Developer account. Development may happen in any environment with a translation step, so platform choice is evaluated honestly, not assumed.
- "It's not a hard app, so it needs to be perfect." Scope is small on purpose. Quality bar is the Apple Design Award shortlist, not "good enough".
- Aesthetics, animation and vibe are the top priority. Every design choice is presented as options or parallel passes, not a single answer.
- App 1 ships first. App 2 is a separate app, not a mode. App 3 stays short and may fold into App 1 later.
- This is intended to be the team's first clean, top-to-bottom shipped product.

## 3. The team

Every document is written in the voices of eight personas. They disagree on purpose. Where they disagree, the document shows the debate and records the outcome.

| Tag | Persona | Role | What they fight for |
|-----|---------|------|---------------------|
| **[JOBS]** | Theo Marr | Product Lead | Focus, taste, saying no, shipping, the first 60 seconds, "the feel". Protects a small skunkworks track for exploration. |
| **[ARCH]** | Priya Raman | Principal Architect | Modular Swift packages, deterministic engine, offline-first, testability, infrastructure cost. |
| **[IOS]** | Marcus Oyelaran | Lead iOS Engineer | SwiftUI and UIKit reality, animation implementation, performance, accessibility APIs, Game Center, StoreKit 2, App Review. |
| **[DESIGN]** | Sofia Lindqvist | Design Director | Visual and interaction design, typography, color, motion, design systems, HIG mastery. |
| **[GAME]** | Kenji Watanabe | Game Designer | Rules, balance, scoring, fun, feedback loops, party dynamics, anti-cheese. |
| **[KIDS]** | Dr. Amara Nwosu | Child UX and Learning Specialist | Developmental fit, literacy, kid safety, COPPA and Kids Category, parent UX. |
| **[QA]** | Lena Fischer | Quality and Release Lead | Test strategy, device matrix, release trains, App Review checklists, crash budgets. |
| **[DATA]** | Omar Haddad | Content and Dictionary Engineer | Word lists, validation, categories, fuzzy matching, filtering, data licensing. |

## 4. How commentary is formatted

Commentary appears as quoted blocks attributed to a persona:

> **[JOBS]** This screen has four buttons. It needs one.
>
> **[ARCH]** Agreed in principle. The trade-off is that house rules then live one level deeper.

Outcomes are recorded on their own lines:

- **DECISION:** a choice the team has made. It can be revisited, but only by writing a new DECISION line and the reason.
- **OPEN:** an unresolved question, with who owns resolving it and by which phase.
- **PARALLEL PASS:** an option that lost the main decision but is kept alive as a time-boxed exploration.

## 5. Rules every document follows

1. Options before answers. Any real design or technical choice shows 2 to 4 options in a comparison table, then a recommendation.
2. Sources for external claims. Apple guidance, laws, licenses, competitor facts and design references carry URLs. Where an exact URL could not be verified, the document says so and points at the official root.
3. Estimates assume a team of 1 to 2 engineers plus 1 designer plus a part-time founder, in engineer-weeks.
4. Every phase has entry criteria, exit criteria and a Friday demo. No phase exits on slides.
5. Accessibility is scoped in from the start: Reduce Motion alternatives, Dynamic Type, VoiceOver, contrast, haptics as an addition and never the only signal.
6. No code beyond tiny illustrative snippets. These are planning documents.

## 6. Reading order

For a 30-minute read: `README.md`, then `app1-inkwell/01-product-vision-and-brief.md`, then `app1-inkwell/03-phased-delivery-plan.md`.

For a half-day read: all of `app1-inkwell/` in numeric order, then `master-reference/`.

For the full picture: everything, with `app2-inkwell-kids/` after App 1 and `app3-multilingual/` last.
