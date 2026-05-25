"""End-to-end test for §6.5 of add-preference-weighted-landed-cost.

A run with preferences `{stopover: hard_yes(MAD), layover_length: hard_no(>4h),
red_eye: avoid}` produces a result set with:
- at least one constructed MAD stopover candidate,
- no >4h layover candidates,
- red-eye candidates ranked below non-red-eye in the soft band.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.enums import RunStatus, Source, VerificationStatus
from app.preferences import (
    Axis,
    AxisSetting,
    CostAssumptions,
    Preferences,
    ScalePosition,
    StopoverTarget,
)
from app.sources.base import FareOffer


@pytest.fixture
def engine(db_engine, monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", "test-key")
    monkeypatch.setenv("SERPAPI_MONTHLY_CEILING", "9999")
    from importlib import reload
    import app.config as cm
    reload(cm)
    return db_engine


def _patch_sources(monkeypatch, *, red_eye_route: tuple[str, str] | None = None,
                    long_layover_route: tuple[str, str] | None = None):
    """Monkey-patch both primary scrapers and SerpAPI to return synthetic
    fares whose attributes vary by route. This lets us induce specific
    friction attributes per leg."""

    def _make_primary(source: Source):
        def _impl(self, query):
            arrival = "14:30"
            layovers = []
            if red_eye_route and (query.origin, query.destination) == red_eye_route:
                arrival = "04:15"
            if long_layover_route and (query.origin, query.destination) == long_layover_route:
                layovers = [{"duration_minutes": 300}]  # 5h
            return [FareOffer(
                origin=query.origin, destination=query.destination, date=query.date,
                carrier="LH", price_per_pax=600, currency="USD",
                stops=0, duration_minutes=600,
                source=source, verification_status=VerificationStatus.LEAD,
                passengers_queried=query.passenger_count,
                raw={"arrival_local_time": arrival, "layovers": layovers},
            )]
        return _impl

    def _fake_serp(self, query):
        return [FareOffer(
            origin=query.origin, destination=query.destination, date=query.date,
            carrier="LH", price_per_pax=620, currency="USD",
            stops=0, duration_minutes=600,
            source=Source.SERPAPI, verification_status=VerificationStatus.LEAD,
            passengers_queried=query.passenger_count,
            raw={"arrival_local_time": "14:30"},
        )]

    from app.sources.fast_flights_source import FastFlightsSource
    from app.sources.fli_source import FliSource
    from app.sources.serpapi_source import SerpApiSource
    monkeypatch.setattr(FastFlightsSource, "search", _make_primary(Source.FAST_FLIGHTS))
    monkeypatch.setattr(FliSource, "search", _make_primary(Source.FLI))
    monkeypatch.setattr(SerpApiSource, "search", _fake_serp)


def _seed_minimal_config(engine, preferences: Preferences, assumptions: CostAssumptions):
    from app.db import get_session
    from app.enums import Structure
    from app.models import Config, Leg

    with get_session() as s:
        cfg = Config(
            name="LandedCost E2E",
            budget_party_total=20000,
            currency="USD",
            passengers={"adults": 6},
            structures=[Structure.A_THREE_ONEWAYS.value],
            blackout_ranges=[],
            validation_tolerance_pct=15,
            validation_top_n=2,
            envelope_long_gap_days=30,
            preferences=preferences.model_dump(mode="json"),
            cost_assumptions=assumptions.model_dump(mode="json"),
        )
        s.add(cfg)
        s.commit()
        s.refresh(cfg)
        # Tight 1-day window so the matrix stays small.
        s.add_all([
            Leg(config_id=cfg.id, ordinal=1, origins=["SJO"], destinations=["VCE", "MXP"],
                date_anchor="2026-09-10", window_days=1, sampling_strategy="anchor"),
            Leg(config_id=cfg.id, ordinal=2, origins=["VCE", "MXP"], destinations=["IAD"],
                date_anchor="2026-11-10", window_days=1, sampling_strategy="anchor"),
            Leg(config_id=cfg.id, ordinal=3, origins=["IAD"], destinations=["SJO"],
                date_anchor="2026-12-20", window_days=1, sampling_strategy="anchor"),
        ])
        s.commit()
        return cfg.id


def test_e2e_hard_yes_stopover_and_hard_no_layover_and_avoid_red_eye(engine, monkeypatch):
    """The scenario from task 6.5."""
    # Make SJO→IAD a red-eye arrival route (to test the avoid-red-eye soft).
    # Make SJO→MXP a long-layover route (to test HARD NO layover filtering).
    _patch_sources(monkeypatch, red_eye_route=("IAD", "SJO"), long_layover_route=("SJO", "MXP"))

    prefs = Preferences(
        defaults={
            Axis.STOPOVER: AxisSetting(position=ScalePosition.HARD_YES),
            Axis.LAYOVER_LENGTH: AxisSetting(position=ScalePosition.HARD_NO, threshold=240),  # 4h
            Axis.RED_EYE: AxisSetting(position=ScalePosition.AVOID),
        },
        stopover_target=StopoverTarget(city="MAD"),
    )
    assumptions = CostAssumptions(stopover_lodging_per_night=200, stopover_rooms=2)
    config_id = _seed_minimal_config(engine, prefs, assumptions)

    from app.db import get_session
    from app.models import Itinerary, Run
    from app.orchestrator.runner import execute_run

    with get_session() as s:
        run = Run(config_id=config_id, config_snapshot={}, status=RunStatus.PENDING.value)
        s.add(run)
        s.commit()
        s.refresh(run)
        run_id = run.id

    execute_run(run_id, get_session)

    with get_session() as s:
        run = s.get(Run, run_id)
        itineraries = s.scalars(
            select(Itinerary).where(Itinerary.run_id == run_id).order_by(Itinerary.rank)
        ).all()

    assert run.status == RunStatus.COMPLETE.value
    assert itineraries, "expected at least one itinerary"

    # (a) at least one constructed MAD stopover candidate.
    stopover_itins = [
        it for it in itineraries
        if (it.friction_attributes or {}).get("stopover_city") == "MAD"
    ]
    assert stopover_itins, "expected constructed MAD stopover itinerary"
    # That itinerary's cost_breakdown must include a lodging component.
    cb = stopover_itins[0].cost_breakdown
    assert any(
        c["label"].startswith("Lodging") for c in cb["components"]
    ), "stopover itinerary must include lodging in cost_breakdown"

    # (b) no >4h layover candidates. The runner persisted the per-axis filter
    # count on the Run row.
    filtered = run.filtered_out_count_by_axis or {}
    assert filtered.get(Axis.LAYOVER_LENGTH.value, 0) >= 1, (
        "expected at least one itinerary filtered by HARD NO layover_length"
    )
    for it in itineraries:
        fa = it.friction_attributes or {}
        if it.verification_status not in {VerificationStatus.FAILED.value}:
            assert fa.get("layover_minutes_max", 0) <= 240, (
                f"itinerary {it.id} has layover_max {fa.get('layover_minutes_max')} > 240"
            )

    # (c) red-eye candidates ranked below non-red-eye in the soft band.
    rank_of_red_eye = [it.rank for it in itineraries if (it.friction_attributes or {}).get("red_eye")]
    rank_of_normal = [it.rank for it in itineraries if not (it.friction_attributes or {}).get("red_eye")]
    if rank_of_red_eye and rank_of_normal:
        assert min(rank_of_normal) < min(rank_of_red_eye), (
            "expected best non-red-eye itinerary to rank above best red-eye itinerary"
        )
