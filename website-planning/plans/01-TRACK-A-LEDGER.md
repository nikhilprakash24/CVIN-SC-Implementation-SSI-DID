# Track A — The Ledger

**Lineage:** Northwind Investor Room (light, editorial, single column).
**Signature idea:** the page is a document, not an app. It reads like a well-set annual report, prints to a clean PDF from the browser's print dialog, and needs no JavaScript to do its job. JavaScript, where present, only adds convenience it would be rude to insist on.

**Why this is different from B and C:** B is built around a live model and treats the URL as state. C is built around a deck. A refuses both: there is no deck on the page (only references to it), and the model is a printed sensitivity table rather than sliders. If an investor forwards A as a PDF, nothing is lost.

**Aesthetic in one line:** a good quarterly letter. Warm paper, serif body, one teal accent used as a pencil mark, hairlines, generous measure.

---

## Phase 0 — Tokens and type

Start from the Northwind `:root` and tighten it.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--bg` | `#f5f7f8` | `#111619` | page ground |
| `--surface` | `#ffffff` | `#181f24` | tables, notes |
| `--fg` | `#16202a` | `#e8ecef` | text |
| `--muted` | `#5b6670` | `#9aa5ad` | captions, slide tags |
| `--line` | `#d9dfe3` | `#2a333a` | hairlines |
| `--accent` | `#1f6f6b` | `#5fb3ad` | the one teal: links, the "pencil" marks, current-quarter bar |
| `--accent-soft` | `#e3efee` | `#1b2f2e` | selected index item, margin notes ground |
| `--warn` | `#b4772a` | `#d9a054` | used once: the "not a forecast" note |

Type: Source Serif 4 for body (17px, 1.6, measure 62ch), Sora for headings and labels, JetBrains Mono for every digit. Tabular numerals everywhere digits align.

Print tokens: a `@media print` block pins light values as literals, hides the header, index, buttons and form, and sets `@page { margin: 18mm }` with running section titles via `h2 { break-before: page }` for sections 2 onward.

**Done when:** a token swap recolours the whole page; light and dark both pass contrast (fg/bg ≥ 12:1, muted/bg ≥ 4.5:1); Print Preview shows a clean 6 to 8 page document with no cut tables.

---

## Phase 1 — Skeleton that works with JS off

Order, top to bottom. It mirrors the deck, but never embeds it.

1. **Masthead.** Company wordmark left, "Investor room · Series A" small-caps under it. Four text links right. Sticky with a blur, hairline under. Hides nothing on mobile; the links wrap.
2. **Opening.** Eyebrow (round and opening date), a two-line serif h1, a 34em lede. Two text-button links: "Round terms" and "Request the data room". A one-line deck status: version, slide count, synced date (read from `ROOM.deck`).
3. **Figures strip.** Four numbers in a hairline-ruled row. Mono. No count-up by default (see Phase 4).
4. **Two-column body** on wide screens: a 200px sticky index at left, a single column of sections at right. On narrow screens the index becomes a row of pill links above the sections.
5. **Sections** in this order: Traction, Model, Use of funds, The round, Team, Questions we get asked, Request the data room. Every section header carries "Expands slide NN" from `ROOM.sections`.
6. **Colophon.** Confidentiality line, as-of date, disclaimer, document version.

Every tab panel, every disclosure and every chart has a no-JS fallback: tabs become stacked subsections with h3s, disclosures are native `<details>`, charts have a sibling `<table class="data">` that is visually hidden only when the SVG has rendered.

**Done when:** with JS disabled and SVG elements blank, the page reads top to bottom and prints correctly. G1.

---

## Phase 2 — Components

