#!/usr/bin/env python3
"""Fetch the public contribution calendar for len-vil without a personal token."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
USERNAME = "len-vil"
URL = f"https://github.com/users/{USERNAME}/contributions"


def main() -> None:
    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    cells = soup.select("[data-date][data-level]")
    if not cells:
        cells = soup.select("td[data-date], rect[data-date]")

    days: list[dict] = []
    for cell in cells:
        raw_date = cell.get("data-date")
        if not raw_date:
            continue
        try:
            day = date.fromisoformat(raw_date)
        except ValueError:
            continue

        label = " ".join(
            filter(
                None,
                [
                    cell.get("aria-label"),
                    cell.get("data-tooltip-text"),
                    cell.get_text(" ", strip=True),
                    *(child.get("aria-label") for child in cell.find_all(attrs={"aria-label": True})),
                    *(child.get_text(" ", strip=True) for child in cell.find_all("tool-tip")),
                ],
            )
        )
        match = re.search(r"([\d,]+)\s+contributions?", label, flags=re.I)
        count = int(match.group(1).replace(",", "")) if match else 0
        try:
            level = int(cell.get("data-level", 0))
        except (TypeError, ValueError):
            level = 0
        days.append({"date": day.isoformat(), "count": count, "level": max(0, min(4, level))})

    if not days:
        raise RuntimeError(
            "GitHub's contribution calendar returned no dated cells. "
            "No placeholder data was written; inspect the page markup and rerun."
        )

    days.sort(key=lambda item: item["date"])
    counts_by_month: dict[str, int] = defaultdict(int)
    for item in days:
        counts_by_month[item["date"][:7]] += item["count"]

    # Derive streaks from calendar days. Zero-contribution days break a streak.
    active = {date.fromisoformat(item["date"]) for item in days if item["count"] > 0}
    longest = current = 0
    run = 0
    for day in sorted({date.fromisoformat(item["date"]) for item in days}):
        run = run + 1 if day in active else 0
        longest = max(longest, run)
    cursor = date.today()
    # If today has no contribution yet, measure the latest streak ending yesterday.
    if cursor not in active:
        cursor -= timedelta(days=1)
    while cursor in active:
        current += 1
        cursor -= timedelta(days=1)

    total = sum(item["count"] for item in days)
    busiest = max(days, key=lambda item: item["count"])
    payload = {
        "username": USERNAME,
        "fetched_at": date.today().isoformat(),
        "total": total,
        "active_days": len(active),
        "current_streak": current,
        "longest_streak": longest,
        "busiest_day": busiest["date"],
        "busiest_day_count": busiest["count"],
        "months": dict(sorted(counts_by_month.items())),
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(days)} contribution days to {OUT}")


if __name__ == "__main__":
    main()
