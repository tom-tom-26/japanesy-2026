# Food research brief (shared by all area agents)

Repo: this folder's grandparent (`japanesy-2026`). Trip: 4 friends (Mandeep, Tom, Josh, Jai), Japan, 8-21 Nov 2026. Rule of the repo: **NO SLOP** -
every venue must be real, currently operating, and every fact (hours, rating, price tier, coordinates) verified from a source you actually opened.
If you cannot verify a venue, DROP it. Never invent or "recall" hours/ratings/coordinates from memory.

## What we are building
A "Food" tab: user picks a day + hour -> a clustered map of food options within a 15-20 min walk of where the itinerary has the group at that
time, showing only places open at that hour. You supply the venue pool for the anchors (locations) assigned to you.

## Selection criteria (priority order)
1. Japanese locals' opinion first: Tabelog score + review count (tabelog.com, English pages tabelog.com/en/... are fine). Tabelog is deflated:
   3.50+ is very good, 3.58+ is top-tier, ramen/izakaya/casual 3.4+ is already excellent. Prefer places whose Tabelog reviews are mostly Japanese.
   Also use: Tabelog "Hyakumeiten" (TOP 100) badges, Retty, Hot Pepper Gourmet, Gurunavi, Japanese food blogs/media (e.g. OZmall, Hanako, Pen, Time Out Tokyo, Kyoto Shimbun, local walker magazines).
2. Cross-check EVERY venue on at least one OTHER independent source (Google Maps rating >=4.0 w/ decent review count, Retty, Michelin Guide/Bib Gourmand, Japan Guide, a Japanese
   blog or media article). Put the URLs in `sources`.
3. Non-Tabelog picks are welcome when "really really good or praised for a reason": famous street-food stalls, standing counters, kissaten/cafes, bakeries, konbini-adjacent
   specialities, depachika, market stalls, tiny bars. Set `tabelog` to null and explain in `why` + show 2+ other sources.
4. NOT tourist traps. Avoid places whose reviews are dominated by foreign tourists with no local presence, unless genuinely excellent (say so).
5. Variety: sit-down restaurants, ramen/soba/udon shops, sushi (incl. cheap/standing), tonkatsu, yakitori, izakaya, kissaten/cafes, bakeries, sweets/wagashi, street food/market stalls,
   standing bars, late-night food, breakfast/morning places, vegetarian-friendly where easy. The group is 4 people: note if a place is tiny (counter of 6 = hard for 4).

## Coverage requirement (the key constraint)
For EACH anchor assigned to you, the pool must let the map show **>=10 open venues at every hour from 07:00 to 23:00** (and as many as realistic 23:00-02:00), within a **20-minute walk of the anchor**
(~1.3 km straight line; ~60% should be within 1.0 km = 15 min). That means deliberately researching breakfast/morning spots, 14:00-17:00 all-day places and cafes, and late-night places - not just dinner.
Target **>=40 venues per anchor** (more where the area is dense, e.g. Shinjuku; fewer is acceptable only where the area genuinely lacks options, e.g. Hakone, Arashiyama mornings - report shortfalls honestly).
The same venue may serve several anchors if it falls in both radii - list it ONCE (anchors are listed in `near`).

## Per-venue facts to capture (JSON object; see schema)
- `id` unique slug (`<area>-<name>`), `name` (English/romaji), `jp` (Japanese name), `lat`,`lng` (decimal, 5-6 dp, from Tabelog page map / Google Maps / OSM - must be the venue itself), `address` (short).
- `cat` one of: ramen, soba-udon, sushi, tonkatsu-fry, yakitori-grill, yakiniku, izakaya, kaiseki-teishoku, unagi-tempura, okonomiyaki-monja, curry, western-yoshoku, cafe-kissaten, bakery-sweets, street-food-market, bar, other.
- `price`: 1-4 using PER-PERSON typical spend for that venue's usual meal: 1 = under ¥1,000 ($), 2 = ¥1,000-2,999 ($$), 3 = ¥3,000-7,999 ($$$), 4 = ¥8,000+ ($$$$). Add `price_note` e.g. "lunch ¥1,100 / dinner ¥4-5k". Use Tabelog's lunch/dinner budget bands as the evidence.
- `reservation`: "none" | "recommended" | "required" | "walk-in-queue" , plus `res_note` (how to book, e.g. Tabelog net reservation, Omakase, phone-only, Japanese-only, opens X days ahead, typical queue time).
- `hours`: weekly opening hours, keys mon..sun, each a list of ["HH:MM","HH:MM"] intervals (24h clock; closes after midnight written as 24:30, 26:00 etc.). Closed day = []. Use the venue's real last-order-aware operating hours; put last order in `notes`.
  Hours must be valid for **Nov 2026** (check for seasonal/winter changes, and that regular closing days e.g. Wed / irregular holidays / Sunday are right). `hours_source` = URL, `hours_checked` = today's date.
- `tabelog`: {"score": 3.57, "reviews": 812, "url": "https://tabelog.com/...", "award": "Hyakumeiten 2024 / Bronze / null"} or null.
- `other_ratings`: e.g. {"google": [4.3, 2100], "retty": null, "michelin": "Bib Gourmand 2025"}.
- `sources`: list of >=2 URLs you actually opened (first = tabelog or primary). 
- `why`: <=160 chars, plain language, why locals love it / what to order. No marketing fluff, no superlatives you cannot back.
- `notes`: practical specifics (cash only, ticket vending machine, standing only, English menu, smoking allowed, max group size, queue times, "closed 3rd Tue", last order, seat charge/otoshi, no kids, etc.)
- `near`: list of anchor ids (assigned to you) whose 20-min walk contains it.
- `confidence`: "high" (hours+rating+location verified on 2 sources), "medium" (hours from one source only), never lower - drop instead.
- `local_pick`: true if reviewers are overwhelmingly Japanese / well-known local favourite.

## Process (be efficient; do NOT waste turns)
- Start from Tabelog area/ranking pages (e.g. https://tabelog.com/en/tokyo/A1304/rstLst/?SrtT=rt , cuisine and "lunch/dinner" ranking pages, Hyakumeiten lists), then build the hour-coverage with breakfast/cafe/late-night searches.
- Batch independent web calls in parallel. Fetch the venue's Tabelog page for hours, budget, rating, coordinates (the page contains a map with lat/lng) and confirm via a second source.
- Write results incrementally to your output file as you go (JSON, valid at all times if possible) so partial work is never lost.
- Output file: `scripts/food/<your-area>.json` = {"anchors": [...], "venues": [...]}, where each anchor = {"id","name","jp","lat","lng","note"} (anchor coordinates must be verified: they are the place named in the itinerary; ids given in your assignment).
- Run `python scripts/food/validate.py scripts/food/<your-area>.json` before finishing and fix every error it reports (it checks schema, distances to anchors, hours format, duplicates, coverage per hour).
- Final reply (<=250 words): counts per anchor, per-hour coverage shortfalls, venues dropped and why, anything suspicious. No raw dumps.
