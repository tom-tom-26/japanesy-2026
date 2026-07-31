# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Trip-planning content for a Japan holiday (Kyoto & Tokyo, 8–21 November 2026, travellers: Mandeep, Tom, Jai). There is no build system, package manager, test suite, or app to run — everything here is static content: a self-contained itinerary webpage, planning docs, and a spreadsheet. Treat every task as document/content editing, not software engineering. 

The `README.md` states the operating rule for this repo: **"NO SLOP"** — every claim (opening hours, prices, transit times, restaurant/bar recommendations) must be real, verifiable, and current. Do not invent venues, prices, or logistics.

## File map

- `japan_holiday_updated.html` — the current, canonical single-page itinerary site (tabbed: Overview / Flights / Kyoto / Tokyo). Self-contained: inline `<style>` and inline `<script>` for tab-switching, no external dependencies, no build step. Open it directly in a browser to view/test changes.
- `Kyoto_Itinerary_Plan.md` — the source-of-truth day-by-day Kyoto plan (Mon 9 Nov – Thu 12 Nov), grouped by neighborhood to minimize transit, with a booking-ahead summary table. The HTML's Kyoto tab is generated/transcribed from this.
- `Kyoto_Itinerary_Sources.md` — citation list backing every venue/hours/price claim in `Kyoto_Itinerary_Plan.md`, plus a running "Corrections made from the original draft plan" log. **Any factual change to the Kyoto plan should be accompanied by a corresponding source entry (or correction note) here.**
- `Tokyo_Itinerary_Plan.md` — the source-of-truth day-by-day Tokyo plan (Thu 12 Nov – Sat 21 Nov), same pattern as Kyoto: neighbourhood-grouped around the Shinjuku base, heavy-walking days flagged, backup/rainy-day + transit notes, booking-ahead table. Departures are staggered (Jai Fri 20, Mandeep & Tom Sat 21).
- `Tokyo_Itinerary_Sources.md` — citation list backing every venue/hours/price claim in `Tokyo_Itinerary_Plan.md`, plus a "judgement calls" log (the Tokyo analogue of the Kyoto corrections log).
- `Tokyo_Accommodation_Guide.md` — broad accommodation research across Airbnb/Booking.com/Agoda/Hostelworld for Shinjuku/Kabukicho.
- `Tokyo_Accommodation_Guide_Ensuite_Budget.md` — narrowed accommodation shortlist filtered to the group's actual constraints (3 travellers, en-suite required, ~£450/person budget, no hostels).
- `japan_plan.xlsx` — spreadsheet backing the itinerary (binary; not directly editable as text — treat as source data to cross-check against, or ask the user for a CSV export if values need to change).
- `kyoto.ics` / `tokyo.ics` — Apple/Google Calendar import files (iCalendar format) generated from the matching `*_Itinerary_Plan.md`, for syncing the trip to phones. One VEVENT per itinerary item, with address, price/hours, booking status, and a Google Maps link in the description, plus a 30-min-before VALARM reminder. **Regenerate these with the shared helper — don't hand-edit raw `.ics` (see "Regenerating the .ics calendars" below).**
- `scripts/ics_common.py` — reusable, dependency-free Python helpers for building the `.ics` files: `esc()` (RFC 5545 TEXT escaping), `fold()` (75-octet line folding), `maps()` (Google Maps URL), `build_calendar()`/`write_calendar()`, and `validate()`. A per-city generator just defines a list of event dicts and calls `write_calendar()`. Run `python scripts/ics_common.py` to self-test.
- The Tokyo tab in `japan_holiday_updated.html` is a full styled transcription of `Tokyo_Itinerary_Plan.md` (same card markup as the Kyoto tab), not a skeleton any more.

## Working conventions

- **Every factual claim needs a source.** When adding or changing a venue, price, opening hour, or transit detail, verify it (web search) and, for Kyoto content, log the citation in `Kyoto_Itinerary_Sources.md`. If a claim can't be verified, drop it rather than guess — this has precedent (see the "Izakaya Itokichi" removal logged in `Kyoto_Itinerary_Sources.md`).
- **Keep the HTML and the Markdown plans in sync.** `japan_holiday_updated.html`'s Kyoto section is a styled transcription of `Kyoto_Itinerary_Plan.md`. If you edit one, mirror the change in the other.
- **Keep `.ics` files in sync, readable, and accurate.** Any factual change to a day plan (time, venue, price, address, booking status) must be mirrored into the corresponding `.ics` file — it's a third transcription target alongside the HTML, not a one-off export. Addresses/hours/prices in `.ics` descriptions must be verified the same way as everything else in this repo (the "NO SLOP" rule applies here too — don't guess an address). On format: keep each VEVENT's DESCRIPTION scannable on a phone screen — short labeled lines (address, price, hours, booking note, Maps link), not a wall of prose — and regenerate/validate (RFC 5545 line folding, escaping, balanced BEGIN/END) via `scripts/ics_common.py` rather than hand-editing raw `.ics` text.
- Double-check any new date text against the actual 2026 calendar/day-of-week pairing (e.g. Mon 9 Nov 2026).
- When adding a new Tokyo day plan, follow the existing Kyoto pattern: neighborhood-grouped days, flag heavy-walking days, note booking-required venues (seats/reservation limits) explicitly, and add a sources file/section if introducing new venues.
- **Always check travel times to locations**. There must be reasonable accommodation/travel time to each location you suggest.

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
