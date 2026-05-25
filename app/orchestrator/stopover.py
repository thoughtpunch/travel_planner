"""HARD YES stopover constructor.

When the user sets HARD YES on the stopover axis, the orchestrator injects a
stopover leg into the structure (e.g. SJO → MAD → [Italy gateway] with a
1-night gap) and prices the constructed itinerary through the normal sweep
→ validate → landed-cost pipeline. The stopover lodging assumption is added
to landed cost by the landed-cost calculator (one extra night).

This module produces ALTERNATIVE leg specs that augment (do NOT replace) the
base config's legs. The runner runs both the original and constructed
expansions and merges the results.

For a named city → one extra structure.
For a sweep candidate set → one extra structure per candidate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_cls, timedelta

from ..preferences import StopoverTarget
from .dates import parse_date
from .matrix import LegSpec


@dataclass(frozen=True)
class StopoverStructure:
    """A constructed stopover variant of the base structure.

    The runner sweeps each `legs` list as if it were a normal config and
    pairs the resulting offers under a single composite candidate stamped
    with `stopover_city` (so landed-cost's friction extractor can flag it).
    """

    stopover_city: str
    gap_nights: int
    legs: list[LegSpec]


def _shift_iso(date_str: str, days: int) -> str:
    d = parse_date(date_str)
    return (d + timedelta(days=days)).isoformat()


def construct_stopover_itineraries(
    *,
    base_legs: list[LegSpec],
    stopover_target: StopoverTarget,
    gap_nights: int = 1,
) -> list[StopoverStructure]:
    """For each candidate stopover city, produce a leg-set where leg 1
    (SJO → first EU gateway) is split into SJO → STOPOVER and STOPOVER → EU
    with a `gap_nights` separation.

    Legs after leg 1 are unchanged. Their ordinals shift up by 1 to keep the
    sequence dense.

    The base_legs list is sorted by ordinal. Only structures where leg 1 is
    one-way (`is_round_trip = False`) are supported in v1 — round-trip
    structure B's outer SJO ⇄ DC is harder to slice (the return needs its
    own stopover too); leave that for a future change.
    """
    if not base_legs:
        return []
    legs_sorted = sorted(base_legs, key=lambda l: l.ordinal)
    leg1 = legs_sorted[0]
    if leg1.is_round_trip:
        # v1 limitation: don't inject into round-trip outer legs.
        return []
    rest = legs_sorted[1:]

    cities: list[str]
    if stopover_target.city is not None:
        cities = [stopover_target.city]
    elif stopover_target.sweep_candidates:
        cities = list(stopover_target.sweep_candidates)
    else:
        return []

    structures: list[StopoverStructure] = []
    for stopover_city in cities:
        # Leg 1a: SJO → stopover, anchored at leg1's date_anchor (we may
        # want a small earlier offset later; v1 keeps it simple).
        leg1a = LegSpec(
            ordinal=1,
            origins=list(leg1.origins),
            destinations=[stopover_city],
            date_anchor=leg1.date_anchor,
            window_days=leg1.window_days,
            sampling_strategy=leg1.sampling_strategy,
        )
        # Leg 1b: stopover → EU gateway, anchored gap_nights after leg1's anchor.
        leg1b = LegSpec(
            ordinal=2,
            origins=[stopover_city],
            destinations=list(leg1.destinations),
            date_anchor=_shift_iso(leg1.date_anchor, gap_nights),
            window_days=leg1.window_days,
            sampling_strategy=leg1.sampling_strategy,
        )
        # Shift the rest's ordinals up by 1 so the sequence is dense.
        shifted_rest = [
            LegSpec(
                ordinal=l.ordinal + 1,
                origins=list(l.origins),
                destinations=list(l.destinations),
                date_anchor=l.date_anchor,
                window_days=l.window_days,
                sampling_strategy=l.sampling_strategy,
                return_date_anchor=l.return_date_anchor,
                return_window_days=l.return_window_days,
                return_sampling_strategy=l.return_sampling_strategy,
            )
            for l in rest
        ]
        structures.append(StopoverStructure(
            stopover_city=stopover_city,
            gap_nights=gap_nights,
            legs=[leg1a, leg1b, *shifted_rest],
        ))
    return structures


__all__ = ["construct_stopover_itineraries", "StopoverStructure"]
