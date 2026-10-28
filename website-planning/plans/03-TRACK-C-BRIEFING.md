# Track C — The Briefing

**Lineage:** none directly. Borrows the section-to-slide mapping both reference pages use and makes it literal.
**Signature idea:** the page is wrapped around an embedded slide deck. The deck slot is a **placeholder for now**; the page is designed so that when a real embed arrives (hosted deck, PDF, or a native HTML deck) it drops into the slot without touching anything else. The companion notes beside the deck follow the current slide.

**Why this is different from A and B:** A refuses to embed the deck; B replaces it with a model. C says the deck is the primary object and the page exists to annotate it. Low key means the deck is framed quietly, the page never competes with it, and the placeholder is a calm numbered frame, not a "coming soon" banner.

**Aesthetic in one line:** a reading room. Mid-grey ground, a single off-white deck frame, small mono captions, one slate-blue accent for the current slide marker.

---

## Phase 0 — Tokens and type

A third palette so the three tracks are visibly distinct.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--bg` | `#eceef0` | `#14171a` | page ground (a little darker than A, so the deck frame reads as the lit object) |
| `--frame` | `#fafafa` | `#1e2327` | the deck slot and note cards |
| `--fg` | `#1a1f24` | `#e6e9ec` | text |
| `--muted` | `#626a72` | `#98a1a9` | captions, slide numbers |
| `--line` | `#d4d8dc` | `#2c3338` | hairlines |
| `--accent` | `#3b5b7a` | `#8fb3d6` | current-slide marker, links |
| `--accent-soft` | `#e2eaf1` | `#1d2a36` | active note card ground |

Type: Inter Tight 500/600 for headings and labels, Inter 400/500 at 16px/1.6 for body, JetBrains Mono for slide numbers and figures. Tabular numerals.

Deck frame: 16:9, `--frame` ground, 1px `--line` border, radius 4px (the only radius on the page), no shadow.

**Done when:** token swap recolours the page; both themes pass contrast; the deck frame is the brightest surface in light and the lightest in dark.

---

## Phase 1 — Skeleton: deck slot plus notes rail

Order, top to bottom.

1. **Header.** Wordmark left, "Briefing · {round}" small-caps, three links right (Deck, Notes, Data room). Sticky, hairline.
2. **Opening.** One line of eyebrow (round, opened date), a one-line h1, a 32em lede. No buttons here; the deck is the call to action.
3. **The deck stage.** A two-column grid on wide screens: the deck slot (minmax 0, 2fr) at left, the **notes rail** (minmax 280px, 1fr) at right. Under the slot a mono status line: "Slide {n} of {N} · Deck v{version} · synced {date}" and prev / next text buttons. On narrow screens the rail moves below the slot and becomes a horizontally scrolled strip of cards.
4. **Below the fold**, in a single column: Figures strip (four actuals, as of date), The round (terms table), Team, Questions, Request the data room, Colophon.

**The deck slot** is a `<section id="deck">` with a single `<div class="slot" data-embed="none">`. It holds exactly one child, chosen by `ROOM.deck.embed.kind`:

| kind | child | when |
|---|---|---|
| `placeholder` | the numbered frame from Phase 3 | now |
| `iframe` | `<iframe src=ROOM.deck.embed.url allow="fullscreen">` | hosted deck (Pitch, Google Slides, Figma) |
| `pdf` | `<object type="application/pdf">` with a download fallback link | PDF export |
| `html` | an inline `<article class="slides">` with one `<section>` per slide | native deck, later |

Nothing else on the page knows which kind is in the slot. The slot emits one event, `slidechange {n}`, and listens for one, `goto {n}`.

**No-JS fallback:** the placeholder frame shows slide 1, the notes rail shows all notes stacked with their slide numbers as h3s, and prev / next are anchor links to `#note-{n}`. G1.

---

## Phase 2 — Components

**Deck frame.** 16:9 via `aspect-ratio`, `--frame` ground, hairline border. Keeps its ratio at every width; never crops.

**Status line.** Mono .74rem, `--muted`, slide number in `--fg`. Prev / next are text buttons with a thin underline on hover and nothing else; disabled at the ends.

**Notes rail.** One card per slide from `ROOM.notes[]` (`{ slide, title, body, links[] }`). Card: slide number in mono, title in Inter Tight, body at 15px. The current slide's card gets `--accent-soft` ground and a 2px `--accent` left rule. Cards are `<a>`s: clicking one sends `goto {n}` to the slot. The rail scrolls the active card into view with `scroll-margin`.

**Figures strip, terms table, team, questions, form.** As in Track A's Phase 2, restyled on this palette: initials avatars drop in favour of a hairline top rule per person; terms table labels are Inter Tight small caps.

**Done when:** every card, the status line and the slot agree on the current slide from both directions (card → slot, slot → card).

---

## Phase 3 — The signature: the placeholder that behaves like a deck

The placeholder must be good enough to send, because for a while it is the deck.

