# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Trip-planning content for a Japan holiday (Kyoto & Tokyo, 8–21 November 2026, travellers: Mandeep, Tom, Jai). There is no build system, package manager, test suite, or app to run — everything here is static content: a self-contained itinerary webpage, planning docs, and a spreadsheet. Treat every task as document/content editing, not software engineering. 

The `README.md` states the operating rule for this repo: **"NO SLOP"** — every claim (opening hours, prices, transit times, restaurant/bar recommendations) must be real, verifiable, current and authentic. Do not invent venues, prices, or logistics. Recommend resturants that japanese locals would frequent

## File map

- `japan_holiday_updated.html` — the current, canonical single-page itinerary site (tabbed: Overview / Flights / Kyoto / Tokyo). Self-contained: inline `<style>` and inline `<script>` for tab-switching, no external dependencies, no build step to *view* it — open it directly in a browser. **But don't hand-edit the Kyoto/Tokyo day-cards in this file** — see "Regenerating the itinerary HTML" below; it's generated output.
- `Kyoto_Itinerary_Plan.md` — the source-of-truth day-by-day Kyoto plan (Mon 9 Nov – Thu 12 Nov), grouped by neighborhood to minimize transit, with a booking-ahead summary table. The HTML's Kyoto tab is generated/transcribed from this.
- `Kyoto_Itinerary_Sources.md` — citation list backing every venue/hours/price claim in `Kyoto_Itinerary_Plan.md`, plus a running "Corrections made from the original draft plan" log. **Any factual change to the Kyoto plan should be accompanied by a corresponding source entry (or correction note) here.**
- `Tokyo_Itinerary_Plan.md` — the source-of-truth day-by-day Tokyo plan (Thu 12 Nov – Sat 21 Nov), same pattern as Kyoto: neighbourhood-grouped around the Shinjuku base, heavy-walking days flagged, backup/rainy-day + transit notes, booking-ahead table. Departures are staggered (Jai Fri 20, Mandeep & Tom Sat 21).
- `Tokyo_Itinerary_Sources.md` — citation list backing every venue/hours/price claim in `Tokyo_Itinerary_Plan.md`, plus a "judgement calls" log (the Tokyo analogue of the Kyoto corrections log).
- `Tokyo_Accommodation_Guide.md` — budget-first accommodation shortlist for the group's real constraints (3 travellers, en-suite, ~£450pp, no hostels), with **live Booking.com prices for the exact split dates** (8→9 Nov arrival night + 12→21 Nov main stay) and dated search links. Key finding baked in: for 3 people an **entire apartment** beats a hotel on price. Re-verify prices before booking (they drift); keep the "checked on" date current when refreshing.
- `kyoto.ics` / `tokyo.ics` — Apple/Google Calendar import files (iCalendar format) generated from the matching `*_Itinerary_Plan.md`, for syncing the trip to phones. One VEVENT per itinerary item, with address, price/hours, booking status, and a Google Maps link in the description, plus a 30-min-before VALARM reminder. **Regenerate these with the shared helper — don't hand-edit raw `.ics` (see "Regenerating the .ics calendars" below).**
- `scripts/ics_common.py` — reusable, dependency-free Python helpers for building the `.ics` files: `esc()` (RFC 5545 TEXT escaping), `fold()` (75-octet line folding), `maps()` (Google Maps URL), `build_calendar()`/`write_calendar()`, and `validate()`. A per-city generator just defines a list of event dicts and calls `write_calendar()`. Run `python scripts/ics_common.py` to self-test.
- `scripts/gen_kyoto_ics.py` / `scripts/gen_tokyo_ics.py` — the per-city `.ics` generators; each defines an `EVENTS` list and calls `write_calendar()` from `ics_common.py`. Edit an event here, re-run the script, done.
- `scripts/data_kyoto.py` / `scripts/data_tokyo.py` — **the source of truth for the Kyoto/Tokyo day-cards shown in `japan_holiday_updated.html`.** Each is a plain Python dict (`KYOTO` / `TOKYO`) — `k`/`sub`/`hint` (section header text), `pills` (the day-strip calendar), `days` (list of day dicts, each with a list of `events`: `map`, `time`, `dur`, `place`, `notes`, `extras` (`[["travel"|"food"|"bar", text], ...]`), `alt`). Values are HTML fragments (already contain `&amp;`, `<b>`, `<span class="tag">`, etc. where needed), not plain text — no escaping happens at render time.
- `scripts/html_common.py` — dependency-free renderers (`render_event`, `render_day`, `render_pill`, `render_section`) that turn the data above back into the exact `<details class="ev">` / `<details class="card daycard">` markup the `<style>` in `japan_holiday_updated.html` expects.
- `scripts/template_shell.html` — the full page shell (hero, nav, Overview, Flights, `<style>`, `<script>`, footer) with `{{KYOTO_*}}` / `{{TOKYO_*}}` markers where the generated day-cards splice in. Hand-edit this directly for anything that isn't a Kyoto/Tokyo day-card (new tab, CSS tweak, script change).
- `scripts/gen_html.py` — reads `template_shell.html`, renders `data_kyoto.py`/`data_tokyo.py` into it via `html_common.py`, and writes `japan_holiday_updated.html`. Run `python scripts/gen_html.py` after any data or template edit.
- The Tokyo tab in `japan_holiday_updated.html` is a full styled transcription of `Tokyo_Itinerary_Plan.md` (same card markup as the Kyoto tab), not a skeleton any more.

