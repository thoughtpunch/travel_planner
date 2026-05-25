"""Top-N validation: re-query candidate fares at full passenger count via
SerpAPI, then promote/demote based on tolerance check.

Per fare-validation.md:
- Validation queries hit SerpAPI directly (NOT the router) so we can trust the
  authoritative source at full pax.
- If a fare within ±tolerance% of the LEAD price exists at full pax → VALIDATED.
- Otherwise → VALIDATION_FAILED (the "6-seat collapse"); promote next-best lead
  if validation budget remains.
- Budget verdicts use VALIDATED only.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from .enums import VerificationStatus
from .orchestrator.structures import ItineraryCandidate, _worst_status
from .sources.base import FareOffer, FareQuery, QuotaExceeded, SourceError
from .sources.serpapi_source import SerpApiSource


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _within_tolerance(lead_price: int, validated_price: int, tolerance_pct: int) -> bool:
    if lead_price <= 0:
        return True
    ratio = abs(validated_price - lead_price) / lead_price * 100
    return ratio <= tolerance_pct


def _validate_leg(
    lead: FareOffer,
    serpapi: SerpApiSource,
    adults: int,
    tolerance_pct: int,
    ttl_seconds: int,
) -> FareOffer:
    """Re-query a single leg at full pax. Returns a new offer with updated
    status (VALIDATED / VALIDATION_FAILED / SKIPPED_QUOTA / FAILED)."""
    query = FareQuery(
        origin=lead.origin,
        destination=lead.destination,
        date=lead.date,
        return_date=lead.return_date,  # preserve RT-ness for the re-query
        adults=adults,
    )
    try:
        offers = serpapi.search(query)
    except QuotaExceeded:
        return replace(lead, verification_status=VerificationStatus.SKIPPED_QUOTA)
    except SourceError:
        return replace(lead, verification_status=VerificationStatus.FAILED)

    if not offers:
        return replace(lead, verification_status=VerificationStatus.VALIDATION_FAILED)

    # Find cheapest offer within tolerance; if none, the lead "collapsed".
    candidates = sorted(offers, key=lambda o: o.price_per_pax)
    for o in candidates:
        if _within_tolerance(lead.price_per_pax, o.price_per_pax, tolerance_pct):
            # Merge raws: SerpAPI carries the validated price; lead carries
            # the richer fli friction data (layovers, arrival_local_time,
            # stopover_city). SerpAPI's raw wins on shared keys so the
            # validated source's view is authoritative where it has an
            # opinion, but the friction attributes survive.
            merged_raw = {**(lead.raw or {}), **(o.raw or {})}
            merged_raw.update({
                "lead_price_per_pax": lead.price_per_pax,
                "validated_at": _now().isoformat(),
                "ttl_seconds": ttl_seconds,
            })
            return FareOffer(
                origin=o.origin,
                destination=o.destination,
                date=o.date,
                return_date=o.return_date,
                carrier=o.carrier,
                price_per_pax=o.price_per_pax,
                currency=o.currency,
                stops=o.stops,
                duration_minutes=o.duration_minutes,
                source=o.source,
                verification_status=VerificationStatus.VALIDATED,
                passengers_queried=adults,
                raw=merged_raw,
            )
    # Authoritative source returned offers, but all are outside tolerance —
    # the lead price was unobtainable at full party. Classic 6-seat collapse.
    return replace(
        lead,
        verification_status=VerificationStatus.VALIDATION_FAILED,
        raw={**lead.raw, "validation_cheapest_at_full_pax": candidates[0].price_per_pax},
    )


def validate_candidate(
    candidate: ItineraryCandidate,
    serpapi: SerpApiSource,
    adults: int,
    tolerance_pct: int,
    ttl_seconds: int,
) -> ItineraryCandidate:
    new_legs = [
        _validate_leg(leg, serpapi, adults, tolerance_pct, ttl_seconds)
        for leg in candidate.legs
    ]
    new_total = sum(o.price_per_pax * max(1, o.passengers_queried) for o in new_legs)
    new_status = _worst_status(new_legs)
    return ItineraryCandidate(
        structure=candidate.structure,
        legs=new_legs,
        gateway=candidate.gateway,
        total_party_price=new_total,
        currency=candidate.currency,
        flags=candidate.flags,
        verification_status=new_status,
    )


def validate_top_n(
    candidates: list[ItineraryCandidate],
    serpapi: SerpApiSource,
    adults: int,
    top_n: int,
    tolerance_pct: int,
    ttl_seconds: int,
) -> list[ItineraryCandidate]:
    """Validate the top N candidates per structure (sorted by current LEAD
    total ascending). If a candidate fails validation and validation budget
    (top_n) remains for this structure, the next-best is promoted automatically
    by simply iterating further in the input list."""
    by_struct: dict[str, list[ItineraryCandidate]] = {}
    for c in candidates:
        by_struct.setdefault(c.structure, []).append(c)

    promoted: list[ItineraryCandidate] = []
    for struct, group in by_struct.items():
        sorted_group = sorted(group, key=lambda c: c.total_party_price)
        validated_count = 0
        validated_results: list[ItineraryCandidate] = []
        for c in sorted_group:
            if validated_count >= top_n:
                validated_results.append(c)  # keep as-is, still LEAD
                continue
            try:
                v = validate_candidate(c, serpapi, adults, tolerance_pct, ttl_seconds)
            except QuotaExceeded:
                # Hard ceiling: stop validating this structure
                validated_results.append(c)
                continue
            validated_results.append(v)
            if v.verification_status == VerificationStatus.VALIDATED:
                validated_count += 1
            # If VALIDATION_FAILED, loop continues — next candidate gets a shot.
        promoted.extend(validated_results)

    # Stamp STALE for any VALIDATED whose ttl already expired (defensive — TTL
    # is enforced again at display time).
    cutoff = _now() - timedelta(seconds=ttl_seconds)
    final: list[ItineraryCandidate] = []
    for c in promoted:
        any_stale = False
        for leg in c.legs:
            ts = leg.raw.get("validated_at") if leg.raw else None
            if ts:
                try:
                    when = datetime.fromisoformat(ts)
                    if when < cutoff:
                        any_stale = True
                        break
                except ValueError:
                    continue
        if any_stale and c.verification_status == VerificationStatus.VALIDATED:
            final.append(
                ItineraryCandidate(
                    structure=c.structure,
                    legs=c.legs,
                    gateway=c.gateway,
                    total_party_price=c.total_party_price,
                    currency=c.currency,
                    flags=c.flags,
                    verification_status=VerificationStatus.STALE,
                )
            )
        else:
            final.append(c)
    return final


__all__ = ["validate_top_n", "validate_candidate"]
