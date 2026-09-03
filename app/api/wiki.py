"""Persistent API for the Italy 2026 operational wiki."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from ..config import settings
from ..db import get_session
from ..models import (
    ActivityAttachment,
    ActivityOption,
    TripCost,
    WikiDay,
    WikiItineraryItem,
    WikiLeg,
    WikiSetting,
    WikiStay,
    WikiStop,
    WikiTraveler,
)

router = APIRouter(prefix="/api/wiki", tags=["Italy trip wiki"])

ActivityStatus = Literal["option", "shortlisted", "selected", "booked", "done", "cancelled", "skipped"]
PaymentStatus = Literal["paid", "partial", "pending", "unknown", "partial_refund", "refunded"]
BookingStatus = Literal["booked", "estimate", "cancelled"]


class ActivityPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    location: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    geocode_precision: str | None = Field(default=None, max_length=40)
    description: str | None = None
    selection_status: ActivityStatus | None = None
    scheduled_date: str | None = None
    scheduled_time: str | None = None
    actual_cost: float | None = Field(default=None, ge=0)
    estimated_cost: float | None = Field(default=None, ge=0)
    notes: str | None = None
    user_url: str | None = None
    payment_status: PaymentStatus | None = None
    paid_amount: float | None = Field(default=None, ge=0)
    paid_date: str | None = None
    refunded_amount: float | None = Field(default=None, ge=0)
    refund_date: str | None = None


class ActivityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    stop_ordinal: int = Field(ge=0, le=8)
    location: str = ""
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    geocode_precision: str | None = Field(default=None, max_length=40)
    description: str = ""
    audience: str = "all"
    category: str = "sight"
    travel_scope: str = "base"
    estimated_cost: float | None = Field(default=None, ge=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    logistics: str = ""
    notes: str = ""
    url: str = ""
    map_url: str = ""
    image_url: str = ""
    selection_status: ActivityStatus = "option"
    scheduled_date: str | None = None
    scheduled_time: str = ""
    user_url: str = ""


class ActivityBulkPatch(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=500)
    action: Literal["hide", "restore"]


class CostPatch(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=300)
    category: str | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    amount: float | None = Field(default=None, ge=0)
    paid_amount: float | None = Field(default=None, ge=0)
    refunded_amount: float | None = Field(default=None, ge=0)
    booking_status: BookingStatus | None = None
    payment_status: PaymentStatus | None = None
    paid_date: str | None = None
    refund_date: str | None = None
    due_date: str | None = None
    note: str | None = None
    payment_reference: str | None = None
    url: str | None = None


class CostCreate(BaseModel):
    label: str = Field(min_length=1, max_length=300)
    category: str = "Other"
    amount: float | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    booking_status: BookingStatus = "estimate"
    payment_status: PaymentStatus = "unknown"
    paid_amount: float = Field(default=0, ge=0)
    refunded_amount: float = Field(default=0, ge=0)
    refund_date: str | None = None
    note: str = ""
    url: str = ""


class SettingsPatch(BaseModel):
    budget_usd: float = Field(ge=0)


class LegPatch(BaseModel):
    date: str | None = None
    from_stop: str | None = None
    to_stop: str | None = None
    mode: str | None = None
    departure_time: str | None = None
    arrival_time: str | None = None
    origin: str | None = None
    destination: str | None = None
    service: str | None = None
    booking_status: Literal["plan", "tobook", "booked"] | None = None
    confirmation: str | None = None
    party_size: int | None = Field(default=None, ge=1)
    cost: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    notes: str | None = None


class StayPatch(BaseModel):
    stop_slug: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=300)
    address: str | None = None
    checkin_date: str | None = None
    checkin_time: str | None = None
    checkout_date: str | None = None
    checkout_time: str | None = None
    booking_status: Literal["plan", "tobook", "booked"] | None = None
    confirmation: str | None = None
    cost_source_key: str | None = None
    notes: str | None = None


class DayPatch(BaseModel):
    weekday: str | None = None
    city: str | None = None
    stop_ordinal: int | None = Field(default=None, ge=0, le=8)
    note: str | None = None


class ItineraryItemCreate(BaseModel):
    day_id: int
    ordinal: int | None = Field(default=None, ge=0)
    time: str = ""
    kind: str = "do"
    status: str = "plan"
    title: str = Field(min_length=1, max_length=300)
    detail: str = ""


class ItineraryItemPatch(BaseModel):
    day_id: int | None = None
    ordinal: int | None = Field(default=None, ge=0)
    time: str | None = None
    kind: str | None = None
    status: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    detail: str | None = None


def _as_money(cents: int | None) -> float | None:
    return None if cents is None else round(cents / 100, 2)


def _to_cents(amount: float | None) -> int | None:
    return None if amount is None else round(amount * 100)


def _itinerary_item_dict(item: WikiItineraryItem) -> dict:
    return {
        "id": item.id, "day_id": item.day_id, "ordinal": item.ordinal,
        "time": item.time, "kind": item.kind, "status": item.status,
        "title": item.title, "detail": item.detail,
    }


def _activity_dict(
    item: ActivityOption,
    attachments: list[ActivityAttachment] | None = None,
    linked_cost: TripCost | None = None,
) -> dict:
    return {
        "id": item.id, "source_key": item.source_key, "stop_ordinal": item.stop_ordinal,
        "location": item.location, "region": item.region,
        "latitude": item.latitude, "longitude": item.longitude,
        "geocode_precision": item.geocode_precision, "title": item.title,
        "description": item.description,
        "audience": item.audience, "category": item.category,
        "travel_scope": item.travel_scope, "estimated_cost_text": item.estimated_cost_text,
        "estimated_cost": _as_money(item.estimated_cost_cents),
        "actual_cost": _as_money(item.actual_cost_cents), "currency": item.currency,
        "logistics": item.logistics, "url": item.url, "map_url": item.map_url,
        "image_url": item.image_url, "is_featured": item.is_featured,
        "source_details": item.source_details or {}, "notes": item.notes,
        "selection_status": item.selection_status, "scheduled_date": item.scheduled_date,
        "scheduled_time": item.scheduled_time, "user_url": item.user_url,
        "attachments": [{
            "id": attachment.id, "filename": attachment.filename,
            "content_type": attachment.content_type, "size_bytes": attachment.size_bytes,
            "download_url": f"/api/wiki/attachments/{attachment.id}",
        } for attachment in (attachments or [])],
        "cost": _cost_dict(linked_cost) if linked_cost else None,
        "is_archived": item.is_archived,
    }


def _cost_dict(item: TripCost) -> dict:
    net_paid_cents = max(0, item.paid_cents - item.refunded_cents)
    return {
        "id": item.id, "activity_id": item.activity_id,
        "source_key": item.source_key, "category": item.category,
        "label": item.label, "amount": _as_money(item.amount_cents), "currency": item.currency,
        "booking_status": item.booking_status, "payment_status": item.payment_status,
        "paid_amount": _as_money(item.paid_cents) or 0,
        "refunded_amount": _as_money(item.refunded_cents) or 0,
        "net_paid_amount": _as_money(net_paid_cents) or 0,
        "paid_date": item.paid_date, "refund_date": item.refund_date,
        "due_date": item.due_date, "payment_reference": item.payment_reference,
        "note": item.note, "url": item.url, "is_archived": item.is_archived,
    }


ACTIVE_ACTIVITY_STATUSES = {"selected", "booked", "done", "cancelled"}


def _get_activity_cost(session, activity: ActivityOption) -> TripCost | None:
    return session.scalar(select(TripCost).where(TripCost.activity_id == activity.id))


def _validate_activity_schedule(session, activity: ActivityOption) -> None:
    """Keep an activity date inside the itinerary stop it belongs to."""
    if not activity.scheduled_date:
        return
    stop = session.scalar(select(WikiStop).where(WikiStop.ordinal == activity.stop_ordinal))
    if stop is None:
        raise HTTPException(422, "activity is not assigned to a valid itinerary stop")
    if not stop.date_start <= activity.scheduled_date <= stop.date_end:
        raise HTTPException(
            422,
            f"{stop.name} activities must be scheduled from {stop.date_start} through {stop.date_end}",
        )


def _sync_cost_from_activity(
    session,
    activity: ActivityOption,
    fields: set[str],
    patch: ActivityPatch | None = None,
) -> TripCost | None:
    """Maintain the activity's ledger projection in the same transaction."""
    cost = _get_activity_cost(session, activity)
    if activity.selection_status not in ACTIVE_ACTIVITY_STATUSES:
        if cost and not cost.is_archived:
            cost.booking_status = "cancelled"
            # A research option can disappear from the catalogue, but money
            # already paid or refunded must remain visible in the ledger.
            has_payment_history = bool(cost.paid_cents or cost.refunded_cents)
            cost.is_archived = not (activity.selection_status == "skipped" and has_payment_history)
            cost.updated_at = datetime.now(UTC)
        return cost

    if cost is None:
        cost = TripCost(
            activity_id=activity.id,
            source_key=f"activity-{activity.id}",
            category="Activities",
            label=activity.title,
            currency=activity.currency,
            amount_cents=activity.actual_cost_cents if activity.actual_cost_cents is not None else activity.estimated_cost_cents,
            booking_status="booked" if activity.selection_status in {"booked", "done"} else "estimate",
            payment_status="pending" if activity.selection_status in {"booked", "done"} else "unknown",
            paid_cents=0,
            refunded_cents=0,
            note=activity.notes,
            url=activity.user_url or activity.url,
        )
        session.add(cost)
    else:
        cost.is_archived = False

    cost.label = activity.title
    cost.category = "Activities"
    cost.currency = activity.currency
    cost.amount_cents = activity.actual_cost_cents if activity.actual_cost_cents is not None else activity.estimated_cost_cents
    cost.booking_status = {
        "selected": "estimate", "booked": "booked", "done": "booked", "cancelled": "cancelled",
    }[activity.selection_status]
    if "notes" in fields:
        cost.note = activity.notes
    if "user_url" in fields:
        cost.url = activity.user_url or activity.url
    if patch:
        if "payment_status" in fields:
            cost.payment_status = patch.payment_status
        if "paid_amount" in fields:
            cost.paid_cents = _to_cents(patch.paid_amount) or 0
        if "paid_date" in fields:
            cost.paid_date = patch.paid_date or None
        if "refunded_amount" in fields:
            cost.refunded_cents = _to_cents(patch.refunded_amount) or 0
        if "refund_date" in fields:
            cost.refund_date = patch.refund_date or None
    if cost.refunded_cents > cost.paid_cents:
        raise HTTPException(422, "refunded amount cannot exceed the amount paid")
    cost.updated_at = datetime.now(UTC)
    return cost


