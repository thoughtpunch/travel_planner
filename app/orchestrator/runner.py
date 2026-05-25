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

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..enums import RunStatus, Source, Structure, VerificationStatus
from ..gateways import venice_metadata
from ..models import Config, Fare, Itinerary, Leg, Run
from ..preferences import Axis, CostAssumptions, Preferences, ScalePosition
from ..sources.base import FareOffer
from ..sources.fast_flights_source import FastFlightsSource
from ..sources.fli_source import FliSource
from ..sources.quota import QuotaTracker
from ..sources.router import SourceRouter
from ..sources.serpapi_source import SerpApiSource
from ..validator import validate_top_n
from .landed_cost import compute_landed_cost
from .matrix import LegSpec, expand_leg
from .preferences import apply_preferences
from .stopover import construct_stopover_itineraries
from .structures import (
    ItineraryCandidate,
    assemble_stopover_variant_a,
    assemble_structure_a,
    assemble_structure_b,
    mark_incomplete_structures,
)

log = logging.getLogger("trip_planner.runner")


def _config_to_snapshot(cfg: Config, legs: list[Leg]) -> dict[str, Any]:
    # `gateway_transfers_at_run_time` records the `last_reviewed` date of
    # every transfer-table entry as of run time so a historical run remains
    # interpretable after the table is updated (see search-config spec).
    from ..data.gateway_transfers import snapshot_table

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
        "preferences": cfg.preferences or {},
        "cost_assumptions": cfg.cost_assumptions or {},
        "gateway_transfers_at_run_time": snapshot_table(),
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
    rows = session.scalars(select(Run.serpapi_calls).where(Run.status == RunStatus.COMPLETE.value)).all()
    return int(sum(r or 0 for r in rows))


