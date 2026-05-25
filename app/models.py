from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Config(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    budget_party_total: int
    currency: str = "USD"
    passengers: dict[str, int] = Field(sa_column=Column(JSON))
    structures: list[str] = Field(sa_column=Column(JSON))
    blackout_ranges: list[dict[str, str]] = Field(default_factory=list, sa_column=Column(JSON))
    validation_tolerance_pct: int = 15
    validation_top_n: int = 5
    envelope_long_gap_days: int = 30
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Leg(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    config_id: int = Field(foreign_key="config.id")
    ordinal: int
    origins: list[str] = Field(sa_column=Column(JSON))
    destinations: list[str] = Field(sa_column=Column(JSON))
    date_anchor: str
    window_days: int = 7
    sampling_strategy: str = "anchor,+/-3,+/-7"
    # When any return_* is set, this leg is a round-trip leg: every
    # (outbound × return) date pair is swept as one RT fare query.
    return_date_anchor: str | None = None
    return_window_days: int | None = None
    return_sampling_strategy: str | None = None

    @property
    def is_round_trip(self) -> bool:
        return self.return_date_anchor is not None


class Run(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    config_id: int = Field(foreign_key="config.id")
    config_snapshot: dict[str, Any] = Field(sa_column=Column(JSON))
    status: str = "PENDING"
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None
    scraper_calls: int = 0
    serpapi_calls: int = 0
    serpapi_quota_remaining: int | None = None
    error: str | None = None


class Fare(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id", index=True)
    leg_ordinal: int
    structure: str
    origin: str
    destination: str
    date: str
    # Set when this fare represents a round-trip; price_per_pax is then the
    # round-trip total per passenger.
    return_date: str | None = None
    carrier: str = ""
    price_per_pax: int
    price_party: int
    currency: str = "USD"
    stops: int = 0
    duration_minutes: int = 0
    source: str
    verification_status: str
    passengers_queried: int
    fetched_at: datetime = Field(default_factory=utcnow)
    ttl_seconds: int = 86400
    flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    notes: str | None = None


class Itinerary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id", index=True)
    structure: str
    total_party_price: int
    currency: str = "USD"
    verification_status: str
    fare_ids: list[int] = Field(sa_column=Column(JSON))
    gateway: str | None = None
    train_to_venice: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    rank: int = 0
