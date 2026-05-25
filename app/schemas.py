from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LegPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ordinal: int
    origins: list[str]
    destinations: list[str]
    date_anchor: str
    window_days: int = 7
    sampling_strategy: str = "anchor,+/-3,+/-7"
    return_date_anchor: str | None = None
    return_window_days: int | None = None
    return_sampling_strategy: str | None = None


class ConfigPayload(BaseModel):
    name: str
    budget_party_total: int
    currency: str = "USD"
    passengers: dict[str, int] = Field(default_factory=lambda: {"adults": 1})
    structures: list[str] = Field(default_factory=lambda: ["A"])
    blackout_ranges: list[dict[str, str]] = Field(default_factory=list)
    validation_tolerance_pct: int = 15
    validation_top_n: int = 5
    envelope_long_gap_days: int = 30
    legs: list[LegPayload]


class ConfigOut(ConfigPayload):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    config_id: int
    status: str
    started_at: datetime
    finished_at: datetime | None
    scraper_calls: int
    serpapi_calls: int
    serpapi_quota_remaining: int | None
    error: str | None


class FareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    leg_ordinal: int
    structure: str
    origin: str
    destination: str
    date: str
    return_date: str | None = None
    carrier: str
    price_per_pax: int
    price_party: int
    currency: str
    stops: int
    duration_minutes: int
    source: str
    verification_status: str
    fetched_at: datetime


class ItineraryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    structure: str
    total_party_price: int
    currency: str
    verification_status: str
    gateway: str | None
    train_to_venice: dict[str, Any] | None
    flags: list[str]
    rank: int
    fares: list[FareOut]


class FailedFareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    leg_ordinal: int
    origin: str
    destination: str
    date: str
    return_date: str | None = None
    source: str
    reason: str | None = None
    fetched_at: datetime


class ResultsOut(BaseModel):
    run: RunOut
    itineraries: list[ItineraryOut]
    budget_verdict: dict[str, Any]
    quota: dict[str, Any]
    structures: dict[str, str] = Field(default_factory=dict)
    failed_query_count: int = 0
    failed_fares: list[FailedFareOut] = Field(default_factory=list)


class QuotaOut(BaseModel):
    ceiling: int
    used_this_month: int
    remaining: int
