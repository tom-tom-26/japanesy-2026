# -*- coding: utf-8 -*-
"""
Reusable renderers for the itinerary day-cards in japan_holiday_updated.html.

Why this exists: the Kyoto/Tokyo tabs are ~49 near-identical event cards
(details/summary/ev-detail markup). Hand-editing that HTML for every venue/time/
price change is slow and error-prone. Instead, each city's content lives as plain
data (scripts/data_kyoto.py, scripts/data_tokyo.py) and this module renders it
back into the exact markup the CSS in japan_holiday_updated.html expects.

Edit the data, run scripts/gen_html.py, done — the .html stays a single
self-contained static file with no build step for anyone just opening it in a
browser; the "build" is only this offline regeneration step for whoever's editing.

No third-party dependencies — standard library only (Python 3).
"""

EXTRA_CLASS_LABELS = {"travel", "food", "bar"}  # the three inline-tag span classes used


def render_pill(p):
    cls = "day leave" if p.get("leave") else "day"
    return ('<div class="{cls}" data-day="{day}"><div class="num">{num}</div>'
            '<div class="lab">{lab}</div></div>').format(cls=cls, **p)


def render_pills(pills):
    return "\n        ".join(render_pill(p) for p in pills)


def render_event(ev):
    lines = [
        '          <details class="ev" data-map="{map}">'.format(map=ev["map"]),
        '            <summary>',
        '              <span class="time">{time}<span class="dur">{dur}</span></span>'.format(
            time=ev["time"], dur=ev["dur"]),
        '              <span class="place">{place}</span>'.format(place=ev["place"]),
        '              <span class="chev">›</span>',
        '            </summary>',
        '            <div class="ev-detail">',
        '              <div class="notes">{notes}</div>'.format(notes=ev["notes"]),
    ]
    for cls, text in ev.get("extras", []):
        assert cls in EXTRA_CLASS_LABELS, "unknown extra span class: {0}".format(cls)
        lines.append('              <span class="{cls}">{text}</span>'.format(cls=cls, text=text))
    if ev.get("alt"):
        lines.append('              <div class="alt"><b>Not up for it?</b> {alt}</div>'.format(alt=ev["alt"]))
    lines += [
        '              <div class="maprow"><a class="mapbtn" target="_blank" rel="noopener">\U0001f5fa️ Open in Google Maps</a></div>',
        '              <div class="mapframe"></div>',
        '            </div>',
        '          </details>',
    ]
    return "\n".join(lines)


def render_day(day):
    open_attr = " open" if day.get("open") else ""
    header = (
        '      <!-- DAY {day} -->\n'
        '      <details class="card daycard" data-day="{day}" data-date="{date}"{open_attr}>\n'
        '        <summary class="card-head"><span class="titlewrap">Day {day} · {title_date} '
        '<small>{title_small}</small></span><span class="chev">›</span></summary>\n'
        '        <div class="card-body">\n'
    ).format(day=day["day"], date=day["date"], open_attr=open_attr,
              title_date=day["title_date"], title_small=day["title_small"])
    body = "\n".join(render_event(ev) for ev in day["events"])
    footer = '\n        </div>\n      </details>'
    return header + body + footer


def render_days(days):
    return "\n\n".join(render_day(d) for d in days)


def render_section(data):
    """data: dict with keys k, sub, hint, pills, days (see data_kyoto.py / data_tokyo.py)."""
    return {
        "K": data["k"],
        "SUB": data["sub"],
        "HINT": data["hint"],
        "PILLS": render_pills(data["pills"]),
        "DAYS": render_days(data["days"]),
    }
