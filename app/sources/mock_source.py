"""Mock fare source for development + browser-driven testing.

Returns deterministic seeded offers per FareQuery so the SPA can be
exercised end-to-end without touching fli, SerpAPI, or any network.

Enable by setting `PRIMARY_SOURCE=mock` in `.env`. Quietly disabled in
production by virtue of the env var defaulting to `fli`.
"""

from __future__ import annotations

import hashlib

from ..enums import Source, VerificationStatus
from .base import FareOffer, FareQuery

# A small carrier pool with stable identifiers so seeded prices stay stable
# across runs for the same (route, date) pair.
_CARRIERS = ["UA", "AA", "LH", "AF", "BA", "DL"]


def _seed(*parts: str | int) -> int:
    """Stable 32-bit hash from the inputs — deterministic across runs."""
    h = hashlib.sha256(":".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16)


class MockSource:
    """Deterministic seeded primary source.

    Generates 3 offers per query with varied carriers, prices, layovers, and
    arrival times so the SPA's friction columns, soft-band reorder, and HARD
    NO filters all have something to chew on.
    """

    name = Source.MOCK

    def __init__(self, currency: str = "USD") -> None:
        self.currency = currency

    def search(self, query: FareQuery) -> list[FareOffer]:
        base = 600 + (_seed(query.origin, query.destination, query.date) % 600)
        offers: list[FareOffer] = []
        for i in range(3):
            carrier = _CARRIERS[_seed(query.origin, query.destination, i) % len(_CARRIERS)]
            price = base + i * 75
            # Vary stops + layover so friction columns show variation.
            stops = i  # 0, 1, 2
            layover_minutes = 0 if i == 0 else 120 + i * 90  # 0, 210, 300
            # Half the offers arrive late enough to be red-eye-adjacent so the
            # avoid-red-eye preference has something to demote.
            arrival = "23:45" if (i == 2 and (_seed(query.origin, query.destination) % 2)) else "14:30"
            raw = {
                "arrival_local_time": arrival,
                "layovers": [{"duration_minutes": layover_minutes}] if layover_minutes else [],
                "carrier": carrier,
                "mock": True,
            }
            offers.append(FareOffer(
                origin=query.origin,
                destination=query.destination,
                date=query.date,
                return_date=query.return_date,
                carrier=carrier,
                price_per_pax=price,
                currency=self.currency,
                stops=stops,
                duration_minutes=540 + i * 60,
                source=Source.MOCK,
                verification_status=VerificationStatus.LEAD,
                passengers_queried=query.passenger_count,
                raw=raw,
            ))
        return offers


__all__ = ["MockSource"]
