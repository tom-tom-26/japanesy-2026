"""Validate food venue JSON files. Usage: python scripts/food/validate.py file.json [more.json ...]
Exit 1 on errors. Prints per-anchor open-venue counts per hour (min across Mon-Sun)."""
import json, math, re, sys

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
CATS = {"ramen", "soba-udon", "sushi", "tonkatsu-fry", "yakitori-grill", "yakiniku", "izakaya", "kaiseki-teishoku",
        "unagi-tempura", "okonomiyaki-monja", "curry", "western-yoshoku", "cafe-kissaten", "bakery-sweets",
        "street-food-market", "bar", "other"}
RES = {"none", "recommended", "required", "walk-in-queue"}
HHMM = re.compile(r"^\d{1,2}:[0-5]\d$")
MAX_KM = 1.5     # hard limit: ~20 min walk with some slack
MIN_PER_HOUR = 10


def km(a, b):
    r = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def mins(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def is_open(venue, day_idx, hour):
    """Open at hour:00 on weekday day_idx (also counts spill-over past midnight from previous day)."""
    t = hour * 60
    for iv in venue["hours"].get(DAYS[day_idx], []):
        if mins(iv[0]) <= t < mins(iv[1]):
            return True
    for iv in venue["hours"].get(DAYS[(day_idx - 1) % 7], []):
        if mins(iv[1]) > 24 * 60 and t + 24 * 60 < mins(iv[1]) and t + 24 * 60 >= mins(iv[0]):
            return True
    return False


def check(path):
    errs, warns = [], []
    d = json.load(open(path, encoding="utf-8"))
    anchors = {a["id"]: a for a in d.get("anchors", [])}
    if not anchors:
        errs.append("no anchors")
    for a in anchors.values():
        for k in ("id", "name", "lat", "lng"):
            if k not in a:
                errs.append(f"anchor {a.get('id')} missing {k}")
    seen_ids, seen_names = set(), {}
    venues = d.get("venues", [])
    for v in venues:
        vid = v.get("id", "?")
        def E(m): errs.append(f"{vid}: {m}")
        def W(m): warns.append(f"{vid}: {m}")
        for k in ("id", "name", "jp", "lat", "lng", "address", "cat", "price", "reservation", "hours", "sources", "why", "near", "confidence"):
            if k not in v or v[k] in (None, "", []):
                E(f"missing {k}")
        if vid in seen_ids:
            E("duplicate id")
        seen_ids.add(vid)
        key = re.sub(r"\W", "", v.get("name", "").lower())
        if key in seen_names:
            W(f"same name as {seen_names[key]}")
        seen_names[key] = vid
        if v.get("cat") not in CATS: E(f"bad cat {v.get('cat')}")
        if v.get("price") not in (1, 2, 3, 4): E("price must be 1-4")
        if v.get("reservation") not in RES: E(f"bad reservation {v.get('reservation')}")
        if v.get("confidence") not in ("high", "medium"): E("confidence must be high|medium")
        if len(v.get("sources", [])) < 2: E("needs >=2 sources")
        for s in v.get("sources", []):
            if not str(s).startswith("http"): E(f"bad source {s}")
        if len(v.get("why", "")) > 200: W("why >200 chars")
        lat, lng = v.get("lat"), v.get("lng")
        if not (isinstance(lat, (int, float)) and isinstance(lng, (int, float)) and 30 < lat < 46 and 128 < lng < 146):
            E(f"coordinates not in Japan: {lat},{lng}")
        else:
            near = [n for n in v.get("near", []) if n in anchors]
            if len(near) != len(v.get("near", [])): E("near has unknown anchor ids")
            if not near: E("no valid near anchor")
            for n in near:
                dist = km((lat, lng), (anchors[n]["lat"], anchors[n]["lng"]))
                if dist > MAX_KM: E(f"{dist:.2f} km from anchor {n} (> {MAX_KM})")
        tb = v.get("tabelog")
        if tb is not None:
            if not (isinstance(tb.get("score"), (int, float)) and 2.5 <= tb["score"] <= 4.6): E("tabelog score implausible")
            if "tabelog.com" not in str(tb.get("url", "")): E("tabelog url")
            if not isinstance(tb.get("reviews"), int): E("tabelog reviews must be int")
        h = v.get("hours", {})
        if set(h) != set(DAYS): E("hours needs exactly keys mon..sun")
        for dy, ivs in h.items():
            for iv in ivs:
                if not (len(iv) == 2 and all(HHMM.match(x) for x in iv)):
                    E(f"bad interval {dy} {iv}")
                elif mins(iv[1]) <= mins(iv[0]) or mins(iv[1]) > 30 * 60:
                    E(f"interval not increasing/too late {dy} {iv}")
        if not v.get("hours_source"): E("hours_source missing")
        if not v.get("hours_checked"): E("hours_checked missing")
    # coverage
    cov = {}
    if not errs:
        for aid, a in anchors.items():
            members = [v for v in venues if aid in v["near"]]
            row = []
            for hr in range(7, 24):
                counts = [sum(is_open(v, di, hr) for v in members) for di in range(7)]
                row.append(min(counts))
            cov[aid] = (len(members), row)
            short = [f"{7+i:02d}h={c}" for i, c in enumerate(row) if c < MIN_PER_HOUR]
            if short: warns.append(f"coverage<{MIN_PER_HOUR} at anchor {aid} (min over week): " + ", ".join(short))
    return errs, warns, cov, len(venues)


if __name__ == "__main__":
    bad = False
    for p in sys.argv[1:]:
        errs, warns, cov, n = check(p)
        print(f"== {p}: {n} venues, {len(errs)} errors, {len(warns)} warnings")
        for e in errs[:60]: print("  ERROR", e)
        for w in warns[:40]: print("  warn ", w)
        for aid, (cnt, row) in cov.items():
            print(f"  {aid:22s} n={cnt:3d} min-open 07..23h: " + " ".join(f"{c:2d}" for c in row))
        bad |= bool(errs)
    sys.exit(1 if bad else 0)
