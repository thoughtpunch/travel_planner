"""Tests for the stopover constructor."""

from __future__ import annotations

import pytest

from app.orchestrator.matrix import LegSpec
from app.orchestrator.stopover import construct_stopover_itineraries
from app.preferences import StopoverTarget


def _structure_a_legs() -> list[LegSpec]:
    return [
        LegSpec(ordinal=1, origins=["SJO"], destinations=["VCE", "MXP", "BLQ"],
                date_anchor="2026-09-10", window_days=3, sampling_strategy="anchor"),
        LegSpec(ordinal=2, origins=["VCE", "MXP", "BLQ"], destinations=["IAD"],
                date_anchor="2026-11-10", window_days=3, sampling_strategy="anchor"),
        LegSpec(ordinal=3, origins=["IAD"], destinations=["SJO"],
                date_anchor="2026-12-20", window_days=3, sampling_strategy="anchor"),
    ]


def test_named_stopover_produces_one_structure():
    legs = _structure_a_legs()
    out = construct_stopover_itineraries(
        base_legs=legs,
        stopover_target=StopoverTarget(city="MAD"),
        gap_nights=1,
    )
    assert len(out) == 1
    s = out[0]
    assert s.stopover_city == "MAD"
    assert len(s.legs) == 4  # leg1a + leg1b + 2 shifted legs
    assert s.legs[0].destinations == ["MAD"]
    assert s.legs[1].origins == ["MAD"]
    assert s.legs[1].destinations == ["VCE", "MXP", "BLQ"]
    # leg 1b anchor is 1 day after leg 1a anchor.
    assert s.legs[0].date_anchor == "2026-09-10"
    assert s.legs[1].date_anchor == "2026-09-11"
    # Shifted rest preserves the rest's anchors and shifts ordinals up by 1.
    assert s.legs[2].ordinal == 3
    assert s.legs[2].date_anchor == "2026-11-10"
    assert s.legs[3].ordinal == 4


def test_sweep_candidates_produces_one_structure_per_candidate():
    legs = _structure_a_legs()
    out = construct_stopover_itineraries(
        base_legs=legs,
        stopover_target=StopoverTarget(sweep_candidates=["MAD", "LIS"]),
    )
    assert len(out) == 2
    assert {s.stopover_city for s in out} == {"MAD", "LIS"}


def test_round_trip_leg1_skipped_in_v1():
    """Structure B's outer SJO ⇄ DC is round-trip — v1 doesn't slice it."""
    rt_legs = [
        LegSpec(ordinal=1, origins=["SJO"], destinations=["IAD"],
                date_anchor="2026-09-05", window_days=3, sampling_strategy="anchor",
                return_date_anchor="2026-12-20", return_window_days=3),
        LegSpec(ordinal=2, origins=["IAD"], destinations=["VCE"],
                date_anchor="2026-09-07", window_days=3, sampling_strategy="anchor",
                return_date_anchor="2026-12-17", return_window_days=3),
    ]
    out = construct_stopover_itineraries(
        base_legs=rt_legs, stopover_target=StopoverTarget(city="MAD"),
    )
    assert out == []


def test_empty_target_returns_empty():
    legs = _structure_a_legs()
    out = construct_stopover_itineraries(
        base_legs=legs, stopover_target=StopoverTarget(sweep_candidates=["MAD"]),
    )
    assert len(out) == 1
