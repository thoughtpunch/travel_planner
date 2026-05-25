"""SerpAPI Google Flights adapter — co-primary, authoritative for validation.

Uses the official `serpapi` Python SDK (https://github.com/serpapi/serpapi-python).
SDK error mapping:
- `serpapi.HTTPError` with `status_code == 429` → QuotaExceeded (their throttle)
- `serpapi.HTTPError` with `status_code == 401` → SourceError("auth")
- other `HTTPError`, `TimeoutError`, `HTTPConnectionError` → SourceError

Used both as fallback when fast-flights fails AND as the validation source
re-querying at full party size. SerpAPI's `google_flights` engine returns
itineraries with the requested adult count, so prices reflect the true party
where availability exists.

Docs: https://serpapi.com/google-flights-api

Price semantics: SerpAPI's `price` field is the TOTAL ticket price for the
requested passenger count in the requested currency. We divide by passenger
count to store `price_per_pax` consistently with the fast-flights adapter
(which returns Google Flights' display price — a per-pax figure).
"""

from __future__ import annotations

import serpapi

from ..enums import Source, VerificationStatus
from .base import FareOffer, FareQuery, QuotaExceeded, SourceError
from .quota import QuotaTracker


class SerpApiSource:
    name = Source.SERPAPI

    def __init__(
        self,
        api_key: str,
        quota: QuotaTracker,
        currency: str = "USD",
        timeout: float = 30.0,
        deep_search: bool = False,
        client: serpapi.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.quota = quota
        self.currency = currency
        self.timeout = timeout
        self.deep_search = deep_search
        self._client = client or serpapi.Client(api_key=api_key, timeout=timeout)

    def search(self, query: FareQuery) -> list[FareOffer]:
        if not self.api_key:
            raise SourceError("SerpAPI key not configured")

        self.quota.reserve(1)

        params: dict = {
            "engine": "google_flights",
            "departure_id": query.origin,
            "arrival_id": query.destination,
            "outbound_date": query.date,
            "currency": self.currency,
            "hl": "en",
            "gl": "us",
            "adults": query.adults,
            "children": query.children,
            "infants_in_seat": query.infants_in_seat,
            "infants_on_lap": query.infants_on_lap,
            "stops": 0,  # 0 = any
        }
        if query.is_round_trip:
            params["type"] = 1  # round-trip — price returned is RT total for party
            params["return_date"] = query.return_date
        else:
            params["type"] = 2  # one-way
        if self.deep_search:
            params["deep_search"] = True

        try:
            payload = self._client.search(params)
        except serpapi.HTTPError as e:
            status = getattr(e, "status_code", None)
            if status == 429:
                # SerpAPI throttle or out-of-monthly-quota — treat as our quota
                # exceeded so callers degrade gracefully.
                raise QuotaExceeded(f"SerpAPI 429: {e}") from e
            if status == 401:
                raise SourceError(f"SerpAPI auth (401): check SERPAPI_KEY") from e
            raise SourceError(f"SerpAPI HTTP {status}: {e}") from e
        except serpapi.TimeoutError as e:
            raise SourceError(f"SerpAPI timeout: {e}") from e
        except serpapi.HTTPConnectionError as e:
            raise SourceError(f"SerpAPI connection error: {e}") from e

        if isinstance(payload, dict) and "error" in payload:
            raise SourceError(f"SerpAPI error: {payload['error']}")

        offers: list[FareOffer] = []
        for bucket_key in ("best_flights", "other_flights"):
            for item in payload.get(bucket_key, []) or []:
                offer = _parse_item(item, query, self.currency)
                if offer is not None:
                    offers.append(offer)
        return offers


def _parse_item(item: dict, query: FareQuery, currency: str) -> FareOffer | None:
    flights = item.get("flights") or []
    if not flights:
        return None
    first = flights[0]
    last = flights[-1]
    carriers = sorted({(f.get("airline") or "") for f in flights if f.get("airline")})
    carrier = ", ".join(carriers)
    price = item.get("price")
    if not isinstance(price, (int, float)):
        return None
    # SerpAPI's `price` is the TOTAL for the requested passenger count.
    pax = max(1, query.passenger_count)
    per_pax = int(round(price / pax))
    stops = max(0, len(flights) - 1)
    duration = item.get("total_duration") or sum(f.get("duration", 0) or 0 for f in flights)

    return FareOffer(
        origin=(first.get("departure_airport") or {}).get("id", query.origin),
        destination=(last.get("arrival_airport") or {}).get("id", query.destination),
        date=query.date,
        return_date=query.return_date,
        carrier=carrier,
        price_per_pax=per_pax,
        currency=currency,
        stops=stops,
        duration_minutes=int(duration or 0),
        source=Source.SERPAPI,
        # Adapter always emits LEAD; validator promotes to VALIDATED after the
        # tolerance check. This keeps "fare returned" separate from "fare
        # confirmed within tolerance of the sweep lead".
        verification_status=VerificationStatus.LEAD,
        passengers_queried=query.passenger_count,
        raw={"total_price": price, "type": item.get("type")},
    )


__all__ = ["SerpApiSource", "QuotaExceeded"]
