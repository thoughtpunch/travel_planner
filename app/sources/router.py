"""Source router: scraper-first sweep with SerpAPI fallback.

Per design.md Decision 2, SerpAPI is co-primary, not rare. The router calls
fast-flights first; if it raises, returns empty, or times out, it falls back
to SerpAPI. Empty scraper results are SOFT failures — they trigger fallback
and are NEVER recorded as a confirmed "no flights".

Validation queries should call SerpAPI directly, not through this router.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..enums import Source, VerificationStatus
from .base import FareOffer, FareQuery, NoFallbackAvailable, QuotaExceeded, SourceError
from .fast_flights_source import FastFlightsSource
from .serpapi_source import SerpApiSource


@dataclass
class RoutedResult:
    offers: list[FareOffer]
    served_by: Source | None
    fallback_used: bool
    error: str | None = None


class SourceRouter:
    def __init__(
        self,
        primary: FastFlightsSource,
        fallback: SerpApiSource | None,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    def sweep(self, query: FareQuery) -> RoutedResult:
        # Sweep: scraper-first; treat empty/exception as soft failure.
        try:
            offers = self.primary.search(query)
            if offers:
                return RoutedResult(offers=offers, served_by=Source.FAST_FLIGHTS, fallback_used=False)
            # empty: soft failure
        except SourceError as e:
            primary_error = str(e)
        else:
            primary_error = "empty result set"

        if self.fallback is None:
            return RoutedResult(
                offers=[_failed_marker(query, reason="no_fallback_available")],
                served_by=None,
                fallback_used=False,
                error=f"primary failed ({primary_error}); no fallback configured",
            )

        try:
            offers = self.fallback.search(query)
            return RoutedResult(offers=offers, served_by=Source.SERPAPI, fallback_used=True)
        except QuotaExceeded as e:
            return RoutedResult(
                offers=[_skipped_quota_marker(query)],
                served_by=None,
                fallback_used=True,
                error=str(e),
            )
        except SourceError as e:
            return RoutedResult(
                offers=[_failed_marker(query, reason=f"fallback_failed: {e}")],
                served_by=None,
                fallback_used=True,
                error=f"primary failed ({primary_error}); fallback failed ({e})",
            )


def _skipped_quota_marker(query: FareQuery) -> FareOffer:
    return FareOffer(
        origin=query.origin,
        destination=query.destination,
        date=query.date,
        carrier="",
        price_per_pax=0,
        currency="USD",
        stops=0,
        duration_minutes=0,
        source=Source.SERPAPI,
        verification_status=VerificationStatus.SKIPPED_QUOTA,
        passengers_queried=query.passenger_count,
        raw={},
    )


def _failed_marker(query: FareQuery, reason: str) -> FareOffer:
    """FAILED marker offer — persisted as a Fare row so the audit trail
    records the failure rather than silently dropping the query."""
    return FareOffer(
        origin=query.origin,
        destination=query.destination,
        date=query.date,
        return_date=query.return_date,
        carrier="",
        price_per_pax=0,
        currency="USD",
        stops=0,
        duration_minutes=0,
        source=Source.FAST_FLIGHTS,
        verification_status=VerificationStatus.FAILED,
        passengers_queried=query.passenger_count,
        raw={"reason": reason},
    )


__all__ = ["SourceRouter", "RoutedResult", "NoFallbackAvailable"]
