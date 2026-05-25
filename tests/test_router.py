from __future__ import annotations

from app.enums import Source, VerificationStatus
from app.sources.base import FareOffer, FareQuery, QuotaExceeded, SourceError
from app.sources.router import SourceRouter


class _ExplodingPrimary:
    name = Source.FAST_FLIGHTS

    def search(self, query):
        raise SourceError("scraper unreachable")


class _EmptyPrimary:
    name = Source.FAST_FLIGHTS

    def search(self, query):
        return []


class _ExplodingFallback:
    name = Source.SERPAPI

    def search(self, query):
        raise SourceError("serpapi 502")


class _QuotaFallback:
    name = Source.SERPAPI

    def search(self, query):
        raise QuotaExceeded("ceiling")


def _q():
    return FareQuery(origin="SJO", destination="VCE", date="2026-09-10", adults=6)


def test_no_fallback_returns_failed_marker():
    router = SourceRouter(primary=_ExplodingPrimary(), fallback=None)
    res = router.sweep(_q())
    assert len(res.offers) == 1
    marker = res.offers[0]
    assert marker.verification_status == VerificationStatus.FAILED
    assert marker.price_per_pax == 0
    assert marker.raw["reason"] == "no_fallback_available"
    assert res.error and "no fallback" in res.error


def test_empty_primary_no_fallback_also_returns_failed_marker():
    router = SourceRouter(primary=_EmptyPrimary(), fallback=None)
    res = router.sweep(_q())
    assert len(res.offers) == 1
    assert res.offers[0].verification_status == VerificationStatus.FAILED
    assert res.offers[0].raw["reason"] == "no_fallback_available"


def test_fallback_also_fails_returns_failed_marker():
    router = SourceRouter(primary=_ExplodingPrimary(), fallback=_ExplodingFallback())
    res = router.sweep(_q())
    assert len(res.offers) == 1
    assert res.offers[0].verification_status == VerificationStatus.FAILED
    assert res.offers[0].raw["reason"].startswith("fallback_failed:")
    assert res.error and "fallback failed" in res.error


def test_quota_exceeded_still_produces_skipped_quota_marker_not_failed():
    router = SourceRouter(primary=_ExplodingPrimary(), fallback=_QuotaFallback())
    res = router.sweep(_q())
    assert len(res.offers) == 1
    # FAILED is reserved for unrecoverable; SKIPPED_QUOTA stays its own thing.
    assert res.offers[0].verification_status == VerificationStatus.SKIPPED_QUOTA
