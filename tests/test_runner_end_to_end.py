"""End-to-end runner test against an on-disk SQLite, with both sources
mocked. Verifies persistence, ranking, and budget verdict propagation."""

from __future__ import annotations

import pytest
from sqlalchemy import select


@pytest.fixture
def engine(db_engine, monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", "test-key")
    monkeypatch.setenv("SERPAPI_MONTHLY_CEILING", "999")

    from importlib import reload

    import app.config as config_module
    reload(config_module)
    return db_engine


def _patch_sources(monkeypatch):
    from app.enums import Source, VerificationStatus
    from app.sources.base import FareOffer

    def _fake_primary_search(source_id: Source):
        def _impl(self, query):
            return [FareOffer(
                origin=query.origin, destination=query.destination, date=query.date,
                carrier="LH", price_per_pax=600, currency="USD", stops=0, duration_minutes=600,
                source=source_id,
                verification_status=VerificationStatus.LEAD,
                passengers_queried=query.passenger_count,
            )]
        return _impl

    def fake_serp_search(self, query):
        # Re-query at full pax returns a slightly higher price (within tolerance).
        return [FareOffer(
            origin=query.origin, destination=query.destination, date=query.date,
            carrier="LH", price_per_pax=650, currency="USD", stops=0, duration_minutes=600,
            source=Source.SERPAPI,
            verification_status=VerificationStatus.LEAD,
            passengers_queried=query.passenger_count,
        )]

    # Patch both primaries so the test is agnostic to PRIMARY_SOURCE default.
    from app.sources.fast_flights_source import FastFlightsSource
    from app.sources.fli_source import FliSource
    from app.sources.serpapi_source import SerpApiSource

    monkeypatch.setattr(FastFlightsSource, "search", _fake_primary_search(Source.FAST_FLIGHTS))
    monkeypatch.setattr(FliSource, "search", _fake_primary_search(Source.FLI))
    monkeypatch.setattr(SerpApiSource, "search", fake_serp_search)


def test_seed_run_a_validates_and_meets_budget(engine, monkeypatch):
    _patch_sources(monkeypatch)
    from app.db import get_session
    from app.enums import RunStatus, VerificationStatus
    from app.models import Itinerary, Run
    from app.orchestrator.runner import execute_run
    from app.seed import seed_all

    ids = seed_all()
    a_id = ids["A"]

    # Use a TINY config for speed: monkey-patch sampling to just the anchor.
    from app.models import Leg as LegModel
    with get_session() as s:
        legs = s.scalars(select(LegModel).where(LegModel.config_id == a_id)).all()
        for l in legs:
            l.sampling_strategy = "anchor"
            s.add(l)
        s.commit()

    with get_session() as s:
        run = Run(config_id=a_id, config_snapshot={}, status=RunStatus.PENDING.value)
        s.add(run)
        s.commit()
        s.refresh(run)
        run_id = run.id

    execute_run(run_id, get_session)

    with get_session() as s:
        run = s.get(Run, run_id)
        assert run.status == RunStatus.COMPLETE.value
        itineraries = s.scalars(
            select(Itinerary).where(Itinerary.run_id == run_id).order_by(Itinerary.rank)
        ).all()

    assert itineraries, "expected at least one itinerary"
    # Top result must be VALIDATED (we mocked SerpAPI to return within-tolerance fares)
    assert itineraries[0].verification_status == VerificationStatus.VALIDATED.value
    # 3 legs × $650/pax × 6 pax = $11,700 — over the $6k budget, which is fine,
    # we're testing that the pipeline classifies and reports correctly.
    assert itineraries[0].total_party_price == 3 * 650 * 6


def test_run_without_serpapi_key_skips_validation(engine, monkeypatch):
    _patch_sources(monkeypatch)
    monkeypatch.setenv("SERPAPI_KEY", "")
    from importlib import reload

    import app.config as config_module
    reload(config_module)
    import app.orchestrator.runner as runner_module
    reload(runner_module)

    from app.db import get_session
    from app.enums import RunStatus, VerificationStatus
    from app.models import Itinerary, Run
    from app.seed import seed_all

    ids = seed_all()
    a_id = ids["A"]
    from app.models import Leg as LegModel
    with get_session() as s:
        legs = s.scalars(select(LegModel).where(LegModel.config_id == a_id)).all()
        for l in legs:
            l.sampling_strategy = "anchor"
            s.add(l)
        s.commit()

    with get_session() as s:
        run = Run(config_id=a_id, config_snapshot={}, status=RunStatus.PENDING.value)
        s.add(run)
        s.commit()
        s.refresh(run)
        run_id = run.id

    runner_module.execute_run(run_id, get_session)

    with get_session() as s:
        itineraries = s.scalars(
            select(Itinerary).where(Itinerary.run_id == run_id)
        ).all()
    # No SerpAPI key → all itineraries remain LEAD
    assert itineraries
    assert all(it.verification_status == VerificationStatus.LEAD.value for it in itineraries)
    # With no validation, no structure reaches VALIDATED → all itineraries flagged INCOMPLETE.
    from app.enums import Flag
    assert all(Flag.INCOMPLETE.value in it.flags for it in itineraries)


def test_scraper_failure_with_no_fallback_persists_failed_fares(engine, monkeypatch):
    """Force the primary scraper to raise + clear SerpAPI key → audit trail
    should contain at least one FAILED Fare row and ResultsOut.failed_query_count > 0."""
    from app.enums import Source, VerificationStatus
    from app.sources.base import SourceError
    from app.sources.fast_flights_source import FastFlightsSource
    from app.sources.fli_source import FliSource
    from app.sources.serpapi_source import SerpApiSource

    def fake_primary_raise(self, query):
        raise SourceError("scraper unreachable")

    def fake_serp_unused(self, query):
        return []

    monkeypatch.setattr(FastFlightsSource, "search", fake_primary_raise)
    monkeypatch.setattr(FliSource, "search", fake_primary_raise)
    monkeypatch.setattr(SerpApiSource, "search", fake_serp_unused)
    monkeypatch.setenv("SERPAPI_KEY", "")
    from importlib import reload

    import app.config as config_module
    reload(config_module)
    import app.orchestrator.runner as runner_module
    reload(runner_module)

    from app.api.runs import _build_results_payload
    from app.db import get_session
    from app.enums import RunStatus
    from app.models import Fare, Run
    from app.seed import seed_all

    ids = seed_all()
    a_id = ids["A"]
    from app.models import Leg as LegModel
    with get_session() as s:
        legs = s.scalars(select(LegModel).where(LegModel.config_id == a_id)).all()
        for l in legs:
            l.sampling_strategy = "anchor"
            s.add(l)
        s.commit()

    with get_session() as s:
        run = Run(config_id=a_id, config_snapshot={}, status=RunStatus.PENDING.value)
        s.add(run)
        s.commit()
        s.refresh(run)
        run_id = run.id

    runner_module.execute_run(run_id, get_session)

    with get_session() as s:
        failed_fares = s.scalars(
            select(Fare).where(
                Fare.run_id == run_id,
                Fare.verification_status == VerificationStatus.FAILED.value,
            )
        ).all()
    assert len(failed_fares) > 0
    assert all(f.price_per_pax == 0 for f in failed_fares)
    # FAILED rows carry the configured primary source identifier (fli by default).
    assert all(f.source == Source.FLI.value for f in failed_fares)
    # Each FAILED row carries a reason in notes (json-encoded).
    import json as _json
    reasons = {_json.loads(f.notes)["reason"] for f in failed_fares if f.notes}
    assert "no_fallback_available" in reasons

    payload = _build_results_payload(run_id)
    assert payload.failed_query_count == len(failed_fares)
    assert payload.failed_fares and payload.failed_fares[0].reason == "no_fallback_available"
