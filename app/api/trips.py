"""Trips + shortlist endpoints.

A trip owns one Config, many Runs, one Shortlist, and Notes. Shortlist items
are immutable snapshots of itineraries at save time so future edits to the
originating run or the gateway-transfer table do NOT mutate the saved view.
Per `add-primevue-trip-wizard/specs/web-api`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from ..db import get_session
from ..models import Config, Itinerary, Run, ShortlistItem, Trip
from ..schemas import (
    ShortlistItemOut,
    ShortlistItemPayload,
    ShortlistItemUpdate,
    TripOut,
    TripPayload,
    TripUpdate,
)

router = APIRouter(prefix="/api/trips", tags=["trips"])


def _trip_to_out(t: Trip) -> TripOut:
    return TripOut.model_validate(t)


@router.get("", response_model=list[TripOut])
def list_trips(include_deleted: bool = Query(False)):
    with get_session() as session:
        q = select(Trip).order_by(Trip.id.desc())
        if not include_deleted:
            q = q.where(Trip.deleted_at.is_(None))
        return [_trip_to_out(t) for t in session.scalars(q).all()]


@router.post("", response_model=TripOut, status_code=201)
def create_trip(payload: TripPayload):
    """Create a trip. If `config_id` is omitted, a draft Config is created
    implicitly so the wizard can start writing fields immediately."""
    with get_session() as session:
        config_id = payload.config_id
        if config_id is None:
            cfg = Config(
                name=f"Draft for {payload.name}",
                budget_party_total=0,
                passengers={"adults": 1},
                structures=["A"],
                blackout_ranges=[],
                preferences={},
                cost_assumptions={},
            )
            session.add(cfg)
            session.commit()
            session.refresh(cfg)
            config_id = cfg.id
        else:
            if session.get(Config, config_id) is None:
                raise HTTPException(404, f"config {config_id} not found")
        trip = Trip(name=payload.name, config_id=config_id, notes=payload.notes)
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return _trip_to_out(trip)


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int):
    with get_session() as session:
        t = session.get(Trip, trip_id)
        if t is None:
            raise HTTPException(404, "trip not found")
        return _trip_to_out(t)


@router.patch("/{trip_id}", response_model=TripOut)
def update_trip(trip_id: int, patch: TripUpdate):
    with get_session() as session:
        t = session.get(Trip, trip_id)
        if t is None:
            raise HTTPException(404, "trip not found")
        if patch.name is not None:
            t.name = patch.name
        if patch.notes is not None:
            t.notes = patch.notes
        t.updated_at = datetime.now(timezone.utc)
        session.add(t)
        session.commit()
        session.refresh(t)
        return _trip_to_out(t)


@router.delete("/{trip_id}", status_code=204)
def soft_delete_trip(trip_id: int):
    """Soft-delete: deleted_at is set; trip remains retrievable for 7 days
    via `?include_deleted=true`. A daily cleanup task can hard-delete after
    that — not implemented here."""
    with get_session() as session:
        t = session.get(Trip, trip_id)
        if t is None:
            raise HTTPException(404, "trip not found")
        t.deleted_at = datetime.now(timezone.utc)
        session.add(t)
        session.commit()


@router.get("/{trip_id}/runs", response_model=list[dict])
def trip_runs(trip_id: int, limit: int = 50):
    with get_session() as session:
        t = session.get(Trip, trip_id)
        if t is None:
            raise HTTPException(404, "trip not found")
        runs = session.scalars(
            select(Run).where(Run.config_id == t.config_id).order_by(Run.id.desc()).limit(limit)
        ).all()
        return [
            {
                "id": r.id, "config_id": r.config_id, "status": r.status,
                "started_at": r.started_at, "finished_at": r.finished_at,
                "scraper_calls": r.scraper_calls, "serpapi_calls": r.serpapi_calls,
                "filtered_out_count_by_axis": r.filtered_out_count_by_axis,
            }
            for r in runs
        ]


@router.get("/{trip_id}/shortlist", response_model=list[ShortlistItemOut])
def list_shortlist(trip_id: int):
    with get_session() as session:
        if session.get(Trip, trip_id) is None:
            raise HTTPException(404, "trip not found")
        items = session.scalars(
            select(ShortlistItem).where(ShortlistItem.trip_id == trip_id)
            .order_by(ShortlistItem.order_index, ShortlistItem.id)
        ).all()
        return [ShortlistItemOut.model_validate(i) for i in items]


@router.post("/{trip_id}/shortlist", response_model=ShortlistItemOut, status_code=201)
def add_to_shortlist(trip_id: int, payload: ShortlistItemPayload):
    """Snapshot an itinerary into the trip's shortlist. The snapshot is
    immutable — future edits to run/itinerary/table do NOT mutate this."""
    with get_session() as session:
        if session.get(Trip, trip_id) is None:
            raise HTTPException(404, "trip not found")
        it = session.get(Itinerary, payload.itinerary_id)
        if it is None or it.run_id != payload.run_id:
            raise HTTPException(404, "itinerary not found in given run")
        snapshot = {
            "structure": it.structure,
            "gateway": it.gateway,
            "total_party_price": it.total_party_price,
            "landed_cost": it.landed_cost,
            "currency": it.currency,
            "verification_status": it.verification_status,
            "flags": it.flags,
            "cost_breakdown": it.cost_breakdown,
            "friction_attributes": it.friction_attributes,
            "preference_explanations": it.preference_explanations,
            "fare_ids": it.fare_ids,
            "originating_run_id": it.run_id,
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
        }
        # Append at the end of the order.
        next_order = session.scalar(
            select(ShortlistItem.order_index)
            .where(ShortlistItem.trip_id == trip_id)
            .order_by(ShortlistItem.order_index.desc())
        )
        item = ShortlistItem(
            trip_id=trip_id,
            run_id=payload.run_id,
            itinerary_id=payload.itinerary_id,
            snapshot=snapshot,
            order_index=(next_order or 0) + 1,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return ShortlistItemOut.model_validate(item)


@router.patch("/{trip_id}/shortlist/{item_id}", response_model=ShortlistItemOut)
def update_shortlist_item(trip_id: int, item_id: int, patch: ShortlistItemUpdate):
    with get_session() as session:
        item = session.get(ShortlistItem, item_id)
        if item is None or item.trip_id != trip_id:
            raise HTTPException(404, "shortlist item not found")
        if patch.notes is not None:
            item.notes = patch.notes
        if patch.tags is not None:
            item.tags = patch.tags
        if patch.order_index is not None:
            item.order_index = patch.order_index
        session.add(item)
        session.commit()
        session.refresh(item)
        return ShortlistItemOut.model_validate(item)


@router.delete("/{trip_id}/shortlist/{item_id}", status_code=204)
def delete_shortlist_item(trip_id: int, item_id: int):
    with get_session() as session:
        item = session.get(ShortlistItem, item_id)
        if item is None or item.trip_id != trip_id:
            raise HTTPException(404, "shortlist item not found")
        session.delete(item)
        session.commit()


__all__ = ["router"]