## Working conventions

- **Every factual claim needs a source.** When adding or changing a venue, price, opening hour, or transit detail, verify it (web search) and, for Kyoto content, log the citation in `Kyoto_Itinerary_Sources.md`. If a claim can't be verified, drop it rather than guess — this has precedent (see the "Izakaya Itokichi" removal logged in `Kyoto_Itinerary_Sources.md`).
- **Keep the HTML and the Markdown plans in sync.** `japan_holiday_updated.html`'s Kyoto/Tokyo tabs are a styled transcription of `Kyoto_Itinerary_Plan.md` / `Tokyo_Itinerary_Plan.md`. If you edit one, mirror the change in the other — for the HTML side that means editing `scripts/data_kyoto.py` / `scripts/data_tokyo.py` and re-running `scripts/gen_html.py`, not hand-editing the day-card HTML (see "Regenerating the itinerary HTML" below).
- **Keep `.ics` files in sync, readable, and accurate.** Any factual change to a day plan (time, venue, price, address, booking status) must be mirrored into the corresponding `.ics` file — it's a third transcription target alongside the HTML, not a one-off export. Addresses/hours/prices in `.ics` descriptions must be verified the same way as everything else in this repo (the "NO SLOP" rule applies here too — don't guess an address). On format: keep each VEVENT's DESCRIPTION scannable on a phone screen — short labeled lines (address, price, hours, booking note, Maps link), not a wall of prose — and regenerate/validate (RFC 5545 line folding, escaping, balanced BEGIN/END) via `scripts/ics_common.py` rather than hand-editing raw `.ics` text.
- Double-check any new date text against the actual 2026 calendar/day-of-week pairing (e.g. Mon 9 Nov 2026).
- When adding a new Tokyo day plan, follow the existing Kyoto pattern: neighborhood-grouped days, flag heavy-walking days, note booking-required venues (seats/reservation limits) explicitly, and add a sources file/section if introducing new venues.
- **Always check travel times to locations**. There must be reasonable accommodation/travel time to each location you suggest.

## Checking live accommodation prices (do this efficiently)

When the task needs real hotel/apartment prices, don't guess or reuse stale figures — pull them live and **timestamp them** ("checked <date>"), and paste the dated search link so they can be re-verified (NO SLOP applies to prices too).

Fastest path that worked:
- Use the in-app **Browser** (`mcp__Claude_Browser__navigate` + `get_page_text`). Build a Booking.com search-results URL directly — no clicking through forms. Template:
  `https://www.booking.com/searchresults.en-gb.html?ss=<AREA>&checkin=YYYY-MM-DD&checkout=YYYY-MM-DD&group_adults=3&no_rooms=1&group_children=0&selected_currency=GBP&order=price&nflt=review_score%3D80%3Bprivacy_type%3D3`
  - `order=price` = cheapest first; `nflt=review_score%3D80` = 8+ reviews; add `%3Bprivacy_type%3D3` for **entire apartments** only.
