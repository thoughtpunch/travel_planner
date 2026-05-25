from __future__ import annotations

from dataclasses import dataclass

from app.enums import Source, Structure, VerificationStatus
from app.orchestrator.structures import ItineraryCandidate
from app.sources.base import FareOffer, QuotaExceeded
from app.validator import validate_candidate, validate_top_n


def _lead(o, d, date, price, pax=6):
    return FareOffer(
        origin=o, destination=d, date=date, carrier="LH",
        price_per_pax=price, currency="USD", stops=0, duration_minutes=600,
        source=Source.FAST_FLIGHTS,
        verification_status=VerificationStatus.LEAD, passengers_queried=pax,
    )


@dataclass
class FakeSerpApi:
    """Lookup keyed by (origin, destination, date) → list[FareOffer]."""
    lookup: dict
    raise_quota_after: int = 99999
    calls: int = 0

    def search(self, q):
        self.calls += 1
        if self.calls > self.raise_quota_after:
            raise QuotaExceeded("over ceiling")
        key = (q.origin, q.destination, q.date)
        offers = self.lookup.get(key, [])
        # Return as-LEAD (matches real adapter)
        return [
            FareOffer(
                origin=o.origin, destination=o.destination, date=o.date,
                carrier=o.carrier, price_per_pax=o.price_per_pax, currency=o.currency,
                stops=o.stops, duration_minutes=o.duration_minutes,
                source=Source.SERPAPI, verification_status=VerificationStatus.LEAD,
                passengers_queried=q.passenger_count,
            )
            for o in offers
        ]


def test_validates_when_within_tolerance():
    lead = _lead("SJO", "VCE", "2026-09-10", 700)
    serp_offer = _lead("SJO", "VCE", "2026-09-10", 750)  # 7% higher → within 15%
    cand = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[lead], gateway="VCE",
        total_party_price=700 * 6, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    serp = FakeSerpApi(lookup={("SJO", "VCE", "2026-09-10"): [serp_offer]})
    v = validate_candidate(cand, serp, adults=6, tolerance_pct=15, ttl_seconds=86400)
    assert v.verification_status == VerificationStatus.VALIDATED
    assert v.legs[0].price_per_pax == 750  # validated price wins, per spec


def test_six_seat_collapse_marks_validation_failed():
    lead = _lead("SJO", "VCE", "2026-09-10", 700)
    # Authoritative source: at 6 adults, cheapest fare jumps to $1200 → way outside 15%
    serp_offer = _lead("SJO", "VCE", "2026-09-10", 1200)
    cand = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[lead], gateway="VCE",
        total_party_price=700 * 6, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    serp = FakeSerpApi(lookup={("SJO", "VCE", "2026-09-10"): [serp_offer]})
    v = validate_candidate(cand, serp, adults=6, tolerance_pct=15, ttl_seconds=86400)
    assert v.verification_status == VerificationStatus.VALIDATION_FAILED
    assert v.legs[0].raw.get("validation_cheapest_at_full_pax") == 1200


def test_no_offers_from_authoritative_source_is_validation_failed():
    lead = _lead("SJO", "VCE", "2026-09-10", 700)
    cand = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[lead], gateway="VCE",
        total_party_price=700 * 6, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    serp = FakeSerpApi(lookup={})  # nothing returned at full pax
    v = validate_candidate(cand, serp, adults=6, tolerance_pct=15, ttl_seconds=86400)
    assert v.verification_status == VerificationStatus.VALIDATION_FAILED


def test_quota_exceeded_marks_skipped_quota():
    lead = _lead("SJO", "VCE", "2026-09-10", 700)
    cand = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[lead], gateway="VCE",
        total_party_price=700 * 6, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    serp = FakeSerpApi(lookup={}, raise_quota_after=0)  # quota gone immediately
    v = validate_candidate(cand, serp, adults=6, tolerance_pct=15, ttl_seconds=86400)
    assert v.verification_status == VerificationStatus.SKIPPED_QUOTA


def test_validate_top_n_promotes_next_after_collapse():
    cheap_collapse = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS,
        legs=[_lead("SJO", "VCE", "2026-09-10", 500)],
        gateway="VCE", total_party_price=500 * 6, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    next_best = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS,
        legs=[_lead("SJO", "MXP", "2026-09-10", 700)],
        gateway="MXP", total_party_price=700 * 6, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    serp = FakeSerpApi(lookup={
        ("SJO", "VCE", "2026-09-10"): [_lead("SJO", "VCE", "2026-09-10", 1200)],
        ("SJO", "MXP", "2026-09-10"): [_lead("SJO", "MXP", "2026-09-10", 720)],
    })
    out = validate_top_n([cheap_collapse, next_best], serp, adults=6, top_n=1,
                         tolerance_pct=15, ttl_seconds=86400)
    statuses = {c.gateway: c.verification_status for c in out}
    assert statuses["VCE"] == VerificationStatus.VALIDATION_FAILED
    assert statuses["MXP"] == VerificationStatus.VALIDATED  # promoted in
