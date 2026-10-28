# Investor Room — Three Parallel Tracks

Three builds run side by side from the same source material (the Northwind and Frontline reference pages, the Frontline direction sheet, and the image-composition process guide). They share one data contract and one set of "low key" rules, and nothing else. Each track is a different answer to the same brief, so the end of Phase 3 is a real choice, not a merge.

| Track | Working name | Lineage | One-line idea | Plan |
|---|---|---|---|---|
| A | **The Ledger** | Northwind (light, editorial) | A page that reads like an annual report and prints like one. No JavaScript required. | `01-TRACK-A-LEDGER.md` |
| B | **The Instrument Panel** | Frontline (dark, showroom) | A page built around one live model; the URL is the state. | `02-TRACK-B-INSTRUMENT-PANEL.md` |
| C | **The Briefing** | New | A page wrapped around an embedded slide deck. Deck is a placeholder slot for now; the page is built around the slot. | `03-TRACK-C-BRIEFING.md` |

## What every track must obey ("low key")

1. **No splash.** No hero video, no stock imagery, no logos wall, no gradients, no scroll-triggered reveals. Everything visible on first paint.
2. **Quiet by default.** One accent colour per track. At most three things move on the page, and `prefers-reduced-motion` switches them off.
3. **Private by default.** `noindex, nofollow`, no social cards, no sitemap entry. Signed or password-gated link before anyone outside the first meeting sees it. Data-room URL never in markup.
4. **One file, no build.** Each track ships as a single `index.html` plus one `data.js` object. Opens from disk. Fonts from Google Fonts only, with real fallback stacks.
5. **Nothing is a forecast.** Every modelled number sits next to its assumptions and a disclaimer. Figures carry an as-of date.
6. **Minimal telemetry.** Section views, model interactions, data-room requests. Nothing else, and only after gating.

## Shared data contract (`data.js`)

All three tracks consume the same object so figures are entered once:

```js
window.ROOM = {
  company: { name, stage, round, openedOn, asOf },
  deck:    { version, slides, syncedOn, embedUrl /* C only, null for now */ },
  kpis:    [ { label, value, unit, delta, note } ],
  series:  { arrByQuarter: [[label, value]], cohorts: [...], segments: [...] },
  model:   { inputs: [{ id, label, min, max, step, default, unit }], assumptions: {...} },
  funds:   [ { label, pct } ],
  terms:   [ [label, value] ],
  team:    [ { name, role, bio, lead: bool, open: bool } ],
  faq:     [ { q, a } ],
  sections:[ { id, title, slide } ],
  contact: { email }
}
```

Slide numbers live in `sections[].slide` and nowhere else. Track C uses them to drive the deck slot; A and B use them for the "Expands slide NN" tags.

## Shared asset pipeline (from the image-composition guide)

The direction sheet bans stock photos. Where a track needs an image at all, it is produced with the multi-image composition loop in `../multi-image-composition-process-guide.md`, adapted from game sprites to brand pieces:

- **Reference library:** wordmark on plain ground, one palette swatch sheet, one "style" image per track (a tonal reference, not content).
- **Character sheet** becomes a **mark sheet**: the wordmark and chevron in 4 to 6 treatments on one plain sheet, the single fixed input for everything after.
- **Test scene** becomes the hero band at 1140×120: compose, shrink to phone, check in greyscale, reject anything that reads as decoration.
- Log every keeper: inputs, prompt, tool, model version, date, in `assets/LOG.md`.

Track A plans for zero images. Track B plans for one (the frontline gesture, drawn as SVG, image only as a fallback). Track C plans for the deck placeholder frame and nothing else.

## Cadence

Phases are numbered 0 to 6 in every plan and aligned so the three tracks can be reviewed together at the same gates:

| Gate | After phase | Review question |
|---|---|---|
| G1 | 1 | Does it read with JS off and SVGs blank? |
| G2 | 3 | Is the signature idea of the track working, or is it a gimmick? |
| G3 | 5 | Does it pass the QA checklist on a 375px phone in both themes? |
| G4 | 6 | Gated, wired, and ready to send to one investor? |

At G2 the three are shown side by side to three outside people with no preference stated, as the composition guide prescribes for style shortlists.
