"""Scrape the public contributions calendar (no token needed).

Usage: python scripts/fetch_contributions.py [username]
Output: data/contributions.json
"""
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else "Carlosvpm"
URL = f"https://github.com/users/{USER}/contributions"

resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# tooltips carry the counts: "3 contributions on May 4th." / "No contributions on ..."
counts = {}
for tip in soup.select("tool-tip[for]"):
    m = re.match(r"(\d+) contribution", tip.get_text(strip=True))
    counts[tip["for"]] = int(m.group(1)) if m else 0

days = []
for td in soup.select("td.ContributionCalendar-day[data-date]"):
    days.append(
        {
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": counts.get(td.get("id"), 0),
        }
    )
days.sort(key=lambda d: d["date"])
if not days:
    sys.exit("no contribution cells found; GitHub markup may have changed")

# streaks (today may still be empty, so the current streak may end yesterday)
by_date = {d["date"]: d["count"] for d in days}
longest = run = 0
for d in days:
    run = run + 1 if d["count"] > 0 else 0
    longest = max(longest, run)

cur = 0
day = date.fromisoformat(days[-1]["date"])
if by_date.get(day.isoformat(), 0) == 0:
    day -= timedelta(days=1)
while by_date.get(day.isoformat(), 0) > 0:
    cur += 1
    day -= timedelta(days=1)

best = max(days, key=lambda d: d["count"])
monthly = defaultdict(int)
for d in days:
    monthly[d["date"][:7]] += d["count"]

data = {
    "user": USER,
    "fetched": date.today().isoformat(),
    "days": days,
    "stats": {
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"] > 0),
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": dict(sorted(monthly.items())),
    },
}

Path("data").mkdir(exist_ok=True)
Path("data/contributions.json").write_text(json.dumps(data, indent=1))
s = data["stats"]
print(f"{len(days)} days, {s['total']} contributions, streak {s['current_streak']}/{s['longest_streak']}")
