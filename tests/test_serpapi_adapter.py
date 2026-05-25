"""Adapter-level tests for the SerpAPI source.

Mocks the official `serpapi.Client` so we don't hit the network. Asserts:
- error class mapping (401 → SourceError, 429 → QuotaExceeded, timeout → SourceError)
- price-per-pax division for multi-passenger queries
- params shape sent to the SDK
"""

from __future__ import annotations

import pytest
import requests
import serpapi

from app.enums import Source, VerificationStatus
from app.sources.base import FareQuery, QuotaExceeded, SourceError
from app.sources.quota import QuotaTracker
from app.sources.serpapi_source import SerpApiSource


def _serpapi_http_error(status_code: int, body: str = "{}") -> serpapi.HTTPError:
    """Build a real serpapi.HTTPError the way the SDK constructs them — from a
    requests.HTTPError carrying a Response."""
    resp = requests.Response()
    resp.status_code = status_code
    resp._content = body.encode()
    original = requests.exceptions.HTTPError("simulated", response=resp)
    return serpapi.HTTPError(original)


class _FakeClient:
    """Stand-in for serpapi.Client that records params and returns a canned payload or raises."""

    def __init__(self, *, payload=None, raises=None):
        self._payload = payload
        self._raises = raises
        self.calls: list[dict] = []

    def search(self, params):
        self.calls.append(params)
        if self._raises is not None:
            raise self._raises
        return self._payload


def _quota(ceiling=10):
    return QuotaTracker(ceiling=ceiling)


def _query(adults=6):
    return FareQuery(origin="SJO", destination="VCE", date="2026-09-10", adults=adults)


def test_sends_documented_params():
    fake = _FakeClient(payload={"best_flights": [], "other_flights": []})
    src = SerpApiSource(api_key="k", quota=_quota(), currency="USD", client=fake)
    src.search(_query(adults=6))
    p = fake.calls[0]
    assert p["engine"] == "google_flights"
    assert p["departure_id"] == "SJO"
    assert p["arrival_id"] == "VCE"
    assert p["outbound_date"] == "2026-09-10"
    assert p["currency"] == "USD"
    assert p["hl"] == "en"
    assert p["gl"] == "us"
    assert p["adults"] == 6
    assert p["type"] == 2  # one-way
    assert p["stops"] == 0
    assert "deep_search" not in p  # off by default


def test_deep_search_opt_in():
    fake = _FakeClient(payload={"best_flights": [], "other_flights": []})
    src = SerpApiSource(api_key="k", quota=_quota(), client=fake, deep_search=True)
    src.search(_query())
    assert fake.calls[0]["deep_search"] is True


def test_price_per_pax_divides_party_total():
    """Per docs, `price` is the total for the requested party. We store per-pax."""
    payload = {
        "best_flights": [{
            "flights": [{
                "departure_airport": {"id": "SJO", "name": "SJO"},
                "arrival_airport": {"id": "VCE", "name": "VCE"},
                "airline": "LH",
                "duration": 600,
            }],
            "price": 4200,  # total for 6 pax
            "total_duration": 600,
            "type": "One way",
        }],
    }
    fake = _FakeClient(payload=payload)
    src = SerpApiSource(api_key="k", quota=_quota(), client=fake)
    offers = src.search(_query(adults=6))
    assert len(offers) == 1
    assert offers[0].price_per_pax == 700  # 4200 / 6
    assert offers[0].source == Source.SERPAPI
    assert offers[0].verification_status == VerificationStatus.LEAD
    assert offers[0].passengers_queried == 6


def test_401_maps_to_source_error():
    fake = _FakeClient(raises=_serpapi_http_error(401))
    src = SerpApiSource(api_key="k", quota=_quota(), client=fake)
    with pytest.raises(SourceError, match="auth"):
        src.search(_query())


def test_429_maps_to_quota_exceeded():
    fake = _FakeClient(raises=_serpapi_http_error(429))
    src = SerpApiSource(api_key="k", quota=_quota(), client=fake)
    with pytest.raises(QuotaExceeded):
        src.search(_query())


def test_timeout_maps_to_source_error():
    fake = _FakeClient(raises=serpapi.TimeoutError("slow"))
    src = SerpApiSource(api_key="k", quota=_quota(), client=fake)
    with pytest.raises(SourceError, match="timeout"):
        src.search(_query())


def test_missing_key_raises_immediately():
    src = SerpApiSource(api_key="", quota=_quota(), client=_FakeClient(payload={}))
    with pytest.raises(SourceError, match="not configured"):
        src.search(_query())


def test_round_trip_sets_type_1_and_return_date():
    fake = _FakeClient(payload={"best_flights": [], "other_flights": []})
    src = SerpApiSource(api_key="k", quota=_quota(), client=fake)
    src.search(FareQuery(
        origin="SJO", destination="IAD", date="2026-09-05",
        return_date="2026-12-20", adults=6,
    ))
    p = fake.calls[0]
    assert p["type"] == 1
    assert p["outbound_date"] == "2026-09-05"
    assert p["return_date"] == "2026-12-20"


def test_round_trip_offer_carries_return_date_and_per_pax_rt_total():
    payload = {
        "best_flights": [{
            "flights": [{
                "departure_airport": {"id": "SJO", "name": "SJO"},
                "arrival_airport": {"id": "IAD", "name": "IAD"},
                "airline": "UA",
                "duration": 360,
            }],
            "price": 4800,  # RT total for 6 pax → $800/pax
            "total_duration": 360,
            "type": "Round trip",
        }],
    }
    fake = _FakeClient(payload=payload)
    src = SerpApiSource(api_key="k", quota=_quota(), client=fake)
    offers = src.search(FareQuery(
        origin="SJO", destination="IAD", date="2026-09-05",
        return_date="2026-12-20", adults=6,
    ))
    assert len(offers) == 1
    o = offers[0]
    assert o.is_round_trip is True
    assert o.return_date == "2026-12-20"
    assert o.price_per_pax == 800  # 4800 / 6


def test_quota_reserved_only_on_actual_call():
    fake = _FakeClient(payload={"best_flights": [], "other_flights": []})
    q = _quota(ceiling=2)
    src = SerpApiSource(api_key="k", quota=q, client=fake)
    src.search(_query())
    src.search(_query())
    assert q.total_used == 2
    with pytest.raises(QuotaExceeded):
        src.search(_query())  # third call should exhaust
