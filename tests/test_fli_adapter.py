"""FliSource adapter tests.

Verifies the adapter's mapping logic by driving `FliSource.search` with
canned `SearchFlights.search` results — one-way (flat
`list[FlightResult]`) and round-trip (`list[tuple[FlightResult, FlightResult]]`).
Per task 5.2 of `migrate-fare-search-to-fli`.
"""

from __future__ import annotations

import datetime
from unittest.mock import patch

import pytest
from fli.models import FlightLeg, FlightResult
from fli.models.airline import Airline
from fli.models.airport import Airport as FliAirport
from fli.search.client import (
    SearchClientError,
    SearchConnectionError,
    SearchHTTPError,
    SearchTimeoutError,
)
from fli.search.flights import SearchParseError

from app.enums import Source, VerificationStatus
from app.sources.base import FareQuery, SourceError
from app.sources.fli_source import FliSource


def _leg(
    *,
    airline: Airline = Airline.UA,
    dep: FliAirport = FliAirport.SJO,
    arr: FliAirport = FliAirport.IAD,
    dep_dt: datetime.datetime = datetime.datetime(2026, 9, 10, 8, 0),
    arr_dt: datetime.datetime = datetime.datetime(2026, 9, 10, 14, 0),
    duration: int = 360,
) -> FlightLeg:
    return FlightLeg(
        airline=airline,
        flight_number=f"{airline.name}1",
        departure_airport=dep,
        arrival_airport=arr,
        departure_datetime=dep_dt,
        arrival_datetime=arr_dt,
        duration=duration,
    )


def _result(
    *,
    legs: list[FlightLeg] | None = None,
    price: float = 600.0,
    stops: int = 0,
    airline: Airline = Airline.UA,
    airline_name: str = "United Airlines",
    token: str = "tok",
) -> FlightResult:
    return FlightResult(
        legs=legs or [_leg(airline=airline)],
        price=price,
        currency="USD",
        duration=sum(int(leg.duration or 0) for leg in (legs or [_leg(airline=airline)])),
        stops=stops,
        primary_airline=airline,
        primary_airline_name=airline_name,
        booking_token=token,
    )


def test_one_way_flat_list_maps_each_result_to_offer():
    results = [
        _result(price=600.0, token="tok-1"),
        _result(price=750.0, airline=Airline.AA, airline_name="American Airlines", token="tok-2"),
    ]
    src = FliSource(currency="USD")
    with patch.object(src._client, "search", return_value=results):
        offers = src.search(
            FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6)
        )
    assert len(offers) == 2
    assert {o.price_per_pax for o in offers} == {600, 750}
    assert all(o.source == Source.FLI for o in offers)
    assert all(o.verification_status == VerificationStatus.LEAD for o in offers)
    assert all(o.return_date is None for o in offers)
    assert all(o.is_round_trip is False for o in offers)


def test_round_trip_tuple_collapses_to_single_offer_with_total_price():
    outbound = _result(price=400.0, token="ob-1")
    inbound = _result(
        legs=[
            _leg(
                airline=Airline.UA,
                dep=FliAirport.IAD,
                arr=FliAirport.SJO,
                dep_dt=datetime.datetime(2026, 12, 20, 9, 0),
                arr_dt=datetime.datetime(2026, 12, 20, 15, 0),
            )
        ],
        price=500.0,
        token="ib-1",
    )
    src = FliSource(currency="USD")
    with patch.object(src._client, "search", return_value=[(outbound, inbound)]):
        offers = src.search(
            FareQuery(
                origin="SJO",
                destination="IAD",
                date="2026-09-10",
                return_date="2026-12-20",
                adults=6,
            )
        )
    assert len(offers) == 1
    o = offers[0]
    assert o.is_round_trip is True
    assert o.return_date == "2026-12-20"
    assert o.date == "2026-09-10"
    assert o.price_per_pax == 900  # outbound + inbound total
    assert o.carrier == "United Airlines"
    assert o.source == Source.FLI
    assert o.verification_status == VerificationStatus.LEAD
    # Duration aggregates both directions.
    assert o.duration_minutes == 720


def test_query_translation_round_trip_builds_two_segments():
    """The adapter must pass two FlightSegments to fli for a round-trip query."""
    captured: dict = {}

    def _capture(filters, **kwargs):
        captured["filters"] = filters
        captured["currency"] = kwargs.get("currency")
        return []

    src = FliSource(currency="USD")
    with patch.object(src._client, "search", side_effect=_capture):
        src.search(
            FareQuery(
                origin="SJO",
                destination="IAD",
                date="2026-09-10",
                return_date="2026-12-20",
                adults=6,
            )
        )
    f = captured["filters"]
    assert len(f.flight_segments) == 2
    assert f.passenger_info.adults == 6
    assert captured["currency"] == "USD"


def test_query_translation_one_way_builds_one_segment():
    captured: dict = {}

    def _capture(filters, **kwargs):
        captured["filters"] = filters
        return []

    src = FliSource(currency="USD")
    with patch.object(src._client, "search", side_effect=_capture):
        src.search(FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6))
    assert len(captured["filters"].flight_segments) == 1


def test_empty_results_returns_empty_list():
    src = FliSource(currency="USD")
    with patch.object(src._client, "search", return_value=[]):
        offers = src.search(
            FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6)
        )
    assert offers == []


def test_none_results_returns_empty_list():
    """fli returns None when there are no flights — adapter must coerce to []."""
    src = FliSource(currency="USD")
    with patch.object(src._client, "search", return_value=None):
        offers = src.search(
            FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6)
        )
    assert offers == []


def test_results_with_none_price_are_skipped():
    no_price = _result(price=600.0)
    no_price.price = None  # type: ignore[assignment]
    good = _result(price=700.0)
    src = FliSource(currency="USD")
    with patch.object(src._client, "search", return_value=[no_price, good]):
        offers = src.search(
            FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6)
        )
    assert len(offers) == 1
    assert offers[0].price_per_pax == 700


@pytest.mark.parametrize(
    ("exc_cls", "marker"),
    [
        (SearchParseError, "SearchParseError"),
        (SearchTimeoutError, "SearchTimeoutError"),
        (SearchConnectionError, "SearchConnectionError"),
        (SearchHTTPError, "SearchHTTPError"),
        (SearchClientError, "SearchClientError"),
    ],
)
def test_typed_exceptions_map_to_source_error(exc_cls, marker):
    src = FliSource(currency="USD")
    with patch.object(src._client, "search", side_effect=exc_cls("boom")):
        with pytest.raises(SourceError, match=marker):
            src.search(
                FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6)
            )


def test_unknown_airport_maps_to_source_error():
    """`Airport['ZZZ']` raises KeyError — adapter wraps it in SourceError."""
    src = FliSource(currency="USD")
    with pytest.raises(SourceError, match="unknown airport"):
        src.search(FareQuery(origin="ZZZ", destination="IAD", date="2026-09-10", adults=6))
