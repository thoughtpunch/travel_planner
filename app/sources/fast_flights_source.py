"""fast-flights adapter. Returns LEAD-only fares.

CRITICAL: per design.md Decision 1, every fare from this source is a LEAD
regardless of price or apparent seat availability. The scraper returns Google
Flights' display fare, which collapses at party size.
"""

from __future__ import annotations

from fast_flights import FlightQuery, Passengers, create_query, get_flights
from fast_flights.parser import FlightsError

from ..enums import Source, VerificationStatus
from .base import FareOffer, FareQuery, SourceError


class FastFlightsSource:
    name = Source.FAST_FLIGHTS

    def __init__(self, currency: str = "USD") -> None:
        self.currency = currency

    def search(self, query: FareQuery) -> list[FareOffer]:
        try:
            flight_queries = [
                FlightQuery(
                    date=query.date,
                    from_airport=query.origin,
                    to_airport=query.destination,
                )
            ]
            if query.is_round_trip:
                # Round-trip query — add the return leg. Google Flights then
                # returns RT TOTAL prices (per pax) in the `price` field.
                flight_queries.append(
                    FlightQuery(
                        date=query.return_date,
                        from_airport=query.destination,
                        to_airport=query.origin,
                    )
                )
            q = create_query(
                flights=flight_queries,
                seat="economy",
                trip="round-trip" if query.is_round_trip else "one-way",
                passengers=Passengers(
                    adults=query.adults,
                    children=query.children,
                    infants_in_seat=query.infants_in_seat,
                    infants_on_lap=query.infants_on_lap,
                ),
                language="en-US",
                currency=self.currency,
            )
            results = get_flights(q)
        except FlightsError as e:
            raise SourceError(f"fast-flights parse error: {e}") from e
        except Exception as e:
            raise SourceError(f"fast-flights transport/unknown error: {e}") from e

        offers: list[FareOffer] = []
        for r in results:
            segments = getattr(r, "flights", []) or []
            first = segments[0] if segments else None
            stops = max(0, len(segments) - 1)
            duration = sum(getattr(s, "duration", 0) or 0 for s in segments)
            carriers = getattr(r, "airlines", []) or []
            carrier = ", ".join(carriers) if carriers else (getattr(first, "plane_type", "") or "")

            offers.append(
                FareOffer(
                    origin=query.origin,
                    destination=query.destination,
                    date=query.date,
                    return_date=query.return_date,
                    carrier=carrier,
                    price_per_pax=int(getattr(r, "price", 0) or 0),
                    currency=self.currency,
                    stops=stops,
                    duration_minutes=duration,
                    source=Source.FAST_FLIGHTS,
                    verification_status=VerificationStatus.LEAD,
                    passengers_queried=query.passenger_count,
                    raw={"type": getattr(r, "type", None)},
                )
            )
        return offers
