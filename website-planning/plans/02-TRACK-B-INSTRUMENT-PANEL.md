# Track B — The Instrument Panel

**Lineage:** Frontline Investor Room and its direction sheet (dark showroom, amber brake-light accent, wide-track type).
**Signature idea:** the page is built around one honest, live model. Every number on the page is a reading from the same instrument, and the URL carries the instrument's settings, so an investor can send a colleague "the page at my assumptions".

**Why this is different from A and C:** A is a document and refuses live state. C is a deck. B is a panel: it exists so a reader can turn two dials and watch every section respond, then share that exact view. It is still low key: the dials are range inputs, the readings are mono numbers, and nothing glows.

**Aesthetic in one line:** a quiet showroom at night. Graphite bands, one amber light, hairlines, wide-track uppercase labels. Radius 2px, no shadows.

---

## Phase 0 — Tokens and type

Adopt the direction sheet's table verbatim (`../DIRECTION-frontline-investor-room.md`, Phase 0): `--bg`, `--band`, `--surface`, `--fg`, `--muted`, `--line`, `--line-strong`, `--accent` (`#e6a23c` dark / `#b8761c` light), `--accent-ink`, `--accent-soft`. Dark is primary; light is a second design, not an inversion.

Add two tokens the panel needs:

| Token | Dark | Light | Role |
|---|---|---|---|
| `--reading` | `#ece9e2` | `#17191b` | live model outputs (same as fg; a separate token so a reading can be dimmed while recomputing) |
| `--stale` | `#6b6a65` | `#9a9790` | outputs that no longer match the dials (only used for 120ms) |

Type: Archivo at `font-stretch: 125%` 500/600 for display, uppercase for h1/h2/labels; IBM Plex Sans 16.5px/1.6 for body; IBM Plex Mono for every digit with tabular numerals.

**Done when:** token swap recolours the page; both themes pass contrast (fg/bg ≥ 12:1, muted/bg ≥ 4.5:1, accent-ink/accent ≥ 7:1).

---

## Phase 1 — Skeleton and the model as the spine

Order, top to bottom, following the direction sheet's Phase 1 with one structural change: **the model sits second, not fourth**, and every later section reads from it.

1. Sticky header: chevron + wordmark, five uppercase links. Nav hides under 720px.
2. Hero: eyebrow, two-line uppercase h1, lede, button row, deck-sync caption, **the frontline gesture** (Phase 3a).
3. **The panel.** Two dials (new rooftops per quarter, revenue per rooftop per month) and five readings (ARR in 8 quarters, rooftops live, months of runway, gross margin, payback). Assumptions printed under it in mono. A "Share this view" button (Phase 3b).
4. KPI rail: five tiles in a 1px-gap grid. These are **actuals** and never move with the dials; the rail is labelled "Actuals · as of {date}" to make that explicit.
5. Section rail: sticky, slide-numbered, amber underline on the active section.
6. Sections, alternating plain and `.band`: Recon → Traction → Rooftops → Round → Team → Questions → Data room. Traction's chart gains a dotted "at your settings" projection line (Phase 3c).
7. Footer: two mono lines.

Spacing, container and header grid exactly as the direction sheet: 64px section padding, `1fr auto` header with hairline, 1140px container, gutter `max(16px, env(safe-area-inset-*))`.

**No-JS fallback:** the panel renders its default readings as static text with the dials disabled, and the projection line is absent. The page still reads. G1.

---

## Phase 2 — Components

Follow the direction sheet's Phase 2 spec for buttons, section headers, KPI tiles, chart frames, stage tiles, terms table, rooftop cards, team rules, FAQ and form. Additions for the panel:

**Dial.** `<input type=range>` with accent colour, a mono value at right of the label, and `aria-valuetext` giving the unit. Step sizes from `ROOM.model.inputs`. Keyboard: arrows step, shift-arrows step ×5.

**Reading.** Display 600 at 1.5rem, mono label beneath. On input, readings set `--stale` for 120ms then settle; under `prefers-reduced-motion` they just change.

**Assumption line.** One mono sentence built from `ROOM.model.assumptions`, never hand-typed, so it cannot drift from the code that computes the readings.

**Projection line.** In the Traction chart, a dotted `--fg` path from the last actual bar to the 8-quarter ARR reading. Its label reads "at your settings". It is the only chart element that moves.

**Share control.** A quiet button that copies the current URL (with the dial state in the hash) and says "Copied" for 1.5s.

**Done when:** the dials, readings, assumption line and projection line all derive from `ROOM.model` and a change to one assumption updates all four.

---

## Phase 3 — The signature: gesture, URL state, and a model you can audit

