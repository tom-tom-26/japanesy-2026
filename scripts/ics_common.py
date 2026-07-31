# -*- coding: utf-8 -*-
"""
Reusable helpers for generating the itinerary .ics calendars (kyoto.ics, tokyo.ics).

Why this exists: the .ics files must be RFC 5545-valid (75-octet line folding,
TEXT escaping, balanced BEGIN/END) and must stay in sync with the Markdown plans.
Hand-editing raw .ics is error-prone, so regenerate instead. A per-city generator
just defines a list of events and calls build_calendar(); see the docstring at the
bottom for a minimal example, and CLAUDE.md for the workflow.

No third-party dependencies — standard library only (Python 3).
"""
import io
import urllib.parse


def maps(query):
    """Google Maps search URL for a place — used in event DESCRIPTIONs."""
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(query)


def esc(text):
    """Escape a value for an iCalendar TEXT field (RFC 5545 3.3.11)."""
    return (text.replace("\\", "\\\\")
                .replace(";", "\\;")
                .replace(",", "\\,")
                .replace("\n", "\\n"))


def fold(line):
    """Fold one logical line to <=75 octets using CRLF + single-space continuation,
    without splitting a multi-byte UTF-8 character."""
    raw = line.encode("utf-8")
    limit = 75
    out = []
    while len(raw) > limit:
        cut = limit
        while cut > 0 and (raw[cut] & 0xC0) == 0x80:  # don't cut mid-codepoint
            cut -= 1
        out.append(raw[:cut])
        raw = b" " + raw[cut:]
    out.append(raw)
    return b"\r\n".join(out).decode("utf-8")


def build_calendar(calname, slug, events, tzid="Asia/Tokyo", dtstamp="20260731T000000Z"):
    """Return a complete, folded .ics string.

    calname : X-WR-CALNAME text, e.g. "Tokyo Itinerary – Nov 2026"
    slug    : UID namespace, e.g. "tokyo-itinerary" -> UIDs like d1-e2-YYYYMMDD@tokyo-itinerary.japanesy2026
    events  : list of dicts, each with keys:
              day, evt (ints, for the UID), date ("YYYYMMDD"),
              start, end ("HHMMSS"), summary, location,
              desc (list[str] — short labelled lines; add a "Map: " + maps(...) line last)
    """
    L = []
    L += [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Japanesy 2026//{0}//EN".format(calname),
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:" + calname,
        "X-WR-TIMEZONE:" + tzid,
        "BEGIN:VTIMEZONE",
        "TZID:" + tzid,
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0900",
        "TZOFFSETTO:+0900",
        "TZNAME:JST",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]
    for ev in events:
        uid = "d{day}-e{evt}-{date}@{slug}.japanesy2026".format(
            day=ev["day"], evt=ev["evt"], date=ev["date"], slug=slug)
        L += [
            "BEGIN:VEVENT",
            "UID:" + uid,
            "DTSTAMP:" + dtstamp,
            "DTSTART;TZID={0}:{1}T{2}".format(tzid, ev["date"], ev["start"]),
            "DTEND;TZID={0}:{1}T{2}".format(tzid, ev["date"], ev["end"]),
            "SUMMARY:" + esc(ev["summary"]),
            "LOCATION:" + esc(ev["location"]),
            "DESCRIPTION:" + "\\n".join(esc(x) for x in ev["desc"]),
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:" + esc(ev["summary"]),
            "TRIGGER:-PT30M",
            "END:VALARM",
            "END:VEVENT",
        ]
    L.append("END:VCALENDAR")
    return "\r\n".join(fold(x) for x in L) + "\r\n"


def write_calendar(path, calname, slug, events, **kw):
    """Build and write the .ics, then run validate(); returns the validation dict."""
    ics = build_calendar(calname, slug, events, **kw)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ics)
    return validate(ics)


def validate(ics):
    """Sanity-check a built .ics string. Returns a dict; raises AssertionError on hard failures."""
    assert ics.endswith("\r\n"), "must end with CRLF"
    phys = ics.split("\r\n")
    over = [len(l.encode("utf-8")) for l in phys if len(l.encode("utf-8")) > 75]
    assert not over, "physical lines over 75 octets: {0}".format(over[:5])
    # unfold, then check BEGIN/END nesting is balanced
    logical = []
    for l in phys:
        if l.startswith(" ") and logical:
            logical[-1] += l[1:]
        else:
            logical.append(l)
    stack = []
    for l in logical:
        if l.startswith("BEGIN:"):
            stack.append(l[6:])
        elif l.startswith("END:"):
            assert stack and stack[-1] == l[4:], "BEGIN/END mismatch at {0}".format(l)
            stack.pop()
    assert not stack, "unclosed blocks: {0}".format(stack)
    return {
        "vevents": sum(1 for l in logical if l == "BEGIN:VEVENT"),
        "valarms": sum(1 for l in logical if l == "BEGIN:VALARM"),
        "physical_lines": len(phys),
    }


# ---------------------------------------------------------------------------
# Minimal example (run this file directly to see it work — writes nothing):
#
#   from ics_common import maps, write_calendar
#   events = [
#       {"day":1,"evt":1,"date":"20261112","start":"190000","end":"210000",
#        "summary":"Dinner: Omoide Yokocho",
#        "location":"1 Chome Nishishinjuku, Shinjuku City, Tokyo",
#        "desc":["Specialty: yakitori at tiny counters. No reservations.",
#                "Map: " + maps("Omoide Yokocho Shinjuku")]},
#   ]
#   info = write_calendar("tokyo.ics", "Tokyo Itinerary – Nov 2026",
#                         "tokyo-itinerary", events)
#   print(info)  # -> {'vevents': 1, 'valarms': 1, 'physical_lines': ...}
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo = [{
        "day": 1, "evt": 1, "date": "20261112", "start": "190000", "end": "210000",
        "summary": "Demo event", "location": "Shinjuku, Tokyo",
        "desc": ["A short labelled line.", "Map: " + maps("Shinjuku Station Tokyo")],
    }]
    print(validate(build_calendar("Demo – Nov 2026", "demo-itinerary", demo)))
