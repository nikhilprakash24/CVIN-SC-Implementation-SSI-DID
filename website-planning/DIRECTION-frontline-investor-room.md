# Frontline Investor Room — Build Direction Sheet

Source: https://claude.ai/artifact/PZf2SJxQ35pVrUsLJWVDwg (saved 2026-10-28)

Hand this to Claude Code (or any dev) alongside `dealer-investor-site.html`. The HTML is the reference build; this sheet is the intent behind it, phase by phase, so the production version keeps the same look as it gets wired to real data.

**Aesthetic in one line:** a quiet showroom at night. Graphite surfaces, one amber light, wide-track type, hairline rules. Nothing bounces, nothing glows, nothing is rounded more than 2px.

**Audience and job:** institutional investors who have already seen the deck. The page exists to answer the next five questions without a call. Every section is tagged with the slide it expands.

---

## Phase 0 — Tokens (do first, change nothing else until done)

Single source of truth in `:root`. Dark is the primary theme; light is a full second design, not an inversion.

| Token | Dark | Light | Role |
|---|---|---|---|
| `--bg` | `#0f1113` | `#f3f1ec` | page ground |
| `--band` | `#15181b` | `#ebe8e2` | alternating section bands |
| `--surface` | `#1b1f23` | `#ffffff` | cards, chart frames, forms |
| `--fg` | `#ece9e2` | `#17191b` | text (warm off-white, never pure white) |
| `--muted` | `#9a9790` | `#6b6a65` | secondary text, axis labels |
| `--line` | `#2b3035` | `#d8d4cc` | hairlines |
| `--line-strong` | `#3d434a` | `#bfbab0` | emphasized rules, inactive bars |
| `--accent` | `#e6a23c` | `#b8761c` | the one amber. Brake-light logic: used sparingly, always meaningful |
| `--accent-ink` | `#1a1206` | `#ffffff` | text on accent |
| `--accent-soft` | `#2a2113` | `#f3e7d2` | accent tint for selected states |

Rules:

- No component may use a literal color. Everything reads a token.
- Neutrals carry a slight warm bias (toward the amber). Never pure grey.
- `color-scheme: dark` on root; light blocks set `color-scheme: light`. Three-state theme: bare root, `prefers-color-scheme`, and `[data-theme]` override.
- Radius: 2px max. Shadows: none, except `inset 0 2px 0 var(--accent)` on selected stage tiles.

Type stack (Google Fonts only):

- **Display** — Archivo, `font-stretch: 125%`, weights 500/600, uppercase for h1/h2/labels, letter-spacing −0.01em on headings, +0.14–0.18em on small caps labels.
- **Body** — IBM Plex Sans 400/500, 16.5px, line-height 1.6, measure ≤ 64ch.
- **Data** — IBM Plex Mono 400/500, `font-variant-numeric: tabular-nums` everywhere digits align.

Scale: h1 `clamp(2rem, 5.2vw, 3.6rem)`, h2 `clamp(1.3rem, 2.4vw, 1.7rem)`, h3 `.95rem`, eyebrow `.68rem`, mono captions `.70–.78rem`.

**Done when:** a token swap recolors the whole page and both themes pass contrast (fg on bg ≥ 12:1, muted on bg ≥ 4.5:1, accent-ink on accent ≥ 7:1).

---

## Phase 1 — Skeleton and rhythm

Structure, top to bottom. Keep this order; it mirrors the deck.

1. Sticky header: wordmark (chevron glyph + "FRONTLINE" wide-track) left, five uppercase nav links right. Blur backdrop, hairline bottom border. Nav hides under 720px.
2. Hero: eyebrow → h1 (two lines, uppercase) → lede (muted, 36em) → button row + deck-sync caption → **the frontline chart** (see Phase 3).
3. KPI rail: five tiles in a 1px-gap grid where the gap IS the border (`background: var(--line)` on the grid, tiles paint `--bg`). Big display number, mono label, amber delta line.
4. Section rail: sticky secondary nav with slide numbers, horizontal-scroll on mobile, amber underline on the active section.
5. Sections, alternating plain and `.band`: Recon → Traction → Model → Rooftops → Round → Team → Questions → Data room.
6. Footer: two mono lines, confidentiality and disclaimer.

Spacing system: sections `padding-block: 64px`; section header is `grid: 1fr auto`, hairline below (`--line-strong`), 14px gap; internal stacks use `gap`, never per-element margins.

Container: 1140px max, side gutter `max(16px, env(safe-area-inset-*))`, set once on `.wrap`; bands get their own inner `.wrap`.

**Done when:** page reads correctly with all JS disabled and all images/SVGs blank.

---

## Phase 2 — Components (style spec)

**Buttons.** Primary: amber fill, `--accent-ink` text, 13×20 padding, 2px radius, uppercase .7rem wide-track with .14em tracking. Quiet: transparent, `--fg` text, `--line-strong` border. No hover color shift; hover = underline-free opacity .9. Focus ring: 2px accent, 3px offset.

**Section header.** h2 uppercase left, `Expands slide NN` mono right with the number in amber. The hairline under it is the strongest rule on the page.