def _sync_activity_from_cost(activity: ActivityOption, cost: TripCost, fields: set[str]) -> None:
    """Apply ledger edits back to the linked activity."""
    if "label" in fields:
        activity.title = cost.label
    if "currency" in fields:
        activity.currency = cost.currency
    if "amount" in fields or "booking_status" in fields:
        if cost.booking_status == "estimate":
            activity.estimated_cost_cents = cost.amount_cents
        else:
            activity.actual_cost_cents = cost.amount_cents
    if "booking_status" in fields:
        if cost.booking_status == "cancelled":
            activity.selection_status = "cancelled"
        elif cost.booking_status == "booked" and activity.selection_status != "done":
            activity.selection_status = "booked"
        elif cost.booking_status == "estimate":
            activity.selection_status = "selected"
    if "note" in fields:
        activity.notes = cost.note
    if "url" in fields:
        activity.user_url = cost.url
    activity.updated_at = datetime.now(UTC)


@router.get("")
def get_wiki() -> dict:
    with get_session() as session:
        setting = session.get(WikiSetting, "trip")
        stops = session.scalars(select(WikiStop).order_by(WikiStop.ordinal)).all()
        travelers = session.scalars(select(WikiTraveler).order_by(WikiTraveler.ordinal)).all()
        legs = session.scalars(select(WikiLeg).order_by(WikiLeg.ordinal)).all()
        stays = session.scalars(select(WikiStay).order_by(WikiStay.checkin_date)).all()
        days = session.scalars(select(WikiDay).order_by(WikiDay.date)).all()
        day_ids = [day.id for day in days]
        items = session.scalars(
            select(WikiItineraryItem)
            .where(WikiItineraryItem.day_id.in_(day_ids))
            .order_by(WikiItineraryItem.day_id, WikiItineraryItem.ordinal)
        ).all() if day_ids else []
        items_by_day: dict[int, list[dict]] = {}
        for item in items:
            items_by_day.setdefault(item.day_id, []).append(_itinerary_item_dict(item))
        activities = session.scalars(
            select(ActivityOption)
            .where(ActivityOption.is_archived.is_(False))
            .order_by(ActivityOption.stop_ordinal, ActivityOption.title)
        ).all()
        activity_ids = [activity.id for activity in activities]
        attachments = session.scalars(
            select(ActivityAttachment)
            .where(ActivityAttachment.activity_id.in_(activity_ids))
            .order_by(ActivityAttachment.created_at)
        ).all() if activity_ids else []
        attachments_by_activity: dict[int, list[ActivityAttachment]] = {}
        for attachment in attachments:
            attachments_by_activity.setdefault(attachment.activity_id, []).append(attachment)
        costs = session.scalars(
            select(TripCost).where(TripCost.is_archived.is_(False)).order_by(TripCost.category, TripCost.id)
        ).all()
        costs_by_activity = {cost.activity_id: cost for cost in costs if cost.activity_id is not None}

        return {
            "trip": setting.value if setting else {},
            "stops": [{
                "id": stop.id, "slug": stop.slug, "ordinal": stop.ordinal,
                "name": stop.name, "subtitle": stop.subtitle,
                "date_start": stop.date_start, "date_end": stop.date_end,
                "nights": stop.nights, "summary": stop.summary, "accent": stop.accent,
                "latitude": stop.latitude, "longitude": stop.longitude,
            } for stop in stops],
            "travelers": [{
                "id": traveler.id, "name": traveler.name, "role": traveler.role,
                "birth_date": traveler.birth_date, "notes": traveler.notes,
            } for traveler in travelers],
            "legs": [{
                "id": leg.id, "source_key": leg.source_key, "ordinal": leg.ordinal,
                "date": leg.date, "from_stop": leg.from_stop, "to_stop": leg.to_stop,
                "mode": leg.mode, "departure_time": leg.departure_time,
                "arrival_time": leg.arrival_time, "origin": leg.origin,
                "destination": leg.destination, "service": leg.service,
                "booking_status": leg.booking_status, "confirmation": leg.confirmation,
                "party_size": leg.party_size, "cost": _as_money(leg.cost_cents),
                "currency": leg.currency, "notes": leg.notes,
            } for leg in legs],
            "stays": [{
                "id": stay.id, "source_key": stay.source_key, "stop_slug": stay.stop_slug,
                "name": stay.name, "address": stay.address,
                "checkin_date": stay.checkin_date, "checkin_time": stay.checkin_time,
                "checkout_date": stay.checkout_date, "checkout_time": stay.checkout_time,
                "booking_status": stay.booking_status, "confirmation": stay.confirmation,
                "cost_source_key": stay.cost_source_key, "notes": stay.notes,
            } for stay in stays],
            "days": [{
                "id": day.id, "date": day.date, "weekday": day.weekday,
                "city": day.city, "stop_ordinal": day.stop_ordinal,
                "note": day.note, "items": items_by_day.get(day.id, []),
            } for day in days],
            "activities": [
                _activity_dict(item, attachments_by_activity.get(item.id), costs_by_activity.get(item.id))
                for item in activities
            ],
            "costs": [_cost_dict(item) for item in costs],
        }


