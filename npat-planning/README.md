# Inkwell Planning Program

Planning documents for a family of iOS word games built from two paper-and-pencil classics: **Name Place Animal Thing** and **Word Chain** (last letter becomes the next first letter, within a category).

Start with [`00-TEAM-CHARTER.md`](00-TEAM-CHARTER.md). It explains the three products, the eight team voices that write and argue inside every document, and the rules the documents follow.

Names are working titles. App 1 is **Inkwell** pending trademark clearance (ranked fallbacks: Nib, Letterhead, Foolscap). App 2's working name is **Inkwell Kids**; its first choice for launch is **Inkling** pending a trademark search. Where documents disagree, [`00-DECISIONS-AND-OPEN-QUESTIONS.md`](00-DECISIONS-AND-OPEN-QUESTIONS.md) records the reconciled decision.

## Document map

### App 1: Inkwell (build first)
| File | Owner voice | What it covers |
|------|-------------|----------------|
| [`app1-inkwell/01-product-vision-and-brief.md`](app1-inkwell/01-product-vision-and-brief.md) | JOBS | Pitch, audience, first 60 seconds, kill list, metrics, naming, competitors, monetization |
| [`app1-inkwell/02-game-design-spec.md`](app1-inkwell/02-game-design-spec.md) | GAME | Formal rules for both games, modes, scoring, validation, bots, edge cases |
| [`app1-inkwell/03-phased-delivery-plan.md`](app1-inkwell/03-phased-delivery-plan.md) | ARCH | Phases 0 to 7, timeline, skunkworks track, risks, go/no-go |
| [`app1-inkwell/04-architecture-and-engineering.md`](app1-inkwell/04-architecture-and-engineering.md) | ARCH | Packages, engine, timers, persistence, content, multiplayer, build pipeline, ADRs |
| [`app1-inkwell/05-quality-release-and-app-store.md`](app1-inkwell/05-quality-release-and-app-store.md) | QA | Test pyramid, beta, App Review readiness, release trains, the "perfect app" checklist |
| [`app1-inkwell/06-platform-choice-and-alternatives.md`](app1-inkwell/06-platform-choice-and-alternatives.md) | ARCH | Native SwiftUI vs React Native vs Flutter vs KMP vs engines vs PWA, the "translate later" question |
| [`app1-inkwell/07-design-directions-and-aesthetics.md`](app1-inkwell/07-design-directions-and-aesthetics.md) | DESIGN | Principles, five visual directions, design system foundations, theming |
| [`app1-inkwell/08-ux-flows-and-screens.md`](app1-inkwell/08-ux-flows-and-screens.md) | DESIGN | Sitemap, first run, every screen, flows, answer-entry and chain-screen deep dives, microcopy |
| [`app1-inkwell/09-motion-sound-and-haptics.md`](app1-inkwell/09-motion-sound-and-haptics.md) | DESIGN | Motion principles, animation catalog, implementation stack bake-off, sound, haptics |
| [`app1-inkwell/10-phase0-kickoff-package.md`](app1-inkwell/10-phase0-kickoff-package.md) | ARCH | Day-one package: founder sign-off sheet, accounts and tooling setup, repo skeleton, W1 to W6 plan, first Friday demos, conventions, content and design bootstrap |

### App 2: Inkwell Kids (build second)
| File | Owner voice | What it covers |
|------|-------------|----------------|
| [`app2-inkwell-kids/01-vision-and-kid-design-principles.md`](app2-inkwell-kids/01-vision-and-kid-design-principles.md) | JOBS + KIDS | Why a separate app, age bands, kid principles, refusals, metrics, naming |
| [`app2-inkwell-kids/02-game-adaptations-and-age-bands.md`](app2-inkwell-kids/02-game-adaptations-and-age-bands.md) | GAME + KIDS | Per-band rules, hints, forgiving validation, progression, kid-safe content |
| [`app2-inkwell-kids/03-phased-plan-and-architecture-reuse.md`](app2-inkwell-kids/03-phased-plan-and-architecture-reuse.md) | ARCH + QA | Reuse map, phases, kid playtest protocol, go/no-go |
| [`app2-inkwell-kids/04-design-directions-kids.md`](app2-inkwell-kids/04-design-directions-kids.md) | DESIGN + KIDS | Four kid visual directions, motion rules, parent area, microcopy |
| [`app2-inkwell-kids/05-safety-privacy-compliance-and-parents.md`](app2-inkwell-kids/05-safety-privacy-compliance-and-parents.md) | KIDS + QA | COPPA, Kids Category, parental gate, data minimization, trust page |

### App 3: Multilingual (back burner)
| File | What it covers |
|------|----------------|
| [`app3-multilingual/short-story-plan.md`](app3-multilingual/short-story-plan.md) | Why "letter" breaks across scripts, language-pack sketch, three options, what to keep open in App 1 |

### Master reference
| File | What it covers |
|------|----------------|
| [`master-reference/INKWELL-COMPLETE-REFERENCE.md`](master-reference/INKWELL-COMPLETE-REFERENCE.md) | The whole game, software, architecture, design, and the team's sourced recommendations and creative contributions |

### Program-level
| File | What it covers |
|------|----------------|
| [`00-TEAM-CHARTER.md`](00-TEAM-CHARTER.md) | Products, personas, commentary format, document rules |
| [`00-DECISIONS-AND-OPEN-QUESTIONS.md`](00-DECISIONS-AND-OPEN-QUESTIONS.md) | Consolidated DECISION and OPEN lines across all documents, plus the cross-document review |