**KPI tile.** Display 600 at 1.9rem, unit as small muted suffix inside the number, mono uppercase label, amber mono delta. Numbers count up on load (1s, cubic ease-out); respect `prefers-reduced-motion` by rendering final value immediately.

**Chart frame.** `--surface` fill, `--line` border, 20px padding, legend in mono .72rem with 14×3px swatches (bars, not dots — reads as instrument markings).

**Stage tiles (recon).** Five equal columns, 4px gap. Each: mono day count big, uppercase micro-label, `--surface` fill. Selected: amber border + inset amber top rule. Below them a 10px segmented bar whose segment widths are proportional to days; selected segment turns amber. Below that a note panel with h3 / paragraph / mono "was X, now Y" line.

**Terms table.** No vertical rules. Mono uppercase row labels at .72rem muted, 40% width. Values in mono where numeric. Hairlines only.

**Rooftop cards.** Same 1px-gap grid as KPIs. Pipeline card is dashed-border and transparent to read as "not yet."

**Team.** Four columns, 2px top rule per person; founders get an amber rule. No avatars, no photos; the rule is the hierarchy.

**FAQ.** Native `details`. Hairline-separated, `+` / `–` in amber mono at the right.

**Form.** Inputs on `--bg` inside a `--surface` card, 2px radius, mono uppercase labels. Validation message inline, never a dialog. Email shown as selectable mono text with a Copy button beside it.

---

## Phase 3 — The one drawn moment

The hero "frontline" line is the page's signature. One SVG, full container width, 120px tall:

- 12 points, trailing-12-month days-to-front-line, descending from 9.4 to 4.2.
- Single amber 2px path, `vector-effect: non-scaling-stroke` so it stays crisp under `preserveAspectRatio="none"`.
- Dashed hairline at the current value (4.2) across the full width.
- Hollow ring at the first point, solid amber dot at the last.
- Mono caption bottom-right. No axis, no gridlines, no labels. It is a gesture, not a chart; the real chart lives in Traction.

Every other chart IS to scale: one shared y-scale per chart, ticks that land on real values, labels inside the viewBox, axis text in `--muted`, value callouts in `--fg`, mono.

---

## Phase 4 — Interaction and motion

Motion budget: three things move, nothing else.

1. KPI count-up on load.
2. Stage bar segment fill transition, 350ms.
3. Section rail underline following scroll (IntersectionObserver, rootMargin `-35% 0 -55% 0`).

No parallax, no fade-in-on-scroll, no hover lift, no gradient animation. All content visible at rest.

Interactive elements:

- Recon stage tabs: `role=tablist`, keyboard operable, aria-selected drives styling.
- Scenario model: two range inputs → three outputs. Compute inline in JS; the formula and assumptions are printed under the outputs in mono. Keep the model honest: assumptions are the real ones from the finance model, not placeholders.
- Section rail: anchors with `scroll-margin-top: 90px`.
- Copy button: clipboard API inside the click handler, fall back to selecting the text.
- Form: `preventDefault`, inline validation, success line in amber. No real submission in the template; wire to CRM in Phase 6.

---

## Phase 5 — Responsive and theme QA

Breakpoints: 820px (two-column sections stack), 720px (top nav hides, rail takes over), 640px (stage tile labels truncate with ellipsis, KPI tiles go to one column).

Checklist:

- [ ] No horizontal page scroll at 375px. Only `.tablewrap` and charts may scroll sideways.
- [ ] Side gutter never below 16px; safe-area insets respected on notched phones.
- [ ] Light theme reviewed on its own: amber darkens to `#b8761c` so it still reads on cream; `--accent-ink` flips to white.
- [ ] Every chart label readable in both themes (all chart text uses tokens, never hex).
- [ ] `prefers-reduced-motion`: count-ups render instantly, bar transition off.
- [ ] Focus visible on every button, link, tab, input, summary.
- [ ] Fonts loaded with `display=swap` and real fallback stacks; page is acceptable in system fonts.

---

## Phase 6 — Wiring for production

- Replace every figure with values from the finance model. Figures live in one JS object at the top of the script so the deck owner can update them without touching markup.
- Deck sync caption pulls version and date from the same object. Slide numbers in `.slide-ref` must match the current deck; add a one-line check in CI if the deck lives in the repo.
- Form POST → CRM or inbox endpoint; keep inline success/failure copy, never a redirect.
- Data-room link gated behind the form or an NDA flow; never expose the room URL in markup.
- Gate the page itself (password or signed link) before sharing beyond the first meeting.
- Analytics: section-view events from the same IntersectionObserver, scenario-slider interactions, data-room requests. Nothing else.
- Keep the whole thing one HTML file plus one JS data object. No framework, no build step; it should still open from disk.

---

## What not to do

- No stock photos of cars, lots, or handshakes. The page is about the operation, not the product shots.
- No gradients, no glassmorphism beyond the header blur, no rounded cards.
- No second accent color. If something needs emphasis, use the amber or use weight.
- No emoji, no icons as decoration. The chevron in the wordmark is the only glyph.
- No scroll-triggered reveals. Investors skim; everything must be there on first paint.