@router.patch("/activities/bulk")
def patch_activities_bulk(patch: ActivityBulkPatch) -> dict:
    """Hide or restore multiple catalogue activities atomically."""
    activity_ids = list(dict.fromkeys(patch.ids))
    with get_session() as session:
        items = session.scalars(
            select(ActivityOption).where(
                ActivityOption.id.in_(activity_ids), ActivityOption.is_archived.is_(False),
            )
        ).all()
        by_id = {item.id: item for item in items}
        missing = [activity_id for activity_id in activity_ids if activity_id not in by_id]
        if missing:
            raise HTTPException(404, f"activities not found: {', '.join(map(str, missing))}")

        statuses: dict[int, str] = {}
        for activity_id in activity_ids:
            item = by_id[activity_id]
            cost = _get_activity_cost(session, item)
            if patch.action == "hide":
                item.selection_status = "skipped"
            else:
                has_payment_history = bool(cost and (cost.paid_cents or cost.refunded_cents))
                item.selection_status = "cancelled" if has_payment_history else "option"
            item.updated_at = datetime.now(UTC)
            _sync_cost_from_activity(session, item, {"selection_status"})
            statuses[item.id] = item.selection_status
        session.commit()
        return {"ids": activity_ids, "action": patch.action, "statuses": statuses}


