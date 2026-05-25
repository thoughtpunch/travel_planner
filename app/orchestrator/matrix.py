"""Expand a leg into (origin, destination, date[, return_date]) query tuples."""

from __future__ import annotations

from dataclasses import dataclass

from ..sources.base import FareQuery
from .dates import sample_dates


@dataclass
class LegSpec:
    ordinal: int
    origins: list[str]
    destinations: list[str]
    date_anchor: str
    window_days: int = 7
    sampling_strategy: str = "anchor,+/-3,+/-7"
    # When return_date_anchor is set, expand as round-trip — cross product of
    # outbound × return dates per (origin × destination).
    return_date_anchor: str | None = None
    return_window_days: int | None = None
    return_sampling_strategy: str | None = None

    @property
    def is_round_trip(self) -> bool:
        return self.return_date_anchor is not None


def expand_leg(leg: LegSpec, adults: int, children: int = 0,
               infants_in_seat: int = 0, infants_on_lap: int = 0) -> list[FareQuery]:
    outbound_dates = sample_dates(leg.date_anchor, leg.window_days, leg.sampling_strategy)
    return_dates: list[str | None]
    if leg.is_round_trip:
        return_dates = sample_dates(
            leg.return_date_anchor,
            leg.return_window_days or leg.window_days,
            leg.return_sampling_strategy or leg.sampling_strategy,
        )
    else:
        return_dates = [None]

    queries: list[FareQuery] = []
    for origin in leg.origins:
        for dest in leg.destinations:
            if origin == dest:
                continue
            for d in outbound_dates:
                for rd in return_dates:
                    if rd is not None and rd <= d:
                        # return must be strictly after outbound
                        continue
                    queries.append(
                        FareQuery(
                            origin=origin,
                            destination=dest,
                            date=d,
                            return_date=rd,
                            adults=adults,
                            children=children,
                            infants_in_seat=infants_in_seat,
                            infants_on_lap=infants_on_lap,
                        )
                    )
    return queries