**3a. The frontline gesture.** One SVG, container width, 120px tall: twelve trailing months of days-to-front-line descending from 9.4 to 4.2 as a single amber 2px path with `vector-effect: non-scaling-stroke`, a dashed hairline at the current value, a hollow ring at the first point and a solid dot at the last. Mono caption bottom-right. No axes, no labels. It is a gesture, not a chart. Produced per the composition guide only as a last resort image; the plan is SVG.

**3b. URL as state.** Dial values are written to `location.hash` as `#r=140&p=560` on `input` (debounced 150ms) with `history.replaceState`, read on load, and clamped to each dial's range. A link with a hash opens at those settings, with the readings already computed, and the projection line already drawn. The hash never carries anything except dial values.

**3c. An auditable model.** The computation lives in one pure function `project(inputs, assumptions) → readings` in `data.js`, with a unit test file `tools/model.test.js` holding three worked examples whose outputs are pasted into the data room's finance model. A "How this is computed" `<details>` under the panel prints the function's assumptions and the three worked examples as a table. Nothing on the panel is a forecast; the heading says "Sensitivity".

**Done when:** three outside readers can open a shared link, state what the dials are set to, and explain where one reading comes from using only the page. G2.

---

## Phase 4 — Interaction and motion

Motion budget, per the direction sheet: three things move.

1. KPI count-up on load (1s, cubic ease-out).
2. Stage bar segment transition, 350ms.
3. Section rail underline following scroll (IntersectionObserver, rootMargin `-35% 0 -55% 0`).

The readings' 120ms stale dim is a colour change, not a motion, and is also disabled under `prefers-reduced-motion`.

Interactive elements: recon stage tabs (`role=tablist`, keyboard), dials, share button, copy email, FAQ details, form with inline validation and no submission until Phase 6.

**Done when:** the whole page is operable by keyboard; dial changes announce their new value to a screen reader via `aria-live="polite"` on the readings group.

---

## Phase 5 — Responsive and theme QA

Breakpoints from the direction sheet: 820px (two-column sections stack), 720px (top nav hides), 640px (stage labels truncate, KPI tiles to one column). Add: under 640px the panel's readings go to a 2-column grid and the dials stack.

Checklist (direction sheet Phase 5, plus):

- [ ] No horizontal page scroll at 375px.
- [ ] Gutter ≥ 16px; safe-area insets respected.
- [ ] Light theme reviewed on its own; amber darkens; accent-ink flips to white.
- [ ] Every chart label uses tokens, never hex.
- [ ] `prefers-reduced-motion`: count-up instant, bar transition off, stale dim off.
- [ ] Focus visible everywhere, including range inputs.
- [ ] Opening a hashed link on a phone lands with the panel in view and the dials set.
- [ ] Fonts `display=swap`; page acceptable in system fonts.

**Done when:** the checklist passes on 375px and 1440px in both themes. G3.

---

## Phase 6 — Wiring for production

Per the direction sheet's Phase 6, plus the panel:

- Every figure from `data.js`. The finance owner updates `ROOM.model.assumptions`, runs `node tools/model.test.js`, and the three worked examples must still match the data room.
- Deck-sync caption and `.slide-ref` tags from `ROOM.deck` and `ROOM.sections`; CI checks slide numbers against `deck.slides`.
- Form POST to CRM or inbox; inline copy, never a redirect.
- Data-room URL never in markup; gated behind the form or NDA flow.
- Page gated with a signed link before it leaves the first meeting; `noindex`.
- Analytics: section views, dial interactions (bucketed, not raw values), share-link copies, data-room requests. Nothing else.
- One HTML file, one `data.js`, no framework, no build step; opens from disk, hash state included.

**Done when:** a signed link with a hash opens for one investor at the intended settings, and the readings match the finance model's worked example. G4.

---

## What not to do (Track B)

Straight from the direction sheet: no stock photos, no gradients, no glassmorphism beyond the header blur, no rounded cards, no second accent, no emoji or decorative icons, no scroll reveals. Added for the panel: no "optimistic / base / pessimistic" presets (they invite the word forecast); no animated number tweening on dial changes; no chart that cannot be explained by the printed assumption line.

## Risks

| Risk | Mitigation |
|---|---|
| Readers treat the panel as a forecast | Heading "Sensitivity", assumptions always visible, actuals rail clearly separated and static. |
| Hash state shared with absurd settings | Clamp to dial ranges on load; show "settings adjusted to range" once in mono. |
| Model drifts from finance model | Worked examples in a test; CI fails on mismatch. |
| Dark page reads heavy in a bright room | Light theme is a full design and the theme follows the OS by default. |
