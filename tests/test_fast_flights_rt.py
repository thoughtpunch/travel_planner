"""Round-trip adapter test for fast-flights.

Verifies the adapter sends `trip="round-trip"` and TWO FlightQuery entries
(outbound + return) when query.return_date is set, and tags the resulting
FareOffer with the return_date so downstream knows it's an RT.
"""

from __future__ import annotations

from app.enums import Source, VerificationStatus
from app.sources.base import FareQuery
from app.sources.fast_flights_source import FastFlightsSource


class _FakeFlight:
    price = 1300  # RT total per pax (Google Flights' display, party-of-1 lens)
    airlines = ["UA"]
    flights: list = []
    type = "round-trip"


def test_round_trip_query_sends_two_legs_and_trip_round_trip(monkeypatch):
    import app.sources.fast_flights_source as mod

    captured: dict = {}

    def _fake_create_query(*, flights, trip, **kwargs):
        captured["flights"] = flights
        captured["trip"] = trip
        return object()

    def _fake_get_flights(_q):
        return [_FakeFlight()]

    monkeypatch.setattr(mod, "create_query", _fake_create_query)
    monkeypatch.setattr(mod, "get_flights", _fake_get_flights)

    src = FastFlightsSource(currency="USD")
    offers = src.search(FareQuery(
        origin="SJO", destination="IAD", date="2026-09-05",
        return_date="2026-12-20", adults=6,
    ))
    assert captured["trip"] == "round-trip"
    assert len(captured["flights"]) == 2
    out, ret = captured["flights"]
    assert (out.from_airport, out.to_airport, out.date) == ("SJO", "IAD", "2026-09-05")
    assert (ret.from_airport, ret.to_airport, ret.date) == ("IAD", "SJO", "2026-12-20")

    assert len(offers) == 1
    o = offers[0]
    assert o.source == Source.FAST_FLIGHTS
    assert o.verification_status == VerificationStatus.LEAD
    assert o.is_round_trip is True
    assert o.return_date == "2026-12-20"
    assert o.price_per_pax == 1300


def test_one_way_query_keeps_existing_shape(monkeypatch):
    import app.sources.fast_flights_source as mod
    captured: dict = {}

    def _fake_create_query(*, flights, trip, **kwargs):
        captured["flights"] = flights
        captured["trip"] = trip
        return object()

    monkeypatch.setattr(mod, "create_query", _fake_create_query)
    monkeypatch.setattr(mod, "get_flights", lambda _q: [_FakeFlight()])

    src = FastFlightsSource(currency="USD")
    src.search(FareQuery(origin="SJO", destination="VCE", date="2026-09-10", adults=6))
    assert captured["trip"] == "one-way"
    assert len(captured["flights"]) == 1
