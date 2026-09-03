from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Config(Base):
    __tablename__ = "config"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    budget_party_total: Mapped[int]
    currency: Mapped[str] = mapped_column(default="USD")
    passengers: Mapped[dict[str, int]] = mapped_column(JSON)
    structures: Mapped[list[str]] = mapped_column(JSON)
    blackout_ranges: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    validation_tolerance_pct: Mapped[int] = mapped_column(default=15)
    validation_top_n: Mapped[int] = mapped_column(default=5)
    envelope_long_gap_days: Mapped[int] = mapped_column(default=30)
    # Preferences (bookended scale per friction axis, global + per-leg) and
    # user-owned cost assumptions feed the landed-cost ranking pipeline.
    # Serialised as JSON because their shape changes more often than the
    # rest of the schema (axis additions, new override types).
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    cost_assumptions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)


class Leg(Base):
    __tablename__ = "leg"

    id: Mapped[int] = mapped_column(primary_key=True)
    config_id: Mapped[int] = mapped_column(ForeignKey("config.id"))
    ordinal: Mapped[int]
    origins: Mapped[list[str]] = mapped_column(JSON)
    destinations: Mapped[list[str]] = mapped_column(JSON)
    date_anchor: Mapped[str]
    window_days: Mapped[int] = mapped_column(default=7)
    sampling_strategy: Mapped[str] = mapped_column(default="anchor,+/-3,+/-7")
    return_date_anchor: Mapped[str | None] = mapped_column(default=None)
    return_window_days: Mapped[int | None] = mapped_column(default=None)
    return_sampling_strategy: Mapped[str | None] = mapped_column(default=None)

    @property
    def is_round_trip(self) -> bool:
        return self.return_date_anchor is not None


class Run(Base):
    __tablename__ = "run"

    id: Mapped[int] = mapped_column(primary_key=True)
    config_id: Mapped[int] = mapped_column(ForeignKey("config.id"))
    config_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(default="PENDING")
    started_at: Mapped[datetime] = mapped_column(default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(default=None)
    scraper_calls: Mapped[int] = mapped_column(default=0)
    serpapi_calls: Mapped[int] = mapped_column(default=0)
    serpapi_quota_remaining: Mapped[int | None] = mapped_column(default=None)
    error: Mapped[str | None] = mapped_column(default=None)
    # Per-axis count of itineraries removed by HARD NO filters during scoring.
    filtered_out_count_by_axis: Mapped[dict[str, int]] = mapped_column(JSON, default=dict)


class Fare(Base):
    __tablename__ = "fare"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("run.id"), index=True)
    leg_ordinal: Mapped[int]
    structure: Mapped[str]
    origin: Mapped[str]
    destination: Mapped[str]
    date: Mapped[str]
    return_date: Mapped[str | None] = mapped_column(default=None)
    carrier: Mapped[str] = mapped_column(default="")
    price_per_pax: Mapped[int]
    price_party: Mapped[int]
    currency: Mapped[str] = mapped_column(default="USD")
    stops: Mapped[int] = mapped_column(default=0)
    duration_minutes: Mapped[int] = mapped_column(default=0)
    source: Mapped[str]
    verification_status: Mapped[str]
    passengers_queried: Mapped[int]
    fetched_at: Mapped[datetime] = mapped_column(default=utcnow)
    ttl_seconds: Mapped[int] = mapped_column(default=86400)
    flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str | None] = mapped_column(default=None)


class Itinerary(Base):
    __tablename__ = "itinerary"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("run.id"), index=True)
    structure: Mapped[str]
    total_party_price: Mapped[int]
    currency: Mapped[str] = mapped_column(default="USD")
    verification_status: Mapped[str]
    fare_ids: Mapped[list[int]] = mapped_column(JSON)
    gateway: Mapped[str | None] = mapped_column(default=None)
    train_to_venice: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    rank: Mapped[int] = mapped_column(default=0)
    # Landed cost (validated airfare + ground transfer + any lodging) becomes
    # the ranking key per `landed-cost-model`. None until the landed-cost
    # calculator has run (FAILED itineraries stay None).
    landed_cost: Mapped[int | None] = mapped_column(default=None)
    cost_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    friction_attributes: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    preference_explanations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)


class Trip(Base):
    """A trip is the persistent unit the SPA works in: it owns one Config,
    many Runs, one Shortlist, and free-form Notes. Soft-deletable with a
    7-day grace window (per web-api spec)."""

    __tablename__ = "trip"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    config_id: Mapped[int] = mapped_column(ForeignKey("config.id"))
    notes: Mapped[str] = mapped_column(default="")
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)


class ShortlistItem(Base):
    """Immutable snapshot of an itinerary saved to a trip's shortlist.

    `snapshot` is a frozen JSON copy of the itinerary at save-time so future
    edits to the originating run or the gateway-transfer table do NOT mutate
    the saved view (per web-api spec).
    """

    __tablename__ = "shortlist_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trip.id"), index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("run.id"))
    itinerary_id: Mapped[int] = mapped_column(ForeignKey("itinerary.id"))
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    notes: Mapped[str] = mapped_column(default="")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    order_index: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


# Italy 2026 operational wiki -------------------------------------------------
#
# These tables deliberately live beside the earlier fare-search models.  The
# fare engine remains available for historical work, while the public app now
# reads and writes the family trip's durable, human-maintained facts here.


class WikiSetting(Base):
    __tablename__ = "wiki_setting"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)


class WikiStop(Base):
    __tablename__ = "wiki_stop"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    ordinal: Mapped[int]
    name: Mapped[str]
    subtitle: Mapped[str] = mapped_column(default="")
    date_start: Mapped[str]
    date_end: Mapped[str]
    nights: Mapped[int]
    summary: Mapped[str] = mapped_column(Text, default="")
    accent: Mapped[str] = mapped_column(default="#173F5F")
    latitude: Mapped[float | None] = mapped_column(default=None)
    longitude: Mapped[float | None] = mapped_column(default=None)


