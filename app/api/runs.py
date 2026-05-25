from __future__ import annotations

import json
import threading
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlmodel import select

from ..config import settings
from ..db import get_session
from ..enums import RunStatus, VerificationStatus
from ..models import Config, Fare, Itinerary, Leg, Run
from ..orchestrator.runner import execute_run
from ..schemas import FailedFareOut, FareOut, ItineraryOut, ResultsOut, RunOut

router = APIRouter(prefix="/api/runs", tags=["runs"])


def _run_to_out(run: Run) -> RunOut:
    return RunOut(
        id=run.id,
        config_id=run.config_id,
        status=run.status,
        started_at=run.started_at,
        finished_at=run.finished_at,
        scraper_calls=run.scraper_calls,
        serpapi_calls=run.serpapi_calls,
        serpapi_quota_remaining=run.serpapi_quota_remaining,
        error=run.error,
    )


@router.post("", response_model=RunOut, status_code=202)
def trigger_run(config_id: int, background: BackgroundTasks):
    with get_session() as session:
        cfg = session.get(Config, config_id)
        if cfg is None:
            raise HTTPException(404, "config not found")
        run = Run(
            config_id=config_id,
            config_snapshot={},
            status=RunStatus.PENDING.value,
            started_at=datetime.now(timezone.utc),
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        run_id = run.id

    def _wrapped():
        try:
            execute_run(run_id, get_session)
        except Exception as e:  # noqa: BLE001
            with get_session() as s:
                r = s.get(Run, run_id)
                if r:
                    r.status = RunStatus.FAILED.value
                    r.error = str(e)[:500]
                    r.finished_at = datetime.now(timezone.utc)
                    s.add(r)
                    s.commit()

    # threading.Thread so the call returns immediately even if the runner is
    # long-running. BackgroundTasks would also work but blocks the worker.
    threading.Thread(target=_wrapped, daemon=True).start()

    with get_session() as session:
        return _run_to_out(session.get(Run, run_id))


@router.get("/{run_id}", response_model=RunOut)
def get_run(run_id: int):
    with get_session() as session:
        run = session.get(Run, run_id)
        if run is None:
            raise HTTPException(404, "run not found")
        return _run_to_out(run)


@router.get("", response_model=list[RunOut])
def list_runs(config_id: int | None = None, limit: int = 50):
    with get_session() as session:
        q = select(Run).order_by(Run.id.desc()).limit(limit)
        if config_id is not None:
            q = select(Run).where(Run.config_id == config_id).order_by(Run.id.desc()).limit(limit)
        return [_run_to_out(r) for r in session.exec(q).all()]


def _planned_serpapi_calls_for_config(config_id: int) -> int:
    """Estimate of SerpAPI calls a run will make.

    Validation = top_n × structures × leg_count_per_structure.
    Sweep contributes additional SerpAPI calls only when scraper fallback fires,
    which we cannot predict — so this is the floor, not the ceiling.
    """
    with get_session() as session:
        cfg = session.get(Config, config_id)
        if cfg is None:
            return 0
        legs = session.exec(select(Leg).where(Leg.config_id == config_id)).all()
        structures = cfg.structures or []
        per_struct = {
            "A": 3,  # three one-ways → 3 SerpAPI calls per top-N candidate
            "B": 2,  # nested envelope = 2 round-trips (1 SerpAPI call each)
        }
        return cfg.validation_top_n * sum(per_struct.get(s, len(legs)) for s in structures)


@router.get("/{run_id}/results", response_model=ResultsOut)
def get_results(run_id: int):
    return _build_results_payload(run_id)


def _build_results_payload(run_id: int) -> ResultsOut:
    from ..orchestrator.ranker import budget_verdict
    from ..orchestrator.structures import ItineraryCandidate, structure_completeness

    with get_session() as session:
        run = session.get(Run, run_id)
        if run is None:
            raise HTTPException(404, "run not found")
        cfg = session.get(Config, run.config_id)
        itin_rows = session.exec(
            select(Itinerary).where(Itinerary.run_id == run_id).order_by(Itinerary.rank)
        ).all()
        fare_rows = session.exec(
            select(Fare).where(Fare.run_id == run_id)
        ).all()
        fares_by_id = {f.id: f for f in fare_rows}

        itineraries: list[ItineraryOut] = []
        candidates_for_verdict: list[ItineraryCandidate] = []
        for it in itin_rows:
            f_outs = []
            for fid in it.fare_ids:
                f = fares_by_id.get(fid)
                if f is None:
                    continue
                f_outs.append(FareOut(
                    id=f.id, leg_ordinal=f.leg_ordinal, structure=f.structure,
                    origin=f.origin, destination=f.destination, date=f.date,
                    return_date=f.return_date,
                    carrier=f.carrier, price_per_pax=f.price_per_pax,
                    price_party=f.price_party, currency=f.currency,
                    stops=f.stops, duration_minutes=f.duration_minutes,
                    source=f.source, verification_status=f.verification_status,
                    fetched_at=f.fetched_at,
                ))
            itineraries.append(ItineraryOut(
                id=it.id, structure=it.structure,
                total_party_price=it.total_party_price, currency=it.currency,
                verification_status=it.verification_status, gateway=it.gateway,
                train_to_venice=it.train_to_venice, flags=it.flags, rank=it.rank,
                fares=f_outs,
            ))
            candidates_for_verdict.append(ItineraryCandidate(
                structure=it.structure, legs=[], gateway=it.gateway,
                total_party_price=it.total_party_price, currency=it.currency,
                flags=it.flags,
                verification_status=VerificationStatus(it.verification_status),
            ))

        verdict = budget_verdict(candidates_for_verdict, cfg.budget_party_total) if cfg else {}
        quota = {
            "ceiling": settings.serpapi_monthly_ceiling,
            "used_this_run": run.serpapi_calls,
            "remaining_after_run": run.serpapi_quota_remaining,
        }
        structures_requested = list((cfg.structures if cfg else []) or [])
        structures = structure_completeness(candidates_for_verdict, structures_requested)
        failed_fares_raw = [f for f in fare_rows if f.verification_status == VerificationStatus.FAILED.value]
        failed_fares: list[FailedFareOut] = []
        for f in failed_fares_raw:
            reason: str | None = None
            if f.notes:
                try:
                    reason = json.loads(f.notes).get("reason")
                except (json.JSONDecodeError, AttributeError):
                    reason = f.notes
            failed_fares.append(FailedFareOut(
                leg_ordinal=f.leg_ordinal,
                origin=f.origin,
                destination=f.destination,
                date=f.date,
                return_date=f.return_date,
                source=f.source,
                reason=reason,
                fetched_at=f.fetched_at,
            ))

        return ResultsOut(
            run=_run_to_out(run),
            itineraries=itineraries,
            budget_verdict=verdict,
            quota=quota,
            structures=structures,
            failed_query_count=len(failed_fares),
            failed_fares=failed_fares,
        )


@router.get("/estimate/{config_id}")
def estimate_run(config_id: int):
    """Pre-run estimate of SerpAPI calls + remaining quota."""
    from ..sources.quota import QuotaTracker
    from ..orchestrator.runner import _sum_used_serpapi_calls

    with get_session() as session:
        used = _sum_used_serpapi_calls(session)
    quota = QuotaTracker(ceiling=settings.serpapi_monthly_ceiling, used_before_run=used)
    planned = _planned_serpapi_calls_for_config(config_id)
    return quota.estimate_run(planned)
