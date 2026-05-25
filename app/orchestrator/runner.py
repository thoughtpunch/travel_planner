"""End-to-end run: matrix sweep → assemble A/B → validate top-N → persist.

The runner is intentionally synchronous internally (FastAPI wraps it in a
BackgroundTask). One run = one Run row; all fares and itineraries written in
a single transaction at the end so partial failures don't leave junk.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from ..config import settings
from ..enums import RunStatus, Source, Structure, VerificationStatus
from ..gateways import venice_metadata
from ..models import Config, Fare, Itinerary, Leg, Run
from ..sources.base import FareOffer
from ..sources.fast_flights_source import FastFlightsSource
from ..sources.quota import QuotaTracker
from ..sources.router import SourceRouter
from ..sources.serpapi_source import SerpApiSource
from ..validator import validate_top_n
from .matrix import LegSpec, expand_leg
from .ranker import rank_candidates
from .structures import (
    ItineraryCandidate,
    assemble_structure_a,
    assemble_structure_b,
)

log = logging.getLogger("trip_planner.runner")


def _config_to_snapshot(cfg: Config, legs: list[Leg]) -> dict[str, Any]:
    return {
        "name": cfg.name,
        "budget_party_total": cfg.budget_party_total,
        "currency": cfg.currency,
        "passengers": cfg.passengers,
        "structures": cfg.structures,
        "blackout_ranges": cfg.blackout_ranges,
        "validation_tolerance_pct": cfg.validation_tolerance_pct,
        "validation_top_n": cfg.validation_top_n,
        "envelope_long_gap_days": cfg.envelope_long_gap_days,
        "legs": [
            {
                "ordinal": l.ordinal,
                "origins": l.origins,
                "destinations": l.destinations,
                "date_anchor": l.date_anchor,
                "window_days": l.window_days,
                "sampling_strategy": l.sampling_strategy,
            }
            for l in sorted(legs, key=lambda x: x.ordinal)
        ],
    }


def _sum_used_serpapi_calls(session: Session) -> int:
    rows = session.exec(select(Run.serpapi_calls).where(Run.status == RunStatus.COMPLETE.value)).all()
    return int(sum(r or 0 for r in rows))


def execute_run(run_id: int, session_factory) -> None:
    """Run synchronously. session_factory is a callable returning a Session."""
    with session_factory() as session:
        run = session.get(Run, run_id)
        if run is None:
            raise RuntimeError(f"Run {run_id} not found")
        cfg = session.get(Config, run.config_id)
        legs = session.exec(select(Leg).where(Leg.config_id == cfg.id)).all()
        snapshot = _config_to_snapshot(cfg, legs)
        run.config_snapshot = snapshot
        run.status = RunStatus.RUNNING.value
        run.started_at = datetime.now(timezone.utc)
        session.add(run)
        session.commit()

        pax = cfg.passengers
        adults = pax.get("adults", 1)

        # Quota tracker carries this-month usage across runs (approximation:
        # we sum completed runs' calls for the rolling tally).
        used_before = _sum_used_serpapi_calls(session)
        quota = QuotaTracker(
            ceiling=settings.serpapi_monthly_ceiling,
            used_before_run=used_before,
        )

        primary = FastFlightsSource(currency=cfg.currency)
        # Two SerpAPI instances sharing the same QuotaTracker:
        # - fallback: fast, deep_search=False — used by the sweep router
        # - validator: deep_search=True — used for the authoritative
        #   re-query at full pax (slower per call, but produces results
        #   identical to Google Flights in the browser per SerpAPI docs)
        fallback = (
            SerpApiSource(
                api_key=settings.serpapi_key, quota=quota,
                currency=cfg.currency, deep_search=False,
            )
            if settings.serpapi_key else None
        )
        validator_source = (
            SerpApiSource(
                api_key=settings.serpapi_key, quota=quota,
                currency=cfg.currency, deep_search=True,
            )
            if settings.serpapi_key else None
        )
        router = SourceRouter(primary=primary, fallback=fallback)

        sweep_calls = 0
        sweep_offers_by_leg: dict[int, list[FareOffer]] = {}
        for leg in sorted(legs, key=lambda x: x.ordinal):
            spec = LegSpec(
                ordinal=leg.ordinal,
                origins=leg.origins,
                destinations=leg.destinations,
                date_anchor=leg.date_anchor,
                window_days=leg.window_days,
                sampling_strategy=leg.sampling_strategy,
                return_date_anchor=leg.return_date_anchor,
                return_window_days=leg.return_window_days,
                return_sampling_strategy=leg.return_sampling_strategy,
            )
            queries = expand_leg(
                spec,
                adults=adults,
                children=pax.get("children", 0),
                infants_in_seat=pax.get("infants_in_seat", 0),
                infants_on_lap=pax.get("infants_on_lap", 0),
            )
            leg_offers: list[FareOffer] = []
            for q in queries:
                sweep_calls += 1
                result = router.sweep(q)
                if result.error:
                    log.warning("sweep %s→%s on %s: %s", q.origin, q.destination, q.date, result.error)
                leg_offers.extend(result.offers)
            sweep_offers_by_leg[leg.ordinal] = leg_offers

        # Structure assembly
        structures_to_price = set(cfg.structures or [])
        all_candidates: list[ItineraryCandidate] = []

        if Structure.A_THREE_ONEWAYS.value in structures_to_price:
            a = assemble_structure_a(
                leg1_offers=sweep_offers_by_leg.get(1, []),
                leg2_offers=sweep_offers_by_leg.get(2, []),
                leg3_offers=sweep_offers_by_leg.get(3, []),
                blackout_ranges=cfg.blackout_ranges,
                currency=cfg.currency,
            )
            all_candidates.extend(a)

        if Structure.B_NESTED_ENVELOPE.value in structures_to_price:
            # For B with RT pricing: leg 1 = SJO ⇄ DC outer RT, leg 2 = DC ⇄ EU inner RT.
            b = assemble_structure_b(
                outer_rt_offers=sweep_offers_by_leg.get(1, []),
                inner_rt_offers=sweep_offers_by_leg.get(2, []),
                blackout_ranges=cfg.blackout_ranges,
                long_gap_days=cfg.envelope_long_gap_days,
                currency=cfg.currency,
            )
            all_candidates.extend(b)

        # Validation pass — uses deep_search=True for accuracy.
        if validator_source is not None and all_candidates:
            validated = validate_top_n(
                candidates=all_candidates,
                serpapi=validator_source,
                adults=adults,
                top_n=cfg.validation_top_n,
                tolerance_pct=cfg.validation_tolerance_pct,
                ttl_seconds=settings.fare_ttl_seconds,
            )
        else:
            validated = all_candidates

        ranked = rank_candidates(validated)

        # Persist — track fare ids per candidate explicitly to avoid mis-mapping
        # when multiple candidates share a leg (cheap pointer to same offer).
        itin_rows: list[Itinerary] = []
        for rank, cand in enumerate(ranked, start=1):
            cand_fare_rows: list[Fare] = []
            for idx, leg_offer in enumerate(cand.legs, start=1):
                cand_fare_rows.append(Fare(
                    run_id=run.id,
                    leg_ordinal=idx,
                    structure=cand.structure,
                    origin=leg_offer.origin,
                    destination=leg_offer.destination,
                    date=leg_offer.date,
                    return_date=leg_offer.return_date,
                    carrier=leg_offer.carrier,
                    price_per_pax=leg_offer.price_per_pax,
                    price_party=leg_offer.price_per_pax * max(1, leg_offer.passengers_queried),
                    currency=leg_offer.currency,
                    stops=leg_offer.stops,
                    duration_minutes=leg_offer.duration_minutes,
                    source=leg_offer.source,
                    verification_status=leg_offer.verification_status,
                    passengers_queried=leg_offer.passengers_queried,
                    flags=[],
                    notes=json.dumps(leg_offer.raw)[:500] if leg_offer.raw else None,
                ))
            session.add_all(cand_fare_rows)
            session.flush()
            ids = [f.id for f in cand_fare_rows]
            itin_rows.append(Itinerary(
                run_id=run.id,
                structure=cand.structure,
                total_party_price=cand.total_party_price,
                currency=cand.currency,
                verification_status=cand.verification_status,
                fare_ids=ids,
                gateway=cand.gateway,
                train_to_venice=venice_metadata(cand.gateway) if cand.gateway else None,
                flags=cand.flags,
                rank=rank,
            ))
        session.add_all(itin_rows)

        run.scraper_calls = sweep_calls
        run.serpapi_calls = quota.used_this_run
        run.serpapi_quota_remaining = quota.remaining
        run.status = RunStatus.COMPLETE.value
        run.finished_at = datetime.now(timezone.utc)
        session.add(run)
        session.commit()


__all__ = ["execute_run"]