class WikiTraveler(Base):
    __tablename__ = "wiki_traveler"

    id: Mapped[int] = mapped_column(primary_key=True)
    ordinal: Mapped[int]
    name: Mapped[str]
    role: Mapped[str] = mapped_column(default="family")
    birth_date: Mapped[str | None] = mapped_column(default=None)
    notes: Mapped[str] = mapped_column(Text, default="")


class WikiLeg(Base):
    __tablename__ = "wiki_leg"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_key: Mapped[str] = mapped_column(unique=True, index=True)
    ordinal: Mapped[int]
    date: Mapped[str]
    from_stop: Mapped[str]
    to_stop: Mapped[str]
    mode: Mapped[str]
    departure_time: Mapped[str] = mapped_column(default="")
    arrival_time: Mapped[str] = mapped_column(default="")
    origin: Mapped[str] = mapped_column(default="")
    destination: Mapped[str] = mapped_column(default="")
    service: Mapped[str] = mapped_column(default="")
    booking_status: Mapped[str] = mapped_column(default="plan")
    confirmation: Mapped[str] = mapped_column(default="")
    party_size: Mapped[int] = mapped_column(default=6)
    cost_cents: Mapped[int | None] = mapped_column(default=None)
    currency: Mapped[str] = mapped_column(default="EUR")
    notes: Mapped[str] = mapped_column(Text, default="")


class WikiStay(Base):
    __tablename__ = "wiki_stay"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_key: Mapped[str] = mapped_column(unique=True, index=True)
    stop_slug: Mapped[str] = mapped_column(index=True)
    name: Mapped[str]
    address: Mapped[str] = mapped_column(default="")
    checkin_date: Mapped[str]
    checkin_time: Mapped[str] = mapped_column(default="")
    checkout_date: Mapped[str]
    checkout_time: Mapped[str] = mapped_column(default="")
    booking_status: Mapped[str] = mapped_column(default="booked")
    confirmation: Mapped[str] = mapped_column(default="")
    cost_source_key: Mapped[str] = mapped_column(default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class WikiDay(Base):
    __tablename__ = "wiki_day"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(unique=True, index=True)
    weekday: Mapped[str]
    city: Mapped[str]
    stop_ordinal: Mapped[int]
    note: Mapped[str] = mapped_column(Text, default="")


class WikiItineraryItem(Base):
    __tablename__ = "wiki_itinerary_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("wiki_day.id"), index=True)
    ordinal: Mapped[int]
    time: Mapped[str] = mapped_column(default="")
    kind: Mapped[str]
    status: Mapped[str]
    title: Mapped[str]
    detail: Mapped[str] = mapped_column(Text, default="")


class ActivityOption(Base):
    __tablename__ = "activity_option"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_key: Mapped[str] = mapped_column(unique=True, index=True)
    stop_ordinal: Mapped[int]
    location: Mapped[str]
    region: Mapped[str] = mapped_column(default="")
    latitude: Mapped[float | None] = mapped_column(default=None)
    longitude: Mapped[float | None] = mapped_column(default=None)
    geocode_precision: Mapped[str | None] = mapped_column(default=None)
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text, default="")
    audience: Mapped[str] = mapped_column(default="all")
    category: Mapped[str] = mapped_column(default="sight")
    travel_scope: Mapped[str] = mapped_column(default="base")
    estimated_cost_text: Mapped[str] = mapped_column(default="")
    estimated_cost_cents: Mapped[int | None] = mapped_column(default=None)
    actual_cost_cents: Mapped[int | None] = mapped_column(default=None)
    currency: Mapped[str] = mapped_column(default="EUR")
    logistics: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(default="")
    map_url: Mapped[str] = mapped_column(default="")
    image_url: Mapped[str] = mapped_column(Text, default="")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    source_details: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str] = mapped_column(Text, default="")
    selection_status: Mapped[str] = mapped_column(default="option")
    scheduled_date: Mapped[str | None] = mapped_column(default=None)
    scheduled_time: Mapped[str] = mapped_column(default="")
    user_url: Mapped[str] = mapped_column(default="")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)


class ActivityAttachment(Base):
    __tablename__ = "activity_attachment"

    id: Mapped[int] = mapped_column(primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activity_option.id"), index=True)
    filename: Mapped[str]
    storage_key: Mapped[str] = mapped_column(unique=True)
    content_type: Mapped[str] = mapped_column(default="application/octet-stream")
    size_bytes: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class TripCost(Base):
    __tablename__ = "trip_cost"

    id: Mapped[int] = mapped_column(primary_key=True)
    activity_id: Mapped[int | None] = mapped_column(
        ForeignKey("activity_option.id", ondelete="SET NULL"), unique=True, index=True, default=None
    )
    source_key: Mapped[str] = mapped_column(unique=True, index=True)
    category: Mapped[str]
    label: Mapped[str]
    amount_cents: Mapped[int | None] = mapped_column(default=None)
    currency: Mapped[str] = mapped_column(default="USD")
    booking_status: Mapped[str] = mapped_column(default="estimate")
    payment_status: Mapped[str] = mapped_column(default="unknown")
    paid_cents: Mapped[int] = mapped_column(default=0)
    refunded_cents: Mapped[int] = mapped_column(default=0)
    paid_date: Mapped[str | None] = mapped_column(default=None)
    refund_date: Mapped[str | None] = mapped_column(default=None)
    due_date: Mapped[str | None] = mapped_column(default=None)
    payment_reference: Mapped[str] = mapped_column(Text, default="")
    note: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(default="")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)
