"""Ranking — VALIDATED first, then LEAD, then failed/stale. Within each
status bucket, cheapest party total wins. BLACKOUT-flagged candidates are
de-prioritized within their bucket (not excluded)."""

from __future__ import annotations

from ..enums import Flag, VerificationStatus
from .structures import ItineraryCandidate


_STATUS_ORDER = {
    VerificationStatus.VALIDATED: 0,
    VerificationStatus.LEAD: 1,
    VerificationStatus.STALE: 2,
    VerificationStatus.VALIDATION_FAILED: 3,
    VerificationStatus.FAILED: 4,
    VerificationStatus.SKIPPED_QUOTA: 5,
}


def rank_candidates(candidates: list[ItineraryCandidate]) -> list[ItineraryCandidate]:
    def sort_key(c: ItineraryCandidate) -> tuple:
        return (
            _STATUS_ORDER.get(c.verification_status, 99),
            1 if Flag.BLACKOUT.value in c.flags else 0,
            c.total_party_price,
        )
    return sorted(candidates, key=sort_key)


def budget_verdict(candidates: list[ItineraryCandidate], budget_party_total: int) -> dict:
    """Verdict uses VALIDATED candidates only — per fare-validation.md."""
    validated = [c for c in candidates if c.verification_status == VerificationStatus.VALIDATED]
    if not validated:
        return {
            "met": False,
            "reason": "no VALIDATED itineraries — only leads or failures available",
            "best_validated_price": None,
            "budget_party_total": budget_party_total,
        }
    best = min(validated, key=lambda c: c.total_party_price)
    return {
        "met": best.total_party_price <= budget_party_total,
        "reason": (
            f"best validated party total ${best.total_party_price} {'<=' if best.total_party_price <= budget_party_total else '>'} "
            f"budget ${budget_party_total}"
        ),
        "best_validated_price": best.total_party_price,
        "budget_party_total": budget_party_total,
    }
