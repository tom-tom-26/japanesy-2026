# Website structure — `japan_holiday_updated.html`

**Read this before editing the site.** It exists so edits are cheap: you should rarely need to open the 81 KB generated HTML, and you should never hand-edit it.

## The one rule

> **`japan_holiday_updated.html` is generated output. Never edit it directly.**
> Edit the data or the template, then run:
> ```bash
> python scripts/gen_html.py
> ```

If you hand-edit the HTML, the next `gen_html.py` run silently overwrites you.

---

## Which file do I touch?

| I want to change… | Edit | Then |
|---|---|---|
| A venue, time, price, note, map pin | `scripts/data_kyoto.py` / `scripts/data_tokyo.py` | `gen_html.py` |
| A day's title / date / which day is open by default | same data files (`days[]`) | `gen_html.py` |
| The day-strip pill labels **or the Overview month-calendar labels** | same data files (`pills[]`) — calendar labels are derived from pills | `gen_html.py` |
| Section heading / subtitle / hint text | same data files (`k`, `sub`, `hint`) | `gen_html.py` |
| Hero, nav, Overview, Flights, footer, **CSS, JS** | `scripts/template_shell.html` (hand-written) | `gen_html.py` |
| How an event/day/pill/calendar renders into markup | `scripts/html_common.py` | `gen_html.py` |
| Non-itinerary calendar days (fly-out etc.) | `CONTEXT_DAYS` in `scripts/gen_html.py` | `gen_html.py` |

**Rule of thumb:** repeated content → data files. One-off page furniture → `template_shell.html`.

---

## Data schema (`data_kyoto.py` / `data_tokyo.py`)

```python
KYOTO = {
  "k":    "京都 · 4 days",       # small grey text beside the <h2>
  "sub":  "Grouped by neighbourhood…",
  "hint": "Tap a day to open it…",
  "pills": [ {"day":1, "num":"9", "lab":"Mon · Fushimi", "leave":False}, … ],
  "days":  [ {…day…}, … ],
}
```

### Day
| Key | Meaning |
|---|---|
| `day` | Day number within the city; links the pill ⇄ day card (`data-day`) |
| `date` | ISO `'2026-11-09'` — drives the **month calendar** and the "📍 Today" button (`data-date`) |
| `open` | `True` = expanded on load (only Day 1 should be) |
| `title_date` | e.g. `'Mon 9 Nov'` |
| `title_small` | the small subtitle in the day header |
| `events` | list of event dicts |

### Event — these 7 keys, nothing else
| Key | Req | Renders as |
|---|---|---|
| `time` | ✅ | Left column, e.g. `'12:30 pm'` |
| `dur` | ✅ | Small grey text under the time (`''` if none) |
| `place` | ✅ | Bold row title (the clickable summary) |
| `notes` | ✅ | Body text when expanded |
| `map` | ✅ | Google Maps **search query** → "Open in Google Maps" button + lazy-loaded embed |
| `extras` | — | `[["travel"|"food"|"bar", "📍 text"], …]` → coloured pills. Class must be one of those three (asserted). |
| `alt` | — | Green "Not up for it?" fallback box |

> ⚠️ **Values are HTML fragments, not plain text** — no escaping happens at render time. Write `&amp;`, `&rsquo;`, `<b>…</b>` yourself. A bare `&` will produce invalid HTML.

### `map` is a query, not a URL
Write `"map": "Fushimi Inari Taisha"`. The page script builds both the link and the embed from it. Same convention as `maps()` in `scripts/ics_common.py`, so **map queries and addresses can be copied verbatim between the `.ics` generators and the site** — reuse them instead of re-searching (cheapest source of already-verified location data).

---

## Overview month calendar

A real November-2026 grid on the Overview tab. Each trip date is a `<button class="mday trip" data-date=…>`; clicking it calls the **same `activateDay()`** the day-strip pills use, which switches to the right city tab, opens that day card and scrolls to it. No separate navigation concept, no duplicated state.

- Built by `render_month_calendar()` in `html_common.py`, spliced in at the `{{MONTH_CAL}}` marker.
- **Labels come from each city's `pills[].lab`**, with the weekday stripped (the column already shows it). So editing a pill updates the strip *and* the calendar.
- Grid layout uses `calendar.Calendar(firstweekday=6)` — Sunday-first, computed, not hardcoded.
- **12 Nov appears in both cities** (Kyoto day 4 → Tokyo day 1). It's labelled `Kyoto → Tokyo` and navigates to the **Kyoto** card (the morning), matching `querySelector`'s first-match behaviour in `jumpToToday()`.
- Non-itinerary days come from `CONTEXT_DAYS` in `gen_html.py` (greyed, not clickable). Everything else in the month renders dimmed.
- Today's date gets a gold ring automatically if viewed during the trip.