**3a. The numbered frame.** An inline SVG filling the slot: `--frame` ground, a hairline 12-column grid at 6% opacity, a large mono slide number centred ("04"), the slide's title from `ROOM.notes[n].title` beneath it in Inter Tight, and a bottom-left mono caption "Placeholder · deck v{version} slide {n} of {N}". It is calm and honest: it says what will be here, not "coming soon".

**3b. Full slide behaviour without a deck.** Prev / next, arrow keys (when the slot has focus), clicking a note card, and `#slide=n` in the URL all change the frame's number and title and move the rail. `history.replaceState` keeps the hash current, so "look at slide 9" is a link.

**3c. The swap contract.** `tools/embed-check.js` takes `ROOM.deck.embed` and verifies: kind is one of the four; for `iframe` the host is on an allowlist and the URL is https; for `pdf` the file exists; for `html` the number of `<section>`s equals `deck.slides`. Changing `kind` from `placeholder` to anything else is a one-line edit in `data.js` and nothing else moves. The notes rail and status line keep working because they only listen for `slidechange`.

For `iframe` embeds that cannot report their slide (most hosted decks), the status line and rail follow **the page's own counter** (prev / next and the rail still work and the embed is told via `postMessage` where supported); the frame is not scraped.

**Done when:** three outside readers can step through the placeholder, read the note for each slide, and say which slide they would ask about first. G2.

---

## Phase 4 — Interaction and motion

Motion budget: two things.

1. The active note card's ground and left rule change over 180ms.
2. The rail scrolls the active card into view with `scroll-behavior: smooth`.

Both off under `prefers-reduced-motion`. No slide transitions in the placeholder: the number simply changes.

Interactive elements: prev / next (buttons, keyboard), note cards (links), the slot (focusable, arrow keys), fullscreen text button (uses the Fullscreen API on the slot; hidden if unsupported), copy email, FAQ details, form with inline validation.

**Done when:** keyboard-only walk: Tab reaches the slot, arrows change slides, Tab moves on to the rail, Enter on a card changes slides, and a screen reader announces "Slide 4 of 16, Traction" from the status line's `aria-live`.

---

## Phase 5 — Responsive and theme QA

Breakpoints: 960px (rail moves under the slot as a horizontal strip), 640px (status line wraps to two lines, figures strip stacks).

Checklist:

- [ ] No horizontal page scroll at 375px; only the note strip and `.tablewrap` scroll sideways.
- [ ] The deck frame never exceeds the viewport height minus the header on a landscape phone.
- [ ] Gutter ≥ 16px; safe-area insets respected.
- [ ] Dark theme reviewed on its own: frame lighter than ground, accent lifted.
- [ ] `#slide=n` links land with the slot in view at that slide.
- [ ] `prefers-reduced-motion` disables both motions.
- [ ] Focus visible on the slot, buttons, cards, inputs and summaries.
- [ ] With `kind: iframe` pointed at a test deck, the frame keeps its ratio and the rail still works.
- [ ] Fonts `display=swap`; acceptable in system fonts.

**Done when:** the checklist passes on 375px portrait, 844px landscape and 1440px, in both themes. G3.

---

## Phase 6 — Wiring for production

- Notes, slide count, version and synced date all from `data.js`; CI fails if `notes.length !== deck.slides` or any `sections[].slide` is out of range.
- Embed swap: set `ROOM.deck.embed = { kind, url }`, run `node tools/embed-check.js`, done. Keep `placeholder` as the fallback kind if the embed fails to load (`iframe` `onerror` or a 5s timeout swaps the frame back in with a mono line "Deck unavailable · placeholder shown").
- Form POST to CRM or inbox; inline copy only.
- Data-room URL never in markup; gated behind the form or NDA flow.
- Page gated with a signed link before it leaves the first meeting; `noindex`. If the deck host supports it, the embed URL is itself signed and expiring.
- Analytics: slide reached (max n per visit), note cards opened, data-room requests. Nothing else.
- One HTML file, one `data.js`; opens from disk with the placeholder, and with a `pdf` embed if the PDF sits beside it.

**Done when:** one investor receives a signed link, steps through the placeholder with notes, and the same link shows the real deck the day the embed is switched on, with no other change. G4.

---

## What not to do (Track C)

- No slide thumbnails strip; the rail is notes, not pictures.
- No "coming soon", no spinner, no greyed-out skeleton. The placeholder is finished work.
- No autoplay, no transitions, no progress bars.
- No scraping or screenshotting the hosted deck to fake slide sync.
- No second accent; the current-slide marker is the only accent use above the fold.

## Risks

| Risk | Mitigation |
|---|---|
| Hosted deck embed cannot report its slide | Page's own counter drives the rail; documented in the status line as "notes follow your position". |
| Placeholder looks unfinished to an investor | It states version, slide title and count; outside-eyes test at G2 decides whether it ships. |
| Deck and notes drift | Notes keyed by slide number; CI checks count; deck owner updates both in one `data.js` edit. |
| Embed host blocks framing | `embed-check.js` tests `X-Frame-Options` / CSP at swap time; falls back to `pdf`. |
