from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, ForeignKey
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