@router.patch("/activities/{activity_id}")
def patch_activity(activity_id: int, patch: ActivityPatch) -> dict:
    with get_session() as session:
        item = session.get(ActivityOption, activity_id)
        if item is None or item.is_archived:
            raise HTTPException(404, "activity not found")
        fields = patch.model_fields_set
        if "title" in fields and patch.title is not None:
            item.title = patch.title
        if "location" in fields:
            item.location = patch.location or ""
        if "latitude" in fields:
            item.latitude = patch.latitude
        if "longitude" in fields:
            item.longitude = patch.longitude
        if "geocode_precision" in fields:
            item.geocode_precision = patch.geocode_precision or None
        if "description" in fields:
            item.description = patch.description or ""
        if "selection_status" in fields and patch.selection_status is not None:
            item.selection_status = patch.selection_status
        if "scheduled_date" in fields:
            item.scheduled_date = patch.scheduled_date or None
        if "scheduled_time" in fields:
            item.scheduled_time = patch.scheduled_time or ""
        if "actual_cost" in fields:
            item.actual_cost_cents = _to_cents(patch.actual_cost)
        if "estimated_cost" in fields:
            item.estimated_cost_cents = _to_cents(patch.estimated_cost)
        if "notes" in fields:
            item.notes = patch.notes or ""
        if "user_url" in fields:
            item.user_url = patch.user_url or ""
        if fields & {"scheduled_date", "selection_status"}:
            _validate_activity_schedule(session, item)
        item.updated_at = datetime.now(UTC)
        linked_cost = _sync_cost_from_activity(session, item, fields, patch)
        session.commit()
        session.refresh(item)
        if linked_cost:
            session.refresh(linked_cost)
        attachments = session.scalars(
            select(ActivityAttachment).where(ActivityAttachment.activity_id == item.id)
        ).all()
        return _activity_dict(item, attachments, linked_cost if linked_cost and not linked_cost.is_archived else None)


