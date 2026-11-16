#!/usr/bin/env python3
"""AIニュース app: check one day's JSON and add it to data/index.json.

Usage:  python3 add_day.py <day.json> <index.json>
  - checks the day file against the format the app reads
  - adds (or replaces) that date in index.json, newest first
Exits with code 1 and prints every problem if the day file is not valid;
index.json is left untouched in that case.
"""
import json, re, sys

SVCS = ["claude", "gpt", "gem", "manus"]
ALL = SVCS + ["other"]
TERM = re.compile(r"\[\[([A-Za-z0-9_-]+)\|([^\]]+?)\]\]")


def check(day):
    errs = []
    def need(cond, msg):
        if not cond:
            errs.append(msg)
    need(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(day.get("date", ""))), "date must be YYYY-MM-DD")
    need(isinstance(day.get("period"), str) and day["period"], "period (対象期間の一文) is missing")
    hl = day.get("highlights")
    need(isinstance(hl, list) and 1 <= len(hl) <= 3, "highlights must have 1-3 entries")
    for h in hl or []:
        need(h.get("svc") in ALL + [""], f"highlight svc must be one of {ALL}: {h}")
        need(h.get("text"), f"highlight text missing: {h}")
    sv = day.get("services")
    need(isinstance(sv, dict), "services must be an object")
    sv = sv or {}
    terms = day.get("terms") or {}
    used = set()
    for k in ALL:
        s = sv.get(k)
        if s is None:
            need(k == "other", f"services.{k} is missing (use items: [] and none: '新しい公式発表なし')")
            continue
        items = s.get("items", [])
        need(isinstance(items, list), f"services.{k}.items must be a list")
        if k in SVCS:
            need(s.get("head") or not items, f"services.{k}.head (タイルの1行) is missing")
        if not items:
            need(s.get("none"), f"services.{k}.none must say '新しい公式発表なし' when there are no items")
        for i, it in enumerate(items):
            need(it.get("body"), f"services.{k}.items[{i}].body is missing")
            need(str(it.get("url", "")).startswith("http"), f"services.{k}.items[{i}].url must be the official page URL")
            for f in ("title", "body"):
                for key, _ in TERM.findall(it.get(f, "") or ""):
                    used.add(key)
        for key, _ in TERM.findall(s.get("none", "") or ""):
            used.add(key)
    for u in day.get("unconfirmed", []) or []:
        need(u.get("text"), f"unconfirmed entry needs text: {u}")
        for key, _ in TERM.findall(u.get("text", "")):
            used.add(key)
    for key in sorted(used):
        need(key in terms, f"term [[{key}|…]] is used in the text but has no entry in terms")
    for key, t in terms.items():
        for f in ("name", "mean", "analogy", "context"):
            need(t.get(f), f"terms.{key}.{f} is missing")
    listed = set()
    for g in day.get("glossary", []) or []:
        for key in g.get("keys", []):
            need(key in terms, f"glossary key '{key}' has no entry in terms")
            listed.add(key)
    for key in terms:
        need(key in listed, f"terms.{key} is not in any glossary group")
    need(isinstance(day.get("sources"), list) and day["sources"], "sources must list the official URLs checked")
    return errs


def main(day_path, index_path):
    with open(day_path, encoding="utf-8") as f:
        day = json.load(f)
    errs = check(day)
    if errs:
        print("NG: fix these and run again")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    with open(index_path, encoding="utf-8") as f:
        idx = json.load(f)
    sv = day["services"]
    entry = {
        "date": day["date"],
        "highlight": day["highlights"][0]["text"],
        "total": sum(len((sv.get(k) or {}).get("items", [])) for k in ALL),
    }
    days = [d for d in idx.get("days", []) if d.get("date") != day["date"]]
    days.append(entry)
    days.sort(key=lambda d: d["date"], reverse=True)
    idx["days"] = days
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)
    print(f"OK: {day['date']} added; index now has {len(days)} days (newest {days[0]['date']})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
