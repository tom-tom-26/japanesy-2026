# -*- coding: utf-8 -*-
"""
Food tab data. Two parts:

1. TIMELINE - where the itinerary has the group at each hour of each day
   (date -> [(from_hour, anchor_id, label), ...]; hour 24+ = after midnight).
   Derived from data_kyoto.py / data_tokyo.py event times. Vague times in the
   data are mapped: Eve ~18:00, Late PM ~16:00, PM ~13:00, Day ~11:00.
   `HOURS` limits the selectable hours on days that are only partly "on the ground".
2. load() - merges scripts/food/*.json (one file per research area; see
   scripts/food/BRIEF.md) into one de-duplicated anchors + venues payload that
   gen_html.py embeds in the page as JSON.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FOOD_DIR = os.path.join(HERE, "food")

# date: (short label, city tag, (first selectable hour, last selectable hour))
DAYS = [
    ("2026-11-08", "Sun 8 Nov", "Tokyo", (20, 26)),
    ("2026-11-09", "Mon 9 Nov", "Kyoto", (7, 26)),
    ("2026-11-10", "Tue 10 Nov", "Kyoto", (7, 26)),
    ("2026-11-11", "Wed 11 Nov", "Kyoto", (7, 26)),
    ("2026-11-12", "Thu 12 Nov", "Kyoto → Tokyo", (7, 26)),
    ("2026-11-13", "Fri 13 Nov", "Tokyo", (7, 26)),
    ("2026-11-14", "Sat 14 Nov", "Tokyo", (7, 26)),
    ("2026-11-15", "Sun 15 Nov", "Tokyo", (7, 26)),
    ("2026-11-16", "Mon 16 Nov", "Hakone", (7, 26)),
    ("2026-11-17", "Tue 17 Nov", "Tokyo", (7, 26)),
    ("2026-11-18", "Wed 18 Nov", "Tokyo", (7, 26)),
    ("2026-11-19", "Thu 19 Nov", "Tokyo", (7, 26)),
    ("2026-11-20", "Fri 20 Nov", "Tokyo", (7, 26)),
    ("2026-11-21", "Sat 21 Nov", "Tokyo → Narita", (7, 19)),
]

TIMELINE = {
    "2026-11-08": [(20, "haneda_t3", "Landing at Haneda (19:50)"),
                   (22, "shinjuku_east", "Arrival night in Shinjuku (stay not booked yet - assumed Shinjuku)")],
    "2026-11-09": [(7, "shinjuku_east", "Morning in Tokyo before the Shinkansen"),
                   (11, "kyoto_station", "Shinkansen to Kyoto - ramen lunch at Kyoto Station"),
                   (13, "fushimi_inari", "Fushimi Inari"),
                   (16, "kiyomizu", "Kiyomizu-dera / Higashiyama"),
                   (18, "gion", "Dinner in Gion")],
    "2026-11-10": [(7, "arashiyama", "Arashiyama + Bamboo Grove"),
                   (13, "kinkakuji", "Kinkaku-ji / Ryoan-ji"),
                   (16, "pontocho", "Dinner / nightlife - Pontocho")],
    "2026-11-11": [(7, "fushimi_inari", "Dawn at Fushimi Inari"),
                   (10, "gion", "Kenninji / Higashiyama / Gion")],
    "2026-11-12": [(7, "nishiki", "Nishiki Market + Ogawa Coffee"),
                   (11, "kyoto_station", "Kyoto Station - Shinkansen to Tokyo"),
                   (15, "shinjuku_east", "Back in Shinjuku - Omoide Yokocho night")],
    "2026-11-13": [(7, "meiji_harajuku", "Meiji Jingu + Harajuku"),
                   (13, "shibuya", "Shibuya - dinner at Nonbei Yokocho")],
    "2026-11-14": [(7, "tsukiji", "Tsukiji Outer Market"),
                   (10, "ginza", "Ginza"),
                   (13, "tokyo_station", "Tokyo Station Marunouchi"),
                   (17, "ginza", "Cocktails in Ginza")],
    "2026-11-15": [(7, "asakusa", "Senso-ji / Asakusa"),
                   (12, "ueno", "Ueno"),
                   (15, "akihabara", "Akihabara"),
                   (17, "ebisu", "Dinner - Ebisu Yokocho")],
    "2026-11-16": [(7, "shinjuku_east", "Odakyu Romancecar from Shinjuku"),
                   (9, "hakone_yumoto", "Hakone-Yumoto"),
                   (11, "gora", "Gora"),
                   (12, "owakudani", "Owakudani"),
                   (14, "moto_hakone", "Lake Ashi / Moto-Hakone"),
                   (16, "hakone_yumoto", "Onsen at Hakone Yuryo"),
                   (19, "shinjuku_east", "Back in Shinjuku")],
    "2026-11-17": [(7, "shinjuku_east", "Morning near the apartment"),
                   (10, "shimokitazawa", "Shimokitazawa"),
                   (14, "nakameguro", "Nakameguro - dinner + drinks")],
    "2026-11-18": [(7, "shinjuku_east", "Morning near the apartment"),
                   (9, "nishi_shinjuku", "Tokyo Metropolitan Government Building"),
                   (11, "shinjuku_gyoen", "Shinjuku Gyoen"),
                   (14, "shinjuku_east", "Afternoon in Shinjuku"),
                   (17, "nishi_shinjuku", "Nishi-Shinjuku cocktail crawl")],
    "2026-11-19": [(7, "shinjuku_east", "Morning near the apartment"),
                   (9, "toyosu", "teamLab Planets + Toyosu"),
                   (16, "shinjuku_east", "Final big night - Kabukicho")],
    "2026-11-20": [(7, "shinjuku_east", "Morning near the apartment (Jai flies out)"),
                   (11, "yanaka", "Relaxed day - Yanaka"),
                   (17, "shinjuku_east", "Evening in Kabukicho")],
    "2026-11-21": [(7, "shinjuku_east", "Last morning in Shinjuku"),
                   (17, "narita_t1", "Narita Airport (19:30 flight)")],
}


def _norm(name):
    return "".join(ch for ch in name.lower() if ch.isalnum())


def load():
    """Merge scripts/food/*.json. Returns the dict embedded in the page."""
    anchors, venues = {}, {}
    by_key = {}  # tabelog url, or normalised name -> venue id (cross-file de-duplication)
    for path in sorted(glob.glob(os.path.join(FOOD_DIR, "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        for a in d.get("anchors", []):
            anchors[a["id"]] = {k: a[k] for k in ("id", "name", "jp", "lat", "lng", "note") if k in a}
        for v in d.get("venues", []):
            key = (v.get("tabelog") or {}).get("url") or _norm(v["name"])
            if key in by_key:                      # same venue in two area files
                venues[by_key[key]]["near"] = sorted(set(venues[by_key[key]]["near"]) | set(v["near"]))
                continue
            by_key[key] = v["id"]
            venues[v["id"]] = v
    for date, steps in TIMELINE.items():
        for _, aid, _ in steps:
            assert aid in anchors, "timeline anchor %s (%s) missing from scripts/food/*.json" % (aid, date)
    return {
        "anchors": anchors,
        "venues": list(venues.values()),
        "timeline": {d: [list(s) for s in steps] for d, steps in TIMELINE.items()},
        "days": [{"date": d, "label": l, "city": c, "hours": list(h)} for d, l, c, h in DAYS],
    }
