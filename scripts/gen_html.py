# -*- coding: utf-8 -*-
"""
Generator for japan_holiday_updated.html — renders the Kyoto & Tokyo day-cards
from data_kyoto.py / data_tokyo.py into scripts/template_shell.html and writes
the result to ../japan_holiday_updated.html.

Edit a venue/time/price? Edit the matching dict in data_kyoto.py or data_tokyo.py,
then re-run:  python scripts/gen_html.py

The shell (hero, nav, Overview, Flights, footer, <style>, <script>) is NOT
data-driven — it changes rarely and isn't repetitive, so it's hand-edited
directly in scripts/template_shell.html. Only the ~49 repeated event cards are
generated. The shipped .html stays a single self-contained static file with no
runtime build step; this script is only for whoever is editing content.

No third-party dependencies — standard library only (Python 3).
"""
import os

from data_kyoto import KYOTO
from data_tokyo import TOKYO
from html_common import render_section

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template_shell.html")
OUTPUT = os.path.join(HERE, "..", "japan_holiday_updated.html")


def main():
    html = open(TEMPLATE, encoding="utf-8").read()
    for prefix, data in (("KYOTO", KYOTO), ("TOKYO", TOKYO)):
        for key, value in render_section(data).items():
            html = html.replace("{{%s_%s}}" % (prefix, key), value)
    remaining = [line for line in html.splitlines() if "{{" in line]
    assert not remaining, "unresolved template markers: {0}".format(remaining)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", OUTPUT, "({0} bytes)".format(len(html)))


if __name__ == "__main__":
    main()