@router.delete("/activities/{activity_id}")
def delete_activity(activity_id: int) -> dict:
    """Archive an activity and its linked ledger row without erasing history."""
    with get_session() as session:
        item = session.get(ActivityOption, activity_id)
        if item is None or item.is_archived:
            raise HTTPException(404, "activity not found")
        item.is_archived = True
        item.updated_at = datetime.now(UTC)
        cost = _get_activity_cost(session, item)
        if cost:
            cost.is_archived = True
            cost.updated_at = datetime.now(UTC)
        session.commit()
        return {"id": activity_id, "archived": True}


@router.patch("/legs/{leg_id}")
def patch_leg(leg_id: int, patch: LegPatch) -> dict:
    with get_session() as session:
        leg = session.get(WikiLeg, leg_id)
        if leg is None:
            raise HTTPException(404, "leg not found")
        fields = patch.model_fields_set
        for field in (
            "date", "from_stop", "to_stop", "mode", "departure_time", "arrival_time",
            "origin", "destination", "service", "booking_status", "confirmation", "notes",
        ):
            if field in fields:
                setattr(leg, field, getattr(patch, field) or "")
        if "party_size" in fields and patch.party_size is not None:
            leg.party_size = patch.party_size
        if "cost" in fields:
            leg.cost_cents = _to_cents(patch.cost)
        if "currency" in fields and patch.currency is not None:
            leg.currency = patch.currency.upper()
        session.commit()
        return {"id": leg.id, "updated": True}


