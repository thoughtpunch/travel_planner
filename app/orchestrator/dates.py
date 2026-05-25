"""Date sampling strategies — control sweep cost vs coverage."""

from __future__ import annotations

from datetime import date, datetime, timedelta


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def sample_dates(anchor: str, window_days: int, strategy: str) -> list[str]:
    """strategy examples:
    - "anchor"               → just anchor
    - "anchor,+/-3"          → anchor, ±3
    - "anchor,+/-3,+/-7"     → anchor, ±3, ±7
    - "every-day"            → every day within window_days
    """
    a = parse_date(anchor)
    offsets: set[int] = set()
    parts = [p.strip() for p in strategy.split(",") if p.strip()]
    for p in parts:
        if p == "anchor":
            offsets.add(0)
        elif p == "every-day":
            for d in range(-window_days, window_days + 1):
                offsets.add(d)
        elif p.startswith("+/-"):
            try:
                n = int(p[3:])
                offsets.add(n)
                offsets.add(-n)
            except ValueError:
                continue
        elif p.startswith("+"):
            try:
                offsets.add(int(p[1:]))
            except ValueError:
                continue
        elif p.startswith("-"):
            try:
                offsets.add(-int(p[1:]))
            except ValueError:
                continue
    # Bound to window
    offsets = {o for o in offsets if abs(o) <= window_days}
    return [(a + timedelta(days=o)).isoformat() for o in sorted(offsets)]
