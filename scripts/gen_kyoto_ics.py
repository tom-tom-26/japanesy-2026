# -*- coding: utf-8 -*-
"""
Generator for kyoto.ics — the single source of truth for the Kyoto calendar.
Edit an event below and re-run:  python scripts/gen_kyoto_ics.py
It writes ../kyoto.ics and prints validation counts. Uses scripts/ics_common.py.

Keep this in sync with Kyoto_Itinerary_Plan.md (and the HTML Kyoto tab) — see CLAUDE.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ics_common import maps, write_calendar  # noqa: E402

# (day, evt, date, start, end, summary, location, [desc lines])
EVENTS = [
    # DAY 1 — Mon 9 Nov — Arrival, Fushimi Inari & Southern Higashiyama
    (1, 1, "20261109", "120000", "123000",
     "Arrive Kyoto Station — drop luggage",
     "Kyoto Station, Hachijo Exit, Shimogyo-ku, Kyoto",
     ["Coin lockers: ¥700 (large), Hachijo Exit.",
      "Drop bags at the Airbnb (4-chōme-432-6 Gojobashihigashi, Higashiyama Ward, "
      "Kyoto 605-0846 — message host ahead) or Crosta Kyoto same-day delivery, "
      "~¥1,000/bag, drop off by 2pm.",
      "Map: " + maps("Kyoto Station Hachijo Exit")]),
    (1, 2, "20261109", "123000", "133000",
     "Lunch: Kyoto Ramen Koji",
     "10F Kyoto Station, Higashishiokoji Kamadonocho, Shimogyo-ku, Kyoto",
     ["Specialty: regional ramen — 8 stalls (Sapporo miso, Hakata tonkotsu, Kyoto shoyu, etc).",
      "Buy tickets from the vending machine outside each stall. No reservation needed.",
      "Map: " + maps("Kyoto Ramen Koji Kyoto Station")]),
    (1, 3, "20261109", "133000", "153000",
     "Fushimi Inari Taisha (lower loop)",
     "68 Fukakusa Yabunouchicho, Fushimi-ku, Kyoto 612-0882",
     ["Lower loop up to the Yotsutsuji viewpoint (~1.5–2 hrs round trip).",
      "Price: free. Open 24 hrs.",
      "Route: JR Nara Line, Kyoto Station → Inari Station, 5 min (local trains only — not express).",
      "You'll return at dawn on Day 3 for the full hike to the summit.",
      "Map: " + maps("Fushimi Inari Taisha")]),
    (1, 4, "20261109", "160000", "180000",
     "Kiyomizu-dera + Sannenzaka/Ninenzaka",
     "1-294 Kiyomizu, Higashiyama-ku, Kyoto 605-0862",
     ["Price: ¥500. Open 6:00–18:00.",
      "Wander the Sannenzaka/Ninenzaka slopes below for matcha sweets shops.",
      "Map: " + maps("Kiyomizu-dera Kyoto")]),
    (1, 5, "20261109", "190000", "203000",
     "Dinner: Gion Duck Noodles",
     "329 Gionmachi Kitagawa, 1F unit D, Higashiyama-ku, Kyoto 605-0073",
     ["Specialty: duck tsukemen/ramen — Kishu duck, handmade German-rye noodles.",
      "4.5/5 Tripadvisor, ranked among Kyoto's top restaurants.",
      "Small and hidden with a regular queue even in winter — go right at opening or "
      "expect a wait. No reservation.",
      "4 min walk from Gion-Shijo Station.",
      "Map: " + maps("Gion Duck Noodles Kyoto")]),
    (1, 6, "20261109", "203000", "223000",
     "OPTIONAL: Gion bar-hopping",
     "Gion / Kiyamachi-dori, Kyoto",
     ["Option A — L'Escamoteur: magic-themed cocktail bar, opens 8pm. "
      "138-9 Saitocho, Shimogyo-ku, Kyoto.",
      "Map: " + maps("L'Escamoteur Kyoto"),
      "Option B — Bee's Knees: Prohibition-style speakeasy, Asia's 50 Best Bars #76, "
      "walk-in only. 364 Kamiyacho, Nakagyo-ku, Kyoto 604-0961.",
      "Map: " + maps("Bee's Knees Kyoto")]),

    # DAY 2 — Tue 10 Nov — Arashiyama & Northwest Kyoto
    (2, 1, "20261110", "073000", "083000",
     "Coffee + Bamboo Grove (Sagano)",
     "%Arabica Kyoto Arashiyama, 3-47 Saga Tenryuji Susukinobabacho, Ukyo-ku, Kyoto 616-8385",
     ["Coffee at %Arabica (global flagship, riverside), then the Bamboo Grove.",
      "Go before 8:30 to beat tour groups.",
      "Note: heaviest walking day of the trip — expect 15,000+ steps today.",
      "Map: " + maps("%Arabica Kyoto Arashiyama")]),
    (2, 2, "20261110", "083000", "100000",
     "Tenryu-ji Sogenchi Garden",
     "68 Saga Tenryuji Susukinobabacho, Ukyo-ku, Kyoto 616-8385",
     ["Price: ¥500 (garden only). Opens 8:30, last entry 16:50.",
      "One of Kyoto's finest Zen gardens.",
      "Map: " + maps("Tenryu-ji Arashiyama")]),
    (2, 3, "20261110", "113000", "123000",
     "Lunch: Yudofu Sagano",
     "45 Saga Tenryuji Susukinobabacho, Ukyo-ku, Kyoto 616-8385",
     ["Specialty: yudofu (simmered hot tofu) kaiseki-style set, private tatami rooms.",
      "On Tabelog's curated \"Best Tofu/Yuba\" list for the area.",
      "No reservations — arrive right at opening for lunch.",
      "Map: " + maps("Yudofu Sagano Arashiyama")]),
    (2, 4, "20261110", "123000", "133000",
     "OPTIONAL: Tea Ceremony Kyoto Nagomi",
     "26 Setogawa, Saga Tenryuji, Ukyo-ku, Kyoto (Arashiyama branch)",
     ["English-friendly, prepaid.",
      "BOOK ONLINE AHEAD if adding this to the day.",
      "Map: " + maps("Tea Ceremony Kyoto Nagomi Arashiyama")]),
    (2, 5, "20261110", "134500", "144500",
     "Kinkaku-ji",
     "1 Kinkakuji-cho, Kita-ku, Kyoto 603-8361",
     ["Price: ¥500. Open 9:00–17:00.",
      "Map: " + maps("Kinkaku-ji Kyoto")]),
    (2, 6, "20261110", "150500", "160500",
     "Ryoan-ji",
     "13 Goryonoshitamachi, Ryoanji, Ukyo-ku, Kyoto 616-8001",
     ["Price: ¥600. Open 8:00–17:00.",
      "18-min walk or 5-min bus from Kinkaku-ji.",
      "Map: " + maps("Ryoan-ji Kyoto")]),
    (2, 7, "20261110", "190000", "203000",
     "Dinner: Pontocho Alley",
     "Pontocho-dori, Nakagyo-ku, Kyoto",
     ["Various yakitori/kappo counters along the lantern-lit alley "
      "(runs Sanjo–Shijo, one block west of the Kamo River).",
      "No single reservation needed — walk the lane and pick a spot with a queue of locals.",
      "Map: " + maps("Pontocho Alley Kyoto")]),
    (2, 8, "20261110", "203000", "223000",
     "OPTIONAL: Evening cocktail bar",
     "Nakagyo-ku / Shimogyo-ku, Kyoto",
     ["Option A — Bar Rocking Chair: machiya cocktail bar, bartender Kenji Tsubokura "
      "(former World Cocktail Champion). 434-2 Tachibanacho, Gokomachi-dori Bukkoji-sagaru, "
      "Shimogyo-ku, Kyoto.",
      "Map: " + maps("Bar Rocking Chair Kyoto"),
      "Option B — Nokishita711: reservation-only \"liquid cuisine\" tasting bar, "
      "seats just 4 guests per sitting. 235 Sendocho, Shimogyo-ku, Kyoto 600-8019.",
      "BOOK WELL IN ADVANCE — not a walk-in.",
      "Map: " + maps("Nokishita711 Kyoto")]),

    # DAY 3 — Wed 11 Nov — Dawn Fushimi Inari, Higashiyama Upper & Gion
    (3, 1, "20261111", "070000", "090000",
     "Fushimi Inari Taisha — dawn summit hike",
     "68 Fukakusa Yabunouchicho, Fushimi-ku, Kyoto 612-0882",
     ["Full hike to the summit this time — quiet, ~2 hrs round trip, best light of the day.",
      "Price: free. Open 24 hrs.",
      "Map: " + maps("Fushimi Inari Taisha")]),
    (3, 2, "20261111", "090000", "100000",
     "Brunch: Vermillion Cafe",
     "5-31 Fukakusa Kaidoguchicho, Fushimi-ku, Kyoto 612-0805",
     ["Specialty: avocado/poached-egg toast, matcha and coffee drinks.",
      "Run by a Japanese owner who spent 18 years in Australia; praised for coffee quality, "
      "blankets provided for outdoor seating.",
      "Open 8:30am–3pm.",
      "Map: " + maps("Vermillion Cafe Fushimi Inari")]),
    (3, 3, "20261111", "103000", "111500",
     "Kenninji Temple",
     "584 Komatsucho, Higashiyama-ku, Kyoto 605-0811",
     ["Price: ¥800. Opens 10:00, last entry 16:30.",
      "Kyoto's oldest Zen temple — the Twin Dragons ceiling painting (108 tatami mats) "
      "is the highlight.",
      "Map: " + maps("Kenninji Kyoto")]),
    (3, 4, "20261111", "111500", "121500",
     "Shogunzuka Seiryuden",
     "28 Zushiokukacho, Yamashina-ku, Kyoto 607-8456",
     ["Price: ¥500.",
      "Arguably the best panoramic view over Kyoto — far less crowded than "
      "Kiyomizu-dera's platform.",
      "Short taxi from Chion-in/Higashiyama.",
      "Map: " + maps("Shogunzuka Seiryuden")]),
    (3, 5, "20261111", "190000", "203000",
     "Dinner: Kichi Kichi Omurice — BOOKED?",
     "185-4 Zaimokucho, Sanjo Pontocho-dori Sagaru, Nakagyo-ku, Kyoto",
     ["Specialty: theatrical tableside omurice by Chef Motokichi Yukimura.",
      "Only 14 seats — internationally famous, books out WEEKS IN ADVANCE. "
      "RESERVE AS SOON AS DATES ARE LOCKED.",
      "Fallback if you can't get in: Gion Duck Noodles again, or okonomiyaki at Gion Tanto "
      "(372 Kiyomotocho, Higashiyama-ku, Gion Shijo — always has a line).",
      "Map: " + maps("Kichi Kichi Omurice Kyoto"),
      "Fallback map: " + maps("Gion Tanto Kyoto")]),

    # DAY 4 — Thu 12 Nov — Relaxed Morning, Central Kyoto & Departure
    (4, 1, "20261112", "083000", "100000",
     "Nishiki Market",
     "609 Nishidaimonjicho, Nakagyo-ku, Kyoto 604-8054",
     ["\"Kyoto's Kitchen\" — many individual stalls close Sundays/Wednesdays, "
      "so Thursday works well.",
      "Arrive before 10–11am while all stalls are open.",
      "Map: " + maps("Nishiki Market Kyoto")]),
    (4, 2, "20261112", "100000", "103000",
     "Coffee: Ogawa Coffee",
     "519-1 Kikuyacho, Nakagyo-ku, Kyoto 604-8127 (Sakaimachi Nishiki branch)",
     ["Kyoto's own roaster, founded 1952 — one of the city's three historic coffee houses "
      "alongside Inoda and Maeda.",
      "Map: " + maps("Ogawa Coffee Sakaimachi Nishiki")]),
    (4, 3, "20261112", "103000", "120000",
     "OPTIONAL SWAP: Kyoto Int'l Manga Museum",
     "Karasuma-Oike, Nakagyo-ku, Kyoto 604-0846",
     ["Price: ¥900. Open 10:00–17:00 (open Thursdays — closed every Wednesday, "
      "which is why this isn't on Day 3).",
      "Worth it only if you're willing to trim Nishiki Market short — needs ~1.5 hrs "
      "on a departure morning.",
      "Map: " + maps("Kyoto International Manga Museum")]),
    (4, 4, "20261112", "110000", "120000",
     "Depart for Kyoto Station — Shinkansen to Tokyo",
     "Kyoto Station, Kyoto",
     ["Head to Kyoto Station for the Shinkansen to Tokyo.",
      "Keep this morning genuinely light — it's a travel day.",
      "Map: " + maps("Kyoto Station")]),
]

if __name__ == "__main__":
    events = [
        {"day": d, "evt": e, "date": date, "start": start, "end": end,
         "summary": summary, "location": location, "desc": desc}
        for (d, e, date, start, end, summary, location, desc) in EVENTS
    ]
    info = write_calendar(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kyoto.ics"),
        "Kyoto Itinerary – Nov 2026", "kyoto-itinerary", events)
    print(info)