**Margin notes (the Ledger's own device).** Any paragraph may carry `<aside class="note">`. On wide screens it sits in the left gutter under the index, aligned to the paragraph, in Sora .78rem on `--accent-soft`. On narrow screens it renders inline after the paragraph with a teal left rule. This is where "why" lives: why NRR is measured at month 12, why the municipal segment is slow. Nothing about the business is hidden in a tooltip.

**Figures strip.** Mono 1.7rem value, Sora label beneath, hairline right rules, last cell has none. Each cell is an `<a>` to its section.

**Data tables.** No vertical rules, `th` in Sora .8rem muted at 38% width, numeric cells right-aligned in mono. Wrapped in `.tablewrap` for sideways scroll only when needed.

**Tabs, if JS is present.** `role=tablist`, arrow-key navigable, `aria-selected` drives styling. Without JS the three panels stack with h3 headings.

**Sensitivity table instead of sliders.** The Model section is a 5×5 grid: rows are new fleets per quarter (10 to 50), columns are price per vehicle ($30 to $46). Each cell holds ARR in 8 quarters; cells past 24 months of runway get a `--warn` dot. The grid is computed once at build time by `tools/sensitivity.js` and pasted as static HTML, so the printed page carries the same table. Assumptions are printed under it in Sora .78rem.

**Team.** Initials in a teal-soft circle, name, role, two-sentence bio. Open roles use an em-dash avatar and say what the round funds.

**Questions.** Native `<details>`, hairline separated, + / – in mono at right. `open` on the first one.

**Request form.** Four fields, inline validation copy, no dialog. Email beside it as selectable mono text with a Copy button that falls back to selecting the text.

**Done when:** every component has a print rendering and a no-JS rendering, checked by toggling each.

---

## Phase 3 — The signature: print and the changelog

Two things make the Ledger a ledger.

**3a. Print as a first-class output.** The "Download PDF" link is `window.print()` with a `beforeprint` handler that opens every `<details>`, shows all tab panels stacked, and expands the sensitivity grid. The print stylesheet sets the masthead as a running header (`position: running()` where supported, static otherwise), numbers pages in the footer, and keeps each terms table on one page. Target: a 7-page A4/Letter PDF whose page 1 is the opening and figures, pages 2 to 6 are the sections, page 7 is the colophon with the as-of date.

**3b. "What changed since v{n-1}".** A `<details>` block under the deck status lists, per section, what moved between deck versions, generated from a `ROOM.changes` array (`{ section, was, now, on }`). Investors who have seen the deck read this first; it is the one piece of content B and C do not have. Rendered as a plain two-column list: section at left, "was → now, date" at right in mono.

**Done when:** the printed PDF is shown to one person who has not seen the web page, and they can answer the five FAQ questions from the paper alone. G2.

---

## Phase 4 — Interaction and motion

Motion budget: two things, both optional.

1. Index highlight follows scroll (IntersectionObserver, rootMargin `-30% 0 -60% 0`).
2. Figures count-up on load, 900ms, cubic ease-out, off under `prefers-reduced-motion`, and off entirely if the page is opened from a `?print=1` link.

No hover lifts, no fades, no parallax. Links underline on hover and nothing else.

Interactive elements: tabs (keyboard), details, copy button, form validation. The form `POST`s to `ROOM.contact.endpoint` with `fetch` when JS is present and submits normally otherwise; both paths land on the same inline success line.

**Done when:** a keyboard-only walk through the page reaches every control in reading order with a visible focus ring.

---

## Phase 5 — Responsive, theme and print QA

Breakpoints: 860px (index moves above content), 640px (figures strip stacks, metrics lose right rules).

Checklist:

- [ ] No horizontal page scroll at 375px; only `.tablewrap` scrolls sideways.
- [ ] Gutter never under 16px; safe-area insets respected.
- [ ] Dark theme reviewed on its own, not as an inversion: teal lifts to `#5fb3ad`, surfaces separate from ground.
- [ ] Margin notes readable at both widths and in print (in print they become footnotes with superscript numbers).
- [ ] Print: no orphaned headings, no split tables, page numbers present, links printed as footnote URLs.
- [ ] `prefers-reduced-motion` disables both motions.
- [ ] Focus visible on every control.
- [ ] System-font fallback acceptable.

**Done when:** the checklist passes on a 375px phone, a 1440px laptop, and a printed PDF. G3.

---

## Phase 6 — Wiring for production

- All figures from `data.js`; nothing numeric in markup. The sensitivity grid regenerates with `node tools/sensitivity.js > sections/model.html` and a CI line diffs it against the committed copy.
- Deck status, slide tags and the changelog all read `ROOM.deck` and `ROOM.changes`; a CI check fails if any `sections[].slide` exceeds `deck.slides`.
- Form endpoint wired to inbox or CRM; success and failure copy stay inline.
- Data-room link gated behind the form or an NDA flow; room URL never in markup.
- Page gated with a signed link (HMAC of recipient + expiry in the query string, checked by the host) before it leaves the first meeting. Add `noindex`.
- Analytics: section-view events from the same observer, PDF downloads, data-room requests. Nothing else.
- One `index.html`, one `data.js`, one `print.css` inlined at build. Opens from disk.

**Done when:** one investor receives a signed link and a PDF, and both carry the same figures and the same as-of date. G4.

---

## What not to do (Track A)

- No sliders, no charts that need JS to exist, no embedded deck.
- No second accent. Emphasis is weight or a margin note.
- No icons. The only glyphs are + / – on disclosures.
- No modal anything.
- Never say "forecast". The word on the page is "sensitivity".

## Risks

| Risk | Mitigation |
|---|---|
| Print output differs by browser | Target Chromium for the official PDF; test Safari and Firefox for acceptable, not identical. |
| Margin notes crowd the index on 860–1000px | Notes collapse inline below 1000px, not 860px. |
| Changelog becomes a leak of internal churn | `ROOM.changes` is curated by the deck owner; only entries with `public: true` render. |
