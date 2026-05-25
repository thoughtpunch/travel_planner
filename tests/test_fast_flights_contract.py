"""Contract test for fast-flights v3.0rc1.

Pins the shape of the returned objects so that a schema drift in the upstream
package (or the parser logic this fork ships) fails LOUDLY here rather than
producing silent wrong fares downstream. Per design.md decision 2.

This test does NOT hit the network — it imports the package's own model
classes and asserts the attributes the adapter relies on exist with the
expected types. If any of these asserts break, the adapter must be updated.
"""

from __future__ import annotations

import dataclasses
import inspect

import pytest


def test_imports_resolve():
    from fast_flights import FlightQuery, Passengers, create_query, get_flights  # noqa: F401
    from fast_flights.parser import FlightsError, MetaList  # noqa: F401
    from fast_flights.model import (  # noqa: F401
        Airport,
        Flights,
        SingleFlight,
    )


def test_flights_has_required_fields():
    from fast_flights.model import Flights

    fields = {f.name: f for f in dataclasses.fields(Flights)}
    # Adapter reads these:
    assert "price" in fields, "Flights.price missing — adapter cannot read fare"
    assert "airlines" in fields, "Flights.airlines missing — adapter cannot read carrier"
    assert "flights" in fields, "Flights.flights missing — adapter cannot read segments"


def test_single_flight_has_required_fields():
    from fast_flights.model import SingleFlight

    fields = {f.name: f for f in dataclasses.fields(SingleFlight)}
    assert "from_airport" in fields
    assert "to_airport" in fields
    assert "duration" in fields


def test_airport_has_code():
    from fast_flights.model import Airport

    fields = {f.name: f for f in dataclasses.fields(Airport)}
    assert "code" in fields, "Airport.code missing — segment origin/dest unreadable"


def test_passengers_signature_supports_party_of_six():
    from fast_flights.querying import Passengers

    sig = inspect.signature(Passengers.__init__)
    params = sig.parameters
    assert "adults" in params
    assert "children" in params
    # Six adults must construct without error.
    Passengers(adults=6)


def test_create_query_accepts_expected_args():
    from fast_flights import FlightQuery, Passengers, create_query

    q = create_query(
        flights=[FlightQuery(date="2026-09-10", from_airport="SJO", to_airport="VCE")],
        seat="economy",
        trip="one-way",
        passengers=Passengers(adults=6),
        language="en-US",
        currency="USD",
    )
    # Sanity: produced query exposes the URL/params surface we may log.
    assert callable(getattr(q, "url", None))
    assert callable(getattr(q, "params", None))


def test_adapter_returns_lead_status():
    """Even if a fake scraper returns a flight, the adapter must stamp LEAD."""
    from app.enums import Source, VerificationStatus
    from app.sources.base import FareQuery
    from app.sources.fast_flights_source import FastFlightsSource

    class _FakeFlight:
        price = 800
        airlines = ["LH"]
        flights: list = []
        type = "non-stop"

    src = FastFlightsSource(currency="USD")
    # Monkey-patch the upstream function to return a controlled list.
    import app.sources.fast_flights_source as mod

    captured = []

    def _fake_get_flights(q):  # noqa: ARG001
        captured.append(q)
        return [_FakeFlight()]

    mod.get_flights = _fake_get_flights
    try:
        offers = src.search(FareQuery(origin="SJO", destination="VCE", date="2026-09-10", adults=6))
    finally:
        from fast_flights.fetcher import get_flights as real

        mod.get_flights = real

    assert len(offers) == 1
    offer = offers[0]
    assert offer.source == Source.FAST_FLIGHTS
    assert offer.verification_status == VerificationStatus.LEAD, (
        "fast-flights offers must ALWAYS be LEAD — see design.md decision 1"
    )
    assert offer.price_per_pax == 800
    assert offer.passengers_queried == 6
