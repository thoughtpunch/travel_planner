"""Contract test for fli.

Pins the shape of the `fli` package surface the adapter relies on so that
upstream attribute drift fails LOUDLY here rather than producing silent
wrong fares downstream. Mirrors the role of
`tests/test_fast_flights_contract.py` for the new primary source per
`openspec/changes/migrate-fare-search-to-fli`.

Does NOT issue live HTTP. The end-to-end parser exercise patches
`fli.search.client.Client.post` so the adapter call path is verified
without contacting Google.
"""

from __future__ import annotations

import datetime
import inspect
from unittest.mock import MagicMock, patch

import pytest


def test_imports_resolve():
    from fli.models import (  # noqa: F401
        FlightLeg,
        FlightResult,
        FlightSearchFilters,
        FlightSegment,
        PassengerInfo,
        SeatType,
        TripType,
    )
    from fli.models.airport import Airport  # noqa: F401
    from fli.search import SearchFlights  # noqa: F401
    from fli.search.client import (  # noqa: F401
        SearchClientError,
        SearchConnectionError,
        SearchHTTPError,
        SearchTimeoutError,
    )
    from fli.search.flights import SearchParseError  # noqa: F401


def test_flight_result_has_required_fields():
    from fli.models import FlightResult

    fields = set(FlightResult.model_fields.keys())
    for required in ("legs", "price", "currency", "stops", "primary_airline_name", "booking_token"):
        assert required in fields, f"FlightResult.{required} missing — adapter cannot read it"


def test_flight_leg_has_required_fields():
    from fli.models import FlightLeg

    fields = set(FlightLeg.model_fields.keys())
    for required in ("airline", "duration", "departure_datetime", "arrival_datetime"):
        assert required in fields, f"FlightLeg.{required} missing — adapter cannot read it"


def test_flight_segment_accepts_airport_wire_format():
    """`departure_airport` is wire-shape `[[Airport, 0]]`. Adapter passes it verbatim."""
    from fli.models import FlightSegment
    from fli.models.airport import Airport

    seg = FlightSegment(
        departure_airport=[[Airport.SJO, 0]],
        arrival_airport=[[Airport.IAD, 0]],
        travel_date="2026-09-10",
    )
    assert seg.travel_date == datetime.date(2026, 9, 10) or str(seg.travel_date) == "2026-09-10"


def test_passenger_info_accepts_party_of_six():
    from fli.models import PassengerInfo

    p = PassengerInfo(adults=6, children=0, infants_in_seat=0, infants_on_lap=0)
    assert p.adults == 6


def test_filters_round_trip_two_segments():
    from fli.models import FlightSearchFilters, FlightSegment, PassengerInfo, SeatType, TripType
    from fli.models.airport import Airport

    f = FlightSearchFilters(
        trip_type=TripType.ROUND_TRIP,
        passenger_info=PassengerInfo(adults=6),
        flight_segments=[
            FlightSegment(
                departure_airport=[[Airport.SJO, 0]],
                arrival_airport=[[Airport.IAD, 0]],
                travel_date="2026-09-10",
            ),
            FlightSegment(
                departure_airport=[[Airport.IAD, 0]],
                arrival_airport=[[Airport.SJO, 0]],
                travel_date="2026-12-20",
            ),
        ],
        seat_type=SeatType.ECONOMY,
    )
    assert len(f.flight_segments) == 2


def test_search_flights_search_signature():
    """The adapter calls `SearchFlights().search(filters, currency=...)`."""
    from fli.search import SearchFlights

    sig = inspect.signature(SearchFlights.search)
    params = sig.parameters
    assert "filters" in params
    assert "currency" in params


def test_airport_enum_lookup_by_iata():
    """Adapter uses `Airport[query.origin]` for unknown-code defence (raises KeyError)."""
    from fli.models.airport import Airport

    # `name` is the IATA code; `value` is the human-readable airport name.
    assert Airport["SJO"].name == "SJO"
    with pytest.raises(KeyError):
        _ = Airport["XYZ_NOT_REAL"]


def test_typed_exceptions_inherit_from_exception():
    """Adapter catches each typed error individually and maps to SourceError."""
    from fli.search.client import (
        SearchClientError,
        SearchConnectionError,
        SearchHTTPError,
        SearchTimeoutError,
    )
    from fli.search.flights import SearchParseError

    for exc_cls in (
        SearchClientError,
        SearchConnectionError,
        SearchHTTPError,
        SearchTimeoutError,
        SearchParseError,
    ):
        assert issubclass(exc_cls, Exception)


def test_adapter_returns_lead_status_one_way():
    """Mock the parsed result and verify the adapter stamps LEAD + FLI source."""
    from fli.models import FlightLeg, FlightResult
    from fli.models.airline import Airline
    from fli.models.airport import Airport as FliAirport

    from app.enums import Source, VerificationStatus
    from app.sources.base import FareQuery
    from app.sources.fli_source import FliSource

    leg = FlightLeg(
        airline=Airline.UA,
        flight_number="UA123",
        departure_airport=FliAirport.SJO,
        arrival_airport=FliAirport.IAD,
        departure_datetime=datetime.datetime(2026, 9, 10, 8, 0),
        arrival_datetime=datetime.datetime(2026, 9, 10, 14, 0),
        duration=360,
    )
    fr = FlightResult(
        legs=[leg],
        price=600.0,
        currency="USD",
        duration=360,
        stops=0,
        primary_airline=Airline.UA,
        primary_airline_name="United Airlines",
        booking_token="tok-1",
    )
    src = FliSource(currency="USD")
    with patch.object(src._client, "search", return_value=[fr]):
        offers = src.search(
            FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6)
        )
    assert len(offers) == 1
    o = offers[0]
    assert o.source == Source.FLI
    assert o.verification_status == VerificationStatus.LEAD, (
        "fli offers must ALWAYS be LEAD — see design.md decision 1"
    )
    assert o.price_per_pax == 600
    assert o.passengers_queried == 6
    assert o.carrier == "United Airlines"
    assert o.stops == 0
    assert o.return_date is None
    assert o.raw.get("booking_token") == "tok-1"


def test_adapter_http_boundary_isolated_via_client_post():
    """Patches `fli.search.client.Client.post` so no real HTTP fires.

    Returns a Mock Response whose `.text` decodes to an empty wrb chunk
    payload — the parser will short-circuit to `None` and the adapter
    must surface that as an empty list.
    """
    from app.sources.base import FareQuery
    from app.sources.fli_source import FliSource

    fake_response = MagicMock()
    fake_response.text = ")]}'\n"  # Google XSSI prefix only — no chunks.
    fake_response.raise_for_status = MagicMock(return_value=None)

    src = FliSource(currency="USD")
    with patch("fli.search.client.Client.post", return_value=fake_response):
        offers = src.search(
            FareQuery(origin="SJO", destination="IAD", date="2026-09-10", adults=6)
        )
    assert offers == []


def test_adapter_unknown_airport_maps_to_source_error():
    from app.sources.base import FareQuery, SourceError
    from app.sources.fli_source import FliSource

    src = FliSource(currency="USD")
    with pytest.raises(SourceError, match="unknown airport"):
        src.search(FareQuery(origin="ZZZ", destination="IAD", date="2026-09-10", adults=6))
