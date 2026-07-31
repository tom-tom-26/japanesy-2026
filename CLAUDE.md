# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Trip-planning content for a Japan holiday (Kyoto & Tokyo, 8–21 November 2026, travellers: Mandeep, Tom, Jai). There is no build system, package manager, test suite, or app to run — everything here is static content: a self-contained itinerary webpage, planning docs, and a spreadsheet. Treat every task as document/content editing, not software engineering. 

The `README.md` states the operating rule for this repo: **"NO SLOP"** — every claim (opening hours, prices, transit times, restaurant/bar recommendations) must be real, verifiable, and current. Do not invent venues, prices, or logistics.

## File map

- `japan_holiday_updated.html` — the current, canonical single-page itinerary site (tabbed: Overview / Flights / Kyoto / Tokyo). Self-contained: inline `<style>` and inline `<script>` for tab-switching, no external dependencies, no build step. Open it directly in a browser to view/test changes.
- `Kyoto_Itinerary_Plan.md` — the source-of-truth day-by-day Kyoto plan (Mon 9 Nov – Thu 12 Nov), grouped by neighborhood to minimize transit, with a booking-ahead summary table. The HTML's Kyoto tab is generated/transcribed from this.
- `Kyoto_Itinerary_Sources.md` — citation list backing every venue/hours/price claim in `Kyoto_Itinerary_Plan.md`, plus a running "Corrections made from the original draft plan" log. **Any factual change to the Kyoto plan should be accompanied by a corresponding source entry (or correction note) here.**
- `Tokyo_Accommodation_Guide.md` — broad accommodation research across Airbnb/Booking.com/Agoda/Hostelworld for Shinjuku/Kabukicho.
- `Tokyo_Accommodation_Guide_Ensuite_Budget.md` — narrowed accommodation shortlist filtered to the group's actual constraints (3 travellers, en-suite required, ~£450/person budget, no hostels).
- `japan_plan.xlsx` — spreadsheet backing the itinerary (binary; not directly editable as text — treat as source data to cross-check against, or ask the user for a CSV export if values need to change).
- `kyoto.ics` — Apple/Google Calendar import file (iCalendar format) generated from `Kyoto_Itinerary_Plan.md`, for syncing the trip to phones. One VEVENT per itinerary item, with address, price/hours, booking status, and a Google Maps link in the description, plus a 30-min-before VALARM reminder. A `tokyo.ics` should follow the same pattern once the Tokyo plan is written.
- Tokyo itinerary content itself is not yet written — the Tokyo tab in the HTML is currently just a date skeleton (12th–21st Nov) to be filled in, analogous to how the Kyoto plan/sources pair works.

## Working conventions

- **Every factual claim needs a source.** When adding or changing a venue, price, opening hour, or transit detail, verify it (web search) and, for Kyoto content, log the citation in `Kyoto_Itinerary_Sources.md`. If a claim can't be verified, drop it rather than guess — this has precedent (see the "Izakaya Itokichi" removal logged in `Kyoto_Itinerary_Sources.md`).
- **Keep the HTML and the Markdown plans in sync.** `japan_holiday_updated.html`'s Kyoto section is a styled transcription of `Kyoto_Itinerary_Plan.md`. If you edit one, mirror the change in the other.
- **Keep `.ics` files in sync, readable, and accurate.** Any factual change to a day plan (time, venue, price, address, booking status) must be mirrored into the corresponding `.ics` file — it's a third transcription target alongside the HTML, not a one-off export. Addresses/hours/prices in `.ics` descriptions must be verified the same way as everything else in this repo (the "NO SLOP" rule applies here too — don't guess an address). On format: keep each VEVENT's DESCRIPTION scannable on a phone screen — short labeled lines (address, price, hours, booking note, Maps link), not a wall of prose — and regenerate/validate (RFC 5545 line folding, escaping, balanced BEGIN/END) rather than hand-editing raw `.ics` text.
- Double-check any new date text against the actual 2026 calendar/day-of-week pairing (e.g. Mon 9 Nov 2026).
- When adding a new Tokyo day plan, follow the existing Kyoto pattern: neighborhood-grouped days, flag heavy-walking days, note booking-required venues (seats/reservation limits) explicitly, and add a sources file/section if introducing new venues.
- **Always check travel times to locations**. There must be reasonable accommodation/travel time to each location you suggest.