- Read results with `get_page_text` (NOT screenshot — the Browser pane often isn't composited, so screenshots time out; text extraction works). Prices show as "N nights, 3 adults £X" per card.
- **Key finding for this group (3 adults + en-suite):** 3 adults in **1 room fails** in central Kabukicho — Booking either throws results to the suburbs or forces 2 rooms (£2,300–3,000/9 nights). For a trio, **search entire apartments** (`privacy_type=3`); they sleep 3 (double + sofa/futon), have en-suite, and are far cheaper. The cheap high-review ones cluster in **Okubo/Shin-Okubo** (~10-min walk to Kabukicho, one Yamanote stop to Shinjuku).
- Favour listings with a **real review count** (24+), not just a 9.9 score from 1–3 reviews.
- Providing the **dated search-results URL** is a more durable "link" than a per-property URL (Booking property URLs carry an expiring `sid`).

## Regenerating the .ics calendars

Don't start an `.ics` from scratch and don't hand-fold lines. Write a small generator that reuses `scripts/ics_common.py`:

```python
# scripts/gen_tokyo_ics.py  (example)
from ics_common import maps, write_calendar
events = [
    {"day":1, "evt":1, "date":"20261112", "start":"190000", "end":"210000",
     "summary":"Dinner: Omoide Yokocho",
     "location":"1 Chome Nishishinjuku, Shinjuku City, Tokyo",
     "desc":["Specialty: yakitori at tiny counters. No reservations.",
             "Map: " + maps("Omoide Yokocho Shinjuku")]},
    # ...one dict per itinerary item, in day/time order...
]
info = write_calendar("tokyo.ics", "Tokyo Itinerary – Nov 2026",
                      "tokyo-itinerary", events)
print(info)   # {'vevents': N, 'valarms': N, 'physical_lines': ...}
```

Conventions the helper already enforces so you don't have to: UID pattern `d{day}-e{evt}-{YYYYMMDD}@{slug}.japanesy2026`, `Asia/Tokyo` VTIMEZONE, a 30-min `VALARM` per event, RFC 5545 escaping + 75-octet folding, and CRLF endings. Keep each `desc` list to short labelled lines with a `"Map: " + maps(...)` line last. `write_calendar()` runs `validate()` (checks folding + balanced BEGIN/END) and returns the counts — eyeball them against the number of items in the plan.

## Regenerating the itinerary HTML (Kyoto/Tokyo day-cards)

The ~49 event cards across the Kyoto and Tokyo tabs used to be hand-written HTML — slow to edit and easy to get subtly wrong (miss a closing tag, forget to update the matching `.ics`/`.md`). They're now generated from data, the same pattern as the `.ics` files above:

1. **Edit the data**, not the HTML. Find the event in `scripts/data_kyoto.py` or `scripts/data_tokyo.py` (it's a plain nested dict/list — `KYOTO["days"][i]["events"][j]`) and change `time`, `dur`, `place`, `notes`, `extras`, or `alt`.
2. **Regenerate:**
   ```
   python scripts/gen_html.py
   ```
   This reads `scripts/template_shell.html`, renders the data through `scripts/html_common.py`, and overwrites `japan_holiday_updated.html`. It asserts every `{{...}}` marker got resolved, so a typo'd field name fails loudly instead of shipping a literal `{{KYOTO_DAYS}}` in the page.
3. **Adding a whole new day or event:** append a dict to the relevant `days`/`events` list (copy an existing one as a template — every event needs `map`, `time`, `dur`, `place`, `notes`, `extras`, `alt`; `extras` is a list of `["travel"|"food"|"bar", text]` pairs, `alt` can be `None`). Also add the matching day-pill to `pills`, then re-run the generator.
4. Anything that **isn't** a Kyoto/Tokyo day-card (hero text, nav, Overview, Flights, `<style>`, `<script>`, footer) is hand-edited directly in `scripts/template_shell.html`, not in the data files.
5. As always, mirror the change into the matching `_Itinerary_Plan.md`, `_Itinerary_Sources.md`, and `.ics` (via `gen_kyoto_ics.py`/`gen_tokyo_ics.py`) — the generator only keeps the HTML itself fast to edit, it doesn't replace the "every claim needs a source, kept in sync across formats" rule above.

The design tokens (colors, spacing) live as CSS custom properties at the top of `<style>` in `template_shell.html` (`--red`, `--ink`, `--slate`, `--paper`, `--card`, `--line`, `--gold`, `--green`, `--blue`, `--soft`) — reuse these rather than hardcoding new colors, and prefer the existing `.travel`/`.food`/`.bar`/`.alt`/`.tag` classes over new inline styles.

## 2026 trip calendar (day-of-week reference)

Derived once so weekdays never get re-guessed — **cross-check any new date text against this** (per the "double-check date text" rule; the old HTML skeleton had these wrong):

| Date (Nov 2026) | Day | Trip phase |
|---|---|---|
| 7 | Sat | Mandeep & Tom outbound (LHR) |
| 8 | Sun | Everyone arrives Tokyo (Jai HND 10:25; M&T NRT 19:00) |
| 9 | Mon | Shinkansen Tokyo → Kyoto |
| 10 | Tue | Kyoto |
| 11 | Wed | Kyoto |
| 12 | Thu | Kyoto → Tokyo (Shinkansen); Tokyo Day 1 |
| 13 | Fri | Tokyo |
| 14 | Sat | Tokyo |
| 15 | Sun | Tokyo |
| 16 | Mon | Tokyo (Hakone day trip) |
| 17 | Tue | Tokyo |
| 18 | Wed | Tokyo |
| 19 | Thu | Tokyo (last full shared day) |
| 20 | Fri | **Jai departs** (HND 13:15) |
| 21 | Sat | **Mandeep & Tom depart** (NRT 19:30) |

Recurring closure gotchas already baked into the plans: teamLab Planets & Tsukiji Outer Market close scattered **Wednesdays**; Shinjuku Gyoen and most museums close **Mondays**; Imperial Palace East Gardens close **Mon & Fri**; Bars Benfiddich/Zoetrope/High Five close **Sundays**.