---

## Edit recipes

**Change a price/time** — grep the venue name in `data_*.py`, edit `time:`/`notes:`, regenerate. One-line diff.

**Add a stop:**
```python
{"map": "Venue Name Tokyo", "time": "3:00 pm", "dur": "1 hr",
 "place": "Venue Name / 日本語",
 "notes": "What it is, price, hours, why it's here.",
 "extras": [["food", "🍜 Lunch"]],
 "alt": "Backup if you're not up for it."},
```

**Add a whole day** — append a day dict to `days` **and** a matching pill to `pills` (same `day` number). The section, day strip, and month calendar all pick it up; no template edit.

**Retheme the whole site** — edit **`:root` in `template_shell.html` only**, then regenerate. See "Design system" below.

---

## Design system

The site is a **dark cinematic theme** and every component draws from the same tokens in `:root`, so the look stays consistent automatically and retheming is a handful of lines rather than a sweep through the markup.

| Token | Used for |
|---|---|
| `--paper` `--ink` `--slate` | page background, body text, secondary text |
| `--card` `--line` `--soft` | glass surfaces, borders, subtle fills |
| `--red` `--rose` `--violet` | primary accent (times, headings, active nav) |
| `--gold` `--green` `--blue` | Kyoto / "not up for it" alt boxes / travel + maps |
| `--grad` | the signature red→violet gradient (nav active, card heads, headings) |
| `--glass` `--shadow` | sticky nav backdrop, elevation |
| `--serif` `--sans` | display type (headings, day numbers) vs UI type |

**The token names are deliberately unchanged from the original light theme.** Some markup carries inline `style="color:var(--red)"`, so keeping the names means a retheme never touches the HTML — only the values in `:root`. Don't rename tokens; change what they point at.

Conventions worth preserving:
- **Kyoto = gold, Tokyo = rose/violet, travel & maps = blue, fallbacks = green.** Used by the month calendar, the day strips and the inline tag pills alike.
- Cards/nav/calendar are **glass**: `var(--card)` + `1px solid var(--line)` + `backdrop-filter: blur()`.
- Interactive things lift on hover (`translateY(-3px)`) and reset on `:active` so touch doesn't feel sticky.
- Decorative-only layers (`.bg-fx` orbs, the 日本 watermark, `#petals`, `.scroll-progress`) sit at negative `z-index`, are `aria-hidden`, and are safe to delete — nothing depends on them.
- Everything is disabled under `@media (prefers-reduced-motion: reduce)`.

---

## Verifying a change

```bash
python scripts/gen_html.py          # asserts no unresolved {{MARKERS}} remain
```
Then open the HTML and check the console is clean. Quick DOM checks in devtools:
```js
document.querySelectorAll('.ev[data-map]').length          // 49 event cards
document.querySelectorAll('.mcal .mday[data-date]').length // 13 clickable dates (9–21 Nov)
// every calendar date resolves to a real day card:
[...document.querySelectorAll('.mcal .mday[data-date]')]
  .filter(c=>!document.querySelector('.daycard[data-date="'+c.dataset.date+'"]'))
```
Generation is deterministic — running it twice produces an identical file, so a noisy `git diff` means you actually changed something.

---

## Gotchas

- **Two `2026-11-12` day cards exist** (Kyoto 4, Tokyo 1). `querySelector` finds Kyoto's first — intentional, don't "fix" it.
- `activateDay()` only closes sibling day cards **within the same section**, so a day left open in a hidden tab stays open. Harmless.
- The map embeds load `maps.google.com` iframes lazily on expand — the only external request the page makes. Everything else is inline and self-contained.
- **Don't rename the `:root` tokens** — inline `style="…var(--red)"` attributes in the markup depend on the current names.
- Weekday/date pairings for Nov 2026 are tabulated in `CLAUDE.md` — cross-check against it rather than re-deriving.
- `scripts/__pycache__/` is gitignored; don't commit it.

## Relationship to the other files

`Kyoto_Itinerary_Plan.md` / `Tokyo_Itinerary_Plan.md` remain the **source of truth for the itinerary**. The site data files and the `.ics` files are transcription targets. Per `CLAUDE.md`, a factual change must land in all of: the plan `.md`, the matching `_Sources.md`, the `.ics` generator, and `data_*.py`.
