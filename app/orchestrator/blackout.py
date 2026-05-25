"""Blackout date flagging (e.g. US Thanksgiving weekend)."""

from __future__ import annotations

from datetime import date, timedelta

from .dates import parse_date


def is_blackout(d: str, ranges: list[dict[str, str]]) -> bool:
    """ranges: [{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "label": "..."}]"""
    target = parse_date(d)
    for r in ranges:
        start = parse_date(r["start"])
        end = parse_date(r["end"])
        if start <= target <= end:
            return True
    return False


def thanksgiving_weekend(year: int) -> dict[str, str]:
    """US Thanksgiving = 4th Thursday of November. Weekend = Wed before through Sun after."""
    first = date(year, 11, 1)
    # Thursday is weekday 3
    first_thursday_offset = (3 - first.weekday()) % 7
    first_thursday = date(year, 11, 1 + first_thursday_offset)
    fourth_thursday = first_thursday + timedelta(days=21)
    wed = fourth_thursday - timedelta(days=1)
    sun = fourth_thursday + timedelta(days=3)
    return {"start": wed.isoformat(), "end": sun.isoformat(), "label": f"Thanksgiving {year}"}