def execute_run(run_id: int, session_factory) -> None:
    """Run synchronously. session_factory is a callable returning a Session."""
    with session_factory() as session:
        run = session.get(Run, run_id)
        if run is None:
            raise RuntimeError(f"Run {run_id} not found")
        cfg = session.get(Config, run.config_id)
        legs = session.scalars(select(Leg).where(Leg.config_id == cfg.id)).all()
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

        if settings.primary_source == "fli":
            primary = FliSource(currency=cfg.currency)
        else:
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

        # Parse preferences + cost_assumptions from the config (Pydantic guards
        # incoherent settings; corrupted JSON → defaults).
        try:
            preferences = Preferences.model_validate(cfg.preferences or {})
        except Exception as e:  # noqa: BLE001
            log.warning("invalid preferences on config %s, using defaults: %s", cfg.id, e)
            preferences = Preferences()
        try:
            cost_assumptions = CostAssumptions.model_validate(cfg.cost_assumptions or {})
        except Exception as e:  # noqa: BLE001
            log.warning("invalid cost_assumptions on config %s, using defaults: %s", cfg.id, e)
            cost_assumptions = CostAssumptions()

        # Stage 0 (HARD YES stopover): construct stopover leg variants BEFORE
        # the sweep so they price through the unchanged pipeline. Empty when
        # stopover is not HARD YES.
        base_leg_specs = [
            LegSpec(
                ordinal=l.ordinal, origins=l.origins, destinations=l.destinations,
                date_anchor=l.date_anchor, window_days=l.window_days,
                sampling_strategy=l.sampling_strategy,
                return_date_anchor=l.return_date_anchor,
                return_window_days=l.return_window_days,
                return_sampling_strategy=l.return_sampling_strategy,
            )
            for l in sorted(legs, key=lambda x: x.ordinal)
        ]
        stopover_default = preferences.defaults.get(Axis.STOPOVER)
        stopover_structures = []
        if (
            stopover_default is not None
            and stopover_default.position == ScalePosition.HARD_YES
            and preferences.stopover_target is not None
        ):
            stopover_structures = construct_stopover_itineraries(
                base_legs=base_leg_specs,
                stopover_target=preferences.stopover_target,
                gap_nights=1,
            )

        sweep_calls = 0
        sweep_offers_by_leg: dict[int, list[FareOffer]] = {}
        out_of_band_markers: list[tuple[int, FareOffer]] = []

        def _sweep_leg(spec: LegSpec) -> list[FareOffer]:
            nonlocal sweep_calls
            queries = expand_leg(
                spec, adults=adults,
                children=pax.get("children", 0),
                infants_in_seat=pax.get("infants_in_seat", 0),
                infants_on_lap=pax.get("infants_on_lap", 0),
            )
            collected: list[FareOffer] = []
            for q in queries:
                sweep_calls += 1
                result = router.sweep(q)
                if result.error:
                    log.warning("sweep %s→%s on %s: %s", q.origin, q.destination, q.date, result.error)
                for o in result.offers:
                    if o.verification_status in (
                        VerificationStatus.FAILED,
                        VerificationStatus.SKIPPED_QUOTA,
                    ):
                        out_of_band_markers.append((spec.ordinal, o))
                    else:
                        collected.append(o)
            return collected

        # Sweep base legs (Structure A / B as configured).
        for spec in base_leg_specs:
            sweep_offers_by_leg[spec.ordinal] = _sweep_leg(spec)

        # Sweep each constructed stopover variant separately, keyed by city.
        stopover_offers_by_city: dict[str, dict[int, list[FareOffer]]] = {}
        for sv in stopover_structures:
            per_leg: dict[int, list[FareOffer]] = {}
            for spec in sv.legs:
                per_leg[spec.ordinal] = _sweep_leg(spec)
            stopover_offers_by_city[sv.stopover_city] = per_leg

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
            b = assemble_structure_b(
                outer_rt_offers=sweep_offers_by_leg.get(1, []),
                inner_rt_offers=sweep_offers_by_leg.get(2, []),
                blackout_ranges=cfg.blackout_ranges,
                long_gap_days=cfg.envelope_long_gap_days,
                currency=cfg.currency,
            )
            all_candidates.extend(b)

        # Constructed-stopover variants: assemble each (Structure A-shaped, 4 legs).
        for stopover_city, per_leg in stopover_offers_by_city.items():
            sv_candidates = assemble_stopover_variant_a(
                leg1a_offers=per_leg.get(1, []),
                leg1b_offers=per_leg.get(2, []),
                leg2_offers=per_leg.get(3, []),
                leg3_offers=per_leg.get(4, []),
                stopover_city=stopover_city,
                blackout_ranges=cfg.blackout_ranges,
                currency=cfg.currency,
            )
            all_candidates.extend(sv_candidates)

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

        validated = mark_incomplete_structures(validated)

        # Compute landed cost on every candidate that has at least one leg
        # priced; FAILED itineraries skip cost computation (their landed_cost
        # remains None and ranking puts them at the end via status order).
        party_size = sum(int(v) for v in pax.values()) or 1
        for cand in validated:
            if cand.verification_status == VerificationStatus.FAILED:
                continue
            try:
                lc, friction = compute_landed_cost(
                    legs=cand.legs, gateway=cand.gateway,
                    assumptions=cost_assumptions, party_size=party_size,
                    currency=cand.currency,
                )
                cand.landed_cost = lc.total
                cand.cost_breakdown = lc
                cand.friction_attributes = friction
            except Exception as e:  # noqa: BLE001
                log.warning("landed-cost failed for candidate gateway=%s: %s", cand.gateway, e)

        # Cheapest VALIDATED landed cost feeds the soft-band bound.
        validated_costs = [
            c.landed_cost for c in validated
            if c.verification_status == VerificationStatus.VALIDATED and c.landed_cost is not None
        ]
        cheapest_validated_landed_cost = min(validated_costs) if validated_costs else None

        scored = apply_preferences(validated, preferences, cheapest_validated_landed_cost)
        ranked = scored.ranked
        filtered_out_by_axis = {axis.value: count for axis, count in scored.filtered_out.items()}

        # Persist FAILED / SKIPPED_QUOTA markers as Fare rows up-front so
        # they show up in the run's audit trail even when no itinerary
        # references them.
        for leg_ord, marker in out_of_band_markers:
            session.add(Fare(
                run_id=run.id,
                leg_ordinal=leg_ord,
                structure="",
                origin=marker.origin,
                destination=marker.destination,
                date=marker.date,
                return_date=marker.return_date,
                carrier="",
                price_per_pax=0,
                price_party=0,
                currency=marker.currency,
                stops=0,
                duration_minutes=0,
                source=marker.source,
                verification_status=marker.verification_status,
                passengers_queried=marker.passengers_queried,
                flags=[],
                notes=json.dumps(marker.raw)[:500] if marker.raw else None,
            ))
        session.flush()

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
                landed_cost=cand.landed_cost,
                cost_breakdown=cand.cost_breakdown.model_dump(mode="json") if cand.cost_breakdown else None,
                friction_attributes=cand.friction_attributes.model_dump(mode="json") if cand.friction_attributes else None,
                preference_explanations=[e.model_dump(mode="json") for e in (cand.preference_explanations or [])],
            ))
        session.add_all(itin_rows)

        run.scraper_calls = sweep_calls
        run.serpapi_calls = quota.used_this_run
        run.serpapi_quota_remaining = quota.remaining
        run.filtered_out_count_by_axis = filtered_out_by_axis
        run.status = RunStatus.COMPLETE.value
        run.finished_at = datetime.now(timezone.utc)
        session.add(run)
        session.commit()


__all__ = ["execute_run"]
