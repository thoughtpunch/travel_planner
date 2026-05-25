from dataclasses import dataclass, field
from typing import Protocol

from ..enums import Source, VerificationStatus


@dataclass
class FareOffer:
    origin: str
    destination: str
    date: str
    carrier: str
    price_per_pax: int
    currency: str
    stops: int
    duration_minutes: int
    source: Source
    verification_status: VerificationStatus
    passengers_queried: int
    # When set, this offer represents a ROUND-TRIP fare. `date` is the
    # outbound; `return_date` is the return. `price_per_pax` is then the
    # round-trip total per passenger. Otherwise (None) it's a one-way.
    return_date: str | None = None
    raw: dict = field(default_factory=dict)

    @property
    def is_round_trip(self) -> bool:
        return self.return_date is not None


@dataclass
class FareQuery:
    origin: str
    destination: str
    date: str
    adults: int
    children: int = 0
    infants_in_seat: int = 0
    infants_on_lap: int = 0
    # When set, query is for a round-trip from `date` to `return_date`.
    return_date: str | None = None

    @property
    def passenger_count(self) -> int:
        return self.adults + self.children + self.infants_in_seat + self.infants_on_lap

    @property
    def is_round_trip(self) -> bool:
        return self.return_date is not None


class FareSource(Protocol):
    name: Source

    def search(self, query: FareQuery) -> list[FareOffer]: ...


class SourceError(RuntimeError):
    """Base class for adapter-level failures (transport, parse, schema)."""


class NoFallbackAvailable(SourceError):
    """Raised when the scraper has failed and there is no configured fallback."""


class QuotaExceeded(SourceError):
    """Raised when a SerpAPI call would exceed the configured monthly ceiling."""
