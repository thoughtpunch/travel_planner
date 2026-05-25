"""fli adapter. Returns LEAD-only fares.

Per design.md Decision 1 (and unchanged by the migrate-fare-search-to-fli
change), every fare from this source is a LEAD. fli hits Google Flights'
internal RPC and returns display fares; it cannot confirm seats at the
configured party size, so the SerpAPI validation pass at full party
remains the only path to VALIDATED.
"""

from __future__ import annotations

from fli.models import (
    FlightResult,
    FlightSearchFilters,
    FlightSegment,
    PassengerInfo,
    SeatType,
    TripType,
)
from fli.models.airport import Airport
from fli.search import SearchFlights
from fli.search.client import (
    SearchClientError,
    SearchConnectionError,
    SearchHTTPError,
    SearchTimeoutError,
)
from fli.search.flights import SearchParseError

from ..enums import Source, VerificationStatus
from .base import FareOffer, FareQuery, SourceError


class FliSource:
    name = Source.FLI

    def __init__(self, currency: str = "USD") -> None:
        self.currency = currency
        self._client = SearchFlights()

    def search(self, query: FareQuery) -> list[FareOffer]:
        try:
            segments = [
                FlightSegment(
                    departure_airport=[[Airport[query.origin], 0]],
                    arrival_airport=[[Airport[query.destination], 0]],
                    travel_date=query.date,
                )
            ]
            if query.is_round_trip:
                segments.append(
                    FlightSegment(
                        departure_airport=[[Airport[query.destination], 0]],
                        arrival_airport=[[Airport[query.origin], 0]],
                        travel_date=query.return_date,
                    )
                )
            filters = FlightSearchFilters(
                trip_type=TripType.ROUND_TRIP if query.is_round_trip else TripType.ONE_WAY,
                passenger_info=PassengerInfo(
                    adults=query.adults,
                    children=query.children,
                    infants_in_seat=query.infants_in_seat,
                    infants_on_lap=query.infants_on_lap,
                ),
                flight_segments=segments,
                seat_type=SeatType.ECONOMY,
            )
            results = self._client.search(filters, currency=self.currency)
        except SearchParseError as e:
            raise SourceError(f"fli SearchParseError: {e}") from e
        except SearchTimeoutError as e:
            raise SourceError(f"fli SearchTimeoutError: {e}") from e
        except SearchConnectionError as e:
            raise SourceError(f"fli SearchConnectionError: {e}") from e
        except SearchHTTPError as e:
            raise SourceError(f"fli SearchHTTPError: {e}") from e
        except SearchClientError as e:
            raise SourceError(f"fli SearchClientError: {e}") from e
        except KeyError as e:
            # Airport[<code>] raises KeyError for unknown IATA codes.
            raise SourceError(f"fli unknown airport: {e}") from e

        if not results:
            return []

        offers: list[FareOffer] = []
        if query.is_round_trip:
            # ROUND_TRIP returns list[tuple[FlightResult, FlightResult]].
            for pair in results:
                outbound: FlightResult = pair[0]
                inbound: FlightResult = pair[1] if len(pair) > 1 else None
                if outbound.price is None:
                    continue
                # fli gives per-direction prices; party RT total is outbound + return.
                rt_price = int(outbound.price + (inbound.price if (inbound and inbound.price) else 0))
                offers.append(_to_offer(query, outbound, inbound, rt_price, self.currency))
        else:
            for r in results:
                if r.price is None:
                    continue
                offers.append(_to_offer(query, r, None, int(r.price), self.currency))
        return offers


def _to_offer(
    query: FareQuery,
    primary: FlightResult,
    inbound: FlightResult | None,
    price_per_pax: int,
    currency: str,
) -> FareOffer:
    legs = list(primary.legs or [])
    duration = sum(int(leg.duration or 0) for leg in legs)
    if inbound and inbound.legs:
        duration += sum(int(leg.duration or 0) for leg in inbound.legs)
    return FareOffer(
        origin=query.origin,
        destination=query.destination,
        date=query.date,
        return_date=query.return_date,
        carrier=primary.primary_airline_name or "",
        price_per_pax=price_per_pax,
        currency=currency,
        stops=int(primary.stops or 0),
        duration_minutes=duration,
        source=Source.FLI,
        verification_status=VerificationStatus.LEAD,
        passengers_queried=query.passenger_count,
        raw={
            "booking_token": primary.booking_token,
            "co2_g": primary.co2_emissions_g,
            "primary_airline": primary.primary_airline.value if primary.primary_airline else None,
        },
    )