@router.patch("/stays/{stay_id}")
def patch_stay(stay_id: int, patch: StayPatch) -> dict:
    with get_session() as session:
        stay = session.get(WikiStay, stay_id)
        if stay is None:
            raise HTTPException(404, "stay not found")
        for field in patch.model_fields_set:
            setattr(stay, field, getattr(patch, field) or "")
        session.commit()
        return {"id": stay.id, "updated": True}


@router.patch("/days/{day_id}")
def patch_day(day_id: int, patch: DayPatch) -> dict:
    with get_session() as session:
        day = session.get(WikiDay, day_id)
        if day is None:
            raise HTTPException(404, "day not found")
        for field in patch.model_fields_set:
            value = getattr(patch, field)
            if field == "stop_ordinal" and value is None:
                continue
            setattr(day, field, value or "")
        session.commit()
        return {"id": day.id, "updated": True}


@router.post("/itinerary-items", status_code=201)
def create_itinerary_item(payload: ItineraryItemCreate) -> dict:
    with get_session() as session:
        if session.get(WikiDay, payload.day_id) is None:
            raise HTTPException(404, "day not found")
        next_ordinal = session.scalar(
            select(func.max(WikiItineraryItem.ordinal)).where(
                WikiItineraryItem.day_id == payload.day_id
            )
        )
        ordinal = payload.ordinal if payload.ordinal is not None else (
            0 if next_ordinal is None else next_ordinal + 1
        )
        if payload.ordinal is not None:
            later = session.scalars(
                select(WikiItineraryItem).where(
                    WikiItineraryItem.day_id == payload.day_id,
                    WikiItineraryItem.ordinal >= ordinal,
                )
            ).all()
            for item in later:
                item.ordinal += 1
        item = WikiItineraryItem(
            day_id=payload.day_id, ordinal=ordinal, time=payload.time,
            kind=payload.kind, status=payload.status, title=payload.title,
            detail=payload.detail,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return _itinerary_item_dict(item)


@router.patch("/itinerary-items/{item_id}")
def patch_itinerary_item(item_id: int, patch: ItineraryItemPatch) -> dict:
    with get_session() as session:
        item = session.get(WikiItineraryItem, item_id)
        if item is None:
            raise HTTPException(404, "itinerary item not found")
        if "day_id" in patch.model_fields_set:
            if patch.day_id is None or session.get(WikiDay, patch.day_id) is None:
                raise HTTPException(404, "day not found")
            item.day_id = patch.day_id
        for field in patch.model_fields_set - {"day_id"}:
            value = getattr(patch, field)
            if field == "ordinal" and value is None:
                continue
            setattr(item, field, value or "")
        session.commit()
        session.refresh(item)
        return _itinerary_item_dict(item)


@router.delete("/itinerary-items/{item_id}")
def delete_itinerary_item(item_id: int) -> dict:
    with get_session() as session:
        item = session.get(WikiItineraryItem, item_id)
        if item is None:
            raise HTTPException(404, "itinerary item not found")
        day_id = item.day_id
        ordinal = item.ordinal
        session.delete(item)
        later = session.scalars(
            select(WikiItineraryItem).where(
                WikiItineraryItem.day_id == day_id,
                WikiItineraryItem.ordinal > ordinal,
            )
        ).all()
        for later_item in later:
            later_item.ordinal -= 1
        session.commit()
        return {"id": item_id, "deleted": True}


@router.post("/activities", status_code=201)
def create_activity(payload: ActivityCreate) -> dict:
    with get_session() as session:
        stamp = int(datetime.now(UTC).timestamp() * 1000)
        item = ActivityOption(
            source_key=f"manual-{stamp}", stop_ordinal=payload.stop_ordinal,
            location=payload.location, latitude=payload.latitude, longitude=payload.longitude,
            geocode_precision=payload.geocode_precision,
            title=payload.title, description=payload.description,
            audience=payload.audience,
            category=payload.category, travel_scope=payload.travel_scope,
            estimated_cost_cents=_to_cents(payload.estimated_cost), currency=payload.currency.upper(),
            logistics=payload.logistics, notes=payload.notes, url=payload.url,
            map_url=payload.map_url, image_url=payload.image_url,
            selection_status=payload.selection_status, scheduled_date=payload.scheduled_date,
            scheduled_time=payload.scheduled_time, user_url=payload.user_url,
        )
        session.add(item)
        _validate_activity_schedule(session, item)
        session.flush()
        linked_cost = _sync_cost_from_activity(
            session,
            item,
            {"selection_status", "notes", "user_url", "estimated_cost"},
        )
        session.commit()
        session.refresh(item)
        if linked_cost:
            session.refresh(linked_cost)
        return _activity_dict(item, linked_cost=linked_cost)


@router.post("/activities/{activity_id}/attachments", status_code=201)
async def upload_activity_attachment(
    activity_id: int,
    attachment: Annotated[UploadFile, File()],
) -> dict:
    with get_session() as session:
        activity = session.get(ActivityOption, activity_id)
        if activity is None or activity.is_archived:
            raise HTTPException(404, "activity not found")
        content = await attachment.read(10 * 1024 * 1024 + 1)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(413, "attachment must be 10 MB or smaller")
        filename = Path(attachment.filename or "attachment").name
        storage_key = f"{uuid4().hex}-{filename}"
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        (upload_dir / storage_key).write_bytes(content)
        record = ActivityAttachment(
            activity_id=activity.id, filename=filename, storage_key=storage_key,
            content_type=attachment.content_type or "application/octet-stream",
            size_bytes=len(content),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return {
            "id": record.id, "filename": record.filename,
            "content_type": record.content_type, "size_bytes": record.size_bytes,
            "download_url": f"/api/wiki/attachments/{record.id}",
        }


@router.get("/attachments/{attachment_id}")
def download_activity_attachment(attachment_id: int):
    with get_session() as session:
        record = session.get(ActivityAttachment, attachment_id)
        if record is None:
            raise HTTPException(404, "attachment not found")
        path = Path(settings.upload_dir) / record.storage_key
        if not path.is_file():
            raise HTTPException(404, "attachment file is missing")
        return FileResponse(path, media_type=record.content_type, filename=record.filename)


@router.delete("/attachments/{attachment_id}")
def delete_activity_attachment(attachment_id: int) -> dict:
    with get_session() as session:
        record = session.get(ActivityAttachment, attachment_id)
        if record is None:
            raise HTTPException(404, "attachment not found")
        path = Path(settings.upload_dir) / record.storage_key
        if path.is_file():
            path.unlink()
        session.delete(record)
        session.commit()
        return {"id": attachment_id, "deleted": True}


@router.patch("/costs/{cost_id}")
def patch_cost(cost_id: int, patch: CostPatch) -> dict:
    with get_session() as session:
        item = session.get(TripCost, cost_id)
        if item is None or item.is_archived:
            raise HTTPException(404, "cost not found")
        fields = patch.model_fields_set
        if "label" in fields and patch.label is not None:
            item.label = patch.label
        if "category" in fields:
            item.category = patch.category or "Other"
        if "currency" in fields and patch.currency is not None:
            item.currency = patch.currency.upper()
        if "amount" in fields:
            item.amount_cents = _to_cents(patch.amount)
        if "paid_amount" in fields:
            item.paid_cents = _to_cents(patch.paid_amount) or 0
        if "refunded_amount" in fields:
            item.refunded_cents = _to_cents(patch.refunded_amount) or 0
        for field in ("booking_status", "payment_status"):
            if field in fields and getattr(patch, field) is not None:
                setattr(item, field, getattr(patch, field))
        for field in ("paid_date", "refund_date", "due_date"):
            if field in fields:
                setattr(item, field, getattr(patch, field) or None)
        for field in ("note", "payment_reference", "url"):
            if field in fields:
                setattr(item, field, getattr(patch, field) or "")
        if item.refunded_cents > item.paid_cents:
            raise HTTPException(422, "refunded amount cannot exceed the amount paid")
        item.updated_at = datetime.now(UTC)
        if item.activity_id is not None:
            activity = session.get(ActivityOption, item.activity_id)
            if activity and not activity.is_archived:
                _sync_activity_from_cost(activity, item, fields)
        session.commit()
        session.refresh(item)
        return _cost_dict(item)


@router.post("/costs", status_code=201)
def create_cost(payload: CostCreate) -> dict:
    with get_session() as session:
        if payload.refunded_amount > payload.paid_amount:
            raise HTTPException(422, "refunded amount cannot exceed the amount paid")
        stamp = int(datetime.now(UTC).timestamp() * 1000)
        item = TripCost(
            source_key=f"manual-{stamp}", category=payload.category, label=payload.label,
            amount_cents=_to_cents(payload.amount), currency=payload.currency.upper(),
            booking_status=payload.booking_status, payment_status=payload.payment_status,
            paid_cents=_to_cents(payload.paid_amount) or 0,
            refunded_cents=_to_cents(payload.refunded_amount) or 0,
            refund_date=payload.refund_date,
            note=payload.note, url=payload.url,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return _cost_dict(item)


@router.delete("/costs/{cost_id}")
def delete_cost(cost_id: int) -> dict:
    """Archive a ledger row; linked activities are archived with it."""
    with get_session() as session:
        item = session.get(TripCost, cost_id)
        if item is None or item.is_archived:
            raise HTTPException(404, "cost not found")
        item.is_archived = True
        item.updated_at = datetime.now(UTC)
        if item.activity_id is not None:
            activity = session.get(ActivityOption, item.activity_id)
            if activity:
                activity.is_archived = True
                activity.updated_at = datetime.now(UTC)
        session.commit()
        return {"id": cost_id, "archived": True}


@router.patch("/settings")
def patch_settings(patch: SettingsPatch) -> dict:
    with get_session() as session:
        setting = session.get(WikiSetting, "trip")
        if setting is None:
            raise HTTPException(404, "trip settings not found")
        setting.value = {**setting.value, "budget_usd": patch.budget_usd}
        setting.updated_at = datetime.now(UTC)
        session.commit()
        return setting.value
