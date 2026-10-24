"""Apply auditor findings (scripts/food/review/findings_*.json) to the area files.

- closed-or-nonexistent -> venue removed
- corrected{field: value} -> applied (only whitelisted fields)
- every audited venue gets audit = verdict; 'ok' also marks confidence "high"
Run once after the audits finish:  python scripts/food/apply_audit.py
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = {"hours", "price", "reservation", "res_note", "lat", "lng", "address", "notes", "price_note", "name", "jp"}

findings = {}
for p in glob.glob(os.path.join(HERE, "review", "findings_*.json")):
    for f in json.load(open(p, encoding="utf-8")):
        findings[f["id"]] = f

stats = {"ok": 0, "minor": 0, "wrong": 0, "removed": 0, "fields": 0}
for p in sorted(glob.glob(os.path.join(HERE, "*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    keep = []
    for v in d["venues"]:
        f = findings.get(v["id"])
        if not f:
            keep.append(v)
            continue
        verdict = f.get("verdict")
        if verdict == "closed-or-nonexistent":
            stats["removed"] += 1
            continue
        for k, val in (f.get("corrected") or {}).items():
            if k in FIELDS:
                v[k] = val
                stats["fields"] += 1
        v["audit"] = verdict
        if verdict == "ok":
            v["confidence"] = "high"
        stats[verdict] = stats.get(verdict, 0) + 1
        keep.append(v)
    d["venues"] = keep
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(stats, "audited:", len(findings))
